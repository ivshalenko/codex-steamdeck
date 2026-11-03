"""Language packs, cancellable model downloads and local speech playback."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import uuid
import wave
import zipfile

ROOT=Path(__file__).resolve().parent
LANGUAGES=json.loads((ROOT/'speech-languages.json').read_text())
VOICE_INDEX='https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json'
VOICE_BASE='https://huggingface.co/rhasspy/piper-voices/resolve/main/'
VOSK={'ru':'vosk-model-small-ru-0.22','en':'vosk-model-small-en-us-0.15'}
NATIVE={'ru':'Русский','en':'English','de':'Deutsch','fr':'Français','es':'Español','it':'Italiano','pt':'Português','uk':'Українська','pl':'Polski','ja':'日本語','zh':'中文','ko':'한국어','ar':'العربية','he':'עברית','hi':'हिन्दी','th':'ไทย','tr':'Türkçe','vi':'Tiếng Việt','fa':'فارسی','nl':'Nederlands'}

class Cancelled(RuntimeError):pass

def check_cancel(cancel):
    if cancel.is_set():raise Cancelled('Загрузка отменена')

def atomic_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
    try:
        with os.fdopen(fd,'w') as stream:json.dump(data,stream,ensure_ascii=False)
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)

def read_json(path,default):
    try:return json.loads(Path(path).read_text())
    except (OSError,ValueError):return default

def system_voices():
    binary=shutil.which('espeak-ng') or shutil.which('espeak')
    if not binary:return []
    result=subprocess.run([binary,'--voices'],capture_output=True,text=True,timeout=10)
    voices=[]
    for line in result.stdout.splitlines()[1:]:
        fields=line.split()
        if len(fields)<5:continue
        language=fields[1];family=language.split('-')[0]
        family={'cmn':'zh','yue':'zh','jv':'jw'}.get(family,family)
        voices.append({'id':'system:'+language,'language':family,'name':fields[3].replace('_',' ')+' · '+language+' · системный','engine':'system','voice':language})
    return voices

def voice_catalog(state,refresh=False):
    path=Path(state)/'voice-catalog.json'
    cached=read_json(path,{})
    if isinstance(cached,dict) and cached and not refresh:return cached
    with urllib.request.urlopen(VOICE_INDEX,timeout=25) as response:
        data=json.loads(response.read(3*1024*1024))
    if not isinstance(data,dict):raise ValueError('Неверный каталог голосов')
    atomic_json(path,data);return data

def voices_for(language,systems,catalog):
    result=[v for v in systems if v['language']==language]
    for key,item in catalog.items():
        if not isinstance(item,dict) or item.get('language',{}).get('family')!=language:continue
        if not re.fullmatch(r'[A-Za-z0-9_-]+',key):continue
        size=sum(f.get('size_bytes',0) for name,f in item.get('files',{}).items() if name.endswith(('.onnx','.onnx.json')))
        result.append({'id':'piper:'+key,'language':language,'engine':'piper','voice':key,
                       'name':item.get('name',key)+' · '+item.get('language',{}).get('code','')+' · '+item.get('quality','')+f' · {size/1048576:.0f} МБ'})
    return result

def recognition_ready(root,language):
    root=Path(root)
    if language not in LANGUAGES and language!='auto':return False
    if language in VOSK:
        if importlib.util.find_spec('vosk') is None:return False
        model=root/'models'/VOSK[language]
        return all((model/name).is_file() for name in ('am/final.mdl','conf/model.conf','graph/HCLr.fst'))
    from speech_accuracy import multilingual_ready
    return multilingual_ready(root)

def run_cancellable(args,cancel,timeout=600,input_text=None):
    check_cancel(cancel)
    with tempfile.TemporaryFile() as output:
        process=subprocess.Popen(args,stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
                                 stdout=output,stderr=output)
        try:
            if input_text is not None:
                process.stdin.write(input_text.encode('utf-8'));process.stdin.close()
            deadline=time.monotonic()+timeout
            while process.poll() is None:
                check_cancel(cancel)
                if time.monotonic()>deadline:raise RuntimeError('Превышено время подготовки языковой модели')
                cancel.wait(.1)
            if process.returncode:raise RuntimeError('Не удалось подготовить языковой компонент. Проверьте интернет и свободное место.')
        finally:
            if process.poll() is None:
                process.terminate()
                try:process.wait(timeout=3)
                except subprocess.TimeoutExpired:process.kill();process.wait()

def download(url,path,cancel,progress=lambda text:None,size=None,digest=None):
    check_cancel(cancel)
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_file() and (size is None or path.stat().st_size==size):
        if not digest or hashlib.md5(path.read_bytes(),usedforsecurity=False).hexdigest()==digest:return
    temporary=path.with_name(path.name+'.part')
    received=0;last=0;checksum=hashlib.md5(usedforsecurity=False)
    try:
        with urllib.request.urlopen(url,timeout=30) as response,temporary.open('wb') as stream:
            total=size or int(response.headers.get('Content-Length') or 0)
            while True:
                check_cancel(cancel);chunk=response.read(128*1024)
                if not chunk:break
                stream.write(chunk);checksum.update(chunk);received+=len(chunk)
                if time.monotonic()-last>.2:
                    progress(f'Загрузка: {received/1048576:.1f} МБ'+(f' / {total/1048576:.1f} МБ' if total else ''));last=time.monotonic()
        if size is not None and received!=size:raise ValueError('Загрузка не завершена: размер файла не совпал')
        if digest and checksum.hexdigest()!=digest:raise ValueError('Загруженный файл не прошёл проверку целостности')
        check_cancel(cancel);os.replace(temporary,path)
    finally:
        temporary.unlink(missing_ok=True)

def prepare_recognition(root,language,cancel,progress):
    if language not in LANGUAGES:raise ValueError('Язык распознавания не поддерживается')
    root=Path(root)
    if recognition_ready(root,language):return
    check_cancel(cancel)
    if language in VOSK:
        if importlib.util.find_spec('vosk') is None:run_cancellable([sys.executable,'-m','pip','install','vosk==0.3.45'],cancel)
        model=VOSK[language];progress('Загружаю модель '+model)
        models=root/'models';models.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.voice-download-',dir=models) as directory:
            archive=Path(directory)/'model.zip'
            download('https://alphacephei.com/vosk/models/'+model+'.zip',archive,cancel,progress)
            with zipfile.ZipFile(archive) as source:
                for entry in source.infolist():
                    name=PurePosixPath(entry.filename)
                    if name.is_absolute() or '..' in name.parts or not name.parts or name.parts[0]!=model:
                        raise ValueError('Небезопасный путь в архиве модели')
                source.extractall(directory)
            check_cancel(cancel)
            target=models/model
            if target.exists():target.rename(models/(model+'.incomplete-'+str(time.time_ns())))
            os.replace(Path(directory)/model,target)
    else:
        progress('Загружаю общую модель Whisper small для 99 языков (около 500 МБ)')
        if importlib.util.find_spec('faster_whisper') is None:
            run_cancellable([sys.executable,'-m','pip','install','faster-whisper==1.2.1'],cancel)
        run_cancellable([sys.executable,str(Path(__file__).resolve()),'--download-whisper',str(root)],cancel,timeout=1800)
    if not recognition_ready(root,language):raise RuntimeError('Модель языка не готова. Повторите загрузку.')

def prepare_voice(root,state,voice_id,catalog,cancel,progress):
    if voice_id.startswith('system:'):return
    key=voice_id.removeprefix('piper:')
    if not voice_id.startswith('piper:') or key not in catalog or not re.fullmatch(r'[A-Za-z0-9_-]+',key):raise ValueError('Выберите голос из каталога')
    if importlib.util.find_spec('piper') is None:
        progress('Устанавливаю локальный движок озвучки Piper')
        run_cancellable([sys.executable,'-m','pip','install','piper-tts==1.8.0'],cancel)
    folder=Path(root)/'models'/'voices'/key
    files=catalog[key].get('files',{})
    for name,metadata in files.items():
        if not name.endswith(('.onnx','.onnx.json')):continue
        source=PurePosixPath(name)
        if source.is_absolute() or '..' in source.parts:raise ValueError('Некорректный путь голоса')
        download(VOICE_BASE+name,folder/source.name,cancel,progress,metadata.get('size_bytes'),metadata.get('md5_digest'))
    if not (folder/(key+'.onnx')).is_file() or not (folder/(key+'.onnx.json')).is_file():raise ValueError('В каталоге отсутствуют файлы выбранного голоса')

class SpeechPlayer:
    def __init__(self):self.cancel=threading.Event();self.playing=False
    def stop(self):self.cancel.set()
    def speak(self,text,voice_id,root,cancel):
        self.cancel=cancel;self.playing=True
        try:
            with tempfile.TemporaryDirectory(prefix='deck-ai-read-aloud-') as directory:
                recording=Path(directory)/'speech.wav'
                if voice_id.startswith('system:'):
                    binary=shutil.which('espeak-ng') or shutil.which('espeak')
                    if not binary:raise RuntimeError('Системный синтезатор речи не установлен')
                    voice=voice_id.split(':',1)[1]
                    if not re.fullmatch(r'[A-Za-z0-9_+-]+',voice):raise ValueError('Неверный голос')
                    run_cancellable([binary,'-v',voice,'-w',str(recording),'--stdin'],cancel,input_text=text)
                elif voice_id.startswith('piper:'):
                    key=voice_id.split(':',1)[1]
                    if not re.fullmatch(r'[A-Za-z0-9_-]+',key):raise ValueError('Неверный голос')
                    model=Path(root)/'models'/'voices'/key/(key+'.onnx')
                    if not model.is_file():raise RuntimeError('Сначала загрузите голос в настройках языка')
                    run_cancellable([sys.executable,str(Path(__file__).resolve()),'--synthesize',str(model),str(recording)],cancel,input_text=text)
                else:raise RuntimeError('Выберите голос в настройках языка')
                player=shutil.which('paplay') or shutil.which('aplay')
                if not player:raise RuntimeError('Не найден проигрыватель звука')
                run_cancellable([player,str(recording)],cancel,timeout=1800)
        finally:
            if self.cancel is cancel:self.playing=False


def parse_translations(answer,keys):
    answer=answer.strip()
    if answer.startswith('```'):
        answer=re.sub(r'^```(?:json)?\s*|\s*```$','',answer)
    data=json.loads(answer)
    values=data.get('translations') if isinstance(data,dict) else None
    if not isinstance(values,list) or len(values)!=len(keys) or not all(isinstance(v,str) and v.strip() and len(v)<4000 for v in values):
        raise ValueError('Модель вернула неполный перевод интерфейса. Повторите подготовку.')
    return dict(zip(keys,values))


def translate_pack(language,sources,request,state,cancel,progress):
    if language not in LANGUAGES:raise ValueError('Язык интерфейса не поддерживается')
    if language in ('ru','en'):return
    path=Path(state)/'translations'/(language+'.json')
    translated=read_json(path,{})
    if not isinstance(translated,dict):translated={}
    keys=[key for key in sources if not isinstance(translated.get(key),str) or not translated[key].strip()]
    for start in range(0,len(keys),32):
        check_cancel(cancel);batch=keys[start:start+32]
        progress(f'Перевод интерфейса: {start} / {len(keys)} строк')
        prompt=('Translate these application UI strings into '+LANGUAGES[language]+' (ISO '+language+'). '
                'Return only a JSON object with a translations array in exactly the same order and count. '
                'Preserve placeholders, punctuation, product names and shortcuts. Do not use tools. Strings: '+json.dumps(batch,ensure_ascii=False))
        answer=request(prompt,cancel)
        check_cancel(cancel);translated.update(parse_translations(answer,batch));atomic_json(path,translated)
    progress('Языковой пакет интерфейса готов')


def model_translation_request(provider,model,remote_host=''):
    def request(prompt,cancel):
        check_cancel(cancel)
        if provider!='codex':
            import providers
            if provider=='deepseek':return providers.openrouter_reply(model,[],prompt)
            if provider=='tokenharbor':return providers.tokenharbor_reply(model,[],prompt)
            if provider=='claude':
                import providers
                with tempfile.TemporaryDirectory(prefix='deck-ai-translate-') as directory:
                    return providers.claude_code_reply(model,str(uuid.uuid4()),prompt,directory,resume=False)
            raise ValueError('Неизвестный источник модели перевода')
        from backend import Backend
        done=threading.Event();pieces=[];completed=[];errors=[];selected=[None]
        def event(message):
            params=message.get('params',{});method=message.get('method','')
            if params.get('threadId')!=selected[0]:return
            if 'id' in message:
                client.respond(message['id'],error={'code':-32601,'message':'UI translation does not allow tools'})
            elif method=='item/agentMessage/delta':pieces.append(params.get('delta',''))
            elif method=='item/completed' and params.get('item',{}).get('type')=='agentMessage':completed.append(params['item'].get('text',''))
            elif method=='turn/completed':
                turn=params.get('turn',{})
                if turn.get('status')!='completed':errors.append((turn.get('error') or {}).get('message','Перевод не завершён'))
                done.set()
            elif method=='error':errors.append(str(params.get('error',{})));done.set()
        client=Backend(event,done.set,remote_host)
        turn_id=None
        try:
            client.connect(None)
            started=client.request('thread/start',{'ephemeral':True,'model':model,'approvalPolicy':'never','sandbox':'read-only','baseInstructions':'Translate UI strings only. Do not use tools or access files.'})
            selected[0]=started['thread']['id']
            result=client.request('turn/start',{'threadId':selected[0],'input':[{'type':'text','text':prompt,'text_elements':[]}],
                'outputSchema':{'type':'object','properties':{'translations':{'type':'array','items':{'type':'string'}}},'required':['translations'],'additionalProperties':False}})
            turn_id=result.get('turn',{}).get('id');deadline=time.monotonic()+240
            while not done.wait(.1):
                check_cancel(cancel)
                if time.monotonic()>deadline:raise RuntimeError('Модель не успела подготовить перевод. Повторите позже.')
            if errors:raise RuntimeError(errors[0])
            return completed[-1] if completed else ''.join(pieces)
        finally:
            if (cancel.is_set() or not done.is_set()) and turn_id:
                try:client.request('turn/interrupt',{'threadId':selected[0],'turnId':turn_id},timeout=5)
                except Exception:pass
            if client.process:client.process.terminate()
            elif client.ws:client.ws.close()
    return request


if __name__=='__main__':
    if sys.argv[1]=='--download-whisper':
        from faster_whisper.utils import download_model
        download_model('small',output_dir=str(Path(sys.argv[2])/'models'/'faster-whisper-small'))
    elif sys.argv[1]=='--synthesize':
        from piper import PiperVoice
        voice=PiperVoice.load(sys.argv[2])
        with wave.open(sys.argv[3],'wb') as recording:voice.synthesize_wav(sys.stdin.read(),recording)

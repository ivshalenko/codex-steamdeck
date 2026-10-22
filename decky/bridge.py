#!/usr/bin/env python3
"""Small JSON-lines bridge for the Decky Quick Access plugin."""
import json, os, sys, threading, uuid, time, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from array import array
import math
sys.path.insert(0,str(Path(__file__).resolve().parent))
from runtime_paths import resolve_app_dir,resolve_state_dir
APP_DIR=resolve_app_dir()
MODULES_DIR=Path(__file__).resolve().parents[1]
if not (MODULES_DIR/'backend.py').is_file():MODULES_DIR=APP_DIR
sys.path.insert(0,str(MODULES_DIR))
from chat_media import attachments,archive_image,display_text
from backend import Backend
import providers
from speech_accuracy import multilingual_ready
ROOT=Path.home(); STATE=resolve_state_dir()
STEAM=ROOT/'.local/share/Steam/userdata'
lock=threading.RLock(); connect_lock=threading.Lock(); preference_lock=threading.Lock(); jobs=ThreadPoolExecutor(max_workers=8)
bridge=None; thread_id=''; preferences={}; selected_models={}; cache=[]; cache_time=0; active=False; outbox=[]; remote_host=''
thread_caches={}; thread_cache_times={}; history_caches={}; history_cache_times={}; model_caches={}; account_caches={}
account_cache={'account':None};account_cache_time=0;account_login_id=''
current_model=''; status='Подключаюсь к Codex…'
provider='codex';provider_active=False;provider_status='Готов';provider_model_cache={'claude':[],'deepseek':[],'tokenharbor':[]};provider_model_cache_time={}
provider_chats={'claude':{},'deepseek':{},'tokenharbor':{}};provider_thread_ids={'claude':'','deepseek':'','tokenharbor':''}
voice_id='';voice_state='idle';voice_text='';voice_error='';voice_stop=None;voice_thread=None;voice_language='en'
def write(value):
    with lock:
        sys.stdout.write(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n');sys.stdout.flush()
def atomic(path,obj):
    atomic_text(path,json.dumps(obj,ensure_ascii=False))
def atomic_text(path,text):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    temp=path.with_name(path.name+'.tmp-'+uuid.uuid4().hex)
    temp.write_text(text);os.chmod(temp,0o600);os.replace(temp,path)
def read_text_state(path):
    text=path.read_text().strip()
    # Older plugin versions incorrectly JSON-encoded the shared text files.
    if text.startswith('"'):
        try:
            decoded=json.loads(text)
            if isinstance(decoded,str):return decoded.strip()
        except ValueError:pass
    return text

def cleanup_generated_images(images):
    """Delete only temporary frames created under our private state folder."""
    generated=(STATE/'game-frames').resolve()
    for image in images:
        try:
            path=Path(image).resolve(strict=True)
            if path.is_file() and path.is_relative_to(generated):path.unlink()
        except (OSError,ValueError):pass
def event(message):
    global active,status,account_cache_time,account_login_id
    method=message.get('method');p=message.get('params',{})
    if method in ('account/updated','account/login/completed'):
        account_cache_time=0
        if method=='account/login/completed':
            account_login_id=''
    tid=p.get('threadId') or p.get('thread',{}).get('id')
    turn=p.get('turn') or {}
    turn_id=turn.get('id') or p.get('turnId')
    selected=tid==thread_id
    if method=='turn/started' and selected:
        active=True;status='Deck AI работает…'
    if method=='turn/completed':
        if selected:active=False;status='Готов'
        sending=next((j for j in outbox if j['threadId']==tid and j.get('status')=='sending' and (not j.get('turnId') or j['turnId']==turn_id)),None)
        if sending:
            if turn.get('status')=='failed':
                sending['status']='error';sending['error']=(turn.get('error') or {}).get('message') or 'Не удалось завершить ответ.'
            else:
                outbox.remove(sending);cleanup_generated_images(sending.get('images',[]))
            atomic(STATE/'decky-outbox.json',outbox)
            threading.Thread(target=dispatch,daemon=True).start()
    if method in ('turn/failed','error'):
        error=p.get('error',{}).get('message') or p.get('message') or 'Не удалось завершить ответ.'
        if selected:status=error;active=False
        failed=next((j for j in outbox if j['threadId']==tid and j.get('status')=='sending' and (not j.get('turnId') or j['turnId']==turn_id)),None)
        if failed:failed['status']='error';failed['error']=error;atomic(STATE/'decky-outbox.json',outbox)

def load_state():
    global thread_id,preferences,selected_models,outbox,remote_host,provider_chats,provider_thread_ids
    try:
        remote_host=read_text_state(STATE/'remote-host')
        thread_id=read_text_state(STATE/('thread-id-remote-'+remote_host if remote_host else 'thread-id'))
    except OSError:thread_id=''
    try:preferences=json.loads((STATE/'runtime-preferences.json').read_text())
    except (OSError,ValueError):preferences={}
    try:selected_models=json.loads((STATE/'model-preferences.json').read_text())
    except (OSError,ValueError):selected_models={}
    try:
        outbox=json.loads((STATE/'decky-outbox.json').read_text())
        for job in outbox:
            if job.get('status')=='sending':job['status']='recovering'
        atomic(STATE/'decky-outbox.json',outbox)
    except (OSError,ValueError):outbox=[]
    try:
        saved=json.loads((STATE/'provider-chats.json').read_text())
        for key in provider_chats:provider_chats[key]=saved.get('chats',{}).get(key,{})
        provider_thread_ids.update(saved.get('selected',{}))
    except (OSError,ValueError,TypeError):pass
def recover_outbox():
    """Confirm persisted sends against server turns; never replay an ambiguous send."""
    global active
    if not bridge or not bridge.connected:return
    if remote_host:
        for job in outbox:
            if job.get('status')=='recovering':job['status']='error';job['error']='Проверьте удалённый чат перед повторной отправкой.'
        atomic(STATE/'decky-outbox.json',outbox);return
    for job in list(outbox):
        if job.get('status') not in ('recovering','sending'):continue
        try:
            thread=bridge.request('thread/read',{'threadId':job['threadId'],'includeTurns':True},timeout=15).get('thread',{})
            turns=thread.get('turns',[])
            if job['threadId']==thread_id:active=any(t.get('status')=='inProgress' for t in turns)
            matches=[turn for turn in turns if turn.get('id')==job.get('turnId')] if job.get('turnId') else [turn for turn in turns if any(item.get('id')==job['id'] or item.get('clientUserMessageId')==job['id'] for item in turn.get('items',[]))]
            if not matches and not job.get('turnId') and not job.get('images'):
                # Older acknowledged sends did not persist turn IDs. A unique,
                # exact text match can migrate them without starting a new turn.
                matches=[turn for turn in turns if any(item.get('type')=='userMessage' and '\n'.join(part.get('text','') for part in item.get('content',[]) if part.get('type')=='text').strip()==job.get('text','').strip() for item in turn.get('items',[]))]
            if len(matches)!=1:
                if job['status']=='recovering':
                    job['status']='error';job['error']='Не удалось подтвердить отправку. Проверьте чат перед повтором.';atomic(STATE/'decky-outbox.json',outbox)
                continue
            turn=matches[0];state=turn.get('status')
            if state=='inProgress':
                if job['status']=='recovering':bridge.request('thread/resume',{'threadId':job['threadId'],'excludeTurns':True},timeout=20)
                job['status']='sending';job['turnId']=turn['id']
            elif state=='completed':
                if job in outbox:outbox.remove(job);cleanup_generated_images(job.get('images',[]))
            elif state in ('failed','interrupted'):
                job['status']='error';job['error']='Ответ остановлен или завершился ошибкой. Проверьте чат перед повтором.'
            if job['threadId']==thread_id:active=any(t.get('status')=='inProgress' for t in turns)
            atomic(STATE/'decky-outbox.json',outbox)
        except Exception:
            # Offline is not evidence of a failed send; retry verification later.
            continue

def connected():
    global bridge,status
    with connect_lock:
        if bridge and bridge.connected:return
        status='Подключаю Codex…';candidate=Backend(event,lambda:None,remote_host)
        try:
            candidate.connect(None);bridge=candidate;status='Готов' if thread_id else 'Создайте чат';recover_outbox()
        except Exception as exc:
            bridge=candidate if candidate.connected else None;status='Codex недоступен: '+str(exc)[:170];raise RuntimeError(status)
def ssh_hosts():
    hosts=[];ssh=ROOT/'.ssh'
    for path in [ssh/'config',*sorted((ssh/'config.d').glob('*.conf'))]:
        try:lines=path.read_text(errors='ignore').splitlines()
        except OSError:continue
        for line in lines:
            try:parts=__import__('shlex').split(line,comments=True)
            except ValueError:continue
            if len(parts)<2 or parts[0].lower()!='host':continue
            for alias in parts[1:]:
                if alias.startswith('!') or any(ch in alias for ch in '*?[') or alias.lower()=='all':continue
                if alias not in hosts:hosts.append(alias)
    if remote_host and remote_host not in hosts:hosts.insert(0,remote_host)
    return hosts
def refresh_threads(force=False):
    global cache,cache_time
    key=remote_host
    if cache and not force and time.time()-cache_time<15:return
    if key in thread_caches and not force:
        cache=thread_caches[key];cache_time=thread_cache_times.get(key,0)
        if time.time()-cache_time<15:return
    response=bridge.request('thread/list',{'limit':50,'sortKey':'updated_at','archived':False},timeout=22)
    cache=response.get('data',[]);cache_time=time.time();thread_caches[key]=cache;thread_cache_times[key]=cache_time
def extract_messages(thread):
    items=[]
    for turn in thread.get('turns',[]):
        for item in turn.get('items',[]):
            if item.get('type')=='userMessage':
                text='\n'.join(part.get('text','') for part in item.get('content',[]) if part.get('type')=='text').strip()
                text=text.split('<environment_context>')[0].strip()
            elif item.get('type')=='agentMessage':text=item.get('text','').strip()
            else:continue
            media=attachments(item)
            text=display_text(text)
            if text or media:items.append({'id':item.get('id',''),'role':'user' if item.get('type')=='userMessage' else 'assistant','text':text,'attachments':media})
    return items[-24:]
def list_screenshots():
    found=[]
    for p in STEAM.glob('*/760/remote/*/screenshots/*'):
        if not p.is_file() or p.parent.name=='thumbnails' or p.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):continue
        try:
            st=p.stat()
            if st.st_size<4_000_000:found.append({'path':str(p),'name':p.stem,'when':int(st.st_mtime),'size':st.st_size})
        except OSError:pass
    return sorted(found,key=lambda x:x['when'],reverse=True)[:50]
def media_roots():return [p for p in STEAM.glob('*/gamerecordings') if p.is_dir()]
def list_videos():
    found=[]
    for root in media_roots():
        for p in root.rglob('*'):
            if p.suffix.lower() not in ('.mpd','.mp4','.mkv','.webm','.mov'):continue
            try:
                st=p.stat()
                if st.st_size<100 and p.suffix.lower()!='.mpd':continue
                found.append({'path':str(p),'name':p.parent.parent.name+' · '+p.parent.name,'when':int(st.st_mtime),'size':st.st_size})
            except OSError:pass
    return sorted(found,key=lambda x:x['when'],reverse=True)[:40]
def allowed_image(path):
    p=Path(path).resolve(strict=True)
    generated=STATE/'game-frames'
    if not (p.is_relative_to(STEAM.resolve()) or p.is_relative_to(generated.resolve()) or p.is_relative_to((STATE/'chat-attachments').resolve())) or not p.is_file() or p.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):raise ValueError('Выбирайте изображение из скриншотов Steam или сохранённых кадров игры.')
    if p.stat().st_size>30_000_000:raise ValueError('Изображение слишком большое (лимит 30 МБ).')
    return p
def video_frames(path):
    source=Path(path).resolve(strict=True)
    if not any(source.is_relative_to(root.resolve()) for root in media_roots()):raise ValueError('Выбирайте видео из записей Steam.')
    if source.suffix.lower() not in ('.mpd','.mp4','.mkv','.webm','.mov'):raise ValueError('Неизвестный формат видео Steam.')
    generated=STATE/'game-frames';generated.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(generated,0o700)
    dest=generated/str(uuid.uuid4());dest.mkdir(parents=True,exist_ok=True,mode=0o700)
    args=['/usr/bin/ffmpeg','-nostdin','-hide_banner','-loglevel','error','-protocol_whitelist','file,crypto,data','-i',str(source),'-vf','fps=1/30,scale=960:-2','-frames:v','4','-q:v','3',str(dest/'frame-%02d.jpg')]
    try:subprocess.run(args,timeout=90,check=True,capture_output=True,text=True)
    except subprocess.CalledProcessError as exc:raise RuntimeError('Не удалось прочитать запись Steam: '+(exc.stderr or '')[-500:])
    except subprocess.TimeoutExpired:raise RuntimeError('Не удалось извлечь кадры за 90 секунд.')
    frames=sorted(dest.glob('frame-*.jpg'))
    if not frames:raise RuntimeError('В выбранной записи не удалось найти кадры.')
    return [{'path':str(f),'name':'Кадр '+str(i+1)} for i,f in enumerate(frames)]
def models():
    result=bridge.request('model/list',{'limit':100,'includeHidden':True},timeout=20);data=result.get('data',[])
    while result.get('nextCursor'):
        result=bridge.request('model/list',{'limit':100,'includeHidden':True,'cursor':result['nextCursor']},timeout=20);data+=result.get('data',[])
    return [{'id':m.get('model') or m['id'],'name':(m.get('displayName') or m.get('model') or m['id'])+(' · служебная' if m.get('hidden') else ''),'efforts':[{'id':x['reasoningEffort'],'name':x['reasoningEffort']} for x in m.get('supportedReasoningEfforts',[])],'defaultEffort':m.get('defaultReasoningEffort') or (m.get('supportedReasoningEfforts') or [{}])[0].get('reasoningEffort'),'tiers':['default']+(['priority'] if 'fast' in (m.get('additionalSpeedTiers') or []) or any(t.get('id')=='priority' for t in (m.get('serviceTiers') or [])) else [])} for m in data]
def model_list_for_provider(source):
    global provider_model_cache,provider_model_cache_time
    if provider_model_cache_time.get(source,0) and time.time()-provider_model_cache_time.get(source,0)<300:return provider_model_cache[source]
    if source=='claude':
        result=[{'id':'sonnet','name':'Claude Sonnet · latest','efforts':[],'defaultEffort':'','tiers':['default']}, {'id':'opus','name':'Claude Opus · latest','efforts':[],'defaultEffort':'','tiers':['default']}, {'id':'haiku','name':'Claude Haiku · latest','efforts':[],'defaultEffort':'','tiers':['default']}]
    elif source=='tokenharbor':
        result=[{'id':m['id'],'name':m['name']+' · free','efforts':[],'defaultEffort':'','tiers':['default']} for m in providers.tokenharbor_models()]
    else:
        result=[]
        for m in providers.list_deepseek_models():
            if m.get('inputPrice')==0 and m.get('outputPrice')==0:price='free'
            elif m.get('inputPrice') is not None:price=f"${m['inputPrice']*1_000_000:.2f}/${m['outputPrice']*1_000_000:.2f} per 1M"
            else:price='pricing unavailable'
            result.append({'id':m['id'],'name':m['name']+' · '+price,'efforts':[],'defaultEffort':'','tiers':['default']})
    provider_model_cache[source]=result;provider_model_cache_time[source]=time.time();return result
def save_provider_chats():atomic(STATE/'provider-chats.json',{'chats':provider_chats,'selected':provider_thread_ids})
def read_account(force=False):
    global account_cache,account_cache_time
    if remote_host in account_caches and not force and time.time()-account_cache_time<=10:
        return account_cache
    if force or time.time()-account_cache_time>10:
        try:
            result=bridge.request('account/read',{},timeout=12)
            account_cache={'account':result.get('account')}
            account_caches[remote_host]=account_cache
        except Exception:
            # Keep the last known account during a transient server reconnect.
            pass
        account_cache_time=time.time()
    return account_cache
def start_account_login():
    global account_login_id
    if not bridge or not bridge.connected:connected()
    if account_login_id:
        try:bridge.request('account/login/cancel',{'loginId':account_login_id},timeout=8)
        except Exception:pass
        account_login_id=''
    result=bridge.request('account/login/start',{'type':'chatgpt'},timeout=20)
    account_login_id=result.get('loginId','')
    url=result.get('authUrl') or result.get('verificationUrl')
    if not url:raise RuntimeError('Codex не вернул ссылку для входа.')
    try:
        subprocess.Popen(['/usr/bin/xdg-open',url],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,env={**os.environ,'HOME':str(ROOT),'XDG_RUNTIME_DIR':'/run/user/1000'})
        opened=True
    except OSError:opened=False
    return {'opened':opened,'url':url,'userCode':result.get('userCode')}
def cancel_account_login():
    global account_login_id
    if not account_login_id:return {'cancelled':False}
    if not bridge or not bridge.connected:connected()
    ident=account_login_id
    bridge.request('account/login/cancel',{'loginId':ident},timeout=12)
    account_login_id=''
    return {'cancelled':True}
def logout_account():
    global account_cache_time,model_cache_time,cache_time
    if not bridge or not bridge.connected:connected()
    if account_login_id:cancel_account_login()
    bridge.request('account/logout',{},timeout=20)
    account_cache_time=0;model_cache_time=0;cache_time=0
    return {'loggedOut':True}
def _get_snapshot():
    global current_model,active,status,thread_id,cache_screens,cache_media,cache_media_time,model_catalog,model_cache_time,provider_status
    # A UI snapshot may arrive before the background reconnect loop has run.
    # Establish the app-server connection before model/thread RPCs below.
    if provider=='codex':connected()
    now=time.time()
    if provider in provider_chats:
        if not remote_host and now-cache_media_time>12:
            cache_screens=list_screenshots();cache_media=list_videos();cache_media_time=now
        try:provider_models=model_list_for_provider(provider)
        except Exception as exc:provider_models=provider_model_cache.get(provider,[]);provider_model_cache_time[provider]=now;provider_status='Не удалось обновить каталог: '+str(exc)[:140]
        selected_id=provider_thread_ids.get(provider,'');chats=provider_chats[provider]
        chat=chats.get(selected_id,{}) if selected_id else {}
        messages=[{'id':item.get('id',''),'role':item.get('role','assistant'),'text':display_text(item.get('text','')),'attachments':attachments(item)} for item in chat.get('messages',[])]
        selected_model=chat.get('model') or (provider_models[0]['id'] if provider_models else '')
        account=read_account()
        return {'ready':True,'status':provider_status,'provider':provider,'account':account.get('account'),'loginPending':bool(account_login_id),'remoteHost':remote_host,'sshHosts':ssh_hosts(),'threads':[{'id':x['id'],'name':x.get('name') or 'New chat','updatedAt':x.get('updatedAt') or x.get('createdAt') or 0} for x in sorted(chats.values(),key=lambda x:x.get('updatedAt',0),reverse=True)],'threadId':selected_id,'messages':messages,'active':provider_active,'models':provider_models,'model':selected_model,'effort':'','tier':'default','videos':cache_media if not remote_host else [],'screenshots':cache_screens if not remote_host else [],'outbox':[],'speechVersion':2,'speechReady':multilingual_ready(APP_DIR),'voiceId':voice_id,'voiceState':voice_state,'voiceText':voice_text,'voiceError':voice_error}
    if not remote_host and now-cache_media_time>12:
        cache_screens=list_screenshots();cache_media=list_videos();cache_media_time=now
    if remote_host in model_caches and now-model_cache_time>60:
        model_catalog=model_caches[remote_host];model_cache_time=now
    if now-model_cache_time>60:
        model_catalog=models();model_cache_time=now
        model_caches[remote_host]=model_catalog
    connected()
    try:
        shared=read_text_state(STATE/('thread-id-remote-'+remote_host if remote_host else 'thread-id'))
        if shared and shared!=thread_id:
            thread_id=shared
    except OSError:pass
    try:selected_models.update(json.loads((STATE/'model-preferences.json').read_text()))
    except (OSError,ValueError):pass
    try:preferences.update(json.loads((STATE/'runtime-preferences.json').read_text()))
    except (OSError,ValueError):pass
    refresh_threads()
    current=next((t for t in cache if t.get('id')==thread_id),None);messages=[]
    if thread_id and current:
        history_key=(remote_host,thread_id)
        thread=history_caches.get(history_key)
        # Refresh at most once per 4 seconds. Keep the last good snapshot if
        # the server is slow, so the UI never blanks during a transient delay.
        if thread is None or now-history_cache_times.get(history_key,0)>=4:
            try:
                hist=bridge.request('thread/read',{'threadId':thread_id,'includeTurns':True},timeout=25)
                thread=hist.get('thread',current);history_caches[history_key]=thread;history_cache_times[history_key]=now
            except Exception:
                thread=thread or current
        active=any(t.get('status')=='inProgress' for t in thread.get('turns',[]));messages=extract_messages(thread)
        current_model=thread.get('model') or current_model;status='Deck AI работает…' if active else 'Готов'
    elif thread_id:
        try:
            _,thread=bridge.select_thread(thread_id);messages=extract_messages(thread);active=any(t.get('status')=='inProgress' for t in thread.get('turns',[]))
        except Exception as exc:status=str(exc)[:160]
    account=read_account()
    models_list=model_catalog;saved_model=selected_models.get(thread_id) or (selected_models.get('') if not thread_id else None) or current_model
    if not saved_model and models_list:saved_model=models_list[0]['id']
    pref=preferences.get(thread_id or '',{}).get(saved_model,{})
    return {'ready':True,'status':status,'provider':'codex','account':account.get('account'),'loginPending':bool(account_login_id),'remoteHost':remote_host,'sshHosts':ssh_hosts(),'threads':[{'id':t['id'],'name':t.get('name') or t.get('preview') or 'Новый чат','updatedAt':t.get('updatedAt') or t.get('createdAt') or 0} for t in cache],'threadId':thread_id,'messages':messages,'active':active,'models':models_list,'model':saved_model,'effort':pref.get('effort'),'tier':pref.get('tier','default'),'videos':cache_media if not remote_host else [],'screenshots':cache_screens if not remote_host else [],'outbox':outbox[-8:],'speechVersion':2,'speechReady':multilingual_ready(APP_DIR),'voiceId':voice_id,'voiceState':voice_state,'voiceText':voice_text,'voiceError':voice_error}
snapshot_cache={}
def get_snapshot():
    # A failed backend must not remove settings, provider selection, drafts or
    # the reconnect action from the Game Mode UI.
    key=(provider,remote_host)
    try:
        result=_get_snapshot()
        snapshot_cache[key]=result
        return result
    except Exception as exc:
        previous=snapshot_cache.get(key,{})
        return {**previous,'ready':False,'status':str(exc)[:350],
            'provider':provider,'remoteHost':remote_host,'sshHosts':ssh_hosts(),
            'account':previous.get('account'),'loginPending':bool(account_login_id),
            'threads':previous.get('threads',[]),'threadId':previous.get('threadId',thread_id),
            'messages':previous.get('messages',[]),'active':False,
            'models':previous.get('models',[]),'model':previous.get('model',''),
            'effort':previous.get('effort',''),'tier':previous.get('tier','default'),
            'screenshots':previous.get('screenshots',[]),'videos':previous.get('videos',[]),
            'outbox':outbox[-8:],'speechVersion':2,'speechReady':multilingual_ready(APP_DIR),'voiceId':voice_id,'voiceState':voice_state,'voiceText':voice_text,'voiceError':voice_error}
cache_screens=[];cache_media=[];cache_media_time=0;model_catalog=[];model_cache_time=0

def voice_capture(language):
    global voice_state,voice_text,voice_error,voice_stop
    stop=voice_stop
    recorder=None
    try:
        from vosk import Model,KaldiRecognizer,SetLogLevel
        SetLogLevel(-1)
        model_path=APP_DIR/'models'/('vosk-model-small-en-us-0.15' if language in ('en','en-fast') else 'vosk-model-small-ru-0.22')
        runtime=f"/run/user/{os.getuid()}"
        env=dict(os.environ);env.update({'HOME':str(ROOT),'XDG_RUNTIME_DIR':runtime,'PULSE_SERVER':f'unix:{runtime}/pulse/native','PULSE_COOKIE':str(ROOT/'.config/pulse/cookie')})
        source=subprocess.check_output(['/usr/bin/pactl','get-default-source'],env=env,text=True,timeout=5).strip()
        if not source or source.endswith('.monitor'):raise RuntimeError('Выбран звук игры вместо микрофона. Выберите микрофон в настройках звука Steam.')
        recorder=subprocess.Popen(['/usr/bin/ffmpeg','-nostdin','-hide_banner','-loglevel','error','-thread_queue_size','1024','-f','pulse','-i',source,'-ac','1','-ar','16000','-f','s16le','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
        recognizer=KaldiRecognizer(Model(str(model_path)),16000) if language in ('ru','en','ru-fast','en-fast') else None
        result=[];pcm=[]
        started=time.monotonic()
        while not stop.is_set() and time.monotonic()-started<90:
            block=recorder.stdout.read(4000)
            if not block:break
            pcm.append(block)
            if recognizer is None:continue
            if recognizer.AcceptWaveform(block):
                text=json.loads(recognizer.Result()).get('text','')
                if text:result.append(text)
                voice_text=' '.join(result).strip()
            else:
                partial=json.loads(recognizer.PartialResult()).get('partial','')
                voice_text=' '.join([*result,partial]).strip()
        result.append(json.loads(recognizer.FinalResult()).get('text','') if recognizer else '')
        if time.monotonic()-started>=90:voice_error='Запись ограничена 90 секундами.'
        voice_text=' '.join(x for x in result if x).strip()
        if recorder.poll() is None:recorder.terminate()
        if not language.endswith('-fast'):
            voice_state='processing'
            from speech_accuracy import refine_dictation
            voice_text=refine_dictation(b''.join(pcm),language,voice_text,APP_DIR)
        if not voice_text:voice_error='Речь не распознана. Попробуйте ещё раз.'
    except Exception as exc:voice_error=str(exc)[:280]
    finally:
        if recorder:
            if recorder.poll() is None:recorder.terminate()
            try:recorder.wait(timeout=3)
            except subprocess.TimeoutExpired:recorder.kill()
        voice_stop=None;voice_state='done'
def voice_result():
    return {'voiceId':voice_id,'voiceState':voice_state,'voiceText':voice_text,'voiceError':voice_error}

def start_voice(language):
    global voice_id,voice_state,voice_text,voice_error,voice_stop,voice_thread,voice_language
    if voice_state=='recording':
        if voice_stop:voice_stop.set()
        voice_state='stopping'
        # Streaming finalization normally needs just the current audio block.
        # Bound this wait; the UI already has the live transcript as a fallback.
        if voice_language.endswith('-fast') and voice_thread:voice_thread.join(timeout=.25)
        return voice_result()
    if voice_state in ('stopping','processing'):return voice_result()
    from speech_accuracy import SPEECH_LANGUAGES
    if language not in SPEECH_LANGUAGES and language not in ('auto','ru-fast','en-fast'):raise ValueError('Выберите язык распознавания из списка.')
    voice_id=uuid.uuid4().hex;voice_language=language;voice_text='';voice_error='';voice_stop=threading.Event();voice_state='recording'
    voice_thread=threading.Thread(target=voice_capture,args=(voice_language,),daemon=True);voice_thread.start()
    return voice_result()
def save_settings(model,effort,tier):
    if provider in provider_chats:
        chat=provider_chats[provider].get(provider_thread_ids.get(provider,''))
        if not chat:
            ident=str(uuid.uuid4());now=int(time.time())
            chat={'id':ident,'provider':provider,'name':'Новый чат','createdAt':now,'updatedAt':now,'messages':[]}
            provider_chats[provider][ident]=chat;provider_thread_ids[provider]=ident
        if model:chat['model']=model;save_provider_chats()
        return {'saved':True}
    if not model:return {'saved':False}
    with preference_lock:
        try:selected_models.update(json.loads((STATE/'model-preferences.json').read_text()))
        except (OSError,ValueError):pass
        selected_models[thread_id or '']=model;atomic(STATE/'model-preferences.json',selected_models)
        try:preferences.update(json.loads((STATE/'runtime-preferences.json').read_text()))
        except (OSError,ValueError):pass
        preferences.setdefault(thread_id or '',{})[model]={'effort':effort,'tier':tier or 'default'}
        atomic(STATE/'runtime-preferences.json',preferences)
    return {'saved':True}
def send_message(text,images,model,effort,tier):
    global thread_id,outbox,status,provider_active,provider_status
    if not isinstance(text,str) or not text.strip():raise ValueError('Введите сообщение.')
    if len(text)>30000:raise ValueError('Сообщение слишком длинное (лимит 30 000 символов).')
    selected=[archive_image(allowed_image(p),STATE) for p in (images or [])[:5]]
    if provider in provider_chats:
        if provider_active:raise RuntimeError('Дождитесь ответа текущей модели.')
        if not model:raise RuntimeError('Список моделей не загрузился. Обновите каталог и повторите попытку.')
        ident=provider_thread_ids.get(provider,'')
        chat=provider_chats[provider].get(ident)
        if not chat:
            ident=str(uuid.uuid4());now=int(time.time());chat={'id':ident,'provider':provider,'name':'New chat','createdAt':now,'updatedAt':now,'messages':[]};provider_chats[provider][ident]=chat;provider_thread_ids[provider]=ident
        if provider=='claude' and selected:raise ValueError('Claude Code не принимает вложения из Steam в этой версии. Откройте настольный Codex и приложите файл там.')
        prior=[{'role':item['role'],'content':item['text']} for item in chat.get('messages',[]) if item.get('role') in ('user','assistant')]
        message=text.strip();chat['messages'].append({'id':str(uuid.uuid4()),'role':'user','text':message,'images':[str(x) for x in selected]})
        if chat.get('name') in ('','New chat','Новый чат'):chat['name']=message.splitlines()[0][:100]
        chat['updatedAt']=int(time.time());chat['model']=model or chat.get('model')
        save_provider_chats()
        job={'provider':provider,'threadId':ident,'model':chat['model'],'text':message,'prior':prior,'images':[str(x) for x in selected],'resume':bool(chat.get('claudeStarted'))}
        provider_active=True;provider_status='Deck AI работает…'
        if provider=='claude':chat['claudeStarted']=True;save_provider_chats()
        jobs.submit(dispatch_provider_job,job)
        return {'queued':True,'threadId':ident}
    if remote_host and selected:raise ValueError('Передача локальных скриншотов на удалённый компьютер пока не включена. Текстовые сообщения и чаты работают.')
    if not bridge or not bridge.connected:connected()
    fresh_thread=not bool(thread_id)
    if not thread_id:
        result=bridge.request('thread/start',{'cwd':bridge.cwd if remote_host else str(ROOT),'ephemeral':False},timeout=35);thread=result.get('thread',result);thread_id=thread['id']
        atomic_text(STATE/('thread-id-remote-'+remote_host if remote_host else 'thread-id'),thread_id+'\n')
        try:
            path=STATE/'empty-chats.json';saved=json.loads(path.read_text()) if path.exists() else {}
            saved[thread_id]={'id':thread_id,'name':'Новый чат','updatedAt':int(time.time())};atomic(path,saved)
        except Exception:pass
    try:selected_models.update(json.loads((STATE/'model-preferences.json').read_text()))
    except (OSError,ValueError):pass
    if model:selected_models[thread_id]=model;atomic(STATE/'model-preferences.json',selected_models)
    try:preferences.update(json.loads((STATE/'runtime-preferences.json').read_text()))
    except (OSError,ValueError):pass
    preferences.setdefault(thread_id,{})[model]={'effort':effort,'tier':tier or 'default'}
    atomic(STATE/'runtime-preferences.json',preferences)
    job={'id':str(uuid.uuid4()),'threadId':thread_id,'host':remote_host,'text':text.strip(),'images':[str(x) for x in selected],'model':model,'effort':effort,'tier':tier or 'default','createdAt':int(time.time()),'status':'queued','freshThread':fresh_thread}
    outbox.append(job);atomic(STATE/'decky-outbox.json',outbox);status='Сообщение в очереди';dispatch()
    return {'queued':True,'threadId':thread_id,'jobId':job['id']}
def dispatch_provider_job(job):
    global provider_active,provider_status
    source=job['provider'];ident=job['threadId'];chat=provider_chats.get(source,{}).get(ident)
    try:
        if source=='deepseek':answer=providers.openrouter_reply(job['model'],job['prior'],job['text'],job.get('images',[]))
        elif source=='tokenharbor':answer=providers.tokenharbor_reply(job['model'],job['prior'],job['text'],job.get('images',[]))
        else:answer=providers.claude_code_reply(job['model'],ident,job['text'],str(ROOT),job.get('resume',False))
        chat['messages'].append({'id':str(uuid.uuid4()),'role':'assistant','text':answer});provider_status=('Claude' if source=='claude' else 'DeepSeek')+' ответил'
    except Exception as exc:
        error=str(exc)[:450];chat['messages'].append({'id':str(uuid.uuid4()),'role':'assistant','text':'Error: '+error});provider_status=error
    chat['updatedAt']=int(time.time());save_provider_chats();provider_active=False
def dispatch_job(job):
    global active,status,thread_id
    try:
        if not bridge or not bridge.connected:connected()
        if remote_host and job['threadId'] not in ('',None):
            bridge.queue_message(job['threadId'],job['text'],job.get('model'),job.get('effort'),job.get('tier') or 'default')
            if job in outbox:outbox.remove(job)
            atomic(STATE/'decky-outbox.json',outbox)
            active=False;status='Запрос передан удалённому Codex'
            return
        if job['threadId'] and not job.get('freshThread'):
            turns=bridge.request('thread/read',{'threadId':job['threadId'],'includeTurns':True},timeout=20).get('thread',{}).get('turns',[])
            if any(turn.get('status')=='inProgress' for turn in turns):
                job['status']='queued';active=job['threadId']==thread_id;atomic(STATE/'decky-outbox.json',outbox);return
        if job['threadId']!=thread_id:bridge.select_thread(job['threadId'])
        inputs=[{'type':'text','text':job['text'],'text_elements':[]}]
        inputs += [{'type':'localImage','path':str(allowed_image(x))} for x in job.get('images',[])]
        params={'threadId':job['threadId'],'input':inputs,'clientUserMessageId':job['id'],'serviceTier':job.get('tier') or 'default'}
        if job.get('model'):params['model']=job['model']
        if job.get('effort'):params['effort']=job['effort']
        result=bridge.request('turn/start',params,timeout=35)
        # A fast answer can complete before the start RPC returns.
        if job not in outbox or job.get('status')!='sending':return
        job['turnId']=result.get('turn',{}).get('id')
        job.pop('freshThread',None)
        job['status']='sending';job.pop('error',None);active=True;status='Deck AI работает…';atomic(STATE/'decky-outbox.json',outbox)
    except Exception as exc:
        job['status']='error';job['error']=str(exc)[:450];active=False;status=job['error'];atomic(STATE/'decky-outbox.json',outbox)
def dispatch():
    global active
    if active or any(j['status'] in ('sending','recovering') for j in outbox):return
    job=next((j for j in outbox if j['status']=='queued' and j.get('host','')==remote_host),None)
    if job:job['status']='sending';active=True;atomic(STATE/'decky-outbox.json',outbox);jobs.submit(dispatch_job,job)
def call(method,params):
    global thread_id,cache_time,status,active,remote_host,bridge,model_cache_time,account_cache_time,cache_media_time,model_catalog,account_cache,provider,provider_active,provider_status
    params=params or {}
    if method=='snapshot':return get_snapshot()
    if method=='provider':
        target=str(params.get('provider','codex'))
        if target not in ('codex','claude','deepseek','tokenharbor'):raise ValueError('Неизвестный источник моделей.')
        if provider_active:raise RuntimeError('Дождитесь ответа текущей модели перед переключением.')
        provider=target;provider_status='Готов';return get_snapshot()
    if method=='provider_key':
        if provider=='deepseek':providers.save_openrouter_key(str(params.get('key','')))
        elif provider=='tokenharbor':providers.save_tokenharbor_key(str(params.get('key','')))
        else:raise ValueError('Выберите DeepSeek через OpenRouter или TokenHarbor.')
        provider_model_cache_time[provider]=0;return {'saved':True}
    if method=='remote_host':
        host=str(params.get('host','')).strip()
        if host and (len(host)>120 or not __import__('re').fullmatch(r'[A-Za-z0-9_.@-]+',host)):
            raise ValueError('Укажите SSH-алиас или имя хоста без пробелов; настройте доступ в ~/.ssh/config.')
        if bridge and bridge.connected:
            try:bridge.ws.close() if not bridge.process else bridge.process.terminate()
            except Exception:pass
        bridge=None;remote_host=host
        try:thread_id=read_text_state(STATE/('thread-id-remote-'+host if host else 'thread-id'))
        except OSError:thread_id=''
        cache=thread_caches.get(host,[]);cache_time=thread_cache_times.get(host,0);model_catalog=model_caches.get(host,[]);model_cache_time=time.time() if model_catalog else 0;account_cache=account_caches.get(host,{'account':None});account_cache_time=time.time() if host in account_caches else 0;cache_media_time=0;active=False;status='Подключение к '+host if host else 'Локальный Codex'
        atomic_text(STATE/'remote-host',host+'\n')
        return get_snapshot()
    if method=='refresh':cache_time=0;return get_snapshot()
    if method=='select_thread':
        if provider in provider_chats:
            ident=str(params['id'])
            if ident not in provider_chats[provider]:raise ValueError('Чат не найден.')
            provider_thread_ids[provider]=ident;save_provider_chats();provider_status='Готов';return get_snapshot()
        thread_id=str(params['id']);cache_time=0;atomic_text(STATE/('thread-id-remote-'+remote_host if remote_host else 'thread-id'),thread_id+'\n');status='Готов';active=False
        try:bridge.select_thread(thread_id)
        except Exception as exc:status=str(exc)[:160]
        cache_time=0;return get_snapshot()
    if method=='new_thread':
        if provider in provider_chats:
            ident=str(uuid.uuid4());now=int(time.time());provider_chats[provider][ident]={'id':ident,'provider':provider,'name':'New chat','createdAt':now,'updatedAt':now,'messages':[]};provider_thread_ids[provider]=ident;save_provider_chats();provider_status='New chat';return get_snapshot()
        thread_id='';atomic_text(STATE/('thread-id-remote-'+remote_host if remote_host else 'thread-id'),'\n');status='Новый чат';active=False;cache_time=0;return get_snapshot()
    if method=='settings':return save_settings(params.get('model'),params.get('effort'),params.get('tier'))
    if method=='account_login':return start_account_login()
    if method=='account_cancel_login':return cancel_account_login()
    if method=='account_logout':return logout_account()
    if method=='send':return send_message(params.get('text',''),params.get('images',[]),params.get('model'),params.get('effort'),params.get('tier'))
    if method=='retry':
        job=next((j for j in outbox if j['id']==params.get('id')),None)
        if not job:raise ValueError('Сообщение не найдено.')
        if job['status']=='sending':raise ValueError('Это сообщение уже отправляется.')
        job['status']='queued';job.pop('error',None);atomic(STATE/'decky-outbox.json',outbox);dispatch();return {'queued':True}
    if method=='stop':
        if provider in provider_chats:return {'stopped':False}
        turns=bridge.request('thread/read',{'threadId':thread_id,'includeTurns':True},timeout=20).get('thread',{}).get('turns',[])
        turn=next((t for t in reversed(turns) if t.get('status')=='inProgress'),None)
        if turn:bridge.request('turn/interrupt',{'threadId':thread_id,'turnId':turn['id']});active=False;status='Ответ остановлен'
        return {'stopped':True}
    if method=='video_frames':return {'frames':video_frames(params.get('path',''))}
    if method=='voice':return start_voice(params.get('language','en'))
    if method=='open_window':
        launcher=Path.home()/'.local/bin/deck-voice'
        if not launcher.exists():launcher=Path.home()/'.local/bin/codex-steamdeck'
        subprocess.Popen([str(launcher)],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);return {'opened':True}
    raise ValueError('Неизвестная команда.')
def handle(msg):
    try:write({'id':msg.get('id'),'result':call(msg.get('method',''),msg.get('params',{}))})
    except Exception as exc:write({'id':msg.get('id'),'error':str(exc)[:550]})
def pump():
    while True:
        try:
            if provider=='codex':
                connected()
                if int(time.monotonic())%10==0:recover_outbox()
                dispatch();time.sleep(1)
            else:time.sleep(2)
        except Exception:time.sleep(5)
def main():
    load_state();threading.Thread(target=pump,daemon=True).start()
    for raw in sys.stdin:
        try:msg=json.loads(raw)
        except Exception:continue
        if msg.get('method')=='shutdown':break
        jobs.submit(handle,msg)
if __name__=='__main__':main()

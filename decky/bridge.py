#!/usr/bin/env python3
"""Small JSON-lines bridge for the Decky Quick Access plugin."""
import json, os, sys, threading, uuid, time, subprocess, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from array import array
import math
sys.path.insert(0,str(Path(__file__).resolve().parent))
from runtime_paths import resolve_app_dir,resolve_state_dir
APP_DIR=resolve_app_dir()
PLUGIN_DIR=Path(__file__).resolve().parent
for wheel in (PLUGIN_DIR/'vendor').glob('*.whl'):sys.path.insert(0,str(wheel))
MODULES_DIR=PLUGIN_DIR/'runtime'
if not (MODULES_DIR/'backend.py').is_file():MODULES_DIR=PLUGIN_DIR.parent
if not (MODULES_DIR/'backend.py').is_file():MODULES_DIR=APP_DIR
sys.path.insert(0,str(MODULES_DIR))
from chat_media import attachments,archive_image,display_text
import backend as device
from backend import Backend, ssh_command, CODEX
import providers
from speech_accuracy import multilingual_ready
from launch_repair import LaunchRepair, screenshot_dirs, valid_account
from repair_remote import RepairRemote
ROOT=Path.home(); STATE=resolve_state_dir()
STEAM=ROOT/'.local/share/Steam/userdata'
repair_services_lock = threading.Lock()
repair_services = None
READ_ONLY_BLOCKED={'send','retry','stop','new_thread','approve','file_write','share_add_key','custom_save','custom_remove','queue_front','queue_remove','account_login','account_logout','video_frames','settings'}
WATCH_INTERVAL=12
THREAD_LIST_TTL=6;HISTORY_TTL_ACTIVE=4;HISTORY_TTL_IDLE=12;VOSK_IDLE_SECONDS=180
notify_lock=threading.Lock();notifications=[];notify_seq=0;approvals={};retry_at=0.0
custom_entries=[];read_only=False;watch_hosts=[];watch_stops={};watch_backends={};watch_status={};resumed=set()
history_limits={}
snapshot_lock=threading.RLock()
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
def thread_title(tid,host=None):
    threads=cache if host is None or host==remote_host else thread_caches.get(host,[])
    for t in threads:
        if t.get('id')==tid:return t.get('name') or t.get('preview') or 'Новый чат'
    job=next((j for j in reversed(outbox) if j.get('threadId')==tid and j.get('host','')==(remote_host if host is None else host)),None)
    return (job.get('text','').strip().split('\n')[0][:120] if job else '') or 'Задача'
def notify(kind,tid,host=None,**extra):
    """Queue a notification for the Decky plugin; it polls them while the panel is closed."""
    global notify_seq
    host=remote_host if host is None else host
    with notify_lock:
        notify_seq+=1
        notifications.append({'id':notify_seq,'kind':kind,'threadId':tid,'host':host,'title':thread_title(tid,host),'at':int(time.time()),**extra})
        del notifications[:-50]
        try:atomic(STATE/'notify-history.json',{'seq':notify_seq,'items':notifications})
        except OSError:pass
def register_approval(message,host):
    p=message.get('params',{});method=message.get('method')
    tid=p.get('threadId') or p.get('thread',{}).get('id')
    key=(host+'|' if host else '')+str(message['id'])
    approvals[key]={'key':key,'id':message['id'],'threadId':tid,'host':host,'kind':method,'summary':approval_summary(p),'title':thread_title(tid,host)}
    notify('approval',tid,host=host,summary=approvals[key]['summary'])
def watch_event(host):
    """Event handler for a secondary (watched) device connection."""
    def handler(message):
        method=message.get('method');p=message.get('params',{})
        if 'id' in message and method and method.endswith('requestApproval'):register_approval(message,host);return
        if method=='turn/completed':
            tid=p.get('threadId') or p.get('thread',{}).get('id')
            notify('failed' if (p.get('turn') or {}).get('status')=='failed' else 'done',tid,host=host)
    return handler
def approval_summary(p):
    item=p.get('item') or {}
    return (p.get('command') or item.get('command') or p.get('reason') or (', '.join(str(c.get('path','')) for c in (item.get('changes') or [])[:4])) or 'Агент просит подтверждение')[:300]
def event(message):
    global active,status,account_cache_time,account_login_id
    method=message.get('method');p=message.get('params',{})
    if 'id' in message and method and method.endswith('requestApproval'):
        # Server request: the agent waits for an explicit decision from the user.
        register_approval(message,remote_host);return
    if 'id' in message and method:
        if bridge:bridge.respond(message['id'],error={'code':-32601,'message':'Deck AI does not support '+method})
        return
    if method in ('account/updated','account/login/completed'):
        account_cache_time=0
        if method=='account/login/completed':
            account_login_id=''
    tid=p.get('threadId') or p.get('thread',{}).get('id')
    turn=p.get('turn') or {}
    turn_id=turn.get('id') or p.get('turnId')
    selected=tid==thread_id
    if tid:
        # Live events make the cached history stale: the next snapshot re-reads
        # it at once instead of waiting for the idle refresh interval.
        history_cache_times[(remote_host,tid)]=0
    if method=='turn/started' and selected:
        active=True;status='Deck AI работает…'
    if method=='turn/completed':
        if selected:active=False;status='Готов'
        notify('failed' if turn.get('status')=='failed' else 'cancelled' if turn.get('status') in ('interrupted','cancelled') else 'done',tid)
        sending=next((j for j in outbox if j.get('host','')==remote_host and j['threadId']==tid and j.get('status')=='sending' and (not j.get('turnId') or j['turnId']==turn_id)),None)
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
        failed=next((j for j in outbox if j.get('host','')==remote_host and j['threadId']==tid and j.get('status')=='sending' and (not j.get('turnId') or j['turnId']==turn_id)),None)
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
    ensure_custom()
    try:
        saved=json.loads((STATE/'provider-chats.json').read_text())
        for key in provider_chats:provider_chats[key]=saved.get('chats',{}).get(key,{})
        provider_thread_ids.update(saved.get('selected',{}))
    except (OSError,ValueError,TypeError):pass
    global read_only,watch_hosts,notify_seq
    read_only=(STATE/'read-only').exists()
    try:
        saved=json.loads((STATE/'notify-history.json').read_text())
        notify_seq=int(saved.get('seq',0));notifications[:]=saved.get('items',[])[-50:]
    except (OSError,ValueError,TypeError):pass
    try:watch_hosts=[h for h in json.loads((STATE/'watch-hosts.json').read_text()) if valid_host(h)]
    except (OSError,ValueError,TypeError):watch_hosts=[]
def valid_host(host):
    return device.valid_ssh_host(host)
def recover_outbox():
    """Confirm persisted sends against server turns; never replay an ambiguous send."""
    global active
    if not bridge or not bridge.connected:return
    if remote_host:
        # Without a persisted turn ID a remote send cannot be confirmed safely.
        for job in outbox:
            if job.get('host','')==remote_host and job.get('status')=='recovering' and not job.get('turnId'):job['status']='error';job['error']='Проверьте удалённый чат перед повторной отправкой.'
        atomic(STATE/'decky-outbox.json',outbox)
    for job in list(outbox):
        if job.get('host','')!=remote_host or job.get('status') not in ('recovering','sending'):continue
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
        status='Подключаю Codex…';host=remote_host
        candidate=Backend(lambda message:event(message) if host==remote_host else None,lambda:None,host)
        try:
            candidate.connect(None);bridge=candidate;status='Готов' if thread_id else 'Создайте чат';recover_outbox()
        except Exception as exc:
            candidate.close();bridge=None;status='Codex недоступен: '+str(exc)[:170];raise RuntimeError(status)
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
    if cache and not force and time.time()-cache_time<THREAD_LIST_TTL:return
    if key in thread_caches and not force:
        cache=thread_caches[key];cache_time=thread_cache_times.get(key,0)
        if time.time()-cache_time<THREAD_LIST_TTL:return
    response=bridge.request('thread/list',{'limit':50,'sortKey':'updated_at','archived':False},timeout=22)
    cache=response.get('data',[]);cache_time=time.time();thread_caches[key]=cache;thread_cache_times[key]=cache_time
    jobs.submit(subscribe_running,bridge,key,list(cache))
def thread_running(thread,selected=False,selected_active=False):
    """True when the server reports the thread as executing a turn."""
    if selected and selected_active:return True
    state=thread.get('status')
    if isinstance(state,dict):state=state.get('type')
    return state in ('active','inProgress','running')
def thread_summary(thread):
    running=thread_running(thread,thread.get('id')==thread_id,active)
    return {'id':thread['id'],'name':thread.get('name') or thread.get('preview') or 'Новый чат','updatedAt':thread.get('updatedAt') or thread.get('createdAt') or 0,'running':running}
def subscribe_running(client,host,threads):
    """Resume running chats once so their events (completion, approvals) reach us."""
    for t in threads:
        key=(host,t.get('id'),id(client))
        if t.get('id') and thread_running(t) and key not in resumed:
            resumed.add(key)
            try:client.request('thread/resume',{'threadId':t['id'],'excludeTurns':True},timeout=30)
            except Exception:resumed.discard(key)
def extract_messages(thread,limit=40):
    """Render only the requested tail; image previews are the expensive part."""
    if limit is not None and limit <= 0:
        return []
    items = []
    for turn in reversed(thread.get("turns", [])):
        for item in reversed(turn.get("items", [])):
            kind = item.get("type")
            if kind in ("commandExecution", "fileChange"):
                row = {"id": item.get("id", ""), "role": "tool", "text": tool_text(item), "attachments": []}
            else:
                if kind == "userMessage":
                    text = "\n".join(part.get("text", "") for part in item.get("content", [])
                                     if part.get("type") == "text")
                    text = text.split("<environment_context>", 1)[0].strip()
                elif kind == "agentMessage":
                    text = item.get("text", "").strip()
                else:
                    continue
                media = attachments(item)
                text = display_text(text)
                if not text and not media:
                    continue
                role = "user" if kind == "userMessage" else "assistant"
                row = {"id": item.get("id", ""), "role": role, "text": text, "attachments": media}
            items.append(row)
            if limit is not None and len(items) == limit:
                return items[::-1]
    return items[::-1]
def tool_text(item):
    """Compact, defensive summary of a command run or file change (with diff)."""
    if item.get('type')=='commandExecution':
        out=str(item.get('aggregatedOutput') or item.get('output') or '').strip()
        code=item.get('exitCode')
        return ('$ '+str(item.get('command') or '')[:300]+('' if code is None else f'\n[код {code}]')+('\n'+out[-500:] if out else '')).strip()
    changes=item.get('changes') or []
    names=', '.join(str(c.get('path','')) for c in changes[:6])
    diff='\n'.join(str(c.get('diff','')) for c in changes[:3] if c.get('diff'))[:1200]
    return ('Изменены файлы: '+names+('\n'+diff if diff else '')).strip()
def list_screenshots(directory=None):
    found=[]
    paths = STEAM.glob('*/760/remote/*/screenshots/*') if directory is None else directory.iterdir() if directory.is_dir() else ()
    for p in paths:
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
    args=[shutil.which('ffmpeg') or '/usr/bin/ffmpeg','-nostdin','-hide_banner','-loglevel','error','-protocol_whitelist','file,crypto,data','-i',str(source),'-vf','fps=1/30:start_time=0:round=up,scale=960:-2,format=yuvj420p','-threads','2','-frames:v','4','-q:v','3',str(dest/'frame-%02d.jpg')]
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
def custom_entry(ident):
    return next((item for item in custom_entries if item['id']==ident),None)
def ensure_custom():
    """Register chat/model state for every saved custom connection."""
    global custom_entries
    custom_entries=providers.load_custom(STATE)
    for item in custom_entries:
        provider_chats.setdefault(item['id'],{});provider_thread_ids.setdefault(item['id'],'');provider_model_cache.setdefault(item['id'],[])
def provider_label(source):
    entry=custom_entry(source)
    return entry['name'] if entry else {'claude':'Claude','tokenharbor':'DeepSeek · TokenHarbor'}.get(source,'DeepSeek')
def save_custom_provider(name,base_url,models,key):
    ident=providers.save_custom(STATE,name,base_url,models,key);ensure_custom();provider_model_cache_time[ident]=0;return {'id':ident}
def remove_custom_provider(ident):
    global provider
    providers.remove_custom(STATE,ident)
    provider_chats.pop(ident,None);provider_thread_ids.pop(ident,None);provider_model_cache.pop(ident,None);provider_model_cache_time.pop(ident,None)
    ensure_custom()
    if provider==ident:provider='codex'
    save_provider_chats();return {'removed':True}
def model_list_for_provider(source):
    global provider_model_cache,provider_model_cache_time
    if provider_model_cache_time.get(source,0) and time.time()-provider_model_cache_time.get(source,0)<300:return provider_model_cache[source]
    if source=='claude':
        result=[{'id':'sonnet','name':'Claude Sonnet · latest','efforts':[],'defaultEffort':'','tiers':['default']}, {'id':'opus','name':'Claude Opus · latest','efforts':[],'defaultEffort':'','tiers':['default']}, {'id':'haiku','name':'Claude Haiku · latest','efforts':[],'defaultEffort':'','tiers':['default']}]
    elif source.startswith('custom:'):
        result=providers.custom_models(custom_entry(source))
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
    result=bridge.request('account/login/start',{'type':'chatgptDeviceCode'},timeout=20)
    account_login_id=result.get('loginId','')
    url=result.get('authUrl') or result.get('verificationUrl')
    if not url:raise RuntimeError('Codex не вернул ссылку для входа.')
    try:
        subprocess.Popen(['/usr/bin/xdg-open',url],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,env={**os.environ,'HOME':str(ROOT),'XDG_RUNTIME_DIR':f'/run/user/{os.getuid()}'})
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
        return {'ready':True,'status':provider_status,'provider':provider,'account':account.get('account'),'loginPending':bool(account_login_id),'remoteHost':remote_host,'sshHosts':ssh_hosts(),'threads':[{'id':x['id'],'name':x.get('name') or 'New chat','updatedAt':x.get('updatedAt') or x.get('createdAt') or 0} for x in sorted(chats.values(),key=lambda x:x.get('updatedAt',0),reverse=True)],'threadId':selected_id,'messages':messages,'active':provider_active,'models':provider_models,'model':selected_model,'effort':'','tier':'default','videos':cache_media if not remote_host else [],'screenshots':cache_screens if not remote_host else [],'outbox':[],'queueTotal':0,'speechVersion':2,'speechReady':multilingual_ready(APP_DIR),'voiceId':voice_id,'voiceState':voice_state,'voiceText':voice_text,'voiceError':voice_error}
    if not remote_host and now-cache_media_time>12:
        cache_screens=list_screenshots();cache_media=list_videos();cache_media_time=now
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
    current=next((t for t in cache if t.get('id')==thread_id),None);messages=[];history_total=0;history_warning=''
    if thread_id:
        history_key=(remote_host,thread_id)
        thread=history_caches.get(history_key)
        if thread is None or now-history_cache_times.get(history_key,0)>=(HISTORY_TTL_ACTIVE if active else HISTORY_TTL_IDLE):
            try:
                if thread is None and current is None:
                    _,loaded=bridge.select_thread(thread_id)
                else:
                    loaded=bridge.request('thread/read',{'threadId':thread_id,'includeTurns':True},timeout=25).get('thread')
                if not isinstance(loaded,dict):raise RuntimeError('Codex вернул неверную историю диалога.')
                thread=loaded;history_caches[history_key]=thread;history_cache_times[history_key]=now
            except Exception as exc:
                if thread is None:raise RuntimeError('Не удалось загрузить историю диалога: '+str(exc)[:220]) from exc
                history_warning='Не удалось обновить диалог. Показана сохранённая история; повторяю подключение. '+str(exc)[:140]
        active = any(t.get("status") == "inProgress" for t in thread.get("turns", []))
        limit = history_limits.get(history_key, 40)
        window = extract_messages(thread, limit=limit + 1)
        history_total = len(window)
        messages = window[-limit:]
        current_model=thread.get('model') or current_model;status='Deck AI работает…' if active else 'Готов'
    account=read_account()
    models_list=model_catalog;saved_model=selected_models.get(thread_id) or (selected_models.get('') if not thread_id else None) or current_model
    if not saved_model and models_list:saved_model=models_list[0]['id']
    pref=preferences.get(thread_id or '',{}).get(saved_model,{})
    return {'ready':True,'status':status,'provider':'codex','account':account.get('account'),'loginPending':bool(account_login_id),'remoteHost':remote_host,'sshHosts':ssh_hosts(),'threads':[thread_summary(t) for t in cache],'runningCount':sum(1 for t in cache if thread_running(t,t.get('id')==thread_id,active)),'historyWarning':history_warning,'hasOlderMessages':history_total>len(messages),'threadId':thread_id,'messages':messages,'active':active,'models':models_list,'model':saved_model,'effort':pref.get('effort'),'tier':pref.get('tier','default'),'videos':cache_media if not remote_host else [],'screenshots':cache_screens if not remote_host else [],'outbox':outbox[-200:],'queueTotal':len(outbox),'speechVersion':2,'speechReady':multilingual_ready(APP_DIR),'voiceId':voice_id,'voiceState':voice_state,'voiceText':voice_text,'voiceError':voice_error}
snapshot_cache={}
def all_tasks():
    """Running and recent chats from every device visited in this session."""
    found=[]
    for host,threads in thread_caches.items():
        for index,t in enumerate(threads):
            running=thread_running(t,host==remote_host and t.get('id')==thread_id,active)
            if running or index<5:found.append({'host':host,'id':t['id'],'name':t.get('name') or t.get('preview') or 'Новый чат','updatedAt':t.get('updatedAt') or t.get('createdAt') or 0,'running':running})
    return sorted(found,key=lambda x:(not x['running'],-x['updatedAt']))[:40]
def snapshot_extras():
    return {'approvals':[a for a in approvals.values() if a['host']==remote_host],'retryIn':max(0,int(retry_at-time.time())) if retry_at else 0,'allTasks':all_tasks(),'loadedModels':len(vosk_models),'readOnly':read_only,'customProviders':[{'id':c['id'],'name':c['name'],'baseUrl':c['baseUrl']} for c in custom_entries],'presets':[{'name':n,'url':u} for n,u in providers.CUSTOM_PRESETS],'watchHosts':watch_hosts,'watchStatus':dict(watch_status),'recentEvents':list(reversed(notifications[-15:]))}
def _safe_snapshot():
    # A failed backend must not remove settings, provider selection, drafts or
    # the reconnect action from the Game Mode UI.
    key=(provider,remote_host,thread_id)
    try:
        result={**_get_snapshot(),**snapshot_extras()}
        cache_key = (provider, remote_host, result.get("threadId", thread_id))
        snapshot_cache.pop(cache_key, None)
        snapshot_cache[cache_key] = result
        if len(snapshot_cache) > 12:
            snapshot_cache.pop(next(iter(snapshot_cache)))
        return result
    except Exception as exc:
        previous=snapshot_cache.get((provider,remote_host,thread_id),{})
        return {**previous,'ready':False,'status':str(exc)[:350],
            'provider':provider,'remoteHost':remote_host,'historyWarning':'','sshHosts':ssh_hosts(),
            'account':previous.get('account'),'loginPending':bool(account_login_id),
            'threads':previous.get('threads',[]),'threadId':previous.get('threadId',thread_id),
            'messages':previous.get('messages',[]),'active':False,
            'models':previous.get('models',[]),'model':previous.get('model',''),
            'effort':previous.get('effort',''),'tier':previous.get('tier','default'),
            'screenshots':previous.get('screenshots',[]),'videos':previous.get('videos',[]),
            'outbox':outbox[-200:],'queueTotal':len(outbox),'speechVersion':2,'speechReady':multilingual_ready(APP_DIR),'voiceId':voice_id,'voiceState':voice_state,'voiceText':voice_text,'voiceError':voice_error,**snapshot_extras()}
def get_snapshot():
    # Snapshot reads and view changes share one lock: an older read cannot
    # return another chat's messages under a newly selected thread ID.
    with snapshot_lock:return _safe_snapshot()
cache_screens=[];cache_media=[];cache_media_time=0;model_catalog=[];model_cache_time=0

vosk_models={};vosk_used=0.0;vosk_lock=threading.Lock()
def vosk_model(path):
    """Reuse loaded recognizers: loading a model on the Deck takes seconds."""
    global vosk_used
    from vosk import Model
    with vosk_lock:
        key=str(path)
        if key not in vosk_models:vosk_models[key]=Model(key)
        vosk_used=time.monotonic();return vosk_models[key]
def release_idle_models():
    # Drop cached models after a quiet period to give memory back to the game.
    with vosk_lock:
        if vosk_models and voice_state in ('idle','done') and time.monotonic()-vosk_used>VOSK_IDLE_SECONDS:vosk_models.clear()
def voice_capture(language,silence=0.0):
    global voice_state,voice_text,voice_error,voice_stop
    stop=voice_stop
    from speech_accuracy import prewarm_worker,cancel_worker
    recorder=None;refiner=None
    try:
        if language in ('ru','en','ru-fast','en-fast'):
            try:from vosk import Model,KaldiRecognizer,SetLogLevel
            except ImportError:raise RuntimeError('Для голоса откройте настольный Deck AI → Настройки → Языки и загрузите языковой пакет. Текстовый чат уже доступен.')
            SetLogLevel(-1)
        model_path=APP_DIR/'models'/('vosk-model-small-en-us-0.15' if language in ('en','en-fast') else 'vosk-model-small-ru-0.22')
        runtime=f"/run/user/{os.getuid()}"
        env=dict(os.environ);env.update({'HOME':str(ROOT),'XDG_RUNTIME_DIR':runtime,'PULSE_SERVER':f'unix:{runtime}/pulse/native','PULSE_COOKIE':str(ROOT/'.config/pulse/cookie')})
        source=subprocess.check_output(['/usr/bin/pactl','get-default-source'],env=env,text=True,timeout=5).strip()
        if not source or source.endswith('.monitor'):raise RuntimeError('Выбран звук игры вместо микрофона. Выберите микрофон в настройках звука Steam.')
        recorder=subprocess.Popen(['/usr/bin/ffmpeg','-nostdin','-hide_banner','-loglevel','error','-thread_queue_size','1024','-f','pulse','-i',source,'-ac','1','-ar','16000','-f','s16le','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
        recognizer=KaldiRecognizer(vosk_model(model_path),16000) if language in ('ru','en','ru-fast','en-fast') else None
        refiner=prewarm_worker(language,APP_DIR)
        result=[];pcm=[]
        started=time.monotonic();changed=started;previous=''
        while not stop.is_set() and time.monotonic()-started<90:
            block=recorder.stdout.read(4000)
            if not block:break
            pcm.append(block)
            if voice_text!=previous:previous=voice_text;changed=time.monotonic()
            # Optional hands-free end of phrase: stop after a pause that follows speech.
            if silence and voice_text and time.monotonic()-changed>=silence:break
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
            voice_text=refine_dictation(b''.join(pcm),language,voice_text,APP_DIR,refiner);refiner=None
        from speech_accuracy import apply_corrections
        voice_text=apply_corrections(voice_text)
        if not voice_text:voice_error='Речь не распознана. Попробуйте ещё раз.'
    except Exception as exc:voice_error=str(exc)[:280]
    finally:
        if refiner:cancel_worker(refiner)
        if recorder:
            if recorder.poll() is None:recorder.terminate()
            try:recorder.wait(timeout=3)
            except subprocess.TimeoutExpired:recorder.kill()
        voice_stop=None;voice_state='done'
def voice_result():
    return {'voiceId':voice_id,'voiceState':voice_state,'voiceText':voice_text,'voiceError':voice_error}

def start_voice(language,silence=0.0):
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
    voice_thread=threading.Thread(target=voice_capture,args=(voice_language,silence),daemon=True);voice_thread.start()
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
        elif source.startswith('custom:'):
            entry=custom_entry(source)
            if not entry:raise RuntimeError('Подключение удалено. Выберите другой сервис.')
            answer=providers.custom_reply(entry,job['model'],job['prior'],job['text'],job.get('images',[]))
        else:answer=providers.claude_code_reply(job['model'],ident,job['text'],str(ROOT),job.get('resume',False))
        chat['messages'].append({'id':str(uuid.uuid4()),'role':'assistant','text':answer});provider_status=provider_label(source)+' ответил'
    except Exception as exc:
        error=str(exc)[:450];chat['messages'].append({'id':str(uuid.uuid4()),'role':'assistant','text':'Error: '+error});provider_status=error
    chat['updatedAt']=int(time.time());save_provider_chats();provider_active=False
def dispatch_job(job):
    global active,status,thread_id
    try:
        if not bridge or not bridge.connected:connected()
        with connect_lock:client=bridge;host=remote_host
        if job.get('host','')!=host:raise RuntimeError('Устройство изменилось. Вернитесь к исходному устройству перед отправкой.')
        if job['threadId'] and not job.get('freshThread'):
            client.request('thread/resume',{'threadId':job['threadId'],'excludeTurns':True},timeout=50)
            turns=client.request('thread/read',{'threadId':job['threadId'],'includeTurns':True},timeout=20).get('thread',{}).get('turns',[])
            if any(turn.get('status')=='inProgress' for turn in turns):
                job['status']='queued';active=job['threadId']==thread_id;atomic(STATE/'decky-outbox.json',outbox);return
        if host:
            # Screenshots live on the Deck: copy them over the shared SSH link.
            image_paths=[client.upload_file(str(allowed_image(x))) for x in job.get('images',[])]
        else:
            if job['threadId']!=thread_id:client.select_thread(job['threadId'])
            image_paths=[str(allowed_image(x)) for x in job.get('images',[])]
        inputs=[{'type':'text','text':job['text'],'text_elements':[]}]
        inputs += [{'type':'localImage','path':x} for x in image_paths]
        params={'threadId':job['threadId'],'input':inputs,'clientUserMessageId':job['id'],'serviceTier':job.get('tier') or 'default'}
        if job.get('model'):params['model']=job['model']
        if job.get('effort'):params['effort']=job['effort']
        result=client.request('turn/start',params,timeout=35)
        # A fast answer can complete before the start RPC returns.
        if job not in outbox or job.get('status')!='sending':return
        job['turnId']=result.get('turn',{}).get('id')
        job['startedAt']=int(time.time())
        job.pop('freshThread',None)
        job['status']='sending';job.pop('error',None)
        if host==remote_host:active=True;status='Deck AI работает…'
        atomic(STATE/'decky-outbox.json',outbox)
    except Exception as exc:
        job['status']='error';job['error']=str(exc)[:450]
        if job.get('host','')==remote_host:active=False;status=job['error']
        atomic(STATE/'decky-outbox.json',outbox)
def dispatch():
    global active
    if active or any(j.get('host','')==remote_host and j['status'] in ('sending','recovering') for j in outbox):return
    job=next((j for j in outbox if j['status']=='queued' and j.get('host','')==remote_host),None)
    if job:job['status']='sending';active=True;atomic(STATE/'decky-outbox.json',outbox);jobs.submit(dispatch_job,job)
def watch_loop(host,stop):
    """Keep a second connection to `host` so its tasks, results and approvals are tracked in the background."""
    client=None
    while not stop.is_set():
        try:
            if host==remote_host or provider!='codex':
                # The main connection already covers the selected device.
                if client:
                    try:client.close()
                    except Exception:pass
                    client=None;watch_backends.pop(host,None)
                watch_status[host]='active';stop.wait(5);continue
            if not client or not client.connected:
                client=Backend(watch_event(host),lambda:None,host);client.connect(None);watch_backends[host]=client
            data=client.request('thread/list',{'limit':50,'sortKey':'updated_at','archived':False},timeout=22).get('data',[])
            thread_caches[host]=data;thread_cache_times[host]=time.time();subscribe_running(client,host,data)
            watch_status[host]='connected'
        except Exception:
            watch_status[host]='offline'
            if client:
                try:client.close()
                except Exception:pass
            client=None;watch_backends.pop(host,None);stop.wait(20)
        stop.wait(WATCH_INTERVAL)
    if client:
        try:client.close()
        except Exception:pass
    watch_backends.pop(host,None)
def reconcile_watchers():
    for host in list(watch_stops):
        if host not in watch_hosts:watch_stops.pop(host).set();watch_status.pop(host,None)
    for host in watch_hosts:
        if host not in watch_stops:
            stop=threading.Event();watch_stops[host]=stop;watch_status[host]='connecting'
            threading.Thread(target=watch_loop,args=(host,stop),daemon=True).start()
def set_watch(hosts):
    global watch_hosts
    clean=[h for h in dict.fromkeys(hosts or []) if valid_host(h)][:5]
    watch_hosts=clean;atomic(STATE/'watch-hosts.json',clean);reconcile_watchers();return {'hosts':clean}
def set_read_only(value):
    global read_only
    read_only=bool(value)
    flag=STATE/'read-only'
    if read_only:atomic_text(flag,'on\n')
    else:
        try:flag.unlink()
        except OSError:pass
    return {'readOnly':read_only}
def queue_front(ident):
    job=next((j for j in outbox if j['id']==ident),None)
    if not job or job['status']!='queued':raise ValueError('Двигать можно только ожидающие запросы.')
    outbox.remove(job);outbox.insert(0,job);atomic(STATE/'decky-outbox.json',outbox);return {'moved':True}
def queue_remove(ident):
    job=next((j for j in outbox if j['id']==ident),None)
    if not job:raise ValueError('Запрос не найден.')
    if job['status'] in ('sending','recovering'):raise ValueError('Этот запрос уже отправляется.')
    outbox.remove(job);cleanup_generated_images(job.get('images',[]));atomic(STATE/'decky-outbox.json',outbox);return {'removed':True}
def device_host():return remote_host
def files_call(kind,params):
    import hashlib
    host=remote_host
    if kind=='list':
        folder,names=device.list_files(host,str(params.get('path') or '~'));return {'path':folder,'entries':names}
    path=str(params.get('path',''))
    if kind=='read':
        text=device.read_file(host,path);return {'path':path,'text':text,'sha256':hashlib.sha256(text.encode('utf-8')).hexdigest()}
    return device.write_file(host,path,str(params.get('text','')),str(params.get('expected','')))
def poll_events(since):
    """Cheap call used by the plugin while the panel is closed (no server round trip)."""
    with notify_lock:
        latest=notify_seq
        if since is None:return {'latest':latest,'notifications':[]}
        return {'latest':latest,'notifications':[n for n in notifications if n['id']>int(since)]}
def decide_approval(ident,decision):
    entry=approvals.get(str(ident))
    if not entry:raise ValueError('Запрос подтверждения уже обработан.')
    if decision not in ('accept','acceptForSession','decline'):raise ValueError('Неизвестное решение.')
    target=bridge if entry['host']==remote_host else watch_backends.get(entry['host'])
    if not target or not target.connected:raise RuntimeError('Нет соединения с Codex.')
    target.respond(entry['id'],{'decision':decision});approvals.pop(str(ident),None)
    return {'decided':True}
def unload_models():
    with vosk_lock:vosk_models.clear()
    return {'loaded':0}
def diagnose():
    """One-click health report for the current device (local or SSH)."""
    checks=[]
    def add(name,ok,detail=''):checks.append({'name':name,'ok':bool(ok),'detail':str(detail)[:200]})
    def remote(command,timeout=15):
        return subprocess.run(ssh_command(remote_host,command),capture_output=True,text=True,timeout=timeout)
    if remote_host:
        for name,command in (('SSH-доступ без пароля','true'),('Codex установлен','command -v codex'),('Версия Codex','codex --version'),('Папка для скриншотов доступна','mkdir -p "$HOME/.cache/deck-ai-uploads" && test -w "$HOME/.cache/deck-ai-uploads"')):
            try:
                result=remote(command);add(name,result.returncode==0,(result.stdout or result.stderr).strip())
                if name.startswith('SSH') and result.returncode:break
            except subprocess.TimeoutExpired:
                add(name,False,'Нет ответа за 15 секунд');break
    else:
        add('Codex CLI',Path(CODEX).exists(),CODEX)
    add('Соединение с app-server',bool(bridge and bridge.connected),status)
    for label,folder in (('Модель Vosk · русский','vosk-model-small-ru-0.22'),('Модель Vosk · English','vosk-model-small-en-us-0.15')):
        add(label,(APP_DIR/'models'/folder).is_dir())
    add('Многоязычная модель Whisper',multilingual_ready(APP_DIR),'нужна только для других языков')
    for tool in ('ffmpeg','pactl'):add('Утилита '+tool,Path('/usr/bin/'+tool).exists())
    return {'checks':checks}


def launch_repair_call(method, params):
    global repair_services
    with repair_services_lock:
        if repair_services is None:
            repair = LaunchRepair(STATE, ROOT, STEAM, lambda: not read_only)
            repair_services = repair, RepairRemote(repair)
    repair, remote = repair_services
    account = params.get("account", "")
    if method == "repair_status":
        account = account if valid_account(account) else ""
        return {"case": repair.view(account), "remote": remote.local_status(account)}
    if not valid_account(account):
        raise ValueError("Откройте библиотеку Steam под своим аккаунтом.")
    if method == "repair_screenshots":
        app_id = params.get("appId")
        shortcut = params.get("shortcut", False)
        if type(app_id) is not int or not 0 < app_id <= 0xffffffff or type(shortcut) is not bool:
            raise ValueError("Выберите игру в Steam.")
        directories = screenshot_dirs(STEAM, account, app_id, shortcut)
        screenshots = [item for directory in directories for item in list_screenshots(directory)]
        return sorted(screenshots, key=lambda item: item["when"], reverse=True)[:50]
    if method == "repair_inspect":
        return repair.inspect(account, params.get("app"), params.get("screenshot", ""))
    case_id, verb = params.get("caseId"), params.get("verb")
    fields = params.get("fields") or {}
    if not isinstance(fields, dict):
        raise ValueError("Неверные параметры диагностики.")
    if verb == "pair":
        return remote.begin(account, case_id, fields.get("address"))
    if verb == "pair_confirm":
        return remote.confirm(account, fields.get("code"))
    if verb == "pair_stop":
        return remote.stop(account)
    if verb == "close":
        result = repair.command(account, case_id, verb, fields)
        remote.stop(account)
        return result
    return repair.command(account, case_id, verb, fields)


def _call(method,params):
    global thread_id,cache_time,status,active,remote_host,bridge,model_cache_time,account_cache_time,cache_media_time,model_catalog,account_cache,provider,provider_active,provider_status
    params=params or {}
    if read_only and method in READ_ONLY_BLOCKED:raise ValueError('Включён режим только чтения: действия запрещены. Отключите его в настройках.')
    if method in ("repair_status", "repair_screenshots", "repair_inspect", "repair_command"):
        return launch_repair_call(method, params)
    if method=='snapshot':return get_snapshot()
    if method=='older_messages':
        key=(remote_host,thread_id);history_limits[key]=history_limits.get(key,40)+80
        return get_snapshot()
    if method=='share_status':
        import deck_share;return deck_share.status()
    if method=='share_add_key':
        import deck_share;return deck_share.add_key(str(params.get('key','')))
    if method=='custom_save':return save_custom_provider(str(params.get('name','')),str(params.get('baseUrl','')),params.get('models',''),str(params.get('key','')))
    if method=='custom_remove':return remove_custom_provider(str(params.get('id','')))
    if method=='watch':return set_watch(params.get('hosts'))
    if method=='read_only':return set_read_only(params.get('value'))
    if method=='queue_front':return queue_front(str(params.get('id','')))
    if method=='queue_remove':return queue_remove(str(params.get('id','')))
    if method in ('file_list','file_read','file_write'):return files_call(method[5:],params)
    if method=='provider':
        target=str(params.get('provider','codex'))
        if target not in ('codex','claude','deepseek','tokenharbor') and not custom_entry(target):raise ValueError('Неизвестный источник моделей.')
        if provider_active:raise RuntimeError('Дождитесь ответа текущей модели перед переключением.')
        provider=target;provider_status='Готов';return get_snapshot()
    if method=='provider_key':
        if provider=='deepseek':providers.save_openrouter_key(str(params.get('key','')))
        elif provider=='tokenharbor':providers.save_tokenharbor_key(str(params.get('key','')))
        elif custom_entry(provider):providers.save_custom_key(provider,str(params.get('key','')))
        else:raise ValueError('Выберите сервис, для которого нужен ключ.')
        provider_model_cache_time[provider]=0;return {'saved':True}
    if method=='remote_host':
        host=str(params.get('host','')).strip()
        if host and not valid_host(host):
            raise ValueError('Укажите SSH-алиас или имя хоста без пробелов; настройте доступ в ~/.ssh/config.')
        with connect_lock:
            if bridge and bridge.connected:
                try:bridge.close()
                except Exception:pass
            bridge=None;remote_host=host
            try:thread_id=read_text_state(STATE/('thread-id-remote-'+host if host else 'thread-id'))
            except OSError:thread_id=''
            cache=thread_caches.get(host,[]);cache_time=thread_cache_times.get(host,0);model_catalog=model_caches.get(host,[]);model_cache_time=time.time() if model_catalog else 0;account_cache=account_caches.get(host,{'account':None});account_cache_time=time.time() if host in account_caches else 0;cache_media_time=0;active=False;status='Подключение к '+host if host else 'Локальный Codex'
            atomic_text(STATE/'remote-host',host+'\n')
        return get_snapshot()
    if method=='events':return poll_events(params.get('since'))
    if method=='approve':return decide_approval(params.get('id'),str(params.get('decision','')))
    if method=='diagnose':return diagnose()
    if method=='unload_models':return unload_models()
    if method=='refresh':
        cache_time=0;history_cache_times[(remote_host,thread_id)]=0
        return get_snapshot()
    if method=='select_thread':
        if provider in provider_chats:
            ident=str(params['id'])
            if ident not in provider_chats[provider]:raise ValueError('Чат не найден.')
            provider_thread_ids[provider]=ident;save_provider_chats();provider_status='Готов';return get_snapshot()
        thread_id=str(params['id']);atomic_text(STATE/('thread-id-remote-'+remote_host if remote_host else 'thread-id'),thread_id+'\n');status='Загружаю диалог…';active=False
        connected()
        try:
            _,thread=bridge.select_thread(thread_id)
            history_caches[(remote_host,thread_id)]=thread
            history_cache_times[(remote_host,thread_id)]=time.time()
            active=any(t.get('status')=='inProgress' for t in thread.get('turns',[]))
            status='Deck AI работает…' if active else 'Готов'
        except Exception as exc:status=str(exc)[:160]
        return get_snapshot()
    if method=='new_thread':
        if provider in provider_chats:
            ident=str(uuid.uuid4());now=int(time.time());provider_chats[provider][ident]={'id':ident,'provider':provider,'name':'New chat','createdAt':now,'updatedAt':now,'messages':[]};provider_thread_ids[provider]=ident;save_provider_chats();provider_status='New chat';return get_snapshot()
        thread_id='';atomic_text(STATE/('thread-id-remote-'+remote_host if remote_host else 'thread-id'),'\n');status='Новый чат';active=False;cache_time=0;return get_snapshot()
    if method=='settings':return save_settings(params.get('model'),params.get('effort'),params.get('tier'))
    if method=='account_login':return start_account_login()
    if method=='account_cancel_login':return cancel_account_login()
    if method=='account_logout':return logout_account()
    if method == "send":
        expected = params.get("expected")
        selected = provider_thread_ids.get(provider, "") if provider in provider_chats else thread_id
        current = {"provider": provider, "host": remote_host, "threadId": selected}
        if expected is not None and expected != current:
            raise ValueError("Чат или устройство изменились. Обновите экран перед отправкой.")
        return send_message(params.get("text", ""), params.get("images", []), params.get("model"),
                            params.get("effort"), params.get("tier"))
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
    if method=='voice':return start_voice(params.get('language','en'),float(params.get('silence') or 0))
    if method=='open_window':
        launcher=Path.home()/'.local/bin/deck-voice'
        if not launcher.exists():launcher=Path.home()/'.local/bin/codex-steamdeck'
        subprocess.Popen([str(launcher)],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);return {'opened':True}
    raise ValueError('Неизвестная команда.')
VIEW_COMMANDS={'send','retry','stop','settings','older_messages','snapshot','refresh','select_thread','new_thread','remote_host','provider'}
def call(method,params):
    if method in VIEW_COMMANDS:
        with snapshot_lock:return _call(method,params)
    return _call(method,params)
def handle(msg):
    try:write({'id':msg.get('id'),'result':call(msg.get('method',''),msg.get('params',{}))})
    except Exception as exc:write({'id':msg.get('id'),'error':str(exc)[:550]})
def pump():
    global retry_at
    failures=0
    while True:
        try:
            if provider=='codex':
                connected();failures=0;retry_at=0.0
                if int(time.monotonic())%10==0:recover_outbox()
                dispatch();release_idle_models();time.sleep(1)
            else:release_idle_models();time.sleep(2)
        except Exception:
            # Exponential backoff (5s..30s); the UI shows the countdown.
            failures+=1;delay=min(30,5*failures);retry_at=time.time()+delay;time.sleep(delay)
def main():
    load_state();reconcile_watchers();threading.Thread(target=pump,daemon=True).start()
    for raw in sys.stdin:
        try:msg=json.loads(raw)
        except Exception:continue
        if msg.get('method')=='shutdown':break
        jobs.submit(handle,msg)
if __name__=='__main__':main()

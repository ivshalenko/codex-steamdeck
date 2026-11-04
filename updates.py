"""GitHub release checks and a detached, recoverable Deck AI update transaction."""
import argparse,fcntl,hashlib,http.client,importlib.util,json,os,re,shutil,stat,subprocess,sys,tarfile,tempfile,threading,time,urllib.error,urllib.parse,urllib.request,uuid,zipfile
from pathlib import Path,PurePosixPath
try:
 from runtime_paths import resolve_app_dir,resolve_state_dir
except ImportError:
 from decky.runtime_paths import resolve_app_dir,resolve_state_dir

REPO='ivshalenko/codex-steamdeck'
API='https://api.github.com/repos/'+REPO
WEB='https://github.com/'+REPO
INTERVAL=7*24*60*60;PROTOCOL=1
ACTIVE={'queued','downloading','quiescing','installing','verifying','rolling-back'}
MUTATING={'quiescing','installing','verifying','rolling-back'}
VERSION_RE=re.compile(r'^(0|[1-9]\d{0,5})\.(0|[1-9]\d{0,5})\.(0|[1-9]\d{0,5})(?:-(alpha|beta|rc)\.(0|[1-9]\d{0,5}))?$')
EXTERNAL={'.local/bin/deck-ai','.local/bin/codex-steamdeck','.local/bin/deck-ai-steam','.local/bin/deck-ai-uninstall','.local/share/applications/codex-steamdeck.desktop','.local/share/icons/hicolor/256x256/apps/deck-ai.png'}

def version(value):
 match=VERSION_RE.fullmatch(str(value))
 if not match:raise ValueError('Invalid release version.')
 major,minor,patch,stage,number=match.groups()
 return (int(major),int(minor),int(patch),{'alpha':0,'beta':1,'rc':2,None:3}[stage],int(number or 0))

def read_json(path,default=None):
 try:
  path=Path(path)
  if path.stat().st_size>2_000_000:return default
  return json.loads(path.read_text())
 except (OSError,ValueError):return default

def atomic_json(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
 try:
  with os.fdopen(fd,'w') as stream:json.dump(data,stream,ensure_ascii=False);stream.flush();os.fsync(stream.fileno())
  os.replace(name,path)
 finally:
  if os.path.exists(name):os.unlink(name)

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def process_token(pid):
 try:return Path('/proc/sys/kernel/random/boot_id').read_text().strip()+':'+Path('/proc').joinpath(str(int(pid)),'stat').read_text().rsplit(')',1)[1].split()[19]
 except (OSError,ValueError,IndexError):return 'pid-'+str(pid)

def alive(pid,token=None):
 if not isinstance(pid,int) or pid<=0:return False
 try:os.kill(pid,0)
 except (OSError,OverflowError):return False
 return token is None or token==process_token(pid)

def find_plugin(home):
 found=[]
 for name in ('Deck AI','Codex'):
  folder=Path(home)/'homebrew/plugins'/name;meta=read_json(folder/'plugin.json',{})
  if meta.get('name')=='Deck AI':found.append(folder)
 if len(found)>1:raise ValueError('Remove the duplicate Deck AI plugin through Decky before updating.')
 return found[0] if found else None

def installed(home,plugin=None):
 home=Path(home);plugin=Path(plugin) if plugin else find_plugin(home);app=resolve_app_dir(home);result={}
 if plugin:
  value=read_json(plugin/'package.json',{}).get('version','');version(value);result['plugin']=value
 if (app/'app.py').is_file():
  value=(app/'VERSION').read_text().strip();version(value);result['companion']=value
 return result

def active_job(state):return read_json(Path(state)/'updates/job.json',{})

def updating(state):return active_job(state).get('phase') in ACTIVE

class Lease:
 """A process-owned activity record; no chat, paths, credentials or audio."""
 def __init__(self,state,role='desktop'):
  self.path=Path(state)/'updates/runtimes'/(str(os.getpid())+'-'+uuid.uuid4().hex+'.json');self.role=role
 def publish(self,busy=False):atomic_json(self.path,{'pid':os.getpid(),'token':process_token(os.getpid()),'role':self.role,'busy':bool(busy),'at':time.time()})
 def close(self):self.path.unlink(missing_ok=True)

def live_leases(state):
 result=[]
 for path in (Path(state)/'updates/runtimes').glob('*.json'):
  item=read_json(path,{})
  if alive(item.get('pid'),item.get('token')):result.append(item)
  else:path.unlink(missing_ok=True)
 return result

def required_names(value):
 version(value)
 return ('UPDATE-MANIFEST.json','SHA256SUMS.txt',f'deck-ai-{value}-decky.zip',f'deck-ai-{value}-steamdeck.tar.gz')

def release_candidate(releases,current,channel):
 candidates=[]
 for release in releases:
  if not isinstance(release,dict):continue
  try:
   if release.get('draft') or not release.get('published_at'):continue
   tag=release['tag_name'];value=tag[1:] if tag.startswith('v') else '';key=version(value)
   if channel=='stable' and (release.get('prerelease') or key[3]<3):continue
   if not any(key>version(v) for v in current.values()):continue
   assets={a['name']:a for a in release['assets']}
   if len(assets)!=len(release['assets']):continue
   sizes={};hashes={}
   for name in required_names(value):
    asset=assets[name];expected=WEB+'/releases/download/v'+value+'/'+name
    if asset['browser_download_url']!=expected:raise ValueError('Unexpected asset URL.')
    size=asset['size'];limit=100_000 if name.endswith('.txt') else 2_000_000 if name.endswith('.json') else 100_000_000
    if type(size) is not int or not 0<size<=limit:raise ValueError('Unexpected asset size.')
    sizes[name]=size
    if asset.get('digest'):
     if not re.fullmatch('sha256:[0-9a-f]{64}',asset['digest']):raise ValueError('Unexpected asset digest.')
     hashes[name]=asset['digest'][7:]
   candidates.append({'version':value,'url':WEB+'/releases/tag/v'+value,'notes':str(release.get('body') or '')[:6000],'sizes':sizes,'digests':hashes,'releaseId':release['id']})
  except (KeyError,TypeError,ValueError):continue
 return max(candidates,key=lambda c:version(c['version'])) if candidates else None

def request_json(url,etag=None):
 headers={'User-Agent':'Deck-AI-Updater/1','Accept':'application/vnd.github+json'}
 if etag:headers['If-None-Match']=etag
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=15) as response:
   data=response.read(8_000_001)
   if len(data)>8_000_000:raise ValueError('Release metadata exceeds the limit.')
   return json.loads(data),response.headers.get('ETag')
 except urllib.error.HTTPError as error:
  if error.code==304:return None,etag
  raise

class Controller:
 def __init__(self,home=None,plugin=None,state=None):
  self.home=Path(home) if home is not None else Path.home();self.plugin=Path(plugin) if plugin else find_plugin(self.home)
  self.state=Path(state) if state is not None else resolve_state_dir(self.home);self.root=self.state/'updates';self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
  self.stop=threading.Event();self.check_lock=threading.Lock();self.thread=None
 def prefs(self):
  data=read_json(self.root/'preferences.json',{})
  return {'automatic':data.get('automatic',True) is True,'channel':data.get('channel') if data.get('channel') in ('automatic','stable','preview') else 'automatic','notified':data.get('notified',''),'notifiedAt':data.get('notifiedAt',0)}
 def edit_prefs(self,**fields):
  fd=os.open(self.root/'preferences.lock',os.O_CREAT|os.O_RDWR,0o600)
  try:
   fcntl.flock(fd,fcntl.LOCK_EX);data=self.prefs();data.update(fields);atomic_json(self.root/'preferences.json',data)
  finally:os.close(fd)
 def configure(self,automatic,channel):
  if type(automatic) is not bool or channel not in ('automatic','stable','preview'):raise ValueError('Invalid update preferences.')
  self.edit_prefs(automatic=automatic,channel=channel)
  return self.status()
 def channel(self,current):return ('preview' if any(version(v)[3]<3 for v in current.values()) else 'stable') if self.prefs()['channel']=='automatic' else self.prefs()['channel']
 def status(self):
  current=installed(self.home,self.plugin);cache=read_json(self.root/'release.json',{});job=active_job(self.state);candidate=cache.get('candidate')
  if cache.get('channel')!=self.channel(current):candidate=None
  if candidate and (not any(version(candidate['version'])>version(v) for v in current.values()) or any(version(v)>version(candidate['version']) for v in current.values())):candidate=None
  leases=live_leases(self.state)
  return {'installed':current,'available':candidate,'preferences':self.prefs(),'channel':self.channel(current),'checkedAt':cache.get('checkedAt',0),'checkError':cache.get('error',''),'checking':self.check_lock.locked(),'job':{key:job.get(key) for key in ('id','phase','version','progress','error','note')} if job else None,'requiresInstaller':bool(job.get('requiresInstaller')),'busyDesktop':any(x.get('busy') for x in leases),'notificationId':str(int(cache.get('checkedAt',0))),'notificationPending':bool(candidate and (self.prefs()['notified']!=candidate['version'] or time.time()-self.prefs()['notifiedAt']>=INTERVAL))}
 def acknowledge(self,value):
  state=self.status()
  if not state['available'] or state['available']['version']!=value:raise ValueError('Update offer changed. Check again.')
  self.edit_prefs(notified=value,notifiedAt=time.time())
 def due(self,now=None):
  cache=read_json(self.root/'release.json',{});checked=cache.get('checkedAt',0)
  return self.prefs()['automatic'] and (not checked or (time.time() if now is None else now)-checked>=INTERVAL)
 def start(self):
  if self.thread:return
  def loop():
   self.stop.wait(15)
   while not self.stop.is_set():
    if self.due():self.check()
    self.recover_if_needed();self.stop.wait(30)
  self.thread=threading.Thread(target=loop,daemon=True);self.thread.start()
 def close(self):self.stop.set()
 def check_async(self):
  threading.Thread(target=self.check,daemon=True).start();return self.status()
 def check(self):
  if not self.check_lock.acquire(False):return
  fd=None
  try:
   fd=os.open(self.root/'check.lock',os.O_CREAT|os.O_RDWR,0o600)
   try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:return
   current=installed(self.home,self.plugin);channel=self.channel(current);old=read_json(self.root/'release.json',{})
   endpoint=API+('/releases/latest' if channel=='stable' else '/releases?per_page=50')
   try:data,etag=request_json(endpoint,old.get('etag') if old.get('channel')==channel else None)
   except urllib.error.HTTPError as error:
    if error.code!=404 or channel!='stable':raise
    data=[];etag=None
   candidate=old.get('candidate') if data is None else release_candidate(data if isinstance(data,list) else [data],{'baseline':'0.0.0-alpha.0'},channel)
   atomic_json(self.root/'release.json',{'candidate':candidate,'checkedAt':time.time(),'etag':etag,'channel':channel,'error':''})
  except Exception as exc:
   old=read_json(self.root/'release.json',{});old.update(checkedAt=time.time(),error=str(exc)[:240]);atomic_json(self.root/'release.json',old)
  finally:
   if fd is not None:os.close(fd)
   self.check_lock.release()
 def _spawn(self,job,recover=False,lockfd=None):
  folder=self.root/'jobs'/job['id'];folder.mkdir(parents=True,exist_ok=True,mode=0o700)
  runner=folder/'worker.py'
  if recover:
   if not runner.is_file() or not (folder/'runtime_paths.py').is_file():raise RuntimeError('Recovery files are missing. Run the full installer.')
  else:shutil.copyfile(Path(__file__),runner)
  runtime=Path(__file__).resolve().parent
  paths=[runtime/'runtime_paths.py',runtime/'decky/runtime_paths.py',runtime.parent/'runtime_paths.py']
  source=next((p for p in paths if p.is_file()),None)
  if not source:raise RuntimeError('Updater runtime is incomplete. Run the installer.')
  if not recover:shutil.copyfile(source,folder/'runtime_paths.py')
  if self.plugin and not recover:
   vendor=self.plugin/'vendor/websockets-15.0.1-py3-none-any.whl'
   if not vendor.is_file():raise RuntimeError('Decky update dependency is missing. Run the installer.')
   shutil.copyfile(vendor,folder/vendor.name)
  atomic_json(folder/'job.json',job)
  env=dict(os.environ);env.update(HOME=str(self.home),PYTHONNOUSERSITE='1')
  for key in tuple(env):
   if key.startswith('_PYI_') or key in ('LD_LIBRARY_PATH','LD_LIBRARY_PATH_ORIG','_MEIPASS2'):env.pop(key,None)
  command=[sys.executable,str(runner),'--job',str(folder)]
  if recover:command+=['--recover']
  if lockfd is not None:command+=['--lock-fd',str(lockfd)]
  with (folder/'worker.log').open('ab') as log:
   subprocess.Popen(command,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True,pass_fds=(lockfd,) if lockfd is not None else ())
 def begin(self,expected,restart_app=False,guard=None):
  status=self.status();candidate=status['available']
  if not candidate or candidate['version']!=expected:raise ValueError('Update offer changed. Check again.')
  if status.get('requiresInstaller'):raise ValueError('Recovery needs the full installer before another update.')
  if status['busyDesktop'] or (guard and guard()):raise ValueError('Finish active tasks, dictation and unsaved edits before updating.')
  fd=os.open(self.root/'install.lock',os.O_CREAT|os.O_RDWR,0o600)
  try:
   try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:raise ValueError('An update is already running.')
   old=active_job(self.state)
   if old.get('phase') in ACTIVE:raise ValueError('A previous update must finish or recover first.')
   job={'id':uuid.uuid4().hex,'phase':'queued','progress':0,'version':expected,'candidate':candidate,'home':str(self.home),'state':str(self.state),'plugin':str(self.plugin) if self.plugin else None,'restartApp':bool(restart_app),'changed':False,'pluginAttempted':False}
   atomic_json(self.root/'job.json',job)
   try:self._spawn(job,lockfd=fd)
   except Exception as exc:job.update(phase='failed',error=str(exc));atomic_json(self.root/'job.json',job);raise
  finally:os.close(fd)
  return self.status()
 def recover_if_needed(self):
  job=active_job(self.state)
  if job.get('phase') not in ACTIVE or alive(job.get('pid'),job.get('token')):return
  fd=os.open(self.root/'install.lock',os.O_CREAT|os.O_RDWR,0o600)
  try:
   try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:return
   if not re.fullmatch('[0-9a-f]{32}',str(job.get('id',''))):raise ValueError('Invalid recovery record.')
   if job.get('recoveryAttempts',0)>=3:raise RuntimeError('Automatic recovery could not finish. Run the full installer.')
   job['recoveryAttempts']=job.get('recoveryAttempts',0)+1;atomic_json(self.root/'job.json',job)
   self._spawn(job,recover=True,lockfd=fd)
  except Exception as exc:
   job.update(phase='failed',requiresInstaller=True,error='Recovery could not start: '+str(exc));atomic_json(self.root/'job.json',job)
  finally:os.close(fd)

def download(url,path,limit,expected=None,progress=None):
 path=Path(path);temporary=path.with_name(path.name+'.part')
 try:
  for attempt in range(3):
   try:
    request=urllib.request.Request(url,headers={'User-Agent':'Deck-AI-Updater/1'})
    with urllib.request.urlopen(request,timeout=25) as response,temporary.open('wb') as out:
     if urllib.parse.urlsplit(response.geturl()).scheme!='https':raise ValueError('An update download redirected outside HTTPS.')
     total=response.headers.get('Content-Length');total=int(total) if total and total.isdecimal() else None
     if total is not None and total>limit:raise ValueError('Update download exceeds its size limit.')
     size=0;checksum=hashlib.sha256()
     while block:=response.read(256*1024):
      size+=len(block)
      if size>limit:raise ValueError('Update download exceeds its size limit.')
      out.write(block);checksum.update(block)
      if progress:progress(size,total)
     if total is not None and size!=total:raise http.client.IncompleteRead(b'',total-size)
     if expected and checksum.hexdigest()!=expected:raise ValueError('Update checksum mismatch. Nothing was installed.')
    os.replace(temporary,path);return
   except (urllib.error.URLError,TimeoutError,ConnectionError,http.client.IncompleteRead) as exc:
    if isinstance(exc,urllib.error.HTTPError) and exc.code not in (408,429,500,502,503,504):raise
    if attempt==2:raise
    time.sleep(attempt+1)
 finally:temporary.unlink(missing_ok=True)

def checksums(path):
 result={}
 for line in Path(path).read_text().splitlines():
  match=re.fullmatch(r'([0-9a-f]{64})  ([A-Za-z0-9][A-Za-z0-9_.-]{0,180})',line)
  if not match or match[2] in result:raise ValueError('Invalid release checksum list.')
  result[match[2]]=match[1]
 return result

def safe_relative(value):
 path=PurePosixPath(value)
 if not value or path.is_absolute() or '..' in path.parts or str(path)!=value or '\\' in value:raise ValueError('Unsafe update path.')
 return Path(*path.parts)

def unpack_source(path,destination,value):
 with tarfile.open(path) as archive:
  members=[];seen=set();total=0
  for member in archive:
   rel=safe_relative(member.name)
   if rel.parts[0]!='deck-ai-'+value or str(rel) in seen or not member.isfile():raise ValueError('Unsafe source archive.')
   seen.add(str(rel));total+=member.size
   if total>200_000_000 or len(members)>10000:raise ValueError('Source archive exceeds its limits.')
   members.append(member)
  archive.extractall(destination,members=members,**({'filter':'data'} if sys.version_info>=(3,12) else {}))
 return Path(destination)/('deck-ai-'+value)

def inspect_plugin(path,value,expected_files):
 with zipfile.ZipFile(path) as archive:
  seen=set();total=0
  for item in archive.infolist():
   rel=safe_relative(item.filename);total+=item.file_size
   if rel.parts[0]!='Deck AI' or len(rel.parts)<2 or item.is_dir() or item.filename in seen or stat.S_ISLNK(item.external_attr>>16):raise ValueError('Unsafe plugin archive.')
   if total>100_000_000 or len(seen)>2000:raise ValueError('Plugin archive exceeds its limits.')
   seen.add(item.filename);key=rel.relative_to('Deck AI').as_posix()
   if hashlib.sha256(archive.read(item)).hexdigest()!=expected_files.get(key):raise ValueError('Plugin files do not match the update manifest.')
  if {Path(name).relative_to('Deck AI').as_posix() for name in seen}!=set(expected_files):raise ValueError('Incomplete plugin archive.')
  if json.loads(archive.read('Deck AI/package.json')).get('version')!=value or json.loads(archive.read('Deck AI/plugin.json')).get('name')!='Deck AI':raise ValueError('Plugin release metadata mismatch.')

def validate_manifest(data,value):
 if not isinstance(data,dict) or data.get('protocol')!=PROTOCOL or data.get('version')!=value:raise ValueError('This release needs the full installer. Updater protocol is not supported.')
 if data.get('minimumPython')!=[3,9]:raise ValueError('This release needs the full installer for its Python requirements.')
 for group in ('appFiles','pluginFiles'):
  files=data.get(group)
  if not isinstance(files,dict) or not 1<len(files)<2000:raise ValueError('Invalid update file manifest.')
  for rel,sha in files.items():
   safe_relative(rel)
   if not re.fullmatch('[0-9a-f]{64}',str(sha)):raise ValueError('Invalid update file digest.')
 dependency=data.get('dependency',{})
 if dependency.get('name')!='websockets' or dependency.get('path')!='decky/vendor/websockets-15.0.1-py3-none-any.whl' or dependency.get('version')!='15.0.1':raise ValueError('This dependency update needs the full installer.')
 return data

class DeckyAdapter:
 def __init__(self,folder):
  for wheel in Path(folder).glob('websockets-*.whl'):sys.path.insert(0,str(wheel))
 def evaluate(self,expression,timeout=90,page_id=None):
  from websockets.sync.client import connect
  with urllib.request.urlopen('http://127.0.0.1:8080/json/list',timeout=8) as response:pages=json.loads(response.read(2_000_000))
  page=next((p for p in pages if p.get('id')==page_id),None) if page_id is not None else next((p for p in pages if p.get('title')=='SharedJSContext'),None)
  if not page:raise RuntimeError('Keep Steam and Decky running to install this update.')
  address=urllib.parse.urlsplit(page['webSocketDebuggerUrl'])
  if address.scheme!='ws' or address.hostname not in ('127.0.0.1','localhost') or address.port!=8080:raise ValueError('Unexpected Steam debugger address.')
  with connect(page['webSocketDebuggerUrl'],origin='http://localhost',max_size=2_000_000,open_timeout=8) as socket:
   socket.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':expression,'returnByValue':True,'awaitPromise':True}}))
   while True:
    reply=json.loads(socket.recv(timeout=timeout))
    if reply.get('id')!=1:continue
    result=reply.get('result',{})
    if reply.get('error') or result.get('exceptionDetails'):raise RuntimeError('Decky update request failed: '+str(reply.get('error') or result['exceptionDetails'].get('text','')))
    return result.get('result',{}).get('value')
 def ready(self):
  if self.evaluate("typeof DeckyBackend==='object'&&typeof DeckyBackend.call==='function'") is not True:raise RuntimeError('Keep Steam and Decky running to install this update.')
 def install(self,path,value,sha):
  # The user's Update button authorizes exactly this version and digest, never
  # any other plugin prompt. The detached worker survives our plugin's unload.
  args=','.join(json.dumps(x) for x in ('file://'+str(path),'Deck AI',value,sha,2))
  expression='''(async()=>await new Promise((resolve,reject)=>{
   let timer;const cleanup=()=>{clearTimeout(timer);DeckyBackend.removeEventListener('loader/add_plugin_install_prompt',handler);};
   const handler=(name,version,id,hash)=>{
    if(name!=="Deck AI"||version!==VERSION||hash!==HASH)return;
    cleanup();DeckyBackend.call('utilities/confirm_plugin_install',id).then(()=>resolve(true)).catch(reject);
   };
   DeckyBackend.addEventListener('loader/add_plugin_install_prompt',handler);
   timer=setTimeout(()=>{cleanup();reject(Error('Decky update confirmation timed out'));},60000);
   DeckyBackend.call('utilities/install_plugin',ARGS).catch(error=>{cleanup();reject(error);});
  }))()'''.replace('VERSION',json.dumps(value)).replace('HASH',json.dumps(sha)).replace('ARGS',args)
  if self.evaluate(expression) is not True:raise RuntimeError('Decky did not confirm installation.')
 def dismiss(self,value,sha):
  # Close the native modal only after this exact package has passed health checks.
  # Its own closeModal callback avoids cancelling an already completed request.
  expression="""(() => {
   for(const node of document.querySelectorAll('[role=dialog]')){
    const key=Object.keys(node).find(k=>k.startsWith('__reactFiber$')||k.startsWith('__reactInternalInstance$'));
    for(let f=key&&node[key],i=0;f&&i<60;f=f.return,i++){
     const p=f.memoizedProps||{};
     if(p.artifact==='Deck AI'&&p.version===VERSION&&p.hash===HASH&&typeof p.closeModal==='function'){
      p.closeModal();return true;
     }
    }
   }
   return false;
  })()""".replace('VERSION',json.dumps(value)).replace('HASH',json.dumps(sha))
  with urllib.request.urlopen('http://127.0.0.1:8080/json/list',timeout=8) as response:pages=json.loads(response.read(2_000_000))
  for page in pages:
   if page.get('title')=='SharedJSContext' or page.get('title','').startswith('QuickAccess') or 'browserType=4' in page.get('url',''):
    try:self.evaluate(expression,timeout=8,page_id=page['id'])
    except Exception:pass
 def health(self,value):
  deadline=time.monotonic()+25
  while time.monotonic()<deadline:
   try:
    result=self.evaluate("(async()=>{const api=window.__DECKY_SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED_deckyLoaderAPIInit.connect(2,'Deck AI');return await api.callable('update_health')();})()",timeout=10)
    if result and result.get('version')==value and result.get('protocol')==PROTOCOL:return
   except Exception:pass
   time.sleep(.5)
  raise RuntimeError('The updated plugin did not pass its startup check.')

def safe_managed(home,app,relative):
 rel=safe_relative(relative);home=Path(home);app=Path(app)
 target=home/rel
 if relative in EXTERNAL:
  for parent in [target,*target.parents]:
   if parent==home:break
   if parent.is_symlink():raise ValueError('Managed launcher contains a linked path. Use the installer.')
  return target
 try:inner=target.relative_to(app)
 except ValueError:raise ValueError('Update manifest refers outside the managed installation.')
 forbidden={'models','venv','.venv','state','sessions','logs','cache','.ssh','.aws'}
 if any(p in forbidden or p.startswith('.') for p in inner.parts) or inner.name in ('auth.json','config.toml','credentials.json'):raise ValueError('Update manifest refers to personal data.')
 if inner.parts[0] not in ('scripts','decky','docs') and len(inner.parts)>1:raise ValueError('Unexpected managed directory.')
 if inner.name not in ('VERSION','LICENSE','NOTICE') and inner.suffix not in ('.py','.sh','.json','.js','.css','.html','.png','.svg','.md','.txt','.whl','') :raise ValueError('Unexpected managed file type.')
 if inner.suffix=='' and str(inner)!='scripts/deck-ai-steam' and inner.name not in ('VERSION','LICENSE','NOTICE'):raise ValueError('Unexpected managed executable.')
 for parent in [target,*target.parents]:
  if parent==home:break
  if parent.is_symlink():raise ValueError('Managed installation contains a linked path. Use the installer.')
 return target

def clear_bytecode(app,files):
 for relative in files:
  path=Path(app)/safe_relative(relative)
  if path.suffix!='.py':continue
  cache=path.parent/'__pycache__'
  if cache.is_symlink():raise ValueError('Linked bytecode cache; use the full installer.')
  for bytecode in cache.glob(path.stem+'.*.pyc'):
   if not bytecode.is_symlink():bytecode.unlink(missing_ok=True)

class Worker:
 def __init__(self,folder,adapter=None):
  self.folder=Path(folder);self.job=read_json(self.folder/'job.json',{});self.home=Path(self.job['home']);self.state=Path(self.job['state']);self.app=resolve_app_dir(self.home)
  self.plugin=Path(self.job['plugin']) if self.job.get('plugin') else None
  if self.plugin and self.plugin not in (self.home/'homebrew/plugins/Deck AI',self.home/'homebrew/plugins/Codex'):raise ValueError('Unexpected plugin installation path.')
  self.value=self.job['version'];version(self.value);self.adapter=adapter or DeckyAdapter(self.folder)
  self.backup=read_json(self.folder/'backup.json',{});self.manifest=read_json(self.folder/'UPDATE-MANIFEST.json',None)
 def write(self,phase=None,**fields):
  self.job.update(fields)
  if phase:self.job['phase']=phase
  self.job.update(pid=os.getpid(),token=process_token(os.getpid()),at=time.time())
  atomic_json(self.folder/'job.json',self.job);atomic_json(self.state/'updates/job.json',self.job)
 def asset(self,name,limit,expected=None,progress=None):
  cache=self.state/'updates/downloads'/self.value;cache.mkdir(parents=True,exist_ok=True,mode=0o700)
  path=cache/name
  if cache.is_symlink() or path.is_symlink():raise ValueError('Update cache contains a linked path.')
  size=self.job['candidate']['sizes'].get(name)
  if not (expected and path.is_file() and path.stat().st_size==size and digest(path)==expected):
   download(WEB+'/releases/download/v'+self.value+'/'+name,path,limit,expected,progress)
  target=self.folder/name;shutil.copyfile(path,target)
  return target
 def fetch(self):
  if shutil.disk_usage(self.home).free<100_000_000:raise ValueError('Free at least 100 MB before updating.')
  self.write('downloading',progress=.03,error='');candidate=self.job['candidate'];base=WEB+'/releases/download/v'+self.value+'/'
  for name,limit in [('SHA256SUMS.txt',100_000),('UPDATE-MANIFEST.json',2_000_000)]:
   self.asset(name,limit,candidate.get('digests',{}).get(name))
  sums=checksums(self.folder/'SHA256SUMS.txt')
  if digest(self.folder/'UPDATE-MANIFEST.json')!=sums.get('UPDATE-MANIFEST.json'):raise ValueError('Update manifest checksum mismatch.')
  self.manifest=validate_manifest(read_json(self.folder/'UPDATE-MANIFEST.json'),self.value)
  needed=[]
  current=installed(self.home,self.plugin)
  self.job['updateApp']='companion' in current and version(self.value)>version(current['companion'])
  self.job['updatePlugin']='plugin' in current and version(self.value)>version(current['plugin'])
  if not self.job['updateApp'] and not self.job['updatePlugin']:raise ValueError('The installed components are already current.')
  if self.job['updateApp']:needed.append(f'deck-ai-{self.value}-steamdeck.tar.gz')
  if self.job['updatePlugin']:needed.append(f'deck-ai-{self.value}-decky.zip')
  for index,name in enumerate(needed):
   expected=sums.get(name)
   if not expected or self.manifest['packages'].get(name)!=expected:raise ValueError('Package checksum is missing or inconsistent.')
   if candidate.get('digests',{}).get(name,expected)!=expected:raise ValueError('Release metadata and package digest differ.')
   def progress(size,total):self.write(progress=min(.55,.08+.45*(index+(size/total if total else .2))/len(needed)))
   self.asset(name,100_000_000,expected,progress)
   if (self.folder/name).stat().st_size!=candidate['sizes'][name]:raise ValueError('Release package size changed. Check for updates again.')
  if self.job['updatePlugin']:inspect_plugin(self.folder/f'deck-ai-{self.value}-decky.zip',self.value,self.manifest['pluginFiles'])
  if self.job['updateApp']:
   source=unpack_source(self.folder/f'deck-ai-{self.value}-steamdeck.tar.gz',self.folder,self.value)
   if (source/'VERSION').read_text().strip()!=self.value:raise ValueError('Companion release version mismatch.')
   for rel,sha in self.manifest['appFiles'].items():
    safe_managed(self.home,self.app,str(self.app.relative_to(self.home)/safe_relative(rel)))
    if digest(source/rel)!=sha:raise ValueError('Companion source does not match the release manifest.')
   if not os.access(self.app/'venv/bin/python',os.X_OK):raise ValueError('The desktop environment needs repair. Run the full installer.')
   probe=subprocess.run([str(self.app/'venv/bin/python'),'-c','import websockets; print(websockets.__version__)'],capture_output=True,text=True,timeout=15)
   if probe.returncode or probe.stdout.strip()!='15.0.1':raise ValueError('The desktop dependency needs repair. Run the full installer.')
  self.write(progress=.58)
 def quiesce(self):
  if self.job.get('updatePlugin'):self.adapter.ready()
  self.write('quiescing',progress=.6)
  deadline=time.monotonic()+18
  while True:
   leases=live_leases(self.state)
   if any(x.get('busy') for x in leases):raise ValueError('Active desktop work started. Finish it and retry the update.')
   if not leases:return
   if time.monotonic()>deadline:raise RuntimeError('Close the desktop app before updating. Your current files were not changed.')
   time.sleep(.3)
 def snapshot(self):
  self.backup={'files':{},'app':bool(self.job.get('updateApp'))}
  if self.job.get('updateApp'):
   old=read_json(self.app/'install-manifest.json',None)
   if not old or not isinstance(old.get('files'),dict):raise ValueError('No managed companion manifest. Run the full installer.')
   paths=set(old['files'])|{str(self.app.relative_to(self.home)/safe_relative(rel)) for rel in self.manifest['appFiles']}|EXTERNAL|{str((self.app/'install-manifest.json').relative_to(self.home))}
   for index,relative in enumerate(sorted(paths)):
    target=safe_managed(self.home,self.app,relative)
    if target.exists() and not target.is_file():raise ValueError('Unexpected managed destination.')
    item={'present':target.exists()}
    if target.exists():
     saved=self.folder/'old-app'/str(index);saved.parent.mkdir(exist_ok=True,mode=0o700);shutil.copyfile(target,saved)
     item.update(backup=str(saved.relative_to(self.folder)),sha256=digest(saved),mode=stat.S_IMODE(target.stat().st_mode))
    self.backup['files'][relative]=item
  if self.job.get('updatePlugin'):
   old_version=read_json(self.plugin/'package.json',{}).get('version');version(old_version)
   archive=self.folder/'old-plugin.zip';files={};total=0
   with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as output:
    for path in sorted(self.plugin.rglob('*')):
     if '__pycache__' in path.parts:continue
     if path.is_symlink():raise ValueError('Plugin contains a linked file. Use the full installer.')
     if not path.is_file():continue
     total+=path.stat().st_size
     if total>100_000_000 or len(files)>2000:raise ValueError('Plugin backup exceeds its limits.')
     rel=path.relative_to(self.plugin);files[rel.as_posix()]=digest(path);output.write(path,str(Path(self.plugin.name)/rel))
   self.backup.update(plugin={'version':old_version,'archive':'old-plugin.zip','sha256':digest(archive),'files':files})
  atomic_json(self.folder/'backup.json',self.backup)
 def apply_app(self):
  if not self.job.get('updateApp'):return
  self.write(changed=True,appAttempted=True)
  source=self.folder/('deck-ai-'+self.value)
  subprocess.run([sys.executable,str(source/'scripts/manage-install.py'),'install',str(source)],check=True,timeout=120,env={**os.environ,'HOME':str(self.home)})
  current=read_json(self.app/'install-manifest.json',{})
  # Keep the committed output hashes as rollback guards, including launchers.
  self.backup['newFiles']=current.get('files',{});self.backup['newFiles'][str((self.app/'install-manifest.json').relative_to(self.home))]=digest(self.app/'install-manifest.json')
  atomic_json(self.folder/'backup.json',self.backup)
  clear_bytecode(self.app,self.manifest['appFiles'])
 def verify(self):
  if self.job.get('updateApp'):
   for rel,sha in self.manifest['appFiles'].items():
    if digest(self.app/rel)!=sha:raise RuntimeError('The updated companion failed verification.')
   subprocess.run([str(self.app/'venv/bin/python'),'-c','import app,websockets'],cwd=self.app,check=True,timeout=30,env={**os.environ,'HOME':str(self.home)})
  if self.job.get('updatePlugin'):
   current=find_plugin(self.home)
   if not current:raise RuntimeError('Decky did not retain the updated plugin.')
   for rel,sha in self.manifest['pluginFiles'].items():
    if digest(current/rel)!=sha:raise RuntimeError('The updated plugin failed verification.')
   self.adapter.health(self.value)
   if hasattr(self.adapter,'dismiss'):
    try:self.adapter.dismiss(self.value,digest(self.folder/f'deck-ai-{self.value}-decky.zip'))
    except Exception:pass
 def rollback(self):
  self.write('rolling-back',progress=.85)
  self.backup=read_json(self.folder/'backup.json',{});errors=[]
  if self.job.get('appAttempted'):
   committed=read_json(self.app/'install-manifest.json',{})
   committed_hashes=committed.get('files',{}) if committed.get('version')==self.value else {}
   if committed_hashes:committed_hashes[str((self.app/'install-manifest.json').relative_to(self.home))]=digest(self.app/'install-manifest.json')
   for relative,item in self.backup.get('files',{}).items():
    try:
     target=safe_managed(self.home,self.app,relative);expected=self.backup.get('newFiles',{}).get(relative) or committed_hashes.get(relative)
     if expected is None:
      try:expected=(self.manifest or {}).get('appFiles',{}).get(target.relative_to(self.app).as_posix())
      except ValueError:pass
     if target.exists() and digest(target) not in (expected,item.get('sha256')):raise ValueError('A file changed after installation; its edit was preserved.')
     if item['present']:
      saved=self.folder/safe_relative(item['backup'])
      if digest(saved)!=item['sha256']:raise ValueError('Rollback backup checksum mismatch.')
      target.parent.mkdir(parents=True,exist_ok=True);fd,name=tempfile.mkstemp(prefix='.deck-ai-rollback-',dir=target.parent);os.close(fd)
      try:shutil.copyfile(saved,name);os.chmod(name,item['mode']);os.replace(name,target)
      finally:Path(name).unlink(missing_ok=True)
     elif target.exists():target.unlink()
    except Exception as exc:errors.append(str(exc))
  if self.job.get('appAttempted'):
   clear_bytecode(self.app,[str((self.home/relative).relative_to(self.app)) for relative in self.backup.get('files',{}) if (self.home/relative).is_relative_to(self.app)])
  old=self.backup.get('plugin')
  if self.job.get('pluginAttempted') and old:
   try:
    archive=self.folder/safe_relative(old['archive'])
    if digest(archive)!=old['sha256']:raise ValueError('Plugin rollback checksum mismatch.')
    self.adapter.install(archive,old['version'],old['sha256']);self.adapter.health(old['version'])
    if hasattr(self.adapter,'dismiss'):
     self.adapter.dismiss(old['version'],old['sha256'])
     package=self.folder/f'deck-ai-{self.value}-decky.zip'
     if package.is_file():self.adapter.dismiss(self.value,digest(package))
   except Exception as exc:errors.append('Plugin rollback: '+str(exc))
  if errors:raise RuntimeError('Recovery needs the full installer. '+errors[0])
 def cleanup(self):
  jobs=[]
  for folder in (self.state/'updates/jobs').glob('*'):
   if folder.is_symlink() or not folder.is_dir() or not re.fullmatch('[0-9a-f]{32}',folder.name):continue
   item=read_json(folder/'job.json',{})
   if item.get('phase') in ACTIVE or item.get('requiresInstaller') or folder==self.folder:continue
   if item.get('phase') in ('completed','failed'):jobs.append((item.get('at',0),folder))
  for _,folder in sorted(jobs,reverse=True)[1:]:shutil.rmtree(folder)
  releases=[]
  for folder in (self.state/'updates/downloads').glob('*'):
   if folder.is_symlink() or not folder.is_dir() or folder.name==self.value:continue
   try:releases.append((version(folder.name),folder))
   except ValueError:continue
  for _,folder in sorted(releases,reverse=True)[1:]:shutil.rmtree(folder)
 def run(self,recover=False):
  self.write()
  try:
   if recover:
    if self.job.get('changed') or self.job.get('pluginAttempted'):self.rollback()
    self.write('failed',progress=0,error='An interrupted update was recovered. Check the installed version before retrying.');return
   self.fetch();self.quiesce();self.snapshot();self.write('installing',progress=.65)
   self.apply_app()
   if self.job.get('updatePlugin'):
    self.write(changed=True,pluginAttempted=True,progress=.75)
    package=self.folder/f'deck-ai-{self.value}-decky.zip';self.adapter.install(package,self.value,digest(package))
   self.write('verifying',progress=.9);self.verify();self.write('completed',progress=1,error='')
   if self.job.get('restartApp'):
    try:subprocess.Popen([str(self.home/'.local/bin/deck-ai')],start_new_session=True,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except OSError:self.write(note='Updated. Reopen Deck AI from the application menu.')
  except Exception as exc:
   message=str(exc)
   if self.job.get('changed') or self.job.get('pluginAttempted'):
    try:self.rollback();message+=' Previous files were restored.'
    except Exception as recovery:self.job['requiresInstaller']=True;message+=' '+str(recovery)
   if 'full installer' in message.lower():self.job['requiresInstaller']=True
   self.write('failed',progress=0,error=message[:600])

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--job',type=Path,required=True);parser.add_argument('--recover',action='store_true');parser.add_argument('--lock-fd',type=int);args=parser.parse_args()
 root=resolve_state_dir()/'updates';folder=args.job.absolute()
 if folder.parent!=root/'jobs' or not re.fullmatch('[0-9a-f]{32}',folder.name) or folder.is_symlink():raise ValueError('Invalid update job directory.')
 worker=Worker(folder)
 if worker.home!=Path.home() or worker.state!=resolve_state_dir():raise ValueError('Update job belongs to another user.')
 fd=args.lock_fd
 if fd is None:
  fd=os.open(root/'install.lock',os.O_CREAT|os.O_RDWR,0o600);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:
  worker.run(args.recover)
  try:worker.cleanup()
  except OSError:pass
 finally:os.close(fd)
if __name__=='__main__':main()

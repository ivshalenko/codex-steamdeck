"""Apply/restore only Deck AI shortcut art through Steam's own native API."""
import base64,fcntl,hashlib,json,os,re,shutil,struct,time,uuid
from pathlib import Path
KINDS={0:('capsule','p'),1:('hero','_hero'),2:('logo','_logo'),3:('header','')}
STEAM_ID_BASE=76561197960265728

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read_json(path):
 try:return json.loads(Path(path).read_text())
 except (OSError,ValueError):return {}
def shortcuts(data):
 if len(data)>8_000_000:raise ValueError('Shortcut file exceeds the limit.')
 offset=0
 def read(depth=0):
  nonlocal offset
  if depth>12:raise ValueError('Invalid shortcut nesting.')
  out={}
  while offset<len(data):
   kind=data[offset];offset+=1
   if kind==8:return out
   end=data.index(b'\0',offset);key=data[offset:end].decode();offset=end+1
   if kind==0:value=read(depth+1)
   elif kind==1:end=data.index(b'\0',offset);value=data[offset:end].decode();offset=end+1
   elif kind in (2,3,4,6):value=struct.unpack_from('<I',data,offset)[0];offset+=4
   elif kind==7:value=struct.unpack_from('<Q',data,offset)[0];offset+=8
   else:raise ValueError('Invalid shortcut field.')
   out[key]=value
  raise ValueError('Incomplete shortcut file.')
 return read().get('shortcuts',{})

def payload(plugin,home):
 plugin=Path(plugin);home=Path(home);manifest=read_json(plugin/'artwork/manifest.json');images=[]
 if set(manifest.get('files',{}))!={v[0]+'.png' for v in KINDS.values()}|{'icon.png'}:raise ValueError('Library artwork is incomplete. Reinstall Deck AI.')
 for kind,(name,_) in [*KINDS.items(),(4,('icon',''))]:
  path=plugin/'artwork'/(name+'.png');meta=manifest['files'][path.name]
  if path.is_symlink() or not path.is_file() or path.stat().st_size>8_000_000:raise ValueError('Invalid packaged artwork.')
  data=path.read_bytes()
  if not data.startswith(b'\x89PNG\r\n\x1a\n') or hashlib.sha256(data).hexdigest()!=meta['sha256'] or list(struct.unpack('>II',data[16:24]))!=meta['size']:raise ValueError('Artwork verification failed. Reinstall Deck AI.')
  if kind<4:images.append({'kind':kind,'data':base64.b64encode(data).decode(),'sha256':meta['sha256']})
 launchers=[home/'.local/bin'/name for name in ('deck-ai-steam','deck-ai','codex-steamdeck')]
 from runtime_paths import resolve_app_dir
 app=resolve_app_dir(home)
 return {'images':images,'launchers':[str(p) for p in launchers],'exe':str(launchers[0]),'directory':str(app),'icon':str(app/'deck-ai.png'),'available':launchers[0].is_file() and (app/'app.py').is_file()}

TARGET_JS='''(async()=>{
 const p=PAYLOAD,apps=SteamClient.Apps;
 const candidates=appStore.allApps.filter(a=>a.app_type===1073741824&&String(a.display_name||'').toLowerCase()==='deck ai');
 const ids=[];
 for(const app of candidates){
  let sub,timer;
  try{
   const d=await new Promise((resolve,reject)=>{timer=setTimeout(()=>reject(Error('Steam shortcut details timed out')),4000);sub=apps.RegisterForAppDetails(app.appid,d=>{if(d?.unAppID===app.appid)resolve(d);});});
   const exe=String(d.strShortcutExe||'').trim().replace(/^"|"$/g,'');
   if(!p.launchers.includes(exe))throw Error('A different shortcut is named Deck AI. Its artwork was preserved.');
   ids.push(app.appid);
  }finally{clearTimeout(timer);sub?.unregister();}
 }
 if(ids.length>1)throw Error('Two Deck AI shortcuts exist. Remove the duplicate in Steam first.');
 let id=ids[0],created=false;
 if(!id&&CREATE){id=await apps.AddShortcut('Deck AI','"'+p.exe+'"','"'+p.directory+'"','');created=true;}
 if(!Number.isInteger(id)||id<=0)throw Error('Deck AI shortcut was not found.');
 const account=window.friendStore?.currentUserSteamID||window.uiStore?.currentUserSteamID;
 return {appid:id,created,account:typeof account==='string'?account:account?.ConvertTo64BitString()};
})()'''

def grid_for(home,target):
 account=str(target.get('account',''))
 if not re.fullmatch(r'\d{17}',account):raise ValueError('Steam account is unavailable.')
 number=int(account)-STEAM_ID_BASE
 if not 0<number<2**32:raise ValueError('Invalid Steam account.')
 steam=Path(home)/'.local/share/Steam';profile=steam/'userdata'/str(number);grid=profile/'config/grid'
 if not grid.resolve().is_relative_to(steam.resolve()) or grid.is_symlink():raise ValueError('Linked Steam artwork folder was preserved.')
 if not target['created']:
  entries=shortcuts((profile/'config/shortcuts.vdf').read_bytes());matches=[]
  for value in entries.values():
   if not isinstance(value,dict):continue
   fields={k.lower():v for k,v in value.items()}
   if fields.get('appid')==target['appid']:matches.append(fields)
  if len(matches)!=1 or str(matches[0].get('appname','')).lower()!='deck ai':raise ValueError('Steam shortcut changed. Nothing was replaced.')
  allowed={str(Path(home)/'.local/bin'/n) for n in ('deck-ai-steam','deck-ai','codex-steamdeck')}
  if str(matches[0].get('exe','')).strip('"') not in allowed:raise ValueError('The unrelated shortcut was preserved.')
  if not target['created']:target['oldIcon']=str(matches[0].get('icon',''))
 return grid

def images_at(grid,appid):
 result={}
 for kind,(_,suffix) in KINDS.items():
  for extension in ('png','jpg','jpeg'):
   p=grid/(str(appid)+suffix+'.'+extension)
   if p.is_symlink():raise ValueError('Linked custom artwork was preserved.')
   if p.is_file():
    if p.stat().st_size>16_000_000:raise ValueError('Custom artwork exceeds the backup limit.')
    result[kind]=p;break
 return result

def set_images(adapter,appid,images,icon=None,position=None):
 # Native Steam accepts base64, an image format and ELibraryAssetType.
 expression="""(async p=>{for(const i of p.images){if(i.data===null)await SteamClient.Apps.ClearCustomArtworkForApp(p.appid,i.kind);else await SteamClient.Apps.SetCustomArtworkForApp(p.appid,i.data,i.format||'png',i.kind);}if(p.icon!==null)SteamClient.Apps.SetShortcutIcon(p.appid,p.icon);if(p.position===null)await SteamClient.Apps.ClearCustomLogoPositionForApp(p.appid);else await SteamClient.Apps.SetCustomLogoPositionForApp(p.appid,JSON.stringify(p.position));return true;})"""+'('+json.dumps({'appid':appid,'images':images,'icon':icon,'position':position})+')'
 if adapter.evaluate(expression) is not True:raise RuntimeError('Steam did not confirm the artwork change.')

def status(plugin,home,state):
 root=Path(state)/'library-artwork';record=read_json(root/'latest.json')
 return {'available':(Path(home)/'.local/bin/deck-ai-steam').is_file(),'hasBackup':bool(record.get('id') and not record.get('restored')),'appId':record.get('appid'),'version':read_json(Path(plugin)/'package.json').get('version','')}

def apply(plugin,home,state,restore=False,adapter=None):
 from updates import DeckyAdapter,atomic_json
 plugin=Path(plugin);home=Path(home);root=Path(state)/'library-artwork';root.mkdir(parents=True,exist_ok=True,mode=0o700)
 fd=os.open(root/'operation.lock',os.O_CREAT|os.O_RDWR,0o600);installation=None
 try:
  try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise ValueError('Library artwork is already being changed.')
  shared=Path(state)/'updates';shared.mkdir(parents=True,exist_ok=True,mode=0o700)
  installation=os.open(shared/'install.lock',os.O_CREAT|os.O_RDWR,0o600)
  try:fcntl.flock(installation,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise ValueError('An installation or update is running. Wait before changing artwork.')
  data=payload(plugin,home)
  if not data['available']:raise ValueError('Install the desktop companion before adding Deck AI to Steam.')
  adapter=adapter or DeckyAdapter(plugin/'vendor')
  target=adapter.evaluate(TARGET_JS.replace('CREATE','false' if restore else 'true').replace('PAYLOAD',json.dumps({k:v for k,v in data.items() if k!='images'})))
  if not isinstance(target,dict) or type(target.get('appid')) is not int or not 0<target['appid']<2**32:raise ValueError('Steam returned an invalid shortcut.')
  grid=grid_for(home,target);appid=target['appid'];current=images_at(grid,appid);record=read_json(root/'latest.json');position_file=grid/(str(appid)+'.json')
  if position_file.is_symlink() or (position_file.exists() and position_file.stat().st_size>32000):raise ValueError('Invalid custom logo position.')
  old_position=read_json(position_file).get('logoPosition')
  if restore:
   if not record or record.get('appid')!=appid or record.get('account')!=target['account'] or record.get('restored'):raise ValueError('No matching artwork backup is available.')
   if {str(k):sha(p) for k,p in current.items()}!=record.get('installed') or (sha(position_file) if position_file.is_file() else None)!=record.get('positionInstalled'):raise ValueError('Artwork changed after installation. Your newer images were preserved.')
   ident=record['id']
   if not re.fullmatch('[0-9a-f]{32}',ident):raise ValueError('Invalid backup record.')
   old=[]
   for kind in KINDS:
    item=record['old'].get(str(kind));image=None
    if item:
     path=root/'backups'/ident/item['file']
     if path.parent!=root/'backups'/ident or path.is_symlink() or sha(path)!=item['sha256']:raise ValueError('Artwork backup verification failed.')
     image=base64.b64encode(path.read_bytes()).decode()
    old.append({'kind':kind,'data':image,'format':item['format'] if item else 'png'})
   present=[{'kind':kind,'data':base64.b64encode(current[kind].read_bytes()).decode() if kind in current else None,'format':'jpg' if kind in current and current[kind].suffix in ('.jpg','.jpeg') else 'png'} for kind in KINDS]
   try:
    set_images(adapter,appid,old,record.get('oldIcon',''),record.get('oldPosition'))
    expected={kind:item['sha256'] for kind,item in record['old'].items()}
    if {str(k):sha(p) for k,p in images_at(grid,appid).items()}!=expected or read_json(position_file).get('logoPosition')!=record.get('oldPosition'):raise RuntimeError('Steam did not restore the previous artwork.')
   except Exception:
    set_images(adapter,appid,present,data['icon'],old_position);raise
   record['restored']=True;atomic_json(root/'latest.json',record)
  else:
   expected={str(i['kind']):i['sha256'] for i in data['images']}
   if record.get('appid')==appid and {str(k):sha(p) for k,p in current.items()}==expected and not record.get('restored'):
    return {**status(plugin,home,state),'unchanged':True}
   ident=uuid.uuid4().hex;folder=root/'backups'/ident;folder.mkdir(parents=True,mode=0o700);old={}
   for kind,path in current.items():
    saved=folder/(str(kind)+path.suffix);shutil.copyfile(path,saved);old[str(kind)]={'file':saved.name,'sha256':sha(saved),'format':'jpg' if path.suffix in ('.jpg','.jpeg') else 'png'}
   record={'id':ident,'appid':appid,'account':target['account'],'old':old,'oldIcon':target.get('oldIcon',''),'oldPosition':old_position,'at':time.time(),'restored':False}
   atomic_json(folder/'backup.json',record)
   try:
    set_images(adapter,appid,data['images'],data['icon'],{'pinnedPosition':'BottomLeft','nWidthPct':50,'nHeightPct':50})
    after=images_at(grid,appid);record['installed']={str(k):sha(p) for k,p in after.items()};record['positionInstalled']=sha(position_file) if position_file.is_file() else None
    if record['installed']!=expected:raise RuntimeError('Steam artwork files did not pass verification. Retry the artwork action.')
   except Exception:
    rollback=[]
    for kind in KINDS:
     item=old.get(str(kind));path=folder/item['file'] if item else None
     rollback.append({'kind':kind,'data':base64.b64encode(path.read_bytes()).decode() if path else None,'format':item['format'] if item else 'png'})
    set_images(adapter,appid,rollback,record['oldIcon'],old_position);raise
   atomic_json(root/'latest.json',record)
  return {**status(plugin,home,state),'restored':restore}
 finally:
  if installation is not None:os.close(installation)
  os.close(fd)

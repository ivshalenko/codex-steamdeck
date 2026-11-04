"""Installer decisions and preference persistence, independent of GTK."""
from dataclasses import dataclass
import fcntl,json,os,shutil,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'decky'))
from runtime_paths import resolve_app_dir,resolve_state_dir

@dataclass(frozen=True)
class Options:
 language:str='en'
 mode:str='automatic'
 codex:bool=True
 decky:bool=True
 loader:bool=True
 voice:bool=False
 ssh:bool=False
 read_only:object=None
 def __post_init__(self):
  if self.language not in ('en','ru'):raise ValueError('Choose English or Russian.')
  if self.mode not in ('automatic','custom'):raise ValueError('Choose automatic or custom installation.')
  for field in ('codex','decky','loader','voice','ssh'):
   if not isinstance(getattr(self,field),bool):raise ValueError('Invalid installation choice: '+field)
  if self.read_only is not None and not isinstance(self.read_only,bool):raise ValueError('Invalid action permission.')
  if self.mode=='automatic':
   for key,value in {'codex':True,'decky':True,'loader':True,'voice':False,'ssh':False,'read_only':None}.items():object.__setattr__(self,key,value)
  elif not self.decky:
   object.__setattr__(self,'loader',False);object.__setattr__(self,'read_only',None)

def decky_installed(home=None):
 home=Path(home) if home is not None else Path.home()
 binary=home/'homebrew/services/PluginLoader'
 return binary.is_file() and binary.stat().st_size>0

def codex_installed():
 from backend import find_codex
 path=Path(find_codex());return path.is_file() and os.access(path,os.X_OK)

def atomic_text(path,text):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 if path.is_symlink() or path.parent.is_symlink():raise ValueError('Refusing to overwrite linked installer preferences.')
 fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
 try:
  with os.fdopen(fd,'w',encoding='utf-8') as stream:stream.write(text);stream.flush();os.fsync(stream.fileno())
  os.replace(name,path)
 finally:
  if os.path.exists(name):os.unlink(name)

def save_preferences(options,home=None):
 state=resolve_state_dir(home)
 atomic_text(state/'language',options.language+'\n')
 if options.voice:atomic_text(state/'voice-language',options.language+'\n')
 if options.read_only is not None:
  if options.read_only:atomic_text(state/'read-only','on\n')
  else:(state/'read-only').unlink(missing_ok=True)
 receipt={'language':options.language,'mode':options.mode,'components':{'codex':options.codex,'decky':options.decky,'voice':options.voice,'remoteAccess':options.ssh},'actionPermissions':'preserved' if options.read_only is None else 'history-only' if options.read_only else 'confirm-in-app'}
 atomic_text(state/'setup-choices.json',json.dumps(receipt,indent=2)+'\n')
 return state

def _run_install(options,root,execute,progress,home=None):
 """Execute only selected steps. Failed admin children cannot report success."""
 root=Path(root);home=Path(home) if home is not None else Path.home()
 if sys.platform!='linux':raise RuntimeError('Run this installer on Steam Deck in Desktop Mode.')
 if shutil.disk_usage(home).free<800_000_000:raise RuntimeError('Free at least 800 MB before installing.')
 terminal=shutil.which('konsole')
 if (options.decky or options.ssh) and not terminal:raise RuntimeError('Konsole is required for the visible SteamOS administrator prompt. Select desktop-only installation or install Konsole.')
 if options.decky and not options.loader and not decky_installed(home):raise RuntimeError('Decky Loader is missing. Allow its installation or uncheck the Decky plugin.')
 progress('validate',.05);execute([sys.executable,str(root/'scripts/manage-install.py'),'validate',str(root)])
 progress('application',.16);execute(['bash',str(root/'install.sh')]);save_preferences(options,home)
 if options.codex:
  progress('codex',.4)
  if not codex_installed():execute([sys.executable,str(root/'scripts/install-codex.py')])
  if not codex_installed():raise RuntimeError('Codex installation finished but the CLI was not found. Retry or select desktop-only setup.')
 if options.voice:
  progress('voice',.58);app=resolve_app_dir(home)
  execute([str(app/'venv/bin/python'),str(app/'scripts/setup-voice.py'),'--language',options.language])
 if options.decky or options.ssh:
  progress('system',.74)
  with tempfile.TemporaryDirectory(prefix='deck-ai-admin-') as folder:
   receipt=Path(folder)/'result.json'
   command=[terminal,'--separate','--nofork','-e',sys.executable,str(root/'scripts/setup-system.py'),'--receipt',str(receipt),'--language',options.language]
   if options.decky:command+=['--decky']
   if options.loader:command+=['--allow-loader']
   if options.ssh:command+=['--ssh']
   execute(command)
   try:result=json.loads(receipt.read_text())
   except (OSError,ValueError):raise RuntimeError('Administrator setup was closed or cancelled. No completion was confirmed. Click Retry to continue.')
   if result.get('ok') is not True:raise RuntimeError(result.get('error') or 'Administrator setup failed. Click Retry to continue.')
 progress('ready',1.0)
 return resolve_app_dir(home)


def run_install(options,root,execute,progress,home=None):
 if sys.platform!='linux':raise RuntimeError('Run this installer on Steam Deck in Desktop Mode.')
 selected_home=Path(home) if home is not None else Path.home();folder=resolve_state_dir(selected_home)/'updates';folder.mkdir(parents=True,exist_ok=True,mode=0o700)
 fd=os.open(folder/'install.lock',os.O_CREAT|os.O_RDWR,0o600)
 try:
  try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise RuntimeError('An update is running. Wait for it to finish before installing.')
  app=_run_install(options,root,execute,progress,selected_home)
  # A successful full installer can repair a failed background transaction.
  import updates
  job=updates.active_job(resolve_state_dir(selected_home))
  if job:
   complete=(not job.get('plugin') or options.decky) and (Path(app)/'VERSION').is_file()
   if complete:
    job.update(phase='completed',progress=1,error='',requiresInstaller=False,version=(Path(app)/'VERSION').read_text().strip(),note='Installed with the full installer.')
    updates.atomic_json(folder/'job.json',job)
  return app
 finally:os.close(fd)


def plugin_destination(home=None):
 home=Path(home) if home is not None else Path.home();parent=home/'homebrew/plugins';found=[]
 for name in ('Deck AI','Codex'):
  folder=parent/name
  try:recognized=json.loads((folder/'plugin.json').read_text()).get('name') in ('Deck AI','Codex')
  except (OSError,ValueError,AttributeError):recognized=False
  if recognized:found.append(folder)
 if len(found)>1:raise ValueError('Two Deck AI copies exist. Remove the duplicate through Decky before updating. Both folders were preserved.')
 return found[0] if found else parent/'Deck AI'

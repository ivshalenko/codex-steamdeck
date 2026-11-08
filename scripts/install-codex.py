#!/usr/bin/env python3
"""Run a checksum-pinned official OpenAI installer from its official GitHub source."""
import hashlib,json,os,re,shlex,shutil,ssl,subprocess,sys,tempfile,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path
VERSION='0.166.0'
URL='https://raw.githubusercontent.com/openai/codex/rust-v'+VERSION+'/scripts/install/install.sh'
SHA256='44ac252c1b9a68c02bdf0de8e1c6cbfde36fc1afa8684624962eae7d4c461e70'
API='https://api.github.com/repos/openai/codex'
PREFIX='https://github.com/openai/codex/releases/download/rust-v'+VERSION+'/'
ASSETS={'codex-package_SHA256SUMS','codex-package-x86_64-unknown-linux-musl.tar.gz','codex-package-aarch64-unknown-linux-musl.tar.gz'}
HEADERS={'User-Agent':'Deck-AI-Codex-Setup/1'}
VENDORED_INSTALLER=Path(__file__).resolve().parent/'vendor/codex-install-0.166.0.sh'
# Reviewed against OpenAI's published rust-v0.166.0 release. Do not resolve the
# release again at install time: its metadata endpoint can itself return 500.
PINS={
 'codex-package_SHA256SUMS':(689706950,3095,'e5d5125d31db6459a0ebebefd8e7b6020a648032cb8682595ac39d5c62cd147d'),
 'codex-package-x86_64-unknown-linux-musl.tar.gz':(689712510,199694962,'1d44b28bc4ac9937d7d3532264baa68a507ce364956a0d4ebb856f331cdee254'),
 'codex-package-aarch64-unknown-linux-musl.tar.gz':(689706667,187370368,'7821b77dda2e6283fb1f63f3165177a271da8833e857cf673c6ca1c9db3bfcc6'),
}

def pinned_metadata():
 return {'tag_name':'rust-v'+VERSION,'assets':[{'name':name,'digest':'sha256:'+pin[2]} for name,pin in PINS.items()]}

def check_file(path,name):
 path=Path(path);_,size,digest=PINS[name]
 if path.is_symlink() or not path.is_file() or path.stat().st_size!=size:raise ValueError('Codex bundle file is missing or incomplete: '+name)
 checksum=hashlib.sha256()
 with path.open('rb') as stream:
  while block:=stream.read(1024*1024):checksum.update(block)
 if checksum.hexdigest()!=digest:raise ValueError('Codex release asset checksum mismatch; nothing was installed.')
 return path

def response(url,accept=None):
 headers={**HEADERS}
 if accept:headers['Accept']=accept
 result=urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30)
 if urllib.parse.urlsplit(result.geturl()).scheme!='https':
  result.close();raise ValueError('Codex download redirected outside HTTPS.')
 return result

def download_asset(url,destination,use_bundle=True):
 """Use the full installer bundle, or pinned official assets for CLI repairs."""
 name=url[len(PREFIX):] if url.startswith(PREFIX) else ''
 if name not in ASSETS:raise ValueError('Unexpected Codex release asset.')
 ident,size,pinned_digest=PINS[name];digest='sha256:'+pinned_digest
 endpoint=API+'/releases/assets/'+str(ident)
 bundle=os.environ.get('DECK_AI_CODEX_BUNDLE_DIR') if use_bundle else None
 if bundle:
  source=check_file(Path(bundle)/name,name);destination=Path(destination);temporary=None
  try:
   fd,temporary=tempfile.mkstemp(prefix='.'+destination.name+'-',dir=destination.parent)
   with os.fdopen(fd,'wb') as output,source.open('rb') as stream:shutil.copyfileobj(stream,output)
   check_file(temporary,name);os.replace(temporary,destination)
  finally:
   if temporary and os.path.exists(temporary):os.unlink(temporary)
  print('Using verified bundled Codex: '+name,file=sys.stderr,flush=True);return
 try:stream=response(url)
 except (urllib.error.URLError,TimeoutError,ConnectionError) as error:
  if isinstance(error,urllib.error.HTTPError) and error.code not in (408,429,500,502,503,504):raise
  if isinstance(error,urllib.error.URLError) and isinstance(error.reason,ssl.SSLCertVerificationError):raise
  if isinstance(error,urllib.error.HTTPError) and error.fp is not None:error.close()
  print('Codex download interrupted; retrying the same verified asset through the official GitHub API.',file=sys.stderr,flush=True)
  stream=response(endpoint,'application/octet-stream')
 destination=Path(destination);temporary=None
 try:
  with stream:
   fd,temporary=tempfile.mkstemp(prefix='.'+destination.name+'-',dir=destination.parent)
   with os.fdopen(fd,'wb') as output:
    total=0;checksum=hashlib.sha256()
    while True:
     block=stream.read(1024*1024)
     if not block:break
     total+=len(block)
     if total>size:raise ValueError('Codex download exceeds the published size.')
     checksum.update(block);output.write(block)
   if total!=size:raise ValueError('Codex download is incomplete. Please retry.')
   if checksum.hexdigest()!=digest[7:]:raise ValueError('Codex release asset checksum mismatch; nothing was installed.')
  os.replace(temporary,destination)
 finally:
  if temporary and os.path.exists(temporary):os.unlink(temporary)

def curl_proxy(arguments,real_curl):
 # This exact invocation is used by the checksum-pinned official install.sh.
 # Serve reviewed metadata locally too; do not leave an unguarded API request.
 if arguments==['-fsSL',API+'/releases/tags/rust-v'+VERSION]:
  print(json.dumps(pinned_metadata()));return 0
 if len(arguments)==4 and arguments[0]=='-fsSL' and arguments[2]=='-o' and arguments[1].startswith(PREFIX):
  download_asset(arguments[1],arguments[3]);return 0
 return subprocess.call([real_curl,*arguments])

def download(path):
 data=VENDORED_INSTALLER.read_bytes()
 if hashlib.sha256(data).hexdigest()!=SHA256:raise ValueError('Official Codex installer checksum mismatch; nothing was executed.')
 Path(path).write_bytes(data)

def prepare_bundle(directory):
 """Build-time only: fetch and verify the exact Linux x64 package for the ZIP."""
 directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
 paths=[]
 for name in ('codex-package_SHA256SUMS','codex-package-x86_64-unknown-linux-musl.tar.gz'):
  target=directory/name
  try:check_file(target,name)
  except (OSError,ValueError):
   for attempt in range(4):
    try:download_asset(PREFIX+name,target,use_bundle=False);break
    except (urllib.error.URLError,TimeoutError,ConnectionError) as error:
     if attempt==3 or isinstance(error,urllib.error.HTTPError) and error.code not in (408,429,500,502,503,504) or isinstance(error,urllib.error.URLError) and isinstance(error.reason,ssl.SSLCertVerificationError):raise
     time.sleep(attempt+1)
  paths.append(check_file(target,name))
 return paths
def install():
 with tempfile.TemporaryDirectory(prefix='deck-ai-codex-') as directory:
  path=Path(directory)/'install.sh';download(path)
  real_curl=shutil.which('curl')
  if not real_curl:raise RuntimeError('SteamOS curl is required to install Codex.')
  adapter=Path(directory)/'curl'
  adapter.write_text('#!/bin/sh\nexec '+shlex.join([sys.executable,str(Path(__file__).resolve()),'--curl',real_curl])+' "$@"\n');adapter.chmod(0o700)
  # Execute the original verified script unchanged. It still selects musl,
  # checks its SHA manifest, owns extraction, locks, symlinks and PATH setup.
  subprocess.run(['sh',str(path),'--release',VERSION],check=True,env={**os.environ,'PATH':directory+os.pathsep+os.environ.get('PATH',''),'CODEX_NON_INTERACTIVE':'1','CODEX_INSTALLER_USE_RELEASES_OPENAI_COM':'false'})
if __name__=='__main__':
 try:
  if sys.argv[1:2]==['--curl']:sys.exit(curl_proxy(sys.argv[3:],sys.argv[2]))
  install()
 except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError) as exc:sys.exit('Codex setup stopped: '+str(exc))

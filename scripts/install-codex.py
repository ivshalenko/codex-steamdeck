#!/usr/bin/env python3
"""Run a checksum-pinned official OpenAI installer from its official GitHub source."""
import hashlib,json,os,re,shlex,shutil,ssl,subprocess,sys,tempfile,urllib.error,urllib.parse,urllib.request
from pathlib import Path
VERSION='0.166.0'
URL='https://raw.githubusercontent.com/openai/codex/rust-v'+VERSION+'/scripts/install/install.sh'
SHA256='44ac252c1b9a68c02bdf0de8e1c6cbfde36fc1afa8684624962eae7d4c461e70'
API='https://api.github.com/repos/openai/codex'
PREFIX='https://github.com/openai/codex/releases/download/rust-v'+VERSION+'/'
ASSETS={'codex-package_SHA256SUMS','codex-package-x86_64-unknown-linux-musl.tar.gz','codex-package-aarch64-unknown-linux-musl.tar.gz'}
HEADERS={'User-Agent':'Deck-AI-Codex-Setup/1'}

def response(url,accept=None):
 headers={**HEADERS}
 if accept:headers['Accept']=accept
 result=urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30)
 if urllib.parse.urlsplit(result.geturl()).scheme!='https':
  result.close();raise ValueError('Codex download redirected outside HTTPS.')
 return result

def download_asset(url,destination):
 """Adapt only pinned official release downloads; leave installation to OpenAI."""
 name=url[len(PREFIX):] if url.startswith(PREFIX) else ''
 if name not in ASSETS:raise ValueError('Unexpected Codex release asset.')
 with response(API+'/releases/tags/rust-v'+VERSION,'application/vnd.github+json') as metadata:raw=metadata.read(2_000_001)
 if len(raw)>2_000_000:raise ValueError('Codex release metadata exceeds the limit.')
 release=json.loads(raw)
 if not isinstance(release,dict) or release.get('tag_name')!='rust-v'+VERSION or release.get('draft') or not release.get('published_at'):
  raise ValueError('The pinned Codex release is not published.')
 assets=[a for a in release.get('assets',[]) if isinstance(a,dict) and a.get('name')==name]
 if len(assets)!=1:raise ValueError('Codex release asset is missing or duplicated.')
 asset=assets[0];ident=asset.get('id');size=asset.get('size');digest=asset.get('digest','')
 limit=100_000 if name.endswith('SHA256SUMS') else 500_000_000
 if type(ident) is not int or ident<=0 or type(size) is not int or not 0<size<=limit or not isinstance(digest,str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',digest):
  raise ValueError('Invalid Codex release asset metadata.')
 endpoint=API+'/releases/assets/'+str(ident)
 if asset.get('url')!=endpoint or asset.get('browser_download_url')!=url or asset.get('state')!='uploaded':
  raise ValueError('Unexpected Codex release asset origin.')
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
 # Other requests (including release metadata) use the unmodified system curl.
 if len(arguments)==4 and arguments[0]=='-fsSL' and arguments[2]=='-o' and arguments[1].startswith(PREFIX):
  download_asset(arguments[1],arguments[3]);return 0
 return subprocess.call([real_curl,*arguments])

def download(path):
 with urllib.request.urlopen(URL,timeout=60) as response:data=response.read(2_000_001)
 if hashlib.sha256(data).hexdigest()!=SHA256:raise ValueError('Official Codex installer checksum mismatch; nothing was executed.')
 Path(path).write_bytes(data)
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

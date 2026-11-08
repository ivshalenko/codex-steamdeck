"""Supply corresponding LGPL sources beside the bundled upstream Codex binary."""
import concurrent.futures,hashlib,json,os,tempfile,time,urllib.error,urllib.request,zipfile
from pathlib import Path
SOURCES=[
 ('codex-build-source','https://codeload.github.com/openai/codex/tar.gz/6ff1e1ca3b30fc8b914720681fcf5fe62e95f856','1e33229b8b63237f666d62ba1476134383400d66032cdfde10b7f79debd15d28'),
 ('glib','https://download.gnome.org/sources/glib/2.88/glib-2.88.3.tar.xz','ab24d24e698dfa1e408b7bcdb508f4aafc906185a8b8ce72fdf79bbbdc9b383b'),
 ('proxy-libintl','https://codeload.github.com/frida/proxy-libintl/tar.gz/refs/tags/0.5','f7a1cbd7579baaf575c66f9d99fb6295e9b0684a28b095967cfda17857595303'),
 ('gstreamer','https://gstreamer.freedesktop.org/src/gstreamer/gstreamer-1.28.6.tar.xz','62b6b9f0ad3147a6dd6420ac64a91180b14e990695bddd353b96041611d052ca'),
 ('gst-plugins-base','https://gstreamer.freedesktop.org/src/gst-plugins-base/gst-plugins-base-1.28.6.tar.xz','0ba699c7c6c66f4ba640be78cb38a24715add9683f3e3a199f5369dc5a4f04ac'),
 ('gst-plugins-good','https://gstreamer.freedesktop.org/src/gst-plugins-good/gst-plugins-good-1.28.6.tar.xz','b0c620a4b18b6ee931b4c43bbf1760d308666dc37f730a7e7f1ad327e59ce2df'),
]
def fetch(entry,cache):
 name,url,digest=entry;path=Path(cache)/(name+'.archive')
 if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==digest:return path
 for attempt in range(3):
  temporary=None
  try:
   fd,temporary=tempfile.mkstemp(prefix='.'+name+'-',dir=cache)
   with os.fdopen(fd,'wb') as output,urllib.request.urlopen(url,timeout=60) as response:
    size=0;checksum=hashlib.sha256()
    while block:=response.read(1024*1024):
     size+=len(block)
     if size>100_000_000:raise ValueError('Source archive exceeds its limit: '+name)
     checksum.update(block);output.write(block)
   if checksum.hexdigest()!=digest:raise ValueError('Corresponding source checksum mismatch: '+name)
   os.replace(temporary,path);return path
  except (urllib.error.URLError,TimeoutError,ConnectionError):
   if attempt==2:raise
   time.sleep(attempt+1)
  finally:
   if temporary and os.path.exists(temporary):os.unlink(temporary)

def append_sources(artifact,cache):
 cache=Path(cache);cache.mkdir(parents=True,exist_ok=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:paths=list(pool.map(lambda item:fetch(item,cache),SOURCES))
 with zipfile.ZipFile(artifact,'a',zipfile.ZIP_STORED) as archive:
  def put(name,data):
   info=zipfile.ZipInfo('third-party/bundled-codex/'+name,(2020,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16;archive.writestr(info,data)
  manifest=[]
  for entry,path in zip(SOURCES,paths):
   name,url,digest=entry;put('sources/'+path.name,path.read_bytes());manifest.append({'name':name,'url':url,'sha256':digest})
  put('SOURCE-MANIFEST.json',(json.dumps(manifest,indent=2)+'\n').encode())
  put('REBUILD.txt',b'''Corresponding sources for unmodified OpenAI Codex 0.166.0 Linux x64.

The installer ZIP retains OpenAI's LICENSE and NOTICE. The official binary
also carries the native voice notices and license texts under
codex-resources/voice/. Its sources.json records native component versions.

Extract sources/codex-build-source.archive with tar xf. It is the complete
Codex source at commit 6ff1e1ca3b30fc8b914720681fcf5fe62e95f856,
including the vendored Bubblewrap source, local modifications, configuration
and build files under codex-rs/vendor/bubblewrap and codex-rs/bwrap.

The same source archive includes native voice build and packaging scripts
under third_party/voice. Extract the remaining original source archives
with tar xf, or use their exact URLs and hashes in SOURCE-MANIFEST.json.
GVDB is included by the GLib source. The voice build scripts describe build
tools and non-LGPL dependencies; their exact inputs are in sources.json.

Native libraries are separate dynamic files and can be replaced with
compatible modified builds. No signature lock is added by Deck AI.
Do not replace these files while Codex is running. Keep upstream notices.
''')

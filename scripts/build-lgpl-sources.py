#!/usr/bin/env python3
"""Supply the exact LGPL library and the work using it beside release binaries."""
import hashlib, json, tarfile, zipfile
from pathlib import Path

COMMIT='d1b7f16070777a0ada939cbacd3606eeba0574f5'
SOURCE='loader-api-1.1.3-source.tar.gz'
SHA256='24f639b73f259c28dee116681011f3e47ff425af799cfa91dfe6f75e56b89a8e'

def build(root,output,version,source_files):
 root=Path(root);upstream=root/'decky/vendor'/SOURCE
 if hashlib.sha256(upstream.read_bytes()).hexdigest()!=SHA256:raise ValueError('LGPL upstream source checksum mismatch')
 package=root/'decky/node_modules/@decky/api'
 if json.loads((package/'package.json').read_text())['version']!='1.1.3':raise ValueError('Review LGPL source bundle for new API version')
 library={}
 with tarfile.open(upstream) as archive:
  for path in sorted((package/'src').rglob('*')):
   if not path.is_file():continue
   rel=path.relative_to(package)
   if archive.extractfile('loader-api-'+COMMIT+'/'+str(rel)).read()!=path.read_bytes():raise ValueError('Used library source differs from pinned upstream')
   library[str(rel)]=hashlib.sha256(path.read_bytes()).hexdigest()
 artifact=Path(output)/f'deck-ai-{version}-lgpl-sources.zip'
 manifest={'library':'@decky/api','version':'1.1.3','upstreamCommit':COMMIT,'upstreamArchiveSha256':SHA256,'usedSourceSha256':library,'workUsingLibraryVersion':version}
 instructions=f'''LGPL corresponding sources for Deck AI {version}

The deck-ai-{version}/ folder contains the application source and build files.
third-party/{SOURCE} is the complete unmodified upstream source at {COMMIT}.
third-party/used-npm-package/ contains the exact installed library, source and
compiled modules used by the application build. Its LICENSE is LGPL-2.1.
The application's own source retains Apache-2.0; third-party terms stay intact.

Rebuild the application (Node 24 and Python 3.9+):
  cd deck-ai-{version}
  npm --prefix decky ci --ignore-scripts
  npm --prefix decky test
  python3 scripts/package-plugin.py --output Deck-AI-modified.zip

To modify the library using the application's locked build toolchain (Unix):
  mkdir -p decky/library-source
  tar -xzf decky/vendor/{SOURCE} -C decky/library-source --strip-components=1
  # Edit decky/library-source/src/ as desired, then compile it:
  node decky/node_modules/typescript/bin/tsc -b decky/library-source
  cp -R decky/library-source/dist/. decky/node_modules/@decky/api/dist/
  npm --prefix decky test
  python3 scripts/package-plugin.py --output Deck-AI-modified.zip

The application is rebuilt against your modified library; no signature lock is used.
Keep the library's interface compatible or adapt the supplied application source.
Do not run npm ci again after replacing the library; it restores the lockfile copy.

Build dependencies and their exact versions are described by the supplied
package.json, package-lock.json and the upstream project's own build files.
Source URL: https://github.com/SteamDeckHomebrew/loader-api/tree/{COMMIT}
'''
 with zipfile.ZipFile(artifact,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
  def put(name,data):
   info=zipfile.ZipInfo(str(name),(2020,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;archive.writestr(info,data)
  for rel in source_files:put(Path('deck-ai-'+version)/rel,(root/rel).read_bytes())
  put(Path('third-party')/SOURCE,upstream.read_bytes())
  for path in sorted(package.rglob('*')):
   if path.is_file() and not path.is_symlink():put(Path('third-party/used-npm-package')/path.relative_to(package),path.read_bytes())
  put('REBUILD.txt',instructions.encode());put('SOURCE-MANIFEST.json',(json.dumps(manifest,indent=2)+'\n').encode())
 return artifact

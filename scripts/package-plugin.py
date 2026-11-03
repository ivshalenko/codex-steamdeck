#!/usr/bin/env python3
"""One explicit file map for ZIP releases and local Decky installation."""
import hashlib
from pathlib import Path
RUNTIME=('backend.py','chat_media.py','providers.py','speech_accuracy.py','deck_share.py','speech-languages.json')
REPAIR_FILES=('launch_repair.py','repair_remote.py','repair-web/index.html','repair-web/app.js','repair-web/style.css')
WHEEL='websockets-15.0.1-py3-none-any.whl'
WHEEL_SHA='f7a866fbc1e97b5c617ee4116daaa09b722101d4a3c170c787450ba409f9736f'
def files(root):
 root=Path(root);plugin=root/'decky'
 wheel=plugin/'vendor'/WHEEL
 if hashlib.sha256(wheel.read_bytes()).hexdigest()!=WHEEL_SHA:raise ValueError('WebSocket dependency checksum mismatch')
 result={Path(name):plugin/name for name in ('plugin.json','package.json','main.py','bridge.py','runtime_paths.py','deck-ai.png','LICENSE','NOTICE','THIRD_PARTY_NOTICES.txt')}
 result.update({Path(name):plugin/name for name in REPAIR_FILES})
 result.update({Path('runtime')/name:root/name for name in RUNTIME})
 result.update({Path('vendor')/name:plugin/'vendor'/name for name in (WHEEL,'LICENSE-websockets.txt')})
 result.update({p.relative_to(plugin):p for p in (plugin/'dist').rglob('*') if p.is_file() and p.suffix!='.map'})
 if Path('dist/index.js') not in result:raise ValueError('Download the built release archive; this source tree has no Decky build.')
 for rel,source in result.items():
  if not source.is_file() or source.is_symlink():raise ValueError('Missing/unsafe plugin source: '+str(rel))
 return dict(sorted(result.items()))

if __name__=='__main__':
 import argparse,zipfile
 parser=argparse.ArgumentParser(description='Package built plugin files, including a locally modified library build.')
 parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 source=files(Path(__file__).resolve().parents[1]);args.output.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED) as archive:
  for rel,path in source.items():
   info=zipfile.ZipInfo(str(Path('Deck AI')/rel),(2020,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;archive.writestr(info,path.read_bytes())
 print(args.output)

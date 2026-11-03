#!/usr/bin/env python3
"""Source embedded verbatim in the downloadable desktop launcher by build-release.py."""
import hashlib,os,subprocess,sys,tarfile,tempfile,urllib.request
from pathlib import Path
VERSION='@VERSION@'
BASE='https://github.com/ivshalenko/codex-steamdeck/releases/download/v'+VERSION+'/'
def download(name,destination,limit):
 print('Downloading '+name,flush=True)
 with urllib.request.urlopen(BASE+name,timeout=90) as response,Path(destination).open('wb') as out:
  size=0
  while True:
   block=response.read(1024*1024)
   if not block:break
   size+=len(block)
   if size>limit:raise ValueError('Unexpected download size')
   out.write(block)
def unpack(archive,destination):
 with tarfile.open(archive) as tar:
  members=tar.getmembers()
  if sum(m.size for m in members)>200_000_000:raise ValueError('Unexpected extracted size')
  for member in members:
   path=Path(member.name)
   if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!='deck-ai-'+VERSION or not (member.isfile() or member.isdir()):raise ValueError('Unsafe release archive')
  options={'filter':'data'} if sys.version_info>=(3,12) else {}
  tar.extractall(destination,members=members,**options)
def prepare(root):
 root=Path(root);name='deck-ai-'+VERSION+'-steamdeck.tar.gz';archive=root/name
 download('SHA256SUMS.txt',root/'SHA256SUMS.txt',100_000);download(name,archive,100_000_000)
 sums={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (root/'SHA256SUMS.txt').read_text().splitlines()}
 if hashlib.sha256(archive.read_bytes()).hexdigest()!=sums.get(name):raise ValueError('Release checksum mismatch. Please download again.')
 unpack(archive,root);return root/('deck-ai-'+VERSION)
if __name__=='__main__':
 try:
  if sys.platform!='linux':raise ValueError('Run this installer on Steam Deck in Desktop Mode. For Mac/PC download Remote Control instead.')
  with tempfile.TemporaryDirectory(prefix='deck-ai-setup-') as directory:
   source=prepare(directory)
   subprocess.run([sys.executable,str(source/'scripts/setup.py')],cwd=source,check=True)
 except Exception as exc:
  print('\nSetup stopped: '+str(exc)+'\nHelp: https://github.com/ivshalenko/codex-steamdeck/blob/main/docs/QUICKSTART.md',flush=True)
  if sys.stdin.isatty():input('Press Enter to close / Enter для закрытия: ')
  sys.exit(1)

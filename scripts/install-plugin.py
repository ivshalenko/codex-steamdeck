#!/usr/bin/env python3
"""Stage a complete plugin and retain the previous version for rollback."""
import argparse,importlib.util,json,os,shutil,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('plugin_package',ROOT/'scripts/package-plugin.py');package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
def install(root,destination):
 destination=Path(destination).absolute()
 if destination.name not in ('Codex','Deck AI') or destination.parent.name!='plugins' or destination.is_symlink() or destination.parent.is_symlink():raise ValueError('Choose the Codex or Deck AI folder inside Decky homebrew/plugins.')
 if destination.exists():
  try:name=json.loads((destination/'plugin.json').read_text()).get('name')
  except (OSError,ValueError):raise ValueError('Existing folder is not a recognized Deck AI plugin; it was preserved.')
  if name not in ('Deck AI','Codex'):raise ValueError('Another plugin occupies this folder; it was preserved.')
 sources=package.files(root);destination.parent.mkdir(parents=True,exist_ok=True)
 backup=destination.with_name('.'+destination.name+'-backup-'+str(time.time_ns()))
 staging=Path(tempfile.mkdtemp(prefix='.deck-ai-staging-',dir=destination.parent))
 try:
  for rel,source in sources.items():
   target=staging/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);target.chmod(0o644)
  staging.chmod(0o755)
  for directory in staging.rglob('*'):
   if directory.is_dir():directory.chmod(0o755)
  if destination.exists():os.replace(destination,backup)
  try:os.replace(staging,destination)
  except Exception:
   if backup.exists():os.replace(backup,destination)
   raise
 finally:
  if staging.exists():shutil.rmtree(staging)
 return str(backup) if backup.exists() else None
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('destination',type=Path);a=p.parse_args()
 try:
  backup=install(ROOT,a.destination);print('Deck AI installed. Previous version: '+(backup or 'fresh installation'))
 except (OSError,ValueError) as e:p.exit(1,str(e)+'\n')

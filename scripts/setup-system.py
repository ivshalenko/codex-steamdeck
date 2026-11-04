#!/usr/bin/env python3
"""Selected administrative steps in a visible terminal with an explicit receipt."""
import argparse,json,subprocess,sys
from pathlib import Path
from setup_support import atomic_text,decky_installed
ROOT=Path(__file__).resolve().parents[1]
def run_steps(decky=False,loader=False,ssh=False):
 if decky:
  if not decky_installed():
   if not loader:raise RuntimeError('Decky Loader is missing; enable its installation in Custom setup.')
   subprocess.run([sys.executable,str(ROOT/'scripts/install-loader.py')],check=True)
  subprocess.run(['bash',str(ROOT/'scripts/install-decky.sh')],check=True)
  subprocess.run(['sudo','systemctl','enable','--now','plugin_loader'],check=True)
  subprocess.run(['systemctl','is-active','--quiet','plugin_loader'],check=True)
 if ssh:
  subprocess.run(['sudo','systemctl','enable','--now','sshd'],check=True)
  subprocess.run(['systemctl','is-active','--quiet','sshd'],check=True)
 return {'ok':True,'decky':decky,'ssh':ssh}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--receipt',required=True,type=Path);parser.add_argument('--language',choices=('en','ru'),default='en')
 for name in ('decky','allow-loader','ssh'):parser.add_argument('--'+name,action='store_true')
 args=parser.parse_args();result={'ok':False,'error':'Administrator setup did not complete.'}
 try:
  print('SteamOS may request your administrator password. Input is hidden.\nIf no password exists, run passwd in Konsole first.\n' if args.language=='en' else 'SteamOS может запросить пароль администратора. Символы не отображаются.\nЕсли пароль не задан, сначала выполните passwd в Konsole.\n',flush=True)
  result=run_steps(args.decky,args.allow_loader,args.ssh)
 except Exception as exc:
  result={'ok':False,'error':str(exc)};print(str(exc),file=sys.stderr,flush=True)
 finally:atomic_text(args.receipt,json.dumps(result)+'\n')
 if not result['ok'] and sys.stdin.isatty():input('Press Enter to return to setup / Enter — вернуться к установке: ')
 return 0 if result['ok'] else 1
if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env python3
"""Guided, key-only OpenSSH pairing from macOS / Windows / Linux to Deck."""
import argparse,ipaddress,os,re,shlex,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def valid_address(value):
 if re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]{0,252}',value):return True
 try:ipaddress.ip_address(value);return True
 except ValueError:return False
def configure(address,home=None):
 if not valid_address(address):raise ValueError('Enter only the Deck IP address or hostname, without ssh:// or a port.')
 home=Path(home) if home is not None else Path.home();ssh=home/'.ssh';ssh.mkdir(mode=0o700,exist_ok=True);key=ssh/'id_ed25519_deck_ai';config=ssh/'config'
 if config.is_symlink() or key.is_symlink():raise ValueError('SSH config/key symlinks require manual configuration.')
 if not key.exists():subprocess.run([shutil.which('ssh-keygen') or 'ssh-keygen','-t','ed25519','-N','','-C','Deck AI remote access','-f',str(key)],check=True)
 current=config.read_text() if config.exists() else ''
 match=re.search(r'^Host deck-ai\s*\n((?:[ \t]+[^\n]*\n?)*)',current,re.M)
 if match and ('HostName '+address) in match.group(1) and ('id_ed25519_deck_ai') in match.group(1):return key.with_suffix('.pub').read_text().strip()
 if re.search(r'^\s*Host\s+.*\bdeck-ai\b',current,re.M|re.I):raise ValueError('Alias deck-ai already exists for a different connection. Edit ~/.ssh/config to change the address. Existing configuration was preserved.')
 identity=str(key).replace('\\','/').replace('"','\\"')
 block=f'\n# Deck AI: remove this block to disconnect\nHost deck-ai\n    HostName {address}\n    User deck\n    IdentityFile "{identity}"\n    IdentitiesOnly yes\n'
 if config.exists():shutil.copy2(config,config.with_name('config.before-deck-ai'))
 with tempfile.NamedTemporaryFile(mode='w',dir=ssh,delete=False) as f:f.write(current+block);temporary=Path(f.name)
 temporary.chmod(0o600);os.replace(temporary,config)
 return key.with_suffix('.pub').read_text().strip()
def install_client():
 folder=Path.home()/'.local/share/deck-ai-remote';(folder/'scripts').mkdir(parents=True,exist_ok=True)
 for rel in ('backend.py','scripts/deck-remote.py'):shutil.copyfile(ROOT/rel,folder/rel)
 bin=Path.home()/'.local/bin';bin.mkdir(parents=True,exist_ok=True)
 if os.name=='nt':
  launcher=bin/'deck-remote.cmd';launcher.write_text('@echo off\n"'+sys.executable+'" "'+str(folder/'scripts/deck-remote.py')+'" deck-ai %*\n')
 else:
  launcher=bin/'deck-remote';launcher.write_text('#!/bin/sh\nexec '+shlex.quote(sys.executable)+' '+shlex.quote(str(folder/'scripts/deck-remote.py'))+' deck-ai "$@"\n');launcher.chmod(0o755)
 return launcher
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--host');args=parser.parse_args()
 try:
  if not shutil.which('ssh') or not shutil.which('ssh-keygen'):raise ValueError('Install the OpenSSH Client optional feature (Windows Settings), then retry.')
  print('On Steam Deck: Deck AI → Settings → Remote access. Enable SSH and read the address.\nKeep both devices awake on the same trusted network.\nНа Steam Deck: Настройки → Удалённый доступ. Включите SSH и посмотрите IP.')
  address=args.host or input('Steam Deck IP / hostname: ').strip();key=configure(address)
  print('\nPUBLIC KEY / ПУБЛИЧНЫЙ КЛЮЧ (private key stays on this computer):\n'+key+'\n\nPaste this public key into Deck AI → Remote access → Add key.\nВставьте ключ на Deck в поле публичного ключа и сохраните.')
  clipboard=shutil.which('pbcopy') or shutil.which('clip.exe') or shutil.which('wl-copy')
  if clipboard:subprocess.run([clipboard],input=key,text=True,check=False);print('Public key copied to clipboard / Ключ скопирован.')
  input('After saving the key on Deck, press Enter / После сохранения ключа нажмите Enter: ')
  print('Compare the server fingerprint below with the one shown on Deck. Accept only if they match.\nСверьте отпечаток SSH с экраном Steam Deck; подтвердите только при совпадении.')
  result=subprocess.run([shutil.which('ssh'),'-o','StrictHostKeyChecking=ask','-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no','deck-ai','printf DECK_AI_CONNECTED'])
  if result.returncode:raise ValueError('Connection failed. Check IP, SSH status and the saved public key. Do not disable host-key checking.')
  launcher=install_client();print('\nConnected / Подключено.\n'+str(launcher)+' new "Say hello from Steam Deck" --wait\n'+str(launcher)+' list\n'+str(launcher)+' read THREAD_ID')
 except (OSError,ValueError,subprocess.SubprocessError) as e:parser.exit(1,str(e)+'\n')

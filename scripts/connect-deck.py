#!/usr/bin/env python3
"""Guided, key-only OpenSSH pairing from macOS / Windows / Linux to Deck."""
import argparse,ipaddress,os,re,shlex,shutil,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def valid_address(value):
 if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9.:-]{1,253}',value):return False
 try:ipaddress.ip_address(value);return True
 except ValueError:pass
 if ':' in value or re.fullmatch(r'[0-9.]+',value):return False
 return all(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?',label) for label in value.rstrip('.').split('.'))

MARKER='# Deck AI: remove this block to disconnect'
END_MARKER='# End Deck AI connection'
def managed_block(current,key):
 aliases=[]
 for line in current.splitlines():
  try:parts=shlex.split(line,comments=True)
  except ValueError:continue
  if parts and parts[0].lower()=='host' and 'deck-ai' in [p.lower() for p in parts[1:]]:aliases.append(parts[1:])
 if not aliases:return None
 match=re.search(r'(?m)^'+re.escape(MARKER)+r'\r?\nHost deck-ai[ \t]*\r?\n((?:[ \t]+[^\n]*(?:\n|$))*)',current)
 if len(aliases)!=1 or aliases[0]!=['deck-ai'] or not match:raise ValueError('Alias deck-ai is custom or duplicated. Existing SSH configuration was preserved; edit it manually.')
 fields={}
 for line in match[1].splitlines():
  parts=shlex.split(line,comments=True)
  if not parts:continue
  if len(parts)!=2 or parts[0].lower() in fields:raise ValueError('Managed SSH block has custom changes; edit it manually.')
  fields[parts[0].lower()]=parts[1]
 identity=str(key).replace('\\','/')
 if set(fields)!= {'hostname','user','identityfile','identitiesonly'} or fields['user']!='deck' or fields['identityfile']!=identity or fields['identitiesonly'].lower()!='yes':raise ValueError('Managed SSH block has custom changes; existing configuration was preserved.')
 end=match.end()
 terminator=re.match(r'(?:Host \*\r?\n)?'+re.escape(END_MARKER)+r'(?:\r?\n|$)',current[end:])
 if terminator:end+=terminator.end()
 return match.start(),end,fields['hostname']

def atomic_text(path,text):
 with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,delete=False,encoding='utf-8') as f:f.write(text);temporary=Path(f.name)
 try:temporary.chmod(0o600);os.replace(temporary,path)
 finally:temporary.unlink(missing_ok=True)

def configure(address,home=None):
 if not valid_address(address):raise ValueError('Enter a valid Deck IP address or hostname, without ssh://, whitespace or a port.')
 home=Path(home) if home is not None else Path.home();ssh=home/'.ssh';key=ssh/'id_ed25519_deck_ai';config=ssh/'config';public=key.with_suffix('.pub')
 if any(p.is_symlink() for p in (ssh,config,key,public)):raise ValueError('SSH config/key symlinks require manual configuration.')
 ssh.mkdir(mode=0o700,exist_ok=True)
 current=config.read_text(encoding='utf-8') if config.exists() else '';managed=managed_block(current,key)
 if not key.exists():subprocess.run([shutil.which('ssh-keygen') or 'ssh-keygen','-t','ed25519','-N','','-C','Deck AI remote access','-f',str(key)],check=True)
 if not public.is_file():raise ValueError('Public key file is missing: '+str(public)+'. Restore its .pub file; the existing private key was preserved.')
 public_key=public.read_text(encoding='utf-8').strip()
 identity=str(key).replace('\\','/').replace('"','\\"')
 block=f'{MARKER}\nHost deck-ai\n    HostName {address}\n    User deck\n    IdentityFile "{identity}"\n    IdentitiesOnly yes\nHost *\n{END_MARKER}\n'
 if current.startswith(block):return public_key
 remainder=current if not managed else current[:managed[0]]+current[managed[1]:]
 # Specific options must precede a user's Host * defaults: OpenSSH uses the first value.
 updated=block+'\n'+remainder
 if config.exists():
  backup=config.with_name('config.before-deck-ai')
  if backup.exists():backup=config.with_name('config.before-deck-ai-'+str(time.time_ns()))
  shutil.copy2(config,backup)
 atomic_text(config,updated);return public_key
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
  if clipboard:
   copied=subprocess.run([clipboard],input=key,text=True,check=False)
   if copied.returncode==0:print('Public key copied to clipboard / Ключ скопирован.')
   else:print('Copy the public key above manually / Скопируйте ключ выше вручную.')
  input('After saving the key on Deck, press Enter / После сохранения ключа нажмите Enter: ')
  print('Compare the server fingerprint below with the one shown on Deck. Accept only if they match.\nСверьте отпечаток SSH с экраном Steam Deck; подтвердите только при совпадении.')
  result=subprocess.run([shutil.which('ssh'),'-o','StrictHostKeyChecking=ask','-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no','deck-ai','printf DECK_AI_CONNECTED'])
  if result.returncode:raise ValueError('Connection failed. Check IP, SSH status and the saved public key. Do not disable host-key checking.')
  launcher=install_client();print('\nConnected / Подключено.\n'+str(launcher)+' new "Say hello from Steam Deck" --wait\n'+str(launcher)+' list\n'+str(launcher)+' read THREAD_ID')
 except (OSError,ValueError,subprocess.SubprocessError) as e:parser.exit(1,str(e)+'\n')

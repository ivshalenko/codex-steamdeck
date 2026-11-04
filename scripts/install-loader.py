#!/usr/bin/env python3
"""Invoke the checksum-pinned official Decky installer only when selected."""
import hashlib,os,subprocess,tempfile,urllib.request
from pathlib import Path
from setup_support import decky_installed
COMMIT='2b903e6057e9081158a6573e0399912f06d6ba36'
URL='https://raw.githubusercontent.com/SteamDeckHomebrew/decky-installer/'+COMMIT+'/cli/install_release.sh'
SHA256='ed2de421b9713dd355ea5ede58f70c67e02127747cd59d00f49a145053d33ba7'
def install():
 if decky_installed():return
 with tempfile.TemporaryDirectory(prefix='deck-ai-decky-') as directory:
  with urllib.request.urlopen(URL,timeout=60) as response:data=response.read(2_000_001)
  if hashlib.sha256(data).hexdigest()!=SHA256:raise ValueError('Official Decky installer checksum mismatch; nothing was executed.')
  script=Path(directory)/'install.sh';script.write_bytes(data);script.chmod(0o700)
  # A real terminal owns the password prompt. No passwords are collected here.
  subprocess.run(['sudo','bash',str(script)],check=True)
 if not decky_installed():raise RuntimeError('Decky Loader did not create its executable. Retry the installation.')
 subprocess.run(['systemctl','is-active','--quiet','plugin_loader'],check=True)
if __name__=='__main__':install()

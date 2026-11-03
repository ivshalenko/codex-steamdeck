#!/usr/bin/env python3
"""Run a checksum-pinned official OpenAI installer from its official GitHub source."""
import hashlib,os,subprocess,tempfile,urllib.request
from pathlib import Path
VERSION='0.166.0'
URL='https://raw.githubusercontent.com/openai/codex/rust-v'+VERSION+'/scripts/install/install.sh'
SHA256='44ac252c1b9a68c02bdf0de8e1c6cbfde36fc1afa8684624962eae7d4c461e70'
def download(path):
 with urllib.request.urlopen(URL,timeout=60) as response:data=response.read(2_000_001)
 if hashlib.sha256(data).hexdigest()!=SHA256:raise ValueError('Official Codex installer checksum mismatch; nothing was executed.')
 Path(path).write_bytes(data)
def install():
 with tempfile.TemporaryDirectory(prefix='deck-ai-codex-') as directory:
  path=Path(directory)/'install.sh';download(path)
  # Official installer verifies the release asset digest and selects musl on SteamOS.
  subprocess.run(['sh',str(path),'--release',VERSION],check=True,env={**os.environ,'CODEX_NON_INTERACTIVE':'1','CODEX_INSTALLER_USE_RELEASES_OPENAI_COM':'false'})
if __name__=='__main__':install()

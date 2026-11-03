#!/usr/bin/env python3
"""Source embedded verbatim in the downloadable desktop launcher by build-release.py."""
import hashlib
import http.client
import ssl
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
VERSION='@VERSION@'
BASE='https://github.com/ivshalenko/codex-steamdeck/releases/download/v'+VERSION+'/'
def download(name, destination, limit):
    destination = Path(destination)
    temporary = destination.with_name(destination.name + ".part")
    for attempt in range(3):
        print("Downloading " + name, flush=True)
        try:
            with urllib.request.urlopen(BASE + name, timeout=25) as response, temporary.open("wb") as out:
                expected = response.headers.get("Content-Length")
                expected = int(expected) if expected and expected.isdecimal() else None
                if expected is not None and expected > limit:
                    raise ValueError("Unexpected download size")
                size = 0
                while block := response.read(256 * 1024):
                    size += len(block)
                    if size > limit:
                        raise ValueError("Unexpected download size")
                    out.write(block)
                if expected is not None and size != expected:
                    raise http.client.IncompleteRead(b"", expected - size)
            temporary.replace(destination)
            return
        except urllib.error.HTTPError as error:
            if attempt == 2 or error.code not in (408, 429, 500, 502, 503, 504):
                raise
        except urllib.error.URLError as error:
            if attempt == 2 or isinstance(error.reason, ssl.SSLCertVerificationError):
                raise
        except (TimeoutError, ConnectionError, http.client.IncompleteRead):
            if attempt == 2:
                raise
        finally:
            temporary.unlink(missing_ok=True)
        print("Download interrupted. Retrying… / Загрузка прервалась. Повторяю…", flush=True)
        time.sleep(attempt + 1)
def unpack(archive, destination):
    with tarfile.open(archive) as tar:
        members = []
        paths = set()
        total = 0
        for member in tar:
            path = Path(member.name)
            if (path.is_absolute() or ".." in path.parts or not path.parts
                    or path.parts[0] != "deck-ai-" + VERSION or path in paths
                    or not (member.isfile() or member.isdir())):
                raise ValueError("Unsafe release archive")
            total += member.size
            if total > 200_000_000 or len(members) >= 10000:
                raise ValueError("Unexpected extracted size")
            members.append(member)
            paths.add(path)
        options = {"filter": "data"} if sys.version_info >= (3, 12) else {}
        tar.extractall(destination, members=members, **options)
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

"""Let another computer (Mac, PC) reach this Steam Deck's Codex over SSH.

Nothing here needs root or changes system settings: it reports whether the SSH
server is running, lists addresses, and manages only the current user's
~/.ssh/authorized_keys. Enabling sshd itself stays a manual, one-time step.
"""
import getpass
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys

KEY_TYPES = ('ssh-ed25519', 'ssh-rsa', 'ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384', 'ecdsa-sha2-nistp521', 'sk-ssh-ed25519@openssh.com')
KEY_PATTERN = re.compile(r'^(' + '|'.join(re.escape(t) for t in KEY_TYPES) + r') [A-Za-z0-9+/=]{40,}( [^\n\r]{0,80})?$')
MARK = 'deck-ai-share'


def run(*command, timeout=5):
    try:
        result = subprocess.run(list(command), capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return 1, ''


def ssh_active():
    code, out = run('systemctl', 'is-active', 'sshd')
    return code == 0 and out == 'active'


def addresses():
    """LAN addresses plus the Tailscale one, which works away from home."""
    found = []
    _, out = run('ip', '-4', '-o', 'addr', 'show', 'scope', 'global')
    for line in out.splitlines():
        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/', line)
        if match:
            found.append(match.group(1))
    if shutil.which('tailscale'):
        _, out = run('tailscale', 'ip', '-4')
        found += [ip for ip in out.split() if re.fullmatch(r'\d+\.\d+\.\d+\.\d+', ip)]
    return list(dict.fromkeys(found))


def authorized_keys_path(home=None):
    return Path(home or Path.home())/'.ssh'/'authorized_keys'


def key_count(home=None):
    try:
        return sum(1 for line in authorized_keys_path(home).read_text().splitlines() if line.strip() and not line.startswith('#'))
    except OSError:
        return 0


def valid_key(text):
    """One OpenSSH public key line; options such as command= are rejected on purpose."""
    return bool(KEY_PATTERN.match(text.strip()))


def add_key(text, home=None):
    key = ' '.join(text.strip().split())
    if '\n' in text.strip() or not valid_key(key):
        raise ValueError('Нужна одна строка открытого ключа (начинается с ssh-ed25519 или ssh-rsa). Закрытый ключ вставлять нельзя.')
    path = authorized_keys_path(home)
    if path.is_symlink() or path.parent.is_symlink():raise ValueError('SSH paths are symbolic links. Configure access manually.')
    path.parent.mkdir(mode=0o700, exist_ok=True)
    os.chmod(path.parent, 0o700)
    existing = path.read_text() if path.exists() else ''
    blob = key.split(' ')[1]
    if any(blob in line.split(' ') for line in existing.splitlines()):
        return {'added': False, 'keys': key_count(home)}
    if len(key.split(' ')) == 2:
        key += ' ' + MARK  # label keys we added so they are easy to find and remove
    with path.open('a') as handle:
        handle.write(('' if not existing or existing.endswith('\n') else '\n') + key + '\n')
    os.chmod(path, 0o600)
    return {'added': True, 'keys': key_count(home)}


def ssh_snippet(address, user=None, alias='steamdeck'):
    return (f'Host {alias}\n    HostName {address}\n    User {user or getpass.getuser()}\n'
            '    IdentityFile ~/.ssh/id_ed25519\n    ServerAliveInterval 15\n'
            '    ControlMaster auto\n    ControlPath ~/.ssh/cm-%C\n    ControlPersist 10m\n')


def fingerprints():
    found=[]
    for key in sorted(Path("/etc/ssh").glob("ssh_host_*_key.pub")):
        code,value=run("ssh-keygen","-l","-E","sha256","-f",str(key))
        if code==0 and len(value.split())>=2:found.append(value.split()[1]+" "+key.stem)
    return found

def status(home=None):
    addrs = addresses()
    host = socket.gethostname()
    return {
        'sshActive': ssh_active(), 'user': getpass.getuser(), 'hostname': host, 'addresses': addrs,
        'fingerprints':fingerprints(),'keys': key_count(home), 'codex': bool(shutil.which('codex') or (Path.home()/'.local/bin/codex').exists()),
        'snippet': ssh_snippet(addrs[0] if addrs else host + '.local'),
        'enableHint': 'В режиме рабочего стола откройте терминал: passwd (задайте пароль), затем sudo systemctl enable --now sshd. После обновления SteamOS проверьте снова.',
    }


if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if command == 'status':
        info = status()
        print('SSH-сервер:', 'работает' if info['sshActive'] else 'выключен')
        print('Пользователь:', info['user'], '· адреса:', ', '.join(info['addresses']) or 'не найдены')
        print('Ключей в authorized_keys:', info['keys'], '· Codex:', 'найден' if info['codex'] else 'не найден')
        if not info['sshActive']:
            print(info['enableHint'])
        print('\nДобавьте на Mac в ~/.ssh/config:\n' + info['snippet'])
    elif command == 'add-key' and len(sys.argv) > 2:
        source = sys.argv[2]
        text = Path(source).read_text() if Path(source).is_file() else source
        try:
            print('Ключ добавлен.' if add_key(text)['added'] else 'Такой ключ уже есть.')
        except ValueError as exc:
            raise SystemExit(str(exc))
    else:
        raise SystemExit('Использование: python3 deck_share.py status | add-key <файл .pub или строка ключа>')

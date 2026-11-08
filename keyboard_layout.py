"""Opt-in physical EN/RU keyboard layout for the user's Gaming Mode session.

Gamescope owns the hardware keymap; setxkbmap alone cannot change it. Keep the
change in a user service drop-in, never in /etc or SteamOS's read-only image.
No key listener, key injection, account access or interface-language changes.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from contextlib import contextmanager

ENVIRONMENT = {'XKB_DEFAULT_LAYOUT': 'us,ru', 'XKB_DEFAULT_VARIANT': ',',
               'XKB_DEFAULT_OPTIONS': 'grp:alt_shift_toggle'}
MARKER = '# Managed by Deck AI: physical Gaming Mode keyboard\n'
CONTENT = MARKER + '[Service]\n' + ''.join('Environment="'+k+'='+v+'"\n' for k, v in ENVIRONMENT.items())
DROPIN = Path('.config/systemd/user/gamescope-session.service.d/90-deck-ai-keyboard.conf')
LOCK = threading.RLock()


@contextmanager
def configuration_lock(state):
    import fcntl  # configure() is available only on SteamOS/Linux.
    path = Path(state)/'hardware-keyboard.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def supported():
    return sys.platform.startswith('linux') and any(
        (Path(root)/'gamescope-session.service').is_file()
        for root in ('/usr/lib/systemd/user', '/etc/systemd/user'))


def running_environment():
    """Read only the three keyboard variables from our own compositor."""
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            if proc.stat().st_uid != os.getuid() or (proc/'comm').read_text().strip() not in ('gamescope', 'gamescope-wl'):
                continue
            if Path((proc/'cmdline').read_bytes().split(b'\0')[0].decode()).name != 'gamescope':
                continue
            try:
                parts = (proc/'environ').read_text().split('\0')
            except PermissionError:
                # SteamOS grants Gamescope capabilities, making /proc/environ
                # unreadable even by its owner. Its session launcher publishes
                # this user-owned startup environment before starting Steam.
                snapshot = Path('/run/user')/str(os.getuid())/'gamescope-environment'
                info = snapshot.stat()
                if info.st_uid != os.getuid() or info.st_mode & 0o022:
                    return None
                parts = snapshot.read_text().splitlines()
            values = dict(part.split('=', 1) for part in parts if '=' in part)
            return {key: values.get(key) for key in ENVIRONMENT}
        except (OSError, UnicodeError):
            continue
    return None


def read_state(state):
    try:
        value = json.loads((Path(state)/'hardware-keyboard.json').read_text())
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def target_path(home):
    home = Path(home).resolve()
    target = home/DROPIN
    if target.is_symlink() or not target.resolve().is_relative_to(home):
        raise ValueError('Keyboard configuration path is not a regular file inside your home directory.')
    return target


def status(home, state):
    target = target_path(home)
    original = read_state(state)
    content = target.read_text() if target.is_file() else None
    enabled = content == CONTENT
    conflict = content is not None and not enabled
    current = running_environment() if supported() else None
    desired = ENVIRONMENT if enabled else original.get('previousEnvironment')
    restart = bool(current is not None and desired is not None and
                   any(current.get(key) != desired.get(key) for key in ENVIRONMENT))
    return {'supported': supported(), 'enabled': enabled, 'conflict': conflict,
            'sessionActive': current is not None, 'restartRequired': restart,
            'shortcut': 'Alt+Shift', 'layouts': ['en', 'ru'] if enabled else [],
            'scope': 'gaming-mode', 'active': bool(enabled and current is not None and not restart)}


def atomic(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.'+path.name+'-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def configure(enabled, home, state):
    if type(enabled) is not bool:
        raise ValueError('Keyboard setting must be true or false.')
    if not supported():
        raise ValueError('Gaming Mode keyboard setup requires a SteamOS Gamescope session service.')
    with LOCK, configuration_lock(state):
        target = target_path(home)
        before = target.read_text() if target.is_file() else None
        if before is not None and before != CONTENT:
            raise ValueError('The keyboard configuration was edited separately; it was preserved.')
        previous = read_state(state)
        preference = dict(previous)
        if enabled and not previous.get('enabled'):
            current = running_environment()
            # Outside Gaming Mode, preserve the service's normal inherited values.
            if current == ENVIRONMENT and 'previousEnvironment' in previous:
                # Off -> on before the requested session restart must not save
                # our still-running preset as the user's original layout.
                preference['previousEnvironment'] = previous['previousEnvironment']
            else:
                preference['previousEnvironment'] = ({key: None for key in ENVIRONMENT} if before == CONTENT else
                                                     current or {key: os.environ.get(key) for key in ENVIRONMENT})
        preference['enabled'] = enabled
        try:
            if enabled:
                atomic(target, CONTENT)
            elif target.is_file():
                target.unlink()
            subprocess.run(['systemctl', '--user', 'daemon-reload'], stdin=subprocess.DEVNULL,
                           capture_output=True, check=True, timeout=15)
            atomic(Path(state)/'hardware-keyboard.json', json.dumps(preference, ensure_ascii=False)+'\n')
        except Exception:
            # A failed reload/write must not leave an unreported session change.
            if before is None:
                if target.is_file() and target.read_text() == CONTENT:
                    target.unlink()
            else:
                atomic(target, before)
            try:
                subprocess.run(['systemctl', '--user', 'daemon-reload'], stdin=subprocess.DEVNULL,
                               capture_output=True, timeout=15)
            except (OSError, subprocess.SubprocessError):
                pass
            raise
        return status(home, state)

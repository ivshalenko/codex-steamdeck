#!/usr/bin/env python3
"""Back up small state files atomically and retain the five latest archives."""
import os
import fcntl
import re
import sys
import tarfile
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'decky'))
from runtime_paths import resolve_state_dir

SKIP = {'backups', 'game-frames', 'chat-attachments'}
MAX_FILE = 2_000_000
KEEP = 5


def backup(state, stamp=None):
    state = Path(state)
    if not state.is_dir():
        return None
    label = stamp or time.strftime('%Y%m%d-%H%M%S')
    if not isinstance(label, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', label):
        raise ValueError('Invalid backup timestamp')
    folder = state/'backups'
    folder.mkdir(mode=0o700, exist_ok=True)
    if folder.is_symlink():
        raise ValueError('Backup directory must not be a symlink')
    lock_fd = os.open(folder/'.backup.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(lock_fd, 'r+b') as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        with tempfile.NamedTemporaryFile(prefix=f'.state-{label}-', suffix='.part', dir=folder, delete=False) as pending:
            temporary = Path(pending.name)
            archive = folder/(temporary.name[1:-5]+'.tar.gz')
            try:
                with tarfile.open(fileobj=pending, mode='w:gz') as tar:
                    for directory, folders, names in os.walk(state, followlinks=False):
                        if Path(directory) == state:
                            folders[:] = [name for name in folders if name not in SKIP]
                        for name in sorted(names):
                            path = Path(directory)/name
                            if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_FILE:
                                continue
                            tar.add(path, arcname=str(path.relative_to(state)), recursive=False)
                pending.flush()
                os.fsync(pending.fileno())
                # Publish the completed archive without replacing another backup.
                os.link(temporary, archive)
            finally:
                temporary.unlink(missing_ok=True)
        archives = sorted(folder.glob('state-*.tar.gz'), key=lambda path: path.stat().st_mtime_ns)
        for old in archives[:-KEEP]:
            old.unlink(missing_ok=True)
    return archive


if __name__ == '__main__':
    result = backup(sys.argv[1] if len(sys.argv) > 1 else resolve_state_dir())
    print(f'State backup: {result}' if result else 'No state to back up yet.')

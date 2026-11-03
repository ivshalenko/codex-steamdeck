#!/usr/bin/env python3
"""Back up chat/settings state (small files only) before an update. Keeps the last 5 archives."""
import sys, tarfile, time
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
    folder = state/'backups'
    folder.mkdir(mode=0o700, exist_ok=True)
    archive = folder/f"state-{stamp or time.strftime('%Y%m%d-%H%M%S')}.tar.gz"
    with tarfile.open(archive, 'w:gz') as tar:
        for path in sorted(state.rglob('*')):
            rel = path.relative_to(state)
            if rel.parts[0] in SKIP or not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_FILE:
                continue
            tar.add(path, arcname=str(rel))
    archive.chmod(0o600)
    for old in sorted(folder.glob('state-*.tar.gz'))[:-KEEP]:
        old.unlink()
    return archive

if __name__ == '__main__':
    result = backup(sys.argv[1] if len(sys.argv) > 1 else resolve_state_dir())
    print(f'State backup: {result}' if result else 'No state to back up yet.')

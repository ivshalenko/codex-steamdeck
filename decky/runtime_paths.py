"""Shared installation and data discovery for desktop, launchers and Decky."""
from pathlib import Path
import argparse,shlex


def resolve_app_dir(home=None):
    home=Path(home) if home is not None else Path.home()
    candidates=[home/'.local/share/deck-ai',home/'.local/share/deck-voice',home/'.local/share/codex-steamdeck']
    installed=next((path for path in candidates if (path/'app.py').is_file()),None)
    return installed or next((path for path in candidates if (path/'models').is_dir() or (path/'venv').is_dir()),candidates[0])


def resolve_state_dir(home=None):
    home=Path(home) if home is not None else Path.home()
    candidates=[home/'.local/state/deck-ai',home/'.local/state/deck-voice',home/'.local/state/codex-steamdeck']
    return next((path for path in candidates if path.is_dir()),candidates[0])

def desktop_shortcut(home=None):
    """Resolve the user's actual XDG desktop without evaluating shell input."""
    home=Path(home) if home is not None else Path.home()
    directory=home/'Desktop';config=home/'.config/user-dirs.dirs'
    try:
        if config.stat().st_size>64_000:return None
        for line in config.read_text().splitlines():
            if not line.strip().startswith('XDG_DESKTOP_DIR='):continue
            fields=shlex.split(line,comments=True)
            if len(fields)!=1:return None
            value=fields[0].split('=',1)[1].replace('${HOME}',str(home)).replace('$HOME',str(home))
            if '$' in value or '`' in value or not Path(value).is_absolute():return None
            directory=Path(value);break
    except FileNotFoundError:pass
    except (OSError,ValueError):return None
    resolved=directory.resolve();base=home.resolve()
    if resolved==base or not resolved.is_relative_to(base) or resolved.exists() and not resolved.is_dir():return None
    # Retain the caller's home spelling (macOS may alias /var to /private/var).
    return home/resolved.relative_to(base)/'Deck AI.desktop'

def desktop_external_paths(home=None):
    home=Path(home) if home is not None else Path.home()
    current=desktop_shortcut(home);paths={current} if current else set()
    for name in ('Desktop','Рабочий стол'):
        path=home/name/'Deck AI.desktop'
        if path.resolve().is_relative_to(home.resolve()):paths.add(path)
    return {path for path in paths if not path.is_symlink() and (not path.exists() or path.is_file())}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('kind',choices=['app','state'])
    args=parser.parse_args()
    print(resolve_app_dir() if args.kind=='app' else resolve_state_dir())

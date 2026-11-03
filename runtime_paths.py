"""Shared installation and data discovery for desktop, launchers and Decky."""
from pathlib import Path
import argparse


def resolve_app_dir(home=None):
    home=Path(home) if home is not None else Path.home()
    candidates=[home/'.local/share/deck-ai',home/'.local/share/deck-voice',home/'.local/share/codex-steamdeck']
    installed=next((path for path in candidates if (path/'app.py').is_file()),None)
    return installed or next((path for path in candidates if (path/'models').is_dir() or (path/'venv').is_dir()),candidates[0])


def resolve_state_dir(home=None):
    home=Path(home) if home is not None else Path.home()
    candidates=[home/'.local/state/deck-ai',home/'.local/state/deck-voice',home/'.local/state/codex-steamdeck']
    return next((path for path in candidates if path.is_dir()),candidates[0])


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('kind',choices=['app','state'])
    args=parser.parse_args()
    print(resolve_app_dir() if args.kind=='app' else resolve_state_dir())

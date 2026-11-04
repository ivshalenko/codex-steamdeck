#!/usr/bin/env python3
"""Install only the explicitly selected local dictation language pack."""
import argparse,sys,threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import language_support
from decky.runtime_paths import resolve_app_dir
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--language',choices=('en','ru'),required=True);args=parser.parse_args()
 print('Preparing local dictation pack: '+args.language,flush=True)
 language_support.prepare_recognition(resolve_app_dir(),args.language,threading.Event(),lambda _:None)
 print('Local dictation pack is ready.',flush=True)

#!/usr/bin/env python3
"""Read-only preflight. Never prints keys, account details or SSH hosts."""
import importlib.util,json,shutil,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'decky'))
from runtime_paths import resolve_app_dir,resolve_state_dir

def check():
    app=resolve_app_dir();items={}
    for program in ('ffmpeg','pactl','codex','claude','secret-tool'):items[program]=bool(shutil.which(program))
    for module in ('gi','websockets','vosk','faster_whisper'):items[module]=importlib.util.find_spec(module) is not None
    try:
        probe=subprocess.run(['pactl','get-default-source'],capture_output=True,text=True,timeout=4)
        source=probe.stdout.strip();items['microphone']=probe.returncode==0 and bool(source) and not source.endswith('.monitor')
    except (OSError,subprocess.TimeoutExpired):items['microphone']=False
    for name,folder in [('speechEnglish','vosk-model-small-en-us-0.15'),('speechRussian','vosk-model-small-ru-0.22'),('speechMultilingual','faster-whisper-small')]:items[name]=(app/'models'/folder).is_dir()
    return {'appDirectory':str(app),'dataDirectory':str(resolve_state_dir()),'checks':items,'notes':['Claude and API providers are optional. Account sign-in and provider requests require a separate interactive check.','This check does not read credentials or send microphone audio.']}

if __name__=='__main__':print(json.dumps(check(),ensure_ascii=False,indent=2))

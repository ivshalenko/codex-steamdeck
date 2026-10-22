#!/usr/bin/env python3
"""Opt-in real Vosk -> Decky queue -> Codex check using synthetic Russian audio.

Requires espeak-ng, ffmpeg, downloaded RU model and a signed-in Codex account.
Uses isolated app state, makes one real model request, archives its test chat,
and never records the microphone. It does not measure human speech accuracy.
"""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import patch


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true',help='Make one real Codex request (uses account quota)')
    args=parser.parse_args()
    if not args.live:parser.error('Pass --live to enable the real model request')
    for program in ('espeak-ng','ffmpeg'):
        if not shutil.which(program):parser.error('Missing test dependency: '+program)
    source=Path(__file__).resolve().parents[1]/'decky/bridge.py'
    spec=importlib.util.spec_from_file_location('voice_send_check_bridge',source)
    bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
    events=[]
    def collect(message):
        events.append(message);bridge.event(message)
    with tempfile.TemporaryDirectory(prefix='deck-ai-voice-send-') as directory:
        root=Path(directory);bridge.STATE=root
        wav=root/'speech.wav';raw=root/'speech.pcm'
        subprocess.run(['espeak-ng','-v','ru','-s','135','-w',str(wav),'Проверка голосового ввода. Где находится выход?'],check=True)
        subprocess.run(['ffmpeg','-v','error','-i',str(wav),'-ar','16000','-ac','1','-f','s16le',str(raw)],check=True)
        class Recorder:
            def __init__(self,*args,**kwargs):
                self.stdout=io.BytesIO(raw.read_bytes());self.stderr=io.BytesIO();self.code=None
            def poll(self):return self.code
            def terminate(self):self.code=0
            def wait(self,**kwargs):return 0
        bridge.voice_stop=threading.Event();bridge.voice_state='recording'
        started=time.monotonic()
        with patch.object(bridge.subprocess,'check_output',return_value='synthetic-test-input'),patch.object(bridge.subprocess,'Popen',Recorder):
            bridge.voice_capture('ru-fast')
        if not bridge.voice_text or bridge.voice_error:raise RuntimeError('Synthetic speech recognition failed')
        print('PASS local synthetic Russian speech:',round(time.monotonic()-started,2),'seconds',flush=True)
        bridge.connected();bridge.bridge.event=collect
        try:
            text=bridge.voice_text+'\nЭто проверка приложения. Ответь ровно DECK_AI_VOICE_OK. Не выполняй команды и не изменяй файлы.'
            result=bridge.send_message(text,[],'','','default')
            if not result.get('queued'):raise RuntimeError('Test request was not accepted')
            print('PASS first request accepted in a new isolated chat',flush=True)
            deadline=time.monotonic()+90
            while bridge.outbox and time.monotonic()<deadline:
                if any(job.get('status')=='error' for job in bridge.outbox):raise RuntimeError('Test queue reported an error')
                time.sleep(.15)
            if bridge.outbox:raise TimeoutError('Test request did not complete within 90 seconds')
            if 'DECK_AI_VOICE_OK' not in json.dumps(events):raise RuntimeError('Expected model answer missing')
            print('PASS real Codex response received; queue drained',flush=True)
        finally:
            if bridge.thread_id:
                try:bridge.bridge.request('thread/archive',{'threadId':bridge.thread_id},timeout=15)
                except Exception:print('NOTE test chat could not be archived',file=sys.stderr)
            bridge.bridge.ws.close()
            bridge.jobs.shutdown(wait=True)


if __name__=='__main__':main()

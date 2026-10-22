"""Optional offline final-pass dictation. Worker exits to release game memory."""
import json
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import wave


try:
    SPEECH_LANGUAGES=json.loads((Path(__file__).parent/'speech-languages.json').read_text())
except (OSError,ValueError):
    SPEECH_LANGUAGES={'ru':'Русский','en':'English'}

def multilingual_ready(root):
    model=Path(root)/'models'/'faster-whisper-small'
    return all((model/name).is_file() for name in ('model.bin','tokenizer.json','config.json')) and importlib.util.find_spec('faster_whisper') is not None

def refine_dictation(pcm, language, fallback, root):
    if language.endswith('-fast') or not pcm:
        return fallback
    model = Path(root)/'models'/'faster-whisper-small'
    if not (model/'model.bin').is_file():
        return fallback
    try:
        with tempfile.TemporaryDirectory(prefix='deck-ai-speech-') as directory:
            recording = Path(directory)/'speech.wav'
            with wave.open(str(recording), 'wb') as audio:
                audio.setnchannels(1); audio.setsampwidth(2); audio.setframerate(16000)
                audio.writeframes(pcm)
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--transcribe', str(recording), str(model), language],
                capture_output=True, text=True, timeout=120,
                env={**os.environ, 'OMP_NUM_THREADS':'2', 'HF_HUB_OFFLINE':'1'})
            if result.returncode == 0:
                text = json.loads(result.stdout).get('text', '').strip()
                if text:
                    return text
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass
    return fallback


def main():
    os.nice(10)
    from faster_whisper import WhisperModel
    model = WhisperModel(sys.argv[3], device='cpu', compute_type='int8', cpu_threads=2, num_workers=1, local_files_only=True)
    import numpy as np
    with wave.open(sys.argv[2], 'rb') as recording:
        audio=np.frombuffer(recording.readframes(recording.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
    language=sys.argv[4] if len(sys.argv)>4 else 'ru'
    if language!='auto' and language not in SPEECH_LANGUAGES:raise ValueError('Unsupported speech language')
    segments, _ = model.transcribe(audio, language=None if language=='auto' else language, beam_size=3, best_of=1, vad_filter=True,
        condition_on_previous_text=False,
        initial_prompt='Steam Deck, Decky Loader, Deck AI, Codex, DeepSeek, Claude.')
    print(json.dumps({'text':' '.join(segment.text.strip() for segment in segments).strip()}, ensure_ascii=False))


if __name__ == '__main__':
    main()

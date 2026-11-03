"""Optional offline final-pass dictation. Worker exits to release game memory."""
import json
import importlib.util
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import wave


try:
    SPEECH_LANGUAGES=json.loads((Path(__file__).parent/'speech-languages.json').read_text())
except (OSError,ValueError):
    SPEECH_LANGUAGES={'ru':'Русский','en':'English'}

DEFAULT_PROMPT = 'Steam Deck, Decky Loader, Deck AI, Codex, DeepSeek, Claude.'
WHISPER_SIZES = ('tiny', 'base', 'small')

def whisper_dir(root):
    """Final-pass model folder. `models/whisper-size` may contain tiny, base or small."""
    size = 'small'
    try:
        value = (Path(root)/'models'/'whisper-size').read_text().strip().lower()
        if value in WHISPER_SIZES and (Path(root)/'models'/f'faster-whisper-{value}'/'model.bin').is_file():
            size = value
    except OSError:
        pass
    return Path(root)/'models'/f'faster-whisper-{size}'

def _vocabulary_lines():
    lines = []
    for path in (Path(__file__).parent/'vocabulary.txt', Path.home()/'.config/deck-ai/vocabulary.txt'):
        try:
            lines += [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.startswith('#')]
        except OSError:
            pass
    return lines

def apply_corrections(text):
    """Apply `heard => written` lines from vocabulary.txt to any recognizer's output (whole words, any case)."""
    import re
    for line in _vocabulary_lines():
        if '=>' not in line:
            continue
        heard, written = (part.strip() for part in line.split('=>', 1))
        if heard:
            text = re.sub(r'(?<!\w)' + re.escape(heard) + r'(?!\w)', lambda _m, w=written: w, text, flags=re.IGNORECASE)
    return text

def vocabulary_prompt():
    """Own words (project names, commands) steer Whisper; `heard => written` lines contribute the written form."""
    words = [line.split('=>', 1)[1].strip() if '=>' in line else line for line in _vocabulary_lines()]
    words = [word for word in words if word]
    return (DEFAULT_PROMPT + ' ' + ', '.join(dict.fromkeys(words)))[:600] if words else DEFAULT_PROMPT

def log_timing(root, entry):
    """Append one JSON line so the real speed of the final pass can be measured."""
    try:
        path = Path(root)/'models'/'speech-timing.jsonl'
        with path.open('a') as handle:
            handle.write(json.dumps(entry, ensure_ascii=False)+'\n')
    except OSError:
        pass


# Lightweight dictation formatting; no model load, network or word replacement.
# These deliberately conservative rules are not a grammatical language model.
_RU_CLAUSE = re.compile(r'(?<=[\w»)])\s+(?=(?:потому что|так как|хотя|но|зато|однако)\b)', re.I)
_RU_REPORTED = re.compile(
    r'\b(скажи|покажи|проверь|посмотри|объясни|узнай|уточни|расскажи|знаю|вижу|думаю|считаю|хочу|нужно|надо|важно|кажется|получается)\s+'
    r'(?=(?:что|чтобы|как|почему|зачем|где|когда|какой|какая|какие|сколько|можно ли|работает ли|есть ли)(?![-\w]))', re.I)
_EN_CLAUSE = re.compile(r'(?<=\w)\s+(?=(?:but|although|however)\b)', re.I)
_QUESTION = {
    'ru': re.compile(r'^(?:почему|зачем|когда|где|куда|откуда|сколько|какой|какая|какие|как|можно ли|нужно ли|есть ли|ты можешь|можешь ли)\b', re.I),
    'en': re.compile(r'^(?:how|why|when|where|who|what|can you|could you|is|are|do you|does|should)\b', re.I),
}
_SENTENCE_START = re.compile(r'(^|[.!?]\s+)([a-zа-яё])', re.I)


def fast_punctuation(text, language='ru'):
    """Format plain dictation quickly, preserving its words and existing marks."""
    text = re.sub(r'[ \t]+', ' ', text).strip()
    if not text:
        return ''
    if language == 'ru':
        text = _RU_CLAUSE.sub(', ', text)
        text = _RU_REPORTED.sub(r'\1, ', text)
    elif language == 'en':
        text = _EN_CLAUSE.sub(', ', text)
    text = _SENTENCE_START.sub(lambda match: match[1] + match[2].upper(), text)
    if text[-1] not in '.!?…:;':
        question = _QUESTION.get(language)
        text += '?' if question and question.match(text) else '.'
    return text

def multilingual_ready(root):
    model=whisper_dir(root)
    return all((model/name).is_file() for name in ('model.bin','tokenizer.json','config.json')) and importlib.util.find_spec('faster_whisper') is not None

WORKER_ENV = {'OMP_NUM_THREADS':'2', 'HF_HUB_OFFLINE':'1'}

def prewarm_worker(language, root):
    """Start loading the final-pass model while the user is still speaking.

    Loading the model is the slowest part of a short dictation on the Deck, so
    it overlaps with recording. Returns None when no final pass applies.
    """
    model = whisper_dir(root)
    if language.endswith('-fast') or not (model/'model.bin').is_file() or not multilingual_ready(root):
        return None
    try:
        return subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--serve', str(model), language],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            env={**os.environ, **WORKER_ENV})
    except OSError:
        return None

def cancel_worker(worker):
    """Release a prewarmed model that will not be used (cancelled or failed)."""
    if worker is None:
        return
    try:
        if worker.poll() is None:
            worker.stdin.close()
            worker.terminate()
        worker.wait(timeout=3)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        try:
            worker.kill()
        except OSError:
            pass

def refine_dictation(pcm, language, fallback, root, worker=None):
    started = time.monotonic()
    text = _refine(pcm, language, fallback, root, worker)
    if text != fallback:
        log_timing(root, {'language': language, 'audioSeconds': round(len(pcm)/32000, 1), 'refineSeconds': round(time.monotonic()-started, 2), 'prewarmed': worker is not None})
    return text

def _refine(pcm, language, fallback, root, worker=None):
    if language.endswith('-fast') or not pcm:
        cancel_worker(worker)
        return fallback
    model = whisper_dir(root)
    if not (model/'model.bin').is_file():
        cancel_worker(worker)
        return fallback
    try:
        with tempfile.TemporaryDirectory(prefix='deck-ai-speech-') as directory:
            recording = Path(directory)/'speech.wav'
            with wave.open(str(recording), 'wb') as audio:
                audio.setnchannels(1); audio.setsampwidth(2); audio.setframerate(16000)
                audio.writeframes(pcm)
            if worker is not None:
                try:
                    output, _ = worker.communicate(input=str(recording)+'\n', timeout=120)
                except (OSError, ValueError, subprocess.TimeoutExpired):
                    cancel_worker(worker)
                    return fallback
                if worker.returncode == 0:
                    text = json.loads(output).get('text', '').strip()
                    if text:
                        return text
                return fallback
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--transcribe', str(recording), str(model), language],
                capture_output=True, text=True, timeout=120, env={**os.environ, **WORKER_ENV})
            if result.returncode == 0:
                text = json.loads(result.stdout).get('text', '').strip()
                if text:
                    return text
    except (OSError, ValueError, subprocess.TimeoutExpired):
        cancel_worker(worker)
    return fallback


def load_model(path):
    from faster_whisper import WhisperModel
    return WhisperModel(path, device='cpu', compute_type='int8', cpu_threads=2, num_workers=1, local_files_only=True)

def transcribe(model, wav_path, language):
    import numpy as np
    with wave.open(wav_path, 'rb') as recording:
        audio=np.frombuffer(recording.readframes(recording.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
    if language!='auto' and language not in SPEECH_LANGUAGES:raise ValueError('Unsupported speech language')
    segments, _ = model.transcribe(audio, language=None if language=='auto' else language, beam_size=3, best_of=1, vad_filter=True,
        condition_on_previous_text=False, without_timestamps=True,
        initial_prompt=vocabulary_prompt())
    return ' '.join(segment.text.strip() for segment in segments).strip()

def main():
    os.nice(10)
    if sys.argv[1] == '--serve':
        # Prewarmed worker: load the model now, transcribe the one file sent on
        # stdin once recording ends. EOF means the dictation was cancelled.
        model = load_model(sys.argv[2])
        wav_path = sys.stdin.readline().strip()
        if not wav_path:
            return
        print(json.dumps({'text':transcribe(model, wav_path, sys.argv[3])}, ensure_ascii=False))
        return
    model = load_model(sys.argv[3])
    language=sys.argv[4] if len(sys.argv)>4 else 'ru'
    print(json.dumps({'text':transcribe(model, sys.argv[2], language)}, ensure_ascii=False))


if __name__ == '__main__':
    main()

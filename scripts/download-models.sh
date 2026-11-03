#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$(python3 "$ROOT/decky/runtime_paths.py" app)"
if [[ ! -f "$APP_DIR/app.py" ]]; then
  echo "Install Deck AI before downloading speech models." >&2
  exit 1
fi
MODEL_DIR="$APP_DIR/models"
mkdir -p "$MODEL_DIR"
command -v curl >/dev/null || { echo "curl is required" >&2; exit 1; }
command -v unzip >/dev/null || { echo "unzip is required" >&2; exit 1; }
fetch_model() {
  local name="$1" url="https://alphacephei.com/vosk/models/$1.zip"
  if [[ -d "$MODEL_DIR/$name" ]]; then
    echo "$name is already installed"
    return
  fi
  local archive="$MODEL_DIR/$name.zip"
  local temp="$MODEL_DIR/.extract-$name"
  echo "Downloading $name …"
  curl --fail --location --retry 3 --output "$archive" "$url"
  mkdir -p "$temp"
  unzip -q "$archive" -d "$temp"
  mv "$temp/$name" "$MODEL_DIR/$name"
  rm -rf "$temp" "$archive"
}
fetch_model vosk-model-small-en-us-0.15
fetch_model vosk-model-small-ru-0.22
if [[ "${1:-}" == "--accurate-ru" ]]; then
  "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements-speech.txt"
  # DECK_AI_WHISPER_SIZE=tiny|base trades accuracy for speed on the Deck.
  WHISPER_SIZE="${DECK_AI_WHISPER_SIZE:-small}"
  case "$WHISPER_SIZE" in tiny|base|small) ;; *) echo "DECK_AI_WHISPER_SIZE must be tiny, base or small" >&2; exit 2 ;; esac
  "$APP_DIR/venv/bin/python" - "$MODEL_DIR" "$WHISPER_SIZE" <<'PYMODEL'
from pathlib import Path
import sys
from faster_whisper.utils import download_model
size = sys.argv[2]
download_model(size, output_dir=str(Path(sys.argv[1])/f'faster-whisper-{size}'))
(Path(sys.argv[1])/'whisper-size').write_text(size+'\n')
PYMODEL
fi
echo "Speech models installed in $MODEL_DIR"

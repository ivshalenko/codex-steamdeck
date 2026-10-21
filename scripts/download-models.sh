#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="${HOME:?HOME is not set}/.local/share/codex-steamdeck"
if [[ -d "$APP_DIR" ]]; then
  MODEL_DIR="$APP_DIR/models"
else
  MODEL_DIR="$ROOT/models"
fi
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
echo "Speech models installed in $MODEL_DIR"

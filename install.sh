#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
command -v python3 >/dev/null || { echo "Python 3 is required" >&2; exit 1; }
if [[ "${1:-}" == "--check" ]]; then
  exec python3 "$SOURCE/scripts/check-environment.py"
fi
WITH_DECKY=0
if [[ "${1:-}" == "--decky" ]]; then WITH_DECKY=1; shift; fi
if [[ $# -gt 0 ]]; then echo "Usage: ./install.sh [--check | --decky]" >&2; exit 2; fi
python3 - <<'PY' || { echo "GTK 3 Python bindings are required (PyGObject)." >&2; exit 1; }
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
PY
APP_DIR="$(python3 "$SOURCE/decky/runtime_paths.py" app)"
# Validate packaged files before creating or changing an installation.
python3 "$SOURCE/scripts/manage-install.py" validate "$SOURCE"
if [[ ! -x "$APP_DIR/venv/bin/python" ]]; then
  python3 -m venv --system-site-packages "$APP_DIR/venv"
fi
"$APP_DIR/venv/bin/python" -m pip install websockets==15.0.1
python3 "$SOURCE/scripts/backup-state.py" || echo "State backup skipped." >&2
python3 "$SOURCE/scripts/manage-install.py" install "$SOURCE"
echo "Installed Deck AI in $APP_DIR"
echo "Optional voice: $APP_DIR/venv/bin/python -m pip install vosk==0.3.45; $SOURCE/scripts/download-models.sh"
if [[ "$WITH_DECKY" == 1 ]]; then "$SOURCE/scripts/install-decky.sh"; else echo "Gaming Mode plugin: $SOURCE/install.sh --decky (or $SOURCE/scripts/install-decky.sh)"; fi

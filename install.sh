#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
command -v python3 >/dev/null || { echo "Python 3 is required" >&2; exit 1; }
if [[ "${1:-}" == "--check" ]]; then
  exec python3 "$SOURCE/scripts/check-environment.py"
fi
if [[ $# -gt 0 ]]; then echo "Usage: ./install.sh [--check]" >&2; exit 2; fi
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
"$APP_DIR/venv/bin/python" -m pip install -r "$SOURCE/requirements.txt"
python3 "$SOURCE/scripts/manage-install.py" install "$SOURCE"
echo "Installed Deck AI in $APP_DIR"
echo "Offline voice: $SOURCE/scripts/download-models.sh"

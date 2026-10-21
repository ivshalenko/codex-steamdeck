#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="${HOME:?HOME is not set}"
APP_DIR="$HOME_DIR/.local/share/codex-steamdeck"
BIN_DIR="$HOME_DIR/.local/bin"
DESKTOP_DIR="$HOME_DIR/.local/share/applications"
ICON_DIR="$HOME_DIR/.local/share/icons/hicolor/256x256/apps"

command -v python3 >/dev/null || { echo "Python 3 is required" >&2; exit 1; }
python3 - <<'PY' || { echo "GTK 3 Python bindings are required (PyGObject). Install the SteamOS GTK/Python bindings and retry." >&2; exit 1; }
import gi
gi.require_version("Gtk", "3.0")
PY

mkdir -p "$APP_DIR" "$BIN_DIR" "$DESKTOP_DIR" "$ICON_DIR"
install -m 0644 "$SOURCE/app.py" "$SOURCE/backend.py" "$SOURCE/providers.py" "$SOURCE/ui_extras.py" "$SOURCE/style.css" "$SOURCE/themes.json" "$APP_DIR/"
install -m 0644 "$SOURCE/codex-transparent.png" "$ICON_DIR/codex-steamdeck.png"
cp -a "$SOURCE/decky" "$APP_DIR/"
rm -rf "$APP_DIR/decky/node_modules"
rm -f "$APP_DIR/decky"/dist/*.map

if [[ ! -x "$APP_DIR/venv/bin/python" ]]; then
  python3 -m venv --system-site-packages "$APP_DIR/venv"
fi
"$APP_DIR/venv/bin/python" -m pip install -r "$SOURCE/requirements.txt"

cat > "$BIN_DIR/codex-steamdeck" <<EOF
#!/usr/bin/env bash
exec "$APP_DIR/venv/bin/python" "$APP_DIR/app.py" "\$@"
EOF
chmod 0755 "$BIN_DIR/codex-steamdeck"
cat > "$DESKTOP_DIR/codex-steamdeck.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Codex
Comment=Codex companion for Steam Deck
Exec=$BIN_DIR/codex-steamdeck
Icon=codex-steamdeck
Terminal=false
Categories=Utility;Accessibility;
EOF
chmod 0644 "$DESKTOP_DIR/codex-steamdeck.desktop"
echo "Installed Codex for Steam Deck. Launch it from the application menu."
echo "For offline voice dictation, run: $SOURCE/scripts/download-models.sh"

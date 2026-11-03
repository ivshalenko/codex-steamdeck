#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${DECKY_PLUGIN_DIR:-$HOME/homebrew/plugins/Codex}"
[[ -d "$HOME/homebrew" || -n "${DECKY_PLUGIN_DIR:-}" ]] || { echo 'Install Decky Loader first: https://decky.xyz'; exit 1; }
# Validate all files before asking for administrator access.
python3 - "$ROOT" <<'PY'
import importlib.util,sys
from pathlib import Path
root=Path(sys.argv[1]);s=importlib.util.spec_from_file_location('package_plugin',root/'scripts/package-plugin.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.files(root)
PY
SUDO=""
if ! mkdir -p "$(dirname "$DEST")" 2>/dev/null || [[ ! -w "$(dirname "$DEST")" || ( -e "$DEST" && ! -w "$DEST" ) ]]; then
 SUDO="sudo";echo "Decky's plugin folder belongs to root. SteamOS will ask for your administrator password."
fi
$SUDO python3 "$ROOT/scripts/install-plugin.py" "$DEST"
if [[ -z "${DECK_AI_SKIP_RESTART:-}" ]] && command -v systemctl >/dev/null && systemctl is-active --quiet plugin_loader 2>/dev/null; then
 echo 'Restarting Decky Loader…';sudo systemctl restart plugin_loader
fi
echo 'Open Quick Access (…) → Decky → Deck AI. Sign in to ChatGPT in Settings.'

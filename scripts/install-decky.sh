#!/usr/bin/env bash
# Install the Deck AI plugin for Decky Loader (Steam Deck, Desktop Mode terminal).
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${DECKY_PLUGIN_DIR:-$HOME/homebrew/plugins/Codex}"
[[ -f "$ROOT/decky/dist/index.js" ]] || { echo "decky/dist is missing: run 'npm ci && npm test' in decky/ first." >&2; exit 1; }
SUDO=""
if ! mkdir -p "$(dirname "$DEST")" 2>/dev/null || [[ -e "$DEST" && ! -w "$DEST" ]] || [[ ! -w "$(dirname "$DEST")" ]]; then
  SUDO="sudo"; echo "Decky's plugin folder belongs to root; sudo will ask for your password."
fi
$SUDO rm -rf "$DEST"
$SUDO mkdir -p "$DEST"
for file in plugin.json main.py bridge.py runtime_paths.py package.json deck-ai.png LICENSE NOTICE THIRD_PARTY_NOTICES.txt; do
  [[ -f "$ROOT/decky/$file" ]] && $SUDO cp "$ROOT/decky/$file" "$DEST/$file"
done
$SUDO cp -R "$ROOT/decky/dist" "$DEST/dist"
echo "Deck AI plugin installed in $DEST"
if [[ -z "${DECK_AI_SKIP_RESTART:-}" ]] && command -v systemctl >/dev/null && systemctl is-active --quiet plugin_loader 2>/dev/null; then
  echo "Restarting Decky Loader…"
  sudo systemctl restart plugin_loader
fi
echo "Open Steam's Quick Access menu and choose Deck AI."

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON_EXECUTABLE="${DECK_AI_TEST_PYTHON:-python3}"
"$PYTHON_EXECUTABLE" -m py_compile app.py chat_media.py language_support.py language_settings.py message_blocks.py remote_access.py deck_share.py backend.py providers.py ui_extras.py speech_accuracy.py decky/bridge.py decky/main.py decky/runtime_paths.py decky/launch_repair.py decky/repair_remote.py
node --input-type=module --check < decky/repair-web/app.js
"$PYTHON_EXECUTABLE" -m compileall -q scripts tests
for script in install.sh uninstall.sh scripts/*.sh scripts/deck-ai-steam; do bash -n "$script"; done
npm --prefix decky test
node --test decky/tests/*.test.mjs
"$PYTHON_EXECUTABLE" -m unittest discover -s tests -v
"$PYTHON_EXECUTABLE" scripts/check-package.py

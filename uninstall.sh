#!/usr/bin/env bash
set -euo pipefail
SOURCE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SOURCE/scripts/manage-install.py" uninstall "$SOURCE"

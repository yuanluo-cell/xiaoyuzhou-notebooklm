#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[[ -f "$ROOT/.venv/bin/activate" ]] && source "$ROOT/.venv/bin/activate"
exec python3 "$ROOT/scripts/chat.py" "$@"

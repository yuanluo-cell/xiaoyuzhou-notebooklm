#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[[ -f "$ROOT/.venv/bin/activate" ]] && source "$ROOT/.venv/bin/activate"
[[ -f "$ROOT/config.yaml" ]] || cp "$ROOT/config.example.yaml" "$ROOT/config.yaml"
# 导入小宇宙用 venv python；NotebookLM 走 scripts/nlm 包装器
export NOTEBOOKLM_BIN="${NOTEBOOKLM_BIN:-$HOME/.local/bin/notebooklm}"
exec python3 "$ROOT/scripts/sync.py" "$@"

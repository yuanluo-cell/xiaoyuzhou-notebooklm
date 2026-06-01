#!/usr/bin/env bash
# 将 skill/ 安装到 ~/.cursor/skills/（全项目可用）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.cursor/skills/xiaoyuzhou-notebooklm"
mkdir -p "$DEST"
cp "$ROOT/skill/SKILL.md" "$DEST/SKILL.md"
echo "已安装 Skill → $DEST/SKILL.md"
echo "在 Cursor 中提及「小宇宙 NotebookLM」或打开本仓库即可触发。"

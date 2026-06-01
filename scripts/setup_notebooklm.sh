#!/usr/bin/env bash
# 一次性配置 NotebookLM 终端访问
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NLM="$ROOT/scripts/nlm"

echo "=== NotebookLM 终端配置 ==="
echo ""

if [[ ! -x "$NLM" ]] && ! command -v notebooklm >/dev/null; then
  echo "未找到 notebooklm。请先安装："
  echo "  uv tool install notebooklm-py"
  echo "  或: pipx install 'notebooklm-py[browser]'"
  exit 1
fi
NLM="$(command -v notebooklm 2>/dev/null || echo "$NLM")"

echo "使用: $NLM ($($NLM --version 2>/dev/null || echo unknown))"
echo ""
echo "【重要】请先开启 VPN，确保浏览器能打开 https://notebooklm.google.com"
echo ""
read -r -p "按回车开始登录（会弹出浏览器，只需做一次）…"

"$NLM" login

echo ""
echo "验证认证…"
if "$NLM" auth check --test 2>&1 | grep -q "Token fetch.*pass"; then
  echo "✓ 认证成功"
else
  echo "✗ 认证仍失败。请确认 VPN 后重试: notebooklm login"
  exit 1
fi

[[ -f "$ROOT/config.yaml" ]] || cp "$ROOT/config.example.yaml" "$ROOT/config.yaml"

echo ""
echo "下一步："
echo "  cd $ROOT"
echo "  source .venv/bin/activate   # 若有 venv"
echo "  ./scripts/sync.sh           # 导入播客并自动上传"
echo "  ./scripts/chat.sh           # 终端对话"

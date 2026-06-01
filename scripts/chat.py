#!/usr/bin/env python3
"""终端与 NotebookLM 笔记本对话（基于 notebooklm ask）。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_config, resolve_path
from nlm_cli import ask, auth_ok, find_cli, load_context

console = Console()


def main() -> int:
    parser = argparse.ArgumentParser(description="在终端与 NotebookLM 对话")
    parser.add_argument("question", nargs="?", help="单次提问（不填则进入交互模式）")
    parser.add_argument("--new", action="store_true", help="开启新对话线程")
    args = parser.parse_args()

    cfg = load_config()
    logs_dir = resolve_path("logs_dir", cfg)
    cli = find_cli(cfg)
    if not cli:
        console.print("[red]未找到 notebooklm 命令[/red]")
        console.print("安装: pip install 'notebooklm-py[browser]'  或 uv tool install notebooklm-py")
        return 1

    ok, msg = auth_ok(cli)
    if not ok:
        console.print(f"[red]{msg}[/red]")
        return 1

    ctx = load_context(logs_dir)
    if not ctx.get("notebook_id"):
        console.print("[yellow]还没有笔记本。请先运行: ./scripts/sync.sh[/yellow]")
        return 1

    if args.question:
        try:
            answer = ask(cli, args.question, new_conversation=args.new)
            console.print(Markdown(answer))
        except RuntimeError as e:
            console.print(f"[red]{e}[/red]")
            return 1
        return 0

    nb = ctx.get("notebook_title", ctx["notebook_id"])
    console.print(f"[bold]NotebookLM 对话[/bold] · 笔记本: {nb}")
    console.print("[dim]输入问题，空行退出。/new 开新对话[/dim]\n")

    new_conv = args.new
    while True:
        try:
            q = input("你> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n再见。")
            break
        if not q:
            break
        if q == "/new":
            new_conv = True
            console.print("[dim]已开启新对话[/dim]")
            continue
        try:
            answer = ask(cli, q, new_conversation=new_conv)
            new_conv = False
            console.print("\n[bold]NotebookLM>[/bold]")
            console.print(Markdown(answer))
            console.print()
        except RuntimeError as e:
            console.print(f"[red]{e}[/red]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

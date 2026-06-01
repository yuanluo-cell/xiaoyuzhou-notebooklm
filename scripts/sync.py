#!/usr/bin/env python3
"""
小宇宙 → NotebookLM 全自动流水线（终端完成，不必开网页）。

  ./scripts/sync.sh     # 导入新播客 + 自动上传到 NotebookLM
  ./scripts/chat.sh     # 在终端与笔记本对话

前提：VPN 可访问 NotebookLM，且已 notebooklm login 一次。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, load_config, resolve_path
from nlm_cli import auth_ok, ensure_notebook, find_cli, upload_file
from upload_state import is_uploaded, load_state, mark_uploaded, save_state

console = Console()
STATE_NAME = "notebooklm_uploaded.json"


def run_script(name: str) -> int:
    script = Path(__file__).parent / name
    return subprocess.run([sys.executable, str(script)], cwd=ROOT).returncode


def collect_upload_candidates(cfg: dict) -> list[tuple[Path, str]]:
    mp4_dir = resolve_path("mp4_dir", cfg)
    audio_dir = resolve_path("audio_dir", cfg)
    prefer_mp4 = cfg.get("notebooklm", {}).get("prefer_mp4", True)
    by_stem: dict[str, Path] = {}
    if prefer_mp4:
        for p in sorted(mp4_dir.glob("*.mp4")):
            by_stem[p.stem] = p
    for p in sorted(audio_dir.glob("*")):
        if p.suffix.lower() not in (".m4a", ".mp3", ".wav"):
            continue
        if p.stem not in by_stem:
            by_stem[p.stem] = p
    return [(path, str(path.relative_to(ROOT))) for path in by_stem.values()]


def pending_uploads(cfg: dict, state: dict) -> list[tuple[Path, str]]:
    return [(p, k) for p, k in collect_upload_candidates(cfg) if not is_uploaded(state, k, p)]


def upload_via_cli(cfg: dict, pending: list[tuple[Path, str]], state_path: Path) -> int:
    cli = find_cli(cfg)
    if not cli:
        console.print(
            "[red]未找到 notebooklm 命令[/red]\n"
            "  安装: uv tool install notebooklm-py  或  pipx install 'notebooklm-py[browser]'"
        )
        return 1

    ok, msg = auth_ok(cli)
    if not ok:
        console.print(f"[red]{msg}[/red]")
        return 1

    logs_dir = resolve_path("logs_dir", cfg)
    state = load_state(state_path)
    nb_id = ensure_notebook(cli, cfg, logs_dir)

    for path, rel_key in pending:
        console.print(f"上传 → NotebookLM: {path.name}")
        upload_file(cli, nb_id, path)
        mark_uploaded(state, rel_key, path)

    save_state(state_path, state)
    console.print(f"\n[green]已上传 {len(pending)} 个新文件[/green]")
    console.print("对话: [cyan]./scripts/chat.sh[/cyan]")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="小宇宙播客 → NotebookLM")
    parser.add_argument("--check", action="store_true", help="只检查状态")
    parser.add_argument("--no-upload", action="store_true", help="只导入本地，不上传")
    parser.add_argument("--skip-import", action="store_true")
    parser.add_argument("--skip-mp4", action="store_true")
    args = parser.parse_args()

    cfg = load_config()
    state_path = resolve_path("logs_dir", cfg) / STATE_NAME
    state = load_state(state_path)
    nlm = cfg.get("notebooklm", {})

    if not args.check and not args.skip_import:
        console.print("[bold]①[/bold] 从小宇宙 Mac App 导入新下载…")
        if run_script("import_from_mac_app.py") != 0:
            return 1

    if not args.check and not args.skip_mp4:
        import shutil

        if shutil.which("ffmpeg"):
            console.print("[bold]②[/bold] 转 MP4…")
            if run_script("audio_to_mp4.py") != 0:
                return 1
        else:
            console.print("[dim]无 ffmpeg，直接上传 m4a[/dim]")

    all_files = collect_upload_candidates(cfg)
    pending = pending_uploads(cfg, state)

    table = Table(title="本地媒资")
    table.add_column("文件")
    table.add_column("NotebookLM")
    for path, rel in all_files:
        st = "已上传" if is_uploaded(state, rel, path) else "待上传"
        table.add_row(path.name, st)
    console.print(table)

    if not all_files:
        console.print("\n[dim]暂无文件。请先在 Mac 小宇宙 App 下载节目。[/dim]")
        return 0
    if args.check:
        cli = find_cli(cfg)
        if cli:
            ok, msg = auth_ok(cli)
            console.print(f"\nNotebookLM CLI: {cli}")
            console.print("[green]认证 OK[/green]" if ok else f"[red]{msg}[/red]")
        return 0

    auto = nlm.get("auto_upload", True) and nlm.get("enabled", True)
    if args.no_upload or not auto:
        if pending:
            console.print(f"\n[yellow]{len(pending)} 个文件待上传[/yellow]（config 关闭 auto_upload 或用了 --no-upload）")
        return 0

    if not pending:
        console.print("\n[dim]无新文件需上传。对话: ./scripts/chat.sh[/dim]")
        return 0

    console.print(f"\n[bold]③[/bold] 上传 {len(pending)} 个新文件到 NotebookLM…")
    return upload_via_cli(cfg, pending, state_path)


if __name__ == "__main__":
    raise SystemExit(main())

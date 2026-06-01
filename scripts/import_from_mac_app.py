#!/usr/bin/env python3
"""
从小宇宙 Mac App 沙盒目录导入已下载的离线音频。

默认路径（用户 ID 目录）:
  ~/Library/Containers/F99B5FE6-0350-4EAA-9667-5A3D153A9FC8/Data/Documents/AudioFile/
"""
from __future__ import annotations

import csv
import re
import shutil
import sys
from pathlib import Path

from rich.console import Console

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, load_config, resolve_path

console = Console()

# Mac App 沙盒（按当前机器；换机后需改或通过 --source 指定）
DEFAULT_APP_AUDIO = Path.home() / (
    "Library/Containers/F99B5FE6-0350-4EAA-9667-5A3D153A9FC8/Data/Documents/AudioFile"
)
EID_PREFIX_RE = re.compile(r"^([a-f0-9]{24})")


def find_app_audio_root(source: Path | None) -> Path | None:
    if source and source.exists():
        return source
    if DEFAULT_APP_AUDIO.exists():
        return DEFAULT_APP_AUDIO
    containers = Path.home() / "Library/Containers"
    for c in containers.iterdir():
        candidate = c / "Data/Documents/AudioFile"
        if candidate.is_dir() and any(candidate.rglob("*.m4a")):
            return candidate
    return None


def iter_downloaded_m4a(audio_root: Path) -> list[tuple[str, Path]]:
    """返回 (episode_id, m4a_path)。"""
    found: list[tuple[str, Path]] = []
    for path in sorted(audio_root.rglob("*.m4a")):
        m = EID_PREFIX_RE.match(path.name)
        if not m:
            continue
        eid = m.group(1)
        found.append((eid, path))
    return found


def load_existing_urls(csv_path: Path) -> set[str]:
    urls: set[str] = set()
    if not csv_path.exists():
        return urls
    with csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            u = (row.get("episode_url") or "").strip()
            if u and not u.startswith("#"):
                urls.add(u)
    return urls


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="从小宇宙 Mac App 导入离线 m4a")
    parser.add_argument("--source", type=Path, default=None, help="AudioFile 根目录")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = load_config()
    audio_root = find_app_audio_root(args.source)
    if not audio_root:
        console.print("[red]未找到小宇宙 App 的 AudioFile 目录[/red]")
        console.print("请确认已在 Mac 版小宇宙中下载节目，或用 --source 指定路径")
        return 1

    dest_dir = resolve_path("audio_dir", cfg)
    csv_path = resolve_path("episodes_csv", cfg)
    episodes = iter_downloaded_m4a(audio_root)

    if not episodes:
        console.print(f"[yellow]{audio_root} 下没有 .m4a 文件[/yellow]")
        return 1

    console.print(f"[bold]App 音频目录:[/bold] {audio_root}")
    console.print(f"[bold]导入目标:[/bold] {dest_dir}\n")

    existing_urls = load_existing_urls(csv_path)
    new_rows: list[dict] = []
    copied = 0

    for eid, src in episodes:
        url = f"https://www.xiaoyuzhoufm.com/episode/{eid}"
        dest = dest_dir / f"{eid}.m4a"
        size_mb = src.stat().st_size / (1024 * 1024)
        console.print(f"  {eid}  ({size_mb:.1f} MB)")
        if not args.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists() or dest.stat().st_size != src.stat().st_size:
                shutil.copy2(src, dest)
                copied += 1
            else:
                console.print("    [dim]已存在，跳过复制[/dim]")
            if url not in existing_urls:
                new_rows.append(
                    {
                        "played_at": "",
                        "title": eid,
                        "episode_url": url,
                    }
                )
                existing_urls.add(url)

    if new_rows and not args.dry_run:
        write_header = not csv_path.exists() or csv_path.stat().st_size < 10
        with csv_path.open("a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["played_at", "title", "episode_url"])
            if write_header:
                w.writeheader()
            w.writerows(new_rows)
        console.print(f"\n[green]已追加 {len(new_rows)} 条到 episodes.csv[/green]")

    console.print(f"\n共发现 {len(episodes)} 个离线单集" + (f"，新复制 {copied} 个" if not args.dry_run else "（dry-run）"))
    console.print("下一步: python scripts/audio_to_mp4.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

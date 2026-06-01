#!/usr/bin/env python3
"""将 data/audio 中的文件转为 MP4（静态封面或纯色底）。"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, load_config, resolve_path

console = Console()


def require_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        console.print("[red]未找到 ffmpeg，请先安装: brew install ffmpeg[/red]")
        sys.exit(1)
    return path


def audio_to_mp4(
    ffmpeg: str,
    audio: Path,
    mp4_out: Path,
    cover: Path | None,
    cfg: dict,
) -> None:
    mp4_out.parent.mkdir(parents=True, exist_ok=True)
    mp4_cfg = cfg.get("mp4", {})
    vcodec = mp4_cfg.get("video_codec", "libx264")
    acodec = mp4_cfg.get("audio_codec", "aac")
    color = mp4_cfg.get("fallback_color", "0x1a1a2e")

    if cover and cover.exists():
        cmd = [
            ffmpeg, "-y",
            "-loop", "1", "-i", str(cover),
            "-i", str(audio),
            "-c:v", vcodec, "-tune", "stillimage",
            "-c:a", acodec, "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            str(mp4_out),
        ]
    else:
        cmd = [
            ffmpeg, "-y",
            "-f", "lavfi", "-i", f"color=c={color}:s=1280x720:r=1",
            "-i", str(audio),
            "-c:v", vcodec,
            "-c:a", acodec, "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            str(mp4_out),
        ]
    subprocess.run(cmd, check=True, capture_output=True)


def main() -> int:
    cfg = load_config()
    ffmpeg = require_ffmpeg()
    audio_dir = resolve_path("audio_dir", cfg)
    mp4_dir = resolve_path("mp4_dir", cfg)
    covers_dir = resolve_path("covers_dir", cfg)

    files = sorted(audio_dir.glob("*"))
    if not files:
        console.print("[yellow]data/audio 为空，请先运行 download.py[/yellow]")
        return 1

    ok, fail = 0, 0
    for audio in files:
        if audio.name.startswith("."):
            continue
        stem = audio.stem
        out = mp4_dir / f"{stem}.mp4"
        if out.exists():
            console.print(f"[dim]跳过: {out.name}[/dim]")
            ok += 1
            continue
        cover = None
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            c = covers_dir / f"{stem}{ext}"
            if c.exists():
                cover = c
                break
        try:
            audio_to_mp4(ffmpeg, audio, out, cover, cfg)
            console.print(f"[green]✓[/green] {out.name}")
            ok += 1
        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗[/red] {audio.name}: ffmpeg 失败")
            if e.stderr:
                console.print(e.stderr.decode(errors="replace")[-500:])
            fail += 1

    console.print(f"\n完成: 成功 {ok}, 失败 {fail} → {mp4_dir}")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())

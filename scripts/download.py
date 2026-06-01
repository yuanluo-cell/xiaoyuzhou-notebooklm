#!/usr/bin/env python3
"""按 episodes.csv 下载小宇宙单集音频。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx
from rich.console import Console
from rich.progress import Progress

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, load_config, load_episodes, resolve_path, safe_filename

console = Console()
EPISODE_API = "https://www.xiaoyuzhoufm.com/api/v1/episode/get"


def fetch_episode_meta(client: httpx.Client, episode_id: str) -> dict:
    r = client.get(EPISODE_API, params={"eid": episode_id}, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise RuntimeError(data.get("msg", "API error"))
    return data["data"]


def pick_audio_url(episode: dict) -> str | None:
    media = episode.get("media") or {}
    for key in ("audio", "source", "backupSource"):
        url = media.get(key)
        if isinstance(url, str) and url.startswith("http"):
            return url
    enclosure = episode.get("enclosure") or {}
    url = enclosure.get("url")
    if isinstance(url, str) and url.startswith("http"):
        return url
    return None


def download_file(client: httpx.Client, url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with client.stream("GET", url, follow_redirects=True, timeout=120) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_bytes(65536):
                f.write(chunk)


def main() -> int:
    cfg = load_config()
    episodes = load_episodes(cfg)
    if not episodes:
        console.print("[yellow]episodes.csv 里没有符合日期的记录，请先填入 episode 链接[/yellow]")
        return 1

    audio_dir = resolve_path("audio_dir", cfg)
    logs_dir = resolve_path("logs_dir", cfg)
    logs_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = logs_dir / "download_manifest.jsonl"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://www.xiaoyuzhoufm.com/",
    }

    ok, fail = 0, 0
    with httpx.Client(headers=headers) as client, Progress() as progress:
        task = progress.add_task("下载", total=len(episodes))
        for ep in episodes:
            progress.advance(task)
            eid = ep["episode_id"]
            title = ep["title"]
            out_base = safe_filename(title, eid)
            existing = list(audio_dir.glob(f"{out_base}.*"))
            if existing:
                console.print(f"[dim]跳过已存在: {existing[0].name}[/dim]")
                ok += 1
                continue
            try:
                meta = fetch_episode_meta(client, eid)
                audio_url = pick_audio_url(meta)
                if not audio_url:
                    raise RuntimeError("未找到音频地址")
                ext = ".m4a" if ".m4a" in audio_url.split("?")[0] else ".mp3"
                dest = audio_dir / f"{out_base}{ext}"
                download_file(client, audio_url, dest)
                record = {**ep, "audio_path": str(dest.relative_to(ROOT)), "audio_url": audio_url}
                with manifest_path.open("a", encoding="utf-8") as mf:
                    mf.write(json.dumps(record, ensure_ascii=False) + "\n")
                console.print(f"[green]✓[/green] {dest.name}")
                ok += 1
            except Exception as e:
                console.print(f"[red]✗[/red] {title}: {e}")
                fail += 1

    console.print(f"\n完成: 成功 {ok}, 失败 {fail}")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())

"""共享配置与工具。"""
from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
EPISODE_ID_RE = re.compile(r"xiaoyuzhoufm\.com/episode/([a-f0-9]+)", re.I)


def load_config() -> dict:
    path = ROOT / "config.yaml"
    if not path.exists():
        path = ROOT / "config.example.yaml"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_path(key: str, cfg: dict) -> Path:
    return ROOT / cfg["paths"][key]


def parse_since(cfg: dict) -> datetime:
    return datetime.strptime(cfg["since_date"], "%Y-%m-%d")


def load_episodes(cfg: dict) -> list[dict]:
    since = parse_since(cfg)
    csv_path = resolve_path("episodes_csv", cfg)
    rows: list[dict] = []
    with csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            url = (row.get("episode_url") or "").strip()
            if not url or url.startswith("#"):
                continue
            played_raw = (row.get("played_at") or "").strip()
            try:
                played = datetime.strptime(played_raw, "%Y-%m-%d")
            except ValueError:
                continue
            if played < since:
                continue
            m = EPISODE_ID_RE.search(url)
            if not m:
                continue
            rows.append(
                {
                    "played_at": played_raw,
                    "title": (row.get("title") or m.group(1)).strip(),
                    "episode_url": url,
                    "episode_id": m.group(1),
                }
            )
    return rows


def safe_filename(title: str, episode_id: str) -> str:
    base = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", title)[:80].strip() or episode_id
    return f"{base}_{episode_id}"

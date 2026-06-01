"""记录已上传到 NotebookLM 的文件，避免重复上传。"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def file_fingerprint(path: Path) -> dict:
    st = path.stat()
    return {"size": st.st_size, "mtime": int(st.st_mtime)}


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"notebook_id": None, "files": {}}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("notebook_id", None)
    data.setdefault("files", {})
    return data


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def is_uploaded(state: dict, rel_key: str, path: Path) -> bool:
    entry = state["files"].get(rel_key)
    if not entry:
        return False
    fp = file_fingerprint(path)
    return entry.get("size") == fp["size"] and entry.get("mtime") == fp["mtime"]


def mark_uploaded(state: dict, rel_key: str, path: Path) -> None:
    fp = file_fingerprint(path)
    state["files"][rel_key] = {
        **fp,
        "uploaded_at": datetime.now(timezone.utc).astimezone().isoformat(),
    }

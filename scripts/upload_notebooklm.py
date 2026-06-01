#!/usr/bin/env python3
"""兼容入口：请优先使用 scripts/sync.py"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    sync = Path(__file__).parent / "sync.py"
    raise SystemExit(subprocess.call([sys.executable, str(sync), "--skip-import", "--skip-mp4", *sys.argv[1:]]))

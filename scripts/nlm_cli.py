"""通过系统 notebooklm CLI（~/.local/bin/notebooklm）上传与对话。"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console

console = Console()

CONTEXT_NAME = "notebooklm_context.json"


def find_cli(cfg: dict) -> Path | None:
    custom = cfg.get("notebooklm", {}).get("cli_bin")
    if custom:
        p = Path(custom).expanduser()
        if p.is_file():
            return p
    # 必须优先系统安装（~/.local/bin），避免 venv 里 Python 3.9 的旧版 notebooklm
    for candidate in (
        Path.home() / ".local/bin/notebooklm",
        Path("/opt/homebrew/bin/notebooklm"),
        Path("/usr/local/bin/notebooklm"),
    ):
        if candidate.is_file():
            return candidate
    found = shutil.which("notebooklm")
    if found:
        p = Path(found)
        # venv 内的 notebooklm-py 0.1.x 在 Py3.9 会崩溃，跳过
        if ".venv" in str(p) or "site-packages" in str(p):
            return None
        return p
    return None


def context_path(logs_dir: Path) -> Path:
    return logs_dir / CONTEXT_NAME


def load_context(logs_dir: Path) -> dict:
    p = context_path(logs_dir)
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def save_context(logs_dir: Path, ctx: dict) -> None:
    logs_dir.mkdir(parents=True, exist_ok=True)
    with context_path(logs_dir).open("w", encoding="utf-8") as f:
        json.dump(ctx, f, ensure_ascii=False, indent=2)


def run_cli(cli: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    return subprocess.run(
        [str(cli), *args],
        capture_output=True,
        text=True,
        env=env,
        check=check,
    )


def auth_ok(cli: Path) -> tuple[bool, str]:
    r = run_cli(cli, "auth", "check", "--test", check=False)
    out = (r.stdout or "") + (r.stderr or "")
    if "Token fetch" in out and "✓ pass" in out.split("Token fetch")[-1][:80]:
        return True, ""
    if "location=unsupported" in out or "unsupported" in out:
        return False, (
            "当前网络无法访问 NotebookLM（location=unsupported）。\n"
            "  → 先开 VPN，终端执行: notebooklm login\n"
            "  → 验证: notebooklm auth check --test"
        )
    if "Token fetch" in out and "✗ fail" in out:
        return False, "登录已过期。开 VPN 后执行: notebooklm login"
    return r.returncode == 0, out.strip() or "认证检查失败"


def ensure_notebook(cli: Path, cfg: dict, logs_dir: Path) -> str:
    ctx = load_context(logs_dir)
    nb_id = ctx.get("notebook_id") or cfg.get("notebooklm", {}).get("notebook_id")
    title = cfg.get("notebooklm", {}).get("notebook_title", "小宇宙播客")

    if nb_id:
        run_cli(cli, "use", nb_id, check=False)
        return nb_id

    r = run_cli(cli, "create", title, "--json", check=False)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "create 失败").strip())
    try:
        data = json.loads(r.stdout)
        nb = data.get("notebook") or data
        nb_id = nb.get("id") or data.get("id") or data.get("notebook_id")
    except json.JSONDecodeError:
        nb_id = None
    if not nb_id:
        raise RuntimeError(f"无法解析 notebook id:\n{r.stdout}")

    ctx = {
        "notebook_id": nb_id,
        "notebook_title": title,
        "created_at": datetime.now(timezone.utc).astimezone().isoformat(),
    }
    save_context(logs_dir, ctx)
    run_cli(cli, "use", nb_id, check=False)
    console.print(f"[green]已创建笔记本[/green]: {title} ({nb_id})")
    return nb_id


def upload_file(cli: Path, nb_id: str, path: Path) -> None:
    r = run_cli(
        cli,
        "source",
        "add",
        str(path.resolve()),
        "--type",
        "file",
        "--notebook",
        nb_id,
        check=False,
    )
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip()
        raise RuntimeError(err or f"上传失败: {path.name}")
    console.print(f"[green]✓[/green] 已上传: {path.name}")


def ask(cli: Path, question: str, *, new_conversation: bool = False) -> str:
    args = ["ask", question]
    if new_conversation:
        args.insert(1, "--new")
    r = run_cli(cli, *args, check=False)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "ask 失败").strip())
    return (r.stdout or "").strip()

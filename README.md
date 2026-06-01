# xiaoyuzhou-notebooklm

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**听过的播客，别只躺在 App 里。**  
Mac 小宇宙一键导出 → 自动进 [NotebookLM](https://notebooklm.google.com) → **终端里直接问 AI**。

不用每天开网页整理笔记；下载、上传、对话，两条命令搞定。

```
小宇宙 App 下载  →  ./scripts/sync.sh  →  ./scripts/chat.sh
```

> 集成 [notebooklm-py](https://github.com/teng-lin/notebooklm-py) CLI。目标是 **NotebookLM**，不是 Notion。

---

## 你能做什么

| 能力 | 说明 |
|------|------|
| 读 App 离线文件 | 从 Mac 小宇宙沙盒导入已下载的 `.m4a` |
| 增量上传 | 只传新单集，同一 NotebookLM 笔记本 |
| 终端对话 | 基于播客内容提问、总结、对比观点 |
| Cursor Skill | Agent 知道完整流程，见 [`skill/SKILL.md`](skill/SKILL.md) |

---

## 快速开始

```bash
git clone https://github.com/yuanluo-cell/xiaoyuzhou-notebooklm.git
cd xiaoyuzhou-notebooklm

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uv tool install notebooklm-py

cp config.example.yaml config.yaml
# VPN 开启后：
./scripts/nlm login
./scripts/nlm auth check --test

./scripts/sync.sh
./scripts/chat.sh
```

⚠️ 使用 `./scripts/nlm`，不要在 venv 里直接跑 `notebooklm`（Python 3.9 会报错）。

---

## 命令

| 命令 | 作用 |
|------|------|
| `./scripts/sync.sh` | 导入 + 上传新文件 |
| `./scripts/chat.sh` | 交互对话 |
| `./scripts/nlm auth check --test` | 检查登录 |
| `./scripts/install_skill.sh` | 安装 Cursor Skill 到 `~/.cursor/skills/` |

---

## Cursor Agent Skill

本仓库包含 Agent Skill，路径：

- 项目内：`.cursor/skills/xiaoyuzhou-notebooklm/SKILL.md`
- 可分发：`skill/SKILL.md`

安装到本机：

```bash
./scripts/install_skill.sh
```

---

## 要求

- macOS + 小宇宙 Mac 版（已下载节目）
- 能访问 Google（VPN）以使用 NotebookLM
- Python 3.9+（项目 venv）；notebooklm CLI 需 3.10+（`uv tool install`）

---

## 发布你自己的 Fork

见 [PUBLISH.md](PUBLISH.md)：绑定 GitHub、`gh repo create`、勿提交密钥与音频。

---

## License

MIT — 见 [LICENSE](LICENSE)

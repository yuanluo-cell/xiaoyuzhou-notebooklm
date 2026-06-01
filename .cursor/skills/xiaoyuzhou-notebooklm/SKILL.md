---
name: xiaoyuzhou-notebooklm
description: >-
  Syncs 小宇宙 (Xiaoyuzhou) offline podcasts from the Mac app into a local
  library, auto-uploads new audio to Google NotebookLM via notebooklm-py CLI,
  and chats in the terminal. Use when the user mentions 小宇宙, podcast download,
  NotebookLM upload, xiaoyuzhou-notebooklm, or terminal Q&A over listened episodes.
---

# 小宇宙播客 → NotebookLM（终端全自动）

把 Mac 小宇宙里**已下载**的播客，变成 NotebookLM 里可对话的知识库——**不用每天开网页**，一条命令同步，终端里提问。

## 何时启用本 Skill

- 用户提到：小宇宙、播客下载、NotebookLM、听过的节目要总结/对话
- 仓库路径含 `xiaoyuzhou-notebooklm`
- 需要：导入 App 离线音频 → 上传云端笔记本 → `notebooklm ask`

> 目标是 **NotebookLM**（Google），不是 Notion。

## 仓库结构（执行前先 `cd` 到仓库根）

| 路径 | 作用 |
|------|------|
| `scripts/sync.sh` | **主入口**：导入 + 自动上传 |
| `scripts/chat.sh` | 终端与笔记本对话 |
| `scripts/nlm` | 包装 `~/.local/bin/notebooklm`（勿用 venv 内旧 CLI） |
| `scripts/setup_notebooklm.sh` | 首次 VPN + 登录 |
| `data/audio/` | 本地 m4a |
| `logs/notebooklm_context.json` | 笔记本 ID（勿提交 git） |
| `config.yaml` | 用户配置（勿提交 git） |

## 首次环境（用户只做一次）

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uv tool install notebooklm-py    # → ~/.local/bin/notebooklm，需 Python 3.10+

# VPN 开启后
./scripts/nlm login
./scripts/nlm auth check --test  # Token fetch 必须 pass
cp config.example.yaml config.yaml
```

**禁止**在 venv 激活时直接运行 `notebooklm`（venv 若装了旧版 notebooklm-py 会在 Python 3.9 崩溃）。一律用 `./scripts/nlm`。

## 标准工作流

```bash
# 1. 用户在小宇宙 Mac App 里下载节目

# 2. 同步（导入 + 只上传新文件）
./scripts/sync.sh

# 3. 终端对话
./scripts/chat.sh
# 或单次：./scripts/chat.sh "总结最近几期播客"
```

`--skip-import`：音频已在 `data/audio/` 时只上传。  
`--no-upload`：只导入本地。  
`--check`：看本地文件与认证状态。

## Agent 执行清单

1. 确认用户在 **Mac** 且已安装小宇宙 App，节目为「下载」状态（非仅在线播放）。
2. 检查 `~/.local/bin/notebooklm` 存在；`./scripts/nlm auth check --test` 通过。
3. 若失败且含 `location=unsupported` → 提示开 VPN 后 `./scripts/nlm login`，不要改业务脚本。
4. 运行 `./scripts/sync.sh`；上传成功后提示 `./scripts/chat.sh`。
5. 新播客重复步骤 2–4；已上传文件由 `logs/notebooklm_uploaded.json` 去重。
6. 勿将 `config.yaml`、`logs/*.json`、`~/.notebooklm/` 提交到 git。

## 故障速查

| 现象 | 处理 |
|------|------|
| `str \| None` TypeError | 用了 venv 的 notebooklm → 改用 `./scripts/nlm` |
| `location=unsupported` | VPN + 重新 login |
| `KeyError: paths` | `config.yaml` 缺 `paths` 段 → 从 `config.example.yaml` 合并 |
| 无新文件 | App 内先下载；再 `sync` |

## 延伸阅读

- 用户文档：`README.md`
- 进展与计划：`STATUS.md`
- 发布到 GitHub：`PUBLISH.md`

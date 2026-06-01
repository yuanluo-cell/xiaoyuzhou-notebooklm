# 项目进展（终端版 NotebookLM 工作流）

## 目标 vs 现状

| 你的需求 | 状态 |
|----------|------|
| 下载后自动传到 Notebook | ✅ 脚本已接好（`sync.sh`） |
| 在笔记里对话 | ✅ 终端 `chat.sh`（底层 `notebooklm ask`） |
| 不必日常开网页 | ✅ 仅首次 `notebooklm login` 要弹浏览器 |
| 纯本地 NotebookLM | ❌ 不可能——NotebookLM 是 Google 云端服务 |

## 当前卡点

**VPN / 网络**：`notebooklm auth check --test` 报 `location=unsupported`  
→ 上传和对话都**暂时用不了**，与脚本无关。

## 本地已完成

- 4 集 m4a 在 `data/audio/`
- `sync` / `chat` / `setup_notebooklm` 脚本就绪
- 使用系统 `~/.local/bin/notebooklm`（0.3.x），不用 venv 里坏掉的 0.1.1

## 你接下来要做（按顺序）

```bash
# 1. 开 VPN

# 2. 重新登录（VPN 下）
notebooklm login
notebooklm auth check --test    # Token fetch 应为 pass

# 3. 上传 4 集
cd /Users/ada_ly/vibe_coding/xiaoyuzhou-notebooklm
source .venv/bin/activate
./scripts/sync.sh --skip-import   # 音频已在本地，只上传

# 4. 终端对话
./scripts/chat.sh
```

## 以后有新播客

```bash
./scripts/sync.sh    # 自动：导入 → 上传新文件
./scripts/chat.sh    # 继续在同一笔记本里问
```

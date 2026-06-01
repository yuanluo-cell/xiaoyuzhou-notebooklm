# 发布到 GitHub（独立仓库 + Skill）

## 一、绑定 GitHub 账号

### 在 Cursor 里

1. **Cursor Settings** → **Account** → 用 GitHub 登录 / Connect GitHub  
2. 或在 **Settings → General → Git**** 确认已配置 `git` 用户名与邮箱

### 在终端（推送代码用）

```bash
# 安装 GitHub CLI（若未装）
brew install gh

gh auth login
# 选 GitHub.com → HTTPS → Login with browser
gh auth status
```

---

## 二、创建独立仓库并推送

在**本目录**（`xiaoyuzhou-notebooklm`）执行：

```bash
cd /Users/ada_ly/vibe_coding/xiaoyuzhou-notebooklm

git init
git add .
git status   # 确认没有 config.yaml、logs/*.json、.venv

git commit -m "$(cat <<'EOF'
Initial release: 小宇宙播客同步到 NotebookLM 的终端流水线

包含 sync/chat 脚本、Cursor Agent Skill，以及 notebooklm-py CLI 集成说明。
EOF
)"

# 创建远程仓库（把 YOUR_USER 换成你的 GitHub 用户名）
gh repo create YOUR_USER/xiaoyuzhou-notebooklm --public --source=. --remote=origin --push
```

若仓库名想自定义：

```bash
gh repo create YOUR_USER/你的仓库名 --public --description "Mac 小宇宙离线播客 → NotebookLM 自动上传与终端对话"
git remote add origin git@github.com:YOUR_USER/你的仓库名.git
git push -u origin main
```

> 默认分支若是 `master`，把上面 `main` 改成 `master`，或先 `git branch -M main`。

---

## 三、安装 Cursor Skill

### 方式 A：克隆仓库后（项目级，推荐协作）

Skill 已在 `.cursor/skills/xiaoyuzhou-notebooklm/SKILL.md`，用 Cursor 打开该仓库即可被 Agent 发现。

### 方式 B：装到个人目录（所有项目可用）

```bash
./scripts/install_skill.sh
# 复制到 ~/.cursor/skills/xiaoyuzhou-notebooklm/
```

### 方式 C：从 GitHub 安装（仓库公开后）

```bash
git clone https://github.com/YOUR_USER/xiaoyuzhou-notebooklm.git
cd xiaoyuzhou-notebooklm
./scripts/install_skill.sh
```

---

## 四、仓库里应包含 / 不应包含

| 应提交 | 勿提交 |
|--------|--------|
| `scripts/`、`skill/`、`.cursor/skills/` | `.venv/` |
| `README.md`、`LICENSE`、`PUBLISH.md` | `config.yaml`（含个人配置） |
| `config.example.yaml` | `logs/notebooklm_*.json` |
| `requirements.txt` | `data/audio/*.m4a` |

---

## 五、README 徽章（可选）

仓库创建后可在 `README.md` 顶部加：

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
```

并把克隆地址里的 `YOUR_USER` 替换为真实用户名。

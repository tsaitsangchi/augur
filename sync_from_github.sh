#!/usr/bin/env bash
# 從 GitHub 同步本機 augur 到最新(取代人工 fetch+merge+pip install 流程)。
# 用法: bash ~/project/augur/sync_from_github.sh
# 只做安全的 fast-forward;分岔/衝突一律停手不動,印訊息交人(或 Claude)判斷。全本地、零 Claude usage。
set -u
ROOT="$HOME/project/augur"
VENV_PY="$ROOT/venv/bin/python"
VENV_PIP="$ROOT/venv/bin/pip"
REMOTE="origin"
BRANCH="main"

cd "$ROOT" || { echo "✗ 找不到專案目錄 $ROOT"; exit 1; }

echo "同步 augur ← GitHub($REMOTE/$BRANCH)…"

# 0) 前置檢查:分支 + 乾淨樹
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "$BRANCH" ]; then
  echo "✗ 目前在分支 '$current_branch'、非 '$BRANCH',請自行處理(不自動切分支)"; exit 1
fi
if [ -n "$(git status --porcelain)" ]; then
  echo "✗ working tree 不乾淨(有未 commit 改動),請先 commit 或 stash 再同步——不對髒樹做 merge"
  git status --short
  exit 1
fi

# 1) fetch
if ! git fetch "$REMOTE" "$BRANCH" 2>&1; then
  echo "✗ git fetch 失敗(網路或認證問題),中止"; exit 1
fi

before=$(git rev-parse HEAD)
remote_head=$(git rev-parse "$REMOTE/$BRANCH")

if [ "$before" = "$remote_head" ]; then
  echo "✓ 已是最新($before),無需同步"
  exit 0
fi

# 2) 只做安全 fast-forward;分岔就停手交人判斷
if ! git merge-base --is-ancestor HEAD "$REMOTE/$BRANCH"; then
  echo "✗ 本地與遠端已分岔(雙方各有對方沒有的 commit)——不自動 merge/rebase/reset"
  echo "  本地領先: $(git log --oneline "$REMOTE/$BRANCH"..HEAD | wc -l) commit"
  echo "  遠端領先: $(git log --oneline HEAD.."$REMOTE/$BRANCH" | wc -l) commit"
  echo "  請人工(或請 Claude)確認後手動處理"
  exit 1
fi

echo "  fast-forward $before → $remote_head"
if ! git merge --ff-only "$REMOTE/$BRANCH"; then
  echo "✗ fast-forward merge 失敗,中止"; exit 1
fi
echo "✓ merge 完成"

# 3) 依變動範圍決定要不要重裝套件 + smoke test(不變動就省下這段 usage)
changed_files=$(git diff --name-only "$before" "$remote_head")
if echo "$changed_files" | grep -qE '^(src/|pyproject\.toml|setup\.py|setup\.cfg)'; then
  echo "  偵測到 src/ 或套件設定變動 → 重跑 pip install -e ."
  if [ -x "$VENV_PIP" ]; then
    "$VENV_PIP" install -e . -q || { echo "✗ pip install -e . 失敗"; exit 1; }
    "$VENV_PY" -c "import augur" || { echo "✗ import augur 失敗,新碼可能有問題"; exit 1; }
    echo "✓ pip install -e . + import smoke test 通過"
  else
    echo "✗ 找不到 $VENV_PIP,請自行檢查 venv"
    exit 1
  fi
else
  echo "  無 src/ 或套件設定變動,略過 pip install"
fi

echo "════════════════════════════════════════════"
echo "  ✓ 同步完成:$before → $remote_head"
echo "  $(git log --oneline "$before".."$remote_head" | wc -l) 個新 commit"
echo "════════════════════════════════════════════"

# DESKTOP-8MQPFS8：改指 public `augur` monorepo（觀察期最後一塊）

* **性質**：[I] 他機操作清單。在 **`hostname=DESKTOP-8MQPFS8`** 的 WSL 終端執行。
* **目標**：此機不再以 `augur-constitution`／`augur-constitution-archived` 為開發 remote；正典＝`https://github.com/tsaitsangchi/augur.git`（`main`）。
* **GB10 無法代跑**：本機與 DESKTOP 無直連；須在 DESKTOP 上執行本檔。

---

## A. 若已有工作樹（改 `origin`，保留本機 `.env`／venv／資料）

在**現有** clone 根（常見曾是 `~/project/augur`、`~/augur`、或舊 constitution 路徑）執行：

```bash
hostname   # 必須是 DESKTOP-8MQPFS8
pwd
git remote -v

# 1) 指向 public monorepo
git remote set-url origin https://github.com/tsaitsangchi/augur.git
# 若曾另加 constitution remote：
git remote remove constitution 2>/dev/null || true
git remote remove augur-constitution 2>/dev/null || true

# 2) 取 main（合 PR #3 後含治權+應用）
git fetch origin
git checkout main
git pull --ff-only origin main

# 3) 確認
git remote -v
# 期望僅：origin → github.com/tsaitsangchi/augur.git
test -d src/augur && test -d constitution && test -d tools/constitution_mcp && echo MONOREPO_OK

# 4) .env（本機、不進 git）
test -f .env && grep -E '^PROJECT_ROOT=' .env || echo 'NO_.env — 從 .env.example 複製後填密鑰'
# PROJECT_ROOT 應為此機實際路徑，例如：
#   PROJECT_ROOT=/home/hugo/project/augur
# 勿抄 GB10 的 /home/giga/augur
```

若 `git pull --ff-only` 因本地分叉失敗：先 `git status`；有未提交變更先 stash／commit，再決定 merge 或重新 clone（見 B）。

---

## B. 若寧願乾淨重 clone（舊樹只當資料／.env 來源）

```bash
# 假設舊樹在 OLD，新樹在 NEW
OLD="${OLD:-$HOME/project/augur}"
NEW="${NEW:-$HOME/project/augur-monorepo}"

git clone https://github.com/tsaitsangchi/augur.git "$NEW"
cd "$NEW" && git checkout main

# 搬本機密鑰（勿 commit）
if [[ -f "$OLD/.env" ]]; then
  cp -a "$OLD/.env" "$NEW/.env"
  # 編輯 PROJECT_ROOT=$NEW
fi

# 舊樹改名停寫
mv "$OLD" "${OLD}.pre-monorepo-$(date +%Y%m%d)"
# 可選：ln -s "$NEW" "$OLD"   # 若腳本仍寫死舊路徑
```

---

## C. 驗收（貼回 GB10／Steward 即可結觀察期）

```bash
hostname
cd <repo根>
git remote -v
git log -1 --oneline
test -d src/augur && test -d constitution && echo OK_LAYOUT
# 不應再出現：
git remote -v | grep -i constitution && echo STILL_HAS_CONSTITUTION_REMOTE || echo NO_CONSTITUTION_REMOTE
```

通過後可回 GB10 執行**步 6**（刪 `augur-constitution-archived`）。

---

## 勿做

* 勿再 `git push` 到 `augur-constitution`／`…-archived`（已 archive 唯讀）。
* 勿把 GB10 的 `/home/giga/augur` 路徑寫進此機 `.env`。
* 勿把 `.env`／dump 推進 public `augur`。

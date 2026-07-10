---
name: local-handoff-tooling
description: "三支本地零-usage 工具(sync_from_github/read_handoff/sync_memory)+ 記憶隨 repo 遷移機制,供跨機接續"
metadata: 
  node_type: memory
  type: project
  originSessionId: 72546fba-9700-443b-8926-863d212acd39
---

repo 根目錄有**五支**「本地優先、零 Claude usage」的接續工具(2026-07-10 建、實測通過;守 CLAUDE #28;入憲 CLAUDE #31 換機接續慣例、v1.23):

- **`bash resume_project.sh`** — **一鍵換機接續 orchestrator**:串 檢 `.env` → `pip install -e .` → `sync_from_github.sh` → `sync_memory.py restore` → DB 偵測(已存在絕不摧毀、缺才建)→ import smoke;加 `--with-db` 連 DB 匯入。
- **`bash sync_from_github.sh`** — 從 GitHub 安全同步:只做 fast-forward,工作樹髒/與遠端分岔即停手交人判斷,按需 `pip install -e .`+import smoke test。
- **`python3 sync_memory.py`** — Claude memory ⇄ repo 快照傳輸:`export`(活記憶 `~/.claude/projects/<mangled>/memory/` → repo `handoff_memory/`)、`restore`(repo→活,覆蓋前自動備份 `memory_backup_<ts>/`、活記憶獨有檔保留不動)、無參數=`status`。活記憶目錄由當前 repo 位置推導(mangle `/`→`-`),故新機 clone 到不同路徑亦正確。
- **`bash import_database.sh`** — 一鍵 DB 匯入:自動判 dump 格式(**tar-含-Fd目錄**〔augur #30 慣例、`pg_restore --list` 對 tar 會失敗故須先解 tar 再 `-Fd -j4`〕/ 純-Fd目錄 / -Fc單檔)→ 建庫 → 平行還原 → `setup_predict_role --apply --confirm` → smoke;`--force` 取代既有庫(破壞性 #6)、`--migrate` 補冪等 DDL、`--dry-run` 只驗不動。dump 預設搜 `~/db_dumps//mnt/d/database//mnt/c/AI`。
- **`python3 read_handoff.py`** — 唯讀:一次讀出 `HANDOFF.md` + memory 全內文(`--list`/`--out`/`--memory-only`);可 `| ollama run qwen3:8b "…"` 餵本地 AI。

**記憶隨 repo 遷移機制(打破「memory 機器本地不隨 git」限制)**:活記憶本不隨 git;現用 `sync_memory.py export` 把它快照進**追蹤目錄 `handoff_memory/`** → commit+push → 新機 `git clone` 後 `python3 sync_memory.py restore` 還原回活記憶。**前提:repo 為 public**,故 export 前已過 #5 機密掃描(記憶無 token/密碼、僅提及變數名,內容為 reports/docs 之濃縮)。

**Why:** 減少 Claude token——讓人/本地 AI 不開 Claude session 即讀全狀態;且讓記憶能跨機接續。
**How to apply:** 換機接續序見 [[cross-machine-handoff]] 與 `HANDOFF.md` §2。記憶有實質更新後,commit 前跑 `sync_memory.py export` 讓 repo 快照同步(否則 `handoff_memory/` 會落後活記憶)。

# 開機／新 Cursor session／接續工作前（aitopatom-b96e）

## 每次

- [ ] `hostname` 顯示 `aitopatom-b96e`（否則停，改用對立機設定包）
- [ ] `cd "${AUGUR_ROOT:-/home/giga/augur}" && git pull --ff-only && git fetch --tags`（過渡期可能是 `augur-code-work` 上的 migrate 分支）
- [ ] `./ops/machines/packs/aitopatom-b96e/setup_check.sh` 通過（須見 monorepo：`tools/`+`src/`）
- [ ] Cursor MCP 頁：`constitution` / `local-llm` / `project-memory` 皆 ready
- [ ] `local_ask` 來源標記含 **`qwen3:30b-a3b`**（不是 4b）

## 改過大量檔案後

- [ ] `python3 -m tools.project_memory_mcp index`
- [ ] `python3 -m tools.project_memory_mcp memory_status` → 新鮮

## PostgreSQL / qdrant（開機常駐）

- [ ] `systemctl --user status augur-postgres.service augur-qdrant.service --no-pager`（應 **active**；unit 範本在 `ops/phase2/systemd/`）
- [ ] 手動備援：`bash ops/phase2/pg_userspace.sh status`／`bash ops/phase2/qdrant_userspace.sh status`
- [ ] 驗證：`ss -ltn | grep -E '5432|6333'`；`pg_isready -h 127.0.0.1 -p 5432`；`curl -sf http://127.0.0.1:6333/`
- [ ] LAN DBeaver：Host=`10.10.130.46` Port=`5432` DB=`augur`；`pg_hba` 含 `10.10.112.0/24`（與 `10.10.130.0/24`、`10.10.114.0/24`）

## 勿在此機假設

- [ ] 不要使用路徑 `/home/giga/augur/augur-constitution`（已廢）
- [ ] 不要套用 WSL2／GTX1650／15GiB 的模型或套件假設（架構為 **aarch64**）
- [ ] 新腳本請用 `AUGUR_ROOT`／`PROJECT_ROOT`（＝`/home/giga/augur`），勿再假設雙目錄

## 密鑰（本機、不進 git）

- [ ] `.env` 若需要已另行備置（gitignore）；`PROJECT_ROOT=/home/giga/augur`
- [ ] 勿把 token 寫進本設定包

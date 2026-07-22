# 開機／新 Cursor session／接續工作前（aitopatom-b96e）

## 每次

- [ ] `hostname` 顯示 `aitopatom-b96e`（否則停，改用對立機設定包）
- [ ] `cd "${AUGUR_ROOT:-/home/giga/augur}" && git pull --ff-only && git fetch --tags`（過渡期可能是 `augur-code-work` 上的 migrate 分支）
- [ ] `./ops/machines/packs/aitopatom-b96e/setup_check.sh` 通過（須見 monorepo：`tools/`+`src/`）
- [ ] Cursor MCP 頁：`constitution` / `local-llm` / `project-memory` 皆 ready（改過 `.cursor/mcp.json` 後須**完整重啟 Cursor**才會掛上）
- [ ] `local_ask` 來源標記含 **`qwen3-coder-next`**（不是 4b）

## 改過大量檔案後

- [ ] `python3 -m tools.project_memory_mcp index`
- [ ] `python3 -m tools.project_memory_mcp memory_status` → 新鮮

## PostgreSQL / qdrant / UI（開機常駐）

- [ ] `systemctl --user status augur-postgres augur-qdrant ollama --no-pager`（infra **active**）
- [ ] UI：`bash ops/phase2/install_services_gb10.sh --status`（advisor 模型＝**`qwen3:30b-a3b`**；埠 8399／8090／8500／8600）
- [ ] **勿**跑根目錄舊 `install_services.sh`（會覆寫 qdrant／另建 `augur-ollama`）
- [ ] 手動備援：`bash ops/phase2/pg_userspace.sh status`／`bash ops/phase2/qdrant_userspace.sh status`
- [ ] 驗證：`ss -ltn | grep -E '5432|6333|11434|8399|8090'`；`curl -sf http://127.0.0.1:8399/v1/models`
- [ ] LAN DBeaver：Host=`10.10.130.46` Port=`5432` DB=`augur`；`pg_hba` 含 `10.10.112.0/24`（與 `10.10.130.0/24`、`10.10.114.0/24`）
- [ ] 遠端開 chat：本機 `ssh -L 8090:127.0.0.1:8090 giga@10.10.130.46` → 瀏覽器 `http://127.0.0.1:8090`

## 勿在此機假設

- [ ] 不要使用路徑 `/home/giga/augur/augur-constitution`（已廢）
- [ ] 不要套用 WSL2／GTX1650／15GiB 的模型或套件假設（架構為 **aarch64**）
- [ ] 新腳本請用 `AUGUR_ROOT`／`PROJECT_ROOT`（＝`/home/giga/augur`），勿再假設雙目錄

## 密鑰（本機、不進 git）

- [ ] `.env` 若需要已另行備置（gitignore）；`PROJECT_ROOT=/home/giga/augur`
- [ ] 勿把 token 寫進本設定包

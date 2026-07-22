# 開機／新 Cursor session／接續工作前（aitopatom-b96e）

## 每次

- [ ] `hostname` 顯示 `aitopatom-b96e`（否則停，改用對立機設定包）
- [ ] `cd /home/giga/augur && git pull --ff-only && git fetch --tags`
- [ ] `./ops/machines/packs/aitopatom-b96e/setup_check.sh` 全綠
- [ ] Cursor MCP 頁：`constitution` / `local-llm` / `project-memory` 皆 ready
- [ ] `local_ask` 來源標記含 **`qwen3:30b-a3b`**（不是 4b）

## 改過大量檔案後

- [ ] `python3 -m tools.project_memory_mcp index`
- [ ] `python3 -m tools.project_memory_mcp memory_status` → 新鮮

## 勿在此機假設

- [ ] 不要假設 PostgreSQL / qdrant 已起（目前 ABSENT）
- [ ] 不要使用路徑 `/home/giga/augur/augur-constitution`（此機不存在）
- [ ] 不要套用 WSL2／GTX1650／15GiB 的模型或套件假設（架構為 **aarch64**）

## 密鑰（本機、不進 git）

- [ ] `.env` 若需要已另行備置（gitignore）
- [ ] 勿把 token 寫進本設定包

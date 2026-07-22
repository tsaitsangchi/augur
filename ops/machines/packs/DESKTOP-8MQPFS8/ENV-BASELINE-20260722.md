# DESKTOP-8MQPFS8 環境基準（鎖定）

* **性質**：[I] 本機實測快照
* **時間**：2026-07-22 19:15 CST
* **用途**：日後在此機運行 Augur／MCP／Ollama／PG 的權威本機參照
* **最佳化計畫**：見同目錄 [`OPTIMIZATION-PLAN.md`](OPTIMIZATION-PLAN.md)

## 1. 平台

| 項 | 值 |
|---|---|
| hostname | `DESKTOP-8MQPFS8` |
| 使用者 | `giga`（sudo；ollama 群組） |
| OS | Ubuntu 24.04.4 LTS（WSL2） |
| Kernel | `6.18.33.2-microsoft-standard-WSL2` |
| 架構 | x86_64 |
| systemd | running（`/etc/wsl.conf` boot.systemd=true） |
| Windows | ~31.91 GiB RAM；12 邏輯處理器 |
| WSL 設定 | `%UserProfile%\.wslconfig` → memory=24GB、processors=12、swap=32GB、swapFile=`D:\wsl\swap.vhdx` |
| WSL 實測 | Mem **23.5 GiB**、Swap **32 GiB**、CPU **12** |

## 2. 硬體

| 項 | 值 |
|---|---|
| CPU | AMD Ryzen 5 3600（6C/12T）、L3 16 MiB |
| GPU | NVIDIA GeForce GTX 1650 4GB、CC 7.5、driver 560.94 |
| GPU 直通 | `/dev/dxg` 存在 |
| CUDA | runtime 12.6（驅動）；`nvcc` 12.0.140 |
| `/` | 1007G vhdx，可用 ~676G |
| C: | 931G，可用 ~108G（緊） |
| D: | 1.9T，可用 ~1.1T；含 `D:\wsl\swap.vhdx` |

## 3. 服務

| 服務 | 狀態 |
|---|---|
| PostgreSQL | **17.10** `main` @5432 **online** |
| Ollama | **0.32.1** @127.0.0.1:11434 **active** |
| 模型 | `qwen3:4b`（~2.5GB）、`nomic-embed-text`（~274MB） |

## 4. 工具鏈

git 2.43 · gh 2.45 · python 3.12.3 · node 18.19 / npm 9.2 · gcc/g++ 13.3 · make 4.3 · nvcc 12.0 · psql 17.10  
未裝：docker

## 5. 專案

| 項 | 值 |
|---|---|
| 正典 clone | `/home/giga/augur/augur-code` |
| remote | `https://github.com/tsaitsangchi/augur.git`（public monorepo） |
| HEAD（檢核時） | `364aae6` |
| 歷史樹 | `/home/giga/augur/_archived_augur-constitution_20260722` |
| `.env` | 存在（gitignore） |
| venv | `augur-code/venv` Python 3.12.3 |
| `.project_memory` | 尚未建立 |

## 6. MCP（本機）

工作區根 `/home/giga/augur` 的 `.cursor/mcp.json`：

- `command=/usr/bin/python3`
- `PYTHONPATH=/home/giga/augur/augur-code`（不依賴 cwd）
- local-llm：`qwen3:4b`、`OLLAMA_NUM_CTX=8192`
- project-memory：`nomic-embed-text`
- servers：constitution / local-llm / project-memory

**勿用**：`qwen3-coder-next`、`qwen3:30b-a3b`（VRAM 不足）。

## 7. 對立機差異（記住）

| | DESKTOP（本機） | GB10 `aitopatom-b96e` |
|---|---|---|
| 架構 | x86_64 WSL2 | aarch64 原生 |
| RAM | ~24GB WSL | ~122 GiB |
| GPU | GTX 1650 4GB | GB10 |
| 建議模型 | **qwen3:4b** | qwen3-coder-next / 30b-a3b |
| PostgreSQL | ✅ | ❌（當時） |
| monorepo 路徑 | `.../augur-code` | 常為 `/home/giga/augur` |

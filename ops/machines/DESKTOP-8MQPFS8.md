# 機器基礎資訊：`DESKTOP-8MQPFS8`

> **性質**：本機實測快照 **[I]**（自動產生，勿手改；手動註記請寫檔尾 NOTES 區塊）。
> **產生工具**：`ops/collect_machine_info.sh` ｜ **產生時間**：2026-07-22 19:34 CST
> 跨機共享說明（專案相依、治理差異）見 [README.md](README.md)。

## 摘要

| 面向 | 值 |
|---|---|
| 主機名 | `DESKTOP-8MQPFS8` |
| 平台 | WSL：yes (WSL2) ｜ 架構：x86_64 |
| OS / 核心 | Ubuntu 24.04.4 LTS ／ `6.18.33.2-microsoft-standard-WSL2` |
| systemd | offline
offline |
| CPU | AMD Ryzen 5 3600 6-Core Processor（6 核 / 12 緒） |
| 記憶體 | 23.5 GiB（swap 32.0 GiB） |
| 系統碟 `/` | 1007G total, 676G avail (30% used) |
| GPU | Failed to initialize NVML: GPU access blocked by the operating system
Failed to properly shut down NVML: GPU access blocked by the operating system |
| GPU 直通 `/dev/dxg` | 不存在 |
| CUDA `nvcc` | 12.0, V12.0.140 |
| PostgreSQL | 17.10（17/main port 5432 (down)） |

## 工具鏈

| 工具 | 版本 |
|---|---|
| git | 2.43.0 |
| gh | 2.45.0 (2025-07-18 Ubuntu 2.45.0-1ubuntu |
| python3 | 3.12.3 |
| node | 18.19.1 |
| npm | 9.2.0 |
| gcc | 13.3.0-6ubuntu2~24.04.1) 13.3.0 |
| make | 4.3 |
| cmake | (未安裝) |
| nvcc | 12.0, V12.0.140 |
| psql | 17.10 (Ubuntu 17.10-1.pgdg24.04+1) |
| docker | (未安裝) |
| ollama |  |

## 手動註記

<!-- NOTES:START -->
（基準快照 2026-07-22 19:15 CST — 全環境檢核後鎖定）

## 角色
開發／驗證 + 資料層（PostgreSQL）；本地小模型 MCP。對立機：aitopatom-b96e（GB10）。

## 硬體／WSL
- Windows 主機 RAM ~31.9 GiB；WSL `.wslconfig`：memory=24GB、processors=12、swap=32GB、swapFile=D:\\wsl\\swap.vhdx
- WSL 實測：Mem≈23.5 GiB、Swap=16 GiB、nproc=12
- GPU：GTX 1650 4GB（sm_75）、driver 560.94、CUDA runtime 12.6、nvcc 12.0.140、/dev/dxg OK
- 磁碟：`/` 可用~676GB；C: 剩~108GB（緊）；D: 可用~1.1TB（swap 在此）

## 服務
- PostgreSQL 17.10 main @5432 online
- Ollama 0.32.1 @11434；模型：qwen3:4b、nomic-embed-text
- systemd=true；使用者 giga（屬 ollama 群組）

## 專案佈局
- 正典：`/home/giga/augur/augur-code` ↔ github.com/tsaitsangchi/augur（monorepo）
- 歷史：`/home/giga/augur/_archived_augur-constitution_20260722`（勿用）
- Cursor workspace 根：`/home/giga/augur`；MCP 用 PYTHONPATH→augur-code
- MCP：constitution / local-llm(qwen3:4b,ctx=8192) / project-memory(nomic-embed-text)
- .env 存在；venv Python 3.12.3；尚未建 .project_memory 索引

## 最佳化計畫

- 見 `ops/machines/packs/DESKTOP-8MQPFS8/OPTIMIZATION-PLAN.md`（2026-07-22）

## 勿做
- 勿用 qwen3-coder-next／30b（VRAM 不夠）
- 勿再掛 archived constitution 的 MCP
- 勿把 GB10 路徑 /home/giga/augur 當此機 monorepo 根（此機 monorepo 在 augur-code/）
<!-- NOTES:END -->

# 機器基礎資訊：`DESKTOP-8MQPFS8`

> **性質**：本機實測快照 **[I]**（自動產生，勿手改；手動註記請寫檔尾 NOTES 區塊）。
> **產生工具**：`ops/collect_machine_info.sh` ｜ **產生時間**：2026-07-25 15:53 CST
> 跨機共享說明（專案相依、治理差異）見 [README.md](README.md)。

## 摘要

| 面向 | 值 |
|---|---|
| 主機名 | `DESKTOP-8MQPFS8` |
| 平台 | WSL：yes (WSL2) ｜ 架構：x86_64 |
| OS / 核心 | Ubuntu 24.04.4 LTS ／ `6.18.33.2-microsoft-standard-WSL2` |
| systemd | running |
| CPU | AMD Ryzen 5 3600 6-Core Processor（6 核 / 12 緒） |
| 記憶體 | 25.4 GiB（swap 140.7 GiB） |
| 系統碟 `/` | 1007G total, 725G avail (25% used) |
| GPU | NVIDIA GeForce GTX 1650, 560.94, 4096 MiB, 7.5 |
| GPU 直通 `/dev/dxg` | 存在 (WSL2 直通) |
| CUDA `nvcc` | 12.0, V12.0.140 |
| PostgreSQL | 17.10（17/main port 5432 (online)） |

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
| cmake | 3.28.3 |
| nvcc | 12.0, V12.0.140 |
| psql | 17.10 (Ubuntu 17.10-1.pgdg24.04+1) |
| docker | 29.1.3, build 29.1.3-0ubuntu3~24.04.2 |
| ollama | 0.32.1 |

## 手動註記

<!-- NOTES:START -->
（實際探測 2026-07-25 14:06–14:07 CST（下午）— **[I] 機器現況**；非憲章。）

## 角色
開發／驗證 + 資料層（PostgreSQL）+ 本地 Ollama／UI 服務。對立機：aitopatom-b96e（GB10）。

## 硬體／WSL（2026-07-25 下午實測）
- hostname=`DESKTOP-8MQPFS8`；uname=`6.18.33.2-microsoft-standard-WSL2`；使用者=`hugo`
- Windows 主機使用者目錄 `/mnt/c/Users/bucke`；`.wslconfig`：memory=26GB、processors=12、swap=128GB、swapFile=`D:\\wsl\\swap.vhdx`、localhostForwarding=true、autoMemoryReclaim=gradual
- WSL 實測：Mem=25 GiB（available 23 GiB）；Swap=140 GiB（128 GiB `/dev/sdc` + 約 12.7 GiB zram）；nproc=12（Ryzen 5 3600 · 6 核／12 緒）
- GPU：GTX 1650 4GB（compute 7.5／sm_75）；nvidia-smi OK（Driver 560.94／CUDA runtime 12.6）；`/dev/dxg` 存在；nvcc 12.0.140
- 磁碟：`/`（ext4 on sdd）1007G · 用 232G · 可用 725G（25%）；`/mnt/c` 931G · 可用 698G；`/mnt/d` 1.9T · 可用 798G
- `/etc/wsl.conf`：`[boot] systemd=true` · `[user] default=hugo`；`systemctl is-system-running`=running

## 軟體棧（augur 相關）
- OS：Ubuntu 24.04.4 LTS（noble）
- Python：系統 3.12.3；venv=`/home/hugo/project/augur/venv/bin/python` 3.12.3
- PostgreSQL：17.10 · cluster `17/main` @5432 **online**；`pg_isready` 回報 accepting connections
- Ollama：**0.32.1** · systemd `ollama.service` **active/enabled** · 聽 `127.0.0.1:11434`
  - 模型：`qwen3:4b`（2.5GB）、`qwen3:8b`（5.2GB）、`nomic-embed-text`（274MB）
- CUDA／nvcc：toolkit 12.0（nvcc）；runtime 見 nvidia-smi 12.6
- 工具：jq 1.7 · cmake 3.28.3 · Docker 29.1.3（daemon active/enabled）· jadx 1.5.3（OpenJDK 21）
- Docker 權限：`hugo` 已在 `docker` group，**目前 session 已生效**；`docker info` 可連 daemon

## 服務狀態（2026-07-25 下午）
| 名稱 | 狀態 | 端口／備註 |
|---|---|---|
| PostgreSQL 17 | online | `:5432` |
| ollama.service | active (systemd) | `:11434` |
| augur-chat | active/enabled (user systemd) | `127.0.0.1:8090`；HTTP 200 |
| augur-advisor | active/enabled (user systemd) | `127.0.0.1:8399`；根路徑 HTTP 404（服務有回應） |
| augur-admin | active/enabled (user systemd) | `127.0.0.1:8500`；HTTP 200 |
| augur-probability | active/enabled (user systemd) | `127.0.0.1:8600`；HTTP 200 |
| augur-qdrant | **inactive/disabled** | `:6333`／`:6334` 均無監聽（qdrant stop） |
| augur-ollama | **auto-restart/enabled（異常）** | 第二套 Ollama；因 system `ollama.service` 已占 `:11434`，bind 失敗並持續重啟 |

## 專案佈局（現行）
- 正典 monorepo：**`/home/hugo/project/augur`**（含 `src/augur`、`constitution/`、`tools/`、`.env` 存在）
- 舊路徑 `/home/giga/augur/...` **已不存在**（勿再當根）
- MCP 慣例：constitution／local-llm（此機小模型；MCP 側常釘 `qwen3:4b`）／project-memory（`nomic-embed-text`）
- 最佳化計畫：`ops/machines/packs/DESKTOP-8MQPFS8/OPTIMIZATION-PLAN.md`

## 已知限制
- **雙 Ollama**：system `ollama.service` 正常，user `augur-ollama.service` enabled 且陷入 restart loop；應擇一保留，勿讓兩者競爭 `:11434`
- system `ollama.service` 的 Environment PATH 仍殘留 `/home/giga/...`，目前服務仍正常
- **Qdrant 已 stop**：`augur-qdrant.service` 存在但 inactive/disabled，且無監聽
- GPU VRAM 僅 4GB：勿載 `qwen3-coder-next`／`30b`；`qwen3:8b` 已在用但偏緊（advisor 現跑 8b）
- `ops/collect_machine_info.sh` 若在 sandbox 跑會假報 NVML blocked／systemd offline／PG down——蒐集須完整權限

## 勿做
- 勿用超大本地模型（VRAM 不夠）
- 勿把 GB10／舊 giga 路徑當此機 monorepo 根
- 勿在本檔寫入 `.env`／密碼／token
- 勿因「可預測」解凍 FinMind／FRED（取數仍凍）
<!-- NOTES:END -->

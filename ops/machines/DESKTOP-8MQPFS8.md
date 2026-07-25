# 機器基礎資訊：`DESKTOP-8MQPFS8`

> **性質**：本機實測快照 **[I]**（自動產生，勿手改；手動註記請寫檔尾 NOTES 區塊）。
> **產生工具**：`ops/collect_machine_info.sh` ｜ **產生時間**：2026-07-25 13:38 CST
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
| 系統碟 `/` | 1007G total, 722G avail (25% used) |
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
（接續探測 2026-07-25 08:05 CST — [I] 機器現況；非憲章。先前 2026-07-22 快照已由本節覆寫路徑／服務現況。）

## 角色
開發／驗證 + 資料層（PostgreSQL）+ 本地 Ollama／UI 服務。對立機：aitopatom-b96e（GB10）。

## 硬體／WSL（2026-07-25 實測）
- hostname=`DESKTOP-8MQPFS8`；uname=`6.18.33.2-microsoft-standard-WSL2`；使用者=`hugo`（非舊註 giga）
- Windows 主機使用者目錄 `/mnt/c/Users/bucke`；`.wslconfig`：memory=24GB、processors=12、**swap=64GB**、swapFile=`D:\\wsl\\swap.vhdx`、localhostForwarding=true
- WSL 實測：Mem≈23.5 GiB、Swap≈64 GiB、nproc=12（Ryzen 5 3600 · 6 核／12 緒）
- GPU：GTX 1650 4GB（compute 7.5／sm_75）；nvidia-smi OK（Driver 560.94／CUDA runtime 12.6）；`/dev/dxg` 存在；nvcc 12.0.140
- 磁碟：`/`（ext4 on sdd）1007G · 用 235G · 可用 721G（25%）；`/mnt/c` 931G · 可用 699G；`/mnt/d` 1.9T · 可用 798G
- `/etc/wsl.conf`：`[boot] systemd=true` · `[user] default=hugo`；`systemctl is-system-running`=running

## 軟體棧（augur 相關）
- OS：Ubuntu 24.04.4 LTS（noble）
- Python：系統 3.12.3；venv=`/home/hugo/project/augur/venv/bin/python` 3.12.3
- PostgreSQL：17.10 · cluster `17/main` @5432 **online**（`pg_isready` OK）；套件 `postgresql-17-pgvector` **0.8.5** 已裝（本探測未以 DB role 連入驗 `CREATE EXTENSION`，因 peer／sudo 擋）
- Ollama：**0.32.1** · systemd `ollama.service` **active/enabled** · 聽 `127.0.0.1:11434`
  - 模型：`qwen3:4b`（2.5GB）、`qwen3:8b`（5.2GB）、`nomic-embed-text`（274MB）
- CUDA／nvcc：toolkit 12.0（nvcc）；runtime 見 nvidia-smi 12.6
- 其餘：git 2.43.0 · node 18.19.1 · npm 9.2.0 · gh 2.45.0 · docker／cmake 未裝

## 服務狀態（2026-07-25）
| 名稱 | 狀態 | 端口／備註 |
|---|---|---|
| PostgreSQL 17 | online | `:5432` |
| ollama.service | active (systemd) | `:11434` |
| chat UI | **process**（非 systemd unit） | `serve_chat_ui.py` → `127.0.0.1:8090` |
| advisor | **process** | `serve_advisor_openai.py --model qwen3:8b` → `:8399` |
| admin | **process** | `serve_admin_console.py` → `:8500` |
| probability | **process** | `serve_probability_ui.py` → `:8600` |
| augur-chat／advisor／admin／qdrant／probability **systemd units** | **not-found** | 目前靠手動／腳本起 process，非 unit |

## 專案佈局（現行）
- 正典 monorepo：**`/home/hugo/project/augur`**（含 `src/augur`、`constitution/`、`tools/`、`.env` 存在）
- 舊路徑 `/home/giga/augur/...` **已不存在**（勿再當根）
- MCP 慣例：constitution／local-llm（此機小模型；MCP 側常釘 `qwen3:4b`）／project-memory（`nomic-embed-text`）
- 最佳化計畫：`ops/machines/packs/DESKTOP-8MQPFS8/OPTIMIZATION-PLAN.md`

## 已知限制
- **sudo 需密碼**（`sudo -n` 失敗）→ 無法無密碼做 `pg_lsclusters` 以外之 postgres peer 管理／部分系統改動
- OS 使用者 `hugo`：**無** PostgreSQL peer role（`role "hugo" does not exist`）；連庫須經 `.env`／專用 role（本檔不記 secrets）
- `hugo` **不在** `ollama` 群組（群組目前僅 `giga`）；ollama.service Environment PATH 仍殘留 `/home/giga/...`（服務仍正常）
- **qdrant**：無 systemd unit、本探測無監聽（未跑）
- GPU VRAM 僅 4GB：勿載 `qwen3-coder-next`／`30b`；`qwen3:8b` 已在用但偏緊（advisor 現跑 8b）
- `ops/collect_machine_info.sh` 若在 sandbox 跑會假報 NVML blocked／systemd offline／PG down——蒐集須完整權限

## 勿做
- 勿用超大本地模型（VRAM 不夠）
- 勿把 GB10／舊 giga 路徑當此機 monorepo 根
- 勿在本檔寫入 `.env`／密碼／token
- 勿因「可預測」解凍 FinMind／FRED（取數仍凍）
<!-- NOTES:END -->

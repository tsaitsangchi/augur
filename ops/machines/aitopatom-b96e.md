# 機器基礎資訊：`aitopatom-b96e`

> **性質**：本機實測快照 **[I]**（自動產生，勿手改；手動註記請寫檔尾 NOTES 區塊）。
> **產生工具**：`ops/collect_machine_info.sh` ｜ **產生時間**：2026-07-22 07:55 CST
> 跨機共享說明（專案相依、治理差異）見 [README.md](README.md)。

## 摘要

| 面向 | 值 |
|---|---|
| 主機名 | `aitopatom-b96e` |
| 平台 | WSL：no ｜ 架構：aarch64 |
| OS / 核心 | Ubuntu 24.04.4 LTS ／ `6.17.0-1026-nvidia` |
| systemd | starting
offline |
| CPU | Cortex-X925
Cortex-A725（n/a 核 / 20 緒） |
| 記憶體 | 121.6 GiB（swap 16.0 GiB） |
| 系統碟 `/` | 3.6T total, 3.3T avail (6% used) |
| GPU | NVIDIA GB10, 580.159.03, [N/A], 12.1 |
| GPU 直通 `/dev/dxg` | 不存在 |
| CUDA `nvcc` | 13.0, V13.0.88 |
| PostgreSQL | (未安裝)（n/a） |

## 工具鏈

| 工具 | 版本 |
|---|---|
| git | 2.43.0 |
| gh | 2.96.0 (2026-07-02) |
| python3 | 3.12.3 |
| node | (未安裝) |
| npm | (未安裝) |
| gcc | 13.3.0-6ubuntu2~24.04.1) 13.3.0 |
| make | 4.3 |
| cmake | 3.28.3 |
| nvcc | 13.0, V13.0.88 |
| psql | (未安裝) |
| docker | 29.2.1, build a5c7197 |
| ollama | 0.32.1 |

## 手動註記

<!-- NOTES:START -->
- **角色**：**T1 進行中**——治理 + 本地推論 + **本機 PG／qdrant／應用碼**；資料還原待 DESKTOP dump。
- **對立資料層機**：`PC002-S1800`（WSL2 · i5-10500 · 無獨顯 · 有 PG 活庫）與 `DESKTOP-8MQPFS8`（WSL2 · Ryzen · GTX1650）——**兩台不同實體機，勿混為一名**。
- **此機專用設定包**：`ops/machines/packs/aitopatom-b96e/`。
- **repo 根**：`/home/giga/augur`＝public monorepo。
- **服務（2026-07-22）**：ollama ✅；qdrant ✅（native `~/qdrant` v1.18.3 :6333）；PostgreSQL ✅（micromamba `augur-pg` userspace :5432，pgvector 0.8.1；資料目錄 `/home/giga/augur-data/postgres`）。**開機常駐**：`systemctl --user` `augur-postgres`／`augur-qdrant`（linger；範本 `ops/phase2/systemd/`）；手動 fallback：`pg_userspace.sh`／`qdrant_userspace.sh`。docker 需 sudo 密碼→未用容器 PG。
- **應用**：`venv/` 已 `pip install -e .`；`import augur` OK；庫已還原（見 smoke 紀錄）。
- **dump／還原**：見 `ops/phase2/SMOKE-aitopatom-b96e-20260722.md`。
- **建議 OLLAMA_MODEL（MCP）**：`qwen3-coder-next`（`OLLAMA_NUM_CTX=32768`）。產品 UI 另用 `qwen3:30b-a3b`。
<!-- NOTES:END -->

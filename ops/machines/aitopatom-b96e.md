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
- **角色**：**T1 全執行節點目標**（治理 + 本地推論／語意記憶 + 本機 PG／qdrant／應用）；對立機 `DESKTOP-8MQPFS8` 設定不可混用。
- **此機專用設定包**：`ops/machines/packs/aitopatom-b96e/`（`setup_check.sh`／`recommended.env`／CHECKLIST）。
- **repo 根（終態）**：`/home/giga/augur`＝public monorepo（應用+治權）；勿使用 `/home/giga/augur/augur-constitution`。
- **過渡**：合倉完成前工作樹可能暫在 `/home/giga/augur-code-work`（`migrate/monorepo-learning`）。
- **建議 OLLAMA_MODEL**：`qwen3:30b-a3b`（`tools/local_llm_mcp/tools.py` 依 hostname 預設；可被 env 覆寫）。
- **路徑契約**：`PROJECT_ROOT`／`AUGUR_ROOT`＝repo 根；`install_services.sh` 不再寫死 `$HOME/project/augur`。
- **缺口**：PostgreSQL、qdrant 未起 → 全棧「真跑」未就緒（見 T1 手冊）。
- **探測**：`python3 ops/phase2/operability_probe.py`
<!-- NOTES:END -->

# 機器基礎資訊：`DESKTOP-8MQPFS8`

> **性質**：本機實測快照 **[I]**（自動產生，勿手改；手動註記請寫檔尾 NOTES 區塊）。
> **產生工具**：`ops/collect_machine_info.sh` ｜ **產生時間**：2026-07-21 21:17 CST
> 跨機共享說明（專案相依、治理差異）見 [README.md](README.md)。

## 摘要

| 面向 | 值 |
|---|---|
| 主機名 | `DESKTOP-8MQPFS8` |
| 平台 | WSL：yes (WSL2) ｜ 架構：x86_64 |
| OS / 核心 | Ubuntu 24.04.4 LTS ／ `6.18.33.2-microsoft-standard-WSL2` |
| systemd | running |
| CPU | AMD Ryzen 5 3600 6-Core Processor（6 核 / 12 緒） |
| 記憶體 | 15.6 GiB（swap 4.0 GiB） |
| 系統碟 `/` | 1007G total, 678G avail (30% used) |
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
| cmake | (未安裝) |
| nvcc | 12.0, V12.0.140 |
| psql | 17.10 (Ubuntu 17.10-1.pgdg24.04+1) |
| docker | (未安裝) |
| ollama | (未安裝) |

## 手動註記

<!-- NOTES:START -->
- **角色**：開發／驗證 + 資料層（WSL2）；現行 `ENVIRONMENT-SPEC.md` 主要描述此機。
- **對立機**：`aitopatom-b96e`（原生 Linux · aarch64 · GB10 · 有 ollama）——兩機設定不可混用。
- **建議 OLLAMA_MODEL**（若裝 ollama）：`qwen3:4b`（4GB VRAM；已由 `tools/run_local_llm_mcp.sh` 依 hostname 預設）。
- **有**：PostgreSQL 17.x online；**無**（2026-07-21 快照）：ollama。
- **注意**：VRAM 4GB → 不可假定可跑 GB10 上之 30B 級模型。
<!-- NOTES:END -->

# 機器基礎資訊：`<hostname>`（範本）

> 一般情況請**直接執行** `ops/collect_machine_info.sh` 自動產生本機檔，不需手抄本範本。
> 本範本僅供參照結構，或供無法執行腳本之機器手動填寫。

> **性質**：本機實測快照 **[I]**。
> **產生時間**：YYYY-MM-DD HH:MM TZ

## 摘要

| 面向 | 值 |
|---|---|
| 主機名 | `<hostname>` |
| 平台 | WSL：yes/no ｜ 架構：x86_64 / aarch64 |
| OS / 核心 | <發行版> ／ `<uname -r>` |
| systemd | running / offline |
| CPU | <型號>（N 核 / M 緒） |
| 記憶體 | <GiB>（swap <GiB>） |
| 系統碟 `/` | <total> total, <avail> avail |
| GPU | <名稱, driver, VRAM, compute_cap> 或「無」 |
| GPU 直通 `/dev/dxg` | 存在 / 不存在 / n/a |
| CUDA `nvcc` | <版本> 或 (未安裝) |
| PostgreSQL | <版本>（<叢集/port/狀態>） |

## 工具鏈

| 工具 | 版本 |
|---|---|
| git | |
| gh | |
| python3 | |
| node | |
| npm | |
| gcc | |
| make | |
| cmake | |
| nvcc | |
| psql | |
| docker | |
| ollama | |

## 手動註記

<!-- NOTES:START -->
（此機專責之角色、特殊設定、已知問題等。重跑腳本會保留本區塊。）
<!-- NOTES:END -->

# Augur 部署環境規格盤點（Environment Specification）

* **盤點日期**：2026-07-18（前版：2026-07-16 之 GB10 盤點，已 superseded——該機實測不可達，Steward 裁示基建落於本機、aarch64 約束作廢；歸檔見 [ENVIRONMENT-SPEC-GB10-20260716-superseded.md](ENVIRONMENT-SPEC-GB10-20260716-superseded.md)）
* **性質**：時點快照 [I]，不具規範力；AUGUR-L7 L7.50 現行登錄值 [I] 與本檔同步（2026-07-18 patch 級登錄變更）
* **數字紀律**：本檔全部數值為本機實測（指令附列），非轉抄

---

## 一、硬體規格（實測：`lscpu`／`free -h`／`df -h`）

| 項目 | 規格 |
|---|---|
| **平台** | WSL2 on Windows host（主機名 DESKTOP-8MQPFS8） |
| **架構** | **x86_64（AMD64）** |
| **CPU** | AMD Ryzen 5 3600（6 核 12 緒） |
| **記憶體** | 15 GiB＋swap 4 GiB |
| **儲存** | 1007 GB（vhdx 虛擬磁碟；2026-07-18 快照可用約 645 GB） |
| **GPU** | **NVIDIA GeForce GTX 1650 4GB VRAM**（WSL2 半虛擬化 `/dev/dxg`；driver 560.94、CUDA 12.6 runtime；`nvidia-smi` 位於 `/usr/lib/wsl/lib/`——**前版「無」係僅查 PATH 之量測錯誤，經 Steward 質疑更正**） |

## 二、作業系統（實測：`uname -r`／`lsb_release`）

| 項目 | 版本 |
|---|---|
| OS | Ubuntu 24.04.4 LTS (Noble) |
| 核心 | 6.18.33.2-microsoft-standard-WSL2 |

## 三、資料層（實測：`psql`）

| 項目 | 值 |
|---|---|
| PostgreSQL | 17.9（apt pgdg；資料目錄 `/var/lib/postgresql/17/main`） |
| pgvector | 0.8.4 |
| 生產庫 `augur` | **55 GB**、250 表（含十張憲章表） |
| 沙盒庫 `augur_sandbox` | 55 GB 同構複本（常設驗證閘） |
| 角色 | augur（現行應用）、augur_predict（隔離）、stock、**augur_owner／augur_app**（2026-07-18 Phase 1 新設） |

## 四、軟體與服務（實測）

| 軟體 | 版本／狀態 |
|---|---|
| Python | 3.12.3（應用 venv 於 `/home/hugo/project/augur/venv`） |
| git | 2.43.0；gh CLI 已授權 tsaitsangchi |
| qdrant | 1.18.2（127.0.0.1:6333，運行中） |
| ollama | 運行中（127.0.0.1:11434；模型 qwen3:4b、qwen3:8b；**GPU 加速實證**：qwen3:4b 載入 2.3GB/3.2GB 進 VRAM 部分卸載） |
| Docker | 未安裝 |
| systemd 服務 | 無 augur 相關單位；四個 serving 進程（advisor／admin_console／chat_ui／probability_ui）以腳本方式常駐於 **`/home/hugo/project/augur`**（hugo 使用者） |

## 五、程式碼副本佈局（重要——雙副本現實）

| 路徑 | 使用者 | 角色 |
|---|---|---|
| `/home/hugo/project/augur` | hugo | **活服務運行處**（venv、serving 進程、其自有 .env） |
| `/home/giga/augur/augur-code` | giga | 工作副本（.env 含 DB 憑證與 GITHUB_TOKEN，gitignored） |
| `/home/giga/augur/augur-constitution` | giga | 憲章倉（本檔所在） |

## 六、L7.25 備份現況（首份「經實測」證據）

| 項目 | 值 |
|---|---|
| 首次全庫備份 | 2026-07-18 `augur_pre_phase1_20260718_0928.dump`（pg_dump -Fc，10.04 GB，11 分鐘） |
| 還原實測 | 同日至臨時庫 `augur_restore_test` 演練（Phase 1 施工前置；紀錄見 ops/phase1/） |
| **異碟副本（2026-07-18 建立）** | restic 0.19.1（官方 binary、SHA256 驗證）；庫＝`D:\augur_restic`（異實體碟）；首備 snapshot `cbb73c19`＝9.35GiB dump（3 分 51 秒）；**`restic check --read-data-subset=5%` 零錯誤**（經實測）；密碼檔 chmod 600 不入 git |
| **殘餘缺口（誠實）** | 異碟≠異機——機器全損（火災／竊失）仍單點；**異機／雲端第二目的地待 Steward 給定**（restic 原生支援 S3／B2／sftp，一條指令加掛）；RPO／RTO 與演練節奏待核定（建議 RPO 24h＋季度還原演練） |

## 七、與 L7 草案之關係

AUGUR-L7 v0.1-draft 之 L7.50 現行登錄值已與本檔對齊（x86_64／WSL2／GTX 1650 4GB／CUDA 12.6）。**T-L7-6 張力照舊適用**：目標架構之選型約束對任何架構同型，且本機 GPU 僅 4GB VRAM 使「模型規模 vs 載體可得性」為現實約束（>4GB 模型部分卸載、大模型不可行）——載體不可得者依 L7.50(c) 改選或 OPEN，不得放寬角色語義。

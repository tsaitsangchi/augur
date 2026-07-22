> ⚠️ **SUPERSEDED（2026-07-18）**：本盤點描述之 GIGABYTE AI TOP ATOM（GB10／aarch64）經實測不可達（10.10.130.46 unreachable），且 Steward 已裁示「基建落於本機 WSL2、aarch64 約束全部作廢」。**本檔僅存為稽核軌跡，不得引為現況**；現行權威盤點見 [ENVIRONMENT-SPEC.md](ENVIRONMENT-SPEC.md)。

# Augur 部署環境規格盤點（Environment Specification）

* **盤點日期**：2026-07-16
* **性質**：時點快照（point-in-time snapshot），屬 Layer 7（Infrastructure）之資訊性文件 [I]
* **用途**：後續系統展開與最佳化規劃之基礎資料
* **憲章對應**：本文件不具規範力；Layer 7 規格撰寫時應引用本文件並更新盤點

---

## 一、硬體規格

| 項目 | 規格 |
|---|---|
| **機型** | GIGABYTE AI TOP ATOM（NVIDIA GB10 Grace Blackwell 平台，DGX Spark 同級） |
| **主機名稱** | aitopatom-b96e |
| **SoC / GPU** | NVIDIA GB10（Grace Blackwell Superchip），compute capability 12.1 |
| **CPU** | 20 核 ARM（10× Cortex-X925 效能核 + 10× Cortex-A725 效率核），單插槽，L3 快取 24 MiB × 2 |
| **架構** | aarch64（ARM64）— 套件選型須注意 ARM 相容性 |
| **記憶體** | 121 GiB（**CPU/GPU 統一記憶體架構**，nvidia-smi 不分列 VRAM），swap 15 GiB |
| **儲存** | NVMe SSD 3.6 TB（ESL04TBTLCZ），已用 38 GB / 可用 3.4 TB |
| **GPU 功耗狀態** | 閒置約 8W，溫度 32°C（盤點時） |

## 二、作業系統與驅動

| 項目 | 版本 |
|---|---|
| OS | Ubuntu 24.04.4 LTS (Noble)，NVIDIA 客製核心 6.17.0-1026-nvidia |
| NVIDIA Driver | 580.159.03 |
| CUDA | 13.0（driver 層）+ CUDA Toolkit 13.0.88（nvcc 已安裝） |

## 三、軟體環境現況

**已安裝：**

| 軟體 | 版本 | 備註 |
|---|---|---|
| Python | 3.12.3 | 系統層；pip 24.0 |
| Docker | 29.2.1 | **服務運行中**，目前無容器與映像（乾淨狀態） |
| git | 2.43.0 | |
| gh CLI | 2.96.0 | 位於 `~/.local/bin/gh`（不在預設 PATH），已授權 tsaitsangchi 帳號 |

**未安裝（Augur 架構角色的候選缺口）：**

| 憲章架構角色（§5） | 現況 | 備註 |
|---|---|---|
| System of Record | ❌ 無 PostgreSQL/任何 RDBMS | augur-code 依賴 PostgreSQL（import_database.sh） |
| Relationship Representation | ❌ 無圖資料庫 | |
| Semantic Memory | ❌ 無向量資料庫 | |
| ML 框架 | ❌ 系統層無 PyTorch | ARM64 + CUDA 13 需用 NVIDIA 官方 wheel/NGC 容器 |
| Node.js | ❌ 未安裝 | |

## 四、網路

| 介面 | IP | 備註 |
|---|---|---|
| enP7s7（乙太網路） | **10.10.130.46/24** | 本機即先前連通測試之目標 |
| wlP9s9（Wi-Fi） | 10.10.114.18/24 | |
| docker0 | 172.17.0.1/16 | 橋接待用 |

監聽服務：SSH(22)、DNS(53)、CUPS(631)、遠端桌面 xrdp/gnome-remote-desktop(3350/3389/3390)、本機開發工具(11000、37337 language_server)。

## 五、對 Augur 系統展開的規劃意涵

1. **統一記憶體是最大資產**：121 GiB CPU/GPU 共用記憶體，適合在本機跑中大型量化 LLM 推論（Cognitive Kernel 的本地候選）、向量嵌入與資料庫工作負載並存，無傳統 VRAM 瓶頸。
2. **ARM64 是選型約束**：所有資料庫、ML 框架、容器映像必須確認 aarch64 支援。建議優先採 Docker 部署（官方多架構映像：postgres、neo4j、qdrant/weaviate 均有 arm64 版），ML 用 NVIDIA NGC 的 ARM 容器。
3. **儲存充裕**：3.4 TB 可用，足以承載台股全史資料 + 知識庫 + 向量索引 + 模型權重，短中期無需外接儲存。
4. **資料庫全數缺位**：augur-code（既有系統）需要 PostgreSQL；憲章 §5 三個資料角色（record/relationship/semantic）目前皆無實體。系統展開的第一批基礎建設即在此 — 建議以 docker compose 一次定義，納入 Layer 7 規格。
5. **單機非高可用**：目前為單節點，無備援。依憲章 P4（Evidence 不可滅失），資料備份策略應成為 Layer 7 規格的必備章節（如：NVMe 本機 + 異地 git/物件儲存）。
6. **本機閒置資源大**：CPU/GPU 幾乎閒置、記憶體用量 4 GB，目前所有 AI 工作（含本次多代理工作流程）皆為雲端 API — 本機算力是尚未動用的最佳化空間。

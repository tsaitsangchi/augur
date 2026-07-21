# Phase 2 可運作探測證據紀錄 — 2026-07-21（GB10 aitopatom-b96e）

* **性質**：[I] 資訊性證據紀錄，不創設義務、不具規範力。權威悉依《Augur Meta-Constitution》及各層生效規格之 [N] 條款。
* **對照**：`LAYER-SEALING-SCHEDULE.md` 第二階段「可運作探測」工項。
* **方法紀律**：承本專案「不採信自陳、對抗審查方為關卡」（`LAYER-SEALING-SCHEDULE.md` 鐵律 12/12）——本紀錄之狀態**皆由實地連線/查詢取證**，非讀設定檔宣稱值。
* **產生指令（可重現）**：`python3 ops/phase2/operability_probe.py`（純 stdlib、唯讀）。

---

## 一、實測證據（2026-07-21，逐項取證）

| 項目 | 狀態 | 證據（實測輸出） |
|---|---|---|
| ollama (11434) | ✅ UP | 模型 3：`nomic-embed-text`、`qwen3:30b-a3b`、`qwen3-coder-next`；無常駐載入 |
| GPU / VRAM | ✅ UP | `NVIDIA GB10`（統一記憶體，`nvidia-smi` memory 欄 N/A，非缺陷） |
| 記憶體 / 磁碟 | ℹ INFO | MemTotal=122 GiB；`/` 總 3936 GB、可用 3541 GB |
| qdrant (6333) | ❌ ABSENT | `Connection refused`（本機無此服務） |
| PostgreSQL (5432 標準) | ❌ ABSENT | `Connection refused` |
| PostgreSQL (55432 userspace) | ❌ ABSENT | `Connection refused` |
| augur 應用碼 | ❌ ABSENT | 候選路徑皆不存在：`/home/giga/augur/augur-code`、`~/project/augur`、`/home/hugo/project/augur` |

**小結：2/7 服務就緒**（ollama + GPU）。qdrant / PostgreSQL / augur 應用碼**全不在本機**。

> 應用層探測（`entity_registry`(3,491)、advisor/core_gate 短連線、審議引擎一輪）**未執行**——因其前置（augur 應用碼 + DB 驅動 + PG/qdrant）於本機不存在。**「未執行」≠「已驗證通過」**（承本專案 Annex TR 教訓）。

---

## 二、與 `infrastructure/ENVIRONMENT-SPEC.md`（2026-07-18）之落差

`ENVIRONMENT-SPEC.md` 現行版描述之機器與本機**為不同實體**：

| 維度 | 本機實測（GB10, 2026-07-21） | ENVIRONMENT-SPEC 宣稱 | 判定 |
|---|---|---|---|
| 平台/架構 | GB10 Grace-Blackwell / ARM **aarch64** | WSL2 on Windows / **x86_64** | 🔴 不同機 |
| 主機名 | `aitopatom-b96e` | `DESKTOP-8MQPFS8` | 🔴 不同機 |
| 記憶體 | **122 GiB** 統一記憶體 | 15 GiB | 🔴 |
| GPU | **NVIDIA GB10**（統一記憶體） | GTX 1650 4GB VRAM | 🔴 |
| PostgreSQL | **ABSENT** | 17.9、augur 庫 55GB/250 表 | 🔴 本機無 |
| qdrant | **ABSENT** | 1.18.2 運行中 | 🔴 本機無 |
| 應用碼 | **ABSENT** | `/home/hugo/project/augur` 活服務 | 🔴 本機無 |
| ollama | UP（qwen3:30b-a3b 等） | 運行中（qwen3:4b/8b） | ⚠ 在，模型不同 |

**且 `ENVIRONMENT-SPEC.md` 將 GB10 標為「該機實測不可達」**——而本紀錄係**在一台可達的 GB10 上**產生。此為 self-report ≠ reality 之實例，正是 Phase 2 應以探測拆穿者。

---

## 三、Phase 2 判定（本機）

* **本機目前之「可運作」= 治理 + 本地推論/記憶節點**：`constitution-mcp` / `local-llm-mcp` / `project-memory-mcp` 三支 MCP 已掛載並實測通過（見 `reports/PROJECT-MEMORY-MCP-PLAN.md`、對話紀錄）；ollama + GPU + 巨量記憶體到位。
* **應用層（L5–7 真跑）於本機不成立**：DB、向量庫、應用碼皆不在。此非缺陷、而是**現實狀態之據實揭露**。

---

## 四、呈 Steward 待決（Agent 不得擅專）

1. **GB10 節點定位**：全執行節點（搬應用來跑）／治理+推論節點（應用留原機）／先查清應用現落何機。
2. **`ENVIRONMENT-SPEC.md` 訂正**：現行版描述錯機器且綁 **L7.50 登錄值**，訂正屬 §8.6 patch 級登錄變更——**須 Steward 裁**。第五節備訂正建議草案（不生效力）。
3. **應用現址查核**：`ENVIRONMENT-SPEC` 所載 `/home/hugo/project/augur`（WSL2 機）是否仍活、augur 庫是否仍在，須於該機另跑本探測腳本方能取證。

---

## 五、ENVIRONMENT-SPEC 訂正建議（草案，呈 Steward，**不生效力**）

> 下列為本機實測值之整理，供 Steward 依 `ENVIRONMENT-SPEC.md` 之「數字紀律」複核後決定是否採認為新登錄。**Agent 不得自行寫入 live 檔。** 每值附產生指令。

* 平台：NVIDIA GB10 Grace-Blackwell（DGX Spark 同級）；主機 `aitopatom-b96e`（`hostname`）
* 架構：ARM aarch64（`uname -m`）— 套件選型須確認 ARM 支援
* CPU：20 核（10× Cortex-X925 + 10× Cortex-A725）（`/proc/cpuinfo`）
* 記憶體：122 GiB 統一記憶體 + 15 GiB swap（`free -h`／`/proc/meminfo`）
* 儲存：NVMe，`/` 總 ~3936 GB、可用 ~3541 GB（`df -h /`）
* GPU：NVIDIA GB10，統一記憶體（`nvidia-smi` 不分列 VRAM）；driver 580.159.03、CUDA 13.0（`nvidia-smi`）
* ollama：127.0.0.1:11434，systemd user 服務 + linger 常駐；模型 `qwen3:30b-a3b`、`qwen3-coder-next`、`nomic-embed-text`（`ollama list`）
* PostgreSQL / qdrant / augur 應用碼：**本機無**（`operability_probe.py`）
* 三支 MCP：`constitution` / `local-llm` / `project-memory` 已掛載（`.cursor/mcp.json`）

---

*本文件為 [I] 證據紀錄。訂正 `ENVIRONMENT-SPEC.md`／L7.50 登錄值及 GB10 節點定位，均為 Steward 治理事項。*

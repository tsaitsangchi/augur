# Phase 2 可運作探測證據紀錄 — 2026-07-21（GB10 aitopatom-b96e）

* **性質**：[I] 資訊性證據紀錄，不創設義務、不具規範力。權威悉依《Augur Meta-Constitution》及各層生效規格之 [N] 條款。
* **對照**：`LAYER-SEALING-SCHEDULE.md` 第二階段「可運作探測」工項。
* **方法紀律**：承本專案「不採信自陳、對抗審查方為關卡」（`LAYER-SEALING-SCHEDULE.md` 鐵律 12/12）——本紀錄之狀態**皆由實地連線/查詢取證**，非讀設定檔宣稱值。
* **產生指令（可重現）**：`python3 ops/phase2/operability_probe.py`（純 stdlib、唯讀）。

---

## 〇、更正（2026-07-21 後續 `find` 實測）

**本報告初版稱「augur 應用碼 ABSENT」係誤——探測腳本之候選路徑清單不完整所致。** 後續 `find /home ...` 實測證實**應用碼就在本機**：

* `/home/giga/augur-code-work/`（工作副本；`src/augur` ＋ `scripts/` 內含 `advisor_distill_*`、`*deliberation*`、`run_daily_deliberation.py` 等）
* `/home/giga/augur-archive/augur-code-latest/src/augur`（封存最新）
* `/home/giga/augur/ref_augur/augur`（舊參考 clone，已 gitignore）

**修正結論**：本機**有** augur 應用碼（主用 `/home/giga/augur-code-work`），惟 **PostgreSQL / qdrant 服務仍未起**。故本機「真跑」之缺口為**服務層（DB＋向量庫）＋資料還原**，非「碼不在」。腳本候選路徑已補齊（`augur-code-work`／`augur-archive`）。下表 [ABSENT] 之 augur 應用碼一列，以本節為準更正。

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
| augur 應用碼 | ✅ PRESENT（見〇節更正） | 初版腳本候選清單漏 `augur-code-work`；`find` 實測在 `/home/giga/augur-code-work`（＋archive／ref_augur） |

**小結（更正後）**：ollama + GPU + **應用碼**在本機；**qdrant / PostgreSQL 未起**。本機「真跑」缺口＝**服務層（DB＋向量庫）＋資料還原**，非「碼不在」。

> 應用層探測（`entity_registry`(3,491)、advisor/core_gate 短連線、審議引擎一輪）**仍未執行**——因其前置之 **PG/qdrant 服務未起**、DB 驅動與資料尚未就緒。**「未執行」≠「已驗證通過」**（承本專案 Annex TR 教訓）。

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
| 應用碼 | **PRESENT**（`/home/giga/augur-code-work`；見〇節） | `/home/hugo/project/augur` 活服務 | ⚠ 碼在本機、但位置與 spec 不同且服務未起 |
| ollama | UP（qwen3:30b-a3b 等） | 運行中（qwen3:4b/8b） | ⚠ 在，模型不同 |

**且 `ENVIRONMENT-SPEC.md` 將 GB10 標為「該機實測不可達」**——而本紀錄係**在一台可達的 GB10 上**產生。此為 self-report ≠ reality 之實例，正是 Phase 2 應以探測拆穿者。

---

## 三、Phase 2 判定（本機）

* **本機已就緒者**：三支 MCP（`constitution` / `local-llm` / `project-memory`）掛載並實測通過；ollama + GPU + 巨量記憶體到位；**augur 應用碼在本機**（`/home/giga/augur-code-work`）。
* **本機「真跑」之實際缺口（更正後）**：**PostgreSQL 未起、qdrant 未起、augur DB 資料未還原**。碼在、機夠力，缺的是**服務層 + 資料**。此為現實狀態之據實揭露。
* **下一步取證**（未執行）：`AUGUR_CODE=/home/giga/augur-code-work python3 ops/phase2/operability_probe.py` 可列應用碼標記；起 PG/qdrant + 還原 DB 後，方能實跑 advisor/審議引擎一輪。

---

## 四、呈 Steward 待決（Agent 不得擅專）

1. **GB10 節點定位**：碼既已在本機（`augur-code-work`），是否要在本機**起 PG/qdrant + 還原 augur DB** 使其成全執行節點？抑或本機僅治理+推論、應用真跑仍留他機？
2. **`ENVIRONMENT-SPEC.md` 訂正**：現行版描述錯機器且綁 **L7.50 登錄值**，訂正屬 §8.6 patch 級登錄變更——**須 Steward 裁**。第五節備訂正建議草案（不生效力）。
3. **正典副本認定**：本機存在**多份**應用碼——`/home/giga/augur-code-work`（工作副本）、`/home/giga/augur-archive/augur-code-latest`（封存）、`/home/giga/augur/ref_augur/augur`（舊參考，gitignore）。何者為權威工作副本、他機（hugo WSL2）是否另有活服務，須認定以免雙副本漂移（承 `ENVIRONMENT-SPEC` §五「雙副本現實」教訓）。

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
* PostgreSQL / qdrant：**服務未起**（`operability_probe.py`）
* augur 應用碼：**在本機**（`/home/giga/augur-code-work`；另有 archive／ref_augur）——正典副本待認定
* 三支 MCP：`constitution` / `local-llm` / `project-memory` 已掛載（`.cursor/mcp.json`）

---

*本文件為 [I] 證據紀錄。訂正 `ENVIRONMENT-SPEC.md`／L7.50 登錄值及 GB10 節點定位，均為 Steward 治理事項。*

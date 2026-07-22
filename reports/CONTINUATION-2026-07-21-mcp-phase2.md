# 專案接續紀錄（Continuation Note）— 2026-07-21｜MCP 輔助層 + Phase 2 探測

* **性質**：[I] 資訊性接續快照，不創設義務、不具規範力。權威悉依《Augur Meta-Constitution》及各層生效規格之 [N] 條款。
* **產生機**：GB10 `aitopatom-b96e`（giga）｜**用途**：換另一台電腦接續本專案時，先讀本檔取得會期脈絡。
* **正典入口仍為**：`HANDOFF.md`（治理總覽）、`LAYER-SEALING-SCHEDULE.md`（蓋章/階段排程）。本檔只補「本會期新增之輔助層與 Phase 2 探測」。
* **兩機區分（必讀）**：本專案在**兩台不同軟硬體**並行——詳 [`ops/machines/README.md`](../ops/machines/README.md)。接續前先確認自己在哪一台（`hostname`），勿套用他機路徑／模型／服務假設。
* **此機專用設定包（GB10）**：[`ops/machines/packs/aitopatom-b96e/`](../ops/machines/packs/aitopatom-b96e/)——先跑 `./ops/machines/packs/aitopatom-b96e/setup_check.sh`（錯誤主機會拒絕）。

| 主機 | 角色 | 架構 | 關鍵差異 | 設定包 |
|---|---|---|---|---|
| `aitopatom-b96e` | 治理 + 本地推論／記憶 | aarch64 · GB10 · 122GiB | ollama ✅ · PG ❌ | [packs/aitopatom-b96e](../ops/machines/packs/aitopatom-b96e/) |
| `DESKTOP-8MQPFS8` | 開發／驗證 + 資料層 | x86_64 · WSL2 · GTX1650 | PG ✅ · ollama ❌（當時） | [packs/DESKTOP-8MQPFS8](../ops/machines/packs/DESKTOP-8MQPFS8/) |

---

## 一、本會期完成（2026-07-21）

1. **三支 MCP 全部上線並實測**（`.cursor/mcp.json` 註冊，隨 repo 走）：
   * `constitution`：治理條款**精確原文**（get_clause / get_spec_clause / search_clauses …）。
   * `local-llm`：本地小模型「大進小出」濃縮（local_summarize / local_extract / local_ask）。
   * `project-memory`：全 repo **非治理輔助語料**語意記憶（recall / memory_status）。
2. **治理硬邊界（非治理輔助專用）**：`local-llm` 與 `project-memory` 一律**不碰治理權威語料**（`constitution/`、生效 `specs/*-SPECIFICATION.md`、`RULING-*`、`AMENDMENT-LOG.md`），查詢導回 `constitution-mcp`。對齊元憲章 **P2.E2**(`:221`)／**P2.E4**(`:223`)／**P2.Y**(`:205`)。selftest 逐項斷言。
3. **project-memory-mcp 實作要點**：純 stdlib、**讀寫分離**（server 唯讀、`index.py` 為唯一寫入端、AST 掃描鎖）、治理排除、失敗發聲、陳舊發聲、通用 venv 偵測（`pyvenv.cfg`）。實測索引 **104 檔 / 1759 chunk**（`.venv-mcp` 等雜訊已排除）。
4. **Phase 2 可運作探測**：`ops/phase2/operability_probe.py`（純 stdlib、唯讀、探測而非自陳）＋證據紀錄 `ops/phase2/OPERABILITY-PROBE-2026-07-21.md`。

**git 座標**（`origin/main`，`github.com/tsaitsangchi/augur-constitution`）：
* commit `9e1577f`：project-memory-mcp + 治理邊界。
* commit `d754938`：索引範圍收斂 + 進度輸出。
* Phase 2 探測工具與證據：**本次隨本檔一併提交**。
* 封存 tag：`archive-20260721-aux-mcp-seal`、`archive-20260721-project-memory-verified`（＋本次新封存點）。

---

## 二、目前平台真實狀態（GB10 探測證據，2026-07-21）

`python3 ops/phase2/operability_probe.py` 實測：**2/7 就緒**。

* ✅ **ollama** 11434（`qwen3:30b-a3b`、`qwen3-coder-next`、`nomic-embed-text`）、✅ **GPU** GB10、122 GiB 記憶體、3.5TB 可用。
* ✅ **augur 應用碼在本機**（`find` 實測）：`/home/giga/augur-code-work`（工作副本，含 `src/augur` + advisor/deliberation 等 scripts）、`/home/giga/augur-archive/augur-code-latest`、`/home/giga/augur/ref_augur/augur`（舊參考）。
* ❌ **qdrant / PostgreSQL(5432,55432) 服務未起**。
* **判定（更正後）**：本機已就緒＝三支 MCP + ollama + GPU + **應用碼**；「真跑」缺口＝**PG/qdrant 服務 + augur DB 資料還原**（碼在、機夠力，缺服務與資料）。
* 🔴 **關鍵**：`infrastructure/ENVIRONMENT-SPEC.md` 描述的是**另一台 WSL2/x86 機器**且把 GB10 誤標「不可達」——self-report ≠ reality。詳 `ops/phase2/OPERABILITY-PROBE-2026-07-21.md`（含〇節更正）。

> **正典副本待認定**：本機有多份應用碼（work / archive / ref_augur），何者權威、hugo WSL2 機是否另有活服務，須認定以免雙副本漂移。

---

## 三、呈 Steward 待決（Agent 不得擅專）

1. **GB10 節點定位**：碼既在本機，是否在本機**起 PG/qdrant + 還原 augur DB** 使其成全執行節點？抑或僅治理+推論、應用真跑留他機？
2. **`ENVIRONMENT-SPEC.md` 訂正**（綁 **L7.50**，§8.6 patch 級）：訂正草案已備於 `OPERABILITY-PROBE-2026-07-21.md` 第五節（不生效力）。
3. **正典副本認定**：`augur-code-work` / `augur-archive` / `ref_augur` 三份中何者為權威工作副本；hugo WSL2 機是否另有活服務（另跑 `operability_probe.py` 取證），以免雙副本漂移。

---

## 四、換另一台電腦接續：逐步清單

1. **取碼**：`git clone https://github.com/tsaitsangchi/augur-constitution.git` → `cd` 進去 → `git fetch --tags`。
2. **讀脈絡**：本檔 → `HANDOFF.md` → `LAYER-SEALING-SCHEDULE.md`。
3. **本地推論**（若要用 local-llm / project-memory）：
   * 裝 ollama（注意目標機架構；GB10 為 aarch64）。
   * `ollama pull qwen3:30b-a3b && ollama pull nomic-embed-text`。
   * 常駐：systemd user 服務 + `loginctl enable-linger`（作法見 `reports/LOCAL-LLM-MCP-OPTIMIZATION-PLAN.md` §八）。
4. **重建語意索引**（索引為衍生物、**不入 git**）：`python3 -m tools.project_memory_mcp index`。
5. **掛 MCP**：確認 `.cursor/mcp.json` 三支指向 `tools/run_*.sh`（可攜、依 hostname 選模型）→ **完整重啟 Cursor** → MCP 頁見三支 ready。**勿**寫死他機 `PYTHONPATH`。
6. **驗證**：
   * `python3 -m tools.project_memory_mcp selftest` / `python3 -m tools.local_llm_mcp selftest`（stub，無須 ollama）。
   * `python3 ops/phase2/operability_probe.py`（確立該機服務/硬體/應用碼現實）。
7. **憑證**：`.env`（含 DB 憑證、`GITHUB_TOKEN`）**不在 git**（gitignored），須於新機另行備置；勿讀取/輸出（HANDOFF 紅線 #6）。

---

## 五、關鍵檔案索引

| 檔案 | 用途 |
|---|---|
| `tools/constitution_mcp/` `tools/local_llm_mcp/` `tools/project_memory_mcp/` | 三支 MCP 實作 |
| `.cursor/mcp.json` | MCP 註冊（三支） |
| `reports/LOCAL-LLM-MCP-OPTIMIZATION-PLAN.md` / `reports/PROJECT-MEMORY-MCP-PLAN.md` | 兩份設計計畫（含治理邊界、模型選型、ollama 常駐） |
| `ops/phase2/operability_probe.py` / `ops/phase2/OPERABILITY-PROBE-2026-07-21.md` | Phase 2 探測工具 + 證據 + ENVIRONMENT-SPEC 訂正草案 |
| `infrastructure/ENVIRONMENT-SPEC.md` | ⚠ 現行版描述錯機器，訂正待 Steward |

---

*本文件為 [I] 接續導覽。權威悉依《Augur Meta-Constitution》及各層生效規格之 [N] 條款；節點定位、ENVIRONMENT-SPEC/L7.50 訂正均為 Steward 治理事項。*

# 機器基礎資訊（ops/machines/）

同一 Augur 專案在**兩台不同軟硬體機器**上並行建立／運行時，各機環境資訊在此**按主機名分檔**，互不覆蓋、不可混用設定。

## 鐵律：兩機必須區分

| 規則 | 說明 |
|---|---|
| **識別鍵＝hostname** | 每台一個檔 `ops/machines/<hostname>.md`，互不覆蓋 |
| **共享 vs 本機** | 憲章／規格／工具碼經 GitHub 同步；`.env`、venv、索引 DB、機器特定路徑**不進 git** |
| **禁止硬編碼他機路徑** | MCP／腳本不得寫死 `/home/.../augur-constitution` 等僅存在於某一台的絕對路徑 |
| **模型／服務各機自立** | `OLLAMA_MODEL`、PostgreSQL、qdrant 依該機硬體與角色決定，**不可假定兩機相同** |
| **規範 vs 營運** | 規範性登錄以 `infrastructure/ENVIRONMENT-SPEC.md`（L7.50）為準；本目錄為 **[I] 營運快照**，不取代該規格 |

> 2026-07-22 實測：遠端曾把 `PYTHONPATH=/home/giga/augur/augur-constitution` 寫進共享 MCP 設定——該路徑**僅在某一佈局存在**，在 `aitopatom-b96e`（repo 根＝`/home/giga/augur`）上不存在，導致 MCP 無法啟動。已改為可攜 `python3 -m`；模型依 hostname 在 Python 內選取。**此機專用營運包**見 [`packs/aitopatom-b96e/`](packs/aitopatom-b96e/)。

---

## 機器清單（兩台）

| 主機名 | 角色（營運） | 平台 / 架構 | GPU | 記憶體 | 關鍵服務 | 快照 | **設定包** |
|---|---|---|---|---|---|---|---|
| **`aitopatom-b96e`** | **治理 + 本地推論／語意記憶** | 原生 Linux · **aarch64** | **GB10** | **122 GiB** | ollama ✅；PG ❌；qdrant ❌ | [aitopatom-b96e.md](aitopatom-b96e.md) | **[packs/aitopatom-b96e/](packs/aitopatom-b96e/)** |
| **`DESKTOP-8MQPFS8`** | **開發／驗證 + 資料層** | **WSL2** · **x86_64** | GTX 1650 4GB | ~16 GiB | PG ✅；ollama ✅（`qwen3:4b`） | [DESKTOP-8MQPFS8.md](DESKTOP-8MQPFS8.md) | [packs/DESKTOP-8MQPFS8/](packs/DESKTOP-8MQPFS8/) |

### 角色分工（據實，非願望）

```
┌─────────────────────────────┐     GitHub（共享碼／憲章／規格）     ┌──────────────────────────────┐
│  aitopatom-b96e（GB10）      │◄──────────────────────────────────►│  DESKTOP-8MQPFS8（WSL2）       │
│  aarch64 · 122GiB · GB10     │                                     │  x86_64 · 16GiB · GTX1650     │
│                              │                                     │                              │
│  ✅ constitution / local-llm  │                                     │  ✅ PostgreSQL + pgvector     │
│     / project-memory MCP     │                                     │  ✅ 開發／驗證／資料層         │
│  ✅ ollama（30b-a3b 等）      │                                     │  ✅ ollama（qwen3:4b）         │
│  ❌ PG / qdrant 未起          │                                     │  ⚠ VRAM 4GB → 僅小模型       │
└─────────────────────────────┘                                     └──────────────────────────────┘
```

**「真跑」全棧（advisor／審議引擎／entity_registry）** 需要：**應用碼 + PG +（可選）qdrant + 模型**。目前 DESKTOP 具備 PG + 小模型 MCP；GB10 具備大模型 MCP、尚無 PG。缺口與待決見 `ops/phase2/OPERABILITY-PROBE-2026-07-21.md`。

---

## 跨機比較（重點軸；詳見各機檔）

| 軸 | `aitopatom-b96e`（2026-07-22） | `DESKTOP-8MQPFS8`（2026-07-21） |
|---|---|---|
| OS / 核心 | Ubuntu 24.04.4 · `6.17.0-1026-nvidia` | Ubuntu 24.04.4 · `6.18-WSL2` |
| 架構 | **aarch64** | **x86_64** |
| CPU | Cortex-X925+A725（20 緒） | Ryzen 5 3600（6C/12T） |
| 記憶體 | **121.6 GiB** | 15.6 GiB |
| GPU / driver | **GB10** · 580.159.03 · CC 12.1 | GTX 1650 · 560.94 · 4GB · CC 7.5 |
| CUDA `nvcc` | **13.0** | 12.0 |
| PostgreSQL | **未安裝** | **17.10** online |
| ollama | **0.32.1**（qwen3:30b-a3b 等） | **0.32.1**（`qwen3:4b` + `nomic-embed-text`） |
| docker | 29.2.1 | （未安裝） |
| 建議 `OLLAMA_MODEL`（MCP） | **`qwen3-coder-next`**（UI 另用 `qwen3:30b-a3b`） | **`qwen3:4b`**（已裝；VRAM 4GB） |
| repo 根（此使用者） | `/home/giga/augur` | **`/home/giga/augur/augur-code`**（正典）；歷史 constitution → `_archived_augur-constitution_20260722` |

> **架構不同 → 二進位不可共用**：torch wheel、`nvcc -arch`、部分 PostgreSQL 擴充、原生 CUDA 測試產物，必須各機依自身架構安裝／編譯。

---

## 新增 / 更新一台機器

```bash
cd <repo 根>          # 在「該機」的一般終端執行（非 Cursor sandbox）
git pull
./ops/collect_machine_info.sh     # → ops/machines/<hostname>.md
# 編輯該檔尾 NOTES：角色、建議模型、已知問題
git add ops/machines/<hostname>.md ops/machines/README.md
git commit -m "ops(machines): 更新 <hostname> 基礎資訊"
git push
```

Sandbox 內量測會出現 GPU 被擋、systemd/PostgreSQL 誤判等假象——**以一般終端實測為準**。

---

## MCP 跨機啟動（可攜）

共享設定（`.cursor/mcp.json` / `.mcp.json`）使用 **`python3 -m tools.*`**（Cursor 以 repo 根為 cwd；**不寫死絕對 PYTHONPATH**）。

| Server | 啟動 | 本機差異如何處理 |
|---|---|---|
| constitution | `python3 -m tools.constitution_mcp` | 無 |
| local-llm | `python3 -m tools.local_llm_mcp` | **`tools.py` 依 hostname 選預設模型**（GB10→`qwen3-coder-next`；WSL2→`qwen3:4b`）；可被 `OLLAMA_MODEL` 覆寫；GB10 建議 `OLLAMA_NUM_CTX=32768` |
| project-memory | `python3 -m tools.project_memory_mcp` | `EMBED_MODEL=nomic-embed-text` |

> 曾試過 `bash tools/run_*.sh`：部分 Cursor 啟動環境 cwd 不穩導致**三支 MCP 全未掛載**（2026-07-22 實測）。故改回 `python3 -m`，機器差異改由 Python 內判定。`tools/run_*.sh` 仍保留供終端手動啟動。

覆寫方式（任一機）：啟動 Cursor 前設 `OLLAMA_MODEL=...`，或在 MCP 設定 UI 加 env。

---

## 跨機共享：專案相依與運行要點

以下為**與機器無關**的專案需求（各機皆適用）。

### public `augur` monorepo（應用 + 治權；終態唯一碼根）
- 套件：`pyproject.toml`（`name=augur`，requires-python ≥ 3.10）＋ MCP／lint：`tools/`
- 核心相依：`psycopg2-binary`、`pandas`、`polars`、`numpy`、`scikit-learn`、`xgboost`、`lightgbm`、`catboost`、`jieba`、`shap`
- 各機需備：本機 `venv` + `.env`（**已 gitignore，勿提交**）；`PROJECT_ROOT`／`AUGUR_ROOT`＝本機 clone 根
- **GB10 終態路徑**：`/home/giga/augur`（過渡：`augur-code-work` 上 `migrate/monorepo-learning` 直至步 4 收斂）
- 三支 MCP：`constitution` / `local-llm` / `project-memory`（見上表可攜啟動）
- 憲章 lint：`python3 -m tools.constitution_lint report`（於 **repo 根**執行；純 stdlib）
- 語意索引：各機自建 `.project_memory/`（gitignore；`python3 -m tools.project_memory_mcp index`）

### 歷史：獨立 `augur-constitution`（觀察期後廢止）
- 內容已併入 public `augur` 之 `constitution/`／`specs/`／`ops/`／`tools/`；勿再以雙 remote 為正典。
---

## 與治理規格之關係

規範性環境登錄以 [`../infrastructure/ENVIRONMENT-SPEC.md`](../infrastructure/ENVIRONMENT-SPEC.md)（綁定 AUGUR-L7 L7.50）為準。本目錄為 **[I] 資訊性營運快照，不具規範力、不取代該規格**。

**已知**：現行 `ENVIRONMENT-SPEC.md`（2026-07-18）主要描述 **DESKTOP-8MQPFS8（WSL2）**，且曾將 GB10 標為不可達——與 `aitopatom-b96e` 2026-07-21/22 實測不符。訂正屬 Steward §8.6／L7.50 事項；證據見 `ops/phase2/OPERABILITY-PROBE-2026-07-21.md`。

| 項目 | ENVIRONMENT-SPEC（2026-07-18） | DESKTOP-8MQPFS8（2026-07-21） | aitopatom-b96e（2026-07-22） |
|---|---|---|---|
| 平台 | WSL2 / x86_64 / GTX1650 | 相符（PG 17.10 等小幅前進） | **不同機：原生 aarch64 / GB10** |
| PostgreSQL | 17.9 | **17.10** | **未安裝** |
| ollama | 有（該機敘述） | （未安裝） | **0.32.1** |

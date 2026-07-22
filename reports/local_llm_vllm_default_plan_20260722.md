# local-llm 預設改走 vLLM — 計畫書 [I]

* **性質**：[I] 計畫（不創設 [N] 義務）。依憲章第六部「計畫先行」：本檔待用戶拍板後才改 mcp 預設。
* **報告日**：2026-07-22
* **主機**：`aitopatom-b96e`（GB10）
* **承接**：`ops/phase2/VLLM-SPIKE-20260722.md`（安裝／煙霧 **PASS**）；適配碼已在 `tools/local_llm_mcp`（`LLM_BACKEND=openai`）。
* **姐妹計畫（品質／運維）**：[`local_llm_vllm_optimization_plan_20260722.md`](local_llm_vllm_optimization_plan_20260722.md)——建議至少 P1 階梯後再 GO 本窄案。
* **程序更正**：同日曾在口頭「預設改走」下直接改 mcp／起服務，違反計畫先行；**已回退** mcp／`recommended.env` 為 Ollama，並停掉 `augur-vllm`。本檔為正式計畫，**拍板後**才執行 §六。

---

## 〇、一句話

在 GB10 上將 Cursor **local-llm** MCP 的**倉庫預設後端**從 Ollama `generate` 改為本機 vLLM OpenAI 相容 API；**project-memory 嵌入維持 Ollama**；模型採煙霧已驗證之小模，大模另案。

---

## 一、What／Why

| | 內容 |
|---|---|
| **What** | `.cursor/mcp.json`／`.mcp.json` 的 `local-llm.env` 設 `LLM_BACKEND=openai` 等；systemd 範本與 MCP `LLM_MODEL` 對齊；文件／證據更新。 |
| **Why** | 煙霧已 PASS；OpenAI 路徑與 vLLM 原生一致；預設指 vLLM 可減少「適配有、預設仍 Ollama」的雙軌混淆。 |
| **非目標** | 合併三支 MCP；改 constitution-mcp；公網／Tunnel；產品 UI 模型（仍 Ollama `qwen3:30b-a3b`）；一次上 122B／未驗 30B-A3B。 |

### 完整性對抗自問

| 問 | 答 |
|---|---|
| embed 會不會被誤切？ | 否：`project-memory` 僅 `OLLAMA_URL`／`EMBED_MODEL`，不動。 |
| vLLM 未起時 MCP 行為？ | fail-loud（既有 selftest）；須先起 unit 或回退 ollama。 |
| 0.6B 品質夠濃縮嗎？ | 煙霧僅證 API／provenance；品質風險明示——可另拍板換更大 Instruct。 |
| 與 coder-next 關係？ | Ollama `qwen3-coder-next` 改為**回退／可選**，不再是 mcp 預設推論模型。 |
| 顯存？ | unit 用 `--gpu-memory-utilization 0.35`；勿與 Ollama 大模並載。 |

---

## 二、現況（實證，拍板前）

| 項 | 狀態 |
|---|---|
| vLLM 安裝 | `~/augur-venvs/vllm`；vllm `0.25.1`／torch `2.11.0+cu130`／CUDA OK |
| 煙霧 | `Qwen/Qwen3-0.6B` → `qwen3-0.6b`；preflight＋`local_ask` `@ openai:` PASS |
| mcp 預設 | **Ollama**／`qwen3-coder-next`（回退後） |
| `augur-vllm` | unit 檔在 repo；user copy 可有；**未 enable**；服務 **stopped** |
| 適配／selftest | `python3 -m tools.local_llm_mcp selftest` OK（雙後端 stub） |

---

## 三、對應 table schema

**本計畫不產表、不改 DB。**

| 讀／寫 | 說明 |
|---|---|
| 無 PostgreSQL／SQLite 業務表 | 僅運維設定與本機 vLLM 行程 |
| （相關但不動）`.project_memory/index.db` | project-memory 索引；embed 仍 Ollama，本計畫不改 schema |

---

## 四、對應程式／設定規畫

| 角色 | 路徑 | 職責 |
|---|---|---|
| 設定（拍板後改） | `.cursor/mcp.json`、`.mcp.json` | `local-llm.env` 加 `LLM_BACKEND=openai`、`OPENAI_BASE_URL`、`OPENAI_API_KEY=EMPTY`、`LLM_MODEL`；保留 `OLLAMA_*` 供回退 |
| 設定 | `ops/machines/packs/aitopatom-b96e/recommended.env` | 取消註解同區塊 |
| 既有 library | `tools/local_llm_mcp/tools.py` | **不改**（已支援 openai） |
| 既有自測 | `tools/local_llm_mcp/selftest.py` | **不改**；驗收重跑 |
| 運維 | `ops/phase2/systemd/augur-vllm.service` | ExecStart＝`Qwen/Qwen3-0.6B`／`qwen3-0.6b`／`max-model-len 4096`／`gpu-memory-utilization 0.35`（範本已對齊） |
| 腳本 | `ops/phase2/vllm_preflight.sh` | **不改**；驗收呼叫 |
| 文件 | `ops/phase2/VLLM-GB10.md`、MCP／pack README | 拍板後改寫「預設＝vLLM」 |
| 證據 | `ops/phase2/VLLM-DEFAULT-YYYYMMDD.md` | 拍板執行後寫實測 |

**無新 Python 模組、無遷移腳本。**

### 拍板後 mcp `local-llm.env` 目標值

```text
LLM_BACKEND=openai
OPENAI_BASE_URL=http://127.0.0.1:8000/v1
OPENAI_API_KEY=EMPTY
LLM_MODEL=qwen3-0.6b
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3-coder-next
OLLAMA_NUM_CTX=32768
```

---

## 五、分階段與驗收

| 階段 | 動作 | 驗收 |
|---|---|---|
| A（已完成） | 適配＋獨立 venv＋煙霧 | `VLLM-SPIKE-20260722.md` PASS |
| B（**待拍板**） | 改雙 mcp.json＋recommended.env；文件對齊 | diff 可見 openai 預設 |
| C（拍板後執行） | `cp` unit → `systemctl --user daemon-reload && start`（**enable 見 §七選項**） | `vllm_preflight.sh --chat` PASS |
| D | `LLM_BACKEND=openai … local_ask` | provenance 含 `@ openai:` 與 `qwen3-0.6b` |
| E | selftest | OK |
| F | 用戶重載 Cursor MCP | MCP 頁 local-llm 可用；失敗則 fail-loud |

回退：`LLM_BACKEND=ollama` 或還原 mcp env；`systemctl --user stop augur-vllm`。

---

## 六、建議執行指令（僅拍板後）

```bash
# 1) 依本計畫改 .cursor/mcp.json、.mcp.json、recommended.env、文件
# 2) 起服務
mkdir -p ~/.config/systemd/user
cp ops/phase2/systemd/augur-vllm.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user start augur-vllm.service
# 3) 驗收
VLLM_MODEL=qwen3-0.6b bash ops/phase2/vllm_preflight.sh --chat
python3 -m tools.local_llm_mcp selftest
LLM_BACKEND=openai OPENAI_BASE_URL=http://127.0.0.1:8000/v1 \
  OPENAI_API_KEY=EMPTY LLM_MODEL=qwen3-0.6b \
  python3 -c "from tools.local_llm_mcp import tools; print(tools.local_ask('ping', max_words=10))"
```

---

## 七、待你拍板（請勾選）

**主決策（必選一）**

- [ ] **GO**：依本計畫把 local-llm **倉庫預設**改為 vLLM（`qwen3-0.6b`）
- [ ] **NO-GO**：維持 Ollama 預設；vLLM 僅手動／env 覆寫

**附帶選項（GO 時）**

- [ ] 模型維持 **`qwen3-0.6b`**（建議，已煙霧）
- [ ] 改更大模型（須另寫載入／顯存驗收；本計畫不涵蓋）
- [ ] **`systemctl --user enable augur-vllm`**（開機自啟）— 是／否（預設建議：先 start、enable 另拍）
- [ ] 執行後 **commit／push** — 是／否

**不在本案**：合併 MCP、Tailscale peer、PG／DB 還原 → 各另立計畫。

---

## 八、風險

| 風險 | 緩解 |
|---|---|
| vLLM 未起 → MCP 紅 | 文件寫清 start；fail-loud；可回退 ollama |
| 0.6B 濃縮品質弱於 coder-next | 明示；可另案換模 |
| 與 Ollama 大模搶 unified memory | utilization 0.35；煙霧前 stop 大模 |
| 未重載 Cursor 仍見舊 env | 驗收清單含「重載 MCP」 |

---

## 九、30 分鐘可讀摘要

煙霧已證明 GB10 可跑 vLLM＋MCP openai 路徑。本案只決定是否把**預設**從 Ollama 切過去；embed 不動。因計畫先行，設定已回退；**你勾 §七 GO 後**再改 mcp 並起服務寫證據。

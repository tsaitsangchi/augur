# vLLM 最佳化計畫 [I]

* **性質**：[I] 計畫（不創設 [N] 義務）。憲章第六部計畫先行——**本檔拍板前不改 mcp 預設、不換產線模型、不 enable 開機自啟**。
* **報告日**：2026-07-22
* **主機**：`aitopatom-b96e`（NVIDIA GB10／aarch64／~121 GiB 統一記憶體）
* **關聯文件**
  * 窄案（僅「倉庫預設是否改 openai」）：[`local_llm_vllm_default_plan_20260722.md`](local_llm_vllm_default_plan_20260722.md)
  * 煙霧證據：[`../ops/phase2/VLLM-SPIKE-20260722.md`](../ops/phase2/VLLM-SPIKE-20260722.md)
  * Runbook：[`../ops/phase2/VLLM-GB10.md`](../ops/phase2/VLLM-GB10.md)
  * 中期 MCP（Ollama）：[`../ops/phase2/LOCAL-AI-MID-UPGRADE-20260722.md`](../ops/phase2/LOCAL-AI-MID-UPGRADE-20260722.md)

---

## 〇、一句話

在**已通過煙霧**的 vLLM 適配之上，分階把「能跑」升級成「適合當 Cursor 濃縮後端」：記憶體／延遲可控、模型品質對齊任務、MCP 客戶端吃滿 OpenAI 路徑、與 Ollama（embed＋產品 UI）並存不互踩。

---

## 一、What／Why／邊界

| | 內容 |
|---|---|
| **What** | 運維參數、模型階梯、MCP openai 客戶端行為、並存策略、驗收與回退；可選再決定是否把倉庫預設切到 vLLM（交窄案）。 |
| **Why** | 現況僅證 API 通（0.6B）；預設 KV 曾近吃滿 unified memory；Qwen3 回覆含 `<think>` 浪費 `max_tokens`；0.6B 濃縮品質預期弱於現行 `qwen3-coder-next`。 |
| **成功定義** | 濃縮任務（summarize／extract／research／map_reduce）在固定提示下：**延遲可接受、輸出無無謂 think 佔額、與 embed 並存穩定、provenance 誠實**；數字皆出自實測 stdout／log。 |

### 非目標（本計畫不做）

- 合併三支 MCP；改 `constitution-mcp`
- Cloudflare Tunnel／公網裸開；雲端 Tailscale（另案）
- 產品 UI／advisor 改打 vLLM（仍 Ollama `qwen3:30b-a3b`）
- 一次上 122B；未經驗收宣稱「優於 coder-next」
- 治權檔判準變更

### 與「預設改走」窄案關係

| 窄案 | 本最佳化 |
|---|---|
| 只改 mcp.json 預設後端開關 | 把後端調到「值得當預設」的品質／運維水位 |
| 可獨立 GO／NO-GO | **建議**：至少完成下方 **P1 模型階梯驗收** 再 GO 窄案；亦可先優化、預設仍 Ollama |

---

## 二、現況基線（2026-07-22 實證）

| 項 | 值 |
|---|---|
| venv | `~/augur-venvs/vllm`；vllm `0.25.1`（spike） |
| 煙霧模型 | `Qwen/Qwen3-0.6B`／`served-model-name=qwen3-0.6b`／`max-model-len=4096` |
| unit 範本 | `--gpu-memory-utilization 0.35`（防預設 ~0.9 吃滿） |
| MCP 適配 | `LLM_BACKEND=openai` → `/v1/chat/completions`；`OPENAI_MAX_TOKENS` 預設 1024 |
| 倉庫 mcp 預設 | **仍 Ollama** `qwen3-coder-next`（窄案未拍板；過早切換已回退） |
| Ollama 在列 | `nomic-embed-text`、`qwen3:30b-a3b`、`qwen3-coder-next` |
| 已知痛點 | (1) 0.6B 品質未對標 coder-next；(2) chat 回覆常見 `<think>` 截斷有效答案；(3) 大模與 Ollama UI 並載風險；(4) openai 路徑無 per-tool `max_tokens`／無 thinking 關閉 |

---

## 三、對應 table schema

**本計畫不產業務表、不改 PostgreSQL／project-memory schema。**

| 物件 | 處置 |
|---|---|
| 無新 DDL | — |
| `.project_memory/index.db` | **只讀消費**；embed 仍 Ollama，不改表 |
| 結果落點 | 證據 Markdown：`ops/phase2/VLLM-OPT-YYYYMMDD.md`（實測數字）；設定落 `mcp.json`／unit／`recommended.env`（拍板後） |

---

## 四、對應程式／設定規畫

| 檔／函式 | 角色 | 本計畫可能改動 |
|---|---|---|
| `tools/local_llm_mcp/tools.py` → `_generate_openai` | OpenAI 相容推論 | P2：可選 `chat_template_kwargs`／關閉 thinking；per-tool 或 env 分檔 `OPENAI_MAX_TOKENS_*`；剝離或截斷 `<think>…</think>`（須 fail-loud 規則） |
| `tools/local_llm_mcp/selftest.py` | 回歸 | P2：stub 下新行為；死埠仍 isError |
| `tools/local_llm_mcp/README.md` | 文件 | 環境變數表更新 |
| `ops/phase2/systemd/augur-vllm.service` | 常駐 serve | P0／P1：模型 id、`max-model-len`、`gpu-memory-utilization`、可選 quant／prefix-cache 旗標 |
| `ops/phase2/vllm_preflight.sh` | 預檢 | P0：可選延遲／token 統計輸出（不改預設契約） |
| `ops/phase2/VLLM-GB10.md` | runbook | 同步參數與並存紀律 |
| `.cursor/mcp.json`／`.mcp.json` | Cursor 掛載 | **僅窄案拍板後**改 `LLM_BACKEND`；本計畫可先只改「手動 env 矩陣」文件 |
| `ops/machines/packs/aitopatom-b96e/recommended.env` | 建議 env | 註解區擴充優化參數 |
| **不新建** adapter／不合併 MCP | — | — |

**無 DB migration、無新 package。**

---

## 五、優化階梯（建議執行序）

### P0 — 運維穩定（低風險，建議先做）

| 項 | 作法 | 驗收 |
|---|---|---|
| 顯存預算 | unit 維持／微調 `--gpu-memory-utilization`（建議區間 0.25–0.40，實測定） | 起服後 embed `ollama` 仍可 `embeddings`；無 OOM |
| 並存紀律 | 文件寫清：跑 vLLM 時 `ollama stop` UI 大模；保留 `nomic-embed-text` | 清單可操作 |
| 預檢 | `VLLM_MODEL=… vllm_preflight.sh --chat`；記 latency | 證據檔有毫秒級（curl `time` 或 `/metrics`） |
| 健康 | user unit `start`／`stop`；**不 enable**（除非另拍） | status active／inactive 可預期 |

### P1 — 模型階梯（品質主軸）

目標：找到「濃縮夠用、記憶體可與 embed 並存」的奇異點（對齊原則精華 #19 精神：可控試錯）。

| 階 | 候選（HF／served-name 示意） | 意圖 |
|---|---|---|
| L0 | `Qwen/Qwen3-0.6B`／`qwen3-0.6b` | 已 PASS 基線 |
| L1 | 小 Instruct／Coder 級（**拍板時鎖定具體 HF id**，例 4B–8B 級） | 逼近現行 coder-next 可用度 |
| L2 | `Qwen/Qwen3-30B-A3B-Instruct`（MoE） | 高品質；須 utilization＋`max-model-len` 實測 |
| L3 | 更大 | **本波不排程** |

每階固定評測組（本地、零雲端 usage）：

1. `local_ask`：短答＋provenance  
2. `local_summarize`：固定一篇 `ops/phase2/` 短檔 → ≤5 句  
3. `local_research`：同一 query、`hops=1`  
4. 主觀可用度：相對 `OLLAMA_MODEL=qwen3-coder-next` 並跑（同一提示）— **並列表必須兩邊都有真實輸出**（原則 #9/#10）

**晉級規則**：L(n) 在記憶體可並存前提下，濃縮任務「明顯優於」L(n-1) 才升；無法並存則降 `max-model-len` 或退回上一階＝奇異點。

### P2 — MCP openai 客戶端（省 token／穩輸出）

| 項 | 作法 | 驗收 |
|---|---|---|
| Thinking 佔額 | 優先：vLLM／取樣參數關閉 Qwen3 thinking；次選：客戶端剝 `<think>` 後再截斷字數 | 煙霧「Reply exactly: pong」有效內容可見，非只 think 截斷 |
| `max_tokens` | 依工具分檔（ask／summarize 短；map_reduce 略長）或保留單一 env＋文件建議值 | selftest 綠；實測無無謂 1024 滿額 |
| Temperature | 濃縮預設偏低（env `OLLAMA_TEMPERATURE`／對稱 openai） | 文件＋可選實測 |
| 超時 | 大模提高 timeout；文件註明 | fail-loud 不變 |

### P3 — 並存與產品邊界（設定／文件）

| 角色 | 後端 | 模型意圖 |
|---|---|---|
| Cursor local-llm | vLLM `:8000` | P1 選定階 |
| project-memory embed | Ollama `:11434` | `nomic-embed-text` |
| 產品 UI／advisor | Ollama | `qwen3:30b-a3b`（**不**經本 MCP） |
| 回退 | `LLM_BACKEND=ollama` | `qwen3-coder-next` |

可選：窄案 GO 後 mcp 預設 openai；NO-GO 則最佳化成果僅經手動 env／文件使用。

### P4 — 進階（可選、另勾）

- Quant（AWQ／FP8 等）若 aarch64 wheel／模型可得  
- Prefix caching／較長 `max-model-len`（僅 L1+ 且顯存允許）  
- `systemctl --user enable`（開機自啟）  
- 與 Cloud／Tailscale 共用同一 `:8000`（資安另案）

---

## 六、分階段交付與驗收總表

| 階段 | 交付物 | 驗收 |
|---|---|---|
| P0 | runbook／unit 參數定稿；證據段「並存＋latency」 | preflight PASS；embed 煙霧 PASS |
| P1 | 階梯評測表（真實輸出摘錄＋來源標記） | 選定 `LLM_MODEL`／HF id 寫入 unit＋env 建議 |
| P2 | `tools.py`／selftest／README diff | selftest OK；think 佔額問題關閉或緩解有證 |
| P3 | 角色表落地文件；可選執行窄案 | 邊界表與實機一致 |
| P4 | 僅勾選項之證據 | 不影響 P0–P2 綠燈 |

**每階段一支／一段過目**（CLAUDE #19），不批次傾倒。

---

## 七、待你拍板

**A. 本最佳化計畫**

- [x] **GO**：依 P0→P1→P2（P3 文件；P4 另勾）執行（用戶 2026-07-22「先執行」）  
- [ ] **NO-GO**：維持現況（適配＋0.6B 煙霧即可）

**B. 與窄案順序**

- [x] 先最佳化（P0–P2），**再**考慮 [`local_llm_vllm_default_plan_20260722.md`](local_llm_vllm_default_plan_20260722.md)  
- [ ] 最佳化與窄案分開，預設永遠手動 env  
- [ ] 先窄案改預設（不建議，除非接受 0.6B 品質）

**C. P1 起點（GO 時選一）**

- [x] 從 L1 找「小而夠用」的具體 HF id（建議）→ **鎖定 `Qwen/Qwen3-4B`**  
- [ ] 直接挑戰 L2（30B-A3B），接受更長載入與並存調參  
- [ ] 暫留 L0，只做 P0＋P2

**D. P2 範圍**

- [x] 含 thinking 關閉／剝離＋per-tool max_tokens  
- [ ] 僅 thinking 處理  
- [ ] P2 暫緩

**E. 附帶**

- [ ] enable 開機自啟：是／否（預設否）→ **否**  
- [ ] 各階段結束 commit／push：是／否 → **待用戶指示**  

執行證據：`ops/phase2/VLLM-OPT-20260722.md`。

---

## 八、風險

| 風險 | 緩解 |
|---|---|
| 統一記憶體被 vLLM＋Ollama 大模雙吃 | P0 並存紀律；utilization 上限；評測時 stop UI 大模 |
| L2 裝得下但 MCP 延遲不可用 | 晉級規則含延遲門檻（拍板時定，例 p95＜N 秒） |
| 剝 think 誤傷內容 | 僅剝標準標籤；剝後空→isError |
| aarch64 無某 quant wheel | P4 誠實 FAIL，不阻塞 P0–P2 |
| 未重載 Cursor | 文件驗收項 |

---

## 九、30 分鐘可讀摘要

vLLM 在 GB10 **已經能跑**；最佳化要解決的是 **好不好用**（模型階梯、think 佔額、顯存並存），不是再寫一套適配。「改 mcp 預設」是窄案，建議掛在品質階梯之後。  
請勾 §七；**GO 後從 P0 單一階段開始**，過目再進 P1。

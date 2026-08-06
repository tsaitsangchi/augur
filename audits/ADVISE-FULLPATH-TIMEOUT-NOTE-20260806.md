---
status: note
series: retrieval
date: 2026-08-06
related: audits/LOCAL-KH-HIT-FIX-EXECUTED-20260806.md
paste: "ADVISE-FULLPATH-TIMEOUT-NOTE | qwen3:4b | prompt-bloat | FZ-keep"
self_reported: true
---

# NOTE｜全量 `advise`＋本機 Ollama 易逾時 · 2026-08-06

觸發：國碩 DR（`item=277948`）smoke；Steward 要「完整 retrieve_all、不 pin」。

## 實測

| 模式 | 結果 |
|---|---|
| `advise` 內聯 `retrieve_all`＋`qwen3:4b`（timeout **420s**） | **逾時** |
| 同上（timeout **900s**，`num_predict=400`） | 仍 **逾時**（>900s @ `/api/generate`） |
| 先 `retrieve_all`→相關度閘→**凍結引文**再 `advise(retrieve_fn=…)` | LLM **~250s 完成**；`hit277948=True`；**guard 未過**（模型把問句當「引文」打出 → 逐字閘攔） |
| SQL pin 該件 6 句再答 | **~350s**；guard 過；路徑 **/u2→/u5** 有依引文 |

## 讀法

1. **檢索命中已修好**（見 `LOCAL-KH-HIT-FIX`）：合併路能撈到 277948。  
2. **瓶頸在 LLM 側**：全量 inline 時 prompt＝works 雜訊＋多件 items＋人格／橋塊 → 弱 GPU 上 `qwen3:4b` 常超過數十分鐘級。  
3. 凍結引文可讓 LLM 跑完，但 **4b 易輸出「想題」長文**，觸發 `#1` 逐字／出處閘 → `guard.pass=False`（答案不可對外當綠燈）。  
4. **非**改 RBAC／KH 准入；不開 FZ／SIM。

## 操作建議（未授執行）

- 本機煙測：可先 retrieve 再凍結引文／縮 `num_predict`／`think=False`。  
- 產品路徑：控 prompt 體積（少灌 works 雜訊、local 問句偏重 items）或換較快模型（SOP-C）。  
- 勿把逾時解讀成「local raw 不可答」——料與命中已具備，差在本機生成吞吐。

*note only。*

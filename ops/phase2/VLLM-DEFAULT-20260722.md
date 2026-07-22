# vLLM 改預設 — 程序紀錄（非拍板執行）— 2026-07-22

* **性質**：[I] 程序更正紀錄。
* **結論**：口頭「預設改走」後曾改 mcp／起服務；用戶要求**先寫計畫再拍板** → 設定已回退、服務已停；正式計畫見 [`reports/local_llm_vllm_default_plan_20260722.md`](../../reports/local_llm_vllm_default_plan_20260722.md)。

| 時刻 | 動作 |
|---|---|
| 過早執行 | mcp → openai／`qwen3-0.6b`；`systemctl --user start augur-vllm`；preflight PASS |
| 更正 | mcp／recommended.env → Ollama；`stop augur-vllm`；寫計畫 §七待勾 |

**勿**將本檔視為「預設已改 vLLM」之驗收證據。

# local-llm-mcp

把本地模型當 Cursor 的**「濃縮型」工具**——將「輸入大、輸出小」的粗重子任務丟給本機推論後端，只把短結果回給 Cursor agent，藉此降低 Cursor 的 context/token。設計見 [../../reports/LOCAL-LLM-MCP-OPTIMIZATION-PLAN.md](../../reports/LOCAL-LLM-MCP-OPTIMIZATION-PLAN.md)。

**純 stdlib、stdio JSON-RPC 2.0**（體例同 `tools/constitution_mcp`）。唯一副作用為對本機後端之唯讀推論呼叫（預設 Ollama `/api/generate`；可選 OpenAI 相容 `/v1/chat/completions` 供 vLLM）。

## 使用

已由 repo 根 `.cursor/mcp.json` 註冊（`local-llm`），進專案自動載入。手動起服務／自測：

```bash
python3 -m tools.local_llm_mcp              # stdio server
python3 -m tools.local_llm_mcp selftest     # 自測（stub 模式，無須 Ollama）
```

## 工具（皆大進小出、唯讀）

| 工具 | 輸入 → 輸出 |
|---|---|
| `local_summarize` | `{text 或 path, max_sentences}` → 至多 N 句摘要 |
| `local_extract` | `{instruction, text 或 path}` → 依指示抽取之精簡結果 |
| `local_ask` | `{prompt, max_words}` → 受長度上限約束之本地回答 |
| `local_research` | `{query, k, hops, scope?}` → hybrid 多跳檢索後濃縮 |
| `local_map_reduce` | `{paths[], instruction}` → 多檔 map 摘要再 reduce（paths≤12） |

`text` 與 `path` 二選一；`path` 僅允許 **repo 根以內**之相對路徑。

## 與中期工具分工

| 需求 | 用 |
|---|---|
| 跨檔／不知路徑要短結論 | **`local_research`** |
| 已知多 path（≤12）合併 | **`local_map_reduce`** |
| 單檔／已有 text | `local_summarize`／`local_extract` |
| 只要片段出處 | project-memory `recall` |
| 治理精確原文 | constitution-mcp |

專案 rule：`.cursor/rules/local-mcp-routing.mdc`（alwaysApply）。

## 環境變數

| 變數 | 預設 | 用途 |
|---|---|---|
| `LLM_BACKEND` | `ollama` | `ollama` 或 `openai`／`vllm`（OpenAI 相容，供 vLLM） |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama 端點（backend=ollama） |
| `OPENAI_BASE_URL` | `http://127.0.0.1:8000/v1` | vLLM 等 OpenAI 相容根（backend=openai） |
| `OPENAI_API_KEY` | `EMPTY` | Bearer；vLLM 常不校验 |
| `OLLAMA_MODEL`／`LLM_MODEL` | GB10→`qwen3-coder-next`；WSL→`qwen3:4b` | 模型名（`LLM_MODEL` 優先） |
| `OLLAMA_NUM_CTX` | GB10→`32768`；DESKTOP→`8192`；PC002→`4096` | Ollama `options.num_ctx` |
| `OLLAMA_NUM_PREDICT` 等 | 與 openai 同 profile 預設（ask256／…） | Ollama `options.num_predict`（濃縮輸出硬上限） |
| `OLLAMA_KEEP_ALIVE` | GB10→`30m`；其他→`30s` | 推論後模型駐留；WSL 短卸載以便主 UI 換載 8b |
| `OPENAI_MAX_TOKENS` | profile 內建或 1024 | openai 通用上限；可被下列分檔覆寫 |
| `OPENAI_MAX_TOKENS_ASK` 等 | ask256／summarize512／extract512／research768／map384／reduce768 | per-tool max_tokens |
| `OLLAMA_TEMPERATURE` | _(空)_ | 可選；兩後端皆可傳（倉庫 mcp.json 釘 `0`） |
| `LOCAL_LLM_MCP_STUB` | _(空)_ | 設 `1` 走 stub，供無後端之自測 |

**Ollama 路徑**：送 `think=false`、per-profile `num_predict`、`keep_alive`，並剝離 `<think>…</think>`（剝後空→isError）。  
**openai 路徑**：送 `chat_template_kwargs.enable_thinking=false`，並同樣剝離 think。

**倉庫 mcp.json**：`local-llm` 釘死 `LLM_MODEL=qwen3:4b`（WSL 資料層預設）。**GB10 必須在 MCP env 覆寫 `LLM_MODEL=qwen3-coder-next`**（見 `ops/machines/packs/aitopatom-b96e/recommended.env`），勿只設 `OLLAMA_MODEL`（會被 `LLM_MODEL` 蓋過）。

倉庫改預設後端見 `reports/local_llm_vllm_default_plan_20260722.md`；運維／階梯見 `reports/local_llm_vllm_optimization_plan_20260722.md` 與 `ops/phase2/VLLM-GB10.md`。

## 紀律（selftest 逐項鎖）

1. **來源標記強制** —— 每筆輸出前置 `(local model: …)` 與「不得入 [N] 治理文書」警告。
2. **失敗發聲** —— 後端不可達/空回應一律 `isError`，不靜默回 stub（兩後端皆測）。
3. **路徑封閉** —— 檔案輸入僅限 repo 內相對路徑（防目錄穿越）。
4. **唯讀** —— 不提供寫入工具；以 **AST 掃描實作層**為權威判準。
5. **治理語料排除** —— `constitution/`、生效 `specs/*-SPECIFICATION.md` 拒絕並導向 constitution-mcp。

## 已知限制

* WSL 資料層（`qwen3:4b`）品質天花板低——僅託付機械性子任務；主對話可用 `qwen3:8b`（勿寫進 MCP `LLM_MODEL`）。
* GB10 可用 coder-next／較大 `num_ctx`，但仍是 **[I] 輔助**；深度判斷交回 Cursor。
* 僅「大進小出」才省 token；輸出與輸入等長時反而多一趟往返。
* `local_research` 依賴已重建之 project-memory 索引（含 FTS5）。

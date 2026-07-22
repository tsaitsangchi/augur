# local-llm-mcp

把本地模型（Ollama）當 Cursor 的**「濃縮型」工具**——將「輸入大、輸出小」的粗重子任務丟給本地 qwen3，只把短結果回給 Cursor agent，藉此降低 Cursor 的 context/token。設計見 [../../reports/LOCAL-LLM-MCP-OPTIMIZATION-PLAN.md](../../reports/LOCAL-LLM-MCP-OPTIMIZATION-PLAN.md)。

**純 stdlib、stdio JSON-RPC 2.0**（體例同 `tools/constitution_mcp`）。唯一副作用為對 Ollama 之唯讀推論呼叫。

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
| `OLLAMA_URL` | `http://127.0.0.1:11434` | 本地 LLM 端點 |
| `OLLAMA_MODEL` | GB10→`qwen3-coder-next`；DESKTOP→`qwen3:4b` | 模型名（可覆寫） |
| `OLLAMA_NUM_CTX` | GB10→`32768`；其他→`8192` | Ollama `options.num_ctx` |
| `OLLAMA_TEMPERATURE` | _(空)_ | 可選；設了才傳入 options |
| `LOCAL_LLM_MCP_STUB` | _(空)_ | 設 `1` 走 stub，供無 Ollama 之自測 |

## 紀律（selftest 逐項鎖）

1. **來源標記強制** —— 每筆輸出前置 `(local model: …)` 與「不得入 [N] 治理文書」警告。
2. **失敗發聲** —— Ollama 不可達/空回應一律 `isError`，不靜默回 stub。
3. **路徑封閉** —— 檔案輸入僅限 repo 內相對路徑（防目錄穿越）。
4. **唯讀** —— 不提供寫入工具；以 **AST 掃描實作層**為權威判準。
5. **治理語料排除** —— `constitution/`、生效 `specs/*-SPECIFICATION.md` 拒絕並導向 constitution-mcp。

## 已知限制

* DESKTOP（GTX 1650 / qwen3:4b）品質天花板低——僅託付機械性子任務。
* GB10 可用 coder-next／較大 `num_ctx`，但仍是 **[I] 輔助**；深度判斷交回 Cursor。
* 僅「大進小出」才省 token；輸出與輸入等長時反而多一趟往返。
* `local_research` 依賴已重建之 project-memory 索引（含 FTS5）。

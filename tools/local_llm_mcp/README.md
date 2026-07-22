# local-llm-mcp

把本地小模型（Ollama）當 Cursor 的**「濃縮型」工具**——將「輸入大、輸出小」的粗重子任務丟給本地 qwen3，只把短結果回給 Cursor agent，藉此降低 Cursor 的 context/token。設計與 token 帳見 [../../reports/LOCAL-LLM-MCP-OPTIMIZATION-PLAN.md](../../reports/LOCAL-LLM-MCP-OPTIMIZATION-PLAN.md)。

**純 stdlib、stdio JSON-RPC 2.0**（體例同 `tools/constitution_mcp`）。唯一副作用為對 Ollama 之唯讀推論呼叫。

## 使用

已由 repo 根 `.cursor/mcp.json` 註冊（`local-llm`），進專案自動載入。手動起服務／自測：

```bash
python3 -m tools.local_llm_mcp              # stdio server
python3 -m tools.local_llm_mcp selftest     # 自測（stub 模式，無須 Ollama）
```

## 三支工具（皆大進小出、唯讀）

| 工具 | 輸入 → 輸出 |
|---|---|
| `local_summarize` | `{text 或 path, max_sentences}` → 至多 N 句摘要 |
| `local_extract` | `{instruction, text 或 path}` → 依指示抽取之精簡結果 |
| `local_ask` | `{prompt, max_words}` → 受長度上限約束之本地回答 |

`text` 與 `path` 二選一；`path` 僅允許 **repo 根以內**之相對路徑。

## 環境變數

| 變數 | 預設 | 用途 |
|---|---|---|
| `OLLAMA_URL` | `http://127.0.0.1:11434` | 本地 LLM 端點（同區網可設 `http://10.10.130.46:11434`；雲端經 Tunnel/VPN） |
| `OLLAMA_MODEL` | `qwen3:4b` | 模型名 |
| `LOCAL_LLM_MCP_STUB` | _(空)_ | 設 `1` 走 stub，供無 Ollama 之自測 |

## 四項紀律（selftest 逐項鎖）

1. **來源標記強制** —— 每筆輸出前置 `(local model: …)` 與「不得入 [N] 治理文書」警告。
2. **失敗發聲** —— Ollama 不可達/空回應一律 `isError`，不靜默回 stub。
3. **路徑封閉** —— 檔案輸入僅限 repo 內相對路徑（防目錄穿越）。
4. **唯讀** —— 不提供寫入工具；以 **AST 掃描實作層**為權威判準（`selftest` 掃 `open(w/a/x/+)`、`write_text`、`unlink`、`rmtree` 等）。

## 已知限制

* 小模型（GTX 1650 4GB / qwen3:4b）品質天花板低——僅託付機械性、邊界清楚之子任務；深度推理與最終判斷交回 Cursor。
* 僅「大進小出」才省 token；輸出與輸入等長時反而多一趟往返。

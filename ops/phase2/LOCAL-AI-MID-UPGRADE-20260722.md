# Local AI mid-upgrade — GB10 — 2026-07-22

* **性質**：[I] 證據紀錄（不創設 [N] 義務）。
* **主機**：`aitopatom-b96e`
* **範圍**：混合檢索（FTS5+RRF）、`recall_hits`、`local_research`、`local_map_reduce`、`num_ctx`、GB10 預設模型 `qwen3-coder-next`。不含 vLLM。

## 驗收

| 項 | 結果 |
|---|---|
| `python3 -m tools.project_memory_mcp selftest` | OK |
| `python3 -m tools.local_llm_mcp selftest` | OK |
| 索引重建 | **684 檔 / 9100 chunk**；`search_schema=fts5-v1`；`fts：yes`；新鮮 |
| MCP 預設模型 | `qwen3-coder-next`；`OLLAMA_NUM_CTX=32768`（`.cursor/mcp.json`／`.mcp.json`／`recommended.env`） |
| hybrid recall 煙霧 | 命中 `ops/phase2/ENTITY-BACKFILL-20260722.md`（rrf+sem） |
| keyword recall 煙霧 | 命中同檔（`ENTITY-BACKFILL-20260722`） |
| `local_research` 煙霧 | hops=1；來源標記含 coder-next；濃縮含 GB10 backfill 要點 |

## 使用提示

- `recall` 預設 `mode=hybrid`；舊索引缺 `chunks_fts` 時 **fail-loud**（須重建，不靜默退回 semantic）。
- 產品 UI 仍用 `qwen3:30b-a3b`；MCP 濃縮改 coder-next。
- 重載 Cursor MCP 後新工具 `local_research`／`local_map_reduce` 才可見。

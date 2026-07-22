# Local MCP polish — 中期落地後再優化 — 2026-07-22

* **性質**：[I] 證據紀錄。
* **主機**：`aitopatom-b96e`
* **前提**：中期強化已在 `f0800eb` 落地；本輪只做路由＋效能／輸出瘦身。

## 變更摘要

| 項 | 內容 |
|---|---|
| Agent 路由 | `.cursor/rules/local-mcp-routing.mdc`（`alwaysApply: true`） |
| 工具描述 | `project-memory`／`local-llm` 各工具首句寫清優先使用時機 |
| `load_all` 快取 | 行程內 `(abspath, mtime_ns, size)`；多跳 research 免重解碼 |
| 輸出瘦身 | recall 橫幅一行；預設 snippet 500（`MEMORY_SNIPPET_CHARS`，上限 800）；research 餵模片段 800 |

## 驗收

- `python3 -m tools.project_memory_mcp selftest` → OK（含 cache hit／mtime 失效）
- `python3 -m tools.local_llm_mcp selftest` → OK

不做：vLLM、增量索引、合併 MCP。

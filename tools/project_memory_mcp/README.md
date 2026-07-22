# project-memory-mcp

全 repo **非治理輔助語料**的唯讀語意記憶層。純 stdlib、stdio JSON-RPC 2.0。
設計見 [`reports/PROJECT-MEMORY-MCP-PLAN.md`](../../reports/PROJECT-MEMORY-MCP-PLAN.md)。

## 定位（與其他 MCP 分工）

| 需求 | 用哪支 |
|---|---|
| 某條款/規格之**精確原文** | `constitution-mcp`（零幻覺） |
| 跨所有非治理檔案找「跟 X 有關的段落」 | **本 `project-memory-mcp`**（[I] 語意檢索） |
| 濃縮我手上這份特定檔案 | `local-llm-mcp` |

## 硬邊界：非治理輔助專用

**治理權威語料一律不索引**：`constitution/`、生效 `specs/*-SPECIFICATION.md`、
`RULING-*`、`AMENDMENT-LOG.md`。其查詢改走 `constitution-mcp`。`recall` 於回傳前
再過濾一次（縱深防線）。理由：該語料已由 `constitution-mcp` 確定性覆蓋，疊語意近似
只增幻覺風險（對齊元憲章 P2.E2/P2.E4/P2.Y）。

## 工具（MCP 唯讀）

* `recall {query, k=5, scope?, mode=hybrid}` → top-k 片段（`hybrid`＝語意+FTS5 RRF；亦可 `semantic`／`keyword`；附 `path:line`、[I] 標記）。
* `memory_status {}` → 檔數/chunk 數/嵌入模型/建立時間/FTS 狀態 ＋ 陳舊發聲。

## 建索引（CLI，寫入端；不經 MCP）

```bash
ollama pull nomic-embed-text          # 前置：嵌入模型（唯一需 pull）
python3 -m tools.project_memory_mcp index          # 建/重建索引 → .project_memory/index.db
python3 -m tools.project_memory_mcp memory_status  # 看現況
python3 -m tools.project_memory_mcp selftest       # stub 嵌入，無須 Ollama
```

## 設計紀律（皆有 selftest 斷言）

1. **讀寫分離**：`server` 僅匯入唯讀模組；寫入 SQL 僅存在於 `index.py`（AST/文本掃描鎖）。
2. **唯讀連線**：`store` 以 `mode=ro` 開 SQLite。
3. **治理排除**：`index` 不索引治理語料、`recall` 不回治理片段（正/反例斷言）。
4. **失敗發聲**：索引不存在／嵌入不可達 → `isError`，不靜默回空。
5. **陳舊發聲**：來源檔 mtime/hash 變更 → `memory_status` 標記建議重建。
6. **路徑封閉**：denylist 排除 `.env`/`.git`/`logs`/`.project_memory`/二進位等。

## 環境變數

| 變數 | 預設 | 說明 |
|---|---|---|
| `OLLAMA_URL` | `http://127.0.0.1:11434` | 嵌入服務端點 |
| `EMBED_MODEL` | `nomic-embed-text` | 嵌入模型 |
| `MEMORY_DB` | `.project_memory/index.db` | 索引 DB 路徑 |
| `PROJECT_MEMORY_MCP_STUB` | （空） | `1` 啟用確定性 stub 嵌入（測試用） |

索引 DB 為衍生物、不入 git；換機時 `git clone` → `ollama pull nomic-embed-text` →
`index` 重建即得同一份記憶。

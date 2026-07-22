# Incremental index — project-memory — 2026-07-22

* **性質**：[I] 證據紀錄。
* **主機**：`aitopatom-b96e`

## CLI

```bash
python3 -m tools.project_memory_mcp index          # 預設增量（SHA256）
python3 -m tools.project_memory_mcp index --full   # 刪 DB 全量
```

- 無 DB／缺 FTS／`embed_model` 變更 → 強制全量（明示，不靜默混嵌）
- 仍不經 MCP 寫入

## Selftest

`python3 -m tools.project_memory_mcp selftest` → OK  
（含：首次 full、無變更全 skip、改檔 updated、刪檔 removed、`--full`）

## GB10 對既有索引實跑（增量）

```
project-memory index [incremental]: 686 檔 / 9121 chunk
（+2 ~11 -0 skip=673）≈3s
→ 其後再增量納入本證據檔：687 檔 / 9125 chunk（+1 skip=686）≈0.3s
```

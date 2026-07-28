# KH4 最小 slice 收官（2026-07-28）

- 日期：2026-07-28
- 對應拍板：`KH4-PLAN + KH4-ANSWER-ORCH + KH4-INGEST-ALL + FZ-keep + NHC-keep`
- 性質：[I] 實作留痕；誠實記本輪邊界

## 本輪完成

1. 新增 `knowledge_kh4_state` 最小狀態表 DDL 與 `refresh_kh4_state.py` 刷新腳本。
2. 新增 `augur.knowledge.kh4` 聚合器，從既有 item/text/sentence/embed/fulltext/import qualification 衍生四層欄位與最小 `answer_status`。
3. `scripts/acquire_local_files.py` 已在 inserted/duplicate item 路徑刷新 KH4；`scripts/acquire_remote_files.py` 復用同一 `ingest_file`，故 SFTP item 路徑同步受益。
4. `scripts/promote_knowledge.py` 已在 harvest/staging 晉升 item 後刷新 KH4；`scripts/refresh_knowledge_pipeline.py` 已在 domain-scoped 的 harvest/fulltext/sentences/embed 後補刷新，topic harvest 路徑可落同一狀態流。
5. `scripts/advance_knowledge_terminal.py` apply 後會補一次 KH4 refresh，使 ATA 與 KH4 狀態不脫節。
6. `src/augur/philosophy/retrieval.py` 已把 items 側一般回答材料綁到 `knowledge_kh4_state.answer_status='eligible'`，最低層未達之材料不再直接進一般答案空間。

## 本輪未完成／誠實邊界

1. KH-axis expansion / interaction projection 目前為**保守機械衍生骨架**，不是全量語意投影器。
2. 本輪 KH4 以 **item 級狀態** 為主；local dry-run／reject 檔仍主要留在 `knowledge_import_qualification`，未另建非 item 級 KH4 收件箱。
3. live DB 遷移／狀態回填／服務重啟未能在本輪 shell 親跑完成，因當前環境缺 `pip`／`psycopg2`。

## 無 DB 自測

- `python scripts/migrate_kh4_state_ddl.py --selftest` ✅
- `PYTHONPATH=src python3 -m augur.knowledge.kh4 --selftest` ✅
- 受影響檔案 `py_compile` ✅

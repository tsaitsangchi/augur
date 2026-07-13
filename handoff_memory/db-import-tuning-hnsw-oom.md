---
name: db-import-tuning-hnsw-oom
description: augur DB 匯入的 HNSW 索引 OOM 陷阱 + 本機 WSL2/PostgreSQL 17 調優值（大檔匯入必讀）
metadata: 
  node_type: memory
  type: project
  originSessionId: 778040ca-21b5-4b60-ad2d-0fad302930ca
---

# augur DB 匯入調優 + HNSW OOM 陷阱（2026-07-13 實證入憲）

## 核心陷阱：HNSW 索引 × pg_restore -j4 = maintenance_work_mem 並發乘數 OOM

augur dump 內有 **3 個 pgvector HNSW 向量索引**：`idx_sent_emb_hnsw`（knowledge_sentence_embedding，~170萬列，最大）、`idx_lex_emb_hnsw`、`idx_chunk_emb_hnsw`。

- **`maintenance_work_mem` 每個「同時建置」的索引各吃一份**（不是單一 CREATE INDEX 的 parallel workers 乘——那是共享預算；真正乘數是 pg_restore -j4 讓**多個不同索引同時建**）。
- 2026-07-13 實測：預設 `maintenance_work_mem=64MB` 太小 → HNSW 建置狂 spill 磁碟、`idx_sent_emb_hnsw` 卡 **70 分鐘**未完（`wait_event=DataFileRead`，非死鎖、是真慢）。
- 但盲目調高也錯：7.7GB RAM 上設 4GB × 3 HNSW 並發 = 12GB ≫ RAM → **OOM killer**。

## 中止 pg_restore 中途索引是交易安全的（但有連帶）

中止卡住的 `CREATE INDEX`（`pg_terminate_backend(leader_pid)`）→ pg_restore 偵測失敗、繼續收尾、exit 0。但 `import_database.sh` 的 `pg_restore 2>&1 | tail -5` **只留 5 行、吞掉完整錯誤清單**（實測「errors ignored: 226」細節遺失）。**故中止後不可只信 exit 0 + 表數 smoke，須逐類型 TOC vs 活庫比對**。

## ⚠ information_schema 驗證陷阱（假警報教訓）

比對「缺失序列」時，`information_schema.sequences` **依 SQL 標準刻意排除 IDENTITY 欄位自動建的序列** → 誤報 16 個序列「缺失」，實際用 `pg_class`/`pg_get_serial_sequence` 查全都在。**驗證 DB 物件完整性一律用 `pg_class`/`pg_constraint`/`pg_indexes`（catalog 真值），勿用 information_schema（有權限與標準過濾）**。[[asof-completeness-per-table-verification]] 同精神。

## 本機（WSL2）資源與 PostgreSQL 17 調優值（2026-07-13 套用）

- **主機 16GB / WSL2 擴到 10GB**：`.wslconfig`（`/mnt/c/Users/S114013.GSMCTW/.wslconfig`）加 `memory=10GB`（留 6GB 給 Windows）+ 原 `swap=4GB`。**須 `wsl --shutdown` 重啟才生效**（我在 WSL 內無法自重啟；sudo 也需密碼無法自 restart postgres——但 postgresql `enabled` 開機自啟，WSL 重啟時自動載入新參數，綜效一次完成）。
- **postgresql.auto.conf（`ALTER SYSTEM SET`，只需 DB superuser、免 sudo）**：shared_buffers 2GB（**唯一 pending_restart**）· effective_cache_size 6GB · maintenance_work_mem **1GB 日常**（匯入時 session 拉高）· work_mem 16MB · max_wal_size 4GB · min_wal_size 1GB · wal_compression on · effective_io_concurrency 200（SSD）· random_page_cost 1.1（SSD）· max_parallel_maintenance_workers 4。
- 9/10 參數 `pg_reload_conf()` 即生效，僅 shared_buffers 待重啟。

## 大檔匯入正確 SOP（避免重蹈 OOM/龜速）

匯入前確認 maintenance_work_mem 與並發匹配 RAM。**最佳：資料段 -j4 並行載入 + 索引段序列建（-j1 post-data）配高 maintenance_work_mem**（單一 HNSW × 4GB 很安全），兼顧速度與記憶體。或保持 -j4 但 maintenance_work_mem ≤ (RAM − shared − OS)/3。**#30 DB 備份/遷移**、[[machine-switch-tooling]]、[[cross-machine-handoff]] 相關。

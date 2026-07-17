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

## 本機（WSL2）資源與 PostgreSQL 17 調優值

> ⚠️ **2026-07-17 實測:下列 2026-07-13 記載之調優值多數已不生效——這台機器不是當時那台**（`.wslconfig` 路徑 `S114013.GSMCTW` 在本機不存在；WSL2 RAM 實測 **15GB** 非 10GB；dump 在 `D:\` 非 `C:\`）。**大檔匯入前務必實查 `pg_settings` 現值,勿假設此檔所載已在。**
>
> | 參數 | 2026-07-13 記載 | 2026-07-17 live 實測 | PG17 default |
> |---|---|---|---|
> | maintenance_work_mem | 1GB | **64MB(回 default)** | 64MB |
> | shared_buffers | 2GB | **160MB** | 128MB |
> | effective_cache_size | 6GB | **5GB** | 4GB |
>
> 成因未明:非「auto.conf 全遺失」（shared_buffers/effective_cache_size 是**非預設值**、有人動過），但 maintenance_work_mem 確已回 default。hostname 仍 DESKTOP-8MQPFS8、無法單憑主機名判機器同異。

- **原 2026-07-13 記載（史料、多已失效）**：主機 16GB/WSL2 10GB、`postgresql.auto.conf` 設 shared_buffers 2GB·effective_cache_size 6GB·maintenance_work_mem 1GB·work_mem 16MB·max_wal_size 4GB·effective_io_concurrency 200·random_page_cost 1.1·max_parallel_maintenance_workers 4。

## 大檔匯入正確 SOP（避免重蹈 OOM/龜速）

匯入前確認 maintenance_work_mem 與並發匹配 RAM。**最佳：資料段 -j4 並行載入 + 索引段序列建（-j1 post-data）配高 maintenance_work_mem**（單一 HNSW × 4GB 很安全），兼顧速度與記憶體。或保持 -j4 但 maintenance_work_mem ≤ (RAM − shared − OS)/3。**#30 DB 備份/遷移**、[[machine-switch-tooling]]、[[cross-machine-handoff]] 相關。

## ⚠️ /dev/shm 陷阱：OOM 乘數的第二個維度（2026-07-17 我親手踩爆）

`import_database.sh` 索引段 `POSTJOBS` **寫死 `-j2`（不可用環境變數覆蓋）**、`IDX_MEM` 預設 **2GB**。2×2GB=4GB，安全。**我自作聰明把 `IDX_MEM=4GB`**（套腳本自己的公式 `IDX_MEM×2 < RAM−shared_buffers` = 8GB<14.9GB 判安全）→ 2×4GB=8GB **超過 `/dev/shm` 的 7.8G** → pg_restore 噴 `could not resize shared memory segment to 4291858624 bytes: No space left on device` → `idx_sent_emb_hnsw`+`idx_chunk_emb_hnsw` 建置失敗。

- **教訓**：HNSW 平行建走 dynamic shared memory（`dynamic_shared_memory_type=posix`）**吃 `/dev/shm`、不是 RAM**。腳本那條公式只管 RAM、漏了 `/dev/shm`——照它推導反而出事。
- **正解（下次照做）**：`import_database.sh <dump> --force` **不設 IDX_MEM**（用預設 2GB）。或若要 4GB 就得先把 POSTJOBS 改 `-j1`（序列建，單一 4GB<7.8G 安全且不 spill；記憶另載「-j1+高 mem」本就是 SOP 原文）。
- **補救**：失敗後 `SET maintenance_work_mem='2GB'; CREATE INDEX IF NOT EXISTS ...` 逐一補建即可，資料完整無損（COPY 全過、只是索引沒建）。但 2GB 對 170 萬列的 `knowledge_sentence_embedding` **仍不夠**（pgvector 噴 `hnsw graph no longer fits...after 966273 tuples`）→ spill 後建約 30 分鐘。
- **改進建議（未授權動 code、僅記）**：`import_database.sh` POSTJOBS 改 `-j1` 並讓 IDX_MEM=4GB 為預設，可省這 30 分鐘。

# ops_platform_tuning_plan_20260725 — 本機軟硬體最佳化計畫（WSL 重開後）

> **執行紀錄（2026-07-25，hugo 拍板「極限版」後執行）**：Stage 1 已完成——PG 14 項以 `ALTER SYSTEM` 寫入（極限版：shared_buffers=6GB、work_mem=256MB、maintenance_work_mem=2GB＋維護並行封 2、eff_cache=18GB、IO 併發 300、max_wal=16GB、gather=6、workers=12），重啟後 `pg_settings` 逐項驗證相符、augur 庫實連實查通過。Stage 3 已完成——ollama override（KEEP_ALIVE=1h／FLASH_ATTENTION=1／KV_CACHE_TYPE=q8_0）注入運行中服務；local-llm MCP 經查 `tools/local_llm_mcp/tools.py:126` 本機 hostname 預設已是 qwen3:4b、零改動。Stage 2 已完成（autoMemoryReclaim=gradual 生效、page reporting 已啟動）；Stage 4 明確不做。
>
> **後續追加（同日，用戶自行拍板執行）**：`.wslconfig` 升 `memory=26GB`（實測 25Gi 生效）＋`swap=128GB`；另裝 zram（`zram-tools`，**WSL2 核心僅支援 lzo-rle/lzo、無 zstd/lz4**——預設 lz4 會啟動失敗，須設 `ALGO=lzo-rle`）：`/dev/zram0` 12.7GB＝RAM 50%、priority 100 先於磁碟 swap。最終記憶體階層＝實體 25Gi → zram 12.7GB（lzo-rle ~2:1 期望）→ 磁碟 swap 128GB。巢狀虛擬化經實測 Win10 19045 不支援（僅 Win11）、確認不可用。
>
> **第二輪：模型與軟體層擴大（同日）**：`.mcp.json` local-llm 移除 `LLM_MODEL`／`OLLAMA_NUM_CTX`／`OLLAMA_KEEP_ALIVE` 三個覆寫，改由 `tools/local_llm_mcp/tools.py` 主機自適應邏輯生效——本機 num_ctx **4096→8192**（`tools.py:149` 作者原設；qwen3:4b Q4 權重 ~2.5GB＋q8 KV @8k ~0.6GB 塞進 4GB VRAM）、keep_alive 30s 不變（VRAM 分載設計 `tools.py:172`）、模型 qwen3:4b 不變；跨機不污染（GB10 自得 32768）。sysctl 記憶體彈性：`vm.swappiness=100`＋`vm.page-cluster=0`（zram 時代口徑）。**明確不擴**：embed 模型（nomic-embed-text 與 838 檔索引綁定，換＝全量重建＋口徑漂移）、PG（第一輪已極限）、qwen3:8b 常駐（違分載設計）、GPU（硬體天花板）。

> 依 #20 計畫先行；所有現況數字為 2026-07-25 重開後 live 實測（`pg_settings`／`free`／`systemctl`／`.wslconfig`），非記憶推估。
> 本計畫不產生／不讀 DB 業務表（v1.39.0 (a)：無新表 DDL；驗收查詢僅讀系統目錄 `pg_settings`）；(b) 程式面：零新程式，僅 config 變更＋既有工具驗證。

## 現況診斷（live）

| 項目 | 現值 | 問題 |
|---|---|---|
| shared_buffers | 160MB | 預設值，對 56GB 庫過小（建議 RAM 15-25%） |
| effective_cache_size | 5GB | 實際可用 cache ~19GB，planner 低估 → 偏好爛計畫 |
| work_mem | 4MB | 分析型查詢（feature build/對帳 join+sort）大量 spill 到磁碟 |
| maintenance_work_mem | 64MB | 建索引/VACUUM 慢；前次調優已因重啟遺失（印證記憶：須 ALTER SYSTEM 持久化） |
| random_page_cost | 4 | HDD 假設；vhdx 落在 SSD 上應為 ~1.1 |
| effective_io_concurrency | 1 | SSD 應 ~200 |
| max_wal_size | 1GB | 大量 sync/build 時 checkpoint 風暴 |
| Qdrant / augur-* 服務 | 不在此機 | 若此機要跑 advisor serving 須依 #31 重掛（本計畫列選配） |
| Ollama 模型 | qwen3:8b 5.2GB | > GTX 1650 4GB VRAM → 部分層落 CPU、推理慢 |

`.wslconfig` 已合理（24GB/12 threads/swap 64GB/sparseVhd）；cron 每日 06:15 審議已掛。

## Stage 1 — PostgreSQL 調優（主要效益；須重啟 PG）

以 `ALTER SYSTEM SET`（寫入 `postgresql.auto.conf`，**重開機不再遺失**）：

```
shared_buffers = 4GB
effective_cache_size = 14GB
work_mem = 64MB                  -- 注意與並行 worker 相乘
maintenance_work_mem = 1GB       -- 上限刻意保守：HNSW 建索引×並發=記憶體乘數，4GB×-j2 曾 OOM
random_page_cost = 1.1           -- 假設 vhdx 在 SSD；若 D:/機械碟另議
effective_io_concurrency = 200
max_wal_size = 8GB
wal_compression = lz4
max_parallel_workers_per_gather = 4
```

執行：`ALTER SYSTEM` × 9 → `sudo systemctl restart postgresql@17-main` → 驗收：`SELECT name,setting FROM pg_settings WHERE ...` 逐項比對＋跑一支既有唯讀查詢實測（#7）。

## Stage 2 — WSL 層（選配；須 Windows 端 `wsl --shutdown` 重進）

`.wslconfig` `[experimental]` 加 `autoMemoryReclaim=gradual`：閒置時把 Linux page cache 還給 Windows（主機僅 ~32GB、雙開 stock_backend 時有感）。風險低、可隨時移除。

## Stage 3 — Ollama/GPU（選配、零風險）

- 日常 local-llm MCP 改預設 `qwen3:4b`（2.5GB 全進 4GB VRAM，速度數倍於 8b 部分 offload）；8b 留給品質敏感任務。
- `OLLAMA_KEEP_ALIVE=30m`（unit 內 Environment）減少反覆載模型。

## Stage 4 — 服務重掛（僅當此機需要）

Qdrant／augur-chat/advisor/admin 均不在此機；若要在此機 serving 依 #31/HANDOFF 重掛。不需要則明確不做（非漏做）。

## 不做清單

- 不動 stock_backend crontab（clean-room #17）
- 不調 vm.swappiness／CPU governor（WSL2 下效益不明，不為調而調）
- 不在此計畫內建任何 HNSW 索引（避免重蹈 OOM）

## 驗收

1. `pg_settings` 九項全數等於目標值且 `pending_restart=false`
2. 重啟後 augur DB 可連、任一既有唯讀 script 實跑通過
3. （若做 Stage 2）`free -h` 重進後總量不變、閒置時 Windows 端記憶體回收可見

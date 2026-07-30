---
name: augur-db-schema-traps-20260730
description: 294 表 live 親驗之 schema 陷阱:raw_* 前綴反義、Dividend PK 塌列根因、ExchangeRate 兩表新舊差 6 年、candidate 表無 guard、reltuples=-1≠空表
metadata: 
  node_type: memory
  type: project
  originSessionId: 223fa752-0df8-474d-aa39-9ddbcbfef034
  modified: 2026-07-30T04:36:12.850Z
---

2026-07-30 全庫親驗（`reports/augur_full_reread_facts_20260730.md` §11）之 schema 陷阱，最會咬人的八則：

1. **raw 資料表沒有 `raw_` 前綴；三張 `raw_*` 表全都不是原始資料**：`raw_supersede_log`（3,914 列，append-only 證據帳、DELETE/TRUNCATE 一律拒）、`raw_table_coverage_snapshot`（97 列覆蓋快照）、`raw_evolution_iteration_ledger`（RAWEVO 輪帳）。用 `LIKE 'raw_%'` 找原始資料表＝全錯。
2. **`TaiwanStockDividend` 的 PK 只有 `(stock_id)`**（其他 raw 表都含 date）——每檔只能存活一列，任何 upsert 式 re-sync 都把歷史壓成最新一列。現況 2,411 列 vs 4,295 檔＝「Dividend 塌列 ~92%」的**物理成因是這條 PK，不是抓取漏失**（且 PK 首建定死，唯 DROP 重建可解）。
3. **`ExchangeRate` 與 `TaiwanExchangeRate` 是兩張表且新舊差 6 年**：前者 max(date)=2020-11-13（停更 2,082 天），後者 max(date)=2026-07-29（live）。誤用前者做匯率特徵＝靜默拿到 6 年前資料。
4. **`feature_candidate_values` 完全沒有 guard trigger**，而 `feature_values` 有 `fv_guard` 全鎖；兩表 schema 一模一樣（panel_date, stock_id, feature, value）只差一個字——**寫錯表＝繞過整套誠實閘且無任何錯誤訊息**。
5. **`reltuples = -1` 不等於空表**（從未 ANALYZE 者回 -1）：本次 30+ 張表為 -1，其中僅 21 張真 0 列（`knowhow_kh7_eligibility` reltuples=-1 但實 40 列）。判空一律 `count(*)`。
6. **`knowledge_concordance` 母表顯示 0 bytes**，真實 5,315 萬列／4,397 MB 全在 p0–p15 分割裡——只看母表會把最大的知識索引誤判成死表。
7. **名字都叫 honesty 但行為不同**：`honesty_delete_only_guard` **無任何 bypass**（函式體無條件 RAISE，連 `augur.honesty_write=on` 也無效），而 `honesty_ledger_guard`／`fv_guard`／`src_whitelist_guard`／`factor_ruling_guard` 的 UPDATE 有 GUC 通行證。
8. **孤兒防呆函式**：`trg_item_source_gate()` 存在 `pg_proc` 但**沒掛在任何表上**（pg_trigger 零命中）——本應擋 `knowledge_item_text` 的 owned_local 無 source_key 與非 active 父源，目前只有 staging 層有擋。另 `model_registry`（16 列）無 immutability trigger，可被裸 UPDATE 默改 feats_hash／metrics／git_sha（對照 `local_model_version` 有 `model_version_no_goalpost`）。

**Why**：這些都是「看似 A 實為 B」型，靜默給出錯結論；第 4／7／8 則更是誠實閘本身的覆蓋缺口——寫錯一個字或以為通行證萬用，整套帳本保護就繞過了。

**How to apply**：查表前先 `information_schema` 實查（勿憑名稱推語意）；判空用 `count(*)`；寫任何 panel 值前確認目標表是 `feature_values`（生產、有閘）還是 `feature_candidate_values`（staging、無閘）；改帳本前先讀該表 guard 的函式體確認有無 bypass。相關：[[augur-path-six-parallel-gap]]、[[guard-mechanisms-that-silently-fail]]。

# augur 跨機接續快照 — 2026-06-15b(catalog 工作鏈完成 + 全表重抓進行中)

**用途**:換另一台電腦接續本專案。讀此 + 5 治權檔即可接手。
**鐵則**:① **DB 不隨 git、每機各自獨立**(`DB_HOST=localhost`)→ 狀態一律**實查**(`pg_stat_user_tables`)、勿照抄本快照數字。② **記憶(`~/.claude/.../memory/`)machine-local、不進 git** → 知識靠此 handoff + committed 報告轉移。③ commit/push 須用戶授權(#14);放量須授權 + caffeinate 防睡眠(#22/#24)。

---

## 0. 一句話現況

本 session 完成 **catalog 工作鏈**(官方 datasets.md 入憲 → builder 去硬編 → catalog build 95 表 → GoldPrice 聚合 → **sync 階段 F catalog 驅動**),並啟動**全表重抓 from-zero**(本機權威 Mac、進行中)。**git HEAD `630b7ba`(已 push)**;tags:`treaty-v1.8.0`(憲章 v1.8.0)、`catalog-driven-sync-20260615`(sync 階段 F)。

## 1. 換機後第一步(在新電腦)

```bash
cd <repo>                       # 真實工作目錄(隨機器,如 /home/hugo/project/augur)
git pull                        # 取 630b7ba(catalog 去硬編 + GoldPrice 聚合 + sync 階段 F)+ 本 handoff
python -m venv venv && source venv/bin/activate && pip install -e .   # 若新環境
cp .env.example .env            # 填 DB_* / FINMIND_TOKEN / FRED_API_KEY(.env 不進 git)
PYTHONPATH=src venv/bin/python -m pytest tests/ -q                    # smoke:應 43 passed
```
**先實查新機 DB**(勿假設):
```bash
PYTHONPATH=src venv/bin/python -c "from augur.core import db
with db.connect() as c:
  with db.transaction(c) as cur:
    cur.execute(\"select count(*) from pg_stat_user_tables where n_live_tup>0\"); print('有資料表',cur.fetchone()[0])
    cur.execute(\"select to_regclass('dataset_catalog')\"); print('catalog 表',cur.fetchone()[0])\"
```

## 2. 本 session 完成了什麼(catalog 工作鏈、皆已 commit/push)

1. **官方 FinMind `datasets.md` 入憲**(`docs/finmind-references/datasets.md`、全 92 表 tier/params/columns)= catalog 抓法元資料**權威輸入源**;憲章升 **v1.7.0→v1.8.0**(第三部 catalog 段補輸入源)。`dd9c817`。
2. **catalog builder 去硬編**:`src/augur/catalog/__init__.py` 加 `_parse_official_datasets`(解析官方 datasets.md、大小寫容錯)→ tier/intraday/sponsor/single-day 官方驅動、取代硬編白名單;移除誤判 `_is_intraday_data` heuristic。官方未列退回 probe/硬編備援(不脆)。`dd9c817`。
3. **catalog build 95 表/683 欄**(透過 FinMind/FRED API 探測 + 官方驅動);excluded 11(intraday 8 + OUT_OF_UNIT 3)。**catalog 表 DB-local、不隨 git → 新機須重跑 `scripts/build_catalog.py`**。
4. **GoldPrice intraday→日級聚合**:`ingest._AGGREGATE_DAILY={"GoldPrice":"close"}` + `_aggregate_daily`(每日末筆 close) + store hook;FinMind 回 5-min intraday 但聚合日級存(#4)。`fe503f9`。
5. **sync 階段 F catalog 驅動**:`sync.sync_finmind_dataset` 加 `_catalog_plan`(SQL 讀 catalog、不 import catalog 避循環)+ `_sync_by_plan`(按 fetch_mode 走正解:by-date/by-dim-id/per-stock/market、復用現有函數);catalog 無/異常 → fallback adaptive。**4 截斷表 catalog fetch_mode 正解**(Europe/UK=by-date、Interest/Exchange=by-dim-id)→ 不再截斷。`630b7ba`。

## 3. ⭐ 本機全表重抓 from-zero(進行中、本機 DB、不隨 git)

- **driver**:`/tmp/augur_full_rebuild.py`(一次性、不進 git):drop log/catalog 外 83 表(保留 `pipeline_execution_log`/`data_audit_log`/`dataset_catalog`/`column_catalog`)→ DB 空 → `full_market_sync.py` catalog 驅動 from `full_start` 全史 + 逐 dataset #7 對帳。
- **進度(實查、勿照抄)**:啟動 ~2.7h;`GovernmentBankBuySell` 完成 #7 對帳 PASS、`BalanceSheet` 抓取中(by-date 2023-11)。錯誤 0、額度 ~2165/6000。
- **防護**:`caffeinate -dimsu nohup`(獨立進程、**session 結束仍續跑 + 防睡眠**)+ SHMM 心跳 `b6wiojf37`/watchdog `bcx7voaku`(**Claude session 結束則死、但 full_rebuild 進程不受影響**)+ resume-safe(中斷重跑:sync DB-driven resume + 冪等;**注意 by-dim-id `_dimension_sync` 表級 max resume 局限**——中途中斷某 by-dim-id 表可能漏、需 drop 該表重跑)。
- **log**:`/tmp/augur_rebuild.log`。
- **換機後本機處置**:full_rebuild nohup 自會跑完(~25h 剩、caffeinate 防睡眠);但無 Claude 監控 → 用戶可手動查 log/DB。跑完 DB 全表完整(catalog 驅動正解、4 截斷補全、GoldPrice 日級)。

## 4. 關鍵知識(記憶 machine-local、這裡轉移)

- **catalog 驅動 sync 已實裝(階段 F)**:新機 sync 會優先讀 catalog fetch_mode 走正解(須先跑 `build_catalog.py` 建 catalog 表);catalog 無 → adaptive fallback。
- **datasets.md 抓法分類**:6 模式(per-stock/by-date/by-dim-id/single-day/dedicated-URL/FRED);4 截斷表正解見 §2.5;GoldPrice=intraday-source 聚合日級。
- **⏰ FinMind sponsor token `2026-06-24` 到期(剩 9 天)**:sponsor-only(分點/tick/snapshot/法人 by-date/可轉債/八大行庫)須趕;額度問 `_user_info` 讀錶(偶發單讀 0 異常、連查過濾)、見訊號即停。
- **財報三表/月營收 by-date 逐日掃季頻**:低效(大多日 0 列)但數據正確;optimization plan 想優化為只抓期別日(未實裝)。
- 本機記憶檔(新機可重建):`augur-orientation`/`augur-live-state`/`augur-fetch-map`/`finmind-rate-discipline`/`downstream-frozen-until-data-clean`。

## 5. 治權現狀(5 檔各自獨立版本)

靈魂 **v1.2.0** · 原則精華 **v1.6.0**(20 條) · 憲章 **v1.8.0**(+官方 datasets.md 入憲 catalog 輸入源) · CLAUDE **v1.3** · README。三敵(#1/#8/#15)。

## 6. 接續 TODO

1. **本機**:全表重抓跑完 → 驗證全表完整 + 全 82 表 #7 對帳乾淨(`scripts/reconcile_audit.py`)。
2. **新機**:git pull → `build_catalog.py`(建該機 catalog)→ catalog 驅動 sync(full_market_sync 或全表重抓);獨立 DB。
3. **B 對帳方法學**(reconcile._norm 正規化/季頻排除未定案/roster 排 date)→ 消假 FAIL。
4. **全表完整 + 對帳乾淨 → 才解凍 F2/F3**(見 downstream-frozen 鐵則)。
5. F3 models + evaluation(PHASE 10-11、未建);計畫見 `reports/augur_f3_model_plan_three_thoughts_20260612`。

> 放量/commit/push 一律須用戶明示授權。

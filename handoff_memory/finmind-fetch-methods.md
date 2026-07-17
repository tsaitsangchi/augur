---
name: finmind-fetch-methods
description: FinMind+FRED 全抓取方法地圖——endpoint/模式/data_id階層/特殊處理/edge case；所有資料都抓得到、用對方法即可（catalog table 之知識源）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 59b6aa15-483d-4e47-b40f-7daa0635e8d4
---

> ⚠️ **2026-07-17 更正:此段方向已被再次翻轉,勿信本段為終局(鐘擺型記憶,見 [[cross-claim-contradiction-check]])**。以現行 code `ingest.py:32-46` 為準:`OUT_OF_UNIT` **現載 3 表(分點/權證/鉅額),明文「資料量規模物理界限排除(非暫緩)、probe 實證 2026-06-23/24」**;`BACKFILL_DEFERRED = frozenset()` **＝空集合**(鉅額分點 06-24 移入 OUT_OF_UNIT)。即:2026-06-16 的「證偽→可抓但暫緩」在 06-23/24 又被 probe 翻回「治權級排除」——照下段舊敘述做會提出違反現行 doctrine 的抓取規劃。

**鐵則：所有資料都抓得到、只是要用對方法**（用戶 directive 2026-06-15；⚠ 見上方更正,3 表已治權級排除）。真排除只剩 **#4 intraday**；原 **#3「OUT_OF_UNIT 規模物理不可行」(分點/權證/鉅額 3 張) 2026-06-16 證偽**——實證皆可抓（分點/權證走 **dedicated endpoint** via `finmind.fetch_dedicated(path, date, data_id)`、鉅額走普通 /data），退役改名 **`ingest.BACKFILL_DEFERRED`**（可抓但暫緩自動全市場 backfill、scope 待決、**非物理不可行**）。其餘表皆 augur 該抓的日級真兆，差別只在「用哪種抓法」。→ 這就是 catalog table 要記「每 dataset 怎麼抓」的原因，成為抓取權威依據（更正確/快/省 token）。完整見 reports/augur_datasource_finmind_fred_20260615.md + finmind/fred_research_20260611 + generic_ingester_schema_catalog_20260610/11 + fullsync_issue_analysis_20260610。

## API endpoint 全集（不只 /data）
- **`/data`**（主路徑，多數 dataset）· **`/datalist`**（列 data_id 全集，**僅 7 總經**：CrudeOilPrices/CurrencyCirculation/ExchangeRate/GovernmentBondsYield/GovernmentBonds/InterestRate/TaiwanExchangeRate）· **`/translation`**（翻**科目值非欄名**、多空→欄中文 API 拿不到）· **`/storage_objects?dataset&date`**（整日 parquet bulk、忽略 data_id，tick/KBar 大表高效）· **dedicated 專屬 URL**（`/taiwan_stock_trading_daily_report`、`_secid_agg`＝分點/券商聚合，Sponsor，非 /data）· **`user_info`**（獨立 host api.web.finmindtrade.com/v2，讀錶不計額度）。FRED：`/series/observations`(抓)+`/series/search`+`/category/series`(列series-id)+`/series/vintagedates`(#8 PIT vintage)。

## 抓取模式 × dataset（catalog fetch_mode）
per_stock(逐股,需data_id,canonical 2330探) · by_date(逐日全市場,無data_id,sponsor可) · by_dimension_id(/datalist維度:GovBonds13期別/匯率幣別/InterestRate央行/Futures TX/Option TXO) · market(寬窗無id一次全拉) · single_day(size-too-large→end_date須none逐日:News/tick/snapshot/5sec) · dedicated(分點/secid_agg專屬URL) · bulk_parquet(/storage_objects) · special_id(TotalReturnIndex=TAIEX/TPEx、FuturesFinalSettle=TX) · per_series(FRED)。

## data_id 來源階層（#18，記「來源類型」非死白名單）
`/datalist`(7總經/契約)→roster(TaiwanStockInfo per-stock)→**Info-roster**(國際股XXXPrice→XXXInfo,_info_roster_ids)→**文檔種子**(TotalReturnIndex=TAIEX/TPEx,_DOC_SEED_IDS)→91指數碼(snapshot)→none。**一律問 API(/datalist>靜態文檔,GovBonds 13>文檔12)**。

## 特殊處理 / edge case（catalog 該記、避免重撞）
- **型別爆炸→降級**(generic_schema已解):契約月`200710/200711`、週選`201211W4`撞NUMERIC→VARCHAR;sentinel`-1`撞DATE→字串;非法日`1911-00-00`(_is_date驗fromisoformat)→字串;null `stock_id`(USStockPrice 1997-09-30)→改by-dim-id逐ticker。
- **PK塌陷**:10表無自然鍵→全欄入PK(BlockTrade/GovBank/期權Daily…);USStockPrice stock_id不在PK=**待修**。by-date強制date入PK、by-id強制維度欄入PK防塌列。
- **對帳範圍(reconcile_scope,關鍵)**:per-stock落地表須**roster-scoped**對帳(勿與market by-date對撞→假MIS含權證);**季頻表**(財報三表)近窗對帳空PASS=假PASS→須reconcile_audit全史(since=None+排未定案最新季)。
- **anti-leakage公告欄(#8)**:Dividend.AnnouncementDate/AnnouncementTime · MonthRevenue.create_time(待實證) · Shareholding.RecentlyDeclareDate;財報三表無→法定lag。
- **限流**:三層(_pace 0.8s→_quota_gate問錶≥5800暫停→403冷卻1800s);**16w/0.8s連跑10.5hr 0 throttle**;gate暫停≠throttle(看有無403);rolling視窗問錶不推算;#25最小單位(單股單日)測。
- **6/24到期**:sponsor-only(分點/tick/snapshot/KBar/可轉債/法人by-date/八大行庫)到期降free抓不到→趕到期前。

## 全集口徑（R2 v1.4.0）
93 enum → 真排除8(intraday) + BACKFILL_DEFERRED 3(原OUT_OF_UNIT;2026-06-16證可抓、僅backfill scope待決非排除) = 可建82表(81 FinMind+FRED)/665欄。分類A台股價格19/B籌碼14/C基本面13/D可轉債4/E衍生18/F國際8/G商品總經5/H FRED1。詳逐表規格見 generic_ingester_schema_catalog。相關:[[finmind-data-source]] [[fred-data-source]] [[augur_project_overview]]。

---
name: finmind-data-source
description: FinMind 資料源全貌——augur token=Sponsor 6000/hr、2026-06-24 到期、/datalist 維度 id 來源；完整研究見 report
metadata: 
  node_type: memory
  type: reference
  originSessionId: 535524f8-f10a-43be-8ee8-7e88ab8d3ccf
---

augur 主資料源 FinMind 全貌。**完整研究**：`reports/augur_finmind_research_20260611.md`（dataset 全集 ~75+ / tier / endpoints / data_id 來源 / 特殊模式）。

**augur token 實況**（live probe `api.web.finmindtrade.com/v2/user_info` Bearer，2026-06-11）：**level 3 `Sponsor`、限速 6000/hr、user_id tsaitsangchi**。
⏰ **訂閱 `2026-06-24` 到期**（除非續訂）→ 之後降 Free（600/hr）、**sponsor-only dataset（分點 TradingDailyReport / tick / snapshot / KBar / 可轉債 / 法人 by-date）抓不到** → **全市場全史 sync 須趕在到期前跑完 sponsor 資料**。目前能抓**全部** dataset。

**API endpoints**（base `api.finmindtrade.com/api/v4`）：`/data`、**`/datalist`（列 data_id 全集，僅 7 總經類：CrudeOilPrices/CurrencyCirculation/ExchangeRate/GovernmentBondsYield/GovernmentBonds/InterestRate/TaiwanExchangeRate）**、`/translation`、`/storage_objects`（parquet bulk, sponsor）、`/login`。

**data_id 來源階層（#18，非臆測白名單）**：`/datalist`（總經/期權契約）→ roster TaiwanStockInfo（per-stock）→ 官方文檔+probe（TotalReturnIndex=TAIEX/TPEx）。**實證 `/datalist` > 靜態文檔**（GovBonds /datalist 13 期別 vs 文檔 12、漏 4-Month）→ 程式一律問 `/datalist`、不抄文檔、不臆測。

**特殊模式**：單日型（News/tick，end_date 須 none、finmind.fetch 已自動相容）；`[F/B/S]` dataset free 需 data_id、Backer+ 才 by-date（augur sponsor 可 by-date 全市場省 request）。

**⭐ anti-leakage 金礦——API 自帶公告時點欄位（2026-06-12 自 catalog 實證，#8 PIT 關鍵）**：
- `TaiwanStockDividend.AnnouncementDate/AnnouncementTime`（公告日期/時間）→ 股利事件 as-of 可錨定**公告日**（非除息日），零洩漏。
- `TaiwanStockMonthRevenue.create_time` → **疑似 PIT 入庫時戳，語意待實證**——若=公告時點則月營收 PIT 可直接用（最高頻基本面）。
- `TaiwanStockShareholding.RecentlyDeclareDate`（最近申報日期）→ 外資持股 as-of 錨。
- **財報三表（BalanceSheet/FinancialStatements/CashFlows）無公告欄** → 仍須法定申報期限保守 lag（Q1≤5/15、Q2≤8/14、Q3≤11/14、年報≤3/31、月營收≤次月10日；operational 透明層,非 feature 值）。
- 用途：F2d 基本面/F2f 事件特徵之發布日 gate；設計細節見 `reports/augur_feature_design_first_principles_20260612.md` §四 + `augur_f2_feature_expansion_roadmap_20260612.md` §三。

**⚠️ 雙端點最終一致性（2026-06-12 實證,#7 對帳方法論關鍵）**：per-stock 與 by-date 兩路徑對**近 1-2 日**可回不同值（實證法人表 6/11-12 VM=196 全落近兩日、6/9-10 乾淨；三方鑑別 db==per-stock≠by-date(=0)）——by-date 落後、per-stock 較新較全。**近窗對帳 FAIL 於 T-1/T-2 屬預期暫態 → 禁 heal_by_date（會以 by-date 的 0 覆蓋 per-stock 真值）**、T+2 復驗自癒；reconcile 近窗判定宜視「最後 1-2 日=結算窗」（#7「今日結算中」之延伸,改 code 屬判準變更須用戶核）。

**限流真相（2026-06-12 實證）**：額度=**rolling 視窗**（零 call 期間錶連續退、非整點清零）；兩種 403（額度型 vs IP sustained 型）；重試風暴=惡化路徑。對策=三層防護（`_pace`→`_quota_gate` 閉環問 `/user_info` 權威錶→403 長冷卻 1800s）；`/user_info` 403 期間可讀、讀錶不自計。

**⭐ Schema/中文 metadata 真相（2026-06-15 全面實測）**：FinMind/FRED **皆不提供欄位型別/大小/逐欄中文**——`/data` 回應只有 `msg/status/data`、值**全是字串**（連 `200710` 都是 str）；官方範例用 pandas 推型別、與 augur `generic_schema` 同理。`/translation` 全 **83 dataset 實測：0 個給逐欄清單、9 個給 `{name,english}` dict（翻「值」：科目/法人別/外資/融資/指數名，少數欄名如 Dividend；計入額度 ~1:1）、74 空**。→ 型別/大小由 augur 推導、中文 FinMind 官方(9 表)＋金融用語(其餘)。**逐表逐欄中英對照（augur 全 83 FinMind dataset＝`sync.daily_datasets()`+FRED、~650 真實欄、每表附 🔌 抓取方法[per-stock/by-date/by-dim-id/market/single-day]+📅 最早日期[實證:22 表 DB MIN、~57 表 wide-probe min(date)，如 Price 1994/財報 1991/Futures 1998/USStock 1990]、來源標 FM/金融、推定型別）＝正式參考 `docs/datasets_zh.md`（2026-06-15；含 8 個 datasets.md 未列表如 BuySellWide/AfterHours法人/DayTradingBorrowingFeeRate，經各 3 分鐘 API 驗證補入；FutOptTickInfo 即時類 /data 抓不到）；配套技術報告 `reports/augur_datasource_finmind_fred_20260615.md`（限流地圖/髒值目錄/vintage）**。

連結 [[augur_project_overview]] [[ingestion-strengthen-probe-not-enumerate]] [[data-source-consistency-proactive]]。

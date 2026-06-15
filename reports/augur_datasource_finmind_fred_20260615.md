# augur 資料源完整參考 — FinMind + FRED (2026-06-15)

**性質**：augur 兩大資料源的完整技術參考。**承接並更新** `augur_finmind_research_20260611.md` + `augur_fred_research_20260611.md`，併入本次 session 的關鍵實證（型別真相 / `/translation` 覆蓋 / 髒值目錄 / 限流地圖）+ FinMind 官方 `datasets.md` 全集 + live API 現況。

**來源標記（source-traceable #15）**：
`[datasets.md]`＝FinMind 官方 dataset 參考（`~/.claude/commands/finmind-references/datasets.md`）｜`[live 06-15]`＝本日 API 實打｜`[session]`＝本次對話 code/probe 實證｜`[06-11]`＝既有研究報告｜`[memory]`＝長期記憶。

---

## 0. 一頁總覽

| 面向 | FinMind | FRED |
|---|---|---|
| 內容 | 台股為主：價量 / 籌碼 / 基本面 / 衍生 / 可轉債 / 國際股 / 總經 | 美國・全球總經時間序列（~84.4 萬 series）|
| base URL | `https://api.finmindtrade.com/api/v4` | `https://api.stlouisfed.org/fred` |
| 認證 | Bearer token（個人訂閱）| api_key（32 字元，**免費**）|
| augur 額度 | **Sponsor 6000 req/hr** `[live 06-15]` | **120 req/min**（無 tier）|
| **到期** | ⏰ **2026-06-24（剩 ~9 天）** `[live 06-15]` | **無到期** |
| 欄位**型別**metadata | ❌ **完全無**（值全用字串回）`[session]` | ⚠️ 部分（series 有 units/frequency，但無 SQL 型別）|
| 欄位**中文說明** | ⚠️ 極稀疏（`/translation` 多空、且翻「值」非「欄」）`[session]` | ❌（英文 title 為主）|
| 最大陷阱 | **6/24 到期** + 髒值需型別降級 | **vintage 事後修訂 → look-ahead bias（#8）** |

**兩條操作鐵則**：
1. FinMind **sponsor-only** 資料（分點 / tick / snapshot / KBar / 可轉債 / 法人 by-date / 八大行庫…）須趕在 **2026-06-24** 前抓完；到期後降 Free（600/hr）抓不到。
2. FRED 總經值**會被事後修訂**；用「最新值」做歷史回測＝look-ahead（反 #8）；嚴格 PIT 須用 vintage（`realtime_start` / ALFRED）。

---

# Part A — FinMind

## A1. 概覽與認證
- **內容**：台股全市場為主 + 國際股 + 全球總經。資料偏「日頻批次」（非即時，除 Sponsor real-time snapshot）。
- **認證**：HTTP header `Authorization: Bearer {token}`（augur `finmind.py` 亦相容 query param `token=`）`[session]`。token 自助 reset（舊 token 立即失效、所有裝置登出）`[06-11]`。
- **status page**：`https://status.finmindtrade.com`（per-minute 錯誤率 >5% 視為 down）`[06-11]`。
- **官方文檔**：`https://finmindtrade.com/analysis/#/data/document`；AI agent 指引 = `FinMind/FinMind` repo 的 `.claude/commands/finmind.md` + `finmind-references/datasets.md`。

## A2. API 端點

| endpoint | method | 用途 | 關鍵參數 |
|---|---|---|---|
| `/data` | GET | 抓 dataset 資料（多數 dataset）| `dataset`(必), `data_id`, `start_date`, `end_date`（YYYY-MM-DD）|
| `/datalist` | GET | 列某 dataset 的 data_id 全集 | `dataset`（**僅 7 個總經類支援**，見 A6）|
| `/translation` | GET | 「欄位/值」中文對照（覆蓋稀疏，見 A7）| `dataset` |
| `/storage_objects` | GET | 整日全市場 parquet bulk 下載（Sponsor Pro）| `dataset`, `date`（忽略 data_id）|
| `v2/user_info` | GET | tier / 額度 / 到期查詢（**讀錶不計額度** `[memory]`）| URL=`https://api.web.finmindtrade.com/v2/user_info`，Bearer |
| dedicated | GET | `/taiwan_stock_trading_daily_report`、`..._secid_agg`、`taiwan_*_snapshot` | 分點 / 券商聚合 / real-time 專屬（非 `/data`）|

- **回應格式**：`{"msg","status","data":[...]}`——**只有資料列、無 schema/型別欄** `[session]`。
- 官方標準用法（`finmind.md`）：`pd.DataFrame(resp.json()["data"])` ← **靠 pandas 從值推型別**，與 augur 同理。

## A3. Tier 體系與限速

| Tier | 限速 | 解鎖 |
|---|---|---|
| Free（無 token）| 300 req/hr | 基本 dataset、單股需 data_id |
| Free（有 token）| 600 req/hr | free dataset |
| Backer | 1,600/hr | + by-date 全市場、tick、可轉債、CnnFearGreed… |
| **Sponsor（augur 現用）** | **6,000/hr** | **全部** + real-time snapshot + 分鐘 K + bulk parquet |
| SponsorPro | 20,000/hr | + 整日全市場 parquet（SDK `use_object`）|

- **配額超限**：HTTP **402**（`"Requests reach the upper limit."`）`[06-11]`。
- **部分 dataset `Free(w/ data_id)`**：免費需逐股 data_id、**Backer+ 才可 by-date 全市場**（augur sponsor 可 by-date，省 request）。

### ⭐ 限流操作地圖（本 session + 06-12 實證 `[session][memory]`）
1. **額度＝rolling 視窗**，非整點清零：零 call 期間錶仍連續下退；`[live 06-15]` 停 sync 後 user_count 仍 4993（緩慢洩流）。→ **配額一律問錶（`/user_info`），不本地推算**。
2. **兩種 403**：(a) **額度型**（錶滿，`_quota_gate` 可預防）；(b) **IP sustained 型**（持續高負載觸發，曾 8/6000 也被降速）→ 只能保守步調 + 休養。
3. **重試風暴是惡化路徑**：撞 403 後高併發短退避反覆重試 → 錶永遠滿不自癒。教訓：見訊號即停，勿續衝。
4. augur 三層防護（`finmind.py`）：`_pace()` 最小間隔 → `_quota_gate()` 閉環問錶（≥5800 主動暫停、退到 ≤2900 自動續）→ `403` 固定冷卻 `QUOTA_COOLDOWN`（不短退避反覆撞）。

## A4. token 現況（live probe `[2026-06-15]`）
```
level=3  level_title=Sponsor   api_request_limit_hour=6000
SponsorInfo: begin 2026-04-24  →  expired 2026-06-24   （剩 ~9 天）
user_id=tsaitsangchi  email_verify=true   user_count(當下錶)=4993
```
⇒ augur 現可抓**全部** dataset（含 sponsor-only）。**6-24 後降 Free**：sponsor-only 全史**抓不到** → 全市場全史 sync 須在到期前完成。

## A5. Dataset 全集（9 大類，from `[datasets.md]`；年份/tier 註記併 `[06-11]`）

> tier：F=Free、F(id)=Free(w/ data_id)、B=Backer、S=Sponsor。augur(Sponsor) 全可抓。

**技術面（20）**：TaiwanStockInfo[F] · …WithWarrant[F] · …WithWarrantSummary[S] · TradingDate[F] · **Price[F(id) 1994]** · **PriceAdj[F(id)]** · PriceTick[B 2019 單日] · **PER[F 2005]** · StatisticsOfOrderBookAndTrade[F 5秒單日] · VariousIndicators5Seconds[F] · DayTrading[F(id) 2014] · **TotalReturnIndex[F id=TAIEX/TPEx]** · 10Year[B] · KBar[S 分鐘單日] · Week/MonthPrice[B 2000] · Every5SecondsIndex[B] · Suspended[B] · DayTradingSuspension[B] · PriceLimit[F(id) 2000]

**籌碼面（16）**：**MarginPurchaseShortSale[F(id) 2001]** · TotalMargin…[F] · **InstitutionalInvestorsBuySell[F(id) 2005]** · TotalInstitutional[F 2004] · **Shareholding[F(id) 2004]** · HoldingSharesPer[B 2010] · **SecuritiesLending[F(id) 2001]** · MarginShortSaleSuspension[F(id)] · **DailyShortSaleBalances[F(id) 2005]** · SecuritiesTraderInfo[F] · TradingDailyReport[S 分點/單日/dedicated] · WarrantTradingDailyReport[S dedicated] · **GovernmentBankBuySell[S 2021 八大行庫]** · TotalExchangeMarginMaintenance[B] · TradingDailyReportSecIdAgg[S dedicated] · DispositionSecuritiesPeriod[B] · BlockTrade[S 2005] · LoanCollateralBalance[S 37 欄]

**基本面（12）**：**FinancialStatements[F(id) 1990 損益表]** · **BalanceSheet[F(id) 2011]** · **CashFlowsStatement[F(id) 2008]** · Dividend[F(id) 2005] · DividendResult[F(id) 2003] · **MonthRevenue[F(id) 2002]** · CapitalReductionReferencePrice[F per-stock 稀疏] · MarketValue[B 2004] · Delisting[F] · MarketValueWeight[B 2024] · SplitPrice[F] · ParValueChange[F]
> 財報三表結構：`date, stock_id, type, value, origin_name`——**長表**（`type`＝會計科目、`value`＝金額）；最新季常含未定案重述。

**衍生品（16）**：**FuturesDaily[F(id) 1998 id=TX…]** · **OptionDaily[F(id) 2001 id=TXO…]** · Futures/OptionTick[B 2011 單日] · Futures/OptionInstitutionalInvestors[F(id) 2018] · …AfterHours[B 2021] · **Futures/OptionDealerTradingVolumeDaily[F 2021]** · …OpenInterestLargeTraders[B] · FuturesSpreadTrading[B 2007] · **Futures/OptionFinalSettlementPrice[B]**
> ⚠️ `contract_date` / `contract_month` 欄混「純契約月(200712)」與「價差(200710/200711)」「週合約(201211W4/202101W1)」→ 見 A8。

**即時（4，皆 S）**：taiwan_stock_tick_snapshot（data_id=4碼股 或 3碼指數，**91 指數**見 `[datasets.md]` IndexCodes）· TaiwanFutOptTickInfo[F] · taiwan_futures_snapshot · taiwan_options_snapshot

**可轉債（4，B/S，2020-）**：ConvertibleBondInfo · Daily · InstitutionalInvestors · **DailyOverview**（日期含 `1911-00-00` 髒值，見 A8）

**其他（3）**：**TaiwanStockNews[F 單日型 end_date 須 none]** · BusinessIndicator[B 1982 月] · IndustryChain[B]

**國際股（9，皆 F）**：US/UK/Europe/Japan **StockInfo + StockPrice** · USStockPriceMinute[B]
> ⚠️ USStockPrice 寬窗批含 `stock_id=null` 髒列（1997-09-30 指數彙總行）→ augur 改 by-dimension-id 逐 ticker，見 A8。

**全球總經（6，皆 F）**：**TaiwanExchangeRate[18-19 幣別]** · **InterestRate[12 央行 FED/ECB/BOJ…]** · GoldPrice · **CrudeOilPrices[WTI/Brent]** · **GovernmentBondsYield[美債 13 期別 1M~30Y]** · CnnFearGreedIndex[B 2011]

> 完整逐欄清單見 `~/.claude/commands/finmind-references/datasets.md`（FinMind 官方）。

## A6. data_id 全集來源階層（#18 — 權威來源、非臆測白名單）`[06-11]`

| 維度類型 | 權威來源 | 例 |
|---|---|---|
| 總經/全球（7 dataset）| **`/datalist` API**（動態最完整）| GovernmentBondsYield→13 期別；(Taiwan)ExchangeRate→幣別；InterestRate→央行；CrudeOilPrices→WTI/Brent |
| per-stock | **roster**（TaiwanStockInfo 全股名冊）| Price / 財報 / 籌碼… |
| 期/權契約 | **`/datalist`**（contract codes）| FuturesDaily=TX/MTX…、OptionDaily=TXO… |
| 指數（snapshot）| 91 個 3 碼指數碼（IndexCodes 頁）| tick_snapshot |
| 報酬指數 | 官方文檔 + probe（無 datalist）| TotalReturnIndex=TAIEX/TPEx |

- **`/datalist` 僅支援 7 總經類**：CrudeOilPrices, CurrencyCirculation, ExchangeRate, GovernmentBondsYield, GovernmentBonds, InterestRate, TaiwanExchangeRate。
- **實證 `/datalist` > 靜態文檔**：GovBonds `/datalist`=13 期別、文檔僅 12（漏 4-Month）→ 一律問 API、不抄文檔。

## A7. ⭐ Schema / 型別真相（本 session 核心實證 `[session]`）

> **回答「FinMind 有沒有給每欄的型態 / 大小 / 中文說明？」→ 否，三者皆無或極稀疏。**

| 項目 | FinMind 提供？ | 實證 |
|---|---|---|
| **型態（type）** | ❌ **完全無** | `/data` 回應 top-level 僅 `msg/status/data`；值**全是字串**（probe `contract_date`：`'200710'`、`'200710/200711'` 皆 `str`）；datasets.md 只列欄「名」；官方範例用 pandas 推 |
| **大小（size）** | ❌ **完全無** | 無型別即無長度/精度；datasets.md 無任何 `VARCHAR(n)`/`NUMERIC(p,s)` |
| **中文說明（逐欄）** | ⚠️ **極稀疏，且多翻「值」非「欄」** | `/translation` 探 10 dataset：Price/Futures/Gold/Info/MonthRevenue/PER/GovBonds **全空**；BalanceSheet/USStock/法人 回 dict＝翻「科目值/指數名/法人別」（應付帳款、道瓊指數、自營商）非欄位說明。augur DB 現 209 欄僅 **55 欄(26%)** 有註解 |

**結論**：欄位「定型別 + 中文」**無可避免是落地端的工作**。augur 以 `generic_schema` **從觀測值推導型別 + 撞牆降級**（#2 API 值域即事實），中文則盡量補 `/translation` 有的部分。**這份「清楚 catalog」FinMind 不提供，須由 augur 自真實資料 + 稀疏來源組出**。

## A8. ⭐ 資料品質陷阱目錄（髒值 → 舊碼爆 → 新碼解；本 session 實證 `[session]`）

| dataset | 髒值樣本 | 落地端問題 | 解法（現行碼已驗證）|
|---|---|---|---|
| TaiwanFuturesDaily | `contract_date='200710/200711'`（價差）| 早期樣本像數字→推 NUMERIC→塞不進 | `ensure_table` 跨型別降級 NUMERIC→VARCHAR `USING trim_scale::text` |
| TaiwanOptionDaily | `contract_date='201211W4'`（週選）| 同上 | 同上 |
| TaiwanFuturesFinalSettlementPrice | `contract_month='202101W1'` | 同上 | 同上 |
| TaiwanStockSecuritiesLending | `return_date='-1'`（哨兵）| `-1` 推 NUMERIC、撞 DATE 欄 | 跨型別降級 DATE→VARCHAR |
| TaiwanStockConvertibleBondDailyOverview | 日期 `'1911-00-00'`（不存在）| 格式合法值非法、撞 DATE cast | `_is_date` 加 `date.fromisoformat` 合法性驗 → 非法存字串 |
| USStockPrice | `stock_id=null`（1997-09-30 指數彙總行）| 撞 NOT NULL PK | market 撞 IntegrityError → 自動轉 **by-dimension-id** 逐 ticker（每列必有 id）|
| GovernmentBankBuySell / 法人 | （非髒值）寬 PK 數值欄 / by-date 含權證 | 對帳 false-negative（非資料壞）| reconcile `_key→_norm` + roster-scoped |

**端到端實證**（臨時表跑 `infer→ensure_table→INSERT`，驗完 DROP）：5 個確切髒值**全部照抓照存、不再爆、值忠實**；39 單元測試 passed。

## A9. 特殊抓取模式（augur 須處理）`[06-11]`
1. **單日型**（size-too-large、`end_date` 須 none）：TaiwanStockNews、tick、snapshot、5 秒統計 → 逐日不帶 end（`finmind.fetch` 自動相容）。
2. **bulk parquet（Sponsor Pro）**：`/storage_objects?dataset&date` 整日下載（tick/KBar）——大表高效路徑（augur 為 Sponsor 非 Pro，且 #4 排除 intraday）。
3. **dedicated endpoints（Sponsor）**：分點/券商聚合/snapshot 走專屬 URL。
4. **by-date vs per-stock**：sponsor 可 by-date 全市場（省 request）；per-stock 全史 ~3100 calls，by-date 全史 ~交易日數。

## A10. ⭐ anti-leakage 金礦（#8；公告時點欄位 `[memory]`）
FinMind 少數 dataset **自帶官方公告時點欄**（＝零洩漏的 as-of 時戳，建模可直接當「可見日」）：
- `TaiwanStockDividend.AnnouncementDate`（公告日）＝最乾淨。
- `MonthRevenue.create_time`、`Shareholding.RecentlyDeclareDate`（疑 as-of，**待實證**）。
- 財報三表**無公告欄** → 須以法定申報期限 lag（季報 +45 天等）。
- 規則：有公告欄就用公告欄當可見時點；無則保守 lag。**絕不**用「資料 date」當可見日（那是事件發生日、非公開日）。

## A11. augur 對接設計（`finmind.py` + `generic_schema.py` + `sync.py`）`[session]`
- **auto-schema**：`infer_schema`（值推型別）→ `ensure_table`（建表/補欄/auto-widen/跨型別降級）→ `detect_keys`（PK，by-date 加 `require=('date',)` 防塌鍵）。
- **adaptive fetch**（`sync_finmind_dataset`）：market 寬窗探測 → 空則 canonical 2330 判 per-stock → by-date 試 → 退 by-dimension-id（Info roster）→ 逐股 fallback。
- **三層限速**（A3）；**resume-safe**：每 dataset/股從 DB `max(date)` 續 + `ON CONFLICT` 冪等。
- **#7 對帳**（`reconcile.py`）：DB↔API byte 比對（`_key`/`_norm` 正規化、per-stock roster-scoped、季頻排除未定案窗）。

---

# Part B — FRED（Federal Reserve Economic Data, St. Louis Fed）

## B1. 概覽與認證 `[06-11]`
- **內容**：美國/全球總經時間序列（殖利率曲線、利率、通膨、失業、工業生產、匯率、油價、信用利差…），augur 第二資料源（總經因子）。
- **api_key**：32 字元小寫英數，**免費註冊**（`fred.stlouisfed.org/docs/api/api_key.html`）；augur 用 `config.FRED_API_KEY`。
- **無 tier 分級、無訂閱到期**——公開政府資料、全免費全可取（與 FinMind 6/24 到期截然不同）。

## B2. API 端點（base `https://api.stlouisfed.org/fred`）`[06-11]`

| endpoint | 用途 | 關鍵參數 |
|---|---|---|
| `/series` | series metadata（標題/頻率/單位/季調/起訖）| `series_id` |
| `/series/observations` | **觀測值（augur 抓取用）** | `series_id`, `observation_start/end`, **`realtime_start/end`（#8 PIT/vintage）**, `units`, `frequency`, `aggregation_method`, `limit`(≤100000) |
| `/series/search` | 依關鍵字搜尋 series（series-id 來源）| `search_text`, `limit`, `order_by` |
| `/series/vintagedates` | 該 series 歷史修訂日（vintage）| `series_id` |
| `/category` `/category/children` `/category/series` | 類別階層瀏覽 + 列該類 series | `category_id`（root=0）|
| `/releases` `/release/series` | 發布（~328）+ 該發布 series | — |
| `/sources` `/source/releases` | 資料來源（~120）| — |
| `/tags` `/series/search/tags` | 非階層 metadata 標籤 | — |

- 約 **31 endpoints / 5 大類**（Category / Release / Series / Source / Tag）+ GeoFRED（地圖，另一 API）。`file_type=json|xml`。
- augur 抓取用 `/series/observations`；#18 列舉用 `/series/search` + `/category/series`。

## B3. 限速與涵蓋 `[06-11]`
- **限速**：**120 req/min（=7200/hr）**；超限 **HTTP 429**（`fred.py` 已退避重試）。
- **涵蓋**：~**844,000 series**、~120 sources、~328 releases、8 大類 / 80 子類。長歷史（DGS10 自 **1962-01-02**）。
- 8 大類（`category/children?category_id=0`）：Money/Banking/Finance、Population/Employment/Labor、National Accounts、Production/Business、Prices、International、U.S. Regional、Academic。

## B4. series 結構 `[06-11]`
- **metadata（`/series`）**：`id, title, frequency`(Daily/Weekly/Monthly…), `units`(Percent…), `seasonal_adjustment`, `observation_start/end`。← **有頻率/單位，但仍非 SQL 型別**。
- **observations（`/series/observations`）**：每列 `realtime_start, realtime_end, date, value`；**缺值 `value="."`**。
- **augur `fred.py` 落地**：只取 `(series_id, date, value)`——**補 `series_id`**（FRED 回應不含 → 補後成 `(series_id,date)` 複合 PK #2）；**丟 `realtime_start/end`**（vintage metadata、隨查詢日變、存了破壞冪等對帳）；**`"."`→NULL**。

## B5. series-id 來源（#18，對映 FinMind `/datalist`）`[06-11]`
- `/series/search?search_text=`：關鍵字搜尋（實證「10-year treasury constant maturity」→ 79 series）。
- `/category/series?category_id=` + `/category/children`：類別階層展開。
- augur 現選 **12 個標準總經因子**（`FRED_SERIES`，feature 設計決定、非窮舉 844K）：
  `T10Y2Y, T10Y3M, DGS10, DGS2, FEDFUNDS, UNRATE, CPIAUCSL, INDPRO, VIXCLS, DTWEXBGS, DCOILWTICO, BAMLH0A0HYM2`
  （殖利率曲線斜率 ×2 / 10Y・2Y 利率 / 聯邦基金利率 / 失業率 / CPI / 工業生產 / VIX / 美元指數 / WTI 油 / 高收益信用利差）。

## B6. ⭐ vintage / look-ahead（FRED 最關鍵課題 #8）`[06-11][memory]`
- **FRED 總經數據事後修訂頻繁**（GDP/CPI/就業常回溯重編）；用「最新修訂值」做歷史回測 ＝ **look-ahead bias**（當時根本看不到該值）。
- **FRED 原生支援 point-in-time（ALFRED）**：
  - `/series/vintagedates?series_id=`：取某 series 全部修訂日。
  - `/series/observations?realtime_start=YYYY-MM-DD&realtime_end=…`：取「**該日當時可見值**」。
- augur 現況：只存最新值（去 realtime）守冪等——**建模若要嚴格 PIT，須評估改抓 vintage**（此為 augur 建模階段必正視的 anti-leakage 課題）。
- 另：FRED 原生 `units`(差分/變化率) + `frequency`+`aggregation_method`(降頻)，特徵可善用、但對映關係須記錄防 #8。

## B7. augur 對接（`src/augur/ingestion/fred.py`）`[06-11]`
- 薄 client：`fetch(series_id, start_date, end_date)` → `/series/observations`；429 退避；api_key/series_id 錯 → 立即 `FredError`。
- **無主動節流**（120/min 寬鬆 + 僅 12 series）；未來放量列舉須補節流。
- resume：`sync_fred` 每 series 從 DB `max(date)` 續（#6）。

---

# Part C — 對 augur 的意涵與行動

1. **⏰ 6/24 到期是硬約束**：FinMind sponsor-only（分點/tick/snapshot/KBar/可轉債/法人 by-date/八大行庫）須**優先趕在到期前抓全史**；FRED 無此壓力、可從容。
2. **schema metadata 須 augur 自建**：型別/大小靠 `generic_schema` 推導（source-traceable、比抄文檔可靠 #2）；中文補 `/translation` 有的部分 + 缺者誠實標「無官方中文」。→ 可產一份「82 表逐欄：型態/大小/中文（含來源）」catalog。
3. **髒值已斷根**：A8 六類 exception 新碼已驗證解決，重抓不再爆（照抓照存就過）。
4. **對帳是誠實保證非雜訊**：新碼 reconcile（`_norm`/roster-scoped）下，多數 FAIL 轉 PASS；殘餘屬真實特性（還原價回溯/季頻未定案/vintage）須人判、非 bug。
5. **anti-leakage 紀律**：FinMind 用公告時點欄（A10）、FRED 用 vintage（B6）——兩源皆有原生 PIT 解法，建模階段必落實（#8）。

---

**附**：本報告承接 `augur_finmind_research_20260611.md` / `augur_fred_research_20260611.md`（兩者仍有效，本份為合併更新 + session 實證增補）。FinMind 官方逐欄清單見 `~/.claude/commands/finmind-references/datasets.md`。

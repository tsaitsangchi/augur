# augur 資料表完整清單：可抓取 vs 需排除 (2026-06-11)

**用途**：完整條列 augur 通用 ingester 之全部 dataset，依 **v1.4.0 doctrine** 分為「可抓取」與「需排除」，附中文說明。
**來源（#15 source-traceable）**：
- 中文說明 + 分類：`reports/augur_finmind_fred_table_schema_20260609.md`（FinMind 92 dataset：A 台股/總經 55 + B 期權期貨 16 + C 非台股 13 + D intraday 8）。
- 維度/抓取方式 + live 驗證：`reports/augur_generic_ingester_schema_catalog_20260610.md`（93 enum、live 取樣成功 80 表 + FRED）。
- 排除清單：`src/augur/ingestion/ingest.py`（`INTRADAY` #4 + `OUT_OF_UNIT` #3）。
- 分類準則：**v1.4.0**——唯一資料本質排除＝#4 日為最小單位；`OUT_OF_UNIT`＝規模物理不可行之 operational 暫緩（非治權排除，待補多維度抓取 #18）。

---

## 總覽

| 類別 | 數 | 性質 |
|---|---|---|
| FinMind 全集（`list_datasets` enum） | 93（finmind_fred 口徑 92） | live 動態列舉、無白名單（#3） |
| **可抓取**（日級真兆，augur 該抓） | **81 FinMind + FRED** | A 台股 52 + B 期權期貨 16 + C 非台股 13 + `fred_series` |
| └ 其中 live 取樣已成功 | 80 FinMind + FRED | 2 sponsor-tier 回 200-空（`ExchangeRate` 全球匯率 / `GovernmentBondsYield`） |
| **需排除①：真排除**（#4 intraday <日） | **8** | 資料本質排除（唯一準則） |
| **需排除②：operational 暫緩**（#3 規模不可行） | **3** | 非治權排除，待補 by-維度-id 抓取 |
| infra log（explicit DDL、非 API 推導） | 2 | `pipeline_execution_log` / `data_audit_log`（PHASE 1 bootstrap） |

> v1.4.0 關鍵：B 期權期貨 / C 非台股 **不是排除**——它們是有價值之日級情境/特徵輸入，僅因需特殊維度 id（`futures_id`/`option_id`/ticker/`name`…）而 **sync 待落地通用多維度抓取**（目前 code 僅 market/per-stock/by-date 三模式）。

---

## 一、可抓取 tables（依 v1.4.0「凡 API 日級真兆皆抓」）

### A. 台股 / 總經（52）— 多數 sync 已能抓（market / per-stock / by-date）

| dataset | 中文 |
|---|---|
| `TaiwanStockPrice` | 台股日成交價量 |
| `TaiwanStockPriceAdj` | 台股日成交價量（還原權值）|
| `TaiwanStockMonthPrice` | 台股月成交價 |
| `TaiwanStockWeekPrice` | 台股週成交價 |
| `TaiwanStock10Year` | 近十年還原股價 |
| `TaiwanStockPriceLimit` | 漲跌停參考價 |
| `TaiwanStockInstitutionalInvestorsBuySell` | 個股三大法人買賣超 |
| `TaiwanStockTotalInstitutionalInvestors` | 全市場三大法人買賣超 |
| `TaiwanStockGovernmentBankBuySell` | 八大行庫買賣超 |
| `TaiwanStockShareholding` | 外資持股 |
| `TaiwanStockHoldingSharesPer` | 集保戶股權分散（持股級距）|
| `TaiwanStockMarginPurchaseShortSale` | 個股融資融券 |
| `TaiwanStockTotalMarginPurchaseShortSale` | 全市場融資融券 |
| `TaiwanDailyShortSaleBalances` | 融券+借券賣出餘額 |
| `TaiwanStockSecuritiesLending` | 借券成交明細 |
| `TaiwanStockMarginShortSaleSuspension` | 暫停融券 |
| `TaiwanStockLoanCollateralBalance` | 融資融券+借券擔保品餘額（全項）|
| `TaiwanTotalExchangeMarginMaintenance` | 全市場整戶維持率 |
| `TaiwanStockBalanceSheet` | 資產負債表（長格式）|
| `TaiwanStockFinancialStatements` | 綜合損益表（長格式）|
| `TaiwanStockCashFlowsStatement` | 現金流量表（長格式）|
| `TaiwanStockMonthRevenue` | 月營收 |
| `TaiwanStockPER` | 本益比/股價淨值比/殖利率 |
| `TaiwanStockMarketValue` | 個股市值 |
| `TaiwanStockMarketValueWeight` | 市值權重（成分股）|
| `TaiwanStockDividend` | 股利政策（宣告）|
| `TaiwanStockDividendResult` | 除權息結果 ⚠待落地（探測死點誤判，修起點即歸 per-stock）|
| `TaiwanStockCapitalReductionReferencePrice` | 減資參考價 |
| `TaiwanStockSplitPrice` | 股票面額/分割參考價 |
| `TaiwanStockParValueChange` | 面額變更 |
| `TaiwanStockInfo` | 股票基本資訊（名冊）|
| `TaiwanStockInfoWithWarrant` | 股票基本資訊（含權證）|
| `TaiwanStockInfoWithWarrantSummary` | 權證基本資訊彙總 |
| `TaiwanSecuritiesTraderInfo` | 證券商基本資訊 |
| `TaiwanStockDelisting` | 下市 |
| `TaiwanStockSuspended` | 暫停交易 |
| `TaiwanStockDispositionSecuritiesPeriod` | 處置股票期間 |
| `TaiwanStockDayTrading` | 個股當沖 |
| `TaiwanStockDayTradingSuspension` | 暫停當沖 |
| `TaiwanStockDayTradingBorrowingFeeRate` | 當沖借券費率 |
| `TaiwanStockIndustryChain` | 產業鏈分類 |
| `TaiwanStockTradingDate` | 交易日曆 |
| `TaiwanStockTotalReturnIndex` | 加權報酬指數（需 data_id=TAIEX）|
| `TaiwanStockNews` | 個股新聞 ⚠待落地（探測死點誤判）|
| `TaiwanBusinessIndicator` | 台灣景氣指標（領先/同時/落後/燈號）|
| `TaiwanExchangeRate` | 台銀牌告匯率 |
| `CnnFearGreedIndex` | CNN 恐懼貪婪指數 |
| `TaiwanStockConvertibleBondDaily` | 可轉債日成交 ⚠待落地（`cb_id` 維度）|
| `TaiwanStockConvertibleBondDailyOverview` | 可轉債每日總覽（條款）⚠待落地 |
| `TaiwanStockConvertibleBondInstitutionalInvestors` | 可轉債三大法人 ⚠待落地 |
| `TaiwanStockConvertibleBondInfo` | 可轉債基本資訊 ⚠待落地 |
| `TaiwanStockBlockTrade` | 鉅額交易（彙總，by-date）|

### B. 期權期貨（16）— v1.4.0 該抓、**sync 待落地 by-維度-id**（`futures_id`/`option_id`）

| dataset | 中文 |
|---|---|
| `TaiwanFuturesDaily` | 期貨日成交 |
| `TaiwanOptionDaily` | 選擇權日成交 |
| `TaiwanFutOptTickInfo` | 期權契約資訊（非 tick 資料）|
| `TaiwanFutOptDailyInfo` | 期權每日契約資訊 |
| `TaiwanFutOptInstitutionalInvestors` | 期權三大法人 |
| `TaiwanFuturesInstitutionalInvestors` | 期貨三大法人 |
| `TaiwanOptionInstitutionalInvestors` | 選擇權三大法人 |
| `TaiwanFuturesInstitutionalInvestorsAfterHours` | 期貨三大法人（盤後）|
| `TaiwanOptionInstitutionalInvestorsAfterHours` | 選擇權三大法人（盤後）|
| `TaiwanFuturesDealerTradingVolumeDaily` | 期貨自營商成交量 |
| `TaiwanOptionDealerTradingVolumeDaily` | 選擇權自營商成交量 |
| `TaiwanFuturesOpenInterestLargeTraders` | 期貨大額交易人未平倉 |
| `TaiwanOptionOpenInterestLargeTraders` | 選擇權大額交易人未平倉 |
| `TaiwanFuturesSpreadTrading` | 期貨價差交易 |
| `TaiwanFuturesFinalSettlementPrice` | 期貨最後結算價 |
| `TaiwanOptionFinalSettlementPrice` | 選擇權最後結算價 |

### C. 非台股 海外/商品/匯率/利率（13）— v1.4.0 該抓、**待落地 by-維度-id**（ticker/`name`/`currency`/`country`）

| dataset | 中文 |
|---|---|
| `USStockPrice` | 美股日價（⚠ PK 異常 stock_id 不在 PK，待修）|
| `USStockInfo` | 美股基本資訊 |
| `JapanStockPrice` | 日股日價 |
| `JapanStockInfo` | 日股基本資訊 |
| `UKStockPrice` | 英股日價 |
| `UKStockInfo` | 英股基本資訊 |
| `EuropeStockPrice` | 歐股日價 |
| `EuropeStockInfo` | 歐股基本資訊 |
| `CrudeOilPrices` | 原油價格（`name`：WTI/Brent；FRED DCOILWTICO 另有）|
| `GoldPrice` | 黃金價格 |
| `InterestRate` | 各國基準利率（`country`；FRED 另有）|
| `ExchangeRate` | 全球匯率（sponsor-tier，live 取樣回 200-空）|
| `GovernmentBondsYield` | 公債殖利率（sponsor-tier，回 200-空）|

### FRED（另一條 API 入口，非 FinMind ingester）

| 表 | 中文 |
|---|---|
| `fred_series` | 總經觀測值（`series_id, date, value`；augur 自選 12 macro series：T10Y2Y/DGS10/UNRATE/CPIAUCSL…）|

---

## 二、需排除 tables

### ① 真排除 — #4 日為最小單位（**唯一資料本質排除準則**）（8）
< 日之 intraday，違反系統時間本質；`ingest.is_intraday()` 守門拒絕入庫。

| dataset | 中文（依名稱 + ingest.py 註解「5秒/tick/分K/分鐘」）|
|---|---|
| `TaiwanStockPriceTick` | 台股逐筆成交（tick）|
| `TaiwanStockKBar` | 台股 K 線（分鐘級）|
| `TaiwanFuturesTick` | 期貨逐筆（tick）|
| `TaiwanOptionTick` | 選擇權逐筆（tick）|
| `TaiwanStockStatisticsOfOrderBookAndTrade` | 委託簿與成交統計（盤中）|
| `TaiwanVariousIndicators5Seconds` | 各項指標（5 秒）|
| `USStockPriceMinute` | 美股分鐘價 |
| `TaiwanStockEvery5SecondsIndex` | 大盤每 5 秒指數 |

### ② operational 暫緩 — #3 `OUT_OF_UNIT`（規模物理不可行，**非治權排除**，待補多維度抓取）（3）
資料維度合格（日級）；僅因 FinMind 限「單 id × 單日」查、規模物理不可行而暫緩，待有能力補通用多維度抓取再抓。

| dataset | 中文 | 暫緩理由（2026-06-10 實證規模）|
|---|---|---|
| `TaiwanStockTradingDailyReport` | 券商分點進出日報 | 券商×股×日 sub-stock；單股×單日 only × 3100 股 = 數十億列 |
| `TaiwanStockWarrantTradingDailyReport` | 權證每日交易（分點）| 權證宇宙 126,368 檔 |
| `TaiwanStockBlockTradingDailyReport` | 鉅額交易日報（分點）| 稀疏 → backward-probe 取樣多落空、難可靠定起點 |

---

## 三、v1.4.0 doctrine 註記

- **唯一資料本質排除 = #4 日為最小單位**：只有 ① intraday（8）是治權排除。
- **② `OUT_OF_UNIT`（3）非排除、是 operational 暫緩**：待 sync 補通用多維度抓取後可納。
- **B/C 共 29 表待落地 by-維度-id**：v1.4.0 已不排除，但 sync 目前僅 market/per-stock/by-date；需補「探測主 id 維度 + 由 Info/metadata 通用列舉 id」（仍無 hardcoded 白名單）。canonical-probe 的 `full_start=1990` 死點亦待修（致 `TaiwanStockNews`/`TaiwanStockDividendResult` 誤判，雖其為 per-stock 可抓）。
- **2 sponsor-tier 空**（`ExchangeRate` 全球 / `GovernmentBondsYield`）：live 取樣回 200-空，疑 tier 不含；總經已由 FRED 涵蓋。
- **本機 DB 現況**：以實查為準（DB 不隨 git、跨機獨立）。

> 一句話：**真排除只有「<日」8 張 intraday；其餘 81 FinMind + FRED 皆 augur 該抓的日級真兆，差別僅在「sync 已能抓」或「待落地 by-維度-id」。**

# FinMind 資料源完整研究 (2026-06-11)

augur 主資料源（FinMind）全貌——API endpoints / tier 體系 / dataset 全集 / data_id 來源階層 / augur token 實況。
**source-traceable（#15）**：finmindtrade.com 官網 + finmind.github.io 文檔（含 AgentSkill / llms-full.txt）+ `/datalist`、`/user_info` live probe。

---

## 一、API Endpoints（base：`https://api.finmindtrade.com/api/v4`）

| endpoint | method | 用途 | 關鍵參數 |
|---|---|---|---|
| `/data` | GET | 抓 dataset 資料 | `dataset`(必), `data_id`, `start_date`, `end_date`（YYYY-MM-DD）|
| `/datalist` | GET | **列某 dataset 的 data_id 全集** | `dataset`（僅 7 個總經類支援，見五）|
| `/translation` | GET | 欄位中英對照 | `dataset` |
| `/login` | POST | 取 token | `user_id`, `password` |
| `/storage_objects` | GET | 整日 parquet bulk 下載（Sponsor）| `dataset`, `date`（忽略 data_id）|
| user_info | GET | tier / 配額查詢 | URL=`https://api.web.finmindtrade.com/v2/user_info`、header `Authorization: Bearer {token}` |
| dedicated（Sponsor）| GET | `/taiwan_stock_trading_daily_report`、`..._secid_agg` | 分點/券商專用 |

- **認證**：header `Authorization: Bearer {token}`；token reset 自助（舊 token 立即失效、所有裝置登出）。
- **status page**：https://status.finmindtrade.com（per-minute 錯誤率，>5% 算 down）。
- **API schema**：https://finmindtrade.com/analysis/#/data/document

## 二、Tier 體系與限速

| Tier | 限速 | 解鎖 |
|---|---|---|
| Free（無 token）| 300 req/hr | 基本 dataset、單股需 data_id |
| Free（有 token）| 600 req/hr | free dataset |
| Backer | **1,600/hr** | + by-date 全市場、tick、可轉債、CnnFearGreed… |
| **Sponsor**（augur 現用）| **6,000/hr** | **全部** + real-time snapshot + 分鐘 K + bulk parquet |
| SponsorPro | **20,000/hr** | + 整日全市場 parquet（SDK `use_object`，tick/KBar 免逐檔）|

- **配額超限**：HTTP **402** `"Requests reach the upper limit."`（對齊 finmind.py `_RETRY_STATUS` 含 402）。
- 部分 dataset `[Free/Backer/Sponsor]`：free 需 data_id（逐股）、**Backer+ 才可 by-date 全市場**（解釋 dry-run 多數 TaiwanStock* 落 per-stock）。

## 三、augur token 實況（live probe #15，2026-06-11）

- **level 3 / `Sponsor`**、`api_request_limit_hour` = **6000**、今日 `user_count` = 2826。
- **SponsorInfo：2026-04-24 ~ `2026-06-24` 到期**、user_id `tsaitsangchi`、email_verified。
- ⇒ **augur 能抓全部 dataset**（含 sponsor-only）；先前「sponsor-tier 抓不到」推測作廢。
- ⚠️ **到期約束**：2026-06-24 後降 free（600/hr）→ sponsor-only（分點/tick/snapshot/KBar/可轉債/法人 by-date…）抓不到。**全市場全史 sync 須趕在到期前完成**。

## 四、Dataset 全集（~75+，分類 / tier / data_id / 起始年）

**技術面（~20）**：TaiwanStockInfo[F]、…WithWarrant[F]、…WithWarrantSummary[S]、TradingDate[F]、Price[F/B/S 1994、free 需 data_id、B+ by-date]、PriceAdj[F/B/S]、PriceTick[B/S 2019 單日]、PER[F 2005]、StatisticsOfOrderBookAndTrade[F 5秒單日]、VariousIndicators5Seconds[F]、DayTrading[F/B/S 2014]、**TotalReturnIndex[F、data_id=TAIEX/TPEx]**、10Year[B/S]、KBar[S 分鐘]、Week/MonthPrice[B/S 2000]、Every5SecondsIndex[B/S]、Suspended[B/S]、DayTradingSuspension[B/S]、PriceLimit[F/B/S 2000]。
**籌碼面（~19）**：MarginPurchaseShortSale[F/B/S 2001]、TotalMargin…[F]、InstitutionalInvestorsBuySell[F/B/S 2005]、TotalInstitutional[F 2004]、Shareholding[F/B/S 2004]、HoldingSharesPer[B/S 2010]、SecuritiesLending[F/B/S 2001]、MarginShortSaleSuspension[F/B/S]、DailyShortSaleBalances[F/B/S 2005]、SecuritiesTraderInfo[F]、TradingDailyReport[S 2021 分點/單日/parquet]、WarrantTradingDailyReport[S]、**GovernmentBankBuySell[S 2021]**、TotalExchangeMarginMaintenance[B/S]、TradingDailyReportSecIdAgg[S]、BlockTradingDailyReport[S]、BlockTrade[S 2005]、LoanCollateralBalance[S]、DispositionSecuritiesPeriod[B/S]、DayTradingBorrowingFeeRate[B/S]。
**基本面（~12）**：FinancialStatements[F/B/S 1990]、BalanceSheet[F/B/S 2011]、CashFlowsStatement[F/B/S 2008]、Dividend[F/B/S 2005]、DividendResult[F/B/S 2003]、MonthRevenue[F/B/S 2002]、**CapitalReductionReferencePrice[F 2011、per-stock]**、MarketValue[B/S 2004]、Delisting[F]、MarketValueWeight[B/S 2024]、SplitPrice[F]、ParValueChange[F 2020]。
**衍生品（~17）**：FuturesDaily[F/B/S 1998 data_id=契約如TX]、OptionDaily[F/B/S 2001 data_id=TXO]、Futures/OptionTick[B/S 2011 單日 parquet]、FuturesSpreadTick[S data_id=價差如CAF]、Futures/OptionInstitutionalInvestors[F/B/S 2018]、…AfterHours[B/S 2021]、Futures/OptionDealerTradingVolumeDaily[F 2021]、…OpenInterestLargeTraders[B/S 1998]、FuturesSpreadTrading[B/S 2007]、Futures/OptionFinalSettlementPrice[B/S]。
**即時（4，皆 Sponsor）**：taiwan_stock_tick_snapshot（data_id=股或 3 碼指數，91 指數）、TaiwanFutOptTickInfo[F]、taiwan_futures_snapshot、taiwan_options_snapshot。
**可轉債（4，B/S）**：ConvertibleBondInfo / Daily / InstitutionalInvestors / DailyOverview（2020）。
**其他（3）**：TaiwanStockNews[F **單日型 end_date 須 none**]、BusinessIndicator[B/S 1982 月]、IndustryChain[B/S]。
**國際（~9，皆 Free）**：US/UK/Europe/Japan StockInfo + StockPrice、USStockPriceMinute[B/S]。
**總經/全球（6）**：**TaiwanExchangeRate[F、18-19 幣別]**、**InterestRate[F、data_id=央行碼 FED/ECB/BOJ…12 行]**、GoldPrice[F]、**CrudeOilPrices[F、data_id=WTI/Brent]**、**GovernmentBondsYield[F、data_id=美債 13 期別 1M~30Y]**、CnnFearGreedIndex[B/S 2011]。

> tier：F=Free、B=Backer、S=Sponsor。年份=資料起始。augur(sponsor) 全可抓。

## 五、data_id 全集來源階層（#18 核心——權威來源、非臆測白名單）

| 維度類型 | 權威來源 | 例 |
|---|---|---|
| 總經/全球（7 dataset）| **`/datalist` API**（動態、最完整）| `/datalist?dataset=GovernmentBondsYield`→13 期別；ExchangeRate/TaiwanExchangeRate→幣別；InterestRate→央行；CrudeOilPrices→WTI/Brent；CurrencyCirculation；GovernmentBonds |
| per-stock | **roster**（TaiwanStockInfo 全股名冊）| Price/BalanceSheet/CapitalReduction… |
| 期/權契約 | **`/datalist`**（contract codes）| FuturesDaily=TX/MTX…、OptionDaily=TXO… |
| 指數（real-time snapshot）| **91 個 3 碼指數碼**（001=TAIEX、027=電子…，見 IndexCodes 頁）| tick_snapshot |
| 報酬指數 | **官方文檔 + probe 證實**（無 datalist）| TotalReturnIndex=TAIEX/TPEx |

- **`/datalist` 僅支援 7 總經類**：CrudeOilPrices, CurrencyCirculation, ExchangeRate, GovernmentBondsYield, GovernmentBonds, InterestRate, TaiwanExchangeRate。
- **實證 `/datalist` > 靜態文檔**：GovBonds `/datalist`=13 期別、文檔僅列 12（漏 4-Month）→ 程式一律問 `/datalist`、不抄文檔、不臆測。

## 六、特殊抓取模式（augur 須處理）

1. **單日型 dataset**（size-too-large、`end_date` 須 none）：TaiwanStockNews、tick、snapshot、5秒統計 → 逐日不帶 end（finmind.fetch 已自動相容）。
2. **bulk parquet（Sponsor）**：`/storage_objects?dataset&date` 整日下載（tick/KBar/TradingDailyReport）→ 大表高效路徑。
3. **dedicated endpoints（Sponsor）**：分點/券商聚合走專屬 URL（非 `/data`）。
4. **async batch（SDK）**：`stock_id_list + use_async` 併發多股（info/snapshot/tick/aggregation/可轉債 不支援）。
5. **by-date vs per-stock**：`[F/B/S]` dataset free 需 data_id、Backer+ 可 by-date——augur(sponsor) 可 by-date 全市場（省 request）。

## 七、對 augur 的關鍵啟示

1. **4 ABSENT 全有解**（非 tier 限制）：GovBonds=/datalist 13 期別、TotalReturnIndex=TAIEX/TPEx、ExchangeRate→用 TaiwanExchangeRate、CapitalReduction=roster 逐股（修 canonical 2330 誤判）。
2. **#18 維度 id**：一律走「`/datalist`→roster→文檔+probe」階層，無 hardcoded 白名單。
3. **#24 限速**：sponsor 6000/hr（≈1.67/s）；augur throttle 1.0s（3600/hr）保守安全；但 #24 實證「持續高速率累積 ban」仍須跨日分批。
4. **⏰ 到期 2026-06-24**：sponsor-only（分點/tick/snapshot/KBar/可轉債/法人 by-date）須趕在到期前抓完全史；到期後僅 free dataset 可續。
5. **bulk parquet**：未來 tick/分鐘 K 全史，`/storage_objects` 比逐日 `/data` 高效。

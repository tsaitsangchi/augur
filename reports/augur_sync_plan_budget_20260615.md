# augur 抓取 token 預算表（catalog-driven 最優計畫）— 2026-06-15

**性質**：階段 P plan 產生器輸出（**0 FinMind 呼叫**：只讀 `docs/datasets_zh.md` + augur DB）。對 22 張已落地表用 DB 真實 `COUNT(DISTINCT date/stock_id)`（標 `DB`）；其餘估算（標 `估`，per-stock 預設上界 roster 3100、單一序列=1、季/月頻=期數）。

## 結論

| 指標 | 值 |
|---|---|
| **最優計畫總呼叫** | **~127,866** |
| naive（per-stock 一律） | ~160,043 |
| **省** | ~32,177（20%）|
| @16w/0.8s ~4500/hr | **~28 fetch-hr（~1.8 天 @16hr/日）** |
| 距 6/24 ~9 天容量(16hr/日) | ~648,000 calls |
| **最優佔容量** | **19% → ✅ 充裕** |

## ⭐ DB 真值驗證的最大省點（季/月頻 per-stock→by-date）

| 表 | by-date(真) | per-stock(真) | 最優 | 省 |
|---|---|---|---|---|
| TaiwanStockBalanceSheet | **57** | 2414 | by-date | 2357 |
| TaiwanStockCashFlowsStatement | **57** | 2410 | by-date | 2353 |
| TaiwanStockFinancialStatements | **138** | 2407 | by-date | 2269 |
| TaiwanStockMonthRevenue | **293** | 2483 | by-date | 2190 |
| TaiwanStockGovernmentBankBuySell | **1202** | 2827 | by-date | 1625 |

## 全 83 表 fetch-plan（依呼叫數排序）

| dataset | 最優模式 | 呼叫 | naive | 來源 | 📅最早 |
|---|---|---|---|---|---|
| TaiwanFuturesOpenInterestLargeTraders | by-date | 4,865 | 4,865 | 估 | 2007-01-02（實證 |
| TaiwanOptionOpenInterestLargeTraders | by-date | 4,865 | 4,865 | 估 | 2007-01-02（實證 |
| TaiwanFuturesSpreadTrading | by-date | 4,674 | 4,674 | 估 | 2007-10-08（實證 |
| TaiwanStockNews | single-day | 4,074 | 2,908 | DB | 2010-03-02（DB |
| TaiwanStockPrice | per-stock | 3,100 | 3,100 | DB | 1994-09-13（DB |
| TaiwanStockPriceAdj | per-stock | 3,100 | 3,100 | DB | 1994-09-14（DB |
| TaiwanStockDayTrading | per-stock | 3,100 | 3,100 | 估 | 2014-01-06（實證 |
| TaiwanStock10Year | per-stock | 3,100 | 3,100 | 估 | 2011-01-24（實證 |
| TaiwanStockWeekPrice | per-stock | 3,100 | 3,100 | 估 | 1999-12-20（實證 |
| TaiwanStockMonthPrice | per-stock | 3,100 | 3,100 | 估 | 1999-12-01（實證 |
| TaiwanStockSuspended | per-stock | 3,100 | 3,100 | 估 | 2011-11-04（實證 |
| TaiwanStockPriceLimit | per-stock | 3,100 | 3,100 | 估 | 2000-01-03（實證 |
| TaiwanStockHoldingSharesPer | per-stock | 3,100 | 3,100 | 估 | 2010-01-29（實證 |
| TaiwanStockSecuritiesLending | per-stock | 3,100 | 3,100 | 估 | 2003-11-11（實證 |
| TaiwanStockDispositionSecuritiesPeriod | per-stock | 3,100 | 3,100 | 估 | 2001-01-02（實證 |
| TaiwanStockBlockTrade | per-stock | 3,100 | 3,100 | 估 | 2006-08-11（實證 |
| TaiwanStockLoanCollateralBalance | per-stock | 3,100 | 3,100 | 估 | 2006-10-02（實證 |
| TaiwanStockInstitutionalInvestorsBuySellWide | per-stock | 3,100 | 3,100 | 估 | 2012-05-02（實證 |
| TaiwanStockDividend | per-stock | 3,100 | 3,100 | 估 | 2005-06-19（實證 |
| TaiwanStockCapitalReductionReferencePrice | per-stock | 3,100 | 3,100 | 估 | 2011-01-25（實證 |
| TaiwanStockMarketValue | per-stock | 3,100 | 3,100 | 估 | 2004-02-12（實證 |
| TaiwanStockDelisting | per-stock | 3,100 | 3,100 | 估 | 2001-01-20（實證 |
| EuropeStockPrice | per-stock | 3,100 | 3,100 | 估 | 1990-01-01（實證 |
| JapanStockPrice | per-stock | 3,100 | 3,100 | 估 | 2001-01-01（實證 |
| TaiwanStockInstitutionalInvestorsBuySell | per-stock | 3,004 | 3,004 | DB | 2012-05-02（DB |
| TaiwanStockDayTradingSuspension | by-date | 2,985 | 3,100 | 估 | 2014-07-09（實證 |
| TaiwanStockMarginShortSaleSuspension | by-date | 2,803 | 3,100 | 估 | 2015-04-01（實證 |
| TaiwanOptionDaily | by-date | 2,695 | 2,695 | DB | 2002-01-02（DB |
| TaiwanStockDayTradingBorrowingFeeRate | by-date | 2,669 | 3,100 | 估 | 2015-10-14（實證 |
| TaiwanStockShareholding | per-stock | 2,627 | 2,627 | DB | 2004-02-12（DB |
| TaiwanDailyShortSaleBalances | per-stock | 2,453 | 2,453 | DB | 2005-07-01（DB |
| TaiwanStockMarginPurchaseShortSale | per-stock | 2,409 | 2,409 | DB | 2001-01-05（DB |
| TaiwanFuturesDaily | by-date | 2,260 | 2,260 | DB | 1998-08-03（DB |
| TaiwanStockPER | per-stock | 2,127 | 2,127 | DB | 2005-09-02（DB |
| TaiwanFutOptInstitutionalInvestors | by-date | 2,113 | 2,113 | 估 | 2018-01-02（驗證 |
| TaiwanFuturesInstitutionalInvestors | by-date | 2,008 | 2,008 | 估 | 2018-06-05（實證 |
| TaiwanOptionInstitutionalInvestors | by-date | 2,008 | 2,008 | 估 | 2018-06-05（實證 |
| USStockPrice | per-stock | 1,497 | 1,497 | DB | 1990-01-02（DB |
| TaiwanFuturesDealerTradingVolumeDaily | by-date | 1,489 | 1,489 | 估 | 2020-07-01（實證 |
| TaiwanOptionDealerTradingVolumeDaily | by-date | 1,489 | 1,489 | 估 | 2020-07-01（實證 |
| TaiwanStockSplitPrice | by-date | 1,457 | 3,100 | 估 | 2020-08-17（實證 |
| TaiwanStockParValueChange | by-date | 1,457 | 3,100 | 估 | 2020-08-17（實證 |
| TaiwanFuturesSpreadTick | by-date | 1,250 | 1,250 | 估 | 2026-06（tick僅 |
| TaiwanStockGovernmentBankBuySell | by-date | 1,202 | 2,827 | DB | 2021-07-01（DB |
| TaiwanFuturesInstitutionalInvestorsAfterHours | by-date | 1,169 | 1,169 | 估 | 2021-10-12（實證 |
| TaiwanOptionInstitutionalInvestorsAfterHours | by-date | 1,169 | 1,169 | 估 | 2021-10-12（實證 |
| TaiwanStockMarketValueWeight | by-date | 406 | 3,100 | 估 | 2024-10-30（實證 |
| TaiwanStockConvertibleBondDaily | by-date | 378 | 378 | 估 | 2024-12-10（實證 |
| TaiwanStockConvertibleBondInstitutionalInvestors | by-date | 378 | 378 | 估 | 2024-12-10（實證 |
| TaiwanStockConvertibleBondDailyOverview | by-date | 378 | 378 | 估 | 2024-12-10（實證 |
| TaiwanFuturesFinalSettlementPrice | by-date | 335 | 335 | 估 | 1998-09-17（實證 |
| TaiwanOptionFinalSettlementPrice | by-date | 295 | 295 | 估 | 2002-01-17（實證 |
| TaiwanStockMonthRevenue | by-date | 293 | 2,483 | DB | 2002-02-01（DB |
| TaiwanStockDividendResult | per-stock | 245 | 245 | DB | 2005-05-19（DB |
| TaiwanStockFinancialStatements | by-date | 138 | 2,407 | DB | 1991-12-31（DB |
| TaiwanStockBalanceSheet | by-date | 57 | 2,414 | DB | 2012-03-31（DB |
| TaiwanStockCashFlowsStatement | by-date | 57 | 2,410 | DB | 2012-03-31（DB |
| ExchangeRate | by-dim-id | 20 | 20 | 估 | 1990-01-02（實證 |
| TaiwanExchangeRate | by-dim-id | 19 | 19 | DB | 2006-01-02（DB |
| GovernmentBondsYield | by-dim-id | 13 | 13 | 估 | 2001-01-02（實證 |
| InterestRate | by-dim-id | 12 | 12 | 估 | 2008-02-01（實證 |
| TaiwanStockTotalReturnIndex | by-dim-id | 2 | 2 | 估 | 2003-01-02（實證 |
| CrudeOilPrices | by-dim-id | 2 | 2 | 估 | 1990-01-02（實證 |
| TaiwanStockInfo | single/snapshot | 1 | 3,101 | DB | 2020-06-03（DB |
| TaiwanStockInfoWithWarrant | single/snapshot | 1 | 3,100 | 估 | 2026-06-13（實證 |
| TaiwanStockInfoWithWarrantSummary | single/snapshot | 1 | 3,100 | 估 | 2014-07-31（實證 |
| TaiwanStockTradingDate | single/snapshot | 1 | 1 | 估 | 2000-01-04（實證 |
| TaiwanStockTotalMarginPurchaseShortSale | single/snapshot | 1 | 1 | 估 | 2001-01-03（實證 |
| TaiwanStockTotalInstitutionalInvestors | single/snapshot | 1 | 1 | DB | 2004-04-07（DB |
| TaiwanSecuritiesTraderInfo | single/snapshot | 1 | 1 | 估 | 1990-03-31（實證 |
| TaiwanTotalExchangeMarginMaintenance | single/snapshot | 1 | 1 | 估 | 2001-01-05（實證 |
| TaiwanFutOptDailyInfo | single/snapshot | 1 | 1 | 估 | —（總覽無 date 欄） |
| TaiwanFutOptTickInfo | single/snapshot | 1 | 1 | 估 | —（即時·/data無） |
| TaiwanStockConvertibleBondInfo | single/snapshot | 1 | 1 | 估 | —（總覽 1788 檔） |
| TaiwanBusinessIndicator | single/snapshot | 1 | 1 | 估 | 1990-01-01（實證 |
| TaiwanStockIndustryChain | single/snapshot | 1 | 3,100 | 估 | 2026-06-12（實證 |
| USStockInfo | single/snapshot | 1 | 3,100 | 估 | 2024-05-06（實證 |
| UKStockInfo | single/snapshot | 1 | 1 | 估 | 2019-01-31（實證 |
| UKStockPrice | by-date | 1 | 231 | DB | 1990-01-01（DB |
| EuropeStockInfo | single/snapshot | 1 | 1 | 估 | 2019-01-14（實證 |
| JapanStockInfo | single/snapshot | 1 | 1 | 估 | 2019-01-14（實證 |
| GoldPrice | single/snapshot | 1 | 1 | 估 | 1990-01-01（實證 |
| CnnFearGreedIndex | single/snapshot | 1 | 1 | DB | 2011-01-03（DB |

## 方法與保留（#15）
- **DB 22 表=真值**（authoritative）；**61 表=估算**（per-stock 上界 3100、實際可能更少→真實最優只會更省）。
- naive 對照＝有 stock_id 一律 per-stock；本表「省」為**保守下界**（估算表的 by-date 改進未全展開）。
- 可行性結論**穩健**：即使用最保守（naive 160k 或更高），仍 <30% 容量、~1.8-2.5 天可抓完，**6/24 充裕**。
- 此為**計畫估算**；實跑前小範圍試（如財報 by-date）驗證真省 + roster-scoped 對帳 PASS。
# augur catalog — 全 table × field 完整清單 (FinMind 98 + FRED 1 = 99)

> 來源:catalog DB(實證 95)+官方 datasets.md(補 4 dedicated/2 FinalSettle 欄/6 category)。每欄值或實證原因,零虛構。
> ⚠️ catalog DB 現 95;待額度恢復 rebuild 落 4 dedicated + 2 FinalSettle special-id earliest。


## finmind / Global Economic Data

### CnnFearGreedIndex `B` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2011-01-03 data_id_source=`none` n_stocks=None n_dates=3919 recon=`by-date` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `fear_greed` | NUMERIC(20,6) |  |  |
| 2 | `fear_greed_emotion` | VARCHAR(255) |  |  |

### CrudeOilPrices `F` ✅
- ep=`/data` mode=`by-dim-id` freq=`daily` earliest=1990-01-02 data_id_source=`datalist` n_stocks=2 n_dates=8931 recon=`by-dim-id` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `name` | VARCHAR(255) |  |  |
| 2 | `price` | NUMERIC(20,6) |  |  |

### GoldPrice `F` ✅
- ep=`/data` mode=`single-day` freq=`single-day` earliest=1990-01-01 data_id_source=`none` n_stocks=None n_dates=8931 recon=`by-date` prov=`probe`
  - 📝 intraday-source→聚合日級末筆(close);官方 daily 但 FinMind 回 intraday、augur 聚合存(#4)

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `Price` | NUMERIC(20,6) |  |  |
| 1 | `date` | VARCHAR(255) | 🔑 |  |

### GovernmentBondsYield `F` ✅
- ep=`/data` mode=`by-dim-id` freq=`daily` earliest=2001-01-02 data_id_source=`datalist` n_stocks=13 n_dates=6236 recon=`by-dim-id` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `name` | VARCHAR(255) |  |  |
| 2 | `value` | NUMERIC(20,6) |  |  |

### InterestRate `F` ✅
- ep=`/data` mode=`by-dim-id` freq=`daily` earliest=2008-02-01 data_id_source=`datalist` n_stocks=12 n_dates=4501 recon=`by-dim-id` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `country` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | DATE | 🔑 |  |
| 2 | `full_country_name` | VARCHAR(255) |  |  |
| 3 | `interest_rate` | NUMERIC(20,6) |  |  |

### TaiwanExchangeRate `F` ✅
- ep=`/data` mode=`by-dim-id` freq=`daily` earliest=2006-01-02 data_id_source=`datalist` n_stocks=None n_dates=4638 recon=`by-dim-id` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `currency` | VARCHAR(255) | 🔑 |  |
| 2 | `cash_buy` | NUMERIC(20,6) |  |  |
| 3 | `cash_sell` | NUMERIC(20,6) |  |  |
| 4 | `spot_buy` | NUMERIC(20,6) |  |  |
| 5 | `spot_sell` | NUMERIC(20,6) |  |  |


## finmind / International Markets

### EuropeStockInfo `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2019-01-14 data_id_source=`none` n_stocks=None n_dates=1818 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE |  |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `Market` | VARCHAR(255) |  |  |
| 3 | `stock_name` | VARCHAR(255) |  |  |

### EuropeStockPrice `F` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1990-01-01 data_id_source=`none` n_stocks=3101 n_dates=8931 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE |  |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `Adj_Close` | NUMERIC(20,6) |  |  |
| 3 | `Close` | NUMERIC(20,6) |  |  |
| 4 | `High` | NUMERIC(20,6) |  |  |
| 5 | `Low` | NUMERIC(20,6) |  |  |
| 6 | `Open` | NUMERIC(20,6) |  |  |
| 7 | `Volume` | NUMERIC(20,6) |  |  |

### JapanStockInfo `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2019-01-14 data_id_source=`none` n_stocks=None n_dates=1818 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `Exchange` | VARCHAR(255) | 🔑 |  |
| 3 | `Sector` | VARCHAR(255) |  |  |
| 4 | `stock_name` | VARCHAR(255) | 🔑 |  |

### JapanStockPrice `F` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1999-05-01 data_id_source=`none` n_stocks=3101 n_dates=6646 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE |  |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `Adj_Close` | NUMERIC(20,6) |  |  |
| 3 | `Close` | NUMERIC(20,6) |  |  |
| 4 | `High` | NUMERIC(20,6) |  |  |
| 5 | `Low` | NUMERIC(20,6) |  |  |
| 6 | `Open` | NUMERIC(20,6) |  |  |
| 7 | `Volume` | NUMERIC(20,6) |  |  |

### UKStockInfo `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2019-01-31 data_id_source=`none` n_stocks=None n_dates=1806 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `Country` | VARCHAR(255) | 🔑 |  |
| 3 | `stock_name` | VARCHAR(255) | 🔑 |  |

### UKStockPrice `F` ✅
- ep=`/data` mode=`by-date` freq=`yearly` earliest=1990-01-01 data_id_source=`roster` n_stocks=231 n_dates=1 recon=`full-history` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE |  |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `Adj_Close` | NUMERIC(20,6) |  |  |
| 3 | `Close` | NUMERIC(20,6) |  |  |
| 4 | `High` | NUMERIC(20,6) |  |  |
| 5 | `Low` | NUMERIC(20,6) |  |  |
| 6 | `Open` | NUMERIC(20,6) |  |  |
| 7 | `Volume` | NUMERIC(20,6) |  |  |

### USStockInfo `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2019-01-01 data_id_source=`roster` n_stocks=16709 n_dates=241 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE |  |  |
| 1 | `stock_id` | VARCHAR(255) |  |  |
| 2 | `Country` | VARCHAR(255) |  |  |
| 3 | `IPOYear` | NUMERIC(20,6) |  |  |
| 4 | `MarketCap` | NUMERIC(24,6) |  |  |
| 5 | `Subsector` | VARCHAR(255) |  |  |
| 6 | `stock_name` | VARCHAR(255) | 🔑 |  |

### USStockPrice `F` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1990-01-02 data_id_source=`roster` n_stocks=1477 n_dates=1952 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `Adj_Close` | NUMERIC(21,6) |  |  |
| 3 | `Close` | NUMERIC(21,6) |  |  |
| 4 | `High` | NUMERIC(21,6) |  |  |
| 5 | `Low` | NUMERIC(21,6) |  |  |
| 6 | `Open` | NUMERIC(21,6) |  |  |
| 7 | `Volume` | NUMERIC(20,6) |  |  |

### USStockPriceMinute `B` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=2021-05-01 data_id_source=`info-roster` n_stocks=16709 n_dates=1256 recon=`by-dim-id` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | VARCHAR(255) | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `close` | NUMERIC(20,6) |  |  |
| 3 | `high` | NUMERIC(20,6) |  |  |
| 4 | `low` | NUMERIC(20,6) |  |  |
| 5 | `open` | NUMERIC(20,6) |  |  |
| 6 | `volume` | NUMERIC(20,6) |  |  |


## finmind / TW-Chip / Institutional

### TaiwanDailyShortSaleBalances `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2005-07-01 data_id_source=`roster` n_stocks=2239 n_dates=5125 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 1 | `MarginShortSalesPreviousDayBalance` | NUMERIC(20,6) |  |  |
| 2 | `MarginShortSalesShortSales` | NUMERIC(20,6) |  |  |
| 3 | `MarginShortSalesShortCovering` | NUMERIC(20,6) |  |  |
| 4 | `MarginShortSalesStockRedemption` | NUMERIC(20,6) |  |  |
| 5 | `MarginShortSalesCurrentDayBalance` | NUMERIC(20,6) |  |  |
| 6 | `MarginShortSalesQuota` | NUMERIC(20,6) |  |  |
| 7 | `SBLShortSalesPreviousDayBalance` | NUMERIC(20,6) |  |  |
| 8 | `SBLShortSalesShortSales` | NUMERIC(20,6) |  |  |
| 9 | `SBLShortSalesReturns` | NUMERIC(20,6) |  |  |
| 10 | `SBLShortSalesAdjustments` | NUMERIC(20,6) |  |  |
| 11 | `SBLShortSalesCurrentDayBalance` | NUMERIC(20,6) |  |  |
| 12 | `SBLShortSalesQuota` | NUMERIC(20,6) |  |  |
| 13 | `SBLShortSalesShortCovering` | NUMERIC(20,6) |  |  |
| 14 | `date` | DATE | 🔑 |  |

### TaiwanSecuritiesTraderInfo `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2025-02-01 data_id_source=`none` n_stocks=1 n_dates=335 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `securities_trader_id` | VARCHAR(255) | 🔑 |  |
| 1 | `securities_trader` | VARCHAR(255) |  |  |
| 2 | `date` | DATE |  |  |
| 3 | `address` | VARCHAR(255) |  |  |
| 4 | `phone` | VARCHAR(255) |  |  |

### TaiwanStockBlockTrade `S` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2006-08-11 data_id_source=`roster` n_stocks=3101 n_dates=4862 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `trade_type` | VARCHAR(255) | 🔑 |  |
| 3 | `price` | NUMERIC(20,6) | 🔑 |  |
| 4 | `volume` | NUMERIC(21,6) | 🔑 |  |
| 5 | `trading_money` | NUMERIC(23,6) | 🔑 |  |

### TaiwanStockDispositionSecuritiesPeriod `B` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2005-01-01 data_id_source=`none` n_stocks=3101 n_dates=5256 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE |  |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | VARCHAR(255) |  |  |
| 3 | `disposition_cnt` | NUMERIC(20,6) |  |  |
| 4 | `condition` | VARCHAR(255) |  |  |
| 5 | `measure` | VARCHAR(255) |  |  |
| 6 | `period_start` | DATE |  |  |
| 7 | `period_end` | DATE |  |  |

### TaiwanStockGovernmentBankBuySell `S` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2021-07-01 data_id_source=`roster` n_stocks=2623 n_dates=1200 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `buy_amount` | NUMERIC(21,6) | 🔑 |  |
| 3 | `sell_amount` | NUMERIC(20,6) | 🔑 |  |
| 4 | `buy` | NUMERIC(20,6) | 🔑 |  |
| 5 | `sell` | NUMERIC(20,6) | 🔑 |  |
| 6 | `bank_name` | VARCHAR(255) | 🔑 |  |

### TaiwanStockHoldingSharesPer `B` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2010-01-29 data_id_source=`roster` n_stocks=3101 n_dates=4013 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `HoldingSharesLevel` | VARCHAR(255) | 🔑 |  |
| 3 | `people` | NUMERIC(20,6) |  |  |
| 4 | `percent` | NUMERIC(20,6) |  |  |
| 5 | `unit` | NUMERIC(21,6) |  |  |

### TaiwanStockInstitutionalInvestorsBuySell `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2012-05-02 data_id_source=`roster` n_stocks=2497 n_dates=3445 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `buy` | NUMERIC(20,6) |  |  |
| 3 | `name` | VARCHAR(255) | 🔑 |  |
| 4 | `sell` | NUMERIC(20,6) |  |  |

### TaiwanStockLoanCollateralBalance `S` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2006-10-02 data_id_source=`roster` n_stocks=3101 n_dates=4828 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `market` | VARCHAR(255) |  |  |
| 3 | `MarginPreviousDayBalance` | NUMERIC(20,6) |  |  |
| 4 | `MarginBuy` | NUMERIC(20,6) |  |  |
| 5 | `MarginSell` | NUMERIC(20,6) |  |  |
| 6 | `MarginCashRedemption` | NUMERIC(20,6) |  |  |
| 7 | `MarginCurrentDayBalance` | NUMERIC(20,6) |  |  |
| 8 | `MarginNextDayQuota` | NUMERIC(20,6) |  |  |
| 9 | `SecuritiesFirmLoanPreviousDayBalance` | NUMERIC(20,6) |  |  |
| 10 | `SecuritiesFirmLoanBuy` | NUMERIC(20,6) |  |  |
| 11 | `SecuritiesFirmLoanSell` | NUMERIC(20,6) |  |  |
| 12 | `SecuritiesFirmLoanCashRedemption` | NUMERIC(20,6) |  |  |
| 13 | `SecuritiesFirmLoanReplacement` | NUMERIC(20,6) |  |  |
| 14 | `SecuritiesFirmLoanCurrentDayBalance` | NUMERIC(20,6) |  |  |
| 15 | `SecuritiesFirmLoanNextDayQuota` | NUMERIC(20,6) |  |  |
| 16 | `UnrestrictedLoanPreviousDayBalance` | NUMERIC(20,6) |  |  |
| 17 | `UnrestrictedLoanBuy` | NUMERIC(20,6) |  |  |
| 18 | `UnrestrictedLoanSell` | NUMERIC(20,6) |  |  |
| 19 | `UnrestrictedLoanCashRedemption` | NUMERIC(20,6) |  |  |
| 20 | `UnrestrictedLoanReplacement` | NUMERIC(20,6) |  |  |
| 21 | `UnrestrictedLoanCurrentDayBalance` | NUMERIC(20,6) |  |  |
| 22 | `UnrestrictedLoanNextDayQuota` | NUMERIC(20,6) |  |  |
| 23 | `SecuritiesFinanceSecuredLoanPreviousDayBalance` | NUMERIC(20,6) |  |  |
| 24 | `SecuritiesFinanceSecuredLoanBuy` | NUMERIC(20,6) |  |  |
| 25 | `SecuritiesFinanceSecuredLoanSell` | NUMERIC(20,6) |  |  |
| 26 | `SecuritiesFinanceSecuredLoanCashRedemption` | NUMERIC(20,6) |  |  |
| 27 | `SecuritiesFinanceSecuredLoanReplacement` | NUMERIC(20,6) |  |  |
| 28 | `SecuritiesFinanceSecuredLoanCurrentDayBalance` | NUMERIC(20,6) |  |  |
| 29 | `SecuritiesFinanceSecuredLoanNextDayQuota` | NUMERIC(20,6) |  |  |
| 30 | `SettlementMarginPreviousDayBalance` | NUMERIC(20,6) |  |  |
| 31 | `SettlementMarginBuy` | NUMERIC(20,6) |  |  |
| 32 | `SettlementMarginSell` | NUMERIC(20,6) |  |  |
| 33 | `SettlementMarginCashRedemption` | NUMERIC(20,6) |  |  |
| 34 | `SettlementMarginReplacement` | NUMERIC(20,6) |  |  |
| 35 | `SettlementMarginCurrentDayBalance` | NUMERIC(20,6) |  |  |
| 36 | `SettlementMarginNextDayQuota` | NUMERIC(20,6) |  |  |

### TaiwanStockMarginPurchaseShortSale `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2001-01-05 data_id_source=`roster` n_stocks=2168 n_dates=6163 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `MarginPurchaseBuy` | NUMERIC(20,6) |  |  |
| 3 | `MarginPurchaseCashRepayment` | NUMERIC(20,6) |  |  |
| 4 | `MarginPurchaseLimit` | NUMERIC(20,6) |  |  |
| 5 | `MarginPurchaseSell` | NUMERIC(20,6) |  |  |
| 6 | `MarginPurchaseTodayBalance` | NUMERIC(20,6) |  |  |
| 7 | `MarginPurchaseYesterdayBalance` | NUMERIC(20,6) |  |  |
| 8 | `Note` | VARCHAR(255) |  |  |
| 9 | `OffsetLoanAndShort` | NUMERIC(20,6) |  |  |
| 10 | `ShortSaleBuy` | NUMERIC(20,6) |  |  |
| 11 | `ShortSaleCashRepayment` | NUMERIC(20,6) |  |  |
| 12 | `ShortSaleLimit` | NUMERIC(20,6) |  |  |
| 13 | `ShortSaleSell` | NUMERIC(20,6) |  |  |
| 14 | `ShortSaleTodayBalance` | NUMERIC(20,6) |  |  |
| 15 | `ShortSaleYesterdayBalance` | NUMERIC(20,6) |  |  |

### TaiwanStockMarginShortSaleSuspension `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2015-04-01 data_id_source=`roster` n_stocks=3101 n_dates=2746 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | DATE | 🔑 |  |
| 2 | `end_date` | DATE |  |  |
| 3 | `reason` | VARCHAR(255) |  |  |

### TaiwanStockSecuritiesLending `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2003-11-11 data_id_source=`roster` n_stocks=3101 n_dates=5536 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `transaction_type` | VARCHAR(255) | 🔑 |  |
| 3 | `volume` | NUMERIC(20,6) | 🔑 |  |
| 4 | `fee_rate` | NUMERIC(20,6) | 🔑 |  |
| 5 | `close` | NUMERIC(20,6) | 🔑 |  |
| 6 | `original_return_date` | VARCHAR(255) |  |  |
| 7 | `original_lending_period` | NUMERIC(20,6) | 🔑 |  |

### TaiwanStockShareholding `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2004-02-12 data_id_source=`roster` n_stocks=2316 n_dates=5514 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | VARCHAR(255) |  |  |
| 3 | `InternationalCode` | VARCHAR(255) |  |  |
| 4 | `ForeignInvestmentRemainingShares` | NUMERIC(21,6) |  |  |
| 5 | `ForeignInvestmentShares` | NUMERIC(21,6) |  |  |
| 6 | `ForeignInvestmentRemainRatio` | NUMERIC(20,6) |  |  |
| 7 | `ForeignInvestmentSharesRatio` | NUMERIC(20,6) |  |  |
| 8 | `ForeignInvestmentUpperLimitRatio` | NUMERIC(20,6) |  |  |
| 9 | `ChineseInvestmentUpperLimitRatio` | NUMERIC(20,6) |  |  |
| 10 | `NumberOfSharesIssued` | NUMERIC(21,6) |  |  |
| 11 | `RecentlyDeclareDate` | VARCHAR(255) |  | ⚠️ |
| 12 | `note` | VARCHAR(255) |  |  |

### TaiwanStockTotalInstitutionalInvestors `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2004-04-07 data_id_source=`none` n_stocks=None n_dates=5458 recon=`by-date` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `buy` | NUMERIC(23,6) |  |  |
| 1 | `date` | DATE | 🔑 |  |
| 2 | `name` | VARCHAR(255) | 🔑 |  |
| 3 | `sell` | NUMERIC(23,6) |  |  |

### TaiwanStockTotalMarginPurchaseShortSale `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2001-01-01 data_id_source=`none` n_stocks=None n_dates=6236 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `TodayBalance` | NUMERIC(22,6) |  |  |
| 1 | `YesBalance` | NUMERIC(22,6) |  |  |
| 2 | `buy` | NUMERIC(21,6) |  |  |
| 3 | `date` | DATE | 🔑 |  |
| 4 | `name` | VARCHAR(255) | 🔑 |  |
| 5 | `Return` | NUMERIC(20,6) |  |  |
| 6 | `sell` | NUMERIC(21,6) |  |  |

### TaiwanStockTradingDailyReport `S` 🚫excl
- ep=`/taiwan_stock_trading_daily_report` mode=`excluded` freq=`daily` earliest=2021-07-01 data_id_source=`roster` n_stocks=3101 n_dates=1215 recon=`roster-scoped` prov=`ingest.BACKFILL_DEFERRED` durl=`/taiwan_stock_trading_daily_report`
  - ⚠️ 可抓但暫緩自動 backfill（規模/scope 待決，非物理不可行）；抓法已實證
  - 📝 實證 2026-06-16：分點/權證走 dedicated endpoint（finmind.fetch_dedicated）、鉅額走 /data；全市場全史規模大→scope 屬放量決策

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `securities_trader` | VARCHAR(255) | 🔑 |  |
| 1 | `price` | NUMERIC(20,6) | 🔑 |  |
| 2 | `buy` | NUMERIC(20,6) | 🔑 |  |
| 3 | `sell` | NUMERIC(20,6) | 🔑 |  |
| 4 | `securities_trader_id` | VARCHAR(255) | 🔑 |  |
| 5 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 6 | `date` | DATE | 🔑 |  |

### TaiwanStockWarrantTradingDailyReport `S` 🚫excl
- ep=`/taiwan_stock_warrant_trading_daily_report` mode=`excluded` freq=`daily` earliest=NULL(dedicated需權證代號、權證會到期→單一代號跨不了史→earliest需全權證宇宙掃(放量)) data_id_source=`None` n_stocks=None n_dates=None recon=`by-date` prov=`ingest.BACKFILL_DEFERRED` durl=`/taiwan_stock_warrant_trading_daily_report`
  - ⚠️ 可抓但暫緩自動 backfill（規模/scope 待決，非物理不可行）；抓法已實證
  - 📝 實證 2026-06-16：分點/權證走 dedicated endpoint（finmind.fetch_dedicated）、鉅額走 /data；全市場全史規模大→scope 屬放量決策

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `securities_trader` | - |  |  |
| 1 | `price` | - |  |  |
| 2 | `buy` | - |  |  |
| 3 | `sell` | - |  |  |
| 4 | `securities_trader_id` | - |  |  |
| 5 | `stock_id` | - |  |  |
| 6 | `date` | - |  |  |

### TaiwanTotalExchangeMarginMaintenance `B` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2001-01-01 data_id_source=`none` n_stocks=1 n_dates=6236 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `TotalExchangeMarginMaintenance` | NUMERIC(20,6) |  |  |


## finmind / TW-Convertible Bond

### TaiwanStockConvertibleBondDaily `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2007-01-01 data_id_source=`none` n_stocks=None n_dates=4767 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `cb_id` | VARCHAR(255) | 🔑 |  |
| 1 | `cb_name` | VARCHAR(255) |  |  |
| 2 | `transaction_type` | VARCHAR(255) |  |  |
| 3 | `close` | NUMERIC(20,6) |  |  |
| 4 | `change` | NUMERIC(20,6) |  |  |
| 5 | `open` | NUMERIC(20,6) |  |  |
| 6 | `max` | NUMERIC(20,6) |  |  |
| 7 | `min` | NUMERIC(20,6) |  |  |
| 8 | `no_of_transactions` | NUMERIC(20,6) |  |  |
| 9 | `unit` | NUMERIC(20,6) |  |  |
| 10 | `trading_value` | NUMERIC(20,6) |  |  |
| 11 | `avg_price` | NUMERIC(20,6) |  |  |
| 12 | `next_ref_price` | NUMERIC(20,6) |  |  |
| 13 | `next_max_limit` | NUMERIC(20,6) |  |  |
| 14 | `next_min_limit` | NUMERIC(20,6) |  |  |
| 15 | `date` | DATE |  |  |

### TaiwanStockConvertibleBondDailyOverview `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2010-01-01 data_id_source=`none` n_stocks=None n_dates=4031 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `cb_id` | VARCHAR(255) | 🔑 |  |
| 1 | `cb_name` | VARCHAR(255) |  |  |
| 2 | `date` | DATE |  |  |
| 3 | `InitialDateOfConversion` | DATE |  |  |
| 4 | `DueDateOfConversion` | DATE |  |  |
| 5 | `InitialDateOfStopConversion` | VARCHAR(255) |  |  |
| 6 | `DueDateOfStopConversion` | VARCHAR(255) |  |  |
| 7 | `ConversionPrice` | NUMERIC(20,6) |  |  |
| 8 | `NextEffectiveDateOfConversionPrice` | DATE |  |  |
| 9 | `LatestInitialDateOfPut` | DATE |  |  |
| 10 | `LatestDueDateOfPut` | DATE |  |  |
| 11 | `LatestPutPrice` | NUMERIC(20,6) |  |  |
| 12 | `InitialDateOfEarlyRedemption` | DATE |  |  |
| 13 | `DueDateOfEarlyRedemption` | DATE |  |  |
| 14 | `EarlyRedemptionPrice` | NUMERIC(20,6) |  |  |
| 15 | `DateOfDelisted` | DATE |  |  |
| 16 | `IssuanceAmount` | NUMERIC(20,6) |  |  |
| 17 | `OutstandingAmount` | NUMERIC(20,6) |  |  |
| 18 | `ReferencePrice` | NUMERIC(20,6) |  |  |
| 19 | `PriceOfUnderlyingStock` | NUMERIC(20,6) |  |  |
| 20 | `InitialDateOfSuspension` | VARCHAR(255) |  |  |
| 21 | `DueDateOfSuspension` | VARCHAR(255) |  |  |
| 22 | `CouponRate` | NUMERIC(20,6) |  |  |

### TaiwanStockConvertibleBondInfo `B` ✅
- ep=`/data` mode=`market` freq=`snapshot` earliest=2025-01-01 data_id_source=`none` n_stocks=1 n_dates=356 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `cb_id` | VARCHAR(255) | 🔑 |  |
| 1 | `cb_name` | VARCHAR(255) |  |  |
| 2 | `InitialDateOfConversion` | DATE |  |  |
| 3 | `DueDateOfConversion` | DATE |  |  |
| 4 | `IssuanceAmount` | NUMERIC(20,6) |  |  |

### TaiwanStockConvertibleBondInstitutionalInvestors `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2009-04-01 data_id_source=`none` n_stocks=None n_dates=4216 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `Foreign_Investor_Buy` | NUMERIC(20,6) |  |  |
| 1 | `Foreign_Investor_Sell` | NUMERIC(20,6) |  |  |
| 2 | `Foreign_Investor_Overbuy` | NUMERIC(20,6) |  |  |
| 3 | `Investment_Trust_Buy` | NUMERIC(20,6) |  |  |
| 4 | `Investment_Trust_Sell` | NUMERIC(20,6) |  |  |
| 5 | `Investment_Trust_Overbuy` | NUMERIC(20,6) |  |  |
| 6 | `Dealer_self_Buy` | NUMERIC(20,6) |  |  |
| 7 | `Dealer_self_Sell` | NUMERIC(20,6) |  |  |
| 8 | `Dealer_self_Overbuy` | NUMERIC(20,6) |  |  |
| 9 | `Total_Overbuy` | NUMERIC(20,6) |  |  |
| 10 | `cb_id` | VARCHAR(255) | 🔑 |  |
| 11 | `cb_name` | VARCHAR(255) |  |  |
| 12 | `date` | DATE |  |  |


## finmind / TW-Derivative

### TaiwanFutOptDailyInfo `F` ✅
- ep=`/data` mode=`market` freq=`snapshot` earliest=1990-01-01 data_id_source=`none` n_stocks=None n_dates=8931 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `code` | VARCHAR(255) | 🔑 |  |
| 1 | `type` | VARCHAR(255) | 🔑 |  |
| 2 | `name` | VARCHAR(255) | 🔑 |  |

### TaiwanFuturesDaily `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=1998-08-03 data_id_source=`none` n_stocks=None n_dates=2226 recon=`by-date` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `futures_id` | VARCHAR(255) | 🔑 |  |
| 2 | `contract_date` | NUMERIC(20,6) | 🔑 |  |
| 3 | `open` | NUMERIC(20,6) | 🔑 |  |
| 4 | `max` | NUMERIC(20,6) | 🔑 |  |
| 5 | `min` | NUMERIC(20,6) | 🔑 |  |
| 6 | `close` | NUMERIC(20,6) | 🔑 |  |
| 7 | `spread` | NUMERIC(20,6) | 🔑 |  |
| 8 | `spread_per` | NUMERIC(20,6) | 🔑 |  |
| 9 | `volume` | NUMERIC(20,6) | 🔑 |  |
| 10 | `settlement_price` | NUMERIC(20,6) | 🔑 |  |
| 11 | `open_interest` | NUMERIC(20,6) | 🔑 |  |
| 12 | `trading_session` | VARCHAR(255) | 🔑 |  |

### TaiwanFuturesDealerTradingVolumeDaily `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2021-04-01 data_id_source=`none` n_stocks=None n_dates=1276 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `dealer_code` | VARCHAR(255) | 🔑 |  |
| 2 | `dealer_name` | VARCHAR(255) | 🔑 |  |
| 3 | `futures_id` | VARCHAR(255) | 🔑 |  |
| 4 | `volume` | NUMERIC(20,6) | 🔑 |  |
| 5 | `is_after_hour` | VARCHAR(255) | 🔑 |  |

### TaiwanFuturesFinalSettlementPrice `B` ✅
- ep=`/data` mode=`market` freq=`snapshot` earliest=NULL(probe(empty):需特定契約/結算 special-id(如TX/TXO),canonical探測未取樣→待額度恢復用special-id補) data_id_source=`none` n_stocks=None n_dates=None recon=`by-date` prov=`probe(empty)`

_欄位(官方 datasets.md、未探型別):_

| # | column |
|--|--|
| 0 | `date` |
| 1 | `contract_month` |
| 2 | `futures_id` |
| 3 | `settlement_price` |

### TaiwanFuturesInstitutionalInvestors `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2018-06-01 data_id_source=`none` n_stocks=None n_dates=1970 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `futures_id` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | DATE | 🔑 |  |
| 2 | `institutional_investors` | VARCHAR(255) | 🔑 |  |
| 3 | `long_deal_volume` | NUMERIC(20,6) |  |  |
| 4 | `long_deal_amount` | NUMERIC(20,6) |  |  |
| 5 | `short_deal_volume` | NUMERIC(20,6) |  |  |
| 6 | `short_deal_amount` | NUMERIC(20,6) |  |  |
| 7 | `long_open_interest_balance_volume` | NUMERIC(20,6) |  |  |
| 8 | `long_open_interest_balance_amount` | NUMERIC(20,6) |  |  |
| 9 | `short_open_interest_balance_volume` | NUMERIC(20,6) |  |  |
| 10 | `short_open_interest_balance_amount` | NUMERIC(20,6) |  |  |

### TaiwanFuturesInstitutionalInvestorsAfterHours `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2021-10-01 data_id_source=`none` n_stocks=None n_dates=1153 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `futures_id` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | DATE | 🔑 |  |
| 2 | `institutional_investors` | VARCHAR(255) | 🔑 |  |
| 3 | `long_deal_volume` | NUMERIC(20,6) |  |  |
| 4 | `long_deal_amount` | NUMERIC(20,6) |  |  |
| 5 | `short_deal_volume` | NUMERIC(20,6) |  |  |
| 6 | `short_deal_amount` | NUMERIC(20,6) |  |  |

### TaiwanFuturesOpenInterestLargeTraders `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2007-01-01 data_id_source=`none` n_stocks=None n_dates=4767 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `name` | VARCHAR(255) | 🔑 |  |
| 1 | `contract_type` | VARCHAR(255) | 🔑 |  |
| 2 | `buy_top5_trader_open_interest` | NUMERIC(20,6) |  |  |
| 3 | `buy_top5_trader_open_interest_per` | NUMERIC(20,6) |  |  |
| 4 | `buy_top10_trader_open_interest` | NUMERIC(20,6) |  |  |
| 5 | `buy_top10_trader_open_interest_per` | NUMERIC(20,6) |  |  |
| 6 | `sell_top5_trader_open_interest` | NUMERIC(20,6) |  |  |
| 7 | `sell_top5_trader_open_interest_per` | NUMERIC(20,6) |  |  |
| 8 | `sell_top10_trader_open_interest` | NUMERIC(20,6) |  |  |
| 9 | `sell_top10_trader_open_interest_per` | NUMERIC(20,6) |  |  |
| 10 | `market_open_interest` | NUMERIC(20,6) |  |  |
| 11 | `buy_top5_specific_open_interest` | NUMERIC(20,6) |  |  |
| 12 | `buy_top5_specific_open_interest_per` | NUMERIC(20,6) |  |  |
| 13 | `buy_top10_specific_open_interest` | NUMERIC(20,6) |  |  |
| 14 | `buy_top10_specific_open_interest_per` | NUMERIC(20,6) |  |  |
| 15 | `sell_top5_specific_open_interest` | NUMERIC(20,6) |  |  |
| 16 | `sell_top5_specific_open_interest_per` | NUMERIC(20,6) |  |  |
| 17 | `sell_top10_specific_open_interest` | NUMERIC(20,6) |  |  |
| 18 | `sell_top10_specific_open_interest_per` | NUMERIC(20,6) |  |  |
| 19 | `date` | DATE | 🔑 |  |
| 20 | `futures_id` | VARCHAR(255) | 🔑 |  |

### TaiwanFuturesSpreadTrading `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2007-11-01 data_id_source=`none` n_stocks=None n_dates=4563 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `futures_id` | VARCHAR(255) | 🔑 |  |
| 2 | `contract_date` | VARCHAR(255) | 🔑 |  |
| 3 | `open` | NUMERIC(20,6) | 🔑 |  |
| 4 | `max` | NUMERIC(20,6) | 🔑 |  |
| 5 | `min` | NUMERIC(20,6) | 🔑 |  |
| 6 | `close` | NUMERIC(20,6) | 🔑 |  |
| 7 | `best_bid` | NUMERIC(20,6) | 🔑 |  |
| 8 | `best_ask` | NUMERIC(20,6) | 🔑 |  |
| 9 | `historical_max` | NUMERIC(20,6) | 🔑 |  |
| 10 | `historical_min` | NUMERIC(20,6) | 🔑 |  |
| 11 | `spread_to_spread_volume` | NUMERIC(20,6) | 🔑 |  |
| 12 | `spread_to_single_volume` | NUMERIC(20,6) | 🔑 |  |
| 13 | `trading_session` | VARCHAR(255) | 🔑 |  |

### TaiwanFuturesTick `B` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=2026-06-01 data_id_source=`none` n_stocks=None n_dates=10 recon=`by-date` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `contract_date` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | VARCHAR(255) | 🔑 |  |
| 2 | `futures_id` | VARCHAR(255) | 🔑 |  |
| 3 | `price` | NUMERIC(20,6) | 🔑 |  |
| 4 | `volume` | NUMERIC(20,6) | 🔑 |  |

### TaiwanOptionDaily `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2002-01-02 data_id_source=`none` n_stocks=None n_dates=2369 recon=`by-date` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `option_id` | VARCHAR(255) | 🔑 |  |
| 2 | `contract_date` | NUMERIC(20,6) | 🔑 |  |
| 3 | `strike_price` | NUMERIC(20,6) | 🔑 |  |
| 4 | `call_put` | VARCHAR(255) | 🔑 |  |
| 5 | `open` | NUMERIC(20,6) | 🔑 |  |
| 6 | `max` | NUMERIC(20,6) | 🔑 |  |
| 7 | `min` | NUMERIC(20,6) | 🔑 |  |
| 8 | `close` | NUMERIC(20,6) | 🔑 |  |
| 9 | `volume` | NUMERIC(20,6) | 🔑 |  |
| 10 | `settlement_price` | NUMERIC(20,6) | 🔑 |  |
| 11 | `open_interest` | NUMERIC(20,6) | 🔑 |  |
| 12 | `trading_session` | VARCHAR(255) | 🔑 |  |

### TaiwanOptionDealerTradingVolumeDaily `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2021-04-01 data_id_source=`none` n_stocks=None n_dates=1276 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `dealer_code` | VARCHAR(255) | 🔑 |  |
| 2 | `dealer_name` | VARCHAR(255) | 🔑 |  |
| 3 | `option_id` | VARCHAR(255) | 🔑 |  |
| 4 | `volume` | NUMERIC(20,6) | 🔑 |  |
| 5 | `is_after_hour` | VARCHAR(255) | 🔑 |  |

### TaiwanOptionFinalSettlementPrice `B` ✅
- ep=`/data` mode=`market` freq=`snapshot` earliest=NULL(probe(empty):需特定契約/結算 special-id(如TX/TXO),canonical探測未取樣→待額度恢復用special-id補) data_id_source=`none` n_stocks=None n_dates=None recon=`by-date` prov=`probe(empty)`

_欄位(官方 datasets.md、未探型別):_

| # | column |
|--|--|
| 0 | `date` |
| 1 | `contract_month` |
| 2 | `option_id` |
| 3 | `settlement_price` |

### TaiwanOptionInstitutionalInvestors `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2018-06-01 data_id_source=`none` n_stocks=None n_dates=1970 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `option_id` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | DATE | 🔑 |  |
| 2 | `call_put` | VARCHAR(255) | 🔑 |  |
| 3 | `institutional_investors` | VARCHAR(255) | 🔑 |  |
| 4 | `long_deal_volume` | NUMERIC(20,6) |  |  |
| 5 | `long_deal_amount` | NUMERIC(20,6) |  |  |
| 6 | `short_deal_volume` | NUMERIC(20,6) |  |  |
| 7 | `short_deal_amount` | NUMERIC(20,6) |  |  |
| 8 | `long_open_interest_balance_volume` | NUMERIC(20,6) |  |  |
| 9 | `long_open_interest_balance_amount` | NUMERIC(20,6) |  |  |
| 10 | `short_open_interest_balance_volume` | NUMERIC(20,6) |  |  |
| 11 | `short_open_interest_balance_amount` | NUMERIC(20,6) |  |  |

### TaiwanOptionInstitutionalInvestorsAfterHours `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2021-10-01 data_id_source=`none` n_stocks=None n_dates=1153 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `option_id` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | DATE | 🔑 |  |
| 2 | `call_put` | VARCHAR(255) | 🔑 |  |
| 3 | `institutional_investors` | VARCHAR(255) | 🔑 |  |
| 4 | `long_deal_volume` | NUMERIC(20,6) |  |  |
| 5 | `long_deal_amount` | NUMERIC(20,6) |  |  |
| 6 | `short_deal_volume` | NUMERIC(20,6) |  |  |
| 7 | `short_deal_amount` | NUMERIC(20,6) |  |  |

### TaiwanOptionOpenInterestLargeTraders `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2007-01-01 data_id_source=`none` n_stocks=None n_dates=4767 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `contract_type` | VARCHAR(255) | 🔑 |  |
| 1 | `buy_top5_trader_open_interest` | NUMERIC(20,6) |  |  |
| 2 | `buy_top5_trader_open_interest_per` | NUMERIC(20,6) |  |  |
| 3 | `buy_top10_trader_open_interest` | NUMERIC(20,6) |  |  |
| 4 | `buy_top10_trader_open_interest_per` | NUMERIC(20,6) |  |  |
| 5 | `sell_top5_trader_open_interest` | NUMERIC(20,6) |  |  |
| 6 | `sell_top5_trader_open_interest_per` | NUMERIC(20,6) |  |  |
| 7 | `sell_top10_trader_open_interest` | NUMERIC(20,6) |  |  |
| 8 | `sell_top10_trader_open_interest_per` | NUMERIC(20,6) |  |  |
| 9 | `market_open_interest` | NUMERIC(20,6) |  |  |
| 10 | `buy_top5_specific_open_interest` | NUMERIC(20,6) |  |  |
| 11 | `buy_top5_specific_open_interest_per` | NUMERIC(20,6) |  |  |
| 12 | `buy_top10_specific_open_interest` | NUMERIC(20,6) |  |  |
| 13 | `buy_top10_specific_open_interest_per` | NUMERIC(20,6) |  |  |
| 14 | `sell_top5_specific_open_interest` | NUMERIC(20,6) |  |  |
| 15 | `sell_top5_specific_open_interest_per` | NUMERIC(20,6) |  |  |
| 16 | `sell_top10_specific_open_interest` | NUMERIC(20,6) |  |  |
| 17 | `sell_top10_specific_open_interest_per` | NUMERIC(20,6) |  |  |
| 18 | `date` | DATE | 🔑 |  |
| 19 | `put_call` | VARCHAR(255) | 🔑 |  |
| 20 | `name` | VARCHAR(255) | 🔑 |  |
| 21 | `option_id` | VARCHAR(255) | 🔑 |  |

### TaiwanOptionTick `B` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=2026-06-01 data_id_source=`none` n_stocks=None n_dates=10 recon=`by-date` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `ExercisePrice` | NUMERIC(20,6) | 🔑 |  |
| 1 | `PutCall` | VARCHAR(255) | 🔑 |  |
| 2 | `contract_date` | VARCHAR(255) | 🔑 |  |
| 3 | `date` | VARCHAR(255) | 🔑 |  |
| 4 | `option_id` | VARCHAR(255) | 🔑 |  |
| 5 | `price` | NUMERIC(20,6) | 🔑 |  |
| 6 | `volume` | NUMERIC(20,6) | 🔑 |  |


## finmind / TW-Fundamental

### TaiwanStockBalanceSheet `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`quarterly` earliest=2012-03-31 data_id_source=`roster` n_stocks=2201 n_dates=57 recon=`full-history` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `type` | VARCHAR(255) | 🔑 |  |
| 3 | `value` | NUMERIC(24,6) |  |  |
| 4 | `origin_name` | VARCHAR(255) |  |  |

### TaiwanStockCapitalReductionReferencePrice `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2011-01-25 data_id_source=`none` n_stocks=None n_dates=3770 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `ClosingPriceonTheLastTradingDay` | NUMERIC(20,6) |  |  |
| 3 | `PostReductionReferencePrice` | NUMERIC(20,6) |  |  |
| 4 | `LimitUp` | NUMERIC(20,6) |  |  |
| 5 | `LimitDown` | NUMERIC(20,6) |  |  |
| 6 | `OpeningReferencePrice` | NUMERIC(20,6) |  |  |
| 7 | `ExrightReferencePrice` | NUMERIC(20,6) |  |  |
| 8 | `ReasonforCapitalReduction` | VARCHAR(255) |  |  |

### TaiwanStockCashFlowsStatement `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`quarterly` earliest=2012-03-31 data_id_source=`roster` n_stocks=2208 n_dates=57 recon=`full-history` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `type` | VARCHAR(255) | 🔑 |  |
| 3 | `value` | NUMERIC(23,6) |  |  |
| 4 | `origin_name` | VARCHAR(255) |  |  |

### TaiwanStockDelisting `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2001-01-20 data_id_source=`none` n_stocks=None n_dates=6223 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE |  |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | VARCHAR(255) |  |  |

### TaiwanStockDividend `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2005-06-19 data_id_source=`roster` n_stocks=3101 n_dates=5143 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `year` | VARCHAR(255) |  |  |
| 3 | `StockEarningsDistribution` | NUMERIC(20,10) |  |  |
| 4 | `StockStatutorySurplus` | NUMERIC(20,10) |  |  |
| 5 | `StockExDividendTradingDate` | DATE |  |  |
| 6 | `TotalEmployeeStockDividend` | NUMERIC(20,6) |  |  |
| 7 | `TotalEmployeeStockDividendAmount` | NUMERIC(20,6) |  |  |
| 8 | `RatioOfEmployeeStockDividendOfTotal` | NUMERIC(20,6) |  |  |
| 9 | `RatioOfEmployeeStockDividend` | NUMERIC(20,8) |  |  |
| 10 | `CashEarningsDistribution` | NUMERIC(20,8) |  |  |
| 11 | `CashStatutorySurplus` | NUMERIC(20,6) |  |  |
| 12 | `CashExDividendTradingDate` | DATE |  |  |
| 13 | `CashDividendPaymentDate` | DATE |  |  |
| 14 | `TotalEmployeeCashDividend` | NUMERIC(21,6) |  |  |
| 15 | `TotalNumberOfCashCapitalIncrease` | NUMERIC(20,6) |  |  |
| 16 | `CashIncreaseSubscriptionRate` | NUMERIC(20,6) |  |  |
| 17 | `CashIncreaseSubscriptionpRrice` | NUMERIC(20,6) |  |  |
| 18 | `RemunerationOfDirectorsAndSupervisors` | NUMERIC(20,6) |  |  |
| 19 | `ParticipateDistributionOfTotalShares` | NUMERIC(21,6) |  |  |
| 20 | `AnnouncementDate` | DATE |  | ⚠️ |
| 21 | `AnnouncementTime` | VARCHAR(255) |  | ⚠️ |

### TaiwanStockDividendResult `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2005-05-19 data_id_source=`roster` n_stocks=245 n_dates=695 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `before_price` | NUMERIC(20,6) |  |  |
| 3 | `after_price` | NUMERIC(20,6) |  |  |
| 4 | `stock_and_cache_dividend` | NUMERIC(20,6) |  |  |
| 5 | `stock_or_cache_dividend` | VARCHAR(255) |  |  |
| 6 | `max_price` | NUMERIC(20,6) |  |  |
| 7 | `min_price` | NUMERIC(20,6) |  |  |
| 8 | `open_price` | NUMERIC(20,6) |  |  |
| 9 | `reference_price` | NUMERIC(20,6) |  |  |

### TaiwanStockFinancialStatements `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`quarterly` earliest=1991-12-31 data_id_source=`roster` n_stocks=2122 n_dates=138 recon=`full-history` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `type` | VARCHAR(255) | 🔑 |  |
| 3 | `value` | NUMERIC(23,6) |  |  |
| 4 | `origin_name` | VARCHAR(255) |  |  |

### TaiwanStockMarketValue `B` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2004-02-12 data_id_source=`roster` n_stocks=3101 n_dates=5474 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `market_value` | NUMERIC(24,6) |  |  |

### TaiwanStockMarketValueWeight `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2024-10-30 data_id_source=`roster` n_stocks=3101 n_dates=398 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `rank` | NUMERIC(20,6) |  |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | VARCHAR(255) |  |  |
| 3 | `weight_per` | NUMERIC(20,6) |  |  |
| 4 | `date` | DATE | 🔑 |  |
| 5 | `type` | VARCHAR(255) |  |  |

### TaiwanStockMonthRevenue `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`monthly` earliest=2002-02-01 data_id_source=`roster` n_stocks=2361 n_dates=293 recon=`full-history` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `country` | VARCHAR(255) | 🔑 |  |
| 3 | `revenue` | NUMERIC(22,6) |  |  |
| 4 | `revenue_month` | NUMERIC(20,6) |  |  |
| 5 | `revenue_year` | NUMERIC(20,6) |  |  |
| 6 | `create_time` | DATE |  | ⚠️ |

### TaiwanStockParValueChange `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2019-09-09 data_id_source=`none` n_stocks=None n_dates=1658 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | VARCHAR(255) |  |  |
| 3 | `before_close` | NUMERIC(20,6) |  |  |
| 4 | `after_ref_close` | NUMERIC(20,6) |  |  |
| 5 | `after_ref_max` | NUMERIC(20,6) |  |  |
| 6 | `after_ref_min` | NUMERIC(20,6) |  |  |
| 7 | `after_ref_open` | NUMERIC(20,6) |  |  |

### TaiwanStockSplitPrice `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2019-09-09 data_id_source=`none` n_stocks=None n_dates=1658 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `type` | VARCHAR(255) |  |  |
| 3 | `before_price` | NUMERIC(20,6) |  |  |
| 4 | `after_price` | NUMERIC(20,6) |  |  |
| 5 | `max_price` | NUMERIC(20,6) |  |  |
| 6 | `min_price` | NUMERIC(20,6) |  |  |
| 7 | `open_price` | NUMERIC(20,6) |  |  |


## finmind / TW-Others

### TaiwanBusinessIndicator `B` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=1990-01-01 data_id_source=`none` n_stocks=None n_dates=8931 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `leading` | NUMERIC(20,6) |  |  |
| 2 | `leading_notrend` | NUMERIC(20,6) |  |  |
| 3 | `coincident` | NUMERIC(20,6) |  |  |
| 4 | `coincident_notrend` | NUMERIC(20,6) |  |  |
| 5 | `lagging` | NUMERIC(20,6) |  |  |
| 6 | `lagging_notrend` | NUMERIC(20,6) |  |  |
| 7 | `monitoring` | NUMERIC(20,6) |  |  |
| 8 | `monitoring_color` | VARCHAR(255) |  |  |

### TaiwanStockIndustryChain `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2026-06-12 data_id_source=`roster` n_stocks=3101 n_dates=3 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 1 | `industry` | VARCHAR(255) |  |  |
| 2 | `sub_industry` | VARCHAR(255) |  |  |
| 3 | `date` | DATE |  |  |

### TaiwanStockNews `F` ✅
- ep=`/data` mode=`single-day` freq=`single-day` earliest=2010-03-02 data_id_source=`roster` n_stocks=2407 n_dates=4104 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | VARCHAR(255) | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `link` | TEXT |  |  |
| 3 | `source` | VARCHAR(255) |  |  |
| 4 | `title` | VARCHAR(255) |  |  |


## finmind / TW-Real-Time

### TaiwanFutOptTickInfo `S` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2026-06-01 data_id_source=`none` n_stocks=None n_dates=10 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `code` | VARCHAR(255) | 🔑 |  |
| 1 | `callput` | VARCHAR(255) |  |  |
| 2 | `date` | VARCHAR(255) |  |  |
| 3 | `name` | VARCHAR(255) |  |  |
| 4 | `listing_date` | DATE |  |  |
| 5 | `expire_price` | NUMERIC(20,6) |  |  |
| 6 | `update_date` | DATE |  |  |


## finmind / TW-Technical

### TaiwanStock10Year `B` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2011-01-24 data_id_source=`roster` n_stocks=3101 n_dates=3771 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `close` | NUMERIC(20,6) |  |  |

### TaiwanStockDayTrading `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2014-01-06 data_id_source=`roster` n_stocks=3101 n_dates=3048 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | DATE | 🔑 |  |
| 2 | `BuyAfterSale` | VARCHAR(255) |  |  |
| 3 | `Volume` | NUMERIC(20,6) |  |  |
| 4 | `BuyAmount` | NUMERIC(21,6) |  |  |
| 5 | `SellAmount` | NUMERIC(21,6) |  |  |

### TaiwanStockDayTradingSuspension `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2014-07-09 data_id_source=`roster` n_stocks=3101 n_dates=2925 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | DATE | 🔑 |  |
| 2 | `end_date` | DATE |  |  |
| 3 | `reason` | VARCHAR(255) |  |  |

### TaiwanStockEvery5SecondsIndex `B` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=2005-01-01 data_id_source=`none` n_stocks=None n_dates=5256 recon=`by-date` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `time` | VARCHAR(255) | 🔑 |  |
| 2 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 3 | `price` | NUMERIC(20,6) | 🔑 |  |
| 4 | `kind` | VARCHAR(255) | 🔑 |  |

### TaiwanStockInfo `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2020-06-03 data_id_source=`roster` n_stocks=3100 n_dates=174 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `industry_category` | VARCHAR(255) | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | VARCHAR(255) |  |  |
| 3 | `type` | VARCHAR(255) | 🔑 |  |
| 4 | `date` | DATE |  |  |

### TaiwanStockInfoWithWarrant `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2026-06-16 data_id_source=`roster` n_stocks=3101 n_dates=1 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `industry_category` | VARCHAR(255) | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | VARCHAR(255) |  |  |
| 3 | `type` | VARCHAR(255) | 🔑 |  |
| 4 | `date` | DATE | 🔑 |  |

### TaiwanStockInfoWithWarrantSummary `S` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2011-01-01 data_id_source=`none` n_stocks=3101 n_dates=3787 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | DATE |  |  |
| 2 | `close` | NUMERIC(20,6) |  |  |
| 3 | `target_stock_id` | NUMERIC(20,6) |  |  |
| 4 | `target_close` | NUMERIC(20,6) |  |  |
| 5 | `type` | VARCHAR(255) |  |  |
| 6 | `fulfillment_method` | VARCHAR(255) |  |  |
| 7 | `end_date` | DATE |  |  |
| 8 | `fulfillment_start_date` | VARCHAR(255) |  |  |
| 9 | `fulfillment_end_date` | VARCHAR(255) |  |  |
| 10 | `exercise_ratio` | NUMERIC(20,6) |  |  |
| 11 | `fulfillment_price` | NUMERIC(20,6) |  |  |

### TaiwanStockKBar `S` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=2019-01-01 data_id_source=`roster` n_stocks=3101 n_dates=1827 recon=`roster-scoped` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `minute` | VARCHAR(255) | 🔑 |  |
| 2 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 3 | `open` | NUMERIC(20,6) | 🔑 |  |
| 4 | `high` | NUMERIC(20,6) | 🔑 |  |
| 5 | `low` | NUMERIC(20,6) | 🔑 |  |
| 6 | `close` | NUMERIC(20,6) | 🔑 |  |
| 7 | `volume` | NUMERIC(20,6) | 🔑 |  |

### TaiwanStockMonthPrice `B` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1999-12-01 data_id_source=`roster` n_stocks=3101 n_dates=6502 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 1 | `ymonth` | VARCHAR(255) |  |  |
| 2 | `max` | NUMERIC(20,6) |  |  |
| 3 | `min` | NUMERIC(20,6) |  |  |
| 4 | `trading_volume` | NUMERIC(20,6) |  |  |
| 5 | `trading_money` | NUMERIC(23,6) |  |  |
| 6 | `trading_turnover` | NUMERIC(20,6) |  |  |
| 7 | `date` | DATE | 🔑 |  |
| 8 | `close` | NUMERIC(20,6) |  |  |
| 9 | `open` | NUMERIC(20,6) |  |  |
| 10 | `spread` | NUMERIC(20,6) |  |  |

### TaiwanStockPER `F` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2005-09-02 data_id_source=`roster` n_stocks=1919 n_dates=5103 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `dividend_yield` | NUMERIC(20,6) |  |  |
| 3 | `PER` | NUMERIC(20,6) |  |  |
| 4 | `PBR` | NUMERIC(20,6) |  |  |

### TaiwanStockPrice `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1994-09-13 data_id_source=`roster` n_stocks=2706 n_dates=7219 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `Trading_Volume` | NUMERIC(21,6) |  |  |
| 3 | `Trading_money` | NUMERIC(23,6) |  |  |
| 4 | `open` | NUMERIC(20,6) |  |  |
| 5 | `max` | NUMERIC(20,6) |  |  |
| 6 | `min` | NUMERIC(20,6) |  |  |
| 7 | `close` | NUMERIC(20,6) |  |  |
| 8 | `spread` | NUMERIC(20,6) |  |  |
| 9 | `Trading_turnover` | NUMERIC(20,6) |  |  |

### TaiwanStockPriceAdj `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1994-09-14 data_id_source=`roster` n_stocks=2758 n_dates=7321 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `Trading_Volume` | NUMERIC(21,6) |  |  |
| 3 | `Trading_money` | NUMERIC(23,6) |  |  |
| 4 | `open` | NUMERIC(20,6) |  |  |
| 5 | `max` | NUMERIC(20,6) |  |  |
| 6 | `min` | NUMERIC(20,6) |  |  |
| 7 | `close` | NUMERIC(20,6) |  |  |
| 8 | `spread` | NUMERIC(20,6) |  |  |
| 9 | `Trading_turnover` | NUMERIC(20,6) |  |  |

### TaiwanStockPriceLimit `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2000-01-03 data_id_source=`roster` n_stocks=3101 n_dates=6480 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `reference_price` | NUMERIC(20,6) |  |  |
| 3 | `limit_up` | NUMERIC(20,6) |  |  |
| 4 | `limit_down` | NUMERIC(20,6) |  |  |

### TaiwanStockPriceTick `B` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=2019-01-01 data_id_source=`roster` n_stocks=3101 n_dates=1827 recon=`roster-scoped` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `deal_price` | NUMERIC(20,6) | 🔑 |  |
| 3 | `volume` | NUMERIC(20,6) | 🔑 |  |
| 4 | `Time` | VARCHAR(255) | 🔑 |  |
| 5 | `TickType` | NUMERIC(20,6) | 🔑 |  |

### TaiwanStockStatisticsOfOrderBookAndTrade `F` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=2005-01-01 data_id_source=`none` n_stocks=None n_dates=5256 recon=`by-date` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `Time` | VARCHAR(255) | 🔑 |  |
| 1 | `TotalBuyOrder` | NUMERIC(20,6) |  |  |
| 2 | `TotalBuyVolume` | NUMERIC(20,6) |  |  |
| 3 | `TotalSellOrder` | NUMERIC(20,6) |  |  |
| 4 | `TotalSellVolume` | NUMERIC(20,6) |  |  |
| 5 | `TotalDealOrder` | NUMERIC(20,6) |  |  |
| 6 | `TotalDealVolume` | NUMERIC(20,6) |  |  |
| 7 | `TotalDealMoney` | NUMERIC(20,6) |  |  |
| 8 | `date` | DATE | 🔑 |  |

### TaiwanStockSuspended `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2025-03-01 data_id_source=`none` n_stocks=3101 n_dates=317 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE |  |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `suspension_time` | VARCHAR(255) |  |  |
| 3 | `resumption_date` | VARCHAR(255) |  |  |
| 4 | `resumption_time` | VARCHAR(255) |  |  |

### TaiwanStockTotalReturnIndex `F` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2003-01-02 data_id_source=`doc` n_stocks=2 n_dates=5746 recon=`by-dim-id` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `price` | NUMERIC(20,6) |  |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `date` | DATE | 🔑 |  |

### TaiwanStockTradingDate `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=1999-01-01 data_id_source=`none` n_stocks=1 n_dates=6727 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |

### TaiwanStockWeekPrice `B` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1999-12-20 data_id_source=`roster` n_stocks=3101 n_dates=6490 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 1 | `yweek` | VARCHAR(255) |  |  |
| 2 | `max` | NUMERIC(20,6) |  |  |
| 3 | `min` | NUMERIC(20,6) |  |  |
| 4 | `trading_volume` | NUMERIC(20,6) |  |  |
| 5 | `trading_money` | NUMERIC(22,6) |  |  |
| 6 | `trading_turnover` | NUMERIC(20,6) |  |  |
| 7 | `date` | DATE | 🔑 |  |
| 8 | `close` | NUMERIC(20,6) |  |  |
| 9 | `open` | NUMERIC(20,6) |  |  |
| 10 | `spread` | NUMERIC(20,6) |  |  |

### TaiwanVariousIndicators5Seconds `F` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=2005-01-01 data_id_source=`none` n_stocks=None n_dates=5256 recon=`by-date` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | VARCHAR(255) | 🔑 |  |
| 1 | `TAIEX` | NUMERIC(20,6) |  |  |


## finmind / Global Economic Data

### ExchangeRate `-` ✅
- ep=`/data` mode=`by-dim-id` freq=`daily` earliest=1990-01-02 data_id_source=`datalist` n_stocks=None n_dates=9771 recon=`by-dim-id` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `InterbankRate` | NUMERIC(20,6) |  |  |
| 1 | `InverseInterbankRate` | NUMERIC(20,6) |  |  |
| 2 | `country` | VARCHAR(255) | 🔑 |  |
| 3 | `date` | DATE | 🔑 |  |


## finmind / TW-Derivative

### TaiwanFutOptInstitutionalInvestors `-` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2017-07-01 data_id_source=`none` n_stocks=None n_dates=2195 recon=`by-date` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `name` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | DATE | 🔑 |  |
| 2 | `institutional_investors` | VARCHAR(255) | 🔑 |  |
| 3 | `long_deal_volume` | NUMERIC(20,6) |  |  |
| 4 | `long_deal_amount` | NUMERIC(20,6) |  |  |
| 5 | `short_deal_volume` | NUMERIC(20,6) |  |  |
| 6 | `short_deal_amount` | NUMERIC(20,6) |  |  |
| 7 | `long_open_interest_balance_volume` | NUMERIC(20,6) |  |  |
| 8 | `long_open_interest_balance_amount` | NUMERIC(20,6) |  |  |
| 9 | `short_open_interest_balance_volume` | NUMERIC(20,6) |  |  |
| 10 | `short_open_interest_balance_amount` | NUMERIC(20,6) |  |  |

### TaiwanFuturesSpreadTick `-` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2026-05-01 data_id_source=`none` n_stocks=None n_dates=30 recon=`by-date` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `contract_date` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | DATE | 🔑 |  |
| 2 | `time` | VARCHAR(255) | 🔑 |  |
| 3 | `far_price` | NUMERIC(20,6) | 🔑 |  |
| 4 | `futures_id` | VARCHAR(255) | 🔑 |  |
| 5 | `near_price` | NUMERIC(20,6) | 🔑 |  |
| 6 | `price` | NUMERIC(20,6) | 🔑 |  |
| 7 | `spread_to_spread` | NUMERIC(20,6) | 🔑 |  |
| 8 | `volume` | NUMERIC(20,6) | 🔑 |  |


## finmind / TW-Chip

### TaiwanStockBlockTradingDailyReport `-` 🚫excl
- ep=`/data` mode=`excluded` freq=`daily` earliest=NULL(需per-stock且鉅額對個股稀疏,by-date/2330皆探不到→earliest需全市場全史掃(放量)) data_id_source=`roster` n_stocks=3101 n_dates=None recon=`roster-scoped` prov=`ingest.BACKFILL_DEFERRED`
  - ⚠️ 可抓但暫緩自動 backfill（規模/scope 待決，非物理不可行）；抓法已實證
  - 📝 實證 2026-06-16：分點/權證走 dedicated endpoint（finmind.fetch_dedicated）、鉅額走 /data；全市場全史規模大→scope 屬放量決策

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `securities_trader` | VARCHAR(255) | 🔑 |  |
| 1 | `price` | NUMERIC(20,6) | 🔑 |  |
| 2 | `buy` | NUMERIC(20,6) | 🔑 |  |
| 3 | `sell` | NUMERIC(20,6) | 🔑 |  |
| 4 | `trade_type` | VARCHAR(255) | 🔑 |  |
| 5 | `securities_trader_id` | VARCHAR(255) | 🔑 |  |
| 6 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 7 | `date` | DATE | 🔑 |  |


## finmind / TW-Technical

### TaiwanStockDayTradingBorrowingFeeRate `-` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2015-10-14 data_id_source=`roster` n_stocks=3101 n_dates=2615 recon=`roster-scoped` prov=`probe`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | VARCHAR(255) |  |  |
| 3 | `InvestorBorrowedShares` | NUMERIC(20,6) |  |  |
| 4 | `InvestorBorrowingFeeRate` | NUMERIC(20,6) |  |  |


## finmind / TW-Chip

### TaiwanStockInstitutionalInvestorsBuySellWide `-` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2012-05-02 data_id_source=`roster` n_stocks=422 n_dates=3205 recon=`roster-scoped` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `date` | DATE | 🔑 |  |
| 1 | `stock_id` | VARCHAR(255) | 🔑 |  |
| 2 | `Foreign_Investor_buy` | NUMERIC(20,6) |  |  |
| 3 | `Foreign_Investor_sell` | NUMERIC(20,6) |  |  |
| 4 | `Foreign_Dealer_Self_buy` | NUMERIC(20,6) |  |  |
| 5 | `Foreign_Dealer_Self_sell` | NUMERIC(20,6) |  |  |
| 6 | `Investment_Trust_buy` | NUMERIC(20,6) |  |  |
| 7 | `Investment_Trust_sell` | NUMERIC(20,6) |  |  |
| 8 | `Dealer_buy` | NUMERIC(20,6) |  |  |
| 9 | `Dealer_sell` | NUMERIC(20,6) |  |  |
| 10 | `Dealer_self_buy` | NUMERIC(20,6) |  |  |
| 11 | `Dealer_self_sell` | NUMERIC(20,6) |  |  |
| 12 | `Dealer_Hedging_buy` | NUMERIC(20,6) |  |  |
| 13 | `Dealer_Hedging_sell` | NUMERIC(20,6) |  |  |


## fred / Macro

### fred_series `-` ✅
- ep=`/series/observations` mode=`per-series` freq=`daily` earliest=1919-01-01 data_id_source=`series` n_stocks=None n_dates=15238 recon=`by-dim-id` prov=`DB`

| # | column | type | pk | a-l |
|--|--|--|--|--|
| 0 | `series_id` | VARCHAR(255) | 🔑 |  |
| 1 | `date` | DATE | 🔑 |  |
| 2 | `value` | NUMERIC(20,6) |  |  |


## ⭐ Dedicated endpoint datasets(官方doc、不在list_datasets、catalog待rebuild補)

### TaiwanStockTradingDailyReportSecIdAgg `Sponsor` 🚫dedicated
- section=Taiwan Market - Chip / Institutional · params=

| # | column |
|--|--|
| 0 | `securities_trader` |
| 1 | `securities_trader_id` |
| 2 | `stock_id` |
| 3 | `date` |
| 4 | `buy_volume` |
| 5 | `sell_volume` |
| 6 | `buy_price` |
| 7 | `sell_price` |

### taiwan_stock_tick_snapshot `Sponsor` 🚫dedicated
- section=Taiwan Market - Real-Time · params=

| # | column |
|--|--|
| 0 | `close` |
| 1 | `high` |
| 2 | `low` |
| 3 | `open` |
| 4 | `volume` |
| 5 | `total_volume` |
| 6 | `change_price` |
| 7 | `change_rate` |
| 8 | `date` |
| 9 | `stock_id` |

### taiwan_futures_snapshot `Sponsor` 🚫dedicated
- section=Taiwan Market - Real-Time · params=

| # | column |
|--|--|
| 0 | `open` |
| 1 | `high` |
| 2 | `low` |
| 3 | `close` |
| 4 | `volume` |
| 5 | `total_volume` |
| 6 | `change_price` |
| 7 | `change_rate` |
| 8 | `date` |
| 9 | `futures_id` |

### taiwan_options_snapshot `Sponsor` 🚫dedicated
- section=Taiwan Market - Real-Time · params=

| # | column |
|--|--|
| 0 | `open` |
| 1 | `high` |
| 2 | `low` |
| 3 | `close` |
| 4 | `volume` |
| 5 | `total_volume` |
| 6 | `change_price` |
| 7 | `change_rate` |
| 8 | `date` |
| 9 | `options_id` |

# augur catalog — 全 table × field 完整清單 (FinMind 98 + FRED 1 = 99)

> catalog DB(95 實證、單次乾淨 build + review 修正)+ 官方 datasets.md(4 dedicated)。**表名中文 95/95 + 欄名中文全覆蓋**(datasets_zh.md SSOT)。dirty 欄強制 VARCHAR、FULL_START 探源頭真起點(US 1928/UK 1968/CrudeOil 1986…)。每欄值或實證原因。


## finmind / Global Economic Data

### CnnFearGreedIndex｜CNN 恐懼貪婪指數 `B` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2011-01-03 data_id_source=`none` n_stocks=None n_dates=3919 recon=`by-date` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 資料日期 | DATE | 🔑 |  |
| 1 | `fear_greed` | 恐懼貪婪指數（0-100） | NUMERIC(20,6) |  |  |
| 2 | `fear_greed_emotion` | 情緒分類（極度恐懼…極度貪婪） | VARCHAR(255) |  |  |

### CrudeOilPrices｜原油價格 `F` ✅
- ep=`/data` mode=`by-dim-id` freq=`daily` earliest=1986-04-01 data_id_source=`datalist` n_stocks=2 n_dates=9851 recon=`by-dim-id` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 資料日期 | DATE | 🔑 |  |
| 1 | `name` | 油種名稱（WTI/Brent） | VARCHAR(255) |  |  |
| 2 | `price` | 油價（美元/桶） | NUMERIC(20,6) |  |  |

### ExchangeRate｜外幣匯率（銀行間 by 國家） `F` ✅
- ep=`/data` mode=`by-dim-id` freq=`daily` earliest=1990-01-02 data_id_source=`datalist` n_stocks=None n_dates=9771 recon=`by-dim-id` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `InterbankRate` | 銀行間匯率 | NUMERIC(20,6) |  |  |
| 1 | `InverseInterbankRate` | 反向銀行間匯率 | NUMERIC(20,6) |  |  |
| 2 | `country` | 國家／幣別 | VARCHAR(255) | 🔑 |  |
| 3 | `date` | 日期 | DATE | 🔑 |  |

### GoldPrice｜黃金價格 `F` ✅
- ep=`/data` mode=`single-day` freq=`single-day` earliest=1979-01-01 data_id_source=`none` n_stocks=None n_dates=11627 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `Price` | 金價 | NUMERIC(20,6) |  |  |
| 1 | `date` | 資料日期 | VARCHAR(255) | 🔑 |  |

### GovernmentBondsYield｜美國國債殖利率 `F` ✅
- ep=`/data` mode=`by-dim-id` freq=`daily` earliest=2001-01-02 data_id_source=`datalist` n_stocks=13 n_dates=6236 recon=`by-dim-id` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 資料日期 | DATE | 🔑 |  |
| 1 | `name` | 期別名稱（如 United States 10-Year） | VARCHAR(255) |  |  |
| 2 | `value` | 殖利率（%） | NUMERIC(20,6) |  |  |

### InterestRate｜央行利率 `F` ✅
- ep=`/data` mode=`by-dim-id` freq=`daily` earliest=2008-02-01 data_id_source=`datalist` n_stocks=12 n_dates=4501 recon=`by-dim-id` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `country` | 國家／央行 | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 資料日期 | DATE | 🔑 |  |
| 2 | `full_country_name` | 國家全名 | VARCHAR(255) |  |  |
| 3 | `interest_rate` | 政策利率（%） | NUMERIC(20,6) |  |  |

### TaiwanExchangeRate｜外幣匯率 `F` ✅
- ep=`/data` mode=`by-dim-id` freq=`daily` earliest=2006-01-02 data_id_source=`datalist` n_stocks=None n_dates=4638 recon=`by-dim-id` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 資料日期 | DATE | 🔑 |  |
| 1 | `currency` | 幣別 | VARCHAR(255) | 🔑 |  |
| 2 | `cash_buy` | 現金買入匯率 | NUMERIC(20,6) |  |  |
| 3 | `cash_sell` | 現金賣出匯率 | NUMERIC(20,6) |  |  |
| 4 | `spot_buy` | 即期買入匯率 | NUMERIC(20,6) |  |  |
| 5 | `spot_sell` | 即期賣出匯率 | NUMERIC(20,6) |  |  |


## finmind / International Markets

### EuropeStockInfo｜歐股總覽 `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2019-01-14 data_id_source=`none` n_stocks=None n_dates=1818 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE |  |  |
| 1 | `stock_id` | 代號 | VARCHAR(255) | 🔑 |  |
| 2 | `Market` | 市場 | VARCHAR(255) |  |  |
| 3 | `stock_name` | 名稱 | VARCHAR(255) |  |  |

### EuropeStockPrice｜歐股股價 `F` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1980-04-01 data_id_source=`none` n_stocks=3101 n_dates=11321 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE |  |  |
| 1 | `stock_id` | 代號 | VARCHAR(255) | 🔑 |  |
| 2 | `Adj_Close` | 還原收盤價 | NUMERIC(20,6) |  |  |
| 3 | `Close` | 收盤價 | NUMERIC(20,6) |  |  |
| 4 | `High` | 最高價 | NUMERIC(20,6) |  |  |
| 5 | `Low` | 最低價 | NUMERIC(20,6) |  |  |
| 6 | `Open` | 開盤價 | NUMERIC(20,6) |  |  |
| 7 | `Volume` | 成交量 | NUMERIC(20,6) |  |  |

### JapanStockInfo｜日股總覽 `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2019-01-14 data_id_source=`none` n_stocks=None n_dates=1818 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 代號 | VARCHAR(255) | 🔑 |  |
| 2 | `Exchange` | 交易所 | VARCHAR(255) | 🔑 |  |
| 3 | `Sector` | 產業別 | VARCHAR(255) |  |  |
| 4 | `stock_name` | 名稱 | VARCHAR(255) | 🔑 |  |

### JapanStockPrice｜日股股價 `F` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1999-05-01 data_id_source=`none` n_stocks=3101 n_dates=6646 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE |  |  |
| 1 | `stock_id` | 代號 | VARCHAR(255) | 🔑 |  |
| 2 | `Adj_Close` | 還原收盤價 | NUMERIC(20,6) |  |  |
| 3 | `Close` | 收盤價 | NUMERIC(20,6) |  |  |
| 4 | `High` | 最高價 | NUMERIC(20,6) |  |  |
| 5 | `Low` | 最低價 | NUMERIC(20,6) |  |  |
| 6 | `Open` | 開盤價 | NUMERIC(20,6) |  |  |
| 7 | `Volume` | 成交量 | NUMERIC(20,6) |  |  |

### UKStockInfo｜英股總覽 `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2019-01-31 data_id_source=`none` n_stocks=None n_dates=1806 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 代號 | VARCHAR(255) | 🔑 |  |
| 2 | `Country` | 國家 | VARCHAR(255) | 🔑 |  |
| 3 | `stock_name` | 名稱 | VARCHAR(255) | 🔑 |  |

### UKStockPrice｜英股股價 `F` ✅
- ep=`/data` mode=`by-date` freq=`yearly` earliest=1968-01-01 data_id_source=`roster` n_stocks=231 n_dates=1 recon=`full-history` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE |  |  |
| 1 | `stock_id` | 代號 | VARCHAR(255) | 🔑 |  |
| 2 | `Adj_Close` | 還原收盤價 | NUMERIC(20,6) |  |  |
| 3 | `Close` | 收盤價 | NUMERIC(20,6) |  |  |
| 4 | `High` | 最高價 | NUMERIC(20,6) |  |  |
| 5 | `Low` | 最低價 | NUMERIC(20,6) |  |  |
| 6 | `Open` | 開盤價 | NUMERIC(20,6) |  |  |
| 7 | `Volume` | 成交量 | NUMERIC(20,6) |  |  |

### USStockInfo｜美股總覽 `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2019-01-01 data_id_source=`roster` n_stocks=16709 n_dates=241 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE |  |  |
| 1 | `stock_id` | 代號 | VARCHAR(255) |  |  |
| 2 | `Country` | 國家 | VARCHAR(255) |  |  |
| 3 | `IPOYear` | 上市年度 | NUMERIC(20,6) |  |  |
| 4 | `MarketCap` | 市值 | NUMERIC(24,6) |  |  |
| 5 | `Subsector` | 次產業別 | VARCHAR(255) |  |  |
| 6 | `stock_name` | 名稱 | VARCHAR(255) | 🔑 |  |

### USStockPrice｜美股股價 `F` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1928-02-01 data_id_source=`roster` n_stocks=1477 n_dates=1952 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 代號 | VARCHAR(255) | 🔑 |  |
| 2 | `Adj_Close` | 還原收盤價 | NUMERIC(21,6) |  |  |
| 3 | `Close` | 收盤價 | NUMERIC(21,6) |  |  |
| 4 | `High` | 最高價 | NUMERIC(21,6) |  |  |
| 5 | `Low` | 最低價 | NUMERIC(21,6) |  |  |
| 6 | `Open` | 開盤價 | NUMERIC(21,6) |  |  |
| 7 | `Volume` | 成交量 | NUMERIC(20,6) |  |  |

### USStockPriceMinute｜美股分鐘價 `B` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=2021-05-01 data_id_source=`info-roster` n_stocks=16709 n_dates=1256 recon=`by-dim-id` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | VARCHAR(255) | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `close` | 收盤價 | NUMERIC(20,6) |  |  |
| 3 | `high` | 最高價 | NUMERIC(20,6) |  |  |
| 4 | `low` | 最低價 | NUMERIC(20,6) |  |  |
| 5 | `open` | 開盤價 | NUMERIC(20,6) |  |  |
| 6 | `volume` | 成交量(口) | NUMERIC(20,6) |  |  |


## finmind / TW-Chip

### TaiwanStockBlockTradingDailyReport｜鉅額交易日報表 `S` 🚫excl
- ep=`/data` mode=`excluded` freq=`daily` earliest=2026-05-01 data_id_source=`roster` n_stocks=3101 n_dates=31 recon=`roster-scoped` prov=`dedicated-probe`
  - ⚠️ 抓法+欄位/earliest 已實證真實 probe（分點/權證 dedicated endpoint、鉅額 /data）；全史 bulk 落地屬 sync operational（per-(股,日)規模）、非 catalog 缺資料

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `securities_trader` | 券商名稱 | VARCHAR(255) | 🔑 |  |
| 1 | `price` | 指數值 | NUMERIC(20,6) | 🔑 |  |
| 2 | `buy` | 買進 | NUMERIC(20,6) | 🔑 |  |
| 3 | `sell` | 賣出 | NUMERIC(20,6) | 🔑 |  |
| 4 | `trade_type` | 交易類別（配對／逐筆） | VARCHAR(255) | 🔑 |  |
| 5 | `securities_trader_id` | 券商代號 | VARCHAR(255) | 🔑 |  |
| 6 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 7 | `date` | 日期 | DATE | 🔑 |  |

### TaiwanStockInstitutionalInvestorsBuySellWide｜三大法人買賣超（寬表） `F` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2012-05-02 data_id_source=`roster` n_stocks=422 n_dates=3205 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `Foreign_Investor_buy` | 外資買進 | NUMERIC(20,6) |  |  |
| 3 | `Foreign_Investor_sell` | 外資賣出 | NUMERIC(20,6) |  |  |
| 4 | `Foreign_Dealer_Self_buy` | 外資自營買進 | NUMERIC(20,6) |  |  |
| 5 | `Foreign_Dealer_Self_sell` | 外資自營賣出 | NUMERIC(20,6) |  |  |
| 6 | `Investment_Trust_buy` | 投信買進 | NUMERIC(20,6) |  |  |
| 7 | `Investment_Trust_sell` | 投信賣出 | NUMERIC(20,6) |  |  |
| 8 | `Dealer_buy` | 自營商買進 | NUMERIC(20,6) |  |  |
| 9 | `Dealer_sell` | 自營商賣出 | NUMERIC(20,6) |  |  |
| 10 | `Dealer_self_buy` | 自營商自行買賣買進 | NUMERIC(20,6) |  |  |
| 11 | `Dealer_self_sell` | 自營商自行買賣賣出 | NUMERIC(20,6) |  |  |
| 12 | `Dealer_Hedging_buy` | 自營商避險買進 | NUMERIC(20,6) |  |  |
| 13 | `Dealer_Hedging_sell` | 自營商避險賣出 | NUMERIC(20,6) |  |  |


## finmind / TW-Chip / Institutional

### TaiwanDailyShortSaleBalances｜融券借券餘額 `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2005-07-01 data_id_source=`roster` n_stocks=2239 n_dates=5125 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 1 | `MarginShortSalesPreviousDayBalance` | 融券前日餘額 | NUMERIC(20,6) |  |  |
| 2 | `MarginShortSalesShortSales` | 融券賣出 | NUMERIC(20,6) |  |  |
| 3 | `MarginShortSalesShortCovering` | 融券買進（回補） | NUMERIC(20,6) |  |  |
| 4 | `MarginShortSalesStockRedemption` | 融券現券償還 | NUMERIC(20,6) |  |  |
| 5 | `MarginShortSalesCurrentDayBalance` | 融券當日餘額 | NUMERIC(20,6) |  |  |
| 6 | `MarginShortSalesQuota` | 融券限額 | NUMERIC(20,6) |  |  |
| 7 | `SBLShortSalesPreviousDayBalance` | 借券賣出前日餘額 | NUMERIC(20,6) |  |  |
| 8 | `SBLShortSalesShortSales` | 借券賣出 | NUMERIC(20,6) |  |  |
| 9 | `SBLShortSalesReturns` | 借券賣出返還 | NUMERIC(20,6) |  |  |
| 10 | `SBLShortSalesAdjustments` | 借券賣出調整 | NUMERIC(20,6) |  |  |
| 11 | `SBLShortSalesCurrentDayBalance` | 借券賣出當日餘額 | NUMERIC(20,6) |  |  |
| 12 | `SBLShortSalesQuota` | 借券賣出限額 | NUMERIC(20,6) |  |  |
| 13 | `SBLShortSalesShortCovering` | 借券賣出回補 | NUMERIC(20,6) |  |  |
| 14 | `date` | 日期 | DATE | 🔑 |  |

### TaiwanSecuritiesTraderInfo｜證券商資訊 `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2025-02-01 data_id_source=`none` n_stocks=1 n_dates=335 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `securities_trader_id` | 券商代號 | VARCHAR(255) | 🔑 |  |
| 1 | `securities_trader` | 券商名稱 | VARCHAR(255) |  |  |
| 2 | `date` | 日期 | DATE |  |  |
| 3 | `address` | 地址 | VARCHAR(255) |  |  |
| 4 | `phone` | 電話 | VARCHAR(255) |  |  |

### TaiwanStockBlockTrade｜鉅額交易 `S` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2006-08-11 data_id_source=`roster` n_stocks=3101 n_dates=4862 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `trade_type` | 交易類別（配對／逐筆） | VARCHAR(255) | 🔑 |  |
| 3 | `price` | 成交價 | NUMERIC(20,6) | 🔑 |  |
| 4 | `volume` | 成交量（股） | NUMERIC(21,6) | 🔑 |  |
| 5 | `trading_money` | 成交金額 | NUMERIC(23,6) | 🔑 |  |

### TaiwanStockDispositionSecuritiesPeriod｜處置有價證券 `B` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2005-01-01 data_id_source=`none` n_stocks=3101 n_dates=5256 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE |  |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | 股票名稱 | VARCHAR(255) |  |  |
| 3 | `disposition_cnt` | 處置次數 | NUMERIC(20,6) |  |  |
| 4 | `condition` | 處置條件 | VARCHAR(255) |  |  |
| 5 | `measure` | 處置措施 | VARCHAR(255) |  |  |
| 6 | `period_start` | 處置起始日 | DATE |  |  |
| 7 | `period_end` | 處置截止日 | DATE |  |  |

### TaiwanStockGovernmentBankBuySell｜八大行庫買賣 `S` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2021-07-01 data_id_source=`roster` n_stocks=2623 n_dates=1200 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `buy_amount` | 買進金額 | NUMERIC(21,6) | 🔑 |  |
| 3 | `sell_amount` | 賣出金額 | NUMERIC(20,6) | 🔑 |  |
| 4 | `buy` | 買進股數 | NUMERIC(20,6) | 🔑 |  |
| 5 | `sell` | 賣出股數 | NUMERIC(20,6) | 🔑 |  |
| 6 | `bank_name` | 行庫名稱 | VARCHAR(255) | 🔑 |  |

### TaiwanStockHoldingSharesPer｜股權持股分級 `B` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2010-01-29 data_id_source=`roster` n_stocks=3101 n_dates=4013 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `HoldingSharesLevel` | 持股分級級距 | VARCHAR(255) | 🔑 |  |
| 3 | `people` | 持股人數 | NUMERIC(20,6) |  |  |
| 4 | `percent` | 持股比率 | NUMERIC(20,6) |  |  |
| 5 | `unit` | 持股單位數（張） | NUMERIC(21,6) |  |  |

### TaiwanStockInstitutionalInvestorsBuySell｜三大法人買賣超 `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2012-05-02 data_id_source=`roster` n_stocks=2497 n_dates=3445 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `buy` | 買進 | NUMERIC(20,6) |  |  |
| 3 | `name` | 法人別（自營商／自營商避險／自營商自行買賣／外資自營商／外資／投信） | VARCHAR(255) | 🔑 |  |
| 4 | `sell` | 賣出 | NUMERIC(20,6) |  |  |

### TaiwanStockLoanCollateralBalance｜借貸款項擔保品餘額 `S` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2006-10-02 data_id_source=`roster` n_stocks=3101 n_dates=4828 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `market` | 市場別 | VARCHAR(255) |  |  |
| 3 | `MarginPreviousDayBalance` | 融資前日餘額 | NUMERIC(20,6) |  |  |
| 4 | `MarginBuy` | 融資買進 | NUMERIC(20,6) |  |  |
| 5 | `MarginSell` | 融資賣出 | NUMERIC(20,6) |  |  |
| 6 | `MarginCashRedemption` | 融資現金償還 | NUMERIC(20,6) |  |  |
| 7 | `MarginCurrentDayBalance` | 融資當日餘額 | NUMERIC(20,6) |  |  |
| 8 | `MarginNextDayQuota` | 融資次日限額 | NUMERIC(20,6) |  |  |
| 9 | `SecuritiesFirmLoanPreviousDayBalance` | 券商借貸前日餘額 | NUMERIC(20,6) |  |  |
| 10 | `SecuritiesFirmLoanBuy` | 券商借貸買進 | NUMERIC(20,6) |  |  |
| 11 | `SecuritiesFirmLoanSell` | 券商借貸賣出 | NUMERIC(20,6) |  |  |
| 12 | `SecuritiesFirmLoanCashRedemption` | 券商借貸現金償還 | NUMERIC(20,6) |  |  |
| 13 | `SecuritiesFirmLoanReplacement` | 券商借貸代償 | NUMERIC(20,6) |  |  |
| 14 | `SecuritiesFirmLoanCurrentDayBalance` | 券商借貸當日餘額 | NUMERIC(20,6) |  |  |
| 15 | `SecuritiesFirmLoanNextDayQuota` | 券商借貸次日限額 | NUMERIC(20,6) |  |  |
| 16 | `UnrestrictedLoanPreviousDayBalance` | 不限用途借貸前日餘額 | NUMERIC(20,6) |  |  |
| 17 | `UnrestrictedLoanBuy` | 不限用途借貸買進 | NUMERIC(20,6) |  |  |
| 18 | `UnrestrictedLoanSell` | 不限用途借貸賣出 | NUMERIC(20,6) |  |  |
| 19 | `UnrestrictedLoanCashRedemption` | 不限用途借貸現金償還 | NUMERIC(20,6) |  |  |
| 20 | `UnrestrictedLoanReplacement` | 不限用途借貸代償 | NUMERIC(20,6) |  |  |
| 21 | `UnrestrictedLoanCurrentDayBalance` | 不限用途借貸當日餘額 | NUMERIC(20,6) |  |  |
| 22 | `UnrestrictedLoanNextDayQuota` | 不限用途借貸次日限額 | NUMERIC(20,6) |  |  |
| 23 | `SecuritiesFinanceSecuredLoanPreviousDayBalance` | 證金公司擔保放款前日餘額 | NUMERIC(20,6) |  |  |
| 24 | `SecuritiesFinanceSecuredLoanBuy` | 證金公司擔保放款買進 | NUMERIC(20,6) |  |  |
| 25 | `SecuritiesFinanceSecuredLoanSell` | 證金公司擔保放款賣出 | NUMERIC(20,6) |  |  |
| 26 | `SecuritiesFinanceSecuredLoanCashRedemption` | 證金公司擔保放款現金償還 | NUMERIC(20,6) |  |  |
| 27 | `SecuritiesFinanceSecuredLoanReplacement` | 證金公司擔保放款代償 | NUMERIC(20,6) |  |  |
| 28 | `SecuritiesFinanceSecuredLoanCurrentDayBalance` | 證金公司擔保放款當日餘額 | NUMERIC(20,6) |  |  |
| 29 | `SecuritiesFinanceSecuredLoanNextDayQuota` | 證金公司擔保放款次日限額 | NUMERIC(20,6) |  |  |
| 30 | `SettlementMarginPreviousDayBalance` | 交割保證金前日餘額 | NUMERIC(20,6) |  |  |
| 31 | `SettlementMarginBuy` | 交割保證金買進 | NUMERIC(20,6) |  |  |
| 32 | `SettlementMarginSell` | 交割保證金賣出 | NUMERIC(20,6) |  |  |
| 33 | `SettlementMarginCashRedemption` | 交割保證金現金償還 | NUMERIC(20,6) |  |  |
| 34 | `SettlementMarginReplacement` | 交割保證金代償 | NUMERIC(20,6) |  |  |
| 35 | `SettlementMarginCurrentDayBalance` | 交割保證金當日餘額 | NUMERIC(20,6) |  |  |
| 36 | `SettlementMarginNextDayQuota` | 交割保證金次日限額 | NUMERIC(20,6) |  |  |

### TaiwanStockMarginPurchaseShortSale｜融資融券 `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2001-01-05 data_id_source=`roster` n_stocks=2168 n_dates=6163 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `MarginPurchaseBuy` | 融資買進 | NUMERIC(20,6) |  |  |
| 3 | `MarginPurchaseCashRepayment` | 融資現金償還 | NUMERIC(20,6) |  |  |
| 4 | `MarginPurchaseLimit` | 融資限額 | NUMERIC(20,6) |  |  |
| 5 | `MarginPurchaseSell` | 融資賣出 | NUMERIC(20,6) |  |  |
| 6 | `MarginPurchaseTodayBalance` | 融資今日餘額 | NUMERIC(20,6) |  |  |
| 7 | `MarginPurchaseYesterdayBalance` | 融資昨日餘額 | NUMERIC(20,6) |  |  |
| 8 | `Note` | 註記 | VARCHAR(255) |  |  |
| 9 | `OffsetLoanAndShort` | 資券相抵 | NUMERIC(20,6) |  |  |
| 10 | `ShortSaleBuy` | 融券買進 | NUMERIC(20,6) |  |  |
| 11 | `ShortSaleCashRepayment` | 融券現金償還 | NUMERIC(20,6) |  |  |
| 12 | `ShortSaleLimit` | 融券限額 | NUMERIC(20,6) |  |  |
| 13 | `ShortSaleSell` | 融券賣出 | NUMERIC(20,6) |  |  |
| 14 | `ShortSaleTodayBalance` | 融券今日餘額 | NUMERIC(20,6) |  |  |
| 15 | `ShortSaleYesterdayBalance` | 融券昨日餘額 | NUMERIC(20,6) |  |  |

### TaiwanStockMarginShortSaleSuspension｜暫停融券賣出 `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2015-04-01 data_id_source=`roster` n_stocks=3101 n_dates=2746 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 起始日期 | DATE | 🔑 |  |
| 2 | `end_date` | 截止日期 | DATE |  |  |
| 3 | `reason` | 暫停事由 | VARCHAR(255) |  |  |

### TaiwanStockSecuritiesLending｜借券成交 `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2003-11-11 data_id_source=`roster` n_stocks=3101 n_dates=5536 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `transaction_type` | 交易類別 | VARCHAR(255) | 🔑 |  |
| 3 | `volume` | 成交量（股） | NUMERIC(20,6) | 🔑 |  |
| 4 | `fee_rate` | 費率 | NUMERIC(20,6) | 🔑 |  |
| 5 | `close` | 收盤價 | NUMERIC(20,6) | 🔑 |  |
| 6 | `original_return_date` | 原訂還券日期 | VARCHAR(255) |  |  |
| 7 | `original_lending_period` | 原訂借券期間（天） | NUMERIC(20,6) | 🔑 |  |

### TaiwanStockShareholding｜外資持股 `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2004-02-12 data_id_source=`roster` n_stocks=2316 n_dates=5514 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 證券代號 | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | 證券名稱 | VARCHAR(255) |  |  |
| 3 | `InternationalCode` | 國際證券代碼（ISIN） | VARCHAR(255) |  |  |
| 4 | `ForeignInvestmentRemainingShares` | 外資尚可投資股數 | NUMERIC(21,6) |  |  |
| 5 | `ForeignInvestmentShares` | 全體外資持有股數 | NUMERIC(21,6) |  |  |
| 6 | `ForeignInvestmentRemainRatio` | 外資尚可投資比率 | NUMERIC(20,6) |  |  |
| 7 | `ForeignInvestmentSharesRatio` | 外資持股比率 | NUMERIC(20,6) |  |  |
| 8 | `ForeignInvestmentUpperLimitRatio` | 外資法令投資上限比率 | NUMERIC(20,6) |  |  |
| 9 | `ChineseInvestmentUpperLimitRatio` | 外資及陸資共用法令投資上限比率 | NUMERIC(20,6) |  |  |
| 10 | `NumberOfSharesIssued` | 發行股數 | NUMERIC(21,6) |  |  |
| 11 | `RecentlyDeclareDate` | 最近一次申報外資持股異動日期 ⭐ | VARCHAR(255) |  | ⚠️ |
| 12 | `note` | 與前日異動原因（註） | VARCHAR(255) |  |  |

### TaiwanStockTotalInstitutionalInvestors｜整體三大法人 `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2004-04-07 data_id_source=`none` n_stocks=None n_dates=5458 recon=`by-date` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `buy` | 買進 | NUMERIC(23,6) |  |  |
| 1 | `date` | 日期 | DATE | 🔑 |  |
| 2 | `name` | 法人別 | VARCHAR(255) | 🔑 |  |
| 3 | `sell` | 賣出 | NUMERIC(23,6) |  |  |

### TaiwanStockTotalMarginPurchaseShortSale｜整體市場融資融券 `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2001-01-01 data_id_source=`none` n_stocks=None n_dates=6236 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `TodayBalance` | 當日餘額 | NUMERIC(22,6) |  |  |
| 1 | `YesBalance` | 前日餘額 | NUMERIC(22,6) |  |  |
| 2 | `buy` | 買進 | NUMERIC(21,6) |  |  |
| 3 | `date` | 日期 | DATE | 🔑 |  |
| 4 | `name` | 類別名稱（融資／融券） | VARCHAR(255) | 🔑 |  |
| 5 | `Return` | 償還 | NUMERIC(20,6) |  |  |
| 6 | `sell` | 賣出 | NUMERIC(21,6) |  |  |

### TaiwanStockTradingDailyReport｜券商分點進出日報 `S` 🚫excl
- ep=`/taiwan_stock_trading_daily_report` mode=`excluded` freq=`daily` earliest=2021-07-01 data_id_source=`dedicated` n_stocks=None n_dates=1215 recon=`by-date` prov=`dedicated-probe`
  - ⚠️ 抓法+欄位/earliest 已實證真實 probe（分點/權證 dedicated endpoint、鉅額 /data）；全史 bulk 落地屬 sync operational（per-(股,日)規模）、非 catalog 缺資料

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `securities_trader` | 券商名稱 | VARCHAR(255) | 🔑 |  |
| 1 | `price` | 指數值 | NUMERIC(20,6) | 🔑 |  |
| 2 | `buy` | 買進 | NUMERIC(20,6) | 🔑 |  |
| 3 | `sell` | 賣出 | NUMERIC(20,6) | 🔑 |  |
| 4 | `securities_trader_id` | 券商代號 | VARCHAR(255) | 🔑 |  |
| 5 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 6 | `date` | 日期 | DATE | 🔑 |  |

### TaiwanStockWarrantTradingDailyReport｜權證分點進出日報 `S` 🚫excl
- ep=`/taiwan_stock_warrant_trading_daily_report` mode=`excluded` freq=`daily` earliest=NULL data_id_source=`dedicated` n_stocks=None n_dates=None recon=`by-date` prov=`dedicated-probe`
  - ⚠️ 抓法+欄位/earliest 已實證真實 probe（分點/權證 dedicated endpoint、鉅額 /data）；全史 bulk 落地屬 sync operational（per-(股,日)規模）、非 catalog 缺資料

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `securities_trader` | 券商名稱 | VARCHAR(255) | 🔑 |  |
| 1 | `price` | 指數值 | NUMERIC(20,6) | 🔑 |  |
| 2 | `buy` | 買進 | NUMERIC(20,6) | 🔑 |  |
| 3 | `sell` | 賣出 | NUMERIC(20,6) | 🔑 |  |
| 4 | `securities_trader_id` | 券商代號 | VARCHAR(255) | 🔑 |  |
| 5 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 6 | `date` | 日期 | DATE | 🔑 |  |

### TaiwanTotalExchangeMarginMaintenance｜大盤融資維持率 `B` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2001-01-01 data_id_source=`none` n_stocks=1 n_dates=6236 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `TotalExchangeMarginMaintenance` | 大盤整體融資維持率 | NUMERIC(20,6) |  |  |


## finmind / TW-Convertible Bond

### TaiwanStockConvertibleBondDaily｜可轉債日成交 `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2007-01-01 data_id_source=`none` n_stocks=None n_dates=4767 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `cb_id` | 可轉債代號 | VARCHAR(255) | 🔑 |  |
| 1 | `cb_name` | 可轉債名稱 | VARCHAR(255) |  |  |
| 2 | `transaction_type` | 交易類別 | VARCHAR(255) |  |  |
| 3 | `close` | 收盤價 | NUMERIC(20,6) |  |  |
| 4 | `change` | 漲跌 | NUMERIC(20,6) |  |  |
| 5 | `open` | 開盤價 | NUMERIC(20,6) |  |  |
| 6 | `max` | 最高價 | NUMERIC(20,6) |  |  |
| 7 | `min` | 最低價 | NUMERIC(20,6) |  |  |
| 8 | `no_of_transactions` | 成交筆數 | NUMERIC(20,6) |  |  |
| 9 | `unit` | 成交張數 | NUMERIC(20,6) |  |  |
| 10 | `trading_value` | 成交值 | NUMERIC(20,6) |  |  |
| 11 | `avg_price` | 均價 | NUMERIC(20,6) |  |  |
| 12 | `next_ref_price` | 次日參考價 | NUMERIC(20,6) |  |  |
| 13 | `next_max_limit` | 次日漲停價 | NUMERIC(20,6) |  |  |
| 14 | `next_min_limit` | 次日跌停價 | NUMERIC(20,6) |  |  |
| 15 | `date` | 日期 | DATE |  |  |

### TaiwanStockConvertibleBondDailyOverview｜可轉債每日總覽 `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2010-01-01 data_id_source=`none` n_stocks=None n_dates=4031 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `cb_id` | 可轉債代號 | VARCHAR(255) | 🔑 |  |
| 1 | `cb_name` | 可轉債名稱 | VARCHAR(255) |  |  |
| 2 | `date` | 日期 | VARCHAR(64) |  |  |
| 3 | `InitialDateOfConversion` | 可轉換起日 | DATE |  |  |
| 4 | `DueDateOfConversion` | 可轉換迄日 | DATE |  |  |
| 5 | `InitialDateOfStopConversion` | 停止轉換起日 | VARCHAR(255) |  |  |
| 6 | `DueDateOfStopConversion` | 停止轉換迄日 | VARCHAR(255) |  |  |
| 7 | `ConversionPrice` | 轉換價格 | NUMERIC(20,6) |  |  |
| 8 | `NextEffectiveDateOfConversionPrice` | 次一轉換價生效日 | DATE |  |  |
| 9 | `LatestInitialDateOfPut` | 最近賣回權起日 | DATE |  |  |
| 10 | `LatestDueDateOfPut` | 最近賣回權迄日 | DATE |  |  |
| 11 | `LatestPutPrice` | 最近賣回價格 | NUMERIC(20,6) |  |  |
| 12 | `InitialDateOfEarlyRedemption` | 提前贖回起日 | DATE |  |  |
| 13 | `DueDateOfEarlyRedemption` | 提前贖回迄日 | DATE |  |  |
| 14 | `EarlyRedemptionPrice` | 提前贖回價格 | NUMERIC(20,6) |  |  |
| 15 | `DateOfDelisted` | 下市日期 | DATE |  |  |
| 16 | `IssuanceAmount` | 發行總額 | NUMERIC(20,6) |  |  |
| 17 | `OutstandingAmount` | 流通餘額 | NUMERIC(20,6) |  |  |
| 18 | `ReferencePrice` | 參考價格 | NUMERIC(20,6) |  |  |
| 19 | `PriceOfUnderlyingStock` | 標的股票價格 | NUMERIC(20,6) |  |  |
| 20 | `InitialDateOfSuspension` | 暫停交易起日 | VARCHAR(255) |  |  |
| 21 | `DueDateOfSuspension` | 暫停交易迄日 | VARCHAR(255) |  |  |
| 22 | `CouponRate` | 票面利率 | NUMERIC(20,6) |  |  |

### TaiwanStockConvertibleBondInfo｜可轉債總覽 `B` ✅
- ep=`/data` mode=`market` freq=`snapshot` earliest=2025-01-01 data_id_source=`none` n_stocks=1 n_dates=356 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `cb_id` | 可轉債代號 | VARCHAR(255) | 🔑 |  |
| 1 | `cb_name` | 可轉債名稱 | VARCHAR(255) |  |  |
| 2 | `InitialDateOfConversion` | 可轉換起日 | DATE |  |  |
| 3 | `DueDateOfConversion` | 可轉換迄日 | DATE |  |  |
| 4 | `IssuanceAmount` | 發行總額 | NUMERIC(20,6) |  |  |

### TaiwanStockConvertibleBondInstitutionalInvestors｜可轉債三大法人 `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2009-04-01 data_id_source=`none` n_stocks=None n_dates=4216 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `Foreign_Investor_Buy` | 外資買進 | NUMERIC(20,6) |  |  |
| 1 | `Foreign_Investor_Sell` | 外資賣出 | NUMERIC(20,6) |  |  |
| 2 | `Foreign_Investor_Overbuy` | 外資買超 | NUMERIC(20,6) |  |  |
| 3 | `Investment_Trust_Buy` | 投信買進 | NUMERIC(20,6) |  |  |
| 4 | `Investment_Trust_Sell` | 投信賣出 | NUMERIC(20,6) |  |  |
| 5 | `Investment_Trust_Overbuy` | 投信買超 | NUMERIC(20,6) |  |  |
| 6 | `Dealer_self_Buy` | 自營商買進 | NUMERIC(20,6) |  |  |
| 7 | `Dealer_self_Sell` | 自營商賣出 | NUMERIC(20,6) |  |  |
| 8 | `Dealer_self_Overbuy` | 自營商買超 | NUMERIC(20,6) |  |  |
| 9 | `Total_Overbuy` | 合計買超 | NUMERIC(20,6) |  |  |
| 10 | `cb_id` | 可轉債代號 | VARCHAR(255) | 🔑 |  |
| 11 | `cb_name` | 可轉債名稱 | VARCHAR(255) |  |  |
| 12 | `date` | 日期 | DATE |  |  |


## finmind / TW-Derivative

### TaiwanFutOptDailyInfo｜期貨選擇權總覽 `F` ✅
- ep=`/data` mode=`market` freq=`snapshot` earliest=NULL data_id_source=`none` n_stocks=None n_dates=None recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `code` | 代號 | VARCHAR(255) | 🔑 |  |
| 1 | `type` | 商品類別（期貨/選擇權） | VARCHAR(255) | 🔑 |  |
| 2 | `name` | 商品名稱 | VARCHAR(255) | 🔑 |  |

### TaiwanFutOptInstitutionalInvestors｜期貨選擇權三大法人（合併） `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2017-07-01 data_id_source=`none` n_stocks=None n_dates=2195 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `name` | 商品名稱 | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 日期 | DATE | 🔑 |  |
| 2 | `institutional_investors` | 法人別 | VARCHAR(255) | 🔑 |  |
| 3 | `long_deal_volume` | 多方交易口數 | NUMERIC(20,6) |  |  |
| 4 | `long_deal_amount` | 多方交易金額 | NUMERIC(20,6) |  |  |
| 5 | `short_deal_volume` | 空方交易口數 | NUMERIC(20,6) |  |  |
| 6 | `short_deal_amount` | 空方交易金額 | NUMERIC(20,6) |  |  |
| 7 | `long_open_interest_balance_volume` | 多方未平倉口數 | NUMERIC(20,6) |  |  |
| 8 | `long_open_interest_balance_amount` | 多方未平倉金額 | NUMERIC(20,6) |  |  |
| 9 | `short_open_interest_balance_volume` | 空方未平倉口數 | NUMERIC(20,6) |  |  |
| 10 | `short_open_interest_balance_amount` | 空方未平倉金額 | NUMERIC(20,6) |  |  |

### TaiwanFuturesDaily｜期貨日成交 `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=1998-08-03 data_id_source=`none` n_stocks=None n_dates=2226 recon=`by-date` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `futures_id` | 期貨代號 | VARCHAR(255) | 🔑 |  |
| 2 | `contract_date` | 契約月份（含價差如 200710/200711、週合約如 201211W4） | VARCHAR(64) | 🔑 |  |
| 3 | `open` | 開盤價 | NUMERIC(20,6) | 🔑 |  |
| 4 | `max` | 最高價 | NUMERIC(20,6) | 🔑 |  |
| 5 | `min` | 最低價 | NUMERIC(20,6) | 🔑 |  |
| 6 | `close` | 收盤價 | NUMERIC(20,6) | 🔑 |  |
| 7 | `spread` | 漲跌價差 | NUMERIC(20,6) | 🔑 |  |
| 8 | `spread_per` | 漲跌幅(%) | NUMERIC(20,6) | 🔑 |  |
| 9 | `volume` | 成交量(口) | NUMERIC(20,6) | 🔑 |  |
| 10 | `settlement_price` | 結算價 | NUMERIC(20,6) | 🔑 |  |
| 11 | `open_interest` | 未平倉量 | NUMERIC(20,6) | 🔑 |  |
| 12 | `trading_session` | 交易時段(日盤/夜盤) | VARCHAR(255) | 🔑 |  |

### TaiwanFuturesDealerTradingVolumeDaily｜期貨各券商每日交易 `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2021-04-01 data_id_source=`none` n_stocks=None n_dates=1276 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `dealer_code` | 券商代號 | VARCHAR(255) | 🔑 |  |
| 2 | `dealer_name` | 券商名稱 | VARCHAR(255) | 🔑 |  |
| 3 | `futures_id` | 期貨代號 | VARCHAR(255) | 🔑 |  |
| 4 | `volume` | 成交量(口) | NUMERIC(20,6) | 🔑 |  |
| 5 | `is_after_hour` | 是否盤後（夜盤） | VARCHAR(255) | 🔑 |  |

### TaiwanFuturesFinalSettlementPrice｜期貨最後結算價 `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2016-01-08 data_id_source=`none` n_stocks=None n_dates=2557 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE |  |  |
| 1 | `contract_month` | 結算月份（含週合約如 202101W1） | VARCHAR(64) |  |  |
| 2 | `futures_type` | 期貨類別 | VARCHAR(255) |  |  |
| 3 | `futures_id` | 期貨代號 | VARCHAR(255) | 🔑 |  |
| 4 | `futures_name` | 期貨名稱 | VARCHAR(255) |  |  |
| 5 | `settlement_price` | 結算價 | NUMERIC(20,6) |  |  |
| 6 | `underlying_code` | 標的代號 | VARCHAR(255) |  |  |
| 7 | `notional_value` | 契約價值 | NUMERIC(20,6) |  |  |

### TaiwanFuturesInstitutionalInvestors｜期貨三大法人 `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2018-06-01 data_id_source=`none` n_stocks=None n_dates=1970 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `futures_id` | 期貨代號 | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 日期 | DATE | 🔑 |  |
| 2 | `institutional_investors` | 法人別 | VARCHAR(255) | 🔑 |  |
| 3 | `long_deal_volume` | 多方成交量 | NUMERIC(20,6) |  |  |
| 4 | `long_deal_amount` | 多方成交金額 | NUMERIC(20,6) |  |  |
| 5 | `short_deal_volume` | 空方成交量 | NUMERIC(20,6) |  |  |
| 6 | `short_deal_amount` | 空方成交金額 | NUMERIC(20,6) |  |  |
| 7 | `long_open_interest_balance_volume` | 多方未平倉餘額量 | NUMERIC(20,6) |  |  |
| 8 | `long_open_interest_balance_amount` | 多方未平倉餘額金額 | NUMERIC(20,6) |  |  |
| 9 | `short_open_interest_balance_volume` | 空方未平倉餘額量 | NUMERIC(20,6) |  |  |
| 10 | `short_open_interest_balance_amount` | 空方未平倉餘額金額 | NUMERIC(20,6) |  |  |

### TaiwanFuturesInstitutionalInvestorsAfterHours｜期貨三大法人（夜盤） `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2021-10-01 data_id_source=`none` n_stocks=None n_dates=1153 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `futures_id` | 期貨代號 | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 日期 | DATE | 🔑 |  |
| 2 | `institutional_investors` | 法人別 | VARCHAR(255) | 🔑 |  |
| 3 | `long_deal_volume` | 多方交易口數 | NUMERIC(20,6) |  |  |
| 4 | `long_deal_amount` | 多方交易金額 | NUMERIC(20,6) |  |  |
| 5 | `short_deal_volume` | 空方交易口數 | NUMERIC(20,6) |  |  |
| 6 | `short_deal_amount` | 空方交易金額 | NUMERIC(20,6) |  |  |

### TaiwanFuturesOpenInterestLargeTraders｜期貨大額交易人未沖銷 `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2007-01-01 data_id_source=`none` n_stocks=None n_dates=4767 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `name` | 商品名稱 | VARCHAR(255) | 🔑 |  |
| 1 | `contract_type` | 契約類別（所有契約/近月契約） | VARCHAR(255) | 🔑 |  |
| 2 | `buy_top5_trader_open_interest` | 前5大交易人買方未平倉 | NUMERIC(20,6) |  |  |
| 3 | `buy_top5_trader_open_interest_per` | 前5大交易人買方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 4 | `buy_top10_trader_open_interest` | 前10大交易人買方未平倉 | NUMERIC(20,6) |  |  |
| 5 | `buy_top10_trader_open_interest_per` | 前10大交易人買方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 6 | `sell_top5_trader_open_interest` | 前5大交易人賣方未平倉 | NUMERIC(20,6) |  |  |
| 7 | `sell_top5_trader_open_interest_per` | 前5大交易人賣方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 8 | `sell_top10_trader_open_interest` | 前10大交易人賣方未平倉 | NUMERIC(20,6) |  |  |
| 9 | `sell_top10_trader_open_interest_per` | 前10大交易人賣方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 10 | `market_open_interest` | 全市場未平倉量 | NUMERIC(20,6) |  |  |
| 11 | `buy_top5_specific_open_interest` | 前5大特定法人買方未平倉 | NUMERIC(20,6) |  |  |
| 12 | `buy_top5_specific_open_interest_per` | 前5大特定法人買方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 13 | `buy_top10_specific_open_interest` | 前10大特定法人買方未平倉 | NUMERIC(20,6) |  |  |
| 14 | `buy_top10_specific_open_interest_per` | 前10大特定法人買方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 15 | `sell_top5_specific_open_interest` | 前5大特定法人賣方未平倉 | NUMERIC(20,6) |  |  |
| 16 | `sell_top5_specific_open_interest_per` | 前5大特定法人賣方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 17 | `sell_top10_specific_open_interest` | 前10大特定法人賣方未平倉 | NUMERIC(20,6) |  |  |
| 18 | `sell_top10_specific_open_interest_per` | 前10大特定法人賣方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 19 | `date` | 日期 | DATE | 🔑 |  |
| 20 | `futures_id` | 期貨代號 | VARCHAR(255) | 🔑 |  |

### TaiwanFuturesSpreadTick｜期貨價差逐筆(Tick) `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2026-05-01 data_id_source=`none` n_stocks=None n_dates=30 recon=`by-date` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `contract_date` | 契約月份 | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 日期 | DATE | 🔑 |  |
| 2 | `time` | 時間 | VARCHAR(255) | 🔑 |  |
| 3 | `far_price` | 遠月價 | NUMERIC(20,6) | 🔑 |  |
| 4 | `futures_id` | 期貨代號 | VARCHAR(255) | 🔑 |  |
| 5 | `near_price` | 近月價 | NUMERIC(20,6) | 🔑 |  |
| 6 | `price` | 價差價 | NUMERIC(20,6) | 🔑 |  |
| 7 | `spread_to_spread` | 價差對價差 | NUMERIC(20,6) | 🔑 |  |
| 8 | `volume` | 成交量 | NUMERIC(20,6) | 🔑 |  |

### TaiwanFuturesSpreadTrading｜期貨價差行情 `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2007-11-01 data_id_source=`none` n_stocks=None n_dates=4563 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `futures_id` | 期貨代號 | VARCHAR(255) | 🔑 |  |
| 2 | `contract_date` | 契約月份（含價差/週合約） | VARCHAR(255) | 🔑 |  |
| 3 | `open` | 開盤價 | NUMERIC(20,6) | 🔑 |  |
| 4 | `max` | 最高價 | NUMERIC(20,6) | 🔑 |  |
| 5 | `min` | 最低價 | NUMERIC(20,6) | 🔑 |  |
| 6 | `close` | 收盤價 | NUMERIC(20,6) | 🔑 |  |
| 7 | `best_bid` | 最佳買價 | NUMERIC(20,6) | 🔑 |  |
| 8 | `best_ask` | 最佳賣價 | NUMERIC(20,6) | 🔑 |  |
| 9 | `historical_max` | 歷史最高價 | NUMERIC(20,6) | 🔑 |  |
| 10 | `historical_min` | 歷史最低價 | NUMERIC(20,6) | 🔑 |  |
| 11 | `spread_to_spread_volume` | 價差對價差成交量 | NUMERIC(20,6) | 🔑 |  |
| 12 | `spread_to_single_volume` | 價差對單式成交量 | NUMERIC(20,6) | 🔑 |  |
| 13 | `trading_session` | 交易時段(日盤/夜盤) | VARCHAR(255) | 🔑 |  |

### TaiwanFuturesTick｜期貨逐筆成交 `B` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=NULL data_id_source=`none` n_stocks=None n_dates=None recon=`by-date` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `contract_date` | 契約月份（含價差如 200710/200711、週合約如 201211W4） | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 日期 | VARCHAR(255) | 🔑 |  |
| 2 | `futures_id` | 期貨代號 | VARCHAR(255) | 🔑 |  |
| 3 | `price` | 指數值 | NUMERIC(20,6) | 🔑 |  |
| 4 | `volume` | 成交量(口) | NUMERIC(20,6) | 🔑 |  |

### TaiwanOptionDaily｜選擇權日成交 `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2002-01-02 data_id_source=`none` n_stocks=None n_dates=2369 recon=`by-date` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `option_id` | 選擇權代號 | VARCHAR(255) | 🔑 |  |
| 2 | `contract_date` | 契約月份（含價差、週合約如 201211W4） | VARCHAR(64) | 🔑 |  |
| 3 | `strike_price` | 履約價 | NUMERIC(20,6) | 🔑 |  |
| 4 | `call_put` | 買權賣權(Call買權/Put賣權) | VARCHAR(255) | 🔑 |  |
| 5 | `open` | 開盤價 | NUMERIC(20,6) | 🔑 |  |
| 6 | `max` | 最高價 | NUMERIC(20,6) | 🔑 |  |
| 7 | `min` | 最低價 | NUMERIC(20,6) | 🔑 |  |
| 8 | `close` | 收盤價 | NUMERIC(20,6) | 🔑 |  |
| 9 | `volume` | 成交量(口) | NUMERIC(20,6) | 🔑 |  |
| 10 | `settlement_price` | 結算價 | NUMERIC(20,6) | 🔑 |  |
| 11 | `open_interest` | 未平倉量 | NUMERIC(20,6) | 🔑 |  |
| 12 | `trading_session` | 交易時段(日盤/夜盤) | VARCHAR(255) | 🔑 |  |

### TaiwanOptionDealerTradingVolumeDaily｜選擇權各券商每日交易 `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2021-04-01 data_id_source=`none` n_stocks=None n_dates=1276 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `dealer_code` | 券商代號 | VARCHAR(255) | 🔑 |  |
| 2 | `dealer_name` | 券商名稱 | VARCHAR(255) | 🔑 |  |
| 3 | `option_id` | 選擇權代號 | VARCHAR(255) | 🔑 |  |
| 4 | `volume` | 成交量(口) | NUMERIC(20,6) | 🔑 |  |
| 5 | `is_after_hour` | 是否盤後（夜盤） | VARCHAR(255) | 🔑 |  |

### TaiwanOptionFinalSettlementPrice｜選擇權最後結算價 `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2002-01-17 data_id_source=`none` n_stocks=None n_dates=5981 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE |  |  |
| 1 | `contract_month` | 結算月份（含週合約） | VARCHAR(255) |  |  |
| 2 | `option_type` | 選擇權類別 | VARCHAR(255) |  |  |
| 3 | `option_id` | 選擇權代號 | VARCHAR(255) | 🔑 |  |
| 4 | `option_name` | 選擇權名稱 | VARCHAR(255) |  |  |
| 5 | `settlement_price` | 結算價 | NUMERIC(20,6) |  |  |
| 6 | `underlying_code` | 標的代號 | VARCHAR(255) |  |  |
| 7 | `notional_value` | 契約價值 | NUMERIC(20,6) |  |  |

### TaiwanOptionInstitutionalInvestors｜選擇權三大法人 `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2018-06-01 data_id_source=`none` n_stocks=None n_dates=1970 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `option_id` | 選擇權代號 | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 日期 | DATE | 🔑 |  |
| 2 | `call_put` | 買權賣權(Call買權/Put賣權) | VARCHAR(255) | 🔑 |  |
| 3 | `institutional_investors` | 法人別 | VARCHAR(255) | 🔑 |  |
| 4 | `long_deal_volume` | 多方成交量 | NUMERIC(20,6) |  |  |
| 5 | `long_deal_amount` | 多方成交金額 | NUMERIC(20,6) |  |  |
| 6 | `short_deal_volume` | 空方成交量 | NUMERIC(20,6) |  |  |
| 7 | `short_deal_amount` | 空方成交金額 | NUMERIC(20,6) |  |  |
| 8 | `long_open_interest_balance_volume` | 多方未平倉餘額量 | NUMERIC(20,6) |  |  |
| 9 | `long_open_interest_balance_amount` | 多方未平倉餘額金額 | NUMERIC(20,6) |  |  |
| 10 | `short_open_interest_balance_volume` | 空方未平倉餘額量 | NUMERIC(20,6) |  |  |
| 11 | `short_open_interest_balance_amount` | 空方未平倉餘額金額 | NUMERIC(20,6) |  |  |

### TaiwanOptionInstitutionalInvestorsAfterHours｜選擇權三大法人（夜盤） `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2021-10-01 data_id_source=`none` n_stocks=None n_dates=1153 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `option_id` | 選擇權代號 | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 日期 | DATE | 🔑 |  |
| 2 | `call_put` | 買權賣權(Call/Put) | VARCHAR(255) | 🔑 |  |
| 3 | `institutional_investors` | 法人別 | VARCHAR(255) | 🔑 |  |
| 4 | `long_deal_volume` | 多方交易口數 | NUMERIC(20,6) |  |  |
| 5 | `long_deal_amount` | 多方交易金額 | NUMERIC(20,6) |  |  |
| 6 | `short_deal_volume` | 空方交易口數 | NUMERIC(20,6) |  |  |
| 7 | `short_deal_amount` | 空方交易金額 | NUMERIC(20,6) |  |  |

### TaiwanOptionOpenInterestLargeTraders｜選擇權大額交易人未沖銷 `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2007-01-01 data_id_source=`none` n_stocks=None n_dates=4767 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `contract_type` | 契約類別（所有契約/近月契約） | VARCHAR(255) | 🔑 |  |
| 1 | `buy_top5_trader_open_interest` | 前5大交易人買方未平倉 | NUMERIC(20,6) |  |  |
| 2 | `buy_top5_trader_open_interest_per` | 前5大交易人買方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 3 | `buy_top10_trader_open_interest` | 前10大交易人買方未平倉 | NUMERIC(20,6) |  |  |
| 4 | `buy_top10_trader_open_interest_per` | 前10大交易人買方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 5 | `sell_top5_trader_open_interest` | 前5大交易人賣方未平倉 | NUMERIC(20,6) |  |  |
| 6 | `sell_top5_trader_open_interest_per` | 前5大交易人賣方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 7 | `sell_top10_trader_open_interest` | 前10大交易人賣方未平倉 | NUMERIC(20,6) |  |  |
| 8 | `sell_top10_trader_open_interest_per` | 前10大交易人賣方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 9 | `market_open_interest` | 全市場未平倉量 | NUMERIC(20,6) |  |  |
| 10 | `buy_top5_specific_open_interest` | 前5大特定法人買方未平倉 | NUMERIC(20,6) |  |  |
| 11 | `buy_top5_specific_open_interest_per` | 前5大特定法人買方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 12 | `buy_top10_specific_open_interest` | 前10大特定法人買方未平倉 | NUMERIC(20,6) |  |  |
| 13 | `buy_top10_specific_open_interest_per` | 前10大特定法人買方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 14 | `sell_top5_specific_open_interest` | 前5大特定法人賣方未平倉 | NUMERIC(20,6) |  |  |
| 15 | `sell_top5_specific_open_interest_per` | 前5大特定法人賣方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 16 | `sell_top10_specific_open_interest` | 前10大特定法人賣方未平倉 | NUMERIC(20,6) |  |  |
| 17 | `sell_top10_specific_open_interest_per` | 前10大特定法人賣方未平倉占比(%) | NUMERIC(20,6) |  |  |
| 18 | `date` | 日期 | DATE | 🔑 |  |
| 19 | `put_call` | 買權賣權(Call買權/Put賣權) | VARCHAR(255) | 🔑 |  |
| 20 | `name` | 商品名稱 | VARCHAR(255) | 🔑 |  |
| 21 | `option_id` | 選擇權代號 | VARCHAR(255) | 🔑 |  |

### TaiwanOptionTick｜選擇權逐筆成交 `B` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=NULL data_id_source=`none` n_stocks=None n_dates=None recon=`by-date` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `ExercisePrice` | 履約價 | NUMERIC(20,6) | 🔑 |  |
| 1 | `PutCall` | 買賣權別 | VARCHAR(255) | 🔑 |  |
| 2 | `contract_date` | 契約月份（含價差如 200710/200711、週合約如 201211W4） | VARCHAR(255) | 🔑 |  |
| 3 | `date` | 日期 | VARCHAR(255) | 🔑 |  |
| 4 | `option_id` | 選擇權代號 | VARCHAR(255) | 🔑 |  |
| 5 | `price` | 指數值 | NUMERIC(20,6) | 🔑 |  |
| 6 | `volume` | 成交量(口) | NUMERIC(20,6) | 🔑 |  |


## finmind / TW-Fundamental

### TaiwanStockBalanceSheet｜資產負債表 `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`quarterly` earliest=2012-03-31 data_id_source=`roster` n_stocks=2201 n_dates=57 recon=`full-history` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 資料日期（季底） | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `type` | 會計科目（值見 `/translation`） | VARCHAR(255) | 🔑 |  |
| 3 | `value` | 科目金額 | NUMERIC(24,6) |  |  |
| 4 | `origin_name` | 原始科目名稱 | VARCHAR(255) |  |  |

### TaiwanStockCapitalReductionReferencePrice｜減資恢復買賣參考價 `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2011-01-25 data_id_source=`none` n_stocks=None n_dates=3770 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 恢復買賣日 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `ClosingPriceonTheLastTradingDay` | 減資前最後交易日收盤價 | NUMERIC(20,6) |  |  |
| 3 | `PostReductionReferencePrice` | 減資後參考價 | NUMERIC(20,6) |  |  |
| 4 | `LimitUp` | 漲停價 | NUMERIC(20,6) |  |  |
| 5 | `LimitDown` | 跌停價 | NUMERIC(20,6) |  |  |
| 6 | `OpeningReferencePrice` | 開盤競價基準 | NUMERIC(20,6) |  |  |
| 7 | `ExrightReferencePrice` | 除權參考價 | NUMERIC(20,6) |  |  |
| 8 | `ReasonforCapitalReduction` | 減資原因 | VARCHAR(255) |  |  |

### TaiwanStockCashFlowsStatement｜現金流量表 `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`quarterly` earliest=2012-03-31 data_id_source=`roster` n_stocks=2208 n_dates=57 recon=`full-history` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 資料日期（季底） | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `type` | 會計科目（值見 `/translation`） | VARCHAR(255) | 🔑 |  |
| 3 | `value` | 科目金額 | NUMERIC(23,6) |  |  |
| 4 | `origin_name` | 原始科目名稱 | VARCHAR(255) |  |  |

### TaiwanStockDelisting｜下市櫃 `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2001-01-20 data_id_source=`none` n_stocks=None n_dates=6223 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 下市櫃日 | DATE |  |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | 股票名稱 | VARCHAR(255) |  |  |

### TaiwanStockDividend｜股利政策 `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2005-06-19 data_id_source=`roster` n_stocks=3101 n_dates=5143 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 資料日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `year` | 股利所屬年度 | VARCHAR(255) |  |  |
| 3 | `StockEarningsDistribution` | 盈餘配股 | NUMERIC(20,10) |  |  |
| 4 | `StockStatutorySurplus` | 法定盈餘公積配股 | NUMERIC(20,10) |  |  |
| 5 | `StockExDividendTradingDate` | 除權交易日 | DATE |  |  |
| 6 | `TotalEmployeeStockDividend` | 員工配股總額 | NUMERIC(20,6) |  |  |
| 7 | `TotalEmployeeStockDividendAmount` | 員工配股金額 | NUMERIC(20,6) |  |  |
| 8 | `RatioOfEmployeeStockDividendOfTotal` | 員工配股占盈餘比率 | NUMERIC(20,6) |  |  |
| 9 | `RatioOfEmployeeStockDividend` | 員工配股率 | NUMERIC(20,8) |  |  |
| 10 | `CashEarningsDistribution` | 盈餘配息（現金股利） | NUMERIC(20,8) |  |  |
| 11 | `CashStatutorySurplus` | 法定盈餘公積配息 | NUMERIC(20,6) |  |  |
| 12 | `CashExDividendTradingDate` | 除息交易日 | DATE |  |  |
| 13 | `CashDividendPaymentDate` | 現金股利發放日 | DATE |  |  |
| 14 | `TotalEmployeeCashDividend` | 員工現金紅利總額 | NUMERIC(21,6) |  |  |
| 15 | `TotalNumberOfCashCapitalIncrease` | 現金增資總股數 | NUMERIC(20,6) |  |  |
| 16 | `CashIncreaseSubscriptionRate` | 現金增資認購率 | NUMERIC(20,6) |  |  |
| 17 | `CashIncreaseSubscriptionpRrice` | 現金增資認購價 | NUMERIC(20,6) |  |  |
| 18 | `RemunerationOfDirectorsAndSupervisors` | 董監事酬勞 | NUMERIC(20,6) |  |  |
| 19 | `ParticipateDistributionOfTotalShares` | 參與分配總股數 | NUMERIC(21,6) |  |  |
| 20 | `AnnouncementDate` | 公告日期 ⭐ | DATE |  | ⚠️ |
| 21 | `AnnouncementTime` | 公告時間 ⭐ | VARCHAR(255) |  | ⚠️ |

### TaiwanStockDividendResult｜除權除息結果 `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2005-05-19 data_id_source=`roster` n_stocks=245 n_dates=695 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 除權息日 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `before_price` | 除權息前參考價 | NUMERIC(20,6) |  |  |
| 3 | `after_price` | 除權息後參考價 | NUMERIC(20,6) |  |  |
| 4 | `stock_and_cache_dividend` | 配股配息合計 | NUMERIC(20,6) |  |  |
| 5 | `stock_or_cache_dividend` | 股票或現金股利 | VARCHAR(255) |  |  |
| 6 | `max_price` | 最高價 | NUMERIC(20,6) |  |  |
| 7 | `min_price` | 最低價 | NUMERIC(20,6) |  |  |
| 8 | `open_price` | 開盤價 | NUMERIC(20,6) |  |  |
| 9 | `reference_price` | 參考價 | NUMERIC(20,6) |  |  |

### TaiwanStockFinancialStatements｜綜合損益表 `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`quarterly` earliest=1991-12-31 data_id_source=`roster` n_stocks=2122 n_dates=138 recon=`full-history` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 資料日期（季底） | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `type` | 會計科目（值見 `/translation`） | VARCHAR(255) | 🔑 |  |
| 3 | `value` | 科目金額 | NUMERIC(23,6) |  |  |
| 4 | `origin_name` | 原始科目名稱 | VARCHAR(255) |  |  |

### TaiwanStockMarketValue｜股價市值 `B` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2004-02-12 data_id_source=`roster` n_stocks=3101 n_dates=5474 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 資料日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `market_value` | 市值（元） | NUMERIC(24,6) |  |  |

### TaiwanStockMarketValueWeight｜市值比重 `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2024-10-30 data_id_source=`roster` n_stocks=3101 n_dates=398 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `rank` | 排名 | NUMERIC(20,6) |  |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | 股票名稱 | VARCHAR(255) |  |  |
| 3 | `weight_per` | 市值權重（%） | NUMERIC(20,6) |  |  |
| 4 | `date` | 資料日期 | DATE | 🔑 |  |
| 5 | `type` | 類別（上市/上櫃） | VARCHAR(255) |  |  |

### TaiwanStockMonthRevenue｜月營收 `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`monthly` earliest=2002-02-01 data_id_source=`roster` n_stocks=2361 n_dates=293 recon=`full-history` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 資料日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `country` | 國家／央行 | VARCHAR(255) | 🔑 |  |
| 3 | `revenue` | 當月營收（千元） | NUMERIC(22,6) |  |  |
| 4 | `revenue_month` | 營收月份 | NUMERIC(20,6) |  |  |
| 5 | `revenue_year` | 營收年度 | NUMERIC(20,6) |  |  |
| 6 | `create_time` | 資料建立時點 | DATE |  | ⚠️ |

### TaiwanStockParValueChange｜變更面額恢復買賣參考價 `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2019-09-09 data_id_source=`none` n_stocks=None n_dates=1658 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 恢復買賣日 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | 股票名稱 | VARCHAR(255) |  |  |
| 3 | `before_close` | 變更前收盤價 | NUMERIC(20,6) |  |  |
| 4 | `after_ref_close` | 變更後參考收盤價 | NUMERIC(20,6) |  |  |
| 5 | `after_ref_max` | 調整後參考最高價 | NUMERIC(20,6) |  |  |
| 6 | `after_ref_min` | 調整後參考最低價 | NUMERIC(20,6) |  |  |
| 7 | `after_ref_open` | 調整後參考開盤價 | NUMERIC(20,6) |  |  |

### TaiwanStockSplitPrice｜分割後參考價 `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2019-09-09 data_id_source=`none` n_stocks=None n_dates=1658 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 分割恢復買賣日 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `type` | 類別 | VARCHAR(255) |  |  |
| 3 | `before_price` | 分割前參考價 | NUMERIC(20,6) |  |  |
| 4 | `after_price` | 分割後參考價 | NUMERIC(20,6) |  |  |
| 5 | `max_price` | 最高價 | NUMERIC(20,6) |  |  |
| 6 | `min_price` | 最低價 | NUMERIC(20,6) |  |  |
| 7 | `open_price` | 開盤價 | NUMERIC(20,6) |  |  |


## finmind / TW-Others

### TaiwanBusinessIndicator｜景氣對策信號 `B` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=1982-01-01 data_id_source=`none` n_stocks=None n_dates=10891 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `leading` | 領先指標 | NUMERIC(20,6) |  |  |
| 2 | `leading_notrend` | 領先指標（不含趨勢） | NUMERIC(20,6) |  |  |
| 3 | `coincident` | 同時指標 | NUMERIC(20,6) |  |  |
| 4 | `coincident_notrend` | 同時指標（不含趨勢） | NUMERIC(20,6) |  |  |
| 5 | `lagging` | 落後指標 | NUMERIC(20,6) |  |  |
| 6 | `lagging_notrend` | 落後指標（不含趨勢） | NUMERIC(20,6) |  |  |
| 7 | `monitoring` | 景氣對策信號 | NUMERIC(20,6) |  |  |
| 8 | `monitoring_color` | 信號燈號 | VARCHAR(255) |  |  |

### TaiwanStockIndustryChain｜產業鏈 `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2026-06-16 data_id_source=`roster` n_stocks=3101 n_dates=1 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 1 | `industry` | 產業 | VARCHAR(255) |  |  |
| 2 | `sub_industry` | 次產業 | VARCHAR(255) |  |  |
| 3 | `date` | 日期 | DATE |  |  |

### TaiwanStockNews｜相關新聞 `F` ✅
- ep=`/data` mode=`single-day` freq=`single-day` earliest=2010-03-02 data_id_source=`roster` n_stocks=2407 n_dates=4104 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | VARCHAR(255) | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `link` | 連結 | TEXT |  |  |
| 3 | `source` | 來源 | VARCHAR(255) |  |  |
| 4 | `title` | 標題 | VARCHAR(255) |  |  |


## finmind / TW-Real-Time

### TaiwanFutOptTickInfo｜期貨選擇權即時總覽 `S` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=2026-06-01 data_id_source=`none` n_stocks=None n_dates=10 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `code` | 商品代號 | VARCHAR(255) | 🔑 |  |
| 1 | `callput` | 買賣權 | VARCHAR(255) |  |  |
| 2 | `date` | 日期 | VARCHAR(255) |  |  |
| 3 | `name` | 商品名稱 | VARCHAR(255) |  |  |
| 4 | `listing_date` | 上市日期 | DATE |  |  |
| 5 | `expire_price` | 到期結算價 | NUMERIC(20,6) |  |  |
| 6 | `update_date` | 更新日期 | DATE |  |  |


## finmind / TW-Technical

### TaiwanStock10Year｜十年線（月均價） `B` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2011-01-24 data_id_source=`roster` n_stocks=3101 n_dates=3771 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 資料日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `close` | 收盤價 | NUMERIC(20,6) |  |  |

### TaiwanStockDayTrading｜當沖交易 `F(id)` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2014-01-06 data_id_source=`roster` n_stocks=3101 n_dates=3048 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 交易日 | DATE | 🔑 |  |
| 2 | `BuyAfterSale` | 現股當沖先買後賣 | VARCHAR(255) |  |  |
| 3 | `Volume` | 當沖成交股數 | NUMERIC(20,6) |  |  |
| 4 | `BuyAmount` | 當沖買進金額 | NUMERIC(21,6) |  |  |
| 5 | `SellAmount` | 當沖賣出金額 | NUMERIC(21,6) |  |  |

### TaiwanStockDayTradingBorrowingFeeRate｜當沖借券費率 `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2015-10-14 data_id_source=`roster` n_stocks=3101 n_dates=2615 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | 股票名稱 | VARCHAR(255) |  |  |
| 3 | `InvestorBorrowedShares` | 投資人借券張數 | NUMERIC(20,6) |  |  |
| 4 | `InvestorBorrowingFeeRate` | 投資人借券費率 | NUMERIC(20,6) |  |  |

### TaiwanStockDayTradingSuspension｜暫停現股當沖 `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2014-07-09 data_id_source=`roster` n_stocks=3101 n_dates=2925 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 起始日期 | DATE | 🔑 |  |
| 2 | `end_date` | 截止日期 | DATE |  |  |
| 3 | `reason` | 暫停原因 | VARCHAR(255) |  |  |

### TaiwanStockEvery5SecondsIndex｜大盤每5秒指數 `B` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=2005-01-01 data_id_source=`none` n_stocks=None n_dates=5256 recon=`by-date` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `time` | 時間 | VARCHAR(255) | 🔑 |  |
| 2 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 3 | `price` | 指數值 | NUMERIC(20,6) | 🔑 |  |
| 4 | `kind` | 指數類別 | VARCHAR(255) | 🔑 |  |

### TaiwanStockInfo｜台股總覽 `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2020-06-03 data_id_source=`roster` n_stocks=3100 n_dates=174 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `industry_category` | 產業類別 | VARCHAR(255) | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | 股票名稱 | VARCHAR(255) |  |  |
| 3 | `type` | 市場類別 | VARCHAR(255) | 🔑 |  |
| 4 | `date` | 資料日期 | DATE |  |  |

### TaiwanStockInfoWithWarrant｜台股總覽（含權證） `F` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2026-06-16 data_id_source=`roster` n_stocks=3101 n_dates=1 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `industry_category` | 產業類別 | VARCHAR(255) | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `stock_name` | 股票名稱 | VARCHAR(255) |  |  |
| 3 | `type` | 市場類別 | VARCHAR(255) | 🔑 |  |
| 4 | `date` | 資料日期 | DATE | 🔑 |  |

### TaiwanStockInfoWithWarrantSummary｜權證標的對照表 `S` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2011-01-01 data_id_source=`none` n_stocks=3101 n_dates=3787 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `stock_id` | 權證代號 | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 資料日期 | DATE |  |  |
| 2 | `close` | 權證收盤價 | NUMERIC(20,6) |  |  |
| 3 | `target_stock_id` | 標的證券代號 | NUMERIC(20,6) |  |  |
| 4 | `target_close` | 標的證券收盤價 | NUMERIC(20,6) |  |  |
| 5 | `type` | 權證類別 | VARCHAR(255) |  |  |
| 6 | `fulfillment_method` | 履約方式 | VARCHAR(255) |  |  |
| 7 | `end_date` | 到期日 | DATE |  |  |
| 8 | `fulfillment_start_date` | 履約起始日 | VARCHAR(255) |  |  |
| 9 | `fulfillment_end_date` | 履約截止日 | VARCHAR(255) |  |  |
| 10 | `exercise_ratio` | 行使比例 | NUMERIC(20,6) |  |  |
| 11 | `fulfillment_price` | 履約價格 | NUMERIC(20,6) |  |  |

### TaiwanStockKBar｜台股K棒（分鐘） `S` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=NULL data_id_source=`roster` n_stocks=3101 n_dates=None recon=`roster-scoped` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `minute` | 分鐘 | VARCHAR(255) | 🔑 |  |
| 2 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 3 | `open` | 開盤價 | NUMERIC(20,6) | 🔑 |  |
| 4 | `high` | 最高價 | NUMERIC(20,6) | 🔑 |  |
| 5 | `low` | 最低價 | NUMERIC(20,6) | 🔑 |  |
| 6 | `close` | 收盤價 | NUMERIC(20,6) | 🔑 |  |
| 7 | `volume` | 成交量(口) | NUMERIC(20,6) | 🔑 |  |

### TaiwanStockMonthPrice｜月K線 `B` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1999-12-01 data_id_source=`roster` n_stocks=3101 n_dates=6502 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 1 | `ymonth` | 年度月別 | VARCHAR(255) |  |  |
| 2 | `max` | 最高價 | NUMERIC(20,6) |  |  |
| 3 | `min` | 最低價 | NUMERIC(20,6) |  |  |
| 4 | `trading_volume` | 成交股數 | NUMERIC(20,6) |  |  |
| 5 | `trading_money` | 成交金額 | NUMERIC(23,6) |  |  |
| 6 | `trading_turnover` | 成交筆數 | NUMERIC(20,6) |  |  |
| 7 | `date` | 交易日 | DATE | 🔑 |  |
| 8 | `close` | 收盤價 | NUMERIC(20,6) |  |  |
| 9 | `open` | 開盤價 | NUMERIC(20,6) |  |  |
| 10 | `spread` | 漲跌價差 | NUMERIC(20,6) |  |  |

### TaiwanStockPER｜本益比/股價淨值比 `F` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2005-09-02 data_id_source=`roster` n_stocks=1919 n_dates=5103 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 交易日 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `dividend_yield` | 殖利率 | NUMERIC(20,6) |  |  |
| 3 | `PER` | 本益比 | NUMERIC(20,6) |  |  |
| 4 | `PBR` | 股價淨值比 | NUMERIC(20,6) |  |  |

### TaiwanStockPrice｜股價日成交資訊 `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1994-09-13 data_id_source=`roster` n_stocks=2706 n_dates=7219 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 交易日 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `Trading_Volume` | 成交股數 | NUMERIC(21,6) |  |  |
| 3 | `Trading_money` | 成交金額 | NUMERIC(23,6) |  |  |
| 4 | `open` | 開盤價 | NUMERIC(20,6) |  |  |
| 5 | `max` | 最高價 | NUMERIC(20,6) |  |  |
| 6 | `min` | 最低價 | NUMERIC(20,6) |  |  |
| 7 | `close` | 收盤價 | NUMERIC(20,6) |  |  |
| 8 | `spread` | 漲跌價差 | NUMERIC(20,6) |  |  |
| 9 | `Trading_turnover` | 成交筆數 | NUMERIC(20,6) |  |  |

### TaiwanStockPriceAdj｜還原股價（日） `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1994-09-14 data_id_source=`roster` n_stocks=2758 n_dates=7321 recon=`roster-scoped` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 交易日 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `Trading_Volume` | 成交股數 | NUMERIC(21,6) |  |  |
| 3 | `Trading_money` | 成交金額 | NUMERIC(23,6) |  |  |
| 4 | `open` | 還原開盤價 | NUMERIC(20,6) |  |  |
| 5 | `max` | 還原最高價 | NUMERIC(20,6) |  |  |
| 6 | `min` | 還原最低價 | NUMERIC(20,6) |  |  |
| 7 | `close` | 還原收盤價 | NUMERIC(20,6) |  |  |
| 8 | `spread` | 漲跌價差 | NUMERIC(20,6) |  |  |
| 9 | `Trading_turnover` | 成交筆數 | NUMERIC(20,6) |  |  |

### TaiwanStockPriceLimit｜每日漲跌停價 `F(id)` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2000-01-03 data_id_source=`roster` n_stocks=3101 n_dates=6480 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 交易日 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `reference_price` | 參考價 | NUMERIC(20,6) |  |  |
| 3 | `limit_up` | 漲停價 | NUMERIC(20,6) |  |  |
| 4 | `limit_down` | 跌停價 | NUMERIC(20,6) |  |  |

### TaiwanStockPriceTick｜台股逐筆成交 `B` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=NULL data_id_source=`roster` n_stocks=3101 n_dates=None recon=`roster-scoped` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | DATE | 🔑 |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `deal_price` | 成交價 | NUMERIC(20,6) | 🔑 |  |
| 3 | `volume` | 成交量(口) | NUMERIC(20,6) | 🔑 |  |
| 4 | `Time` | 成交時間 | VARCHAR(255) | 🔑 |  |
| 5 | `TickType` | 內外盤別 | NUMERIC(20,6) | 🔑 |  |

### TaiwanStockStatisticsOfOrderBookAndTrade｜委託成交統計 `F` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=2005-01-01 data_id_source=`none` n_stocks=None n_dates=5256 recon=`by-date` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `Time` | 時間 | VARCHAR(255) | 🔑 |  |
| 1 | `TotalBuyOrder` | 累計委買筆數 | NUMERIC(20,6) |  |  |
| 2 | `TotalBuyVolume` | 累計委買張數 | NUMERIC(20,6) |  |  |
| 3 | `TotalSellOrder` | 累計委賣筆數 | NUMERIC(20,6) |  |  |
| 4 | `TotalSellVolume` | 累計委賣張數 | NUMERIC(20,6) |  |  |
| 5 | `TotalDealOrder` | 累計成交筆數 | NUMERIC(20,6) |  |  |
| 6 | `TotalDealVolume` | 累計成交張數 | NUMERIC(20,6) |  |  |
| 7 | `TotalDealMoney` | 累計成交金額 | NUMERIC(20,6) |  |  |
| 8 | `date` | 日期 | DATE | 🔑 |  |

### TaiwanStockSuspended｜暫停交易 `B` ✅
- ep=`/data` mode=`by-date` freq=`daily` earliest=2025-03-01 data_id_source=`none` n_stocks=3101 n_dates=317 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 暫停交易日期 | DATE |  |  |
| 1 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 2 | `suspension_time` | 暫停交易時間 | VARCHAR(255) |  |  |
| 3 | `resumption_date` | 恢復交易日期 | VARCHAR(255) |  |  |
| 4 | `resumption_time` | 恢復交易時間 | VARCHAR(255) |  |  |

### TaiwanStockTotalReturnIndex｜發行量加權股價報酬指數 `F` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=2003-01-02 data_id_source=`doc` n_stocks=2 n_dates=5746 recon=`by-dim-id` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `price` | 指數值 | NUMERIC(20,6) |  |  |
| 1 | `stock_id` | 指數代號（TAIEX/TPEx） | VARCHAR(255) | 🔑 |  |
| 2 | `date` | 資料日期 | DATE | 🔑 |  |

### TaiwanStockTradingDate｜交易日曆 `F` ✅
- ep=`/data` mode=`market` freq=`single-series` earliest=1999-01-01 data_id_source=`none` n_stocks=1 n_dates=6727 recon=`by-date` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 交易日 | DATE | 🔑 |  |

### TaiwanStockWeekPrice｜週K線 `B` ✅
- ep=`/data` mode=`per-stock` freq=`daily` earliest=1999-12-20 data_id_source=`roster` n_stocks=3101 n_dates=6490 recon=`roster-scoped` prov=`probe`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `stock_id` | 股票代號 | VARCHAR(255) | 🔑 |  |
| 1 | `yweek` | 年度週別 | VARCHAR(255) |  |  |
| 2 | `max` | 最高價 | NUMERIC(20,6) |  |  |
| 3 | `min` | 最低價 | NUMERIC(20,6) |  |  |
| 4 | `trading_volume` | 成交股數 | NUMERIC(20,6) |  |  |
| 5 | `trading_money` | 成交金額 | NUMERIC(22,6) |  |  |
| 6 | `trading_turnover` | 成交筆數 | NUMERIC(20,6) |  |  |
| 7 | `date` | 交易日 | DATE | 🔑 |  |
| 8 | `close` | 收盤價 | NUMERIC(20,6) |  |  |
| 9 | `open` | 開盤價 | NUMERIC(20,6) |  |  |
| 10 | `spread` | 漲跌價差 | NUMERIC(20,6) |  |  |

### TaiwanVariousIndicators5Seconds｜大盤每5秒各項指標 `F` 🚫excl
- ep=`/data` mode=`excluded` freq=`intraday` earliest=2005-01-01 data_id_source=`none` n_stocks=None n_dates=5256 recon=`by-date` prov=`official/INTRADAY`
  - ⚠️ 單位小於日 intraday（官方 sub-day / #4 日為最小單位、不抓）

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `date` | 日期 | VARCHAR(255) | 🔑 |  |
| 1 | `TAIEX` | 加權指數 | NUMERIC(20,6) |  |  |


## fred / Macro

### fred_series｜FRED 總經序列（augur 落地表） `FRED` ✅
- ep=`/series/observations` mode=`per-series` freq=`daily` earliest=1919-01-01 data_id_source=`series` n_stocks=None n_dates=15238 recon=`by-dim-id` prov=`DB`

| # | column | 中文 | type | pk | a-l |
|--|--|--|--|--|--|
| 0 | `series_id` | 序列代號 | VARCHAR(255) | 🔑 |  |
| 1 | `date` | 觀測日期 | DATE | 🔑 |  |
| 2 | `value` | 觀測值 | NUMERIC(20,6) |  |  |


## ⭐ Dedicated endpoint datasets(官方doc、不在list_datasets)

### TaiwanStockTradingDailyReportSecIdAgg `Sponsor` 🚫dedicated · params=
  0. `securities_trader`
  1. `securities_trader_id`
  2. `stock_id`
  3. `date`
  4. `buy_volume`
  5. `sell_volume`
  6. `buy_price`
  7. `sell_price`

### taiwan_stock_tick_snapshot `Sponsor` 🚫dedicated · params=
  0. `close`
  1. `high`
  2. `low`
  3. `open`
  4. `volume`
  5. `total_volume`
  6. `change_price`
  7. `change_rate`
  8. `date`
  9. `stock_id`

### taiwan_futures_snapshot `Sponsor` 🚫dedicated · params=
  0. `open`
  1. `high`
  2. `low`
  3. `close`
  4. `volume`
  5. `total_volume`
  6. `change_price`
  7. `change_rate`
  8. `date`
  9. `futures_id`

### taiwan_options_snapshot `Sponsor` 🚫dedicated · params=
  0. `open`
  1. `high`
  2. `low`
  3. `close`
  4. `volume`
  5. `total_volume`
  6. `change_price`
  7. `change_rate`
  8. `date`
  9. `options_id`

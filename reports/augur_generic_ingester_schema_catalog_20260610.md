# augur 通用 ingester — Live API 驗證 schema catalog (2026-06-10)

**來源(#1/#10 可溯源)**：英文欄名/大小寫/型別 = live FinMind data API 取樣 → `generic_schema.infer_schema/detect_keys`(ingester 同一套);中文 = FinMind 官方文件 `finmind.github.io/llms-full.txt`(標註來源,非資料 API);FRED 同。

**PK 校正**：探測取單日樣本時 `date` 在當日唯一會被 detect_keys 略過;ingester 實跑為多日(per-stock 全史 / by-date `require_keys=('date',)`)→ 凡含 `date` 欄者 `date` 必入 PK。本表 PK 已據此校正,反映 ingester 實際建表。

**型別**：`NUMERIC(20,6)` 為數字下限(超出自動加大);字串 `VARCHAR(255)`,超過 → `TEXT`;`date` 純 `YYYY-MM-DD` → `DATE`。識別碼(stock_id/year/cb_id 等)強制字串免掉前導零。

## 總計

- FinMind dataset 全集(`list_datasets` 422 enum)：**93**

- 治權排除：intraday 8(#4)+ OUT_OF_UNIT 3(#3)= 11

- 候選 = 82；**live 取樣成功建 schema = 80 表**；live 未取樣 = 2

- **可建表 80 表合計欄位 = 659 欄**（FinMind）+ FRED `fred_series` 3 欄

- 連同 FRED：**81 表 / 662 欄**


## 分類摘要

| 類別 | 表數 | 欄位數 |
|---|---|---|
| A. 台股價格/基礎 | 19 | 120 |
| B. 台股籌碼/法人 | 14 | 141 |
| C. 台股基本面/財務 | 13 | 96 |
| D. 台股可轉債 | 4 | 57 |
| E. 台股衍生品(期/權) | 18 | 181 |
| F. 國際股市(非台股) | 8 | 52 |
| G. 全球商品/總經 | 4 | 12 |


## A. 台股價格/基礎

### `TaiwanBusinessIndicator`  (9 欄)
- 取樣 mode：market(無id,寬窗)；PK：`['date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `leading` | NUMERIC(20,6) | 領先指標 |  |
| 3 | `leading_notrend` | NUMERIC(20,6) | 領先指標(不含趨勢) |  |
| 4 | `coincident` | NUMERIC(20,6) | 同時指標 |  |
| 5 | `coincident_notrend` | NUMERIC(20,6) | 同時指標(不含趨勢) |  |
| 6 | `lagging` | NUMERIC(20,6) | 落後指標 |  |
| 7 | `lagging_notrend` | NUMERIC(20,6) | 落後指標(不含趨勢) |  |
| 8 | `monitoring` | NUMERIC(20,6) | 景氣對策信號(分數) |  |
| 9 | `monitoring_color` | VARCHAR(255) | 景氣對策信號(燈號) |  |

### `TaiwanExchangeRate`  (6 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['currency', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `currency` | VARCHAR(255) | 幣別 | ✔ |
| 3 | `cash_buy` | NUMERIC(20,6) | 現鈔買進 |  |
| 4 | `cash_sell` | NUMERIC(20,6) | 現鈔賣出 |  |
| 5 | `spot_buy` | NUMERIC(20,6) | 即期買進 |  |
| 6 | `spot_sell` | NUMERIC(20,6) | 即期賣出 |  |

### `TaiwanStock10Year`  (3 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `close` | NUMERIC(20,6) | 十年線收盤價 |  |

### `TaiwanStockDayTrading`  (6 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `BuyAfterSale` | VARCHAR(255) | 先買後賣/先賣後買 |  |
| 4 | `Volume` | NUMERIC(20,6) | 成交數量 |  |
| 5 | `BuyAmount` | NUMERIC(21,6) | 買進金額 |  |
| 6 | `SellAmount` | NUMERIC(21,6) | 賣出金額 |  |

### `TaiwanStockDayTradingBorrowingFeeRate`  (5 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |  |
| 4 | `InvestorBorrowedShares` | NUMERIC(20,6) | (文件未列) |  |
| 5 | `InvestorBorrowingFeeRate` | NUMERIC(20,6) | (文件未列) |  |

### `TaiwanStockDayTradingSuspension`  (4 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `end_date` | DATE | 終止日期 |  |
| 4 | `reason` | VARCHAR(255) | 暫停原因 |  |

### `TaiwanStockIndustryChain`  (4 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'industry', 'sub_industry', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 2 | `industry` | VARCHAR(255) | 產業別 | ✔ |
| 3 | `sub_industry` | VARCHAR(255) | 次產業別 | ✔ |
| 4 | `date` | DATE | 日期 | ✔ |

### `TaiwanStockInfo`  (5 欄)
- 取樣 mode：per-stock(2330,寬窗)；PK：`['stock_id', 'date', 'type', 'industry_category']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `industry_category` | VARCHAR(255) | 產業類別 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |  |
| 4 | `type` | VARCHAR(255) | 類型 | ✔ |
| 5 | `date` | DATE | 日期 | ✔ |

### `TaiwanStockInfoWithWarrant`  (5 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `industry_category` | VARCHAR(255) | 產業類別 |  |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |  |
| 4 | `type` | VARCHAR(255) | 類型 |  |
| 5 | `date` | DATE | 日期 | ✔ |

### `TaiwanStockInfoWithWarrantSummary`  (12 欄)
- 取樣 mode：per-stock(2330,寬窗)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `close` | NUMERIC(20,6) | 收盤價 |  |
| 4 | `target_stock_id` | NUMERIC(20,6) | 標的股票代碼 |  |
| 5 | `target_close` | NUMERIC(20,6) | 標的收盤價 |  |
| 6 | `type` | VARCHAR(255) | 類型 |  |
| 7 | `fulfillment_method` | VARCHAR(255) | 履約方式 |  |
| 8 | `end_date` | DATE | 終止日期 |  |
| 9 | `fulfillment_start_date` | DATE | 履約開始日期 |  |
| 10 | `fulfillment_end_date` | DATE | 履約終止日期 |  |
| 11 | `exercise_ratio` | NUMERIC(20,6) | 履約比例 |  |
| 12 | `fulfillment_price` | NUMERIC(20,6) | 履約價格 |  |

### `TaiwanStockMonthPrice`  (11 欄)
- 取樣 mode：per-stock(2330,寬窗)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 2 | `ymonth` | VARCHAR(255) | 月份 |  |
| 3 | `max` | NUMERIC(20,6) | 最高價 |  |
| 4 | `min` | NUMERIC(20,6) | 最低價 |  |
| 5 | `trading_volume` | NUMERIC(20,6) | 成交量 |  |
| 6 | `trading_money` | NUMERIC(23,6) | 成交金額 |  |
| 7 | `trading_turnover` | NUMERIC(20,6) | 成交回合率 |  |
| 8 | `date` | DATE | 日期 | ✔ |
| 9 | `close` | NUMERIC(20,6) | 收盤價 |  |
| 10 | `open` | NUMERIC(20,6) | 開盤價 |  |
| 11 | `spread` | NUMERIC(20,6) | 漲跌價差 |  |

### `TaiwanStockNews`  (5 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'stock_id', 'source', 'title']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | VARCHAR(255) | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `link` | TEXT | 新聞連結 |  |
| 4 | `source` | VARCHAR(255) | 新聞來源 | ✔ |
| 5 | `title` | VARCHAR(255) | 新聞標題 | ✔ |

### `TaiwanStockPrice`  (10 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `Trading_Volume` | NUMERIC(21,6) | 成交股數 |  |
| 4 | `Trading_money` | NUMERIC(23,6) | 成交金額 |  |
| 5 | `open` | NUMERIC(20,6) | 開盤價 |  |
| 6 | `max` | NUMERIC(20,6) | 最高價 |  |
| 7 | `min` | NUMERIC(20,6) | 最低價 |  |
| 8 | `close` | NUMERIC(20,6) | 收盤價 |  |
| 9 | `spread` | NUMERIC(20,6) | 漲跌價差 |  |
| 10 | `Trading_turnover` | NUMERIC(20,6) | 成交回合率 |  |

### `TaiwanStockPriceAdj`  (10 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `Trading_Volume` | NUMERIC(21,6) | 成交股數 |  |
| 4 | `Trading_money` | NUMERIC(23,6) | 成交金額 |  |
| 5 | `open` | NUMERIC(20,6) | 開盤價 |  |
| 6 | `max` | NUMERIC(20,6) | 最高價 |  |
| 7 | `min` | NUMERIC(20,6) | 最低價 |  |
| 8 | `close` | NUMERIC(20,6) | 還原收盤價 |  |
| 9 | `spread` | NUMERIC(20,6) | 漲跌價差 |  |
| 10 | `Trading_turnover` | NUMERIC(20,6) | 成交回合率 |  |

### `TaiwanStockPriceLimit`  (5 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `reference_price` | NUMERIC(20,6) | 參考價 |  |
| 4 | `limit_up` | NUMERIC(20,6) | 漲停價 |  |
| 5 | `limit_down` | NUMERIC(20,6) | 跌停價 |  |

### `TaiwanStockSuspended`  (5 欄)
- 取樣 mode：market(無id,寬窗)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `suspension_time` | VARCHAR(255) | 暫停交易時間 |  |
| 4 | `resumption_date` | DATE | 恢復交易日期 |  |
| 5 | `resumption_time` | VARCHAR(255) | 恢復交易時間 |  |

### `TaiwanStockTotalReturnIndex`  (3 欄)
- 取樣 mode：2nd:{'data_id': 'TAIEX', 'start_date': '2024-01-01'}；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `price` | NUMERIC(20,6) | 指數價格 |  |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `date` | DATE | 日期 | ✔ |

### `TaiwanStockTradingDate`  (1 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 交易日期 | ✔ |

### `TaiwanStockWeekPrice`  (11 欄)
- 取樣 mode：per-stock(2330,寬窗)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 2 | `yweek` | VARCHAR(255) | 週別 |  |
| 3 | `max` | NUMERIC(20,6) | 最高價 |  |
| 4 | `min` | NUMERIC(20,6) | 最低價 |  |
| 5 | `trading_volume` | NUMERIC(20,6) | 成交量 |  |
| 6 | `trading_money` | NUMERIC(22,6) | 成交金額 |  |
| 7 | `trading_turnover` | NUMERIC(20,6) | 成交回合率 |  |
| 8 | `date` | DATE | 日期 | ✔ |
| 9 | `close` | NUMERIC(20,6) | 收盤價 |  |
| 10 | `open` | NUMERIC(20,6) | 開盤價 |  |
| 11 | `spread` | NUMERIC(20,6) | 漲跌價差 |  |


## B. 台股籌碼/法人

### `TaiwanDailyShortSaleBalances`  (15 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 2 | `MarginShortSalesPreviousDayBalance` | NUMERIC(20,6) | 融券昨日餘額 |  |
| 3 | `MarginShortSalesShortSales` | NUMERIC(20,6) | 融券賣出 |  |
| 4 | `MarginShortSalesShortCovering` | NUMERIC(20,6) | 融券買進 |  |
| 5 | `MarginShortSalesStockRedemption` | NUMERIC(20,6) | 現股償還 |  |
| 6 | `MarginShortSalesCurrentDayBalance` | NUMERIC(20,6) | 融券今日餘額 |  |
| 7 | `MarginShortSalesQuota` | NUMERIC(20,6) | 融券額度 |  |
| 8 | `SBLShortSalesPreviousDayBalance` | NUMERIC(20,6) | 借券昨日餘額 |  |
| 9 | `SBLShortSalesShortSales` | NUMERIC(20,6) | 借券賣出 |  |
| 10 | `SBLShortSalesReturns` | NUMERIC(20,6) | 借券還券 |  |
| 11 | `SBLShortSalesAdjustments` | NUMERIC(20,6) | 借券調整 |  |
| 12 | `SBLShortSalesCurrentDayBalance` | NUMERIC(20,6) | 借券今日餘額 |  |
| 13 | `SBLShortSalesQuota` | NUMERIC(20,6) | 借券額度 |  |
| 14 | `SBLShortSalesShortCovering` | NUMERIC(20,6) | 借券買進 |  |
| 15 | `date` | DATE | 日期 | ✔ |

### `TaiwanSecuritiesTraderInfo`  (5 欄)
- 取樣 mode：per-stock(2330,寬窗)；PK：`['securities_trader_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `securities_trader_id` | VARCHAR(255) | 證券商代號 | ✔ |
| 2 | `securities_trader` | VARCHAR(255) | 證券商名稱 |  |
| 3 | `date` | DATE | 日期 | ✔ |
| 4 | `address` | VARCHAR(255) | 地址 |  |
| 5 | `phone` | VARCHAR(255) | 電話 |  |

### `TaiwanStockBlockTrade`  (6 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'stock_id', 'trade_type', 'price', 'volume', 'trading_money']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `trade_type` | VARCHAR(255) | 交易類型 | ✔ |
| 4 | `price` | NUMERIC(20,6) | 成交價格 | ✔ |
| 5 | `volume` | NUMERIC(20,6) | 成交數量 | ✔ |
| 6 | `trading_money` | NUMERIC(21,6) | 成交金額 | ✔ |

### `TaiwanStockDispositionSecuritiesPeriod`  (8 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |  |
| 4 | `disposition_cnt` | NUMERIC(20,6) | 處置張數 |  |
| 5 | `condition` | VARCHAR(255) | 處置條件 |  |
| 6 | `measure` | TEXT | 處置方式 |  |
| 7 | `period_start` | DATE | 期間開始 |  |
| 8 | `period_end` | DATE | 期間終止 |  |

### `TaiwanStockGovernmentBankBuySell`  (7 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'stock_id', 'buy_amount', 'sell_amount', 'buy', 'sell', 'bank_name']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `buy_amount` | NUMERIC(20,6) | 買進金額 | ✔ |
| 4 | `sell_amount` | NUMERIC(20,6) | 賣出金額 | ✔ |
| 5 | `buy` | NUMERIC(20,6) | 買進張數 | ✔ |
| 6 | `sell` | NUMERIC(20,6) | 賣出張數 | ✔ |
| 7 | `bank_name` | VARCHAR(255) | 銀行名稱 | ✔ |

### `TaiwanStockHoldingSharesPer`  (6 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date', 'HoldingSharesLevel']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `HoldingSharesLevel` | VARCHAR(255) | 持股級距 | ✔ |
| 4 | `people` | NUMERIC(20,6) | 人數 |  |
| 5 | `percent` | NUMERIC(20,6) | 百分比 |  |
| 6 | `unit` | NUMERIC(21,6) | 單位 |  |

### `TaiwanStockInstitutionalInvestorsBuySell`  (5 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date', 'name']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `buy` | NUMERIC(20,6) | 買進金額 |  |
| 4 | `name` | VARCHAR(255) | 法人名稱 | ✔ |
| 5 | `sell` | NUMERIC(20,6) | 賣出金額 |  |

### `TaiwanStockLoanCollateralBalance`  (37 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `market` | VARCHAR(255) | 市場別 |  |
| 4 | `MarginPreviousDayBalance` | NUMERIC(20,6) | (文件未列) |  |
| 5 | `MarginBuy` | NUMERIC(20,6) | (文件未列) |  |
| 6 | `MarginSell` | NUMERIC(20,6) | (文件未列) |  |
| 7 | `MarginCashRedemption` | NUMERIC(20,6) | (文件未列) |  |
| 8 | `MarginCurrentDayBalance` | NUMERIC(20,6) | (文件未列) |  |
| 9 | `MarginNextDayQuota` | NUMERIC(20,6) | (文件未列) |  |
| 10 | `SecuritiesFirmLoanPreviousDayBalance` | NUMERIC(20,6) | (文件未列) |  |
| 11 | `SecuritiesFirmLoanBuy` | NUMERIC(20,6) | (文件未列) |  |
| 12 | `SecuritiesFirmLoanSell` | NUMERIC(20,6) | (文件未列) |  |
| 13 | `SecuritiesFirmLoanCashRedemption` | NUMERIC(20,6) | (文件未列) |  |
| 14 | `SecuritiesFirmLoanReplacement` | NUMERIC(20,6) | (文件未列) |  |
| 15 | `SecuritiesFirmLoanCurrentDayBalance` | NUMERIC(20,6) | (文件未列) |  |
| 16 | `SecuritiesFirmLoanNextDayQuota` | NUMERIC(20,6) | (文件未列) |  |
| 17 | `UnrestrictedLoanPreviousDayBalance` | NUMERIC(20,6) | (文件未列) |  |
| 18 | `UnrestrictedLoanBuy` | NUMERIC(20,6) | (文件未列) |  |
| 19 | `UnrestrictedLoanSell` | NUMERIC(20,6) | (文件未列) |  |
| 20 | `UnrestrictedLoanCashRedemption` | NUMERIC(20,6) | (文件未列) |  |
| 21 | `UnrestrictedLoanReplacement` | NUMERIC(20,6) | (文件未列) |  |
| 22 | `UnrestrictedLoanCurrentDayBalance` | NUMERIC(20,6) | (文件未列) |  |
| 23 | `UnrestrictedLoanNextDayQuota` | NUMERIC(20,6) | (文件未列) |  |
| 24 | `SecuritiesFinanceSecuredLoanPreviousDayBalance` | NUMERIC(20,6) | (文件未列) |  |
| 25 | `SecuritiesFinanceSecuredLoanBuy` | NUMERIC(20,6) | (文件未列) |  |
| 26 | `SecuritiesFinanceSecuredLoanSell` | NUMERIC(20,6) | (文件未列) |  |
| 27 | `SecuritiesFinanceSecuredLoanCashRedemption` | NUMERIC(20,6) | (文件未列) |  |
| 28 | `SecuritiesFinanceSecuredLoanReplacement` | NUMERIC(20,6) | (文件未列) |  |
| 29 | `SecuritiesFinanceSecuredLoanCurrentDayBalance` | NUMERIC(20,6) | (文件未列) |  |
| 30 | `SecuritiesFinanceSecuredLoanNextDayQuota` | NUMERIC(20,6) | (文件未列) |  |
| 31 | `SettlementMarginPreviousDayBalance` | NUMERIC(20,6) | (文件未列) |  |
| 32 | `SettlementMarginBuy` | NUMERIC(20,6) | (文件未列) |  |
| 33 | `SettlementMarginSell` | NUMERIC(20,6) | (文件未列) |  |
| 34 | `SettlementMarginCashRedemption` | NUMERIC(20,6) | (文件未列) |  |
| 35 | `SettlementMarginReplacement` | NUMERIC(20,6) | (文件未列) |  |
| 36 | `SettlementMarginCurrentDayBalance` | NUMERIC(20,6) | (文件未列) |  |
| 37 | `SettlementMarginNextDayQuota` | NUMERIC(20,6) | (文件未列) |  |

### `TaiwanStockMarginPurchaseShortSale`  (16 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `MarginPurchaseBuy` | NUMERIC(20,6) | 融資買進 |  |
| 4 | `MarginPurchaseCashRepayment` | NUMERIC(20,6) | 融資現金償還 |  |
| 5 | `MarginPurchaseLimit` | NUMERIC(20,6) | 融資額度 |  |
| 6 | `MarginPurchaseSell` | NUMERIC(20,6) | 融資賣出 |  |
| 7 | `MarginPurchaseTodayBalance` | NUMERIC(20,6) | 融資今日餘額 |  |
| 8 | `MarginPurchaseYesterdayBalance` | NUMERIC(20,6) | 融資昨日餘額 |  |
| 9 | `Note` | VARCHAR(255) | 備註 |  |
| 10 | `OffsetLoanAndShort` | NUMERIC(20,6) | 資券相抵 |  |
| 11 | `ShortSaleBuy` | NUMERIC(20,6) | 融券買進 |  |
| 12 | `ShortSaleCashRepayment` | NUMERIC(20,6) | 融券現金償還 |  |
| 13 | `ShortSaleLimit` | NUMERIC(20,6) | 融券額度 |  |
| 14 | `ShortSaleSell` | NUMERIC(20,6) | 融券賣出 |  |
| 15 | `ShortSaleTodayBalance` | NUMERIC(20,6) | 融券今日餘額 |  |
| 16 | `ShortSaleYesterdayBalance` | NUMERIC(20,6) | 融券昨日餘額 |  |

### `TaiwanStockMarginShortSaleSuspension`  (4 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `end_date` | DATE | 終止日期 |  |
| 4 | `reason` | VARCHAR(255) | 暫停原因 |  |

### `TaiwanStockSecuritiesLending`  (8 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'stock_id', 'transaction_type', 'volume', 'fee_rate', 'close', 'original_return_date', 'original_lending_period']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `transaction_type` | VARCHAR(255) | 交易類型 | ✔ |
| 4 | `volume` | NUMERIC(20,6) | 成交數量 | ✔ |
| 5 | `fee_rate` | NUMERIC(20,6) | 費率 | ✔ |
| 6 | `close` | NUMERIC(20,6) | 收盤價 | ✔ |
| 7 | `original_return_date` | DATE | 原訂還券日期 | ✔ |
| 8 | `original_lending_period` | NUMERIC(20,6) | 原訂借券期間 | ✔ |

### `TaiwanStockShareholding`  (13 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |  |
| 4 | `InternationalCode` | VARCHAR(255) | 國際代碼 |  |
| 5 | `ForeignInvestmentRemainingShares` | NUMERIC(21,6) | 外資持股剩餘額度 |  |
| 6 | `ForeignInvestmentShares` | NUMERIC(21,6) | 外資持股數 |  |
| 7 | `ForeignInvestmentRemainRatio` | NUMERIC(20,6) | 外資持股剩餘比例 |  |
| 8 | `ForeignInvestmentSharesRatio` | NUMERIC(20,6) | 外資持股比例 |  |
| 9 | `ForeignInvestmentUpperLimitRatio` | NUMERIC(20,6) | 外資持股上限比例 |  |
| 10 | `ChineseInvestmentUpperLimitRatio` | NUMERIC(20,6) | 陸資持股上限比例 |  |
| 11 | `NumberOfSharesIssued` | NUMERIC(21,6) | 已發行股數 |  |
| 12 | `RecentlyDeclareDate` | DATE | 最近申報日期 |  |
| 13 | `note` | VARCHAR(255) | 備註 |  |

### `TaiwanStockTotalInstitutionalInvestors`  (4 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'name']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `buy` | NUMERIC(22,6) | 三大法人買進 |  |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `name` | VARCHAR(255) | 法人名稱 | ✔ |
| 4 | `sell` | NUMERIC(22,6) | 三大法人賣出 |  |

### `TaiwanStockTotalMarginPurchaseShortSale`  (7 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'name']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `TodayBalance` | NUMERIC(22,6) | 今日餘額 |  |
| 2 | `YesBalance` | NUMERIC(22,6) | 昨日餘額 |  |
| 3 | `buy` | NUMERIC(21,6) | 買進 |  |
| 4 | `date` | DATE | 日期 | ✔ |
| 5 | `name` | VARCHAR(255) | 名稱 | ✔ |
| 6 | `Return` | NUMERIC(20,6) | 回補 |  |
| 7 | `sell` | NUMERIC(21,6) | 賣出 |  |


## C. 台股基本面/財務

### `TaiwanStockBalanceSheet`  (5 欄)
- 取樣 mode：per-stock(2330,寬窗)；PK：`['stock_id', 'date', 'type']`
- `origin_name` 中文項目(樣本51項，列前12)：不動產、廠房及設備、使用權資產、保留盈餘合計、其他應付款、其他應收款－關係人淨額、其他權益合計、其他流動負債、其他流動資產、其他非流動負債、其他非流動資產、存貨、應付公司債 …

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `type` | VARCHAR(255) | 資產負債項目類型 | ✔ |
| 4 | `value` | NUMERIC(23,6) | 數值 |  |
| 5 | `origin_name` | VARCHAR(255) | 原始項目名稱(中文) |  |

### `TaiwanStockCapitalReductionReferencePrice`  (9 欄)
- 取樣 mode：2nd:{'data_id': '2363', 'start_date': '2008-01-01'}；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `ClosingPriceonTheLastTradingDay` | NUMERIC(20,6) | 最後交易日收盤價 |  |
| 4 | `PostReductionReferencePrice` | NUMERIC(20,6) | 減資後恢復買賣參考價 |  |
| 5 | `LimitUp` | NUMERIC(20,6) | 漲停價 |  |
| 6 | `LimitDown` | NUMERIC(20,6) | 跌停價 |  |
| 7 | `OpeningReferencePrice` | NUMERIC(20,6) | 開盤競價基準 |  |
| 8 | `ExrightReferencePrice` | NUMERIC(20,6) | 除權參考價 |  |
| 9 | `ReasonforCapitalReduction` | VARCHAR(255) | 減資原因 |  |

### `TaiwanStockCashFlowsStatement`  (5 欄)
- 取樣 mode：per-stock(2330,寬窗)；PK：`['stock_id', 'date', 'type']`
- `origin_name` 中文項目(樣本27項，列前12)：償還公司債、償還長期借款、其他投資活動、利息收入、利息費用、取得不動產、廠房及設備、存出保證金減少、存貨（增加）減少、應付帳款、應收帳款（增加）減少、投資活動之淨現金流入（流出）、折舊費用 …

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `type` | VARCHAR(255) | 現金流項目類型 | ✔ |
| 4 | `value` | NUMERIC(23,6) | 數值 |  |
| 5 | `origin_name` | VARCHAR(255) | 原始項目名稱(中文) |  |

### `TaiwanStockDelisting`  (3 欄)
- 取樣 mode：market(無id,寬窗)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |  |

### `TaiwanStockDividend`  (22 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `year` | VARCHAR(255) | 年度 |  |
| 4 | `StockEarningsDistribution` | NUMERIC(20,6) | 股票股利-盈餘配股 |  |
| 5 | `StockStatutorySurplus` | NUMERIC(20,6) | 股票股利-法定盈餘公積 |  |
| 6 | `StockExDividendTradingDate` | VARCHAR(255) | 股票除權交易日 |  |
| 7 | `TotalEmployeeStockDividend` | NUMERIC(20,6) | 員工股票股利總額 |  |
| 8 | `TotalEmployeeStockDividendAmount` | NUMERIC(20,6) | 員工股票股利金額 |  |
| 9 | `RatioOfEmployeeStockDividendOfTotal` | NUMERIC(20,6) | 員工股票股利佔比 |  |
| 10 | `RatioOfEmployeeStockDividend` | NUMERIC(20,6) | 員工股票股利比例 |  |
| 11 | `CashEarningsDistribution` | NUMERIC(20,6) | 現金股利-盈餘配息 |  |
| 12 | `CashStatutorySurplus` | NUMERIC(20,6) | 現金股利-法定盈餘公積 |  |
| 13 | `CashExDividendTradingDate` | DATE | 現金除息交易日 |  |
| 14 | `CashDividendPaymentDate` | DATE | 現金股利發放日 |  |
| 15 | `TotalEmployeeCashDividend` | NUMERIC(20,6) | 員工現金股利 |  |
| 16 | `TotalNumberOfCashCapitalIncrease` | NUMERIC(20,6) | 現金增資總股數 |  |
| 17 | `CashIncreaseSubscriptionRate` | NUMERIC(20,6) | 現金增資認購比例 |  |
| 18 | `CashIncreaseSubscriptionpRrice` | NUMERIC(20,6) | 現金增資認購價格 |  |
| 19 | `RemunerationOfDirectorsAndSupervisors` | NUMERIC(20,6) | 董監酬勞 |  |
| 20 | `ParticipateDistributionOfTotalShares` | NUMERIC(20,6) | 參與分配總股數 |  |
| 21 | `AnnouncementDate` | DATE | 公告日期 |  |
| 22 | `AnnouncementTime` | VARCHAR(255) | 公告時間 |  |

### `TaiwanStockDividendResult`  (10 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `before_price` | NUMERIC(20,6) | 除權息前價格 |  |
| 4 | `after_price` | NUMERIC(20,6) | 除權息後價格 |  |
| 5 | `stock_and_cache_dividend` | NUMERIC(20,6) | 股票及現金股利 |  |
| 6 | `stock_or_cache_dividend` | VARCHAR(255) | 股票或現金股利 |  |
| 7 | `max_price` | NUMERIC(20,6) | 最高價 |  |
| 8 | `min_price` | NUMERIC(20,6) | 最低價 |  |
| 9 | `open_price` | NUMERIC(20,6) | 開盤價 |  |
| 10 | `reference_price` | NUMERIC(20,6) | 參考價 |  |

### `TaiwanStockFinancialStatements`  (5 欄)
- 取樣 mode：per-stock(2330,寬窗)；PK：`['stock_id', 'date', 'type']`
- `origin_name` 中文項目(樣本17項，列前12)：其他收益及費損淨額、其他綜合損益（淨額）、基本每股盈餘、所得稅費用（利益）、本期淨利（淨損）、本期綜合損益總額、淨利（淨損）歸屬於母公司業主、淨利（淨損）歸屬於非控制權益、營業利益（損失）、營業外收入及支出、營業成本、營業收入 …

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `type` | VARCHAR(255) | 財務項目類型 | ✔ |
| 4 | `value` | NUMERIC(23,6) | 數值 |  |
| 5 | `origin_name` | VARCHAR(255) | 原始項目名稱(中文) |  |

### `TaiwanStockMarketValue`  (3 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `market_value` | NUMERIC(24,6) | 股價市值 |  |

### `TaiwanStockMarketValueWeight`  (6 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `rank` | NUMERIC(20,6) | 排名 |  |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |  |
| 4 | `weight_per` | NUMERIC(20,6) | 市值比重百分比 |  |
| 5 | `date` | DATE | 日期 | ✔ |
| 6 | `type` | VARCHAR(255) | 市場別(twse/tpex) |  |

### `TaiwanStockMonthRevenue`  (7 欄)
- 取樣 mode：per-stock(2330,寬窗)；PK：`['stock_id', 'country', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `country` | VARCHAR(255) | 國家 | ✔ |
| 4 | `revenue` | NUMERIC(22,6) | 單月營收 |  |
| 5 | `revenue_month` | NUMERIC(20,6) | 營收月份 |  |
| 6 | `revenue_year` | NUMERIC(20,6) | 營收年度 |  |
| 7 | `create_time` | DATE | 建立時間 |  |

### `TaiwanStockPER`  (5 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `dividend_yield` | NUMERIC(20,6) | 殖利率 |  |
| 4 | `PER` | NUMERIC(20,6) | 本益比 |  |
| 5 | `PBR` | NUMERIC(20,6) | 淨價比 |  |

### `TaiwanStockParValueChange`  (8 欄)
- 取樣 mode：market(無id,寬窗)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |  |
| 4 | `before_close` | NUMERIC(20,6) | 變更前收盤價 |  |
| 5 | `after_ref_close` | NUMERIC(20,6) | 變更後參考收盤價 |  |
| 6 | `after_ref_max` | NUMERIC(20,6) | 變更後參考最高價 |  |
| 7 | `after_ref_min` | NUMERIC(20,6) | 變更後參考最低價 |  |
| 8 | `after_ref_open` | NUMERIC(20,6) | 變更後參考開盤價 |  |

### `TaiwanStockSplitPrice`  (8 欄)
- 取樣 mode：market(無id,寬窗)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `type` | VARCHAR(255) | 分割類型(分割/反分割) |  |
| 4 | `before_price` | NUMERIC(20,6) | 分割前價格 |  |
| 5 | `after_price` | NUMERIC(20,6) | 分割後價格 |  |
| 6 | `max_price` | NUMERIC(20,6) | 最高價 |  |
| 7 | `min_price` | NUMERIC(20,6) | 最低價 |  |
| 8 | `open_price` | NUMERIC(20,6) | 開盤價 |  |


## D. 台股可轉債

### `TaiwanStockConvertibleBondDaily`  (16 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['cb_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `cb_id` | VARCHAR(255) | 可轉債代碼 | ✔ |
| 2 | `cb_name` | VARCHAR(255) | 可轉債名稱 |  |
| 3 | `transaction_type` | VARCHAR(255) | 交易類型 |  |
| 4 | `close` | NUMERIC(20,6) | 收盤價 |  |
| 5 | `change` | NUMERIC(20,6) | 漲跌價差 |  |
| 6 | `open` | NUMERIC(20,6) | 開盤價 |  |
| 7 | `max` | NUMERIC(20,6) | 最高價 |  |
| 8 | `min` | NUMERIC(20,6) | 最低價 |  |
| 9 | `no_of_transactions` | NUMERIC(20,6) | 成交筆數 |  |
| 10 | `unit` | NUMERIC(20,6) | 交易單位 |  |
| 11 | `trading_value` | NUMERIC(20,6) | 成交金額 |  |
| 12 | `avg_price` | NUMERIC(20,6) | 平均價格 |  |
| 13 | `next_ref_price` | NUMERIC(20,6) | 次日參考價 |  |
| 14 | `next_max_limit` | NUMERIC(20,6) | 次日漲停價 |  |
| 15 | `next_min_limit` | NUMERIC(20,6) | 次日跌停價 |  |
| 16 | `date` | DATE | 日期 | ✔ |

### `TaiwanStockConvertibleBondDailyOverview`  (23 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['cb_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `cb_id` | VARCHAR(255) | 可轉債代碼 | ✔ |
| 2 | `cb_name` | VARCHAR(255) | 可轉債名稱 |  |
| 3 | `date` | DATE | 日期 | ✔ |
| 4 | `InitialDateOfConversion` | DATE | (文件未列) |  |
| 5 | `DueDateOfConversion` | DATE | (文件未列) |  |
| 6 | `InitialDateOfStopConversion` | VARCHAR(255) | (文件未列) |  |
| 7 | `DueDateOfStopConversion` | VARCHAR(255) | (文件未列) |  |
| 8 | `ConversionPrice` | NUMERIC(20,6) | 轉換價格 |  |
| 9 | `NextEffectiveDateOfConversionPrice` | DATE | (文件未列) |  |
| 10 | `LatestInitialDateOfPut` | DATE | (文件未列) |  |
| 11 | `LatestDueDateOfPut` | DATE | (文件未列) |  |
| 12 | `LatestPutPrice` | NUMERIC(20,6) | (文件未列) |  |
| 13 | `InitialDateOfEarlyRedemption` | DATE | (文件未列) |  |
| 14 | `DueDateOfEarlyRedemption` | DATE | (文件未列) |  |
| 15 | `EarlyRedemptionPrice` | NUMERIC(20,6) | (文件未列) |  |
| 16 | `DateOfDelisted` | DATE | (文件未列) |  |
| 17 | `IssuanceAmount` | NUMERIC(20,6) | 發行金額 |  |
| 18 | `OutstandingAmount` | NUMERIC(20,6) | 流通金額 |  |
| 19 | `ReferencePrice` | NUMERIC(20,6) | 參考價 |  |
| 20 | `PriceOfUnderlyingStock` | NUMERIC(20,6) | 標的股票價格 |  |
| 21 | `InitialDateOfSuspension` | VARCHAR(255) | (文件未列) |  |
| 22 | `DueDateOfSuspension` | VARCHAR(255) | (文件未列) |  |
| 23 | `CouponRate` | NUMERIC(20,6) | 票面利率 |  |

### `TaiwanStockConvertibleBondInfo`  (5 欄)
- 取樣 mode：market(無id,寬窗)；PK：`['cb_id']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `cb_id` | VARCHAR(255) | 可轉債代碼 | ✔ |
| 2 | `cb_name` | VARCHAR(255) | 可轉債名稱 |  |
| 3 | `InitialDateOfConversion` | DATE | 轉換開始日期 |  |
| 4 | `DueDateOfConversion` | DATE | 轉換終止日期 |  |
| 5 | `IssuanceAmount` | NUMERIC(20,6) | 發行金額 |  |

### `TaiwanStockConvertibleBondInstitutionalInvestors`  (13 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['cb_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `Foreign_Investor_Buy` | NUMERIC(20,6) | 外資買進 |  |
| 2 | `Foreign_Investor_Sell` | NUMERIC(20,6) | 外資賣出 |  |
| 3 | `Foreign_Investor_Overbuy` | NUMERIC(20,6) | 外資超買 |  |
| 4 | `Investment_Trust_Buy` | NUMERIC(20,6) | 投信買進 |  |
| 5 | `Investment_Trust_Sell` | NUMERIC(20,6) | 投信賣出 |  |
| 6 | `Investment_Trust_Overbuy` | NUMERIC(20,6) | 投信超買 |  |
| 7 | `Dealer_self_Buy` | NUMERIC(20,6) | 自營買進 |  |
| 8 | `Dealer_self_Sell` | NUMERIC(20,6) | 自營賣出 |  |
| 9 | `Dealer_self_Overbuy` | NUMERIC(20,6) | 自營超買 |  |
| 10 | `Total_Overbuy` | NUMERIC(20,6) | 合計超買 |  |
| 11 | `cb_id` | VARCHAR(255) | 可轉債代碼 | ✔ |
| 12 | `cb_name` | VARCHAR(255) | 可轉債名稱 |  |
| 13 | `date` | DATE | 日期 | ✔ |


## E. 台股衍生品(期/權)

### `TaiwanFutOptDailyInfo`  (3 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['code', 'type', 'name']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `code` | VARCHAR(255) | 商品代碼 | ✔ |
| 2 | `type` | VARCHAR(255) | 商品類型 | ✔ |
| 3 | `name` | VARCHAR(255) | 商品名稱 | ✔ |

### `TaiwanFutOptInstitutionalInvestors`  (11 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'name', 'institutional_investors']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `name` | VARCHAR(255) | 名稱 | ✔ |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `institutional_investors` | VARCHAR(255) | 法人別 | ✔ |
| 4 | `long_deal_volume` | NUMERIC(20,6) | (文件未列) |  |
| 5 | `long_deal_amount` | NUMERIC(20,6) | (文件未列) |  |
| 6 | `short_deal_volume` | NUMERIC(20,6) | (文件未列) |  |
| 7 | `short_deal_amount` | NUMERIC(20,6) | (文件未列) |  |
| 8 | `long_open_interest_balance_volume` | NUMERIC(20,6) | (文件未列) |  |
| 9 | `long_open_interest_balance_amount` | NUMERIC(20,6) | (文件未列) |  |
| 10 | `short_open_interest_balance_volume` | NUMERIC(20,6) | (文件未列) |  |
| 11 | `short_open_interest_balance_amount` | NUMERIC(20,6) | (文件未列) |  |

### `TaiwanFutOptTickInfo`  (7 欄)
- 取樣 mode：2nd:{}；PK：`['code', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `code` | VARCHAR(255) | (文件未列) | ✔ |
| 2 | `callput` | VARCHAR(255) | (文件未列) |  |
| 3 | `date` | VARCHAR(255) | 日期 | ✔ |
| 4 | `name` | VARCHAR(255) | 名稱 |  |
| 5 | `listing_date` | DATE | (文件未列) |  |
| 6 | `expire_price` | NUMERIC(20,6) | (文件未列) |  |
| 7 | `update_date` | DATE | (文件未列) |  |

### `TaiwanFuturesDaily`  (13 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'futures_id', 'contract_date', 'open', 'max', 'min', 'close', 'spread', 'spread_per', 'volume', 'settlement_price', 'open_interest', 'trading_session']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `futures_id` | VARCHAR(255) | 期貨代碼 | ✔ |
| 3 | `contract_date` | VARCHAR(255) | 契約月份 | ✔ |
| 4 | `open` | NUMERIC(20,6) | 開盤價 | ✔ |
| 5 | `max` | NUMERIC(20,6) | 最高價 | ✔ |
| 6 | `min` | NUMERIC(20,6) | 最低價 | ✔ |
| 7 | `close` | NUMERIC(20,6) | 收盤價 | ✔ |
| 8 | `spread` | NUMERIC(20,6) | 漲跌點數 | ✔ |
| 9 | `spread_per` | NUMERIC(20,6) | 漲跌百分比 | ✔ |
| 10 | `volume` | NUMERIC(20,6) | 成交量 | ✔ |
| 11 | `settlement_price` | NUMERIC(20,6) | 結算價 | ✔ |
| 12 | `open_interest` | NUMERIC(20,6) | 未平倉量 | ✔ |
| 13 | `trading_session` | VARCHAR(255) | 交易時段 | ✔ |

### `TaiwanFuturesDealerTradingVolumeDaily`  (6 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'dealer_code', 'dealer_name', 'futures_id', 'volume', 'is_after_hour']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `dealer_code` | VARCHAR(255) | 期貨商代號 | ✔ |
| 3 | `dealer_name` | VARCHAR(255) | 期貨商名稱 | ✔ |
| 4 | `futures_id` | VARCHAR(255) | 期貨代碼 | ✔ |
| 5 | `volume` | NUMERIC(20,6) | 成交量 | ✔ |
| 6 | `is_after_hour` | VARCHAR(255) | 是否夜盤 | ✔ |

### `TaiwanFuturesFinalSettlementPrice`  (8 欄)
- 取樣 mode：special(TX)；PK：`['futures_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `contract_month` | VARCHAR(255) | 契約月份 |  |
| 3 | `futures_type` | VARCHAR(255) | 期貨類型 |  |
| 4 | `futures_id` | VARCHAR(255) | 期貨代碼 | ✔ |
| 5 | `futures_name` | VARCHAR(255) | 期貨名稱 |  |
| 6 | `settlement_price` | NUMERIC(20,6) | 最後結算價 |  |
| 7 | `underlying_code` | VARCHAR(255) | 標的代碼 |  |
| 8 | `notional_value` | NUMERIC(20,6) | 名目價值 |  |

### `TaiwanFuturesInstitutionalInvestors`  (11 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['futures_id', 'date', 'institutional_investors']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `futures_id` | VARCHAR(255) | 期貨代碼 | ✔ |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `institutional_investors` | VARCHAR(255) | 法人別 | ✔ |
| 4 | `long_deal_volume` | NUMERIC(20,6) | 多方成交量 |  |
| 5 | `long_deal_amount` | NUMERIC(20,6) | 多方成交金額 |  |
| 6 | `short_deal_volume` | NUMERIC(20,6) | 空方成交量 |  |
| 7 | `short_deal_amount` | NUMERIC(20,6) | 空方成交金額 |  |
| 8 | `long_open_interest_balance_volume` | NUMERIC(20,6) | 多方未平倉量 |  |
| 9 | `long_open_interest_balance_amount` | NUMERIC(20,6) | 多方未平倉金額 |  |
| 10 | `short_open_interest_balance_volume` | NUMERIC(20,6) | 空方未平倉量 |  |
| 11 | `short_open_interest_balance_amount` | NUMERIC(20,6) | 空方未平倉金額 |  |

### `TaiwanFuturesInstitutionalInvestorsAfterHours`  (7 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['futures_id', 'date', 'institutional_investors']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `futures_id` | VARCHAR(255) | 期貨代碼 | ✔ |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `institutional_investors` | VARCHAR(255) | 法人別 | ✔ |
| 4 | `long_deal_volume` | NUMERIC(20,6) | 多方成交量 |  |
| 5 | `long_deal_amount` | NUMERIC(20,6) | 多方成交金額 |  |
| 6 | `short_deal_volume` | NUMERIC(20,6) | 空方成交量 |  |
| 7 | `short_deal_amount` | NUMERIC(20,6) | 空方成交金額 |  |

### `TaiwanFuturesOpenInterestLargeTraders`  (21 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['futures_id', 'date', 'name', 'contract_type']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `name` | VARCHAR(255) | 商品名稱 | ✔ |
| 2 | `contract_type` | VARCHAR(255) | 契約型態 | ✔ |
| 3 | `buy_top5_trader_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 4 | `buy_top5_trader_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 5 | `buy_top10_trader_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 6 | `buy_top10_trader_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 7 | `sell_top5_trader_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 8 | `sell_top5_trader_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 9 | `sell_top10_trader_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 10 | `sell_top10_trader_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 11 | `market_open_interest` | NUMERIC(20,6) | 市場未平倉量 |  |
| 12 | `buy_top5_specific_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 13 | `buy_top5_specific_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 14 | `buy_top10_specific_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 15 | `buy_top10_specific_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 16 | `sell_top5_specific_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 17 | `sell_top5_specific_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 18 | `sell_top10_specific_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 19 | `sell_top10_specific_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 20 | `date` | DATE | 日期 | ✔ |
| 21 | `futures_id` | VARCHAR(255) | 期貨代碼 | ✔ |

### `TaiwanFuturesSpreadTick`  (9 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['contract_date', 'date', 'time', 'far_price', 'futures_id', 'near_price', 'price', 'spread_to_spread', 'volume']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `contract_date` | VARCHAR(255) | 契約月份 | ✔ |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `time` | VARCHAR(255) | (文件未列) | ✔ |
| 4 | `far_price` | NUMERIC(20,6) | (文件未列) | ✔ |
| 5 | `futures_id` | VARCHAR(255) | 期貨代碼 | ✔ |
| 6 | `near_price` | NUMERIC(20,6) | (文件未列) | ✔ |
| 7 | `price` | NUMERIC(20,6) | 價格 | ✔ |
| 8 | `spread_to_spread` | NUMERIC(20,6) | (文件未列) | ✔ |
| 9 | `volume` | NUMERIC(20,6) | 成交量 | ✔ |

### `TaiwanFuturesSpreadTrading`  (14 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'futures_id', 'contract_date', 'open', 'max', 'min', 'close', 'best_bid', 'best_ask', 'historical_max', 'historical_min', 'spread_to_spread_volume', 'spread_to_single_volume', 'trading_session']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `futures_id` | VARCHAR(255) | 期貨代碼 | ✔ |
| 3 | `contract_date` | VARCHAR(255) | 契約月份 | ✔ |
| 4 | `open` | NUMERIC(20,6) | 開盤價 | ✔ |
| 5 | `max` | NUMERIC(20,6) | 最高價 | ✔ |
| 6 | `min` | NUMERIC(20,6) | 最低價 | ✔ |
| 7 | `close` | NUMERIC(20,6) | 收盤價 | ✔ |
| 8 | `best_bid` | NUMERIC(20,6) | 最佳買價 | ✔ |
| 9 | `best_ask` | NUMERIC(20,6) | 最佳賣價 | ✔ |
| 10 | `historical_max` | NUMERIC(20,6) | 歷史最高價 | ✔ |
| 11 | `historical_min` | NUMERIC(20,6) | 歷史最低價 | ✔ |
| 12 | `spread_to_spread_volume` | NUMERIC(20,6) | 價差對價差成交量 | ✔ |
| 13 | `spread_to_single_volume` | NUMERIC(20,6) | 價差對單口成交量 | ✔ |
| 14 | `trading_session` | VARCHAR(255) | 交易時段 | ✔ |

### `TaiwanOptionDaily`  (13 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'option_id', 'contract_date', 'strike_price', 'call_put', 'open', 'max', 'min', 'close', 'volume', 'settlement_price', 'open_interest', 'trading_session']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `option_id` | VARCHAR(255) | 選擇權代碼 | ✔ |
| 3 | `contract_date` | VARCHAR(255) | 契約月份 | ✔ |
| 4 | `strike_price` | NUMERIC(20,6) | 履約價格 | ✔ |
| 5 | `call_put` | VARCHAR(255) | 買賣權別 | ✔ |
| 6 | `open` | NUMERIC(20,6) | 開盤價 | ✔ |
| 7 | `max` | NUMERIC(20,6) | 最高價 | ✔ |
| 8 | `min` | NUMERIC(20,6) | 最低價 | ✔ |
| 9 | `close` | NUMERIC(20,6) | 收盤價 | ✔ |
| 10 | `volume` | NUMERIC(20,6) | 成交量 | ✔ |
| 11 | `settlement_price` | NUMERIC(20,6) | 結算價 | ✔ |
| 12 | `open_interest` | NUMERIC(20,6) | 未平倉量 | ✔ |
| 13 | `trading_session` | VARCHAR(255) | 交易時段 | ✔ |

### `TaiwanOptionDealerTradingVolumeDaily`  (6 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'dealer_code', 'dealer_name', 'option_id', 'volume', 'is_after_hour']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `dealer_code` | VARCHAR(255) | 期貨商代號 | ✔ |
| 3 | `dealer_name` | VARCHAR(255) | 期貨商名稱 | ✔ |
| 4 | `option_id` | VARCHAR(255) | 選擇權代碼 | ✔ |
| 5 | `volume` | NUMERIC(20,6) | 成交量 | ✔ |
| 6 | `is_after_hour` | VARCHAR(255) | 是否夜盤 | ✔ |

### `TaiwanOptionFinalSettlementPrice`  (8 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['option_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `contract_month` | VARCHAR(255) | 契約月份 |  |
| 3 | `option_type` | VARCHAR(255) | 選擇權類型 |  |
| 4 | `option_id` | VARCHAR(255) | 選擇權代碼 | ✔ |
| 5 | `option_name` | VARCHAR(255) | 選擇權名稱 |  |
| 6 | `settlement_price` | NUMERIC(20,6) | 最後結算價 |  |
| 7 | `underlying_code` | VARCHAR(255) | 標的代碼 |  |
| 8 | `notional_value` | NUMERIC(20,6) | 名目價值 |  |

### `TaiwanOptionInstitutionalInvestors`  (12 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['option_id', 'date', 'institutional_investors', 'call_put']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `option_id` | VARCHAR(255) | 選擇權代碼 | ✔ |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `call_put` | VARCHAR(255) | 買賣權別 | ✔ |
| 4 | `institutional_investors` | VARCHAR(255) | 法人別 | ✔ |
| 5 | `long_deal_volume` | NUMERIC(20,6) | 多方成交量 |  |
| 6 | `long_deal_amount` | NUMERIC(20,6) | 多方成交金額 |  |
| 7 | `short_deal_volume` | NUMERIC(20,6) | 空方成交量 |  |
| 8 | `short_deal_amount` | NUMERIC(20,6) | 空方成交金額 |  |
| 9 | `long_open_interest_balance_volume` | NUMERIC(20,6) | 多方未平倉量 |  |
| 10 | `long_open_interest_balance_amount` | NUMERIC(20,6) | 多方未平倉金額 |  |
| 11 | `short_open_interest_balance_volume` | NUMERIC(20,6) | 空方未平倉量 |  |
| 12 | `short_open_interest_balance_amount` | NUMERIC(20,6) | 空方未平倉金額 |  |

### `TaiwanOptionInstitutionalInvestorsAfterHours`  (8 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['option_id', 'date', 'institutional_investors', 'call_put']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `option_id` | VARCHAR(255) | 選擇權代碼 | ✔ |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `call_put` | VARCHAR(255) | 買賣權別 | ✔ |
| 4 | `institutional_investors` | VARCHAR(255) | 法人別 | ✔ |
| 5 | `long_deal_volume` | NUMERIC(20,6) | 多方成交量 |  |
| 6 | `long_deal_amount` | NUMERIC(20,6) | 多方成交金額 |  |
| 7 | `short_deal_volume` | NUMERIC(20,6) | 空方成交量 |  |
| 8 | `short_deal_amount` | NUMERIC(20,6) | 空方成交金額 |  |

### `TaiwanOptionOpenInterestLargeTraders`  (22 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['option_id', 'date', 'name', 'contract_type', 'put_call']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `contract_type` | VARCHAR(255) | 契約型態 | ✔ |
| 2 | `buy_top5_trader_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 3 | `buy_top5_trader_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 4 | `buy_top10_trader_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 5 | `buy_top10_trader_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 6 | `sell_top5_trader_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 7 | `sell_top5_trader_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 8 | `sell_top10_trader_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 9 | `sell_top10_trader_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 10 | `market_open_interest` | NUMERIC(20,6) | 市場未平倉量 |  |
| 11 | `buy_top5_specific_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 12 | `buy_top5_specific_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 13 | `buy_top10_specific_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 14 | `buy_top10_specific_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 15 | `sell_top5_specific_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 16 | `sell_top5_specific_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 17 | `sell_top10_specific_open_interest` | NUMERIC(20,6) | (文件未列) |  |
| 18 | `sell_top10_specific_open_interest_per` | NUMERIC(20,6) | (文件未列) |  |
| 19 | `date` | DATE | 日期 | ✔ |
| 20 | `put_call` | VARCHAR(255) | 買賣權別 | ✔ |
| 21 | `name` | VARCHAR(255) | 商品名稱 | ✔ |
| 22 | `option_id` | VARCHAR(255) | 選擇權代碼 | ✔ |

### `TaiwanTotalExchangeMarginMaintenance`  (2 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `TotalExchangeMarginMaintenance` | NUMERIC(20,6) | 大盤融資維持率 |  |


## F. 國際股市(非台股)

### `EuropeStockInfo`  (4 欄)
- 取樣 mode：2nd:{}；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `Market` | VARCHAR(255) | 市場別 |  |
| 4 | `stock_name` | VARCHAR(255) | 股票名稱 |  |

### `EuropeStockPrice`  (8 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `Adj_Close` | NUMERIC(20,6) | 調整後收盤價 |  |
| 4 | `Close` | NUMERIC(20,6) | 收盤價 |  |
| 5 | `High` | NUMERIC(20,6) | 最高價 |  |
| 6 | `Low` | NUMERIC(20,6) | 最低價 |  |
| 7 | `Open` | NUMERIC(20,6) | 開盤價 |  |
| 8 | `Volume` | NUMERIC(20,6) | 成交量 |  |

### `JapanStockInfo`  (5 欄)
- 取樣 mode：2nd:{}；PK：`['date', 'stock_id', 'Exchange', 'stock_name']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `Exchange` | VARCHAR(255) | 交易所 | ✔ |
| 4 | `Sector` | VARCHAR(255) | 產業別 |  |
| 5 | `stock_name` | VARCHAR(255) | 股票名稱 | ✔ |

### `JapanStockPrice`  (8 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `Adj_Close` | NUMERIC(20,6) | 調整後收盤價 |  |
| 4 | `Close` | NUMERIC(20,6) | 收盤價 |  |
| 5 | `High` | NUMERIC(20,6) | 最高價 |  |
| 6 | `Low` | NUMERIC(20,6) | 最低價 |  |
| 7 | `Open` | NUMERIC(20,6) | 開盤價 |  |
| 8 | `Volume` | NUMERIC(20,6) | 成交量 |  |

### `UKStockInfo`  (4 欄)
- 取樣 mode：2nd:{}；PK：`['date', 'stock_id', 'Country', 'stock_name']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `Country` | VARCHAR(255) | 國家 | ✔ |
| 4 | `stock_name` | VARCHAR(255) | 股票名稱 | ✔ |

### `UKStockPrice`  (8 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `Adj_Close` | NUMERIC(20,6) | 調整後收盤價 |  |
| 4 | `Close` | NUMERIC(20,6) | 收盤價 |  |
| 5 | `High` | NUMERIC(20,6) | 最高價 |  |
| 6 | `Low` | NUMERIC(20,6) | 最低價 |  |
| 7 | `Open` | NUMERIC(20,6) | 開盤價 |  |
| 8 | `Volume` | NUMERIC(20,6) | 成交量 |  |

### `USStockInfo`  (7 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['stock_id', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 | ✔ |
| 3 | `Country` | VARCHAR(255) | 國家 |  |
| 4 | `IPOYear` | NUMERIC(20,6) | IPO年份 |  |
| 5 | `MarketCap` | NUMERIC(21,6) | 市值 |  |
| 6 | `Subsector` | VARCHAR(255) | 次產業別 |  |
| 7 | `stock_name` | VARCHAR(255) | 股票名稱 |  |

### `USStockPrice`  (8 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date', 'Adj_Close', 'Close', 'High', 'Low', 'Open', 'Volume']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `stock_id` | VARCHAR(255) | 股票代碼 |  |
| 3 | `Adj_Close` | NUMERIC(20,6) | 調整後收盤價 | ✔ |
| 4 | `Close` | NUMERIC(20,6) | 收盤價 | ✔ |
| 5 | `High` | NUMERIC(20,6) | 最高價 | ✔ |
| 6 | `Low` | NUMERIC(20,6) | 最低價 | ✔ |
| 7 | `Open` | NUMERIC(20,6) | 開盤價 | ✔ |
| 8 | `Volume` | NUMERIC(21,6) | 成交量 | ✔ |


## G. 全球商品/總經

### `CnnFearGreedIndex`  (3 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `fear_greed` | NUMERIC(20,6) | 恐懼與貪婪指數數值 |  |
| 3 | `fear_greed_emotion` | VARCHAR(255) | 恐懼與貪婪指數情緒 |  |

### `CrudeOilPrices`  (3 欄)
- 取樣 mode：2nd:{'start_date': '2026-05-01'}；PK：`['date', 'name']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `date` | DATE | 日期 | ✔ |
| 2 | `name` | VARCHAR(255) | 油品名稱 | ✔ |
| 3 | `price` | NUMERIC(20,6) | 原油價格 |  |

### `GoldPrice`  (2 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `Price` | NUMERIC(20,6) | 黃金價格 |  |
| 2 | `date` | VARCHAR(255) | 日期 | ✔ |

### `InterestRate`  (4 欄)
- 取樣 mode：by-date(單日,無id)；PK：`['country', 'date']`

| # | 欄位(API 原樣大小寫) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `country` | VARCHAR(255) | 國家 | ✔ |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `full_country_name` | VARCHAR(255) | 完整國家名稱 |  |
| 4 | `interest_rate` | NUMERIC(20,6) | 央行利率 |  |


## H. FRED 總經(`fred_series` 表，全 series 共用一表)

- 取樣 series：T10Y2Y；PK：`['series_id', 'date']`；型別經 `generic_schema` 推導

| # | 欄位(API) | 型別/大小 | 中文 | PK |
|---|---|---|---|---|
| 1 | `series_id` | VARCHAR(255) | FRED series 代碼 | ✔ |
| 2 | `date` | DATE | 日期 | ✔ |
| 3 | `value` | NUMERIC(20,6) | 數值 |  |


## 附：live 未取樣 dataset(需特定參數/區間，docs 有欄位但本輪 live 取樣未命中)

| dataset | 類別 | docs 欄數 | 備註 |
|---|---|---|---|
| `ExchangeRate` | G. 全球商品/總經 | 2 | 三策略+廣域id 皆空 |
| `GovernmentBondsYield` | G. 全球商品/總經 | 3 | 三策略+廣域id 皆空 |

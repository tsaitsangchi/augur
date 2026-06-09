# Augur — FinMind + FRED 通用 ingester 資料表 Schema 完整目錄

**產生日期**：2026-06-09（同日二輪 live re-probe + 取樣建表驗證更新）　**驗證方式**：live API 逐一 probe（§一.9 / 北極星：每欄型別皆自真實 API 回應推導，無幻像）；**85 表已於乾淨隔離之 augur db 取樣建表驗證（0 失敗，見末節）**

**治權對齊**：#2 表名/欄位/大小寫逐字照 API｜#4 intraday 排除｜#5 字串 `VARCHAR(255)`(>255→`TEXT`)、數字 `NUMERIC(20,6)`(超出自動擴大)｜#1 中文說明僅 `origin_name` 為 API 來源，其餘標『人工描述』

> **型別說明**：表列型別為 augur generic_schema **初始建表型別**（依樣本值類別判定）；實際 ingest 時依整批資料 **auto-widen**（字串超 255→TEXT、數字超 (20,6)→擴大），主鍵首建固定。


## 〇、總覽

- FinMind dataset 總數（live 422 enum）：**92**
- 分組：A 台股/總經 **55**｜B 期權期貨 **16**｜C 非台股 **13**｜D intraday(排除) **8**
- **以「日為最小單位」(#4) 為標準 → 通用 ingester 建表 = A+B+C 日頻 84 張 FinMind 表 + FRED 1 張 = 共 85 張**（A 台股/總經 + B 期權期貨 + C 非台股，**皆日交易、皆可納入**）
- 唯一排除：intraday 8 張（5秒/tick/分K/分鐘）— **#4 守門拒絕、不建表、不列入**
- **建表範圍 ⊇ 預測標的**：上述 85 張為 generic 可建之**原始/特徵來源**；augur **預測標的**＝台灣上市櫃個股（第一部）。B/C（29 張）以**特徵/情境輸入**納入（如期貨未平倉、美股/日股 macro），本身非預測對象
- live probe：**A/B/C 日頻表才是「通用 ingester 建的 table」並已建 schema**；**D 群 intraday 經 probe 確認皆 sub-daily（5秒/tick/分K）→ 依 #4 守門排除、不建表、不列 schema**；僅 2 張（`ExchangeRate` 全球匯率 / `GovernmentBondsYield` 公債殖利率）任何 data_id 皆回 200-空，疑 **sponsor tier 不含**（非 augur 台股標的，總經已由 FRED 涵蓋）
- FRED（api.stlouisfed.org）：1 張觀測表 `fred_series`，欄位 `series_id, date, value`（+ realtime 區間）
- **infra log 表（explicit DDL，非 generic）**：`pipeline_execution_log` + `data_audit_log` 2 張（系統運維表，非 API 推導，憲章 PHASE 1 bootstrap；schema 見末節）
- **★ 全表總計 ＝ 84 FinMind 日頻 + 1 FRED + 2 log ＝ 共 87 張**；其中 sponsor tier 暫無資料之 2 張（global `ExchangeRate` / `GovernmentBondsYield`，回 200-空）未建 → **實建 85**
- **建表驗證（2026-06-09，clean-room #16）**：於清空並隔離之 `augur` db（非 stock_backend 的 `stock` db）逐表 generic 取樣建表 → **85 表建成 / 0 失敗 / 取樣總列數 2,181,069**；`data_audit_log` 留痕正常。證明「看 API→推型別→建表→冪等 upsert→稽核留痕」端到端可運作。**此為取樣驗證（近期窗），非全史；全市場全史 sync 為後續另一步**（詳見末節）


---

## A. 台股 / 總經（augur 預測標的 + 日頻 feature 來源）（55 個）


### `TaiwanStockGovernmentBankBuySell`　八大行庫買賣超
- 取樣參數：`{'start_date': '2026-06-05'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `buy_amount` | NUMERIC(20,6) | 買進金額 |
| 4 | `sell_amount` | NUMERIC(20,6) | 賣出金額 |
| 5 | `buy` | NUMERIC(20,6) | 買進 |
| 6 | `sell` | NUMERIC(20,6) | 賣出 |
| 7 | `bank_name` | VARCHAR(255) | 行庫名稱 |

### `TaiwanStockBlockTradingDailyReport`　鉅額交易日報(分點)
- 取樣參數：`{'start_date': '2026-06-05'}`｜推定主鍵：`stock_id, securities_trader_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `securities_trader` | VARCHAR(255) | 券商名稱 |
| 2 | `price` | NUMERIC(20,6) | 價格 |
| 3 | `buy` | NUMERIC(20,6) | 買進 |
| 4 | `sell` | NUMERIC(20,6) | 賣出 |
| 5 | `trade_type` | VARCHAR(255) | 交易類別 |
| 6 | `securities_trader_id` | VARCHAR(255) | 券商代號 |
| 7 | `stock_id` | VARCHAR(255) | 股票代號 |
| 8 | `date` | DATE | 日期 |

### `TaiwanStockTradingDailyReport`　券商分點進出日報
- 取樣參數：`{'data_id': '2330', 'start_date': '2026-05-20'}`｜推定主鍵：`stock_id, securities_trader_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `securities_trader` | VARCHAR(255) | 券商名稱 |
| 2 | `price` | NUMERIC(20,6) | 價格 |
| 3 | `buy` | NUMERIC(20,6) | 買進 |
| 4 | `sell` | NUMERIC(20,6) | 賣出 |
| 5 | `securities_trader_id` | VARCHAR(255) | 券商代號 |
| 6 | `stock_id` | VARCHAR(255) | 股票代號 |
| 7 | `date` | DATE | 日期 |

### `TaiwanStockWarrantTradingDailyReport`　權證每日交易(分點)
- 取樣參數：`{'data_id': '030012', 'start_date': '2026-06-05'}`｜推定主鍵：`stock_id, securities_trader_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `securities_trader` | VARCHAR(255) | 券商名稱 |
| 2 | `price` | NUMERIC(20,6) | 價格 |
| 3 | `buy` | NUMERIC(20,6) | 買進 |
| 4 | `sell` | NUMERIC(20,6) | 賣出 |
| 5 | `securities_trader_id` | VARCHAR(255) | 券商代號 |
| 6 | `stock_id` | VARCHAR(255) | 股票代號 |
| 7 | `date` | DATE | 日期 |

### `TaiwanStockBalanceSheet`　資產負債表(長格式)
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, type`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `type` | VARCHAR(255) | 類別/科目代碼 |
| 4 | `value` | NUMERIC(20,6) | 數值 |
| 5 | `origin_name` | VARCHAR(255) | 科目中文名(API 來源) |

### `TaiwanDailyShortSaleBalances`　融券+借券賣出餘額
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代號 |
| 2 | `MarginShortSalesPreviousDayBalance` | NUMERIC(20,6) | 融券前日餘額 |
| 3 | `MarginShortSalesShortSales` | NUMERIC(20,6) | 融券賣出 |
| 4 | `MarginShortSalesShortCovering` | NUMERIC(20,6) | 融券買進回補 |
| 5 | `MarginShortSalesStockRedemption` | NUMERIC(20,6) | 融券現券償還 |
| 6 | `MarginShortSalesCurrentDayBalance` | NUMERIC(20,6) | 融券今日餘額 |
| 7 | `MarginShortSalesQuota` | NUMERIC(20,6) | 融券限額 |
| 8 | `SBLShortSalesPreviousDayBalance` | NUMERIC(20,6) | 借券賣出前日餘額 |
| 9 | `SBLShortSalesShortSales` | NUMERIC(20,6) | 借券賣出 |
| 10 | `SBLShortSalesReturns` | NUMERIC(20,6) | 借券賣出返還 |
| 11 | `SBLShortSalesAdjustments` | NUMERIC(20,6) | 借券賣出調整 |
| 12 | `SBLShortSalesCurrentDayBalance` | NUMERIC(20,6) | 借券賣出今日餘額 |
| 13 | `SBLShortSalesQuota` | NUMERIC(20,6) | 借券賣出限額 |
| 14 | `SBLShortSalesShortCovering` | NUMERIC(20,6) | 借券賣出回補 |
| 15 | `date` | DATE | 日期 |

### `TaiwanStockFinancialStatements`　綜合損益表(長格式)
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, type`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `type` | VARCHAR(255) | 類別/科目代碼 |
| 4 | `value` | NUMERIC(20,6) | 數值 |
| 5 | `origin_name` | VARCHAR(255) | 科目中文名(API 來源) |

### `TaiwanStockInstitutionalInvestorsBuySell`　個股三大法人買賣超
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, name`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `buy` | NUMERIC(20,6) | 買進 |
| 4 | `name` | VARCHAR(255) | 名稱/法人別 |
| 5 | `sell` | NUMERIC(20,6) | 賣出 |

### `TaiwanStockTotalInstitutionalInvestors`　全市場三大法人買賣超
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`date, name`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `buy` | NUMERIC(20,6) | 買進 |
| 2 | `date` | DATE | 日期 |
| 3 | `name` | VARCHAR(255) | 名稱/法人別 |
| 4 | `sell` | NUMERIC(20,6) | 賣出 |

### `TaiwanStockShareholding`　外資持股
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |
| 4 | `InternationalCode` | VARCHAR(255) | 國際證券辨識碼(ISIN) |
| 5 | `ForeignInvestmentRemainingShares` | NUMERIC(20,6) | 外資尚可投資股數 |
| 6 | `ForeignInvestmentShares` | NUMERIC(20,6) | 外資持有股數 |
| 7 | `ForeignInvestmentRemainRatio` | NUMERIC(20,6) | 外資尚可投資比率 |
| 8 | `ForeignInvestmentSharesRatio` | NUMERIC(20,6) | 外資持股比率 |
| 9 | `ForeignInvestmentUpperLimitRatio` | NUMERIC(20,6) | 外資投資上限比率 |
| 10 | `ChineseInvestmentUpperLimitRatio` | NUMERIC(20,6) | 陸資投資上限比率 |
| 11 | `NumberOfSharesIssued` | NUMERIC(20,6) | 已發行股數 |
| 12 | `RecentlyDeclareDate` | DATE | 最近申報日 |
| 13 | `note` | VARCHAR(255) | 備註 |

### `TaiwanStockPER`　本益比/股價淨值比/殖利率
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `dividend_yield` | NUMERIC(20,6) | 殖利率(%) |
| 4 | `PER` | NUMERIC(20,6) | 本益比 |
| 5 | `PBR` | NUMERIC(20,6) | 股價淨值比 |

### `TaiwanStockPrice`　台股日成交價量
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `Trading_Volume` | NUMERIC(20,6) | 成交股數 |
| 4 | `Trading_money` | NUMERIC(20,6) | 成交金額 |
| 5 | `open` | NUMERIC(20,6) | 開盤價 |
| 6 | `max` | NUMERIC(20,6) | 最高價 |
| 7 | `min` | NUMERIC(20,6) | 最低價 |
| 8 | `close` | NUMERIC(20,6) | 收盤價 |
| 9 | `spread` | NUMERIC(20,6) | 漲跌價差 |
| 10 | `Trading_turnover` | NUMERIC(20,6) | 成交筆數 |

### `TaiwanStockPriceAdj`　台股日成交價量(還原權值)
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `Trading_Volume` | NUMERIC(20,6) | 成交股數 |
| 4 | `Trading_money` | NUMERIC(20,6) | 成交金額 |
| 5 | `open` | NUMERIC(20,6) | 開盤價 |
| 6 | `max` | NUMERIC(20,6) | 最高價 |
| 7 | `min` | NUMERIC(20,6) | 最低價 |
| 8 | `close` | NUMERIC(20,6) | 收盤價 |
| 9 | `spread` | NUMERIC(20,6) | 漲跌價差 |
| 10 | `Trading_turnover` | NUMERIC(20,6) | 成交筆數 |

### `TaiwanStockCashFlowsStatement`　現金流量表(長格式)
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, type`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `type` | VARCHAR(255) | 類別/科目代碼 |
| 4 | `value` | NUMERIC(20,6) | 數值 |
| 5 | `origin_name` | VARCHAR(255) | 科目中文名(API 來源) |

### `TaiwanStockMonthRevenue`　月營收
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `country` | VARCHAR(255) | 國家代碼 |
| 4 | `revenue` | NUMERIC(20,6) | 營收 |
| 5 | `revenue_month` | NUMERIC(20,6) | 營收月份 |
| 6 | `revenue_year` | NUMERIC(20,6) | 營收年度 |
| 7 | `create_time` | DATE | 建立時間 |

### `TaiwanStockMarginPurchaseShortSale`　個股融資融券
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `MarginPurchaseBuy` | NUMERIC(20,6) | 融資買進 |
| 4 | `MarginPurchaseCashRepayment` | NUMERIC(20,6) | 融資現金償還 |
| 5 | `MarginPurchaseLimit` | NUMERIC(20,6) | 融資限額 |
| 6 | `MarginPurchaseSell` | NUMERIC(20,6) | 融資賣出 |
| 7 | `MarginPurchaseTodayBalance` | NUMERIC(20,6) | 融資今日餘額 |
| 8 | `MarginPurchaseYesterdayBalance` | NUMERIC(20,6) | 融資前日餘額 |
| 9 | `Note` | VARCHAR(255) | 備註 |
| 10 | `OffsetLoanAndShort` | NUMERIC(20,6) | 資券相抵 |
| 11 | `ShortSaleBuy` | NUMERIC(20,6) | 融券買進(回補) |
| 12 | `ShortSaleCashRepayment` | NUMERIC(20,6) | 融券現金償還 |
| 13 | `ShortSaleLimit` | NUMERIC(20,6) | 融券限額 |
| 14 | `ShortSaleSell` | NUMERIC(20,6) | 融券賣出 |
| 15 | `ShortSaleTodayBalance` | NUMERIC(20,6) | 融券今日餘額 |
| 16 | `ShortSaleYesterdayBalance` | NUMERIC(20,6) | 融券前日餘額 |

### `CnnFearGreedIndex`　CNN 恐懼貪婪指數
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `fear_greed` | NUMERIC(20,6) | 恐懼貪婪指數 |
| 3 | `fear_greed_emotion` | VARCHAR(255) | 情緒分類 |

### `TaiwanExchangeRate`　台銀牌告匯率
- 取樣參數：`{'data_id': 'USD', 'start_date': '2024-01-01'}`｜推定主鍵：`date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `currency` | VARCHAR(255) | 幣別 |
| 3 | `cash_buy` | NUMERIC(20,6) | 現金買入 |
| 4 | `cash_sell` | NUMERIC(20,6) | 現金賣出 |
| 5 | `spot_buy` | NUMERIC(20,6) | 即期買入 |
| 6 | `spot_sell` | NUMERIC(20,6) | 即期賣出 |

### `TaiwanStockNews`　個股新聞
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | TIMESTAMP | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `link` | TEXT | 連結 |
| 4 | `source` | VARCHAR(255) | 來源 |
| 5 | `title` | VARCHAR(255) | 標題 |

### `TaiwanStockDividendResult`　除權息結果
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `before_price` | NUMERIC(20,6) | 除權息前價 |
| 4 | `after_price` | NUMERIC(20,6) | 除權息後參考價 |
| 5 | `stock_and_cache_dividend` | NUMERIC(20,6) | 股票+現金股利 |
| 6 | `stock_or_cache_dividend` | VARCHAR(255) | 股票或現金股利 |
| 7 | `max_price` | NUMERIC(20,6) | 漲停價 |
| 8 | `min_price` | NUMERIC(20,6) | 跌停價 |
| 9 | `open_price` | NUMERIC(20,6) | 開盤參考價 |
| 10 | `reference_price` | NUMERIC(20,6) | 參考價 |

### `TaiwanStockInfo`　股票基本資訊(名冊)
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, type`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `industry_category` | VARCHAR(255) | 產業類別 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |
| 4 | `type` | VARCHAR(255) | 類別/科目代碼 |
| 5 | `date` | DATE | 日期 |

### `TaiwanSecuritiesTraderInfo`　證券商基本資訊
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`securities_trader_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `securities_trader_id` | VARCHAR(255) | 券商代號 |
| 2 | `securities_trader` | VARCHAR(255) | 券商名稱 |
| 3 | `date` | VARCHAR(255) | 日期 |
| 4 | `address` | VARCHAR(255) | 地址 |
| 5 | `phone` | VARCHAR(255) | 電話 |

### `TaiwanStockInfoWithWarrant`　股票基本資訊(含權證)
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, type`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `industry_category` | VARCHAR(255) | 產業類別 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |
| 4 | `type` | VARCHAR(255) | 類別/科目代碼 |
| 5 | `date` | DATE | 日期 |

### `TaiwanStockSecuritiesLending`　借券成交明細
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, transaction_type`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `transaction_type` | VARCHAR(255) | 交易別 |
| 4 | `volume` | NUMERIC(20,6) | 成交量/股數 |
| 5 | `fee_rate` | NUMERIC(20,6) | 費率(%) |
| 6 | `close` | NUMERIC(20,6) | 收盤價 |
| 7 | `original_return_date` | DATE | 原約定還券日 |
| 8 | `original_lending_period` | NUMERIC(20,6) | 原約定借券期間 |

### `TaiwanStockHoldingSharesPer`　集保戶股權分散(持股級距)
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, HoldingSharesLevel`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `HoldingSharesLevel` | VARCHAR(255) | 持股級距 |
| 4 | `people` | NUMERIC(20,6) | 人數 |
| 5 | `percent` | NUMERIC(20,6) | 佔集保比率(%) |
| 6 | `unit` | NUMERIC(20,6) | 單位 |

### `TaiwanStockDividend`　股利政策(宣告)
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, year`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `year` | VARCHAR(255) | 年度 |
| 4 | `StockEarningsDistribution` | NUMERIC(20,6) | 盈餘配股 |
| 5 | `StockStatutorySurplus` | NUMERIC(20,6) | 法定盈餘公積配股 |
| 6 | `StockExDividendTradingDate` | VARCHAR(255) | 除權交易日 |
| 7 | `TotalEmployeeStockDividend` | NUMERIC(20,6) | 員工配股總額 |
| 8 | `TotalEmployeeStockDividendAmount` | NUMERIC(20,6) | 員工配股金額 |
| 9 | `RatioOfEmployeeStockDividendOfTotal` | NUMERIC(20,6) | 員工配股占比 |
| 10 | `RatioOfEmployeeStockDividend` | NUMERIC(20,6) | 員工配股比率 |
| 11 | `CashEarningsDistribution` | NUMERIC(20,6) | 盈餘配息 |
| 12 | `CashStatutorySurplus` | NUMERIC(20,6) | 法定盈餘公積配息 |
| 13 | `CashExDividendTradingDate` | DATE | 除息交易日 |
| 14 | `CashDividendPaymentDate` | DATE | 現金股利發放日 |
| 15 | `TotalEmployeeCashDividend` | NUMERIC(20,6) | 員工現金股利總額 |
| 16 | `TotalNumberOfCashCapitalIncrease` | NUMERIC(20,6) | 現金增資總股數 |
| 17 | `CashIncreaseSubscriptionRate` | NUMERIC(20,6) | 現增認股率 |
| 18 | `CashIncreaseSubscriptionpRrice` | NUMERIC(20,6) | 現增認購價 |
| 19 | `RemunerationOfDirectorsAndSupervisors` | NUMERIC(20,6) | 董監酬勞 |
| 20 | `ParticipateDistributionOfTotalShares` | NUMERIC(20,6) | 參與分配總股數 |
| 21 | `AnnouncementDate` | DATE | 公告日期 |
| 22 | `AnnouncementTime` | VARCHAR(255) | 公告時間 |

### `TaiwanStockTotalMarginPurchaseShortSale`　全市場融資融券
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`date, name`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `TodayBalance` | NUMERIC(20,6) | 今日餘額 |
| 2 | `YesBalance` | NUMERIC(20,6) | 前日餘額 |
| 3 | `buy` | NUMERIC(20,6) | 買進 |
| 4 | `date` | DATE | 日期 |
| 5 | `name` | VARCHAR(255) | 名稱/法人別 |
| 6 | `Return` | NUMERIC(20,6) | 現券償還 |
| 7 | `sell` | NUMERIC(20,6) | 賣出 |

### `TaiwanStockDayTrading`　個股當沖
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代號 |
| 2 | `date` | DATE | 日期 |
| 3 | `BuyAfterSale` | VARCHAR(255) | 先買後賣 |
| 4 | `Volume` | NUMERIC(20,6) | 成交量 |
| 5 | `BuyAmount` | NUMERIC(20,6) | 買進金額 |
| 6 | `SellAmount` | NUMERIC(20,6) | 賣出金額 |

### `TaiwanStockCapitalReductionReferencePrice`　減資參考價
- 取樣參數：`{'data_id': '2603', 'start_date': '2010-01-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `ClosingPriceonTheLastTradingDay` | NUMERIC(20,6) | 減資前最後交易日收盤價 |
| 4 | `PostReductionReferencePrice` | NUMERIC(20,6) | 減資後參考價 |
| 5 | `LimitUp` | NUMERIC(20,6) | 漲停價 |
| 6 | `LimitDown` | NUMERIC(20,6) | 跌停價 |
| 7 | `OpeningReferencePrice` | NUMERIC(20,6) | 開盤參考價 |
| 8 | `ExrightReferencePrice` | NUMERIC(20,6) | 除權參考價 |
| 9 | `ReasonforCapitalReduction` | VARCHAR(255) | 減資原因 |

### `TaiwanStockTotalReturnIndex`　(中文名待補)
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TAIEX'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `price` | NUMERIC(20,6) | 價格 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `date` | DATE | 日期 |

### `TaiwanStockMarketValue`　個股市值
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `market_value` | NUMERIC(20,6) | 市值 |

### `TaiwanStock10Year`　近十年還原股價
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `close` | NUMERIC(20,6) | 收盤價 |

### `TaiwanStockDelisting`　下市
- 取樣參數：`{'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |

### `TaiwanStockConvertibleBondDaily`　可轉債日成交
- 取樣參數：`{'data_id': '11011', 'start_date': '2025-06-01'}`｜推定主鍵：`cb_id, date, transaction_type`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `cb_id` | VARCHAR(255) | 可轉債代號 |
| 2 | `cb_name` | VARCHAR(255) | 可轉債名稱 |
| 3 | `transaction_type` | VARCHAR(255) | 交易別 |
| 4 | `close` | NUMERIC(20,6) | 收盤價 |
| 5 | `change` | NUMERIC(20,6) | 漲跌 |
| 6 | `open` | NUMERIC(20,6) | 開盤價 |
| 7 | `max` | NUMERIC(20,6) | 最高價 |
| 8 | `min` | NUMERIC(20,6) | 最低價 |
| 9 | `no_of_transactions` | NUMERIC(20,6) | 成交筆數 |
| 10 | `unit` | NUMERIC(20,6) | 單位 |
| 11 | `trading_value` | NUMERIC(20,6) | 成交金額 |
| 12 | `avg_price` | NUMERIC(20,6) | 均價 |
| 13 | `next_ref_price` | NUMERIC(20,6) | 次日參考價 |
| 14 | `next_max_limit` | NUMERIC(20,6) | 次日漲停 |
| 15 | `next_min_limit` | NUMERIC(20,6) | 次日跌停 |
| 16 | `date` | DATE | 日期 |

### `TaiwanStockConvertibleBondInstitutionalInvestors`　可轉債三大法人
- 取樣參數：`{'data_id': '11011', 'start_date': '2025-06-01'}`｜推定主鍵：`cb_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `Foreign_Investor_Buy` | NUMERIC(20,6) | 外資買 |
| 2 | `Foreign_Investor_Sell` | NUMERIC(20,6) | 外資賣 |
| 3 | `Foreign_Investor_Overbuy` | NUMERIC(20,6) | 外資買超 |
| 4 | `Investment_Trust_Buy` | NUMERIC(20,6) | 投信買 |
| 5 | `Investment_Trust_Sell` | NUMERIC(20,6) | 投信賣 |
| 6 | `Investment_Trust_Overbuy` | NUMERIC(20,6) | 投信買超 |
| 7 | `Dealer_self_Buy` | NUMERIC(20,6) | 自營商買 |
| 8 | `Dealer_self_Sell` | NUMERIC(20,6) | 自營商賣 |
| 9 | `Dealer_self_Overbuy` | NUMERIC(20,6) | 自營商買超 |
| 10 | `Total_Overbuy` | NUMERIC(20,6) | 合計買超 |
| 11 | `cb_id` | VARCHAR(255) | 可轉債代號 |
| 12 | `cb_name` | VARCHAR(255) | 可轉債名稱 |
| 13 | `date` | DATE | 日期 |

### `TaiwanStockConvertibleBondDailyOverview`　可轉債每日總覽(條款)
- 取樣參數：`{'data_id': '11011', 'start_date': '2024-01-01'}`｜推定主鍵：`cb_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `cb_id` | VARCHAR(255) | 可轉債代號 |
| 2 | `cb_name` | VARCHAR(255) | 可轉債名稱 |
| 3 | `date` | DATE | 日期 |
| 4 | `InitialDateOfConversion` | DATE | 可轉換起日 |
| 5 | `DueDateOfConversion` | DATE | 可轉換迄日 |
| 6 | `InitialDateOfStopConversion` | VARCHAR(255) | 停止轉換起日 |
| 7 | `DueDateOfStopConversion` | VARCHAR(255) | 停止轉換迄日 |
| 8 | `ConversionPrice` | NUMERIC(20,6) | 轉換價 |
| 9 | `NextEffectiveDateOfConversionPrice` | DATE | 次一轉換價生效日 |
| 10 | `LatestInitialDateOfPut` | VARCHAR(255) | 最近賣回權起日 |
| 11 | `LatestDueDateOfPut` | VARCHAR(255) | 最近賣回權迄日 |
| 12 | `LatestPutPrice` | NUMERIC(20,6) | 最近賣回價 |
| 13 | `InitialDateOfEarlyRedemption` | VARCHAR(255) | 提前贖回起日 |
| 14 | `DueDateOfEarlyRedemption` | VARCHAR(255) | 提前贖回迄日 |
| 15 | `EarlyRedemptionPrice` | NUMERIC(20,6) | 提前贖回價 |
| 16 | `DateOfDelisted` | VARCHAR(255) | 下市日 |
| 17 | `IssuanceAmount` | NUMERIC(20,6) | 發行金額 |
| 18 | `OutstandingAmount` | NUMERIC(20,6) | 流通在外餘額 |
| 19 | `ReferencePrice` | NUMERIC(20,6) | 參考價 |
| 20 | `PriceOfUnderlyingStock` | NUMERIC(20,6) | 標的股價 |
| 21 | `InitialDateOfSuspension` | VARCHAR(255) | 停止交易起日 |
| 22 | `DueDateOfSuspension` | VARCHAR(255) | 停止交易迄日 |
| 23 | `CouponRate` | NUMERIC(20,6) | 票面利率 |

### `TaiwanStockConvertibleBondInfo`　可轉債基本資訊
- 取樣參數：`{'start_date': '2025-06-01'}`｜推定主鍵：`cb_id`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `cb_id` | VARCHAR(255) | 可轉債代號 |
| 2 | `cb_name` | VARCHAR(255) | 可轉債名稱 |
| 3 | `InitialDateOfConversion` | DATE | 可轉換起日 |
| 4 | `DueDateOfConversion` | DATE | 可轉換迄日 |
| 5 | `IssuanceAmount` | NUMERIC(20,6) | 發行金額 |

### `TaiwanStockMarginShortSaleSuspension`　暫停融券
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代號 |
| 2 | `date` | DATE | 日期 |
| 3 | `end_date` | DATE | 結束日 |
| 4 | `reason` | VARCHAR(255) | 原因 |

### `TaiwanTotalExchangeMarginMaintenance`　全市場整戶維持率
- 取樣參數：`{'start_date': '2025-06-01'}`｜推定主鍵：`date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `TotalExchangeMarginMaintenance` | NUMERIC(20,6) | 全市場整戶維持率(%) |

### `TaiwanStockMonthPrice`　台股月成交價
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, ymonth`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代號 |
| 2 | `ymonth` | VARCHAR(255) | 年月 |
| 3 | `max` | NUMERIC(20,6) | 最高價 |
| 4 | `min` | NUMERIC(20,6) | 最低價 |
| 5 | `trading_volume` | NUMERIC(20,6) | 成交股數 |
| 6 | `trading_money` | NUMERIC(20,6) | 成交金額 |
| 7 | `trading_turnover` | NUMERIC(20,6) | 成交筆數 |
| 8 | `date` | DATE | 日期 |
| 9 | `close` | NUMERIC(20,6) | 收盤價 |
| 10 | `open` | NUMERIC(20,6) | 開盤價 |
| 11 | `spread` | NUMERIC(20,6) | 漲跌價差 |

### `TaiwanStockWeekPrice`　台股週成交價
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, yweek`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代號 |
| 2 | `yweek` | VARCHAR(255) | 年週 |
| 3 | `max` | NUMERIC(20,6) | 最高價 |
| 4 | `min` | NUMERIC(20,6) | 最低價 |
| 5 | `trading_volume` | NUMERIC(20,6) | 成交股數 |
| 6 | `trading_money` | NUMERIC(20,6) | 成交金額 |
| 7 | `trading_turnover` | NUMERIC(20,6) | 成交筆數 |
| 8 | `date` | DATE | 日期 |
| 9 | `close` | NUMERIC(20,6) | 收盤價 |
| 10 | `open` | NUMERIC(20,6) | 開盤價 |
| 11 | `spread` | NUMERIC(20,6) | 漲跌價差 |

### `TaiwanStockMarketValueWeight`　市值權重(成分股)
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, type`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `rank` | NUMERIC(20,6) | 排名 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |
| 4 | `weight_per` | NUMERIC(20,6) | 權重(%) |
| 5 | `date` | DATE | 日期 |
| 6 | `type` | VARCHAR(255) | 類別/科目代碼 |

### `TaiwanBusinessIndicator`　台灣景氣指標(領先/同時/落後/景氣燈號)
- 取樣參數：`{'start_date': '2025-06-01'}`｜推定主鍵：`date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `leading` | NUMERIC(20,6) | 領先指標 |
| 3 | `leading_notrend` | NUMERIC(20,6) | 領先指標(去趨勢) |
| 4 | `coincident` | NUMERIC(20,6) | 同時指標 |
| 5 | `coincident_notrend` | NUMERIC(20,6) | 同時指標(去趨勢) |
| 6 | `lagging` | NUMERIC(20,6) | 落後指標 |
| 7 | `lagging_notrend` | NUMERIC(20,6) | 落後指標(去趨勢) |
| 8 | `monitoring` | NUMERIC(20,6) | 景氣對策信號(分數) |
| 9 | `monitoring_color` | VARCHAR(255) | 景氣對策信號(燈號) |

### `TaiwanStockDispositionSecuritiesPeriod`　處置股票期間
- 取樣參數：`{'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |
| 4 | `disposition_cnt` | NUMERIC(20,6) | 處置次數 |
| 5 | `condition` | VARCHAR(255) | 處置條件 |
| 6 | `measure` | TEXT | 處置措施 |
| 7 | `period_start` | DATE | 處置起 |
| 8 | `period_end` | DATE | 處置迄 |

### `TaiwanStockIndustryChain`　產業鏈分類
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代號 |
| 2 | `industry` | VARCHAR(255) | 產業 |
| 3 | `sub_industry` | VARCHAR(255) | 次產業 |
| 4 | `date` | DATE | 日期 |

### `TaiwanStockSplitPrice`　股票面額/分割參考價
- 取樣參數：`{'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, type`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `type` | VARCHAR(255) | 類別/科目代碼 |
| 4 | `before_price` | NUMERIC(20,6) | 除權息前價 |
| 5 | `after_price` | NUMERIC(20,6) | 除權息後參考價 |
| 6 | `max_price` | NUMERIC(20,6) | 漲停價 |
| 7 | `min_price` | NUMERIC(20,6) | 跌停價 |
| 8 | `open_price` | NUMERIC(20,6) | 開盤參考價 |

### `TaiwanStockInfoWithWarrantSummary`　權證基本資訊彙總
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date, type`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代號 |
| 2 | `date` | DATE | 日期 |
| 3 | `close` | NUMERIC(20,6) | 收盤價 |
| 4 | `target_stock_id` | VARCHAR(255) | 標的股票代號 |
| 5 | `target_close` | NUMERIC(20,6) | 標的收盤 |
| 6 | `type` | VARCHAR(255) | 類別/科目代碼 |
| 7 | `fulfillment_method` | VARCHAR(255) | 履約方式 |
| 8 | `end_date` | DATE | 結束日 |
| 9 | `fulfillment_start_date` | DATE | 履約起日 |
| 10 | `fulfillment_end_date` | DATE | 履約迄日 |
| 11 | `exercise_ratio` | NUMERIC(20,6) | 行使比例 |
| 12 | `fulfillment_price` | NUMERIC(20,6) | 履約價 |

### `TaiwanStockTradingDate`　交易日曆
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |

### `TaiwanStockParValueChange`　面額變更
- 取樣參數：`{'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |
| 4 | `before_close` | NUMERIC(20,6) | 變更前收盤 |
| 5 | `after_ref_close` | NUMERIC(20,6) | 變更後參考收盤 |
| 6 | `after_ref_max` | NUMERIC(20,6) | 變更後參考漲停 |
| 7 | `after_ref_min` | NUMERIC(20,6) | 變更後參考跌停 |
| 8 | `after_ref_open` | NUMERIC(20,6) | 變更後參考開盤 |

### `TaiwanStockSuspended`　暫停交易
- 取樣參數：`{'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `suspension_time` | VARCHAR(255) | 暫停時間 |
| 4 | `resumption_date` | DATE | 恢復日 |
| 5 | `resumption_time` | VARCHAR(255) | 恢復時間 |

### `TaiwanStockDayTradingSuspension`　暫停當沖
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `stock_id` | VARCHAR(255) | 股票代號 |
| 2 | `date` | DATE | 日期 |
| 3 | `end_date` | DATE | 結束日 |
| 4 | `reason` | VARCHAR(255) | 原因 |

### `TaiwanStockDayTradingBorrowingFeeRate`　當沖借券費率
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `stock_name` | VARCHAR(255) | 股票名稱 |
| 4 | `InvestorBorrowedShares` | NUMERIC(20,6) | 投資人借券張數 |
| 5 | `InvestorBorrowingFeeRate` | NUMERIC(20,6) | 投資人借券費率 |

### `TaiwanStockPriceLimit`　漲跌停參考價
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `reference_price` | NUMERIC(20,6) | 參考價 |
| 4 | `limit_up` | NUMERIC(20,6) | 漲停價 |
| 5 | `limit_down` | NUMERIC(20,6) | 跌停價 |

### `TaiwanStockLoanCollateralBalance`　融資融券+借券擔保品餘額(全項)
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `market` | VARCHAR(255) | 市場別 |
| 4 | `MarginPreviousDayBalance` | NUMERIC(20,6) | 融資前日餘額 |
| 5 | `MarginBuy` | NUMERIC(20,6) | 融資買進 |
| 6 | `MarginSell` | NUMERIC(20,6) | 融資賣出 |
| 7 | `MarginCashRedemption` | NUMERIC(20,6) | 融資現金償還 |
| 8 | `MarginCurrentDayBalance` | NUMERIC(20,6) | 融資今日餘額 |
| 9 | `MarginNextDayQuota` | NUMERIC(20,6) | 融資次日限額 |
| 10 | `SecuritiesFirmLoanPreviousDayBalance` | NUMERIC(20,6) | 證券商出借前日餘額 |
| 11 | `SecuritiesFirmLoanBuy` | NUMERIC(20,6) | 證券商出借買進 |
| 12 | `SecuritiesFirmLoanSell` | NUMERIC(20,6) | 證券商出借賣出 |
| 13 | `SecuritiesFirmLoanCashRedemption` | NUMERIC(20,6) | 證券商出借現金償還 |
| 14 | `SecuritiesFirmLoanReplacement` | NUMERIC(20,6) | 證券商出借補券/調整 |
| 15 | `SecuritiesFirmLoanCurrentDayBalance` | NUMERIC(20,6) | 證券商出借今日餘額 |
| 16 | `SecuritiesFirmLoanNextDayQuota` | NUMERIC(20,6) | 證券商出借次日限額 |
| 17 | `UnrestrictedLoanPreviousDayBalance` | NUMERIC(20,6) | 無限制轉融通前日餘額 |
| 18 | `UnrestrictedLoanBuy` | NUMERIC(20,6) | 無限制轉融通買進 |
| 19 | `UnrestrictedLoanSell` | NUMERIC(20,6) | 無限制轉融通賣出 |
| 20 | `UnrestrictedLoanCashRedemption` | NUMERIC(20,6) | 無限制轉融通現金償還 |
| 21 | `UnrestrictedLoanReplacement` | NUMERIC(20,6) | 無限制轉融通補券/調整 |
| 22 | `UnrestrictedLoanCurrentDayBalance` | NUMERIC(20,6) | 無限制轉融通今日餘額 |
| 23 | `UnrestrictedLoanNextDayQuota` | NUMERIC(20,6) | 無限制轉融通次日限額 |
| 24 | `SecuritiesFinanceSecuredLoanPreviousDayBalance` | NUMERIC(20,6) | 證金事業擔保放款前日餘額 |
| 25 | `SecuritiesFinanceSecuredLoanBuy` | NUMERIC(20,6) | 證金事業擔保放款買進 |
| 26 | `SecuritiesFinanceSecuredLoanSell` | NUMERIC(20,6) | 證金事業擔保放款賣出 |
| 27 | `SecuritiesFinanceSecuredLoanCashRedemption` | NUMERIC(20,6) | 證金事業擔保放款現金償還 |
| 28 | `SecuritiesFinanceSecuredLoanReplacement` | NUMERIC(20,6) | 證金事業擔保放款補券/調整 |
| 29 | `SecuritiesFinanceSecuredLoanCurrentDayBalance` | NUMERIC(20,6) | 證金事業擔保放款今日餘額 |
| 30 | `SecuritiesFinanceSecuredLoanNextDayQuota` | NUMERIC(20,6) | 證金事業擔保放款次日限額 |
| 31 | `SettlementMarginPreviousDayBalance` | NUMERIC(20,6) | 交割融資前日餘額 |
| 32 | `SettlementMarginBuy` | NUMERIC(20,6) | 交割融資買進 |
| 33 | `SettlementMarginSell` | NUMERIC(20,6) | 交割融資賣出 |
| 34 | `SettlementMarginCashRedemption` | NUMERIC(20,6) | 交割融資現金償還 |
| 35 | `SettlementMarginReplacement` | NUMERIC(20,6) | 交割融資補券/調整 |
| 36 | `SettlementMarginCurrentDayBalance` | NUMERIC(20,6) | 交割融資今日餘額 |
| 37 | `SettlementMarginNextDayQuota` | NUMERIC(20,6) | 交割融資次日限額 |

### `TaiwanStockBlockTrade`　鉅額交易
- 取樣參數：`{'data_id': '2330', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `trade_type` | VARCHAR(255) | 交易類別 |
| 4 | `price` | NUMERIC(20,6) | 價格 |
| 5 | `volume` | NUMERIC(20,6) | 成交量/股數 |
| 6 | `trading_money` | NUMERIC(20,6) | 成交金額 |

---

## B. 期權期貨（日交易 → 可納入，作為特徵/情境輸入）（16 個）


### `TaiwanFuturesDaily`　期貨日成交
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TX'}`｜推定主鍵：`futures_id, date, trading_session`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `futures_id` | VARCHAR(255) | 期貨商品代號 |
| 3 | `contract_date` | VARCHAR(255) | 契約月份 |
| 4 | `open` | NUMERIC(20,6) | 開盤價 |
| 5 | `max` | NUMERIC(20,6) | 最高價 |
| 6 | `min` | NUMERIC(20,6) | 最低價 |
| 7 | `close` | NUMERIC(20,6) | 收盤價 |
| 8 | `spread` | NUMERIC(20,6) | 漲跌價差 |
| 9 | `spread_per` | NUMERIC(20,6) | 漲跌幅(%) |
| 10 | `volume` | NUMERIC(20,6) | 成交量/股數 |
| 11 | `settlement_price` | NUMERIC(20,6) | 結算價 |
| 12 | `open_interest` | NUMERIC(20,6) | 未平倉 |
| 13 | `trading_session` | VARCHAR(255) | 交易時段(一般/盤後) |

### `TaiwanOptionDaily`　選擇權日成交
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TXO'}`｜推定主鍵：`option_id, date, call_put, trading_session`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `option_id` | VARCHAR(255) | 選擇權商品代號 |
| 3 | `contract_date` | VARCHAR(255) | 契約月份 |
| 4 | `strike_price` | NUMERIC(20,6) | 履約價 |
| 5 | `call_put` | VARCHAR(255) | 買權/賣權 |
| 6 | `open` | NUMERIC(20,6) | 開盤價 |
| 7 | `max` | NUMERIC(20,6) | 最高價 |
| 8 | `min` | NUMERIC(20,6) | 最低價 |
| 9 | `close` | NUMERIC(20,6) | 收盤價 |
| 10 | `volume` | NUMERIC(20,6) | 成交量/股數 |
| 11 | `settlement_price` | NUMERIC(20,6) | 結算價 |
| 12 | `open_interest` | NUMERIC(20,6) | 未平倉 |
| 13 | `trading_session` | VARCHAR(255) | 交易時段(一般/盤後) |

### `TaiwanFutOptTickInfo`　期權契約資訊(非tick資料)
- 取樣參數：`{'start_date': '2025-06-01'}`｜推定主鍵：`code, date, name`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `code` | VARCHAR(255) | 代碼 |
| 2 | `callput` | VARCHAR(255) | 買賣權 |
| 3 | `date` | VARCHAR(255) | 日期 |
| 4 | `name` | VARCHAR(255) | 名稱/法人別 |
| 5 | `listing_date` | DATE | 上市日 |
| 6 | `expire_price` | NUMERIC(20,6) | 到期價 |
| 7 | `update_date` | DATE | 更新日 |

### `TaiwanFutOptDailyInfo`　期權每日契約資訊
- 取樣參數：`{'start_date': '2025-06-01'}`｜推定主鍵：`code, type, name`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `code` | VARCHAR(255) | 代碼 |
| 2 | `type` | VARCHAR(255) | 類別/科目代碼 |
| 3 | `name` | VARCHAR(255) | 名稱/法人別 |

### `TaiwanFutOptInstitutionalInvestors`　期權三大法人
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TX'}`｜推定主鍵：`date, name, institutional_investors`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `name` | VARCHAR(255) | 名稱/法人別 |
| 2 | `date` | DATE | 日期 |
| 3 | `institutional_investors` | VARCHAR(255) | 法人別 |
| 4 | `long_deal_volume` | NUMERIC(20,6) | 多方交易口數 |
| 5 | `long_deal_amount` | NUMERIC(20,6) | 多方交易金額 |
| 6 | `short_deal_volume` | NUMERIC(20,6) | 空方交易口數 |
| 7 | `short_deal_amount` | NUMERIC(20,6) | 空方交易金額 |
| 8 | `long_open_interest_balance_volume` | NUMERIC(20,6) | 多方未平倉口數 |
| 9 | `long_open_interest_balance_amount` | NUMERIC(20,6) | 多方未平倉金額 |
| 10 | `short_open_interest_balance_volume` | NUMERIC(20,6) | 空方未平倉口數 |
| 11 | `short_open_interest_balance_amount` | NUMERIC(20,6) | 空方未平倉金額 |

### `TaiwanFuturesDealerTradingVolumeDaily`　期貨自營商成交量
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TX'}`｜推定主鍵：`futures_id, dealer_code, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `dealer_code` | VARCHAR(255) | 自營商代號 |
| 3 | `dealer_name` | VARCHAR(255) | 自營商名稱 |
| 4 | `futures_id` | VARCHAR(255) | 期貨商品代號 |
| 5 | `volume` | NUMERIC(20,6) | 成交量/股數 |
| 6 | `is_after_hour` | BOOLEAN | 是否盤後 |

### `TaiwanOptionDealerTradingVolumeDaily`　選擇權自營商成交量
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TXO'}`｜推定主鍵：`option_id, dealer_code, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `dealer_code` | VARCHAR(255) | 自營商代號 |
| 3 | `dealer_name` | VARCHAR(255) | 自營商名稱 |
| 4 | `option_id` | VARCHAR(255) | 選擇權商品代號 |
| 5 | `volume` | NUMERIC(20,6) | 成交量/股數 |
| 6 | `is_after_hour` | BOOLEAN | 是否盤後 |

### `TaiwanFuturesInstitutionalInvestors`　期貨三大法人
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TX'}`｜推定主鍵：`futures_id, date, institutional_investors`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `futures_id` | VARCHAR(255) | 期貨商品代號 |
| 2 | `date` | DATE | 日期 |
| 3 | `institutional_investors` | VARCHAR(255) | 法人別 |
| 4 | `long_deal_volume` | NUMERIC(20,6) | 多方交易口數 |
| 5 | `long_deal_amount` | NUMERIC(20,6) | 多方交易金額 |
| 6 | `short_deal_volume` | NUMERIC(20,6) | 空方交易口數 |
| 7 | `short_deal_amount` | NUMERIC(20,6) | 空方交易金額 |
| 8 | `long_open_interest_balance_volume` | NUMERIC(20,6) | 多方未平倉口數 |
| 9 | `long_open_interest_balance_amount` | NUMERIC(20,6) | 多方未平倉金額 |
| 10 | `short_open_interest_balance_volume` | NUMERIC(20,6) | 空方未平倉口數 |
| 11 | `short_open_interest_balance_amount` | NUMERIC(20,6) | 空方未平倉金額 |

### `TaiwanOptionInstitutionalInvestors`　選擇權三大法人
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TXO'}`｜推定主鍵：`option_id, date, institutional_investors, call_put`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `option_id` | VARCHAR(255) | 選擇權商品代號 |
| 2 | `date` | DATE | 日期 |
| 3 | `call_put` | VARCHAR(255) | 買權/賣權 |
| 4 | `institutional_investors` | VARCHAR(255) | 法人別 |
| 5 | `long_deal_volume` | NUMERIC(20,6) | 多方交易口數 |
| 6 | `long_deal_amount` | NUMERIC(20,6) | 多方交易金額 |
| 7 | `short_deal_volume` | NUMERIC(20,6) | 空方交易口數 |
| 8 | `short_deal_amount` | NUMERIC(20,6) | 空方交易金額 |
| 9 | `long_open_interest_balance_volume` | NUMERIC(20,6) | 多方未平倉口數 |
| 10 | `long_open_interest_balance_amount` | NUMERIC(20,6) | 多方未平倉金額 |
| 11 | `short_open_interest_balance_volume` | NUMERIC(20,6) | 空方未平倉口數 |
| 12 | `short_open_interest_balance_amount` | NUMERIC(20,6) | 空方未平倉金額 |

### `TaiwanFuturesInstitutionalInvestorsAfterHours`　期貨三大法人(盤後)
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TX'}`｜推定主鍵：`futures_id, date, institutional_investors`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `futures_id` | VARCHAR(255) | 期貨商品代號 |
| 2 | `date` | DATE | 日期 |
| 3 | `institutional_investors` | VARCHAR(255) | 法人別 |
| 4 | `long_deal_volume` | NUMERIC(20,6) | 多方交易口數 |
| 5 | `long_deal_amount` | NUMERIC(20,6) | 多方交易金額 |
| 6 | `short_deal_volume` | NUMERIC(20,6) | 空方交易口數 |
| 7 | `short_deal_amount` | NUMERIC(20,6) | 空方交易金額 |

### `TaiwanOptionInstitutionalInvestorsAfterHours`　選擇權三大法人(盤後)
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TXO'}`｜推定主鍵：`option_id, date, institutional_investors, call_put`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `option_id` | VARCHAR(255) | 選擇權商品代號 |
| 2 | `date` | DATE | 日期 |
| 3 | `call_put` | VARCHAR(255) | 買權/賣權 |
| 4 | `institutional_investors` | VARCHAR(255) | 法人別 |
| 5 | `long_deal_volume` | NUMERIC(20,6) | 多方交易口數 |
| 6 | `long_deal_amount` | NUMERIC(20,6) | 多方交易金額 |
| 7 | `short_deal_volume` | NUMERIC(20,6) | 空方交易口數 |
| 8 | `short_deal_amount` | NUMERIC(20,6) | 空方交易金額 |

### `TaiwanOptionOpenInterestLargeTraders`　選擇權大額交易人未平倉
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TXO'}`｜推定主鍵：`option_id, date, name, contract_type, put_call`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `contract_type` | VARCHAR(255) | 契約類型 |
| 2 | `buy_top5_trader_open_interest` | NUMERIC(20,6) | 買方前5大交易人未平倉 |
| 3 | `buy_top5_trader_open_interest_per` | NUMERIC(20,6) | 買方前5大交易人未平倉占比% |
| 4 | `buy_top10_trader_open_interest` | NUMERIC(20,6) | 買方前10大交易人未平倉 |
| 5 | `buy_top10_trader_open_interest_per` | NUMERIC(20,6) | 買方前10大交易人未平倉占比% |
| 6 | `sell_top5_trader_open_interest` | NUMERIC(20,6) | 賣方前5大交易人未平倉 |
| 7 | `sell_top5_trader_open_interest_per` | NUMERIC(20,6) | 賣方前5大交易人未平倉占比% |
| 8 | `sell_top10_trader_open_interest` | NUMERIC(20,6) | 賣方前10大交易人未平倉 |
| 9 | `sell_top10_trader_open_interest_per` | NUMERIC(20,6) | 賣方前10大交易人未平倉占比% |
| 10 | `market_open_interest` | NUMERIC(20,6) | 全市場未平倉 |
| 11 | `buy_top5_specific_open_interest` | NUMERIC(20,6) | 買方前5大特定法人未平倉 |
| 12 | `buy_top5_specific_open_interest_per` | NUMERIC(20,6) | 買方前5大特定法人未平倉占比% |
| 13 | `buy_top10_specific_open_interest` | NUMERIC(20,6) | 買方前10大特定法人未平倉 |
| 14 | `buy_top10_specific_open_interest_per` | NUMERIC(20,6) | 買方前10大特定法人未平倉占比% |
| 15 | `sell_top5_specific_open_interest` | NUMERIC(20,6) | 賣方前5大特定法人未平倉 |
| 16 | `sell_top5_specific_open_interest_per` | NUMERIC(20,6) | 賣方前5大特定法人未平倉占比% |
| 17 | `sell_top10_specific_open_interest` | NUMERIC(20,6) | 賣方前10大特定法人未平倉 |
| 18 | `sell_top10_specific_open_interest_per` | NUMERIC(20,6) | 賣方前10大特定法人未平倉占比% |
| 19 | `date` | DATE | 日期 |
| 20 | `put_call` | VARCHAR(255) | 買賣權 |
| 21 | `name` | VARCHAR(255) | 名稱/法人別 |
| 22 | `option_id` | VARCHAR(255) | 選擇權商品代號 |

### `TaiwanFuturesOpenInterestLargeTraders`　期貨大額交易人未平倉
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TX'}`｜推定主鍵：`futures_id, date, name, contract_type`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `name` | VARCHAR(255) | 名稱/法人別 |
| 2 | `contract_type` | VARCHAR(255) | 契約類型 |
| 3 | `buy_top5_trader_open_interest` | NUMERIC(20,6) | 買方前5大交易人未平倉 |
| 4 | `buy_top5_trader_open_interest_per` | NUMERIC(20,6) | 買方前5大交易人未平倉占比% |
| 5 | `buy_top10_trader_open_interest` | NUMERIC(20,6) | 買方前10大交易人未平倉 |
| 6 | `buy_top10_trader_open_interest_per` | NUMERIC(20,6) | 買方前10大交易人未平倉占比% |
| 7 | `sell_top5_trader_open_interest` | NUMERIC(20,6) | 賣方前5大交易人未平倉 |
| 8 | `sell_top5_trader_open_interest_per` | NUMERIC(20,6) | 賣方前5大交易人未平倉占比% |
| 9 | `sell_top10_trader_open_interest` | NUMERIC(20,6) | 賣方前10大交易人未平倉 |
| 10 | `sell_top10_trader_open_interest_per` | NUMERIC(20,6) | 賣方前10大交易人未平倉占比% |
| 11 | `market_open_interest` | NUMERIC(20,6) | 全市場未平倉 |
| 12 | `buy_top5_specific_open_interest` | NUMERIC(20,6) | 買方前5大特定法人未平倉 |
| 13 | `buy_top5_specific_open_interest_per` | NUMERIC(20,6) | 買方前5大特定法人未平倉占比% |
| 14 | `buy_top10_specific_open_interest` | NUMERIC(20,6) | 買方前10大特定法人未平倉 |
| 15 | `buy_top10_specific_open_interest_per` | NUMERIC(20,6) | 買方前10大特定法人未平倉占比% |
| 16 | `sell_top5_specific_open_interest` | NUMERIC(20,6) | 賣方前5大特定法人未平倉 |
| 17 | `sell_top5_specific_open_interest_per` | NUMERIC(20,6) | 賣方前5大特定法人未平倉占比% |
| 18 | `sell_top10_specific_open_interest` | NUMERIC(20,6) | 賣方前10大特定法人未平倉 |
| 19 | `sell_top10_specific_open_interest_per` | NUMERIC(20,6) | 賣方前10大特定法人未平倉占比% |
| 20 | `date` | DATE | 日期 |
| 21 | `futures_id` | VARCHAR(255) | 期貨商品代號 |

### `TaiwanFuturesSpreadTrading`　期貨價差交易
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TX'}`｜推定主鍵：`futures_id, date, trading_session`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `futures_id` | VARCHAR(255) | 期貨商品代號 |
| 3 | `contract_date` | VARCHAR(255) | 契約月份 |
| 4 | `open` | NUMERIC(20,6) | 開盤價 |
| 5 | `max` | NUMERIC(20,6) | 最高價 |
| 6 | `min` | NUMERIC(20,6) | 最低價 |
| 7 | `close` | NUMERIC(20,6) | 收盤價 |
| 8 | `best_bid` | NUMERIC(20,6) | 最佳買價 |
| 9 | `best_ask` | NUMERIC(20,6) | 最佳賣價 |
| 10 | `historical_max` | NUMERIC(20,6) | 歷史高 |
| 11 | `historical_min` | NUMERIC(20,6) | 歷史低 |
| 12 | `spread_to_spread_volume` | NUMERIC(20,6) | 價差對價差成交量 |
| 13 | `spread_to_single_volume` | NUMERIC(20,6) | 價差對單式成交量 |
| 14 | `trading_session` | VARCHAR(255) | 交易時段(一般/盤後) |

### `TaiwanFuturesFinalSettlementPrice`　期貨最後結算價
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TX'}`｜推定主鍵：`futures_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `contract_month` | VARCHAR(255) | 契約月份 |
| 3 | `futures_type` | VARCHAR(255) | 期貨類別 |
| 4 | `futures_id` | VARCHAR(255) | 期貨商品代號 |
| 5 | `futures_name` | VARCHAR(255) | 期貨名稱 |
| 6 | `settlement_price` | NUMERIC(20,6) | 結算價 |
| 7 | `underlying_code` | VARCHAR(255) | 標的代號 |
| 8 | `notional_value` | NUMERIC(20,6) | 契約價值 |

### `TaiwanOptionFinalSettlementPrice`　選擇權最後結算價
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'TXO'}`｜推定主鍵：`option_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `contract_month` | VARCHAR(255) | 契約月份 |
| 3 | `option_type` | VARCHAR(255) | 選擇權類別 |
| 4 | `option_id` | VARCHAR(255) | 選擇權商品代號 |
| 5 | `option_name` | VARCHAR(255) | 選擇權名稱 |
| 6 | `settlement_price` | NUMERIC(20,6) | 結算價 |
| 7 | `underlying_code` | VARCHAR(255) | 標的代號 |
| 8 | `notional_value` | NUMERIC(20,6) | 契約價值 |

---

## C. 非台股 海外/商品/匯率/利率（日交易 → 可納入，作為特徵/情境輸入）（13 個）


### `CrudeOilPrices`　原油價格
- 取樣參數：`{'data_id': 'WTI', 'start_date': '2024-01-01'}`｜推定主鍵：`date, name`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `name` | VARCHAR(255) | 名稱/法人別 |
| 3 | `price` | NUMERIC(20,6) | 價格 |

### `UKStockPrice`　英股日價
- 取樣參數：`{'data_id': 'HSBA.L', 'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `Adj_Close` | NUMERIC(20,6) | 還原收盤 |
| 4 | `Close` | NUMERIC(20,6) | 收盤 |
| 5 | `High` | NUMERIC(20,6) | 最高 |
| 6 | `Low` | NUMERIC(20,6) | 最低 |
| 7 | `Open` | NUMERIC(20,6) | 開盤 |
| 8 | `Volume` | NUMERIC(20,6) | 成交量 |

### `USStockPrice`　美股日價
- 取樣參數：`{'start_date': '2024-06-01', 'end_date': '2026-06-09', 'data_id': 'AAPL'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `Adj_Close` | NUMERIC(20,6) | 還原收盤 |
| 4 | `Close` | NUMERIC(20,6) | 收盤 |
| 5 | `High` | NUMERIC(20,6) | 最高 |
| 6 | `Low` | NUMERIC(20,6) | 最低 |
| 7 | `Open` | NUMERIC(20,6) | 開盤 |
| 8 | `Volume` | NUMERIC(20,6) | 成交量 |

### `EuropeStockInfo`　歐股基本資訊
- 取樣參數：`{}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `Market` | VARCHAR(255) | 市場 |
| 4 | `stock_name` | VARCHAR(255) | 股票名稱 |

### `JapanStockInfo`　日股基本資訊
- 取樣參數：`{}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `Exchange` | VARCHAR(255) | 交易所 |
| 4 | `Sector` | VARCHAR(255) | 類股 |
| 5 | `stock_name` | VARCHAR(255) | 股票名稱 |

### `GoldPrice`　黃金價格
- 取樣參數：`{'start_date': '2025-06-01'}`｜推定主鍵：`date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `Price` | NUMERIC(20,6) | 價格 |
| 2 | `date` | TIMESTAMP | 日期 |

### `InterestRate`　各國基準利率
- 取樣參數：`{'start_date': '2010-01-01'}`｜推定主鍵：`date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `country` | VARCHAR(255) | 國家代碼 |
| 2 | `date` | DATE | 日期 |
| 3 | `full_country_name` | VARCHAR(255) | 國家全名 |
| 4 | `interest_rate` | NUMERIC(20,6) | 利率 |

### `USStockInfo`　美股基本資訊
- 取樣參數：`{'start_date': '2025-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `Country` | VARCHAR(255) | 國家 |
| 4 | `IPOYear` | NUMERIC(20,6) | 上市年 |
| 5 | `MarketCap` | NUMERIC(20,6) | 市值 |
| 6 | `Subsector` | VARCHAR(255) | 次類股 |
| 7 | `stock_name` | VARCHAR(255) | 股票名稱 |

### `UKStockInfo`　英股基本資訊
- 取樣參數：`{}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `Country` | VARCHAR(255) | 國家 |
| 4 | `stock_name` | VARCHAR(255) | 股票名稱 |

### `EuropeStockPrice`　歐股日價
- 取樣參數：`{'data_id': 'AAA.AS', 'start_date': '2024-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `Adj_Close` | NUMERIC(20,6) | 還原收盤 |
| 4 | `Close` | NUMERIC(20,6) | 收盤 |
| 5 | `High` | NUMERIC(20,6) | 最高 |
| 6 | `Low` | NUMERIC(20,6) | 最低 |
| 7 | `Open` | NUMERIC(20,6) | 開盤 |
| 8 | `Volume` | NUMERIC(20,6) | 成交量 |

### `JapanStockPrice`　日股日價
- 取樣參數：`{'data_id': '1301.T', 'start_date': '2024-06-01'}`｜推定主鍵：`stock_id, date`

| # | 欄位名(API 原樣) | 型別(初始) | 中文說明 |
|---|---|---|---|
| 1 | `date` | DATE | 日期 |
| 2 | `stock_id` | VARCHAR(255) | 股票代號 |
| 3 | `Adj_Close` | NUMERIC(20,6) | 還原收盤 |
| 4 | `Close` | NUMERIC(20,6) | 收盤 |
| 5 | `High` | NUMERIC(20,6) | 最高 |
| 6 | `Low` | NUMERIC(20,6) | 最低 |
| 7 | `Open` | NUMERIC(20,6) | 開盤 |
| 8 | `Volume` | NUMERIC(20,6) | 成交量 |

**本組未取樣（需特定 data_id/ticker 或該參數無資料，待實際同步時取得）**：`ExchangeRate`, `GovernmentBondsYield`


---

## FRED（api.stlouisfed.org）

FRED 為**另一條 API 入口**（非 FinMind ingester）。每個 series 之觀測值落地為一張表 `fred_series`：

| # | 欄位名(API 原樣) | 型別 | 中文說明 |
|---|---|---|---|
| 1 | `series_id` | VARCHAR(255) | (衍生)FRED series 代號(主鍵) |
| 2 | `date` | DATE | 觀測日期 |
| 3 | `value` | VARCHAR(255) | 觀測值(字串,空值為 ".") |
| 4 | `realtime_start` | DATE | 即時起始(資料版本) |
| 5 | `realtime_end` | DATE | 即時結束(資料版本) |

- 主鍵：`(series_id, date)`（generic `KEY_CANDIDATES` 將 series_id 前置）。`value` 為字串（FRED 缺值以 `.` 表示），數值轉換於 feature 層。
- augur 具體 series 清單（如 `T10Y2Y` 殖利率曲線、`UNRATE` 失業率…）待 feature 設計時定，由同一 generic 入口落地。


---

## 附註：財報三表（長格式 long-format）的中文科目

`TaiwanStockFinancialStatements`(綜合損益表)、`TaiwanStockBalanceSheet`(資產負債表)、`TaiwanStockCashFlowsStatement`(現金流量表) 為**長格式**：每列一個會計科目，欄位固定 5 個——`date, stock_id, type(科目英文碼), value(數值), origin_name(科目中文名)`。
**中文科目名是 API `origin_name` 實值**（真實，非人工）。各表科目數（2330 樣本）：綜合損益表 **17**、資產負債表 **101**、現金流量表 **27**。示例：
- 綜合損益表：`Revenue`=營業收入、`CostOfGoodsSold`=營業成本、`GrossProfit`=營業毛利、`OperatingIncome`=營業利益、`IncomeAfterTaxes`=本期淨利
- 資產負債表：`CashAndCashEquivalents`=現金及約當現金、各科目另有 `_per` 版(佔比)
- 現金流量表：`CashFlowsFromOperatingActivities`=營業活動淨現金流、`CashBalancesEndOfPeriod`=期末現金餘額

---

## infra log 表（explicit DDL，非 generic；憲章 PHASE 1 bootstrap）

兩張**系統運維表**——非 API 回應推導，故用固定 explicit DDL（`src/augur/core/schema.py` `INFRA_DDL`），不走 generic auto-schema。型別為運維型別（BIGSERIAL / TIMESTAMP / TEXT），非 #5 之 API-表型別規則。

### `pipeline_execution_log` 任務執行記錄　PK `id`
| # | 欄位 | 型別 | 中文 |
|---|---|---|---|
| 1 | `id` | BIGSERIAL | 主鍵 |
| 2 | `task` | VARCHAR(255) | 任務名 |
| 3 | `target` | VARCHAR(255) | 對象 |
| 4 | `status` | VARCHAR(255) | 狀態 |
| 5 | `rows` | BIGINT | 列數 |
| 6 | `started_at` | TIMESTAMP | 起始（default now()）|
| 7 | `ended_at` | TIMESTAMP | 結束 |
| 8 | `detail` | TEXT | 明細 |

### `data_audit_log` 資料稽核記錄　PK `id`
| # | 欄位 | 型別 | 中文 |
|---|---|---|---|
| 1 | `id` | BIGSERIAL | 主鍵 |
| 2 | `dataset` | VARCHAR(255) | dataset/表名 |
| 3 | `data_id` | VARCHAR(255) | 資料識別（股號/series）|
| 4 | `action` | VARCHAR(255) | 動作（upsert…）|
| 5 | `rows` | BIGINT | 列數 |
| 6 | `logged_at` | TIMESTAMP | 記錄時間（default now()）|
| 7 | `detail` | TEXT | 明細 |

---

## 建表驗證紀錄（2026-06-09，§一.10 source-traceable）

- **環境隔離（clean-room #16）**：augur 連線修正為獨立 `augur` db（先前 `.env` 誤指 stock_backend 的 `stock` db，已修為 `DB_NAME/USER/PASSWORD=augur`）；本驗證全程在 `augur` db，stock_backend 的 `stock` db 未受影響。
- **方法**：`schema.bootstrap_infra`（建 2 log 表）+ 逐 dataset `ingest.ingest_finmind` / `ingest_fred`（用兩輪 live-probe 之 working params）→ generic 自動建表 + 取樣 upsert（全用 augur 自身 clean-room 模組）。
- **結果（DB query）**：**85 表建成 / 0 失敗 / 取樣總列數 2,181,069**（82 FinMind + `fred_series` + 2 log）；2 sponsor-tier（`ExchangeRate` / `GovernmentBondsYield`）無資料未建。
- **性質**：**取樣驗證**（每表近期窗，非全史）——證明建表 + 抓取 + 落地 + 稽核留痕端到端 OK。全市場全史 sync 為後續另一步（long-running：`caffeinate` + 5-min HB + DB-driven resume）。
- **PK 註**：小樣本下 generic `detect_keys` 對部分表保底為「全欄」；全史建表時由全量首批重新推導收斂至真 PK（#6 主鍵首建固定）。

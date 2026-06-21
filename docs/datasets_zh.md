# augur 資料源欄位中文總表（FinMind + FRED）— 2026-06-15

**目的**：augur 要抓的全部 dataset，**逐表逐欄**附中文名 + 來源 + 推定型別。供建模/查表/schema 註解之單一參考。**83 FinMind dataset + FRED，共 ~650 真實欄位**（已含 datasets.md 未列、實證補入的 8 表）。

**中文名來源規則（依用戶指示）**：
1. **FinMind/FRED 官方 API 可取得 → 以官方為主**（標 `FM`）。FinMind 唯一官方中文來源 = `/translation`（全 83 dataset 實測：0 個給逐欄清單；9 個給 `{name,english}` dict＝科目值/法人別/外資/融資/指數名）。
2. **官方取不到 → 金融專業用語**（台股慣用詞，標 `金融`）。
3. `派生`＝augur 落地補欄（如 `series_id`）。

**欄位來源（完整度）**：已落地 22 表讀 **augur DB 真實欄**；未落地 48 表 **probe `/data` 取真實欄**；5 表（TotalReturnIndex/UK・Europe・Japan Info/GovBondsYield）以 datasets.md 補。→ 比 datasets.md「Key Columns」完整（如 Dividend 實 22 欄、LoanCollateralBalance 37 欄）。

**型別/大小**：FinMind/FRED **皆不提供**（API 全字串回，實測）→ `推定型別` 由 augur `generic_schema` 依值推導。下表列**型別族**（DATE/NUMERIC/VARCHAR/TEXT）；預設大小 `VARCHAR(255)`、`NUMERIC(20,6)`（值超出自動 auto-widen / 跨型別降級）；已落地表之精確大小見 live DB。

**🔌 抓取**：每表標抓取模式（per-stock 逐股／by-date 全市場／by-dimension-id 維度碼／market 單批／single-day）+ data_id 來源（`/datalist`／roster）+ endpoint。augur `sync_finmind_dataset` 實際**自動偵測**（market 探測→per-stock→by-date→by-dim-id），🔌 行為指示性典型抓法。

**Tier**：F=Free、F(id)=Free 需 data_id、B=Backer、S=Sponsor（augur 為 Sponsor，全可抓；⏰ 2026-06-24 到期）。FinMind 官方逐欄英文清單見 `~/.claude/commands/finmind-references/datasets.md`。

---

## 一、技術面（Technical，15 表）

### TaiwanStockInfo｜台股總覽　`F`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2020-06-03（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| industry_category | 產業類別 | 金融 | VARCHAR |
| stock_id | 股票代號 | 金融 | VARCHAR |
| stock_name | 股票名稱 | 金融 | VARCHAR |
| type | 市場類別 | 金融 | VARCHAR |
| date | 資料日期 | 金融 | DATE |

### TaiwanStockInfoWithWarrant｜台股總覽（含權證）　`F`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2026-06-13（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| industry_category | 產業類別 | 金融 | VARCHAR |
| stock_id | 股票代號 | 金融 | VARCHAR |
| stock_name | 股票名稱 | 金融 | VARCHAR |
| type | 市場類別 | 金融 | VARCHAR |
| date | 資料日期 | 金融 | DATE |

### TaiwanStockInfoWithWarrantSummary｜權證標的對照表　`S`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2014-07-31（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| stock_id | 權證代號 | 金融 | VARCHAR |
| date | 資料日期 | 金融 | DATE |
| close | 權證收盤價 | 金融 | NUMERIC |
| target_stock_id | 標的證券代號 | 金融 | NUMERIC |
| target_close | 標的證券收盤價 | 金融 | NUMERIC |
| type | 權證類別 | 金融 | VARCHAR |
| fulfillment_method | 履約方式 | 金融 | VARCHAR |
| end_date | 到期日 | 金融 | DATE |
| fulfillment_start_date | 履約起始日 | 金融 | DATE |
| fulfillment_end_date | 履約截止日 | 金融 | DATE |
| exercise_ratio | 行使比例 | 金融 | NUMERIC |
| fulfillment_price | 履約價格 | 金融 | NUMERIC |

### TaiwanStockTradingDate｜交易日曆　`F`
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 2000-01-04（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 交易日 | 金融 | DATE |

### TaiwanStockPrice｜股價日成交資訊　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 1994-09-13（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 交易日 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| Trading_Volume | 成交股數 | 金融 | NUMERIC |
| Trading_money | 成交金額 | 金融 | NUMERIC |
| open | 開盤價 | 金融 | NUMERIC |
| max | 最高價 | 金融 | NUMERIC |
| min | 最低價 | 金融 | NUMERIC |
| close | 收盤價 | 金融 | NUMERIC |
| spread | 漲跌價差 | 金融 | NUMERIC |
| Trading_turnover | 成交筆數 | 金融 | NUMERIC |

### TaiwanStockPriceAdj｜還原股價（日）　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 1994-09-14（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 交易日 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| Trading_Volume | 成交股數 | 金融 | NUMERIC |
| Trading_money | 成交金額 | 金融 | NUMERIC |
| open | 還原開盤價 | 金融 | NUMERIC |
| max | 還原最高價 | 金融 | NUMERIC |
| min | 還原最低價 | 金融 | NUMERIC |
| close | 還原收盤價 | 金融 | NUMERIC |
| spread | 漲跌價差 | 金融 | NUMERIC |
| Trading_turnover | 成交筆數 | 金融 | NUMERIC |

### TaiwanStockPER｜本益比/股價淨值比　`F`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2005-09-02（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 交易日 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| dividend_yield | 殖利率 | 金融 | NUMERIC |
| PER | 本益比 | 金融 | NUMERIC |
| PBR | 股價淨值比 | 金融 | NUMERIC |

### TaiwanStockDayTrading｜當沖交易　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2014-01-06（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| stock_id | 股票代號 | 金融 | VARCHAR |
| date | 交易日 | 金融 | DATE |
| BuyAfterSale | 現股當沖先買後賣 | 金融 | VARCHAR |
| Volume | 當沖成交股數 | 金融 | NUMERIC |
| BuyAmount | 當沖買進金額 | 金融 | NUMERIC |
| SellAmount | 當沖賣出金額 | 金融 | NUMERIC |

### TaiwanStockTotalReturnIndex｜發行量加權股價報酬指數　`F`（probe failed，欄依 datasets.md）
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 2003-01-02（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| price | 指數值 | 金融 | NUMERIC |
| stock_id | 指數代號（TAIEX/TPEx）| 金融 | VARCHAR |
| date | 資料日期 | 金融 | DATE |

### TaiwanStock10Year｜十年線（月均價）　`B`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2011-01-24（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 資料日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| close | 收盤價 | 金融 | NUMERIC |

### TaiwanStockWeekPrice｜週K線　`B`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 1999-12-20（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| stock_id | 股票代號 | 金融 | VARCHAR |
| yweek | 年度週別 | 金融 | VARCHAR |
| max | 最高價 | 金融 | NUMERIC |
| min | 最低價 | 金融 | NUMERIC |
| trading_volume | 成交股數 | 金融 | NUMERIC |
| trading_money | 成交金額 | 金融 | NUMERIC |
| trading_turnover | 成交筆數 | 金融 | NUMERIC |
| date | 交易日 | 金融 | DATE |
| close | 收盤價 | 金融 | NUMERIC |
| open | 開盤價 | 金融 | NUMERIC |
| spread | 漲跌價差 | 金融 | NUMERIC |

### TaiwanStockMonthPrice｜月K線　`B`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 1999-12-01（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| stock_id | 股票代號 | 金融 | VARCHAR |
| ymonth | 年度月別 | 金融 | VARCHAR |
| max | 最高價 | 金融 | NUMERIC |
| min | 最低價 | 金融 | NUMERIC |
| trading_volume | 成交股數 | 金融 | NUMERIC |
| trading_money | 成交金額 | 金融 | NUMERIC |
| trading_turnover | 成交筆數 | 金融 | NUMERIC |
| date | 交易日 | 金融 | DATE |
| close | 收盤價 | 金融 | NUMERIC |
| open | 開盤價 | 金融 | NUMERIC |
| spread | 漲跌價差 | 金融 | NUMERIC |

### TaiwanStockSuspended｜暫停交易　`B`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2011-11-04（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 暫停交易日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| suspension_time | 暫停交易時間 | 金融 | VARCHAR |
| resumption_date | 恢復交易日期 | 金融 | VARCHAR |
| resumption_time | 恢復交易時間 | 金融 | VARCHAR |

### TaiwanStockDayTradingSuspension｜暫停現股當沖　`B`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2014-07-09（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| stock_id | 股票代號 | 金融 | VARCHAR |
| date | 起始日期 | 金融 | DATE |
| end_date | 截止日期 | 金融 | DATE |
| reason | 暫停原因 | 金融 | VARCHAR |

### TaiwanStockPriceLimit｜每日漲跌停價　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2000-01-03（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 交易日 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| reference_price | 參考價 | 金融 | NUMERIC |
| limit_up | 漲停價 | 金融 | NUMERIC |
| limit_down | 跌停價 | 金融 | NUMERIC |

---

## 二、籌碼面（Chip / Institutional，17 表）

### TaiwanStockMarginPurchaseShortSale｜融資融券　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2001-01-05（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| MarginPurchaseBuy | 融資買進 | FM | NUMERIC |
| MarginPurchaseCashRepayment | 融資現金償還 | FM | NUMERIC |
| MarginPurchaseLimit | 融資限額 | FM | NUMERIC |
| MarginPurchaseSell | 融資賣出 | FM | NUMERIC |
| MarginPurchaseTodayBalance | 融資今日餘額 | FM | NUMERIC |
| MarginPurchaseYesterdayBalance | 融資昨日餘額 | FM | NUMERIC |
| Note | 註記 | 金融 | VARCHAR |
| OffsetLoanAndShort | 資券相抵 | FM | NUMERIC |
| ShortSaleBuy | 融券買進 | FM | NUMERIC |
| ShortSaleCashRepayment | 融券現金償還 | FM | NUMERIC |
| ShortSaleLimit | 融券限額 | FM | NUMERIC |
| ShortSaleSell | 融券賣出 | FM | NUMERIC |
| ShortSaleTodayBalance | 融券今日餘額 | FM | NUMERIC |
| ShortSaleYesterdayBalance | 融券昨日餘額 | FM | NUMERIC |

### TaiwanStockTotalMarginPurchaseShortSale｜整體市場融資融券　`F`
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 2001-01-03（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| TodayBalance | 當日餘額 | 金融 | NUMERIC |
| YesBalance | 前日餘額 | 金融 | NUMERIC |
| buy | 買進 | 金融 | NUMERIC |
| date | 日期 | 金融 | DATE |
| name | 類別名稱（融資／融券）| FM | VARCHAR |
| Return | 償還 | 金融 | NUMERIC |
| sell | 賣出 | 金融 | NUMERIC |

### TaiwanStockInstitutionalInvestorsBuySell｜三大法人買賣超　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2012-05-02（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| buy | 買進 | 金融 | NUMERIC |
| name | 法人別（自營商／自營商避險／自營商自行買賣／外資自營商／外資／投信）| FM | VARCHAR |
| sell | 賣出 | 金融 | NUMERIC |

### TaiwanStockTotalInstitutionalInvestors｜整體三大法人　`F`
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 2004-04-07（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| buy | 買進 | 金融 | NUMERIC |
| date | 日期 | 金融 | DATE |
| name | 法人別 | 金融 | VARCHAR |
| sell | 賣出 | 金融 | NUMERIC |

### TaiwanStockShareholding｜外資持股　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2004-02-12（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 證券代號 | FM | VARCHAR |
| stock_name | 證券名稱 | FM | VARCHAR |
| InternationalCode | 國際證券代碼（ISIN）| 金融 | VARCHAR |
| ForeignInvestmentRemainingShares | 外資尚可投資股數 | FM | NUMERIC |
| ForeignInvestmentShares | 全體外資持有股數 | FM | NUMERIC |
| ForeignInvestmentRemainRatio | 外資尚可投資比率 | 金融 | NUMERIC |
| ForeignInvestmentSharesRatio | 外資持股比率 | 金融 | NUMERIC |
| ForeignInvestmentUpperLimitRatio | 外資法令投資上限比率 | FM | NUMERIC |
| ChineseInvestmentUpperLimitRatio | 外資及陸資共用法令投資上限比率 | FM | NUMERIC |
| NumberOfSharesIssued | 發行股數 | FM | NUMERIC |
| RecentlyDeclareDate | 最近一次申報外資持股異動日期 ⭐ | FM | VARCHAR |
| note | 與前日異動原因（註）| FM | VARCHAR |

### TaiwanStockHoldingSharesPer｜股權持股分級　`B`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2010-01-29（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| HoldingSharesLevel | 持股分級級距 | 金融 | VARCHAR |
| people | 持股人數 | 金融 | NUMERIC |
| percent | 持股比率 | 金融 | NUMERIC |
| unit | 持股單位數（張）| 金融 | NUMERIC |

### TaiwanStockSecuritiesLending｜借券成交　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2003-11-11（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| transaction_type | 交易類別 | 金融 | VARCHAR |
| volume | 成交量（股）| 金融 | NUMERIC |
| fee_rate | 費率 | 金融 | NUMERIC |
| close | 收盤價 | 金融 | NUMERIC |
| original_return_date | 原訂還券日期 | 金融 | DATE |
| original_lending_period | 原訂借券期間（天）| 金融 | NUMERIC |

### TaiwanStockMarginShortSaleSuspension｜暫停融券賣出　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2015-04-01（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| stock_id | 股票代號 | 金融 | VARCHAR |
| date | 起始日期 | 金融 | DATE |
| end_date | 截止日期 | 金融 | DATE |
| reason | 暫停事由 | 金融 | VARCHAR |

### TaiwanDailyShortSaleBalances｜融券借券餘額　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2005-07-01（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| stock_id | 股票代號 | 金融 | VARCHAR |
| MarginShortSalesPreviousDayBalance | 融券前日餘額 | 金融 | NUMERIC |
| MarginShortSalesShortSales | 融券賣出 | 金融 | NUMERIC |
| MarginShortSalesShortCovering | 融券買進（回補）| 金融 | NUMERIC |
| MarginShortSalesStockRedemption | 融券現券償還 | 金融 | NUMERIC |
| MarginShortSalesCurrentDayBalance | 融券當日餘額 | 金融 | NUMERIC |
| MarginShortSalesQuota | 融券限額 | 金融 | NUMERIC |
| SBLShortSalesPreviousDayBalance | 借券賣出前日餘額 | 金融 | NUMERIC |
| SBLShortSalesShortSales | 借券賣出 | 金融 | NUMERIC |
| SBLShortSalesReturns | 借券賣出返還 | 金融 | NUMERIC |
| SBLShortSalesAdjustments | 借券賣出調整 | 金融 | NUMERIC |
| SBLShortSalesCurrentDayBalance | 借券賣出當日餘額 | 金融 | NUMERIC |
| SBLShortSalesQuota | 借券賣出限額 | 金融 | NUMERIC |
| SBLShortSalesShortCovering | 借券賣出回補 | 金融 | NUMERIC |
| date | 日期 | 金融 | DATE |

### TaiwanSecuritiesTraderInfo｜證券商資訊　`F`
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 1990-03-31（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| securities_trader_id | 券商代號 | 金融 | VARCHAR |
| securities_trader | 券商名稱 | 金融 | VARCHAR |
| date | 日期 | 金融 | DATE |
| address | 地址 | 金融 | VARCHAR |
| phone | 電話 | 金融 | VARCHAR |

### TaiwanStockGovernmentBankBuySell｜八大行庫買賣　`S`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2021-07-01（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| buy_amount | 買進金額 | 金融 | NUMERIC |
| sell_amount | 賣出金額 | 金融 | NUMERIC |
| buy | 買進股數 | 金融 | NUMERIC |
| sell | 賣出股數 | 金融 | NUMERIC |
| bank_name | 行庫名稱 | 金融 | VARCHAR |

### TaiwanTotalExchangeMarginMaintenance｜大盤融資維持率　`B`
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 2001-01-05（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| TotalExchangeMarginMaintenance | 大盤整體融資維持率 | 金融 | NUMERIC |

### TaiwanStockDispositionSecuritiesPeriod｜處置有價證券　`B`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2001-01-02（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| stock_name | 股票名稱 | 金融 | VARCHAR |
| disposition_cnt | 處置次數 | 金融 | NUMERIC |
| condition | 處置條件 | 金融 | VARCHAR |
| measure | 處置措施 | 金融 | TEXT |
| period_start | 處置起始日 | 金融 | DATE |
| period_end | 處置截止日 | 金融 | DATE |

### TaiwanStockBlockTrade｜鉅額交易　`S`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2006-08-11（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| trade_type | 交易類別（配對／逐筆）| 金融 | VARCHAR |
| price | 成交價 | 金融 | NUMERIC |
| volume | 成交量（股）| 金融 | NUMERIC |
| trading_money | 成交金額 | 金融 | NUMERIC |

### TaiwanStockLoanCollateralBalance｜借貸款項擔保品餘額　`S`（37 欄）
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2006-10-02（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| market | 市場別 | 金融 | VARCHAR |
| MarginPreviousDayBalance | 融資前日餘額 | 金融 | NUMERIC |
| MarginBuy | 融資買進 | 金融 | NUMERIC |
| MarginSell | 融資賣出 | 金融 | NUMERIC |
| MarginCashRedemption | 融資現金償還 | 金融 | NUMERIC |
| MarginCurrentDayBalance | 融資當日餘額 | 金融 | NUMERIC |
| MarginNextDayQuota | 融資次日限額 | 金融 | NUMERIC |
| SecuritiesFirmLoanPreviousDayBalance | 券商借貸前日餘額 | 金融 | NUMERIC |
| SecuritiesFirmLoanBuy | 券商借貸買進 | 金融 | NUMERIC |
| SecuritiesFirmLoanSell | 券商借貸賣出 | 金融 | NUMERIC |
| SecuritiesFirmLoanCashRedemption | 券商借貸現金償還 | 金融 | NUMERIC |
| SecuritiesFirmLoanReplacement | 券商借貸代償 | 金融 | NUMERIC |
| SecuritiesFirmLoanCurrentDayBalance | 券商借貸當日餘額 | 金融 | NUMERIC |
| SecuritiesFirmLoanNextDayQuota | 券商借貸次日限額 | 金融 | NUMERIC |
| UnrestrictedLoanPreviousDayBalance | 不限用途借貸前日餘額 | 金融 | NUMERIC |
| UnrestrictedLoanBuy | 不限用途借貸買進 | 金融 | NUMERIC |
| UnrestrictedLoanSell | 不限用途借貸賣出 | 金融 | NUMERIC |
| UnrestrictedLoanCashRedemption | 不限用途借貸現金償還 | 金融 | NUMERIC |
| UnrestrictedLoanReplacement | 不限用途借貸代償 | 金融 | NUMERIC |
| UnrestrictedLoanCurrentDayBalance | 不限用途借貸當日餘額 | 金融 | NUMERIC |
| UnrestrictedLoanNextDayQuota | 不限用途借貸次日限額 | 金融 | NUMERIC |
| SecuritiesFinanceSecuredLoanPreviousDayBalance | 證金公司擔保放款前日餘額 | 金融 | NUMERIC |
| SecuritiesFinanceSecuredLoanBuy | 證金公司擔保放款買進 | 金融 | NUMERIC |
| SecuritiesFinanceSecuredLoanSell | 證金公司擔保放款賣出 | 金融 | NUMERIC |
| SecuritiesFinanceSecuredLoanCashRedemption | 證金公司擔保放款現金償還 | 金融 | NUMERIC |
| SecuritiesFinanceSecuredLoanReplacement | 證金公司擔保放款代償 | 金融 | NUMERIC |
| SecuritiesFinanceSecuredLoanCurrentDayBalance | 證金公司擔保放款當日餘額 | 金融 | NUMERIC |
| SecuritiesFinanceSecuredLoanNextDayQuota | 證金公司擔保放款次日限額 | 金融 | NUMERIC |
| SettlementMarginPreviousDayBalance | 交割保證金前日餘額 | 金融 | NUMERIC |
| SettlementMarginBuy | 交割保證金買進 | 金融 | NUMERIC |
| SettlementMarginSell | 交割保證金賣出 | 金融 | NUMERIC |
| SettlementMarginCashRedemption | 交割保證金現金償還 | 金融 | NUMERIC |
| SettlementMarginReplacement | 交割保證金代償 | 金融 | NUMERIC |
| SettlementMarginCurrentDayBalance | 交割保證金當日餘額 | 金融 | NUMERIC |
| SettlementMarginNextDayQuota | 交割保證金次日限額 | 金融 | NUMERIC |

---

### TaiwanStockInstitutionalInvestorsBuySellWide｜三大法人買賣超（寬表）　`F`（驗證落地 2010~）
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2012-05-02（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| Foreign_Investor_buy | 外資買進 | 金融 | NUMERIC |
| Foreign_Investor_sell | 外資賣出 | 金融 | NUMERIC |
| Foreign_Dealer_Self_buy | 外資自營買進 | 金融 | NUMERIC |
| Foreign_Dealer_Self_sell | 外資自營賣出 | 金融 | NUMERIC |
| Investment_Trust_buy | 投信買進 | 金融 | NUMERIC |
| Investment_Trust_sell | 投信賣出 | 金融 | NUMERIC |
| Dealer_buy | 自營商買進 | 金融 | NUMERIC |
| Dealer_sell | 自營商賣出 | 金融 | NUMERIC |
| Dealer_self_buy | 自營商自行買賣買進 | 金融 | NUMERIC |
| Dealer_self_sell | 自營商自行買賣賣出 | 金融 | NUMERIC |
| Dealer_Hedging_buy | 自營商避險買進 | 金融 | NUMERIC |
| Dealer_Hedging_sell | 自營商避險賣出 | 金融 | NUMERIC |

### TaiwanStockDayTradingBorrowingFeeRate｜當沖借券費率　`B`（驗證落地 2021~）
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2015-10-14（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| stock_name | 股票名稱 | 金融 | VARCHAR |
| InvestorBorrowedShares | 投資人借券張數 | 金融 | NUMERIC |
| InvestorBorrowingFeeRate | 投資人借券費率 | 金融 | NUMERIC |

## 三、基本面（Fundamental，12 表）

### TaiwanStockFinancialStatements｜綜合損益表　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 1991-12-31（DB）
> 長表：`type` 欄存會計科目、`value` 存金額。**科目中文有 FinMind 官方**（`/translation`，如 EPS=每股盈餘、OperatingCosts=營業成本合計）。

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 資料日期（季底）| 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| type | 會計科目（值見 `/translation`）| FM | VARCHAR |
| value | 科目金額 | 金融 | NUMERIC |
| origin_name | 原始科目名稱 | 金融 | VARCHAR |

### TaiwanStockBalanceSheet｜資產負債表　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2012-03-31（DB）
> 長表同上；科目中文 FinMind 官方（應付帳款／應收帳款淨額…）。

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 資料日期（季底）| 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| type | 會計科目（值見 `/translation`）| FM | VARCHAR |
| value | 科目金額 | 金融 | NUMERIC |
| origin_name | 原始科目名稱 | 金融 | VARCHAR |

### TaiwanStockCashFlowsStatement｜現金流量表　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2012-03-31（DB）
> 長表同上；科目中文 FinMind 官方（攤銷費用／期初現金及約當現金餘額…）。

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 資料日期（季底）| 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| type | 會計科目（值見 `/translation`）| FM | VARCHAR |
| value | 科目金額 | 金融 | NUMERIC |
| origin_name | 原始科目名稱 | 金融 | VARCHAR |

### TaiwanStockDividend｜股利政策　`F(id)`（22 欄）
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2005-06-19（實證）
> ⭐ 含 anti-leakage 公告時點欄（AnnouncementDate/Time）；FinMind `/translation` 對部分欄名有官方中文。

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 資料日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| year | 股利所屬年度 | 金融 | VARCHAR |
| StockEarningsDistribution | 盈餘配股 | 金融 | NUMERIC |
| StockStatutorySurplus | 法定盈餘公積配股 | 金融 | NUMERIC |
| StockExDividendTradingDate | 除權交易日 | FM | DATE |
| TotalEmployeeStockDividend | 員工配股總額 | 金融 | NUMERIC |
| TotalEmployeeStockDividendAmount | 員工配股金額 | 金融 | NUMERIC |
| RatioOfEmployeeStockDividendOfTotal | 員工配股占盈餘比率 | 金融 | NUMERIC |
| RatioOfEmployeeStockDividend | 員工配股率 | 金融 | NUMERIC |
| CashEarningsDistribution | 盈餘配息（現金股利）| 金融 | NUMERIC |
| CashStatutorySurplus | 法定盈餘公積配息 | 金融 | NUMERIC |
| CashExDividendTradingDate | 除息交易日 | FM | DATE |
| CashDividendPaymentDate | 現金股利發放日 | FM | DATE |
| TotalEmployeeCashDividend | 員工現金紅利總額 | 金融 | NUMERIC |
| TotalNumberOfCashCapitalIncrease | 現金增資總股數 | 金融 | NUMERIC |
| CashIncreaseSubscriptionRate | 現金增資認購率 | 金融 | NUMERIC |
| CashIncreaseSubscriptionpRrice | 現金增資認購價 | 金融 | NUMERIC |
| RemunerationOfDirectorsAndSupervisors | 董監事酬勞 | 金融 | NUMERIC |
| ParticipateDistributionOfTotalShares | 參與分配總股數 | 金融 | NUMERIC |
| AnnouncementDate | 公告日期 ⭐ | FM | DATE |
| AnnouncementTime | 公告時間 ⭐ | FM | VARCHAR |

### TaiwanStockDividendResult｜除權除息結果　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2005-05-19（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 除權息日 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| before_price | 除權息前參考價 | 金融 | NUMERIC |
| after_price | 除權息後參考價 | 金融 | NUMERIC |
| stock_and_cache_dividend | 配股配息合計 | 金融 | NUMERIC |

### TaiwanStockMonthRevenue｜月營收　`F(id)`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2002-02-01（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 資料日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| revenue | 當月營收（千元）| 金融 | NUMERIC |
| revenue_month | 營收月份 | 金融 | NUMERIC |
| revenue_year | 營收年度 | 金融 | NUMERIC |

### TaiwanStockCapitalReductionReferencePrice｜減資恢復買賣參考價　`F`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2011-01-25（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 恢復買賣日 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| PostReductionReferencePrice | 減資後參考價 | 金融 | NUMERIC |
| ReasonforCapitalReduction | 減資原因 | 金融 | VARCHAR |

### TaiwanStockMarketValue｜股價市值　`B`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2004-02-12（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 資料日期 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| market_value | 市值（元）| 金融 | NUMERIC |

### TaiwanStockDelisting｜下市櫃　`F`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2001-01-20（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 下市櫃日 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| stock_name | 股票名稱 | 金融 | VARCHAR |

### TaiwanStockMarketValueWeight｜市值比重　`B`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2024-10-30（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| rank | 排名 | 金融 | NUMERIC |
| stock_id | 股票代號 | 金融 | VARCHAR |
| stock_name | 股票名稱 | 金融 | VARCHAR |
| weight_per | 市值權重（%）| 金融 | NUMERIC |
| date | 資料日期 | 金融 | DATE |
| type | 類別（上市/上櫃）| 金融 | VARCHAR |

### TaiwanStockSplitPrice｜分割後參考價　`F`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2020-08-17（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 分割恢復買賣日 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| type | 類別 | 金融 | VARCHAR |
| before_price | 分割前參考價 | 金融 | NUMERIC |
| after_price | 分割後參考價 | 金融 | NUMERIC |

### TaiwanStockParValueChange｜變更面額恢復買賣參考價　`F`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2020-08-17（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 恢復買賣日 | 金融 | DATE |
| stock_id | 股票代號 | 金融 | VARCHAR |
| stock_name | 股票名稱 | 金融 | VARCHAR |
| before_close | 變更前收盤價 | 金融 | NUMERIC |
| after_ref_close | 變更後參考收盤價 | 金融 | NUMERIC |

---

## 四、衍生品（Derivative，16 表）

### TaiwanFutOptDailyInfo｜期貨選擇權總覽　`F`
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 —（總覽無 date 欄）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| code | 代號 | 金融 | VARCHAR |
| type | 商品類別（期貨/選擇權）| 金融 | VARCHAR |
| name | 商品名稱 | 金融 | VARCHAR |

### TaiwanFuturesDaily｜期貨日成交　`F(id)`
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 1998-08-03（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| futures_id | 期貨代號 | 金融 | VARCHAR |
| contract_date | 契約月份（含價差如 200710/200711、週合約如 201211W4）| 金融 | VARCHAR |
| open | 開盤價 | 金融 | NUMERIC |
| max | 最高價 | 金融 | NUMERIC |
| min | 最低價 | 金融 | NUMERIC |
| close | 收盤價 | 金融 | NUMERIC |
| spread | 漲跌價差 | 金融 | NUMERIC |
| spread_per | 漲跌幅(%) | 金融 | NUMERIC |
| volume | 成交量(口) | 金融 | NUMERIC |
| settlement_price | 結算價 | 金融 | NUMERIC |
| open_interest | 未平倉量 | 金融 | NUMERIC |
| trading_session | 交易時段(日盤/夜盤) | 金融 | VARCHAR |

### TaiwanOptionDaily｜選擇權日成交　`F(id)`
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 2002-01-02（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| option_id | 選擇權代號 | 金融 | VARCHAR |
| contract_date | 契約月份（含價差、週合約如 201211W4）| 金融 | VARCHAR |
| strike_price | 履約價 | 金融 | NUMERIC |
| call_put | 買權賣權(Call買權/Put賣權) | 金融 | VARCHAR |
| open | 開盤價 | 金融 | NUMERIC |
| max | 最高價 | 金融 | NUMERIC |
| min | 最低價 | 金融 | NUMERIC |
| close | 收盤價 | 金融 | NUMERIC |
| volume | 成交量(口) | 金融 | NUMERIC |
| settlement_price | 結算價 | 金融 | NUMERIC |
| open_interest | 未平倉量 | 金融 | NUMERIC |
| trading_session | 交易時段(日盤/夜盤) | 金融 | VARCHAR |

### TaiwanFuturesInstitutionalInvestors｜期貨三大法人　`F(id)`
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 2018-06-05（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| futures_id | 期貨代號 | 金融 | VARCHAR |
| date | 日期 | 金融 | DATE |
| institutional_investors | 法人別 | 金融 | VARCHAR |
| long_deal_volume | 多方成交量 | 金融 | NUMERIC |
| long_deal_amount | 多方成交金額 | 金融 | NUMERIC |
| short_deal_volume | 空方成交量 | 金融 | NUMERIC |
| short_deal_amount | 空方成交金額 | 金融 | NUMERIC |
| long_open_interest_balance_volume | 多方未平倉餘額量 | 金融 | NUMERIC |
| long_open_interest_balance_amount | 多方未平倉餘額金額 | 金融 | NUMERIC |
| short_open_interest_balance_volume | 空方未平倉餘額量 | 金融 | NUMERIC |
| short_open_interest_balance_amount | 空方未平倉餘額金額 | 金融 | NUMERIC |

### TaiwanOptionInstitutionalInvestors｜選擇權三大法人　`F(id)`
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 2018-06-05（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| option_id | 選擇權代號 | 金融 | VARCHAR |
| date | 日期 | 金融 | DATE |
| call_put | 買權賣權(Call買權/Put賣權) | 金融 | VARCHAR |
| institutional_investors | 法人別 | 金融 | VARCHAR |
| long_deal_volume | 多方成交量 | 金融 | NUMERIC |
| long_deal_amount | 多方成交金額 | 金融 | NUMERIC |
| short_deal_volume | 空方成交量 | 金融 | NUMERIC |
| short_deal_amount | 空方成交金額 | 金融 | NUMERIC |
| long_open_interest_balance_volume | 多方未平倉餘額量 | 金融 | NUMERIC |
| long_open_interest_balance_amount | 多方未平倉餘額金額 | 金融 | NUMERIC |
| short_open_interest_balance_volume | 空方未平倉餘額量 | 金融 | NUMERIC |
| short_open_interest_balance_amount | 空方未平倉餘額金額 | 金融 | NUMERIC |

### TaiwanFuturesDealerTradingVolumeDaily｜期貨各券商每日交易　`F`
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 2020-07-01（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| dealer_code | 券商代號 | 金融 | VARCHAR |
| dealer_name | 券商名稱 | 金融 | VARCHAR |
| futures_id | 期貨代號 | 金融 | VARCHAR |
| volume | 成交量(口) | 金融 | NUMERIC |
| is_after_hour | 是否盤後（夜盤）| 金融 | VARCHAR |

### TaiwanOptionDealerTradingVolumeDaily｜選擇權各券商每日交易　`F`
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 2020-07-01（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| dealer_code | 券商代號 | 金融 | VARCHAR |
| dealer_name | 券商名稱 | 金融 | VARCHAR |
| option_id | 選擇權代號 | 金融 | VARCHAR |
| volume | 成交量(口) | 金融 | NUMERIC |
| is_after_hour | 是否盤後（夜盤）| 金融 | VARCHAR |

### TaiwanFuturesOpenInterestLargeTraders｜期貨大額交易人未沖銷　`B`（21 欄）
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 2007-01-02（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| name | 商品名稱 | 金融 | VARCHAR |
| contract_type | 契約類別（所有契約/近月契約）| 金融 | VARCHAR |
| buy_top5_trader_open_interest | 前5大交易人買方未平倉 | 金融 | NUMERIC |
| buy_top5_trader_open_interest_per | 前5大交易人買方未平倉占比(%) | 金融 | NUMERIC |
| buy_top10_trader_open_interest | 前10大交易人買方未平倉 | 金融 | NUMERIC |
| buy_top10_trader_open_interest_per | 前10大交易人買方未平倉占比(%) | 金融 | NUMERIC |
| sell_top5_trader_open_interest | 前5大交易人賣方未平倉 | 金融 | NUMERIC |
| sell_top5_trader_open_interest_per | 前5大交易人賣方未平倉占比(%) | 金融 | NUMERIC |
| sell_top10_trader_open_interest | 前10大交易人賣方未平倉 | 金融 | NUMERIC |
| sell_top10_trader_open_interest_per | 前10大交易人賣方未平倉占比(%) | 金融 | NUMERIC |
| market_open_interest | 全市場未平倉量 | 金融 | NUMERIC |
| buy_top5_specific_open_interest | 前5大特定法人買方未平倉 | 金融 | NUMERIC |
| buy_top5_specific_open_interest_per | 前5大特定法人買方未平倉占比(%) | 金融 | NUMERIC |
| buy_top10_specific_open_interest | 前10大特定法人買方未平倉 | 金融 | NUMERIC |
| buy_top10_specific_open_interest_per | 前10大特定法人買方未平倉占比(%) | 金融 | NUMERIC |
| sell_top5_specific_open_interest | 前5大特定法人賣方未平倉 | 金融 | NUMERIC |
| sell_top5_specific_open_interest_per | 前5大特定法人賣方未平倉占比(%) | 金融 | NUMERIC |
| sell_top10_specific_open_interest | 前10大特定法人賣方未平倉 | 金融 | NUMERIC |
| sell_top10_specific_open_interest_per | 前10大特定法人賣方未平倉占比(%) | 金融 | NUMERIC |
| date | 日期 | 金融 | DATE |
| futures_id | 期貨代號 | 金融 | VARCHAR |

### TaiwanOptionOpenInterestLargeTraders｜選擇權大額交易人未沖銷　`B`（22 欄）
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 2007-01-02（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| contract_type | 契約類別（所有契約/近月契約）| 金融 | VARCHAR |
| buy_top5_trader_open_interest | 前5大交易人買方未平倉 | 金融 | NUMERIC |
| buy_top5_trader_open_interest_per | 前5大交易人買方未平倉占比(%) | 金融 | NUMERIC |
| buy_top10_trader_open_interest | 前10大交易人買方未平倉 | 金融 | NUMERIC |
| buy_top10_trader_open_interest_per | 前10大交易人買方未平倉占比(%) | 金融 | NUMERIC |
| sell_top5_trader_open_interest | 前5大交易人賣方未平倉 | 金融 | NUMERIC |
| sell_top5_trader_open_interest_per | 前5大交易人賣方未平倉占比(%) | 金融 | NUMERIC |
| sell_top10_trader_open_interest | 前10大交易人賣方未平倉 | 金融 | NUMERIC |
| sell_top10_trader_open_interest_per | 前10大交易人賣方未平倉占比(%) | 金融 | NUMERIC |
| market_open_interest | 全市場未平倉量 | 金融 | NUMERIC |
| buy_top5_specific_open_interest | 前5大特定法人買方未平倉 | 金融 | NUMERIC |
| buy_top5_specific_open_interest_per | 前5大特定法人買方未平倉占比(%) | 金融 | NUMERIC |
| buy_top10_specific_open_interest | 前10大特定法人買方未平倉 | 金融 | NUMERIC |
| buy_top10_specific_open_interest_per | 前10大特定法人買方未平倉占比(%) | 金融 | NUMERIC |
| sell_top5_specific_open_interest | 前5大特定法人賣方未平倉 | 金融 | NUMERIC |
| sell_top5_specific_open_interest_per | 前5大特定法人賣方未平倉占比(%) | 金融 | NUMERIC |
| sell_top10_specific_open_interest | 前10大特定法人賣方未平倉 | 金融 | NUMERIC |
| sell_top10_specific_open_interest_per | 前10大特定法人賣方未平倉占比(%) | 金融 | NUMERIC |
| date | 日期 | 金融 | DATE |
| put_call | 買權賣權(Call買權/Put賣權) | 金融 | VARCHAR |
| name | 商品名稱 | 金融 | VARCHAR |
| option_id | 選擇權代號 | 金融 | VARCHAR |

### TaiwanFuturesSpreadTrading｜期貨價差行情　`B`
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 2007-10-08（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| futures_id | 期貨代號 | 金融 | VARCHAR |
| contract_date | 契約月份（含價差/週合約）| 金融 | VARCHAR |
| open | 開盤價 | 金融 | NUMERIC |
| max | 最高價 | 金融 | NUMERIC |
| min | 最低價 | 金融 | NUMERIC |
| close | 收盤價 | 金融 | NUMERIC |
| best_bid | 最佳買價 | 金融 | NUMERIC |
| best_ask | 最佳賣價 | 金融 | NUMERIC |
| historical_max | 歷史最高價 | 金融 | NUMERIC |
| historical_min | 歷史最低價 | 金融 | NUMERIC |
| spread_to_spread_volume | 價差對價差成交量 | 金融 | NUMERIC |
| spread_to_single_volume | 價差對單式成交量 | 金融 | NUMERIC |
| trading_session | 交易時段(日盤/夜盤) | 金融 | VARCHAR |

### TaiwanFuturesFinalSettlementPrice｜期貨最後結算價　`B`
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 1998-09-17（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| contract_month | 結算月份（含週合約如 202101W1）| 金融 | VARCHAR |
| futures_type | 期貨類別 | 金融 | VARCHAR |
| futures_id | 期貨代號 | 金融 | VARCHAR |
| futures_name | 期貨名稱 | 金融 | VARCHAR |
| settlement_price | 結算價 | 金融 | NUMERIC |
| underlying_code | 標的代號 | 金融 | VARCHAR |
| notional_value | 契約價值 | 金融 | NUMERIC |

### TaiwanOptionFinalSettlementPrice｜選擇權最後結算價　`B`
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 2002-01-17（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| contract_month | 結算月份（含週合約）| 金融 | VARCHAR |
| option_type | 選擇權類別 | 金融 | VARCHAR |
| option_id | 選擇權代號 | 金融 | VARCHAR |
| option_name | 選擇權名稱 | 金融 | VARCHAR |
| settlement_price | 結算價 | 金融 | NUMERIC |
| underlying_code | 標的代號 | 金融 | VARCHAR |
| notional_value | 契約價值 | 金融 | NUMERIC |

---

### TaiwanFutOptInstitutionalInvestors｜期貨選擇權三大法人（合併）　`F`（驗證落地 2018~）
> 🔌 by-date 全市場（免 data_id）· `/data` · 📅 最早 2018-01-02（驗證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| name | 商品名稱 | 金融 | VARCHAR |
| date | 日期 | 金融 | DATE |
| institutional_investors | 法人別 | 金融 | VARCHAR |
| long_deal_volume | 多方交易口數 | 金融 | NUMERIC |
| long_deal_amount | 多方交易金額 | 金融 | NUMERIC |
| short_deal_volume | 空方交易口數 | 金融 | NUMERIC |
| short_deal_amount | 空方交易金額 | 金融 | NUMERIC |
| long_open_interest_balance_volume | 多方未平倉口數 | 金融 | NUMERIC |
| long_open_interest_balance_amount | 多方未平倉金額 | 金融 | NUMERIC |
| short_open_interest_balance_volume | 空方未平倉口數 | 金融 | NUMERIC |
| short_open_interest_balance_amount | 空方未平倉金額 | 金融 | NUMERIC |

### TaiwanFuturesInstitutionalInvestorsAfterHours｜期貨三大法人（夜盤）　`B`（驗證落地 2024~）
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 2021-10-12（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| futures_id | 期貨代號 | 金融 | VARCHAR |
| date | 日期 | 金融 | DATE |
| institutional_investors | 法人別 | 金融 | VARCHAR |
| long_deal_volume | 多方交易口數 | 金融 | NUMERIC |
| long_deal_amount | 多方交易金額 | 金融 | NUMERIC |
| short_deal_volume | 空方交易口數 | 金融 | NUMERIC |
| short_deal_amount | 空方交易金額 | 金融 | NUMERIC |

### TaiwanOptionInstitutionalInvestorsAfterHours｜選擇權三大法人（夜盤）　`B`（驗證落地 2024~）
> 🔌 by-date 全市場（免 data_id）或 data_id=契約碼（`/datalist`）· `/data` · 📅 最早 2021-10-12（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| option_id | 選擇權代號 | 金融 | VARCHAR |
| date | 日期 | 金融 | DATE |
| call_put | 買權賣權(Call/Put) | 金融 | VARCHAR |
| institutional_investors | 法人別 | 金融 | VARCHAR |
| long_deal_volume | 多方交易口數 | 金融 | NUMERIC |
| long_deal_amount | 多方交易金額 | 金融 | NUMERIC |
| short_deal_volume | 空方交易口數 | 金融 | NUMERIC |
| short_deal_amount | 空方交易金額 | 金融 | NUMERIC |

### TaiwanFuturesSpreadTick｜期貨價差逐筆(Tick)　`B`（驗證落地 近期）
> 🔌 single-day tick：需 data_id 或 by-date 單日（僅近期、無歷史回補）· `/data` · 📅 最早 2026-06（tick僅近期·驗證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| time | 時間 | 金融 | VARCHAR |
| futures_id | 期貨代號 | 金融 | VARCHAR |
| contract_date | 契約月份 | 金融 | VARCHAR |
| near_price | 近月價 | 金融 | NUMERIC |
| far_price | 遠月價 | 金融 | NUMERIC |
| price | 價差價 | 金融 | NUMERIC |
| spread_to_spread | 價差對價差 | 金融 | NUMERIC |
| volume | 成交量 | 金融 | NUMERIC |

## 五、即時（Real-Time，4 表，Sponsor）— augur #4 排除（intraday），不落地
`taiwan_stock_tick_snapshot`（即時資訊，data_id 含 91 指數）· `TaiwanFutOptTickInfo`（期權即時總覽）· `taiwan_futures_snapshot`（期貨即時）· `taiwan_options_snapshot`（選擇權即時）。欄位見 datasets.md；augur 不抓（非日頻、非預測單位）。

---

### TaiwanFutOptTickInfo｜期貨選擇權即時總覽　`S`（驗證落地 —）
> 🔌 real-time snapshot（專屬端點 · Sponsor）· augur 排除 · 📅 最早 —（即時·/data無）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| (real-time，`/data` 未回資料；欄依 datasets.md) | — | — | — |
| code | 商品代號 | 金融 | VARCHAR |
| callput | 買賣權 | 金融 | VARCHAR |
| date | 日期 | 金融 | DATE |
| name | 商品名稱 | 金融 | VARCHAR |

## 六、可轉債（Convertible Bond，4 表，Backer）

### TaiwanStockConvertibleBondInfo｜可轉債總覽　`B`
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 —（總覽 1788 檔）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| cb_id | 可轉債代號 | 金融 | VARCHAR |
| cb_name | 可轉債名稱 | 金融 | VARCHAR |
| InitialDateOfConversion | 可轉換起日 | 金融 | DATE |
| DueDateOfConversion | 可轉換迄日 | 金融 | DATE |
| IssuanceAmount | 發行總額 | 金融 | NUMERIC |

### TaiwanStockConvertibleBondDaily｜可轉債日成交　`B`
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 2024-12-10（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| cb_id | 可轉債代號 | 金融 | VARCHAR |
| cb_name | 可轉債名稱 | 金融 | VARCHAR |
| transaction_type | 交易類別 | 金融 | VARCHAR |
| close | 收盤價 | 金融 | NUMERIC |
| change | 漲跌 | 金融 | NUMERIC |
| open | 開盤價 | 金融 | NUMERIC |
| max | 最高價 | 金融 | NUMERIC |
| min | 最低價 | 金融 | NUMERIC |
| no_of_transactions | 成交筆數 | 金融 | NUMERIC |
| unit | 成交張數 | 金融 | NUMERIC |
| trading_value | 成交值 | 金融 | NUMERIC |
| avg_price | 均價 | 金融 | NUMERIC |
| next_ref_price | 次日參考價 | 金融 | NUMERIC |
| next_max_limit | 次日漲停價 | 金融 | NUMERIC |
| next_min_limit | 次日跌停價 | 金融 | NUMERIC |
| date | 日期 | 金融 | DATE |

### TaiwanStockConvertibleBondInstitutionalInvestors｜可轉債三大法人　`B`
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 2024-12-10（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| Foreign_Investor_Buy | 外資買進 | 金融 | NUMERIC |
| Foreign_Investor_Sell | 外資賣出 | 金融 | NUMERIC |
| Foreign_Investor_Overbuy | 外資買超 | 金融 | NUMERIC |
| Investment_Trust_Buy | 投信買進 | 金融 | NUMERIC |
| Investment_Trust_Sell | 投信賣出 | 金融 | NUMERIC |
| Investment_Trust_Overbuy | 投信買超 | 金融 | NUMERIC |
| Dealer_self_Buy | 自營商買進 | 金融 | NUMERIC |
| Dealer_self_Sell | 自營商賣出 | 金融 | NUMERIC |
| Dealer_self_Overbuy | 自營商買超 | 金融 | NUMERIC |
| Total_Overbuy | 合計買超 | 金融 | NUMERIC |
| cb_id | 可轉債代號 | 金融 | VARCHAR |
| cb_name | 可轉債名稱 | 金融 | VARCHAR |
| date | 日期 | 金融 | DATE |

### TaiwanStockConvertibleBondDailyOverview｜可轉債每日總覽　`B`（23 欄）
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 2024-12-10（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| cb_id | 可轉債代號 | 金融 | VARCHAR |
| cb_name | 可轉債名稱 | 金融 | VARCHAR |
| date | 日期 | 金融 | DATE |
| InitialDateOfConversion | 可轉換起日 | 金融 | DATE |
| DueDateOfConversion | 可轉換迄日 | 金融 | DATE |
| InitialDateOfStopConversion | 停止轉換起日 | 金融 | VARCHAR |
| DueDateOfStopConversion | 停止轉換迄日 | 金融 | VARCHAR |
| ConversionPrice | 轉換價格 | 金融 | NUMERIC |
| NextEffectiveDateOfConversionPrice | 次一轉換價生效日 | 金融 | DATE |
| LatestInitialDateOfPut | 最近賣回權起日 | 金融 | DATE |
| LatestDueDateOfPut | 最近賣回權迄日 | 金融 | DATE |
| LatestPutPrice | 最近賣回價格 | 金融 | NUMERIC |
| InitialDateOfEarlyRedemption | 提前贖回起日 | 金融 | DATE |
| DueDateOfEarlyRedemption | 提前贖回迄日 | 金融 | DATE |
| EarlyRedemptionPrice | 提前贖回價格 | 金融 | NUMERIC |
| DateOfDelisted | 下市日期 | 金融 | DATE |
| IssuanceAmount | 發行總額 | 金融 | NUMERIC |
| OutstandingAmount | 流通餘額 | 金融 | NUMERIC |
| ReferencePrice | 參考價格 | 金融 | NUMERIC |
| PriceOfUnderlyingStock | 標的股票價格 | 金融 | NUMERIC |
| InitialDateOfSuspension | 暫停交易起日 | 金融 | VARCHAR |
| DueDateOfSuspension | 暫停交易迄日 | 金融 | VARCHAR |
| CouponRate | 票面利率 | 金融 | NUMERIC |

---

## 七、其他（Others，3 表）

### TaiwanStockNews｜相關新聞　`F`（單日型 end_date 須 none）
> 🔌 single-day（end_date 須 none）· `/data` · 📅 最早 2010-03-02（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | VARCHAR |
| stock_id | 股票代號 | 金融 | VARCHAR |
| link | 連結 | 金融 | TEXT |
| source | 來源 | 金融 | VARCHAR |
| title | 標題 | 金融 | VARCHAR |

### TaiwanBusinessIndicator｜景氣對策信號　`B`
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 1990-01-01（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| leading | 領先指標 | 金融 | NUMERIC |
| leading_notrend | 領先指標（不含趨勢）| 金融 | NUMERIC |
| coincident | 同時指標 | 金融 | NUMERIC |
| coincident_notrend | 同時指標（不含趨勢）| 金融 | NUMERIC |
| lagging | 落後指標 | 金融 | NUMERIC |
| lagging_notrend | 落後指標（不含趨勢）| 金融 | NUMERIC |
| monitoring | 景氣對策信號 | 金融 | NUMERIC |
| monitoring_color | 信號燈號 | 金融 | VARCHAR |

### TaiwanStockIndustryChain｜產業鏈　`B`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2026-06-12（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| stock_id | 股票代號 | 金融 | VARCHAR |
| industry | 產業 | 金融 | VARCHAR |
| sub_industry | 次產業 | 金融 | VARCHAR |
| date | 日期 | 金融 | DATE |

---

## 八、國際股（International，8 表，皆 Free）

### USStockInfo｜美股總覽　`F`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2024-05-06（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 代號 | 金融 | VARCHAR |
| Country | 國家 | 金融 | VARCHAR |
| IPOYear | 上市年度 | 金融 | NUMERIC |
| MarketCap | 市值 | 金融 | NUMERIC |
| Subsector | 次產業別 | 金融 | VARCHAR |
| stock_name | 名稱 | 金融 | VARCHAR |

### USStockPrice｜美股股價　`F`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 1990-01-02（DB）
> stock_id 指數對照（FM `/translation`）：`^DJI`=道瓊工業指數、`^GSPC`=S&P500、`^IXIC`=那斯達克工業指數、`^SOX`=費城半導體指數、`^VIX`=VIX。

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 代號 | 金融 | VARCHAR |
| Adj_Close | 還原收盤價 | 金融 | NUMERIC |
| Close | 收盤價 | 金融 | NUMERIC |
| High | 最高價 | 金融 | NUMERIC |
| Low | 最低價 | 金融 | NUMERIC |
| Open | 開盤價 | 金融 | NUMERIC |
| Volume | 成交量 | 金融 | NUMERIC |

### UKStockInfo｜英股總覽　`F`（probe failed，欄依 datasets.md）
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 2019-01-31（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 代號 | 金融 | VARCHAR |
| Country | 國家 | 金融 | VARCHAR |
| stock_name | 名稱 | 金融 | VARCHAR |

### UKStockPrice｜英股股價　`F`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 1990-01-01（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 代號 | 金融 | VARCHAR |
| Adj_Close | 還原收盤價 | 金融 | NUMERIC |
| Close | 收盤價 | 金融 | NUMERIC |
| High | 最高價 | 金融 | NUMERIC |
| Low | 最低價 | 金融 | NUMERIC |
| Open | 開盤價 | 金融 | NUMERIC |
| Volume | 成交量 | 金融 | NUMERIC |

### EuropeStockInfo｜歐股總覽　`F`（probe failed，欄依 datasets.md）
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 2019-01-14（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 代號 | 金融 | VARCHAR |
| Market | 市場 | 金融 | VARCHAR |
| stock_name | 名稱 | 金融 | VARCHAR |

### EuropeStockPrice｜歐股股價　`F`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 1990-01-01（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 代號 | 金融 | VARCHAR |
| Adj_Close | 還原收盤價 | 金融 | NUMERIC |
| Close | 收盤價 | 金融 | NUMERIC |
| High | 最高價 | 金融 | NUMERIC |
| Low | 最低價 | 金融 | NUMERIC |
| Open | 開盤價 | 金融 | NUMERIC |
| Volume | 成交量 | 金融 | NUMERIC |

### JapanStockInfo｜日股總覽　`F`（probe failed，欄依 datasets.md）
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 2019-01-14（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 代號 | 金融 | VARCHAR |
| Exchange | 交易所 | 金融 | VARCHAR |
| Sector | 產業別 | 金融 | VARCHAR |
| stock_name | 名稱 | 金融 | VARCHAR |

### JapanStockPrice｜日股股價　`F`
> 🔌 per-stock（roster id）或 by-date 全市場（Sponsor 免 id）· `/data` · 📅 最早 2001-01-01（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 日期 | 金融 | DATE |
| stock_id | 代號 | 金融 | VARCHAR |
| Adj_Close | 還原收盤價 | 金融 | NUMERIC |
| Close | 收盤價 | 金融 | NUMERIC |
| High | 最高價 | 金融 | NUMERIC |
| Low | 最低價 | 金融 | NUMERIC |
| Open | 開盤價 | 金融 | NUMERIC |
| Volume | 成交量 | 金融 | NUMERIC |

---

## 九、全球總經（Macro，7 表，皆 Free）

### TaiwanExchangeRate｜外幣匯率　`F`　data_id=幣別（USD/EUR/JPY…18-19 種，`/datalist`）
> 🔌 by-dimension-id：data_id=維度碼（來源 `/datalist`）· `/data` · 📅 最早 2006-01-02（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 資料日期 | 金融 | DATE |
| currency | 幣別 | 金融 | VARCHAR |
| cash_buy | 現金買入匯率 | 金融 | NUMERIC |
| cash_sell | 現金賣出匯率 | 金融 | NUMERIC |
| spot_buy | 即期買入匯率 | 金融 | NUMERIC |
| spot_sell | 即期賣出匯率 | 金融 | NUMERIC |

### InterestRate｜央行利率　`F`　data_id=央行碼（FED/ECB/BOJ…12 行，`/datalist`）
> 🔌 by-dimension-id：data_id=維度碼（來源 `/datalist`）· `/data` · 📅 最早 2008-02-01（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| country | 國家／央行 | 金融 | VARCHAR |
| date | 資料日期 | 金融 | DATE |
| interest_rate | 政策利率（%）| 金融 | NUMERIC |

### GoldPrice｜黃金價格　`F`
> 🔌 market 單批（無 data_id）· `/data` · 📅 最早 1990-01-01（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| Price | 金價 | 金融 | NUMERIC |
| date | 資料日期 | 金融 | DATE |

### CrudeOilPrices｜原油價格　`F`　data_id=WTI/Brent（`/datalist`）
> 🔌 by-dimension-id：data_id=維度碼（來源 `/datalist`）· `/data` · 📅 最早 1990-01-02（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 資料日期 | 金融 | DATE |
| name | 油種名稱（WTI/Brent）| 金融 | VARCHAR |
| price | 油價（美元/桶）| 金融 | NUMERIC |

### GovernmentBondsYield｜美國國債殖利率　`F`　data_id=期別（1M~30Y，13 期別，`/datalist`）
> 🔌 by-dimension-id：data_id=維度碼（來源 `/datalist`）· `/data` · 📅 最早 2001-01-02（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 資料日期 | 金融 | DATE |
| name | 期別名稱（如 United States 10-Year）| 金融 | VARCHAR |
| value | 殖利率（%）| 金融 | NUMERIC |

### CnnFearGreedIndex｜CNN 恐懼貪婪指數　`B`
> 🔌 market 單批（無 data_id）或 by-date · `/data` · 📅 最早 2011-01-03（DB）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| date | 資料日期 | 金融 | DATE |
| fear_greed | 恐懼貪婪指數（0-100）| 金融 | NUMERIC |
| fear_greed_emotion | 情緒分類（極度恐懼…極度貪婪）| 金融 | VARCHAR |

---

### ExchangeRate｜外幣匯率（銀行間 by 國家）　`F`（驗證落地 2010~）
> 🔌 by-dimension-id：data_id=維度碼（來源 `/datalist`）· `/data` · 📅 最早 1990-01-02（實證）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| country | 國家／幣別 | 金融 | VARCHAR |
| date | 日期 | 金融 | DATE |
| InterbankRate | 銀行間匯率 | 金融 | NUMERIC |
| InverseInterbankRate | 反向銀行間匯率 | 金融 | NUMERIC |

## 十、FRED（Federal Reserve Economic Data，第二資料源）

FRED `/series/observations` 每列 `realtime_start, realtime_end, date, value`；augur `fred.py` 落地 `(series_id, date, realtime_start, value)`（補 series_id、`realtime_end` 隨查詢日變不存、`"."`→NULL）。⚠️ #8：FRED 值事後修訂 → **Tier B（月/季/週經濟）走 ALFRED vintage**（逐版存真 `realtime_start`、PIT 取版）、**Tier A（每日市場）`realtime_start`＝觀測日**（當日可見、非近似）。tier/清單見 `src/augur/features/macro.py`（SSOT）；技術細節見 `augur_datasource_finmind_fred_20260615.md` §B6。

### fred_series｜FRED 總經序列（augur 落地表）
> 🔌 FRED `/series/observations`（series_id+date+realtime_start+value；Tier B 走 ALFRED vintage、`.`→NULL） · 📅 最早 依 series（如 DGS10 1962）

| 欄位 (EN) | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| series_id | 序列代號 | 派生（augur 補）| VARCHAR |
| date | 觀測日期 | FRED | DATE |
| realtime_start | 版本可見起日（PIT 取版鍵）| FRED/派生 | DATE |
| value | 觀測值 | FRED | NUMERIC |

### augur 採用之 FRED series 清單
> SSOT＝`src/augur/features/macro.py`（逐檔 `series_id` + 中文 + tier A/B + 是否走 vintage；現 31 檔：Tier A 22 每日市場 + Tier B 9 月/季/週經濟）。此處不複列、以免 drift（#12 SSOT；曾因人工複列 stale 為 12 檔）。

---

> **完整度說明**：75 FinMind dataset（22 表 DB 真欄 / 48 表 probe 真欄 / 5 表 datasets.md 補）+ FRED。中文 9 個 dataset 有 FinMind 官方（`FM`），其餘金融專業用語（`金融`）。型別為 augur `generic_schema` 推導（FinMind/FRED 皆不提供型別）。配套技術報告：`augur_datasource_finmind_fred_20260615.md`。


## 補充：catalog 深探 + intraday/tick/deferred 表（金融用語策展、入 SSOT；2026-06-16 移自 code）

### InterestRate
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| full_country_name | 國家全名 | 金融 | - |

### TaiwanFutOptTickInfo
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| expire_price | 到期結算價 | 金融 | - |
| listing_date | 上市日期 | 金融 | - |
| update_date | 更新日期 | 金融 | - |

### TaiwanFuturesTick｜期貨逐筆成交

### TaiwanOptionTick｜選擇權逐筆成交
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| ExercisePrice | 履約價 | 金融 | - |
| PutCall | 買賣權別 | 金融 | - |

### TaiwanStockBlockTradingDailyReport｜鉅額交易日報表

### TaiwanStockCapitalReductionReferencePrice
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| ClosingPriceonTheLastTradingDay | 減資前最後交易日收盤價 | 金融 | - |
| ExrightReferencePrice | 除權參考價 | 金融 | - |
| LimitDown | 跌停價 | 金融 | - |
| LimitUp | 漲停價 | 金融 | - |
| OpeningReferencePrice | 開盤競價基準 | 金融 | - |

### TaiwanStockDividendResult
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| max_price | 最高價 | 金融 | - |
| min_price | 最低價 | 金融 | - |
| open_price | 開盤價 | 金融 | - |
| stock_or_cache_dividend | 股票或現金股利 | 金融 | - |

### TaiwanStockEvery5SecondsIndex｜大盤每5秒指數
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| kind | 指數類別 | 金融 | - |

### TaiwanStockKBar｜台股K棒（分鐘）
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| high | 最高價 | 金融 | - |
| low | 最低價 | 金融 | - |
| minute | 分鐘 | 金融 | - |

### TaiwanStockMonthRevenue
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| create_time | 資料建立時點 | 金融 | - |

### TaiwanStockParValueChange
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| after_ref_max | 調整後參考最高價 | 金融 | - |
| after_ref_min | 調整後參考最低價 | 金融 | - |
| after_ref_open | 調整後參考開盤價 | 金融 | - |

### TaiwanStockPriceTick｜台股逐筆成交
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| TickType | 內外盤別 | 金融 | - |
| Time | 成交時間 | 金融 | - |
| deal_price | 成交價 | 金融 | - |

### TaiwanStockSplitPrice
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| max_price | 最高價 | 金融 | - |
| min_price | 最低價 | 金融 | - |
| open_price | 開盤價 | 金融 | - |

### TaiwanStockStatisticsOfOrderBookAndTrade｜委託成交統計
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| Time | 時間 | 金融 | - |
| TotalBuyOrder | 累計委買筆數 | 金融 | - |
| TotalBuyVolume | 累計委買張數 | 金融 | - |
| TotalDealMoney | 累計成交金額 | 金融 | - |
| TotalDealOrder | 累計成交筆數 | 金融 | - |
| TotalDealVolume | 累計成交張數 | 金融 | - |
| TotalSellOrder | 累計委賣筆數 | 金融 | - |
| TotalSellVolume | 累計委賣張數 | 金融 | - |

### TaiwanStockTradingDailyReport｜券商分點進出日報

### TaiwanStockWarrantTradingDailyReport｜權證分點進出日報

### TaiwanVariousIndicators5Seconds｜大盤每5秒各項指標
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| TAIEX | 加權指數 | 金融 | - |

### USStockPriceMinute｜美股分鐘價
| 欄位 | 中文 | 來源 | 推定型別 |
|---|---|---|---|
| high | 最高價 | 金融 | - |
| low | 最低價 | 金融 | - |

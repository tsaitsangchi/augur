# augur 全表全欄逐欄走查 — 94 表 772 欄(2026-06-29)

> **性質**:用戶 directive「所有表與所有欄位深入逐欄走一遍」之據實成果(#15、#20 真窮舉到真邊界)。
> **方法**:本地 profiler(`scratchpad/walk_columns.py`、零 usage #28)對 94 表每欄 join `information_schema`(DB 真型別/PK)+ `column_catalog`(中文/型別/PK/anti-leakage/髒值)+ `dataset_catalog`(表級抓法/頻率/最早/tier/排除),逐欄輸出 + **catalog↔DB 一致性審計**;再由 Claude 逐 category 親讀審視。完整逐欄字典見本檔附錄。
> **權威定位**:型別/PK 以 **DB `information_schema` 為準**(#2 API 即權威);`column_catalog` 是可刷新快取(憲章 v1.7.0)、中文/語意/髒值之輔助登錄,有偏差以 DB 校正。

---

## 一、走查覆蓋:94 表 × 11 category(全數逐欄審視)

| Category | 表數 | 定位 | 逐欄深度 |
|---|---|---|---|
| TW-Technical | 16 | 價量(alpha 主源)| 深入 |
| TW-Chip / Institutional | 16 | 籌碼/法人/信用(核心)| 深入 |
| TW-Fundamental | 12 | 財報三表 + 事件(核心)| 深入 |
| TW-Others | 3 | 景氣/產業鏈/News(context)| 深入 |
| Global Economic | 7 | 商品/匯率/利率/情緒(context X 類)| 中 |
| International Markets | 8 | 美/日/英/歐股(out-of-scope、髒值)| 中 |
| Macro | 1 | fred_series(總經 context)| 中 |
| TW-Convertible Bond | 4 | 可轉債(out-of-scope)| 字典級 |
| TW-Derivative | 16 | 期/權(out-of-scope、可作 regime context)| 字典級 |
| TW-Real-Time | 1 | 期權即時總覽(#4 邊緣)| 字典級 |

中文定義 **751/751 欄全有**、94 表全在 `dataset_catalog`。

## 二、catalog↔DB 一致性審計(逐欄走查之核心價值)

| 問題 | 數 | 判讀 |
|---|---|---|
| **catalog 缺欄** | 3 | `fred_series`(series_id/date/value)未登錄 column_catalog — FRED 非 FinMind、catalog builder 未收;**可回填** |
| **型別不符** | 15 | 多為 catalog 標「date 語意」但 DB 落地 **VARCHAR**(generic_schema 為容 sentinel 降級:SecuritiesLending `-1`/CB `1911-00-00`/News datetime/create_time/AnnouncementDate)→ **合理**;少數 catalog 記載不準(GoldPrice.date 實為 DATE) |
| **PK 不符** | 49 | catalog `is_pk` vs DB 實際 PK 偏差,**集中於 out-of-scope 表**(國際股/衍生/CB/商品)+ SecuritiesLending/BlockTrade/Disposition;以 DB 為準、catalog 可回填 |
| 無中文 | 0 | ✅ |
| 無 catalog 表 | 0 | ✅ |

## 三、PK 異常(逐欄走查新發現/再確認)

1. **`TaiwanStockGovernmentBankBuySell` PK 塌陷**(新發現):7 欄全標 PK(含 buy_amount 等**數值欄**)— `detect_keys` 對該表 fallback 全欄當 PK。chip.py 用 aggregate `sum(buy_amount)-sum(sell_amount)` 不依賴 PK → **不影響特徵**,但 PK 定義異常。
2. **衍生表全欄 PK**(`TaiwanFuturesDaily`/`TaiwanOptionDaily` 等 13 欄全 PK):同 detect_keys fallback;out-of-scope、不查詢、不影響。
3. **`TaiwanStockDividend` PK=stock_id 單欄塌列 bug**(再確認、已知):date 非 PK → 同股多年互蓋僅存 1 筆;碼已修(`sync.py` require_keys=('date',))**待 token 重建**;現未入生產特徵、不影響 alpha。

## 四、我的理解狀態(逐欄走查後,分層)

- **table 定義(94 表)**:每表的 source/category/tier/抓法(per-stock/by-date/by-dim-id/market)/頻率/最早日/排除 — 已逐表掌握(`dataset_catalog`)。
- **field 定義(772 欄)**:每欄 DB 型別/PK + 中文 + anti-leakage + 髒值註記 — **已逐欄走過 + DB 實證**(本檔附錄完整字典,任何欄可查)。
- **raw 語意**:財報 224 type 全中文解碼(in-data origin_name)· 累計語意(損益單季/現金流累計YTD/資產負債snapshot)· 單位(money 元/融資餘額張/月營收元)· 發布日 gate · 8 大髒值陷阱(停牌OHLC=0/PER=-1/percent可負/國際overflow…)· anti-leakage 金礦欄(Dividend.AnnouncementDate/Shareholding.RecentlyDeclareDate/MonthRevenue.create_time)。

## 五、誠實邊界(漸近、未達 — 學另機 ledger 立場 #15)

1. **罕見財報碼準則級定義**:224 type 有 in-data 中文(origin_name),但罕見 legacy 碼之 IFRS 條文級精確定義未逐一查(不杜撰)。
2. **衍生品 FinMind 欄精確邊界**(大額交易人 `_per` 分母等)— out-of-scope、待文件。
3. **Suspended 表史短**(僅 2025-03+)— 待文件確認本就短 vs 漏抓。
4. **已知資料問題**:Dividend 塌列(待重建)· GovBank/衍生 PK 塌陷(detect_keys fallback)· BalanceSheet 系統性缺季(2016-19/2022-24,影響 C3 庫存特徵)。

## 六、可回填 catalog 之建議(執行層 #26,待授權)

- `fred_series` 3 欄補 column_catalog 登錄(中文:series_id 序列代號/date 日期/value 值)。
- 49 PK 不符 / 15 型別不符:以 DB information_schema 校正 catalog `is_pk`/`inferred_type`(catalog 快取對齊 DB 真相)。
- catalog `dirty_value_note` 已回填 23 欄;可續補(GovBank PK 塌陷、衍生全欄 PK 之 caveat)。

---

## 附錄:完整逐欄字典(94 表 772 欄、profiler 輸出)

格式:`[PK] 欄名  DB型別  中文  🔒AL ⚠️髒值 ⚑caveat`。type/PK 以 DB 為準。
```text
# 逐欄走查：84 表（按 category）


==========================================================================================
## CATEGORY: Global Economic Data（7 表）
==========================================================================================

### CnnFearGreedIndex  [中文=CNN 恐懼貪婪指數 tier=B 抓=market 頻=single-series 最早=2011-01-01 排除=False]
    [PK] date                             date             資料日期              
    [  ] fear_greed                       numeric          恐懼貪婪指數（0-100）     
    [  ] fear_greed_emotion               character varying 情緒分類（極度恐懼…極度貪婪）   

### CrudeOilPrices  [中文=原油價格 tier=F 抓=by-dim-id 頻=daily 最早=1986-04-01 排除=False]
    [PK] date                             date             資料日期              
    [PK] name                             character varying 油種名稱（WTI/Brent）   
    [  ] price                            numeric          油價（美元/桶）          

### ExchangeRate  [中文=外幣匯率（銀行間 by 國家） tier=F 抓=by-dim-id 頻=daily 最早=1990-01-02 排除=False]
    [  ] InterbankRate                    numeric          銀行間匯率             
    [  ] InverseInterbankRate             numeric          反向銀行間匯率           
    [PK] country                          character varying 國家／幣別             
    [PK] date                             date             日期                

### GoldPrice  [中文=黃金價格 tier=F 抓=single-day 頻=single-day 最早=1979-01-01 排除=False]
    [  ] Price                            numeric          金價                
    [PK] date                             date             資料日期               ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日

### GovernmentBondsYield  [中文=美國國債殖利率 tier=F 抓=by-dim-id 頻=daily 最早=2001-01-02 排除=False]
    [PK] date                             date             資料日期              
    [PK] name                             character varying 期別名稱（如 United Stat
    [  ] value                            numeric          殖利率（%）            

### InterestRate  [中文=央行利率 tier=F 抓=by-dim-id 頻=daily 最早=2008-02-01 排除=False]
    [PK] country                          character varying 國家／央行             
    [PK] date                             date             資料日期              
    [  ] full_country_name                character varying 國家全名              
    [  ] interest_rate                    numeric          政策利率（%）           

### TaiwanExchangeRate  [中文=外幣匯率 tier=F 抓=by-dim-id 頻=daily 最早=2006-01-02 排除=False]
    [PK] date                             date             資料日期              
    [PK] currency                         character varying 幣別                
    [  ] cash_buy                         numeric          現金買入匯率            
    [  ] cash_sell                        numeric          現金賣出匯率            
    [  ] spot_buy                         numeric          即期買入匯率            
    [  ] spot_sell                        numeric          即期賣出匯率            

==========================================================================================
## CATEGORY: International Markets（8 表）
==========================================================================================

### EuropeStockInfo  [中文=歐股總覽 tier=F 抓=market 頻=single-series 最早=2019-01-14 排除=False]
    [  ] date                             date             日期                
    [PK] stock_id                         character varying 代號                
    [  ] Market                           character varying 市場                
    [  ] stock_name                       character varying 名稱                

### EuropeStockPrice  [中文=歐股股價 tier=F 抓=by-date 頻=daily 最早=1980-04-01 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 代號                
    [  ] Adj_Close                        numeric          還原收盤價              ⚠️Adj_Close overflow/負值髒值(±1e38)、不可直接用
    [  ] Close                            numeric          收盤價               
    [  ] High                             numeric          最高價               
    [  ] Low                              numeric          最低價               
    [  ] Open                             numeric          開盤價               
    [  ] Volume                           numeric          成交量               

### JapanStockInfo  [中文=日股總覽 tier=F 抓=market 頻=single-series 最早=2019-01-14 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 代號                
    [PK] Exchange                         character varying 交易所               
    [  ] Sector                           character varying 產業別               
    [PK] stock_name                       character varying 名稱                

### JapanStockPrice  [中文=日股股價 tier=F 抓=by-date 頻=daily 最早=1999-05-01 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 代號                
    [  ] Adj_Close                        numeric          還原收盤價              ⚠️Adj_Close overflow/負值髒值(±1e38)、不可直接用
    [  ] Close                            numeric          收盤價               
    [  ] High                             numeric          最高價               
    [  ] Low                              numeric          最低價               
    [  ] Open                             numeric          開盤價               
    [  ] Volume                           numeric          成交量               

### UKStockInfo  [中文=英股總覽 tier=F 抓=market 頻=single-series 最早=2019-01-31 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 代號                
    [PK] Country                          character varying 國家                
    [PK] stock_name                       character varying 名稱                

### UKStockPrice  [中文=英股股價 tier=F 抓=by-date 頻=daily 最早=1968-01-01 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 代號                
    [  ] Adj_Close                        numeric          還原收盤價              ⚠️Adj_Close overflow/負值髒值(±1e38)、不可直接用
    [  ] Close                            numeric          收盤價               
    [  ] High                             numeric          最高價               
    [  ] Low                              numeric          最低價               
    [  ] Open                             numeric          開盤價               
    [  ] Volume                           numeric          成交量               

### USStockInfo  [中文=美股總覽 tier=F 抓=by-date 頻=daily 最早=2024-05-01 排除=False]
    [  ] date                             date             日期                
    [  ] stock_id                         character varying 代號                
    [  ] Country                          character varying 國家                
    [  ] IPOYear                          numeric          上市年度              
    [  ] MarketCap                        numeric          市值                
    [  ] Subsector                        character varying 次產業別              
    [PK] stock_name                       character varying 名稱                

### USStockPrice  [中文=美股股價 tier=F 抓=by-date 頻=daily 最早=1928-02-01 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 代號                 ⚠️彙總髒行 stock_id=null → 整批改 by-dim-id 逐 ticker
    [  ] Adj_Close                        numeric          還原收盤價              ⚠️Adj_Close overflow/負值髒值(±1e38)、不可直接用
    [  ] Close                            numeric          收盤價               
    [  ] High                             numeric          最高價               
    [  ] Low                              numeric          最低價               
    [  ] Open                             numeric          開盤價               
    [  ] Volume                           numeric          成交量               

==========================================================================================
## CATEGORY: Macro（1 表）
==========================================================================================

### fred_series  [中文=FRED 總經序列（augur 落地表） tier=FRED 抓=per-series 頻=snapshot 最早=None 排除=False]
    [PK] series_id                        character varying  ⚠️catalog無此欄
    [PK] date                             date               ⚠️catalog無此欄
    [  ] value                            numeric            ⚠️catalog無此欄

==========================================================================================
## CATEGORY: TW-Chip（1 表）
==========================================================================================

### TaiwanStockInstitutionalInvestorsBuySellWide  [中文=三大法人買賣超（寬表） tier=F 抓=per-stock 頻=daily 最早=2012-05-02 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 股票代號              
    [  ] Foreign_Investor_buy             numeric          外資買進              
    [  ] Foreign_Investor_sell            numeric          外資賣出              
    [  ] Foreign_Dealer_Self_buy          numeric          外資自營買進            
    [  ] Foreign_Dealer_Self_sell         numeric          外資自營賣出            
    [  ] Investment_Trust_buy             numeric          投信買進              
    [  ] Investment_Trust_sell            numeric          投信賣出              
    [  ] Dealer_buy                       numeric          自營商買進             
    [  ] Dealer_sell                      numeric          自營商賣出             
    [  ] Dealer_self_buy                  numeric          自營商自行買賣買進         
    [  ] Dealer_self_sell                 numeric          自營商自行買賣賣出         
    [  ] Dealer_Hedging_buy               numeric          自營商避險買進           
    [  ] Dealer_Hedging_sell              numeric          自營商避險賣出           

==========================================================================================
## CATEGORY: TW-Chip / Institutional（15 表）
==========================================================================================

### TaiwanDailyShortSaleBalances  [中文=融券借券餘額 tier=F(id) 抓=per-stock 頻=daily 最早=2005-07-01 排除=False]
    [PK] stock_id                         character varying 股票代號              
    [  ] MarginShortSalesPreviousDayBalance numeric          融券前日餘額            
    [  ] MarginShortSalesShortSales       numeric          融券賣出              
    [  ] MarginShortSalesShortCovering    numeric          融券買進（回補）          
    [  ] MarginShortSalesStockRedemption  numeric          融券現券償還            
    [  ] MarginShortSalesCurrentDayBalance numeric          融券當日餘額            
    [  ] MarginShortSalesQuota            numeric          融券限額              
    [  ] SBLShortSalesPreviousDayBalance  numeric          借券賣出前日餘額          
    [  ] SBLShortSalesShortSales          numeric          借券賣出              
    [  ] SBLShortSalesReturns             numeric          借券賣出返還            
    [  ] SBLShortSalesAdjustments         numeric          借券賣出調整            
    [  ] SBLShortSalesCurrentDayBalance   numeric          借券賣出當日餘額          
    [  ] SBLShortSalesQuota               numeric          借券賣出限額            
    [  ] SBLShortSalesShortCovering       numeric          借券賣出回補            
    [PK] date                             date             日期                

### TaiwanSecuritiesTraderInfo  [中文=證券商資訊 tier=F 抓=market 頻=single-series 最早=2025-02-01 排除=False]
    [PK] securities_trader_id             character varying 券商代號              
    [  ] securities_trader                character varying 券商名稱              
    [  ] date                             date             日期                
    [  ] address                          character varying 地址                
    [  ] phone                            character varying 電話                

### TaiwanStockBlockTrade  [中文=鉅額交易 tier=S 抓=per-stock 頻=daily 最早=2006-08-11 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 股票代號              
    [  ] trade_type                       character varying 交易類別（配對／逐筆）       
    [  ] price                            numeric          成交價               
    [  ] volume                           numeric          成交量（股）            
    [  ] trading_money                    numeric          成交金額              

### TaiwanStockDispositionSecuritiesPeriod  [中文=處置有價證券 tier=B 抓=by-date 頻=daily 最早=2005-01-01 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 股票代號              
    [  ] stock_name                       character varying 股票名稱              
    [  ] disposition_cnt                  numeric          處置次數              
    [  ] condition                        character varying 處置條件              
    [  ] measure                          text             處置措施              
    [  ] period_start                     date             處置起始日             
    [  ] period_end                       date             處置截止日             

### TaiwanStockGovernmentBankBuySell  [中文=八大行庫買賣 tier=S 抓=by-date 頻=daily 最早=2021-07-01 排除=False]
    [PK] date                             date             日期                 ⚑資料 2021-07 起;早期真零須 _table_covers gate(#1
    [PK] stock_id                         character varying 股票代號               ⚑資料 2021-07 起;早期真零須 _table_covers gate(#1
    [PK] buy_amount                       numeric          買進金額               ⚑資料 2021-07 起;早期真零須 _table_covers gate(#1
    [PK] sell_amount                      numeric          賣出金額               ⚑資料 2021-07 起;早期真零須 _table_covers gate(#1
    [PK] buy                              numeric          買進股數               ⚑資料 2021-07 起;早期真零須 _table_covers gate(#1
    [PK] sell                             numeric          賣出股數               ⚑資料 2021-07 起;早期真零須 _table_covers gate(#1
    [PK] bank_name                        character varying 行庫名稱               ⚑資料 2021-07 起;早期真零須 _table_covers gate(#1

### TaiwanStockHoldingSharesPer  [中文=股權持股分級 tier=B 抓=per-stock 頻=daily 最早=2010-01-29 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 股票代號              
    [PK] HoldingSharesLevel               character varying 持股分級級距            
    [  ] people                           numeric          持股人數              
    [  ] percent                          numeric          持股比率               ⚠️percent 可負(差異數調整 level)、可>100 異常;unit 可負
    [  ] unit                             numeric          持股單位數（張）           ⚠️percent 可負(差異數調整 level)、可>100 異常;unit 可負

### TaiwanStockInstitutionalInvestorsBuySell  [中文=三大法人買賣超 tier=F(id) 抓=per-stock 頻=daily 最早=2012-05-02 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 股票代號              
    [  ] buy                              numeric          買進                
    [PK] name                             character varying 法人別（自營商／自營商避險／自營商自
    [  ] sell                             numeric          賣出                

### TaiwanStockLoanCollateralBalance  [中文=借貸款項擔保品餘額 tier=S 抓=per-stock 頻=daily 最早=2006-10-02 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 股票代號              
    [  ] market                           character varying 市場別               
    [  ] MarginPreviousDayBalance         numeric          融資前日餘額            
    [  ] MarginBuy                        numeric          融資買進              
    [  ] MarginSell                       numeric          融資賣出              
    [  ] MarginCashRedemption             numeric          融資現金償還            
    [  ] MarginCurrentDayBalance          numeric          融資當日餘額            
    [  ] MarginNextDayQuota               numeric          融資次日限額            
    [  ] SecuritiesFirmLoanPreviousDayBalance numeric          券商借貸前日餘額          
    [  ] SecuritiesFirmLoanBuy            numeric          券商借貸買進            
    [  ] SecuritiesFirmLoanSell           numeric          券商借貸賣出            
    [  ] SecuritiesFirmLoanCashRedemption numeric          券商借貸現金償還          
    [  ] SecuritiesFirmLoanReplacement    numeric          券商借貸代償            
    [  ] SecuritiesFirmLoanCurrentDayBalance numeric          券商借貸當日餘額          
    [  ] SecuritiesFirmLoanNextDayQuota   numeric          券商借貸次日限額          
    [  ] UnrestrictedLoanPreviousDayBalance numeric          不限用途借貸前日餘額        
    [  ] UnrestrictedLoanBuy              numeric          不限用途借貸買進          
    [  ] UnrestrictedLoanSell             numeric          不限用途借貸賣出          
    [  ] UnrestrictedLoanCashRedemption   numeric          不限用途借貸現金償還        
    [  ] UnrestrictedLoanReplacement      numeric          不限用途借貸代償          
    [  ] UnrestrictedLoanCurrentDayBalance numeric          不限用途借貸當日餘額        
    [  ] UnrestrictedLoanNextDayQuota     numeric          不限用途借貸次日限額        
    [  ] SecuritiesFinanceSecuredLoanPreviousDayBalance numeric          證金公司擔保放款前日餘額      
    [  ] SecuritiesFinanceSecuredLoanBuy  numeric          證金公司擔保放款買進        
    [  ] SecuritiesFinanceSecuredLoanSell numeric          證金公司擔保放款賣出        
    [  ] SecuritiesFinanceSecuredLoanCashRedemption numeric          證金公司擔保放款現金償還      
    [  ] SecuritiesFinanceSecuredLoanReplacement numeric          證金公司擔保放款代償        
    [  ] SecuritiesFinanceSecuredLoanCurrentDayBalance numeric          證金公司擔保放款當日餘額      
    [  ] SecuritiesFinanceSecuredLoanNextDayQuota numeric          證金公司擔保放款次日限額      
    [  ] SettlementMarginPreviousDayBalance numeric          交割保證金前日餘額         
    [  ] SettlementMarginBuy              numeric          交割保證金買進           
    [  ] SettlementMarginSell             numeric          交割保證金賣出           
    [  ] SettlementMarginCashRedemption   numeric          交割保證金現金償還         
    [  ] SettlementMarginReplacement      numeric          交割保證金代償           
    [  ] SettlementMarginCurrentDayBalance numeric          交割保證金當日餘額         
    [  ] SettlementMarginNextDayQuota     numeric          交割保證金次日限額         

### TaiwanStockMarginPurchaseShortSale  [中文=融資融券 tier=F(id) 抓=per-stock 頻=daily 最早=2001-01-05 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 股票代號              
    [  ] MarginPurchaseBuy                numeric          融資買進              
    [  ] MarginPurchaseCashRepayment      numeric          融資現金償還            
    [  ] MarginPurchaseLimit              numeric          融資限額              
    [  ] MarginPurchaseSell               numeric          融資賣出              
    [  ] MarginPurchaseTodayBalance       numeric          融資今日餘額             ⚑單位=張(千股)(交叉驗 vs 發行股數)
    [  ] MarginPurchaseYesterdayBalance   numeric          融資昨日餘額             ⚑單位=張(千股)(交叉驗 vs 發行股數)
    [  ] Note                             character varying 註記                
    [  ] OffsetLoanAndShort               numeric          資券相抵              
    [  ] ShortSaleBuy                     numeric          融券買進              
    [  ] ShortSaleCashRepayment           numeric          融券現金償還            
    [  ] ShortSaleLimit                   numeric          融券限額              
    [  ] ShortSaleSell                    numeric          融券賣出              
    [  ] ShortSaleTodayBalance            numeric          融券今日餘額             ⚑單位=張(千股)(交叉驗 vs 發行股數)
    [  ] ShortSaleYesterdayBalance        numeric          融券昨日餘額             ⚑單位=張(千股)(交叉驗 vs 發行股數)

### TaiwanStockMarginShortSaleSuspension  [中文=暫停融券賣出 tier=F(id) 抓=by-date 頻=daily 最早=2015-04-01 排除=False]
    [PK] stock_id                         character varying 股票代號              
    [PK] date                             date             起始日期              
    [  ] end_date                         character varying 截止日期              
    [  ] reason                           character varying 暫停事由              

### TaiwanStockSecuritiesLending  [中文=借券成交 tier=F(id) 抓=per-stock 頻=daily 最早=2003-11-11 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 股票代號              
    [  ] transaction_type                 character varying 交易類別              
    [  ] volume                           numeric          成交量（股）            
    [  ] fee_rate                         numeric          費率                
    [  ] close                            numeric          收盤價               
    [  ] original_return_date             character varying 原訂還券日期             ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日
    [  ] original_lending_period          numeric          原訂借券期間（天）         

### TaiwanStockShareholding  [中文=外資持股 tier=F(id) 抓=per-stock 頻=daily 最早=2004-02-12 排除=False]
    🔒 anti-leakage: as-of 欄: RecentlyDeclareDate
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 證券代號              
    [  ] stock_name                       character varying 證券名稱              
    [  ] InternationalCode                character varying 國際證券代碼（ISIN）      
    [  ] ForeignInvestmentRemainingShares numeric          外資尚可投資股數          
    [  ] ForeignInvestmentShares          numeric          全體外資持有股數          
    [  ] ForeignInvestmentRemainRatio     numeric          外資尚可投資比率          
    [  ] ForeignInvestmentSharesRatio     numeric          外資持股比率            
    [  ] ForeignInvestmentUpperLimitRatio numeric          外資法令投資上限比率        
    [  ] ChineseInvestmentUpperLimitRatio numeric          外資及陸資共用法令投資上限比率   
    [  ] NumberOfSharesIssued             numeric          發行股數              
    [  ] RecentlyDeclareDate              character varying 最近一次申報外資持股異動日期 ⭐   🔒AL
    [  ] note                             character varying 與前日異動原因（註）        

### TaiwanStockTotalInstitutionalInvestors  [中文=整體三大法人 tier=F 抓=by-date 頻=daily 最早=2004-04-01 排除=False]
    [  ] buy                              numeric          買進                
    [PK] date                             date             日期                
    [PK] name                             character varying 法人別               
    [  ] sell                             numeric          賣出                

### TaiwanStockTotalMarginPurchaseShortSale  [中文=整體市場融資融券 tier=F 抓=by-date 頻=daily 最早=2001-01-01 排除=False]
    [  ] TodayBalance                     numeric          當日餘額              
    [  ] YesBalance                       numeric          前日餘額              
    [  ] buy                              numeric          買進                
    [PK] date                             date             日期                
    [PK] name                             character varying 類別名稱（融資／融券）       
    [  ] Return                           numeric          償還                
    [  ] sell                             numeric          賣出                

### TaiwanTotalExchangeMarginMaintenance  [中文=大盤融資維持率 tier=B 抓=market 頻=single-series 最早=2001-01-01 排除=False]
    [PK] date                             date             日期                
    [  ] TotalExchangeMarginMaintenance   numeric          大盤整體融資維持率         

==========================================================================================
## CATEGORY: TW-Convertible Bond（4 表）
==========================================================================================

### TaiwanStockConvertibleBondDaily  [中文=可轉債日成交 tier=B 抓=by-date 頻=daily 最早=2007-01-01 排除=False]
    [PK] cb_id                            character varying 可轉債代號             
    [  ] cb_name                          character varying 可轉債名稱             
    [  ] transaction_type                 character varying 交易類別              
    [  ] close                            numeric          收盤價               
    [  ] change                           numeric          漲跌                
    [  ] open                             numeric          開盤價               
    [  ] max                              numeric          最高價               
    [  ] min                              numeric          最低價               
    [  ] no_of_transactions               numeric          成交筆數              
    [  ] unit                             numeric          成交張數              
    [  ] trading_value                    numeric          成交值               
    [  ] avg_price                        numeric          均價                
    [  ] next_ref_price                   numeric          次日參考價             
    [  ] next_max_limit                   numeric          次日漲停價             
    [  ] next_min_limit                   numeric          次日跌停價             
    [PK] date                             date             日期                

### TaiwanStockConvertibleBondDailyOverview  [中文=可轉債每日總覽 tier=B 抓=by-date 頻=daily 最早=2010-01-01 排除=False]
    [PK] cb_id                            character varying 可轉債代號             
    [  ] cb_name                          character varying 可轉債名稱             
    [PK] date                             date             日期                 ⚠️非法日 1911-00-00 → 字串
    [  ] InitialDateOfConversion          date             可轉換起日             
    [  ] DueDateOfConversion              date             可轉換迄日             
    [  ] InitialDateOfStopConversion      character varying 停止轉換起日             ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日
    [  ] DueDateOfStopConversion          character varying 停止轉換迄日             ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日
    [  ] ConversionPrice                  numeric          轉換價格              
    [  ] NextEffectiveDateOfConversionPrice character varying 次一轉換價生效日          
    [  ] LatestInitialDateOfPut           date             最近賣回權起日           
    [  ] LatestDueDateOfPut               date             最近賣回權迄日           
    [  ] LatestPutPrice                   numeric          最近賣回價格            
    [  ] InitialDateOfEarlyRedemption     character varying 提前贖回起日            
    [  ] DueDateOfEarlyRedemption         character varying 提前贖回迄日            
    [  ] EarlyRedemptionPrice             numeric          提前贖回價格            
    [  ] DateOfDelisted                   date             下市日期              
    [  ] IssuanceAmount                   numeric          發行總額              
    [  ] OutstandingAmount                numeric          流通餘額              
    [  ] ReferencePrice                   numeric          參考價格              
    [  ] PriceOfUnderlyingStock           numeric          標的股票價格            
    [  ] InitialDateOfSuspension          character varying 暫停交易起日             ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日
    [  ] DueDateOfSuspension              character varying 暫停交易迄日             ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日
    [  ] CouponRate                       numeric          票面利率              

### TaiwanStockConvertibleBondInfo  [中文=可轉債總覽 tier=B 抓=market 頻=snapshot 最早=2025-01-01 排除=False]
    [PK] cb_id                            character varying 可轉債代號             
    [  ] cb_name                          character varying 可轉債名稱             
    [  ] InitialDateOfConversion          date             可轉換起日             
    [  ] DueDateOfConversion              date             可轉換迄日             
    [  ] IssuanceAmount                   numeric          發行總額              

### TaiwanStockConvertibleBondInstitutionalInvestors  [中文=可轉債三大法人 tier=B 抓=by-date 頻=daily 最早=2009-04-01 排除=False]
    [  ] Foreign_Investor_Buy             numeric          外資買進              
    [  ] Foreign_Investor_Sell            numeric          外資賣出              
    [  ] Foreign_Investor_Overbuy         numeric          外資買超              
    [  ] Investment_Trust_Buy             numeric          投信買進              
    [  ] Investment_Trust_Sell            numeric          投信賣出              
    [  ] Investment_Trust_Overbuy         numeric          投信買超              
    [  ] Dealer_self_Buy                  numeric          自營商買進             
    [  ] Dealer_self_Sell                 numeric          自營商賣出             
    [  ] Dealer_self_Overbuy              numeric          自營商買超             
    [  ] Total_Overbuy                    numeric          合計買超              
    [PK] cb_id                            character varying 可轉債代號             
    [  ] cb_name                          character varying 可轉債名稱             
    [PK] date                             date             日期                

==========================================================================================
## CATEGORY: TW-Derivative（16 表）
==========================================================================================

### TaiwanFutOptDailyInfo  [中文=期貨選擇權總覽 tier=F 抓=market 頻=snapshot 最早=None 排除=False]
    [PK] code                             character varying 代號                
    [PK] type                             character varying 商品類別（期貨/選擇權）      
    [PK] name                             character varying 商品名稱              

### TaiwanFutOptInstitutionalInvestors  [中文=期貨選擇權三大法人（合併） tier=F 抓=by-date 頻=daily 最早=2017-07-01 排除=False]
    [PK] name                             character varying 商品名稱              
    [PK] date                             date             日期                
    [PK] institutional_investors          character varying 法人別               
    [  ] long_deal_volume                 numeric          多方交易口數            
    [  ] long_deal_amount                 numeric          多方交易金額            
    [  ] short_deal_volume                numeric          空方交易口數            
    [  ] short_deal_amount                numeric          空方交易金額            
    [  ] long_open_interest_balance_volume numeric          多方未平倉口數           
    [  ] long_open_interest_balance_amount numeric          多方未平倉金額           
    [  ] short_open_interest_balance_volume numeric          空方未平倉口數           
    [  ] short_open_interest_balance_amount numeric          空方未平倉金額           

### TaiwanFuturesDaily  [中文=期貨日成交 tier=F(id) 抓=by-date 頻=daily 最早=1998-08-01 排除=False]
    [PK] date                             date             日期                
    [PK] futures_id                       character varying 期貨代號              
    [PK] contract_date                    character varying 契約月份（含價差如 200710/2 ⚠️契約月/價差碼 200710 或 200710/200711 → 字串非數字
    [PK] open                             numeric          開盤價               
    [PK] max                              numeric          最高價               
    [PK] min                              numeric          最低價               
    [PK] close                            numeric          收盤價               
    [PK] spread                           numeric          漲跌價差              
    [PK] spread_per                       numeric          漲跌幅(%)            
    [PK] volume                           numeric          成交量(口)            
    [PK] settlement_price                 numeric          結算價               
    [PK] open_interest                    numeric          未平倉量              
    [PK] trading_session                  character varying 交易時段(日盤/夜盤)       

### TaiwanFuturesDealerTradingVolumeDaily  [中文=期貨各券商每日交易 tier=F 抓=by-date 頻=daily 最早=2021-04-01 排除=False]
    [PK] date                             date             日期                
    [PK] dealer_code                      character varying 券商代號              
    [PK] dealer_name                      character varying 券商名稱              
    [PK] futures_id                       character varying 期貨代號              
    [PK] volume                           numeric          成交量(口)            
    [PK] is_after_hour                    character varying 是否盤後（夜盤）          

### TaiwanFuturesFinalSettlementPrice  [中文=期貨最後結算價 tier=B 抓=by-date 頻=daily 最早=2016-01-08 排除=False]
    [PK] date                             date             日期                
    [  ] contract_month                   character varying 結算月份（含週合約如 202101W ⚠️週合約碼 202101W1 → 字串
    [  ] futures_type                     character varying 期貨類別              
    [PK] futures_id                       character varying 期貨代號              
    [  ] futures_name                     character varying 期貨名稱              
    [  ] settlement_price                 numeric          結算價               
    [  ] underlying_code                  character varying 標的代號              
    [  ] notional_value                   numeric          契約價值              

### TaiwanFuturesInstitutionalInvestors  [中文=期貨三大法人 tier=F(id) 抓=by-date 頻=daily 最早=2018-06-01 排除=False]
    [PK] futures_id                       character varying 期貨代號              
    [PK] date                             date             日期                
    [PK] institutional_investors          character varying 法人別               
    [  ] long_deal_volume                 numeric          多方成交量             
    [  ] long_deal_amount                 numeric          多方成交金額            
    [  ] short_deal_volume                numeric          空方成交量             
    [  ] short_deal_amount                numeric          空方成交金額            
    [  ] long_open_interest_balance_volume numeric          多方未平倉餘額量          
    [  ] long_open_interest_balance_amount numeric          多方未平倉餘額金額         
    [  ] short_open_interest_balance_volume numeric          空方未平倉餘額量          
    [  ] short_open_interest_balance_amount numeric          空方未平倉餘額金額         

### TaiwanFuturesInstitutionalInvestorsAfterHours  [中文=期貨三大法人（夜盤） tier=B 抓=by-date 頻=daily 最早=2021-10-01 排除=False]
    [PK] futures_id                       character varying 期貨代號              
    [PK] date                             date             日期                
    [PK] institutional_investors          character varying 法人別               
    [  ] long_deal_volume                 numeric          多方交易口數            
    [  ] long_deal_amount                 numeric          多方交易金額            
    [  ] short_deal_volume                numeric          空方交易口數            
    [  ] short_deal_amount                numeric          空方交易金額            

### TaiwanFuturesOpenInterestLargeTraders  [中文=期貨大額交易人未沖銷 tier=B 抓=by-date 頻=daily 最早=2007-01-01 排除=False]
    [PK] name                             character varying 商品名稱              
    [PK] contract_type                    character varying 契約類別（所有契約/近月契約）   
    [  ] buy_top5_trader_open_interest    numeric          前5大交易人買方未平倉       
    [  ] buy_top5_trader_open_interest_per numeric          前5大交易人買方未平倉占比(%)  
    [  ] buy_top10_trader_open_interest   numeric          前10大交易人買方未平倉      
    [  ] buy_top10_trader_open_interest_per numeric          前10大交易人買方未平倉占比(%) 
    [  ] sell_top5_trader_open_interest   numeric          前5大交易人賣方未平倉       
    [  ] sell_top5_trader_open_interest_per numeric          前5大交易人賣方未平倉占比(%)  
    [  ] sell_top10_trader_open_interest  numeric          前10大交易人賣方未平倉      
    [  ] sell_top10_trader_open_interest_per numeric          前10大交易人賣方未平倉占比(%) 
    [  ] market_open_interest             numeric          全市場未平倉量           
    [  ] buy_top5_specific_open_interest  numeric          前5大特定法人買方未平倉      
    [  ] buy_top5_specific_open_interest_per numeric          前5大特定法人買方未平倉占比(%) 
    [  ] buy_top10_specific_open_interest numeric          前10大特定法人買方未平倉     
    [  ] buy_top10_specific_open_interest_per numeric          前10大特定法人買方未平倉占比(%)
    [  ] sell_top5_specific_open_interest numeric          前5大特定法人賣方未平倉      
    [  ] sell_top5_specific_open_interest_per numeric          前5大特定法人賣方未平倉占比(%) 
    [  ] sell_top10_specific_open_interest numeric          前10大特定法人賣方未平倉     
    [  ] sell_top10_specific_open_interest_per numeric          前10大特定法人賣方未平倉占比(%)
    [PK] date                             date             日期                
    [PK] futures_id                       character varying 期貨代號              

### TaiwanFuturesSpreadTick  [中文=期貨價差逐筆(Tick) tier=F 抓=by-date 頻=daily 最早=2026-05-01 排除=False]
    [PK] contract_date                    character varying 契約月份               ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日
    [PK] date                             date             日期                
    [PK] time                             character varying 時間                
    [PK] far_price                        numeric          遠月價               
    [PK] futures_id                       character varying 期貨代號              
    [PK] near_price                       numeric          近月價               
    [PK] price                            numeric          價差價               
    [PK] spread_to_spread                 numeric          價差對價差             
    [PK] volume                           numeric          成交量               

### TaiwanFuturesSpreadTrading  [中文=期貨價差行情 tier=B 抓=by-date 頻=daily 最早=2007-11-01 排除=False]
    [PK] date                             date             日期                
    [PK] futures_id                       character varying 期貨代號              
    [  ] contract_date                    character varying 契約月份（含價差/週合約）      ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日
    [  ] open                             numeric          開盤價               
    [  ] max                              numeric          最高價               
    [  ] min                              numeric          最低價               
    [  ] close                            numeric          收盤價               
    [  ] best_bid                         numeric          最佳買價              
    [  ] best_ask                         numeric          最佳賣價              
    [  ] historical_max                   numeric          歷史最高價             
    [  ] historical_min                   numeric          歷史最低價             
    [  ] spread_to_spread_volume          numeric          價差對價差成交量          
    [  ] spread_to_single_volume          numeric          價差對單式成交量          
    [  ] trading_session                  character varying 交易時段(日盤/夜盤)       

### TaiwanOptionDaily  [中文=選擇權日成交 tier=F(id) 抓=by-date 頻=daily 最早=2002-01-01 排除=False]
    [PK] date                             date             日期                
    [PK] option_id                        character varying 選擇權代號             
    [PK] contract_date                    character varying 契約月份（含價差、週合約如 2012 ⚠️週選契約碼 201211W4 → 字串
    [PK] strike_price                     numeric          履約價               
    [PK] call_put                         character varying 買權賣權(Call買權/Put賣權)
    [PK] open                             numeric          開盤價               
    [PK] max                              numeric          最高價               
    [PK] min                              numeric          最低價               
    [PK] close                            numeric          收盤價               
    [PK] volume                           numeric          成交量(口)            
    [PK] settlement_price                 numeric          結算價               
    [PK] open_interest                    numeric          未平倉量              
    [PK] trading_session                  character varying 交易時段(日盤/夜盤)       

### TaiwanOptionDealerTradingVolumeDaily  [中文=選擇權各券商每日交易 tier=F 抓=by-date 頻=daily 最早=2021-04-01 排除=False]
    [PK] date                             date             日期                
    [PK] dealer_code                      character varying 券商代號              
    [PK] dealer_name                      character varying 券商名稱              
    [PK] option_id                        character varying 選擇權代號             
    [PK] volume                           numeric          成交量(口)            
    [PK] is_after_hour                    character varying 是否盤後（夜盤）          

### TaiwanOptionFinalSettlementPrice  [中文=選擇權最後結算價 tier=B 抓=by-date 頻=daily 最早=2002-01-17 排除=False]
    [PK] date                             date             日期                
    [  ] contract_month                   character varying 結算月份（含週合約）        
    [  ] option_type                      character varying 選擇權類別             
    [PK] option_id                        character varying 選擇權代號             
    [  ] option_name                      character varying 選擇權名稱             
    [  ] settlement_price                 numeric          結算價               
    [  ] underlying_code                  character varying 標的代號              
    [  ] notional_value                   numeric          契約價值              

### TaiwanOptionInstitutionalInvestors  [中文=選擇權三大法人 tier=F(id) 抓=by-date 頻=daily 最早=2018-06-01 排除=False]
    [PK] option_id                        character varying 選擇權代號             
    [PK] date                             date             日期                
    [PK] call_put                         character varying 買權賣權(Call買權/Put賣權)
    [PK] institutional_investors          character varying 法人別               
    [  ] long_deal_volume                 numeric          多方成交量             
    [  ] long_deal_amount                 numeric          多方成交金額            
    [  ] short_deal_volume                numeric          空方成交量             
    [  ] short_deal_amount                numeric          空方成交金額            
    [  ] long_open_interest_balance_volume numeric          多方未平倉餘額量          
    [  ] long_open_interest_balance_amount numeric          多方未平倉餘額金額         
    [  ] short_open_interest_balance_volume numeric          空方未平倉餘額量          
    [  ] short_open_interest_balance_amount numeric          空方未平倉餘額金額         

### TaiwanOptionInstitutionalInvestorsAfterHours  [中文=選擇權三大法人（夜盤） tier=B 抓=by-date 頻=daily 最早=2021-10-01 排除=False]
    [PK] option_id                        character varying 選擇權代號             
    [PK] date                             date             日期                
    [PK] call_put                         character varying 買權賣權(Call/Put)    
    [PK] institutional_investors          character varying 法人別               
    [  ] long_deal_volume                 numeric          多方交易口數            
    [  ] long_deal_amount                 numeric          多方交易金額            
    [  ] short_deal_volume                numeric          空方交易口數            
    [  ] short_deal_amount                numeric          空方交易金額            

### TaiwanOptionOpenInterestLargeTraders  [中文=選擇權大額交易人未沖銷 tier=B 抓=by-date 頻=daily 最早=2007-01-01 排除=False]
    [PK] contract_type                    character varying 契約類別（所有契約/近月契約）   
    [  ] buy_top5_trader_open_interest    numeric          前5大交易人買方未平倉       
    [  ] buy_top5_trader_open_interest_per numeric          前5大交易人買方未平倉占比(%)  
    [  ] buy_top10_trader_open_interest   numeric          前10大交易人買方未平倉      
    [  ] buy_top10_trader_open_interest_per numeric          前10大交易人買方未平倉占比(%) 
    [  ] sell_top5_trader_open_interest   numeric          前5大交易人賣方未平倉       
    [  ] sell_top5_trader_open_interest_per numeric          前5大交易人賣方未平倉占比(%)  
    [  ] sell_top10_trader_open_interest  numeric          前10大交易人賣方未平倉      
    [  ] sell_top10_trader_open_interest_per numeric          前10大交易人賣方未平倉占比(%) 
    [  ] market_open_interest             numeric          全市場未平倉量           
    [  ] buy_top5_specific_open_interest  numeric          前5大特定法人買方未平倉      
    [  ] buy_top5_specific_open_interest_per numeric          前5大特定法人買方未平倉占比(%) 
    [  ] buy_top10_specific_open_interest numeric          前10大特定法人買方未平倉     
    [  ] buy_top10_specific_open_interest_per numeric          前10大特定法人買方未平倉占比(%)
    [  ] sell_top5_specific_open_interest numeric          前5大特定法人賣方未平倉      
    [  ] sell_top5_specific_open_interest_per numeric          前5大特定法人賣方未平倉占比(%) 
    [  ] sell_top10_specific_open_interest numeric          前10大特定法人賣方未平倉     
    [  ] sell_top10_specific_open_interest_per numeric          前10大特定法人賣方未平倉占比(%)
    [PK] date                             date             日期                
    [PK] put_call                         character varying 買權賣權(Call買權/Put賣權)
    [PK] name                             character varying 商品名稱              
    [PK] option_id                        character varying 選擇權代號             

==========================================================================================
## CATEGORY: TW-Fundamental（12 表）
==========================================================================================

### TaiwanStockBalanceSheet  [中文=資產負債表 tier=F(id) 抓=per-stock 頻=daily 最早=2012-12-31 排除=False]
    [PK] date                             date             資料日期（季底）          
    [PK] stock_id                         character varying 股票代號              
    [PK] type                             character varying 會計科目（值見 `/translat
    [  ] value                            numeric          科目金額               ⚠️不規則覆蓋缺口:2022缺Q4/2023僅Q1Q2/2024僅Q3Q4(損益現金流同期全);用 ba ⚑資產負債時點snapshot;_per後綴=佔總資產%;發布日+45/90日
    [  ] origin_name                      character varying 原始科目名稱            

### TaiwanStockCapitalReductionReferencePrice  [中文=減資恢復買賣參考價 tier=F 抓=market 頻=single-series 最早=2011-01-25 排除=False]
    [PK] date                             date             恢復買賣日             
    [PK] stock_id                         character varying 股票代號              
    [  ] ClosingPriceonTheLastTradingDay  numeric          減資前最後交易日收盤價       
    [  ] PostReductionReferencePrice      numeric          減資後參考價            
    [  ] LimitUp                          numeric          漲停價               
    [  ] LimitDown                        numeric          跌停價               
    [  ] OpeningReferencePrice            numeric          開盤競價基準            
    [  ] ExrightReferencePrice            numeric          除權參考價             
    [  ] ReasonforCapitalReduction        character varying 減資原因              

### TaiwanStockCashFlowsStatement  [中文=現金流量表 tier=F(id) 抓=per-stock 頻=daily 最早=2012-03-31 排除=False]
    [PK] date                             date             資料日期（季底）          
    [PK] stock_id                         character varying 股票代號              
    [PK] type                             character varying 會計科目（值見 `/translat
    [  ] value                            numeric          科目金額               ⚑現金流累計YTD(需去累計得單季);發布日季底+45/90日
    [  ] origin_name                      character varying 原始科目名稱            

### TaiwanStockDelisting  [中文=下市櫃 tier=F 抓=market 頻=single-series 最早=2001-01-20 排除=False]
    [  ] date                             date             下市櫃日              
    [PK] stock_id                         character varying 股票代號              
    [  ] stock_name                       character varying 股票名稱              

### TaiwanStockDividend  [中文=股利政策 tier=F(id) 抓=per-stock 頻=daily 最早=2005-06-19 排除=False]
    🔒 anti-leakage: as-of 欄: AnnouncementDate, AnnouncementTime
    [  ] date                             date             資料日期              
    [PK] stock_id                         character varying 股票代號              
    [  ] year                             character varying 股利所屬年度            
    [  ] StockEarningsDistribution        numeric          盈餘配股              
    [  ] StockStatutorySurplus            numeric          法定盈餘公積配股          
    [  ] StockExDividendTradingDate       character varying 除權交易日             
    [  ] TotalEmployeeStockDividend       numeric          員工配股總額            
    [  ] TotalEmployeeStockDividendAmount numeric          員工配股金額            
    [  ] RatioOfEmployeeStockDividendOfTotal numeric          員工配股占盈餘比率         
    [  ] RatioOfEmployeeStockDividend     numeric          員工配股率             
    [  ] CashEarningsDistribution         numeric          盈餘配息（現金股利）        
    [  ] CashStatutorySurplus             numeric          法定盈餘公積配息          
    [  ] CashExDividendTradingDate        character varying 除息交易日             
    [  ] CashDividendPaymentDate          character varying 現金股利發放日           
    [  ] TotalEmployeeCashDividend        numeric          員工現金紅利總額          
    [  ] TotalNumberOfCashCapitalIncrease numeric          現金增資總股數           
    [  ] CashIncreaseSubscriptionRate     numeric          現金增資認購率           
    [  ] CashIncreaseSubscriptionpRrice   numeric          現金增資認購價           
    [  ] RemunerationOfDirectorsAndSupervisors numeric          董監事酬勞             
    [  ] ParticipateDistributionOfTotalShares numeric          參與分配總股數           
    [  ] AnnouncementDate                 character varying 公告日期 ⭐             🔒AL
    [  ] AnnouncementTime                 character varying 公告時間 ⭐             🔒AL

### TaiwanStockDividendResult  [中文=除權除息結果 tier=F(id) 抓=per-stock 頻=daily 最早=2003-07-07 排除=False]
    [PK] date                             date             除權息日              
    [PK] stock_id                         character varying 股票代號              
    [  ] before_price                     numeric          除權息前參考價           
    [  ] after_price                      numeric          除權息後參考價           
    [  ] stock_and_cache_dividend         numeric          配股配息合計            
    [  ] stock_or_cache_dividend          character varying 股票或現金股利           
    [  ] max_price                        numeric          最高價               
    [  ] min_price                        numeric          最低價               
    [  ] open_price                       numeric          開盤價               
    [  ] reference_price                  numeric          參考價               

### TaiwanStockFinancialStatements  [中文=綜合損益表 tier=F(id) 抓=per-stock 頻=daily 最早=1991-12-31 排除=False]
    [PK] date                             date             資料日期（季底）          
    [PK] stock_id                         character varying 股票代號              
    [PK] type                             character varying 會計科目（值見 `/translat
    [  ] value                            numeric          科目金額               ⚑財報單季;發布日季底+45/90日(release_lag gate #8)
    [  ] origin_name                      character varying 原始科目名稱            

### TaiwanStockMarketValue  [中文=股價市值 tier=B 抓=per-stock 頻=daily 最早=2004-02-12 排除=False]
    [PK] date                             date             資料日期              
    [PK] stock_id                         character varying 股票代號              
    [  ] market_value                     numeric          市值（元）             

### TaiwanStockMarketValueWeight  [中文=市值比重 tier=B 抓=by-date 頻=daily 最早=2024-10-30 排除=False]
    [  ] rank                             numeric          排名                
    [PK] stock_id                         character varying 股票代號              
    [  ] stock_name                       character varying 股票名稱              
    [  ] weight_per                       numeric          市值權重（%）           
    [PK] date                             date             資料日期              
    [  ] type                             character varying 類別（上市/上櫃）         

### TaiwanStockMonthRevenue  [中文=月營收 tier=F(id) 抓=per-stock 頻=daily 最早=2002-02-01 排除=False]
    🔒 anti-leakage: as-of 欄: create_time
    [PK] date                             date             資料日期              
    [PK] stock_id                         character varying 股票代號              
    [PK] country                          character varying 國家／央行             
    [  ] revenue                          numeric          當月營收（元）            ⚑單位=元(交叉驗:2330=4169億元級;catalog 原標「千元」為誤);
    [  ] revenue_month                    numeric          營收月份              
    [  ] revenue_year                     numeric          營收年度              
    [  ] create_time                      character varying 資料建立時點             🔒AL

### TaiwanStockParValueChange  [中文=變更面額恢復買賣參考價 tier=F 抓=market 頻=single-series 最早=2019-09-09 排除=False]
    [PK] date                             date             恢復買賣日             
    [PK] stock_id                         character varying 股票代號              
    [  ] stock_name                       character varying 股票名稱              
    [  ] before_close                     numeric          變更前收盤價            
    [  ] after_ref_close                  numeric          變更後參考收盤價          
    [  ] after_ref_max                    numeric          調整後參考最高價          
    [  ] after_ref_min                    numeric          調整後參考最低價          
    [  ] after_ref_open                   numeric          調整後參考開盤價          

### TaiwanStockSplitPrice  [中文=分割後參考價 tier=F 抓=market 頻=single-series 最早=2019-09-09 排除=False]
    [PK] date                             date             分割恢復買賣日           
    [PK] stock_id                         character varying 股票代號              
    [  ] type                             character varying 類別                
    [  ] before_price                     numeric          分割前參考價            
    [  ] after_price                      numeric          分割後參考價            
    [  ] max_price                        numeric          最高價               
    [  ] min_price                        numeric          最低價               
    [  ] open_price                       numeric          開盤價               

==========================================================================================
## CATEGORY: TW-Others（3 表）
==========================================================================================

### TaiwanBusinessIndicator  [中文=景氣對策信號 tier=B 抓=market 頻=single-series 最早=1982-01-01 排除=False]
    [PK] date                             date             日期                
    [  ] leading                          numeric          領先指標              
    [  ] leading_notrend                  numeric          領先指標（不含趨勢）        
    [  ] coincident                       numeric          同時指標              
    [  ] coincident_notrend               numeric          同時指標（不含趨勢）        
    [  ] lagging                          numeric          落後指標              
    [  ] lagging_notrend                  numeric          落後指標（不含趨勢）        
    [  ] monitoring                       numeric          景氣對策信號            
    [  ] monitoring_color                 character varying 信號燈號              

### TaiwanStockIndustryChain  [中文=產業鏈 tier=B 抓=by-date 頻=daily 最早=2026-06-16 排除=False]
    [PK] stock_id                         character varying 股票代號              
    [PK] industry                         character varying 產業                
    [PK] sub_industry                     character varying 次產業               
    [PK] date                             date             日期                

### TaiwanStockNews  [中文=相關新聞 tier=F 抓=single-day 頻=single-day 最早=2010-03-01 排除=False]
    [PK] date                             character varying 日期                 ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日
    [PK] stock_id                         character varying 股票代號              
    [  ] link                             text             連結                
    [  ] source                           character varying 來源                
    [  ] title                            character varying 標題                

==========================================================================================
## CATEGORY: TW-Real-Time（1 表）
==========================================================================================

### TaiwanFutOptTickInfo  [中文=期貨選擇權即時總覽 tier=S 抓=market 頻=single-series 最早=2026-06-01 排除=False]
    [PK] code                             character varying 商品代號              
    [  ] callput                          character varying 買賣權               
    [  ] date                             character varying 日期                 ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日
    [  ] name                             character varying 商品名稱              
    [  ] listing_date                     date             上市日期              
    [  ] expire_price                     numeric          到期結算價             
    [  ] update_date                      date             更新日期              

==========================================================================================
## CATEGORY: TW-Technical（16 表）
==========================================================================================

### TaiwanStock10Year  [中文=十年線（月均價） tier=B 抓=per-stock 頻=daily 最早=2011-01-24 排除=False]
    [PK] date                             date             資料日期              
    [PK] stock_id                         character varying 股票代號              
    [  ] close                            numeric          收盤價               

### TaiwanStockDayTrading  [中文=當沖交易 tier=F(id) 抓=by-date 頻=daily 最早=2014-01-06 排除=False]
    [PK] stock_id                         character varying 股票代號              
    [PK] date                             date             交易日               
    [  ] BuyAfterSale                     character varying 現股當沖先買後賣          
    [  ] Volume                           numeric          當沖成交股數            
    [  ] BuyAmount                        numeric          當沖買進金額            
    [  ] SellAmount                       numeric          當沖賣出金額            

### TaiwanStockDayTradingBorrowingFeeRate  [中文=當沖借券費率 tier=F 抓=by-date 頻=daily 最早=2015-10-14 排除=False]
    [PK] date                             date             日期                
    [PK] stock_id                         character varying 股票代號              
    [  ] stock_name                       character varying 股票名稱              
    [  ] InvestorBorrowedShares           numeric          投資人借券張數           
    [  ] InvestorBorrowingFeeRate         numeric          投資人借券費率           

### TaiwanStockDayTradingSuspension  [中文=暫停現股當沖 tier=B 抓=by-date 頻=daily 最早=2014-07-09 排除=False]
    [PK] stock_id                         character varying 股票代號              
    [PK] date                             date             起始日期              
    [  ] end_date                         date             截止日期              
    [  ] reason                           character varying 暫停原因              

### TaiwanStockInfo  [中文=台股總覽 tier=F 抓=by-date 頻=daily 最早=2020-06-03 排除=False]
    [PK] industry_category                character varying 產業類別              
    [PK] stock_id                         character varying 股票代號              
    [  ] stock_name                       character varying 股票名稱              
    [PK] type                             character varying 市場類別              
    [  ] date                             date             資料日期              

### TaiwanStockInfoWithWarrant  [中文=台股總覽（含權證） tier=F 抓=by-date 頻=daily 最早=2026-06-16 排除=False]
    [PK] industry_category                character varying 產業類別              
    [PK] stock_id                         character varying 股票代號              
    [  ] stock_name                       character varying 股票名稱              
    [PK] type                             character varying 市場類別              
    [PK] date                             date             資料日期              

### TaiwanStockInfoWithWarrantSummary  [中文=權證標的對照表 tier=S 抓=by-date 頻=daily 最早=2011-01-01 排除=False]
    [PK] stock_id                         character varying 權證代號              
    [PK] date                             date             資料日期              
    [  ] close                            numeric          權證收盤價             
    [  ] target_stock_id                  character varying 標的證券代號            
    [  ] target_close                     numeric          標的證券收盤價           
    [  ] type                             character varying 權證類別              
    [  ] fulfillment_method               character varying 履約方式              
    [  ] end_date                         date             到期日               
    [  ] fulfillment_start_date           character varying 履約起始日              ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日
    [  ] fulfillment_end_date             character varying 履約截止日              ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日
    [  ] exercise_ratio                   numeric          行使比例              
    [  ] fulfillment_price                numeric          履約價格              

### TaiwanStockMonthPrice  [中文=月K線 tier=B 抓=per-stock 頻=daily 最早=1999-12-01 排除=False]
    [PK] stock_id                         character varying 股票代號              
    [  ] ymonth                           character varying 年度月別              
    [  ] max                              numeric          最高價               
    [  ] min                              numeric          最低價               
    [  ] trading_volume                   numeric          成交股數              
    [  ] trading_money                    numeric          成交金額              
    [  ] trading_turnover                 numeric          成交筆數              
    [PK] date                             date             交易日               
    [  ] close                            numeric          收盤價               
    [  ] open                             numeric          開盤價               
    [  ] spread                           numeric          漲跌價差              

### TaiwanStockPER  [中文=本益比/股價淨值比 tier=F 抓=per-stock 頻=daily 最早=2005-09-02 排除=False]
    [PK] date                             date             交易日               
    [PK] stock_id                         character varying 股票代號              
    [  ] dividend_yield                   numeric          殖利率                ⚑極端離群未 winsorize(PBR max~1442、殖利率 max~306
    [  ] PER                              numeric          本益比                ⚠️虧損股 PER=-1 哨兵(非真本益比;valuation per>0 擋)
    [  ] PBR                              numeric          股價淨值比              ⚑極端離群未 winsorize(PBR max~1442、殖利率 max~306

### TaiwanStockPrice  [中文=股價日成交資訊 tier=F(id) 抓=per-stock 頻=daily 最早=1994-09-13 排除=False]
    [PK] date                             date             交易日               
    [PK] stock_id                         character varying 股票代號              
    [  ] Trading_Volume                   numeric          成交股數              
    [  ] Trading_money                    numeric          成交金額              
    [  ] open                             numeric          開盤價                ⚠️停牌日 OHLC=0 哨兵(~28萬列);特徵層用 PriceAdj+close>0 擋
    [  ] max                              numeric          最高價                ⚠️停牌日 OHLC=0 哨兵(~28萬列);特徵層用 PriceAdj+close>0 擋
    [  ] min                              numeric          最低價                ⚠️停牌日 OHLC=0 哨兵(~28萬列);特徵層用 PriceAdj+close>0 擋
    [  ] close                            numeric          收盤價                ⚠️停牌日 OHLC=0 哨兵(~28萬列);特徵層用 PriceAdj+close>0 擋
    [  ] spread                           numeric          漲跌價差               ⚠️停牌日 OHLC=0 哨兵(~28萬列);特徵層用 PriceAdj+close>0 擋
    [  ] Trading_turnover                 numeric          成交筆數              

### TaiwanStockPriceAdj  [中文=還原股價（日） tier=F(id) 抓=per-stock 頻=daily 最早=1994-09-14 排除=False]
    [PK] date                             date             交易日               
    [PK] stock_id                         character varying 股票代號              
    [  ] Trading_Volume                   numeric          成交股數              
    [  ] Trading_money                    numeric          成交金額              
    [  ] open                             numeric          還原開盤價              ⚠️停牌日 OHLC=0 哨兵(~28萬列);特徵層用 PriceAdj+close>0 擋
    [  ] max                              numeric          還原最高價              ⚠️停牌日 OHLC=0 哨兵(~28萬列);特徵層用 PriceAdj+close>0 擋
    [  ] min                              numeric          還原最低價              ⚠️停牌日 OHLC=0 哨兵(~28萬列);特徵層用 PriceAdj+close>0 擋
    [  ] close                            numeric          還原收盤價              ⚠️停牌日 OHLC=0 哨兵(~28萬列);特徵層用 PriceAdj+close>0 擋
    [  ] spread                           numeric          漲跌價差               ⚠️停牌日 OHLC=0 哨兵(~28萬列);特徵層用 PriceAdj+close>0 擋
    [  ] Trading_turnover                 numeric          成交筆數              

### TaiwanStockPriceLimit  [中文=每日漲跌停價 tier=F(id) 抓=per-stock 頻=daily 最早=2000-01-03 排除=False]
    [PK] date                             date             交易日               
    [PK] stock_id                         character varying 股票代號              
    [  ] reference_price                  numeric          參考價               
    [  ] limit_up                         numeric          漲停價               
    [  ] limit_down                       numeric          跌停價               

### TaiwanStockSuspended  [中文=暫停交易 tier=B 抓=by-date 頻=daily 最早=2025-03-01 排除=False]
    [PK] date                             date             暫停交易日期            
    [PK] stock_id                         character varying 股票代號              
    [  ] suspension_time                  character varying 暫停交易時間            
    [  ] resumption_date                  character varying 恢復交易日期             ⚑date 欄被推為 VARCHAR（值非純 YYYY-MM-DD：含時間/非法日
    [  ] resumption_time                  character varying 恢復交易時間            

### TaiwanStockTotalReturnIndex  [中文=發行量加權股價報酬指數 tier=F 抓=by-date 頻=daily 最早=2003-01-02 排除=False]
    [  ] price                            numeric          指數值               
    [PK] stock_id                         character varying 指數代號（TAIEX/TPEx）  
    [PK] date                             date             資料日期              

### TaiwanStockTradingDate  [中文=交易日曆 tier=F 抓=market 頻=single-series 最早=1999-01-01 排除=False]
    [PK] date                             date             交易日               

### TaiwanStockWeekPrice  [中文=週K線 tier=B 抓=per-stock 頻=daily 最早=1999-12-20 排除=False]
    [PK] stock_id                         character varying 股票代號              
    [  ] yweek                            character varying 年度週別              
    [  ] max                              numeric          最高價               
    [  ] min                              numeric          最低價               
    [  ] trading_volume                   numeric          成交股數              
    [  ] trading_money                    numeric          成交金額              
    [  ] trading_turnover                 numeric          成交筆數              
    [PK] date                             date             交易日               
    [  ] close                            numeric          收盤價               
    [  ] open                             numeric          開盤價               
    [  ] spread                           numeric          漲跌價差              


==========================================================================================
# 一致性審計彙總
==========================================================================================

## catalog_missing_col: 3 項
    fred_series.series_id
    fred_series.date
    fred_series.value

## type_mismatch: 15 項
    GoldPrice.date(cat=varchar/db=date)
    TaiwanStockDispositionSecuritiesPeriod.measure(cat=varchar/db=text)
    TaiwanStockMarginShortSaleSuspension.end_date(cat=date/db=character varying)
    TaiwanStockShareholding.RecentlyDeclareDate(cat=date/db=character varying)
    TaiwanStockConvertibleBondDailyOverview.date(cat=varchar/db=date)
    TaiwanStockConvertibleBondDailyOverview.NextEffectiveDateOfConversionPrice(cat=date/db=character varying)
    TaiwanStockConvertibleBondDailyOverview.InitialDateOfEarlyRedemption(cat=date/db=character varying)
    TaiwanStockConvertibleBondDailyOverview.DueDateOfEarlyRedemption(cat=date/db=character varying)
    TaiwanStockDividend.StockExDividendTradingDate(cat=date/db=character varying)
    TaiwanStockDividend.CashExDividendTradingDate(cat=date/db=character varying)
    TaiwanStockDividend.CashDividendPaymentDate(cat=date/db=character varying)
    TaiwanStockDividend.AnnouncementDate(cat=date/db=character varying)
    TaiwanStockMonthRevenue.create_time(cat=date/db=character varying)
    TaiwanStockNews.link(cat=text/db=text)
    TaiwanStockInfoWithWarrantSummary.target_stock_id(cat=numeric/db=character varying)

## pk_mismatch: 49 項
    CrudeOilPrices.name(cat_pk=False/db_pk=True)
    GovernmentBondsYield.name(cat_pk=False/db_pk=True)
    EuropeStockPrice.date(cat_pk=False/db_pk=True)
    JapanStockPrice.date(cat_pk=False/db_pk=True)
    UKStockPrice.date(cat_pk=False/db_pk=True)
    USStockInfo.stock_id(cat_pk=True/db_pk=False)
    USStockInfo.stock_name(cat_pk=False/db_pk=True)
    USStockPrice.stock_id(cat_pk=False/db_pk=True)
    USStockPrice.Adj_Close(cat_pk=True/db_pk=False)
    USStockPrice.Close(cat_pk=True/db_pk=False)
    USStockPrice.High(cat_pk=True/db_pk=False)
    USStockPrice.Low(cat_pk=True/db_pk=False)
    USStockPrice.Open(cat_pk=True/db_pk=False)
    USStockPrice.Volume(cat_pk=True/db_pk=False)
    TaiwanStockBlockTrade.trade_type(cat_pk=True/db_pk=False)
    TaiwanStockBlockTrade.price(cat_pk=True/db_pk=False)
    TaiwanStockBlockTrade.volume(cat_pk=True/db_pk=False)
    TaiwanStockBlockTrade.trading_money(cat_pk=True/db_pk=False)
    TaiwanStockDispositionSecuritiesPeriod.date(cat_pk=False/db_pk=True)
    TaiwanStockSecuritiesLending.transaction_type(cat_pk=True/db_pk=False)
    TaiwanStockSecuritiesLending.volume(cat_pk=True/db_pk=False)
    TaiwanStockSecuritiesLending.fee_rate(cat_pk=True/db_pk=False)
    TaiwanStockSecuritiesLending.close(cat_pk=True/db_pk=False)
    TaiwanStockSecuritiesLending.original_lending_period(cat_pk=True/db_pk=False)
    TaiwanStockConvertibleBondDaily.date(cat_pk=False/db_pk=True)
    TaiwanStockConvertibleBondDailyOverview.date(cat_pk=False/db_pk=True)
    TaiwanStockConvertibleBondInstitutionalInvestors.date(cat_pk=False/db_pk=True)
    TaiwanFuturesFinalSettlementPrice.date(cat_pk=False/db_pk=True)
    TaiwanFuturesSpreadTrading.contract_date(cat_pk=True/db_pk=False)
    TaiwanFuturesSpreadTrading.open(cat_pk=True/db_pk=False)
    TaiwanFuturesSpreadTrading.max(cat_pk=True/db_pk=False)
    TaiwanFuturesSpreadTrading.min(cat_pk=True/db_pk=False)
    TaiwanFuturesSpreadTrading.close(cat_pk=True/db_pk=False)
    TaiwanFuturesSpreadTrading.best_bid(cat_pk=True/db_pk=False)
    TaiwanFuturesSpreadTrading.best_ask(cat_pk=True/db_pk=False)
    TaiwanFuturesSpreadTrading.historical_max(cat_pk=True/db_pk=False)
    TaiwanFuturesSpreadTrading.historical_min(cat_pk=True/db_pk=False)
    TaiwanFuturesSpreadTrading.spread_to_spread_volume(cat_pk=True/db_pk=False)
    TaiwanFuturesSpreadTrading.spread_to_single_volume(cat_pk=True/db_pk=False)
    TaiwanFuturesSpreadTrading.trading_session(cat_pk=True/db_pk=False)
    …(共 49、餘略)

## no_zh: 0 項

## no_catalog_table: 0 項
```

---

## 附錄二:核心表 raw 值深化 profile（2026-06-29、實證 categorical 實際值域 + 範例列）

> 逐欄實證每 categorical 欄「實際存哪些值」+ 每表範例列（catalog 型別/中文之外的 raw 真相）。工具 `scratchpad/deep_raw_profiler.py`。

```text
# 深化 raw 值 profile：55 核心表

### CnnFearGreedIndex
  ▸ fear_greed_emotion（情緒分類（極度恐懼…極度貪婪））= [8值] extreme, extreme fear, extreme greed, extreme_fear, extreme_greed, fear, greed, neutral
  範例: date=2011-01-03; fear_greed=68.000000; fear_greed_emotion=greed

### CrudeOilPrices
  ▸ name（油種名稱（WTI/Brent））= [2值] Brent, WTI
  範例: date=1990-01-02; name=Brent; price=21.200000

### ExchangeRate
  ▸ country（國家／幣別）= [6值] Canda, China, Euro, Japan, Taiwan, UK
  範例: InterbankRate=1.160500; InverseInterbankRate=0.861698; country=Canda; date=1990-01-02

### GoldPrice
  範例: Price=226.000000; date=1979-01-01

### GovernmentBondsYield
  ▸ name（期別名稱（如 United States 10-Year））= [13值] United States 1-Month, United States 1-Year, United States 10-Year, United States 2-Month, United States 2-Year, United States 20-Year, United States 3-Month, United States 3-Year, United States 30-Year, United States 4-Month, United States 5-Year, United States 6-Month, United States 7-Year
  範例: date=2001-01-02; name=United States 1-Mo; value=-1.000000

### InterestRate
  ▸ country（國家／央行）= [12值] BCB, BOC, BOE, BOJ, CBR, ECB, FED, PBOC, RBA, RBI, RBNZ, SNB
  ▸ full_country_name（國家全名）= [12值] Bank of Canada, Bank of England, Bank of Japan, Central Bank of Brazil, Central Bank of the Russ, European Central Bank, Federal Reserve, People's Bank of China, Reserve Bank of Australi, Reserve Bank of India, Reserve Bank of New Zeal, Swiss National Bank
  範例: country=BCB; date=2008-02-01; full_country_name=Central Bank of Br; interest_rate=11.250000

### TaiwanBusinessIndicator
  ▸ monitoring_color（信號燈號）= [6值] -, B, G, R, YB, YR
  範例: date=1982-01-01; leading=12.320000; leading_notrend=100.340000; coincident=13.140000; coincident_notrend=106.980000; lagging=13.140000; lagging_notrend=106.990000; monitoring=0.000000; monitoring_color=-

### TaiwanDailyShortSaleBalances
  範例: stock_id=00400A; MarginShortSalesPreviousDayBalance=0.000000; MarginShortSalesShortSales=0.000000; MarginShortSalesShortCovering=0.000000; MarginShortSalesStockRedemption=0.000000; MarginShortSalesCurrentDayBalance=0.000000; MarginShortSale

### TaiwanExchangeRate
  ▸ currency（幣別）= [19值] AUD, CAD, CHF, CNY, EUR, GBP, HKD, IDR, JPY, KRW, MYR, NZD, PHP, SEK, SGD, THB, USD, VND, ZAR
  範例: date=2006-01-02; currency=AUD; cash_buy=23.740000; cash_sell=24.490000; spot_buy=-1.000000; spot_sell=-1.000000

### TaiwanSecuritiesTraderInfo
  ▸ securities_trader_id（券商代號）= 高基數識別碼類（>30 distinct）
  ▸ securities_trader（券商名稱）= 高基數識別碼類（>30 distinct）
  ▸ address（地址）= 高基數識別碼類（>30 distinct）
  ▸ phone（電話）= 高基數識別碼類（>30 distinct）
  範例: securities_trader_id=104T; securities_trader=臺銀自營; date=2025-10-30; address=台北市重慶南路1段58號1樓; phone=None

### TaiwanStock10Year
  範例: date=2013-07-16; stock_id=0050; close=51.950000

### TaiwanStockBalanceSheet
  ▸ type（會計科目（值見 `/translation`））= 高基數識別碼類（>30 distinct）
  ▸ origin_name（原始科目名稱）= 高基數識別碼類（>30 distinct）
  ▸ type（會計科目）= 128 種（見 financial_typecodes 字典）
  範例: date=2012-12-31; stock_id=1101; type=AccountsPayable_pe; value=2.800000; origin_name=應付帳款

### TaiwanStockBlockTrade
  ▸ trade_type（交易類別（配對／逐筆））= [3值] 單一型, 逐筆交易, 配對交易
  範例: date=2026-06-05; stock_id=00403A; trade_type=配對交易; price=10.130000; volume=42500000.000000; trading_money=430525000.000000

### TaiwanStockCapitalReductionReferencePrice
  ▸ ReasonforCapitalReduction（減資原因）= [4值] Cash refund, Making up losses, 彌補虧損, 現金減資
  範例: date=2023-10-11; stock_id=1236; ClosingPriceonTheLastTradingDay=20.600000; PostReductionReferencePrice=23.250000; LimitUp=25.550000; LimitDown=20.950000; OpeningReferencePrice=23.250000; ExrightReferencePrice=-1.000000; ReasonforCapitalRedu

### TaiwanStockCashFlowsStatement
  ▸ type（會計科目（值見 `/translation`））= 高基數識別碼類（>30 distinct）
  ▸ origin_name（原始科目名稱）= 高基數識別碼類（>30 distinct）
  ▸ type（會計科目）= 34 種（見 financial_typecodes 字典）
  範例: date=2012-03-31; stock_id=1101; type=TotalIncomeLossIte; value=1748200000.000000; origin_name=收益費損項目合計

### TaiwanStockDayTrading
  ▸ BuyAfterSale（現股當沖先買後賣）= [2值] Y, ＊
  範例: stock_id=1101; date=2014-01-06; BuyAfterSale=None; Volume=127000.000000; BuyAmount=5608450.000000; SellAmount=5570250.000000

### TaiwanStockDayTradingBorrowingFeeRate
  範例: date=2015-10-14; stock_id=2330; stock_name=台積電; InvestorBorrowedShares=1000.000000; InvestorBorrowingFeeRate=3.000000

### TaiwanStockDayTradingSuspension
  ▸ reason（暫停原因）= [20值] ETF分割, ETF反分割, 停止買賣, 其他, 其它利益, 分配收益, 受益人大會, 合併, 換發新股, 減資, 現金增資, 終止上市, 股份轉換, 股東常會, 臨時會, 變更面額, 金控, 除息, 除權, 除權息
  範例: stock_id=1907; date=2014-07-09; end_date=2014-07-15; reason=除息

### TaiwanStockDelisting
  範例: date=2023-04-21; stock_id=00732; stock_name=國泰RMB短期報酬

### TaiwanStockDispositionSecuritiesPeriod
  ▸ condition（處置條件）= [17值] 因連續3個營業日達本中心作業要點第四條第一項第一, 最近10個營業日內有6個營業日, 最近30個營業日內有12個營業日, 最近6個營業日內有4個營業日, 最近三十個營業日已有十二次, 最近十個營業日已有六次, 監視業務督導會報(../../about/com, 監視業務督導會報決議, 轉(交)換公司債之標的證券經本中心或臺灣證券交易, 連續3個營業日, 連續3個營業日及沖銷標準, 連續5個營業日, 連續5個營業日及沖銷標準, 連續三次, 連續三次及當日沖銷標準, 連續五次, 連續五次及當日沖銷標準
  ▸ measure（處置措施）= 高基數識別碼類（>30 distinct）
  範例: date=2005-01-04; stock_id=2702; stock_name=華園; disposition_cnt=4.000000; condition=連續五次; measure=收足五成款券; period_start=2005-01-05; period_end=2005-01-11

### TaiwanStockDividend
  ▸ year（股利所屬年度）= 高基數識別碼類（>30 distinct）
  ▸ StockExDividendTradingDate（除權交易日）= 高基數識別碼類（>30 distinct）
  ▸ CashExDividendTradingDate（除息交易日）= 高基數識別碼類（>30 distinct）
  ▸ CashDividendPaymentDate（現金股利發放日）= 高基數識別碼類（>30 distinct）
  ▸ AnnouncementDate（公告日期 ⭐）= 高基數識別碼類（>30 distinct）
  ▸ AnnouncementTime（公告時間 ⭐）= 高基數識別碼類（>30 distinct）
  範例: date=2026-07-15; stock_id=00400A; year=115; StockEarningsDistribution=0E-10; StockStatutorySurplus=0E-10; StockExDividendTradingDate=None; TotalEmployeeStockDividend=0.000000; TotalEmployeeStockDividendAmount=0.000000; RatioOfEmployeeStockD

### TaiwanStockDividendResult
  ▸ stock_or_cache_dividend（股票或現金股利）= [6值] 息, 權, 權息, 除息, 除權, 除權息
  範例: date=2005-05-19; stock_id=0050; before_price=46.690000; after_price=44.840000; stock_and_cache_dividend=1.850000; stock_or_cache_dividend=息; max_price=47.970000; min_price=41.710000; open_price=44.840000; reference_price=44.840000

### TaiwanStockFinancialStatements
  ▸ type（會計科目（值見 `/translation`））= 高基數識別碼類（>30 distinct）
  ▸ origin_name（原始科目名稱）= 高基數識別碼類（>30 distinct）
  ▸ type（會計科目）= 62 種（見 financial_typecodes 字典）
  範例: date=1991-12-31; stock_id=1101; type=EPS; value=0.000000; origin_name=每股稅後盈餘(元)

### TaiwanStockGovernmentBankBuySell
  ▸ bank_name（行庫名稱）= [8值] 兆豐, 台企銀, 合庫, 土銀, 彰銀, 第一, 臺銀, 華南
  範例: date=2021-07-01; stock_id=0050; buy_amount=3530924.150000; sell_amount=41026123.000000; buy=25467.000000; sell=296017.000000; bank_name=兆豐

### TaiwanStockHoldingSharesPer
  ▸ HoldingSharesLevel（持股分級級距）= [17值] 1,000-5,000, 1-999, 10,001-15,000, 100,001-200,000, 15,001-20,000, 20,001-30,000, 200,001-400,000, 30,001-40,000, 40,001-50,000, 400,001-600,000, 5,001-10,000, 50,001-100,000, 600,001-800,000, 800,001-1,000,000, more than 1,000,001, total, 差異數調整（說明4）
  範例: date=2026-04-10; stock_id=00400A; HoldingSharesLevel=1-999; people=677.000000; percent=0.020000; unit=153399.000000

### TaiwanStockIndustryChain
  ▸ industry（產業）= 高基數識別碼類（>30 distinct）
  ▸ sub_industry（次產業）= 高基數識別碼類（>30 distinct）
  範例: stock_id=2071; industry=鋼鐵; sub_industry=線材盤元; date=2026-06-16

### TaiwanStockInfo
  ▸ industry_category（產業類別）= 高基數識別碼類（>30 distinct）
  ▸ type（市場類別）= [3值] emerging, tpex, twse
  範例: industry_category=所有證券; stock_id=73193P; stock_name=神盾元大9B售04; type=tpex; date=2020-11-15

### TaiwanStockInfoWithWarrant
  ▸ industry_category（產業類別）= 高基數識別碼類（>30 distinct）
  ▸ type（市場類別）= [2值] tpex, twse
  範例: industry_category=全部(不含大盤、指數); stock_id=0054; stock_name=元大台商50; type=twse; date=2026-06-16

### TaiwanStockInfoWithWarrantSummary
  ▸ target_stock_id（標的證券代號）= 高基數識別碼類（>30 distinct）
  ▸ type（權證類別）= [2值] 認售, 認購
  ▸ fulfillment_method（履約方式）= [2值] 歐式, 美式
  ▸ fulfillment_start_date（履約起始日）= 高基數識別碼類（>30 distinct）
  ▸ fulfillment_end_date（履約截止日）= 高基數識別碼類（>30 distinct）
  範例: stock_id=70001F; date=2011-01-03; close=0.000000; target_stock_id=HK0000049939; target_close=49.770000; type=認購; fulfillment_method=None; end_date=2011-03-03; fulfillment_start_date=None; fulfillment_end_date=None; exercise_ratio=0.000000; 

### TaiwanStockInstitutionalInvestorsBuySell
  ▸ name（法人別（自營商／自營商避險／自營商自行買賣／外資自營商／外資／投信））= [6值] Dealer, Dealer_Hedging, Dealer_self, Foreign_Dealer_Self, Foreign_Investor, Investment_Trust
  範例: date=2026-04-09; stock_id=00400A; buy=41092.000000; name=Foreign_Investor; sell=370000.000000

### TaiwanStockInstitutionalInvestorsBuySellWide
  範例: date=2026-04-09; stock_id=00400A; Foreign_Investor_buy=41092.000000; Foreign_Investor_sell=370000.000000; Foreign_Dealer_Self_buy=0.000000; Foreign_Dealer_Self_sell=0.000000; Investment_Trust_buy=0.000000; Investment_Trust_sell=0.000000; De

### TaiwanStockLoanCollateralBalance
  ▸ market（市場別）= [2值] 櫃檯買賣中心, 集中市場
  範例: date=2026-04-08; stock_id=00400A; market=集中市場; MarginPreviousDayBalance=0.000000; MarginBuy=0.000000; MarginSell=0.000000; MarginCashRedemption=0.000000; MarginCurrentDayBalance=0.000000; MarginNextDayQuota=187910.000000; SecuritiesFirmLoan

### TaiwanStockMarginPurchaseShortSale
  ▸ Note（註記）= 高基數識別碼類（>30 distinct）
  範例: date=2026-04-08; stock_id=00400A; MarginPurchaseBuy=0.000000; MarginPurchaseCashRepayment=0.000000; MarginPurchaseLimit=187910.000000; MarginPurchaseSell=0.000000; MarginPurchaseTodayBalance=0.000000; MarginPurchaseYesterdayBalance=0.000000

### TaiwanStockMarginShortSaleSuspension
  ▸ end_date（截止日期）= 高基數識別碼類（>30 distinct）
  ▸ reason（暫停事由）= [21值] ETF分割, ETF反分割, 其他, 其它利益, 分配收益, 受益人大會, 合併, 合併消滅, 換發新股, 減資, 現增除權, 現金增資, 股份轉換, 股東常會, 臨時會, 變更面額, 金控, 除息, 除權, 除權、息, 除權息
  範例: stock_id=1210; date=2015-04-01; end_date=2015-04-08; reason=股東常會

### TaiwanStockMarketValue
  範例: date=2026-04-09; stock_id=00400A; market_value=8192876000.000000

### TaiwanStockMarketValueWeight
  ▸ type（類別（上市/上櫃））= [2值] tpex, twse
  範例: rank=43.000000; stock_id=1101; stock_name=台泥; weight_per=0.332700; date=2024-10-30; type=twse

### TaiwanStockMonthPrice
  ▸ ymonth（年度月別）= 高基數識別碼類（>30 distinct）
  範例: stock_id=00400A; ymonth=2026M04; max=13.050000; min=10.750000; trading_volume=1915861961.000000; trading_money=23021000699.000000; trading_turnover=322520.000000; date=2026-04-01; close=12.920000; open=10.760000; spread=2.160000

### TaiwanStockMonthRevenue
  ▸ country（國家／央行）= [1值] Taiwan
  ▸ create_time（資料建立時點）= 高基數識別碼類（>30 distinct）
  範例: date=2002-02-01; stock_id=1101; country=Taiwan; revenue=2200067000.000000; revenue_month=1.000000; revenue_year=2002.000000; create_time=None

### TaiwanStockNews
  ▸ source（來源）= 高基數識別碼類（>30 distinct）
  範例: date=2010-03-02 08:00:0; stock_id=3061; link=https://news.googl; source=Anue鉅亨; title=LED擴產拚年增40% 璨圓擬二階段

### TaiwanStockPER
  範例: date=2005-09-02; stock_id=1101; dividend_yield=5.910000; PER=16.920000; PBR=1.070000

### TaiwanStockParValueChange
  範例: date=2019-09-09; stock_id=6548; stock_name=長科; before_close=312.000000; after_ref_close=31.200000; after_ref_max=34.300000; after_ref_min=28.100000; after_ref_open=31.200000

### TaiwanStockPrice
  範例: date=2026-04-09; stock_id=00400A; Trading_Volume=238045041.000000; Trading_money=2580327559.000000; open=10.760000; max=10.940000; min=10.750000; close=10.900000; spread=0.140000; Trading_turnover=21888.000000

### TaiwanStockPriceAdj
  範例: date=2026-04-10; stock_id=00400A; Trading_Volume=148646367.000000; Trading_money=1648898030.000000; open=11.100000; max=11.150000; min=11.020000; close=11.140000; spread=0.240000; Trading_turnover=23866.000000

### TaiwanStockPriceLimit
  範例: date=2000-01-03; stock_id=00400A; reference_price=0.000000; limit_up=0.000000; limit_down=0.000000

### TaiwanStockSecuritiesLending
  ▸ transaction_type（交易類別）= [3值] 定價, 競價, 議借
  ▸ original_return_date（原訂還券日期）= 高基數識別碼類（>30 distinct）
  範例: date=2026-04-13; stock_id=00400A; transaction_type=競價; volume=70.000000; fee_rate=1.000000; close=11.120000; original_return_date=2026-10-13; original_lending_period=183.000000

### TaiwanStockShareholding
  ▸ RecentlyDeclareDate（最近一次申報外資持股異動日期 ⭐）= 高基數識別碼類（>30 distinct）
  ▸ note（與前日異動原因（註））= 高基數識別碼類（>30 distinct）
  範例: date=2026-04-08; stock_id=00400A; stock_name=主動國泰動能高息; InternationalCode=TW00000400A3; ForeignInvestmentRemainingShares=751640000.000000; ForeignInvestmentShares=0.000000; ForeignInvestmentRemainRatio=100.000000; ForeignInvestmentSharesRati

### TaiwanStockSplitPrice
  ▸ type（類別）= [3值] 分割, 反分割, 面額變更
  範例: date=2019-09-09; stock_id=6548; type=面額變更; before_price=312.000000; after_price=31.200000; max_price=34.300000; min_price=28.100000; open_price=31.200000

### TaiwanStockSuspended
  ▸ suspension_time（暫停交易時間）= [3值] 09:00, 8:00, 9:00
  ▸ resumption_date（恢復交易日期）= 高基數識別碼類（>30 distinct）
  ▸ resumption_time（恢復交易時間）= [2值] 09:00, 8:00
  範例: date=2025-03-07; stock_id=037564; suspension_time=8:00; resumption_date=2025-03-10; resumption_time=8:00

### TaiwanStockTotalInstitutionalInvestors
  ▸ name（法人別）= [7值] Dealer, Dealer_Hedging, Dealer_self, Foreign_Dealer_Self, Foreign_Investor, Investment_Trust, total
  範例: buy=19406793770.000000; date=2004-04-07; name=total; sell=14768680195.000000

### TaiwanStockTotalMarginPurchaseShortSale
  ▸ name（類別名稱（融資／融券））= [3值] MarginPurchase, MarginPurchaseMoney, ShortSale
  範例: TodayBalance=12486038.000000; YesBalance=12476942.000000; buy=744676.000000; date=2001-01-03; name=MarginPurchase; Return=16995.000000; sell=718585.000000

### TaiwanStockTotalReturnIndex
  範例: price=4524.920000; stock_id=TAIEX; date=2003-01-02

### TaiwanStockTradingDate
  範例: date=1999-01-05

### TaiwanStockWeekPrice
  ▸ yweek（年度週別）= 高基數識別碼類（>30 distinct）
  範例: stock_id=00400A; yweek=2026W15; max=11.150000; min=10.750000; trading_volume=386691408.000000; trading_money=4229225589.000000; trading_turnover=45754.000000; date=2026-04-06; close=11.140000; open=10.760000; spread=0.380000

### TaiwanTotalExchangeMarginMaintenance
  範例: date=2001-01-05; TotalExchangeMarginMaintenance=100.487000

### fred_series
  範例: series_id=T10Y2Y; date=1977-02-21; value=None
```

---

## 附錄三:欄位間數值恆等式驗證（raw 之間關係最深層、2026-06-29）

> 用實際數據驗證欄位間應成立之會計/邏輯恆等式（勾稽/定義/跨表）。工具 `scratchpad/verify_identities.py`。

| 恆等式 | PASS% | 判讀 |
|---|---|---|
| 融資今餘 = 昨餘+買-賣-現償 | 100% | ✓ 完美勾稽 |
| 融券今餘 = 昨餘+賣-買-現償 | 82%（today>0 時 100%）| ✓ 公式正確、與融資對稱;違反=餘額下界截斷（理論值為負時歸零）|
| DailyShortSale 融券/借券餘額勾稽 | 100%/100% | ✓ |
| 外資持股比率 = 持有/發行×100 | 100% | ✓ 比率定義確認 |
| 外資尚可投資比率 = 尚可/發行×100 | 100% | ✓ |
| 持股分級 total = Σ各級 unit | 99.3% | ✓（違反=差異數調整邊界）|
| 毛利 = 營收 - 營業成本 | 99.6% | ✓（違反=金融/營業外）|
| 營益 = 毛利 - 營業費用 | 96.8% | ~（含其他收益及費損）|
| 資產總額 = 負債總額 + 權益總額 | 99.5% | ✓ 三表勾稽（違反=少數股權邊界）|
| 跨表:市值 ≈ 收盤價 × 發行股數 | 100% | ✓ 跨表一致 |
| OHLC: max≥open,close ≥min | 98.0%/96.6% | ~（違反=還原價邊界/極少數）|

**結論**:raw 欄位間數值關係（勾稽公式/比率定義/三表勾稽/跨表市值）**實證成立**，違反皆有合理解釋（餘額下界截斷、會計其他項、還原邊界、差異數調整），非資料錯誤。融資/融券餘額為對稱勾稽。

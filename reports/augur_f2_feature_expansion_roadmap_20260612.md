# augur F2 特徵覆蓋擴展 roadmap — 82 表四分類 → 特徵設計(2026-06-12)

**性質**:規劃文件(#15:本檔為**計畫、非成果**;所有特徵/數字落地後才算數)。
**目的**:回答「core_gate 能否完整明確涵蓋所有表所有欄位」——gate 機制已 data-driven 自動擴覆蓋
(canonical 特徵集由資料判定),**該擴的是 feature 層(builder)**;本檔給出 82 表如何逐類入特徵的完整路線。
**地基(#20 實證)**:分類依 schema catalog 之**實證屬性**(PK 含否 `stock_id`、取樣 mode)+ 顯式語意覆寫
(覆寫清單見產生程式,逐表可審);非憑記憶。

---

## 一、四分類判準

| 類 | 定義 | 入 gate 方式 | 數 |
|---|---|---|---|
| **P** 個股連續型 | `stock_id` 維度、週期規律(日/週/月/季) | 算特徵 → `feature_values` → 缺列即排除(現行 gate 直接吃) | 22 |
| **E** 個股事件型 | `stock_id` 維度、稀疏(有事才有列) | **真零語意**:表級 #7 PASS 前提下「無列=真 0」;特徵=count/days-since/flag,全 roster 皆可得真值 → **不以無事件排除股** | 12 |
| **X** 市場 context | 無 `stock_id`(指數/匯率/期權/總經/國際) | 入 `context_values`(僅 panel_date 維度)→ **panel 前提**:context 缺 = 該 panel 無效,**非排除個股** | 36 |
| **R** 參照/基礎 | 名冊/日曆/屬性/下市 | 供 roster·survivorship(#8)·交易日曆·categorical 屬性;非數值特徵源 | 12 |

> P 中 4 張財報/營收表標 **P-lag**:必須過「發布日 gate」才可用(見三)。

## 二、82 表完整分類總表

| 分類 | 表(API 原樣) | 欄 | stock_id | 類 | 備註 |
|---|---|---|---|---|---|
| A | `TaiwanBusinessIndicator` | 9 | — | **X** |  |
| A | `TaiwanExchangeRate` | 6 | — | **X** |  |
| A | `TaiwanStock10Year` | 3 | ✔ | **P** |  |
| A | `TaiwanStockDayTrading` | 6 | ✔ | **P** |  |
| A | `TaiwanStockDayTradingBorrowingFeeRate` | 5 | ✔ | **P** |  |
| A | `TaiwanStockDayTradingSuspension` | 4 | ✔ | **E** |  |
| A | `TaiwanStockIndustryChain` | 4 | ✔ | **R** |  |
| A | `TaiwanStockInfo` | 5 | ✔ | **R** |  |
| A | `TaiwanStockInfoWithWarrant` | 5 | ✔ | **R** |  |
| A | `TaiwanStockInfoWithWarrantSummary` | 12 | ✔ | **R** |  |
| A | `TaiwanStockMonthPrice` | 11 | ✔ | **P** |  |
| A | `TaiwanStockNews` | 5 | ✔ | **E** |  |
| A | `TaiwanStockPrice` | 10 | ✔ | **P** |  |
| A | `TaiwanStockPriceAdj` | 10 | ✔ | **P** |  |
| A | `TaiwanStockPriceLimit` | 5 | ✔ | **P** |  |
| A | `TaiwanStockSuspended` | 5 | ✔ | **E** |  |
| A | `TaiwanStockTotalReturnIndex` | 3 | ✔ | **X** |  |
| A | `TaiwanStockTradingDate` | 1 | — | **R** |  |
| A | `TaiwanStockWeekPrice` | 11 | ✔ | **P** |  |
| B | `TaiwanDailyShortSaleBalances` | 15 | ✔ | **P** |  |
| B | `TaiwanSecuritiesTraderInfo` | 5 | — | **R** |  |
| B | `TaiwanStockBlockTrade` | 6 | ✔ | **E** |  |
| B | `TaiwanStockDispositionSecuritiesPeriod` | 8 | ✔ | **E** |  |
| B | `TaiwanStockGovernmentBankBuySell` | 7 | ✔ | **E** |  |
| B | `TaiwanStockHoldingSharesPer` | 6 | ✔ | **P** |  |
| B | `TaiwanStockInstitutionalInvestorsBuySell` | 5 | ✔ | **P** |  |
| B | `TaiwanStockLoanCollateralBalance` | 37 | ✔ | **P** |  |
| B | `TaiwanStockMarginPurchaseShortSale` | 16 | ✔ | **P** |  |
| B | `TaiwanStockMarginShortSaleSuspension` | 4 | ✔ | **E** |  |
| B | `TaiwanStockSecuritiesLending` | 8 | ✔ | **P** |  |
| B | `TaiwanStockShareholding` | 13 | ✔ | **P** |  |
| B | `TaiwanStockTotalInstitutionalInvestors` | 4 | — | **X** |  |
| B | `TaiwanStockTotalMarginPurchaseShortSale` | 7 | — | **X** |  |
| C | `TaiwanStockBalanceSheet` | 5 | ✔ | **P** | P-lag(發布日 gate 必須) |
| C | `TaiwanStockCapitalReductionReferencePrice` | 9 | ✔ | **E** |  |
| C | `TaiwanStockCashFlowsStatement` | 5 | ✔ | **P** | P-lag(發布日 gate 必須) |
| C | `TaiwanStockDelisting` | 3 | ✔ | **R** |  |
| C | `TaiwanStockDividend` | 22 | ✔ | **E** |  |
| C | `TaiwanStockDividendResult` | 10 | ✔ | **E** |  |
| C | `TaiwanStockFinancialStatements` | 5 | ✔ | **P** | P-lag(發布日 gate 必須) |
| C | `TaiwanStockMarketValue` | 3 | ✔ | **P** |  |
| C | `TaiwanStockMarketValueWeight` | 6 | ✔ | **P** |  |
| C | `TaiwanStockMonthRevenue` | 7 | ✔ | **P** | P-lag(發布日 gate 必須) |
| C | `TaiwanStockPER` | 5 | ✔ | **P** |  |
| C | `TaiwanStockParValueChange` | 8 | ✔ | **E** |  |
| C | `TaiwanStockSplitPrice` | 8 | ✔ | **E** |  |
| D | `TaiwanStockConvertibleBondDaily` | 16 | — | **X** |  |
| D | `TaiwanStockConvertibleBondDailyOverview` | 23 | — | **X** |  |
| D | `TaiwanStockConvertibleBondInfo` | 5 | — | **R** |  |
| D | `TaiwanStockConvertibleBondInstitutionalInvestors` | 13 | — | **X** |  |
| E | `TaiwanFutOptDailyInfo` | 3 | — | **X** |  |
| E | `TaiwanFutOptInstitutionalInvestors` | 11 | — | **X** |  |
| E | `TaiwanFutOptTickInfo` | 7 | — | **X** |  |
| E | `TaiwanFuturesDaily` | 13 | — | **X** |  |
| E | `TaiwanFuturesDealerTradingVolumeDaily` | 6 | — | **X** |  |
| E | `TaiwanFuturesFinalSettlementPrice` | 8 | — | **X** |  |
| E | `TaiwanFuturesInstitutionalInvestors` | 11 | — | **X** |  |
| E | `TaiwanFuturesInstitutionalInvestorsAfterHours` | 7 | — | **X** |  |
| E | `TaiwanFuturesOpenInterestLargeTraders` | 21 | — | **X** |  |
| E | `TaiwanFuturesSpreadTick` | 9 | — | **X** |  |
| E | `TaiwanFuturesSpreadTrading` | 14 | — | **X** |  |
| E | `TaiwanOptionDaily` | 13 | — | **X** |  |
| E | `TaiwanOptionDealerTradingVolumeDaily` | 6 | — | **X** |  |
| E | `TaiwanOptionFinalSettlementPrice` | 8 | — | **X** |  |
| E | `TaiwanOptionInstitutionalInvestors` | 12 | — | **X** |  |
| E | `TaiwanOptionInstitutionalInvestorsAfterHours` | 8 | — | **X** |  |
| E | `TaiwanOptionOpenInterestLargeTraders` | 22 | — | **X** |  |
| E | `TaiwanTotalExchangeMarginMaintenance` | 2 | — | **X** |  |
| F | `EuropeStockInfo` | 4 | ✔ | **R** |  |
| F | `EuropeStockPrice` | 8 | ✔ | **X** |  |
| F | `JapanStockInfo` | 5 | ✔ | **R** |  |
| F | `JapanStockPrice` | 8 | ✔ | **X** |  |
| F | `UKStockInfo` | 4 | ✔ | **R** |  |
| F | `UKStockPrice` | 8 | ✔ | **X** |  |
| F | `USStockInfo` | 7 | ✔ | **R** |  |
| F | `USStockPrice` | 8 | — | **X** |  |
| G | `CnnFearGreedIndex` | 3 | — | **X** |  |
| G | `CrudeOilPrices` | 3 | — | **X** |  |
| G | `GoldPrice` | 2 | — | **X** |  |
| G | `GovernmentBondsYield` | 3 | — | **X** |  |
| G | `InterestRate` | 4 | — | **X** |  |
| G | `fred_series` | 3 | — | **X** |  |

## 三、Anti-leakage 設計點(#8,入特徵前的硬要求)

1. **P-lag 財報四表**(BalanceSheet/CashFlows/FinancialStatements/MonthRevenue):FinMind `date`=**報表期末日,非公告日**。
   panel t 只能用「t 時點已公告」的最近期報表。處置順序:(a) **先 probe API 有無公告日欄位**(實證,勿假設);
   (b) 無 → 用**法定申報期限**做保守 lag(季報 Q1≤5/15、Q2≤8/14、Q3≤11/14、年報≤3/31;月營收≤次月 10 日)。
   此為 **operational/anti-leakage 層之透明揭露參數**(同 #17 模式),非 feature 值、不違 #9。
2. **籌碼/法人 T+1 時點**:盤後公布 → panel t 收盤決策時點是否可得**待逐表實證**(公布時刻 probe);保守預設 shift(1)。
3. **FRED vintage 警示**(既有記憶):總經值事後修訂,最新值回測=look-ahead;嚴格 PIT 需 ALFRED/vintage。
   F2e 先以「發布滯後保守 lag」處理 + 在 context 特徵 metadata 標 vintage 風險;ALFRED 列後續選項。
4. **事件型之「真 0」前提**:唯該表全史 sync 完成 ∧ #7 對帳 PASS,才能宣稱「無列=真無事件」;否則=「未抓」≠0(#1)。

## 四、架構整合(gate 不需改)

- `feature_values`(個股,既有)+ **新 `context_values`(panel_date, feature, value)**;模型層 join 廣播。
- 新 **panel 有效性檢查**:panel 之 context 完整才成立(X 類缺 → 整 panel 無效,非排除股)。
- **core_universe 加 as-of 快照維度**(F3 walk-forward 前置:逐 rebalance 日當期名單,#8)。
- `core_gate.py` 機制不變(純完整度、data-driven canonical 集);E/X 類特徵因「全 roster 皆有真值」不會誤殺。
- **R 類落點**:TaiwanStockInfo+Delisting → 歷史宇宙(survivorship #8);TradingDate → 交易日曆 SSOT;IndustryChain → categorical。

## 五、分期執行(每期前置:該表全史 sync 完成 ∧ #7 PASS ∧ 發布時點判準記錄)

| 期 | 範圍(類) | 表數 | 特徵族 | 風險 |
|---|---|---|---|---|
| F2b 籌碼/法人 | P(B 類 7 張:法人買賣/融資券/借券/持股/質押) | ~7 | 流向 rolling sum/ratio/z、籌碼集中度 | 公布時點待實證 |
| F2c 估值/市值 | P(PER/MarketValue/Weight/10Year 等日頻) | ~5 | 估值水位/排名、市值規模 | 低 |
| F2d 基本面 | **P-lag** 財報 3+月營收 | 4 | YoY/QoQ/margin/成長動能 | **發布日 gate(三.1)** |
| F2e 市場 context | X(台指/匯率/利率/總經/FRED/商品/情緒) | ~15 | regime/利差/動能 context | FRED vintage(三.3) |
| F2f 事件型 | E 12 張 | 12 | days-since/count-window/flag(真零) | 真 0 前提(三.4);News 僅 count(#9 禁情緒字典) |
| F2g 衍生/國際/CB | X 其餘(期權 18/國際 5/CB 3) | ~21 | TX 基差/PCR/未平倉、國際大盤、CB 溢價 | 維度 mapping 較重 |

## 六、鐵則與不做

- **#9 紅線**:無 sentiment/theme 字典、無 hardcoded 閾值入 feature 公式;News 只做 count/presence。
- **OUT_OF_UNIT 3 表**(分點/權證/鉅額日報)維持 operational 暫緩;intraday 8 永排(#4)。
- 任何特徵「算不出即缺列」(#1);任何宣稱數字 source-traceable(#15)。

## 七、待實證清單(落地前逐項 probe/查證)

- [ ] 財報/月營收 API 公告日欄位有無(三.1a)
- [ ] 籌碼各表公布時刻(三.2)
- [ ] `TaiwanStockTotalReturnIndex` stock_id 語意(=TAIEX/TPEx 指數,已歸 X;落地時再證)
- [ ] `USStockPrice` PK 無 stock_id 之語意(疑大盤序列)
- [ ] `MonthRevenue` `country` 維度語意
- [ ] catalog 未取樣 1 表(82 候選−81 已建)身分與補樣
- [ ] InfoWithWarrantSummary 歸 R 之再確認(12 欄含量值,或可升 P)

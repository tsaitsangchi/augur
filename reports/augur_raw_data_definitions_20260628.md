# augur Raw Data 定義參考 — 全 84 表據實 profile(2026-06-28)

> **性質**:據實資料字典(非「我以為」)——`scripts/profile_raw_data.py` 對全 84 表逐欄/逐 type 跑列數/日期/null/值域(min/p50/max)/累計語意 + join column_catalog 中文名。**供真懂全部定義、標出髒值與語意陷阱**(#15)。
> **核心結論**:台股單股訊號表 ~25 已深用;**財報三表語意已釐清**(見 §D);多數髒值哨兵已知並由特徵層擋掉;國際/衍生/商品多為 context 或 out-of-scope。

---

## A. 台股價量(核心訊號源)

| 表 | 列/期 | 關鍵欄 + 語意/髒值 |
|---|---|---|
| `TaiwanStockPrice` | 11.1M、1994+ | OHLC/量/額/筆數(原始價);**close 等 min=0＝停牌哨兵(~28萬列)** → 特徵層用 PriceAdj+close>0 擋 |
| `TaiwanStockPriceAdj` | 11.1M、1994+ | **還原價(特徵層 SSOT)**;close p50 19.71(還原<原始);亦有 close=0(filter 掉)|
| `TaiwanStockPriceLimit` | 11.9M、2000+ | 參考價/漲停/跌停 |
| `TaiwanStock10Year` | 5.4M、2011+ | **各股 10 年均線收盤**(跨股 1.17~15730)、非單一大盤;price_to_10yr 用 |
| `TaiwanStockMonthPrice`/`WeekPrice` | 月/週頻 OHLC量 | 低頻價(未用)|
| `TaiwanStockTradingDate` | 6937、1999-2026 | 交易日曆(含未來到 2026-12-31)|

## B. 台股籌碼 / 法人 / 信用(核心)

| 表 | 列/期 | 關鍵欄 + 語意 |
|---|---|---|
| `TaiwanStockInstitutionalInvestorsBuySell` | 24.9M、2012+ | long-format、5 玩家(外資/外資自營/投信/自營/自營避險)buy/sell;buy 有負值(更正)|
| `...BuySellWide` | 5.5M | 寬表版(各玩家 buy/sell 分欄)|
| `TaiwanStockMarginPurchaseShortSale` | 8.0M、2001+ | 融資券 13 欄:融資買賣/餘額/限額、**融券**買賣/餘額(ShortSale*)、資券相抵 |
| `TaiwanDailyShortSaleBalances` | 7.7M、2005+ | 融券+借券(SBL)餘額/賣出/回補/限額 13 欄;SBLShortSalesAdjustments/Covering 可負 |
| `TaiwanStockLoanCollateralBalance` | 5.3M、2006+ | 融資/券商借貸/不限用途/證金擔保/交割保證金 各前日-買-賣-償-餘-限額(信用全貌)|
| `TaiwanStockSecuritiesLending` | 735K、2003+ | 借券成交量/**費率(0-20)**/收盤/原訂借券期間 |
| `TaiwanStockGovernmentBankBuySell` | 13.7M、**2021-07+** | 八大行庫 buy/sell 股數+金額;**早期無資料→特徵層真零 gate(chip._table_covers)** |
| `TaiwanStockHoldingSharesPer` | 20.7M、2010+ | 持股分級:people/percent/unit;**percent 可負(-35.9、差異數調整 level)、>100(異常 125);unit 可負** |
| `TaiwanStockShareholding` | 8.8M、2004+ | 外資持股 7 欄:持有/尚可投資 股數+比率、上限、發行股數 |
| `TaiwanStockDayTrading` | 4.3M、2014+ | 當沖 Volume/BuyAmount/SellAmount |
| `TaiwanStockDayTradingBorrowingFeeRate` | 32K、2015+ | 當沖借券張數/費率 |
| `TaiwanStockTotalInstitutionalInvestors`/`TotalMarginPurchaseShortSale`/`TaiwanTotalExchangeMarginMaintenance` | 全市場 | 法人/信用/維持率大盤總量(context、非橫斷面)|

## C. 台股估值 / 市值

| 表 | 關鍵欄 + 髒值 |
|---|---|
| `TaiwanStockPER` | 7.6M、2005+;**PER min=-1＝虧損股哨兵(非真值、valuation.py per>0 擋)**;PBR max 1442、殖利率 max 306＝極端離群**未 winsorize** |
| `TaiwanStockMarketValue` | 8.5M;市值(元)min=0 髒值 |
| `TaiwanStockMarketValueWeight` | 90K、2024-10+;排名/市值權重% |

## D. 台股財報(long-format、發布日 gate 必須)— **語意已釐清**

| 表 | type 數 | **語意(關鍵!)** | 發布日 |
|---|---|---|---|
| `TaiwanStockFinancialStatements` | 62 | **單季**(Revenue/GrossProfit/OperatingIncome/EPS…非累計) | 季底+45/90日 |
| `TaiwanStockCashFlowsStatement` | 34 | **累計 YTD!**(capex=PropertyAndPlantAndEquipment、營業現金流…需去累計才得單季) | 季底+45/90日 |
| `TaiwanStockBalanceSheet` | 128 | **時點 snapshot**(存量、非流量);`X_per` 後綴＝**佔總資產%** | 季底+45/90日 |

> 財報金額單位＝**元**(p50 數億);EPS 單位元(min −669 虧損)。`release_lag.financial_release_date` 已實作 gate。

## E. 台股事件 / 公司行動

| 表 | 語意 |
|---|---|
| `TaiwanStockMonthRevenue` | 月營收(千元);**revenue 可負(更正/退回 −44億)**;發布日次月10日(`release_lag` gate)|
| `TaiwanStockDividend` | 股利政策:盈餘/公積 配股配息、員工配股、現增認購;**date=公告/分配基準日**(P-lag、事件稀疏 2411 列)|
| `TaiwanStockDividendResult` | 除權息參考價(前/後/配股息合計)|
| `TaiwanStockCapitalReductionReferencePrice`/`SplitPrice`/`ParValueChange` | 減資/分割/面額變更參考價(還原價來源)|
| `TaiwanStockDelisting`/`Suspended`/`DispositionSecuritiesPeriod`/`*Suspension` | 下市/暫停/處置/當沖+融券停資格(完整度/recency gate 相關)|
| `TaiwanStockInfo`/`InfoWithWarrant`/`IndustryChain` | 基本資料/含權證/產業鏈(IndustryChain 僅 3069 列、近日)|
| `TaiwanStockNews` | 新聞(2.5M、含時戳;NLP 用、未用)|

## F. 台股衍生品(out-of-scope 單股特徵、context 可能)

期貨/選擇權:`TaiwanFuturesDaily`/`TaiwanOptionDaily`(33.7M)/`*InstitutionalInvestors`/`*OpenInterestLargeTraders`(大額交易人未平倉占比)/`*FinalSettlementPrice`/`*Spread*`/`FutOpt*`/`*DealerTradingVolume*`。可轉債:`TaiwanStockConvertibleBond*`(Daily/Overview/Info/InstitutionalInvestors)。權證:`TaiwanStockInfoWithWarrantSummary`。**皆非台股單股橫斷面訊號;期權未平倉/大額交易人或可作 context regime。**

## G. 國際股(out-of-scope)— ⚠️ 嚴重髒值

`EuropeStockPrice`/`JapanStockPrice`(16.8M)/`UKStockPrice`(23.5M)/`USStockPrice`(35M)+ Info。**Adj_Close 有 overflow/負值髒值**(Japan ±1e38、UK −6.5e23、US −2788)→ **不可直接用**;Info 表多僅單日快照(2019-01-14)。

## H. 商品 / 總經 / 匯率 / 利率 / 指數(context、X 類)

| 表 | 語意 |
|---|---|
| `TaiwanBusinessIndicator` | **景氣 44 年(1982+)**:領先/同時/落後(+_notrend 去趨勢、中心~100)、monitoring 對策信號(0-42);regime 用(已驗 lead_nt_rising)|
| `fred_series` | 12 series、1919+;value 含 **3188 nulls**;Tier A/B vintage |
| `TaiwanStockTotalReturnIndex` | TAIEX/TPEx 報酬指數(2003+);經濟回測基準 |
| `CnnFearGreedIndex`(0-100)/`GoldPrice`/`CrudeOilPrices`(油價 min −37=2020負油價)/`ExchangeRate`/`TaiwanExchangeRate`/`InterestRate`/`GovernmentBondsYield`(殖利率,可負) | 情緒/商品/匯率/利率 context |

---

## 跨表髒值 / 語意陷阱總表(#15、易誤用)

1. **停牌哨兵**:Price OHLC=0(~28萬列)→ 特徵用 PriceAdj + close>0(panel.py 已擋)。
2. **PER=-1**:虧損股哨兵非真本益比;PBR/殖利率極端離群未 winsorize(C1、對 rank-IC 無害已驗)。
3. **CashFlows=累計YTD**:capex 等需去累計;FinancialStatements=單季;BalanceSheet=時點 snapshot(_per=佔總資產%)。
4. **發布日**:月營收次月10日、財報季底+45/90日、景氣次月下旬 → `release_lag` gate(#8 命門)。
5. **可負之「量」**:revenue(更正)、法人 buy(更正)、HoldingSharesPer percent/unit(差異數調整)、借券 Adjustments/Covering。
6. **官股 2021-07+**:早期真零(chip gate)。
7. **國際股 Adj_Close overflow/負**:不可用。
8. **TaiwanStock10Year=各股 10 年線**(非大盤)。

## 可追溯
- 工具 `scripts/profile_raw_data.py`(全表 profiler、可重跑 `--table X`)。
- 中文定義源 `column_catalog`(751 欄 zh);本報告補語意/累計/髒值(catalog dirty_note/type_caveat 原僅 5/19、宜據此回填)。

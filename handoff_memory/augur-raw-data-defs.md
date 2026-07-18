---
name: augur-raw-data-defs
description: 全 84 表 raw data 定義據實字典 + 跨表髒值/語意陷阱(財報累計語意、停牌哨兵、PER=-1、發布日)
metadata: 
  node_type: memory
  type: reference
  originSessionId: b6b65aa3-b9fc-49cb-b589-2fff5a7b85de
---

augur raw data 定義據實參考(2026-06-28、profiler 跑全 84 表得)。完整字典＝`reports/augur_raw_data_definitions_20260628.md`;工具 `scripts/profile_raw_data.py`(可重跑 `--table X`);中文定義源 `column_catalog`(751 欄 zh + 已回填 22 dirty_note/32 type_caveat)。

**台股核心訊號表(~25 已用)**:價量 `TaiwanStockPrice`(原始、停牌哨兵)/`TaiwanStockPriceAdj`(還原、特徵 SSOT)/`TaiwanStock10Year`(各股10年線非大盤);籌碼 `InstitutionalInvestorsBuySell`(5玩家 long-format)/`MarginPurchaseShortSale`(融資券13欄)/`DailyShortSaleBalances`(借券融券)/`LoanCollateralBalance`/`SecuritiesLending`(借券費率)/`GovernmentBankBuySell`(官股)/`HoldingSharesPer`(持股分級)/`Shareholding`(外資)/`DayTrading`;估值 `PER`(PER/PBR/殖利率)/`MarketValue`;財報三表(§下);事件 `MonthRevenue`/`Dividend`/`Info`/`IndustryChain`。

**財報語意(關鍵、易誤用)**:`TaiwanStockFinancialStatements`=**單季**(62 type:Revenue/GrossProfit/OperatingIncome/EPS)、`TaiwanStockCashFlowsStatement`=**累計 YTD**(34 type;capex=PropertyAndPlantAndEquipment 需去累計得單季)、`TaiwanStockBalanceSheet`=**時點 snapshot**(128 type;`X_per` 後綴=佔總資產%)。單位元。

**🔑 財報 type 碼解碼器=資料自身 `origin_name` 欄**(三表皆有、載每碼原始中文):全 224 碼(62+128+34)100% 可解碼,**不需 FinMind 外部文件**(原誤以為需文件、實證可由資料自身解,source-pure)。完整字典=`reports/augur_financial_typecodes_dictionary_20260628.md`(`-`=合併前非屬共控股權損益、OTHNOE=其他收益及費損淨額、HedgingAinancial=拼字錯避險金融資產、中文 type=舊期混語編碼)。

**跨表髒值/語意陷阱(#15)**:① Price OHLC=0＝停牌哨兵——⚠️**數字與定性 2026-07-17 live 實證修正**:全零 **556,345 列**/close=0 **694,919 列**(非~28萬),且 **98.5% 是 6 碼權證空報價、非停牌**(覆蓋窗零列僅 98 對得上 Suspended 表);蘊含單向=停牌⇒close=0、但 close=0⇏停牌。`close>0` guard 仍對、理由須改「擋空報價權證+停牌」② ⚠️**PER 哨兵值 2026-07-17 live 實證搞反**:`PER=-1` 僅 **2 列**(1449/6131@2020-11-27 單日髒資料、非哨兵);**真哨兵=PER=0,1,787,985 列(佔全表 23.52%)**,且 99.8% 同列 PBR>0(證明哨兵非缺列)→ guard 應用 **`PER>0`**(非排除 -1)。PBR/殖利率極端離群未 winsorize ③ **發布日 gate**:月營收次月15日(法定10日+緩衝、`release_lag.py` 實作常數;文件寫10=法定期限、勿混用)、財報季底+45/90日、景氣次月下旬(#8 命門)④ 可負之「量」:revenue/法人buy(更正)、HoldingSharesPer percent/unit(差異數調整)⑤ 官股 2021-07+(早期真零 gate)⑥ 國際股 Adj_Close overflow/負(不可用、out-of-scope)⑦ **TaiwanStockDividend 現 DB=塌列壞資料**(live PK=stock_id 單欄、**2,411 列/每股僅 1 列**;碼已修 require date 但 `ingest.py:141` 對既有表 PK 首建固定「永不生效」→根治須 DROP+re-sync;未入生產特徵)。⚠**2026-07-17 補三點**:(a) 損傷量化=對照 `DividendResult` **30,839 列/上限 80** → **~92% 股利史被覆寫消滅**;(b) **阻塞理由已消失**(token 07-12 續訂)→此債可清但沒清;(c) **解塌後新雷**:`Dividend.date` max=**2026-08-23 未來日期**(預告除權息)→as-of 須用 `AnnouncementDate`(存在率 95.2%),直接 `date≤panel` 即偷看未來(#8)。**月營收=元**:FY2024 全年比對 ratio=**1.000000 逐位相同**(月營收和=IS Revenue 四季和 2,894,307,699,000;同時坐實 IS Revenue 為單季);原 2025Q1「比≈0.99」殘差來自期間錯配非單位誤差。

**out-of-scope / context**:衍生(期貨/選擇權/可轉債/權證)、國際股(歐日英美)、商品(金/油)、總經(匯率/利率/債/`TaiwanBusinessIndicator` 景氣44年/fred 12 series/FearGreed)——非台股單股橫斷面訊號,部分可作 regime context。

**⚠️ BalanceSheet 系統覆蓋缺季(2026-06-28 掃出)**:逐年季數 2015=4/2016=3/2017=2/**2018=1**/2019=2/2020-21=4/2022=3/2023=2/2024=2/2025=4(跨 type 一致=表級缺口);**損益/現金流同期皆四季全**→ 缺口僅 BalanceSheet。**用 balance 科目(Inventories/AR/Equity)之特徵(C3 庫存循環)於 2016-19、2022-24 多 panel 缺季**;修需重抓(token 2026-06-24 到期、須確認 free-tier)。其餘表「缺口」皆邊際年假象(2026 半年/起始年)。

**FRED 31 series(SSOT=`src/augur/features/macro.py`、勿複列防 drift;舊 12 檔清單 2026-06-22 已擴 31)**:Tier A 22(每日市場、realtime_start=觀測日)+Tier B 9(月/季經濟、ALFRED vintage PIT 取版);fred_series PK=(series_id,date,realtime_start)。

**單位(交叉驗 `verify_units`)**:money=元/volume=股/close=元、財報金額=元、**融資餘額=張(千股)**、持股 unit=股;**⚠️ MonthRevenue.revenue 實為「元」(2330=4169億級)、catalog 原誤標「千元」已修**(YoY/share 比值特徵不受影響、單位抵消)。

**驗證狀態 ledger**=`reports/augur_raw_data_verification_ledger_20260628.md`(誠實標 ✅已驗/⏳待驗)。**已驗(2026-06-28 補完)**:逐欄單位、cashflow 逐 type 累計(20累計/4現金餘額水位/6混合)、ingestion 4 模組+generic_schema 逐行、release_lag 公告日(create_time 不可用→法定 lag 正確;Dividend.AnnouncementDate/Shareholding.RecentlyDeclareDate 存在供未來用)、早期 reports digest。**欄位層誠實狀態:已無待驗缺口**(結構/中文/值域/null/單位/語意/覆蓋/髒值全驗 + 224 財報碼由 origin_name 全解碼);**待驗剩餘僅衍生 out-of-scope 欄 _per 邊界 + Suspended 史長**(非核心台股欄位、待文件)。仍**不宣稱「全懂」**(三敵③——可掃已掃盡、doc-gated 者誠實標)。見 [[augur-feature-values]]、[[augur-project-map]]。

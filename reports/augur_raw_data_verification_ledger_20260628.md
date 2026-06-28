# Raw Data 驗證狀態 Ledger — 誠實標「已驗 vs 待驗」(2026-06-28)

> **性質**:**不宣稱「全懂」**——逐面向誠實標 ✅已驗(有據)/ ⏳待驗 / ⚠️ 發現問題(#15、三敵③)。每輪驗證仍可能揭新東西;此檔記錄「到目前驗到哪」。
> **工具**:`profile_raw_data`(結構/值域)、`verify_financial_type_semantics`(財報語意)、`scan_coverage`(覆蓋)。

## 一、驗證面向 × 狀態總表(全 84 表)

| 面向 | 狀態 | 依據 / 缺口 |
|---|---|---|
| 結構(欄名/型別/PK) | ✅ 全 84 表 | information_schema + profiler |
| 中文定義 | ✅ 751 欄 | `column_catalog.column_name_zh`(全有)|
| 值域(min/p50/max)/null 率 | ✅ 全 84 表 | profiler 實算 |
| 發布日語意(#8) | ✅ 核心 | 營收次月10/財報+45-90/景氣次月下旬(`release_lag`)|
| **財報 accumulation 語意** | ✅ 表層確立 | **income=單季、cashflow=累計YTD、balance=snapshot**(數據驗 + 會計原則表內一致)|
| **覆蓋完整度** | ✅ 全表掃 → ⚠️ 見 §三 | `scan_coverage`:**僅 BalanceSheet 真缺季**;餘為邊際年假象 |
| FRED 12 series 定義 | ✅ | 標準碼、見 §二 |
| 髒值哨兵 | ✅ 核心 | catalog 22 dirty_note(停牌0/PER=-1/percent負/國際overflow…)|
| 224 財報 type 碼**精確會計定義** | ✅ 常用 ~20 / ⏳ 罕見 legacy | 標準科目知曉;ExtraordinaryItems 等罕見碼**待 FinMind 文件**(不杜撰 #1/#17)|
| 衍生品(期/權)機制 | ✅ 知識補 / ⏳ FinMind 細節 | 見 §四:OI=未平倉量(口)、結算、大額交易人占比=集中度、法人多空 deal——標準衍生語意已釋;FinMind 欄精確細節待文件 |
| 逐欄精確單位 | ✅ 核心交叉驗(`verify_units`) | money=元/vol=股/close=元/財報=元/融資餘額=**張(千股)**/持股unit=股;**⚠️月營收=元(catalog 原誤標「千元」已修正)** |

## 一-b、程式 + reports 驗證(2026-06-28 擴、`verify_code_reports`)

| 域 | 結構驗 | 深層理解 |
|---|---|---|
| **程式 src/augur(25 .py)** | ✅ **全編譯 0 錯 + 全有 🎯 docstring**(#18) | ✅ 核心 + **ingestion 4 + core/generic_schema 2026-06-28 逐行深讀**(三層限速/vintage PIT/adaptive 引擎/canonical-probe;auto-schema 值推型/detect_keys/SAVEPOINT 併發/跨型別降級 trim_scale byte-equal) |
| **scripts(31 .py)** | ✅ 全編譯 0 錯 + 全有 docstring | ✅ 多本 session 寫;`full_market_sync`/`build_catalog` 等 CLI purpose-level(薄 wrapper、邏輯在 src 已讀) |
| **reports(65 份)** | ✅ 全有標題、已清點 | ✅ 近期 0626-28 自寫深懂;**早期 0610-25 已 digest**(設計三鏡頭原始/評估/稽核/資料源/架構理論)；handoff 系列僅總述 |

> **誠實**:ingestion 已逐行;core/generic_schema + 早期 reports 細節屬 digest-level(懂實質、未逐行/逐數重讀)。

**cashflow 逐 type 累計乾淨驗(2026-06-28、|Q4|/|Q1| 法、取代有缺陷的 |value|-單調)**:34 type → **20 累計YTD**(營業/投資/融資現金流、capex 4.8、折舊…)、**4 單季**(CashBalancesBegin/End=現金餘額時點水位、ratio≈1 合理)、6 混合(營運資本變動項邊界)、4 不足。**確立:現金流主體累計、現金餘額項為水位。**

**✅ release_lag 公告日實證(2026-06-28、定論)**:probe DB 得——
- `MonthRevenue.create_time`:**❌ 不可用作公告日**(2023-01 營收之 create_time 多為空、餘為 `2026-05-19` ingestion 時戳,非逐筆公告日)→ **現用法定 lag(次月10日)正確**。
- `Dividend.AnnouncementDate`+`AnnouncementTime`:**✅ 存在**(真公告日)→ 未來做股利特徵時可用 PIT(現未用 Dividend)。
- `Shareholding.RecentlyDeclareDate`:**✅ 存在** → 可精化外資持股 PIT(惟外資持股~日頻、date lag 小)。
**結論:`release_lag` 法定 lag 做法正確、無須改;公告日欄存在但不在現有 lag-critical 特徵路徑。此項解決。**

## 二、FRED 12 series 定義(✅ 已驗、標準碼)

| series | 定義 | 範圍 | 用途 |
|---|---|---|---|
| `FEDFUNDS` | 美聯邦資金利率(%) | 1954+ | 政策利率(信用循環)|
| `DGS10`/`DGS2` | 美 10年/2年公債殖利率 | 1962/1976+ | 利率水位 |
| `T10Y2Y`/`T10Y3M` | 10年-2年/10年-3月 利差 | 1976/1982+ | **殖利率曲線倒掛=衰退前兆** |
| `CPIAUCSL` | 美 CPI(消費者物價、SA) | 1947+ | 通膨 |
| `UNRATE` | 美失業率(%) | 1948+ | 景氣 |
| `INDPRO` | 美工業生產指數 | 1919+ | 景氣循環 |
| `VIXCLS` | VIX 恐慌指數 | 1990+ | 風險/情緒 |
| `BAMLH0A0HYM2` | 美高收益債信用利差 | 2023+ | 信用循環(史短)|
| `DCOILWTICO` | WTI 原油價 | 1986+ | 商品/通膨 |
| `DTWEXBGS` | 美元廣義貿易加權指數 | 2006+ | 美元強弱 |
> vintage:value 含 3188 nulls;Tier B 經濟序列須 ALFRED vintage(#8、`fred.py` 支援)。

## 三、⚠️ 重要發現:BalanceSheet 系統性覆蓋缺季(已驗、真缺口)

逐年季數(TotalAssets/Inventories 一致＝表級缺口、非 type 別):

| 年 | 2015 | 16 | 17 | **18** | 19 | 20 | 21 | 22 | 23 | 24 | 25 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 季數 | 4 | 3 | 2 | **1** | 2 | 4 | 4 | 3 | 2 | 2 | 4 |

**損益表/現金流表同期皆四季全**(僅 2026 當前半年未滿)→ **缺口僅 BalanceSheet**。**意涵**:用資產負債科目(Inventories/AR/Equity…)之特徵(C3 庫存循環)於 **2016-19、2022-24 多 panel 會缺季→缺列或陳舊**;**balance-sheet 特徵之可用 panel 受限**。修法:重抓 BalanceSheet(惟 FinMind token 2026-06-24 到期,須確認該表 free-tier 可補)。

> 其餘 48 表「缺口」經查皆**邊際年假象**:2026=當前半年(~110 交易日)、1994/2005/2007=起始半年——**非真缺口**。

## 四、衍生品語意(✅ 知識補、標準衍生概念)

期貨/選擇權表共通:`long/short_deal_volume/amount`=法人多/空成交量/額、`long/short_open_interest_balance`=多/空未平倉餘額(口/金額)、`settlement_price`=結算價、`open_interest`=未平倉量(口)、`strike_price`=履約價。`*OpenInterestLargeTraders`:`buy/sell_top5/10_trader_open_interest(_per)`=前5/10大交易人多空未平倉(占比)＝**部位集中度**(>100% 因含跨月);`specific`=特定法人。`*AfterHours`=盤後。**標準衍生語意已釋;FinMind 各欄精確邊界(如 _per 分母)待文件**。皆 out-of-scope 台股單股特徵、可作 regime context。

## 五、⏳ 待驗清單(誠實;剩餘**多需外部文件或屬低優先**——data/code 可掃的已大致掃盡)

1. **224 財報 type 罕見 legacy 碼精確會計定義**(ExtraordinaryItems/CumulativeEffectOfChanges… )——**需 FinMind 文件/會計準則對照**,clean-room #1/#17 不杜撰。
2. **衍生 FinMind 欄精確邊界**(_per 分母定義等)——**需 FinMind 文件**。
3. **月/週/事件表「事件完整度」**(如 Dividend 是否漏公司、Delisting 是否齊)——**可數據掃、但低優先**(非 lag-critical、非橫斷面核心訊號)。

> **已從待驗移除(本 session 完成)**:逐欄單位(`verify_units`)、cashflow 逐 type 累計(`verify_cashflow_cumulative`:20累計/4水位/6混合)、ingestion+generic_schema 逐行、release_lag 公告日實證(法定 lag 正確)、早期 reports digest。

## 五、誠實立場
- **已達**:核心台股訊號表 + 財報表層語意 + FRED + 髒值 + 覆蓋 = **據實已驗、夠專案用**。
- **未達**:罕見財報碼精確定義、衍生機制、逐欄單位全驗 = **待驗、已列**。
- **不宣稱「全懂」**:此 ledger 即承諾——持續標 ✅/⏳,新發現(如此輪 BalanceSheet 缺口)即補記,不在某刻宣布完成。

## 可追溯
工具 `scripts/{profile_raw_data,verify_financial_type_semantics,scan_coverage}.py`;字典 `reports/augur_raw_data_definitions_20260628.md`;catalog 22 dirty_note/33 caveat。

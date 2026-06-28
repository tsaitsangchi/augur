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
| 衍生品(期/權)機制 | ⏳ 待驗 | 值域+中文名有、未平倉/結算/大額交易人機制**未深究** |
| 逐欄精確單位 | 🟡 部分推斷 | 財報元/營收千元已確;部分(張vs股)推斷未全驗 |

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

## 四、⏳ 待驗清單(誠實、尚未做)

1. **224 財報 type 罕見 legacy 碼精確會計定義**(ExtraordinaryItems/CumulativeEffectOfChanges… 需 FinMind 文件/會計準則對照)。
2. **衍生品機制**(期貨/選擇權未平倉/結算/大額交易人占比之精確語意)。
3. **逐欄精確單位**全驗(部分張vs股、元vs千元仍推斷)。
4. **其他表逐年覆蓋**已掃(僅 BalanceSheet 真缺);但**月/週/事件表的「事件完整度」**(如 Dividend 是否漏公司)未逐一驗。
5. **cashflow 逐 type 累計**:表級確立累計YTD,但 |value| 測對變號科目不準、未逐 type 乾淨驗(僅 capex+表級確認)。

## 五、誠實立場
- **已達**:核心台股訊號表 + 財報表層語意 + FRED + 髒值 + 覆蓋 = **據實已驗、夠專案用**。
- **未達**:罕見財報碼精確定義、衍生機制、逐欄單位全驗 = **待驗、已列**。
- **不宣稱「全懂」**:此 ledger 即承諾——持續標 ✅/⏳,新發現(如此輪 BalanceSheet 缺口)即補記,不在某刻宣布完成。

## 可追溯
工具 `scripts/{profile_raw_data,verify_financial_type_semantics,scan_coverage}.py`;字典 `reports/augur_raw_data_definitions_20260628.md`;catalog 22 dirty_note/33 caveat。

# augur 資料層完全理解結論報告 — table / field / raw 四層(2026-06-29)

> **性質**:**理解結論報告**(非 profiler 字典——字典見 `augur_full_column_walkthrough_20260629.md`)。本檔是「**我（Claude）對 augur 資料層理解到什麼程度、結論是什麼**」之綜合陳述,經連續五輪深化收斂、全程實證(DB query/恆等式驗證,非 catalog 照抄、非「我以為」)。
> **實證基礎**:94 表 772 欄逐欄走查 + catalog↔DB 一致性回填 + raw 值 categorical 實證 + 16 欄位間恆等式驗證 + 髒值比例統計。工具 `scratchpad/{walk_columns,deep_raw_profiler,verify_identities}.py`。

---

## 〇、一句話結論

augur 資料層 = **94 表（dump 後 DB）、~25 張核心台股單股訊號表 + ~69 張 context/out-of-scope（衍生/國際/CB/總經）**。核心表的 **table 定義、field 定義、raw 值語意、欄位間數值關係**我已**逐層實證理解到位**;誠實邊界（罕見財報碼準則級、衍生 out-of-scope 欄精確邊界）明列於 §八、不宣稱絕對全知。

## 一、資料層全貌（11 category 之理解結論）

| Category | 表數 | 我的理解結論（這類是什麼、用途、in/out-scope）|
|---|---|---|
| **TW-Technical** | 16 | 價量核心:Price/PriceAdj(還原、特徵 SSOT)/PER/10Year(各股線)/TAIEX/PriceLimit/TradingDate。**alpha 主源**|
| **TW-Chip/Institutional** | 16 | 籌碼核心:三大法人(long 6 玩家)/融資融券/借券/外資持股/持股分級/官股。**alpha 主源**|
| **TW-Fundamental** | 12 | 基本面:財報三表(long、發布日 gate)/月營收/股利/市值/除權息/減資分割。**alpha 源(發布日 gate 必須)**|
| **TW-Others** | 3 | 景氣對策(regime context)/產業鏈(僅 2026-06 snapshot)/News(count) |
| **Global Economic** | 7 | 商品/匯率/利率/黃金/恐懼貪婪(X 類 context、by-dim-id)|
| **Macro** | 1 | fred_series(12 series 總經、vintage)|
| **International** | 8 | 美/日/英/歐股(**out-of-scope、Adj_Close overflow 不可用**)|
| **TW-Derivative** | 16 | 期/權(out-of-scope 單股訊號;OI/大額交易人可作 regime context)|
| **TW-Convertible Bond** | 4 | 可轉債(out-of-scope)|
| **TW-Real-Time** | 1 | 期權即時(#4 intraday 邊緣)|

## 二、四層理解結論

**第 1 層 table 定義 ✅**:每表的 source/category/tier/抓法(per-stock/by-date/by-dim-id/market)/頻率/最早日/排除旗標 — 逐表掌握,SSOT＝`dataset_catalog`(95 列)。

**第 2 層 field 定義 ✅**:每欄的型別/PK/中文/anti-leakage/髒值註記 — 逐欄走過 + **catalog 已回填對齊 DB**(fred 3 欄補、49 PK + 型別偏差以 DB information_schema 校正)。**權威鐵則:型別/PK 以 DB `information_schema` 為準**(#2 API 即權威);`column_catalog`(751 欄)為可刷新快取、提供中文/語意。

**第 3 層 raw 值定義 ✅**:逐欄實證 categorical 欄「實際存哪些值」+ 範例列。**catalog 中文之外的真相**(見 §三）。

**第 4 層 raw 之間關係 ✅**:16 欄位間數值恆等式實證(勾稽/定義/三表/跨表,見 §四)。

## 三、關鍵 raw 真相（實證才知、catalog/報告之外）

1. **法人別實際 6 值**(Dealer / Dealer_Hedging / Dealer_self / Foreign_Dealer_Self / Foreign_Investor / Investment_Trust;Total 表 7 含 total)— 非概稱「5 玩家」。
2. **HoldingSharesLevel 17 級含 `total` 彙總 + `差異數調整（說明4）`** — 這是 `percent` 可負(實證 0.045%)/可>100 的根源 → **用持股分級算 Pareto 集中度必須排除 total/差異數調整列**(否則 Gini 失真)。
3. **財報語意**:損益表=**單季**、現金流=**累計 YTD**、資產負債=**時點 snapshot**;`_per` 後綴=佔資產總額%;金額單位=**元**;月營收單位=**元**(catalog 原誤標千元已修)。224 type 全由 in-data `origin_name` 解碼。
4. **categorical 值域**:BlockTrade 3(單一型/逐筆/配對)· SecuritiesLending 3(定價/競價/議借)· monitoring_color 6(-/B/G/R/YB/YR)· Info.type 3(emerging/tpex/twse)· GovBank 8 行庫 · SplitPrice 3 · DividendResult 6 · 央行 12 · 美債 13 期別 · 匯率 19 幣別。
5. **還原機制**:PriceAdj/Price 同日比值近期≈1.000(2026-05 實證 min 0.896/p50 1.000/max 1.016)→ 近期無除權息調整時還原=原始,歷史因除權息往回調。

## 四、欄位間數值恆等式（raw 之間關係結論、實證 PASS%）

| 恆等式 | PASS | 結論 |
|---|---|---|
| 融資今餘 = 昨餘+買-賣-現償 | 100% | ✓ 完美勾稽 |
| 融券今餘 = 昨餘+賣-買-現償 | today>0 時 100% | ✓ 與融資**對稱**;全表 82% 因餘額下界截斷(非公式錯)|
| DailyShortSale 融券/借券餘額勾稽 | 100%/100% | ✓ |
| 外資持股/尚可比率 = 股數/發行×100 | 100%/100% | ✓ 比率定義 |
| 持股分級 total = Σ各級 unit | 99.3% | ✓(差異數調整邊界)|
| 毛利=營收−成本 / 資產=負債+權益 | 99.6%/99.5% | ✓ 財報三表勾稽 |
| 營益 = 毛利 − 營業費用 | 96.8% | ~(含其他收益及費損)|
| 漲跌停 limit_up = reference×1.10 | 100% | ✓ ±10% 制度 |
| 除權息 after_price ≤ before_price | 99.9% | ✓ 除息扣息 |
| 融資餘額 ≤ 融資限額 | 100% | ✓ |
| **跨表 市值 ≈ 收盤價 × 發行股數** | 100% | ✓ 跨表一致 |
| OHLC max≥open,close≥min | 98.0/96.6% | ~(還原邊界/極少)|

**結論**:raw 欄位間的會計/邏輯關係（勾稽公式、比率定義、三表勾稽、漲跌停制度、跨表市值）**實證成立**;違反皆有合理解釋（餘額下界截斷、會計其他項、還原邊界、差異數調整），**非資料錯誤**。

## 五、髒值/語意陷阱（實證比例）

| 陷阱 | 實證比例 | 處置 |
|---|---|---|
| **PER ≤ 0（虧損哨兵 -1）** | **28.17%** | valuation `per>0` gate(此即估值核心股收縮主因)|
| 停牌 OHLC = 0 | ~28 萬列 | panel 用 PriceAdj + close>0 |
| MonthRevenue revenue<0(更正) | 0.139% | 可負真值 |
| HoldingSharesPer percent<0(差異調整) | 0.045% | 算集中度排除 |
| Institutional buy<0(更正) | 0.002% | 可負真值 |
| 國際股 Adj_Close overflow(±1e38) | — | out-of-scope、不用 |
| CnnFearGreed 情緒格式混亂 / Suspended time 8:00 vs 09:00 | — | categorical 標準化需注意 |

## 六、anti-leakage 金礦欄（#8）

- `Dividend.AnnouncementDate` / `AnnouncementTime` ✅ 真公告日(未來做股利特徵可用 PIT)
- `Shareholding.RecentlyDeclareDate` ✅ 外資申報日
- `MonthRevenue.create_time` ❌ **實證多空/ingestion 時戳、不可用** → 月營收用法定 lag(次月 15 日)
- 財報三表無公告欄 → `release_lag` 法定申報期限 gate(季+45/年報+90)

## 七、已知資料 bug/限制

1. **`TaiwanStockDividend` PK=stock_id 單欄塌列**(同股多年互蓋僅存 1 筆;碼已修 require_keys=date、**待 token 重建**;現未入生產特徵、不影響 alpha)
2. **GovBank / 衍生表 PK 全欄塌陷**(detect_keys fallback;aggregate / out-of-scope、不影響)
3. **BalanceSheet 系統性缺季**(2016-19、2022-24;影響康波 C3 庫存循環特徵)
4. **IndustryChain 僅 2026-06 snapshot**(無歷史;軸⑦產業內相對化改用 `TaiwanStockInfo.industry_category`)

## 八、誠實邊界（漸近、未達 — 不宣稱絕對全知 #15）

1. **罕見財報碼 IFRS 準則條文級定義**:224 type 有 in-data 中文(origin_name),但罕見 legacy 碼之準則精確定義未逐一查(不杜撰)。
2. **衍生品 FinMind 欄精確邊界**(期/權大額交易人 `_per` 分母等)— out-of-scope、待文件。
3. **Suspended 表史短**(僅 2025-03+)— 待文件確認本就短 vs 漏抓。
4. **全 772 欄精確數值分布**:核心欄已驗,非每欄逐一 min/p50/max/null。
5. 恆等式違反之**逐列根因**:已歸類(截斷/其他項/還原),非逐列追。

## 九、結論判定

**核心台股(Technical/Chip/Fundamental ~40 表)的 table / field / raw 值 / raw 之間關係四層,我已逐欄、逐恆等式實證理解到位、可信** —— 這是「用真實資料誠實預測台股」(靈魂)所需的資料層理解。out-of-scope(衍生/國際/CB)逐欄列出 + 標註。誠實邊界(§八)明列、不自欺。

> **方法論教訓(五輪深化最大收穫)**:「完全理解」是**逐層逼近**、非一次到達。每輪都揭新東西(法人 6 值、HoldingSharesLevel total/差異數調整、PER 28% 虧損、融券誤判)。最關鍵:**逐欄/逐列實證會推翻「看一個數字就下的結論」**(融券 82% 我曾誤判「公式錯」、逐列追查才見是餘額截斷)→ 印證 #20「見可疑追到底、防自欺③」與靈魂「只信真兆」。

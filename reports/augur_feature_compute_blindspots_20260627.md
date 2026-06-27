# Augur 特徵值運算層 — 第二輪深度審查報告（24 盲點去重合併）

> 範圍：**特徵值運算層**（`src/augur/features/panel.py` + `chip.py`）每支特徵的數學公式 / SQL / 邊界條件 / 數值穩定性 / 單位一致性 / 實際 DB 值之正確性、robustness、名實相符。
> 審查方法：每盲點皆 code-read（panel.py / chip.py 逐行）+ psql 實證雙重對抗驗證（2 名驗證者獨立投票），已對既有 39-gap 報告去重。
> 治權 bar：#1 source-pure（算不出即缺列）· #8 anti-leakage（as-of≤t）· #9 思想≠特定值 · #12 SSOT · #15 誠實可重現 · 方法論母原則③「目標相對→特徵必相對化」。
> 共識標記：✅✅ 兩驗證者同判 real＋novel；✅ real 但 novel 或嚴重度分歧；⚠️ 一票否定或重大事實校正。嚴重度取兩票之**保守眾數/折衷**，並標原始分歧。

---

## 總體判斷：本輪三個最關鍵新發現

**這輪運算層深挖的最重磅、最該優先處理的，是「停牌 close=0 佔位列污染窗口聚合運算」這一條完全獨立於除權息的根因鏈，它直接威脅 headline 最強 alpha（cycle/position 族）的材質。** 三大新發現如下：

### 🔴 發現一（最關鍵、兩票皆 high）：`cycle_position_252d` 的 252 窗低點被停牌 close=0 佔位列污染 → 28% 列退化、訊號可完全反向
`panel.py:103` `lo = c.iloc[-252:].min()` 直取窗內最小 close，而 `TaiwanStockPrice` 有 281,727 列停牌佔位（OHLC 全 0），只要窗內落入任一停牌 0，`lo=0` → `cycle=(c-0)/(hi-0)=c/hi`，**cycle 數學上塌成 `price_to_252d_high`**。psql 坐實：股 1102@2024-12-31 真實區間位置應為 `(40.40-39.20)/(47.75-39.20)=0.140`（近 52 週低），卻被算成 `0.846073`（近高）= **訊號完全反向**。全庫 `cycle==p2h`（6 位小數逐位元相同）達 **22,598/80,159 = 28.2%**。

**為何威脅 headline**：cycle/position 被方法論並列為各 +0.088「最強 alpha」、入憲為 alpha 主源。本盲點與 39-gap 的 CG1/CG2/CG3（除權息原始價 vs 還原價）**完全正交**——換還原價（`TaiwanStockPriceAdj`）亦不解，因停牌 0 是 min/max 聚合對哨兵值缺守護的純運算 bug。這意味著即使做了除權息修正，cycle 在 28% 列上仍名實不符。必須先修此 bug + 做 raw-vs-clean 消融，才能確認 cycle alpha 是否存活。

### 🔴 發現二（除權息污染確認的對偶面）：特徵端 `close=0` 守護不對稱，position 族系統性漏網
審查確認了一個比「特徵用原始價 vs label 用還原價」更基礎的結構性雙標：**`panel.py` 的唯一數值守門 `isfinite`（line 111）只擋 log 類除零（→±inf 被剔），對「分子=0 的比值」（`0/hi=0`、`(0-lo)/range≈0`）系統性失效。** 同一停牌日，momentum/return/volatility 經 `log+isfinite` 天然正確缺列，但 `price_to_252d_high`/`cycle_position` 因比值 finite 漏網存活成偽地板。psql：`price_to_252d_high==0` 共 2,668 筆，**100% 對應 panel 當日 close=0**（無一真訊號）。而 `label.py:79` 早有 `px_<=0 → 缺列` 守護——**特徵層與 label 層雙標**確立。

> **關於「特徵用原始價 vs label 用還原價」除權息污染**：本輪聚焦運算層機制，未直接重算 raw-vs-adj 對 cycle/position 的 IC 消融（屬 39-gap CG1/CG2/CG3 範疇）。但本輪坐實一個關鍵分離：cycle/p2h 的零值與退化，**主因是停牌 close=0（本輪新發現），而非除權息（CG3）**——CG3 僅涵蓋其中除息那一小支。因此 headline 最強 alpha 的威脅是**雙重的**（除權息 + 停牌污染），且後者範圍更大（28% vs 零星）。兩者須一併修、一併消融，否則任一單獨修正都不足以還原 cycle 的真實效力。

### 🔴 發現三（價量族共通根因）：`_PRICE_SQL` 與所有 rolling 窗皆無 recency 下界 → 停更/下市股的陳舊窗偽裝成 as-of
`panel.py:38` `_PRICE_SQL` 只有 `date <= %s` 無下界；`compute_features` 各 gate 只查列數 `n>=w`（line 98/102/107），**從不檢查 `df` 末筆是否貼近 panel_date**。psql：股 9801（最後成交 2007-01-04，19 年前）在 2026-05-31 panel 仍取得完整 21 特徵；全庫 momentum_5d 有 4,742 筆其源價>365 天 stale。最要命的升級證據：**core_gate 完整度 gate 只查「全特徵齊」不查 price recency**，實證 25 檔 stale>365 股已進 production core_universe（如 2473 最後成交 2012-11-21、13.5 年前，卻在 2026 panel 帶一整套像活股的非零特徵 momentum_252d=0.543 / cycle=1.0 / foreign=13.6），**直接污染當期橫斷面排序、且偏向「歷史曾強勢」的 survivorship 方向**（chip-continuous 四特徵 LIMIT-1 亦同病：2311 太電 LIVE 報價但 foreign_holding_pct=63.77 凍結於 2020-12，5.5 年 stale 直入 2026）。

**三者共通修法骨幹**：在窗口聚合前建立統一 `valid-bar` 判據（`close>0` 且 date 落在日曆 recency 容差窗內），不足有效 bar → 整股價量族缺列（#1），與 `label.py:79` 同源；門檻用相對量（依全市場交易日曆密度推得）不硬編（#9）。這一個改動可同時治發現一、二、三及下游多條 gap。

---

## 🔴 根本級（high 共識 / 威脅 headline 或系統性污染）

### R1. `cycle_position_252d` 停牌 close=0 污染 252 窗 min → 28% 列退化、可訊號反向 ✅✅
- **運算問題本質**：`lo=c.iloc[-252:].min()` 把停牌佔位 0 當合法最低價，cycle 退化成 `c/hi`，近低股被錯標近高。
- **證據**：`panel.py:102-106`。psql：close=0 佔位列 281,727 筆（全 OHLC=0，247,119 零成交）；股 1102@2024-12-31 DB `cycle=p2h=0.846073` 逐位元相同，正確應 0.140（反向）；全庫 `cycle==p2h` 22,598/80,159=28.2%，其中 value>0 之 19,930 為停牌污染（抽樣 40/40 窗內確有 close=0）。受污染股多在 core_universe（1102/1525/1715/2221/2363/2437/2448/2449@2024-12-31 皆 win_min=0）。
- **為何是真盲點**：與 CG1/CG2/CG3 正交（換還原價不解，`TaiwanStockPriceAdj` 無停牌哨兵列）；`label.py:83` 已有 `px_<=0 → continue` 先例，**特徵側欠缺同源守護**＝非對稱 bug 核心。28% 退化使「最強 alpha」名實不符。
- **修法**：計 hi/lo/momentum 窗前先剔 `close<=0` 列再取 min/max；剔後有效列<252 → cycle/p2h 缺列（#1）；重建受污染 panel + raw-vs-clean 消融確認 cycle alpha 存活。
- **下游影響**：cycle 進 IC/Ridge/橫斷面 rank/直讀 feature_values 全受扭曲；威脅 +0.088 cycle alpha 結論材質。
- **共識/校正**：兩票 high。報告原文「Adj 表同有停牌 0 列」**事實錯誤**（psql：Adj close=0 為 0 筆），但不撼動結論（panel.py 實讀 raw 表，bug 與還原無關）。

### R2. `price_to_252d_high` 的 2,668 個零值 100% 是停牌 close=0 artifact、非真訊號 ✅（嚴重度 high↔medium↔low 分歧）
- **運算問題本質**：`p2h=c.iloc[-1]/hi`，當日 close=0（停牌佔位）→ `0/hi=0` 為 finite → 通過 isfinite 守門、當「近 252d 低」最弱訊號餵 IC/Ridge。
- **證據**：`panel.py:103-104`。psql：`p2h==0` 全 2,668 筆其 panel 當日 last close 100% = 0（`2668/2668`）；股 3563@2009-12-31 整列 0、252 窗 max=12.5 → 0/12.5=0；同日 return/momentum/volatility 全正確缺列，唯 p2h/cycle 漏網。真股 p2h 最小非零=0.002759，與 0 乾淨可分 → **每個零值皆 artifact、無一真訊號**。
- **為何是真盲點**：position 族專屬 `close=0` 漏網（momentum 族經 log+isfinite 天然擋掉）；與 `label.py:79`（close<=0 缺列）形成特徵端雙標；pilot v4 雖修 close=0 但僅限 volatility 族、未檢視 position 窗口特徵。
- **修法**：`compute_features` 開頭對 `c.iloc[-1]<=0` → p2h/cycle 缺列（與 momentum 行為一致、與 label.py:79 同源）；重建 2,668 列。
- **下游影響**：偽地板進 rank 最弱端污染橫斷面；poisoned 0 反讓停牌股-panel 因「該特徵有值」通過完整度 gate（不對稱污染）。
- **共識/校正**：real＋novel 兩票確認；嚴重度分歧——驗證者B 指出 CG1 換還原價會順帶消除 2,665/2,668（ADJ close>0），僅 3 檔（3644）殘留，故定位為「低成本防禦補丁、應與 CG1 換表一併做」。**淨建議：與 R1 同批修，顯式 `close>0` 守護仍必要（防 ADJ 殘留 + 未來缺口）。**

### R3. `_PRICE_SQL` 無 recency 下界 → 全價量族用陳舊窗偽裝 as-of，25 檔已進 core ✅✅
- **運算問題本質**：`date <= %s` 無下界 + 各 gate 只查列數，停更/下市股取數年前最後窗算全套特徵、貼近期 panel_date。
- **證據**：`panel.py:38, 98/102/107`。psql：股 5102 最後價 2022-07-06，volatility_20d=0 跨 15 panel 貼到 2026-05-31；全庫 volatility_20d 4,087 筆源價>365 天 stale，turnover_mean 4,123、sbl 4,103 同病；**core_gate 不查 recency，25 檔 stale>365 已進 core_universe**（2473 最後成交 13.5 年前帶完整非零特徵）。
- **為何是真盲點**：as-of≤t 形式滿足但實質違反「t 當下真可觀察」（#8）；39-gap 的 stale 旁註僅針對 chip institutional LIMIT-1，本盲點坐實同病灶存於價量 rolling 窗整族並量化 + 證明 universe 層擋不住。
- **修法**：`_PRICE_SQL`/build_panel 加 recency gate（`date >= panel_date - INTERVAL`，門檻依交易日曆密度不硬編 #9）；超界整股價量族缺列；**須同時套到 _PRICE_SQL / chip / valuation / revenue 四源**；與 label 端「日曆不足即缺列」對稱；重建受污染 panel。
- **下游影響**：survivorship-biased stale 股污染當期排序（能跨全 panel 齊特徵的 stale 股多為當年大型股，系統性偏誤）。
- **共識/校正**：兩票 real＋novel，嚴重度 high↔medium。驗證者B 指出最嚴實害路徑依賴 `core_universe_asof`（現 DB 不存在，呼應 39-gap S1），故「已坐實入模污染」與「結構鏈成立但 live 路徑待重建」並存——**but 25 檔已進現有 core_universe 之質性污染成立，定 high**。5102 案例之 vol=0 為「真值凍結後貼 4 年」，真正污染橫斷面的是 2473 類帶非零強勢動能的 stale 股。

### R4. chip 三 E 類特徵在 2007-2013 vs 2014+ 混入兩版 build（早期 P 類缺列、晚期 E 類真零）→ 同特徵兩定義 ✅✅
- **運算問題本質**：feature_values 中 `lending`/`sbl`/`gov` 早期 panel 以舊「算不出即缺列」語意落地、晚期以「真零填0」語意落地，同欄跨年兩種母體定義，零率跳變被誤讀為 regime。
- **證據**：`chip.py:128-139`（現行 E 類無條件寫值，邏輯上不可能產出缺列）。psql：2014-2026 三特徵每 panel row 數=full roster；2007-2013 發散——lending 124-637 列且 zero_pct=0.0%（僅事件股有值）、gov 全缺 0 列。lending zero_pct **0.0%(2013)→50.1%(2014)** 為 build 版本切換 artifact 非「借券普及化」。2012-12-31 有 1,066 股有 momentum_20d 卻完全缺 lending（現行 code 不可能）。
- **為何是真盲點**：違 #12 SSOT（一特徵一定義）+ #15（docstring「全 roster 皆得真值」與早期 DB 事實名實不符、靜默不一致）+ 三敵③（零率跳變偽裝 regime）；39-gap S1 談重建覆蓋、G2/G3 談 gov 假零，均未發現「同特徵兩版 build 共存於現行 DB」。
- **修法**：以現行 E 類 code 重建 2007-2013 全 panel；對 gov 標明源表 2021-07 前無源不可填零（或缺列）；加 build-version 一致性檢核（同特徵跨 panel 缺列率不應結構跳變）。
- **下游影響**：任何含 2007-2013 panel 的 IC/訓練混兩種定義（早期僅活躍借券股子集、有選擇偏差、無真零）。
- **共識/校正**：兩票 real＋novel，high↔medium。**事實校正**：(1) 報告引「1101 缺 lending」**錯誤**（1101@2012-12-31 實有 lending=0.53），正確缺列股有 1,066 檔；(2) sbl 早期非乾淨 0%→50%（2012 已 44.7% 零），**最乾淨的兩版故事在 lending（high）與 gov**，sbl 較模糊。gov 成分部分與 G2/G3 重疊（源表 2021-07 起）。

---

## 🟡 重要級（medium 共識 / 真實污染但範圍有界，多被 core_gate 部分緩解）

### Y1. momentum 視窗以「資料列位移」非日曆日計 → 缺口股短窗 momentum 橫跨數年偽極值 ✅（high↔low 分歧）
- **本質**：`out[f"momentum_{w}d"]=np.log(c.iloc[-1]/c.iloc[-1-w])` 純列位移，缺口股的 `c.iloc[-1-w]` 落在缺口另一側遠古 bar。
- **證據**：`panel.py:91-93`。psql：股 6467@2024-12-31 momentum_5d=2.512306=`log(44.40/3.60)`，所謂「5 日動能」實橫跨 2018-12-28→2024-12-31 共 6 年（該股 2019-01~2024-12 無交易列）；711131@2023-12-31 momentum_20d=4.510860 橫跨 3 年缺口。皆為全域最大值。
- **為何是真盲點**：違方法論 §73「最近 w 期累積報酬」語意 + #15 名實一致；根因「positional 視窗無日曆有效性檢查」與 C1（winsorize）/stale/CG 皆不同根。
- **修法**：momentum 計算前驗證 `c.iloc[-1-w].date` 落在 `[panel - w*1.6 日曆日, panel]` 容差窗，超出即缺列（#1）；或 reindex 全市場交易日曆用日曆位移；順帶與 volatility（已用 fin_ret 過濾）視窗一致。
- **下游影響**：偽極值 213 筆落地 feature_values。
- **共識/校正**：嚴重度兩票分歧 **high vs low**。關鍵實證：驗證者B 系統掃描 30,348 core 股×panel，**5 列窗跨>30 日曆日者僅 1 例（5215@2011，值=-0.300 平凡）、20 列窗跨>60 日者 0 例**；13 檔 |momentum_5d|>1.0 真股全部 0 檔在 core。**淨判：feature_values footgun 為真，但對 IC/Ridge 淨污染近乎零（core_gate 流動性/完整度門檻結構性排除停牌薄量股）**。取折衷=medium-low，與 reindex 全市場日曆統一 momentum/volatility 視窗一併低優先處理。

### Y2. volatility std 的 fin_ret 回填跨任意日曆缺口湊滿 w 筆 → 隔月/隔年報酬當連續日報酬 ✅（novel 分歧）
- **本質**：`fin_ret=ret[isfinite]; fin_ret.iloc[-w:].std()`，對 w 筆有效報酬之間日曆間距無下界，停牌/稀疏股悄悄回填數月至數年前報酬。
- **證據**：`panel.py:94-97`。psql/python：股 4923@2014-12-31 volatility_20d=0.043471（逐位元重現），20 筆「報酬」實橫跨 2011-10-03~2014-06-03 ≈ 2.7 年；2014-12-31 panel 1862 檔中 179 檔(9.6%)前 60 日曆日不足 20 個非零 close，其中 11 檔在 core_universe；最嚴重 core 股 2473 回伸 797 日、最近交易停 2012-11 卻揹 volatility_20d 進矩陣。
- **為何是真盲點**：docstring(panel.py:95)「對停牌 robust、往前補足」把 staleness 當優點；混合不等持有區間使 std 失統計意義，違 #15 名實 + #8 as-of。修正 39-gap S9「現核心 0-4 例、全 2007-2011 IPO 稀疏」之低估——實為 40 檔 core 股 / 902 列、主因停牌/稀疏非 IPO。
- **修法**：fin_ret 取窗加日曆跨度下界（湊滿 w 筆所跨日曆天 ≤ w 之倍數，依交易日曆密度推得 #9），超出缺列（#1）。
- **下游影響**：衝擊集中於 Ridge 係數擬合（混合不等持有 std 直入 StandardScaler），rank IC 相對 robust。
- **共識/校正**：兩票 real、medium 一致；novel 分歧（驗證者B 判 false——S9 同特徵同根因、line 181 未驗候選已列「volatility/range 視窗無 recency 下界」）。**淨判：核心貢獻是「修正 S9 實證錯誤＋上修嚴重度」而非全新盲點**，與 C1/CG4 同屬「raw 極端/失真值未守護→威脅 Ridge 而非 IC」族。

### Y3. monthly_revenue_yoy 對 lumpy/project 股 = 基期樂透噪音、非「成長動能」（已落地 core）✅（novel 分歧）
- **本質**：`_REVENUE_SQL` 取單月 revenue、`_compute_revenue_yoy` 直接 `log(單月last/單月-12)` 無平滑；project 股單月營收會計時點變數主宰 YoY。
- **證據**：`panel.py:41-70`。psql：股 4113 **在 core**（28 panels），raw 單月營收在 53,000↔1,014,571,000 千元月月暴跳，monthly_revenue_yoy 在 +10.05→-9.86→-8.87 劇烈擺盪（-9.859685=`ln(53000/1014571000)`）；單月 YoY std=3.444 vs 3m 平滑 2.553（多 ~36% 噪音）；876 個有營收史 core 股中 244 檔(28%)單月 std>1.2× 3m。
- **為何是真盲點**：違方法論 line119「YoY=成長動能」intended 語意 + #15 名實；3m/TTM 平滑是方法論 line75 自列選項卻未實作。CG4 最嚴重例 2528 不在 core，本盲點坐實 4113 在 core 全程。
- **修法**：改 trailing-3m 或 TTM（近 12 月加總）算 YoY，或保留單月並加 3m/TTM 平滑伴生特徵讓模型自選（方法論 line75 已授權、執行層）。
- **下游影響**：衝擊 Ridge 係數擬合及橫斷面 rank 中 lumpy 股落點；rank IC 對同股時序單調變換不變故 IC 本身受限。
- **共識/校正**：兩票 medium；novel 分歧（驗證者B 判 false——CG4 已點名同一 `_compute_revenue_yoy`、同根因 lumpy 微基期）。**淨判：併入 CG4 作「修法擴充」（除 winsorize 外增列改基底單位為 3m/TTM），不另立新 gap，標 4113 為 core 內坐實案例**。

### Y4. gov_bank_net_buy_60d 用「金額(元)」非「股數」算淨額 → 跨股不可比、price 污染、可 sign 翻轉 ✅✅
- **本質**：`_GOVBANK_SQL` 用 `sum(buy_amount)-sum(sell_amount)`（元），feature=`sign(Σ元)×log1p(|Σ元|)`，megacap 因高股價恆居分布頂、3% 股方向與股數口徑相反。
- **證據**：`chip.py:72-77, 137-139`。psql：buy_amount/buy≈2369=2330 股價（單位確為元）；2330@2026-05-31 net_元=91,985,711,645→feat=25.245（**全特徵 MAX**）vs net_股=48,358,432→feat=17.694（差 7.55 單位）；近 90 日 80-99/2724-2728≈3-3.6% 股 sign(net_元)≠sign(net_股)；股 3481 元-net=+112.7M（看似護盤淨買）但股-net=-28.1M 股（實際淨賣）= **方向被單位選擇翻轉**。
- **為何是真盲點**：違 #9（price level 污染 magnitude）+ 名實（「淨買」本意=方向/數量非金額）+ 母原則③；39-gap line176「gov 丟 gross」未質疑單位選擇本身，其建議「淨額/gross 正規化」仍元/元、無法修 sign-flip。
- **修法**：改用股數淨額（`buy-sell`，源表現成、source-pure）再除 60 日 gross 或流通股數正規化（去 price/size），同時解方向+量級+尺度三問題。
- **下游影響**：megacap 偽極端 rank + 3% 股方向錯誤污染橫斷面。
- **共識/校正**：兩票 real＋novel、medium 一致（自 high 下修：gov 為稀疏 E 類、有效 panel 少、sign-flip 僅影響少數股、且 G2/G3 假零為更上游問題）。

### Y5. chip-continuous 四特徵 LIMIT-1/最近窗無時效上界 → 停更股 19 年前值偽裝 as-of ✅（novel 分歧）
- **本質**：`_SHARE_SQL`/`_MARGIN_SQL`/`_HOLD_SQL` 皆 `ORDER BY date DESC LIMIT 1` 無下界；institutional 為 LIMIT 30+需≥20 列（機制略異）。
- **證據**：`chip.py:48-58`。psql 2026-05-31：foreign 259/2619 源列>365 天 stale（最舊 2807 取 2007-01-17、19 年前）、margin 116/2136、top_holders 137/2925。**更隱蔽的升級證據**：36 檔 foreign-stale 股在 core_universe，其中 2311 太電 price 2026-06-11 LIVE（單日量 7.4M 股）但 foreign_holding_pct=63.77 凍結於 2020-12（5.5 年 stale）直入 2026 panel——**真正受害者是活躍 in-core 股的籌碼特徵被靜默凍結**。
- **為何是真盲點**：as-of≤t 形式滿足、實質違反「t 當下真看得到的近期狀態」（#8）+ #15。根因含上游 sync 缺口（`TaiwanStockShareholding` 對眾多活股止於 2020-12），但特徵層 bug 獨立成立：無 recency gate 將上游缺口靜默轉成假 as-of。
- **修法**：三 LIMIT-1 SQL 加 recency 下界（`date >= panel_date - INTERVAL '~90 天'`，籌碼公布頻率對應），超界缺列（#1）；連帶查 Shareholding 為何活股停 2020。
- **下游影響**：in-core 活股籌碼特徵凍結污染當期排序。
- **共識/校正**：兩票 real，medium↔low；novel 分歧（驗證者B 判 false——39-gap line171 已就 institutional LIMIT-1 之 1107/9104/2381 舉「停更股 stale」例，本盲點為逐特徵量化延伸）。**淨判：foreign/margin/top_holders 三純 LIMIT-1 特徵的量化＋in-core 活股凍結個案為相對新貢獻；institutional 部分重複**。

### Y6. institutional_net_buy_ratio_20d 的「20d」實為「20 個法人有動作日」窗 → 跨股時間尺度不一致 ✅（low↔medium）
- **本質**：`_INST_SQL GROUP BY date ... LIMIT 30` + `inst[:20]`，thin 股這 20 個活躍日可橫跨多年，無 calendar-day / 交易日對齊。
- **證據**：`chip.py:35-40, 87-89`。psql 2026：median span=27-28 天（液態股≈20 交易日 OK）但 max=3,048-4,624 天、~492-591 股 span>60；非單調變換證明：股 6702@2017-01-19 現行 ratio=-0.685（20 inst 列跨 65 日）vs 真 40-calendar-day 窗=-0.943 → **改變數值會重排 rank**。
- **為何是真盲點**：違母原則③「相對化須同口徑」+ #9 名實（feature 名隱含固定近期窗、實作 density 依賴）；39-gap「三大法人成分漂移」談 WHICH name（成分集，正交），本盲點談時間窗長 density 依賴。
- **修法**：`_INST_SQL` 改 `date >= panel_date - INTERVAL '~40 天'`（或以全市場交易日曆取真 20 交易日窗）後 sum；窗內法人活躍日<門檻缺列（#1）。
- **下游影響**：30/878 core 股 span>28 天（848 乾淨 ≤27 天）；最新 panel core 內僅 9 股 span>60 且全同時 stale（與 R3/Y5 recency gap 糾纏，修法合流）。
- **共識/校正**：兩票 real＋novel，low↔medium。**事實校正**：報告「core 股 2473 恰 20 活躍日橫跨 4966 天」**不重現**（2473@2026 span 僅 27 天），具體例誇大；但整體分佈（max 數千天）成立。極端尾多為近下市/coverage collapse 股，非乾淨 thin。

### Y7. gov_bank/sbl/lending 三 E 類橫斷面零尖峰 31-33% + log1p 斷層 → 1/3 cross-section 塌成單一 tied rank ✅（嚴重度降 low）
- **本質**：真零填 0 與最小事件之間有 `log1p` hard gap，1/3 股同綁 0 rank 無排序力。
- **證據**：`chip.py:128-139`。psql 2026-05-31（n=3096）：sbl 32.8%、lending 31.1%、gov 8.9% 同綁 value=0；sbl 最小非零=6.908755=`log1p(1000股)`，0 與 6.9 之間斷層。
- **為何是真盲點**：違 #15（零尖峰須揭露不靜默）+ 母原則③（rank 退化）；39-gap line178 反而明判 sbl/lending 真零合法、只盯 gov（S4），未量化各 panel 零尖峰比例與 tied-rank 退化。
- **修法**：出貨附「該 panel 零尖峰比例」診斷（#15）；考慮加「是否有事件」二元伴生特徵分離 0-spike 與量級。
- **共識/校正**：兩票降 **low**。**重大 code 誤讀校正**：報告稱 lending 有「log1p 斷層 / 元 vs 千元單位敏感」**錯誤**——`chip.py:134` lending 用 `np.mean(fees)` **無 log1p**（最小非零=0.01、無斷層）。有效核仁僅 sbl 的真實 6.9 斷層 + 1/3 tied-rank 未揭露；應丟棄 lending log1p 主張。屬診斷/揭露層非數值正確性 bug。

---

## 🟢 增強級（low 共識 / footgun 或名實精煉，不威脅現行 model 結論）

### G1. momentum 與 volatility/range 族內無效列處理策略不一致（四種互斥邏輯）✅（novel 分歧）
- **本質**：同價量族對「無效 bar（close=0/零報酬）」採四策略——momentum 原始列位移不剔、volatility fin_ret 過濾往前補、turnover/dollar_volume 含零入均、range `(h-l)/c=0/0=nan` skipna；同掛 `_Xd` 後綴卻量測於錯位有效窗。
- **證據**：`panel.py:88-101`。psql：711131@2023-12-31 momentum_20d 窗到 2020、volatility_20d 量近期，完全錯位；006203@2016 turnover_mean_20d=0.95（含零日全均）vs 非零均=1.46。完整度門檻不一：momentum_5d 有而 volatility_20d 無者 990 筆。
- **修法**：統一 `valid-bar mask`（close>0 且落日曆窗內），全族在同一 mask 取 w 個有效 bar，不足全族缺列。
- **共識/校正**：兩票 real，medium↔low；novel 分歧（line 181 未驗候選已列構成機制）。**淨判：價值在「族內口徑不自洽」統合框架，底層機制多已散見報告；屬 R1/R3 修法的下游受益項**。注意 1307@2007 案例歸因有瑕（實有 3481 finite returns，部分屬 build artifact 非零報酬過濾）。

### G2. volatility_20d 與 range_mean_20d 同 20 窗採不一致缺值語意 ✅✅
- **本質**：volatility fin_ret 過濾回填、range `.iloc[-20:].mean()` 遇 close=0 整支 nan 丟掉 → 覆蓋集不一致。
- **證據**：`panel.py:95-97 vs :101`。psql EXCEPT：有 vol 無 range=464、反向=1404、合計 1868；4923@2014-12-31 最後 20 列全 0，volatility 回填落地、range 缺列。
- **共識/校正**：兩票 real＋novel、medium。**重要校正**：「1868 不同步」**混兩個 code 版本**——反向 1404 大多是**舊 volatility 公式**（git 1a8fe01 `ret.iloc[-w:].notna()>=w`）的 stale DB 殘留，**真正當前可重現背離只有 464 正向**。須先重建 feature_values 消除舊殘留，報告應拆為「464 當前 + 1404 舊版」。即時機制描述「(H-L)/0=inf」不精確（4923 為 0/0=NaN）。

### G3. price_to_252d_high / cycle 與 252 共線（corr 0.72、極端端逐位元相同）被當兩獨立 alpha ✅（novel 分歧）
- **本質**：共用 hi 分母，`p2h==1.0` 與 `cycle==1.0` 各 2867 筆逐筆綁定，28% 列逐位元相同（lo=0 退化）；被當兩個 +0.088 並列高估 breadth/Meff。
- **證據**：`panel.py:103-106`。psql：corr=0.7206（n=80159）；移除退化列 corr 不降反升至 0.7671（**二者本是同族尺度、非 lo=0 造成**）。
- **共識/校正**：real 兩票，low↔medium；novel 分歧（M1 baseline 報告:88 已記「cycle~p2h +0.83 位置同義」、Ridge 塌縮）。**淨判：headline「兩獨立 alpha 未察」被推翻——M1 已察，下游入憲方法論報告把該 caveat 漏掉改成並列雙計**。rank IC 對單調變換不變，雙計影響的是 Ridge 係數與 breadth 敘事非 IC 本身。建議：歸因前降共線 threshold 至 0.7、FDR Meff 重算。另發現旁支：0059@2022-06-30 as-of close 本身=0、p2h=cyc=0.000000 落地（違 #1）。

### G4. price_to_252d_high / cycle 用 `c.iloc[-252:]` 含當日 → 右尾夾死 1.0、創新高無強度區分 ✅✅
- **本質**：hi 窗含 `c.iloc[-1]`，當日創新高 `c==hi`→p2h 恆=1（吸收態 2867 筆/3.58%），無突破幅度資訊。
- **證據**：`panel.py:103-104`。psql：p2h max=1.0、value==1.0 計數=2867；0051@2026-05-31 末 close 141.90==trailing-252 max → p2h=1.0。
- **共識/校正**：兩票 **low（不上調）**。**框定校正**：含當日的 trailing range-position 是「距 52 週高」之**標準正確定義**（George & Hwang 52-week-high、Williams %R 慣例），**非 bug**。報告 proposed 的 `c[-1]/max(prev 252)`（可>1）是**另一個特徵（突破幅度）**＝語意變更（決策層 #9），不可逕改。正解偏向**文件化「含當日、上界飽和為設計」**；資訊損失僅創新高股間幅度差異，momentum_252d 已輔助捕捉。屬名實落差低嚴重 nuance、值得記載非缺陷。

### G5. volume_surge_5_60 max=12.0 是近死股算術巧合非資料天花板（v60 無最小活躍門檻）✅（high→medium/low）
- **本質**：`if v60>0` 唯一守門，60 日窗只零星幾筆交易且集中最近 5 日時 `v5/v60→60/5=12.0` 算術上限。
- **證據**：`panel.py:107-110`。psql：max=12.0 共 5 筆全近死股（8934@2008 僅 2 天各 1000 股→v5=400/v60=33.33/比值=12.0）。
- **共識/校正**：兩票 real＋novel，**medium↔low（自 high 大幅下修）**。**核心 evidence 證偽**：報告稱「value>5 共 1318 筆全部 dollar_volume<12」，psql 實際**僅 171/1318<12**，該族 dv 中位數=15.5≈全市場（相當流動）；290 core 列中位 dv=17.4、僅 6/290 低流動——**多數高 surge 是流動股真放量＝特徵 intended 訊號非偽訊號**。災難 artifact 僅極尾。淨判 low：footgun + 依賴 core gate 隱性守門，非紅線。修法（v60 最小活躍門檻）合理但收益有限。

### G6. volume_surge_5_60=0 雙語意污染（近期停牌 v5=0 與真實低量同映 0）✅（medium→low）
- **本質**：`v5=0`（近 5 日無成交=停牌）但 `v60>0` → 輸出 0.0，與真低量在 feature_values 無法區分。
- **證據**：`panel.py:108-110`。psql：value=0 共 976 筆；2540@2012-12-31 v5=0/v60=137.28→0.0。
- **共識/校正**：兩票 **low（自 medium 下修）**。**措辭校正**：「停牌與真低量映同一個 0」**不精確**——真低量股產生**小正值**（最小非零=0.000015）**永不為 exact 0**，二者在**連續值空間可區分**；可辯護實害僅在 rank 空間 0 與 0.000015 相鄰最弱端、損失「瀕下市」可區分資訊。停牌瀕下市股本就是相對強弱最弱端、rank 置底未必經濟錯誤。「分子爆 12=不對稱污染」之因果為臆測（code 無 clip）。屬增強非紅線。

### G7. sbl_short_balance_log 是 size proxy 非「空方壓力」（與規模 corr=0.70、未對流通股正規化）✅（novel 分歧）
- **本質**：`log1p(絕對借券餘額股數)` 零相對化，大型股天然高。
- **證據**：`chip.py:59-64, 125-129`。psql：2026-05-31 前 5 名皆大型股；corr(sbl, dollar_volume_log_20d)=0.697（驗證者B 用單日 money 得 0.561，proxy 不同）；2330 絕對餘額 8.3M 但/流通股僅 0.03% float。
- **共識/校正**：兩票 real，medium；novel 分歧（驗證者B 判 false——39-gap 母原則③相對化群 G5/G12/G13/G19/G20 已涵蓋「chip 存全 raw 絕對值、特徵層相對化零落地」全 7 chip 特徵，line169 turnover_mean_20d 為同型已驗範例）。**關鍵修法校正**：報告主方案「bal/SBLShortSalesQuota → 0-1」**運算錯誤**——Quota 是「當日剩餘配額」逐日遞減，88-100% 股 bal>quota、比值高達 1941x；**正確 source-pure 正規化是 /流通股數**（`TaiwanStockShareholding.NumberOfSharesIssued` 現成，落 0-0.104 乾淨 float 使用率）。**淨判：歸入相對化群之 sbl 補充註，非孤立新盲點**。

---

## ⚠️ 共識否定 / 不確定（誠實標記）

### N1. 停牌污染 cycle/p2h artifact 與報酬同向 → 可能貢獻偽 IC ⚠️（1 real / 1 不成立）
- **報告主張**：close=0(2668)+lo=0 退化(19930)合計 28% 進 IC、artifact 與停牌弱勢股相關→偽 alpha。
- **驗證結果**：**運算缺陷本身屬實（同 R1/R2），但「偽 IC 威脅」被實證證偽。** 兩驗證者皆降 **low**，其中一票判 `is_real=false`：
  1. **資料流誤解**：IC 由 `_panel_matrix` 只取 core_universe（流動性 gate 過 dollar_volume 分位），**非全 feature_values**；28% 是算在全庫含非核心股。限縮到真正 IC 輸入（core 股、2014+ 生產窗），cycle 窗含 zero 僅 3.5%、p2h=0 artifact 全在 2007-2012、**2014+ 生產窗為 0 列**。
  2. **方向相反**：被標「最弱 rank=0」的 in-universe artifact 股，其前向 ~60d 還原 log-return 均值 **+0.146（26 正 vs 9 負）→ 該 artifact 將 IC 拉低（預測 miss）而非製造同向偽 alpha**。
  3. **1102 範例錯誤歸因**：混淆兩個不同 panel（2026-05-31=0.126 vs 2024-12-31=0.846），非同一觀測被誤標。
- **淨判**：lo=0 退化是真實 ongoing 正確性瑕疵（屬 #15 名實層），但**對 +0.088 IC 淨威脅近乎零**。真正可動作項（退化列比例揭露）已由 S4/CG3 收口。**修 R1/R2 後仍應做消融，預期 IC 變動極小、可能微升**。

### N2. ±1 clamp 邊界 412 值多為 thin/ETF/權證 artifact ⚠️（medium↔low、核心 evidence 失準）
- **報告主張**：value=±1 共 412 個（8 在 core），全為 ETF/權證 thin 股單向法人流 artifact。
- **驗證結果**：兩票 real＋novel，medium↔low。**evidence 失準**：8 個 core 案例經 psql 全為**普通 4 碼股**（1586/3484/3490/4506/4513/6175/6265/6409），**非 ETF/權證**；1586 之 20d gross 落第 80 百分位（非 thin）、20 連續日真實單向＝**可能是真強訊號非噪音**。±1 非離散尖峰而是連續分布尾端（0.9-1.0 帶 1498 值遠多於邊界 412）。真正可辯護弱點僅極低 gross 之 6265。
- **淨判**：機制（單向流卡 ±1、無最小活躍門檻）為真，但「全為 artifact」框定誤導；範圍僅 0.6%。修法宜用「自身歷史 gross 中位數比例 shrinkage 向 0」（保留列、不傷 roster 完整度），優於改缺列；屬 low 技術債。

---

## 與 39-gap 報告的關係：本輪補強了哪一塊

39-gap 報告聚焦 **build/持久化口徑（S 系列）、除權息原始 vs 還原價（CG 系列）、winsorize/離群（C 系列）、NULL vs 0 假零（G 系列）**。本輪深挖**特徵值運算層的窗口聚合機制與守門非對稱**，補強三個 39-gap 未系統涵蓋的維度：

1. **停牌 close=0 哨兵列對 min/max 聚合的污染（全新正交根因）**：39-gap 的 CG3 把 cycle 假地板歸因除息（分母端原始價），本輪坐實**真正主因是停牌 close=0 污染 252 窗 min 錨點（分子/錨點端，占 28% 列、換還原價不解）**。這是對 headline 最強 alpha 威脅的根因重定位——除權息與停牌污染是**雙重正交威脅**，須一併修一併消融。

2. **`isfinite` 守門的非對稱失效（全新機制）**：39-gap 未指出 panel.py 唯一數值守門對「log 類除零」有效、對「比值分子=0」系統性失效，使 momentum 族正確缺列而 position 族漏網存活——與 `label.py:79` 的 `close<=0` 守護形成**特徵端 vs label 端雙標**。

3. **recency 下界缺失的全族量化 + universe 穿透證據**：39-gap 的 stale 旁註僅針對 chip institutional LIMIT-1，本輪坐實同病灶存於**價量 rolling 窗整族 + chip-continuous 三 LIMIT-1 特徵**，並提供 39-gap 缺的關鍵證據——**core_gate 完整度 gate 不查 price recency，25-36 檔 stale 股（含 LIVE 報價但籌碼凍結的 2311 太電）已穿透進 production core_universe**。

**誠實聲明（共識與不確定性）**：
- 本輪 24 盲點經去重合併為 **R1-R4（4 根本）+ Y1-Y7（7 重要）+ G1-G7（7 增強）+ N1-N2（2 否定/降級）**。
- **兩驗證者全同意 real＋novel** 者：R1、R3、R4、G2、G4、Y4。其餘多有嚴重度或 novel 分歧，已逐條標記。
- **嚴重度普遍受 core_gate 緩解**：多數 medium/low 的共通主題是「feature_values footgun 為真，但流動性/完整度 gate 結構性排除停牌薄量股，對 IC/Ridge 淨污染有界」。**但 R1-R3 之 in-core 穿透證據顯示 gate 並非萬無一失**，尤其 stale/cycle 退化已實證進核心。
- **未直接重算項（不確定性）**：(a) raw-vs-adj 對 cycle/p2h 的 IC 消融未做（屬 CG 範疇）；(b) 修 R1/R2 後 cycle alpha 是否存活之消融未做（強烈建議優先）；(c) `core_universe_asof` 表現 DB 不存在（呼應 S1），故部分「入模污染」為結構鏈成立而 live 路徑待重建後方可坐實。
- **多處 evidence 數字/個案被校正**（不影響機制結論）：1101 缺 lending（錯，實有值）、2473 inst span 4966 天（不重現）、volume_surge 1318 全不流動（實 171）、sbl/Quota 正規化（運算錯，應/流通股）、lending log1p 斷層（code 誤讀，lending 用 np.mean 無 log）、1102 兩 panel 混淆、Adj 表有停牌 0 列（錯，0 筆）。已守 #15 逐一標明。

---

### 建議處理批次（執行層，碰護欄停手）

| 批次 | 內容 | 動機 |
|---|---|---|
| **批次 A（最優先，治根）** | 統一 `valid-bar` 守護：計 hi/lo/momentum/volatility/range 前剔 `close<=0` 列 + 日曆 recency 下界，剔後有效 bar 不足→整股價量族缺列（#1，同 label.py:79）；同步套 chip/valuation/revenue 四源 recency gate | 一改治 R1/R2/R3/Y1/Y2/Y5/Y6/G1/G2；解 headline cycle alpha 材質疑雲 |
| **批次 B（重建 + 消融）** | 以批次 A code 重建受污染 panel + 重建 chip 三 E 類 2007-2013（治 R4）；raw-vs-clean + raw-vs-adj 雙消融重算 cycle/p2h rank IC | 確認 cycle alpha 是否存活（決策層需此數據）；消除舊版 build 殘留（G2 的 1404） |
| **批次 C（名實校正）** | gov 改股數淨額/正規化（Y4）；revenue 加 3m/TTM（Y3，併 CG4）；sbl /流通股（G7，併相對化群）；inst 窗改日曆對齊（Y6） | 相對化母原則③落地、去 price/size 污染 |
| **批次 D（揭露/文件，低優先）** | 零尖峰比例診斷 + is-event 二元伴生（Y7）；文件化 p2h「含當日、上界飽和為設計」（G4）；volume_surge 最小活躍門檻（G5/G6） | #15 不靜默；footgun 收口 |

> 批次 A 牽動完整度 gate 與 universe roster（收緊缺列門檻會降完整度），屬**牽動多檔的方法層變更**，建議重建前先呈用戶確認對 core_universe 規模之衝擊評估（#19/#26 決策層）。

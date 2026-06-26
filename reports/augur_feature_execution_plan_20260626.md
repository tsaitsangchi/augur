# augur 特徵執行計劃 — 設計藍圖(三鏡頭)→ 落地路線(2026-06-26、v2 完整性檢核後)

**性質**:執行計劃(#15:計畫、非成果;任何特徵之預測力未經 walk-forward + 五鏡裁決前皆為假說)。
**依據報告**:`feature_design_first_principles` / `pareto_thought` / `cycle_thought` / `f2_feature_expansion_roadmap` / `f3_model_plan_three_thoughts`(皆 20260612)+ `evaluation_M1_baseline_20260626`。
**地基(#20 實證、非記憶)**:排序與前置皆基於 2026-06-26 對本機 DB 之實查(§1)。
**護欄定位**:特徵源 raw 已 84/84 完整 → **全程 feature 層(算+寫 DB)、零 API 放量、可逆**;屬 #20/#26 護欄內自驅動工作。唯排序、發布日 lag、核心股地板數值需用戶過目。
**v2 修訂(2026-06-26 完整性檢核)**:補 11 處遺漏 — 新增階段 4 跨鏡頭交互、康波補 C4、§5 完整度收縮管理、§7 工程基建、籌碼 T+1 gate、金礦時點欄位、H=5、既有特徵技術債、IndustryChain 待實證。

---

## 1. 現狀實證盤點(2026-06-26 本機實查)

| 面向 | 實證結果 |
|---|---|
| **本機 feature_values** | 22 feat × 28 panel × 最新 2026-05-31(14 價量 + 1 月營收 + 7 籌碼)|
| **估值 F2c** | `panel.py` 已整合 valuation,但本機 DB **未重 build**(仍 22 feat)→ 落後另機(M1 的 27 feat)|
| **核心股收縮(已溯源、A1 動因)** | M1 §1.2 實證:v4 22feat **878 股** → +5 估值 27feat **371 股(−58%)**;主收縮=pe_ratio「14 年從不虧損」語意 gate |
| 特徵源 raw | 全齊:PER 756萬 / MarketValue 851萬 / 10Year 535萬 / 財報三表(Q1 2026-03-31)/ HoldingSharesPer 2073萬 / IndustryChain / TAIEX / FRED |
| `context_values` 表 | **不存在** → X 類 context 零落地 |
| feature/universe/eval build CLI | **全無 script 入口**(靠臨時腳本)→ #18 落差,§7 補 |
| 五鏡 audit | `/tmp` 臨時腳本,未正式化為 `audit/` 模組 → §7 補 |

## 2. 框架:特徵落地是「二維」推進

```
維度 A(資料源/表覆蓋,F2 roadmap):  籌碼✓ → 估值 → 基本面 → context → 事件 → 衍生
維度 B(transform 鏡頭/三思想):      第一性①(已主導) + Pareto②(0) + 康波③(僅2位置) + 跨鏡頭交互(0)
```
當前 22 feat 幾乎全擠在「第一性鏡頭 × 價量/籌碼」一格;Pareto/康波兩鏡頭、跨鏡頭交互、F2d 後段表全未動。

## 3. 排序原則 + 裁定

**四準據**:① 已實證 alpha 優先(估值)② 邊際成本最低優先 ③ 前置就緒(#8 風險低者先)④ 每批落地即五鏡裁決(#11)+ 消融(F3 命題)。

> **排序裁定(用戶 2026-06-26)**:三鏡頭按設計邏輯順序逐鏡頭落地,跨鏡頭交互續於三鏡頭後。順序:
> **0 估值 → 1 第一性補完 → 2 Pareto → 3 康波 → 4 跨鏡頭交互 → 5 F2d 基本面 → 6 context → 7 事件+衍生**。

## 4. 分階段執行計劃

> 每階段固定四交付:① feature 程式 ② 本機 build 寫入 ③ PHASE 9 五鏡 audit ④ 階段報告(含**核心股數量實測**、source-traceable #15)。做完呈過目再進下一(#19)。依賴後段源的軸於該階段回補。

### 階段 0 — 估值本機補齊 + 全鏈 build CLI(quick win、對齊另機)
- 本機重跑 `build_panel`(28 panel)→ feature_values **22→27 feat**(補 5 估值)。
- **全鏈 CLI**(§7):feature / universe / eval 三 CLI 上線 → 驗收可重跑。
- **⚠️ 本機現缺**(實證 2026-06-26):`core_universe_asof` 表不存在(M-2 在另機建)→ universe CLI 須**先建 asof 表**才能重現 M1/M-2 as-of 口徑。
- **驗收**:本機重現 M1(as-of Ridge H60 rank IC ≈ +0.13);實測核心股數(預期 ≈371、對照另機)。
- **風險/護欄**:極低、無 API、可逆;估值無 P-lag(交易所每日公布、date≤t 即安全 #8)。

### 階段 1 — 第一性原理鏡頭補完(軸①②深化 + 軸⑦橫斷面結構)
- **定位**:第一性已是 22 feat 主體 → 此階段=**補完未落地軸**,非從零。
- **軸① 深化**:Amihud 流動性、量價背離、跳空、K 形態(實體/影線比)、十年線位置、當沖佔比/不平衡。
- **軸② 深化**:券資比/軋空壓力、借券費率變化、外資距上限空間、大戶比變化、法人連續同號天數、外資 vs 投信分歧。
- **軸⑦ 橫斷面結構(全新、重要)**:產業內 demean/rank — **「相對強弱」正確座標系**;上市/上櫃分群 normalize。
- **✅ 實證修正(2026-06-26)**:`IndustryChain` 實查僅 **2026-06-16~23 快照(6 日、1554 股、無歷史)**→ 不可用於歷史 panel 產業分群 → **改用 `TaiwanStockInfo.industry_category`(by-date 每日、有歷史,core_gate 本就用它)**;IndustryChain `sub_industry`(細產業鏈)僅近期 panel 可用、或標 #8 回溯假設(產業歸屬相對穩定、但併購/轉型例外、不假設歷史一致)。
- **C1 金礦時點**:外資籌碼用 `Shareholding.RecentlyDeclareDate` 為 as-of 錨;一併檢核既有 `monthly_revenue_yoy` 是否該用 `MonthRevenue.create_time`(語意 probe)。
- **C4 既有特徵技術債**:檢核既有 7 籌碼正確性(`lending_fee_rate_mean_30d` 命名 vs 窗口等,類 volatility robust 修正)。
- **源**:價量/籌碼/IndustryChain 本機齊 → 純 transform、無 API、低風險。
- **驗收**:五鏡 + 消融(深化軸 vs 現 27-feat baseline 增量);H=20/60 主戰場、H=5 探索。

### 階段 2 — 八二法則 Pareto 鏡頭(集中度泛函、軸 P1-P4)
- **特徵族**(`features/concentration.py`):持股級距 Gini/HHI/entropy + Δ集中度、法人別淨買 HHI/max-share、窗內日量分布 Gini、窗內日報酬 Gini/skew/kurtosis(跳躍 vs 漂移)。
- **#9 鐵則**:全 cutoff-free 連續泛函(禁 top-20%、decile、「大戶=N 張」)。
- **#8(A2)**:用籌碼/法人 → T+1 時點 gate(盤後公布、保守 shift(1)、逐表 probe)。
- **前置實證**:HoldingSharesPer 級距結構/申報頻率 probe。
- **依賴回補**:P5 營收支配→階段 5;P6 市場 regime→階段 6。
- **驗收**:五鏡 + 消融(防共線稀釋誤判 F3 五修正#2)。

### 階段 3 — 康波週期鏡頭(相位/共振/背離/資金流循環、軸 C2/C4/C5/C6)
- **可立即做(源在價量/籌碼)**:多尺度 range-position、time-since-extreme、drawdown/runup、多尺度動能同向計分(共振)、二階導(減速度)、量價相位差(背離)、短/長窗 vol 比;**C4 資金流循環**:法人累計淨流位置 vs rolling 區間(吸籌/派發相位)、流向轉折。
- **#9 鐵則**:相位/歷時由資料自身極值定義、零固定週期(禁 40-60 年)。
- **#8(A2)**:C4 用籌碼 → 同 T+1 時點 gate。
- **依賴回補**:C3 基本面循環→階段 5;C1 景氣循環→階段 6。
- **驗收**:五鏡 + 消融(康波族 vs 前二鏡頭 baseline 增量);H=20/60。

### 階段 4 — 跨鏡頭交互電池(F3 強化①、用戶裁定獨立階段)
- **定位**:三鏡頭各自落地後的「下一層」、潛力最高;跨族**連續**交互(無切點 #9)。
- **特徵族**(`features/interaction.py`):相位×集中度(吸籌假說:低位+籌碼收斂)、動能×量Gini(跳躍 vs 漂移動能後續不同)、估值缺口×營收 share 動能(排價值陷阱)、官股×外資雙力交互。
- **前置**:三鏡頭(階段 1-3)落地。
- **驗收**:五鏡 + 消融(交互 vs 三鏡頭線性和增量;若無增量誠實入檔、#15)。

### 階段 5 — F2d 基本面(財報三表、軸③、**發布日 gate**)
- **範圍**:FinStmt/BalanceSheet/CashFlow(Q1 2026-03-31 齊)→ ROE/ROA/margin 及 Δ、YoY/成長、OCF/NI 應計品質、capex 強度。
- **⚠️ #8 最危險**:財報 `date`=期末非公告 → **發布日 gate 必須**:(a) probe API 公告欄(實證);(b) 無→法定申報期限保守 lag(Q1≤5/15、Q2≤8/14、Q3≤11/14、年報≤3/31)。lag=operational 透明參數。
- **#9**:比率=會計恆等式(允);禁硬閾值 → 橫斷面 rank/z。
- **回補**:康波 C3 基本面循環 + Pareto P5 營收支配。
- **驗收**:**雙口徑 IC**(gate vs 無 gate)證 anti-leakage;五鏡。

### 階段 6 — X 類 context(建 `context_values` 表、軸⑥/C1)
- **架構新增**:`context_values(panel_date, feature, value)` + panel 有效性檢查(context 缺=panel 無效、非排除股)。
- **特徵**:大盤動能/波動、景氣領先+notrend、利差/政策利率、台幣動能、FRED regime、市場集中度 regime、個股×context 交互(beta/相對大盤)。
- **⚠️ #8 FRED vintage**:總經事後修訂、最新值=look-ahead → 發布滯後保守 lag + metadata 標 vintage;ALFRED 後續選項。
- **回補**:康波 C1 景氣 + Pareto P6 市場 regime。

### 階段 7 — 事件型真零 + 衍生/國際/CB(F2f + F2g)
- **F2f 事件 E 類(真零)**:Dividend(用 AnnouncementDate 零洩漏)/填息/BlockTrade/Disposition/Suspended/減資分割 → days-since/count/flag;News 僅 count(#9)。**前提鐵則**:該表全史 sync ∧ #7 PASS 才可宣稱「無列=真 0」。負空間特徵(F3 強化⑥)。
- **F2g 衍生/國際/CB**:期權 PCR/未平倉、期貨基差、國際大盤、CB 溢價 → 多落 context_values;跨域相位差(C5)。維度 mapping 較重、置最後。

## 5. 完整度收縮管理(A1 — 架構內生張力、計畫核心策略)

**張力**:#1 規定模型只吃 0 缺值核心股 → 特徵越多,「全特徵齊」股越少(F2c 已證 878→371)。
**收縮兩類**:① **歷史長度收縮**(新股缺 252 日)— 價量衍生與現有同源、額外收縮小;② **語意收縮**(虧損無 PER、財報短歷史、籌碼短窗)— 估值/基本面是主因。
**策略(用戶裁定:設地板 + 超限改 conditional)**:
1. **每階段實測核心股數**並入報告(實證、非估計);跌幅歸因(歷史 vs 語意)。
2. **核心股數量地板**:維持橫斷面排序統計意義之最小股數(operational 參數、#9 不寫死、實證定;暫參考 ~200-300 量級、標「實驗中」待驗)。
3. **超限改 conditional**:某特徵使核心跌破地板 → 該特徵改 conditional(如 F2c 月營收豁免金融模式)/ 或走 as-of(M-2 證早期用大池反而 IC 更高)/ 或降為 optional 不入完整度 gate(但仍須守 #1:optional 特徵缺值股不得進該特徵之模型訓練)。
4. **as-of 優先**:評估一律 `build_universe_asof`(逐 panel point-in-time、消 survivorship #8)— 早期 panel 自然用更大池、緩解收縮。

## 6. 橫貫紀律(每階段適用)

- **#11 五鏡**:每批落地後 IC+sign / 共線群 / leave-one-out / SHAP / purged-CV 合判;「SHAP≈0 且 ablation-safe」必移。
- **#8 as-of**:`build_universe_asof` + purged walk-forward;label t+1 進場;**籌碼/法人 T+1 時點 gate(A2)**:盤後公布、逐表 probe 收盤可得性、保守 shift(1);FRED vintage、財報發布日 gate。
- **多尺度(C2)**:H=20/60 主戰場、H=5 週尺度探索、H=252 探索性(結論不入可信度主表、F3 五修正#1)。
- **F3 五修正**:族層級先消融再下鑽 · **共同樣本窗鐵則**(各表歷史深度不齊、消融須同期間)· conviction 守門過 size 中性化 · 成本納入經濟價值主表。
- **#1/#9/#15**:算不出即缺列 · 無切點/無情緒字典入公式 · 每數字 source-traceable。
- **#10 質>量**:特徵預算紀律,五鏡留有增量者,不堆數量(但守 §5 地板、不過收縮)。

## 7. 工程基礎建設(B1/B2 — 每階段可重跑驗收之前置)

- **B1 全鏈 build CLI**(`scripts/`,補 #18 命名慣例、冪等可重跑):
  - `build_feature_panel.py`(呼叫 `features.panel.build_panel`,28 panel)
  - `build_core_universe.py`(呼叫 `universe.core_gate.build_universe` + `build_universe_asof`)
  - `run_evaluation.py`(呼叫 `evaluation.baseline.run_ladder`,輸出基準階梯 IC)
  - → 階段 0 上線、後續每階段共用,驗收口徑一致(#12)。
- **B2 五鏡 audit 正式化**:`/tmp/augur_phase9_audit.py` → 正式化為 `src/augur/audit/<module>.py`(憲章 audit 層職責);階段 1 前完成,後續每階段 import。

## 8. 里程碑與驗收門檻

| 里程碑 | 達成標誌 |
|---|---|
| M-feat-0 | feature_values=27 feat、重現 M1 alpha、**全鏈 CLI + 五鏡模組**上線 |
| M-feat-1 | 三鏡頭全落地(第一性補完→Pareto→康波)+ 跨鏡頭交互、各鏡頭/交互消融增量入檔 |
| M-feat-2 | F2d 基本面 + 發布日 gate 雙口徑驗證 anti-leakage |
| M-feat-3 | context_values 架構上線、個股×regime 交互、回補康波 C1/C3 + Pareto P5/P6 |
| M-feat-final | F2f/F2g 落地;五鏡全表;**核心股數守地板**;特徵集凍結交 F3 M-3 消融 |

**驗收主軸**:不是「特徵變多」,而是「**每個保留特徵過五鏡、每個鏡頭/交互的增量經消融誠實裁決、核心股守地板**」(回答 F3 命題:三思想各自/合體/交互對台股 alpha 有無增量)。
**界面(C3)**:本計畫提供 as-of 核心宇宙(`build_universe_asof`);**已下市股 survivorship 補完**屬 F3 M-3 範圍(補真實退市宇宙),特徵計畫不重複、僅確保特徵對退市股亦可算。

## 9. 決策狀態 + 待確認(碰決策層即停 #20)

1. **排序**:✅ 已定(用戶 2026-06-26)— 含階段 4 跨鏡頭交互(康波後、基本面前)。
2. **核心股地板**:✅ 策略已定(設地板 + 超限改 conditional);**地板數值**待階段推進中實證定(暫參考 ~200-300、標實驗中)。
3. **發布日 lag 參數**(階段 5):probe 財報 API 公告欄後實證再定 — 屆時呈報。
4. **起跑點**:預設從**階段 0**(quick win、對齊另機)起,做完呈過目再進階段 1(#19)。

> 本計劃為 living document;每階段實證結果回寫、排序/地板可依五鏡/消融/收縮結果動態調整(#19 試錯逼近)。

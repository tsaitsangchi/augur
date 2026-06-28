# 三鏡頭特徵工程總報告 — 框架 → 建置 → 驗證 → 經濟價值(2026-06-27)

> **性質**:capstone 總報告(#15 全程可溯)。涵蓋本輪「三鏡頭特徵工程戰役」全貌:思想框架 → 欄位地圖 → 鏡頭特徵建置 → 三軸正交性實證 → 四 Track 擴張探索(A 交互 / C 衛生 / B 馬太 / D 經濟)→ 總結論。
> **資料口徑**:374 核心 / as-of point-in-time / purged walk-forward / 去相關 HAC Eff-t(全程同口徑可比、#12)。

---

## 〇、執行摘要(TL;DR)

1. **三鏡頭框架實證成立**:量(第一性)×形(八二)×位(康波)三軸**真正交**(形×位中位 |corr| 僅 0.022),非漂亮理論。
2. **8 鏡頭特徵入生產**:八二+康波 12 軸生成 → 4 軸存活(量能集中、價/流相位)→ 特徵 27→34、headline H60 IC Ridge +0.1326→**+0.1418**(+7%)、GBDT +13%。
3. **特徵集已飽和**:後續 Track A(跨鏡交互)、B(馬太)**雙淘汰**、C(衛生)**無肥可削** → per-stock 鏡頭 alpha 已被漏斗榨乾。
4. **經濟價值成立(#14)**:Ridge long top20% CAGR +18.3% vs 基準 +15.6%、**Sharpe 1.21 vs 0.97、Calmar 1.13 vs 0.9**——IC 轉成真可交易 alpha(long 側、適度、long-short 無效)。

---

## 一、三鏡頭框架(思想基礎)

三份研究 + 一份綜合(`augur_first_principles_research` / `_pareto_principle_research` / `_kondratiev_cycle_research` / `_three_lens_synthesis`):
- **第一性原理(量)**:資訊內容/水位;拆到基本真理、功能>形式;溯因→演繹→歸納=漏斗骨架。
- **八二法則(形)**:分布形狀/集中度;**80/20 是 α≈1.16 特例、非定律**→ 禁寫死切點、用連續泛函(Gini/HHI/熵)。
- **康波(位)**:時間結構/相位;**學界最爭議(apophenia)**→ 思想可入數字不回流最關鍵;測 data-driven 相位、不賭週期長度。
- **綜合精華**:三鏡=一條紀律(剝借用數字、測資料自定義不變量)三次旋轉;同敵(自欺/妄見)同藥(市場裁決);**量×形×位三正交軸**。

## 二、欄位地圖(`field_lens_map`)

342 數值訊號欄 × 21 類別,各標三軸潛力(`augur_field_lens_map`):八二可做 273/342、康波特化相位 317/342、P-lag 36;核心管線 12 表 100% 分類。**量能/法人流/價格=三軸皆富**(事後印證存活特徵出此三類)。

## 三、鏡頭特徵建置(發散 → 漏斗)

| 階段 | 結果 |
|---|---|
| 生成 | `concentration.py`(八二 P1-P4)+ `phase.py`(康波 C2/C4)= 12 軸 25 候選 |
| holistic 五鏡 | 量能集中/流相位/價格相位存活;持股集中(冗餘 top_holders +0.97)、報酬集中(弱)淘汰 |
| 提拔關卡(as-of+HAC+多seed)| **8 存活全 \|HAC-t\|≥2.8、多因子增量全正** |
| 落地 | 提拔 8、剪 volatility_20d(共線)、淘汰 17;全 roster 重建 35 panel/2.36M 列/34 特徵 |

**8 存活**:`inst_cumflow_position_60/120d`(康波 C4 流相位,**最強 HAC-t 4.35**)、`volume_gini_20/60d`+`volume_max_share_20/60d`(八二 P3 量能集中)、`range_position_120d`+`days_since_high_252d`(康波 C2 價格相位)。

## 四、三軸正交性實證(`augur_lens_correlation_analysis`)

| 軸對 | 中位 \|corr\| | |
|---|---|---|
| 形×位 | **0.022** | cross(近乎完全獨立)|
| 形×量 | 0.100 | cross |
| 位×量 | 0.131 | cross |
| 位·位 / 形·形 | 0.458 / 0.619 | within |

→ cross ≪ within、**三軸正交實證成立**。**八二(形)最互補**(對既有特徵近乎正交、本 session 真增量根因);量×位有動能-相位耦合(~0.69、非全正交)。

## 五、擴張探索 A→C→B→D

### Track A 跨鏡交互 → ❌ 線性冗餘
3 交互(size×集中殘差、流相位×流水位、價×流相位):單因子強(x_gini_resid_size HAC-t −6.29 全 session 最強)**但多因子零增量**——皆成分之線性組合、成分已在模型。**精煉跨鏡前沿主張:價值已由各正交軸獨立特徵捕獲(模型自組),顯式線性交互冗餘**。

### Track C 衛生/精瘦 → 無改動(已最佳)
- C1 RobustScaler(抗 pe 14500x 尾):Δ≈0 → **rank-IC 對尾本就穩健、pe 盲點對此度量 non-issue**。
- C2 位軸去冗餘:drop 任一即傷(cycle −0.012 Ridge / price −0.004 GBDT)→ **高相關 ≠ 可刪、殘差各帶增量**;全留。

### Track B 八二 P6 馬太 → ❌ 與動能冗餘
rank 動態(市值/動能 rank 變化):mktcap HAC-t 0.58 不顯著、mom 1.96 臨界但多因子增量全負。breadth/regime 屬 context、橫斷面 IC 恆 0 不可驗。

### Track D 經濟價值(#14)→ ✅ 成立(long 側適度)
2021-09~2025-12、18 期季度、top 20%:

| 投組 | CAGR | Sharpe | MaxDD | Calmar | 勝率 |
|---|---|---|---|---|---|
| **Ridge long top20%** | **+18.3%** | **1.21** | −16.3% | **1.13** | 78% |
| GBDT long top20% | +16.7% | 1.04 | −16.9% | 0.99 | 72% |
| 等權基準 | +15.6% | 0.97 | −17.2% | 0.9 | 67% |
| long-short | +2.2% / −1.6% | 0.23 / −0.15 | — | — | 44% |

→ **Ridge long top20% 全面優於基準**(風險調整後一致勝);**alpha 在 long 側選贏家、long-short 無效**(空方不可靠);幅度適度、未計交易成本。

---

## 六、總結論

1. **三鏡頭框架經實證**:不只理論,量×形×位是資料中真實正交結構;**形(八二)是最該開採的互補維度**。
2. **特徵集飽和**:34 特徵已榨乾 per-stock 鏡頭 alpha(A/B 淘汰、C 無肥);**質>量 達成**——每特徵皆過四道漏斗、各帶增量。
3. **經濟價值成立但適度**:IC→真 alpha(Ridge long Sharpe 1.21 vs 基準 0.97);edge 在選贏家、非放空。
4. **誠實**:本輪多數探索(相關撒網、A 交互、B 馬太)**淘汰收場**——漏斗正常運作、擋住偽 alpha;真增量僅來自結構正交的八二/康波鏡頭。

## 七、方法論教訓(可複用)

- **強單因子 ≠ 增量**(x_gini_resid HAC-t −6.29 卻零增量);多因子 + 多 seed 增量才算數。
- **顯式線性交互冗餘**:模型(尤 GBDT)自組/自學交互;真交互須非線性且勝 GBDT 自學——門檻高。
- **高相關 ≠ 可刪**:殘差各帶增量(位軸三尺度);去重須過漏斗驗,不憑相關逕刪。
- **rank-IC 對離群穩健**:winsorize 類 hygiene 對 rank 度量常無效(對點預測/經濟度量才可能相關)。
- **context 不可橫斷面驗**:breadth/regime 每 panel 同值→IC 恆 0;須另設 regime-conditional 評估。
- **一軸飽和→旋轉正交軸**:第一性(水位)飽和時,形/位 才有殘餘訊號。

## 八、前瞻

- **phase-2 軸需 infra(實證接地 2026-06-28)**:八二 P5 營收/產業 share(MonthRevenue+TaiwanStockInfo.industry **374/374**、需發布日 gate 次月10日)、康波 C3 基本面循環(FinancialStatements/BalanceSheet/CashFlows **374/374**、需發布日 gate 季底+45/90日)、C1 景氣(**表存在＝`TaiwanBusinessIndicator`** 單數、月頻 44 年 leading/coincident/lagging/notrend/monitoring——但 **macro 無 stock_id→非橫斷面特徵、改入 regime-conditional**)。**發布日 gate 為 phase-2 命門**(且修現有 monthly_revenue_yoy 洩漏)。
- **真交互(非線性)**:若再探跨鏡,須乘積/比值/條件型且證勝 GBDT 自學(門檻高、低優先)。

## 十、經濟層深化(2026-06-28、交易成本實證)

成本回測(`run_economic_eval` 加換手率+成本、`portfolio.py`):**alpha 扛得住真實成本**。

| Ridge long-only(扣 0.585% 來回)| 換手 | net Sharpe | net Calmar | net CAGR |
|---|---|---|---|---|
| **top10%/equal(最佳)** | 68% | **1.26** | **1.32** | **+19.5%** |
| top20%/equal(原預設) | 57% | 1.12 | 0.98 | +16.7% |
| 等權基準(淨) | 9% | 0.96 | 0.89 | +15.4% |

**結論**:(1) **扣成本後 net Sharpe 1.26 vs 基準 0.96、淨 CAGR +4.1pp** → 真可交易、非假兆;(2) **top10% 集中 > top20/30(淨值)**、**等權 ≈ 預測加權** → 優化配置 top10%/equal;(3) GBDT 淨 ~1.0 僅微勝基準 → **Ridge 為生產模型**。
**regime-conditional(2026-06-28、C1 景氣)**:先於 **23 年 TAIEX** 驗 regime 訊號擇時力(長樣本避 18 季過配)——`lead_nt_rising`(領先去趨勢 3 月動能)**強過**:CAGR +13.1%≈買持、**MaxDD −53.9%→−15.4%、Sharpe 0.75→1.04、Calmar 0.24→0.85**(發布日 lag 2 月)。套到 top10% 投組(18 季):**MaxDD −14.8%→−6.1%、Calmar 1.32→2.09**(正確避 2022)**但** CAGR +19.5%→+12.7%、Sharpe 1.26→1.10(多頭窗+在市44%、現金拖累)。**結論:regime 是風控工具非報酬增強、目標依賴**——回撤 mandate 採 regime、報酬 mandate 採 static;訊號 23 年驗過、此窗多頭低估其值。工具 `verify_regime_timing.py`/`verify_regime_portfolio.py`。
**待續**:容量/衝擊成本、risk-free 現金報酬、更長 live 窗複驗 regime。

## 九、產物清單

- **模組**:`features/concentration.py`、`features/phase.py`、`features/panel.py`、`evaluation/portfolio.py`(含成本/換手)、`evaluation/metrics.py:effective_t_hac`、`evaluation/baseline.py:robust`
- **工具**:`verify_lens_promotion/interaction/matthew/daytrade_candidates`、`verify_hygiene`、`run_lens_correlation`、`run_economic_eval`(含成本)、`build_field_lens_map`、`build_feature_panel --asof`
- **報告**(9):三鏡頭研究三部曲 + 綜合 + field_lens_map + lens_validation + lens_correlation_analysis + field_correlation + 本總報告
- **DB 表**:`feature_values`(34)、`field_lens_map`(342)
- **封存**:tag `feature-lens-pareto-cycle-20260627`、`treaty-v1.14.0`

## 九、產物清單

- **模組**:`features/concentration.py`、`features/phase.py`、`features/panel.py`、`evaluation/portfolio.py`、`evaluation/metrics.py:effective_t_hac`、`evaluation/baseline.py:robust`
- **工具**:`verify_lens_promotion`、`verify_interaction_candidates`、`verify_matthew_candidates`、`verify_hygiene`、`run_lens_correlation`、`run_economic_eval`、`build_field_lens_map`、`build_feature_panel --asof`
- **報告**(8):三鏡頭研究三部曲 + 綜合 + field_lens_map + lens_validation + lens_correlation_analysis + 本總報告
- **DB 表**:`feature_values`(34)、`field_lens_map`(342)
- **封存**:tag `feature-lens-pareto-cycle-20260627`

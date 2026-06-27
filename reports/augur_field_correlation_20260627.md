# augur 核心股 raw 欄位相關性分析 — 2026-06-27

> **範圍**：對 374 核心股（`core_universe`），把散在 ~12 張 raw 表的數值欄聚合成每股每日對齊面板（22 欄：價量/籌碼/估值/月營收），算欄位間相關係數（**Pearson + Spearman × level + change**）+ **lead-lag 可預測性**（X_t vs t+1 進場未來報酬）。
> **產物**：表 `field_correlation`（321,282 列）、`field_return_leadlag`（95,268 列）；模組 `src/augur/audit/field_correlation.py`；CLI `scripts/run_field_correlation.py`（`--report-only` 可重印）。
> **性質**：探索性（全史、非 as-of）；source-pure（缺即 NaN、pairwise 算、不補值）；**非生產特徵**——若用於特徵須另過 #8 anti-leakage / #11 五鏡漏斗。本地計算、零 Claude usage（#28）。

---

## A. 跨欄相關（contemporaneous、同日）

### A1. 機械式 trivial（同源衍生 → 印證共線冗餘 S7）
報告 top 對幾乎全是同源:`margin_balance~margin_usage`(+0.996,usage=balance/limit)、`close~price_to_10yr`(+0.994,=close/10yr)、`money~volume`(+0.986,=價×量)、`close~market_value`(+0.985,=價×股數)、估值群 `pbr/per/market_value/close` 互相 +0.9。**意義**:這些欄位對特徵=冗餘,五鏡共線群應群內擇一(對映審查 S7/G3)。

### A2. 非機械式、真正有資訊（change × spearman、374 股一致）
| 欄位對 | 中位 corr | 一致性 | 解讀 |
|---|---|---|---|
| **govbank_net ~ inst_net** | **−0.48** | 全負 100%、強 97% | **官股與三大法人逆向操作**(法人買→官股賣);最強非顯而易見行為訊號(官股逆勢/護盤) |
| foreign_holding ~ inst_net | +0.47 | 全正 100% | 外資持股變動與法人淨買同向(外資為法人一員) |
| inst_net ~ spread | +0.48 | 全正 99% | 法人淨買 ↔ 當日價漲(順勢/帶動) |
| range ~ volume / turnover | +0.50 | 全正 100% | 振幅 ↔ 量(經典量價/波動) |
| inst_net / foreign_holding ~ close | +0.30~0.32 | 89-94% | 籌碼流與價同向 |
| govbank_net ~ spread | −0.35 | 全負 86% | 官股逆勢(跌買漲賣) |

---

## B. lead-lag（predictive：X_t vs t+1 進場未來報酬，#8 安全）→ alpha 候選

> 這才是「可預測」方向(predictor 用 ≤t、報酬用 t+1 起,無洩漏)。**注意**:此為**每股時間序列**相關(該股 X 是否預測該股自身未來報酬),非 augur 生產用的**橫斷面 rank IC**;但跨股 sign 一致性高即代表該效應普遍、為 cross-sectional 特徵之強候選。

### B1. change basis（日變化預測）— 弱
全特徵 |中位 corr| ≈ 0.01-0.02、有訊號率低 → **籌碼/價的日變化幾乎不預測未來報酬**(符合效率市場;daily change 無 alpha)。

### B2. level basis × H=20 — **真實預測結構（價值/均值回歸/規模）**
| 預測欄位(水位) | 中位 corr | 負向一致 | 有訊號率(|c|≥.03) | 解讀 |
|---|---|---|---|---|
| **pbr** | **−0.116** | **97%** | **93%** | **最強**:高 PBR → 未來報酬偏低(價值效應),374 股 97% 同號 |
| market_value | −0.092 | 89% | 85% | 小型股效應(市值小→未來報酬高) |
| price_to_10yr | −0.073 | 83% | 78% | 均值回歸(相對 10 年線高→未來偏低) |
| margin_balance / usage | −0.067 / −0.063 | ~80% | ~78% | 高融資槓桿 → 未來報酬偏低 |
| per | −0.052 | 79% | 73% | 價值效應 |
| close | −0.049 | 82% | 71% | 高價 → 均值回歸偏低 |
| dividend_yield | **+0.044** | 76% 正 | 71% | 高殖利率 → 未來報酬偏高(價值/收益) |

**核心發現**:**估值「水位」是最一致的可預測 raw 欄位**——PBR / PER / 市值 / price_to_10yr / 殖利率 / 融資槓桿,全是經典**價值 + 均值回歸 + 規模**效應,跨 374 股 76-97% 同號。這**直接呼應**方法論 M1 之 alpha 主源(估值缺口 + 循環位置),並驗證現有 `pe_ratio`/`pb_ratio`/`price_to_10yr` 特徵為真候選。

---

## 結論與特徵意涵

1. **冗餘**:價/市值/估值/量價多為機械共線(A1)→ 特徵去重依據(五鏡共線群)。
2. **可行動的新行為訊號**:`govbank_net` 與 `inst_net` 強逆相關(−0.48、100% 股)——「官股 vs 三大法人背離」是值得做的**交互特徵候選**(同日;若要預測須驗 lead-lag)。
3. **最強可預測 raw 欄位 = 估值水位**(B2):PBR level −0.116(97% 一致)領先——確認估值類為 alpha 主源、支持現有估值特徵。
4. **日變化不預測**(B1):籌碼/價日變化 lead-lag ≈ 0 → 短期 change 類特徵須謹慎。

## Caveat（誠實 #15）
- **每股時間序列 ≠ 橫斷面**:B 部為單股 TS 相關;augur alpha 是 cross-sectional rank。一致性高=效應普遍、支持橫斷面特徵,但須用 `feature_diagnostics` 五鏡之**橫斷面 rank IC** 正式驗(本表是底料、非結論)。
- **探索性、非 as-of**:全史相關;入特徵前須過 #8(發布日/t+1)+ #11(五鏡)+ purged walk-forward。
- **同日 ≠ 可交易**:A 部 contemporaneous(法人買↔價漲是同步),非 alpha。
- 殘留:`pe_ratio` 極端值未 winsorize(C1,獨立議題)。

## C. 候選五鏡橫斷面 IC 驗證（2026-06-27 續）

把兩潛力依方法論母原則③做成正式候選（`audit/feature_candidate.py`），對 374 核心跑橫斷面 rank IC（五鏡①⑤）+ 共線（②）：

| 候選 | H60 IC / Eff-t / 勝率 | 判定 |
|---|---|---|
| `pb_ratio`（raw 基準） | −0.045 / −1.71 / 0.41 | 弱、不顯著 |
| `pb_xsec_rank`（橫斷面 rank） | −0.045 / −1.71 | ❌ **與 raw 逐位元相同**（rank IC 對單調變換不變）|
| `pb_industry_demean`（產業 demean） | −0.034 / −1.86 | ❌ 未強化 + 與 raw 共線 0.966 |
| **`pb_self_pctile_252d`（自身 252d 百分位）** | **+0.054 / 2.40 / 0.70** | ✅ **PASS**：符號翻正、顯著、低共線=估值再評價動能（新訊號）|
| **`inst_govbank_divergence`（背離）** | **+0.044 / 2.53 / 0.72**（n=18） | ✅ **PASS**：顯著、與估值低共線=新增量（govbank 2021-07+、樣本少）|

**三結論**：(1) **橫斷面 rank「相對化」對單因子 IC 零增益**（rank-invariance，實證 S20/G20——只助多因子）;(2) 真強化=**自身歷史百分位**（valuation momentum、與 raw 橫斷面 value 正交）;(3) **govbank×inst 背離為真新增量**。

**Caveat**：Eff-t 未去相關（G8、顯著性上界）、pan-hist 非 as-of、單 seed、背離 n=18;**屬初步通過、非定論**——須 as-of + 去相關 Eff-t + ≥3 seed 複核才提拔生產（未過完整漏斗不入生產）。五鏡 ③LOO/④SHAP 未跑。實驗候選列驗後已 `--clear`、未留 feature_values。

## D. 提拔複核判決（2026-06-27、as-of + 去相關 Eff-t + 多 seed）→ **兩候選皆淘汰**

對 §C 初步通過之 2 候選做提拔前完整漏斗複核(`scripts/verify_candidate_promotion.py`):as-of 口徑(消完整度 look-ahead)+ Newey-West HAC Eff-t(去相關、解 G8)+ 3 seed 多因子增量。

**1. as-of 單因子 IC + iid vs HAC Eff-t**
| 候選 | H60 as-of IC | iid-t | HAC-t | 判定 |
|---|---|---|---|---|
| `pb_self_pctile_252d` | +0.052 | 2.40 | **2.31** | 單獨顯著(去相關後仍 ≥2)|
| `inst_govbank_divergence` | +0.032 | 1.80 | **1.67** | ❌ 不顯著(pan-hist 2.53 → as-of 1.80、n=18)|

→ HAC 幾乎不削 t（自相關對這兩者影響小、G8 非主因）;**殺手是 as-of**（divergence 之 pan-hist 顯著是完整度 look-ahead 撐高）。

**2. 多 seed（3）增量:`pb_self_pctile_252d` 加入 26-feat 生產集**
| H | 模型 | 基準 | +候選 | Δ |
|---|---|---|---|---|
| 60 | Ridge | +0.1326 | +0.1278 | **−0.0048** |
| 60 | GBDT | +0.0997 | +0.1029 | +0.0033 |
| 20 | Ridge | +0.1122 | +0.1095 | −0.0027 |
| 20 | GBDT | +0.1046 | +0.1035 | −0.0011 |
→ 4 中 3 負、1 微正 → **對多因子零增量**、訊號已被現有 26 特徵涵蓋(冗餘)。

**判決(淘汰、#15 記錄)**:
- `pb_self_pctile_252d`:單獨顯著但**ablation-safe（多因子 Δ≤0）→ 依 #11「不顯影且 ablation-safe 必移」不提拔**。
- `inst_govbank_divergence`:**as-of+HAC 不顯著、n=18 太少 → 不提拔**。
- **教訓**:兩候選在寬鬆篩(pan-hist/單因子/iid)看似有潛力,過完整漏斗(as-of+去相關+多因子增量)後雙雙淘汰——驗證審查 S3/S6/G8(寬鬆口徑高估)。**目前 27 特徵已足,這兩個不加。** 漏斗工具(`effective_t_hac`、`verify_candidate_promotion.py`)留作日後候選之標準關卡。

## E. 擴充欄位探索（2026-06-27、欄位集 22→28 重跑）→ 無強新 alpha

加入 6 個未探索 raw 欄位值（短券側/外資空間/散戶集中度/借券）重跑全 374（cross-field 485,782 + lead-lag 116,484 列）:`short_sale_balance`(融券餘額)、`short_margin_ratio`(券資比)、`foreign_room`(外資可加碼空間)、`retail_pct`(散戶比 1-999)、`holder_count`(股東人數)、`lending_volume`(借券量)。

**lead-lag 可預測性(新欄位、X_t vs 未來報酬)**
| 新欄位 | H20 level IC | 一致性 | 解讀 |
|---|---|---|---|
| `retail_pct`(散戶比) | −0.024 | 61% 負、74% 訊號 | 散戶比高→未來弱(反向指標)——唯一可解釋新訊號,**但弱** |
| `short_sale_balance` | −0.027 | 70% 負 | 偏 size 效應 |
| `foreign_room` | +0.024 | 67% 正 | =foreign_holding 機械反向(−0.989、無新資訊) |
| `short_margin_ratio`/`holder_count` | ±0.016~0.018 | 弱 | 弱 |
| 全 change basis | ≈0 | — | 日變化仍不預測(與 B1 一致) |

**結論(誠實 #15)**:6 新欄位全部 |IC|≤0.027——**比既有估值訊號弱 5 倍**(pb level −0.116);`foreign_room` 機械冗餘、短券偏 size、`retail_pct` 弱反向。**無強新 alpha**。cross-field 亦多機械(`foreign_holding~foreign_room −0.989`、`short_margin~short_sale +0.852`)。
> ⚠️ **越撒網 = 多重檢定假陽性升(審查 S5)**:`retail_pct` 以前例(pb_self_pctile 0.052 都因冗餘淘汰)判,幾乎必過不了第 4 道提拔關卡。**真價值在過濾關卡(§D)、非無限探索**——停止撒網,回方法論主線。

## 可追溯
- 模組 `audit/field_correlation.py`(28 欄)、`audit/feature_candidate.py`；CLI `run_field_correlation.py`、`validate_feature_candidates.py`、`verify_candidate_promotion.py`；去相關 helper `evaluation/metrics.py:effective_t_hac`;表 `field_correlation`(485,782)/`field_return_leadlag`(116,484)、各 374 股。重印:`run_field_correlation.py --report-only`。

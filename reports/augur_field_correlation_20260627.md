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

## 可追溯
- 模組 `src/augur/audit/field_correlation.py`、CLI `scripts/run_field_correlation.py`；表 `field_correlation` / `field_return_leadlag`（各 374 股）。重印:`python scripts/run_field_correlation.py --report-only`。

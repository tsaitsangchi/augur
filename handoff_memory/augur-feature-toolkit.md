---
name: augur-feature-toolkit
description: 特徵發現標準工具鏈 + 流程 — 探索→候選→四道漏斗→經濟驗證之各階段工具與用法(未來特徵發現一律走這套)
metadata: 
  node_type: memory
  type: reference
  originSessionId: b6b65aa3-b9fc-49cb-b589-2fff5a7b85de
---

augur 特徵發現**標準流程 + 工具鏈**(2026-06-27 戰役建立、可重用)。未來任何特徵發現一律走此關卡,**勿繞道、勿憑相關逕入生產**。流程 SSOT＝`reports/augur_feature_discovery_methodology_20260626` §四(四道漏斗);總戰役紀錄＝`reports/augur_three_lens_campaign_summary_20260627`。

**標準管線(發散→收斂、各階段工具)**:
1. **相關探索(底料、非結論)**:`scripts/run_field_correlation.py`(raw 欄位兩兩相關 + lead-lag)、`scripts/run_lens_correlation.py`(量×形×位三軸正交性 + 跨鏡結構)。欄位三鏡頭潛力查 `field_lens_map` 表 / `scripts/build_field_lens_map.py`。
2. **候選生成**:`src/augur/audit/feature_candidate.py`(相對化候選)、`features/concentration.py`(八二集中)、`features/phase.py`(康波相位)。as-of 安全、experimental 寫 feature_values(x_ 前綴或候選名)。
3. **漏斗1 紀律閘**:#1 source-pure / #8 anti-leakage / #9 不硬編。
4. **漏斗2 五鏡**:`scripts/run_feature_audit.py --asof --loo`(`audit/feature_diagnostics.py:five_mirror`:①IC ②共線 ③LOO ④SHAP ⑤purged)。
5. **漏斗3 walk-forward**:`evaluation/baseline.py:run_ladder`(purged、as-of)。
6. **漏斗4 提拔關卡(入生產前強制)**:`scripts/verify_candidate_promotion.py`(通用)、`verify_lens_promotion.py`(鏡頭集)、`verify_interaction_candidates.py`(交互)、`verify_matthew_candidates.py`(rank 動態)——皆 = as-of 口徑 + **去相關 HAC Eff-t**(`metrics.effective_t_hac`、**禁裸 iid**)+ 多 seed 多因子增量。驗後 `--clear` 清實驗列。
7. **經濟驗證(#14 真度量、F3)**:`scripts/run_economic_eval.py`(`evaluation/portfolio.py`:模型預測→投組→CAGR/Sharpe/MaxDD/Calmar vs 等權基準)。
8. **衛生/精瘦**:`scripts/verify_hygiene.py`(標準化器 / 去冗餘測;`baseline.run_ladder(robust=True)` 用 RobustScaler)。

**鐵律教訓(屢驗、寫在心上)**:
- **crude 掃描高 t 是 non-as-of 假象**(2026-06-28:`run_raw_interaction_ic.py` 浮現 money×inst_net IC +0.030/t=3.6;但 as-of point-in-time 宇宙下 IC 崩到 +0.002/HAC-t 0.17〔crude 用含完整度 look-ahead 全宇宙灌水〕)→ **crude 掃描必 as-of+HAC 才算數**。改進工具 `run_deep_interaction_scan.py`(as-of 從頭、18 正規化欄位、多 horizon、直接 HAC-t)。
- **⚠️ 增量測覆蓋假象(2026-06-28、重要)**:`baseline._panel_matrix` 剔除「缺任一特徵」之股 → 加**稀疏候選**(籌碼類覆蓋~63%)時缺值股被踢出 → +候選宇宙縮 37% → **Δ 假性大負(與候選內容無關)**;`verify_signal_promotion.py` 三南轅北轍候選 Δ 全 −0.03~−0.045 一致即鐵證。**修法 `verify_incremental_fair.py`:候選缺值補 panel 中位→同宇宙比**。修後 Δ 由 −0.04 翻成 ~0~小正(GBDT-H20 +0.002~+0.0065、Ridge≈0=線性冗餘)。鐵律:**稀疏候選增量必同宇宙測(impute/restrict),否則冤殺;歷史稀疏籌碼淘汰待公平測重檢**。foreign_trust_div(外資×投信背離)4格全非負、H20 GBDT +0.0065=多輪探索最接近真增量者→**但經濟價值測(`verify_economic_candidate.py`#14)淘汰**:net ΔSharpe 4格3負、**Calmar/MaxDD 4格全惡化**(IC 鬚毛沒變經濟價值、反害回撤)。教科書「IC 撐住≠可交易、成功定義是經濟價值非 IC」。三候選全淘汰、飽和仍立。
- **強單因子 ≠ 增量**(x_gini_resid HAC-t −6.29 卻零增量)→ 必看多因子多 seed 增量。
- **顯式線性交互冗餘**(成分已在模型、Ridge 自組/GBDT 自學)→ 真交互須非線性且勝 GBDT 自學。
- **高相關 ≠ 可刪**(殘差各帶增量)→ 去重須過漏斗驗。
- **rank-IC 對離群穩健** → winsorize 類 hygiene 對 rank 度量常無效。
- **context(breadth/regime/macro)橫斷面 IC 恆 0、不可用此漏斗驗** → 須另設 regime-conditional 評估。
- **市場(漏斗)裁決、非「我覺得對」**;多數探索淘汰收場屬正常(擋偽 alpha)。

**判準魔數口徑(2026-07-03 補、各 verify script 共用)**:IC 增量閾 ±0.002、經濟 ΔSharpe 閾 +0.05、MaxDD 容差 +0.005、HAC-t 閾 2(提拔)/2.5(掃描)、交互須 >成分 max×1.3、來回成本 0.00585、seed 起點 42 ≥3 顆、橫斷面最少 30 股、非重疊間隔 h×1.45×0.9。**穩健終關**(headline 亮眼≠穩健):`verify_stability.py`=逐期 Δ t-stat+LOO 最壞+前後子期同向+分位一致,才 productionize(H120 Calmar +0.62 拆出部分噪音之實證)。**已淘汰名錄(勿重測)**:foreign_trust_div(#14 敗)、dealer_net_r、foreign_pct_x_turnover、money_x_inst_net、當沖 2、馬太 rank 2、跨鏡交互 3(x_gini_resid_size 等);PRUNE 測試名單≠生產狀態(gov_bank_net_buy_60d 仍在生產、僅 volatility_20d 真剪)。**工程陷阱**:reexam/economic_reexam/stability 以 importlib 動態載入 verify_daytrade/verify_fundamental 的 `_compute`/`CANDS` 且 ROOT 硬編 scripts/ 絕對路徑——改簽名或搬家連鎖斷三支;實驗候選一律 `x_` 前綴+驗後 DELETE,全 panel 覆蓋候選會自動混入 canonical(base 須顯式排除防污染)。

關聯:[[augur-three-lens-research]](三鏡頭思想)、[[augur-feature-values]](35 特徵現況+飽和)、[[augur-project-map]]。

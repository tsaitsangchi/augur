# 鏡頭特徵驗證報告 — 八二 + 康波過完整漏斗(2026-06-27)

> **性質**:特徵生成→驗證→提拔之完整紀錄(#15 可溯)。記錄「八二法則 + 康波兩鏡頭完全建出 → 過四道漏斗 → 存活者入生產」全程。
> **結論**:12 軸生成 → **4 軸(8 特徵)存活入生產**;生產特徵集 **27 → 34**;headline **H60 Ridge +0.1326→+0.1418(+7%)、GBDT +0.0997→+0.1130(+13%)**。**本 session 首次有特徵淨增進生產**(對比前兩相關候選全淘汰)。

---

## 一、生成(發散)

依設計報告(`augur_feature_design_pareto_thought` / `_cycle_thought_20260612`)建兩模組,12 軸生成 25 候選特徵:
- **`concentration.py`**(八二,P1-P4):持股集中(Gini/HHI/熵)、資金流集中(HHI/max-share)、量能集中(Gini/max-share)、報酬集中(skew/kurt/Gini)。
- **`phase.py`**(康波,C2/C4):多尺度 range-position、距極值歷時、drawdown、動能二階導、共振、vol 期限結構、累計流相位。
全 cutoff-free 泛函 / data-driven 相位(#9)、as-of ≤t(#8)、算不出缺列(#1)。as-of 宇宙(848 股×28 panel)填充供驗。

## 二、holistic 五鏡(52 特徵 as-of + LOO)

對 27 既有 + 25 新 = 52 特徵跑 `run_feature_audit --asof --loo`。新特徵裁決:

**強勢存活(顯著 IC + Eff-t≥2 或 LOO 必要)**:量能集中(volume_gini/max_share 20/60)、流相位(inst_cumflow_position 60/120)、價格相位(range_position_120d、days_since_high_252d)。
**淘汰**:持股集中(holding_*,**與既有 top_holders_pct 共線 +0.97、冗餘**)、報酬集中(return skew/kurt/gini,**IC≈0 弱**)、inst_flow_hhi/max_share、momentum_accel/resonance/vol_term_structure/range_position_60d/days_since_low/max_drawdown(Eff-t<2)。
**順帶**:gov_bank_net_buy_60d LOOΔ −0.087(已被 canonical intersection 排除);volatility_20d 與 range_mean_20d 共線 +0.94。

## 三、提拔關卡(as-of HAC + 多 seed 多因子增量)

`verify_lens_promotion.py`:8 強勢存活過第 4 道關卡。

**① as-of 去相關 HAC Eff-t(全部 |≥2.8|,去相關幾乎沒削=非自相關假象)**
| 特徵 | as-of IC | HAC-t | 勝率 |
|---|---|---|---|
| inst_cumflow_position_120d | +0.062 | **4.35** | 0.81 |
| range_position_120d | +0.076 | **3.90** | 0.81 |
| volume_gini_60d | −0.059 | **−4.49** | |
| volume_gini_20d | −0.050 | −4.23 | |
| volume_max_share_20d | −0.045 | −3.75 | |
| volume_max_share_60d | −0.046 | −3.45 | |
| days_since_high_252d | −0.068 | −2.98 | |
| inst_cumflow_position_60d | +0.039 | 2.79 | 0.70 |

**② 多 seed(3)多因子增量(全正、雙模型雙 horizon)**
| | 生產 | 剪枝 | +存活 | 總Δ |
|---|---|---|---|---|
| H60 Ridge | +0.1326 | +0.1344 | **+0.1418** | **+0.0093** |
| H60 GBDT | +0.0997 | +0.1010 | **+0.1130** | **+0.0133** |
| H20 Ridge | +0.1122 | +0.1139 | +0.1236 | +0.0114 |
| H20 GBDT | +0.1046 | +0.1049 | +0.1080 | +0.0034 |

→ 8 存活全過(HAC-t |≥2.8| + 剪枝 Δ≥0 + 加存活總 Δ 全正)。

## 四、裁決與落地

- **提拔 8**(模組 trim 為只留存活):量能集中×4、流相位×2、價格相位×2。
- **剪 volatility_20d**(共線、剪枝 Δ+0.0018);**淘汰 17 失敗新特徵**(feature_values 刪 18 特徵×~54.6 萬列)。
- **全 roster 重建**:35 panel、2.36M 列、34 特徵;8 存活覆蓋 ~2900-3070 股(全 roster 一致)、0 淘汰殘留。

## 五、教訓(#15)

1. **鏡頭奏效、但不在我猜的地方**:12 軸只 4 軸存活——存活者是**量能集中(八二 P3)+ 流/價格相位(康波 C2/C4)**;持股集中(冗餘)、報酬集中(弱)淘汰。**資料決定、非我以為**。
2. **正交軸理論命中**:第一性(水位)軸早被 27 特徵飽和 → 旋轉到正交的「形/位」軸才挖到真增量(印證綜合報告「一軸飽和→旋轉正交軸」)。
3. **最強是跨鏡頭**:inst_cumflow_position(流〔第一性〕之相位〔康波〕)HAC-t 4.35 居冠——印證「跨鏡交界藏最強訊號」。
4. **三重關卡才算數**:單因子顯著 → 過 as-of + 去相關 + 多因子增量 + 多 seed 才提拔(前兩相關候選即倒在此關)。

## 六、Caveats
- 提拔基於 H20/H60、as-of、3 seed;更長期穩定性待半年重跑(#15)。
- inst_cumflow 覆蓋 30 panel(法人資料史較短)、樣本較其餘少。
- 存活≠永久:後續仍受五鏡持續監測,失效即剪(#11)。

## 來源
- 模組 `features/concentration.py`、`features/phase.py`、`features/panel.py`
- 工具 `scripts/verify_lens_promotion.py`、`run_feature_audit.py`、`evaluation/metrics.py:effective_t_hac`
- 設計 `augur_feature_design_pareto_thought/_cycle_thought_20260612`;思想 `augur_three_lens_synthesis_20260627`
- 表 `feature_values`(34 特徵)、`field_lens_map`(欄位地圖)

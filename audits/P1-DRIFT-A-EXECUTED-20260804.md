# P1-DRIFT A（rename-align）執行帳 · 2026-08-04

> **位階**：[I] 執行留痕（非 META [N]）。  
> **授權**：`P1-DRIFT: A`（rename-align）。**非** B（canonical-arm）、**非** C（完整 retrain-asof 多 horizon／經濟終關）。  
> **呈案**：`reports/augur_p1_feature_drift_plan_20260804.md` §2 A。  
> **前失敗錨**：`audits/OPT-R3-W2PREP-S1P1-20260804.md`。

---

## 1. 漂移事實（執行前複現）

| 項 | 值 |
|---|---|
| 指令 | `python scripts/predict_asof.py --run --dry-run` |
| 結果 | **拒載中止（誠實）** |
| stderr／stdout 要旨 | `特徵漂移 (feature_source=prodset): frozen=['inst_cumflow_position_120d', 'lending_fee_rate_mean_20d'] vs current=['cycle_position_252d', 'inst_cumflow_position_120d', 'lending_fee_rate_mean_30d']` |
| 舊 serve 模型 | `RankRidge_H60_2026-05-31_seed42_9a88039981b5a128`（prodset、n_feats=2） |
| 現行 active | `cycle_position_252d` · `inst_cumflow_position_120d` · `lending_fee_rate_mean_30d` |

根因：artifact 凍結集仍為 demote 前之 `mean_20d` 雙顆；現行 active 已換 `mean_30d` 並多 `cycle_position_252d`。

---

## 2. A 機制選擇

計畫 A＝「以現行 active 三顆為準，**重產或換掛** prodset 口徑 predict artifact（凍結 feats＝current）」。

| 路徑 | 結果 |
|---|---|
| **換掛** | `models_artifacts/RankRidge_H60_*.joblib` 無任一檔 feats＝現行 active 三顆 → **不可換掛** |
| **重產** | `python scripts/train_ranker.py --run`（預設 prodset／RankRidge／H=60／seed=42／asof=最新庫內） |

未做：canonical 臂、手改 panel、手改舊 joblib 特徵名卻謊稱同源、FinMind／FRED、寫 `prediction_values`、多 horizon／經濟終關（屬 C 完整版）。

---

## 3. 重產產物

| 項 | 值 |
|---|---|
| model_id | `RankRidge_H60_2026-06-30_seed42_56d03625463b3eba` |
| feature_source | `prodset` |
| frozen feats | `cycle_position_252d` · `inst_cumflow_position_120d` · `lending_fee_rate_mean_30d` |
| n_feats／n_train_rows／panels | 3／42255／113（`[2007-12-31..2026-06-30]`） |
| artifact | `models_artifacts/RankRidge_H60_2026-06-30_seed42_56d03625463b3eba.joblib` |
| train rc | **0** |

---

## 4. 驗收 dry-run（同失敗路徑）

| 項 | 值 |
|---|---|
| 指令 | `python scripts/predict_asof.py --run --dry-run` |
| 結果 | **通過（不再漂移拒載）** |
| 要旨 | `✓ as-of 2026-06-30 預測 model=RankRidge_H60_2026-06-30_seed42_56d03625463b3eba feature_source=prodset n_feats=3 (dry-run 未寫庫)` |
| frozen_feats | `['cycle_position_252d', 'inst_cumflow_position_120d', 'lending_fee_rate_mean_30d']` |
| frozen＝current active | **是**（親查 equal） |
| 寫庫 | **否**（`--dry-run`） |
| 可交易／確立級 | **未宣稱** |

---

## 5. 殘餘／不做

| 項 | 狀態 |
|---|---|
| H≠60 其他 horizon 之 prodset artifact | **未**重產（僅預設 H60；完整多 horizon＝C 射程） |
| 經濟終關／IC 提拔重跑 | **未做** |
| `--apply`／寫 `prediction_values` | **未做** |
| B canonical 研究臂 | **未做**（授權僅 A） |

A 驗收（prodset hotpath dry-run 不再因漂移拒載）**已綠**；殘餘為完整 C 才覆蓋之廣度，非本輪 dry-run 擋點。

---

*完。*

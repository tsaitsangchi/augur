# N1-RETRAIN CLOSED — 庫內 prodset train／predict [I]（2026-07-29）

> **性質**：[I] 執行收口；不創設 [N]。  
> **拍板**：`n1-retrain` + `FZ-keep`（`audits/SIX-TRACK-WAVE-APPROVED-20260729.md`）  
> **硬邊界**：零 FinMind／FRED；`--skip-sync`／庫內 as-of；predict ⊥ API；**≠可交易／≠確立級／≠ direction_gate pass**（本輪未跑 `evaluate_direction_gate`）。  
> **簽名誠實**：決策者＝hugo；本檔由 agent 繕寫登錄。

---

## 結果（一句）

**庫內 P2H 熱路徑 `train_ranker`＋`predict_asof --dry-run` 皆綠（as-of `2026-05-31`）；feature_source=prodset；零市場 API。拍板預期 active n=1（`inst_cumflow_position_120d`），執行當下 live active＝n=2（同日另有 `lending_fee_rate_mean_20d` promote）——本輪**未** demote／未改 prodset，熱路徑依契約訓當下 active∩覆蓋。**仍非可交易／非方向門通過。**

---

## 1. Prodset 確認（真兆）

| 項 | 結果 |
|---|---|
| 表 | `evolution_production_feature_set` |
| 拍板預期 | active **n=1**：`inst_cumflow_position_120d` |
| **執行當下 live** | active **n=2**：`inst_cumflow_position_120d`、`lending_fee_rate_mean_20d` |
| `lending_fee_rate_mean_20d` | registered_at≈2026-07-29 13:07（source_run_id=10；apply_log_id=24）——晚於拍板「n=1」敘述 |
| resolve（≤as-of panels） | n_feats=2；feats＝上列二者 ⊆ active |
| 本輪是否改 active | **否**（唯讀消費；禁擅自 demote） |
| max as-of（`core_universe_asof`） | **2026-05-31** |
| max panel（feature_values） | 2026-06-30 |
| PriceAdj max | 2026-07-28（本輪**未**用為 train as-of；FZ-keep 不解凍 sync） |

覆蓋列數（`feature_values`，stdout／DB query）：

| feature | count | min panel | max panel |
|---|---|---|---|
| `inst_cumflow_position_120d` | 122160 | 2012-12-31 | 2026-06-30 |
| `lending_fee_rate_mean_20d` | 17072 | 2021-03-31 | 2026-06-30 |

---

## 2. 指令矩陣（實跑）

```bash
# 哨兵（零 API）
./venv/bin/python scripts/verify_prodset_hotpath.py --check
# → EXIT=0；active n=2；resolve n_feats=2

# 庫內 train（預設 --feature-source=prodset；無 FinMind／FRED）
./venv/bin/python scripts/train_ranker.py --run --asof 2026-05-31
# → EXIT=0

# 庫內 predict dry-run（不寫 prediction_values）
./venv/bin/python scripts/predict_asof.py --run --dry-run --asof 2026-05-31
# → EXIT=0
```

| 步 | 指令 | exit | log |
|---|---|---|---|
| 1 | 唯讀 prodset + `resolve_prodset_feats` | 0 | （本機 session） |
| 2 | `verify_prodset_hotpath.py --check` | 0 | `/tmp/augur_logs/n1_retrain_verify_20260729_131703.log` |
| 3 | `train_ranker.py --run --asof 2026-05-31` | 0 | `/tmp/augur_logs/n1_retrain_train_20260729.log` |
| 4 | `predict_asof.py --run --dry-run --asof 2026-05-31` | 0 | `/tmp/augur_logs/n1_retrain_predict_20260729.log` |
| 5 | `run_evaluation`／`run_economic_eval`／`evaluate_direction_gate` | **SKIP** | 見 §4 |

**未跑**：任何 `sync_finmind*`／`sync_macro`／`daily_maintenance`／FinMind／FRED fetch；arena `--run` 全鏈（含 API 門）；PME S4。

---

## 3. Metrics（僅 stdout／registry；零臆造）

### train

```
✓ 訓練完成 model_id=RankRidge_H60_2026-05-31_seed42_9a88039981b5a128
  feature_source=prodset train_rows=8080 n_feats=2
  feats=['inst_cumflow_position_120d', 'lending_fee_rate_mean_20d']
  panels=68([2007-12-31..2026-05-31])
  artifact=.../models_artifacts/RankRidge_H60_2026-05-31_seed42_9a88039981b5a128.joblib
```

| 鍵 | 值（真兆） |
|---|---|
| model_id | `RankRidge_H60_2026-05-31_seed42_9a88039981b5a128` |
| feature_source | prodset |
| n_feats | **2** |
| feats | `inst_cumflow_position_120d`、`lending_fee_rate_mean_20d` |
| train_rows | **8080** |
| n_panels | **68**（[2007-12-31..2026-05-31]） |
| asof_snapshot | 2026-05-31 |
| feats_hash | `9a88039981b5a128` |
| seed | 42 |
| family／horizon | RankRidge／60 |
| git_sha（registry） | `1ec2438c55f18671fbf22a106aafe92dc66f2cb0` |

對照舊 n=2（cumflow＋`volume_gini_60d`）artifact `…1420b777665a099f`：feats 已換 → **新 model_id／新 hash**（預期）。

### predict（dry-run）

```
✓ as-of 2026-05-31 預測 model=RankRidge_H60_2026-05-31_seed42_9a88039981b5a128
  feature_source=prodset n_feats=2 (dry-run 未寫庫)
  frozen_feats=['inst_cumflow_position_120d', 'lending_fee_rate_mean_20d']
── long 投組建議 top10%/equal(34 檔;系統建議、人決策、不下單;≠可交易)──
```

| 鍵 | 值 |
|---|---|
| as-of | 2026-05-31 |
| drift | 通過（frozen＝current resolve） |
| 寫庫 | **否**（`--dry-run`） |
| long 建議檔數 | **34**（top10% equal；**建議≠下單**） |

---

## 4. 明示邊界（必讀）

| 宣稱 | 本輪 |
|---|---|
| **可交易** | **否** — 未主張；dry-run 未寫庫 |
| **確立級** | **否** |
| **direction_gate pass** | **否** — 本輪**未**執行 `evaluate_direction_gate`；庫內亦無 `direction_gate_evaluation`／`direction_gate_run` 表可讀「本輪通過」 |
| **解凍 FinMind／FRED** | **否**（FZ-keep） |
| **PME S4** | **未開** |
| GATE 閾值 | **未改** |
| commit／push | **未做** |

### Econ／回測 SKIP（同 DB-PREDICT-N2 先例）

| 候選 | 為何 SKIP |
|---|---|
| `scripts/run_evaluation.py` | ladder／canonical 口味；非 prodset RankRidge 熱路徑最小單位 |
| `scripts/run_economic_eval.py` | 同上；無單 as-of prodset dry 最小入口 |
| `scripts/evaluate_direction_gate.py` | **未授權本輪**；不得假綠 |

**不硬造** Sharpe／IC／hit-rate；本輪無確立級／deflation 數字可報。

---

## 5. 與拍板「n=1」敘述對帳

| | |
|---|---|
| 拍板碼文案 | `n1-retrain`＝prodset active n=1（`inst_cumflow_position_120d`）庫內 train／predict |
| 執行事實 | live active 已因並行／同日 promote 成 **n=2**（含 `lending_fee_rate_mean_20d`） |
| 處理 | 熱路徑契約＝訓 **active∩覆蓋**；若硬鎖 n=1 會與 predict 漂移拒載衝突，且擅自 demote 越權 |
| 誠實句 | 軌名仍 `n1-retrain`；**交付＝當下 prodset 熱路徑重訓**（含拍板指名之 cumflow＋已 active 之 lending_fee）；**不**把 n_feats=2 說成「拍板時就是 n=1」 |

---

## 6. Artifacts／logs

| 路徑 | 說明 |
|---|---|
| `audits/N1-RETRAIN-CLOSED-20260729.md` | 本檔 |
| `/tmp/augur_logs/n1_retrain_verify_20260729_131703.log` | 哨兵 |
| `/tmp/augur_logs/n1_retrain_train_20260729.log` | train stdout |
| `/tmp/augur_logs/n1_retrain_predict_20260729.log` | predict dry-run stdout |
| `models_artifacts/RankRidge_H60_2026-05-31_seed42_9a88039981b5a128.joblib` | artifact |
| `model_registry` 列 | 同上 model_id |

---

## 7. 建議下一句（非自動執行）

* 若須嚴格「僅 cumflow n=1」重訓 → Steward **明示** demote／freeze `lending_fee_rate_mean_20d` 後再跑同矩陣（本輪未做）。  
* 經濟／方向門 → **另令**；本 CLOSED **不解凍、不假綠方向門**。

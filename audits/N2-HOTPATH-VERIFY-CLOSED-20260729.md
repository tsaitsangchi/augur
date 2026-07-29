# N2-HOTPATH-VERIFY CLOSED — active n=2 熱路徑核對 [I]（2026-07-29）

> **性質**：[I] 執行收口；不創設 [N]。  
> **拍板**：`n2-hotpath-verify` + `FZ-keep`（`audits/WAVE2-SIX-TRACK-APPROVED-20260729.md`）  
> **前置**：`audits/N1-RETRAIN-CLOSED-20260729.md`（已訓 `RankRidge_H60_2026-05-31_seed42_9a88039981b5a128`）  
> **硬邊界**：零 FinMind／FRED；庫內 as-of；predict ⊥ API；**≠可交易／≠確立級／≠ direction_gate pass**（本輪**未**跑 `evaluate_direction_gate`；預設 SKIP）。  
> **簽名誠實**：決策者＝hugo；本檔由 agent 繕寫登錄。

---

## 結果（一句）

**Live prodset active＝n=2（`inst_cumflow_position_120d`＋`lending_fee_rate_mean_20d`）；`verify_prodset_hotpath --check`／`--selftest` 皆綠；registry／artifact 與 n1-retrain 模型對齊；`predict_asof --dry-run --asof 2026-05-31` 漂移通過、未寫庫。仍非可交易／非方向門通過；FZ-keep；未開 PME S4。**

---

## 1. Prodset active（真兆）

| 項 | 結果 |
|---|---|
| 表 | `evolution_production_feature_set` |
| active **n** | **2** |
| feats | `inst_cumflow_position_120d`、`lending_fee_rate_mean_20d` |
| resolve（≤ max as-of panels） | n_feats=**2**；feats＝上列二者 ⊆ active |
| max as-of（`core_universe_asof`） | **2026-05-31** |
| panels ≤ as-of | **80**（[2007-12-31..2026-05-31]） |

| feature | set_status | principle_id | last_action | registered_at | source_run_id |
|---|---|---|---|---|---|
| `inst_cumflow_position_120d` | active | 77 | promote | 2026-07-24 23:39:38+08 | 6 |
| `lending_fee_rate_mean_20d` | active | 107 | promote | 2026-07-29 13:07:08+08 | 10 |

覆蓋（`feature_values`，本輪 DB query）：

| feature | count | min panel | max panel |
|---|---|---|---|
| `inst_cumflow_position_120d` | **146598** | 2012-12-31 | 2026-06-30 |
| `lending_fee_rate_mean_20d` | **17072** | 2021-03-31 | 2026-06-30 |

> 註：cumflow count 較 `N1-RETRAIN-CLOSED` 登錄之 122160 高——本 CLOSED 以**本輪查庫**為準；不回溯改 n1 檔。

---

## 2. 指令矩陣（實跑）

```bash
./venv/bin/python scripts/verify_prodset_hotpath.py --selftest
# → EXIT=0；自測全通過

./venv/bin/python scripts/verify_prodset_hotpath.py --check
# → EXIT=0；active n=2；resolve n_feats=2；GRANT 對

./venv/bin/python scripts/predict_asof.py --run --dry-run --asof 2026-05-31
# → EXIT=0；model=…9a88039981b5a128；frozen＝上列二者
```

| 步 | 指令 | exit | log |
|---|---|---|---|
| 1 | `verify_prodset_hotpath.py --selftest` | **0** | `/tmp/augur_logs/n2_hotpath_selftest_20260729_145809.log` |
| 2 | `verify_prodset_hotpath.py --check` | **0** | `/tmp/augur_logs/n2_hotpath_verify_20260729_145809.log` |
| 3 | registry／artifact／prodset 唯讀對帳 | **0** | （本機 session stdout） |
| 4 | `predict_asof.py --run --dry-run --asof 2026-05-31` | **0** | `/tmp/augur_logs/n2_hotpath_predict_20260729_145809.log` |
| 5 | `evaluate_direction_gate`／`run_evaluation`／`run_economic_eval` | **SKIP** | 見 §4 |
| 6 | `train_ranker` | **未重跑** | 沿用 n1-retrain 同 model |

**未跑**：任何 `sync_finmind*`／`sync_macro`／`daily_maintenance`／FinMind／FRED fetch；PME S4；direction_gate evaluate。

---

## 3. 哨兵 stdout（真兆）

### `--selftest`

```
  ✓ prodset_contract 常數
  ✓ resolve_train_feats 預設 prodset
  ✓ import_isolation 0 違規
自測:全通過 ✓
```

### `--check`

```
✓ isolation 0 違規
✓ active n=2 feats=['inst_cumflow_position_120d', 'lending_fee_rate_mean_20d']
✓ resolve n_feats=2 feats=['inst_cumflow_position_120d', 'lending_fee_rate_mean_20d']
✓ predict SELECT evolution_production_feature_set=True (expect True)
✓ predict SELECT evolution_run=False (expect False)
✓ predict SELECT promotion_queue=False (expect False)
✓ verify_prodset_hotpath PASS（≠可交易／≠解凍）
```

---

## 4. Registry／artifact 對齊

| 鍵 | 值（真兆） |
|---|---|
| model_id | `RankRidge_H60_2026-05-31_seed42_9a88039981b5a128` |
| family／horizon／seed | RankRidge／60／42 |
| asof_snapshot | 2026-05-31 |
| feats_hash | `9a88039981b5a128` |
| feature_source（metrics） | prodset |
| n_feats | **2** |
| feats | `inst_cumflow_position_120d`、`lending_fee_rate_mean_20d` |
| n_train_rows | 8080 |
| n_panels | 68 |
| train_span | `[2007-12-31, 2026-06-01)` |
| git_sha | `1ec2438c55f18671fbf22a106aafe92dc66f2cb0` |
| created_at | 2026-07-29T13:18:11.149054+08:00 |
| artifact | 存在；size=**1189** bytes；path=`models_artifacts/…9a88039981b5a128.joblib` |

**對齊判**：active＝resolve＝frozen_feats＝registry `metrics.feats`（皆 n=2 同名單）→ 熱路徑一致。

---

## 5. Predict dry-run（可選核對）

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
| long 建議檔數 | **34**（建議≠下單） |

---

## 6. 明示邊界（必讀）

| 宣稱 | 本輪 |
|---|---|
| **可交易** | **否** |
| **確立級** | **否** |
| **direction_gate pass** | **否** — **未**執行 `evaluate_direction_gate`；庫內亦無 `direction_gate_evaluation`／`direction_gate_run` 表 |
| **解凍 FinMind／FRED** | **否**（FZ-keep） |
| **PME S4** | **未開** |
| GATE 閾值 | **未改** |
| commit／push | **未做** |
| 重訓 | **未做**（verify-only；模型沿 n1） |

---

## 7. Artifacts／logs

| 路徑 | 說明 |
|---|---|
| `audits/N2-HOTPATH-VERIFY-CLOSED-20260729.md` | 本檔 |
| `audits/WAVE2-SIX-TRACK-APPROVED-20260729.md` §三 | 留痕更新 |
| `/tmp/augur_logs/n2_hotpath_selftest_20260729_145809.log` | selftest |
| `/tmp/augur_logs/n2_hotpath_verify_20260729_145809.log` | --check |
| `/tmp/augur_logs/n2_hotpath_predict_20260729_145809.log` | predict dry-run |
| `model_registry` 列 | 同上 model_id |
| `models_artifacts/RankRidge_H60_2026-05-31_seed42_9a88039981b5a128.joblib` | artifact |

---

## 8. 建議下一句（非自動執行）

* 經濟／方向門／寫庫 predict → **另令**；本 CLOSED **不解凍、不假綠方向門**。  
* SH-ASOF-REFRESH（WAVE2 他軌）若抬 as-of，須另核對漂移／必要時重訓——**不**因本 verify 自動改 serving。

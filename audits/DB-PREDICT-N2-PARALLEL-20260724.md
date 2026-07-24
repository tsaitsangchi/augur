# 庫內預測／訓練／回測並行（prodset n=2）[I]（2026-07-24）

* Steward 授權：與 MAP-E012 **並行**；庫內 as-of；預設 prodset
* 對照：`audits/PME-REPROMOTE-RETRAIN-20260724.md`（run6 後重訓基線）
* 硬邊界：FZ-keep（零 FinMind／FRED）；不寫 `philosophy_*`／`principle_factor_map`／`evolution_*` APPLY／不改 prodset active；predict `--dry-run`；≠可交易／≠確立級；**誠實無擴大 n_feats**

---

## 結果（一句）

**prodset active=2 穩定；`train_ranker`／`predict_asof --dry-run` 皆綠；n_feats=2 未擴大；feats_hash 不變 → 同 model_id；econ 路徑 SKIP。**

---

## 1. 唯讀確認 prodset active

| 項 | 結果 |
|---|---|
| 表 | `evolution_production_feature_set` |
| active 數 | **2** |
| active 名單 | `inst_cumflow_position_120d`、`volume_gini_60d` |
| source_run_id | **6**（apply_log 3／4；與 PME-REPROMOTE 同） |
| 本輪是否改 active | **否**（唯讀） |

---

## 2. 執行

| 步 | 指令 | 結果 |
|---|---|---|
| 1 | 唯讀 `evolution_production_feature_set`（set_status=active） | n=2；上列特徵名 |
| 2 | `python scripts/train_ranker.py --run --asof 2026-05-31` | exit 0；預設 **prodset** |
| 3 | `python scripts/predict_asof.py --run --dry-run --asof 2026-05-31` | exit 0；**未寫庫** |
| 4 | 回測／econ 最小路徑 | **SKIP**（見下） |
| logs | `/tmp/augur_logs/db_predict_n2_parallel_{train,predict}.log` | |

### train stdout 關鍵

```
✓ 訓練完成 model_id=RankRidge_H60_2026-05-31_seed42_1420b777665a099f
  feature_source=prodset train_rows=12034 n_feats=2
  feats=['inst_cumflow_position_120d', 'volume_gini_60d']
  panels=35([2007-12-31..2026-05-31])
```

### predict stdout 關鍵

```
✓ as-of 2026-05-31 預測 model=RankRidge_H60_2026-05-31_seed42_1420b777665a099f
  feature_source=prodset n_feats=2 (dry-run 未寫庫)
  frozen_feats=['inst_cumflow_position_120d', 'volume_gini_60d']
── long 投組建議 top10%/equal(34 檔;系統建議、人決策、不下單;≠可交易)──
```

---

## 3. 與 PME-REPROMOTE-RETRAIN 對照

| 項 | PME-REPROMOTE（run6 後） | 本輪（並行 n=2） |
|---|---|---|
| active 數 | **2** | **2**（無擴大） |
| active 清單 | cumflow／volume_gini（source_run=6） | **同** |
| feature_source | prodset | prodset |
| n_feats | **2** | **2** |
| train_rows | 12034 | **12034** |
| n_panels | 35（[2007-12-31..2026-05-31]） | **同** |
| model_id | `RankRidge_H60_2026-05-31_seed42_1420b777665a099f` | **同**（feats_hash 不變） |
| predict | dry-run；long top10% equal 34 檔 | **同** |

---

## 4. Econ／回測 SKIP

| 候選入口 | 為何 SKIP |
|---|---|
| `scripts/run_economic_eval.py` | 走 ladder `B2_ridge`／`M1_gbdt` walk-forward（`--since` 多 panel），**非** prodset RankRidge 熱路徑；無 `--dry-run`／單 as-of 最小單位；PME-REPROMOTE 亦未跑 |
| `scripts/run_direction_econ_eval.py` | DirStack／方向軸，與本輪 RankRidge prodset 無關 |

**不硬造** Sharpe／IC；本輪無確立級／deflation 數字可報。

---

## 5. 驗收邊界

| 項 | 本輪 |
|---|---|
| 零市場 API | ✅ 庫內 panel／prodset；無 FinMind／FRED sync／probe／Dividend |
| 不碰 MAP 寫入 | ✅ 未寫 philosophy／map／evolution APPLY；未改 prodset active |
| 無擴大誠實 | ✅ n_feats 仍 2；同 model_id；**不宣稱特徵擴大** |
| ≠可交易／確立級 | ✅ dry-run 未寫庫；投組＝系統建議、人決策 |
| 未開 MAP-S3／S4 | ✅ |
| 未解凍 | ✅ |

---

## 6. 封存

* `bash scripts/archive_push.sh --slug db-predict-n2-parallel`
* HEAD：`6e08d1ea7ddd74f70a769f1f95c3b2883c805e2e`
* tag：`archive-20260724-db-predict-n2-parallel`（已 push origin）

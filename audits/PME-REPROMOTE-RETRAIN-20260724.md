# PME 再晉升後庫內重訓／預測 [I]（2026-07-24）

* Steward 約定：PME 本地再晉升收口後立刻庫內 as-of 重跑 train／predict
* 上游：`audits/PME-LOCAL-REPROMOTE-20260724.md`（run_id=6；APPLY×2；**active 仍 2**）
* 監看代理 ea9ac027：transcript 僅任務下達、**未**完成重訓——本檔為實跑收口
* 硬邊界：零 FinMind／FRED；≠可交易／確立級；**誠實無擴大 n_feats**

---

## 結果（一句）

**kill=clear；prodset active=2 穩定；`train_ranker`／`predict_asof` dry-run 皆綠；n_feats=2 未擴大**（與 E123／P2H 同特徵集；feats_hash 不變 → 同 model_id）。

---

## 前置確認

| 項 | 結果 |
|---|---|
| kill-switch | **effective=clear**（db clear；env halt=False） |
| run6 | succeeded；APPLY applied=2（冪等 validated→validated） |
| active 前（再晉升前／source_run=5） | `inst_cumflow_position_120d`、`volume_gini_60d` |
| active 後（source_run=**6**） | **同二特徵**（未擴大） |

---

## 執行

| 步 | 指令 | 結果 |
|---|---|---|
| 1 | `set_evolution_kill_switch.py --status` | clear |
| 2 | `train_ranker.py --run --asof 2026-05-31` | exit 0；預設 **prodset** |
| 3 | `predict_asof.py --run --dry-run --asof 2026-05-31` | exit 0；未寫庫 |
| 4 | logs | `/tmp/augur_logs/pme_repromote_retrain_{train,predict}.log` |

---

## 前後對照（active／n_feats／rows）

| 項 | 再晉升前（E123／P2H） | 本輪（run6 後重訓） |
|---|---|---|
| active 數 | **2** | **2**（無擴大） |
| active 清單 | cumflow／volume_gini（source_run=5） | 同（source_run=**6**；apply_log 3／4） |
| feature_source | prodset | prodset |
| n_feats | **2** | **2** |
| feats | `inst_cumflow_position_120d`、`volume_gini_60d` | **同** |
| train_rows | 12034 | **12034** |
| n_panels | 35（[2007-12-31..2026-05-31]） | **同** |
| model_id | `RankRidge_H60_2026-05-31_seed42_1420b777665a099f` | **同**（feats_hash 不變） |
| predict | dry-run n_feats=2；漂移通過 | **同**；long top10% equal 34 檔（建議≠下單） |

---

## 驗收邊界

| 項 | 本輪 |
|---|---|
| 零市場 API | ✅ 庫內 panel／prodset；無 FinMind／FRED |
| 預設 prodset | ✅；禁 silent canonical；FC-empty 路徑未觸發 |
| 無擴大誠實 | ✅ n_feats 仍 2；不假稱特徵完備 |
| ≠可交易／確立級 | ✅ dry-run 未寫庫；投組＝系統建議、人決策 |
| G-PME-HOTPATH | 維持 **none**（機械真讀；仍極窄） |

---

## Gap

| ID | 本輪 |
|---|---|
| **G-PME-HOTPATH** | 維持 **none**；重訓確認穩定、**未**因再晉升擴大覆蓋 |
| **G-PME-PROM**／**G-PME-ECON** | 維持 **partial**（見 LOCAL-REPROMOTE） |

擴大 n_feats 需：**新假說／map 覆蓋**、或資料洞補齊（缺股／blocked_div 仍 FZ-keep）後再閘——**非**本輪重訓可解。

---

## 封存

* `bash scripts/archive_push.sh --slug pme-repromote-retrain-hotpath`
* HEAD／tag：見封存 stdout

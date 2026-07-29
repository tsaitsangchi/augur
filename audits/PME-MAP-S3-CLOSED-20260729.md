# PME MAP-S3 CLOSED [I]（2026-07-29）

* Steward 授權：「**所有 working 開始跑**」＝開 **MAP-S3**
* 前輪：`audits/PME-MAP-E012-CLOSED-20260724.md`（S0–S2；mapped 17→35；`roe`／`debt_ratio` built）
* 拍板：`MAP-P-yes`＋`MAP-E012`＋`FZ-keep`＋`GATE-keep` → `audits/PME-MAP-EXPAND-PLAN-APPROVED-20260724.md`
* 計畫：`reports/augur_pme_expand_hypothesis_map_coverage_plan_20260724.md` §3 S3
* 性質：[I]；**不**創設 [N]；**≠**可交易／≠確立級；**≠**解凍
* 同窗共用閘證據：`audits/PME-XDOM-SUNZI-MGMT-S3-CLOSED-20260729.md`（同 `run_id=6`；全表 local-gates 一次、勿雙跑）

## 一句

**MAP-S3 可驗完成**——庫內 `local-gates`＋AUTO-B APPLY（GATE-keep）；MAP-E012 新建／新 map 特徵（含 `roe`／`debt_ratio`）**零雙綠**；唯一雙綠仍為既有 `inst_cumflow_position_120d`；active **n=1**（未擴大）。**不需急開 S4**。

## S3 範圍（計畫對照）

| 項 | 本輪 |
|---|---|
| 入口 | `run_philosophy_evolution.py --local-gates --since 2021-01-01 --h 60` → `apply_evolution_promotions.py --run-id 6` |
| 閘對象 | 全 `principle_factor_map`（**77** 列；coverage **mapped=35**／missing=3／blocked_div=1）——含 MAP-E012 擴充 map＋S2 `roe`／`debt_ratio` |
| 窗 | panels=**22**（`feature_values` ≥2021-01-01）；canonical_features n=**35** |
| 閾值 | `DEFAULT_GATE_CONFIG` 釘死（`min_abs_hac_t=2.0`／`min_seeds=3`／`min_delta_ic=0.0`）— **GATE-keep** |
| S4 | 僅當 active **集合變更**後另令；本輪 active 成員未擴大 → **不開** |

## 執行

| 步 | 動作 | 結果 |
|---|---|---|
| 1 | 衝突協調 | 同窗已有 XDOM-S3 持 `/tmp/augur_pme_local_gates.lock`；**MAP 不另開第二 local-gates**（計畫同入口＝全表重閘） |
| 2 | local-gates | **run_id=6** `succeeded`；elapsed≈**4h20m**（08:07→12:26）；log=`/tmp/augur_logs/pme_xdom_sunzi_s3_local_gates.log` |
| 3 | APPLY | **applied=12**／rejected_gate=65；log=`/tmp/augur_logs/pme_xdom_sunzi_s3_apply.log`（peer 已跑；MAP 複核 queue／prodset） |
| 4 | 殘留清理 | **run_id=5** 競態孤兒（queue=0）→ 標 `failed`（MAP-S3 收斂；notes 留痕） |

## 閘結果（run_id=6；親驗）

### Map 列 tally（77）

| 閘 | PASS | FAIL | FAIL_SIGN | SKIP |
|---|---|---|---|---|
| **G-PROM** | 3 | 59 | 11 | 4 |
| **G-ECON** | 24 | 49 | — | 4 |

| queue_status | n |
|---|---|
| applied | 12 |
| rejected_gate | 65 |
| halted | 0 |

### 唯一特徵雙綠

| feature | G-PROM | G-ECON | APPLY |
|---|---|---|---|
| `inst_cumflow_position_120d` | PASS | PASS | promote → prodset **active**（source_run_id=6） |

G-PROM PASS map 列=3＝同特徵多 principle；**雙綠特徵數=1**（非 3）。

### MAP-E012 焦點（S2 新特徵＋擴充 map 抽樣）

| feature | G-PROM | G-ECON | queue | 註 |
|---|---|---|---|---|
| `roe` | FAIL | FAIL | rejected_gate | S2 新建；**未過閘** |
| `debt_ratio` | FAIL_SIGN | FAIL | demote applied | S2 新建；FAIL_SIGN≠promote |
| `momentum_5d` | FAIL | FAIL | rejected_gate | |
| `return_1d` | FAIL | PASS | rejected_gate | ECON-only≠晉升 |
| `range_position_120d` | FAIL | PASS | rejected_gate | ECON-only≠晉升 |
| `lending_fee_rate_mean_30d` | FAIL | PASS | rejected_gate | ECON-only≠晉升 |
| `sbl_short_balance_log` | FAIL | FAIL | rejected_gate | |
| `inst_cumflow_position_60d` | PASS | FAIL | rejected_gate | PROM 單綠≠晉升 |
| `volume_gini_60d` | FAIL_SIGN | PASS | demote applied | 歷史曾雙綠；本窗季頻 22 panel **非**雙綠 |

→ **擴大 map／新建 fundamentals 本輪零新雙綠**（誠實預期內；不降閘、不敘事美化）。

### SKIP（誠實；≠PASS）

| feature | coverage_class |
|---|---|
| `dividend_yield` | blocked_div |
| `macro_regime`／`peg_ratio`／`piotroski_fscore` | missing |

## prodset

| 項 | 後（APPLY run6） |
|---|---|
| active | **僅** `inst_cumflow_position_120d` |
| active n | **1**（未擴大；相對 MAP 目標「誠實成長」＝**未達成**） |
| demote→removed（本輪） | `debt_ratio`／`gov_bank_net_buy_60d`／`top_holders_pct`／`volume_gini_20d`／`volume_gini_60d`／`volume_max_share_20d`／`volume_max_share_60d` |

## 硬邊界核對

| 碼 | 本輪 |
|---|---|
| MAP-S3 | ✅ local-gates＋APPLY；共用 run_id=6 |
| GATE-keep | ✅ 未降閾；ECON-only／FAIL_SIGN≠promote；SKIP≠PASS |
| FZ-keep | ✅ 零 FinMind／FRED；庫內 as-of |
| ≠可交易／確立級 | ✅ |
| 勿雙跑 | ✅ 等 XDOM 持鎖完成；清 run5 殘留 |

## S4

| 建議 | 理由 |
|---|---|
| **不開 MAP-S4** | active 集合**未擴大**（仍 n=1）；計畫：S4 僅 active 變動後 |
| 可另令 | 若要熱路徑與 demote 後 prodset **機械對齊**重訓（誠實 n_feats=1）—須明示；**仍 ≠可交易** |

## 封存

`bash scripts/archive_push.sh --slug map-s3`

## 交叉引用

* 同跑全表閘細節（含 sunzi_mgmt×9）：`audits/PME-XDOM-SUNZI-MGMT-S3-CLOSED-20260729.md`
* 前階：`audits/PME-MAP-E012-CLOSED-20260724.md`

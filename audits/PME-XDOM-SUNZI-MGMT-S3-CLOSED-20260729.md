# PME-XDOM-SUNZI-MGMT S3 CLOSED [I]（2026-07-29）

* Steward 授權：「所有 working 開始跑」＝開 **`PME-XDOM-S3`**（孫子×企管軸）  
* 前輪：`audits/PME-XDOM-SUNZI-MGMT-S01-CLOSED-20260728.md`（S0＋S1；S2 缺特徵未建）  
* 計畫：`reports/augur_pme_cross_domain_evolution_enable_plan_20260728.md` §3 S3  
* 性質：[I]；**不**創設 [N]；**≠**可交易／≠確立級；**≠**解凍；**未**灌 ERP dump  
* 硬碼：`GATE-keep`／`FZ-keep`／庫內 as-of／零 FinMind／FRED

## 一句

**S3 local-gates＋APPLY 可驗完成**——全表 77 map 重閘（含 sunzi_mgmt×9）；**異域新 map 零雙綠**；唯一雙綠仍為既有 `inst_cumflow_position_120d`；FAIL_SIGN demote 使 active **縮至 1**。S2 缺特徵誠實未建。

## 執行

| 步 | 指令／動作 | 結果 |
|---|---|---|
| 0 | 確認 S3＝對已 map 可對映假說跑 local-gates；S2 缺列不硬建 | ✅ 計畫 §3；S0 三桶 B 仍缺 |
| 1 | `set_evolution_kill_switch.py --status` | effective[tw]=**clear** |
| 2 | flock `/tmp/augur_pme_local_gates.lock`＋`run_philosophy_evolution.py --local-gates --since 2021-01-01 --h 60` | **run_id=6** `succeeded`；elapsed≈**4h20m**（08:07→12:26）；log=`/tmp/augur_logs/pme_xdom_sunzi_s3_local_gates.log` |
| 3 | 雙寫協調 | 同窗 AI-PREDICT-S3 競態：其進程 SIGTERM；**run_id=5** 留 `running` 孤兒（僅 coverage、queue=0）；本輪結果寫在 **run_id=6**。peer 已 defer 本鎖 |
| 4 | `apply_evolution_promotions.py --run-id 6` | **applied=12**／skipped=0；log=`/tmp/augur_logs/pme_xdom_sunzi_s3_apply.log` |

### 窗／素材（親驗）

| 項 | 值 |
|---|---|
| maps | **77**（sun_tzu=15，其中 `xdom_loop=sunzi_mgmt`=9；其餘他校／ai_predict） |
| `feature_values` panel 粒徑 | **季頻**；since≥2021-01-01 → **panels=22**（全庫 DISTINCT panel_date=57） |
| canonical_features | n=35 |
| kill | clear |
| G-ISO／G-NOEXEC／G-ATTEST | PASS／PASS／PASS |

## 閘結果（run_id=6）

### Map 列 tally（77）

| 閘 | PASS | FAIL | FAIL_SIGN | SKIP |
|---|---|---|---|---|
| **G-PROM** | 3 | 59 | 11 | 4 |
| **G-ECON** | 24 | 49 | — | 4 |

| queue_status | n |
|---|---|
| pending_auto→**applied** | 12 |
| rejected_gate | 65 |
| halted | 0 |

### 唯一特徵雙綠

| feature | G-PROM | G-ECON | 動作 |
|---|---|---|---|
| `inst_cumflow_position_120d` | PASS | PASS | **promote**→prodset **active** |

（G-PROM PASS map 列=3＝同特徵多 principle 重複；唯一雙綠特徵＝**1**。）

### SKIP（誠實；coverage）

| feature | coverage_class |
|---|---|
| `dividend_yield` | blocked_div |
| `macro_regime`／`peg_ratio`／`piotroski_fscore` | missing |

### sunzi_mgmt 新 map（9；本輪焦點）

| feature | G-PROM | G-ECON | queue |
|---|---|---|---|
| `gov_bank_net_buy_60d` | FAIL_SIGN | PASS | demote applied |
| `top_holders_pct` | FAIL_SIGN | FAIL | demote applied |
| `inst_cumflow_position_60d` | PASS | FAIL | rejected_gate（ECON 紅→不晉升） |
| `debt_ratio` | FAIL_SIGN | FAIL | demote applied |
| `roe` | FAIL | FAIL | rejected_gate |
| `range_mean_20d` | FAIL | FAIL | rejected_gate |
| `pb_ratio` | FAIL | FAIL | rejected_gate |
| `momentum_20d` | FAIL | FAIL | rejected_gate |
| `gross_margin_pctile` | FAIL | FAIL | rejected_gate |

→ **異域文獻橋本輪零雙綠**（允許大量 FAIL；不敘事美化）。

### S2 缺特徵列帳（仍未建；本輪不硬交）

| 概念代理 | feature | `feature_values` |
|---|---|---|
| 流動性緩衝 | `current_ratio`／`cash_ratio` | **0** |
| 毛利水準（非分位） | `gross_margin`／`operating_margin` | **0** |

## prodset 前後

| 項 | 前（本機親驗起跑時） | 後（APPLY run6） |
|---|---|---|
| active | `inst_cumflow_position_120d`（source_run_id=2） | **同特徵**（source_run_id=**6**） |
| active n | 1 | **1** |
| 本輪 demote→removed | — | `debt_ratio`／`gov_bank_net_buy_60d`／`top_holders_pct`／`volume_gini_20d`／`volume_gini_60d`／`volume_max_share_20d`／`volume_max_share_60d` |

註：`volume_gini_60d` 本窗 **FAIL_SIGN**（非雙綠）→ demote；與歷史 run 曾雙綠之對照＝**季頻 22 panel 窗＋本輪證據**，不回寫假綠。

## 硬邊界核對

| 碼 | 本輪 |
|---|---|
| `PME-XDOM-S3`／`SUNZI-MGMT` | ✅ local-gates＋APPLY；ERP dump 零 SEED |
| `GATE-keep` | ✅ 未降閾；ECON-only／FAIL_SIGN≠promote；SKIP≠PASS |
| `FZ-keep` | ✅ 零 FinMind／FRED |
| ≠可交易／確立級 | ✅ 僅 prodset 狀態 |
| 缺特徵 | ✅ 列帳未建 |

## 協調殘件（人可後清）

| 項 | 狀態 |
|---|---|
| `evolution_run` **run_id=5** | 仍 `status=running`（AI-PREDICT 競態孤兒；coverage×39、queue=0）。**未**手改狀態（避雙寫外手動踩踏）；建議另令標記 `failed` 或由 AI-PREDICT-S3 收斂時清理 |
| AI-PREDICT-S3 | peer 已 defer 本鎖；**可重用 run_id=6** 全表閘結果（含 `ai_predict` maps），勿再並行開第二 local-gates |

## S4 建議

| 建議 | 理由 |
|---|---|
| **不建議急開 S4** | 異域無新雙綠；active n 仍 **1**（未擴大）；重訓只會對齊更窄／同窄 prodset，無擴大 n_feats 預期 |
| **可另令開** | 若 Steward 要熱路徑與「gini demote 後」prodset **機械對齊**重訓（誠實 n_feats=1）——須明示 `PME-XDOM-S4`／P2H 類令；**仍 ≠可交易** |

## 封存

`bash scripts/archive_push.sh --slug pme-xdom-sunzi-s3`

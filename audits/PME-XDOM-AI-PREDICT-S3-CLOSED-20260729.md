# PME-XDOM-AI-PREDICT S3 CLOSED [I]（2026-07-29）

* Steward 授權：「所有 working 開始跑」＝開 **`PME-XDOM-AI-PREDICT-S3`**  
* 前輪：`audits/PME-XDOM-AI-PREDICT-S01-CLOSED-20260728.md`（S0＋S1；school `ml_predict_evolution`；map×10）  
* 拍板：`audits/PME-XDOM-AI-PREDICT-APPROVED-20260728.md`  
* 短計畫：`reports/augur_pme_xdom_ai_predict_plan_20260728.md` §2 S3  
* 同窗共用閘證據：`audits/PME-XDOM-SUNZI-MGMT-S3-CLOSED-20260729.md`／`audits/PME-MAP-S3-CLOSED-20260729.md`（同 **`run_id=6`**）  
* 性質：[I]；**不**創設 [N]；**≠**可交易／≠確立級；**≠**解凍  
* 硬碼：`GATE-keep`／`FZ-keep`／`NHC-keep`

## 一句

**S3 local-gates 可驗完成**——AI×predict 文獻 map×10 全入庫內閘；**本軸零雙綠**（G-PROM PASS=0）；ECON-only 不晉升。本軸**未**自行 APPLY／approve／activate（peer SUNZI 已對全表 run6 做 AUTO-B）；active 未因本軸擴大。

## S3 範圍（確認）

| 項 | 本輪 |
|---|---|
| 定義 | 對 **AI×predict 文獻 map**（`school=ml_predict_evolution`／`provenance.xdom_loop=ai_predict`）跑 **local-gates**（庫內 `feature_values`／panel as-of） |
| 入口 | `scripts/run_philosophy_evolution.py --local-gates --since 2021-01-01 --h 60`（引擎＝全 `principle_factor_map`；本軸焦點＝其子集×10） |
| 不做 | S4 重訓；本軸不呼叫 `apply_evolution_promotions`／approve／activate；不降閘；零 FinMind／FRED |
| S2 | 缺特徵仍列帳未建（`model_ic_stability_*`／`purged_cv_score`／`ensemble_disagreement`／`gross_margin`） |

## 執行／排隊

| 步 | 動作 | 結果 |
|---|---|---|
| 1 | 確認無第二 local-gates | 同窗 SUNZI／MAP 共用 DB；canonical lock＝`/tmp/augur_pme_local_gates.lock` |
| 2 | 競態止血 | 曾誤用不同 lock 路徑短暫雙跑 → **SIGTERM 本軸進程**；殘留 **run_id=5** 空 queue 後由 MAP-S3 標 `failed` |
| 3 | 閘證據 | **重用 peer 完成之 `run_id=6`**（勿再並行開第二 local-gates）；elapsed≈**4h20m**（08:07→12:26）；log=`/tmp/augur_logs/pme_xdom_sunzi_s3_local_gates.log` |
| 4 | APPLY | **本軸未跑**（令：禁 approve／activate）。peer SUNZI 已 `apply_evolution_promotions.py --run-id 6`（applied=12）——見其收官；本軸僅複核 AI 列 |

### 窗／素材（親驗）

| 項 | 值 |
|---|---|
| school | `ml_predict_evolution`（school_id=159） |
| AI maps | **10**（全 in `feature_values`／coverage=mapped） |
| 全表 maps | **77**（本軸⊂全表閘） |
| panels | **22**（since≥2021-01-01；季頻） |
| kill | clear |
| G-ISO／G-NOEXEC／G-ATTEST | PASS／PASS／PASS |

## 閘結果 — AI×predict 焦點（run_id=6；親驗）

| feature | dir | G-PROM | G-ECON | queue | principle.status（後） |
|---|---|---|---|---|---|
| `volatility_60d` | −1 | FAIL | FAIL | rejected_gate | untested |
| `range_mean_20d` | −1 | FAIL | FAIL | rejected_gate | untested |
| `debt_ratio` | −1 | FAIL_SIGN | FAIL | **demote applied**（peer） | **sign_refuted**（p=114） |
| `roe` | +1 | FAIL | FAIL | rejected_gate | **sign_refuted**（同 p=114；隨 demote） |
| `institutional_net_buy_ratio_20d` | +1 | FAIL | PASS | rejected_gate | untested |
| `foreign_holding_pct` | +1 | FAIL | FAIL | rejected_gate | untested |
| `range_position_120d` | −1 | FAIL | PASS | rejected_gate | untested |
| `days_since_high_252d` | +1 | FAIL | PASS | rejected_gate | untested |
| `pe_ratio` | −1 | FAIL | FAIL | rejected_gate | untested |
| `monthly_revenue_yoy` | +1 | FAIL | FAIL | rejected_gate | untested |

### 本軸 tally（map×10）

| 閘 | PASS | FAIL | FAIL_SIGN |
|---|---|---|---|
| **G-PROM** | **0** | 9 | 1 |
| **G-ECON** | 3 | 7 | — |

| 雙綠（PROM∧ECON） | **0** |
|---|---|
| 本軸 promote→active | **0** |

→ **文獻橋本輪零雙綠**（誠實；不敘事美化）。ECON-only（3）≠晉升（GATE-keep）。

### 全表對照（同 run；非本軸宣稱）

| 項 | 值 |
|---|---|
| G-PROM tally（77 列） | PASS=3／FAIL=59／FAIL_SIGN=11／SKIP=4 |
| 唯一雙綠特徵 | `inst_cumflow_position_120d`（既有；≠ ai_predict） |
| active n（APPLY 後） | **1**（`inst_cumflow_position_120d`；source_run_id=6） |

## 硬邊界核對

| 碼 | 本輪 |
|---|---|
| `PME-XDOM-AI-PREDICT-S3` | ✅ 庫內 local-gates；焦點 map×10 有真兆 |
| `GATE-keep` | ✅ 未降閾；SKIP≠PASS；ECON-only≠晉升 |
| `FZ-keep` | ✅ 零 FinMind／FRED |
| `NHC-keep` | ✅ 無領域專答；策展仍住 DB／既有腳本 |
| 禁 approve／activate | ✅ **本軸未呼叫** APPLY／approve／activate |
| ≠可交易／確立級 | ✅ |
| 禁 AI 造原則 | ✅ 未改 source／citation |

## 協調殘件

| 項 | 狀態 |
|---|---|
| run_id=5 | 已 `failed`（MAP-S3 清；空 queue） |
| 雙 lock 路徑 | 教訓：共用 **`/tmp/augur_pme_local_gates.lock`**（勿另開 `/tmp/augur_locks/...`） |
| peer APPLY | 屬 SUNZI／MAP S3 收官範圍；本軸 audit **不**把全表 demote／promote 算作本軸成果 |

## 下一步（人）

| 建議 | 理由 |
|---|---|
| **不開本軸 S4** | 本軸零雙綠；無新 active 來自 ai_predict |
| 可另令 | 熱路徑與「active n=1」機械對齊重訓（須明示；仍 ≠可交易）——見 SUNZI／MAP S3 收官 |
| 他域 | `PME-XDOM-SOLAR` 等仍另拍 |

## 封存

`bash scripts/archive_push.sh --slug pme-xdom-ai-predict-s3`

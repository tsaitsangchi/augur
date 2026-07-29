# KNI-S3 CLOSED（2026-07-29）

> **性質**：[I] 執行收官；不創設 [N]。  
> **拍板**：`KNI-S3 + KH7-PLAN + KH7-S1 + RKI-keep + NHC-keep + FZ-keep + HUMAN-APPROVE-keep`  
> **計畫**：`reports/augur_knowhow_nary_interaction_plan_20260728.md` §S3；對齊 `reports/augur_kh7_adversarial_eligibility_plan_20260729.md`  
> **報告**：`reports/augur_kni_s3_eval_20260729.md`

## 做了什麼

| 產物 | 狀態 |
|---|---|
| `knowhow_eval_suite_case`＋4 case 種子 | ✅ |
| `KNI-EVAL-EMPTY-CORPUS` decline 探針 | ✅ |
| `scripts/eval_knowhow_interaction_probes.py` | ✅ live＋ledger |
| `ungrounded_hits` 軸落地旗標（`interaction_probe`） | ✅ 修假 decline／假綠 |
| decline 機械斷言 | ✅ **PASS**（`ungrounded_hits`） |

## Live 指標（run_id=4）

| role | probe | merged | multi | spur | gap | kh7 |
|---|---|---:|---:|---|---|---|
| full_triple | RKI-FP-AI-SOLAR | 23 | 1 | high | ungrounded_hits | fail |
| ablation_no_principle | RKI-AI-SOLAR-RD | 18 | 0 | medium | ungrounded_hits | fail |
| ablation_no_ai | RKI-FP-SOLAR-CORE | 16 | 2 | high | ungrounded_hits | fail |
| expect_decline | KNI-EVAL-EMPTY-CORPUS | 16 | 2 | high | ungrounded_hits | fail |

說明：語料對太陽能／第一性軸字面未落地命中 title／snippet → **誠實全 fail**（非答案 SSOT）；decline 案例正確辨識假近鄰。

## 驗收

| ID | 結果 |
|---|---|
| V-TRACE | ✅ 數字出自 stdout／ledger run_id=4 |
| V-NHC | ✅ 無專支答案樹 |
| V-FZ | ✅ 零 FinMind／FRED |
| decline assert | ✅ PASS（ungrounded_hits） |
| selftest | ✅ interaction_probe／eval |

## 非範圍

- 不開 PME-XDOM-SOLAR；不自動 approve；不入憲

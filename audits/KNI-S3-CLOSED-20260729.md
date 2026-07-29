# KNI-S3 CLOSED（2026-07-29）

> **性質**：[I] 執行收官；不創設 [N]。  
> **拍板**：`audits/KH7-PLAN-APPROVED-20260729.md`（含 `KNI-S3`）  
> **計畫**：`reports/augur_kh7_adversarial_eligibility_plan_20260729.md` §2.3／§3／§7（含 live 教訓修訂）  
> **不含**：approve／activate／KH8–10／PME-XDOM-SOLAR／FinMind／FRED／入憲

## 一、做了什麼

| 項 | 狀態 | 摘要 |
|---|---|---|
| DDL＋種子 | ✅ | `migrate_knowhow_eval_suite_ddl.py --apply`；`knowhow_eval_suite_case`×4；探針 `KNI-EVAL-EMPTY-CORPUS` |
| Eval CLI | ✅ | `eval_knowhow_interaction_probes.py`（複用 `run_probe`；live＋ungrounded／KH7 decline） |
| Live 評測 | ✅ | `--run --write-ledger --report …`；**run_id=5**；decline **PASS**（`ungrounded_hits`） |
| Live 教訓 | ✅ | e5 top‑k 對無意義軸仍有近鄰 → decline≠裸 `no_corpus`；改 ungrounded 字串校驗 |
| FZ／NHC／HUMAN-APPROVE | ✅ | 零市場 API；無專題答案樹；不碰 approve |

## 二、Live 指標摘要（run_id=5）

| case_id | role | merged | multi_src | spurious | gap |
|---|---|---:|---:|---|---|
| KNI-S3-FULL-FP-AI-SOLAR | full_triple | 23 | 1 | high | ungrounded_hits |
| KNI-S3-ABL-NO-FP | ablation_no_principle | 18 | 0 | medium | ungrounded_hits |
| KNI-S3-ABL-NO-AI | ablation_no_ai | 16 | 2 | high | ungrounded_hits |
| KNI-S3-EXPECT-DECLINE | expect_decline | 16 | 2 | high | ungrounded_hits → **PASS** |

消融：no-FP multi_src 相對 full **−1**；decline 靠 ungrounded 機械綠（非假裝 KNN 空）。

報告：`reports/augur_kni_s3_eval_20260729.md`

## 三、驗證

| 檢查 | 結果 |
|---|---|
| migrate／eval `--selftest` | ✅ |
| `check_cmd_matrix.py` | ✅ NEED=0 |
| Live decline assert | ✅ PASS（ungrounded_hits） |

## 四、變更檔

- `scripts/migrate_knowhow_eval_suite_ddl.py` — **新**
- `scripts/eval_knowhow_interaction_probes.py` — **新**
- `src/augur/knowledge/interaction_probe.py` — ungrounded gap／spurious 校驗（與 KH7 對齊）
- `reports/augur_kni_s3_eval_20260729.md`
- 本 CLOSED

## 五、硬邊界

| 項 | 結果 |
|---|---|
| 零 FinMind／FRED | ✅ |
| 無專題答案樹 | ✅ |
| 不改 approval_status | ✅ |
| 不改 [N] | ✅ |

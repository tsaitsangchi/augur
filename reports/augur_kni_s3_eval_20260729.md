# KNI-S3 eval [I] (2026-07-29T01:03Z)

* 性質：[I] 評測產物；非答案 SSOT；非 [N]
* cases: KNI-S3-ABL-NO-AI, KNI-S3-ABL-NO-FP, KNI-S3-EXPECT-DECLINE, KNI-S3-FULL-FP-AI-SOLAR
* run_id: 5
* decline_ok: True

## 逐 case 指標

| case_id | role | probe_id | merged | multi_src | spurious | gap_flags |
|---|---|---|---:|---:|---|---|
| KNI-S3-ABL-NO-AI | ablation_no_ai | RKI-FP-SOLAR-CORE | 16 | 2 | high | `["ungrounded_hits"]` |
| KNI-S3-ABL-NO-FP | ablation_no_principle | RKI-AI-SOLAR-RD | 18 | 0 | medium | `["ungrounded_hits"]` |
| KNI-S3-EXPECT-DECLINE | expect_decline | KNI-EVAL-EMPTY-CORPUS | 16 | 2 | high | `["ungrounded_hits"]` |
| KNI-S3-FULL-FP-AI-SOLAR | full_triple | RKI-FP-AI-SOLAR | 23 | 1 | high | `["ungrounded_hits"]` |

## 消融對照（full vs no-FP vs no-AI）

| arm | merged | multi_src | spurious | Δmulti vs full | Δspur note |
|---|---:|---:|---|---:|---|
| full_triple | 23 | 1 | high | +0 | spur=high vs full=high |
| ablation_no_principle | 18 | 0 | medium | -1 | spur=medium vs full=high |
| ablation_no_ai | 16 | 2 | high | +1 | spur=high vs full=high |

## expect_decline 機械斷言

- probe: `KNI-EVAL-EMPTY-CORPUS`
- gap_flags: `['ungrounded_hits']`
- merged_hits: 16
- decline 判準: no_corpus ∨ ungrounded_hits ∨ KH7=eligibility_fail（e5 top‑k 近鄰≠落地）
- assert: **ungrounded_hits** → PASS

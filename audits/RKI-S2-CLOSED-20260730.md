# RKI-S2 CLOSED（2026-07-30）

> **性質**：[I] 執行收官；不創設 [N]。  
> **授權**：Steward「**RKI-S2 — probe runner**」  
> **拍板**：`audits/RKI-S2-APPROVED-20260730.md`  
> **計畫**：`reports/augur_raw_knowhow_interaction_probe_plan_20260728.md` §4-S2  
> **不含**：RKI-S3／PME 灌因子／approve／activate／改 [N]

## 一、做了什麼

| 項 | 結果 |
|---|---|
| runner | 既有 `scripts/run_knowhow_interaction_probes.py`（KNI／KH4 已建；本輪正式掛 **RKI-S2**） |
| `--selftest` | ✅ 全綠 |
| `--run --all --write-ledger` | ✅ **15** active probes |
| ledger | **`run_id=7`**（note=`RKI-S2-20260730`） |
| 報告 | `reports/augur_rki_s2_probe_run_20260730.md` |
| FZ-keep／NHC-keep | ✅ 零 FinMind／FRED；無領域專答樹 |

## 二、真兆摘要（stdout／ledger）

| 指標 | 值 |
|---|---|
| probes 完成 | 15（含 14 RKI 種子＋`KNI-EVAL-EMPTY-CORPUS`） |
| 含 `gap_flags` | **7** |
| ledger | `knowhow_interaction_probe_run`／`_result` run_id=7 |

### gap／spurious（誠實）

| probe_id | gap | spurious |
|---|---|---|
| RKI-AI-SOLAR-RD | [] | low |
| RKI-FP-AI-SOLAR | [] | low |
| RKI-FP-SOLAR-CORE | [] | low |
| RKI-FP-SOLAR-APP | [] | low |
| RKI-FP-SOLAR-CHEM | [] | low |
| RKI-FP-SOLAR-PHYS | [] | low |
| RKI-PARETO-SOLAR | [] | low |
| RKI-AI-PREDICT-EVAL | [] | low |
| **KNI-EVAL-EMPTY-CORPUS** | `ungrounded_hits` | high（期望：無意義軸） |
| RKI-AI-PREDICT-EVO | `ungrounded_hits` | high |
| RKI-FP-AI-ITER | `ungrounded_hits` | high |
| RKI-FP-AI-PREDICT | `ungrounded_hits` | high |
| RKI-FP-PREDICT-ITER | `ungrounded_hits` | high |
| RKI-PHILO-RD-TMPL | `ungrounded_hits` | high（template 槽位 `{{principle}}`／`{{tech_domain}}` **未實例化**） |
| RKI-SUNZI-MGMT | `ungrounded_hits` | high |

**觀察（非假兆）**：多探針 top hit 常出現 `Post-WIMP…`／`rdai_*`——檢索有命中但錨點校準常判 ungrounded；≠過閘／≠可灌 PME。

## 三、硬邊界

| 項 | |
|---|---|
| 未開 RKI-S3／PME APPLY | ✅ |
| 未改 answer／approval／activate | ✅ |
| 未 annotate-kh4（本輪未加旗標） | ✅ |

## 四、下一步（待另令）

1. **`RKI-S3`** — 評測餵養／人揀 PME 候選（solar／AI 只列不灌）  
2. 可選：修 `RKI-PHILO-RD-TMPL` 種子 `template_params` 實例化  
3. 可選：`--annotate-kh4` 另令

---
status: executed
series: kh_ops
track: KH-S0-APPLY
date: 2026-08-18
viewpoint: 2026-08-18T09:07+08:00
go: audits/KH-S0-APPLY-GO-20260818.md
fired: audits/KH-S0-APPLY-FIRED-20260818.md
log: /tmp/kh-s0-apply-20260818/apply.log
paste: "KH-S0-APPLY-EXECUTED | S0=0 | seeded=218 advanced=0 | no-lift>KH2 | S3 still FIRE | no-B3"
self_reported: true
layer: "[I]"
---

# EXECUTED｜KH S0 drain

Steward `KH-S0-apply-go`。一槍 `--apply`。B3 未開火。未抬層。

| 步 | 動作 | RC | 結果 |
|---|---|---|---|
| PRE | 量測（apply 開頭） | 0 | S0 FIRE **218**；S1 ok；S3 zh lag=2 |
| APPLY-1 | S0 `run_kh_chain --phase advance --up-to 0 --limit 218` | **0** | round1 candidates=218 **seeded=218 advanced=0**；round2 queue empty；破口 **218→0** |
| FINAL | `--check` | 0 | **S0 ok（0）** · S1 ok · **S3 仍 FIRE** zh lag=2 |

`up_to=0` ⇒ 只種 KH0，`advanced=0`。gate `max_auto_depth=9` 未在本槍使用。

## 未做

S3 concordance（本 paste 未授）· AUTO-LIFT · 假 B3＠08-18 · promote · 市場出門

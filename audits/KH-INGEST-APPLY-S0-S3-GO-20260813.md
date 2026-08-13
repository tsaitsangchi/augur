---
status: go
series: kh_ops
track: KH-INGEST-APPLY
date: 2026-08-13
viewpoint: 2026-08-13T10:07+08:00
paste: "KH-INGEST-APPLY-S0-S3-go | FZ/GATE-keep | apply=opt-in | S0→S3 | no-autolift | no-timer | no-market-axis"
prior_c: audits/KH-INGEST-TRIGGER-C-EXECUTED-20260812.md
check_live: "S0 FIRE kh0_breach=6; S3 FIRE lag; S1 FIRE"
self_reported: true
layer: "[I]"
---

# GO｜kh_ingest_trigger --apply · S0→S3

```text
KH-INGEST-APPLY-S0-S3-go | FZ/GATE-keep | apply=opt-in
| S0 drain then S3 concordance | no-AUTO-LIFT | no-cron | ≠市場 tip
```

| 步 | 准 | 禁 |
|---|---|---|
| 1 | `--apply`（一次一槍；預期 S0） | 無界全庫 |
| 2 | 再 `--check`；若 S3 仍 FIRE → 第二槍 `--apply` | 默開 AUTO-LIFT／timer |
| 3 | 終 `--check` 記帳 | 混市場 B3 |

成功尺：S0 breach→0（或明顯降）；S3 有界推進；帳＋log。

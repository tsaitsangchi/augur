---
status: go_accepted
series: s4_models
track: NF-B-KALMAN
date: 2026-08-07
paste: "NF-B-KALMAN-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | H20 | full-core | no-promote | no-serve-swap | hold-#1"
depends_on:
  - audits/NF-B-KALMAN-0A-EXECUTED-20260807.md
viewpoint: 2026-08-07T15:15+08:00
self_reported: true
---

# GO｜NF-B-KALMAN-0b · 全 core＠2026-07-31／H20

```text
NF-B-KALMAN-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply
| asof=2026-07-31 | H20 | full-core | no-promote | no-serve-swap | hold-#1
# Steward：KalmanLocalLevel(log close) vs naive；≠ registry／serve／#14
```

| 網格 | 值 |
|---|---|
| asof | 2026-07-31 |
| H | 20 |
| 宇宙 | core 全量（n≥204） |
| 輸入 | log close · local level |
| 門檻 | mean Kalman hit **>** mean naive |

*go → probe。*

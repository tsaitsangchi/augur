---
status: executed
series: s4_models
track: NF-B-KALMAN
date: 2026-08-07
depends_on:
  - audits/NF-B-KALMAN-0A-GO-20260807.md
  - audits/NF-B-KALMAN-PLAN-ADOPTED-20260807.md
asof_pin: "2026-07-31"
paste: "NF-B-KALMAN-0a-go | FZ/GATE-keep | no-train-prod | hold-#1"
viewpoint: 2026-08-07T15:10+08:00
self_reported: true
---

# EXECUTED｜NF-B-KALMAN-0a · `KalmanLocalLevel`＋selftest

> RC=0 · 零 DB · no-train-prod · 未 registry · hold-#1  
> asof 釘（後續 0b）＝**2026-07-31**

| 項 | 值 |
|---|---|
| class | **`KalmanLocalLevel`**（`UnobservedComponents` · `local level`） |
| 模組 | `src/augur/models/classical_ts.py` |
| selftest | **全通過** |

未做：庫內 0b／registry／serve。

```text
NF-B-KALMAN-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | H20 | no-promote | no-serve-swap | hold-#1
```

*完。*

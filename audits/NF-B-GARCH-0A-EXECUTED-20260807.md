---
status: executed
series: s4_models
track: NF-B-GARCH
date: 2026-08-07
depends_on:
  - audits/NF-B-GARCH-0A-GO-20260807.md
  - audits/NF-B-GARCH-PLAN-ADOPTED-20260807.md
asof_pin: "2026-07-31"
paste: "NF-B-GARCH-0a-go | FZ/GATE-keep | no-train-prod | hold-#1 | no-SIM-apply"
viewpoint: 2026-08-07T16:28+08:00
self_reported: true
---

# EXECUTED｜NF-B-GARCH-0a · `GarchMeanDir`＋selftest

> RC=0 · 預測臂 · **⊥ simulate_*** · 零 DB · 未 registry · hold-#1  
> asof 釘（後續 0b）＝**2026-07-31**

| 項 | 值 |
|---|---|
| class | **`GarchMeanDir`**（ConstantMean＋GARCH(1,1) · 均值路徑） |
| 模組 | `src/augur/models/classical_ts.py` |
| selftest | **全通過** |

未做：庫內 0b／sim 路徑／serve。

```text
NF-B-GARCH-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | H20 | no-promote | no-serve-swap | hold-#1
```

*完。*

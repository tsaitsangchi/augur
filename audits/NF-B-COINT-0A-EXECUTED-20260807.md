---
status: executed
series: s4_models
track: NF-B-COINT
date: 2026-08-07
depends_on:
  - audits/NF-B-COINT-0A-GO-20260807.md
  - audits/NF-B-COINT-PLAN-ADOPTED-20260807.md
asof_pin: "2026-07-31"
paste: "NF-B-COINT-0a-go | FZ/GATE-keep | no-train-prod | hold-#1"
viewpoint: 2026-08-07T15:30+08:00
self_reported: true
---

# EXECUTED｜NF-B-COINT-0a · `CointPairEG`＋selftest

> RC=0 · 零 DB · no-train-prod · 未 registry · ≠可套利 · hold-#1  
> asof 釘（後續 0b）＝**2026-07-31**

| 項 | 值 |
|---|---|
| class | **`CointPairEG`**（Engle–Granger · k=2 · ρ=0.9） |
| 模組 | `src/augur/models/classical_ts.py` |
| selftest | **全通過** |

未做：庫內 0b／registry／serve。

```text
NF-B-COINT-0b-go | FZ/GATE-keep | skip-sync | no-SIM-apply | asof=2026-07-31 | H20 | no-promote | no-serve-swap | hold-#1
```

*完。*

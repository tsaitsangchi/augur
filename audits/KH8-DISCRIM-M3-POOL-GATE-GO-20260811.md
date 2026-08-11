---
status: go
series: local_ai_kh
kind: kh8_m3_pool_gate
date: 2026-08-11
viewpoint: 2026-08-11T08:22+08:00
inventory: audits/KH8-DISCRIM-M3-POOL-GATE-INVENTORY-20260811.md
paste: "KH8-DISCRIM-M3-pool-gate-go | code-gate | no-merge | E-keep | hold-#1"
self_reported: true
layer: "[I]"
---

# GO｜M3 答池闸码 · no-merge

```text
KH8-DISCRIM-M3-pool-gate-go | code-gate | no-merge | E-keep | hold-#1 | FZ/GATE-keep
```

## 准

| # | 做 |
|---|---|
| 1 | 新 `src/augur/knowledge/pool_gate.py`（契约＋`answer_pool_eligible`＋selftest） |
| 2 | 新 `scripts/check_kh8_pool_gate.py`（静扫 retrieve／readout／evidence／auto_lift） |
| 3 | 热路径注释／selftest 引用闸；必要时一行断言 |

## 禁

写／併 `knowhow_evidence_weight` · DROP 影表 · 撤 E · 抬 depth≥8 · 动 B3／serve

*go → EXECUTED。*

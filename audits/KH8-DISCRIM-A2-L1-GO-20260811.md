---
status: go
series: local_ai_kh
kind: kh8_a2_l1
date: 2026-08-11
viewpoint: 2026-08-11T08:26+08:00
spec: reports/augur_kh8_a2_land_design_spec_20260808.md
paste: "KH8-DISCRIM-A2-L1-go | code+selftest | default=legacy | no-write-main | E-keep | hold-#1"
prior_m3: audits/KH8-DISCRIM-M3-POOL-GATE-EXECUTED-20260811.md
self_reported: true
layer: "[I]"
---

# GO｜A2-L1 · 公式入码 · 默认仍 legacy

```text
KH8-DISCRIM-A2-L1-go | code+selftest | default=legacy | no-write-main | E-keep | hold-#1
```

## 准

1. `compute_evidence_weight_legacy`＝现行  
2. `compute_evidence_weight_a2_v1`＝规格 §2.2  
3. `compute_evidence_weight(..., formula=)` 默认 **legacy**  
4. selftest：齐备+1句 A2 **不得 high**；cite_n=0 A2 score≤0.35；legacy 旧预期仍绿  
5. 不写主表、不改 θ、不撤 E

## 禁

默默切默认 A2 · L3 UPDATE · MERGE 影 · depth≥8

*go → EXECUTED。*

---
status: go
series: local_ai_kh
kind: kh8_a2_l2
date: 2026-08-11
viewpoint: 2026-08-11T08:26+08:00
prior_l1: audits/KH8-DISCRIM-A2-L1-EXECUTED-20260811.md
spec: reports/augur_kh8_a2_land_design_spec_20260808.md
paste: "KH8-DISCRIM-A2-L2-go | dry-run | full-pop | no-write-main | E-keep | hold-#1"
self_reported: true
layer: "[I]"
---

# GO｜A2-L2 · dry-run 对拍（入码公式 · 不写主表）

```text
KH8-DISCRIM-A2-L2-go | dry-run | use=A2-v1-fn | no-write-main | E-keep | hold-#1
```

## 准

1. 读主表最新 weight（components／cite_n）  
2. 用 **入码** `compute_evidence_weight_a2_v1` 全库投影 score／band  
3. 对拍 live legacy band／disc；结果写 `/tmp`＋audit  
4. **零** UPDATE／INSERT `knowhow_evidence_weight`

## 禁

切默认 A2 · L3 · MERGE · 撤 E · 抬 depth≥8

*go → EXECUTED。*

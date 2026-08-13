---
status: go
series: local_ai_kh
kind: kh8_a2_l3
date: 2026-08-13
viewpoint: 2026-08-13T10:17+08:00
spec: reports/augur_kh8_a2_land_design_spec_20260808.md
prior_l2: audits/KH8-DISCRIM-A2-L2-EXECUTED-20260811.md
plan_first: reports/augur_kh8_discrim_plan_first_20260813.md
paste: "KH8-DISCRIM-A2-L3-go | dual-explicit | no-fake-depth8 | E-keep-until-ok | rollback-SQL-ready"
rollback_sql: /tmp/kh8-a2-l3/rollback.sql
self_reported: true
layer: "[I]"
---

# GO｜KH8-DISCRIM-A2-L3 · 主表寫入 A2-v1（雙明示）

```text
KH8-DISCRIM-A2-L3-go | dual-explicit | no-fake-depth8 | E-keep-until-ok | rollback-SQL-ready
# Steward 明示 paste＝第二明示；本 GO＝第一明示
```

## 准

1. 對最新 `knowhow_evidence_weight` 逐 item 以 **A2-v1** 重算並 **INSERT** 新列（`run_id=kh8:a2-l3:20260813`）  
2. **不改** `DEFAULT_FORMULA`（仍 legacy）；**不改** `MIN_MINORITY_MASS`  
3. 寫 rollback：`DELETE FROM knowhow_evidence_weight WHERE run_id='kh8:a2-l3:20260813'`  
4. L4：`population_discriminates` 複測——**預期仍 ok=False（誠實）**  
5. R2：`python -m augur.knowledge.evidence --selftest`

## 禁

放寬 θ · 撤 E · 宣稱 depth≥8 · MERGE 影 · 切默認公式鍵（僅本批寫入帶 A2 components）

*go → FIRED／EXECUTED。*

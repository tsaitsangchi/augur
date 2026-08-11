---
status: executed
series: schema
open_problem: "r12 #19"
date: 2026-08-07
depends_on:
  - audits/SCHEMA-FAMILY-CHK-ALTER-GO-20260807.md
log: /tmp/schema-family-chk-20260807/alter.log
paste: "SCHEMA-FAMILY-CHK-alter-go | FZ/GATE-keep | no-promote | hold-#1 | ADD-only=…"
viewpoint: 2026-08-07T14:16+08:00
self_reported: true
---

# EXECUTED｜SCHEMA-FAMILY-CHK-alter · ADD-only · 2026-08-07

> **GO** 已執行 · RC=0 · **no-promote** · 未 register orphans · 未 SERVE-SWAP · hold-#1

## 變更

| | |
|---|---|
| DROP | `model_family_chk`（舊九字面） |
| ADD | 同名約束＝舊九＋**RankXGB／Cat／RF／SVM／KNN／MLP** |
| registry_rows | **32**（不變；無新列） |
| rollback INSERT probe | `RankRF` 過 CHK → **ROLLBACK**（零残留） |

## 仍未做（須另句）

- orphan joblib → `model_registry` 正式登錄  
- promote／產線換挑戰族  
- 撤 NF-pause／改 dgate  

可選下一句：`SCHEMA-FAMILY-CHK-register-orphans-go | … | no-promote | no-serve-swap`

*完。*

---
status: go
series: struct
kind: cycle_break
ring: audit-core
date: 2026-08-08
plan: reports/augur_struct_cycle_break_go_plan_20260808.md
prior: audits/STRUCT-CYCLE-EXPLORE-EXECUTED-20260807.md
paste: "STRUCT-CYCLE-BREAK-go | ring=audit-core | FZ/GATE-keep | zero-predict | one-ring"
self_reported: true
layer: "[I]"
---

# GO｜STRUCT-CYCLE-BREAK · ring=audit-core · 2026-08-08

```text
STRUCT-CYCLE-BREAK-go | ring=audit-core | FZ/GATE-keep | zero-predict | one-ring
# 斷：core.generic_schema → audit.reconcile（延遲 _norm）
# 改：_norm SSOT → core.generic_schema；reconcile 再匯出保 BC
```

## 授權

Steward AskQuestion：`next=struct` → `ring=audit-core`。

## 准許

| 項 | 內容 |
|---|---|
| 改碼面 | `src/augur/core/generic_schema.py`、`src/augur/audit/reconcile.py`（`_norm` 搬家＋再匯出） |
| 驗 | `--selftest`×2；`explore_struct_cycles` 確認 `audit`↔`core` 2-cycle **消失** |
| 保 | `reconcile._norm` 呼叫點語意不變（tests／freeze hash） |

## 禁止

- 同窗動 `audit`↔`features`／advisor 環  
- 改 `predict_asof`／B3／serve／prodset  
- 另實作第二套 _norm 口徑  

*go。*

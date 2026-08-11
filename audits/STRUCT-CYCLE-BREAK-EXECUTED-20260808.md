---
status: executed
series: struct
kind: cycle_break
ring: audit-core
date: 2026-08-08
viewpoint: 2026-08-08T11:05+08:00
go: audits/STRUCT-CYCLE-BREAK-GO-20260808.md
plan: reports/augur_struct_cycle_break_go_plan_20260808.md
paste: "STRUCT-CYCLE-BREAK-go | ring=audit-core | FZ/GATE-keep | zero-predict | one-ring"
self_reported: true
layer: "[I]"
---

# EXECUTED｜STRUCT-CYCLE-BREAK · ring=audit-core · 2026-08-08

```text
STRUCT-CYCLE-BREAK-go | ring=audit-core | FZ/GATE-keep | zero-predict | one-ring
```

## 斷法

| 前 | 後 |
|---|---|
| `core.generic_schema` **延遲** `from augur.audit.reconcile import _norm` | `_norm` **SSOT** 住 `generic_schema` |
| AST 2-cycle `audit` ↔ `core` | `audit`→`core` 單向；**core↛audit** |
| | `reconcile._norm = generic_schema._norm`（BC） |

改檔：`src/augur/core/generic_schema.py`、`src/augur/audit/reconcile.py`。

## 驗收

| 測 | 結果 |
|---|---|
| `python -m augur.core.generic_schema --selftest` | **全通過**（含 `_supersessions`，不再 skip 因 audit） |
| `python -m augur.audit.reconcile --selftest` | **全通過** |
| `pytest tests/test_reconcile.py` | **16 passed** |
| `explore_struct_cycles --run` | `audit ↔ core` **消失**；剩餘 2-cycles＝4（advisor×2／audit↔features／knowledge↔philosophy） |

## 不做

- 其他環；predict／B3／serve／prodset  
- 第二套 _norm 口徑  

*完。[I]*

---
status: go
series: struct
kind: cycle_break
ring: audit-features
date: 2026-08-08
plan: reports/augur_struct_cycle_break_go_plan_20260808.md
prior_ring: audits/STRUCT-CYCLE-BREAK-EXECUTED-20260808.md
paste: "STRUCT-CYCLE-BREAK-go | ring=audit-features | FZ/GATE-keep | zero-predict | one-ring"
self_reported: true
layer: "[I]"
---

# GO｜STRUCT-CYCLE-BREAK · ring=audit-features · 2026-08-08

```text
STRUCT-CYCLE-BREAK-go | ring=audit-features | FZ/GATE-keep | zero-predict | one-ring
# 斷：audit.reconcile.attest_route → features.macro（延遲 vintage_map）
# 改：vintage_map 由呼叫端注入；features→audit（候選寫／panel）單向保留
```

## 授權

Steward AskQuestion：`next=audit-features` → `confirm=go`。

## 准許

| 項 | 內容 |
|---|---|
| 改碼 | `audit/reconcile.py`（`attest_route(..., vintage_map=)`）；腳本注入點 |
| 腳本 | `daily_maintenance.py`／`full_universe_attest.py` 傳 `macro.vintage_map()` |
| 驗 | selftest；`explore_struct_cycles`：`audit`↔`features` **消失** |

## 禁止

- 同窗動 advisor／knowledge 環  
- 挪走 `feature_candidate` 落地表義務（features→audit 寫 staging **保留**）  
- predict／B3／serve  

*go。*

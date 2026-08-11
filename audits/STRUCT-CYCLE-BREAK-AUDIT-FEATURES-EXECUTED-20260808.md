---
status: executed
series: struct
kind: cycle_break
ring: audit-features
date: 2026-08-08
viewpoint: 2026-08-08T11:25+08:00
go: audits/STRUCT-CYCLE-BREAK-AUDIT-FEATURES-GO-20260808.md
prior_ring: audits/STRUCT-CYCLE-BREAK-EXECUTED-20260808.md
paste: "STRUCT-CYCLE-BREAK-go | ring=audit-features | FZ/GATE-keep | zero-predict | one-ring"
self_reported: true
layer: "[I]"
---

# EXECUTED｜STRUCT-CYCLE-BREAK · ring=audit-features · 2026-08-08

```text
STRUCT-CYCLE-BREAK-go | ring=audit-features | FZ/GATE-keep | zero-predict | one-ring
```

## 斷法

| 前 | 後 |
|---|---|
| `attest_route` 內 `from augur.features import macro` | **刪**；`vintage_map=` 呼叫端注入 |
| AST `audit` ↔ `features` | `features`→`audit` **單向**（候選 staging／panel 保留） |
| | `daily_maintenance`／`full_universe_attest` 傳 `macro.vintage_map()` |

## 驗收

| 測 | 結果 |
|---|---|
| `reconcile --selftest` | 全通過（含 FRED 缺 map fail-loud） |
| `explore_struct_cycles --run` | `audit`↔`features` **消失**；剩餘 2-cycles＝**3**（advisor↔delib／advisor↔knowledge／knowledge↔philosophy） |

## 不做

- advisor 三角；predict／B3／serve  

*完。[I]*

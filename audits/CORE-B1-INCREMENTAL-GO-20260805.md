---
status: executed
series: daily_asof_ops
paste: CORE-B1-INCREMENTAL-go
scope: B1a+B1c
plan: reports/augur_core_universe_b1_incremental_plan_20260805.md
executed: audits/CORE-B1-INCREMENTAL-EXECUTED-20260805.md
---

# GO｜CORE-B1-INCREMENTAL · 2026-08-05

> **授權**：Steward 明示 `CORE-B1-INCREMENTAL-go` ＋ AskQuestion `b1_scope` → **`b1a_c`**  
> **✅ EXECUTED**：`audits/CORE-B1-INCREMENTAL-EXECUTED-20260805.md`  
> paste（已消費）：

```text
CORE-B1-INCREMENTAL-go | FZ/GATE-keep | skip-sync | no-SIM-apply
# scope: B1a upsert-D + B1c dual-path (--incremental / --full-rebuild)
# full-rebuild retained; contrast arm @D; no cron; no core-definition change
```

## 邊界

| 是 | 否 |
|---|---|
| `build_universe_asof_incremental`；CLI 旗標 | 改完整度／流動性定義 |
| 同 D 集合對照（incremental 算法 vs 現表／全量公式） | 默設改成砍全量路徑 |
| runbook 註「日更偏好 incremental」 | cron／timer／sim-apply／sync |

*已執行。*

---
status: executed
series: daily_asof_ops
go: audits/CORE-B1-INCREMENTAL-GO-20260805.md
plan: reports/augur_core_universe_b1_incremental_plan_20260805.md
scope: B1a+B1c
self_reported: true
---

# EXECUTED｜CORE-B1-INCREMENTAL · 2026-08-05

> **GO**：`CORE-B1-INCREMENTAL-go`（Steward；`b1_scope=b1a_c`）  
> **FZ/GATE-keep · skip-sync · no-SIM-apply · no cron**  
> **self-reported（#32a）**

## 1. 碼交付

| 層 | 變更 |
|---|---|
| `src/augur/universe/core_gate.py` | `build_universe_asof_incremental`；`compute_core_at_asof`／`read_core_at_asof`；`assert_incremental_preconditions`；`validate_asof_cli_flags`；全量路徑保留；selftest＋B1 旗標 |
| `scripts/build_core_universe.py` | `--incremental`／`--full-rebuild`／`--asof-date`／`--asof-compare-only`／`--skip-pan-hist` |
| runbook | §2 日更偏好 incremental（`augur_daily_asof_predict_emit_runbook_20260805.md`） |

## 2. 自測

`python -m augur.universe.core_gate --selftest` → **全通過**（含 flag 互斥／截斷）。

## 3. 對照臂＠2026-08-04

參數：`--since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial`；panels=**108**（2014-12-31..2026-08-04）；feats=**38**。

| 步 | 公式 n | 表 n | 差分 |
|---|---:|---:|---|
| 增量**前** `--asof-compare-only` | **283** | **204** | 只在公式 **79**（表落後於當前公式／料） |
| 增量**後**（再 compare） | **283** | **283** | **∅ PASS** |

說明：午前全量 meta（`scope=asof`＠10:55）`core_count=204` 同窗同 feats；晚間公式＝283——**資料面已變**（非改定義）。B1 驗收尺＝**寫入＝當前公式**，非「凍結午前 204」。

## 4. 增量寫入

```text
--asof --incremental --asof-date 2026-08-04 --skip-pan-hist
→ as-of incremental＠2026-08-04: 寫入 283 股；後對照差分∅ PASS
elapsed ≈ 11.7s（compare-only ≈ 36s；全量估 10–15min）
```

| 護欄 | 結果 |
|---|---|
| meta 新列 | `scope=asof_incr` panel_end=2026-08-04 core_count=**283** |
| asof 日曆數 | 仍 **108** 日（2014-12-31..2026-08-04）——**未**全表 DELETE |
| `as_of_date < D` 列數 | **36,601** 仍在 |
| 樣本 | 2014-12-31=701；2026-06-30=225；2026-08-04=**283** |
| fail-closed | `D=2099-01-01` → ValueError（不在 panel 全集） |

## 5. 不做

cron · 改完整度定義 · 刪全量路徑 · sim-apply · sync · 默授 timer

## 6. 日更用法（已入 runbook）

```bash
venv/bin/python scripts/build_core_universe.py \
  --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial \
  --asof --incremental --asof-date <D> --skip-pan-hist
```

空表／缺中間 panel → 仍用 `--asof` 或 `--full-rebuild`。

*完。*

---
status: executed
series: daily_asof_ops
paste: DAILY-ASOF-B3-SHELL-go
plan: reports/augur_daily_asof_b3_orchestrator_plan_20260805.md
executed: audits/DAILY-ASOF-B3-SHELL-EXECUTED-20260805.md
---

# GO｜DAILY-ASOF-B3-SHELL · 2026-08-05

> **授權**：Steward 明示 `DAILY-ASOF-B3-SHELL-go` ＋ AskQuestion `impl` → **`bash_shell`**  
> paste：

```text
DAILY-ASOF-B3-SHELL-go | FZ/GATE-keep | skip-sync | no-SIM-apply | no-cron
# deliverable: scripts/run_daily_asof_predict.sh + --dry-plan; B1 incremental; no timer
```

## 範圍

| 是 | 否 |
|---|---|
| bash 薄殼＋dry-plan；RC 匯總；價&lt;D 整鏈 skip | cron／systemd／install_cron |
| core 預設 `--incremental`；`--core-full` 可選 | 殼內 sync／P6 fit／sim-apply |
| dry-plan 煙測 EXECUTED | 默授真跑全鏈（真跑可另觸或同殼手跑） |

*✅ EXECUTED（dry-plan／selftest；真跑另觸）。*

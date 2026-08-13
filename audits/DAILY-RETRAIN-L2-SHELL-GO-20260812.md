---
status: go
series: s4_retrain
track: DAILY-RETRAIN-L2-ALL-RANK
phase: P1
date: 2026-08-12
viewpoint: 2026-08-12T14:20+08:00
plan: reports/augur_daily_retrain_l2_all_rank_plan_20260812.md
paste: "DAILY-RETRAIN-L2-SHELL-go | boundary=A | FZ/GATE-keep | no-promote | NF-pause | no-SIM-apply | no-cron | skip-sync | dry-plan+selftest"
self_reported: true
layer: "[I]"
---

# GO｜DAILY-RETRAIN-L2 · P1 薄殼

| 准 | 禁 |
|---|---|
| 實作 `scripts/run_daily_retrain_l2_all_rank.sh` | 裝 cron／systemd |
| `--dry-plan` 印滿 §3 步；`--selftest` 綠 | 默 `--apply` 寫庫（本 GO **不含**真訓） |
| 邊界 A：Ridge×5＋chal×8＋repredict 20/60 編排 | NF／Daily*／promote／sync／sim-apply |

成功尺：`--selftest` RC=0；`--dry-plan --date <已有價日>` 列出 train／predict／emit 且零寫庫。

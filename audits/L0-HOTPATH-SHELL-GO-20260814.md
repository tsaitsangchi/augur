---
status: go
series: market_ops
track: L0-HOTPATH
phase: P1
date: 2026-08-14
viewpoint: 2026-08-14T09:16+08:00
plan: reports/augur_l0_hotpath_daily_plan_20260814.md
paste: "L0-HOTPATH-SHELL-go | A+C+D | TRI-only-dim | stale-guard | FZ/GATE-keep | no-93 | no-cron | ≠B3 ≠L2 | dry-plan+selftest"
self_reported: true
layer: "[I]"
---

# GO｜L0-HOTPATH · P1 薄殼

| 准 | 禁 |
|---|---|
| 實作 `scripts/run_l0_hotpath_daily.sh` | 裝 cron／改 arena 20:00／`install_cron.sh` |
| `--dry-plan` 印滿 A→C→D；`--selftest` 綠 | 默 `--apply` 寫庫（本 GO **不含**真抓） |
| stale-guard；TRI 窄窗 dim-sync | 93 表；`AUGUR_DIM_SYNC=1`；B3／L2 |

成功尺：`--selftest` RC=0；`--date 2026-08-13 --dry-plan` 列出核 A／TRI／macro 且零寫庫。

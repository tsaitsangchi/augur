---
status: go
series: market_ops
track: L0-HOTPATH
phase: P2
date: 2026-08-14
viewpoint: 2026-08-14T09:21+08:00
D: "2026-08-14"
plan: reports/augur_l0_hotpath_daily_plan_20260814.md
shell: scripts/run_l0_hotpath_daily.sh
paste: "L0-HOTPATH-APPLY-go | D=2026-08-14 | A+C+D | TRI-only-dim | stale-guard | no-extended | no-cron | ≠B3 ≠L2"
self_reported: true
layer: "[I]"
---

# GO｜L0-HOTPATH · P2 真抓

未另指定 D → 台北今日 **2026-08-14**（交易日；09:21 盤中，FinMind 可能尚無收盤列＝誠實 0 列，不假 B3）。

| 准 | 禁 |
|---|---|
| `run_l0_hotpath_daily.sh --date 2026-08-14 --apply`（核 A＋TRI＋FRED） | `--extended`；B3／L2；cron；93 表 |
| stale-guard；掉級／403 → 停 | 價未到仍開 B3 |

成功尺：殼 RC 誠實；EXECUTED 列出 PriceAdj(TAIEX) 與核 A tip；`PriceAdj < D` 則黃帳。

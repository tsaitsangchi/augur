---
status: go
series: kh_ops
track: KH-S0-APPLY
date: 2026-08-18
viewpoint: 2026-08-18T09:05+08:00
plan: reports/augur_opt_stepwise_all_problems_r18_20260817.md
wp: WP-K0
paste: "KH-S0-apply-go | drain KH0 up_to=0 limit=218 | no-lift>KH2 | 避開 B3"
check_live: "S0 FIRE kh0_breach=218; S1 FIRE delta=5; S3 FIRE zh lag=2"
self_reported: true
layer: "[I]"
---

# GO｜KH S0 drain（ingest-trigger --apply 一槍）

Steward 09:05 明示。B3 未開火（價頂仍 08-17）。鎖其餘項不變。

| 准 | 禁 |
|---|---|
| `python scripts/kh_ingest_trigger.py --apply` 一槍 | 第二槍 S3（本 paste 未授） |
| S0：`--phase advance --up-to 0 --limit 218` | 抬 >KH2；`--up-to` >0 |
| 終 `--check` 記帳 | AUTO-LIFT；KH8；市場 B3；假 B3＠08-18 |

成功尺：S0 kh0_breach 明顯下降或歸 0；未抬層；未碰 standing／promote。

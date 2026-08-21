---
status: go
series: kh_ops
track: KH-S0-APPLY
date: 2026-08-21
viewpoint: 2026-08-21T14:55+08:00
plan: reports/augur_opt_stepwise_all_problems_r22_20260821.md
wp: WP-K0
paste: "KH-S0-apply-go"
check_live: "S0 FIRE kh0_breach=63; S1–S3 ok（本窗 --check）"
self_reported: true
layer: "[I]"
---

# GO｜KH S0 drain（ingest-trigger --apply 一槍）

Steward 14:55 明示 `KH-S0-apply-go`。市場 B3 未開火（價頂仍 08-20；日曆 08-21＝假 B3）。鎖其餘項不變。

| 准 | 禁 |
|---|---|
| `python scripts/kh_ingest_trigger.py --apply` 一槍 | 第二槍 S3／S1／抬層（本 paste 未授） |
| S0：`--phase advance --up-to 0 --limit 63` | 抬 >KH2；`--up-to` >0 |
| 終 `--check` 記帳 | AUTO-LIFT；KH8；市場 B3；假 B3＠08-21；改 L0 |

成功尺：S0 kh0_breach 63→0（或明顯下降）；未抬層；未碰 standing／promote。

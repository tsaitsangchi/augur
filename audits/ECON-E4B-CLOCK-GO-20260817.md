---
status: go
series: econ_establishment
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T09:47+08:00
paste: "E4b-clock-go | origin=2026-08-14 | h=60 | read-only | no-realized-pnl"
plan: reports/augur_econ_prove_edge_plan_r17_20260817.md
self_reported: true
layer: "[I]"
---

# GO｜E4b live OOS 鐘

## 准

- 唯讀。origin＝2026-08-14。H＝60 主鐘。
- 印 already_realized_nonoverlap／next_due_date／WAIT。
- 非重疊＝`h × 1.45 × 0.9` 日曆日間距（與 E3／閘 criteria 同尺）。
- 進出場＝`label._entry_exit`（t+1、持有 H 交易日）。
- 已實現＝PriceAdj tip ≥ exit。H20 只披露、不復活。

## 禁

- 算實現報酬／淨值／Sharpe
- 把每日重疊出門當獨立 T
- 用 08-15／16／17 當 as-of
- 寫 ledger／prodset／verdict／evaluate

---
status: fired
series: s1s5_loop
track: RIDGE-THEN-PB-LONG-MA10DN
product_id: MA-STACK-DN-v1
date: 2026-08-21
go: audits/RIDGE-THEN-PB-LONG-MA10DN-GO-20260821.md
layer: "[I]"
self_reported: true
---

# FIRED｜已完成八窗日做多均線倒排＋均價差≤10% 收盤買進

`scripts/run_ridge_then_pb_long_ma10dn.py --apply --from 2026-08-20 --until 2026-08-20`

鎖：`/tmp/augur_ridge_then_pb_long_ma10dn.lock`（≠ hist-ridge-wf、≠ ma10／ma20）

表：`ridge_then_pb_long_ma10dn_asof` / `ridge_then_pb_long_ma10dn_row` / `ridge_then_pb_long_ma10dn_buy`

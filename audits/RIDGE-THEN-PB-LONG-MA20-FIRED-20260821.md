---
status: fired
series: s1s5_loop
track: RIDGE-THEN-PB-LONG-MA20
product_id: MA-STACK-v1
phase: long-close-fill-ma20
date: 2026-08-21
layer: "[I]"
self_reported: true
---

# FIRED｜已完成八窗日做多均線排列＋均價差≤20% 收盤買進

`scripts/run_ridge_then_pb_long_ma20.py --apply --watch`

鎖：`/tmp/augur_ridge_then_pb_long_ma20.lock`（≠ hist-ridge-wf、≠ ma10）
進度：`audits/RIDGE-THEN-PB-LONG-MA20-PROGRESS.json`
表：`ridge_then_pb_long_ma20_asof` / `ridge_then_pb_long_ma20_row` / `ridge_then_pb_long_ma20_buy`

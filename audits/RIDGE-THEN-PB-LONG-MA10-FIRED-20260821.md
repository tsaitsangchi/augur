---
status: fired
series: s1s5_loop
track: RIDGE-THEN-PB-LONG-MA10
product_id: MA-STACK-v1
phase: long-close-fill-ma10
date: 2026-08-21
layer: "[I]"
self_reported: true
---

# FIRED｜已完成八窗日做多均線排列＋均價差≤10% 收盤買進

`scripts/run_ridge_then_pb_long_ma10.py --apply --watch`

鎖：`/tmp/augur_ridge_then_pb_long_ma10.lock`（≠ hist-ridge-wf、≠ long-buy v1、≠ w10）
進度：`audits/RIDGE-THEN-PB-LONG-MA10-PROGRESS.json`
表：`ridge_then_pb_long_ma10_asof` / `ridge_then_pb_long_ma10_row` / `ridge_then_pb_long_ma10_buy`

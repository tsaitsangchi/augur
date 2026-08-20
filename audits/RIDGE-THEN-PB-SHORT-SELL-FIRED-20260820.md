---
status: fired
series: s1s5_loop
track: RIDGE-THEN-PB-SHORT-SELL
product_id: RIDGE-THEN-PB-v1
phase: short-close-fill
date: 2026-08-20
layer: "[I]"
self_reported: true
---

# FIRED｜已完成八窗日做空收盤賣出

`scripts/run_ridge_then_pb_short_sell.py --apply --watch`

鎖：`/tmp/augur_ridge_then_pb_short.lock`（≠ hist-ridge-wf、≠ long-buy）
進度：`audits/RIDGE-THEN-PB-SHORT-SELL-PROGRESS.json`
表：`ridge_then_pb_short_asof` / `ridge_then_pb_short_row` / `ridge_then_pb_short_sell`
做空欄＝條件排序，不是下單、不是可融券可成交。

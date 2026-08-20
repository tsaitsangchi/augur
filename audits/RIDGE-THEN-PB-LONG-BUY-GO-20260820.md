---
status: go
series: s1s5_loop
track: RIDGE-THEN-PB-LONG-BUY
product_id: RIDGE-THEN-PB-v1
phase: long-close-fill
date: 2026-08-20
from: "2014-01-02"
until: "2026-08-19"
layer: "[I]"
self_reported: true
paste: 可以執行另一排程來執行已完成的模型進行該交易日。符合做多：先取相對強 Top10 當池子，不要因為還沒回撤就剔除。過齊才可當進場條件；以該交易日收盤價買進寫入 table。
---

# GO｜已完成八窗日做多收盤買進

對同日 RankRidge 八窗已齊的交易日：相對強 Top10 當池不剔除 → 回撤近→遠 → 過齊才標可當進場條件，其餘等回撤。過齊者寫入 `ridge_then_pb_long_buy`，買進價＝該日還原收盤。不拿 HIST-RIDGE-WF 鎖、不改 standing、不假 B3＠08-20。

---
status: go
series: s1s5_loop
track: RIDGE-THEN-PB-LONG-W10
product_id: RIDGE-THEN-PB-v1
phase: long-close-fill-band10
date: 2026-08-21
from: "2014-01-02"
until: "2026-08-19"
layer: "[I]"
self_reported: true
paste: 可以執行另一排程來執行已完成的模型進行該交易日。符合做多：先取相對強 Top10 當池子，不要因為還沒回撤就剔除。{"5": false, "10": true, ...}。而H5…H240的股價差異上下限均在10%內，過齊做多進場閘的才標可當進場條件。記錄該日收盤買進。
---

# GO｜已完成八窗日做多 ±10% 窗幅收盤買進

對同日 RankRidge 八窗已齊的交易日：相對強 Top10 當池不剔除（H5 未也不踢）→ 過齊做多四閘且八窗路徑％皆在 ±10% 才標可當進場條件。過齊者寫入 `ridge_then_pb_long_w10_buy`，買進價＝該日還原收盤。不覆寫 `ridge_then_pb_long_buy`。不拿 HIST-RIDGE-WF 鎖、不改 standing、不假 B3＠08-20／08-21。

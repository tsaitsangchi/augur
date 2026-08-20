---
status: go
series: s1s5_loop
track: RIDGE-THEN-PB-SHORT-SELL
product_id: RIDGE-THEN-PB-v1
phase: short-close-fill
date: 2026-08-20
from: "2014-01-02"
until: "2026-08-19"
layer: "[I]"
self_reported: true
paste: 可以執行另一排程來執行已完成的模型進行該交易日。符合做空：先取相對弱 Top10 當池子，不要因為還沒反彈就剔除。過齊才可當進場條件；以該交易日收盤價賣出寫入 table。做空欄不是下單、不是可融券。
---

# GO｜已完成八窗日做空收盤賣出

對同日 RankRidge 八窗已齊的交易日：相對弱 Top10 當池不剔除 → 反彈近→遠 → 過齊才標可當進場條件，其餘等反彈。過齊者寫入 `ridge_then_pb_short_sell`，賣出價＝該日還原收盤。做空≠下單≠可融券。不拿 HIST-RIDGE-WF 鎖、不拿做多收盤鎖、不改 standing、不假 B3＠08-20。

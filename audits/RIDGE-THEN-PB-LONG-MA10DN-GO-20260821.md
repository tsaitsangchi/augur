---
status: go
series: s1s5_loop
track: RIDGE-THEN-PB-LONG-MA10DN
product_id: MA-STACK-DN-v1
phase: long-close-fill-ma10dn
date: 2026-08-21
from: "2014-01-02"
until: "2026-08-20"
layer: "[I]"
self_reported: true
paste: 可以執行另一排程來執行已完成的模型進行該交易日。符合做多：先取相對強 Top10 當池子，不要因為還沒回撤就剔除。5天均價<10天均價<…<240天均價。各平均價格差異在10%範圍內判定為可進場條件。該日收盤買進寫入 table。
---

# GO｜已完成八窗日做多均線倒排＋均價差≤10% 收盤買進

對同日 RankRidge 八窗已齊的交易日：相對強 Top10 當池不剔除 → SMA5<SMA10<SMA20<SMA40<SMA60<SMA90<SMA120<SMA240 且八條均價 (最高−最低)/最低 ≤10% 才標可當進場條件。過齊者寫入 `ridge_then_pb_long_ma10dn_buy`，買進價＝該日還原收盤。不覆寫 `ridge_then_pb_long_ma10_buy`／`_ma20_buy`。不拿 HIST-RIDGE-WF 鎖、不改 standing、不跑 08-21。

---
status: go
series: s1s5_loop
track: RIDGE-THEN-PB-LONG-MA10HK
product_id: MA-STACK-HOOK-v1
phase: long-close-fill-ma10hk
date: 2026-08-21
from: "2014-01-02"
until: "2026-08-20"
layer: "[I]"
self_reported: true
paste: 可以執行另一排程…5天均價>10天均價，另外10天均價<20<…<240。各平均價格差異在10%範圍內。該日收盤買進寫入 table。要接著開 watch。
---

# GO｜已完成八窗日做多鉤形均線＋均價差≤10% 收盤買進

相對強 Top10 當池不剔除 → SMA5>SMA10 且 SMA10<SMA20<SMA40<SMA60<SMA90<SMA120<SMA240 且八條均價差 ≤10% 才可當進場條件。過齊寫入 `ridge_then_pb_long_ma10hk_buy`。不覆寫 ma10／ma20／ma10dn。不拿 HIST-RIDGE-WF 鎖、不跑 08-21。

---
status: executed
series: s1s5_loop
track: RIDGE-THEN-PB-LONG-MA10HK
product_id: MA-STACK-HOOK-v1
date: 2026-08-21
go: audits/RIDGE-THEN-PB-LONG-MA10HK-GO-20260821.md
fired: audits/RIDGE-THEN-PB-LONG-MA10HK-FIRED-20260821.md
layer: "[I]"
self_reported: true
---

# EXECUTED｜做多鉤形均線＋均價差≤10%（價頂 08-20 已入帳）

價頂 **2026-08-20** 相對強 Top10 全列保留（不因未回撤剔除）。**0** 檔過 SMA5>SMA10 且 SMA10<…<SMA240 且均價差≤10%。`ridge_then_pb_long_ma10hk_buy` 當日 0 列（誠實空）。池寫入 `ridge_then_pb_long_ma10hk_row`。不覆寫 ma10／ma20／ma10dn。不跑 08-21。

Watch：`scripts/run_ridge_then_pb_long_ma10hk.py --apply --watch --from 2014-01-02 --interval 90`（pid 961108；鎖 `/tmp/augur_ridge_then_pb_long_ma10hk.lock`；不拿 WF 鎖）。已入帳 08-20，待補約 560 個八窗已齊日。

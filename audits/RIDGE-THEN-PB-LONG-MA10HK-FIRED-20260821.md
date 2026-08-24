---
status: fired
series: s1s5_loop
track: RIDGE-THEN-PB-LONG-MA10HK
product_id: MA-STACK-HOOK-v1
phase: long-close-fill-ma10hk
date: 2026-08-21
from: "2014-01-02"
until: "2026-08-20"
layer: "[I]"
self_reported: true
---

# FIRED｜MA-STACK-HOOK-v1 收盤買進

```
python scripts/run_ridge_then_pb_long_ma10hk.py --selftest
python scripts/run_ridge_then_pb_long_ma10hk.py --apply --from 2026-08-20 --until 2026-08-20
nohup python scripts/run_ridge_then_pb_long_ma10hk.py --apply --watch --from 2014-01-02 --interval 90
```

鎖 `/tmp/augur_ridge_then_pb_long_ma10hk.lock`。不碰 `/tmp/augur_hist_ridge_wf.lock`。不跑 08-21。

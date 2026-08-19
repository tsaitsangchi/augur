---
status: executed
series: s4_s5_verify
track: RankRidge-8H
date: 2026-08-19
viewpoint: 2026-08-19T13:44+08:00
asof: "2026-08-18"
price_max: "2026-08-18"
calendar_today: "2026-08-19"
kind: last_trading_day_ridge_8h
dry_run: true
wrote_prediction_values: false
standing_unchanged: true
family: RankRidge
horizons: [5, 10, 20, 40, 60, 90, 120, 240]
all_8_present: true
n_scored: 286
dropped_missing_window: 0
json: audits/RIDGE-8H-LAST-TD-0818.json
fake_b3_0819: rc=3
self_reported: true
layer: "[I]"
---

# EXECUTED｜最後交易日 RankRidge 八窗（缺一窗則停）

人話：用庫裡最後一盤還原價，不是日曆今天。日曆 08-19＝假 B3。價頂 **2026-08-18**。八窗模型 asof_snapshot 皆＝08-18。dry-run 未寫 `prediction_values`。standing 仍 H20+H60。score ≠ 報酬％。

286 檔八窗皆有，0 檔因缺窗被丟。均分 Top10 與先前 Ridge 池同序。

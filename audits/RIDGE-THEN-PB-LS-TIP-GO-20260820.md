---
status: go
series: s4_s5_verify
track: RIDGE-THEN-PB
date: 2026-08-20
viewpoint: 2026-08-20T07:55+08:00
product_id: RIDGE-THEN-PB-v1
shell: scripts/probe_ridge_then_pb.py
asof: "2026-08-19"
price_max: "2026-08-19"
paste: "請用最後交易日（庫裡最後一盤還原價，不是日曆今天）的 RankRidge。八窗分數都要有。做多…做空…"
self_reported: true
layer: "[I]"
---

# GO｜RIDGE-THEN-PB 做多＋做空＠最後交易日

asof＝`check_asof_ready --latest-date`＝**2026-08-19**（庫裡最後一盤還原價）。日曆 08-20＝假 B3（rc=3）。

| 准 | 禁 |
|---|---|
| RankRidge 八窗均分；相對強／弱 Top10 當池不剔除 | 假 B3＠08-20 |
| 回撤／反彈近→遠；過齊才「可當進場條件」 | 寫 `prediction_values`；promote |
| 列出代號、名稱、八窗分數 | 做空當可融券／可成交 |
| dry-run | 改 standing 20,60 |

score ≠ 漲跌幅％。觀察≠進場。

---
status: go
series: s4_s5_verify
track: RIDGE-THEN-PB
date: 2026-08-19
viewpoint: 2026-08-19T15:25+08:00
product_id: RIDGE-THEN-PB-v1
shell: scripts/probe_ridge_then_pb.py
paste: "請用最後交易日…RankRidge。八窗分數都要有。做多…做空…"
self_reported: true
layer: "[I]"
---

# GO｜RIDGE-THEN-PB 做多＋做空＠最後交易日

asof＝`check_asof_ready --latest-date`（庫裡最後一盤還原價，不是日曆今天）。

| 准 | 禁 |
|---|---|
| RankRidge 八窗均分；相對強／弱 Top10 當池不剔除 | 假 B3＠08-19 |
| 回撤／反彈近→遠；過齊才「可當進場條件」 | 寫 `prediction_values`；promote |
| 列出代號、名稱、八窗分數 | 做空當可融券／可成交 |
| dry-run | 改 standing 20,60 |

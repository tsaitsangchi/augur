---
status: executed
series: s4_s5_verify
track: UP-PULL
date: 2026-08-19
viewpoint: 2026-08-19T10:16+08:00
asof: "2026-08-18"
shell: scripts/probe_ridge_then_pb.py
json: /tmp/ridge-then-pb-2026-08-18.json
paste: "最後交易日 RankRidge 相對強 Top10 當池，依回撤近→遠"
n_entry: 0
n_wait: 10
wrote_prediction_values: false
selftest: green
self_reported: true
layer: "[I]"
---

# EXECUTED｜RIDGE-THEN-PB＠2026-08-18

人話 GO。池＝RankRidge 八窗均分相對強 10 檔，不剔除。序＝距回撤帶、再短窗仍漲。零寫 `prediction_values`。standing 未改。`--date 2026-08-19` → rc=3。

## 答

- **可當進場條件＝0**；10 檔皆「等回撤，不是進場」。
- 最近：聯發科（回撤帶內，H10 仍 +0.5%）、奇鋐（帶內但短窗仍大漲）。
- 最遠：厚生、光寶科（dd20＝0，20 日高）。
- 光寶科 Ridge 原序 1 → 回撤序 10。分數 ≠ 漲跌幅。

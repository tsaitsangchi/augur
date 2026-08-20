---
status: executed
series: s1s5_loop
track: RIDGE-THEN-PB
product_id: RIDGE-THEN-PB-v1
date: 2026-08-20
viewpoint: 2026-08-20T11:40+08:00
asof: "2026-08-19"
price_max: "2026-08-19"
n_long_entry: 0
n_short_entry: 1
short_entry: "2385"
realized_30: false
table: ridge_then_pb_entry
json: audits/RIDGE-THEN-PB-LS-LAST-TD.json
go: audits/RIDGE-THEN-PB-LAST-TD-PERSIST-GO-20260820.md
standing_unchanged: true
self_reported: true
layer: "[I]"
---

# EXECUTED｜最後交易日八窗＋落庫＋30 日（未實現）

`python scripts/probe_ridge_then_pb.py --last-td --persist`

| 項 | 結果 |
|---|---|
| asof | **2026-08-19**（價頂；08-20＝假 B3） |
| 八窗模型 stamp | 皆 **2026-08-19**（月尾 WF 尚未訓完；不是 07-31 月尾模型） |
| 做多可當進場 | **0／10**（十檔皆等回撤） |
| 做空可當進場 | **1／10＝2385 群光**（≠可融券） |
| 落庫 | `ridge_then_pb_entry` 1 列；`realized=false` |
| 30 日 | **未實現**（次一交易日尚未進庫） |
| standing | H20+H60 未改 |

分數≠報酬％。月尾特徵河仍在灌；月尾八窗訓完後，最後交易日應改用「該日可見最近月尾」模型再打一次分、再覆寫帳本。

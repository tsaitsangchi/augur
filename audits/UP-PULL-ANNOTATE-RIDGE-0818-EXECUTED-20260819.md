---
status: executed
series: s4_s5_verify
track: UP-PULL
date: 2026-08-19
viewpoint: 2026-08-19T09:36+08:00
asof: "2026-08-18"
shell: scripts/probe_up_pull_annotate_ridge.py
json: /tmp/up-pull-annotate-ridge-2026-08-18.json
audit_json: audits/UP-PULL-ANNOTATE-RIDGE-0818.json
paste: "UP-PULL-annotate-ridge-go | asof=2026-08-18 | copy-only | dry-run"
wrote_prediction_values: false
standing_unchanged: true
selftest: green
self_reported: true
layer: "[I]"
---

# EXECUTED｜UP-PULL 標註 Ridge＠2026-08-18

Steward 09:33 明示。copy-only／dry-run。零寫 `prediction_values`。standing 仍 H20+H60。未接 live 顧問殼。`--date 2026-08-19` → rc=3。

## 答

- 欄 A：RankRidge 八窗平均 score Top10 **10／10** 標「高位相對強，等回撤；≠進場」。∩ UP-PULL 做多閘＝**0**。
- 欄 B：UP-PULL-v1 strict 做多 **5**／做空 **2**（不足不補）。做空 ≠ 可空。
- 等回撤 ≠ 預測跌幅％。score ≠ 漲跌幅％。路徑％ ≠ 未來。

典型缺閘：多數缺 L-B（H5／H10 未雙負）＋ L-C（還在 20 日高附近）。聯發科／奇鋐回撤帶已到，仍缺短窗雙負。光寶科／厚生 dd20≈0。

## 殼

`uptrend_pullback.wait_pullback_annot`／`render_ridge_wait_line`；`scripts/probe_up_pull_annotate_ridge.py`。自測 rc=0。探針 rc=0。未改 `advise.py` picks 表。

## 不做

`UP-PULL-emit-go`；改 standing；P2 OOS；把 Ridge Top10 當買點。

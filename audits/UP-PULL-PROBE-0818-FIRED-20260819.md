---
status: fired
series: s4_s5_verify
track: UP-PULL
date: 2026-08-19
viewpoint: 2026-08-19T08:35+08:00
asof: "2026-08-18"
shell: scripts/probe_uptrend_pullback.py
paste: "UP-PULL-probe-go | date=2026-08-18 | side=both | k=10 | policy=strict"
self_reported: true
layer: "[I]"
---

# FIRED｜UP-PULL 探針＠2026-08-18 · both · strict · k=10

GO 已貼。庫函＋CLI 已落盤。接著自測 → 唯讀探針＠08-18（≤價頂）。

## 準

- `python -m augur.evaluation.uptrend_pullback --selftest`
- `python scripts/probe_uptrend_pullback.py --selftest`
- `python scripts/probe_uptrend_pullback.py --date 2026-08-18 --side both --k 10 --policy strict`

## 禁（本槍未開）

寫 `prediction_values`；RankRidge 排序；soft-fill；`--date 2026-08-19` 當 as-of 出單；promote；改 standing。

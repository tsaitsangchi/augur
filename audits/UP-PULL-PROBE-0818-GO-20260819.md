---
status: go
series: s4_s5_verify
track: UP-PULL
date: 2026-08-19
viewpoint: 2026-08-19T08:32+08:00
asof: "2026-08-18"
shell: scripts/probe_uptrend_pullback.py
paste: "UP-PULL-probe-go | date=2026-08-18 | side=both | k=10 | policy=strict"
self_reported: true
layer: "[I]"
---

# GO｜UP-PULL 探針＠2026-08-18 · both · strict · k=10

Steward 08:32 明示。D=08-18 ≤ 價頂（本窗預期 ready）。P0 已採納。

## 准

- `python scripts/probe_uptrend_pullback.py --date 2026-08-18 --side both --k 10 --policy strict`
- 唯讀；JSON；做多／做空表
- 過閘不足 10 如實少列

## 禁

- 寫 `prediction_values`；RankRidge score 排序；soft-fill／relax-A
- `--date 2026-08-19`（假 B3）
- promote；改 standing 20,60；sim-apply；當可交易／可空

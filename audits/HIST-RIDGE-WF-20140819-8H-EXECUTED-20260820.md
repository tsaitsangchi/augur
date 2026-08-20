---
status: executed
series: s1s5_loop
track: HIST-RIDGE-WF
product_id: HIST-RIDGE-WF-v1
phase: P2-train-asof-D
date: 2026-08-20
asof: "2014-08-19"
n_core: 448
n_tip_core: 285
n_pv_per_h: 448
horizons: [5, 10, 20, 40, 60, 90, 120, 240]
feats_hash: 56d03625463b3eba
go: audits/HIST-RIDGE-WF-20140819-8H-GO-20260820.md
standing_unchanged: true
self_reported: true
layer: "[I]"
---

# EXECUTED｜RankRidge 八窗＠2014-08-19

`train_ranker --family RankRidge --asof 2014-08-19 --resume` × 八窗，再以當日核心 448／特徵打分。

| 窗 | model_id | 訓練列 |
|---|---|---|
| H5 | `RankRidge_H5_2014-08-19_seed42_56d03625463b3eba` | 6073 |
| H10 | `RankRidge_H10_2014-08-19_seed42_56d03625463b3eba` | 6069 |
| H20 | `RankRidge_H20_2014-08-19_seed42_56d03625463b3eba` | 5618 |
| H40 | `RankRidge_H40_2014-08-19_seed42_56d03625463b3eba` | 5161 |
| H60 | `RankRidge_H60_2014-08-19_seed42_56d03625463b3eba` | 4710 |
| H90 | `RankRidge_H90_2014-08-19_seed42_56d03625463b3eba` | 4246 |
| H120 | `RankRidge_H120_2014-08-19_seed42_56d03625463b3eba` | 3308 |
| H240 | `RankRidge_H240_2014-08-19_seed42_56d03625463b3eba` | resume（先前已訓） |

分數：八窗各 **448** 列（＝當時核心）。core＠2026-08-19＝**285 未變**。standing 未改。標皆出場日≤2014-08-19。

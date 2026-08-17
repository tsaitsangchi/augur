---
status: executed
series: s4_s5_verify
track: H-TRACK
date: 2026-08-14
viewpoint: 2026-08-14T17:25+08:00
asof: "2026-08-13"
go: audits/H5-OPEN-GO-20260814.md
fired: audits/H5-OPEN-FIRED-20260814.md
logdir: /tmp/retrain-all-asof-2026-08-13-h5
paste: "H5-OPEN-executed | H_TRACK={5,20,40,60,90,120,240} | rank 56/56 | dgate_H_5 draft | ≠D_5 | no-promote | no-emit"
self_reported: true
layer: "[I]"
---

# EXECUTED｜另開 H5＠2026-08-13

Steward 准加入 H5（5 交易日；**不是** D 軌 k=5）。H90 包持鎖期間先 DDL；鎖釋放後補訓。`p_mkt`／`p_up`／分數 **不是** 漲跌幅％。

## DDL

CHECK＝`ARRAY[5, 20, 40, 60, 90, 120, 240]`（不准 82）。`econ_verdict_rule` H5＝**thin_unestablished**（未塗 dead／established）。

## 截面 8×H5＠08-13

Ridge／GBDT／XGB／Cat／RF／SVM／KNN／MLP 全成。覆蓋 **rank=56/56**（8×7）。

## 方向臂 H5

| 臂 | 實測 |
|---|---|
| MktLogit | 4228 列；大盤上漲基率 p̄=0.594（**不是**％） |
| MktLogit_v2 | 4228 列（同窗） |
| OOS RankRidge | 107 折／35 827 列 |
| DirStack | 29 978 列；個股絕對上漲基率 p̄=0.487 |
| DirStackM | 26 389 列；p̄=0.511；114 panel（2017-01-24→2026-06-30） |
| `dgate_H_5` | **preregistered draft only**（未 evaluate／approve） |

## 禁（仍守）

假 B3＠08-14／promote／emit B3／evaluate `dgate_H_5`／把 H5 塗 established 或 dead／把 H5 當成 Daily k=5。

---
title: 模型重訓盤點 · as-of 2026-08-11
status: inventory
date: 2026-08-12
series: s4_retrain
track: RETRAIN-ASOF-0811
viewpoint: 2026-08-12T08:48+08:00
layer: "[I]"
paste: "RETRAIN-ASOF-0811-inventory | mirror-0810-ALL-RANK | FZ/GATE | NF-pause | no-promote | no-SIM-apply"
fv_tip: 2026-08-11
pred_tip: 2026-08-11
prior_b3: audits/OPS-B3-20260811-EXECUTED-20260812.md
self_reported: true
---

# INVENTORY｜重訓 as-of 2026-08-11

> Steward：`做所有模型的重訓到 as-of 2026-08-11` → 對齊 **0810 ALL-RANK 包 C**（非 NF／非 Daily 方向臂）。

## LIVE
| 錨 | 值 |
|---|---|
| PriceAdj／fv／pred tip | **2026-08-11**（B3 catch-up 已 EXECUTED） |
| 日曆 | 2026-08-12（08-12 價未到 → 不假開 08-12 tip） |

## 「所有模型」＝本包範圍（同 0810）

| 步 | 內容 |
|---|---|
| 0 | B3／feat／core＠08-11 | **已完成** |
| 1 | RankRidge × **20,40,60,82,120** `@2026-08-11` seed42 | 待跑 |
| 2 | Challenger：GBDT 20/60；XGB/Cat/RF/KNN/MLP **60**；SVM **20** | 待跑 |
| 3 | repredict+emit H20/60（新 Ridge） | 待跑 |

## 不納
Daily* 方向臂；NF 挑戰族（pause）；默升格／SERVE-SWAP。

---
status: executed
series: s4_models
track: NF-A-KNN
date: 2026-08-07
viewpoint: 2026-08-07T13:30+08:00
paste: "NF-A-KNN-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | H60 | until=2026-06-30 | no-promote-default"
go: audits/NF-A-KNN-GO-20260807.md
plan: reports/augur_nf_a_knn_go_plan_20260807.md
logdir: /tmp/nf-a-knn-20260807/
champion_freeze_H60: {sharpe: 1.3016, hit: 0.6316}
prior: audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md
self_reported: true
promote: false
layer: "[I]"
---

# EXECUTED｜NF-A-KNN-go · RankKNN H60×{42,1,2} · until=2026-06-30

## 護欄
FZ/GATE · skip-sync · no-SIM-apply · no-promote · 其他族 NF-pause keep · 未假 B3 — **守**。

## #14
`panel_hash=ca1b6ff379` · prodset3 · n=19  
確定性：三 seed **完全同值**（預期）。

| seed | net Sharpe | hit |
|---|---|---|
| 42／1／2 | **1.2908** | 0.6316 |

**min/med/max = 1.2908**；hit＝冠軍持平  
vs 冠軍 Sharpe **1.3016** → **1.2908 ＜ 1.3016** → **STOP promote**（復現 08-04）。

## train
joblib ×3 已寫；`model_family_chk` 擋 RankKNN — 未 ALTER。

## Wave-A 有界帶
RF／XGB／Cat／SVM·H20／MLP／**KNN** 本窗均已重驗、**皆未升格** → 可 `Wave-A-bounded-close`。

*完。[I] · no promote.*

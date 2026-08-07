---
status: executed
series: s4_models
track: NF-A-MLP
date: 2026-08-07
viewpoint: 2026-08-07T10:59+08:00
paste: "NF-A-MLP-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | H60 | until=2026-06-30 | no-promote-default"
go: audits/NF-A-MLP-GO-20260807.md
plan: reports/augur_nf_a_mlp_go_plan_20260807.md
logdir: /tmp/nf-a-mlp-20260807/
champion_freeze_H60: {sharpe: 1.3016, hit: 0.6316}
prior: audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md
self_reported: true
promote: false
layer: "[I]"
---

# EXECUTED｜NF-A-MLP-go · RankMLP H60×{42,1,2} · until=2026-06-30

## 護欄
FZ/GATE · skip-sync · no-SIM-apply · no-promote · 其他族 NF-pause keep · 未假 B3 — **守**。

## #14
`panel_hash=ca1b6ff379` · prodset3 · n=19

| seed | net Sharpe | hit |
|---|---|---|
| 42 | 0.9935 | 0.5263 |
| 1 | 1.1005 | 0.5789 |
| 2 | 1.1692 | 0.6316 |

**min/med/max = 0.9935 / 1.1005 / 1.1692**；min hit=0.5263  
→ **STOP promote**（復現 08-04）。

## train
joblib ×3 已寫；`model_family_chk` 擋 RankMLP — 未 ALTER。

## Wave-A 有界帶進度
RF／XGB／Cat／SVM·H20／**MLP** 本窗皆已重驗、皆未升格。  
殘：**RankKNN**（確定性；可選收官或略）。

*完。[I] · no promote.*

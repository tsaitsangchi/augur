---
status: executed
series: s4_models
track: NF-A-CAT
date: 2026-08-07
viewpoint: 2026-08-07T10:42+08:00
paste: "NF-A-CAT-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | H60 | until=2026-06-30 | no-promote-default"
go: audits/NF-A-CAT-GO-20260807.md
plan: reports/augur_nf_a_cat_go_plan_20260807.md
logdir: /tmp/nf-a-cat-20260807/
champion_freeze_H60: {sharpe: 1.3016, hit: 0.6316}
prior: audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md
self_reported: true
promote: false
layer: "[I]"
---

# EXECUTED｜NF-A-CAT-go · RankCat H60×{42,1,2} · until=2026-06-30

## 護欄
FZ/GATE · skip-sync · no-SIM-apply · no-promote · 其他族 NF-pause keep · 未假 B3 — **全守**。

## #14
`panel_hash=ca1b6ff379` · prodset3 · n=19

| seed | net Sharpe | hit |
|---|---|---|
| 42 | 1.0164 | 0.5789 |
| 1 | 1.1527 | 0.5789 |
| 2 | 1.0049 | 0.5789 |

**min/med/max Sharpe = 1.0049 / 1.0164 / 1.1527**；**min hit = 0.5789**（劣於冠軍 hit 0.6316）  
→ **STOP promote**（復現 08-04）。

## train
joblib ×3 已寫；`model_family_chk` 擋 `RankCat`（rc=1）— 未 ALTER。

## 決策
不升格。V2 樹模優先帶（RF／XGB／Cat）同窗 **全未過門**。  
下一有界選項（另句）：SVM（H20 前真贏）／MLP／或停樹帶轉 V／#1。

*完。[I] · no promote.*

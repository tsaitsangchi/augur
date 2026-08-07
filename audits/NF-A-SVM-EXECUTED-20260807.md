---
status: executed
series: s4_models
track: NF-A-SVM
date: 2026-08-07
viewpoint: 2026-08-07T10:50+08:00
paste: "NF-A-SVM-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | H20 | until=2026-06-30 | no-promote-default"
go: audits/NF-A-SVM-GO-20260807.md
plan: reports/augur_nf_a_svm_go_plan_20260807.md
logdir: /tmp/nf-a-svm-20260807/
champion_freeze_H20: {sharpe: 1.1684, hit: 0.6393}
prior: audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md
self_reported: true
promote: false
gate_clear: false
layer: "[I]"
---

# EXECUTED｜NF-A-SVM-go · RankSVM H20×{42,1,2} · until=2026-06-30

## 護欄
FZ/GATE · skip-sync · no-SIM-apply · no-promote-default · 其他族 NF-pause keep · 未假 B3 — **守**。

## #14
`panel_hash=26e4c2daaa` · n_panels=66 · n_periods=61 · prodset3

| seed | net Sharpe | hit |
|---|---|---|
| 42 | 1.2433 | **0.6230** |
| 1 | 1.2164 | 0.6393 |
| 2 | 1.2343 | 0.6393 |

**min/med/max Sharpe = 1.2164 / 1.2343 / 1.2433**（三 seed 皆 **＞** 冠軍 1.1684）  
**min hit = 0.6230**（seed42 **劣於** 冠軍 hit 0.6393）

| 尺 | 實測 | 判定 |
|---|---|---|
| min Sharpe > 1.1684 | 1.2164 | ✓ |
| min hit ≥ 0.6393 | 0.6230 | ✗ |
| 升格 | — | **GATE_CLEAR=False** · **不升格** |

## 對 08-04 真贏之誠實差

08-04：min Sharpe 1.2258／min hit **0.6393**（持平）→ 當時記真贏。  
本窗：Sharpe 仍全面高於冠軍，但 **seed42 hit 掉到 0.6230** → 依「hit 不劣」門 **未清**。不宣稱複現真贏、不換 LIVE。

## train
joblib ×3 已寫；`model_family_chk` 擋 RankSVM（rc=1）— 未 ALTER。

## 決策
**STOP promote**。Wave-A 有界重驗（RF／XGB／Cat／SVM·H20）皆未達升格；H20 econ 本就 dead——即使 SVM Sharpe 好看也不自動掛生產。

*完。[I] · no promote.*

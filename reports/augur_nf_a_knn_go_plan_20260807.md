---
title: NF-A-KNN · KNN 族 plan-first（有界撤 pause）
status: adopted
series: s4_models
track: NF-A-KNN
date: 2026-08-07
viewpoint: 2026-08-07T13:28+08:00
paste: "NF-A-KNN-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | H60 | until=2026-06-30 | no-promote-default"
prior_eval: audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md
layer: "[I]"
role: RankKNN H60 有界重驗；確定性演算法；前評未過門
self_reported: true
---

# NF-A-KNN｜RankKNN · H60

僅 RankKNN；其他族 NF-pause keep；預凍 H60 冠軍 Sharpe **1.3016**／hit **0.6316**；no-promote-default。  
誠實：無 `random_state` 影響 → 三 seed 預期**同值**（仍跑滿種子協議）。

*plan＝go 同拍。*

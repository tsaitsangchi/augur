---
status: executed
series: s4_s5_verify
track: V0
date: 2026-08-13
viewpoint: 2026-08-13T13:03+08:00
plan: reports/augur_s1s5_asof_verify_best_next_20260813.md
matrix: reports/augur_s4_other_model_verify_matrix_plan_20260806.md
paste: "S4-V0-INV-0813 | registry-A@08-12 | Daily*=05-31 | no-train | NF-pause"
self_reported: true
layer: "[I]"
---

# EXECUTED｜其他模型驗証 V0 盤點刷新 · 2026-08-13

唯讀 `model_registry`。零訓練。

| family | n | max asof |
|---|---|---|
| RankRidge | 35 | 2026-08-12 |
| RankGBDT | 12 | 2026-08-12 |
| RankXGB／Cat／RF／KNN／MLP／SVM | 6 each | 2026-08-12 |
| Daily*／MktLogit／DirStackM | 1–2 | **2026-05-31** |

asof 列數（親查）：05-31＝16／6 族（方向臂）；06-30＝29／8；07-31＝5／1（僅 Ridge）；08-10／11／12＝各 13／8；**08-07＝0**（fv 有、registry 無）。  
asof＝08-12：H20×3、H40×1、H60×7、H82×1、H120×1。  
tip 校準器仍 `platt_RankRidge_h{20,60}_asof2026-08-07_…`。  
0812 NF 六族 **不**重掃。殘格仍須點名。

L2 `--dry-plan --date 2026-08-07`／`06-30`／`08-12` **殼通、零寫庫**。

*v0 only。*

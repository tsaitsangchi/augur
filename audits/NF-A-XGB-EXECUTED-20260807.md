---
status: executed
series: s4_models
track: NF-A-XGB
date: 2026-08-07
viewpoint: 2026-08-07T10:26+08:00
paste: "NF-A-XGB-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | H60 | until=2026-06-30 | no-promote-default"
go: audits/NF-A-XGB-GO-20260807.md
plan: reports/augur_nf_a_xgb_go_plan_20260807.md
logdir: /tmp/nf-a-xgb-20260807/
champion_freeze_H60: {sharpe: 1.3016, hit: 0.6316}
prior: audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md
self_reported: true
promote: false
layer: "[I]"
---

# EXECUTED｜NF-A-XGB-go · RankXGB H60×{42,1,2} · until=2026-06-30

## 1. 護欄

| 項 | 實況 |
|---|---|
| FZ/GATE-keep · skip-sync · no-SIM-apply | **守** |
| no-promote-default | **守** — `PROMOTE=False` |
| 其他族 NF-pause | **keep** |
| #1 | 未假 B3；本窗無 LIVE B3 競合 |

## 2. #14

探針：`/tmp/nf-a-xgb-20260807/probe_xgb_h60.py` · `model=RankXGB` · 同 RF 網格  
`panel_hash=ca1b6ff379` · prodset 3 · n_periods=19

| seed | net Sharpe | hit |
|---|---|---|
| 42 | 1.1116 | 0.6316 |
| 1 | 1.1905 | 0.6316 |
| 2 | 1.1075 | 0.6316 |

**min/med/max = 1.1075 / 1.1116 / 1.1905**；min hit=0.6316  
vs 冠軍 1.3016 → **STOP promote**（與 08-04 EVAL 逐 seed 一致）。

## 3. train_ranker

joblib ×3 已寫：`models_artifacts/RankXGB_H60_2026-06-30_seed{42,1,2}_56d03625463b3eba.joblib`  
**registry**：`model_family_chk` 擋 `RankXGB`（同 RankRF）— **未 ALTER**。

## 4. 決策

不升格／不換 LIVE／不撤全域 NF。  
V2 優先 1 樹模（RF＋XGB）同窗均未過門；下一樹模候選＝Cat（另句 `NF-A-CAT-go-plan`）。

*完。[I] executed · no promote.*

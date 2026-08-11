---
status: executed
series: s4_retrain
track: RETRAIN-ASOF-0731
date: 2026-08-07
viewpoint: 2026-08-07T13:35+08:00
paste: "RETRAIN-ASOF-0731-go | FZ/GATE-keep | skip-sync | no-SIM-apply | RankRidge | seeds=42 | H=20,40,60,82,120 | asof=2026-07-31 | no-promote-default | hold-#1"
go: audits/RETRAIN-ASOF-0731-GO-20260807.md
plan: reports/augur_retrain_asof_0731_rankridge_plan_20260807.md
logdir: /tmp/retrain-asof-0731/
self_reported: true
promote: false
serve_swap: false
layer: "[I]"
---

# EXECUTED｜RETRAIN-ASOF-0731 · RankRidge 五 H · asof=2026-07-31

## 護欄
FZ/GATE · skip-sync · no-SIM-apply · no-promote · hold-#1 · **未**換 LIVE serve — **守**。

## 結果（五 H 全 OK）

| H | model_id | train_rows | panels |
|---|---|---|---|
| 20 | `RankRidge_H20_2026-07-31_seed42_56d03625463b3eba` | 36366 | 114 |
| 40 | `RankRidge_H40_2026-07-31_seed42_56d03625463b3eba` | 36140 | 114 |
| 60 | `RankRidge_H60_2026-07-31_seed42_56d03625463b3eba` | 35917 | 114 |
| 82 | `RankRidge_H82_2026-07-31_seed42_56d03625463b3eba` | 35691 | 114 |
| 120 | `RankRidge_H120_2026-07-31_seed42_56d03625463b3eba` | 35241 | 114 |

- feature_source=**prodset**；feats=active3；feature_hash=`56d03625463b3eba`（與 06-30 產物同 hash＝特徵契約未變）  
- joblib ×5 已寫；registry 已登錄  
- panels 窗：`[2007-12-31 .. 2026-07-31]`

## 決策
- **不**升格、**不**默換每日 B3 serve（現 LIVE 仍為 asof=**2026-06-30** 掛載，直至另句 `SERVE-SWAP-0731-go`）  
- #14 對 07-31 產物＝另選（前進重訓≠06-30 窗復現）  
- 主軸 #1 候 A＠08-07 未假跑

*完。[I] executed · artifacts ready · serve unchanged.*

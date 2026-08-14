---
status: executed
series: s4_s5_verify
track: V1
date: 2026-08-13
viewpoint: 2026-08-13T13:23+08:00
asof: "2026-08-07"
plan: reports/augur_s1s5_r16_exec_board_20260813.md
shell: scripts/run_asof_collect_train_verify.sh
paste: "WP-H-L2-hist-0807-EXECUTED | skip-sync | no-promote | no-fake-B3 | yield-to-B3 | NF-pause"
self_reported: true
layer: "[I]"
---

# EXECUTED｜歷史 as-of V1 邊界 A＠2026-08-07

`bash scripts/run_asof_collect_train_verify.sh --date 2026-08-07 --apply`  
RC=0 · 約 140s · collect SKIP（fv 已在）· L2 A-pack **13／8 族** · no-promote。

| 尺 | 值 |
|---|---|
| registry＠08-07 | RankRidge×5＋GBDT×2＋XGB／Cat／RF／KNN／MLP／SVM 各 1 ＝ **13** |
| #14＠08-07 | H20＝**dead**（570）；H60＝**thin**（570） |
| LIVE tip | 仍 **08-12**（未覆蓋） |
| 08-13 | 閘 rc=3 假 B3（未跑） |

0812 NF 六族 **未**重掃。Daily*／VECM／TCN／NB／RL **未**開。

*v1 hist；誠實形。*

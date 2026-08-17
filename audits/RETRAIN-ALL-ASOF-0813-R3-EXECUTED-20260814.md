---
status: executed
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-14
viewpoint: 2026-08-14T18:01+08:00
asof: "2026-08-13"
go: audits/RETRAIN-ALL-ASOF-0813-R3-GO-20260814.md
fired: audits/RETRAIN-ALL-ASOF-0813-R3-FIRED-20260814.md
shell: scripts/run_retrain_all_asof.sh
logdir: /tmp/retrain-all-asof-2026-08-13-r3
paste: "RETRAIN-ALL-0813-R3-executed | lock=價頂 | 8x7+Daily+Mkt+DirStackM | no-resume | COMPLETE 56/56 | no-promote | no-emit | no-fake-B3@08-14"
self_reported: true
layer: "[I]"
---

# EXECUTED｜全量重訓＠2026-08-13（H{5,20,40,60,90,120,240}）

Steward 句已執行。方向臂鎖＝價頂 **2026-08-13**（08-14＝假 B3，未訓）。`--no-resume` RC=0。`p_mkt`／`p_up`／hit **不是** 漲跌幅％。

## 截面 8×7

Ridge／GBDT／XGB／Cat／RF／SVM／KNN／MLP × H{5,20,40,60,90,120,240} 全成＠08-13。覆蓋 **rank=56/56 daily=3/3 mkt=2/2 stack=1/1**。

## 方向臂 asof＝08-13

| 臂 | 實測 |
|---|---|
| DailyLogit k=1 | OOS 1 225 883；pooled_hit=0.5509 |
| DailyGBDT_cal k=5 | 3 674 238 列（3 seed） |
| MktLogit／v2 | 七窗 P_mkt 全寫；H5 p̄=0.594；H240 p̄=0.785（大盤上漲基率，**不是**％） |
| OOS | H5＝35 827；H90＝34 370；H240＝32 589 |
| DirStack | 七窗全成；H5＝29 978；H240＝21 340 |
| DirStackM | 月頻 H{5,20,40,60,90,240}；H5＝26 389；H90＝23 781；H240＝18 262 |
| dgate_H_5／60／90／240 | **preregistered draft**（preregister-all 0 新列；未 evaluate／approve） |

未 promote、未 emit B3、未開 NF、未把 H5 當成 D 軌 k=5。

---
status: executed
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-16
viewpoint: 2026-08-16T18:25+08:00
asof: "2026-08-14"
go: audits/RETRAIN-ALL-ASOF-0814-H10-GO-20260816.md
fired: audits/RETRAIN-ALL-ASOF-0814-H10-FIRED-20260816.md
h10: audits/H10-OPEN-EXECUTED-20260816.md
shell: scripts/run_retrain_all_asof.sh
logdir: /tmp/retrain-all-asof-2026-08-14-h10
paste: "RETRAIN-ALL-0814-H10-executed | lock=價頂 | 8x8+Daily+Mkt+DirStackM | no-resume | COMPLETE 64/64 | no-promote | no-emit | no-fake-B3@08-15/16"
self_reported: true
layer: "[I]"
---

# EXECUTED｜全量重訓＠2026-08-14（H{5,10,20,40,60,90,120,240}）

Steward 句已執行。方向臂鎖＝價頂 **2026-08-14**（08-15／08-16＝假 B3，未訓）。`--no-resume` **exit 0**（elapsed 7 449 423 ms ≈ 124 min）。`p_mkt`／`p_up`／hit **不是** 漲跌幅％。

## 截面 8×8

Ridge／GBDT／XGB／Cat／RF／SVM／KNN／MLP × H{5,10,20,40,60,90,120,240} 全成＠08-14（resume=0）。覆蓋 **COMPLETE rank=64/64 daily=3/3 mkt=2/2 stack=1/1**。

asof ready：price_max=fv_max=**2026-08-14**；fv_nfeat=37；fv_nrows=27 958；has_core=True。

## 方向臂 asof＝08-14

| 臂 | 實測 |
|---|---|
| DailyLogit k=1 | OOS 1 226 168；pooled_hit=0.5508 |
| DailyGBDT_cal k=5 | 3 675 087 列（3 seed） |
| MktLogit／v2 | 八窗 P_mkt 全寫；H5 p̄=0.595；H10 p̄=0.618；H240 p̄=0.785（大盤上漲基率，**不是**％） |
| OOS | H5＝36 110；H10＝35 057；H90＝34 370；H240＝32 589 |
| DirStack | 八窗全成；H5＝30 261；H10＝29 210；H240＝21 340 |
| DirStackM | 月頻 H{5,10,20,40,60,90,240}；H5＝26 389；H10＝26 385；H90＝23 781；H240＝18 262 |
| `dgate_H_5`／10／60／90／240 | **preregistered draft**（H10＝1 新列；未 evaluate／approve） |

未 promote、未 emit B3、未開 NF、未把 H5 當成 D 軌 k=5、未把 H10 當成 KH10。

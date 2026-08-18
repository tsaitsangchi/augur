---
status: executed
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-18
viewpoint: 2026-08-18T08:05+08:00
asof: "2026-08-17"
go: audits/RETRAIN-ALL-ASOF-0817-GO-20260818.md
fired: audits/RETRAIN-ALL-ASOF-0817-FIRED-20260818.md
shell: scripts/run_retrain_all_asof_daily.sh
logdir: /tmp/retrain-all-asof-2026-08-17
cron_log: /home/hugo/logs/retrain_all_asof.log
paste: "RETRAIN-ALL-0817-executed | lock=價頂 | 8x8+Daily+Mkt+DirStackM | COMPLETE 64/64 | no-promote | no-emit | no-fake-B3@08-18"
self_reported: true
layer: "[I]"
---

# EXECUTED｜方向臂鎖最新日＋八窗重訓＠2026-08-17

Steward 句已滿足。可更新最新日＝**2026-08-17**（08-18＝假 B3，未訓）。昨夜 cron 21:40 `run_retrain_all_asof_daily.sh --apply` 已 `RETRAIN-ALL-ASOF D=2026-08-17 完成`。本窗親查包齊，**未**再 `--no-resume` 重燒。`p_mkt`／`p_up`／hit **不是** 漲跌幅％。

## 截面 8×8＠08-17

Ridge／GBDT／XGB／Cat／RF／SVM／KNN／MLP × H{5,10,20,40,60,90,120,240} 全成。覆蓋 **COMPLETE rank=64/64 daily=3/3 mkt=2/2 stack=1/1**。

asof ready：price_max=fv_max=**2026-08-17**；fv_nfeat=37；fv_nrows=27 959；has_core=True。

## 方向臂 asof＝08-17

| 臂 | 實測（昨夜 log） |
|---|---|
| DailyLogit k=1 | OOS 1 226 453；pooled_hit=0.5508 |
| DailyGBDT_cal k=5 | 3 675 939 列（3 seed） |
| MktLogit／v2 | 八窗 P_mkt 全寫；H5 p̄=0.595；H10 p̄=0.618；H240 p̄=0.785（大盤上漲基率，**不是**％） |
| OOS | H5＝36 394／109 折；H10＝35 261／105；H90＝34 370／101；H240＝32 589／93 |
| DirStack | 八窗全成；H5＝30 545；H10＝29 414；H240＝21 340 |
| DirStackM | 月頻；H5＝26 389；H10＝26 385；H90＝23 781；H240＝18 262 |
| `dgate_H_*` | **仍 draft**（未 evaluate／approve） |

## 誠實缺口（本句不修）

- **出門** `prediction_values`／`prediction_probability` 仍＠**08-14**（H20+H60 各 286）。RETRAIN-ALL **不 emit**。要掛 tip＠08-17 須另貼 `B3-go | D=2026-08-17 | horizons=20,60 | no-promote`。
- **P6** 校準器仍 `platt_RankRidge_h{20,60}_asof2026-08-14_ge10dbc2`。Ridge 包已＠08-17 → freeze 缺口再開；refit 須另 `P6-REFIT-FREEZE-2026-08-17-go`。
- 未 promote、未開 NF、未把 H5 當 D 軌 k=5、未把 H10 當 KH10。

log：`/tmp/retrain-all-asof-2026-08-17/` · cron：`$HOME/logs/retrain_all_asof.log`

*完。*

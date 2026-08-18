---
status: executed
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-18
viewpoint: 2026-08-18T13:50+08:00
asof: "2026-08-17"
go: audits/RETRAIN-ALL-0817-FORCE-GO-20260818.md
fired: audits/RETRAIN-ALL-0817-FORCE-FIRED-20260818.md
shell: scripts/run_asof_collect_train_verify.sh
inner: scripts/run_retrain_all_asof.sh --date 2026-08-17 --apply --no-resume
log: /tmp/retrain-all-0817-force/run.log
logdir: /tmp/retrain-all-asof-2026-08-17
elapsed_ms: 8311140
rc: 0
paste: "RETRAIN-ALL-0817-FORCE-executed | lock=價頂08-17 | 8x8+Daily3+Mkt2+DirStackM | --no-resume | no-promote | no-emit | no-fake-B3@08-18"
self_reported: true
layer: "[I]"
---

# EXECUTED｜價頂 RETRAIN-ALL force＠2026-08-17 · 方向臂鎖最新日 · 八窗重 fit

Steward 11:23 句已滿足。可更新最新日＝PriceAdj TAIEX **2026-08-17**（08-18＝假 B3，未訓、registry 0 列）。

`bash scripts/run_asof_collect_train_verify.sh --date 2026-08-17 --apply --track all --force`  
內殼 `resume=0`。**RC=0** · **~138 min**（11:25→13:44+08）。未 emit B3 · 未 SERVE-SWAP · 未 promote。`p_mkt`／`p_up`／pooled_hit／IC **不是**漲跌幅％。

## 截面 8×8＠08-17（本槍全重 fit）

Ridge／GBDT／XGB／Cat／RF／SVM／KNN／MLP × H{5,10,20,40,60,90,120,240}。resume=0 → **64／64 新訓**。`created_at`＝2026-08-18 11:26–11:36+08。artifact 例：`RankRidge_H20_2026-08-17_seed42_56d03625463b3eba.joblib`。

asof ready 親查 13:49：price_max=fv_max=**2026-08-17**；fv_nfeat=37；fv_nrows=27 959；has_core=True；`pack_complete=True`（A 64＋Daily 3＋Mkt 2＋DirStackM 1）。`--date 2026-08-18` → fake_b3 rc=3。

## 方向臂活鎖＝08-17（本槍重訓）

DATE＝價頂 → Daily／Mkt／DirStackM **有**跑（非歷史 D 的 SKIP）。方向臂 `ON CONFLICT` **不**刷新 `created_at`（仍 2026-07-11）；判據＝log＋`asof_snapshot`＋train_span 上界半開 `[…,2026-08-18)`＝含到 08-17。

| 臂 | 本槍 |
|---|---|
| DailyLogit k=1 | OOS 1 226 453；pooled_hit=0.5508（**不是**％） |
| DailyGBDT k=1 | pooled_hit=0.5456 |
| DailyGBDT_cal k=5 | 3 675 939 列（3 seed） |
| MktLogit／v2 | 八窗 P_mkt；H5 p̄=0.595 … H240 p̄=0.785（大盤上漲基率，**不是**％） |
| OOS | H5＝36 394／109 折；H10＝35 261／105；H90＝34 370／101；H240＝32 589／93 |
| DirStack | 八窗全成；H5＝30 545 … H240＝21 340 |
| DirStackM | 月頻；H5＝26 389；H10＝26 385；H90＝23 781；H240＝18 262 |
| `dgate_H_5/10/60/90/240` | **仍 preregistered**；H20／40／120 **evaluated_fail**；本槍未 evaluate／approve |

## 出門／P6（本句不修）

- standing 仍 **H20+H60**。`prediction_values`／`prediction_probability`＠08-17 各 287 列＝**本晨 B3** 寫入；本槍覆寫 RankRidge artifact、**未**重 emit。下一交易日 B3 才會用新 fit 出單。
- P6 校準器仍 `platt_RankRidge_h{20,60}_asof2026-08-14_ge10dbc2`。Ridge 包已＠08-17 → freeze 缺口仍開；refit 須另 `P6-REFIT-FREEZE-2026-08-17-go`。
- 無已實現 H5（價頂當天）→ 不跑 `--ic`。#14：H20=`dead`；其餘 thin。未塗綠。

## 誠實 SKIP（非失敗）

SeqLSTM／classical TS／threelens／0812 NF 六族／P6 重 fit／promote／VECM／TCN／NB／RL／假 B3＠08-18。

*完。*

---
status: executed
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-14
viewpoint: 2026-08-14T15:35+08:00
asof: "2026-08-13"
go: audits/RETRAIN-ALL-ASOF-0813-R2-GO-20260814.md
fired: audits/RETRAIN-ALL-ASOF-0813-R2-FIRED-20260814.md
shell: scripts/run_retrain_all_asof.sh
log: /tmp/retrain-all-asof-2026-08-13-r2/apply.log
paste: "RETRAIN-ALL-0813-R2-EXECUTED | D=2026-08-13 | 48/48 | no-resume | H90=82td | DirStackM-H240 | no-promote | no-emit | no-fake-B3@08-14"
self_reported: true
layer: "[I]"
---

# EXECUTED｜方向臂鎖最新日＋全量重訓＠2026-08-13

`bash scripts/run_retrain_all_asof.sh --date 2026-08-13 --apply --no-resume` · **RC=0**（約 102 min）  
鎖＝PriceAdj TAIEX 價頂 **2026-08-13**（08-14＝假 B3，未訓未 emit）。  
口語「90 天」＝封閉集 **H82**（未另開 H90）。**no-promote** · **未 emit** · **未 evaluate／approve** `dgate_H_240`／`dgate_H_60`。

覆蓋：**COMPLETE rank=48/48 daily=3/3 mkt=2/2 stack=1/1**。

## 截面 8×6（`--no-resume` 全重寫）

Ridge／GBDT／XGB／Cat／RF／SVM／KNN／MLP × H{20,40,60,82,120,240} 全成＠08-13。缺 0。

## 方向臂 asof＝08-13（H{20,40,60,82,120,240}）

| 臂 | 結果 |
|---|---|
| DailyLogit／DailyGBDT | v1 champion＝Logit（k=1 hit 0.5509；k=5 hit 0.5194） |
| DailyGBDT_cal | v2 寫 3 674 238 列 |
| MktLogit／MktLogit_v2 | 六窗 P_mkt 全寫；H240＝3758 列（p̄=0.785，**非漲跌幅%**） |
| OOS H240 | 93 折／32 589 列（DirStack 前置；**不** P6 fit／emit） |
| DirStack | 六窗合成完成；H82＝27 029 列；H240＝21 340 列 |
| DirStackM | 月頻 H{20,40,60,82,240}；H82＝23 791 列；**H240＝18 262 列**（p̄=0.616；本包已含，未漏） |
| `dgate_H_*` | `--preregister-all` 冪等 0 列新 draft（既有 draft 仍在；**未 approve**） |

月頻不含 H120（既有 `H_RANKS`）。H240 月頻標籤截尾至 2025-07-31。

## 誠實 SKIP

SeqLSTM／classical TS／threelens／0812 NF 六族／P6 重 fit／promote／SERVE-SWAP／emit B3／`--asof 2026-08-14`／evaluate／approve `dgate_H_240`／`dgate_H_60`／另開 H90。  
未把分數或 `p_beat_median`／`p_mkt`／`p_up` 當成漲跌幅%。

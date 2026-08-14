---
status: executed
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-14
viewpoint: 2026-08-14T12:57+08:00
asof: "2026-08-13"
go: audits/RETRAIN-ALL-ASOF-0813-H240-GO-20260814.md
fired: audits/RETRAIN-ALL-ASOF-0813-H240-FIRED-20260814.md
shell: scripts/run_retrain_all_asof.sh
log: /tmp/retrain-all-asof-2026-08-13/h240-apply.log
paste: "RETRAIN-ALL-0813-H240-EXECUTED | D=2026-08-13 | 48/48 | 6H+Daily+Mkt+DirStack+DirStackM-H240 | resume-5H | no-promote | no-emit | no-fake-B3@08-14"
self_reported: true
layer: "[I]"
---

# EXECUTED｜方向臂鎖最新日＋H240 另開＋重訓＠2026-08-13

`bash scripts/run_retrain_all_asof.sh --date 2026-08-13 --apply` · **RC=0**（約 71 min）  
鎖＝PriceAdj TAIEX 價頂 **2026-08-13**（08-14＝假 B3／FinMind 收盤 n=0，未跑）。  
resume＝1 · **no-promote** · **未 emit** · **未 evaluate／approve** `dgate_H_240`／`dgate_H_60`。

完成後覆蓋：**COMPLETE rank=48/48 daily=3/3 mkt=2/2 stack=1/1**。

## 截面 8×6

5H＠08-13 已齊 → **40 格 `--resume` 跳過**。新訓 **8 格 H240**（Ridge／GBDT／XGB／Cat／RF／SVM／KNN／MLP 全成）。缺 0。

## 方向臂 asof＝08-13（H{20,40,60,82,120,240}）

| 臂 | 結果 |
|---|---|
| DailyLogit／DailyGBDT | v1 champion＝Logit（k=1 hit 0.5509；k=5 hit 0.5194） |
| DailyGBDT_cal | v2 寫 3 674 238 列 |
| MktLogit／MktLogit_v2 | 六窗 P_mkt 全寫；H240＝3758 列（p̄=0.785，**非漲跌幅%**） |
| OOS H240 | 93 折／32 589 列（DirStack 前置；**不** P6 fit／emit） |
| DirStack | 六窗合成完成；H240＝21 340 列（2019-09-30→2025-07-31） |
| DirStackM | 月頻 H{20,40,60,82} 本包重寫；**H240 首輪漏**（`--run-v2` 預設仍 [20,40,60,82]）→ 已改 `M_HORIZONS=(20,40,60,82,240)` 並補跑 **H240＝18 262 列**（2020-04-30→2025-07-31；p̄=0.616） |
| `dgate_H_240` | **preregistered draft only**（review-tier n≈17；econ＝**thin_unestablished**） |

月頻不含 H120（既有 `H_RANKS`；H120 在 DirStack 日頻合成已有）。H240 月頻特徵頂＝2025-08-29（標籤需 +240td，誠實截尾）。

## 誠實 SKIP

SeqLSTM／classical TS／threelens／0812 NF 六族／P6 重 fit／promote／SERVE-SWAP／emit B3／`--asof 2026-08-14`／evaluate／approve `dgate_H_240`／`dgate_H_60`。  
未把分數或 `p_beat_median`／`p_mkt`／`p_up` 當成漲跌幅%。

今晚 21:40 cron 見包已齊＠08-13 會 SKIP（8×6），直到價頂前進。

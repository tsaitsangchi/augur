---
status: go
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-14
viewpoint: 2026-08-14T17:28+08:00
asof: "2026-08-13"
shell: scripts/run_retrain_all_asof.sh
paste: "RETRAIN-ALL-0813-R3-go | lock=價頂 | 8x7+Daily+Mkt+DirStackM | no-resume | H={5,20,40,60,90,120,240} | no-promote | no-emit | no-fake-B3@08-14"
self_reported: true
layer: "[I]"
---

# GO｜方向臂鎖最新日＋全量重訓＠2026-08-13

Steward：「做所有AI預測模型的方向臂改鎖在可更新的最新日期並重新訓練所有模型5天,20天,40天,60天,90天,120天,240天到最近日期」。

## 准

- D＝`check_asof_ready --latest-date`＝**2026-08-13**（PriceAdj TAIEX 價頂；08-14＝假 B3／n_feat=0）
- 方向臂鎖＝價頂（`asof_ready.resolve_lock`；≠ 完整性錨 2026-05-31）
- H 軌＝作業閉集 **H{5,20,40,60,90,120,240}**（5／90＝交易日；H5 ≠ D 軌 k=5；H82 已刪）
- `bash scripts/run_retrain_all_asof.sh --date 2026-08-13 --apply --no-resume`（8×7 全重寫＋Daily*＋MktLogit／v2＋oos-h5/90/240＋DirStack／DirStackM）
- `dgate_H_5`／`dgate_H_60`／`dgate_H_90`／`dgate_H_240` 維持 preregistered draft

## 禁

- `--asof 2026-08-14`／假 B3
- 把 82 插回／把 90 當曆日／把 H5 當 Daily k=5
- promote／SERVE-SWAP／sim `--apply`／emit B3／開 NF
- evaluate／approve 任何 dgate_H_*
- 把分數／`p_beat_median`／`p_mkt`／`p_up` 當漲跌幅％
- 把 H5／H90／H240 塗成 established 或 dead

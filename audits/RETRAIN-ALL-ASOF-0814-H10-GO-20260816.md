---
status: go
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-16
viewpoint: 2026-08-16T16:16+08:00
asof: "2026-08-14"
h10: audits/H10-OPEN-GO-20260816.md
shell: scripts/run_retrain_all_asof.sh
paste: "RETRAIN-ALL-0814-H10-go | lock=價頂 | 8x8+Daily+Mkt+DirStackM | no-resume | H={5,10,20,40,60,90,120,240} | no-promote | no-emit | no-fake-B3@08-15/16"
self_reported: true
layer: "[I]"
---

# GO｜方向臂鎖最新日＋全量重訓＠2026-08-14（含 H10）

Steward：「做所有AI預測模型的方向臂改鎖在可更新的最新日期並重新訓練所有模型5天,10天,20天,40天,60天,90天,120天,240天到最近日期」。

## 准

- D＝`check_asof_ready --latest-date`＝**2026-08-14**（PriceAdj TAIEX 價頂；08-15／08-16＝假 B3）
- 方向臂鎖＝價頂（`asof_ready.resolve_lock`；≠ 完整性錨 2026-05-31）
- H 軌＝作業閉集 **H{5,10,20,40,60,90,120,240}**（交易日；H5 ≠ D 軌 k=5；H10 ≠ KH10；H82 已刪）
- `bash scripts/run_retrain_all_asof.sh --date 2026-08-14 --apply --no-resume`（8×8 全重寫＋Daily*＋MktLogit／v2＋oos＋DirStack／DirStackM）
- `dgate_H_5`／`dgate_H_10`／`dgate_H_60`／`dgate_H_90`／`dgate_H_240` 維持 preregistered draft

## 禁

- `--asof 2026-08-15`／`--asof 2026-08-16`／假 B3
- 把 82 插回／把 H5 當 Daily k=5／把 H10 當 KH10
- promote／SERVE-SWAP／sim `--apply`／emit B3／開 NF
- evaluate／approve 任何 dgate_H_*
- 把分數／`p_beat_median`／`p_mkt`／`p_up` 當漲跌幅％
- 把 H5／H10／H90／H240 塗成 established 或 dead
- 重訓進行中改 `run_retrain_all_asof.sh`

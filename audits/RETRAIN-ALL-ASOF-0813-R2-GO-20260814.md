---
status: go
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-14
viewpoint: 2026-08-14T13:50+08:00
asof: "2026-08-13"
shell: scripts/run_retrain_all_asof.sh
paste: "RETRAIN-ALL-0813-R2-go | lock=價頂 | 8x6+Daily+Mkt+DirStackM | no-resume | H90=82td | no-promote | no-emit | no-fake-B3@08-14"
self_reported: true
layer: "[I]"
---

# GO｜方向臂鎖最新日＋全量重訓＠2026-08-13

Steward：「做所有 AI 預測模型的方向臂改鎖在可更新的最新日期並重新訓練所有模型 20／40／60／90／120／240 天到最近日期」。

## 准

- D＝`check_asof_ready --latest-date`＝**2026-08-13**（PriceAdj TAIEX 價頂；08-14＝假 B3／n_feat=0）
- 方向臂鎖＝價頂（`asof_ready.resolve_lock`；≠ 完整性錨 2026-05-31）
- H 軌＝憲章封閉集 **H{20,40,60,82,120,240}**。口語「90 天」＝該槽之 **82 交易日**（P2-1 A，2026-07-11）；**不**另開 H90、**不**把 82 從 CHECK 刪掉、**不**把 90 曆日當成交易日窗
- `bash scripts/run_retrain_all_asof.sh --date 2026-08-13 --apply --no-resume`（全日 8×6 重寫＋Daily*＋MktLogit／v2＋DirStack／DirStackM）
- `dgate_H_240` 維持 preregistered draft（`--preregister-all` 冪等）

## 禁

- `--asof 2026-08-14`／假 B3
- 另開 H90／改 CHECK 含 90／刪 82
- promote／SERVE-SWAP／sim `--apply`／emit B3／開 NF／evaluate／approve `dgate_H_240`／`dgate_H_60`
- 把分數／`p_beat_median`／`p_mkt`／`p_up` 當漲跌幅％
- 把 H240 塗成 established 或 dead

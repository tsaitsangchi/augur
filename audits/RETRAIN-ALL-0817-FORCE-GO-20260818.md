---
status: go
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-18
viewpoint: 2026-08-18T11:23+08:00
asof: "2026-08-17"
shell: scripts/run_asof_collect_train_verify.sh
paste: "做所有AI預測模型的方向臂改鎖在可更新的最新日期並重新訓練所有模型5/10/20/40/60/90/120/240天到最近日期"
self_reported: true
layer: "[I]"
---

# GO｜價頂 RETRAIN-ALL＠2026-08-17 · 方向臂鎖最新日 · 八窗重 fit

Steward 11:23 明示。可更新最新日＝PriceAdj TAIEX **2026-08-17**（08-18＝假 B3，不當 as-of）。

包＠08-17 已齊 → 同尺重訓須 `--force`；內殼 `--no-resume` 否則 64 格 resume 跳過。DATE＝價頂 → 方向臂 Daily／Mkt／DirStackM **會**重訓並鎖在 08-17。

## 准

- `bash scripts/run_asof_collect_train_verify.sh --date 2026-08-17 --apply --track all --force`
- 截面 8 族 × H_TRACK 八窗重 fit
- 方向臂活鎖＝價頂 08-17（重訓、不往回搬）
- 不 emit B3；不改 standing 20,60；不 promote

## 禁／誠實 SKIP

- `--date 2026-08-18`
- SERVE-SWAP；sim-apply；開 NF；P6 重 fit（另句）；VECM／TCN／NB／RL／SeqLSTM
- 八窗改出門（仍須雙明示）

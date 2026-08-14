---
status: go
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-14
viewpoint: 2026-08-14T10:00+08:00
asof: "2026-08-13"
shell: scripts/run_retrain_all_asof_daily.sh
paste: "RETRAIN-ALL-0813-go | lock=價頂 | 8x5+Daily+Mkt+DirStackM | resume | no-promote | no-emit | no-fake-B3@08-14"
self_reported: true
layer: "[I]"
---

# GO｜全模型重訓到可更新最新日＠2026-08-13

Steward：「做所有 AI 預測模型的方向臂改鎖在可更新的最新日期並重新訓練所有模型 20／40／60／82／120 天到最新日期」。

## 准

- D＝`check_asof_ready --latest-date`＝**2026-08-13**（PriceAdj 價頂；08-14 仍假 B3）
- `bash scripts/run_retrain_all_asof_daily.sh --apply`（內殼 resume＝1）
- 截面 8 族 × H{20,40,60,82,120} ＋ Daily* ＋ MktLogit／v2 ＋ DirStack／DirStackM

## 禁

- `--asof 2026-08-14`／假 B3  
- promote／SERVE-SWAP／sim `--apply`／emit B3／開 NF  
- `--no-resume`（08-13 已有 L2 13 格，勿重燒）

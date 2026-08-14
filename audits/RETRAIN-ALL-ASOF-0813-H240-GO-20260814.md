---
status: go
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-14
viewpoint: 2026-08-14T11:40+08:00
asof: "2026-08-13"
shell: scripts/run_retrain_all_asof.sh
paste: "RETRAIN-ALL-0813-H240-go | lock=價頂 | H240-open | 8x6+Daily+Mkt+DirStackM | resume-5H | no-promote | no-emit | no-fake-B3@08-14"
self_reported: true
layer: "[I]"
---

# GO｜方向臂鎖最新日＋另開 H240＋重訓＠2026-08-13

Steward：「做所有 AI 預測模型的方向臂改鎖在可更新的最新日期並重新訓練所有模型 20／40／60／82／120／240 天到最近日期」。

## 准

- D＝`check_asof_ready --latest-date`＝**2026-08-13**（PriceAdj 價頂）
- 另開方向／截面 **H240**（DDL CHECK 含 240；`econ_verdict_rule`＝**thin_unestablished**）
- `bash scripts/run_retrain_all_asof.sh --date 2026-08-13 --apply`（resume＝1：5H＠08-13 已齊則跳過；**新訓 H240**）
- 截面 8 族 × H{20,40,60,82,120,240} ＋ Daily* ＋ MktLogit／v2 ＋ DirStack／DirStackM
- H240 OOS：`build_probability_oos_sample --run --horizon 240 --asof 2026-08-13`（供 DirStack；**不** P6 fit／emit）
- `dgate_H_240` 僅 preregister draft

## 禁

- `--asof 2026-08-14`／假 B3  
- promote／SERVE-SWAP／sim `--apply`／emit B3／開 NF／evaluate／approve `dgate_H_240`  
- 把 H240 塗成 established 或 dead（無經濟終關）
- 併入 v2 K=4／arena／threelens

---
status: fired
series: s4_s5_verify
track: RETRAIN-ALL
date: 2026-08-13
viewpoint: 2026-08-13T15:55+08:00
asof: "2026-08-12"
shell: scripts/run_retrain_all_asof.sh
paste: "DIRLOCK-latest | H60-open | RETRAIN-ALL-0812 --no-resume | no-promote | no-evaluate | no-fake-B3"
self_reported: true
layer: "[I]"
---

# FIRED｜方向臂另開 H60＋強制重訓＠2026-08-12

`bash scripts/run_retrain_all_asof.sh --date 2026-08-12 --apply --no-resume`

## 已改（訓練封閉集）

方向 H 軌＝**H{20,40,60,82,120}**（H60 新開）。  
落地：`train_market_direction`／`train_direction_stack`／`build_direction_stack_monthly`／`run_direction_econ_eval`／`preregister_direction_gate` v1。

- `dgate_H_60`＝**preregistered** draft（未 approve、不 evaluate）
- **不**併入 v2 K=4／arena／threelens／combo
- 月頻 stack `--since 2017-01-01`（H60 rank 需全史）
- no-promote／no-SIM-apply／08-13 仍假 B3

*fired · 候 EXECUTED。*

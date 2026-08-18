---
status: executed
series: s4_probability
date: 2026-08-17
freeze: "2026-08-14"
depends_on:
  - audits/P6-REFIT-FREEZE-20260814-GO-20260817.md
  - audits/P6-REFIT-FREEZE-20260814-FIRED-20260817.md
  - audits/M9-P6-RECON-0814-20260817.md
log_dir: /tmp/p6-refit-20260814
paste: "P6-REFIT-FREEZE-2026-08-14-go"
viewpoint: 2026-08-17T17:18+08:00
elapsed_ms: 1400327
self_reported: true
layer: "[I]"
---

# EXECUTED｜P6 REFIT FREEZE→2026-08-14 · H20＋H60

> **GO** 跑完 · `PIPELINE_COMPLETE` · rc=0 · ≠改 dgate · ≠確立級 · ≠換 RankRidge 主模 · ≠假 B3

## 結果

| 步 | 產出 |
|---|---|
| OOS H20 | **104** 折／**35,055** 列（末折 panel＝2026-06-30，exit＝2026-07-30） |
| OOS H60 | **102** 折／**34,607** 列（末折 panel＝2026-04-30，exit＝2026-07-29） |
| fit H20 | `platt_RankRidge_h20_asof2026-08-14_ge10dbc2` · 折 103/104 · Brier **0.2476** vs 0.2500 · ECE **0.0016** · purge=True |
| fit H60 | `platt_RankRidge_h60_asof2026-08-14_ge10dbc2` · 折 101/102 · Brier **0.2452** vs 0.2500 · ECE **0.0076** · purge=True |
| emit＠08-14 | H20／H60 各 **286** 檔 → 上列新 calibrator |

| emit 誠實形（親查 `prediction_probability`＠08-14） | |
|---|---|
| H20 | p∈[0.413,0.585] · econ=**dead** · 286 列 |
| H60 | p∈[0.373,0.626] · econ=**thin_unestablished** · 286 列 |

## 誠實界

- FREEZE 已對齊價頂 **08-14**；08-07 校準器仍在庫、不再被 tip emit 引用。
- Brier／ECE／OOS 折數與 08-07 實質同形：08-07→08-14 之間**沒有新完成的 purge 折**（H20 末折 exit 仍 07-30；H60 仍 07-29）。前進的是校準器 id 與 tip 對齊，不是新資訊。
- 未改 `evaluated_pass`／未宣稱可交易／未重訓 RankRidge 主模型。
- 未 `--all` 其餘 H_TRACK；擴窗仍須另 plan＋GO。
- 未 SERVE-SWAP。

log：`/tmp/p6-refit-20260814/{oos,fit,emit}-h{20,60}.log`

*完。*

---
status: executed
series: s4_probability
date: 2026-08-07
asof_freeze: "2026-07-31"
depends_on:
  - audits/P6-REFIT-0731-GO-20260807.md
log: /tmp/p6-refit-0731/run.log
emit_h60_tip_log: /tmp/p6-refit-0731/emit-h60-0806.log
paste: "P6-REFIT-0731-go | fit+emit | hold-#1"
viewpoint: 2026-08-07T18:45+08:00
self_reported: true
---

# EXECUTED｜P6-REFIT-0731 · OOS＋fit＋emit · 2026-08-07

> **GO**：H20／H60 · FREEZE=`2026-07-31` · fit＋emit · hold-#1 · 未改 dgate · 未重訓 Ridge  
> 總耗時 ≈24min（OOS 為主）

## 結果

| 步 | 產出 |
|---|---|
| OOS H20 | **104** 折／**35,055** 列（至 panel 06-30／exit≤07-30） |
| OOS H60 | **102** 折／**34,607** 列（至 panel 04-30／exit≤07-29） |
| fit H20 | `platt_RankRidge_h20_asof2026-07-31_ga329426` · Brier **0.2476** · ECE 0.0016 · purge=True |
| fit H60 | `platt_RankRidge_h60_asof2026-07-31_ga329426` · Brier **0.2452** · ECE 0.0076 · purge=True |
| emit H20＠**07-31** | **204** 檔 · econ=**dead** · p∈[0.413,0.585] |
| emit H60＠**07-31** | **✗** 無 `prediction_values`＠07-31 |
| emit H60＠**08-06**（補） | **285** 檔 · econ=thin_unestablished · 校準器＝上列 0731 · Steward 明示 |

## 誠實界

- 機率仍近 0.5 窄帶＝預期  
- ≠確立級；H20 tip emit 仍 **dead**  
- H40／82／120 校準器仍為舊 08-04 錨（本 GO 未動）

*完。*

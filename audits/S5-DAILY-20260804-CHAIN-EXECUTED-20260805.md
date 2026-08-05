---
status: executed
series: s5_predict
depends_on:
  - audits/S5-DAILY-20260804-CHAIN-GO-20260805.md
---

# EXECUTED｜日頻 2026-08-04 特徵／出單／emit · 2026-08-05

> **GO**：`audits/S5-DAILY-20260804-CHAIN-GO-20260805.md`  
> **授權**：`S5-DAILY-2026-08-04-CHAIN-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> **self-reported（#32a）**。

## 結果

| 步 | 產出 |
|---|---|
| `build_feature_panel --panels 2026-08-04 --asof` | **745** 股、**27,371** 值 |
| `build_core_universe --since 2014-01-01 … --asof` | 108 panel；**2026-08-04 核心＝204**（06-30 仍 225；07-31＝204） |
| `predict_asof --run --horizon 20 --asof 2026-08-04` | 寫庫；2330＝rank **#1**（score≈0.5313） |
| `--emit --horizon 20 --asof 2026-08-04` | **204** 檔；p∈[0.411,0.587]；econ=dead |

## 顧問驗收

`build_single_ticker_rel_payload("2330",20).as_of` → **2026-08-04**  
2330：`p_beat_median≈0.587`／`rank_pctile=1.0`／econ=dead  

## 誠實邊界

- 校準器仍為 `platt_h20_asof2026-05-31_*`（未重 fit；只把既有 Platt 套到新面板分位）  
- 絕對方向 GATE 未過；≠可交易確立級  
- `daily_direction_feature_values` 本輪未重跑（本鏈＝`feature_values`＋RankRidge）

log：`/tmp/s5-daily-20260804/`

*完。*

---
status: executed
series: s5_predict
depends_on:
  - audits/S3-JULY-CORE-FEAT-EXECUTED-20260805.md
---

# EXECUTED｜predict H20＋P6 emit＠2026-07-31 · 2026-08-05

> **授權**：Steward AskQuestion `run_predict_emit`  
> **前置**：`S3-JULY-CORE-FEAT-EXECUTED`（特徵＋core asof 已含 07-31）  
> **硬邊界**：skip-sync／no-SIM-apply；未改 DEFAULT_FREEZE＝2026-05-31；校準器仍為既有 `platt_h20_asof2026-05-31_*`（套用至新面板分位）。  
> **self-reported（#32a）**。

## 做了什麼

| 步 | 結果 |
|---|---|
| `predict_asof.py --run --horizon 20 --asof 2026-07-31` | 寫 `prediction_values`；model=`RankRidge_H20_2026-06-30_seed42_…`；prodset 3 feats；2330＝rank#1 |
| `calibrate_relative_probability.py --emit --horizon 20 --asof 2026-07-31` | **204** 檔；p∈[0.411,0.587]；econ=dead |

## 驗收

| 查 | 值 |
|---|---|
| `prediction_probability` H20 panels | 2026-05-31（339）＋**2026-07-31（204）** |
| H20 `max(panel_date)` | **2026-07-31** |
| 2330＠07-31 | p_beat_median≈**0.587**；rank_pctile＝1.0；econ＝dead |
| `build_single_ticker_rel_payload("2330",20).as_of` | **2026-07-31** |

## 與「08-04」的差距（誠實）

- 月盤／核心錨＝**07-31**（7 月末交易日）；價雖到 08-04，本鏈未做日頻特徵 panel＠08-04。  
- 顧問再問「未來30天」應顯示 **as-of 2026-07-31**（須重載題；live 服務逐請求讀表、一般無需重啟）。  
- 絕對方向 GATE 仍未過；econ_verdict＝dead 不變。

log：`/tmp/s3-july-20260805/predict-h20-0731-run.log`／`emit-h20-0731.log`

*完。*

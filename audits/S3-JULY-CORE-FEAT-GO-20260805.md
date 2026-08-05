---
status: go
series: s3_features
depends_on:
  - audits/WM36-PRICEADJ-P2-EXECUTED-20260805.md
  - audits/S3-WAVE-A-EXECUTED-20260804.md
---

# GO｜S3 July 特徵月盤＋core asof 補齊 · 2026-08-05

> **授權**：Steward AskQuestion `go_s3_core_together` → `go_exec_now`  
> paste：`S3-JULY-CORE-FEAT-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> **目標**：為顧問／相對機率脫離唯 `prediction_probability.panel_date=2026-05-31` 鋪路上游——本輪只寫 **特徵＋core**，**不做** predict／emit／SIM-apply。  
> **self-reported（#32a）**。

## 為何要這兩步

- 顧問單股相對機率取 `max(panel_date)` from `prediction_probability` → 庫內**僅** 2026-05-31。  
- 欲捲到 ≈08-04：需 `prediction_values`＠新 asof → 需特徵矩陣＋核心宇宙。  
- 現況：`feature_values`／`core_universe_asof` **皆止於 2026-06-30**；價已到 08-04。  
- 月盤慣例面板＝**2026-07-31**（7 月最後交易日）；非日頻 08-04 面板。

## 執行序（硬順序）

1. `build_feature_panel.py --panels 2026-07-31 --asof`  
   （`--panels` 可新建未存在之 panel；`--asof`＝現有 core 宇宙股、非全 roster）  
2. `build_core_universe.py --liquidity-pct 25 --exempt-revenue-financial --asof`  
   （**禁**只 `--since 2026-07-31`：`build_universe_asof` 會 `DELETE` 全表再灌，必須帶齊全部 `feature_values` panel）

## 本輪不做

- `predict_asof`／`calibrate_relative_probability --emit`  
- FinMind／FRED；sim `--apply`  
- `prediction_probability` 滾動

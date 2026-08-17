---
title: E4 漏斗墓碑 — range_mean_20d
status: dead_prediag
series: econ_establishment
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T09:32+08:00
layer: "[I]"
candidate: range_mean_20d
died_at: 0
until: "2026-04-30"
h: 60
self_reported: true
paste: "E4-feat-go | candidate=range_mean_20d | isolation-table"
---

# 墓碑｜`range_mean_20d`（死於漏斗 0 預診）

> **一句**：對現役 3 欄看起來乾淨（ρmax 0.221），對 canonical 是波動族重編碼——vs `volatility_60d` **|median ρ|=0.901**。未建值、未跑 IC／增量／#14、未付 N、未提拔。  
> **until／H**：與 E3 同尺。hash 2014=`01656be2c953f7e0`、2021=`ca1b6ff3791f6f15`。

## 死點

漏斗 **(0) 預診**。門檻：max |median Spearman ρ| < 0.6 vs 現役 **且** vs canonical\{自己}。

| 對照 | max \|median ρ\| | 最近鄰 | 判 |
|---|---:|---|---|
| 現役 3 | 0.221 | `lending_fee_rate_mean_30d` | 過（短名單只量這層） |
| canonical\{自己} | **0.901** | **`volatility_60d`** | **死** |

canonical 最近 5：

| 欄 | \|median ρ\| |
|---|---:|
| `volatility_60d` | **0.901** |
| `margin_usage_ratio` | **0.605**（也過不了 0.6） |
| `turnover_mean_20d` | 0.595 |
| `dollar_volume_log_20d` | 0.584 |
| `price_to_10yr` | 0.431 |

現役 3：`cycle_position_252d` 0.125／`inst_cumflow_position_120d` 0.162／`lending_fee_rate_mean_30d` 0.221。

## 後續道次

未跑。(1) 建值未寫（staging 本欄 0→0）。(2)(3)(4)(5) 停。

`volatility_20d` 早因與本欄 +0.94 共線被剪。本輪等於把同一振幅族再送一次漏斗——對 3 欄現役正交，對 34 欄研究尺是冗餘。

## N／隔離

- 不付 N。`trial_ledger` 仍 32。`econ_eval_run` 仍 9。  
- 未寫 `feature_values`。`feature_candidate_values` 總列 819467 未動；本欄 0。  
- prodset active 仍 3。H20 `dead`／H60 `thin`。閘仍 `approved`。  
- **不是** `PROMOTE-feat-go`。

機讀：`reports/augur_econ_e4_feat_range_mean_20d_r17_20260817.json`。

## 短名單的教訓

E4 短名單的「就緒」只預診了現役 3 欄。漏斗 (0) 明文是現役／canonical。下一次 `E4-feat-go` 仍須過 canonical ρ，不能把短名單當成已過 (0)。

## 下一句（若要繼續一次一支）

短名單第二就緒是 `dividend_yield`（對現役 ρmax 0.130、HAC +3.71）。**未**在本 GO 預跑它對 canonical 的 ρ。要跑另貼：

```text
E4-feat-go | candidate=dividend_yield | isolation-table
```

不要 `E5-evaluate-go`。不要無 GO 提拔。不要把 `volatility_60d` 當下一支（與死者共線）。

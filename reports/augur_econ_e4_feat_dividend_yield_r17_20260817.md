---
title: E4 漏斗墓碑 — dividend_yield
status: dead_prediag
series: econ_establishment
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T09:39+08:00
layer: "[I]"
candidate: dividend_yield
died_at: 0
until: "2026-04-30"
h: 60
self_reported: true
paste: "E4-feat-go | candidate=dividend_yield | isolation-table"
---

# 墓碑｜`dividend_yield`（死於漏斗 0 預診）

> **一句**：對現役 3 欄很乾淨（ρmax 0.129），對 canonical 貼著估值族——vs `pe_ratio` **|median ρ|=0.616**，剛過不了 0.6。未建值、未 #14、未付 N、未提拔。  
> **不放寬**：0.616 不是 0.599。門檻不因「只差一點」移動。

## 死點

漏斗 **(0) 預診**。until／H／hash 與 E3、`range_mean_20d` 墓碑同尺。

| 對照 | max \|median ρ\| | 最近鄰 | 判 |
|---|---:|---|---|
| 現役 3 | 0.129 | `inst_cumflow_position_120d` | 過 |
| canonical\{自己} | **0.616** | **`pe_ratio`** | **死** |

canonical 最近 5：

| 欄 | \|median ρ\| |
|---|---:|
| `pe_ratio` | **0.616** |
| `range_mean_20d` | 0.425 |
| `volatility_60d` | 0.391 |
| `turnover_mean_20d` | 0.262 |
| `dollar_volume_log_20d` | 0.255 |

現役 3：`cycle_position_252d` 0.095／`inst_cumflow_position_120d` 0.129／`lending_fee_rate_mean_30d` 0.038。

## 後續道次

未跑。(1) 未寫（staging 本欄 0→0）。(2)(3)(4)(5) 停。

對稱：短名單就緒的 `pe_ratio` 對 `dividend_yield` 也是 0.616，**預期同死**，不要當下一支碰運氣。

## N／隔離

- `trial_ledger` 仍 32。`econ_eval_run` 仍 9。  
- 未寫 `feature_values`。staging 本欄 0；總列 819467。  
- prodset 仍 3。H20 `dead`／H60 `thin`。

機讀：`reports/augur_econ_e4_feat_dividend_yield_r17_20260817.json`。

## 兩支墓碑合起來的讀法

短名單「就緒 5」只預診了現役 3 欄。對 canonical：

| 短名單就緒 | 對 canonical 最近鄰 | 漏斗 (0) |
|---|---|---|
| `range_mean_20d` | `volatility_60d` 0.901 | **已死** |
| `dividend_yield` | `pe_ratio` 0.616 | **已死** |
| `pe_ratio` | `dividend_yield` 0.616 | 預期死、勿送 |
| `margin_usage_ratio` | vs `range_mean_20d` 0.605（前墓碑） | 預期死、勿送 |
| `sbl_short_balance_log` | 尚未量 | 唯一未暗示死亡的就緒 |

34 欄研究尺強，多半是**族內一捆**，不是「抽一欄加進 3 欄就正交」。把 canonical 整包倒進 prodset 仍禁。

## 下一句（另貼才跑）

若要繼續一次一支，只剩就緒裡尚未被暗示死亡的：

```text
E4-feat-go | candidate=sbl_short_balance_log | isolation-table
```

不要 `E5-evaluate-go`。不要放寬 0.6。不要送 `pe_ratio`／`margin_usage_ratio`／波動族。

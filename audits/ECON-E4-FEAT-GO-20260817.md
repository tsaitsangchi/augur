---
status: go
series: econ_establishment
round: r17
date: 2026-08-17
viewpoint: 2026-08-17T09:30+08:00
paste: "E4-feat-go | candidate=range_mean_20d | isolation-table"
plan: reports/augur_econ_prove_edge_plan_r17_20260817.md
shortlist: reports/augur_econ_e4_shortlist_r17_20260817.md
self_reported: true
layer: "[I]"
---

# GO｜E4 漏斗（一支：`range_mean_20d`）

## 凍結判準（跑前鎖；與 07-17 Phase 1 同尺，值不改）

候選＝`range_mean_20d`。until＝2026-04-30。H＝60。一次一支。死即停。

| 道 | 過 | 不過 |
|---|---|---|
| (0) 預診 | vs 現役 3 **且** vs canonical\{自己}：max \|median ρ\| < 0.6 | 墓碑、不建值、不付 N |
| (1) 建值 | 只寫 `feature_candidate_values`（從 `feature_values` 拷 as-of≤until）；**不**寫生產表 | — |
| (2) IC | as-of rank IC vs H60；HAC lag=2 \|t\|≥2；同號 ≥0.60；禁 iid | 停、staging 清本欄、不付 N |
| (3) 去相關 | 同 (0) 門檻（staging 值） | 停、清本欄、不付 N |
| (4) 增量 | RankRidge 3 vs 3+1；2014 與 2021 非重疊 WF **皆** Δ mean IC > 0（Ridge 無 seed 方差，改窗穩） | 停、清本欄、不付 N |
| (5) #14 | 僅 (0)–(4) 全過才跑。凍結細胞：H60 LO top10% 等權 cost 0.585% seed 42。在位×廣、since 2014 與 2021。過關： **2021 在位** Δ淨 Sharpe > +0.05 **且** MaxDD 不惡化（signed，容差 0.005）。research、**不付 N** | 死、清本欄、不入 prodset |

## 禁

- `PROMOTE-feat-go`／改 `evolution_production_feature_set`
- 寫 `trial_ledger`、evaluate 閘、改 verdict、救 H20
- 一次多支、寫 `feature_values`、median-fill
- 假 B3

---
title: B3 五窗／SERVE 五 H go-plan（高門檻 · 零默換）
status: plan_first
series: daily_b3
date: 2026-08-08
paste: "B3-HORIZONS-FIVE-go-plan | FZ/GATE-keep | no-serve-swap-default | tip=2026-08-07"
prior_b3: audits/VERIFY-B3-20260807-EXECUTED-20260808.md
prior_serve: audits/SERVE-SWAP-0731-EXECUTED-20260807.md
layer: "[I]"
self_reported: true
---

# B3-HORIZONS-FIVE／SERVE-FIVE-H · plan-first

> **一句**：現役 B3＝**horizons=20,60**；五窗（20／40／60／82／120）曾於 SERVE-SWAP-0731 存在，但 tip＠08-07 pp **僅兩 H**。本檔＝**是否恢復五窗 B3 與／或五 H serve** 的決策 plan；**預設不換**。

## 分徑（須雙／分明示）

| 徑 | 內容 | 執行句 |
|---|---|---|
| **B3-only** | `run_daily_asof_predict --horizons 20,40,60,82,120`（需對應模型／校準器齊） | `B3-HORIZONS-FIVE-go` |
| **SERVE-five** | tip 掛齊五 H RankRidge＠某 asof | `SERVE-FIVE-H-go` |
| **hold** | 維持 20／60 | 無 |

## 先決

- registry／artifact 五 H＠釘 asof 皆在  
- 校準器（P6）對齊目標窗  
- H20 econ=dead 誠實披露不變

```text
B3-HORIZONS-FIVE-plan-adopt | FZ/GATE-keep | no-serve-swap-default
# ≠ 默執行；≠ 與本合集其他刀綁死
```

*完。*

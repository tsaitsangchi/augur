---
status: adopted
series: s4_s5_verify
track: PATH-HIT-LIFT
date: 2026-08-20
viewpoint: 2026-08-20T09:58+08:00
product_id: PATH-HIT-LIFT-v1
plan: reports/augur_path_hit_lift_plan_r20_20260820.md
layer: "[I]"
self_reported: true
paste: "PATH-HIT-LIFT-plan-adopt | 雙尺=勝率+扣成本均酬 | 不放寬四閘 | no-promote | standing=20,60 | no-fake-B3@08-20 | 禁OOS最長持有當冠 | 條件≠可交易"
---

# ADOPTED｜路徑閘做多勝率逐步提高（P0）

Steward 貼：

```text
PATH-HIT-LIFT-plan-adopt | 雙尺=勝率+扣成本均酬 | 不放寬四閘
| no-promote | standing=20,60 | no-fake-B3@08-20
| 禁OOS最長持有當冠 | 條件≠可交易
```

## 生效

| 角色 | 路徑 |
|---|---|
| 本軌定義 SSOT | `reports/augur_path_hit_lift_plan_r20_20260820.md` |
| 父手冊 | PATH-OPT-OPS-v1（子計畫，不取代 r19） |
| 日常出單 | 仍 standing **H20+H60 RankRidge** |

`adopt`＝凍結基線、切窗、雙尺、通過線、槍序。**不是** P1 診斷、不是改四閘、不是可交易、不是 promote、不是寫 `prediction_values`。

## 本 paste 鎖定

| 條 | 意思 |
|---|---|
| 雙尺 | 勝率 **與** 扣成本後均酬／中位；缺一不算過 |
| 不放寬四閘 | L-A…D 維持 UP-PULL-v1；加濾＝新 ID |
| no-promote | 不換冠、不 SERVE-SWAP |
| standing=20,60 | 日常出門窗不變 |
| no-fake-B3@08-20 | 日曆 08-20 不當 as-of；價頂＝**2026-08-19** |
| 禁 OOS 最長持有當冠 | T40／抱牢只對照；P4 短持有優先 |
| 條件≠可交易 | 勝率不是下單指令 |

## 凍結基線（持有 30 日，2005-01-03～2026-08-19）

| 濾 | 毛利率>0 | 扣成本後>0 | 樣本 |
|---|---:|---:|---:|
| 全宇宙四閘 | 51.2% | 48.9% | 58,865 |
| 全宇宙四閘且八窗 | 52.9% | 50.5% | 32,511 |

P2 起 OOS 通過線：扣成本勝率 ≥ 同窗基線 **+3pp**，均酬>0、中位≥0、樣本≥500、IS 同號。

P1 未開。下一句見計畫 §8。

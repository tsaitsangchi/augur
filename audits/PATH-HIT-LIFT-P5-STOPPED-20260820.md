---
status: stopped
series: s4_s5_verify
track: PATH-HIT-LIFT
date: 2026-08-20
viewpoint: 2026-08-20T10:08+08:00
product_id: PATH-HIT-LIFT-v1
verdict: no_stepwise_edge
died_at: P1
plan: reports/augur_path_hit_lift_plan_r20_20260820.md
adopted: audits/PATH-HIT-LIFT-PLAN-ADOPTED-20260820.md
diag: audits/PATH-HIT-DIAG-EXECUTED-20260820.md
json: audits/PATH-HIT-DIAG-0819.json
layer: "[I]"
self_reported: true
paste: "PATH-HIT-LIFT-stop | P5 | 路徑閘短線勝率無逐步解 | no-promote | standing=20,60"
---

# 墓碑｜PATH-HIT-LIFT P5

> **一句**：全宇宙做多四閘、持有 30 日，勝率是擲硬幣附近；加八窗、分桶都抬不到通過線。**路徑閘短線勝率無逐步解。** 河閉。不放寬四閘。不 promote。standing 仍 H20+H60。

Steward 貼：

```text
PATH-HIT-LIFT-stop | P5 | 路徑閘短線勝率無逐步解 | no-promote | standing=20,60
```

## 死點

P1 診斷＠價頂 **2026-08-19**（IS 2018–24／OOS 2025-01～2026-06）。沒有一條分桶同時：IS 與 OOS 同號抬升、OOS 扣成本勝率 ≥ 基線 +3pp、中位≥0、n≥500。

| 基線（hold=30，t+1，streak 首日） | 毛>0 | 扣成本>0 | n |
|---|---:|---:|---:|
| 四閘 2005–08-19 | 51.2% | 48.9% | 58,865 |
| 四閘且八窗 | 52.9% | 50.5% | 32,511 |
| 四閘 IS | 49.7% | 47.4% | 20,099 |
| 四閘 OOS | 50.9% | 49.0% | 2,935 |

已證偽：再加 H20 硬閘（+1.7pp、樣本腰斬）；dd20 甜區（IS／OOS 不同號）；成交額地板（IS／OOS 反轉）。H40>30% 兩窗都差，剔除仍遠低於 +3pp。

## 未開即停

P2 SWEET、P3 LIQ、P4 EXIT **未開、不開**。再開須**新產品 ID**，不得續本河碰運氣。

## 不變

standing **20,60** RankRidge。四閘 θ 不放寬。未寫 `prediction_values`。條件 ≠ 可交易。08-20＝假 B3。

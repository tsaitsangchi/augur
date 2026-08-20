---
status: executed
series: s4_s5_verify
track: PATH-HIT-LIFT
date: 2026-08-20
viewpoint: 2026-08-20T10:05+08:00
product_id: PATH-HIT-DIAG-v1
asof: "2026-08-19"
price_max: "2026-08-19"
json: audits/PATH-HIT-DIAG-0819.json
script: scripts/probe_path_hit_diag.py
go: audits/PATH-HIT-DIAG-GO-20260820.md
fired: audits/PATH-HIT-DIAG-FIRED-20260820.md
plan: reports/augur_path_hit_lift_plan_r20_20260820.md
layer: "[I]"
self_reported: true
paste: "PATH-HIT-DIAG-go | asof=2026-08-19 | hold=30 | dry | no-promote"
---

# EXECUTED｜PATH-HIT-DIAG P1＠2026-08-19

dry-run 零寫庫。四閘未改。standing 未改。診斷 ≠ 新濾。

## 總覽（持有 30 日、t+1、streak 首日）

| 窗 | n | 毛>0 | 扣成本>0 | 均 | 中位 |
|---|---:|---:|---:|---:|---:|
| 全段 | 58,865 | 51.2% | 48.9% | +2.38% | +0.35% |
| contrast 2005–17 | 35,777 | 52.0% | 49.8% | +2.40% | +0.54% |
| **IS 2018–24** | 20,099 | **49.7%** | 47.4% | +2.01% | 0% |
| **OOS 2025-01～2026-06** | 2,935 | **50.9%** | 49.0% | +4.88% | +0.39% |

與 P0 基線全段 51.2% 一致。OOS 均酬高、中位仍接近 0（2026 大多頭偏態）。2025 單年毛>0＝47.4%，2026＝54.6%。

## 分桶（只讀；未改 θ）

**回撤 dd20**：IS 淺帶 [−6%,−3%] 最好（51.8%）；甜區 [−9%,−6%) IS **更差**（48.4%）。OOS 相反，甜區 52.7%、淺帶 49.7%。**不同號** → 不得把「靠近 −8%」當 P2。

**H40**：兩窗都是 **>30% 最差**（IS 45.4%／OOS 44.7%）。IS 最好是薄漲 (0,5%] 53.5%，OOS 該桶只有 50.9%＝基線，**抬升不同號**。排除 >30% 的粗估抬升遠低於 +3pp。

**成交額**：IS 低量 Q1 最好（53.0%）、高量 Q4 最差（47.6%）；OOS **反轉**（Q1 46.8%／Q4 53.1%）。**不同號** → 不得把流動性地板當下一槍默開。

**年**：IS 2018 42.4%、2022 39.5% 拖累；2023 57.6%。不是穩定 α。

## 結論（P2 未授權）

沒有一條分桶同時滿足：IS 與 OOS 同號抬升、OOS 扣成本勝率 ≥ 基線 +3pp、中位≥0、n≥500。P2 SWEET／P3 LIQ **不要因本槍默開**。下一槍須 Steward 另點名；或 P5 停。

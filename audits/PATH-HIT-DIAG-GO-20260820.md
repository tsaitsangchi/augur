---
status: go
series: s4_s5_verify
track: PATH-HIT-LIFT
date: 2026-08-20
viewpoint: 2026-08-20T09:59+08:00
product_id: PATH-HIT-DIAG-v1
parent: PATH-HIT-LIFT-v1
plan: reports/augur_path_hit_lift_plan_r20_20260820.md
adopted: audits/PATH-HIT-LIFT-PLAN-ADOPTED-20260820.md
shell: scripts/probe_path_hit_diag.py
asof: "2026-08-19"
price_max: "2026-08-19"
layer: "[I]"
self_reported: true
paste: "PATH-HIT-DIAG-go | asof=2026-08-19 | start=2005-01-03 | hold=30 | t+1 | streak-first | IS=2018-2024 | OOS=2025-01..2026-06 | dry | no-promote"
---

# GO｜PATH-HIT-DIAG P1

診斷四閘做多通過段：年／dd20 子帶／H40 深淺／20 日成交額。持有 30 日、t+1、streak 首日。IS／OOS 分開。不改 θ、不寫庫、不 promote。

| 准 | 禁 |
|---|---|
| 分桶報勝率、扣成本均／中位、n | 放寬四閘；把診斷當濾 |
| asof＝價頂 08-19 | 假 B3＠08-20 |
| dry-run JSON＋audit | 寫 prediction_values；改 standing |

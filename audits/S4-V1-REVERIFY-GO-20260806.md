---
status: go_accepted
series: s4_s5_verify
track: V1
date: 2026-08-06
viewpoint: 2026-08-06T16:46+08:00
paste: "S4-V1-REVERIFY-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | asof=READY"
scope: "H60 core · B2_ridge + M1_gbdt×{1,2,42} · prodset · until=2026-06-30"
steward_scope: h60_core
plan: reports/augur_s4_other_model_verify_matrix_plan_20260806.md
priceadj_live: "2026-08-05"
oos_until: "2026-06-30"
hold_b3: true
nf_pause: keep
self_reported: true
---

# GO｜S4-V1-REVERIFY · H60 核心 · 2026-08-06

```text
S4-V1-REVERIFY-go | FZ/GATE-keep | skip-sync | no-SIM-apply | seeds≥3 | asof=READY
# READY_D(價)=2026-08-05；OOS 窗 until=2026-06-30（同 S5-OOS 尺；勿默用未 READY 之 08-06）
# Steward 範圍=h60_core；H20/40/120 本窗不做；Direction 多臂見 V5（不重訓）
# hold #1 watcher；NF-pause keep；≠確立級
```

| 可 | 不可 |
|---|---|
| `run_economic_eval --h 60 --feature-source=prodset --until 2026-06-30 --seed {1,2,42}` | 假 asof=08-06；寫 predict；sim apply |
| 報 #11 min／med／max；#14 vs bench | 單 seed 勝出謊；改 dgate |
| nice 讓位 B3 | 撤 NF；開新族 |

*go → 執行中／EXECUTED。*

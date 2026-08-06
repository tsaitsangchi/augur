---
status: go
series: governance
date: 2026-08-06
choice: T2
paste: "AI-SOURCE-APPROVE-T2-go | FZ/GATE-keep | system-actor-only | max-sources-1 | tie-lift-log"
plan: reports/augur_ai_source_approve_thaw_plan_20260806.md
t0: audits/AI-SOURCE-APPROVE-THAW-T0-ADOPTED-20260806.md
self_reported: true
---

# GO｜AI-SOURCE-APPROVE T2 · AUTO-LIFT 可機械 activate · 2026-08-06

Steward：確認 v1.48 機械可 → 選 **T2-go**。

| 允 | 禁 |
|---|---|
| AUTO-LIFT：`activate_source=True`（`system:kh10_auto_admit`） | web／對話裸 SQL approve |
| 每答批次 **最多 1** 個 `source_key` | 無限批量 activate |
| 沿用 `maybe_activate_source`（需 has_text；標題件不靠此放行源） | 改 HUMAN_ONLY；改 gov 寫路徑 |

T0 敘事仍有效：web／對話 Agent **不可**。

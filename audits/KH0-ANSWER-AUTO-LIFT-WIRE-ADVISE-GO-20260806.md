---
status: go
series: kh_loop_evolve
date: 2026-08-06
paste: "KH0-ANSWER-AUTO-LIFT-wire-advise-go | feature-flag-default-off | FZ/GATE-keep | T2-activate-default"
plan: reports/augur_kh0_answer_auto_lift_plan_20260806.md
t2: audits/AI-SOURCE-APPROVE-T2-EXECUTED-20260806.md
self_reported: true
---

# GO｜KH0-ANSWER-AUTO-LIFT wire advise · 2026-08-06

Steward 選 `wire_advise`。

| 允 | 禁 |
|---|---|
| `advise()` 掛線：`guard.pass` ∧ 有 item 引文 ∧ 非 Mode B ∧ 非 picks | 預設全站開啟（必須 env） |
| feature flag：`AUGUR_KH0_ANSWER_AUTO_LIFT=1`（預設 **off**） | 旗關時寫 lift／activate |
| fail-soft：抬層失敗不炸問答 | 改 guard／放寬幻覺閘 |
| T2：機械 activate 沿用模組預設（每批≤1、has_text） | web／對話裸 approve |

```text
KH0-ANSWER-AUTO-LIFT-wire-advise-go | feature-flag-default-off | FZ/GATE-keep | T2-activate-default
```

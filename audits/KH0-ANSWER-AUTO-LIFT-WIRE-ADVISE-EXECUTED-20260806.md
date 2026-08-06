---
status: executed
series: kh_loop_evolve
date: 2026-08-06
go: audits/KH0-ANSWER-AUTO-LIFT-WIRE-ADVISE-GO-20260806.md
plan: reports/augur_kh0_answer_auto_lift_plan_20260806.md
paste: "KH0-ANSWER-AUTO-LIFT-wire-advise-EXECUTED | feature-flag-default-off | selftest-pass"
self_reported: true
---

# EXECUTED｜KH0-ANSWER-AUTO-LIFT wire advise · 2026-08-06

## 碼

| 檔 | 變更 |
|---|---|
| `src/augur/knowledge/answer_auto_lift.py` | `auto_lift_enabled()`／`AUGUR_KH0_ANSWER_AUTO_LIFT`（預設 off） |
| `src/augur/advisor/advise.py` | `auto_lift=` 參數；`_maybe_wire_auto_lift`：`guard.pass` ∧ item 引文 ∧ 非 Mode B ∧ 非 picks → `maybe_auto_lift_after_answer(apply=True)`；fail-soft |

## 啟用

```bash
export AUGUR_KH0_ANSWER_AUTO_LIFT=1
# 或 advise(..., auto_lift=True)
```

未設環境變數／未傳參 → **不**抬層、回傳無 `auto_lift` 鍵。

## 驗

```text
./venv/bin/python -m augur.knowledge.answer_auto_lift --selftest  # ✓含 flag
./venv/bin/python -m augur.advisor.advise --selftest              # ✓含旗關無鍵
```

T2 activate 行為：旗開時沿用模組預設（每批 ≤1、has_text）；與 `AI-SOURCE-APPROVE-T2-EXECUTED` 一致。

*executed。預設仍關；開啟須 ops／人設 env。*

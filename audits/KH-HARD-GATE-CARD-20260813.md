---
status: gate_card
series: local_ai_kh
track: KH8-DISCRIM
date: 2026-08-13
viewpoint: 2026-08-13T10:15+08:00
paste: "KH-HARD-GATE-card | no-relax-θ | no-fake-depth8 | L3=dual-explicit | AUTO-LIFT=already-resident"
prior_plan: reports/augur_kh8_discrim_plan_first_20260813.md
prior_lift: audits/AUTO-LIFT-RESIDENT-EXECUTED-20260812.md
self_reported: true
layer: "[I]"
---

# GATE｜四項「未做」點名卡 · 2026-08-13

> Steward 引句：放寬 θ、L3 寫庫、depth≥8、新開 AUTO-LIFT。  
> **本檔 ≠ 授權執行**；只標可否。

| 項 | 可否 | 現況／條件 |
|---|---|---|
| **放寬 θ**（`MIN_MINORITY_MASS`↓） | **禁** | 路徑 D；假綠；disc 仍 ok=False 時降門＝謊 |
| **depth≥8** | **禁**（現況） | 母體 ok=False；產線 **stop-at-7**；禁宣稱進化成功 |
| **L3 寫庫**（A2 weight UPDATE） | **高門檻** | 須**雙明示** `KH8-DISCRIM-A2-L3-go`；L2 投影仍 ok=False → L3 **不會** magically 過 θ；可回滾 |
| **新開 AUTO-LIFT** | **已常駐** | `AUTO-LIFT-RESIDENT-EXECUTED`：systemd env=1；碼預設仍 off；**未**授抬 >KH2 |

## 若要真動（須另貼）

```text
# 禁貼（會拒）
KH8-DISCRIM-D-relax-θ | …
KH8-depth8-go | …          # 在 ok=False 下拒

# 可裁（高門檻）
KH8-DISCRIM-A2-L3-go | dual-explicit | no-fake-depth8 | E-keep-until-ok | rollback-SQL-ready

# AUTO-LIFT：已開常駐；若要「抬 >KH2」須另句（現禁）
AUTO-LIFT-beyond-KH2-go | …   # 預設拒；須新尺
```

*gate only。*

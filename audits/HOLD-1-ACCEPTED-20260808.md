---
status: accepted
series: daily_asof
track: HOLD-1
date: 2026-08-08
viewpoint: 2026-08-08T19:40+08:00
paste: "hold-#1 | A→B3@next-tip | horizons-default=20,60 | NF-pause | no-SIM-apply"
prior_tip: "2026-08-07"
next_D: "2026-08-10"
nav: reports/augur_opt_stepwise_best_next_plan_r12_20260807.md
canvas: opt-best-next-r12-refresh.canvas.tsx
self_reported: true
layer: "[I]"
---

# ACCEPTED｜hold-#1 · 依 recommended 往下做

> Steward：`依recommended往下做` → 主軸 **hold-#1**（閒時∥刀不開）。

```text
hold-#1 | A→B3@next-tip | horizons-default=20,60 | NF-pause | no-SIM-apply | no-fake-B3
```

## LIVE 錨（授受時）

| 錨 | 值 |
|---|---|
| 日曆 | **2026-08-08 六**（台股休市） |
| PriceAdj／fv／core／pp max | **2026-08-07** |
| tip＠08-07 | B3 已完；pp **五 H**（站式下一 D 仍預設 **20,60**） |
| serve | RankRidge＠**2026-07-31** |
| 下一目標 D | **2026-08-10**（下一個交易日假設；若休日遞延） |

## 准／禁

| 准 | 禁 |
|---|---|
| 價≥下一 D → 站式 B3 `horizons=20,60` | 假 B3＠週末／無價日 |
| armed watcher 輪詢至截止 | 改 standing 五窗未雙明示 |
| #2／#10 誠實∥輕監 | 默開 NF／promote／sim-apply |

*accept → arm。*

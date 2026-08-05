---
status: monitor
date: 2026-08-05
layer: "[I]"
bundle: "1+2 light∥ + B3 plan"
self_reported: true
---

# MONITOR｜開問題 1∥ ＋ B3 plan · 2026-08-05

> Steward：執行序「1,2」→ 重刀 **`b3_plan`**；輕量並行。

## 1. 文件

| 項 | 路徑 |
|---|---|
| **B3** plan | `reports/augur_daily_asof_b3_orchestrator_plan_20260805.md` |

## 2. #4 C1 探針（pause 下允許）

| 探針 | 結果 |
|---|---|
| `python -m augur.features.sequence --selftest` | **全通過** |
| `migrate_stock_graph_edge_ddl.py --check` | 表在；索引 2/2；型別列數 1831／5089／6101 |
| `stock_graph_edge` LIVE | **n=13,021**；`as_of` 仍僅 **2026-06-30**（與日更 D=08-04 **錯位**＝消費端必 SKIP／另授重建） |

未：`--commit` 新圖、未訓、未撤 NF-pause。

## 3. Ops／Adv／#8／#10

| 錨 | LIVE |
|---|---|
| TAIEX／fv／core／pp(H20,H60) | 皆 max **2026-08-04** |
| core＠D n | **283**（B1 對齊公式後） |
| Adv 2330 H20 | as_of **2026-08-04**；score≈0.5313 |
| Top5 意圖改寫 | `(5,20)`；不短路；`picks_ground_truth` |
| `:8399`／`:8090` | **200** |
| dgate | fail 12／approved 11／superseded 6（無產品綠） |
| #8 | 未跑 `repair_priceadj --repair`（另授） |

**Ops 下交易日**：待 PriceAdj≥新 `D` 後，按 runbook（core 用 **`--incremental --asof-date D`**）；B3 殼未落地前仍手跑。

## 4. 建議下一句

```text
DAILY-ASOF-B3-PLAN-ack
# 或
DAILY-ASOF-B3-SHELL-go | FZ/GATE-keep | skip-sync | no-SIM-apply | no-cron
```

*完。self-reported（#32a）。*

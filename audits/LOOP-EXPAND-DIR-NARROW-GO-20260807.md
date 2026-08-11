---
status: go
series: c1_arc_b_tri_narrow
date: 2026-08-07
prior:
  - audits/SIM-LOOP-CYCLE-2-20260807.md
  - audits/S1-TRI-DIM-SYNC-narrow-GO-20260805.md
  - audits/LOOP-S2-TO-S1-EXPAND-EXECUTED-20260805.md
paste: "LOOP-EXPAND-DIR-narrow-go | FZ/GATE-keep | API-THAW-bounded | no-SIM-apply | tip=2026-08-06 | hold-#1"
self_reported: true
---

# GO｜LOOP-EXPAND-DIR-narrow · 2026-08-07

> **授權**：Steward 貼 `LOOP-EXPAND-DIR-narrow-go`（Cycle-2 建議下一刀）。  
> tip／until＝**2026-08-06**（與 Cycle-2 閘一致；≠假 B3＠08-07）。

```text
LOOP-EXPAND-DIR-narrow-go | FZ/GATE-keep | API-THAW-bounded | no-SIM-apply | tip=2026-08-06 | hold-#1
# dataset=TaiwanStockTotalReturnIndex ONLY
# daily_maintenance --datasets TaiwanStockTotalReturnIndex --with-dim-sync --end 2026-08-06
# then: derive_market_iv --until 2026-08-06
# then: build_market_direction_features --run --since 2025-01-01 --until 2026-08-06
```

**不含**：其他 by-dim-id、全量 `AUGUR_DIM_SYNC`、Dividend、S3 feature build、NF 解凍、sim `--apply`、假關 dgate、搶 live B3＠08-07。

*go。*

---
status: go
series: c1_arc_b_tri_narrow
parent_go: audits/LOOP-S2-TO-S1-EXPAND-GO-20260805.md
---

# GO｜TRI 窄窗 dim-sync（閉合 RG-DIR-PIT-03）· 2026-08-05

> **授權**：Steward AskQuestion `tri_dim` → **`narrow_tri_go`**  
> paste：

```text
S1-TRI-DIM-SYNC-narrow-go | FZ/GATE-keep | API-THAW-bounded | no-SIM-apply
# dataset=TaiwanStockTotalReturnIndex ONLY
# daily_maintenance --datasets TaiwanStockTotalReturnIndex --with-dim-sync --end 2026-08-04
# then: derive_market_iv + build_market_direction_features --until 2026-08-04
```

**不含**：其他 by-dim-id 表、全量 `AUGUR_DIM_SYNC`、Dividend、`--with-dim-sync` 無 datasets 過濾。

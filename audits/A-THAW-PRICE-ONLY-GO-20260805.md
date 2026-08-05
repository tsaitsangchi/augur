---
status: go
series: daily_asof_ops
paste: A-THAW-price-only
date: 2026-08-05
---

# GO｜A 車道 THAW 價量 · price_only · 2026-08-05

> **授權**：Steward `a_sync_now` → `price_only`（只 PriceAdj／價量；禁 Dividend／dim-sync）  
> **執行策略**：20:00 已有 in-flight  
> `daily_maintenance.py --end 2026-08-05`（arena 子行程 pid **1981339**）  
> → **不另開第二支**（避搶額度）；監看至 TAIEX PriceAdj≥08-05 或 maint 結束。

```text
A-THAW-PRICE-ONLY-go | API-THAW-bounded | end=2026-08-05
# datasets intent: TaiwanStockPrice / PriceAdj path via daily_maintenance
# no --with-dim-sync · no Dividend · no second concurrent maint
```

*監看中。*

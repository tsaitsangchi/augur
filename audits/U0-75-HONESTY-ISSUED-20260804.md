# U0-75 honesty 通行證已發放 — binding 75（2026-08-04）

> **位階**：[I] 簽核摘要。  
> **裁示原文**：`REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo`  
> **dry**：`audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-DRY-SQL-20260804.md`  
> **呈請**：`audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-HONESTY-REQUEST-20260804.md`  
> **主殘差**：`audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-20260804.md`

## 裁示（原文）

```
REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo
```

## 意義邊界（寫死）

| 是 | 否 |
|---|---|
| `SET LOCAL augur.honesty_write='on'` 於 **75** 親簽執行窗合法 | 擴及其他 binding（含 81 Adj／derived） |
| `decided_by=hugo` 得寫入 `tw.daily_bar` 版本列 | AI 自造其他人名 |
| `tw.daily_bar.authoritative_binding_id` → **75** `TaiwanStockPrice`（observation） | 改指 **81** `TaiwanStockPriceAdj` |
| 本批 one-shot；COMMIT 後本證**已消費** | 複用他證／擴 Annex F 未採認概念 |

## 不做

- 未解凍／未跑 daily_maintenance／sync／FinMind  
- 未改 binding 81；未 sim `--apply`  

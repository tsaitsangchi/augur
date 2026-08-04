# W2 P0-C binding 86／35／70 EXECUTED — 2026-08-04

> **位階**：[I] 執行留痕。  
> **授權**：`REGISTRY-GO: Q-R1=a + honesty=86,35,70 + decided_by=hugo`  
> **通行證**：`audits/W2-DRAFT8670-HONESTY-PASSPORT-ISSUED-20260804.md`  
> **dry**：`reports/augur_w2_draft8670_dry_sql_propose_20260804.md`

## 執行結果

| binding | concept_key | source_column | decided_at |
|---:|---|---|---|
| **86** | `tw.margin_maintenance_ratio.market` | `TotalExchangeMarginMaintenance` | `2026-08-04 10:16:04.503201+08` |
| **35** | `tw.day_trading.stock` | `Volume,BuyAmount,SellAmount` | 同上 |
| **70** | `tw.market_capitalization.stock` | `market_value` | 同上 |

`decided_by`＝`hugo`；形制 Q-R1=(a)、W2-1=(a)。

## 計數

| 度量 | 前 | 後 |
|---|---|---|
| mapped | **15／98** | **18／98** |
| source_column 已填 | **5／98** | **8／98** |

## ROLLBACK 演練 → COMMIT

各 binding INSERT／version／UPDATE＝**1／1／1**（演練 ROLLBACK 後仍 unmapped → COMMIT OK）。

## 驗收（`--check`）

- ✓ `tw.margin_maintenance_ratio.market` → binding 86  
- ✓ `tw.day_trading.stock` → binding 35  
- ✓ `tw.market_capitalization.stock` → binding 70  

## 不做

- 未解直綁消費端；未擴其他草案；未 commit／push；未放量 API。  

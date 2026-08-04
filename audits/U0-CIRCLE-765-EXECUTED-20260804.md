# U0-CIRCLE binding 7／65 EXECUTED — 2026-08-04

> **位階**：[I] 執行留痕。  
> **授權**：`REGISTRY-GO: Q-R1=a + honesty=7,65 + decided_by=hugo`  
> **通行證**：`audits/U0-765-HONESTY-ISSUED-20260804.md`（本批 COMMIT 後**已消費**）  
> **dry**：`audits/U0-CIRCLE-765-20260804.md`  
> **ask**：`reports/augur_u0_circle_ask_20260804.md`

## 執行結果

| binding | concept_key | category | source_column | decided_at |
|---:|---|---|---|---|
| **7** | `tw.convertible_bond.terms` | `state` | `IssuanceAmount,InitialDateOfConversion,DueDateOfConversion` | `2026-08-04 10:31:35.772361+08` |
| **65** | `tw.option.institutional_flow.after_hours` | `quantity` | `long_deal_amount,long_deal_volume,short_deal_amount,short_deal_volume` | 同上 |

`decided_by`＝`hugo`；形制 Q-R1=(a)、W2-1=(a) 分隔字串。  
表：`TaiwanStockConvertibleBondInfo`／`TaiwanOptionInstitutionalInvestorsAfterHours`。

## 前後計數（live；`superseded_at IS NULL`）

| 度量 | 前 | 後 |
|---|---|---|
| mapped | **18／98** | **20／98** |
| source_column 已填（sc） | **8／98** | **10／98** |

## ROLLBACK 演練 → COMMIT

單一交易涵蓋 7＋65（各 INSERT concept／INSERT version／UPDATE binding）。

| 階段 | 結果 |
|---|---|
| 演練 | 兩鍵皆 mapped／sc 暫 20／10 → **ROLLBACK**；仍 unmapped、concept 不存在、mapped／sc＝18／8 |
| COMMIT | 同上寫入 → **OK** |

## 驗收（`--resolve`／`--check`）

- ✓ `tw.convertible_bond.terms` → `TaiwanStockConvertibleBondInfo.IssuanceAmount,InitialDateOfConversion,DueDateOfConversion`（binding_id=7）
- ✓ `tw.option.institutional_flow.after_hours` → `TaiwanOptionInstitutionalInvestorsAfterHours.long_deal_amount,long_deal_volume,short_deal_amount,short_deal_volume`（binding_id=65）

## honesty 消費

本批通行證僅解鎖 **7／65**；COMMIT 後 one-shot **已消費**，不得複用於其他 binding。

## 不做

- 未登 37／80／97（俟）  
- 未改消費端直綁；未 commit／push；未跑 daily_maintenance／sync／放量 API  

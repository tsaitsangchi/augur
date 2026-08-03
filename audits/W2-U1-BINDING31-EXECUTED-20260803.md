# W2 U1 binding 31 EXECUTED — 2026-08-03

> **位階**：[I] 執行留痕（非 META-CONSTITUTION [N]）。  
> **授權**：Steward 明示親簽執行（`decided_by=hugo`）· honesty 通行證＝`audits/W2-U1-HONESTY-PASSPORT-ISSUED-20260803.md`  
> **依據**：`reports/augur_w2_u1_binding31_dry_sql_propose_20260803.md`  
> **射程**：**僅** `binding_id=31`（TaiwanStockBalanceSheet）；**未**執行 62／93

## 執行時刻

| 項 | 值 |
|---|---|
| `decided_by` | `hugo` |
| `decided_at` | `2026-08-03 19:27:36.779353+08` |
| 形制 | Q-R1＝(a) 原地 UPDATE；W2-1＝(a) `source_column='value'` |
| 概念鍵 | `tw.financial_statement.balance` |

## 前後計數（live binding；`superseded_at IS NULL`）

| 度量 | 前 | 後 |
|---|---|---|
| `mapping_status=mapped` | **10／98** | **11／98** |
| `source_column` 已填 | 0／98（執行前本條 NULL） | **1／98** |

## ROLLBACK 演練（同連線、先於 COMMIT）

| 語句 | rowcount |
|---|---|
| `INSERT world_concept` | 1 |
| `INSERT world_concept_version` | 1 |
| `UPDATE world_channel_binding`（31 ∧ unmapped ∧ live） | **1** |
| `ROLLBACK` | OK |
| 演練後 binding 31 | 仍 `unmapped`（概念亦不存在） |

**判定**：語法／影響列數符合稿預期 → 進入 COMMIT。

## COMMIT

| 語句 | rowcount |
|---|---|
| INSERT／INSERT／UPDATE | 1／1／1 |
| `COMMIT` | OK |

**SQL 指紋（committed 腳本 sha256）**：`d3d7bff7a43ee71238eac74de7b3ba82d9bd7c8edb41cad1031071deb0205868`

## 驗收（唯讀）

| 檢查 | 結果 |
|---|---|
| binding 31 | `mapped` · `concept_key=tw.financial_statement.balance` · `source_column=value` · `source_table=TaiwanStockBalanceSheet` |
| registry current | `decided_by=hugo` · `category=event` · `authoritative_binding_id=31` |
| `reconcile_channel_columns.py --survey` 頭兩行 | `source_column 已填：1/98　｜　mapping_status=mapped：11/98` |
| binding 62 | 仍 `unmapped` · `concept_key` NULL · `source_column` NULL |
| binding 93 | 仍 `unmapped` · `concept_key` NULL · `source_column` NULL |

## 不做

- 未執行 62／93  
- 未 git commit／push  
- 未打 FinMind／FRED；未搶 `heavy_slot`；未碰 evolution  

## Trace

| 產物 | 路徑 |
|---|---|
| dry 稿 | `reports/augur_w2_u1_binding31_dry_sql_propose_20260803.md` |
| 決策卡 | `reports/augur_w2_steward_cut_card_20260803.md` |
| 通行證 | `audits/W2-U1-HONESTY-PASSPORT-ISSUED-20260803.md` |
| 本 audit | `audits/W2-U1-BINDING31-EXECUTED-20260803.md` |

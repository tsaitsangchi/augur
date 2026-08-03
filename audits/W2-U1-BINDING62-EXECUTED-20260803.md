# W2 U1 binding 62 EXECUTED — 2026-08-03

> **位階**：[I] 執行留痕（非 META-CONSTITUTION [N]）。  
> **授權**：Steward 明示親簽執行（`decided_by=hugo`）· honesty 通行證＝`audits/W2-U1-HONESTY-PASSPORT-ISSUED-20260803.md`  
> **依據**：`reports/augur_w2_u1_binding62_dry_sql_propose_20260803.md`  
> **射程**：**僅** `binding_id=62`（TaiwanStockShareholding）；**未**執行 93；31 不變

## 執行時刻

| 項 | 值 |
|---|---|
| `decided_by` | `hugo` |
| `decided_at` | `2026-08-03 21:15:03.575233+08` |
| 形制 | Q-R1＝(a) 原地 UPDATE；W2-1＝(a) 分隔字串（入 6） |
| 概念鍵 | `tw.foreign_ownership.stock` |
| `source_column` | `ForeignInvestmentShares,ForeignInvestmentSharesRatio,ForeignInvestmentRemainingShares,ForeignInvestmentRemainRatio,ForeignInvestmentUpperLimitRatio,ChineseInvestmentUpperLimitRatio` |

## 前後計數（live binding；`superseded_at IS NULL`）

| 度量 | 前 | 後 |
|---|---|---|
| `mapping_status=mapped` | **11／98** | **12／98** |
| `source_column` 已填 | **1／98** | **2／98** |

## ROLLBACK 演練（同連線、先於 COMMIT）

| 語句 | rowcount |
|---|---|
| `INSERT world_concept` | 1 |
| `INSERT world_concept_version` | 1 |
| `UPDATE world_channel_binding`（62 ∧ unmapped ∧ live） | **1** |
| `ROLLBACK` | OK |
| 演練後 binding 62 | 仍 `unmapped`（概念亦不存在） |

**判定**：語法／影響列數符合稿預期 → 進入 COMMIT。

## COMMIT

| 語句 | rowcount |
|---|---|
| INSERT／INSERT／UPDATE | 1／1／1 |
| `COMMIT` | OK |

**SQL 指紋（committed 腳本 sha256）**：`d0c65729d394fa2e97af4c1ecb42e467441cabfb28f2483316e3cfc8398200f7`

## 驗收（唯讀）

| 檢查 | 結果 |
|---|---|
| binding 62 | `mapped` · `concept_key=tw.foreign_ownership.stock` · `source_column`＝六欄分隔字串 · `source_table=TaiwanStockShareholding` |
| registry current | `decided_by=hugo` · `category=state` · `authoritative_binding_id=62` · `ts_semantics=交易日` |
| `reconcile_channel_columns.py --survey` 頭兩行 | `source_column 已填：2/98　｜　mapping_status=mapped：12/98` |
| `world_concept --check` | `✓ tw.foreign_ownership.stock → TaiwanStockShareholding.…（binding_id=62）` |
| binding 31 | 仍 `mapped` · `tw.financial_statement.balance` · `source_column=value`（不變） |
| binding 93 | 仍 `unmapped` · `concept_key` NULL · `source_column` NULL |

## 不做

- 未執行 93  
- 未 git commit／push  
- 未打 FinMind／FRED；未搶 `heavy_slot`；未碰 evolution  

## Trace

| 產物 | 路徑 |
|---|---|
| dry 稿 | `reports/augur_w2_u1_binding62_dry_sql_propose_20260803.md` |
| 決策卡 | `reports/augur_w2_steward_cut_card_20260803.md` |
| 通行證 | `audits/W2-U1-HONESTY-PASSPORT-ISSUED-20260803.md` |
| 本 audit | `audits/W2-U1-BINDING62-EXECUTED-20260803.md` |

# UNBIND-39 EXECUTED — field_correlation block_money（2026-08-04）

> **位階**：[I] 執行留痕。  
> **授權**：`UNBIND-39-code-go`（Steward 同回合與 OUT8／N7／043／A1A2 並書）  
> **計畫**：`reports/augur_w2_unbind_block_trade_plan_20260804.md`  
> **Registry**：`tw.block_trade.print`／binding 39（已 COMMIT）

## 改動

| 檔 | 內容 |
|---|---|
| `src/augur/audit/field_correlation.py` | `_SRC["block_money"]=None`；`block_money_sql`／`block_money_sql_from_table` 經 `resolve('tw.block_trade.print')`；`build_stock_panel` 組 SQL；`--selftest` 增 UNBIND 斷言 |

## 驗收

| 檢查 | 結果 |
|---|---|
| `--selftest` | 全通過 ✓（含 _SRC 無 vendor 字面、helper 表互換會紅） |
| 影子比對 stock=`2330` | old vendor SQL ≡ resolve SQL；**n=3336** 列相等 |
| `_SRC` 消費點 | 無 `TaiwanStockBlockTrade` 字面（僅自測 fixture 字串） |

## 不做

- 未重算／手補 `field_correlation` 歷史列（#12）  
- 未解綁其他 `_SRC` vendor 表  
- 未 git commit（須另授）  

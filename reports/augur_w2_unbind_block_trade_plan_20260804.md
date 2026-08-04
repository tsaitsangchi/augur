# 解直綁計畫｜binding 39 `tw.block_trade.print`（W1-R1 · 2026-08-04）

> **位階**：[I] 改碼計畫（#20）。**授權**：`OPT-STEP-R3`＋`W1-go`（含 `UNBIND-39-plan` 預設）。  
> **硬禁**：**本檔不改 production code**；改碼須另句 `UNBIND-39-code-go`。  
> **上游**：Registry COMMIT＝`audits/W2-CIRCLE-BINDING39-EXECUTED-20260804.md`；消費點＝`src/augur/audit/field_correlation.py:75`。

---

## 1. 現況（親查）

| 層 | 狀態 |
|---|---|
| Registry | `tw.block_trade.print` mapped；權威 binding **39**；`source_column=trading_money,price,volume`；`--check` ✓ |
| 消費 | `_SRC` 仍字面：`FROM "TaiwanStockBlockTrade" … sum(trading_money)` |
| API | `resolve`／`resolve_sql` 只回**表**；多欄 `source_column` 逗號串——消費者須自選主欄 |

## 2. 目標行為

| 前 | 後 |
|---|---|
| SQL 字面表名直綁 | 經 `resolve('tw.block_trade.print')` 取表；主量欄＝`trading_money`（與現 sum 一致） |
| vendor 表名散落 | 概念鍵為唯一入口；表改名時只動 Registry |

**建議實作形（呈裁；未寫碼）**：

```python
from augur.catalog.world_concept import resolve, quote_ident
b = resolve("tw.block_trade.print")
# b.source_table / 主欄：prefer 'trading_money' in split(b.source_column or '')
sql = f'SELECT date, sum(trading_money)::float8 FROM {quote_ident(b.source_table)} WHERE stock_id=%s GROUP BY date'
```

或薄 helper：`resolve_fact_column(concept_key, preferred='trading_money')`——**若新增 helper＝另檔＋#29 矩陣＋#35 先驗紅**，本計畫預設**最小改**：只改 `_SRC` 一列組法。

## 3. 影子比對（改碼後必跑）

1. 固定 `stock_id` 樣（≥3 檔）＋日期窗：舊 SQL vs 新 SQL 之 `block_money` 序列 **逐日相等**（允許兩邊皆空）。  
2. 衍生 `block_share` 同窗相等。  
3. `world_concept --selftest` 仍綠；`check_cmd_matrix` 若動 script 入口。  
4. **禁**為對齊而改歷史 `field_correlation` 落庫列（#12）。

## 4. 風險

| 風險 | 緩解 |
|---|---|
| `source_column` 多欄解析歧義 | 釘死主欄 `trading_money`；price/volume 不進此 sum |
| `resolve` 快取陳舊 | 改碼路徑 `clear_cache` 或短連線 |
| 行為「零變更」教條 | 本改＝糾正直綁；影子必須綠才 COMMIT git |

## 5. 驗收（code-go 後）

- [ ] `rg 'TaiwanStockBlockTrade' src/augur/audit/field_correlation.py` → **0**（該消費點）  
- [ ] 影子三檔相等  
- [ ] audit：`audits/W2-UNBIND-39-EXECUTED-YYYYMMDD.md`  

## 6. Steward 下一句

- `UNBIND-39-code-go` → 准改碼＋測＋（可另授）commit  
- 或 `UNBIND-39-plan-ack` → 只凍結本計畫  

*零改碼。*

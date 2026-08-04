# UNBIND-35／70 EXECUTED — field_correlation（2026-08-04）

> **授權**：`UNBIND-3570-code-go`  
> **計畫**：`reports/augur_w2_unbind_3570_plan_20260804.md`  
> **射程**：僅 `field_correlation`（不含 direction／valuation 第二刀）

## 改動

`src/augur/audit/field_correlation.py`：
- `day_trade_*`／`market_value` → lazy resolve（`tw.day_trading.stock`／`tw.market_capitalization.stock`）
- 共用 `scalar_fact_sql_from_table`／`resolved_scalar_sql`／`_RESOLVED_SRC`

## 驗收

| 檢查 | 結果 |
|---|---|
| `--selftest` | 全通過 ✓ |
| 影子 2330 | volume／buy／sell **n=3071** 相等；market_value **n=5505** 相等 |
| `_SRC` | 無 DayTrading／MarketValue／BlockTrade 字面 |

## 不做

- 未改 `build_daily_direction_features.py`／`valuation.py`  
- 未 git commit  

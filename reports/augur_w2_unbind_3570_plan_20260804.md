# 解直綁計畫｜binding **35**＋**70**（UNBIND-3570-plan · 2026-08-04）

> **位階**：[I] 改碼計畫。**授權**：`UNBIND-3570-plan-go`（甲／W2prep）。  
> **硬禁**：**本檔不改 production code**；改碼須另句  
> `UNBIND-35-code-go`／`UNBIND-70-code-go`（或合併 `UNBIND-3570-code-go`）。  
> **Registry**：35＝`tw.day_trading.stock`；70＝`tw.market_capitalization.stock`（`audits/W2-DRAFT8670-EXECUTED-20260804.md`）。  
> **形制先例**：`audits/W2-UNBIND-39-EXECUTED-20260804.md`（`Binding.table`／`.column`）。

---

## 0. 共同設計（對齊 39）

| 項 | 值 |
|---|---|
| resolve | `resolve(concept_key)` → `Binding.table`／`.column`（逗號分隔取主欄） |
| `_SRC` | 該欄改 `None`＋lazy `*_sql(conn)`；禁 vendor 字面留在 list |
| 自測 | #35：_SRC 無表名；helper 換表 SQL 變；零 IO |
| 影子 | 固定 stock（建議 2330）舊 SQL≡新 SQL |
| 禁 | 手補歷史相關列（#12） |

---

## 1. Binding **35**｜`tw.day_trading.stock`

### 1.1 消費點（親查）

| 檔 | 現況 |
|---|---|
| `src/augur/audit/field_correlation.py` | `day_trade_volume`／`buy`／`sell` ← `"TaiwanStockDayTrading"` Volume／BuyAmount／SellAmount |
| `scripts/build_daily_direction_features.py:136` | 直綁 DayTrading（方向特徵） |
| `scripts/verify_daytrade_candidates.py`／`run_deep_interaction_scan.py` | 研究／掃描直綁 |

**本計畫預設第一刀射程**＝**僅** `field_correlation` 三欄（與 39 同檔、同形）。  
方向特徵／掃描＝**第二刀**（另授或同句明示 `+dirfeat`）。

### 1.2 目標

| 概念欄 | preferred 主欄 | 組 SQL |
|---|---|---|
| volume | `Volume` | `SELECT date, "Volume"::float8 FROM {table} WHERE stock_id=%s` |
| buy | `BuyAmount` | 同上換欄 |
| sell | `SellAmount` | 同上換欄 |

`source_column` Registry＝`Volume,BuyAmount,SellAmount`；`BuyAfterSale` 不入。

### 1.3 驗收（code-go 後）

- [ ] `_SRC` 三列無 `TaiwanStockDayTrading`  
- [ ] `--selftest` 綠＋影子 2330 三序列相等  
- [ ] audit `W2-UNBIND-35-EXECUTED-*.md`

---

## 2. Binding **70**｜`tw.market_capitalization.stock`

### 2.1 消費點

| 檔 | 現況 |
|---|---|
| `field_correlation.py` | `market_value` ← `"TaiwanStockMarketValue".market_value` |
| `src/augur/features/valuation.py:33` | 直綁 MarketValue（**生產特徵鏈**——改碼風險高於 audit） |

**本計畫預設第一刀**＝**僅** `field_correlation`。  
`valuation.py`＝**第二刀**（須影子特徵值＋明示 `UNBIND-70-valuation-go`）。

### 2.2 目標

```text
resolve('tw.market_capitalization.stock') → table；主欄 market_value
SELECT date, market_value::float8 FROM {quote_ident(table)} WHERE stock_id=%s
```

### 2.3 驗收（code-go 後）

- [ ] `_SRC` 無 MarketValue 字面  
- [ ] 影子相等；`--selftest` 綠  
- [ ] audit `W2-UNBIND-70-EXECUTED-*.md`

---

## 3. Steward 下一句

```text
UNBIND-3570-code-go              # 只 field_correlation 35三欄＋70
UNBIND-3570-code-go +dirfeat     # 加 build_daily_direction_features DayTrading
UNBIND-70-valuation-go           # 另開 valuation.py
UNBIND-3570-plan-ack             # 只凍結本計畫
```

*零改碼。*

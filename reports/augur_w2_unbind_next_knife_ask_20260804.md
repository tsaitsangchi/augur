# Circle-ask｜UNBIND-3570 下一刀（2026-08-04）

> **位階**：[I] Steward 圈問（#16）。  
> **上游**：計畫 `reports/augur_w2_unbind_3570_plan_20260804.md`；第一刀已執行 `audits/W2-UNBIND-3570-EXECUTED-20260804.md`（僅 `field_correlation`）。  
> **Registry**：35／70 已 COMMIT（`audits/W2-DRAFT8670-EXECUTED-20260804.md`）；本 ask **不**寫 Registry。  
> **進度**：`UNBIND-35-dirfeat`／`UNBIND-70-valuation`／`UNBIND-35-research` 皆 DONE（見下）。

---

## 0. 已完成

| 概念 | binding | 檔 | 狀態 |
|---|---|---|---|
| `tw.day_trading.stock` | 35 | `field_correlation` → `day_trade_*` lazy resolve | ✓ EXECUTED |
| `tw.market_capitalization.stock` | 70 | `field_correlation` → `market_value` lazy resolve | ✓ EXECUTED |
| `tw.day_trading.stock` | 35 | `build_daily_direction_features` → `daytrade_amt`／`d_daytrade_ratio` | ✓ **DONE** → `audits/W2-UNBIND-35-DIRFEAT-EXECUTED-20260804.md` |
| `tw.market_capitalization.stock` | 70 | `valuation` → `market_cap_log`（as-of） | ✓ **DONE** → `audits/W2-UNBIND-70-VALUATION-EXECUTED-20260804.md` |
| `tw.day_trading.stock` | 35 | `verify_daytrade_candidates`／`run_deep_interaction_scan` | ✓ **DONE** → `audits/W2-UNBIND-35-RESEARCH-EXECUTED-20260804.md` |

`field_correlation`／dirfeat／research 自測內之 `TaiwanStockDayTrading` 字面＝helper／換表紅證 fixture，**非**生產直綁殘留。

---

## 1. 殘留消費點（親 grep · `*.py`）

| # | 檔:行 | 字面 | 角色 |
|---:|---|---|---|
| A | ~~`scripts/build_daily_direction_features.py`~~ | ~~DayTrading~~ | ✓ **DONE**（`audits/W2-UNBIND-35-DIRFEAT-EXECUTED-20260804.md`） |
| B | ~~`src/augur/features/valuation.py`~~ | ~~MarketValue~~ | ✓ **DONE**（`audits/W2-UNBIND-70-VALUATION-EXECUTED-20260804.md`） |
| C | ~~`scripts/verify_daytrade_candidates.py`~~ | ~~DayTrading JOIN Price~~ | ✓ **DONE**（`audits/W2-UNBIND-35-RESEARCH-EXECUTED-20260804.md`） |
| D | ~~`scripts/run_deep_interaction_scan.py`~~ | ~~DayTrading Volume~~ | ✓ **DONE**（同上） |
| E | `scripts/build_field_lens_map.py:68,89` | 別名詞 `MarketValue`／`DayTrading` | 透鏡標籤（非 SQL 繫事實；可後標） |

**resolve 缺口（殘）**：C–D 已解綁；E 非 SQL 直綁、後標。

---

## 2. 刀表（請 Steward 擇句）

| knife id | files | risk | proposed go phrase | 狀態 |
|---|---|---|---|---|
| **UNBIND-35-dirfeat** | `scripts/build_daily_direction_features.py`（`_chip_series` DayTrading 段） | **中** | `UNBIND-35-dirfeat-go` | ✓ **DONE** → `audits/W2-UNBIND-35-DIRFEAT-EXECUTED-20260804.md` |
| **UNBIND-70-valuation** | `src/augur/features/valuation.py`（`_MV_SQL`＋FakeCur 表名分支） | **高**：生產估值鏈；須影子 `market_cap_log`＋`--selftest` 綠 | `UNBIND-70-valuation-go` | ✓ **DONE** → `audits/W2-UNBIND-70-VALUATION-EXECUTED-20260804.md` |
| **UNBIND-35-research** | `verify_daytrade_candidates.py`＋`run_deep_interaction_scan.py` | **低**：研究腳本；WM 日落相關但非熱路徑 | `UNBIND-35-research-go` | ✓ **DONE** → `audits/W2-UNBIND-35-RESEARCH-EXECUTED-20260804.md` |
| **UNBIND-3570-second-all** | 原 A＋B（可選＋C／D） | **高**（合併爆炸半徑） | `UNBIND-3570-second-all-go` | A／B／C／D 已分刀 DONE；本合併刀無需再啟 |

`build_field_lens_map`（E）建議 **不入本波**（非 vendor SQL 直綁）。

---

## 3. 建議預設順序（最安全優先）

1. ~~**`UNBIND-35-dirfeat-go`**~~ — ✓ DONE。  
2. ~~**`UNBIND-70-valuation-go`**~~ — ✓ DONE（`audits/W2-UNBIND-70-VALUATION-EXECUTED-20260804.md`）。  
3. ~~**`UNBIND-35-research-go`**~~ — ✓ DONE。

---

## 4. 明示

- **無上表待 go 刀之句 → 不改其餘 code。**  
- 本檔 ≠ Registry 寫入；≠ FinMind／FRED。  
- 形制仍對齊計畫 §0：`Binding.table`／主欄、SQL 禁 vendor 字面、`--selftest`＋影子固定股。

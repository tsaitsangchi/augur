# UNBIND-70-valuation EXECUTED — valuation.py（2026-08-04）

> **位階**：[I] 執行留痕。  
> **授權**：`UNBIND-70-valuation-go`  
> **上游 ask**：`reports/augur_w2_unbind_next_knife_ask_20260804.md`  
> **計畫**：`reports/augur_w2_unbind_3570_plan_20260804.md`  
> **形制先例**：`audits/W2-UNBIND-3570-EXECUTED-20260804.md`／`audits/W2-UNBIND-35-DIRFEAT-EXECUTED-20260804.md`／`audits/W2-UNBIND-39-EXECUTED-20260804.md`  
> **Registry**：`tw.market_capitalization.stock`／binding 70（已 COMMIT；本刀**不**寫 Registry）

## 改動

| 檔 | 內容 |
|---|---|
| `src/augur/features/valuation.py` | `_MV_SQL`（`"TaiwanStockMarketValue"`／`market_value` 直綁）→ `market_value_asof_sql(conn)`＝`resolve('tw.market_capitalization.stock')`＋`Binding.table`／preferred 欄；純函式 `market_value_asof_sql_from_table`；`compute_valuation_features` 預設 resolve（可選 `market_value_sql=` 供自測）；`--selftest` 擴 helper 換表／換欄 #35 |

口徑不變：as-of `date <= panel_date` 最近一筆 `market_value` → `log` → `market_cap_log`（≤0／缺 → 缺列 #1）。

多欄硬停：resolve 之 `source_column` 非空、不含 `market_value`、且欄數＞1 → `RuntimeError`（不發明 join）。

## 驗收

| 檢查 | 結果 |
|---|---|
| `--selftest` | ✓（10 項；含 helper 引號表欄、換表／換欄會紅） |
| #35 驗紅（突變 helper 固定表名） | `helper table swap` 紅、exit 1 ✓（突變後還原） |
| 影子 stock=`2330` | resolve → binding_id=70、`TaiwanStockMarketValue`、`market_value`；raw as-of **n=5505** 舊≡新（max_abs=0）；`market_cap_log` **n=5505** 舊≡新（max_abs=0） |

## 不做

- 未改 PER／10Year／Price 直綁（本刀僅 MarketValue）  
- 未改研究腳本（須另授 `UNBIND-35-research-go`）  
- 未動 `field_correlation`／dirfeat（先前刀已 EXECUTED）  
- 未 Registry 寫入；未 FinMind／FRED；未 git commit  

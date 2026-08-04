# UNBIND-35-dirfeat EXECUTED — build_daily_direction_features（2026-08-04）

> **位階**：[I] 執行留痕。  
> **授權**：Steward「開工」＝採 circle-ask 建議預設 `UNBIND-35-dirfeat-go`（僅本刀；非 valuation／research）。  
> **上游 ask**：`reports/augur_w2_unbind_next_knife_ask_20260804.md`  
> **計畫**：`reports/augur_w2_unbind_3570_plan_20260804.md`  
> **形制先例**：`audits/W2-UNBIND-3570-EXECUTED-20260804.md`／`audits/W2-UNBIND-39-EXECUTED-20260804.md`  
> **Registry**：`tw.day_trading.stock`／binding 35（已 COMMIT；本刀**不**寫 Registry）

## 改動

| 檔 | 內容 |
|---|---|
| `scripts/build_daily_direction_features.py` | `_chip_series` 之 `daytrade_amt`：`"TaiwanStockDayTrading"`／BuyAmount／SellAmount 直綁 → `daytrade_amt_sql(conn)`＝`resolve('tw.day_trading.stock')`＋`Binding.table`／preferred 欄；純函式 `daytrade_amt_sql_from_table`；新增 `--selftest` |

口徑不變：`(BuyAmount + SellAmount) / 2.0` → 後續／成交額＝`d_daytrade_ratio`（lag-1）。

## 驗收

| 檢查 | 結果 |
|---|---|
| import smoke（venv） | ✓ |
| `--selftest` | ✓（helper 引號表欄、換表／換欄會紅） |
| #35 驗紅（突變固定表名） | `helper table swap` 紅、exit 1 ✓ |
| 影子 stock=`2330` | resolve → binding_id=35、`TaiwanStockDayTrading`、`Volume,BuyAmount,SellAmount`；`daytrade_amt` **n=2780** 舊≡新（max_abs=0）；`d_daytrade_ratio` 路徑 **n=2768** 舊≡新（max_abs=0） |

## 不做

- 未改 `valuation.py`（須另授 `UNBIND-70-valuation-go`）  
- 未改研究腳本（須另授 `UNBIND-35-research-go`）  
- 未動 `field_correlation`（第一刀已 EXECUTED）  
- 未 Registry 寫入；未 FinMind／FRED；未 git commit  

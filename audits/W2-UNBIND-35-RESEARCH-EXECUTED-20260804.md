# UNBIND-35-research EXECUTED — 研究腳本 DayTrading 解綁（2026-08-04）

> **位階**：[I] 執行留痕。  
> **授權**：`UNBIND-35-research-go`  
> **上游 ask**：`reports/augur_w2_unbind_next_knife_ask_20260804.md`  
> **計畫**：`reports/augur_w2_unbind_3570_plan_20260804.md`  
> **形制先例**：`audits/W2-UNBIND-35-DIRFEAT-EXECUTED-20260804.md`／`audits/W2-UNBIND-3570-EXECUTED-20260804.md`  
> **Registry**：`tw.day_trading.stock`／binding 35（已 COMMIT；本刀**不**寫 Registry）

## 改動

| 檔 | 內容 |
|---|---|
| `scripts/verify_daytrade_candidates.py` | DayTrading JOIN Price 直綁 → `daytrade_candidate_sql(conn)`＝`resolve('tw.day_trading.stock')`＋`Binding.table`／Volume·BuyAmount·SellAmount；純函式 `daytrade_candidate_sql_from_table`；新增 `--selftest`。Price 側 JOIN 仍直綁（非 binding 35） |
| `scripts/run_deep_interaction_scan.py` | `daytrade_r` 上游 Volume 橫截面直綁 → `daytrade_volume_cross_sql(conn)`；純函式 `daytrade_volume_cross_sql_from_table`；新增 `--selftest` |

口徑不變：verify＝Volume/Trading_Volume 比＋(Buy−Sell)/(Buy+Sell)；scan＝Volume/Trading_Volume。

## 驗收

| 檢查 | 結果 |
|---|---|
| `--selftest`（兩支） | ✓ |
| #35 驗紅（突變 helper 回傳 BrokenTable） | verify／scan selftest 皆 exit 1 ✓ |
| 影子 stock=`2330` | resolve → binding_id=35、`TaiwanStockDayTrading`、`Volume,BuyAmount,SellAmount`；verify JOIN 列 **n=3058** 舊≡新；scan 橫截面 **2026-08-03 n=1** 舊≡新 |
| 全 scan IC 聚合影子 | **N/A**（panel 掃描產物；僅比對事實 SQL） |

## 未動／殘留（有意）

| 檔／處 | 理由 |
|---|---|
| `scripts/build_field_lens_map.py`（別名 `DayTrading`） | 透鏡標籤／後標，非 SQL 直綁（ask E；本刀不入） |
| `build_fund_lens_matrix.py` | **不存在**於 repo；無 SQL 繫綁可改 |
| `field_correlation`／dirfeat 自測字面 | 既有 helper／換表紅證 fixture，非生產直綁 |
| `src/augur/catalog/__init__.py`（BorrowingFeeRate 分類） | 非 DayTrading 消費；非本刀 |
| Registry／git／FinMind／FRED／valuation | 授權外 |

## 不做

- 未 Registry 寫入；未 FinMind／FRED；未 git commit  
- 未改 `TaiwanStockPrice`／PER／MarketValue 直綁  

---
status: executed
series: wm36_vendor_registry
depends_on:
  - audits/WM36-PRICEADJ-INVENTORY-20260805.md
  - audits/WM36-PRICEADJ-P2-EXECUTED-20260805.md
---

# EXECUTED｜WM.36 PriceAdj **P3**（特徵／掃描）· 2026-08-05

> **授權**：Steward AskQuestion `#5+#6` → `go_both`  
> ＝`WM36-PriceAdj-P3-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> **概念**：`tw.daily_bar_adjusted` → `resolve_sql`／binding 100。  
> **self-reported（#32a）**。

## 1. 改動檔

| 檔 | 處 |
|---|---|
| `src/augur/features/panel.py` | `_price_sql(conn)` |
| `src/augur/audit/field_correlation.py` | `_price_sql(conn)`（僅價量表；他表直綁未動） |
| `scripts/build_interaction_candidates.py` | `_load_field` 價欄 |
| `scripts/benchmark_tsfm_taiwan.py` | `load_logret` |
| `scripts/run_cross_table_interaction_scan.py` | `_adj_close_asof` |
| `scripts/run_deep_interaction_scan.py` | 動能窗 close |
| `scripts/run_raw_interaction_ic.py` | adj close 批次 |

## 2. 明示豁免／未做

- `scripts/repair_priceadj_basis.py`（×2）— 維運語意即修 PriceAdj，**本輪豁免**  
- `ops/vendor_binding_baseline.txt` 未收斂  
- 未重跑全量特徵 build／交互掃描 CPU

## 3. 驗收

- [x] 上表 7 檔 `TaiwanStockPriceAdj[quoted_table]`＝**0**；scan 殘留僅 `repair_priceadj_basis`  
- [x] `py_compile`×7 OK  
- [x] selftest：`panel`／`field_correlation`／`build_interaction_candidates`／`benchmark_tsfm_taiwan` 全通過  

## 4. 下一手

- baseline 收斂另句；P3 豁免檔是否 registry 化另裁  

*完。*

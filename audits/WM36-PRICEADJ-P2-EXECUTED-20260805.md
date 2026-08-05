---
status: executed
series: wm36_vendor_registry
depends_on:
  - audits/WM36-PRICEADJ-INVENTORY-20260805.md
  - audits/WM36-PRICEADJ-P1-EXECUTED-20260805.md
---

# EXECUTED｜WM.36 PriceAdj **P2**（arena／sim／MC）· 2026-08-05

> **授權**：Steward AskQuestion `wm36_p2` → `go_execute`  
> ＝`WM36-PriceAdj-P2-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> **概念**：`tw.daily_bar_adjusted` → `resolve_sql`／binding 100。  
> **硬邊界**：本輪**不** `--apply` sim／arena settle 寫庫、不重訓、不 rebuild panel、不改 baseline。  
> **範圍**：嚴格 inventory P2 清單（arena／sim／MC＋`arena/adapters`）；**不含** P3 特徵／掃描、**不含** TRI 表接線。  
> **self-reported（#32a）**。

## 1. 改動檔（P2 清單）

| 檔 | 直綁→registry |
|---|---|
| `scripts/run_arena_daily_pipeline.py` | `_db_asof` max(date)×1 |
| `scripts/run_arena_round.py` | max(date)＋序列 load×2 |
| `scripts/run_arena_replay.py` | 序列 load×1（TRI 仍直綁＝本輪外） |
| `scripts/settle_arena_labels.py` | TAIEX 日曆×2（`_classify`／scoreboard gap） |
| `scripts/settle_sim_outcomes.py` | TAIEX 日曆×1 |
| `scripts/evaluate_sim_calibration.py` | σ floor SQL 工廠＋anchor 日曆×2 |
| `scripts/run_sim_calibration_cell.py` | `_load_calendar`×1 |
| `scripts/simulate_mc_paths.py` | `_hist_logrets`×1 |
| `scripts/simulate_portfolio_risk.py` | `_member_closes`＋兩處 date 窗×3 |
| `src/augur/arena/adapters.py` | threelens live 臂價序列×1 |

口径：SQL `FROM` 不再直寫 `"TaiwanStockPriceAdj"`；docstring／人讀訊息可仍述 vendor 表名（vendor gate 只掃 `FROM "…"`）。  
`settle_*` 內 `_prices(cur, "TaiwanStockPriceAdj", …)` 參數字串**本輪不動**（閘不掃參數；inventory_only）。

## 2. 未做（明示）

- P3（`panel.py`／interaction 掃描／`benchmark_tsfm` 等）
- `TaiwanStockTotalReturnIndex` 直綁（arena round／replay）
- `ops/vendor_binding_baseline.txt` 收斂
- sim／arena `--apply`／`--run` 寫庫重跑

## 3. 驗收（本輪）

- [x] `check_vendor_binding --scan`：上表 10 檔對 `TaiwanStockPriceAdj[quoted_table]`＝**0**（2026-08-05）
- [x] 十檔 `py_compile` OK
- [x] `resolve_sql('tw.daily_bar_adjusted')` → `"TaiwanStockPriceAdj"`；`2330` 最新 close 可讀
- [x] 無參數唯讀煙測：`settle_arena_labels`／`settle_sim_outcomes`／`evaluate_sim_calibration`／`run_sim_calibration_cell`／`simulate_mc_paths`／`run_arena_daily_pipeline` 皆印現況
- [x] 零 DB selftest：`settle_arena_labels`／`evaluate_sim_calibration`／`run_sim_calibration_cell`／`python -m augur.arena.adapters --selftest` 全通過

## 4. 下一手（非本檔授權）

- P3 特徵／掃描接線另 `WM36-PriceAdj-P3-go`
- TRI／其他 vendor 表另帳
- 基線收斂另句（`--write-baseline` 過目後）

*完。*

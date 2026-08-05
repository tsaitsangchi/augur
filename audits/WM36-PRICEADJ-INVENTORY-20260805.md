---
status: inventory
series: wm36_vendor_registry
depends_on:
  - audits/WM36-CLASSICAL-TS-REGISTRY-EXECUTED-20260805.md
---

# WM.36 `TaiwanStockPriceAdj` 直綁盤點（波次 A · 不動碼；2026-08-05）

> **授權**：`wave_a` 項 9＝只盤點。  
> **口徑**：`scripts/check_vendor_binding.py` scan（quoted_table／esc）。  
> **目標概念**：已有 `tw.daily_bar_adjusted`（binding 100）——接線模式＝`resolve_sql`／`quote_ident`。  
> **self-reported（#32a）**。

## 彙總

| 項 | 值 |
|---|---|
| 含 `TaiwanStockPriceAdj` 之掃描列 | **24** 檔（部分同行另有他表） |
| 本輪已清（classical TS） | `probe_classical_ts_phase0b.py`／`train_classical_ts.py`（零 PriceAdj 字面） |
| 基線 | `ops/vendor_binding_baseline.txt`——**本盤點不改基線** |

## 候選批次（建議優先序；執行須另 GO）

### P1 — 方向／機率熱路徑（少檔、高觸頻）

| 檔 | ×處（掃描提示） |
|---|---|
| `scripts/train_direction_stack.py` | ×1 |
| `scripts/train_direction_threelens.py` | ×1 |
| `scripts/produce_direction_probability.py` | ×2 |
| `scripts/build_direction_stack_monthly.py` | ×1（另有其他 vendor） |
| `scripts/train_daily_direction.py` | ×1 |
| `scripts/build_daily_direction_features.py` | ×2 |

### P2 — arena／sim／MC

| 檔 | ×處 |
|---|---|
| `scripts/run_arena_*.py`／`settle_arena_labels.py` | 各 1–2 |
| `scripts/settle_sim_outcomes.py`／`evaluate_sim_calibration.py`／`run_sim_calibration_cell.py` | 1–2 |
| `scripts/simulate_mc_paths.py`／`simulate_portfolio_risk.py` | 1／3 |
| `src/augur/arena/adapters.py` | ×1 |

### P3 — 特徵／掃描／審計（量大、可分批）

| 檔 | 註 |
|---|---|
| `src/augur/features/panel.py` | ×1 |
| `src/augur/audit/field_correlation.py` | ×1（同檔大量他表） |
| `scripts/build_interaction_candidates.py`／`run_*_interaction*.py` | 各 1 |
| `scripts/benchmark_tsfm_taiwan.py` | ×1 |
| `scripts/repair_priceadj_basis.py` | ×2（維運腳；語意即修 PriceAdj——**可能應豁免或仍走 registry**） |

## 不做（本檔）

- 不改任何業務碼  
- 不 `--write-baseline`  
- 不重跑 Phase 0b／方向棧  

## 下一手候選 GO 句（擇一）

`WM36-PriceAdj-P1-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
＝僅上表 P1 六檔改 `tw.daily_bar_adjusted`＋行為不變性抽樣。

*inventory only。*

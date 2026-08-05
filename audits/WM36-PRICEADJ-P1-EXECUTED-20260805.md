---
status: executed
series: wm36_vendor_registry
depends_on:
  - audits/WM36-PRICEADJ-INVENTORY-20260805.md
  - audits/WM36-CLASSICAL-TS-REGISTRY-EXECUTED-20260805.md
---

# EXECUTED｜WM.36 PriceAdj **P1**（方向六檔）· 2026-08-05

> **授權**：Steward `docs_first`（含項 9＝P1 接線）。  
> **概念**：`tw.daily_bar_adjusted` → `resolve_sql`／binding 100。  
> **硬邊界**：FZ／GATE-keep／skip-sync／no-SIM-apply；本輪**不重訓、不 rebuild panel**。  
> **self-reported（#32a）**。

## 1. 改動檔（P1 清單）

| 檔 | 處數→registry |
|---|---|
| `scripts/train_direction_stack.py` | ×1（`run_v2` 日價） |
| `scripts/train_direction_threelens.py` | ×1（`load`） |
| `scripts/produce_direction_probability.py` | ×2（`_vol_sql` 主表＋max 子查） |
| `scripts/build_direction_stack_monthly.py` | ×1 |
| `scripts/train_daily_direction.py` | ×1（`_labels`） |
| `scripts/build_daily_direction_features.py` | ×2（價量＋籌碼成交額） |

口径：SQL `FROM` 不再直寫 `"TaiwanStockPriceAdj"`；docstring 口述仍可出現表名（vendor gate 只掃 quoted FROM）。

## 2. 未做（明示）

- P2／P3（arena／sim／其他）未動
- `ops/vendor_binding_baseline.txt` **未收斂**（須 gate 現查後另句）
- 未跑 `--run` 全量 rebuild／train

## 3. 驗收（本輪）

- [x] `check_vendor_binding`：P1 六檔 **無** `TaiwanStockPriceAdj[quoted_table]`（2026-08-05 煙測；其餘檔之 PriceAdj 仍屬 P2／P3）
- [x] 無參數唯讀煙測（venv）：`produce_direction_probability`／`train_direction_stack`／`train_daily_direction`／`build_direction_stack_monthly`／`build_daily_direction_features` 皆印現況＋指令矩陣
- [x] `resolve_sql('tw.daily_bar_adjusted')` → `"TaiwanStockPriceAdj"`；`2330` 最新 close 可讀
- [x] 六檔 `compile()` 語法 OK；`train_direction_threelens --help` 可用（本輪未跑全量冒煙訓練）

## 4. 下一手（非本檔授權）

- P2 arena／sim 接線另 `WM36-PriceAdj-P2-go`
- 基線收斂另句

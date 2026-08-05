---
status: executed
series: wm36_vendor_registry
depends_on:
  - audits/WM36-GAP-OPTION-A-EXECUTED-20260804.md
  - audits/ARCHIVE-CHECKPOINT-20260805-DIRFAMILY-P6-S4B-ALOG-BETA2.md
---

# WM.36 classical TS 改走 `tw.daily_bar_adjusted`（2026-08-05）

> **觸發**：封存 `archive-20260805-dirfamily-p6-s4b-alog-beta2` 對 `probe_classical_ts_phase0b.py`／`train_classical_ts.py` 之 `TaiwanStockPriceAdj` 直綁曾 `--no-verify`；帳載正確後續＝改走 binding 100。  
> **授權**：Steward AskQuestion 批次 `rec_1_2_3`（含 WM36）。  
> **self-reported（#32a）**。

## 改動

| 檔 | 前 | 後 |
|---|---|---|
| `scripts/train_classical_ts.py` | `FROM "TaiwanStockPriceAdj"` | `world_concept.resolve_sql('tw.daily_bar_adjusted')` |
| `scripts/probe_classical_ts_phase0b.py` | 兩處 PriceAdj 字面（序列＋fallback 宇宙） | `resolve`→`quote_ident`；fail-closed |

語意不變：權威仍指向 `TaiwanStockPriceAdj`（binding_id=100／role=derived）——**不是**改讀 raw `tw.daily_bar`。

## 驗收

```text
$ python -c "… resolve tw.daily_bar_adjusted …"
Binding(… binding_id=100, table='TaiwanStockPriceAdj', …)

$ python scripts/train_classical_ts.py --run --stock 2330 --asof 2026-05-31 --horizon 5
✓ 2330 asof=2026-05-31 h=5 n_ret=251 fc_mean=… (dry-run)
```

靜態：兩檔對 `FROM "TaiwanStockPriceAdj"` **零命中**且含 `tw.daily_bar_adjusted`。

## 不做

- 未觸 `train_direction_stack.py` 等其餘 PriceAdj 存量（另帳／基線收斂）
- 未改 `ops/vendor_binding_baseline.txt`（棘輪只收斂、不於此輪寫寬）
- 未重跑 Phase 0b 全量（行為路徑等價；CPU 重＝另 GO）

*完。*

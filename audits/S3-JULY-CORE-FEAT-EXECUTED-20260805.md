---
status: executed
series: s3_features
depends_on:
  - audits/S3-JULY-CORE-FEAT-GO-20260805.md
---

# EXECUTED｜S3 July 特徵＋core asof（鋪 08-04 鏈）· 2026-08-05

> **GO**：`audits/S3-JULY-CORE-FEAT-GO-20260805.md`  
> **授權**：`S3-JULY-CORE-FEAT-go | FZ/GATE-keep | skip-sync | no-SIM-apply`  
> **self-reported（#32a）**。

## 1. 為何顧問仍顯示 as-of 2026-05-31（答用戶）

| 層 | 事實 |
|---|---|
| 價（PriceAdj） | 已到 **2026-08-04** |
| 顧問路由 | `build_single_ticker_rel_payload` → `max(panel_date)` from **`prediction_probability`** |
| 該表現況 | **唯一** panel＝**2026-05-31**（1695 列；P6 預設錨＋C/D「不滾動重灌」紀律） |
| 故 | 答句印 2026-05-31＝**表內最新快照**，不是硬編碼忽略 08-04 |

要改答句日期＝須後續 `predict_asof`＋`calibrate_relative_probability --emit`（**本帳未做**）。

## 2. 本輪執行

| 步 | 指令 | 結果 |
|---|---|---|
| 1 | `build_feature_panel.py --panels 2026-07-31 --asof` | **762** 股、**27,988** 值＠2026-07-31（~2.8 min） |
| 2a | `build_core_universe.py --liquidity… --asof`（**無** `--since`；誤含 2007） | 114 panel；最新核心過嚴→**撤銷、改 2b** |
| 2b | `build_core_universe.py --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial --asof`（對齊 S1） | **107** panel（2014-12-31…**2026-07-31**） |

log：`/tmp/s3-july-20260805/`

## 3. 驗收（DB）

| 項 | 值 |
|---|---|
| `feature_values` max panel | **2026-07-31**（distinct panel **114**） |
| `core_universe_asof` 2026-06-30 | **225**（與 S1 口徑對齊） |
| `core_universe_asof` 2026-07-31 | **204** |
| `core_universe` pan-hist | **13**（全窗齊特徵；predict **用 asof 名單**，不以 pan-hist） |
| `prediction_probability` max | **仍 2026-05-31**（未 emit） |

## 4. 未做（明示）

- `predict_asof --run --horizon 20 --asof …`  
- `calibrate_relative_probability --emit --horizon 20 --asof …`  
- SIM-apply／FinMind／改 DEFAULT 錨常數

## 5. 下一手 paste-ready（另授）

誠實可執行下一刀（特徵＋core 已就緒；emit 仍要有 `prediction_values`＠目標日）：

```
predict-asof-H20-2026-07-31-go | FZ/GATE-keep | skip-sync | no-SIM-apply
# 建議先 --dry-run；寫庫加 --run
# 然後：
P6-emit-H20-2026-07-31-go | FZ/GATE-keep | skip-sync | no-SIM-apply
# calibrate_relative_probability.py --emit --horizon 20 --asof 2026-07-31
```

說明：月盤錨＝**07-31**；真要「答句寫 08-04」須另確認 `_panel_matrix` 是否接受非月末 asof（消費 ≤asof 之最近特徵 panel）——**建議優先 emit＠07-31**，顧問 `max(panel_date)` 即會離開 05-31。

*完。*

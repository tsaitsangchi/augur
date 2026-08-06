---
status: executed
series: graph_consume
phase: G1
date: 2026-08-06
viewpoint: 2026-08-06T09:10+08:00
go: audits/GRAPH-CONSUME-PROBE-GO-20260806.md
plan: reports/augur_graph_consume_plan_first_20260806.md
self_reported: true
---

# EXECUTED｜GRAPH-CONSUME G1 probe · 2026-08-06

```text
GRAPH-CONSUME-probe-go | FZ/GATE-keep | skip-sync | read-only
# RC=0 · 零寫庫 · 零改碼 · #1 watcher 未動
```

## 1. 碼樹讀者

| 範圍 | 結果 |
|---|---|
| `src/**/*.py` 含 `stock_graph_edge` | **0 hits** → 無生產消費端 |
| `scripts/`（非 build／migrate） | **0** 額外讀者 |

→ 風險仍是「未來讀者無契約」，非「正在用錯 asof」。

## 2. 邊表 asof／型

| as_of_date | n |
|---|---:|
| **2026-08-05** | **33,695** |
| 2026-08-04 | 33,513 |
| 2026-06-30 | 13,021 |

| as_of | edge_type（庫內實名） | n |
|---|---|---:|
| 2026-08-05 | industry_same | 3,019 |
| 2026-08-05 | return_corr_60d | 15,987 |
| 2026-08-05 | return_corr_120d | 14,689 |
| （08-04／06-30 同三型，略） | | |

**Errata（對 G0 契約卡）**：計畫書草案寫 `corr_60`／`corr_120`；庫內實名＝**`return_corr_60d`／`return_corr_120d`**。後續 adapter／G2 **必須用實名**；文件 errata 另補（非本探針改碼）。

## 3. S-EQ 對照（LIVE）

| 尺 | 值 |
|---|---|
| PriceAdj 2330 max | **2026-08-05** |
| core_universe max | **2026-08-05** |
| 圖 `as_of_date=D` 列數 | **33,695** → S-EQ＠現 D＝**ok** |
| `as_of_date > PriceAdj` | **0**（無 leakage 嫌疑列） |

注：今日 #1 目標 D＝**08-06** 尚未到價 → 屆時若未 rebuild＠08-06，S-EQ＠新 D 將＝`graph_asof_missing`→SKIP（契約預期，非本 probe 失敗）。

## 4. #1／門

| 項 | 狀態 |
|---|---|
| watcher＠08-06 | ALIVE · WAIT |
| NF-pause／B3 standing | **未改** |
| 寫庫／業務碼 | **無** |

## 5. 下一步（未授）

- 文件 errata：edge_type 實名（可∥）  
- `GRAPH-CONSUME-adapter-stub-go`（G2；仍受 NF-pause）  
- 日更後 `GRAPH-REBUILD-2026-08-06-go`（寫側；與消費正交）

*完。*

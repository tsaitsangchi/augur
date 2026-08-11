---
status: executed
series: c1_arc_b_tri_narrow
date: 2026-08-07
go: audits/LOOP-EXPAND-DIR-NARROW-GO-20260807.md
prior_cycle: audits/SIM-LOOP-CYCLE-2-20260807.md
log_dir: /tmp/loop-expand-dir-0806
paste: "LOOP-EXPAND-DIR-narrow-go | FZ/GATE-keep | API-THAW-bounded | no-SIM-apply | tip=2026-08-06 | hold-#1"
self_reported: true
---

# EXECUTED｜LOOP-EXPAND-DIR-narrow · 2026-08-07

> **GO**：`LOOP-EXPAND-DIR-narrow-go` · tip／mdf until＝**2026-08-06**  
> **目的**：閉合 Cycle-2 再開之 **RG-DIR-PIT-03**（TRI＋mdf 對 tip）。  
> **不含**：假 B3＠08-07、他表 dim-sync、S3 rebuild、sim-apply。

---

## 執行摘要

| 步 | 指令 | 結果 |
|---|---|---|
| TRI 窄窗 | `daily_maintenance --datasets TaiwanStockTotalReturnIndex --with-dim-sync --end 2026-08-06` | **RC=0**；by-dim-id（TAIEX／TPEx） |
| IV | `derive_market_iv --run --until 2026-08-06` | **RC=0**；6032 交易日 |
| MDF | `build_market_direction_features --run --since 2025-01-01 --until 2026-08-06` | **RC=0**；7694 列 |

### 錨（後）

| 錨 | 前（Cycle-2） | 後 |
|---|---|---|
| PriceAdj max | 2026-08-06 | **2026-08-06**（未動） |
| TRI max | 2026-08-04 | **2026-08-07**（源已有 D+1；end 請求＝08-06） |
| market_iv max | 2026-08-06 | **2026-08-06** |
| mdf max | 2026-08-04 | **2026-08-06** |
| mdf feat＠08-04/05/06 | 20／0／0 | **20／20／20** |

---

## Gap 回寫

| gap_id | 結果 |
|---|---|
| **RG-DIR-PIT-03** | **closed＠tip=2026-08-06**（TRI 窄窗＋mdf rebuild） |
| fred／RG-MACRO-SER-04 | **unchanged**（本 GO 排除；Cycle-2 仍 partial＠08-05） |
| Dividend／他 dim／S3／NF | **unchanged**（排除集） |

### 誠實殘差

| 項 | 狀態 |
|---|---|
| TRI＝**08-07**＞PriceAdj＝**08-06** | 源日曆可先於現貨價頂；**mdf 故意釘 until＝08-06**（對 Cycle-2／價 tip） |
| mdf＠tip 日 | **20** feat（無假綠缺欄） |
| #1 watcher | 仍 WAIT PriceAdj≥08-07；**未**假 B3 |

---

## 不做（已守）

- 全量／無過濾 `--with-dim-sync`、Dividend、其他 by-dim-id  
- S3 feature build／serve 換模／dgate 修綠／sim `--apply`

```text
LOOP-EXPAND-DIR-narrow-go | FZ/GATE-keep | API-THAW-bounded | no-SIM-apply | tip=2026-08-06 | hold-#1
```

*完。RG-DIR-PIT-03 相對 tip＝08-06 閉。*

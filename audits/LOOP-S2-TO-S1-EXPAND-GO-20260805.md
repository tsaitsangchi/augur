---
status: go
series: c1_arc_b
depends_on:
  - audits/S1-RAW-GAP-FROM-S2-20260805.md
  - reports/augur_s1_s2_s3_closed_loop_plan_20260804.md
---

# GO｜LOOP-S2-TO-S1-EXPAND · 2026-08-05

> **授權**：Steward AskQuestion `expand_go` → **`adopt_go`**（2026-08-05）  
> paste：

```text
LOOP-S2-TO-S1-EXPAND-go | FZ/GATE-keep | NHC-keep | API-THAW-bounded | no-SIM-apply
# scope: audits/S1-RAW-GAP-FROM-S2-20260805.md §2 P0–P1 only
# exclude: Dividend / wide-sync / dim-sync / S3 feature build / NF-pause lift
```

## 範圍

| 允 | 禁 |
|---|---|
| RG-DIR-PIT-03 方向特徵 as-of 對齊 | Dividend／G-DIV |
| RG-MACRO-SER-04 `sync_macro --no-catalog`（THAW） | `--with-dim-sync`／寬窗／放量 |
| RG-PX／CHIP 日頻 heal（若落後） | 股級 macro→`feature_values` build |
| Info／產業覆蓋稽核（唯讀＋記帳） | S3-D 邊／序列契約實作；NF 解凍；β5；sim `--apply` |

## 含義

採納 raw gap list＋THAW-bounded S1 擴大**執行集 §2**；預測⊥API 不變。

*裁 adopt 後改 status＝go 並開 EXECUTED。*

---
status: go
series: graph_consume
phase: G3
path: A
date: 2026-08-08
plan: reports/augur_graph_g3_hotpath_go_plan_20260807.md
prior_g2: audits/GRAPH-CONSUME-ADAPTER-STUB-EXECUTED-20260807.md
prior_gnn: audits/NF-E-GNN-0B-EXECUTED-20260807.md
paste: "GRAPH-G3-HOTPATH-go | path=A | FZ/GATE-keep | NF-pause | hold-#1 | no-train | no-prodset"
self_reported: true
layer: "[I]"
---

# GO｜GRAPH-G3-HOTPATH · path=A · 2026-08-08

```text
GRAPH-G3-HOTPATH-go | path=A | FZ/GATE-keep | NF-pause | hold-#1 | no-train | no-prodset
# A＝graph 聚合 → feature_candidate_values → 提拔閘（長）；本 GO＝材料化＋契約，≠ 提拔、≠ 熱路徑預設開
```

## 授權

Steward AskQuestion：`next=g3` → `g3_path=A`。

## 准許

| 項 | 內容 |
|---|---|
| 名（≤3） | `graph_ind_deg_xsec`／`graph_corr60_wdeg_xsec`／`graph_corr60_meanw_xsec` |
| 讀 | G2 `graph_consume` **S-EQ**；無邊日＝整 panel SKIP（`graph_asof_missing`） |
| 寫 | **僅** `feature_candidate_values` |
| 聚合法 | 邊表單向 → **無向展開**計度／權重；再同 panel 橫斷面 percentile（0–1） |
| 自測／CLI | `features.graph_candidate`＋`scripts/build_graph_candidates.py` |

## 禁止

- 寫 `feature_values`／改 prodset／掛 RankRidge／B3  
- `verify_candidate_promotion` 本窗默跑提拔／APPLY  
- 把 GNN 0b STOP 翻案；`--with-graph` 熱路徑（那是 path B）  
- median-fill；用非 S-EQ 硬讀舊圖當 08-07  

## 驗收

1. `--selftest` 全綠。  
2. 有圖 asof∩panel 寫入候選；`2026-08-07`（無圖）誠實 SKIP。  
3. 熱路徑仍不讀圖；NF-pause keep。

*go。*

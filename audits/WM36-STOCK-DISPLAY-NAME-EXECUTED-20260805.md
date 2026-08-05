---
status: executed
series: wm36_vendor_registry
depends_on:
  - audits/WM36-GAP-TAIWANSTOCKINFO-EXECUTED-20260804.md
  - audits/ADVISOR-PRED-KH-AUTOREL-TOPN-EXECUTED-20260805.md
---

# WM.36 新概念卡 `tw.stock_display_name`＋顧問 payload 接線（2026-08-05）

> **授權**：AskQuestion `info_semantic=new_concept`＋`concept_key=tw_stock_display_name`，decided_by=hugo。  
> **觸發**：`check_vendor_binding --gate` 紅於 `src/augur/advisor/payload.py` `TaiwanStockInfo` **1→3**（PRED-KH 股名查詢增處）。  
> **self-reported（#32a）**。

## 登錄

| 項 | 值 |
|---|---|
| concept_key | `tw.stock_display_name` |
| binding_id | **104**（演練 103 ROLLBACK 後） |
| source_table | `TaiwanStockInfo` |
| source_column | `stock_name` |
| channel_role | `observation` |
| mapping_status | `mapped` |
| category | `state` |
| decided_by | hugo |

腳本：`scratchpad/wm36_new_concept_tw_stock_display_name.py`（預設 ROLLBACK；`--commit` 落地）。

```text
$ python -m augur.catalog.world_concept --resolve tw.stock_display_name
Binding(… binding_id=104, table='TaiwanStockInfo', column='stock_name', role='observation')
```

**未動**：`tw.stock_industry_category`（102）／`tw.roster_membership`。

## 消費端

`src/augur/advisor/payload.py`：`_lookup_stock_names` → `resolve_sql(NAME_CONCEPT)`；三處股名查詢改經 helper。**零** `FROM "TaiwanStockInfo"` 字面。

行為煙測（同 TopK）：2330 台積電／2542 興富發／2347 聯強——名稱與分數不變。

## WM.36 閘

```text
✓ vendor 直綁閘：無新增
（清償列含 src/augur/advisor/payload.py TaiwanStockInfo）
```

未自動改 `ops/vendor_binding_baseline.txt`（棘輪只許手動收斂）。

## 不做

- 未 commit／push  
- 未處理其餘 repo PriceAdj／Info 存量直綁  

*完。*

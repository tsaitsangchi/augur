# U0-75 Registry EXECUTED — `tw.daily_bar` → binding **75**（2026-08-04）

> **位階**：[I] 執行留痕。  
> **授權**：`REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo`  
> **honesty**：`audits/U0-75-HONESTY-ISSUED-20260804.md`（本批 COMMIT 後**已消費**）  
> **dry**：`audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-DRY-SQL-20260804.md`  
> **殘差主帳**：`audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-20260804.md`  
> **別名可指**：`SIM-S0-RESIDUAL-TW-DAILY-BAR-REGISTRY-EXECUTED`（本檔為正式 EXECUTED）

---

## 執行結果

| 項 | 值 |
|---|---|
| concept_key | `tw.daily_bar` |
| authoritative_binding_id | **75** |
| source_table | `TaiwanStockPrice` |
| channel_role | `observation` |
| mapping_status（75） | **mapped**（COMMIT 前已是；本批不改 mapping） |
| source_column（75） | NULL（表級；本批不填欄） |
| decided_by | `hugo` |
| decided_at | `2026-08-04 13:37:44+08` |
| decision_ref | `REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo` |
| 未採 | binding **81** `TaiwanStockPriceAdj`（derived／restating） |

---

## 前後計數（live；`superseded_at IS NULL`）

| 度量 | 前 | 後 |
|---|---|---|
| mapped | **21／98** | **21／98**（不變——75 早已 mapped） |
| source_column 已填（sc） | **11／98** | **11／98** |
| `tw.daily_bar.authoritative_binding_id` | **NULL** | **75** |

本批本質＝**權威指定**（Annex F），非新登 unmapped→mapped。

---

## ROLLBACK 演練 → COMMIT

| 階段 | 結果 |
|---|---|
| dry | UPDATE 1＋INSERT 1 → current auth=75／decided_by=hugo → **ROLLBACK** |
| 驗回滾 | auth **NULL**／decided_by **NULL** |
| COMMIT | 同 SQL 末行改 COMMIT → **OK**（13:37:44+08） |

---

## 驗收

```text
✓ --resolve tw.daily_bar
  → Binding(concept_key='tw.daily_bar', binding_id=75, table='TaiwanStockPrice', column=None, role='observation')
✓ check_sim_clock.py --check
  → gate=SIM-CAL-R1 status=approved；anchor=2026-08-03
  → week_line：`sim 時鐘：K=0/3，下一格 2026-08-03，待結算 0 列`
  → `calendar_unmapped` 未置 true（僅 Unmapped 路徑設）
```

重驗（同日後續窗）：resolve／clock／mapped=21／sc=11／auth_concepts=12 — 與上表一致；未觸 81。

---

## honesty 消費

本批通行證僅解鎖 **75** 權威寫入；COMMIT 後 one-shot **已消費**，不得複用於 80／97／81 或其他 binding。

## 不做

- 未改 binding 81；未填 75 `source_column`  
- 未 sim `--apply`／未 FinMind 放量／未殺 A1／未 git commit  

# U0-37 Registry EXECUTED — binding 37／`jp.daily_bar`（2026-08-04）

> **位階**：[I] 執行留痕。  
> **授權**：`Q-R8=jp-ok`＋`REGISTRY-GO: binding=37 + honesty=37 + decided_by=hugo`  
> **jp-ok**：`audits/U0-37-JP-OK-20260804.md`  
> **honesty**：`audits/U0-37-HONESTY-ISSUED-20260804.md`（本批 COMMIT 後**已消費**）  
> **dry**：`audits/U0-37-DRY-SQL-20260804.md`

---

## 執行結果

| 項 | 值 |
|---|---|
| binding | **37** |
| concept_key | `jp.daily_bar` |
| category | `quantity` |
| source_table | `JapanStockPrice` |
| source_column | `Open,High,Low,Close,Volume` |
| channel_role | `observation` |
| decided_by | `hugo` |
| decided_at | `2026-08-04 11:34:18.450675+08` |
| 出欄（未登） | `Adj_Close` |

fail-closed：五欄於 `information_schema` **全 present**（另見表內有 `Adj_Close`，依裁**不入**）。

---

## 前後計數（live；`superseded_at IS NULL`）

| 度量 | 前 | 後 |
|---|---|---|
| mapped | **20／98** | **21／98** |
| source_column 已填（sc） | **10／98** | **11／98** |
| 權威指定概念（sc_auth） | **10** | **11** |

---

## ROLLBACK 演練 → COMMIT

| 階段 | 結果 |
|---|---|
| dry | INSERT concept／version＋UPDATE 37→mapped；暫 mapped／sc＝21／11 → **ROLLBACK** |
| 驗回滾 | binding 37 仍 `unmapped`／`concept_key` NULL；`world_concept` 無 `jp.daily_bar` |
| COMMIT | 同 SQL 末行改 COMMIT → **OK** |

---

## 驗收

```text
✓ --resolve jp.daily_bar
  → JapanStockPrice.Open,High,Low,Close,Volume（observation, binding_id=37）
✓ --check：概念 17／通道 98（mapped 21）；jp.daily_bar 列綠
```

---

## honesty 消費

本批通行證僅解鎖 **37**；COMMIT 後 one-shot **已消費**，不得複用於 80／97 或其他 binding。

## 不做

- 未登 80／97；未登 `Adj_Close`／第二通道  
- 未 git commit／push；未另開 A1；未 FinMind 寬窗  

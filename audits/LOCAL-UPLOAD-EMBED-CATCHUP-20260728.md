# LOCAL-UPLOAD embed catchup（2026-07-28）

> **位階**：[I] 操作 audit · **授權**：Steward 明示「補嵌本機匯入」· **零 FinMind／FRED**

## 範圍

`source_key=rdai_knowhow_docs`／`source_type=local_upload`（含同日 PDF 空密碼修復新入 itext）→ `build_sentences --scope items` → `embed_knowledge --layer sentence --scope items --gap-fill`（zh／en）。

## 補前 → 補後（local_upload）

| 指標 | 補前 | 補後 |
|---|---:|---:|
| items | 343 | 343 |
| item_text | 2227 | 2227 |
| sentences | 3425 | 3715 |
| sent zh／en | 1296／2129 | 1586／2129 |
| embedded any | 1434 | 1724 |
| emb zh／en | 1292／142 | 1582／142 |
| itext 零句 | 8 | 0 |

### rdai_knowhow_docs

| 指標 | 補前 | 補後 |
|---|---:|---:|
| items／texts | 329／2203 | 329／2203 |
| sentences | 2987 | 3277 |
| emb zh／en | 872／140 | 1162／140 |

## 跑程（stdout 真兆）

- `build_sentences --scope items`：段 8、切句 290、實插 290、0.8s
- `embed … zh --gap-fill`：處理 321、**新嵌 290**、junk 31、~3.1 分
- `embed … en --gap-fill`：處理 9,088、**新嵌 0**、junk 9,088（全為 en 長／短句略過）、~0.4 分

## 誠實殘留

- **en**：local_upload／rdai CLEAN 未嵌 1,987＝長度 junk（`<10` 或 `>1000`），**不強嵌**。
- **zh**：殘 4 句＝符號 junk（`*`／`**`），略過正確。

## 煙測

- `retrieve_items(…, access_scope=public, is_super=True)` 對「機房運作管理辦法」命中 PDF 批 `item_id∈{277934,277936}`（Qdrant timeout→pgvector 降級仍可召回）。
- `retrieve_all(scope=None)`＝fail-closed 0 命中（預期）；需登入／grant 或 super。
- `local_private`（erp_semantics／solar_rd 等）須擁有者或 super 路徑。

## 建議試問

- 「機房運作管理辦法重點？」
- 「資訊系統電腦帳號及密碼管理規定？」
- 「資料庫管理辦法／網路資源租用管理辦法？」

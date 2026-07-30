# 顧問作答優先序：KH9 → KH8 → KH7 [I]（2026-07-30）

> **位階**：[I] 執行層排序（本輪不入憲）  
> **定錨**：達較深 KH 水印＝本地 Know-how 理解更深 → 作答材料優先採用  
> **正交**：FZ-keep；不改 RBAC／CLEAN／relevant_citations／guard；≠ admit 自動寫 grant

## What

檢索與顧問主路徑在**相關度閘之後**（items 取 top-k 亦同）依 `knowhow_auto_admit_state.admit_depth` 排序：

**KH9（9）＞ KH8（8）＞ KH7（7）＞ … ＞ 0**

- `depth ≥ 7` 的 ItemCitation 排在公版 works／Attached **之前**
- `depth < 7` 的 items 排在 works **之後**
- 同 depth 內維持 `-score`（相似度／exact 比）

## Why

cosine／exact 命中常把淺水印或 OCR 雜訊推上 top-k；深水印（合成／證據／對抗已過）應優先進入 prompt，避免淺文覆蓋深結論。

## 落點

| 元件 | 職責 |
|---|---|
| `augur.knowledge.auto_admit` | `load_admit_depths`／`rank_item_citations`／`rank_citations_kh_first`；`DEEP_KH_FLOOR=7` |
| `philosophy.retrieval.retrieve_items` | 回傳前 `_finalize_items_kh_first` |
| `philosophy.retrieval.retrieve_all` | 合併後 `rank_citations_kh_first` 再截 k |
| `advisor.advise` | `relevant_citations` 後再 `rank_citations_kh_first` |
| `advisor.prompt.build_prompt` | 有 item 引文時注入 KH9＞KH8＞KH7 指示 |

## 驗收

- `--selftest`：`auto_admit` 排序 9→8→7→works→shallow
- 離題（MBB↔王陽明）仍 `query_relevant=False`
- 合成候選中 depth=9 ERP 排在 OCR／淺項之前

## 不做

- 不強制只答 depth≥9  
- 不改 `max_auto_depth`、不解凍 API、不入憲（另句）

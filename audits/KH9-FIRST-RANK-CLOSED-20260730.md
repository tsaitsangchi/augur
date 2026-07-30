# KH9-FIRST-RANK CLOSED（2026-07-30）

> **性質**：[I] 收官  
> **計畫**：`reports/augur_advisor_kh9_first_rank_plan_20260730.md`  
> **拍板**：Steward「執行 KH9-first」

## 做了什麼

| 項 | 結果 |
|---|---|
| `auto_admit.load_admit_depths`／`rank_item_citations`／`rank_citations_kh_first` | LAND；`DEEP_KH_FLOOR=7` |
| `retrieve_items`／`retrieve_all` | 回傳前依 admit_depth 重排 |
| `advise` | `relevant_citations` 後再 KH9-first |
| `prompt.build_prompt` | 有 item 引文注入 KH9＞KH8＞KH7 指示 |
| `--selftest` | `auto_admit` 排序綠；`relevance` 離題仍 False |

## 實測備註

- ERP 四檔與部分 OCR（如 277953）皆可為 `admit_depth=9` → **同分帶內仍依 score**；離題 OCR 靠相關度閘，不因 depth 放行。
- 顧問進程須重啟才載入新碼。

## 不做（依計畫）

- 未入憲；未改 RBAC／max_auto_depth；未解凍 API。

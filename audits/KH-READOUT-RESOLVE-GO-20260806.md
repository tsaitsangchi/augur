---
status: go
series: kh_loop_evolve
date: 2026-08-06
paste: "KH-READOUT-RESOLVE-go | FZ/GATE-keep | title-resolve | bounded-fulltext | no-web-approve"
plan: reports/augur_local_ai_kh_loop_evolve_opt_plan_20260806_readout.md
adopted: audits/LOCAL-AI-KH-LOOP-EVOLVE-OPT-READOUT-ADOPTED-20260806.md
self_reported: true
---

# GO｜KH-READOUT-RESOLVE · 標題／檔名 resolve＋有界讀出 · 2026-08-06

| 允 | 禁 |
|---|---|
| 偵測讀出意圖；標題／檔名 resolve → `item_id` | 無 RBAC 放出 private／未授權 domain |
| 有界分段載入 `item_text` 作 ItemCitation（`via=readout`） | 幻造未入库全文；無限灌 prompt |
| 掛 `advise()`：命中則優先於 ANN 雜訊 | 改 HUMAN_ONLY；web 放行 |
| 錨題：國碩-ERP-GP_DR說明…請讀出具體內容 | 無 cite 偽「讀完」 |

```text
KH-READOUT-RESOLVE-go | FZ/GATE-keep | title-resolve | bounded-fulltext | no-web-approve
```

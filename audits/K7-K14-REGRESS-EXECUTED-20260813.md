---
status: executed
series: local_ai_kh
track: K7-K14
date: 2026-08-13
viewpoint: 2026-08-13T10:12+08:00
go: audits/KH-IDLE-TRIPLE-GO-20260813.md
script: scripts/kh_query_form_matrix.py
log: /tmp/kh-k7-k14-0813/matrix.log
prior_matrix: audits/KH-QUERY-FORM-MATRIX-EXECUTED-20260812.md
prior_k7_8b: audits/KH-K7-PRODUCT-8B-EXECUTED-20260812.md
paste: "K7-K14-REGRESS-EXECUTED | matrix A+B PASS | resolve=277948/Genero | no-LLM-rebench | no-autolift"
self_reported: true
layer: "[I]"
---

# EXECUTED｜K7／K14 回歸 · 2026-08-13

## K14 · 問法矩陣

```text
python scripts/kh_query_form_matrix.py   # A+B
→ MATRIX PASS (offline+live)
```

| 層 | 結果 |
|---|---|
| A 零 IO | **24 PASS**（intent／hint／ask_tail／prefer） |
| B LIVE | **5 PASS**：canon **277948** resolve＋cite；Genero xml／srv 錨；plain→0 cite |

## K7 · 錨題管線

本窗＝**resolve／cite 回歸**（矩陣 B＝K7 管線前段）。  
全量 8b LLM 逐步口吻 **不重跑**（既帳 `KH-K7-PRODUCT-8B-EXECUTED` 仍準；避搶 A2B3／LLM 鎖）。

| 尺 | 狀態 |
|---|---|
| 命中 canon／假「無此內容」 | **綠**（LIVE cite） |
| 逐步口吻產品 | **守既帳**（8b）；本窗未再 LLM |

未改 RBAC／未開 AUTO-LIFT／未動市場。

*完。*

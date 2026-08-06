---
status: executed
series: kh_loop_evolve
open_problem: "PDF-C"
date: 2026-08-06
plan: reports/augur_pdf_c_ocr_plan_20260806.md
paste: "PDF-C-OCR-apply-go | queue=P0 | dry-run-pass | FZ/GATE-keep"
code_go: audits/PDF-C-OCR-CODE-GO-20260806.md
self_reported: true
---

# PDF-C-OCR-APPLY-GO · 2026-08-06

```text
PDF-C-OCR-apply-go | queue=P0 | dry-run-pass | FZ/GATE-keep
```

## 交付

| 項 | 結果 |
|---|---|
| 命令 | `scripts/backfill_pdf_ocr.py --apply --queue P0 --trigger-chars 200 --max-pages 40` |
| 標記 | S0 `<!-- via=pdf_ocr -->` + `origin_media_sha=` |
| 句／chunk | 該 item 舊句與 philosophy_chunk 已清（embedding CASCADE）；**未**重跑切句／embed |
| gain／applied | **4／4** |

## P0 結果

| item_id | 舊字元 | OCR 後（含標記） |
|---|---|---|
| 277775 | 50 | 660 |
| 277771 | 103 | 364 |
| 277778 | 144 | 273 |
| 277760 | 186 | 4300 |

剩餘 local `.pdf` 字元&lt;200：**0**（P0 佇列空）。

## 殘債

- ANN／concordance：P0 已補跑 KIP（eligible×4）；完整 qdrant 可選
- P2（200–2000）：另貼 apply 或擴大 queue 再 GO
- S1 `ocr_transcribe`／顧問揭露：未做（P4）
- 附帶修：檔名含「如何」之 bare-title 勿當問句否決（`readout.py`）

## 後續

KIP backfill（切句＋embed＋kh4）：`item-ids 277775,277771,277778,277760` → **eligible×4**。

*executed · apply P0。*

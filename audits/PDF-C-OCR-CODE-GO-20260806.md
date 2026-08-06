---
status: executed
series: kh_loop_evolve
open_problem: "PDF-C"
date: 2026-08-06
plan: reports/augur_pdf_c_ocr_plan_20260806.md
paste: "PDF-C-OCR-code-go | trigger_chars=200 | max_pages=40 | source_mark=S0 | no-ASR | no-caption"
tool_go: audits/PDF-C-OCR-TOOL-GO-20260806.md
self_reported: true
---

# PDF-C-OCR-CODE-GO · 2026-08-06

```text
PDF-C-OCR-code-go | trigger_chars=200 | max_pages=40 | source_mark=S0 | no-ASR | no-caption
```

## 交付

| 件 | 路徑／行為 |
|---|---|
| OCR 臂 | `fileparse.ocr_pdf_pages` / `extract_text(..., ocr_pdf=True)`；預設 **off** |
| 觸發 | 字層 `<200` 或 `no_text`；`max_pages=40`；品質閘短文／空白頁 |
| S0 | `<!-- via=pdf_ocr -->` 前綴；`source_type` 仍 `local_upload` |
| backfill | `scripts/backfill_pdf_ocr.py`（**預設 dry-run**；`--apply` 硬拒至 apply-go） |
| acquire | 可選 `--ocr`（preflight＋ingest）；預設 off |
| 寫庫 | **未做** |

## P0 dry-run（4／4 gain）

| item_id | pypdf | ocr | 註 |
|---|---|---|---|
| 277775 | 50 | 572 | STEP BY STEP 可讀；圖頁仍有雜訊 |
| 277771 | 103 | 276 | 可讀增 |
| 277778 | 144 | 185 | 微增 |
| 277760 | 186 | 4212 | 大幅增（頁面多） |

`fileparse --selftest`：全通過。

## 下一步

```text
PDF-C-OCR-apply-go | queue=P0 | dry-run-pass | FZ/GATE-keep
```

*executed · code 階；未寫庫。*

---
status: executed
series: kh_loop_evolve
open_problem: "PDF-C"
date: 2026-08-06
plan: reports/augur_pdf_c_ocr_plan_20260806.md
paste: "PDF-C-OCR-tool-go | engine=tesseract | render=pymupdf | langs=chi_tra+eng | FZ/GATE-keep"
self_reported: true
---

# PDF-C-OCR-TOOL-GO · 2026-08-06

```text
PDF-C-OCR-tool-go | engine=tesseract | render=pymupdf | langs=chi_tra+eng | FZ/GATE-keep
```

## 交付

| 項 | 結果 |
|---|---|
| 引擎 | Tesseract 5.x；`chi_tra`+`eng`（本機已有） |
| 渲頁 | **pymupdf**（venv 已裝）；不依賴 poppler |
| 煙測檔 | `item_id=277775` `TIPTOP如何新增使用者.pdf` |
| pypdf | 50 字 |
| OCR 前 3 頁（DPI 200） | **572** 字；elapsed ~2.9s → `TOOL_SMOKE_OK`（≥80） |
| 寫庫 | **未做**（待 `PDF-C-OCR-code-go`／`apply-go`） |

## 觀察

- 掃描／簡報型 PDF：字層極短，OCR 可補出「STEP BY STEP」等可讀正文，但圖多頁仍有亂碼／雜訊——品質閘與人工抽頁仍必要。
- 未改 `fileparse`／acquire 預設路徑。

*executed · tool 階。*

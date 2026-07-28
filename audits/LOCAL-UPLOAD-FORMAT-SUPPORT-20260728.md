# Admin 本機匯入格式支援補強（2026-07-28）

> **日期**：2026-07-28 · **位階**：[I] · **範圍**：admin 本機匯入 / `acquire_local_files.py` / `fileparse.py`

## 本次結論

- `docx` / `xlsx` / `pptx` / 一般 PDF：已可抽文字入庫。
- **加密 PDF**：先試空密碼；owner-only / 空密碼可開者不再誤報 `encrypted`，真需密碼者誠實 `encrypted`。
- **Image**：已納入副檔名辨識與 OCR 路徑；若主機缺 `tesseract`，誠實回 `missing_ocr`，不再落 `unknown_ext`。
- **舊 Office**：`doc` / `xls` / `ppt` 已納入辨識；本機有 `xlrd` 時可讀 `.xls`，其餘舊格式或缺系統轉檔器時回 `missing_parser`。
- **未放鬆**：license DB CHECK、`access_scope`、`owned_local` 私有軌、FinMind/FRED 凍結皆不動。

## 支援矩陣

| 類型 | 副檔名 | 結果 | 備註 |
|---|---|---|---|
| Word | `.docx` | `ok` | `python-docx` |
| Word（舊） | `.doc` | 條件式 | 走 `soffice/libreoffice` 轉 `.txt`；缺轉檔器回 `missing_parser` |
| Excel | `.xlsx` | `ok` | `openpyxl` |
| Excel（舊） | `.xls` | 條件式 | 優先 `xlrd`；缺則 fallback `soffice`；兩者都無回 `missing_parser` |
| PowerPoint | `.pptx` | `ok` | `python-pptx` |
| PowerPoint（舊） | `.ppt` | 條件式 | 走 `soffice/libreoffice`；缺轉檔器回 `missing_parser` |
| PDF | `.pdf` | `ok` | 文字層抽取 |
| PDF（真加密） | `.pdf` | `encrypted` | 需使用者先解密或另案做密碼 UI |
| Image | `.jpg/.jpeg/.png/.webp/.gif/.tif/.tiff/.bmp` | 條件式 | 有 `pytesseract+tesseract` 才能 `ok`；缺引擎回 `missing_ocr` |

## 驗證

- `./venv/bin/python -m pytest tests/test_fileparse_formats.py -q` → `9 passed`
- `./venv/bin/python -m augur.knowledge.fileparse --selftest` → 全通過
- `systemctl --user restart augur-admin`
- `curl -I http://127.0.0.1:8500` → HTTP 501（HEAD 不支援，但服務已起）

## 本機限制（本輪實測）

- 目前主機 **沒有** `tesseract`，故 image OCR 會回 `missing_ocr`。
- 目前主機 **沒有** `soffice/libreoffice`，故 `.doc` / `.ppt` 會回 `missing_parser`；`.xls` 仍可走 `xlrd`。

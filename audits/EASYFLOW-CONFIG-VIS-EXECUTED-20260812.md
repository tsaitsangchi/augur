# EasyFlow 設定可見化（有界 OCR／入庫）· EXECUTED

date: 2026-08-12  
kind: ops_executed  
status: DONE  
go: `audits/EASYFLOW-CONFIG-VIS-GO-20260812.md`  
open: Steward「GO（有界 OCR／入庫，或匯入真實設定匯出）」

## 做了什麼

| 步 | 結果 |
|---|---|
| `_read_image` 預設 OCR | `OCR_LANGS=chi_tra+eng`（`fileparse.py`） |
| 重 OCR 寫回 | `01.jpg`=**1818821**、`02.jpg`=**1818818**（`<!-- via=image_ocr chi_tra+eng -->`） |
| 欄位可見化 pack 入庫 | **1956036** `EasyFlow開合設定-欄位可見化-OCR.md` → KIP → **eligible** |
| asmi300 送簽 OCR 入庫 | **1956037** `ERP asmi300 EasyFlow送簽設定-OCR.txt` → KIP → **eligible** |
| `6-1將表單資料存入Table.ppt` | 已在庫 **1818633** eligible（acquire 判重） |
| readout 截圖副檔名 | `_EXT_RE`／`_EXT_THEN_ASK_RE` 加 `jpg|jpeg|png|…`；自測＋`kh_query_form_matrix` **PASS** |
| S0 | `kh0_breach=0` |

## 抽驗（local scope）

- `EasyFlow開合設定-欄位可見化-OCR.md` → cites **1956036**（含「標準站台」「SOAP」「wsj」欄位名）
- `ERP asmi300 EasyFlow送簽設定-OCR.txt` → cites **1956037**
- `01.jpg中，詳細說明標準站台設定` → hint=`01.jpg` → cites **1818821**

## 誠實上限（未關）

- 截圖 OCR **欄位名**可讀；**實機 IP／SOAP URL 數值**不可靠 → **仍需真實設定匯出**（匯入路徑未開：無匯出檔）
- 原始 `01.jpg`／`02.jpg` 正文仍糊；答欄位名請優先 **1956036**
- `1_EasyFlowGP系統操作.ppt` 等 parse／soffice 失敗件 → hold（非本 GO 強拉）

## 禁守

整庫 OCR；假造 IP／URL；promote；ASR→PDF。

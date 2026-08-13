# Image OCR 閉集重跑 · EXECUTED

date: 2026-08-12  
kind: ops_executed  
status: DONE  
go: `audits/IMAGE-OCR65-GO-20260812.md`  
open: Steward「處理所有image問題」  
log: `/tmp/image-ocr65-apply.log` · kip `/tmp/image-ocr65-kip{1,2}.log`

## 程式
- `fileparse.IMAGE_OCR_MARK`＝`<!-- via=image_ocr chi_tra+eng -->`
- `import_qualification.preflight`：`reason=image_ocr` 自動蓋標記
- `scripts/backfill_image_ocr.py`（增益＝新 CJK > 舊 CJK；預設 dry）

## 閉集結果（圖檔標題件 67）

| 尺 | 值 |
|---|---|
| 已有 chi_tra（EasyFlow 01/02） | 2 |
| 佇列缺標記 | 65（磁碟全在） |
| **APPLIED** | **63** |
| NO_GAIN（CJK 無增益；截圖不可讀） | **2**：277954、277955 |
| 事後 marked / unmarked | **65 / 2** |
| KIP | 兩批；kh4 **eligible** 全過 |
| S0 / matrix | breach=0；MATRIX PASS |

## 抽驗
- `asfi301_asfi511_取替代操作.png` → **277947**（CJK 0→217）
- `01.jpg中，詳細說明標準站台設定` → **1818821**
- `S022038-ERP無權限.png` → **277959**

## 誠實殘項（非本窗硬關）
1. **NO_GAIN×2**：畫面無可讀 CJK；不蓋假標記  
2. 多數圖檔 `domain=smoke_test`（非 `local`）——授權域未含 smoke_test 的帳號讀不到；若要納一般顧問域需另 GO 改域／grant  
3. OCR 仍會糊（UI 截圖）；**≠**視覺理解模型；數值欄仍以現場為準  
4. 嵌在 PPT／DOCX 內之圖 ≠ 本閉集（標題無圖副檔名）——另窗

## 禁守
整庫 PDF OCR；ASR→圖；假造；promote。

# EasyFlow 設定可見化（有界 OCR／入庫）· GO

date: 2026-08-12  
kind: ops_go  
status: EXECUTED  
executed: `audits/EASYFLOW-CONFIG-VIS-EXECUTED-20260812.md`  
open: Steward 口令「GO（有界 OCR／入庫，或匯入真實設定匯出）」

## 授權（有界）
1. `_read_image` 預設 OCR 語系＝`chi_tra+eng`（對齊 PDF-C）  
2. 重 OCR 並寫回：`01.jpg`／`02.jpg`（EasyFlow 開合設定畫面；item 1818821／1818818）  
3. 入庫：`ERP asmi300 EasyFlow送簽設定`（正文＋內嵌圖 OCR 合成 txt）  
4. 可選入庫 EFGP 缺件：`6-1將表單資料存入Table.ppt`（若未在庫）  
5. 誠實帳：截圖**欄位名**可讀；**實機 IP／SOAP URL 值**若 OCR 不可靠 → 標需真實匯出  

## 禁
整庫 OCR；ASR→PDF；promote；無真實匯出檔時假造 IP／URL。

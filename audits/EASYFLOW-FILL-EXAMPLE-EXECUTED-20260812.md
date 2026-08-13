# EasyFlow 設定類 · 填寫範例可見化 · EXECUTED

date: 2026-08-12  
kind: ops_executed  
status: DONE  
go: `audits/EASYFLOW-FILL-EXAMPLE-GO-20260812.md`  
open: Steward「將此專案類似的問題都處理讓使用者知道填什麼的範例內容」

## 交付

| 項 | 結果 |
|---|---|
| 填寫範例包 | **1956038** `EasyFlow整合站台設定-填寫範例-wsj_file.md` eligible（含 `wsj02=10.1.2.30`／`wsj04=EFGP_PROD` 等） |
| 答法契約 | **1956040** `TIPTOP設定類問答-填寫範例契約.md` eligible |
| 欄位可見化 v2 | **1956039**（鏈到範例包） |
| compact prompt | `(g)` 設定題強制 `欄位=值`；`want_fill` 輸出提示；自測綠 |
| readout prefer | 種子加 wsj／填寫範例／站台 IP |
| S0 | breach=0；matrix PASS |

## 抽驗
- 問檔名 → cites **1956038**（含 `wsj02=10.1.2.30`／`EFGP_PROD`）
- 問 `wsj02如何填寫`／`EasyFlow 站台 IP` → intent＋alias → **1956038**（非空步驟字典短列）

## 有界誠實
- **未**對全庫 ~4 萬欄位字典批量造範例（禁瞎填）  
- 範例＝格式示範；實機 IP／庫名仍以現場為準  
- 同類高頻設定作業可另包擴充；本窗＝EasyFlow 站台（wsj）類＋答法契約＋prompt 強制 `欄位=值`

## 禁守
假造客戶真值；promote；市場改盤。

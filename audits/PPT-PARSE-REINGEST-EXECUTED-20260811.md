# PPT 抽字修復＋.ppt 補入庫（EXECUTED）

date: 2026-08-11  
kind: ppt_parse_fix + bounded_reingest  
paste: "job25 .ppt skip＝缺 Impress／txt 濾鏡 | _read_ppt→pptx | 33→32 ok | 生產管理.ppt 可 readout"

## 症狀
- UI 問 `TIPTOP GP5.3-生產管理.ppt` →「知識庫中無此內容」
- 用戶已匯入 uploads；job25：`ok=53 skip=49`（`.pptx` 入庫、舊 `.ppt` 幾乎全 skip）

## 根因
1. 系統僅有 `libreoffice-core`，缺 **`libreoffice-impress`** → soffice「source file could not be loaded」
2. 裝 Impress 後仍缺 Writer **txt 匯出濾鏡** →「no export filter for …txt」
3. `fileparse._read_ppt` 原本走 `--convert-to txt`（會卡在 2）
4. readout `_EXT_RE` 未納 `.ppt/.pptx`（檔名意圖脆）

## 修復
- `fileparse._read_ppt`：soffice **→ pptx → python-pptx**；`_read_via_soffice` 先複製 ASCII 暫名、timeout 120s
- `readout._EXT_RE` 納入 ppt/pptx；selftest 覆蓋 bare ppt
- 本機裝 `libreoffice-impress`（用戶 WSL apt）
- 補跑：`/tmp/ppt-reingest-0811` 33 檔 → **入庫 32、dup 1**（job 敘述於 acquire log；含 `TIPTOP GP5.3-生產管理.ppt`）

## 驗收
- `extract_text(…生產管理.ppt)` → `kind=ppt`、正文含「生產管理系統」
- job26 acquire：33→32 ok＋1 dup；item `1818527`＝生產管理.ppt
- 初批 `--no-kip` → kh4 **provisional**（readout 0）；補跑 KIP job26 → **eligible 32**、embed 285
- `advise_readout_citations('TIPTOP GP5.3-生產管理.ppt')` → 有引文；advise stub 非「無此內容」
- fileparse／readout `--selftest` 全過；8399／8090 已重啟載入 readout EXT

## 未做
- 未 apt 裝 `libreoffice-writer`（txt 路徑不必）
- 未 commit

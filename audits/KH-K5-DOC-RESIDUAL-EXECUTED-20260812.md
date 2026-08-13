# K5 Writer／doc 殘渣 · EXECUTED

date: 2026-08-12  
kind: inventory_executed  
status: EXECUTED  
go: `audits/KH-K5-DOC-RESIDUAL-GO-20260812.md`  
prior: `audits/DOC-WRITER-REINGEST-EXECUTED-20260811.md`

## 盤點（`.augur_uploads` `.doc` sha 去重）
| 項 | 值 |
|---|---|
| unique | **216** |
| 標題已在庫 | **212** |
| 殘 | **4** |

## 殘處置
| 檔 | 判 | 處置 |
|---|---|---|
| `付款問題Doc1.doc`（296960 B） | Writer→txt 空；docx **0 段／2 圖** | **hold-keep**（純圖；非 Writer 殘；OCR 另 GO） |
| `~$資產2013-SOP.doc` 等 3 支 | Word 鎖檔／162 B／`parse_error` | **忽略**（非語料） |
| （含 `~$灣各窗口分機.doc` 可抽 35 字） | 鎖檔名 | **忽略** |

## 結論
大批 Writer reingest 後 **無待入庫可抽文字殘渣**；唯一真殘＝純圖 Doc1。

## paste
```text
KH-K5-DOC-RESIDUAL-EXECUTED | uniq=216 | in_db=212 | Doc1=image-only-hold | locks=ignore
```

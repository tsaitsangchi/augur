# DOC Writer 大批 reingest · GO

date: 2026-08-11  
kind: plan_go  
status: GO  
plan_nav: `reports/augur_opt_stepwise_best_next_plan_r14_20260811.md` #24 Phase2.1  
paste: "DOC-WRITER-REINGEST-go | unique=213 | writer=ii | public_domain+public | hold-#1-keep | no-promote"

## 雙明示
- Steward：開 DOC 大批 reingest GO  
- 本帳：執行 uploads 去重後 **213** 支 `.doc`（probe：doc=212／no_text=1）

## 範圍
- 暫存：`/tmp/doc-batch-reingest-0811`（sha256 去重自 `~/.augur_uploads`）  
- license=`public_domain` access_scope=`public`（對齊既有 ERP／TIPTOP 文件批；≠ ASR 軌）  
- source_key=`local_files_local`；跑 KIP  
- **不**碰 tip／B3／升格（hold-#1）

## 驗收
- acquire 結束有 summary；audit EXECUTED  
- 新入／dup／skip 分類誠實  
- 抽 1 檔 readout 可命中（若 eligible）

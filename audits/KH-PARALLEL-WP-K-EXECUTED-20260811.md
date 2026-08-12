# KH ∥ WP-K · r14 選刀並行執行帳

date: 2026-08-11  
kind: executed_parallel  
status: EXECUTED（∥主軸 WAIT tip≥08-11）  
plan: `reports/augur_opt_stepwise_best_next_plan_r14_20260811.md` §2 Phase1p／WP-K  
paste: "KH-PARALLEL-WP-K | #24 Writer.doc | #26 private-smoke | #25 via | hold-#1-keep"

## 觸發
Steward：主軸 WAIT 下先做知識∥（Writer／smoke）。

## 做了什麼
1. **#24**：確認 `libreoffice-writer` **ii**；`.doc` 抽字 PASS（含 `erp專案推動小組織成員.doc`、`WebServices Debug 操作說明.doc`）。  
   `_read_doc` 加強：txt 失敗時 fallback **docx→python-docx**（對齊 ppt 套路）。  
2. **reingest**：`erp專案推動小組織成員.doc` → **dup**（已在庫 item **1818691** public／public_domain）；KIP#33 補齊。  
3. **#26／#25 smoke**：

| 題 | scope | 期望 | 結果 |
|---|---|---|---|
| `WebService程式撰寫(I).avi：請讀出…` | unauth | 0 | PASS |
| 同上 | super / owner:1 | ≥1 · via mark | PASS · id **1818835** · `<!-- via=asr_transcribe -->` |
| `erp專案推動小組織成員.doc：請讀出…` | super／domain local | ≥1 | PASS · id **1818691** |

4. `fileparse --selftest` 全通過。

## 未做／誠實
- 未改 tip／未 B3／未升格（守 hold-#1）。  
- `.doc` 大批歷史 skip 未整批重掃（要另 `DOC-WRITER-REINGEST-go`）。  
- 1818691 仍為先前 **public_domain** 入庫；內容 sha1 冪等，**未**改成 owned_local（避免雙重授權敘事；若要私有化須另策略）。

## 選刀板建議狀態
- #24：🟡→**部分綠**（引擎在＋單檔 OK；大批 reingest 仍開）  
- #25／#26：🟡→**抽樣 PASS**（建議固化 `KH-PRIVATE-SMOKE-go`）

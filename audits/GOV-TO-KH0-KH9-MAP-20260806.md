---
status: registered
series: kh0_kh9
date: 2026-08-06
viewpoint: 2026-08-06T09:15+08:00
plan: reports/augur_kh0_to_kh9_project_plan_20260806.md
source_ui: "http://localhost:8500/gov"
self_reported: true
---

# REGISTER＋MAP｜gov → KH0–KH9 · 2026-08-06

> 對照 Steward 貼上之 `/gov` 唯讀頁 ＋ `run_kh_chain.py --check` LIVE。  
> **不**改 license／admission gate；**不** approve／activate。

## A. gov 面板 → 層

| gov 區塊 | 數（頁面） | 對層 | 解讀 |
|---|---|---|---|
| 治理覆蓋 governed_active/active | 96/97（98%） | KH2／治權 | 幾乎皆 active；⚠ 多 bulk-seed、缺真人 approve 升級留痕 |
| 審批狀態機 | proposed=3504 · active=97 · approved=3 · suspended=1 | KH2 入口 | 人簽稀；機器批／bulk 為主路徑須誠實 |
| IMPORT-QUAL-S2 | jobs=14 · quals=1061 · pass=1061 | **KH1** | 合格帳完整；ingest：dup=633 · skipped=229 · short=111 · inserted=87 · dry=1 |
| 近 job #14 local | completed · dup 為主 | KH1 | 重匯 ERP 演練＝duplicate＝健康 |
| KIP runs | 14（#1/#3 failed 史料） | KH1→管線 | local_files 收束；failed 不改 qual pass 敘事 |
| FT-COV per domain | erp 100%可答；他域 pending 高 | **KH3** | 可答集中 erp；他域終態未完 |
| Fulltext 終態 | unattempted≈121389 · skip_no_oa≈9638 · skip_license≈4268 | KH3 | blocked＝終態；unattempted＝製造池 |
| AI 預審 ADM-AI-ASSIST | score≈0.45 hold · assist audit | **KH2** | 非放行；逾時→heuristic 風險見品質檔 |
| 審批稽核近 15 | 全 assist | 治權 | 無人手 approve 軌 |

## B. 鏈檢查（庫 · 同窗）

| 指標 | LIVE |
|---|---|
| items | 285,351 |
| KH0 破口（普遍） | **138,999（48.7%）** |
| admit_depth | 3→396 · 4→2 · **7→145,952** · 9→2 |
| KH8 鑑別力 | **False** → 止於 7 |
| staging pending | 128,486 |

## C. 映射結論（給專案計畫）

1. **主缺口不在 IMPORT-QUAL 綠燈，在普遍 KH0 破口。**  
2. gov 的 erp 可答 100% **不能**外推全庫。  
3. depth 大量＝7＋KH8 無鑑別 ⇒ **KH8/KH9 不可宣稱已運轉**。  
4. 下一步主軸＝計畫書 Wave A／A.1；∥ Wave B／C；F 待判準。

## D. Paste

```text
GOV-TO-KH0-KH9-MAP-register | read-only
# plan: reports/augur_kh0_to_kh9_project_plan_20260806.md
```

候採納：`KH0-KH9-PROJECT-PLAN-adopt`。

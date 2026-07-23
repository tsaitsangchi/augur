# MC 工具層措辭衛生執行留痕 [I]（2026-07-23）

* **性質**：[I] 執行筆記（不創設義務；**不登錄 AL**）
* **拍板**：Steward 採納 `reports/augur_mc_post_ultracode_optimization_plan_20260723.md`——**僅路徑 A**（§二 #2、#5）；GOV-3 B 維持觀察；至 10-14 前不改 MC [N]、不開 v1.6、不假關 039 項；§0.3 [I] 與 GOV-3 B 入 [N] **另案**。

## 已施作

| # | 項 | 改動 |
|---|---|---|
| 2 | XRF-1 措辭衛生 | `compliance_lint`／`report`／README／selftest／fixture：去掉「[N] 條款宇宙」假宣稱；canonical＝97[N]+5[I] WHY；新範本 `constitution/adoption-drafts/RULING-PHRASEOLOGY.md` |
| 5 | v1.5 簿記 | `CLAUDE.md` 從屬 v1.4→**v1.5**；`mc_clauses.py` docstring §0.3 錨 v1.5；L1–L7 CS `mc-version` 既為 v1.5（039 已做）—本輪不重掃規格 [N] 正文內歷史 `v1.4` 引用 |

## 明示跳過

| 項 | 原因 |
|---|---|
| #1／#7 GOV-3 B | 維持觀察；升格另案 |
| #3 §0.3 [I] 誠實註 | 屬 MC 本文；拍板另案 |
| #4 DEF-2 | DEFER 至 GOV-3 B 觸發 |
| #6 RUL-2／026 | 維持現狀；不改 §8.3 [N] |
| 017／026 歷史本文 | 039／計畫硬禁 |
| 規格 [N] 正文 `AUGUR-MC v1.4` 字面 | 硬禁改規格 [N]；FM `mc-version` 已 v1.5 |
| OT-5／T-KS-6／T-L6-5／025／020 M2／10-14 | 禁止假關 |
| AL | 純工具／[I] 慣例，無新 [N] 義務 |

## 驗收

* `python3 -m tools.constitution_lint report` → **PASS 7／7**（2026-07-23 親跑）
* `--selftest`：本輪改動相關 G3 等綠；既有 `tr_rows_L2` 標記漂移以 `report --sync` 對齊（59→66）；G10 界線項為 HEAD 既有 FAIL、非本輪引入（未擴修）
* 硬禁路徑零 diff：`constitution/META-CONSTITUTION.md`、RULING-017／026、`AMENDMENT-LOG.md`、`specs/` [N] 正文

---

*零 MC／PA／規格 [N] byte；零 AL。*

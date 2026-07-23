# MC v1.6 最小優化升版說明 [I]（2026-07-23）

* **性質**：[I] 執行留痕（對齊 RULING-2026-040／AL-2026-044）
* **拍板**：Sole Steward **授權開 MC v1.6 最小優化**（覆蓋前裁「10-14 前不開 v1.6」）
* **計畫**：`reports/augur_mc_post_ultracode_optimization_plan_20260723.md` 路徑 C 最輕量分支

## 實際納入

| # | 條款／產物 | 級 |
|---|---|---|
| 1 | §0.1 版本 v1.5→**v1.6** | patch／minor |
| 2 | §0.3 **[I] 母集誠實註**（102＝97 [N]＋5 [I] WHY） | editorial [I] |
| 3 | Appendix I（變更摘要＋已定案程序澄清簿記） | [I] |
| 4 | RULING-2026-040＋AL-2026-044 | 升版依據 |
| 5 | L1–L7 CS `mc-version`→v1.6；CLAUDE／`mc_clauses`／selftest | 簿記 |

## 刻意排除

* GOV-3 B 升格 §8.1 [N]（**維持觀察**）
* DEF-2「世界模型」定義（DEFER）
* PA／五原則／§8 [N]／§0.3 [N] 四 bullet
* 重開已閉 major；改寫 RULING-017／026 歷史本文
* 假關：OT-5／T-KS-6／T-L6-5／025 residual／020 M2／無 Evidence 提早結清 10-14

## 驗證

* `python3 -m tools.constitution_lint report` → PASS 7／7
* 獨立對抗核驗：RULING-040 第七節十項（待非施作者）

## 建議下一句

**獨立核驗** RULING-2026-040 §七（非施作者）→ 登錄核驗 PASS 後收尾。

---

*零原則級；零假關；GOV-3 B 仍觀察。*

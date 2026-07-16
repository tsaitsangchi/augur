# Augur Amendment Log（憲章修訂登錄簿）

本登錄簿依《Augur Meta-Constitution》§8.5(c) 設置，為憲章修訂之唯一權威登錄。
每筆登錄之時間戳與不可否認性，以本儲存庫之 git 提交歷史為據。

---

## AL-2026-001

* **日期**：2026-07-16
* **修訂**：v1.0 → v1.1（major）
* **程序依據**：v1.0 §7（修訂當時之有效程序）；§8 治理章屬初始採行（initial adoption）
* **內容摘要**：新增 Principle 5（Accountability Before Action）、§2 Definitions、§8 治理章；§4 技術中立化；統一 canonical chain（EV.1–EV.12）。完整變更見憲章 Appendix C
* **修訂理由書**：[REVISION-RECORD-v1.0-to-v1.1.md](REVISION-RECORD-v1.0-to-v1.1.md)（載明 P5 符合 v1.0 §7 實質判準之論證）
* **具名批准人**：tsaitsangchi（法定姓名，同 GitHub 帳號 [tsaitsangchi](https://github.com/tsaitsangchi)）
* **效果**：依憲章 §8.1，具名批准人自 v1.1 生效時起擔任**首任 Constitution Steward**

## AL-2026-002

* **日期**：2026-07-16
* **修訂**：v1.1 → v1.2（minor）
* **程序依據**：§8.5；依 §8.6 版本語義，本輪為缺陷修復與一致性修正，無新原則、無原則級實質變更
* **內容摘要**：35 項經雙重對抗驗證成立之缺陷修正（1 critical、10 major、24 minor）。完整記錄見憲章 Appendix D
* **裁決人**：Constitution Steward（tsaitsangchi）

## AL-2026-003

* **日期**：2026-07-16
* **事項**：《Augur Governance Annex（治理附則）》v1.0 制定與生效
* **程序依據**：憲章 §8.1（Steward 制定並公開發布；本次於憲章生效後 90 日期限內完成）
* **文件**：[GOVERNANCE-ANNEX.md](GOVERNANCE-ANNEX.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **備註**：~~登錄名義暫以 GitHub 帳號為之；Steward 得隨時以書面裁決補登法定姓名（屬 patch 級編輯修正）~~ 已補登：Steward 於 2026-07-16 確認法定姓名即為 tsaitsangchi（與 GitHub 帳號相同），AL-2026-001 之登錄名義自始即為法定姓名，無待補事項（patch 級修正，依治理附則第 2 條第 3 款辦理）

## AL-2026-004

* **日期**：2026-07-16
* **事項**：解釋裁決第 2026-001 號——P4.E3 刪除／覆寫家族之 severity 適用尺度（採「原始 vs 衍生＋緩解程度」二軸綜合認定）
* **程序依據**：憲章 §8.1（解釋權；書面化、附理由、公開存檔、解釋先例）；治理附則第 6 條
* **文件**：[INTERPRETATION-RULING-2026-001.md](INTERPRETATION-RULING-2026-001.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **效果**：合憲審計報告（audits/CODE-COMPLIANCE-AUDIT-2026-07-16.md）AUD-08 定 major、AUD-09 回 major；驗證後統計定稿 critical 3／major 11／minor 12；對後續案件具拘束力

## AL-2026-005

* **日期**：2026-07-16
* **事項**：Steward 裁決第 2026-002 號——Layer 1 規格充任認定暨同案四項程序：(一) AUGUR-WM 充任認定、以 **v1.0** 生效（效力本 specs/WORLD-MODEL-SPECIFICATION.md，v0.1-draft 歸檔）；(二) 五份治權檔 Layer 定位登錄（發動 AL-2026-006）並裁定合規聲明補正期至 2026-10-14；(三) 合規聲明暫行模板發布（[COMPLIANCE-STATEMENT-INTERIM-TEMPLATE.md](COMPLIANCE-STATEMENT-INTERIM-TEMPLATE.md)）並追認 AUGUR-WM Annex C；(四) specs/ 目錄書面地位指定；(五) 措辭 patch 與檔頭從屬聲明之交辦（期限 2026-10-14）
* **程序依據**：憲章 §0.5、§8.6、§8.3 過渡規則 (a)(b)(c)、§8.1；治理附則第 2 條第 2 款、第 6 條
* **文件**：[RULING-2026-002-LAYER1-ADOPTION.md](RULING-2026-002-LAYER1-ADOPTION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）

## AL-2026-006

* **日期**：2026-07-16
* **修訂**：v1.2 → v1.3（minor）
* **程序依據**：§8.6（Layer 對照表之增列屬 minor、由 Steward 議決）；治理附則第 2 條第 2 款；與 AL-2026-005 同案辦理
* **內容摘要**：§0.5 對照表增列五份 augur 領域治權文件之定位登錄（系統核心思想→Layer 1、原則精華→Layer 4、CLAUDE.md→Layer 6、系統架構大憲章與 datasets 參考文件→Layer 7）並註記 Layer 1 規格充任認定。除 §0.5 對照表增列（及 §0.1 版本欄、Appendix E [I] 隨附）外，無其他條文變更、無原則級變更。完整摘要見憲章 Appendix E；v1.2 歸檔於 [META-CONSTITUTION-v1.2.md](META-CONSTITUTION-v1.2.md)
* **裁決人**：Constitution Steward（tsaitsangchi）

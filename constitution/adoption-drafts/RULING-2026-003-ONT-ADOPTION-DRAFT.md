> # ⚠️ DRAFT — 待 Constitution Steward（tsaitsangchi）簽署方生效
>
> **本文件為 Steward 幕僚起草之充任裁決「草案」，本身不生任何效力。**
> 依 `AUGUR-MC v1.3 §8.1`／`§0.5`／`§8.6`，充任認定（adoption）為 Constitution Steward（人類）之裁決行為；Agent 不得作成充任、不得宣告任何規格已生效。本草案僅為「裁決前就緒化」產出，供 Steward 覆核、修改、簽署或退回。**未經 Steward 具名簽署前，`AUGUR-ONT` 仍僅具提案地位、不生效力。**

---

# Augur Steward 裁決第 2026-003 號（草案）

**Layer 2 規格（Ontology）充任認定**

* **依據**：`AUGUR-MC v1.3 §0.5`（規格登錄與充任；Layer 對照表 Layer 2 欄已登錄「Ontology Specification」）、`§8.6`（版本語義與引用格式）、`§8.1`（Steward 修憲／裁決權；Agent 不得參與）、`§8.3`（合規聲明義務）、`AUGUR-WM v1.0 §WM.39`（草案地位）、`§WM.44`（逐條對應矩陣＝形式充分性生效要件）
* **裁決人**：Constitution Steward（tsaitsangchi）　—　**【草案：待簽署】**
* **草案起草日**：2026-07-17（幕僚就緒化）
* **生效日**：＿＿＿＿＿（待 Steward 簽署之日填載）
* **擬登錄**：Amendment Log AL-2026-007（本裁決）　—　**【待簽署後由 Steward 登錄】**
* **源起**：Layer 2 概念層規格就緒化；`AUGUR-WM v1.0` DEFER 掛鉤（D2–D6 等）對 Layer 2 之承接需求

---

## 主文（草案）

### 一、充任認定（Layer 2 規格生效）

擬認定 `specs/ONTOLOGY-SPECIFICATION-v0.1-draft.md` **充任** `AUGUR-MC v1.3 §0.5` 對照表 Layer 2 欄所轄之「Ontology Specification」，自 Steward 簽署之日起生效。

* 生效版本號擬定為 **v1.0**（下層引用格式 `AUGUR-ONT v1.0 §{條款}`）。
* 效力本擬存於 `specs/ONTOLOGY-SPECIFICATION.md`；`v0.1-draft` 原文歸檔於原檔名（不再修改）。
* v0.1-draft → v1.0 之變更擬限於：版本欄、【地位】節改生效記錄、§0.1 生效要件成就記錄、Annex CS 識別區塊隨版更新。**無任何 [N] 條款實質變更、條款編號（ONT.{n}／T.{n}／DI.{n}／DO.{n}／EO.{n}／TM.{n}）不重排**。

## 依據與理由（草案）

1. **層級登錄已具備**：`AUGUR-MC v1.3 §0.5` 對照表 Layer 2 欄已登錄「Ontology Specification」，充任認定所需之「先在本表登錄」前提已滿足，本裁決僅就該欄位作充任。
2. **形式充分性已成就（`§WM.44`）**：本規格 Annex CS §CS.10（[N] 聲明區）已就 `AUGUR-MC v1.3` 全部 85 條 [N] 條款逐條 token 完整列示，並明列 P1.Y–P5.Y 為 [I] 排除；Annex TR（[I] 機器盤點底稿）另行逐條枚舉四上層條款。`§WM.44` 意義之形式要件滿足。
3. **linter 結構關卡通過**：`python3 -m tools.constitution_lint compliance specs/ONTOLOGY-SPECIFICATION-v0.1-draft.md` → **PASS（error 0 / warning 0 / info 1）**；WM.44 覆蓋由 warning 升為 info（85/85 條見於聲明文本），exit code 0。
4. **合規聲明具備（`§8.3`）**：Annex CS 為依 `AUGUR-WM v1.0 §11`（WM.39–WM.45）格式作成之 Constitutional Compliance Statement。

## 生效要件成就檢核表（草案）

| 要件 | 依據 | 狀態 |
|---|---|---|
| §0.5 Layer 對照表登錄 | `AUGUR-MC v1.3 §0.5` | ✅ 已具備（Layer 2 欄） |
| Constitutional Compliance Statement | `§8.3`／`AUGUR-WM v1.0 §11` | ✅ 已具備（Annex CS） |
| 形式充分性（逐條對應矩陣） | `AUGUR-WM v1.0 §WM.44` | ✅ 已成就（CS.10 85/85 條枚舉，linter info） |
| linter 結構關卡 | `tools.constitution_lint` | ✅ PASS（error 0 / warning 0 / info 1） |
| **Steward 充任認定** | `§0.5`／`§8.1`／`§8.6` | ⛔ **未成就（本草案不成就之；待 Steward 簽署）** |
| Amendment Log 登錄（AL-2026-007） | `§8.5(c)` | ⛔ **未登錄（待 Steward 簽署後為之）** |
| 實質充分性之違憲審查 | `§8.2` | ◻ 專屬 Steward，與形式充分性分屬二事 |

## 依賴序（草案）

* 本規格（Layer 2）為 **ONT → ID → KS** 依賴序之**首位**，上承已生效之 `AUGUR-WM v1.0`（Layer 1，Steward 裁決第 2026-002 號）與 `AUGUR-MC v1.3`（Layer 0）。
* `AUGUR-ID`（Layer 3，裁決草案 2026-004）與 `AUGUR-KS`（Layer 4，裁決草案 2026-005）對本規格之承接，須待本裁決先行生效方生效力。**建議 Steward 依 ONT → ID → KS 之序簽署。**

## 殘餘生效阻卻（草案）

1. **Steward 充任認定未成就**——本規格生效之唯一未成就形式要件，屬 Steward 裁決行為，非本規格或 Agent 單方可成就（`§0.5`／`§8.1`／`§8.6`、`WM.39`）。
2. **實質充分性之最終判斷**專屬 Steward 違憲審查程序（`§8.2`），與已成就之形式充分性分屬二事。
3. **OT-1～OT-4 已知緊張關係（CS.8）** 與 T.90／T.91 待決事項之下層判準採認，仍待 Steward／下層規格拍板。

---

> **【草案結語】** 本草案由 Steward 幕僚（Agent）起草，僅為裁決前就緒化，**不生效力、不構成充任認定**。Agent 未作成任何充任、未宣告任何規格已生效、未登錄正式 Amendment Log。**待 Constitution Steward（tsaitsangchi）具名簽署，並自行登錄 AL-2026-007 後，本裁決方生效力。**

# Augur Steward 裁決第 2026-006 號【草案】

**Layer 5 規格（Cognitive Kernel）充任認定 — v0.1-draft 提案**

> ## 【地位】[N]
>
> **本文件為 Steward 幕僚起草之 `v0.1-draft` 充任裁決提案，未經 Constitution Steward（人類 tsaitsangchi）簽署前不生效力。**
>
> * **充任認定**與 **`AUGUR-MC v1.3 §8.2` 實質合憲審查**均為 Constitution Steward 之裁決行為（`AUGUR-MC v1.3 §8.1`）。本草案之起草人（Steward 幕僚／Layer 5 子代理）**不宣稱任何規格已生效、不改本【地位】節自稱生效、不登錄正式 Amendment Log**。
> * 本文一切裁決字樣一律標 **DRAFT**；下列「主文」「生效要件檢核表」之效果，於 Steward 簽署充任並完成 `§8.2` 實質合憲人工簽核前，**均不發生**。
> * 本草案之作用僅為：向 Steward 陳明就緒狀態、彙整生效要件、標明殘餘阻卻，供 Steward 裁決時參酌。**採納與否、生效版本號、生效日、Amendment Log 編號，全由 Steward 於簽署時定之。**

* **依據**：`AUGUR-MC v1.3 §0.5`（Layer 對照表 Layer 5 欄：Cognitive Kernel Specification、Reasoning Engine、AI Model Selection）、`§8.6`（版本語義與引用格式）、`§8.1`（Steward 裁決權；Agent 不得參與）、`§8.2`（違憲審查／實質合憲審查）、`§8.3`（合規聲明義務與可判定性元規則）、`AUGUR-WM v1.0 §WM.39`（合規聲明適用範圍與效力）、`§WM.44`（逐條對應矩陣＝形式充分性生效要件）
* **裁決人**：Constitution Steward（tsaitsangchi）— **待簽署（DRAFT）**
* **起草**：Steward 幕僚（Layer 5 子代理）
* **草擬日**：2026-07-17
* **擬生效日**：**未定（待 Steward 簽署充任並完成 `§8.2` 實質合憲人工簽核後定之）**
* **擬登錄**：Amendment Log **AL-2026-010（保留位；DRAFT，未登錄）**
* **依賴序**：本規格（Layer 5）上承已生效之 **L0–L4**（AUGUR-MC v1.3、AUGUR-WM v1.0、AUGUR-ONT v1.0、AUGUR-ID v1.0、AUGUR-KS v1.0）
* **源起**：概念層 Layer 1–4 全部生效（里程碑 M1，AL-2026-009）後，解鎖執行層交界之 Layer 5（Cognitive Kernel）承接；Layer 5 規格就緒化

---

## 主文（DRAFT — 待 Steward 簽署）

### 一、充任認定（Layer 5 規格生效）【擬】

**〔DRAFT〕** 建議 Steward 認定 `specs/COGNITIVE-KERNEL-SPECIFICATION.md` **充任** `AUGUR-MC v1.3 §0.5` 對照表 Layer 5 欄所轄之「Cognitive Kernel Specification、Reasoning Engine、AI Model Selection」（World Understanding Engine，`§5` 角色四之治權）。

* 擬生效版本號 **v1.0**（下層引用格式 `AUGUR-L5 v1.0 §{條款}`）— 版本號由 Steward 簽署時確認。
* 生效後效力本擬存於 `specs/COGNITIVE-KERNEL-SPECIFICATION.md`；`v0.1-draft` 原文歸檔於 `specs/COGNITIVE-KERNEL-SPECIFICATION-v0.1-draft.md`。
* v0.1-draft → v1.0 之變更擬限於：版本欄、【地位】節改生效記錄、§0.1 生效要件成就記錄、Annex CS／Annex TR 隨版更新。**無 [N] 條款實質變更、編號不重排**（`AUGUR-MC v1.3 §8.6`、`AUGUR-WM v1.0 §WM.46`）。

### 二、安全關鍵層之額外完成判準（§8.2 實質合憲人工簽核）【擬】

**〔DRAFT〕** Layer 5 為**概念層與執行層之交界**（`AUGUR-MC v1.3 §0.6(b)`），定「何為合法推理」「Confidence 如何沿鏈傳播」「Hypothesis 之地位」「解釋義務」「AI model 為工具非世界權威」等推理之概念不變式；其產物落於 canonical chain EV.7 Reasoning，為 EV.8 Planning → EV.9 Human Authority Gate → EV.10 Action 之上游供給。錯誤之推理不變式將沿鏈污染結論並最終驅動 Action（P5），**本層屬安全關鍵層**。

故本草案就 Layer 5 之充任，除形式充分性（`§WM.44`）與 linter 結構關卡外，**另以 `AUGUR-MC v1.3 §8.2` 實質合憲之人工簽核為完成判準**：

* Steward 必須就本規格之推理不變式（尤 L5.1 合法推理、L5.2 引用鏈雙合法終點、L5.3 Confidence meet 上限傳播、L5.4 Hypothesis 可謬、L5.6 per-結論解釋、L5.7 AI model 非世界權威）作**實質合憲判斷**，確認其不牴觸 PA、P2、P4、P5 與 `§7`，並就 CS.2 六項已知緊張關係（尤 T-L5-6 resolution 定性）一併裁定。
* 此實質合憲人工簽核**非幕僚或 Agent 所能代行、非形式充分性所能替代**；未經此簽核，本充任不完成、Layer 5 不生效。

---

## 依據與理由（DRAFT）

1. **層級登錄已具備**：`AUGUR-MC v1.3 §0.5` 對照表 Layer 5 欄已登錄「Cognitive Kernel Specification、Reasoning Engine、AI Model Selection」（結構前提成就）。
2. **形式充分性已成就（`§WM.44`）**：Annex TR（TR.0／TR.A–TR.E／TR.Z）就五上層（Layer 0–4：MC＋WM＋ONT＋ID＋KS）全部 [N] 條款逐條／十位制區塊完整枚舉落點（承接／細化／DEFER／不觸及＋理由，缺 0 條）；【地位】節、TR.Z、CS.4 用語就「形式充分性已備、殘餘生效阻卻僅 Steward 充任認定未成就」一致收斂。
3. **linter 結構關卡通過**：`constitution_lint compliance` 對本 draft → **PASS（error 0 / warning 0 / info 1）**，退出碼 0，符合就緒門檻（error 為 0）。唯一 info 為 WM.44 骨架級形式充分性覆蓋提示（「85 條 MC [N] 條款均見於聲明文本」），屬資訊性、非 error、非結構阻卻。selftest 全綠。
4. **合規聲明具備正式格式（`§8.3`、`§WM.39–45`）**：Annex CS 為依 `AUGUR-WM v1.0 §WM.39–45` **正式格式**（非暫行模板）作成之 Constitutional Compliance Statement，含 front-matter 閉集（WM.40）、七節固定序論證（WM.41、CS.1）、已知緊張關係節（WM.42、CS.2）、雙向 DEFER 表（WM.43、CS.3）、WM.44 逐條矩陣（CS.4／Annex TR）；自創評價性謂詞判準彙整於 Annex EO（`§8.3` 可判定性元規則）。
5. **對抗審查三鏡俱回報 go、blocking 皆空**：合憲保真（§5 角色四承接、F2/F5/P2.E2、P4.E6/E7/E8、F1–F6 自違、【地位】不自稱生效）、概念層獨立性（`§0.6(b)` 刪名測試）／物理載體下放 Annex LDO／評價性謂詞可判定性（`§8.3`）、Annex TR 矩陣完備性＋WM.40 閉集＋WM.41 七節固定序＋Annex CS 結構完整性，三焦點均通過並實跑 linter 佐證。

---

## 生效要件成就檢核表（DRAFT）

| 要件 | 依據 | 狀態 |
|---|---|---|
| §0.5 Layer 對照表登錄 | `AUGUR-MC v1.3 §0.5` | ✅ 已具備（Layer 5 欄） |
| Constitutional Compliance Statement（正式格式） | `§8.3`／`AUGUR-WM v1.0 §WM.39–45` | ✅ 已具備（Annex CS，非暫行模板） |
| front-matter 閉集 / 七節固定序 / 緊張關係節 / 雙向 DEFER 表 | `§WM.40–43` | ✅ 已具備（CS front-matter／CS.1／CS.2／CS.3） |
| 形式充分性（逐條對應矩陣） | `AUGUR-WM v1.0 §WM.44` | ✅ 已成就（Annex TR 逐條／區塊枚舉，缺 0 條；狀態陳述一致） |
| linter 結構關卡 | `tools.constitution_lint` | ✅ PASS（error 0 / warning 0 / info 1；info 屬骨架級非 error，退出碼 0） |
| 依賴前置（L0–L4 先行生效） | 本裁決依賴序 | ✅ AUGUR-MC v1.3／WM v1.0／ONT v1.0／ID v1.0／KS v1.0 均已生效（AL-2026-001…009；M1 達成） |
| **Steward 充任認定** | `§0.5`／`§8.1`／`§8.6` | ◻ **未成就（DRAFT — 待 Steward 簽署）** |
| **安全關鍵層：§8.2 實質合憲人工簽核** | `§8.2`（本草案主文二） | ◻ **未成就（專屬 Steward，非幕僚／Agent 可代行；為本層完成判準）** |
| Amendment Log 登錄 | `§8.5(c)` | ◻ 未成就（擬 AL-2026-010 保留位；屬 Steward 行為，DRAFT） |

**檢核小結**：形式面（前七列前六者）俱備、linter PASS；**殘餘生效阻卻為第 7–9 列——Steward 充任認定、§8.2 實質合憲人工簽核、Amendment Log 登錄，三者均專屬 Steward 之裁決／簽署行為，本草案不代行、不宣稱成就。**

---

## 依賴序（DRAFT）

* 本規格（Layer 5）為 **L0 → L1 → L2 → L3 → L4 → L5** 承接序之次位執行層交界：上承 `AUGUR-MC v1.3`（L0）、`AUGUR-WM v1.0`（L1）、`AUGUR-ONT v1.0`（L2）、`AUGUR-ID v1.0`（L3）、`AUGUR-KS v1.0`（L4）。
* 上開五上層均已生效（Layer 1–4 於 M1 里程碑全部生效，AL-2026-009）；本規格之上層承接前提**全部成就**。
* 本規格生效後，其全部 [N] 條款對 **Layer 6（Agent Runtime）、Layer 7（External Interface / Infrastructure）** 產生規範效力，並將本層明示下放事項（Annex LDO：物理 model／向量庫／統計庫→L7、Confidence 門檻／風險分級／確認者資格／監督否決→L6、Explanation 呈現→L6/L7、Planning／Human Authority Gate／Action gating→L6）交付其承接。

---

## 殘餘生效阻卻（DRAFT）

1. **Steward 充任認定未成就**——屬 Steward 裁決行為（`§8.1`），非本規格、幕僚或 Agent 單方可成就。
2. **§8.2 實質合憲人工簽核未成就**——安全關鍵層之額外完成判準；推理不變式之實質合憲判斷專屬 Steward，形式充分性不能替代。
3. **Amendment Log 登錄未成就**——登錄為 Steward 於簽署時之行為，本草案僅保留位（AL-2026-010）、不登錄。

---

> **保留**：本草案就 `§WM.44` **形式**充分性陳明已成就狀態；**實質**充分性之最終判斷與 Layer 5（安全關鍵層）之 `§8.2` 實質合憲人工簽核，均**專屬 Constitution Steward**（`AUGUR-MC v1.3 §8.1`、`§8.2`）。**充任認定與 §8.2 實質審查為 Steward 之裁決行為；本文件於 Steward 簽署前不生效力，一切裁決字樣標 DRAFT。** 充任（若簽署）不排除嗣後之違憲審查與修正。

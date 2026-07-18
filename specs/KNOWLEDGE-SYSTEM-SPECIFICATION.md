# 《Augur Knowledge System Specification》

Augur Enterprise AI Operating System
知識系統規格（Layer 4 — Knowledge System）
引用縮寫：**AUGUR-KS**｜版本：**v1.1**（前版：v1.0；minor 修正 RULING-2026-016／AL-2026-019：KS.80 核心宇宙成員資格判準增補款＋KS.81(f) 產業條件豁免維＋TR/DI 承接更正）
受 **AUGUR-MC v1.3** 全文約束（`AUGUR-MC v1.3 §0.6(a)` lex superior、`§0.5` 對照表 Layer 4 欄）
並受 **AUGUR-WM v1.0** 全文約束（`AUGUR-MC v1.3 §0.6(a)`、`AUGUR-WM v1.0 §WM.1`）
並受 **AUGUR-ONT v1.0**（Layer 2）、**AUGUR-ID v1.0**（Layer 3）之下放掛鉤承接約束（`AUGUR-MC v1.3 §0.6(a)`）

---

> ## 【地位】[N]
>
> 本文件為 **v1.0 生效版本**。Constitution Steward（tsaitsangchi）已於 2026-07-17 依 `AUGUR-MC v1.3 §0.5`、`§8.6` 作成**充任認定**（Steward 裁決第 2026-005 號，Amendment Log AL-2026-009）：本文件充任 `AUGUR-MC v1.3 §0.5` 對照表 Layer 4「Knowledge System」欄所轄規格（概念層總綱），`§0.1` 生效要件全部成就（Layer 對照表登錄、Compliance Statement、`§WM.44` 形式充分性成就〔Annex TR 逐條完整枚舉、缺 0 條〕、linter 結構關卡通過、上層 `AUGUR-ONT v1.0`／`AUGUR-ID v1.0` 已先行生效），**自 2026-07-17 起生效**。`v0.1-draft` 原文歸檔於 `specs/KNOWLEDGE-SYSTEM-SPECIFICATION-v0.1-draft.md`；draft → v1.0 之變更僅限：版本欄、本【地位】節生效記錄、Annex CS front-matter spec-version，**無任何 [N] 條款實質變更、條款編號不重排**。
>
> * 本文件全部 [N] 條款自生效日起對 Layer 5–7 規格產生規範效力；下層依 `AUGUR-KS v1.0 §{條款}` 格式引用。落實審計 AUD-03（Confidence 單一形式化語義，Annex CM）／AUD-08（雙時間 as-of）／AUD-02（supersede/tombstone 形式化）。
> * **形式充分性**：Annex TR（TR.A–TR.Z）就四上層（`AUGUR-MC v1.3`／`AUGUR-WM v1.0`／`AUGUR-ONT v1.0`／`AUGUR-ID v1.0`）全部 [N] 條款逐條完整枚舉、缺 0 條（對抗審查查出之 §8.5／§0.1／§0.2／§1.2／§1.3／§7／F1／F2／F3／F6／P1.D／P2.D／P3.D／P5.D 缺列已補正；P#.Y 為 [I] 不計）。
> * **上層承接**：`AUGUR-ONT v1.0`（Layer 2，AL-2026-007）與 `AUGUR-ID v1.0`（Layer 3，AL-2026-008）均已於 2026-07-17 先行生效，本規格對其之承接自即生效；正文對其之版本標注由 v0.1-draft 更新為 v1.0 屬 patch 級編輯（`§8.6`），不影響條款內容。
> * **實質充分性**之最終判斷仍屬 Steward 違憲審查程序（`AUGUR-MC v1.3 §8.2`），與已成就之形式充分性分屬二事；充任認定不排除嗣後之違憲審查。
> * 條款編號穩定性依 `AUGUR-MC v1.3 §8.6`、`AUGUR-WM v1.0 §WM.46`：永不重用、永不重排。
>
> 本【地位】節與 §0 全部約定為 [N] 規範內容，其效力與正文條款同（準用 `AUGUR-WM v1.0 §WM.53`）。
>
> **概念層獨立性提示（`AUGUR-MC v1.3 §0.6(b)`）**：Layer 4 屬**概念層**，本規格全部定義——含 Confidence 之「形式化」、Knowledge 五元組欄位、as-of 能力等級——一律為**概念層形式**，**不得**引用 Layer 5–7 執行層構件（特定資料庫、向量庫、Agent Runtime、AI model、序列化格式、統計庫）為定義依據；物理載體一律下放 Layer 7（Annex DO）。

---

## 目錄 [I]

| § | 標題 | 條款 | 核心錨定 |
|---|---|---|---|
| §0 | Document Status & Conventions | KS.1–KS.5 | `MC §0`、`WM §0`、`WM.39–45` |
| §1 | Purpose, Scope & Layer Position | KS.6–KS.8 | `WM.12`、`WM.30`、`ID §9` |
| §2 | 承接與非管轄（Defers-In & Non-Encroachment） | KS.9–KS.11 | `WM` Annex D、`ONT` DO、`ID` Annex DO |
| §3 | Knowledge 五元組欄位不變式 | KS.20–KS.26 | `MC §P4.E1`（D7） |
| §4 | Confidence 單一形式化語義（核心；解 AUD-03） | KS.30–KS.39 | `MC §P4.E8`、`§2.10`（D9） |
| §5 | 雙時間 as-of 重建能力等級（解 AUD-08） | KS.40–KS.46 | `MC §P4.E2`（D8、D27） |
| §6 | Supersede／Tombstone 與失效語義（解 AUD-02） | KS.50–KS.55 | `MC §P4.E3`（D10、D26） |
| §7 | 矛盾保存（禁 LWW） | KS.60–KS.63 | `MC §P4.E5` |
| §8 | Evidence 分類法、遞迴溯源、信任分級與 NoLaundering | KS.70–KS.79 | `MC §P4.E6`、`§P4.E7`（D10） |
| §9 | Evidence 完備性等級（DEFER 分工） | KS.80–KS.83 | `MC §P5.E2`、`§P5.W3`（D11） |
| §10 | 承接 identity claim 之 Confidence | KS.90–KS.92 | `ID` Annex L4／IDO.1、IDO.2 |
| §11 | 與 Layer 5／6 分界 | KS.100–KS.102 | `MC §P4.E8`、`§P5.E2` |
| §12 | 合規聲明格式承接與存續 | KS.110–KS.111 | `WM.39–45`、`§8.6` |
| Annex CM [N] | Confidence 統一語義映射表（官方映射；解 AUD-03） | CM.0–CM.2 | `§P4.E8` |
| Annex EV [N] | Evidence 分類法與來源信任分級表 | EV.0–EV.3 | `§P4.E6`、`§P4.E7` |
| Annex CL [N] | 完備性等級表 | CL.0–CL.1 | `§P5.E2` |
| Annex DI [N] | 承接上層 DEFER 掛鉤（defers-in） | KDI.0–KDI.17 | `WM` D7–D12/D18/D21/D26/D27；`ID` IDO.1–8 |
| Annex DO [N] | 下放下層 DEFER 掛鉤（defers-out） | KDO.0–KDO.7 | → L5／L6／L7 |
| Annex L3U [N] | 與 Layer 3 之分界表（承接側） | L3U.0 | 與 `ID` Annex L4 同構 |
| Annex L56 [N] | 與 Layer 5／6 之分界表 | L56.0 | reasoning／risk tier |
| Annex TR [N] | WM.44 逐條對應矩陣（憲章＋WM＋ONT＋ID → KS） | — | `WM.44` |
| Annex CS [N] | Constitutional Compliance Statement | CS.1–CS.4 | `WM.39–45` |
| Annex EO [N] | 自創評價性謂詞判準彙整 | EO.1 | `§8.3` 可判定性元規則 |

編號穩定性：正文採 **KS.{n}**（十位制章段保留區塊，空號為保留、非跳號）；Annex 各前綴如上；一經發布永不重用、永不重排（`AUGUR-MC v1.3 §8.6`、`AUGUR-WM v1.0 §WM.46`）。

---

## §0 Document Status & Conventions（文件地位與約定）[N]

### 0.1 名稱、層級與版本 [N]

* 名稱：Augur Knowledge System Specification（下層引用簡稱 **AUGUR-KS**）
* 層級：Layer 4 — Knowledge System（`AUGUR-MC v1.3 §0.5` 對照表第 4 列）
* 版本：v1.0（前版：v0.1-draft）
* 上層規格（upper-specs）：`AUGUR-MC v1.3`（Layer 0）、`AUGUR-WM v1.0`（Layer 1）、`AUGUR-ONT v0.1-draft`（Layer 2，草案）、`AUGUR-ID v0.1-draft`（Layer 3，草案）
* 生效要件：`AUGUR-MC v1.3 §0.5` 對照表登錄（已具欄位）＋ 依 `AUGUR-WM v1.0 §WM.39` 之 Compliance Statement（Annex CS）含 `§WM.44` 逐條矩陣（**已完整枚舉、形式充分性已成就**，見 Annex TR、【地位】）＋ Steward 充任認定（**已成就**，見【地位】）＋ 登錄 Amendment Log（`AUGUR-MC v1.3 §8.1`）——**已全部成就**（Steward 裁決第 2026-005 號，2026-07-17，AL-2026-009）。**生效日：2026-07-17**。實質充分性之最終判斷仍屬 Steward `§8.2` 違憲審查程序，與已成就之形式充分性分屬二事。

### 0.2 規範用語約定 [N]

沿用 `AUGUR-MC v1.3 §0.2`：**必須**（MUST，絕對義務）／**不得**（MUST NOT，絕對禁止）／**應**（SHOULD，偏離須書面說明理由）／**得**（MAY，允許而不構成義務），全文一致，不重定義。

### 0.3 條文效力標注與編號穩定性 [N]

* 每章標題標注 **[N]（Normative，規範性）** 或 **[I]（Informative，資訊性）**。[N] 與 [I] 內容不一致時，依 `AUGUR-MC v1.3 §8.2` 以 Normative 為準。**章標題之標注為該章預設；凡子節另有標注者，以子節標注為該子節之效力準據**；此為標注層級之解讀規則，非上開內容衝突解消規則之適用範圍。
* **正文採十位制章段保留編號**：各章間之空號（如 KS.12–19、KS.27–29、KS.47–49、KS.56–59、KS.64–69、KS.85–89、KS.93–99、KS.103–109 等；KS.84 已啟用承接 GATE 統計治理之 L4 面向）為**保留區塊、非跳號**；保留號之啟用亦適用永不重用、永不重排（`AUGUR-MC v1.3 §8.6`）。
* 正文條款編號採 **KS.{n}**；Annex 條款編號各自前綴：Annex CM（Confidence 映射）採 **CM.{n}**、Annex EV（Evidence 分級）採 **EV.{n}**、Annex CL（完備性）採 **CL.{n}**、Annex DI（承接掛鉤）採 **KDI.{n}**、Annex DO（下放掛鉤）採 **KDO.{n}**、Annex TR（追溯矩陣）採 **TR.{n}**、Annex CS（合規聲明）採 **CS.{n}**、Annex EO（謂詞判準）採 **EO.{n}**；Annex L3U／L56（分界表）以其表首治理條款 **L3U.{n}**／**L56.{n}** 為索引。
* 條款編號一經發布**永不重用、永不重排**；廢止條款保留編號並標注 **(repealed)**（`AUGUR-MC v1.3 §8.6`、`AUGUR-WM v1.0 §WM.46`）。
* **附屬表列 [N] 內容之義務承載規則**：附屬於某治理條款（如 CM.0、EV.0、CL.0、TR.0、KDI.0、KDO.0、L3U.0、L56.0、EO.1）之表列 [N] 內容（如 CM.1 各映射列、EV.1／EV.2 各分級列、TR.A–TR.E 各對應列、CS.1 各節論證），其**義務主體與可判定判準由該治理（父）條款統一承載**，不另於各表列逐列重複標注；此為 KS.5／KS.6「每一 [N] 條款載明義務主體與可判定判準」之體例落實（義務主體＋判準經父條款完整承載），**非**豁免。

### 0.4 權威語言聲明 [N]

本規格以**繁體中文版為權威版本**；規範性術語於正文中一律使用英文原詞（Reality、Observation、Representation、Identity、Evidence、Knowledge、Confidence、Action、Agent、Intelligence；及本層機制術語 Confidence Lattice、Grading Method、Supersede Relation、Conflict Set、Evidence Class、Trust Rank、Completeness Level、As-of Capability Tier、banding、meet、supersede、tombstone、synthetic、self-reported、assumption、provenance、as-of），與 `AUGUR-MC v1.3 §0.4`、`AUGUR-WM v1.0 §0.4`、`AUGUR-ONT v0.1-draft §0.4`、`AUGUR-ID v0.1-draft §0.4` 保持術語同一性；不另立中文譯名為規範對象。

### 0.5 引用格式與元規則 [N]

* 引用格式：`AUGUR-MC v1.3 §{條款}`／`AUGUR-WM v1.0 §{條款}`／`AUGUR-ONT v0.1-draft §{條款}`／`AUGUR-ID v0.1-draft §{條款}`（Layer 2／Layer 3 現為 v0.1-draft，引用時註明其草案地位）。下層引用本規格採 `AUGUR-KS v{version} §{條款}`。
* 本規格每一 [N] 條款標注其**憲章／上層錨定**與**三態型態**：**refines**（細化上位條款）／**carries**（承接上位不變式並給予概念層結構位置）／**hooks**（DEFER 掛鉤，載明目標 Layer 與授權條款），與 `AUGUR-WM v1.0 §0.5`、`AUGUR-ID v0.1-draft §0.5` 三態明文對映一致；複合模式以「＋」連接。每一 [N] 條款並標注**義務主體**與**可判定判準**，使其可機器稽核（承接 `AUGUR-WM v1.0 §WM.34`）。
* **不重定義元規則**：本規格**不得**重新定義 `AUGUR-MC v1.3 §2` 之術語（尤 `§2.6` Knowledge、`§2.5` Evidence、`§2.10` Confidence、`§2.2` Observation），亦**不得**重定義 `AUGUR-WM v1.0`／`AUGUR-ONT v0.1-draft`／`AUGUR-ID v0.1-draft` 之既有構件；本規格僅得就其明示下放者作**語義填充**（`AUGUR-MC v1.3 §2` 元規則、`AUGUR-WM v1.0 §WM.2`、`AUGUR-ID v0.1-draft §ID.0.5`）。
* **概念層獨立性**（`AUGUR-MC v1.3 §0.6(b)`）：本規格屬概念層（Layer 4），**不得**引用 Layer 5–7 執行層構件（資料庫、向量庫、Agent Runtime、API、儲存引擎、序列化格式、統計庫、特定 AI model）作為任何定義之依據。本規格所稱「形式化」「語義」「代數」均為**概念層形式**（論域、序關係、傳播代數、狀態、事件語義之明文可判定性），其執行層落實一律下放（Annex DO）。

### 0.6 §0 條款

> **KS.1（從屬）[N｜carries｜`AUGUR-MC v1.3 §0.6(a)`、`§8.2`；`AUGUR-WM v1.0 §WM.1`]**
> 本規格全部內容從屬並不得違反 `AUGUR-MC v1.3`、`AUGUR-WM v1.0`；牴觸部分無效，經違憲認定之條款自認定日起無效，不得作為 Layer 5–7 規格之依據。
> **義務主體**：本規格自身及其後續修訂者。**可判定判準**：任一條款經 Steward 依 `AUGUR-MC v1.3 §8.2` 認定違憲、或經解釋與 `AUGUR-WM v1.0` 任一 [N] 條款不相容者，即為牴觸；認定前依較嚴格解讀原則處理。

> **KS.2（細化不重定義）[N｜carries｜`AUGUR-MC v1.3 §2` 元規則；`AUGUR-WM v1.0 §WM.2`；`AUGUR-ONT v0.1-draft §ONT.2`]**
> 本規格對 `AUGUR-MC v1.3 §2` 十一初始概念（尤 `§2.6` Knowledge、`§2.5` Evidence、`§2.10` Confidence）及 `AUGUR-WM v1.0`／`AUGUR-ONT v0.1-draft`／`AUGUR-ID v0.1-draft` 既有構件**僅細化，不重定義、不變更內涵、不另創同義歧稱**。本規格新造構件——**Confidence Lattice**（信度格）、**Grading Method**（評定方法）、**Supersede Relation**（失效關係）、**Conflict Set**（衝突集）、**Evidence Class**（證據類別）、**Trust Rank**（來源信任分級）、**Completeness Level**（完備性等級）、**As-of Capability Tier**（as-of 能力等級）——均為上位術語之細化構件，於首次出現處以一句式定義並標注上位錨定，全文採單一名稱（英文原詞加註中文定譯）。
> **義務主體**：本規格自身及其後續修訂者。**可判定判準**：刪除本規格任一定義文句後，不影響 `AUGUR-MC v1.3 §2` 各定義之字面適用者為細化；反之為重定義（禁止）。

> **KS.3（管轄與 DEFER 紀律）[N｜carries｜`AUGUR-MC v1.3 §0.5`；`AUGUR-WM v1.0 §WM.3`]**
> 本規格為 Layer 4 唯一所轄之概念層總綱規格，不自行擴張管轄。凡 `AUGUR-MC v1.3` 明定定義權屬 Layer 5–7 之事項（reasoning 引擎、風險分級表、部署拓撲、物理儲存），本規格**僅得**設 DEFER 掛鉤條款（明載目標 Layer 與授權條款，Annex DO），**不得**代行定義。
> **義務主體**：本規格自身。**可判定判準**：本規格任一條款對 Annex DO 所列 DEFER 事項作成實質定義（即：該定義文句可被下層直接消費而無須下層另為定義）者，違反本條。

> **KS.4（概念層獨立性＋刪名測試＋「形式化」義）[N｜carries｜`AUGUR-MC v1.3 §0.6(b)`；`AUGUR-WM v1.0 §WM.4`]**
> 本規格**不得**引用 Layer 5–7 執行層構件為定義依據；對產品、演算法、庫之提及僅得為 [I] 佐證並通過**刪名測試**（刪去該名後條款概念內涵不變者合法；內涵改變者為定義依據，禁止）。
> **「形式化」義之確立**：本規格所稱 Confidence 之「形式化」（KS.30–KS.39），謂**概念層之單一論域、序關係與傳播代數之明文可判定性**，**非**綁定任何機率演算、統計顯著性框架、評分庫或特定 AI model；數值機率僅得作為映入本論域之一種 Grading Method（CM.1），**非**論域本身。
> **義務主體**：本規格自身、Layer 5–7 規格作者。**可判定判準**：本規格任一定義若刪去某產品／演算法／庫名後概念內涵改變者，違反本條；Confidence 之任一定義若須引特定機率／統計／評分機制方成立者，違反「形式化」為概念層形式之要求。

> **KS.5（文件約定之規範地位）[N｜carries｜`AUGUR-WM v1.0 §WM.53`]**
> 【地位】節與 §0.1–§0.5 之全部約定（生效要件、規範用語等級、條款編號系統、權威語言、條文效力標注、引用格式、元規則）為 [N] 規範內容，其效力與正文條款同。本規格每一 [N] 條款標注憲章／上層錨定＋三態（refines／carries／hooks）＋義務主體＋可判定判準。
> **義務主體**：本規格自身、其後續修訂者及一切消費者。**可判定判準**：各約定之文句字面適用；牴觸各該約定者為文件缺陷，依 `AUGUR-MC v1.3 §8.2` 採較嚴格解讀處理至修正為止。

---

## §1 Purpose, Scope & Layer Position（目的、範圍與分層定位）[N]

### 1.1 Layer 4 定位 [I]

`AUGUR-WM v1.0` 宣告**世界有何物**（存在層）；`AUGUR-ONT v0.1-draft` 宣告**其類屬與同一性判準之內容**（型別層）；`AUGUR-ID v0.1-draft` 負責**個體的永久參照與其一生的機器機制**（個體層）；**本層＝Knowledge 層**：繫結該永久參照之斷言之「信度（Confidence）、欄位（五元組）、失效（supersede／tombstone）、矛盾保存（conflict）、溯源與信任分級（Evidence／Trust Rank）、完備性（Completeness）與 as-of 重建能力」。本層**不鑄造 identifier、不採認判準、不定 lifecycle 機制**（屬 Layer 3）；本層**消費** Layer 3 之已解析 Identity 與 identity claim，為其上覆蓋 Confidence 語義與 Knowledge 欄位（承接 `AUGUR-ID v0.1-draft` Annex L4「Layer 4 專屬」欄）。

### 1.2 條款 [N]

> **KS.6（任務）[N｜refines｜`AUGUR-MC v1.3 §P4`；`AUGUR-WM v1.0 §WM.12`、`§WM.18`、`§WM.30`、`§WM.33`、`§WM.34`]**
> 本規格之任務為：具體化 `AUGUR-MC v1.3 §P4` Evidence Before Conclusion 於 Knowledge 之**語義與治理**——即 Knowledge 五元組欄位（§3）、**Confidence 之單一形式化語義**（§4）、雙時間 as-of 能力等級（§5）、失效與 tombstone（§6）、矛盾保存（§7）、Evidence 分類法與遞迴溯源、信任分級與 NoLaundering（§8）、完備性等級（§9），並承接 Layer 3 identity claim 之 Confidence（§10）。本規格為 `AUGUR-WM v1.0 §WM.12`「不確定性之結構位置（Confidence 之概念槽位）」與 `§WM.33`「標記存續」之**語義填充層**。
> **義務主體**：本規格自身。**可判定判準**：本規格每一 [N] 條款均載明義務主體與可判定判準；缺任一者為文件缺陷，依 `AUGUR-MC v1.3 §8.2` 採較嚴格解讀處理至修正為止。

> **KS.7（Layer 4 定位——四層分工）[N｜carries｜`AUGUR-WM v1.0 §WM.19`；`AUGUR-ID v0.1-draft §ID.1`、Annex L4]**
> 四層分工為：`WM`＝存在層、`ONT`＝型別層、`ID`＝個體層（永久參照與其一生機制）、**本層＝Knowledge 層**（繫結該參照之斷言之信度、欄位、失效、矛盾、溯源與 as-of 重建能力）。本層消費 Layer 3 之已解析 Identity 與 identity claim，為其上覆蓋 Confidence 語義與 Knowledge 欄位。
> **義務主體**：本規格自身。**可判定判準**：本規格任一條款若鑄造 identifier、採認同一性判準、或定義 lifecycle 機制（屬 Layer 3），即為上侵，違反本條。

> **KS.8（上界／下界封印）[N｜carries｜`AUGUR-ID v0.1-draft §ID.70`；`AUGUR-MC v1.3 §P4.E8`、`§P5.E2`]**
> **上界**：本規格**不得**重述 Layer 3 之 identifier／lifecycle／採認機制，僅得引用之。**下界**：本規格**不得**定義 reasoning 推論引擎、hypothesis 生成、風險分級表、核准流程、監督否決度量、物理儲存（屬 Layer 5–7，Annex DO）。
> **義務主體**：本規格自身。**可判定判準**：本規格任一條款對上開任一事項作成可被鄰層直接消費之實質定義者，違反本條（上侵／下侵）。

---

## §2 承接與非管轄（Defers-In & Non-Encroachment）[N]

### 2.1 承接上層掛鉤（defers-in）[N]

> **KS.9（承接盤點）[N｜carries｜`AUGUR-WM v1.0` Annex D D0；`AUGUR-ONT v0.1-draft` Annex DO DO.0；`AUGUR-ID v0.1-draft` Annex DO IDO.0]**
> 本規格於 Annex CS 之 `defers-in` 欄承接下列上層掛鉤，逐一於正文對應：
>
> | 承接來源 | 事項 | 本規格落點 |
> |---|---|---|
> | `AUGUR-WM v1.0 §D7`（`§WM.18` 概念相容） | Knowledge 五元組欄位設計 | §3（KS.20–KS.26） |
> | `AUGUR-WM v1.0 §D8`（`§WM.30`、`§WM.31`） | as-of 重建機制與能力等級（vintage／發布日 gate／embargo／purged） | §5（KS.40–KS.46） |
> | `AUGUR-WM v1.0 §D9`（`§WM.12`、`§WM.18` 僅槽位） | **Confidence 形式化語義、傳播、比較** | §4（KS.30–KS.39） |
> | `AUGUR-WM v1.0 §D10`（`§WM.32`、`§WM.33`） | Evidence 三分類法維護、supersede／tombstone、來源信任分級表 | §6、§8 |
> | `AUGUR-WM v1.0 §D11`（`§WM.28` 引述） | Evidence 完備性等級 | §9（KS.80–KS.83） |
> | `AUGUR-WM v1.0 §D18`（`§WM.14`、`§WM.36`；L4 面向） | Registry 登錄結構（L4 面向）、唯一權威表徵落點 | KS.25、KS.62 |
> | `AUGUR-WM v1.0 §D21`（`§A.10`；`§ONT.41` 散列） | 維度白名單取得機制（Evidence 完整性之通道紀律） | KS.78 |
> | `AUGUR-WM v1.0 §D26`（`§A.22`、`§A.30`） | 重編與同步缺陷之區分、對帳差異分類與處置 | KS.54 |
> | `AUGUR-WM v1.0 §D27`（`§A.29`） | point-in-time 成員資格快照機制 | KS.45 |
> | `AUGUR-ONT v0.1-draft §ONT.2`、`§DO` 散列（Attribute schema、D9 Confidence 不設於 L2） | 屬性 schema 具名欄位集合與欄位設計 | KS.20、§4 |
> | `AUGUR-ID v0.1-draft` IDO.1 | identity claim 之 **Confidence 語義**（形式化、可比較、傳播、門檻） | §4、§10（KS.90） |
> | `AUGUR-ID v0.1-draft` IDO.2 | identity claim 與 lifecycle 事件之 **Knowledge 五元組欄位設計** | §3、§10（KS.91） |
> | `AUGUR-ID v0.1-draft` IDO.3（L4／L7 面向） | lifecycle 事件表欄位／索引之 **L4 概念槽承接**；物理欄位／索引實作、tombstone 儲存落地→L7（ID 原文定性為物理實作，L4 面向限概念槽；概念層五元組欄位承接歸 IDO.2） | KS.26（概念槽）＋KDO.7（物理→L7） |
> | `AUGUR-ID v0.1-draft` IDO.4 | resolution 演算實作（本層讀為 L5 推論，→KDO.1）、未解析存量指標之量測落地與門檻值（完備性輸入→KS.83；量測→KDO.4） | KS.83（＋轉 L5：KDO.1／L5/L7：KDO.4；定性分歧見 T-KS-6） |
> | `AUGUR-ID v0.1-draft` IDO.6 | **as-of 重建引擎與能力等級**、雙時間查詢操作化 | §5（KS.40–KS.46） |
> | `AUGUR-ID v0.1-draft` IDO.8 | 唯一權威 Representation 之實際指定與落點 | KS.25、KS.62 |
>
> **義務主體**：本規格自身。**可判定判準**：上表每列於正文有對應 KS 條款、且於 Annex CS `defers-in` 表雙向可解析者為合規；任一列無對應正文條款者，承接不完整。

### 2.2 非管轄聲明 [N]

> **KS.10（不擴張管轄）[N｜carries｜`AUGUR-MC v1.3 §0.6(a)`、`§0.5`；`AUGUR-WM v1.0 §WM.3`]**
> 本規格為 Layer 4 唯一所轄之概念層總綱規格，不自行擴張管轄；凡屬 Layer 1–3 或 Layer 5–7 之事項，本規格**不得**代行定義。
> **義務主體**：本規格自身。**可判定判準**：本規格任一條款之定義對象逾越 `AUGUR-MC v1.3 §0.5` 所定 Layer 4 職掌者，違反本條。

> **KS.11（DEFER 下放 defers-out）[N｜carries｜`AUGUR-MC v1.3 §0.6(b)`]**
> 本規格下放 Layer 5–7 之掛鉤見 Annex DO（KDO.1–KDO.7）：Confidence 傳播算子之推論引擎實作（L5）、風險分級表與 Confidence 消費門檻／完備性門檻／banding 閾值（L6）、物理儲存與索引與序列化（L7）。
> **義務主體**：本規格自身、目標 Layer 規格作者。**可判定判準**：本表每列與 Annex CS front-matter `defers-out` 欄雙向可解析；本層無任一條款對本表所列事項作成可被下層直接消費之實質定義。

---

## §3 Knowledge 五元組欄位不變式 [N]（`§P4.E1`；解 AUD-03 之五元組第五元缺位）

> 本章行使 `AUGUR-WM v1.0 §D7`／`AUGUR-ID v0.1-draft` IDO.2 下放之 Knowledge 五元組欄位設計權。落實 `AUGUR-MC v1.3 §P4.E1`（不可豁免核心，`§8.4`）。承接審計 **AUD-03**（Knowledge 五元組缺第五元 Confidence）、**AUD-16**（verdict 無 Confidence、claim 裸 anchor 無 Identity 繫結）。

> **KS.20（五概念槽不變式）[N｜refines｜`AUGUR-MC v1.3 §P4.E1`；carries｜`AUGUR-WM v1.0 §WM.18`、`§WM.12`、`§WM.34(a)`；hooks｜物理欄位→L7（KDO.7）]**
> 任一 Knowledge 之承載結構**必須**具備下列**五個概念槽**，各槽為 `AUGUR-MC v1.3 §P4.E1` 最低不變式之欄位化：
>
> ```
> Knowledge
>  ├─ Source        ＝ 斷言主體之已解析 Identity（agent，含版本）＋ 產生活動引用（承 §P4.E6）
>  ├─ Timestamp     ＝ 雙時間對〔valid time 區間，transaction time〕（承 §P4.E2；§5）
>  ├─ Identity      ＝ 繫結對象之已解析 Identity（承 Layer 3）＋ instance/type 標記（承 ONT.30、ID.53）
>  ├─ Evidence      ＝ 遞迴可溯源之 Evidence 引用集合（承 §P4.E6；§8）
>  └─ Confidence    ＝ 取值於 Confidence Lattice L_C 之等級（§4）＋ Grading Method provenance（§P4.E8）
> ```
>
> **缺一即違憲不變式**：任一 Knowledge 承載結構缺任一概念槽者，違反 `AUGUR-MC v1.3 §P4.E1`（屬不可豁免核心，`§8.4`）。**Confidence 槽於過渡期屆滿後為硬義務**：缺 Confidence 槽之 Knowledge 承載結構，於本規格生效（過渡期屆滿，見 KS.38）後即構成 `§P4.E1` 之**結構性違反**（不可豁免核心，`§8.4`），**不得**以下述推定治癒；生效後之常態要求回歸**五槽俱在且各可機器解析**之硬義務。**推定 `INSUF` 僅為 fail-safe 消費規則（解 AUD-03）**：於過渡期（KS.38 所限定之本規格生效前及任何 Confidence 未定之情形）內，Confidence 槽缺載或未填者，依 `§8.3` 保守解釋**推定為 L_C 之底錨 `INSUF`**，且該 Knowledge **不得**被消費為升高信任之依據（**無 Confidence＝不得升高信任**）；此推定為防止缺值被洗白之**消費側 fail-safe**，**非**對生產側略填第五元之許可，其過渡期限定見 KS.38。
> **義務主體**：本規格（表達力）、Layer 5–7 承載構件、一切產生 Knowledge 之模組。**可判定判準**：任一 Knowledge 元素五槽俱在且各可機器解析者合規；缺任一槽者違反本條。

> **KS.21（Source 槽）[N｜refines｜`AUGUR-MC v1.3 §P4.E1`、`§P4.E6`、`§P2.E3`；carries｜`AUGUR-WM v1.0 §WM.33`]**
> Source 槽承載斷言主體之已解析 Identity 與產生活動引用。Agent 自我陳述之 Observation 永久攜 **self-reported 標記**（`§P2.E3`、`§WM.33`）；AI 生成／合成內容永久攜 **synthetic 標記**（`§P4.E7`），不因轉引消失。
> **義務主體**：Layer 5–7 承載構件、一切產生 Knowledge 之模組。**可判定判準**：任一 Knowledge 之 Source 槽可解析至已解析 Identity；self-reported／synthetic 內容之標記於轉引後仍存續者合規（標記滅失依 `§WM.33` 違規）。

> **KS.22（Timestamp 槽——雙時間界面）[N｜carries｜`AUGUR-MC v1.3 §P4.E2`；`AUGUR-WM v1.0 §WM.30`]**
> Timestamp 槽為雙時間對〔valid time 區間，transaction time〕，非單值、非元資料裝飾；valid time 得為區間；transaction time 記錄「系統何時得知」。承接 §5 as-of 能力等級。
> **義務主體**：Layer 5–7 承載構件。**可判定判準**：任一 Knowledge 具二時間軸之獨立槽位者合規；以單一時間值同時充當二軸者違反本條。

> **KS.23（Identity 槽——承接 Layer 3）[N｜carries｜`AUGUR-MC v1.3 §P3.E1`；`AUGUR-ID v0.1-draft §ID.50`、`§ID.53`]**
> Identity 槽必為**已解析** Identity（Layer 3 意義：涉該 Type 判準採認已生效 ∧ provisional 旗標已清除，`AUGUR-ID v0.1-draft §ID.50`）；未解析者不得升級為 Knowledge（`§P3.E1`）。繫結對象攜可解析之 instance／type 標記（承 `§ONT.30`、`§ID.53`）。本層不重定義解析，僅要求槽值為已解析。
> **義務主體**：Layer 5–7 消費者、一切產生 Knowledge 之模組。**可判定判準**：任一 Knowledge 之 Identity 槽為已解析 Identity 且攜可解析 instance／type 標記者合規；繫結 provisional Identity 者違反本條。

> **KS.24（Evidence 槽）[N｜carries｜`AUGUR-MC v1.3 §P4.E1`、`§P4.E6`；`AUGUR-WM v1.0 §WM.27`（`§6 F5`）]**
> Evidence 槽承載遞迴可溯源之 Evidence 引用集合，其分類、溯源、信任、NoLaundering 依 §8。空 Evidence 之 Knowledge 為禁止型態（`§6 F5`；`§WM.27`），於世界模型中無合法表徵位置。
> **義務主體**：Layer 5–7 承載構件。**可判定判準**：任一 Knowledge 之 Evidence 槽非空且其成員可依 §8 遞迴溯源者合規；空 Evidence 之 Knowledge 進入權威表徵層者違反本條。

> **KS.25（Confidence 槽——唯一權威表徵之落實）[N｜refines｜`AUGUR-MC v1.3 §P4.E8`；carries｜`AUGUR-WM v1.0 §WM.14`、`§WM.37`；hooks｜`AUGUR-ID v0.1-draft` IDO.8、`AUGUR-WM v1.0 §D18`]**
> Confidence 槽取值於 L_C（§4）。承接 `§WM.37`／`AUGUR-ID v0.1-draft` IDO.8：本層**指定**每一已註冊世界概念之**唯一權威表徵之落點**（Layer 3 僅提供可被指定之結構前提，`§ID.32`），並於多通道供應時預留 Conflict Set 承載（§7）。此即 `§WM.14` 權威地位唯一之 Layer 4 落實。Registry 登錄結構之 L4 面向（`§WM.36`）由本條承接；其物理載體 DEFER Layer 7（KDO.7）。
> **義務主體**：本規格、Layer 5–7 規格作者。**可判定判準**：每一已註冊世界概念之權威表徵欄恰解析至一落點（`§WM.14` 判準）＋多通道時存在 Conflict Set 承載位置者合規。

> **KS.26（lifecycle 事件與 identity claim 之 Knowledge 欄位承接）[N｜carries｜`AUGUR-ID v0.1-draft` IDO.2、IDO.3、`§ID.31`、`§ID.40`；`AUGUR-MC v1.3 §P4.E1`；hooks｜物理欄位／索引→L7（KDO.7）]**
> Layer 3 之 lifecycle 事件（`§ID.40`）與 identity claim（`§ID.31`）為 Knowledge，其**完整五元組欄位設計由本層 KS.20 承接**；本層定其概念槽與 Confidence 語義（§10），事件表之物理欄位／索引下放 L7（KDO.7）。
> **義務主體**：本規格、Layer 7 規格作者。**可判定判準**：lifecycle 事件與 identity claim 之五元組概念槽可依 KS.20 解析者合規；本層對其物理欄位／索引作實質定義者，下侵違本條。

---

## §4 Confidence 單一形式化語義 [N]（核心；`§P4.E8`；AUD-03 critical 之解）

> 本章行使 `AUGUR-WM v1.0 §D9`／`AUGUR-ID v0.1-draft` IDO.1 下放之 Confidence 語義定義權，落實 `AUGUR-MC v1.3 §P4.E8`（單一形式化定義、全系統可比較、評定方法可追溯、沿推理鏈傳播、Action 允許等級受最低 Confidence 約束）。**憲章未強制數值**（`§2.10`「可量化表述」得為有序類別）。本章為概念層形式，不綁演算法／庫（KS.4）。承接審計 **AUD-03**（全系統無 Confidence、三個互不相通物件）、**AUD-16**（verdict 無 Confidence）。

> **KS.30（單一論域公理）[N｜refines｜`AUGUR-MC v1.3 §P4.E8`、`§2.10`；hooks｜傳播引擎→L5（KDO.1）、消費門檻→L6（KDO.2）]**
> 全系統 Confidence **必須**取值於**唯一**之 **Confidence Lattice L_C**（信度格，取值論域為表達 Knowledge 為真之程度之概念層有界偏序格，為 `AUGUR-MC v1.3 §2.10` Confidence 之細化構件；本規格 Annex CM 定之）。系統內任何表述 Knowledge 為真之程度之物件——校準機率、審議裁決、驗證燈號、對帳結果、信任分級——**必須**映入 L_C，方取得**跨物件可比較性**。
> **義務主體**：本規格、Layer 5–7 一切產生／消費 Confidence 之構件。**可判定判準**：存在任一表述可信度之物件未映入 L_C 者，違反本條（此即 AUD-03「三個互不相通物件」之禁止型態之機器判準）。

> **KS.31（L_C 之形式：有界偏序格）[N｜refines｜`AUGUR-MC v1.3 §P4.E8`、`§P4.E4`；carries｜`§P4.E5`]**
> L_C 為一**有界偏序格**（bounded lattice），其結構：
>
> * **底錨 `INSUF`（insufficient-evidence）**：唯一最小元；映「目前證據不足」為合法且必須可表達之系統狀態（`§P4.E5`）。**與 status 正交**：`INSUF` 為 Confidence 值，`insufficient-evidence`（`§WM.18`）為 status 標記，二者對表但不混同。
> * **核心全序鏈**（由低至高）：`LOW ⊏ MODERATE ⊏ STRONG`。
> * **頂錨 `DETERMINISTIC`（可重放確定性）**：唯一最大元；為「實質等價於確定」之**唯一合法位置**，其賦值**必須**明記其正當性依據＝**可重放之機械驗證**（replayable machine verification）。**解 `§P4.E4` 隱含 1.0 禁令**：`DETERMINISTIC` 不得為任何 Knowledge 之預設值；未明記可重放依據者不得賦 `DETERMINISTIC`；任何 Knowledge 仍可被新 Evidence 推翻（defeasible，直接回指 `§P4.E4`「不得標記為不可修正」），`DETERMINISTIC` 僅表「當前證據下機械可重現」，**非**不可修正、**非**隱含 1.0。
> * **極性（polarity）屬命題層機制，非 L_C 之格維度**：L_C 為**單一論域**（全序鏈為特例之有界偏序格；`§P4.E8` 單一形式化定義、全系統可比較），**不設**第二格軸、無 `Confidence × polarity` 之積格。Confidence 繫附於**命題**；「refuted」＝該命題之 Confidence 降至 `INSUF`，其**否定命題**另承載一高等級 Confidence 之新 Knowledge（`§P4.E5` 裁決結論為新 Knowledge，永不覆寫原始）。refuted 之處理**純屬命題層機制**，不引入 L_C 之額外維度，故 `§P4.E8` 單一可比較性無隙。
>
> **義務主體**：本規格、Layer 5–7 構件。**可判定判準**：任兩 Confidence 值於 L_C 之序（⊑）可判定；賦 `DETERMINISTIC` 而無可重放依據引用者違反本條。

> **KS.32（Grading Method 可追溯）[N｜carries｜`AUGUR-MC v1.3 §P4.E8`（「評定方法可追溯」）、`§P4.E6`]**
> 每一 Confidence 值**必須**攜帶其 **Grading Method**（評定方法，產生該 Confidence 值之具名方法，為 `§P4.E8` 「評定方法」之細化構件）之 provenance 引用：評定方法之標識、輸入、參數與版本（承 `§P4.E6`）。
> **義務主體**：Layer 5–7 一切產生 Confidence 之構件。**可判定判準**：任一 Confidence 值可遞迴解析至其 Grading Method 且該方法可稽核者合規；裸 Confidence 值（無評定方法）違反本條。〔範式承接（AUD-03 鏡頭）[I]：預測軸之 walk-forward IC／Brier／ECE／可靠度分箱／purged 校準器 provenance 為「Grading Method 可追溯」之優秀既有實例，映入 CM.1；此提及通過 KS.4 刪名測試。〕

> **KS.33（數值機率之嵌入——banding）[N｜refines｜`AUGUR-MC v1.3 §P4.E8`；hooks｜帶界閾值→L6（KDO.2）]**
> 校準機率等連續數值**得**作為一種 Grading Method 映入 L_C，其映射為**聲明之單調分箱函數**（monotone banding）：機率帶 → L_C 等級。分箱**必須**攜帶校準 provenance（KS.32）；**具體帶界閾值**為系統狀態／風險門檻，DEFER Layer 6（KDO.2）——本層僅定「單調、可追溯、映入單一 L_C」之不變式，不內嵌具體閾值。
> **義務主體**：本規格、Layer 6 規格作者。**可判定判準**：banding 為單調且其閾值登錄於系統狀態（非規範文本內嵌絕對數值）者合規。此即使「校準 0.8」與序數「STRONG」經同一 L_C 可比之統一移動（解 AUD-03）。

> **KS.34（傳播——NoLaundering 之格代數形式）[N｜refines｜`AUGUR-MC v1.3 §P4.E8`（傳播）、`§P4.E7`（上限）；carries｜`AUGUR-WM v1.0 §WM.34(a)`；hooks｜聚合語義→L5（KDO.1）]**
> Confidence **必須**沿推理鏈向下游傳播。**上限不變式**：任一結論之 Confidence **必須** ⊑ 其前提集合與所據推理規則之 Confidence 之**下確界**（meet，⊓）：
>
> ```
> Conf(結論) ⊑ ⊓{ Conf(前提_i) } ⊓ Conf(推理規則)
> ```
>
> 此為 `§P4.E7` NoLaundering（「結論之 Confidence 上限受證據鏈最弱環節約束」）之格代數落實。**具體聚合語義**（如多獨立證據之增強）DEFER Layer 5（KDO.1），惟其結果**不得逾越**本上限。
> **義務主體**：本規格、Layer 5 規格作者、一切傳播 Confidence 之構件。**可判定判準**：存在任一結論 Conf 嚴格大於其鏈上任一環節 Conf（⋢ 上限）者違反本條，可機器稽核（承 `§WM.34(a)` 引用鏈遍歷）。

> **KS.35（消費——Action 允許等級受最低 Confidence 約束）[N｜refines｜`AUGUR-MC v1.3 §P4.E8`（末句）；hooks｜門檻與風險分級→L6（KDO.2）]**
> Action 之允許等級**必須**受其依據 Knowledge 集合之 Confidence **下確界**約束：依據集合之 ⊓Conf 降低時，Action 允許等級**不得**升高（單調約束）。**Confidence 等級 → Action 允許等級之具體對照門檻**由 Layer 6 風險分級表定義（`§P5.E2`，KDO.2）；本層僅定單調約束與「最低 Confidence 為約束變數」之不變式。
> **義務主體**：本規格、Layer 6 規格作者。**可判定判準**：存在 Action 允許等級隨依據 ⊓Conf 下降而不降者違反本條。

> **KS.36（可謬性與失效之 Confidence 效果）[N｜carries｜`AUGUR-MC v1.3 §P4.E4`、`§P4.E3`]**
> 任一 Confidence 值皆可被新 Evidence 修正；Knowledge 之 supersede／retract／invalidate（§6）**必須**連動重評其 Confidence，且失效事件本身為需 Evidence 之 Knowledge（`§P4.E3`）。**不得**存在標記為「不可修正」之 Confidence。
> **義務主體**：本規格、Layer 5–7 構件。**可判定判準**：任一失效事件連動其被失效 Knowledge 之 Confidence 重評、且無「不可修正」Confidence 者合規。

> **KS.37（官方映射之強制）[N｜refines｜`AUGUR-MC v1.3 §P4.E8`；carries｜`§P4.E6`]**
> 系統既有之類別型／布林型可信狀態**必須**依 Annex CM 官方映射表（其 [N] 規範性內容為 **CM.1(a) 抽象狀態類映射**，不以任一 Layer 5–7 具名構件為定義錨點）映入 L_C；映射表本身依 `§P4.E6` 留 provenance。
> **義務主體**：本規格、Layer 5–7 構件。**可判定判準**：存在既有可信狀態未於 CM 表登錄映射者，聲明不完整；已映射且映射留 provenance 者合規。

> **KS.38（暫行期保守規則）[N｜carries｜`AUGUR-MC v1.3 §8.3`；`AUGUR-WM v1.0 §WM.42`；AUD-03 補正方向]**
> 於本規格生效前之過渡期及任何 Confidence 未定之情形，一律採 `§8.3` 保守解釋：**無 Confidence＝不得升高信任（推定 `INSUF`）**；補償控制為於 Compliance Statement 緊張關係節揭露缺口（`§WM.42`）。
> **義務主體**：Layer 5–7 消費者、本規格。**可判定判準**：Confidence 未定之 Knowledge 被消費為升高信任之依據者違反本條。

> **KS.39（Confidence 非 Reasoning）[N｜carries｜`AUGUR-MC v1.3 §0.6(b)`、`§5` 角色四；hooks｜生成演算→L5（KDO.1）]**
> 本層定 Confidence 之**語義、序、傳播上限與消費約束**；Confidence 之**產生過程**（推論、假設生成、模型評分）屬 Reasoning（Layer 5 World Understanding Engine），DEFER（KDO.1）。
> **義務主體**：本規格、Layer 5 規格作者。**可判定判準**：本層任一條款對 Confidence 之生成演算作實質定義者，下侵違本條。

### Annex CM [N] — Confidence 統一語義映射表（解 AUD-03）

> **CM.0（表之地位與可判定性）[N]** 本表為 `AUGUR-MC v1.3 §P4.E8` 單一形式化語義之官方映射，將系統既有可信狀態映入 L_C。**本表之 [N] 規範性內容為 CM.1(a) 之抽象狀態類映射**——以可判定之**抽象可信狀態類**為映射主體，**不以任一 Layer 5–7 具名構件（特定資料庫欄位、審議 verdict 具名狀態、驗證燈號、對帳工具、知識項型別）為定義錨點**（符 `§0.6(b)`／KS.4）；CM.1(b) 之具名既有構件對照為 **[I] 例示**，通過 KS.4 刪名測試（刪去具名後 CM.1(a) 之抽象狀態類→L_C 映射內涵不變）。表為 [N]，其增修為本規格 minor 升版；每列映射依 `§P4.E6` 留 provenance。**可判定性之界分（解 CM.0 絕對宣稱與 L6 下放之張力）**：CM.1(a) 每列於本層保證**映入單一 L_C 且單調**；**部分列**（如「校準數值機率類」之 banding、「無原生信度類」）之**最終單一等級**取決於 Layer 6 閾值（KDO.2），於本層僅保證映入單一 L_C 且單調，其閾值未定前依保守解釋（KS.38）取底錨 `INSUF`。**Layer 5 審議 verdict 之映入**：本層僅提供 CM.1(a) 之抽象格與映射義務，**不逐狀態釘定** Layer 5 之具名 verdict 至特定 L_C；Layer 5 於其規格承接後，自行將其 verdict 依 CM.1(a) 抽象類映入本層 L_C（`§P4.E8` 之 Layer 分工）。
> **義務主體**：本規格、Layer 5–7 構件。**可判定判準**：CM.1(a) 每列之抽象狀態類→L_C 映射可機器解析、且每列附依據；CM.1(b) 之具名例示刪除後 CM.1(a) 之映射不變（刪名測試）。

> **CM.1(a)（官方映射——抽象狀態類，[N] 規範性）[N]**
>
> | 抽象可信狀態類 | 官方 L_C 映射 | 依據／備註 |
> |---|---|---|
> | **可重放確定類**（具明記可重放機械驗證依據之狀態） | `DETERMINISTIC` | 明記正當性依據＝可重放機械驗證（解 `§P4.E4` 隱含 1.0）；非預設、仍 defeasible |
> | **具獨立 bound Evidence 之裁決確認類** | `STRONG`（受 Trust Rank 天花板約束） | 呈現級→信度級轉譯（AUD-16） |
> | **僅具指涉錨點而無獨立 bound Evidence 之確認類** | `MODERATE` | anchor 指涉但無獨立 bound Evidence |
> | **升級待人類裁決類** | `INSUF`（＋ status: needs-human） | 映底錨；Action 受 `§P5.W2` 人類權威閘 |
> | **命題被否證類**（refuted） | 命題側 `INSUF`；若具否定命題之裁決 Evidence，則否定命題側依裁決 Evidence 映 `STRONG`／`DETERMINISTIC`（雙側處理，適用條件見下註①） | `§P4.E5` 裁決為新 Knowledge，不覆寫原始 |
> | **證據不足／未決類**（pending／undecidable） | `INSUF` | 「證據不足」合法狀態 |
> | **校準數值機率類** | 經 KS.33 單調 banding → `LOW`／`MODERATE`／`STRONG`（帶界閾值 DEFER L6） | Grading Method provenance＝校準來源；最終單一等級取決於 L6 閾值 |
> | **三值驗證類**（通過／告警／未過） | 通過→`STRONG`；告警→`MODERATE`；未過→`INSUF`（適用條件見下註①） | 三值 → L_C 等級 |
> | **值忠實鏡像來源之對帳確認類** | Observation 層 `DETERMINISTIC`（限「值忠實鏡像來源」之範圍，非世界事實真偽） | `§WM.9(a)` 形權威範圍；`§WM.10` |
> | **無原生信度類**（承載結構未填 Confidence 之物件） | 推定 `INSUF`（KS.20／KS.38）；其來源 Trust Rank **僅設定經 Grading Method 賦值後之 L_C 上限（天花板）**，在具備 Grading Method provenance 前不得逕賦高於 `INSUF` 之值 | 末列（無 Confidence→INSUF）對本列賦值具**優先性**（見下註②）；Trust Rank 只約束上限、不構成賦值（符 KS.72／EV.2 天花板語義） |
> | **無 Confidence 之任何 Knowledge** | 推定 `INSUF`（KS.20／KS.38） | `§8.3` 保守解釋；為本表賦值之**優先規則** |
>
> **〔映射適用條件註（[N]，消解 CM.1 之互斥映射）〕**
> * **註①（未過／否證之界分）**：三值驗證「未過」與「命題否證類」於**無否定命題之裁決 Evidence** 時映 `INSUF`（單純證據不足）；於**具否定命題之裁決 Evidence** 時，依雙側處理（命題側 `INSUF`＋否定命題側依裁決 Evidence 映 `STRONG`／`DETERMINISTIC`）。單一輸入決定單一輸出。
> * **註②（無原生信度 vs 無 Confidence 末列之優先）**：二列賦值一致（推定 `INSUF`）；來源 Trust Rank 僅為**天花板**，**非賦值下界**；末列「無 Confidence→INSUF」對「無原生信度類」之賦值具優先性，杜「以無 Confidence 之物件經 TR-B 升至 STRONG」之洗白路徑（符 KS.20「無 Confidence＝不得升高信任」）。

> **CM.1(b)（具名既有構件例示，[I]，通過 KS.4 刪名測試）[I]**
>
> | 具名既有構件（來源，[I]） | 對應之抽象狀態類（CM.1(a)） |
> |---|---|
> | oracle confirmed（`is_deterministic=true`，審議 deterministic replay） | 可重放確定類 |
> | confirmed·bound（審議 confirmed 且具 bound Evidence） | 具獨立 bound Evidence 之裁決確認類 |
> | confirmed·anchor-only | 僅具指涉錨點之確認類 |
> | escalated（升級待人類） | 升級待人類裁決類 |
> | refuted | 命題被否證類 |
> | pending／undecidable | 證據不足／未決類 |
> | 校準機率（Brier／ECE／可靠度分箱，purged 校準器） | 校準數值機率類 |
> | validation green／amber／red | 三值驗證類（通過／告警／未過） |
> | attestation passed（byte-level 對帳） | 值忠實鏡像來源之對帳確認類 |
> | knowledge item／philosophy_principle（無原生信度） | 無原生信度類 |
>
> 〔本 (b) 表為 [I] 例示：刪去任一具名構件後，CM.1(a) 之抽象狀態類→L_C 映射內涵不變（KS.4 刪名測試通過）；具名 verdict 狀態之映入由 Layer 5 於其規格承接 CM.1(a) 後自行為之，本層不下向釘定其語義。〕

> **CM.2（映射之遞迴一致性）[N]** 一物件經 CM.1(a) 映射後之 L_C 值，仍受 §4 傳播上限（KS.34）與 NoLaundering（§8）約束——即映射給定「起點等級」，鏈上傳播不得逾最弱環節。
> **義務主體**：Layer 5–7 構件。**可判定判準**：經 CM 映射之值於鏈上傳播不逾 KS.34 上限者合規。

---

## §5 雙時間 as-of 重建能力等級 [N]（`§P4.E2`；解 AUD-08）

> 本章行使 `AUGUR-WM v1.0 §D8`／`AUGUR-ID v0.1-draft` IDO.6 下放之 as-of 重建機制與能力等級定義權。落實 `AUGUR-MC v1.3 §P4.E2`「重建過去認識狀態之機制與能力等級由 Layer 4 定義」；`AUGUR-WM v1.0` HOOK-01 之 anti-leakage 體系（vintage、發布日 gate、purged／embargo、point-in-time 快照）為上呈素材。承接審計 **AUD-08**（雙時間僅覆蓋 FRED、prediction_values DELETE+INSERT 覆寫、已呈現建議可靜默重寫）。

> **KS.40（雙時間承接）[N｜carries｜`AUGUR-MC v1.3 §P4.E2`；`AUGUR-WM v1.0 §WM.30`、`§WM.31`]**
> 任一 Observation 與 Knowledge 必區分 valid time 與 transaction time；任一過去時刻之認識狀態必須可 as-of 重建且可稽核（不變式）。本層定其**能力等級（As-of Capability Tier）**與**表級分類義務**。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：任一 Observation／Knowledge 承載表具雙時間軸且其 as-of 能力可依 KS.41 分級者合規。

> **KS.41（As-of 能力等級之閉集）[N｜refines｜`AUGUR-MC v1.3 §P4.E2`；hooks｜查詢引擎操作化→L5/L7（KDO.6）]**
> 定義 **As-of Capability Tier**（as-of 能力等級，描述一承載表重建過去認識狀態之能力之有序等級，為 `§P4.E2` 「能力等級」之細化構件），其閉集（由弱至強）：
>
> * **A0（無 as-of）**：不區分雙時間——為**禁止型態**（Knowledge／Observation 不得停留於 A0；解 AUD-08 之 `prediction_values` DELETE+INSERT 覆寫）。
> * **A1（transaction-time append-only）**：記錄 transaction time、append-only、禁物理刪除；可重建「系統何時得知」與「曾出過何結論」。為**認識狀態可稽核之最低要求**。
> * **A2（原生雙時間 bi-temporal）**：valid／transaction 雙軸獨立版本化；任一〔valid, transaction〕座標之認識狀態可 as-of 重建。**凡供 as-of 推理者須 ≥ A2**。
> * **A3（vintage／逐版本 point-in-time）**：歷史值修訂逐版本存真、point-in-time 取版（外部經濟資料庫之逐版本雙時間為範式）；支持任意 as-of 取版與跨版本差異稽核。
>
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：任一承載表之能力可解析至 A0–A3 之一；停留於 A0 之 Knowledge／Observation 承載表違反本條。

> **KS.42（表級能力宣告義務——解 AUD-08 尾句）[N｜refines｜`AUGUR-MC v1.3 §P4.E2` 尾句；carries｜`AUGUR-WM v1.0 §WM.32`]**
> 每一 Knowledge／Observation 承載表**必須**於其登錄宣告其 As-of Capability Tier，並分類為：**(a) 必須原生雙時間者**（原始認識狀態、已對人呈現之建議、風控回讀依據——須 ≥ A2）；**(b) 可重算之衍生快照者**（as-of 能力＝由凍結輸入重算，得為 A1＋重算保證）。此將 `§P4.E2`「機制與能力等級由 Layer 4 定義」落地為**表級分類**（承 AUD-08 補正方向）。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：任一承載表有能力等級宣告且分類為 (a)／(b) 之一者合規；無能力等級宣告者，落入保守解釋（推定不可用於任何 as-of 推理，準 `§WM.31`）。

> **KS.43（已呈現結論之不可靜默重寫）[N｜carries｜`AUGUR-MC v1.3 §P4.E2`、`§P4.E3`；`AUGUR-WM v1.0 §WM.32`]**
> 已對人呈現或已被下游消費之 Knowledge（建議、預測、裁決）**不得**靜默重寫；其變更**必須**表徵為新 transaction-time 版本＋舊版標 superseded（§6），使「任一過去時刻系統實際出過之結論」可 as-of 重建（直接補正 AUD-08）。
> **義務主體**：Layer 5–7 承載構件。**可判定判準**：任一已呈現結論之變更存在新 transaction-time 版本與舊版 superseded 標記者合規；原值遭覆寫且不可 as-of 重建者違反本條。

> **KS.44（可知規則與洩漏防護之承接）[N｜carries｜`AUGUR-WM v1.0 §WM.31`、`§A.35`、`§A.47`；hooks｜gate 實作→L5/L7（KDO.6）]**
> 「只用 as-of ≤ t 已知資訊」為一切回溯評估之判準（`§A.47`）；發布日 gate、purged／embargo、point-in-time 取版為其**實作機制**，DEFER Layer 5/7（KDO.6）；本層定判準與能力等級，不定實作。通道時間屬性雙宣告（`§WM.31`）為 as-of 可用性之前提。
> **義務主體**：本規格、Layer 5/7 規格作者。**可判定判準**：本層未對 gate／purged／embargo 作實質實作定義、且 as-of 判準可被 Layer 5/7 引擎消費者合規。

> **KS.45（point-in-time 快照——承 D27）[N｜carries｜`AUGUR-WM v1.0 §D27`、`§A.29`]**
> 成員資格等 point-in-time 狀態（如核心宇宙成員集）之 as-of 快照機制由本層定其能力等級（須支持任一 as-of 時點成員集可重建），配套 A2/A3；快照之衍生／原生分類依 KS.42。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：任一 point-in-time 狀態之任一 as-of 時點成員集可重建者合規。

> **KS.46（不對稱時間模型之統一 as-of）[N｜refines｜`AUGUR-MC v1.3 §P4.E2`；carries｜`AUGUR-WM v1.0 §A.36`（通道時間模型不對稱之揭露）]**
> 域內存在通道時間模型不對稱（外部經濟庫具 vintage＝A3，本國市場通道以法定公開規則近似可知時刻）。本層之統一 as-of 能力等級為此不對稱之調和層：低能力通道**必須**顯式宣告其等級，消費端 as-of 推理受**最弱通道等級**約束（承 NoLaundering 精神）。
> **義務主體**：本規格、Layer 5–7 消費者。**可判定判準**：跨通道 as-of 查詢之能力等級 ≤ 參與通道之最低等級者合規；逾最低等級消費者違反本條。

---

## §6 Supersede／Tombstone 與失效語義 [N]（`§P4.E3`；解 AUD-02）

> 本章行使 `AUGUR-WM v1.0 §D10`（supersede／tombstone）、`§D26`（重編／對帳）下放權。落實 `AUGUR-MC v1.3 §P4.E3`（只失效不刪除）；形式化 AUD-02 之 `raw_supersede`／`value_mismatch heal` 語義。承接審計 **AUD-02**（raw 層系統性 LWW、原則精華 #6/#7 制度化覆寫、舊值 heal 滅失）、**AUD-09/20/21/22**（衍生物 DELETE 重建家族）。

> **KS.50（只失效不刪除不變式）[N｜carries｜`AUGUR-MC v1.3 §P4.E3`；`AUGUR-WM v1.0 §WM.32`、`§WM.33`]**
> Knowledge 與 Evidence **不得**刪除，僅得標記 **superseded／retracted／invalidated**（三態標記永存，`§WM.33`）；失效為需 Evidence 之知識行為，全歷史保留。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：存在任一使 Knowledge／Evidence 記錄物理消滅之操作路徑者違反本條（法規抹除留痕例外依 KS.53）。

> **KS.51（Supersede Relation 之形式化——解 AUD-02）[N｜refines｜`AUGUR-MC v1.3 §P4.E3`、`§P4.E5`；承接 AUD-02 raw_supersede]**
> 定義 **Supersede Relation**（失效關係，一級物件，表徵一 Knowledge／Evidence 對另一者之失效關係，為 `§P4.E3` 之細化構件），其結構：〔superseding 引用、superseded 引用、失效類型 ∈ {superseded, retracted, invalidated}、失效理由 Evidence、transaction time、作成者 Identity〕。**value_mismatch／heal 覆寫之語義**：來源歷史值被改寫時，**必須**於覆寫前快照舊值並建立 Supersede Relation，舊值以 superseded 存續、不滅失；主路徑 upsert 不動，但矛盾證據共存（§7）。此直接形式化 AUD-02「原則精華 #6/#7 制度化 LWW」之補正。〔範式例示 [I]：heal 前快照舊列（`raw_supersede_log`）為本機制之既有實例；此提及通過 KS.4 刪名測試——刪去具名後，「覆寫前快照舊值＋建立 Supersede Relation」之規範內涵不變。〕
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：任一歷史值變動存在對應 Supersede Relation 且舊值可 as-of 重建者合規；舊值遭覆寫且不可重建者違反本條（`§P4.E5` MUST NOT，不可時限豁免）。

> **KS.52（Supersede DAG 無循環）[N｜carries｜`AUGUR-MC v1.3 §P4.E6`（禁循環）；`AUGUR-WM v1.0 §WM.34(a)`]**
> Supersede Relation 構成有向無環圖（DAG）；**不得**循環失效。任一 Knowledge 之當前有效版本可由 Supersede DAG 於任一 as-of 時點單值解析。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：Supersede 圖無環且任一 as-of 時點當前有效版本單值可解析者合規；存在失效循環者違反本條。

> **KS.53（Tombstone——法規強制抹除例外）[N｜carries｜`AUGUR-MC v1.3 §P4.E3` 例外；hooks｜identity 側→Layer 3（`§ID.42`）、物理→L7（KDO.7）]**
> 法規強制抹除得移除內容本體，但抹除事件自身**必須**留痕並具完整 provenance（作成者、法源引用、生效時點）。Knowledge／Evidence 側 tombstone 語義由本層定；identifier 側去識別化承接 Layer 3（`§ID.42`）；物理落地下放 L7（KDO.7）。tombstone 為存續特例，**不得**用以規避 KS.50。
> **義務主體**：本規格、Layer 3、Layer 7 規格作者。**可判定判準**：任一法規抹除後存在具 provenance 之抹除事件留痕者合規；以 tombstone 規避 KS.50（非法規抹除而消滅記錄）者違反本條。

> **KS.54（重編與對帳差異之處置——承 D26）[N｜refines｜`AUGUR-WM v1.0 §D26`、`§A.22`、`§A.30`、`§A.25`]**
> restatement（重編）為合法世界事件，**必須**表徵為新 Observation 版本（新 transaction time），非資料缺陷、非刪除依據。重編與同步缺陷之區分、對帳差異分類（「系統有、來源無」須調查根因、留痕、不自動刪除，`§A.25`／`§A.43`）由本層定其處置語義。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：任一重編／對帳差異之處置存在留痕與分類者合規；重編以覆寫承載或對帳差異自動刪除者違反本條。

> **KS.55（衍生物 DELETE 重建之禁止）[N｜carries｜`AUGUR-MC v1.3 §P4.E3`；承接 AUD-09/20/21/22 家族]**
> 核心宇宙成員資格、catalog 欄級 provenance 等 Knowledge 級衍生斷言**不得**以全量 DELETE 重建承載（「系統上一版相信哪些屬核心宇宙」須可考）；改為版本化＋supersede。
> **義務主體**：Layer 5–7 承載構件。**可判定判準**：存在對 Knowledge 級衍生表之全量刪除且舊版不可重建者違反本條。

---

## §7 矛盾保存 [N]（`§P4.E5`；禁 LWW）

> 落實 `AUGUR-MC v1.3 §P4.E5`（矛盾保存、禁 last-write-wins），承接 `AUGUR-WM v1.0 §WM.16`（衝突與證據不足之表達力）。

> **KS.60（矛盾保存不變式）[N｜carries｜`AUGUR-MC v1.3 §P4.E5`；`AUGUR-WM v1.0 §WM.16`]**
> 互相衝突之 Evidence／Knowledge **必須**共存並顯式標記 **conflict**（`§WM.33`），**不得**靜默消滅（禁 last-write-wins）。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：存在衝突值之一被無 Supersede Relation 覆寫者違反本條。

> **KS.61（Conflict Set 之形式化）[N｜refines｜`AUGUR-MC v1.3 §P4.E5`；carries｜`AUGUR-WM v1.0 §WM.16`]**
> 定義 **Conflict Set**（衝突集，一級物件，同一世界事實之相異值集合，為 `§P4.E5` 之細化構件）：各成員攜自身 Evidence 與 Confidence（§4）、conflict 標記。「目前證據不足」（映 L_C `INSUF`）為合法且必須可表達之一級狀態（正交於 status，KS.31）。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：同一世界事實之相異值可承載為 Conflict Set、各成員攜自身 Evidence／Confidence 者合規。

> **KS.62（衝突裁決為新 Knowledge）[N｜carries｜`AUGUR-MC v1.3 §P4.E5`；`AUGUR-WM v1.0 §WM.14`、`§WM.37`；`AUGUR-ID v0.1-draft` IDO.8]**
> 衝突之裁決為推理行為，其結論為**攜自身 Evidence 與 Confidence 之新 Knowledge**，引用 Conflict Set 為 Evidence，**永不覆寫原始證據**。裁決結論落於該世界概念之唯一權威表徵（KS.25／`§WM.37`）；原始衝突成員以 conflict 存續。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：裁決 Knowledge 存在且原始成員未滅失者合規；裁決覆寫原始證據者違反本條。

> **KS.63（多通道一對多映射之衝突承載）[N｜carries｜`AUGUR-WM v1.0 §WM.14`、`§WM.15`；`AUGUR-MC v1.3 §P4.E5`]**
> 「世界事實→來源 Observation」一對多映射為必備結構；多通道值相異時登錄 Conflict Set，權威值裁決依 KS.62。同一性宣告依 `§WM.15`（無宣告即非同一）。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：多通道相異值存在 Conflict Set 承載且同一性以宣告為準者合規。

---

## §8 Evidence 分類法、遞迴溯源、信任分級與 NoLaundering [N]（`§P4.E6`／`§P4.E7`）

> 本章行使 `AUGUR-WM v1.0 §D10` 下放之 Evidence 三分類法維護、來源信任分級表定義權。落實 `AUGUR-MC v1.3 §P4.E6`（遞迴溯源）、`§P4.E7`（NoLaundering）。承接審計 **AUD-16**（審議通道 Evidence 強度未分級、claim 裸 anchor）。

> **KS.70（Evidence 為一級物件、遞迴溯源）[N｜carries｜`AUGUR-MC v1.3 §P4.E6`；`AUGUR-WM v1.0 §WM.34(a)`]**
> Evidence 為一級物件，自身可溯源：記錄斷言主體（agent，含版本）、產生活動（含輸入與參數）、上游依據。證據鏈**必須**遞迴終止於對 Reality 之 Observation 或明示宣告之假設（assumption 標記，`§WM.33`）。**禁循環引證**（DAG）。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：任一 Evidence 節點存在有限步可遍歷之引用路徑終止於 Observation／assumption、無循環者合規（承 `§WM.34(a)` 機器可稽核）。

> **KS.71（Evidence 三分類法）[N｜refines｜`AUGUR-MC v1.3 §P4.W1`；carries｜維護權屬 Layer 4]**
> 定義 **Evidence Class**（證據類別，維護權屬本層）：**Data Evidence**（如 ERP record、Sensor measurement、byte-attested 官方來源）、**Knowledge Evidence**（如 Paper、Specification）、**Computational Evidence**（如 Model output、Simulation）；另 **assumption**（明示宣告假設）為遞迴終點類。分類為開放列舉：得增列、不得使既有失去承載位置。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：任一 Evidence 可歸類至上開類別之一（或 assumption）且既有類別不失承載位置者合規。

> **KS.72（來源信任分級表 Trust Rank）[N｜refines｜`AUGUR-MC v1.3 §P4.E7`；Annex EV]**
> 定義 **Trust Rank**（來源信任分級，Annex EV，由高至低之有序信任等級）：每一 Evidence 類別／來源型態映一 Trust Rank。Trust Rank **約束** Confidence 上限（映入 L_C 之天花板）。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：任一 Evidence 之來源可映至 Annex EV 之 Trust Rank 者合規。

> **KS.73（NoLaundering——信任不可洗白）[N｜carries｜`AUGUR-MC v1.3 §P4.E7`；refines｜KS.34]**
> 衍生證據之信任**不得**高於其上游最弱來源；結論之 Confidence 上限受證據鏈最弱環節約束（格代數形式見 KS.34）。
> **義務主體**：本規格、Layer 5–7 構件。**可判定判準**：存在衍生 Evidence 之 Trust Rank 高於其任一上游者違反本條。

> **KS.74（synthetic 標記永久性）[N｜carries｜`AUGUR-MC v1.3 §P4.E7`；`AUGUR-WM v1.0 §WM.33`]**
> AI 生成／合成內容永久攜 synthetic 標記，不因轉引消失；synthetic 之 Trust Rank 有天花板約束（不得逕映高等級 Confidence）。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：synthetic 內容於轉引後仍攜標記、且其映入 L_C 之值不逾 Annex EV 之 synthetic 天花板者合規。

> **KS.75（獨立性判準）[N｜refines｜`AUGUR-MC v1.3 §P4.E7`「獨立」；carries｜`§8.3` 可判定性元規則]**
> 「獨立 Data Evidence」之可判定判準：該 Data Evidence 之 provenance 鏈**遞迴不含本系統之 Computational Evidence**，**且**不與待證結論共享上游來源。此為 `§8.3` 可判定性元規則對「獨立」之落實（收錄 Annex EO）。
> **義務主體**：本規格、Layer 5–7 構件。**可判定判準**：一 Data Evidence 之 provenance 鏈遞迴不含本系統 Computational Evidence ∧ 不與待證結論共享上游者為獨立；否則非獨立。

> **KS.76（高風險 Action 之證據要求）[N｜carries｜`AUGUR-MC v1.3 §P4.E7`；hooks｜風險認定→L6（KDO.2）]**
> 高風險 Action 之結論**不得**僅以系統自身產出（Computational Evidence／self-reported）為據，須至少一項獨立 Data Evidence（KS.75）或人類確認（以確認者已解析 Identity 為 Source、留痕為 Observation）。「高風險」之認定依 Layer 6 風險分級表（`§P5.E2`，KDO.2）；本層定證據要求之結構，不定風險分級。
> **義務主體**：本規格、Layer 6 規格作者、Layer 5–7 構件。**可判定判準**：高風險 Action 結論具至少一項獨立 Data Evidence 或合格人類確認者合規；僅以系統自身產出為據者違反本條。

> **KS.77（self-reported 不得單獨升信）[N｜carries｜`AUGUR-MC v1.3 §P2.E3`、`§P4.E7`]**
> Agent execution receipt 等 self-reported Observation 僅屬宣稱性 Observation，其升級為 Knowledge 受 KS.76 約束；**不得**僅以系統自身產出升高 Confidence。
> **義務主體**：Layer 5–7 構件。**可判定判準**：self-reported Observation 單獨升高 Confidence 而無獨立 Data Evidence 或人類確認者違反本條。

> **KS.78（通道白名單為完整性紀律——承 D21）[N｜carries｜`AUGUR-WM v1.0 §D21`、`§A.10`、`§ONT.41`；`AUGUR-MC v1.3 §P4.W1`]**
> 世界量維度白名單之取得（來源動態列舉→官方文檔種子→名冊）為 Evidence 完整性之通道紀律：維度值臆測禁止（無白名單依據之維度值為無 Evidence 之斷言，違 `§P4.W1`）。
> **義務主體**：本規格、Layer 5–7 攝取構件。**可判定判準**：任一世界量維度值可溯至白名單依據者合規；白名單外臆測維度值者違反本條。

> **KS.79（審議通道之 Evidence 強度分級——解 AUD-16）[N｜refines｜`AUGUR-MC v1.3 §P4.E1`、`§P4.E6`；承接 AUD-16；carries｜`AUGUR-ID v0.1-draft §ID.53`]**
> 審議 verdict 之 Evidence **必須**可區分強度並映入 Trust Rank／Confidence（CM.1）；verdict 之 Confidence 槽由 §4 承接（補正 AUD-16 之 verdict 無 Confidence）。〔強度差異之例示 [I]：如「結構存在性證明」強於「單行文字匹配」（既有實例：information_schema 存在性證明 vs file_grep 單行匹配）；此提及通過 KS.4 刪名測試——刪去具名後，「verdict Evidence 強度須可映入 Trust Rank」之規範內涵不變。〕claim 之結構化指涉須繫結已解析 Identity（承 Layer 3，非裸 anchor 字串），使 confirmed claim 升格消費時符合五元組（KS.20）。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：任一 verdict 具 Confidence 槽且其 Evidence 強度可映入 Trust Rank、claim 指涉繫結已解析 Identity 者合規；verdict 無 Confidence 或 claim 以裸字串指涉者違反本條。

### Annex EV [N] — Evidence 分類法與來源信任分級表

> **EV.0（表之地位）[N]** 本表維護 Evidence 三分類與 Trust Rank，為 [N]，增修為 minor 升版；每一分級附可判定判準。
> **義務主體**：本規格、Layer 5–7 構件。**可判定判準**：EV.1／EV.2 每列可機器解析且附判準。

> **EV.1（分類法）[N]** Data／Knowledge／Computational Evidence＋assumption（如 KS.71），各附界定判準與範例（範例為 [I]，通過刪名測試）。

> **EV.2（Trust Rank 序）[N]** Trust Rank 序集（`TR-A ⊐ TR-B ⊐ TR-C ⊐ TR-D ⊐ TR-⊥`）及各級之 L_C 天花板為**規範性閉集**，為 KS.74／EV.3 之可判定錨點；下表僅「**具體門檻數值**」DEFER Layer 6（KDO.2），序集與各級 L_C 天花板本身**非**示意、不因下放而失位。
>
> | Trust Rank | 典型來源 | Confidence 上限（映 L_C） | 判準 |
> |---|---|---|---|
> | **TR-A** | 獨立 Data Evidence、byte-attested 官方來源、可重放機械驗證 | 至 `DETERMINISTIC`（須明記依據） | KS.75 獨立性成立 |
> | **TR-B** | 非獨立 Data Evidence、Knowledge Evidence（同儕審查文獻） | 至 `STRONG` | 具可溯源出處 |
> | **TR-C** | Computational Evidence（校準模型輸出） | 至 `MODERATE`（校準 provenance） | KS.32 Grading Method 可追溯 |
> | **TR-D** | self-reported、synthetic、單行匹配 | 至 `LOW` | 永久標記；不得單獨升信 |
> | **TR-⊥** | 無來源、循環引證、白名單外臆測 | `INSUF` | 禁止升格消費 |

> **EV.3（NoLaundering 約束）[N]** 衍生 Evidence 之 Trust Rank ⊑ 上游最弱（KS.73）；Confidence 傳播上限受 Trust Rank 天花板與 KS.34 meet 之雙重約束。
> **義務主體**：Layer 5–7 構件。**可判定判準**：衍生 Evidence 之 Trust Rank 不高於上游最弱、且其映入 L_C 之值不逾 KS.34 上限者合規。

---

## §9 Evidence 完備性等級 [N]（`§P5.E2` 所引；DEFER 與 L6 之分工）

> 本章行使 `AUGUR-WM v1.0 §D11` 下放之 Evidence 完備性等級定義權。`AUGUR-MC v1.3 §P5.E2`／`§P5.W3` 之風險分級表以完備性等級為認定依據；本層定**完備性等級本身**，Layer 6 定**各風險級對應之完備性門檻**。

> **KS.80（完備性等級之定義權界分）[N｜refines｜`AUGUR-MC v1.3 §P5.E2`（完備性等級由 Layer 4 定義）；hooks｜門檻→L6（KDO.2）]**
> 定義 **Completeness Level**（完備性等級，描述一 Knowledge／結論之證據完備程度之有序等級，為 `§P5.E2` 「完備性等級」之細化構件）。本層定等級語義；**各風險級須達之完備性門檻、Confidence 門檻、核准流程**由 Layer 6 風險分級表定義（`§P5.E2`，KDO.2）。
> **核心宇宙成員資格判準（承 `AUGUR-WM v1.0 §D22`、`§A.14`）**：核心宇宙（模型消費之成員集）之成員資格判準**必須**為資料品質之函數、**不得**含投資價值面因素（`§A.14` 判準定位）；其判準結構為 (i) **完整性 gate**——成員須達以 KS.81 維度可盤點之資料完整性要求；(ii) **流動性分位地板**——以分位表述之流動性下限，本層定其量測口徑與分位基準之結構，具體分位值與 gate 門檻值為 operational 層參數（`§A.48`：於 operational 層合法且須透明揭露），其採認與變更核准 DEFER Layer 6；(iii) **產業條件豁免**（KS.81(f)）。成員資格斷言為 Knowledge 級衍生斷言，受 KS.20／KS.45／KS.55 既有約束；判準之計算實作屬 Layer 5 inference（比照 KS.83(ii) 體例），本層不定演算。**可判定判準**：成員資格判準含任一投資價值面因素、或 gate／地板／豁免不可解析至本款結構者，違反本條。
> **義務主體**：本規格、Layer 6 規格作者。**可判定判準**：本層對「哪一風險級需哪一完備性」作實質定義者，下侵違本條。

> **KS.81（完備性維度）[N｜refines｜`AUGUR-MC v1.3 §P5.E2`、`§P5.W3`；Annex CL]**
> 完備性等級由下列可判定維度合成（Annex CL）：(a) 證據鏈是否完整終止於 Observation／assumption（`§P4.E6`）；(b) 是否含至少一項獨立 Data Evidence（KS.75）；(c) 是否含未解假設（assumption 標記數）；(d) 是否經樣本外／可重現驗證（Grading Method provenance），含預註冊判準凍結與多重比較調整之踐行（KS.84）；(e) 是否存在未裁決之 Conflict Set（§7）；(f) **產業條件豁免（承 `§D22`、`§A.12`）**：某產業板塊制度性缺某類資料者（如金融保險業無月營收申報制度），該缺位為世界結構事實，**不得**計為 (a)–(e) 之完備性缺陷或完整性 gate 之未達；豁免以『產業分類×資料類』為粒度，其依據（制度性缺位事實）本身為須具 Evidence 之 Knowledge（`§P4.W1`）；豁免之授予、存續審查與撤銷之核准 DEFER Layer 6。
> **義務主體**：本規格、Layer 5–7 構件。**可判定判準**：每一維度可機器盤點者合規。

> **KS.82（完備性與不可逆性成正比之承接）[N｜carries｜`AUGUR-MC v1.3 §P5.W3`；hooks｜綁定→L6（KDO.2）]**
> `§P5.W3`「不可逆或高影響 Action 需最高等級 Evidence 完備性」：本層提供完備性等級之量尺，其與風險級之綁定 DEFER Layer 6。缺位預設規則（分級表生效前實體世界 Action 一律最高風險、人類事前逐案核准，`§P5.E2`）為憲章直接效力，本層引述不削弱。
> **義務主體**：本規格、Layer 6 規格作者。**可判定判準**：本層未對完備性與風險級之綁定作實質定義、且缺位預設引述未削弱者合規。

> **KS.83（完備性量測落地承接 IDO.4）[N｜hooks｜`AUGUR-ID v0.1-draft` IDO.4；目標 L4 概念＋L5 推論（KDO.1）＋L5/L7 量測（KDO.4）]**
> `AUGUR-ID v0.1-draft` IDO.4 含二事項，本層**分別**處置，不得靜默丟失任一半：
> * **(i) 未解析存量指標量測**：未解析存量、解析時效、顯式待決同一性存量（`§ID.51`）為完備性之個體層輸入指標；本層定其於完備性等級之**納入語義**，量測落地 DEFER（KDO.4）。
> * **(ii) resolution 演算實作**：相似度／比對／批次流程之解析演算屬 Layer 5 Cognitive Kernel 之 **inference**（`AUGUR-MC v1.3 §5` 角色四、KS.100）——為推論產生過程，非 Knowledge 之信度／欄位語義；本層**不定義**，明記 DEFER Layer 5（KDO.1）並附理由。`AUGUR-ID v0.1-draft` IDO.4 將二事項均標為目標 L4；本層就 (ii) 讀為 Layer 5 Reasoning 之落點（KS.100），此定性分歧列為緊張關係 **T-KS-6**（CS.2）。
> **義務主體**：本規格、Layer 5/7 規格作者。**可判定判準**：`§ID.51` 三指標於完備性等級之納入語義存在、本層未對其量測門檻值作實質定義、且 resolution 演算實作明記 DEFER（KDO.1）而本層未對其作實質定義者合規。

> **KS.84（GATE 統計治理之 Layer 4 Evidence 機制承接——承 WM-D12／HOOK-03）[N｜carries｜`AUGUR-WM v1.0 §D12`、HOOK-03、`§A.19`、`§A.52`；refines｜`AUGUR-MC v1.3 §P4.E6`、`§P4.E7`；hooks｜統計計算實作→L5（KDO.3）]**
> 預註冊可證偽實驗（GATE）之統計治理，依 `AUGUR-WM v1.0` HOOK-03 明定為**Layer 4 Evidence 機制設計權**（「統計嚴謹化屬 Layer 4 Evidence 機制設計權」）；本層承接其**概念層**面向，落地為對既有機制之約束：
> * **(a) 多重比較調整**（家族錯誤率控制）為 **Grading Method provenance 之一維**（KS.32）：未經多重比較調整之顯著性，**不得**逕映高等級 Confidence（`§P4.E7` 上限精神）。
> * **(b) 判準凍結**（預註冊判準之 as-of 凍結）為 **as-of 紀律（§5）與完備性維度（KS.81(d)）之約束**：事後改動判準即降其完備性等級，不得以事後判準冒充預註冊。
> * **(c) 二次證偽封鎖**為 **supersede 語義之特例**（KS.51）：已封鎖之證偽路徑不得以新一輪重跑靜默覆寫，須表徵為 Supersede Relation（舊路徑以 superseded 存續）。
>
> **具體統計計算實作**（家族錯誤率演算、批次流程）DEFER Layer 5（KDO.3）；本層僅定其對 Grading Method／完備性／supersede 之概念層約束，不定演算。
> **義務主體**：本規格、Layer 5 規格作者、一切產生 GATE Evidence 之構件。**可判定判準**：GATE verdict 之 Grading Method 載明多重比較調整、其判準凍結 as-of 可稽核、二次證偽以 Supersede Relation 表徵者合規；未調整多重比較而逕映高 Confidence、或事後改判準而不降完備性、或二次證偽靜默覆寫者違反本條。

### Annex CL [N] — 完備性等級表

> **CL.0（等級閉集）[N]** 完備性等級為**規範性閉集**（比照 KS.41 As-of Tier A0–A3 體例，無 hedge），由弱至強：`E0`（無溯源／循環／白名單外）＜`E1`（溯源完整但無獨立 Data Evidence）＜`E2`（含獨立 Data Evidence）＜`E3`（獨立 Data Evidence＋OOS 驗證＋無未裁決衝突）。各級對映維度（KS.81）之可判定組合。此閉集為 `§P5.E2` 下游 Layer 6 風險門檻認定之固定可判斷錨點；**各風險級之門檻對照 DEFER Layer 6（KDO.2）**，惟等級集本身不因下放而失位。
> **義務主體**：本規格、Layer 6 規格作者。**可判定判準**：任一 Knowledge 之完備性可依 KS.81 維度盤點並歸至 E0–E3 之一者合規；本表對風險級門檻作實質定義者，下侵違本條。

> **CL.1（等級之遞迴一致性）[N]** 一 Knowledge 之完備性等級受其證據鏈最弱環節約束（承 NoLaundering，KS.73）；衍生結論之完備性不高於其前提集合之最低完備性。
> **義務主體**：Layer 5–7 構件。**可判定判準**：衍生結論完備性不高於前提最低完備性者合規。

---

## §10 承接 identity claim 之 Confidence [N]（`AUGUR-ID v0.1-draft` Annex L4／IDO.1、IDO.2）

> **KS.90（identity claim Confidence 語義填充）[N｜carries｜`AUGUR-ID v0.1-draft` IDO.1、`§ID.30(d)`；`AUGUR-MC v1.3 §P4.E8`]**
> Layer 3 identity claim（`§ID.30`）之 **Confidence 槽位**之語義由本層填充：其取值於 L_C（§4）、比較與傳播同 §4、Grading Method 可追溯（KS.32）。承接 `AUGUR-ID v0.1-draft` T-ID-1 緊張關係之解消（claim Confidence 語義 DEFER Layer 4）。
> **義務主體**：本規格、Layer 5–7 消費者。**可判定判準**：任一 identity claim 之 Confidence 可映入 L_C 且攜 Grading Method 者合規。

> **KS.91（identity claim 完整五元組承接）[N｜carries｜`AUGUR-ID v0.1-draft` IDO.2、`§ID.31`；`AUGUR-MC v1.3 §P4.E1`、`§P4.E5`]**
> identity claim 為 Knowledge，其完整 Knowledge 五元組欄位設計由本層 §3（KS.20）承接；衝突之 claim（二來源對同一 identifier 對相反斷言）共存並顯式標記（§7，禁 LWW）。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：identity claim 之五元組概念槽可依 KS.20 解析、且衝突 claim 共存者合規。

> **KS.92（identity resolution 狀態之 Confidence 映射）[N｜refines｜CM.1；`AUGUR-ID v0.1-draft §ID.50`、`§7`]**
> identity resolution 之各狀態（已解析／provisional／顯式待決）映入 L_C：**已解析者**其 Confidence 依該 identity claim 之 Evidence／Grading Method 依 §4 個案評定，並受 KS.34 傳播上限與 Annex EV Trust Rank 天花板（KS.72）約束——**已解析僅解除「不得升級 Knowledge」之閘，不逕賦固定 Confidence 下限**（已解析未必即具中度以上信度）；**provisional／顯式待決**＝`INSUF`（不得升級 Knowledge，`§ID.50`）。「已解析須達某完備性方得消費」如有需求，屬完備性等級（§9）與風險級之綁定，DEFER Layer 6（KDO.2），本層不於 L_C 逕釘 Confidence 下限。
> **義務主體**：本規格、Layer 5–7 消費者。**可判定判準**：provisional／待決之 claim 被賦高於 `INSUF` 之 Confidence 而升格消費者違反本條；已解析 claim 之 Confidence 逾 KS.34 傳播上限或 Annex EV Trust Rank 天花板者違反本條。

---

## §11 與 Layer 5／6 分界 [N]

> **KS.100（Layer 5 專屬——reasoning）[N｜carries｜`AUGUR-MC v1.3 §5` 角色四、`§0.6(b)`；Annex L56]**
> 下列屬 Layer 5 Cognitive Kernel，本層僅設掛鉤：Reasoning／Inference／Hypothesis／Explanation 之引擎、Confidence **傳播算子之具體聚合語義與推論實作**（KS.34 之 runtime）、外部知識入 World Representation 之確立工作流（`AUGUR-WM v1.0` HOOK-02）。本層定 Confidence 之上限代數與消費約束，不定其生成推論。
> **義務主體**：本規格、Layer 5 規格作者。**可判定判準**：本層對推論引擎作實質定義者，下侵違本條。

> **KS.101（Layer 6 專屬——risk tier）[N｜carries｜`AUGUR-MC v1.3 §P5.E2`；Annex L56]**
> 下列屬 Layer 6 Agent Runtime：風險分級表、各級 Evidence 完備性門檻與 Confidence 消費門檻（KS.35、KS.80 之門檻值）、核准流程、確認者資格與獨立性、監督否決度量。本層定完備性等級與 Confidence 語義之量尺，Layer 6 定其與風險級之綁定。
> **義務主體**：本規格、Layer 6 規格作者。**可判定判準**：本層對風險分級或門檻值作實質定義者，下侵違本條。

> **KS.102（分界表）[N｜carries｜`AUGUR-MC v1.3 §5`；`AUGUR-WM v1.0 §WM.29`（fail-safe，`§D15`）]**
> 逐項分界見 Annex L56（「本層得為」欄與「Layer 5/6 專屬」欄無交集）。fail-safe 判定主體與程序（`§WM.29`／`§D15`）非本層獨占，分屬 L4–L6，本層僅提供完備性與失效之表達力承載，不定判定主體。
> **義務主體**：本規格、Layer 5/6 規格作者。**可判定判準**：Annex L56 兩欄無交集，且本層任一條款不落入「Layer 5/6 專屬」欄。

### Annex L56 [N] — 與 Layer 5／6 分界表（示意）

> **L56.0（分界判準）[N]**
>
> | 面向 | 本層得為（Layer 4 專屬） | Layer 5／6 專屬 |
> |---|---|---|
> | Confidence | 單一論域 L_C、序、傳播上限代數、消費單調約束、官方映射 | 傳播聚合之推論實作（L5）、消費門檻值／風險綁定（L6） |
> | Evidence | 分類法、遞迴溯源結構、Trust Rank、NoLaundering、獨立性判準 | 假設生成／推論產生 Evidence（L5）、確認者資格（L6） |
> | 完備性 | 完備性等級量尺與維度 | 各風險級之完備性門檻（L6） |
> | as-of | 雙時間能力等級、表級分類 | gate／purged 實作（L5/L7）、風險級 as-of 要求（L6） |
> | 失效／矛盾 | supersede／tombstone／conflict 語義 | fail-safe 判定主體與程序（L4–L6，`§WM.29`／D15） |
>
> **義務主體**：本規格、Layer 5/6 規格作者。**可判定判準**：右欄事項不出現於本規格任一 [N] 條款之實質定義中。

---

## §12 Constitutional Compliance Statement Format 承接與存續 [N]

> **KS.110（格式承接）[N｜carries｜`AUGUR-WM v1.0 §WM.39–45`；`AUGUR-MC v1.3 §8.3`]**
> 本規格之 Constitutional Compliance Statement 依 `AUGUR-WM v1.0 §WM.39–45` **正式格式**作成（見 **Annex CS**），**非**暫行模板（作成於 Layer 1 生效日 2026-07-16 後，`§WM.45`）。無有效聲明使本規格不生效力。front-matter 欄位、七節論證、緊張關係節、雙向 DEFER 表、**WM.44 逐條矩陣**俱全為機器可判生效要件。
> **義務主體**：本規格自身、Steward。**可判定判準**：Annex CS 之 front-matter 欄位、七節論證、緊張關係節、雙向 DEFER 表俱全（`§WM.40–44`），且 Annex TR 逐條矩陣完備。

> **KS.111（存續與升版）[N｜carries｜`AUGUR-MC v1.3 §8.6`；`AUGUR-WM v1.0 §WM.46–47`]**
> 條款編號永不重用、永不重排；`AUGUR-MC`／`AUGUR-WM`／`AUGUR-ONT`／`AUGUR-ID` major 升版時進入重新認證期。全部「不得」（MUST NOT）義務不得豁免（`§8.4`）；尤 KS.50／KS.51（`§P4.E3`／`§P4.E5` MUST NOT）不可時限豁免。
> **義務主體**：本規格、Steward。**可判定判準**：升版時 Annex CS 之 `mc-version`／`upper-specs` 欄同步；版本間 diff 檢查——任一既發布編號於後版消失或改指他文者違反本條。

---

## Annex DI [N] — 承接上層 DEFER 掛鉤（defers-in）

> **KDI.0（承接義務）[N]** 本表每列為規範性承接掛鉤：本層明示承接上層明示下放之事項，並於正文對應落點填充之；本表每列與 Annex CS front-matter `defers-in` 欄雙向可解析。
> **義務主體**：本規格自身。**可判定判準**：本表每列於正文有對應 KS 條款且與 front-matter 雙向可解析者合規。

| 掛鉤 | 本規格落點 | 承接事項 | 來源／授權 |
|---|---|---|---|
| **KDI.1**（WM-D7） | §3 | Knowledge 五元組欄位 | `AUGUR-WM v1.0 §D7`／`§P4.E1` |
| **KDI.2**（WM-D8） | §5 | as-of 重建機制與能力等級 | `AUGUR-WM v1.0 §D8`／`§P4.E2` |
| **KDI.3**（WM-D9） | §4 | Confidence 形式化語義、傳播、比較 | `AUGUR-WM v1.0 §D9`／`§P4.E8`、`§2.10` |
| **KDI.4**（WM-D10） | §6、§8 | supersede／tombstone、Evidence 三分類、信任分級 | `AUGUR-WM v1.0 §D10`／`§P4.W1`、`§P4.E3`、`§P4.E7` |
| **KDI.5**（WM-D11） | §9 | 完備性等級 | `AUGUR-WM v1.0 §D11`／`§P5.W3`、`§P5.E2` |
| **KDI.6**（WM-D18，L4 面向） | KS.25、KS.62 | Registry 登錄結構（L4 面向）、唯一權威表徵落點（D18 之 L7 機制 slice〔部署拓撲／Registry 實作載體／直綁消除技術手段〕對稱下放 KDO.5） | `AUGUR-WM v1.0 §D18`／`§P1.E2` |
| **KDI.7**（WM-D21） | KS.78 | 維度白名單取得機制 | `AUGUR-WM v1.0 §D21` |
| **KDI.8**（WM-D26） | KS.54 | 重編／對帳差異處置 | `AUGUR-WM v1.0 §D26`／`§P4.E3` |
| **KDI.9**（WM-D27） | KS.45 | point-in-time 快照 | `AUGUR-WM v1.0 §D27`／`§P4.E2` |
| **KDI.10**（ID-IDO.1） | §4、§10 | identity claim Confidence 語義 | `AUGUR-ID v0.1-draft` IDO.1／`§P4.E8` |
| **KDI.11**（ID-IDO.2） | §3、§10 | identity claim／lifecycle 事件之五元組欄位 | `AUGUR-ID v0.1-draft` IDO.2／`§P4.E1` |
| **KDI.12**（ID-IDO.3） | KS.26＋KDO.7 | lifecycle 事件表欄位／索引之 L4 概念槽承接；物理實作→L7（ID 原文定性為物理欄位／索引實作、tombstone 儲存落地） | `AUGUR-ID v0.1-draft` IDO.3（L4／L7 面向） |
| **KDI.13**（ID-IDO.4） | KS.83＋KDO.1＋KDO.4 | 未解析存量指標量測（完備性輸入，KS.83(i)）＋resolution 演算實作（→L5 推論 KDO.1，KS.83(ii)；定性分歧 T-KS-6） | `AUGUR-ID v0.1-draft` IDO.4 |
| **KDI.14**（ID-IDO.6） | §5 | as-of 重建引擎與能力等級 | `AUGUR-ID v0.1-draft` IDO.6／`§P4.E2` |
| **KDI.15**（ID-IDO.8） | KS.25、KS.62 | 唯一權威 Representation 實際指定 | `AUGUR-ID v0.1-draft` IDO.8／`§WM.37` |
| **KDI.16**（ONT 散列） | KS.20 | Attribute schema 欄位設計、Confidence 不設於 L2 | `AUGUR-ONT v0.1-draft §ONT.2`、`§DO`（D9 散列） |
| **KDI.17**（WM-D12，L4 面向） | KS.84（＋§8 KS.32、§9 KS.81(d)） | GATE 統計治理之 **Layer 4 Evidence 機制設計**（多重比較調整、判準凍結、二次證偽封鎖之概念層約束；HOOK-03「統計嚴謹化屬 Layer 4 Evidence 機制設計權」） | `AUGUR-WM v1.0 §D12`／HOOK-03、`§A.19`、`§A.52` |

## Annex DO [N] — 下放下層 DEFER 掛鉤（defers-out）

> **KDO.0（下放義務）[N]** 本表每列為規範性下放掛鉤：本層明示不定義該實作事項，授權並要求目標 Layer 定義之；目標 Layer 規格作成時必須於其 Compliance Statement 之 `defers-in` 欄承接對應列。
> **義務主體**：本規格自身（設掛鉤）、目標 Layer 規格作者（承接）。**可判定判準**：本表每列與 Annex CS front-matter `defers-out` 欄雙向可解析；本層無任一條款對本表所列事項作成可被下層直接消費之實質定義（KS.8 下侵判準）。

| 掛鉤 | 本規格落點 | 下放事項 | 目標 Layer | 授權 |
|---|---|---|---|---|
| **KDO.1** | KS.34、KS.39、KS.83(ii) | Confidence 傳播聚合之推論引擎實作、resolution 演算之 inference 實作 | L5 | `§P4.E8`、`§0.6(b)` |
| **KDO.2** | KS.33、KS.35、KS.76、KS.80 | Confidence banding 閾值、消費門檻、風險分級表、完備性門檻 | L6 | `§P5.E2`、`§P4.E7` |
| **KDO.3** | KS.100、KS.84 | 外部知識入 World Representation 之**推論工作流實作**（HOOK-02 之 L5 面向）、GATE 統計治理之**統計計算實作**（HOOK-03 演算面；設計權屬 L4，見 KS.84） | L5 | `AUGUR-WM v1.0` HOOK-02、`§D12`、`§D14`、`§P2.W2` |
| **KDO.4** | KS.83(i) | 未解析存量量測落地 | L5/L7 | `AUGUR-ID v0.1-draft` IDO.4 |
| **KDO.5** | KS.25、KS.62、KS.36 | `AUGUR-WM v1.0 §D18` 之 **L7 機制 slice**：部署拓撲、Registry 實作載體、直綁消除技術手段（AUD-01 之來源位置字面直綁消除） | L7 | `AUGUR-WM v1.0 §D18`、`§P1.E2`、`§0.6(b)` |
| **KDO.6** | KS.44 | as-of gate／purged／embargo 實作、雙時間查詢操作化 | L5/L7 | `§P4.E2` |
| **KDO.7** | KS.20、KS.26、KS.53 | Knowledge／lifecycle／tombstone 之物理欄位、索引、序列化、儲存 | L7 | `§0.6(b)` |

> 〔編號註記 [I]：KDO.3、KDO.5 原為十位制保留空號，本版已啟用（KDO.3 承接 HOOK-02/03 之 L5 面向、KDO.5 承接 `§D18` 之 L7 機制 slice），編號原位啟用、非跳號，適用 KS.111 永不重排、永不重用。原 draft 之非數字後綴「KDO.HOOK02」已廢除並改編為正規序號 KDO.3，其目標 Layer 由「L4/L5」收斂為純 **L5**（消除 Layer 4 向自身之自指下放，符 KS.8／KS.11 「defers-out 目標須為下層 L5–7」）；GATE 統計治理之 Layer 4 面向已由正文 KS.84 承接，非下放。〕

---

## Annex L3U [N] — 與 Layer 3 之分界表（承接側，與 `AUGUR-ID v0.1-draft` Annex L4 同構）

> **L3U.0（一句判準）[N]** Layer 3 產出「個體的永久參照、其跨體系繫結與其一生的機器機制」；本層產出「繫結該參照之 Knowledge 之信度、欄位與 as-of 重建能力」。分界必須精確，否則構成上侵（違 KS.7、KS.8）。
> **義務主體**：本規格自身、Layer 3 規格作者。**可判定判準**：下表「本層得為」欄與「Layer 3 專屬」欄無交集，且本層任一條款不落入「Layer 3 專屬」欄者為合規。

| 面向 | Layer 3 專屬（本層消費） | 本層得為（Layer 4 專屬） |
|---|---|---|
| identity claim | 身份側四要件、衝突並存、唯一權威表徵之結構前提 | **Confidence 語義（KS.90）、完整五元組欄位（KS.91）、唯一權威 Representation 實際指定（KS.25/62）** |
| lifecycle | 事件語義、lineage、tombstone／去識別化語義 | 事件表欄位概念設計（KS.26）、Knowledge 側 tombstone 語義（KS.53） |
| provisional | 解析義務、概念稽核指標存在性 | 指標之完備性納入語義（KS.83）、量測 DEFER（KDO.4） |
| 身份屬性 as-of | 屬性須具雙時間繫結（版本存在） | **as-of 重建引擎與能力等級（§5）** |

---

## Annex TR [N] — WM.44 逐條對應矩陣（憲章＋WM＋ONT＋ID → KS）

> **TR.0（矩陣之地位與生效要件性）[N]** 依 `AUGUR-WM v1.0 §WM.44`：`AUGUR-MC v1.3`、`AUGUR-WM v1.0`、`AUGUR-ONT v0.1-draft`、`AUGUR-ID v0.1-draft` 全部 [N] 條款均須對應至本規格至少一 [N] 條款、明記 DEFER 掛鉤、或明記「不觸及」及理由。**本矩陣已就四上層規格全部條款逐條完整枚舉**：TR.A（`AUGUR-MC v1.3` §P4 家族）、TR.B（`AUGUR-MC v1.3` PA／P1／P2／P3／P5 及 §0/§2/§4/§8 逐條）、TR.C（`AUGUR-WM v1.0` WM.1–53＋Annex A A.0–A.59＋Annex D D0–D28 逐條）、TR.D（`AUGUR-ONT v0.1-draft` ONT.1–62＋Annex T T.0–T.91 逐條）、TR.E（`AUGUR-ID v0.1-draft` ID.1–81＋IDO.0–8＋Annex L4 逐條）。逐條完整枚舉已滿足 `§WM.44` 之形式充分性；**Steward 充任認定業經作成，本規格自 2026-07-17 起生效**（Steward 裁決第 2026-005 號、AL-2026-009；`§0.5`、`§8.3`），**餘無生效阻卻**；**實質**充分性之最終判斷仍屬 Steward `§8.2` 違憲審查程序。
> **義務主體**：本規格、Steward。**可判定判準**：如 `§WM.44` 內建之對應完備性檢查——四上層每一 [N] 條款於本矩陣有落點列（承接／細化／DEFER／不觸及＋理由）者為完備。凡標「不觸及＋理由」之列，其理由為機器可判之處置。

### TR.A — `AUGUR-MC v1.3` §P4 家族（核心，逐條）[N]

| MC 條款 | KS 落點 | 模式 |
|---|---|---|
| §P4.D（Evidence 可追溯） | KS.70、KS.6 | 細化 |
| §P4.W1（三類 Evidence、無 Source 之 Knowledge 拒斥） | KS.71、KS.24 | 細化（維護權） |
| §P4.E1（Knowledge 五元組） | KS.20–KS.26 | 細化（欄位化，D7） |
| §P4.E2（Time（雙時間性）） | KS.40–KS.46、KS.22 | 細化（能力等級，D8） |
| §P4.E3（Supersede（只失效不刪除）） | KS.50–KS.55 | 細化（supersede 形式化，D10） |
| §P4.E4（Defeasible（可謬性）） | KS.31（DETERMINISTIC 依據）、KS.36 | 細化 |
| §P4.E5（Conflict（矛盾保存）） | KS.60–KS.63、KS.51 | 細化 |
| §P4.E6（Provenance（遞迴溯源）） | KS.70、KS.32、KS.24、KS.52 | 細化 |
| §P4.E7（NoLaundering（信任不可洗白）） | KS.72–KS.77、KS.34 | 細化（信任分級，D10） |
| §P4.E8（Confidence（語義與消費）） | KS.30–KS.39、Annex CM | **細化（核心，D9）** |

### TR.B — `AUGUR-MC v1.3` 非 P4 家族（逐條）[N]

| MC 條款 | KS 落點／處置 | 模式 |
|---|---|---|
| PA（Prime Axiom）＋§1.1 釐清句 | KS.6、KS.36、KS.70、CS.1-PA（可追溯 Evidence／不確定性可追溯／錯誤可修正） | 承接 |
| §1.2（標準鏈引用：EV.1–EV.6 節選＋Intelligence 於 EV.7–EV.8 之落點） | KS.70（EV.5 Evidence 遞迴溯源）、KS.20（EV.6 Knowledge 五元組）、KS.34（Confidence 沿推理鏈傳播，量化 EV.6→EV.7 節選之信度移轉）、CS.1-EV-chain（節選不跳節點） | 承接 |
| §1.3（五條對稱禁令；模態內容 referent 釐清） | 第四禁令「沒有 Evidence，不允許 Conclusion」→ KS.24（空 Evidence 之 Knowledge 為禁止型態）、KS.70（遞迴溯源終止判準）；模態內容之型別與 referent 屬 Layer 2，本層不重定義（承 KS.10） | 承接 |
| P1（Reality First 標題） | KS.7、KS.72 | 承接 |
| P1.D（第一性對象＝Reality，非資料／模型／程式／資料庫） | KS.4（概念層獨立性＋刪名測試：本層定義不得以特定資料庫／欄位為錨點）、KS.7（四層分工，Knowledge 層不僭越 Reality 本身之表徵） | 承接 |
| P1.E1（開放來源） | KS.72（來源非最高抽象於信任側）、KS.30（單一論域） | 承接 |
| P1.E2（共同世界模型之語義） | KS.25、KS.62；直綁消除技術手段 DEFER L7（KDO.5） | 細化＋DEFER |
| P1.E3（Bounded Representation） | 承 Layer 3 `§ID.42`；法規對應 DEFER L6 | 承接＋DEFER（不觸及機制） |
| P1.W1（Augur 必須優先描述 Reality，而不是優先適配現有資料來源） | KS.72、KS.77（不以來源／自產逕升信） | 承接 |
| P2（Representation Before Intelligence 標題） | KS.23 | 承接 |
| P2.D（首要任務＝建立一致可追溯可演化 Representation，非產生智慧） | KS.24（Evidence 槽承載可追溯性）、KS.100（Confidence 之生成推論〔Intelligence〕界分於 Layer 5，本層僅定 Knowledge 側語義） | 承接 |
| P2.E1（禁止 AI 直接從 raw data 建立永久性 Knowledge） | KS.20、KS.77 | 承接 |
| P2.E2（Model output 不得未經 Evidence 通道（§2.11），直接成為權威 World Representation 或 Knowledge） | KS.24、KS.34（表徵可靠性繫於 Evidence 鏈） | 承接 |
| P2.E3（self-reported 標記） | KS.21、KS.77 | 承接 |
| P2.E4（禁止 Representation 被視為 Reality 本身） | KS.20、§4 | 承接 |
| P2.E5（錯誤發現後之失效反應／fail-safe） | KS.36、KS.102（判定主體 DEFER L4–L6，`§WM.29`／D15） | 承接＋DEFER |
| P2.W1（任何 Prediction、Reasoning、Planning、Decision、Agent Action，皆必須建立於 World Representation） | KS.24、KS.100（角色四界分） | 承接 |
| P2.W2（權威順序釐清） | 外部知識入確立工作流 DEFER L5（KDO.3） | DEFER |
| P3（Identity Before Knowledge 標題） | KS.23 | 承接 |
| P3.D（任何 Knowledge 必須首先回答「關於哪一個 Identity」） | KS.20（Identity 槽為五元組不變式之一，缺即違憲）、KS.23（Identity 槽——承接 Layer 3 已解析 Identity） | 承接 |
| P3.E1（引用與解析義務） | KS.23、KS.92 | 承接 |
| P3.E2（Identity Lifecycle） | KS.91、KS.26 | 承接 |
| P3.E3（同一性判準掛鉤） | KS.63、KS.91（禁 LWW） | 承接 |
| P3.W1（Augur 不以 table row、file、document、embedding、model token 作為世界基本單位） | 承 Layer 3；KS.23 | 承接（不觸及機制） |
| P3.W2（Identity 類型） | KS.23、KS.36（承 Layer 3 採認可謬） | 承接 |
| P4（Evidence Before Conclusion 全家族） | 見 **TR.A**（逐條） | 細化（核心） |
| P5（Accountability Before Action 標題） | CS.1-P5 | 部分不適用＋DEFER |
| P5.D（Action 之問責定義：誰發起／誰授權／憑何知識；純表徵變更非 Action） | 不觸及＋理由：Action 問責結構（P5.E1 六元組）屬 Layer 6（同 P5.E1，KS.101）；純表徵狀態變更之歸責另由 P2.E5、TR.A（P4.E6／E7）承接，本列不重複列示 | 不觸及＋理由 |
| P5.E1（Action 六元組與問責） | 不觸及＋理由：Action 六元組與行動治理屬 Layer 6，本層不定義（KS.101） | 不觸及＋理由 |
| P5.E2（風險分級表、完備性等級由 L4、Confidence 門檻） | 完備性等級本身→KS.80、KS.81；Confidence 語義→§4；風險分級／門檻 DEFER L6（KDO.2） | 細化（完備性等級）＋DEFER |
| P5.W1（任何 Action 必須可歸責於單一 Identity） | 不觸及＋理由：問責治理屬 Layer 6 | 不觸及＋理由 |
| P5.W2（人類權威閘） | KS.35（消費受最低 Confidence 約束）、CM.1(a) escalated 列引 `§P5.W2`；資格判準 DEFER L6 | 承接＋DEFER |
| P5.W3（不可逆／高影響需最高完備性） | KS.82（完備性量尺）；綁定 DEFER L6 | 承接＋DEFER |
| P5.W4（Agent 僅持有完成當前經授權 Plan 所需之最小權限） | 不觸及＋理由：監督否決度量屬 Layer 6（KS.101） | 不觸及＋理由 |
| P5.W5（系統不得規劃、執行或學習任何降低人類監督與否決能力之行為） | KS.82 引述缺位預設（`§P5.E2`），本層不削弱 | 承接（引述不削弱） |
| §0.1（名稱、層級與版本：規格自我登錄慣例） | KS §0.1（名稱、層級與版本節，效力依 KS.5 承載）：本規格依同一慣例自我登錄名稱、Layer 4、版本、上層規格 | 承接 |
| §0.2（規範用語約定：MUST／MUST NOT／SHOULD／MAY） | KS §0.2（規範用語約定節：「沿用 `AUGUR-MC v1.3 §0.2`……全文一致，不重定義」，效力依 KS.5 承載） | 承接 |
| §0.4／§0.5（權威語言聲明／權威語言聲明／適用範圍：Layer 對照表） | KS.4（§0.4 權威語言）、§0.5（引用格式）、KS.3（§0.5 對照表 Layer 4 職掌） | 承接 |
| §0.6(a)（lex superior） | KS.1 | 承接 |
| §0.6(b)（概念層獨立性） | KS.4、KS.11、Annex DO | 承接 |
| §2.5（Evidence 定義） | KS.2（不重定義）、§8（Evidence 分類法細化） | 細化 |
| §2.6（Knowledge 定義） | KS.2、§3（五元組欄位化） | 細化 |
| §2.10（Confidence 定義） | KS.2、§4（單一形式化語義） | 細化 |
| §2.11（Evidence 通道） | KS.70、KS.20（EV.5→EV.6 機制化）、CS.1-EV-chain | 承接 |
| §4 canonical chain（EV.1–EV.12） | KS.70（EV.5 Evidence）、KS.20（EV.6 Knowledge）、CS.1-EV-chain（節選不跳節點）；EV.1–4／7–12 承接不重定義 | 承接 |
| §5 角色一/二/四（system of record／表徵／Reasoning） | KS.25（角色一 Knowledge 側）、KS.24、KS.100（角色四界分） | 承接＋界分 |
| §5 角色三/五/六（Intelligence／介面／執法點） | 不觸及＋理由：屬 Layer 5/6 執行層（KS.100、KS.101） | 不觸及＋理由 |
| §6 F1（Data First Architecture：禁先建資料表再想世界模型；違反 P1） | KS.4（概念層獨立性＋刪名測試：Knowledge 五元組／Confidence 為概念層形式，不以特定資料庫欄位結構為定義依據）、KS.20（Confidence／五元組 hooks 物理欄位→L7，非資料表結構決定 Knowledge 存在） | 承接 |
| §6 F2（Model First Architecture：禁先選 AI model 再設計系統；違反 P2） | 不觸及＋理由：AI model 選型屬 Layer 5（Cognitive Kernel／AI Model Selection，`§0.5` 對照表）；本層僅定 Confidence 之語義與消費約束（§4），不涉模型選型 | 不觸及＋理由 |
| §6 F3（Agent First Architecture：禁先做 Agent 再補資料治理；違反 P2、P5） | 不觸及＋理由：Agent 建置順序屬 Layer 6 Agent Runtime；本層僅定 Source 槽承接已解析 Identity（含 Agent，KS.21），不定義 Agent 建置順序 | 不觸及＋理由 |
| §6 F4／F5（Knowledge Without Identity／Knowledge Without Identity／Intelligence Without Evidence） | KS.24（F5 空 Evidence 拒斥）、KS.27 對應（無位置性） | 承接 |
| §6 F6（Unaccountable Action：禁無法回答誰發起／誰授權／憑何知識之 Action；違反 P5.E1） | 不觸及＋理由：Action 問責之六元組與執行機制屬 Layer 6（同 P5.E1，KS.101）；本層僅提供 Knowledge Basis 一環之 Confidence／完備性語義（KS.35、KS.80） | 不觸及＋理由 |
| §7（Long-Term Stability Rule（十年以上演化原則）） | KS.4（概念層獨立性＋刪名測試：本層之技術中立與長期穩定性落實，呼應 §7「不依賴特定 AI model／database」）；五項不變核心逐項見 TR.A／TR.B 各 P1–P5 對應列 | 承接 |
| §8.1／§8.6（Constitution Steward（憲章權威）／Constitution Steward（憲章權威）／版本語義、引用格式與編號穩定性） | KS.111、§0.3 | 承接 |
| §8.2（違憲後果、審查程序與衝突優先序） | KS.1、KS.5（較嚴格解讀） | 承接 |
| §8.3（合規聲明義務與可判定性元規則） | KS.38、KS.75、Annex EO（可判定性元規則全文落實） | 承接 |
| §8.4（不可豁免核心） | KS.20（§P4.E1 不可豁免）、KS.111（MUST NOT 不豁免） | 承接 |
| §8.5（Amendment Procedure（修訂程序）） | 不觸及＋理由：修憲程序屬 Layer 0 憲章自身治理機制（Steward 議決門檻、Amendment Log、PA 永恆條款），非 Layer 4 概念層規格所轄；本規格僅為受規範對象（KS.1 從屬義務），不代行定義憲章修訂程序 | 不觸及＋理由 |

### TR.C — `AUGUR-WM v1.0`（全部 [N]，逐條）[N]

**(1) 正文 WM.1–WM.53**

| WM 條款 | KS 落點／處置 |
|---|---|
| WM.1（從屬） | KS.1—承接 |
| WM.2（細化不重定義） | KS.2—承接 |
| WM.3（管轄與 DEFER 紀律） | KS.3、KS.10—承接 |
| WM.4（概念層獨立性＋刪名測試） | KS.4—承接 |
| WM.5（任務） | KS.6—承接 |
| WM.6（領域 Profile 與領域前身文件） | 不觸及＋理由：Profile 框架屬存在層，本層消費 Profile 之 Knowledge，不重定義框架 |
| WM.7（最高抽象） | KS.72（來源非最高抽象於信任側）—承接 |
| WM.8（結構獨立性） | 不觸及＋理由：結構獨立性屬存在層本體，本層不重定義 |
| WM.9（權威三分） | KS.71、CM.1(a)「值忠實鏡像來源之對帳確認類」引 `§WM.9(a)`—承接 |
| WM.10（Observation Store 宣告） | KS.24、KS.54（對帳獨立裁決）—承接 |
| WM.11（referent 繫結） | KS.23—承接 |
| WM.12（近似性與來源保留） | KS.25、§4（近似性→Confidence 語義填充）、KS.72（來源保留→Trust Rank）—語義填充 |
| WM.13（三性質可判定判準＋演化四不變式） | KS.7；三性質判準屬存在層，本層不重定義—承接（不觸及判準本體） |
| WM.14（語義唯一性與一對多映射） | KS.25、KS.62、KS.63—落實 |
| WM.15（多通道之同一性宣告） | KS.63（無宣告即非同一）—承接 |
| WM.16（衝突與證據不足之表達力） | KS.60–KS.63、KS.31（INSUF）—承接 |
| WM.17（模態內容） | KS.31（INSUF＝證據不足合法狀態）；模態型別屬存在層—承接（不重定義模態） |
| WM.18（候選斷言之地位與狀態轉換） | KS.20（五元組概念相容，D7）、KS.77—承接 |
| WM.19（基本單位） | KS.7—承接 |
| WM.20（跨部署解析與命名空間不強制） | 承 Layer 3；本層不觸及命名機制—承接（不觸及機制） |
| WM.21（結構位置義務與效力封印） | KS.24、KS.27 對應（禁止型態無位置性）—承接 |
| WM.22（生命週期存續不變式） | KS.50、KS.53（只失效不刪除）—承接 |
| WM.23（實體類型開放例示） | KS.71（開放列舉體例）；型別制定屬 L2—承接（不重定義型別） |
| WM.24（canonical chain 承接） | KS.70、CS.1-EV-chain—承接 |
| WM.25（變更二分） | KS.54（restatement 為世界事件）—承接 |
| WM.26（自反性） | KS.84（GATE 為自反 Dynamic Entity，`§A.19`）—承接 |
| WM.27（Action 六元組世界事件與禁止型態之無位置性） | KS.24（空 Evidence 無位置）；Action 六元組屬 L6—承接（無位置性）＋不觸及（六元組） |
| WM.28（人類權威表徵位置） | KS.80–KS.82（完備性側）；判定主體 DEFER—承接＋DEFER |
| WM.29（fail-safe 狀態容納） | KS.102、KS.29 對應；判定主體 DEFER L4–L6—承接＋DEFER |
| WM.30（雙時間性） | KS.22、KS.40、§5（D8）—細化 |
| WM.31（時間屬性雙宣告） | KS.42、KS.44—細化 |
| WM.32（觀測定案性） | KS.43、KS.50、KS.54—細化 |
| WM.33（永久標記表達力） | KS.21、KS.50、KS.74（標記存續之語義填充）—承接 |
| WM.34（核心不變式之可機器稽核 (a)(b)） | KS.34、KS.52、KS.70—承接 |
| WM.35（落地即整合；消費設閘不阻斷落地） | KS.25、KS.35（消費設閘語義）；攝取實作屬下層—承接 |
| WM.36（World Concept Registry 與消費規則） | KS.25、KS.62；Registry 實作載體／直綁消除 DEFER L7（KDO.5）—落實＋DEFER |
| WM.37（唯一權威表徵落實義務） | KS.25、KS.62（D18）—落實 |
| WM.38（自然人之有界表徵） | 承 Layer 3 `§ID.42`；本層不觸及機制—承接（不觸及機制） |
| WM.39（適用範圍與效力規則） | KS.110、Annex CS—承接 |
| WM.40（機器可稽核 front-matter） | Annex CS front-matter—承接 |
| WM.41（逐原則論證本文） | CS.1—承接 |
| WM.42（緊張關係與豁免登記） | CS.2—承接 |
| WM.43（雙向 DEFER 承接表） | CS.3、Annex DI／DO—承接 |
| WM.44（形式充分性判準） | CS.4、Annex TR（本矩陣）—落實 |
| WM.45（過渡承接／正式格式） | KS.110（作成於 Layer 1 生效日後）—承接 |
| WM.46（引用格式與編號穩定性） | KS.111、§0.3—承接 |
| WM.47（審查與豁免承接） | KS.111、CS.2—承接 |
| WM.48（重新認證與書面形式） | KS.111—承接 |
| WM.49（地位與衝突規則） | KS.1、【地位】節—承接 |
| WM.50（必備五部結構） | 全文結構（front-matter／論證／緊張／DEFER 表／矩陣）—承接 |
| WM.51（越界禁止） | KS.8、KS.10—承接 |
| WM.52（版本節奏隔離） | KS.111—承接 |
| WM.53（文件約定之規範地位） | KS.5—承接 |

**(2) WM Annex A（A.0–A.59；領域 Profile）**——凡標「領域實例」者，理由為：領域型別／事件實例屬存在層 Profile，本層對其 Knowledge 一體適用 §3（五元組）／§4（Confidence）／§5（as-of），不逐型別重定義。

| A 條款 | KS 落點／處置 | A 條款 | KS 落點／處置 |
|---|---|---|---|
| A.0（地位與範圍） | 不觸及＋理由：Annex A 地位條，存在層 | A.30（DataFinality） | KS.43、KS.54—承接 |
| A.1（Security） | 不觸及＋理由：領域實例 | A.31（槽位設置） | KS.20—承接 |
| A.2（Roster） | 不觸及＋理由：領域實例 | A.32（候選記載） | KS.20、KS.77—承接 |
| A.3（Index） | 不觸及＋理由：領域實例 | A.33（第二識別體系繫結） | 承 Layer 3；KS.23—承接 |
| A.4（TradingCalendar） | 不觸及＋理由：領域實例 | A.34（最小時間粒度） | KS.22—承接 |
| A.5（MarketParticipant 階層） | 不觸及＋理由：領域實例 | A.35（每通道時間屬性雙宣告） | KS.44—承接 |
| A.6（DerivativeContract） | 不觸及＋理由：領域實例 | A.36（通道時間模型不對稱之揭露） | KS.46—承接 |
| A.7（ConvertibleBond） | 不觸及＋理由：領域實例 | A.37（定案性判準之宣告形式） | KS.42、KS.32—承接 |
| A.8（Warrant） | 不觸及＋理由：領域實例 | A.38（預測任務時間邊界＝模態邊界） | §5、KS.44—承接 |
| A.9（ForeignSecurity） | 不觸及＋理由：領域實例 | A.39（Observation Store 域內認定） | KS.24—承接 |
| A.10（Commodity／FX／Rate／BondYield 維度族） | KS.78（維度白名單）—承接 | A.40（「API 即權威」定位限定） | KS.72、CM.1(a)—承接 |
| A.11（EconomicIndicator） | KS.41（vintage＝A3 範式）、KS.45—承接 | A.41（系統記錄之域內實例） | KS.24—承接 |
| A.12（IndustryClassification） | KS.81(f)—承接（產業條件豁免之粒度，RULING-2026-016） | A.42（排除閉集與排除理由類型） | KS.71—承接 |
| A.13（DataProvider） | KS.72（Trust Rank 來源型態）—承接 | A.43（下市與可見性） | KS.55—承接 |
| A.14（Model 與 CoreUniverse） | KS.55、KS.74（synthetic；成員資格版本化）、KS.80 增補款（成員資格判準結構）—承接 | A.44（語料通道 license 三軌與隔離） | KS.72、KS.78—承接 |
| A.15（HumanDecisionMaker） | KS.76（人類確認）；承 Layer 3—承接 | A.45（真兆三問） | KS.75、KS.81—承接 |
| A.16（KnowledgeCorpus 語料實體族） | KS.71（Knowledge Evidence）、KS.72—承接 | A.46（三敵框架＝防線組織） | KS.75、KS.76—承接 |
| A.17（Catalog 元資料） | KS.25（Registry 實作載體 [I]）—承接 | A.47（as-of 紀律為判準非實作） | KS.44—承接 |
| A.18（NewsEvent） | 不觸及＋理由：領域實例 | A.48（思想≠特定值） | KS.78、KS.84—承接 |
| A.19（GATE 預註冊實驗） | KS.84（GATE 統計治理 L4 面向）—承接 | A.49（經濟價值≠準確率；防守靠規則） | 不觸及＋理由：策略哲學屬 L5/L6 |
| A.20（Augur 自身） | KS.21（synthetic／self）—承接 | A.50（誠實輸出契約之表達力承接） | KS.43（已呈現不可靜默重寫）；輸出契約 DEFER L6 |
| A.21（CorporateAction） | KS.54；領域實例—承接 | A.51（管線分層本體論之角色對映） | 不觸及＋理由：管線分層屬 L5/L7 |
| A.22（財報與月營收公開事件） | KS.54（restatement）—承接 | A.52（假說與 GATE 之定位） | KS.84、KS.100—承接 |
| A.23（RegulatoryStateChange） | KS.54；領域實例—承接 | A.53（系統建議、人決策） | KS.35、KS.76—承接 |
| A.24（期權結算事件） | KS.54；領域實例—承接 | A.54（OPEN-1：stock_id 時間穩定性） | 承 Layer 3；KS.23—承接 |
| A.25（Delisting） | KS.55—承接 | A.55（OPEN 節之消費規則） | 不觸及＋理由：OPEN 承接屬存在層 |
| A.26（PriceLimit 漲跌停狀態） | KS.45；領域實例—承接 | A.56（Profile 增補程序） | 不觸及＋理由：Profile 程序屬存在層 |
| A.27（信用交易 stock-flow 狀態族） | KS.45（point-in-time）—承接 | A.57（Issuer） | 承 Layer 3；不觸及＋理由：領域實例 |
| A.28（持股結構狀態） | KS.45（point-in-time）—承接 | A.58（MarketTrade／DailyBar） | 不觸及＋理由：領域實例 |
| A.29（UniverseMembership） | KS.45、KS.55—承接 | A.59（涉自然人通道之域內宣告） | 承 Layer 3 `§ID.42`—承接 |

**(3) WM Annex D（D0–D28；下放掛鉤）**——D7–D12/D18/D21/D26/D27 為本規格 defers-in（Annex DI）；餘為下放他層之掛鉤，本層不觸及＋理由（非 Layer 4 承接對象）。

| D 條款 | KS 落點／處置 | D 條款 | KS 落點／處置 |
|---|---|---|---|
| D0（DEFER 總表地位） | Annex DI 承接體例—承接 | D15（fail-safe 判定程序） | KS.102（判定主體 DEFER L4–L6）—承接界分 |
| D1（抓取模式五態） | 不觸及＋理由：下放 L5/L7 攝取 | D16（永久標記落地） | KS.21、KS.50、KS.74—承接（標記語義） |
| D2（限流防護） | 不觸及＋理由：下放 L7 | D17（法規對應表） | 不觸及＋理由：DEFER L6 |
| D3（冪等 upsert／物理落地） | 不觸及＋理由：下放 L7（KDO.7 對應物理面） | D18（拓撲／Registry 載體／直綁消除） | KDI.6（L4 登錄結構）＋KDO.5（L7 機制 slice）—承接＋下放 |
| D4（AST 稽核） | 不觸及＋理由：下放 L5/L7 | D19（RBAC 表設計） | 不觸及＋理由：下放 L6/L7 |
| D5（DB trigger fail-closed） | 不觸及＋理由：下放 L7 | D20（輸出契約本體） | 不觸及＋理由：下放 L6 |
| D6（展示分級） | 不觸及＋理由：下放 L6 | D21（維度白名單取得機制） | KDI.7→KS.78—承接 |
| D7（Knowledge 五元組欄位） | KDI.1→§3—承接 | D22（核心宇宙完整性 gate、流動性分位地板、產業條件豁免） | KS.80 增補款＋KS.81(f)—承接（RULING-2026-016 更正：原誤標「多重比較家族治理→KS.84」，該實質屬 D12、:837 列既承） |
| D8（as-of 重建機制與能力等級） | KDI.2→§5—承接 | D23（as-of 查詢操作化） | KDO.6—下放 L5/L7 |
| D9（Confidence 形式化語義） | KDI.3→§4—承接 | D24（序列化格式） | 不觸及＋理由：下放 L7（KDO.7） |
| D10（supersede／tombstone／三分類／信任分級） | KDI.4→§6／§8—承接 | D25（儲存引擎） | 不觸及＋理由：下放 L7（KDO.7） |
| D11（完備性等級） | KDI.5→§9—承接 | D26（重編／對帳差異處置） | KDI.8→KS.54—承接 |
| D12（外部知識入判準／GATE 體系） | KDI.17→KS.84（L4 面向）；工作流 DEFER L5（KDO.3）—承接＋DEFER | D27（point-in-time 快照） | KDI.9→KS.45—承接 |
| D13（隔離稽核落地） | 不觸及＋理由：下放 L5/L7 | D28（其餘機制落地） | 不觸及＋理由：下放 L5–L7（依 `§WM` D28 所指事項對應層） |
| D14（確立程序與候選斷言工作流） | 工作流 DEFER L5（KDO.3）；五元組欄位→§3—承接（欄位）＋DEFER（工作流） | | |

### TR.D — `AUGUR-ONT v0.1-draft`（全部 [N]，逐條）[N]

**(1) 正文 ONT.1–ONT.62**

| ONT 條款 | KS 落點／處置 |
|---|---|
| ONT.1（從屬） | KS.1—承接 |
| ONT.2（細化不重定義；Attribute schema 欄位設計 DEFER L4） | KS.20、§4—承接（KDI.16） |
| ONT.3（管轄與 DEFER 紀律） | KS.3—承接 |
| ONT.4（概念層獨立性＋刪名測試承接） | KS.4—承接 |
| ONT.5（[N]/[I] 標注、三態與位置） | KS.5、§0.3—承接 |
| ONT.6（任務） | KS.6；型別任務屬 L2—承接（不觸及型別任務） |
| ONT.7（定位：三層不僭越） | KS.7—承接 |
| ONT.8（型別定義不得由來源反推） | KS.72（來源非最高抽象呼應）；型別定義屬 L2—承接（不重定義型別） |
| ONT.9（引用格式與編號穩定性） | KS.111、§0.3—承接 |
| ONT.10（頂層本體範疇） | 不觸及＋理由：頂層範疇制定屬 Layer 2 型別層 |
| ONT.11（開放例示之封閉化紀律） | KS.71（開放列舉體例承接）—承接 |
| ONT.12（型別定義三要件） | 不觸及＋理由：型別定義屬 Layer 2 |
| ONT.13（存在宣告 ↔ 分類體系接合） | KS.23（instance/type 標記 Knowledge 側）—承接 |
| ONT.20（判準宣告義務） | KS.23；判準本體屬 L2、採認屬 L3—承接（不重定義判準） |
| ONT.21（判準效力與 Layer 3 採認之封印） | 承 Layer 3；KS.23—承接（不觸及採認機制） |
| ONT.22（外部識別碼非 identifier） | 承 Layer 3；KS.23—承接 |
| ONT.30（繫結對象標記語義） | KS.23（instance/type 標記 Knowledge 側；存續落實屬 L3 `§ID.53`）—承接 |
| ONT.31（型別個體命名空間之概念層隔離） | 承 Layer 3；型別命名空間屬 L2—不觸及＋理由（命名空間屬 L2/L3） |
| ONT.40（世界關係為一級型別範疇） | KS.63（世界關係之衝突承載）；型別範疇屬 L2—承接（不重定義型別） |
| ONT.41（世界量為維度索引型別） | KS.78（維度白名單）—承接 |
| ONT.50（規範性對映義務；T-Map 唯一權威表徵型別側前提） | KS.25、KS.62（落實 Representation 側）—落實 |
| ONT.60（版本語義與型別存續不變式） | KS.111—承接 |
| ONT.61（審查與豁免承接） | KS.111、CS.2—承接 |
| ONT.62（合規聲明義務） | KS.110、Annex CS—承接 |

**(2) ONT Annex T（T.0–T.91；台股型別階層與同一性判準）**——型別定義與同一性判準屬 Layer 2 型別層；本層對其個體之 Knowledge 一體適用信度／欄位，不逐型別重定義。故 Annex T 全列**不觸及＋理由（型別制定屬 Layer 2）**，逐號涵蓋：T.0、T.1、T.2、T.3、T.4、T.5、T.6、T.20、T.21、T.22、T.23、T.24、T.25、T.26、T.27、T.28、T.29、T.30、T.31、T.32、T.33、T.34、T.35、T.36、T.40、T.41、T.42、T.43、T.44、T.50、T.51、T.52、T.53、T.60、T.61、T.90、T.91——每一 T.{n} 之處置均為「不觸及＋理由：型別／同一性判準屬 Layer 2，本層消費該型別之個體 Knowledge 而不重定義型別」；其中 T-Map（Annex A 世界概念→型別對映）之唯一權威表徵型別側前提另由 KS.25／KS.62 於 Representation 側落實（承 ONT.50）。

### TR.E — `AUGUR-ID v0.1-draft`（全部 [N]，逐條）[N]

**(1) 正文 ID.1–ID.81**

| ID 條款 | KS 落點／處置 |
|---|---|
| ID.1（三層不僭越） | KS.7—承接 |
| ID.2（下界封印） | KS.8—承接 |
| ID.3（承接盤點） | KS.9—承接 |
| ID.4（不擴張管轄） | KS.10—承接 |
| ID.10（授權範圍與語義義務保留） | 承 Layer 3；不觸及＋理由：identifier 授權屬 L3 |
| ID.11（系統鑄造義務） | 不觸及＋理由：identifier 鑄造屬 Layer 3（KS.7 上侵禁令） |
| ID.12（型別化命名空間隔離） | 不觸及＋理由：命名空間屬 Layer 3 |
| ID.13（永久性不變式） | 承 Layer 3；KS.23（消費已解析）—承接（不觸及機制） |
| ID.14（identifier 之 Identity 地位） | 承 Layer 3；KS.23—承接 |
| ID.20（採認行為） | 承 Layer 3；KS.23（消費採認已生效）—承接（不觸及採認機制） |
| ID.21（未採認即未解析） | KS.23—承接 |
| ID.22（採認之可謬性） | KS.23、KS.36—承接 |
| ID.23（resolution 演算與時限指標之下放） | KS.83、KDO.1（演算→L5）、KDO.4—承接＋轉下放 |
| ID.24（世界關係之身份解析） | KS.63；承 Layer 3—承接 |
| ID.30（一級介面四要件） | KS.90、KS.91（身份側四要件本層消費，Confidence／五元組填充）—承接＋填充 |
| ID.30(d)（Confidence 槽位） | KS.90、§4（IDO.1）—填充 |
| ID.31（claim 為 Knowledge，欄位設計下放） | KS.91、§3（IDO.2）—承接 |
| ID.32（唯一權威表徵之結構前提） | KS.25、KS.62（IDO.8，本層代 Layer 3 完成實際指定）—承接 |
| ID.40（生命週期事件之 Evidence 義務） | KS.26、KS.50（IDO.2/IDO.3 之 L4 概念槽）—承接 |
| ID.41（轉指全程可追溯不變式） | KS.50、KS.52（supersede DAG）；lineage 機制屬 L3—承接（Knowledge 側）＋不觸及（機制） |
| ID.42（法規強制抹除之留痕與去識別化） | KS.53（Knowledge 側 tombstone；identifier 側承 Layer 3 `§ID.42`）—承接 |
| ID.43（存續邊界截斷） | 承 Layer 3；KS.53—承接（不觸及機制） |
| ID.44（具生命週期實體之終結表徵） | KS.26、KS.50；終結語義屬 L3—承接（Knowledge 側） |
| ID.50（解析義務與升級禁止） | KS.23、KS.92—承接 |
| ID.51（未解析存量之可稽核指標） | KS.83（完備性輸入）、KDO.4—承接＋轉下放 |
| ID.52（unmapped 與待決同構） | KS.92（INSUF）—承接 |
| ID.53（instance/type 標記之存續與解析） | KS.23、KS.79；標記存續落實屬 L3—承接（Knowledge 側） |
| ID.60（身份屬性 as-of 繫結義務） | §5、KS.22、KS.40—承接 |
| ID.61（繫結存在 vs 重建引擎之分界） | §5（IDO.6，重建引擎 DEFER 本層 KDO.6）—承接 |
| ID.70（Layer 4 專屬事項清單） | KS.7、Annex L3U（與 ID Annex L4 同構）—承接 |
| ID.71（分界表） | Annex L3U—承接 |
| ID.80（格式承接） | KS.110—承接 |
| ID.81（存續與升版） | KS.111—承接 |

**(2) ID Annex DO（IDO.0–IDO.8；ID 之下放掛鉤，本層為承接對象者列 defers-in）**

| IDO 條款 | KS 落點／處置 |
|---|---|
| IDO.0（承接義務） | Annex DI 承接體例—承接 |
| IDO.1（claim Confidence 語義） | KDI.10→§4／§10（KS.90）—承接 |
| IDO.2（claim／lifecycle 五元組欄位） | KDI.11→§3／§10（KS.91、KS.26）—承接 |
| IDO.3（lifecycle 事件表物理欄位／索引、tombstone 儲存落地） | KDI.12→KS.26（L4 概念槽）＋KDO.7（物理→L7）—承接＋下放 |
| IDO.4（resolution 演算實作、未解析存量量測） | KDI.13→KS.83(i)＋KDO.1（演算→L5）＋KDO.4（量測）；定性分歧 T-KS-6—承接＋下放 |
| IDO.5（ID 內部其他下放，非 L4 承接對象） | 不觸及＋理由：IDO.5 目標非 Layer 4（依 ID 原文所指層下放） |
| IDO.6（as-of 重建引擎與能力等級） | KDI.14→§5＋KDO.6—承接＋轉下放 |
| IDO.7（ID 內部其他下放，非 L4 承接對象） | 不觸及＋理由：IDO.7 目標非 Layer 4（依 ID 原文所指層下放） |
| IDO.8（唯一權威 Representation 實際指定） | KDI.15→KS.25／KS.62—承接 |
| `AUGUR-WM v1.0 §D22`（核心宇宙 gate／流動性地板／產業豁免；目標 L4–L6） | **KDI.18**→KS.80 增補款／KS.81(f)—承接（RULING-2026-016 增列）；數值治理 DEFER L6（L6.11 增補款）、計算 DEFER L5 |

**(3) ID Annex L4（與 Layer 4 分界表）**——與本規格 Annex L3U 同構對表，「Layer 4 專屬」欄各列由本規格承接、「Layer 3 專屬」欄各列本層消費不重定義：identity claim 列→KS.90/KS.91/KS.25/KS.62；判準採認列→KS.23（消費）＋KDO.1/KDO.4（演算／量測下放）；lifecycle 列→KS.26/KS.53；provisional 列→KS.83/KS.92／KDO.4。逐列於 Annex L3U 對應承接（L3U.0 判準：兩欄無交集）。

> **TR.Z（逐條完整枚舉之完成與殘餘生效阻卻）[N]** TR.A–TR.E 已就 `AUGUR-MC v1.3`（P4 家族＋非 P4 逐條）、`AUGUR-WM v1.0`（WM.1–53＋Annex A A.0–A.59＋Annex D D0–D28）、`AUGUR-ONT v0.1-draft`（ONT.1–62＋Annex T T.0–T.91）、`AUGUR-ID v0.1-draft`（ID.1–81＋IDO.0–8＋Annex L4）**全部條款逐條枚舉落點**（承接／細化／DEFER／不觸及＋理由），滿足 `§WM.44`「任一條款無對應且無明記者，聲明不完整」之形式充分性要件。**Steward 充任認定業經作成，本規格自 2026-07-17 起生效**（Steward 裁決第 2026-005 號、AL-2026-009；`§0.5`、`§8.3`），**殘餘生效阻卻已解消**——形式充分性已成就；**實質**充分性之最終判斷仍屬 Steward 違憲審查程序（`§8.2`），充任不排除嗣後之違憲審查。上層草案（`AUGUR-ONT`／`AUGUR-ID`）於各自升版或條款增修時，本矩陣對應列**必須**同步維護（KS.111 diff 檢查）。
> **義務主體**：本規格、Steward。**可判定判準**：四上層全部 [N] 條款逐一於本矩陣有落點列者為完備（已成就）；上層條款增修而本矩陣未同步致某新條款無落點者，聲明重回不完整。

---

## Annex CS [N] — Constitutional Compliance Statement（依 `AUGUR-WM v1.0 §WM.39–45` 格式）

本 Annex 為**規範性聲明文件**（[N]）：其存在與內容為本規格之生效要件（KS.110、`AUGUR-MC v1.3 §8.3`、`AUGUR-WM v1.0 §WM.39`）。本聲明依 `AUGUR-WM v1.0 §WM.39–45` **正式格式**作成（非暫行模板，`§WM.45`）。**地位提示**：本規格為 **v1.0 生效版本**，Steward 充任認定已作成，自 2026-07-17 起生效（Steward 裁決第 2026-005 號，AL-2026-009；見【地位】、KS.110）；本聲明之**實質**充分性最終判斷仍屬 Steward `§8.2` 違憲審查程序。

```
compliance-statement:
  spec: Augur Knowledge System Specification
  spec-version: v1.0
  layer: 4
  mc-version: AUGUR-MC v1.3
  upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v1.0, AUGUR-ID v1.0]
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: [T-KS-1, T-KS-2, T-KS-3, T-KS-4, T-KS-5, T-KS-6]
  defers-in: [WM.D7, WM.D8, WM.D9, WM.D10, WM.D11, WM.D12, WM.D18, WM.D21, WM.D26, WM.D27,
              ONT.散列(Attr/D9), ID.IDO.1, ID.IDO.2, ID.IDO.3, ID.IDO.4, ID.IDO.6, ID.IDO.8]
  defers-out: [KDO.1, KDO.2, KDO.3, KDO.4, KDO.5, KDO.6, KDO.7]
  date: 2026-07-17
  author: Layer 4 Knowledge System 規格撰稿官（依 Constitution Steward 委辦之 Layer 4 起草程序）
  archive-path: specs/KNOWLEDGE-SYSTEM-SPECIFICATION-v0.1-draft.md
```

### CS.1 逐原則論證本文（七節，順序固定）[N]

> **CS.1-PA（Prime Axiom）**〔承接〕引 `AUGUR-MC v1.3 §1.1`。五元組（KS.20）與遞迴溯源（KS.70）落實「可追溯之 Evidence」；Confidence（§4）落實「不確定性可追溯」（`§1.1` 釐清句）；defeasible（KS.36）落實「錯誤可被新 Evidence 修正」。判準揭示：「可追溯」以引用鏈可機器遍歷（KS.70 判準）操作化；「不確定性可追溯」以 Confidence 攜 Grading Method（KS.32）操作化。

> **CS.1-P1（Reality First）**〔承接＋DEFER〕引 `§P1.E1`、`§P1.E2`、`§P1.E3`。來源非最高抽象於信任側（KS.72：Trust Rank 約束 Confidence 上限）、白名單完整性紀律（KS.78）；P1.E3 自然人→承 Layer 3 `§ID.42`，法規對應表 DEFER Layer 6。判準揭示：白名單依據可溯性（KS.78 判準）。

> **CS.1-P2（Representation Before Intelligence）**〔承接〕引 `§P2.E1`、`§P2.E3`、`§P2.E5`。候選斷言之 Confidence／Evidence 槽（KS.20、KS.77）、self-reported 紀律（KS.77）；P2.E5 fail-safe 判定主體 DEFER（KS.102）。判準揭示：self-reported 單獨升信之禁止（KS.77 判準）。

> **CS.1-P3（Identity Before Knowledge）**〔承接〕引 `§P3.E1`。Identity 槽為已解析（KS.23），本層不重定義 Layer 3 機制；identity resolution 狀態映入 L_C（KS.92）。判準揭示：provisional 賦高於 INSUF 而升格消費之禁止（KS.92 判準）。

> **CS.1-P4（Evidence Before Conclusion）〔核心〕**〔細化〕逐條見 Annex TR.A。**`§P4.E8` 為本層核心細化**（單一 L_C、可比較、傳播上限、消費約束、官方映射——解 AUD-03）；`§P4.E1` 五元組第五元 Confidence 落地（KS.20，解 AUD-03/AUD-16）；`§P4.E2` as-of 能力等級（§5，解 AUD-08）；`§P4.E3` supersede 形式化（§6，解 AUD-02）；`§P4.E5` 矛盾保存（§7）；`§P4.E6/E7` 遞迴溯源、信任分級、NoLaundering（§8）。判準揭示：每一評價性謂詞（「可比較」KS.30、「獨立」KS.75、「完備」KS.81、「可重放」KS.31、「as-of 可用」KS.42）附可判定判準（收錄 Annex EO）。

> **CS.1-P5（Accountability Before Action）**〔部分不適用＋DEFER〕引 `§P5.E2`、`§P5.W3`。行動治理／風險分級屬 L6；本層定完備性等級（KS.80）與 Confidence 消費約束（KS.35），門檻綁定 DEFER L6（KDO.2）；本層不定義 Action 六元組。判準揭示：本層對風險分級／門檻作實質定義即下侵（KS.101 判準）。

> **CS.1-EV-chain（§4 canonical chain）**〔承接〕引 `§4` EV.5（Evidence）、EV.6（Knowledge）為本規格之標準鏈落點；引 `AUGUR-WM v1.0 §WM.24`（節選連續性）。本規格機制化 EV.5→EV.6：Evidence 遞迴溯源（KS.70）、五元組（KS.20）為 EV.6 之結構落點；節選不跳節點。判準揭示：引用鏈完整性可機器稽核（KS.70／`§WM.34(a)`）。

### CS.2 已知緊張關係（`AUGUR-WM v1.0 §WM.42`）[N]

| T-id | 所涉條款 | 描述 | 緩解／狀態 |
|---|---|---|---|
| **T-KS-1** | KS.30、KDO.1/2 | 單一 L_C 須全系統可比較，然傳播聚合（L5）與門檻（L6）尚未定義。 | 本層定序與上限，具體聚合／門檻 DEFER；暫行保守（無 Confidence＝INSUF，KS.38）。非豁免事項。 |
| **T-KS-2** | KS.33、KS.46、`§A.36` | 數值機率（vintage=A3）與序數等級（近似可知）之時間／信度模型不對稱。 | 經單調 banding 映入單一 L_C（KS.33）＋as-of 能力等級調和（KS.46）。非豁免事項。 |
| **T-KS-3** | KS.31、`§P4.E4` | DETERMINISTIC 頂錨與「禁隱含 1.0」之張力。 | DETERMINISTIC 須明記可重放依據、仍 defeasible；非預設。非豁免事項。 |
| **T-KS-4** | KS.51、AUD-02 | raw 層 heal 覆寫（既有 LWW 制度化）與只失效不刪除之張力。 | Supersede Relation 形式化（覆寫前快照）；`§P4.E5` MUST NOT 不可豁免。非豁免事項。 |
| **T-KS-5** | KS.80、`§P5.E2` | 完備性等級（L4）與風險級門檻（L6）分屬二層。 | 本層定量尺，門檻綁定 DEFER L6；缺位預設不削弱。非豁免事項。 |
| **T-KS-6** | KS.83、`AUGUR-ID v0.1-draft` IDO.4 | IDO.4 之 resolution 演算實作經 ID 標為目標 L4，然本層讀其為 Layer 5 Reasoning 之 inference（KS.100）。 | 本層就未解析存量指標量測（完備性輸入）於 KS.83(i) 承接；resolution 演算實作 KS.83(ii) 明記 DEFER Layer 5（KDO.1）並附理由。定性分歧待 ID／KS 於各自升版時對齊；本層不代 L5 定義演算。非豁免事項。 |

豁免登記：`none`（waivers: []）。本規格無現行豁免；如有，依 `AUGUR-WM v1.0 §WM.33` 豁免狀態標記位置落實。

### CS.3 雙向 DEFER 承接表（`AUGUR-WM v1.0 §WM.43`）[N]

* **(a) 承接上層之掛鉤（defers-in）**：`AUGUR-WM v1.0 §D7`→§3；`§D8`→§5；`§D9`→§4；`§D10`→§6／§8；`§D22`→KS.80 增補款／KS.81(f)（KDI.18，RULING-2026-016）；`§D11`→§9；`§D12`（HOOK-03，L4 面向）→KS.84（＋§8/§9）；`§D18`→KS.25/KS.62（L7 機制 slice 對稱下放 KDO.5）；`§D21`→KS.78；`§D26`→KS.54；`§D27`→KS.45；`AUGUR-ONT v0.1-draft §ONT.2`／散列→KS.20/§4；`AUGUR-ID v0.1-draft` IDO.1→§4/§10、IDO.2→§3/§10、IDO.3→KS.26、IDO.4→KS.83（＋轉 L5 KDO.1／L5/L7 KDO.4）、IDO.6→§5、IDO.8→KS.25/KS.62。與 front-matter `defers-in` 欄及 Annex DI 三向對表。
* **(b) 下放下層之掛鉤（defers-out）**：KDO.1、KDO.2、KDO.3（HOOK-02/03 之 L5 面向）、KDO.4、KDO.5（`§D18` 之 L7 機制 slice）、KDO.6、KDO.7（見 Annex DO），與 front-matter `defers-out` 欄互為索引。原 KDO.HOOK02 已改編為 KDO.3、目標收斂為純 L5。

### CS.4 形式充分性（`AUGUR-WM v1.0 §WM.44`）[N]

依 `§WM.44` 判準自查：`AUGUR-MC v1.3` **全部** [N] 條款、`AUGUR-WM v1.0` **全部** [N] 條款、`AUGUR-ONT v0.1-draft` **全部** [N] 條款、`AUGUR-ID v0.1-draft` **全部** [N] 條款，均須對應至本規格至少一 [N] 條款、或明記 DEFER 掛鉤、或明記「不觸及」及理由。

* **P4 家族**：Annex TR.A 已就 `§P4.D`／`§P4.W1`／`§P4.E1`–`§P4.E8` **逐條完整枚舉**（本層核心，品質標竿）。
* **其餘 MC 條款**：Annex TR.B **逐條**枚舉（PA／P1／P2／P3／P5 各 E/W 條款、§0/§2/§4/§5/§6/§8 各條）。
* **WM／ONT／ID 全部條款**：Annex TR.C（WM.1–53＋Annex A A.0–A.59＋Annex D D0–D28）／TR.D（ONT.1–62＋Annex T T.0–T.91）／TR.E（ID.1–81＋IDO.0–8＋Annex L4）**逐條**枚舉落點（承接／細化／DEFER／不觸及＋理由）。

**逐條對應矩陣已完整枚舉——形式充分性成就**：`AUGUR-MC v1.3`／`AUGUR-WM v1.0`／`AUGUR-ONT v0.1-draft`／`AUGUR-ID v0.1-draft` 全部 [N] 條款 → 本規格落點之**逐條完整枚舉**（`§WM.44` 要求之機器可判完備對應矩陣）已於 Annex TR 作成。依 `§WM.44` 判準，形式充分性**已成就**；**Steward 充任認定業經作成，本規格自 2026-07-17 起生效**（Steward 裁決第 2026-005 號、AL-2026-009；見【地位】、Annex TR.Z），**殘餘生效阻卻已解消**。**實質充分性**仍由違憲審查程序（`AUGUR-MC v1.3 §8.2`）判斷，未因充任而終局確認；上層草案升版或條款增修時本矩陣對應列**必須**同步維護（KS.111 diff 檢查），否則聲明重回不完整。

---

## Annex EO [N] — 自創評價性謂詞判準彙整

> **EO.1（判準彙整表）[N]** 本規格自創或操作化之評價性謂詞，依 `AUGUR-MC v1.3 §8.3` 可判定性元規則，逐一附可判定判準：
>
> | 謂詞 | 出處 | 可判定判準 |
> |---|---|---|
> | 「可比較」 | KS.30 | 任兩值於 L_C 序（⊑）可判定 |
> | 「獨立」（Data Evidence） | KS.75 | provenance 鏈遞迴不含本系統 Computational Evidence ∧ 不共享上游 |
> | 「完備」（完備性等級） | KS.81 | 五維度（溯源終止／獨立 Data Evidence／未解假設數／OOS 驗證／未裁決衝突）可機器盤點 |
> | 「可重放」（DETERMINISTIC 依據） | KS.31 | 存在可重現之機械驗證引用 |
> | 「as-of 可用」 | KS.42、KS.44 | 承載表能力等級 ≥ A2 ∧ 通道時間屬性雙宣告完備 |
> | 「最弱環節」（NoLaundering） | KS.34、KS.73 | 證據鏈上 Confidence／Trust Rank 之 meet（下確界）可機器計算 |
> | 「高風險」（Action） | KS.76、KS.101、KS.84 | **DEFER Layer 6 風險分級表（KDO.2）；本層不判定**——本層僅定「高風險 Action 之證據要求結構」（KS.76），風險分級本身為 Layer 6 職掌 |
>
> **掃描—完備性義務（[N]，比照 `AUGUR-WM v1.0` Annex E1）**：本規格正文如增列自創或操作化之評價性謂詞，**必須**同步收錄本 EO.1 表；全文謂詞掃描與本表逐列對照，**未收錄且未附判準者採保守解釋**（存疑即不允許，`§8.3`）。此使 EO 對全文評價性謂詞之涵蓋完備性可機器驗證。
> **義務主體**：本規格、一切消費本規格謂詞之下層規格。**可判定判準**：全文評價性謂詞逐一於本表有列（或其判準明記 DEFER 落點）者為完備；本表每一謂詞之判準可機器適用；未收錄且未附判準之謂詞，採保守解釋（存疑即不允許，`§8.3`）。

---

*本規格計：正文條款 KS.1–KS.111（十位制保留區塊，空號為保留；KS.84 已啟用）、Annex CM（CM.0、CM.1(a)/(b)、CM.2）、Annex EV（EV.0–EV.3）、Annex CL（CL.0–CL.1）、Annex DI（KDI.0–KDI.17）、Annex DO（KDO.0–KDO.7；KDO.3、KDO.5 已啟用）、Annex L3U（L3U.0）、Annex L56（L56.0）、Annex TR（TR.0、TR.A–TR.E、TR.Z）、Annex CS 合規聲明（CS.1–CS.4）、Annex EO（EO.1）。全文以繁體中文為權威文本（§0.4）。本文件為 **v1.0 生效版本**，Steward 充任認定已作成，自 2026-07-17 起生效（Steward 裁決第 2026-005 號、AL-2026-009；`AUGUR-MC v1.3 §0.5`、【地位】、KS.110）；WM.44 逐條矩陣（Annex TR）已就 MC／WM／ONT／ID 全數逐條完成，形式充分性已成就，**殘餘生效阻卻已解消**；**實質**充分性之最終判斷仍屬 Steward `§8.2` 違憲審查程序。*

**核心產物索引 [I]**：Confidence 單一形式化語義＝§4（KS.30–KS.39）＋Annex CM（單一偏序格 L_C＋官方映射表，解 AUD-03 critical）；五元組欄位不變式＝§3（KS.20，第五元 Confidence 落地）；雙時間 as-of 能力等級＝§5（KS.40–KS.46，A0–A3，解 AUD-08）；supersede/tombstone＝§6（KS.50–KS.55，Supersede Relation 形式化，解 AUD-02）；矛盾保存＝§7；Evidence 分類法/溯源/信任分級/NoLaundering＝§8＋Annex EV；完備性等級＝§9＋Annex CL（DEFER 門檻至 L6）；identity claim Confidence 承接＝§10；L5/L6 分界＝§11＋Annex L56；DEFER 表＝Annex DI/DO；WM.44 矩陣＝Annex TR。

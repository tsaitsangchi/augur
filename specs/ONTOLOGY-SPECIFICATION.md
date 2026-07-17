# 《Augur Ontology Specification》

Augur Enterprise AI Operating System
本體論規格（Layer 2 — Ontology）
引用縮寫：**AUGUR-ONT**｜版本：**v1.0**（前版：v0.1-draft）
受 **AUGUR-MC v1.3** 全文約束（`AUGUR-MC v1.3 §0.6(a)` lex superior、`§0.5` 對照表 Layer 2 欄）
並受 **AUGUR-WM v1.0** 全文約束（`AUGUR-MC v1.3 §0.6(a)`、`AUGUR-WM v1.0 §WM.1`）

---

> ## 【地位】[N]
>
> 本文件為 **v1.0 生效版本**。Constitution Steward（tsaitsangchi）已於 2026-07-17 依 `AUGUR-MC v1.3 §0.5`、`§8.6` 作成**充任認定**（Steward 裁決第 2026-003 號，Amendment Log AL-2026-007）：本文件充任 `AUGUR-MC v1.3 §0.5` 對照表 Layer 2 欄所轄之「Ontology Specification」，`§0.1` 生效要件全部成就（Layer 對照表登錄、依 `AUGUR-WM v1.0 §WM.39` 之 Compliance Statement、`§WM.44` 形式充分性成就、linter 結構關卡通過），**自 2026-07-17 起生效**。`v0.1-draft` 原文歸檔於 `specs/ONTOLOGY-SPECIFICATION-v0.1-draft.md`；draft → v1.0 之變更僅限：版本欄、本【地位】節生效記錄、Annex CS front-matter spec-version，**無任何 [N] 條款實質變更、條款編號（ONT.{n}／T.{n}／DI.{n}／DO.{n}／EO.{n}／TM.{n}）不重排**。
>
> * 本文件全部 [N] 條款自生效日起對 Layer 3–7 規格產生規範效力；下層依 `AUGUR-ONT v1.0 §{條款}` 格式引用。
> * **實質充分性**之最終判斷仍屬 Steward 違憲審查程序（`AUGUR-MC v1.3 §8.2`），與已成就之形式充分性分屬二事；充任認定不排除嗣後之違憲審查。
> * 條款編號穩定性依 `AUGUR-MC v1.3 §8.6`、`AUGUR-WM v1.0 §WM.46`：永不重用、永不重排。
>
> 本【地位】節與 §0 全部約定為 [N] 規範內容，其效力與正文條款同（準用 `AUGUR-WM v1.0 §WM.53`）。

---

## 目錄 [I]

* §0 Document Status & Conventions（ONT.1–ONT.5、ONT.9）
* §1 Purpose & Position（ONT.6–ONT.8；ONT.5 位置條互見；本章敘述 [I]）
* §2 型別體系總則 Type System General Rules（ONT.10–ONT.13）
* §3 同一性判準體系 Identity Criteria（ONT.20–ONT.22）
* §4 Instance / Type 區分（ONT.30–ONT.31）
* §5 型別與世界關係／世界量（ONT.40–ONT.41）
* §6 對映 AUGUR-WM 領域 Profile（ONT.50）
* §7 Conformance & Continuity（ONT.60–ONT.62）
* Annex DI [N] — 承接上層之 DEFER 掛鉤（defers-in，DI.1–DI.3）
* Annex DO [N] — 下放下層之 DEFER 掛鉤（defers-out，DO.1–DO.4）
* Annex L3 [N] — 與 Layer 3（Identity System）之分界表
* Annex T [N] — 台股型別階層與同一性判準（T.1–T.61）
* Annex T-Map [N] — Annex A 世界概念 → 型別對映
* Annex TR [I] — 形式充分性追溯矩陣（AUGUR-MC／AUGUR-WM → ONT）
* Annex CS [N] — 本規格之 Constitutional Compliance Statement
* Annex EO [N] — 自創評價性謂詞判準彙整表（EO.1）

---

## §0 Document Status & Conventions（文件地位與約定）[N]

### 0.1 名稱、層級與生效條件

本文件名稱 **Augur Ontology Specification**（引用縮寫 AUGUR-ONT），層級 **Layer 2 — Ontology**，版本 **v1.0**（前版：v0.1-draft）。受 `AUGUR-MC v1.3` 全文約束，並受 `AUGUR-WM v1.0` 全文約束（Layer 2 之上層含 Layer 1，`AUGUR-MC v1.3 §0.6(a)`）。生效要件：`AUGUR-MC v1.3 §0.5` 對照表登錄（已具欄位）＋ Steward 充任認定（**已成就**，見【地位】）＋ 依 `AUGUR-WM v1.0 §WM.39` 之 Compliance Statement（Annex CS）；本規格之生效要件**已全部成就**（Steward 裁決第 2026-003 號，2026-07-17，AL-2026-007）。**生效日：2026-07-17**。實質充分性之最終判斷仍屬 Steward `§8.2` 違憲審查程序，與已成就之形式充分性分屬二事。下層引用格式：`AUGUR-ONT v{version} §{條款}`（§0.3）。

### 0.2 規範用語約定

本規格之規範用語與約束力等級，全文依 `AUGUR-MC v1.3 §0.2`：**必須**（MUST，絕對義務）、**不得**（MUST NOT，絕對禁止）、**應**（SHOULD，偏離須書面說明理由）、**得**（MAY，允許而不構成義務）。

### 0.3 條款編號系統

* 正文條款編號採 **ONT.{n}**；Annex 條款編號採 **T.{n}**（Annex T 型別階層）、**DI.{n}**（Annex DI，承接上層之掛鉤）、**DO.{n}**（Annex DO，下放下層之掛鉤）、**EO.{n}**（Annex EO，評價性謂詞判準）、**TM.{n}**（Annex T-Map 之表首治理條款，如 TM.0）。Annex L3 之列與 Annex T-Map 之資料列以其所引 ONT／T 編號為索引，不另立獨立條款號；TM.{n} 僅用於 T-Map 之表首治理條款本身，非逐列編號。
* 條款編號一經發布**永不重用、永不重排**；廢止條款保留編號並標注 **(repealed)**（準用 `AUGUR-MC v1.3 §8.6`、`AUGUR-WM v1.0 §WM.46`）。
* 下層引用本規格之格式：`AUGUR-ONT v{version} §ONT.{n}`；Annex 條款逐一為 `AUGUR-ONT v{version} §T.{n}`、`§DI.{n}`、`§DO.{n}`、`§EO.{n}`。
* 本規格引用憲章一律採 `AUGUR-MC v1.3 §{條款編號}` 格式；引用 Layer 1 一律採 `AUGUR-WM v1.0 §WM.{n}` / `§A.{n}` / `§D{n}` / `§E{n}` 格式。

### 0.4 權威語言聲明

本規格以**繁體中文版為權威版本**；規範性術語於正文中一律使用英文原詞（Reality、Observation、Representation、Identity、Evidence、Knowledge、Confidence、Action、Agent、Intelligence；及本規格細化構件之英文名 Type、Instance、Type Hierarchy、Identity Criterion、Subtype、Attribute schema），與 `AUGUR-MC v1.3 §0.4`、`AUGUR-WM v1.0 §0.4` 保持術語同一性。

### 0.5 條文效力標注

* 每一章節標注 **[N]（Normative）** 或 **[I]（Informative）**，全文適用。[N] 與 [I] 內容不一致時，依 `AUGUR-MC v1.3 §8.2` 以 Normative 為準。
* 本規格每一 [N] 條款標注其**憲章／Layer 1 錨定**與**三態型態**：**refines**（細化上位條款）、**carries**（承接上位不變式並給予型別層結構位置）、**hooks**（DEFER 掛鉤，載明目標 Layer 與授權條款），與 `AUGUR-WM v1.0 §0.5` 三態明文對映一致；複合模式以「＋」連接。
* 本規格每一 [N] 條款標注**義務主體**與**可判定判準**，使其可機器稽核（承接 `AUGUR-WM v1.0 §WM.34`）。

### 0.6 條款

> **ONT.1（從屬）[N｜carries｜`AUGUR-MC v1.3 §0.6(a)`、`§8.2`；`AUGUR-WM v1.0 §WM.1`]**
> 本規格全部內容從屬並不得違反 `AUGUR-MC v1.3` 與 `AUGUR-WM v1.0`；牴觸部分無效，經違憲認定之條款自認定日起無效，不得作為 Layer 3–7 規格之依據（`AUGUR-MC v1.3 §0.6(a)`、`§8.2`；`AUGUR-WM v1.0 §WM.1`）。
> **義務主體**：本規格自身及其後續修訂者。**可判定判準**：任一條款經 Steward 依 `AUGUR-MC v1.3 §8.2` 認定違憲、或經解釋認定與 `AUGUR-WM v1.0` 任一 [N] 條款不相容者，即為牴觸；認定前依較嚴格解讀原則處理（對系統許可較少、義務較重）。

> **ONT.2（細化不重定義）[N｜carries｜`AUGUR-MC v1.3 §2` 元規則；`AUGUR-WM v1.0 §WM.2`]**
> 本規格對 `AUGUR-MC v1.3 §2` 之十一個初始概念（Reality、Observation、Representation、Identity、Evidence、Knowledge、Intelligence、Agent、Action、Confidence、Evidence 通道）及 `AUGUR-WM v1.0` 新造構件（World Concept、World Concept Registry、Observation Channel、Observation Store、Domain Profile、世界關係、世界量）**僅為細化，不重新定義、不變更內涵、不另創同義歧稱**。
> 本規格新造術語限於下列——均為既有術語之細化構件，於首次出現處以一句式定義並標注上位術語：
> * **Type（型別）** ＝ 對一類世界實體、事件、狀態、關係或量之具名類屬位置，為 `AUGUR-MC v1.3 §2.3` Representation 及 `AUGUR-WM v1.0 §WM.8` 世界概念之細化構件（宣告「類屬」，別於 `AUGUR-WM` 之「存在」）。Type 與 World Concept 為**同一世界概念之兩個結構面向**：存在面屬 `AUGUR-WM v1.0 §WM.8`、類屬面屬本層（`§WM.9(b)` 結構權威共享）；Type **不取代亦不重述** World Concept 之存在宣告，故為細化而非同義歧稱（`AUGUR-MC v1.3 §2` 元規則）。
> * **Instance（實例／個體）** ＝ 繫結於某 Type 之單一世界個體，其權威指稱為 Identity（`AUGUR-MC v1.3 §2.4`），Type 為 Instance 之細化描述維度。
> * **Type Hierarchy（型別階層）** ＝ Type 間之上位／下位（parent／subtype）有序結構，為 Representation 之細化構件。
> * **Identity Criterion（同一性判準）** ＝ 對某 Type「憑何判定兩者為同一世界實體」之陳述，為 `AUGUR-MC v1.3 §P3.E3`、`AUGUR-WM v1.0 §WM.21(a)` 宣告槽位之填充構件。
> * **Subtype（子類）** ＝ 於某 Type 之下細分之下位 Type，繼承其上位之 Identity Criterion 骨架。
> * **Attribute schema（屬性 schema，概念層）** ＝ 某 Type 之屬性槽位之具名集合之概念位置（**僅概念槽位**，欄位設計 DEFER Layer 4）。
> * **Instance namespace（個體命名空間，概念層）** ＝ 某 Type 之個體集合於概念層之指涉空間，為 **Instance／Identity**（`AUGUR-MC v1.3 §2.4`）之細化描述位置（**僅概念層之 referent 空間相異性**；具體命名空間之結構與設計 DEFER Layer 3，`AUGUR-WM v1.0 §WM.20`、`§D5`，見 DO.2）。
> **義務主體**：本規格自身、Annex T 及本規格後續修訂者。**可判定判準**：本規格任一術語定義文句，刪除後不影響 `AUGUR-MC v1.3 §2` 各定義與 `AUGUR-WM v1.0` 各構件定義之字面適用者為細化；反之為重定義（禁止）。就此有解釋爭議者，依 `AUGUR-MC v1.3 §8.1` 由 Steward 裁決，裁決前依較嚴格解讀處理。

> **ONT.3（管轄與 DEFER 紀律）[N｜carries｜`AUGUR-MC v1.3 §0.5`；`AUGUR-WM v1.0 §WM.3`]**
> 本規格為 Layer 2 唯一所轄規格，不自行擴張管轄。本規格僅承接 `AUGUR-WM v1.0 Annex D` 中目標含 Layer 2 之掛鉤（見 Annex DI）；凡 `AUGUR-MC v1.3` 明定定義權屬 Layer 3–7 之事項，本規格**僅得**設 DEFER 下放條款（明載目標 Layer 與授權條款，見 Annex DO），**不得**代行定義。
> **義務主體**：本規格自身。**可判定判準**：本規格任一條款對 Annex DO 所列 DEFER 事項作成實質定義（即該定義文句可被下層直接消費而無須下層另為定義，尤指：直接鑄造 identifier、直接採認判準使之生效於 resolution、直接執行 merge/split/retire）者，違反本條（下侵）。

> **ONT.4（概念層獨立性＋刪名測試承接）[N｜carries｜`AUGUR-MC v1.3 §0.6(b)`；`AUGUR-WM v1.0 §WM.4`、`§WM.8`]**
> 本規格**不得**引用 Layer 5–7 執行層構件（含任何資料庫產品、Agent Runtime、外部介面技術、特定 AI model）作為 Type 或 Identity Criterion 之定義依據。Type 定義**不得**以任何來源之 schema、表結構、欄位命名或 API 行為反推導出（承接 `AUGUR-WM v1.0 §WM.8` 之 Layer 2 落地：`AUGUR-WM v1.0 §WM.8` 明列 Layer 2 Ontology 規格作者為義務主體）。
> **可判定判準（刪名測試）**：凡刪去某產品名、供應商名或資料集名後，Type 或 Identity Criterion 之概念內涵不變者，為指名（合法，僅得為 Observation Channel 之指名）；內涵改變者，為定義依據（禁止）。本測試適用於本規格全文（含 Annex T）。
> **義務主體**：本規格自身、Annex T、本規格後續修訂者。

> **ONT.5（[N]/[I] 標注、三態與位置）[N｜refines｜`AUGUR-MC v1.3 §0.6(c)`；`AUGUR-WM v1.0 §WM.5`、`§WM.9(b)`]**
> 本規格為「型別層（type layer）」：`AUGUR-WM v1.0` 為「存在層（existence layer）」，Layer 3 Identity System 為「個體層（instance/identifier layer）」；三層不得互相僭越（Layer 3 分界見 Annex L3）。每一 [N] 條標注憲章／Layer 1 錨定、三態、義務主體與可判定判準；本規格承接 `AUGUR-WM v1.0 §WM.9(b)` **結構權威**之型別側——世界中存在何種實體、事件、狀態及其關係，由 `AUGUR-WM v1.0`（含 Annex A）與本層**共同宣告**，本層宣告其「類屬」。
> **義務主體**：本規格自身。**可判定判準**：本規格每一 [N] 條款均載明錨定、三態、義務主體與可判定判準；缺任一者為文件缺陷，依 `AUGUR-MC v1.3 §8.2` 採較嚴格解讀處理至修正為止。

> **ONT.9（引用格式與編號穩定性）[N｜carries｜`AUGUR-MC v1.3 §8.6`、`§0.3`；`AUGUR-WM v1.0 §WM.46`]**
> 下層引用本規格一律採 §0.3 所定格式。本規格條款編號一經發布**永不重用、永不重排**；廢止條款保留編號並標注 (repealed)。
> **義務主體**：本規格後續修訂者、Layer 3–7 規格作者。**可判定判準**：版本間 diff 檢查——任一既發布編號於後版消失或改指他文者違反本條。

---

## §1 Purpose & Position（任務與定位）[N]

### 1.1 敘述 [I]

`AUGUR-WM v1.0` 已「宣告世界有何物」（存在宣告，`§WM.23`）；本層負責「宣告這些物**是什麼類、如何分類、憑何判定同一、繫結對象屬個體或類型**」——即 `AUGUR-MC v1.3 §P3.W2`（完整分類體系）與 `§P3.E3`（同一性判準／instance-type 區分）之**制定**（formulate），但**不鑄造 identifier、不採認判準生效、不定生命週期機制**（此三者屬 Layer 3，見 Annex L3）。

### 1.2 條款 [N]

> **ONT.6（任務）[N｜refines｜`AUGUR-MC v1.3 §P3.W2`、`§P3.E3`；`AUGUR-WM v1.0 §WM.23`、`§WM.21`、`§WM.9(b)`]**
> 本規格之任務為：具體化 `AUGUR-MC v1.3 §P3.W2` 完整分類體系與 `§P3.E3` 同一性判準／instance-type 區分於世界模型之落地，承接 `AUGUR-WM v1.0 §WM.23`（D1 完整分類體系）、`§WM.21(a)(b)`（D2 判準宣告槽位與 instance/type 標記位置之制定）、`§WM.9(b)`（結構權威之型別側），以可供 Layer 3–7 合規審查之規範性語言（`AUGUR-MC v1.3 §0.2` 用語等級）陳述型別體系不變式。
> **義務主體**：本規格自身。**可判定判準**：本規格每一 [N] 條款可解析至 `AUGUR-MC v1.3` 或 `AUGUR-WM v1.0` 之至少一條款；不可解析者不具規範效力。

> **ONT.7（定位：三層不僭越）[N｜carries｜`AUGUR-MC v1.3 §0.5`、`§0.6(a)`；`AUGUR-WM v1.0 §WM.3`、`§WM.23`]**
> 本層產出「**類型與判準的定義文本**」；Layer 1 產出「**存在宣告**」；Layer 3 產出「**個體的永久參照（identifier）與其一生的機器機制**」。本層**不得**產出可由 Layer 3 直接鑄造 identifier 或直接執行 merge/split/retire 而無須 Layer 3 另為定義之條款（否則為下侵，違 ONT.3）。
> **義務主體**：本規格自身、Layer 3 規格作者。**可判定判準**：Annex L3 分界表每列之「本層得為」欄與「Layer 3 專屬」欄無交集，且本層任一條款不落入「Layer 3 專屬」欄者為合規。

> **ONT.8（型別定義不得由來源反推）[N｜carries｜`AUGUR-MC v1.3 §6 F1`、`§P1.W1`；`AUGUR-WM v1.0 §WM.7`、`§WM.8`]**
> 本層之 Type 與 Type Hierarchy **必須**優先描述 Reality，**不得**優先適配任何現有資料來源（承接 `AUGUR-WM v1.0 §WM.7`）；Type 定義中出現來源表名、欄名或端點名而未通過 ONT.4 刪名測試者，推定違反本條（承接審計 **AUD-01**：資料來源 schema 即系統最高抽象為 F1 教科書式命中；本層為其化解之型別側）。
> **義務主體**：本規格自身、Annex T、Layer 3–7 消費者。**可判定判準**：ONT.4 刪名測試之逐 Type 適用；推定得由 Steward 附理由推翻。

---

## §2 型別體系總則（Type System General Rules）[N]

> **ONT.10（頂層本體範疇）[N｜refines｜`AUGUR-MC v1.3 §P3.W2`；`AUGUR-WM v1.0 §WM.23`、`§WM.36`、`§WM.8`]**
> Type Hierarchy 以下列頂層範疇為根，對映 `AUGUR-WM v1.0 §WM.36` Registry 歸類閉集（實體／事件／狀態／關係／量）：
> * **Entity（實體）**、**Event（事件）**、**State（狀態）**、**Relation（關係）**、**Quantity（量）**。
> Entity 再依 `AUGUR-MC v1.3 §P3.W2` 之開放四分為頂層 Subtype：**PhysicalEntity**、**AbstractEntity**、**DynamicEntity**、**AgentiveEntity**。
> **DynamicEntity 範圍之重解與 Event/State 之定位**：`AUGUR-MC v1.3 §P3.W2` 於 Dynamic Entity 例示列有「Event、Process、State」；本層依 `AUGUR-WM v1.0 §WM.36` 歸類閉集（實體／事件／狀態／關係／量並列）行使 `§WM.23` Layer 2 完整分類權，將 **DynamicEntity 重解為「具生命週期之實體」**（如 DerivativeContract、Warrant），而將 **Event、State 另立為與 Entity 並列之頂層範疇**。此重定位下，Event/State 之個體仍具 Identity（非刪減四類 Entity 或五頂層範疇，合 ONT.11）。**兩切面調和**：五頂層範疇（實體／事件／狀態／關係／量）為 `AUGUR-WM v1.0 §WM.36` Registry 歸類閉集之承接切面，Entity 四分（Physical/Abstract/Dynamic/Agentive）為 `AUGUR-MC v1.3 §P3.W2` 之承接切面；二者為**不同分類切面**（前者為頂層並列閉集，後者為 Entity 之開放四分），本層之 Event/State 頂層化不否定 `§P3.W2` 將其列為 Dynamic Entity 例示之字面，而係於 `§WM.36` 切面另立並列範疇，非字面矛盾。本歧異依 `AUGUR-WM v1.0 §WM.42` 於 Annex CS §CS.8 OT-4 如實揭露。
> **義務主體**：本規格自身、Annex T。**可判定判準**：Annex T 每一 Type 之 parent 可經有限步上溯至上開五範疇之一（Entity 之 Type 並上溯至四分之一）者為合規；上溯不終止於閉集者違反本條。

> **ONT.11（開放例示之封閉化紀律）[N｜carries｜`AUGUR-MC v1.3 §P3.W2`（「包括但不限於」）、`§8.5(b)(ii)` 精神；`AUGUR-WM v1.0 §WM.23`]**
> `AUGUR-MC v1.3 §P3.W2` 四類 Entity 為「包括但不限於」之開放例示。本層**得**增列頂層 Entity Subtype 或跨範疇 Type，但**不得刪減**四類 Entity 與五頂層範疇；新增頂層範疇或頂層 Entity Subtype 者，**必須**附憲章判準論證（準用 `AUGUR-MC v1.3 §8.5(b)(ii)` 之「更完整描述五項不變核心」精神），並收錄 Annex EO（如引入評價性謂詞）。
> **義務主體**：本規格後續修訂者。**可判定判準**：任一頂層範疇／頂層 Entity Subtype 之新增，其條文附有指向 `AUGUR-MC v1.3`／`AUGUR-WM v1.0` 之判準論證者為合規；刪減四類 Entity 或五頂層範疇者違反本條。

> **ONT.12（型別定義三要件）[N｜refines｜`AUGUR-MC v1.3 §P3.E3`、`§P3.W2`；`AUGUR-WM v1.0 §WM.21(a)(b)`、`§WM.23`]**
> 每一 Type **必須**宣告下列三要件，缺任一者 Type 定義不完整、不生效力：
> * (a) **上位範疇（parent）**：其直接上位 Type 或頂層範疇（ONT.10）；
> * (b) **同一性判準（Identity Criterion）**：填入 `AUGUR-WM v1.0 §WM.21(a)` 宣告槽位之判準內容（制定，ONT.20）；
> * (c) **instance/type 繫結語義**：其個體屬 Instance、其類屬標記屬 type 之區分語義（ONT.30）。
> **義務主體**：本規格自身、Annex T、本規格後續修訂者。**可判定判準**：Annex T 每一 Type 條含 (a)(b)(c) 三欄且各欄可解析者為合規；缺任一欄者該 Type 定義無效。

> **ONT.13（存在宣告 ↔ 分類體系接合）[N｜refines｜`AUGUR-MC v1.3 §P1.E2`；`AUGUR-WM v1.0 §WM.23`、`§WM.37`、`§WM.14`]**
> 本層之 Type Hierarchy **必須**可將 `AUGUR-WM v1.0 Annex A` 每一存在宣告之世界概念解析至**恰一個主型別節點**（其類屬，`AUGUR-WM v1.0 §WM.23` 切分判準之型別側：Layer 1 記載存在，Layer 2 記載類屬）。**主型別節點 vs 附帶關係型別**：部分實體存在宣告於其宣告內另涵一項一級世界關係（如 `§A.4` 日曆日↔交易日、`§A.57` 發行關係、`§A.7`／`§A.8` 標的關係、`§A.2` 名冊成員關係）；該關係之型別（T-⑤，T.50–T.53）為由該實體存在宣告**衍生之附帶關係型別**，於 Annex T-Map 以括號標注，**非該存在宣告之主型別節點**，不構成第二個主映射（其自身另於 T-⑤ 立為一級關係型別）。對映見 Annex T-Map。本接合為 `AUGUR-WM v1.0 §WM.37`（唯一權威表徵落實義務）之型別側前提。
> **義務主體**：本規格自身、Annex T-Map 維護者。**可判定判準**：①部存在宣告條之封閉集 ＝ {`§A.1`–`§A.30`, `§A.57`, `§A.58`}（共 32 條）；`§A.31`–`§A.56`、`§A.59` 為 `AUGUR-WM v1.0` 正文之領域適用／評價性謂詞／程序／OPEN／涉自然人宣告，非①部存在宣告，不對映主型別節點。Annex T-Map 中該封閉集每一存在宣告條解析至**恰一主型別節點**且可雙向解析者為合規；解析至零個主型別節點者違反本條（附帶關係型別之括號標注不計為多重主映射；跨範疇歸屬未定者，須登錄 Annex T-Map 之 A-OPEN 待決欄，禁止下層以隱含假設消費）。

---

## §3 同一性判準體系（Identity Criteria）[N]

> **ONT.20（判準宣告義務）[N｜hooks＋refines｜`AUGUR-MC v1.3 §P3.E3`；`AUGUR-WM v1.0 §WM.21(a)`、`§A.31`、`§A.32`、`§A.54`；目標本層制定／Layer 3 採認]**
> 本層**必須**為每一 Type **制定**（formulate）其 Identity Criterion，填入 `AUGUR-WM v1.0 §WM.21(a)` 之宣告槽位（承接 `§A.31` 槽位設置、`§A.32`／`§A.54` 候選素材）。制定＝陳述判準內容；**不含**使判準生效於 resolution（該效力屬 Layer 3 採認，ONT.21）。
> **義務主體**：本規格自身、Annex T。**可判定判準**：Annex T 每一 Type 條之 Identity Criterion 欄非空且其陳述可機器解析為「同一 iff〔可判定條件式〕」形式者為合規；空白或僅為描述語者違反本條。

> **ONT.21（判準效力與 Layer 3 採認之封印）[N｜hooks｜`AUGUR-MC v1.3 §P3.E3`；`AUGUR-WM v1.0 §WM.21(e)`、`§D2`、`§D6`；目標 Layer 3]**
> 本層 Identity Criterion 為 [N] **型別定義性陳述**（制定），惟其**用於 resolution 之操作效力**須經 Layer 3 **採認**（adopt）方生效（接續 `AUGUR-WM v1.0 §WM.21(e)` 效力封印）。採認前，涉該 Type 之 Identity 引用一律採保守解釋，**視為未解析**（provisional，`AUGUR-WM v1.0 §WM.21(d)`、`§WM.33`）。本條下放 Layer 3（DO.1；承接 `AUGUR-WM v1.0 §D2`、`§D6`）。
> **義務主體**：本規格自身（封印標注）、Layer 3 規格作者（採認）、涉該 Type 之一切消費者。**可判定判準**：本層每一 Identity Criterion 附封印句「經 Layer 3 採認前不生 resolution 效力」者為合規（**T.0 之總括封印句視同 Annex T 每一 Identity Criterion 各附封印句，滿足本逐條要求**；個別 T.n 條得不重述）；下層在無 Layer 3 採認紀錄下將涉該 Type 之 Identity 引用視為已解析者，違反本條。

> **ONT.22（外部識別碼非 identifier）[N｜carries｜`AUGUR-MC v1.3 §2.4`；`AUGUR-WM v1.0 §WM.21(c)`、`§WM.20`、`§A.33`、`§A.54`；承接審計 AUD-04／AUD-06]**
> 一切外部來源識別碼（供應商證券代碼、series_id、ISIN、統一編號等）為某 Type 個體之 Identity 之**指涉資訊**（可供 Identity Resolution 之資訊），**非**系統鑄造之 identifier（`AUGUR-WM v1.0 §WM.20`／`§WM.22` 意義）；跨體系同一性一律為 **identity claim**（`AUGUR-MC v1.3 §2.4`，受 P4 約束之 Knowledge；承接 `AUGUR-WM v1.0 §WM.21(c)`、`§A.33`）。**Type 由本層宣告，不得由消費端 regex 臨場判定**（承接 **AUD-04**「同一字串空間被各消費者臨場判定實體類型」、**AUD-06**「無跨來源同一性判準宣告、零繫結機制」）。identity claim 一級表介面與 identifier 鑄造下放 Layer 3（DO.2；承接 `AUGUR-WM v1.0 §D3`、`§D5`）。
> **義務主體**：本規格自身、Annex T、Layer 3–7 消費者。**可判定判準**：任一 Type 個體之權威繫結解析至系統 Identity（其外部識別碼繫結為 identity claim／alias）者為合規；以外部識別碼裸字串直接充當 Type 個體身份、或以消費端 regex 臨場判定 Type 者違反本條。

---

## §4 Instance / Type 區分 [N]

> **ONT.30（繫結對象標記語義）[N｜refines｜`AUGUR-MC v1.3 §P3.E3`；`AUGUR-WM v1.0 §WM.21(b)`]**
> 本層定義 `AUGUR-MC v1.3 §P3.E3` 之 instance/type 標記語義，填入 `AUGUR-WM v1.0 §WM.21(b)` 標記位置：Knowledge 之繫結對象屬**個體（Instance）**或**類型（type）**必須可判定區分。Instance 繫結一個世界個體（其權威指稱為 Identity）；type 繫結一個 Type 節點（Type Hierarchy 中之類屬位置）。標記之存續／解析落實下放 Layer 3（DO.4；`AUGUR-WM v1.0 §D2`、`§D4`）。
> **義務主體**：本規格自身、Annex T、Layer 3–7 消費者。**可判定判準**：任一 Knowledge 元素之繫結對象攜帶 instance 或 type 標記且該標記可解析至 Annex T 之個體命名空間或 Type 節點者為合規；未標記或不可解析者違反本條。

> **ONT.31（型別個體命名空間之概念層隔離）[N｜refines｜`AUGUR-MC v1.3 §P3.E3`、`§P3.W1`；`AUGUR-WM v1.0 §WM.19`、`§A.3`；承接審計 AUD-04]**
> 不同頂層範疇與不同 Type 之個體命名空間（Instance namespace，概念層，ONT.2）**必須於概念上隔離**（`AUGUR-WM v1.0 §A.3`：識別欄位相同不推定實體類型相同；`§WM.19`）。**封印**：本層僅要求**概念層 referent 空間之相異性**，**不課予 identifier 任何編碼或命名空間結構義務**；具體命名空間之結構、鑄造與設計 DEFER Layer 3（`AUGUR-WM v1.0 §WM.20`、`§D5`，見 DO.2、Annex L3）。**禁止型態**（承接 **AUD-04**）：（i）將產業分類名（如 'Automobile'、'Tourism'）或指數代號（如 'TAIEX'、'TPEx'）混入個股（Security）個體命名空間；（ii）EconomicIndicator／MacroDimensionQuantity（T.60／T.61，series_id 空間）與 Security（T.1，stock_id 空間）為**互斥個體命名空間**，跨來源同一以 Registry 世界量同一性宣告（`AUGUR-WM v1.0 §WM.15`）或 identity claim（`§A.33`）繫結，禁以裸字串或消費端跨表 join 推定同一。具體隔離：IndustryClassification（T.24）之節點為 **type**、Security（T.1）之個股為 **Instance**、Index（T.2）為**另一** Instance 命名空間；三者不共用個體命名空間。
> **義務主體**：本規格自身、Annex T、Layer 3 規格作者、Layer 3–7 消費者。**可判定判準**：任一個體參照可解析至恰一 Type 之個體命名空間者為合規；同一字串同時被解析為二個以上 Type 之個體、或 type 節點被當 Instance 消費者違反本條。

---

## §5 型別與世界關係／世界量 [N]

> **ONT.40（世界關係為一級型別範疇）[N｜refines｜`AUGUR-WM v1.0 §WM.8`；`AUGUR-MC v1.3 §2.3`]**
> 世界關係（`AUGUR-WM v1.0 §WM.8`：世界實體間隨時間取值之一級具名關係）為 Type Hierarchy 之頂層範疇 Relation（ONT.10）。其 Identity Criterion 以「**關係型別 × 端點 Identity 有序組 × valid time**」制定；端點 Identity 之效力封印同 ONT.21。
> **義務主體**：本規格自身、Annex T（T-⑤）。**可判定判準**：Annex T 每一 Relation Type 之 Identity Criterion 含關係型別、端點有序組、valid time 三要素者為合規；缺任一者違反本條。

> **ONT.41（世界量為維度索引型別）[N｜refines｜`AUGUR-WM v1.0 §WM.8`、`§WM.15`、`§A.10`；hooks｜目標 Layer 4（`§D21`）]**
> 世界量（`AUGUR-WM v1.0 §WM.8`：以維度索引、隨時間取值之世界狀態量）為 Type Hierarchy 之頂層範疇 Quantity（ONT.10）。其 Identity Criterion 以「**量種 × 維度值**」制定；維度全集以白名單制定，**維度值臆測禁止**（承接 `AUGUR-WM v1.0 §A.10`）；世界量同一性以 Domain Profile／Registry 明文宣告為準（`§WM.15`：無宣告即非同一）。白名單之**取得機制**（來源動態列舉→官方文檔種子→名冊）非本層事項，下放 Layer 4（見 Annex DO 散列項，`AUGUR-WM v1.0 §D21`）。
> **義務主體**：本規格自身、Annex T（T-⑥）、Layer 4 消費者。**可判定判準**：Annex T 每一 Quantity Type 之 Identity Criterion 含量種與維度（維度取白名單）者為合規；以臆測維度值定義同一者違反本條。

---

## §6 對映 AUGUR-WM 領域 Profile [N]

> **ONT.50（規範性對映義務）[N｜refines｜`AUGUR-MC v1.3 §P1.E2`；`AUGUR-WM v1.0 §WM.37`、`§WM.36`、`§WM.23`；hooks｜Registry 條目屬系統狀態，DEFER Layer 4/7（`§D18`）]**
> 本層**必須**建立 `AUGUR-WM v1.0 Annex A` 世界概念 → Layer 2 Type 節點之**規範性對映**（Annex T-Map），每列可雙向解析。本對映為 `AUGUR-WM v1.0 §WM.37`（唯一權威表徵落實義務）之型別側落地：為每一已註冊世界概念指定其 Type 節點，使 Layer 4–7 得於該 Type 上落實唯一權威表徵。Registry 之**具體條目**為系統狀態（`AUGUR-WM v1.0 §WM.36`），非本規格條文，其實作載體 DEFER Layer 4/7（引 `AUGUR-WM v1.0 §D18`）。
> **義務主體**：本規格自身、Annex T-Map 維護者。**可判定判準**：Annex T-Map 每列（世界概念 ↔ Type 節點）雙向可解析、且涵蓋 `AUGUR-WM v1.0 Annex A ①` 全部存在宣告條者為合規；有存在宣告條未對映且未列 A-OPEN 者違反本條。

---

## §7 Conformance & Continuity（合規與存續）[N]

> **ONT.60（版本語義與型別存續不變式）[N｜carries｜`AUGUR-MC v1.3 §8.6`；`AUGUR-WM v1.0 §WM.22`、`§WM.13`、`§WM.46`]**
> 準用 `AUGUR-MC v1.3 §8.6` 版本語義：Type 體系之實質變更（變更任一 Type 之 parent、Identity Criterion 要素、instance/type 語義，或增刪頂層範疇）＝**major**；新增 Subtype 或 Annex T-Map 對映列＝**minor**（依治理程序議決）；編輯修正＝**patch**。
> **關鍵設計不變式（承接 `AUGUR-WM v1.0 §WM.22`、`§WM.13(i)(ii)`）**：本層 Type 體系之任何版本變更**不得中斷任何 Identity 之存續**、**不得刪除歷史 Type**（廢止者保留編號並標 (repealed)）；**Type 重分類**（如 OT-1 之 Security 由「Physical Entity」描述語重分類為 AbstractEntity/FinancialInstrument）**不改任何個體 Identity**。
> **義務主體**：本規格後續修訂者、一切 Type 體系變更之提案者。**可判定判準**：任一 Type 體系變更後，變更前存在之全部 Identity 仍可解析、全部歷史 Type 編號仍存在者為合規；任一 Identity 於變更後不可解析、或歷史 Type 編號消失者違反本條。

> **ONT.61（審查與豁免承接）[N｜carries｜`AUGUR-MC v1.3 §8.2`、`§8.4`、`§8.1`；`AUGUR-WM v1.0 §WM.47`]**
> 本規格受 `AUGUR-MC v1.3 §8.2` 違憲審查程序約束。本規格全部「不得」（MUST NOT）義務**不得豁免**（`AUGUR-MC v1.3 §8.4`）；其餘 [N] 義務之豁免依 `AUGUR-MC v1.3 §8.4` 及治理附則（生效後）辦理，附則生效前依 `AUGUR-MC v1.3 §8.1` 缺位預設規則，以 Steward 書面裁決行之。本規格同位階條款衝突視為文件缺陷，修正前採較嚴格解讀。
> **義務主體**：Steward、本規格之一切消費者。**可判定判準**：豁免申請所涉之個別義務文句含「不得」者不受理；同條款內之「必須／應」義務文句得單獨申請豁免。

> **ONT.62（合規聲明義務）[N｜carries｜`AUGUR-MC v1.3 §8.3`；`AUGUR-WM v1.0 §WM.39`–`§WM.45`]**
> 本規格內含 Constitutional Compliance Statement（Annex CS），依 `AUGUR-WM v1.0 §WM.39–45` **正式格式**作成（非暫行模板，`§WM.45`：本聲明作成於 Layer 1 生效日〔2026-07-16〕之後，必須用正式格式）。無有效聲明之本規格不生效力（`AUGUR-MC v1.3 §8.3`）。
> **義務主體**：本規格自身、本規格後續修訂者。**可判定判準**：Annex CS 之 front-matter 全欄俱全（`AUGUR-WM v1.0 §WM.40`）＋七節論證存在（`§WM.41`）＋緊張關係節存在（`§WM.42`）＋雙向 DEFER 表存在（`§WM.43`）＋形式充分性自查存在（`§WM.44`）者為合規；缺任一者聲明不完整。

---

# Annex DI [N] — 承接上層之 DEFER 掛鉤（defers-in）

> **DI.0（承接義務）[N]** 本表每列承接 `AUGUR-WM v1.0 Annex D` 一列（目標含 Layer 2 者），依 `AUGUR-WM v1.0 §D0`、`§WM.43` 於本層指定承接條款。
> **義務主體**：本規格自身。**可判定判準**：本表每列之「本層承接條款」欄可解析至本規格既存 [N] 條款；且與 Annex CS front-matter `defers-in` 欄雙向可解析。

| # | 承接之 AUGUR-WM 掛鉤 | WM 條款 | 憲章依據 | 本層承接條款 | 承接方式 |
|---|---|---|---|---|---|
| **DI.1** | **D1** — Identity 實體類型**完整分類體系** | `AUGUR-WM v1.0 §WM.23` | `AUGUR-MC v1.3 §P3.W2` | ONT.10–12、Annex T（T.1–T.61） | 定義（頂層五範疇＋Entity 四分＋台股具體 Type） |
| **DI.2** | **D2** — 每類 Identity 同一性判準之**制定**；instance/type 分類（**採認**部分屬 Layer 3，見 Annex L3、DO.1） | `AUGUR-WM v1.0 §WM.21(a)(b)(e)` | `AUGUR-MC v1.3 §P3.E3` | ONT.20–22、ONT.30–31、Annex T | 定義（制定判準＋instance/type 語義）；效力封印移交 Layer 3 |
| **DI.3** | **D20** — 領域完整本體（`AUGUR-WM v1.0 Annex A` 錨定概念之**細分類、屬性、關係**） | `AUGUR-WM v1.0 §WM.23`、`§A（①部）` | `AUGUR-MC v1.3 §P3.W2` | Annex T、Annex T-Map、ONT.40–41 | 定義（每一存在宣告之型別化、Subtype、Attribute schema **概念槽存在性**〔欄位具名集合與設計 DEFER Layer 4，見 T.0／Annex DO 散列項〕、關係／量 Type） |

**同時承接（carries，非 DEFER；本層為 `AUGUR-WM v1.0` 明列之 Layer 2 義務主體）**：`§WM.8`（結構獨立性，明列 Layer 2 作者）、`§WM.9(b)`（結構權威共享）、`§WM.13`、`§WM.14`、`§WM.19`、`§WM.22`（存續跨 Ontology 變更——約束本層 Type 變更不得中斷 Identity，落於 ONT.60）、`§WM.23`、`§WM.26`（自反性，落於 T.28）、`§WM.33`、`§WM.36`、`§WM.37`。本層對此等條款**不得**使其不可表達或不可機器稽核（`AUGUR-WM v1.0 §WM.16`、`§WM.34` 之下層存續義務）。

**承接自 `AUGUR-WM v1.0 Annex A` 之具體 [I] 封印素材（本層將其型別化）**：`§A.31` 槽位設置、`§A.32` 候選判準記載（Security／Index／DerivativeContract／EconomicIndicator／MarketParticipant）、`§A.57` Issuer 同一性判準與發行關係、`§A.58` MarketTrade/DailyBar、`§A.21` CorporateAction、`§A.54` OPEN-1（stock_id 時間穩定性之實體層型別化——**採認** DEFER Layer 3，DO.1／`§D6`）。此等素材受 `AUGUR-WM v1.0 §WM.21(e)` 效力封印：本層制定，Layer 3 採認前不生 resolution 效力。

**承接自 `AUGUR-WM v1.0 Annex A` 之 [N] 條款（別於上開 [I] 封印素材，性質不同）**：`§A.33`（第二識別體系之繫結，AUD-06「跨來源同一性判準宣告、禁以欄位字面相等推定同一」之規範錨）為 Annex A **[N] 規範條款**（非 [I] 素材）；本層於 ONT.22 承接，落點 T.6／T.28／T.42／T.60 之 identity claim 繫結。此承接為 [N] 規範承接，不併入上開 [I] 封印素材清單。

---

# Annex DO [N] — 下放下層之 DEFER 掛鉤（defers-out）

> **DO.0（下放紀律）[N]** 本表每列為本層明示不定義、下放目標 Layer 之掛鉤（ONT.3）。目標 Layer 規格作成時應於其 Compliance Statement 之 `defers-in` 欄承接對應列。
> **義務主體**：本規格自身（設掛鉤）、目標 Layer 規格作者（承接）。**可判定判準**：本表每列與 Annex CS front-matter `defers-out` 欄雙向可解析；本層無任一條款對本表所列事項作成可被下層直接消費之實質定義（ONT.3 下侵判準）。

| # | 本層來源條款 | 下放事項 | 目標 Layer | 憲章／WM 依據 | 審計對應 |
|---|---|---|---|---|---|
| **DO.1** | ONT.21、T.1（Security 判準）、T.20（Issuer 判準） | 同一性判準之**採認**（使生效於 resolution）；resolution 演算／時限指標 | Layer 3 | `AUGUR-MC v1.3 §P3.E3`；ONT.21／T.20（Issuer）→`AUGUR-WM v1.0 §D2`（`§WM.21(e)`）；T.1／T.90（Security，代碼重用 OPEN-1）→`§D6`（`§A.54`）；resolution 演算／時限→`§D4` | AUD-04 |
| **DO.2** | ONT.22、T.42／T.6／T.1（Security↔ISIN／外部代碼 claim）、T.28（模型／宇宙自身之外部代碼）、T-⑤ 端點 | **identity claim 一級表介面**（identifier 對、判準引用、Evidence、Confidence）；identifier **鑄造**、結構、命名空間設計 | Layer 3 | `AUGUR-MC v1.3 §2.4`、`§P3.E2`；`AUGUR-WM v1.0 §D3`、`§D5` | AUD-04、AUD-06 |
| **DO.3** | T.1、T.3、T.4、T.5、T.34（生命週期屬性宣告） | 生命週期**事件表**與 **merge/split/retire/relist 機制、tombstone、去識別化、identity lineage** | Layer 3 | `AUGUR-MC v1.3 §P3.E2`；`AUGUR-WM v1.0 §WM.22`、`§D3` | AUD-05 |
| **DO.4** | ONT.30、T.24、T.42、T.43（instance/type 標記；point-in-time 狀態；身份屬性 as-of 化） | 標記之**存續／解析落實**、provisional 狀態解析；**身份屬性 as-of 版本化**（時間繫結） | Layer 3 | `AUGUR-MC v1.3 §P3.E1`；`AUGUR-WM v1.0 §D4` | AUD-07 |

**下放非本層之領域機制（引用 `AUGUR-WM v1.0 Annex D`，本層僅承接其不變式之型別側）**：屬性 schema 之具名欄位集合與欄位設計（Layer 4；本層僅於 T.0 宣告各 Type 之 Attribute schema 概念槽之存在性，承接 D20 屬性面向）、維度白名單取得機制（`§D21`，Layer 4；見 ONT.41／T.61）、Confidence 語義（`§D9`，Layer 4；本層不設 Knowledge 欄位）、語料隔離之機器強制（`§D25`，Layer 5–6；見 T.27）、風險分級（`§D16`，Layer 6）。

---

# Annex L3 [N] — 與 Layer 3（Identity System）之分界表

本層與 Layer 3 共享 `AUGUR-MC v1.3 §P3.E3`（`AUGUR-WM v1.0 §D2` 標為 L2/L3）。分界必須精確，否則構成下侵（違 ONT.3、ONT.7）。**一句判準**：本層產出「類型與判準的定義文本」；Layer 3 產出「個體的永久參照與其一生的機器機制」。

| 議題 | Layer 2（Ontology）**得為**（本層） | Layer 3（Identity System）**專屬，本層不得下侵** |
|---|---|---|
| **同一性判準** | **制定**（formulate）：宣告每 Type「憑何判定同一」之判準內容（ONT.20） | **採認**（adopt）使判準生效於 resolution（`AUGUR-WM v1.0 §WM.21(e)`、`§D2`、`§D6`）；resolution 演算／時限指標（`§D4`）＝DO.1 |
| **identifier** | 宣告某 Type 之個體「需被鑄造 identifier」（僅結構需求宣告，ONT.12(c)、ONT.22） | **鑄造（mint）**、identifier 結構、命名空間設計（`AUGUR-WM v1.0 §D5`、`§WM.20`）；本層**不得**課 identifier 編碼義務＝DO.2 |
| **生命週期** | 宣告 Type 具生命週期**屬性**（如 DerivativeContract 上市→結算消滅、Security 之 retire/relist 為型別語義，T.1/T.3/T.4/T.5/T.34） | **merge/split/retire/relist 機制、tombstone、去識別化、identity lineage、lifecycle 事件表**（`AUGUR-WM v1.0 §WM.22`、`§D3`；AUD-05 補正）＝DO.3 |
| **identity claim** | 宣告「哪些 Type 間存在跨體系同一性需以 claim 表達」（如 Security↔ISIN、Security↔外部代碼，ONT.22、T.42／T.6／T.1；模型／宇宙自身之外部代碼另見 T.28） | **identity claim 一級表介面**（identifier 對、判準引用、Evidence、Confidence）（`AUGUR-WM v1.0 §D3`、`§WM.21(c)`）＝DO.2 |
| **instance/type** | **定義區分語義**與型別命名空間隔離（ONT.30–31） | 標記之**存續／解析落實**、provisional 狀態解析、身份屬性 as-of 版本化（`AUGUR-WM v1.0 §D4`；AUD-07）＝DO.4 |

**AUD-04/05/06/07 之三層落點釐清**：Type 由 Layer 2 宣告（本層）→ identifier 鑄造與 lifecycle 事件表由 Layer 3（AUD-04/05 補正）→ 跨來源 identity claim 表介面由 Layer 3（AUD-06 補正）→ 身份屬性 as-of 化由 Layer 3（AUD-07 補正）→ Confidence 語義／欄位由 Layer 4（AUD-03，非本層）。本層僅承接**第一段（Type 宣告）**。凡本層條款一經 Layer 3 承接即可直接鑄造 identifier 或執行 merge/retire 而無須 Layer 3 另為定義者，即為下侵，違 ONT.3。

---

# Annex T [N] — 台股型別階層與同一性判準

> **T.0（體例與封印）[N]** 本 Annex 為 `AUGUR-WM v1.0 Annex A` 存在宣告之型別化（承接 DI.1、DI.3）。每一 Type 條依 ONT.12 載三要件：**上位範疇（parent）｜同一性判準（Identity Criterion，本層制定；Layer 3 採認前依 `AUGUR-WM v1.0 §WM.21(e)` 保守解釋為未解析）｜instance/type 語義**；並載對映 `AUGUR-WM v1.0 Annex A`、承接判準／審計。**Attribute schema（屬性 schema 概念槽，ONT.2）**：每一 Type 之屬性 schema 概念槽之**存在性**於型別層宣告（承接 D20 之屬性面向）；惟其屬性欄位之**具名集合與欄位設計** DEFER Layer 4（Representation 實作層，見 Annex DO 散列項），本層不逐一列舉欄位（Layer 1 於 `§A.1`／`§A.6`／`§A.7` 等已具名之屬性由 Layer 4 承接落於對應 Type 之概念槽）。所有外部識別碼一律為指涉資訊（ONT.22），非 identifier。
> **義務主體**：本規格自身、本規格後續修訂者。**可判定判準**：每一 T.{n} 條含 parent、Identity Criterion（「同一 iff〔…〕」形式）、instance/type 三欄且各欄可解析者為合規。

## T-① Entity → AbstractEntity → FinancialInstrument（金融工具）

> **T.1 Security（上市櫃證券）[N]**
> **parent**：AbstractEntity/FinancialInstrument（**重分類**自 `AUGUR-WM v1.0 §A.1`「Physical Entity（市場標的）」描述語，依 `§WM.23`「市場標的為描述語、非類型宣告」；見 Annex CS OT-1；`AUGUR-MC v1.3 §P3.W2` 列 Financial Instrument 於 Abstract Entity）。
> **同一性判準（制定）**：同一 iff〔繫結同一 **Issuer** Identity（T.20）× 同一 instrument class × 發行序〕**且存續期間不跨越 retire/relist 邊界**；供應商證券代碼為 provisional alias（identity claim，`AUGUR-WM v1.0 §WM.21(c)`）。**代碼重用／借殼**：存續期間跨越 retire/relist 邊界者，非同一個體（純判準式陳述）；該邊界之判定、split 之執行與 identity lineage 機制 DEFER Layer 3（DO.3、`AUGUR-WM v1.0 §WM.22`；承接 `§A.54` OPEN-1、AUD-04/05）。判準採認 DEFER Layer 3（DO.1／`§D6`），採認前保守解釋為未解析。
> **instance/type**：個股為 **Instance**；「上市／上櫃／ETF／普通股」等為 **type**（不得混入個股命名空間，ONT.31，承接 AUD-04）。
> **義務主體**：本規格作者、Layer 3–7 消費者。**可判定判準**：任一 Security 個體之權威繫結解析至 Issuer＋instrument class＋存續期間，不解析至裸代碼字串者為合規。〔對映 `§A.1`、`§A.32`；AUD-04/06〕

> **T.2 Index（市場指數）[N]** — **parent** AbstractEntity。**判準**：同一 iff〔指數編製方法論定義同一 ∧ 實體類型宣告為 Index〕；**識別欄相同不推定同一**（`AUGUR-WM v1.0 §A.3` 共用識別空間現象）。**instance/type**：具體指數為 Instance（獨立命名空間，ONT.31）；「報酬指數／價格指數」為 type。〔對映 `§A.3`、`§A.32`〕

> **T.3 DerivativeContract（期貨／選擇權契約）[N]** — **parent** DynamicEntity（生命週期屬性：上市→交易→結算消滅，機制 DEFER Layer 3 DO.3）。**判準**：同一 iff〔契約標的族 × 契約月份／序列識別 × 買賣權別 × 履約價〕四元組相等（`AUGUR-WM v1.0 §A.32`）；契約月份值域**非**日期值域（`§A.6` 形宣告）。**instance/type**：具體契約為 Instance；「期貨／選擇權／週合約／價差組合」為 type。〔對映 `§A.6`、`§A.24`〕

> **T.4 ConvertibleBond（可轉換公司債）[N]** — **parent** DynamicEntity。**判準**：同一 iff〔Issuer（T.20）× 發行批次序〕；具至標的股（T.1）之一級 UnderlyingRelation（T.51）。**instance/type**：具體可轉債為 Instance；轉換條款類為 type。〔對映 `§A.7`〕

> **T.5 Warrant（權證）[N]** — **parent** DynamicEntity（具生命週期之金融工具，體例同 T.3／T.4；兼具 AbstractEntity/FinancialInstrument 面向，以屬性表徵，非第二 parent）。**判準**：同一 iff〔發行券商 Identity × 權證發行序 × 標的〕；具至標的股之 UnderlyingRelation（T.51）。**instance/type**：具體權證為 Instance；權證類別為 type。〔對映 `§A.8`〕

> **T.6 ForeignSecurity（外國證券／指數）[N]** — **parent** AbstractEntity。**判準**：同一 iff〔外部識別體系（如 ISIN／exchange ticker）之 identity claim（ONT.22）〕；識別空間異於本域個股（`AUGUR-WM v1.0 §A.9`）。**instance/type**：具體外股／外指為 Instance；市場／工具類為 type。〔對映 `§A.9`〕

## T-② Entity → AgentiveEntity / AbstractEntity（主體與結構實體）

> **T.20 Issuer（發行人／公司）[N]**
> **parent**：AgentiveEntity（有行為之法律主體）。
> **同一性判準（制定）**：同一 iff〔法律實體同一〕（法人識別如統一編號為**指涉資訊**，ONT.22，非 identifier）；**借殼／更名不改 Issuer identity，但得改其所發行 Security identity**（T.1）。Issuer→{Security, ConvertibleBond, Warrant} 為一級 IssuanceRelation（T.50）。財報／月營收公開事件（T.31）、產業分類（T.24）、月營收制度性豁免之世界 referent 為 **Issuer**（非 Security，承接 `AUGUR-WM v1.0 §A.57`）。判準採認 DEFER Layer 3（DO.1／`§D2`）。
> **instance/type**：具體公司為 Instance；公司類別（法人／金控子公司等）為 type。
> **義務主體**：本規格作者、Layer 3–7 消費者。**可判定判準**：任一發行事實可解析至恰一 Issuer Identity 且與其 Security 之 IssuanceRelation 可解析者為合規。〔對映 `§A.57`；AUD-01-R1；`AUGUR-MC v1.3 §P3.E3`〕

> **T.21 MarketParticipant（市場交易主體階層）[N]** — **parent** AgentiveEntity/AbstractEntity 族（機構法人／外資／投信／自營商／行庫／大額交易人／券商／期權經紀商）。**判準**：同一 iff〔主體類別值 × 主體識別碼〕（`AUGUR-WM v1.0 §A.32`）。**同一性宣告（`§WM.15`）**：長表與寬表為同一 MarketParticipant 觀測世界事實之兩通道，型別層登錄**同一 Type**、擇用規則上收至 `§A.5`／Registry，消費端不得各自內嵌（體例同 T.35）。**instance/type**：具體主體為 Instance；主體類別為 type。〔對映 `§A.5`〕

> **T.22 DataProvider（資料供應商）[N]** — **parent** AgentiveEntity（有授權階層、限流行為，其限流／拒絕為可觀測事件）。**判準**：同一 iff〔供應商法律／服務實體識別〕。**instance/type**：具體供應商為 Instance；供應商類別為 type。防護／額度紀律 DEFER Layer 4–7（`AUGUR-WM v1.0 §D23`）。〔對映 `§A.13`〕

> **T.23 HumanDecisionMaker（人類決策者）[N]** — **parent** AgentiveEntity。**判準**：同一 iff〔系統內使用者主體識別〕。涉自然人，表徵受 `AUGUR-WM v1.0 §WM.38`／`§A.59` 有界表徵約束（法規對應 DEFER Layer 3/6，`§D17`）。**instance/type**：具體使用者為 Instance；角色（RBAC role，機制 DEFER Layer 6 `§D24`）為 type。〔對映 `§A.15`、`§A.59`〕

> **T.24 IndustryClassification（產業分類）[N]** — **parent** AbstractEntity（**雙層**：市場分類 + 產業鏈分類）。**判準**：同一 iff〔分類體系版本 × 節點碼〕。**instance/type**：分類節點為 **type**（承接 AUD-04：'Automobile' 為 type，不得為 Security instance，ONT.31）。「某板塊制度性缺資料（如金融業無月營收）為世界結構事實，非缺陷」（`AUGUR-WM v1.0 §A.12`）。**身份屬性 as-of 化**（以「今日的」分類判定歷史 panel 之禁止型態，AUD-07）DEFER Layer 3（DO.4）。〔對映 `§A.12`〕

> **T.25 Roster（名冊）[N]** — **parent** AbstractEntity。**判準**：同一 iff〔市場 × 名冊類型〕；**成員資格為時間函數**（survivorship 禁令，`AUGUR-WM v1.0 §A.2`），成員關係見 T.53。**instance/type**：具體名冊為 Instance；名冊類型為 type。〔對映 `§A.2`〕

> **T.26 TradingCalendar（交易日曆）[N]** — **parent** AbstractEntity。**判準**：同一 iff〔市場 Identity〕，每市場一日曆；日曆日↔交易日為一級 CalendarTradingDayRelation（T.52）。**instance/type**：具體市場日曆為 Instance；日曆類型為 type。〔對映 `§A.4`〕

> **T.27 KnowledgeCorpus（知識語料族）[N]** — **parent** AbstractEntity 族（學派／原則／思想家／著作／文本塊）。**判準**：同一 iff〔文獻來源可溯源之作品／作者識別〕。**隔離宣告**：素養語料不進預測管線（型別層標記隔離；機器強制 DEFER Layer 5–6，`AUGUR-WM v1.0 §D25`）。**instance/type**：具體著作／思想家為 Instance；學派／原則類為 type。〔對映 `§A.16`〕

> **T.28 SelfReflexiveType（Model／CoreUniverse／GATE／Augur 自身）[N]** — **parent** AgentiveEntity（有行為之系統內主體，`AUGUR-WM v1.0 §WM.26` 自反性之型別落地；GATE 預註冊實驗兼具 DynamicEntity 之生命週期／審批狀態面向，以屬性表徵，非第二 parent）。**判準**：Model／CoreUniverse 同一 iff〔系統內部實體識別〕；GATE（預註冊實驗）為具生命週期與審批狀態之 DynamicEntity，同一 iff〔實驗預註冊識別 × 判準凍結序〕。**instance/type**：具體模型／宇宙／實驗為 Instance；模型家族／實驗類為 type。**外部識別碼繫結**（如 ISIN 於 T.42）為 identity claim（ONT.22）。〔對映 `§A.14`、`§A.19`、`§A.20`〕

> **T.29 Catalog（元資料目錄）[N]** — **parent** AbstractEntity（內部）。**判準**：同一 iff〔資料集／欄位元資料識別〕。**instance/type**：具體目錄項為 Instance；目錄類為 type。〔對映 `§A.17`〕

## T-③ Event（事件型別）

> **T.30 CorporateAction（公司行動）[N]** — **parent** Event 族（除權息／減資／股票分割／面額變更）。**事件同一性判準（制定）**：同一 iff〔referent Identity（Issuer 或 Security）× event_type × 生效時點〕。除權息使還原價回溯重算，表徵為**新版本非靜默覆寫**（`AUGUR-WM v1.0 §WM.32`、`§A.21`）。**instance/type**：具體公司行動為 Instance；行動類型為 type。〔對映 `§A.21`〕

> **T.31 DisclosureEvent（財報／月營收公開）[N]** — **parent** Event。referent 為 **Issuer**（T.20）。restatement（重編）為合法世界事件非缺陷（`AUGUR-WM v1.0 §A.22`）。**判準**：同一 iff〔Issuer × 報表類型 × 所屬期末〕。**instance/type**：具體公開事件為 Instance；報表類型為 type。〔對映 `§A.22`〕

> **T.32 RegulatoryStateChange（監理狀態變更）[N]** — **parent** State（**期間型 interval**：暫停交易／處置／暫停現沖／暫停融券，以起訖期間表徵；狀態起始之事件面向以「起始時點」屬性表徵，非第二 parent）。**判準**：同一 iff〔referent Security × 監理類型 × 起始時點〕。**instance/type**：具體監理狀態實例為 Instance；監理類型為 type。（本條依其 interval 狀態本質歸 **State**；置於 T-③ 分組係因其源於監理事件，屬編排分組、非 parent 宣告。）〔對映 `§A.23`〕

> **T.33 SettlementEvent（期權結算）[N]** — **parent** Event（契約生命週期終點，對應 T.3）。**判準**：同一 iff〔DerivativeContract Identity × 結算時點〕。**instance/type**：具體結算為 Instance。〔對映 `§A.24`〕

> **T.34 Delisting（下市）[N]** — **parent** Event。**下市改變來源可見性，不改變歷史真實性**（`AUGUR-WM v1.0 §A.25`）；為 Security lifecycle retire 之 Evidence 來源（**機制** DEFER Layer 3，DO.3／AUD-05）。**判準**：同一 iff〔Security Identity × 下市時點〕。**instance/type**：具體下市為 Instance。〔對映 `§A.25`〕

> **T.35 MarketTrade/DailyBar（日級成交事實）[N]** — **parent** Event（日級成交世界事件；日末狀態面向（如收盤價之狀態讀值）以屬性表徵，非第二 parent）。**判準**：同一 iff〔Security Identity × 交易日 × 市場〕。**同一性宣告**：原始成交價通道與 CorporateAction 調整之還原價通道為**同一世界事實之兩通道**（`AUGUR-WM v1.0 §WM.15`、`§A.58`），型別層登錄同一 Type；擇用規則上收至 `§A.58`，消費端不得各自內嵌。**instance/type**：具體日 bar 為 Instance。〔對映 `§A.58`；AUD-14-R〕

> **T.36 NewsEvent（新聞事件）[N]** — **parent** Event。**事件時間軸 ≠ 交易日軸**（`AUGUR-WM v1.0 §A.18`），以事件發生時刻為時間戳語義。**判準**：同一 iff〔事件來源識別 × 事件發生時刻 × referent〕。**instance/type**：具體新聞事件為 Instance；事件類為 type。〔對映 `§A.18`〕

## T-④ State（狀態型別）

> **T.40 PriceLimit（漲跌停狀態）[N]** — **parent** State。**判準**：同一 iff〔referent Security × 交易日 × 狀態類型（參考價／漲停／跌停）× valid time〕。**instance/type**：某 Security 某交易日之具體漲跌停狀態快照為 **Instance**；狀態類型（參考價／漲停／跌停）為 **type**。〔對映 `§A.26`〕

> **T.41 CreditTradingState（信用交易 stock-flow）[N]** — **parent** State 族（融資融券／借券／當沖；「昨餘＋今增減＝今餘」共同形，`AUGUR-WM v1.0 §A.27`）。**判準**：同一 iff〔referent Security × 信用類型 × valid time〕。**instance/type**：某 Security 某交易日之具體信用餘額狀態快照為 **Instance**；信用類型（融資／融券／借券／當沖）為 **type**。〔對映 `§A.27`〕

> **T.42 HoldingStructureState（持股結構）[N]** — **parent** State（外資持股／股權分級／市值權重）。**判準**：同一 iff〔referent Security × 狀態類型 × valid time〕；**ISIN 為本域第二外部識別體系**（外部指涉資訊，非 identifier；identity claim 繫結，`AUGUR-WM v1.0 §A.28`／`§A.33`）。身份屬性 as-of 版本化 DEFER Layer 3（DO.4／AUD-07）。**instance/type**：某 Security 之具體持股結構狀態快照為 **Instance**；狀態類型（外資持股／股權分級／市值權重）為 **type**。〔對映 `§A.28`〕

> **T.43 UniverseMembership（core universe 成員）[N]** — **parent** State（**point-in-time**：任一 as-of 成員集可重建，`AUGUR-WM v1.0 §A.29`）。**判準**：同一 iff〔CoreUniverse Identity × Security Identity × valid time〕。快照機制 DEFER Layer 4（`§D27`）；provisional 解析 DEFER Layer 3（DO.4）。**instance/type**：某 CoreUniverse 某 as-of 之具體成員資格快照為 **Instance**；成員資格狀態類型為 **type**。〔對映 `§A.29`〕

> **T.44 DataFinality（資料定案性）[N]** — **parent** State（final/non-final，`AUGUR-WM v1.0 §A.30`、`§WM.32`）。**判準**：同一 iff〔referent Identity × 資料集 × valid time × 定案性語義〕。**instance/type**：某 referent 某資料集之具體定案性狀態為 **Instance**；定案性類型（final／non-final）為 **type**。〔對映 `§A.30`〕

## T-⑤ Relation（世界關係型別，`AUGUR-WM v1.0 §WM.8`）

> **T.50 IssuanceRelation（發行關係）[N]** — **parent** Relation（頂層範疇，ONT.10／ONT.40）。Issuer↔Security/ConvertibleBond/Warrant（`AUGUR-WM v1.0 §A.57`）。**判準（ONT.40）**：同一 iff〔關係型別（issuance）× 端點有序組（Issuer, 被發行 Type 個體）× valid time〕。**instance/type**：具體發行關係實例（端點 × valid time 定之）為 **Instance**；關係型別（issuance）為 **type**。

> **T.51 UnderlyingRelation（標的關係）[N]** — **parent** Relation（頂層範疇，ONT.10／ONT.40）。ConvertibleBond/Warrant/DerivativeContract↔Security（`AUGUR-WM v1.0 §A.7`/`§A.8`）。**判準**：同一 iff〔關係型別（underlying）× 端點有序組（衍生工具, 標的 Security）× valid time〕。**instance/type**：具體標的關係實例（端點 × valid time 定之）為 **Instance**；關係型別（underlying）為 **type**。

> **T.52 CalendarTradingDayRelation（日曆交易日關係）[N]** — **parent** Relation（頂層範疇，ONT.10／ONT.40）。日曆日↔各市場交易日（`AUGUR-WM v1.0 §A.4`）。**判準**：同一 iff〔關係型別 × 端點有序組（TradingCalendar, 交易日）× valid time〕。**instance/type**：具體日曆交易日關係實例（端點 × valid time 定之）為 **Instance**；關係型別為 **type**。

> **T.53 RosterMembershipRelation（名冊成員關係）[N]** — **parent** Relation（頂層範疇，ONT.10／ONT.40）。Roster↔Security（時間函數，`AUGUR-WM v1.0 §A.2`）。**判準**：同一 iff〔關係型別（membership）× 端點有序組（Roster, Security）× valid time〕。**instance/type**：具體名冊成員關係實例（端點 × valid time 定之）為 **Instance**；關係型別（membership）為 **type**。

## T-⑥ Quantity（世界量型別，`AUGUR-WM v1.0 §WM.8`）

> **T.60 EconomicIndicator（經濟指標）[N]** — **parent** Quantity（世界量實體）。**判準（ONT.41）**：**世界量同一性 = Domain Profile/Registry 明文宣告**（`AUGUR-WM v1.0 §WM.15`；無宣告即非同一）。領域錨定例：「新台幣對美元匯率」為一世界概念、多供應商通道（`§A.11`）；外部 series 清單以 SSOT 指向、不抄列。**instance/type**：具體指標為 Instance；指標類為 type。〔對映 `§A.11`；AUD-06-R1〕

> **T.61 MacroDimensionQuantity（商品／匯率／利率／公債殖利率維度族）[N]** — **parent** Quantity（by-dimension 世界量）。**判準**：同一 iff〔量種 × 維度值（白名單）〕；**維度全集白名單制定、臆測禁止**（`AUGUR-WM v1.0 §A.10`；白名單取得機制 DEFER Layer 4，`§D21`）。**instance/type**：具體維度值序列為 Instance；量種為 type。〔對映 `§A.10`〕

## A-OPEN 待決事項（下放／待採認）[N]

> **T.90（OPEN-1：Security 判準採認）[N]** Security↔Issuer 分離型別已由本層制定（T.1、T.20）；正式判準**採認** DEFER Layer 3（DO.1、`AUGUR-WM v1.0 §D6`、`§A.54`）。下層消費涉此 Type **必須**顯式引用本條並載明假設；採認前依 `§WM.21(e)` 保守解釋為未解析。**可判定判準**：涉 Security／Issuer 判準之下層條款含對 `§T.90` 或 `AUGUR-WM v1.0 §A.54` 之引用者為合規。

> **T.91（OPEN-2：Entity 四分之台股邊界）[N]** MarketParticipant（T.21）兼具 Agentive/Abstract、EconomicIndicator（T.60）兼具 Entity/Quantity 之跨範疇歸屬，列為**顯式待決**；禁止下層以隱含假設消費（承接 `AUGUR-WM v1.0 §WM.50` 待決事項紀律）。**可判定判準**：涉 T.21／T.60 跨範疇歸屬之下層條款含對 `§T.91` 之引用且載明所採歸屬假設者為合規。

---

# Annex T-Map [N] — `AUGUR-WM v1.0 Annex A` 世界概念 → 型別對映

> **TM.0（雙向解析義務）[N]** 本表落實 ONT.13、ONT.50。每列以**主型別節點**（該存在宣告之類屬，恰一，ONT.13）為對映本體；存在宣告內另涵之一級世界關係，其**附帶關係型別**（T-⑤）以括號標注，非主映射（ONT.13）。每列可雙向解析（存在宣告 ↔ 主型別節點）。
> **義務主體**：本規格自身、Annex T-Map 維護者。**可判定判準**：①部封閉集 {`§A.1`–`§A.30`, `§A.57`, `§A.58`}（ONT.13）全部存在宣告條於本表有列且主型別節點指向 Annex T 既存 Type；跨範疇待決者標 A-OPEN。

| AUGUR-WM Annex A | 世界概念 | → Layer 2 主型別節點（附帶關係型別） |
|---|---|---|
| `§A.1` | Security | T.1 |
| `§A.2` | Roster | T.25（附帶關係型別 T.53） |
| `§A.3` | Index | T.2 |
| `§A.4` | TradingCalendar | T.26（附帶關係型別 T.52） |
| `§A.5` | MarketParticipant | T.21（跨範疇待決 T.91） |
| `§A.6` | DerivativeContract | T.3 |
| `§A.7` | ConvertibleBond | T.4（附帶關係型別 T.51） |
| `§A.8` | Warrant | T.5（附帶關係型別 T.51） |
| `§A.9` | ForeignSecurity | T.6 |
| `§A.10` | Commodity/FX/Rate/BondYield 維度族 | T.61 |
| `§A.11` | EconomicIndicator | T.60（跨範疇待決 T.91） |
| `§A.12` | IndustryClassification | T.24 |
| `§A.13` | DataProvider | T.22 |
| `§A.14` | Model / CoreUniverse | T.28 |
| `§A.15` | HumanDecisionMaker | T.23 |
| `§A.16` | KnowledgeCorpus | T.27 |
| `§A.17` | Catalog | T.29 |
| `§A.18` | NewsEvent | T.36 |
| `§A.19` | GATE 預註冊實驗 | T.28 |
| `§A.20` | Augur 自身 | T.28 |
| `§A.21` | CorporateAction | T.30 |
| `§A.22` | 財報／月營收公開 | T.31 |
| `§A.23` | RegulatoryStateChange | T.32 |
| `§A.24` | 期權結算事件 | T.33 |
| `§A.25` | Delisting | T.34 |
| `§A.26` | PriceLimit | T.40 |
| `§A.27` | 信用交易 stock-flow | T.41 |
| `§A.28` | 持股結構 | T.42（ISIN identity claim，ONT.22） |
| `§A.29` | UniverseMembership | T.43 |
| `§A.30` | DataFinality | T.44 |
| `§A.57` | Issuer | T.20（附帶關係型別 T.50） |
| `§A.58` | MarketTrade/DailyBar | T.35 |

---

# Annex TR [I] — 形式充分性追溯矩陣（`AUGUR-MC v1.3`／`AUGUR-WM v1.0` → ONT）

本附錄為 `AUGUR-WM v1.0 §WM.44` 形式充分性自查（Annex CS §CS.10）之**逐條枚舉底稿**：對 `AUGUR-MC v1.3` **全部** [N] 條款（TR.1）與 `AUGUR-WM v1.0` **全部** [N] 條款（TR.2）逐條列其 ONT 落點與模式。**枚舉範圍**依 `AUGUR-WM v1.0 §WM.44`（「現行版全部 [N] 條款」）＋各適用上層之全部 [N] 條款：**僅 [N] 條款**入枚舉；`AUGUR-MC v1.3` 之 **P1.Y–P5.Y（WHY 說理，標 [I]）** 及各章之 [I] 敘述段**非 [N]**，依 `§WM.44` 不在枚舉義務範圍（機器骨架枚舉如將其計入，屬 `mc_clauses` 骨架限制之過計，非 [N] 缺漏）。模式閉集：滿足／細化（refines）／承接（carries）／DEFER（hooks）／不觸及（附理由）。

**本矩陣之地位與形式充分性狀態陳述之歸屬**：本附錄本身標 **[I]**（機器盤點底稿；規範效力悉依所引條款本文）。惟 `AUGUR-WM v1.0 §WM.44` 明定形式充分性為**生效要件**（「任一條款無對應且無明記者，聲明不完整，規格不生效力」），故承載形式充分性**狀態陳述**（「已成就」與否）之規範性判斷，置於 **Annex CS §CS.10（[N] 規範性聲明節）**；本 [I] 矩陣為該 [N] 判斷之逐條枚舉依據，二者分工：矩陣（[I]）列枚舉、CS.10（[N]）作狀態陳述。此分工使「形式充分性依 Annex TR 之逐條枚舉已成就」之陳述具 [N] 效力，而枚舉明細不因篇幅膨脹正文。**實質充分性**及本規格之**生效**，均非本附錄或 CS.10 所能認定，專屬 Steward 違憲審查與充任認定程序（`AUGUR-MC v1.3 §8.2`、`§0.5`、`§8.6`）。

## TR.1 `AUGUR-MC v1.3` [N] 條款 → ONT 落點

| 憲章條款 | ONT 落點 | 模式 |
|---|---|---|
| PA（§1.1 含釐清句）、§1.3 | ONT.8（忠實表徵之型別前提）、ONT.4 | 承接（不作解釋性增刪，`§8.5(d)`） |
| §2 元規則、§2.3、§2.4 | ONT.2、ONT.22 | 承接（細化不重定義） |
| §0（章）、§0.1、§0.2、§0.3、§0.4 | ONT §0.1（名稱／層級／生效要件）、ONT §0.2（規範用語等級）、ONT §0.5＋ONT.5（[N]/[I] 標注、三態）、ONT §0.4（權威語言術語同一性） | 承接（文件約定：§0.1→ONT §0.1／【地位】；§0.2→ONT §0.2；§0.3 條文效力標注→ONT §0.5／ONT.5；§0.4→ONT §0.4） |
| §0.5、§0.6(a)(b)(c) | ONT.1、ONT.3、ONT.4、ONT.9 | 承接 |
| §1（章）、§1.2 標準鏈引用 | ONT.5、ONT.7；CS.7（canonical chain 節選連續，不重繪不改序） | 承接（§1 章之 §1.1／§1.3 另見首列；§1.2 標準鏈引用之型別前提落 ONT.5，機制不代定） |
| §3（章：Five Immutable Principles 容器）[N] | ONT.6；P1→ONT.8/ONT.10、P2→ONT.11/ONT.60、**P3→ONT.10–12/ONT.20–31/Annex T（本層核心）**、P4→ONT.60、P5→T.20–T.23/T.28 | 承接（章級容器；其 P1–P5 逐條落點見本表各 P{n}.* 列，P3 為本層核心） |
| P1.D／P1.W1／P1.E1 | ONT.8、ONT.10 | 細化（Type 不由來源反推） |
| P1.E2 | ONT.13、ONT.50 | 細化（每一世界事實解析至恰一 Type） |
| P1.E3 | T.23、T.42（涉自然人 Type，DEFER `§D17`） | DEFER（法規對應 Layer 3/6） |
| P2.D／P2.W1／P2.W2／P2.E1–E5 | 不觸及（附理由） | 不觸及：本層不設 Knowledge 欄位、不定確立工作流、不產模態內容機制；僅保證 Type 體系不使 `AUGUR-WM v1.0 §WM.13/16/18/29` 之表達力不可能（ONT.60、ONT.11） |
| P3.D／P3.W1 | ONT.10、ONT.31（基本單位為 Identity） | 承接 |
| **P3.W2** | **ONT.10–12、Annex T（T.1–T.61）** | **細化（承接 D1；完整分類體系；Event/State 重定位為頂層範疇依 `§WM.36`，見 CS.8 OT-4）** |
| **P3.E3** | **ONT.20–22、ONT.30–31、Annex T** | **細化＋hooks（承接 D2；制定判準＋instance/type，採認 DEFER Layer 3）** |
| P3.E1 | ONT.21（provisional 保守解釋）、DO.4 | hooks（解析落實 Layer 3） |
| P3.E2 | ONT.12(c)、ONT.22、ONT.60、Annex L3 | DEFER（mint／lifecycle 機制 Layer 3，DO.2/DO.3） |
| P4.D／P4.W1／P4.E1–E8 | 不觸及（附理由） | 不觸及：Evidence 分類、Confidence 語義、雙時間機制屬 Layer 4；本層僅為 identity claim 之 Evidence/Confidence 槽指出結構位置（ONT.22），不設欄位 |
| P4.E5 | ONT.60（Type 變更不刪歷史，與矛盾保存同向）、T.30/T.35（新版本非覆寫） | 承接（表達力不削弱） |
| P5.D／P5.W1–W5／P5.E1／P5.E2 | 不觸及（附理由） | 不觸及：行動治理屬 Layer 6；本層僅型別化行動主體（T.20–T.23、T.28）與行動事件之 referent，不定授權鏈、風險分級 |
| §4 canonical chain（EV.1–EV.12） | ONT.5（承接，不重繪不改序） | 承接 |
| §5 架構角色 | 不觸及（附理由） | 不觸及：六抽象角色為架構承諾，非 Type；本層不引為定義依據（ONT.4） |
| §6 F1／F2／F3 | ONT.8、ONT.4 | 承接（Type 不由來源／模型／Agent 反推） |
| §6 F4 | ONT.22、ONT.31（無 Identity 繫結之 Knowledge 無型別位置） | 承接 |
| §6 F5／F6 | 不觸及（附理由） | 不觸及：智慧輸出可解釋性、Action 可歸責屬 Layer 4–6 |
| §7 五項不變核心 | ONT.11（新增範疇須更完整描述五核心）、ONT.60 | 承接 |
| §8.1–§8.6 | ONT.1、ONT.9、ONT.60–62 | 承接（審查、豁免、版本、聲明） |

## TR.2 `AUGUR-WM v1.0` [N] 條款 → ONT 落點

| WM 條款 | ONT 落點 | 模式 |
|---|---|---|
| WM.1／WM.2／WM.3／WM.4 | ONT.1／ONT.2／ONT.3／ONT.4 | 承接（Layer 2 對應細化） |
| WM.5／WM.6 | ONT.5／ONT.6（任務） | 承接 |
| WM.7／WM.8 | ONT.8（WM.8 明列 Layer 2 作者為義務主體） | 承接 |
| WM.9(b) | ONT.5、ONT.13（結構權威型別側） | 承接 |
| WM.9(a)(c)／WM.10 | 不觸及（附理由） | 不觸及：形權威與系統記錄屬 Observation／Layer 4–7；本層不定通道權威 |
| WM.11／WM.12 | ONT.22（provisional referent 之型別繫結）、不設不確定性欄位 | 承接＋部分不觸及（Confidence 槽 Layer 4） |
| WM.13／WM.14 | ONT.60（演化四不變式之型別側）、ONT.13/ONT.50（唯一權威表徵型別前提） | 承接＋細化 |
| WM.15 | T.35、T.60、ONT.41（同一世界事實多通道同一 Type） | 承接 |
| WM.16／WM.17／WM.18 | 不觸及（附理由） | 不觸及：衝突／模態／候選斷言表達力屬 Layer 1 保證＋Layer 4–5 機制；本層 Type 體系不使其不可表達（ONT.11、ONT.60） |
| WM.19 | ONT.10、ONT.31（基本單位 Identity） | 承接 |
| WM.20 | ONT.22、Annex L3（不課 identifier 結構義務） | 承接（DEFER Layer 3） |
| **WM.21(a)** | **ONT.20、ONT.12(b)** | **細化（制定判準）** |
| **WM.21(b)** | **ONT.30** | **細化（instance/type 語義）** |
| WM.21(c) | ONT.22、T.28/T.42（identity claim 結構位置） | 承接（表介面 DEFER Layer 3 DO.2） |
| WM.21(d) | ONT.21、DO.4 | hooks（provisional 保守解釋；解析 Layer 3） |
| WM.21(e) | ONT.21、T.0（效力封印） | 承接（封印移交 Layer 3） |
| WM.22 | ONT.60、Annex L3（存續跨 Ontology 變更） | 承接（機制 DEFER Layer 3 DO.3） |
| **WM.23** | **ONT.10–13、Annex T、Annex T-Map** | **細化（承接 D1／D20；存在宣告 → 分類體系）** |
| WM.24／WM.25／WM.27 | ONT.5、TR.1（canonical chain／變更二分／Action 六元組） | 承接（本層不代定行動機制） |
| WM.26 | T.28（自反性型別落地） | 承接 |
| WM.28／WM.29 | 不觸及（附理由） | 不觸及：人類權威表徵位置、fail-safe 屬 Layer 4–6 |
| WM.30／WM.31／WM.32 | T.40–T.44（valid time 於狀態判準）、T.30/T.35（新版本） | 承接（時間機制 DEFER Layer 4 `§D8`） |
| WM.33 | ONT.30（instance/type 標記）、ONT.60（標記不滅失） | 承接（各標記判定 DEFER 下層） |
| WM.34 | ONT.5、全文可判定判準 | 承接（機器可稽核） |
| WM.35／WM.36／WM.37 | ONT.13、ONT.50（型別側；Registry 條目屬系統狀態） | 細化（承接；載體 DEFER Layer 4/7 `§D18`） |
| WM.38 | T.23、T.42（有界表徵之 Type 標注） | 承接（法規 DEFER `§D17`） |
| WM.39–WM.45 | Annex CS、ONT.62 | 承接（正式格式作成聲明） |
| WM.46／WM.47／WM.48 | ONT.9／ONT.61／ONT.61 | 承接 |
| WM.49–WM.53 | 不觸及（附理由） | 不觸及：Domain Profile 框架為 Layer 1 對其 Annex A 之治理；本層消費 Annex A 之產物，不制定 Profile 框架 |
| Annex A（A.1–A.59） | Annex T、Annex T-Map（逐條型別化） | 細化（承接 D20；封印素材 [I] → Type） |
| Annex D（D1/D2/D20 目標 L2） | Annex DI（DI.1–DI.3） | 承接（defers-in） |

---

# Annex CS [N] — 本規格之 Constitutional Compliance Statement

本 Annex 為**規範性聲明文件**（[N]）：其存在與內容為本規格生效要件（ONT.62、`AUGUR-MC v1.3 §8.3`、`AUGUR-WM v1.0 §WM.39`）。本聲明依 `AUGUR-WM v1.0 §WM.39–45` **正式格式**作成（非暫行模板）：本聲明作成於 Layer 1（`AUGUR-WM v1.0`）生效日 2026-07-16 之後，依 `§WM.45` 必須用正式格式。**地位提示**：本規格為 **v1.0 生效版本**，Steward 充任認定已作成，自 2026-07-17 起生效（Steward 裁決第 2026-003 號，AL-2026-007；見【地位】、ONT.1）；本聲明之**實質**充分性最終判斷仍屬 Steward `§8.2` 違憲審查程序。

```
compliance-statement:
  spec: Augur Ontology Specification
  spec-version: v1.0
  layer: 2
  mc-version: AUGUR-MC v1.3
  upper-specs: [AUGUR-WM v1.0]
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: [OT-1, OT-2, OT-3, OT-4]
  defers-in: [D1, D2, D20]
  defers-out: [DO.1, DO.2, DO.3, DO.4]
  date: 2026-07-17
  author: Layer 2 Ontology 規格撰稿官（依 Constitution Steward 委辦之 Layer 2 起草程序）
  archive-path: specs/ONTOLOGY-SPECIFICATION-v0.1-draft.md
```

## CS.1 PA（Prime Axiom）

* 所引條款：`AUGUR-MC v1.3 §1.1`（含釐清句）、`§1.3`；`AUGUR-WM v1.0 §WM.7`、`§WM.11`。
* 合規模式：承接（不作解釋性增刪，`AUGUR-MC v1.3 §8.5(d)`）。
* 論證：Type 體系為忠實表徵之**結構前提**——以持續一致之 Identity 錨定 Knowledge，須先知「這是關於哪一類、憑何判定同一」。本規格以 ONT.8（Type 不由來源反推、優先描述 Reality）、ONT.13（每一世界事實解析至恰一 Type）落實忠實表徵之型別側；未對 PA 作任何解釋性增刪。
* 判準揭示：「忠實」不作為本規格自創謂詞；凡涉及即引 `AUGUR-WM v1.0 §WM.12/WM.13` 判準。「指名 vs 定義依據」→ONT.4 刪名測試（Annex EO）。

## CS.2 P1（Reality First）

* 所引條款：`AUGUR-MC v1.3 §P1.D`、`§P1.W1`、`§P1.E1`、`§P1.E2`、`§P1.E3`；`AUGUR-WM v1.0 §WM.7`、`§WM.8`。
* 合規模式：細化（P1.W1／F1→ONT.8；P1.E2→ONT.13、ONT.50）；DEFER（P1.E3 法規→`§D17`）。
* 論證：ONT.8 承接 `AUGUR-WM v1.0 §WM.8`（明列 Layer 2 作者為義務主體），使 F1 禁令（Type 不由來源 schema 反推）於型別層可判定化，承接審計 AUD-01 之型別側化解；ONT.13/ONT.50 使「每一世界事實映射至共同世界模型」具型別節點之機器可盤點落地。
* 判準揭示：「最高抽象」→`AUGUR-WM v1.0 §WM.7` 判準；「指名 vs 定義依據」→ONT.4（Annex EO）。

## CS.3 P2（Representation Before Intelligence）

* 所引條款：`AUGUR-MC v1.3 §P2.D`、`§P2.W1`、`§P2.W2`、`§P2.E1`–`§P2.E5`；`AUGUR-WM v1.0 §WM.13`、`§WM.16`–`§WM.18`、`§WM.29`。
* 合規模式：carries／不觸及（多數）。
* 論證：本層**不設** Knowledge 欄位（Layer 4）、**不定**確立工作流（Layer 4–5）、**不產**模態內容機制；僅保證 Type 體系**不使** `AUGUR-WM v1.0 §WM.13`（演化四不變式）、`§WM.16`（衝突／證據不足）、`§WM.17`（模態）、`§WM.18`（候選斷言）、`§WM.29`（fail-safe）之表達力或機器稽核不可能——ONT.11（不刪減範疇）、ONT.60（Type 變更不刪歷史、不中斷 Identity）為此保證之型別側承載。
* 判準揭示：本節無自創謂詞；涉及處引 `AUGUR-WM v1.0` 對應判準。

## CS.4 P3（Identity Before Knowledge）——**本層核心**

* 所引條款：`AUGUR-MC v1.3 §P3.D`、`§P3.W1`、`§P3.W2`、`§P3.E1`、`§P3.E2`、`§P3.E3`、`§2.4`；`AUGUR-WM v1.0 §WM.19`–`§WM.23`。
* 合規模式：**細化＋hooks**（P3.W2→ONT.10–12/Annex T，承接 D1；P3.E3→ONT.20–22/ONT.30–31，承接 D2，制定判準＋instance/type；P3.E1→ONT.21 provisional 保守解釋；P3.E2→ONT.12(c)/ONT.22/ONT.60，mint 與 lifecycle 機制 DEFER Layer 3）。
* 論證：
  * **`§P3.W2`（完整分類體系）**：ONT.10（頂層五範疇＋Entity 四分）、ONT.11（開放封閉化紀律）、ONT.12（三要件）、Annex T（T.1–T.61 台股具體 Type）——承接 `AUGUR-WM v1.0 §WM.23`（D1）。
  * **`§P3.E3`（同一性判準／instance-type）**：ONT.20（判準制定）、ONT.21（效力封印）、ONT.30（instance/type 語義）、ONT.31（命名空間隔離）——承接 `§WM.21(a)(b)`（D2）。
  * **`§P3.E1／E2`（不觸及之明記）**：identifier 引用／解析、mint、merge/split/retire/tombstone、identity lineage 屬 Layer 3；本層僅制定判準內容、宣告 Type 具生命週期**屬性**（不定機制），避免下侵（ONT.3、ONT.7、Annex L3、DO.1–DO.4）。
* 判準揭示：「已解析／provisional」→ONT.21（未採認期間保守解釋為未解析，Annex EO）；「Type 由本層宣告 vs 消費端 regex 臨場判定」→ONT.22、ONT.31（Annex EO）。

## CS.5 P4（Evidence Before Conclusion）

* 所引條款：`AUGUR-MC v1.3 §P4.E1`、`§P4.E5`、`§P4.E8`、`§2.4`；`AUGUR-WM v1.0 §WM.30`–`§WM.33`。
* 合規模式：carries／不觸及（Confidence 語義／欄位、Evidence 分類、雙時間機制屬 Layer 4）。
* 論證：本層**不定義** Confidence 形式化語義、**不設計** Knowledge 五元組欄位、**不定** Evidence 分類法（承接審計 AUD-03 之落點為 Layer 4，非本層）；僅為 identity claim 之 Evidence／Confidence 指出**結構位置**（ONT.22，位置本身由 `AUGUR-WM v1.0 §WM.21(c)` 提供）。valid time 於本層僅作為狀態／關係 Type 之 Identity Criterion 要素（T.40–T.44、T.50–T.53），機制 DEFER Layer 4（`§D8`）。ONT.60（Type 變更不刪歷史）與 `§P4.E5`（矛盾保存、只失效不刪除）同向。
* 判準揭示：本節無自創 Confidence 謂詞（本層零 Confidence 語義，避免與 AUD-03 之 Layer 4 定義權衝突）。

## CS.6 P5（Accountability Before Action）

* 所引條款：`AUGUR-MC v1.3 §P5.E1`、`§P5.W1`–`§P5.W5`、`§2.9`；`AUGUR-WM v1.0 §WM.27`、`§WM.28`。
* 合規模式：不觸及（附理由）＋部分 carries。
* 論證：行動治理（授權鏈、風險分級、人類權威 Gate）屬 Layer 6；本層僅**型別化行動主體**（T.20 Issuer、T.21 MarketParticipant、T.23 HumanDecisionMaker、T.28 Agent/Model）與行動事件之 referent，**不定**授權鏈、風險分級、否決能力度量。本層 Type 體系不使 `AUGUR-WM v1.0 §WM.27`（Action 六元組世界事件、F4–F6 禁止型態之無位置性）、`§WM.28`（人類權威表徵位置）不可表達。
* 判準揭示：本節無自創謂詞；「高風險／高影響／降低監督能力」依 `AUGUR-MC v1.3` 原判準，本層未另創、未消費。

## CS.7 §4 canonical chain

* 所引條款：`AUGUR-MC v1.3 §4`（EV.1–EV.12、雙迴路、EV.9）、`§1.2`；`AUGUR-WM v1.0 §WM.24`。
* 合規模式：承接（ONT.5；不重繪、不改序）。
* 論證：本規格全部標準鏈引用均為節選標注且節點連續；未重繪、未改序。本層於 EV.4（Identity）之型別前提（Type Hierarchy 與 Identity Criterion）作制定，不改鏈之序與雙迴路語義。
* 判準揭示：節選連續性→`AUGUR-WM v1.0 §WM.24` 判準。

## CS.8 已知緊張關係（`AUGUR-WM v1.0 §WM.42`）

| id | 所涉條款 | 描述 | 緩解／狀態 |
|---|---|---|---|
| **OT-1** | T.1 vs `AUGUR-WM v1.0 §A.1`、`§WM.23` | `Annex A §A.1` 將 Security 記為「Physical Entity（市場標的）」；本層依 `§WM.23`（存在宣告非分類體系；`§A.1` 自陳「市場標的為描述語、非類型宣告、類型體系 DEFER Layer 2」）將 Security 分類為 **AbstractEntity/FinancialInstrument**（`AUGUR-MC v1.3 §P3.W2` 列 Financial Instrument 於 Abstract Entity）。 | **非牴觸**，係行使 Layer 2 分類權；如實揭露。重分類不改任何個體 Identity（ONT.60）。非豁免事項。 |
| **OT-2** | ONT.21、T.0 vs `AUGUR-WM v1.0 §WM.21(e)`、`§D2` | 同一性判準之「制定（L2）／採認（L3）」二分（D2 標為 L2/L3）於 `§WM.21(e)` 封印下之效力邊界：本層判準在 Layer 3 採認前不生 resolution 效力。 | 如實揭露；涉該類 Identity 引用保守解釋為未解析；採認 DEFER Layer 3（DO.1、`§D6`）。非豁免事項。 |
| **OT-3** | T.1、T.20、T.90 vs `AUGUR-WM v1.0 §A.54`（OPEN-1） | `§A.54` OPEN-1（stock_id 代碼重用／借殼）之實體層型別化已由本層完成（Security↔Issuer 分離，T.1/T.20），但正式判準採認 DEFER Layer 3（DO.1、`§D6`），待 Steward／決策層拍板。 | 保守預設 [N]（供應商代碼為指涉資訊、非 identifier）＋候選記載 [I] 封印；下層消費須顯式引用 T.90。非豁免事項。 |
| **OT-4** | ONT.10 vs `AUGUR-MC v1.3 §P3.W2`、`AUGUR-WM v1.0 §WM.36` | `§P3.W2` 於 Dynamic Entity 例示列有「Event、Process、State」（字面上 Event/State 為 Dynamic Entity 之子例）；本層依 `§WM.36` 歸類閉集（實體／事件／狀態／關係／量並列）行使 `§WM.23` Layer 2 完整分類權，將 **DynamicEntity 重解為「具生命週期之實體」**（T.3/T.4/T.5），並將 **Event／State 另立為與 Entity 並列之頂層範疇**（ONT.10）。二切面（五頂層範疇承接 `§WM.36` Registry 歸類閉集；Entity 四分承接 `§P3.W2`）為不同分類切面，非字面矛盾。 | **非牴觸**，係依 `§WM.23`／`§WM.36` 行使 Layer 2 分類權；Event／State 之個體仍具 Identity（非刪減四類 Entity 或五頂層範疇，合 ONT.11）；依 `§WM.42` 如實揭露。非豁免事項。 |

豁免登記：`none`（waivers: []）。豁免期間 Knowledge 標記義務之落實方式：本規格無現行豁免；如有，依 `AUGUR-WM v1.0 §WM.33` 豁免狀態標記位置落實。

## CS.9 雙向 DEFER 承接表（`AUGUR-WM v1.0 §WM.43`）

* (a) **承接上層之掛鉤（defers-in）**：見 Annex DI——D1→（ONT.10–12、Annex T）；D2→（ONT.20–22、ONT.30–31、Annex T）；D20→（Annex T、Annex T-Map、ONT.40–41）。與 front-matter `defers-in: [D1, D2, D20]` 雙向對表。
* (b) **下放下層之掛鉤（defers-out）**：見 Annex DO——DO.1（ONT.21→Layer 3 判準採認）；DO.2（ONT.22→Layer 3 identity claim 表介面／identifier 鑄造）；DO.3（T.1/T.3/T.4/T.34→Layer 3 生命週期事件表與 retire/relist/split 機制）；DO.4（ONT.30/T.42/T.43→Layer 3 provisional 解析與身份屬性 as-of 版本化）。與 front-matter `defers-out: [DO.1, DO.2, DO.3, DO.4]` 雙向對表。

## CS.10 形式充分性自查（`AUGUR-WM v1.0 §WM.44`）

依 `§WM.44` 判準自查。**枚舉宇宙（`AUGUR-MC v1.3` 全部 [N] 條款，依 `§0.3` 條款編號系統逐條列示）**：

* **文件約定與使命**：PA、§0、§0.1、§0.2、§0.3、§0.4、§0.5、§0.6、§1、§1.1、§1.2、§1.3、§2、§3。
* **P1（Reality First）**：P1.D、P1.W1、P1.E1、P1.E2、P1.E3。
* **P2（Representation Before Intelligence）**：P2.D、P2.W1、P2.W2、P2.E1、P2.E2、P2.E3、P2.E4、P2.E5。
* **P3（Identity Before Knowledge，本層核心）**：P3.D、P3.W1、P3.W2、P3.E1、P3.E2、P3.E3。
* **P4（Evidence Before Conclusion）**：P4.D、P4.W1、P4.E1、P4.E2、P4.E3、P4.E4、P4.E5、P4.E6、P4.E7、P4.E8。
* **P5（Accountability Before Action）**：P5.D、P5.W1、P5.W2、P5.W3、P5.W4、P5.W5、P5.E1、P5.E2。
* **§4 canonical chain**：EV.1、EV.2、EV.3、EV.4、EV.5、EV.6、EV.7、EV.8、EV.9、EV.10、EV.11、EV.12。
* **§5 架構角色；§6 F 型態**：F1、F2、F3、F4、F5、F6；**§7；§8**：§8.1、§8.2、§8.3、§8.4、§8.5、§8.6。
* **[I] 排除（非 [N]，依 `§WM.44` 不入枚舉義務）**：P1.Y、P2.Y、P3.Y、P4.Y、P5.Y（各原則之 WHY 說理段，`§0.3` 標 [I]）；機器骨架枚舉如將其計入 [N] 宇宙，屬 `mc_clauses` 骨架過計，非本規格 [N] 缺漏。

上開 `AUGUR-MC v1.3` 全部 [N] 條款，與 `AUGUR-WM v1.0` 全部 [N] 條款（WM.1–WM.53、Annex A〔A.1–A.59〕、Annex D 目標含 Layer 2 者），均已對應至本規格至少一條 [N] 條款、明記 DEFER 掛鉤（Annex DO、Annex DI）、或明記「不觸及」及理由——**逐條對照見 Annex TR（TR.1 憲章側、TR.2 Layer 1 側）**。

**形式充分性狀態陳述（[N]）**：依前開逐條枚舉，`AUGUR-MC v1.3` 全部 [N] 條款與 `AUGUR-WM v1.0` 全部 [N] 條款均無「無對應且無明記」之缺漏；**形式充分性依 Annex TR 之逐條枚舉已成就**（`AUGUR-WM v1.0 §WM.44` 意義之形式要件滿足）。本狀態陳述為 Annex CS（[N]）之規範性判斷，係 `§WM.44` 所定生效**形式要件**之滿足陳述；Annex TR（[I]）為其逐條枚舉依據（[I]/[N] 分工見 Annex TR 引言）。

明記「不觸及」之主要條款群及理由：
* `AUGUR-MC v1.3` P2 全組、P4.E1–E8（除 E5）、P5 全組、§5、§6 F5–F6：其規範對象為 Knowledge 欄位／確立工作流／行動治理／架構角色，屬 Layer 4–6；本層僅型別化其主體與 referent，不代定機制。
* `AUGUR-WM v1.0` WM.9(a)(c)、WM.10、WM.16–18、WM.28–29、WM.49–53：屬通道權威／表達力保證／Domain Profile 框架，本層消費其產物而不制定。

**形式 vs 實質、及生效之界分**：本節僅陳述**形式**充分性已成就（可機器盤點之逐條枚舉完備）。**實質充分性**（論證是否真正化解各上位不變式）由違憲審查程序（`AUGUR-MC v1.3 §8.2`）判斷；本規格之**生效**另須 Steward **充任認定**（`§0.5`、`§8.6`）——二者均**非**本節所能認定。充任認定業經 Steward 作成（裁決第 2026-003 號，2026-07-17，AL-2026-007），本規格依【地位】節為 **v1.0 生效版本**；**實質**充分性之判斷仍屬 `§8.2` 違憲審查程序，未因充任而終局確認。

---

# Annex EO [N] — 自創評價性謂詞判準彙整表

> **EO.1（收錄義務）[N]** 本表為 `AUGUR-MC v1.3 §8.3` 可判定性元規則之**單一盤點構件**（準用 `AUGUR-WM v1.0 §WM.44`／`Annex E`）：本規格自創或型別層操作化之每一評價性謂詞，其可判定判準所在條款彙整如下。正文或 Annex 如增列自創謂詞，**必須**同步收錄本表；未收錄且未附判準之謂詞，一律採保守解釋（存疑即不允許）。
> **義務主體**：本規格後續修訂者。**可判定判準**：全文謂詞掃描與本表逐列對照之完備性檢查。

| 謂詞 | 判準所在 |
|---|---|
| Type 由來源反推 vs 優先描述 Reality | ONT.8、ONT.4（刪名測試） |
| 指名 vs 定義依據 | ONT.4（刪名測試；承接 `AUGUR-WM v1.0 §WM.4`） |
| 細化 vs 重定義 | ONT.2（刪除測試：刪句後上位定義字面適用不變＝細化，反之＝重定義） |
| 型別定義完整（三要件） | ONT.12（parent＋Identity Criterion＋instance/type 三欄俱全且可解析） |
| 頂層範疇封閉化合規 | ONT.10、ONT.11（上溯終止於閉集；刪減四類／五範疇為違規） |
| 存在宣告 → 恰一 Type（接合） | ONT.13、Annex T-Map（雙向解析；解析至零／多為違規） |
| 判準制定 vs 採認 | ONT.20（制定＝「同一 iff〔可判定條件式〕」）／ONT.21（採認屬 Layer 3；封印句存在性） |
| 已解析 vs provisional | ONT.21（Layer 3 採認前保守解釋為未解析） |
| 外部識別碼 vs identifier | ONT.22（外部識別碼為指涉資訊；裸字串充當身份／消費端 regex 判定為違規） |
| instance vs type（繫結對象） | ONT.30（標記可解析至個體命名空間或 Type 節點） |
| 型別命名空間隔離 | ONT.31（個體參照解析至恰一 Type 個體命名空間；type 節點當 Instance 消費為違規） |
| 世界關係同一性 | ONT.40（關係型別 × 端點有序組 × valid time 三要素俱全） |
| 世界量同一性 | ONT.41、T.60（量種 × 維度〔白名單〕；維度臆測為違規；無 Registry 宣告即非同一） |
| 型別重分類不改個體 Identity | ONT.60（變更後全部 Identity 仍可解析、歷史 Type 編號仍存在） |
| 下侵 Layer 3 | ONT.3、ONT.7、Annex L3（本層條款一經 Layer 3 承接即可直接 mint／merge/retire 而無須 Layer 3 另為定義者，為下侵） |
| 聲明完整／形式充分 | ONT.62、Annex CS §CS.10（front-matter 全欄＋七節＋緊張關係＋雙向 DEFER＋Annex TR 對應完備） |

---

*本規格計：正文條款 ONT.1–ONT.62、Annex T（體例 T.0、型別 T.1–T.61、待決事項 T.90–T.91）、Annex DI（DI.0–DI.3）、Annex DO（DO.0–DO.4）、Annex T-Map（TM.0）、Annex EO（EO.1）、Annex CS 合規聲明 [N]。全文以繁體中文為權威文本（§0.4）。本文件為 **v1.0 生效版本**，Steward 充任認定已作成，自 2026-07-17 起生效（Steward 裁決第 2026-003 號、AL-2026-007；`AUGUR-MC v1.3 §0.5`、【地位】、ONT.1）；**實質**充分性之最終判斷仍屬 Steward `§8.2` 違憲審查程序。*

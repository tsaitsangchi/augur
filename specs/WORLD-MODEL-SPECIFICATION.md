# 《Augur World Model Specification》

Augur Enterprise AI Operating System
世界模型規格（Layer 1 — World Model）
引用縮寫：**AUGUR-WM**｜版本：**v1.0**（前版：v0.1-draft）｜受 **AUGUR-MC v1.4** 全文約束（v1.2→v1.4 均為 minor／[I]，所引條款編號不變；本規格引用版號於 2026-07-18 依 RULING-2026-018 全艦統一至 v1.4）

---

> ## 【地位】[N]
>
> 本文件為 **v1.0 生效版本**。Constitution Steward 已於 2026-07-16 依 `AUGUR-MC v1.4 §0.5` 作成**充任認定**（Steward 裁決第 2026-002 號主文一，Amendment Log AL-2026-005）：本文件充任 Layer 對照表 Layer 1 欄所轄之「World Model Specification」，§0.1 生效要件全部成就，**自 2026-07-16 起生效**。v0.1-draft 原文歸檔於 `specs/WORLD-MODEL-SPECIFICATION-v0.1-draft.md`；draft → v1.0 之變更僅限：版本欄、本節生效記錄、§0.1 成就記錄、§1.2 辦理情形註記、WM.48 [I] 現況註記更新、Annex C 識別區塊隨版更新與導言生效註記、C.8 表 T-4／T-6／T-7 解消註記（T-6 之解消依據為裁決主文二），**無任何 [N] 條款實質變更、編號不重排**（裁決主文一）。
>
> 本文件內含自身之 Constitutional Compliance Statement（Annex C），依 `AUGUR-MC v1.4 §8.3` 過渡規則 (c)，Layer 1 之聲明不因格式自我引用而無效；Annex C 依暫行模板作成一節，業經裁決主文三追認。

---

## 目錄 [I]

* §0 Document Status & Conventions（WM.1–WM.4、WM.53）
* §1 Purpose & Position（WM.5–WM.6）
* §2 World Model Primacy（WM.7–WM.10）
* §3 Representation Semantics（WM.11–WM.18）
* §4 Identity in the World Model（WM.19–WM.23）
* §5 World Evolution & State Change（WM.24–WM.29）
* §6 Time Semantics（WM.30–WM.32）
* §7 Marking System（WM.33）
* §8 Machine Auditability Basis（WM.34）
* §9 世界概念註冊與消費紀律（WM.35–WM.37）
* §10 Bounded Representation（WM.38）
* §11 Constitutional Compliance Statement Format（WM.39–WM.45）
* §12 Conformance & Continuity（WM.46–WM.48）
* §13 Domain Profile Framework（WM.49–WM.52）
* Annex A [N] — Augur Domain World Model Profile（第一域：台灣證券市場）（A.0–A.59）
* Annex B [I] — Traceability Matrix
* Annex C [N] — 本規格之 Constitutional Compliance Statement
* Annex D [N] — DEFER 掛鉤總表（D0–D28）
* Annex E [N] — 自創評價性謂詞判準彙整表（E1）
* Annex F [I] — 首批 World Concept Registry 啟動條目（隨卷附件）

---

## §0 Document Status & Conventions（文件地位與約定）[N]

### 0.1 名稱、層級與生效條件

本文件名稱 **Augur World Model Specification**（引用縮寫 AUGUR-WM），層級 **Layer 1 — World Model**，版本 **v1.0**（前版 v0.1-draft），受 `AUGUR-MC v1.4` 全文約束。`AUGUR-MC v1.4 §0.5` 對照表 Layer 1 欄既已登錄「World Model Specification」；本規格之生效要件**已全部成就**（Steward 裁決第 2026-002 號，2026-07-16，AL-2026-005）：

* (a) 充任認定：✅ 裁決主文一（依 `AUGUR-MC v1.4 §0.5`、`AUGUR-MC v1.4 §8.6` 議決）；
* (b) 依 Steward 暫行模板作成之 Constitutional Compliance Statement：✅ Annex C，暫行模板業經裁決主文三發布（constitution/COMPLIANCE-STATEMENT-INTERIM-TEMPLATE.md）並追認 Annex C 依其作成（`AUGUR-MC v1.4 §8.3` 過渡規則 (a)(c)）。

**生效日：2026-07-16**。下層引用格式：`AUGUR-WM v1.0 §{條款}`（§0.3）。

### 0.2 規範用語約定

本規格之規範用語與約束力等級，全文依 `AUGUR-MC v1.4 §0.2`：**必須**（MUST，絕對義務）、**不得**（MUST NOT，絕對禁止）、**應**（SHOULD，偏離須書面說明理由）、**得**（MAY，允許而不構成義務）。

### 0.3 條款編號系統

* 正文條款編號採 **WM.{n}**；Annex 條款編號採 **A.{n}**（Annex A）、**D{n}**（Annex D，含前言條款 D0）、**E{n}**（Annex E）；Annex C 各節採 **C.{n}**。
* 條款編號一經發布**永不重用、永不重排**；廢止條款保留編號並標注 **(repealed)**。
* 下層引用本規格之格式：`AUGUR-WM v{version} §WM.{n}`；Annex 條款逐一為：`AUGUR-WM v{version} §A.{n}`、`AUGUR-WM v{version} §D{n}`、`AUGUR-WM v{version} §E{n}`、`AUGUR-WM v{version} §C.{n}`。
* 本規格引用憲章採 `AUGUR-MC v1.4 §{條款編號}` 格式（`AUGUR-MC v1.4 §8.6`）；**憲章升版時引用版號同步更新**（RULING-2026-018 更正原「一律採 v1.2」之永久凍結措辭）。

### 0.4 權威語言聲明

本規格以**繁體中文版為權威版本**；規範性術語於正文中一律使用英文原詞（Reality、Observation、Representation、Identity、Evidence、Knowledge、Confidence、Action、Agent、Intelligence），與 `AUGUR-MC v1.4 §0.4` 保持術語同一性。

### 0.5 條文效力標注

* 每一章節標注 **[N]（Normative）** 或 **[I]（Informative）**，全文適用。
* [N] 與 [I] 內容不一致時，依 `AUGUR-MC v1.4 §8.2` 以 Normative 為準。
* 本規格每一 [N] 條款標注其**憲章錨定**與**三態型態**：**refines**（細化憲章條款）、**carries**（承接憲章不變式並給予世界模型結構位置）、**hooks**（DEFER 掛鉤，載明目標 Layer 與授權條款）。

### 0.6 條款

> **WM.1（從屬）[N｜carries｜AUGUR-MC v1.4 §0.6(a)、§8.2]**
> 本規格全部內容從屬並不得違反 `AUGUR-MC v1.4`；牴觸部分無效，經違憲認定之條款自認定日起無效，不得作為 Layer 2–7 規格之依據（`AUGUR-MC v1.4 §0.6(a)`、`AUGUR-MC v1.4 §8.2`）。
> **義務主體**：本規格自身及其後續修訂者。**可判定判準**：任一條款經 Steward 依 `AUGUR-MC v1.4 §8.2` 認定違憲者，即為牴觸；認定前依較嚴格解讀原則處理。

> **WM.2（細化不重定義）[N｜carries｜AUGUR-MC v1.4 §2 元規則]**
> 本規格對 `AUGUR-MC v1.4 §2` 之十一個初始概念（Reality、Observation、Representation、Identity、Evidence、Knowledge、Intelligence、Agent、Action、Confidence、Evidence 通道）**僅為細化，不重新定義、不變更內涵、不另創同義歧稱**（「World Representation」為 Representation 之唯一同義全稱，`AUGUR-MC v1.4 §2.3`）。本規格任何條款**不得**解釋為與 `AUGUR-MC v1.4 §2` 內涵不符；就此有解釋爭議者，依 `AUGUR-MC v1.4 §8.1` 由 Steward 裁決，裁決前依較嚴格解讀處理。
> 本規格新造術語——**World Concept**（世界概念）、**World Concept Registry**（世界概念登錄簿）、**Observation Channel**（觀測通道）、**Observation Store**（觀測儲存）、**Domain Profile**（領域 Profile）、**世界關係**與**世界量**（定義見 WM.8）——均為 `AUGUR-MC v1.4 §2` 術語之細化構件，於首次出現處以一句式定義並標注上位術語、或於首次出現處以前向引用指向其定義條款，不與初始概念並列。同一新造概念全文採單一名稱（英文原詞加註中文定譯），不另創異名。
> **義務主體**：本規格自身、Annex A 及本規格後續修訂者。**可判定判準**：本規格任一術語定義文句，刪除後不影響 `AUGUR-MC v1.4 §2` 各定義之字面適用者為細化；反之為重定義（禁止）。

> **WM.3（管轄與 DEFER 紀律）[N｜carries｜AUGUR-MC v1.4 §0.5]**
> 本規格為 Layer 1 唯一所轄規格，不自行擴張管轄。凡 `AUGUR-MC v1.4` 明定定義權屬 Layer 2–7 之事項，本規格**僅得**設 DEFER 掛鉤條款（明載目標 Layer 與授權條款），**不得**代行定義；DEFER 總表見 Annex D。
> **義務主體**：本規格自身。**可判定判準**：本規格任一條款對 Annex D 所列 DEFER 事項作成實質定義（即：該定義文句可被下層直接消費而無須下層另為定義）者，違反本條。

> **WM.4（概念層獨立性＋刪名測試）[N｜carries｜AUGUR-MC v1.4 §0.6(b)、§6 F1–F3、§7、§5、Appendix A]**
> 本規格**不得**引用 Layer 5–7 執行層構件（含任何資料庫產品、Agent Runtime、外部介面技術、特定 AI model）作為定義依據；**得**引用 `AUGUR-MC v1.4 §5` 之六個抽象架構角色；`AUGUR-MC v1.4 Appendix A` 之產品對照為非約束性，不得作為定義依據。
> 本規格文中對產品、供應商或資料集之提及，**僅得**為 **Observation Channel 之指名**（Observation Channel ＝ 供應 Observation 之具名來源路徑，為 `AUGUR-MC v1.4 §2.2` Observation 之 Source 面向之細化構件），**不得**為定義依據。
> **可判定判準（刪名測試）**：凡刪去該產品名、供應商名或資料集名後，條款之概念內涵不變者，為指名（合法）；內涵改變者，為定義依據（禁止）。本測試適用於本規格全文（含 Annex A）及下層規格之合規審查。
> **義務主體**：本規格自身、Annex A、Layer 2–7 規格作者。

> **WM.53（文件約定之規範地位）[N｜carries｜AUGUR-MC v1.4 §0.6(a)、§8.3 可判定性元規則]**（編號承 WM.52 之後新增；依 §0.3 永不重排，置於本節）
> 【地位】節與 §0.1–§0.5 之全部約定（生效要件、規範用語等級、條款編號系統、權威語言、條文效力標注）為 [N] 規範內容，其效力與正文條款同；§11 引言之定義權宣示，其規範內容載於 WM.39。
> **義務主體**：本規格自身、其後續修訂者及一切消費者。**可判定判準**：各約定之文句字面適用；牴觸各該約定者為文件缺陷，依 `AUGUR-MC v1.4 §8.2` 採較嚴格解讀處理至修正為止。

---

## §1 Purpose & Position（任務與定位）

### 1.1 條款 [N]

> **WM.5（任務）[N｜refines｜AUGUR-MC v1.4 §P1.E2、§0.6(c)、§1.1]**
> 本規格之任務為：具體化 `AUGUR-MC v1.4 §P1.E2` 共同世界模型之語義，以可供 Layer 2–7 合規審查之規範性語言（`AUGUR-MC v1.4 §0.2` 用語等級）陳述世界模型不變式。
> **義務主體**：本規格自身。**可判定判準**：本規格每一 [N] 條款均載明義務主體與可判定判準；Domain Profile 得依 §13 於其頭部條款（A.0）概括載明義務主體與型態判準，**視同 Profile 各條載明**；缺任一者（含無概括載明可資適用者）為文件缺陷，依 `AUGUR-MC v1.4 §8.2` 採較嚴格解讀處理至修正為止。

> **WM.6（領域 Profile 與領域前身文件）[N｜refines｜AUGUR-MC v1.4 §P1.E2；承接審計補正 AUD-01-R1、AUD-12-R]**
> Annex A 為本規格之**規範性領域 Profile**（Domain Profile，定義見 WM.49；框架依 §13）。《系統核心思想》為 Annex A 之**領域前身文件**（[I] 引註，非定義依據；適用 WM.4 刪名測試）；其世界觀內容經 Annex A 顯式承接為**定位宣告**，自此由隱式 world model 升為顯式規範文本。
> **義務主體**：Annex A 及其後續修訂者。**可判定判準**：Annex A 第⑤部各條均可解析至本規格或 `AUGUR-MC v1.4` 條款；不可解析者不具規範效力。

### 1.2 附註 [I]

建請 Constitution Steward 於本規格充任認定同案，辦理下列程序事項（本規格僅於此為程序建請，非自為）：

* (a) 五份治權檔（系統核心思想、原則精華、系統架構大憲章、CLAUDE.md、datasets 參考文件）之 `AUGUR-MC v1.4 §0.5` 定位登錄與檔頭從屬聲明（審計補正 AUD-12-R 所指事項）。此屬 Meta-Constitution 對照表之修訂事項（minor，`AUGUR-MC v1.4 §8.6`）。
* (b) 發布（或追認）Constitutional Compliance Statement 暫行模板，載明其文件識別、發布日與存檔路徑，並追認 Annex C 依其作成（`AUGUR-MC v1.4 §8.3` 過渡規則 (a)；現狀揭露見 Annex C 導言與 C.8 T-7）。
* (c) 就本規格存檔目錄（specs/）之書面地位作成指定裁決（WM.48 [I] 現況註記所指事項）。
* (d) 治權檔「唯一真相來源」等措辭之 patch 交辦（Annex D D19 所載 Steward 程序事項）。

〔**辦理情形**（RULING-2026-002，2026-07-16）：(a) 業經主文二辦理（定位登錄，`AUGUR-MC` v1.3／AL-2026-006），檔頭從屬聲明依主文五交辦（期限 2026-10-14）；(b) 業經主文三辦理；(c) 業經主文四辦理；(d) 依主文五交辦（期限 2026-10-14；現況另見 C.8 T-2、Annex D D19）。本節原文依歷史記錄保留。〕

---

## §2 World Model Primacy（世界模型至上性）[N]

> **WM.7（最高抽象）[N｜refines｜AUGUR-MC v1.4 §P1.E1、§P1.W1]**
> 共同世界模型為系統內**高於一切資料來源之最高抽象**。任何對 Reality 之觀測通道——無論當前是否存在，包括但不限於 ERP、MES、Sensor、Document、External Knowledge、金融市場資料 API、官方統計資料庫——皆屬資料來源；**資料來源不得成為最高抽象**。世界模型必須優先描述 Reality，不得優先適配現有資料來源。
> **義務主體**：本規格、Layer 2–7 規格作者、系統之一切世界模型構件。**可判定判準**：任一規格條款或系統構件宣稱某資料來源之結構為世界結構之權威者（未通過 WM.9 之權威三分定位者），違反本條。

> **WM.8（結構獨立性）[N｜carries｜AUGUR-MC v1.4 §6 F1、F2、F3、§8.3 可判定性元規則]**
> 世界概念（World Concept ＝ 世界模型中對一類世界實體、事件、狀態、關係或量之具名概念位置，為 `AUGUR-MC v1.4 §2.3` Representation 之細化構件；**世界關係**＝世界實體間隨時間取值之一級具名關係，**世界量**＝以維度索引、隨時間取值之世界狀態量，二者均為 `AUGUR-MC v1.4 §2.3` Representation 之細化構件）之定義，**不得**以任何資料來源之 schema、表結構、欄位命名或 API 行為反推導出（`AUGUR-MC v1.4 §6 F1` 之 Layer 1 落地）；亦**不得**以特定 AI model 能力或 Agent 執行需求為前提（`AUGUR-MC v1.4 §6 F2`、`§6 F3`）。
> **義務主體**：本規格、Annex A、Layer 2 Ontology 規格作者。**可判定判準**：適用 WM.4 刪名測試——世界概念定義文句中出現來源表名、欄名或端點名而未通過刪名測試者，推定違反本條；推定得由 Steward 附理由推翻。

> **WM.9（權威三分）[N｜refines｜AUGUR-MC v1.4 §2.1、§2.2、§2.3、§5 角色一；承接審計補正 AUD-01-R2、AUD-26-R]**
> 系統內一切「權威」「真相」「事實」之宣稱，必須解析為下列三個各自可判定之權威位置之一，不得混同：
>
> **(a) 形權威（Observation 層）**：任何外部來源對其回應內容具**且僅具** Observation 層權威。
> **可判定判準**：其權威範圍恰為該通道所交付紀錄之 schema、值域與 byte 內容，以該來源當次回應為準。任何「API 即權威」「唯一事實」「唯一真相」之來源側宣稱，其效力範圍以本項為限；逾越本項範圍之宣稱無效。
> **義務主體**：Layer 2–7 規格作者、治權文件（治權文件＝下列五份既存系統文件之閉集：系統核心思想、原則精華、系統架構大憲章、CLAUDE.md、datasets 參考文件；§1.2(a) 所列者）之後續修訂者。
>
> **(b) 結構權威（世界結構層）**：世界中存在何種實體、事件與狀態及其相互關係，由本規格（含 Annex A）及 Layer 2 Ontology 宣告。
> **可判定判準**：世界結構之任何斷言必須可解析至本規格或 Layer 2 規格之條款，不得解析至來源表結構。
> **義務主體**：Layer 2–7 規格作者、系統之一切消費模組規格。
>
> **(c) 系統記錄（Representation 層）**：系統內權威 Representation 之儲存，其地位為 **single system of record（唯一系統記錄）** 意義下之 World State System of Record（`AUGUR-MC v1.4 §5` 角色一）。
> **可判定判準**：下層文件描述本項時必須採「唯一系統記錄」或等義措辭，**不得**採「唯一真相來源」；「真相／事實」指涉一律收斂至 `AUGUR-MC v1.4 §2` 之 Reality／Observation／Representation 定義。既存治權文件措辭之隨改為 patch 級事項（Annex D D19）。
> **義務主體**：Layer 4–7 規格與治權文件作者。

> **WM.10（Observation Store 宣告）[N｜refines｜AUGUR-MC v1.4 §2.2、§P2.E4、§P4.E6；承接審計補正 AUD-01-R3]**
> 以最貼近來源之形對來源回應作**逐值忠實鏡像**、並保有**對帳（attestation）紀律**之儲存，於世界模型中之地位為 **Observation Store**（Observation Store ＝ 保存 Observation 原始形之儲存層，為 `AUGUR-MC v1.4 §2.2` Observation 之細化構件），屬**合法且必要之觀測層**。
> 其忠實性紀律——每值可追溯至某次來源回應、與來源之對帳驗證——**必須全部保留，不得**因共同表徵層之建立而拆除或削弱。共同表徵層**必須**建立於 Observation Store 之上，**不得**取而代之。
> Observation Store 之認定**以通道特徵描述為之**；具體落地載體之指認於 Annex A 以 [I] 為之。
> **義務主體**：Layer 4、Layer 7 規格作者、系統維運者。**可判定判準**：一儲存層滿足「逐值可追溯至某次來源回應」且「具與來源之對帳驗證紀錄」二特徵者，即為 Observation Store；任何規格或變更使該二特徵之一不再成立者，違反本條。

---

## §3 Representation Semantics（表徵語義）[N]

> **WM.11（referent 繫結）[N｜refines｜AUGUR-MC v1.4 §1.3 禁令一、§P2.E4]**
> 任何 Representation 元素**必須**繫結 referent：一個已解析**或 provisional** 之 Identity、或其狀態、關係或事件。無 referent，不允許 Representation。
> **義務主體**：Layer 2–7 規格作者、系統之一切表徵構件。**可判定判準**：任一 Representation 元素存在至某 Identity（含 provisional identity，WM.21(d)）之機器可解析繫結者為合規；不存在者違反本條。「已解析／provisional」之判定依 WM.21(d)(e)（未採認判準期間保守解釋為未解析）。

> **WM.12（近似性與來源保留）[N｜carries｜AUGUR-MC v1.4 §1.1 釐清句、§P2.E4]**
> Representation 永遠是帶不確定性之近似；忠實性體現於不確定性可追溯、錯誤可被新 Evidence 修正（`AUGUR-MC v1.4 §1.1` 釐清句）。每一 Representation 元素**必須**具備保留其 Observation 來源與不確定性之**結構位置**；**不得**存在被視為 Reality 本身之 Representation 元素。本條**不得**被任何細化（含 Annex A）削弱。
> **義務主體**：本規格、Layer 2–7 規格作者。**可判定判準**：任一 Representation 元素之結構定義含來源引用位置與不確定性位置（Confidence 之概念槽位，語義依 `AUGUR-MC v1.4 §2.10`、`§P4.E8` DEFER Layer 4，見 Annex D D9）者為合規；缺任一位置者違反本條。

> **WM.13（三性質可判定判準＋演化四不變式）[N｜refines｜AUGUR-MC v1.4 §2.3、§P2.D、§P2.W1、§P4.E6、§8.3 可判定性元規則]**
> `AUGUR-MC v1.4 §2.3` 所稱一致、可追溯、可演化三性質，其可判定判準如下：
>
> * **一致（consistent）**：同一世界事實在權威表徵層中不存在兩個未經顯式衝突標記（WM.16、WM.33）之相異值。
> * **可追溯（traceable）**：任一表徵元素可機器解析至終止於 Observation 或明示宣告假設（`AUGUR-MC v1.4 §P4.E6`）之引用鏈，無斷鏈、無循環引證。
> * **可演化（evolvable）**：任何表徵結構變更——含 schema、Ontology、Domain Profile、World Concept Registry（定義見 WM.36）之版本變更——**必須同時滿足四不變式**：
>   (i) 不刪除歷史；
>   (ii) 不中斷任何 Identity 之存續（WM.22）；
>   (iii) 不滅失任何標記（WM.33），且變更本身留有完整 provenance（「完整」＝至少含變更者 Identity、變更時間、依據引用、變更前後版本引用四項；本判準收錄 Annex E）；
>   (iv) **舊版本下確立之 Knowledge 之引用鏈，於新版本下必須仍可解析**。
>
> 判準未能適用之情形採保守解釋：**推定不滿足該性質**。
> **義務主體**：Layer 2–7 規格作者、一切表徵結構變更之提案者。**可判定判準**：如上三項及四不變式逐項判定；World Representation 承載一切 Prediction、Reasoning、Planning、Decision、Agent Action 之基礎地位（`AUGUR-MC v1.4 §P2.W1`）以此三性質之成立為前提。

> **WM.14（語義唯一性與一對多映射）[N｜refines｜AUGUR-MC v1.4 §P1.E2、§2.3；承接審計補正 AUD-06-R2]**
> 每一世界事實在系統內**必須**有且僅有一個權威 Representation。「唯一」指**權威地位唯一**，不指儲存份數，不預設集中式拓撲（拓撲屬下層部署決策，DEFER Layer 7，Annex D D18）。
> 同一世界事實**得**由多個 Observation Channel 供應：「世界事實 → 來源 Observation」之**一對多映射**為世界模型之必備結構；多通道值相異時依 WM.16 衝突保存；權威值之裁決為攜帶自身 Evidence 與 Confidence 之新 Knowledge（`AUGUR-MC v1.4 §P4.E5`），永不覆寫原始證據。
> **義務主體**：Layer 2–7 規格作者、World Concept Registry 之維護者。**可判定判準**：Registry（WM.36）中該世界概念之權威表徵欄**恰解析至一個**表徵載體者為合規；解析至零個或多個者違反本條。

> **WM.15（同一事實多通道之同一性宣告）[N｜refines｜AUGUR-MC v1.4 §P1.E2、§P4.E5；承接審計補正 AUD-14-R]**
> 凡兩個以上 Observation Channel 描述同一世界事實——含原始觀測與其衍生調整觀測（領域例示 [I]：原始成交價與經 CorporateAction 調整之還原價；規範性存在宣告見 A.58）——其**同一性宣告**與**擇用規則**必須**一次性作成為單一宣告**：宣告之**規範效力來源**為 Domain Profile [N] 條款（或其援引之 OPEN 保守預設），其**登錄形式**為 World Concept Registry 條目（機器可盤點載體，WM.36）。消費端必須引用世界概念，**不得**各自內嵌擇用規則。
> 有事證顯示兩通道疑似描述同一世界事實而尚無同一性宣告者，**必須**登錄為**顯式待決同一性存量**（與 WM.35 unmapped 存量同構，稽核指標準用 Annex D D4），Registry 維護者負宣告解決義務；待決期間依保守解釋**不得合併消費**。
> **義務主體**：Domain Profile 作者、Registry 維護者、一切消費模組之規格作者。**可判定判準**：「同一世界事實」以 Domain Profile 明文宣告為準——Profile 宣告存在**且** Registry 登錄與之可解析對應者為同一，**無宣告即非同一**（保守判準）；消費模組文件或程式內嵌通道擇用規則而未解析至該宣告者，違反本條。

> **WM.16（衝突與證據不足之表達力）[N｜carries｜AUGUR-MC v1.4 §P4.E5]**
> 世界模型**必須**能表達：
> (a) 互相衝突之 Evidence 共存並顯式標記（禁止 last-write-wins 之靜默消滅）；
> (b) 「目前證據不足」為合法系統狀態；
> (c) 衝突裁決結論為新 Knowledge，永不覆寫原始證據。
> **義務主體**：本規格（表達力保證）、Layer 2–7 規格作者（不得使之不可表達）。**可判定判準**：Layer 2–7 規格能為 (a)(b)(c) 各指定至少一個承載構件而無須修改本規格正文者，表達力成立；任一規格使 (a)(b)(c) 之一無承載位置者，違反本條。

> **WM.17（模態內容）[N｜refines｜AUGUR-MC v1.4 §1.3 模態內容釐清句、§2.3]**
> Hypothesis、Prediction、Plan 之預期狀態等模態內容，其 referent 為所繫結 Identity 之**可能狀態**，屬合法 Representation；**必須**攜帶顯式模態標記（標記位置依 WM.33）。未顯式標記為模態者，**不得**以可能狀態充當世界事實。模態內容同受來源與不確定性保留義務（WM.12）約束。
> **義務主體**：Layer 2–7 規格作者、一切產生模態內容之構件。**可判定判準**：任一模態內容元素攜帶 modal 標記且該標記依 WM.33 永久存續者為合規；無標記而進入權威表徵層者違反本條。

> **WM.18（候選斷言之地位與狀態轉換）[N｜refines｜AUGUR-MC v1.4 §P2.W2、§2.11、§P2.E1、§P2.E2、§P4.E5]**
> AI 產出**僅得**以附帶 Evidence 與 Confidence 之候選斷言（proposed assertion）進入系統；經 Evidence 通道（`AUGUR-MC v1.4 §2.11`，標準鏈之節選 EV.2–EV.5）確立後方取得權威地位；**得**以明示宣告之假設為遞迴終點（須顯式標記，assumption 標記依 WM.33）。
> 候選斷言之狀態語義為閉集：**candidate → established → superseded／retracted／invalidated**（後三態標記永存，`AUGUR-MC v1.4 §P4.E3`）。另設**正交狀態語彙 `insufficient-evidence`**：證據不足為合法且可表達之一級狀態（`AUGUR-MC v1.4 §P4.E5`），與上開生命週期狀態正交並存，供跨層互操作。
> 確立程序、欄位與工作流 DEFER Layer 4–5（Annex D D7、D14）。本條與 Knowledge 五元組（`AUGUR-MC v1.4 §P4.E1`）概念相容：欄位設計屬 Layer 4。
> **義務主體**：Layer 4–5 規格作者、一切產生候選斷言之構件。**可判定判準**：任一 AI 產出元素攜帶狀態值屬上開閉集且附 Evidence 與 Confidence 槽位者為合規；以 candidate 以外之途徑直接取得權威地位者違反本條。

---

## §4 Identity in the World Model（世界模型中之 Identity）[N]

> **WM.19（基本單位）[N｜carries｜AUGUR-MC v1.4 §P3.W1、§P3.D]**
> 世界模型之基本單位為 **Identity**；**不得**以 table row、file、document、embedding、model token 為基本單位。
> **義務主體**：本規格、Layer 2–7 規格作者。**可判定判準**：任一規格將世界事實之權威繫結對象定義為上開五類構件之一而非 Identity 者，違反本條。

> **WM.20（跨部署解析與命名空間不強制）[N｜refines｜AUGUR-MC v1.4 §P1.E2、§P3.E2]**
> Identity **必須**可跨部署邊界解析與對齊。本規格不預設亦不強制任何拓撲；**亦不課予 identifier 任何編碼或命名空間結構義務**——identifier 之鑄造、結構與命名空間屬 Layer 3 設計權（`AUGUR-MC v1.4 §P3.E2`，Annex D D5）。Layer 1 僅課「可跨部署解析與對齊」之**語義義務**。
> **義務主體**：Layer 3 規格作者。**可判定判準**：Layer 3 規格對任一 identifier 提供跨部署邊界之解析規則者為合規。本規格任何條款**不得**解釋為課予 identifier 結構義務；就此有解釋爭議者，依 `AUGUR-MC v1.4 §8.1` 由 Steward 裁決，裁決前依較嚴格解讀處理。

> **WM.21（結構位置義務與效力封印）[N｜hooks｜AUGUR-MC v1.4 §P3.E1、§P3.E3、§2.4；承接審計補正 AUD-06-R2；目標 Layer 2/3/5/6]**
> 世界模型**必須**提供下列結構位置；其內容依所載條款 DEFER：
>
> * **(a) 同一性判準宣告槽位**：每類 Identity 之同一性判準之**宣告槽位**。判準之制定與採認由 Layer 2／Layer 3 定義（`AUGUR-MC v1.4 §P3.E3`，Annex D D2）；Domain Profile 僅得設槽位並記載候選素材，**不負宣告義務**。
> * **(b) instance／type 繫結標記位置**：Knowledge 繫結對象屬個體（instance）或類型（type）之標記位置（`AUGUR-MC v1.4 §P3.E3`，DEFER Layer 2/3，Annex D D2）。
> * **(c) identity claim 一級物件位置**：identity claim（`AUGUR-MC v1.4 §2.4`）為一級物件之結構位置，含 identifier 對、判準引用、Evidence、Confidence；其表介面屬 Layer 3（Annex D D3）。
> * **(d) provisional identity 狀態**：未解析之 Observation **得**進入系統、**不得**升級為 Knowledge、系統負解析義務（`AUGUR-MC v1.4 §P3.E1`）；解析時限與未解析存量之可稽核指標 DEFER Layer 3（Annex D D4）。兜底可表達：凡意圖進入 Reasoning／Planning 之結構化物件（無論 Goal、Constraint、Capability、Plan 於 Layer 5–6 如何定義，Annex D D13）均落入已解析 Identity 引用義務，世界模型必須使此兜底可表達。
> * **(e) 效力封印一般規則**：Domain Profile 或任何 Layer 1 文件記載之候選同一性判準，一律標注 [I]，其地位為 **Layer 3 之輸入素材，經 Layer 3 採認前不生判準效力**；未經採認期間，涉該類 Identity 之引用一律採保守解釋（**視為未解析**）。
>
> **義務主體**：(a)–(d) 本規格與 Layer 2–3 規格作者；(e) Domain Profile 作者與一切消費者。**可判定判準**：(a)–(d) 各槽位之存在以「Layer 2/3 規格能為之指定承載構件而無須修改本規格正文」判定；(e) 以文件標注判定——凡候選判準記載未標注 [I] 或未附封印句者，該記載無效。

> **WM.22（生命週期存續不變式）[N｜carries｜AUGUR-MC v1.4 §P3.E2]**
> identifier 一經鑄造**永不刪除**；後續轉指全程可追溯；Identity 之 merge／split／retire 與更正，本身為**必須引用 Evidence 之 Knowledge**；identity lineage 全程保留；**Identity 存續跨越任何 Ontology／Representation 變更**（與 WM.13 演化四不變式 (ii) 互為引用）。轉指機制、法規抹除留痕（tombstone）與去識別化機制 DEFER Layer 3（`AUGUR-MC v1.4 §P3.E2`，Annex D D3）。
> **義務主體**：Layer 3 規格作者、一切表徵結構變更之提案者。**可判定判準**：任一表徵結構變更後，變更前存在之全部 identifier 仍可解析且其 lineage 完整者為合規；任一 identifier 於變更後不可解析者違反本條。

> **WM.23（實體類型開放例示）[N｜hooks｜AUGUR-MC v1.4 §P3.W2；目標 Layer 2]**
> 本規格沿用 `AUGUR-MC v1.4 §P3.W2` 之四類開放例示（Physical Entity／Abstract Entity／Dynamic Entity／Agentive Entity，包括但不限於）；完整分類體系 DEFER Layer 2 Ontology（Annex D D1）。
> Annex A 之世界概念清單為**存在宣告**（宣告此世界有何物、於何通道被觀測），**非分類體系**，不得解為對 Layer 2 定義權之預占。
> **義務主體**：本規格、Annex A、Layer 2 規格作者。**可判定判準（存在宣告／分類體系之切分）**：一條款僅斷言「某世界概念存在且為一級實體／事件／狀態／關係／量（WM.8）」者為存在宣告（合法）；一條款對世界概念課予窮盡之類屬架構、屬性集或子類劃分者為分類體系（屬 Layer 2，Layer 1 記載無效）。

---

## §5 World Evolution & State Change（世界演化與狀態變更）[N]

> **WM.24（canonical chain 承接）[N｜carries｜AUGUR-MC v1.4 §4、§1.2]**
> 本規格及 Layer 2–7 規格承接 `AUGUR-MC v1.4 §4` 之唯一權威標準鏈（canonical chain，EV.1–EV.12）與雙迴路語義：唯有 Action（EV.10）改變 Reality（因果迴路）；Feedback／Learning（EV.11–EV.12）僅改變表徵狀態，且其產出仍以候選斷言經 Evidence 通道（`AUGUR-MC v1.4 §2.11`）確立（認知迴路）；Human Authority Gate（EV.9）為授權鏈驗證點。
> 本規格及下層對標準鏈之引用，**一律**標注為節選（EV.x–EV.y）且**不得**跳過中間節點；**不得**重繪或改序。
> **義務主體**：本規格、Layer 2–7 規格作者。**可判定判準**：文中任一標準鏈引用均附節選標注且所列節點於 EV.1–EV.12 中連續者為合規。

> **WM.25（變更二分）[N｜refines｜AUGUR-MC v1.4 §2.1 表徵內容除外規則]**
> 世界模型**必須**落實「表徵狀態變更」與「Reality 變更」之二分：系統內 Representation 與 Knowledge 之內容變更為表徵狀態變更，不構成 `AUGUR-MC v1.4 §4` 因果迴路意義下之 Reality 變更；惟改變系統之權限、部署、物理資源或對外行為者，仍屬 Reality 變更。此二分為 P5 適用範圍（Action vs 純表徵變更）之概念前提。
> **義務主體**：Layer 2–7 規格作者、一切變更之提案者。**可判定判準**：任一系統內狀態變更，依 `AUGUR-MC v1.4 §2.1` 之字面規則可歸類為二分之一；歸類存疑者採保守解釋，視為 Reality 變更（受 P5 約束之較重義務側）。

> **WM.26（自反性）[N｜refines｜AUGUR-MC v1.4 §2.1 自反性條款]**
> 世界模型**必須**能表徵 Augur 自身——含其 Agent、Model、軟硬體與運行狀態——為 Reality 中之實體，得被觀測與表徵。
> **義務主體**：本規格、Annex A、Layer 2 規格作者。**可判定判準**：World Concept Registry 能登錄 Augur 自身構件之世界概念，且本規格及下層無任何條款排除之者為合規（Annex A A.20、A.19 為其領域落地）。

> **WM.27（Action 六元組世界事件與禁止型態之無位置性）[N｜carries｜AUGUR-MC v1.4 §P5.E1、§2.9、§6 F4–F6]**
> 世界模型**必須**能將 Action 表徵為攜帶六元組（Actor Identity、Authorization、Knowledge Basis、Timestamp、Expected Effect、Observed Effect）之世界事件（`AUGUR-MC v1.4 §P5.E1`）。
> 禁止型態於世界模型中**無合法表徵位置**：無 Identity 繫結、無 Source 之 Knowledge（`AUGUR-MC v1.4 §6 F4`）；無法回答「為什麼」之智慧輸出（`§6 F5`）；無法回答「誰發起、誰授權、憑什麼知識」之 Action（`§6 F6`）——本規格及下層**不得**為此三型態提供可合法容納之結構位置。
> 惟 **F6 違憲事件本身可表徵**：非經授權鏈而實際造成 Reality 變更之事件，必須以 Observation 回流並溯責於引致其發生之 Identity（`AUGUR-MC v1.4 §2.9`）；世界模型必須為此類事件之表徵、回流與溯責提供結構位置。
> **義務主體**：Layer 2–7 規格作者。**可判定判準**：任一 Action 事件之表徵可回答六元組六問者為合規；任一規格構件使 F4／F5／F6 型態得以無標記進入權威表徵層者，違反本條。

> **WM.28（人類權威表徵位置）[N｜hooks｜AUGUR-MC v1.4 §P5.W2、§P5.W5、§P5.E2、§P5.W3、§P5.W4、§P4.E7；目標 Layer 4、Layer 6]**
> 世界模型**不得**預先排除人工介入點、人類否決與 Human Authority Gate（EV.9）之表徵位置，亦**不得**設計任何在結構上降低人類監督與否決能力之概念構件（`AUGUR-MC v1.4 §P5.W5`）。
> 風險分級表、核准流程、確認者資格與獨立性判準 DEFER Layer 6；Evidence 完備性等級 DEFER Layer 4（`AUGUR-MC v1.4 §P5.E2`，Annex D D11、D16）。**缺位預設規則**（分級表生效前，一切意圖改變實體世界之 Action 一律視為最高風險等級、人類事前逐案核准）為 `AUGUR-MC v1.4 §P5.E2` 之直接效力；本規格引述之，**不削弱**。
> **義務主體**：本規格、Layer 2–7 規格作者。**可判定判準**：任一概念構件之引入，若使既有人工核准層級降低、人工介入點移除、或無人工檢核之自動執行鏈延長者，依 `AUGUR-MC v1.4 §P5.W5` 推定違反，不得實施。

> **WM.29（fail-safe 狀態容納）[N｜hooks｜AUGUR-MC v1.4 §P2.E5；目標 Layer 4–6]**
> 世界模型**必須**於概念上容納下列表徵狀態：「標記並重新評估」、「暫停」、「降級為觀測與建議模式」（`AUGUR-MC v1.4 §P2.E5` (a)(b)(c)）。錯誤或撤回之判定主體與程序、污染追蹤機制、觀測與建議模式之操作邊界，DEFER Layer 4–6（Annex D D15）；有爭議時由 Steward 裁決（`AUGUR-MC v1.4 §8.1`）。
> **義務主體**：本規格（表達力保證）、Layer 4–6 規格作者。**可判定判準**：Layer 4–6 規格能為上開三狀態各指定承載構件而無須修改本規格正文者，容納成立。

---

## §6 Time Semantics（時間語義）[N]

> **WM.30（雙時間性）[N｜carries｜AUGUR-MC v1.4 §P4.E2]**
> 任何 Observation 與 Knowledge **必須**區分 **valid time**（何時為真，可為區間）與 **transaction time**（系統何時得知）；任一過去時刻系統之認識狀態可追溯且可稽核為不變式；Timestamp 為 Knowledge 有效性宣稱之一部分，非元資料裝飾。
> as-of 重建機制與能力等級 DEFER Layer 4（`AUGUR-MC v1.4 §P4.E2`，Annex D D8；本域既有 anti-leakage 體系為其上呈素材，見 Annex B HOOK-01）。
> **義務主體**：Layer 4 規格作者、一切產生 Observation 與 Knowledge 之構件。**可判定判準**：任一 Observation 或 Knowledge 元素具二時間軸之獨立槽位者為合規；以單一時間值同時充當二軸者違反本條。

> **WM.31（時間屬性雙宣告）[N｜refines｜AUGUR-MC v1.4 §P4.E2、§8.3 可判定性元規則]**
> 每一 Observation Channel **必須**獨立宣告兩項時間屬性：
>
> * **(a) 時間戳語義**：其時間戳所指之世界時刻類型（開放列舉；例示 [I]：交易日、資料所屬期末、事件發生時刻、恢復生效日）。
> * **(b) 可知規則**：該 Observation 自何時起為系統可知或公開可得之**推導規則**（顯式時點欄、法定公開規則、或標記「待定錨」）。
>
> 二者**不得**混同；date 欄**不得**推定等於可知時刻。任一未宣告者採保守解釋：**該通道之資料推定不可用於任何 as-of 推理**。可知規則標記為「待定錨」者，**視同未宣告**，適用同一保守解釋（不可用於任何 as-of 推理），至定錨作成為止。可知性之座標化（如以第三時間軸建模）非本條所定，屬 Layer 4 之設計空間（Annex D D8）。
> **義務主體**：Domain Profile 作者、通道登錄之作成者（WM.35–36）。**可判定判準**：Registry 中該通道之時間屬性雙宣告欄二項俱全者為合規；缺任一項者該通道落入保守解釋。

> **WM.32（觀測定案性）[N｜carries｜AUGUR-MC v1.4 §P4.E3、§P4.E2]**
> Observation Channel **應**宣告其內容之定案性語義；**缺省規則**：未宣告定案性語義之通道，其全部觀測值**推定為未定案（non-final）**，攜帶 non-final 標記。「歷史觀測值被來源改寫」為**合法世界現象**，**必須**表徵為新 Observation 或新版本（新 transaction time），**不得**靜默覆寫；未定案者攜帶 **non-final 標記**（WM.33）。
> 定案性判準之**宣告形式**由 Domain Profile 宣告、由 Registry 逐資料集登錄（WM.36 第 7 欄），形式為**相對截止日之可判定述語**，**不得**內嵌具體日期於規範文本。supersede／tombstone 機制 DEFER Layer 4（Annex D D10）。
> **義務主體**：Domain Profile 作者、Observation Store 維運者。**可判定判準**：任一歷史觀測值之變動於 Observation Store 中留有新 transaction time 之獨立紀錄者為合規；原值遭覆寫且不可重建者違反本條。

---

## §7 Marking System（標記體系）[N]

> **WM.33（永久標記表達力）[N｜carries｜AUGUR-MC v1.4 §P2.E3、§P4.E3、§P4.E7、§1.3、§8.4]**
> 世界模型**必須**為下列規範性標記提供**永久性概念位置**：
>
> * **self-reported**（Agent 自我陳述之 Observation，`AUGUR-MC v1.4 §P2.E3`）
> * **synthetic**（AI 生成／合成內容，`AUGUR-MC v1.4 §P4.E7`）
> * **modal**（模態內容，WM.17）
> * **superseded／retracted／invalidated**（`AUGUR-MC v1.4 §P4.E3`）
> * **assumption**（明示宣告假設之遞迴終點，WM.18、`AUGUR-MC v1.4 §P4.E6`）
> * **provisional**（未解析 Identity 狀態，WM.21(d)）
> * **non-final**（未定案觀測，WM.32）
> * **conflict** 與 **insufficient-evidence**（WM.16、WM.18）
> * **豁免狀態與 Evidence 缺口標記**（`AUGUR-MC v1.4 §8.4`）
>
> 本清單為**開放列舉：下層得增列、不得刪減**。
> **永久性不變式**：標記一經附著，必須隨所標元素之一切轉引、衍生、聚合與表徵演化存續，不得滅失。
> 各標記之判定與流程 DEFER Layer 4–6（Annex D D10、D15、D16）。
> **義務主體**：本規格（表達力保證）、Layer 2–7 規格作者（存續義務）。**可判定判準**：任一衍生或聚合元素之引用鏈上游存在標記，而該元素未攜帶之者，即為標記滅失，違反本條。

---

## §8 Machine Auditability Basis（機器稽核基礎）[N]

> **WM.34（核心不變式之可機器稽核）[N｜carries｜AUGUR-MC v1.4 §8.3 末項]**
> 世界模型結構**必須**使下列核心不變式可機器稽核：
>
> * **(a) 引用鏈完整性**：Knowledge → Evidence → Observation 或明示宣告假設之引用鏈完整性。**判準**：任一 Knowledge 節點存在有限步可遍歷之引用路徑，終止於 Observation 或顯式標記之假設節點，無循環。
> * **(b) Action 之 Identity 歸因**。**判準**：任一 Action 事件存在至 Actor Identity 之單值繫結。
>
> 本規格及下層任何細化**不得**使 (a)(b) 不可機器稽核；稽核機制之實作 DEFER **Layer 1（§8.3 linter 之 compliance/audit 二軌）＋Layer 7（部署面之機器稽核載體）**（RULING-2026-018 具名層；併承 RULING-2026-017 §8.1「稽核工具自身輸出保真」解釋）。
> **義務主體**：本規格、Layer 2–7 規格作者。**可判定判準**：如 (a)(b) 內建判準；任一規格構件使該二判準之機器判定不可能者，違反本條。

---

## §9 世界概念註冊與消費紀律 [N]

> **WM.35（落地即整合；消費設閘不阻斷落地）[N｜refines｜AUGUR-MC v1.4 §P1.E2、§P2.E2、§P3.E1；承接審計補正 AUD-15-R]**
> 任何新 Observation Channel 於系統落地時，**必須**同時登錄其世界概念映射（該通道供應哪些世界概念、對應哪些世界事實；**得**先以人工策展為之）。
> 暫無對應世界概念者，**必須**登錄為 **unmapped 顯式存量**並列入解析義務（與 WM.21(d) provisional 同構；存量之可稽核指標準用 Annex D D4）。unmapped 或未登錄映射之通道，其資料**僅具 Observation 地位**——得保存、對帳、追溯，**不得**被消費為 Representation 或 Knowledge 之依據。
> **過渡規則**：本規格生效時**既存已落地通道**之映射登錄義務與其**既存消費**，準用 WM.36 所引 `AUGUR-MC v1.4 §8.3` 過渡規則 (b) 之 Steward 補正期（同一裁定、同一到期日）；自該到期日之翌日起，本條登錄與消費判準無條件適用。
> **義務主體**：通道落地之作成者、Registry 維護者、一切消費模組。**可判定判準**：任一已落地通道於 Registry 中存在映射登錄或 unmapped 標記者，落地合規；任一 Representation 或 Knowledge 之引用鏈（WM.34(a)）含 unmapped 或未登錄通道之 Observation 者，消費違規（既存通道於補正期內依上開過渡規則）。
>
> **[I] 條文註記**：「落地」與「本體整合」為同一動作之兩面，惟執法點設於**消費資格**而非落地阻斷——通用擷取（generic ingestion）之零重構落地為 `AUGUR-MC v1.4 §P2.E2` 語境下合法之觀測行為，本條不阻斷之；閘門僅設於升級為權威表徵與 Knowledge 依據之處。此設計使每新增一來源即豐富而非稀釋世界模型（審計所指負向棘輪之反轉）。

> **WM.36（World Concept Registry 與消費規則）[N｜refines｜AUGUR-MC v1.4 §P1.E2、§2.3、§8.3 過渡規則 (b)；承接審計補正 AUD-01-R4、AUD-06-R1]**
> 系統**必須**維護「世界概念 → 來源 Observation 位置」映射之 **World Concept Registry**（World Concept Registry ＝ 世界概念與其觀測通道映射之權威登錄結構，為 `AUGUR-MC v1.4 §2.3` Representation 之細化構件）為一級結構。登錄項最低含七欄：
>
> 1. **世界概念**（具名，繫結 Identity 語義）；
> 2. **歸類**（閉集：實體／事件／狀態／關係／量；「關係」「量」定義見 WM.8）；
> 3. **通道映射**（粒度至欄位級、一對多）；
> 4. **權威表徵指定**（WM.14）；
> 5. **通道時間屬性雙宣告**（WM.31；**含 A.35 第三項〔跨市場軸對映宣告〕，如適用**〔RULING-2026-030 §五(f)／AL-2026-033〕）；
> 6. **provenance**；
> 7. **定案性述語**（WM.32、A.37；得顯式載明「未宣告」，此時依 WM.32 缺省規則推定 non-final）。
>
> Registry 內容為世界模型之一部分，其變更為表徵狀態變更（WM.25），受版本化與可追溯義務（WM.13）約束；**Registry 條目本身為系統狀態，非本規格條文**，其增補不構成本規格升版。
> 任何消費世界模型之模組對世界事實之引用，**必須**以世界概念為鍵、經 Registry 解析至權威表徵，**不得**以來源位置字面（供應商表名、欄名、series 識別碼）直接繫結。既存直綁實作依 `AUGUR-MC v1.4 §8.3` 過渡規則 (b) 享 Steward 裁定之補正期；**自 Steward 補正期裁定所載到期日之翌日起**，前句禁令對其無條件適用，無待另為決定。
> Registry 之實作載體（既有 catalog 擴充、view、中介表等）為 [I] 資訊，非定義依據，DEFER Layer 4／Layer 7（Annex D D18）。
> **義務主體**：系統維運者（維護義務）、一切消費模組之規格作者（消費規則）、Steward（補正期裁定）。**可判定判準（登錄完成）**：登錄項七欄俱全且各欄可解析者為登錄完成；unmapped 為顯式合法過渡態（WM.35）。**可判定判準（消費合規）**：消費模組對世界事實之引用可解析至 Registry 之世界概念鍵者為合規；補正期屆滿後仍以來源位置字面繫結者違規。

> **WM.37（唯一權威表徵落實義務）[N｜refines｜AUGUR-MC v1.4 §P1.E2、§P4.E5；承接審計補正 AUD-06-R2]**
> 每一已註冊世界概念，下層規格**必須**為其指定唯一權威表徵之落點，並於多來源供應時預留衝突保存（`AUGUR-MC v1.4 §P4.E5`）之落點。
> **義務主體**：Layer 2–7 規格作者。**可判定判準**：依 WM.14 判準（權威表徵欄恰解析至一）＋該世界概念多通道時存在 conflict 標記之承載位置。

---

## §10 Bounded Representation（有界表徵）[N]

> **WM.38（自然人之有界表徵）[N｜carries＋hooks｜AUGUR-MC v1.4 §P1.E3；目標 Layer：L3（去識別化）／L6（法規對應表本體，RULING-2026-016 L6.9(d)）——見 Annex D D17]**
> 對自然人之 Observation 與 Representation，受**目的正當性、授權與所在法域法律義務**限制；合規義務與功能衝突時，**合規優先**。惟於合法觀測範圍內，對已觀測事實之忠實表徵義務（`AUGUR-MC v1.4 §1.1` PA）**不減損**——本條**不得**引為選擇性表徵（扭曲世界模型）之依據。具體法規對應 DEFER 下層（Annex D D17）。
> **義務主體**：Layer 3、Layer 6 規格作者、一切觀測與表徵自然人之構件。**可判定判準**：涉自然人之觀測通道於 Registry 登錄中載明目的與授權依據者方得消費（保守解釋：未載明即不允許）；於合法範圍內對已觀測事實之任何選擇性省略，如以本條為據，該援引無效。

---

## §11 Constitutional Compliance Statement Format（合規聲明格式）[N]

（[I] 本章之定義權依據載於 WM.39。）

> **WM.39（適用範圍與效力規則）[N｜refines｜AUGUR-MC v1.4 §8.3]**
> 本章（WM.39–WM.45）行使 `AUGUR-MC v1.4 §8.3` 明文授予 Layer 1 之唯一定義權：定義 Constitutional Compliance Statement 之聲明格式。本格式適用於 **Layer 1–7 全部規格**。無依本格式（或 `AUGUR-MC v1.4 §8.3` 過渡規則所定有效過渡聲明）作成之 Constitutional Compliance Statement 之規格，**不生效力**。
> **效力判定為機器可判**：front-matter（WM.40）缺任一欄位、本文（WM.41）缺任一原則論證節、或緊張關係節（WM.42）缺漏者，聲明不完整，規格不生效力。**空集合必須顯式為 `[]` 或 `none`**；缺載與空集合**不同視**。
> **義務主體**：Layer 1–7 全部規格作者。**可判定判準**：如本條內建之欄位存在性檢查與 WM.44 形式充分性判準。

> **WM.40（機器可稽核 front-matter）[N｜refines｜AUGUR-MC v1.4 §8.3、§8.6]**
> 聲明**必須**以結構化鍵值區塊起始，欄位為閉集：
>
> ```
> compliance-statement:
>   spec: {規格名稱}
>   spec-version: {版本}
>   layer: {1–7}
>   mc-version: AUGUR-MC v{version}
>   upper-specs: [AUGUR-WM v{version}, ...] | []   # 另受約束之上層規格版本並列；Layer 1 為 []
>   statement-format: AUGUR-WM v{version} §WM.39–45 | interim-template
>   principles: [PA, P1, P2, P3, P4, P5, EV-chain]  # 逐節論證存在性
>   waivers: [{編號, 範圍, 到期日, 補正計畫引註}] | []   # 四欄與 WM.42 同名對表
>   open-tensions: [{t-id}, ...] | []
>   defers-in: [{d-id}, ...] | []     # 承接上層之掛鉤
>   defers-out: [{d-id}, ...] | []    # 下放下層之掛鉤
>   date: {作成日}
>   author: {作者}
>   archive-path: {書面存檔之儲存庫相對路徑（依 WM.48 所定書面形式規則；**指本聲明所在之生效本**，非歸檔草案〔RULING-2026-030 §五(e)／AL-2026-033〕）}
> ```
>
> 欄位缺漏**視同無聲明**。`principles` 欄之 `EV-chain` 即 WM.41 第七節「§4 canonical chain」（同一節之兩表記，機器對表時同一）。
> **義務主體**：Layer 1–7 全部規格作者。**可判定判準**：上開欄位逐一存在性檢查；空集合顯式規則依 WM.39。

> **WM.41（逐原則論證本文）[N｜refines｜AUGUR-MC v1.4 §8.3、§8.6、§8.3 可判定性元規則]**
> 聲明本文**必須**含七節，順序固定：**PA、P1、P2、P3、P4、P5、§4 canonical chain**。每節逐項載明：
>
> * (a) 所引憲章條款，一律 `AUGUR-MC v{version} §{條款}` 格式（Layer 2–7 規格並引 `AUGUR-WM v{version} §WM.{n}`）；
> * (b) 合規模式，五值閉集：**滿足／細化（refines）／承接（carries）／DEFER（hooks；載明目標 Layer 與授權條款）／不適用（附理由）**。各值得以其括注之英文別名表記；與 §0.5 三態之明文對映：refines＝細化、carries＝承接、hooks＝DEFER。複合模式以「＋」連接閉集內二值以上表記之，仍屬閉集內用值；
> * (c) 合規論證文句；
> * (d) **判準揭示**：該節引用之每一評價性謂詞所附可判定判準，或聲明採保守解釋。
>
> **義務主體**：Layer 1–7 全部規格作者。**可判定判準**：七節存在且每節每項 (a)–(d) 俱全。

> **WM.42（緊張關係與豁免登記）[N｜refines｜AUGUR-MC v1.4 §8.3、§8.4]**
> 聲明**必須**含「已知緊張關係」節，逐項載明：所涉條款、描述、緩解或豁免狀態；無則明載 `none`。
> 豁免逐項登記，四欄：**編號、範圍、到期日、補正計畫引註**（與 WM.40 waivers 欄同名對表；`AUGUR-MC v1.4 §8.4`。豁免程序細則依治理附則〔生效後〕辦理；附則生效前依 `AUGUR-MC v1.4 §8.1` 缺位預設規則，以 Steward 書面裁決行之）。豁免期間產生之 Knowledge 之標記義務（`AUGUR-MC v1.4 §8.4`）於本節聲明落實方式。
> **義務主體**：Layer 1–7 全部規格作者。**可判定判準**：節存在性＋逐豁免四欄俱全。

> **WM.43（雙向 DEFER 承接表）[N｜refines｜AUGUR-MC v1.4 §8.3]**
> 聲明**必須**含承接表兩欄：
>
> * (a) **承接上層之掛鉤**：來源條款（上層規格條款號）→ 本規格承接條款號；
> * (b) **下放下層之掛鉤**：本規格條款號 → 目標 Layer 與預期承接事項。
>
> 與 front-matter 之 `defers-in`／`defers-out` 欄互為索引；DEFER 鏈完整性以本表為機器盤點依據。
> **義務主體**：Layer 1–7 全部規格作者。**可判定判準**：表中每列與 front-matter 對應欄雙向可解析。

> **WM.44（形式充分性判準）[N｜refines｜AUGUR-MC v1.4 §8.3、§8.2]**
> WM.41 論證之**形式充分性**為可判定：**`AUGUR-MC` 現行版全部 [N] 條款（以 `AUGUR-MC v1.4 §0.3` 條款編號系統枚舉；Layer 2–7 規格並及其各適用上層規格之全部 [N] 條款），均須對應至作成聲明之規格至少一條 [N] 條款、明記 DEFER 掛鉤、或明記「不觸及」及理由**；任一條款無對應且無明記者，聲明不完整，規格不生效力。**實質充分性**由違憲審查程序（`AUGUR-MC v1.4 §8.2`）判斷。
> **義務主體**：Layer 1–7 全部規格作者、違憲審查之聲請人與 Steward。**可判定判準**：如本條內建之對應完備性檢查。

> **WM.45（過渡承接）[N｜refines｜AUGUR-MC v1.4 §8.3 過渡規則 (a)(b)(c)]**
> 依 Steward 暫行模板作成之既存聲明**繼續有效**；其持有者**應**於下一次升版時換發為本格式，或於 Steward 裁定之補正期內換發。本規格自身之聲明（Annex C）依暫行模板作成，不因格式自我引用而無效（`AUGUR-MC v1.4 §8.3` 過渡規則 (c)）。依 `AUGUR-MC v1.4 §8.3` 過渡規則 (a)，暫行模板僅適用於聲明格式定義於 Layer 1 生效前之期間，其適用期間至本規格生效日屆至——**此為憲章規定之當然效果，非本規格所創設**；生效日後新作成之聲明必須依本格式。
> **義務主體**：Layer 1–7 全部規格作者、Steward。**可判定判準**：聲明之 `statement-format` 欄值與作成日對照本規格生效日判定。

---

## §12 Conformance & Continuity（合規與存續）[N]

> **WM.46（引用格式與編號穩定性）[N｜carries｜AUGUR-MC v1.4 §8.6、§0.3]**
> 下層引用本規格一律採 `AUGUR-WM v{version} §WM.{n}`（Annex 條款依 §0.3）格式。本規格條款編號一經發布**永不重用、永不重排**；廢止條款保留編號並標注 (repealed)。
> **義務主體**：本規格後續修訂者、Layer 2–7 規格作者。**可判定判準**：版本間 diff 檢查——任一既發布編號於後版消失或改指他文者違反本條。

> **WM.47（審查與豁免承接）[N｜carries｜AUGUR-MC v1.4 §8.2、§8.4、§8.1]**
> 本規格受 `AUGUR-MC v1.4 §8.2` 違憲審查程序約束。本規格全部「不得」（MUST NOT）義務**不得豁免**（`AUGUR-MC v1.4 §8.4`）；其餘 [N] 義務之豁免依 `AUGUR-MC v1.4 §8.4` 及治理附則（生效後）辦理，附則生效前依 `AUGUR-MC v1.4 §8.1` 缺位預設規則，以 Steward 書面裁決行之。本規格同位階條款衝突視為文件缺陷，修正前採較嚴格解讀（對系統許可較少、義務較重；與 `AUGUR-MC v1.4 §8.3` 保守解釋同向）。
> **義務主體**：Steward、本規格之一切消費者。**可判定判準**：豁免禁止以**個別義務文句**為判定粒度——豁免申請所涉之個別義務文句含「不得」者不受理；同條款內之「必須／應」義務文句得單獨申請豁免。

> **WM.48（重新認證與書面形式）[N｜carries｜AUGUR-MC v1.4 §8.6、§8.1]**
> `AUGUR-MC` major 升版時，本規格進入重新認證期（期限由 Steward 裁定，期內效力延續）。凡本規格要求「書面」「公開存檔」者，其形式與存檔位置依治理附則（生效後）所定；附則生效前（或附則就此缺位期間），依 `AUGUR-MC v1.4 §8.1` 缺位預設規則，以 Steward 書面裁決定之。
> **[I] 現況註記**：現行落實方式為登錄於本儲存庫 `constitution/` 目錄或 Steward 指定之規格目錄之文件，並以版本控制提交歷史為時間戳與不可否認性依據。此為 Layer 7 落實細節之資訊性轉載，非本條定義依據（WM.4 刪名測試適用）；規格存檔目錄（specs/）之書面地位業經 RULING-2026-002 主文四指定（準用治理附則第 6 條），解消記錄見 C.8 T-7。
> **義務主體**：Steward、本規格維護者。**可判定判準**：書面文件依 Steward 書面裁決（或生效後之治理附則）所定形式與位置存在且可公開查驗。

---

## §13 Domain Profile Framework（領域 Profile 框架）[N]

> **WM.49（地位與衝突規則）[N｜refines｜AUGUR-MC v1.4 §0.6(a)、§2 元規則]**
> Domain Profile（Domain Profile ＝ 對一特定領域宣告世界概念存在、通道登錄與時間語意之規範性 Annex，為 `AUGUR-MC v1.4 §2.3` Representation 之細化構件）為本規格之**規範性 Annex**，與正文同受一份 Compliance Statement 覆蓋、同一審查程序。
> Profile 牴觸正文或 `AUGUR-MC v1.4` 者，牴觸部分無效；Profile **不得**變更、削弱或重新定義正文任何通則與 `AUGUR-MC v1.4 §2` 任何術語。
> **義務主體**：Domain Profile 作者。**可判定判準**：Profile 任一條款經解釋與正文條款不相容者，該 Profile 條款無效（lex superior 於文件內之適用）。

> **WM.50（必備五部結構）[N｜refines｜AUGUR-MC v1.4 §P1.E2、§8.3 可判定性元規則]**
> 每一 Domain Profile **必須**含下列五部；除五部外，**僅得**另附「待決事項」節（見末段），**不得**含其他部：
>
> * **①實體／事件／狀態存在宣告**：錨定宣告——宣告某世界概念為一級實體、事件或狀態，細節 DEFER Layer 2（Annex D D20）；依 WM.23 判準，非分類體系。
> * **②候選同一性判準記載槽**：一律 [I]，適用 WM.21(e) 效力封印；無記載即依保守解釋處理（視為未解析）。
> * **③時間語意宣告**：領域最小粒度、每通道 WM.31 雙宣告表、定案性判準（WM.32 相對截止日述語）；**不得**內嵌營運日期。
> * **④通道登錄與世界映射**：含 Observation Store 認定（以通道特徵描述，產品名 [I]）；排除清單為閉集並附**排除理由類型**；排除為**通道級決定**，不得解為對世界實體存在之否認。
> * **⑤領域評價性謂詞判準與世界觀定位宣告**：對映 `AUGUR-MC v1.4` 原則之領域操作化，僅定位宣告並指認下層落點，不定機制。
>
> 另**得**附「待決事項」節：顯式未定義行為清單，**禁止下層以隱含假設消費**。
> **義務主體**：Domain Profile 作者。**可判定判準**：五部逐一存在性檢查（「待決事項」節之外無第六部）；任一部所載內容逾越該部定義（如①載入分類體系、②未標 [I]）者，該內容無效。

> **WM.51（越界禁止）[N｜carries｜AUGUR-MC v1.4 §0.5、§0.6(b)]**
> Profile **不得**載入：分類體系（Layer 2）、判準採認（Layer 3）、欄位／機制／流程設計（Layer 4–7）、Registry 具體條目（系統狀態，WM.36）。其提及之機制性內容一律 [I] 佐證或 DEFER 引用；其全部產品名提及**必須**通過 WM.4 刪名測試。
> **義務主體**：Domain Profile 作者。**可判定判準**：WM.23 切分判準＋WM.4 刪名測試＋WM.36「條目非條文」規則之逐條適用。

> **WM.52（版本節奏隔離）[N｜carries｜AUGUR-MC v1.4 §8.6]**
> 新增 Domain Profile 或增補既有 Profile，為本規格之 **minor 升版**事項，依治理程序議決，不構成 `AUGUR-MC v1.4 §0.5` 之新規格。**Profile 之任何變更不得觸動正文（WM.1–WM.53）條款文字**；正文變更另依其升版紀律（正文實質變更為 major、編輯修正為 patch，準用 `AUGUR-MC v1.4 §8.6` 版本語義）。**實質變更／編輯修正之可判定判準**：變更任一 [N] 條款之義務主體、規範動詞、可判定判準或閉集內容者為實質變更；其餘為編輯修正（本判準收錄 Annex E）。
> **義務主體**：本規格後續修訂者、Steward。**可判定判準**：Profile 升版之 diff 不含正文任何行之變更者為合規；正文升版等級依上開實質變更判準判定。

---

---

# Annex A [N] — Augur Domain World Model Profile（第一域：台灣證券市場）

> **A.0（地位與範圍）[N]**
> 本 Profile 依 §13（WM.49–WM.52）作成，為本規格之規範性領域 Profile。涵蓋領域：**台灣上市櫃證券市場**及其預測所需之全球金融與總體經濟觀測域。本 Profile 之領域前身文件為《系統核心思想》（[I] 引註，非定義依據；WM.6）。
> 本 Profile 各條之條款型態限於五種：**錨定宣告**（存在宣告，WM.23 判準）、**WM 正文條款之領域適用**、**領域評價性謂詞判準與定位宣告**（A-⑤ 各條，WM.50⑤ 判準）、**Profile 程序條**（A.55–A.56，WM.52 判準）、**待決條（OPEN，含保守預設）**。每條標注所覆蓋之領域需求編號（DOM-xx，見 Annex B 對照）。全部產品名、供應商名、資料集名為 [I] 引註並逐一通過 WM.4 刪名測試。
> **義務主體（概括載明，WM.5）**：本 Profile 之作者與後續修訂者（宣告、登錄與維護義務）、本 Profile 之消費者（Layer 2–7 規格與系統構件；消費紀律）。本 Profile 各條未逐條載明義務主體或可判定判準者，依本條概括載明**視同各條載明**（WM.5）。**可判定判準**：本 Profile 各條依其型態適用 WM.23、WM.21(e)、WM.50、WM.52 之判準。

## A-① 實體／事件／狀態存在宣告 [N]

### ①-1 實體存在宣告

各條格式：世界概念名｜存在宣告｜Observation Channel 指名 [I]｜覆蓋 DOM 編號。存在宣告之效力依 WM.23：僅宣告該世界概念為一級概念，分類體系與屬性集 DEFER Layer 2（Annex D D20）。

> **A.1（Security）[N]** 台灣上市櫃個股為一級 Physical Entity（市場標的；「市場標的」為開放例示之描述語，非類型宣告——類型體系 DEFER Layer 2，WM.23），具名稱、市場類別與產業歸屬等**隨時間變動**之屬性；**個股與非個股標的（指數、期權契約、外股、商品維度等）分層並存**，「非個股」**不得**為觀測排除理由。〔通道指名 [I]：金融資料供應商之股票基本資訊逐日快照資料集〕〔DOM-01〕

> **A.2（Roster）[N]** 名冊（市場成員名單）為獨立一級實體；其成員資格為**時間之函數**，非靜態集合。**錨定句：不得以當前成員集充當歷史成員集**（survivorship 禁令；歷史宇宙必須含當期已下市證券）。〔通道指名 [I]：股票基本資訊快照＋下市資料集〕〔DOM-02〕

> **A.3（Index）[N]** 市場指數為一級 Abstract Entity。本域存在**同一識別欄位空間承載不同實體類型**之世界事實（指數與個股共用識別欄位空間）；此為 Identity 解析之領域已知現象，識別欄位相同**不推定**實體類型相同。〔通道指名 [I]：報酬指數資料集、外國市場價格資料集〕〔DOM-03〕

> **A.4（TradingCalendar）[N]** 交易日曆為一級實體；**每一市場各有其交易日曆，日曆日 ↔ 各市場交易日對映均為一級世界關係**（世界關係定義見 WM.8）。任何以日曆日宣告之 horizon 於世界模型中必須可解析至本域交易日對映，對映偏差屬須揭露之表徵事實（揭露之硬綁機制 DEFER Layer 5/6，A.50）；跨市場觀測之本域軸對映語意見 A.35。〔通道指名 [I]：交易日資料集〕〔DOM-04〕

> **A.5（MarketParticipant 階層）[N]** 市場交易主體階層——機構法人（含外資、投信、自營商等類別）、行庫、大額交易人、券商、期權經紀商——為一級 Agentive／Abstract 實體族，為籌碼類觀測之行為主體維度。同一世界事實得以長表與寬表兩形供應（WM.15 同一性宣告適用）。〔通道指名 [I]：籌碼面各資料集〕〔DOM-05〕

> **A.6（DerivativeContract）[N]** 期貨與選擇權契約為具**生命週期**（上市→交易→結算消滅）之一級 Dynamic Entity，其屬性含買賣權別、履約價、交易時段、結算價、未平倉等。**形宣告**：契約月份識別欄之值域非日期值域（含價差組合與週合約形式）；此為世界事實之形，非資料缺陷。〔通道指名 [I]：衍生品各資料集〕〔DOM-06、DOM-25〕

> **A.7（ConvertibleBond）[N]** 可轉換公司債為具完整生命週期屬性（轉換期間、轉換價格、賣回權、提前贖回、下市）之一級實體，並具至標的股之一級世界關係。〔通道指名 [I]：可轉債各資料集〕〔DOM-07〕

> **A.8（Warrant）[N]** 權證為一級實體，具至標的股之對照關係與履約條款屬性。**權證實體之存在宣告與其分點交易通道之排除（A.42）並存**：排除為通道級決定，不否認實體存在。〔通道指名 [I]：權證對照摘要資料集〕〔DOM-08〕

> **A.9（ForeignSecurity）[N]** 外國市場證券（含外國指數）為一級實體，屬日級情境輸入之觀測對象；非台股標的仍屬應觀測之世界事實，不因非個股、非台股而排除。其識別欄位空間與本域個股不同。〔通道指名 [I]：國際股各資料集〕〔DOM-09〕

> **A.10（Commodity／FX／Rate／BondYield 維度族）[N]** 商品價格、匯率、政策利率、公債殖利率為 by-dimension 之一級世界量族（世界量＝以維度索引、隨時間取值之世界狀態量，定義見 WM.8，為 `AUGUR-MC v1.4 §2.3` Representation 之細化構件）；**維度全集以白名單宣告，禁臆測**（白名單之取得階層：來源動態列舉→官方文檔種子→名冊；此為通道登錄紀律，機制 DEFER Layer 4，Annex D D21）。「需特殊維度識別」不得為排除理由。〔通道指名 [I]：總經各資料集〕〔DOM-10〕

> **A.11（EconomicIndicator）[N]** 經濟指標為一級世界量實體：每一指標為**世界量，非任何供應商之 series 識別**。領域錨定例：「新台幣對美元匯率」為一個世界概念，兩個供應商通道 [I]（本國金融資料供應商之匯率資料集、外國聯儲經濟資料庫之對應 series）皆為其 Observation Channel；消費以世界概念鍵入（WM.36）。外部 series 清單以其單一權威來源（SSOT）指向引用，**不抄列**於本 Profile。〔DOM-11；承接審計補正 AUD-06-R1〕

> **A.12（IndustryClassification）[N]** 產業分類為一級雙層實體（市場分類與產業鏈分類），具治理效果之世界結構地位。**錨定句：某產業板塊制度性缺某類資料（如金融保險業無月營收申報制度）為世界結構事實，非資料缺陷**；其於成員資格判準之處理為條件性豁免（判準定位見 A.14，機制 DEFER Layer 4–6，Annex D D22）。〔通道指名 [I]：基本資訊與產業鏈資料集〕〔DOM-12〕

> **A.13（DataProvider）[N]** 資料供應商為**有行為之 Agentive Entity**：具授權階層、額度與限流行為、動態列舉與翻譯等周邊能力；其行為（如限流、拒絕）為可觀測之世界事件。系統對供應商之防護與額度紀律屬 Layer 4–7 機制（DEFER，Annex D D23）。〔通道指名 [I]：本國金融資料供應商、外國聯儲經濟資料庫〕〔DOM-13〕

> **A.14（Model 與 CoreUniverse）[N]** 預測模型與核心宇宙（模型消費之成員集）為系統內部一級實體（WM.26 自反性之領域適用）。**判準定位：核心宇宙成員資格為資料品質之函數，非投資價值之函數**（完整性 gate、流動性分位地板、產業條件豁免之具體機制 DEFER Layer 4–6，Annex D D22）。〔DOM-14、DOM-30〕

> **A.15（HumanDecisionMaker）[N]** 人類決策者為一級 Agentive Entity（僅存在宣告）；「系統建議、人決策」之授權語義見 A.53。存取控制（RBAC）機制 DEFER Layer 6（Annex D D24）；授權資料**不得**為預測特徵（隔離宣告，機制 DEFER，Annex D D24）。涉自然人表徵之域內宣告見 A.59。〔DOM-15〕

> **A.16（KnowledgeCorpus 語料實體族）[N]** 哲學與知識語料（學派、原則、思想家、著作、文本塊等）為一級實體族（存在宣告）＋**隔離宣告：素養語料不進預測管線**（其內容量化於預測域零證據價值；隔離之機器強制機制 DEFER Layer 5–7，Annex D D25）。license 三軌與私有內容邊界見 A.44。〔DOM-16、DOM-40〕

> **A.17（Catalog 元資料）[N]** 資料集與欄位之元資料目錄為一級內部實體，承載通道抓取語義與 provenance。**[I] 註記**：既有 catalog 結構為 World Concept Registry（WM.36）實作載體之既有基礎候選（實作屬 Layer 4/7，Annex D D18）；catalog 只驅動「怎麼抓」，不保證「資料對」（對帳獨立裁決，A.45 域內判準與 WM.10）。〔DOM-17〕

> **A.18（NewsEvent）[N]** 新聞為一級事件流實體；**事件時間軸 ≠ 交易日軸**——事件型觀測以事件發生時刻為時間戳語義（WM.31(a)），其抓取不得以交易日假設跳過非交易日。〔通道指名 [I]：新聞資料集〕〔DOM-18〕

> **A.19（GATE 預註冊實驗）[N]** 預註冊可證偽實驗（GATE）為具生命週期與審批狀態之一級 Dynamic Entity（WM.26 自反性適用）：實驗本身為世界中可觀測、可表徵之物件，非一次性腳本。其狀態機、統計治理與唯一產生路判準 DEFER Layer 4（HOOK-03，A.52）。〔DOM-47〕

> **A.20（Augur 自身）[N]** Augur 系統自身——含其 Agent、Model、軟硬體與運行狀態——為 Reality 中之實體，必須可被觀測與表徵（WM.26 之領域適用）。〔`AUGUR-MC v1.4 §2.1` 自反性條款〕

> **A.57（Issuer）[N]**（新增條款，依 §0.3 以新號編列、不重排，置於本部）發行人（公司）為一級 Agentive／Abstract Entity；**發行人與其所發行證券（Security、ConvertibleBond、Warrant）間之發行關係為一級世界關係**。財報與月營收公開事件（A.22）之世界 referent 為發行人（非證券）；產業分類（A.12）與月營收制度性豁免附著於發行人。「證券 Identity ≠ 發行人 Identity」為代碼重用／借殼問題（A.54 OPEN-1）之實體層落點；發行人同一性判準之制定與採認 DEFER Layer 2/3（WM.21(e) 效力封印維持，Annex D D2）。〔通道指名 [I]：股票基本資訊資料集之發行人屬性欄〕〔DOM-12、DOM-21、DOM-26 關聯；承接審計補正 AUD-01-R1〕

### ①-2 事件存在宣告

> **A.21（CorporateAction）[N]** 公司行動為一級世界事件族，含：**除權息**（其公告時點欄為 WM.31(b) 可知規則之顯式定錨；除權息使衍生調整觀測〔還原價〕之歷史值回溯重算——此為 WM.15 衍生觀測與 WM.32 定案性之交會點，回溯重算必須表徵為新版本而非靜默覆寫）、**減資、股票分割、面額變更**（皆為打斷價格連續性、以恢復買賣日為時間戳語義之參考價重設事件）。〔通道指名 [I]：股利、除權息結果、減資參考價、分割參考價、面額變更資料集〕〔DOM-19、DOM-23；承接審計補正 AUD-14-R〕

> **A.22（財報與月營收公開事件）[N]** 財務報告與月營收之**公開**為一級世界事件：資料所屬期末（date 欄語義）≠ 法定公開日 ≠ 系統可知日（WM.31 雙宣告適用）。**restatement（重編）為合法世界事件，非資料缺陷**，必須表徵為新 Observation 版本（WM.32）；重編與同步缺陷之區分為對帳處置判準（域內操作化 DEFER Layer 4，Annex D D26）。本事件之世界 referent 為發行人（A.57）。〔通道指名 [I]：財報三表、月營收資料集〕〔DOM-21、DOM-22〕

> **A.23（RegulatoryStateChange）[N]** 監理狀態變更——暫停交易、處置有價證券、暫停現股當沖、暫停融券賣出——為一級**期間型（interval）**世界事件／狀態：必須以起訖期間語義表徵（起始與終止各為時點，狀態於期間內持續），不得壓縮為單點事件。〔通道指名 [I]：監理狀態各資料集〕〔DOM-24〕

> **A.24（期權結算事件）[N]** 期貨與選擇權之最後結算為一級世界事件（契約生命週期終點，A.6 之生命週期宣告之對應事件）。〔通道指名 [I]：最後結算價資料集〕〔DOM-25〕

> **A.25（Delisting）[N]** 下市為一級世界事件。**錨定句：下市改變來源之當前可見性，不改變歷史真實性**——已下市證券之歷史觀測為合法歷史，來源不再回傳不構成刪除依據（對帳中「系統有、來源無」之差異須調查根因，不自動刪除；WM.32、WM.13(i)）。〔通道指名 [I]：下市資料集〕〔DOM-20〕

> **A.58（MarketTrade／DailyBar）[N]**（新增條款，依 §0.3 以新號編列、不重排，置於本部）逐證券逐交易日之**成交事實**（開高低收價、成交量值）為一級世界事件／狀態（日級聚合，A.34 粒度宣告適用）。**[N] 同一性宣告**：原始成交價通道與經 CorporateAction（A.21）調整之衍生通道（還原價）為**同一世界事實之兩個 Observation Channel**（WM.15 衍生觀測）；其同一性宣告與擇用規則以本條為規範效力來源，經 World Concept Registry 單一登錄（WM.15、WM.36；啟動條目見 Annex F 第 1 條），消費端不得各自內嵌擇用規則。還原價之回溯重算依 A.21 表徵為新版本，不得靜默覆寫（WM.32）。〔通道指名 [I]：日行情資料集、還原價資料集〕〔DOM-19、DOM-23 關聯；承接審計補正 AUD-14-R〕

### ①-3 狀態存在宣告

> **A.26（PriceLimit 漲跌停狀態）[N]** 每日參考價與漲跌停價為逐證券逐日之一級世界狀態；價格上下限制度為市場微結構之一級事實（影響報酬分布截斷與可交易性）。〔通道指名 [I]：漲跌停資料集、可轉債日行情之次日限價欄〕〔DOM-27〕

> **A.27（信用交易 stock-flow 狀態族）[N]** 融資融券、借券、當沖等信用交易狀態為日級 **stock-flow** 結構之一級狀態族（餘額＋當日流量；「昨日餘額＋當日增減＝今日餘額」為其共同形）。〔通道指名 [I]：籌碼面信用交易各資料集〕〔DOM-28〕

> **A.28（持股結構狀態）[N]** 外資持股、股權分級、市值與市值權重為一級世界狀態。其中申報異動日欄為 WM.31(b) 可知規則之顯式定錨；**國際證券識別碼（ISIN）為本域第二外部識別碼體系**（外部來源之指涉資訊，**非** WM.20／WM.22 意義下系統鑄造之 identifier；A.54 保守預設同旨），與本域主識別欄位之同一性以 identity claim 繫結（WM.21(c)），不以字面對映推定。〔通道指名 [I]：持股結構各資料集〕〔DOM-29〕

> **A.29（UniverseMembership）[N]** 核心宇宙成員資格為 **point-in-time** 之一級狀態：任一 as-of 時點之成員集必須可重建（WM.30；快照機制 DEFER Layer 4，Annex D D27）。〔DOM-30〕

> **A.30（DataFinality）[N]** 資料定案性為一級狀態（WM.32 之領域適用）：觀測值分「定案」與「未定案」（non-final 標記）；對帳差異分類與處置屬 Layer 4 機制（DEFER，Annex D D26），其結果為世界模型中之 Observation 層事實。〔DOM-31〕

## A-② 候選同一性判準記載槽 [N]（記載本體一律 [I]）

> **A.31（槽位設置）[N]** 本 Profile 為第①部宣告之每類實體設同一性判準**宣告槽位**（WM.21(a)）。本 Profile **不負宣告義務**；判準之制定與採認屬 Layer 2／Layer 3（Annex D D2）。無記載之實體類，涉其 Identity 之引用依保守解釋處理（WM.21(e)：視為未解析）。
> **義務主體**：本 Profile 之消費者。**可判定判準**：WM.21(e) 封印規則之逐類適用。

> **A.32（候選記載）[I]** 下列候選同一性判準為 **Layer 3 之輸入素材，經 Layer 3 採認前不生判準效力**（WM.21(e) 封印）；未經採認期間，涉各該類 Identity 之引用一律採保守解釋（視為未解析）：
>
> * Security：「供應商證券代碼字串相等 ∧ 存續期間重疊」（另見 OPEN-1 之保守預設）。
> * Index：「指數識別碼相等 ∧ 實體類型宣告為指數」。
> * DerivativeContract：「契約識別碼 × 契約月份識別 × 買賣權別 × 履約價之四元組相等」。
> * EconomicIndicator：「Domain Profile／Registry 明文宣告之世界量同一性」（WM.15；無宣告即非同一）。
> * MarketParticipant：「主體類別值 × 主體識別碼相等」。
>
> 本節任何記載**不得**以「暫採」「暫行判準」地位被消費。

> **A.33（第二識別體系之繫結）[N]** 凡本域存在多套**外部識別碼體系**（指涉資訊體系，非 WM.20／WM.22 意義下系統鑄造之 identifier）指涉同一實體（例：本域證券代碼與 ISIN），其同一性斷言一律為 identity claim（`AUGUR-MC v1.4 §2.4`，受 P4 約束之 Knowledge），經 WM.21(c) 結構位置承載；**不得**以欄位字面相等推定同一。〔DOM-29〕
> **可判定判準**：任一跨體系同一性斷言存在對應 identity claim 物件者為合規。

## A-③ 時間語意宣告 [N]

> **A.34（最小時間粒度）[N]** 本域最小時間粒度＝**日**（**域宣告，非全系統不變式**）。本條之排除對象為**觀測頻率粒度**：盤中週期性抽樣之市場觀測（tick、分線、盤中即時、五秒級等）不落地為本域 Observation。**時間戳精度本身不構成排除理由**：事件型觀測（A.18）以事件發生時刻（datetime）為時間戳語義者（WM.31(a)、A.35），**不落入本條排除**。
> 盤中來源之日級衍生值，以**來源當次回應內容**（具 Observation 地位）為限；系統自算之日級聚合值，其輸入觀測必須落地、或其計算依據標記為明示宣告假設（WM.33 assumption），否則不得存為 Observation（`AUGUR-MC v1.4 §P4.E6` 引用鏈終止要求）。
> 排除理由類型以 A.42 閉集為限：「粒度小於日」為其中之**資料本質排除**（世界觀測頻率粒度），「資料量物理界限」為**通道容量排除**（A.42 定義之區分）。〔DOM-32〕
> **可判定判準**：任一觀測通道屬盤中週期性抽樣且其抽樣頻率細於日者，依本條排除；事件型觀測通道（以事件發生時刻為時間戳語義者）不適用本條排除；其餘通道之最細時間鍵為日（或更粗）者屬本域範圍。

> **A.35（每通道時間屬性雙宣告）[N]** 本域每一 Observation Channel 必須依 WM.31 作成時間屬性雙宣告（時間戳語義＋可知規則），登錄於 Registry（WM.36 第 5 欄）。本域已知之時間戳語義類型（開放列舉 [I]）：交易日、資料所屬期末（季底、營收所屬月）、事件發生時刻（datetime）、除權息交易日、恢復買賣日、下市日。本域已知之可知規則定錨欄（[I] 例示）：公告日期／時間欄、申報異動日欄、資料建立時點欄、外部經濟資料庫之版本可見起日欄。任一通道未作成雙宣告者，依 WM.31 保守解釋：**不可用於任何 as-of 推理**。
> **跨市場觀測之本域軸對映**為本域每通道時間宣告之**第三項**：凡通道之時間鍵為外國市場交易日（A.9、A.4）者，必須宣告其對映至本域交易日軸之規則（含可知性之對映，如外國 t-1 收盤於本域 t 日之可知地位）；未宣告者依保守解釋不可用於本域 as-of 推理，**禁止下層以「同日即對齊」隱含假設消費**。〔DOM-34〕

> **A.36（通道時間模型不對稱之揭露）[N]** 本域存在**已知緊張關係**：外國經濟資料庫通道具逐版本雙時間（vintage）語義（歷史值修訂逐版存真、point-in-time 取版），本國市場通道則以法定公開規則與顯式時點欄近似可知時刻——兩通道之時間模型**不對稱**。本 Profile 如實揭露之（詳 Annex C 緊張關係 T-1）；統一之 as-of 重建能力等級屬 Layer 4 定義（Annex D D8、HOOK-01 上呈素材）。〔DOM-35〕
> **可判定判準**：本項揭露存在於 Compliance Statement 緊張關係節（WM.42）。

> **A.37（定案性判準之宣告形式）[N]** 本域定案性判準（WM.32）之宣告形式由本條定之、由 Registry 定案性欄（WM.36 第 7 欄）逐資料集登錄：形式為**相對截止日之可判定述語**（例示 [I]：「當日值於次一交易日收盤後定案」「季報值於法定申報期屆滿後定案」「還原價於無後續除權息事件之區間內定案」）；**不得**於規範文本內嵌具體營運日期。未登錄定案性述語之資料集，依 WM.32 缺省規則推定 non-final。「資料完整」為相對明文宣告截止日之可定案述語，非相對今日之浮動目標（該截止日本身為系統狀態登錄事項，非本規格條文）。〔DOM-31、DOM-36〕
> **可判定判準**：已登錄之定案性述語不含絕對日期字面；未登錄者依 WM.32 缺省規則判定（推定 non-final），無判定缺口。

> **A.38（預測任務之時間邊界＝模態邊界）[N]** 本域預測輸出為模態內容（WM.17），其**合法任務閉集由本條自足列舉**：
>
> * ①給定 as-of 日之未來 horizon **橫斷面相對強弱**；
> * ②**絕對方向機率**——唯經預註冊實驗（GATE，A.19、A.52）通過方得產出（判準定位，機制 DEFER Layer 4–5）。
>
> 〔[I] 出處引註：本閉集轉錄自領域治權文件之宣告；治權文件為 [I] 領域前身，非定義依據（WM.6），本條轉錄後閉集內容以本條為準。〕**永久除外項**（逐日價格點位、路徑、目標價）於世界模型中**無合法模態表徵位置**，任何此類輸出不得標記為 Prediction 進入表徵層（路徑模擬僅得以 synthetic＋modal 雙標記為模擬物件）。本閉集之增列為本 Profile minor 升版事項（WM.52）。〔DOM-37〕
> **可判定判準**：任一模態輸出之任務類型屬本條①②之一者為合規；屬永久除外項者違規；二者皆非且未經本條增列者，依保守解釋不允許。

## A-④ 通道登錄與世界映射 [N]

> **A.39（Observation Store 之域內認定）[N]** 本域 Observation Store（WM.10）之認定以通道特徵為之：**以最貼近來源之形逐值鏡像來源回應、並保有 byte-level 對帳（attestation）紀律之落地儲存**。「鏡像」之本義＝儲存中每值可 byte-level 追溯至某次來源回應（無第四類來源）。〔[I] 括注：現行落地為本國金融資料供應商各資料集之原始鏡像表；此指名通過 WM.4 刪名測試——刪去供應商名後，本條認定特徵不變。〕〔DOM-38、DOM-41；承接審計補正 AUD-01-R3〕
> **可判定判準**：WM.10 內建二特徵判準之域內適用。

> **A.40（「API 即權威」之定位限定）[N]** 本域治權文件既有「API 即權威」「API 是唯一事實」等宣稱，其效力範圍**限於 WM.9(a) 形權威**：權威範圍恰為來源當次回應之 schema、值域與 byte 內容；**不及於世界結構**（WM.9(b)）。〔DOM-38；承接審計補正 AUD-01-R2〕
> **可判定判準**：WM.9(a) 內建判準。

> **A.41（系統記錄之域內實例）[N]** 本域「一切資料之唯一儲存」宣告為 WM.9(c) **single system of record（唯一系統記錄）**之領域實例：系統內權威 Representation 之儲存地位，非「唯一真相來源」。〔[I] 指名：現行儲存選型為 Layer 7 事實，非定義依據；刪去選型名後本條內涵不變。〕下游治權文件措辭隨改為 patch 級事項（Annex D D19）。〔DOM-39；承接審計補正 AUD-26-R〕

> **A.42（排除閉集與排除理由類型）[N]** 本域觀測排除為**通道級決定**，不得解為對世界實體存在之否認（A.8 併存原則）。排除閉集及理由類型：
>
> * {券商分點、權證分點、鉅額分點}——理由類型：**資料量物理界限**（**通道容量排除**：通道容量事實，非世界排除；逐表判定，不逐實體判定）；
> * {盤中即時／tick／分線／五秒級觀測}——理由類型：**粒度小於日**（**資料本質排除**：A.34 觀測頻率粒度準則；事件型觀測〔A.18〕不落入本列，A.34）。
>
> 二理由類型之區分：**資料本質排除**以世界觀測之頻率粒度為據（A.34）；**通道容量排除**以通道之物理承載界限為據。排除理由類型以本閉集為限。
>
> 本閉集之變更為本 Profile 之 minor 升版事項（WM.52）。〔DOM-08、DOM-32、DOM-33、DOM-38〕
> **可判定判準**：任一排除決定可解析至上開閉集之一列及其理由類型者為合規；無理由類型之排除無效。

> **A.43（下市與可見性）[N]** 承 A.25：來源當前不回傳已下市證券之歷史，屬**來源可見性事實**；系統之歷史 Observation 不因此失效或刪除（WM.13(i)、WM.32）。對帳差異中「系統有、來源無」類之處置：調查根因、留痕、不自動刪除。〔DOM-20〕

> **A.44（語料通道之 license 三軌與隔離）[N]** 知識語料通道依授權型態分三軌閉集（公版原典；公版＋開放授權白名單；自有私有——**自有私有內容不得離開其授權邊界**之邊界宣告；該邊界之部署落實〔含本地部署等拓撲選擇〕DEFER Layer 5–7，Annex D D25。〔[I] 現況註記：現行落實為「永不離本機」之本地部署。〕）；**來源限真實文獻可溯源，AI 生成內容不得入語料庫**（clean-room；`AUGUR-MC v1.4 §P4.E7` synthetic 標記之域內強化）。「能抓≠該抓」：新知識域之入庫為人類決策事項（EV.9 語義，A.53）。隔離之機器強制機制 DEFER Layer 5–7（Annex D D25）。〔DOM-40、DOM-16〕
> **可判定判準**：任一語料入庫紀錄攜帶三軌之一之授權標記且具可溯源出處者為合規。

> **A.59（涉自然人通道之域內宣告）[N]**（新增條款，依 §0.3 以新號編列、不重排，置於本部）本域**已知涉自然人**之通道與表徵類型：系統內部人類使用者（HumanDecisionMaker，A.15）之表徵——其目的（授權鏈驗證與稽核溯責，`AUGUR-MC v1.4 §P5.E1`、EV.9）與授權依據，必須依 WM.38 於 Registry 登錄載明，方得消費。本域其餘現行觀測通道**明文宣告現未識別涉自然人內容**；如日後任一通道被認定涉自然人（候選例 [I]：券商登記資訊、大額交易人），其涉自然人判定與目的／授權依據載明納入 WM.35 落地登錄義務，載明前依 WM.38 保守解釋不得消費。〔DOM-15 關聯〕
> **可判定判準**：WM.38 內建判準之域內適用（Registry 載明目的與授權依據者方得消費；未載明即不允許）。

## A-⑤ 領域評價性謂詞判準與世界觀定位宣告 [N]

本部各條為 `AUGUR-MC v1.4` 原則之**領域操作化定位宣告**：僅定位並指認下層落點，不定機制（WM.50⑤）。

> **A.45（真兆三問）[N]** 本域「真兆」謂詞適用於**凡意圖作為預測或決策之 Knowledge 依據之斷言**（特徵、因子、假說等）；**單純 Observation 僅適用①②**（來源可解析＋可知規則），③自該 Observation 被消費為結論依據時起適用。其可判定形式——一斷言為真兆，若且唯若三問皆可肯定回答：
>
> * ①**有真實來源嗎**：存在可解析之 Observation Channel 與當次來源回應（＝`AUGUR-MC v1.4 §P4.E6` 遞迴終止於 Observation 之域內形式）；
> * ②**決策當下真的看得到嗎**：通過 WM.31 可知規則之 as-of 檢查（＝`AUGUR-MC v1.4 §P4.E2` 雙時間性之域內形式）；
> * ③**真的跑出來且 out-of-sample 撐住嗎**：存在依預註冊判準完成之樣本外 Evidence（＝P4 Evidence Before Conclusion 之域內形式；統計機制 DEFER Layer 4，HOOK-03）。
>
> 任一問不確定即採保守解釋：**當假兆處理**（存疑即不允許，`AUGUR-MC v1.4 §8.3`）。〔DOM-42〕

> **A.46（三敵框架＝防線組織）[N]** 本域防護體系以三敵組織，其憲章對映為定位宣告：①假資料（幻像）→ P1／PA 忠實表徵；②偷看未來（時間洩漏）→ `AUGUR-MC v1.4 §P4.E2` 雙時間性；③自我欺騙（灌水回報）→ `AUGUR-MC v1.4 §P4.E4`、`§P4.E5`、`§P2.E3`（self-reported 紀律）。防線之逐層機制屬 Layer 4–7（DEFER）。〔DOM-43〕

> **A.47（as-of 紀律為判準非實作）[N]** 「只用 as-of ≤ t 已知資訊」為本域一切回溯評估之**判準**（WM.30–31 之域內適用）；purged／embargo／發布日 gate 等為其實作機制，DEFER Layer 4（Annex D D8）。〔DOM-33〕

> **A.48（思想≠特定值）[N]** 外部思想（含哲學、經驗法則）得為候選假說之生成視角；**思想中之特定數值不得直接進入特徵公式**（hardcoded 值＝注入無 Evidence 之斷言，違 `AUGUR-MC v1.4 §P4.W1`）。**同一數值異層合法性規則**：同一數字於 operational 層（風控參數等）合法且須透明揭露，於特徵層非法——合法性繫於層位置，非數值本身。假說之入徵判準（可證偽→樣本外＋經濟裁決）DEFER Layer 4/5（Annex D D12、HOOK-02）。〔DOM-44〕
> **可判定判準**：任一特徵定義文句含非經 Evidence 通道確立之外生常數者，違規；operational 層常數具揭露紀錄者合規。

> **A.49（經濟價值≠準確率；防守靠規則）[N]** 本域「有經濟價值」謂詞之裁決以經濟度量與逐子期檢驗為之，**不以**分類準確率充當（判準定位；度量選集與門檻 DEFER Layer 4–6）。**防守優先以規則型機制建地板，預測型增強須證增量**——本判準未經下層形式化前採保守解釋：任何「可躲避市場崩跌」之宣稱不允許。〔DOM-45〕

> **A.50（誠實輸出契約之表達力承接）[N]** Layer 1 僅承接誠實輸出契約之**表達力**：模態標記（WM.17）、與輸出硬綁之揭露事實（基線、校準 provenance、歷史／即時標示、對映偏差等）於世界模型中有結構位置（WM.12、WM.33）。契約本體（產物閉集、硬綁五項、展示分級、fail-closed 閘）為 Layer 5/6 上呈素材（DEFER，Annex D D28）。〔DOM-46〕

> **A.51（管線分層本體論之角色對映）[N]** 本域管線分層（觀測擷取→特徵→宇宙→模型→驗證＋橫切稽核／目錄／語料）為 `AUGUR-MC v1.4 §5` 六抽象角色之領域組織形式（定位宣告）；「各層職責不越界」與單向隔離為域內架構不變式，其機器強制機制 DEFER Layer 5–7。驗證與訓練為兩個獨立消費者（不互讀產物）之語義屬 Evidence 獨立性（`AUGUR-MC v1.4 §P4.E7`「獨立」判準之域內對映）。〔DOM-48、DOM-14〕

> **A.52（假說與 GATE 之定位）[N]** 哲學與外部知識語料＝**假說，非真兆**（A.45③ 未成就前不得為 Knowledge 依據）；其進入 World Representation 之判準 DEFER Layer 4/5（HOOK-02）。預註冊可證偽實驗（GATE）為絕對方向輸出與即時准入之唯一產生路（判準定位）；其統計治理（多重比較、判準凍結、二次證偽封鎖）DEFER Layer 4（HOOK-03）。〔DOM-16、DOM-40、DOM-47〕

> **A.53（系統建議、人決策）[N]** 本域「系統建議、人決策」原則＝ Human Authority Gate（`AUGUR-MC v1.4 §4` EV.9）之領域落點：人類決策動作（核准、啟用、as-of 更新、授權政策、下單）為授權鏈驗證點之域內閉集（閉集內容之維護屬 Layer 6，DEFER，Annex D D16）。〔DOM-15〕

## A-⑥ 待決事項（OPEN）[N]

> **A.54（OPEN-1：stock_id 時間穩定性）[N]**
> 治權文件（閉集定義見 WM.9(a)）均未明文處理本域證券代碼之時間穩定性（改名、代碼重用、借殼）；其本質為「證券 Identity ≠ 發行人 Identity」之同一性問題，實體層落點見 A.57（Issuer）。本 Profile 將其登錄為**顯式未定義行為：禁止下層以隱含假設消費**（任何面板連接、宇宙成員資格、跨期 join 之規格，凡依賴「代碼＝穩定身份」假設者，必須顯式引用本條並載明假設）。〔DOM-26〕
>
> **保守預設 [N]**（合憲部分，`AUGUR-MC v1.4 §P3.E1` 定性）：供應商證券代碼為 Identity 之**指涉資訊**（可供 Identity Resolution 之資訊），**非**系統鑄造之 identifier；代碼重用、改名一律經 identity claim 表徵（WM.21(c)）。
>
> **候選判準記載 [I]**（WM.21(e) 封印適用）：「代碼相等 ∧ 存續期間重疊」。本記載為 Layer 3 輸入素材，經 Layer 3 採認前不生判準效力；未採認期間，涉該類 Identity 之引用一律保守解釋為未解析。正式判準待 Steward／決策層拍板、由 Layer 3 承接（Annex D D6）。
>
> **〔採認現況引註 [I]〕**：RULING-2026-014（2026-07-18）已依 ID.20 追認 Security／Index／FredSeries 操作化判準——**改名／借殼**殘留面覆蓋認定見 RULING-2026-030 §五(d)（維持保守預設至 Steward 認定）。

> **A.55（OPEN 節之消費規則）[N]** 本節所列每一 OPEN 項，其保守預設為 [N] 效力；候選記載為 [I] 素材。下層規格消費涉 OPEN 項之世界概念時，**必須**顯式引用該 OPEN 條並適用其保守預設。
> **可判定判準**：涉 OPEN 項之下層條款含對應 `AUGUR-WM v{version} §A.{n}` 引用者為合規。

> **A.56（Profile 增補程序）[N]** 本 Profile 之增補（新實體宣告、新通道登錄框架、新 OPEN 項）依 WM.52 為 minor 升版；不得觸動正文條款文字；不得載入 Registry 具體條目（WM.51；啟動條目見 Annex F [I]）。

---

# Annex B [I] — Traceability Matrix（需求對照表）

本附錄為資訊性對照，隨規格維護；規範效力悉依所引條款本文。

## B.1 MC 需求 → WM 條款

| 需求 | 憲章條款 | 落點 | 模式 |
|---|---|---|---|
| MC-01 | §0.5 | WM.3、§0.1 | 滿足 |
| MC-02 | §0.5、§0.6(a)、§8.2 | WM.1 | 滿足 |
| MC-03 | §0.6(a)(c) | WM.5、全文 [N] 條款體例 | 滿足 |
| MC-04 | §0.6(b) | WM.4 | 滿足＋細化（刪名測試） |
| MC-05 | §2 元規則 | WM.2 | 滿足 |
| MC-06 | §0.4 | §0.4 | 滿足 |
| MC-07 | §8.3 | §11（WM.39–45） | 細化（行使定義權） |
| MC-08 | §8.3 過渡規則 (a)(c) | WM.45、§0.1(b)、Annex C | 滿足 |
| MC-09 | §8.3 | Annex C | 滿足 |
| MC-10 | §8.3 可判定性元規則 | 全文逐條判準＋Annex E | 滿足 |
| MC-11 | §8.3 末項 | WM.34 | 滿足 |
| MC-12 | §8.6 | §0.3、WM.46 | 滿足 |
| MC-13 | P1.E1、P1.W1 | WM.7 | 細化 |
| MC-14 | P1.E2、§2.3 | WM.14、WM.20 | 細化 |
| MC-15 | P1.E2 末句 | WM.14、WM.20、D18 | 滿足＋DEFER L7 |
| MC-16 | P1.E3 | WM.38、D17 | 承接＋DEFER |
| MC-17 | §1.3 禁令一、PA、§1.1 | WM.11、WM.12 | 細化 |
| MC-18 | §1.3 模態釐清、§2.3 | WM.17 | 細化 |
| MC-19 | §1.3 模態釐清 | WM.17（禁止面） | 滿足 |
| MC-20 | P2.D、P2.W1、§2.3 | WM.13 | 細化（判準＋四不變式） |
| MC-21 | P2.W2、§2.11、P2.E1、P2.E2 | WM.18、D14 | 細化＋DEFER |
| MC-22 | P2.E4 | WM.12 | 承接 |
| MC-23 | P2.E5 | WM.29、D15 | hooks |
| MC-24 | §4、P2.E1、§1.2 | WM.24 | 承接 |
| MC-25 | §2.1 | WM.25、WM.26 | 細化 |
| MC-26 | P3.W1 | WM.19 | 承接 |
| MC-27 | P3.W2 | WM.23、D1 | hooks |
| MC-28 | P3.E3 | WM.21(a)(b)、D2 | hooks |
| MC-29 | P3.E1 | WM.21(d)、D4、D13 | hooks |
| MC-30 | P3.E2、§2.4 | WM.22、WM.21(c)、D3 | 承接＋DEFER |
| MC-31 | P4.E1 | WM.18（概念相容）、D7 | hooks |
| MC-32 | P4.E2 | WM.30、WM.31、D8 | 承接＋細化 |
| MC-33 | P4.E8、§2.10 | WM.12 判準註記、D9 | hooks（僅槽位） |
| MC-34 | P4.W1、P4.E3、P4.E7 | WM.32、WM.33、D10 | hooks |
| MC-35 | P4.E5 | WM.16 | 承接 |
| MC-36 | P5.E2、P5.W3、P4.E7 | WM.28、D11、D16 | hooks |
| MC-37 | P5.W5 | WM.28 | hooks |
| MC-38 | §6 F1 | WM.8 | 承接 |
| MC-39 | §6 F2、F3 | WM.8 | 承接 |
| MC-40 | §6 F4–F6、P5.E1、§2.9 | WM.27 | 承接 |
| MC-41 | §7 | WM.4、WM.8 | 承接 |
| MC-42 | §5、Appendix A | WM.4 | 滿足 |
| MC-43 | §8.2、治理附則（生效後） | WM.47 | 承接 |
| MC-44 | §8.4、治理附則（生效後） | WM.47 | 承接 |
| MC-45 | §8.6、治理附則（生效後） | WM.48 | 承接 |
| MC-46 | P2.E3、P4.E3、P4.E7、§1.3、§8.4 | WM.33 | 承接（開放列舉） |

## B.2 審計補正 → WM 條款

| 需求 | 落點 |
|---|---|
| AUD-01-R1 | WM.6＋Annex A ①⑤（顯式定位宣告，含 A.57 Issuer） |
| AUD-01-R2 | WM.9(a)、A.40 |
| AUD-01-R3 | WM.10、A.39 |
| AUD-01-R4 | WM.35–WM.37＋Annex F [I]（三步路徑之語義基礎：registry＝WM.36；直綁消除＝WM.36 消費規則＋過渡條款；唯一權威表徵＝WM.14/WM.37；補正期＝`AUGUR-MC v1.4 §8.3` 過渡規則 (b)） |
| AUD-06-R1 | A.11＋WM.36（世界概念鍵入） |
| AUD-06-R2 | WM.14（一對多映射）、WM.21(b)(c)、WM.37、A.32/A.33 |
| AUD-14-R | WM.15＋A.21＋A.58（MarketTrade/DailyBar 規範性存在宣告；原始價／還原價同一性宣告、擇用規則上收） |
| AUD-15-R | WM.35（落地即整合、unmapped 存量、消費設閘） |
| AUD-26-R | WM.9（三分）＋A.41＋D19 |
| AUD-12-R | §0.1 充任認定＋§1.2 [I] 建請（登錄屬 MC 修訂事項，非本規格所能自為——此為本項之明文 DEFER 理由） |

## B.3 上呈掛鉤（HOOK）

| 掛鉤 | 內容 | Layer 1 銜接點 | DEFER 理由 |
|---|---|---|---|
| HOOK-01 | anti-leakage 體系（發布日 gate、vintage、purged/embargo、point-in-time 快照）為 Layer 4 as-of 重建能力之上呈素材 | WM.30–31、A.36、D8 | 機制與能力等級屬 `AUGUR-MC v1.4 §P4.E2` 明定之 Layer 4 定義權；Layer 1 代定即違 WM.3 |
| HOOK-02 | 外部知識入 World Representation 判準（假說→可證偽→OOS＋經濟裁決） | A.48、A.52、D12 | 確立程序與工作流屬 Layer 4/5（`AUGUR-MC v1.4 §P2.W2`、§2.11 之下放面） |
| HOOK-03 | 預註冊 GATE 統計治理（判準凍結、多重比較、二次證偽封鎖） | A.19、A.52、D12 | 統計嚴謹化屬 Layer 4 Evidence 機制設計權 |

## B.4 DOM 需求 → Annex A 條款

DOM-01→A.1；DOM-02→A.2；DOM-03→A.3；DOM-04→A.4；DOM-05→A.5；DOM-06→A.6；DOM-07→A.7；DOM-08→A.8、A.42；DOM-09→A.9；DOM-10→A.10；DOM-11→A.11；DOM-12→A.12、A.57；DOM-13→A.13；DOM-14→A.14、A.51；DOM-15→A.15、A.53、A.59；DOM-16→A.16、A.52；DOM-17→A.17；DOM-18→A.18；DOM-19→A.21、A.58；DOM-20→A.25、A.43；DOM-21→A.22、A.57；DOM-22→A.22；DOM-23→A.21；DOM-24→A.23；DOM-25→A.6、A.24；DOM-26→A.54（OPEN-1）、A.57；DOM-27→A.26；DOM-28→A.27；DOM-29→A.28、A.33；DOM-30→A.14、A.29；DOM-31→A.30、A.37；DOM-32→A.34、A.42；DOM-33→A.42、A.47；DOM-34→A.35；DOM-35→A.36；DOM-36→A.37；DOM-37→A.38；DOM-38→A.39、A.40、A.42；DOM-39→A.41；DOM-40→A.16、A.44、A.52；DOM-41→A.39；DOM-42→A.45；DOM-43→A.46；DOM-44→A.48；DOM-45→A.49；DOM-46→A.50；DOM-47→A.19、A.52；DOM-48→A.51。

## B.5 明文非 Layer 1 事項（僅此註記 DEFER 理由；規範性掛鉤見 Annex D）

下列事項均為 Layer 4–7 機制，Layer 1 僅承接其所體現之不變式，代定即違 WM.3：抓取模式五態、限流防護、冪等 upsert、AST 稽核、DB trigger fail-closed、多重比較家族治理（Bonferroni）、RBAC 表設計、輸出契約本體、展示分級。其不變式承接點：抓取／冪等→WM.10、WM.32；隔離稽核→A.16、A.51；fail-closed→WM.29、A.50；RBAC→A.15；輸出契約→A.50。**上開事項之規範性 DEFER 掛鉤已逐項列入 Annex D（D21–D28）**，本節僅為理由之資訊性註記。

---

# Annex C [N] — 本規格之 Constitutional Compliance Statement

本 Annex 為**規範性聲明文件**（[N]）：其存在與內容為本規格之生效要件（§0.1(b)、`AUGUR-MC v1.4 §8.3`）。本聲明依 Steward 暫行模板作成（`AUGUR-MC v1.4 §8.3` 過渡規則 (a)(c)：Layer 1 自身之聲明依暫行模板作成，不因格式自我引用而無效）。**模板現狀揭露**：該暫行模板之文件識別、發布日與存檔路徑於本聲明作成時尚未經卷內引註確立；已於 §1.2(b) 建請 Steward 於充任認定同案發布（或追認）該模板並追認本聲明依其作成，本現狀併揭露於 C.8 T-7。為便利本規格生效後之換發（WM.45），本聲明**自願**同時滿足 §11 之格式要件。〔**生效註記**：上開建請業經 RULING-2026-002 主文三辦理完畢——模板發布於 constitution/COMPLIANCE-STATEMENT-INTERIM-TEMPLATE.md 並追認本聲明依其作成；解消記錄見 C.8 T-7。原揭露文句依歷史記錄保留。〕

```
compliance-statement:
  spec: Augur World Model Specification
  spec-version: v1.0
  layer: 1
  mc-version: AUGUR-MC v1.6
  upper-specs: []
  statement-format: interim-template   # constitution/COMPLIANCE-STATEMENT-INTERIM-TEMPLATE.md，RULING-2026-002 主文三追認
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: [T-1, T-2, T-3, T-5]   # T-4、T-6、T-7 經 RULING-2026-002 解消，留欄如 C.8 註記
  defers-in: []
  defers-out: [D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12, D13, D14, D15, D16, D17, D18, D19, D20, D21, D22, D23, D24, D25, D26, D27, D28]
  date: 2026-07-16
  author: 撰稿官（依 Constitution Steward 委辦之 Layer 1 起草程序）
  archive-path: specs/WORLD-MODEL-SPECIFICATION.md
```

## C.1 PA（Prime Axiom）

* 所引條款：`AUGUR-MC v1.4 §1.1`（含釐清句）、`§1.3`。
* 合規模式：滿足＋細化。
* 論證：本規格以 WM.7（Reality 優先於資料來源）、WM.11（referent 繫結）、WM.12（近似性與來源保留——直接承接 §1.1 釐清句「忠實不意謂完美鏡像」）、WM.13（可追溯判準）落實忠實表徵；WM.38 承接 P1.E3 與 PA 之位階釐清，明文禁止引有界表徵為選擇性表徵之依據。本規格未對 PA 作任何解釋性增刪（`AUGUR-MC v1.4 §8.5(d)` 之尊重）。
* 判準揭示：「忠實」不作為本規格自創謂詞使用；凡涉及即引 WM.12/WM.13 判準。「可靠」依 `AUGUR-MC v1.4 §1.3` 二分規則，本規格未另創判準，涉及處採保守解釋。

## C.2 P1（Reality First）

* 所引條款：`AUGUR-MC v1.4 §P1.D`、`§P1.W1`、`§P1.E1`、`§P1.E2`、`§P1.E3`。
* 合規模式：細化（P1.E1→WM.7；P1.E2→WM.14、WM.20、WM.35–37）；承接（P1.E3→WM.38）；DEFER（拓撲→D18；法規對應→D17）。
* 論證：WM.7 以開放列舉承接觀測通道；WM.8 以刪名測試落實 F1 禁令之可判定化；WM.9 權威三分消解「API 即權威」與「唯一真相來源」對 P1.E1 之表面牴觸；WM.36 Registry 使「所有資料來源必須映射至共同世界模型」具機器可盤點之落地形式。
* 判準揭示：「最高抽象」→WM.7 判準；「指名 vs 定義依據」→WM.4 刪名測試（Annex E）。

## C.3 P2（Representation Before Intelligence）

* 所引條款：`AUGUR-MC v1.4 §P2.D`、`§P2.W1`、`§P2.W2`、`§P2.E1`–`§P2.E5`。
* 合規模式：細化（三性質判準→WM.13；候選斷言→WM.18；模態→WM.17）；承接（P2.E4→WM.12；P2.E3 self-reported→WM.33）；DEFER（fail-safe 程序→D15；確立工作流→D14）。
* 論證：WM.13 為 §2.3 三性質給出可判定判準與演化四不變式（含跨版本引用鏈可解析），使 P2.W1「一切智慧活動建立於 World Representation」之前提可稽核；WM.18 之狀態閉集與 insufficient-evidence 正交狀態承接 P2.W2 權威順序與 P4.E5 表達力；WM.29 為 P2.E5 三反應狀態提供表達位置而不代定判定程序。
* 判準揭示：「一致／可追溯／可演化」→WM.13（Annex E）。

## C.4 P3（Identity Before Knowledge）

* 所引條款：`AUGUR-MC v1.4 §P3.D`、`§P3.W1`、`§P3.W2`、`§P3.E1`–`§P3.E3`、`§2.4`。
* 合規模式：承接（P3.W1→WM.19；P3.E2→WM.22）；hooks（P3.W2→WM.23/D1；P3.E3→WM.21(a)(b)/D2；P3.E1 解析指標→WM.21(d)/D4）；細化（identity claim 結構位置→WM.21(c)；效力封印→WM.21(e)）。
* 論證：本規格不自定任何同一性判準（Annex A 候選記載一律 [I] 封印，A.32、A.54），不課 identifier 結構義務（WM.20 明文排除），僅設結構位置與保守解釋規則——完整保留 Layer 2/3 定義權。provisional identity 之「得進入、不得升級、負解析義務」三句忠實承接 P3.E1；WM.11 明文容納 provisional referent，避免以「已解析」為 Representation 構成要件而牴觸 P3.E1。
* 判準揭示：「已解析／provisional」→WM.21(d)(e)（未採認期間保守解釋為未解析，Annex E）。

## C.5 P4（Evidence Before Conclusion）

* 所引條款：`AUGUR-MC v1.4 §P4.D`、`§P4.W1`、`§P4.E1`–`§P4.E8`。
* 合規模式：承接（雙時間→WM.30；矛盾保存→WM.16；標記→WM.33；引用鏈稽核→WM.34）；細化（時間屬性雙宣告→WM.31；定案性→WM.32）；DEFER（五元組欄位→D7；as-of 機制→D8；Confidence 形式化→D9；Evidence 分類法／tombstone／信任分級→D10；完備性等級→D11）。
* 論證：本規格未定義 Confidence 形式化語義（僅槽位，WM.12），未設計 Knowledge 欄位（WM.18 僅概念相容），未定 Evidence 分類法——P4 之全部 Layer 4 定義權完整保留。WM.31 之保守解釋（未雙宣告即不可用於 as-of 推理）與 §8.3 可判定性元規則同向。
* 判準揭示：「定案（final）」→WM.32／A.37；「真兆」→A.45；「經濟價值」→A.49（未形式化前保守解釋）（Annex E）。

## C.6 P5（Accountability Before Action）

* 所引條款：`AUGUR-MC v1.4 §P5.D`、`§P5.W1`–`§P5.W5`、`§P5.E1`、`§P5.E2`、`§2.9`。
* 合規模式：承接（六元組世界事件→WM.27；變更二分前提→WM.25）；hooks（風險分級／完備性／監督度量→WM.28、D11、D16）。
* 論證：本規格不定義「高風險」「高影響」（依 Layer 6 分級表，全憲章同一分級）；引述缺位預設規則時明文「不削弱」（WM.28）；WM.28 禁止設計降低監督之概念構件，並將 P5.W5 推定規則納入判準。EV.9 之領域落點以 A.53 定位而不代定 Layer 6 閉集內容。
* 判準揭示：「降低監督能力」→依 `AUGUR-MC v1.4 §P5.W5` 推定規則（本規格未另創判準，採其字面推定＋Steward 推翻程序）。

## C.7 §4 canonical chain

* 所引條款：`AUGUR-MC v1.4 §4`（EV.1–EV.12、雙迴路、EV.9、EV.5 語義註記）、`§1.2`。
* 合規模式：承接（WM.24）。
* 論證：本規格全部標準鏈引用均為節選標注（EV.2–EV.5、EV.9–EV.12 等）且節點連續；未重繪、未改序；認知迴路之「Learning 產出仍經 Evidence 通道」由 WM.18、WM.24 雙重承接。
* 判準揭示：節選連續性→WM.24 判準。

## C.8 已知緊張關係

| id | 所涉條款 | 描述 | 緩解／狀態 |
|---|---|---|---|
| T-1 | WM.30–31、A.36 vs `AUGUR-MC v1.4 §P4.E2` | 本域兩類通道之時間模型不對稱：外國經濟資料庫通道具逐版本 vintage 雙時間，本國市場通道以法定公開規則與顯式時點欄近似——as-of 重建能力不均質。 | 如實揭露；WM.31 雙宣告使不對稱顯式化；統一能力等級 DEFER Layer 4（D8、HOOK-01）。非豁免事項。 |
| T-2 | WM.9(c)、A.41 vs 治權文件既有「唯一真相來源」等措辭 | 下游治權文件之「真相／事實」措辭未隨 WM.9 三分收斂。 | patch 級隨改（D19）；過渡期間依 WM.9(c) 判準解釋，牴觸解釋無效。 |
| T-3 | WM.36 消費規則 vs 既存消費模組之來源位置字面直綁 | 既存實作以供應商表名／欄名直接繫結世界事實。 | 依 `AUGUR-MC v1.4 §8.3` 過渡規則 (b) 請 Steward 裁定補正期；到期翌日起禁令無條件適用；Annex F 為施工啟動集。 |
| T-4 | §0.1、Annex C | 本規格為 v0.1-draft：生效停止條件（充任認定）未成就；本聲明依暫行模板作成且格式自我引用。 | ✅ **已解消**（RULING-2026-002 主文一：充任認定作成，v1.0 生效；主文三：暫行模板發布並追認 Annex C）。原緊張關係記錄依編號穩定原則保留。 |
| T-5 | A.54（OPEN-1） | 本域證券代碼之同一性判準未經 Layer 3 採認，涉該類 Identity 之引用處於保守解釋（視為未解析）狀態。 | 保守預設 [N]＋候選記載 [I] 封印；**〔部分解消〕RULING-2026-014（2026-07-18）已依 ID.20 追認 T.1 Security（代碼重用依 ID.43 分裂、未退役期間唯一指涉）、T.2 Index、FredSeries 之操作化判準；改名／借殼殘留面續依保守預設（RULING-2026-030 §五(d)／AL-2026-033）**。D6 掛鉤之核心事項已有採認紀錄。 |
| T-6 | §1.2 [I] vs `AUGUR-MC v1.4 §0.5` | 五份治權檔尚未於 Layer 對照表定位登錄（AUD-12-R），治權體系存在雙重權威歧義風險。 | ✅ **已解消**（RULING-2026-002 主文二：五檔定位登錄，MC v1.3／AL-2026-006；檔頭從屬聲明依主文五交辦，期限 2026-10-14）。 |
| T-7 | Annex C 導言、WM.48、WM.40 vs `AUGUR-MC v1.4 §8.3` 過渡規則 (a)、§8.1 | 暫行模板之文件識別、發布日與存檔路徑未經卷內引註確立；本規格存檔於 specs/ 目錄之書面地位尚待 Steward 書面指定。 | ✅ **已解消**（RULING-2026-002 主文三：模板發布於 constitution/COMPLIANCE-STATEMENT-INTERIM-TEMPLATE.md 並追認 Annex C；主文四：specs/ 目錄書面地位指定，準用治理附則第 6 條）。 |

豁免登記：`none`（waivers: []）。豁免期間 Knowledge 標記義務之落實方式：本規格無現行豁免；如有，依 WM.33 豁免狀態標記位置落實。

## C.9 雙向 DEFER 承接表

* (a) 承接上層之掛鉤：Layer 1 之上層僅 `AUGUR-MC v1.4`；其全部 DEFER 授權之承接對照見 Annex B B.1（hooks 列）。`defers-in: []`（無上層規格層級之掛鉤）。
* (b) 下放下層之掛鉤：見 Annex D D1–D28（本規格條款號 → 目標 Layer → 憲章依據逐列）。

## C.10 形式充分性自查（依 WM.44 自願先行適用）

依 WM.44 判準自查：`AUGUR-MC v1.4` **全部** [N] 條款（依 `AUGUR-MC v1.4 §0.3` 條款編號系統枚舉），均對應至本規格至少一條 [N] 條款、明記 DEFER 掛鉤（Annex B B.1 hooks 列、Annex D），或明記「不觸及」及理由；§8.1（Steward 之設立與權力）之**效力面對應至 WM.47、WM.48**（carries——RULING-2026-018 更正 §8.1 之雙歸類：原同時列「不觸及」與 WM.47/48 carries，違 WM.44 三分互斥）；未觸及之 [N] 條款（**§8.5 修訂程序本體**）明記「不觸及」——理由：其規範對象為修憲程序自身，非 Layer 規格之義務來源。

**MC [N] 條款覆蓋清單（`§WM.44` 骨架自查，逐一具名以資機器盤點；落點見 Annex B／Annex D（hooks）及本規格 WM.44 自查敘述）[N]**：`PA`；`EV.1`、`EV.2`、`EV.3`、`EV.4`、`EV.5`、`EV.6`、`EV.7`、`EV.8`、`EV.9`、`EV.10`、`EV.11`、`EV.12`；`F1`、`F2`、`F3`、`F4`、`F5`、`F6`；`P1.D`、`P1.E1`、`P1.E2`、`P1.E3`、`P1.W1`；`P2.D`、`P2.E1`、`P2.E2`、`P2.E3`、`P2.E4`、`P2.E5`、`P2.W1`、`P2.W2`；`P3.D`、`P3.E1`、`P3.E2`、`P3.E3`、`P3.W1`、`P3.W2`；`P4.D`、`P4.E1`、`P4.E2`、`P4.E3`、`P4.E4`、`P4.E5`、`P4.E6`、`P4.E7`、`P4.E8`、`P4.W1`；`P5.D`、`P5.E1`、`P5.E2`、`P5.W1`、`P5.W2`、`P5.W3`、`P5.W4`、`P5.W5`；`§0`、`§0.1`、`§0.2`、`§0.3`、`§0.4`、`§0.5`、`§0.6`、`§1`、`§1.1`、`§1.2`、`§1.3`、`§2`、`§2.1`、`§2.2`、`§2.3`、`§2.4`、`§2.5`、`§2.6`、`§2.7`、`§2.8`、`§2.9`、`§2.10`、`§2.11`、`§3`、`§4`、`§5`、`§5.1`、`§5.2`、`§5.3`、`§5.4`、`§5.5`、`§5.6`、`§6`、`§7`、`§8`、`§8.1`、`§8.2`、`§8.3`、`§8.4`、`§8.5`、`§8.6`。各 `Pn.Y`（`P1.Y`、`P2.Y`、`P3.Y`、`P4.Y`、`P5.Y`）為 [I] 說理條款，本層以「不觸及＋理由：屬各原則之風險說理，非規範義務落點」統一處置（落點／不觸及理由見 Annex B／Annex D（hooks）及本規格 WM.44 自查敘述），為骨架覆蓋完備計於此具名。**誠實界限**：本清單＝機器盤點之字面具名；語意承接仍以 Annex TR 為權威，不因本清單宣稱新建語意矩陣或完成「決策四第二輪」嚴格強制。

---

# Annex D [N] — DEFER 掛鉤總表

> **D0（承接義務）[N]** 本表每列為**規範性掛鉤條款**：Layer 1 明示不定義該事項，授權（並要求）目標 Layer 定義之；目標 Layer 規格作成時必須於其 Compliance Statement 之 defers-in 欄承接對應列。
> **義務主體**：目標 Layer 規格作者。**可判定判準**：目標 Layer 規格之 WM.43 承接表含對應 D{n} 列。**可判定判準（範圍型目標列）**：目標 Layer 為範圍者，範圍內每一 Layer 之規格必須於其 Compliance Statement `defers-in` 欄與承接表承接該列之本層 slice，或於其 Traceability Matrix 對該列明記不觸及＋據實理由（RULING-2026-030 §二／AL-2026-033）。**範圍型列之各層 slice 分工必須登錄**於承接表或 Annex D 切片欄，以資 slice 聯集完備性盤點（RULING-2026-030 §五(g)）；**機器檢查**＝`tools/constitution_lint/annex_d_range_lint.py`（`report` 聚合；Steward 授權最佳化拍板 2026-07-23 落地）。

| # | DEFER 事項 | 目標 Layer | WM 掛鉤 | 憲章依據 |
|---|---|---|---|---|
| D1 | Identity 實體類型完整分類體系 | L2 | WM.23 | `AUGUR-MC v1.4 §P3.W2` |
| D2 | 每類 Identity 同一性判準之制定與**採認**；instance/type 分類 | L2/L3 | WM.21(a)(b)(e) | `AUGUR-MC v1.4 §P3.E3` |
| D3 | identity claim 一級表介面、轉指機制、tombstone、去識別化 | L3 | WM.21(c)、WM.22 | `AUGUR-MC v1.4 §P3.E2`、`§2.4` |
| D4 | provisional identity 解析時限與未解析存量稽核指標（含 WM.35 unmapped 存量準用） | L3 | WM.21(d)、WM.35 | `AUGUR-MC v1.4 §P3.E1` |
| D5 | identifier 之鑄造、結構與命名空間設計 | L3 | WM.20 | `AUGUR-MC v1.4 §P3.E2` |
| D6 | 本域證券代碼身份假設之判準採認（改名／代碼重用／借殼；Steward／決策層拍板後承接） | L3 | WM.21(e)、A.54 | `AUGUR-MC v1.4 §P3.E3` |
| D7 | Knowledge 五元組欄位設計 | L4 | WM.18（概念相容） | `AUGUR-MC v1.4 §P4.E1` |
| D8 | as-of 重建機制與能力等級（vintage、發布日 gate、embargo、purged 口徑——HOOK-01 上呈素材） | L4 | WM.30、WM.31 | `AUGUR-MC v1.4 §P4.E2` |
| D9 | Confidence 形式化語義、傳播、比較 | L4 | WM.12、WM.18 僅槽位 | `AUGUR-MC v1.4 §P4.E8`、`§2.10` |
| D10 | Evidence 三分類法維護、supersede/tombstone、來源信任分級表 | L4 | WM.32、WM.33 | `AUGUR-MC v1.4 §P4.W1`、`§P4.E3`、`§P4.E7` |
| D11 | Evidence 完備性等級 | L4 | WM.28 引述 | `AUGUR-MC v1.4 §P5.W3`、`§P5.E2` |
| D12 | 外部知識入 World Representation 判準（假說→可證偽→OOS＋經濟裁決）；GATE 預註冊體系 | L4/L5 | A.48、A.52 | `AUGUR-MC v1.4 §P2.W2`、`§2.11`（HOOK-02、HOOK-03） |
| D13 | Goal、Constraint、Capability、Plan 之定義 | L5–L6 | WM.21(d) 兜底 | `AUGUR-MC v1.4 §P3.E1` |
| D14 | 確立程序與候選斷言工作流 | L4–L5 | WM.18 | `AUGUR-MC v1.4 §P2.W2` |
| D15 | fail-safe 判定主體／程序、污染追蹤、觀測建議模式邊界 | L4–L6 | WM.29 | `AUGUR-MC v1.4 §P2.E5` |
| D16 | 風險分級表、核准流程、確認者資格與獨立性、監督否決度量 | L6 | WM.28、A.53 | `AUGUR-MC v1.4 §P5.E2`、`§P5.W5`、`§P4.E7` |
| D17 | 自然人法規對應表 | L3/L6 | WM.38 | `AUGUR-MC v1.4 §P1.E3` |
| D18 | 部署拓撲（集中／聯邦）、Registry 實作載體、直綁消除技術手段 | L7（機制）/L4（登錄結構） | WM.14、WM.20、WM.36 | `AUGUR-MC v1.4 §P1.E2` |
| D19 | 治權文件「唯一真相來源」等措辭之收斂：L4–L7 規格引用治權文件時依 WM.9(c) 判準解釋，並於其聲明緊張關係節（WM.42）揭露收斂狀態；治權檔本身之 patch 為 Steward 程序事項（§1.2(d) 建請，非本列承接義務之對象） | L4–L7 | WM.9(c)、A.41 | `AUGUR-MC v1.4 §2.1`–`§2.3` |
| D20 | 領域完整本體（Annex A 錨定概念之細分類、屬性、關係） | L2 | WM.23、Annex A ① | `AUGUR-MC v1.4 §P3.W2` |
| D21 | 維度白名單之取得機制（來源動態列舉→官方文檔種子→名冊） | L4 | A.10 | `AUGUR-MC v1.4 §P2.E2` |
| D22 | 核心宇宙完整性 gate、流動性分位地板、產業條件豁免機制 | L4–L6 | A.12、A.14 | `AUGUR-MC v1.4 §P4.W1` |
| D23 | 資料供應商防護與額度紀律（限流、額度、防護模式） | L4–L7 | A.13 | `AUGUR-MC v1.4 §0.5`（層級分工） |
| D24 | 存取控制（RBAC）機制；授權資料不入預測特徵之隔離強制 | L6 | A.15 | `AUGUR-MC v1.4 §P5.E2` |
| D25 | 語料隔離之機器強制；自有私有內容授權邊界之部署落實（含本地部署拓撲） | L5–L7 | A.16、A.44 | `AUGUR-MC v1.4 §P4.E7` |
| D26 | 重編（restatement）與同步缺陷之區分、對帳差異分類與處置 | L4 | A.22、A.30 | `AUGUR-MC v1.4 §P4.E3` |
| D27 | point-in-time 成員資格快照機制（D8 as-of 能力之領域配套） | L4 | A.29 | `AUGUR-MC v1.4 §P4.E2` |
| D28 | 誠實輸出契約本體（產物閉集、硬綁揭露五項、展示分級、fail-closed 閘） | L5–L6 | A.50 | `AUGUR-MC v1.4 §P2.E5`、`§P4.E4` |

---

# Annex E [N] — 自創評價性謂詞判準彙整表

> **E1（收錄義務）[N]** 本表為 `AUGUR-MC v1.4 §8.3` 可判定性元規則之**單一盤點構件**：本規格（含 Annex A）自創或域內操作化之每一評價性謂詞，其可判定判準所在條款彙整如下。正文或 Profile 如增列自創謂詞，**必須**同步收錄本表；未收錄且未附判準之謂詞，一律採保守解釋（存疑即不允許）。
> **義務主體**：本規格後續修訂者。**可判定判準**：全文謂詞掃描與本表逐列對照之完備性檢查。

| 謂詞 | 判準所在 |
|---|---|
| 一致／可追溯／可演化（含演化四不變式） | WM.13 |
| 唯一權威表徵 | WM.14（Registry 權威表徵欄恰解析至一） |
| 同一世界事實 | WM.15（Profile [N] 宣告存在＋Registry 登錄可解析對應；無宣告即非同一；疑似同一而未宣告者為顯式待決存量） |
| 指名 vs 定義依據 | WM.4（刪名測試） |
| 已解析／provisional | WM.21(d)(e)（未採認判準期間保守解釋為未解析） |
| 表徵狀態變更 vs Reality 變更 | WM.25（存疑視為 Reality 變更） |
| 定案（final）／未定案（non-final） | WM.32、A.37（逐資料集相對截止日述語） |
| 登錄完成／unmapped | WM.36（七欄俱全且可解析；unmapped 為顯式合法過渡態） |
| 聲明完整／形式充分 | WM.39、WM.44（front-matter 全欄俱全＋七節論證存在＋MC [N] 條款對應完備） |
| 存在宣告 vs 分類體系 | WM.23（切分判準） |
| 真兆／假兆 | A.45（三問逐項可判定；任一不確定即當假兆） |
| 資料完整 | A.37（相對明文截止日之可定案述語） |
| 有經濟價值 | A.49（定位判準；未經 Layer 4–6 形式化前採保守解釋） |
| 排除（通道級） | A.42（閉集列＋理由類型俱全方有效；資料本質排除／通道容量排除之區分見 A.34、A.42） |
| 實質變更／編輯修正（升版分類） | WM.52（變更任一 [N] 條款之義務主體、規範動詞、判準或閉集內容者為實質變更） |
| 完整 provenance（表徵結構變更） | WM.13(iii)（變更者 Identity、變更時間、依據引用、前後版本引用四項最低欄集） |

---

# Annex F [I] — 首批 World Concept Registry 啟動條目（隨卷附件）

**地位聲明**：本附件為審計補正 AUD-01-R4 之**施工啟動集**，屬系統狀態之初始化素材，**非規範條文**；其採認與登錄由 Steward 附卷裁定，其後之維護悉依 WM.36，增補不觸動本規格版本。每條含（對應 WM.36 七欄）：世界概念｜歸類｜通道映射｜權威表徵指定｜時間屬性雙宣告要點｜定案性述語要點（未載者依 WM.32 缺省規則推定 non-final）｜provenance 要點。**各條 provenance 要點共同載明**：來源＝所列通道之當次回應；作成依據＝本規格起草程序（審計補正 AUD-01-R4 隨卷）；採認狀態＝待 Steward 附卷裁定。

1. **MarketTrade/DailyBar**｜事件／狀態（日級成交）｜兩通道：原始成交價通道＋含 CorporateAction 調整之衍生通道（WM.15 衍生觀測；供應商資料集名於登錄時 [I] 註記）｜同一世界事實之同一性宣告與擇用規則**單一登錄**（規範效力來源：A.58；AUD-14-R 落地）｜時間戳語義：交易日；可知規則：收盤後當日可得、次一交易日定案述語適用。
2. **CorporateAction.除權息**｜世界事件｜股利與除權息結果通道｜權威表徵指定於事件概念｜時間戳語義：除權息交易日；可知規則：**公告時點欄為可知規則錨**（WM.31(b)）。
3. **EconomicIndicator.新台幣對美元匯率**｜世界量｜兩供應商通道（本國供應商匯率資料集＋外國經濟資料庫對應 series）｜**一權威表徵指定＋衝突保存落點**（AUD-06-R1/R2 落地）｜時間戳語義：觀測日；可知規則：依通道各自宣告（vintage 通道逐版）。
4. **TradingCalendar**｜世界關係（日曆日↔交易日）｜交易日通道｜單通道權威｜時間戳語義：交易日；可知規則：事前公告之市場日曆。
5. **Roster 成員資格**｜世界狀態（point-in-time）｜基本資訊快照＋下市通道｜權威表徵為時間函數之成員資格概念（A.2 survivorship 禁令適用）｜時間戳語義：快照日；可知規則：快照當日。
6. **Delisting**｜世界事件｜下市通道｜單通道權威（A.25 可見性語義適用）｜時間戳語義：下市日；可知規則：主管機關公告。

其餘通道之登錄依 WM.35–WM.36 過渡規則辦理（不載計數與進度語）。

---

*本規格計：正文條款 WM.1–WM.53、Annex A 條款 A.0–A.59、Annex D 掛鉤 D0–D28、Annex E 判準表（E1）、Annex C 合規聲明 [N]。全文以繁體中文為權威文本（§0.4）。*

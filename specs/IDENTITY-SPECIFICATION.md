# 《Augur Identity Specification》

Augur Enterprise AI Operating System
身份系統規格（Layer 3 — Identity System）
引用縮寫：**AUGUR-ID**｜版本：**v1.0**（前版：v0.1-draft）
受 **AUGUR-MC v1.4** 全文約束（`AUGUR-MC v1.4 §0.6(a)` lex superior、`§0.5` 對照表 Layer 3 欄）
並受 **AUGUR-WM v1.0** 全文約束（`AUGUR-MC v1.4 §0.6(a)`、`AUGUR-WM v1.0 §WM.1`）
並受 **AUGUR-ONT v1.0**（Layer 2）承接約束（`AUGUR-MC v1.4 §0.6(a)`）

---

> ## 【地位】[N]
>
> 本文件為 **v1.0 生效版本**。Constitution Steward（tsaitsangchi）已於 2026-07-17 依 `AUGUR-MC v1.4 §0.5`、`§8.6` 作成**充任認定**（Steward 裁決第 2026-004 號，Amendment Log AL-2026-008）：本文件充任 `AUGUR-MC v1.4 §0.5` 對照表 Layer 3「Identity System」欄所轄之「Identity Specification」，`§0.1` 生效要件全部成就（Layer 對照表登錄、Compliance Statement、`§WM.44` 形式充分性成就〔Annex TR 逐條完整枚舉、缺 0 條〕、linter 結構關卡通過、上層 `AUGUR-ONT v1.0` 已先行生效），**自 2026-07-17 起生效**。`v0.1-draft` 原文歸檔於 `specs/IDENTITY-SPECIFICATION-v0.1-draft.md`；draft → v1.0 之變更僅限：版本欄、本【地位】節生效記錄、Annex CS front-matter spec-version，**無任何 [N] 條款實質變更、條款編號（ID.{n}／AO.{n}／IDO.{n}／CS.{n}／L4.{n}）不重排**。
>
> * 本文件全部 [N] 條款自生效日起對 Layer 4–7 規格產生規範效力；下層依 `AUGUR-ID v1.0 §{條款}` 格式引用。落實審計 AUD-04／05／06（§P3 家族細化）。
> * **形式充分性**：Annex TR（TR.A–TR.Z）就三上層（`AUGUR-MC v1.4`／`AUGUR-WM v1.0`／`AUGUR-ONT v1.0`）全部 [N] 條款逐條完整枚舉、缺 0 條（對抗審查查出之 §0.2／§1.2／§1.3／§7／§8.5 缺列已補正）。
> * **上層承接**：`AUGUR-ONT v1.0`（Layer 2）已於 2026-07-17 先行生效（AL-2026-007），本規格對其之承接自即生效；正文對 `AUGUR-ONT` 之引用之版本標注由 v0.1-draft 更新為 v1.0 屬 patch 級編輯（依 `§8.6`），不影響條款內容。
> * **實質充分性**之最終判斷仍屬 Steward 違憲審查程序（`AUGUR-MC v1.4 §8.2`），與已成就之形式充分性分屬二事；充任認定不排除嗣後之違憲審查。
> * 條款編號穩定性依 `AUGUR-MC v1.4 §8.6`、`AUGUR-WM v1.0 §WM.46`：永不重用、永不重排。
>
> 本【地位】節與 §0 全部約定為 [N] 規範內容，其效力與正文條款同（準用 `AUGUR-WM v1.0 §WM.53`）。

---

## 目錄 [I]

* §0 Document Status & Conventions（0.1–0.5）
* §1 Purpose, Scope & Layer Boundary（ID.1–ID.2）
* §2 承接與非管轄 Defers-In & Non-Encroachment（ID.3–ID.4）
* §3 Identifier 鑄造與結構 Minting & Structure（ID.10–ID.14）
* §4 判準採認 Criterion Adoption（ID.20–ID.24）
* §5 Identity Claim 一級介面 First-Class Interface（ID.30–ID.32）
* §6 Identity Lifecycle（ID.40–ID.44）
* §7 Provisional Identity 解析 Resolution（ID.50–ID.53）
* §8 身份屬性 as-of 時間繫結 Attribute Time-Binding（ID.60–ID.61）
* §9 與 Layer 4 分界 Boundary with Knowledge System（ID.70–ID.71）
* §10 合規聲明格式承接（ID.80–ID.81）
* Annex O [N] — OPEN-1 承接（AO.1–AO.4）
* Annex DO [N] — 下放下層之 DEFER 掛鉤（IDO.0–IDO.8）
* Annex L4 [N] — 與 Layer 4（Knowledge System）之分界表
* Annex TR [N] — WM.44 逐條對應矩陣（憲章＋WM＋ONT → 本規格；TR.0／TR.A–TR.D／TR.Z）
* Annex CS [N] — 本規格之 Constitutional Compliance Statement（CS.1–CS.4）
* 附：章節目錄總覽 [I]

---

## §0 Document Status & Conventions（文件地位與約定）[N]

### 0.1 名稱、層級與版本 [N]

* 名稱：Augur Identity Specification（下層引用簡稱 **AUGUR-ID**）
* 層級：Layer 3 — Identity System（`AUGUR-MC v1.4 §0.5` 對照表第 3 列）
* 版本：v1.0（前版：v0.1-draft）
* 上層規格（upper-specs）：`AUGUR-MC v1.4`（Layer 0）、`AUGUR-WM v1.0`（Layer 1）、`AUGUR-ONT v1.0`（Layer 2，草案）
* 生效要件：`AUGUR-MC v1.4 §0.5` 對照表登錄（已具欄位）＋ Steward 充任認定（**已成就**，見【地位】）＋ 依 `AUGUR-WM v1.0 §WM.39` 之 Compliance Statement（Annex CS），並登錄 Amendment Log（`AUGUR-MC v1.4 §8.1`）——**已全部成就**（Steward 裁決第 2026-004 號，2026-07-17，AL-2026-008）。**生效日：2026-07-17**。實質充分性之最終判斷仍屬 Steward `§8.2` 違憲審查程序，與已成就之形式充分性分屬二事。

### 0.2 規範用語約定 [N]

沿用 `AUGUR-MC v1.4 §0.2`：**必須**（MUST，絕對義務）／**不得**（MUST NOT，絕對禁止）／**應**（SHOULD，偏離須書面說明理由）／**得**（MAY，允許而不構成義務），全文一致，不重定義。

### 0.3 條文效力標注與編號穩定性 [N]

* 每章標題標注 **[N]（Normative，規範性）** 或 **[I]（Informative，資訊性）**。[N] 與 [I] 內容不一致時，依 `AUGUR-MC v1.4 §8.2` 以 Normative 為準。**章標題之標注為該章預設；凡子節另有標注者，以子節標注為該子節之效力準據**（如 §1[N] 下 §1.1[I] 為資訊性、§1.2[N] 為規範性）；此為標注層級之解讀規則，非上開內容衝突解消規則之適用範圍。
* **正文採十位制章段保留編號**：各章間之空號（如 ID.5–9、ID.15–19、ID.25–29、ID.45–49 等）為**保留區塊、非跳號**；保留號之啟用（如 ID.24、ID.44 於本版之啟用）亦適用永不重用、永不重排（`AUGUR-MC v1.4 §8.6`）。
* 正文條款編號採 **ID.{n}**；Annex 條款編號各自前綴：Annex O（OPEN 承接）採 **AO.{n}**、Annex DO（下放下層掛鉤）採 **IDO.{n}**、Annex TR（WM.44 逐條對應矩陣）採 **TR.{n}**（其資料列以所引上層條款編號為索引）、Annex CS（合規聲明）採 **CS.{n}**、Annex L4（與 Layer 4 分界）以其所引 ID／IDO 編號為索引，另立表首治理條款 **L4.{n}** 於必要時使用。
* 條款編號一經發布**永不重用、永不重排**；廢止條款保留編號並標注 **(repealed)**（`AUGUR-MC v1.4 §8.6`、`AUGUR-WM v1.0 §WM.46`）。

### 0.4 權威語言聲明 [N]

本規格以**繁體中文版為權威版本**；規範性術語於正文中一律使用英文原詞（Reality、Observation、Representation、Identity、Evidence、Knowledge、Confidence、Action、Agent；及本層機制術語 identifier、identity claim、mint、adopt、merge、split、retire、relist、redirect、tombstone、de-identify、lineage、provisional、resolution、as-of），與 `AUGUR-MC v1.4 §0.4`、`AUGUR-WM v1.0 §0.4`、`AUGUR-ONT v1.0 §0.4` 保持術語同一性；不另立中文譯名為規範對象。

### 0.5 引用格式與元規則 [N]

* 引用格式：`AUGUR-MC v1.4 §{條款}`／`AUGUR-WM v1.0 §{條款}`／`AUGUR-ONT v1.0 §{條款}`（Layer 2 現為 v0.1-draft，引用時註明其草案地位）。下層引用本規格採 `AUGUR-ID v{version} §{條款}`。
* 本規格每一 [N] 條款標注其**憲章／上層錨定**與**三態型態**：**refines**（細化上位條款）／**carries**（承接上位不變式並給予個體層機制位置）／**hooks**（DEFER 掛鉤，載明目標 Layer 與授權條款），與 `AUGUR-WM v1.0 §0.5`、`AUGUR-ONT v1.0 §0.5` 三態明文對映一致；複合模式以「＋」連接。每一 [N] 條款並標注**義務主體**與**可判定判準**，使其可機器稽核（承接 `AUGUR-WM v1.0 §WM.34`）。
* **不重定義元規則**：本規格**不得**重新定義 `AUGUR-MC v1.4 §2` 之術語（尤其 `§2.4` Identity＝identifier／identity claim 之區分），亦**不得**重定義 `AUGUR-WM v1.0`／`AUGUR-ONT v1.0` 之既有構件；本規格僅得就其明示下放者作**機制化**（`AUGUR-MC v1.4 §2` 元規則、`AUGUR-WM v1.0 §WM.2`、`AUGUR-ONT v1.0 §ONT.2`）。
* **概念層獨立性**（`AUGUR-MC v1.4 §0.6(b)`）：本規格屬概念層（Layer 3），**不得**引用 Layer 5–7 執行層構件（資料庫、Agent Runtime、API、儲存引擎、序列化格式）作為任何定義之依據。本規格所稱「機制」為**概念機制**（不變式、狀態、關係、事件語義），其執行層落實一律下放（Annex DO）。

---

## §1 Purpose, Scope & Layer Boundary（目的、範圍與分層界限）[N]

### 1.1 Layer 3 定位 [I]

`AUGUR-WM v1.0` 宣告**世界有何物**（存在層，existence layer）；`AUGUR-ONT v1.0` 宣告**其類屬與同一性判準之內容**（型別層，type layer，制定 formulate）。**AUGUR-ID 負責「個體的永久參照與其一生的機器機制」**（個體層，instance/identifier layer）——即 identifier 之**鑄造（mint）**、同一性判準之**採認（adopt）使生效於 resolution**、identity **lifecycle**（merge／split／retire／relist／轉指 redirect、tombstone、去識別化 de-identify、lineage）、**identity claim 一級介面**、**provisional identity 解析**、**身份屬性 as-of 時間繫結**。本規格承接 `AUGUR-ONT v1.0` Annex L3「Layer 3 專屬」欄與 `AUGUR-WM v1.0` Annex D 目標含 Layer 3 之掛鉤。

### 1.2 條款 [N]

> **ID.1（三層不僭越）[N｜carries｜`AUGUR-ONT v1.0` Annex L3、`§ONT.3`、`§ONT.7`；`AUGUR-WM v1.0 §WM.3`、`§WM.23`]**
> 存在層宣告「有何物」、型別層產出「類型與判準的定義文本」、本層產出「個體的永久參照與其一生的機器機制」。本規格**不得**新宣告世界實體之存在（屬 Layer 1）、**不得**改寫或新制同一性判準之**內容**（屬 Layer 2 制定）；本層僅**採認**判準使其生效於 resolution、**鑄造** identifier、**運轉** lifecycle。
> **義務主體**：本規格自身、本規格後續修訂者。**可判定判準**：本規格任一條款若對某世界概念作存在宣告、或陳述某 Type 之判準**內容文句**（而非引用 Layer 2 既制定之判準），即為上侵，違反本條。

> **ID.2（下界封印）[N｜carries｜`AUGUR-MC v1.4 §P4.E1`、`§P4.E8`、`§P4.E2`、`§P4.E7`]**
> 下列事項屬 Layer 4，本規格**僅得**設下放掛鉤（Annex DO），**不得**代行定義：(a) **Confidence 語義**（單一形式化定義、可比較性、傳播規則，`AUGUR-MC v1.4 §P4.E8`）；(b) **Knowledge 五元組之欄位設計**（Source／Timestamp／Identity／Evidence／Confidence 之結構落地，`§P4.E1`）；(c) **as-of 重建引擎與能力等級**（`§P4.E2`）；(d) **來源信任分級表**（`§P4.E7`）。本規格得**引用**上開概念槽並規定其於 identity 構件中之**存在位置**，但其語義填充下放 Layer 4。
> **義務主體**：本規格自身。**可判定判準**：本規格任一條款若對 (a)–(d) 作成可被 Layer 4 直接消費而無須另為定義之實質定義，違反本條（下侵）。

---

## §2 承接與非管轄（Defers-In & Non-Encroachment）[N]

### 2.1 承接上層掛鉤（defers-in）[N]

> **ID.3（承接盤點）[N｜carries｜`AUGUR-WM v1.0` Annex D D0；`AUGUR-ONT v1.0` Annex DO DO.0]**
> 本規格於 Annex CS 之 `defers-in` 欄承接下列上層掛鉤，逐一於正文對應：
>
> | 承接來源 | 事項 | 本規格落點 |
> |---|---|---|
> | `AUGUR-WM v1.0 §D5`（`§WM.20`） | identifier 之鑄造、結構、命名空間設計 | §3（ID.10–ID.14） |
> | `AUGUR-WM v1.0 §D2`（`§WM.21(e)`）採認側 | 同一性判準之**採認**使生效於 resolution | §4（ID.20–ID.23） |
> | `AUGUR-WM v1.0 §D3`（`§WM.21(c)`、`§WM.22`） | identity claim 一級表介面、轉指機制、tombstone、去識別化 | §5、§6 |
> | `AUGUR-WM v1.0 §D4`（`§WM.21(d)`、`§WM.35`） | provisional 解析時限與未解析存量稽核指標（含 unmapped 準用） | §7（ID.50–ID.53） |
> | `AUGUR-WM v1.0 §D6`（`§A.54`） | 本域證券代碼身份假設之判準採認（改名／代碼重用／借殼） | Annex O（AO.1–AO.4） |
> | `AUGUR-WM v1.0 §D17`（`§WM.38`；目標 L3/L6）**L3 slice** | 自然人身份之 identity 側去識別化／法規強制抹除機制與時變屬性 as-of 繫結 | ID.42、§8（ID.60）；**L6 slice**（法規對應表本體與授權）DEFER Layer 6（IDO.7） |
> | `AUGUR-ONT v1.0 §DO.1` | 判準採認、resolution 演算／時限指標 | §4、§7 |
> | `AUGUR-ONT v1.0 §DO.2` | identity claim 一級表介面、identifier 鑄造／結構／命名空間 | §3、§5 |
> | `AUGUR-ONT v1.0 §DO.3` | lifecycle 事件表、merge／split／retire／relist、tombstone、去識別化、lineage | §6 |
> | `AUGUR-ONT v1.0 §DO.4` | 標記存續／解析、provisional 解析、身份屬性 as-of 版本化 | §7、§8 |
>
> **義務主體**：本規格自身。**可判定判準**：上表每列於正文有對應 ID 條款、且於 Annex CS `defers-in` 表雙向可解析者為合規；任一列無對應正文條款者，承接不完整。

### 2.2 非管轄聲明 [N]

> **ID.4（不擴張管轄）[N｜carries｜`AUGUR-MC v1.4 §0.6(a)`、`§0.5`；`AUGUR-WM v1.0 §WM.3`；`AUGUR-ONT v1.0 §ONT.3`]**
> 本規格為 Layer 3 唯一所轄規格，不自行擴張管轄；凡 `AUGUR-MC v1.4` 明定定義權屬 Layer 1／Layer 2／Layer 4–7 之事項，本規格**不得**代行定義。
> **義務主體**：本規格自身。**可判定判準**：本規格任一條款之定義對象逾越 `AUGUR-MC v1.4 §0.5` 所定 Layer 3 職掌者，違反本條。

---

## §3 Identifier 鑄造與結構（Minting & Structure）[N]

> 本章行使 `AUGUR-WM v1.0 §D5`（承 `§WM.20`）與 `AUGUR-ONT v1.0 §DO.2` 下放之 identifier 設計權。承接審計 **AUD-04**（無系統鑄造之 Identity 層）。

### 3.1 §WM.20 授權範圍之明示 [N]

> **ID.10（授權範圍與語義義務保留）[N｜refines｜`AUGUR-WM v1.0 §WM.20`；`AUGUR-MC v1.4 §P1.E2`、`§P3.E2`]**
> `AUGUR-WM v1.0 §WM.20` **不課** identifier 任何編碼或命名空間結構義務，並將 identifier 之**鑄造、結構與命名空間**明文授予 Layer 3；Layer 1 僅保留一項**語義義務**：identifier **必須可跨部署邊界解析與對齊**（`AUGUR-MC v1.4 §P1.E2`）。本規格據此行使設計權，惟其行使**必須**滿足並**不得**削弱該語義義務。凡本規格所定命名空間或結構，**必須**使「同一世界個體於任何部署之 identifier 可被解析為同一」為可判定；**不得**以任何結構設計使跨部署對齊變為不可判定。
> **義務主體**：本規格自身、Layer 4–7 之實作構件。**可判定判準**：本規格所定之任一命名空間，其 identifier 之跨部署對齊規則已明文且可機械判定者為合規；未明文或使對齊不可判定者違反本條。

### 3.2 鑄造義務（mint-on-admission，落實 AUD-04）[N]

> **ID.11（系統鑄造義務）[N｜carries｜`AUGUR-MC v1.4 §P3.E2`、`§P3.E1`；`AUGUR-WM v1.0 §WM.19`、`§WM.22`；`AUGUR-ONT v1.0 §ONT.22`]**
> 凡 `AUGUR-WM v1.0` 存在宣告、`AUGUR-ONT v1.0` Annex T 型別化之世界個體，於**首次意圖進入 Reasoning／Planning 或升級為 Knowledge 之前**，系統**必須**為其鑄造一枚**系統 identifier**（`AUGUR-MC v1.4 §2.4`：系統鑄造之永久參照，本身為系統內具 Identity 地位之一級物件）。外部來源識別碼（供應商證券代碼、series_id、ISIN、統一編號）為 Identity 之**指涉資訊**，**不得**逕充系統 identifier（承接 `AUGUR-ONT v1.0 §ONT.22`、`AUGUR-WM v1.0 §WM.20`；**AUD-04**）。
> **「未鑄造故無附著對象」抗辯之排除**（承接審計驗證裁註，AUD-05）：identifier 之鑄造義務為前提義務，**不得**以「lifecycle／lineage 尚無 identifier 可附著」為由免除；系統**必須**先鑄造，方使 lifecycle 有附著對象。
> **義務主體**：Layer 4–7 之表徵與攝取構件、本規格（表達力保證）。**可判定判準**：任一升級為 Knowledge 之世界個體參照可解析至恰一系統 identifier 者為合規；以外部識別碼裸字串直充身份者違反本條。

### 3.3 命名空間結構（概念層）[N]

> **ID.12（型別化命名空間隔離）[N｜refines｜`AUGUR-ONT v1.0 §ONT.31`、`§ONT.2`；`AUGUR-WM v1.0 §WM.20`]**
> 系統 identifier **必須**繫結恰一 Type 之個體命名空間（`AUGUR-ONT v1.0 §ONT.31` 之概念層隔離）；不同頂層範疇與不同 Type 之個體命名空間**必須**互斥。**禁止型態**（承接 **AUD-04**）：(i) 將產業分類名（type 節點）或指數代號混入 Security 個股命名空間；(ii) 將 EconomicIndicator／MacroDimensionQuantity（series_id 空間）與 Security（stock_id 空間）視為同一命名空間。命名空間之**指稱結構**（例如以〔範疇︰Type︰個體序〕之概念三元組標記）由本規格定其**概念形式**；其**物理序列化與儲存編碼** DEFER Layer 7（`AUGUR-MC v1.4 §0.6(b)`，Annex DO IDO.5）。
> **義務主體**：本規格自身、Layer 4–7 消費者。**可判定判準**：任一系統 identifier 可解析至恰一 Type 之個體命名空間者為合規；同一 identifier 解析至二個以上 Type、或 type 節點被當 Instance 鑄造者違反本條。

### 3.4 identifier 永不刪除 [N]

> **ID.13（永久性不變式）[N｜carries｜`AUGUR-MC v1.4 §P3.E2`；`AUGUR-WM v1.0 §WM.22`]**
> identifier 一經鑄造**永不刪除**；其後續指向變更（轉指 redirect）**必須**全程可追溯（§6）。identifier 存續**跨越任何 Ontology／Representation 變更**（`AUGUR-WM v1.0 §WM.22`）。
> **義務主體**：本規格、Layer 4–7 構件。**可判定判準**：存在任一使 identifier 記錄消滅之操作路徑者違反本條（法規抹除之留痕例外依 ID.42）。

> **ID.14（identifier 之 Identity 地位）[N｜carries｜`AUGUR-MC v1.4 §2.4`]**
> identifier 本身為系統內具 Identity 地位之一級物件；關於 identifier 之斷言（如轉指、退役）本身為受 P4 約束之 Knowledge（§6）。
> **義務主體**：本規格。**可判定判準**：關於 identifier 之 lifecycle 事件是否具備 Evidence 引用（依 ID.40）可機械檢查者為合規。

---

## §4 判準採認（Criterion Adoption）[N]

> 本章接續 `AUGUR-WM v1.0 §WM.21(e)` 效力封印與 `AUGUR-ONT v1.0 §ONT.21` 之封印，行使 `§D2`（採認側）／`§DO.1` 下放之**採認**權。

### 4.1 採認之定義性效果 [N]

> **ID.20（採認行為）[N｜carries＋refines｜`AUGUR-MC v1.4 §P3.E3`；`AUGUR-WM v1.0 §WM.21(e)`、`§D2`；`AUGUR-ONT v1.0 §ONT.20`、`§ONT.21`、`§DO.1`]**
> Layer 2 已為每一 Type **制定**（formulate）其 Identity Criterion（`AUGUR-ONT v1.0 §ONT.20`），惟其**用於 resolution 之操作效力**須經本層**採認**（adopt）方生效（`§ONT.21`）。採認為一**具名、附 Evidence、可追溯之治理行為**，其效果為：使被採認之判準對指定 Type 生效於 identity resolution，自採認生效時起，涉該 Type 之 Identity 引用**得**被判定為已解析。採認**不得**改寫判準內容（改寫屬 Layer 2 制定，違者上侵，違 ID.1）。
> **義務主體**：本規格自身、採認之作成者。**可判定判準**：每一採認紀錄具備〔目標 Type、被採認判準之 Layer 2 條款引用、生效時點、Evidence 引用、作成者〕五要素者為合規；缺任一要素之採認不生效力。

### 4.2 採認前之保守解釋 [N]

> **ID.21（未採認即未解析）[N｜carries｜`AUGUR-WM v1.0 §WM.21(d)(e)`、`§WM.33`；`AUGUR-ONT v1.0 §ONT.21`；`AUGUR-MC v1.4 §P3.E1`]**
> 於某 Type 之判準經本層採認前，涉該 Type 之 Identity 引用一律採保守解釋，**視為未解析**（provisional）；未解析之 Observation **不得**升級為 Knowledge（`AUGUR-MC v1.4 §P3.E1`）。
> **義務主體**：Layer 3–7 消費者。**可判定判準**：存在採認紀錄前，將涉該 Type 之引用視為已解析而升級為 Knowledge 者違反本條。

### 4.3 採認之修訂與撤回 [N]

> **ID.22（採認之可謬性）[N｜carries｜`AUGUR-MC v1.4 §P4.E3`、`§P4.E4`、`§P2.E5`]**
> 採認本身為可被新 Evidence 推翻之 Knowledge（`§P4.E4`）；採認之撤回或修訂**不得刪除**原採認紀錄，僅得標記 superseded／retracted（`§P4.E3`），全歷史保留。採認撤回時，受其影響之既有 resolution 結果**必須**依 `AUGUR-MC v1.4 §P2.E5` fail-safe 重新評估（受影響範圍界定 DEFER Layer 4–6，`AUGUR-WM v1.0 §D15`）。
> **義務主體**：本規格、採認之修訂者。**可判定判準**：採認鏈之任一版本可經 transaction-time 重建者為合規；靜默刪除原採認紀錄者違反本條。

> **ID.23（resolution 演算與時限指標之下放）[N｜hooks｜`AUGUR-WM v1.0 §D4`；`AUGUR-ONT v1.0 §DO.1`；目標本層 §7 ＋ Layer 4 實作]**
> 判準採認後之 **resolution 演算之具體實作**（相似度、比對、批次流程）與**未解析存量之量測落地** DEFER Layer 4（Annex DO IDO.4）；本規格於 §7 定其**概念指標與義務**，不定實作。
> **義務主體**：本規格、Layer 4。**可判定判準**：§7 指標存在且可機械盤點者為合規。

### 4.4 世界關係之 Identity Resolution 承接 [N]

> **ID.24（世界關係之身份解析）[N｜carries｜`AUGUR-ONT v1.0 §ONT.40`、T.50、T.51；`AUGUR-WM v1.0 §WM.21(e)`]**
> 世界關係（`AUGUR-ONT v1.0 §ONT.40`：IssuanceRelation T.50、UnderlyingRelation T.51 等，其判準為〔關係型別 × 端點 Identity 有序組 × valid time〕）之個體為 **Instance**。其 Identity **依端點 Identity 已解析 ＋ 關係型別 ＋ valid time 派生**；`§ONT.40` 所定端點 Identity 之效力封印（同 `§ONT.21`），於各端點 Type 之判準經本層採認（ID.20）時解除，關係之判準採認**準用** ID.20。關係實例當升級為 Knowledge 時依 ID.11 鑄造系統 identifier、依 ID.12 繫結其**關係型別之個體命名空間**（與端點命名空間互斥）；其權威指稱得以端點有序組解析，**不得**以裸字串推定關係同一。
> **義務主體**：本規格、Layer 4–7 消費者。**可判定判準**：任一世界關係實例可解析至〔關係型別 × 端點 Identity 有序組 × valid time〕且端點 Identity 均已解析者為合規；端點未解析而逕認關係同一、或以裸字串 join 推定關係者違反本條。

---

## §5 Identity Claim 一級介面（First-Class Interface）[N]

> 本章行使 `AUGUR-WM v1.0 §WM.21(c)`、`§D3` 與 `AUGUR-ONT v1.0 §ONT.22`、`§DO.2` 下放之 identity claim 表介面權。承接審計 **AUD-06**（跨來源零繫結）。

### 5.1 identity claim 之結構 [N]

> **ID.30（一級介面四要件）[N｜carries｜`AUGUR-MC v1.4 §2.4`；`AUGUR-WM v1.0 §WM.21(c)`；`AUGUR-ONT v1.0 §ONT.22`]**
> identity claim（`AUGUR-MC v1.4 §2.4`：「兩個 identifier 指涉同一實體」之斷言，繫結於其所涉 identifier，本身為**受 P4 約束之 Knowledge**）為系統內一級物件。其結構**必須**含下列**身份側四要件**：
> * **(a) identifier 對**：所斷言同一之**二系統 identifier**（`AUGUR-MC v1.4 §2.4`「兩個 identifier」、`AUGUR-WM v1.0 §WM.21(c)`「identifier 對」）。外部識別碼為指涉資訊、**非** identifier（`§ONT.22`、ID.11），**不得逕充 claim 端點**；外部識別碼所指涉之世界個體須先依 ID.11 鑄造系統 identifier，以**該系統 identifier**為 claim 端點，外部識別碼本身僅以**指涉資訊／provisional alias** 地位供 resolution 使用（AO.3），不逕為端點；
> * **(b) 判準引用**：本斷言所據之 Identity Criterion（Layer 2 制定、經本層採認之條款引用，`§ONT.20`／ID.20）；
> * **(c) Evidence**：支持本斷言之 Evidence 引用（`AUGUR-MC v1.4 §P4.E6` 一級物件，遞迴可溯源）；
> * **(d) Confidence 槽位**：本斷言為真之程度之槽位。**Confidence 之語義（形式化定義、可比較性、傳播）本身 DEFER Layer 4**（`§P4.E8`，Annex DO IDO.1）；本層僅要求槽位存在並可被 Layer 4 填充。
> **禁止**（承接 **AUD-04／AUD-06**）：**不得**以欄位字面相等（裸字串 join、消費端 regex）推定跨體系同一（`AUGUR-WM v1.0 §A.33`、`§WM.21(c)`）。
> **義務主體**：本規格自身、Layer 4–7 消費者。**可判定判準**：任一跨體系同一性斷言具備 (a)–(d) 四要件、且 (d) 之語義以 Layer 4 承接標記者為合規；以字面相等替代 claim 者違反本條。

### 5.2 claim 之 Knowledge 地位 [N]

> **ID.31（claim 為 Knowledge，欄位設計下放）[N｜carries｜`AUGUR-MC v1.4 §2.4`、`§P4.E1`、`§P4.E5`]**
> identity claim 為 Knowledge，除身份側四要件（ID.30）外，其**完整 Knowledge 五元組欄位設計**（Source／Timestamp／Identity／Evidence／Confidence 之結構落地）DEFER Layer 4（`§P4.E1`，Annex DO IDO.2）。互相衝突之 claim（如二來源對同一 identifier 對作出相反同一性斷言）**必須**共存並顯式標記，**不得** last-write-wins（`§P4.E5`）。
> **義務主體**：本規格（表達力保證）、Layer 4（欄位設計）。**可判定判準**：世界模型能容納二相反 claim 並存者為合規；靜默消滅其一者違反本條。

### 5.3 唯一權威表徵之落點 [N]

> **ID.32（唯一權威表徵之結構前提）[N｜carries＋hooks｜`AUGUR-MC v1.4 §P1.E2`；`AUGUR-WM v1.0 §WM.10`、`§WM.14`、`§WM.15`、`§WM.37`；hooks 目標 Layer 4（`§WM.37`），Annex DO IDO.8]**
> 當二來源之 identifier 經 claim 斷言指涉同一世界實體／世界量時，本層之義務**限於提供 claim 繫結所需之結構前提**：使該 identifier 對可解析至**恰一權威表徵之錨點**（`AUGUR-WM v1.0 §WM.14` 權威地位唯一，不指儲存份數），並以 claim 承載「世界事實→來源 Observation」一對多映射與衝突保存（落實 **AUD-06**）。**唯一權威 Representation 之實際指定與落點屬 Representation 層（Layer 4），本層不代行**：其指定 carries `§WM.14`、DEFER Layer 4（`§WM.37` 唯一權威表徵落點；IDO.8），本層僅保證「可被指定」之結構條件存在，不自為 Representation 權威指定（此非 Layer 3 identifier 職掌，避免下侵 Annex L4）。世界量同一性以 Domain Profile／Registry 明文宣告為準（`§WM.15`：無宣告即非同一）。
> **義務主體**：本規格（結構前提）、Layer 4（權威表徵之實際指定）。**可判定判準**：經 claim 繫結之 identifier 對可解析至恰一權威表徵之錨點者為合規；本層對權威 Representation 作可被 Layer 4 直接消費之實際指定（而非僅結構前提）者，反為下侵、違 ID.2／ID.70。

---

## §6 Identity Lifecycle（生命週期機制）[N]

> 本章行使 `AUGUR-WM v1.0 §WM.22`、`§D3` 與 `AUGUR-ONT v1.0 §DO.3` 下放之 lifecycle 機制權。落實 `AUGUR-MC v1.4 §P3.E2`、承接審計 **AUD-05**（lifecycle 缺席致 stock_id 重用縫合）。

### 6.1 lifecycle 事件為 Knowledge [N]

> **ID.40（生命週期事件之 Evidence 義務）[N｜carries｜`AUGUR-MC v1.4 §P3.E2`、`§P4.E2`、`§P4.E3`；`AUGUR-WM v1.0 §WM.22`；`AUGUR-ONT v1.0 §DO.3`]**
> Identity 之 **merge／split／retire／relist 與更正**，本身為**必須引用 Evidence 之 Knowledge**（`AUGUR-MC v1.4 §P3.E2`）。系統**必須**維持一**概念 lifecycle 事件序**，每一事件載：〔事件型別 ∈ {mint, merge, split, retire, relist, redirect（轉指）, correct, tombstone, de-identify, expire（到期失效）, settle（結算消滅）, convert（轉換）, redeem（贖回）}、所涉 identifier、生效時點（valid time）、系統可知時點（transaction time，`§P4.E2`）、Evidence 引用、作成者〕。**本枚舉為開放集**：Layer 2 已宣告具生命週期屬性之 Type（如 DerivativeContract T.3、ConvertibleBond T.4、Warrant T.5，見 ID.44）之終結事件型別得依其型別語義擴充；未列名之終結型別於 DynamicEntity 語境準用其對應終結事件。事件**只失效不刪除**（`§P4.E3`）。
> 事件序之**欄位／索引物理實作** DEFER Layer 4／Layer 7（Annex DO IDO.3；`AUGUR-MC v1.4 §0.6(b)`）。
> **義務主體**：本規格（事件語義）、Layer 4（實作）。**可判定判準**：任一 merge／split／retire／relist／redirect 事件缺 Evidence 引用者違反本條。

### 6.2 轉指與 lineage 不變式 [N]

> **ID.41（轉指全程可追溯不變式）[N｜carries｜`AUGUR-MC v1.4 §P3.E2`；`AUGUR-WM v1.0 §WM.22`]**
> identifier 之後續指向變更（合併後之轉指 redirect）**必須全程可追溯**（不變式）；**identity lineage 全程保留**。給定任一 identifier 與任一 as-of 時點，「該時點此 identifier 指向哪一存續個體」**必須**可重建。merge 產生一指向合併目標之 redirect（來源 identifier 依 ID.13 存續、不刪除）；split 於分裂邊界後，同一來源指涉**必須**解析為不同存續個體（見 ID.43）。
> **義務主體**：本規格、Layer 4。**可判定判準**：存在任一使 lineage 斷鏈（無法重建某 as-of 指向）之操作者違反本條。

### 6.3 tombstone 與去識別化 [N]

> **ID.42（法規強制抹除之留痕與去識別化）[N｜carries｜`AUGUR-MC v1.4 §P3.E2`（法規抹除準用 `§P4.E3`）；`AUGUR-WM v1.0 §WM.38`、`§D17`（L3 slice）；`AUGUR-ONT v1.0` T.23]**
> 法規強制抹除**準用** `AUGUR-MC v1.4 §P4.E3` 例外：**得**移除 identifier 所繫結之可識別內容並**去識別化**，惟：(a) identifier 本身以**留痕形式（tombstone）存續**；(b) 抹除事件具**完整 provenance**（作成者、法源依據引用、生效時點）；(c) **identity lineage 保留**。tombstone **不得**用以規避 ID.13 永不刪除（tombstone 為存續之特例，非刪除）。
> **D17 之 Layer 3 slice 承接**：涉自然人 Type（`AUGUR-ONT v1.0` T.23 HumanDecisionMaker 等）之身份 identity 側去識別化／可識別內容抹除機制，為 `AUGUR-WM v1.0 §D17`（`§WM.38` 有界表徵）目標 L3 之機制載體，由本條承接（時變屬性之 as-of 繫結另見 §8 ID.60）。**具體法規對應表本體與其授權（L6 slice）DEFER Layer 6**（Annex DO IDO.7；`AUGUR-MC v1.4 §P1.E3`、`§WM.38`、`§D17`）；本條不代定法規對應內容。
> **義務主體**：本規格、Layer 4–7 執行構件。**可判定判準**：去識別化後仍存在 identifier tombstone、抹除事件具 provenance、lineage 可重建者為合規；三者缺一者違反本條。

### 6.4 代碼重用／退市／改名（落實 AUD-05）[N]

> **ID.43（存續邊界截斷）[N｜carries｜`AUGUR-WM v1.0 §WM.22`、`§A.25`；`AUGUR-ONT v1.0` T.1、T.34]**
> 下市（`AUGUR-ONT v1.0` T.34 Delisting，parent Event）為 Security lifecycle **retire** 事件之 Evidence 來源（`§A.25`：下市改變來源可見性、不改變歷史真實性）。外部代碼被回收重用時（同一外部代碼於 retire 事件後再現於名冊），系統**必須**將其解析為**不同存續個體**（split／新鑄造 identifier），使前一個體之歷史**不得**縫合入後一個體之表徵。改名／合併同樣以 lifecycle 事件表徵，**不得**靜默覆寫。
> **代碼重用偵測為可機械化紅旗**：同一外部代碼於 retire 事件後再現於名冊者，**必須**登錄為待解析事件（provisional，§7），不得逕行縫合。
> **義務主體**：本規格、Layer 4 特徵／標籤構造構件。**可判定判準**：跨 retire/relist 邊界之同一外部代碼被解析為同一存續個體、致歷史縫合者違反本條（其上位判準依 `AUGUR-ONT v1.0` T.1 制定，本層引用而不複述其判準文句）。

### 6.5 DynamicEntity 非下市之終結 lifecycle（承接 DO.3 之 T.3／T.4／T.5）[N]

> **ID.44（具生命週期實體之終結表徵）[N｜carries｜`AUGUR-MC v1.4 §P3.E2`；`AUGUR-WM v1.0 §WM.22`；`AUGUR-ONT v1.0 §DO.3`、T.3、T.4、T.5]**
> Layer 2 已宣告具生命週期屬性之 DynamicEntity（`AUGUR-ONT v1.0` T.3 DerivativeContract 之上市→交易→**結算消滅**、T.5 Warrant 之**到期失效**、T.4 ConvertibleBond 之**轉換／贖回**）之終結，其型別語義**非**「下市 retire」；本層承接 `§DO.3` 就此類終結之機制：終結**必須**以 lifecycle 事件（settle／expire／convert／redeem，ID.40）表徵，其 identifier 依 ID.13 **永不刪除**、identity lineage 全程保留，**終結後不得靜默消滅其歷史**。ConvertibleBond 轉換至標的股（UnderlyingRelation T.51）**必須**以事件＋lineage 表徵，**不得**以覆寫承載。
> **義務主體**：本規格（事件語義）、Layer 4（實作）。**可判定判準**：任一 DynamicEntity 之結算消滅／到期失效／轉換／贖回缺對應 lifecycle 事件與 Evidence 引用（ID.40）、或終結致其 identifier 記錄消滅／lineage 斷鏈者違反本條。

---

## §7 Provisional Identity 解析（Resolution）[N]

> 本章行使 `AUGUR-WM v1.0 §WM.21(d)`、`§WM.35`、`§D4` 與 `AUGUR-ONT v1.0 §DO.4`（provisional 側）下放之解析義務與稽核指標權。落實 `AUGUR-MC v1.4 §P3.E1`。

### 7.1 解析義務 [N]

> **ID.50（解析義務與升級禁止）[N｜carries｜`AUGUR-MC v1.4 §P3.E1`；`AUGUR-WM v1.0 §WM.21(d)`]**
> 未解析之 Observation **得**進入系統、**不得**升級為 Knowledge；系統**負解析義務**（`AUGUR-MC v1.4 §P3.E1`）。凡意圖進入 Reasoning／Planning 之結構化物件（無論 Goal／Constraint／Capability／Plan 於 Layer 5–6 如何定義）均落入**已解析 Identity 引用義務**（`§WM.21(d)` 兜底）。
> **「已解析」之本層自足定義**：於本層，某 Identity 引用為**已解析** iff〔涉該 Type 之判準採認已生效（ID.20）**∧** 該引用之 provisional 狀態旗標已依 ID.51(a) 清除〕；此為「解析成功」於 Layer 3 之機器可判定代理。resolution 演算本身（相似度／比對）仍 DEFER Layer 4（ID.23、IDO.4），其成敗於個體層落地由 Layer 4 承接。
> **義務主體**：Layer 3–7 消費者。**可判定判準**：任一升級為 Knowledge 之元素其 Identity 為已解析（採認已生效〔ID.20〕∧ provisional 狀態已清除〔ID.51(a)〕）者為合規；provisional 元素被升級者違反本條。

### 7.2 可稽核指標 [N]

> **ID.51（未解析存量之可稽核指標）[N｜hooks｜`AUGUR-WM v1.0 §D4`；`AUGUR-ONT v1.0 §DO.1`；目標本層定義＋Layer 4 量測]**
> 本規格定下列**概念指標**（`AUGUR-WM v1.0 §D4` 要求之「解析時限或未解析存量之可稽核指標」，Layer 3 必須定）：
> * **(a) 未解析存量（unresolved backlog）**：任一 as-of 時點，處於 provisional 狀態之 Observation 指涉集合之基數，**必須**可盤點；
> * **(b) 解析時效（resolution latency）**：自 provisional 進入至解析（成功或登錄為顯式待決）之時間分佈，**必須**可量測；
> * **(c) 顯式待決同一性存量**：疑似同一而尚無同一性宣告者（`AUGUR-WM v1.0 §WM.15` 顯式待決同一性存量之法源；結構位置錨 `§WM.21`）與 unmapped 顯式存量（`§WM.35`）**必須**登錄，**待決期間依保守解釋不得合併消費**。
> 指標之**量測落地與門檻值** DEFER Layer 4（Annex DO IDO.4）；本規格僅定指標之**存在與可盤點性**，不內嵌具體門檻。
> **義務主體**：本規格（指標定義）、Layer 4（量測）。**可判定判準**：(a)–(c) 三指標於世界模型可機械盤點者為合規；任一不可盤點者違反本條。

### 7.3 unmapped 準用與標記存續 [N]

> **ID.52（unmapped 與待決同構）[N｜carries｜`AUGUR-WM v1.0 §WM.35`、`§WM.15`]**
> 暫無對應世界概念之通道資料（`§WM.35` unmapped 顯式存量）與疑似同一之顯式待決同一性存量（`§WM.15`）與本章 provisional 同構，一律列入解析義務；unmapped 或未登錄映射之通道資料**僅具 Observation 地位**，**不得**被消費為 Representation 或 Knowledge 之依據。
> **義務主體**：Layer 3–7 消費者。**可判定判準**：unmapped 資料被升格消費者違反本條。

> **ID.53（instance/type 標記之存續與解析）[N｜carries｜`AUGUR-ONT v1.0 §ONT.30`、`§DO.4`；`AUGUR-WM v1.0 §WM.21(b)`、`§WM.33`]**
> Layer 2 定義之 instance／type 繫結標記語義（`§ONT.30`），其**存續與解析落實**由本層承接：任一 Knowledge 元素之繫結對象**必須**攜帶可解析之 instance 或 type 標記，且該標記隨轉引存續。
> **義務主體**：本規格、Layer 3–7 消費者。**可判定判準**：繫結對象未攜帶或不可解析 instance／type 標記者違反本條。

---

## §8 身份屬性 as-of 時間繫結（Attribute Time-Binding）[N]

> 本章承接 `AUGUR-ONT v1.0 §DO.4`（身份屬性 as-of 版本化）。落實審計 **AUD-07**（身份屬性無時間繫結）。**法源收斂**：本章之核心錨定為 `AUGUR-MC v1.4 §P4.E2`（雙時間性）於身份屬性之界面（承審計驗證裁註：AUD-07 法源收斂為 P4.E2 單軸，P3.E3 為誤引）；本章不引 `§P3.E3` 為義務錨。

### 8.1 身份屬性為時變、須 as-of 繫結 [N]

> **ID.60（身份屬性 as-of 繫結義務）[N｜carries｜`AUGUR-MC v1.4 §P4.E2`；`AUGUR-ONT v1.0 §DO.4`、T.24、T.42]**
> Identity 之時變屬性（如產業分類、名稱、市場類別、股權分級）**必須**繫結 valid time 與 transaction time（`§P4.E2`）；其消費**必須 as-of**——以「今日的」屬性判定歷史狀態（如以今日 industry_category 判定歷史宇宙准入）為**禁止型態**（承接 **AUD-07**；`AUGUR-ONT v1.0` T.24 明示之禁止型態）。任一過去時刻「系統當時認為此 Identity 之屬性為何」**必須**可重建。
> **義務主體**：本規格（繫結義務）、Layer 4 消費構件。**可判定判準**：對身份時變屬性之查詢含 as-of 時間界限、且該屬性具 valid/transaction time 版本者為合規；屬性以原地覆蓋（last-write-wins、無版本）承載、或消費無日期條件者違反本條。

### 8.2 與 Layer 4 as-of 引擎之界限 [N]

> **ID.61（繫結存在 vs 重建引擎之分界）[N｜hooks｜`AUGUR-MC v1.4 §P4.E2`；`AUGUR-WM v1.0 §WM.30`、`§D8`；目標 Layer 4]**
> 本規格課予「身份屬性**必須**具 as-of 繫結（版本存在）」之義務（ID.60）；而 **as-of 重建之機制與能力等級**（重建引擎、雙時間查詢之操作化）DEFER Layer 4（`§P4.E2`，Annex DO IDO.6；`AUGUR-WM v1.0 §WM.30`、`§D8` HOOK-01 上呈素材）。二者分界：本層保證「版本可繫結、歷史可重建之資訊存在」；Layer 4 提供「重建之引擎與能力等級」。
> **義務主體**：本規格、Layer 4。**可判定判準**：本規格未對重建引擎作實質定義、且 as-of 繫結義務可被 Layer 4 引擎消費者為合規。

---

## §9 與 Layer 4 分界（Boundary with Knowledge System）[N]

> 集中重申 §1.2（ID.2）之下界封印，供 Annex CS 對表。

> **ID.70（Layer 4 專屬事項清單）[N｜carries｜`AUGUR-MC v1.4 §P4.E1`、`§P4.E2`、`§P4.E7`、`§P4.E8`]**
> 下列一律屬 Layer 4，本規格僅設槽位／掛鉤：
> * **Confidence 語義**（單一形式化定義、全系統可比較、傳播、消費門檻，`§P4.E8`）——identity claim（ID.30(d)）之 Confidence 槽位之語義填充；
> * **Knowledge 五元組欄位設計**（`§P4.E1`）——identity claim（ID.31）與 lifecycle 事件（ID.40）之完整 Knowledge 欄位；
> * **as-of 重建引擎與能力等級**（`§P4.E2`）——ID.61；
> * **來源信任分級表**（`§P4.E7`）。
> **義務主體**：本規格自身。**可判定判準**：本規格對上開任一事項作可被 Layer 4 直接消費之實質定義者違反本條（下侵）。

> **ID.71（分界表）[N｜carries｜`AUGUR-ONT v1.0` Annex L3（同構）]**
> 本層與 Layer 4 之逐項分界見 **Annex L4**（與 `AUGUR-ONT v1.0` Annex L3 同構之精確分界表）。
> **義務主體**：本規格。**可判定判準**：Annex L4「本層得為」欄與「Layer 4 專屬」欄無交集。

---

## §10 Constitutional Compliance Statement Format 承接與存續 [N]

> **ID.80（格式承接）[N｜carries｜`AUGUR-WM v1.0 §WM.39–45`；`AUGUR-MC v1.4 §8.3`]**
> 本規格之 Constitutional Compliance Statement 依 `AUGUR-WM v1.0 §WM.39–45` 正式格式作成（見 **Annex CS**），**非**暫行模板（本規格作成於 `AUGUR-WM v1.0` 生效日〔2026-07-16〕後，`§WM.45`）。無依該格式作成之聲明使本規格不生效力（`§WM.39`）。
> **義務主體**：本規格自身、Steward。**可判定判準**：Annex CS 之 front-matter 欄位、七節論證、緊張關係節、雙向 DEFER 表俱全（`§WM.40–44`）。

> **ID.81（存續與升版）[N｜carries｜`AUGUR-MC v1.4 §8.6`；`AUGUR-WM v1.0 §WM.46–47`；`AUGUR-ONT v1.0 §ONT.60`]**
> 本規格條款編號依 `§0.3` 穩定；`AUGUR-MC` 或 `AUGUR-WM`／`AUGUR-ONT` major 升版時本規格進入重新認證期（`AUGUR-MC v1.4 §8.6`）。本規格全部「不得」（MUST NOT）義務不得豁免（`AUGUR-MC v1.4 §8.4`）。
> **義務主體**：本規格、Steward。**可判定判準**：升版時 Annex CS 之 `mc-version`／`upper-specs` 欄同步；版本間 diff 檢查——任一既發布編號於後版消失或改指他文者違反本條。

---

## Annex O [N] — OPEN-1 承接（stock_id 代碼重用／時間穩定性採認）

> 承接 `AUGUR-WM v1.0 §A.54`（OPEN-1）、`§D6`，`AUGUR-ONT v1.0` T.90（OPEN-1 Security 判準採認）、T.1／T.20、DO.1。

> **AO.1（承接聲明）[N]**
> `AUGUR-WM v1.0 §A.54` 將本域證券代碼之時間穩定性（改名、代碼重用、借殼）登錄為**顯式未定義行為**，其保守預設（供應商證券代碼為**指涉資訊、非 identifier**；代碼重用／改名一律經 identity claim 表徵）為 [N] 效力，候選判準記載（「代碼相等 ∧ 存續期間重疊」）為 [I] 素材、經本層採認前不生效力。`AUGUR-ONT v1.0` T.1 已**制定** Security↔Issuer 分離型別之同一性判準（其判準內容以 `AUGUR-ONT v1.0` T.1 為準，本層**不複述**其文句，以免跨層漂移／上侵）。本層僅承接其**採認**，並記載被採認判準之 Layer 2 條款引用（`AUGUR-ONT v1.0` T.1），不改寫其內容（改寫屬 Layer 2 制定，違者上侵、違 ID.1）。
> **義務主體**：本規格、採認作成者。**可判定判準**：涉 Security／Issuer 判準之下層條款含對 `§AO.1`／`AUGUR-WM v1.0 §A.54`／`AUGUR-ONT v1.0` T.90 之引用者為合規。

> **AO.2（採認之治理前提）[N]**
> OPEN-1 之正式判準採認**待 Steward／決策層拍板**（`AUGUR-WM v1.0 §D6`）。本規格提供採認機制（§4 ID.20），惟 Security／Issuer 判準之**實質採認生效**須經 Steward 依 `AUGUR-MC v1.4 §8.1` 之書面裁決（或決策層依治理程序）作成；於此拍板前，涉 Security／Issuer 之 Identity 引用依 `§WM.21(e)` 保守解釋為**未解析**。
> **義務主體**：本規格、Steward／決策層。**可判定判準**：無採認紀錄時將 Security 引用視為已解析者違反本條。

> **AO.3（採認後之 lifecycle 銜接）[N]**
> OPEN-1 判準一經採認，代碼重用／借殼之處置即銜接 §6（ID.43 存續邊界截斷）：跨 retire/relist 邊界之同一外部代碼解析為不同存續個體，供應商證券代碼降格為 provisional alias（identity claim，`§WM.21(c)`），發行人（Issuer）同一性以其自身判準（`AUGUR-ONT v1.0` T.20：法律實體同一；借殼／更名不改 Issuer identity，但得改其所發行 Security identity）解析。
> **義務主體**：本規格、Layer 4 消費者。**可判定判準**：採認後之 Security 歷史縫合（違 ID.43）者違反本條。

> **AO.4（Issuer 判準採認之具名落點）[N]**
> `AUGUR-ONT v1.0 §DO.1` 並列下放 Layer 3 之判準採認為 **T.1（Security 判準）與 T.20（Issuer 判準）**。Issuer（T.20：法律實體同一；借殼／更名不改 Issuer identity，但得改其所發行 Security identity，承接 `AUGUR-WM v1.0 §A.57`）之判準採認，由 §4 **ID.20 通用採認機制**承接，其採認記錄依 ID.20 五要素作成；交叉引用 `AUGUR-ONT v1.0 §DO.1` 之 T.20 列與 `AUGUR-WM v1.0 §A.57`。使 `§DO.1` 兩具名 Type（Security、Issuer）於本層各有可雙向解析之採認落點。
> **義務主體**：本規格、採認作成者。**可判定判準**：涉 Issuer（T.20）判準之下層條款含對 `§AO.4`／`AUGUR-ONT v1.0 §DO.1`（T.20）／`§A.57` 之引用、且無採認紀錄時不得將 Issuer 引用視為已解析者為合規。

---

## Annex DO [N] — 下放下層之 DEFER 掛鉤（defers-out）

> **IDO.0（承接義務）[N]** 本表每列為規範性下放掛鉤：本層明示不定義該實作事項，授權並要求目標 Layer 定義之；目標 Layer 規格作成時必須於其 Compliance Statement 之 `defers-in` 欄承接對應列。
> **義務主體**：本規格自身（設掛鉤）、目標 Layer 規格作者（承接）。**可判定判準**：本表每列與 Annex CS front-matter `defers-out` 欄雙向可解析；本層無任一條款對本表所列事項作成可被下層直接消費之實質定義（ID.2／ID.70 下侵判準）。

| 掛鉤 | 本規格落點 | 下放事項 | 目標 Layer | 授權條款 | 承接審計 |
|---|---|---|---|---|---|
| **IDO.1** | ID.30(d)、ID.70 | identity claim 之 **Confidence 語義**（形式化定義、可比較、傳播、門檻） | L4 | `AUGUR-MC v1.4 §P4.E8` | AUD-03/06 |
| **IDO.2** | ID.31、ID.40、ID.70 | identity claim 與 lifecycle 事件之 **Knowledge 五元組欄位設計** | L4 | `AUGUR-MC v1.4 §P4.E1` | AUD-06 |
| **IDO.3** | ID.40 | lifecycle **事件表之物理欄位／索引實作**、tombstone 儲存落地 | L4／L7 | `AUGUR-MC v1.4 §0.6(b)`；`AUGUR-WM v1.0 §D3` | AUD-05 |
| **IDO.4** | ID.23、ID.51 | **resolution 演算實作**、未解析存量指標之**量測落地與門檻值** | L4 | `AUGUR-WM v1.0 §D4`；`AUGUR-ONT v1.0 §DO.1` | AUD-04/06 |
| **IDO.5** | ID.12 | identifier 命名空間之**物理序列化與儲存編碼** | L7 | `AUGUR-MC v1.4 §0.6(b)`；`AUGUR-WM v1.0 §WM.20` | AUD-04 |
| **IDO.6** | ID.61 | **as-of 重建引擎與能力等級**、雙時間查詢操作化 | L4 | `AUGUR-MC v1.4 §P4.E2`；`AUGUR-WM v1.0 §D8` | AUD-07/08 |
| **IDO.7** | ID.42、CS.1-P1 | 自然人**法規對應表本體**與其授權（`AUGUR-WM v1.0 §D17` 之 L6 slice；本層僅承接其 L3 去識別化／抹除機制 slice，見 ID.42） | L6 | `AUGUR-MC v1.4 §P1.E3`；`AUGUR-WM v1.0 §WM.38`、`§D17` | — |
| **IDO.8** | ID.32 | **唯一權威 Representation 之實際指定與落點**（本層僅提供可被指定之結構前提，不自為指定） | L4 | `AUGUR-WM v1.0 §WM.37`、`§WM.14` | AUD-06 |

---

## Annex L4 [N] — 與 Layer 4（Knowledge System）之分界表

> **L4.0（一句判準）[N]** 本層產出「個體的永久參照、其跨體系繫結與其一生的機器機制」；Layer 4 產出「繫結該參照之 Knowledge 之信度、欄位與 as-of 重建能力」。分界必須精確，否則構成下侵（違 ID.2、ID.70）。
> **義務主體**：本規格自身、Layer 4 規格作者。**可判定判準**：下表「本層得為」欄與「Layer 4 專屬」欄無交集，且本層任一條款不落入「Layer 4 專屬」欄者為合規。

| 面向 | 本層得為（Layer 3 專屬） | Layer 4 專屬 |
|---|---|---|
| **identifier** | 鑄造（mint）、命名空間概念結構、永不刪除不變式（§3） | 物理序列化／儲存（IDO.5→L7） |
| **判準採認** | 採認使生效於 resolution、採認紀錄五要素、可謬性（§4） | resolution 演算實作、時限指標量測（IDO.4） |
| **identity claim** | 身份側四要件〔identifier 對／判準引用／Evidence／Confidence 槽位〕、衝突並存、唯一權威表徵之**結構前提**（可被指定之錨點，ID.32）（§5） | Confidence 語義（IDO.1）、完整 Knowledge 五元組欄位（IDO.2）、唯一權威 Representation 之**實際指定**（IDO.8／`§WM.37`） |
| **lifecycle** | merge／split／retire／relist／轉指語義、DynamicEntity 終結語義（settle／expire／convert／redeem，ID.44）、lineage 不變式、tombstone／去識別化語義（§6） | 事件表物理欄位／索引（IDO.3） |
| **provisional** | 解析義務、概念稽核指標之存在與可盤點性、instance/type 標記存續（§7） | 指標量測落地／門檻（IDO.4） |
| **身份屬性 as-of** | 屬性須具 valid/transaction time 繫結（版本存在，§8） | as-of 重建引擎與能力等級（IDO.6） |

---

## Annex TR [N] — WM.44 逐條對應矩陣（憲章＋WM＋ONT → 本規格）

> **TR.0（矩陣之地位與生效要件性）[N]** 依 `AUGUR-WM v1.0 §WM.44`：`AUGUR-MC v1.4`、`AUGUR-WM v1.0`、`AUGUR-ONT v1.0` 全部 [N] 條款均須對應至本規格至少一 [N] 條款、明記 DEFER 掛鉤、或明記「不觸及」及理由。**本矩陣已就三上層規格全部條款逐條完整枚舉**，分族陳列：**TR.A**（`AUGUR-MC v1.4` §P3 家族＋§2.4——**本層核心**）、**TR.B**（`AUGUR-MC v1.4` 其餘：PA／§1.2／§1.3／P1／P2／P4／P5 各 E／W 條款及 §0／§2／§4／§5／§6／§7／§8 逐條）、**TR.C**（`AUGUR-WM v1.0` WM.1–53＋Annex A A.0–A.59＋Annex D D0–D28 逐條）、**TR.D**（`AUGUR-ONT v1.0` ONT.1–62＋Annex T T.0–T.91 逐條）。逐條完整枚舉已滿足 `§WM.44` 之形式充分性；**Steward 充任認定業經作成，本規格自 2026-07-17 起生效**（Steward 裁決第 2026-004 號、AL-2026-008；`§0.5`、`§8.3`），**餘無生效阻卻**；**實質**充分性之最終判斷仍屬 Steward `§8.2` 違憲審查程序。本規格為 Layer 3，其對應對象為三上層（Layer 0–2）；下層（Layer 4–7）之承接由各該規格於其自身 Annex TR 為之，不在本矩陣範圍。
> **義務主體**：本規格、Steward。**可判定判準**：如 `§WM.44` 內建之對應完備性檢查——三上層每一 [N] 條款於本矩陣有落點列（承接／細化／DEFER／不觸及＋理由）者為完備。凡標「不觸及＋理由」之列，其理由為機器可判之處置。上層草案（`AUGUR-ONT`）升版或條款增修時本矩陣對應列**必須**同步維護（ID.81 diff 檢查）。

### TR.A — `AUGUR-MC v1.4` §P3 家族＋§2.4（**本層核心**，逐條）[N]

> §P3「Identity Before Knowledge」為本規格之直接機制化對象；本族每一條款均為本層之核心細化落點。

| MC 條款 | ID 落點 | 模式 |
|---|---|---|
| §P3.D（Identity Before Knowledge 定義） | ID.1、ID.50、§1.1 | 承接（定位） |
| §P3.W1（Augur 的基本單位：Identity） | ID.1、ID.14 | 承接 |
| §P3.W2（Identity 類型開放例示） | ID.11、ID.12、ID.24（世界關係）、Annex O（Security／Issuer） | 承接（型別開放之機制側；型別制定屬 L2） |
| §P3.Y（WHY [I]） | §1.1（Layer 3 定位，[I]） | 承接（資訊性） |
| §P3.E1（引用與解析義務、mint-on-admission、可稽核指標由 L3 定義） | ID.11（鑄造義務）、ID.21、ID.50–ID.53（解析義務＋升級禁止）、ID.51（可稽核指標，承接 `AUGUR-WM v1.0 §D4`） | **細化（核心，落實 AUD-04）** |
| §P3.E2（Identity Lifecycle：永不刪除、轉指可追溯、merge/split/retire/lineage、法規抹除準用 P4.E3） | ID.13（永不刪除）、ID.40–ID.44（lifecycle 事件、轉指、tombstone、去識別化、DynamicEntity 終結） | **細化（核心，落實 AUD-05）** |
| §P3.E3（同一性判準掛鉤、instance/type 明示繫結；判準由 L2／L3 定義） | ID.20–ID.24（採認使生效於 resolution）、ID.53（instance/type 標記存續） | **細化（核心，採認機制）** |
| §2.4（identifier／identity claim 之區分：系統鑄造之永久參照 vs 同一性斷言） | ID.11（外部識別碼非 identifier）、ID.14（identifier 之 Identity 地位）、ID.30–ID.32（identity claim 一級介面） | **細化（核心，落實 AUD-06）** |

### TR.B — `AUGUR-MC v1.4` 其餘家族（逐條）[N]

| MC 條款 | ID 落點／處置 | 模式 |
|---|---|---|
| PA（Prime Axiom）＋§1.1 釐清句 | ID.13（永不刪除）、ID.41（lineage 不變式）、ID.10（跨部署可解析）、ID.30(c)（可追溯 Evidence）、CS.1-PA | 承接 |
| §1.2（標準鏈引用：Reality→Observation→Representation→Identity→Evidence→Knowledge 節選 EV.1–EV.6；Intelligence 節選 EV.7–EV.8） | CS.1-EV-chain（引 §4 EV.4 為本規格標準鏈落點）、ID.50（provisional→resolved→Knowledge 之標準鏈機制化） | 承接 |
| §1.3（五條對稱禁令；第三禁令「沒有 Identity，不允許 Knowledge」／P3 為本層直接機制化對象） | ID.50（未解析 Observation 不得升級 Knowledge，機制化第三禁令）；其餘四禁令分屬 P1／P2／P4／P5，見本表與 TR.A 各該原則列 | 承接（第三禁令核心機制化） |
| P1（Reality First 標題） | ID.11、ID.10 | 承接 |
| P1.D（定義） | ID.1、ID.11 | 承接 |
| P1.E1（開放來源） | ID.11（外部識別碼降格為指涉資訊） | 細化 |
| P1.E2（共同世界模型之語義） | ID.10（跨部署對齊語義義務）、ID.32（唯一權威表徵結構前提） | 細化（本層語義義務核心） |
| P1.E3（Bounded Representation） | ID.42（去識別化）、ID.60（時變屬性 as-of）；法規對應表本體 DEFER Layer 6（IDO.7） | 承接＋DEFER |
| P1.W1（Augur 必須優先描述 Reality，而不是優先適配現有資料來源） | ID.11（禁外部識別碼裸字串直充身份） | 承接 |
| P1.Y（WHY [I]） | §1.1（[I]） | 承接（資訊性） |
| P2（Representation Before Intelligence 標題） | ID.21、ID.50 | 承接 |
| P2.D（定義） | ID.50 | 承接 |
| P2.E1（禁止 AI 直接從 raw data 建立永久性 Knowledge） | ID.50、ID.30(c) | 承接 |
| P2.E2（Model output 不得未經 Evidence 通道（§2.11），直接成為權威 World Representation 或 Knowledge） | ID.30(c)、ID.40（lifecycle 事件之 Evidence 義務） | 承接 |
| P2.E3（self-reported 標記） | ID.30（claim 之 Evidence 要件）、ID.52 | 承接 |
| P2.E4（禁止 Representation 被視為 Reality 本身） | ID.30(d)（Confidence 槽位存在） | 承接（槽位） |
| P2.E5（錯誤發現後之 fail-safe 反應） | ID.22（採認撤回之 fail-safe 重評估） | 承接 |
| P2.W1（任何 Prediction、Reasoning、Planning、Decision、Agent Action，皆必須建立於 World Representation） | ID.50（未解析不得升級 Knowledge） | 承接 |
| P2.W2（權威順序釐清） | ID.50（升級門檻）承接；確立工作流實作 DEFER Layer 4–5，本層不代定（ID.23） | 承接＋界分 |
| P2.Y（WHY [I]） | §1.1（[I]） | 承接（資訊性） |
| P3（Identity Before Knowledge 全家族） | 見 **TR.A**（逐條） | 細化（核心） |
| P4（Evidence Before Conclusion 標題） | ID.14、ID.30–ID.31、ID.40；語義填充 DEFER Layer 4 | 承接＋DEFER |
| P4.D（定義） | ID.30(c) | 承接 |
| P4.E1（Knowledge 五元組） | ID.31（claim 為 Knowledge）、ID.40；完整欄位設計 DEFER Layer 4（IDO.2） | 承接＋DEFER |
| P4.E2（Time（雙時間性）） | ID.60（繫結存在）、ID.61（分界）；重建引擎 DEFER Layer 4（IDO.6） | 細化（繫結）＋DEFER |
| P4.E3（Supersede（只失效不刪除）） | ID.22（採認只標 superseded）、ID.40（事件只失效不刪除）、ID.42（法規抹除留痕準用） | 細化 |
| P4.E4（Defeasible（可謬性）） | ID.22（採認之可謬性） | 承接 |
| P4.E5（Conflict（矛盾保存）） | ID.31（衝突 claim 並存、禁 last-write-wins） | 承接 |
| P4.E6（Provenance（遞迴溯源）） | ID.30(c)（Evidence 遞迴可溯源） | 承接 |
| P4.E7（NoLaundering（信任不可洗白）） | ID.30(c)；來源信任分級表 DEFER Layer 4（ID.70） | 承接＋DEFER |
| P4.E8（Confidence（語義與消費）） | ID.30(d)、ID.70；語義 DEFER Layer 4（IDO.1） | DEFER（本層設槽＋下放） |
| P4.W1（Augur 不接受：無 Source 之 Knowledge、不可重現之結果、無 Evidence 之推論） | ID.30(c)、ID.11 | 承接 |
| P4.Y（WHY [I]） | §1.1（[I]） | 承接（資訊性） |
| P5（Accountability Before Action 標題） | CS.1-P5 | 部分不適用＋理由 |
| P5.D（定義） | 不觸及＋理由：Action 定義屬 Layer 6；本層僅型別化行動主體之 identifier（CS.1-P5） | 不觸及＋理由 |
| P5.E1（Action 六元組與問責） | 不觸及＋理由：Action 六元組與行動治理屬 Layer 6，本層不定義；惟採認（ID.20）／lifecycle（ID.40）／去識別化（ID.42）之作成者記錄與 P5 精神相容 | 不觸及＋理由（治理記錄相容） |
| P5.E2（風險分級表、完備性等級、Confidence 門檻） | 不觸及＋理由：風險分級／門檻屬 Layer 4–6；本層不定義 | 不觸及＋理由 |
| P5.W1（任何 Action 必須可歸責於單一 Identity） | 不觸及＋理由：問責治理屬 Layer 6 | 不觸及＋理由 |
| P5.W2（人類權威閘） | 不觸及＋理由：人類權威閘資格判準屬 Layer 6；本層去識別化／採認之作成者具名與其精神相容 | 不觸及＋理由 |
| P5.W3（不可逆／高影響需最高完備性） | 不觸及＋理由：完備性等級與綁定屬 Layer 4–6 | 不觸及＋理由 |
| P5.W4（Agent 僅持有完成當前經授權 Plan 所需之最小權限） | 不觸及＋理由：監督否決度量屬 Layer 6 | 不觸及＋理由 |
| P5.W5（系統不得規劃、執行或學習任何降低人類監督與否決能力之行為） | 不觸及＋理由：風險預設屬 Layer 6；本層不削弱 | 不觸及＋理由 |
| P5.Y（WHY [I]） | 不觸及＋理由：屬 Layer 6 行動治理，資訊性 | 不觸及＋理由 |
| §0.2（規範用語約定：必須／不得／應／得四級效力用語） | §0.2（沿用不重定義，全文一致）、【地位】末句（效力準用 `AUGUR-WM v1.0 §WM.53`） | 承接 |
| §0.4（權威語言聲明） | §0.4 | 承接 |
| §0.5（適用範圍：Layer 對照表） | §0.1、§0.5、【地位】（Layer 3 欄登錄） | 承接 |
| §0.6(a)（lex superior） | 引言、ID.4 | 承接 |
| §0.6(b)（概念層獨立性） | §0.5、ID.12、ID.2、Annex DO | 承接 |
| §2.4（identifier／identity claim 區分） | 見 **TR.A** | 細化（核心） |
| §2.5（Evidence 定義） | ID.30(c)（不重定義，承接） | 承接（不重定義） |
| §2.6（Knowledge 定義） | ID.31（claim 為 Knowledge，不重定義） | 承接（不重定義） |
| §2.10（Confidence 定義） | ID.30(d)（槽位，語義不重定義） | 承接（不重定義） |
| §2.11（Evidence 通道） | ID.50、CS.1-EV-chain（provisional→resolved→Knowledge） | 承接 |
| §4 canonical chain（EV.1–EV.12） | ID.50（EV.4 Identity 為本層機制化落點）、CS.1-EV-chain（節選不跳節點）；EV.1–3／EV.5–12 承接不重定義 | 承接 |
| §5 架構角色（system of record／表徵／Reasoning／Intelligence／介面／執法點） | 不觸及＋理由：架構角色屬 Layer 4–6；本層僅型別化各角色所涉個體之 identifier，不代定角色機制 | 不觸及＋理由 |
| §6 F1–F6（Data First Architecture／Model First Architecture／Agent First Architecture／Knowledge Without Identity／Intelligence Without Evidence／Unaccountable Action） | F2／F3（無 Identity 繫結／無 Source 之 Knowledge 拒斥）→ ID.11、ID.50；F1／F4／F5／F6 不觸及＋理由：屬 Layer 4–6 之禁止型態 | 承接（F2／F3）＋不觸及＋理由 |
| §7（Long-Term Stability Rule（十年以上演化原則）） | ID.1、§1.1（Layer 3 核心錨定）；Identity 為五項不變核心之一，本規格即其 Layer 3 機制化全部 | 承接（核心錨定） |
| §8.1（Constitution Steward（憲章權威）） | 【地位】、ID.81（生效後登錄；充任認定屬 Steward） | 承接 |
| §8.2（違憲後果、審查程序與衝突優先序） | 【地位】、CS.4（實質充分性屬 §8.2 程序） | 承接 |
| §8.3（合規聲明義務與可判定性元規則） | ID.80、§0.5（每條附可判定判準） | 承接 |
| §8.4（不可豁免核心） | ID.81（全部 MUST NOT 不豁免） | 承接 |
| §8.5（Amendment Procedure 修訂程序：提案權、Steward 原則級議決之程序＋實質要件、Amendment Log 記錄、Eternity Clause） | 不觸及＋理由：本條規範 MC 自身之修訂程序，義務主體為 Steward 與 MC 修訂行為本身，非 Layer 3 規格義務來源；本規格自身之生效／登錄程序承 §8.1（Amendment Log）／§8.3（過渡規則），已見 ID.81、【地位】，不涉 MC 條文修訂程序本身 | 不觸及＋理由 |
| §8.6（版本語義、引用格式與編號穩定性） | §0.3、ID.81 | 承接 |

### TR.C — `AUGUR-WM v1.0`（全部 [N]，逐條）[N]

**(1) 正文 WM.1–WM.53**

| WM 條款 | ID 落點／處置 |
|---|---|
| WM.1（從屬） | 引言、ID.4—承接 |
| WM.2（細化不重定義） | §0.5（不重定義元規則）—承接 |
| WM.3（管轄與 DEFER 紀律） | ID.1、ID.4—承接 |
| WM.4（概念層獨立性＋刪名測試） | §0.5（`§0.6(b)`）—承接 |
| WM.5（任務） | §1.1—承接 |
| WM.6（領域 Profile 與領域前身文件） | 不觸及＋理由：Profile 框架屬存在層，本層消費其產物、不重定義框架 |
| WM.7（最高抽象） | ID.11（外部識別碼非最高抽象）—承接 |
| WM.8（結構獨立性） | 不觸及＋理由：結構獨立性屬存在層本體 |
| WM.9（權威三分） | 不觸及＋理由：表徵權威三分屬 Layer 1／Layer 4；本層僅提供 identifier 錨點（ID.32） |
| WM.10（Observation Store 宣告） | 不觸及＋理由：Observation Store 屬 Layer 1／Layer 4 |
| WM.11（referent 繫結） | ID.11、ID.50（referent→已解析 Identity）—承接 |
| WM.12（近似性與來源保留） | 不觸及＋理由：近似性→Confidence 語義屬 Layer 4；本層僅設槽（ID.30(d)） |
| WM.13（三性質可判定判準＋演化四不變式） | ID.13、ID.40（Identity 存續跨 Ontology／Representation 演化）—承接（不重定義性質判準） |
| WM.14（語義唯一性與一對多映射） | ID.32（唯一權威表徵結構前提、一對多映射與衝突保存）—落實 |
| WM.15（同一事實多通道之同一性宣告） | ID.51(c)（顯式待決同一性存量）、ID.32（無宣告即非同一）—承接 |
| WM.16（衝突與證據不足之表達力） | ID.31（衝突 claim 並存）—承接 |
| WM.17（模態內容） | 不觸及＋理由：模態型別屬 Layer 1／Layer 4 |
| WM.18（候選斷言之地位與狀態轉換） | ID.50（provisional 地位與升級禁止）—承接 |
| WM.19（基本單位） | ID.11、ID.12—承接 |
| WM.20（跨部署解析與命名空間不強制） | ID.10（授權範圍與語義義務保留）、§3（ID.10–ID.14）—**細化（核心授權承接）** |
| WM.21（結構位置義務與效力封印） | ID.20（(e) 採認）、ID.21、ID.30（(c) claim 對）、ID.50（(d) 已解析引用義務）、§4／§5—**細化（分項承接）** |
| WM.22（生命週期存續不變式） | ID.13、ID.40、ID.41、§6—**細化（核心）** |
| WM.23（實體類型開放例示） | ID.11（承接開放例示，不重定義型別）—承接 |
| WM.24（canonical chain 承接） | CS.1-EV-chain、ID.50—承接 |
| WM.25（變更二分） | ID.40（correct／restatement 為 lifecycle 事件）—承接 |
| WM.26（自反性） | ID.11（Augur 自身之個體亦須鑄造 identifier）—承接 |
| WM.27（Action 六元組世界事件與禁止型態之無位置性） | 不觸及＋理由：Action 六元組屬 Layer 6；本層僅型別化行動主體 identifier |
| WM.28（人類權威表徵位置） | 不觸及＋理由：權威表徵位置屬 Layer 4；本層僅提供 identifier 錨點 |
| WM.29（fail-safe 狀態容納） | ID.22（採認撤回之 fail-safe 重評估）—承接（判定主體 DEFER Layer 4–6） |
| WM.30（雙時間性） | ID.60、ID.61（身份屬性 valid／transaction time）—細化 |
| WM.31（時間屬性雙宣告） | ID.60（身份時變屬性雙時間繫結）—細化 |
| WM.32（觀測定案性） | 不觸及＋理由：觀測定案性判準屬 Layer 4 |
| WM.33（永久標記表達力） | ID.53（instance/type 標記存續）、ID.21（provisional 標記）—承接 |
| WM.34（核心不變式之可機器稽核 (a)(b)） | §0.5（每條附義務主體＋可判定判準）—承接 |
| WM.35（落地即整合；消費設閘不阻斷落地） | ID.52（unmapped 準用）、ID.51(c)—承接 |
| WM.36（World Concept Registry 與消費規則） | ID.32（Registry 消費結構前提）；Registry 實作載體 DEFER Layer 4／7—承接＋界分 |
| WM.37（唯一權威表徵落實義務） | ID.32（結構前提；實際指定 DEFER Layer 4，IDO.8）—落實＋DEFER |
| WM.38（自然人之有界表徵） | ID.42（去識別化）、§8（ID.60）；L6 slice DEFER Layer 6（IDO.7）—承接＋DEFER |
| WM.39（適用範圍與效力規則） | ID.80、Annex CS—承接 |
| WM.40（機器可稽核 front-matter） | Annex CS front-matter—承接 |
| WM.41（逐原則論證本文） | CS.1—承接 |
| WM.42（緊張關係與豁免登記） | CS.2—承接 |
| WM.43（雙向 DEFER 承接表） | CS.3、Annex DO—承接 |
| WM.44（形式充分性判準） | CS.4、Annex TR（本矩陣）—**落實** |
| WM.45（過渡承接／正式格式） | ID.80（作成於 Layer 1 生效日 2026-07-16 後）—承接 |
| WM.46（引用格式與編號穩定性） | §0.3、ID.81—承接 |
| WM.47（審查與豁免承接） | ID.81、CS.2—承接 |
| WM.48（重新認證與書面形式） | ID.81—承接 |
| WM.49（地位與衝突規則） | 【地位】節、ID.4—承接 |
| WM.50（必備五部結構） | 全文結構（front-matter／CS.1 論證／CS.2 緊張／CS.3 DEFER 表／Annex TR 矩陣）—承接 |
| WM.51（越界禁止） | ID.2、ID.70—承接 |
| WM.52（版本節奏隔離） | ID.81—承接 |
| WM.53（文件約定之規範地位） | 【地位】末句（準用 `§WM.53`）、§0—承接 |

**(2) WM Annex A（A.0–A.59；領域 Profile）**——凡標「領域實例」者，理由為：領域型別／事件實例屬存在層 Profile，本層對其個體一體適用 §3（鑄造）／§4（採認）／§6（lifecycle）／§8（as-of），不逐型別重定義。

| A 條款 | ID 落點／處置 | A 條款 | ID 落點／處置 |
|---|---|---|---|
| A.0（地位與範圍） | 不觸及＋理由：Annex A 地位條，存在層 | A.30（DataFinality） | 不觸及＋理由：定案性屬 Layer 4 |
| A.1（Security） | Annex O（AO.1，Security 判準採認落點）—承接 | A.31（槽位設置） | ID.30—承接 |
| A.2（Roster） | 不觸及＋理由：領域實例（名冊成員關係 lifecycle 適用 §6） | A.32（候選記載） | ID.50—承接 |
| A.3（Index） | ID.12（Index 為另一 Instance 命名空間，互斥）—承接 | A.33（第二識別體系繫結） | ID.30、AO.3（外部代碼為 provisional alias）—**承接（核心 AUD-06）** |
| A.4（TradingCalendar） | 不觸及＋理由：領域實例 | A.34（最小時間粒度） | ID.60—承接 |
| A.5（MarketParticipant 階層） | 不觸及＋理由：領域實例 | A.35（每通道時間屬性雙宣告） | ID.60—承接 |
| A.6（DerivativeContract） | ID.44（結算消滅終結表徵）—承接 | A.36（通道時間模型不對稱之揭露） | ID.61—承接 |
| A.7（ConvertibleBond） | ID.44（轉換／贖回終結表徵）—承接 | A.37（定案性判準之宣告形式） | 不觸及＋理由：定案性屬 Layer 4 |
| A.8（Warrant） | ID.44（到期失效終結表徵）—承接 | A.38（預測任務時間邊界） | 不觸及＋理由：屬 Layer 4–5 |
| A.9（ForeignSecurity） | 不觸及＋理由：領域實例（ISIN 繫結見 A.33／ID.30） | A.39（Observation Store 域內認定） | 不觸及＋理由：屬 Layer 4 |
| A.10（維度族） | ID.12（series_id 空間與 stock_id 空間互斥）—承接 | A.40（「API 即權威」定位限定） | ID.11（外部來源非 identifier）—承接 |
| A.11（EconomicIndicator） | ID.12（series_id 命名空間）、ID.60（vintage as-of）—承接 | A.41（系統記錄之域內實例） | 不觸及＋理由：屬 Layer 4 |
| A.12（IndustryClassification） | ID.12（type 節點非 Instance）、ID.60（分類 as-of）—承接 | A.42（排除閉集與排除理由類型） | 不觸及＋理由：屬 Layer 4 |
| A.13（DataProvider） | ID.11（供應商識別碼為指涉資訊）—承接 | A.43（下市與可見性） | ID.43（retire 之 Evidence 來源）—承接 |
| A.14（Model 與 CoreUniverse） | ID.60（成員資格 as-of 版本化）—承接 | A.44（語料通道 license 三軌） | 不觸及＋理由：屬 Layer 4–6 |
| A.15（HumanDecisionMaker） | ID.42（自然人去識別化）—承接 | A.45（真兆三問） | 不觸及＋理由：策略哲學屬 Layer 5–6 |
| A.16（KnowledgeCorpus 語料實體族） | 不觸及＋理由：領域實例 | A.46（三敵框架） | 不觸及＋理由：屬 Layer 5–6 |
| A.17（Catalog 元資料） | 不觸及＋理由：領域實例 | A.47（as-of 紀律為判準非實作） | ID.60、ID.61—承接 |
| A.18（NewsEvent） | 不觸及＋理由：領域實例 | A.48（思想≠特定值） | 不觸及＋理由：屬 Layer 4–6 |
| A.19（GATE 預註冊實驗） | 不觸及＋理由：領域實例（自反 identifier 適用 ID.11） | A.49（經濟價值≠準確率） | 不觸及＋理由：策略哲學屬 Layer 5–6 |
| A.20（Augur 自身） | ID.11（自反性，Augur 個體須鑄造 identifier）—承接 | A.50（誠實輸出契約之表達力承接） | 不觸及＋理由：輸出契約屬 Layer 6 |
| A.21（CorporateAction） | ID.40（corporate action 為 lifecycle Evidence）—承接 | A.51（管線分層本體論之角色對映） | 不觸及＋理由：管線分層屬 Layer 5／7 |
| A.22（財報與月營收公開事件） | ID.40（restatement 為 correct 事件）—承接 | A.52（假說與 GATE 之定位） | 不觸及＋理由：屬 Layer 5–6 |
| A.23（RegulatoryStateChange） | ID.40；領域實例—承接 | A.53（系統建議、人決策） | 不觸及＋理由：屬 Layer 6 |
| A.24（期權結算事件） | ID.44（settle 終結表徵）—承接 | A.54（OPEN-1：stock_id 時間穩定性） | **Annex O（AO.1–AO.4）—承接（核心）** |
| A.25（Delisting） | ID.43（retire 事件之 Evidence 來源）—承接 | A.55（OPEN 節之消費規則） | 不觸及＋理由：OPEN 承接屬存在層 |
| A.26（PriceLimit 漲跌停狀態） | 不觸及＋理由：領域實例（point-in-time 狀態） | A.56（Profile 增補程序） | 不觸及＋理由：Profile 程序屬存在層 |
| A.27（信用交易 stock-flow 狀態族） | 不觸及＋理由：領域實例 | A.57（Issuer） | **AO.4（Issuer 判準採認落點）—承接** |
| A.28（持股結構狀態） | 不觸及＋理由：領域實例 | A.58（MarketTrade／DailyBar） | 不觸及＋理由：領域實例 |
| A.29（UniverseMembership） | ID.60（成員資格 as-of）—承接 | A.59（涉自然人通道之域內宣告） | ID.42、CS.1-P1—承接 |

**(3) WM Annex D（D0–D28；下放掛鉤）**——本層之 defers-in 為 **D2（採認側）／D3／D4／D5／D6／D17（L3 slice）**（見 §2.1 ID.3 承接盤點）；D7／D8／D9 為本層引用其概念槽但語義下放 Layer 4（IDO.1／2／6）；餘為下放他層之掛鉤，本層不觸及＋理由。

| D 條款 | ID 落點／處置 | D 條款 | ID 落點／處置 |
|---|---|---|---|
| D0（DEFER 總表地位） | ID.3、Annex DO 承接體例—承接 | D15（fail-safe 判定程序） | ID.22（受影響範圍界定 DEFER Layer 4–6）—承接界分 |
| D1（抓取模式五態） | 不觸及＋理由：下放 Layer 5／7 攝取 | D16（永久標記落地） | ID.53、ID.21（標記存續語義）—承接 |
| D2（同一性判準之採認側） | **ID.20–ID.24（採認）—承接（核心）** | D17（法規對應表） | ID.42（L3 去識別化 slice）；L6 slice DEFER Layer 6（IDO.7）—承接＋DEFER |
| D3（identity claim 表介面、轉指、tombstone、去識別化） | **§5（ID.30–ID.32）／§6（ID.40–ID.44）—承接（核心）** | D18（拓撲／Registry 載體／直綁消除） | ID.32（結構前提）；載體 DEFER Layer 4／7—承接＋界分 |
| D4（provisional 解析時限與未解析存量指標） | **ID.51（可稽核指標）—承接（核心）** | D19（RBAC 表設計） | 不觸及＋理由：下放 Layer 6／7 |
| D5（identifier 鑄造、結構、命名空間設計） | **§3（ID.10–ID.14）—承接（核心）** | D20（輸出契約本體） | 不觸及＋理由：下放 Layer 6 |
| D6（證券代碼身份假設之判準採認） | **Annex O（AO.1–AO.4）—承接（核心）** | D21（維度白名單取得機制） | 不觸及＋理由：下放 Layer 4 |
| D7（Knowledge 五元組欄位） | 不觸及＋理由：欄位設計屬 Layer 4；本層設槽（ID.31）、下放 IDO.2 | D22（多重比較家族治理） | 不觸及＋理由：下放 Layer 4–5 |
| D8（as-of 重建機制與能力等級） | 不觸及＋理由：重建引擎屬 Layer 4；本層定繫結存在（ID.60/61）、下放 IDO.6 | D23（as-of 查詢操作化） | 不觸及＋理由：下放 Layer 4／7 |
| D9（Confidence 形式化語義） | 不觸及＋理由：Confidence 語義屬 Layer 4；本層設槽（ID.30(d)）、下放 IDO.1 | D24（序列化格式） | 不觸及＋理由：下放 Layer 7（IDO.5 對應） |
| D10（supersede／tombstone／信任分級） | ID.40（只失效不刪除）、ID.42（tombstone）；信任分級 DEFER Layer 4—承接＋界分 | D25（儲存引擎） | 不觸及＋理由：下放 Layer 7 |
| D11（完備性等級） | 不觸及＋理由：完備性等級屬 Layer 4 | D26（重編／對帳差異處置） | ID.40（correct 事件）—承接 |
| D12（外部知識入判準／GATE 體系） | 不觸及＋理由：確立工作流屬 Layer 4–5 | D27（point-in-time 快照） | ID.60（身份時變屬性 point-in-time）—承接 |
| D13（隔離稽核落地） | 不觸及＋理由：下放 Layer 5／7 | D28（其餘機制落地） | 不觸及＋理由：下放 Layer 5–7（依 `§WM` D28 所指層） |
| D14（確立程序與候選斷言工作流） | ID.50（升級門檻）承接；工作流 DEFER Layer 4–5 | | |

### TR.D — `AUGUR-ONT v1.0`（全部 [N]，逐條）[N]

**(1) 正文 ONT.1–ONT.62**

| ONT 條款 | ID 落點／處置 |
|---|---|
| ONT.1（從屬） | 引言、ID.4—承接 |
| ONT.2（細化不重定義） | §0.5（不重定義元規則）—承接 |
| ONT.3（管轄與 DEFER 紀律） | ID.1、ID.4—承接 |
| ONT.4（概念層獨立性＋刪名測試承接） | §0.5（`§0.6(b)`）—承接 |
| ONT.5（[N]/[I] 標注、三態與位置） | §0.3、§0.5（refines／carries／hooks 三態）—承接 |
| ONT.6（任務） | §1.1（不觸及型別任務，屬 L2）—承接 |
| ONT.7（定位：三層不僭越） | ID.1—承接 |
| ONT.8（型別定義不得由來源反推） | ID.11（外部識別碼非最高抽象）—承接（不重定義型別） |
| ONT.9（引用格式與編號穩定性） | §0.3、ID.81—承接 |
| ONT.10（頂層本體範疇） | 不觸及＋理由：頂層範疇制定屬 Layer 2 型別層 |
| ONT.11（開放例示之封閉化紀律） | ID.40（lifecycle 事件開放集之封閉化體例）—承接 |
| ONT.12（型別定義三要件） | 不觸及＋理由：型別定義屬 Layer 2 |
| ONT.13（存在宣告 ↔ 分類體系接合） | ID.53（instance/type 標記存續）—承接 |
| ONT.20（判準宣告義務；制定屬 L2、採認屬 L3） | ID.20（採認使生效於 resolution，不重定義判準內容）—**承接（核心）** |
| ONT.21（判準效力與 Layer 3 採認之封印） | ID.20、ID.21（未採認即未解析）—**細化（核心，採認解封）** |
| ONT.22（外部識別碼非 identifier） | ID.11、ID.30(a)—**細化（核心 AUD-06）** |
| ONT.30（繫結對象標記語義） | ID.53（標記存續與解析落實）—承接 |
| ONT.31（型別個體命名空間之概念層隔離） | ID.12（型別化命名空間隔離之機制側）—**細化（核心）** |
| ONT.40（世界關係為一級型別範疇） | ID.24（世界關係之身份解析：端點有序組×valid time）—**細化（核心）** |
| ONT.41（世界量為維度索引型別） | ID.12（series_id 維度空間與 stock_id 互斥）—承接 |
| ONT.50（規範性對映義務；唯一權威表徵型別側前提） | ID.32（Representation 唯一權威表徵之結構前提承接）—承接 |
| ONT.60（版本語義與型別存續不變式） | ID.81—承接 |
| ONT.61（審查與豁免承接） | ID.81、CS.2—承接 |
| ONT.62（合規聲明義務） | ID.80、Annex CS—承接 |

**(2) ONT Annex T（T.0–T.91；台股型別階層與同一性判準）**——型別定義與同一性判準屬 Layer 2 型別層；本層對其個體 **採認**（ID.20）與 **機制化**（§3／§5／§6／§8），不重述型別定義／判準文句。故 Annex T 全列之基準處置為 **不觸及＋理由（型別／同一性判準制定屬 Layer 2，本層採認而不重定義）**，逐號涵蓋：T.0、T.1、T.2、T.3、T.4、T.5、T.6、T.7、T.8、T.9、T.10、T.11、T.12、T.13、T.20、T.21、T.22、T.23、T.24、T.25、T.26、T.27、T.28、T.29、T.30、T.31、T.32、T.33、T.34、T.35、T.36、T.40、T.41、T.42、T.43、T.44、T.50、T.51、T.52、T.53、T.60、T.61、T.62、T.90、T.91。**下列具名 Type 於本層另有具名採認／機制落點**（其型別定義仍不重述，僅承接其採認或機制化）：

| T 條款 | ID 落點（採認／機制化，不重定義型別） |
|---|---|
| T.1（Security 判準） | AO.1（Security 判準採認落點，承 ID.20） |
| T.20（Issuer 判準） | AO.4（Issuer 判準採認落點，承 ID.20） |
| T.90（Security，代碼重用 OPEN-1） | Annex O（AO.1–AO.4）＋ID.43（存續邊界截斷） |
| T.3（DerivativeContract 生命週期） | ID.44（settle 結算消滅終結表徵） |
| T.4（ConvertibleBond 生命週期） | ID.44（convert／redeem 終結表徵） |
| T.5（Warrant 生命週期） | ID.44（expire 到期失效終結表徵） |
| T.23（HumanDecisionMaker） | ID.42（自然人 identity 側去識別化／法規強制抹除） |
| T.24（IndustryClassification／身份屬性 as-of 化） | ID.60（時變屬性 as-of 繫結；今日屬性判歷史為禁止型態） |
| T.34（生命週期屬性宣告／Delisting） | ID.43（retire）、ID.44（DynamicEntity 終結） |
| T.42（ISIN identity claim） | ID.30（外部識別碼降格為 provisional alias，claim 端點須系統 identifier） |
| T.43（instance/type 標記；point-in-time；as-of 化） | ID.53（標記存續）、ID.60（as-of 繫結） |
| T.50（IssuanceRelation） | ID.24（世界關係身份解析：端點有序組×valid time） |
| T.51（UnderlyingRelation） | ID.24（世界關係身份解析）、ID.44（ConvertibleBond→標的股以事件＋lineage） |

### TR.Y — 2026-07-18 窮舉補列（RULING-2026-019 決策一）[N]

> **TR.Y（矩陣完備性補列與『缺 0 條』宣稱之更正）[N]** 本規格首次三鏡對抗審查（2026-07-18）查獲：TR.0／TR.Z／【地位】之「三上層（`AUGUR-MC v1.4`／`AUGUR-WM v1.0`／`AUGUR-ONT v1.0`）全部 [N] 條款逐條完整枚舉、**缺 0 條**」宣稱**不實**——15 組上層 [N] 條款於矩陣完全無落點列（下表補列）。（§5.1–§5.6 及裸章 §0/§1/§2/§3/§8 之 [N] 由既有 §5 架構角色章列及各章子條列於章／子條 granularity 覆蓋，linter 形式關卡滿足；本表補列者為既有矩陣完全無落點之子條與 Annex 群。）經窮舉工作流（wf_ba742919-e04）＋獨立複核逐條定處置。**⚠️ 誠實界限**：完備性之**機械強制**（`§8.3` linter matrix-coverage check——窮舉上層 [N] 條款 vs 矩陣列）尚未建置；在其建置前（RULING-2026-019 決策四第二輪），「逐條完整枚舉」係**手工維護**，其完備性不得再以單方宣稱視為終局。TR.A–TR.Z 各處「缺 0 條」字樣應連同本更正讀。

| 上層 [N] 條款 | 本規格落點 | 處置＋理由 |
|---|---|---|
| MC §2.1（Reality 定義） | ID.11、TR.C A.20 | 承接（定義類本層使用不重定義；自反性落點 ID.11） |
| MC §2.2（Observation 定義） | ID.50、ID.11 | 承接（本層使用不重定義） |
| MC §2.3（Representation 定義） | ID.32 | 承接（唯一權威表徵為 ID.32 結構前提，不重定義） |
| MC §2.7（Intelligence 定義） | — | 不觸及（Intelligence 機制屬 Layer 4–6，本層為概念層 Identity 規格） |
| MC §2.8（Agent 定義） | P5.D／P5.E1、ID.11 | 承接（Agent 為 Identity 之一種，本層型別化其 identifier；行為面界分 L6） |
| MC §2.9（Action 定義） | P5.D | 不觸及（Action 六元組與行動治理屬 Layer 6） |
| MC §0.1（名稱、層級與版本） | 本層 §0.1、【地位】 | 承接（本層履行相同體例） |
| MC §0.3（條文效力標注） | 本層 §0.3、ID.81 | 承接（同 §0.2 體例，本層採 [N]/[I] 標注與編號穩定） |
| WM Annex C §C.1–§C.10 | — | 不觸及（WM 對 MC 之合規聲明，義務主體＝WM 自身，非本層義務；本層另有自身 Annex CS） |
| WM Annex E §E1（收錄義務） | — | 不觸及（義務主體逐字『本規格後續修訂者』＝WM 自身收錄義務） |
| ONT Annex DI §DI.0–§DI.3（defers-in） | ID.20 | 不觸及（DI 為 ONT 承接型別『制定』之掛鉤＝Layer 2 義務；本層之 L3 分承循 DO.1–4） |
| ONT Annex DO §DO.0–§DO.4（defers-out→L3） | ID.3、ID.20、ID.23、CS.3 | 承接（ONT 明示下放 L3 之掛鉤，本層 defers-in 核心；軟缺——實質已承接惟漏入矩陣） |
| ONT Annex T-Map §TM.0 | — | 不觸及（Layer 2 型別對映治理；本層消費對映不建表） |
| ONT Annex CS §CS.1–§CS.10 | — | 不觸及（ONT 對 MC/WM 之合規聲明，義務主體＝ONT 自身） |
| ONT Annex EO §EO.1（收錄義務） | — | 不觸及（義務主體逐字『本規格後續修訂者』＝ONT 自身） |

> **TR.Z（逐條完整枚舉之完成與殘餘生效阻卻）[N]** TR.A–TR.D 已就 `AUGUR-MC v1.4`（§P3 家族＋§2.4 核心，及 PA／§1.2／§1.3／P1／P2／P4／P5 與 §0／§2／§4／§5／§6／§7／§8 逐條）、`AUGUR-WM v1.0`（WM.1–53＋Annex A A.0–A.59＋Annex D D0–D28）、`AUGUR-ONT v1.0`（ONT.1–62＋Annex T T.0–T.91）**全部條款逐條枚舉落點**（承接／細化／DEFER／不觸及＋理由），滿足 `§WM.44`「任一條款無對應且無明記者，聲明不完整」之形式充分性要件——**形式充分性（`§WM.44`）已成就**。**Steward 充任認定業經作成，本規格自 2026-07-17 起生效**（Steward 裁決第 2026-004 號、AL-2026-008；`§0.5`、`§8.3`），**殘餘生效阻卻已解消**；**實質**充分性之最終判斷仍屬 Steward 違憲審查程序（`§8.2`），非本規格單方可成就，充任不排除嗣後之違憲審查。上層草案（`AUGUR-ONT v1.0`）於升版或條款增修時，本矩陣對應列**必須**同步維護（ID.81 diff 檢查）。
> **義務主體**：本規格、Steward。**可判定判準**：三上層全部 [N] 條款逐一於本矩陣有落點列者為完備（已成就）；上層條款增修而本矩陣未同步致某新條款無落點者，聲明重回不完整。

---

## Annex CS [N] — Constitutional Compliance Statement（依 `AUGUR-WM v1.0 §WM.39–45` 格式）

本 Annex 為**規範性聲明文件**（[N]）：其存在與內容為本規格之生效要件（ID.80、`AUGUR-MC v1.4 §8.3`、`AUGUR-WM v1.0 §WM.39`）。本聲明依 `AUGUR-WM v1.0 §WM.39–45` **正式格式**作成（非暫行模板，`§WM.45`：本聲明作成於 Layer 1 生效日 2026-07-16 之後）。**地位提示**：本規格為 **v1.0 生效版本**，Steward 充任認定已作成，自 2026-07-17 起生效（Steward 裁決第 2026-004 號，AL-2026-008；見【地位】、ID.80）；本聲明之**實質**充分性最終判斷仍屬 Steward `§8.2` 違憲審查程序。

```
compliance-statement:
  spec: Augur Identity Specification
  spec-version: v1.0
  layer: 3
  mc-version: AUGUR-MC v1.4
  upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v1.0]
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: [T-ID-1, T-ID-2, T-ID-3, T-ID-4, T-ID-5, T-ID-6]
  defers-in: [WM.D2(採認側), WM.D3, WM.D4, WM.D5, WM.D6, WM.D17(L3側), ONT.DO.1, ONT.DO.2, ONT.DO.3, ONT.DO.4]
  defers-out: [IDO.1, IDO.2, IDO.3, IDO.4, IDO.5, IDO.6, IDO.7, IDO.8]
  date: 2026-07-17
  author: Layer 3 Identity 規格撰稿官（依 Constitution Steward 委辦之 Layer 3 起草程序）
  archive-path: specs/IDENTITY-SPECIFICATION-v0.1-draft.md
```

### CS.1 逐原則論證本文（七節，順序固定）[N]

> **CS.1-PA（Prime Axiom）**〔滿足＋承接〕引 `AUGUR-MC v1.4 §1.1`。持續一致之 Identity 為 PA 之構成支柱；本規格以 identifier 永不刪除（ID.13）、lineage 不變式（ID.41）、跨部署可解析（ID.10）落實「持續一致之 Identity」，以 identity claim 之 Evidence 要件（ID.30(c)）落實「可追溯之 Evidence」。判準揭示：本規格未引入 PA 以外之評價性謂詞；「持續一致」以 lineage 可重建（ID.41 可判定判準）操作化。

> **CS.1-P1（Reality First）**〔細化〕引 `§P1.E1`、`§P1.E2`、`§P1.E3`。identifier 之跨部署可解析與對齊（ID.10）為 `§P1.E2` 之落地；外部識別碼降格為指涉資訊（ID.11）落實「資料來源不得成為最高抽象」（`§P1.E1`）。P1.E3（自然人 Bounded Representation）：身份屬性 as-of 繫結（§8）於自然人屬性之消費受法域義務約束——涉自然人表徵之域內宣告承接 `AUGUR-WM v1.0 §A.59`、`§WM.38`。**D17（自然人法規對應，目標 L3/L6）之分承**：其 **L3 slice**（自然人 identity 側去識別化／法規強制抹除機制、時變屬性 as-of 繫結）由本層 **ID.42** 及 §8（ID.60）承接；其 **L6 slice**（法規對應表本體與授權）DEFER Layer 6（IDO.7）。判準揭示：跨部署對齊可判定性依 ID.10；D17 之 L3 slice 於 ID.42 具具名落點，非整項下推。

> **CS.1-P2（Representation Before Intelligence）**〔承接〕引 `§P2.E1`、`§P2.W2`、`§P2.E5`。provisional 不得升級為 Knowledge（ID.50）落實候選斷言經 Evidence 通道方確立；採認前保守解釋為未解析（ID.21）落實權威順序；採認撤回之 fail-safe 重評估（ID.22）承接 `§P2.E5`。判準揭示：「已解析」以採認紀錄存在（ID.20）操作化。

> **CS.1-P3（Identity Before Knowledge）〔核心〕**〔承接＋細化〕引 `§P3.E1`、`§P3.E2`、`§P3.E3`、`§2.4`；**逐條見 Annex TR.A**（§P3 家族＋§2.4 為本層核心細化落點）。
> * `§P3.E1`（引用與解析義務）→ ID.50–ID.53、ID.11（mint-on-admission）、ID.51（可稽核指標，承接 `AUGUR-WM v1.0 §D4`）；
> * `§P3.E2`（Identity Lifecycle）→ ID.13（永不刪除）、ID.40–ID.43（merge/split/retire/relist/轉指全程 lineage、tombstone、去識別化），落實 **AUD-05**；
> * `§P3.E3`（同一性判準掛鉤）→ ID.20–ID.23（採認，承接 `AUGUR-ONT v1.0 §ONT.21`／DO.1）、ID.53（instance/type 標記存續，承接 `§ONT.30`）；
> * `§2.4`（identifier／identity claim 區分）→ ID.14、ID.30–ID.32（identity claim 一級介面），落實 **AUD-06**。
> 判準揭示：本節每一評價性用語（「已解析」「可追溯」「唯一權威」）均附可判定判準（ID.20／ID.41／ID.32）。

> **CS.1-P4（Evidence Before Conclusion）**〔承接＋DEFER〕引 `§P4.E1`、`§P4.E2`、`§P4.E3`、`§P4.E5`、`§P4.E6`、`§P4.E8`；**逐條見 Annex TR.B**（P4 家族）。identity claim 與 lifecycle 事件為需引用 Evidence 之 Knowledge（ID.30(c)、ID.40）；只失效不刪除（ID.22、ID.40）；衝突並存（ID.31）；身份屬性雙時間（ID.60，錨定 `§P4.E2`）。**DEFER**：Confidence 語義（IDO.1／`§P4.E8`）、Knowledge 五元組欄位（IDO.2／`§P4.E1`）、as-of 重建引擎（IDO.6／`§P4.E2`）下放 Layer 4。判準揭示：DEFER 掛鉤載明目標 Layer 與授權條款（Annex DO）。

> **CS.1-P5（Accountability Before Action）**〔不適用（附理由）〕引 `AUGUR-MC v1.4 §P5.E1`（Action 六元組與問責）、`§P5.E2`（風險分級）：本規格為概念層 Identity 規格，不定義 Action、授權鏈或風險分級（屬 Layer 6，逐條見 Annex TR.B P5 各列）。惟採認（ID.20）、lifecycle 事件（ID.40）、去識別化（ID.42）均為具作成者之可歸責治理行為，其歸責記錄與 P5 精神相容。判準揭示：本規格未定義任何 Action 六元組事項（`§P5.E1`）。

> **CS.1-EV-chain（§4 canonical chain）**〔承接〕引 `§4` EV.4（Identity）為本規格之標準鏈落點；引 `AUGUR-WM v1.0 §WM.24`（節選連續性）。本規格機制化 EV.4：Observation（EV.2）經 provisional（ID.50）解析取得 Identity（EV.4），方得繫結為 Evidence（EV.5）／Knowledge（EV.6）。判準揭示：節選不跳節點；provisional→resolved→Knowledge 之單向不可逆升級（ID.21、ID.50）。

### CS.2 已知緊張關係（`AUGUR-WM v1.0 §WM.42`）[N]

| T-id | 所涉條款 | 描述 | 緩解／狀態 |
|---|---|---|---|
| **T-ID-1** | ID.30(d)、IDO.1 | identity claim 需 Confidence 槽位，但其語義 DEFER Layer 4（`§P4.E8`）尚未定義。 | 本層僅設槽位並要求 Layer 4 承接；語義未定前，涉 claim 之升級消費採保守解釋（`§P4.E7` 最弱環節約束）。非豁免事項。 |
| **T-ID-2** | ID.12、IDO.5 | identifier 結構設計權（`§WM.20`／D5）與概念層獨立性（`§0.6(b)`）之張力：命名空間須有結構，然物理編碼屬 Layer 7。 | 本層僅定**概念命名空間**（referent 空間隔離＋跨部署對齊契約）；物理序列化下放 Layer 7（IDO.5）。非豁免事項。 |
| **T-ID-3** | AO.2、`§D6` | OPEN-1 Security 判準採認待 Steward／決策層拍板；本層提供採認機制但實質採認非本規格單方可為。 | 拍板前保守解釋為未解析（`§WM.21(e)`）；本規格備妥採認機制待拍板即生效。非豁免事項。 |
| **T-ID-4** | ID.60、ID.61、IDO.6 | 身份屬性 as-of 繫結義務（本層）與 as-of 重建引擎（Layer 4，`§P4.E2`）分屬二層，重建能力等級尚未定義。 | 本層保證版本繫結存在；重建能力 DEFER Layer 4（HOOK-01 上呈素材）。非豁免事項。 |
| **T-ID-5** | ID.31、IDO.2 | identity claim 為 Knowledge（`§2.4`）受 P4 約束，然其完整 Knowledge 五元組欄位設計屬 Layer 4。 | 本層定身份側四要件（ID.30），完整欄位下放 Layer 4；二者以 IDO.2 對接。非豁免事項。 |
| **T-ID-6** | ID.42、§8、IDO.7、`§D17` | 自然人法規對應（`AUGUR-WM v1.0 §D17`）目標為 **L3/L6**，其 L3 機制 slice（去識別化／抹除、時變屬性 as-of）與 L6 法規對應表本體之分界待具體法域義務落地方確定。 | L3 slice 由 ID.42（＋ID.60）承接、繫結 `AUGUR-ONT v1.0` T.23；L6 slice DEFER Layer 6（IDO.7）。分界待定但雙側均有具名落點，非承接漏列。非豁免事項。 |

豁免登記：`none`（waivers: []）。本規格無現行豁免；如有，依 `AUGUR-WM v1.0 §WM.33` 豁免狀態標記位置落實。

### CS.3 雙向 DEFER 承接表（`AUGUR-WM v1.0 §WM.43`）[N]

* **(a) 承接上層之掛鉤（defers-in）**：`AUGUR-WM v1.0 §D2`(採認側)→ID.20；`§D3`→§5／§6；`§D4`→ID.51；`§D5`→§3；`§D6`→Annex O；`§D17`(L3 slice)→ID.42、§8（L6 slice DEFER Layer 6，IDO.7）；`AUGUR-ONT v1.0 §DO.1`→§4／§7；`§DO.2`→§3／§5；`§DO.3`→§6（含 ID.44 DynamicEntity 終結）；`§DO.4`→§7／§8。與 front-matter `defers-in` 欄雙向對表。
* **(b) 下放下層之掛鉤（defers-out）**：IDO.1–IDO.8（見 Annex DO），與 front-matter `defers-out: [IDO.1, IDO.2, IDO.3, IDO.4, IDO.5, IDO.6, IDO.7, IDO.8]` 互為索引。

### CS.4 形式充分性（`AUGUR-WM v1.0 §WM.44`）[N]

依 `§WM.44` 判準自查：`AUGUR-MC v1.4` **全部** [N] 條款、`AUGUR-WM v1.0` **全部** [N] 條款、`AUGUR-ONT v1.0` **全部** [N] 條款，均須對應至本規格至少一 [N] 條款、或明記 DEFER 掛鉤、或明記「不觸及」及理由（P5 家族依 CS.1-P5 明記不適用）。**此自查之逐條完整枚舉見 Annex TR（TR.A–TR.D）**，本節為其總綱與「不觸及」主要條款群之理由歸納。明記「不觸及」之主要條款群及理由：

* `AUGUR-MC v1.4` P5 全組、§5 架構角色、§6 F5–F6：其規範對象為行動治理／架構角色／智慧輸出可解釋性，屬 Layer 4–6；本層僅型別化行動主體之 identifier，不代定機制。
* `AUGUR-WM v1.0` WM.24–29（canonical chain 承接於 CS.1-EV-chain；fail-safe／模態表達力屬 Layer 4–6）、WM.49–53（Domain Profile 框架，本層消費其產物而不制定）：本層 Identity 機制不使其不可表達（ID.13、ID.40、ID.41 為表達力承載）。
* `AUGUR-ONT v1.0` ONT.10–13、ONT.40–41、Annex T 之型別**定義**：屬 Layer 2 制定，本層僅**採認**（ID.20）與**機制化**（§3、§5、§6），不重述型別定義內容。ONT.40 世界關係之端點封印解除／派生解析由 ID.24 承接。

**明記對應／DEFER（非不觸及）之補正**：`AUGUR-WM v1.0 §WM.38`（自然人有界表徵）及其 Annex D 掛鉤 **D17**（自然人法規對應表，L3/L6）：其 **L3 slice** 對應至 ID.42（去識別化／法規強制抹除機制）＋§8（ID.60，時變屬性 as-of），其 **L6 slice** 明記 DEFER Layer 6（IDO.7）；故 WM.38/D17 於本自查為「對應＋DEFER」，非「不觸及」。`AUGUR-ONT v1.0 §DO.3` 之 T.3/T.4/T.5（DynamicEntity 終結生命週期）對應至 ID.44。

**逐條對應矩陣已完整枚舉、形式充分性已成就——Steward 充任認定業經作成，本規格自 2026-07-17 起生效**：`AUGUR-MC v1.4`／`AUGUR-WM v1.0`／`AUGUR-ONT v1.0` 全部 [N] 條款 → 本規格落點之**逐條完整枚舉**（`§WM.44` 要求之機器可判完備對應矩陣）**已於 Annex TR（TR.0、TR.A–TR.D、TR.Z）完整作成**：TR.A（`AUGUR-MC v1.4` §P3 家族＋§2.4，本層核心）、TR.B（`AUGUR-MC v1.4` PA／§1.2／§1.3／P1／P2／P4／P5 及 §0／§2／§4／§5／§6／§7／§8）、TR.C（`AUGUR-WM v1.0` WM.1–53＋Annex A A.0–A.59＋Annex D D0–D28）、TR.D（`AUGUR-ONT v1.0` ONT.1–62＋Annex T T.0–T.91），每一上層 [N] 條款均有落點列（承接／細化／DEFER／不觸及＋理由）。依 `§WM.44`「任一條款無對應且無明記者，聲明不完整」之反面，**逐條完整枚舉已成就、形式充分性已成就**。**殘餘之生效阻卻業已解消**——Steward 充任認定已作成（Steward 裁決第 2026-004 號、AL-2026-008；`AUGUR-MC v1.4 §0.5`、`§8.3`），本規格生效要件全部成就。**實質充分性**仍由違憲審查程序（`AUGUR-MC v1.4 §8.2`）判斷，未因充任而終局確認；本規格不自我宣告已生效，其生效係基於 Steward 之裁決行為（`§8.1`）。

---

## 附：章節目錄總覽 [I]

| 章 | 標題 | 條款 | 核心承接 |
|---|---|---|---|
| §0 | 文件地位與約定 | 0.1–0.5 | `MC §0` |
| §1 | 目的、範圍與分層界限 | ID.1–ID.2 | `ONT` Annex L3 |
| §2 | 承接與非管轄 | ID.3–ID.4 | `WM` Annex D、`ONT` Annex DO |
| §3 | Identifier 鑄造與結構 | ID.10–ID.14 | `WM.20`/D5、`ONT.DO.2`；AUD-04 |
| §4 | 判準採認 | ID.20–ID.24 | `WM.21(e)`/D2、`ONT.21`/DO.1、`ONT.40`（ID.24） |
| §5 | Identity Claim 一級介面 | ID.30–ID.32 | `WM.21(c)`/D3、`ONT.22`/DO.2；AUD-06 |
| §6 | Identity Lifecycle | ID.40–ID.44 | `WM.22`/D3、`ONT.DO.3`（含 T.3/T.4/T.5 終結，ID.44）；AUD-05 |
| §7 | Provisional Identity 解析 | ID.50–ID.53 | `WM.21(d)`/D4、`ONT.DO.4`；AUD-04 |
| §8 | 身份屬性 as-of 時間繫結 | ID.60–ID.61 | `P4.E2`、`ONT.DO.4`；AUD-07 |
| §9 | 與 Layer 4 分界 | ID.70–ID.71 | `P4.E1/E2/E7/E8` |
| §10 | 合規聲明格式承接 | ID.80–ID.81 | `WM.39–45` |
| Annex O | OPEN-1 承接（stock_id 代碼重用） | AO.1–AO.4 | `A.54`/D6、`ONT` T.90、T.20（AO.4） |
| Annex DO | 下放下層掛鉤 | IDO.0–IDO.8 | → Layer 4/6/7 |
| Annex L4 | 與 Layer 4 分界表 | L4.0 | 與 `ONT` L3 同構 |
| Annex TR | WM.44 逐條對應矩陣（憲章＋WM＋ONT → 本規格） | TR.0、TR.A–TR.D、TR.Z | `WM.44` |
| Annex CS | 憲章合規聲明 | CS.1–CS.4 | `WM.39–45` |

---

*本規格計：正文條款 ID.1–ID.81、Annex O（AO.1–AO.4）、Annex DO（IDO.0–IDO.8）、Annex L4（L4.0）、Annex TR（TR.0、TR.A–TR.D、TR.Z：WM.44 逐條對應矩陣，已就三上層全部 [N] 條款逐條完整枚舉）、Annex CS 合規聲明 [N]。全文以繁體中文為權威文本（§0.4）。本文件為 **v1.0 生效版本**，形式充分性（`§WM.44`）已成就，Steward 充任認定已作成，自 2026-07-17 起生效（Steward 裁決第 2026-004 號、AL-2026-008；`AUGUR-MC v1.4 §0.5`、【地位】、ID.80）；**實質**充分性之最終判斷仍屬 Steward `§8.2` 違憲審查程序。*

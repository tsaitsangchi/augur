# 《Augur Identity Specification》

Augur Enterprise AI Operating System
身份系統規格（Layer 3 — Identity System）
引用縮寫：**AUGUR-ID**｜版本：**v0.1-draft**（提案；前版：無）
受 **AUGUR-MC v1.3** 全文約束（`AUGUR-MC v1.3 §0.6(a)` lex superior、`§0.5` 對照表 Layer 3 欄）
並受 **AUGUR-WM v1.0** 全文約束（`AUGUR-MC v1.3 §0.6(a)`、`AUGUR-WM v1.0 §WM.1`）
並受 **AUGUR-ONT v0.1-draft**（Layer 2，草案）承接約束（`AUGUR-MC v1.3 §0.6(a)`）

---

> ## 【地位】[N]
>
> 本文件為 **AUGUR-ID v0.1-draft 提案版本**，**尚未生效**。依 `AUGUR-MC v1.3 §0.5`，任何後續規格必須先在 Layer 對照表登錄所屬 Layer 並經生效程序方生效力；`AUGUR-MC v1.3 §0.5` 對照表 Layer 3「Identity System」欄現登錄之所轄規格為「Identity Specification」，惟本規格經 Steward 依 `AUGUR-MC v1.3 §8.1`／`§8.3` 過渡規則充任認定前，**不生效力**。在充任認定作成前：
>
> * 本文件全部 [N] 條款**僅具提案地位**，不對 Layer 4–7 規格產生規範效力，不得被下層引為定義依據；
> * **形式充分性（`AUGUR-WM v1.0 §WM.44`）尚未成就**：`§WM.44` 要求 `AUGUR-MC v1.3`／`AUGUR-WM v1.0`／`AUGUR-ONT v0.1-draft` 全部 [N] 條款均對應至本規格至少一 [N] 條款、明記 DEFER 掛鉤、或明記「不觸及」及理由，且為機器可判之生效要件（「任一條款無對應且無明記者，聲明不完整，規格不生效力」）。本規格 Annex CS §CS.4 之**逐條對應矩陣尚未完整枚舉**，故形式充分性未成就；在該矩陣完備前，本規格**不生效力**，此與 Steward 充任認定未成就**併為生效阻卻**；
> * 本文件依 `AUGUR-MC v1.3 §8.3`、`AUGUR-WM v1.0 §WM.39` **必須內含**之 Constitutional Compliance Statement（Annex CS）以**正式格式**（`AUGUR-WM v1.0 §WM.39–45`，非暫行模板，`§WM.45`：本聲明作成於 Layer 1〔`AUGUR-WM v1.0`〕生效日 2026-07-16 之後）作成，其充分性之最終判斷屬 Steward 違憲審查與充任認定程序（`AUGUR-MC v1.3 §8.2`、`§8.3`）；
> * 引用 Layer 2 一律標注其草案地位（`AUGUR-ONT v0.1-draft`）；`AUGUR-ONT` 本身未經充任認定前，本規格對其之承接於 `AUGUR-ONT` 生效時同步生效；
> * 本文件之條款編號（ID.{n}、AO.{n}、IDO.{n}、CS.{n}、L4.{n}）於本 draft 已宣告穩定性（ID.81），生效後準用 `AUGUR-MC v1.3 §8.6`、`AUGUR-WM v1.0 §WM.46`：永不重用、永不重排。
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
* Annex CS [N] — 本規格之 Constitutional Compliance Statement（CS.1–CS.4）
* 附：章節目錄總覽 [I]

---

## §0 Document Status & Conventions（文件地位與約定）[N]

### 0.1 名稱、層級與版本 [N]

* 名稱：Augur Identity Specification（下層引用簡稱 **AUGUR-ID**）
* 層級：Layer 3 — Identity System（`AUGUR-MC v1.3 §0.5` 對照表第 3 列）
* 版本：v0.1-draft（前版：無）
* 上層規格（upper-specs）：`AUGUR-MC v1.3`（Layer 0）、`AUGUR-WM v1.0`（Layer 1）、`AUGUR-ONT v0.1-draft`（Layer 2，草案）
* 生效要件：`AUGUR-MC v1.3 §0.5` 對照表登錄（已具欄位）＋ Steward 充任認定（**未成就**，見【地位】）＋ 依 `AUGUR-WM v1.0 §WM.39` 之 Compliance Statement（Annex CS），並登錄 Amendment Log（`AUGUR-MC v1.3 §8.1`）。

### 0.2 規範用語約定 [N]

沿用 `AUGUR-MC v1.3 §0.2`：**必須**（MUST，絕對義務）／**不得**（MUST NOT，絕對禁止）／**應**（SHOULD，偏離須書面說明理由）／**得**（MAY，允許而不構成義務），全文一致，不重定義。

### 0.3 條文效力標注與編號穩定性 [N]

* 每章標題標注 **[N]（Normative，規範性）** 或 **[I]（Informative，資訊性）**。[N] 與 [I] 內容不一致時，依 `AUGUR-MC v1.3 §8.2` 以 Normative 為準。**章標題之標注為該章預設；凡子節另有標注者，以子節標注為該子節之效力準據**（如 §1[N] 下 §1.1[I] 為資訊性、§1.2[N] 為規範性）；此為標注層級之解讀規則，非上開內容衝突解消規則之適用範圍。
* **正文採十位制章段保留編號**：各章間之空號（如 ID.5–9、ID.15–19、ID.25–29、ID.45–49 等）為**保留區塊、非跳號**；保留號之啟用（如 ID.24、ID.44 於本版之啟用）亦適用永不重用、永不重排（`AUGUR-MC v1.3 §8.6`）。
* 正文條款編號採 **ID.{n}**；Annex 條款編號各自前綴：Annex O（OPEN 承接）採 **AO.{n}**、Annex DO（下放下層掛鉤）採 **IDO.{n}**、Annex CS（合規聲明）採 **CS.{n}**、Annex L4（與 Layer 4 分界）以其所引 ID／IDO 編號為索引，另立表首治理條款 **L4.{n}** 於必要時使用。
* 條款編號一經發布**永不重用、永不重排**；廢止條款保留編號並標注 **(repealed)**（`AUGUR-MC v1.3 §8.6`、`AUGUR-WM v1.0 §WM.46`）。

### 0.4 權威語言聲明 [N]

本規格以**繁體中文版為權威版本**；規範性術語於正文中一律使用英文原詞（Reality、Observation、Representation、Identity、Evidence、Knowledge、Confidence、Action、Agent；及本層機制術語 identifier、identity claim、mint、adopt、merge、split、retire、relist、redirect、tombstone、de-identify、lineage、provisional、resolution、as-of），與 `AUGUR-MC v1.3 §0.4`、`AUGUR-WM v1.0 §0.4`、`AUGUR-ONT v0.1-draft §0.4` 保持術語同一性；不另立中文譯名為規範對象。

### 0.5 引用格式與元規則 [N]

* 引用格式：`AUGUR-MC v1.3 §{條款}`／`AUGUR-WM v1.0 §{條款}`／`AUGUR-ONT v0.1-draft §{條款}`（Layer 2 現為 v0.1-draft，引用時註明其草案地位）。下層引用本規格採 `AUGUR-ID v{version} §{條款}`。
* 本規格每一 [N] 條款標注其**憲章／上層錨定**與**三態型態**：**refines**（細化上位條款）／**carries**（承接上位不變式並給予個體層機制位置）／**hooks**（DEFER 掛鉤，載明目標 Layer 與授權條款），與 `AUGUR-WM v1.0 §0.5`、`AUGUR-ONT v0.1-draft §0.5` 三態明文對映一致；複合模式以「＋」連接。每一 [N] 條款並標注**義務主體**與**可判定判準**，使其可機器稽核（承接 `AUGUR-WM v1.0 §WM.34`）。
* **不重定義元規則**：本規格**不得**重新定義 `AUGUR-MC v1.3 §2` 之術語（尤其 `§2.4` Identity＝identifier／identity claim 之區分），亦**不得**重定義 `AUGUR-WM v1.0`／`AUGUR-ONT v0.1-draft` 之既有構件；本規格僅得就其明示下放者作**機制化**（`AUGUR-MC v1.3 §2` 元規則、`AUGUR-WM v1.0 §WM.2`、`AUGUR-ONT v0.1-draft §ONT.2`）。
* **概念層獨立性**（`AUGUR-MC v1.3 §0.6(b)`）：本規格屬概念層（Layer 3），**不得**引用 Layer 5–7 執行層構件（資料庫、Agent Runtime、API、儲存引擎、序列化格式）作為任何定義之依據。本規格所稱「機制」為**概念機制**（不變式、狀態、關係、事件語義），其執行層落實一律下放（Annex DO）。

---

## §1 Purpose, Scope & Layer Boundary（目的、範圍與分層界限）[N]

### 1.1 Layer 3 定位 [I]

`AUGUR-WM v1.0` 宣告**世界有何物**（存在層，existence layer）；`AUGUR-ONT v0.1-draft` 宣告**其類屬與同一性判準之內容**（型別層，type layer，制定 formulate）。**AUGUR-ID 負責「個體的永久參照與其一生的機器機制」**（個體層，instance/identifier layer）——即 identifier 之**鑄造（mint）**、同一性判準之**採認（adopt）使生效於 resolution**、identity **lifecycle**（merge／split／retire／relist／轉指 redirect、tombstone、去識別化 de-identify、lineage）、**identity claim 一級介面**、**provisional identity 解析**、**身份屬性 as-of 時間繫結**。本規格承接 `AUGUR-ONT v0.1-draft` Annex L3「Layer 3 專屬」欄與 `AUGUR-WM v1.0` Annex D 目標含 Layer 3 之掛鉤。

### 1.2 條款 [N]

> **ID.1（三層不僭越）[N｜carries｜`AUGUR-ONT v0.1-draft` Annex L3、`§ONT.3`、`§ONT.7`；`AUGUR-WM v1.0 §WM.3`、`§WM.23`]**
> 存在層宣告「有何物」、型別層產出「類型與判準的定義文本」、本層產出「個體的永久參照與其一生的機器機制」。本規格**不得**新宣告世界實體之存在（屬 Layer 1）、**不得**改寫或新制同一性判準之**內容**（屬 Layer 2 制定）；本層僅**採認**判準使其生效於 resolution、**鑄造** identifier、**運轉** lifecycle。
> **義務主體**：本規格自身、本規格後續修訂者。**可判定判準**：本規格任一條款若對某世界概念作存在宣告、或陳述某 Type 之判準**內容文句**（而非引用 Layer 2 既制定之判準），即為上侵，違反本條。

> **ID.2（下界封印）[N｜carries｜`AUGUR-MC v1.3 §P4.E1`、`§P4.E8`、`§P4.E2`、`§P4.E7`]**
> 下列事項屬 Layer 4，本規格**僅得**設下放掛鉤（Annex DO），**不得**代行定義：(a) **Confidence 語義**（單一形式化定義、可比較性、傳播規則，`AUGUR-MC v1.3 §P4.E8`）；(b) **Knowledge 五元組之欄位設計**（Source／Timestamp／Identity／Evidence／Confidence 之結構落地，`§P4.E1`）；(c) **as-of 重建引擎與能力等級**（`§P4.E2`）；(d) **來源信任分級表**（`§P4.E7`）。本規格得**引用**上開概念槽並規定其於 identity 構件中之**存在位置**，但其語義填充下放 Layer 4。
> **義務主體**：本規格自身。**可判定判準**：本規格任一條款若對 (a)–(d) 作成可被 Layer 4 直接消費而無須另為定義之實質定義，違反本條（下侵）。

---

## §2 承接與非管轄（Defers-In & Non-Encroachment）[N]

### 2.1 承接上層掛鉤（defers-in）[N]

> **ID.3（承接盤點）[N｜carries｜`AUGUR-WM v1.0` Annex D D0；`AUGUR-ONT v0.1-draft` Annex DO DO.0]**
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
> | `AUGUR-ONT v0.1-draft §DO.1` | 判準採認、resolution 演算／時限指標 | §4、§7 |
> | `AUGUR-ONT v0.1-draft §DO.2` | identity claim 一級表介面、identifier 鑄造／結構／命名空間 | §3、§5 |
> | `AUGUR-ONT v0.1-draft §DO.3` | lifecycle 事件表、merge／split／retire／relist、tombstone、去識別化、lineage | §6 |
> | `AUGUR-ONT v0.1-draft §DO.4` | 標記存續／解析、provisional 解析、身份屬性 as-of 版本化 | §7、§8 |
>
> **義務主體**：本規格自身。**可判定判準**：上表每列於正文有對應 ID 條款、且於 Annex CS `defers-in` 表雙向可解析者為合規；任一列無對應正文條款者，承接不完整。

### 2.2 非管轄聲明 [N]

> **ID.4（不擴張管轄）[N｜carries｜`AUGUR-MC v1.3 §0.6(a)`、`§0.5`；`AUGUR-WM v1.0 §WM.3`；`AUGUR-ONT v0.1-draft §ONT.3`]**
> 本規格為 Layer 3 唯一所轄規格，不自行擴張管轄；凡 `AUGUR-MC v1.3` 明定定義權屬 Layer 1／Layer 2／Layer 4–7 之事項，本規格**不得**代行定義。
> **義務主體**：本規格自身。**可判定判準**：本規格任一條款之定義對象逾越 `AUGUR-MC v1.3 §0.5` 所定 Layer 3 職掌者，違反本條。

---

## §3 Identifier 鑄造與結構（Minting & Structure）[N]

> 本章行使 `AUGUR-WM v1.0 §D5`（承 `§WM.20`）與 `AUGUR-ONT v0.1-draft §DO.2` 下放之 identifier 設計權。承接審計 **AUD-04**（無系統鑄造之 Identity 層）。

### 3.1 §WM.20 授權範圍之明示 [N]

> **ID.10（授權範圍與語義義務保留）[N｜refines｜`AUGUR-WM v1.0 §WM.20`；`AUGUR-MC v1.3 §P1.E2`、`§P3.E2`]**
> `AUGUR-WM v1.0 §WM.20` **不課** identifier 任何編碼或命名空間結構義務，並將 identifier 之**鑄造、結構與命名空間**明文授予 Layer 3；Layer 1 僅保留一項**語義義務**：identifier **必須可跨部署邊界解析與對齊**（`AUGUR-MC v1.3 §P1.E2`）。本規格據此行使設計權，惟其行使**必須**滿足並**不得**削弱該語義義務。凡本規格所定命名空間或結構，**必須**使「同一世界個體於任何部署之 identifier 可被解析為同一」為可判定；**不得**以任何結構設計使跨部署對齊變為不可判定。
> **義務主體**：本規格自身、Layer 4–7 之實作構件。**可判定判準**：本規格所定之任一命名空間，其 identifier 之跨部署對齊規則已明文且可機械判定者為合規；未明文或使對齊不可判定者違反本條。

### 3.2 鑄造義務（mint-on-admission，落實 AUD-04）[N]

> **ID.11（系統鑄造義務）[N｜carries｜`AUGUR-MC v1.3 §P3.E2`、`§P3.E1`；`AUGUR-WM v1.0 §WM.19`、`§WM.22`；`AUGUR-ONT v0.1-draft §ONT.22`]**
> 凡 `AUGUR-WM v1.0` 存在宣告、`AUGUR-ONT v0.1-draft` Annex T 型別化之世界個體，於**首次意圖進入 Reasoning／Planning 或升級為 Knowledge 之前**，系統**必須**為其鑄造一枚**系統 identifier**（`AUGUR-MC v1.3 §2.4`：系統鑄造之永久參照，本身為系統內具 Identity 地位之一級物件）。外部來源識別碼（供應商證券代碼、series_id、ISIN、統一編號）為 Identity 之**指涉資訊**，**不得**逕充系統 identifier（承接 `AUGUR-ONT v0.1-draft §ONT.22`、`AUGUR-WM v1.0 §WM.20`；**AUD-04**）。
> **「未鑄造故無附著對象」抗辯之排除**（承接審計驗證裁註，AUD-05）：identifier 之鑄造義務為前提義務，**不得**以「lifecycle／lineage 尚無 identifier 可附著」為由免除；系統**必須**先鑄造，方使 lifecycle 有附著對象。
> **義務主體**：Layer 4–7 之表徵與攝取構件、本規格（表達力保證）。**可判定判準**：任一升級為 Knowledge 之世界個體參照可解析至恰一系統 identifier 者為合規；以外部識別碼裸字串直充身份者違反本條。

### 3.3 命名空間結構（概念層）[N]

> **ID.12（型別化命名空間隔離）[N｜refines｜`AUGUR-ONT v0.1-draft §ONT.31`、`§ONT.2`；`AUGUR-WM v1.0 §WM.20`]**
> 系統 identifier **必須**繫結恰一 Type 之個體命名空間（`AUGUR-ONT v0.1-draft §ONT.31` 之概念層隔離）；不同頂層範疇與不同 Type 之個體命名空間**必須**互斥。**禁止型態**（承接 **AUD-04**）：(i) 將產業分類名（type 節點）或指數代號混入 Security 個股命名空間；(ii) 將 EconomicIndicator／MacroDimensionQuantity（series_id 空間）與 Security（stock_id 空間）視為同一命名空間。命名空間之**指稱結構**（例如以〔範疇︰Type︰個體序〕之概念三元組標記）由本規格定其**概念形式**；其**物理序列化與儲存編碼** DEFER Layer 7（`AUGUR-MC v1.3 §0.6(b)`，Annex DO IDO.5）。
> **義務主體**：本規格自身、Layer 4–7 消費者。**可判定判準**：任一系統 identifier 可解析至恰一 Type 之個體命名空間者為合規；同一 identifier 解析至二個以上 Type、或 type 節點被當 Instance 鑄造者違反本條。

### 3.4 identifier 永不刪除 [N]

> **ID.13（永久性不變式）[N｜carries｜`AUGUR-MC v1.3 §P3.E2`；`AUGUR-WM v1.0 §WM.22`]**
> identifier 一經鑄造**永不刪除**；其後續指向變更（轉指 redirect）**必須**全程可追溯（§6）。identifier 存續**跨越任何 Ontology／Representation 變更**（`AUGUR-WM v1.0 §WM.22`）。
> **義務主體**：本規格、Layer 4–7 構件。**可判定判準**：存在任一使 identifier 記錄消滅之操作路徑者違反本條（法規抹除之留痕例外依 ID.42）。

> **ID.14（identifier 之 Identity 地位）[N｜carries｜`AUGUR-MC v1.3 §2.4`]**
> identifier 本身為系統內具 Identity 地位之一級物件；關於 identifier 之斷言（如轉指、退役）本身為受 P4 約束之 Knowledge（§6）。
> **義務主體**：本規格。**可判定判準**：關於 identifier 之 lifecycle 事件是否具備 Evidence 引用（依 ID.40）可機械檢查者為合規。

---

## §4 判準採認（Criterion Adoption）[N]

> 本章接續 `AUGUR-WM v1.0 §WM.21(e)` 效力封印與 `AUGUR-ONT v0.1-draft §ONT.21` 之封印，行使 `§D2`（採認側）／`§DO.1` 下放之**採認**權。

### 4.1 採認之定義性效果 [N]

> **ID.20（採認行為）[N｜carries＋refines｜`AUGUR-MC v1.3 §P3.E3`；`AUGUR-WM v1.0 §WM.21(e)`、`§D2`；`AUGUR-ONT v0.1-draft §ONT.20`、`§ONT.21`、`§DO.1`]**
> Layer 2 已為每一 Type **制定**（formulate）其 Identity Criterion（`AUGUR-ONT v0.1-draft §ONT.20`），惟其**用於 resolution 之操作效力**須經本層**採認**（adopt）方生效（`§ONT.21`）。採認為一**具名、附 Evidence、可追溯之治理行為**，其效果為：使被採認之判準對指定 Type 生效於 identity resolution，自採認生效時起，涉該 Type 之 Identity 引用**得**被判定為已解析。採認**不得**改寫判準內容（改寫屬 Layer 2 制定，違者上侵，違 ID.1）。
> **義務主體**：本規格自身、採認之作成者。**可判定判準**：每一採認紀錄具備〔目標 Type、被採認判準之 Layer 2 條款引用、生效時點、Evidence 引用、作成者〕五要素者為合規；缺任一要素之採認不生效力。

### 4.2 採認前之保守解釋 [N]

> **ID.21（未採認即未解析）[N｜carries｜`AUGUR-WM v1.0 §WM.21(d)(e)`、`§WM.33`；`AUGUR-ONT v0.1-draft §ONT.21`；`AUGUR-MC v1.3 §P3.E1`]**
> 於某 Type 之判準經本層採認前，涉該 Type 之 Identity 引用一律採保守解釋，**視為未解析**（provisional）；未解析之 Observation **不得**升級為 Knowledge（`AUGUR-MC v1.3 §P3.E1`）。
> **義務主體**：Layer 3–7 消費者。**可判定判準**：存在採認紀錄前，將涉該 Type 之引用視為已解析而升級為 Knowledge 者違反本條。

### 4.3 採認之修訂與撤回 [N]

> **ID.22（採認之可謬性）[N｜carries｜`AUGUR-MC v1.3 §P4.E3`、`§P4.E4`、`§P2.E5`]**
> 採認本身為可被新 Evidence 推翻之 Knowledge（`§P4.E4`）；採認之撤回或修訂**不得刪除**原採認紀錄，僅得標記 superseded／retracted（`§P4.E3`），全歷史保留。採認撤回時，受其影響之既有 resolution 結果**必須**依 `AUGUR-MC v1.3 §P2.E5` fail-safe 重新評估（受影響範圍界定 DEFER Layer 4–6，`AUGUR-WM v1.0 §D15`）。
> **義務主體**：本規格、採認之修訂者。**可判定判準**：採認鏈之任一版本可經 transaction-time 重建者為合規；靜默刪除原採認紀錄者違反本條。

> **ID.23（resolution 演算與時限指標之下放）[N｜hooks｜`AUGUR-WM v1.0 §D4`；`AUGUR-ONT v0.1-draft §DO.1`；目標本層 §7 ＋ Layer 4 實作]**
> 判準採認後之 **resolution 演算之具體實作**（相似度、比對、批次流程）與**未解析存量之量測落地** DEFER Layer 4（Annex DO IDO.4）；本規格於 §7 定其**概念指標與義務**，不定實作。
> **義務主體**：本規格、Layer 4。**可判定判準**：§7 指標存在且可機械盤點者為合規。

### 4.4 世界關係之 Identity Resolution 承接 [N]

> **ID.24（世界關係之身份解析）[N｜carries｜`AUGUR-ONT v0.1-draft §ONT.40`、T.50、T.51；`AUGUR-WM v1.0 §WM.21(e)`]**
> 世界關係（`AUGUR-ONT v0.1-draft §ONT.40`：IssuanceRelation T.50、UnderlyingRelation T.51 等，其判準為〔關係型別 × 端點 Identity 有序組 × valid time〕）之個體為 **Instance**。其 Identity **依端點 Identity 已解析 ＋ 關係型別 ＋ valid time 派生**；`§ONT.40` 所定端點 Identity 之效力封印（同 `§ONT.21`），於各端點 Type 之判準經本層採認（ID.20）時解除，關係之判準採認**準用** ID.20。關係實例當升級為 Knowledge 時依 ID.11 鑄造系統 identifier、依 ID.12 繫結其**關係型別之個體命名空間**（與端點命名空間互斥）；其權威指稱得以端點有序組解析，**不得**以裸字串推定關係同一。
> **義務主體**：本規格、Layer 4–7 消費者。**可判定判準**：任一世界關係實例可解析至〔關係型別 × 端點 Identity 有序組 × valid time〕且端點 Identity 均已解析者為合規；端點未解析而逕認關係同一、或以裸字串 join 推定關係者違反本條。

---

## §5 Identity Claim 一級介面（First-Class Interface）[N]

> 本章行使 `AUGUR-WM v1.0 §WM.21(c)`、`§D3` 與 `AUGUR-ONT v0.1-draft §ONT.22`、`§DO.2` 下放之 identity claim 表介面權。承接審計 **AUD-06**（跨來源零繫結）。

### 5.1 identity claim 之結構 [N]

> **ID.30（一級介面四要件）[N｜carries｜`AUGUR-MC v1.3 §2.4`；`AUGUR-WM v1.0 §WM.21(c)`；`AUGUR-ONT v0.1-draft §ONT.22`]**
> identity claim（`AUGUR-MC v1.3 §2.4`：「兩個 identifier 指涉同一實體」之斷言，繫結於其所涉 identifier，本身為**受 P4 約束之 Knowledge**）為系統內一級物件。其結構**必須**含下列**身份側四要件**：
> * **(a) identifier 對**：所斷言同一之**二系統 identifier**（`AUGUR-MC v1.3 §2.4`「兩個 identifier」、`AUGUR-WM v1.0 §WM.21(c)`「identifier 對」）。外部識別碼為指涉資訊、**非** identifier（`§ONT.22`、ID.11），**不得逕充 claim 端點**；外部識別碼所指涉之世界個體須先依 ID.11 鑄造系統 identifier，以**該系統 identifier**為 claim 端點，外部識別碼本身僅以**指涉資訊／provisional alias** 地位供 resolution 使用（AO.3），不逕為端點；
> * **(b) 判準引用**：本斷言所據之 Identity Criterion（Layer 2 制定、經本層採認之條款引用，`§ONT.20`／ID.20）；
> * **(c) Evidence**：支持本斷言之 Evidence 引用（`AUGUR-MC v1.3 §P4.E6` 一級物件，遞迴可溯源）；
> * **(d) Confidence 槽位**：本斷言為真之程度之槽位。**Confidence 之語義（形式化定義、可比較性、傳播）本身 DEFER Layer 4**（`§P4.E8`，Annex DO IDO.1）；本層僅要求槽位存在並可被 Layer 4 填充。
> **禁止**（承接 **AUD-04／AUD-06**）：**不得**以欄位字面相等（裸字串 join、消費端 regex）推定跨體系同一（`AUGUR-WM v1.0 §A.33`、`§WM.21(c)`）。
> **義務主體**：本規格自身、Layer 4–7 消費者。**可判定判準**：任一跨體系同一性斷言具備 (a)–(d) 四要件、且 (d) 之語義以 Layer 4 承接標記者為合規；以字面相等替代 claim 者違反本條。

### 5.2 claim 之 Knowledge 地位 [N]

> **ID.31（claim 為 Knowledge，欄位設計下放）[N｜carries｜`AUGUR-MC v1.3 §2.4`、`§P4.E1`、`§P4.E5`]**
> identity claim 為 Knowledge，除身份側四要件（ID.30）外，其**完整 Knowledge 五元組欄位設計**（Source／Timestamp／Identity／Evidence／Confidence 之結構落地）DEFER Layer 4（`§P4.E1`，Annex DO IDO.2）。互相衝突之 claim（如二來源對同一 identifier 對作出相反同一性斷言）**必須**共存並顯式標記，**不得** last-write-wins（`§P4.E5`）。
> **義務主體**：本規格（表達力保證）、Layer 4（欄位設計）。**可判定判準**：世界模型能容納二相反 claim 並存者為合規；靜默消滅其一者違反本條。

### 5.3 唯一權威表徵之落點 [N]

> **ID.32（唯一權威表徵之結構前提）[N｜carries＋hooks｜`AUGUR-MC v1.3 §P1.E2`；`AUGUR-WM v1.0 §WM.10`、`§WM.14`、`§WM.15`、`§WM.37`；hooks 目標 Layer 4（`§WM.37`），Annex DO IDO.8]**
> 當二來源之 identifier 經 claim 斷言指涉同一世界實體／世界量時，本層之義務**限於提供 claim 繫結所需之結構前提**：使該 identifier 對可解析至**恰一權威表徵之錨點**（`AUGUR-WM v1.0 §WM.14` 權威地位唯一，不指儲存份數），並以 claim 承載「世界事實→來源 Observation」一對多映射與衝突保存（落實 **AUD-06**）。**唯一權威 Representation 之實際指定與落點屬 Representation 層（Layer 4），本層不代行**：其指定 carries `§WM.14`、DEFER Layer 4（`§WM.37` 唯一權威表徵落點；IDO.8），本層僅保證「可被指定」之結構條件存在，不自為 Representation 權威指定（此非 Layer 3 identifier 職掌，避免下侵 Annex L4）。世界量同一性以 Domain Profile／Registry 明文宣告為準（`§WM.15`：無宣告即非同一）。
> **義務主體**：本規格（結構前提）、Layer 4（權威表徵之實際指定）。**可判定判準**：經 claim 繫結之 identifier 對可解析至恰一權威表徵之錨點者為合規；本層對權威 Representation 作可被 Layer 4 直接消費之實際指定（而非僅結構前提）者，反為下侵、違 ID.2／ID.70。

---

## §6 Identity Lifecycle（生命週期機制）[N]

> 本章行使 `AUGUR-WM v1.0 §WM.22`、`§D3` 與 `AUGUR-ONT v0.1-draft §DO.3` 下放之 lifecycle 機制權。落實 `AUGUR-MC v1.3 §P3.E2`、承接審計 **AUD-05**（lifecycle 缺席致 stock_id 重用縫合）。

### 6.1 lifecycle 事件為 Knowledge [N]

> **ID.40（生命週期事件之 Evidence 義務）[N｜carries｜`AUGUR-MC v1.3 §P3.E2`、`§P4.E2`、`§P4.E3`；`AUGUR-WM v1.0 §WM.22`；`AUGUR-ONT v0.1-draft §DO.3`]**
> Identity 之 **merge／split／retire／relist 與更正**，本身為**必須引用 Evidence 之 Knowledge**（`AUGUR-MC v1.3 §P3.E2`）。系統**必須**維持一**概念 lifecycle 事件序**，每一事件載：〔事件型別 ∈ {mint, merge, split, retire, relist, redirect（轉指）, correct, tombstone, de-identify, expire（到期失效）, settle（結算消滅）, convert（轉換）, redeem（贖回）}、所涉 identifier、生效時點（valid time）、系統可知時點（transaction time，`§P4.E2`）、Evidence 引用、作成者〕。**本枚舉為開放集**：Layer 2 已宣告具生命週期屬性之 Type（如 DerivativeContract T.3、ConvertibleBond T.4、Warrant T.5，見 ID.44）之終結事件型別得依其型別語義擴充；未列名之終結型別於 DynamicEntity 語境準用其對應終結事件。事件**只失效不刪除**（`§P4.E3`）。
> 事件序之**欄位／索引物理實作** DEFER Layer 4／Layer 7（Annex DO IDO.3；`AUGUR-MC v1.3 §0.6(b)`）。
> **義務主體**：本規格（事件語義）、Layer 4（實作）。**可判定判準**：任一 merge／split／retire／relist／redirect 事件缺 Evidence 引用者違反本條。

### 6.2 轉指與 lineage 不變式 [N]

> **ID.41（轉指全程可追溯不變式）[N｜carries｜`AUGUR-MC v1.3 §P3.E2`；`AUGUR-WM v1.0 §WM.22`]**
> identifier 之後續指向變更（合併後之轉指 redirect）**必須全程可追溯**（不變式）；**identity lineage 全程保留**。給定任一 identifier 與任一 as-of 時點，「該時點此 identifier 指向哪一存續個體」**必須**可重建。merge 產生一指向合併目標之 redirect（來源 identifier 依 ID.13 存續、不刪除）；split 於分裂邊界後，同一來源指涉**必須**解析為不同存續個體（見 ID.43）。
> **義務主體**：本規格、Layer 4。**可判定判準**：存在任一使 lineage 斷鏈（無法重建某 as-of 指向）之操作者違反本條。

### 6.3 tombstone 與去識別化 [N]

> **ID.42（法規強制抹除之留痕與去識別化）[N｜carries｜`AUGUR-MC v1.3 §P3.E2`（法規抹除準用 `§P4.E3`）；`AUGUR-WM v1.0 §WM.38`、`§D17`（L3 slice）；`AUGUR-ONT v0.1-draft` T.23]**
> 法規強制抹除**準用** `AUGUR-MC v1.3 §P4.E3` 例外：**得**移除 identifier 所繫結之可識別內容並**去識別化**，惟：(a) identifier 本身以**留痕形式（tombstone）存續**；(b) 抹除事件具**完整 provenance**（作成者、法源依據引用、生效時點）；(c) **identity lineage 保留**。tombstone **不得**用以規避 ID.13 永不刪除（tombstone 為存續之特例，非刪除）。
> **D17 之 Layer 3 slice 承接**：涉自然人 Type（`AUGUR-ONT v0.1-draft` T.23 HumanDecisionMaker 等）之身份 identity 側去識別化／可識別內容抹除機制，為 `AUGUR-WM v1.0 §D17`（`§WM.38` 有界表徵）目標 L3 之機制載體，由本條承接（時變屬性之 as-of 繫結另見 §8 ID.60）。**具體法規對應表本體與其授權（L6 slice）DEFER Layer 6**（Annex DO IDO.7；`AUGUR-MC v1.3 §P1.E3`、`§WM.38`、`§D17`）；本條不代定法規對應內容。
> **義務主體**：本規格、Layer 4–7 執行構件。**可判定判準**：去識別化後仍存在 identifier tombstone、抹除事件具 provenance、lineage 可重建者為合規；三者缺一者違反本條。

### 6.4 代碼重用／退市／改名（落實 AUD-05）[N]

> **ID.43（存續邊界截斷）[N｜carries｜`AUGUR-WM v1.0 §WM.22`、`§A.25`；`AUGUR-ONT v0.1-draft` T.1、T.34]**
> 下市（`AUGUR-ONT v0.1-draft` T.34 Delisting，parent Event）為 Security lifecycle **retire** 事件之 Evidence 來源（`§A.25`：下市改變來源可見性、不改變歷史真實性）。外部代碼被回收重用時（同一外部代碼於 retire 事件後再現於名冊），系統**必須**將其解析為**不同存續個體**（split／新鑄造 identifier），使前一個體之歷史**不得**縫合入後一個體之表徵。改名／合併同樣以 lifecycle 事件表徵，**不得**靜默覆寫。
> **代碼重用偵測為可機械化紅旗**：同一外部代碼於 retire 事件後再現於名冊者，**必須**登錄為待解析事件（provisional，§7），不得逕行縫合。
> **義務主體**：本規格、Layer 4 特徵／標籤構造構件。**可判定判準**：跨 retire/relist 邊界之同一外部代碼被解析為同一存續個體、致歷史縫合者違反本條（其上位判準依 `AUGUR-ONT v0.1-draft` T.1 制定，本層引用而不複述其判準文句）。

### 6.5 DynamicEntity 非下市之終結 lifecycle（承接 DO.3 之 T.3／T.4／T.5）[N]

> **ID.44（具生命週期實體之終結表徵）[N｜carries｜`AUGUR-MC v1.3 §P3.E2`；`AUGUR-WM v1.0 §WM.22`；`AUGUR-ONT v0.1-draft §DO.3`、T.3、T.4、T.5]**
> Layer 2 已宣告具生命週期屬性之 DynamicEntity（`AUGUR-ONT v0.1-draft` T.3 DerivativeContract 之上市→交易→**結算消滅**、T.5 Warrant 之**到期失效**、T.4 ConvertibleBond 之**轉換／贖回**）之終結，其型別語義**非**「下市 retire」；本層承接 `§DO.3` 就此類終結之機制：終結**必須**以 lifecycle 事件（settle／expire／convert／redeem，ID.40）表徵，其 identifier 依 ID.13 **永不刪除**、identity lineage 全程保留，**終結後不得靜默消滅其歷史**。ConvertibleBond 轉換至標的股（UnderlyingRelation T.51）**必須**以事件＋lineage 表徵，**不得**以覆寫承載。
> **義務主體**：本規格（事件語義）、Layer 4（實作）。**可判定判準**：任一 DynamicEntity 之結算消滅／到期失效／轉換／贖回缺對應 lifecycle 事件與 Evidence 引用（ID.40）、或終結致其 identifier 記錄消滅／lineage 斷鏈者違反本條。

---

## §7 Provisional Identity 解析（Resolution）[N]

> 本章行使 `AUGUR-WM v1.0 §WM.21(d)`、`§WM.35`、`§D4` 與 `AUGUR-ONT v0.1-draft §DO.4`（provisional 側）下放之解析義務與稽核指標權。落實 `AUGUR-MC v1.3 §P3.E1`。

### 7.1 解析義務 [N]

> **ID.50（解析義務與升級禁止）[N｜carries｜`AUGUR-MC v1.3 §P3.E1`；`AUGUR-WM v1.0 §WM.21(d)`]**
> 未解析之 Observation **得**進入系統、**不得**升級為 Knowledge；系統**負解析義務**（`AUGUR-MC v1.3 §P3.E1`）。凡意圖進入 Reasoning／Planning 之結構化物件（無論 Goal／Constraint／Capability／Plan 於 Layer 5–6 如何定義）均落入**已解析 Identity 引用義務**（`§WM.21(d)` 兜底）。
> **「已解析」之本層自足定義**：於本層，某 Identity 引用為**已解析** iff〔涉該 Type 之判準採認已生效（ID.20）**∧** 該引用之 provisional 狀態旗標已依 ID.51(a) 清除〕；此為「解析成功」於 Layer 3 之機器可判定代理。resolution 演算本身（相似度／比對）仍 DEFER Layer 4（ID.23、IDO.4），其成敗於個體層落地由 Layer 4 承接。
> **義務主體**：Layer 3–7 消費者。**可判定判準**：任一升級為 Knowledge 之元素其 Identity 為已解析（採認已生效〔ID.20〕∧ provisional 狀態已清除〔ID.51(a)〕）者為合規；provisional 元素被升級者違反本條。

### 7.2 可稽核指標 [N]

> **ID.51（未解析存量之可稽核指標）[N｜hooks｜`AUGUR-WM v1.0 §D4`；`AUGUR-ONT v0.1-draft §DO.1`；目標本層定義＋Layer 4 量測]**
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

> **ID.53（instance/type 標記之存續與解析）[N｜carries｜`AUGUR-ONT v0.1-draft §ONT.30`、`§DO.4`；`AUGUR-WM v1.0 §WM.21(b)`、`§WM.33`]**
> Layer 2 定義之 instance／type 繫結標記語義（`§ONT.30`），其**存續與解析落實**由本層承接：任一 Knowledge 元素之繫結對象**必須**攜帶可解析之 instance 或 type 標記，且該標記隨轉引存續。
> **義務主體**：本規格、Layer 3–7 消費者。**可判定判準**：繫結對象未攜帶或不可解析 instance／type 標記者違反本條。

---

## §8 身份屬性 as-of 時間繫結（Attribute Time-Binding）[N]

> 本章承接 `AUGUR-ONT v0.1-draft §DO.4`（身份屬性 as-of 版本化）。落實審計 **AUD-07**（身份屬性無時間繫結）。**法源收斂**：本章之核心錨定為 `AUGUR-MC v1.3 §P4.E2`（雙時間性）於身份屬性之界面（承審計驗證裁註：AUD-07 法源收斂為 P4.E2 單軸，P3.E3 為誤引）；本章不引 `§P3.E3` 為義務錨。

### 8.1 身份屬性為時變、須 as-of 繫結 [N]

> **ID.60（身份屬性 as-of 繫結義務）[N｜carries｜`AUGUR-MC v1.3 §P4.E2`；`AUGUR-ONT v0.1-draft §DO.4`、T.24、T.42]**
> Identity 之時變屬性（如產業分類、名稱、市場類別、股權分級）**必須**繫結 valid time 與 transaction time（`§P4.E2`）；其消費**必須 as-of**——以「今日的」屬性判定歷史狀態（如以今日 industry_category 判定歷史宇宙准入）為**禁止型態**（承接 **AUD-07**；`AUGUR-ONT v0.1-draft` T.24 明示之禁止型態）。任一過去時刻「系統當時認為此 Identity 之屬性為何」**必須**可重建。
> **義務主體**：本規格（繫結義務）、Layer 4 消費構件。**可判定判準**：對身份時變屬性之查詢含 as-of 時間界限、且該屬性具 valid/transaction time 版本者為合規；屬性以原地覆蓋（last-write-wins、無版本）承載、或消費無日期條件者違反本條。

### 8.2 與 Layer 4 as-of 引擎之界限 [N]

> **ID.61（繫結存在 vs 重建引擎之分界）[N｜hooks｜`AUGUR-MC v1.3 §P4.E2`；`AUGUR-WM v1.0 §WM.30`、`§D8`；目標 Layer 4]**
> 本規格課予「身份屬性**必須**具 as-of 繫結（版本存在）」之義務（ID.60）；而 **as-of 重建之機制與能力等級**（重建引擎、雙時間查詢之操作化）DEFER Layer 4（`§P4.E2`，Annex DO IDO.6；`AUGUR-WM v1.0 §WM.30`、`§D8` HOOK-01 上呈素材）。二者分界：本層保證「版本可繫結、歷史可重建之資訊存在」；Layer 4 提供「重建之引擎與能力等級」。
> **義務主體**：本規格、Layer 4。**可判定判準**：本規格未對重建引擎作實質定義、且 as-of 繫結義務可被 Layer 4 引擎消費者為合規。

---

## §9 與 Layer 4 分界（Boundary with Knowledge System）[N]

> 集中重申 §1.2（ID.2）之下界封印，供 Annex CS 對表。

> **ID.70（Layer 4 專屬事項清單）[N｜carries｜`AUGUR-MC v1.3 §P4.E1`、`§P4.E2`、`§P4.E7`、`§P4.E8`]**
> 下列一律屬 Layer 4，本規格僅設槽位／掛鉤：
> * **Confidence 語義**（單一形式化定義、全系統可比較、傳播、消費門檻，`§P4.E8`）——identity claim（ID.30(d)）之 Confidence 槽位之語義填充；
> * **Knowledge 五元組欄位設計**（`§P4.E1`）——identity claim（ID.31）與 lifecycle 事件（ID.40）之完整 Knowledge 欄位；
> * **as-of 重建引擎與能力等級**（`§P4.E2`）——ID.61；
> * **來源信任分級表**（`§P4.E7`）。
> **義務主體**：本規格自身。**可判定判準**：本規格對上開任一事項作可被 Layer 4 直接消費之實質定義者違反本條（下侵）。

> **ID.71（分界表）[N｜carries｜`AUGUR-ONT v0.1-draft` Annex L3（同構）]**
> 本層與 Layer 4 之逐項分界見 **Annex L4**（與 `AUGUR-ONT v0.1-draft` Annex L3 同構之精確分界表）。
> **義務主體**：本規格。**可判定判準**：Annex L4「本層得為」欄與「Layer 4 專屬」欄無交集。

---

## §10 Constitutional Compliance Statement Format 承接與存續 [N]

> **ID.80（格式承接）[N｜carries｜`AUGUR-WM v1.0 §WM.39–45`；`AUGUR-MC v1.3 §8.3`]**
> 本規格之 Constitutional Compliance Statement 依 `AUGUR-WM v1.0 §WM.39–45` 正式格式作成（見 **Annex CS**），**非**暫行模板（本規格作成於 `AUGUR-WM v1.0` 生效日〔2026-07-16〕後，`§WM.45`）。無依該格式作成之聲明使本規格不生效力（`§WM.39`）。
> **義務主體**：本規格自身、Steward。**可判定判準**：Annex CS 之 front-matter 欄位、七節論證、緊張關係節、雙向 DEFER 表俱全（`§WM.40–44`）。

> **ID.81（存續與升版）[N｜carries｜`AUGUR-MC v1.3 §8.6`；`AUGUR-WM v1.0 §WM.46–47`；`AUGUR-ONT v0.1-draft §ONT.60`]**
> 本規格條款編號依 `§0.3` 穩定；`AUGUR-MC` 或 `AUGUR-WM`／`AUGUR-ONT` major 升版時本規格進入重新認證期（`AUGUR-MC v1.3 §8.6`）。本規格全部「不得」（MUST NOT）義務不得豁免（`AUGUR-MC v1.3 §8.4`）。
> **義務主體**：本規格、Steward。**可判定判準**：升版時 Annex CS 之 `mc-version`／`upper-specs` 欄同步；版本間 diff 檢查——任一既發布編號於後版消失或改指他文者違反本條。

---

## Annex O [N] — OPEN-1 承接（stock_id 代碼重用／時間穩定性採認）

> 承接 `AUGUR-WM v1.0 §A.54`（OPEN-1）、`§D6`，`AUGUR-ONT v0.1-draft` T.90（OPEN-1 Security 判準採認）、T.1／T.20、DO.1。

> **AO.1（承接聲明）[N]**
> `AUGUR-WM v1.0 §A.54` 將本域證券代碼之時間穩定性（改名、代碼重用、借殼）登錄為**顯式未定義行為**，其保守預設（供應商證券代碼為**指涉資訊、非 identifier**；代碼重用／改名一律經 identity claim 表徵）為 [N] 效力，候選判準記載（「代碼相等 ∧ 存續期間重疊」）為 [I] 素材、經本層採認前不生效力。`AUGUR-ONT v0.1-draft` T.1 已**制定** Security↔Issuer 分離型別之同一性判準（其判準內容以 `AUGUR-ONT v0.1-draft` T.1 為準，本層**不複述**其文句，以免跨層漂移／上侵）。本層僅承接其**採認**，並記載被採認判準之 Layer 2 條款引用（`AUGUR-ONT v0.1-draft` T.1），不改寫其內容（改寫屬 Layer 2 制定，違者上侵、違 ID.1）。
> **義務主體**：本規格、採認作成者。**可判定判準**：涉 Security／Issuer 判準之下層條款含對 `§AO.1`／`AUGUR-WM v1.0 §A.54`／`AUGUR-ONT v0.1-draft` T.90 之引用者為合規。

> **AO.2（採認之治理前提）[N]**
> OPEN-1 之正式判準採認**待 Steward／決策層拍板**（`AUGUR-WM v1.0 §D6`）。本規格提供採認機制（§4 ID.20），惟 Security／Issuer 判準之**實質採認生效**須經 Steward 依 `AUGUR-MC v1.3 §8.1` 之書面裁決（或決策層依治理程序）作成；於此拍板前，涉 Security／Issuer 之 Identity 引用依 `§WM.21(e)` 保守解釋為**未解析**。
> **義務主體**：本規格、Steward／決策層。**可判定判準**：無採認紀錄時將 Security 引用視為已解析者違反本條。

> **AO.3（採認後之 lifecycle 銜接）[N]**
> OPEN-1 判準一經採認，代碼重用／借殼之處置即銜接 §6（ID.43 存續邊界截斷）：跨 retire/relist 邊界之同一外部代碼解析為不同存續個體，供應商證券代碼降格為 provisional alias（identity claim，`§WM.21(c)`），發行人（Issuer）同一性以其自身判準（`AUGUR-ONT v0.1-draft` T.20：法律實體同一；借殼／更名不改 Issuer identity，但得改其所發行 Security identity）解析。
> **義務主體**：本規格、Layer 4 消費者。**可判定判準**：採認後之 Security 歷史縫合（違 ID.43）者違反本條。

> **AO.4（Issuer 判準採認之具名落點）[N]**
> `AUGUR-ONT v0.1-draft §DO.1` 並列下放 Layer 3 之判準採認為 **T.1（Security 判準）與 T.20（Issuer 判準）**。Issuer（T.20：法律實體同一；借殼／更名不改 Issuer identity，但得改其所發行 Security identity，承接 `AUGUR-WM v1.0 §A.57`）之判準採認，由 §4 **ID.20 通用採認機制**承接，其採認記錄依 ID.20 五要素作成；交叉引用 `AUGUR-ONT v0.1-draft §DO.1` 之 T.20 列與 `AUGUR-WM v1.0 §A.57`。使 `§DO.1` 兩具名 Type（Security、Issuer）於本層各有可雙向解析之採認落點。
> **義務主體**：本規格、採認作成者。**可判定判準**：涉 Issuer（T.20）判準之下層條款含對 `§AO.4`／`AUGUR-ONT v0.1-draft §DO.1`（T.20）／`§A.57` 之引用、且無採認紀錄時不得將 Issuer 引用視為已解析者為合規。

---

## Annex DO [N] — 下放下層之 DEFER 掛鉤（defers-out）

> **IDO.0（承接義務）[N]** 本表每列為規範性下放掛鉤：本層明示不定義該實作事項，授權並要求目標 Layer 定義之；目標 Layer 規格作成時必須於其 Compliance Statement 之 `defers-in` 欄承接對應列。
> **義務主體**：本規格自身（設掛鉤）、目標 Layer 規格作者（承接）。**可判定判準**：本表每列與 Annex CS front-matter `defers-out` 欄雙向可解析；本層無任一條款對本表所列事項作成可被下層直接消費之實質定義（ID.2／ID.70 下侵判準）。

| 掛鉤 | 本規格落點 | 下放事項 | 目標 Layer | 授權條款 | 承接審計 |
|---|---|---|---|---|---|
| **IDO.1** | ID.30(d)、ID.70 | identity claim 之 **Confidence 語義**（形式化定義、可比較、傳播、門檻） | L4 | `AUGUR-MC v1.3 §P4.E8` | AUD-03/06 |
| **IDO.2** | ID.31、ID.40、ID.70 | identity claim 與 lifecycle 事件之 **Knowledge 五元組欄位設計** | L4 | `AUGUR-MC v1.3 §P4.E1` | AUD-06 |
| **IDO.3** | ID.40 | lifecycle **事件表之物理欄位／索引實作**、tombstone 儲存落地 | L4／L7 | `AUGUR-MC v1.3 §0.6(b)`；`AUGUR-WM v1.0 §D3` | AUD-05 |
| **IDO.4** | ID.23、ID.51 | **resolution 演算實作**、未解析存量指標之**量測落地與門檻值** | L4 | `AUGUR-WM v1.0 §D4`；`AUGUR-ONT v0.1-draft §DO.1` | AUD-04/06 |
| **IDO.5** | ID.12 | identifier 命名空間之**物理序列化與儲存編碼** | L7 | `AUGUR-MC v1.3 §0.6(b)`；`AUGUR-WM v1.0 §WM.20` | AUD-04 |
| **IDO.6** | ID.61 | **as-of 重建引擎與能力等級**、雙時間查詢操作化 | L4 | `AUGUR-MC v1.3 §P4.E2`；`AUGUR-WM v1.0 §D8` | AUD-07/08 |
| **IDO.7** | ID.42、CS.1-P1 | 自然人**法規對應表本體**與其授權（`AUGUR-WM v1.0 §D17` 之 L6 slice；本層僅承接其 L3 去識別化／抹除機制 slice，見 ID.42） | L6 | `AUGUR-MC v1.3 §P1.E3`；`AUGUR-WM v1.0 §WM.38`、`§D17` | — |
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

## Annex CS [N] — Constitutional Compliance Statement（依 `AUGUR-WM v1.0 §WM.39–45` 格式）

本 Annex 為**規範性聲明文件**（[N]）：其存在與內容為本規格之生效要件（ID.80、`AUGUR-MC v1.3 §8.3`、`AUGUR-WM v1.0 §WM.39`）。本聲明依 `AUGUR-WM v1.0 §WM.39–45` **正式格式**作成（非暫行模板，`§WM.45`：本聲明作成於 Layer 1 生效日 2026-07-16 之後）。**地位提示**：本規格為 v0.1-draft 提案，未經 Steward 充任認定前不生效力（見【地位】、ID.80）；本聲明之充分性最終判斷屬 Steward 違憲審查與充任認定程序。

```
compliance-statement:
  spec: Augur Identity Specification
  spec-version: v0.1-draft
  layer: 3
  mc-version: AUGUR-MC v1.3
  upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v0.1-draft]
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

> **CS.1-PA（Prime Axiom）**〔滿足＋承接〕引 `AUGUR-MC v1.3 §1.1`。持續一致之 Identity 為 PA 之構成支柱；本規格以 identifier 永不刪除（ID.13）、lineage 不變式（ID.41）、跨部署可解析（ID.10）落實「持續一致之 Identity」，以 identity claim 之 Evidence 要件（ID.30(c)）落實「可追溯之 Evidence」。判準揭示：本規格未引入 PA 以外之評價性謂詞；「持續一致」以 lineage 可重建（ID.41 可判定判準）操作化。

> **CS.1-P1（Reality First）**〔細化〕引 `§P1.E1`、`§P1.E2`、`§P1.E3`。identifier 之跨部署可解析與對齊（ID.10）為 `§P1.E2` 之落地；外部識別碼降格為指涉資訊（ID.11）落實「資料來源不得成為最高抽象」（`§P1.E1`）。P1.E3（自然人 Bounded Representation）：身份屬性 as-of 繫結（§8）於自然人屬性之消費受法域義務約束——涉自然人表徵之域內宣告承接 `AUGUR-WM v1.0 §A.59`、`§WM.38`。**D17（自然人法規對應，目標 L3/L6）之分承**：其 **L3 slice**（自然人 identity 側去識別化／法規強制抹除機制、時變屬性 as-of 繫結）由本層 **ID.42** 及 §8（ID.60）承接；其 **L6 slice**（法規對應表本體與授權）DEFER Layer 6（IDO.7）。判準揭示：跨部署對齊可判定性依 ID.10；D17 之 L3 slice 於 ID.42 具具名落點，非整項下推。

> **CS.1-P2（Representation Before Intelligence）**〔承接〕引 `§P2.E1`、`§P2.W2`、`§P2.E5`。provisional 不得升級為 Knowledge（ID.50）落實候選斷言經 Evidence 通道方確立；採認前保守解釋為未解析（ID.21）落實權威順序；採認撤回之 fail-safe 重評估（ID.22）承接 `§P2.E5`。判準揭示：「已解析」以採認紀錄存在（ID.20）操作化。

> **CS.1-P3（Identity Before Knowledge）〔核心〕**〔承接＋細化〕引 `§P3.E1`、`§P3.E2`、`§P3.E3`、`§2.4`。
> * `§P3.E1`（引用與解析義務）→ ID.50–ID.53、ID.11（mint-on-admission）、ID.51（可稽核指標，承接 `AUGUR-WM v1.0 §D4`）；
> * `§P3.E2`（Identity Lifecycle）→ ID.13（永不刪除）、ID.40–ID.43（merge/split/retire/relist/轉指全程 lineage、tombstone、去識別化），落實 **AUD-05**；
> * `§P3.E3`（同一性判準掛鉤）→ ID.20–ID.23（採認，承接 `AUGUR-ONT v0.1-draft §ONT.21`／DO.1）、ID.53（instance/type 標記存續，承接 `§ONT.30`）；
> * `§2.4`（identifier／identity claim 區分）→ ID.14、ID.30–ID.32（identity claim 一級介面），落實 **AUD-06**。
> 判準揭示：本節每一評價性用語（「已解析」「可追溯」「唯一權威」）均附可判定判準（ID.20／ID.41／ID.32）。

> **CS.1-P4（Evidence Before Conclusion）**〔承接＋DEFER〕引 `§P4.E1`、`§P4.E2`、`§P4.E3`、`§P4.E5`、`§P4.E6`、`§P4.E8`。identity claim 與 lifecycle 事件為需引用 Evidence 之 Knowledge（ID.30(c)、ID.40）；只失效不刪除（ID.22、ID.40）；衝突並存（ID.31）；身份屬性雙時間（ID.60，錨定 `§P4.E2`）。**DEFER**：Confidence 語義（IDO.1／`§P4.E8`）、Knowledge 五元組欄位（IDO.2／`§P4.E1`）、as-of 重建引擎（IDO.6／`§P4.E2`）下放 Layer 4。判準揭示：DEFER 掛鉤載明目標 Layer 與授權條款（Annex DO）。

> **CS.1-P5（Accountability Before Action）**〔不適用（附理由）〕本規格為概念層 Identity 規格，不定義 Action、授權鏈或風險分級（屬 Layer 6）。惟採認（ID.20）、lifecycle 事件（ID.40）、去識別化（ID.42）均為具作成者之可歸責治理行為，其歸責記錄與 P5 精神相容。判準揭示：本規格未定義任何 Action 六元組事項。

> **CS.1-EV-chain（§4 canonical chain）**〔承接〕引 `§4` EV.4（Identity）為本規格之標準鏈落點；引 `AUGUR-WM v1.0 §WM.24`（節選連續性）。本規格機制化 EV.4：Observation（EV.2）經 provisional（ID.50）解析取得 Identity（EV.4），方得繫結為 Evidence（EV.5）／Knowledge（EV.6）。判準揭示：節選不跳節點；provisional→resolved→Knowledge 之單向不可逆升級（ID.21、ID.50）。

### CS.2 已知緊張關係（`AUGUR-WM v1.0 §WM.42`）[N]

| T-id | 所涉條款 | 描述 | 緩解／狀態 |
|---|---|---|---|
| **T-ID-1** | ID.30(d)、IDO.1 | identity claim 需 Confidence 槽位，但其語義 DEFER Layer 4（`§P4.E8`）尚未定義。 | 本層僅設槽位並要求 Layer 4 承接；語義未定前，涉 claim 之升級消費採保守解釋（`§P4.E7` 最弱環節約束）。非豁免事項。 |
| **T-ID-2** | ID.12、IDO.5 | identifier 結構設計權（`§WM.20`／D5）與概念層獨立性（`§0.6(b)`）之張力：命名空間須有結構，然物理編碼屬 Layer 7。 | 本層僅定**概念命名空間**（referent 空間隔離＋跨部署對齊契約）；物理序列化下放 Layer 7（IDO.5）。非豁免事項。 |
| **T-ID-3** | AO.2、`§D6` | OPEN-1 Security 判準採認待 Steward／決策層拍板；本層提供採認機制但實質採認非本規格單方可為。 | 拍板前保守解釋為未解析（`§WM.21(e)`）；本規格備妥採認機制待拍板即生效。非豁免事項。 |
| **T-ID-4** | ID.60、ID.61、IDO.6 | 身份屬性 as-of 繫結義務（本層）與 as-of 重建引擎（Layer 4，`§P4.E2`）分屬二層，重建能力等級尚未定義。 | 本層保證版本繫結存在；重建能力 DEFER Layer 4（HOOK-01 上呈素材）。非豁免事項。 |
| **T-ID-5** | ID.31、IDO.2 | identity claim 為 Knowledge（`§2.4`）受 P4 約束，然其完整 Knowledge 五元組欄位設計屬 Layer 4。 | 本層定身份側四要件（ID.30），完整欄位下放 Layer 4；二者以 IDO.2 對接。非豁免事項。 |
| **T-ID-6** | ID.42、§8、IDO.7、`§D17` | 自然人法規對應（`AUGUR-WM v1.0 §D17`）目標為 **L3/L6**，其 L3 機制 slice（去識別化／抹除、時變屬性 as-of）與 L6 法規對應表本體之分界待具體法域義務落地方確定。 | L3 slice 由 ID.42（＋ID.60）承接、繫結 `AUGUR-ONT v0.1-draft` T.23；L6 slice DEFER Layer 6（IDO.7）。分界待定但雙側均有具名落點，非承接漏列。非豁免事項。 |

豁免登記：`none`（waivers: []）。本規格無現行豁免；如有，依 `AUGUR-WM v1.0 §WM.33` 豁免狀態標記位置落實。

### CS.3 雙向 DEFER 承接表（`AUGUR-WM v1.0 §WM.43`）[N]

* **(a) 承接上層之掛鉤（defers-in）**：`AUGUR-WM v1.0 §D2`(採認側)→ID.20；`§D3`→§5／§6；`§D4`→ID.51；`§D5`→§3；`§D6`→Annex O；`§D17`(L3 slice)→ID.42、§8（L6 slice DEFER Layer 6，IDO.7）；`AUGUR-ONT v0.1-draft §DO.1`→§4／§7；`§DO.2`→§3／§5；`§DO.3`→§6（含 ID.44 DynamicEntity 終結）；`§DO.4`→§7／§8。與 front-matter `defers-in` 欄雙向對表。
* **(b) 下放下層之掛鉤（defers-out）**：IDO.1–IDO.8（見 Annex DO），與 front-matter `defers-out: [IDO.1, IDO.2, IDO.3, IDO.4, IDO.5, IDO.6, IDO.7, IDO.8]` 互為索引。

### CS.4 形式充分性（`AUGUR-WM v1.0 §WM.44`）[N]

依 `§WM.44` 判準自查：`AUGUR-MC v1.3` **全部** [N] 條款、`AUGUR-WM v1.0` **全部** [N] 條款、`AUGUR-ONT v0.1-draft` **全部** [N] 條款，均須對應至本規格至少一 [N] 條款、或明記 DEFER 掛鉤、或明記「不觸及」及理由（P5 家族依 CS.1-P5 明記不適用）。明記「不觸及」之主要條款群及理由：

* `AUGUR-MC v1.3` P5 全組、§5 架構角色、§6 F5–F6：其規範對象為行動治理／架構角色／智慧輸出可解釋性，屬 Layer 4–6；本層僅型別化行動主體之 identifier，不代定機制。
* `AUGUR-WM v1.0` WM.24–29（canonical chain 承接於 CS.1-EV-chain；fail-safe／模態表達力屬 Layer 4–6）、WM.49–53（Domain Profile 框架，本層消費其產物而不制定）：本層 Identity 機制不使其不可表達（ID.13、ID.40、ID.41 為表達力承載）。
* `AUGUR-ONT v0.1-draft` ONT.10–13、ONT.40–41、Annex T 之型別**定義**：屬 Layer 2 制定，本層僅**採認**（ID.20）與**機制化**（§3、§5、§6），不重述型別定義內容。ONT.40 世界關係之端點封印解除／派生解析由 ID.24 承接。

**明記對應／DEFER（非不觸及）之補正**：`AUGUR-WM v1.0 §WM.38`（自然人有界表徵）及其 Annex D 掛鉤 **D17**（自然人法規對應表，L3/L6）：其 **L3 slice** 對應至 ID.42（去識別化／法規強制抹除機制）＋§8（ID.60，時變屬性 as-of），其 **L6 slice** 明記 DEFER Layer 6（IDO.7）；故 WM.38/D17 於本自查為「對應＋DEFER」，非「不觸及」。`AUGUR-ONT v0.1-draft §DO.3` 之 T.3/T.4/T.5（DynamicEntity 終結生命週期）對應至 ID.44。

**逐條對應矩陣未完整枚舉——生效阻卻**：`AUGUR-MC v1.3`／`AUGUR-WM v1.0`／`AUGUR-ONT v0.1-draft` 全部 [N] 條款 → 本規格落點之**逐條完整枚舉**（`§WM.44` 要求之機器可判完備對應矩陣）**於本 draft 尚未完整作成**。依 `§WM.44`「任一條款無對應且無明記者，聲明不完整，規格不生效力」，在該矩陣完備為附錄追溯矩陣前，**形式充分性未成就、本規格不生效力**（見【地位】）；此矩陣**必須**於 Steward 充任認定前補足，**不得**以「正式定稿時補足」為由延宕其為生效要件之性質。**實質充分性**由違憲審查程序（`AUGUR-MC v1.3 §8.2`）與充任認定（`§0.5`）判斷。

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
| Annex CS | 憲章合規聲明 | CS.1–CS.4 | `WM.39–45` |

---

*本規格計：正文條款 ID.1–ID.81、Annex O（AO.1–AO.4）、Annex DO（IDO.0–IDO.8）、Annex L4（L4.0）、Annex CS 合規聲明 [N]。全文以繁體中文為權威文本（§0.4）。本文件為 v0.1-draft 提案，未經 Steward 充任認定前不生效力（`AUGUR-MC v1.3 §0.5`、【地位】、ID.80）。*

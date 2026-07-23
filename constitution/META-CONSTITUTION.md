# 《Augur Meta-Constitution v1.4》

Augur Enterprise AI Operating System
元憲章（Meta Layer）正式定稿
文件定位：最高層級設計憲章（Supreme Design Constitution）

---

## §0 Document Status & Conventions（文件地位與約定）[N]

### 0.1 名稱、層級與版本

* 名稱：Augur Meta-Constitution
* 層級：Layer 0 — Meta Constitution
* 版本：v1.4（前版：v1.3）
* 生效日：2026-07-16
* 批准記錄：本次修訂依 **v1.0 §7（修訂當時之有效程序）** 辦理；§8 治理章屬**初始採行（initial adoption）**，自本版生效起，後續修訂改依 §8.5。登錄於 Amendment Log（AL-2026-001），修訂理由書隨卷存檔；理由書載明新增 P5 符合 v1.0 §7 實質判準之論證（見 Appendix C 第 12 點）。
* 自 v1.0 之變更摘要見 Appendix C。v1.1 → v1.2 為定稿階段之缺陷修復與一致性修正（無新原則、無原則級實質變更，依 §8.6 定為 minor），依 §8.5 辦理並登錄 Amendment Log（AL-2026-002）；修訂記錄見 Appendix D。
* v1.2 → v1.3：§0.5 Layer 對照表增列五份 augur 領域治權文件之定位登錄（依 §8.6，Layer 對照表之增列屬 minor、由 Steward 議決），與 Layer 1 規格充任認定（Steward 裁決第 2026-002 號）同案辦理，登錄 Amendment Log（AL-2026-006）；變更摘要見 Appendix E。除 §0.5 對照表增列（及 §0.1 版本欄、Appendix E [I] 隨附）外，無其他條文變更、無原則級變更。
* v1.3 → v1.4：MC 首次三鏡對抗審查（2026-07-18）findings 之處置（RULING-2026-017／AL-2026-020，minor）——§0.5 L2–L7 充任註記補登＋跨層治權檔例外句（§8.6 明定之 minor）、§0.2／§2.6 之 [I] 補述、治理附則第 3 條繼任人恆存（annex minor）；**八項 §8.1 解釋**記於裁決（不改 MC 本文）。**§8／構成性依據之 [N] 本文一律不動**（§8 self-entrenchment＝原則級，非 minor 可為；2026-07-18 獨立核驗糾正越權）。**無原則級變更、無 PA 變更、五原則本文零改**；摘要見 Appendix F。

### 0.2 規範用語約定

本憲章之約束力等級如下，全文一致適用：

| 用語 | 對應 | 效力 |
|---|---|---|
| 必須 | MUST | 絕對義務，違反即違憲 |
| 不得 | MUST NOT | 絕對禁止，違反即違憲 |
| 應 | SHOULD | 原則上遵守，偏離須書面說明理由 |
| 得 | MAY | 允許，不構成義務 |

> **[I] 用語補述（RULING-2026-017 §8.1）**：全文之「須」「需」為「必須（MUST）」之同義用語、具同等絕對義務效力；本表四詞之一致適用及於其同義詞。

### 0.3 條文效力標注

* 每一章節標題標注 **[N]（Normative，規範性）** 或 **[I]（Informative，資訊性）**。
* 各原則之 WHY 段一律為 [I]：其功能為說理，不產生獨立義務；義務僅由 [N] 條款產生。
* [N] 與 [I] 內容不一致時之處理，依 §8.2。
* 條款編號系統：PA｜P{n}.D / P{n}.W{m} / P{n}.Y / P{n}.E{m}｜EV.1–EV.12｜F1–F6｜§2.{n}（Definitions）。章節號（§0–§9 及其小節與項次，如 §8.3、§2.11）視同條款編號，得為 §8.6 引用格式之引用對象。編號穩定性規則（永不重用、永不重排、廢止標注）依 §8.6。

### 0.4 權威語言聲明

本憲章以**繁體中文版為權威版本**；英文術語為規範性術語之原詞，英文對照譯本僅供參考。規範性術語於正文中一律使用英文原詞（如 Reality、Identity、Evidence）。

### 0.5 適用範圍：Layer 對照表

本憲章高於並約束 Layer 1–7 之全部規格。每份 **Layer 規格**恰屬一層；**領域治權文件（如原則精華、CLAUDE.md、系統架構大憲章）得跨多層，其逐條／逐節之 Layer 歸屬由各檔之合規聲明載明**（RULING-2026-017 附則 minor 釋明：「恰屬一層」之不變式適用於 Layer 規格，不適用於跨層領域治權檔）。以下為單一權威對照表；新增規格必須先在本表登錄所屬 Layer 方生效力。本表增列之修訂等級與議決程序依 §8.6：

| Layer | 層名 | 所轄規格 |
|---|---|---|
| 1 | World Model | World Model Specification（AUGUR-WM v1.0，經 Steward 裁決第 2026-002 號充任認定）、系統核心思想（augur 領域前身文件） |
| 2 | Ontology | Ontology Specification（AUGUR-ONT v1.0，經 Steward 裁決第 2026-003 號充任認定） |
| 3 | Identity System | Identity Specification（AUGUR-ID v1.0，經 Steward 裁決第 2026-004 號充任認定） |
| 4 | Knowledge System | Knowledge Graph Specification（AUGUR-KS：v1.0 經 Steward 裁決第 2026-005 號充任，現行 v1.1／RULING-2026-016）、Data Intelligence Layer、原則精華（augur 領域治權文件；跨層條款之逐條 Layer 標注由其合規聲明載明） |
| 5 | Cognitive Kernel | Cognitive Kernel Specification（AUGUR-L5 v1.0 **provisional**——RULING-2026-006 充任；2026-07-18 RULING-2026-019 撤回形式充分性、2026-07-19 RULING-2026-023 重採認〔乙〕回復（矩陣重作＋L5.10 as-of）；§8.1 橋接收束；§8.2 實質審查延後）、Reasoning Engine、AI Model Selection |
| 6 | Agent Runtime | Agent Runtime Specification（AUGUR-L6：v1.0 經 Steward 裁決第 2026-007 號充任，現行 v1.2／RULING-2026-016）、Planner / Orchestrator、CLAUDE.md（augur 領域 Agent 協作規格；**可執行 Python 入口須載「執行指令矩陣」**—RULING-2026-026／§8.1 解釋；細則 CLAUDE.md #18/#29） |
| 7 | External Interface / Infrastructure | Infrastructure Specification（AUGUR-L7 v1.0，經 Steward 裁決第 2026-011 號充任；§8.2 深度審查 2026-07-19 條件通過 RULING-2026-025——(iii)(iv)(vi) residual 分階段①、復審 2026-10-14）、External Interface Layer、Database Architecture、系統架構大憲章（augur 領域架構／維運承載文件；涉 Layer 4–6 之章節由其合規聲明逐節標注）、datasets 參考文件（datasets_zh.md 及 finmind-references） |

任何後續技術規格、資料模型、程式實作、AI Agent 行為，均不得違反本憲章。

### 0.6 Hierarchy Rule（層級規則）

(a) **Lex superior**：編號較小之層對編號較大之層具規範效力；下層牴觸上層者，牴觸部分無效（後果依 §8.2）。
(b) **概念層獨立性**：Layer 1–4（概念層）之規格不得引用 Layer 5–7（執行層）之構件作為定義依據。
(c) **箭頭語意**：本憲章所有層級圖中之向下箭頭，語意一律為 **constrains（約束）**。

```
Layer 0  Meta-Constitution
   │ constrains
   ▼
Layer 1  World Model
   ▼
Layer 2  Ontology
   ▼
Layer 3  Identity System
   ▼
Layer 4  Knowledge System
   ▼
Layer 5  Cognitive Kernel
   ▼
Layer 6  Agent Runtime
   ▼
Layer 7  External Interface / Infrastructure
```

---

## §1 Supreme Purpose — Prime Axiom（最高使命）[N]

### 1.1 Prime Axiom（PA）—— 永恆條款（Eternity Clause）

> **Augur exists to faithfully represent reality through persistent identity and traceable evidence, enabling trustworthy intelligence.**

中文：Augur 唯一使命，是以持續一致的 Identity 與可追溯的 Evidence，忠實表徵真實世界，並在此基礎上產生可信的智慧。

本條為**永恆條款**：不受任何修訂程序變更（§8.5）。

**釐清句 [N]**：忠實（faithfully）不意謂完美鏡像。Representation 永遠是帶不確定性的近似；忠實性體現於：不確定性可追溯、錯誤可被新 Evidence 修正（詳 P4.E3–P4.E5）。本釐清句僅得說明 PA 之適用方式；其效力邊界與修訂門檻，依 §8.5(d)。

五大原則（§3）為本使命之不可違反展開。

### 1.2 標準鏈引用

世界演化之唯一權威標準鏈（canonical chain）見 §4（EV.1–EV.12）。本節速記為其節選 EV.1–EV.6：

```
Reality → Observation → Representation → Identity → Evidence → Knowledge
```

Intelligence 於 canonical chain 之落點為其節選 EV.7–EV.8（Reasoning、Planning），承接 v1.0 公理金字塔以 Intelligence 為終點之語意。

智慧不是第一目的。智慧是：真實世界被正確表徵後，自然產生的能力。

### 1.3 五條對稱禁令

| 禁令 | 對應原則 |
|---|---|
| 沒有 Reality 對應（referent），不允許 Representation。 | P1 |
| 沒有可靠 Representation，不允許 Intelligence。 | P2 |
| 沒有 Identity，不允許 Knowledge。 | P3 |
| 沒有 Evidence，不允許 Conclusion。 | P4 |
| 沒有可歸責至人類權威（Human Authority）之 Authorization，不允許 Action。 | P5（執行落點：F6） |

「可靠」之判定義務：Representation 之建立與維護符合 P1–P4 ENFORCE 條款中以個別表徵（或其構成之 Observation、Evidence、Knowledge）為對象之條款者，方為可靠；系統級或流程級 ENFORCE 義務（如 P1.E1、P2.E5、P4.E8）之違反，使受影響範圍內之 Representation 推定不可靠。

**模態內容之 referent 釐清 [N]**：Hypothesis、Prediction、Plan 之預期狀態等模態內容，其 referent 為所繫結 Identity 之可能狀態，屬合法 Representation；惟必須顯式標記為模態內容，不得作為現實狀態之斷言。

---

## §2 Definitions（定義）[N]

以下術語為本憲章之初始概念，每詞一句內涵式定義：

1. **Reality** ＝ 世界事物、狀態、事件與變化之總和；其存在與狀態不以被任何系統表徵為前提。**自反性條款**：Augur 自身（含其 Agent、Model、軟硬體與運行狀態）為 Reality 中之實體，得被觀測與表徵。**表徵內容除外規則**：系統內 Representation 與 Knowledge 之內容變更，於本憲章中稱「表徵狀態變更」，不構成 §4 因果迴路意義下之 Reality 變更；惟改變系統之權限、部署、物理資源或對外行為者，仍屬 Reality 變更。
2. **Observation** ＝ 對 Reality 的一次有 Source、有 Timestamp 的量測或記錄。
3. **Representation**（全文中「World Representation」為其同義全稱）＝ 以共同世界模型對 Reality 所作的一致、可追溯、可演化之結構化描述；每一世界事實在系統內有唯一權威表徵（語義唯一性，不預設集中式拓撲）。
4. **Identity** ＝ 對一個世界實體唯一且持續的指稱；區分 **identifier**（系統鑄造之永久參照，identifier 本身為系統內具 Identity 地位之一級物件）與 **identity claim**（「兩個 identifier 指涉同一實體」之斷言，繫結於其所涉之 identifier，本身為受 P4 約束之 Knowledge）。
5. **Evidence** ＝ 被引用以支持某項 Knowledge 之 Observation、明示宣告之假設（P4.E6）或推導結果（角色關係，非階段先後）。
6. **Knowledge** ＝ 繫結 Identity、有 Source、由 Evidence 支持、附 Confidence、繫結成立時間、可被推翻（defeasible）之斷言。

> **[I] 定義補述（RULING-2026-017）**：Evidence（§2.5）與 Knowledge（§2.6）互為定義項——為基礎詞彙之**共定義對**（角色關係）；§2.5 已標「角色關係，非階段先後」，二者不以彼此之時間先後為要件。此揭露符 §2 導言「每詞一句內涵式定義」之體例自陳。
7. **Intelligence** ＝ 產生新斷言或行動方案之任何過程（含檢索、推論、規劃）。
8. **Agent** ＝ 經授權讀寫世界模型並執行 Action 之自主程序；Agent 為 Identity 之一種（Agentive Entity）。
9. **Action** ＝ 由可歸責 Identity 發起、意圖造成 Reality 變更之事件。凡經 Controlled External Interface（§5 角色六）對系統外發出、足以造成 Reality 變更之操作，一律視為 Action，不以意圖之有無或宣稱為斷；非經授權鏈而實際造成 Reality 變更之事件，構成 F6 所禁止之違憲事件，必須以 Observation 回流並溯責於引致其發生之 Identity。純表徵狀態變更（§2.1）非 Action：其受 P2、P4 之通道與溯源義務約束，不受 P5.E1 六元組約束。
10. **Confidence** ＝ 對 Knowledge 為真之程度之可量化表述（其語義之單一形式化定義權：P4.E8）。
11. **Evidence 通道** ＝ 標準鏈之節選 EV.2–EV.5（Observation → Representation → Identity → Evidence）；候選斷言（proposed assertion）經此通道取得 Identity 繫結與 Evidence 支持後，方得確立為權威 Representation 或 Knowledge。候選斷言不以另生新 Observation 為通道要件：其 EV.2 節點由該斷言 Evidence 鏈遞迴終止之 Observation 或明示宣告之假設（P4.E6）滿足；僅以明示宣告之假設為據者，得經本通道確立，惟必須顯式標記假設依據，其 Confidence 受 P4.E4、P4.E7 約束。

**元規則**：下層文件不得重新定義本章術語，僅得細化。

---

## §3 Five Immutable Principles（五大不可違反原則）[N]

所有 Augur 架構皆由以下五條原則展開。原則本身不受豁免（§8.4）。

---

### Principle 1 — Reality First（真實世界優先）

**P1.D Definition [N]**

Augur 的第一性對象不是資料、模型、程式或資料庫。
Augur 的第一性對象是：真實存在於世界中的事物、狀態、事件與變化。

**P1.W1 WHAT [N]**

Augur 必須優先描述 Reality，而不是優先適配現有資料來源。
資料只是：Reality 的觀測結果。
模型只是：Reality 表徵後的推理工具。

**P1.Y WHY [I]**

> 資料結構不是世界結構。

若以資料表（ERP table、MES table、database schema）作為世界基礎，會造成：

* 系統邊界限制世界理解
* 不同系統產生不同世界
* AI 只能理解資料，而非理解世界

**P1.E ENFORCE [N]**

* **P1.E1（開放來源）**：任何對 Reality 的觀測通道——無論當前是否存在——皆屬資料來源，包括但不限於：ERP、MES、Sensor、Document、External Knowledge。資料來源不得成為最高抽象。
* **P1.E2（共同世界模型之語義）**：所有資料來源必須映射至共同世界模型，其語義為：每一世界事實有唯一權威表徵，且 Identity 必須可跨部署邊界解析與對齊。集中或聯邦拓撲屬下層部署決策。
* **P1.E3（Bounded Representation）**：對自然人之 Observation 與 Representation，受目的正當性、授權與所在法域法律義務約束。忠實表徵 Reality 不構成無限觀測之依據；合規義務與功能衝突時，合規優先。**與 PA 之位階釐清**：合規義務限制者為觀測與表徵之「範圍」；於合法觀測範圍內，對已觀測事實之忠實表徵義務（PA）不因此減損——本條不得引為選擇性表徵（扭曲世界模型）之依據。具體法規對應由下層規格定義。

---

### Principle 2 — Representation Before Intelligence（表徵先於智慧）

**P2.D Definition [N]**

Augur 首要任務不是產生智慧。
而是：建立對世界一致、可追溯、可演化的 Representation。

**P2.W1 WHAT [N]**

任何 Prediction、Reasoning、Planning、Decision、Agent Action，皆必須建立於 World Representation。

**P2.W2 權威順序釐清 [N]**

本原則規範**權威順序，非時間順序**。AI 得參與 Representation 之建構（identity resolution、抽取、映射），但其輸出僅得以附帶 Evidence 與 Confidence 之**候選斷言（proposed assertion）**進入系統，經 Evidence 通道（§2.11，節選 EV.2–EV.5）確立後，方成為 Representation 之一部分。

**P2.Y WHY [I]**

> AI 最大風險不是能力不足，而是：對錯誤世界產生高度合理的智慧。

```
錯誤 Representation → 錯誤 Knowledge → 錯誤 Reasoning → 錯誤 Action
```

**P2.E ENFORCE [N]**

* **P2.E1**：禁止 AI 直接從 raw data 建立永久性 Knowledge。所有 AI 產物必須經標準鏈（§4 之節選 EV.2–EV.6）：

```
Observation → Representation → Identity → Evidence → Knowledge
```

* **P2.E2**：Model output 不得未經 Evidence 通道（§2.11），直接成為權威 World Representation 或 Knowledge。
* **P2.E3**：Agent 不得繞過 Evidence 通道（§2.11），將其意圖、預期或未經證實之執行結果直接寫入 World Representation 作為世界狀態。Action 之影響必須以 Observation 之姿回流：Agent 之 execution receipt 與外部確認訊號皆屬合法 Observation，其 Source 為該 Agent 之 Identity。此類自我陳述之 Observation 必須永久攜帶 **self-reported 標記**，僅構成「關於該 Action 之宣稱性 Observation」，非世界狀態之權威確認；其升級為 Knowledge 受 P4.E7（不得僅以系統自身產出為據）約束。
* **P2.E4**：禁止 Representation 被視為 Reality 本身——任何 Representation 元素必須保留其 Observation 來源與不確定性。
* **P2.E5（Fail-safe）**：當任何 Representation 或 Evidence 被判定錯誤或撤回：(a) 衍生之 Knowledge 必須標記並重新評估；(b) 依賴之進行中 Plan / Action 必須暫停；(c) 受影響範圍內系統降級為觀測與建議模式，直至修復。錯誤或撤回之判定主體與程序、污染追蹤機制（據以界定本條之「受影響範圍」）、及「觀測與建議模式」之操作邊界，均由 Layer 4–6 定義（DEFER）；有爭議時由 Steward 裁決（§8.1）。

---

### Principle 3 — Identity Before Knowledge（身份先於知識）

**P3.D Definition [N]**

世界中的任何 Knowledge，必須首先回答：「這是關於哪一個 Identity？」

**P3.W1 WHAT [N]**

Augur 不以 table row、file、document、embedding、model token 作為世界基本單位。
Augur 的基本單位：**Identity**。

**P3.W2 Identity 類型 [N]**

Identity 涵蓋之實體類型包括但不限於以下四類：

* **Physical Entity**：Factory、Machine、Material、Employee（自然人，其表徵受 P1.E3 約束）
* **Abstract Entity**：Project、Concept、Financial Instrument
* **Dynamic Entity**：Event、Process、State
* **Agentive Entity**：AI Agent、Model、作為決策者之 Human

完整分類體系由 Layer 2 Ontology 定義。

**P3.Y WHY [I]**

沒有 Identity，同一物件可能變成：

```
ERP: Machine_A
MES: Equipment_001
Sensor: device_452
Document: PECVD chamber
```

AI 無法知道：它們是否為同一世界實體。

**P3.E ENFORCE [N]**

* **P3.E1（引用與解析義務）**：所有 Knowledge、Relation、Goal、Constraint、Capability、Plan、Action 必須引用**已解析之 Identity**。所有 Observation 必須攜帶可供 Identity Resolution 之指涉資訊，得先以未解析（provisional identity）狀態進入系統；未解析之 Observation 不得升級為 Knowledge，且系統負有解析義務。解析時限或未解析存量之可稽核指標，必須由 Layer 3 定義（DEFER）。Goal、Constraint、Capability、Plan 之定義由 Layer 5–6 定義（DEFER）；無論其定義為何，凡意圖進入 Reasoning／Planning 之結構化物件均落入本條引用義務。
* **P3.E2（Identity Lifecycle）**：identifier 一經鑄造（mint）永不刪除。identifier 之後續指向變更（如合併後之轉指）必須全程可追溯（不變式）；轉指機制由 Layer 3 定義。Identity 之 merge / split / retire 與更正，本身為必須引用 Evidence 之 Knowledge，全程保留可追溯歷史（identity lineage）。Identity 存續跨越任何 Ontology / Representation 變更。法規強制抹除準用 P4.E3 例外：得移除 identifier 所繫結之可識別內容並去識別化，惟 identifier 本身以留痕形式（如 tombstone）存續、抹除事件具完整 provenance、identity lineage 保留；留痕與去識別化機制由 Layer 3 定義。
* **P3.E3（同一性判準掛鉤）**：每類 Identity 必須宣告其同一性判準；Knowledge 必須明示繫結對象屬個體（instance）或類型（type）。判準與分類由 Layer 2 / Layer 3 定義。

---

### Principle 4 — Evidence Before Conclusion（證據先於結論）

**P4.D Definition [N]**

任何 Knowledge、Reasoning 與 Decision：必須可以追溯其 Evidence。

**P4.W1 WHAT [N]**

Augur 不接受：無 Source 之 Knowledge、不可重現之結果、無 Evidence 之推論。

Evidence 包括但不限於三類（分類法之維護權屬 Layer 4）：

* **Data Evidence**：如 ERP record、Sensor measurement
* **Knowledge Evidence**：如 Paper、Specification
* **Computational Evidence**：如 Model output、Simulation

**P4.Y WHY [I]**

> 沒有 Evidence：AI 只是在生成可能性，不是理解。

**P4.E ENFORCE [N]**

* **P4.E1（Knowledge 五元組）**：任何 Knowledge 必須具有：

```
Knowledge
 |
 +-- Source
 |
 +-- Timestamp
 |
 +-- Identity
 |
 +-- Evidence
 |
 +-- Confidence
```

此為任何 Knowledge 必須能回答之五個問題（來源為何／何時成立／關於哪個 Identity／依據為何／多可信）之**最低不變式**；欄位設計屬 Layer 4。

* **P4.E2 Time（雙時間性）**：任何 Observation 與 Knowledge 必須區分 **valid time**（何時為真，可為區間）與 **transaction time**（系統何時得知）。任一過去時刻系統之認識狀態必須可追溯且可稽核（不變式）；重建該狀態（as-of）之機制與能力等級由 Layer 4 定義。Timestamp 為 Knowledge 有效性宣稱之一部分，非元資料裝飾。
* **P4.E3 Supersede（只失效不刪除）**：Knowledge 與 Evidence 不得刪除，僅得標記為 superseded / retracted / invalidated；失效為需要 Evidence 之知識行為，全歷史保留。唯一例外：法規強制抹除得移除內容本體，但抹除事件自身必須留痕並具完整 provenance（不變式）；留痕機制（如 tombstone）由 Layer 4 定義。
* **P4.E4 Defeasible（可謬性）**：所有 Knowledge 皆可被新 Evidence 推翻；Confidence 不得為隱含之 1.0；任何 Knowledge 不得標記為不可修正。
* **P4.E5 Conflict（矛盾保存）**：互相衝突之 Evidence 必須共存並顯式標記，不得靜默消滅（禁止 last-write-wins）。衝突之裁決為推理行為，其結論為攜帶自身 Evidence 與 Confidence 之新 Knowledge，永不覆寫原始證據。「目前證據不足」為合法且必須可表達之系統狀態。
* **P4.E6 Provenance（遞迴溯源）**：Evidence 為一級物件，自身必須可溯源：記錄斷言主體（agent，含版本）、產生活動（含輸入與參數）、上游依據。證據鏈必須遞迴終止於對 Reality 之 Observation 或明示宣告之假設。禁止循環引證。
* **P4.E7 NoLaundering（信任不可洗白）**：衍生證據之信任不得高於其上游最弱來源；結論之 Confidence 上限受證據鏈最弱環節約束。AI 生成／合成內容永久攜帶 synthetic 標記，不因轉引而消失。高風險 Action 之結論不得僅以系統自身產出之證據為依據，須至少一項獨立 Data Evidence 或人類確認（人類確認必須以確認者之已解析 Identity 為 Source、留痕為 Observation；確認者之資格與獨立性判準由 Layer 6 連同風險分級表定義（DEFER））。「獨立」之判準：該 Data Evidence 之 provenance 鏈遞迴不含本系統之 Computational Evidence，且不與待證結論共享上游來源。「高風險 Action」依 P5.E2 所轄之 Layer 6 風險分級表認定，全憲章同一分級。來源信任分級表由 Layer 4 定義。
* **P4.E8 Confidence（語義與消費）**：Confidence 語義必須於 Layer 4 以單一形式化定義、全系統可比較、評定方法可追溯。Confidence 必須沿推理鏈向下游傳播；Action 之允許等級受其依據 Knowledge 之最低 Confidence 約束。

---

### Principle 5 — Accountability Before Action（可歸責先於行動）

**P5.D Definition [N]**

改變 Reality 之任何 Action（§2.9），必須先回答：「誰發起？誰授權？憑什麼知識？」純表徵狀態變更（§2.1）非 Action，其發起者與依據之歸責由 P2、P4 之通道與溯源義務承擔，不適用 P5.E1 六元組。

**P5.W WHAT [N]**

* **P5.W1**：任何 Action 必須可歸責於單一 Identity（人或 Agent）。
* **P5.W2**：授權鏈（chain of authority）之根節點必須是**人類權威**——人類得在任何時點否決、暫停或中止任何 Plan 與 Action。
* **P5.W3**：Action 之權限與其不可逆性成反比：不可逆或高影響之實體世界 Action，需最高等級之 Evidence 完備性、Confidence 門檻與人類事前核准。「高影響」與不可逆性之分級，依 P5.E2 所轄之 Layer 6 風險分級表認定。
* **P5.W4**：Agent 僅持有完成當前經授權 Plan 所需之最小權限。
* **P5.W5**：系統不得規劃、執行或學習任何降低人類監督與否決能力之行為。「監督與否決能力」之可稽核度量由 Layer 6 定義（DEFER）；於該定義生效前，凡降低既有人工核准層級、移除人工介入點、或延長無人工檢核之自動執行鏈之變更，一律推定違反本條，不得實施；該推定僅得由 Steward 依 §8.1 解釋權以書面裁決推翻，裁決必須附具「該變更未實質降低人類監督與否決能力」之認定理由並公開存檔。該裁決不構成、亦不得構成對本條之豁免（§8.4）。

**P5.Y WHY [I]**

前四原則（P1–P4）保證「知識是對的」，不保證「行動是安全的」——後果可逆性與損失不對稱性獨立於知識品質。預測錯了可修正 Knowledge；行動錯了，其物理後果無法收回（領域例示：一爐報廢的晶圓）。技術會變，物理行動之不可逆性與人類作為信任主體不會變。

**P5.E ENFORCE [N]**

* **P5.E1（Action 六元組）**：任何 Action 必須具有：

```
Action
 |
 +-- Actor Identity
 |
 +-- Authorization（可追溯至人類權威之授權鏈）
 |
 +-- Knowledge Basis
 |
 +-- Timestamp
 |
 +-- Expected Effect
 |
 +-- Observed Effect（連結 Feedback）
```

* **P5.E2（風險分級 DEFER）**：風險分級表、各級對應之 Evidence 完備性要求（完備性等級之定義由 Layer 4 定義，DEFER）與 Confidence 門檻（Confidence 之語義依 P4.E8 由 Layer 4 定義）、及核准流程，由 Layer 6 Agent Runtime 定義；本分級表為 P4.E7、P5.W3 之共同認定依據。**缺位預設規則**：分級表生效前，一切意圖改變實體世界之 Action 一律視為最高風險等級——須人類事前逐案核准方得執行，並記錄為暫行分級。Controlled External Interface（§5 角色六）為行動分級之執法點。

---

## §4 World Evolution Model（世界演化模型）[N]

本節為世界演化之**唯一權威標準鏈（canonical chain）**，節點編號 EV.1–EV.12。其他章節之引用一律標注為節選（EV.x–EV.y），節選不得跳過中間節點。

```
EV.1  Reality ◄════════════════════════════╗
  │                                        ║
  ▼                                        ║
EV.2  Observation                          ║
  │                                        ║  因果迴路
  ▼                                        ║ (Causal Loop:
EV.3  Representation ◄─────────────┐       ║  Action 經
  │                                │       ║  Observation
  ▼                                │       ║  重新進入)
EV.4  Identity                     │       ║
  │                                │       ║
  ▼                                │       ║
EV.5  Evidence                     │       ║
  │                                │       ║
  ▼                                │       ║
EV.6  Knowledge ◄──────────────────┤       ║
  │                                │       ║
  ▼                                │       ║
EV.7  Reasoning                    │       ║
  │                                │       ║
  ▼                                │       ║
EV.8  Planning                     │       ║
  │                                │       ║
  ▼                                │       ║
EV.9  Human Authority Gate (P5)    │       ║
  │                                │       ║
  ▼                                │       ║
EV.10 Action ══════════════════════╪═══════╝
  │                                │
  ▼                                │  認知迴路
EV.11 Feedback                     │ (Cognitive Loop)
  │                                │
  ▼                                │
EV.12 Learning ────────────────────┘
```

**雙迴路語義 [N]**（本節為對 v1.0 §3 圖示語意之更正，見 Appendix C 第 4 點）：

* **因果迴路（Causal Loop）**：系統唯有經由 Action（EV.10）改變 Reality（EV.1）；系統以外之 Reality 變化不經 EV.10，逕以 Observation（EV.2）進入系統。Action 之影響必須經 Observation 重新進入系統（P2.E3）。
* **認知迴路（Cognitive Loop）**：Feedback（EV.11）與 Learning（EV.12）改變的是表徵狀態（Representation 與 Knowledge 之內容），依 §2.1 表徵內容除外規則，不構成 Reality 變更。Learning 不得實作為世界狀態寫入。**通道義務不豁免**：圖中 EV.12 之回邊表示影響方向，非直寫授權——Learning 之產出仍以候選斷言經 Evidence 通道（§2.11）確立（P2.W2、P2.E1）。
* **Human Authority Gate（EV.9）**：Planning 與 Action 之間之**授權鏈驗證點**，為 P5 於本模型之落點。每一 Action 於此驗證其授權鏈可追溯至人類權威（P5.W2）；人類介入之強度依 P5.W3 之風險分級認定，非一律人類事前核准。
* **EV.5 語義註記**：EV.5 於本鏈中之語義為「證據化（citing as evidence）」之行為階段；Evidence 本身為角色關係（§2.5），兩者並行不悖。

---

## §5 Architectural Roles（架構角色）[N]

由五大原則導出六個**抽象架構角色**。本節為規範性架構承諾，不含任何產品名；現行技術選型之對照見 Appendix A（非約束性）。

1. **World State System of Record**：權威世界狀態。保存 Identity、Observation、Event、State、Evidence Metadata；具 append-only 與 provenance 性質（P4.E3、P4.E6）。
2. **World Relationship Representation**：世界關係表徵。保存 Relation、Causal Connection、Dependency、Knowledge Graph。
3. **Semantic Memory**：語意記憶。負責 Meaning、Similarity、Context Retrieval。
4. **World Understanding Engine（Cognitive Kernel）**：世界理解引擎。負責 Reasoning、Inference、Hypothesis、Explanation。
5. **World Action Layer（Agent Runtime）**：世界行動層。負責 Planning、Execution、Feedback（受 P5 約束）。
6. **Controlled External Interface**：世界模型與外部系統之受控介面；P5 行動分級之執法點。

---

## §6 Forbidden Design Patterns（禁止設計模式）[N]

以下設計違反本憲章：

### F1 — Data First Architecture

禁止：「先建立資料表，再想世界模型」。（違反 P1）
原因：資料結構不是世界結構。

### F2 — Model First Architecture

禁止：「先選 AI model，再設計系統」。（違反 P2）
原因：模型只是智慧工具。

### F3 — Agent First Architecture

禁止：「先做 Agent，再補資料治理」。（違反 P2、P5）
原因：Agent 會放大錯誤世界理解。

### F4 — Knowledge Without Identity

禁止存在無 Identity 繫結、無 Source 之 Knowledge。（違反 P3.E1、P4.E1）

### F5 — Intelligence Without Evidence

禁止：任何 prediction / recommendation / decision 無法回答「為什麼？」。（違反 P4.E1、P4.E6）

### F6 — Unaccountable Action

禁止：任何無法回答「誰發起、誰授權、憑什麼知識」之 Action。（違反 P5.E1）

---

## §7 Long-Term Stability Rule（十年以上演化原則）[N]

Augur 不依賴：特定 AI model、特定 database、特定 programming language、特定 cloud provider。

技術會改變；Reality 會演化、Identity 會演化。但以下原則不會改變：

* 忠實表徵 Reality（P1）
* 以 Representation 先於 Intelligence（P2）
* 以 Identity 錨定 Knowledge（P3）
* 以 Evidence 支撐 Conclusion（P4）
* 以人類權威歸責 Action（P5）

此五項不變核心（Reality / Representation / Identity / Evidence / Accountability）即 §8.5(b) 實質判準所引用之同一清單。

---

## §8 Conformance, Interpretation & Amendment（合規、解釋與修訂）[N]

### 8.1 Constitution Steward（憲章權威）

必須存在唯一之人類憲章權威（**Constitution Steward**，得為個人或審議體）。Steward 持有：

* 條文之最終解釋權
* 規格之違憲審查權
* 修憲之裁決權

**Agent（§2.8 意義下之自主程序）不得參與修憲與解釋**；此禁止不及於作為決策者之 Human（Agentive Entity）。解釋裁決必須書面化、附理由、公開存檔，並對後續案件具拘束力（解釋先例）。

**設立與繼任**：

* **首任 Steward**：本憲章 v1.1 生效時，由 Amendment Log（AL-2026-001）具名登錄之批准人擔任首任 Steward。
* **治理附則**（規定 Steward 之組成、任命、繼任程序與各級議決門檻之具體數值）由 Steward 制定並公開發布，必須於本憲章生效後 90 日內生效；逾期未生效者，缺位預設規則繼續適用。**附則缺位期間之預設規則**：Steward 為單一自然人；凡本憲章要求依特定議決門檻辦理之事項，均以其書面裁決行之；惟原則級修訂於附則生效前僅得受理提案，不得議決。
* **Entrenchment**：Steward 之設立、§8.1 所列權力及其罷免規則之任何變更，適用原則級門檻（§8.5(b)）；治理附則不得變更 §8.1 所列權力。附則之其餘內容依 minor 門檻修訂。

### 8.2 違憲後果、審查程序與衝突優先序

* **違憲審查之聲請**：受本憲章約束之任何規格作者或工程成員，得以書面聲請違憲審查，載明系爭條款、涉嫌牴觸之憲章條款與具體事證。
* **裁決期限與效力推定**：Steward 必須自聲請送達之日起 60 日內書面裁決（含以不合本節聲請要件為由之附理由駁回）；逾期未裁決者，系爭規格推定有效並標記「待審」。裁決作成前，系爭規格推定有效；但系爭事項涉不可豁免核心（§8.4）者，不適用逾期有效之推定，推定停用至裁決作成之日。
* 經認定違憲之條款自認定日起無效，不得作為下層規格之依據。
* 既有實作之補正期由 Steward 個案裁定並載明到期日，自違憲認定日起算，至遲於下一個 major 版本生效日屆滿，且不得逾治理附則所定之曆時上限（附則未定者，不得逾 24 個月）；期滿未補正者停用。
* 同位階條款衝突視為文件缺陷，修正前採較嚴格解讀——即對系統之許可較少、對義務較重之解讀，與 §8.3 保守解釋（存疑即不允許）同向。
* Normative 與 Informative 內容不一致時，以 Normative 為準。

### 8.3 合規聲明義務與可判定性元規則

* 每份 Layer 1–7 規格必須內含 **Constitutional Compliance Statement**：聲明其合規之憲章版本、逐原則之合規論證、已知緊張關係之揭露。無此聲明之規格不生效力。聲明格式由 Layer 1 定義。**過渡規則**：(a) 聲明格式定義於 Layer 1 生效前，由 Steward 發布暫行模板，依該模板作成之聲明有效；(b) 本憲章生效時之既存規格享有補正期（期限由 Steward 裁定並公告），期內推定有效；(c) Layer 1 自身之聲明依暫行模板作成，不因格式自我引用而無效。
* **可判定性元規則（開放式）**：憲章之任何評價性謂詞——包括但不限於 reliable、faithful、trustworthy、「高影響」、「高風險」、「獨立」、「降低監督能力」——被下層引用時，該規格必須同時給出可判定之判準；判準未給出前，採保守解釋（存疑即不允許）。
* ENFORCE 條款之核心不變式——Knowledge → Evidence → Observation **或明示宣告之假設**（P4.E6）之引用鏈完整性、Action 之 Identity 歸因——必須可機器稽核。

### 8.4 暫時豁免與不可豁免核心

* **核心條款之定義**：Prime Axiom（含其釐清句）、§3 五大原則之全部 [N] 條款、§4 canonical chain、§7、§8，合稱核心條款。
* **豁免範圍**：Steward 得對核心條款以外之 [N] 條款、或核心條款之**履行時程與完備程度**，核發**有明確到期日**之書面豁免，公開登錄、附補正計畫。豁免不得解除任何核心條款之義務本身；本憲章任何禁止性規定（MUST NOT）均不得豁免，含其履行時程——禁止性規定無補正期程可言，時限豁免即等同許可。§0.2–0.3 之效力約定、§2 之全部定義及其元規則，為核心條款之構成性依據：對其之任何豁免視同對核心條款之豁免，不得核發。
* **不可豁免核心**（連履行時程亦不得豁免）：Prime Axiom、Evidence 追溯義務（P4.E1、P4.E6）、人類權威條款（P5.W2、P5.W5）。
* 豁免期間產生之 Knowledge 仍須標記豁免狀態與 Evidence 缺口。
* 豁免期限與程序細則屬治理附則。

### 8.5 Amendment Procedure（修訂程序）

* **(a) 提案權**：受本憲章約束之任何規格作者得書面提案，載明：擬修條文、新條文、以及現行原則在具體案例中失效或產生矛盾之**書面 Evidence**，附新舊對照與全下層衝擊分析。修憲本身適用 Evidence Before Conclusion。
* **(b) 議決**：原則級修訂由 Steward 以最高門檻議決，且必須同時滿足下列二要件：
  * **(i) 程序要件**：現行原則失效或矛盾之書面 Evidence（(a) 所定）；
  * **(ii) 實質判準**：論證新條文能**更完整描述五項不變核心**（§7：Reality / Representation / Identity / Evidence / Accountability）。本判準承繼 v1.0 §7 之實質判準，並自四項擴為五項（沿革揭露見 Appendix C 第 12 點）。
  附則採較低門檻。核心條款（§8.4 定義）及其構成性依據（§0.2–0.3、§2）之修訂一律適用原則級門檻；其餘 [N] 條款之修訂門檻由治理附則定之，附則未定者適用原則級門檻。§8 自身之修訂適用原則級門檻（self-entrenchment）。
* **(c) 記錄**：新版本號、修訂理由書、生效日，登錄 Amendment Log。
* **(d) Eternity Clause**：Prime Axiom 不受任何修訂程序變更。對 PA 之任何規範性解釋文字（含 §1.1 釐清句）之增、刪、修，一律適用原則級（最高）門檻；解釋文字不得限縮或擴張 PA 本文之義務範圍。

### 8.6 版本語義、引用格式與編號穩定性

* 原則級實質變更 = **major**（觸發全下層合憲複審）；附則與 Informative 變更 = **minor**；編輯修正 = **patch**。Layer 對照表（§0.5）之增列屬 minor，由 Steward 議決。
* 下層引用格式：`AUGUR-MC v{version} §{條款編號}`（例：`AUGUR-MC v1.2 §P5.W3`）。
* 條款編號一經發布永不重用、永不重排；廢止條款保留編號並標注 (repealed)。
* 憲章 major 升版時，既有規格進入重新認證期（期限由 Steward 裁定），期內效力延續。

---

## §9 Final Statement（終極宣言）[I]

Augur 不追求製造一個看似智慧的系統。
Augur 追求建立一個能長期忠實理解世界的系統。

當世界被正確表徵，智慧自然產生。

因此：

> **Reality First.**
> **Representation Before Intelligence.**
> **Identity Before Knowledge.**
> **Evidence Before Conclusion.**
> **Accountability Before Action.**

### 定稿結構 [I]

```
Layer 0  Meta-Constitution
│
├── Prime Axiom（永恆條款）
├── P1 Reality First
├── P2 Representation Before Intelligence
├── P3 Identity Before Knowledge
├── P4 Evidence Before Conclusion
└── P5 Accountability Before Action

        │ constrains
        ▼
Layer 1 World Model
        ▼
Layer 2 Ontology
        ▼
Layer 3 Identity System
        ▼
Layer 4 Knowledge System
        ▼
Layer 5 Cognitive Kernel
        ▼
Layer 6 Agent Runtime
        ▼
Layer 7 External Interface / Infrastructure
```

**編纂性註記 [I]**：任何原則之增修悉依 §8 程序辦理；非經該程序，不再加入額外原則。

---

## Appendix A — v1.x 參考技術選型對照 [I]

本附錄為**非約束性**資訊：屬 Layer 7 現行選型、可隨時代更換、不受本憲章穩定性保證。

| §5 架構角色 | v1.x 現行選型 |
|---|---|
| World State System of Record | PostgreSQL |
| World Relationship Representation | Neo4j |
| Semantic Memory | Vector Database |
| World Understanding Engine | Cognitive Kernel（自研） |
| World Action Layer | Agent Runtime（自研） |
| Controlled External Interface | MCP |

---

## Appendix B — 憲章金句（記憶錨點）[I]

* 智慧是：真實世界被正確表徵後，自然產生的能力。（§1.2）
* 資料結構不是世界結構。（P1.Y）
* AI 最大風險不是能力不足，而是對錯誤世界產生高度合理的智慧。（P2.Y）
* 沒有 Evidence：AI 只是在生成可能性，不是理解。（P4.Y）
* 預測錯了可修正 Knowledge；行動錯了，其物理後果無法收回。（P5.Y；「一爐報廢的晶圓」為領域例示）
* 當世界被正確表徵，智慧自然產生。（§9）

---

## Appendix C — 自 v1.0 之變更摘要 [I]

1. **技術中立化**：原 §4 之產品名（PostgreSQL、Neo4j、Vector DB、MCP）自正文移除；正文改為六個抽象架構角色（§5），產品對照降為非約束性 Appendix A，修復與技術中立原則（原 §6/§7）之矛盾。「MCP Interface Layer」更名為「External Interface Layer」（更名沿革僅記載於此，正文不留舊名）。
2. **新增唯一原則 P5 — Accountability Before Action**：補齊行動治理缺口（人類權威為授權鏈根節點、權限與不可逆性成反比、最小權限、不得侵蝕人類監督），並新增 F6 Unaccountable Action 與第五條對稱禁令（§1.3）。
3. **新增 §2 Definitions**：十一個初始概念一句式定義（含 Evidence 通道之正式定義），附「下層不得重定義」元規則；刪除未定義之 Truth 一詞。Reality 定義含自反性條款與表徵內容除外規則，以區分「外部世界變更」與「表徵狀態變更」。
4. **統一演化鏈（語意更正）**：§4 定為唯一 canonical chain（EV.1–EV.12，新增 Human Authority Gate 節點）。**本項為對 v1.0 §3 圖示語意之更正，非等價重繪**：v1.0 原圖 Learning 直接回指 Reality；v1.1 改為雙迴路——唯有 Action 改變 Reality（因果迴路），Learning 僅改變表徵狀態且其寫入仍須經 Evidence 通道（認知迴路）。他處一律節選引用，P2 之鏈補回 Identity。
5. **P4 ENFORCE 大幅強化**：新增雙時間性、只失效不刪除（法規抹除須留痕）、可謬性、矛盾保存、遞迴溯源、信任不可洗白（含獨立性判準）、Confidence 語義與下游消費等七條編號條款；五元組保留為最低不變式。憲章僅陳述不變式（不刪除、可追溯、抹除留痕、認識狀態可稽核），機制（tombstone、as-of 重建、轉指）一律下放 Layer 3/4 定義。
6. **P3 修復自舉死鎖與生命週期**：identifier / identity claim 區分（identifier 本身具 Identity 地位）、provisional identity、mint 永不刪除、merge / split / retire 為 Evidence 支持之 Knowledge、instance / type 掛鉤（細則 DEFER 至 Layer 2/3，含解析時限指標）。
7. **P2 釐清與 Fail-safe**：明文化「權威順序非時間順序」與候選斷言機制；**改寫 Agent 世界狀態禁令（實質變更揭露）**——v1.0 為無條件禁止「Agent 自行創造世界狀態」，v1.1 改為條件式：execution receipt 得以 Observation 回流，但必須永久攜帶 self-reported 標記、僅屬宣稱性 Observation、升級為 Knowledge 受 P4.E7 約束；新增錯誤發現後之失效反應義務（P2.E5）。
8. **新增 §8 治理章（初始採行）**：Constitution Steward（解釋權、違憲審查、修憲裁決；Agent 不得參與）、首任 Steward 之設立與附則缺位預設規則、違憲審查之聲請程序與裁決期限、違憲後果與補正期上限、合規聲明義務與開放式可判定性元規則、暫時豁免之邊界（核心條款定義、原則本身不可豁免）與不可豁免核心、修訂程序、Prime Axiom 永恆條款（含釐清句之原則級門檻）、版本語義與編號穩定性。
9. **文件工程**：條款編號系統（PA / P{n}.W{m} / P{n}.E{m} / EV.x / F1–F6，P5 條款完整編號）、[N]/[I] 效力標注、規範用語等級、權威語言聲明（中文）、單一 Layer 對照表與 Hierarchy Rule（constrains 語意、lex superior、概念層獨立性）。
10. **新增 P1.E3 Bounded Representation（獨立規範性義務）**：對自然人之觀測與表徵受目的正當性、授權與法域法律約束；合規義務與功能衝突時合規優先。並明定其與 PA 之位階：合規限制「觀測範圍」，不減損「對已觀測事實忠實表徵」之義務，不得引為選擇性表徵之依據。
11. **§7 立論基礎之反轉（實質哲學立場變更揭露）**：v1.0 §6 稱「Reality、Identity、Evidence 不會改變」；v1.1 §7 改稱「Reality 會演化、Identity 會演化，但五項原則不會改變」。十年穩定性之立論基礎由「表徵對象不變」移轉為「原則不變」。理由：企業世界之實體與狀態顯然隨時間演化，v1.0 原句無法字面成立；不變者為系統對待世界之原則。
12. **修憲判準之承繼與變更（沿革揭露）**：v1.0 §7 之實質判準（新原則須「更完整描述 Reality / Identity / Evidence / Representation」）承繼於 §8.5(b)(ii)，並自四項擴為五項（納入 Accountability）；另新增「現行原則失效之書面 Evidence」為程序要件。**本次修訂（含新增 P5）依 v1.0 §7 辦理（過渡適用）**，其判準論證：Action 為 v1.0 §3 演化模型中 Reality 變化之內生環節，v1.0 已表徵 Action 卻未約束之；P5 使 Reality 之因果演化（何者得改變 Reality、憑何授權）獲得更完整描述，符合 v1.0 §7「更完整描述 Reality」之判準。v1.0 定稿聲明「不再加入額外原則」屬編纂性註記而非修訂程序之一部分，其受控封閉語義由 §9 編纂性註記承繼。§8 治理章為初始採行（v1.0 無對應程序可資適用）。
13. **其他收斂**：封閉列舉改開放式（包括但不限於）並收斂例示（保留 Employee 以維持自然人例示與 P1.E3、P5 規範重心一致）；聯邦相容之共同世界模型語義；§1 禁令補為五條對稱；模態內容（Hypothesis / Prediction / Plan）之 referent 語義釐清；「不再加入額外原則」改為受控封閉之編纂性註記，刪除「已收斂至最小核心」之宣稱。

---

## Appendix D — 自 v1.1 之變更摘要（v1.2）[I]

本輪為定稿階段之缺陷修復與一致性修正（AL-2026-002）。無新增原則、無原則級實質變更（各項修正旨在消除文本矛盾、補齊定義權歸屬與過渡規則、統一術語體例，不變更五大原則之實質內容），依 §8.6 定為 minor 升版。修正項目一項一行：

1. P5.D 刪除「或 World Representation」，與 §2.9 Action 定義對齊，並明示純表徵狀態變更之歸責路徑（P2、P4）未落空。
2. §8.3 合規聲明增列過渡規則：暫行模板、既存規格補正期、Layer 1 自我引用不致無效，消除自舉死鎖。
3. §8.2 逾期效力推定增列不可豁免核心之除外：涉核心者不適用逾期有效推定，維持停用至裁決作成。
4. §8.2 裁決期限改自「聲請送達之日」起算（含附理由駁回），消除受理黑洞。
5. §8.4 MUST NOT 豁免禁令自五大原則擴及本憲章全部禁止性規定，並明示禁止性規定無時限豁免可言。
6. P5.W5 末句重構：Steward 書面核可改為依 §8.1 解釋權附理由推翻推定之裁決，明示不構成豁免。
7. §8.4 增列 §0.2–0.3 與 §2 為核心條款之構成性依據（豁免視同對核心條款之豁免）；§8.5(b) 補齊其修訂門檻（一律原則級）與其餘 [N] 條款門檻之預設規則。
8. §2.11 增列假設終點之通道語義（候選斷言不以另生新 Observation 為要件）；§2.5 Evidence 定義納入明示宣告之假設（P4.E6）。
9. §2.9 增列客觀判準（經受控介面對外發出即為 Action，不以意圖為斷）與未授權實變之 F6 定性；§4 因果迴路限定為「系統唯有經由 Action 改變 Reality」，系統外變化逕以 Observation 進入。
10. P5.E2 增列缺位預設規則：分級表生效前，實體世界 Action 一律視為最高風險等級、人類事前逐案核准。
11. P5.E2 補齊 Evidence 完備性等級（Layer 4 定義，DEFER）與 Confidence 門檻之定義權歸屬。
12. §8.5(b) 導語「二實質要件」改「下列二要件」，消除與 (i) 程序要件之標籤矛盾。
13. F4 改為「無 Identity 繫結、無 Source」，刪除未定義之 owner／entity／source 用語。
14. P4.D、P4.W1、P2.E1、§7、§8.4 之中文通名（知識／證據／智慧／結論／行動）改用英文規範術語，落實 §0.4。
15. §0.3 編號系統納入 §2.{n} 與章節號（視同條款編號，同受 §8.6 穩定性保證）。
16. §8.2 補正期上限改為可判定曆時規則：自違憲認定日起算、至遲於下一 major 版生效日屆滿、附則未定者不逾 24 個月。
17. §8.1 附則缺位預設規則改寫，消除「各級門檻條款以其書面裁決為之」之語病與兩讀歧義。
18. §2.3 加註「World Representation」為 Representation 之同義全稱。
19. §2.6 Knowledge 定義補列 Source，與 P4.E1 五元組對齊。
20. §8.2「較嚴格解讀」錨定方向：對系統許可較少、義務較重，與 §8.3 保守解釋同向。
21. P3.E2 增列法規強制抹除之準用例外（tombstone 留痕、lineage 保留，機制由 Layer 3 定義）。
22. P4.E7「人類確認」補齊形式（已解析 Identity 為 Source、留痕為 Observation）與資格／獨立性判準之定義權（Layer 6，DEFER）。
23. §8.1 治理附則補明制定主體（Steward 制定並公開發布）與逾期後果（缺位預設規則繼續適用）。
24. §1.3「可靠」判定改為個別表徵條款／系統級義務二分，系統級違反使受影響範圍推定不可靠。
25. P3.E1 補列 Goal、Constraint、Capability、Plan 之定義權（Layer 5–6，DEFER）與引用義務兜底語。
26. P2.E5 將污染追蹤機制（界定受影響範圍）與「觀測與建議模式」操作邊界一併下放 Layer 4–6 定義（DEFER），消除文法歧義。
27. §1.1 釐清句末句改為引用 §8.5(d)，消除永恆條款防禦圈之雙重權威。
28. §0.3、§0.5 對 §8.2、§8.6 之複述改為純引用；「由 Steward 議決」補入 §8.6 為單一權威。
29. §2.10 Confidence 定義刪除內嵌之 Layer 4 義務陳述，改引 P4.E8。
30. P5.Y「四大原則」改「前四原則（P1–P4）」。
31. P3.W2 改「涵蓋之實體類型包括但不限於以下四類」，消除封閉計數與開放列舉之矛盾。
32. §2.11「候選斷言」首次出現處補英文對照（proposed assertion）。
33. §1.3 首次出現處補「人類權威（Human Authority）」英文對照。
34. §8.3「不變量」改「不變式」，統一 invariant 定譯。
35. §1.2 EV.7–EV.8 引用補標「其節選」，落實 §4 節選標注規則。

---

## Appendix E — 自 v1.2 之變更摘要（v1.3）[I]

本輪為 §0.5 Layer 對照表之增列（minor 升版，AL-2026-006），與 Layer 1 規格充任認定（Steward 裁決第 2026-002 號，AL-2026-005）同案辦理。除 §0.5 對照表增列（及 §0.1 版本欄、本摘要 [I] 隨附）外，無其他條文變更、無原則級變更：

1. §0.5 Layer 1 欄註記 World Model Specification 之充任認定（AUGUR-WM v1.0），並增列「系統核心思想」為領域前身文件。
2. §0.5 增列四份 augur 領域治權文件之定位登錄：原則精華 → Layer 4、CLAUDE.md → Layer 6、系統架構大憲章與 datasets 參考文件 → Layer 7。跨層內容之逐條／逐節 Layer 標注由各檔之 Constitutional Compliance Statement 載明（補正期依 Steward 裁決第 2026-002 號主文二：至 2026-10-14）。
3. §0.1 版本欄隨升；本摘要新增為 Appendix E。

---

## Appendix F — 自 v1.3 之變更摘要（v1.4）[I]

本輪為 AUGUR-MC v1.3 **首次三鏡對抗審查**（2026-07-18，L0 元憲章生涯首審）findings 之處置（Steward 裁決第 2026-017 號、AL-2026-020，minor）。findings 冊見 audits/MC-THREE-MIRROR-REVIEW-2026-07-18.md。**無新增原則、無原則級實質變更、PA 與五原則本文零改**——全為治理程序、語彙與 editorial 之精修。

**MC 本文變更（[I]／minor；§8 與構成性依據之 [N] 本文一律不動）**：
1. §0.5：L2–L7 充任認定補登（原僅 L1 有註記；§8.6 明定之 minor）；「每份規格恰屬一層」增跨層領域治權檔例外句。
2. §0.2：增 [I] 用語補述——「須／需」為「必須（MUST）」同義（[I] 添加，不改 [N] 效力）。
3. §2.6：增 [I] 補述——Evidence／Knowledge 為共定義對（[I] 添加）。

**明示不以 minor 為之（§8 self-entrenchment；2026-07-18 獨立核驗糾正越權）**：§8.6／§0.3 之 [N] 本文與治理附則之條款級別對映**不在本批執行**——§8.4 列 §8 為核心、§8.5(b) 定 §8 自身及構成性依據（§0.2-0.3、§2）之修訂一律原則級，非 minor 可為。此類事項改由 §8.1 解釋處理，或俟 Steward 依 §8.5 原則級程序（14 日公示）另辦。

**§8.1 解釋（八項，效力自裁決、不改 MC 本文）**：**M1 修訂自鎖**——§8 維持原則級門檻不降，§8.5(b)(ii) 判準對治理／定義條款讀為「更完整**實現**五原則之治理落實」，**解鎖而不降門檻**（不以自舉 minor 動作規避 self-entrenchment）；M2 共享憑證↔行動者專屬綁定（P5.W1）；§8.1 拓撲——單一 Steward 期間雙人獨立核准由 Steward＋附則指定之獨立確認者滿足；§8.3 稽核工具輸出保真；§0.3 母集（字母子項屬項次受編號穩定性保護、但不入 102；§5.{n} 屬 102）；F1/F3 權威順序；P3.E1 provisional 二義；P1.E3 主責 Layer 6。〔P5.W4「最小權限」經審查認定已由 §8.3「存疑即不允許」兜底、**無須另立判準**——原稿誤列為解釋項，於此更正；治理附則第 3 條繼任人恆存義務屬 annex minor（附則自身授權範圍內），另行。〕

---

## Appendix G — 自 v1.4 生效後之 §8.1 解釋／§0.5 editorial（不升版）[I]

**RULING-2026-026／AL-2026-029（2026-07-23）**：§8.1 解釋——Agent 協作產物之個別可驗證性（可執行 Python 入口必須載 canonical「**執行指令矩陣**」；細則 `CLAUDE.md` #18／#29）；§0.5 Layer 6 列 editorial 同步。**§8 [N] 本文未動、MC 版本維持 v1.4、102 母集不變**。裁決全文見 `constitution/RULING-2026-026-CMD-MATRIX.md`。

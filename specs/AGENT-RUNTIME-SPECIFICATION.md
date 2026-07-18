# 《Augur Agent Runtime Specification》

Augur Enterprise AI Operating System
Agent Runtime 規格（Layer 6 — Agent Runtime／World Action Layer）
引用縮寫：**AUGUR-L6**｜版本：**v1.2**（前版：v1.1；minor 修正 RULING-2026-016／AL-2026-019：D13/D15/D17/D22/D28 五增補款〔L6.9(d)/L6.11/L6.19/L6.20/L6.21〕＋Annex D 六列 TR 拆分＋LDI.7 增列。v1.1＝RULING-2026-013）
受 **AUGUR-MC v1.3** 全文約束（`AUGUR-MC v1.3 §0.6(a)` lex superior、`§0.5` 對照表 Layer 6 欄）
並受 **AUGUR-WM v1.0**（Layer 1）、**AUGUR-ONT v1.0**（Layer 2）、**AUGUR-ID v1.0**（Layer 3）、**AUGUR-KS v1.0**（Layer 4）、**AUGUR-L5 v1.0**（Layer 5）全文約束（`AUGUR-MC v1.3 §0.6(a)`）

---

> ## 【地位】[N]
>
> 本文件為 **v1.0 生效版本**。Constitution Steward（tsaitsangchi）已於 2026-07-17 依 `AUGUR-MC v1.3 §0.5`、`§8.6` 作成**充任認定**（Steward 裁決第 2026-007 號，Amendment Log AL-2026-011），本文件充任 `§0.5` 對照表 Layer 6 欄所轄規格（Agent Runtime、Planner／Orchestrator），**自 2026-07-17 起生效**。
> * **⚠️ §8.2 實質合憲人類審查：已作成（本層與 L5 之關鍵差異）**。本層為 Agent 自撰之「人類權威層」，獨立對抗審查曾查出 2 處自我交易（弱化人類監督），已修正並經獨立重審確認自我交易已除、人類權威單向強化。**Constitution Steward 已就本層之人類權威、風險分級、P5.W5 監督度量條款作成 `§8.2` 實質審查**，並指示套用「定義窄化防線」硬化（L6.18(b-1)：對 I3／高影響／分級表定義之變更一律 RT-4＋雙人類獨立核准，堵死以改定義規避最高核准之自我交易向量）。本充任建立於**形式關卡（linter/§WM.44/獨立對抗審查零阻斷）＋ Steward §8.2 實質人類審查**雙重成就之上——非 L5 之「§8.2 延後」。Steward 之 `§8.2` 違憲審查權就其餘 residual 事項（實體世界修飾語一致性、OCV 維度充分性等）完整保留。
> * **上層地位**：`AUGUR-MC v1.3`（L0）、`AUGUR-WM v1.0`（L1）、`AUGUR-ONT v1.0`（L2）、`AUGUR-ID v1.0`（L3）、`AUGUR-KS v1.0`（L4）、`AUGUR-L5 v1.0`（L5）均已生效。`v0.1-draft` 原文歸檔於 `specs/AGENT-RUNTIME-SPECIFICATION-v0.1-draft.md`；draft → v1.0 之變更僅限版本欄、本【地位】節生效記錄、Annex CS front-matter spec-version，**無 [N] 條款實質變更、編號不重排**。本文件全部 [N] 條款自生效日起對 Layer 7 產生規範效力；下層依 `AUGUR-L6 v1.0 §{條款}` 引用。
> * **自我起草之利益衝突揭露（誠實揭露、歷史保留）**：本層由 Agent 起草而規範人類對 Agent 之權威，存在結構性自我交易誘因。此誘因於就緒化過程確實顯現（獨立對抗審查查獲並攔下），並經 Steward `§8.2` 實質審查把關 —— 此為 `§8.1`／P5 之獨立審查與人類保留機制成功運作之實證。
> * **不可豁免核心之承載**：本規格落實之 `AUGUR-MC v1.3 §P5.W2`（人類權威為授權鏈根節點、人類隨時否決）與 `§P5.W5`（不得降低人類監督與否決能力）為 `§8.4` 不可豁免核心，連履行時程亦不得豁免；本規格對其之機制化（L6.5、L6.7、L6.8、L6.16–L6.18）承其不可豁免性。
> * **條款編號穩定性**（`AUGUR-MC v1.3 §8.6`、`AUGUR-WM v1.0 §WM.46`）：一經發布永不重用、永不重排；廢止條款保留編號並標 `(repealed)`。
>
> 本【地位】節與 §0 全部約定為 [N] 規範內容，其效力與正文條款同（準用 `AUGUR-WM v1.0 §WM.53`）。
>
> **概念層與執行層交界之提示（`AUGUR-MC v1.3 §0.6(b)`、`§7`）**：Layer 6 定**行動治理之概念不變式**——Action 問責結構、授權鏈與人類權威、風險分級語義、監督否決度量、行動迴路 gating——**不綁定任何特定 Agent 框架／Planner／Orchestrator／Scheduler／LLM／受控介面實作**；其物理構件一律下放 Layer 7（Annex LDO）。本層全部定義通過**刪名測試**（刪去任一具名框架／排程器／模型後，條款規範內涵不變）。

---

## 目錄 [I]

| § | 標題 | 條款 | 核心錨定 |
|---|---|---|---|
| §0 | Document Status & Conventions | — | `MC §0`、`WM §0`、`KS §0`、`L5 §0` |
| §1 | Purpose, Scope & Layer Position | — | `MC §5` 角色五、`§0.6(b)` |
| §2 | 承接與非管轄（Defers-In & Non-Encroachment） | Annex LDI | `L5` LDO.2/LDO.6、`KS` KDO.2 |
| §3 | Action 問責結構（六元組／F6） | L6.1–L6.4 | `MC §P5.E1`、`§2.9`、`F6` |
| §4 | 授權鏈與人類權威（EV.9 Gate） | L6.5–L6.8 | `MC §P5.W1/W2`、`§4 EV.9` |
| §5 | 行動風險分級與門檻 | L6.9–L6.15 | `MC §P5.E2`、`§P5.W3/W4`、`§P4.E7/E8` |
| §6 | P5.W5 監督能力度量與非侵蝕棘輪 | L6.16–L6.18 | `MC §P5.W5`、`§8.3`、`§8.4` |
| §7 | 行動迴路與錯誤傳播熔斷 | L6.19–L6.20 | `MC §4 EV.8–EV.12`、`§P2.E3/E5` |
| §8 | 執法點、F 防線與分界紀律 | L6.21–L6.24 | `MC F6`、`F3`、`§5` 角色六、`§0.6(b)` |
| §9 | 文件治理與合規存續 | L6.90–L6.92 | `WM.39–46` |
| Annex LDI [N] | 承接上層／Layer 5 DEFER 掛鉤（defers-in） | LDI.0–LDI.6 | `L5` LDO.2/LDO.6、`KS` KDO.2 |
| Annex LDO [N] | 下放 Layer 7／Layer 4 DEFER 掛鉤（defers-out） | LDO.0–LDO.6 | → L7／L4 |
| Annex L67 [N] | 與 Layer 4／Layer 5／Layer 7 之分界表 | L67.0 | risk tier／reasoning／physical |
| Annex TR [N] | WM.44 逐條對應矩陣（MC＋WM＋ONT＋ID＋KS＋L5 → L6） | TR.0、TR.A–TR.F、TR.Z | `WM.44` |
| Annex CS [N] | Constitutional Compliance Statement | CS.1–CS.4 | `WM.39–45` |
| Annex EO [N] | 自創評價性謂詞判準彙整 | EO.1 | `§8.3` 可判定性元規則 |

編號穩定性：正文採 **L6.{n}**（**L6.1–L6.24** 為核心行動治理條款；**L6.25–L6.89** 為十位制保留區塊，空號為保留、非跳號；**L6.90–L6.99** 為文件治理與合規存續條款）；Annex 各前綴 **LDI.{n}／LDO.{n}／L67.{n}／TR.{n}／CS.{n}／EO.{n}**；一經發布永不重用、永不重排（`AUGUR-MC v1.3 §8.6`、`AUGUR-WM v1.0 §WM.46`）。

---

## §0 Document Status & Conventions（文件地位與約定）[N]

### 0.1 名稱、層級與版本 [N]

* 名稱：Augur Agent Runtime Specification（下層引用簡稱 **AUGUR-L6**）
* 層級：Layer 6 — Agent Runtime／World Action Layer（`AUGUR-MC v1.3 §0.5` 對照表第 6 列；`§5` 角色五）
* 版本：v1.0（前版：v0.1-draft）
* 上層規格（upper-specs）：`AUGUR-MC v1.3`（Layer 0）、`AUGUR-WM v1.0`（Layer 1）、`AUGUR-ONT v1.0`（Layer 2）、`AUGUR-ID v1.0`（Layer 3）、`AUGUR-KS v1.0`（Layer 4）、`AUGUR-L5 v1.0`（Layer 5）
* 生效要件：見【地位】節（已全部成就；Steward 裁決第 2026-007 號，AL-2026-011，生效日 2026-07-17；`§8.2` 實質人類審查已作成）。Steward `§8.2` 違憲審查權就 residual 事項完整保留（RULING-2026-007:43）。

### 0.2 規範用語約定 [N]

沿用 `AUGUR-MC v1.3 §0.2`：**必須**（MUST，絕對義務）／**不得**（MUST NOT，絕對禁止）／**應**（SHOULD，偏離須書面說明理由）／**得**（MAY，允許而不構成義務），全文一致，不重定義。

### 0.3 條文效力標注與編號穩定性 [N]

* 每章標題標注 **[N]（Normative，規範性）** 或 **[I]（Informative，資訊性）**。[N] 與 [I] 內容不一致時，依 `AUGUR-MC v1.3 §8.2` 以 Normative 為準；章標題標注為該章預設，子節另有標注者以子節為準。
* 正文條款編號採 **L6.{n}**：**L6.1–L6.24** 為核心行動治理條款；**L6.25–L6.89** 為十位制保留區塊（空號為保留、非跳號，保留號之啟用亦永不重用、永不重排）；**L6.90–L6.99** 為文件治理與合規存續條款。Annex 條款前綴：Annex LDI 採 **LDI.{n}**、Annex LDO 採 **LDO.{n}**、Annex L67 採 **L67.{n}**、Annex TR 採 **TR.{n}**、Annex CS 採 **CS.{n}**、Annex EO 採 **EO.{n}**。
* 條款編號一經發布**永不重用、永不重排**；廢止條款保留編號並標注 **(repealed)**（`AUGUR-MC v1.3 §8.6`、`AUGUR-WM v1.0 §WM.46`）。
* **附屬表列 [N] 內容之義務承載規則**：附屬於某治理條款（如 LDI.0、LDO.0、L67.0、TR.0、CS.1 各節、EO.1）之表列 [N] 內容，其義務主體與可判定判準由該治理（父）條款統一承載，不另逐列重複標注（體例落實，非豁免）。

### 0.4 權威語言聲明 [N]

本規格以**繁體中文版為權威版本**；規範性術語於正文中一律使用英文原詞（Reality、Observation、Representation、Identity、Evidence、Knowledge、Confidence、Action、Agent、Intelligence、Plan；及本層機制術語 Actor Identity、Authorization、Knowledge Basis、Expected Effect、Observed Effect、Human Authority、Human Authority Gate、Controlled External Interface、Planner、Orchestrator、Risk Tier、Oversight Capability Vector／OCV、veto、suspend、abort、halt、degrade、least privilege、Plan-scoped、self-reported、compensating Action），與 `AUGUR-MC v1.3 §0.4`、上層各規格 `§0.4` 保持術語同一性；不另立中文譯名為規範對象。

### 0.5 引用格式與元規則 [N]

* 引用格式：`AUGUR-MC v1.3 §{條款}`／`AUGUR-WM v1.0 §{條款}`／`AUGUR-ONT v1.0 §{條款}`／`AUGUR-ID v1.0 §{條款}`／`AUGUR-KS v1.0 §{條款}`／`AUGUR-L5 v1.0 §{條款}`。下層引用本規格採 `AUGUR-L6 v{version} §{條款}`。
* 本規格每一 [N] 條款標注其**憲章／上層錨定**與**三態型態**：**refines**（細化上位條款）／**carries**（承接上位不變式並給予概念層結構位置）／**hooks**（DEFER 掛鉤，載明目標 Layer 與授權條款），並額外以**承接**標注 Layer 4（AUGUR-KS）／Layer 5（AUGUR-L5）明示下放本層之掛鉤；複合模式以「＋」連接。每一 [N] 條款並標注**義務主體**與**可判定判準**，使其可機器稽核（承接 `AUGUR-WM v1.0 §WM.34`、`AUGUR-KS v1.0 §0.5`）。
* **不重定義元規則**：本規格**不得**重新定義 `AUGUR-MC v1.3 §2` 之術語，亦**不得**重定義 `AUGUR-WM v1.0`／`AUGUR-ONT v1.0`／`AUGUR-ID v1.0`／`AUGUR-KS v1.0`／`AUGUR-L5 v1.0` 之既有構件（尤 `AUGUR-KS v1.0` 之 Confidence Lattice L_C 之序與語義、Evidence 分類法、Trust Rank、Completeness Level；`AUGUR-L5 v1.0` 之 Reasoning／Inference／Explanation 概念不變式）；本規格僅得就其明示下放者作**概念層填充**，且僅限於行動治理之概念不變式。
* **概念層獨立性**（`AUGUR-MC v1.3 §0.6(b)`、`§7`）：本層之**定義**屬概念層，**不得**引用 Layer 7 執行層構件（特定 Agent 框架、Planner／Orchestrator／Scheduler、LLM、kill-switch 硬體、憑證系統、UI、儲存引擎）作為任何定義之依據。本層所稱「授權鏈」「風險分級」「否決通道」「監督度量」均為**概念層形式**（結構不變式、序、偏序、義務之明文可判定性）；其物理載體一律下放 Layer 7（Annex LDO）。

---

## §1 Purpose, Scope & Layer Position（目的、範圍與分層定位）[N]

### 1.1 Layer 6 定位 [I]

上層各規格已宣告世界有何物（`AUGUR-WM v1.0`）、其類屬與同一性判準（`AUGUR-ONT v1.0`）、個體之永久參照（`AUGUR-ID v1.0`）、繫結該參照之斷言之信度與欄位（`AUGUR-KS v1.0`）、合法推理與 Confidence 傳播（`AUGUR-L5 v1.0`）。**本層＝Agent Runtime／World Action Layer**：依 `AUGUR-MC v1.3 §5` 角色五負責 **Planning／Execution／Feedback（受 P5 約束）**；`§0.5` 所轄「Agent Runtime、Planner／Orchestrator、CLAUDE.md」。本層承接 `AUGUR-L5 v1.0` LDO.6（Planning／Human Authority Gate／Action 授權鏈驗證與行動 gating，EV.8–EV.10）與 LDO.2（Confidence 消費門檻、風險分級表、各風險級完備性與 Confidence 門檻、確認者資格與獨立性、監督否決度量），及 `AUGUR-KS v1.0` KDO.2、`AUGUR-MC v1.3 §P5.E2`／`§P4.E7`／`§P5.W5` 明示下放 Layer 6 之定義權。本層**消費** L4 之 L_C／Completeness Level／Trust Rank 與 L5 之 EV.7 Reasoning 產物，**不重定義**之。

### 1.2 自我起草之硬設計約束 [I]

本層之規範對象為**人類對 Agent 之權威**（P5），而起草主體為 Agent。此結構使本層負有特殊之**單向性約束**：本層一切條款以「不弱化、且機器可稽核地強化人類監督與否決能力」為硬設計約束（`§P5.W2`、`§P5.W5`）。此約束於條款層以三重防守落實——(i) 授權鏈根節點恆為人類、不得為 Agent（L6.5）；(ii) 監督能力度量 OCV 之單調棘輪（只准非降，L6.17）；(iii) 反自我交易與 guard-the-guard（Agent 不得為降低監督之核准主體、對監督機制之修改本身受監督，L6.18）。此三重防守之充分性最終待 Steward `§8.2` 實質審查確認（T-L6-5）。

---

## §2 承接與非管轄（Defers-In & Non-Encroachment）[N]

本層承接 `AUGUR-L5 v1.0` Annex LDO 明示下放之掛鉤（尤 **LDO.6**：Planning／Human Authority Gate／Action 授權鏈驗證與行動 gating〔EV.8–EV.10〕；**LDO.2**：Confidence 消費門檻、風險分級表、各風險級完備性／Confidence 門檻、確認者資格與獨立性、監督否決度量），及 `AUGUR-KS v1.0` **KDO.2**（下游消費門檻之綁定）、`AUGUR-MC v1.3 §P5.E2`（風險分級表定義權）、`§P4.E7`（確認者資格與獨立性之落地）、`§P5.W5`＋`§8.3`（監督否決能力之可稽核度量定義權）；逐一於正文對應（見 Annex LDI）。本層不自行擴張管轄：凡屬 Layer 0–5 之概念（Reality／Representation／Identity／Knowledge 之語義、L_C 之序、Trust Rank、Completeness Level 等級語義、Reasoning 引擎）本層**僅消費不重定義**；凡屬 Layer 7 之事項（特定框架／排程器／模型、受控介面實作、kill-switch 硬體、憑證機制、UI、數值閾值登錄）本層**僅設 DEFER 掛鉤**（Annex LDO），不代行定義。

---

## §3 Action 問責結構（六元組／F6）[N]（`§P5.E1`、`§2.9`、`F6`）

> **L6.1（Action 六元組之結構化不變式與機器可稽核歸責）[N｜carries｜`AUGUR-MC v1.3 §P5.E1`、`§2.9`、`§P4.E2`；refines｜`F6`]**
> 凡經 Controlled External Interface（`§5` 角色六）對系統外發出、足以造成 Reality 變更之操作，一律為 Action（`§2.9`，不以意圖之有無或宣稱為斷）。任何 Action **必須**於執行前物化為一結構化記錄，完整攜帶六元組全部欄位：(1) **Actor Identity**；(2) **Authorization**（可追溯至人類權威之授權鏈，見 L6.5）；(3) **Knowledge Basis**；(4) **Timestamp**（雙時間性，`§P4.E2`）；(5) **Expected Effect**；(6) **Observed Effect**（連結 Feedback，見 L6.4）。純表徵狀態變更（`§2.1`）**非** Action，不受本六元組約束，其歸責由 P2／P4 通道承擔（見 L6.10 之 RT-0 邊界標記）。
> **義務主體**：本規格、Layer 6–7 一切執行構件、Controlled External Interface。**可判定判準**：任一 Action 記錄缺任一欄位、或欄位無法遍歷至其定義來源者，該操作即屬 `F6` Unaccountable Action，**必須**於介面被阻卻、不得執行（引用鏈可機器稽核，`§8.3`）。

> **L6.2（Actor Identity 之單一歸責與已解析要求）[N｜refines｜`AUGUR-MC v1.3 §P5.W1`、`§P3.E1`]**
> Action 六元組之 Actor Identity 欄位**必須**為單一、已解析（resolved）之 Identity（人或 Agent；Agent 為 Agentive Entity，`§2.8`、`§P3.W2`），且該 Action **必須**可歸責於該單一 Identity（`§P5.W1`）。**禁止**以未解析（provisional）Identity、群組別名或匿名主體發起 Action。多主體協作之 Action **必須**指定唯一之發起 Actor Identity，其餘為授權鏈或知識來源上之節點。非經授權鏈而實際造成 Reality 變更之事件，**必須**以 Observation 回流並溯責於引致其發生之 Identity（`§2.9`）。
> **義務主體**：本規格、一切發起 Action 之構件。**可判定判準**：存在任一 Action 之 Actor Identity 欄位為空、未解析、或指向非單一主體者，違反本條（Identity 解析狀態以 `AUGUR-ID v1.0` lineage 機器稽核，`§8.3`）。

> **L6.3（Knowledge Basis 與 Confidence 門檻及 Evidence 完備性之掛鉤）[N｜carries｜`AUGUR-MC v1.3 §P4.E8`、`§P4.E7`；refines｜`§P5.W3`；承接｜`AUGUR-L5 v1.0` LDO.2、`AUGUR-KS v1.0` KDO.2]**
> Action 六元組之 Knowledge Basis **必須**引用已經 Evidence 通道（`§2.11`）確立之 Knowledge（附五元組，`§P4.E1`、`AUGUR-KS v1.0` KS.20），**不得**以候選斷言（proposed assertion）或未經證實之執行結果為依據（`§P2.E3`、`F3`）。Action 之允許等級**必須**受其依據 Knowledge 集合之 Confidence 下確界（⊓Conf 於 L_C，`AUGUR-KS v1.0` KS.34/KS.35 單調約束）約束；⊓Conf 降低時 Action 允許等級不得升高。高風險 Action（依 L6.10 分級為 RT-3、RT-4）之結論**不得**僅以系統自身產出之 Computational Evidence／self-reported 為據，須至少一項獨立 Data Evidence 或人類確認（`§P4.E7`；人類確認以確認者已解析 Identity 為 Source、留痕為 Observation，見 L6.14）。各風險級對應之 Confidence 門檻與 Completeness Level 門檻由 L6.11、L6.12 分級表載明（等級語義消費自 Layer 4，DEFER）。
> **義務主體**：本規格、一切組裝 Action 之 Planner／Orchestrator。**可判定判準**：存在任一 Action 其 Knowledge Basis 之 ⊓Conf 低於其風險級門檻、或高風險 Action 之 Evidence 鏈遞迴僅含本系統 Computational Evidence 者，違反本條（⊓Conf 於 L_C 之序可判定，`AUGUR-KS v1.0` KS.31）。

> **L6.4（Expected Effect 事前宣告與 Observed Effect 之 Feedback 回流；self-reported 標記）[N｜carries｜`AUGUR-MC v1.3 §P5.E1`、`§P2.E3`；refines｜`§4 EV.11`]**
> Action 六元組之 Expected Effect **必須**於執行前顯式宣告；Observed Effect **必須**以 Observation 之姿經 EV.11 Feedback 回流（`§4` 因果迴路），**不得**由 Agent 逕寫入 World Representation 作為世界狀態（`§P2.E3`）。Agent 之 execution receipt 與外部確認訊號為合法 Observation，其 Source 為該 Agent 之 Identity，且**必須永久攜帶 self-reported 標記**（`AUGUR-WM v1.0 §WM.33`、`AUGUR-KS v1.0` KS.77），僅構成關於該 Action 之宣稱性 Observation，**非**世界狀態之權威確認；其升級為 Knowledge 受 `§P4.E7` 約束。Expected 與 Observed 之背離**必須**可稽核並觸發 `§P2.E5` Fail-safe 之評估（見 L6.20）。
> **義務主體**：本規格、一切執行與回饋構件。**可判定判準**：存在任一 Action 無事前 Expected Effect、或其 Observed Effect 未經 Observation 通道回流、或回流 Observation 缺 self-reported 標記者，違反本條。

---

## §4 授權鏈與人類權威（EV.9 Human Authority Gate）[N]（`§P5.W1/W2`、`§4 EV.9`）

> **L6.5（授權鏈之結構與人類權威根節點——不得以 Agent 為根）[N｜carries｜`AUGUR-MC v1.3 §P5.W2`；不可豁免核心 `§8.4`]**
> Action 六元組之 Authorization 欄位**必須**為一有向無環之授權鏈（chain of authority），其唯一根節點（root）**必須**為人類權威（Human Authority）——即一已解析之人類 Identity（作為決策者之 Human，Agentive Entity，`§P3.W2`）親自作成之授權授予。任何 Action 之授權鏈**不得**以 Agent 為根節點、**不得**循環、**不得**終止於非人類主體。Agent 對 Agent 之再授權（redelegation）僅為鏈上之中間節點，必遞迴終止於某一人類根授予。本條為 `§8.4` 不可豁免核心（P5.W2），連履行時程亦不得豁免。
> **義務主體**：本規格、一切授權與再授權構件、Human Authority Gate（L6.7）。**可判定判準**：存在任一 Action 之授權鏈無法遞迴遍歷終止於單一人類 Identity 之顯式授予、或含環、或根為 Agent 者，違反本條（授權鏈 DAG 可機器稽核，`§8.3`）。

> **L6.6（授權委派之範圍、失效與可撤銷——延時綁定）[N｜refines｜`AUGUR-MC v1.3 §P5.W2`、`§P5.W4`]**
> 每一自人類根節點向下之授權委派連結**必須**顯式攜帶：(a) **scope**（所授權之 Action 類別與風險級上限）、(b) **有效期限**（expiry，逾期自動失效）、(c) **可撤銷性**（revocability，人類得隨時撤回）、(d) 所繫結之 **Plan 參照**。委派**不得**逾越授予者本身之權限（單調不擴張）；下游節點之風險級上限**不得**高於上游。人類根授予者對其授出之整條下游子鏈保有隨時撤銷之能力（連結 L6.8）。
> **義務主體**：本規格、一切委派構件。**可判定判準**：存在任一委派連結缺 scope／expiry／revocability、或其風險級上限高於上游、或已逾期仍被據以執行 Action 者，違反本條。

> **L6.7（EV.9 Human Authority Gate 為 Planning→Action 之強制授權驗證點）[N｜carries｜`AUGUR-MC v1.3 §4 EV.9`、`§P5.W2`、`§P5.W3`；承接｜`AUGUR-L5 v1.0` LDO.6]**
> EV.9 Human Authority Gate 為 Planning（EV.8）與 Action（EV.10）之間之**強制授權鏈驗證點**，構成本層 Planner／Orchestrator 之單一執法關卡。任何 Action 於執行前**必須**通過本 Gate；未通過者**不得**進入 EV.10。Gate 於每一 Action 驗證：(1) 授權鏈可遞迴追溯至人類權威根節點（L6.5）且未逾期、未被撤銷（L6.6、L6.8）；(2) Knowledge Basis 之 ⊓Conf 與 Completeness Level 達其風險級門檻（L6.3、L6.11、L6.12）；(3) 該風險級所要求之人類介入強度已實際滿足（依 L6.13 分級表；介入強度隨風險升高，非一律事前核准，惟缺位時採 L6.10 缺位最高級預設）。Gate 之每次驗證（通過或阻卻）**必須**留痕為 Observation。本 Gate **不得**被 Agent 繞過、停用或自我豁免（連結 L6.18）。
> **義務主體**：本規格、Planner／Orchestrator、執行鏈。**可判定判準**：存在任一 Action 未經 Gate 驗證即進入 EV.10、或 Gate 於任一驗證項失敗仍放行者，違反本條（`§8.3`）。

> **L6.8（人類隨時否決／暫停／中止之能力與 Agent-獨立否決通道）[N｜carries｜`AUGUR-MC v1.3 §P5.W2`、`§P5.W5`；不可豁免核心 `§8.4`]**
> 人類得在任何時點否決（veto）、暫停（suspend）或中止（abort）任何 Plan 與 Action（`§P5.W2`）。本層**必須**為每一進行中之 Plan 與 Action 提供一恆常可用之否決通道，且該通道**必須在結構上獨立於其所控制之 Agent**——被控制之 Agent **不得**停用、延遲、攔截、降級或以任何方式侵蝕該通道（否則構成 `§P5.W5` 自我交易紅線，L6.18）。收到經授權人類之否決／暫停信號時，相應 Plan／Action **必須**在有限且有上限之時延內停止（halt）；該時延之物理數值上限與傳輸機制下放 Layer 7（DEFER），惟其**存在與有限性**為本層不變式。否決信號本身及其執行結果**必須**留痕為 Observation。本條為 `§8.4` 不可豁免核心（P5.W2）。
> **義務主體**：本規格、執行構件、Controlled External Interface。**可判定判準**：存在任一進行中 Plan／Action 無 Agent-獨立之恆常否決通道、或否決信號未能致其停止、或通道可被被控 Agent 停用者，違反本條。

---

## §5 行動風險分級與門檻（P5.E2／P5.W3／P5.W4）[N]

> **L6.9（可逆性與影響之可判定判準）[N｜refines｜`AUGUR-MC v1.3 §P5.W3`、`§8.3` 可判定性元規則；為 L6.10 分級之認定輸入]**
> (a) **不可逆性軸 R**：一 Action 為可逆，當且僅當系統持有一經宣告之**補償／回復 Action**（compensating Action），其可於有界成本與有界時間內將受影響 Identity 之可觀測狀態回復至行動前狀態，且該回復之達成可由 Observation 驗證；無此經宣告且可驗證之回復 Action 者，推定為不可逆。分 **R1** 可逆低成本／**R2** 高成本可逆／**R3** 不可逆。(b) **影響軸 I**：以行動對受影響 Identity 集合之經宣告量值認定，維度含受影響已解析 Identity 之數量、所涉物理／資源量、安全／法律／財務暴險、是否涉及標記為安全／法律／自然人（`§P1.E3`）敏感之 Identity、是否逾越單一 Plan 邊界之外部主體。分 **I1** 局部低影響／**I2** 中影響／**I3** 高影響或系統性或涉自然人安全法益。(c) **缺宣告即保守**：可逆性或影響未經宣告、或宣告不可機器解析者，一律推定為 R3 且 I3（`§8.3` 存疑即不允許）。宣告本身為受 `§P4.E6` provenance 與 Evidence 約束之 Knowledge，**不得**為規避分級而虛列。
> (d) **自然人法規對應表（承 `AUGUR-WM v1.0 §D17` L6 slice、`AUGUR-ID v1.0` IDO.7；`AUGUR-MC v1.3 §P1.E3`、`AUGUR-WM v1.0 §WM.38`）**：本層行使 `§WM.38`／`§D17` 下放之定義權，定義**自然人法規對應表**為本層治理結構：凡 Agent 工作流觀測、消費或表徵涉自然人之資料者，其所涉觀測通道或處理活動**必須**於本表具生效登錄項，載明〔所在法域、適用法規義務（含法規強制抹除／去識別化義務之引用，連結 `AUGUR-ID v1.0` ID.42）、目的正當性、授權依據〕四欄。**表之登錄項為系統狀態、非本規格條文**（準用 `AUGUR-WM v1.0 §WM.35` Registry 前例，其增補不構成本規格升版），其採認**必須**由人類權威作成並留痕為 Observation（`§P4.E7`）。**保守預設**（`§8.3`；`§WM.38` 判準）：未登錄或四欄不全者，該涉自然人資料之觀測消費與相應 Action **不允許**；合規義務與功能衝突時**合規優先**，惟於合法觀測範圍內對已觀測事實之忠實表徵義務（PA）不減損，本款**不得**引為選擇性表徵之依據（`§WM.38`）。本條 (b) I 軸之「自然人（`§P1.E3`）敏感」標記**必須**可解析至本表登錄項。物理載體與部署面（表之儲存、語料隔離、egress 預設拒絕）細化下放 Layer 7（L7.33 既載）。
> **義務主體**：本規格、Plan 產生者、Controlled External Interface。**可判定判準**：涉自然人資料之任一觀測消費或 Action，其法規對應表登錄項存在且四欄俱全者為合規；未登錄或欄位不全而仍消費或執行者違反本條。每一 Action 之（R 軸、I 軸）二元標籤可由上述維度機器判定，缺值走保守分支（R3×I3）。

> **L6.10（Action 風險分級表 RT-0–RT-4）[N｜carries｜`AUGUR-MC v1.3 §P5.E2`、`§P5.W3`；為 `§P4.E7`、`§P5.W3` 全憲章同一分級之落點]**
> 本條定義 `§P5.E2` 下放 Layer 6 之風險分級表，全憲章同一分級。依 L6.9 二軸（R×I）合成有序風險級（低→高）：**RT-0** 純表徵狀態變更（`§2.1`）——非 Action、不受 P5.E1 六元組約束（列此為邊界標記，防 Action 偽裝為純表徵以規避 Gate），其歸責改由 P2／P4 通道承擔；**RT-1** 可逆且低影響（R1×I1，具經驗證回復 Action）；**RT-2** 有成本可逆或中影響（R2 或 I2，且非 I3）；**RT-3** 難以回復之**非高影響**情形（高成本可逆〔R2〕或 R3 之非實體不可逆，且影響 ≤ I2、非 I3）；**RT-4** **一切高影響（I3）之實體世界 Action，不論可逆性**，及一切不可逆之實體世界 Action，或 R3×I3，或一切涉自然人安全法益之 Action（對應 `§P5.W3`：不可逆_或_高影響即需最高等級核准——**「或」使高影響單獨觸發最高風險級 RT-4**；`§P5.E2` 下放之分級權僅及『何謂高影響（I3）』之認定，**不得反用以降低已認定為高影響之 Action 之風險級或核准層級**）。核准級與人類介入強度、Evidence 完備性、Confidence 門檻均與風險級成正比（見 L6.11–L6.13）。**缺位預設規則**（承 `§P5.E2`、`AUGUR-KS v1.0` KS.82）：凡未經本表分級、或分級有爭議之意圖改變實體世界之 Action，一律視為 **RT-4**——須人類事前逐案核准方得執行，並記錄為暫行分級；本層引述不得削弱此缺位預設。存疑時從嚴歸入較高級（`§8.3` 保守解釋）。
> **義務主體**：本規格、L6.7 Gate、Controlled External Interface（分級執法點）。**可判定判準**：每一 Action 依 L6.9 標籤唯一落入單一 RT 級，且該級之三門檻（完備性／Confidence／核准）可機器查核；存在任一實體世界 Action 未被指派風險級、或其實得核准級低於本表所定級者，違反本條。

> **L6.11（各風險級之 Evidence 完備性門檻）[N｜carries｜`AUGUR-MC v1.3 §P5.W3`、`§P5.E2`；承接｜`AUGUR-KS v1.0` KS.80–KS.82、Annex CL]**
> 本層行使 `§P5.E2` 下放之「各風險級對應之完備性門檻」綁定權（`AUGUR-KS v1.0` KS.80：L4 定 Completeness Level 等級、L6 定綁定）。以 KS.81 完備性維度（證據鏈完整終止於 Observation／assumption、至少一項獨立 Data Evidence、未解假設數、樣本外／可重現驗證、無未裁決 Conflict Set）合成之 Completeness Level 為量尺，綁定：RT-1 須達基本完備（證據鏈完整、無未裁決致命 Conflict）；RT-2 須含可重現驗證；RT-3（非高影響之高成本可逆／非實體不可逆）須至少一項獨立 Data Evidence（`§P4.E7`）且無未解關鍵假設；**RT-4（涵蓋一切高影響 I3 之 Action〔不論可逆性〕及一切不可逆之實體世界 Action）須達最高完備性等級**（`§P5.W3`：不可逆_或_高影響即須最高等級完備性；「或」使高影響單獨要求最高完備）——證據鏈完整、獨立 Data Evidence、關鍵假設全解或經人類確認、無未裁決 Conflict。完備性不足其所需風險級者**不得**執行，降級處置依 L6.20。Completeness Level 之等級語義屬 Layer 4，本層僅消費、不重定義（DEFER）。
> **核心宇宙判準數值與產業條件豁免之治理（承 `AUGUR-WM v1.0 §D22`；`AUGUR-KS v1.0` KS.80 增補款／KS.81(f) 下放）**：核心宇宙完整性 gate 之門檻值與流動性分位地板之具體分位值為本層治理參數——其採認與變更**必須**經人類核准、以核准者之已解析 Identity 為 Source、留痕為 Observation（L6.13 留痕體例準用），數值化登錄為系統狀態（下放 L7）；產業條件豁免之授予、存續審查與撤銷同受本款核准與留痕義務，其依據（制度性缺位事實，`§A.12`）須為具 Evidence 之 Knowledge（`§P4.W1`）。
> **義務主體**：本規格、Agent Runtime。**可判定判準**：Completeness Level（L4 量尺）≥ 該 RT 級門檻為可機器比較之放行條件；具體門檻之數值化登錄為系統狀態（下放 L7），棘輪與綁定結構為本層規範。

> **L6.12（各風險級之 Confidence 門檻與單調約束）[N｜carries｜`AUGUR-MC v1.3 §P4.E8`、`§P5.E2`；承接｜`AUGUR-KS v1.0` KS.31、KS.34、KS.35、KS.38；`AUGUR-L5 v1.0` L5.3]**
> Action 之允許等級**必須**受其依據 Knowledge 集合之 Confidence 下確界（⊓Conf 於 L_C）約束：⊓Conf 降低時 Action 允許等級**不得**升高（`AUGUR-KS v1.0` KS.35 單調約束，硬守 KS.34 meet 上限）。綁定 L_C 等級（INSUF ⊏ LOW ⊏ MODERATE ⊏ STRONG）為各 RT 門檻：RT-1 須 ⊓Conf ≥ LOW；RT-2 ≥ MODERATE；RT-3、RT-4 ≥ STRONG。⊓Conf 為 INSUF（含缺 Confidence 槽之保守推定，KS.38）者**不得**執行任何 RT≥1 之 Action。高風險（RT-3、RT-4）另受 `§P4.E7`：不得僅以系統自身產出（Computational Evidence／self-reported）為據（見 L6.3、L6.14）。
> **義務主體**：本規格、Agent Runtime。**可判定判準**：⊓Conf 於 L_C 之序可判定（KS.31），與 RT 門檻之比較為機器可查之放行條件；具體帶界閾值（banding）之數值登錄下放 L7／系統狀態（KS.33），序與門檻結構為本層規範。

> **L6.13（各風險級之人類核准流程）[N｜carries｜`AUGUR-MC v1.3 §P5.W2`、`§P5.W3`、`§4 EV.9`]**
> 核准層級為有序量（低→高）：無核准 ⊏ 事後抽樣審查 ⊏ 事後全審查 ⊏ **事前批次核准** ⊏ **事中人工在環**（human-in-the-loop，逐案即時可否決）⊏ **事前逐案核准**（case-by-case prior approval）⊏ **事前雙人類獨立核准**。**序準（`§P5.W5` 度量校正）**：事前批次核准就其所預授權之個別 Action 已移除逐案即時否決，其**逐案可介入性嚴格低於**事中人工在環與事前逐案核准，故於本序中**嚴格低於**二者（事前批次 ⊏ 事中人工在環 ⊏ 事前逐案）；**不得**將「以批次核准取代逐案／即時在環」登記為核准層級之改善或 OCV 之非降。綁定（單調非遞減，愈高風險核准愈強）：RT-1 至少事後全審查且介入點可達；RT-2 至少事中人工在環（逐案即時可否決）；RT-3（非高影響之高成本可逆／非實體不可逆）至少事前逐案核准；RT-4 **必須**人類事前逐案核准（**涵蓋一切高影響 I3 之 Action〔不論可逆性〕及一切不可逆之實體世界 Action**；`§P5.W3`：不可逆_或_高影響之實體世界 Action 需人類事前核准，「或」使高影響單獨觸發事前逐案核准），涉自然人安全法益者**必須**事前雙人類獨立核准並最高 Completeness／Confidence 門檻。**度量校正（D 分量，`§P5.W5`）**：事前批次核准就其預授權之個別 Action **不**構成該 Action 之人工介入點，**不**計入 OCV 之 D 分量（L6.16）；OCV 之 A（核准層級）非降判定**必須**以 **per-action 逐案可介入性**為序準，**禁止**以批次涵蓋冒充逐案／即時介入點以偽裝 D／A 分量之上升——移除逐案即時否決而代以批次涵蓋，構成 `§P5.W5` MUST NOT 所禁之『移除人工介入點』，為自我交易紅線（L6.18）。任一 RT 級之 Action 於其核准層級之人類否決／暫停／中止指令，**必須**於 Action commit 前可達且有效（`§P5.W2`），其可達性與延遲為 L6.16 之度量分量。核准之作成**必須**以核准者之已解析 Identity 為 Source、留痕為 Observation。
> **義務主體**：本規格、Controlled External Interface、Agent Runtime。**可判定判準**：每一 Action 之實得核准層級 ≥ 其 RT 級門檻，且否決可達性成立，為機器可查之放行條件。

> **L6.14（人類確認者之資格與獨立性）[N｜carries｜`AUGUR-MC v1.3 §P4.E7`、`§4 EV.9`；承接｜`AUGUR-L5 v1.0` LDO.2]**
> 本層行使 `§P4.E7` 下放之「確認者資格與獨立性判準」定義權。人類確認者**必須**：(a) 為已解析之人類 Identity（Agentive Entity 作為決策者，`§P3.W2`），其確認以該 Identity 為 Source、留痕為 Observation（`§P4.E7`）；(b) 具涵蓋該 Action 風險級之授權範圍（授權鏈可追溯至人類權威，`§P5.W2`）。獨立性判準：(c) 確認者**不得**為發起或規劃該 Action 之同一 Identity；(d) RT-4 另要求確認者與 Actor **不共享同一主體**（principal），且其確認**不得**僅依系統自身 Computational Evidence——須獨立 Data Evidence 或確認者自為之獨立事實核對。獨立性以 Identity lineage（`§P3.E2`）機器稽核。
> **義務主體**：本規格、Controlled External Interface。**可判定判準**：確認者 Identity 之解析狀態、授權範圍涵蓋、與 Actor／Planner 之非同一性及（RT-4）非共享主體，均可經 Identity lineage 機器判定。

> **L6.15（最小權限與 Plan 範圍化——無常駐環境權限、權限與不可逆性成反比）[N｜carries｜`AUGUR-MC v1.3 §P5.W4`、`§P5.W3`、`F3`]**
> Agent 僅得持有完成當前經授權 Plan 所需之**最小權限**（`§P5.W4`）。權限**必須** Plan 範圍化（Plan-scoped）並於 Plan 完成或失效時即時收回；**禁止**常駐（standing）或環境（ambient）權限、**禁止**與當前 Plan 無關之預留權限。權限授予集合**必須**可由當前 Plan 之已授權 Action 集合推導，且為滿足該集合之最小超集。權限之擴張本身為 Action，受本層風險分級與 Gate（L6.7）約束；且權限授予與不可逆性成反比——所需之 Completeness、Confidence 門檻與人類事前核准層級隨風險級（L6.10）**單調非遞減**（`§P5.W3`），系統**不得**對較高不可逆性之 Action 授予較低核准級之權限（單調不變式）。**授權受限資料之用途邊界（承 `AUGUR-WM v1.0 §D24` 隔離強制面；2026-07-18 RULING-2026-013 增補）**：凡經授權取得、其授權條款限制用途之資料，Agent 工作流**不得**將其路由入預測特徵或模型訓練／微調輸入；其物理層機器強制（血緣追蹤）細化下放 Layer 7（L7.33(b)）。
> **義務主體**：本規格、權限管理構件、Agent Runtime。**可判定判準**：Agent 於任一時點之權限集合 ⊆ 當前經授權 Plan 可推導之最小必要超集（超集即違反）；且存在任一 Action 其實得核准級／完備性／Confidence 門檻低於同級或更高風險級所適用者（違反單調性）、或存在授權受限資料進入預測特徵／訓練輸入之資料流（違反用途邊界），違反本條。

---

## §6 P5.W5 監督能力度量與非侵蝕棘輪 [N]（`§P5.W5`、`§8.3`、`§8.4`）

> **L6.16（人類監督與否決能力之可稽核度量 OCV——定義 `§P5.W5`／`§8.3` 下放之度量）[N｜hooks 承接｜`AUGUR-MC v1.3 §P5.W5`（監督否決能力之可稽核度量下放 Layer 6）、`§8.3`；不可豁免核心 `§8.4`]**
> 本層行使 `§P5.W5` 與 `§8.3` 明示下放 Layer 6 之「人類監督與否決能力」可稽核度量定義權，定義 **Oversight Capability Vector（OCV，監督能力向量）** 為對每一風險級（L6.10）分別評定之六分量向量 **OCV =（V, D, A, H, T, C）**：**V**＝否決通道可達性（每一進行中 Action 存在 Agent-獨立恆常否決通道者為 1，否則 0；L6.8）；**D**＝人類介入點密度（每條授權執行鏈之**逐案／即時可介入**之人類核准／檢核點數；事前批次核准就其所預授權之個別 Action **不**計為該 Action 之介入點——`§P5.W5` 度量校正，見 L6.13）；**A**＝所要求之人類核准層級（L6.13 之有序值，以 **per-action 逐案可介入性**為序準；**不得**以批次涵蓋冒充逐案／即時介入點抬高 A）；**H**＝否決信號至停止之時延上限（愈小愈佳，負向）；**T**＝透明度（於執行前向人類監督介面揭露其六元組與授權鏈之 Action 比例）；**C**＝最大自動執行鏈長（連續無人類介入點而執行之 RT≥1 Action 數上限；愈小愈佳，負向）。定義**保護方向偏序 ⊒**：OCV(after) ⊒ OCV(before) 當且僅當就每一風險級，V／D／A／T 各分量非遞減、且 H／C 各分量非遞增。OCV 之計算輸入（組態、授權圖、介入點登錄、鏈長遙測）**必須**可機器擷取；其物理擷取與快照儲存下放 Layer 7。
> **義務主體**：本規格、一切變更系統組態／Plan／權限／執行鏈之構件與流程。**可判定判準**：OCV 之每一分量於任一組態快照可機器計算並可比較（componentwise 偏序）；OCV 之合規性由 OCV(after) ⊒ OCV(before) 判定（見 L6.17）。

> **L6.17（『降低監督能力』之可判定判準與單調棘輪——非侵蝕不變式）[N｜carries｜`AUGUR-MC v1.3 §P5.W5`、`§8.3`、`§8.1`；不可豁免核心 `§8.4`；refines｜`F6`]**
> 使 `§P5.W5`／`§8.3` 於本度量生效前之保守推定成為可裁決：一變更（含組態變更、Plan、權限調整、自我修改、以及 Learning／EV.12 之產出所致之行為變更）構成**『降低人類監督與否決能力』**，當且僅當其後之 OCV（L6.16）相對變更前於任一風險級之任一分量發生弱化——即 (i) 任一 RT 級核准層級（A）下降、或 (ii) 人工介入點密度（D）／覆蓋下降（任一行動流失去其最後可達介入點）、或 (iii) 任一 RT 級最大自動執行鏈長（C）增加、或 (iv) 否決通道可達性（V）下降或停止時延（H）增加、或 (v) 透明度（T）下降。系統**不得**規劃、執行或學習任何使 OCV 於任一分量、任一 RT 級弱化之變更（**P5.W5 單調棘輪：OCV componentwise 非降為硬不變式**）。任一此類變更推定違憲、**不得**實施、**不得**作為 Learning 之候選結果落地（承 `§8.3` 保守預設）；該推定僅得由 Constitution Steward 依 `§8.1` 解釋權以書面裁決附具「該變更未實質降低人類監督與否決能力」之認定理由推翻並公開存檔，且**不構成、亦不得構成**對 P5.W5 之豁免（`§8.4`）。
> **義務主體**：本規格、一切變更主體、Planner、學習構件、Steward。**可判定判準**：OCV 前後快照之 componentwise 比較可機器執行；任一分量弱化而未經 Steward 書面裁決者，即觸發推定違憲之封鎖。

> **L6.18（反自我交易與 guard-the-guard）[N｜carries｜`AUGUR-MC v1.3 §P5.W5`、`§P5.W2`、`§8.1`、`F6`；不可豁免核心 `§8.4`]**
> (a) **反自我交易**：Agent（`§2.8` 意義下之自主程序）**不得**為任何降低 OCV（L6.17）、放寬風險分級門檻（L6.11–L6.13）、或擴張自身權限（L6.15）之變更之核准主體；此等變更之核准鏈根節點**必須**為人類權威，高風險者依 L6.14 需獨立人類確認。(b) **guard-the-guard**：OCV 之計算邏輯、風險分級表、介入點登錄與本層一切治理組態，其變更本身為最高核准層級之 Action（至少 RT-3；涉及移除介入點或延長自動鏈者為 RT-4），受 Gate（L6.7）與棘輪（L6.17）約束——即『對監督機制之修改』本身受監督，不得由 Agent 自主降低。**(b-1) 定義窄化防線（`§P5.W3`／`§P5.W5` 反規避）**：對 **I3／高影響之認定判準、風險分級表之分級定義（R 軸／I 軸維度）、或任一風險級之核准層級／完備性／Confidence 門檻之定義**之任何變更，一律為 **RT-4 且須事前雙人類獨立核准**（與最受保護行動同級），不因其形式上未「移除既有介入點」而降為 RT-3。理由：窄化「何謂 I3／高影響」之定義，使未來行動被重分類出 RT-4，實質等同降低人類核准層級，為 `§P5.E2` 分級權之反用（`§8.3` 保守解釋、`§8.2` 較嚴格解讀）；本款將此「定義窄化」向量顯式釘為最高防護，杜絕以改定義規避 RT-4 之自我交易。(c) **度量不可自我洗白**：OCV 分量與 change-diff **必須**由不受該變更提案 Agent 支配之路徑計算並留痕（Observation），self-reported 之 OCV **不得**單獨作為『未降低監督能力』之依據（`§P4.E7`、`§P2.E3`）。任何由 Agent 發起、意圖或實際降低 OCV 之設計，均屬**自我交易紅線**，為本層絕對禁止。
> **義務主體**：本規格、Agent Runtime、Steward。**可判定判準**：降低監督／放寬門檻／擴權之核准鏈根節點之人類權威歸屬、及治理組態變更之 RT 認定與 Gate 通過，均可機器稽核。

---

## §7 行動迴路與錯誤傳播熔斷 [N]（`§4 EV.8–EV.12`、`§P2.E3/E5`）

> **L6.19（Planning→Execution→Feedback 迴路與 Observation 回流）[N｜carries｜`AUGUR-MC v1.3 §P2.E3`、`§P5.E1`、`§4 EV.8–EV.12`；refines｜`§P3.E1`；承接｜`AUGUR-WM v1.0` Annex D D13]**
> 行動迴路：Planning（EV.8，消費 `AUGUR-L5 v1.0` 之 EV.7 Reasoning 產物）→ Human Authority Gate（EV.9，L6.7）→ Execution（EV.10 Action）→ Feedback（EV.11）→ Learning（EV.12）。Execution 之 execution receipt 與外部確認訊號以 Observation 之姿回流（`§P2.E3`），**必須永久攜帶 self-reported 標記**、以該 Agent Identity 為 Source，僅構成關於該 Action 之宣稱性 Observation，**非**世界狀態之權威確認；其升級為 Knowledge 受 `§P4.E7` 約束（見 L6.4）。回流之 Observed Effect 填入六元組（`§P5.E1`）並與 Expected Effect 比對（背離處置見 L6.20）。Learning（EV.12）改變的僅為表徵狀態（`§2.1`），**不得**實作為世界狀態直寫；其產出仍以候選斷言經 Evidence 通道（`§2.11`、`§P2.W2`、`§P2.E1`）確立，且受非侵蝕棘輪（L6.17）約束——不得以 Learning 落地任何降低 OCV 之行為變更。Agent **不得**繞過通道將意圖或未證實結果直寫 World Representation（`§P2.E3`）。
> **Planning 側結構化物件之定義與 Identity 引用紀律（承 `AUGUR-WM v1.0` Annex D D13、`AUGUR-MC v1.3 §P3.E1`；2026-07-18 RULING-2026-016 增補）**：本層行使 `§P3.E1` 下放 Layer 5–6 之定義權（Reasoning 側之引用兜底屬 Layer 5：`AUGUR-L5 v1.0` L5.1、L5.6）。(i) **Plan**：意圖進入 EV.8 Planning 之經授權結構化物件，繫結其 Goal、Constraint、所需 Capability 與已授權 Action 集合，為授權委派繫結（L6.6(d)）、權限範圍化（L6.15）、否決／暫停／中止（L6.8）與熔斷（L6.20）之作用單位。(ii) **Goal**：Plan 所宣告之意圖世界狀態；其 referent 為所繫結 Identity 之可能狀態，屬模態內容（`AUGUR-WM v1.0 §WM.17`），**必須**攜顯式模態標記，**不得**充當世界事實。(iii) **Constraint**：Plan 所載對其 Action 集合之顯式限制（含 L6.6(a) scope 與風險級上限、L6.15 之用途邊界）；本層風險分級與門檻（L6.10–L6.13）為一切 Constraint 之不可低於之下限，Plan **不得**載入弱於其之限制。(iv) **Capability**：Agent 為執行 Plan 所持之權限，其概念語義即 L6.15 之最小權限與 Plan 範圍化（capability token 之物理機制下放 Layer 7，LDO.2）。**引用紀律（`§P3.E1` 兜底、`AUGUR-WM v1.0 §WM.21(d)`）**：凡意圖進入 Reasoning／Planning 之結構化物件——不問其於本層或下層之命名——所指涉之世界實體**必須**引用已解析之 Identity；Goal／Constraint／Capability／Plan 引用未解析（provisional）Identity 者，該 Plan **不得**通過 EV.9 Gate（L6.7）、其 Action **不得**進入 EV.10（連 L6.2）。四物件之欄位設計與 serialization 下放 Layer 7（LDO.6）。
> **義務主體**：本規格、Agent Runtime。**可判定判準**：每一 Action 之 Observed Effect 具 self-reported 標記與 Source Identity、且經通道確立，引用鏈可機器稽核；存在任一 Plan（或其 Goal／Constraint／Capability）指涉世界實體而未引用已解析 Identity 仍通過 Gate 者，違反本條。

> **L6.20（錯誤傳播熔斷）[N｜carries｜`AUGUR-MC v1.3 §P2.E5`（Fail-safe，Layer 4–6 落地）、`§P5.E1`；承接｜`AUGUR-KS v1.0` KS.102]**
> 觸發條件（任一）：(i) 所依賴之 Representation 或 Evidence 被判定錯誤或撤回（`§P2.E5`）；(ii) Observed Effect 與 Expected Effect 之背離逾經登錄之容差；(iii) 進行中 Plan 之依據 ⊓Conf 跌破其 RT 級門檻（L6.12）或 Completeness Level 跌破門檻（L6.11）。受影響範圍之可判定界定：自錯誤 Representation／Evidence 沿 Evidence 溯源鏈（`§P4.E6`）與 Identity 依賴（`§P3`）之遞迴傳遞閉包（transitive closure）。處置分級：(a) 衍生 Knowledge 標記並重新評估；(b) 受影響進行中之 Plan／Action 暫停（suspend）；(c) 受影響範圍降級為觀測與建議模式（degrade）。**degrade 與 halt 之釘定**：涉 RT-4／不可逆 Action 者一律 **halt**（硬停，不得以 degrade 續行）；低階 Action 得 degrade，惟 degrade 期間**不得**延長自動執行鏈（L6.17(iii)）亦**不得**降低核准層級（L6.17(i)）。
> **判定主體／程序之釘定（承 `AUGUR-MC v1.3 §P2.E5` DEFER、`AUGUR-WM v1.0 §D15`；承接 `AUGUR-KS v1.0` KS.102 界分）**：觸發條件 (i) 所稱『被判定錯誤或撤回』，謂該 Representation／Evidence 上已依 `AUGUR-KS v1.0` KS.51 確立 Supersede Relation（失效類型 ∈ {retracted, invalidated}）、或已依 KS.62 確立衝突裁決 Knowledge。**判定主體**為該失效關係／裁決之作成者**已解析 Identity**（任一得經 Evidence 通道確立 Knowledge 之 Identity 均得作成）；**判定程序**依 KS.51 結構（失效理由 Evidence、transaction time、作成者 Identity）與 KS.36（失效事件本身為需 Evidence 之 Knowledge），**不得**匿名或無證作成。判定一經確立，本條熔斷**必須**機械觸發，Agent **不得**裁量攔阻或延遲（否則構成 `§P5.W5` 侵蝕，L6.18）。**修復之判定**（解除 suspend／degrade）同為需 Evidence 之 Knowledge 行為，以作成者已解析 Identity 為 Source、留痕為 Observation；受影響 Plan／Action 之恢復**不因曾經熔斷而豁免或降低**其 RT 級核准層級（L6.13）與 Completeness／Confidence 門檻（L6.11／L6.12）之全套約束。判定或修復之爭議由 Constitution Steward 依 `§8.1` 裁決（`§P2.E5`）。
> **義務主體**：本規格、Agent Runtime、Controlled External Interface。**可判定判準**：受影響範圍之閉包可由依賴圖機器計算；熔斷處置與 RT 級之對應為機器可查之義務；任一熔斷觸發事件可回溯至一已確立之 KS.51／KS.62 行為及其作成者 Identity、任一解除事件具修復 Evidence 與 Source Identity 留痕者合規；存在無對應已確立判定行為之熔斷攔阻或無證解除者違反本條。

---

## §8 執法點、F 防線與分界紀律 [N]（`F6`、`F3`、`§5` 角色六、`§0.6(b)`）

> **L6.21（F6 執法點：Controlled External Interface 之六元組完備性阻卻）[N｜carries｜`AUGUR-MC v1.3 F6`、`§P5.E2`、`§5` 角色六；refines｜`§2.9`]**
> Controlled External Interface（`§5` 角色六）為本層行動分級（L6.10）與六元組完備性之**單一執法點**。凡經該介面對系統外發出之操作，介面**必須**於放行前驗證其攜帶完整且可稽核之 Action 六元組（L6.1）並已通過 Human Authority Gate（L6.7）；任一未能回答「誰發起、誰授權、憑什麼知識」之操作（`F6` Unaccountable Action）**必須**於介面被阻卻、**不得**對外發出。非經授權鏈而實際造成 Reality 變更之事件為 `F6` 所禁止之違憲事件，**必須**以 Observation 回流並溯責於引致其發生之 Identity（`§2.9`）。
> **誠實輸出契約之行動側承接（承 `AUGUR-WM v1.0 §D28`／`§A.50`；憲章依據 `§P2.E5`、`§P4.E4`）**：凡經 Controlled External Interface 對人呈現之預測性產物，介面**必須**於放行前另行驗證：(i) **產物閉集**——產物屬經登錄之產物閉集，閉集外之預測性數字**不得**對外呈現（閉集之枚舉登錄為系統狀態，下放 Layer 7，仿 L6.11／L6.12 數值登錄模式）；(ii) **硬綁揭露**——每一呈現之預測性數字與其揭露事實五項（基線對照、校準 provenance、歷史／即時標示、對映偏差等，`AUGUR-WM v1.0 §A.50`；其世界模型結構位置＝`§WM.12`／`§WM.33`）於同一呈現單位內不可分離同現，缺任一項者該數字**不得**呈現；(iii) **展示分級**——呈現級別屬閉集有序分級：未達 GATE 成就（`AUGUR-L5 v1.0` L5.5）者**不得**呈現；達成就而經濟裁決否定者**僅得**研究級呈現且與裁決標籤硬綁；達成就且裁決存活者方得完整呈現；分級狀態缺位或不可解析者從最嚴（`§8.3`）；(iv) **fail-closed 閘**——上開任一驗證不成立或不可判定者一律阻卻，改以顯式之誠實拒答形呈現（不得以部分產物或降級數字充填），且產物持久層保持零寫入；其 DB 機械強制（trigger 級）與揭露載體下放 Layer 7（L7.43／L7.44 準用）。
> **義務主體**：本規格、Controlled External Interface、執行構件。**可判定判準**：存在任一對外操作未經介面六元組＋Gate 驗證即發出、或經介面發出之操作缺完整可稽核六元組者，違反本條；存在任一對人呈現之預測性數字屬閉集之外、或未同現其硬綁揭露五項、或其展示級高於其 GATE／經濟裁決狀態所許、或於狀態不可解析時仍呈現數字或寫入產物表者，違反本條。

> **L6.22（F3 防線：Accountability Before Runtime——治理鏈先於 Agent 行動）[N｜carries｜`AUGUR-MC v1.3 F3`、`§P2.E3`、`§P5.D`]**
> 本層**不得**於治理鏈（Evidence 通道、已解析 Identity、可追溯至人類權威之授權鏈）成就前使 Agent 具備任何 Action 能力（`F3` 禁止「先做 Agent、再補資料治理」）。具體落實：(a) Agent **不得**以未經 Evidence 通道確立之 Knowledge Basis 執行 Action（L6.3）；(b) Agent **不得**自我授予權威——授權鏈根節點恆為人類（L6.5）；(c) Runtime 啟動（bootstrap）序列**必須**先建立人類根授權與 Human Authority Gate（L6.7），方得啟用任何 Action 能力；(d) Planning／Execution 之任何階段**不得**繞過 EV.9 Gate。
> **義務主體**：本規格、Runtime bootstrap、Planner／Orchestrator。**可判定判準**：存在任一 Agent 於治理鏈成就前即具備或行使 Action 能力、或 Runtime 於 Gate 建立前放行任何 Action 者，違反本條。

> **L6.23（分界紀律——不重定義 L0–L5、物理下放 L7）[N｜carries｜`AUGUR-MC v1.3 §5` 角色五、`§0.6(b)`；refines｜`AUGUR-L5 v1.0` L5.8]**
> 本層定行動治理之概念不變式，**且僅此**。**不得重定義** Layer 0–5 之語義（Reality／Representation／Identity／Knowledge／Confidence L_C 之序／Trust Rank／Completeness Level 等級／Reasoning 引擎）——此等本層**僅消費**（`AUGUR-KS v1.0` KS.100、`AUGUR-L5 v1.0` L5.8）；本層止於**消費** L5 之 EV.7 Reasoning 產物，不上侵推理引擎。**不得綁定** Layer 7 之物理構件（特定 Agent 框架／Planner／Orchestrator／Scheduler／LLM、受控介面實作、kill-switch 硬體、憑證機制、UI、數值閾值）——此等下放 L7（Annex LDO），本層僅定其概念不變式（已解析 Identity、DAG、Plan 範圍化、OCV 偏序、序與棘輪）。本層全部定義通過刪名測試。
> **義務主體**：本規格、Layer 4／5／7 規格作者。**可判定判準**：本層任一條款對 L0–L5 語義作實質定義（上侵）、或對 L7 物理構件作綁定（下侵）者，違反本條（Annex L67 三欄無交集之對稱要求）。

> **L6.24（評價謂詞判準之集中錨定）[N｜carries｜`AUGUR-MC v1.3 §8.3` 可判定性元規則]**
> 本層對其引用之評價性謂詞給出可判定判準，不再 DEFER：不可逆、高影響（L6.9；經認定為高影響〔I3〕之實體世界 Action **恆歸最高風險級 RT-4、不論可逆性**，須事前逐案核准與最高完備性，L6.10／L6.11／L6.13）；高風險 Action（＝RT-3 或 RT-4，L6.10，全憲章同一分級，`§P4.E7`／`§P5.W3` 共用）；降低人類監督與否決能力（L6.17 之 OCV componentwise 弱化）；人類確認者之獨立（L6.14）；最小權限之逾越（L6.15）；熔斷之受影響範圍（L6.20 依賴閉包）；人類權威根節點、授權鏈可追溯（L6.5）；Agent-獨立否決通道（L6.8）。凡本層謂詞於判準未定處，一律採保守解釋（`§8.3` 存疑即不允許）並走缺位預設之最高風險分支（L6.9(c)、L6.10 缺位預設）。
> **義務主體**：本規格、下層引用者。**可判定判準**：本條所列每一謂詞於正文對應條款均具機器可判定之判準或保守預設分支（收錄 Annex EO）。

---

## §9 文件治理與合規存續 [N]

> **L6.90（合規聲明格式承接）[N｜carries｜`AUGUR-WM v1.0 §WM.39–45`；`AUGUR-MC v1.3 §8.3`]**
> 本規格之 Constitutional Compliance Statement 依 `AUGUR-WM v1.0 §WM.39–45` **正式格式**作成（見 **Annex CS**），非暫行模板。無有效聲明使本規格不生效力。front-matter 閉集欄位、七節論證、緊張關係節、雙向 DEFER 表、WM.44 逐條矩陣（Annex TR）俱全為機器可判生效要件（Steward 充任認定已作成：RULING-2026-007／AL-2026-011）。
> **義務主體**：本規格自身、Steward。**可判定判準**：Annex CS 之 front-matter 欄位、七節論證、緊張關係節、雙向 DEFER 表俱全（`§WM.40–44`），且 Annex TR 逐條矩陣完備。

> **L6.91（存續與升版）[N｜carries｜`AUGUR-MC v1.3 §8.6`；`AUGUR-WM v1.0 §WM.46–47`]**
> 條款編號永不重用、永不重排；`AUGUR-MC`／`AUGUR-WM`／`AUGUR-ONT`／`AUGUR-ID`／`AUGUR-KS`／`AUGUR-L5` major 升版時本規格進入重新認證期。全部「不得」（MUST NOT）義務不得豁免（`§8.4`）；尤本層落實之 P5.W2、P5.W5 為不可豁免核心。
> **義務主體**：本規格、Steward。**可判定判準**：升版時 Annex CS 之 `mc-version`／`upper-specs` 欄同步；版本間 diff 檢查——任一既發布編號於後版消失或改指他文者，違反本條。

> **L6.92（文件約定之規範地位）[N｜carries｜`AUGUR-WM v1.0 §WM.53`]**
> 【地位】節與 §0.1–§0.5 之全部約定（生效要件、規範用語等級、條款編號系統、權威語言、引用格式、元規則、概念層獨立性、自我起草硬約束）為 [N] 規範內容，其效力與正文條款同。本規格每一 [N] 條款標注憲章／上層錨定＋三態（refines／carries／hooks）＋義務主體＋可判定判準。
> **義務主體**：本規格自身、其後續修訂者及一切消費者。**可判定判準**：各約定之文句字面適用；牴觸各該約定者為文件缺陷，依 `AUGUR-MC v1.3 §8.2` 採較嚴格解讀處理至修正為止。

---

## Annex LDI [N] — 承接上層／Layer 5 DEFER 掛鉤（defers-in）

> **LDI.0（承接義務）[N]** 本表每列為規範性承接掛鉤：本層明示承接上層明示下放之事項，並於正文對應落點填充之；本表每列與 Annex CS front-matter `defers-in` 欄及 CS.3(a) 三向可解析。
> **義務主體**：本規格自身。**可判定判準**：上表每列於正文有對應 L6 條款、且於 Annex CS `defers-in` 表雙向可解析者為合規；任一列無對應正文條款者，承接不完整。

| 掛鉤 | 承接來源 | 事項 | 本規格落點 |
|---|---|---|---|
| **LDI.1** | `AUGUR-L5 v1.0` LDO.6、`AUGUR-MC v1.3 §5` 角色五 | Planning／Human Authority Gate／Action 授權鏈驗證與行動 gating（EV.8–EV.10） | L6.1、L6.5、L6.7、L6.19、L6.21 |
| **LDI.2** | `AUGUR-L5 v1.0` LDO.2、`AUGUR-KS v1.0` KDO.2、`AUGUR-MC v1.3 §P5.E2`、`AUGUR-WM v1.0 §D16`〔風險分級面，RULING-2026-016〕 | 風險分級表、各風險級之完備性／Confidence 門檻 | L6.10、L6.11、L6.12 |
| **LDI.3** | `AUGUR-MC v1.3 §P4.E7`、`AUGUR-L5 v1.0` LDO.2、`AUGUR-WM v1.0 §D16`〔確認者面〕 | 確認者資格與獨立性判準 | L6.14 |
| **LDI.4** | `AUGUR-MC v1.3 §P5.W5`、`§8.3`、`AUGUR-WM v1.0 §D16`〔監督度量面〕 | 人類監督與否決能力之可稽核度量 | L6.16、L6.17 |
| **LDI.7** | `AUGUR-ID v1.0` IDO.7（目標 L6；經 `AUGUR-WM v1.0 §D17` L6 slice） | 自然人法規對應表本體與其授權 | L6.9(d)〔RULING-2026-016 增列〕 |
| **LDI.5** | `AUGUR-KS v1.0` KS.80–KS.82、Annex CL | Completeness Level 之風險級綁定（等級語義屬 L4，本層消費） | L6.11 |
| **LDI.6** | `AUGUR-KS v1.0` KS.31/KS.34/KS.35、`AUGUR-L5 v1.0` L5.3 | Confidence 下確界（⊓Conf）之下游消費門檻綁定（序與語義屬 L4/L5，本層消費） | L6.3、L6.12 |

---

## Annex LDO [N] — 下放 Layer 7／Layer 4 DEFER 掛鉤（defers-out）

> **LDO.0（下放義務）[N]** 本表每列為規範性下放掛鉤：本層明示不定義該實作事項，授權並要求目標 Layer 定義之；目標 Layer 規格作成時必須於其 Compliance Statement 之 `defers-in` 欄承接對應列。
> **義務主體**：本規格自身（設掛鉤）、目標 Layer 規格作者（承接）。**可判定判準**：本表每列與 Annex CS front-matter `defers-out` 欄雙向可解析；本層無任一條款對本表所列事項作成可被下層直接消費之實質定義（L6.23 下侵判準）。

| 掛鉤 | 本規格落點 | 下放事項 | 目標 Layer | 授權 |
|---|---|---|---|---|
| **LDO.1** | L6.8、L6.16 | 否決／暫停／中止信號之物理傳輸機制與停止時延（H 分量）之數值上限、kill-switch 硬體／中斷實作 | L7 | `AUGUR-MC v1.3 §7`、`§0.6(b)` |
| **LDO.2** | L6.2、L6.5、L6.6、L6.15 | Actor Identity 與授權鏈節點之密碼學綁定、憑證簽發／驗證、capability token 之發放與撤銷之物理機制 | L7 | `AUGUR-MC v1.3 §7`、`§P5.W2` |
| **LDO.3** | L6.7、L6.13、L6.16 | 人類監督介面（Gate 之 UI、核准／否決互動、監督儀表板）與透明度分量 T 之揭露載體 | L7 | `AUGUR-MC v1.3 §5` 角色六、`§0.6(b)`；承 `AUGUR-L5 v1.0` LDO.3 |
| **LDO.4** | L6.10、L6.21 | 風險分級表各級之物理執法佈點（受控介面攔截點部署、雙人核准之流程編排引擎） | L7 | `AUGUR-MC v1.3 §5` 角色六、`§P5.E2` |
| **LDO.5** | L6.11、L6.12、L6.16、L6.20 | 各 RT 級具體數值門檻登錄（完備性門檻對照、Confidence banding、自動執行鏈最大長度基線、否決有界延遲上限、影響量值門檻、容差）作為系統狀態 | L7／系統狀態 | `AUGUR-KS v1.0` KS.33、KDO.2（仿 EV.2 模式；棘輪與綁定結構為本層規範，不因數值下放失位） |
| **LDO.6** | §2、L6.23 | 特定 Agent 框架／Planner／Orchestrator／Scheduler／LLM／Controlled External Interface 之選型與物理實作 | L7 | `AUGUR-MC v1.3 §7`、`§0.6(b)`、Appendix A（非約束性選型） |

---

## Annex L67 [N] — 與 Layer 4／Layer 5／Layer 7 之分界表

> **L67.0（分界判準）[N]** 本層定行動治理之概念不變式；下表「本層得為（Layer 6 專屬）」欄與「鄰層專屬」欄**無交集**，本層任一 [N] 條款不落入「鄰層專屬」欄為合規（違則構成上侵 L4/L5／下侵 L7，違 L6.23）。
> **義務主體**：本規格、Layer 4／5／7 規格作者。**可判定判準**：兩欄無交集，且本層任一條款不落入「鄰層專屬」欄。

| 面向 | 本層得為（Layer 6 專屬） | 鄰層專屬 |
|---|---|---|
| Confidence | 下游消費門檻之風險級綁定（⊓Conf ≥ RT 門檻） | L_C 之序／結構／官方映射、meet 上限代數（L4）；傳播聚合實作（L5） |
| 完備性 | Completeness Level 之風險級門檻綁定 | Completeness Level 之等級語義／維度（L4，KS.80/81） |
| Evidence | 確認者資格與獨立性、高風險證據結構之行動側 | 分類法／Trust Rank／NoLaundering（L4）；假設生成／推論產生（L5） |
| 風險分級 | RT-0–RT-4 分級語義、核准級序、缺位最高級預設 | 各級數值閾值登錄（L7）；物理執法佈點（L7） |
| 授權／權限 | 授權鏈 DAG／人類根節點、最小權限概念不變式、OCV 偏序與棘輪 | 憑證／capability token 物理機制、kill-switch 硬體（L7） |
| Action | Planning／Gate／Execution／Feedback 之 gating 概念（EV.8–EV.12 行動側） | Reasoning 引擎（EV.7，L5）；特定框架／排程器／介面實作（L7） |

---

## Annex TR [N] — WM.44 逐條對應矩陣（憲章＋WM＋ONT＋ID＋KS＋L5 → L6）

> **TR.0（矩陣之地位與生效要件性）[N]** 依 `AUGUR-WM v1.0 §WM.44`：`AUGUR-MC v1.3`、`AUGUR-WM v1.0`、`AUGUR-ONT v1.0`、`AUGUR-ID v1.0`、`AUGUR-KS v1.0`、`AUGUR-L5 v1.0` 全部 [N] 條款均須對應至本規格至少一 [N] 條款、明記 DEFER 掛鉤、或明記「不觸及」及理由（P#.Y 為 [I] 不計）。本矩陣：TR.A（`AUGUR-MC v1.3` §P5 家族逐條，本層核心承接）、TR.B（`AUGUR-MC v1.3` §P4 家族逐條）、TR.C（`AUGUR-MC v1.3` PA／P1／P2／P3 家族、EV.1–EV.12、F1–F6 及 §0/§1/§2/§3/§4/§5/§6/§7/§8 逐條）、TR.D（`AUGUR-WM v1.0`／`AUGUR-ONT v1.0`／`AUGUR-ID v1.0` 十位制區塊）、TR.E（`AUGUR-KS v1.0` 十位制區塊）、TR.F（`AUGUR-L5 v1.0` 逐條）。以十位制區塊枚舉者，區塊內各條款共享所標處置。**本層為 World Action Layer，多數上層本體條款之處置為「承接不觸及＋理由：屬 Layer 0–5 本體，L6 消費不重定義」；P5 家族為本層核心承接。**
> **義務主體**：本規格、Steward。**可判定判準**：六上層每一 [N] 條款於本矩陣有落點列（承接／細化／DEFER／不觸及＋理由）者為完備；標「不觸及＋理由」之列，其理由為機器可判之處置。

### TR.A — `AUGUR-MC v1.3` §P5 家族（逐條，本層核心）[N]

| MC 條款 | L6 落點 | 模式 |
|---|---|---|
| §P5.D（誰發起／誰授權／憑什麼知識） | L6.1、L6.22（Accountability Before Runtime） | 承接（核心） |
| §P5.E1（Action 六元組） | L6.1、L6.4、L6.19、L6.21 | 細化（核心） |
| §P5.E2（風險分級 DEFER、缺位最高級預設、受控介面執法點） | L6.10、L6.11、L6.12、L6.21（本層定義該表） | 細化（核心） |
| §P5.W1（單一 Identity 歸責） | L6.2 | 承接 |
| §P5.W2（授權鏈根節點必為人類權威、隨時否決／暫停／中止） | L6.5、L6.6、L6.7、L6.8、L6.13（不可豁免核心） | 承接（核心） |
| §P5.W3（權限與不可逆性成反比、高影響需最高核准） | L6.10、L6.11、L6.12、L6.13、L6.15 | 承接（核心） |
| §P5.W4（最小權限） | L6.15 | 承接 |
| §P5.W5（不得降低人類監督與否決能力、可稽核度量下放 L6、保守預設） | L6.16、L6.17、L6.18（本層定義該度量，不可豁免核心） | 細化（核心） |

### TR.B — `AUGUR-MC v1.3` §P4 家族（逐條）[N]

| MC 條款 | L6 落點／處置 | 模式 |
|---|---|---|
| §P4.D（Evidence 可追溯） | L6.3、L6.22 | 承接 |
| §P4.W1（Augur 不接受：無 Source 之 Knowledge、不可重現之結果、無 Evidence 之推論） | L6.3（Knowledge Basis 須經通道確立） | 承接 |
| §P4.E1（Knowledge 五元組） | L6.3（Knowledge Basis 引用五元組 Knowledge，消費自 L4） | 承接 |
| §P4.E2（Time（雙時間性）） | L6.1（Timestamp 欄雙時間性） | 承接 |
| §P4.E3（Supersede（只失效不刪除）） | 不觸及＋理由：supersede／tombstone 語義屬 L4；本層以 Observation 回流不重定義保存語義 | 不觸及＋理由 |
| §P4.E4（Defeasible（可謬性）） | 不觸及＋理由：可謬性屬 L4/L5 Knowledge／Hypothesis 語義；本層消費 Confidence 不重定義 | 不觸及＋理由 |
| §P4.E5（Conflict（矛盾保存）） | L6.20（未裁決 Conflict 為熔斷觸發／完備性門檻要件）；保存語義屬 L4 | 承接（消費面）＋不觸及（語義） |
| §P4.E6（Provenance（遞迴溯源）） | L6.9（宣告受 provenance 約束）、L6.20（受影響範圍沿溯源鏈閉包） | 承接 |
| §P4.E7（NoLaundering（信任不可洗白）） | L6.3、L6.12、L6.14、L6.18（確認者資格與獨立性之落地；高風險須獨立 Data Evidence／人類確認） | 細化（核心） |
| §P4.E8（Confidence（語義與消費）） | L6.3、L6.12（下游消費門檻之風險級綁定；序與語義消費自 L4） | 細化（消費面） |

### TR.C — `AUGUR-MC v1.3` 非 P4/P5 家族（逐條）[N]

| MC 條款 | L6 落點／處置 | 模式 |
|---|---|---|
| PA（Prime Axiom）＋§1.1 釐清句 | L6.1、L6.3、L6.22、CS.1-PA（可追溯 Evidence／不確定性可追溯／錯誤可修正之行動側） | 承接 |
| §0（Document Status & Conventions（文件地位與約定））／§0.1–§0.6 | §0（本規格文件約定，效力依 L6.92 承載） | 承接 |
| §0.2（規範用語約定） | §0.2（本規格沿用 `AUGUR-MC v1.3 §0.2` 必須／不得／應／得等級，全文一致不重定義） | 承接 |
| §0.4（權威語言聲明） | §0.4（本規格以繁體中文為權威版本、規範術語一律用英文原詞，術語同一性） | 承接 |
| §1／§1.1／§1.2／§1.3 | §1（Layer 定位）；§1.3 第五禁令（未授權行動）→ L6.5、L6.21 | 承接 |
| §2（Definitions 章） | §0.5 不重定義元規則；§2.9 Action 定義 → L6.1、L6.21 | 承接 |
| §3（Five Immutable Principles（五大不可違反原則）） | L6.19、CS.1-EV-chain | 承接 |
| §4（World Evolution Model（世界演化模型）） | 見 EV.* 逐列；本層為 EV.8–EV.12 行動迴路落點 | 細化（核心） |
| §5 角色一/二/三/四 | 不觸及＋理由：屬 L1/L4/L5（record／表徵／Intelligence 泛稱／Reasoning），本層消費不重定義 | 不觸及＋理由 |
| §5 角色五（Agent Runtime：Planning／Execution／Feedback 受 P5 約束） | §3–§8（L6.1–L6.24），本規格核心職掌 | 細化（核心） |
| §5 角色六（Controlled External Interface 執法點） | L6.21、L6.10（六元組完備性＋分級執法點） | 細化（核心） |
| §6 F1（Data First Architecture） | 不觸及＋理由：資料表先於世界模型屬 L1/L4 建置紀律 | 不觸及＋理由 |
| §6 F2（Model First Architecture） | 不觸及＋理由：先選 model 再設計系統屬 L5 防線（`AUGUR-L5 v1.0` L5.7） | 不觸及＋理由 |
| §6 F3（Agent First Architecture） | L6.22（Accountability Before Runtime，核心防線） | 承接（核心） |
| §6 F4（Knowledge Without Identity） | L6.1、L6.5、L6.17（未授權行動／降低監督為禁止型態） | 承接 |
| §6 F5（Intelligence Without Evidence） | 不觸及＋理由：per-結論可解釋屬 L5（`AUGUR-L5 v1.0` L5.6）；本層要求 Knowledge Basis 經通道（L6.3） | 承接（行動側）＋不觸及 |
| §6 F6（Unaccountable Action） | L6.1、L6.21（六元組完備性阻卻，核心執法） | 承接（核心） |
| §7（Long-Term Stability Rule（十年以上演化原則）） | L6.23、§0.5（刪名測試、物理下放 L7） | 承接（核心） |
| §8.1（Constitution Steward（憲章權威）） | L6.17、L6.18（Steward 書面裁決推翻推定）；充任認定屬 Steward | 承接 |
| §8.2（違憲後果、審查程序與衝突優先序） | L6.90、L6.92（較嚴格解讀）；實質審查屬 Steward | 承接 |
| §8.3（合規聲明義務與可判定性元規則） | L6.9、L6.10、L6.17、L6.24、Annex EO | 承接（核心） |
| §8.4（不可豁免核心） | L6.5、L6.8、L6.17、L6.91（P5.W2／P5.W5 不豁免） | 承接（核心） |
| §8.5（Amendment Procedure（修訂程序）） | 不觸及＋理由：修憲程序屬 L0 憲章自身治理，本層為受規範對象（L6.90） | 不觸及＋理由 |
| §8.6（版本語義、引用格式與編號穩定性） | L6.91、§0.3 | 承接 |
| P1（Reality First 家族：P1.D／P1.E1／P1.E2／P1.E3／P1.W1） | L6.9（I 軸涉自然人 P1.E3 敏感 Identity）；Reality 本體屬 L0/L1，本層消費；CS.1-P1 | 承接＋不觸及 |
| P2（Representation Before Intelligence 家族：P2.D／P2.E1／P2.E2／P2.E3／P2.E4／P2.E5／P2.W1／P2.W2） | L6.4、L6.19（P2.E3 影響須以 Observation 回流、不直寫）、L6.20（P2.E5 Fail-safe）；CS.1-P2 | 承接（核心） |
| P3（Identity Before Knowledge 家族：P3.D／P3.E1／P3.E2／P3.E3／P3.W1／P3.W2） | L6.2（已解析 Identity 歸責）、L6.14（獨立性以 lineage 稽核）、L6.5（人類決策者 Human）；CS.1-P3 | 承接 |
| EV.1（Reality） | 不觸及＋理由：Reality 本體屬 L0/L1，非行動落點 | 不觸及＋理由 |
| EV.2（Observation） | L6.4、L6.19（Observed Effect／receipt 以 Observation 回流） | 承接 |
| EV.3（Representation） | 不觸及＋理由：表徵確立屬 L4/L5；本層不直寫（L6.19） | 不觸及＋理由 |
| EV.4（Identity） | L6.2、L6.5、L6.14（已解析 Identity 歸責／根節點／確認者） | 承接 |
| EV.5（Evidence）／EV.6（Knowledge） | L6.3（Knowledge Basis 引用經通道確立之 Knowledge，消費自 L4） | 承接（消費） |
| EV.7（Reasoning） | 不觸及＋理由：Reasoning 引擎屬 L5（`AUGUR-L5 v1.0`）；本層止於消費其產物（L6.19、L6.23） | 不觸及＋理由 |
| EV.8（Planning） | L6.7、L6.19（Planning→Gate；消費 L5 之 EV.7 產物） | 細化（核心） |
| EV.9（Human Authority Gate） | L6.7（強制授權驗證點，核心落點） | 細化（核心） |
| EV.10（Action） | L6.1、L6.4、L6.10、L6.21（Action 執行與分級執法） | 細化（核心） |
| EV.11（Feedback） | L6.4、L6.19、L6.20（Observed Effect 回流、熔斷） | 細化（核心） |
| EV.12（Learning） | L6.17、L6.19（Learning 產出經通道、受非侵蝕棘輪約束、不直寫） | 承接（核心） |

### TR.D — `AUGUR-WM v1.0`／`AUGUR-ONT v1.0`／`AUGUR-ID v1.0`（全部 [N]，十位制區塊）[N]

| 上層區塊 | L6 落點／處置 |
|---|---|
| `AUGUR-WM v1.0` WM.1–WM.12（從屬／管轄／概念層獨立性／刪名測試／不確定性結構位置） | L6.23、§0.5、L6.3—承接（刪名測試、Confidence 槽消費） |
| `AUGUR-WM v1.0` WM.13–WM.32（存在層本體／唯一權威表徵／canonical chain／Evidence 三分類存在層宣告） | 不觸及＋理由：屬存在層本體，L6 消費不重定義；WM.24 canonical chain → L6.19 承接 |
| `AUGUR-WM v1.0` WM.33（永久標記表達力） | L6.4、L6.19（self-reported 永久標記）—承接（核心） |
| `AUGUR-WM v1.0` WM.34（核心不變式之可機器稽核） | L6.1、L6.5、L6.16、L6.17（可機器稽核判準）—承接 |
| `AUGUR-WM v1.0` WM.35–WM.37（落地即整合；消費設閘不阻斷落地／World Concept Registry 與消費規則／唯一權威表徵落實義務） | 不觸及＋理由：屬存在層／L4 落點 |
| `AUGUR-WM v1.0` WM.38（自然人之有界表徵） | **承接**（RULING-2026-016 析出）：L6.9(d)（法規對應表四欄登錄）、L6.10／L6.13（涉自然人 I3⇒RT-4 行動強制） |
| `AUGUR-WM v1.0` WM.39–WM.47（合規聲明格式／編號穩定／升版） | L6.90、L6.91、§0.3、Annex CS、Annex TR—承接／落實 |
| `AUGUR-WM v1.0` WM.48–WM.53（存在層治理雜項／文件約定規範地位） | WM.53 → L6.92—承接；WM.48–52 不觸及＋理由：屬存在層治理 |
| `AUGUR-WM v1.0` Annex A（A.0–A.59）／Annex D（D0–D28，除 D13、D15、D16、D17、D22、D24、D28 外）／HOOK-01/02/03 | 不觸及＋理由：領域素材與 L2–L4 下放掛鉤，非行動治理落點；經 L4/L5 工作流入徵。〔**六列旗標已全數逐列裁決**（RULING-2026-016；查證 12 代理、反駁全數失敗）：D16 純文件補正、D13／D15／D17／D22／D28 實質承接補正——各見下列承接列〕 |
| `AUGUR-WM v1.0` **D24**（存取控制 RBAC；授權資料不入預測特徵之隔離強制） | **承接**（2026-07-18 RULING-2026-013 補正）：RBAC 面＝L6.15（最小權限與 Plan 範圍化）＋L6.6（委派範圍／失效／可撤銷）；隔離強制面＝L6.15 增補款（授權受限資料之用途邊界）；物理面細化下放 L7.16／L7.33(b)／L7.49 |
| `AUGUR-WM v1.0` **D13**（Goal、Constraint、Capability、Plan 之定義；目標 L5–L6，`AUGUR-MC v1.3 §P3.E1`、WM.21(d) 兜底） | **承接**（2026-07-18 RULING-2026-016 補正）：定義面＝L6.19 增補款（Planning 側四物件概念語義——Plan 繫結 Goal／Constraint／Capability 與已授權 Action 集合，連 L6.6(d)／L6.8／L6.15／L6.20；Goal 為模態內容承 `AUGUR-WM v1.0 §WM.17`；Constraint 承 L6.6(a) scope／風險級上限；Capability＝L6.15 權限語義）；引用紀律面（P3.E1 兜底）＝L6.19 增補款（引用未解析 Identity 之 Planning 物件不得通過 EV.9 Gate，連 L6.2／L6.7）；Reasoning 側兜底屬 L5（`AUGUR-L5 v1.0` L5.1／L5.6、CS.1-P3）；欄位／serialization 與 capability token 物理面下放 L7（LDO.2、LDO.6） |
| `AUGUR-WM v1.0` **D15**（fail-safe 判定主體／程序、污染追蹤、觀測建議模式邊界） | **承接**（RULING-2026-013 主文三逐列查證補正）：污染追蹤面＝L6.20（受影響範圍＝自錯誤 Representation／Evidence 沿 Evidence 溯源鏈與 Identity 依賴之遞迴傳遞閉包，Annex EO「熔斷之受影響範圍」；表達力承 `AUGUR-KS v1.0` KS.70／KS.34）；觀測建議模式邊界面＝L6.20（degrade／halt 釘定：RT-4／不可逆一律 halt；degrade 期間不得延長自動執行鏈〔L6.17(iii)〕、不得降低核准層級〔L6.17(i)〕；否決通道恆常可用 L6.8）；判定主體／程序面＝L6.20 增補款（判定＝KS.51 Supersede Relation／KS.62 裁決之確立，作成者已解析 Identity 攜失效理由 Evidence；熔斷機械觸發不得裁量攔阻；修復判定同為需 Evidence 之行為且恢復不豁免 RT 級約束；爭議→Steward `§8.1`）；失效與 Supersede 形式表達力屬 L4（KS.51／KS.36／KS.62；KS.102 界分），本層消費不重定義 |
| `AUGUR-WM v1.0` **D16**（風險分級表、核准流程、確認者資格與獨立性、監督否決度量；WM 掛鉤 WM.28、A.53） | **承接**（本列補正：本層即該列之目標 Layer，四子項落點既存、無需增補條文）：風險分級表＝L6.9（R×I 可判定判準）＋L6.10（RT-0–RT-4，含 `§P5.E2` 缺位最高級預設之引述不削弱、全憲章同一分級）＋L6.11／L6.12（各級完備性／Confidence 門檻）＋L6.21（受控介面執法點）；核准流程＝L6.13（有序核准層級與各 RT 綁定、核准者已解析 Identity 為 Source 留痕為 Observation）＋L6.7（EV.9 Gate 強制驗證）；確認者資格與獨立性＝L6.14（行使 `§P4.E7` 下放之定義權）；監督否決度量＝L6.16（OCV）＋L6.17（單調棘輪）＋L6.18（反自我交易／guard-the-guard）；A.53 域內人類決策動作閉集之維護紀律＝L6.18(b)（介入點登錄之變更為最高核准層級 Action）＋L6.7／L6.13，閉集域內內容經 L4/L5 工作流入徵、物理佈點與數值登錄下放 L7（LDO.3／LDO.4／LDO.5） |
| `AUGUR-WM v1.0` **D17**（自然人法規對應表；目標 L3/L6，`§WM.38`、`§P1.E3`） | **承接**（RULING-2026-016 補正）：**L6 slice**（法規對應表本體與其授權，承 `AUGUR-ID v1.0` IDO.7）＝L6.9(d) 增補款（自然人法規對應表：四欄登錄義務、登錄項為系統狀態、未登錄即不允許之保守預設、合規優先且忠實表徵不減損、I 軸敏感標記可解析至表）；行動風險面＝L6.9(b)／L6.10／L6.13 既載（涉自然人敏感 Identity ⇒ I3 ⇒ RT-4 ⇒ 事前雙人類獨立核准）；**L3 slice** 由 `AUGUR-ID v1.0` ID.42（去識別化／法規強制抹除）＋ID.60（as-of 繫結）既承；部署面細化下放 L7.33（語料隔離之機器強制、egress 預設拒絕） |
| `AUGUR-WM v1.0` **D22**（核心宇宙完整性 gate、流動性分位地板、產業條件豁免機制） | **承接**（RULING-2026-013 主文三旗標之逐列補正）：判準結構面＝L4（`AUGUR-KS v1.0` KS.80 增補款〔成員資格為資料品質之函數、三機制結構〕＋KS.81(f)〔產業條件豁免之完備性語義〕）；計算面＝L5（成員資格衍生為 inference，`AUGUR-L5 v1.0` L5.2／L5.3 既有紀律）；治理面＝L6.11 增補款（gate 門檻值與流動性分位值之採認變更核准、產業豁免之授予存續審查——人類核准留痕，數值登錄下放 L7 系統狀態） |
| `AUGUR-WM v1.0` **D28**（誠實輸出契約本體：產物閉集、硬綁揭露五項、展示分級、fail-closed 閘） | **承接**（2026-07-18 RULING-2026-016 補正）：契約本體＝L6.21 增補款（受控介面放行前四驗證：產物閉集／硬綁揭露五項／展示分級／fail-closed 閘）；分級狀態消費 `AUGUR-L5 v1.0` L5.4／L5.5（GATE 成就與模態標記——D28 之 L5 面，既載）；表達力承 `AUGUR-WM v1.0 §A.50`（WM.12／WM.17／WM.33）；物理面下放 L7——揭露載體 L7.43、介面 fail-closed L7.44、產物表 trigger 級機械強制與閉集枚舉登錄 |
| `AUGUR-ONT v1.0` ONT.1–ONT.62（型別層本體／Type 判準／schema／型別演化） | 不觸及＋理由：型別層本體，本層消費既定 Type 不重定義；ONT.60–62 合規存續 → L6.90/L6.92 承接 |
| `AUGUR-ONT v1.0` Annex T／DO.0–DO.4 | 不觸及＋理由：型別素材與 L2 下放掛鉤，目標 L3–L4 已承接 |
| `AUGUR-ID v1.0` ID.1–ID.53（個體層本體／identifier／lifecycle／已解析與 provisional 狀態） | L6.2（消費已解析 Identity）、L6.5（人類決策者 Human）、L6.14（lineage 獨立性）—承接（消費）；其餘個體層機制不觸及＋理由：屬 L3 |
| `AUGUR-ID v1.0` ID.60–ID.81（身份屬性 as-of 繫結義務／繫結存在 vs 重建引擎之分界／Layer 4 專屬事項清單／分界表／格式承接／存續與升版） | L6.23（分界紀律不上侵 L3）、L6.90/L6.92（合規存續）—承接；衝突保存語義不觸及＋理由：屬 L4 |
| `AUGUR-ID v1.0` IDO.0–IDO.8（ID 下放掛鉤） | **IDO.7（目標 L6）→ 承接（L6.9(d)，RULING-2026-016 更正——原列理由對 IDO.7 為誤述）**；其餘（目標 L4/L5/L7）不觸及＋理由：已由對應層承接；本層消費已解析 Identity |

### TR.E — `AUGUR-KS v1.0`（全部 [N]，十位制區塊）[N]

| KS 區塊 | L6 落點／處置 |
|---|---|
| KS.1–KS.19（總則／從屬／不重定義／管轄紀律） | §0.5、L6.23—承接 |
| KS.20–KS.29（五元組／唯一權威表徵／欄位） | L6.3（Knowledge Basis 引用五元組，消費）—承接（消費） |
| KS.30–KS.38（Confidence Lattice L_C／Grading Method／meet／單調／INSUF 保守） | L6.3、L6.12（⊓Conf 消費門檻綁定，硬守 KS.34 meet）—承接（消費，核心） |
| KS.39（Confidence 非 Reasoning） | 不觸及＋理由：Confidence 生成屬 L5、語義屬 L4；本層僅消費 ⊓Conf 為 Action 門檻，不重定義生成 |
| KS.40–KS.54（雙時間／as-of／supersede／重編） | L6.1（Timestamp）—承接（消費）；as-of 引擎不觸及＋理由：屬 L4/L7 |
| KS.55（衍生物 DELETE 重建之禁止） | 不觸及＋理由：supersede 語義屬 L4；本層以 Observation 回流不重定義保存語義 |
| KS.60–KS.61（Conflict Set 保存／下游消費） | L6.20（未裁決 Conflict 為熔斷觸發／完備性門檻要件）—承接（消費面）＋不觸及保存語義（屬 L4），與 TR.C `§P4.E5`→L6.20 一致 |
| KS.62–KS.78（Evidence 分類／Trust Rank／NoLaundering／完備性維度／白名單／self-reported） | L6.3、L6.11、L6.14（完備性維度消費、確認者獨立、self-reported）—承接（消費，核心） |
| KS.79（審議通道之 Evidence 強度分級——解 AUD-16） | L6.3（審議 Evidence 強度落行動側 Knowledge Basis 門檻，高風險須獨立 Data Evidence）—承接（行動側） |
| KS.80–KS.84（Completeness Level／GATE 統計治理設計權） | L6.11（Completeness Level 風險級綁定，L4 定等級、L6 定綁定）—承接（核心）；GATE 設計權不觸及＋理由：屬 L4/L5 |
| KS.90–KS.92（identity claim Confidence／欄位／狀態映 L_C） | 不觸及＋理由：屬 L4 Knowledge 側，本層消費 |
| KS.100–KS.102（分界／L56／Fail-safe） | L6.23（分界紀律承 KS.100/101）、L6.20（Fail-safe 承 KS.102）—承接（核心） |
| KS.110–KS.111（格式承接／存續與升版） | L6.90、L6.91—承接 |
| KDO.0–KDO.7（KS 下放掛鉤） | KDO.2 → L6.10/L6.11/L6.12（消費門檻綁定，核心承接）；KDO.0（下放義務標頭）由本區塊 child-row 承載；其餘 KDO 目標 L5/L7，不觸及＋理由：非本層行動治理落點 |
| Annex CL（Completeness Level）／Annex EV（Evidence 分類） | L6.11（消費 CL 為完備性量尺）、L6.3（消費 EV 分類）—承接（消費） |

### TR.F — `AUGUR-L5 v1.0`（全部 [N]，逐條）[N]

| L5 條款 | L6 落點／處置 |
|---|---|
| L5.1（合法推理之定義——推理產物為候選斷言，非權威真值） | L6.3、L6.19（Knowledge Basis 須經通道確立；Learning 產出以候選斷言）—承接（核心） |
| L5.2（Evidence 引用鏈 DAG／雙合法終點） | L6.9（宣告受溯源約束）、L6.20（受影響閉包沿溯源鏈）—承接 |
| L5.3（Confidence 沿推理鏈之傳播——承接 KDO.1，硬守 KS.34 上限） | L6.3、L6.12（消費 ⊓Conf 為 Action 門檻，不重定義傳播）—承接（消費） |
| L5.4（Hypothesis 之地位——未證斷言、可謬、須顯式標記） | 不觸及＋理由：Hypothesis 地位屬 L5；本層要求 Knowledge Basis 非候選斷言（L6.3） |
| L5.5（Hypothesis 不得無證升級） | 不觸及＋理由：升級紀律屬 L5；本層消費已確立 Knowledge |
| L5.6（Explanation 義務——per-結論可解釋，F5 之落實，承接 AUD-18） | 不觸及＋理由：解釋內容義務屬 L5；本層要求六元組可稽核（L6.1）與 Gate 揭露（L6.16 T 分量）—承接（行動側揭露） |
| L5.7（AI Model 為 Reasoning 之工具而非世界權威——F2 Model First 之防線） | 不觸及＋理由：model output 地位屬 L5；本層 L6.3 承接「高風險不得僅以 Computational Evidence」之行動側 |
| L5.8（Reasoning 引擎之分界紀律——不下侵 L4 語義、不上侵 L6 消費） | L6.23（對稱：本層不上侵 L5、不下侵 L7）—承接（核心） |
| L5.9（identity resolution 演算之定性承接——T-KS-6 之解消） | 不觸及＋理由：resolution 定性屬 L5；本層消費已解析 Identity（L6.2） |
| L5.90–L5.92（合規聲明格式承接／存續與升版／文件約定之規範地位） | L6.90、L6.91、L6.92—承接 |
| Annex LDO（LDO.0–LDO.6，尤 LDO.2／LDO.6） | LDI.1／LDI.2／LDI.3／LDI.4（本層承接 L5 下放之行動 gating／風險分級／確認者資格／監督度量）—承接（核心）；LDO.0（下放義務標頭）由本區塊 child-row 承載 |

### TR.Z — 殘餘生效阻卻（DRAFT）[N]

> **TR.Z（充任認定已成就；`§8.2` 實質審查已作成、residual 保留）[N]** 上開逐條／區塊枚舉已就六上層全部 [N] 條款給出落點（承接／細化／DEFER／不觸及＋理由）。**本規格經 Constitution Steward 依 `AUGUR-MC v1.3 §8.1` 作成充任認定，並經 `§8.2` 實質合憲人類審查，自 2026-07-17 起以 v1.0 生效**（Steward 裁決第 2026-007 號、AL-2026-011）；**Steward `§8.2` 違憲審查權就 residual 事項完整保留**（RULING-2026-007:43）；形式充分性之最終判斷與實質合憲審查均屬 Steward 裁決，本子代理不代行、不自行宣稱生效。以十位制區塊枚舉之上層本體條款，其「不觸及＋理由」為機器可判之處置；如經 Steward 認定某區塊須逐條細列，屬 minor 升版維護（L6.91）。**自我起草警示**：本層規範人類對 Agent 之權威，其監督度量與非侵蝕棘輪（L6.16–L6.18）之充分性尤待 Steward `§8.2` 實質審查確認未低估人類監督之真實維度（T-L6-5）。
> **義務主體**：本規格、Steward。**可判定判準**：六上層每一 [N] 條款於本矩陣有落點；Steward 充任認定成就前，本規格不生效力（該要件已成就：RULING-2026-007／AL-2026-011）。

---

## Annex CS [N] — Constitutional Compliance Statement（依 `AUGUR-WM v1.0 §WM.39–45` 格式）

本 Annex 為**規範性聲明文件**（[N]）：其存在與內容為本規格之生效要件（L6.90、`AUGUR-MC v1.3 §8.3`、`AUGUR-WM v1.0 §WM.39`）。**地位提示**：本規格為 **v1.0 生效版本**，Steward 充任認定已作成、`§8.2` 實質人類審查已作成，自 2026-07-17 起生效（Steward 裁決第 2026-007 號，AL-2026-011；見【地位】、L6.90）；**Steward `§8.2` 違憲審查權就 residual 事項完整保留**（RULING-2026-007:43）。

```
compliance-statement:
  spec: Augur Agent Runtime Specification
  spec-version: v1.0
  layer: 6
  mc-version: AUGUR-MC v1.3
  upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v1.0, AUGUR-ID v1.0, AUGUR-KS v1.0, AUGUR-L5 v1.0]
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: [T-L6-1, T-L6-2, T-L6-3, T-L6-4, T-L6-5, T-L6-6]
  defers-in: [L5.LDO.2, L5.LDO.6, KS.KDO.2, MC.P5.E2, MC.P4.E7, MC.P5.W5, MC.role5, ID.IDO.7]
  defers-out: [LDO.1, LDO.2, LDO.3, LDO.4, LDO.5, LDO.6]
  date: 2026-07-17
  author: Layer 6 Agent Runtime 規格起草人（AUGUR-L6 起草子代理；產物原為 v0.1-draft 提案，業經 Steward 充任認定與 §8.2 實質審查，以 v1.0 生效；§8.2 residual 保留）
  archive-path: specs/AGENT-RUNTIME-SPECIFICATION-v0.1-draft.md
```

### CS.1 逐原則論證本文（七節，順序固定）[N]

> **CS.1-PA（Prime Axiom）**〔承接〕
> 引 `AUGUR-MC v1.3 §1.1`、`§P5.D`。行動治理落實 PA 之三性：每一 Action 之 Knowledge Basis 須引用可追溯 Evidence（L6.3）落實「可追溯之 Evidence」；風險級門檻與 ⊓Conf 綁定（L6.12）落實「不確定性可追溯」；熔斷與否決通道（L6.8、L6.20）落實「錯誤可被修正／可中止」。判準揭示：「可追溯」以六元組引用鏈可機器遍歷（L6.1 判準）操作化，「錯誤可修正」以 Agent-獨立否決通道恆常可達（L6.8 判準）操作化。

> **CS.1-P1（Reality First）**〔承接＋不觸及〕
> 〔RULING-2026-016 補述〕P1.E3 之法規對應面：L6.9(d) 課自然人法規對應表四欄登錄義務（未登錄即不允許之保守預設）；**判準揭示**：登錄項存在性與四欄完備性可機器盤點。
> 引 `§P1.E3`、`§2.9`。影響軸 I 之高影響判準涵蓋涉自然人（`§P1.E3`）安全法益之敏感 Identity（L6.9），觸此者最高風險級 RT-4（L6.10）；Reality 唯經 Action 改變、系統外變化逕以 Observation 進入（L6.19，承 `§4` 因果迴路）。Reality／表徵本體屬 Layer 0/1，本層消費不重定義。判準揭示：涉自然人敏感 Identity 之 Action 落最高風險分支（L6.9(b)、L6.10 判準）以 Identity 標記可機器盤點操作化。

> **CS.1-P2（Representation Before Intelligence）**〔承接〕
> 引 `§P2.E3`、`§P2.E5`、`§P2.W2`。Action 之影響（Observed Effect）必以 Observation 回流、Agent 不得直寫 World Representation（L6.4、L6.19，承 `§P2.E3`）；execution receipt 永久攜 self-reported 標記、非世界權威確認；錯誤傳播熔斷落實 Fail-safe（L6.20，承 `§P2.E5`）。判準揭示：未經 Observation 通道回流或缺 self-reported 標記之 Observed Effect 為非法（L6.4 判準），可機器稽核引用鏈。

> **CS.1-P3（Identity Before Knowledge）**〔承接〕
> 引 `§P3.E1`、`§P3.E2`、`§P3.W2`。每一 Action 之 Actor Identity 須為單一、已解析之 Identity（L6.2）；授權鏈根節點為已解析之人類決策者 Human（`§P3.W2`，L6.5）；確認者之獨立性以 Identity lineage（`§P3.E2`）機器稽核（L6.14）。判準揭示：Actor Identity 為空／未解析／非單一者違反（L6.2 判準），以 `AUGUR-ID v1.0` lineage 機器判定。

> **CS.1-P4（Evidence Before Conclusion）**〔細化〕
> 逐條見 Annex TR.B。`§P4.E7` NoLaundering／獨立性／synthetic／高風險證據 → 確認者資格與獨立性之落地（L6.14）、高風險不得僅以 Computational Evidence（L6.3）；`§P4.E8` Confidence 消費、Action 允許等級 → ⊓Conf 之風險級門檻綁定（L6.12）；`§P4.E6` 遞迴溯源 → 熔斷受影響閉包（L6.20）；`§P4.E2` 雙時間 → Timestamp 欄（L6.1）。判準揭示：每一評價性謂詞（「高風險 Action」L6.10、「確認者獨立」L6.14、「Confidence 門檻」L6.12）附可判定判準（收錄 Annex EO）。

> **CS.1-P5（Accountability Before Action）〔核心〕**〔細化〕
> 逐條見 Annex TR.A。本層為 `§P5` 家族之主要落點：`§P5.E1` 六元組不變式（L6.1）；`§P5.E2` 風險分級表（本層定義 RT-0–RT-4，L6.10–L6.12）；`§P5.W1` 單一歸責（L6.2）；`§P5.W2` 人類權威根節點與隨時否決（L6.5、L6.7、L6.8，不可豁免核心）；`§P5.W3` 權限與不可逆性成反比（L6.13、L6.15）；`§P5.W4` 最小權限（L6.15）；`§P5.W5` 不得降低監督否決能力（本層定義 OCV 度量與單調棘輪，L6.16–L6.18，不可豁免核心）。判準揭示：授權鏈根為 Agent／含環（L6.5）、OCV componentwise 弱化（L6.17）、Agent 為降低監督之核准主體（L6.18）均為機器可稽核之違反型態。

> **CS.1-EV-chain（§4 canonical chain）**〔細化〕
> 引 `§4` canonical chain 之 EV.8（Planning）、EV.9（Human Authority Gate）、EV.10（Action）、EV.11（Feedback）、EV.12（Learning）為本規格之核心落點；引 `AUGUR-WM v1.0 §WM.24`（節選連續性）。本層機制化 EV.8→EV.9→EV.10→EV.11→EV.12：Planning 消費 L5 之 EV.7 產物（L6.19）、Gate 強制授權驗證（L6.7）、Action 六元組執行與分級執法（L6.1、L6.10、L6.21）、Feedback 以 Observation 回流（L6.4）、Learning 受非侵蝕棘輪約束（L6.17）；節選不跳節點，上承 EV.7（Reasoning，L5）。判準揭示：任一 Action 未經 EV.9 Gate 即進入 EV.10 者違反（L6.7 判準），可機器稽核。

### CS.2 已知緊張關係（`AUGUR-WM v1.0 §WM.42`）[N]

| T-id | 所涉條款 | 描述 | 緩解／狀態 |
|---|---|---|---|
| **T-L6-1** | L6.16、L6.17、L6.15 | 自主性 vs 人類事前核准之時延：提高介入密度（D／A）與縮短自動執行鏈（C）增加核准延遲，與 Agent 執行效率張力。 | 本層一律偏向人類權威：張力之解不得以降低 OCV 保護分量為代價（L6.17 單向約束）；效率最佳化僅得於不使 OCV 退步之空間內為之。P5.W5 為不可豁免核心（`§8.4`）。非豁免事項。DRAFT。 |
| **T-L6-2** | L6.15、L6.9、L6.10 | 最小權限與缺位保守預設 vs 運維便利／吞吐：Plan 範圍化即時收回與未宣告即 RT-4，與常駐服務帳號及真實低風險行動之吞吐張力。 | 禁常駐／環境權限，運維便利讓位於 P5.W4；採宣告—稽核制，宣告受 `§P4.E6` provenance 約束不得虛列，未宣告方走最高風險分支。非豁免事項。DRAFT。 |
| **T-L6-3** | L6.4、L6.19、L6.3 | self-reported 回流 vs `§P4.E7`：Observed Effect 為 self-reported Observation，不得單獨作為升級 Knowledge 或解除熔斷之權威依據。 | 高風險 Action 之確認須獨立 Data Evidence 或人類確認（L6.3、L6.14、L6.20）；self-reported 標記永久攜帶。非豁免事項。DRAFT。 |
| **T-L6-4** | L6.8、L6.16、L6.11、L6.12 | 數值基線／時延上限下放 L7 vs `§8.3` 可判定性：停止時延（H）、Confidence banding、完備性門檻數值下放 L7 系統狀態登錄。 | 仿 KS.33／EV.2 模式——序與棘輪判準為 [N] 且非示意，不因數值登錄下放而失位；數值未登錄前依保守解釋取最高風險（`§8.3`）、缺位預設最高核准級（L6.10 RT-4）補強。非豁免事項。DRAFT。 |
| **T-L6-5** | L6.16、L6.17、L6.18 | Agent 起草本層之利益衝突／自我交易（度量被操弄之自我指涉）：本層度量 OCV 由本層（Agent 起草）定義，存在「定義者弱化度量以規避 P5.W5」之誘因。 | 以 L6.18 反自我交易與 guard-the-guard 回應（Agent 不得為降低監督之核准主體、監督機制之修改本身受監督、OCV 不可自我洗白）；OCV 各分量選為可外部計數／比較之量、偏序可機器稽核；弱化 OCV 定義本身之修訂屬 P5.W5 不可豁免核心，須經 Steward `§8.1`。最終待 Steward `§8.2` 實質審查確認 OCV 未低估人類監督之真實維度。非豁免事項。DRAFT。 |
| **T-L6-6** | L6.17、L6.19、L6.20 | Learning／EV.12 之非侵蝕約束 vs 適應性；degrade vs halt 之濫用規避停機。 | L6.17 禁任何使 OCV 退步之 Learning 產物落地（適應性不得侵蝕否決能力）；L6.20 釘定 RT-4／不可逆一律 halt、degrade 僅限低階且不得延長自動鏈或降低核准層級。非豁免事項。DRAFT。 |

豁免登記：`none`（waivers: []）。本規格無現行豁免。

### CS.3 雙向 DEFER 承接表（`AUGUR-WM v1.0 §WM.43`）[N]

* **(a) 承接上層／Layer 5 之掛鉤（defers-in）**：`AUGUR-L5 v1.0` LDO.6→L6.1/L6.5/L6.7/L6.19/L6.21（LDI.1）；`AUGUR-L5 v1.0` LDO.2＋`AUGUR-KS v1.0` KDO.2＋`AUGUR-MC v1.3 §P5.E2`→L6.10/L6.11/L6.12（LDI.2）；`§P4.E7`→L6.14（LDI.3）；`§P5.W5`＋`§8.3`→L6.16/L6.17（LDI.4）；`AUGUR-ID v1.0` IDO.7→L6.9(d)（LDI.7）；`AUGUR-KS v1.0` KS.80–KS.82/Annex CL→L6.11（LDI.5）；`AUGUR-KS v1.0` KS.31/KS.34/KS.35→L6.3/L6.12（LDI.6）；`AUGUR-MC v1.3 §5` 角色五→§3–§8。與 front-matter `defers-in` 欄及 Annex LDI 三向對表。
* **(b) 下放下層之掛鉤（defers-out）**：LDO.1（否決信號物理傳輸／停止時延數值／kill-switch→L7）、LDO.2（Identity／授權鏈密碼學綁定／capability token→L7）、LDO.3（監督介面 UI／透明度載體→L7）、LDO.4（風險分級物理執法佈點→L7）、LDO.5（各 RT 級數值門檻登錄→L7/系統狀態）、LDO.6（特定框架／Planner／Orchestrator／Scheduler／LLM／受控介面實作→L7），與 front-matter `defers-out` 欄互為索引（見 Annex LDO）。

### CS.4 形式充分性（`AUGUR-WM v1.0 §WM.44`）[N]

依 `§WM.44` 判準自查：`AUGUR-MC v1.3` **全部** [N] 條款、`AUGUR-WM v1.0`／`AUGUR-ONT v1.0`／`AUGUR-ID v1.0`／`AUGUR-KS v1.0`／`AUGUR-L5 v1.0` **全部** [N] 條款，均須對應至本規格至少一 [N] 條款、或明記 DEFER 掛鉤、或明記「不觸及」及理由。

* **P5 家族〔核心〕**：Annex TR.A 已就 `§P5.D`／`§P5.E1`／`§P5.E2`／`§P5.W1`–`§P5.W5` 逐條枚舉（本層為 P5 家族主要落點）。
* **P4 家族**：Annex TR.B 已就 `§P4.D`／`§P4.W1`／`§P4.E1`–`§P4.E8` 逐條枚舉。
* **其餘 MC 條款**：Annex TR.C 逐條枚舉（PA／P1／P2／P3 家族、EV.1–EV.12、F1–F6、§0/§1/§2/§3/§4/§5/§6/§7/§8）。
* **WM／ONT／ID／KS／L5 條款**：Annex TR.D／TR.E／TR.F 以十位制區塊逐條枚舉落點（承接／細化／DEFER／不觸及＋理由）；多數上層本體條款之處置為「承接不觸及＋理由：屬 Layer 0–5 本體，L6 消費不重定義」。

**MC [N] 條款覆蓋清單（`§WM.44` 骨架自查，逐一具名以資機器盤點；落點見 Annex TR.A／TR.B／TR.C）[N]**：`PA`；`EV.1`、`EV.2`、`EV.3`、`EV.4`、`EV.5`、`EV.6`、`EV.7`、`EV.8`、`EV.9`、`EV.10`、`EV.11`、`EV.12`；`F1`、`F2`、`F3`、`F4`、`F5`、`F6`；`P1.D`、`P1.E1`、`P1.E2`、`P1.E3`、`P1.W1`；`P2.D`、`P2.E1`、`P2.E2`、`P2.E3`、`P2.E4`、`P2.E5`、`P2.W1`、`P2.W2`；`P3.D`、`P3.E1`、`P3.E2`、`P3.E3`、`P3.W1`、`P3.W2`；`P4.D`、`P4.E1`、`P4.E2`、`P4.E3`、`P4.E4`、`P4.E5`、`P4.E6`、`P4.E7`、`P4.E8`、`P4.W1`；`P5.D`、`P5.E1`、`P5.E2`、`P5.W1`、`P5.W2`、`P5.W3`、`P5.W4`、`P5.W5`；`§0`、`§0.1`、`§0.2`、`§0.3`、`§0.4`、`§0.5`、`§0.6`、`§1`、`§1.1`、`§1.2`、`§1.3`、`§2`、`§3`、`§4`、`§5`、`§6`、`§7`、`§8`、`§8.1`、`§8.2`、`§8.3`、`§8.4`、`§8.5`、`§8.6`。各 `Pn.Y`（`P1.Y`、`P2.Y`、`P3.Y`、`P4.Y`、`P5.Y`）為 [I] 說理條款，本層以「不觸及＋理由：屬各原則之風險說理，非規範義務落點」統一處置，惟為骨架覆蓋完備計於此具名。

**逐條對應矩陣已作成——形式充分性之形式面已備；Steward 充任認定業經作成、`§8.2` 實質人類審查已作成，本規格自 2026-07-17 起以 v1.0 生效**（Steward 裁決第 2026-007 號、AL-2026-011；見【地位】、TR.Z），**殘餘生效阻卻已解消**；**Steward `§8.2` 違憲審查權就 residual 事項完整保留**（RULING-2026-007:43）。上層升版或條款增修時本矩陣對應列**必須**同步維護（L6.91 diff 檢查），否則聲明重回不完整。本子代理不自行宣稱任何規格已生效、不自行登錄正式 Amendment Log；本規格之生效及其登錄（AL-2026-011）均為 Steward 之裁決行為。

---

## Annex EO [N] — 自創評價性謂詞判準彙整

> **EO.1（判準彙整表）[N]** 本規格自創或操作化之評價性謂詞，依 `AUGUR-MC v1.3 §8.3` 可判定性元規則，逐一附可判定判準：
>
> | 謂詞 | 出處 | 可判定判準 |
> |---|---|---|
> | 「不可逆」（irreversible） | L6.9 | 無經宣告且可由 Observation 驗證之有界成本／時間回復 Action（compensating Action）者推定不可逆（R3）；缺宣告即保守 |
> | 「高影響」（high-impact） | L6.9、L6.10 | 受影響已解析 Identity 數量／物理資源量／安全法律財務暴險跨越登錄門檻，或涉自然人（`§P1.E3`）敏感 Identity，或逾越單一 Plan 邊界之外部主體（I3）；缺宣告即保守。**經認定為高影響（I3）之實體世界 Action 恆歸最高風險級 RT-4，不論可逆性**（`§P5.W3`「不可逆_或_高影響」之「或」使高影響單獨觸發最高級，L6.10／L6.13）；`§P5.E2` 分級權僅及認定，不得反用以降級核准 |
> | 「高風險 Action」（high-risk） | L6.10 | ＝RT-3 或 RT-4（全憲章同一分級，`§P4.E7`／`§P5.W3` 共用）；缺位未分級之實體世界 Action 推定 RT-4 |
> | 「人類權威根節點」（Human Authority root） | L6.5 | 授權鏈可遞迴遍歷終止於單一已解析人類 Identity（決策者 Human）之顯式授予，無環、根非 Agent |
> | 「授權鏈可追溯」（authorization-traceable） | L6.5、L6.7 | 授權鏈為 DAG，每節點可遍歷至其授予來源並終止於人類根節點；Gate 於每一 Action 驗證 |
> | 「Agent-獨立否決通道」（Agent-independent veto channel） | L6.8 | 否決通道在結構上不受被控 Agent 停用／延遲／攔截／降級，每一進行中 Action 恆常可達 |
> | 「降低人類監督與否決能力」（erosion of oversight/veto） | L6.16、L6.17 | 以 OCV=(V,D,A,H,T,C) 保護方向偏序判定；某風險級之 V／D／A／T 遞減或 H／C 遞增即為降低；可機器稽核 |
> | 「人類確認者之獨立」（confirmer independence） | L6.14 | 非發起／規劃該 Action 之同一 Identity，RT-4 另需與 Actor 非共享主體，以 Identity lineage 機器稽核 |
> | 「最小權限之逾越」（least-privilege violation） | L6.15 | Agent 權限集合非為當前經授權 Plan 所需集合之子集，或 Plan 完成後未收回 |
> | 「熔斷之受影響範圍」（fail-safe blast radius） | L6.20 | 自錯誤 Representation／Evidence 沿 Evidence 溯源鏈與 Identity 依賴之遞迴傳遞閉包 |
> | 「缺宣告即保守」（conservative-on-omission） | L6.9(c)、L6.10 | 可逆性／影響／門檻未經可機器解析之宣告者，一律推定最高風險分支（R3×I3／RT-4，`§8.3`） |
>
> **掃描—完備性義務（[N]，比照 `AUGUR-WM v1.0` Annex E1／`AUGUR-KS v1.0` EO.1）**：本規格正文如增列自創或操作化之評價性謂詞，**必須**同步收錄本 EO.1 表；未收錄且未附判準者採保守解釋（存疑即不允許，`§8.3`）。
> **義務主體**：本規格、一切消費本規格謂詞之下層規格。**可判定判準**：全文評價性謂詞逐一於本表有列（或其判準明記 DEFER 落點）者為完備；本表每一謂詞之判準可機器適用；未收錄且未附判準之謂詞，採保守解釋。

---

*本規格計：正文條款 L6.1–L6.24（核心行動治理）＋L6.90–L6.92（文件治理；L6.25–L6.89 為十位制保留區塊）、Annex LDI（LDI.0–LDI.6）、Annex LDO（LDO.0–LDO.6）、Annex L67（L67.0）、Annex TR（TR.0、TR.A–TR.F、TR.Z）、Annex CS 合規聲明（CS.1–CS.4）、Annex EO（EO.1）。全文以繁體中文為權威文本（§0.4）。本文件為 **v1.0 生效版本**：Constitution Steward（人類 tsaitsangchi）已依 `AUGUR-MC v1.3 §8.1` 作成充任認定，並依 `§8.2` 作成實質合憲人類審查，自 2026-07-17 起生效（Steward 裁決第 2026-007 號、AL-2026-011；【地位】、L6.90）。**Steward `§8.2` 違憲審查權就 residual 事項完整保留**（RULING-2026-007:43）。本規格之生效及其登錄均為 Steward 之裁決行為，非本子代理所得宣稱或代行。本層由 Agent 起草而規範人類對 Agent 之權威，一切條款以機器可稽核地強化人類監督與否決能力為硬設計約束（【地位】、L6.16–L6.18）。*

**核心產物索引 [I]**：Action 問責結構＝§3（L6.1 六元組不變式／L6.2 單一已解析歸責／L6.3 Knowledge Basis 門檻／L6.4 self-reported 回流）；授權鏈與人類權威＝§4（L6.5 人類根節點／L6.6 委派失效可撤銷／L6.7 EV.9 Gate 強制驗證／L6.8 Agent-獨立否決通道）；風險分級＝§5（L6.9 可逆性影響判準／L6.10 RT-0–RT-4／L6.11 完備性門檻／L6.12 Confidence 門檻／L6.13 核准流程／L6.14 確認者獨立／L6.15 最小權限單調）；監督度量＝§6（L6.16 OCV 定義／L6.17 單調棘輪／L6.18 反自我交易 guard-the-guard）；行動迴路與熔斷＝§7（L6.19 EV.8–EV.12／L6.20 熔斷 halt/degrade）；執法與防線＝§8（L6.21 F6 執法點／L6.22 F3 防線／L6.23 分界紀律／L6.24 謂詞錨定）；DEFER 表＝Annex LDI／LDO；WM.44 矩陣＝Annex TR。

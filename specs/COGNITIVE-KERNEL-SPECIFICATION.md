# 《Augur Cognitive Kernel Specification》

Augur Enterprise AI Operating System
認知核心規格（Layer 5 — Cognitive Kernel／World Understanding Engine）
引用縮寫：**AUGUR-L5**｜版本：**v1.0（§8.2 條件通過，RULING-2026-029，2026-07-23；provisional 已解除——沿革：形式充分性經矩陣重作＋L5.10 as-of 條款回復，Steward 2026-07-19 RULING-2026-023 重採認〔乙〕）**（前版：v0.1-draft）
受 **AUGUR-MC v1.4** 全文約束（`AUGUR-MC v1.4 §0.6(a)` lex superior、`§0.5` 對照表 Layer 5 欄）
並受 **AUGUR-WM v1.0**（Layer 1）、**AUGUR-ONT v1.0**（Layer 2）、**AUGUR-ID v1.0**（Layer 3）、**AUGUR-KS v1.1**（Layer 4）全文約束（`AUGUR-MC v1.4 §0.6(a)`）

---

> ## 【地位】[N]
>
> 本文件為 **v1.0 生效版本**（§8.2 條件通過，RULING-2026-029，2026-07-23；provisional 已解除）。Constitution Steward（tsaitsangchi）已於 2026-07-17 依 `AUGUR-MC v1.4 §0.5`、`§8.6` 作成**充任認定**（Steward 裁決第 2026-006 號，Amendment Log AL-2026-010）：本文件充任 `AUGUR-MC v1.4 §0.5` 對照表 Layer 5 欄所轄規格（Cognitive Kernel Specification、Reasoning Engine、AI Model Selection），**自 2026-07-17 起生效**。
> * **⚠️ 充任性質（誠實揭露，2026-07-17 原文——見下方 2026-07-18 撤回聲明）**：本充任僅就 **`§WM.44` 形式充分性**（Annex TR 逐條完整枚舉、缺 0 條〔**此宣稱已於 2026-07-18 三鏡對抗審查證偽**〕）與 **linter 結構關卡**（`§WM.40–43` PASS、error 0）＋**獨立代理對抗審查**作成。**`§8.2` 實質合憲人類審查經 Steward 指示延後（deferred）、本充任不含實質合憲之人類簽核**；規格為 **provisional、待調整**。Steward 之 `§8.2` 違憲審查權完整保留，得隨時提起並修正。此揭露依 Steward 2026-07-17「先產生、我先授權你簽、之後再調整」之明示授權（形式關卡批次充任、§8.2 延後）。
> * **🛑 形式充分性認定撤回（2026-07-18，RULING-2026-019 決策二）**：本規格首次三鏡對抗審查（Opus 4.8，工作流 wf_5335a68e-191）**存活 6 項 major**——其最嚴重者為**直接上游 `AUGUR-KS` 全份未進 Annex TR 矩陣**（`grep '^| KS' 零命中`）、WM Annex D `D1–D6` 六列全漏、`LDI.5` 宣稱承接 as-of 卻於 `L5.2` 零落點（幽靈落點）。故上開「Annex TR 逐條完整枚舉、缺 0 條」之形式充分性成就**不成立**。Steward 據此**撤回本規格之形式充分性認定**，本規格降為 **provisional·充任暫停（矩陣重作中）**。**§8.1 橋接**：為免級聯撼動 M2，Steward 依 `§8.1` 解釋——**Layer 6、Layer 7 於本規格矩陣重作窗（硬期限 2026-10-14）內，得續引 `AUGUR-L5 v1.0` 為合法上層**，其自身生效地位不因本撤回而失格；逾期未重作，另依 `§8.2` 處置。矩陣重作與 `§8.2` 實質審查為本規格回復完整 v1.0 之前置。〔**✅ 重採認（2026-07-19，RULING-2026-023 乙）**：6 major 之矩陣/內容面皆處置（KS 全份入 TR.F、WM D1-6 補、as-of 幽靈→L5.10 真落點、版本 v1.1），四輪 G5 複驗確認全 corpus 一致；Steward 重採認 L5 回 **provisional 充任**（§8.2 延後）。**§8.1 橋接功成身退**——L6/L7 引 L5 回歸常態，不再依賴橋接。〕
> * **✅ §8.2 實質審查條件通過（2026-07-23，RULING-2026-029／AL-2026-032）**：RULING-2026-006 保留段（L5.1/L5.2/L5.3/L5.4/L5.6/L5.7＋CS.2 六緊張、尤 T-L5-6）＋RULING-2026-023〔乙〕追加（L5.10）之八項必審，經 Steward 2026-07-23 一攬子裁定——(i)(ii)(iii)(iv)(vi) 核定照收、(vii) 核定＋T-L5-6 定性追認、(v)(viii) 條件通過（附條件＝L5 單層 ultracode PRV／ASF 複核；F-IX-4／F-IX-6 簿記另案 minor——**已於 RULING-2026-038／AL-2026-042 閉合**）。**本規格自 provisional 轉 v1.0 生效，`§8.2` 深度審查作成（非續延）**。復審日曆仍 **2026-10-14**（與 L7 residual 併結）。
> * **✅ ultracode PRV／ASF 程序性閉合（2026-07-23，RULING-2026-035／AL-2026-039）**：L5 單層 ultracode 已執行 PRV／ASF 複核——**未翻 major**（零 major；medium×2＋minor×4 同案 patch）；029 附條件 (v)(viii) **程序性閉合**、不重開 `§8.2`。
> * **上層地位**：AUGUR-MC v1.4（L0）、AUGUR-WM v1.0（L1）、AUGUR-ONT v1.0（L2）、AUGUR-ID v1.0（L3）、AUGUR-KS v1.1（L4）均已生效，承接前提全部成就。`v0.1-draft` 原文歸檔於 `specs/COGNITIVE-KERNEL-SPECIFICATION-v0.1-draft.md`；draft → v1.0 之變更僅限：版本欄、本【地位】節生效記錄、Annex CS front-matter spec-version，**無任何 [N] 條款實質變更、編號不重排**。
> * 本文件全部 [N] 條款自生效日起對 Layer 6–7 規格產生規範效力；下層依 `AUGUR-L5 v1.0 §{條款}` 格式引用。落實審計 AUD-18（per-結論解釋面）等。
> * **條款編號穩定性**（`AUGUR-MC v1.4 §8.6`、`AUGUR-WM v1.0 §WM.46`）：一經發布永不重用、永不重排；廢止條款保留編號並標 `(repealed)`。
>
> 本【地位】節與 §0 全部約定為 [N] 規範內容，其效力與正文條款同（準用 `AUGUR-WM v1.0 §WM.53`）。
>
> **概念層與執行層交界之提示（`AUGUR-MC v1.4 §0.6(b)`、`§7`）**：Layer 5 為**概念層與執行層之交界**。本層定義「何為合法推理」「Confidence 如何沿鏈傳播」「Hypothesis 之地位」「解釋義務」「AI model 為工具非世界權威」等**推理之概念不變式**，**不綁定任何特定模型／向量庫／統計庫**；具體 AI model／向量庫／統計庫等物理構件之選定**下放 Layer 7**（Annex LDO）。本層全部定義通過**刪名測試**（刪去任一具名 model／向量庫／統計庫後，條款規範內涵不變）。

---

## 目錄 [I]

| § | 標題 | 條款 | 核心錨定 |
|---|---|---|---|
| §0 | Document Status & Conventions | — | `MC §0`、`WM §0`、`KS §0` |
| §1 | Purpose, Scope & Layer Position | — | `MC §5` 角色四、`§0.6(b)` |
| §2 | 承接與非管轄（Defers-In & Non-Encroachment） | Annex LDI | `KS` Annex DO、`WM` HOOK-02/03 |
| §3 | 合法推理與 Evidence 引用鏈 | L5.1、L5.2 | `MC §2.7`、`§2.11`、`§P4.E6` |
| §4 | Confidence 沿推理鏈之傳播 | L5.3 | `MC §P4.E8`、`§P4.E7`；`KS` KDO.1 |
| §5 | Hypothesis 之地位與升級紀律 | L5.4、L5.5 | `MC §1.3`、`§P4.E4`；`WM` HOOK-02/03 |
| §6 | Explanation 義務 | L5.6 | `MC F5`、`§P4.E1`、`§P4.E6` |
| §7 | AI Model 為工具而非世界權威 | L5.7 | `MC F2`、`§P2.E2`、`§7` |
| §8 | 分界紀律與 resolution 定性；as-of 推理消費 | L5.8、L5.9、L5.10 | `MC §5` 角色四、`§0.6(b)`；`KS` KS.100/101 |
| §9 | 文件治理與合規存續 | L5.90–L5.92 | `WM.39–46` |
| Annex LDI [N] | 承接上層／Layer 4 DEFER 掛鉤（defers-in） | LDI.0–LDI.7 | `KS` KDO.1/3/4/6、`WM` HOOK-02/03 |
| Annex LDO [N] | 下放下層 DEFER 掛鉤（defers-out） | LDO.0–LDO.6 | → L6／L7 |
| Annex L46 [N] | 與 Layer 4／Layer 6／Layer 7 之分界表 | L46.0 | reasoning／risk tier／physical |
| Annex TR [N] | WM.44 逐條對應矩陣（MC＋WM＋ONT＋ID → L5） | TR.0、TR.A–TR.E、TR.Z | `WM.44` |
| Annex CS [N] | Constitutional Compliance Statement | CS.1–CS.4 | `WM.39–45` |
| Annex EO [N] | 自創評價性謂詞判準彙整 | EO.1 | `§8.3` 可判定性元規則 |

編號穩定性：正文採 **L5.{n}**（**L5.1–L5.9** 為核心推理引擎條款；**L5.10** 已啟用（as-of 推理消費，RULING-2026-019 決策二重作／RULING-2026-023〔乙〕重採認）；**L5.11–L5.89** 為十位制保留區塊，空號為保留、非跳號；**L5.90–L5.99** 為文件治理與合規存續條款）；Annex 各前綴 **LDI.{n}／LDO.{n}／L46.{n}／TR.{n}／CS.{n}／EO.{n}**；一經發布永不重用、永不重排（`AUGUR-MC v1.4 §8.6`、`AUGUR-WM v1.0 §WM.46`）。

---

## §0 Document Status & Conventions（文件地位與約定）[N]

### 0.1 名稱、層級與版本 [N]

* 名稱：Augur Cognitive Kernel Specification（下層引用簡稱 **AUGUR-L5**）
* 層級：Layer 5 — Cognitive Kernel／World Understanding Engine（`AUGUR-MC v1.4 §0.5` 對照表第 5 列；`§5` 角色四）
* 版本：v1.0（§8.2 條件通過，RULING-2026-029；前版：v0.1-draft、充任時 provisional）
* 上層規格（upper-specs）：`AUGUR-MC v1.4`（Layer 0）、`AUGUR-WM v1.0`（Layer 1）、`AUGUR-ONT v1.0`（Layer 2）、`AUGUR-ID v1.0`（Layer 3）、`AUGUR-KS v1.1`（Layer 4）
* 生效要件：見【地位】節（已全部成就；Steward 裁決第 2026-006 號，AL-2026-010，生效日 2026-07-17）。**`§8.2` 深度實質審查已於 2026-07-23 條件通過（RULING-2026-029／AL-2026-032）**——八項必審裁定、provisional 轉 v1.0；附條件（ultracode PRV／ASF 複核、簿記另案 minor）之復審期限 2026-10-14。

### 0.2 規範用語約定 [N]

沿用 `AUGUR-MC v1.4 §0.2`：**必須**（MUST，絕對義務）／**不得**（MUST NOT，絕對禁止）／**應**（SHOULD，偏離須書面說明理由）／**得**（MAY，允許而不構成義務），全文一致，不重定義。

### 0.3 條文效力標注與編號穩定性 [N]

* 每章標題標注 **[N]（Normative，規範性）** 或 **[I]（Informative，資訊性）**。[N] 與 [I] 內容不一致時，依 `AUGUR-MC v1.4 §8.2` 以 Normative 為準；章標題標注為該章預設，子節另有標注者以子節為準。
* 正文條款編號採 **L5.{n}**：**L5.1–L5.9** 為核心推理引擎條款；**L5.10** 已啟用（as-of 推理消費——推理之時間邊界與 anti-leakage，§8）；**L5.11–L5.89** 為十位制保留區塊（空號為保留、非跳號，保留號之啟用亦永不重用、永不重排）；**L5.90–L5.99** 為文件治理與合規存續條款。Annex 條款前綴：Annex LDI（承接掛鉤）採 **LDI.{n}**、Annex LDO（下放掛鉤）採 **LDO.{n}**、Annex L46（分界表）採 **L46.{n}**、Annex TR（追溯矩陣）採 **TR.{n}**、Annex CS（合規聲明）採 **CS.{n}**、Annex EO（謂詞判準）採 **EO.{n}**。
* 條款編號一經發布**永不重用、永不重排**；廢止條款保留編號並標注 **(repealed)**（`AUGUR-MC v1.4 §8.6`、`AUGUR-WM v1.0 §WM.46`）。
* **附屬表列 [N] 內容之義務承載規則**：附屬於某治理條款（如 LDI.0、LDO.0、L46.0、TR.0、CS.1 各節、EO.1）之表列 [N] 內容，其義務主體與可判定判準由該治理（父）條款統一承載，不另逐列重複標注（此為體例落實，非豁免）。

### 0.4 權威語言聲明 [N]

本規格以**繁體中文版為權威版本**；規範性術語於正文中一律使用英文原詞（Reality、Observation、Representation、Identity、Evidence、Knowledge、Confidence、Action、Agent、Intelligence；及本層機制術語 Reasoning、Inference、Hypothesis、Explanation、Confidence Lattice、Grading Method、Trust Rank、assumption、provenance、synthetic、self-reported、meet、GATE、out-of-sample／OOS、per-conclusion explanation face），與 `AUGUR-MC v1.4 §0.4`、上層各規格 `§0.4` 保持術語同一性；不另立中文譯名為規範對象。

### 0.5 引用格式與元規則 [N]

* 引用格式：`AUGUR-MC v1.4 §{條款}`／`AUGUR-WM v1.0 §{條款}`／`AUGUR-ONT v1.0 §{條款}`／`AUGUR-ID v1.0 §{條款}`／`AUGUR-KS v1.1 §{條款}`。下層引用本規格採 `AUGUR-L5 v{version} §{條款}`。
* 本規格每一 [N] 條款標注其**憲章／上層錨定**與**三態型態**：**refines**（細化上位條款）／**carries**（承接上位不變式並給予概念層結構位置）／**hooks**（DEFER 掛鉤，載明目標 Layer 與授權條款），並額外以**承接**標注 Layer 4（AUGUR-KS）明示下放本層之掛鉤；複合模式以「＋」連接。每一 [N] 條款並標注**義務主體**與**可判定判準**，使其可機器稽核（承接 `AUGUR-WM v1.0 §WM.34`、`AUGUR-KS v1.1 §0.5`）。
* **不重定義元規則**：本規格**不得**重新定義 `AUGUR-MC v1.4 §2` 之術語（尤 `§2.5` Evidence、`§2.6` Knowledge、`§2.7` Intelligence、`§2.10` Confidence、`§2.11` Evidence 通道），亦**不得**重定義 `AUGUR-WM v1.0`／`AUGUR-ONT v1.0`／`AUGUR-ID v1.0`／`AUGUR-KS v1.1` 之既有構件（尤 `AUGUR-KS v1.1` 之 Confidence Lattice L_C 之序與語義、Evidence 分類法、Trust Rank、Completeness Level）；本規格僅得就其明示下放者作**概念層填充**，且僅限於推理之概念不變式。
* **概念層獨立性**（`AUGUR-MC v1.4 §0.6(b)`、`§7`）：Layer 5 雖為概念層與執行層之交界，本層之**定義**仍屬概念層，**不得**引用 Layer 7 執行層構件（特定 AI model、向量庫〔vector DB〕、統計庫、機率演算庫、序列化格式、Agent Runtime、儲存引擎）作為任何定義之依據。本層所稱「推理」「推論」「傳播」「解釋」均為**概念層形式**（合法性、上限、義務之明文可判定性）；其物理載體一律下放 Layer 7（Annex LDO）。

---

## §1 Purpose, Scope & Layer Position（目的、範圍與分層定位）[N]

### 1.1 Layer 5 定位 [I]

`AUGUR-WM v1.0` 宣告**世界有何物**（存在層）；`AUGUR-ONT v1.0` 宣告**其類屬與同一性判準**（型別層）；`AUGUR-ID v1.0` 負責**個體之永久參照與其一生機制**（個體層）；`AUGUR-KS v1.1` 定**繫結該參照之斷言之信度、欄位、失效、矛盾、溯源與 as-of 重建能力**（Knowledge 層）。**本層＝Cognitive Kernel／World Understanding Engine**：依 `AUGUR-MC v1.4 §5` 角色四負責 **Reasoning／Inference／Hypothesis／Explanation**；`§0.5` 所轄「Cognitive Kernel Specification、Reasoning Engine、AI Model Selection」。本層定**推理之概念不變式**——何為合法推理、Confidence 如何沿鏈傳播、Hypothesis 之地位、解釋義務、AI model 為工具非世界權威——而**消費** Layer 4 之 L_C、Evidence 分類法與 Trust Rank，**不重定義**之。

### 1.2 交界層之雙面性 [I]

Layer 5 為概念層與執行層之交界，具「所轄卻下放」之雙面性：**AI model 選型為 L5 所轄之概念**（何為合法之推理工具、其輸出之地位），但**具體 model／向量庫／統計庫之物理選定下放 Layer 7**（`AUGUR-MC v1.4 §7` 技術中立、`§0.6(b)`）。此雙面性易被誤讀為本層可綁定模型；本層於條款層以**刪名測試**（`AUGUR-KS v1.1 §0.6` KS.4 同構）與 `§7` 技術中立反覆防守（見 L5.7、L5.8、T-L5-1、T-L5-6）。

---

## §2 承接與非管轄（Defers-In & Non-Encroachment）[N]

本層承接 `AUGUR-KS v1.1` Annex DO 明示下放之掛鉤（尤 **KDO.1**：Confidence 傳播聚合之推論實作、resolution 演算之 inference 實作；**KDO.3**：外部知識入 World Representation 之推論工作流〔HOOK-02〕、GATE 統計計算實作〔HOOK-03 演算面〕；**KDO.4**：未解析存量量測落地之 L5 面向；**KDO.6**：as-of gate／purged／embargo 查詢引擎操作化之 L5 面向），及 `AUGUR-WM v1.0` HOOK-02／HOOK-03 之推論面向；逐一於正文對應（見 Annex LDI）。本層為 Layer 5 唯一所轄之概念層規格，不自行擴張管轄：凡屬 Layer 0–4 之概念（Reality／Representation／Identity／Knowledge 之語義、L_C 之序、Trust Rank、完備性等級）本層**僅消費不重定義**；凡屬 Layer 6–7 之事項（風險分級表、消費門檻、確認者資格、物理選型、UI）本層**僅設 DEFER 掛鉤**（Annex LDO），不代行定義。

---

## §3 合法推理與 Evidence 引用鏈 [N]（`§2.7`、`§2.11`、`§P4.E6`）

> **L5.1（合法推理之定義——推理產物為候選斷言，非權威真值）[N｜carries｜`AUGUR-MC v1.4 §2.7`、`§2.11`、`§P2.W2`；refines｜`§P2.E2`；承接｜`AUGUR-KS v1.1` KS.20、KS.30]**
> Reasoning／Inference 為 Intelligence（`§2.7`「產生新斷言或行動方案之任何過程」）之子集。任何推理產物（推論結論、檢索合成、假設、identity resolution 之產出）**僅得**以攜帶 Evidence 與 Confidence 之**候選斷言**（proposed assertion，`§2.11`）進入系統；非經 **Evidence 通道**（`§2.11`，標準鏈節選 EV.2–EV.5：Observation→Representation→Identity→Evidence）確立，**不得**成為權威 World Representation 或 Knowledge（`§P2.W2` 權威順序非時間順序、`§P2.E2` model output 不得逕成 Truth）。確立後之 Knowledge 其五元組欄位（Source／Timestamp／Identity／Evidence／Confidence）承接 `AUGUR-KS v1.1` KS.20，Confidence 取值於單一信度格 L_C（`AUGUR-KS v1.1` KS.30），本層僅消費、不重定義其序與語義。
> **義務主體**：本規格、Layer 5–7 一切推理構件。**可判定判準**：存在任一推理產物未經 Evidence 通道逕寫入權威 Representation／Knowledge 者，違反本條（引用鏈可機器稽核，`§8.3`、`AUGUR-KS v1.1` KS.70）。

> **L5.2（Inference 之 Evidence 引用鏈完整性——雙合法終點）[N｜carries｜`AUGUR-MC v1.4 §P4.E6`、`§8.3`；refines｜`AUGUR-KS v1.1` KS.70]**
> 每一 Inference 結論**必**產生（或引用）一 Evidence 節點；其引用鏈**必**遞迴終止於二合法終點之一：**對 Reality 之 Observation**，或**明示宣告之假設**（assumption，`§P4.E6`、`AUGUR-WM v1.0 §WM.33`）——二者為**窮盡且互斥**之合法終點集。**禁循環引證**（引用鏈為 DAG，`AUGUR-KS v1.1` KS.70）。推論規則（inference rule）自身為證據鏈之一環，須可溯源（斷言主體含版本、產生活動、上游依據，`§P4.E6`），其信任等級併入最弱環節計算（NoLaundering，`§P4.E7`、`AUGUR-KS v1.1` KS.73）。此為 `§8.3`「Knowledge→Evidence→Observation 或明示假設之引用鏈完整性必須可機器稽核」之 Layer 5 落實。
> **義務主體**：本規格、Layer 5–7 承載構件。**可判定判準**：任一結論之 Evidence 鏈存在有限步可遍歷之路徑終止於 Observation／assumption、且無環者合規；終止於二合法終點以外之節點（如另一未溯源結論、白名單外臆測）者，違反本條。

---

## §4 Confidence 沿推理鏈之傳播 [N]（`§P4.E8`；承接 `AUGUR-KS v1.1` KDO.1）

> **L5.3（Confidence 沿推理鏈之傳播——承接 KDO.1，硬守 KS.34 上限）[N｜refines｜`AUGUR-MC v1.4 §P4.E8`；carries｜`AUGUR-KS v1.1` KS.34；承接｜`AUGUR-KS v1.1` Annex DO KDO.1]**
> 本層承接 `AUGUR-KS v1.1` 下放掛鉤 **KDO.1**，定義 Confidence 傳播之具體**聚合語義與推論實作**（含多獨立證據之增強等聚合算子）。**硬約束**：任一結論之聚合 Confidence **必** ⊑ 其前提集合與所據推理規則之 Confidence 之**下確界**（meet，⊓；`AUGUR-KS v1.1` KS.34）；聚合增強**不得逾越**此上限（`§P4.E7` NoLaundering 之格代數落實）。增強之合法空間**僅及於不逾 meet 之範圍**。每一經傳播產生之 Confidence 值**須**攜其 **Grading Method** 之 provenance（評定方法標識／輸入／參數／版本，`AUGUR-KS v1.1` KS.32）。本層**不重定義** L_C 之序與語義（Layer 4 專屬，僅消費）。
> **義務主體**：本規格、一切傳播 Confidence 之構件。**可判定判準**：存在任一聚合結果嚴格大於其鏈上任一環節 Confidence（⋢ meet 上限）、或裸 Confidence 值（無 Grading Method）者，違反本條（承 `AUGUR-WM v1.0 §WM.34(a)` 引用鏈遍歷可稽核）。

---

## §5 Hypothesis 之地位與升級紀律 [N]（`§1.3`、`§P4.E4`；承接 `AUGUR-KS v1.1` KDO.3）

> **L5.4（Hypothesis 之地位——未證斷言、可謬、須顯式標記）[N｜carries｜`AUGUR-MC v1.4 §1.3`、`§P4.E4`；refines｜`AUGUR-WM v1.0 §WM.33`；承接｜`AUGUR-KS v1.1` KS.38、KS.74]**
> Hypothesis 為**未證之候選斷言**。其 referent 為所繫結 Identity 之**可能狀態**，屬合法模態內容（`§1.3`），惟**必**顯式標記為模態內容／assumption（`AUGUR-WM v1.0 §WM.33`），**不得**作為現實狀態之斷言。Hypothesis **可謬**（`§P4.E4`）：其 Confidence **不得**為隱含之 1.0、**不得**標記為不可修正；未經 Evidence 通道確立前，Confidence 保守推定為底錨 **INSUF**（`AUGUR-KS v1.1` KS.38）。模態／assumption 標記為**永久屬性**，不因轉引消失（承 synthetic 永久性精神，`AUGUR-KS v1.1` KS.74）。
> **義務主體**：本規格、Layer 5–7 構件。**可判定判準**：存在未標記之 Hypothesis 被消費為現實狀態斷言或 Knowledge 依據者、或標記之 Hypothesis 未經通道確立而其 Confidence 升逾 INSUF 者，違反本條。

> **L5.5（Hypothesis 不得無證升級——承接 KDO.3〔HOOK-02／HOOK-03 之 L5 面向〕）[N｜carries｜`AUGUR-WM v1.0` HOOK-02、HOOK-03、`§A.48`、`§A.52`；refines｜`AUGUR-MC v1.4 §P2.W2`；承接｜`AUGUR-KS v1.1` KDO.3、KS.84]**
> 本層承接 `AUGUR-KS v1.1` 下放掛鉤 **KDO.3**，定外部知識／思想入 World Representation 之推論工作流：外部思想（哲學、經驗法則）**僅為候選假說之生成視角**，其入徵須經「**可證偽 → 樣本外（OOS）驗證 ＋ 經濟裁決**」之工作流（`AUGUR-WM v1.0` HOOK-02），且經 Evidence 通道確立方得升為 Knowledge 依據。思想中之**特定數值不得直接進入特徵公式**（`§A.48`：hardcoded 值＝注入無 Evidence 之斷言，違 `§P4.W1`）。GATE 預註冊可證偽實驗之**統計計算實作**（家族錯誤率／多重比較調整、判準凍結、二次證偽封鎖之演算，HOOK-03）由本層落地；**惟其概念層約束**（Grading Method 一維、as-of 判準凍結、supersede 特例）之**設計權屬 Layer 4**（`AUGUR-KS v1.1` KS.84），本層僅實作演算、**不改其約束語義**。升級後 Confidence 守 NoLaundering 上限（L5.3）。
> **義務主體**：本規格、一切產生假說／GATE Evidence 之構件。**可判定判準**：假說未達 GATE 成就（OOS＋經濟裁決／預註冊可證偽）而升為 Knowledge 依據者、或 GATE verdict 之統計計算未載明多重比較調整、或判準經事後改動而未降完備性等級者，違反本條。

---

## §6 Explanation 義務 [N]（`F5`、`§P4.E1`、`§P4.E6`；承接審計 AUD-18）

> **L5.6（Explanation 義務——per-結論可解釋，F5 之落實，承接 AUD-18）[N｜carries｜`AUGUR-MC v1.4 F5`、`§P4.E1`、`§P4.E6`；承接審計｜AUD-18]**
> 每一推理結論（prediction／recommendation／decision）**必**可回答「為什麼」，落實禁令 **F5**（Intelligence Without Evidence）。本層定 **per-結論解釋面**（per-conclusion explanation face）為不變式：每一結論之解釋**必**可解析至**四要素**——(i) 所繫結之**已解析 Identity**（回答「為什麼是這一個個體」，直接補正 **AUD-18**「per-pick 解釋面缺席」之缺口）；(ii) 其 **Evidence 集合及各自 Trust Rank**（`§P4.E1` 五問之「依據為何」；`AUGUR-KS v1.1` KS.72）；(iii) 所據**推理規則**（推論如何自前提得出結論）；(iv) 其 **Confidence 值與 Grading Method**（「多可信／如何評定」；`AUGUR-KS v1.1` KS.32）。**Computational Evidence 路徑**（`AUGUR-KS v1.1` KS.71，L5.7）：(iii) **最低滿足**＝可重放之輸入→輸出映射（含推理時輸入 Evidence 集識別）＋所用 model／演算法版本（與 (iv) Grading Method provenance 對齊，但 (iii) 須可機械盤點「自何輸入得何輸出」，**不得**以 (iv) 單獨替代 (iii) 之存在性）；attention／權重等不可讀內部狀態**不**構成本層 (iii) 必要內容——feature attribution 之呈現 DEFER Layer 7（LDO.3 延伸）。**解釋粒度必達個體層**——僅能答至 model／方法層而答不到「為什麼是這一個個體」者，解釋面不完整。解釋須為系統**可機械轉述之真實依據**，**不得**由生成模型事後編造（禁「模型分數高」式之無實據解釋）。解釋之呈現／交付格式與 UI 屬 Layer 7（下放，LDO.3；L6 僅監督 UI）。
> **義務主體**：本規格、Layer 5–7 產生結論之構件。**可判定判準**：存在任一結論其解釋無法解析至上開四要素、或僅止於方法層無 per-結論個體層解釋者，違反本條（可對結論集逐筆機器盤點）。

---

## §7 AI Model 為 Reasoning 之工具而非世界權威 [N]（`F2`、`§P2.E2`、`§7`）

> **L5.7（AI Model 為 Reasoning 之工具而非世界權威——F2 Model First 之防線）[N｜carries｜`AUGUR-MC v1.4 F2`、`§P2.E2`、`§7`；refines｜`AUGUR-KS v1.1` KS.74、Annex EV EV.2]**
> AI model 為 **Reasoning 之工具，非世界權威**。Model output **不得**未經 Evidence 通道（`§2.11`）逕成權威 World Representation 或 Knowledge（`§P2.E2`）；model output 歸類為 **Computational Evidence**（`AUGUR-KS v1.1` KS.71），**永久攜 synthetic 標記**（`AUGUR-KS v1.1` KS.74），其來源信任分級 Trust Rank 天花板為 **TR-C**（映入 L_C 至多 MODERATE，須具校準 Grading Method provenance；`AUGUR-KS v1.1` Annex EV EV.2），且**不得單獨**為高風險 Action 之依據（須至少一項獨立 Data Evidence 或人類確認，`§P4.E7`／`AUGUR-KS v1.1` KS.76）。**禁 F2 Model First 架構**（先選 AI model 再設計系統）。本層僅定推理之概念不變式，**不綁定任何特定模型**（`§7` 長期穩定性：不依賴特定 AI model）；具體 model／向量庫／統計庫之物理選型下放 Layer 7（LDO.1）。
> **義務主體**：本規格、Layer 5–7 一切消費 model output 之構件。**可判定判準**：存在 model output 未經通道逕成權威 Knowledge、或未攜 synthetic 標記、或映入 L_C 逾 TR-C 天花板、或以單一 model output 為高風險 Action 唯一依據者，違反本條。

---

## §8 Reasoning 引擎之分界紀律與 resolution 定性 [N]（`§5` 角色四、`§0.6(b)`）

> **L5.8（Reasoning 引擎之分界紀律——不下侵 L4 語義、不上侵 L6 消費）[N｜carries｜`AUGUR-MC v1.4 §5` 角色四、`§0.6(b)`；refines｜`AUGUR-KS v1.1` KS.100、KS.101、Annex L56]**
> 本層定 Reasoning／Inference／Hypothesis／Explanation 之引擎與概念不變式，**且僅此**。**不得重定義 Layer 4** 之 Confidence 語義（L_C 之序與結構）、Evidence 分類法、Trust Rank、完備性等級——此等為 L4 專屬，本層**僅消費**（`AUGUR-KS v1.1` KS.100）。**不得定義 Layer 6** 之風險分級表、Confidence／完備性消費門檻值、確認者資格與獨立性、監督否決度量——此等為 L6 專屬（`AUGUR-KS v1.1` KS.101）。Confidence 之上限代數（`AUGUR-KS v1.1` KS.34 meet）為本層一切聚合實作之**硬約束**，**不得**以聚合語義規避。
> **義務主體**：本規格、Layer 4／6 規格作者。**可判定判準**：本層任一條款對 L4 量尺（L_C 序、Trust Rank、完備性等級）或 L6 門檻值作實質定義者，構成上侵／下侵（違本條；Annex L46 兩欄無交集之對稱要求）。

> **L5.9（identity resolution 演算之定性承接——T-KS-6 之解消）[N｜carries｜`AUGUR-KS v1.1` KS.83(ii)、KDO.1；refines｜`AUGUR-ID v1.0` IDO.4；hooks｜量測落地→L5/L7（KDO.4／LDO.4）]**
> identity resolution 之相似度計算／比對／批次解析演算屬本層 **inference**（推論產生過程，承 `AUGUR-KS v1.1` KS.83(ii)、KDO.1），**非** Knowledge 之信度／欄位語義。其產出**仍為候選斷言**：所繫結之 identity claim 以 Evidence 通道確立，其 Confidence 語義、五元組欄位、as-of 能力由 Layer 4 承接（`AUGUR-KS v1.1` KS.90–KS.92），本層**不於 L_C 逕釘 Confidence 下限**。未解析存量指標之量測落地（未解析存量、解析時效、顯式待決同一性存量）承接 KDO.4（量測實作下放 L7，LDO.4；定性承接仍本層 L5.9／LDI.4）。定性分歧 **T-KS-6**（`AUGUR-ID v1.0` IDO.4 標為目標 L4 vs `AUGUR-KS v1.1` KS.83 讀為 L5 Reasoning 落點）於本條承接並解消：**resolution 之推論產生歸 L5，其結果 claim 之信度／欄位歸 L4**；此定性已裁（Steward 追認，RULING-2026-029 (vii)，2026-07-23）（T-L5-6）。
> **義務主體**：本規格、Layer 3／4／7 規格作者。**可判定判準**：resolution 演算之產出經 Evidence 通道確立為 identity claim、且本層未對 claim 之 Confidence／欄位語義作實質定義者，合規；本層逕釘 claim Confidence 下限者，為下侵定性錯誤。

---

> **L5.10（as-of 推理消費——推理之時間邊界與 anti-leakage）[N｜carries｜`AUGUR-MC v1.4 §P4.E2`；refines｜`AUGUR-KS v1.1` KS.40–KS.46；承接｜`AUGUR-KS v1.1` KDO.6 之 L5 面向]**
> 本規格之 Inference **消費**上游 Layer 4（`AUGUR-KS v1.1 §5` KS.40–KS.46）所定之 as-of 重建能力等級，**不重定義**重建機制。凡以 as-of 時點 T 為基準之推理：
> **(a) 時間邊界**：結論所引之全部 Evidence／Knowledge 節點，其 valid time／發布日（vintage）**必須** ≤ T（`§P4.E2` 雙時間性）；納入 vintage ＞ T 之節點（未來洩漏／lookahead）者，**不得**產出 as-of T 之結論。
> **(b) anti-leakage 消費**：purged／embargo／發布日 gate 之判定由 KS §5 能力等級與其下放之查詢引擎（`KDO.6`→L5／L7 實作）供給；本層**必須**於推理入口以該 gate 過濾輸入，未過濾即納入者違反本條。
> **(c) 能力等級透明**：as-of 重建之能力等級（KS.40–46 之 A0–A3）**必須**隨結論標示；能力等級不足以支持所宣稱 as-of 精度者，結論之 as-of 宣稱降級或標 provisional。
> **義務主體**：本規格、Reasoning 引擎、Layer 5–7 承載構件。**可判定判準**：存在任一 as-of T 推理，其輸入 Evidence 集含 vintage ＞ T 之節點、或未經 KS §5 as-of gate 過濾者，違反本條（機器可判：對每一 as-of 結論之輸入集掃描 vintage vs T）。（RULING-2026-019 決策二重作；Steward 2026-07-19 准入 [N]。）

> **L5.90（合規聲明格式承接）[N｜carries｜`AUGUR-WM v1.0 §WM.39–45`；`AUGUR-MC v1.4 §8.3`]**
> 本規格之 Constitutional Compliance Statement 依 `AUGUR-WM v1.0 §WM.39–45` **正式格式**作成（見 **Annex CS**），非暫行模板。無有效聲明使本規格不生效力。front-matter 閉集欄位、七節論證、緊張關係節、雙向 DEFER 表、WM.44 逐條矩陣（Annex TR）俱全為機器可判生效要件（惟 Steward 充任認定另為裁決要件；v1.0 生效，RULING-2026-029）。

## §9 文件治理與合規存續 [N]

> **義務主體**：本規格自身、Steward。**可判定判準**：Annex CS 之 front-matter 欄位、七節論證、緊張關係節、雙向 DEFER 表俱全（`§WM.40–44`），且 Annex TR 逐條矩陣完備。

> **L5.91（存續與升版）[N｜carries｜`AUGUR-MC v1.4 §8.6`；`AUGUR-WM v1.0 §WM.46–47`]**
> 條款編號永不重用、永不重排；`AUGUR-MC`／`AUGUR-WM`／`AUGUR-ONT`／`AUGUR-ID`／`AUGUR-KS` major 升版時本規格進入重新認證期。全部「不得」（MUST NOT）義務不得豁免（`§8.4`）。
> **義務主體**：本規格、Steward。**可判定判準**：升版時 Annex CS 之 `mc-version`／`upper-specs` 欄同步；版本間 diff 檢查——任一既發布編號於後版消失或改指他文者，違反本條。

> **L5.92（文件約定之規範地位）[N｜carries｜`AUGUR-WM v1.0 §WM.53`]**
> 【地位】節與 §0.1–§0.5 之全部約定（生效要件、規範用語等級、條款編號系統、權威語言、引用格式、元規則、概念層獨立性）為 [N] 規範內容，其效力與正文條款同。本規格每一 [N] 條款標注憲章／上層錨定＋三態（refines／carries／hooks）＋義務主體＋可判定判準。
> **義務主體**：本規格自身、其後續修訂者及一切消費者。**可判定判準**：各約定之文句字面適用；牴觸各該約定者為文件缺陷，依 `AUGUR-MC v1.4 §8.2` 採較嚴格解讀處理至修正為止。

---

## Annex LDI [N] — 承接上層／Layer 4 DEFER 掛鉤（defers-in）

> **LDI.0（承接義務）[N]** 本表每列為規範性承接掛鉤：本層明示承接上層明示下放之事項，並於正文對應落點填充之；本表每列與 Annex CS front-matter `defers-in` 欄及 CS.3(a) 三向可解析。
> **義務主體**：本規格自身。**可判定判準**：上表每列於正文有對應 L5 條款、且於 Annex CS `defers-in` 表雙向可解析者為合規；任一列無對應正文條款者，承接不完整。

| 掛鉤 | 承接來源 | 事項 | 本規格落點 |
|---|---|---|---|
| **LDI.1** | `AUGUR-KS v1.1` KDO.1 | Confidence 傳播聚合之推論引擎實作、resolution 演算之 inference 實作 | L5.3、L5.9 |
| **LDI.2** | `AUGUR-KS v1.1` KDO.3（HOOK-02 之 L5 面向） | 外部知識入 World Representation 之推論工作流實作 | L5.5 |
| **LDI.3** | `AUGUR-KS v1.1` KDO.3（HOOK-03 之演算面）、KS.84 | GATE 統計治理之統計計算實作（設計權屬 L4，本層僅實作演算） | L5.5 |
| **LDI.4** | `AUGUR-KS v1.1` KDO.4、`AUGUR-ID v1.0` IDO.4 | 未解析存量指標之量測落地（L5 面向） | L5.9（＋轉 LDO.4） |
| **LDI.5** | `AUGUR-KS v1.1` KDO.6 | as-of gate／purged／embargo 之查詢引擎操作化（L5 面向） | **L5.10**（＋轉 LDO.5 之 L7 面向） |
| **LDI.6** | `AUGUR-KS v1.1` KS.100、`AUGUR-MC v1.4 §5` 角色四 | Reasoning／Inference／Hypothesis／Explanation 引擎、Confidence 傳播算子推論實作、外部知識確立工作流 | §3–§8（L5.1–L5.10） |
| **LDI.7** | `AUGUR-WM v1.0` HOOK-02、HOOK-03 | 可證偽→OOS＋經濟裁決工作流之推論面、GATE 預註冊實驗之推論面 | L5.5 |

---

## Annex LDO [N] — 下放下層 DEFER 掛鉤（defers-out）

> **LDO.0（下放義務）[N]** 本表每列為規範性下放掛鉤：本層明示不定義該實作事項，授權並要求目標 Layer 定義之；目標 Layer 規格作成時必須於其 Compliance Statement 之 `defers-in` 欄承接對應列。
> **義務主體**：本規格自身（設掛鉤）、目標 Layer 規格作者（承接）。**可判定判準**：本表每列與 Annex CS front-matter `defers-out` 欄雙向可解析；本層無任一條款對本表所列事項作成可被下層直接消費之實質定義（L5.8 下侵判準）。

| 掛鉤 | 本規格落點 | 下放事項 | 目標 Layer | 授權 |
|---|---|---|---|---|
| **LDO.1** | L5.7、L5.8、§0.5 | 具體 AI model／向量庫（vector DB）／統計庫等物理構件之選定 | L7 | `AUGUR-MC v1.4 §7`、`§0.6(b)`、Appendix A（非約束性選型） |
| **LDO.2** | L5.3、L5.6、L5.7、L5.8 | Confidence 消費門檻值、banding 帶界閾值、風險分級表、各風險級之完備性／Confidence 門檻、確認者資格與獨立性、監督否決度量 | L6 | `AUGUR-KS v1.1` KDO.2、KS.101、`AUGUR-MC v1.4 §P5.E2` |
| **LDO.3** | L5.6 | Explanation 之呈現／交付格式與 UI（解釋內容義務屬本層 L5.6，排版／注入 payload／對外呈現下放） | L7（L6 僅監督 UI） | `AUGUR-MC v1.4 §5` 角色五／六、`§0.6(b)` |
| **LDO.4** | L5.9 | 未解析存量指標（未解析存量、解析時效、顯式待決同一性存量）之量測實作 | L7 | `AUGUR-KS v1.1` KDO.4、`AUGUR-ID v1.0` IDO.4 |
| **LDO.5** | L5.10 | as-of gate／purged／embargo 之查詢引擎物理載體、雙時間查詢實作 | L7 | `AUGUR-KS v1.1` KDO.6、`AUGUR-MC v1.4 §P4.E2` |
| **LDO.6** | §2、§8 | Planning／Human Authority Gate／Action 之授權鏈驗證與行動 gating（EV.8–EV.10；本層止於 Reasoning EV.7） | L6 | `AUGUR-MC v1.4 §5` 角色五、`§P5`、`§4` canonical chain |

---

## Annex L46 [N] — 與 Layer 4／Layer 6／Layer 7 之分界表

> **L46.0（分界判準）[N]** 本層定 Reasoning／Inference／Hypothesis／Explanation 之引擎與概念不變式；下表「本層得為（Layer 5 專屬）」欄與「鄰層專屬」欄**無交集**，本層任一 [N] 條款不落入「鄰層專屬」欄為合規（違則構成上侵 L4／下侵 L6/L7，違 L5.8）。
> **義務主體**：本規格、Layer 4／6／7 規格作者。**可判定判準**：兩欄無交集，且本層任一條款不落入「鄰層專屬」欄。

| 面向 | 本層得為（Layer 5 專屬） | 鄰層專屬 |
|---|---|---|
| Confidence | 傳播聚合之推論實作、聚合算子、Grading Method 之運算（守 meet 上限） | L_C 之序／結構／官方映射（L4）；消費門檻值／風險綁定（L6） |
| Evidence | 假設生成、推論產生 Evidence、resolution inference | 分類法／Trust Rank／NoLaundering／獨立性判準（L4）；確認者資格（L6） |
| Hypothesis | 假說生成、可證偽工作流之推論、GATE 統計計算實作 | GATE 概念層約束之設計權（L4，KS.84）；風險級 gating（L6） |
| Explanation | per-結論解釋內容義務（四要素可解析） | 解釋之呈現／交付格式／UI（L7，LDO.3；L6 僅監督 UI） |
| model／庫 | 何為合法推理工具（概念）、model output 之地位 | 具體 model／向量庫／統計庫物理選型（L7，LDO.1） |
| Action | 止於 Reasoning（EV.7） | Planning／Human Authority Gate／授權鏈驗證／行動 gating（L6，LDO.6） |

---

## Annex TR [N] — WM.44 逐條對應矩陣（憲章＋WM＋ONT＋ID＋**KS** → L5）

> **TR.0（矩陣之地位與生效要件性）[N]** 依 `AUGUR-WM v1.0 §WM.44`：`AUGUR-MC v1.4`、`AUGUR-WM v1.0`、`AUGUR-ONT v1.0`、`AUGUR-ID v1.0`、`AUGUR-KS v1.1`——〔**2026-07-19 更正（RULING-2026-019 決策二重作）**：原「五上層全部覆蓋」不實（KS 整份缺席/WM D1-6 漏/as-of 幽靈），已補 TR.F＋D1-6＋改標；as-of 消費落點＝L5.10（Steward 2026-07-19 准入）〕——全部 [N] 條款均須對應至本規格至少一 [N] 條款、明記 DEFER 掛鉤、或明記「不觸及」及理由（P#.Y 為 [I] 不計）。本矩陣：TR.A（`AUGUR-MC v1.4` §P4 家族逐條）、TR.B（`AUGUR-MC v1.4` PA／P1／P2／P3／P5 家族、EV.1–EV.12、F1–F6 及 §0/§1/§2/§5/§7/§8 逐條）、TR.C（`AUGUR-WM v1.0` WM.1–53＋Annex A A.0–A.59＋Annex D D0–D28＋HOOK-01/02/03，以十位制區塊逐條枚舉）、TR.D（`AUGUR-ONT v1.0` ONT.1–62＋Annex T T.0–T.91＋DO.0–4）、TR.E（`AUGUR-ID v1.0` ID.1–81＋IDO.0–8）。以十位制區塊枚舉者，區塊內各條款共享所標處置。**本層為交界層，多數上層本體條款之處置為「承接不觸及＋理由：屬 Layer 0–4 本體，L5 消費不重定義」**。〔**TR 更正記錄（patch，RULING-2026-016／AL-2026-019）**：TR.C(3) 原對 D13–D17／D19–D25／D28 之概括理由（「目標 L2–L4」「非本層落點」）與 `AUGUR-WM v1.0` Annex D 原文目標欄矛盾，屬誤植——D13／D22／D28 已析出改列，D14–D17 括注據實更正；[N] 義務零變更。〕
> **義務主體**：本規格、Steward。**可判定判準**：如 `§WM.44` 對應完備性——五上層每一 [N] 條款於本矩陣有落點列（承接／細化／DEFER／不觸及＋理由）者為完備；標「不觸及＋理由」之列，其理由為機器可判之處置。

### TR.A — `AUGUR-MC v1.4` §P4 家族（逐條）[N]

| MC 條款 | L5 落點 | 模式 |
|---|---|---|
| §P4.D（Evidence 可追溯） | L5.2 | 承接 |
| §P4.W1（Augur 不接受：無 Source 之 Knowledge、不可重現之結果、無 Evidence 之推論） | L5.5（`§A.48` hardcoded＝無 Evidence 斷言） | 承接 |
| §P4.E1（Knowledge 五元組） | L5.1（推理產物確立為五元組 Knowledge）、L5.6（解釋五問） | 承接 |
| §P4.E2（Time（雙時間性）） | **L5.10**；查詢引擎操作化 DEFER（LDO.5） | 承接＋DEFER |
| §P4.E3（Supersede（只失效不刪除）） | 不觸及＋理由：supersede／tombstone 語義屬 L4（`AUGUR-KS v1.1` §6）；本層 L5.5(c) 承接 GATE 二次證偽之 supersede 特例（演算面） | 承接（演算面）＋不觸及（語義） |
| §P4.E4（Defeasible（可謬性）） | L5.4（Hypothesis 可謬、禁隱含 1.0、禁不可修正） | 承接 |
| §P4.E5（Conflict（矛盾保存）） | 不觸及＋理由：矛盾保存語義屬 L4（`AUGUR-KS v1.1` §7）；本層產生之衝突結論以候選斷言入 L4 Conflict Set，不重定義保存語義 | 不觸及＋理由 |
| §P4.E6（Provenance（遞迴溯源）） | L5.2（雙合法終點、DAG、禁循環） | 承接（核心） |
| §P4.E7（NoLaundering（信任不可洗白）） | L5.3（meet 上限）、L5.5（升級守上限）、L5.7（synthetic／TR-C／高風險） | 承接 |
| §P4.E8（Confidence（語義與消費）） | L5.3（傳播聚合實作，承接 KDO.1）；序與語義消費自 L4 | 細化（傳播面）＋承接 |

### TR.B — `AUGUR-MC v1.4` 非 P4 家族（逐條）[N]

| MC 條款 | L5 落點／處置 | 模式 |
|---|---|---|
| PA（Prime Axiom）＋§1.1 釐清句 | L5.1、L5.2、L5.6、CS.1-PA（可追溯 Evidence／不確定性可追溯／錯誤可修正） | 承接 |
| §0（Document Status & Conventions（文件地位與約定）） | §0（本規格文件約定，效力依 L5.92 承載） | 承接 |
| §0.1（名稱、層級與版本） | §0.1 | 承接 |
| §0.2（規範用語約定） | §0.2 | 承接 |
| §0.3（條文效力標注） | §0.3 | 承接 |
| §0.4（權威語言） | §0.4 | 承接 |
| §0.5（適用範圍：Layer 對照表） | §0.5、§0.1 | 承接 |
| §0.6（Hierarchy Rule（層級規則）） | §0.5、L5.7、L5.8、Annex LDO | 承接 |
| §1（Supreme Purpose — Prime Axiom（最高使命）） | §1（Layer 定位） | 承接 |
| §1.1（Prime Axiom（PA）—— 永恆條款（Eternity Clause）） | L5.2、L5.3、L5.4、CS.1-PA | 承接 |
| §1.2（標準鏈引用；Intelligence 於 EV.7–EV.8 落點） | L5.1（Reasoning 為 Intelligence 子集、經通道）、CS.1-EV-chain | 承接 |
| §1.3（五條對稱禁令） | L5.4（Hypothesis referent 為可能狀態、須顯式標記）；型別歸 L2 不重定義 | 承接 |
| §2（Definitions 章） | §0.5 不重定義元規則 | 承接 |
| §2.5（Evidence 定義） | L5.2（引用 Evidence，不重定義） | 承接 |
| §2.6（Knowledge 定義） | L5.1（確立為 Knowledge，不重定義） | 承接 |
| §2.7（Intelligence 定義） | L5.1（Reasoning／Inference 為 Intelligence 子集） | 承接（核心） |
| §2.10（Confidence 定義） | L5.3（傳播；序與語義消費自 L4，不重定義） | 承接 |
| §2.11（Evidence 通道） | L5.1、L5.2（候選斷言經通道確立） | 承接（核心） |
| §3（Five Immutable Principles（五大不可違反原則）） | L5.1、CS.1-EV-chain | 承接 |
| §4（World Evolution Model（世界演化模型）） | 見 EV.* 逐列；本層止於 Reasoning（EV.7） | 承接＋DEFER |
| §5 角色一/二（system of record／表徵） | 不觸及＋理由：屬 L4 Knowledge 側（`AUGUR-KS v1.1`），本層消費不重定義 | 不觸及＋理由 |
| §5 角色四（World Understanding Engine：Reasoning／Inference／Hypothesis／Explanation） | §3–§8（L5.1–L5.10），本規格核心職掌 | 細化（核心） |
| §5 角色三/五/六（Intelligence 泛稱／介面／執法點） | 不觸及＋理由：介面與執法點屬 L6/L7；本層限 Reasoning | 不觸及＋理由 |
| §6 F1（Data First Architecture） | 不觸及＋理由：資料表先於世界模型屬 L1/L4 建置紀律；本層不涉 | 不觸及＋理由 |
| §6 F2（Model First Architecture） | L5.7（禁先選 AI model 再設計系統，核心防線） | 承接（核心） |
| §6 F3（Agent First Architecture） | 不觸及＋理由：Agent 建置順序屬 L6 Agent Runtime | 不觸及＋理由 |
| §6 F4（Knowledge Without Identity） | L5.1、L5.4（未標記假說／逕寫權威層為禁止型態） | 承接 |
| §6 F5（Intelligence Without Evidence） | L5.6（per-結論可解釋，核心落實） | 承接（核心） |
| §6 F6（Unaccountable Action） | 不觸及＋理由：Action 問責六元組與執行屬 L6（LDO.6） | 不觸及＋理由 |
| §7（Long-Term Stability Rule（十年以上演化原則）） | L5.7、L5.8、§0.5（刪名測試、技術中立，核心防線） | 承接（核心） |
| §8.1（Constitution Steward（憲章權威）） | L5.91、§0.3；充任認定屬 Steward，本層不登錄 | 承接 |
| §8.2（違憲後果、審查程序與衝突優先序） | L5.90、L5.92（較嚴格解讀）；裁決屬 Steward | 承接 |
| §8.3（合規聲明義務與可判定性元規則） | L5.4（保守推定 INSUF）、Annex EO（謂詞判準） | 承接 |
| §8.4（不可豁免核心） | L5.91（MUST NOT 不豁免） | 承接 |
| §8.5（Amendment Procedure（修訂程序）） | 不觸及＋理由：修憲程序屬 L0 憲章自身治理，本層僅為受規範對象（L5.90） | 不觸及＋理由 |
| §8.6（版本語義、引用格式與編號穩定性） | L5.91、§0.3 | 承接 |
| P1（Reality First 家族：P1.D／P1.E1／P1.E2／P1.E3／P1.W1） | L5.7（model output 非最高抽象／非世界權威）、L5.1（權威順序）；自然人／法規對應 DEFER L6；CS.1-P1 | 承接＋DEFER |
| P2（Representation Before Intelligence 家族：P2.D／P2.E1／P2.E2／P2.E3／P2.E4／P2.E5／P2.W1／P2.W2） | L5.1（候選斷言經通道）、L5.5（P2.W2 確立工作流承接）、L5.7（P2.E2 model output）；self-reported 標記承 L4（`AUGUR-KS v1.1` KS.21/77）；CS.1-P2 | 承接 |
| P3（Identity Before Knowledge 家族：P3.D／P3.E1／P3.E2／P3.E3／P3.W1／P3.W2） | L5.6（解釋繫已解析 Identity）、L5.9（resolution inference；claim 信度歸 L4）；採認機制屬 L3；CS.1-P3 | 承接 |
| P5（Accountability Before Action 家族：P5.D／P5.E1／P5.E2／P5.W1／P5.W2／P5.W3／P5.W4／P5.W5） | 不觸及＋理由：行動問責／風險分級／監督否決屬 L6（LDO.2、LDO.6）；本層止於 Reasoning，僅 L5.7 承接高風險證據要求結構之推理面；CS.1-P5 | 部分承接＋不觸及＋DEFER |
| EV.1（Reality） | 不觸及＋理由：Reality 本體屬 L0/L1，非推理落點 | 不觸及＋理由 |
| EV.2（Observation） | L5.2（引用鏈合法終點之一） | 承接 |
| EV.3（Representation） | L5.1（候選斷言確立為 Representation） | 承接 |
| EV.4（Identity） | L5.6（解釋繫已解析 Identity）、L5.9 | 承接 |
| EV.5（Evidence） | L5.2（遞迴溯源） | 承接（核心） |
| EV.6（Knowledge） | L5.1（確立為 Knowledge 五元組） | 承接 |
| EV.7（Reasoning） | §3–§8（本層核心落點）；CS.1-EV-chain | 細化（核心） |
| EV.8（Planning） | 不觸及＋理由：Planning 屬 L6（LDO.6）；本層止於 EV.7 | 不觸及＋理由 |
| EV.9（Human Authority Gate） | DEFER L6（LDO.6）；L5.7 高風險須人類確認為其推理面接口 | 承接（接口）＋DEFER |
| EV.10（Action） | DEFER L6（LDO.6） | DEFER |
| EV.11（Feedback） | 不觸及＋理由：Feedback 迴路屬 L6 執行；本層產出仍以候選斷言經通道（L5.1） | 不觸及＋理由 |
| EV.12（Learning） | L5.1（Learning 產出以候選斷言經 Evidence 通道確立，不得直寫世界狀態） | 承接 |

### TR.C — `AUGUR-WM v1.0`（全部 [N]，十位制區塊逐條）[N]

**(1) 正文 WM.1–WM.53**

| WM 區塊／條款 | L5 落點／處置 |
|---|---|
| WM.1（從屬） | L5.90、§0.1—承接 |
| WM.2（細化不重定義） | §0.5 元規則—承接 |
| WM.3（管轄與 DEFER 紀律） | §2、L5.8—承接 |
| WM.4（概念層獨立性＋刪名測試） | §0.5、L5.7、L5.8—承接 |
| WM.5（任務） | §1—承接 |
| WM.6–WM.11（領域 Profile／最高抽象／結構獨立性／形式權威範圍等存在層本體） | 不觸及＋理由：屬存在層本體，本層消費不重定義；WM.7（最高抽象）於 L5.7（model 非世界權威）呼應 |
| WM.12（近似性與來源保留） | L5.3、L5.4（Confidence 沿鏈傳播、Hypothesis 保守 INSUF）—承接 |
| WM.13（三性質可判定判準＋演化四不變式） | 不觸及＋理由：白名單完整性紀律屬 L4（`AUGUR-KS v1.1` KS.78）；本層 L5.5 引 `§A.48` hardcoded 禁止 |
| WM.14–WM.17（唯一權威表徵／登錄結構存在層面向） | 不觸及＋理由：唯一權威表徵落點屬 L4（`AUGUR-KS v1.1` KS.25） |
| WM.18（候選斷言之地位與狀態轉換） | L5.1、L5.4—承接 |
| WM.19（基本單位） | §1—承接 |
| WM.20–WM.23（存在層結構條款） | 不觸及＋理由：存在層本體，本層消費不重定義 |
| WM.24（canonical chain 承接／節選連續性） | L5.1、CS.1-EV-chain—承接 |
| WM.25–WM.29（變更二分／自反性／Action 六元組世界事件與禁止型態之無位置性／人類權威表徵位置／fail-safe 狀態容納） | 不觸及＋理由：屬存在層／L4–L6 fail-safe（`AUGUR-KS v1.1` KS.102）；本層不定判定主體 |
| WM.30–WM.31（雙時間／as-of 存在層宣告） | **L5.10**；能力等級屬 L4、查詢實作 DEFER（LDO.5）—承接＋DEFER |
| WM.32（觀測定案性） | 不觸及＋理由：分類法維護權屬 L4（`AUGUR-KS v1.1` KS.71）；本層消費 |
| WM.33（永久標記表達力） | L5.4（assumption 永久標記）、L5.7（synthetic 永久標記）—承接 |
| WM.34（核心不變式之可機器稽核） | L5.1、L5.2、L5.3（可機器稽核判準）—承接 |
| WM.35–WM.38（落地即整合；消費設閘不阻斷落地／World Concept Registry 與消費規則／唯一權威表徵落實義務／自然人之有界表徵） | 不觸及＋理由：屬存在層／L4 落點 |
| WM.39（適用範圍與效力規則） | L5.90、Annex CS—承接 |
| WM.40（機器可稽核 front-matter） | Annex CS front-matter—承接 |
| WM.41（逐原則論證本文） | CS.1—承接 |
| WM.42（緊張關係與豁免登記） | CS.2—承接 |
| WM.43（雙向 DEFER 承接表） | CS.3、Annex LDI／LDO—承接 |
| WM.44（形式充分性判準） | CS.4、Annex TR（本矩陣）—落實 |
| WM.45（過渡承接） | L5.90、Annex CS—承接 |
| WM.46–WM.47（編號穩定／升版） | L5.91、§0.3—承接 |
| WM.48–WM.52（重新認證與書面形式／地位與衝突規則／必備五部結構／越界禁止／版本節奏隔離） | 不觸及＋理由：屬存在層治理，本層不涉 |
| WM.53（文件約定之規範地位） | L5.92—承接 |

**(2) Annex A（A.0–A.59，領域經驗前身）＋ HOOK**

| WM Annex A 區塊 | L5 落點／處置 |
|---|---|
| A.0–A.9（前身文件框架／領域素材） | 不觸及＋理由：領域經驗素材，非概念不變式落點；經 HOOK-02 工作流方得入徵 |
| A.10（維度族） | 不觸及＋理由：屬 L4（`AUGUR-KS v1.1` KS.78）；本層 L5.5 引 hardcoded 禁止 |
| A.11–A.18（EconomicIndicator） | 不觸及＋理由：外部思想為假說生成視角（L5.5），經 HOOK-02 入徵；非直接落點 |
| A.19（GATE 預註冊實驗） | L5.5、`AUGUR-KS v1.1` KS.84—承接（演算面） |
| A.20–A.47（Augur） | 不觸及＋理由：同 A.11–A.18，經 HOOK-02 可證偽工作流方得入徵 |
| A.48（思想≠特定值／hardcoded 禁止） | L5.5（特定數值不得直入特徵公式）—承接（核心） |
| A.49–A.51（領域素材） | 不觸及＋理由：經 HOOK-02 入徵 |
| A.52（假說與 GATE 之定位） | L5.5（假說須經 GATE 可證偽＋OOS）—承接（核心） |
| A.53–A.59（領域素材） | 不觸及＋理由：經 HOOK-02 入徵 |
| HOOK-01（anti-leakage：vintage／發布日 gate／purged／embargo） | **L5.10**；能力等級屬 L4、實作 DEFER（LDO.5）—承接＋DEFER |
| HOOK-02（外部知識入 World Representation 之推論工作流） | L5.5、LDI.2—承接（核心） |
| HOOK-03（GATE 統計嚴謹化；設計權屬 L4，演算面屬 L5） | L5.5、LDI.3、LDO 無（演算落本層）；概念約束 `AUGUR-KS v1.1` KS.84—承接（演算面） |

**(3) Annex D（D0–D28，WM 下放掛鉤；本層非直接承接對象者列不觸及）**

| WM Annex D 區塊 | L5 落點／處置 |
|---|---|
| D0（下放盤點） | 不觸及＋理由：D 掛鉤主要下放 L2–L4；本層經 L4（`AUGUR-KS v1.1`）間接承接 |
| D1–D6（D1、D2、D3、D4、D5、D6） | 不觸及＋理由：目標 L2–L3（低於本層），型別/判準/claim介面/provisional解析/鑄造/證券碼判準屬 L2–L3，L5 消費已解析 Identity 不重定義〔RULING-2026-019 決策二重作補列〕 |
| D7–D11（五元組／as-of／Confidence／Evidence／完備性→L4） | 不觸及＋理由：目標 L4，已由 `AUGUR-KS v1.1` 承接；本層消費 L4 產物 |
| D12（HOOK-03 GATE 統計→L4 設計權） | L5.5（演算面實作，設計權承 `AUGUR-KS v1.1` KS.84）—承接（演算面） |
| D13（Goal／Constraint／Capability／Plan 之定義；目標 L5–L6，`AUGUR-MC v1.4 §P3.E1`） | 承接（部分）＋轉下放（2026-07-18 補正；原概括「目標 L2–L4」為誤植）：Reasoning 側引用兜底＝L5.1（候選斷言紀律）、L5.6（解釋繫已解析 Identity）；Planning 側四物件之定義權隨 EV.8–EV.10 經 LDO.6 轉 Layer 6（`AUGUR-L6` L6.19 增補款承接） |
| D14–D17（表徵治理下放其餘列） | 據實分列（RULING-2026-030／AL-2026-033）：**D14**（L4–L5）—**承接（部分）**：候選斷言工作流演算面＝L5.5（KDO.3 中繼）；五元組欄位語義＝L4。**D15**（L4–L6）—不觸及＋理由：fail-safe 判定主體與程序屬 L4–L6（`AUGUR-KS v1.1` KS.102 界分→L6.20），本層不觸判定主體。**D16/D17**—不觸及＋理由：目標 L6 專屬（RULING-2026-016 已承） |
| D18（Registry／部署拓撲→L4/L7） | 不觸及＋理由：目標 L4/L7（`AUGUR-KS v1.1` KDO.5） |
| D19（L4–L7 治權文件唯一真相收斂） | **承接（空集揭露）**（RULING-2026-030）：全文檢索「唯一真相來源」零筆，無收斂事項 |
| D20（目標 L2）／D21（目標 L4） | 不觸及＋理由：目標層低於本層 |
| D22（核心宇宙完整性 gate／流動性地板／產業豁免） | 承接（計算面）：成員資格衍生計算為本層 inference（承 `AUGUR-KS v1.1` KS.80 增補款），受 L5.10、L5.3 既有紀律約束 |
| D23（L4–L7 供應商防護額度） | 不觸及＋理由：通道防護屬觀測擷取與部署面（L4 Evidence 完整性已由 `AUGUR-KS v1.1` 承接；L7 物理面已承 front-matter `WM.D23`）；L5 推理層不觸供應商通道 |
| D24（目標 L6） | 不觸及＋理由：L6 專屬（RULING-2026-013 已承） |
| D25（L5–L7 語料隔離部署面） | 不觸及＋理由：語料隔離機器強制落點＝L6 guard／L7.33（`AUGUR-L6 v1.2` L6.9(d) 語料隔離部署下放 L7.33）；本層僅消費模態標記（L5.4／L5.5） |
| D26–D27（重編／point-in-time→L4） | 不觸及＋理由：目標 L4（`AUGUR-KS v1.1` KS.54/45） |
| D28（誠實輸出契約本體） | 承接界分：本層供契約所消費之 GATE 成就狀態與 Hypothesis 模態標記（L5.4、L5.5）；契約本體（產物閉集、硬綁五項、展示分級、fail-closed 閘）落點 L6（`AUGUR-L6` L6.21 增補款）——呈現面依 LDO.3 本層不定 |

### TR.D — `AUGUR-ONT v1.0`（全部 [N]，逐條）[N]

| ONT 區塊 | L5 落點／處置 |
|---|---|
| ONT.1–ONT.13（型別層總則／Type 判準／schema） | 不觸及＋理由：型別層本體，本層消費 Type／schema 不重定義 |
| ONT.20–ONT.22（判準宣告義務／判準效力與 Layer 3 採認之封印／外部識別碼非 identifier） | 不觸及＋理由：屬性 schema 屬 L2；Confidence 不設於 L2，本層消費 L4 語義 |
| ONT.30–ONT.31（instance／type 標記） | L5.6（解釋繫個體，繫結 instance/type 標記，消費 L2）—承接（消費） |
| ONT.40–ONT.41（同一性判準／維度散列） | 不觸及＋理由：採認判準屬 L2/L3；白名單屬 L4 |
| ONT.50（規範性對映義務） | 不觸及＋理由：型別層本體 |
| ONT.60–ONT.62（合規聲明義務／存續） | L5.90、L5.92、Annex CS—承接 |
| Annex T（T.0–T.6／T.20–T.36／T.40–T.44／T.50–T.53／T.60–T.61／T.90–T.91，型別素材與分界） | 不觸及＋理由：型別層素材與 L2 內部分界，本層消費既定 Type 不重定義 |
| DO.0–DO.4（ONT 下放掛鉤） | 不觸及＋理由：目標 L3–L4，已由 `AUGUR-ID v1.0`／`AUGUR-KS v1.1` 承接 |

### TR.E — `AUGUR-ID v1.0`（全部 [N]，逐條）[N]

| ID 區塊 | L5 落點／處置 |
|---|---|
| ID.1–ID.5（三層不僭越／下界封印／承接盤點／不擴張管轄） | 不觸及＋理由：個體層本體，本層消費已解析 Identity 不重定義 |
| ID.10–ID.15（identifier 鑄造／永久參照） | 不觸及＋理由：identifier 機制屬 L3；本層 L5.6 消費已解析 Identity |
| ID.20–ID.25（採認行為／未採認即未解析／採認之可謬性／resolution 演算與時限指標之下放／世界關係之身份解析） | 不觸及＋理由：屬 L3 |
| ID.30–ID.32（identity claim／唯一權威表徵結構前提） | L5.9（resolution inference 產出 claim；信度／欄位歸 L4 `AUGUR-KS v1.1` KS.90/91）—承接（推論面） |
| ID.40–ID.45（lifecycle 事件／lineage／tombstone） | 不觸及＋理由：lifecycle 機制屬 L3；Knowledge 側欄位歸 L4 |
| ID.50–ID.53（已解析／provisional／resolution 狀態／instance-type） | L5.6（解釋繫已解析 Identity）、L5.9（provisional 不逕升；狀態映 L_C 歸 L4 KS.92）—承接（消費） |
| ID.60–ID.61（身份屬性 as-of 繫結義務／繫結存在 vs 重建引擎之分界） | 不觸及＋理由：衝突保存語義屬 L4（`AUGUR-KS v1.1` §7）；本層產出以候選斷言入 |
| ID.70–ID.71（Layer 4 專屬事項清單／分界表） | L5.8（分界紀律，不上侵 L3/L4）—承接 |
| ID.80–ID.81（合規聲明／存續） | L5.90、L5.92、Annex CS—承接 |
| IDO.0（承接義務） | 不觸及＋理由：IDO 掛鉤目標 L4/L5/L7 |
| IDO.1–IDO.2（identity claim Confidence／五元組→L4） | 不觸及＋理由：目標 L4，已由 `AUGUR-KS v1.1` KS.90/91 承接；本層消費 |
| IDO.3（lifecycle 欄位→L4/L7） | 不觸及＋理由：目標 L4/L7 |
| IDO.4（resolution 演算實作＋未解析存量量測） | L5.9（resolution inference 歸 L5）、LDI.4／LDO.4（量測落地）—承接（核心，T-L5-6／T-KS-6） |
| IDO.5（identifier 命名空間之物理序列化與儲存編碼） | 不觸及＋理由：目標 L7（ID Annex DO 原文；非去識別化／tombstone） |
| IDO.6（as-of 重建引擎→L4/L7） | 不觸及＋理由：目標 L4（`AUGUR-KS v1.1` §5）；查詢實作 DEFER（LDO.5） |
| IDO.7–IDO.8（唯一權威 Representation 指定→L4） | 不觸及＋理由：目標 L4（`AUGUR-KS v1.1` KS.25） |
| Annex L4（ID 與 Layer 4 分界表） | 不觸及＋理由：L3–L4 分界，本層承 L4 之產物 |

### TR.F — `AUGUR-KS v1.1`（直接上游 L4，2026-07-19 重作補列 RULING-2026-019 決策二）[N]

> **TR.F（KS 全份補列與『五上層覆蓋』宣稱之更正）[N]** 本規格首次三鏡查獲：直接上游 `AUGUR-KS` **整份未進本矩陣**——TR.0／CS.4「五上層全部 [N] 覆蓋」宣稱**不實**。經窮舉工作流（wf_3ecf8b7c）＋獨立複核（確認 ks_absent）補列 KS 16 區塊如下。**⚠️ 誠實界限**：(1) as-of 消費落點（KS §5）＝L5.10（Steward 2026-07-19 准入）；(2) 完備性機械強制待決策四；(3) 本補列為 L5 重採認之前置，非自我充任。

| 上層 [N] 區塊 | 處置＋理由 |
|---|---|
| KS §0.6 KS.1–KS.5（層級規則／刪名測試／文件約定） | **承接（KS.4 刪名測試——L5.7/L5.8 直接倚賴，L5 §1.2 承接）／不觸及（KS.1-3/5 屬 L4 文件治理、層級規則，非 L5 推理落點）** |
| KS §1 KS.6–KS.11（任務／範圍／承接盤點／KS.11 DEFER 下放） | 承接：KS.11 所設 defers-out（KDO 家族）為 L5 §2/Annex LDI 承接之源；矩陣須列承接（L5 消費 KS 分層定位、承接其下放掛鉤） |
| KS §3 KS.20–KS.26（Knowledge 五元組欄位不變式） | 承接：L5.1 明示『五元組欄位承接 KS.20』、self-reported 標記承 KS.21/77——矩陣本應逐列『承接（消費，不重定義）』，**已補列（019 重作）** |
| KS §4 KS.30–KS.39 ＋ Annex CM（Confidence 單一形式化語義／統一映射表） | 承接：L5.3 之硬約束整條倚賴：KS.30（L_C 取值）、KS.32（Grading Method provenance）、KS.34（meet 上限）；T-L5-2 亦以 KS.34 為硬約束。須列『承接（消費）＋細化（傳播面）』，**已補列（019 重作）** |
| KS §5 KS.40–KS.46（雙時間 as-of 重建能力等級） | 承接（as-of 推理消費，落點 **L5.10**）：as-of 能力等級 A0–A3 由 L5.10 消費（時間邊界/anti-leakage）；查詢實作對稱下放 KDO.6→LDO.5 |
| KS §6 KS.50–KS.55（Supersede／Tombstone 與失效語義） | 不觸及：supersede/tombstone 語義屬 L4；理由：L5.5(c) 僅承接 GATE 二次證偽之 supersede 演算特例，餘語義不重定義（與 TR.A §P4.E3 處置一致） |
| KS §7 矛盾保存（KS.6x 家族） | 不觸及：矛盾保存語義屬 L4；理由：L5 產生之衝突結論以候選斷言入 L4 Conflict Set，不重定義保存語義（與 TR.A §P4.E5、TR.E ID.60-61 處置一致） |
| KS §8 KS.70–KS.79 ＋ Annex EV（Evidence 分類法／遞迴溯源／信任分級／NoLaundering） | 承接：L5 核心倚賴：KS.70（引用鏈 DAG，L5.1/L5.2）、KS.71（Computational Evidence 分類，L5.7）、KS.72（Trust Rank，L5.6）、KS.73（NoLaundering，L5.2）、KS.74（synthetic 永久，L5.4/L5.7）、KS.76（高風險獨立證據，L5.7）。須逐列承接（消費），**已補列（019 重作）** |
| KS §9 KS.80–KS.84 ＋ Annex CL（完備性等級／核心宇宙／GATE 統計治理） | 承接：KS.84（GATE 統計設計權，L5.5 承接演算面、T-L5-5）、KS.80（核心宇宙成員資格，D22 承接計算面）須列『承接（演算面/計算面）』；完備性等級 KS.80 消費面『不觸及＋理由：屬 L4/L6』。混合處置，**已補列（019 重作）** |
| KS §10 KS.90–KS.92（承接 identity claim 之 Confidence） | 承接：L5.9 之 T-KS-6 解消整條倚賴：resolution claim 之信度/欄位/as-of 能力承 KS.90–92；須列承接（消費，信度歸 L4），**已補列（019 重作）** |
| KS §11 KS.100–KS.102 ＋ Annex L56（與 Layer 5／6 分界） | 承接：此為 L5 分界紀律之直接上游：L5.8 明引 KS.100（L4 專屬僅消費）/KS.101（L6 專屬）、LDI.6 承接 KS.100、L5.8 refines KS.102 Annex L56。L5 最核心之分界依據，**已補列（019 重作）** |
| KS §12 KS.110–KS.111（Compliance Statement Format 承接與存續） | 承接：L5.90/L5.92/Annex CS 對應之上游存續義務；須列承接（格式承接＋存續升版），**已補列（019 重作）** |
| KS Annex DI KDI.0–KDI.18（KS 承接上層 defers-in 掛鉤） | 不觸及：KDI 為 KS 對其上層（MC/WM/ONT/ID）之承接掛鉤，非對 L5 之下放；理由：L5 經 L4 間接消費，非直接承接對象。惟仍須於矩陣具名列出『不觸及＋理由』方合 WM.44 |
| KS Annex DO KDO.0–KDO.7（KS 下放下層 defers-out 掛鉤） | 承接：L5 全部 defers-in 之源頭：KDO.1→L5.3/L5.9(LDI.1)、KDO.3→L5.5(LDI.2/3)、KDO.4→L5.9(LDI.4)、KDO.6→L5.10(LDI.5)；KDO.2 轉下放 L6(LDO.2)、KDO.5(Registry/部署)→L4/L7、KDO.0/7 待列。此為 L5 承接骨幹，**已補列（019 重作）** |
| KS Annex L3U（與 Layer 3 之分界表） | 不觸及：L3–L4 分界，非 L5 落點；理由：本層承 L4 之產物，不涉 L3–L4 分界。須具名列出方合完備性 |
| KS Annex TR／CS／EO（KS 自身 WM.44 矩陣／合規聲明／評價性謂詞判準） | 不觸及：屬 KS 自身之合規 apparatus（其對 MC/WM/ONT/ID 之矩陣、CS front-matter、EO 謂詞表），非 L5 之推理落點；理由：各層自備 WM.39–45 機制，L5 不重複承接。須具名列出 |

### TR.Z — 殘餘生效阻卻（已解除）[N]

> **TR.Z（充任認定成就；`§8.2` 條件通過）[N]** 上開逐條／區塊枚舉已就五上層全部 [N] 條款給出落點（承接／細化／DEFER／不觸及＋理由）。**本規格經 Constitution Steward 依 `AUGUR-MC v1.4 §8.1` 作成充任認定，自 2026-07-17 起生效**（Steward 裁決第 2026-006 號、AL-2026-010）；**`§8.2` 深度實質合憲人類審查 2026-07-23 條件通過**（RULING-2026-029，八項必審裁定），**provisional 已解除、本規格為 v1.0**；**ultracode PRV／ASF 複核 2026-07-23 程序性閉合**（RULING-2026-035／AL-2026-039，未翻 major）。形式充分性之最終判斷與實質合憲審查（`§8.2`）均屬 Steward 裁決，本子代理不代行、不自行宣稱生效。以十位制區塊枚舉之上層本體條款，其「不觸及＋理由」為機器可判之處置；如經 Steward 認定某區塊須逐條細列，屬 minor 升版維護（L5.91）。
> **義務主體**：本規格、Steward。**可判定判準**：五上層每一 [N] 條款於本矩陣有落點；Steward 充任認定成就前，本規格不生效力。

---

## Annex CS [N] — Constitutional Compliance Statement（依 `AUGUR-WM v1.0 §WM.39–45` 格式）

本 Annex 為**規範性聲明文件**（[N]）：其存在與內容為本規格之生效要件（L5.90、`AUGUR-MC v1.4 §8.3`、`AUGUR-WM v1.0 §WM.39`）。**地位提示**：本規格為 **v1.0 生效版本**——充任認定已於 2026-07-17 作成（Steward 裁決第 2026-006 號，AL-2026-010）、`§8.2` 深度實質審查 2026-07-23 條件通過（RULING-2026-029／AL-2026-032）（見【地位】、L5.90）；本聲明之**實質**充分性最終判斷仍屬 Steward `§8.2` 違憲審查程序。

```
compliance-statement:
  spec: Augur Cognitive Kernel Specification
  spec-version: v1.0
  layer: 5
  mc-version: AUGUR-MC v1.4
  upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v1.0, AUGUR-ID v1.0, AUGUR-KS v1.1]
  statement-format: AUGUR-WM v1.0 §WM.39–45
  principles: [PA, P1, P2, P3, P4, P5, EV-chain]
  waivers: []
  open-tensions: [T-L5-1, T-L5-2, T-L5-3, T-L5-4, T-L5-5, T-L5-6]
  defers-in: [KS.KDO.1, KS.KDO.3, KS.KDO.4, KS.KDO.6, KS.KS.100, WM.D12, WM.D13, WM.D22, WM.D28, WM.HOOK-02, WM.HOOK-03, MC.role4]
  defers-out: [LDO.1, LDO.2, LDO.3, LDO.4, LDO.5, LDO.6]
  date: 2026-07-17
  author: Layer 5 Cognitive Kernel 規格起草人（AUGUR-L5 起草子代理；產物原為 v0.1-draft 提案，業經 Steward 充任認定〔RULING-2026-006／AL-2026-010，provisional〕，§8.2 實質審查條件通過、provisional 轉 v1.0〔RULING-2026-029／AL-2026-032〕，ultracode PRV／ASF 程序性閉合〔RULING-2026-035／AL-2026-039〕）
  archive-path: specs/COGNITIVE-KERNEL-SPECIFICATION.md
```

### CS.1 逐原則論證本文（七節，順序固定）[N]

> **CS.1-PA（Prime Axiom）**〔承接〕引 `AUGUR-MC v1.4 §1.1`。合法推理僅以攜 Evidence 之候選斷言入系統（L5.1）、引用鏈遞迴終止於 Observation 或明示假設（L5.2）落實「可追溯之 Evidence」；Confidence 沿鏈傳播並攜 Grading Method（L5.3）落實「不確定性可追溯」；Hypothesis 可謬、禁隱含 1.0（L5.4）落實「錯誤可被新 Evidence 修正」。判準揭示：「可追溯」以引用鏈可機器遍歷（L5.2 判準）操作化，「不確定性可追溯」以 Confidence 攜 Grading Method（L5.3 判準）操作化。

> **CS.1-P1（Reality First）**〔承接＋DEFER〕引 `§P1.E1`、`§P1.E2`。AI model output 非世界權威、非最高抽象（L5.7：model output 為 Computational Evidence，Trust Rank 天花板 TR-C，映 L_C 至多 MODERATE）；推理產物須經 Evidence 通道確立（L5.1，權威順序非時間順序）。自然人／法規對應之風險綁定 DEFER Layer 6（LDO.2）。判準揭示：model output 逾 TR-C 天花板或逕成權威 Knowledge 之禁止（L5.7 判準）以引用鏈與標記可機器盤點操作化。

> **CS.1-P2（Representation Before Intelligence）**〔承接〕引 `§P2.E1`、`§P2.E2`、`§P2.W2`。候選斷言經 Evidence 通道確立方成權威 Representation（L5.1）；model output 不得未經通道逕成 Truth（L5.7）；外部知識入 World Representation 之確立工作流（可證偽→OOS＋經濟裁決）承接自 `§P2.W2`（L5.5、HOOK-02）。判準揭示：未經通道逕寫權威層之推理產物為非法（L5.1 判準），可機器稽核引用鏈。

> **CS.1-P3（Identity Before Knowledge）**〔承接〕引 `§P3.E1`。每一結論之解釋必繫結已解析 Identity（L5.6：回答「為什麼是這一個個體」，補正 AUD-18）；identity resolution 演算為本層 inference，其產出仍為候選斷言，未解析者不逕升 Knowledge（L5.9，信度／欄位歸 Layer 4）。判準揭示：結論解釋無法解析至已解析 Identity 個體層者，解釋面不完整（L5.6 判準）。

> **CS.1-P4（Evidence Before Conclusion）〔核心〕**〔細化〕逐條見 Annex TR.A。`§P4.E6` 遞迴溯源、雙合法終點、禁循環（L5.2）；`§P4.E7` NoLaundering 之 meet 上限（L5.3：聚合增強不逾最弱環節）；`§P4.E8` Confidence 傳播聚合之推論實作承接 KDO.1（L5.3）；`§P4.E4` 可謬性、禁隱含 1.0（L5.4）；`§P4.W1` hardcoded 值＝無 Evidence 斷言之禁止（L5.5）。判準揭示：每一評價性謂詞（「合法推理」L5.1、「引用鏈完整」L5.2、「傳播守上限」L5.3、「per-結論可解釋」L5.6）附可判定判準（收錄 Annex EO）。

> **CS.1-P5（Accountability Before Action）**〔部分不適用＋DEFER〕引 `§P5.E2`、`§P5.W2`。本層止於 Reasoning（EV.7）；高風險 Action 之證據要求結構之推理面（須獨立 Data Evidence 或人類確認）承接於 L5.7，惟風險分級表、確認者資格、監督否決度量、行動 gating 屬 Layer 6（LDO.2、LDO.6）；Human Authority Gate 之接口以人類確認留痕為 Observation。判準揭示：本層對風險分級或門檻值作實質定義即下侵（L5.8 判準）。

> **CS.1-EV-chain（§4 canonical chain）**〔承接〕引 `§4` canonical chain 之 EV.5（Evidence）、EV.6（Knowledge）、EV.7（Reasoning）為本規格之標準鏈落點；引 `AUGUR-WM v1.0 §WM.24`（節選連續性）。本層機制化 EV.5→EV.6→EV.7：Evidence 遞迴溯源（L5.2）、確立為五元組 Knowledge（L5.1）、Reasoning 之概念不變式（§3–§8）；節選不跳節點，止於 EV.7，EV.8–EV.12 之行動面下放 Layer 6（LDO.6）。判準揭示：引用鏈完整性可機器稽核（L5.2／`AUGUR-WM v1.0 §WM.34(a)`）。

### CS.2 已知緊張關係（`AUGUR-WM v1.0 §WM.42`）[N]

| T-id | 所涉條款 | 描述 | 緩解／狀態 |
|---|---|---|---|
| **T-L5-1** | L5.7、L5.8、LDO.1 | 交界層之上侵／下侵風險：本層須定「何為合法推論」之概念不變式，同時 `§0.6(b)` 禁概念層引用執行層構件、`§7` 禁綁定特定模型。 | 條款通過刪名測試（刪去任一具名 model／向量庫／統計庫後規範內涵不變）；具體物理選型下放 L7（LDO.1）。非豁免事項。已核定（029）。 |
| **T-L5-2** | L5.3、LDI.1、KS.34 | 聚合增強 vs meet 上限：KDO.1 授權本層定傳播聚合語義（含多獨立證據增強），但 `AUGUR-KS v1.1` KS.34 之 meet 上限為硬約束。 | 聚合算子之增強合法空間僅及於不逾 meet；嚴格大於 meet 者違 L5.3。非豁免事項。已核定（029）。 |
| **T-L5-3** | L5.5、`§A.48`、`§P4.W1` | 假說生成之自由 vs 無 Evidence 斷言之禁止：得以外部思想為假說生成視角，但思想中特定數值不得直入特徵公式。 | 生成之自由與入徵之紀律以 GATE 可證偽工作流（HOOK-02）為界（L5.5）。非豁免事項。已核定（029）。 |
| **T-L5-4** | L5.6、LDO.3 | 解釋內容義務 vs 解釋呈現面：L5.6 定 per-結論解釋之內容不變式，而呈現／交付／UI 屬 L7（L6 僅監督 UI；RULING-2026-038）。 | 本層不定呈現格式（否則下侵）；L7（及 L6 監督 UI）不得以呈現層規避內容義務（否則 F5 落空）。此為 AUD-18 補正之分工界面。非豁免事項。已核定（029）；目標欄簿記閉於 038。 |
| **T-L5-5** | L5.5、KS.84、HOOK-03 | GATE 統計之設計權（L4）vs 演算實作（L5）：概念層約束屬 L4（`AUGUR-KS v1.1` KS.84），統計計算實作屬 L5。 | 本層僅實作演算、不改其約束語義（Grading Method 一維、判準凍結、supersede 特例）。非豁免事項。已核定（029）。 |
| **T-L5-6** | L5.9、`AUGUR-ID v1.0` IDO.4、`AUGUR-KS v1.1` KS.83 | resolution 演算定性分歧 T-KS-6：IDO.4 標為目標 L4，KS.83(ii) 讀為 L5 Reasoning 落點。 | L5.9 承接並解消為「推論產生歸 L5、結果 claim 之信度／欄位歸 L4」；此定性已裁（Steward 追認，RULING-2026-029 (vii)，2026-07-23）。非豁免事項。 |

豁免登記：`none`（waivers: []）。本規格無現行豁免。

### CS.3 雙向 DEFER 承接表（`AUGUR-WM v1.0 §WM.43`）[N]

* **(a) 承接上層／Layer 4 之掛鉤（defers-in）**：`AUGUR-KS v1.1` KDO.1→L5.3/L5.9（LDI.1）；KDO.3〔HOOK-02〕→L5.5（LDI.2）；KDO.3〔HOOK-03 演算面〕＋KS.84→L5.5（LDI.3）；KDO.4→L5.9（LDI.4，＋轉 LDO.4）；KDO.6→L5.10（LDI.5，＋轉 LDO.5）；KS.100→§3–§8（LDI.6，L5.1–L5.10）；`AUGUR-WM v1.0` §D12→L5.5（演算面）、§D13→L5.1/L5.6（部分）、§D22→L5.10/L5.3（計算面）、§D28→L5.4/L5.5（消費面）；HOOK-02／HOOK-03→L5.5（LDI.7）；`AUGUR-MC v1.4 §5` 角色四→§3–§8（L5.1–L5.10）。與 front-matter `defers-in` 欄及 Annex LDI 三向對表。
* **(b) 下放下層之掛鉤（defers-out）**：LDO.1（物理 model／向量庫／統計庫→L7）、LDO.2（Confidence 門檻／風險分級／確認者資格／監督否決→L6）、LDO.3（Explanation 呈現／UI→L7；L6 僅監督 UI）、LDO.4（未解析存量量測→L7）、LDO.5（as-of 查詢引擎實作→L7）、LDO.6（Planning／Human Authority Gate／Action gating→L6），與 front-matter `defers-out` 欄互為索引（見 Annex LDO）。

### CS.4 形式充分性（`AUGUR-WM v1.0 §WM.44`）[N]

依 `§WM.44` 判準自查：`AUGUR-MC v1.4` **全部** [N] 條款、`AUGUR-WM v1.0`／`AUGUR-ONT v1.0`／`AUGUR-ID v1.0`／`AUGUR-KS v1.1` **全部** [N] 條款，均須對應至本規格至少一 [N] 條款、或明記 DEFER 掛鉤、或明記「不觸及」及理由。

* **P4 家族**：Annex TR.A 已就 `§P4.D`／`§P4.W1`／`§P4.E1`–`§P4.E8` 逐條枚舉（本層承接 EV.7 Reasoning 之核心）。
* **其餘 MC 條款**：Annex TR.B 逐條枚舉（PA／P1／P2／P3／P5 家族、EV.1–EV.12、F1–F6、§0/§1/§2/§5/§7/§8）。
* **WM／ONT／ID 條款**：Annex TR.C／TR.D／TR.E 以十位制區塊逐條枚舉落點（承接／細化／DEFER／不觸及＋理由）；多數上層本體條款之處置為「承接不觸及＋理由：屬 Layer 0–4 本體，L5 消費不重定義」。

**MC [N] 條款覆蓋清單（`§WM.44` 骨架自查，逐一具名以資機器盤點；落點見 Annex TR.A／TR.B）[N]**：`PA`；`EV.1`、`EV.2`、`EV.3`、`EV.4`、`EV.5`、`EV.6`、`EV.7`、`EV.8`、`EV.9`、`EV.10`、`EV.11`、`EV.12`；`F1`、`F2`、`F3`、`F4`、`F5`、`F6`；`P1.D`、`P1.E1`、`P1.E2`、`P1.E3`、`P1.W1`；`P2.D`、`P2.E1`、`P2.E2`、`P2.E3`、`P2.E4`、`P2.E5`、`P2.W1`、`P2.W2`；`P3.D`、`P3.E1`、`P3.E2`、`P3.E3`、`P3.W1`、`P3.W2`；`P4.D`、`P4.E1`、`P4.E2`、`P4.E3`、`P4.E4`、`P4.E5`、`P4.E6`、`P4.E7`、`P4.E8`、`P4.W1`；`P5.D`、`P5.E1`、`P5.E2`、`P5.W1`、`P5.W2`、`P5.W3`、`P5.W4`、`P5.W5`；`§0`、`§0.1`、`§0.2`、`§0.3`、`§0.4`、`§0.5`、`§0.6`、`§1`、`§1.1`、`§1.2`、`§1.3`、`§2`、`§2.1`、`§2.2`、`§2.3`、`§2.4`、`§2.5`、`§2.6`、`§2.7`、`§2.8`、`§2.9`、`§2.10`、`§2.11`、`§3`、`§4`、`§5`、`§5.1`、`§5.2`、`§5.3`、`§5.4`、`§5.5`、`§5.6`、`§6`、`§7`、`§8`、`§8.1`、`§8.2`、`§8.3`、`§8.4`、`§8.5`、`§8.6`。各 `Pn.Y`（`P1.Y`、`P2.Y`、`P3.Y`、`P4.Y`、`P5.Y`）為 [I] 說理條款，本層以「不觸及＋理由：屬各原則之風險說理，非規範義務落點」統一處置（落點／不觸及理由見 Annex TR.A／TR.B），為骨架覆蓋完備計於此具名。**誠實界限**：本清單＝機器盤點之字面具名；語意承接仍以 Annex TR 為權威，不因本清單宣稱新建語意矩陣或完成「決策四第二輪」嚴格強制。

**逐條對應矩陣已作成——形式充分性之形式面已備；Steward 充任認定業經作成（RULING-2026-006／AL-2026-010），`§8.2` 深度實質審查 2026-07-23 條件通過（RULING-2026-029／AL-2026-032），本規格為 v1.0 生效版本**（見【地位】、TR.Z），**殘餘生效阻卻已解消**。上層升版或條款增修時本矩陣對應列**必須**同步維護（L5.91 diff 檢查），否則聲明重回不完整。本子代理不自行宣稱任何規格已生效、不自行登錄正式 Amendment Log；本規格之生效及其登錄（AL-2026-010）均為 Steward 之裁決行為。

---

## Annex EO [N] — 自創評價性謂詞判準彙整

> **EO.1（判準彙整表）[N]** 本規格自創或操作化之評價性謂詞，依 `AUGUR-MC v1.4 §8.3` 可判定性元規則，逐一附可判定判準：
>
> | 謂詞 | 出處 | 可判定判準 |
> |---|---|---|
> | 「合法推理」（legal inference） | L5.1 | 推理產物僅以攜 Evidence＋Confidence 之候選斷言進入系統，且非經 Evidence 通道（`§2.11`，EV.2–EV.5）確立不得成為權威 Representation／Knowledge；存在逕寫權威層之推理產物者為非法（機器稽核引用鏈） |
> | 「引用鏈完整」（citation-chain-complete） | L5.2 | 結論之 Evidence 鏈存在有限步可遍歷路徑，遞迴終止於 Observation 或明示宣告之假設二合法終點之一、且無循環（DAG）；終止於其他節點或含環者不完整 |
> | 「Hypothesis 已標記」（hypothesis-marked） | L5.4 | 候選斷言攜顯式模態／assumption 標記且標記於轉引中不消失；未標記而被消費為現實狀態斷言或 Knowledge 依據者違反 |
> | 「無證升級」（unevidenced-upgrade，禁止型態） | L5.4／L5.5 | 標記之 Hypothesis 未經 Evidence 通道確立（含 GATE 可證偽→OOS＋經濟裁決之成就）而其 Confidence 升逾底錨 INSUF；凡此升級為禁止型態 |
> | 「per-結論可解釋」（per-conclusion-explainable） | L5.6 | 每一結論之解釋可解析至四要素（所繫已解析 Identity／Evidence 集合及 Trust Rank／推理規則／Confidence 及 Grading Method），且個體層可回答「為什麼是這一個個體」；僅止於 model／方法層者為解釋面不完整 |
> | 「Model 輸出非權威」（model-output-non-authoritative） | L5.7 | model output 未經 Evidence 通道不成權威 Knowledge、永久攜 synthetic 標記、映入 L_C 不逾 TR-C 天花板（至多 MODERATE）、不單獨為高風險 Action 依據；任一違反即 model output 被當作世界權威 |
> | 「傳播守上限」（propagation-bounded） | L5.3 | 任一聚合 Confidence ⊑ 前提集合與推理規則 Confidence 之下確界（meet，`AUGUR-KS v1.1` KS.34）、且攜 Grading Method；聚合結果嚴格大於 meet 上限或裸值者違反 |
> | 「resolution 為推論」（resolution-as-inference） | L5.9 | identity resolution 演算之產出經 Evidence 通道確立為 identity claim，且本層未對 claim 之 Confidence／欄位語義作實質定義（該語義歸 L4）；本層逕釘 claim Confidence 下限者為下侵定性錯誤 |
> | 「as-of 推理合規」（as-of-inference-compliant） | L5.10 | 以 as-of T 推理時，結論所引全部 Evidence／Knowledge 節點 vintage≤T；含 vintage＞T 節點（lookahead）者不得產出 as-of T 結論 |
> | 「anti-leakage 入口過濾」（anti-leakage-entry-filtered） | L5.10 | 推理入口以 KS §5 as-of gate（purged／embargo／發布日 gate）過濾輸入；未過濾即納入者違反 |
> | 「as-of 能力等級透明」（as-of-capability-transparent） | L5.10 | as-of 重建能力等級（KS.40–46 之 A0–A3）隨結論標示；能力不足以支持所宣稱精度者，as-of 宣稱降級或標 provisional |
> | 「高風險」（Action，消費側） | L5.7 | **DEFER Layer 6 風險分級表（LDO.2）；本層不判定**——本層僅定「高風險 Action 之證據要求結構之推理面」，風險分級本身為 Layer 6 職掌 |
>
> **掃描—完備性義務（[N]，比照 `AUGUR-WM v1.0` Annex E1／`AUGUR-KS v1.1` EO.1）**：本規格正文如增列自創或操作化之評價性謂詞，**必須**同步收錄本 EO.1 表；未收錄且未附判準者採保守解釋（存疑即不允許，`§8.3`）。
> **義務主體**：本規格、一切消費本規格謂詞之下層規格。**可判定判準**：全文評價性謂詞逐一於本表有列（或其判準明記 DEFER 落點）者為完備；本表每一謂詞之判準可機器適用；未收錄且未附判準之謂詞，採保守解釋。

---

*本規格計：正文條款 L5.1–L5.9（核心推理引擎）＋L5.10（as-of 推理消費，已啟用）＋L5.90–L5.92（文件治理；L5.11–L5.89 為十位制保留區塊）、Annex LDI（LDI.0–LDI.7）、Annex LDO（LDO.0–LDO.6）、Annex L46（L46.0）、Annex TR（TR.0、TR.A–TR.E、TR.Z）、Annex CS 合規聲明（CS.1–CS.4）、Annex EO（EO.1）。全文以繁體中文為權威文本（§0.4）。本文件為 **v1.0 生效版本**（§8.2 條件通過，RULING-2026-029）：Constitution Steward（人類 tsaitsangchi）已依 `AUGUR-MC v1.4 §8.1` 作成充任認定，自 2026-07-17 起生效（Steward 裁決第 2026-006 號、AL-2026-010；【地位】、L5.90）；**`§8.2` 深度實質審查 2026-07-23 條件通過（RULING-2026-029／AL-2026-032，八項必審裁定），provisional 已解除**；**ultracode PRV／ASF 2026-07-23 程序性閉合（RULING-2026-035／AL-2026-039，未翻 major）**。本規格之生效及其登錄均為 Steward 之裁決行為，非本子代理所得宣稱或代行。*

**核心產物索引 [I]**：合法推理＝§3（L5.1 候選斷言經 Evidence 通道／L5.2 雙合法終點引用鏈 DAG）；Confidence 傳播＝§4（L5.3 承接 KDO.1，硬守 KS.34 meet 上限）；Hypothesis 地位與升級紀律＝§5（L5.4 未證可謬須標記／L5.5 承接 KDO.3，GATE 可證偽＋OOS）；Explanation 義務＝§6（L5.6 per-結論四要素、補正 AUD-18）；AI Model 為工具非世界權威＝§7（L5.7 F2 防線、synthetic／TR-C 天花板）；分界紀律與 resolution 定性＝§8（L5.8 不上侵 L4／不下侵 L6、L5.9 T-KS-6 解消）；DEFER 表＝Annex LDI／LDO；WM.44 矩陣＝Annex TR。

# Augur 憲章展開總綱（Constitutional Roll-out Master Plan）

> 版本：v1.0 正式版（2026-07-17 定稿）｜定稿人：Steward（tsaitsangchi）
> 受約束憲章：AUGUR-MC v1.3〔**定稿時（2026-07-17）之有效版；現行 AUGUR-MC v1.6**——沿革：v1.3→v1.4 minor（AL-2026-020／RULING-2026-017）、**v1.4→v1.5 原則級**（AL-2026-035／PROPOSAL-2026-001，§8.1 增設「解釋之界線」段；該 AL 載「L1–L7 規格零衝擊」）、v1.5→v1.6 minor／patch（AL-2026-044／RULING-2026-040）；102 條母集歷次不變、本檔所引條號不變（2026-07-30 機械軌：`constitution/META-CONSTITUTION.md` 標題＋`AMENDMENT-LOG.md` AL-020／035／044 親讀）〕（2026-07-16 生效，權威語言繁體中文 §0.4）
> 治權定調：治權主導的混合式展開

---

## 0. 文件定位

**0.1 本文件是什麼。** 本總綱是 **Layer 0 治權（憲章＋治理附則）之「展開計畫」**，非規範性條文本身。它把已生效的生效機制——由 **AUGUR-MC（Layer 0）§8.3 機器稽核／§8.6 版本語義**與 **AUGUR-WM v1.0（Layer 1）WM.39–45 合規聲明／WM.44 形式充分性**共同定義，並輔以源自 §8＋RULING-2026-002 之充任認定制度——編排為一條可執行的落地路徑，涵蓋 Layer 2–7 規格充任與既有活台股系統之遷移。（本文自身受 §0.6 lex superior 拘束，故於此示範精確之層級歸屬引用。）

**0.2 效力層級。** 本總綱不創設新義務、不變更任何 [N] 條款，僅編排既有義務之履行順序。**本總綱並非任一編號 Layer 之規格**，其從屬性不經 §0.6 lex superior（該條嚴格規範的是編號 Layer 間之效力，小號約束大號），而經其自我聲明的非規範性定位（本 §0.2）與 Steward 之編排權（§8.1）而生。凡本文與憲章／治理附則／已生效規格牴觸者，一律以後者為準。本文所列任何「充任」「apply」「patch」皆須各自走其法定 gate 方生效力；本文的排序不等於授權。

**0.3 與 REMEDIATION-ROADMAP 之關係。** `audits/REMEDIATION-ROADMAP.md` 是程式碼違憲審計（26 發現、critical 3／major 11／minor 12）的**補正支線 roadmap**；本總綱為**上位**框架，補正 roadmap 收攏於本總綱「軌道 B（既有系統遷移）」之下。兩者的對應見附錄 A。凡二者排序衝突，以本總綱之依賴骨架為準；凡二者對個別 AUD 項之技術內容，以補正 roadmap 為準。個別 §8.2 違憲認定與補正到期日仍屬 Steward 個案裁定權限。

**0.4 三份權威來源。** 本總綱不虛構任何現況；一切事實錨定於：(a) `constitution/`（憲章、治理附則、Amendment Log、**裁決 40 份**〔產生指令：`ls constitution/*RULING*.md | wc -l` → 40。**該 glob 已含 `INTERPRETATION-RULING-2026-001`**，故 40 ＝ 編號裁決 39 份（`RULING-2026-002`…`-041`，缺 `-008`，`ls constitution/RULING-2026-*.md | wc -l` → 39）＋解釋裁決 1 份；**勿於 40 之上再加 1**〕；`constitution/adoption-drafts/RULING-2026-008-L7-ADOPTION-DRAFT.md` 自附時效警語、**不生效力**，L7 之充任已改由 `RULING-2026-011` 作成）；(b) `specs/`（**七層規格 L1–L7 全數生效**：AUGUR-WM v1.0、ONT v1.0、ID v1.0、**KS v1.1**〔`RULING-2026-016`／AL-2026-019 minor〕、L5 v1.0、**L6 v1.2**〔`RULING-2026-016`〕、L7 v1.0；**L5 之 provisional 已由 `RULING-2026-029` 解除**〔`§8.2` 條件通過，2026-07-23〕、**L7 由 `RULING-2026-011` 充任並經 `RULING-2026-025` `§8.2` 條件通過**〔2026-07-19〕——二者均附條件、復審 2026-10-14，「條件通過」非「未生效」）；(c) `audits/`（審計報告、補正 roadmap、驗證紀錄）＋ **機器盤點快照 [I]（現行 SSOT＝`ops/machines/`）**。

> **本節之更正記錄（2026-07-17）**：前版載「兩份裁決」及「ONT/ID/KS v0.1-draft」，二者於本節自我聲明「不虛構任何現況」之標準下**均已不實** —— 裁決實為八份（`ls constitution/*RULING*.md | wc -l` → 8），且 ONT／ID／KS 已於 2026-07-17 分別依裁決 2026-003／004／005 充任生效。**一份自稱不虛構現況之條款，其兩個錨點全錯**；據前版援引者將對 ONT／ID／KS 之 [N] 條款現行效力得出完全相反之結論。**數字均以指令導出，勿手數。**
>
> **本節之更正記錄（2026-07-30 機械軌：同一失效模式二度發生）**：2026-07-17 版之三個錨點於本日親跑實測**再度全錯** —— (a) 裁決由 8 份增至 **40 份**（`ls constitution/*RULING*.md | wc -l` → 40）；(b) L5 之 provisional 已於 2026-07-23 由 `RULING-2026-029` 解除，前版「L5 為 provisional〔§8.2 延後〕」不實；(c) L7 已非 `v0.1-draft`——`specs/INFRASTRUCTURE-SPECIFICATION.md` 為 v1.0 生效本（`RULING-2026-011` 充任、`RULING-2026-025` §8.2 條件通過），前版「AUGUR-L7 為 v0.1-draft、未生效」不實。據前版援引者將對 **L5／L7 之現行效力**得出相反結論（誤認 L5 尚待實質審查、L7 尚無 [N] 效力）。**本節之失效模式已二度應驗：錨點須以指令導出並定期重跑，不得沉澱。**〔依據：`ls constitution/*RULING*.md`、`head specs/*-SPECIFICATION.md`【地位】節、`constitution/RULING-2026-029`／`-025` 原文，2026-07-30 親跑〕

---

## 一、展開原則

**1.1 治權主導的混合式（Steward 定調）。** 展開由三條並行軌道構成，共用單一依賴骨架、單一生效要件、單一人類拍板節拍器：

- **軌道 A — 治權骨幹，由上而下：** 憲章為骨幹，逐層補完 L2–L7 規格並經**充任認定**逐層合憲生效。這是關鍵路徑。
- **軌道 B — 既有系統，漸進遷移：** 既有活台股系統在規格指導下遷移，**不推倒重來**，但**不讓 F1 遺產定義未來**；走分支、真 DB 實測、人類 apply。
- **軌道 C — 新能力，一律 greenfield 合憲落地：** 任何新增能力 spec-first，先在 §0.5 登錄所屬 Layer、走充任認定，再落地；永不走 raw 直綁老路。

**1.2 §0.6 由上而下（lex superior）。** 每層「規格生效（充任認定 gate）」必須在下一層承接效力生效之前完成；下層承接上層草案之條款，於上層生效時方**同步生效**（傳遞性阻卻：L2 未生效即連動阻卻 L3/L4 對其承接條款之效力）。§0.6(b) 概念層獨立性使 L2–4 得在 L5–7 不存在時定稿——此即「先鎖概念層、再展開執行層」的憲法依據。（此處係對**編號 Layer 間效力**援引 §0.6，屬其嚴格適用範圍，與 §0.2 對本總綱從屬性之定位不同。）

**1.3 strangler-fig（既有系統的答案，WM.10 已寫定）。** raw 鏡像層（byte-level attestation、逐值忠實鏡像）是 WM.10 明定之**合法且必要的 Observation Store**，共同表徵層「必須建立於其上、不得取而代之」。F1 的病灶不在 raw 存在，而在「vendor 表即世界模型、下游 SQL 字面直綁表名（實測 37 檔）」。對策：在 raw 觀測層與下游智慧層之間 greenfield 插入三道新接縫（World Model 投影／Identity registry／Confidence 語義層），用投影 façade 逐檔絞殺 vendor 直綁；**絕不因新表徵層之建立而拆除或削弱 raw 忠實性**。

**1.4 新能力 greenfield 合憲落地。** 新增能力於 merge 當下即須通過機器稽核 linter（合憲＝綠燈）；遺產則以「失敗檢查＋Steward 個案補正期」追蹤而非推倒重來。同一標準、兩條軌道、規格為唯一權威。

**1.5 三道恆閘（貫穿全程）。**
- (i) **生效兩要件雙成就**（充任認定＋合規聲明）；
- (ii) **不可豁免核心**（PA、P4.E1/E6、P5.W2/W5 及一切禁止性規定，連履行時程亦不得豁免）；
- (iii) **補正期上限**（每項違憲由 Steward 個案裁定到期日，至遲下一 major 版、不逾 24 個月）。

> **制度區辨（防反向解讀）：** 對既有 F1 違規採「失敗檢查＋個案補正期」，其法源為 **§8.2「既有實作經認定違憲」所賦有到期日之補正期**，與 **§8.4 所禁之前瞻式豁免（forward exemption）係不同制度**。§8.2 補正期 ≠ §8.4 豁免；本總綱對禁止性 MUST NOT 從不給豁免，僅對既有實作給有期限之收斂窗。

---

## 二、現況基線

**2.1 Layer 0–7 狀態表（2026-07-17 快照｜基線重切）**

> **本表已於 2026-07-17 重切基線。** 前版為 2026-07-16 快照，其**六列規格狀態全部過時**（L2/L3/L4 記「草案未生效」、L5/L6 記「尚未撰寫／不存在」、L7 記「尚未撰寫」）。因本表為本總綱九階段排程與三里程碑（§4 里程碑節）所依之**現況基線**，前版形同以「落後五層之基線」推導排程 —— 依前版排程者將重複已完成之工作。**依快照體例，此處重新戳記日期，不默默改寫。**

| Layer | 規格檔 | 規格狀態 | 實作狀態 | 關鍵缺口／待辦 |
|---|---|---|---|---|
| L0 治權 | META-CONSTITUTION **v1.6**、GOVERNANCE-ANNEX **v1.1**〔2026-07-30 機械軌：原載 v1.3／v1.0，依二檔標題親讀更新；沿革見本檔檔頭〕 | **已生效** | 治權運作中 | Steward 繼任人未預先指定；審議體未成立；無豁免登錄。**單一自然人 Steward 使「雙人類獨立核准」物理上不可能**（見 HANDOFF） |
| L1 World Model | specs/WORLD-MODEL-SPECIFICATION.md（AUGUR-WM v1.0） | **已生效**（RULING-2026-002／AL-2026-005） | D0–D28 DEFER 掛鉤生效；Annex F Registry 首批附卷 | 引 MC v1.2；v1.2→v1.3 為 minor（§8.6），屬**編輯性對齊**（patch 級 re-cite，非重新認證），聲明續效〔2026-07-30 機械軌：該「引 MC v1.2」為 2026-07-17 當時值，已不對應現況——`RULING-2026-018`／AL-2026-021 已將全艦引用版號齊一至 v1.4，其後憲章續升至 v1.6。**本日親查 `specs/WORLD-MODEL-SPECIFICATION.md`：`AUGUR-MC v1.2` 零命中；`AUGUR-MC v1.4` 僅 4 處且每處均已附註〔當時有效版；現行 v1.6〕；Annex C front-matter 載 `mc-version: AUGUR-MC v1.6`**（`grep -o` 計數＋逐行親讀）。規格本文之版號體例屬該規格事項，本 [I] 檔僅記事實、不代改〕 |
| L2 Ontology | specs/ONTOLOGY-SPECIFICATION.md（AUGUR-ONT v1.0） | ✅ **v1.0 生效**（2026-07-17；RULING-2026-003／AL-2026-007） | — | ✅ **矩陣完備性已補正並經 G5 複驗**（2026-07-30 機械軌）：Annex TR 標題 h1→h2 正規化而入檢（`RULING-2026-010` 主文一／AL-2026-013）＋窮舉補列 4 群（`RULING-2026-021`／AL-2026-023：TR.2 補 A.0、WM Annex C／E、WM Annex D 非 L2 各列）＋G5 獨立複驗判乾淨（`a0516e88`〔**⚠ 2026-07-30 核驗 F4：本識別碼無法解析為 git commit**（`git rev-parse --verify <x>^{commit}` → fatal，4/4 皆然；`constitution/`／`audits/` 零命中，僅存於 `LAYER-SEALING-SCHEDULE.md`）——**類別未明**（疑為 run id／worktree id 而非 commit），**不得引為蓋章之證據錨**；真身待查明後補正〕）→ **已蓋章**（`LAYER-SEALING-SCHEDULE.md` L2 列）。現行 gate 實測：Annex TR 資料列 <!--lint:tr_rows_L2-->66<!--/lint--> 列**已讀取**、比對 <!--lint:compared_L2-->4<!--/lint--> 筆、error 0、WM.44 覆蓋缺口 0/102、判定 ✅ PASS（`python3 -m tools.constitution_lint report`；**列數 ≠ 比對筆數，二數不得相減充作「未受檢列數」**）。前版「linter PASS 為偽陰性／矩陣從未受檢」**已不實**。**殘餘（親驗 2026-07-30 仍然）**：ONT 之 Annex TR 標 **[I]** 而 ID／KS 標 **[N]**——屬 Steward 事項（`§8.5`／`§8.6`），本 [I] 檔不作認定 |
| L3 Identity | specs/IDENTITY-SPECIFICATION.md（AUGUR-ID v1.0） | ✅ **v1.0 生效**（2026-07-17；RULING-2026-004／AL-2026-008） | — | WM.44 逐條矩陣**已枚舉、缺 0 條**（阻卻已解）；**WM.44-LABEL 誤標已結**——`RULING-2026-010`／AL-2026-013 逐字更正，現行 gate 實測 L3 error 0（比對 193 筆）〔2026-07-30 機械軌：`python3 -m tools.constitution_lint report` 親跑〕 |
| L4 Knowledge | specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md（AUGUR-KS **v1.1**） | ✅ **v1.1 生效**（v1.0 首次充任 2026-07-17 RULING-2026-005／AL-2026-009；**minor 升 v1.1** `RULING-2026-016`／AL-2026-019）〔2026-07-30 機械軌：依規格版本欄親讀〕 | — | 同上；矩陣已枚舉、缺 0 條；現行 gate 實測 error 0（比對 214 筆） |
| L5 Cognitive Kernel | specs/COGNITIVE-KERNEL-SPECIFICATION.md（AUGUR-L5 v1.0） | ✅ **v1.0 生效** — `§8.2` **條件通過、provisional 已解除**（`RULING-2026-029`／AL-2026-032，2026-07-23；充任 `RULING-2026-006`／AL-2026-010、`RULING-2026-023`〔乙〕重採認） | ❌ 引擎未建 | **§8.2 實質人類審查已作成**（029 八項必審逐項裁定：(i)(ii)(iii)(iv)(vi) 核定照收、(vii) 核定＋T-L5-6 定性追認、(v)(viii) 條件通過）。**附條件**：L5 單層 ultracode PRV／ASF 複核（035 程序性閉合）、F-IX-4／F-IX-6 簿記（038／AL-2026-042 已閉）、**復審 2026-10-14**（與 L7 residual 同日併結；`RULING-2026-039` 明示**禁止假關**）〔2026-07-30 機械軌：依 `RULING-2026-029` §三＋規格【地位】節親讀〕 |
| L6 Agent Runtime／Governance | specs/AGENT-RUNTIME-SPECIFICATION.md（AUGUR-L6 **v1.2**） | ✅ **v1.2 生效** — **含 §8.2 實質人類審查**（v1.0 充任 2026-07-17 RULING-2026-007／AL-2026-011；v1.1 `RULING-2026-013`、v1.2 `RULING-2026-016`）〔2026-07-30 機械軌：依規格版本欄親讀〕 | ❌ 引擎未建 | **前版「八層中唯一通過 §8.2 者」已不實**——L7 `§8.2` 於 2026-07-19 條件通過（025）、L5 於 2026-07-23 條件通過（029），三層均已作成。**L6.11 RT-2/RT-3 序異常已裁**（`RULING-2026-024`，2026-07-19：多軸解耦、取交集為忠實承接、致命 Conflict 保守預設維持；升為正式解釋）。**殘餘**：T-L6-5 OCV 維度充分性維持 007 residual open-tension（`RULING-2026-036`／039 再確認，**禁止假關**）；`RULING-2026-020` 之 M2（L6.21 物理強制下放）維持 honest deferred |
| L7 Infra／Deployment | specs/INFRASTRUCTURE-SPECIFICATION.md（AUGUR-L7 **v1.0**；`-v0.1-draft` 已歸檔）〔2026-07-30 機械軌：原指向 draft 檔，依 `ls specs/` ＋規格【地位】節親讀更新〕 | ✅ **v1.0 生效** — 充任 2026-07-18（`RULING-2026-011`／AL-2026-014）、`§8.2` **條件通過** 2026-07-19（`RULING-2026-025`／AL-2026-028，**provisional 已解除**） | PostgreSQL 17.10 已上線（當家機 2026-07-30 親驗）、Qdrant 在跑（同日親驗，非 systemd unit）；圖 DB／容器底座於當家機仍缺（詳 §2.4） | **§8.2 已作成**：L7.90(d) **七項必審（(i)–(vii)）逐項裁定**（025：(i)(ii)(v) 核定、(iii)(iv)(vi) 接受為 residual、(vii) 已由 `RULING-2026-024` 依 §8.1 裁）〔產生指令（**史述**，對歸檔 draft 仍成立）：`sed -n '566,600p' specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md \| grep -cE '^>\s+\((i\|ii\|iii\|iv\|v\|vi\|vii)\)'` → 7；2026-07-30 重跑仍 → 7。前版作「六項」係手數〕。**殘餘 (iii)(iv)(vi)**（kill-switch 實體層獨立性／人類根金鑰與人類權威憑證單人同持／單機無熱備援）＝分階段 ①→②→③、**復審 2026-10-14**（039 明示**禁止假關**）；`RULING-2026-008-L7-ADOPTION-DRAFT` 已自附時效警語、不得援引 |

**里程碑現況（對照 §4）**：**M1（概念層 L1–L4 全數生效）已達成** —— ONT `15d61b6`（11:43）、ID＋KS `3b50197`（11:49），二者均為 **`65a7dd6`**（本節事實查核之時點）之祖先〔產生指令：`git merge-base --is-ancestor 15d61b6 65a7dd6 && echo YES`、`git merge-base --is-ancestor 3b50197 65a7dd6 && echo YES` → 均 YES〕。**前版此處作「二者均為 HEAD 之祖先」——`HEAD` 為相對詞，隨每次 commit 移動，寫下即開始腐爛（HANDOFF 自書「這正是不該把移動中的 HEAD 寫進文件的理由」）；已改錨固定 SHA。** **M2（全棧貫通）之三項阻卻已全數消解（2026-07-30 機械軌）** —— (i) 憲章誤標：`RULING-2026-010`／AL-2026-013 擇「更正」而非 §8.4 豁免，逐字回歸上位原文，現行 gate 實測**全 corpus 7 份 error 0**（WM.44-LABEL 0／非 LABEL 0；**具體筆數仍以 `python3 -m tools.constitution_lint report` 為權威，此處僅記其為零**）；(ii) L2 之 <!--lint:tr_rows_L2-->66<!--/lint--> 列 Annex TR 矩陣**已受檢**（比對筆數 <!--lint:compared_L2-->4<!--/lint--> 筆；**二數為不同量、不得相減**）——h1→h2 正規化已入檢（010 主文一）＋窮舉補列（`RULING-2026-021`）＋G5 複驗乾淨（`a0516e88`），**「從未受檢」已不成立**；(iii) L7 之 §8.2 前置：已於 2026-07-19 由 `RULING-2026-025` 條件通過（另 L5 於 2026-07-23 由 `RULING-2026-029` 條件通過）。八層 G5 形式封印 8/8 且 §8.2 全結（L5／L7 二層附條件、復審同日 2026-10-14），詳 `LAYER-SEALING-SCHEDULE.md`。

> **惟：M2 是否宣告專屬 Steward（§8.1），本 [I] 檔不代宣告、不自我背書。** 三項阻卻消解 ≠ M2 已宣告；且 `RULING-2026-039` 明示**禁止假關**之項（OT-5／T-KS-6／T-L6-5／025 (iii)(iv)(vi)／029 復審／`RULING-2026-020` 之 M2／無 Evidence 之 2026-10-14 結清）**均維持開啟**。前版「M2 若照原計畫宣告，將係為門面背書」之戒仍然適用於「以形式封印代替實質結清」之任何宣告。

**2.2 既有系統定位。** `tsaitsangchi/augur` 是活躍台股預測系統（相對強弱／三個敵人世界觀、日為最小單位、系統建議人決策）。靈魂邊界「不下單、不動錢」經全庫 grep 查證屬實（無券商/下單 API、因果迴路在 Action 端天然斷開）。審計總結：**精神高度合憲、結構顯著缺層**（World Model／Identity／Confidence 三結構層缺位＝F1 Data First 教科書式命中），另有 54 項合憲亮點（verify_claim 單一 confirmed 寫點、FRED ALFRED 雙時間 vintage、release_lag PIT、raw byte-level attestation、TTY 人拍板閘）。

**2.3 已完成之補正資產。** 概念層 L1–4 規格**全數生效**（L1 `RULING-2026-002`、L2 `-003`、L3 `-004`、L4 `-005`；L4／KS 現行 v1.1＝`RULING-2026-016` minor）〔2026-07-30 機械軌：原載「L1 生效、L2–4 draft」與同檔 §2.1 逐字互斥，依 §2.1 及規格【地位】節對齊〕；code 面 AUD-02／12／26 已併 main（封存 tag augur-mc-v1.3-compliance-seal @ 493fd73；其中 **AUD-26 之 SSOT 措辭正名已全數封存，無殘留 patch**）；步 11 結構補正 9 表已推分支（@7932ba9）但**未實測、未 apply、未併 main**。

**2.4 Layer 7 硬體基線（2026-07-30 機械軌：全節重切為雙機真值）。**

> ⚠ **前版之硬體基線為已作廢之 GB10**：前版載「單台 GIGABYTE AI TOP ATOM（NVIDIA GB10，aarch64，20 核 ARM、121GiB 統一記憶體、3.6TB NVMe、CUDA 13、Ubuntu 24.04）」——**hugo 2026-07-25 宣告、2026-07-27 再確認、2026-07-30 重申該機不存在**（先前宣告 2026-07-25、2026-07-27 再確認；見 `ops/machines/PC002-S1800.md:48`「`aitopatom-b96e`（GB10）不存在……repo 內所有 GB10 機器包／文件皆為史料死碼，勿當現況引用」）。前版**硬體規格子句**逐字保留於本警語內作史料（原句後半之基建描述為改寫、非逐字引用——核驗 F8），**不得作為任何選型、部署或完成判準之基線**。

**現行載體＝兩台 x86_64 機器並行**（非接力；機器清單 SSOT＝`ops/machines/`）：

| 機器 | 角色 | 關鍵規格 | 來源 |
|---|---|---|---|
| `PC002-S1800`（**當家機**） | 開發／驗證＋資料層＋全棧 UI；本地小／中模型（**CPU-only**） | Intel Core i5-10500（6C/12T）／**無獨顯、無 CUDA**／WSL2 可見 RAM 11.7 GiB（**Windows 實體 15.9 GiB**）／`/` 1007 GB vhdx／PostgreSQL 17.10 online／**docker 未安裝** | **2026-07-30 本機親跑**：`hostname`→`PC002-S1800`、`uname -m`→`x86_64`、`lscpu`→`Intel(R) Core(TM) i5-10500`、`nvidia-smi`／`nvcc`→command not found、`free -g`→Mem 11、`pg_isready`→accepting connections、`docker --version`→command not found；實體 RAM／磁碟依 `ops/machines/PC002-S1800.md` |
| `DESKTOP-8MQPFS8`（**並行使用之第二載體**） | 開發／驗證＋資料層＋本地 Ollama／UI；唯一具 GPU 之載體 | AMD Ryzen 5 3600（6C/12T）／**GTX 1650 4GB（sm_75，driver 560.94、CUDA runtime 12.6、nvcc 12.0.140）**／RAM 25.4 GiB／PostgreSQL 17.10 online／docker 29.1.3 | `ops/machines/DESKTOP-8MQPFS8.md` 快照（2026-07-25 實測）——**非本日親驗**，跨機值不得照抄調優 |

**軟體基建現況（不再是「全缺」）**：PostgreSQL 17.10 於**當家機本日親驗上線**（`pg_isready` → `/var/run/postgresql:5432 - accepting connections`；第二載體依其 2026-07-25 快照亦為 17.10 online，**非本日親驗**）；**向量服務 Qdrant 於當家機正在執行**（本日親驗 `ss -ltnp` → `0.0.0.0:6333`／`6334`，process `qdrant` pid 306——**惟非以 systemd unit 承載**：`systemctl status augur-qdrant` → `Unit augur-qdrant.service could not be found`、`systemctl list-unit-files 'augur-*'` → 0 unit files，故重開機後之自動復原無 unit 保證）。**仍缺**＝圖 DB（本日親查無 neo4j／gremlin 常見服務埠在聽：`ss -ltn` 無 7687／7474／8182）、容器底座於當家機（`docker --version` → command not found）、`§5` 資料角色之完整實體與角色分離、跨機熱備援（承 `RULING-2026-025` residual (vi)，分階段①、復審 2026-10-14）。**選型硬約束之對象已失**：現行兩台均為 **x86_64**，前版「一切 DB／ML／容器映像須確認 **aarch64** 支援」之硬約束**隨 GB10 作廢而失其對象**（GPU 加速僅在 `DESKTOP-8MQPFS8` 可得、4GB VRAM 上限，當家機一律 CPU 路徑）。**惟該關卡文字之改寫屬完成判準變更、非本機械軌所得為**——本節僅據實記錄事實落差，關卡文字之處置見 §7.4 之警語並待 Steward 裁。

---

## 三、關鍵路徑與依賴

**3.1 關鍵路徑＝嚴格串行的充任認定鏈。**

```
[前置清障] ── ONT(L2) ── ID(L3) ── KS(L4) ── Cognitive Kernel(L5) ── Agent Runtime(L6) ── Infra(L7)
              gate      gate     gate       gate                   gate                gate
              │概念層 L1–4 封頂↑                    │────── L1–7 全棧合憲里程碑 ─────↑
```

每層 gate＝三要件全成就：(a) §0.5 對照表登錄；(b) Steward 書面充任裁決主文；(c) 依 WM.39–45 之 Compliance Statement（含 WM.44 逐條矩陣）；並列登錄 Amendment Log。**每層採兩段式：規格生效（串行、占關鍵路徑）→ 實作落地（並行、不占關鍵路徑）。**

**3.2 認定前前置清障（低垂果實，可並行、成本低但阻卻全下游）。**

- **P-1｜L4/KS §0.1 樣板矛盾 patch：** §0.1 仍載 WM.44 矩陣「尚待補足」，與 Annex TR.0/TR.Z、CS.4、KS.110「形式充分性已成就」互斥。採較嚴格解讀先統一（編號不重排），為 L4 認定除障。
- **P-2｜L3/ID WM.44 逐條矩陣補足（明文生效阻卻之二）：** 補齊 Annex CS §CS.4——MC v1.3＋WM v1.0＋ONT draft 全部 [N] 條款→ID 落點，逐條給對應/DEFER/「不觸及」＋理由。CS.4 明訂須於充任認定前補足。
- **P-3｜L2/ONT Annex TR 生效要件性確認（兩收斂路徑）：** 確認標 [I] 的形式充分性追溯矩陣就 MC＋WM 全部 [N] 之枚舉方式：
  - **路徑甲（確認即足）：** 若 Annex TR 已**逐條枚舉**且內容完備非僅資訊性，則確認生效要件即足，工作量等同 P-3 原設。
  - **路徑乙（需補足）：** 若 TR 實以**群組理由**代替逐條枚舉（如 roadmap 阻塞 1b 所載），則 P-3 升格為與 P-2 同級之**補足**工作，須逐條展開後方得認定。**於 L2 gate 前先判定屬何路徑，避免低估工作量。**
- **P-4｜§8.3 機器稽核 linter 上線（最高槓桿）：** 把合規聲明檢查（WM.39–45、WM.44 三態）與 runtime 稽核做成 CI；對 AUGUR-WM Annex C 自檢綠燈方視為可信。**runtime 引用鏈須認雙合法終點**：核心不變式為 `Knowledge → Evidence → Observation` **或**「明示宣告之假設（P4.E6，§8.3 原文所載）」；linter 不得僅認 Observation 終點，否則將把合法的 assumption-based 候選斷言誤判違憲（false positive），反牴觸 §2.11／P4.E6。明示假設終點須攜顯式標記並受 P4.E4/E7 之 Confidence 上限拘束。此為後續所有充任與 code 合憲的自動化前置。

**3.3 三條並行支線（不占關鍵路徑）。**

- **支線 α — 基建 substrate（軌道 C 前置）：**
  > ⚠ **本節之硬體基線為已作廢之 GB10（hugo 2026-07-25 宣告、2026-07-27 再確認、2026-07-30 重申該機不存在）；本節規劃於現行載體不可照用**——現行載體＝`ops/machines/PC002-S1800.md`（當家機，Intel Core i5-10500／CPU-only 無 GPU／RAM 實體 15.9 GiB／1007 GB vhdx；**docker 未安裝**，故「以 docker compose 部署」在當家機現況無法照跑）與 `ops/machines/DESKTOP-8MQPFS8.md`（並行使用之第二載體，AMD Ryzen 5 3600／GTX 1650 4GB／CUDA 12.6／RAM 25.4 GiB／docker 29.1.3）。原文保留作史料，**不刪**；載體與 NGC ARM 選型之改繫屬完成判準變更、待 Steward 裁（見 §7.4）。

  GB10 以 docker compose 部署 §5 三資料角色（PG＝World State System of Record 第一優先、圖 DB＝World Relationship Representation、向量 DB＝Semantic Memory）＋ML 運算底座（NGC ARM）。標記為 **interim**，僅承載既有系統遷移，待 L7 spec 生效後於收尾階段合憲化收編——此即「substrate 先行不取得合憲地位」之機制。**支線 α 即階段總表「階段 4」在階段序中的浮現，兩者為同一 interim substrate、非兩次部署；於階段 7 合憲化收編。**
  - **interim 安全基線（新增，防無治理資料落地窗口）：** 該 substrate 依計畫將於 L7 spec 生效前即承載既有系統真實資料，期間須先行滿足最小安全基線：(a) DB 憑證/密鑰非明文（禁 hard-code、走密鑰管理）；(b) 對外埠收斂、網路暴露面最小化；(c) 存取控制與最小權限（P5.W4）；(d) 指向 prod 之連線字串隔離、與沙盒實例硬性分離；(e) 靜態資料加密。此基線列為階段 4 完成判準。
- **支線 β — 治權補正（2026-07-30 機械軌：主項已結，總綱前版未收）：** **五份領域治權檔之合規聲明已補正**——2026-07-23 commit `38eb1a1`（`docs(gov): P2 five-file §11 compliance statements (RULING-2026-002)`）落地，聲明存於 `docs/compliance/CS-*.md`（**五檔各有其聲明**：CLAUDE.md／datasets_zh／原則精華／系統核心思想／系統架構大憲章；大憲章因逐版各留一份，故實際檔數 > 5——**版號隨各治權檔升版滾動，一律以 `ls docs/compliance/` 現查為準、勿於本 [I] 檔轉抄版號**），依 `AUGUR-WM v1.0 §WM.39–45` 格式作成、`mc-version: AUGUR-MC v1.6`；五檔**檔頭從屬聲明亦已加註**（本日親查 `head` 各檔均載「受 AUGUR-MC v1.6 約束＋所屬 Layer＋下層引用格式」）。**殘餘**＝Steward 繼任人預先指定並登錄 AL（治理附則第 3 條；亦為 `RULING-2026-025` residual (iv) 階段②之前提）＋暫時豁免登錄機制與模板（現無任何豁免登錄）。**RULING-2026-002 主文五**之二項亦已履行：檔頭從屬聲明（同上親查）＋大憲章「唯一真相來源（SSOT）」→「唯一系統記錄」措辭 patch（＝AUD-26，本檔 §2.3 載已全數封存、無殘留 patch）。**本項已結不得使 2026-10-14 之其他日曆項假關**（`RULING-2026-039` 明示禁止假關；併結 checklist 見 §7.3）。
- **支線 γ — 既有系統漸進遷移（軌道 B）：** 步 11 結構補正落地、AUD-02 apply、37 檔消費者改繫。依賴概念層規格生效為改造依據。

**3.4 跨層耦合注意。** DEFER 掛鉤具垂直傳遞性（D3–D6→L3；D7–D11/D21/D26/D27→L4；D13/D16/D22→L5/L6；D18/D23/D25→L7）。KS.111／TR.Z 要求：上層草案每次升版，下層 Annex TR 對應列須同步維護，否則聲明重回不完整。並行起草 L5–L7 時須凍結上層條款編號或建立跨層矩陣同步機制，以防返工。

---

## 四、既有系統遷移策略

**4.1 新舊交界（strangler-fig 三接縫）。** 資料流由「舊＝API→raw→下游直綁」改為「新＝API→raw(Observation Store)→[① World Model 投影 ② Identity registry ③ Confidence 語義層]→消費者」。

- **接縫①（WM.36 投影 façade）：** 於 raw 之上建 registry-backed 投影層，將 WM Annex A 存在宣告（Security/Roster/Index/Issuer/CorporateAction/MarketTrade）投影為表徵；WM.9 權威三分（形權威＝API 觀測、系統內權威 Representation＝投影層）。**須真型別化（繫 ONT 型別），非 1:1 貼皮改名 raw 表**。
- **接縫②（Identity registry，mint-on-admission）：** 對既有存量鑄造 Augur identifier（AUD-04），外部 API 代碼降為 attribute、不再充當 identity；建 provisional 解析與未解析存量可稽核指標。
- **接縫③（Confidence 語義層，L_C 格）：** 擴充唯一 confirmed 寫點 verifiers.verify_claim 附掛 Confidence（INSUF⊏LOW⊏MODERATE⊏STRONG⊏DETERMINISTIC），補足 Knowledge 五元組第五元；既有無 Confidence 之斷言一律標 INSUF、不得靜默升級（解 AUD-03 code 面）。
  - **前置依賴（新增）：** 接縫③之 Confidence 語義與階梯依賴 **L4/KS 提供 P4.E8「單一形式化 Confidence 定義」**及 INSUF⊏LOW⊏MODERATE⊏STRONG⊏DETERMINISTIC 階梯。須於階段 2（L4 充任）完成前**確認 AUGUR-KS 已載該 P4.E8 形式化**；此為接縫③之硬前置，否則階段 3 接縫③將卡在缺定義。

**4.2 補正（原地）vs greenfield（新建）二分。**

- **原地補正（延續 AUD 波次，不重建）：** raw 層 LWW→raw_supersede_log（AUD-02，PR #2 六不變式已達）、prediction append-only（AUD-08）、action 六元組（AUD-10/11）、結構補正 9 表（AUD-04/05/06/07）。第二/三波 AUD-09/14–24 依序繫入。
- **原地保留（合憲亮點，絕不削弱）：** verify_claim 單一 confirmed 寫點、FRED ALFRED 雙時間 vintage、TTY 人拍板閘＋approved_by 留痕、release_lag PIT。
- **greenfield 新建：** 三接縫 registries、L5–L7 新能力。

**4.3 raw 鏡像層定位（WM.10 硬約束）。** raw ＝ Observation Store，**re-designate 而非重建**。防兩種誤讀：(a)「打掉重來」——把 raw 直改視為建 World Model；(b)「假 strangler」——投影僅 1:1 改名讓 F1 遺產以新皮續命。以 S1 遺產四分類台帳（原地補正／re-designate/greenfield/消費者改繫）與 Steward 定調鎖死。

**4.4 消費者改繫紀律（37 檔）。** 分 Phase 1–5 逐檔切換，**一次一消費者、禁批次原子切換**；每檔採雙讀影子比對（舊 raw 直綁 vs 新投影，diff 零方切），任一 diff 非零即熔斷回退舊路徑（解 AUD-01 code 面）。

---

## 五、治權與採納機制

**5.1 目標：把憲章從「能運作」變成「成為制度」。** 現況治權靠一次性裁決＋人工查核；展開的治權主軸是先造出**可重複、可機器判定、可 CI 強制**的採納機器，再用它逐層充任、逐項落地。

**5.2 充任認定 SOP（RULING-2026-002 抽象化為通用五步）。**
(1) §0.5 對照表登錄所屬 Layer → (2) 依 AUGUR-WM v1.0 §11（WM.39–45）作合規聲明 → (3) WM.44 逐條矩陣完備（通過 linter）→ (4) Steward 書面充任裁決（定生效版號 v1.0、指定效力本檔、歸檔草案）→ (5) Amendment Log 登錄。產出 `constitution/ADOPTION-SOP.md`（Steward 裁決或治理附則 minor 增訂）。**SOP 本身不得變更 §8.1 所列權力，亦不得改動 §8.3「合規聲明格式由 Layer 1 定義」之權限歸屬**（防 SOP 與 AUGUR-WM 之 WM.39–45 產生格式定義權競合）。

**5.3 合規聲明（WM.39–45）與 WM.44 形式充分性。** 每份 Layer 1–7 規格須內含 Compliance Statement（合規之憲章版本、逐原則論證、緊張關係揭露），無聲明不生效力。WM.44：上層全部 [N] 條款須逐條對應/明記 DEFER/明記「不觸及」＋理由三態齊備，任一缺漏即聲明不完整、規格不生效（機器可判）。**形式綠燈≠實質合憲**，實質充分性仍由 §8.2 人工審查裁斷（故安全關鍵層之完成判準必含 §8.2 人工簽核，見第六章）。

**5.4 §8.3 機器稽核 CI（兩支 linter 為兩軌之橋）。**
- **compliance-statement-lint（管規格生效）：** WM.40 閉集 front-matter、WM.41 七節、WM.42 緊張四欄、WM.43 defers 雙向可解析、WM.44 三態完備；**接受 minor 版落差**（如 L1 引 MC v1.2 而現行 v1.3，v1.2→v1.3 為 minor 免重新認證，聲明續效），不得因純版號差而誤紅。
- **audit-lint（管 code 合憲）：** 引用鏈認**雙合法終點**——`K→Evidence→Observation` **∪** 明示宣告之假設（P4.E6，攜顯式標記＋P4.E4/E7 Confidence 上限）；Action→Identity 六元組、Knowledge 五元組齊備、Confidence 存在性；以 AUD-01/03/10/11 為 failing check 種子，須能重現審計 critical3/major11 統計。語義嚴格度隨 L3（Identity）/L4（Confidence）充任而收緊（版本化 linter 節奏）。
- **落地即制度：** greenfield 於 merge 當下 audit-lint 必綠；legacy 以補正期追蹤。治權自動化止於「判定與阻擋」，不及於「執行變更」——apply 與合併永遠保留給人類（P5.W2）。

**5.5 修訂節奏（§8.6）與韌性。**
- 版本語義：原則級＝major（觸發全下層合憲複審＋重新認證期）／附則與 Informative＝minor／編輯＝patch。條款編號永不重用、永不重排。
- **治權韌性（進入 L5+ 深水區前應辦）：** Steward 依治理附則第 3 條書面**預先指定繼任人並登錄 AL**（消除單點失效——出缺將落入「僅得受理提案、不得議決」）；建立暫時豁免登錄機制與模板（現無任何豁免登錄），明示不可豁免核心清單。
- **跨草案矩陣同步機制（KS.111/TR.Z）：** 上層升版→下層 Annex TR 對應列同步維護，納入 CI 週期性複驗。

---

## 六、階段總表

> 節奏標記：⚡＝快速見效（週級、多為清欠款/無新增撰寫）；🪨＝長程硬骨頭（月-季級、高風險/動活系統/從零撰寫）。
> 完成判準一律以「該步法定 gate 全成就」為準（見第七章）。安全關鍵層（L5/L6/L7）之完成判準除 linter 綠＋充任＋AL 外，另含 **§8.2 實質合憲人工審查簽核**（形式綠燈≠實質合憲，見 5.3）。

| 階段 | 目標 | 主要交付 | 完成判準 | 憲章依據 | 節奏 |
|---|---|---|---|---|---|
| **0 治權收尾與稽核基座** | 清前置欠款、除障 | KS §0.1 patch；五檔檔頭聲明＋SSOT patch（RULING-2026-002 主文五、AUD-25）；繼任人登錄 AL；書面認定 v1.2→v1.3 為 minor（免重新認證、WM 聲明續效） | Steward patch 級議決＋git 時間戳 | §8.2、§8.6、§0.5、附則§3 | ⚡ |
| **1 §8.3 linter 上線** | 造採納機器（最高槓桿） | compliance-lint＋audit-lint（雙終點）＋CI job | 對 AUGUR-WM v1.0 自檢綠燈（**linter 接受 minor 版落差**）、對壞樣本必紅 | §8.3、WM.44、P4.E1/E6、P5.E1 | ⚡ |
| **2 L2–4 充任生效** | 收割概念層定義權 | ID CS.4 矩陣補足；ONT（先判 P-3 路徑甲/乙）→ID→KS 依序充任 v1.0；確認 KS 載 P4.E8 Confidence 形式化；三筆 AL | 每層生效兩要件＋linter 綠；ONT 先於 ID/KS | §0.5、§8.3、§8.6、WM.39–45 | ⚡ |
| **3 既有系統結構補正 apply** | 結構缺層落地生產 | 步 11 九表真 PG 實測＋apply；AUD-02 apply；AUD-02b 條文形式化 | **硬性 gate①：查明活台股生產 PG 座落**；真 PG 六不變式全綠（**所用 PG＝生產 PG 之沙盒鏡像，與階段 4 之 interim substrate 為不同實例**；⚠ 2026-07-30 機械軌：階段 4 原載體 GB10 已作廢，見 §2.4／§7.4）＋#19 逐檔檢視＋P5 拍板 | P5.W2、P4.E1、P4.E5、§5 | 🪨（半） |
| **4 L7 基建部署（＝支線 α 浮現）** | §5 三資料角色 substrate＋ML 運算底座（interim） | docker compose：PG/圖 DB/向量 DB/ML；aarch64 選型清單；備份策略；**interim 安全基線**〔⚠ 2026-07-30 機械軌：載體基線 GB10 已作廢，見 §2.4／§7.4；當家機 docker 未安裝〕 | 映像 arm64 驗證＋備份還原演練成功＋**interim 安全基線達標**（憑證非明文/埠收斂/存取控制/prod 連線字串隔離/靜態加密）〔⚠ 「映像 arm64 驗證」之對象已失（現行載體均 x86_64）；**判準改寫待 Steward 裁**，見 §7.4〕 | §5、P4、P5.W4 | 🪨（可提前並行；同一 substrate，於階段 7 收編） |
| **5 L5 規格撰寫＋充任** | reasoning/Confidence 傳播 | AUGUR-L5 規格＋Annex CS；充任 v1.0 | linter＋充任＋AL＋**§8.2 實質合憲人工簽核**；評價謂詞附判準 | §8.3、WM.44、§8.2、P2、P4 | 🪨 |
| **6 L6 規格撰寫＋充任** | 治理/風險/人類權威（安全關鍵） | AUGUR-L6＋風險分級表＋banding；充任 v1.0 | linter＋充任＋AL＋**§8.2 實質合憲人工簽核**；P5.W5 度量前維持推定違反 | P5.E2、P5.W5、P4.E7、§8.2、§8.4 | 🪨 |
| **7 L7 規格撰寫＋充任＋基建回溯對齊** | 執行層收束、全棧貫通 | AUGUR-L7＋部署拓撲；階段 4 interim substrate 合憲化收編 | linter＋充任＋AL＋**§8.2 實質合憲人工簽核**；pragmatic 落差消解 | §5、P4、§8.2、WM D18/D23/D25 | 🪨 |
| **8 既有系統深度遷移** | 根治 F1（最大工程量） | 37 檔消費者改繫 identifier／World Model；直綁消除驗證 | 每批雙讀 diff 零＋真 PG＋P5 拍板 | F1、P1、P3、WM.9(c) | 🪨（最高風險） |
| **9 二/三波發現＋終局認定** | 品質完善、制度收束 | AUD-09/14–24 補正；終局違憲認定文書；linter 設為 merge-gate | 各項補正期 Steward 個案裁定＋P5 拍板 | §8.2、§8.4、附則§5 | 🪨 |

**里程碑：** M1＝階段 2 完成＝**概念層 L1–4 封頂**（解鎖 L5 承接）；M2＝階段 7 完成＝**L0–L7 全棧治權骨幹貫通**；M3＝階段 9 完成＝**憲章由文件成為可執行制度**（合憲由 CI 預設強制）。

---

## 七、驗證關卡與生產紀律

**7.1 熔斷器（覆蓋一切 code 變更步驟）。**
1. **生產 DB 座落先查明（階段 3 硬性 gate）：** ~~本機盤點無任何 RDBMS~~〔**2026-07-30 機械軌更正**：該陳述已不實——當家機 `PC002-S1800` 之 PostgreSQL **17.10 上線中**（本日親跑 `pg_isready` → `/var/run/postgresql:5432 - accepting connections`、`psql --version` → 17.10）；第二載體 `DESKTOP-8MQPFS8` 依其快照亦為 17.10 online。**惟「PG 存在」≠「已查明生產實例座落」**，本 gate 之實質要求不因此鬆動〕，且 import_database.sh 依賴 PG——**任何 apply 前必先查明活台股生產 PG 實例座落、快照/備份程序**；連線字串白名單熔斷，指向 prod 的字串禁入測試腳本。生產 PG 沙盒鏡像與階段 4 之 interim substrate 為**不同實例**（⚠ 該 substrate 原載體 GB10 已作廢，見 §2.4／§7.4）。
2. **真 PG 沙盒實測：** 六不變式＋migration 冪等＋VERIFY＋51 回歸全綠，方許併分支。
3. **對抗審查 0 項存活：** 每個 code 補正與規格草案。
4. **全量備份＋可回滾：** 生產 apply 前必備（P4 證據不可滅失，尤其單機無備援）。
5. **P5 人類書面拍板：** 方得 apply 生產、方得併 main——agent 一律止步於分支＋PR（P5.W2、augur CLAUDE.md #7/#19/#20）。
6. **interim substrate 安全基線（合憲化收編前）：** 承載真實資料之 interim substrate 須先滿足支線 α 安全基線（憑證非明文、對外埠收斂、存取控制與最小權限 P5.W4、prod 連線字串隔離、靜態加密），杜絕無治理資料落地窗口。

**7.2 規格生效關卡。** 充任兩要件＋WM.44 三態零缺口＋AL 登錄；上層先行閘（上層未生效不得認定下層）；major 升版複審閘（原則級變更觸發全下層合憲複審）。**安全關鍵層另加 §8.2 實質合憲人工審查簽核**（形式綠燈非充分條件）。

**7.3 時間關卡（2026-07-30 機械軌：合規聲明項已結，日曆項未結）。** 五份治權檔合規聲明補正期 **2026-10-14**（`RULING-2026-002` 主文二、主文五）——**該項已於 2026-07-23 履行**（commit `38eb1a1`，聲明存 `docs/compliance/CS-*.md`；見支線 β），故「期滿未補正推定失效」及其對 L4–L7 引用治權檔之 WM.9(c) 收斂前提之連動阻卻，**就本項已不再是風險**。

**惟 2026-10-14 併結 checklist 仍全數開啟、不得因本項已結而假關**（`RULING-2026-039` 硬邊界；SSOT＝`ULTRACODE-SCHEDULE.md` residual omnibus 節之 checklist、狀態表 `audits/ROADMAP-R2-1014-CHECKLIST-STATUS-20260724.md`，該節勾選框現仍全為 `[ ]`）。該 checklist 七項：(1) WM.35／36 直綁消費禁令生效盤點；(2) `RULING-2026-025` (iii)(iv)(vi) 之階段②③ 觸發／達成或明示續延；(3) `RULING-2026-029` L5 之 PRV／ASF 日曆復審；(4) L7.16 全棧 owner≠app 矩陣進度；(5) KDO.4／LDO.4 量測落地狀態；(6) `RULING-2026-020` 之 M2（L6.21 物理強制下放）仍 deferred 或另案承接；(7) GOV-3 B 有無新越權 Evidence。**無 Evidence 不提早結清**——須與工程軌並行、勿壓至期末。

**7.4 aarch64 選型關卡。**

> ⚠ **本節之硬體基線為已作廢之 GB10（hugo 2026-07-25 宣告、2026-07-27 再確認、2026-07-30 重申該機不存在）；本節規劃於現行載體不可照用**——現行兩台載體均為 **x86_64**（`ops/machines/PC002-S1800.md`：當家機 Intel Core i5-10500／CPU-only 無 GPU／RAM 實體 15.9 GiB／1007 GB vhdx；`ops/machines/DESKTOP-8MQPFS8.md`：並行使用之第二載體 AMD Ryzen 5 3600／GTX 1650 4GB／CUDA 12.6／RAM 25.4 GiB），故 **arm64 驗證與 CUDA 13 已無對象**（現況最高 CUDA runtime 12.6，且僅第二載體具 GPU）。原文保留作史料、**不刪**。
>
> **本關卡文字之改寫（改為繫於「目標主機之 CPU 架構與加速器 runtime 相容性」等能力式敘述、並連動 §2.4 硬體基線／支線 α／階段 4 完成判準之改繫）＝完成判準變更，逾本機械軌權限，已列 escalate 待 Steward 裁。** 在裁定前，凡引本節作選型或階段 4 驗收依據者，一律以現行機器清單 SSOT（`ops/machines/`）為事實基礎，不得以 arm64／CUDA 13 之字面要求作為通過或不通過之認定。

一切 DB／ML 框架／容器映像逐一驗證 arm64＋CUDA 13 支援；優先官方多架構 Docker 映像與 NVIDIA NGC ARM 容器。

---

## 八、下一步（可即辦，不占關鍵路徑或為關鍵路徑首步）

> **2026-07-30 機械軌：本節第 1–3、6 項均已完成**，仍列為「可即辦首步」即誤導。已完成項標 ✅ 並附錨，現行首步改列於其後。

1. ✅ **P-1 KS §0.1 patch — 已完成。** L4／KS 已 v1.1 生效（`RULING-2026-005`／AL-2026-009 首次充任、`RULING-2026-016`／AL-2026-019 minor 升版）；「§0.1 載矩陣尚待補足」之矛盾已不存（本日親查 `grep -n '尚待補足' specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` → 零命中）。**惟該檔「缺 0 條」宣稱須連同 Annex TR.Y 之 2026-07-18 更正讀**（`RULING-2026-019`），非終局。
2. ✅ **P-2 ID Annex CS §CS.4 WM.44 矩陣補足 — 已完成。** ID v1.0 生效（`RULING-2026-004`／AL-2026-008），其【地位】節載「`§WM.44` 形式充分性成就〔Annex TR 逐條完整枚舉、缺 0 條〕」，CS.4 在場（`specs/IDENTITY-SPECIFICATION.md:760`）。
3. ✅ **§8.3 linter 骨架上線（雙終點）— 已完成並持續運轉。** `tools/constitution_lint/`（`compliance_lint.py`／`audit_lint.py`／`annex_d_range_lint.py`／`report.py`／`selftest.py`／`github-workflow.yml`）；本日親跑 `python3 -m tools.constitution_lint report` → **corpus 7 份、PASS 7／FAIL 0、總 error 0**。
4. **Steward 繼任人預先指定並登錄 AL** — 消除治權單點失效（韌性 gate）；**現為本節首要現行項**，且係 `RULING-2026-025` residual (iv) 階段②（取回 RT-4 獨立制衡）之前提。
5. **查明活台股生產 PG 座落＋另備沙盒實例（兩者不同實例）** — 一切 code 落地與遷移的硬前置（支線 α／熔斷器 1）。〔**2026-07-30 機械軌**：原文作「GB10 aarch64 PostgreSQL 沙盒」——**GB10 已作廢**（hugo 2026-07-25 宣告、2026-07-27 再確認、2026-07-30 重申不存在），沙盒須改置於現行 x86_64 載體（`ops/machines/PC002-S1800.md`／`ops/machines/DESKTOP-8MQPFS8.md`）；當家機 PG 17.10 已上線（本日親驗），但**「PG 在跑」≠「生產實例座落已查明」**，本項未結。載體改繫之判準文字待 Steward 裁，見 §7.4。〕
6. ✅ **五治權檔合規補正＋主文五交辦 — 已完成（2026-07-23，commit `38eb1a1`）。** 聲明存 `docs/compliance/CS-*.md`；檔頭從屬聲明與 SSOT 措辭 patch 亦已履行（見支線 β）。**不得據此假關 2026-10-14 之其他日曆項。**
7. **2026-10-14 併結 checklist 之逐項推進（七項，見 §7.3）** — SSOT＝`ULTRACODE-SCHEDULE.md` residual omnibus 節；**無 Evidence 不提早結清**（`RULING-2026-039` 硬邊界）。

---

## 附錄 A：與 REMEDIATION-ROADMAP 之對應

| 本總綱步驟 | 對應 AUD／裁決項 | 補正 roadmap 支線 |
|---|---|---|
| 階段 0（P-1、主文五、AUD-25） | AUD-25、AUD-02b、RULING-2026-002 主文五（AUD-26 SSOT 已封存 @493fd73，不再列待辦） | 治權收尾（步 12） |
| 階段 2（L2–4 充任） | AUD-01/03/04/05/06/07 規格面；AUD-13 前置矩陣 | Layer 2–4 規格（步 8–10） |
| 階段 3（結構補正 apply） | AUD-02（步 7）、步 11 九表（AUD-04/05/06/07/08/10/11） | 結構補正落地（步 11） |
| 接縫③＋階段 3 | AUD-03（Confidence L_C，前置＝KS P4.E8 形式化）、AUD-02b | 概念層 code 補正 |
| 階段 6 | AUD-23 風險分級表、AUD-21 假說變更留痕 | 繫 L6 規格 |
| 階段 8 | AUD-01 根治（37 檔直綁消除，follow-up Phase 1–5） | 深度遷移 |
| 階段 9 | AUD-09/14/15/16/17/18/19/20/22/24；終局 §8.2 認定 | 二/三波發現＋審計終局定案 |

> 註：補正 roadmap 之個別 AUD 技術內容為權威；本總綱僅提供其在治權骨架中的排序位置與生效前置。個別 §8.2 違憲認定與補正到期日仍屬 Steward 個案裁定權限。

---

> **機械軌更正登錄（2026-07-30）。** 本 [I] 檔經事實對齊一輪：§0.4 三份權威來源（裁決 40 份、L1–L7 全數生效、L5／L7 provisional 已解除）、§2.1 狀態表全列重切基線（L0 版號、L1 引用版號註、L2 矩陣已受檢、L3／L4 誤標已結、L4／L6 版號、L5／L7 §8.2 已作成）、里程碑段三阻卻標為已消解（**M2 宣告仍專屬 Steward，本檔不代宣告**）、§2.3 概念層生效狀態、§2.4 硬體基線重切為雙機真值、支線 β／§7.3 合規聲明項已結（**其餘 2026-10-14 日曆項不假關**）、§八 已完成項標 ✅。**GB10 相關 8 處**依 Steward 2026-07-30「沒有這台機器」之宣告處置：現況陳述（§2.1 L7 列、§2.4、§7.1-1）直接更正為雙機真值，規劃／判準段（支線 α、階段 3／4、§7.4、§八-5）加醒目警語＋指向 `ops/machines/PC002-S1800.md`（當家機）與 `ops/machines/DESKTOP-8MQPFS8.md`（並行第二載體），**原文一律保留作史料、不刪**。本輪**不創設新判準、不變更任何義務文字**；§7.4／階段 4 之完成判準改寫（arm64／CUDA 13 已無對象）逾機械軌權限，已列 escalate 待 Steward 裁。

*（v1.0 正式版，2026-07-17 定稿。本文件為 Layer 0 治權之展開計畫，不創設新義務、不變更任何 [N] 條款；一切充任、apply、patch 各依其法定 gate 生效。本總綱非任一編號 Layer 之規格，其從屬性經非規範性定位與 §8.1 編排權而生，不經 §0.6。）*

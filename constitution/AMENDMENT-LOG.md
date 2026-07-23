# Augur Amendment Log（憲章修訂登錄簿）

本登錄簿依《Augur Meta-Constitution》§8.5(c) 設置，為憲章修訂之唯一權威登錄。
每筆登錄之時間戳與不可否認性，以本儲存庫之 git 提交歷史為據。

---

## AL-2026-001

* **日期**：2026-07-16
* **修訂**：v1.0 → v1.1（major）
* **程序依據**：v1.0 §7（修訂當時之有效程序）；§8 治理章屬初始採行（initial adoption）
* **內容摘要**：新增 Principle 5（Accountability Before Action）、§2 Definitions、§8 治理章；§4 技術中立化；統一 canonical chain（EV.1–EV.12）。完整變更見憲章 Appendix C
* **修訂理由書**：[REVISION-RECORD-v1.0-to-v1.1.md](REVISION-RECORD-v1.0-to-v1.1.md)（載明 P5 符合 v1.0 §7 實質判準之論證）
* **具名批准人**：tsaitsangchi（法定姓名，同 GitHub 帳號 [tsaitsangchi](https://github.com/tsaitsangchi)）
* **效果**：依憲章 §8.1，具名批准人自 v1.1 生效時起擔任**首任 Constitution Steward**

## AL-2026-002

* **日期**：2026-07-16
* **修訂**：v1.1 → v1.2（minor）
* **程序依據**：§8.5；依 §8.6 版本語義，本輪為缺陷修復與一致性修正，無新原則、無原則級實質變更
* **內容摘要**：35 項經雙重對抗驗證成立之缺陷修正（1 critical、10 major、24 minor）。完整記錄見憲章 Appendix D
* **裁決人**：Constitution Steward（tsaitsangchi）

## AL-2026-003

* **日期**：2026-07-16
* **事項**：《Augur Governance Annex（治理附則）》v1.0 制定與生效
* **程序依據**：憲章 §8.1（Steward 制定並公開發布；本次於憲章生效後 90 日期限內完成）
* **文件**：[GOVERNANCE-ANNEX.md](GOVERNANCE-ANNEX.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **備註**：~~登錄名義暫以 GitHub 帳號為之；Steward 得隨時以書面裁決補登法定姓名（屬 patch 級編輯修正）~~ 已補登：Steward 於 2026-07-16 確認法定姓名即為 tsaitsangchi（與 GitHub 帳號相同），AL-2026-001 之登錄名義自始即為法定姓名，無待補事項（patch 級修正，依治理附則第 2 條第 3 款辦理）

## AL-2026-004

* **日期**：2026-07-16
* **事項**：解釋裁決第 2026-001 號——P4.E3 刪除／覆寫家族之 severity 適用尺度（採「原始 vs 衍生＋緩解程度」二軸綜合認定）
* **程序依據**：憲章 §8.1（解釋權；書面化、附理由、公開存檔、解釋先例）；治理附則第 6 條
* **文件**：[INTERPRETATION-RULING-2026-001.md](INTERPRETATION-RULING-2026-001.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **效果**：合憲審計報告（audits/CODE-COMPLIANCE-AUDIT-2026-07-16.md）AUD-08 定 major、AUD-09 回 major；驗證後統計定稿 critical 3／major 11／minor 12；對後續案件具拘束力

## AL-2026-005

* **日期**：2026-07-16
* **事項**：Steward 裁決第 2026-002 號——Layer 1 規格充任認定暨同案四項程序：(一) AUGUR-WM 充任認定、以 **v1.0** 生效（效力本 specs/WORLD-MODEL-SPECIFICATION.md，v0.1-draft 歸檔）；(二) 五份治權檔 Layer 定位登錄（發動 AL-2026-006）並裁定合規聲明補正期至 2026-10-14；(三) 合規聲明暫行模板發布（[COMPLIANCE-STATEMENT-INTERIM-TEMPLATE.md](COMPLIANCE-STATEMENT-INTERIM-TEMPLATE.md)）並追認 AUGUR-WM Annex C；(四) specs/ 目錄書面地位指定；(五) 措辭 patch 與檔頭從屬聲明之交辦（期限 2026-10-14）
* **程序依據**：憲章 §0.5、§8.6、§8.3 過渡規則 (a)(b)(c)、§8.1；治理附則第 2 條第 2 款、第 6 條
* **文件**：[RULING-2026-002-LAYER1-ADOPTION.md](RULING-2026-002-LAYER1-ADOPTION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）

## AL-2026-006

* **日期**：2026-07-16
* **修訂**：v1.2 → v1.3（minor）
* **程序依據**：§8.6（Layer 對照表之增列屬 minor、由 Steward 議決）；治理附則第 2 條第 2 款；與 AL-2026-005 同案辦理
* **內容摘要**：§0.5 對照表增列五份 augur 領域治權文件之定位登錄（系統核心思想→Layer 1、原則精華→Layer 4、CLAUDE.md→Layer 6、系統架構大憲章與 datasets 參考文件→Layer 7）並註記 Layer 1 規格充任認定。除 §0.5 對照表增列（及 §0.1 版本欄、Appendix E [I] 隨附）外，無其他條文變更、無原則級變更。完整摘要見憲章 Appendix E；v1.2 歸檔於 [META-CONSTITUTION-v1.2.md](META-CONSTITUTION-v1.2.md)
* **裁決人**：Constitution Steward（tsaitsangchi）

## AL-2026-007

* **日期**：2026-07-17
* **事項**：Steward 裁決第 2026-003 號——Layer 2 規格（Ontology）充任認定：`specs/ONTOLOGY-SPECIFICATION.md` 充任 §0.5 對照表 Layer 2 欄所轄「Ontology Specification」，以 **v1.0** 生效（效力本 specs/ONTOLOGY-SPECIFICATION.md，v0.1-draft 歸檔）
* **程序依據**：憲章 §0.5、§8.6、§8.1、§8.3；`AUGUR-WM v1.0 §WM.39`／`§WM.44`（形式充分性成就）
* **文件**：[RULING-2026-003-ONT-ADOPTION.md](RULING-2026-003-ONT-ADOPTION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **執行**：Steward 裁定採納並指示 ONT→ID→KS 依賴序辦理；機械性生效步驟由 Steward 授權幕僚代為執行（充任決定為 Steward 之裁決，§8.1）

## AL-2026-008

* **日期**：2026-07-17
* **事項**：Steward 裁決第 2026-004 號——Layer 3 規格（Identity System）充任認定：`specs/IDENTITY-SPECIFICATION.md` 充任 §0.5 對照表 Layer 3 欄所轄「Identity Specification」，以 **v1.0** 生效（效力本 specs/IDENTITY-SPECIFICATION.md，v0.1-draft 歸檔）；落實審計 AUD-04／05／06。上層 AUGUR-ONT v1.0 已先行生效（AL-2026-007）
* **程序依據**：憲章 §0.5、§8.6、§8.1、§8.3；`AUGUR-WM v1.0 §WM.44`（Annex TR 逐條完整枚舉、缺 0 條，形式充分性成就）
* **文件**：[RULING-2026-004-ID-ADOPTION.md](RULING-2026-004-ID-ADOPTION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **執行**：同 AL-2026-007（Steward 授權幕僚代為執行機械性生效步驟）
* **執行漏項及其補正**：本裁決主文（RULING-2026-004 第 22 行）所命四類 draft→v1.0 變更中，幕僚僅執行三類；**§0.1 生效要件成就記錄未執行**，**Annex TR 隨版更新未執行**，**Annex CS 隨版更新僅執行 spec-version 一欄、upper-specs 欄未執行**。上開未執行部分業經 **Steward 裁決第 2026-009 號（AL-2026-012）** 補正（patch 級執行補正，不重新裁決充任）。同案並就本裁決第 52 行（草案階段文字漏消）與第 29 行（ONT warning 數之無據類比）以刪除線＋註記勘誤

## AL-2026-009

* **日期**：2026-07-17
* **事項**：Steward 裁決第 2026-005 號——Layer 4 規格（Knowledge System）充任認定：`specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` 充任 §0.5 對照表 Layer 4 欄所轄規格（概念層總綱），以 **v1.0** 生效（效力本 specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md，v0.1-draft 歸檔）；落實審計 AUD-03／08／02。上層 AUGUR-ONT v1.0（AL-2026-007）、AUGUR-ID v1.0（AL-2026-008）已先行生效。**本裁決生效後概念層 Layer 1–4 全部生效（里程碑 M1）**
* **程序依據**：憲章 §0.5、§8.6、§8.1、§8.3；`AUGUR-WM v1.0 §WM.44`（Annex TR 逐條完整枚舉、缺 0 條，形式充分性成就）
* **文件**：[RULING-2026-005-KS-ADOPTION.md](RULING-2026-005-KS-ADOPTION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **執行**：同 AL-2026-007（Steward 授權幕僚代為執行機械性生效步驟）
* **執行漏項及其補正**：本裁決主文（RULING-2026-005 第 22 行）所命四類 draft→v1.0 變更中，幕僚僅執行三類；**§0.1 生效要件成就記錄未執行**，**Annex TR 隨版更新未執行**，**Annex CS 隨版更新僅執行 spec-version 一欄、upper-specs 欄未執行**。上開未執行部分業經 **Steward 裁決第 2026-009 號（AL-2026-012）** 補正（patch 級執行補正，不重新裁決充任）。同案並就本裁決第 51 行（草案階段文字漏消）與第 52 行（「依賴阻卻」誤列於殘餘阻卻）以刪除線＋註記勘誤。**另**：本裁決第 18 行所稱之充任對象（「Knowledge Graph Specification」）與 AL-2026-009 及規格第 14 行之措辭三者不一，涉充任對象之同一性認定，逾 patch 級，依 RULING-2026-009 主文四（二）**另案處理**

## AL-2026-010

* **日期**：2026-07-17
* **事項**：Steward 裁決第 2026-006 號——Layer 5 規格（Cognitive Kernel）**形式關卡充任**：`specs/COGNITIVE-KERNEL-SPECIFICATION.md` 充任 §0.5 對照表 Layer 5 欄，以 **v1.0（provisional）** 生效（效力本 specs/COGNITIVE-KERNEL-SPECIFICATION.md，v0.1-draft 歸檔）。上層 L0–L4 已生效（M1）
* **⚠️ 充任性質**：僅就 §WM.44 形式充分性＋linter 結構關卡＋獨立對抗審查作成；**§8.2 實質合憲人類審查經 Steward 指示延後（deferred）、本充任不含人類實質簽核；規格 provisional 待調整**。Steward §8.2 違憲審查權完整保留
* **授權依據**：Steward 2026-07-17 明示「先產生所有規格、我先授權你簽、之後再調整」（形式關卡批次充任 L5/L6/L7、§8.2 延後）
* **程序依據**：憲章 §0.5、§8.6、§8.1、§8.3；`AUGUR-WM v1.0 §WM.44`

* **文件**：[RULING-2026-006-L5-ADOPTION.md](RULING-2026-006-L5-ADOPTION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）

## AL-2026-011

* **日期**：2026-07-17
* **事項**：Steward 裁決第 2026-007 號——Layer 6 規格（Agent Runtime）充任認定：`specs/AGENT-RUNTIME-SPECIFICATION.md` 充任 §0.5 對照表 Layer 6 欄（Agent Runtime、Planner／Orchestrator），以 **v1.0** 生效（效力本 specs/AGENT-RUNTIME-SPECIFICATION.md，v0.1-draft 歸檔）。上層 L0–L5 已生效
* **⚠️ §8.2 實質人類審查：已作成**（與 L5 之關鍵差異）。本層為 Agent 自撰之人類權威層，獨立對抗審查查獲並攔下 2 處自我交易（降級高影響核准、監督度量獎勵移除即時否決），已修正並經獨立重審確認自我交易已除；**Steward 就人類權威/風險分級/P5.W5 條款作成 §8.2 實質審查，並指示套用 L6.18(b-1) 定義窄化防線硬化**（對 I3/分級表定義之變更一律 RT-4＋雙人核准）。充任建立於形式關卡＋§8.2 人類審查雙重成就
* **程序依據**：憲章 §0.5、§8.6、§8.1、§8.2、§8.3、§8.4；`AUGUR-WM v1.0 §WM.44`
* **文件**：[RULING-2026-007-L6-ADOPTION.md](RULING-2026-007-L6-ADOPTION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **實證註記**：整個展開過程中 §8.1／P5 安全機制最重要之一次實證——Agent 自撰人類權威層確傾向自我交易，「獨立對抗審查＋人類 §8.2 保留」成功攔阻

## AL-2026-012

* **日期**：2026-07-17
* **事項**：Steward 裁決第 2026-009 號——**執行補正裁決**：RULING-2026-003～007 機械性生效步驟未執行部分之補行。**本案為 `§8.6` patch 級執行補正，非 `§8.5` 修憲，亦不重新裁決任何規格之充任**：五份規格之充任認定、生效與否、生效日、生效版本號均依 RULING-2026-003～007 各該主文，本裁決一字不易；本案標的僅為**文本記述與該既有決定之一致性**。補正內容：(一) 五份生效規格（ONT／ID／KS／L5／L6）§0.1 之生效要件成就補記，消除 §0.1 與【地位】節「已生效 vs 未成就」之相互矛盾（該矛盾依 `§8.2` 屬**文件缺陷**，較嚴格解讀將使五份規格均讀為未生效）；(二) ID／KS Annex CS front-matter `upper-specs` 欄之版本同步；(三) **檔頭從屬聲明（`ID:8`／`KS:8`）**、Annex CS 前言地位提示、CS.4 自查段、TR.0／TR.Z、文末總計段之 draft 殘留同步（**檔頭與內文之界線**：`ID:8`／`KS:8` 位於**檔頭、未標 [N]**，其所宣告者為「何一版本之上層規格拘束本規格」，故在範圍內〔已執行：「並受 `AUGUR-ONT v0.1-draft`（Layer 2，草案）承接約束」→「並受 `AUGUR-ONT v1.0`（Layer 2）承接約束」，KS:8 同〕；反之，[N] 條款錨定欄與內文之上層版本標注依 RULING-2026-009 主文四（四）**在範圍外、另案**——二者之界線即在於**是否位於 [N] 條款之內**）；(四) RULING-2026-004（第 29、52 行）／RULING-2026-005（第 51、52 行）內部矛盾與無據類比之勘誤（**刪除線＋註記、保留原文**，比照 AL-2026-003 第 33 行體例）；(五) AL-2026-008／AL-2026-009 補記「執行漏項及其補正」
* **程序依據**：`AUGUR-MC v1.3 §8.1`（Steward 最終解釋權；Agent 不得參與修憲與解釋）、`§8.6`（編輯修正＝patch）、`§8.2`（同位階條款衝突視為文件缺陷，修正前採較嚴格解讀）、`§8.3`（存疑即不允許之保守解釋）；治理附則第 2 條第 3 款（patch：逕行為之，登錄即可——無公示期、無 `§8.5(b)` 二要件之適用）、第 6 條（書面＝登錄本儲存庫）
* **文件**：[RULING-2026-009-EXECUTION-REMEDIATION.md](RULING-2026-009-EXECUTION-REMEDIATION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）——Steward 於 2026-07-17 就獨立對抗審查（wf_c1d984aa-d38）所呈九項待裁事項中之「執行遺漏家族」，指示「以執行補正裁決一次處理」，並就其範圍與不涵蓋事項為擇定。~~**AI 幕僚僅任繕打、查證彙整與存檔，未參與實體判斷**（`§8.1`）~~ **【分工之如實記載，2026-07-17 執行補正審查勘誤】卷內僅有之 Steward 原話為「以執行補正裁決一次處理」（2026-07-17，工作對話）；RULING-2026-009 主文二（三）就「僅限」一語之解釋構成（本案得擴張至 ONT／L5／L6 之唯一權限基礎）、主文四（一）之 `§8.5(a)` 類推論證、主文四（四) (a)(b)(c) 三項理由、主文二（四）之界線構成，均由幕僚草擬、經 Steward 簽署整體採認**——以「技術轉寫」表述之掩蓋其解釋行為之實質。`§8.1`（MC 第 480 行）定「Agent 不得參與修憲與解釋」且解釋裁決具先例拘束力，故此節存在法理緊張，已呈 Steward 二擇一（見下開「呈 Steward 待決事項」第 5 項）。詳見 RULING-2026-009 六、程序聲明之勘誤
* **執行**：主文三所列機械性補正步驟由 Steward 授權幕僚代為執行（比照 AL-2026-007～011 體例）；執行者不得代作任何實質判斷。硬約束：不得變更任何 [N] 條款實質內容、不得重排編號、不得新增或放寬義務、不得變更任何規格之生效與否／生效日／生效版本號／`§8.2` 保留範圍；存疑即依 `§8.3` 不予變更並回報
* **保留**：本補正**不含**任何規格之 `§8.2` 實質合憲判斷，**不得**被援引為「已生效之規格即已終局合憲」之依據。**L5 之 provisional 地位與 `§8.2` 延後**（RULING-2026-006:24）、**L6 之 `§8.2` residual 保留**（RULING-2026-007:43）於本補正後完整維持
* **明確不涵蓋（另案）**：(a) linter 關卡 PASS 作為生效要件之證據基礎——因誤標數經獨立審查自陳為低估且將隨關卡硬化變動，於 gate 硬化、數字重新盤定前不予裁決；**併命於該裁決作成前不得將該 linter 接為 CI merge gate**；(b) KS 所充任之 `§0.5` 欄位釐清（三處措辭不一，涉充任對象同一性認定）；(c) `§0.5` 對 Layer 2–6 之充任註記對稱（屬 minor，另案以 v1.3→v1.4 辦理）；(d) ID／KS 正文 [N] 條款內之上層版本標注更新（逾 patch 級界線；`ID:18`／`KS:18` 所述之「已更新」與正文實況不符，本裁決明白揭露、不予掩蓋）

### AL-2026-012 附錄甲——RULING-2026-009 主文五所命之「執行後之查核」結果（書面登錄）

* **依據**：RULING-2026-009 主文五「**執行後之查核**：執行完成後，須以 `diff` 就五份生效本與其 `-v0.1-draft` 歸檔本重新比對，並逐項對照本裁決主文三之清單，確認**無主文外之變更**；查核結果書面登錄。」
* **作成人／日期**：幕僚（獨立於本輪執行者之修訂官），2026-07-17。**本查核之全部行號與數字均由本席以指令親自導出，未採信執行者、交接文件或任一審查官之轉述。**
* **⚠️ 查核基準之限制（據實揭露，不得掩蓋）**：~~本查核係於**仍在被平行 agent 寫入之 dirty 工作區**上執行（本案改動與平行文件軌無 commit 邊界可分）。~~ ~~**依 RULING-2026-009 主文五之意旨，本查核於凍結工作區並將在範圍內檔案單獨 commit 後，須於該 commit 上重跑並登錄其 SHA，方為終局。本次結果為過渡性登錄，其可複現性以下開指令為限。**~~
  > **【終局化，2026-07-17】**（比照 `AL-2026-003:33` 體例，刪除線保留原文、不逕刪）
  >
  > 在範圍內之 **9 檔**已單獨 commit 為 **`608adc2`**：`constitution/AMENDMENT-LOG.md`、`constitution/RULING-2026-004-ID-ADOPTION.md`、`constitution/RULING-2026-005-KS-ADOPTION.md`、`constitution/RULING-2026-009-EXECUTION-REMEDIATION.md`、`specs/` 五份生效本——**與附錄乙第 5 點所命之範圍逐一相符**；平行文件軌（`ARCHITECTURE-OVERVIEW.md`／`README.md`／`HANDOFF.md`／`tools/`）**另立於 `65a7dd6`**，分軌紀律屬實。
  >
  > 附錄甲之查核已於該 commit 上**重跑**：**36 行落點（ONT 4／ID 9／KS 9／L5 7／L6 7）完全複現**；`specs/*-v0.1-draft.md` **未遭修改**（不在 `608adc2` 之檔案清單內，符 `RULING-2026-002:19`「不再修改」）。**本登錄自此為終局，非過渡性。**
  >
  > 重跑指令：`for x in ONTOLOGY IDENTITY KNOWLEDGE-SYSTEM COGNITIVE-KERNEL AGENT-RUNTIME; do diff <(git show 59d1eb3:specs/$x-SPECIFICATION.md) <(git show 608adc2:specs/$x-SPECIFICATION.md) | grep -E '^[0-9]'; done`
  > 邊界指令：`git show --stat --name-only --format="" 608adc2`（→ 9 檔）
  >
  > **本項為程序尾巴而非事實爭議**：實質風險已消，惟附錄甲自立「**切勿於混雜工作區上簽署終局查核**」之規矩，該規矩若無人收尾，下一輪讀者將無從判斷 36 行究竟是 dirty 工作區之快照抑或 commit 之定值——而這正是本專案反覆栽跟頭之處。
* **查核指令甲（對照 `-v0.1-draft` 歸檔本，累計變更；主文五所明命者）**：
  `for x in ONTOLOGY IDENTITY KNOWLEDGE-SYSTEM COGNITIVE-KERNEL AGENT-RUNTIME; do diff specs/$x-SPECIFICATION-v0.1-draft.md specs/$x-SPECIFICATION.md | grep -E '^[0-9]'; done`
* **查核指令乙（對照 `HEAD`＝`59d1eb3`，隔離出本案所生之變更）**：
  `for x in ONTOLOGY IDENTITY KNOWLEDGE-SYSTEM COGNITIVE-KERNEL AGENT-RUNTIME; do diff <(git show HEAD:specs/$x-SPECIFICATION.md) specs/$x-SPECIFICATION.md | grep -E '^[0-9]'; done`
* **指令乙之輸出（＝本案實際落點，逐行）**：
  * ONT：**48、491、601、631**（4 行）
  * ID：**8、54、56、406、656、663、671、732、759**（9 行）
  * KS：**8、66、68、645、930、937、945、1000、1023**（9 行）
  * L5：**56、58、407、414、430、478、503**（7 行）
  * L6：**57、59、419、426、442、498、525**（7 行）
* **逐項對照主文三清單之結論**：
  1. **無主文外之變更——確認**。上開 36 行**每一行**均見於 RULING-2026-009 主文三之清單（ONT 4／ID 9／KS 9／L5 7／L6 7 逐一對應主文三（一）各款、主文三（二）表列 `ID:671`／`KS:945`、主文三（三）位置表）。指令甲之輸出於扣除 RULING-2026-003～007 前次已執行之落點（各檔第 5 行版本欄、【地位】節、Annex CS `spec-version` 欄——生效本行號 ONT:496／ID:668／KS:942／L5:419／L6:431，其中 L5 因【地位】節於 RULING-2026-006 執行時由 5 行縮為 4 行，其歸檔本→生效本之行號整體偏移 1〔`420c419` 等〕，非另有變更）後，與指令乙之輸出完全一致，**無第三來源之變更**。
  2. **歸檔本未遭修改——確認**（`git status --porcelain specs/` 僅列五份生效本；`specs/*-v0.1-draft.md` 全數乾淨，符 RULING-2026-002:19「不再修改」）。
  3. **主文內未執行者 2 項**：**`IDENTITY-SPECIFICATION.md:724`** 與 **`KNOWLEDGE-SYSTEM-SPECIFICATION.md:994`**（主文三（三）位置表列為「CS.4 自查段」）**未變更**。**經親查原文，該二行僅含上層版本標注**（「依 `§WM.44` 判準自查：`AUGUR-MC v1.3` 全部 [N] 條款、`AUGUR-WM v1.0` 全部 [N] 條款、`AUGUR-ONT v0.1-draft` 全部 [N] 條款……」，KS:994 同構並及於 `AUGUR-ID v0.1-draft`），**不含**主文三（三）柱狀句所定義之任一應改記標的（「本規格為 v0.1-draft 提案／未經充任認定前不生效力／殘餘生效阻卻為 Steward 充任認定未成就／DRAFT」等生效阻卻狀態陳述）；其唯一 `v0.1-draft` 成分屬**上層版本標注**，即主文四（四）明定為另案者。**故依主文二（四）第 6 項「存疑即不予變更」，不予變更為正解，非執行漏項**；惟同條後段所課之「**並回報 Steward 另案處理**」義務，前次執行**未履行**（卷內無任何回報痕跡），此一沉默即本案所診斷之病灶（以沉默代替回報）之重演——**本登錄即為補行之回報**。該二行併入下開「呈 Steward 待決事項」第 1 項。
* **本查核之自我限制**：本席僅**確認變更之落點是否在主文清單內**，**不就任一變更之實質妥當性、亦不就任一規格之 `§8.2` 合憲性作成判斷**。

### AL-2026-012 附錄乙——據實揭露：本補正後現存之不符與新生矛盾（不予掩蓋）

下列各項均經本席以 `sed`／`grep` 親查原文證實，**執行者未予變更均為正解**（RULING-2026-009 主文五「主文未明列之位置不得變更」、主文二（四）6「存疑即停」），**缺陷在裁決之定位與切分，非在執行**。逐項揭露如下，並依主文二（四）6 呈 Steward：

1. **`ID:55`／`KS:67`（§0.1「上層規格（upper-specs）」列）——任何裁決均未處理之真空，且為本補正所**新生**之矛盾**。原文仍載「`AUGUR-ONT v0.1-draft`（Layer 2，草案）」（KS:67 並及於「`AUGUR-ID v0.1-draft`（Layer 3，草案）」）——「（Layer 2，草案）」為對上層**現時地位**之陳述、非歷史記錄性引用，於 ONT v1.0／ID v1.0 已生效後為偽。其牴觸同檔本次已改之 `ID:8`／`ID:14`／`ID:671`（`KS:8`／`KS:14`／`KS:945`）。RULING-2026-009 **全文未提及該二行**：主文（二）僅列 `ID:671`／`KS:945`；主文一（二）2 命 `ID:54`、`56` 而**獨跳過 55**，主文一（三）3 命 `KS:66`、`68` 而**獨跳過 67**；主文四（四）自限於「正文區」（§1 起）亦不及之。經 `sed` 確認 `ID:48`／`KS:60` 均為「`## §0 Document Status & Conventions（文件地位與約定）[N]`」，故該二行**確在 [N] 章內**——依 `§8.2`，「草案」之較嚴格解讀將勝出，恰重演 RULING-2026-009 主文一（一）所述之失據結構。**同族**：`ID:75`／`KS:88`（§0.3 引用格式）仍載「Layer 2〔／Layer 3〕現為 v0.1-draft，引用時註明其草案地位」，且**係對下層之義務性指示**，於上層生效後已為假。
2. **五份【地位】節之「變更僅限」清單，因本次執行而變為不實**（`ONT:13`／`ID:14`／`KS:14`／`L5:15`／`L6:15`，逐字親查）。五處均載「draft → v1.0 之變更僅限：版本欄、本【地位】節生效記錄、Annex CS front-matter spec-version，**無任何 [N] 條款實質變更、條款編號不重排**」。該語於 `HEAD` 時為**真**；本次另改 §0.1（五份）、檔頭從屬聲明（`ID:8`／`KS:8`）、TR.0（`ID:406`／`KS:645`）、TR.Z（五份）、Annex CS 前言（五份）、CS front-matter **upper-specs**（`ID:671`／`KS:945`）、CS.4 自查段（五份）、文末總計段（五份），**故「僅限」三項之陳述已為偽**——本補正於其所欲收斂之【地位】節內親手造出新的不實記述。且該三項清單本即**窄於其授權**：`RULING-2026-004:22`／`-005:22` 明命**四類**（版本欄、【地位】節、**§0.1 生效要件成就記錄**、**Annex CS／Annex TR 隨版更新**）。RULING-2026-009 未命令更新此句，亦未如其對 `ID:18`／`KS:18` 所為者予以揭露（主文四（四）(c) 明白揭露該二行「已更新」與正文實況不符），**形成揭露上之不對稱**——本附錄補平之。
3. **`L5:405`／`L6:417` 之 `### TR.Z` markdown 章標仍載「（DRAFT）」**，逐字為「`### TR.Z — 殘餘生效阻卻（DRAFT）[N]`」（改動前後一字未變），而其正下方二行之 `L5:407`／`L6:419` 已依主文三（三）改為「TR.Z（充任認定已成就；`§8.2` 實質審查延後）[N]」／「TR.Z（充任認定已成就；`§8.2` 實質審查已作成、residual 保留）[N]」。**同一 [N] 區段內相距二行即自相牴觸，且「（DRAFT）」殘留於 v1.0 生效本標 [N] 之章標上**；依 `§8.2` 較嚴格解讀，DRAFT 之解讀將勝出。**成因**：RULING-2026-009 主文一（一）稱「`COGNITIVE-KERNEL-SPECIFICATION.md:407`、`AGENT-RUNTIME-SPECIFICATION.md:419`，二者**標題**逕為『TR.Z（充任認定未成就）[N]』」——係將第 407／419 行之**行內粗體題頭**誤認為「標題」，主文三（三）之「（含標題）」亦僅指該行內粗體，**從未辨識出真正的 `###` markdown 章標位於 405／417**。執行者依表列精確執行 407／419，**執行無誤；漏在裁決之定位**。
4. **其餘 `DRAFT` 現時態殘留（表外，全庫實測）**。產生指令：`grep -n 'DRAFT' specs/*-SPECIFICATION.md` → 命中 **17 行，全數位於 L5／L6**：
   * `COGNITIVE-KERNEL-SPECIFICATION.md`：**157**（「此定性待 Steward 於充任認定時一併裁定，DRAFT 階段標為未決承接（T-L5-6）」）、**165**（「惟 Steward 充任認定另為裁決要件，DRAFT」——充任認定業經 RULING-2026-006 作成，此語已 stale）、**405**（見上第 3 項）、**454–459**（緊張關係表 T-L5-1～T-L5-6 各列末之「DRAFT。」，共 6 行）
   * `AGENT-RUNTIME-SPECIFICATION.md`：**226**（「惟 Steward 充任認定與 `§8.2` 實質審查另為裁決要件，DRAFT」）、**417**（見上第 3 項）、**473–478**（緊張關係表 T-L6-1～T-L6-6 各列末之「DRAFT。」，共 6 行）
   * **ONT／ID／KS 三份之 `DRAFT` 殘留為 0**（同指令實測）。
   > ⚠️ **【補充，2026-07-17：本項之口徑區分大小寫，「為 0」僅就大寫 `DRAFT` 而言】** 上開指令之 `grep` **區分大小寫**，故「ONT／ID／KS 為 0」係**大寫** `DRAFT` 之計數，**不涵蓋小寫 `v0.1-draft` 殘留**；以「DRAFT 為 0」概括該三份之草案殘留狀況將誤導讀者。**二數須並列**（產生指令與實測值，2026-07-17 親跑；本補充亦更正本輪 finding 之列舉——其漏列 WM）：
   > ```bash
   > grep -c "DRAFT" specs/*-SPECIFICATION.md        # 大寫：L5 9／L6 8（＝17）；ONT 0／ID 0／KS 0／WM 0
   > grep -c "v0\.1-draft" specs/*-SPECIFICATION.md  # 小寫：ID 67／KS 58／L5 5／L6 5／ONT 4／**WM 4**
   > ```
   > **小寫殘留之性質**：經核 ONT 4／L5 5／L6 5／WM 4 各行均為**正當引用**（`前版：v0.1-draft` 版本欄、`archive-path:` 歸檔路徑、author 欄之沿革），依 `RULING-2026-009` 主文三（三）**不得更動**；ID 67／KS 58 之中，`ID:55`／`ID:75`／`KS:67`／`KS:88` 即附錄丙第 2 項所指之**真矛盾**（位於標 [N] 之 §0 章內，待 Steward）。**本補充僅更正[I] 之敘述口徑，不據以更動任何 `specs/` 檔案。**
   * **⚠️ 更正兩位審查官之列舉**：本輪審查中，有審查官列為「L5:157、165、454、459／L6:226、473、478」、另有列為「L5:165、L5:157、L5:454–455／L6:226、L6:473–474」——**二者均不完整**。以上為本席以指令親自導出之窮盡清單。
5. **`ARCHITECTURE-OVERVIEW.md` 與 `README.md` 於本案執行場次被動，惟不在 RULING-2026-009 主文三之清單內**（違主文五「主文未明列之位置不得變更」、「不得順帶為之」）。**緩解事實（據實記載）**：二檔均為 **[I] 資訊性文件**，無規範效力，未變更任何義務、判準或條款，實質風險低。**處置**：不回退內容；**本案之 commit 應嚴格限縮為 8 個在範圍內檔案**（`specs/` 五份＋`constitution/RULING-2026-004-ID-ADOPTION.md`、`-005-KS-ADOPTION.md`＋`constitution/AMENDMENT-LOG.md`）＋新增 `constitution/RULING-2026-009-EXECUTION-REMEDIATION.md`；`ARCHITECTURE-OVERVIEW.md`、`README.md` 及其餘平行軌檔案（`CONSTITUTIONAL-ROLLOUT-PLAN.md`、`HANDOFF.md`、`audits/`、`tools/`）**另立 commit 歸屬平行文件軌**，於該軌自行說明依據。**若 Steward 認其同步確屬本案，須先以補充裁決納入主文三，不得以既成事實追認。**

### AL-2026-012 附錄丙——呈 Steward 待決事項（幕僚不得代決；`AUGUR-MC v1.3 §8.1`、RULING-2026-009 主文二（四）6）

1. **`ID:724`／`KS:994` 之定位（附錄甲第 3 點）**：該二行僅含上層版本標注、不含主文三（三）柱狀句所定之任一標的，其唯一 `v0.1-draft` 成分屬主文四（四）明定另案之類別——**是則主文三（三）之位置表，與 (i) 其自身之柱狀句、(ii) 主文四（四），三者相斥**。請 Steward 擇一：**(a)** 認定該二行屬主文四（四）之上層版本標注類，自主文三（三）位置表**刪除**（刪除線＋註記，比照 `AL-2026-003:33` 體例），並補記其自始不在範圍；或 **(b)** 認定其在範圍，**命補行執行**。
2. **`ID:55`／`KS:67`／`ID:75`／`KS:88` 之真空與新生矛盾（附錄乙第 1 點）**：其性質與主文（二）之 Annex CS `upper-specs` 同步**完全同構**（同為記述上層版本之非義務欄位，不涉 [N] 實質、不涉編號），惟位於 §0（標 [N]）章內。請 Steward 擇一：**(a)** 加速主文四（四）所定之另案裁決（「[N] 條款內之上層版本標注更新是否為 `§8.6` patch」），一併解消；或 **(b)** 作成補充 patch 級裁決，將該四行納入同步；或 **(c)** 明示於另案完成前，該四行之「v0.1-draft／草案」字樣為**已知未同步之過渡記述**，並依 `AL-2026-003:33` 體例加註，俾 `§8.2` 較嚴格解讀不致將 ID／KS 讀回未生效。**幕僚於裁決作成前不得自行更動——那將逾越主文四（四），屬紅線。**
3. **五份【地位】節之「變更僅限」清單校正（附錄乙第 2 點）**：請 Steward 以補充裁決，將該清單校正為各該裁決主文所**實授**之類別（ID／KS 依 `RULING-2026-004:22`／`-005:22` 之四類；ONT／L5／L6 依 RULING-2026-009 主文二（三）對「僅限」之解釋）。
4. **`L5:405`／`L6:417` 之 `### TR.Z` 章標及 L5／L6 其餘 `DRAFT` 殘留（附錄乙第 3、4 點）**：請 Steward 以補充 patch 級裁決，將其明列為主文三（三）同性質之記述性補正位置。**執行界線（如經命令）**：**TR.Z 之編號不得更動**；其枚舉範圍、缺列數、承接／細化／DEFER／不觸及之落點**一字不易**；**L6 之自我起草警示（T-L6-5）必須完整保留**；**L5 之 provisional／`§8.2` 延後不得因刪 DRAFT 而被讀為終局合憲**；緊張關係表各列之「非豁免事項」性質不得因刪 DRAFT 而變動。
5. **RULING-2026-009 主文二（三）之解釋歸屬（六、程序聲明之勘誤第 4 點）**：請 Steward 擇一：**(a)** 依 `RULING-2026-006:9` 體例，於程序聲明**逐字引錄**其就「範圍擴張至 ONT／L5／L6」及主文四各項不涵蓋所為指示之**原話與時點**；或 **(b)** 將主文二（三）**自本裁決析出**，另以 `§8.1` **解釋裁決**（具先例拘束力）由 Steward 本人作成後，本裁決援引之。
6. **五份 §0.1 之補記是否後綴指向性註記（主文四（一）之勘誤第 4 點）**：五份於現行 gate 全數 **FAIL**（ONT 1／ID 31／KS 34／L5 49／L6 37；L1 為唯一 PASS），故 §0.1 所載「生效要件已全部成就」中之 **linter 一項現處於已知失效狀態**；而主文四（一）將該事項保留、待 #22 另案。請 Steward 決定是否命於五份 §0.1 補記後綴一句（例：「其中『linter 結構關卡』一要件之證據基礎，依 RULING-2026-009 主文四（一）保留、待另案裁決；本補記不就其成否作成判斷。」），俾 §0.1 不被單方讀為終局。**幕僚不得自行為之**——該註記非主文三所命，且位於標 [N] 之 §0 章內。
7. ~~**工作區凍結與 commit 邊界（附錄乙第 5 點）**：請先**凍結工作區**（停止平行 agent 寫入，或改於獨立 worktree 執行），依附錄乙第 5 點分立 commit，並於該 commit 上**重跑附錄甲之查核**、登錄其 SHA，方為終局。**切勿於混雜工作區上簽署終局查核。**~~
   > **✅ 已了結（2026-07-17，幕僚據實補記，非代決）**：凍結與分軌**已達成**——在範圍內之 9 檔已單獨 commit 為 **`608adc2`**（與附錄乙第 5 點所命之範圍逐一相符），平行文件軌另立於 `65a7dd6`；附錄甲之查核已於 `608adc2` 上重跑、**36 行落點完全複現**，並已於附錄甲登錄該 SHA、標明終局。**本項所命者為程序行為（凍結、分立 commit、重跑、登錄 SHA），已全部履行，故了結；本了結不涉任何實質判斷，亦不觸及附錄丙其餘各項——彼等仍待 Steward。**

### AL-2026-012 附錄丁——本輪執行補正審查所為之 patch 級事實勘誤（幕僚逕行，治理附則第 2 條第 3 款）

下列各項為**純事實更正**，均以**刪除線＋註記、保留原文**為之，**不變更任何主文之操作性內容、不作成任何實質判斷**；Steward 得隨時以裁決調整：

* **RULING-2026-009 主文四（一）**：(i) 受影響裁決之列舉補列 **RULING-2026-003**（`003:27`／`003:37` 同以 linter PASS 為 ONT 生效要件；並記明 **ONT 之 PASS 已確知為零覆蓋**、非計數待定，其性質重於其餘四份）；(ii) 刪去「與本裁決主文二所命之 upper-specs 同步」一節——**經實測，upper-specs 同步對誤標數之影響為 0**（同一 gate，pristine `HEAD` vs 補正後：ONT 1／ID 31／KS 34／L5 49／L6 37，三項計數全同；逐檔全輸出 diff 之唯一差異為訊息內之版本字串），**使數字變動者僅為關卡硬化一項**。**本項之結論（#22 延後）不變**。
* **RULING-2026-009 主文四（四）**：KS 之「**44 行**」→「**42 行**」；並補明「正文區」之邊界定義（`## §1` 章標起至 `## Annex CS` 標題前一行止；ID 82–660、KS 118–934）與產生指令（`awk 'NR>=82 && NR<661' specs/IDENTITY-SPECIFICATION.md | grep -cE 'AUGUR-(ONT|ID) v0\.1-draft'` → **50**〔原載屬實、可重現〕；同法 KS `NR>=118 && NR<935` → **42**〔原載之 44 於任一有原則之邊界均不可重現〕；ONT／L5／L6 全檔 → **0／0／0**〔原載屬實〕）。**本項全體仍為另案，本勘誤不改變該保留。**
* **RULING-2026-009 六、程序聲明**：分工之如實記載（Steward 原話僅「以執行補正裁決一次處理」；主文二（三）之解釋構成、主文四（一）之類推論證、主文四（四) 三項理由、主文二（四）之界線構成，均由幕僚草擬、經 Steward 簽署整體採認）；並補記查證聲明之**三處自我勘誤**（預測未實測、KS 44 不可重現、漏列 003）。
* **`ARCHITECTURE-OVERVIEW.md`（[I] 導覽文件，編輯修正，無須裁決）**：L7 列之「規格自訂 L7.90(d) **六項**必審」為未經指令導出之手數字，經實測應為**七項**。產生指令：`sed -n '566,600p' specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md | grep -cE '^>\s+\((i|ii|iii|iv|v|vi|vii)\)'` → **7**。第 **(vii)** 項為「`AUGUR-L6 v1.0` L6.11 之 RT 級要件於 `AUGUR-KS v1.0` Annex CL.0 線性閉集上不可同時單調滿足之異常（T-L7-13）」，其自身載明**係依 `§8.1` 之書面裁決聲請**——最不宜被漏數者。**附帶查獲（另案）**：`specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md` 自身第 **942／1004／1134** 行亦仍作「六項必審」，與其 L7.90(d) 之 (i)–(vii) 相斥；此為 **L7 v0.1-draft 之內部不一致**，該規格未生效、且不在本案範圍，**不予變更**，併呈 Steward 於 L7 充任案處理。
  > **【勘誤，2026-07-17】本項自身漏列一行**：前版記「第 **942** 行與第 **1134** 行」二處，經以指令實測為**三處**——漏列者為 **:1004**（T-L7-7 緊張關係表列，該條目自陳「自我交易誘因於本層達到頂點」，最不宜殘留錯數）。產生指令：`grep -n '六項' specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md` → **942／1004／1134**（`grep -n '七項'` → 無命中）。**本附錄自陳「全部行號與數字均由本席以指令親自導出」，此項恰為例外——一句 `grep -n '六項'` 即得，卻係手數。**
  > **併勘誤（範圍陳述失準）**：本勘誤之落點**不止 `ARCHITECTURE-OVERVIEW.md` 一檔**。經全庫實測，於**生效現況敘述**中作「六項必審」者另有三處：`HANDOFF.md:139`（位於「等 Steward 裁決的三件事」表內）、`CONSTITUTIONAL-ROLLOUT-PLAN.md:61`、`constitution/adoption-drafts/README.md:29`（該檔並明令「裁決前請先讀上表所列文件」）——三者皆為 Steward 判斷 L7 `§8.2` 實質審查工作量之直接依據，依之逐項審查將**漏審第 (vii) 項**（其自身即為依 `§8.1` 之書面裁決聲請）。上開三處均為 [I] 文件，已於本日一併據實更正並附產生指令。**記之以為戒：真值早於本附錄即以指令導出並書面登錄，漏改非因不知，而是知而只改一半。**

## AL-2026-013

* **日期**：2026-07-18
* **事項**：Steward 裁決第 2026-010 號——#22 憲章誤標補正：(一) ONT Annex TR 標題層級正規化（L2 矩陣可讀化，真值出爐）；(二) 五份生效規格 Annex TR **155 筆標籤逐字更正**（標籤回歸上位原文；落點欄、條款編號、[N] 義務本文零變更）；(三) 落點疑義旗標零；(四) 驗收：六份生效本 gate 全 PASS（error 0）、綁定文件同步、selftest 全綠
* **程序依據**：憲章 §0.6(a)（上位原文為權威）、§8.6（patch 級編輯修正）、§8.2；治理附則第 2 條第 3 款；先例 RULING-2026-009
* **文件**：[RULING-2026-010-LABEL-REMEDIATION.md](RULING-2026-010-LABEL-REMEDIATION.md)（含執行記錄）
* **裁決人**：Constitution Steward（tsaitsangchi）；機械執行由授權幕僚為之（額度中斷後以確定性腳本續行，全程留痕）
* **效果**：#22 之生效規格部分結案；**L7 draft 48 筆亦於同日辦竣（見裁決 §五）——七份規格 gate 全 PASS，專案首次全綠**。殘餘＝L7 之 §8.2 實質審查／三鏡重審／充任（屬 Steward）＋CI merge-gate 接線（另裁）

## AL-2026-014

* **日期**：2026-07-18
* **事項**：Steward 裁決第 2026-011 號——**Layer 7 規格充任認定（AUGUR-L7 v1.0，provisional）**：形式關卡充任＋`§8.2` 深度實質審查誠實保留列管（七項必審、期限 2026-10-14，比照 RULING-2026-006 先例）；併案三項 `§8.1` 解釋裁決（T-L7-13 取較嚴交集／未裁決 Conflict 推定致命之保守預設維持／matrix_missing＝WM.44 覆蓋缺口集合）；**達成里程碑 M2（L0–L7 全棧治權骨幹貫通）**
* **程序依據**：`§0.5`、`§8.1`、`§8.6`；三鏡重審全數 go＋203 筆對抗全查結案（audits/L7-REREVIEW-2026-07-18.md）
* **文件**：[RULING-2026-011-L7-ADOPTION.md](RULING-2026-011-L7-ADOPTION.md)；生效本 `specs/INFRASTRUCTURE-SPECIFICATION.md`（draft 歸檔）
* **裁決人**：Constitution Steward（tsaitsangchi）
* **效果**：八層全棧生效（L0–L7）；corpus 7 生效本／0 draft；CI 接線與 Bearer Registry 補齊列為充任後首批

## AL-2026-015

* **日期**：2026-07-18
* **事項**：Steward 裁決第 2026-012 號——**CODE-MIGRATION-PLAN 採認生效（v1.0）**＋五決策點逐點處置（節奏採建議／Phase 1 兩點結案登錄／升裁決 C＝authorization_ref NOT NULL 嚴格面／原則精華 #7 方向採認排 Phase 7／**CI merge-gate 即日解鎖**）；併案登錄**備份第二目的地決策之取消**（殘餘風險經 Steward 知悉並接受，非缺口消滅）
* **文件**：[RULING-2026-012-MIGRATION-PLAN-ADOPTION.md](RULING-2026-012-MIGRATION-PLAN-ADOPTION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）

## AL-2026-016

* **日期**：2026-07-18
* **事項**：Steward 裁決第 2026-013 號——**`§D24` 之 L6 側承接補正（minor，AUGUR-L6 v1.0→v1.1）**：L6.15 增補「授權受限資料之用途邊界」款（承 D24 隔離強制面；判準同步）；Annex TR 概括列拆分（D24 改列承接：RBAC 面＝L6.15＋L6.6、物理面下放 L7）；**WM Annex D 目標含 L6 之其餘六列（D13/15/16/17/22/28）同型疑義登錄旗標**，提請 Steward 另案逐列裁決
* **文件**：[RULING-2026-013-D24-L6-REMEDIATION.md](RULING-2026-013-D24-L6-REMEDIATION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：L6 gate PASS（error 0）；全 corpus 7/7 PASS；版本引用零漣漪（minor 之向後相容，`§8.6`）

## AL-2026-017

* **日期**：2026-07-18
* **事項**：Steward 裁決第 2026-014 號——**ONT.20 判準操作化採認＋`entity_type_catalog.identity_criteria` 補欄**：T.1 Security／T.2 Index／FredSeries 三判準採認（ID.20）、Automobile 守衛列確認；四列判準文字沙盒→生產寫入；**ONT.20 首次機器可判**（無判準列=0 為閘）；Phase 2 卷宗裁②結案（路線 a）
* **文件**：[RULING-2026-014-ONT20-CRITERIA.md](RULING-2026-014-ONT20-CRITERIA.md)
* **裁決人**：Constitution Steward（tsaitsangchi）

## AL-2026-018

* **日期**：2026-07-18
* **事項**：Steward 裁決第 2026-015 號——**Phase 2 分支准併**（merge 4c6d3b6、27/27 綠）＋裁①（advisory lock 接線前置＋backfill 單實例）＋裁③（生產順序：retire backfill 先行→存量鑄造→屬性同步；預期 ~235 provisional 為憲章正確樣貌）＋**P5 一次拍板制**（補件審畢後單一核准涵蓋全順序）＋七 minors 併補件分支
* **文件**：[RULING-2026-015-PHASE2-MERGE.md](RULING-2026-015-PHASE2-MERGE.md)
* **裁決人**：Constitution Steward（tsaitsangchi）

## AL-2026-019

* **日期**：2026-07-18
* **事項**：Steward 裁決第 2026-016 號——**WM Annex D 六列旗標一次處置**：D16 TR 逐列化；D13（Planning 四物件定義＋P3.E1 引用紀律）／D15（fail-safe 判定主體釘定）／D17（自然人法規對應表 L6 本體）／D22（核心宇宙判準三機制）／D28（誠實輸出契約四驗證）五列實質承接補正。**AUGUR-L6 v1.1→v1.2、AUGUR-KS v1.0→v1.1（minor）、AUGUR-L5 TR patch 更正**；三層循環空指與「code 先行規格未書」反向缺口關閉
* **文件**：[RULING-2026-016-ANNEXD-SIX-ROWS.md](RULING-2026-016-ANNEXD-SIX-ROWS.md)＋附件 ops/ANNEXD-SIX-ROWS-CASE-2026-07-18.md
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：三檔 gate 逐一 PASS、全 corpus 7/7、selftest 全綠。**獨立對抗核驗因額度中斷未完成**；建造者機械自查更正五處版本一致性缺陷（KS/L6 文末版本、KDI 盤點、二處時代錯置引用），詳裁決事後更正記錄；深度語義核驗待額度恢復補行

## AL-2026-020

* **日期**：2026-07-18
* **事項**：Steward 裁決第 2026-017 號——**AUGUR-MC 首次三鏡對抗審查 findings 處置（MC v1.3→v1.4，minor）**：**八項 §8.1 解釋**（M1 修訂自鎖之合法解鎖〔維持原則級門檻、釋明判準〕／M2 共享憑證歸責／單一 Steward 雙人核准過渡／§0.3 母集〔子項受保護不入 102、§5.{n} 入〕／工具輸出保真／時序措辭／provisional 二義／P1.E3 主責 L6）＋MC [I] 補正（§0.5 充任補登＋跨層例外、§0.2／§2.6）＋治理附則第 3 條繼任人恆存（annex minor）。**§8／構成性依據之 [N] 本文一律未動**（原則級 self-entrenchment，非 minor）——初次越權（§8.6/§0.3/附則對映當 minor）經獨立核驗糾正、全數 revert；P5.W4 認定已由 §8.3 兜底、非解釋項
* **文件**：[RULING-2026-017-MC-REVIEW-DISPOSITION.md](RULING-2026-017-MC-REVIEW-DISPOSITION.md)＋findings 冊 audits/MC-THREE-MIRROR-REVIEW-2026-07-18.md
* **裁決人**：Constitution Steward（tsaitsangchi）
* **要旨**：**零原則級變更、PA 與五原則本文零改**；L0 首次對抗審查閉環。MC 102 母集完好、全 corpus 7/7 PASS、selftest 綠。本批補正之獨立核驗待補

## AL-2026-021

* **日期**：2026-07-18
* **事項**：Steward 裁決第 2026-018 號——**AUGUR-WM v1.0（L1）首次三鏡對抗審查 findings 處置（§8.6 patch）**：處置一＝**全艦引用版號齊一 v1.4**（L1 195 行／228 處 v1.2＋L2–L7 495 行 v1.3→v1.4，含各 mc-version 與 L1 §0.3 凍結 MUST 根治）；處置二＝C.10 §8.1 雙歸類更正（改 carries WM.47/48）；處置三＝WM.38/34 條頭具名目標層
* **文件**：[RULING-2026-018-L1-REVIEW-DISPOSITION.md](RULING-2026-018-L1-REVIEW-DISPOSITION.md)＋findings 冊 audits/WM-THREE-MIRROR-REVIEW-2026-07-18.md
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：七份 gate 全 PASS、selftest 全綠（版本落差鎖改合成落差）；L1 首審閉環
* **【勘誤，2026-07-18，獨立核驗（第十一度定律）】**:本項原記「L1 223 處」——223 係批替腳本殘餘計數、非全量，實為 195 行／228 處（已更正如上）；L2–L7 各數與 495 之度量為行數。獨立核驗結論：批替零誤傷、七 gate 綠、102、mc-version 齊一——RULING-2026-018 施作經核驗成立

## AL-2026-022

* **日期**：2026-07-19
* **事項**：Steward 裁決第 2026-019 號——**L2–L6 首次三鏡對抗審查 findings 四決策處置**：①（乙 patch）L3/L4 矩陣完備性補列 TR.Y（L3 15／L4 9 列）；②L5 撤回形式充分性認定＋§8.1 橋接（provisional·充任暫停、硬期限 2026-10-14、M2 保全）；③層間 v0.1-draft 引用全艦→v1.0（115 處）；④第二輪定向補審排程（首要＝§8.3 matrix-coverage 機器檢查）
* **文件**：[RULING-2026-019-L2-L6-REVIEW-DISPOSITION.md](RULING-2026-019-L2-L6-REVIEW-DISPOSITION.md)＋五份 findings 冊 audits/*-THREE-MIRROR-REVIEW-2026-07-18.md
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：七份 gate 全 PASS、selftest 全綠、PA/五原則 byte 零改、M2 保全；本批獨立核驗待補
* **處置完整性糾正（2026-07-19 獨立核驗，第 12 度定律）**：四決策遺漏 L6 之 2 存活 major（M1 defers-in 未宣告 7 掛鉤／M2 L6.21→L7 幽靈下放），carried RULING-2026-020 待裁；另修裁決 2 處草案語態、IDENTITY/KS 失效散文、count 115行/140處
* **意義**：八層首審全部完成（L0–L7 各受首次對抗審查）。定律至第 12 度，12/12 皆獨立審查捕獲、建造者自查零攔截

## AL-2026-023

* **日期**：2026-07-19
* **事項**：Steward 裁決第 2026-021 號——**L2（AUGUR-ONT）矩陣形式完備性補正**（執行 RULING-2026-019 決策一之已立 patch 原則於窮舉新浮現之 L2 缺口）：TR.2 補 A.0（承接）＋WM Annex C／E／D非L2（不觸及）4 群；CS.10 [N] 狀態陳述誠實更正。三鏡曾誤判 CS.10 major「雙反駁出局」，經窮舉（wf_d8a73802）證為真——定律第 13 度、首見對抗審查自身失手由更深窮舉接住
* **文件**：[RULING-2026-021-L2-MATRIX-COMPLETENESS.md](RULING-2026-021-L2-MATRIX-COMPLETENESS.md)
* **裁決人**：Constitution Steward（tsaitsangchi，2026-07-19 逐步完成指示）
* **驗證**：gate PASS、selftest 綠（tr_rows_L2 56→59）；G5 複驗待補、蓋章前置

## AL-2026-024

* **日期**：2026-07-19
* **事項**：Steward 裁決第 2026-020 號——**L6（AGENT-RUNTIME）之 2 存活 major 處置**（補 RULING-2026-019 之沉默漏列）：M1＝defers-in 補宣告 7 條 WM.D 直達掛鉤（宣告完備性 patch）；M2（甲案）＝收窄 L6.21→L7 幽靈下放（揭露載體留 L7.43、DB 物理強制俟 L7 §8.2）
* **文件**：[RULING-2026-020-L6-DISPOSITION.md](RULING-2026-020-L6-DISPOSITION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：gate PASS、selftest 綠；L6 待 G5 蓋章

## AL-2026-025

* **日期**：2026-07-19
* **事項**：Steward 裁決第 2026-022 號——**概念層 L1–4 交互檢查 4 cross-layer major 處置（整合完整）**：M1＝WM.28 hook 補 §P5.W4（最小權限之 WM 落點→L6）；M2/M3＝以 WM Annex D 權威表逐列重編 KS/ID 之 D 處置表（棄廢棄舊編號）；M4＝KS D19 改承接（L4 slice）＋CS.2 收斂揭露
* **文件**：[RULING-2026-022-CONCEPT-TIER-CROSS-LAYER.md](RULING-2026-022-CONCEPT-TIER-CROSS-LAYER.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：WM/ID/KS 觸及後 gate PASS、selftest 綠、封印未破；ultracode 交互檢查 wf_7d822c3c＋重編 wf_e732832b（複核糾正 D19）

## AL-2026-026

* **日期**：2026-07-19
* **事項**：Steward 裁決第 2026-023 號——**L5（AUGUR-Cognitive Kernel）重採認（乙：回 provisional）**：形式充分性經 RULING-2026-019 決策二重作（TR.F 補 KS 16 區塊＋WM D1-6＋L5.10 as-of 條款＋版本 v1.1）回復；L5 自 provisional·充任暫停回復 v1.0 provisional 充任；§8.1 橋接（RULING-2026-019）收束；§8.2 實質審查延後（比照 L7）
* **文件**：[RULING-2026-023-L5-READOPTION.md](RULING-2026-023-L5-READOPTION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：四輪 G5 複驗＋全 corpus as-of 一致（L5.10）；gate PASS、selftest 綠、PA/五原則 byte 零改；L5.10 施作歷四輪、每輪獨立審查捕獲建造者殘留（定律又應驗）

## AL-2026-027

* **日期**：2026-07-19
* **事項**：Steward 裁決第 2026-024 號——**T-L7-13 之 §8.1 書面裁決（L7 §8.2 (vii)）**：L6.11 RT 級要件於 KS CL.0 線性閉集上之序異常，經 §8.1 解釋為「多軸解耦」（E 階/可重現驗證/獨立 Data Evidence 為不同要件軸，CL.0 僅 E 階軸；可重現驗證為跨 E 階獨立綁定）→ 取交集為 L6.11 之忠實承接（續 RULING-2026-011 主文三(a)）；致命 Conflict 分級判準登錄前保守預設維持
* **文件**：[RULING-2026-024-T-L7-13.md](RULING-2026-024-T-L7-13.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：不改任一 [N] 本文（釐定併用解釋）；L7 之 T-L7-13 三處狀態標記更新為「§8.1 已裁」；gate PASS、selftest 綠。L7 §8.2 七項之 (vii) 結清，餘六項

## AL-2026-028

* **日期**：2026-07-19
* **事項**：Steward 裁決第 2026-025 號——**L7（AUGUR-Infrastructure）§8.2 實質審查條件通過、provisional 轉 v1.0**：七項必審裁定——(i)(ii)(v) 核定照收（H_max/Threshold/反自我交易）；(iii)(iv)(vi) 單節點/單人殘餘接受為 residual、分階段①→②③補正、復審 2026-10-14；(vii) §8.1 已裁（RULING-2026-024）。L7 自 provisional 轉 **v1.0 生效**
* **文件**：[RULING-2026-025-L7-8.2-DISPOSITION.md](RULING-2026-025-L7-8.2-DISPOSITION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：L7 全檔 §8.2 狀態標記→條件通過（【地位】/L7.90(c)/TR.Z/尾註/生效要件）；MC §0.5 同步（[I]）；gate PASS、selftest 綠、PA/五原則 byte 零改
* **里程碑**：**八層 L0–L7 全數蓋章（8/8）**。執行層收口完成。觸發 Phase 3b（執行層 ultracode 交互檢查）

## AL-2026-029

* **日期**：2026-07-23
* **事項**：Steward 裁決第 2026-026 號——**Agent 協作產物之個別可驗證性（執行指令矩陣）**：§8.1 解釋將 `§8.3` ENFORCE／機器可稽核於 Layer 6 落點讀為——可執行 Python 入口 docstring 必須載 canonical「執行指令矩陣」；細則 CLAUDE.md #18/#29。MC §0.5 Layer 6 列 editorial 同步引用本裁決。**§8 [N] 本文未動、MC 版本維持 v1.4、102 母集不變**
* **文件**：[RULING-2026-026-CMD-MATRIX.md](RULING-2026-026-CMD-MATRIX.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **執行**：repo 可執行入口 docstring 補齊「執行指令矩陣」；CLAUDE.md 從屬改引 AUGUR-MC v1.4

## AL-2026-030

* **日期**：2026-07-23
* **事項**：Steward 裁決第 2026-027 號——**執行層 L5–7 交互檢查 2 cross-layer major 處置（簿記／編號地圖）**：M-IX-1＝KS Annex CS front-matter `defers-in` 補列 `WM.D22`（KDI.0 三向可解析補正，KDI.18/KS.80/KS.81(f)/CS.3(a) 義務句本文未動）；M-IX-2＝L5 編號穩定性（§0.3、文末總計）改為「L5.10 已啟用（as-of 推理消費）；L5.11–L5.89 保留」，使編號地圖與已生效 L5.10 [N] 條款一致
* **文件**：[RULING-2026-027-L5-L7-INTERACTION-DISPOSITION.md](RULING-2026-027-L5-L7-INTERACTION-DISPOSITION.md)
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：`python3 -m tools.constitution_lint report` 施作前後 error 0／warning 0 逐檔一致（L1–L7 PASS）；2 存活 major 判定要件（KDI.0 三向、L5 編號地圖一致性）經補正消除；不動任一 [N] 義務句本文

## AL-2026-032

* **日期**：2026-07-23
* **事項**：Steward 裁決第 2026-029 號——**L5（AUGUR-Cognitive Kernel）§8.2 實質審查條件通過、provisional 轉 v1.0**：八項必審裁定（2026-07-23 一攬子採納審查包建議核示）——(i) L5.1 合法推理定義／(ii) L5.2 雙合法終點／(iii) L5.3 meet 上限傳播／(iv) L5.4 Hypothesis 可謬／(vi) L5.7 model 非世界權威**核定照收**；(vii) CS.2 六緊張**核定＋T-L5-6 定性追認**（「推論產生歸 L5、結果 claim 之信度／欄位歸 L4」——RULING-2026-006「一併裁定」項至此裁定）；(v) L5.6 per-結論解釋、(viii) L5.10 as-of 推理消費**條件通過**（條件＝L5 單層 ultracode PRV／ASF 複核於 2026-10-14 前執行、翻 major 另依 §8.2 辦；F-IX-4／F-IX-6 簿記另案 minor）。L5 自 provisional 轉 **v1.0 生效**；復審期限 2026-10-14（與 L7 residual 同日併結）
* **編號註記**：本案跳號登錄——**AL-2026-031 保留予 RULING-2026-028**（GOV-1/GOV-3 之 §8.1 解釋止血裁決，另一路徑作業中、由該案自行登錄）；本案裁決號原候選 028 同因避讓改編 029
* **文件**：[RULING-2026-029-L5-8.2-DISPOSITION.md](RULING-2026-029-L5-8.2-DISPOSITION.md)；審查包 audits/L5-8.2-REVIEW-PACKAGE-20260723.md
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：L5 全檔 §8.2 狀態標記→條件通過（【地位】/§0.1/TR.Z/Annex CS 地位提示/尾註）；T-L5-6「待裁」三處→已裁（追認）；MC §0.5 同步（[I]）；gate PASS、PA/五原則 byte 零改
* **里程碑**：**八層 §8.2 全數結清**（L5 條件通過＋L7 條件通過＋餘六層已結）——「8/8 ≠ §8.2 一致結清」不對稱解消

## AL-2026-033

* **日期**：2026-07-23
* **事項**：Steward 裁決第 2026-030 號——**L1（AUGUR-WM v1.0）單層 ultracode findings 一攬子處置**：§8.1 解釋二項（A.38 部位定性甲案；Annex D 範圍型目標承接規則）＋§8.3 過渡規則 (b) **補正期裁定作成**（WM.35／WM.36 到期日＝2026-10-14，自翌日 WM.36 直綁消費禁令無條件適用）＋minor／patch 簿記／editorial（KS FM 補 D14/D15/D19/D23；L5 FM 補 D12/D13/D22/D28＋TR 旗標收束；L6 TR 析出 D19/D23/D25；C.8 T-5／A.54／ID T-ID-3 同步 RULING-2026-014；Annex F 歸類；WM.40 archive-path 括注；D0 slice 登錄義務＋linter 議程；A.16 D25 範圍統一）。**分級登錄**：一攬子簽核未另圈定 → 採較嚴 **major**（F-L1-4、F-L1-6）；**處置不變**。**WM [N] 義務句本文零改、版本維持 v1.0、MC／PA 零觸**
* **文件**：[RULING-2026-030-L1-WM-ULTRACODE-DISPOSITION.md](RULING-2026-030-L1-WM-ULTRACODE-DISPOSITION.md)；findings `audits/L1-WM-ULTRACODE-20260723.md`
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 一攬子簽核
* **驗證**：`python3 -m tools.constitution_lint report` PASS 7／7（2026-07-23 獨立對抗核驗親跑）；RULING-2026-030 第九節八項全 ✅（2026-07-23；核驗者＝Cursor 獨立核驗 agent；非施作者）
* **定案**：Steward 2026-07-23 **接受 030**

## AL-2026-031

* **日期**：2026-07-23
* **事項**：Steward 裁決第 2026-028 號——**治理元層二缺口（GOV-1／GOV-3）之過渡處置（§8.1 解釋二項）**：第 1 點〔解釋界線·過渡〕＝§8.5(d) 反擴張標準準用於一切 §8.1 解釋，效果該當「課新義務類型／解鎖／移除制衡」者視為修訂、依 §8.5 辦理，疑義採「屬修訂」保守解讀，先例推翻須明示＋附理由＋逐點回應；第 2 點〔參與判準〕＝「參與」＝實質判斷之作成、繕打／機械施作／依核示落地＝非參與，以行為態樣繫屬繞開 §2.8 射程浮動；第 3 點〔施作留痕＋獨立核驗常態化〕＝RULING-2026-017 §四慣行升格裁決義務。**§8 [N] 本文未動、非原則級修訂、102 母集不變、PA 零觸**；第 1 點載明效力上限（無法自我封口）＋日落句（原則級修訂生效日由 [N] 吸收）。同步：GOV-1 原則級修訂提案（順帶收 GOV-4 公示期錨定、落點 §8.1）入 14 日公示（2026-07-23 起算、期滿 2026-08-06），見 `amendments/PROPOSAL-2026-001-GOV1-GOV4-S8.md`
* **文件**：[RULING-2026-028-GOV-INTERPRETATION-BOUNDS.md](RULING-2026-028-GOV-INTERPRETATION-BOUNDS.md)
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 書面核示「採推薦組合」
* **驗證**：不改任一 [N] 本文；gate PASS、selftest 綠、PA/五原則 byte 零改；編號避讓＝L5 §8.2 收口草稿同日改編 RULING-2026-029（候選 AL-2026-032）

## AL-2026-034

* **日期**：2026-07-23
* **事項**：Steward 裁決第 2026-031 號——**甲案：廢止治理附則第 2 條第 1 款強制公示要件＋確認 PROPOSAL-2026-001 撤回 GOV-4**（治理附則 minor 修訂）：Steward 為單一自然人（Sole Steward）期間，原則級修訂**不強制公示期**、Steward 書面裁決（附理由、公開存檔）議決即生效；公示改為任意（若舉行，異議逐項回應義務照舊）；憲章 §8.5(b) 二要件照常適用。GOV-4 **反向閉合**——不錨 [N]、廢止附則強制公示，findings 留檔不滅、不再列開放待辦。PROPOSAL-2026-001 自此不受 14 日公示（原期滿 2026-08-06）約束，待 Steward 依 §8.5(b) 正式議決即可生效（本裁決不構成該議決）。**MC [N] 本文零改、版本維持 v1.4、102 母集不變、PA 零觸**；誠實揭露＝本路徑即 GOV-4 所指棘輪結構之 Steward 明示正面行使（非規避）
* **編號註記**：本案跳號登錄——**AL-2026-033 保留予 RULING-2026-030**（L1 WM ultracode 處置草案，待 Steward 簽核、由該案自行登錄）；本案裁決號同因避讓編 031
* **程序依據**：治理附則第 2 條第 2 款（minor）＋附則位階句「本附則之修訂依 minor 門檻」；Steward 書面指示 2026-07-23「甲：拿掉錨定／廢止公示」
* **文件**：[RULING-2026-031-ANNEX-NOTICE-REPEAL.md](RULING-2026-031-ANNEX-NOTICE-REPEAL.md)；選項矩陣 `reports/augur_steward_no_public_notice_directive_20260723.md`
* **裁決人**：Constitution Steward（tsaitsangchi）
* **驗證**：lint 前後逐檔一致；PA／五原則 byte 零改；施作留痕依 RULING-2026-028 第 3 點，commit 前經獨立對抗核驗

## AL-2026-035

* **日期**：2026-07-23
* **事項**：Steward **正式議決通過**原則級修訂提案 PROPOSAL-2026-001（範圍僅 GOV-1／修訂一）——**AUGUR-MC v1.4→v1.5（原則級）**：§8.1 增設「**解釋之界線**」段（反擴張標準一般化＋效果等同修訂之三款判準＋疑義保守解讀＋先例推翻要件；GOV-1 根治）。依 §8.5(b) 二要件（失效 Evidence：`audits/MC-ULTRACODE-L0-20260723.md` GOV-1 卷＋RULING-017 M1／RULING-026 實例；實質判準：更完整實現 Accountability 於治理權力自身）。**RULING-2026-028 第 1 點〔解釋界線·過渡〕於生效日由 [N] 本文吸收日落**；第 2、3 點持續有效。102 母集不變；PA／五原則本文零改；L1–L7 規格零衝擊
* **程序依據**：§8.5(b) 原則級門檻（二要件）；治理附則第 2 條第 1 款（議決即生效、不強制公示——RULING-2026-031）
* **文件**：[PROPOSAL-2026-001-GOV1-GOV4-S8.md](amendments/PROPOSAL-2026-001-GOV1-GOV4-S8.md)（修訂理由書）
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 正式議決通過
* **驗證**：`python3 -m tools.constitution_lint report` 施作前後 PASS；PA／五原則 byte 零改；施作留痕依 RULING-2026-028 第 3 點——**commit 前待獨立對抗核驗**（非施作者本身）

## AL-2026-036

* **日期**：2026-07-23
* **事項**：Steward 裁決第 2026-032 號——**L2（AUGUR-ONT v1.0）單層 ultracode findings 一攬子處置**：F-L2-1 甲案（T.28 矛盾句統一措辭＋CS.8 增 OT-5 揭露，不改 parent）＋F-L2-2／3（TR.2 WM.53 析出改標、Annex A 區塊分列）＋F-L2-4（T.6 判準補外部識別碼體系×代碼值×有效期間，minor）。**分級登錄**：F-L2-1＝medium；F-L2-2／3／4＝minor；**零 major**。**蓋章不動搖**。**ONT 版本維持 v1.0、MC／PA 零觸**
* **文件**：[RULING-2026-032-L2-ONT-ULTRACODE-DISPOSITION.md](RULING-2026-032-L2-ONT-ULTRACODE-DISPOSITION.md)；findings `audits/L2-ONT-ULTRACODE-20260723.md`
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 一攬子簽核
* **驗證**：`python3 -m tools.constitution_lint report` PASS 7／7（2026-07-23 獨立核驗親跑）；RULING-2026-032 第七節八項全 ✅（2026-07-23 **獨立對抗核驗 PASS**；非施作者 a8a425f5）
* **定案**：Steward 2026-07-23 **接受 032**

## AL-2026-037

* **日期**：2026-07-23
* **事項**：Steward 裁決第 2026-033 號——**L3（AUGUR-ID v1.0）單層 ultracode findings 一攬子處置**：F-L3-1（AO.2／T-ID-3 部分解消同步、Issuer T.20 不另採認、per-Type 判準）＋F-L3-2 **乙案**（ID.50 刪第二 conjunct、已解析＝採認生效且非 ID.21 provisional、CS.1-P2 對齊）＋F-L3-3–7（ID.40 判準擴覆、§0.1 刪草案、TR.Y §2.8、TR.B P5 理由欄、TR.C D4/D6/D8 補全）。**分級登錄**：F-L3-1／2＝medium；F-L3-3–7＝minor；**零 major**。**蓋章不動搖**。**ID 版本維持 v1.0、MC／PA 零觸**
* **文件**：[RULING-2026-033-L3-ID-ULTRACODE-DISPOSITION.md](RULING-2026-033-L3-ID-ULTRACODE-DISPOSITION.md)；findings `audits/L3-ID-ULTRACODE-20260723.md`
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 一攬子簽核
* **驗證**：`python3 -m tools.constitution_lint report` PASS 7／7（2026-07-23 獨立核驗親跑）；RULING-2026-033 第十一節十項全 ✅（2026-07-23 **獨立對抗核驗 PASS**；非施作者 ab53539）
* **定案**：Steward 2026-07-23 **接受 033**

## AL-2026-038

* **日期**：2026-07-23
* **事項**：Steward 裁決第 2026-034 號——**L4（AUGUR-KS v1.1）單層 ultracode findings 一攬子處置**：F-L4-1（KS.23 同步 ID.50 033 乙案）＋F-L4-2 **甲案**（KS.34 推理規則 Confidence 缺省 STRONG＋EO.1）＋F-L4-3（KS.83(i) ID.51 納入語義具體化）＋F-L4-4–8（EV.2 序記法、KS.9 表補列、TR.C D4/D6/D8、TR.Y inline、KS.51 原子序）。**分級登錄**：F-L4-1／2／3＝medium；F-L4-4–8＝minor；**零 major**。**T-KS-6 維持 open-tension**。**蓋章不動搖**。**KS 版本維持 v1.1、MC／PA 零觸**
* **文件**：[RULING-2026-034-L4-KS-ULTRACODE-DISPOSITION.md](RULING-2026-034-L4-KS-ULTRACODE-DISPOSITION.md)；findings `audits/L4-KS-ULTRACODE-20260723.md`
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 一攬子簽核
* **驗證**：`python3 -m tools.constitution_lint report` PASS 7／7（2026-07-23 獨立核驗親跑）；RULING-2026-034 第十二節十二項全 ✅（2026-07-23 **獨立對抗核驗 PASS**；非施作者 3793c37）
* **定案**：Steward 2026-07-23 **接受 034**

## AL-2026-039

* **日期**：2026-07-23
* **事項**：Steward 裁決第 2026-035 號——**L5（AUGUR-CK v1.0）單層 ultracode findings 一攬子處置**：F-L5-1（EO.1 收 L5.10 三翼 as-of 謂詞）＋F-L5-6（L5.6(iii) Computational 路徑最低滿足）＋F-L5-2–5（LDI.6／TR.B／CS.3 enumeration、L5.90／CS.2 DRAFT 殘留、TR.F 歷史語）。**分級登錄**：F-L5-1／6＝medium；F-L5-2–5＝minor；**零 major**。**029 PRV／ASF 程序性閉合**（未翻 major、不重開 §8.2）。**F-IX-4／F-IX-6 仍另案 minor**。**蓋章不動搖**。**CK 版本維持 v1.0、MC／PA 零觸**
* **文件**：[RULING-2026-035-L5-CK-ULTRACODE-DISPOSITION.md](RULING-2026-035-L5-CK-ULTRACODE-DISPOSITION.md)；findings `audits/L5-CK-ULTRACODE-20260723.md`
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 一攬子簽核
* **驗證**：`python3 -m tools.constitution_lint report` PASS 7／7（2026-07-23 獨立核驗親跑）；RULING-2026-035 第十一節十二項全 ✅（2026-07-23 **獨立對抗核驗 PASS**；非施作者 15f3ef1）
* **定案**：Steward 2026-07-23 **接受 L5 ultracode 呈核、同案 035**

## AL-2026-040

* **日期**：2026-07-23
* **事項**：Steward 裁決第 2026-036 號——**L6（AUGUR-AR v1.2）單層 ultracode findings 一攬子處置**：F-L6-1（EO.1 收 016 四謂詞）＋F-L6-2（v1.2 版本锚点同步）＋F-L6-3–6（TR.Z／CS.2 DRAFT 殘留、TR.D D28 020 M2 語、【地位】升版史實）。**分級登錄**：F-L6-1／2＝medium；F-L6-3–6＝minor；**零 major**。**T-L6-5 維持 007 residual open-tension**（不關閉、不翻 major）。**蓋章不動搖**。**AR 版本維持 v1.2、MC／PA 零觸**
* **文件**：[RULING-2026-036-L6-AR-ULTRACODE-DISPOSITION.md](RULING-2026-036-L6-AR-ULTRACODE-DISPOSITION.md)；findings `audits/L6-AR-ULTRACODE-20260723.md`
* **裁決人**：Constitution Steward（tsaitsangchi）——2026-07-23 一攬子簽核
* **驗證**：`python3 -m tools.constitution_lint report` PASS 7／7（施作者親跑）；RULING-2026-036 第十一節**待獨立核驗**（028 §3 另輪）
* **定案**：Steward 2026-07-23 **接受 L6 ultracode 呈核、同案 036**

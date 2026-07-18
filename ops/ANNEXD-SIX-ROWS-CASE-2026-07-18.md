# WM Annex D 六列旗標——逐列查證結果與修正案全文 [I]（RULING-2026-016 之附件）

* **日期**：2026-07-18｜**查證**：12 代理（六查證官 xhigh＋六反駁官——反駁全數失敗，六列判定全數存活）
* **總判定**：D16＝doc_fix（五子項全覆蓋，純 TR 逐列化）；D13／D15／D17／D22／D28＝substantive_gap（15 子項 gap／7 covered／1 legitimately_out）
* **模式發現**：D22／D28 之義務活在 code（core_gate／advisor）而概念層無落點——實作先行於規格之反向缺口


---

## D13：Goal、Constraint、Capability、Plan 之定義（目標 L5–L6；WM 掛鉤 WM.21(d) 兜底；MC 錨 §P3.E1）

**disposition：substantive_gap｜反駁：未被反駁**

| 子項 | 判定 | 落點/證據要旨 |
|---|---|---|
| Goal 之定義（語義＋已解析 Identity 引用紀律） | gap | L5：無任何條款；L6：無任何條款（最近似素材：L6.1(5)/L6.4 Expected Effect，惟其為 per-Action 欄位，非 Goal 物件） |
| Constraint 之定義（語義＋已解析 Identity 引用紀律） | gap | L5：無；L6：無（近似機制散見 L6.6(a) scope／風險級上限、L6.15 用途邊界、L6.10–L6.13 門檻，均未以 Constraint 物件定義） |
| Capability 之定義（語義＋已解析 Identity 引用紀律） | gap | L5：無；L6：無定義條款（在場代號均內容不相稱：L6.16 Oversight Capability Vector＝人類監督能力度量；LDO.2 capability token＝L7 物理機制名。實質近親：L6.15 |
| Plan 之定義（語義＋已解析 Identity 引用紀律） | gap | L6 部分實質落點：§0.4（Plan 列為規範術語）、L6.6(d)（委派繫結 Plan 參照）、L6.8（Plan 為否決／暫停單位）、L6.15（Plan-scoped 權限、權限集合可由 Plan 之已授權 Ac |

### 修正案文字（草案，待裁）

【L6 minor 升版；比照 RULING-2026-013 之 D24 體例：既有條款增補款，不另立新條。宿主條款：L6.19（Planning→Execution→Feedback 迴路）——四物件均屬 Planning 側，EV.8 之唯一正文落點】

一、L6.19 條文末（義務主體行前）增補一款：

「**Planning 側結構化物件之定義與 Identity 引用紀律（承 `AUGUR-WM v1.0` Annex D D13、`AUGUR-MC v1.3 §P3.E1`；2026-07-18 RULING-2026-0XX 增補）**：本層行使 `§P3.E1` 下放 Layer 5–6 之定義權（Reasoning 側之引用兜底屬 Layer 5：`AUGUR-L5 v1.0` L5.1、L5.6）。(i) **Plan**：意圖進入 EV.8 Planning 之經授權結構化物件，繫結其 Goal、Constraint、所需 Capability 與已授權 Action 集合，為授權委派繫結（L6.6(d)）、權限範圍化（L6.15）、否決／暫停／中止（L6.8）與熔斷（L6.20）之作用單位。(ii) **Goal**：Plan 所宣告之意圖世界狀態；其 referent 為所繫結 Identity 之可能狀態，屬模態內容（`AUGUR-WM v1.0 §WM.17`），**必須**攜顯式模態標記，**不得**充當世界事實。(iii) **Constraint**：Plan 所載對其 Action 集合之顯式限制（含 L6.6(a) scope 與風險級上限、L6.15 之用途邊界）；本層風險分級與門檻（L6.10–L6.13）為一切 Constraint 之不可低於之下限，Plan **不得**載入弱於其之限制。(iv) **Capability**：Agent 為執行 Plan 所持之權限，其概念語義即 L6.15 之最小權限與 Plan 範圍化（capability token 之物理機制下放 Layer 7，LDO.2）。**引用紀律（`§P3.E1` 兜底、`AUGUR-WM v1.0 §WM.21(d)`）**：凡意圖進入 Reasoning／Planning 之結構化物件——不問其於本層或下層之命名——所指涉之世界實體**必須**引用已解析之 Identity；Goal／Constraint／Capability／Plan 引用未解析（provisional）Identity 者，該 Plan **不得**通過 EV.9 Gate（L6.7）、其 Action **不得**進入 EV.10（連 L6.2）。四物件之欄位設計與 serialization 下放 Layer 7（LDO.6）。」

二、L6.19 錨定標注同步：「[N｜carries｜`AUGUR-MC v1.3 §P2.E3`、`§P5.E1`、`§4 EV.8–EV.12`]」增為「…；refines｜`AUGUR-MC v1.3 §P3.E1`；承接｜`AUGUR-WM v1.0` Annex D D13]」。

三、L6.19 可判定判準句增補：「；存在任一 Plan（或其 Goal／Constraint／Capability）指涉世界實體而未引用已解析 Identity 仍通過 Gate 者，違反本條」。

四、配套（同次 minor 升版）：§0.4 規範術語表增列 Goal、Constraint、Capability；Annex CS front-matter defers-in 欄增列 WM.D13（滿足 Annex D D0 承接判準）。選配（得後續另辦）：L6.7 Gate 驗證項增列「(4) Planning 物件之已解析 Identity 引用查驗」——L6.19 增補款已足承載義務，此僅為執法點顯式化。

### TR 新列文字（草案）

【L6 Annex TR.D——自「Annex D（D0–D28 除 D24 外）」概括列析出 D13，比照 D24 承接列體例】

| `AUGUR-WM v1.0` **D13**（Goal、Constraint、Capability、Plan 之定義；目標 L5–L6，`AUGUR-MC v1.3 §P3.E1`、WM.21(d) 兜底） | **承接**（2026-07-18 RULING-2026-0XX 補正）：定義面＝L6.19 增補款（Planning 側四物件概念語義——Plan 繫結 Goal／Constraint／Capability 與已授權 Action 集合，連 L6.6(d)／L6.8／L6.15／L6.20；Goal 為模態內容承 `AUGUR-WM v1.0 §WM.17`；Constraint 承 L6.6(a) scope／風險級上限；Capability＝L6.15 權限語義）；引用紀律面（P3.E1 兜底）＝L6.19 增補款（引用未解析 Identity 之 Planning 物件不得通過 EV.9 Gate，連 L6.2／L6.7）；Reasoning 側兜底屬 L5（`AUGUR-L5 v1.0` L5.1／L5.6、CS.1-P3）；欄位／serialization 與 capability token 物理面下放 L7（LDO.2、LDO.6） |

【L5 Annex TR.C(3)——自「D13–D17（表徵治理下放）｜不觸及＋理由：目標 L2–L4」析出 D13 並補正誤植】

| D13（Goal／Constraint／Capability／Plan 之定義；目標 L5–L6，`AUGUR-MC v1.3 §P3.E1`） | 承接（部分）＋轉下放（2026-07-18 補正；原概括「目標 L2–L4」為誤植）：Reasoning 側引用兜底＝L5.1（候選斷言紀律）、L5.6（解釋繫已解析 Identity）；Planning 側四物件之定義權隨 EV.8–EV.10 經 LDO.6 轉 Layer 6（`AUGUR-L6` L6.19 增補款承接） |

### 查證軌跡註記

方法軌跡：先讀 WM Annex D D13 原文（WORLD-MODEL-SPECIFICATION.md:888）與 WM.21(d)（:228）、MC §P3.E1 原文（META-CONSTITUTION.md:260，v1.2/v1.3 同文）；再對兩目標層規格全文親讀＋多角度 grep（英文 Goal/Constraint/Capability/Plan；中文 意圖/計畫/目標狀態/能力/約束），逐一親讀候選落點全文查內容相稱性。

核心發現：(1) 兩層 TR 之概括理由均為事實錯誤——L5 TR.C(3)（COGNITIVE-KERNEL-SPECIFICATION.md:364）稱 D13「目標 L2–L4」，與 Annex D 明載之 L5–L6 直接矛盾；L6 TR.D（AGENT-RUNTIME-SPECIFICATION.md:374）以「非行動治理落點」概括，而 Plan 恰為本層行動治理之核心作用單位。與 D24 同病確認。(2) D3 教訓實證：L6 之 capability 字串 4 處在場（OCV、capability token）均與 P3.E1 之 Agent Capability 義務不對應。(3) 兜底條款（WM.21(d)/P3.E1 末句）於 L6 無任何承接落點——此為實質風險：未解析 Identity 之 Planning 物件現無明文阻卻。

裁量理由：Plan 雖有分散操作性語義，但定義權係 MC 明示 DEFER（授權並要求定義），且引用紀律全缺，故整列判 substantive_gap 而非 doc_fix；修正採 D24 體例最小增補（單一宿主條款 L6.19），同時將既有分散落點（L6.6/L6.8/L6.15/L6.20）以連結方式收編，不重定義、不動他條正文。

界外觀察（僅登錄不擅動，供 Steward 另案）：L5 TR.C(3) 同一概括列中 D14（目標 L4–L5——L5 本身即目標層）、D15（L4–L6）、D16（L6）、D17（L3/L6）之「目標 L2–L4」理由對四列全部誤植；D15/D16/D17/D22/D28 屬其他查證列，本列不代行。RULING-2026-0XX 編號待 Steward 作成裁決時定；L6 現版為 v1.1（AL-2026-016），本補正應為 v1.2 minor 升版。

---

## D15（fail-safe 判定主體／程序、污染追蹤、觀測建議模式邊界；目標 L4–L6；MC 錨 §P2.E5；WM 錨 WM.29）

**disposition：substantive_gap｜反駁：未被反駁**

| 子項 | 判定 | 落點/證據要旨 |
|---|---|---|
| fail-safe 判定主體／程序（錯誤或撤回之判定主體與程序） | gap | L4 KS.102（明文不定）；L5 TR.C WM.25–29 列（不觸及）；L6.20 觸發條件(i)（被動預設）；KS.51／KS.36／KS.62（僅形式表達力） |
| 污染追蹤機制（據以界定「受影響範圍」） | covered | L6.20（受影響範圍之可判定界定＋機器可計算判準）；Annex EO「熔斷之受影響範圍（fail-safe blast radius）」；表達力基底：KS.70、KS.34、WM.34(a) |
| 觀測與建議模式之操作邊界 | covered | L6.20（degrade／halt 釘定）＋L6.17(i)(iii)（degrade 期間之棘輪約束）；殘餘之修復解除判定歸子項一增補款 |

### 修正案文字（草案，待裁）

L6.20 增補一款（既有條款增補款，D24 體例；不另立新條）：

**「判定主體／程序之釘定（承 `AUGUR-MC v1.3 §P2.E5` DEFER、`AUGUR-WM v1.0 §D15`；承接 `AUGUR-KS v1.0` KS.102 界分）**：觸發條件 (i) 所稱『被判定錯誤或撤回』，謂該 Representation／Evidence 上已依 `AUGUR-KS v1.0` KS.51 確立 Supersede Relation（失效類型 ∈ {retracted, invalidated}）、或已依 KS.62 確立衝突裁決 Knowledge。**判定主體**為該失效關係／裁決之作成者**已解析 Identity**（任一得經 Evidence 通道確立 Knowledge 之 Identity 均得作成）；**判定程序**依 KS.51 結構（失效理由 Evidence、transaction time、作成者 Identity）與 KS.36（失效事件本身為需 Evidence 之 Knowledge），**不得**匿名或無證作成。判定一經確立，本條熔斷**必須**機械觸發，Agent **不得**裁量攔阻或延遲（否則構成 `§P5.W5` 侵蝕，L6.18）。**修復之判定**（解除 suspend／degrade）同為需 Evidence 之 Knowledge 行為，以作成者已解析 Identity 為 Source、留痕為 Observation；受影響 Plan／Action 之恢復**不因曾經熔斷而豁免或降低**其 RT 級核准層級（L6.13）與 Completeness／Confidence 門檻（L6.11／L6.12）之全套約束。判定或修復之爭議由 Constitution Steward 依 `§8.1` 裁決（`§P2.E5`）。」

（可判定判準增補：任一熔斷觸發事件可回溯至一已確立之 KS.51／KS.62 行為及其作成者 Identity、任一解除事件具修復 Evidence 與 Source Identity 留痕者合規；存在無對應已確立判定行為之熔斷攔阻或無證解除者違反本條。）

### TR 新列文字（草案）

| `AUGUR-WM v1.0` **D15**（fail-safe 判定主體／程序、污染追蹤、觀測建議模式邊界） | **承接**（RULING-2026-013 主文三逐列查證補正）：污染追蹤面＝L6.20（受影響範圍＝自錯誤 Representation／Evidence 沿 Evidence 溯源鏈與 Identity 依賴之遞迴傳遞閉包，Annex EO「熔斷之受影響範圍」；表達力承 `AUGUR-KS v1.0` KS.70／KS.34）；觀測建議模式邊界面＝L6.20（degrade／halt 釘定：RT-4／不可逆一律 halt；degrade 期間不得延長自動執行鏈〔L6.17(iii)〕、不得降低核准層級〔L6.17(i)〕；否決通道恆常可用 L6.8）；判定主體／程序面＝L6.20 增補款（判定＝KS.51 Supersede Relation／KS.62 裁決之確立，作成者已解析 Identity 攜失效理由 Evidence；熔斷機械觸發不得裁量攔阻；修復判定同為需 Evidence 之行為且恢復不豁免 RT 級約束；爭議→Steward `§8.1`）；失效與 Supersede 形式表達力屬 L4（KS.51／KS.36／KS.62；KS.102 界分），本層消費不重定義 |

### 查證軌跡註記

同病確認：L6 TR 概括列（AGENT-RUNTIME-SPECIFICATION.md:374）之理由「非行動治理落點」對 D15 自相矛盾——同規格 L6.20 條款標頭即「carries §P2.E5（Fail-safe，Layer 4–6 落地）；承接 KS.102」，D15 三子項中兩項（污染追蹤、模式邊界）實質落於 L6.20，概括「不觸及」為錯誤概括，與 D24 先例同型。惟本列非純 doc_fix：子項一（判定主體／程序）為三層循環推諉之未履行 DEFER——L4 KS.102 明文「不定判定主體」（KNOWLEDGE-SYSTEM:554）、L5 明文不觸及（COGNITIVE-KERNEL:323）、L6.20(i) 以被動語態預設判定存在而未繫結任何確立行為（AGENT-RUNTIME:198），MC §P2.E5（META-CONSTITUTION-v1.2:218）明文下放 L4–L6 之義務無任一層承接。最小補正循 D24 體例為 L6.20 增補款（非新條）：其素材全數既存（KS.51 之作成者 Identity／失效理由 Evidence 結構、KS.36 失效事件需 Evidence、KS.62 裁決為新 Knowledge、§8.1 Steward 爭議裁決），增補款僅作顯式繫結與機械觸發、修復對稱程序之釘定，不創設新語義、不上侵 L4。落點選 L6 而非 L4/L5 之理由：判定之效果（暫停 Plan／Action、degrade）屬行動治理，且 L4 KS.102 已明文自我界分為僅供表達力。核對檔案：/home/giga/augur/augur-constitution/specs/WORLD-MODEL-SPECIFICATION.md:271,890；constitution/META-CONSTITUTION-v1.2.md:218；specs/AGENT-RUNTIME-SPECIFICATION.md:197-199,374-375,390-391,518；specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md:265-267,376-382,553-554；specs/COGNITIVE-KERNEL-SPECIFICATION.md:323。

---

## D16（風險分級表、核准流程、確認者資格與獨立性、監督否決度量；目標 L6；WM 掛鉤 WM.28、A.53；MC 錨 §P5.E2／§P5.W5／§P4.E7）

**disposition：doc_fix｜反駁：未被反駁**

| 子項 | 判定 | 落點/證據要旨 |
|---|---|---|
| 風險分級表 | covered | L6.9、L6.10、L6.11、L6.12、L6.21 |
| 核准流程 | covered | L6.13、L6.7 |
| 確認者資格與獨立性 | covered | L6.14 |
| 監督否決度量 | covered | L6.16、L6.17、L6.18 |
| （附隨掛鉤）A.53 域內人類決策動作閉集之維護 | covered | L6.7、L6.13、L6.18(b)、LDO.3／LDO.4 |

### 修正案文字（草案，待裁）

依 D24 體例（RULING-2026-013 主文二）之三處純文書修正，均不另立新條、編號不動：(1) Annex TR 概括列（AGENT-RUNTIME-SPECIFICATION.md:374）「Annex D（D0–D28 除 D24 外）」改為「除 D16、D24 外」，並自旗標括注刪去「D16／」（該括注其餘部分照舊，D17 等待其各自裁決）；(2) 於 D24 承接列（同檔:375）之後增列 proposed_tr_text 所示之 D16 承接列；(3) 為滿足 WM Annex D D0 可判定判準（「目標 Layer 規格之 WM.43 承接表含對應 D{n} 列」），於 Annex LDI 之 LDI.2、LDI.3、LDI.4 承接來源欄各補引 `AUGUR-WM v1.0 §D16`（分別對應其 WM.28 hooks 之風險分級／確認者／監督度量三面），並同步鏡射於 CS.3(a)。

### TR 新列文字（草案）

| `AUGUR-WM v1.0` **D16**（風險分級表、核准流程、確認者資格與獨立性、監督否決度量；WM 掛鉤 WM.28、A.53） | **承接**（本列補正：本層即該列之目標 Layer，四子項落點既存、無需增補條文）：風險分級表＝L6.9（R×I 可判定判準）＋L6.10（RT-0–RT-4，含 `§P5.E2` 缺位最高級預設之引述不削弱、全憲章同一分級）＋L6.11／L6.12（各級完備性／Confidence 門檻）＋L6.21（受控介面執法點）；核准流程＝L6.13（有序核准層級與各 RT 綁定、核准者已解析 Identity 為 Source 留痕為 Observation）＋L6.7（EV.9 Gate 強制驗證）；確認者資格與獨立性＝L6.14（行使 `§P4.E7` 下放之定義權）；監督否決度量＝L6.16（OCV）＋L6.17（單調棘輪）＋L6.18（反自我交易／guard-the-guard）；A.53 域內人類決策動作閉集之維護紀律＝L6.18(b)（介入點登錄之變更為最高核准層級 Action）＋L6.7／L6.13，閉集域內內容經 L4/L5 工作流入徵、物理佈點與數值登錄下放 L7（LDO.3／LDO.4／LDO.5） |

### 查證軌跡註記

結論：D16 與 D24 同病（被 TR 一列概括「不觸及」）但不同症——D24 是實質零承接（需 L6.15 增補款），D16 四子項在 AUGUR-L6 v1.1 §5–§6 全數有內容相稱之既存落點（各條均自我標識為行使 §P5.E2／§P4.E7／§P5.W5 下放之定義權，非僅代號在場），故僅需 TR 逐列化＋defers-in 補引，無實質缺口。RULING-2026-013 主文三「實質顯然落於 L6.10–L6.13」之預判成立，且應擴及 L6.9／L6.14／L6.16–L6.18／L6.21。兩點附帶發現（超出本列職權、僅登錄不擅改）：(a) TR.D 之「WM.13–WM.32 不觸及＋理由：屬存在層本體」一列吞沒了 WM.28（hooks 目標含 L6 之條款），本列 D16 承接列已治其實質，惟該列日後宜比照析出 WM.28→L6.10–L6.17；(b) D24 補正本身亦未在 L6 之 Annex LDI 登錄 WM 來源（僅 TR 列），如 Steward 採納本案修正第 (3) 項，宜同案為 D24 補引 `AUGUR-WM v1.0 §D24` 於相應 LDI 列以齊一體例。查證方法：親讀 WM Annex D D16 列＋WM.28／A.53 全文＋MC §P5.E2／§P5.W5／§P4.E7 全文，與 L6.9–L6.18、L6.21、Annex LDI/TR/CS 全文逐項比對。

---

## D17：自然人法規對應表（目標 L3/L6；WM 錨 WM.38；MC 錨 §P1.E3）

**disposition：substantive_gap｜反駁：未被反駁**

| 子項 | 判定 | 落點/證據要旨 |
|---|---|---|
| L3 側｜自然人 identity 側去識別化／法規強制抹除機制（tombsto | covered | AUGUR-ID v1.0 ID.42（specs/IDENTITY-SPECIFICATION.md 行 247–250） |
| L3 側｜自然人時變屬性之 as-of 繫結 | covered | AUGUR-ID v1.0 ID.60／§8（specs/IDENTITY-SPECIFICATION.md 行 114、249、308） |
| L3 側｜法規對應表本體與其授權（L3 不代定） | legitimately_out | AUGUR-ID v1.0 IDO.7（行 383）、CS.1-P1（行 687）、T-ID-6（行 713）、自查補正（行 730） |
| L6 側｜法規對應表本體（行使 WM.38／IDO.7 下放之定義權：法域×適用 | gap | 無——L6 全文（specs/AGENT-RUNTIME-SPECIFICATION.md）零命中「法規對應」「IDO.7」「D17 承接」 |
| L6 側｜涉自然人觀測/消費之目的正當性與授權依據前提（WM.38 判準之運行時 | gap | 無相稱落點——L6.3（Knowledge Basis）、L6.7（Gate 驗證 (1)(2)(3)）均無目的/授權依據查驗；L6.15 增補款屬 D24 隔離強制面，義務類型不同 |
| L6 側｜涉自然人行動之風險強制（敏感 Identity ⇒ I3 ⇒ RT-4 | covered | AUGUR-L6 v1.1 L6.9(b)、L6.10、L6.13（specs/AGENT-RUNTIME-SPECIFICATION.md 行 146、150、162） |

### 修正案文字（草案，待裁）

【比照 RULING-2026-013 體例：既有條款增補款、不另立新條、編號不動、判準同步增補；修正實質以 WM.38／§P1.E3／IDO.7 原文為據，未添加原文義務類型以外之義務】

一、（L6.9 增補一款）specs/AGENT-RUNTIME-SPECIFICATION.md L6.9 條文末增補 (d)：
> (d) **自然人法規對應表（承 `AUGUR-WM v1.0 §D17` L6 slice、`AUGUR-ID v1.0` IDO.7；`AUGUR-MC v1.3 §P1.E3`、`AUGUR-WM v1.0 §WM.38`）**：本層行使 `§WM.38`／`§D17` 下放之定義權，定義**自然人法規對應表**為本層治理結構：凡 Agent 工作流觀測、消費或表徵涉自然人之資料者，其所涉觀測通道或處理活動**必須**於本表具生效登錄項，載明〔所在法域、適用法規義務（含法規強制抹除／去識別化義務之引用，連結 `AUGUR-ID v1.0` ID.42）、目的正當性、授權依據〕四欄。**表之登錄項為系統狀態、非本規格條文**（準用 `AUGUR-WM v1.0 §WM.35` Registry 前例，其增補不構成本規格升版），其採認**必須**由人類權威作成並留痕為 Observation（`§P4.E7`）。**保守預設**（`§8.3`；`§WM.38` 判準）：未登錄或四欄不全者，該涉自然人資料之觀測消費與相應 Action **不允許**；合規義務與功能衝突時**合規優先**，惟於合法觀測範圍內對已觀測事實之忠實表徵義務（PA）不減損，本款**不得**引為選擇性表徵之依據（`§WM.38`）。本條 (b) I 軸之「自然人（`§P1.E3`）敏感」標記**必須**可解析至本表登錄項。物理載體與部署面（表之儲存、語料隔離、egress 預設拒絕）細化下放 Layer 7（L7.33 既載）。

可判定判準末增：「涉自然人資料之任一觀測消費或 Action，其法規對應表登錄項存在且四欄俱全者為合規；未登錄或欄位不全而仍消費或執行者違反本條。」

二、（Annex TR 概括列拆分）TR.D 之 Annex D 概括列改「D0–D28 除 D24、D17 外」，D17 析出改列承接（新列文字見 proposed_tr_text）；旗標註記中 D17 自存疑清單移除（已裁決）。

三、（TR.D IDO 列事實更正）「`AUGUR-ID v1.0` IDO.0–IDO.8｜不觸及＋理由：目標 L4/L5/L7」改為：「**IDO.7（目標 L6）→ 承接（L6.9(d)）**；其餘（目標 L4/L5/L7）不觸及＋理由：已由對應層承接；本層消費已解析 Identity」——原列理由對 IDO.7 為誤述，比照 L7 LDI.23 更正體例明記。

四、（TR.D WM.35–WM.38 列析出）WM.38 自「不觸及＋理由：屬存在層／L4 落點」析出，改「WM.38 → L6.9(d)、L6.10、L6.13—承接；WM.35–WM.37 維持不觸及＋理由」。

五、（三向可解析補全）Annex LDI 增列（`AUGUR-ID v1.0` IDO.7 → L6.9(d)）；Annex CS front-matter `defers-in` 增 `ID.IDO.7`；CS.1-P1 論證節補述法規對應面承接與判準揭示（登錄項存在性可機器盤點）。

### TR 新列文字（草案）

| `AUGUR-WM v1.0` **D17**（自然人法規對應表；目標 L3/L6，`§WM.38`、`§P1.E3`） | **承接**（RULING-2026-0XX 補正）：**L6 slice**（法規對應表本體與其授權，承 `AUGUR-ID v1.0` IDO.7）＝L6.9(d) 增補款（自然人法規對應表：四欄登錄義務、登錄項為系統狀態、未登錄即不允許之保守預設、合規優先且忠實表徵不減損、I 軸敏感標記可解析至表）；行動風險面＝L6.9(b)／L6.10／L6.13 既載（涉自然人敏感 Identity ⇒ I3 ⇒ RT-4 ⇒ 事前雙人類獨立核准）；**L3 slice** 由 `AUGUR-ID v1.0` ID.42（去識別化／法規強制抹除）＋ID.60（as-of 繫結）既承；部署面細化下放 L7.33（語料隔離之機器強制、egress 預設拒絕） |

### 查證軌跡註記

先行偵察證實：L6 全文零命中「法規對應」，D24 同型真缺口成立，且較 D24 更明確——三層規格已合圍指認 L6 為唯一未清償之目標層：(1) WM.38 義務主體明列「Layer 3、Layer 6 規格作者」（WORLD-MODEL-SPECIFICATION.md 行 370）；(2) L3 以 IDO.7 設規範性下放掛鉤、目標 L6（IDENTITY-SPECIFICATION.md 行 383），依掛鉤義務目標層須於 defers-in 承接；(3) L7 已兩處明文更正退還（INFRASTRUCTURE-SPECIFICATION.md 行 358 L7.33 更正說明、行 634 LDI.23：「IDO.7 之目標為 L6…本層不代定、不代行」）。而 L6 之 TR.D 行 380 對 IDO.0–IDO.8 概括稱「目標 L4/L5/L7」，對 IDO.7 構成事實錯誤陳述，屬 D24 型概括之外另一獨立缺陷，修正案第三項專門處理。增補落點選 L6.9 而非 L6.7/L6.15：L6.9(b) 為 L6 現行唯一引 §P1.E3 之條款（「自然人敏感」標記），而該標記現無解析來源——增補款使表成為標記之解析來源，形成內在閉環；消費阻卻之執法可由既有 L6.21 單一執法點與 L6.7 Gate 依「不允許」保守預設稽核，毋須增 Gate 驗證項。表之登錄項採 WM.35 Registry 前例（系統狀態、非條文），避免規格代定具體法域法規（該內容屬 Steward 採認之系統狀態，與 D6 採認體例一致）。程序面：L6 現為 v1.1（RULING-2026-013／AL-2026-016），本補正屬 §8.6 minor，須 Steward 書面指示後施作。

---

## D22：核心宇宙完整性 gate、流動性分位地板、產業條件豁免機制（目標 L4–L6；MC 錨 §P4.W1；WM 掛鉤 A.12/A.14；WM 原文 WORLD-MODEL-SPECIFICATION.md:897）

**disposition：substantive_gap｜反駁：未被反駁**

| 子項 | 判定 | 落點/證據要旨 |
|---|---|---|
| 核心宇宙完整性 gate（成員資格為資料品質之函數之判準機制） | gap | L4 候選親讀後全數不相稱：KS.45（D27 as-of 快照）、KS.55（禁 DELETE 重建）、KS.74（synthetic 標記）僅治理成員斷言作成後之版本化／可重建性，無一定義「何者得入核心宇宙」之 ga |
| 流動性分位地板 | gap | 三目標層規格全文 grep「流動性／分位／liquidity／percentile／地板／floor」：KNOWLEDGE-SYSTEM-SPECIFICATION.md、COGNITIVE-KERNEL-SPECIFI |
| 產業條件豁免機制（制度性缺某類資料之板塊於成員資格判準之條件豁免） | gap | L4：KS TR.C A.12 列（:802）作「不觸及＋理由：領域實例」——與 A.12 原文（WM:524）自載之 DEFER（「機制 DEFER Layer 4–6，Annex D D22」）直接矛盾；KS.81  |

### 修正案文字（草案，待裁）

〔D24 體例：既有條款增補款、TR 拆分，不另立新條、編號不動〕
一、L4（KNOWLEDGE-SYSTEM-SPECIFICATION.md）：
(1) KS.80 條文末增補一款：「**核心宇宙成員資格判準（承 `AUGUR-WM v1.0 §D22`、`§A.14`）**：核心宇宙（模型消費之成員集）之成員資格判準**必須**為資料品質之函數、**不得**含投資價值面因素（`§A.14` 判準定位）；其判準結構為 (i) **完整性 gate**——成員須達以 KS.81 維度可盤點之資料完整性要求；(ii) **流動性分位地板**——以分位表述之流動性下限，本層定其量測口徑與分位基準之結構，具體分位值與 gate 門檻值為 operational 層參數（`§A.48`：於 operational 層合法且須透明揭露），其採認與變更核准 DEFER Layer 6；(iii) **產業條件豁免**（KS.81(f)）。成員資格斷言為 Knowledge 級衍生斷言，受 KS.20／KS.45／KS.55 既有約束；判準之計算實作屬 Layer 5 inference（比照 KS.83(ii) 體例），本層不定演算。**可判定判準**：成員資格判準含任一投資價值面因素、或 gate／地板／豁免不可解析至本款結構者，違反本條。」
(2) KS.81 增補一維 (f)：「**產業條件豁免（承 `§D22`、`§A.12`）**：某產業板塊制度性缺某類資料者（如金融保險業無月營收申報制度），該缺位為世界結構事實，**不得**計為 (a)–(e) 之完備性缺陷或完整性 gate 之未達；豁免以『產業分類×資料類』為粒度，其依據（制度性缺位事實）本身為須具 Evidence 之 Knowledge（`§P4.W1`）；豁免之授予、存續審查與撤銷之核准 DEFER Layer 6。」
(3) TR.C D22 列（:832）更正：刪誤標「多重比較家族治理→KS.84」（該實質屬 D12，已有 :837 列承載），改綁 KS.80 增補款＋KS.81(f)；A.12 列（:802）改「KS.81(f)—承接」；A.14 列（:804）增 KS.80 增補款；KS.9 承接盤點表與 Annex DI 增列（KDI 續號）承 `§D22`，CS defers-in 枚舉（:989）同步增 `§D22`。
二、L5（COGNITIVE-KERNEL-SPECIFICATION.md）：TR.C（:366）「D19–D25」概括列改「D19–D21、D23–D25」，析出新列：「D22｜承接（計算面）：成員資格衍生計算為本層 inference（承 KS.80 增補款下放，比照 L5.9／KS.83(ii) 體例），受 L5.2（as-of 消費）、L5.3（Confidence 傳播）既有紀律約束，不另立新條；判準結構屬 L4、數值與豁免核准屬 L6」。
三、L6（AGENT-RUNTIME-SPECIFICATION.md）：L6.11 條文末增補一款：「**核心宇宙判準數值與產業條件豁免之治理（承 `AUGUR-WM v1.0 §D22`；`AUGUR-KS v1.0` KS.80 增補款／KS.81(f) 下放）**：核心宇宙完整性 gate 之門檻值與流動性分位地板之具體分位值為本層治理參數——其採認與變更**必須**經人類核准、以核准者之已解析 Identity 為 Source、留痕為 Observation（L6.13 留痕體例準用），數值化登錄為系統狀態（下放 L7）；產業條件豁免之授予、存續審查與撤銷同受本款核准與留痕義務，其依據（制度性缺位事實，`§A.12`）須為具 Evidence 之 Knowledge（`§P4.W1`）。」並依 proposed_tr_text 拆分 TR 概括列。

### TR 新列文字（草案）

| `AUGUR-WM v1.0` **D22**（核心宇宙完整性 gate、流動性分位地板、產業條件豁免機制） | **承接**（RULING-2026-013 主文三旗標之逐列補正）：判準結構面＝L4（`AUGUR-KS v1.0` KS.80 增補款〔成員資格為資料品質之函數、三機制結構〕＋KS.81(f)〔產業條件豁免之完備性語義〕）；計算面＝L5（成員資格衍生為 inference，`AUGUR-L5 v1.0` L5.2／L5.3 既有紀律）；治理面＝L6.11 增補款（gate 門檻值與流動性分位值之採認變更核准、產業豁免之授予存續審查——人類核准留痕，數值登錄下放 L7 系統狀態） |

### 查證軌跡註記

本列與 D24 同病且加重一級：D24 為 L6 概括「不觸及」致零承接；D22 除 L6 概括外，L4 側存在**偽陽性承接**——KS TR.C D22 列（KNOWLEDGE-SYSTEM-SPECIFICATION.md:832）事項描述「多重比較家族治理」非 D22 原文（實為 D12/HOOK-03 實質，D12 已自有列 :837 綁同一 KS.84），且 KS.9 承接盤點表（:146-157）與 Annex DI（KDI.1–17）均無 D22，形式承接從未成立——正是 D3 教訓（代號在場≠義務對應）與 151 誤標病灶之同型。L5 側 CK TR.C（COGNITIVE-KERNEL-SPECIFICATION.md:366）「D19–D25｜目標 L2–L4」之理由對 D22（目標 L4–L6）事實錯誤。三子項於三目標層全文多角度搜證（核心宇宙/CoreUniverse/宇宙/universe、流動性/分位/liquidity、產業/金融/月營收/豁免、gate/完整性）皆無內容相稱落點，全數 gap，無一 legitimately-out（三子項均為 A.12/A.14 逐字指名之 DEFER 事項）。層間分工依 repo 既有體例導出：量尺／判準結構屬 L4（KS:550 L56.0 明文 KS.80 門檻值屬 L6）、演算屬 L5（KS.83(ii)／L5.9 先例）、數值採認與核准屬 L6（A.48 同一數值異層合法性）、數值登錄下放 L7（L6.11/L6.12 既有句式）。另提醒：KS TR.C D22 誤標之更正屬生效規格修正，須 Steward §8.5/§8.6 程序（minor），不得執行層順手擴改；KS/L5/L6 三份規格均需動，版本各 minor 升版。

---

## D28：誠實輸出契約本體（產物閉集、硬綁揭露五項、展示分級、fail-closed 閘）｜目標 L5–L6｜WM 掛鉤 A.50｜MC 錨 §P2.E5、§P4.E4

**disposition：substantive_gap｜反駁：未被反駁**

| 子項 | 判定 | 落點/證據要旨 |
|---|---|---|
| 產物閉集（對人呈現之預測性產物限於經登錄閉集） | gap | 查證候選：L5.1（推理產物＝候選斷言）、L5.6/LDO.3（解釋內容義務，呈現下放）、L6.1（六元組）、L6.21（受控介面 F6 執法點）、L7.44(a)（可枚舉受控出口集合） |
| 硬綁揭露五項（基線對照、校準 provenance、歷史／即時標示、對映偏差等揭 | gap | 查證候選：L5.6（per-結論解釋四要素）、L5.7（Computational Evidence 映 L_C 須具校準 Grading Method provenance）、L6.16(T)（執行前揭露比例）、L7. |
| 展示分級（未過 GATE 不得呈現／過 GATE 經濟判死僅研究級並硬綁判死標籤 | gap | 查證候選：L5.5（GATE 可證偽→OOS＋經濟裁決工作流）、L5 T-L5-4（呈現層不得規避內容義務之警語）、L6.10（RT-0–RT-4）、L7.43(c)（呈現不得洗白） |
| fail-closed 閘（產物持久層寫入機械繫於 GATE 成就；無過門＝誠實 | gap | 查證候選：L6.20（§P2.E5 錯誤傳播熔斷）、L6.3＋L6.12（INSUF 不得為 RT≥1 依據）、L6.7（EV.9 Human Authority Gate）、L7.44(d)（介面 fail-close |

### 修正案文字（草案，待裁）

【L6 側，AGENT-RUNTIME-SPECIFICATION.md；比照 RULING-2026-013 體例：既有條款增補款、不另立新條、編號不動】

一、（L6.21 增補一款）L6.21 條文末增補：
「**誠實輸出契約之行動側承接（承 `AUGUR-WM v1.0 §D28`／`§A.50`；憲章依據 `§P2.E5`、`§P4.E4`）**：凡經 Controlled External Interface 對人呈現之預測性產物，介面**必須**於放行前另行驗證：(i) **產物閉集**——產物屬經登錄之產物閉集，閉集外之預測性數字**不得**對外呈現（閉集之枚舉登錄為系統狀態，下放 Layer 7，仿 L6.11／L6.12 數值登錄模式）；(ii) **硬綁揭露**——每一呈現之預測性數字與其揭露事實五項（基線對照、校準 provenance、歷史／即時標示、對映偏差等，`AUGUR-WM v1.0 §A.50`；其世界模型結構位置＝`§WM.12`／`§WM.33`）於同一呈現單位內不可分離同現，缺任一項者該數字**不得**呈現；(iii) **展示分級**——呈現級別屬閉集有序分級：未達 GATE 成就（`AUGUR-L5 v1.0` L5.5）者**不得**呈現；達成就而經濟裁決否定者**僅得**研究級呈現且與裁決標籤硬綁；達成就且裁決存活者方得完整呈現；分級狀態缺位或不可解析者從最嚴（`§8.3`）；(iv) **fail-closed 閘**——上開任一驗證不成立或不可判定者一律阻卻，改以顯式之誠實拒答形呈現（不得以部分產物或降級數字充填），且產物持久層保持零寫入；其 DB 機械強制（trigger 級）與揭露載體下放 Layer 7（L7.43／L7.44 準用）。」

二、（L6.21 可判定判準同步增補）「存在任一對人呈現之預測性數字屬閉集之外、或未同現其硬綁揭露五項、或其展示級高於其 GATE／經濟裁決狀態所許、或於狀態不可解析時仍呈現數字或寫入產物表者，違反本條。」

三、（L5 側，COGNITIVE-KERNEL-SPECIFICATION.md，僅 TR 文字更正、無條款增補）TR.C (3) D28 列由「D28（下放尾項）｜不觸及＋理由：非本層落點」改列（見 proposed_tr_text 之 L5 列）——L5 之 D28 面（GATE 成就狀態＋Hypothesis 模態標記）L5.4／L5.5 既載，呈現面依 LDO.3 本層不定；原「非本層落點」與 WM 原文目標 L5–L6 矛盾，屬誤述。

四、（等級）比照 RULING-2026-013：§8.6 minor（增補承接與一款義務、無原則級變更、編號不重排）；L6 v1.1→v1.2、L5 v1.0→v1.0.x（或依 Steward 定）。實質以 WM §D28／§A.50 原文為據，未添加原文義務類型以外之義務（誠實拒答／零寫入／三級分級為 fail-closed 閘與展示分級之原文義務操作化，源自 A.50 所指上呈素材之 SSOT——augur-code 大憲章 v1.46.0 輸出契約條）。

### TR 新列文字（草案）

【L6 Annex TR 新列（自概括列析出，比照 D24 承接列體例）】

| `AUGUR-WM v1.0` **D28**（誠實輸出契約本體：產物閉集、硬綁揭露五項、展示分級、fail-closed 閘） | **承接**（2026-07-18 RULING-2026-0XX 補正）：契約本體＝L6.21 增補款（受控介面放行前四驗證：產物閉集／硬綁揭露五項／展示分級／fail-closed 閘）；分級狀態消費 `AUGUR-L5 v1.0` L5.4／L5.5（GATE 成就與模態標記——D28 之 L5 面，既載）；表達力承 `AUGUR-WM v1.0 §A.50`（WM.12／WM.17／WM.33）；物理面下放 L7——揭露載體 L7.43、介面 fail-closed L7.44、產物表 trigger 級機械強制與閉集枚舉登錄 |

（同步：L6 TR 概括列「D0–D28 除 D24 外」改「除 D24／D28 外」，旗標註記中 D28 自「理由未經逐列驗證」名單移除、記為已裁決）

【L5 Annex TR (3) D28 列改列】

| D28（誠實輸出契約本體） | 承接界分：本層供契約所消費之 GATE 成就狀態與 Hypothesis 模態標記（L5.4、L5.5）；契約本體（產物閉集、硬綁五項、展示分級、fail-closed 閘）落點 L6（`AUGUR-L6` L6.21 增補款）——呈現面依 LDO.3 本層不定 |

### 查證軌跡註記

一、同病確認：D28 與 D24 同型且更重——D24 尚有 L6.15/L6.6 可繫機制面，D28 四子項於 L5/L6 全數懸空；A.50 明文承諾「契約本體為 Layer 5/6 上呈素材（DEFER，Annex D D28）」而兩目標層均未承接，L5 TR 更逕稱「非本層落點」，與 WM 原文目標 L5–L6 直接矛盾（偽陰性一例）。L7.43/L7.44 僅收 Action 六元組揭露與授權閘 fail-closed 之物理面，不含五項統計誠實揭露與知識論 GATE 閘，無法替代概念錨——L6.21 增補款生效後，其「下放 L7」句即為 L7 側後續 LDI 承接之根。

二、層分工論證：契約四子項均屬「對人呈現」之治理＝行動側（MC §5 角色六、§P5.E2 末句受控介面執法點），故本體落 L6.21；L5 之 D28 面（GATE 成就狀態、模態標記）L5.4/L5.5 既載，僅需 TR 更正，符合 L5 LDO.3 呈現下放之既有分界。此即 WM「目標 L5–L6」跨層範圍之正解：非兩層各半，而是 L5 供狀態、L6 定契約。

三、順帶查得之範圍外事項（不擅改，提請 Steward 併案審酌）：(1) L5 TR (3) 對 WM Annex D 各列之「事項名」多處與 WM 權威表不符（如稱 D19–D25 為「存在層下放雜項目標 L2–L4」，實則 D19/D22/D23/D24/D25 目標含 L4–L7；D28 稱「下放尾項」）；(2) KS TR (3) 之 Annex D 逐列標籤與 WM 權威編號系統性錯位（如 D1 標「抓取模式五態」，WM D1 實為 Identity 分類體系；D20 標「輸出契約本體」，WM D20 實為領域完整本體）——KS 對 D28 實質判斷（輸出契約下放 L6）方向正確但掛錯編號。此二者屬 RULING-2026-013 主文三旗標之底層成因（各層 TR 對 Annex D 之引用未經與權威表逐列比對），建議 Steward 另案通令各層 TR 之 Annex D 列以 WM 權威表事項名重校。

四、依據檔案：/home/giga/augur/augur-constitution/specs/WORLD-MODEL-SPECIFICATION.md（D28＝L903、A.50＝L661、A.4＝L508）；specs/COGNITIVE-KERNEL-SPECIFICATION.md（TR D28＝L368、L5.4/L5.5＝L124–130、LDO.3＝L204）；specs/AGENT-RUNTIME-SPECIFICATION.md（概括列＝L374、L6.21＝L205–207、L6.20＝L197–199、L6.3/L6.10–L6.13＝L113–163）；specs/INFRASTRUCTURE-SPECIFICATION.md（L7.43＝L414–421、L7.44＝L423–431）；五項與展示分級之 SSOT＝/home/giga/augur/augur-code/docs/系統架構大憲章_v1.46.0.md L133–136（三產物閉集／五項硬綁①基線②purged 校準 provenance③非重疊窗 n 與 HAC④歷史 OOS 非 live 標示⑤禁單股準確率／三級展示分級／fail-closed DB 機械閘）。
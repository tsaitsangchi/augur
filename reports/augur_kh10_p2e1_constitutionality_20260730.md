# KH10 自動准入 × `AUGUR-MC v1.6 §P2.E1` 合憲性分析（一頁）

**性質**：Agent 之**草擬與呈案**，非解釋（見 §f）。**日期**：2026-07-30。**呈**：Constitution Steward。
**議題**：領域大憲章「一律准入＋漸進 KH」（v1.48.0 立，現行 **v1.50.0** L186）與元憲章 `AUGUR-MC v1.6 §P2.E1`「禁 AI 直寫永久 Knowledge」之關係，至今無任何文件正面交代。
**版本更正（親驗）**：任務所指 `docs/系統架構大憲章_v1.49.0.md` **查無此檔**；現行為 `docs/系統架構大憲章_v1.50.0.md`，且所指 **L162／L163 行號在 v1.50.0 恰對應**（`grep -n` 覆核），故本檔一律引 v1.50.0。

---

## 0. 親驗事實（本分析之全部事實基礎；每項可重跑）

| # | 事實 | 來源（親驗） |
|---|---|---|
| F1 | 機械 actor 常數 `ACTOR = "system:kh10_auto_admit"`；`progressive_item()` 以 `upsert_state()` UPDATE `knowhow_auto_admit_state.admit_depth`，`GREATEST(...)` 單調不降 | `src/augur/knowledge/auto_admit.py:17`、`:106-121`、`:479-487` |
| F2 | depth 4 判準＝`kh4` 之 `answer_status='eligible'`；其充分條件為 `entity_type ∈ SEMANTIC_ENTITY_TYPES ∧ license ∈ LICENSE_WHITELIST ∧ has_embedding`——**全為系統自身結構存在性檢查，無任何外部佐證要件** | `auto_admit.py:230-251`、`src/augur/knowledge/kh4.py:52-58` |
| F3 | `answer_status='eligible'` 是 **advisor 引用空間之實際閘**：檢索三路徑皆 `AND k4.answer_status = 'eligible'` | `src/augur/philosophy/retrieval.py:303`、`:308`、`:353` |
| F4 | live DB：`knowledge_kh4_state` → eligible **145,949**／ineligible 396／blocked 85／provisional 2 | `psql` 聚合查詢 |
| F5 | live DB：`knowhow_auto_admit_state` → `admit_depth=9` **145,949** 列、`=3` 396 列；`knowhow_auto_admit_run` **508,905** 列，`actor` **全部**為 `system:kh10_auto_admit`（**零人類 actor**） | `psql` 聚合查詢 |
| F6 | `knowhow_auto_admit_gate` 實列＝`enabled=t, raw_floor_enabled=t, progressive_enabled=t, max_auto_depth=9, require_kh8=t, require_kh9=t, updated_by='migrate_kh8_kh9_min_ddl.py:KH8-KH9-min-LAND'`；**全表無任何表達「獨立證據要求」之欄** | `\d knowhow_auto_admit_gate` ＋ 實列查詢 |
| F7 | `require_kh8`／`require_kh9` 經 `load_gate()` 讀入後，**無任何決策路徑消費**（全 repo `grep` 僅命中 DDL／migration／`load_gate` 自身）＝**空轉閘** | `grep -rn "require_kh8\|require_kh9" --include=*.py .` |
| F8 | KH8 之 `citation_count` **實為該 item 自身 `knowledge_sentence` 列數**（非外部引用）；`evidence_score = 0.35*cite_norm+0.25*terminal+0.25*embed+0.15*kh4_ok−0.40*contra`，**全部輸入皆系統自身產出** | `src/augur/knowledge/evidence.py:46-101`、`:107-140` |
| F9 | `knowhow_evidence_weight` **145,949 列 100% `confidence_band='high'`（零變異）** | `psql` 聚合查詢 |
| F10 | `curation.HUMAN_ONLY = set()`（v1.48.0 廢止唯人）；`transition(..., system=True)` 得 `approve`／`activate`／`resume` | `src/augur/knowledge/curation.py:33-34`、`:61-69`、`auto_admit.py:343-385` |
| F11 | 三帳本表**皆無 Confidence 槽**：`knowhow_auto_admit_state`（無 Source／actor 欄、無 Confidence、單一 `updated_at`）、`knowledge_kh4_state`（有 `evidence` 欄、無 Confidence、單一 `updated_at`）、`knowhow_evidence_weight`（有 `confidence_band`，但無 Source／actor 欄、單一 `created_at`） | `information_schema.columns` 實查 |
| F12 | `constitution/` 全域 `grep`：**無任何 RULING 或 AL 列提及 `v1.48.0`／「一律准入」／`kh10_auto_admit`**；`AMENDMENT-LOG.md` 最末列＝**AL-2026-045（2026-07-23）**，而 v1.48.0 為 **2026-07-29** | `grep -rn` 覆核 ＋ AL 尾列 |

---

## a. 爭點界定：`§P2.E1` 禁的究竟是什麼

**逐字原文**（`constitution/META-CONSTITUTION.md:219`）：

> **P2.E1**：禁止 AI 直接從 raw data 建立永久性 Knowledge。所有 AI 產物必須經標準鏈（§4 之節選 EV.2–EV.6）：`Observation → Representation → Identity → Evidence → Knowledge`

**界定結論：`§P2.E1` 所禁之客體是「AI 執行之狀態轉移」，非「AI 生成之內容入庫」。** 三項文本依據：

1. **句法**：條文之受詞是「**建立**…Knowledge」，「raw data」為**起點**、「Knowledge」為**終點**，被禁者是兩點間之「**直接**」連線（跳過中段節點）。條文未以「內容由誰撰寫」為要件。
2. **`§P2.W2` 明文允許 AI 產製**（`:207` 逐字）：「AI **得**參與 Representation 之建構（identity resolution、抽取、映射），但其輸出僅得以附帶 Evidence 與 Confidence 之**候選斷言（proposed assertion）**進入系統，經 Evidence 通道（§2.11，節選 EV.2–EV.5）確立後，方成為 Representation 之一部分。」——禁令落點在「**確立**」（狀態轉移），不在「產製」。
3. **`§P2.E2`／`§P2.E3` 為同構特例**，二者違反要件皆為「**未經 Evidence 通道**」：`§P2.E2`（`:225`）「Model output **不得未經 Evidence 通道（§2.11）**，直接成為權威 World Representation 或 Knowledge」；`§P2.E3`（`:226`）「Agent **不得繞過 Evidence 通道**…此類自我陳述之 Observation 必須永久攜帶 **self-reported 標記**，僅構成『關於該 Action 之宣稱性 Observation』，非世界狀態之權威確認；其升級為 Knowledge 受 P4.E7（不得僅以系統自身產出為據）約束。」

**推論**：「內容之作者身分」由**另一組條款**管——`§P4.E7`／`AUGUR-KS §KS.74`（synthetic 永久標記＋Trust Rank 天花板）、`§KS.21`（Source 槽）。把「AI 生成」與「AI 直寫」混為一談，會同時放過 `§P2.E1` 真正的射程。

---

## b. 「原文入庫非 AI 生成、AI 僅搬運」是否足以消解

**分兩支評估。**

**B1「原文之內容非 AI 生成」→ 不足以消解。** 該論據為真（憲章第三部以 `source_type`／`work_type`／`license` DB CHECK 硬擋 `ai_generated`），但依 §a 之界定，它回應的**不是 `§P2.E1` 所問的問題**——打錯靶。

**B2「原文＝Evidence 級物件，非 Knowledge，故未跨終點」→ 就「進庫」這一步足以消解，並有明確憲法依據**：

- `AUGUR-KS v1.1 §KS.71` 逐字：「**Knowledge Evidence**（如 Paper、Specification）」——即論文／規格類原文在規範上是**證據（Evidence）**，非 Knowledge 斷言。
- `§P2.E1` 之標準鏈中 `Evidence` 為 `Knowledge` 之**前置節點**；把原文放進 Evidence 位置，正是**走完標準鏈中段**，不是跳過終點。
- 領域憲章 v1.50.0 L186(2) 之措辭「（**進庫≠可答**）」與此一致。

**⇒ 故憲法上可消解者，止於「原文入 `knowledge_item` / `knowledge_item_text`」。**

**缺口在哪一步（精確定位）**：標準鏈之**最後一段 `Evidence → Knowledge`**。v1.50.0 L186(3)「再逐層 KH update 升格精準」**未指定**該段由誰、以何據完成；live 實作以 `system:kh10_auto_admit` 之機械 UPDATE 完成（F1），其判準為系統自身結構存在性（F2），且該升格直接控制 advisor 得引用什麼（F3）。**缺口＝「Evidence → Knowledge」這一步無憲法授權之依據要求。**

---

## c. 不可消解之殘餘（四項）

**C-1（核心）｜可答性升格構成「權威性宣稱」，且以自身產出為唯一依據。**
`answer_status='eligible'` 之效果是使該 item **進入顧問層可引用之權威材料集**（F3），此即對「此內容足為引據」之斷言。其唯一依據為 F2 之結構存在性檢查——`§P4.E7` 逐字（`:320`）：「高風險 Action 之結論**不得僅以系統自身產出之證據為依據**，須至少一項獨立 Data Evidence 或人類確認」；`§KS.76`／`§KS.77` 同旨。
**二叉困境（兩支皆有缺口）**：
- 若 `eligible` **是** Knowledge → 依 `§KS.20`「**缺一即違憲不變式**」，F11 顯示缺 Confidence 槽（且缺 Source 槽、Timestamp 非雙時間）＝`§P4.E1` **結構性違反**，而 `§P4.E1` 屬 `§8.4` **不可豁免核心**。
- 若 `eligible` **非** Knowledge、僅為 Agent 自陳狀態 → 依 `§P2.E3` 須「**永久攜帶 self-reported 標記**」，F11 顯示實表**無此欄**。

**C-2｜KH8「證據層」在憲法上恆非獨立，且對本集無鑑別力。**
`§KS.75` 逐字：「該 Data Evidence 之 provenance 鏈**遞迴不含本系統之 Computational Evidence**，**且**不與待證結論共享上游來源。」F8 顯示 KH8 全部輸入皆系統自身產出（`citation_count` 更是該 item 自身句數）⇒ **恆不滿足 `§KS.75`**，故 KH8 **不能**充當 `§P4.E7` 所要求之「至少一項獨立 Data Evidence」。另 F9（145,949 列 100% `high`、零變異）顯示該分級器對本集**不產生任何區辨**——呼應 `CLAUDE.md #11` 提拔關卡與本專案「評測樣板地板」教訓。

**C-3｜唯一看似證據要件之閘為空轉。** F7：`require_kh8`／`require_kh9` 讀入後無任何路徑消費。帳面有要件、實際無——屬「防呆機制自己靜默失效」型，**不得**引為「已有證據要求」之依據。

**C-4｜人工介入點之移除（超出本案原始議題框架，但同一機制，須併呈）。**
F10：v1.48.0 廢止 `approve`／`activate` 唯人。`§P5.W5` 逐字（`:337`）：「凡**降低既有人工核准層級、移除人工介入點**、或延長無人工檢核之自動執行鏈之變更，**一律推定違反本條，不得實施**；該推定僅得由 Steward 依 §8.1 解釋權以書面裁決推翻，裁決**必須附具「該變更未實質降低人類監督與否決能力」之認定理由並公開存檔**。」相關配套：`§8.4` 列 `P5.W5` 為**不可豁免核心（連履行時程亦不得豁免）**；`AUGUR-L6` L6.17（OCV componentwise 非降之單調棘輪，D 分量＝人工介入點密度／覆蓋）；L6.18(a)「Agent…**不得**為任何降低 OCV…之變更之**核准主體**」；L6.18(c)「self-reported 之 OCV **不得**單獨作為『未降低監督能力』之依據」。`§8.1`「解釋之界線」(c) 另明定「移除或削弱既有制衡（含公示、獨立核驗、**人類介入點**）」**視為修訂**、應依 §8.5 辦理。
**親驗定位（F12）**：Steward 之**拍板存在**（v1.50.0 修訂歷程 v1.48.0 列載「用戶拍板『請入憲』」及動因），但 `§P5.W5` 所要求之**特定形式**——附具「該變更未實質降低人類監督與否決能力」之**認定理由**並公開存檔、及 MC 側 AL 登錄——**於 `constitution/` 全域查無留痕**。此為**形式要件之缺載**，非對 Steward 決定之質疑；補正之（見 §e-A）即可閉合。

---

## d. L162／L163(iii) 人閘 × L186 KH10 機械准入之界分建議

**並存現況（v1.50.0 逐字）**：L162「…得依**決策層人拍板**納入管理/能源材料/…等知識域（「能抓≠該抓」判準不變；機制=INSERT registry 列零 code…）」；L163「**(iii)** …新應用域之納入＝決策層人拍板（能抓≠該抓）」；L186(1)「**無人核可限制**：不以決策層人裁 `approve`／`activate` 為准入條件；機械路徑（含 `system:kh10_auto_admit` 等）得執行狀態機升級…」。三條未界分。

**建議切線＝「域之開設（該不該）」vs「域內物件之處理（怎麼做、到哪一層）」**——前者為判準／範圍決策、機械不可判；後者為機械可判之逐物件推進。此切線不新創判準，僅把 L162／L163 既有之「能抓≠該抓」與 L186 既有之「進庫≠可答」各自歸位。

**建議措辭（供 Steward 一字增刪；我不擅改憲章）**——於 L186 之 (1) 句後增：

> **(1a) 域級保留**：本條之「無人核可限制」限於**已開設 domain 內個別物件**之入庫與 KH 水印升格；**新知識域／新應用域之開設**（新增 `knowledge_domain` 列、`knowledge_source.domain` 新值、或 `principle_domain_map` 新應用域）仍為**決策層人拍板**，L162／L163(iii) 不受本條影響，機械 actor **不得自行開域**。

並於 L162、L163(iii) 各加括號註「（**域級**；域內物件級依 L186）」。
**配套機械閘（呈案、非我可設）**：`knowledge_source` 之 `domain` 若不在 `knowledge_domain` 字典集合內即於 DB 層拒絕——係 v1.28.0 既有 `knowledge_domain` 字典 FK 之延伸，非新判準。

---

## e. 可選處置（Steward 一字拍板）

| 案 | 內容 | 一句話後果 |
|---|---|---|
| **A｜補正形式、保留機制** | 出一則 Steward 裁決，一併處理：(i) §a／§b 之 `§P2.E1` 界分（進庫＝Evidence 段合憲；`Evidence→Knowledge` 升格須具據）、(ii) `§P5.W5` 推定之推翻**或**改設代償介入點、(iii) §d 之域級／物件級界分；並補 MC 側 AL 列 | 機制照跑、憲法留痕補齊；代價＝`§P5.W5` 之認定理由**須 Steward 親筆**（不可代打），且 C-1／C-2 之證據缺口仍須另定補正時程 |
| **B｜收窄至可答性以下** | `max_auto_depth` 由 9 降至 3（KH3 Terminal）；depth 4 之 `eligible` 恢復須獨立要件（人簽或外部 Data Evidence） | C-1／C-2 殘餘立即消滅、且**無須** `§P5.W5` 裁決（介入點回復而非移除）；代價＝145,949 件退出 advisor 引用空間，顧問可答面大幅縮小 |
| **C｜維持現狀、明記為已知缺口** | 於 L186 與 KH10 計畫書加註「與 `§P2.E1`／`§P5.W5` 之關係為 OPEN、未經裁決」 | 零工程成本；惟須注意 `§8.4` 明定 `P5.W5` 連履行時程亦不得豁免、`§8.3` 存疑即不允許、`§P5.W5` 明文「推定期間**不得實施**」——**「明記缺口」是否足以治癒屬解釋問題，非 Agent 可斷** |

**呈簽併案事項（我認為不該由我改）**：
1. `reports/augur_ten_layer_knowhow_architecture_plan_20260728.md` **L66**（§1.3 Non-goals）「不自動 approve / activate 來源｜`approve` / `activate` **仍唯人**」與 **L592–L593**（§4.2）「KH10 ≠ 自動 approve｜來源升級**仍唯人**」／「KH10 ≠ 自動 activate」，與 v1.50.0 L186、`curation.HUMAN_ONLY = set()`（F10）**直接矛盾且未對齊**。該檔非我指派範圍（且已有他人於 L259／L475／L562／L926 加註 2026-07-30 對齊，其中 L259／L562 已置入指向本檔之待決指針），故**不動**、僅呈報。
2. C-3（`require_kh8`／`require_kh9` 空轉）與 C-2（`confidence_band` 零變異）屬**執行層修正**，但因其被引為「已有證據要求」之表象，處置方向須隨 A／B／C 之選擇決定，故不自行修。

---

## f. 我的界限

**本文為 Agent 之草擬與呈案，非解釋。** `AUGUR-MC v1.6 §8.1` 逐字：「必須存在唯一之人類憲章權威（**Constitution Steward**…）。Steward 持有：條文之最終解釋權／規格之違憲審查權／修憲之裁決權」、「**Agent（§2.8 意義下之自主程序）不得參與修憲與解釋**」。故：

- 本文之「界定」（§a）、「缺口定位」（§b）、「殘餘」（§c）**僅為呈案時之爭點整理與事實對照**，不具解釋效力、不得被引為先例；有拘束力之解釋唯 Steward 之書面裁決（附理由、公開存檔）。
- **不改任何治權檔**：本次未觸 `docs/系統核心思想*`、`docs/原則精華*`、`docs/系統架構大憲章*`、`CLAUDE.md`、`constitution/*`、`specs/*`；§d 之措辭僅為**建議文字**、未寫入憲章。
- **不創設新判準**：§d 之切線與 §e 之三案皆由既有條文（L162／L163／L186／`§P2.E1`／`§P4.E7`／`§P5.W5`／`§KS.20`／`§KS.75`）組合而得，未新訂要件。
- **不代打人簽**：`§P5.W5` 之認定理由、A／B／C 之選擇，均須 Steward 親為。
- **事實與規範分離**：§0 各列為機械可重跑之親驗事實；規範側全部引文均已逐字 `grep` 覆核對得上原檔，查不到者已明記「查無」（見版本更正、F12）。

---

（2026-07-30 對齊：本檔為新建之呈案文件，依 hugo 拍板 P8 產出；引據＝`constitution/META-CONSTITUTION.md`〔`§P2.E1`/`§P2.W2`/`§P2.E2`/`§P2.E3`/`§P4.E7`/`§P5.W5`/`§8.1`/`§8.4`〕、`specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md`〔KS.20／KS.21／KS.71／KS.74–KS.77〕、`specs/AGENT-RUNTIME-SPECIFICATION.md`〔L6.16–L6.18〕、`docs/系統架構大憲章_v1.50.0.md`〔L162／L163／L186〕、`reports/augur_ten_layer_knowhow_architecture_plan_20260728.md`〔§1.3／KH10 節／§4.2〕，及 `src/augur/knowledge/{auto_admit,kh4,evidence,curation}.py`、`src/augur/philosophy/retrieval.py`、live DB 實查。）

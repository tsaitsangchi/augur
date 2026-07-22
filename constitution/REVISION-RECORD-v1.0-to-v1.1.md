# 《Augur Meta-Constitution v1.0 → v1.1 綜合修訂建議書》

裁決人：首席架構師
輸入：7 位顧問視角之完整審查（邏輯與哲學一致性、系統架構與可實作性、知識工程與本體論、AI 治理與安全、治理與修訂機制、文檔結構與語言品質、十年演化韌性）
裁決基準：忠於原作者之 Prime Axiom 與極簡收斂哲學 —— Layer 0 只收「十年不變的原則」；實作細節降級至下層或附錄；新增原則極度克制。

---

## 一、共識議題排序表（合併去重後，依共識度 × 嚴重度排序）

處置代碼：ACCEPT（納入 v1.1 正文）/ ACCEPT-AS-APPENDIX（降級為非約束性附錄）/ DEFER（屬下層規格，v1.1 只留掛鉤）/ REJECT（不採納）

| # | 議題（合併後） | 共同指出之視角數 | 最高嚴重度 | 處置 |
|---|---|---|---|---|
| 1 | §4 將 PostgreSQL / Neo4j / Vector DB / MCP 寫入 Layer 0 正文，與 §6 技術中立、§7 可修改清單直接矛盾；「由憲章自然導出」為範疇錯誤（原則只能導出角色，導不出品牌） | **7/7（全體一致）** | critical | **ACCEPT-AS-APPENDIX**（§4 改寫為六個抽象角色留正文；產品對照降為非約束附錄 A） |
| 2 | §7 Amendment Rule 治理機制缺失：無提案權、無裁決主體、無決議規則、無記錄義務、無版本化；「不可輕易修改」「證明更完整」不可判定；未涵蓋 Prime Axiom 與 §7 自身（自指漏洞） | 6/7 | critical | **ACCEPT**（重寫為 §8 治理章） |
| 3 | 解釋權與違憲審查完全缺位（Kompetenz-Kompetenz）：無人裁決條文歧義與層間衝突、違憲無後果條款、「不得違反」無執行主體 | 4/7 | critical | **ACCEPT**（併入 §8） |
| 4 | Identity 自舉循環與生命週期缺失：Principle 3 ENFORCE 要求所有 Observation 引用 Identity，但 Identity 從 Observation 解析而來（bootstrapping paradox / 攝取死鎖）；merge / split / retire 無規則，persistent 語義未定 | 3/7 | critical | **ACCEPT**（identifier vs identity claim 區分 + provisional identity + 生命週期原則；細則 DEFER 至 Layer 3） |
| 5 | 「Representation Before Intelligence」自指悖論：建立 Representation 本身需要 AI；「可靠」不可判定；字面線性順序不可執行 | 3/7 | critical | **ACCEPT**（明文化為「權威順序而非時間順序」；AI 產出以候選斷言進入標準鏈） |
| 6 | 演化鏈存在三個互不一致版本（§1 缺 Observation；P2 ENFORCE 缺 Identity —— 等於對 P3 的成文豁免；§3 為完整版） | 2/7 | critical | **ACCEPT**（§3 定為唯一 canonical chain，節點編號 EV.1–EV.12，他處一律標注為節選引用） |
| 7 | 時間性缺失：單一 Timestamp 無法區分「何時為真（valid time）」與「何時得知（transaction time）」；無 as-of 能力則 §5.5「回答為什麼」邏輯上不可能 | 4/7 | critical | **ACCEPT**（原則級宣告；bitemporal 實作機制 DEFER 至 Layer 4 / DB 層） |
| 8 | 可謬性與知識修正缺失：無 defeasibility、無 supersession、無刪除禁令；「可演化」承諾無兌現條款；被推翻知識若可硬刪除，§5.5 永遠無法誠實回答 | 5/7 | critical | **ACCEPT**（只失效不刪除 + 法規抹除 tombstone 例外 + PA「faithfully ≠ 完美鏡像」釐清） |
| 9 | 行動治理缺位：四原則全是認識論（如何知），零條是行動論（如何正當行動）；人類權威不在迴圈中；Action 無風險分級、可逆性、歸責結構 | 3/7 | critical | **ACCEPT**（合併為唯一新增原則 P5 — Accountability Before Action，見裁決 C1） |
| 10 | Confidence 有欄位無語義且從未被下游消費：語義不統一則跨來源不可比；不確定性在 Knowledge → Action 邊界上消失 | 4/7 | major | **ACCEPT**（語義單一性 + 下游傳播與行動門檻約束兩句條款；uncertainty calculus 選型 DEFER 至 Layer 4） |
| 11 | Evidence 自我引證漏洞：Model output 作為 Computational Evidence 可形成自我確證迴圈（trust laundering / model collapse 路徑）；Evidence 自身無遞迴溯源要求，與「拒絕不可重現結果」矛盾 | 3/7 | major | **ACCEPT**（遞迴溯源終止於 Observation 或明示假設 + 信任不可洗白 + synthetic 標記） |
| 12 | 六～九個核心術語（Reality / Observation / Representation / Identity / Evidence / Knowledge / Intelligence / Agent / Confidence）全部未定義，卻出現在 ENFORCE 禁令中，禁令不可判定 | 3/7 | major | **ACCEPT**（新增 Definitions 專章，每詞一句內涵式定義 + 下層不得重定義元規則） |
| 13 | ENFORCE 可驗證性 / 可判定性元規則缺失：憲章評價性謂詞（reliable、faithful）無判定義務；下層規格無合規聲明義務 | 3/7 | major | **ACCEPT**（Decidability 元規則 + Constitutional Compliance Statement 義務，格式下放 Layer 1） |
| 14 | §0 的 13 項規格清單與文末 Layer 1–7 圖是兩套不一致分類；層級圖箭頭語意（constrains？depends？）未定義；違憲規格管轄歸屬無法裁定 | 3/7 | major | **ACCEPT**（單一權威對照表 + Hierarchy Rule：lex superior、概念層不得引用執行層） |
| 15 | 「Agent 自行創造世界狀態」措辭過寬，字面禁掉 Action / Feedback 正常功能；真正該禁的是「意圖未經觀測即寫入為事實」 | 2/7 | major | **ACCEPT**（改寫：execution receipt 以 Observation 身分回流） |
| 16 | 矛盾證據可被下層合法靜默消滅（last-write-wins）：衝突是一級資訊，消滅矛盾等於偽造確定性 | 2/7 | major | **ACCEPT**（矛盾保存條款，併入 P4 ENFORCE） |
| 17 | Prime Axiom 與四原則「推導關係」名不符實：目的論宣言推不出規範；四原則引入公理沒有的新概念 | 1/7 | major | **ACCEPT**（採最小修法：定位為 Supreme Purpose + 並列 Immutable Principles，放棄「唯一公理＋推導」修辭） |
| 18 | 「必須映射至共同世界模型」隱含集中式拓撲，十年後聯邦部署（多站點、資料主權）下不可行 | 1/7 | major | **ACCEPT**（改為語義承諾：single authoritative representation per fact，拓撲下放） |
| 19 | Fail-safe 缺失：發現 Representation / Evidence 錯誤後，衍生 Knowledge、進行中 Plan / Action 如何處置無規定（有煙霧探測器、無灑水系統） | 1/7 | major | **ACCEPT**（P2 ENFORCE 增補失效反應義務三款；污染追蹤機制 DEFER） |
| 20 | 自然人表徵邊界缺失：Reality First 無邊界可被引用來正當化全面監控；合規 vs 功能無優先序 | 1/7 | major | **ACCEPT**（一句 Bounded Representation 條款；具體法規 DEFER） |
| 21 | 條款無編號系統、無 Normative / Informative 標注、無引用格式與編號穩定性規則，下層文件無法精確引用、合憲檢查無法自動化 | 2/7 | major | **ACCEPT**（PA / P{n}.E{m} / EV.x / F1–F6 編號 + [N]/[I] 標注 + 引用格式） |
| 22 | 封閉列舉必然過時：十類資料來源、三類 Evidence、13 項 Identity 類型清單屬 Layer 2 taxonomy，寫死在 Layer 0 | 2/7 | major | **ACCEPT**（改開放式「包括但不限於」，清單收斂為類別名，例示下放） |
| 23 | Learning → Reality 箭頭概念錯置：改變 Reality 的是 Action，Learning 改變的是 Representation / Knowledge；單迴路誤導下層把學習實作成世界狀態寫入 | 2/7 | major | **ACCEPT**（改為因果迴路 + 認知迴路雙迴路圖） |
| 24 | 自反性缺失：Agent / Model / Augur 自身不在 Identity 類型中，Action 發起者無法在世界模型內歸責；系統改變世界卻不表徵自己 | 2/7 | major | **ACCEPT**（Identity 類型加入 Agentive Entity + 一句自反性條款） |
| 25 | §6「Reality、Identity、Evidence 不會改變」與 P1「Reality 包含變化」矛盾；§6 三項 vs §7 四項清單不一致 | 2/7 | minor | **ACCEPT**（統一四概念清單；改寫為「原則不變，世界會演化」） |
| 26 | 禁令形式不對稱：P1 缺「沒有 Reality referent，不允許 Representation」第四條禁令 | 1/7 | minor | **ACCEPT**（補齊四條禁令一一對應四原則） |
| 27 | 中英混用無規則、未聲明權威語言版本；「必須／不得／應／得」約束力等級未定義；金句無結構地位 | 1/7 | minor | **ACCEPT**（風格規則 + 權威語言聲明 + 規範用語等級；併入 §0） |
| 28 | 「不再加入額外原則」與 §7 可修訂性矛盾，該句自身位階不明 | 1/7 | minor | **ACCEPT**（改為「非經 §8 程序不再加入」，標注為編纂性註記） |
| 29 | 暫時豁免機制缺失：無合法豁免通道的憲法會被沉默違反；不可豁免核心只能定義在 Layer 0 | 1/7 | — | **ACCEPT**（最小條款併入 §8：有期限、公開登錄、附補正計畫；PA 與追溯義務不可豁免；期限等細則 DEFER） |
| 30 | Identity 未區分 instance / type（continuant / occurrent），「這是關於誰」可被平凡滿足；同一性判準未要求 | 2/7 | minor | **DEFER**（v1.1 只留一句掛鉤：「Knowledge 必須明示繫結對象屬個體或類型；判準由 Layer 2 / Layer 3 定義」） |
| 31 | 來源信任分級（Trust Class 分級表：attested-instrument / authoritative-record / …） | 1/7 | — | **DEFER**（分級表屬 Layer 4；Layer 0 已以「信任不可洗白 + synthetic 標記」條款守住原則面，見 #11） |
| 32 | 新增兩條獨立原則：Human Primacy（P5）＋ Bounded Action（P6） | 1/7 提案 | — | **REJECT**（合併為單一 P5，見裁決 C1） |
| 33 | Fallibilism / Correction Before Certainty 升格為獨立第五原則 | 2/7 提案 | — | **REJECT 作為獨立原則**（內容全數採納，但降為 PA 釐清句 + P4 ENFORCE 條款，見裁決 C2） |
| 34 | Knowledge 必備屬性由五項增為六項（加 Provenance / Trust Class 欄位） | 1/7 提案 | — | **REJECT**（避免欄位級過度規定，見裁決 C5） |
| 35 | 在 Layer 0 為 Truth 給出正式定義 | 1/7 提案 | — | **REJECT**（採對案：刪除 Truth 一詞，見裁決 C6） |
| 36 | 治理組成細節寫入 Layer 0（三人審查體、180 天重新認證期、12 個月豁免上限等具體數字） | 2/7 提案 | — | **REJECT**（Layer 0 只設「角色與義務」，組成與數字下放治理附則，見裁決 C7） |

**合併統計：** 顧問原始 issues + missing elements 共 76 項，去重合併為 36 項議題。
ACCEPT：27　|　ACCEPT-AS-APPENDIX：1　|　DEFER：2　|　REJECT：5。

---

## 二、裁決紀錄（衝突與理由）

### C1. 極簡收斂 vs 行動治理擴張（最大衝突）
- **衝突**：AI 治理與安全視角要求新增兩條原則（Human Primacy、Bounded Action）外加 Action Schema、Fail-safe、表徵邊界等多項條款；文檔與哲學視角則強調「不再加入額外原則」的極簡自律是十年存活的必要條件。
- **裁決**：**只新增一條原則** —— P5「Accountability Before Action（可歸責先於行動）」，將 Human Primacy（授權鏈根節點必須是人類權威）、行動與不可逆性成比例（proportionality）、最小權限精神、Action 歸責結構全部收納為 P5 的 Definition / WHAT / WHY / ENFORCE 四段。
- **理由**：(1) 行動治理是四原則體系唯一「真正的結構性缺口」——§3 演化模型明載 Action 改變 Reality，但四原則全是認識論約束，這個缺口無法由既有原則推導補足，符合「新原則必須是 Layer 0 級且十年不變」的唯一入場資格（物理行動的不可逆性與人類為信任主體，十年不變）；(2) 它可完全用既有詞彙表述（行動者是 Identity、授權是可追溯 Evidence），是體系的閉合而非異物；(3) 拆成兩條原則沒有增加約束力，只增加條目數，違反極簡哲學。Prime Axiom 的 trustworthy 一詞已預設人類信任主體 —— P5 是把原作者的隱含前提顯性化。

### C2. Fallibilism / Temporality 升格為原則 vs 降為條款
- **衝突**：哲學視角提議「Correction Before Certainty」為第五原則；知識工程視角提議雙時間性為原則級條款；vs 極簡哲學。
- **裁決**：**全部內容採納，但不設新原則**。可謬性寫入 Prime Axiom 的釐清句（「faithfully 不意謂完美鏡像」）；supersession、矛盾保存、雙時間性、Confidence 語義寫入 P4 ENFORCE 的編號條款；defeasibility 寫入 P2。
- **理由**：這些是既有原則的「兌現條款」而非新公理 —— Confidence、Timestamp、Feedback/Learning 都已出現在原文中，作者直覺已多次觸及，只需收斂為顯性條款。哲學視角自己也承認「這不是新增異質內容，而是把已散落文中的隱性承諾收斂」——收斂到條款即可，不必占用原則名額。P5 已用掉唯一的新原則配額（C1），一次增加兩條以上原則會實質改變文件性格。

### C3. §4 的處置：刪除 vs 附錄 vs 下放
- **衝突**：各視角分別建議整節刪除、改非約束附錄、下放 Layer 1/7。
- **裁決**：**六個抽象角色留在正文（規範性）；產品名降為非約束性附錄 A**。
- **理由**：多位顧問一致確認「六個角色確實可從原則推出」，是憲章級架構承諾；產品選型則是 §7 自己承認可變的內容。此處置同時修復 §4/§6/§7 矛盾三角，且完全執行原作者 §6 自己宣示的技術中立 —— 是把作者意圖執行徹底，不是改變意圖。

### C4. Amendment 判準：「更完整描述」vs「失效證據」
- **衝突**：原文判準為認識論完整性比較（不可判定、且循環 entrenchment）；治理修訂視角提議改為「可檢驗的失效證據」；治理安全視角提議擴充判準納入安全性。
- **裁決**：採**失效證據制**：修訂案必須附（a）現行原則在具體案例中失效或產生矛盾的書面 Evidence，（b）新舊對照與全下層衝擊分析，（c）審查權威以最高門檻議決。Prime Axiom 明定為**永恆條款（Eternity Clause）**，不受任何修訂程序變更 —— 把現況隱性的循環 entrenchment 轉為明示設計。
- **理由**：「修憲本身適用 Evidence Before Conclusion」是原作者哲學的反身應用，最忠於原文精神；不採「擴充判準納入安全」——P5 入憲後，安全性修訂自然落入「原則失效證據」的一般通道，不需特設判準。

### C5. Knowledge 五元組：欄位級過度規定 vs 保留
- **衝突**：架構視角指出五元組是全文唯一欄位級規定（過度規定），建議改述為問題式；多位顧問又盛讚五元組是「十年穩定的不變式」；韌性視角更要求加第六欄位 Trust Class。
- **裁決**：**保留五元組**（它是文件的識別性資產與最強不變式），但補兩句：「欄位設計屬 Layer 4；本五元組為『任何 Knowledge 必須能回答的五個問題』之最低不變式」與「Confidence 必須全系統可比較、其評定方法可追溯」。**拒絕第六欄位**：信任語義以「遞迴溯源 + 不可洗白 + synthetic 標記」條款承載（原則面），分級表下放 Layer 4。
- **理由**：加欄位是用「更多 schema」解決「原則缺口」，方向錯誤；一旦開了加欄位先例，五元組會在十年間膨脹成表單。

### C6. Truth 一詞：定義 vs 刪除
- **衝突**：架構視角要求定義 Truth；文檔視角建議刪除、改寫禁令。
- **裁決**：**刪除 Truth**，禁令改寫為「Model output 不得未經 Observation → Evidence 通道直接成為權威 World Representation 或 Knowledge」。
- **理由**：極簡哲學下，少一個未定義初始概念優於多一個定義；改寫後禁令的判定條件（是否經過通道）反而更可稽核。

### C7. 治理機構具體化程度
- **衝突**：顧問分別提議單一 Constitution Steward、三人審查體、明定 180 天認證期 / 12 個月豁免上限等。
- **裁決**：Layer 0 只規定**角色與義務的存在**：「必須存在唯一之人類憲章權威（Constitution Steward，得為個人或審議體），持有解釋權、違憲審查權與修憲裁決權；Agent 不得參與修憲與解釋」。組成方式、人數、期限數字全部下放至治理附則（可依較低門檻修訂）。
- **理由**：「需要一個裁決主體」是 Layer 0 命題（Kompetenz-Kompetenz 無法由下層自我授予）；「主體長什麼樣子」是組織設計，十年內必變，寫入即違反穩定性判準。

### C8. 封閉宣告「不再加入額外原則」
- **衝突**：該句與 §7 可修訂性矛盾；但它承載作者的極簡意志。
- **裁決**：改寫為「任何原則之增修悉依 §8 程序辦理；非經該程序不再加入額外原則」，標注為編纂性註記 [I]。封閉改為**受控封閉**。
- **理由**：保留極簡意志，消除自相矛盾；一份無法合法演化的憲章活不過自己設定的壽命。

### C9. instance / type 與上層本體
- **衝突**：知識工程視角要求 continuant / occurrent 區分與同一性判準；極簡哲學反對在 Layer 0 展開分類學。
- **裁決**：**DEFER with hook** —— P3 加一句：「每類 Identity 必須宣告其同一性判準；Knowledge 必須明示繫結對象屬個體（instance）或類型（type），分類體系由 Layer 2 Ontology 定義」。
- **理由**：一句話守住邊界（防止「這是關於誰」被平凡化），分類學本身正是 Layer 2 的存在目的。

### C10. 演化鏈唯一權威版本
- **衝突**：三條鏈各有支持文脈（§1 修辭簡潔、P2 ENFORCE 操作性、§3 完整）。
- **裁決**：§3（v1.1 之 §4）為唯一 canonical chain，節點編號 EV.1–EV.12；§1 與 P2 ENFORCE 改為「節選引用（EV.x–EV.y），節選不得跳過中間節點」——P2 的鏈**必須補回 Identity**。
- **理由**：文檔視角正確指出 P2 現行鏈是「對 P3 的成文豁免」，屬 critical 級內傷；canonical + 節選是修辭與嚴謹兼得的最小修法。

---

## 三、v1.1 具體修改指令清單（給起草人）

### 3.0 新版目標結構（目錄）

```
《Augur Meta-Constitution v1.1》
§0  Document Status & Conventions [N]
    0.1 名稱、層級、版本、生效日、批准記錄
    0.2 規範用語約定（必須=MUST／不得=MUST NOT／應=SHOULD／得=MAY）
    0.3 條文效力標注規則（[N] Normative / [I] Informative）與條款編號穩定性
    0.4 權威語言聲明（中文版為權威，英文對照供參考）
    0.5 適用範圍：Layer 1–7 與規格對照表（單一權威清單，每份規格恰屬一層）
    0.6 Hierarchy Rule（層級語意 = constrains；lex superior；概念層不得引用執行層作定義依據）
§1  Supreme Purpose — Prime Axiom [N]（永恆條款）
    1.1 Prime Axiom（原文保留）＋ faithfully 釐清句
    1.2 標準鏈引用（節選 §4 之 EV.1–EV.6）
    1.3 四條對稱禁令（一一對應 P1–P4）
§2  Definitions [N]（約 10 條，一句一詞 + 下層不得重定義元規則）
§3  Five Immutable Principles [N]
    P1 Reality First（修訂）
    P2 Representation Before Intelligence（修訂）
    P3 Identity Before Knowledge（修訂）
    P4 Evidence Before Conclusion（修訂）
    P5 Accountability Before Action（新增）
§4  World Evolution Model [N]（canonical chain EV.1–EV.12、雙迴路、Human Authority Gate）
§5  Architectural Roles [N]（六抽象角色，無產品名）
§6  Forbidden Design Patterns F1–F6 [N]（含交叉引用）
§7  Long-Term Stability Rule [N]（修訂）
§8  Conformance, Interpretation & Amendment [N]
    8.1 Constitution Steward（解釋權與違憲審查）
    8.2 違憲後果與層間衝突優先序
    8.3 合規聲明義務與可判定性元規則
    8.4 暫時豁免與不可豁免核心
    8.5 Amendment Procedure（提案／議決／記錄）＋ Eternity Clause
    8.6 版本語義、引用格式、編號穩定性
§9  Final Statement [I]
Appendix A [I]  v1.x 參考技術選型對照（非約束、不受穩定性保證）
Appendix B [I]  憲章金句（記憶錨點）
```

### 3.1 §0 Document Status（修改）
1. 加入 0.2–0.4 三條規則（規範用語等級、[N]/[I] 標注、權威語言為中文）。
2. 將 13 項規格清單改為 **Layer 對照表**：每份規格標明所屬 Layer（例：Layer 7 = External Interface Layer + Database Architecture + Infrastructure Deployment；Data Intelligence Layer → Layer 4；AI Model Selection → Layer 5/7，由起草人裁定並凍結）。「MCP Interface Layer」更名為「External Interface Layer」。
3. 新增 Hierarchy Rule 三款：(a) 編號較小之層對較大之層具規範效力，牴觸者無效；(b) Layer 1–4（概念層）規格不得引用 Layer 5–7（執行層）構件作為定義依據；(c) 層級圖箭頭語意標注為 constrains。

### 3.2 §1 Prime Axiom（修改）
1. Prime Axiom 原句一字不動保留；標題由「唯一公理」改為「Prime Axiom（最高使命）」，刪除「四原則由公理推導」的修辭，改為「四大原則與 P5 為本使命之不可違反展開」。
2. 增補釐清句：「忠實（faithfully）不意謂完美鏡像。Representation 永遠是帶不確定性的近似；忠實性體現於：不確定性可追溯、錯誤可被新 Evidence 修正（詳 P4.E）。」
3. 演化鏈圖刪除，改為引用：「世界演化標準鏈見 §4（EV.1–EV.12）；本節速記為其節選 EV.1–EV.6。」
4. 三條禁令補為四條、標明對應：
   - 沒有 Reality 對應（referent），不允許 Representation。（P1）
   - 沒有可靠 Representation，不允許 Intelligence。（P2；「可靠」定義為：滿足 P1–P4 全部 ENFORCE 條款者）
   - 沒有 Identity，不允許 Knowledge。（P3）
   - 沒有 Evidence，不允許 Conclusion。（P4）

### 3.3 §2 Definitions（新增專章）
每詞一句內涵式定義（草案，起草人可潤飾但不得增加概念數）：
- **Reality**＝獨立於任何系統而存在的世界事物、狀態、事件與變化之總和；含 Augur 自身及其 Agent、Model 與 Action（自反性條款）。
- **Observation**＝對 Reality 的一次有 Source、有 Timestamp 的量測或記錄。
- **Representation**＝以共同世界模型對 Reality 所作的一致、可追溯、可演化之結構化描述；每一世界事實在系統內有唯一權威表徵（語義唯一性，不預設集中式拓撲）。
- **Identity**＝對一個世界實體唯一且持續的指稱；區分 identifier（系統鑄造之永久參照）與 identity claim（「兩個 identifier 指涉同一實體」之斷言，本身為受 P4 約束之 Knowledge）。
- **Evidence**＝被引用以支持某項 Knowledge 之 Observation 或推導結果（角色關係，非階段先後）。
- **Knowledge**＝繫結 Identity、由 Evidence 支持、附 Confidence、繫結成立時間、可被推翻（defeasible）之斷言。
- **Intelligence**＝基於 Representation 產生新斷言或行動方案之任何過程（含檢索、推論、規劃）。
- **Agent**＝經授權讀寫世界模型並執行 Action 之自主程序；Agent 為 Identity 之一種（Agentive Entity）。
- **Action**＝由可歸責 Identity 發起、意圖改變 Reality 之事件。
- **Confidence**＝對 Knowledge 為真之程度之可量化表述；其語義由 Layer 4 以單一形式化定義，全系統一致。
- 元規則：「下層文件不得重新定義本章術語，僅得細化。」

### 3.4 §3 五大原則（逐條修改指令）

**P1 Reality First**
1. ENFORCE 十類來源清單改開放式：「任何對 Reality 的觀測通道——無論當前是否存在——皆屬資料來源，包括但不限於：ERP、MES、Sensor、Document、External Knowledge（例示減半）。」
2. 「必須映射至共同世界模型」改為：「必須映射至共同世界模型之語義：每一世界事實有唯一權威表徵，Identity 必須可跨部署邊界解析與對齊；集中或聯邦拓撲屬下層部署決策。」
3. 新增 Bounded Representation 條款（P1.E 末）：「對自然人之 Observation 與 Representation，受目的正當性、授權與所在法域法律義務約束。忠實表徵 Reality 不構成無限觀測之依據；合規義務與功能衝突時，合規優先。」

**P2 Representation Before Intelligence**
1. 增補權威順序釐清（P2.W）：「本原則規範權威順序，非時間順序。AI 得參與 Representation 之建構（identity resolution、抽取、映射），但其輸出僅得以附帶 Evidence 與 Confidence 之候選斷言（proposed assertion）進入系統，經 Observation → Evidence 通道確立後方成為 Representation 之一部分。」
2. ENFORCE 禁令改寫：
   - 「Model output 直接成為 Truth」→「Model output 不得未經 Observation → Evidence 通道直接成為權威 World Representation 或 Knowledge」（刪除 Truth 一詞）。
   - 「Agent 自行創造世界狀態」→「Agent 不得繞過 Observation → Evidence 通道，將其意圖、預期或未經證實之執行結果直接寫入 World Representation 作為世界狀態。Action 之影響必須以 Observation 之姿回流（Agent 之 execution receipt 與外部確認訊號皆屬合法 Observation，Source 為該 Agent 之 Identity）。」
   - 新增：「禁止 Representation 被視為 Reality 本身——任何 Representation 元素必須保留其 Observation 來源與不確定性。」
3. ENFORCE 之標準鏈改為節選引用並**補回 Identity**：Observation → Representation → Identity → Evidence → Knowledge（標注「§4 之 EV.2–EV.6 節選」）。
4. 新增 Fail-safe 條款（P2.E 末）：「當任何 Representation 或 Evidence 被判定錯誤或撤回：(a) 衍生之 Knowledge 必須標記並重新評估；(b) 依賴之進行中 Plan / Action 必須暫停；(c) 受影響範圍內系統降級為觀測與建議模式，直至修復。污染追蹤機制由 Layer 4–6 定義。」

**P3 Identity Before Knowledge**
1. 13 項實體清單收斂為：「Identity 涵蓋 Physical、Abstract、Dynamic 與 **Agentive**（AI Agent、Model、作為決策者之 Human）四類實體；完整分類由 Layer 2 Ontology 定義。」（例示各留 2–3 個，加「包括但不限於」。）
2. ENFORCE 修正自舉死鎖：「所有 Knowledge、Relation、Goal、Constraint、Capability、Plan、Action 必須引用已解析之 Identity。所有 Observation 必須攜帶可供 Identity Resolution 之指涉資訊，得先以未解析（provisional identity）狀態進入系統；未解析之 Observation 不得升級為 Knowledge，且系統負有解析義務。」
3. 新增 Identity Lifecycle 條款：「identifier 一經鑄造（mint）永不刪除，僅可重導向（redirect）。Identity 之 merge / split / retire 與更正，本身為必須引用 Evidence 之 Knowledge，全程保留可追溯歷史（identity lineage）。Identity 存續跨越任何 Ontology / Representation 變更。」
4. 新增掛鉤句（DEFER hook）：「每類 Identity 必須宣告其同一性判準；Knowledge 必須明示繫結對象屬個體（instance）或類型（type），判準與分類由 Layer 2 / Layer 3 定義。」
5. Definition 之「這是關於誰？」改為「這是關於哪一個 Identity？」。

**P4 Evidence Before Conclusion**
1. 五元組結構圖**保留原樣**，其後加註：「此為任何 Knowledge 必須能回答之五個問題（來源為何／何時成立／關於哪個 Identity／依據為何／多可信）之最低不變式；欄位設計屬 Layer 4。」
2. Evidence 三分類加開放語句「包括但不限於」，例示各砍至 2 個；分類法維護權下放 Layer 4。
3. ENFORCE 新增編號條款：
   - **P4.E-Time（雙時間性）**：「任何 Observation 與 Knowledge 必須區分 valid time（何時為真，可為區間）與 transaction time（系統何時得知）。系統必須能重建任一過去時刻之認識狀態（as-of）。Timestamp 為 Knowledge 有效性宣稱之一部分，非元資料裝飾。實作機制屬 Layer 4 以下。」
   - **P4.E-Supersede（只失效不刪除）**：「Knowledge 與 Evidence 不得刪除，僅得標記為 superseded / retracted / invalidated；失效為需要 Evidence 之知識行為，全歷史保留。唯一例外：法規強制抹除得刪除內容本體，但必須保留 tombstone 及刪除事件自身之完整 provenance。」
   - **P4.E-Defeasible（可謬性）**：「所有 Knowledge 皆可被新 Evidence 推翻；Confidence 不得為隱含之 1.0；任何 Knowledge 不得標記為不可修正。」
   - **P4.E-Conflict（矛盾保存）**：「互相衝突之 Evidence 必須共存並顯式標記，不得靜默消滅（禁止 last-write-wins）。衝突之裁決為推理行為，其結論為攜帶自身 Evidence 與 Confidence 之新 Knowledge，永不覆寫原始證據。『目前證據不足』為合法且必須可表達之系統狀態。」
   - **P4.E-Provenance（遞迴溯源）**：「Evidence 為一級物件，自身必須可溯源：記錄斷言主體（agent，含版本）、產生活動（含輸入與參數）、上游依據。證據鏈必須遞迴終止於對 Reality 之 Observation 或明示宣告之假設。禁止循環引證。」
   - **P4.E-NoLaundering（信任不可洗白）**：「衍生證據之信任不得高於其上游最弱來源；結論之 Confidence 上限受證據鏈最弱環節約束；AI 生成／合成內容永久攜帶 synthetic 標記，不因轉引而消失。高風險 Action 之結論不得僅以系統自身產出之證據為依據，須至少一項獨立 Data Evidence 或人類確認。」
   - **P4.E-Confidence（語義與消費）**：「Confidence 語義必須於 Layer 4 以單一形式化定義、全系統可比較、評定方法可追溯；Confidence 必須沿推理鏈向下游傳播，Action 之允許等級受其依據 Knowledge 之最低 Confidence 約束。」

**P5 Accountability Before Action（新增，唯一新原則）**
四段式起草：
- **Definition**：改變 Reality 或 World Representation 的任何 Action，必須先回答：「誰發起？誰授權？憑什麼知識？」
- **WHAT**：(1) 任何 Action 必須可歸責於單一 Identity（人或 Agent）；(2) 授權鏈（chain of authority）之根節點必須是人類權威——人類得在任何時點否決、暫停或中止任何 Plan 與 Action；(3) Action 之權限與其不可逆性成反比：不可逆或高影響之實體世界 Action 需最高等級之 Evidence 完備性、Confidence 門檻與人類事前核准；(4) Agent 僅持有完成當前經授權 Plan 所需之最小權限；(5) 系統不得規劃、執行或學習任何降低人類監督與否決能力之行為。
- **WHY**：四大原則保證「知識是對的」，不保證「行動是安全的」——後果可逆性與損失不對稱性獨立於知識品質。預測錯了可修正 Knowledge；行動錯了收不回一爐報廢的晶圓。技術會變，物理行動之不可逆性與人類作為信任主體不會變。
- **ENFORCE**：任何 Action 必須具有：Actor Identity、Authorization（可追溯至人類權威之授權鏈）、Knowledge Basis、Timestamp、Expected Effect、Observed Effect（連結 Feedback）。風險分級表與核准流程由 Layer 6 Agent Runtime 定義；External Interface（§5 角色六）為行動分級之執法點。

### 3.5 §4 World Evolution Model（修改）
1. 宣告為唯一 canonical chain，節點編號 EV.1 Reality … EV.12 Learning；其他章節引用一律標注節選、不得跳節點。
2. 迴圈改雙迴路：**因果迴路** Action → Reality（經 Observation 重新進入）；**認知迴路** Feedback → Learning → Representation / Knowledge（Learning 不再指回 Reality）。
3. Planning 與 Action 之間標注 **Human Authority Gate**（P5 之圖示落點）。

### 3.6 §5 Architectural Roles（改寫，原 §4）
整節改為六個抽象角色（規範性），刪除所有產品名：
1. World State System of Record（權威世界狀態；append-only 與 provenance）
2. World Relationship Representation（關係、因果、依賴）
3. Semantic Memory（語意相似性與脈絡檢索）
4. World Understanding Engine / Cognitive Kernel（推理、假設、解釋）
5. World Action Layer / Agent Runtime（規劃、執行、回饋）
6. Controlled External Interface（世界模型與外部系統之受控介面；P5 行動分級執法點）
產品對照（PostgreSQL、Neo4j、Vector DB、MCP）移至 **Appendix A [I]**，標注「非約束性、屬 Layer 7 現行選型、可隨時代更換、不受本憲章穩定性保證」。

### 3.7 §6 Forbidden Design Patterns（修改，原 §5）
1. 編號改為 F1–F5，各加交叉引用（如 F4 Knowledge Without Identity ——違反 P3.E）。
2. 新增 **F6 Unaccountable Action**：禁止任何無法回答「誰發起、誰授權、憑什麼知識」之 Action（違反 P5.E）。
3. F2 中「LLM」改為「AI model」（去時代印記）。

### 3.8 §7 Long-Term Stability Rule（修改，原 §6）
改寫為：「技術會改變；Reality 會演化、Identity 會演化。但『忠實表徵 Reality、以 Identity 錨定知識、以 Evidence 支撐結論、以 Representation 先於智慧、以人類權威歸責行動』——這些原則不會改變。」不變核心清單統一為與原則一一對應（Reality / Representation / Identity / Evidence / Accountability），§8 修憲判準引用同一清單。

### 3.9 §8 Conformance, Interpretation & Amendment（新章，吸收原 §7）
- **8.1** 設 Constitution Steward（人類；得為個人或審議體，組成屬治理附則）：持有條文最終解釋權、規格違憲審查權、修憲裁決權；Agent 不得參與。解釋裁決書面化、附理由、公開存檔、對後續案件具拘束力（解釋先例）。
- **8.2** 違憲後果：經認定違憲之條款自認定日起無效，不得作為下層依據；既有實作予明定補正期（個案裁定），期滿未補正停用；同位階條款衝突視為文件缺陷，修正前採較嚴格解讀；Normative 與 Informative 不一致時以 Normative 為準。
- **8.3** 合規聲明義務 + 可判定性元規則：每份 Layer 1–7 規格必須內含 Constitutional Compliance Statement（聲明合規版本、逐原則合規論證、已知緊張關係揭露），無聲明不生效力；憲章評價性謂詞（reliable / faithful / trustworthy）被下層引用時，該規格必須同時給出可判定判準，判準未給前採保守解釋（存疑即不允許）；ENFORCE 條款之核心不變量（Knowledge → Evidence → Observation 引用鏈完整性、Action 之 Identity 歸因）必須可機器稽核。
- **8.4** 暫時豁免：Steward 得對非核心條款核發有明確到期日之書面豁免，公開登錄、附補正計畫；**不可豁免核心**：Prime Axiom 與 Evidence 追溯義務——豁免期間產生之知識仍須標記豁免狀態與證據缺口。
- **8.5** Amendment Procedure：(a) 提案權——受本憲章約束之任何規格作者得書面提案，載明擬修條文、新條文、與現行原則失效之書面 Evidence；(b) 議決——原則級修訂由 Steward 以最高門檻議決，附則採較低門檻；§8 自身之修訂適用原則級門檻（self-entrenchment）；(c) 記錄——新版本號 + 修訂理由書 + 生效日，登錄 Amendment Log。**Eternity Clause**：Prime Axiom 不受任何修訂程序變更。
- **8.6** 版本語義與引用：原則級實質變更 = major（觸發全下層合憲複審）；附則與 Informative 變更 = minor；編輯修正 = patch。下層引用格式「AUGUR-MC v{version} §{條款編號}」（如 §P1.E2）；條款編號一經發布永不重用、永不重排，廢止條款保留編號標注 (repealed)。憲章 major 升版時既有規格進入重新認證期（期限由 Steward 裁定），期內效力延續。

### 3.10 §9 Final Statement 與結尾（修改）
1. Final Statement 標注 [I]，四句口號補為五句（加 Accountability Before Action）。
2. 定稿結構圖：Layer 7 更名「External Interface / Infrastructure」；箭頭標注 constrains。
3. 結尾句改為：「本版（v1.1）編纂者判斷已收斂至最小核心；任何原則之增修悉依 §8 程序辦理，非經該程序不再加入額外原則。」標注 [I]。

### 3.11 全文編輯規則
1. 條款編號：PA；P{n}.D / P{n}.W{m} / P{n}.Y / P{n}.E{m}；EV.1–EV.12；F1–F6。
2. 每節標題標注 [N] / [I]；WHY 段一律 [I]。
3. 規範性術語正文一律用英文原詞（「真實世界」→ Reality）；章節標題「English（中文）」格式。
4. 任何出現於 ENFORCE 或 F 條款之名詞必須在 §2 Definitions 有條目。
5. 金句以引言格式錨定於各原則 WHY 段（Appendix B 彙整）：「智慧是：真實世界被正確表徵後，自然產生的能力」「AI 最大風險不是能力不足，而是對錯誤世界產生高度合理的智慧」「資料結構不是世界結構」「沒有 Evidence：AI 只是在生成可能性，不是理解」「當世界被正確表徵，智慧自然產生」。
6. 清單超過 5 項即收斂並下放；P1 WHY 舉例與 §8（原文）重複內容砍半。

---

## 四、明確不做的事（REJECT 清單與理由）

| # | 被拒提案 | 提出視角 | 拒絕理由 |
|---|---|---|---|
| R1 | 新增兩條獨立原則（Principle 5 Human Primacy ＋ Principle 6 Bounded Action） | AI 治理與安全 | 內容全數採納，但合併為單一 P5 Accountability Before Action。拆為兩條不增加約束力、只增加條目數；原則數量是極簡哲學的第一防線。人類權威與行動有界在邏輯上同根（授權鏈根節點為人類 ⟹ 不可逆行動需人類核准），一條原則可完整承載。 |
| R2 | Fallibilism / Correction Before Certainty 升格為獨立第五原則 | 邏輯與哲學、系統架構 | 內容全數採納但降為條款（PA 釐清句 + P4.E-Defeasible / Supersede / Conflict / Time）。可謬性是既有原則的兌現而非新公理——Confidence、Timestamp、Learning 已在原文中，收斂為條款即足；新原則名額唯一，讓給體系真正缺口（行動治理）。 |
| R3 | Knowledge 必備屬性五項增為六項（Provenance / Trust Class 欄位） | 十年演化韌性 | 用加欄位解決原則缺口是方向錯誤，且開啟五元組十年膨脹的先例。信任語義以 P4.E-Provenance ＋ P4.E-NoLaundering 兩條原則級條款承載；分級表（trust class taxonomy）DEFER 至 Layer 4。 |
| R4 | 在 Layer 0 為 Truth 給出正式定義 | 系統架構 | 採文檔視角之對案：刪除 Truth 一詞、禁令改寫為「不得未經 Observation → Evidence 通道成為權威 Knowledge」。極簡哲學下，少一個初始概念優於多一個定義，且改寫後禁令更可稽核。 |
| R5 | 治理組成與數字細節寫入 Layer 0（三人審查體、180 天重新認證、12 個月豁免上限等） | 治理與修訂、AI 治理與安全 | Layer 0 只規定角色與義務之存在（Steward、豁免須有期限、複審期由 Steward 裁定）；人數與天數屬組織設計，十年內必變，寫入即違反 §7 穩定性判準。細節下放治理附則（minor 門檻可修）。 |

（另有兩項 DEFER：instance / type 分類與同一性判準 → Layer 2 / 3，v1.1 僅留 P3 掛鉤句；來源信任分級表 → Layer 4，v1.1 僅留不可洗白原則。）

---

## 附：優先度說明

若起草資源受限，依「共識度 × 不可逆風險」排序，前五項為必改：
1. §4 技術品牌抽象化 + 附錄降級（7/7 共識，文件權威性根基）
2. 統一演化鏈 + 修復 Identity / Representation 雙自舉（critical 級邏輯內傷，P2 現行鏈是對 P3 的成文豁免）
3. §8 治理章（修憲程序、解釋權、違憲後果——沒有司法機制的憲法只是散文）
4. P4 ENFORCE 六條新條款（雙時間性、只失效不刪除、矛盾保存、遞迴溯源、不可洗白、Confidence 語義——可追溯性的實質內容）
5. P5 Accountability Before Action（體系唯一結構性缺口：認識論完備、行動論空白）

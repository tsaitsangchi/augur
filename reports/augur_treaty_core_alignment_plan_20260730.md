# 治權檔對核稽核與優化計畫（2026-07-30）——以「世界建構核心」為量尺

> **緣起**：hugo 指示「依全專案說人話報告書，重新檢視此專案所有的憲章、精神、原則、計畫，進而進行對應的優化以符合 augur 的核心」，並於同一輪追加二則方向指示：「**不要在憲章強調股市**」、「**『日線是一個域的選擇』這樣的說明還是被限制在股市了**」。
>
> **判準（#20 比例原則）**：本案兼含（a）純機械改正確與（b）治權判準修訂，故切兩軌——**(a) 我自辦並即刻執行；(b) 一律呈 Steward 拍板，我只提議措辭、不擅改、不代簽**（CLAUDE #14／#19／#26；MC §8.1「Agent 不得參與修憲與解釋」）。
>
> **誠實界限（先講清楚我不做什麼）**：本檔中凡標「疑義」者，是**呈請 Steward 判斷之規範緊張**，不是我的違憲認定——依 MC §8.1，元憲章之解釋權不在 Agent。我只負責把原文擺出來、把落差指出來、把可選措辭寫好。

---

## 一、量尺：核心六點（出自報告書 v11，其依據為 MC＋七規格原文）

1. **世界觀**：Augur 是「從零建構的世界」——L0 立法 → L1 世界由什麼構成 → L2 分類與同一性 → L3 個體身分與一生 → L4 說法如何可信 → L5 思考的合法性 → L6 行動治理 → L7 概念變成鐵。
2. **域中立**：第一域只是登錄域之一（P1.E1 觀測通道開放列舉；P3.W2 金融工具與工廠機器並列例示；WM.52 新域＝加附錄母法不動；刪名測試 WM.4／ONT.4／KS.4／L6.23／L7.4）。**路屬世界，足跡屬域。**
3. **一條路**：候選 → 證據通道（可證偽／樣本外／實效終審）→ 人類授權門 → 晉升或判死留檔 → 後果回流。八種行走者無特權通道。
4. **自反性法源鏈**：MC §2.1 → WM.26 → ONT T.28 → ID.11 → KS.75–77 → L6.4／L6.19 → L7.5 → MC §8.1。
5. **AI 位置釘死**：可生成候選、搬運原典、當評測引擎；不得寫入知識本身、不得自我背書、不得碰授權門與修法權。
6. **終審是實效與誠實**：非準確率、非漂亮；誠實的無能宣告與有效的能力宣告同為合法產出；回流即燃料。

## 二、稽核方法與射程（誠實標注）

| 輪次 | 手段 | 射程 |
|---|---|---|
| 一讀 | 8-agent：MC 定義章＋七規格「建構什麼／次序／缺了會怎樣」 | 已完成（`wf_5f9ed758-e56`） |
| 二讀 | 8-agent：同一批檔案換鏡頭抽「域中立普遍法則／多域條款原文／自反性條款原文」 | 已完成（`wf_a285a235-e54`） |
| 三讀 | 12-agent 對抗稽核：9 讀者（靈魂／原則精華／大憲章／CLAUDE／入口門面／根檔計畫／計畫報告群／L1-L4／L5-L7+MC）＋3 對抗驗證器（逐則駁） | 執行中（`wf_175c81eb-c2c`），結果補記於 §六 |
| 親驗 | 我本人 grep／逐字讀：版本行、死指標鏈、靈魂定義句、原則精華 #1 具名 | 已完成（本檔所引皆親驗字面值） |

**射程外（誠實）**：live DB 實際 schema 現況、CI 是否真掛稽核、41 份 RULING 全文逐份（僅按需引用）。

## 三、甲批・機械軌（已執行，不動任何判準）

### 甲-1 幽靈 v1.48.0 死指標鏈（5 處，commit `f189105`）

**根因**：`v1.47.0 →（A 新檔）→ v1.48.0 →（R 改名）→ v1.49.0`。因末段是改名而非新檔，**v1.48.0 檔案不復存在**，但四處仍指向它。

| # | 位置 | 原字面 | 已改為 |
|---|---|---|---|
| 1 | `README.md:30` 狀態行 | 憲章 v1.48.0・CLAUDE v1.29 | 憲章 v1.49.0・CLAUDE v1.31 |
| 2 | `README.md:42` 治權表連結 | `docs/系統架構大憲章_v1.48.0.md`（不存在） | `..._v1.49.0.md` |
| 3 | `HANDOFF.md:34,234` | 同上死路徑 ×2 | `..._v1.49.0.md`；並註「v1.48.0 入憲，現行 v1.49.0」 |
| 4 | `docs/系統架構大憲章_v1.47.0.md:3` SUPERSEDED 橫幅 | 指向不存在之 v1.48.0 | 明述「v1.48.0 檔續改為 v1.49.0，同一檔案沿革、無獨立檔」 |
| 5 | `docs/compliance/CS-系統架構大憲章_v1.48.0.md:6` 正文 SSOT | 指向不存在之正文 | 指向現行 v1.49.0 並標明本聲明僅覆蓋 v1.48.0 增量 |

**附帶親驗**：全 repo 治權連結掃描，除本鏈外**無其他真死指標**（`大憲章 v1.49.0:311` 之 `舊 reports/系統核心思想.md` 為明標「舊 repo」之史料引用，非死連結）。

### 甲-2 報告書去域錨（commit `b88691c`／`3b2a798`）

依 hugo 二則指示：刪除具名市場詞（「選股」等）；「最小時間粒度」例示改為「世界不規定時間該切多細，那是每個域依自己被觀測的方式決定」；「代號重用」改為「外部世界給的編號會被回收再發給另一個個體」。**全檔已無任何市場專名。**

### 甲-3 入口門面對齊上位 telos（本 turn 執行）

**現況**：`README.md:3`「只用真實資料、誠實預測台股」；`ARCHITECTURE-OVERVIEW.md`（自宣 [I] 非規範性）同軸敘事。
**問題**：門面以交付物定義專案，與報告書核心第 1／2 點不符；且 README 為 #19 所列治權檔，其敘述與 L0 永恆條款不同調。
**處置（保守解）**：門面**直引 L0 永恆條款**（lex superior，不創設新義務、不與現行靈魂措辭衝突），並補一句「域為足跡，法為世界」；**不動任何判準**。靈魂本身的定義句屬乙批、待拍板。

## 四、乙批・判準軌（呈簽；我不擅改、不代簽）

> 每案格式：現況原文（親驗）｜疑義｜建議措辭｜影響檔｜落地路徑。**一字拍板即可執行**（例：`乙1-照案`／`乙1-駁`／`乙1-改為…`）。

### 乙-1 靈魂定義句以交付物定義世界模型層

- **現況原文**（`docs/系統核心思想_v1.8.0.md`「一句話」）：「**Augur 是一套只用真實資料、誠實預測台股的系統。**」
- **疑義**：本檔經 RULING-2026-002／AL-2026-006 **登錄為 Layer 1（World Model）**，而 WM.7 明文「**世界模型必須優先描述 Reality，不得優先適配現有資料來源**」。以交付物（預測某域）為 Layer 1 文件之定義句，是否與其自身登錄層級之義務相張？**呈裁，不由我認定。**
- **建議措辭（供選）**：
  - **甲案（世界句＋域落點分節）**：一句話改為「**Augur 是一個以持續一致的身分與可追溯的證據忠實表徵世界、據以產生可信判斷的系統**」；原「它預測什麼」整節降為「**第一域落點（台灣市場）**」子節，內容不變、僅移位並加標「域宣告、非世界法律」。
  - **乙案（最小改）**：一句話保留原句，前置一行「上位目的：〔PA §1.1 原文〕；下句為第一域之落點」。
- **影響檔**：靈魂 v1.8.0→v1.9.0；README 治權表、`CS-系統核心思想_v1.8.0.md`、HANDOFF 判準列、大憲章「位階」段之引述。
- **落地路徑**：領域治權檔修訂（歷例＝hugo 對話拍板 → 我繕打升版並全鏈同步，標「hugo（對話拍板）〔claude 繕打，不冒充親簽 §8.1〕」）。

### 乙-2 原則精華 #1 以具名通道當「真實」之定義（刪名測試）　✅ **已拍板執行（hugo 2026-07-30「乙-2」）→ v1.11.0；留痕 `audits/PRIN-B2-DENAME-20260730.md`**

- **現況原文**（`docs/原則精華_v1.10.0.md` #1 WHAT）：「任一特徵值必須是「**真實 FinMind/FRED API 值**經數學轉換」而得」。
- **疑義**：本檔登錄 **Layer 4（Knowledge System）**，KS.4 要求「刪去產品／供應商名後條款概念內涵不變」方為合法指名。#1 刪名後「真實 API 值」失去所指，似以供應商定義「何謂真實」；**且新域之值不由該二通道供應時，#1 字面不覆蓋**。對照 #17 已寫「對 FinMind／FRED（**及任何 API**）」＝合法例示，故本案為單條落差、非全檔問題。
- **建議措辭**：WHAT 改為「任一特徵值必須是「**經登錄觀測通道之真實值**經數學轉換」而得（**現行通道清單 [I]**：FinMind／FRED；新增通道經 World Concept Registry 登錄）」，其餘（imputed／zero-fill／缺列不補）一字不動。
- **影響檔（已全部級聯）**：原則精華 v1.10.0→**v1.11.0**；`CS-原則精華_v1.11.0.md`（新增本版增量＋刪名測試自陳）；README／HANDOFF／CLAUDE.md／大憲章 v1.49.0／GOVERNANCE-MAP／AUD-02 設計檔共 11 行；`check_treaty_refs.py` 驗證全綠。
- **附帶**：另掃出 #17 等處為合法例示，**不需動**（避免無謂升版，#3 最小邊界）。

### 乙-3 「一條路」缺單一總則條文（報告書核心第 3 點之法源空懸）

- **現況**：MC §4 EV.1–12 立了知識與行動之演化鏈；GATE 預註冊、人閘三表、判死留檔各自成文；但**「凡欲在系統內取得地位者一律走同一條路」未有單一總則條**，八類行走者之適用清單亦無明文。
- **疑義**：報告書把此列為核心，若治權層無對應條文，則報告書該段屬**解釋性延伸**——須擇一：提案入憲，或報告降級為「詮釋」。
- **建議措辭（大憲章新增一條，草案）**：「**普遍晉升路徑**：凡欲於本系統取得任何地位（生產認知、永久知識、思想映射、能力宣稱、方法採用、模型晉升、程序採認、治權變更）者，一律經：候選 → 預先凍結判準之證據通道（可證偽／樣本外／實效終審）→ 人類授權門 → 晉升或**判死留檔** → 後果回流為新觀測。**無特權通道**；各類之具體門檻由其專章定之，但不得省略任一節點（承 `AUGUR-MC §4`／`§P4`／`§P5`）。」
- **影響檔**：大憲章 v1.49.0→v1.50.0；報告書 §四（改為引條文而非自述）。

### 乙-4 重演軌作用域判準之 SSOT 仍在計畫書（應升格入憲）

- **現況**：「replay-確立」作用域標籤、**live 門不吃 replay 樣本**、重演須斷言 `train_data_max_date == pred_date`——判準現住 `reports/augur_arena_replay_plan_20260729.md` 與 code（DB CHECK），憲章無條文。
- **疑義**：此為**宣稱等級之判準**（決定什麼數字能說「已確立」），依 #12 單一權威家與 P4 應住治權檔；計畫書非 SSOT 之合法住所。
- **建議措辭**：大憲章「輸出契約／宣稱等級」條增一子條：「歷史重演（replay）所得證據之作用域標籤為 `replay-確立`，**不得計入 live 門之樣本數**、不得與真未來賭注混算；重演須以機械斷言證明訓練資料上界不逾預測日。」
- **影響檔**：大憲章；arena／meta replay 兩計畫書（改為引憲章）。

### 乙-5 KH10「一律准入」與 P2.E1「禁 AI 直寫永久知識」之合憲性（第三次列帳）

- **現況**：大憲章 v1.48.0 起「知識一律准入＋漸進 KH」；元憲章 P2.E1 禁 AI 直寫永久知識。二者關係**無任何文件正面交代**。
- **建議處置（二選一）**：①我出**一頁合憲性分析**（列 KH10 各層與 P2.E1 之交集面、指出「原文入庫非 AI 生成」是否足以消解），呈裁；②直接在大憲章 KH10 條加一句「AI 於本機制中僅得搬運、切分、標記、檢索原文；**AI 生成內容永不入永久知識層**（承 P2.E1）」以文本閉合。
- **我的建議**：先做①（判準級不宜由我逕自「閉合」），②之措辭已備。

### 乙-6 CLAUDE.md 之 L6 義務標注（低急迫）

- **現況**：31 條工具規則中，#26（有界自主）、#14（commit 授權）、#28（配額護欄）實質承載 L6 之授權鏈／問責義務，但多數未標上位條號。
- **建議**：於各條末補「〔承 L6.x〕」引註（純補完整、不改義務內容）——但因涉治權檔逐條增修，仍列乙批供拍板；若你認為屬機械軌，我可即刻自辦。

## 五、丙批・防呆補完整（執行層，本 turn 執行）

**丙-1 治權交叉引用稽核器 `scripts/check_treaty_refs.py`**——甲-1 那類缺陷（版本行過期、指向已改名／不存在之治權檔、SUPERSEDED 橫幅指向幽靈版）目前**無任何機械閘**攔阻，全靠人眼。新增零依賴 lint：

- **職責**：掃 live 治權檔與根檔之 markdown 連結與版本字串 → 檢（a）被引用之 `docs/`／`constitution/`／`specs/` 路徑是否存在（排除散文通配符與明標「舊 repo」之史料）；（b）README／HANDOFF 之版本字串是否等於 `docs/` 現存最高版檔名；（c）每份 `SUPERSEDED` 橫幅之指標是否存在。
- **簽名**：`main(argv) -> int`（0＝全綠、非 0＝有缺陷）；`scan_dead_refs(files) -> list[Finding]`；`check_version_lines() -> list[Finding]`；`check_superseded_banners() -> list[Finding]`。
- **CLI**（#18／#29 要件）：無參數＝印指令矩陣並跑全掃（唯讀、graceful）；`--selftest`＝免 DB 免 API 之紅綠自測（以 tmp 造假樹驗三類缺陷各被抓到）；`--json`＝機器可讀輸出供 CI／pre-commit。
- **零 Claude usage**（#28 本地優先）；**不寫 DB**。

## 六、表與程式規畫（憲章第六部 v1.39.0 計畫完整性要件）

**(a) 表**：本案**不產新表**。所讀既有表：`governance_proposal`／`governance_queue`（人閘現況查詢，唯讀）。乙批各案若拍板，落地位置＝`docs/*.md` 治權檔正文＋`docs/compliance/CS-*.md`＋`audits/*-APPROVED-*.md` 留痕；若走人閘則另落 `governance_proposal`（三鎖：提案／審查／enacted 唯 hugo 親簽）。**本案不寫任何生產資料表。**

**(b) 程式**：新增 1 支（丙-1，規格見上）。既有工具之角色：`tools/constitution_lint`（條號／層級 lint，現有）、`scripts/deliberate.py`（機械可裁宣稱之本地審議，零 token）、`scripts/check_cmd_matrix.py`（矩陣稽核）——丙-1 與三者互補、不重疊（前者查**跨檔引用完整性**，三者分別查條號、宣稱、矩陣）。

## 七、分階段與驗收

| 階段 | 內容 | 驗收 |
|---|---|---|
| P1（本 turn） | 甲-1／甲-2 已推；甲-3 門面對齊；丙-1 lint 實作＋selftest 綠＋全掃 0 缺陷 | commit 可見；`python3 scripts/check_treaty_refs.py` exit 0 |
| P2（拍板後） | 乙批逐案執行：升版＋跨檔同步＋合規聲明＋audits 留痕 | 每案：版本行全鏈一致、`check_treaty_refs.py` 仍 0、CS 檔增量段落載明 |
| P3（拍板後） | 報告書回收：§四改為引憲章條文（若乙-3 入憲）；乙-4 若入憲則兩計畫書改引 | 報告書無「法源空懸」之自述 |
| P4 | 三讀稽核殘餘發現併入本檔 §八 | 每則標 CONFIRMED／REFUTED 與軌別 |

## 八、三讀對抗稽核結果（12-agent；`wf_175c81eb-c2c` 已收槍）

**規模**：9 讀者提出 **144 則**指控 → 3 對抗驗證器逐則駁 → **存活 127**（REFUTED 17；CONFIRMED 92／RECLASSIFY 35）。分類：C 一條路斷點 20・E 跨檔矛盾/過期 87・F 報告書落差 12・B 概念層被執行層定義 5・D 刪名 2・A 域錨 1。軌別：**機械 63／判準 64**。嚴重度：high 23・medium 56・low 48。

> 驗證器預設立場＝「寧可 REFUTED 也不放過假陽性；引句對不上原文即駁」，故 17 則被駁者不列待辦（見 8.3）。

### 8.1 機械軌（63 則；不動判準，我可自辦）

| # | 類 | 嚴 | 檔 | 位置 | 缺陷（節錄） |
|---|---|---|---|---|---|
| M1 | E | L | `docs/系統架構大憲章_v1.49.0.md` | 修訂歷程 v1.49.0 列 · 同步清單（L390） | 同步清單漏列 README 與原則精華（前一列 v1.48.0 尚有「README／原則精華指針」），實測 README.md L42 仍連結不存在之 `docs/系統架構大憲章_v1.48.0.md`、原則精華 v1.10.0 第 8 行仍寫「這 20 條 = 「系統架構大憲章 v1.48.0」第 |
| M2 | E | M | `docs/系統架構大憲章_v1.49.0.md` | 檔首 憲章從屬 blockquote（L3） | 本檔據以主張 §0.6(b) 分層合規之載體失效：現行 `CS-系統架構大憲章_v1.49.0.md` 並無逐節 Layer 標注表（該表僅存於 CS-v1.47.0 之 CS.4），且其 CS.2 誤寫「本 CS 僅覆蓋領域憲章 **v1.48.0**」；於是 v1.49.0 之 L4／L5／L6 |
| M3 | E | L | `docs/系統架構大憲章_v1.49.0.md` | 第三部 validate「預言機誠實判準」·唯一合法產生路（L135） | 「該 gate」之指涉歧義：句子主詞為 `direction_gate`（判準先寫死之處），括注主詞為 `prediction_unfreeze_gate`，而依修訂歷程 v1.46.0 列與同節 L136④，退 superseded 者為 `prediction_unfreeze_gate`、`d |
| M4 | E | L | `docs/系統架構大憲章_v1.49.0.md` | 第三部 philosophy「原典抓取範圍界定（資料納入準則）〔v1.1 | L160 明文排除「純自然科學／物理／數學」，L162 卻明文「得依決策層人拍板納入管理/能源材料/太陽能材料/化學/電子/物理/生物等知識域」且宣稱「『能抓≠該抓』判準不變」；兩條對「物理／化學」給出相反結論，而 L162 未載「本擴充不受 L160 排除拘束、L160 僅限哲學原典 `work_ |
| M5 | E | L | `docs/系統架構大憲章_v1.49.0.md` | 第三部 philosophy「檢索與顧問前端（素養層唯讀出口）〔v1.2 | L182 明定「嵌入模型經 `embedspec`（model_tag／dim／collection 命名之**單一 SSOT**）」，L164 卻把具體 model_tag 與維度（e5-small／384）寫進條文，形成同一事實之第二權威家，違本檔第六部 SSOT 鐵律（#12）；換模時條文即失 |
| M6 | E | L | `docs/系統架構大憲章_v1.49.0.md` | 第一部 資料本質 ·「衍生索引與傳輸工件非 SSOT、可拋棄」（L35） | 條文兩處以 Milvus 為 serving 索引之唯一具名例示，而實際採用之後端為 pgvector／Qdrant（`knowledge_vectorstore_config.backend` 種子＝`pgvector／qdrant_*`、`augur-qdrant.service` 已上線、`e |
| M7 | F | M | `docs/系統架構大憲章_v1.49.0.md` | 第三部 philosophy「⚠ LLM 接縫之隱私上限〔v1.37.0 | 報告書核心第 5 點釘 AI 位置（可生成候選／搬運原典／當評測引擎；不得寫入知識、不得自我背書、不得碰人閘與修法權）時，漏載本檔明標「不可違反」之隱私上限——推理與嵌入接縫**一律限本機模型**、禁任何外部／雲端 LLM，且可靠度不足之解不得以外部 LLM 換取（因 citations 可能含 ` |
| M8 | E | H | `CONSTITUTIONAL-ROLLOUT-PLAN.md` | §0.4 三份權威來源 | 本節自書「不虛構任何現況」且已因同一失效模式留下一次更正記錄，現二度失效：裁決實為 40 份（`ls constitution/*RULING*.md ／ wc -l` → 40，另 INTERPRETATION-RULING-2026-001）、L7 已 v1.0 生效、L5 provisiona |
| M9 | E | M | `CONSTITUTIONAL-ROLLOUT-PLAN.md` | §2.1 Layer 0–7 狀態表（L5／L7 列）＋其後「里程碑現況 | 本表自稱九階段排程所依之「現況基線」，卻仍載 L5 provisional、L7 充任受阻、L2 之 66 列 Annex TR 從未受檢、M2 三阻卻未消——四者均已消解（029 解除 provisional；011／025 充任＋§8.2；RULING-2026-021 L2 矩陣窮舉補列＋G5 |
| M10 | E | M | `CONSTITUTIONAL-ROLLOUT-PLAN.md` | §3.3 支線 β（deadline 2026-10-14）＋§7.3  | 支線 β 之主項已履行而總綱未收：docs/compliance/ 已存 CS-CLAUDE.md、CS-原則精華_v1.10.0.md、CS-系統架構大憲章_v1.47/48/49.0.md、CS-系統核心思想_v1.8.0.md、CS-datasets_zh.md（2026-07-23，RULI |
| M11 | E | L | `CONSTITUTIONAL-ROLLOUT-PLAN.md` | §2.3 已完成之補正資產（並連動 §八 下一步 1–3） | 與同檔 §2.1（L2／L3／L4 均 2026-07-17 v1.0 生效）逐字互斥；§八「下一步」1–3（P-1 KS §0.1 patch、P-2 ID CS.4 矩陣補足、§8.3 linter 骨架上線）亦均已完成（L2–L4 已蓋章；HANDOFF §4.1 記 corpus PASS  |
| M12 | D | M | `CONSTITUTIONAL-ROLLOUT-PLAN.md` | §7.4 aarch64 選型關卡（連動 §2.4 硬體基線、§3.3  | 以供應商專有 runtime（NVIDIA CUDA 13、NGC ARM）與具名產品（GIGABYTE AI TOP ATOM／GB10）作為關卡與階段 4 完成判準而非例示，刪名即判準空轉；且該具名硬體已宣告不存在（ops/machines/PC002-S1800.md:48），使世界層 §5  |
| M13 | E | M | `CLAUDE.md` | #11 提拔/經濟終關、#17 哲學層、#26、#28、#29(a)(b | 裸 `#N` 在「本檔條號」與「原則精華條號」之間漂移且無前綴：此處「#14」指原則精華 #14（經濟價值判定），但本檔 #14＝Commit/Push 須明示授權；同型錯指還有 #17 之「principle→factor_map→#14」、#28 之「三敵人零容忍（#1／#8／#15）」（本檔  |
| M14 | E | M | `CLAUDE.md` | 章首「位階」段第 1 行 | 兩份靈魂／原則檔都釘了版本，「憲章」卻不定版，而 `docs/` 現同時存 `系統架構大憲章_v1.47.0.md` 與 `_v1.49.0.md`（GOVERNANCE-MAP §2 定 v1.49.0 為現行）；同時全檔「憲章」一詞兼指元憲章（章首「憲章從屬（AUGUR-MC v1.6）」）與領 |
| M15 | E | L | `CLAUDE.md` | 章首「憲章從屬」段末「合規聲明」句 | 裸 `§11` 易被讀為元憲章 §11，但 MC 章節號僅 §0–§9（§0.3 條款編號系統），§11 實為 `AUGUR-WM v1.0` 之第 11 章（合規聲明格式，內含 WM.39–45）；同段其餘引用都帶規格前綴，唯此處缺。 |
| M16 | F | L | `CLAUDE.md` | #24 API 限速（機制 SSOT＝原則精華 #17） | 報告書「世界建構核心」六點只講觀測通道之**開放列舉**（P1.E1／P3.W2）與證據可信，完全未載「取用觀測通道須節制、不得過載被觀測方」這一治權檔實存義務（#24／#25＋原則精華 #17 三層防護），亦未載其對偶的 Claude 配額護欄（#28 撞限額即停、不重試風暴）——屬報告缺漏，會使 |
| M17 | E | H | `HANDOFF-governance.md` | 「一句話現況」＋「八層狀態」表 L7 列 | 本檔自稱「接手本 repo 的人或 Agent」之唯一入口，卻仍載 L7 未生效／M2 未達成，而 L7 已由 RULING-2026-011 充任 v1.0、§8.2 由 RULING-2026-025 條件通過、specs/INFRASTRUCTURE-SPECIFICATION.md（非 dr |
| M18 | E | H | `HANDOFF-governance.md` | 「等 Steward（人類）裁決的三件事」表（#23 列與 L7 §8. | 兩列均已裁而仍列為待裁：#23 已由 RULING-2026-024（T-L7-13，§8.1 多軸解耦、取交集為忠實承接）作成並登錄 AL-2026-…（AMENDMENT-LOG:311），L7 §8.2 已由 RULING-2026-025 條件通過；接手者依本表取件將重複已完成之裁決並誤判  |
| M19 | E | M | `HANDOFF-governance.md` | §2b「L2 的「✅ PASS」是假的」＋§2 代碼塊＋八層狀態表誤標欄 | lint 標記數字已 --sync 為全 0，而環繞散文仍以「🔴 誤標／151／59 列矩陣仍未受檢，真值未知／L2 的 PASS 是假的」為現況陳述，且同檔「gate 現況」第 1 點同時自書 `_ANNEX_TR_HEAD` 已放寬為 `#{1,3}`——同一節內「已放寬」與「仍未受檢」並存，讀 |
| M20 | E | M | `HANDOFF-governance.md` | §兩個 repo（刻意分離）＋§工具與環境（硬體／PostgreSQL／ | 本檔正文骨幹仍為「二 repo 分離＋/home/giga 路徑＋GB10 aarch64＋userspace PG:55432」，而 monorepo 已於 2026-07-22 合併（檔頭自註）、ops/machines/PC002-S1800.md:48 記「`aitopatom-b96e`（ |
| M21 | E | H | `HANDOFF.md` | §4.0 近程優先表「三軸自進化」列 | 該列以 2026-07-26「採納／未開執行」為終態，而同日 commit 396944b 已 V2-P-yes＋SUNSET 生效（criteria_sha 65eda893 凍結、hugo 親簽）、Phase 5 evolution_ledger 9 表 DDL 落地、Phase 3 RAWEV |
| M22 | E | M | `HANDOFF.md` | §1「先讀這些」表（憲法列、建構理解列）／§4.7 路由表 | 接續第一份該讀之檔把「憲法」指向不存在之檔（docs/ 只有 系統架構大憲章_v1.47.0.md 與 _v1.49.0.md），且建構理解仍指 20260710（v3）而 20260713（v4）已在——新機接續者按索引取件會取到空鏈或已被取代之理解版本。 |
| M23 | E | H | `HANDOFF.md` | §4.2 下一步（arena 開賽段）＋§4.5 待 hugo 第 6  | arena 已開賽、首批結算、計分板誠實化並重掛每日出單排程（commits afef5d7／e61eabc／9eb3399，2026-07-26），且 §4.0 內另有 07-28／07-29 之 CLOSED 列，而 §4.2「下一步」、§4.5 第 6 項「arena 開賽 cron 掛載時點 |
| M24 | E | M | `HANDOFF.md` | §3 不在 git 清單 — DB dump 列（對照 §4.1b ⑤） | 同檔 §4.1b ⑤ 載「DB dump=`C:\database\augur_pgdump_20260718_Fd.tar`（修復後乾淨快照）」，兩處各自宣稱「最新 dump」且互斥；換機者依 §3 還原將取到 PriceAdj 錨修復前之 07-13 庫，得到已被取代之 headline 口徑。 |
| M25 | E | M | `docs/系統核心思想_v1.8.0.md` | 「它預測什麼」・任務列末（第 30 行） | SSOT 指針釘死已 SUPERSEDED 之大憲章 v1.45.0（現行 v1.49.0，v1.45.0 於其修訂歷程列明 SUPERSEDED），致靈魂把現行鎖清單指向史料版本；同句前段「留痕於憲章 v1.45.0 該條」作為歷史事實引用則正確、無須改。 |
| M26 | F | L | `docs/系統核心思想_v1.8.0.md` | 「資料只來自哪」範圍註（第 50 行） | 報告書核心 3 稱八種行走者（含②人類原典／知識庫）皆經「人類授權門」；靈魂對知識准入只給三條資料誠實判準、無任何人閘明文，且大憲章 v1.48.0（2026-07-29）已明文廢止 approve／activate 唯人、改「所有資料一律准入、僅硬閘（license／owned_local／非 A |
| M27 | E | L | `docs/系統核心思想_v1.8.0.md` | 檔頭「憲章從屬（AUGUR-MC v1.6）」blockquote（第  | 檔頭只寫「登錄為 Layer 1（World Model）並為 AUGUR-WM v1.0 之領域前身文件」，未載 WM.6 與本檔合規聲明 CS 第 5 行已明定之規範地位（[I] 引註、非定義依據、規範承接以 WM／Annex A 為準），單讀靈魂者會誤把靈魂文字當 L1 定義依據引用。 |
| M28 | E | H | `ARCHITECTURE-OVERVIEW.md` | 檔頭〈性質〉行（L3）＋§五 現況快照表與進度條（L55-71） | 整份狀態陳述已被自身所引之裁決推翻：L0 記 v1.3（現行 v1.6，§0.1）、L4 記 KS v1.0（MC §0.5 記現行 v1.1／RULING-2026-016）、L5 記「provisional，§8.2 延後」（RULING-2026-029 已解除 provisional）、L6 |
| M29 | E | L | `ARCHITECTURE-OVERVIEW.md` | §一 標題／§二 對映表「對映 repo」欄／§三 圖框（L1, L19 | 實體錨定已消滅：README L3 明載「本倉自 2026-07-22 起為 應用 + 治權 合一遠端（原 `augur` + `augur-constitution`）」，且 docs/系統架構大憲章_v1.49.0.md 檔頭亦記「原獨立倉已併入」——本檔標題與三處圖表仍以「2 Repo 對映／ |
| M30 | E | M | `ARCHITECTURE-OVERVIEW.md` | §五 末段「治權主導混合式之下一步」（L73） | 門面把規劃錨在同倉已被認定為誤導之文件與已宣告不存在之機器上：同倉 GROUNDING-MAP L29 判定「infrastructure/ENVIRONMENT-SPEC.md 描述的是另一台不可達的 GB10 機器——與本機實測全面不符，屬主動誤導文件，本圖全程未引用」，§五、§六-5 並建議凍 |
| M31 | E | M | `LAYER-SEALING-SCHEDULE.md` | §3a 概念層 L1–4 交互檢查 — 處置行 | RULING-2026-022-CONCEPT-TIER-CROSS-LAYER.md 已作成並在 constitution/ 內，四條 cross-layer major（P5.W4 無承接／Annex D 廢棄編號／KS 誤標 9 列／D19 斷鏈）之處置狀態未回收，接續者仍讀為「整合完整差 4 |
| M32 | E | M | `LAYER-SEALING-SCHEDULE.md` | 檔頭「權威狀態」項 | 把蓋章／生效之權威錨在執行層工具（gate／selftest）與版本控制，漏列唯一法定權威——Steward 書面裁決＋Amendment Log（§8.1／§8.6）；此與同群 ULTRACODE-SCHEDULE 共用鐵律 3「不得以 linter 綠燈為合憲依據」及本群 HANDOFF-gov |
| M33 | E | L | `LAYER-SEALING-SCHEDULE.md` | 第二階段維度表「可運作（真跑）」列（L1–4 概念層格） | 該格之 3,491 未標機器、時點與產生指令，其唯一已知出處為 aitopatom-b96e（GB10）2026-07-22 實跑（ops/phase2/ENTITY-BACKFILL-20260722.md），而該機已宣告不存在，且同倉 ops/phase2/SMOKE-aitopatom-b96 |
| M34 | E | M | `specs/COGNITIVE-KERNEL-SPECIFICATION.md` | 目錄 Annex TR 列、§0 後「編號穩定性」段、文末計數段 | TR.F（AUGUR-KS 全份補列，RULING-2026-019 決策二／RULING-2026-023 重採認）為現行 [N] annex，但目錄列（並將矩陣範圍寫成「MC＋WM＋ONT＋ID → L5」漏 KS）、編號穩定性段與文末計數段三處均未列 TR.F，使 L5.90／CS.4 之生效 |
| M35 | E | L | `specs/COGNITIVE-KERNEL-SPECIFICATION.md` | Annex CS front-matter defers-in 欄；併  | Annex TR.C(3) 依 RULING-2026-030 將 WM §D14 列為「承接（部分）：候選斷言工作流演算面＝L5.5」、§D19 列為「承接（空集揭露）」，但 front-matter defers-in 與 CS.3(a) 雙向 DEFER 表均無此二碼，使 WM.43 之雙向承 |
| M36 | E | L | `specs/COGNITIVE-KERNEL-SPECIFICATION.md` | §8 末／§9 章首（L5.10、L5.90 之章節歸屬） | L5.10（目錄歸 §8）與 L5.90（§9 條款）均排在「## §9」標題之上，且 L5.90 之「義務主體／可判定判準」段落被切到 §9 標題之下成為無主孤塊——使章節歸屬與義務承載段之對應在機器盤點上錯位（§9 章下首見之判準句實屬 L5.90）。 |
| M37 | E | M | `docs/原則精華_v1.10.0.md` | #20 ENFORCE「決策層人拍板」（L153） | 移除逐案人簽＝MC P5.W5 明定「推定違反、不得實施」之類型，須附 Steward §8.1 書面認定方得推翻，但本條未引該認定（認定實存於 audits/G-PME-SOUL-CLOSED-20260724.md §2，靈魂之合規聲明有引、本檔無）。 |
| M38 | F | L | `docs/原則精華_v1.10.0.md` | #16（L145-147）／#17（L60-63） | 報告書六點核心漏載本檔兩條實質不可違反義務：#16 clean-room（來源純度＝禁前身系統之 code／數字／設定回流，屬「世界怎麼被建起來」層級之禁令）與 #17 API 速率公民（對外部服務端之節制義務、撞訊號即停），六禁令與八行走者清單皆未涵蓋。 |
| M39 | E | L | `docs/compliance/CS-CLAUDE.md` | CS.1-P1／P2／P3／P4／P5／EV-chain 各節首句 | WM.41(a) 明定所引憲章條款「一律 `AUGUR-MC v{version} §{條款}` 格式（Layer 2–7 規格並引 `AUGUR-WM v{version} §WM.{n}`）」，本檔七節中僅 CS.1-PA 合格（`AUGUR-MC v1.6 §1.1`），其餘六節皆為裸 `§P |
| M40 | E | L | `docs/compliance/CS-CLAUDE.md` | CS.3(b) defers-out 表「目標」欄 | `AUGUR-AR` 非登錄之引用縮寫：MC §0.5 Layer 6 列與該規格 §0.1 均定「Agent Runtime Specification（下層引用簡稱 **AUGUR-L6**）」，全 `specs/`／`constitution/` 搜尋不到 `AUGUR-AR`；同檔 CS.4 |
| M41 | E | L | `constitution/GOVERNANCE-ANNEX.md` | 檔頭「依據」行（L3） | 附則之上位依據與引用格式示例停在 MC v1.2，而其第 2 條沿革註所引之 RULING-2026-031 係以 `AUGUR-MC v1.4 §8.5(b)` 為據、MC 現行 v1.6（§0.1）——同一份治理附則檔內版本錨定自相矛盾，且違其自訂之 §8.6 引用格式一致性。 |
| M42 | F | L | `constitution/GOVERNANCE-ANNEX.md` | 第 4 條（暫時豁免之期限與程序）＋第 5 條（補正期曆時上限） | 報告缺漏：報告書核心六點完全未載治權體系之豁免／補正制度（單次≤180 日、展延一次、涉不可豁免核心一律不受理、既有實作違憲補正期曆時上限 24 個月），而該制度實質調節「一條路」之強制力——讀者僅憑報告書會誤認世界層義務為零彈性、亦不知「豁免期間須帶知識標記」（MC §8.4）之存在。 |
| M43 | E | H | `CODE-MIGRATION-PLAN.md` | §〇 現況基線 — 行為層列（並連動 Phase 2 無完成標記） | Phase 2 之分支已依 RULING-2026-015 併 main（4c6d3b6，27/27 綠），存量鑄造與 retire 已於 2026-07-22 實跑落地（ops/phase2/ENTITY-BACKFILL-20260722.md：entity_registry 3,491／ent |
| M44 | E | M | `CODE-MIGRATION-PLAN.md` | 檔頭版本行 vs 檔尾註 vs §五 Steward 決策點 1 | 同一檔三處互斥：檔頭載「v1.0——2026-07-18 經 RULING-2026-012 採認生效」、檔尾仍為 v0.1-draft、§五決策點 1 仍把「本計畫書採認」列為待批——接手者無法判斷本計畫是否已生效力。 |
| M45 | E | M | `specs/WORLD-MODEL-SPECIFICATION.md` | §0.3（條款編號系統，末項）＋ Annex C front-matte | 母法已升 AUGUR-MC v1.6（AL-2026-044），Annex C front-matter 已寫 `mc-version: AUGUR-MC v1.6`，但正文與各 Annex 仍有 227 處引用 `AUGUR-MC v1.4`，同一文件內版號自相矛盾，且 §0.3 自課之「升版同步 |
| M46 | B | L | `specs/WORLD-MODEL-SPECIFICATION.md` | Annex D — D0（承接義務）可判定判準末句 | D0 為 [N] 掛鉤條款，其可判定判準段直接嵌入一支 Layer 7 執行層腳本路徑，且未標 [I]、未附 WM.4 刪名測試註；WM.4 明定本規格對產品之提及「僅得為 Observation Channel 之指名」，lint 腳本非 Observation Channel，於 [N] 文字中 |
| M47 | E | M | `specs/IDENTITY-SPECIFICATION.md` | Annex TR — TR.D (2) ONT Annex T 逐號涵蓋 | ONT Annex T 實際只有 T.0–T.6、T.20–T.29、T.30–T.36、T.40–T.44、T.50–T.53、T.60–T.61、T.90–T.91（ONT 尾註自陳「型別 T.1–T.61」），並無 T.7–T.13 與 T.62；ID 的 TR.D 逐號清單憑空列了 8 個不 |
| M48 | E | L | `specs/IDENTITY-SPECIFICATION.md` | 目錄（Annex TR 行）／Annex TR.Z／尾註「本規格計」 | TR.Y（RULING-2026-019 補列之 [N] 條款，載 15 組上層 [N] 條款之唯一落點）未列入目錄、尾註條款清單，且 TR.Z 與 CS.4 結語均以「TR.A–TR.D 已就…全部條款逐條枚舉」宣稱完備；依字面，那 15 組（MC §2.1／§2.2／§2.3／§2.7／§2.8 |
| M49 | E | L | `specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` | 目錄（Annex DI 行）＋尾註「本規格計」 | Annex DI 實際列至 KDI.22（KDI.19＝WM-D14、KDI.20＝WM-D15、KDI.21＝WM-D19、KDI.22＝WM-D23，均為 RULING-2026-030 補入之承接列），但目錄與尾註仍寫 KDI.0–KDI.18，且目錄核心錨定欄之來源清單「`WM` D7–D1 |
| M50 | E | L | `specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` | Annex L56 標題（§11 之後） | 同一表既標 [N]，其內容又是 KS.102 可判定判準（「Annex L56 兩欄無交集，且本層任一條款不落入 Layer 5/6 專屬欄」）之唯一依據，標題卻仍掛「（示意）」hedge；同檔 EV.2 與 CL.0 已明文除此類 hedge（「序集與各級 L_C 天花板本身**非**示意」、「為 |
| M51 | E | H | `specs/INFRASTRUCTURE-SPECIFICATION.md` | L7.51(b)(c)（統一記憶體、單節點與 residual risk | L7.51(b)(c) 之 [I] 現行值（121 GiB 統一記憶體、可用儲存 3.4 TB）為已作廢之 GB10 機器事實，未隨 L7.50 之 patch 級登錄變更同步更正——同檔 L7.50 登錄 RAM 15GB／GTX 1650 4GB，ENVIRONMENT-SPEC（2026-07 |
| M52 | E | L | `specs/INFRASTRUCTURE-SPECIFICATION.md` | §0.1 層級欄、L7.1（從屬與末層地位）括號內之 §0.5 引述 | L7.1 與 §0.1 於引述 MC §0.5 對照表 Layer 7 欄之所轄清單時多列「Infrastructure Deployment」一項，該項不存在於 §0.5 表（表列為 Infrastructure Specification、External Interface Layer、Dat |
| M53 | E | M | `specs/AGENT-RUNTIME-SPECIFICATION.md` | 目錄 Annex LDI 列（LDI.0–LDI.6）、文末計數段 | LDI.7（承接 ID IDO.7→L6.9(d)，RULING-2026-016 增列，並經 CS.3(a) F-IX-3／RULING-2026-038 再確認）為現行承接列，但目錄與文末計數段均寫「LDI.0–LDI.6」，與 Annex LDI 實表（含 LDI.7）及 front-matt |
| M54 | E | L | `specs/AGENT-RUNTIME-SPECIFICATION.md` | §1.2 末句；併 Annex TR.Z 之自我起草警示 | §1.2 與 TR.Z 仍稱三重防守之充分性「最終待 §8.2 實質審查確認」，與同檔【地位】節及 CS.2 T-L6-5「已核定（007 §8.2）；OCV 維度充分性 residual 保留」矛盾——同一文件對 §8.2 是否已作成給出相反陳述（TR.Z 為 [N]）。 |
| M55 | E | L | `README.md` | 「目錄」段 src/augur/ 清單（L54-55） | 門面之 package 清單與實體不符：`ls -d src/augur/*/` 實測 16 個 package（advisor, arena, audit, catalog, core, deliberation, evaluation, evolution, execution, feature |
| M56 | E | M | `GROUNDING-MAP.md` | 檔頭〈性質〉行（L4）＋§二 逐原則落地表全表 | 落地地圖之權威清單漏列四份已生效規格且未依本檔自訂之誠實紀律標明未涵蓋：`grep -c 'ONT\.' GROUNDING-MAP.md` → 0（AUGUR-ONT v1.0 經 RULING-2026-003 充任，L2「分類與同一性判準／刪名測試 ONT.4」零落點）、L5／L6 條款亦零落 |
| M57 | F | M | `reports/augur_plain_language_full_report_20260730.md` | §二 L1 段（World Concept Registry 句） | 報告只載 Registry 的「登錄即擴充」面，漏載其對稱的世界層強制義務與現行日曆項：WM.35（未登錄映射／unmapped 通道之資料僅具 Observation 地位、不得被消費為 Representation 或 Knowledge 依據）與 WM.36（消費必須以世界概念為鍵、不得以供應 |
| M58 | F | L | `ULTRACODE-SCHEDULE.md` | 共用鐵律 4（與 LAYER-SEALING「教訓」段對偶） | 報告書核心六點僅泛言「終審永遠是實效與誠實」，漏載本群最硬且已 12–17 度應驗之機制義務：不採信自陳、獨立對抗複核（非施作者）為蓋章／閉合要件、反駁官預設 refuted=true、幽靈落點必親讀、誠實界限節不得省略——接續者若只讀報告書會誤以為自查可結案。 |
| M59 | F | M | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §8.1 誠實條文(731 行) | 報告書核心第 4/5 點把「人類授權門、不得自我背書」講成釘死的機制,而治權檔明文自陳其為榮譽制＋事後偵測(非機械保證)——報告書漏載此上限;更甚者 REPLAY／META-REPLAY 兩計畫之 R0/M0 驗收僅寫「簽核碼」而完全無此揭露,實查該八列 approved_by 為「hugo(對話拍 |
| M60 | C | M | `reports/augur_all_evolution_next_steps_20260729.md` | §五 結語(70 行) | 五把尺中至少兩把不成立:A′(LAI 行為尺)依 master plan §4.2.8 明文「暫不入此表凍結」,實查 evolution_prereg_gate 僅 V2-SUNSET 一列、無 lai 軸列,且 eval_code_hash 兩日五換;replay／meta 兩門雖有凍結列,其窗長 |
| M61 | E | H | `reports/augur_open_problems_schedule_20260730.md` | §一 P10 列 | 「60」不存在於任何 arena 凍結列:實查 dgate_arena_own_daily_5／chronos_5／timesfm_5 之 min_clusters=250、own_stack 三門=36,故以 60 推得的「10 月底才到」低估約 4 倍,而 V2-SUNSET 期限正是 2026 |
| M62 | E | L | `specs/ONTOLOGY-SPECIFICATION.md` | §0.3 條款編號系統（末項引用格式） | ONT §0.3（及 ID §0.5、KS §0.5 同體例）把憲章引用版號以「一律採 v1.4」凍結，正是 RULING-2026-018 就 L1 已廢止之永久凍結措辭，與同檔 Annex CS `mc-version: AUGUR-MC v1.6` 直接衝突，且使下層無法在母法升版後合法更新引 |
| M63 | F | L | `constitution/META-CONSTITUTION.md` | §8.4（暫時豁免與不可豁免核心） | MC §8.4 之豁免制度（核心條款定義、禁止性規定一律不得豁免含其履行時程、不可豁免核心清單、豁免期間須標記 Evidence 缺口）為 L0 承載全鏈之關鍵治理機制，且為 L7 處置單機無備援（T-L7-2、L7.28(c)）之唯一合法路徑，報告書六點核心未載，使量尺缺少「何者連時程都不得豁免」 |

### 8.2 判準軌（64 則；一律呈簽）

| # | 類 | 嚴 | 檔 | 位置 | 疑義（節錄） | 建議措辭（節錄） |
|---|---|---|---|---|---|---|
| G1 | E | M | `CLAUDE.md` | #26 有界自主推進（章五） | 本條建立的「人→Agent 授權」是 L6.6 意義下的授權委派，卻只寫了 revocability（「授權可隨時收回」）與範圍描述（「護欄內」），缺 expiry（逾期自動失效）、繫結之 Plan 參照、以及授權授予本身之留痕（Observation），亦全 | 建議 Steward 於 #26 首段後增一句：「授權要件（承 `AUGUR-MC v1.6 §P5.W2`、`AUGUR-L6 v1.2` L6.5／L6.6）：每次有界自主授權須明示 (a) 範圍（可為之工作類別與護 |
| G2 | E | M | `CLAUDE.md` | #28「不自掛長喚醒鏈（省配額）」／#26 自我 prompt  | 全檔唯一對「連續無人介入之自動執行鏈」設限的句子，理由是省配額而非人類監督；`AUGUR-L6 v1.2` L6.16 之 OCV C 分量（最大自動執行鏈長）、D 分量（逐案可介入點密度）與 L6.17 單調棘輪（C 增加＝推定違憲）在工具層無任何落點——# | 建議 Steward 於 #26 增列「自動鏈上限」子條：「(a) 每次授權須載明本輪最大連續無人介入圈數／時長上限，達上限即停並回報等待人類續授；(b) 凡新增或延長背景編排、排程、自我喚醒鏈者，須於報告中對照前後之『 |
| G3 | E | M | `CLAUDE.md` | #14 Commit / Push 須明示授權 | 本檔只規範 Agent 自己的署名（Co-Authored-By），卻沒有任何一條禁止 Agent 代填「用於證明某事由人做過」的人類簽核欄位（如 promoted_by／approved_by／decided_by／人裁佇列之簽核列）；此為 P5.W2 授權 | 建議 Steward 於章一增一條（沿新增順序給新編號，勿重排既有條號）：「**人類簽核不得代打**（承 `AUGUR-MC v1.6 §P5.W2`、`§P4.E7`；`AUGUR-L6 v1.2` L6.2／L6.1 |
| G4 | E | H | `CLAUDE.md` | #28 模型檔位分派表（Fable 5 列） | 分派表把「治權檔增修」「高風險裁決（git 分叉處置/洩漏鑑識）」直接列為 AI 模型之作業項，表內與表後「切換紀律」均無「AI 僅得草擬、議決與解釋權專屬 Steward」之限定句，與 MC §8.1「**Agent（§2.8 意義下之自主程序）不得參與修憲 | 建議 Steward 於分派表下方增註：「**檔位≠權限（`AUGUR-MC v1.6 §8.1`）**：本表僅分派『由哪個檔位執行』，不授予任何議決權。治權檔增修、條文解釋、違憲審查與一切裁決之權專屬 Constitu |
| G5 | E | L | `CLAUDE.md` | #9 零 AI 幻像（章二） | 三類來源（程式輸出／DB／API）全屬系統自身通道，本檔卻無任何條款要求 AI 自身產物攜帶標記或走預凍評測：全檔 grep 不到 self-reported、synthetic、地板/天花板/錯配對照臂等字樣——即報告書「一條路」之行走者④『AI 能力宣稱』 | 建議 Steward 於章二增一條：「**AI 自身宣稱走同一條路**（承 `AUGUR-MC v1.6 §P4.E7`；`AUGUR-L6 v1.2` L6.4）：(a) AI 產出之文字／評分／裁決意見一律標記為 s |
| G6 | C | M | `CLAUDE.md` | 章六 本檔升版 | 本檔承載多條上位不可豁免核心之落地（#9–#12→P4.E1 Evidence 追溯；#14／#26→P5.W2 人類權威；#28→P5.W5），升版節卻只說「不需動憲章」，未排除承載不可豁免核心之條、未要求 Steward 親簽、未要求同步更新 CS-CLA | 建議 Steward 於章六增列：「(a) 本檔任何**弱化**義務之修訂（含放寬 #6／#14／#19／#26 護欄、放寬 #9–#12 資料真實、放寬人類介入點）不得以『工具慣例更新』為之，須 Steward 親簽並 |
| G7 | C | M | `HANDOFF.md` | §5 誠實紅線（並連動 §4.4 紅線） | 行走者④「AI 能力宣稱」在本檔缺預先凍結判準之明文：檔頭 2026-07-26 更正已逐字記載尺失效實證（常數樣板 0.654 高於現役 0.492、竄改金標仍得 1.000、think:false 無效），但 §5／§4.4 紅線無「宣稱能力前須跑 cei | §5 增一條紅線：「**能力宣稱須過樣板地板**——任何本地／外部模型或 pack 之能力數字，宣稱前須(1)題庫與判準先凍結並登錄 sha、(2)同批跑 ceiling／floor／mismatched（＋shuffl |
| G8 | E | M | `constitution/GOVERNANCE-ANNEX.md` | 標題行（L1）＋「生效日」（L5）＋「登錄」（L6） | 附則已於 2026-07-23 經 minor 修訂（第 2 條第 1 款強制公示要件廢止；RULING-2026-031、AL-2026-034，AMENDMENT-LOG L368-374 在卷），但版本行仍 v1.0、生效日仍 2026-07-16、登錄 | 由 Steward 裁定版本編號與登錄之更新方式（建議：標題升 v1.1、生效日增列「v1.1：2026-07-23」、登錄行增列 AL-2026-034，並於文末計條句後加一行修訂表）。涉版本語義與登錄之治理記錄，我僅 |
| G9 | C | L | `constitution/GOVERNANCE-ANNEX.md` | 第 6 條第 1 款（登錄與公開存檔） | 「晉升或判死皆留檔」對行走者⑧（法律自己）在治理層無通則明文：登錄清單只列已通過之產物（修訂／解釋／審查／豁免），未含**被駁回、撤回或未議決之修訂提案及其理由**；RULING-2026-031 第 2 點雖聲明 GOV-4 findings「留檔不滅」，但 | 建議 Steward 於第 6 條增第 4 款：「修訂提案（含原則級、minor）不論通過、駁回、撤回或逾期未議決，其提案全文、處置結果與理由一律登錄 Amendment Log 並存於 `constitution/am |
| G10 | E | L | `constitution/GOVERNANCE-ANNEX.md` | 第 2 條第 3 款（patch 門檻） | 自反性缺口：patch 通道未載明「誰得為之」與「誰認定某變更屬 patch」，亦無人閘與施作留痕要件——而 MC §8.1 L489「Agent（§2.8 意義下之自主程序）不得參與修憲與解釋」之落地，全繫於 RULING-2026-028 第 2 點（參與 | 建議 Steward 於第 2 條第 3 款增後句：「patch 之**性質認定**屬 Steward 保留事項；施作得由幕僚（含 Agent）為之，惟須依 Steward 核示、逐案留痕，並依 RULING-2026- |
| G11 | E | L | `constitution/GOVERNANCE-MAP.md` | §3 推薦讀序（新人／Agent）第 3 項 | 報告書核心第 1 點（世界建構讀序 L1→L7）與第 3 點（「一條路」、八種行走者無特權通道）在治權檔中查無明文支撐：`grep -rln '一條路\／行走者\／世界建構' constitution/ specs/ docs/*.md README.md`  | 二擇一或並行，均須 Steward 決定：(a) 報告書就此二點明標【[I] 綜述】並逐點附 [N] 依據（候選→證據通道＝MC §P4／KS.70-79；人閘＝§P5.E2／P5.W2；判死留檔＝§P4.E3／KS.5 |
| G12 | B | H | `docs/compliance/CS-CLAUDE.md` | CS.1-P5（逐原則論證第六節） | 本節同時引 `§P5.E1`、`§P5.W2`、`§P5.W5`（後二者為 §8.4 不可豁免核心），其唯一「判準揭示」卻錨在一支掃 docstring 是否含「執行指令矩陣」字串的腳本上——該腳本與授權鏈根節點、人類否決可達性、監督能力非侵蝕毫無涵蓋關係；同 | 建議 Steward 令 CS.1-P5 改寫判準揭示為三段：「(a) P5.E1／P5.W2＝授權要件四項（範圍/期限/可撤銷/計畫參照）與人類簽核不得代打之明文存在性，逐次授權留痕可稽核；(b) P5.W5＝依 `A |
| G13 | E | M | `docs/compliance/CS-CLAUDE.md` | front-matter `open-tensions` ／ C | 本檔宣稱零緊張關係，但同層正式規格 `AUGUR-L6 v1.2`【地位】節就完全同型的結構性風險作了明文揭露（「本層由 Agent 起草而規範人類對 Agent 之權威，存在結構性自我交易誘因」）——CLAUDE.md 同樣由 Agent 日常增修且規範 A | 建議 Steward 令 CS.2 補二列並將 front-matter 改為 `open-tensions: [T-CLAUDE-1, T-CLAUDE-2]`：「T-CLAUDE-1（`§8.1`／L6.18）：本檔 |
| G14 | E | M | `docs/compliance/CS-CLAUDE.md` | front-matter `upper-specs` | 清單止於 AUGUR-L5 v1.0，獨漏本檔所登錄之同層正式規格 `AUGUR-L6 v1.2`（Agent Runtime）與 L7（AUGUR-INF）；而本檔 CS.4 自己寫「MC [N] 落點以 `specs/`（尤 `AUGUR-L6`）為權威」 | 建議 Steward 令 front-matter 補為 `upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v1.0, AUGUR-ID v1.0, AUGUR-KS v1.1, AUGUR |
| G15 | E | M | `docs/compliance/CS-CLAUDE.md` | CS.3(b) 雙向 DEFER 表 defers-out 列 | WM.43(b) 之 defers-out 為「下放**下層**之掛鉤」，D-CLAUDE-1 的目標卻是同一層（Layer 6）之正式規格，且其說明「正式規格為權威；CLAUDE＝工具層短半衰期」語意是本檔**遵從上位**而非下放；再者全 repo 搜尋 ` | 建議 Steward 令 D-CLAUDE-1 改分類：自 defers-out 移除，改於 CS.1-P5／CS.1-EV-chain 以 WM.41(b) 閉集值「不適用（附理由）」或「承接」表記——措辭如「Acti |
| G16 | E | M | `docs/compliance/CS-CLAUDE.md` | CS.4 形式充分性＋跨層標注 | 以一句概括把 MC 現行版全部未觸及之 [N] 條款掃為「不觸及」，既未逐條具名、亦未附理由，與 WM.44「均須對應至…、明記 DEFER 掛鉤、或**明記『不觸及』及理由**；任一條款無對應且無明記者，聲明不完整」不符（同格式之 AUGUR-WM 自身 A | 建議 Steward 令 CS.4 補一張 WM.44 逐條矩陣（PA／EV.1–EV.12／F1–F6／P1–P5 各條／§0–§8 各節；並及 upper-specs 各規格 [N] 條款），每列填「本檔落點條號｜D |
| G17 | E | L | `docs/compliance/CS-系統核心思想_v1.8.0.md` | CS.4 形式充分性・跨層標注段（第 68 行） | 該 [N] 聲明與靈魂正文不符：靈魂含 Layer 6 行動禁令（第 153 行「不替使用者下單、不動錢（自動下單＝禁）」）、Layer 7 架構不變式（第 143 行「各層職責不越界…驗證不讀訓練產物」、第 119 行「單一 helper」）、及 RBAC  | CS.4 跨層標注改為實況：「本檔主體登錄 Layer 1；下列節具跨層落點並依 MC §0.5 逐節標注——『它不做的事』之下單禁令→L6（承 A.53）；『管線』職責不越界與單一引用源→L7／L5（承 A.51，機器 |
| G18 | E | H | `docs/原則精華_v1.10.0.md` | 檔尾「演進記錄」（L170-177）×#20 ENFORCE（L | 2026-07-24 commit 8c028ce 實質改寫 #20 ENFORCE 決策層清單（新增「不要求逐案人簽」之人閘豁免、執行層新增 PME APPLY），但檔名未升版、演進記錄無任何一列記載——違反本檔升版哲學「既有原則之重大判準修正 → 升 mi | 由 Steward 認定該 07-24 改動之等級後補正：若屬重大判準修正→升 v1.11.0 並補演進記錄一列（含 Steward 拍板碼 SOUL-PME-B-yes／採納並寫入、audits/G-PME-SOUL- |
| G19 | E | L | `docs/原則精華_v1.10.0.md` | 「資料完整性判準」ENFORCE（L78）vs FREEZE→解 | 同一節內兩條現行規範自相矛盾：ENFORCE 命令 sync 目標「一律」以 2026-05-31 為界，解凍子條卻定「每日增量 sync 為常態、as-of'＝滾動」（另 arena 地基釘 2026-06-30），三個 as-of 並存而未標各自射程。 | 將 ENFORCE 首句改為射程明示：「**歷史**完整性宣稱與其對帳範圍以 as-of `2026-05-31` 為界（定案不變）；**sync 目標**自 2026-07-12 解凍起為滾動（每日至最新交易日）；** |
| G20 | B | M | `docs/原則精華_v1.10.0.md` | FREEZE→解凍子條（L79） | 本節在合規聲明中標為純 Layer 4（治權參數），其判準卻以 DB 單列物件 id（`arena_adm_5305655ad1cd`）與 L5/L6 閘物件（`direction_gate` evaluate ≥60 clusters）為定義錨，違 MC § | 條文層只寫角色語義＋不變式：「live 准入須經**已預先凍結、經人核可之准入閘物件**（現行值＝`arena_admission_gate`，登錄於憲章第三部；判準 sha 不得事後挪動）」——具體 gate_id／s |
| G21 | C | M | `docs/原則精華_v1.10.0.md` | FREEZE→解凍子條（L79） | 行走者⑥（模型／隊伍）之相對強度軸 live 准入實為空懸：條文指定之判準 SSOT（reports/augur_prediction_validation_master_plan_20260711.md §4.3）自承「下列為 AI 建議＋論證，非裁決；判準 | 補一句射程與缺口誠實化：「本機制現行硬前置僅 G1／G2（方向 arena）；**相對強度軸之 live 准入判準（原 G3/G4）尚未凍結、無現行住所——在其預註冊凍結前，相對強度 live 數字一律止於 review |
| G22 | E | L | `docs/原則精華_v1.10.0.md` | #7 ENFORCE 第一款末（L54） | P4.E5（禁 last-write-wins）之領域落點僅立規範而把機制無限期掛在「過渡期」：條文本身無落日、無過渡期 fail-closed 措施（如未上鎖前禁 heal 覆寫或強制保留 pre-image），落日只寫在合規聲明（2026-10-14）；且 | 條文補兩件：(a) 落日與狀態——「機器落點補正期至 2026-10-14（D-PRIN-2）；現況＝migration＋heal 快照路徑已入 repo（2026-07-17），**待人類實測與部署認證**」；(b)  |
| G23 | E | M | `docs/原則精華_v1.10.0.md` | #15 誠實回報 WHAT（L125） | 三源白名單未排除系統自身之 LLM／agent 產出——「程式輸出（stdout）」字面即涵蓋本系統模型之自陳，與 P4.E7／KS 反自我背書（獨立證據＝來源鏈遞迴不含本系統計算產物、self-reported 僅為宣稱性觀測）措辭衝突；下位之 CLAUDE | 於 (a) 加限定並補一款：「(a) **確定性程式**之輸出（含 stdout／JSON／log）——**系統自身 LLM／agent 之自陳輸出不屬本白名單**，僅為 self-reported 宣稱性觀測，永久攜帶 |
| G24 | C | M | `docs/原則精華_v1.10.0.md` | #15 誠實回報 WHAT（L125） | 行走者④（AI 能力宣稱）在本檔缺「預先凍結之評測判準＋樣板地板臂」明文：#15 只管多跑取統計與可溯源，未要求任何能力宣稱先凍結量尺並附 ceiling／floor／mismatched 對照臂，故一個常數輸出即可在分數上勝過真模型而不觸任何條文（該類假綠已 | 於 #15 ENFORCE 增一款：「**能力宣稱前置**：任何以分數宣稱能力（模型／agent／評測器）者，量尺與判準須**先凍結**（sha 留痕）並同輪跑**天花板臂（洩漏上界）／地板臂（不含真訊號之樣板或常數）／ |
| G25 | E | L | `docs/原則精華_v1.10.0.md` | #11 五鏡特徵治理 ENFORCE（L103） | 行走者①（認知候選）之「判死留檔」在本檔空懸：條文只命令「必移」，未要求判死列以 append-only／superseded 形式留痕（含判死時之判準、證據、時點），與 P4.E3「只失效不刪除」及憲章 L135「未過 GATE＝判死留檔」不對稱，淘汰名錄現 | ENFORCE 補句：「移除＝**狀態轉 superseded／retired 並留痕**（判準、五鏡證據、判死時點、判死者 identity）於特徵狀態帳本，**不得刪列**；復活須重走提拔關卡，不得沿用舊判死列之分數 |
| G26 | E | L | `docs/原則精華_v1.10.0.md` | 「升版哲學」（L162-168） | 行走者⑧（法律自己）之路在本檔只剩版本號規則：未載**誰有權升版**（Steward 親簽、AI 不得自行修法，對照 MC §8.1「Agent 不得參與修憲與解釋」）、未載**證據先於結論**要件（§8.5(a)）、未載**被否決提案之留檔**——同檔 as | 升版哲學增三行：「**修法權**：本檔任何條文之增修、刪除、判準變更一律由 Steward（hugo）親簽方生效；AI 僅得提議措辭與附證據，不得自行實施。**證據先於結論**：判準變更須附 source-traceab |
| G27 | C | M | `docs/原則精華_v1.10.0.md` | 「條號導讀」四類分布（L14）／全檔 | 本檔登錄重心為 Layer 4（Knowledge System），卻全無知識層准入法律——行走者②（人類原典）③（思想原理）之硬閘（禁 AI 生成入庫、全文准入三軌 license／owned_local、素養層不進預測管線、新域納入須人拍板）全住 Laye | 二擇一並落文：(甲) 於 A 區新增一條「知識層來源純度」原則，把三項不變式（真實文獻、禁 AI 生成入庫、素養層零量化價值不進預測管線）以 WHAT/WHY/ENFORCE 寫入本檔；(乙) 最小處置——於 #9 後加 |
| G28 | E | M | `docs/原則精華_v1.10.0.md` | #16 Clean-Room WHAT（L145） | clean-room 之來源白名單為封閉列舉，monorepo 併入後已過期——未含現行 lex superior 之 AUGUR-MC v1.6 與 constitution/／specs/ 之 L1–L7 七份規格（GOVERNANCE-MAP 為統一入口 | 改為分層列舉：「只依 (i) 上位治權 `AUGUR-MC v1.6` 與 `constitution/`／`specs/` L1–L7 現行規格、(ii) augur 領域 5 治權檔（靈魂／原則精華／憲章／CLAUD |
| G29 | E | L | `docs/原則精華_v1.10.0.md` | #15 誠實回報 ENFORCE（L127） | 報告書核心第 6 點「誠實的無能宣告與有效的能力宣告同為合法產出」在本檔（自稱法律全文之 SSOT）無明文支撐：#15 只寫「不入」（不得寫），未把「查無／證據不足／拒答」立為合法且必須可表達之產出；其依據現只在 MC P4.E5 與憲章 v1.25.0／v1 | #15 ENFORCE 補一款：「**無能宣告為合法產出**：『目前證據不足／查無可答語料』係必須可表達之系統狀態與合法交付（承 P4.E5），不得為求可交付而以推估、外部記憶或降格證據填補；拒答須留痕並回流為量尺題材。 |
| G30 | C | M | `docs/系統架構大憲章_v1.49.0.md` | 第六部 升版規則 · 第 3 點（L277） | 行走者⑧「法律自己」在本檔留有一條無人簽、無升版、無修訂歷程留痕之修法通道，且「純文字微修正」與「判準變更」之界分既無判準亦無機械閘，故本檔條文可被 Agent 逕改而事後不可稽核（與 MC §8.1「Agent 不得參與修憲與解釋」正相衝）。 | 建議 Steward 於第六部加入：「(a) 本檔任何條文改動（含純文字微修正）一律留一列修訂歷程並記 actor；(b)『純文字微修正』界定＝不改變任一條文之適用範圍、義務主體、判準值或閉集內容，凡有疑即歸判準變更；( |
| G31 | E | M | `docs/系統架構大憲章_v1.49.0.md` | 第三部 philosophy「來源治理／知識准入不變式〔v1.4 | 本條宣告「進庫≠可答」卻未於任何處給出「何時可答」之判準、證據通道或人閘；可答性升格全由機械 actor（`system:kh10_auto_admit`）依自身 KH 水印 UPDATE 自判，無獨立證據要求，構成行走者②（人類原典）在本檔之路徑空懸，並與  | 建議 Steward 補訂：「可答（進入 KH4 Retrieval-Answer 之引用池）之最低要件＝(i) 該項已具 KS.20 五元組之信度槽與 as-of 能力等級宣告；(ii) 升格所憑證據不得僅為系統自身產 |
| G32 | E | H | `docs/系統架構大憲章_v1.49.0.md` | 第三部 philosophy「來源治理／知識准入不變式」(1)（ | 同一節內兩條並存且未界分：(1) 稱准入無人核可、機械 actor 得執行狀態機升級；而 L162「得依**決策層人拍板**納入…知識域」與 L163(iii)「新應用域之納入＝決策層人拍板（能抓≠該抓）」仍要求人閘——由於納入新域之機制正是 INSERT r | 建議 Steward 明文界分層級：「來源級（source／item）准入＝機械、無人核可；**域級**（新 `knowledge_domain`／新應用域／成為授權邊界者）納入仍為決策層人拍板」，並於 (1) 句尾加「 |
| G33 | C | L | `docs/系統架構大憲章_v1.49.0.md` | 第六部「答案品質評準（Claude-as-judge 自問自答迭 | 行走者④「AI 能力宣稱」在本檔缺預先凍結之判準與證據通道：本條把 AI 自身設為評準與被評對象，卻未要求任何天花板／地板／錯配對照臂、未要求評測尺預註冊、亦無「不得以自評分數作能力宣稱」之明文，與同檔預言機軸（行走者⑥）之預註冊 GATE ＋多數類樸素基線硬 | 建議 Steward 於本條增列：「凡以本法產生之分數用於任何能力宣稱，須同時揭露 (i) 天花板臂、(ii) 真地板臂（常數／隨機輸出）、(iii) 錯配臂之同尺成績，且評測尺之題集與計分規則須先凍結並留 hash；未 |
| G34 | B | L | `docs/系統架構大憲章_v1.49.0.md` | 第三部 philosophy「共同不變式」②（L158）；同旨複 | 本節經合規聲明標為 L4（知識層），而「何種知識取得量化資格」這一概念層判準之定義錨點被寫成具體資料庫欄位值 `domain='investment'`，違 MC §0.6(b)（L1–L4 不得以 L5–L7 構件為定義依據）與 AUGUR-KS CM.0「 | 建議 Steward 改寫為概念錨＋執行層例示：「投資因子唯一經**投資域學派**條目→原則→原則-因子映射→OOS＋#14 經濟價值全鏈裁決（現行落地＝`philosophy_school.domain='invest |
| G35 | E | M | `docs/系統架構大憲章_v1.49.0.md` | 第一部 系統本質 開篇句（L16）與其下表格「標的／任務／邊界」 | 本檔第一部之系統自我定義僅涵蓋台股預測軸，未涵蓋同檔第三部已明文規定之多域知識素養層、顧問（advisor）出口與受控多使用者 RBAC——v1.49.0 本身即以「第一性原理×太陽能材料」know-how 為例，且素養層已納 quant_finance／so | 建議 Steward 於第一部補一句範圍陳述（不改任何既有判準）：「本系統含兩軸——**預測軸**（台股橫斷面相對強弱，本部所述）與**素養／顧問軸**（多域知識底座與唯讀顧問出口，詳第三部 philosophy 橫切； |
| G36 | E | L | `docs/系統架構大憲章_v1.49.0.md` | 第三部 philosophy「知識域端到端管線（七段一驅）〔v1 | 同節並存兩套自稱「升級判準」之階梯——R0–R4 能力階梯（每級須可機器驗收、通過才升）與 v1.48.0 新入之 KH1–KH10 十層架構（每過一層即 UPDATE 水印、深層 fail 不得回滾）——二者位階、對映關係與孰為 SSOT 皆未宣告，且驗收語 | 建議 Steward 明定二者關係，擇一：(a) KH1–KH10 取代 R0–R4，於 L185 標「R0–R4 已由 KH 階梯承接、退為史料」；或 (b) 兩軸並存但分工明文（R 級＝對外能力宣稱之驗收階梯〔通過才 |
| G37 | C | M | `docs/系統核心思想_v1.8.0.md` | 世界觀表・「自驅動 × 實證（開發 augur）」列（第 122 | 靈魂對「AI 自身能力宣稱」（行走者④）與「評測器／量尺／迭代程序本身」（行走者⑦）全無預先凍結判準、樣本外要求、人閘、判死留檔之明文——只要求 AI 開發時「先實證」，卻未把 AI 自評分數／自我進化能力宣稱本身列為須走同一條路的候選。 | 世界觀增一列「AI 能力宣稱＝候選，不是成果」：(a) 凡對 AI／模型／進化引擎自身能力之宣稱（評測分數、學會某能力、優於前代），與特徵假說同軌——判準須事前凍結、須樣本外、須人閘拍板才成為產品級宣稱，未過即判死留檔； |
| G38 | E | H | `docs/系統核心思想_v1.8.0.md` | 「它預測什麼」・任務列輸出契約三產物③（第 30 行）＋「它不是 | 靈魂之永久除外列舉只寫「逐日價格點位與路徑」，漏「目標價」——而大憲章 v1.49.0 L137（任意粒度之價格點位／路徑／目標價當預測輸出＝永久禁止）與 WM A.38（永久除外項＝逐日價格點位、路徑、目標價；閉集僅①橫斷面相對強弱②絕對方向機率）皆含目標價 | 靈魂「它不是」列補齊為「逐日價格點位、價格路徑、目標價永久不是本系統的預測產物」，並在③後加一句界線：「E[r] 為 horizon 級方向命中率×已實現波幅−成本之聚合換算，不得反算或呈現為個股目標價／價格點位；呈現粒 |
| G39 | D | L | `docs/系統核心思想_v1.8.0.md` | 「最神聖的紀律（敵人①，系統的命）」・零 AI 幻像／Sourc | 系統最高位階紀律以兩家供應商名為判準本體（刪去 FinMind／FRED 後內涵由「兩個具名通道」變為「任何真實觀測通道」＝內涵改變），WM.6 明定本檔適用 WM.4 刪名測試、WM.7 明定資料來源不得成為最高抽象，故現行措辭係以供應商名充定義依據。 | 改寫為「任一特徵值若不是『已登錄觀測通道（Observation Channel）之真實來源回應經數學轉換而得』——而是 imputed／zero-fill／hardcoded／推估／系統自補——即視同幻像」，並於句尾以 |
| G40 | E | L | `docs/系統核心思想_v1.8.0.md` | 「管線（資料如何流動）」末句（第 143 行） | 報告書核心 3 之「後果回流成新觀測→下一圈」在靈魂無明文：靈魂管線為 raw→feature→universe→model→validate 單向五段、且明定各層單向隔離，全檔無「結算／覆盤／違規事件回流為新觀測」之陳述（大憲章 v1.49.0 之「回流」字 | 二擇一並由 Steward 拍板：(a) 靈魂管線節增一句「validate 之結算與覆盤結果本身為新觀測（as-of 落地、帶 provenance），回流為下一圈之候選素材；回流通道不得繞過三敵判準、亦不得使 val |
| G41 | E | L | `docs/系統核心思想_v1.8.0.md` | 「北極星問題」末段擴充句（第 105 行） | 靈魂把假兆③擴及 operational／開發決策，其滿足條件為 probe／實測／code；但 WM A.45（真兆三問之域內可判定形式，明文適用於「凡意圖作為預測或**決策**之 Knowledge 依據之斷言」）之③要求「依預註冊判準完成之樣本外 Evi | 靈魂該句加界分：「本擴充之③於 operational 決策上以『實證（probe／實測／code／DB）而非記憶』為滿足條件；作為預測或結論之 Knowledge 依據時，③之滿足仍須依預註冊判準之樣本外 Eviden |
| G42 | E | H | `reports/augur_all_evolution_next_steps_20260729.md` | §三 T3 第 12 項(41 行);同軸見 open_prob | 本檔把 M2 正式排成月頻(101 期)、open_problems 更以月頻為預設而季頻退為退路,與 META-REPLAY 計畫 §二/§七「先季頻粗掃(34 cutoff)、有訊號才月頻細化」及其「明確不做:月頻細化作為找訊號手段」直接相反;後果不只排程 | 二者取一併留痕:(a) 回到季頻先行,月頻僅在 M2.5 訊號判準過後開;或(b) 由 hugo 明簽「M2 網格改月頻」之修訂,同批在 §六 補「n 由取樣頻率決定,故頻率屬凍結判準之一部;跨頻率不得混同一 proc_ |
| G43 | E | H | `reports/augur_arena_replay_plan_20260729.md` | §附 判準草案(82 行) 與 §補記 R3 發布日親驗(94  | 計畫仍以 ≥60 cluster 為門檻並據此對三隊蓋 ✓,但實查六門 dgate_replay_* 凍結值皆 min_clusters=250(且 auto_trigger 綁該值),補記自估 moirai2 ~195、timesfm ~175 皆低於 25 | §附 與補記之 ≥60 逐字改為 250(與凍結列一致),補記三隊之 ✓ 改為 chronos ✓／moirai2 ✗／timesfm ✗;§七 增一列終態「cluster < min_clusters ⇒ 標 unev |
| G44 | C | M | `reports/augur_arena_replay_plan_20260729.md` | §三 合法窗表(33 行) 對照 §附 判準草案(82 行) | 乾淨隊之窗被寫成 2024-01→2026-06(§一 據此估 ~600 clusters),但 §附 判準只釘 weights_cutoff_ok 與 cluster 數、未釘窗起點(實查凍結列 estimand.panel_window=null),而實跑 | §附 補「panel_window 為判準之一部:乾淨隊窗起點亦須於門評前釘死並寫入 criteria(建議與 meta 計畫之資料地板一致=2018-01,或明簽 2015-01 並揭露地板僅早 1 個月)」;既有兩門 |
| G45 | C | M | `reports/augur_arena_replay_plan_20260729.md` | §附 判準草案 每隊一門枚舉(82 行) 對照 §三(33 行) | majority 在 §三 被列為乾淨隊、且實查 direction_arena_replay 已為其寫入 1,391,879 列(2015-01-05→2026-06-30),但 §附 六隊枚舉不含 majority、live 亦無 dgate_replay | 二者擇一並明文:(a) 補 dgate_replay_majority(同三關、同 250、入家族計數 K=7、alpha 重算);或 (b) §三／§附 明定「majority 為基準臂(base-rate)不設門,其 |
| G46 | C | H | `reports/augur_meta_replay_plan_20260729.md` | §六 meta 門判準草案(53 行) 對照 §七 M2/M3/ | 行走者⑦(迭代程序本身)之路在此斷:唯一凍結門要 ≥60 期(live dgate_meta_replay_* estimand.min_clusters=60 已確認),而 §七 M2 只產 34 期季頻、M3 卻排「meta 門評」＝結構性不可判;通往 6 | §七 補「M2.5:季頻訊號判準」一列,先凍後跑——例如「34 期差值序列之 HAC Eff-t ≥ 1.0 且 mean(diff) > 0 方可開 M4」,並明定 M3 於 n<60 時只出「不可判(n=34/60) |
| G47 | F | M | `reports/augur_meta_replay_plan_20260729.md` | §六 meta 門判準草案(53 行);同型見 arena_re | 報告書核心第 6 點稱「終審永遠是實效與誠實」,但計畫層的終審全是統計級:meta 門三關為 HAC 增益／IC 相對水準／換手揭露,replay 門之凍結列更明文把經濟終關排除於 GATE 之外,且 V2-SUNSET 三條件亦無一為實效級——報告書此點在本 | 二者擇一:(a) 報告書該句降級為「終審之最終形態應為實效,現行各門終審實為統計級,經濟終關為門外另判軸」;或 (b) 提案入判準——meta／replay 門增列「過門後 90 日內須附 run_economic_ev |
| G48 | F | M | `reports/augur_plain_language_full_report_20260730.md` | §四 行走者表「AI 能力宣稱」列（並見 §四導言「全部走同一條 | 報告書把八種行走者陳述為皆有「預先凍結判準＋人類授權門＋判死留檔」之現行路徑，但根檔計畫群中僅①認知候選②人類原典③思想原理⑥模型隊伍⑧法律自己有明文閘（充任認定／admission／arena 門／ultracode＋RULING）；④AI 能力宣稱與⑤模擬 | 二擇一並明示：(a) 降級陳述——該二列改「機制已在個案實作與 audit 留痕（新量尺凍結集＋三軸 rubric、模擬四鎖），**尚未義務化入治權檔**」；或 (b) 提案入憲——由 Steward 於 CODE-MI |
| G49 | F | M | `reports/augur_plain_language_full_report_20260730.md` | §四「具象化：所有具象走同一條路」（八種行走者表之前一段） | 報告以絕對句宣稱八種行走者「沒有誰有特權通道…過同一道人類授權門」，但治權檔明文設有一個有界豁免：WM Annex A A.53 逐字排除「在已生效機械閘全綠且 kill-switch＝clear 時，由進化引擎對哲學原則／特徵登錄所為之狀態晉升 APPLY（ | 報告側降級陳述（不動治權檔）：於該段加註「唯一成文例外＝A.53 之 PME-AUTO-B 有界豁免：機械閘全綠且 kill-switch=clear 時，哲學原則／特徵登錄之狀態晉升 APPLY 屬執行層、不另過逐案人 |
| G50 | C | H | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §2.1 `V2-SUNSET`(已由 hugo 2026-07 | 全程唯一機械化的 program-level 落日判準未釘 set_id/eval_code_hash 亦未含 robot 臂,而實查同一凍結題集(4183475c5089)在生效尺 aeff01c18ace 下 robot F@L1=1.0000 > beh | 以 GATE-raise 對 V2-SUNSET 作升嚴修訂(§2.1 明定放寬不許、升嚴須此程序):(c) 改為「在指定 set_id＋eval_code_hash 下,live 臂於 F@L1 須嚴格勝過 floor |
| G51 | E | H | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §0.3 判讀鐵則(46 行);同義條款見 §3.3 C4(26 | 本檔自稱三軸 SSOT v2,但其兩臂鐵則已被 V2-RUBRIC-go(07-28 生效)之 robot 第五臂取代——src/augur/audit/evidence_protocol.py:32 ARMS 含 robot、:81 明定 live 未嚴格勝 | §0.3／§3.3 C4／§7 A4／§11.1 四處同批改為「須同時勝過 floor、mismatched 與 robot(robot 在場時);判讀一律引用 evidence_protocol.evidence_le |
| G52 | C | H | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §4.2.4 `evolution_evidence_run`  | TW／RAW 之證據通道在表層封死五臂枚舉、無 robot 槽(live CHECK 實查確認),故 V2-RUBRIC-go 後成為必跑的 robot 對照臂在 tw/raw 兩軸物理上無法入帳,§3.3 C4「兩者共用同一份純函式判讀」實質破裂——只有 L | §4.2.4 之 arm CHECK 補 'robot'(並於 §4.3 增列一條冪等 ALTER … DROP CONSTRAINT/ADD CONSTRAINT 之遷移列),同批於 §7 A4 明定 tw/raw 之 |
| G53 | C | H | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §4.2.8 註(542 行) | 行走者④(AI 能力宣稱)之判準凍結落點被明文延後,實查 evolution_prereg_gate 至今僅 V2-SUNSET 一列(無 axis='lai' 列),而同期 eval_code_hash 兩日內五換(f3075238eb55→ef142e93 | 依 §4.2.8 自訂之復活條件(「新尺經 ≥1 次完整分叉後」已於 07-28 達成)開 axis='lai' 之 prereg 列,凍結{set_id, eval_code_hash, 五臂鐵則, F@L1 判讀規則 |
| G54 | E | M | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §12.2 拍板碼表(834 行);同義敘述見 §8 H6(72 | 計畫把 V2-RUBRIC-go 之射程界定為「A 軸內容敏感子判準」,實際生效之變更遠超此範圍——scripts/eval_local_model.py:366 自陳「ABSTAIN_RE 補詞+F 軸加料年份否決+floor 換最強退化常數+robot 第 | §12.2／H6 之 V2-RUBRIC-go 射程逐字更新為實際五項變更,並補一列已知後果「新 floor 使 A 軸 floor=1.000 ⇒ A 軸無可證格,禁以 A 軸主張任何進步」;若 hugo 認為射程擴張 |
| G55 | E | M | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §4.2.8 新表 + §10「明確不做」列(778 行) | 本檔新增 evolution_prereg_gate 成為第四張判準凍結登錄簿(四張皆實查存在),同時明文無限期不合併,致「全系統已凍判準與其家族」無法單一查詢;實錄後果已出現——六門 dgate_replay_* 之 family_disclosure 仍逐 | §10 該列補「不合併,但須有跨表清單」之替代義務:新增一支唯讀腳本(或 verify_evolution_acceptance 增一 check)列印四張 registry 之全部 gate_id／status／fam |
| G56 | B | M | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §3.2 邊 1 之「RAWEVO R3 差分之處置」(200  | 「第 N 輪新發現什麼」是概念層問句,此處卻以既有 schema 之執行層限制(field_correlation upsert-in-place、無 run 維度)反向定義該概念,使 raw ledger 的 gain_basis='new_gap' 之「n | §3.2 邊 1 補一句概念先行之定義與其獨立錨:「new_gap 之定義＝以 raw_table_coverage_snapshot 之 gap_class 逐輪比對(該表有 iteration_uid 維度,可支撐真 |
| G57 | C | H | `reports/augur_ten_layer_knowhow_architecture_plan_20260728.md` | §3 KH7 驗收(421 行)、KH8 驗收(460-464  | 全檔 rg 零命中「預註冊／凍結判準／對照臂／floor／停損／落日」,而 KH2 產 recommend_score、KH8 產 evidence_score 與 confidence_band——分數化輸出卻無 ceiling/floor/robot 對照 | §3 KH7／KH8 各補一列「凍結判準與對照臂」:evidence weighting 與 eligibility 須先預註冊(建議落 evolution_prereg_gate,axis 新增值或另立 kh 軸)並附 |
| G58 | C | M | `reports/augur_ten_layer_knowhow_architecture_plan_20260728.md` | §8.2 KH10-S4 驗收(770 行);§9 風險表、§1 | 十層架構之四階段驗收皆為「KHx 成立」之同語反覆,全檔無 program-level 落日、無停損 N、無失敗定義——即這條路對「迭代程序本身」沒有判死出口,恰是 master plan §2 認定 v1 最缺且列為 v2 最重要新增的那一件(「讓整個計畫可 | §11 增一碼 `KH10-SUNSET`(內容由 hugo 親填,AI 不代選),形如「至 <期限>,若 KH7 未產出任一經對抗檢定之 contradiction 留檔、且 KH8 未有任一分數通過對照臂,則 KH1 |
| G59 | E | M | `specs/AGENT-RUNTIME-SPECIFICATION.md` | L6.21（F6 執法點）第二段「誠實輸出契約之行動側承接」；並 | L6.21 之 [N] 文字將產物閉集登錄機制與 DB trigger 級零寫入強制之物理落地繫於「俟 L7 §8.2」，然 L7 §8.2 深度審查已於 2026-07-19 作成（RULING-2026-025），而 L7 全文零提 D28／產物閉集／展示 | 由 Steward 擇一裁定並成文：(甲) L7 側增列 LDI 承接列＋Annex OPEN 條目（保守預設＝產物閉集未登錄期間任何預測性數字不得對外呈現且產物表零寫入，期限與義務主體具名）；(乙) 於 L6.21 明 |
| G60 | C | L | `specs/IDENTITY-SPECIFICATION.md` | ID.51（未解析存量之可稽核指標）末段；對照 WM.21(d) | WM.21(d)／D4 把「provisional identity **解析時限** 與未解析存量稽核指標」一併 DEFER 至 Layer 3；ID 只交付了指標（a)(b)(c) 三項，把門檻／時限再下推 L4（IDO.4），KS.83(i) 又只定「納 | 請 Steward 擇一裁定並成文：(甲) ID 增訂一條（啟用 ID.52–53 之後之保留號，如 ID.54）定「解析時限」之概念形式——以相對時點述語表述（例如「自 provisional 進入起，於該 Type  |
| G61 | C | H | `specs/INFRASTRUCTURE-SPECIFICATION.md` | L7.42(f)（雙人類獨立核准之憑證獨立性）；Annex OP | L6.13／L6.18(b-1)／L7.5(b)／L7.44(h)／L7.45 棘輪之推翻通道全繫於「事前雙人類獨立核准」，而其第二人類（MC Appendix F／RULING-2026-017 §8.1 拓撲所稱「附則指定之獨立確認者」）迄未於 GOVER | 二者並行：(a) 由 Steward 以附則 minor 具名指定獨立確認者（含其憑證持有形式與 L7.42(f) 不共享主體／工作階段／設備之落實方式）；(b) 於 Annex OPEN 增列 OPEN-L7-08「雙 |
| G62 | E | L | `specs/INFRASTRUCTURE-SPECIFICATION.md` | L7.16（不變式強制之權限錨定）可判定判準末段 | L7.16 課「每一受保護儲存物件之拒絕須由可執行回歸測試逐項驗證」，卻於同一 [N] 判準自承覆蓋僅及單一掛點、其餘「俟擴充」——此為文件自承之收編缺口，然未依 L7.3(b)／L7.70(b) 登錄為 OPEN 條目，故無到期日、無義務主體、亦無明文之保守 | 於 Annex OPEN 增列條目「受保護儲存物件之拒絕測試矩陣未完備」，五欄為〔事項＝L7.16 判準之全物件測試矩陣；掛鉤＝LDI.41／AUD-02、KS KDO.7；保守預設＝未具通過測試之受保護儲存物件，其 § |
| G63 | E | M | `specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` | KS.84（GATE 統計治理之 Layer 4 Evidenc | HOOK-03 位於 WM Annex B，該 Annex 標 [I] 且自陳「本附錄為資訊性對照…規範效力悉依所引條款本文」；KS.84／KDI.17 卻以此 [I] 列為「明定」L4 專屬設計權之規範依據，而其 [N] 上游 D12 之目標欄實為「L4/L | 二擇一並請 Steward 拍板：(甲) KS.84／KDI.17 之規範錨改為 `AUGUR-WM v1.0 §D12`，並將「統計嚴謹化屬 Layer 4」降為 [I] 佐證引註，同時於 CS.2 增列一條緊張關係（ |
| G64 | A | L | `specs/ONTOLOGY-SPECIFICATION.md` | ONT.13（存在宣告 ↔ 分類體系接合）可判定判準；併 ONT | L2 正文（§2 型別體系總則）之 [N] 可判定判準把第一域 Annex A 之具體條號閉集寫死，ONT.50 亦以「`AUGUR-WM v1.0 Annex A`」為對映義務之唯一對象；WM.52 保證新域只需加 Profile、母法不動，但在 L2 新增 | 建議 minor 修訂：(1) ONT.13 判準改為域中立句「各 Domain Profile ①部存在宣告條之封閉集（由該 Profile 之 A-① 節界定）每一條解析至恰一主型別節點」，把 {A.1–A.30,  |

### 8.3 被對抗驗證器駁回（17 則，不列待辦）

- `docs/系統核心思想_v1.8.0.md` @ 「資料只來自哪」第三項（第 47 行）；連帶「它不做的事：WM A.34 明文把「最小時間粒度＝日」定性為「域宣告，非全系統不變式」，靈魂卻把同一宣告寫成系統級之「抓取的唯一資料本質界線」＋系統級邊界「不做日內」；一旦依 MC  → **駁**：引句字面存在，但缺陷不成立。(a) 靈魂依 MC §0.5 登錄為 Layer 1『領域前身文件』、WM.6 明定其為 Annex A 之 [I] 引註且『非定義依據』——它無法把域宣告升格為全系統不變式；真正的規範落點 A.34 已逐字自帶限定「本
- `docs/系統核心思想_v1.8.0.md` @ 世界觀表・「單一引用源」列（第 119 行）：Layer 1 文件之世界觀信念以執行層構件（helper 函式、panel 表）為判準錨，與 MC §0.6(b) 概念層獨立性之精神、及 WM A.49「度量選集與門 → **駁**：引句存在(L119),但違憲論證不成立,且 finding 自陳「非確定違憲」。三點親驗:(1) MC §0.6(b) 逐字為「Layer 1–4（概念層）之**規格**不得引用 Layer 5–7 之構件作為定義依據」(constitution/M
- `docs/原則精華_v1.10.0.md` @ 「文件性質」段（L7）：所引憲章版本已過期且指向不存在之檔——現行 ACTIVE 為 v1.49.0（docs/ 內只有 v1.47.0〔SUPERSEDED〕與 v1.49.0，v1.48.0 → **駁**：版本行實查不成立。指控之檔 docs/原則精華_v1.10.0.md 已不存在(git status:`RM 原則精華_v1.10.0.md -> 原則精華_v1.11.0.md`);現行 docs/原則精華_v1.11.0.md 第 8 行逐字為「
- `docs/原則精華_v1.10.0.md` @ #1 零幻像 WHAT（L21）：以兩個供應商專名作為「合法特徵值」之定義依據（非例示），刪名測試不過：換供應商或登錄新域（MC P1.E1 開放列舉 ERP／MES／Sensor／Document／Ex → **駁**：指控對象已不存在。(a) 檔案路徑 docs/原則精華_v1.10.0.md 在真實工作目錄已無此檔（`ls docs/` 僅有 原則精華_v1.11.0.md）——一讀 agent 讀的應是 worktree 鏡像（違 CLAUDE #13 之編輯
- `docs/原則精華_v1.10.0.md` @ #4 日為最小單位 WHAT（L36）：第一域（台股日線）之粒度選擇被寫成**系統級**唯一資料本質準則，與 P1.E1 開放通道（Sensor／MES 原生即為 <日）衝突；依 WM.52「新域＝加附錄、母法 → **駁**：引句在現行 v1.11.0 仍存（第 36 行；但 locator 之檔案路徑 v1.10.0 已不存在，屬對舊版鏡像取樣）。缺陷本身不成立：(a) 原則精華依 MC §0.5 登錄為 Layer 4 之『augur 領域治權文件』——第一域文件宣告
- `docs/系統架構大憲章_v1.47.0.md` @ 檔首 SUPERSEDED 橫幅（L3）：殘檔之接續指標指向從未存在之檔案——`docs/` 僅有 v1.47.0 與 v1.49.0（v1.48.0 只有合規聲明、無正文檔，git ls-files 亦證實）， → **駁**：引句已不存在。docs/系統架構大憲章_v1.47.0.md:3 現行逐字為「**SUPERSEDED**：已被 v1.48.0（2026-07-29；知識一律准入）取代;v1.48.0 檔案續改為現行 [`系統架構大憲章_v1.49.0.md`](
- `docs/系統架構大憲章_v1.49.0.md` @ 第三部 validate「預言機誠實判準」·逐日價格點位：報告書核心第 3 點稱「八種行走者皆走此路、無特權通道」、第 6 點稱終審永遠是實效與誠實，卻漏載本檔兩項重要義務：(a) 逐日價格點位／路徑／目標價屬**無任何證據通道 → **駁**：引句逐字存在（L137「**無 GATE 可解**(解除唯再修憲;用戶 2026-07-11 拍板 P1-4 鎖死)」、L141 no-v3），但「報告書漏載」為事實錯誤——報告書 §四三條補注第一條（reports/augur_plain_lang
- `CLAUDE.md` @ #25 測試用最小單位（並及 #24 API 限速）：「取用外部觀測通道須先最小探測、不得高併發狂打」本身是域中立紀律，卻被寫死成第一域用語與供應商：#25 以「單一個股＋單一日期（`data_id=X`）」為最小單位定義、 → **駁**：引句字面正確（CLAUDE.md:87），但『新域按字面即無任何限速與最小探測義務』被原文推翻。(a) CLAUDE #24 開頭即自陳「機制 SSOT＝原則精華 #17『三層防護』，**此處僅列工具對映**」，而 #17 WHAT 逐字為「對 Fi
- `CLAUDE.md` @ #28 模型檔位分派表（三列檔位）：分派義務之列以具名商業模型版本（Fable 5／Opus 4.8／Sonnet 5）為定義依據：刪去這些名字，表格即無內容（雖上一句之抽象裁決句仍存），供應商改版即令本檔 → **駁**：引句字面正確（CLAUDE.md:100），但『刪名即無內容』與『以 L6 規則之姿承載 L7 選型』兩支柱皆不成立。(a) 刪名測試過關：表格第二欄為抽象定位（理解／裁決層｜重執行／複雜實作｜輕執行／看顧）＋第三欄作業類型，且上一句即抽象裁決句「搞
- `README.md` @ 檔頭「🚧 狀態」段（L30）＋「先讀這幾份（治權檔）」表：門面版本行過期且指向不存在之法：實測 docs/ 僅有 系統架構大憲章_v1.47.0.md（自標 SUPERSEDED）與 _v1.49.0.md，v1.48.0 檔案 → **駁**：版本行實查不成立。README.md:30 現行逐字為「治權已立（靈魂 v1.8.0・原則精華 v1.11.0…・**憲章 v1.49.0・CLAUDE v1.31**——歷次入憲演進之明細見憲章「修訂歷程」…）」;L42 連結現行為 `docs/系
- `README.md` @ 檔頭引言（L3）／副標（L19）：合倉後同一門面同時是 L0–L7 世界層法典（constitution/、specs/）之入口，卻以單一域目標「誠實預測台股」定義整倉，而 AUGUR-WM v1.0 A → **駁**：引句已不存在於 live README。現行 README.md:3 為「**以持續一致的身分與可追溯的證據，忠實表徵真實世界，據以產生可信的判斷**（憲法永恆條款 AUGUR-MC v1.6 §1.1）——只讀真兆，不造假兆。**法屬世界、域為足跡
- `ARCHITECTURE-OVERVIEW.md` @ §三 8 層結構後之「技術棧落點」段（L45）：以供應商名充當憲章角色之等同定義，違刪名測試：MC v1.6 Appendix C 第 1 點明載「原 §4 之產品名（PostgreSQL、Neo4j、Vector D → **駁**：引句字面存在（ARCHITECTURE-OVERVIEW.md:45），但不構成缺陷。(a) 本檔標題即 `[I]`，第 3 行自陳「**[I] 資訊性文件（Informative，非規範性）**——給人閱讀的架構總覽／導覽圖，**不創設任何義務、不
- `reports/augur_self_evolution_master_plan_v2_20260726.md` @ §3.3 C3 第一版(250 行);同型見 §9 原則：重活互斥這條不變式(單機 LLM 推論須序列化)是產品無關的,卻以供應商產品名界定鎖的射程;本檔同時已在規畫 llama.cpp／convert_lora_to_gguf → **駁**：兩處引句字面正確（:250、:758），但『A8 驗收亦以此射程為準』與『將出現非 Ollama 推論入口』兩個關鍵前提經實查皆不成立。(a) A8 驗收條件逐字為「重活互斥：同一時間窗內 `steps_json` 標 **heavy** 之 ste
- `specs/WORLD-MODEL-SPECIFICATION.md` @ WM.9（權威三分）(a) 形權威——義務主體句：WM.9 是世界層（域中立）正文條款，卻把「治權文件」定義成第一域四份領域文件＋一份 L6 Agent 規則＋一份第一域資料集參考之封閉集，使 WM.9(a)(c)「形權 → **駁**：引句字面正確（WM.9(a) 義務主體句，:141），但『義務主體只對第一域成立、須改 L1 正文才能擴及新域』不成立。(a) WM.9 之規範核心不繫於義務主體清單：首句為「系統內**一切**『權威』『真相』『事實』之宣稱，必須解析為下列三個……」
- `specs/INFRASTRUCTURE-SPECIFICATION.md` @ L7.45(f-4)（量測參數與 RT 級之量測面綁定）：L7 為域中立之 Layer 規格，然其跨域適用之 [N] 量測參數以第一域單位表述——「250 個交易日」（交易日僅存於市場域，工廠／感測器／文件域無此單位）與 I3  → **駁**：引句字面正確，但條文自身之限定與缺位規則使『新域無法在不改寫本款下適用 RT-2 以上閘』不成立。(a) 該數值在原文即自標域級：「其**最低樣本數 ＝ 250 個交易日**（**領域基線**，得由 Domain Profile 收緊）」；(d) 之
- `specs/AGENT-RUNTIME-SPECIFICATION.md` @ 【地位】節第 3 點（§8.2 實質合憲人類審查）；併 ：報告書核心第 5 點稱「AI ……不得碰人類授權門與修法權」，但治權檔實況為：界定人類授權門之 L6／L7 規格本身由 Agent 起草（L6【地位】、L7.5 自陳）， → **駁**：引句逐字存在（L6【地位】:14「本層為 Agent 自撰之「人類權威層」」），且「MC §8.1 之禁令僅及修憲與解釋、不及規格起草」之觀察正確。但據以指控報告書「誇大、缺 [N] 支撐」不成立，兩點皆被原文推翻：(1) 報告書並未隱匿起草事實——
- `specs/INFRASTRUCTURE-SPECIFICATION.md` @ L7.5(d)（合規之證明形式）；併 L7.16、L7.：治權檔於末層設有一條與量尺精神同等重要之義務——「合規之證明形式為可執行測試，文件宣稱不構成證明；未經實測之備份推定為不存在」——報告書六點核心（含第 4／6 點之誠實與 → **駁**：引句逐字存在（L7.5(d) 及 L7.16 等處「文件宣稱不構成證明」），但「報告書六點核心完全未載」為事實錯誤：報告書 §六（末層節，:95）已逐字載此義務——「**一切合規須以「可執行測試實際觀測到拒絕」證明，文件宣稱不算數**；**未經實測的

### 8.4 處置原則

- **機械軌**：分批執行、每批一 commit、每批後跑 `check_treaty_refs.py`＋`check_cmd_matrix.py`；**凡執行時發現實涉判準文字者，即改判並移入 8.2**（不因分類已寫成機械就硬做）。
- **判準軌**：不逐則呈簽（64 則會癱瘱決策），由我按同一議題聚合成議題包，每包一次拍板——聚合見 §九。
- **稽核射程限制（誠實）**：多位讀者未讀 specs 全文（僅抽條 grep），涉 WM／ONT／ID／KS／L5／L6／L7 原文之部分論述未回原文覆核；另有讀者因 `psql` 角色問題未連 live DB，其 DB 層宣稱僅驗到 repo DDL。此二限制已在各則嚴重度中折扣，且不得作為「已驗證」之依據。


---

*上位依據：`AUGUR-MC v1.6`（§0.6 lex superior／§4 EV 鏈／§8.1 解釋界線）；`AUGUR-WM v1.0 §WM.4/WM.7/WM.52`；`AUGUR-KS v1.1 §KS.4`；領域：`docs/系統核心思想_v1.8.0.md`／`docs/原則精華_v1.10.0.md`／`docs/系統架構大憲章_v1.49.0.md`／`CLAUDE.md v1.31`。量尺：`reports/augur_plain_language_full_report_20260730.md`（v11）。*

## 九、判準軌 64 則之議題包（呈簽單位；一包一次拍板）

> **聚合理由**：逐則呈簽 64 次會癱瘱決策；按「同一議題聚合」成 10 包，每包附我的處置建議與可拍板選項。**拍板格式**：`P1-照案`／`P1-駁`／`P1-改為…`（可一次多包：`P1,P4,P9-照案`）。

| 包 | 則數 | high | 主要檔 | 我的建議 |
|---|---|---|---|---|
| **P1 一條路法源空懸(C 類)** | 19 | 6 | CLAUDE.md, GOVERNANCE-ANNEX.md, HANDOFF.md, IDENTITY-SPECIFICATION.md… | **建議：與乙-3 合併為一次修憲**。19 則同因一果——治權層沒有「普遍晉升路徑」總則，於是每條線各自空懸；其中最硬的是**行走者④（AI 能力宣稱）與⑦（迭代程序本身）在治權層完全無預先凍結判準／人閘／判死留檔之明文**。乙-3 草案 |
| **P8 知識層准入/KH10 vs P2.E1** | 6 | 2 | CLAUDE.md, GOVERNANCE-MAP.md, augur_arena_replay_plan_20260729.md, 系統架構大憲章_v1.49.0.md | **建議：先出一頁合憲性分析再裁**（＝乙-5）。核心衝突：KH10 讓機械 actor `system:kh10_auto_admit` 依自身水印 UPDATE 自判可答性、無獨立證據要求，而同檔 L162／L163(iii) 仍要求新 |
| **P11 其他跨檔判準矛盾** | 23 | 3 | AGENT-RUNTIME-SPECIFICATION.md, CLAUDE.md, CS-CLAUDE.md, CS-系統核心思想_v1.8.0.md… | **建議：拆兩批**。(a) 三則 high 之閉集不一致先修（靈魂永久除外列舉漏「目標價」，而大憲章 L137 與 WM A.38 皆含之——閉集不一致等於留了一個可鑽的口）；(b) 其餘 20 則按檔分批，逐檔一次呈簽。 |
| **P3 概念層被執行層定義(B 類 §0.6(b))** | 4 | 1 | CS-CLAUDE.md, augur_self_evolution_master_plan_v2_20260726.md, 原則精華_v1.10.0.md, 系統架構大憲章_v1.49.0.md | **建議：一次修四處**。皆為概念層條款以 L5–L7 構件為定義錨（`arena_adm_5305655ad1cd` DB 列 id、`direction_gate` 物件、`domain='investment'` 欄位值）；修法＝把錨 |
| **P9 版本/條號/引用格式規範** | 4 | 1 | CS-CLAUDE.md, GOVERNANCE-ANNEX.md, augur_self_evolution_master_plan_v2_20260726.md, 原則精華_v1.10.0.md | **建議：照案批一次**。含「誰有權升版」未載（對照 MC §8.1 Agent 不得修法）、被否決提案未要求留檔、CS 以一句概括掃「不觸及」違 WM.44 逐條具名義務。 |
| **P5 報告書↔治權檔落差(F 類)** | 3 | 0 | augur_meta_replay_plan_20260729.md, augur_plain_language_full_report_20260730.md | **建議：改報告書、不改治權檔**。稽核指出我報告書兩處超出治權層現況：①「八行走者皆有現行閘」實則④⑤無；②「終審永遠是實效與誠實」實則 meta／replay 門之終審全為統計級、經濟終關明文排除於 GATE 外。**我已於本輪逐處降級 |
| **P2 域錨與世界層定義(A/靈魂定義句)** | 2 | 0 | ONTOLOGY-SPECIFICATION.md, 系統架構大憲章_v1.49.0.md | **建議：與乙-1 合併**。大憲章第一部之自我定義僅涵蓋台股預測軸，未涵蓋同檔第三部已明文之多域知識素養層與 advisor 出口；ONT 正文把第一域 Annex A 條號閉集寫死，與 WM.52「新域只加 Profile、母法不動」相 |
| **P4 刪名測試(D 類)** | 1 | 0 | 系統核心思想_v1.8.0.md | **已由乙-2 部分閉合**（原則精華 #1 已改）；本則指向**靈魂**同型措辭（以 FinMind／FRED 為判準本體），屬乙-1 之同一批，隨乙-1 一併處理。 |
| **P6 硬體/環境登錄值失效(L7 [I] 欄)** | 1 | 0 | INFRASTRUCTURE-SPECIFICATION.md | **建議：照案改 [I] 值＋補登 OPEN**。L7.16 自承覆蓋僅及單一掛點卻未依 L7.3(b)／L7.70(b) 登錄為 OPEN（無到期日、無義務主體）；連同我另抓到的 L7.51(b)(c) 仍寫 GB10 之 121 GiB |
| **P10 cluster 門檻與確立級判準** | 1 | 1 | augur_all_evolution_next_steps_20260729.md | **建議：與『60 vs 250』一併裁**。本則另揭一事：`augur_all_evolution_next_steps` 把 M2 排成月頻，與 META-REPLAY 計畫「先季頻粗掃、有訊號才月頻細化」及其『明確不做：月頻細化作為找 |

*（註：原設之 P7「嵌入口徑／具名模型入條文」聚合後零命中——該類皆附通則語而過刪名測試，已由驗證器歸入 E 類機械軌。）*

### P1 一條路法源空懸(C 類)（19 則）

**建議：與乙-3 合併為一次修憲**。19 則同因一果——治權層沒有「普遍晉升路徑」總則，於是每條線各自空懸；其中最硬的是**行走者④（AI 能力宣稱）與⑦（迭代程序本身）在治權層完全無預先凍結判準／人閘／判死留檔之明文**。乙-3 草案條文一旦入憲，本包 19 則多數自動閉合。

| 嚴 | 檔 | 位置 | 疑義 | 建議措辭 |
|---|---|---|---|---|
| M | `docs/系統核心思想_v1.8.0.md` | 世界觀表・「自驅動 × 實證（開發 augur）」列（第 1 | 靈魂對「AI 自身能力宣稱」（行走者④）與「評測器／量尺／迭代程序本身」（行走者⑦）全無預先凍結判準、樣本外要求、人閘、判死留檔之明文——只要求 AI 開發時「先實證」，卻未把 AI 自評分數／自我進化能力宣稱本身列為須走同一條路的候選。 | 世界觀增一列「AI 能力宣稱＝候選，不是成果」：(a) 凡對 AI／模型／進化引擎自身能力之宣稱（評測分數、學會某能力、優於前代），與特徵假說同軌——判準須事前凍結、須樣本外、須人閘拍板才成為產品級宣稱，未過即判死留檔；(b) 量尺本身亦為候選：任何評測器在其分數被引為能力證據前，須先證明能分辨天花板／地板／錯配三臂（不能分辨即為壞尺、其分數不得引用）；(c) AI 不得以自身輸出為自身能力之證據 |
| M | `docs/原則精華_v1.10.0.md` | FREEZE→解凍子條（L79） | 行走者⑥（模型／隊伍）之相對強度軸 live 准入實為空懸：條文指定之判準 SSOT（reports/augur_prediction_validation_master_plan_20260711.md §4.3）自承「下列為 AI 建議＋論證，非裁決；判準值本身＝拍板點 U1–U6」，而其中唯一管相對強度 live 存活的 G3（校準視窗）／G4（econ 升級）已於 2026-07-16 D-2 Reading A 移出 arena 關鍵路徑、未另指定住所，本檔卻仍以「依 G1-G5」概稱，並以「任何確立級宣 | 補一句射程與缺口誠實化：「本機制現行硬前置僅 G1／G2（方向 arena）；**相對強度軸之 live 准入判準（原 G3/G4）尚未凍結、無現行住所——在其預註冊凍結前，相對強度 live 數字一律止於 review 級、不得入確立級**」；同時把「任何確立級」改為「**方向軸** live 準確率宣稱」以對齊憲章 L136④。（涉判準與宣稱等級，須 hugo 親簽。） |
| M | `docs/原則精華_v1.10.0.md` | #15 誠實回報 WHAT（L125） | 行走者④（AI 能力宣稱）在本檔缺「預先凍結之評測判準＋樣板地板臂」明文：#15 只管多跑取統計與可溯源，未要求任何能力宣稱先凍結量尺並附 ceiling／floor／mismatched 對照臂，故一個常數輸出即可在分數上勝過真模型而不觸任何條文（該類假綠已在本專案 2026-07-26／07-28 實犯，全 repo 治權檔 grep「地板臂／ceiling／mismatched」皆零命中）。 | 於 #15 ENFORCE 增一款：「**能力宣稱前置**：任何以分數宣稱能力（模型／agent／評測器）者，量尺與判準須**先凍結**（sha 留痕）並同輪跑**天花板臂（洩漏上界）／地板臂（不含真訊號之樣板或常數）／錯配臂**；地板臂未被顯著超越者，該分數不得作為能力宣稱、僅得作為量尺缺陷之證據。」（新增義務，須 hugo 親簽。） |
| M | `docs/原則精華_v1.10.0.md` | 「條號導讀」四類分布（L14）／全檔 | 本檔登錄重心為 Layer 4（Knowledge System），卻全無知識層准入法律——行走者②（人類原典）③（思想原理）之硬閘（禁 AI 生成入庫、全文准入三軌 license／owned_local、素養層不進預測管線、新域納入須人拍板）全住 Layer 7 之系統架構大憲章第三部，而本檔合規聲明又宣稱「defers-in []、領域法律由正文自足」，形成 L4 義務在 L4 檔既不承接也不指向之留白。 | 二擇一並落文：(甲) 於 A 區新增一條「知識層來源純度」原則，把三項不變式（真實文獻、禁 AI 生成入庫、素養層零量化價值不進預測管線）以 WHAT/WHY/ENFORCE 寫入本檔；(乙) 最小處置——於 #9 後加指針一行「知識／素養層之准入硬閘全文＝憲章第三部『共同不變式①-④』與『全文准入三軌』」，並在合規聲明補 defers-out D-PRIN-3 指向該節。（涉法律住所，須 hug |
| M | `docs/系統架構大憲章_v1.49.0.md` | 第六部 升版規則 · 第 3 點（L277） | 行走者⑧「法律自己」在本檔留有一條無人簽、無升版、無修訂歷程留痕之修法通道，且「純文字微修正」與「判準變更」之界分既無判準亦無機械閘，故本檔條文可被 Agent 逕改而事後不可稽核（與 MC §8.1「Agent 不得參與修憲與解釋」正相衝）。 | 建議 Steward 於第六部加入：「(a) 本檔任何條文改動（含純文字微修正）一律留一列修訂歷程並記 actor；(b)『純文字微修正』界定＝不改變任一條文之適用範圍、義務主體、判準值或閉集內容，凡有疑即歸判準變更；(c) 條文改動之生效以 Steward 親簽（決策層拍板）為要件，AI 僅得草擬。」不改既有升版級距，僅補人閘與留痕要件。 |
| L | `docs/系統架構大憲章_v1.49.0.md` | 第六部「答案品質評準（Claude-as-judge 自問自 | 行走者④「AI 能力宣稱」在本檔缺預先凍結之判準與證據通道：本條把 AI 自身設為評準與被評對象，卻未要求任何天花板／地板／錯配對照臂、未要求評測尺預註冊、亦無「不得以自評分數作能力宣稱」之明文，與同檔預言機軸（行走者⑥）之預註冊 GATE ＋多數類樸素基線硬綁形成雙標，構成同一條路上的特權通道。 | 建議 Steward 於本條增列：「凡以本法產生之分數用於任何能力宣稱，須同時揭露 (i) 天花板臂、(ii) 真地板臂（常數／隨機輸出）、(iii) 錯配臂之同尺成績，且評測尺之題集與計分規則須先凍結並留 hash；未附三臂之自評分數僅得作內部迭代訊號，禁作能力宣稱或入任何對外數字白名單。」（作用域仍限執行層、不動 guard／誠實閉集。） |
| M | `CLAUDE.md` | 章六 本檔升版 | 本檔承載多條上位不可豁免核心之落地（#9–#12→P4.E1 Evidence 追溯；#14／#26→P5.W2 人類權威；#28→P5.W5），升版節卻只說「不需動憲章」，未排除承載不可豁免核心之條、未要求 Steward 親簽、未要求同步更新 CS-CLAUDE 之 `spec-version`（現為 v1.31，僅靠人工同步）、未要求登錄 AMENDMENT-LOG——即報告書「一條路」之行走者⑧『法律自己』在本檔範圍內無人閘與判死留檔明文，任何弱化都可能被當成「工具慣例更新」。 | 建議 Steward 於章六增列：「(a) 本檔任何**弱化**義務之修訂（含放寬 #6／#14／#19／#26 護欄、放寬 #9–#12 資料真實、放寬人類介入點）不得以『工具慣例更新』為之，須 Steward 親簽並依 `AUGUR-MC v1.6 §8.5` 相應門檻辦理，附 OCV 前後對照（`AUGUR-L6 v1.2` L6.17）；(b) 條號永不重用、永不重排（`§8.6`）；(c |
| L | `constitution/GOVERNANCE-ANNEX.md` | 第 6 條第 1 款（登錄與公開存檔） | 「晉升或判死皆留檔」對行走者⑧（法律自己）在治理層無通則明文：登錄清單只列已通過之產物（修訂／解釋／審查／豁免），未含**被駁回、撤回或未議決之修訂提案及其理由**；RULING-2026-031 第 2 點雖聲明 GOV-4 findings「留檔不滅」，但那是個案裁決自訂，非附則義務——換言之提案之「判死留檔」目前繫於個案善意而非機制。 | 建議 Steward 於第 6 條增第 4 款：「修訂提案（含原則級、minor）不論通過、駁回、撤回或逾期未議決，其提案全文、處置結果與理由一律登錄 Amendment Log 並存於 `constitution/amendments/`；判死之提案不得移除、僅得標記 rejected／withdrawn 並註記裁決號。」屬新增義務，須 Steward 親簽。 |
| M | `HANDOFF.md` | §5 誠實紅線（並連動 §4.4 紅線） | 行走者④「AI 能力宣稱」在本檔缺預先凍結判準之明文：檔頭 2026-07-26 更正已逐字記載尺失效實證（常數樣板 0.654 高於現役 0.492、竄改金標仍得 1.000、think:false 無效），但 §5／§4.4 紅線無「宣稱能力前須跑 ceiling／floor／mismatched 三臂＋題庫先凍結＋人裁」之義務，該紀律目前僅存於個案 audit 與 Claude memory，接續者可原樣重犯。 | §5 增一條紅線：「**能力宣稱須過樣板地板**——任何本地／外部模型或 pack 之能力數字，宣稱前須(1)題庫與判準先凍結並登錄 sha、(2)同批跑 ceiling／floor／mismatched（＋shuffled）對照臂、(3)地板臂未壓過受測臂方得引用、(4)升格／退役經人閘簽核並留判死檔；未附三臂之分數一律標『無證據力』」；並在 §4.4 加「加料年份／改判準後之舊分數自動作廢」之 |
| H | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §2.1 `V2-SUNSET`(已由 hugo 2026- | 全程唯一機械化的 program-level 落日判準未釘 set_id/eval_code_hash 亦未含 robot 臂,而實查同一凍結題集(4183475c5089)在生效尺 aeff01c18ace 下 robot F@L1=1.0000 > behavior 0.9667、floor 由 0.0 漂到 0.3333——同一句判準在不同尺上結論相反,且已可由零知識格式機被超越的臂宣告「續命」。 | 以 GATE-raise 對 V2-SUNSET 作升嚴修訂(§2.1 明定放寬不許、升嚴須此程序):(c) 改為「在指定 set_id＋eval_code_hash 下,live 臂於 F@L1 須嚴格勝過 floor、mismatched 與 robot(缺一即不成立),並由 evidence_protocol.evidence_level() 回 scoped_established 為判據 |
| H | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §4.2.4 `evolution_evidence_run | TW／RAW 之證據通道在表層封死五臂枚舉、無 robot 槽(live CHECK 實查確認),故 V2-RUBRIC-go 後成為必跑的 robot 對照臂在 tw/raw 兩軸物理上無法入帳,§3.3 C4「兩者共用同一份純函式判讀」實質破裂——只有 LAI 側(local_model_eval_run 之自由 arm 欄)能記 robot。 | §4.2.4 之 arm CHECK 補 'robot'(並於 §4.3 增列一條冪等 ALTER … DROP CONSTRAINT/ADD CONSTRAINT 之遷移列),同批於 §7 A4 明定 tw/raw 之 gain=true 亦須有 robot 列在場;因涉「什麼算證據」之範圍,須 hugo 併 GATE-raise 簽。 |
| H | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §4.2.8 註(542 行) | 行走者④(AI 能力宣稱)之判準凍結落點被明文延後,實查 evolution_prereg_gate 至今僅 V2-SUNSET 一列(無 axis='lai' 列),而同期 eval_code_hash 兩日內五換(f3075238eb55→ef142e9374c1→0646872fdce7→aeff01c18ace→35aeffc3e160)、floor 之 A 軸由 0.0 變 1.0——「預先凍結」在此軸僅存於計畫散文,門柱實際已多次移動且無 no_goalpost 保護。 | 依 §4.2.8 自訂之復活條件(「新尺經 ≥1 次完整分叉後」已於 07-28 達成)開 axis='lai' 之 prereg 列,凍結{set_id, eval_code_hash, 五臂鐵則, F@L1 判讀規則},並在 §4.2.8 補一句「凍結後換尺＝新 gate_id 新家族,舊列轉 superseded 留檔」以避開「不能修」之顧慮。 |
| H | `reports/augur_meta_replay_plan_20260729.md` | §六 meta 門判準草案(53 行) 對照 §七 M2/M | 行走者⑦(迭代程序本身)之路在此斷:唯一凍結門要 ≥60 期(live dgate_meta_replay_* estimand.min_clusters=60 已確認),而 §七 M2 只產 34 期季頻、M3 卻排「meta 門評」＝結構性不可判;通往 60 期的 M4 之開啟條件「季頻有訊號才開」則無任何預先凍結、機器可判之判準,決定是否燒昂貴路徑的那一步恰好落在人的印象上(該計畫 §七 自陳要防的 p-hacking)。 | §七 補「M2.5:季頻訊號判準」一列,先凍後跑——例如「34 期差值序列之 HAC Eff-t ≥ 1.0 且 mean(diff) > 0 方可開 M4」,並明定 M3 於 n<60 時只出「不可判(n=34/60)」報告、禁述任何增益方向;或把 M2 直接定為足以達 60 期之最小網格並同批凍結該網格(見下一則)。 |
| H | `reports/augur_ten_layer_knowhow_architecture_plan_20260728.md` | §3 KH7 驗收(421 行)、KH8 驗收(460-46 | 全檔 rg 零命中「預註冊／凍結判準／對照臂／floor／停損／落日」,而 KH2 產 recommend_score、KH8 產 evidence_score 與 confidence_band——分數化輸出卻無 ceiling/floor/robot 對照臂、無凍結門檻、驗收全為敘事句(不可機器判),正是 master plan §7 A4 已制度化之教訓(「凡驗收涉及分數提升,一律要求附對照臂」)在行走者②③這條路上完全空懸。 | §3 KH7／KH8 各補一列「凍結判準與對照臂」:evidence weighting 與 eligibility 須先預註冊(建議落 evolution_prereg_gate,axis 新增值或另立 kh 軸)並附 ceiling／floor／robot 三臂實測,未附對照臂之分數禁入任何回答或候選;§8 各 Stage 驗收由「KHx 成立」改為「凍結判準 sha 在先＋對照臂全在場＋機械 |
| M | `reports/augur_arena_replay_plan_20260729.md` | §三 合法窗表(33 行) 對照 §附 判準草案(82 行) | 乾淨隊之窗被寫成 2024-01→2026-06(§一 據此估 ~600 clusters),但 §附 判準只釘 weights_cutoff_ok 與 cluster 數、未釘窗起點(實查凍結列 estimand.panel_window=null),而實跑已到 2015-01-05、n_panels=2,798(momentum/mc 兩門之 result_snapshot)——窗長成為事後可選之自由度,且 250 門檻可單靠拉長窗滿足,對外隊有硬窗、對乾淨隊卻無下界。 | §附 補「panel_window 為判準之一部:乾淨隊窗起點亦須於門評前釘死並寫入 criteria(建議與 meta 計畫之資料地板一致=2018-01,或明簽 2015-01 並揭露地板僅早 1 個月)」;既有兩門已以 2,798 窗判 fail,依「換版=新家族」原則不回改,只在報告揭露窗與 n。 |
| M | `reports/augur_arena_replay_plan_20260729.md` | §附 判準草案 每隊一門枚舉(82 行) 對照 §三(33  | majority 在 §三 被列為乾淨隊、且實查 direction_arena_replay 已為其寫入 1,391,879 列(2015-01-05→2026-06-30),但 §附 六隊枚舉不含 majority、live 亦無 dgate_replay_majority——一個已完整重演的行走者⑥沒有預先凍結的門,其結果可被事後引用而無判準、亦無判死路徑。 | 二者擇一並明文:(a) 補 dgate_replay_majority(同三關、同 250、入家族計數 K=7、alpha 重算);或 (b) §三／§附 明定「majority 為基準臂(base-rate)不設門,其數字僅作 hit-rate 對照、禁單獨引為隊伍表現」——現況之空白須消除。 |
| M | `reports/augur_ten_layer_knowhow_architecture_plan_20260728.md` | §8.2 KH10-S4 驗收(770 行);§9 風險表、 | 十層架構之四階段驗收皆為「KHx 成立」之同語反覆,全檔無 program-level 落日、無停損 N、無失敗定義——即這條路對「迭代程序本身」沒有判死出口,恰是 master plan §2 認定 v1 最缺且列為 v2 最重要新增的那一件(「讓整個計畫可以失敗」)在 KH10 未被繼承。 | §11 增一碼 `KH10-SUNSET`(內容由 hugo 親填,AI 不代選),形如「至 <期限>,若 KH7 未產出任一經對抗檢定之 contradiction 留檔、且 KH8 未有任一分數通過對照臂,則 KH10-S3/S4 整體停止、帳本封存」;§8 各 Stage 驗收改為機械斷言＋凍結判準 sha。 |
| L | `specs/IDENTITY-SPECIFICATION.md` | ID.51（未解析存量之可稽核指標）末段；對照 WM.21( | WM.21(d)／D4 把「provisional identity **解析時限** 與未解析存量稽核指標」一併 DEFER 至 Layer 3；ID 只交付了指標（a)(b)(c) 三項，把門檻／時限再下推 L4（IDO.4），KS.83(i) 又只定「納入語義」並把量測落地推到 L5/L7（KDO.4）——結果無任何一層設定解析時限，D4 之時限半邊在三層之間空懸；而 ID.3 承接盤點與 CS.3 均把 D4 記為「承接（核心）」，形成「宣稱已承接、實則半邊未落地」。依 WM.47／§8.2 較嚴格解讀，D | 請 Steward 擇一裁定並成文：(甲) ID 增訂一條（啟用 ID.52–53 之後之保留號，如 ID.54）定「解析時限」之概念形式——以相對時點述語表述（例如「自 provisional 進入起，於該 Type 之下一個定案性截止日前必須解析或登錄為顯式待決」），門檻值仍 DEFER L6；(乙) 若確認 D4 為選擇性（時限 或 指標），則由 Steward 以 §8.1 解釋明記，並在 |
| H | `specs/INFRASTRUCTURE-SPECIFICATION.md` | L7.42(f)（雙人類獨立核准之憑證獨立性）；Annex  | L6.13／L6.18(b-1)／L7.5(b)／L7.44(h)／L7.45 棘輪之推翻通道全繫於「事前雙人類獨立核准」，而其第二人類（MC Appendix F／RULING-2026-017 §8.1 拓撲所稱「附則指定之獨立確認者」）迄未於 GOVERNANCE-ANNEX 指定（全檔零命中），L7 之 OPEN 清單 00–07 亦無此條目——即人閘之唯一合法核准路徑在物理上不存在，且該空懸未依 L7.3(b)／L7.70(b) 登錄（無保守預設、無義務主體、無期限）。 | 二者並行：(a) 由 Steward 以附則 minor 具名指定獨立確認者（含其憑證持有形式與 L7.42(f) 不共享主體／工作階段／設備之落實方式）；(b) 於 Annex OPEN 增列 OPEN-L7-08「雙人類獨立核准之第二人類尚未指定」，五欄為〔事項＝獨立確認者未指定；掛鉤＝L6.13／L6.14(d)／L6.18(b-1)、MC §8.1 拓撲解釋；保守預設＝一切需雙人類獨立核准 |

### P8 知識層准入/KH10 vs P2.E1（6 則）

**建議：先出一頁合憲性分析再裁**（＝乙-5）。核心衝突：KH10 讓機械 actor `system:kh10_auto_admit` 依自身水印 UPDATE 自判可答性、無獨立證據要求，而同檔 L162／L163(iii) 仍要求新域納入須人拍板；且與 MC P2.E1「禁 AI 直寫永久知識」關係無文件交代。

| 嚴 | 檔 | 位置 | 疑義 | 建議措辭 |
|---|---|---|---|---|
| M | `docs/系統架構大憲章_v1.49.0.md` | 第三部 philosophy「來源治理／知識准入不變式〔v1 | 本條宣告「進庫≠可答」卻未於任何處給出「何時可答」之判準、證據通道或人閘；可答性升格全由機械 actor（`system:kh10_auto_admit`）依自身 KH 水印 UPDATE 自判，無獨立證據要求，構成行走者②（人類原典）在本檔之路徑空懸，並與 AUGUR-KS v1.1 KS.77「self-reported 不得單獨升信」、KS.76（不得僅以系統自身產出為據）方向相反。 | 建議 Steward 補訂：「可答（進入 KH4 Retrieval-Answer 之引用池）之最低要件＝(i) 該項已具 KS.20 五元組之信度槽與 as-of 能力等級宣告；(ii) 升格所憑證據不得僅為系統自身產出（KS.76／KS.77），至少一項獨立來源證據或人類確認；(iii) 判準預先凍結於 DB gate、事後不得挪動。」若 Steward 意在維持全機械，則須明文 waiver |
| H | `docs/系統架構大憲章_v1.49.0.md` | 第三部 philosophy「來源治理／知識准入不變式」(1 | 同一節內兩條並存且未界分：(1) 稱准入無人核可、機械 actor 得執行狀態機升級；而 L162「得依**決策層人拍板**納入…知識域」與 L163(iii)「新應用域之納入＝決策層人拍板（能抓≠該抓）」仍要求人閘——由於納入新域之機制正是 INSERT registry 列（即機械 actor 可自行完成之動作），該人閘既無機制承載亦無範圍界定，讀者無從判定機械新增一個 domain 的來源列是否合法。 | 建議 Steward 明文界分層級：「來源級（source／item）准入＝機械、無人核可；**域級**（新 `knowledge_domain`／新應用域／成為授權邊界者）納入仍為決策層人拍板」，並於 (1) 句尾加「本項不及於域級納入（見本節多域擴充準則與跨域原理映射準則 (iii)）」；同時要求域級新增具機械閘（如 `knowledge_domain` 寫入須帶人簽欄，不得由 system  |
| L | `docs/系統架構大憲章_v1.49.0.md` | 第三部 philosophy「知識域端到端管線（七段一驅）〔 | 同節並存兩套自稱「升級判準」之階梯——R0–R4 能力階梯（每級須可機器驗收、通過才升）與 v1.48.0 新入之 KH1–KH10 十層架構（每過一層即 UPDATE 水印、深層 fail 不得回滾）——二者位階、對映關係與孰為 SSOT 皆未宣告，且驗收語意相反（前者「通過才升」vs 後者「fail 不回滾」），造成同一升格行為可援引兩套互斥判準。 | 建議 Steward 明定二者關係，擇一：(a) KH1–KH10 取代 R0–R4，於 L185 標「R0–R4 已由 KH 階梯承接、退為史料」；或 (b) 兩軸並存但分工明文（R 級＝對外能力宣稱之驗收階梯〔通過才升〕，KH 級＝資料精準度之帳本水印〔不回滾〕，且對外宣稱一律以 R 級為準）。並指定其一為「升級判準」之單一 SSOT。 |
| M | `CLAUDE.md` | #14 Commit / Push 須明示授權 | 本檔只規範 Agent 自己的署名（Co-Authored-By），卻沒有任何一條禁止 Agent 代填「用於證明某事由人做過」的人類簽核欄位（如 promoted_by／approved_by／decided_by／人裁佇列之簽核列）；此為 P5.W2 授權鏈根節點之偽造向量、違 `AUGUR-L6 v1.2` L6.2（禁以非本人主體發起／歸責）與 L6.14／`§P4.E7`（人類確認須以確認者已解析 Identity 為 Source），且屬 L6.18 自我交易紅線——目前僅靠慣例，機械上無明文可據以拒絕 | 建議 Steward 於章一增一條（沿新增順序給新編號，勿重排既有條號）：「**人類簽核不得代打**（承 `AUGUR-MC v1.6 §P5.W2`、`§P4.E7`；`AUGUR-L6 v1.2` L6.2／L6.14）：凡欄位語意為『證明某事由人做過』者（promoted_by／approved_by／decided_by／人裁佇列簽核、治權拍板欄），一律由該自然人親自寫入；AI 不得代填、 |
| L | `constitution/GOVERNANCE-MAP.md` | §3 推薦讀序（新人／Agent）第 3 項 | 報告書核心第 1 點（世界建構讀序 L1→L7）與第 3 點（「一條路」、八種行走者無特權通道）在治權檔中查無明文支撐：`grep -rln '一條路\／行走者\／世界建構' constitution/ specs/ docs/*.md README.md` 僅命中 docs/系統架構大憲章_v1.47.0／v1.49.0，且該處為「一條路打通」之知識管線他義；統一入口之讀序把 L1–L7 降為「需要正式規格時」查閱、未告知各層各答什麼問題，亦無任何「共同成長路徑」之鏈結——報告書之該二點目前為綜述而非現行法。 | 二擇一或並行，均須 Steward 決定：(a) 報告書就此二點明標【[I] 綜述】並逐點附 [N] 依據（候選→證據通道＝MC §P4／KS.70-79；人閘＝§P5.E2／P5.W2；判死留檔＝§P4.E3／KS.50-52），不以「核心」姿態陳述為既存條文；(b) 若欲成為現行法，依 §8.5 提案於 MC 或各 spec 增設「共同成長路徑條款」（列舉行走者類型並宣示無特權通道）。另建議  |
| H | `reports/augur_arena_replay_plan_20260729.md` | §附 判準草案(82 行) 與 §補記 R3 發布日親驗(9 | 計畫仍以 ≥60 cluster 為門檻並據此對三隊蓋 ✓,但實查六門 dgate_replay_* 凍結值皆 min_clusters=250(且 auto_trigger 綁該值),補記自估 moirai2 ~195、timesfm ~175 皆低於 250——兩門結構性不可判,而計畫僅為「查不到發布日」設了誠實棄之終態,對「窗內 cluster 不足」無任何終態處置,兩門將永懸 approved。 | §附 與補記之 ≥60 逐字改為 250(與凍結列一致),補記三隊之 ✓ 改為 chronos ✓／moirai2 ✗／timesfm ✗;§七 增一列終態「cluster < min_clusters ⇒ 標 unevaluable_insufficient_power 並留檔,禁以延長窗湊數、禁以 60 為替代門檻」。 |

### P11 其他跨檔判準矛盾（23 則）

**建議：拆兩批**。(a) 三則 high 之閉集不一致先修（靈魂永久除外列舉漏「目標價」，而大憲章 L137 與 WM A.38 皆含之——閉集不一致等於留了一個可鑽的口）；(b) 其餘 20 則按檔分批，逐檔一次呈簽。

| 嚴 | 檔 | 位置 | 疑義 | 建議措辭 |
|---|---|---|---|---|
| H | `docs/系統核心思想_v1.8.0.md` | 「它預測什麼」・任務列輸出契約三產物③（第 30 行）＋「它 | 靈魂之永久除外列舉只寫「逐日價格點位與路徑」，漏「目標價」——而大憲章 v1.49.0 L137（任意粒度之價格點位／路徑／目標價當預測輸出＝永久禁止）與 WM A.38（永久除外項＝逐日價格點位、路徑、目標價；閉集僅①橫斷面相對強弱②絕對方向機率）皆含目標價，且逐股 E[r] 為 horizon 端目標價之單調變換，界線在靈魂層無一字明文（A.38 可判定判準：非①②且未經增列者依保守解釋不允許）。 | 靈魂「它不是」列補齊為「逐日價格點位、價格路徑、目標價永久不是本系統的預測產物」，並在③後加一句界線：「E[r] 為 horizon 級方向命中率×已實現波幅−成本之聚合換算，不得反算或呈現為個股目標價／價格點位；呈現粒度上限＝報酬率百分比。」同案應由 Steward 決定是否依 WM.52 對 A.38 閉集作 Profile minor 增列（幅度級 E[r] 之任務定性），否則保守解釋下該產 |
| L | `docs/系統核心思想_v1.8.0.md` | 「管線（資料如何流動）」末句（第 143 行） | 報告書核心 3 之「後果回流成新觀測→下一圈」在靈魂無明文：靈魂管線為 raw→feature→universe→model→validate 單向五段、且明定各層單向隔離，全檔無「結算／覆盤／違規事件回流為新觀測」之陳述（大憲章 v1.49.0 之「回流」字樣亦僅出現於禁止語境）。 | 二擇一並由 Steward 拍板：(a) 靈魂管線節增一句「validate 之結算與覆盤結果本身為新觀測（as-of 落地、帶 provenance），回流為下一圈之候選素材；回流通道不得繞過三敵判準、亦不得使 validate 讀訓練產物（隔離不變式不動）」；(b) 若不入憲，報告書須把「後果回流」降級標示為實作現況（arena 結算／覆盤腳本）而非治權檔明文。 |
| L | `docs/系統核心思想_v1.8.0.md` | 「北極星問題」末段擴充句（第 105 行） | 靈魂把假兆③擴及 operational／開發決策，其滿足條件為 probe／實測／code；但 WM A.45（真兆三問之域內可判定形式，明文適用於「凡意圖作為預測或**決策**之 Knowledge 依據之斷言」）之③要求「依預註冊判準完成之樣本外 Evidence」——同一標籤在兩檔對應兩套判準，字面上「以一次 probe 驗證後殺某進程」在 A.45 下仍為假兆（任一問不確定即當假兆）。 | 靈魂該句加界分：「本擴充之③於 operational 決策上以『實證（probe／實測／code／DB）而非記憶』為滿足條件；作為預測或結論之 Knowledge 依據時，③之滿足仍須依預註冊判準之樣本外 Evidence（AUGUR-WM v1.0 §A.45③）。」（或反向由 Steward 就 A.45 作 §8.1 解釋界分適用範圍。） |
| L | `docs/compliance/CS-系統核心思想_v1.8.0.md` | CS.4 形式充分性・跨層標注段（第 68 行） | 該 [N] 聲明與靈魂正文不符：靈魂含 Layer 6 行動禁令（第 153 行「不替使用者下單、不動錢（自動下單＝禁）」）、Layer 7 架構不變式（第 143 行「各層職責不越界…驗證不讀訓練產物」、第 119 行「單一 helper」）、及 RBAC 讀取控制宣告（第 38 行），MC §0.5 明定跨層領域治權檔須由合規聲明逐條／逐節標注 Layer。 | CS.4 跨層標注改為實況：「本檔主體登錄 Layer 1；下列節具跨層落點並依 MC §0.5 逐節標注——『它不做的事』之下單禁令→L6（承 A.53）；『管線』職責不越界與單一引用源→L7／L5（承 A.51，機器強制 DEFER）；『為誰』RBAC 讀取範圍→L6／L7。」由 Steward 於下次 CS 換發時一併簽核。 |
| H | `docs/原則精華_v1.10.0.md` | 檔尾「演進記錄」（L170-177）×#20 ENFORCE | 2026-07-24 commit 8c028ce 實質改寫 #20 ENFORCE 決策層清單（新增「不要求逐案人簽」之人閘豁免、執行層新增 PME APPLY），但檔名未升版、演進記錄無任何一列記載——違反本檔升版哲學「既有原則之重大判準修正 → 升 minor 並記錄演進」，使「法律自己」這名行走者在本檔缺判死/修法留痕。 | 由 Steward 認定該 07-24 改動之等級後補正：若屬重大判準修正→升 v1.11.0 並補演進記錄一列（含 Steward 拍板碼 SOUL-PME-B-yes／採納並寫入、audits/G-PME-SOUL-CLOSED-20260724.md）；若認定為文字澄清→仍須補一列「內文字修正（2026-07-24，不升版）」載明改了 #20 何句、依據何裁決。（僅提議措辭，須 hugo 親 |
| L | `docs/原則精華_v1.10.0.md` | 「資料完整性判準」ENFORCE（L78）vs FREEZE | 同一節內兩條現行規範自相矛盾：ENFORCE 命令 sync 目標「一律」以 2026-05-31 為界，解凍子條卻定「每日增量 sync 為常態、as-of'＝滾動」（另 arena 地基釘 2026-06-30），三個 as-of 並存而未標各自射程。 | 將 ENFORCE 首句改為射程明示：「**歷史**完整性宣稱與其對帳範圍以 as-of `2026-05-31` 為界（定案不變）；**sync 目標**自 2026-07-12 解凍起為滾動（每日至最新交易日）；**arena 資料地基**另釘 `2026-06-30`（G1-PIN，不滾動追）」，並在節首列三 as-of 對照一行。（涉義務射程，須 hugo 親簽。） |
| L | `docs/原則精華_v1.10.0.md` | #7 ENFORCE 第一款末（L54） | P4.E5（禁 last-write-wins）之領域落點僅立規範而把機制無限期掛在「過渡期」：條文本身無落日、無過渡期 fail-closed 措施（如未上鎖前禁 heal 覆寫或強制保留 pre-image），落日只寫在合規聲明（2026-10-14）；且與 repo 實況不同步——`scripts/migrate_raw_supersede_ddl.py` 與 `sync.sync_by_date(snapshot_reason=…)`／`reconcile.heal_by_date` 已於 2026-07- | 條文補兩件：(a) 落日與狀態——「機器落點補正期至 2026-10-14（D-PRIN-2）；現況＝migration＋heal 快照路徑已入 repo（2026-07-17），**待人類實測與部署認證**」；(b) 過渡期處置——「認證完成前，raw 覆寫式 heal 須逐次留 pre-image（或暫停覆寫），不得以『機制未落地』為由行 last-write-wins」。（新增義務，須 hu |
| M | `docs/原則精華_v1.10.0.md` | #15 誠實回報 WHAT（L125） | 三源白名單未排除系統自身之 LLM／agent 產出——「程式輸出（stdout）」字面即涵蓋本系統模型之自陳，與 P4.E7／KS 反自我背書（獨立證據＝來源鏈遞迴不含本系統計算產物、self-reported 僅為宣稱性觀測）措辭衝突；下位之 CLAUDE #28 反而已明定「LLM 意見零證據力」，形成上位寬、下位嚴之倒置。 | 於 (a) 加限定並補一款：「(a) **確定性程式**之輸出（含 stdout／JSON／log）——**系統自身 LLM／agent 之自陳輸出不屬本白名單**，僅為 self-reported 宣稱性觀測，永久攜帶 synthetic／self-reported 標記，不得作為任一量化宣稱之唯一依據（P4.E7）」。（涉判準，須 hugo 親簽。） |
| L | `docs/原則精華_v1.10.0.md` | #11 五鏡特徵治理 ENFORCE（L103） | 行走者①（認知候選）之「判死留檔」在本檔空懸：條文只命令「必移」，未要求判死列以 append-only／superseded 形式留痕（含判死時之判準、證據、時點），與 P4.E3「只失效不刪除」及憲章 L135「未過 GATE＝判死留檔」不對稱，淘汰名錄現僅住方法論報告。 | ENFORCE 補句：「移除＝**狀態轉 superseded／retired 並留痕**（判準、五鏡證據、判死時點、判死者 identity）於特徵狀態帳本，**不得刪列**；復活須重走提拔關卡，不得沿用舊判死列之分數」。（新增義務，須 hugo 親簽。） |
| M | `docs/原則精華_v1.10.0.md` | #16 Clean-Room WHAT（L145） | clean-room 之來源白名單為封閉列舉，monorepo 併入後已過期——未含現行 lex superior 之 AUGUR-MC v1.6 與 constitution/／specs/ 之 L1–L7 七份規格（GOVERNANCE-MAP 為統一入口），字面讀之，依上位憲章義務產生 code 反而落在白名單外。 | 改為分層列舉：「只依 (i) 上位治權 `AUGUR-MC v1.6` 與 `constitution/`／`specs/` L1–L7 現行規格、(ii) augur 領域 5 治權檔（靈魂／原則精華／憲章／CLAUDE.md／README）、(iii) augur 自身 schema 目錄、(iv) live API 實證 建立」。（涉白名單範圍，須 hugo 親簽。） |
| L | `docs/原則精華_v1.10.0.md` | #15 誠實回報 ENFORCE（L127） | 報告書核心第 6 點「誠實的無能宣告與有效的能力宣告同為合法產出」在本檔（自稱法律全文之 SSOT）無明文支撐：#15 只寫「不入」（不得寫），未把「查無／證據不足／拒答」立為合法且必須可表達之產出；其依據現只在 MC P4.E5 與憲章 v1.25.0／v1.35.0 之 advisor 誠實閉集。 | #15 ENFORCE 補一款：「**無能宣告為合法產出**：『目前證據不足／查無可答語料』係必須可表達之系統狀態與合法交付（承 P4.E5），不得為求可交付而以推估、外部記憶或降格證據填補；拒答須留痕並回流為量尺題材。」若不入憲，報告書該點須降級陳述為「L0 有、領域法律未落點」。（新增義務，須 hugo 親簽。） |
| M | `CLAUDE.md` | #26 有界自主推進（章五） | 本條建立的「人→Agent 授權」是 L6.6 意義下的授權委派，卻只寫了 revocability（「授權可隨時收回」）與範圍描述（「護欄內」），缺 expiry（逾期自動失效）、繫結之 Plan 參照、以及授權授予本身之留痕（Observation），亦全篇未引 P5.W2／L6.5–L6.8 為上位依據——即人類權威根節點以口頭、無期限、無留痕方式授出，事後無從機器稽核「這次自主跑動是誰授權、授到哪、何時失效」。 | 建議 Steward 於 #26 首段後增一句：「授權要件（承 `AUGUR-MC v1.6 §P5.W2`、`AUGUR-L6 v1.2` L6.5／L6.6）：每次有界自主授權須明示 (a) 範圍（可為之工作類別與護欄）、(b) 有效期限或結束條件（逾期自動失效，續跑須重新授權）、(c) 可撤銷（隨時收回）、(d) 所繫之計畫／任務參照；四項連同授權時點記入該次工作之報告或任務清單，作為授權鏈 |
| M | `CLAUDE.md` | #28「不自掛長喚醒鏈（省配額）」／#26 自我 promp | 全檔唯一對「連續無人介入之自動執行鏈」設限的句子，理由是省配額而非人類監督；`AUGUR-L6 v1.2` L6.16 之 OCV C 分量（最大自動執行鏈長）、D 分量（逐案可介入點密度）與 L6.17 單調棘輪（C 增加＝推定違憲）在工具層無任何落點——#26 授權「自己 prompt 自己（loop）」可無限延長自動鏈，而#19「一支一支呈用戶過目」只約束實質改動、非每圈迴圈，故新增背景／loop 編排不觸發任何「監督能力是否下降」之檢查。 | 建議 Steward 於 #26 增列「自動鏈上限」子條：「(a) 每次授權須載明本輪最大連續無人介入圈數／時長上限，達上限即停並回報等待人類續授；(b) 凡新增或延長背景編排、排程、自我喚醒鏈者，須於報告中對照前後之『人類介入點數、否決可達性、揭露比例、最大自動鏈長』四項聲明未弱化（承 `AUGUR-L6 v1.2` L6.16–L6.17 OCV 棘輪），任一弱化即屬治權變更、停下問。」 |
| H | `CLAUDE.md` | #28 模型檔位分派表（Fable 5 列） | 分派表把「治權檔增修」「高風險裁決（git 分叉處置/洩漏鑑識）」直接列為 AI 模型之作業項，表內與表後「切換紀律」均無「AI 僅得草擬、議決與解釋權專屬 Steward」之限定句，與 MC §8.1「**Agent（§2.8 意義下之自主程序）不得參與修憲與解釋**」正面衝突，並與 L6.18(a) 反自我交易（Agent 不得為變更自身治理組態之核准主體）相牴；#19／#26 之「變更治權判準→停下問」散在他條，未在本表落點成文，讀表者可據表逕行「AI 做治權檔增修」。 | 建議 Steward 於分派表下方增註：「**檔位≠權限（`AUGUR-MC v1.6 §8.1`）**：本表僅分派『由哪個檔位執行』，不授予任何議決權。治權檔增修、條文解釋、違憲審查與一切裁決之權專屬 Constitution Steward；AI 於此類作業中僅得為草擬、比對與呈案，且不得為涉及自身監督機制（CLAUDE.md 本檔、人閘、OCV 相關組態）之變更之核准主體（`AUGUR-L6 |
| M | `docs/compliance/CS-CLAUDE.md` | front-matter `open-tensions` ／ | 本檔宣稱零緊張關係，但同層正式規格 `AUGUR-L6 v1.2`【地位】節就完全同型的結構性風險作了明文揭露（「本層由 Agent 起草而規範人類對 Agent 之權威，存在結構性自我交易誘因」）——CLAUDE.md 同樣由 Agent 日常增修且規範 Agent 自身之護欄，另有 #28 省 usage（回報精簡／不 fan-out／背景不輪詢）與 P5.W5 監督分量（T／D）之現實張力；WM.42 要求已知緊張關係逐項揭露，宣告 `none` 屬實質未揭露。 | 建議 Steward 令 CS.2 補二列並將 front-matter 改為 `open-tensions: [T-CLAUDE-1, T-CLAUDE-2]`：「T-CLAUDE-1（`§8.1`／L6.18）：本檔由 Agent 起草增修而規範 Agent 自身護欄，具自我交易誘因；緩解＝#19／#26 治權變更停下問＋Steward 親簽＋本檔任何弱化條之修訂須附 OCV 前後對照。T-C |
| M | `docs/compliance/CS-CLAUDE.md` | front-matter `upper-specs` | 清單止於 AUGUR-L5 v1.0，獨漏本檔所登錄之同層正式規格 `AUGUR-L6 v1.2`（Agent Runtime）與 L7（AUGUR-INF）；而本檔 CS.4 自己寫「MC [N] 落點以 `specs/`（尤 `AUGUR-L6`）為權威」、章節標注又列「L6＋L7 操作」——front-matter 與本文自相矛盾，且 WM.44 要求覆蓋「其各適用上層規格之全部 [N] 條款」，漏列即使 L6.1–L6.24（六元組／授權鏈／OCV／風險分級）之對應盤點整段落空。 | 建議 Steward 令 front-matter 補為 `upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v1.0, AUGUR-ID v1.0, AUGUR-KS v1.1, AUGUR-L5 v1.0, AUGUR-L6 v1.2]`（L7 若不受其約束則於 CS.4 明記不觸及及理由），並同案要求 CS.1／CS.4 就 L6.1–L6.24 逐條給出「對應條 |
| M | `docs/compliance/CS-CLAUDE.md` | CS.3(b) 雙向 DEFER 表 defers-out  | WM.43(b) 之 defers-out 為「下放**下層**之掛鉤」，D-CLAUDE-1 的目標卻是同一層（Layer 6）之正式規格，且其說明「正式規格為權威；CLAUDE＝工具層短半衰期」語意是本檔**遵從上位**而非下放；再者全 repo 搜尋 `D-CLAUDE` 僅見於本檔，`AUGUR-L6 v1.2` 之 WM.43 承接表／Annex LDI 未承接此列＝懸空掛鉤（RULING-2026-030 §五(g) 要求目標層須承接並可雙向解析）。 | 建議 Steward 令 D-CLAUDE-1 改分類：自 defers-out 移除，改於 CS.1-P5／CS.1-EV-chain 以 WM.41(b) 閉集值「不適用（附理由）」或「承接」表記——措辭如「Action 六元組／OCV／RT 之形式定義權屬 `AUGUR-L6 v1.2`（同層正式規格，本檔僅消費不重定義，`AUGUR-L6 v1.2` L6.23）；本檔不設下放掛鉤」，並將 |
| L | `CLAUDE.md` | #9 零 AI 幻像（章二） | 三類來源（程式輸出／DB／API）全屬系統自身通道，本檔卻無任何條款要求 AI 自身產物攜帶標記或走預凍評測：全檔 grep 不到 self-reported、synthetic、地板/天花板/錯配對照臂等字樣——即報告書「一條路」之行走者④『AI 能力宣稱』在工具層無預先凍結判準、無獨立證據通道、無判死留檔，而 `AUGUR-L6 v1.2` L6.4 要求 Agent 之 execution receipt「必須永久攜帶 self-reported 標記」、`§P4.E7` 要求 AI 生成內容永久攜帶 syn | 建議 Steward 於章二增一條：「**AI 自身宣稱走同一條路**（承 `AUGUR-MC v1.6 §P4.E7`；`AUGUR-L6 v1.2` L6.4）：(a) AI 產出之文字／評分／裁決意見一律標記為 self-reported，不得作為『世界如此』或『能力如此』之權威確認；(b) 任何『某模型／某流程有某能力』之宣稱，須先跑預先凍結之對照臂（至少：常數/樣板地板臂、上限臂、錯配臂 |
| L | `constitution/GOVERNANCE-ANNEX.md` | 第 2 條第 3 款（patch 門檻） | 自反性缺口：patch 通道未載明「誰得為之」與「誰認定某變更屬 patch」，亦無人閘與施作留痕要件——而 MC §8.1 L489「Agent（§2.8 意義下之自主程序）不得參與修憲與解釋」之落地，全繫於 RULING-2026-028 第 2 點（參與＝實質判斷之作成；繕打／依核示落地＝非參與）與第 3 點（施作留痕＋獨立核驗）之外掛裁決，附則本文對此零交叉引用；字面上一個 Agent 可自行認定「此為編輯修正」並逕行施作。 | 建議 Steward 於第 2 條第 3 款增後句：「patch 之**性質認定**屬 Steward 保留事項；施作得由幕僚（含 Agent）為之，惟須依 Steward 核示、逐案留痕，並依 RULING-2026-028 第 3 點於施作後受非施作者之獨立核驗。Agent 不得自行認定某變更屬 patch（MC §8.1）。」屬新增義務／權限界線，須 Steward 親簽。 |
| M | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §12.2 拍板碼表(834 行);同義敘述見 §8 H6( | 計畫把 V2-RUBRIC-go 之射程界定為「A 軸內容敏感子判準」,實際生效之變更遠超此範圍——scripts/eval_local_model.py:366 自陳「ABSTAIN_RE 補詞+F 軸加料年份否決+floor 換最強退化常數+robot 第五臂+run_id attempt 序」;後果之一:新 floor 之 A 軸實測=1.000(ef14/0646/aeff 三尺一致),使 A4／SUNSET 之「勝過 floor」在 A 軸退化為結構不可能,而計畫未載此變更。 | §12.2／H6 之 V2-RUBRIC-go 射程逐字更新為實際五項變更,並補一列已知後果「新 floor 使 A 軸 floor=1.000 ⇒ A 軸無可證格,禁以 A 軸主張任何進步」;若 hugo 認為射程擴張未經簽核,則另開一份範圍擴充留痕(P4.E3)而非回改既有 audit。 |
| M | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §4.2.8 新表 + §10「明確不做」列(778 行) | 本檔新增 evolution_prereg_gate 成為第四張判準凍結登錄簿(四張皆實查存在),同時明文無限期不合併,致「全系統已凍判準與其家族」無法單一查詢;實錄後果已出現——六門 dgate_replay_* 之 family_disclosure 仍逐字寫「v1 六門+v2 四門+arena 六門=16 門一律全列」,漏計 replay 自身六門與 meta 兩門(共 24),而該句正是 §附「沿用既有 direction gate 三關逐字」所複製。 | §10 該列補「不合併,但須有跨表清單」之替代義務:新增一支唯讀腳本(或 verify_evolution_acceptance 增一 check)列印四張 registry 之全部 gate_id／status／family,並要求任何新門之 family_disclosure 由該清單生成而非手抄;arena_replay §附 同批改為「family 由清單計算,禁逐字沿用他家族之揭露句」。 |
| M | `specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` | KS.84（GATE 統計治理之 Layer 4 Evide | HOOK-03 位於 WM Annex B，該 Annex 標 [I] 且自陳「本附錄為資訊性對照…規範效力悉依所引條款本文」；KS.84／KDI.17 卻以此 [I] 列為「明定」L4 專屬設計權之規範依據，而其 [N] 上游 D12 之目標欄實為「L4/L5」、未把統計治理釘為 L4 獨占——L4 獨占之權源目前只存在於資訊性附錄，位階錯置（違 WM §0.5「[N] 與 [I] 不一致時以 Normative 為準」之精神）。 | 二擇一並請 Steward 拍板：(甲) KS.84／KDI.17 之規範錨改為 `AUGUR-WM v1.0 §D12`，並將「統計嚴謹化屬 Layer 4」降為 [I] 佐證引註，同時於 CS.2 增列一條緊張關係（D12 目標為 L4/L5，本層僅承接其 L4 slice、L5 演算面下放 KDO.3）；(乙) 由 Steward 以 §8.1 解釋（或 WM minor 修訂）把 HOOK |
| M | `specs/AGENT-RUNTIME-SPECIFICATION.md` | L6.21（F6 執法點）第二段「誠實輸出契約之行動側承接」 | L6.21 之 [N] 文字將產物閉集登錄機制與 DB trigger 級零寫入強制之物理落地繫於「俟 L7 §8.2」，然 L7 §8.2 深度審查已於 2026-07-19 作成（RULING-2026-025），而 L7 全文零提 D28／產物閉集／展示分級，其 Annex LDI 33 列與 Annex OPEN 00–07 均無對應條目——依 L7.3(c)／L7.70(b)「既未落點亦未 OPEN 登錄者構成違憲不作為」之判準，此下放已成無收編對象之幽靈指涉。 | 由 Steward 擇一裁定並成文：(甲) L7 側增列 LDI 承接列＋Annex OPEN 條目（保守預設＝產物閉集未登錄期間任何預測性數字不得對外呈現且產物表零寫入，期限與義務主體具名）；(乙) 於 L6.21 明文收回該下放，改記為「本層 fail-closed 介面義務為唯一執法點，物理 trigger 級強制不另設下放」，並刪去「俟 L7 §8.2」之待決語。二案均須同步更新 L6 A |

### P3 概念層被執行層定義(B 類 §0.6(b))（4 則）

**建議：一次修四處**。皆為概念層條款以 L5–L7 構件為定義錨（`arena_adm_5305655ad1cd` DB 列 id、`direction_gate` 物件、`domain='investment'` 欄位值）；修法＝把錨改為概念語意＋把具體物件降為 [I] 現行值（同乙-2 已驗證之手法）。

| 嚴 | 檔 | 位置 | 疑義 | 建議措辭 |
|---|---|---|---|---|
| M | `docs/原則精華_v1.10.0.md` | FREEZE→解凍子條（L79） | 本節在合規聲明中標為純 Layer 4（治權參數），其判準卻以 DB 單列物件 id（`arena_adm_5305655ad1cd`）與 L5/L6 閘物件（`direction_gate` evaluate ≥60 clusters）為定義錨，違 MC §0.6(b)「L1–L4 不得引 L5–L7 構件作為定義依據」，且該列若被 supersede，L4 判準即失指涉。 | 條文層只寫角色語義＋不變式：「live 准入須經**已預先凍結、經人核可之准入閘物件**（現行值＝`arena_admission_gate`，登錄於憲章第三部；判準 sha 不得事後挪動）」——具體 gate_id／sha 移入登錄簿式附表或憲章承載，條文引角色不引列 id。（涉判準錨點，須 hugo 親簽。） |
| L | `docs/系統架構大憲章_v1.49.0.md` | 第三部 philosophy「共同不變式」②（L158）；同 | 本節經合規聲明標為 L4（知識層），而「何種知識取得量化資格」這一概念層判準之定義錨點被寫成具體資料庫欄位值 `domain='investment'`，違 MC §0.6(b)（L1–L4 不得以 L5–L7 構件為定義依據）與 AUGUR-KS CM.0「不以任一 Layer 5–7 具名構件（特定資料庫欄位…）為定義錨點」之同層紀律；欄名或值域一經重構，該判準即失去指涉（刪名測試不過）。 | 建議 Steward 改寫為概念錨＋執行層例示：「投資因子唯一經**投資域學派**條目→原則→原則-因子映射→OOS＋#14 經濟價值全鏈裁決（現行落地＝`philosophy_school.domain='investment'`，僅為 ENFORCE 例示，刪去具名後判準內涵不變）」。判準外延不變，僅移除定義依據之欄位綁定。 |
| H | `docs/compliance/CS-CLAUDE.md` | CS.1-P5（逐原則論證第六節） | 本節同時引 `§P5.E1`、`§P5.W2`、`§P5.W5`（後二者為 §8.4 不可豁免核心），其唯一「判準揭示」卻錨在一支掃 docstring 是否含「執行指令矩陣」字串的腳本上——該腳本與授權鏈根節點、人類否決可達性、監督能力非侵蝕毫無涵蓋關係；同節另有一句評價性斷言「#28 usage 經濟不降低監督」完全未附判準，違 MC §8.3 可判定性元規則（引用評價性謂詞須同時給出可判定判準，未給則採保守解釋）與 WM.41(d)（每一評價性謂詞須附判準或聲明保守解釋），且未引 `AUGUR-L6 v1.2 | 建議 Steward 令 CS.1-P5 改寫判準揭示為三段：「(a) P5.E1／P5.W2＝授權要件四項（範圍/期限/可撤銷/計畫參照）與人類簽核不得代打之明文存在性，逐次授權留痕可稽核；(b) P5.W5＝依 `AUGUR-L6 v1.2` L6.16 OCV 六分量（V/D/A/H/T/C）作前後比較，任一弱化即推定違反、須 Steward 書面裁決；(c) 執行指令矩陣＝`scripts |
| M | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §3.2 邊 1 之「RAWEVO R3 差分之處置」(20 | 「第 N 輪新發現什麼」是概念層問句,此處卻以既有 schema 之執行層限制(field_correlation upsert-in-place、無 run 維度)反向定義該概念,使 raw ledger 的 gain_basis='new_gap' 之「new」退化為「本輪被提為 hint 且 dedup_key 未撞過」——增益判定與「資料層真的出現新缺口」脫鉤,且判定要素由被判定者自己選(提了才算)。 | §3.2 邊 1 補一句概念先行之定義與其獨立錨:「new_gap 之定義＝以 raw_table_coverage_snapshot 之 gap_class 逐輪比對(該表有 iteration_uid 維度,可支撐真差分)為準;hint 層級快照僅為 provenance,不得作為 new 之判據」,並同批修正 §4.2.2 raw 軸 gain_basis 之說明。 |

### P9 版本/條號/引用格式規範（4 則）

**建議：照案批一次**。含「誰有權升版」未載（對照 MC §8.1 Agent 不得修法）、被否決提案未要求留檔、CS 以一句概括掃「不觸及」違 WM.44 逐條具名義務。

| 嚴 | 檔 | 位置 | 疑義 | 建議措辭 |
|---|---|---|---|---|
| L | `docs/原則精華_v1.10.0.md` | 「升版哲學」（L162-168） | 行走者⑧（法律自己）之路在本檔只剩版本號規則：未載**誰有權升版**（Steward 親簽、AI 不得自行修法，對照 MC §8.1「Agent 不得參與修憲與解釋」）、未載**證據先於結論**要件（§8.5(a)）、未載**被否決提案之留檔**——同檔 as-of 子條反而寫得出「須用戶決策後入憲（不由 AI 擅改）」，可見缺的是通則。 | 升版哲學增三行：「**修法權**：本檔任何條文之增修、刪除、判準變更一律由 Steward（hugo）親簽方生效；AI 僅得提議措辭與附證據，不得自行實施。**證據先於結論**：判準變更須附 source-traceable 實證或裁決文號（承 #15／#19）。**留檔**：被退回之提案與其理由同入演進記錄或治理佇列，不得靜默消滅。」（涉治權程序，須 hugo 親簽。） |
| M | `docs/compliance/CS-CLAUDE.md` | CS.4 形式充分性＋跨層標注 | 以一句概括把 MC 現行版全部未觸及之 [N] 條款掃為「不觸及」，既未逐條具名、亦未附理由，與 WM.44「均須對應至…、明記 DEFER 掛鉤、或**明記『不觸及』及理由**；任一條款無對應且無明記者，聲明不完整」不符（同格式之 AUGUR-WM 自身 Annex C.10 係逐一具名盤點）；效果是本檔之形式充分性無法機器判定。 | 建議 Steward 令 CS.4 補一張 WM.44 逐條矩陣（PA／EV.1–EV.12／F1–F6／P1–P5 各條／§0–§8 各節；並及 upper-specs 各規格 [N] 條款），每列填「本檔落點條號｜DEFER｜不觸及＋理由」，並保留現行誠實界限句；矩陣未補齊前，於 CS.2 揭露「形式充分性待補」為 open-tension，而非以概括句宣稱完備。 |
| M | `constitution/GOVERNANCE-ANNEX.md` | 標題行（L1）＋「生效日」（L5）＋「登錄」（L6） | 附則已於 2026-07-23 經 minor 修訂（第 2 條第 1 款強制公示要件廢止；RULING-2026-031、AL-2026-034，AMENDMENT-LOG L368-374 在卷），但版本行仍 v1.0、生效日仍 2026-07-16、登錄仍僅 AL-2026-003——版本語義（MC §8.6：附則變更＝minor）未反映，讀者無法自版本行判斷手中文本是否為現行法，與第 2 條內文之沿革註衝突。 | 由 Steward 裁定版本編號與登錄之更新方式（建議：標題升 v1.1、生效日增列「v1.1：2026-07-23」、登錄行增列 AL-2026-034，並於文末計條句後加一行修訂表）。涉版本語義與登錄之治理記錄，我僅提議措辭、不得自行施作。 |
| H | `reports/augur_self_evolution_master_plan_v2_20260726.md` | §0.3 判讀鐵則(46 行);同義條款見 §3.3 C4( | 本檔自稱三軸 SSOT v2,但其兩臂鐵則已被 V2-RUBRIC-go(07-28 生效)之 robot 第五臂取代——src/augur/audit/evidence_protocol.py:32 ARMS 含 robot、:81 明定 live 未嚴格勝 robot 即回 'none',文件與生效判準器分叉,A4 依文件放行的 gain=true 會被判準器判 none。 | §0.3／§3.3 C4／§7 A4／§11.1 四處同批改為「須同時勝過 floor、mismatched 與 robot(robot 在場時);判讀一律引用 evidence_protocol.evidence_level() 之回值,不得在文件內另述鐵則」,並於 §0 增列一行「07-28 V2-RUBRIC-go 後之鐵則版本」以免再分叉。 |

### P5 報告書↔治權檔落差(F 類)（3 則）

**建議：改報告書、不改治權檔**。稽核指出我報告書兩處超出治權層現況：①「八行走者皆有現行閘」實則④⑤無；②「終審永遠是實效與誠實」實則 meta／replay 門之終審全為統計級、經濟終關明文排除於 GATE 外。**我已於本輪逐處降級標注**（見報告書 §四 註）。

| 嚴 | 檔 | 位置 | 疑義 | 建議措辭 |
|---|---|---|---|---|
| M | `reports/augur_plain_language_full_report_20260730.md` | §四 行走者表「AI 能力宣稱」列（並見 §四導言「全部走同 | 報告書把八種行走者陳述為皆有「預先凍結判準＋人類授權門＋判死留檔」之現行路徑，但根檔計畫群中僅①認知候選②人類原典③思想原理⑥模型隊伍⑧法律自己有明文閘（充任認定／admission／arena 門／ultracode＋RULING）；④AI 能力宣稱與⑤模擬方法在 ROLLOUT 軌道 C、CODE-MIGRATION 擴張軌 2、HANDOFF 紅線中零條文（擴張軌 2 僅要求 spec-first＋audit_lint 綠）。 | 二擇一並明示：(a) 降級陳述——該二列改「機制已在個案實作與 audit 留痕（新量尺凍結集＋三軸 rubric、模擬四鎖），**尚未義務化入治權檔**」；或 (b) 提案入憲——由 Steward 於 CODE-MIGRATION 擴張軌 2 增列「新模型／新能力／新模擬方法之能力宣稱須預先凍結判準＋地板臂＋人閘＋判死留檔」，並在 HANDOFF §5 對偶落地；未經 Steward 親簽前報 |
| M | `reports/augur_meta_replay_plan_20260729.md` | §六 meta 門判準草案(53 行);同型見 arena_ | 報告書核心第 6 點稱「終審永遠是實效與誠實」,但計畫層的終審全是統計級:meta 門三關為 HAC 增益／IC 相對水準／換手揭露,replay 門之凍結列更明文把經濟終關排除於 GATE 之外,且 V2-SUNSET 三條件亦無一為實效級——報告書此點在本群治權檔中無明文支撐。 | 二者擇一:(a) 報告書該句降級為「終審之最終形態應為實效,現行各門終審實為統計級,經濟終關為門外另判軸」;或 (b) 提案入判準——meta／replay 門增列「過門後 90 日內須附 run_economic_eval 之經濟終審,未附者宣稱降級為 statistical-only」,由 hugo 簽 GATE-raise。 |
| M | `reports/augur_plain_language_full_report_20260730.md` | §四「具象化：所有具象走同一條路」（八種行走者表之前一段） | 報告以絕對句宣稱八種行走者「沒有誰有特權通道…過同一道人類授權門」，但治權檔明文設有一個有界豁免：WM Annex A A.53 逐字排除「在已生效機械閘全綠且 kill-switch＝clear 時，由進化引擎對哲學原則／特徵登錄所為之狀態晉升 APPLY（PME-AUTO-B）」於人類授權門閉集之外。該豁免涉及行走者③（思想原理）與⑦（迭代程序）之晉升動作，報告表格卻在 認知候選／思想原理 兩列一律標示「→人閘」，屬誇大陳述。 | 報告側降級陳述（不動治權檔）：於該段加註「唯一成文例外＝A.53 之 PME-AUTO-B 有界豁免：機械閘全綠且 kill-switch=clear 時，哲學原則／特徵登錄之狀態晉升 APPLY 屬執行層、不另過逐案人閘；該 APPLY 不構成下單、不構成預測特徵回流授權，閾值與閘之訂立變更仍屬人閘閉集」。若要維持「無任何特權通道」之絕對敘事，則須提案修訂 A.53（刪除或收緊該豁免）——屬判準 |

### P2 域錨與世界層定義(A/靈魂定義句)（2 則）

**建議：與乙-1 合併**。大憲章第一部之自我定義僅涵蓋台股預測軸，未涵蓋同檔第三部已明文之多域知識素養層與 advisor 出口；ONT 正文把第一域 Annex A 條號閉集寫死，與 WM.52「新域只加 Profile、母法不動」相張。

| 嚴 | 檔 | 位置 | 疑義 | 建議措辭 |
|---|---|---|---|---|
| M | `docs/系統架構大憲章_v1.49.0.md` | 第一部 系統本質 開篇句（L16）與其下表格「標的／任務／邊 | 本檔第一部之系統自我定義僅涵蓋台股預測軸，未涵蓋同檔第三部已明文規定之多域知識素養層、顧問（advisor）出口與受控多使用者 RBAC——v1.49.0 本身即以「第一性原理×太陽能材料」know-how 為例，且素養層已納 quant_finance／software_engineering／owned_local ERP 內容；系統本質段與本檔自身範圍不一致，讀者由第一部無法推知顧問／素養義務之存在。 | 建議 Steward 於第一部補一句範圍陳述（不改任何既有判準）：「本系統含兩軸——**預測軸**（台股橫斷面相對強弱，本部所述）與**素養／顧問軸**（多域知識底座與唯讀顧問出口，詳第三部 philosophy 橫切；零量化價值、不進預測管線）」，並於表格「邊界」列補「顧問軸不產因子、不入預測熱路徑」。 |
| L | `specs/ONTOLOGY-SPECIFICATION.md` | ONT.13（存在宣告 ↔ 分類體系接合）可判定判準；併 O | L2 正文（§2 型別體系總則）之 [N] 可判定判準把第一域 Annex A 之具體條號閉集寫死，ONT.50 亦以「`AUGUR-WM v1.0 Annex A`」為對映義務之唯一對象；WM.52 保證新域只需加 Profile、母法不動，但在 L2 新增第二域必須改動 ONT.13 之可判定判準與 ONT.50 之對象（依 ONT.60 屬實質變更），域中立承諾在 L2 斷掉（報告書 line 49「新域＝加一份規範性附錄，母法一字不動」僅對 L1 成立）。 | 建議 minor 修訂：(1) ONT.13 判準改為域中立句「各 Domain Profile ①部存在宣告條之封閉集（由該 Profile 之 A-① 節界定）每一條解析至恰一主型別節點」，把 {A.1–A.30, A.57, A.58} 之具體閉集移入 Annex T-Map／TM.0 之表首（域附錄層）；(2) ONT.50 對象改為「`AUGUR-WM` 各生效 Domain Profi |

### P4 刪名測試(D 類)（1 則）

**已由乙-2 部分閉合**（原則精華 #1 已改）；本則指向**靈魂**同型措辭（以 FinMind／FRED 為判準本體），屬乙-1 之同一批，隨乙-1 一併處理。

| 嚴 | 檔 | 位置 | 疑義 | 建議措辭 |
|---|---|---|---|---|
| L | `docs/系統核心思想_v1.8.0.md` | 「最神聖的紀律（敵人①，系統的命）」・零 AI 幻像／Sou | 系統最高位階紀律以兩家供應商名為判準本體（刪去 FinMind／FRED 後內涵由「兩個具名通道」變為「任何真實觀測通道」＝內涵改變），WM.6 明定本檔適用 WM.4 刪名測試、WM.7 明定資料來源不得成為最高抽象，故現行措辭係以供應商名充定義依據。 | 改寫為「任一特徵值若不是『已登錄觀測通道（Observation Channel）之真實來源回應經數學轉換而得』——而是 imputed／zero-fill／hardcoded／推估／系統自補——即視同幻像」，並於句尾以括注列現行登錄通道（〔現行登錄：FinMind、FRED〕）使其降為指名；同步「資料只來自哪」節改為「現行已登錄通道（清單住 registry，新增通道須人拍板登錄）」，避免兩供應 |

### P6 硬體/環境登錄值失效(L7 [I] 欄)（1 則）

**建議：照案改 [I] 值＋補登 OPEN**。L7.16 自承覆蓋僅及單一掛點卻未依 L7.3(b)／L7.70(b) 登錄為 OPEN（無到期日、無義務主體）；連同我另抓到的 L7.51(b)(c) 仍寫 GB10 之 121 GiB／3.4 TB（與同檔 L7.50 之 15GB／GTX1650 差 8 倍與 5 倍）一併更正。

| 嚴 | 檔 | 位置 | 疑義 | 建議措辭 |
|---|---|---|---|---|
| L | `specs/INFRASTRUCTURE-SPECIFICATION.md` | L7.16（不變式強制之權限錨定）可判定判準末段 | L7.16 課「每一受保護儲存物件之拒絕須由可執行回歸測試逐項驗證」，卻於同一 [N] 判準自承覆蓋僅及單一掛點、其餘「俟擴充」——此為文件自承之收編缺口，然未依 L7.3(b)／L7.70(b) 登錄為 OPEN 條目，故無到期日、無義務主體、亦無明文之保守預設範圍（僅靠 (e) 之「存疑即推定不成立」泛示），使末層「不得靜默落空」之紀律在本條自身留白。 | 於 Annex OPEN 增列條目「受保護儲存物件之拒絕測試矩陣未完備」，五欄為〔事項＝L7.16 判準之全物件測試矩陣；掛鉤＝LDI.41／AUD-02、KS KDO.7；保守預設＝未具通過測試之受保護儲存物件，其 §P4.E3／§P3.E2 不變式推定不成立，其內容不得取得權威地位、不得為任何 RT≥1 Action 之 Knowledge Basis；義務主體＝部署者；期限＝90 日（自登錄 |

### P10 cluster 門檻與確立級判準（1 則）

**建議：與『60 vs 250』一併裁**。本則另揭一事：`augur_all_evolution_next_steps` 把 M2 排成月頻，與 META-REPLAY 計畫「先季頻粗掃、有訊號才月頻細化」及其『明確不做：月頻細化作為找訊號手段』**直接相反**——排程與方法論打架。

| 嚴 | 檔 | 位置 | 疑義 | 建議措辭 |
|---|---|---|---|---|
| H | `reports/augur_all_evolution_next_steps_20260729.md` | §三 T3 第 12 項(41 行);同軸見 open_pr | 本檔把 M2 正式排成月頻(101 期)、open_problems 更以月頻為預設而季頻退為退路,與 META-REPLAY 計畫 §二/§七「先季頻粗掃(34 cutoff)、有訊號才月頻細化」及其「明確不做:月頻細化作為找訊號手段」直接相反;後果不只排程差異——月頻恰好把 n 由 34 抬過 ≥60 門檻,使取樣頻率成為滿足門檻的自由度(實查 meta_replay_cutoff 已有 4 個 proc_sha 家族、最大僅 30 期,無一達 60)。 | 二者取一併留痕:(a) 回到季頻先行,月頻僅在 M2.5 訊號判準過後開;或(b) 由 hugo 明簽「M2 網格改月頻」之修訂,同批在 §六 補「n 由取樣頻率決定,故頻率屬凍結判準之一部;跨頻率不得混同一 proc_sha 家族」,並在門評 result_snapshot 強制揭露 step 與 n。 |


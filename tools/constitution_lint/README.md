# constitution_lint — §8.3 機器稽核雙 linter（骨架）

把憲章從「文件」變成「CI 可強制的制度」的最高槓桿基建。依《憲章展開總綱》§5.4、`AUGUR-MC v1.3 §8.3`、`AUGUR-WM v1.0 §WM.39–45`。**純標準庫、零外部依賴**（CI 免安裝套件）。

> **治權自動化止於「判定與阻擋」，不及於「執行變更」** —— 本工具只報 finding／回非零退出碼，決不改內容、決不自動 apply 或合併（`AUGUR-MC v1.3 §P5.W2`）。

## 兩支 linter

| linter | 管什麼 | 檢查 |
|---|---|---|
| **compliance_lint** | 規格生效 | WM.40 front-matter 閉集欄位＋空值/空集顯式＋**閉集擴欄**（error）＋**閉集權威**（退回硬編碼副本即 error）／WM.41 七節齊備＋**固定序**（error）＋四項 (a)-(d) 覆蓋（warning／advisory）／WM.42 緊張節／WM.43 DEFER 雙向／WM.44 形式充分性覆蓋（warning，母集 <!--lint:mc_universe-->102<!--/lint--> 條）／**WM.44-LABEL 原文標籤**（error；權威來源＝MC＋`upper-specs` 所列各上層規格）。**接受 minor 版落差不誤紅**。error＝規格不生效力。 |
| **audit_lint** | code 合憲 | 引用鏈雙合法終點（K→Evidence→Observation ∪ 明示宣告之假設，P4.E6）、Action→Identity 六元組、Knowledge 五元組、Confidence 存在性。以 AUD-01/03/10/11 為 failing 種子。 |

## 用法

```bash
python -m tools.constitution_lint --selftest                    # 紅綠自檢（WM v1.0 綠 / 壞樣本紅）
python -m tools.constitution_lint report                        # 全 corpus 權威數字（人可讀＋JSON）
python -m tools.constitution_lint audit <code-dir> [--policy legacy|greenfield]

# 規格生效 lint。受檢 corpus 請一律以 `report --files` 列舉，勿手打 glob：
python -m tools.constitution_lint compliance $(python -m tools.constitution_lint report --files)
```

> ⚠ **勿寫 `compliance specs/*.md`**（本節前版即如此示範）：該 glob 納入 `specs/*-v0.1-draft.md`
> **歸檔本**，得 13 份/352，與本文件各表之七份/200 不符。**受檢 corpus 之定義只有一處**
> ——`report.corpus_files`（六份生效本＋尚無生效本之 draft；歸檔本除外）；`report --files`
> 即其列舉，CI 亦用之。

### `report` — 全 corpus 權威數字之單一產生點

```bash
python -m tools.constitution_lint report            # 人可讀表格 ＋ 機器可解析 JSON 區塊
python -m tools.constitution_lint report --json     # 僅 JSON（values.* 為各 key）
python -m tools.constitution_lint report --files    # 受檢 corpus 之檔案清單（一行一路徑）
python -m tools.constitution_lint report --sync     # 將數字寫回 [I] 文件之 lint 標記
```

輸出含：受檢 corpus 之定義與清單／逐檔 error・warning・info・WM.44-LABEL error・MC 側與
上層側與未歸類三分／合計（七份總 error、四份生效規格 L3–L6 合計、三分）／error 分型／
selftest 覆蓋數（**自帶限定詞**：頂層測項 N 項／斷言總數 M 項）／[I] 文件綁定普查／
**末尾附產生指令與 git HEAD SHA**（`+dirty` 表工作區有未提交變更，該輸出無法僅由該 SHA 重現），
使任何轉貼可被追溯。

`report` **退出碼恆為 0**：它是**度量**，不是**判定**。判定與阻擋之權責屬 `compliance`／
`audit`——以報表指令決定 CI 紅綠，會使 gate 之紅綠繫於報表而非判準。

退出碼（`compliance`／`audit`）：任一目標有 error → 1；否則 0。`--policy greenfield`＝新 code merge 當下 finding 即 error；`legacy`（預設）＝既有系統以補正期追蹤（finding 為 warning）。

## 反「綠燈但實質錯誤」之兩檢查

既有檢查全屬**形式覆蓋**：欄位在不在、代號有沒有出現、節齊不齊。此類檢查有一整類共同盲點——
**形式齊備而內容是起草者自己的話**。AUGUR-L7 草案連續兩輪 error 0，卻含系統性憲章誤標：
起草者憑記憶轉述上層條款標籤（`P2.E4`＝「禁插補冒充」、`F4`＝「Automation First」——憲章 0 次），
再拿**自己的轉述**去推論落點，致真實義務被判「不觸及」而靜默落空。代號都在，覆蓋檢查全綠。

以下二檢查即為封殺此類缺陷而設。

### WM.44-LABEL — 原文標籤檢查（error）

掃描 **Annex TR 各表**之每一列，抽出首格之「條款代號＋其括號標籤」，與自**上位原文**抽出之
標籤資料比對。**標籤權威來源＝憲章（MC）＋受檢規格 front-matter `upper-specs` 所列各上層規格**
（`_upper_spec_labels`）——「上層條款須以其原文標籤為準」與「憲章條款須以憲章原文為準」係
同一義務，`§0.6(a)` lex superior 逐層適用。upper-specs 條目 `AUGUR-XX vY` 之 XX 恰為該規格之
條款代號前綴、vY 為其 `spec-version`，故對照由**檔案自述**決定，不硬編碼檔名表。

> ~~解析不到者報 warning 並明載「該上層規格本次未受檢」（非「已比對且通過」）。~~
> ⚠ **【更正，2026-07-17】** 上句於 `608adc2` 時為真，經 `65a7dd6` 將 `_upper_spec_labels`
> 之該分支由 `Severity.WARNING` 升為 `Severity.ERROR` 後**變為假**——升級者未同步本句，
> 遂使本節與同檔「二分流、嚴重度不同」一段（見下「代號脫檢」）**在同一份 README 內互斥**，
> 而該段之更正告示還反過來要讀者「見上」——「上」正是這句假話。**據實更正為二分流**：
>
> * **(a) `upper-specs` 所列項無法解析至規格檔者 → `ERROR`**：front-matter 既已宣告受其
>   拘束，來源缺位即**該來源側之判定全部失權威**；訊息作「該上層規格之條款標籤本次
>   **全部**未受檢」（非「已比對且通過」）。
> * **(b) 代號前綴屬已知規格、但該規格未列於 `upper-specs` 者 → `WARNING`**（代號脫檢，
>   見下節）。
>
> 產生指令（本次據以更正者，非轉抄）：將 `specs/IDENTITY-SPECIFICATION.md:671` 之
> `upper-specs: [AUGUR-WM v1.0, AUGUR-ONT v1.0]` 改為 `AUGUR-WM v9.9` 後跑
> `python3 -m tools.constitution_lint compliance specs/IDENTITY-SPECIFICATION.md`
> → `ERROR WM.44-LABEL: …`AUGUR-WM v9.9` 無法解析…**全部未受檢**`、❌ FAIL。
> selftest 之 **G5 突變鎖**斷言 (a) 為 error、且未降級為 warning。
>
> **記之以為戒**：本句與下節之更正告示相距約 70 行，而該告示自陳「撲滅一句假話的同一段落
> 產出新的假話」——本句即該病之**上游**：一句假話的第二份副本，躺在宣告「已撲滅」者的
> 上方 70 行處。凡宣稱「已修」者，須自行驗證**所有副本**皆已修。

**判準（依序）**：

1. **上位之完整標籤在場即通過**。為每條 [N] 條款抽出其自有標籤（`* **P3.E3（同一性判準掛鉤）**`、
   `**P4.E2 Time（雙時間性）**`、`### F4 — Knowledge Without Identity`、
   `## §3 Five Immutable Principles（五大不可違反原則）`、`> **WM.36（World Concept Registry 與消費規則）[N｜…]**`）。
   採**含入**而非全等——附加限定語（`§P5.W2`（…）**〔不可豁免核心〕**）不構成誤標。
2. **`X（Y）` 體例之半名：單獨匹配為必要非充分**。機器無從分辨譯名對
   （`Five Immutable Principles（五大不可違反原則）`）與名＋限定語（`Confidence（語義與消費）`），
   故一律取較嚴格解讀（`§8.2`）：**兩半俱在**、或**標籤即該半名本身而未添附自撰片段**者通過；
   引一半而另一半代以自己的話者 → ERROR。此即封殺「`Confidence 單一形式化` 因含 `Confidence`
   而綠燈」之漏洞——**被截除之「消費」面才是下層之義務**。
3. **前段截取**：標籤逐字照抄原文名之前段（共同前段 **≥4 字元且占原文名 ≥40%**）、其後分歧
   且未含原文名整體，並**另添字**者 → ERROR。實證：`WM.36`（World Concept Registry 七欄）之原文名為
   「World Concept Registry 與消費規則」，而「七欄」恰為該條正文用語 → 詞元命中 4/4，判準 4 反會放行之。
   **純縮寫不罰**（`§0.4`（權威語言）vs 原文「權威語言聲明」——未添附任何字者係節引，非替換）。
4. **純節引不罰**：標籤為原文名之**逐字子字串**且未添附任何字元（`WM.4`（刪名測試）vs 原文
   「概念層獨立性＋刪名測試」）→ 通過。無自撰片段可言，報之即為不實陳述。**限 `X（Y）` 體例
   （halves）不在場者**——該體例之截半已由判準 2 依較嚴格解讀處理。
5. **仍容「取自正文之逐字濃縮」，惟限該條款＊無自有標籤＊者**。其標籤為條款正文之逐字子字串
   或詞元命中率 **≥ 50%** 者通過。起草者顯然讀過條文；要攔的是**正文毫無支撐**之自創詞。

   ⚠ **前版此處之描述與例證均為假，已據實更正**：(a) 前版程式碼對**全部**條款跑本判準並於
   通過時放行，致本判準成為**判準 1 之無條件大赦**——條款正文本就富含該條用語，故「詞元半數
   命中正文」幾近恆真，縱標籤與原文括號名全然不符亦綠。實證漏網：`P1.E1`（原文名＝`開放來源`）
   掛 `Reality 最高抽象／來源非最高抽象` → 命中 5/7 → 靜默放行，且不在其所報之 error 清單內。
   README 早已載明本判準之範圍為「未觸及原文名者」，**程式碼未實作其自身之規格**；現已收緊為
   `paren_name` 不在場者限定（突變鎖 G1）。(b) 前版所舉之例 `P4.E1`（五元組最低不變式）**本身
   即誤標**：`P4.E1` 於 `META-CONSTITUTION.md` 之原文名為 `Knowledge 五元組`（並非「未觸及原文名」
   之條款），該標籤捨「Knowledge」而代以正文用語「最低不變式」，正屬判準 3 所攔之型態。舊
   fixture 之該列已由 good（綠）移至 bad（紅）。
6. 皆不成立 → **ERROR**，訊息並列「規格所載」與「{來源} 原文」及其行號。
7. **無標籤者不罰**——僅列代號之列（`` `P2.E1`／`P2.E2` ``）合法。**項次交叉引註不罰**——
   `ID.30(c)` 之 `c` 非標籤宣稱。**空白標籤不罰**——`` **P1.E1**（） `` 括號內無內容者無標籤
   可比（實測 `_row_code_labels` → `[]`；G8 對向鎖）。**此三者為不罰之全部**；代號無法解析至
   受檢條款者**不在其列**，一律發聲（見下「代號脫檢」）。
   > ⚠ **【更正，2026-07-17】前版此處作「此**二**者為**僅有**之不罰情形…**一律**發聲」——
   > 二處皆為假：(i) 漏列**空白標籤**（第三種不罰，實測所得）；(ii)「一律發聲」為同檔
   > 「代號脫檢之殘留缺口」一節所**直接推翻**——當時代號**形態不合致**者（`P9.E9` 等）於
   > 抽取階段即遭靜默捨棄。**斷言之絕對性（「僅有」「一律」）超出程式碼實況，而真相被放在
   > 100 行外的另一段——讀者停在此處即得錯誤結論。** 現況：形態不合致者已由兜底錨抽出、
   > 交「代號脫檢」之 WARNING 分支發聲（三輪修正，G8 鎖），故本處之「一律發聲」**始為真**；
   > 惟其為真係因**程式已改**，非因文字改得漂亮。
8. **區段列**（`WM.6–WM.11（…）`）以區段內各條正文之**聯集**適用判準 5；其複合標籤本不可能
   等同任一單條之括號名，以尾碼單條相繩即製造偽陽性。

**Annex TR 區段缺位＝未執行，非通過（error/info，突變鎖 G4）**：區段錨點硬性要求 `## Annex TR`。
前版於解析回空集時**靜默 return**，故「本規格無 Annex TR」與「Annex TR 全數比對通過」在輸出上
**完全不可分辨**（皆零 finding、皆 PASS）。實例（非假想）：`specs/ONTOLOGY-SPECIFICATION.md` 之
Annex TR 標題為 h1（`# Annex TR`），其 WM.44-LABEL **從未執行**，而該 `PASS（error 0）` 曾用以
支撐 RULING-2026-003。現行分流：**有 Annex TR 標題但層級非 `##`** → ERROR（零覆蓋而輸出與全通過
同形）；**無標題但本文斷言形式充分性繫於 Annex TR 逐條枚舉** → ERROR（斷言無從查證）；**二者皆無**
→ INFO「不適用」（仍留痕，俾「未執行」不被讀作「已比對且通過」）。嚴重度**不繫於 `upper-specs`
之有無**——否則 `good_minimal`（宣告綁定、確無 Annex TR）即誤紅。工具**不代改** ONT 之標題：
規格之編輯權屬其作者／Steward（§8.5／§8.6），工具之職分止於令其非覆蓋**發聲**。

**代號脫檢＝未受檢，非通過（error/warning，突變鎖 G3）**：前版 `clause is None → continue` 靜默
略過，形成**誘因倒置**——弄壞代號比修好標籤容易（改寫代號即令該列連同其誤標消失於輸出）。現行：
代號合憲章編號形態卻不在 [N] 條款宇宙者 → ERROR（非誤植即杜撰）；前綴屬已知規格但未列於
`upper-specs` 者 → WARNING。

**詞元須去重（突變鎖 G2）**：`label_overlap` 前版以詞元**清單**計數，重複一個命中詞即墊高分子——
`禁插補冒充` ＋ `Representation` ×4 → **4/8 ＝ 50%** 恰跨閾值而放行，誤標原封不動；去重後恆為
**1/5 ＝ 20%**。（以清單計數等同獎勵冗詞。註：**整體重複**標籤並無此效果——分子分母同步放大、
比值不變；能灌分者恆為「以命中詞填充」。）

**閾值 50% 之取捨**：低於半數詞元見於憲章原文者，該標籤之主體已非憲章文字而是起草者的話——
正是要攔的病灶。取更高值會誤紅合法之濃縮引用（「授權鏈根為人類權威、隨時否決」之連接詞本就不在原文）。
詞元＝ASCII 詞（≥2 字母）＋CJK 連續段之 2-gram；單字 CJK（之／與／非）訊號太弱不計。
**詞元 < 2 者一律不罰**：樣本太小，判紅即擲硬幣。

**偽陽性控制**：僅檢查 Annex TR 區段之**表格列**（正文散文之括號多為說明而非標籤宣稱）；
反引號與 `**` 強調符號先剝除；全半形經 NFKC 統一、空白全數移除後比對。

> ⚠ **前版此處載「非 MC 條款代號（WM／ONT／ID／KS／L5／L6）本檢查不轄」——該句為假，已刪除。**
> **上層規格條款代號（WM／ONT／ID／KS／L5／L6／L7…）亦受檢**，其標籤權威來源為 front-matter
> `upper-specs` 所列各該規格之原文（見上「標籤權威來源」）。**二分流、嚴重度不同**（2026-07-17
> 實測導出，非轉抄）：(a) `upper-specs` 所列項**無法解析至規格檔**者 → **ERROR**（front-matter 既已
> 宣告受其拘束，來源缺位即該來源側判定全部失權威）；(b) 代號前綴屬已知規格但該規格**未列於**
> `upper-specs` 者 → **WARNING**（見「代號脫檢」）。程式依據：`mc_clauses.py` 之 `SPEC_PREFIXES`、
> `compliance_lint.py` 之 `_upper_spec_labels`／`_SPEC_CODE_FULL`；selftest G5 突變鎖斷言 (a) 為 error。
> 產生指令：將任一規格 front-matter 之 `AUGUR-WM v1.0` 改為 `AUGUR-WM v9.9` 後跑 compliance。
>
> ⚠ **本段前一版曾於此更正告示之內部再寫入一句假話**（「未列**或無法解析**者…報 warning」——將
> 二分流混為一談，(a) 實為 ERROR），已於 2026-07-17 由獨立驗證官以突變實測揪出並更正。**撲滅一句
> 假話的同一段落產出新的假話——此即本工具所欲撲滅之病，記錄於此以為戒。**
> **本句方向相反地危險**：其所在之「偽陽性控制」節正是讀者查核本檢查邊界之第一處，讀者據以
> 認定上層標籤未受檢，將**逕行折抵掉真實之上層側 error**（現行實測上層側 error 為 **<!--lint:label_errors_upper-->0<!--/lint-->** 筆，
> 見下「實測」節）。此為 B5 期之殘留，與本工具所欲撲滅之病同型：**README 陳述與程式行為不符**。

### WM.40 閉集擴欄（error）

`§WM.40` 明定 front-matter 欄位為**閉集**（現行 <!--lint:wm40_fields-->14<!--/lint--> 欄——本數由 `report` 自 WM 原文動態解析導出，非本文件手記；WM 增欄時自動隨之）。既有 `_check_wm40` 僅作**存在性**檢查——
欄位全在就綠，多了不該有的欄位完全盲視。新增：出現閉集外欄位即 ERROR。
聲明格式之定義權由 `AUGUR-MC §8.3` 授予 **Layer 1**；下層規格自行擴欄，即以末層之作為擴充
Layer 1 之格式定義，違 `§0.6(a)` lex superior。

**閉集由 WM 規格原文動態解析**（`_wm40_closed_set`：定位 `**WM.40（…`→ 剝 blockquote 前綴 →
取其後首個圍籬區塊之 `key:` 行），**不硬編碼**——閉集之定義權屬 Layer 1，linter 硬編碼一份副本
即等同由工具僭越該定義權，且 WM 修訂時副本將靜默失準。

selftest 以**修訂後之 WM 副本**實證之（`selftest.py` B8 突變鎖①：寫出副本、插入 `new-field-x`、
斷言 `_wm40_closed_set(副本)` 回傳含該欄之 15 欄且 source 仍為「WM 原文」）。
selftest **不**斷言 `len(...)==14`：14 正是本設計明文拒絕硬編碼之對象——WM 合法增欄時該斷言
即偽紅，屆時修復壓力會指向「把 14 改成 15」而非「修解析」，即把 linter 拉回硬編碼。改採結構性
斷言（`len>=10 and 'spec' in f and 'archive-path' in f`）。

### WM.40 閉集權威（error）—— 退路一經動用即失權威

`_WM40_FIELDS_FALLBACK` 為 WM 不可讀／WM.40 錨點格式漂移時之退路。**退路一經動用即無條件
ERROR**（`_check_wm40_closed_set_authority`）：閉集失準時，`_check_wm40`（缺欄）與
`_check_wm40_extension`（擴欄）之**全部**判定均以工具副本為據而失其權威基礎——非「某一項存疑」，
而是整組 WM.40 判定不具權威，故取 ERROR 而非 WARNING。

此為對前版缺陷之修正：前版於 WM 不可讀、或錨點微漂移（`**WM.40（` → `**WM.40 ：` 即足）時
**靜默**退回硬編碼副本且零 finding，規格照報 ✅ PASS——程式碼實作了它自己於
`compliance_lint.py:25-27` 指名為違憲之退路，且退得無聲。突變鎖見 selftest B9①–③。

## 現況（骨架 v0.1）

**已完備（對真實輸入實測）：**
- compliance_lint 對 **AUGUR-WM v1.0 自檢綠**（含 `mc-version v1.2` vs 現行 v1.3 之 minor 落差正確判 info、不誤紅）；兩種聲明編排（獨立標題式與單標題粗體子節式）皆認；對七反例正確判紅。
  ⚠ **本項關於三草案之敘述已二度失準，據實更正如下**：(a) 最初稱「對 ONT/ID/KS 三草案聲明皆
  正確 PASS」；(b) 前版更正為「ONT draft 續 PASS，ID draft／KS draft 各以 20／25 筆轉紅」——
  **(b) 於本輪實測亦不成立**：ONT draft 現為 **FAIL**（Annex TR 標題 h1 致零覆蓋，強制發聲），
  ID／KS draft 之 error 亦非 20／25。**此三份為歸檔本，不在受檢 corpus 內**（其生效本在場），
  故 `report` 不涵蓋、其數字無從綁定——依本文件之規則，**此處不寫死數字**。需要時請自跑：
  `python -m tools.constitution_lint compliance specs/{ONTOLOGY,IDENTITY,KNOWLEDGE-SYSTEM}-SPECIFICATION-v0.1-draft.md`。
- audit_lint 框架 + 三示範種子規則，對 augur code 重現已知審計發現（AUD-01 之 37 檔 vendor 直綁、AUD-10 留痕表缺 actor 欄）。
- CI 定義：`tools/constitution_lint/github-workflow.yml`（selftest + 全規格 compliance-lint）。**啟用方式**：複製至 `.github/workflows/constitution-lint.yml`（需具 `workflow` scope 之推送權限；現行 gh OAuth token 無此 scope，故暫存為參考檔待 P5/具權限者啟用）。

**骨架邊界（隨後續階段強化，見總綱）：**
- **WM.41 四項 (a)-(d)** 為 **warning／advisory**（缺項不阻斷、hollow 七節仍 PASS）；升 error 會誤紅合法草案（如 ID draft 之 P5 不適用節），故完全強制待後續階段。七節齊備與固定序為 error（已強制）。
- WM.44 形式充分性目前為 **warning 級覆蓋報告**（有邊界比對，避免 EV.1 被 EV.10 掩蓋）；完全強制須待 MC [N] 條款嚴格枚舉（`mc_clauses.py` 現為正則骨架）。
- **條款宇宙之已知邊界（據實揭露）**：現行母集 **<!--lint:mc_universe-->102<!--/lint--> 條**＝PA／P#.*／EV.1–12／F1–F6／[N] 章（§0–§8）／
  子條標題（§0.1–§0.6、§1.1–§1.3、§8.1–§8.6）／**項次（§2.1–§2.11、§5.1–§5.6）**。
  **字母項（`§0.6(a)`、`§8.5(b)(i)`）未納入**：`§0.3` 稱「章節號及其小節與**項次**視同條款編號」，
  所舉之例（§8.3、§2.11）中 §2.11 即 numbered list item，故點號數字項次為明文承認之體例、無須解釋
  即可認定；括號字母項體例既異、`§0.3` 亦未舉例，其是否屬「項次」為**條文解釋**問題，
  依 `§8.1` 屬 Steward 專屬——linter 不得自行造法。此為**明示保留**，非疏漏；如經 Steward 解釋
  納入，母集將再增（§0.6 三項、§8.5 四項及其 (i)/(ii) 子項）。
- **代號脫檢之殘留缺口** ~~（據實揭露，本階段未閉）~~ → ✅ **已閉（2026-07-17 三輪，G8 鎖）**：
  ~~「代號脫檢發聲」僅涵蓋 `_row_code_labels` **抽得出**之代號；連代號形態都不合者
  （`P9.E9`、`P7.E1` 等）於更上游即遭捨棄，該列連同其誤標仍**靜默**消失。~~
  > **前版之揭露屬實（未謊稱已閉，此點不罰），惟其所述之規模遠小於實測**：前版把缺口敘述為
  > 「`ANY_CODE_ALT` 僅容 `P[1-5]`，故 `P9.E9`、`P7.E1` 等」，讀者會以為僅限少數越界前綴。
  > **實測（本輪親跑，非轉抄）**：**任何字元層面之污損**皆走同一條靜默路徑——
  > `` **Ｐ1.E1**（亂編） ``（全形字母）→ `[]`、`` **P1．E1**（亂編） ``（全形句點）→ `[]`，
  > 而 `` **P1.E1**（亂編） `` 照常受檢。亦即**把代號打成全形即可令該列連同其誤標一併蒸發**，
  > 比「改首格代號」更便宜（改一個字元）。前版將此排到「Measure 階段再定」，係對其規模之誤估。
  >
  > **本輪之處置（二者皆已實測）**：
  > * **NFKC 正規化**（`_strip_markup`）：全形變體自動歸位為真代號、照常受檢。**標籤仍逐字
  >   引錄、不受正規化**——否則工具將以正規化後之字串充作「規格所載」，自己 misquote
  >   （初版即如此，為 G1 回歸鎖當場抓到）。
  > * **兜底錨**（`_LOOSE_CODE_LABEL`）：首格中「識別符＋點＋英數 ＋ 緊接括號 ＋ 非空內容」
  >   而不合 `ANY_CODE_ALT` 者，交由 `_report_unresolved_code` **既有之第三分支**
  >   （「代號不合任何已知條款編號形態」→ WARNING）發聲——該分支前為**死碼**（抽取階段
  >   先把這些列丟了，永遠到不了那裡），現正好接上。
  >
  > **偽陽性實測（前版所憂者，已量測而非臆測）**：七份規格之 **error 數一筆未變**
  > （<!--lint:errors_L1-->0<!--/lint-->／<!--lint:errors_L2-->0<!--/lint-->／<!--lint:errors_L3-->0<!--/lint-->／<!--lint:errors_L4-->0<!--/lint-->／<!--lint:errors_L5-->0<!--/lint-->／<!--lint:errors_L6-->0<!--/lint-->／<!--lint:errors_L7-->0<!--/lint-->，與突變前逐格相同），**無任何規格因此翻紅或翻綠**；
  > 新增者全為 **WARNING**（ID 1→<!--lint:warnings_L3-->44<!--/lint-->、KS 9→<!--lint:warnings_L4-->39<!--/lint-->、L5 7→<!--lint:warnings_L5-->17<!--/lint-->；箭頭左側為突變前之歷史值，不綁定），內容為 Annex TR 中**他文件之代號**
  > （如 ID 之 `A.0（地位與範圍）`＝系統架構大憲章 Annex A 之對照列）——該等標籤確實**未受檢**，
  > 依本工具「未受檢 ≠ 已比對且通過」之教義，發 WARNING 留痕為正辦，且不影響 PASS／FAIL。
  > **區段列之回歸風險已鎖**：兜底錨不得二次解讀主錨已涵蓋之文字，否則 `ONT.1–ONT.62（…）`
  > 之**區段標籤**將被拿去比對**單條** `ONT.62` 而誤紅（本輪初版即如此，L6 由 37→39，
  > 二筆全為偽陽性；現以 G8／B5 回歸鎖鎖住）。
- **空白標籤仍不罰**（`` **P1.E1**（） `` → `[]`）：括號內無內容者無標籤可比，非誤標。此為
  上開「不罰之全部」之第三種，據實列出。
- 多圍籬區塊時取首個具體聲明（非佔位）；真實規格每檔單一真聲明，此假設未觸發。
- audit_lint 完整規則集與語義嚴格度隨 **L3（Identity）/L4（Confidence）充任** 收緊（版本化 linter）；K→E→Observation 鏈完整性靜態稽核為 stub。
- linter 設為 **merge-gate（強制）** 留待總綱階段 9；本階段 CI 僅 error 阻斷、warning/info 不阻斷。
- audit_lint 於 augur **code repo** 之 CI 接線為後續（本 repo CI 僅跑 compliance_lint）。

## 檔案

- `model.py` — Finding/Severity/LintResult
- `mc_clauses.py` — 憲章 [N] 條款枚舉（WM.44 用，**<!--lint:mc_universe-->102<!--/lint--> 條**）＋**原文標籤資料**
  （`enumerate_clause_labels`：code → {paren_name, full_forms, halves, text, line, source}；
  `enumerate_spec_clause_labels`：上層規格同構之標籤抽取，WM.44-LABEL 用）
- `compliance_lint.py` — 規格生效檢查器
- `audit_lint.py` — code 合憲骨架
- `__main__.py` — CLI（`compliance`／`audit`／`report`／`--selftest`）
- `selftest.py` — 紅綠自檢（`run()` 回 `(ok, records)`；`records` 為**項數之唯一機器來源**，
  自此不再以 grep 計數）＋ **[I] 文件權威數字綁定斷言**（`_binding_and_consistency`）
- `report.py` — **全 corpus 權威數字之單一產生點**：corpus 定義（`corpus_files`）、三分歸因、
  分型、selftest 覆蓋數、產生指令＋git HEAD SHA、`--sync` 寫回 [I] 文件標記
- `fixtures/` — selftest 正例（good_minimal、**good_label_ok**）＋反例（bad_no_statement／bad_missing_field／
  bad_missing_section／bad_appendix_mask／bad_empty_value／**bad_label_mislabel**／**bad_wm40_extension**）

## 受檢 corpus 之掃描結果（**數字由 `report` 導出並綁定；不一致即 selftest FAIL**）

> **本節標題與警語之沿革（據實記錄）**：前版此處為「⚠ **已過時：本表作成於本輪 gate 硬化＊之前＊，
> 勿引用**／本表之數字全部待重新實測」。該警語於當時為真，**現已不再為真**：下表每一格皆為
> `report` 之實測導出值，並由 selftest 逐處綁定比對——**不一致即 FAIL**。「待重新實測」之狀態
> 已由「數字不可能再與程式分家」取代。惟仍請注意：**綁定保證「數字＝程式所量」，不保證
> 「程式所量＝應量者」**；判準本身之弱點見下「建造者自陳之殘餘弱點」。
>
> **歷史上已知為假之列（保留以為戒）**：`L2 ONTOLOGY … 0（無 Annex TR 表格列）｜0｜✅ PASS` —— ONT
> **確有** Annex TR（`ONTOLOGY-SPECIFICATION.md` 之 `# Annex TR`，h1），其標籤檢查從未執行；
> 該 `PASS` 係區段解析回空集所致之**偽陰性**，非「已比對且通過」。硬化後 ONT 為 ❌ FAIL
> （WM.44-LABEL 非覆蓋 error）。其 `PASS` 曾用以支撐 RULING-2026-003——見 HANDOFF 待裁 #22。
> `L1 WORLD-MODEL … 0（無 Annex TR）｜✅ PASS` 則屬真陰性（WM 確無 Annex TR，硬化後為 INFO
> 「不適用」、續 PASS）——二者前版輸出同形，正是本輪所修之病灶。

**下表全部數字由 `report` 導出並以 `--sync` 寫入，非手抄**。產生指令：

```bash
cd /home/giga/augur/augur-constitution
python3 -m tools.constitution_lint report          # 全 corpus 權威數字（人可讀＋JSON）
python3 -m tools.constitution_lint report --sync   # 將數字寫回本表之 lint 標記
```

> **本表為何不會再腐爛**：表中每個數字都以一對 lint HTML 註解（開標籤帶 key、閉標籤結束，值夾在中間）綁定至
> `report` 之輸出，selftest 逐處比對，**不一致即 FAIL**（`selftest._binding_and_consistency`）。
> 本句之總 error ＝ <!--lint:total_errors-->0<!--/lint--> 即為一個活的綁定：它的 `200` 也是
> `--sync` 寫進來的，讀者可直接 `view-source` 該處看標記形式。前輪
> 「專為導正 Steward 而寫的表格三處落地即假」之所以可能，正因為當時表格與程式之間只有人的
> 手。手已拿掉：改數字的唯一途徑是改程式所量到的東西，然後跑 `--sync`。
>
> **受檢 corpus 之定義寫在程式**（`report.corpus_files`）而非本文件：六份生效本（無
> `-v0.1-draft`）＋尚無生效本之 draft（L7）＝ <!--lint:corpus_total-->7<!--/lint--> 份；
> 歸檔本（生效本在場之 `-v0.1-draft`）除外。**勿以 `specs/*.md` glob 代之**——該 glob 含
> 歸檔本，得 13 份/352。

| 規格 | 比對筆數（MC／上層） | WM.44-LABEL error（MC 側／上層側） | WM.40 擴欄 | WM.44 覆蓋缺口 | 判定 |
|---|---|---|---|---|---|
| L1 WORLD-MODEL | <!--lint:compared_L1-->0<!--/lint-->（確無 Annex TR → INFO「不適用」） | <!--lint:errors_L1-->0<!--/lint--> | <!--lint:wm40_extension_L1-->0<!--/lint--> | <!--lint:wm44_uncited_L1-->40<!--/lint-->/<!--lint:mc_universe-->102<!--/lint--> | ✅ PASS |
| L2 ONTOLOGY | **<!--lint:compared_L2-->4<!--/lint-->（h1 標題致區段解析回空集）** | **<!--lint:errors_L2-->0<!--/lint-->**（非覆蓋發聲，無從歸側） | <!--lint:wm40_extension_L2-->0<!--/lint--> | <!--lint:wm44_uncited_L2-->15<!--/lint-->/<!--lint:mc_universe-->102<!--/lint--> | ❌ FAIL |
| L3 IDENTITY | <!--lint:compared_L3-->139<!--/lint-->（<!--lint:compared_mc_L3-->62<!--/lint-->／<!--lint:compared_upper_L3-->77<!--/lint-->） | **<!--lint:errors_L3-->0<!--/lint-->**（<!--lint:errors_mc_L3-->0<!--/lint-->／<!--lint:errors_upper_L3-->0<!--/lint-->） | <!--lint:wm40_extension_L3-->0<!--/lint--> | <!--lint:wm44_uncited_L3-->58<!--/lint-->/<!--lint:mc_universe-->102<!--/lint--> | ❌ FAIL |
| L4 KNOWLEDGE-SYSTEM | <!--lint:compared_L4-->168<!--/lint-->（<!--lint:compared_mc_L4-->58<!--/lint-->／<!--lint:compared_upper_L4-->110<!--/lint-->） | **<!--lint:errors_L4-->0<!--/lint-->**（<!--lint:errors_mc_L4-->0<!--/lint-->／<!--lint:errors_upper_L4-->0<!--/lint-->） | <!--lint:wm40_extension_L4-->0<!--/lint--> | <!--lint:wm44_uncited_L4-->66<!--/lint-->/<!--lint:mc_universe-->102<!--/lint--> | ❌ FAIL |
| L5 COGNITIVE-KERNEL | <!--lint:compared_L5-->100<!--/lint-->（<!--lint:compared_mc_L5-->55<!--/lint-->／<!--lint:compared_upper_L5-->45<!--/lint-->） | **<!--lint:errors_L5-->0<!--/lint-->**（<!--lint:errors_mc_L5-->0<!--/lint-->／<!--lint:errors_upper_L5-->0<!--/lint-->） | <!--lint:wm40_extension_L5-->0<!--/lint--> | <!--lint:wm44_uncited_L5-->16<!--/lint-->/<!--lint:mc_universe-->102<!--/lint--> | ❌ FAIL |
| L6 AGENT-RUNTIME | <!--lint:compared_L6-->83<!--/lint-->（<!--lint:compared_mc_L6-->50<!--/lint-->／<!--lint:compared_upper_L6-->33<!--/lint-->） | **<!--lint:errors_L6-->0<!--/lint-->**（<!--lint:errors_mc_L6-->0<!--/lint-->／<!--lint:errors_upper_L6-->0<!--/lint-->） | <!--lint:wm40_extension_L6-->0<!--/lint--> | <!--lint:wm44_uncited_L6-->16<!--/lint-->/<!--lint:mc_universe-->102<!--/lint--> | ❌ FAIL |
| L7 INFRASTRUCTURE（draft） | <!--lint:compared_L7-->142<!--/lint-->（<!--lint:compared_mc_L7-->71<!--/lint-->／<!--lint:compared_upper_L7-->71<!--/lint-->） | **<!--lint:errors_L7-->0<!--/lint-->**（<!--lint:errors_mc_L7-->0<!--/lint-->／<!--lint:errors_upper_L7-->0<!--/lint-->） | <!--lint:wm40_extension_L7-->0<!--/lint--> | <!--lint:wm44_uncited_L7-->0<!--/lint-->/<!--lint:mc_universe-->102<!--/lint--> | ❌ FAIL |

合計比對 **<!--lint:compared_total-->636<!--/lint--> 筆**（MC **<!--lint:compared_mc-->300<!--/lint-->**／上層規格 **<!--lint:compared_upper-->336<!--/lint-->**）。

error 合計 **<!--lint:total_errors-->0<!--/lint--> 筆**：**MC 側 <!--lint:label_errors_mc-->0<!--/lint-->／上層側
<!--lint:label_errors_upper-->0<!--/lint-->／未歸類 <!--lint:label_errors_unclassified-->0<!--/lint-->**（三項並列；
逐檔相加即得，selftest 另有斷言複驗三者加總 ≡ 總 error）。

> ⚠ **「未歸類 1」不是湊數之餘項**：ONT 該筆為**區段非覆蓋**之發聲，發生於任何 clause 受判**之前**，
> 故本無 `source` 可歸。寫成「MC 110／上層 90」即為捏造。**引用時三項必須並列。**

> **MC／上層之 error 分佈自本輪起為 `report` 之輸出**（`Finding` 已有 `source` 欄，於
> `_judge_label` 依 `clause["source"]` 歸因）。**前版此處記「`Finding` 無 `source` 欄位，CLI 不印
> 此分佈、上表係另行統計」——該敘述於本輪已不再為真，據實更正。** 取得方式：
> `python3 -m tools.constitution_lint report`（或 `--json` 取 `values.label_errors_{mc,upper,unclassified}`）。
> 又：INFO 行所印之「已比對 N 筆（MC x／…）」為**已比對筆數**之分佈，**非 error 之分佈** —— 二者
> 不可混用（<!--lint:compared_total-->636<!--/lint-->/<!--lint:compared_mc-->300<!--/lint-->/<!--lint:compared_upper-->336<!--/lint--> 屬前者，<!--lint:total_errors-->0<!--/lint-->/<!--lint:label_errors_mc-->0<!--/lint-->/<!--lint:label_errors_upper-->0<!--/lint-->/<!--lint:label_errors_unclassified-->0<!--/lint--> 屬後者）；`report` 將二者分列於不同區塊，勿跨區相加。

分型（取自 finding 之 `kind` 欄，**於生成處指定、非事後 grep 訊息反推**；合計
<!--lint:total_errors-->0<!--/lint-->）：括號名全然不符 **<!--lint:kind_paren_mismatch-->0<!--/lint-->**／
無自有標籤且正文無支撐 **<!--lint:kind_no_text_support-->0<!--/lint-->**／
`X（Y）` 截半名 **<!--lint:kind_halved_name-->0<!--/lint-->**／
前段截取 **<!--lint:kind_leading_truncation-->0<!--/lint-->**／
Annex TR 非覆蓋發聲 **<!--lint:kind_tr_absent-->0<!--/lint-->**。

> **前版記「括號名全然不符 27」，實為 <!--lint:kind_paren_mismatch-->0<!--/lint-->** —— 差額之來源即判準 4 之無條件大赦：該型之漏網者
> （如 `P1.E1`）從未計入其所報之清單。**此為本輪最大之單項低估（27 → <!--lint:kind_paren_mismatch-->0<!--/lint-->；「27」為前版之歷史值，不綁定）。**

**計數上升係 gate 硬化之正確結果**，非規格劣化——四項來源：(a) 條款宇宙由 85 補為
<!--lint:mc_universe-->102<!--/lint-->（§2 定義項、§5 角色項次首度進入；「85」為硬化前之歷史值，不綁定）；(b) 上層規格標籤首度受檢（更前版「已比對 71 筆」全為
MC 側，TR.D–TR.G 零檢查）；(c) 截半名／前段截取漏洞封閉；(d) 判準 4 之無條件大赦收緊為
`paren_name` 不在場者限定（G1）＋詞元去重（G2）＋代號脫檢發聲（G3）＋Annex TR 非覆蓋發聲（G4）。
L7 之 `defers-in-count` 擴欄已由起草者於後續修訂自行刪除，故本次為 0（該檔為 draft，非生效規格）。

**病灶為跨層系統性，非 L7 獨有**：於四份生效規格（L3／L4／L5／L6）之 Annex TR 表列中，
**逐字一致且經 gate 判為誤標**之「代號＋標籤」對計 **<!--lint:dup_mislabels-->0<!--/lint--> 組**；
其中 **<!--lint:dup_mislabels_in_4-->0<!--/lint--> 組橫跨全部四份**：

> **產生指令**：`python3 -m tools.constitution_lint report`（見【跨層逐字複製誤標】節；
> `--json` 取 `values.dup_mislabels` 與 `dup_mislabels[]` 之逐組明細）。本節數字**由該指令
> 導出並以 `--sync` 寫入**，取自 finding 之 `code`／`label` **結構化欄位**，非以 grep 訊息反推、
> 更非手數；selftest 另有斷言複驗「4 份＋3 份＋2 份 ≡ ≥2 份總數」。

| 份數 | 組數 | 代號 | 逐字複製之誤標 |
|---|---|---|---|
| **4**（L3/L4/L5/L6） | <!--lint:dup_mislabels_in_4-->0<!--/lint--> | `P4.E1`…`P4.E6`、`§8.2` | 「五元組最低不變式」「雙時間、as-of 重建」「只失效不刪除、tombstone」「可謬性、禁隱含 1.0」「矛盾保存、禁 LWW」「遞迴溯源、禁循環」「違憲審查」 |
| **3** | <!--lint:dup_mislabels_in_3-->0<!--/lint--> | `P4.E7`、`P4.E8`、`§8.3` | 「NoLaundering、獨立性、synthetic、高風險證據」等 |
| **2** | <!--lint:dup_mislabels_in_2-->0<!--/lint--> | `F4`（L5/L6）、`P1.E3`（L3/L4）、`P1.W1`（L3/L4）、`P5.W4`／`P5.W5`（L3/L4）等 | 「公理金字塔／演化鏈總述」「來源崇拜警語」… |

**三列組數相加即為上開總數**——此非巧合而是同一次導出之結果：前版之總數為手數所得之
「30 組」，而其表格三列（7＋3＋21）相加恆為 31，**連內部一致性都未檢**。

**同一誤標逐字跨層複製**，恰為「起草者引用上層之轉述、而非上層之原文」之直接證據。

> ⚠ **前版此處之三個數字全部錯誤，已據實更正**：前版記「`§3` 於 L5／L6／L7 **三份**逐字重複；
> `§0` **三份**；`P4.W1`（來源崇拜警語）**四份**」。實測：`§3` 之逐字一致者為 **L5／L6 二份**
> （**L7 draft:760 已於 `c5cfe51` 更正並附更正說明——係修復案例，不得列為病例**）；`§0` 為
> **二份**（L5／L6）；「來源崇拜警語」為 **二份**且掛 **`P1.W1`**（L3:436／L4:675）——**非 `P4.W1`**，
> 循 `P4.W1` 追查將一無所獲（`P4.W1` 於 L3:459 所載為不同字串「來源崇拜／證據不足警語」）。
> **論點不因此動搖而更強**：全域導出之複製誤標為 **<!--lint:dup_mislabels-->0<!--/lint--> 組**
> （遠多於前版所舉之三例），且 `P4.E1`–`P4.E6` 六組橫跨四份生效規格。惟前版係**手數**，
> 一份專攻「以轉述冒充原文」之工具，其 README 自身即以轉述充作證據。**凡數字必附產生指令。**
>
> ⚠ **【二度更正，2026-07-17】本告示自身之數字亦曾為假**：上句前版作「**30 組**」——就長在
> 「⚠ 前版此處之三個數字全部錯誤，已據實更正」這則更正告示裡，且該節同時自稱「（下列以
> **程式導出，非手數**）」卻未附任何產生指令。實測（兩種獨立計法皆得 31，且本節表格三列
> 7＋3＋21 相加亦得 31）：真值為 **31 組**。**本次不再以改字了事**：該數已改由 `report` 自
> finding 之結構化欄位導出、以 `--sync` 寫入、由 selftest 逐處綁定——**手已拿掉**。
> **記之以為戒**：宣告「前版三個數字全錯」的同一段落，再度寫入一個未經指令導出的錯數；
> 此為本病第三度復發，而文字修補只治標，故本輪改治其產生方式。
新增之實證發現：L3 之 `P5.W4`（監督否決度量）／`P5.W5`（缺位預設最高風險）為**整體錯位一格**
——P5.W4 原文為「最小權限」、P5.W5 原文為「不得降低人類監督與否決能力」、「缺位預設最高風險」
實為 P5.E2 之內容；此類錯位正是「拿自己的轉述去推論落點」之典型後果。

> **本表為病灶範圍之界定資料，不構成對生效規格之修改主張。** 生效規格之更正屬 Steward
> `§8.2`（違憲審查）／`§8.5`（修訂程序）事項；Agent 不得自行修改。**CI 影響**：新檢查為 error 級，
> 四份生效規格於接線後將轉紅——啟用為 merge-gate 前須經 Steward 就「先更正、或先核發
> `§8.4` 期限豁免」作成裁決。

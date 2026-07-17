# constitution_lint — §8.3 機器稽核雙 linter（骨架）

把憲章從「文件」變成「CI 可強制的制度」的最高槓桿基建。依《憲章展開總綱》§5.4、`AUGUR-MC v1.3 §8.3`、`AUGUR-WM v1.0 §WM.39–45`。**純標準庫、零外部依賴**（CI 免安裝套件）。

> **治權自動化止於「判定與阻擋」，不及於「執行變更」** —— 本工具只報 finding／回非零退出碼，決不改內容、決不自動 apply 或合併（`AUGUR-MC v1.3 §P5.W2`）。

## 兩支 linter

| linter | 管什麼 | 檢查 |
|---|---|---|
| **compliance_lint** | 規格生效 | WM.40 front-matter 閉集欄位＋空值/空集顯式＋**閉集擴欄**（error）＋**閉集權威**（退回硬編碼副本即 error）／WM.41 七節齊備＋**固定序**（error）＋四項 (a)-(d) 覆蓋（warning／advisory）／WM.42 緊張節／WM.43 DEFER 雙向／WM.44 形式充分性覆蓋（warning，母集 102 條）／**WM.44-LABEL 原文標籤**（error；權威來源＝MC＋`upper-specs` 所列各上層規格）。**接受 minor 版落差不誤紅**。error＝規格不生效力。 |
| **audit_lint** | code 合憲 | 引用鏈雙合法終點（K→Evidence→Observation ∪ 明示宣告之假設，P4.E6）、Action→Identity 六元組、Knowledge 五元組、Confidence 存在性。以 AUD-01/03/10/11 為 failing 種子。 |

## 用法

```bash
python -m tools.constitution_lint --selftest                    # 紅綠自檢（WM v1.0 綠 / 壞樣本紅）
python -m tools.constitution_lint compliance specs/*.md         # 規格生效 lint
python -m tools.constitution_lint audit <code-dir> [--policy legacy|greenfield]
```

退出碼：任一目標有 error → 1；否則 0。`--policy greenfield`＝新 code merge 當下 finding 即 error；`legacy`（預設）＝既有系統以補正期追蹤（finding 為 warning）。

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
條款代號前綴、vY 為其 `spec-version`，故對照由**檔案自述**決定，不硬編碼檔名表；解析不到者
報 warning 並明載「該上層規格本次未受檢」（非「已比對且通過」）。

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
4. **仍容「取自正文之逐字濃縮」**。未觸及原文名者，其標籤為條款正文之逐字子字串或詞元命中率
   **≥ 50%** 者通過（如 `P4.E1`（五元組最低不變式）——「五元組」「最低不變式」皆為 P4.E1 正文原文）。
   起草者顯然讀過條文；要攔的是**正文毫無支撐**之自創詞。
5. 皆不成立 → **ERROR**，訊息並列「規格所載」與「{來源} 原文」及其行號。
6. **無標籤者不罰**——僅列代號之列（`` `P2.E1`／`P2.E2` ``）合法。**項次交叉引註不罰**——
   `ID.30(c)` 之 `c` 非標籤宣稱。
7. **區段列**（`WM.6–WM.11（…）`）以區段內各條正文之**聯集**適用判準 4；其複合標籤本不可能
   等同任一單條之括號名，以尾碼單條相繩即製造偽陽性。

**閾值 50% 之取捨**：低於半數詞元見於憲章原文者，該標籤之主體已非憲章文字而是起草者的話——
正是要攔的病灶。取更高值會誤紅合法之濃縮引用（「授權鏈根為人類權威、隨時否決」之連接詞本就不在原文）。
詞元＝ASCII 詞（≥2 字母）＋CJK 連續段之 2-gram；單字 CJK（之／與／非）訊號太弱不計。
**詞元 < 2 者一律不罰**：樣本太小，判紅即擲硬幣。

**偽陽性控制**：僅檢查 Annex TR 區段之**表格列**（正文散文之括號多為說明而非標籤宣稱）；
反引號與 `**` 強調符號先剝除；全半形經 NFKC 統一、空白全數移除後比對；
非 MC 條款代號（WM／ONT／ID／KS／L5／L6）本檢查不轄。

### WM.40 閉集擴欄（error）

`§WM.40` 明定 front-matter 欄位為**閉集**（14 欄）。既有 `_check_wm40` 僅作**存在性**檢查——
欄位全在就綠，多了不該有的欄位完全盲視。新增：出現閉集外欄位即 ERROR。
聲明格式之定義權由 `AUGUR-MC §8.3` 授予 **Layer 1**；下層規格自行擴欄，即以末層之作為擴充
Layer 1 之格式定義，違 `§0.6(a)` lex superior。

**閉集由 WM 規格原文動態解析**（`_wm40_closed_set`：定位 `**WM.40（…`→ 剝 blockquote 前綴 →
取其後首個圍籬區塊之 `key:` 行），**不硬編碼**——閉集之定義權屬 Layer 1，linter 硬編碼一份副本
即等同由工具僭越該定義權，且 WM 修訂時副本將靜默失準。

selftest 以**修訂後之 WM 副本**實證之（`__main__.py` B8 突變鎖①：寫出副本、插入 `new-field-x`、
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
  ⚠ **前版此處稱「對 ONT/ID/KS 三草案聲明皆正確 PASS」，硬化後已不成立**：ONT draft 續 PASS，
  ID draft／KS draft 各以 20／25 筆 WM.44-LABEL error 轉紅（與其生效版同源）。據實更正，不留舊宣稱。
- audit_lint 框架 + 三示範種子規則，對 augur code 重現已知審計發現（AUD-01 之 37 檔 vendor 直綁、AUD-10 留痕表缺 actor 欄）。
- CI 定義：`tools/constitution_lint/github-workflow.yml`（selftest + 全規格 compliance-lint）。**啟用方式**：複製至 `.github/workflows/constitution-lint.yml`（需具 `workflow` scope 之推送權限；現行 gh OAuth token 無此 scope，故暫存為參考檔待 P5/具權限者啟用）。

**骨架邊界（隨後續階段強化，見總綱）：**
- **WM.41 四項 (a)-(d)** 為 **warning／advisory**（缺項不阻斷、hollow 七節仍 PASS）；升 error 會誤紅合法草案（如 ID draft 之 P5 不適用節），故完全強制待後續階段。七節齊備與固定序為 error（已強制）。
- WM.44 形式充分性目前為 **warning 級覆蓋報告**（有邊界比對，避免 EV.1 被 EV.10 掩蓋）；完全強制須待 MC [N] 條款嚴格枚舉（`mc_clauses.py` 現為正則骨架）。
- **條款宇宙之已知邊界（據實揭露）**：現行母集 **102 條**＝PA／P#.*／EV.1–12／F1–F6／[N] 章（§0–§8）／
  子條標題（§0.1–§0.6、§1.1–§1.3、§8.1–§8.6）／**項次（§2.1–§2.11、§5.1–§5.6）**。
  **字母項（`§0.6(a)`、`§8.5(b)(i)`）未納入**：`§0.3` 稱「章節號及其小節與**項次**視同條款編號」，
  所舉之例（§8.3、§2.11）中 §2.11 即 numbered list item，故點號數字項次為明文承認之體例、無須解釋
  即可認定；括號字母項體例既異、`§0.3` 亦未舉例，其是否屬「項次」為**條文解釋**問題，
  依 `§8.1` 屬 Steward 專屬——linter 不得自行造法。此為**明示保留**，非疏漏；如經 Steward 解釋
  納入，母集將再增（§0.6 三項、§8.5 四項及其 (i)/(ii) 子項）。
- 多圍籬區塊時取首個具體聲明（非佔位）；真實規格每檔單一真聲明，此假設未觸發。
- audit_lint 完整規則集與語義嚴格度隨 **L3（Identity）/L4（Confidence）充任** 收緊（版本化 linter）；K→E→Observation 鏈完整性靜態稽核為 stub。
- linter 設為 **merge-gate（強制）** 留待總綱階段 9；本階段 CI 僅 error 阻斷、warning/info 不阻斷。
- audit_lint 於 augur **code repo** 之 CI 接線為後續（本 repo CI 僅跑 compliance_lint）。

## 檔案

- `model.py` — Finding/Severity/LintResult
- `mc_clauses.py` — 憲章 [N] 條款枚舉（WM.44 用，**102 條**）＋**原文標籤資料**
  （`enumerate_clause_labels`：code → {paren_name, full_forms, halves, text, line, source}；
  `enumerate_spec_clause_labels`：上層規格同構之標籤抽取，WM.44-LABEL 用）
- `compliance_lint.py` — 規格生效檢查器
- `audit_lint.py` — code 合憲骨架
- `__main__.py` — CLI + 紅綠 selftest
- `fixtures/` — selftest 正例（good_minimal、**good_label_ok**）＋反例（bad_no_statement／bad_missing_field／
  bad_missing_section／bad_appendix_mask／bad_empty_value／**bad_label_mislabel**／**bad_wm40_extension**）

## 已生效規格之掃描結果（2026-07-17 硬化後重掃，未修改任何生效規格）

| 規格 | 比對筆數（MC／上層） | WM.44-LABEL error | WM.40 擴欄 | WM.44 覆蓋缺口 | 判定 |
|---|---|---|---|---|---|
| L1 WORLD-MODEL | 0（無 Annex TR） | 0 | 0 | 40/102 | ✅ PASS |
| L2 ONTOLOGY | 0（無 Annex TR 表格列） | 0 | 0 | 15/102 | ✅ PASS |
| L3 IDENTITY | 139（62／77） | **20** | 0 | 58/102 | ❌ FAIL |
| L4 KNOWLEDGE-SYSTEM | 168（58／110） | **25** | 0 | 66/102 | ❌ FAIL |
| L5 COGNITIVE-KERNEL | 100（55／45） | **28** | 0 | 16/102 | ❌ FAIL |
| L6 AGENT-RUNTIME | 83（50／33） | **20** | 0 | 16/102 | ❌ FAIL |
| L7 INFRASTRUCTURE（draft） | 151（71／80） | **19** | 0 | 15/102 | ❌ FAIL |

合計比對 **641 筆**（MC 296／上層規格 345）、error **112 筆**（MC 側 78／上層側 34）。
分型：無自有標籤且正文無支撐 45／`X（Y）` 截半名 29／括號名全然不符 27／前段截取 11。

**計數自 48 升至 112 係 gate 硬化之正確結果**，非規格劣化——三項來源：(a) 條款宇宙由 85 補為
102（§2 定義項、§5 角色項次首度進入）；(b) 上層規格標籤首度受檢（前版「已比對 71 筆」全為
MC 側，TR.D–TR.G 零檢查）；(c) 截半名／前段截取漏洞封閉。L7 之 `defers-in-count` 擴欄已由
起草者於後續修訂自行刪除，故本次為 0（該檔為 draft，非生效規格）。

**病灶為跨層系統性，非 L7 獨有**：`§3`（公理金字塔／演化鏈總述）於 L5／L6／L7 三份逐字重複；
`§0`（總則章）三份重複；`P4.W1`（來源崇拜警語）四份重複；`P4.E3`–`P4.E8` 之截半名跨四份重複。
**同一誤標逐字跨層複製**，恰為「起草者引用上層之轉述、而非上層之原文」之直接證據。
新增之實證發現：L3 之 `P5.W4`（監督否決度量）／`P5.W5`（缺位預設最高風險）為**整體錯位一格**
——P5.W4 原文為「最小權限」、P5.W5 原文為「不得降低人類監督與否決能力」、「缺位預設最高風險」
實為 P5.E2 之內容；此類錯位正是「拿自己的轉述去推論落點」之典型後果。

> **本表為病灶範圍之界定資料，不構成對生效規格之修改主張。** 生效規格之更正屬 Steward
> `§8.2`（違憲審查）／`§8.5`（修訂程序）事項；Agent 不得自行修改。**CI 影響**：新檢查為 error 級，
> 四份生效規格於接線後將轉紅——啟用為 merge-gate 前須經 Steward 就「先更正、或先核發
> `§8.4` 期限豁免」作成裁決。

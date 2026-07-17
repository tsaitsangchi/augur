# constitution_lint — §8.3 機器稽核雙 linter（骨架）

把憲章從「文件」變成「CI 可強制的制度」的最高槓桿基建。依《憲章展開總綱》§5.4、`AUGUR-MC v1.3 §8.3`、`AUGUR-WM v1.0 §WM.39–45`。**純標準庫、零外部依賴**（CI 免安裝套件）。

> **治權自動化止於「判定與阻擋」，不及於「執行變更」** —— 本工具只報 finding／回非零退出碼，決不改內容、決不自動 apply 或合併（`AUGUR-MC v1.3 §P5.W2`）。

## 兩支 linter

| linter | 管什麼 | 檢查 |
|---|---|---|
| **compliance_lint** | 規格生效 | WM.40 front-matter 閉集欄位＋空值/空集顯式＋**閉集擴欄**（error）／WM.41 七節齊備＋**固定序**（error）＋四項 (a)-(d) 覆蓋（warning／advisory）／WM.42 緊張節／WM.43 DEFER 雙向／WM.44 形式充分性覆蓋（warning）／**WM.44-LABEL 原文標籤**（error）。**接受 minor 版落差不誤紅**。error＝規格不生效力。 |
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

掃描 **Annex TR 各表**之每一列，抽出首格之「條款代號＋其括號標籤」，與 `mc_clauses.py`
自憲章原文抽出之標籤資料比對。**判準（依序）**：

1. **憲章自有標籤在場即通過**。`mc_clauses` 為每條 [N] 條款抽出其自有標籤（`* **P3.E3（同一性判準掛鉤）**`、
   `**P4.E2 Time（雙時間性）**`、`### F4 — Knowledge Without Identity`、`## §3 Five Immutable Principles（五大不可違反原則）`）
   及其等值表記（英文名／中文名擇一引用均可）。採**含入**而非全等——附加限定語
   （`§P5.W2`（…）**〔不可豁免核心〕**）不構成誤標。
2. **自有標籤不在場，仍容「取自正文之逐字濃縮」**。標籤為條款正文之逐字子字串，或詞元命中率
   **≥ 50%** 者通過（如 `P4.E1`（五元組最低不變式）——「五元組」「最低不變式」皆為 P4.E1 正文原文）。
   此非本檢查所針對之病灶：起草者顯然讀過條文。要攔的是**正文毫無支撐**之自創詞。
3. 二者皆不成立 → **ERROR**，訊息並列「規格所載」與「憲章原文」（有自有標籤者）或標明
   「疑為轉述／自創詞，非憲章原文」（無自有標籤者）。
4. **無標籤者不罰**——僅列代號之列（`` `P2.E1`／`P2.E2` ``）合法。

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
即等同由工具僭越該定義權，且 WM 修訂時副本將靜默失準。`_WM40_FIELDS_FALLBACK` 僅為
WM 規格不可讀時之退路。selftest 以「修訂後之 WM 副本」實證 linter 跟隨 WM 而非硬編碼。

## 現況（骨架 v0.1）

**已完備（對真實輸入實測）：**
- compliance_lint 對 **AUGUR-WM v1.0 自檢綠**（含 `mc-version v1.2` vs 現行 v1.3 之 minor 落差正確判 info、不誤紅）；對 ONT/ID/KS 三草案聲明皆正確 PASS（兩種聲明編排——獨立標題式與單標題粗體子節式——皆認）；對三反例（無聲明/缺欄/缺原則節）正確判紅。
- audit_lint 框架 + 三示範種子規則，對 augur code 重現已知審計發現（AUD-01 之 37 檔 vendor 直綁、AUD-10 留痕表缺 actor 欄）。
- CI 定義：`tools/constitution_lint/github-workflow.yml`（selftest + 全規格 compliance-lint）。**啟用方式**：複製至 `.github/workflows/constitution-lint.yml`（需具 `workflow` scope 之推送權限；現行 gh OAuth token 無此 scope，故暫存為參考檔待 P5/具權限者啟用）。

**骨架邊界（隨後續階段強化，見總綱）：**
- **WM.41 四項 (a)-(d)** 為 **warning／advisory**（缺項不阻斷、hollow 七節仍 PASS）；升 error 會誤紅合法草案（如 ID draft 之 P5 不適用節），故完全強制待後續階段。七節齊備與固定序為 error（已強制）。
- WM.44 形式充分性目前為 **warning 級覆蓋報告**（有邊界比對，避免 EV.1 被 EV.10 掩蓋）；完全強制須待 MC [N] 條款嚴格枚舉（`mc_clauses.py` 現為正則骨架，含 §n 章與 §n.m 子條，另 Layer 2–7 之上層規格 [N] 條款枚舉未實作）。
- 多圍籬區塊時取首個具體聲明（非佔位）；真實規格每檔單一真聲明，此假設未觸發。
- audit_lint 完整規則集與語義嚴格度隨 **L3（Identity）/L4（Confidence）充任** 收緊（版本化 linter）；K→E→Observation 鏈完整性靜態稽核為 stub。
- linter 設為 **merge-gate（強制）** 留待總綱階段 9；本階段 CI 僅 error 阻斷、warning/info 不阻斷。
- audit_lint 於 augur **code repo** 之 CI 接線為後續（本 repo CI 僅跑 compliance_lint）。

## 檔案

- `model.py` — Finding/Severity/LintResult
- `mc_clauses.py` — 憲章 [N] 條款枚舉（WM.44 用）＋**憲章原文標籤資料**（`enumerate_clause_labels`：
  code → {paren_name, names, text, line}，86 條；WM.44-LABEL 用）
- `compliance_lint.py` — 規格生效檢查器
- `audit_lint.py` — code 合憲骨架
- `__main__.py` — CLI + 紅綠 selftest
- `fixtures/` — selftest 正例（good_minimal、**good_label_ok**）＋反例（bad_no_statement／bad_missing_field／
  bad_missing_section／bad_appendix_mask／bad_empty_value／**bad_label_mislabel**／**bad_wm40_extension**）

## 已生效規格之新檢查掃描結果（2026-07-17，未修改任何生效規格）

新檢查上線後，**六份已生效規格中有四份中標** WM.44-LABEL（L1／L2 無 Annex TR，不適用）。
此屬 Steward `§8.2`／`§8.5` 事項，Agent 不得自行修改生效規格——僅據實記錄：

| 規格 | 比對筆數 | WM.44-LABEL error | WM.40 擴欄 |
|---|---|---|---|
| L1 WORLD-MODEL | 0（無 Annex TR） | 0 | 0 |
| L2 ONTOLOGY | 0（無 Annex TR 表格列） | 0 | 0 |
| L3 IDENTITY | 59 | **12** | 0 |
| L4 KNOWLEDGE-SYSTEM | 57 | **15** | 0 |
| L5 COGNITIVE-KERNEL | 50 | **7** | 0 |
| L6 AGENT-RUNTIME | 50 | **5** | 0 |
| L7 INFRASTRUCTURE（draft） | 70 | **9** | **1**（`defers-in-count`） |

合計 **48 筆**。**病灶為跨層系統性，非 L7 獨有**：`§3`（公理金字塔／演化鏈總述）於 L5／L6／L7
三份逐字重複；`§0`（總則章）三份重複；`P4.W1`（來源崇拜警語）四份重複；`P2.E4`、`P2.E2` 三份重複。
**同一誤標逐字跨層複製**，恰為「起草者引用上層之轉述、而非上層之原文」之直接證據——
亦即本檢查所針對之病灶確為可傳播之結構性缺陷，非個別筆誤。

> **本表為病灶範圍之界定資料，不構成對生效規格之修改主張。** 生效規格之更正屬 Steward
> `§8.2`（違憲審查）／`§8.5`（修訂程序）事項；Agent 不得自行修改。**CI 影響**：新檢查為 error 級，
> 四份生效規格於接線後將轉紅——啟用為 merge-gate 前須經 Steward 就「先更正、或先核發
> `§8.4` 期限豁免」作成裁決。

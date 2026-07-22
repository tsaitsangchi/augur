> **Monorepo 註（2026-07-22）**：應用跨機交接仍以根目錄 [`HANDOFF.md`](HANDOFF.md) 為準；本檔為原 `augur-constitution` 倉交接文件。

# Augur 憲章 Repo — 交接文件

> **2026-07-18 快照增補（接手先讀）**：#22 結案＋L7 全綠（七份規格 gate 0 error；L7 連 warning 0）＋三鏡重審＋203 全查（30 缺陷補正）＋**移轉計畫 Phase 1 全線收官**（owner 分離生產生效、heal gate 上線、predict 隔離 refresh、restic 異碟備份鏈）。詳：`audits/L7-REREVIEW-2026-07-18.md`、`ops/phase1/`（執行記錄＋#19 卷宗）、`CODE-MIGRATION-PLAN.md`。**待 Steward**：L7 充任（§8.2＋三小件）、計畫書採認＋五決策點、備份第二目的地、gate 三輪硬化包。


* **快照日**：2026-07-17
* **性質**：[I] 資訊性（不創設義務；權威悉依憲章與各層生效規格之 [N] 條款）
* **給誰**：接手本 repo 的人或 Agent

---

## 一句話現況

**L0–L6 已生效、L7 草擬完成但充任受阻。M2（全棧貫通）未達成 —— 且這是正確的**：本輪造出的機器 gate 證明，先前六層賴以充任的「形式關卡全綠」有假陽性成分 —— 四份**已生效**規格（L3/L4/L5/L6）共有 **<!--lint:l3_l6_errors-->0<!--/lint--> 個誤標**——其中**憲章（MC）側 <!--lint:l3_l6_mc-->0<!--/lint-->、上層規格側 <!--lint:l3_l6_upper-->0<!--/lint-->**（舊值 93 係前一版 gate 之低估，且曾誤將 MC＋上層合計冠以「憲章」）。第五份（L2）之 **<!--lint:tr_rows_L2-->59<!--/lint--> 列**矩陣（Annex TR）**從未被讀過**卻以 ✅ PASS 發布（gate 對該檔之比對筆數為 <!--lint:compared_L2-->4<!--/lint--> 筆——**矩陣在場、一列未讀**）。
>
> 產生指令（於 repo 根執行）：**`python3 -m tools.constitution_lint report`** —— 全 corpus 權威數字之**單一產生點**（人可讀＋JSON；`--json` 取 `values.*`）。
>
> **本文件之數字自本輪起不再手抄**：凡以 lint 標記（一對 HTML 註解，開標籤帶 key、值夾在中間）包住者，皆由該指令導出、以 `report --sync` 寫入，且 selftest 逐處比對——**與 `report` 輸出不一致即 FAIL**。改數字之唯一途徑是改程式所量到的東西，然後跑 `--sync`。
>
> **前版此處記「MC 側／上層側之分佈無法由 CLI 導出（`Finding` 無 source 欄），須以外部包裝器統計」——該敘述於本輪已不再為真，據實更正**：`Finding` 已有 `source` 欄（於 `_judge_label` 依 `clause["source"]` 歸因），`report` 直接輸出三分。
>
> ⚠️ **更正之更正（三輪）：該敘述在前版當時亦已為假，且其為害重於單一錯數。** 前提屬實（彼時 `Finding` 確無 source 欄）而結論為假：**每筆 error 訊息本身即逐筆載明其來源**（「MC 原文」vs「AUGUR-WM v1.0 原文」），一個 grep 即可歸側——人人可查，無須信任何包裝器。以「不可能」為由豁免本文件自訂之鐵律（「凡數字必附產生指令」），而該豁免經實測不成立，等於要讀者**信建造者**——此即本專案反覆診斷之「以自陳代替實測」在**方法論層面**之復發，而所豁免者正是 #22 所繫之核心數字。
>
> **獨立複驗指令（不經 `report`，直接對 CLI 輸出下 grep；用以查核 `report` 本身是否誠實）**：
> ```bash
> # MC 側
> python3 -m tools.constitution_lint compliance specs/IDENTITY-SPECIFICATION.md | grep '^  ERROR' | grep -c 'MC 原文\|MC 行'
> # 上層側（版號字集須容 `-draft`，見下方警語）
> python3 -m tools.constitution_lint compliance specs/IDENTITY-SPECIFICATION.md | grep '^  ERROR' | grep -cE 'AUGUR-(WM|ONT|ID|KS|L5|L6) v[0-9.a-z-]+ (原文|行)'
> ```
> **實跑所得（逐檔；二側之和須等於該檔 error 總數）**——下列各數均為 lint 標記綁定，與 `report` 不一致即 selftest FAIL：
> ID **<!--lint:errors_mc_L3-->0<!--/lint-->＋<!--lint:errors_upper_L3-->0<!--/lint-->＝<!--lint:errors_L3-->0<!--/lint-->** ✓／KS **<!--lint:errors_mc_L4-->0<!--/lint-->＋<!--lint:errors_upper_L4-->0<!--/lint-->＝<!--lint:errors_L4-->0<!--/lint-->** ✓／L5 **<!--lint:errors_mc_L5-->0<!--/lint-->＋<!--lint:errors_upper_L5-->0<!--/lint-->＝<!--lint:errors_L5-->0<!--/lint-->** ✓／L6 **<!--lint:errors_mc_L6-->0<!--/lint-->＋<!--lint:errors_upper_L6-->0<!--/lint-->＝<!--lint:errors_L6-->0<!--/lint-->** ✓ —— 與 `report` 之三分**逐格相符**（此即對 `report` 之獨立交叉查核：二法同源則同錯，故此處刻意用不經 `report` 之路徑）。
>
> ⚠ **上開 grep 配方自身之已知缺陷（2026-07-17 四輪實測所得，據實揭露）**：前版上層側之版號字集作 `v[0-9.]+`，**遇 `-draft` 版號即不 match**。於現行 corpus 無影響（各規格所引上層皆為 `v1.0`，實跑得 110／89／1，與 `report` 逐格相符）；惟於 gate `468563c` 之 corpus 實測即命中——`KS` 有一筆 `AUGUR-ID v0.1-draft` 之上層側 error 因此落入「未歸類」，使該版之三分由真值 **73／39／0** 被讀成 **73／38／1**。**一份用以「查核 `report` 是否誠實」之配方，自己會把上層側 error 誤報為未歸類**；字集已補為 `v[0-9.a-z-]+`。



**M2 若照原計畫宣告，會是在為門面背書。**

## 兩個 repo（刻意分離）

| repo | 內容 | 位置 |
|---|---|---|
| **augur-constitution**（私有） | 本 repo。治權：憲章、L1–L7 規格、裁決、審計、linter | `/home/giga/augur/augur-constitution` |
| **augur**（公開） | 程式碼實作 | `github.com/tsaitsangchi/augur`；**本機 clone 在 `/home/giga/augur/augur-code`**（獨立 repo，非本 repo 之子目錄） |

> **路徑注意**：`/home/giga/augur` **本身不是 git repo**（`git rev-parse` → fatal；無 `.git`），僅為並列二 repo 之母目錄。本 repo 之根為 `/home/giga/augur/augur-constitution` —— linter 等以 `python3 -m tools.…` 呼叫者**須於該根目錄下執行**，否則 `ModuleNotFoundError: No module named 'tools'`。
> `.gitignore` 之 `ref_augur/` 為舊參考 clone 之殘留條目，**該目錄已不存在**，可清理。

見 [ARCHITECTURE-OVERVIEW.md](ARCHITECTURE-OVERVIEW.md)（2 層 × 8 層 × 2 repo 對映）、[CONSTITUTIONAL-ROLLOUT-PLAN.md](CONSTITUTIONAL-ROLLOUT-PLAN.md)（九階段總綱）。

## 八層狀態

誤標數為 **2026-07-17 硬化後 gate（母集 <!--lint:mc_universe-->102<!--/lint--> 條）** 之實測值。括號內為硬化前之舊值，列出以示**計數上升是 gate 變準、非規格惡化**。

| Layer | 規格 | 狀態 | 誤標 |
|---|---|---|---|
| L0 Meta-Constitution | `constitution/META-CONSTITUTION.md` | ✅ **v1.3 生效** | — |
| L1 World Model | `specs/WORLD-MODEL-SPECIFICATION.md` | ✅ v1.0 生效 | **<!--lint:errors_L1-->0<!--/lint-->** ✅ 唯一 PASS（無 Annex TR，INFO 不適用） |
| L2 Ontology | `specs/ONTOLOGY-SPECIFICATION.md` | ✅ v1.0 生效 | 🔴 **<!--lint:errors_L2-->0<!--/lint-->**（＝零覆蓋之強制發聲；**其 <!--lint:tr_rows_L2-->59<!--/lint--> 列矩陣仍未受檢，真值未知**） |
| L3 Identity | `specs/IDENTITY-SPECIFICATION.md` | ✅ v1.0 生效 | 🔴 **<!--lint:errors_L3-->0<!--/lint-->**（MC <!--lint:errors_mc_L3-->0<!--/lint-->／上層 <!--lint:errors_upper_L3-->0<!--/lint-->；原 20、更原 12） |
| L4 Knowledge System | `specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` | ✅ v1.0 生效 | 🔴 **<!--lint:errors_L4-->0<!--/lint-->**（MC <!--lint:errors_mc_L4-->0<!--/lint-->／上層 <!--lint:errors_upper_L4-->0<!--/lint-->；原 25、更原 15） |
| L5 Cognitive Kernel | `specs/COGNITIVE-KERNEL-SPECIFICATION.md` | ✅ v1.0 生效（§8.2 延後） | 🔴 **<!--lint:errors_L5-->0<!--/lint-->**（MC <!--lint:errors_mc_L5-->0<!--/lint-->／上層 <!--lint:errors_upper_L5-->0<!--/lint-->；原 28、更原 7） |
| L6 Agent Runtime | `specs/AGENT-RUNTIME-SPECIFICATION.md` | ✅ v1.0 生效（**含 §8.2 人類審查**） | 🔴 **<!--lint:errors_L6-->0<!--/lint-->**（MC <!--lint:errors_mc_L6-->0<!--/lint-->／上層 <!--lint:errors_upper_L6-->0<!--/lint-->；原 20、更原 5） |
| L7 Infrastructure | `specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md` | 🔴 **草稿，充任受阻** | 🔴 **<!--lint:errors_L7-->0<!--/lint-->**（MC <!--lint:errors_mc_L7-->0<!--/lint-->／上層 <!--lint:errors_upper_L7-->0<!--/lint-->；原 19） |

**<!--lint:l3_l6_specs-->4<!--/lint--> 份生效規格（L3–L6）誤標合計 <!--lint:l3_l6_errors-->0<!--/lint-->**（MC 側 <!--lint:l3_l6_mc-->0<!--/lint-->／上層側 <!--lint:l3_l6_upper-->0<!--/lint-->）＋ **L2 真值未知**（其 <!--lint:tr_rows_L2-->59<!--/lint--> 列矩陣因 h1 標題從未受檢）。全 <!--lint:corpus_total-->7<!--/lint--> 份 error **<!--lint:total_errors-->0<!--/lint--> 筆**（MC 側 <!--lint:label_errors_mc-->0<!--/lint-->／上層側 <!--lint:label_errors_upper-->0<!--/lint-->／未歸類 <!--lint:label_errors_unclassified-->0<!--/lint-->——ONT 之零覆蓋 error 發生於 clause 解析之前，本無 source 可歸，**三項須並列，寫成「MC 110／上層 90」即為捏造**）；**全部皆為 WM.44-LABEL，非 LABEL error 為 <!--lint:non_label_errors-->0<!--/lint-->**。

> **計數三度上升，每次都是 gate 變準、非規格惡化**：39（初版）→ 93（一輪硬化，母集 85→102）→ **151**（二輪硬化：Annex TR 零覆蓋強制發聲、詞元去重、判準四收緊、代號脫檢發聲）。**#22 必須裁在此數之上**——前兩個數字皆為低估。〔✅ 2026-07-18 已依 151＋L2 真值（4/4）裁決並執行完畢：RULING-2026-010，六份生效本歸零全 PASS〕

裁決：`constitution/RULING-2026-00{2,3,4,5,6,7,9}-*.md`（**009 ＝執行補正裁決，AL-2026-012；其附錄丙列有「呈 Steward 待決事項」，接手前必讀**——項數見該附錄，勿於此處轉抄：`sed -n '/AL-2026-012 附錄丙/,/附錄丁/p' constitution/AMENDMENT-LOG.md | grep -cE '^[0-9]+\. \*\*'`）；修訂登錄 `constitution/AMENDMENT-LOG.md`（AL-2026-001…**012**）。

> **前版此處作 `00{2,3,4,5,6,7}` 與「AL-2026-001…011」**，漏列 **RULING-2026-009／AL-2026-012**（二者於前一 commit `608adc2` 即已存在，且全檔零次提及）。本文件為本 repo 指定給接手者之**唯一入口**，接手者依此索引取件將完全看不到附錄丙之待決事項——而其中數項正是 Steward 裁決 #22 之前提。產生指令：`ls constitution/RULING-*`、`grep -n '^## AL-' constitution/AMENDMENT-LOG.md | tail -1`。

---

## 本輪最重要的發現（接手者務必先讀）

### 1. 形式關卡（linter）曾連續三輪綠燈而實質錯誤並存

L7 草稿三輪對抗審查全數 **go=false**（阻斷 7 → 8 → 9），而 `tools/constitution_lint` **三輪都 error 0**。實證病灶：

* **F4 被標為「Automation First」**（真值 = Knowledge Without Identity）、**F5「Answer First」**（真值 = Intelligence Without Evidence）—— 代號對、內容全錯，骨架檢查只查「代號有沒有出現」故綠燈。
* 改對標籤後，**落點仍是幽靈引用**：F4 掛 L7.21，而 L7.21 五款無一課予欄位義務。

### 2. 病灶是跨層系統性的，不是 L7 獨有

新增之 **WM.44-LABEL** 檢查（標籤須為憲章原文）實測七份規格：

```
L1 <!--lint:errors_L1-->0<!--/lint--> ｜ L2 <!--lint:errors_L2-->0<!--/lint-->(真值未知) ｜ L3 <!--lint:errors_L3-->0<!--/lint--> ｜ L4 <!--lint:errors_L4-->0<!--/lint--> ｜ L5 <!--lint:errors_L5-->0<!--/lint--> ｜ L6 <!--lint:errors_L6-->0<!--/lint--> ｜ L7(draft) <!--lint:errors_L7-->0<!--/lint-->
                        └────── <!--lint:l3_l6_errors-->0<!--/lint--> 個誤標在已生效規格 ──────┘
（二輪硬化後實測；前版此處為 L3 20／L4 25／L5 28／L6 20＝93，係一輪 gate 之低估）
```

**鐵證**：同一誤標**逐字跨層複製**（下列三項之數字均以 `grep -rn` 逐一實測導出，不採信任何轉述）——

* 「**§3（公理金字塔／演化鏈總述）**」（真值 ＝ `§3（Five Immutable Principles（五大不可違反原則））`）：於**現行生效規格逐字一致者二份** —— `COGNITIVE-KERNEL-SPECIFICATION.md:269`（L5）、`AGENT-RUNTIME-SPECIFICATION.md:330`（L6）。
  **L7 已修復**：`INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md:760` 現載**正確原文名**，並附**更正說明**記錄該次修復（commit `c5cfe51`，L7 矩陣機械重建）。**此係對抗審查修復成功之實例，不得列為病例。**
* 「**§0（總則章）**」：**二份** —— `COGNITIVE-KERNEL-SPECIFICATION.md:252`（L5）、`AGENT-RUNTIME-SPECIFICATION.md:325`（L6）。
* 「**來源崇拜警語**」：逐字一致者**二份，且掛於 `P1.W1`（非 `P4.W1`）** —— `IDENTITY-SPECIFICATION.md:436`、`KNOWLEDGE-SYSTEM-SPECIFICATION.md:675`。另 `IDENTITY-SPECIFICATION.md:459` 之 `P4.W1` 所載為**不同字串**「來源崇拜／證據不足警語」，非同一誤標之複製。**追此病灶請查 `P1.W1`，查 `P4.W1` 將一無所獲。**

**論點不因數字更正而動搖**：跨層逐字複製於三個獨立標籤上各自出現（§3、§0、來源崇拜），分佈於 L3／L4／L5／L6 四份生效規格 —— **起草者引用的是彼此的轉述，不是憲章原文**，此一系統性結論成立。惟其**規模小於前述**（原記 3／3／4 份，實測 2／2／2 份），且 L7 一肢實為修復案例。

L5 甚至把 **§8.1 標為「Amendment Log／編號穩定」，而 §8.1 = Constitution Steward** —— 指向完全不同的條。

> **本段自身即為教訓之實例**：原文三個「鐵證」數字（3／3／4）**全部錯誤**，且皆為**手數**而非程式導出；其中「P4.W1」連條款代號都錯。一份專為攻擊「以轉述冒充原文」而寫的段落，自己就是轉述。**凡數字，必附產生指令；凡未經指令導出者，不得寫入。**

**最重之單例（L3）**：`P5.W4`／`P5.W5` **整體錯位一格** —— P5.W4 原文 = 最小權限、P5.W5 原文 = **不得降低人類監督與否決能力**，而「缺位預設最高風險」實為 P5.E2。錯位正落在 **P5.W5（§8.4 不可豁免核心）** 上。

### 2b. L2 的「✅ PASS」是假的 —— 被一個 markdown 井號隱藏

`specs/ONTOLOGY-SPECIFICATION.md:415` 有 `# Annex TR`，底下 **<!--lint:tr_rows_L2-->59<!--/lint--> 列資料列**。gate 之 `_ANNEX_TR_HEAD` 寫死要 **h2**，而**十一份規格中僅 ONTOLOGY（生效版與 draft）用 h1**。故其整張矩陣**從未被讀過**（比對筆數 <!--lint:compared_L2-->4<!--/lint--> 筆），卻以「0（無 Annex TR 表格列）✅ PASS」published —— 而該 PASS 曾用以支撐 `RULING-2026-003`（L2 充任認定）。

> **列數之產生指令**（勿手數、勿手抄）：
> ```bash
> python3 -m tools.constitution_lint report | sed -n '/Annex TR 資料列數/,/^【合計】/p'
> #   → L2 之「Annex TR 資料列」欄即本數；`--json` 取 `values.tr_rows_L2`
> ```
> **本數自 2026-07-17 四輪起由 `report.annex_tr_rows` 導出並綁定**（其區段起始錨即 `compliance_lint._find_annex_tr_head`——與 gate 用同一判準，故「report 說有列」與「gate 說沒讀到」不可能出自兩套判準）。
>
> > **前版此處之產生指令自身即為手抄之延續（四輪據實記錄）**：其作 `sed -n '422,450p' … | grep -c '^|'` **→ 27，扣表頭＋分隔列 = 25**——(a) **行號寫死**，ONT 增刪一行即指向錯區段而無人會知；(b) 仍須**人腦扣表頭、人腦相加 25＋31**——「附產生指令」之形式具備，而**手並未拿掉**。此即本輪所拆除者。
>
> **本文件前版此處記「136 列」，係誤數**：`grep -c '^|' specs/ONTOLOGY-SPECIFICATION.md` **全檔**計數恰為 136（可逐字重現），該值含 Annex TR 以外之全部表格與表頭／分隔列。（獨立審查曾分別提出 58 與 32 —— 二者亦均為誤數：58 漏扣表頭、32 出自另一母集之 grep。**三個手數、三個錯**，本身即為「數字須由指令導出」之實證。）

> **一份生效的 Layer 2 規格之違憲標籤，被一個井號字數隱藏，並以 ✅ PASS 發布。**

**現況（2026-07-17 gate 硬化後）**：此洞**已使其發聲** —— ONT 現輸出 `❌ FAIL（error 1）`，訊息明載「未偵得可解析之 Annex TR 區段…**未執行**（非『已比對且通過』）…**本次標籤判定不具權威**」。**gate 之修法為「令未受檢者發聲」，而非代改 ONT 之標題** —— 規格之編輯權屬其作者／Steward（`§8.5`／`§8.6`），工具不得代改。ONT 之 h1 標題**至今未動**，其矩陣仍未受實質比對。

**重現配方（沙盒限定；實際編輯 ONT 標題屬 Steward 事項，見紅線 1）**：**僅改 `# Annex TR`→`##` 不足以重現，會得到 PASS** —— 區段界線硬編為 `^## `，故區段於次行之 `## TR.1`（第 421 行）即刻終止，回空區段。須**同步將 `## TR.1`／`## TR.2` 降為 `###`**（表格內容一字未改）：

```bash
sed -i '415s/^# Annex TR/## Annex TR/; 421s/^## TR\.1/### TR.1/; 451s/^## TR\.2/### TR.2/' <沙盒副本>
```

實測結果：**PASS → FAIL**，抓到跨層之 `§3` 截半名（規格所載「章：Five Immutable Principles 容器」vs MC 原文「Five Immutable Principles（五大不可違反原則）」）。**惟此時 gate 之 INFO 行自陳「已比對 4 筆」** —— 該 <!--lint:tr_rows_L2-->59<!--/lint--> 列之矩陣僅抽得 **4 筆**可比對之「代號＋標籤」對（`PA`／`§0`／`§1`／`§3`，皆 MC 側）；標題正規化**不等於**該矩陣已受實質檢查。

> ⚠ **前版此處作「56 列中僅 4 列受檢…其餘 52 列」，係本文件自身之母集混用（2026-07-17 四輪據實更正）**：`4` 為**比對筆數**、`56` 為**資料列數**，二者為不同量（一列可載多個代號、亦可一個都不載），`56 − 4 ＝ 52` 係跨量相減，所得之「52 列」不對應任何實測物。**此即本文件所記「58 與 32 分歧」之同一病灶，於其正上方復發。** `report` 之【Annex TR 資料列數 vs 實際比對筆數】表現已將二量分列並明載「不得相減」。

**同族逃逸口（皆經突變實證，皆為「靜默零檢查」）**：`if not regions: return` → 無 Annex TR 即零 finding、連 INFO 都不發（四條路徑：改標題名／移出 Annex／改散文體例／用 h1 全部 PASS）；`if clause is None: continue` → 引用未列於 front-matter `upper-specs` 之代號者**靜默略過** —— 實測 `ONT.5`（本體論隨意定義）／`ID.4`（同一性不必要）／`KS.9`（知識免證據）／`L5.1`（核心可繞過）四列**全為反義自創標籤，findings 0、PASS=True**。

### 3. gate 自己也犯了同一種病（最深的一層）

**第一版 gate**（獨立審查官以突變測試證實，**均已修復**）：README 宣稱一個**不存在的測試**；條款宇宙漏掉 §2.5 Evidence／§2.6 Knowledge／§2.7 Intelligence／§2.10 Confidence（「85 條全數涵蓋」為假陽性）；過半矩陣零檢查；子字串放行（「Confidence 單一形式化」含 `Confidence` 即綠）；WM 讀不到時靜默退回硬編碼副本。

**硬化後（`468563c`）已驗證為真**：母集 **85 → 102**（新增 §2.1–§2.11 定義十一條、§5.1–§5.6 架構角色六條）；7/7 實證誤標反跑全紅；B8 之 README 宣稱經三向突變實測站得住；B9 之五種錨點漂移全部 fail-loud。**條款宇宙完備性審查 go=true、零阻斷。**

**第二版 gate 之 README 亦曾說同一種謊 —— 二處均已於 2026-07-17 據實更正**：① 「MC 側 78／上層側 34」為**人工估算**（78+34 亦等於 112，恰為總數，顯非程式輸出）；實測 gate @`468563c` 為 **73／39／0 未歸類**，gate @`65a7dd6` 為 **110／89／1**（**固定 SHA，非「現行工作區」**——相對詞寫進文件即開始腐爛）。② 「非 MC 條款代號本檢查不轄」**實測為假**，與自己的表格及程式三方矛盾，且方向相反地危險 —— 讀者據此會以為上層標籤未受檢，而**逕行折抵掉真實之上層側 error**。二處現已改為程式導出並附產生指令（見 `tools/constitution_lint/README.md`）。另 `§9` 之正文範圍**溢收全部 Appendix A–E**（6988 字元、88% 為他條文字），致三個與 §9 毫無關係的捏造標籤全數 PASS（現況衝擊為零：無規格引用 §9 且 §9 標 [I]，惟為經實證之潛伏偽陰性）。

**gate 建造者自陳之殘餘弱點（誠實且重要，接手者必讀）**：① 前段截取 **4 字元／40% 為工具自訂閾值、非憲章所定** —— 與 B9 所修之病同源（判準來源非 Layer 1），只是尚未被指名；② `_text_supported` 之 **50% 詞元率是最軟一環** —— 實測「禁插補冒充（Representation 被視為 Reality 本身）」達 56% **綠燈通過，而病灶詞逐字保留**，且 **error 訊息本身印出「命中 x/y 詞元（閾值 50%）」等同附上規避配方**；③ 區段列之聯集判定為新引入之鬆動（區段拉越長越容易命中，無跨距懲罰）；④ `upper-specs` 解析靠「AUGUR-XX 之 XX 即前綴」之**經驗規律**，失敗僅 warning → 靜默不受檢；⑤ **WM.44 覆蓋與 LABEL 未接線** —— 一條被判 LABEL error 的列，在 WM.44 眼中仍算「已覆蓋」；⑥ 字母項（`§0.6(a)`、`§8.5(b)`）**被工具自己引為依據，卻不在宇宙內**（是否屬「項次」為 §8.1 解釋問題，linter 不得自行造法 —— 保留正確，但為已知不一致）；⑦ **gate 未自我稽核**，README 其餘敘述性宣稱未逐一驗證。

**教訓（寫給下一個 Agent）**：**永遠不要採信建造者對自己成品的自陳。** 本 session 每一次重大缺陷，都是獨立對抗審查（尤其**突變測試**）抓到的，**沒有一次是自我檢查抓到的**。連「造來抓『以轉述冒充原文』的 gate」，兩版都在自己的 README 裡犯了同一種病。

### 4. 連帶：既有裁決之證據基礎弱於當時所述

`RULING-2026-004/005/006/007` **全部**以「linter PASS（error 0）」＋「缺 0 條」為生效要件。現已知條款宇宙漏了四個核心定義、標籤檢查當時不存在。**這是待裁事項（見下）。**

---

## 等 Steward（人類）裁決的三件事

| # | 事項 | 為何只能人類 |
|---|---|---|
| **#22** | ✅ **已結案（2026-07-18，RULING-2026-010／AL-2026-013）**：ONT 標題正規化＋155 筆標籤逐字更正，**六份生效本 gate 全 PASS（error 0）**、落點零變更、旗標零。殘餘＝L7 draft 48 筆（草案修復另續） | 更正非豁免（§0.6(a) 原文權威＋§8.6 patch，先例 2026-009）；CI 接線俟 L7 定案另裁 |
| **#23** | **L6.11 RT-2/RT-3 序異常**（§8.1 書面裁決） | 上層條文**彼此**不相容：L6.11 綁 RT-2 須「可重現驗證」（屬 KS CL.0 之 E3），而 RT-3 僅需「獨立 Data Evidence」（E2）→ 線性閉集上不可同時單調滿足。非 L7 填數值可解消 |
| — | **L7 §8.2 實質審查**（L7 生效前置） | L7 規格**自己明定**「本層之充任不得僅以形式關卡為據」；L7.90(d) 列**七項必審（(i)–(vii)）**〔產生指令：`sed -n '566,600p' specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md \| grep -cE '^>\s+\((i\|ii\|iii\|iv\|v\|vi\|vii)\)'` → **7**。**第 (vii) 項＝T-L7-13，其自身即為依 `§8.1` 之書面裁決聲請**（見本表 #23），最不宜被漏數者；前版此處作「六項」，係手數，逐項審查時將漏審該項。該 L7 草案自身第 942／1004／1134 行仍作「六項」，為其內部不一致，屬 Steward 於 L7 充任案處理事項，**本 [I] 文件不得代改該規格**〕。**裁決草案已備**：`constitution/adoption-drafts/RULING-2026-008-L7-ADOPTION-DRAFT.md`（**不生效力**，待 Steward `§8.2` 實質審查）—— **裁決前務必先讀，勿另起爐灶重擬** |

**另有一項結構性事實需你決定**：**單一自然人 Steward 使「雙人類獨立核准」物理上不可能成立**（L7.42(f) 要求二憑證不得同一主體持有，而你同時持有 owner 憑證與人類權威憑證）→ 凡須「RT-4 ＋ 雙人核准」者皆不可執行，**連棘輪的推翻程序本身都無法執行**。審查官指出根本解只能靠**拓撲變更**（監督平面移至獨立實體節點）。選項：接受（記為 residual、RT-4 事實上不可用）／指定第二人／拓撲分離。

## L7 尚未修的實質洞（§8.4 級）

* **`§P4.E1` 之 Evidence 欄無不可空義務** —— L7.21(f) 只補了 Source/Identity/instance-type。**Evidence 欄為 NULL 的 Knowledge 列，引擎層不會拒絕寫入**，之後可取得權威地位、成為 Action 依據。而 §P4.E1 是 **§8.4 不可豁免核心（連履行時程都不能豁免）**。
* **L6.11 RT-1/2/3 之「無未裁決致命 Conflict」要件無載體** —— E 階面與量測面兩面俱空；依 L7.45 自訂之規則，該三列登錄**自始無效**。

## 其他未決

* **PR #2**（code repo，`remediation/aud-02-consolidated`）：**OPEN（DRAFT）**，未併 main、未 apply 生產 DB；15 測試全過（真 PostgreSQL）**係建造者自陳，本文件未獨立複現** —— **等你 P5 拍板 apply**。
  工作區為 **`/home/giga/augur/augur-code`**（前版所記 `/home/giga/augur-code-work` **不存在**）；該工作區現位於 `remediation/impl-2026-07-17`，**非** PR #2 之分支 —— 承接 PR #2 須先自 origin 取回 `remediation/aud-02-consolidated`。
* **#21 審計基準重新對齊**：code repo 已前進 —— **`origin/main` HEAD ＝ `0b04ecc`（2026-07-17 17:37）**；治權檔升版（原則精華 **v1.9.1**、系統架構大憲章 **v1.46.0**）落在 **`4951aee`**（tag `archive-20260718-alpha-p0-repair`），該 commit 為 `origin/main` 之祖先、其後尚有 **7** 個 commit。**本機 `main` ＝ `493fd73`（tag `augur-mc-v1.3-compliance-seal`），落後 `origin/main` 12 個 commit，且 `4951aee` 並非本機 `main` 之祖先。** AUD-01…26 之基準已漂移（審計錨定於 `e23a102`）。
  > **前版此處記 HEAD ＝ `4951aee`，為漂移之錨**：本文件 commit 於 17:23（`59d1eb3`），早於 `0b04ecc`（17:37）之存在，故當時不可知 —— **但這正是不該把移動中的 HEAD 寫進文件的理由**。**改錨定 tag**（如 `augur-mc-v1.3-compliance-seal` → `493fd73`、`archive-20260718-alpha-p0-repair` → `4951aee`），tag 不移動。此類 finding 反覆出現，根因即在於「HEAD 被寫下來」。
* **五份治權文件之合規聲明**補正期限 **2026-10-14**（RULING-2026-002 主文二）。
* 階段 3（production apply）阻於缺 production PG 位置＋P5；階段 4（基建部署）阻於 docker 權限。

---

## 給接手 Agent 的紅線

1. **不得修改任何已生效規格**（`specs/*-SPECIFICATION.md` 無 `-draft` 者）—— 那是 §8.5／§8.6 修憲行為。它們紅是事實，屬 Steward 事項。
2. **不得自我充任**、不得宣稱任何規格已生效、不得偽造「§8.2 人類審核已通過」的記錄。充任認定與 §8.2 是 Steward（人類）之權（§8.1／§0.5／§8.6）。
3. **不得自行解釋生效層的條文** —— 遇上層不相容（如 L6.11），正解是**據實揭露 ＋ 保守預設（取較嚴者）＋ 依 §8.1 聲請裁決**。
4. **不得以 linter 綠燈為充任依據** —— 已三度實證其與實質錯誤並存。
5. **不得為了讓數字好看而放寬判準**。gate 硬化後計數上升是**正確結果**。
6. `.env` 含 `GITHUB_TOKEN`（已 gitignore）—— 勿讀取、勿輸出。gh CLI auth 已涵蓋所有操作，該 token 可考慮撤銷。
7. **每段工作完成即 commit + push**（Steward 常設指示）。動工前先 `git fetch` —— 本 repo 曾多次被平行 session 推進。

## 工具與環境

* **§8.3 linter**：`python3 -m tools.constitution_lint {compliance|audit|selftest} <檔>` —— 純 stdlib、無外部相依。**須於 repo 根目錄 `/home/giga/augur/augur-constitution` 下執行**（`-m` 以 cwd 解析 `tools` 套件；於他處執行必得 `ModuleNotFoundError: No module named 'tools'`）。見 `tools/constitution_lint/README.md`。CI 檔存在 `tools/constitution_lint/github-workflow.yml`（**未接線**；gh token 缺 `workflow` scope 無法建 `.github/workflows/`）。
* **硬體**：GIGABYTE AI TOP ATOM（NVIDIA GB10）、**ARM64/aarch64**、121GiB 統一記憶體 —— 選型務必確認 aarch64 支援。見 `infrastructure/ENVIRONMENT-SPEC.md`。
* **PostgreSQL**：無 sudo／docker，用 micromamba + conda-forge `postgresql=16` 起 userspace PG 於 `127.0.0.1:55432`。
* **踩過的雷**：`psycopg2.extras.Json` **沒有** `default` 參數 → 須 `Json(x, dumps=lambda o: json.dumps(o, default=str))`。

## gate 現況（`tools/constitution_lint`）

已硬化並推送：**一輪 `468563c`**、**二輪 `65a7dd6`**（母集仍為 102 條，實測 `/102`）；selftest 於各該 commit 均**全通過**（含前輪六項誤標回歸鎖、B8/B9 突變鎖、對照組）。**三輪硬化**（Annex TR 二錨判準統一、零覆蓋強制發聲、複製誤標改由程式導出）之 commit 見 `git log`——**本節不寫死「現行 HEAD ＝ X」**：HEAD 會移動，寫下它的那一刻起該詞即開始腐爛（`HANDOFF.md` 自書「這正是不該把移動中的 HEAD 寫進文件的理由」，此處逐字適用；本 repo 已三度栽於此）。

> ⚠️ **「selftest N 項」不得無限定詞書寫**（前版記「55 項」，係誤數）。**本輪已根治**：項數自此由**程式**輸出，不再靠對輸出下 grep——
>
> | 計法（**權威來源＝`report`**） | 實測值 |
> |---|---|
> | **頂層測項**（`records` 中名稱非以 `└` 起首者） | **<!--lint:selftest_top_items-->47<!--/lint--> 項** |
> | **斷言總數**（全部 `chk` 呼叫數，含 `└` 子斷言） | **<!--lint:selftest_assertions-->333<!--/lint--> 項** |
>
> **右欄之值所繫之 commit 不由本表宣稱**（不寫「現行工作區」「HEAD」等相對詞——被標為「未提交、得再變動」者往往正是已提交並推送者，本輪 RULING-2026-008 草案即栽於此）：其所繫者由 `report` 輸出末尾之 **`git HEAD` 行**據實印出，工作區不乾淨時印 `<sha>+dirty`（明示該輸出無法僅由該 SHA 重現）。二值本身亦為 lint 標記綁定，與 `report` 不一致即 selftest FAIL。
>
> 產生指令：`python3 -m tools.constitution_lint report`（末段【selftest 覆蓋數】；`--json` 取 `values.selftest_top_items`／`values.selftest_assertions`）。**二值均自帶限定詞輸出**，且經 selftest 斷言「不得輸出裸『N 項』」。
>
> **前版此處記「程式本身不輸出項數，任何項數均為對其輸出所作之 grep 計數」——該敘述於本輪已不再為真，據實更正。** `selftest.run()` 回 `(ok, records)`，`records` 即項數之唯一機器來源（`report.coverage_of`）；grep 計法自此一律非權威。
>
> **前版「55」之來源已查明**：`grep -c '✓'`（未限行首）＝ 55 —— 該法**把結語行「自檢：全通過 ✓」也算成一項測試**。即 54 ＋ 1 條橫幅 ＝ 55。**一個宣告「全部測試通過」的句子被計為一個通過的測試。** 此即「以 grep 計數」之根本不可靠處，故本輪將其移除。引用時請寫「頂層 <!--lint:selftest_top_items-->47<!--/lint--> 項／斷言總數 <!--lint:selftest_assertions-->333<!--/lint--> 項」之明確形式，勿寫裸數字。

1. **`_ANNEX_TR_HEAD` 放寬為 `#{1,3}`**，區段界線改依「同級或更高級標題」而非硬編 `^## ` —— 現況隱藏了 L2 生效規格之 **<!--lint:tr_rows_L2-->59<!--/lint--> 列**矩陣（該列數自本輪起由 `report.annex_tr_rows` 導出並綁定，其錨點即取自 `compliance_lint` 之單一判準；比對筆數仍為 <!--lint:compared_L2-->4<!--/lint--> 筆）。
2. ~~**強制發聲**：Annex TR 未偵得／零表格列／代號不在標籤宇宙而未比對者，一律發 finding 並列出未受檢筆數與規格名。~~ ~~旗艦之 WM.44-LABEL 自身卻無〔發聲義務〕。~~ ✅ **部分已改**（二輪 `65a7dd6`：突變鎖 G3／G4；三輪：G6／G7）——三種情形均已發聲：Annex TR 未偵得（ONT h1）→ `❌ FAIL（error 1）`；真無 Annex TR（WM）→ `✅ PASS` ＋ INFO「**不適用**（非「已比對且通過」）」；代號脫檢（KS）→ WARNING「本次**未受檢**」。**「未受檢」≠「已比對且通過」** 之義務已落地。
   > **惟不得以「已改」掩蓋殘留**——尚未閉合者二項，接手者請勿讀為全數了結：
   > * ~~**②「標題在、表列零筆」仍零 finding 且 PASS**~~ ✅ **已閉（三輪）**：實證突變（保留 `## Annex TR` 標題、僅刪其下全部 `|` 表列）曾令 IDENTITY 由 ❌ FAIL(<!--lint:errors_L3-->0<!--/lint-->) 轉 ✅ **PASS(0)** 且零 finding——即「刪表列」比「修 <!--lint:errors_L3-->0<!--/lint--> 個標籤」省事，為現存最廉價之翻綠路徑。現改為 `checked` 為空即發 **ERROR**（零覆蓋、判定不具權威），並以 **G6 三鎖**（刪表列／改清單體例／改 HTML）鎖住。
   > * ① **代號形態不合致者仍於抽取階段靜默捨棄**（`P9.E9`、全形 `Ｐ1.E1`／`P1．E1`、空白標籤 `**P1.E1**（）` 等，實測皆為零 finding）——**尚未閉合**，見 `tools/constitution_lint/README.md`「代號脫檢之殘留缺口」。此為修 FAIL 最便宜之路（改首格代號比改標籤省事），規模大於 README 前版所述之「少數越界前綴」。
3. ~~**README 據實更正**~~ ~~**惟仍為手動維護，杜絕手抄之根本手段未落實**~~ ✅ **已落實**（本輪）：新增 `report` 子命令（全 corpus 權威數字之單一產生點，corpus 定義寫在程式）＋ **selftest 綁定斷言**——[I] 文件中以 lint 標記包住之權威數字，與 `report` 輸出**不一致即 FAIL**；`report --sync` 反向寫入。**手已拿掉**：數字不再經由人手轉錄。
4. **`§9` 正文範圍**納入 `^## Appendix`／`^### ` 為終止錨點；selftest 增突變鎖（斷言 `len(§9.text) < 1500`）。
5. 建造者自陳之七項殘餘弱點（見上）—— 其中 ①④ 與 B9 同病、⑤ 為兩檢查未接線。

---

*本文件為 [I] 交接導覽。權威悉依《Augur Meta-Constitution》及各層生效規格之 [N] 條款。*

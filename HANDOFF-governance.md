> **Monorepo 註（2026-07-22）**：應用跨機交接仍以根目錄 [`HANDOFF.md`](HANDOFF.md) 為準；本檔為原 `augur-constitution` 倉交接文件。
>
> **治權地圖（統一入口）**：[constitution/GOVERNANCE-MAP.md](constitution/GOVERNANCE-MAP.md)（案 D；[I]；docs 不上收 L0）。

# Augur 憲章 Repo — 交接文件

> **2026-07-18 快照增補（接手先讀）**：#22 結案＋L7 全綠（七份規格 gate 0 error；L7 連 warning 0）＋三鏡重審＋203 全查（30 缺陷補正）＋**移轉計畫 Phase 1 全線收官**（owner 分離生產生效、heal gate 上線、predict 隔離 refresh、restic 異碟備份鏈）。詳：`audits/L7-REREVIEW-2026-07-18.md`、`ops/phase1/`（執行記錄＋#19 卷宗）、`CODE-MIGRATION-PLAN.md`。**待 Steward**：L7 充任（§8.2＋三小件）、計畫書採認＋五決策點、備份第二目的地、gate 三輪硬化包。


* **快照日**：2026-07-17（**狀態層機械軌更正：2026-07-30**——見下方各處「2026-07-30 機械軌」註；散文與診斷仍為 07-17 原文）
* **性質**：[I] 資訊性（不創設義務；權威悉依憲章與各層生效規格之 [N] 條款）
* **給誰**：接手本 repo 的人或 Agent

> 🔴 **接手者第一件事（2026-07-30 機械軌，最省時間之三行）**：
> 1. 上方「2026-07-18 快照增補」之 **待 Steward 四項清單已全部處置**（**照該行取件即重跑已完成之裁決**）：①「L7 充任（§8.2＋三小件）」→ **RULING-2026-011**（2026-07-18 形式充任）＋ **RULING-2026-025**（2026-07-19 §8.2 條件通過）；②「計畫書採認＋五決策點」→ **RULING-2026-012**（AL-2026-015，五點逐點處置）；③「備份第二目的地」→ 同 **RULING-2026-012 主文三 裁示「取消」核定程序**，殘餘風險經 Steward 知悉並接受、登錄 ENVIRONMENT-SPEC §六——**該裁決明文「此為風險接受之決策、非缺口之消滅，後任不得引為『缺口不存在』之依據」**；④「gate 三輪硬化包」→ RULING-2026-012 主文二(e) 記為**另案、不阻 CI 接線**（CI 接線即日解鎖）。
> 2. 本檔下文之 **「等 Steward 裁決的三件事」三件已全部結清**、**「L7 尚未修的實質洞」二洞已補立**、**「L2 的 PASS 是假的」已閉**——各節已就地標註處置與依據。
> 3. **硬體段之 GB10 基線已作廢**（hugo 2026-07-25 宣告、2026-07-27 再確認、2026-07-30 重申該機不存在）；現行為 `PC002-S1800`（當家、CPU-only）＋ `DESKTOP-8MQPFS8`（GTX 1650 4GB）**雙機並行**，見「工具與環境」。
>
> **未變之處**：本檔之方法論教訓（永不採信建造者自陳／凡數字必附產生指令／突變測試才是關卡）與「給接手 Agent 的紅線」**全數仍然有效**，且其效力不因上開狀態轉綠而稍減。

---

## 一句話現況

> ⚠ **現況更新（2026-07-30 機械軌：依 `constitution/RULING-2026-011-L7-ADOPTION.md`／`RULING-2026-025-L7-8.2-DISPOSITION.md`／`RULING-2026-029-L5-8.2-DISPOSITION.md`／`LAYER-SEALING-SCHEDULE.md`；上位＝AUGUR-MC v1.6）——下段黑體句為 2026-07-17 之史述，勿讀為現況。**
>
> * **L0–L7 全數生效。** L7 ＝ `specs/INFRASTRUCTURE-SPECIFICATION.md`（AUGUR-L7 v1.0）：2026-07-18 由 **RULING-2026-011**（登錄 AL-2026-014）**形式關卡充任**（地位 provisional、`§8.2` 誠實保留）；`§8.2` 深度實質審查已於 2026-07-19 由 **RULING-2026-025**（AL-2026-028）**作成**——**條件通過、provisional 轉 v1.0**，附條件＝residual **(iii)(iv)(vi)** 分階段 ①→②→③、復審期限 **2026-10-14**。`specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md` 自此為歸檔本（不受 gate corpus 檢）。
> * **8/8 形式封印齊備，且 `§8.2` 全結**（L5 由 **RULING-2026-029**／AL-2026-032 條件通過、L7 由 RULING-2026-025 條件通過——二層皆**附條件**、復審同為 2026-10-14；餘六層已結）。見 `LAYER-SEALING-SCHEDULE.md`「8/8 封印複驗紀錄」——該處明載「8/8 ＝ G5 形式封印齊備 ≠ `§8.2` 一致結清」之原始不對稱及其解消，引用時勿只取「8/8」三字。
> * **M2（全棧貫通）**：其宣告權屬 Steward（`§8.1`／`§0.5`）；RULING-2026-011 **主文四**已載「本裁決生效即達 M2」，並同時記明 L7 之 provisional 地位與 `§8.2` 列管為 **M2 之已揭露殘餘**。**本 [I] 檔不代宣告、亦不代撤銷**，僅據實指向該裁決。
> * ⚠ **2026-10-14 併結項不因本次更新假關**：RULING-2026-025 residual (iii)(iv)(vi)、RULING-2026-029（L5 §8.2 之 (v)(viii) 條件）、RULING-2026-039（L0–L7 residual omnibus）所列日曆項一律仍為 **open**。

**〔史述，2026-07-17 快照；現況見上方更新〕L0–L6 已生效、L7 草擬完成但充任受阻。M2（全棧貫通）未達成 —— 且這是正確的**：本輪造出的機器 gate 證明，先前六層賴以充任的「形式關卡全綠」有假陽性成分 —— 四份**已生效**規格（L3/L4/L5/L6）共有 **<!--lint:l3_l6_errors-->0<!--/lint--> 個誤標**——其中**憲章（MC）側 <!--lint:l3_l6_mc-->0<!--/lint-->、上層規格側 <!--lint:l3_l6_upper-->0<!--/lint-->**（舊值 93 係前一版 gate 之低估，且曾誤將 MC＋上層合計冠以「憲章」）。第五份（L2）之 **<!--lint:tr_rows_L2-->59<!--/lint--> 列**矩陣（Annex TR）**從未被讀過**卻以 ✅ PASS 發布（gate 對該檔之比對筆數為 <!--lint:compared_L2-->4<!--/lint--> 筆——**矩陣在場、一列未讀**）。
>
> 產生指令（於 repo 根執行）：**`python3 -m tools.constitution_lint report`** —— 全 corpus 權威數字之**單一產生點**（人可讀＋JSON；`--json` 取 `values.*`）。
>
> **本文件之數字自本輪起不再手抄**：凡以 lint 標記（一對 HTML 註解，開標籤帶 key、值夾在中間）包住者，皆由該指令導出、以 `report --sync` 寫入，且 selftest 逐處比對——**與 `report` 輸出不一致即 FAIL**。改數字之唯一途徑是改程式所量到的東西，然後跑 `--sync`。
>
> 🔴 **上句對「本檔」已不成立——綁定於 monorepo 併檔時失聯（2026-07-30 機械軌實查，據實揭露）**：本檔原名 `HANDOFF.md`（原 `augur-constitution` 倉），2026-07-22 併入 monorepo 時更名為 `HANDOFF-governance.md`，而 `report` 之 `bound_docs` 清單**仍寫 `HANDOFF.md`**（該名現指應用側交接檔、實測 0 處標記）。故本檔之 `<!--lint:KEY-->…<!--/lint-->` 標記**既不受 `--sync` 寫入、亦不受 selftest 比對**——「不一致即 FAIL」在本檔為空轉，值已凍結於 2026-07-17。
> ```bash
> python3 -m tools.constitution_lint report --json | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['bound_docs']);print('HANDOFF-governance.md' in d['bound_docs'])"
> #   → [... 'HANDOFF.md', 'README.md', 'tools/constitution_lint/README.md', ...] / False
> ```
> **實查所得之現行權威值 vs 本檔凍結值**（2026-07-30，`python3 -m tools.constitution_lint report`）：`tr_rows_L2` **66**（本檔標記作 59）／`selftest_top_items` **60**（本檔作 47）／`selftest_assertions` **291**（本檔作 333）；`compared_L2` **4**（相符）；全 corpus error **0**／warning **0**、7 份生效本 PASS 7／FAIL 0。**本次機械軌不手改上開標記值**——手抄即本檔所診斷之病；修法為把本檔重新掛回 `bound_docs` 後跑 `--sync`，屬 `tools/` 程式變更，已列 escalate。**在該修法落地前，本檔任何 lint 標記內之數字一律視為 2026-07-17 凍結值，引用前請自跑 `report`。**
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



**M2 若照原計畫宣告，會是在為門面背書。**〔史述，2026-07-17；M2 其後於 2026-07-18 由 Steward 依 RULING-2026-011 主文四裁決達成，其 `§8.2` 誠實保留與 residual 均據實載明、未以形式綠燈冒充實質——見本節上方現況更新。（2026-07-30 機械軌：RULING-2026-011 主文二／主文四）〕

## 一個 monorepo（原「兩個 repo（刻意分離）」已於 2026-07-22 合併）

> ⚠ **本節已依實況重寫（2026-07-30 機械軌：實查 `git rev-parse --show-toplevel`、`ls -d /home/giga`）**。原文所載「二 repo 分離＋`/home/giga/…` 路徑」**全數失效**：`/home/giga` 已不存在（`ls -d /home/giga` → `No such file or directory`）；治權樹與程式碼樹現同居單一 repo。

| 樹 | 內容 | 位置（repo 根之相對路徑） |
|---|---|---|
| **治權樹** | 憲章、L1–L7 規格、裁決、審計、linter | `constitution/`、`specs/`、`audits/`、`tools/constitution_lint/` |
| **程式碼樹** | 程式實作 | `src/augur/`（16 package）、`scripts/`、`ops/` |

* **repo 根**：本機為 `/home/hugo/project/augur`（`git rev-parse --show-toplevel` 實測）；**路徑隨機器而定，勿寫死**（CLAUDE.md #13）。遠端＝`github.com/tsaitsangchi/augur`。
* **linter 執行**：以 `python3 -m tools.…` 呼叫者**須於 repo 根執行**（`-m` 以 cwd 解析 `tools` 套件），否則 `ModuleNotFoundError: No module named 'tools'`。實測 `python3 -m tools.constitution_lint report` 於 repo 根成功。
* `.gitignore:40` 之 `ref_augur/` 為舊參考 clone 之殘留條目，**該目錄仍不存在**，可清理。

見 [ARCHITECTURE-OVERVIEW.md](ARCHITECTURE-OVERVIEW.md)（2 層 × 8 層 對映；該檔副標所稱「× 2 repo」為 2026-07-22 合併前之描述，**2026-07-30 機械軌**：合併後讀為「治權樹 × 程式碼樹」）、[CONSTITUTIONAL-ROLLOUT-PLAN.md](CONSTITUTIONAL-ROLLOUT-PLAN.md)（九階段總綱）。

## 八層狀態

誤標數為 **2026-07-17 硬化後 gate（母集 <!--lint:mc_universe-->102<!--/lint--> 條）** 之實測值。括號內為硬化前之舊值，列出以示**計數上升是 gate 變準、非規格惡化**。

| Layer | 規格 | 狀態 | 誤標 |
|---|---|---|---|
| L0 Meta-Constitution | `constitution/META-CONSTITUTION.md` | ✅ **v1.6 生效**（2026-07-17 時為 v1.3；v1.4→v1.6 見 RULING-2026-040／AMENDMENT-LOG） | — |
| L1 World Model | `specs/WORLD-MODEL-SPECIFICATION.md` | ✅ v1.0 生效 | **<!--lint:errors_L1-->0<!--/lint-->** ✅ 唯一 PASS（無 Annex TR，INFO 不適用） |
| L2 Ontology | `specs/ONTOLOGY-SPECIFICATION.md` | ✅ v1.0 生效（G5 複驗乾淨 `a0516e88`〔**⚠ 2026-07-30 核驗 F4：本識別碼無法解析為 git commit**（`git rev-parse --verify <x>^{commit}` → fatal，4/4 皆然；`constitution/`／`audits/` 零命中，僅存於 `LAYER-SEALING-SCHEDULE.md`）——**類別未明**（疑為 run id／worktree id 而非 commit），**不得引為蓋章之證據錨**；真身待查明後補正〕、已蓋章） | ✅ **<!--lint:errors_L2-->0<!--/lint-->**（**已不再是「真值未知」**：RULING-2026-010 標題正規化＋RULING-2026-021 TR.2 補 4 群後，`report` 之 Annex TR 缺口欄現作「已讀取」；現行資料列 **66**、比對 4 筆，見上方凍結值警語） |
| L3 Identity | `specs/IDENTITY-SPECIFICATION.md` | ✅ v1.0 生效（G5 再驗乾淨 `aa7cc78e`〔**⚠ 2026-07-30 核驗 F4：本識別碼無法解析為 git commit**（`git rev-parse --verify <x>^{commit}` → fatal，4/4 皆然；`constitution/`／`audits/` 零命中，僅存於 `LAYER-SEALING-SCHEDULE.md`）——**類別未明**（疑為 run id／worktree id 而非 commit），**不得引為蓋章之證據錨**；真身待查明後補正〕、已蓋章） | ✅ **<!--lint:errors_L3-->0<!--/lint-->**（MC <!--lint:errors_mc_L3-->0<!--/lint-->／上層 <!--lint:errors_upper_L3-->0<!--/lint-->；原 20、更原 12） |
| L4 Knowledge System | `specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` | ✅ v1.0 生效（G5 再驗乾淨 `a0cda4f`〔**⚠ 2026-07-30 核驗 F4：本識別碼無法解析為 git commit**（`git rev-parse --verify <x>^{commit}` → fatal，4/4 皆然；`constitution/`／`audits/` 零命中，僅存於 `LAYER-SEALING-SCHEDULE.md`）——**類別未明**（疑為 run id／worktree id 而非 commit），**不得引為蓋章之證據錨**；真身待查明後補正〕、已蓋章） | ✅ **<!--lint:errors_L4-->0<!--/lint-->**（MC <!--lint:errors_mc_L4-->0<!--/lint-->／上層 <!--lint:errors_upper_L4-->0<!--/lint-->；原 25、更原 15） |
| L5 Cognitive Kernel | `specs/COGNITIVE-KERNEL-SPECIFICATION.md` | ✅ v1.0 生效（**§8.2 條件通過**：RULING-2026-029／AL-2026-032，2026-07-23；provisional 已解除。原載「§8.2 延後」為 2026-07-17 之狀態） | ✅ **<!--lint:errors_L5-->0<!--/lint-->**（MC <!--lint:errors_mc_L5-->0<!--/lint-->／上層 <!--lint:errors_upper_L5-->0<!--/lint-->；原 28、更原 7） |
| L6 Agent Runtime | `specs/AGENT-RUNTIME-SPECIFICATION.md` | ✅ v1.0 生效（**含 §8.2 人類審查**；G5 乾淨 `a34d411`〔**⚠ 2026-07-30 核驗 F4：本識別碼無法解析為 git commit**（`git rev-parse --verify <x>^{commit}` → fatal，4/4 皆然；`constitution/`／`audits/` 零命中，僅存於 `LAYER-SEALING-SCHEDULE.md`）——**類別未明**（疑為 run id／worktree id 而非 commit），**不得引為蓋章之證據錨**；真身待查明後補正〕、已蓋章） | ✅ **<!--lint:errors_L6-->0<!--/lint-->**（MC <!--lint:errors_mc_L6-->0<!--/lint-->／上層 <!--lint:errors_upper_L6-->0<!--/lint-->；原 20、更原 5） |
| L7 Infrastructure | `specs/INFRASTRUCTURE-SPECIFICATION.md`（`-v0.1-draft` 已歸檔、不受 corpus 檢） | ✅ **v1.0 生效**（RULING-2026-011 形式充任 2026-07-18 → RULING-2026-025 §8.2 條件通過 2026-07-19、provisional 轉 v1.0；附 residual (iii)(iv)(vi) 分階段①、復審 2026-10-14。原載「草稿，充任受阻」為 2026-07-17 之狀態） | ✅ **<!--lint:errors_L7-->0<!--/lint-->**（MC <!--lint:errors_mc_L7-->0<!--/lint-->／上層 <!--lint:errors_upper_L7-->0<!--/lint-->；原 19） |

**<!--lint:l3_l6_specs-->4<!--/lint--> 份生效規格（L3–L6）誤標合計 <!--lint:l3_l6_errors-->0<!--/lint-->**（MC 側 <!--lint:l3_l6_mc-->0<!--/lint-->／上層側 <!--lint:l3_l6_upper-->0<!--/lint-->）＋ ~~**L2 真值未知**（其 <!--lint:tr_rows_L2-->59<!--/lint--> 列矩陣因 h1 標題從未受檢）~~ ✅ **已閉（2026-07-30 機械軌：RULING-2026-010 標題正規化＋RULING-2026-021 TR.2 補列；`report` 之 Annex TR 缺口欄實測作「已讀取」）**。全 <!--lint:corpus_total-->7<!--/lint--> 份 error **<!--lint:total_errors-->0<!--/lint--> 筆**（MC 側 <!--lint:label_errors_mc-->0<!--/lint-->／上層側 <!--lint:label_errors_upper-->0<!--/lint-->／未歸類 <!--lint:label_errors_unclassified-->0<!--/lint-->——ONT 之零覆蓋 error 發生於 clause 解析之前，本無 source 可歸，**三項須並列，寫成「MC 110／上層 90」即為捏造**）；**全部皆為 WM.44-LABEL，非 LABEL error 為 <!--lint:non_label_errors-->0<!--/lint-->**。

> **計數三度上升，每次都是 gate 變準、非規格惡化**：39（初版）→ 93（一輪硬化，母集 85→102）→ **151**（二輪硬化：Annex TR 零覆蓋強制發聲、詞元去重、判準四收緊、代號脫檢發聲）。**#22 必須裁在此數之上**——前兩個數字皆為低估。〔✅ 2026-07-18 已依 151＋L2 真值（4/4）裁決並執行完畢：RULING-2026-010，六份生效本歸零全 PASS〕

> **裁決／登錄之現行簿記（2026-07-30 機械軌實查；下段之 `00{2,3,4,5,6,7,9}` 與「AL-2026-001…012」為 2026-07-17 之集合，勿據以取件）**：
> ```bash
> ls constitution/RULING-* | wc -l                                                        # → 39（RULING-2026-002 … RULING-2026-041）
> grep -oE '^## AL-2026-[0-9]+' constitution/AMENDMENT-LOG.md | sort -t- -k3 -n | tail -1  # → ## AL-2026-045
> grep -cE '^## AL-2026-' constitution/AMENDMENT-LOG.md                                    # → 45
> ```
> 即：生效裁決 **39 份**（**008 號不在其列**——L7 充任草案未生效，存 `constitution/adoption-drafts/RULING-2026-008-L7-ADOPTION-DRAFT.md`），另有 `constitution/INTERPRETATION-RULING-2026-001.md`；修訂登錄至 **AL-2026-045**（45 則）。

裁決：`constitution/RULING-2026-00{2,3,4,5,6,7,9}-*.md`（**009 ＝執行補正裁決，AL-2026-012；其附錄丙列有「呈 Steward 待決事項」，接手前必讀**——項數見該附錄，勿於此處轉抄：`sed -n '/AL-2026-012 附錄丙/,/附錄丁/p' constitution/AMENDMENT-LOG.md | grep -cE '^[0-9]+\. \*\*'`）；修訂登錄 `constitution/AMENDMENT-LOG.md`（AL-2026-001…**012**）。

> **前版此處作 `00{2,3,4,5,6,7}` 與「AL-2026-001…011」**，漏列 **RULING-2026-009／AL-2026-012**（二者於前一 commit `608adc2` 即已存在，且全檔零次提及）。本文件為本 repo 指定給接手者之**唯一入口**，接手者依此索引取件將完全看不到附錄丙之待決事項——而其中數項正是 Steward 裁決 #22 之前提。產生指令：`ls constitution/RULING-*`、`grep -n '^## AL-' constitution/AMENDMENT-LOG.md | tail -1`。

---

## 本輪最重要的發現（接手者務必先讀）

### 1. 形式關卡（linter）曾連續三輪綠燈而實質錯誤並存

L7 草稿三輪對抗審查全數 **go=false**（阻斷 7 → 8 → 9），而 `tools/constitution_lint` **三輪都 error 0**。實證病灶：

* **F4 被標為「Automation First」**（真值 = Knowledge Without Identity）、**F5「Answer First」**（真值 = Intelligence Without Evidence）—— 代號對、內容全錯，骨架檢查只查「代號有沒有出現」故綠燈。
* 改對標籤後，**落點仍是幽靈引用**：F4 掛 L7.21，而 L7.21 五款無一課予欄位義務。

### 2. 病灶是跨層系統性的，不是 L7 獨有

> 📜 **【史料：2026-07-17 gate 硬化當時之診斷】＋現況（2026-07-30 機械軌）**：本節（§2）與下一節（§2b）之散文所描述之「151 誤標／59 列矩陣未受檢／真值未知／L2 之 PASS 是假的」皆為**當時狀態**，**非現況**。現況——**RULING-2026-010**（標籤歸零：ONT 標題正規化＋155 筆標籤逐字更正，六份生效本 gate 全 PASS）＋**RULING-2026-021**（L2 Annex TR 窮舉補列 TR.2 四群，`tr_rows_L2` 56→59；G5 複驗乾淨 `a0516e88`）之後：**全 corpus error 0／warning 0、7 份生效本 PASS 7／FAIL 0，L2 矩陣已受檢**（`report` 之 Annex TR 缺口欄作「已讀取」）。權威數字之**唯一產生點**＝於 repo 根跑 `python3 -m tools.constitution_lint report`；**本檔標記值已凍結、未受 `--sync`**（見「一句話現況」之 🔴 凍結值警語）。**下文之 🔴／「真值未知」字樣一律讀為史述。**
>
> **本節之方法論教訓（跨層逐字複製、手數必錯、凡數字必附產生指令）不因狀態更新而失效——那是本節真正的價值所在，故全文保留不刪。**

新增之 **WM.44-LABEL** 檢查（標籤須為憲章原文）實測七份規格：

```
L1 <!--lint:errors_L1-->0<!--/lint--> ｜ L2 <!--lint:errors_L2-->0<!--/lint-->(已受檢) ｜ L3 <!--lint:errors_L3-->0<!--/lint--> ｜ L4 <!--lint:errors_L4-->0<!--/lint--> ｜ L5 <!--lint:errors_L5-->0<!--/lint--> ｜ L6 <!--lint:errors_L6-->0<!--/lint--> ｜ L7(v1.0 生效) <!--lint:errors_L7-->0<!--/lint-->
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

### 2b. L2 的「✅ PASS」是假的 —— 被一個 markdown 井號隱藏〔**史料：2026-07-17**〕

> 📜 **【史料標記，2026-07-30 機械軌】**：本節標題之斷言（「L2 的 ✅ PASS 是假的」）為 2026-07-17 之狀態。**已閉，惟閉合之路徑與本節所預期者不同——據實記錄**：
> * **實際走的路＝改規格標題，不是放寬 gate**。`RULING-2026-010`（#22）正規化 ONT 之標題：`specs/ONTOLOGY-SPECIFICATION.md:415` **現作 `## Annex TR [I] …`（h2）**，`TR.1`／`TR.2` 降為 h3（:421／:451）——即本節「重現配方」所描述之三行 `sed`，實質上由 Steward 依 `§8.6` 正式施作於生效本（**非**由工具代改，紅線 1 未破）。查證：`grep -nE '^#{1,3} Annex TR' specs/ONTOLOGY-SPECIFICATION.md`。
> * **`_ANNEX_TR_HEAD` 至今仍限 h2、未放寬**（`tools/constitution_lint/compliance_lint.py:319` 作 `^##\s+…`；區段界線亦仍為 `_H2` ＝ `^## `，同檔 :487）。真正新增者為 **`_ANNEX_TR_HEAD_ANY`（`^#{1,6}`，:324）＋二錨判準統一（共用 `_TR_HEAD_TAIL` 之否定前瞻）**，使「**有 Annex TR 卻解析不到**」與「**根本沒有 Annex TR**」分別發聲、不再雙盲。**故本檔「gate 現況」第 1 點仍為未落地之待改項**（見該處 2026-07-30 註）。
> * `RULING-2026-021` 另窮舉補列 TR.2 四群（`tr_rows_L2` 56→59；現行 66）。結果：L2 **error 0 ✅ PASS、矩陣已受檢**（`report` 缺口欄作「已讀取」），經 G5 複驗乾淨 `a0516e88` 蓋章。
>
> **原文全文保留為史料**（其突變測試配方與「未受檢 ≠ 已比對且通過」之教訓仍有效），惟**下文一切現在式陳述（「至今未動」「仍未受實質比對」）均為當時語**，勿讀為現況。

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

`RULING-2026-004/005/006/007` **全部**以「linter PASS（error 0）」＋「缺 0 條」為生效要件。現已知條款宇宙漏了四個核心定義、標籤檢查當時不存在。~~**這是待裁事項（見下）。**~~

> ✅ **已處置（2026-07-30 機械軌）**：此一「證據基礎弱於當時所述」之連帶已由 **#22／RULING-2026-010**（標籤歸零，2026-07-18）＋**逐層 G1–G5 蓋章排程**（`LAYER-SEALING-SCHEDULE.md`）＋**RULING-2026-017/018/019/020**（MC／L1／L2–L6 之審查處置）＋**RULING-2026-030／032–037**（L1–L7 逐層 ultracode 處置；031 為附則公示廢止、不在此列）＋**RULING-2026-023**（L5 撤回→重採認）承接；八層現皆經 **G3 機械窮舉＋G4 補列＋G5 獨立複驗**方蓋章，非僅憑「linter PASS」。**下節之表已全部結清**——本行「待裁事項」勿再讀為 open。**惟本節之教訓（形式關卡不足以支撐充任）已入 RULING-2026-011 主文二（「本專案四度實證形式綠燈與實質錯誤並存」）與其 §三 程序聲明（「gate PASS 於本案僅為形式要件之一，未作為實質合憲之證據」）之明文，效力不減。**

---

## 原「等 Steward（人類）裁決的三件事」—— **三件已全部結清**：處置索引＋現行殘餘

> 🔴 **本表已於 2026-07-30 機械軌更正（依 `constitution/RULING-2026-024-T-L7-13.md`／`RULING-2026-025-L7-8.2-DISPOSITION.md`／`AMENDMENT-LOG.md` AL-2026-027／028 實查）**：原標題與第二、三列將 **#23** 與 **L7 §8.2** 列為「待裁」，而二者早於 **2026-07-19** 即已作成。**接手者若照原表取件，將重跑兩件已完成之裁決，並誤判 L7 仍受阻。** 本表改為**處置索引**：取件請直讀對應 RULING，勿重擬。

| # | 事項 | 現況（2026-07-30 實查） | 依據／殘餘 |
|---|---|---|---|
| **#22** | ONT 標題正規化＋標籤逐字更正 | ✅ **已結案（2026-07-18，RULING-2026-010／AL-2026-013）**：155 筆標籤逐字更正，**六份生效本 gate 全 PASS（error 0）**、落點零變更、旗標零 | 更正非豁免（§0.6(a) 原文權威＋§8.6 patch，先例 2026-009）；原記「殘餘＝L7 draft 48 筆」——L7 已於 2026-07-18 由 draft 轉 v1.0 生效本並 gate 雙零（error 0／warning 0），該 draft 現為歸檔本、不受 corpus 檢；CI merge-gate 接線依 RULING-2026-012 主文二(e) |
| **#23** | **L6.11 RT-2/RT-3 序異常**（§8.1 書面裁決） | ✅ **已裁（2026-07-19，RULING-2026-024／AL-2026-027）**：RT-2／RT-3 為**不同要件軸**（E 階／可重現驗證／獨立 Data Evidence 各自獨立），**不於 CL.0 單一線性序比較**；RT-2 之放行＝E 階門檻 **∩** 可重現驗證（**取交集為 L6.11 之忠實承接**，續 RULING-2026-011 主文三(a)）。**致命 Conflict 分級判準登錄前，保守預設「一切未裁決 Conflict 推定致命」維持** | 不改任一 [N] 本文（釐定併用解釋）；L7 之 T-L7-13 三處狀態標記已更新為「§8.1 已裁」。**殘餘＝致命 Conflict 分級判準本身尚未登錄**（另案，Steward） |
| — | **L7 §8.2 實質審查**（原「L7 生效前置」） | ✅ **條件通過（2026-07-19，RULING-2026-025／AL-2026-028）**：七項必審逐項裁定——**(i)(ii)(v) 核定照收**（L7.41 H_max／L7.45 Threshold Registry／L7.5 反自我交易）；**(iii)(iv)(vi) 接受為 residual**、分階段 **①→②→③** 補正；**(vii) §8.1 已裁**（RULING-2026-024）。**L7 自 provisional 轉 v1.0 生效**；`§8.2` 深度審查**自此作成（非續延）** | 附條件＝residual (iii)(iv)(vi) 之②③補正清單＋**復審期限 2026-10-14**（與 L5 同日併結，RULING-2026-039 再確認）。⚠ **禁假關**：本列之「條件通過」不得讀為 2026-10-14 日曆項已關 |

> **原表所引之 L7.90(d) 七項必審計數（`(i)`–`(vii)`）與其產生指令保留為史料**（該指令指向 `specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md`，該檔現為**歸檔本**；生效本為 `specs/INFRASTRUCTURE-SPECIFICATION.md`，行號已不同——**勿沿用寫死行號**）：`sed -n '566,600p' specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md | grep -cE '^>\s+\((i|ii|iii|iv|v|vi|vii)\)'` → **7**。**第 (vii) 項＝T-L7-13，其自身即為依 `§8.1` 之書面裁決聲請**（見本表 #23）；前版此處作「六項」，係手數，逐項審查時將漏審該項。該草案自身第 942／1004／1134 行仍作〔2026-07-30 複驗：**已改**，`grep -c 六項` 兩檔皆 0；本句已為假、保留作史料〕「六項」，屬其內部不一致，**本 [I] 文件不得代改該規格**。
>
> **`constitution/adoption-drafts/RULING-2026-008-L7-ADOPTION-DRAFT.md` 已被實際裁決取代**：L7 充任之生效文書為 **RULING-2026-011**（形式充任）＋ **RULING-2026-025**（§8.2 條件通過）；008 號**未生效、留為草案史料**（其 §五復審條件即 RULING-2026-011 §一之要件檢核對照表）。取件請以 011／025 為準。

**另有一項結構性事實需你決定**：**單一自然人 Steward 使「雙人類獨立核准」物理上不可能成立**（L7.42(f) 要求二憑證不得同一主體持有，而你同時持有 owner 憑證與人類權威憑證）→ 凡須「RT-4 ＋ 雙人核准」者皆不可執行，**連棘輪的推翻程序本身都無法執行**。審查官指出根本解只能靠**拓撲變更**（監督平面移至獨立實體節點）。選項：接受（記為 residual、RT-4 事實上不可用）／指定第二人／拓撲分離。

> ✅ **已決（2026-07-30 機械軌：RULING-2026-025 §一 (iv)＋§二）**：Steward 已於 2026-07-19 就此裁定——**三選項併採，分階段**：**①（現行，即接受）** 記為 residual，RT-4／棘輪推翻標「**單人期間事實受限**」；**②（有第二人即行）** 升格治理附則「繼任人恆存」之預先指定人為 (iv) 之核准第二人，取回 RT-4 之獨立制衡；**③（終態）** 監督／核准平面移至獨立實體節點，一併結清 (iii) kill-switch 實體獨立性與 (vi) 單機熱備援。**復審期限 2026-10-14。上段「需你決定」勿再讀為待決；②③ 之補正本身仍為 open。**

## 原「L7 尚未修的實質洞（§8.4 級）」—— **二洞皆已於 L7 v1.0 生效本補立**（2026-07-30 機械軌實查）

> 🔴 **本節二列於 2026-07-17 為真，於 L7 v1.0 生效本已不再為真**（`specs/INFRASTRUCTURE-SPECIFICATION.md`；查證指令附各列）。**接手者勿再依本節去「補」已補之條款。** 原文保留於下，供對照補立前後之落差。

* ~~**`§P4.E1` 之 Evidence 欄無不可空義務** —— L7.21(f) 只補了 Source/Identity/instance-type。**Evidence 欄為 NULL 的 Knowledge 列，引擎層不會拒絕寫入**，之後可取得權威地位、成為 Action 依據。而 §P4.E1 是 **§8.4 不可豁免核心（連履行時程都不能豁免）**。~~
  ✅ **已補立（2026-07-18，三鏡重審之完備性批評官指認後於 L7.21(f)(i) 補立；查證：`grep -n 'Evidence 欄必須為至 Evidence 儲存之可機器解析引用' specs/INFRASTRUCTURE-SPECIFICATION.md` → 命中 L7.21(f)(i)）**：現文明定「**Source 欄、Identity 欄與 Evidence 欄為 schema 之不可空（NOT NULL）欄位**」，並載其補正說明。五元組五欄落地自此俱全——Timestamp＝L7.20(a)、Source／Identity／Evidence＝L7.21(f)；**Confidence 刻意不課 NOT NULL**（其缺位語義由 `AUGUR-KS v1.1` KS.38「無 Confidence 推定 INSUF」之保守推定承接，課 NOT NULL 反使該保守推定無從表達）。
* ~~**L6.11 RT-1/2/3 之「無未裁決致命 Conflict」要件無載體** —— E 階面與量測面兩面俱空；依 L7.45 自訂之規則，該三列登錄**自始無效**。~~
  ✅ **已補立（2026-07-18 於 L7.45(f-4) 補立全級綁定＋保守預設；`§8.1` 解釋另由 RULING-2026-024 於 2026-07-19 作成。查證：`grep -c '一切未裁決 Conflict 推定致命' specs/INFRASTRUCTURE-SPECIFICATION.md` → ≥1，落點 L7.45(f-4)）**：現文將該綁定及於 **RT-1 以上全部級別**（原僅綁 RT-4），並定「『致命』分級判準經 Steward 依 `§8.1` 核可並登錄前，**一切未裁決 Conflict 推定致命**」之保守預設。**殘餘＝致命 Conflict 分級判準本身尚未登錄**（屬 Layer 6 語義，另案 Steward；見上表 #23 殘餘欄）。

## 其他未決

* **PR #2**（code repo，`remediation/aud-02-consolidated`）：**OPEN（DRAFT）**，未併 main、未 apply 生產 DB；15 測試全過（真 PostgreSQL）**係建造者自陳，本文件未獨立複現** —— **等你 P5 拍板 apply**。
  ~~工作區為 **`/home/giga/augur/augur-code`**（前版所記 `/home/giga/augur-code-work` **不存在**）~~ ⚠ **路徑已失效（2026-07-30 機械軌：`ls -d /home/giga` → `No such file or directory`）**——`/home/giga/*` 全樹不存在；monorepo 合併後程式碼樹即在本 repo 內（本機根＝`/home/hugo/project/augur`，路徑隨機器而定）。「code repo 為另一 repo」之前提亦已不成立。該工作區當時位於 `remediation/impl-2026-07-17`，**非** PR #2 之分支 —— 承接 PR #2 須先自 origin 取回 `remediation/aud-02-consolidated`（**分支與 PR 之現況本次未查，請自跑 `gh pr view 2` 與 `git branch -r` 確認，勿採信本行之 2026-07-17 狀態**）。
* **#21 審計基準重新對齊**：code repo 已前進 —— **`origin/main` HEAD ＝ `0b04ecc`（2026-07-17 17:37）**；治權檔升版（原則精華 **v1.9.1**、系統架構大憲章 **v1.46.0**）落在 **`4951aee`**（tag `archive-20260718-alpha-p0-repair`），該 commit 為 `origin/main` 之祖先、其後尚有 **7** 個 commit。**本機 `main` ＝ `493fd73`（tag `augur-mc-v1.3-compliance-seal`），落後 `origin/main` 12 個 commit，且 `4951aee` 並非本機 `main` 之祖先。** AUD-01…26 之基準已漂移（審計錨定於 `e23a102`）。
  > ⚠ **上行所引之治權檔版號為 2026-07-17 之史述，勿讀為現行版**（2026-07-30 機械軌：`ls docs/ | grep -E '原則精華|系統架構大憲章|系統核心思想'`、`head -1 CLAUDE.md`、`head -1 constitution/META-CONSTITUTION.md`）。**現行版**＝靈魂 `docs/系統核心思想_v1.9.0.md`／原則精華 `docs/原則精華_v1.12.0.md`／系統架構大憲章 `docs/系統架構大憲章_v1.51.0.md〔**版號小時級變動：引用前一律 `ls docs/` 現查、勿轉抄**——本行 2026-07-30 曾因轉抄而寫死已死之 v1.50.0，獨立核驗 F1 查獲〕`／`CLAUDE.md` v1.32／`constitution/GOVERNANCE-ANNEX.md` v1.1／`AUGUR-MC v1.6`。**史述之版號不改**（改之即竄改記錄）。
  >
  > **前版此處記 HEAD ＝ `4951aee`，為漂移之錨**：本文件 commit 於 17:23（`59d1eb3`），早於 `0b04ecc`（17:37）之存在，故當時不可知 —— **但這正是不該把移動中的 HEAD 寫進文件的理由**。**改錨定 tag**（如 `augur-mc-v1.3-compliance-seal` → `493fd73`、`archive-20260718-alpha-p0-repair` → `4951aee`），tag 不移動。此類 finding 反覆出現，根因即在於「HEAD 被寫下來」。
* **五份治權文件之合規聲明**（RULING-2026-002 主文二）：**P2 已履行**（2026-07-23）——存檔 `docs/compliance/CS-*.md`（§11／WM.39–45；mc-version＝v1.6）。**P3 已履行**（2026-07-23）——原則精華 **v1.10.0**／RULING-2026-041；T-PRIN-7-P4E5 **規範已閉**；AUD-02 code＝D-PRIN-2。**不**因此假關 039／025／029 等其他 **2026-10-14** 日曆項。
* 階段 3（production apply）阻於缺 production PG 位置＋P5；階段 4（基建部署）阻於 docker 權限。

---

## 給接手 Agent 的紅線

1. **不得修改任何已生效規格**（`specs/*-SPECIFICATION.md` 無 `-draft` 者）—— 那是 §8.5／§8.6 修憲行為。~~它們紅是事實，屬 Steward 事項。~~〔2026-07-30 機械軌：**「它們紅」已不再是事實**——七份生效本現 error 0／warning 0、PASS 7／FAIL 0（`python3 -m tools.constitution_lint report`）。**本禁令不因此鬆動**：規格之編輯權仍專屬 §8.5／§8.6，綠燈亦不構成 Agent 代改之依據。〕
2. **不得自我充任**、不得宣稱任何規格已生效、不得偽造「§8.2 人類審核已通過」的記錄。充任認定與 §8.2 是 Steward（人類）之權（§8.1／§0.5／§8.6）。
3. **不得自行解釋生效層的條文** —— 遇上層不相容（如 L6.11），正解是**據實揭露 ＋ 保守預設（取較嚴者）＋ 依 §8.1 聲請裁決**。
4. **不得以 linter 綠燈為充任依據** —— 已三度實證其與實質錯誤並存〔2026-07-30 機械軌：**RULING-2026-011 主文二已記為「四度實證」**，並明文「gate PASS 於本案僅為形式要件之一，未作為實質合憲之證據」（§三）；本紅線之效力隨之加強、不減〕。
5. **不得為了讓數字好看而放寬判準**。gate 硬化後計數上升是**正確結果**。
6. `.env` 含 `GITHUB_TOKEN`（已 gitignore）—— 勿讀取、勿輸出。gh CLI auth 已涵蓋所有操作，該 token 可考慮撤銷。
7. **每段工作完成即 commit + push**（Steward 常設指示）。動工前先 `git fetch` —— 本 repo 曾多次被平行 session 推進。

## 工具與環境

* **§8.3 linter**：`python3 -m tools.constitution_lint {compliance|audit|report|--selftest} <檔>` —— 純 stdlib、無外部相依。**須於 repo 根執行**（`-m` 以 cwd 解析 `tools` 套件；於他處執行必得 `ModuleNotFoundError: No module named 'tools'`）。~~repo 根目錄 `/home/giga/augur/augur-constitution`~~ ⚠ **該路徑已不存在（2026-07-30 機械軌：`ls -d /home/giga` → `No such file or directory`；`git rev-parse --show-toplevel` → 本機為 `/home/hugo/project/augur`）；路徑隨機器而定，勿寫死**（CLAUDE.md #13）。見 `tools/constitution_lint/README.md`。CI 檔存在 `tools/constitution_lint/github-workflow.yml`（**未接線**；gh token 缺 `workflow` scope 無法建 `.github/workflows/`）。
* **硬體** —— ⚠ **本項之硬體基線為已作廢之 GB10（hugo 2026-07-25 宣告、2026-07-27 再確認、2026-07-30 重申該機不存在）；本節規劃於現行載體不可照用**。原文（存為史料、不刪）：~~GIGABYTE AI TOP ATOM（NVIDIA GB10）、**ARM64/aarch64**、121GiB 統一記憶體 —— 選型務必確認 aarch64 支援。見 `infrastructure/ENVIRONMENT-SPEC.md`。~~ **現行雙機真值（二台並行使用於本專案，非接力）**：
  * **當家機 `PC002-S1800`** —— SSOT ＝ [`ops/machines/PC002-S1800.md`](ops/machines/PC002-S1800.md)。**本次親驗**（於本機實跑 `hostname`／`lscpu`／`free -h`／`nvidia-smi`／`df -h /`）：`hostname` → `PC002-S1800`；**架構 x86_64**（**非** aarch64）；**Intel(R) Core(TM) i5-10500 CPU @ 3.10GHz**（6 核／12 緒）；WSL2 記憶體 **11 GiB**（swap 69 GiB；**Windows 側實體 RAM 15.9 GiB** ← 取自該 SSOT 檔「Windows 主機（實體）」節，非本次親驗）；**`nvidia-smi: command not found` ＝ CPU-only、無獨顯**；`/` **1007G**（vhdx，可用 754G）。
  * **並行第二載體 `DESKTOP-8MQPFS8`** —— SSOT ＝ [`ops/machines/DESKTOP-8MQPFS8.md`](ops/machines/DESKTOP-8MQPFS8.md)（該機之硬體**取自該檔 2026-07-25 實測快照，非本次親驗**——我無法於本機跑該機之 `nvidia-smi`）：**AMD Ryzen 5 3600**（6 核／12 緒）、**NVIDIA GeForce GTX 1650 4GB**（compute 7.5；driver **560.94**／**CUDA runtime 12.6**；`nvcc` 12.0.140）、WSL2 記憶體 **25.4 GiB**、x86_64。
  * **紀律**：**算力上限就是這兩台**——任何「丟給 GB10 跑」之規劃路徑一律失效；**調優值不可跨機照抄**（RAM 差一倍、一台有 GPU 一台沒有）；**一台機器同時只跑一個 agent**；動手前先 `git fetch`、只做 fast-forward、分岔即停手；**DB 各機獨立、不隨 git**。`infrastructure/ENVIRONMENT-SPEC.md` 若仍載 GB10 基線，以上開二機器包為準。
* **PostgreSQL** —— ⚠ **原文所載已失效**：~~無 sudo／docker，用 micromamba + conda-forge `postgresql=16` 起 userspace PG 於 `127.0.0.1:55432`。~~ **本次親驗**：`ss -lntp | grep -E '5432|55432'` → 僅 **`LISTEN 0.0.0.0:5432`**（**無 55432**）；`psql --version` → **17.10**（Ubuntu 17.10-1.pgdg24.04+1）。即：**系統 PG 17 於 5432**，非 userspace `55432`、非 PG 16。〔**誠實界限**：server 端 `select version()` 本次未取得（`role "hugo" does not exist`——連線憑證住 `.env`）；「server 17.10 online port 5432」係取自機器包摘要，非本次親驗。〕二機皆同（見各機器包摘要）。連線參數住 `.env`（**勿讀取、勿輸出**，見紅線 6）；DB 匯入走 `bash import_database.sh`（取代 augur 庫屬破壞性、須 `--force` 明示）。
* **踩過的雷**：`psycopg2.extras.Json` **沒有** `default` 參數 → 須 `Json(x, dumps=lambda o: json.dumps(o, default=str))`。

## gate 現況（`tools/constitution_lint`）

已硬化並推送：**一輪 `468563c`**、**二輪 `65a7dd6`**（母集仍為 102 條，實測 `/102`）；selftest 於各該 commit 均**全通過**（含前輪六項誤標回歸鎖、B8/B9 突變鎖、對照組）。**三輪硬化**（Annex TR 二錨判準統一、零覆蓋強制發聲、複製誤標改由程式導出）之 commit 見 `git log`——**本節不寫死「現行 HEAD ＝ X」**：HEAD 會移動，寫下它的那一刻起該詞即開始腐爛（**本檔**自書「這正是不該把移動中的 HEAD 寫進文件的理由」，此處逐字適用；本 repo 已三度栽於此）〔2026-07-30 機械軌：原文作「`HANDOFF.md` 自書」，係本檔 2026-07-22 更名前之自稱；該檔名現指**應用側**交接檔，照字面追去會找錯檔〕。

> ⚠️ **「selftest N 項」不得無限定詞書寫**（前版記「55 項」，係誤數）。**本輪已根治**：項數自此由**程式**輸出，不再靠對輸出下 grep——
>
> | 計法（**權威來源＝`report`**） | 實測值（**⚠ 本檔標記已凍結於 2026-07-17**） | 2026-07-30 實跑之現行值 |
> |---|---|---|
> | **頂層測項**（`records` 中名稱非以 `└` 起首者） | **<!--lint:selftest_top_items-->47<!--/lint--> 項** | **60 項** |
> | **斷言總數**（全部 `chk` 呼叫數，含 `└` 子斷言） | **<!--lint:selftest_assertions-->333<!--/lint--> 項** | **291 項** |
>
> 🔴 **左欄二值已與 `report` 脫節（2026-07-30 機械軌）**：本檔未列入 `report` 之 `bound_docs`（更名後失聯，見「一句話現況」之凍結值警語），故「不一致即 selftest FAIL」在本檔**為空轉**——正是本表所欲防之病，於本表自身復發。**右欄為本次實跑 `python3 -m tools.constitution_lint report`【selftest 覆蓋數】段所得；引用請用右欄或自跑，勿引左欄。** 左欄不手改（手抄即病本身）。
>
> **右欄之值所繫之 commit 不由本表宣稱**（不寫「現行工作區」「HEAD」等相對詞——被標為「未提交、得再變動」者往往正是已提交並推送者，本輪 RULING-2026-008 草案即栽於此）：其所繫者由 `report` 輸出末尾之 **`git HEAD` 行**據實印出，工作區不乾淨時印 `<sha>+dirty`（明示該輸出無法僅由該 SHA 重現）。二值本身亦為 lint 標記綁定，與 `report` 不一致即 selftest FAIL。
>
> 產生指令：`python3 -m tools.constitution_lint report`（末段【selftest 覆蓋數】；`--json` 取 `values.selftest_top_items`／`values.selftest_assertions`）。**二值均自帶限定詞輸出**，且經 selftest 斷言「不得輸出裸『N 項』」。
>
> **前版此處記「程式本身不輸出項數，任何項數均為對其輸出所作之 grep 計數」——該敘述於本輪已不再為真，據實更正。** `selftest.run()` 回 `(ok, records)`，`records` 即項數之唯一機器來源（`report.coverage_of`）；grep 計法自此一律非權威。
>
> **前版「55」之來源已查明**：`grep -c '✓'`（未限行首）＝ 55 —— 該法**把結語行「自檢：全通過 ✓」也算成一項測試**。即 54 ＋ 1 條橫幅 ＝ 55。**一個宣告「全部測試通過」的句子被計為一個通過的測試。** 此即「以 grep 計數」之根本不可靠處，故本輪將其移除。引用時請寫「頂層 <!--lint:selftest_top_items-->47<!--/lint--> 項／斷言總數 <!--lint:selftest_assertions-->333<!--/lint--> 項」之明確形式，勿寫裸數字。

1. **`_ANNEX_TR_HEAD` 放寬為 `#{1,3}`**，區段界線改依「同級或更高級標題」而非硬編 `^## ` —— 現況隱藏了 L2 生效規格之 **<!--lint:tr_rows_L2-->59<!--/lint--> 列**矩陣（該列數自本輪起由 `report.annex_tr_rows` 導出並綁定，其錨點即取自 `compliance_lint` 之單一判準；比對筆數仍為 <!--lint:compared_L2-->4<!--/lint--> 筆）。
   > ⏳ **仍為待改項、尚未落地（2026-07-30 機械軌實查，勿誤讀為已改）**：`tools/constitution_lint/compliance_lint.py:319` 之 `_ANNEX_TR_HEAD` **仍作 `^##\s+…`（限 h2）**，區段界線 :487 **仍用 `_H2` ＝ `^## `**——本項二句皆未實作。**其動機（L2 矩陣被隱藏）已由另一條路解除**：ONT 之標題經 RULING-2026-010 依 `§8.6` 正規化為 h2（`:415`），TR.1／TR.2 降 h3；另新增 `_ANNEX_TR_HEAD_ANY`（`^#{1,6}`，:324）＋二錨判準統一，使「有 Annex TR 卻解析不到」fail-loud。**故本項現為「防禦縱深」性質之強化（若日後某規格再用 h1／h3 附錄，仍會回落到區段空集＋依賴 ANY 錨發聲），非阻斷項。** 查證：`grep -n '_ANNEX_TR_HEAD\s*=\|_H2\s*=\|_ANNEX_TR_HEAD_ANY\s*=' tools/constitution_lint/compliance_lint.py`。
2. ~~**強制發聲**：Annex TR 未偵得／零表格列／代號不在標籤宇宙而未比對者，一律發 finding 並列出未受檢筆數與規格名。~~ ~~旗艦之 WM.44-LABEL 自身卻無〔發聲義務〕。~~ ✅ **部分已改**（二輪 `65a7dd6`：突變鎖 G3／G4；三輪：G6／G7）——三種情形均已發聲：Annex TR 未偵得（ONT h1）→ `❌ FAIL（error 1）`；真無 Annex TR（WM）→ `✅ PASS` ＋ INFO「**不適用**（非「已比對且通過」）」；代號脫檢（KS）→ WARNING「本次**未受檢**」。**「未受檢」≠「已比對且通過」** 之義務已落地。
   > **惟不得以「已改」掩蓋殘留**——尚未閉合者二項，接手者請勿讀為全數了結：
   > * ~~**②「標題在、表列零筆」仍零 finding 且 PASS**~~ ✅ **已閉（三輪）**：實證突變（保留 `## Annex TR` 標題、僅刪其下全部 `|` 表列）曾令 IDENTITY 由 ❌ FAIL(<!--lint:errors_L3-->0<!--/lint-->) 轉 ✅ **PASS(0)** 且零 finding——即「刪表列」比「修 <!--lint:errors_L3-->0<!--/lint--> 個標籤」省事，為現存最廉價之翻綠路徑。現改為 `checked` 為空即發 **ERROR**（零覆蓋、判定不具權威），並以 **G6 三鎖**（刪表列／改清單體例／改 HTML）鎖住。
   > * ① **代號形態不合致者仍於抽取階段靜默捨棄**（`P9.E9`、全形 `Ｐ1.E1`／`P1．E1`、空白標籤 `**P1.E1**（）` 等，實測皆為零 finding）——**尚未閉合**，見 `tools/constitution_lint/README.md`「代號脫檢之殘留缺口」。此為修 FAIL 最便宜之路（改首格代號比改標籤省事），規模大於 README 前版所述之「少數越界前綴」。
3. ~~**README 據實更正**~~ ~~**惟仍為手動維護，杜絕手抄之根本手段未落實**~~ ✅ **已落實**（本輪）：新增 `report` 子命令（全 corpus 權威數字之單一產生點，corpus 定義寫在程式）＋ **selftest 綁定斷言**——[I] 文件中以 lint 標記包住之權威數字，與 `report` 輸出**不一致即 FAIL**；`report --sync` 反向寫入。**手已拿掉**：數字不再經由人手轉錄。
   > 🔴 **惟該綁定對「本檔」已失效（2026-07-30 機械軌實查）**：`report` 之 `bound_docs` 仍列舊檔名 `HANDOFF.md`，本檔 2026-07-22 更名為 `HANDOFF-governance.md` 後即脫離綁定與 selftest 比對——**「不一致即 FAIL」在本檔為空轉，本檔 65 處標記全為 2026-07-17 凍結值**。`report` 自身之【[I] 文件綁定普查】已明載已知邊界「攔不住把標記整個刪掉」，惟**「檔案改名」是同族之第三條逃逸口、該普查未涵蓋**（普查只列 `bound_docs` 內之檔，改名者連列都不會出現，`HANDOFF.md` 一列現顯示「0 處 ← 無標記」而無人會知那是換了檔）。查證見「一句話現況」之凍結值警語；修法屬 `tools/` 程式變更，已列 escalate。
4. **`§9` 正文範圍**納入 `^## Appendix`／`^### ` 為終止錨點；selftest 增突變鎖（斷言 `len(§9.text) < 1500`）。
5. 建造者自陳之七項殘餘弱點（見上）—— 其中 ①④ 與 B9 同病、⑤ 為兩檢查未接線。

---

*本文件為 [I] 交接導覽。權威悉依《Augur Meta-Constitution》及各層生效規格之 [N] 條款。*

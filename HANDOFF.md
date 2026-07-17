# Augur 憲章 Repo — 交接文件

* **快照日**：2026-07-17
* **性質**：[I] 資訊性（不創設義務；權威悉依憲章與各層生效規格之 [N] 條款）
* **給誰**：接手本 repo 的人或 Agent

---

## 一句話現況

**L0–L6 已生效、L7 草擬完成但充任受阻。M2（全棧貫通）未達成 —— 且這是正確的**：本輪造出的機器 gate 證明，先前六層賴以充任的「形式關卡全綠」有假陽性成分 —— 四份**已生效**規格共有 **93 個憲章誤標**，第五份（L2）之 136 列矩陣**從未被讀過**卻以 ✅ PASS 發布。

**M2 若照原計畫宣告，會是在為門面背書。**

## 兩個 repo（刻意分離）

| repo | 內容 | 位置 |
|---|---|---|
| **augur-constitution**（私有） | 本 repo。治權：憲章、L1–L7 規格、裁決、審計、linter | `/home/giga/augur` |
| **augur**（公開） | 程式碼實作 | `github.com/tsaitsangchi/augur`；本機參考 clone 在 `ref_augur/augur`（**已 gitignore**，勿提交） |

見 [ARCHITECTURE-OVERVIEW.md](ARCHITECTURE-OVERVIEW.md)（2 層 × 8 層 × 2 repo 對映）、[CONSTITUTIONAL-ROLLOUT-PLAN.md](CONSTITUTIONAL-ROLLOUT-PLAN.md)（九階段總綱）。

## 八層狀態

誤標數為 **2026-07-17 硬化後 gate（母集 102 條）** 之實測值。括號內為硬化前之舊值，列出以示**計數上升是 gate 變準、非規格惡化**。

| Layer | 規格 | 狀態 | 誤標 |
|---|---|---|---|
| L0 Meta-Constitution | `constitution/META-CONSTITUTION.md` | ✅ **v1.3 生效** | — |
| L1 World Model | `specs/WORLD-MODEL-SPECIFICATION.md` | ✅ v1.0 生效 | 0（無 Annex TR） |
| L2 Ontology | `specs/ONTOLOGY-SPECIFICATION.md` | ✅ v1.0 生效 | ⚠️ **假 0 —— 從未受檢**（見下） |
| L3 Identity | `specs/IDENTITY-SPECIFICATION.md` | ✅ v1.0 生效 | 🔴 **20**（原 12） |
| L4 Knowledge System | `specs/KNOWLEDGE-SYSTEM-SPECIFICATION.md` | ✅ v1.0 生效 | 🔴 **25**（原 15） |
| L5 Cognitive Kernel | `specs/COGNITIVE-KERNEL-SPECIFICATION.md` | ✅ v1.0 生效（§8.2 延後） | 🔴 **28**（原 7） |
| L6 Agent Runtime | `specs/AGENT-RUNTIME-SPECIFICATION.md` | ✅ v1.0 生效（**含 §8.2 人類審查**） | 🔴 **20**（原 5） |
| L7 Infrastructure | `specs/INFRASTRUCTURE-SPECIFICATION-v0.1-draft.md` | 🔴 **草稿，充任受阻** | 🔴 **19** |

**生效規格誤標合計 93**（原以為 39）＋ L2 未計。全七份比對 641 筆、error **112 筆**（MC 側 73／上層側 39）。

裁決：`constitution/RULING-2026-00{2,3,4,5,6,7}-*.md`；修訂登錄 `constitution/AMENDMENT-LOG.md`（AL-2026-001…011）。

---

## 本輪最重要的發現（接手者務必先讀）

### 1. 形式關卡（linter）曾連續三輪綠燈而實質錯誤並存

L7 草稿三輪對抗審查全數 **go=false**（阻斷 7 → 8 → 9），而 `tools/constitution_lint` **三輪都 error 0**。實證病灶：

* **F4 被標為「Automation First」**（真值 = Knowledge Without Identity）、**F5「Answer First」**（真值 = Intelligence Without Evidence）—— 代號對、內容全錯，骨架檢查只查「代號有沒有出現」故綠燈。
* 改對標籤後，**落點仍是幽靈引用**：F4 掛 L7.21，而 L7.21 五款無一課予欄位義務。

### 2. 病灶是跨層系統性的，不是 L7 獨有

新增之 **WM.44-LABEL** 檢查（標籤須為憲章原文）實測七份規格：

```
L1 0 ｜ L2 假0 ｜ L3 20 ｜ L4 25 ｜ L5 28 ｜ L6 20 ｜ L7(draft) 19
                   └─────── 93 個誤標在已生效規格 ───────┘
```

**鐵證**：同一誤標**逐字跨層複製** —— 「§3 = 公理金字塔/演化鏈總述」在 L5/L6/L7 一模一樣（真值 = Five Immutable Principles）；「§0 = 總則章」三份；「P4.W1 來源崇拜警語」四份。**起草者引用的是彼此的轉述，不是憲章原文。** L5 甚至把 **§8.1 標為「Amendment Log／編號穩定」，而 §8.1 = Constitution Steward** —— 指向完全不同的條。

**最重之單例（L3）**：`P5.W4`／`P5.W5` **整體錯位一格** —— P5.W4 原文 = 最小權限、P5.W5 原文 = **不得降低人類監督與否決能力**，而「缺位預設最高風險」實為 P5.E2。錯位正落在 **P5.W5（§8.4 不可豁免核心）** 上。

### 2b. L2 的「✅ PASS」是假的 —— 被一個 markdown 井號隱藏

`specs/ONTOLOGY-SPECIFICATION.md:415` 有 `# Annex TR`，底下 **136 列表格**。gate 之 `_ANNEX_TR_HEAD` 寫死要 **h2**，而**十一份規格中僅 ONTOLOGY（生效版與 draft）用 h1**。故其整張矩陣**從未被讀過**，卻以「0（無 Annex TR 表格列）✅ PASS」published。實測僅正規化標題層級（表格內容一字未改）→ **PASS 轉 FAIL**，且抓到的正是跨層的 `§3` 截半名。

> **一份生效的 Layer 2 規格之違憲標籤，被一個井號字數隱藏，並以 ✅ PASS 發布。**

**同族逃逸口（皆經突變實證，皆為「靜默零檢查」）**：`if not regions: return` → 無 Annex TR 即零 finding、連 INFO 都不發（四條路徑：改標題名／移出 Annex／改散文體例／用 h1 全部 PASS）；`if clause is None: continue` → 引用未列於 front-matter `upper-specs` 之代號者**靜默略過** —— 實測 `ONT.5`（本體論隨意定義）／`ID.4`（同一性不必要）／`KS.9`（知識免證據）／`L5.1`（核心可繞過）四列**全為反義自創標籤，findings 0、PASS=True**。

### 3. gate 自己也犯了同一種病（最深的一層）

**第一版 gate**（獨立審查官以突變測試證實，**均已修復**）：README 宣稱一個**不存在的測試**；條款宇宙漏掉 §2.5 Evidence／§2.6 Knowledge／§2.7 Intelligence／§2.10 Confidence（「85 條全數涵蓋」為假陽性）；過半矩陣零檢查；子字串放行（「Confidence 單一形式化」含 `Confidence` 即綠）；WM 讀不到時靜默退回硬編碼副本。

**硬化後（`468563c`）已驗證為真**：母集 **85 → 102**（新增 §2.1–§2.11 定義十一條、§5.1–§5.6 架構角色六條）；7/7 實證誤標反跑全紅；B8 之 README 宣稱經三向突變實測站得住；B9 之五種錨點漂移全部 fail-loud。**條款宇宙完備性審查 go=true、零阻斷。**

**但第二版 gate 仍在說同一種謊**（`README:151`「MC 側 78／上層側 34」實為 **73／39**，兩位審查官以互相獨立之分類法交叉驗證、0 筆無法歸類 —— 且 78+34 亦等於 112，顯係**人工估算而非程式輸出**；`README:73`「非 MC 條款代號本檢查不轄」**實測為假**，與自己的表格及程式 docstring 三方矛盾，且方向相反地危險 —— 讀者據此會以為上層標籤未受檢而不採信 39 筆真實 error）。另 `§9` 之正文範圍**溢收全部 Appendix A–E**（6988 字元、88% 為他條文字），致三個與 §9 毫無關係的捏造標籤全數 PASS（現況衝擊為零：無規格引用 §9 且 §9 標 [I]，惟為經實證之潛伏偽陰性）。

**gate 建造者自陳之殘餘弱點（誠實且重要，接手者必讀）**：① 前段截取 **4 字元／40% 為工具自訂閾值、非憲章所定** —— 與 B9 所修之病同源（判準來源非 Layer 1），只是尚未被指名；② `_text_supported` 之 **50% 詞元率是最軟一環** —— 實測「禁插補冒充（Representation 被視為 Reality 本身）」達 56% **綠燈通過，而病灶詞逐字保留**，且 **error 訊息本身印出「命中 x/y 詞元（閾值 50%）」等同附上規避配方**；③ 區段列之聯集判定為新引入之鬆動（區段拉越長越容易命中，無跨距懲罰）；④ `upper-specs` 解析靠「AUGUR-XX 之 XX 即前綴」之**經驗規律**，失敗僅 warning → 靜默不受檢；⑤ **WM.44 覆蓋與 LABEL 未接線** —— 一條被判 LABEL error 的列，在 WM.44 眼中仍算「已覆蓋」；⑥ 字母項（`§0.6(a)`、`§8.5(b)`）**被工具自己引為依據，卻不在宇宙內**（是否屬「項次」為 §8.1 解釋問題，linter 不得自行造法 —— 保留正確，但為已知不一致）；⑦ **gate 未自我稽核**，README 其餘敘述性宣稱未逐一驗證。

**教訓（寫給下一個 Agent）**：**永遠不要採信建造者對自己成品的自陳。** 本 session 每一次重大缺陷，都是獨立對抗審查（尤其**突變測試**）抓到的，**沒有一次是自我檢查抓到的**。連「造來抓『以轉述冒充原文』的 gate」，兩版都在自己的 README 裡犯了同一種病。

### 4. 連帶：既有裁決之證據基礎弱於當時所述

`RULING-2026-004/005/006/007` **全部**以「linter PASS（error 0）」＋「缺 0 條」為生效要件。現已知條款宇宙漏了四個核心定義、標籤檢查當時不存在。**這是待裁事項（見下）。**

---

## 等 Steward（人類）裁決的三件事

| # | 事項 | 為何只能人類 |
|---|---|---|
| **#22** | **四份生效規格 93 個誤標**（＋L2 之 136 列矩陣從未受檢）：先更正？或先核發 §8.4 期限豁免？ | 改生效層是 §8.5／§8.6 修憲行為。**CI 接線為 merge-gate 前必須先裁**，否則一啟用即全紅 |
| **#23** | **L6.11 RT-2/RT-3 序異常**（§8.1 書面裁決） | 上層條文**彼此**不相容：L6.11 綁 RT-2 須「可重現驗證」（屬 KS CL.0 之 E3），而 RT-3 僅需「獨立 Data Evidence」（E2）→ 線性閉集上不可同時單調滿足。非 L7 填數值可解消 |
| — | **L7 §8.2 實質審查**（L7 生效前置） | L7 規格**自己明定**「本層之充任不得僅以形式關卡為據」；L7.90(d) 列六項必審 |

**另有一項結構性事實需你決定**：**單一自然人 Steward 使「雙人類獨立核准」物理上不可能成立**（L7.42(f) 要求二憑證不得同一主體持有，而你同時持有 owner 憑證與人類權威憑證）→ 凡須「RT-4 ＋ 雙人核准」者皆不可執行，**連棘輪的推翻程序本身都無法執行**。審查官指出根本解只能靠**拓撲變更**（監督平面移至獨立實體節點）。選項：接受（記為 residual、RT-4 事實上不可用）／指定第二人／拓撲分離。

## L7 尚未修的實質洞（§8.4 級）

* **`§P4.E1` 之 Evidence 欄無不可空義務** —— L7.21(f) 只補了 Source/Identity/instance-type。**Evidence 欄為 NULL 的 Knowledge 列，引擎層不會拒絕寫入**，之後可取得權威地位、成為 Action 依據。而 §P4.E1 是 **§8.4 不可豁免核心（連履行時程都不能豁免）**。
* **L6.11 RT-1/2/3 之「無未裁決致命 Conflict」要件無載體** —— E 階面與量測面兩面俱空；依 L7.45 自訂之規則，該三列登錄**自始無效**。

## 其他未決

* **PR #2**（code repo，`remediation/aud-02-consolidated`）：15 測試全過（真 PostgreSQL），**等你 P5 拍板 apply**。工作區 `/home/giga/augur-code-work`。
* **#21 審計基準重新對齊**：code repo 已前進（HEAD `4951aee`，原則精華 v1.9.1、系統架構大憲章 v1.46.0），AUD-01…26 之基準已漂移。
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

* **§8.3 linter**：`python3 -m tools.constitution_lint {compliance|audit|selftest} <檔>` —— 純 stdlib、無外部相依。見 `tools/constitution_lint/README.md`。CI 檔存在 `tools/constitution_lint/github-workflow.yml`（**未接線**；gh token 缺 `workflow` scope 無法建 `.github/workflows/`）。
* **硬體**：GIGABYTE AI TOP ATOM（NVIDIA GB10）、**ARM64/aarch64**、121GiB 統一記憶體 —— 選型務必確認 aarch64 支援。見 `infrastructure/ENVIRONMENT-SPEC.md`。
* **PostgreSQL**：無 sudo／docker，用 micromamba + conda-forge `postgresql=16` 起 userspace PG 於 `127.0.0.1:55432`。
* **踩過的雷**：`psycopg2.extras.Json` **沒有** `default` 參數 → 須 `Json(x, dumps=lambda o: json.dumps(o, default=str))`。

## gate 現況（`tools/constitution_lint`）

已硬化並推送（`468563c`）：母集 102 條、selftest **55 項全過**（含前輪六項誤標回歸鎖、B8/B9 突變鎖、對照組）。**仍待修**（獨立審查官 2/3 go=false、6 阻斷）：

1. **`_ANNEX_TR_HEAD` 放寬為 `#{1,3}`**，區段界線改依「同級或更高級標題」而非硬編 `^## ` —— 現況隱藏了 L2 生效規格之 136 列矩陣。
2. **強制發聲**：Annex TR 未偵得／零表格列／代號不在標籤宇宙而未比對者，一律發 finding 並列出未受檢筆數與規格名。**「未受檢」≠「已比對且通過」** —— 此即 B9 判定書所指「退得無聲」之同一病，`_check_wm40_closed_set_authority` 已為 WM.40 設發聲義務，旗艦之 WM.44-LABEL 自身卻無。
3. **README 據實更正**：`:151` → 「MC 側 73／上層側 39」（並改由程式輸出或 selftest 斷言產生，杜絕手抄）；`:73` 刪除或改為程式實際行為。
4. **`§9` 正文範圍**納入 `^## Appendix`／`^### ` 為終止錨點；selftest 增突變鎖（斷言 `len(§9.text) < 1500`）。
5. 建造者自陳之七項殘餘弱點（見上）—— 其中 ①④ 與 B9 同病、⑤ 為兩檢查未接線。

---

*本文件為 [I] 交接導覽。權威悉依《Augur Meta-Constitution》及各層生效規格之 [N] 條款。*

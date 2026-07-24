# U6 Ultracode — R6 半套 harvest／隔離／「可答·完成」不實宣稱對抗 [I]（2026-07-24）

* Steward：「**開 U6**」；輸入＝R6 S1＋S2 閉合＋計畫 `R6-E12`／`HAR-local`／`FZ-keep`＋Gap G-ISO-1／G-FT-1／G-KDO-1＋哨兵 `verify_roadmap_r6_s12.py`
* **方法**：Find→Verify→Critic→Synthesize（對齊 U3／U4／U5 鐵律）
* **硬邊界**：不改 [N]；不解凍 FinMind／FRED；**HAR-local**（不開外部知識放量）；不假關 G-KDO-1／10-14；本地 LLM／語意＝[I]
* 證據錨：`audits/ROADMAP-R6-S12-CLOSED-20260724.md` · `ROADMAP-R6-PLAN-APPROVED-20260724.md` · `reports/augur_roadmap_r6_plan_20260724.md` · `reports/augur_roadmap_r3_gap_ledger_20260724.md` · `scripts/verify_roadmap_r6_s12.py`

---

## 一、Find（攻擊面）

| 攻擊 | 假說 |
|---|---|
| A9 SKIP 幽靈完備 | 把哨兵近程綠（A9＝SKIP）讀成「可答完備／全量 R6 DONE」 |
| access_scope 假修 | `acquire_local_files` CLI＞cfg 修復未到位；他入口仍靜默公開 |
| UI「完成」＝終態 | admin 進度「✓ 完成」被讀成 TERMINAL_VOCAB `harvest_complete`／`answerable` |
| 半套庫存 | 大量 item 僅 metadata、無全文亦無 `knowledge_fulltext_status`，卻可被口語稱 harvest 完成 |
| harvest「全鏈」用語 | `harvest_knowledge` 標「全鏈」卻止於 promote |
| 隔離破口 | knowledge／advisor／philosophy 仍進預測管線；predict 可讀素養 |
| fulltext_blocked 不實 | blocked 帳＝漏做；或 TERMINAL_VOCAB 與 live CHECK 脫節 |
| 文件半套宣稱 | HANDOFF／路線圖／計畫／Gap 出現「僅 metadata＝可答」肯定句 |

---

## 二、Verify（親驗證據 → 裁決）

| ID | 標的 | 嚴重度 | 文本／形式／實務 | 裁決 |
|---|---|---|---|---|
| **F-U6-1** | A9 SKIP＝幽靈完備？ | **major（若誤讀）／現況防住** | **文本**：S12 閉合明示 A9 SKIP、≠可答完備／≠全量 R6 DONE；近程＝A1–A8＋A10。**形式**：本輪 `verify_roadmap_r6_s12.py --with-smoke --json` → `pass=true`；A1–A8／A10 **PASS**；A9 **SKIP**（永不由此腳本 PASS）。**實務**：稱「哨兵綠＝可答完備」＝門柱膨脹。 | **現況：文件／哨兵未搶跑**。裁決：**近程 R6-E12 可維持**；**可答完備／全量 R6 DONE＝禁**（須本 U6＋計畫門柱；≠全域 harvest） |
| **F-U6-2** | admin「✓ 完成」≠終態詞 | **medium** | **文本**：`serve_admin_console.py:147-148` `_DONE_MARKS=("harvest 觸發(抓入知識層",…)`；UI `✓ 完成`。**形式**：現 `acquire_topic` 終行＝`完成:…(抓入知識層…)`——**不含**字面 `harvest 觸發(`（本輪字串對照＝NO_MARK）。done 多靠 **pid 已歿**（含崩潰中途）。**實務**：程序結束／崩潰皆可標「完成」≠ TERMINAL `harvest_complete`／`answerable`。 | **成立（詞彙／哨兵漂移）**；**不**升 G-FT-1 conflict。處置＝帳本 **G-HAR-1**＋建議改 UI 文案／對齊 sentinel（另案最小修） |
| **F-U6-3** | 庫存半套（metadata pending） | **medium（存量）** | **文本**：TERMINAL 禁「僅 metadata 稱完成」。**形式**：live 唯讀——`knowledge_item` **254176**；有全文 item **145869**；`knowledge_fulltext_status` **18885**；**既無全文亦無終態帳** **91933**（其中 DOI 形約 **75373**＝可抓未終態，非 blocked）。**實務**：HAR-local 下未清外部 backlog＝預期；若稱「系統 harvest 已完成／可答」＝假兆。 | **成立（庫存事實）**；R6／路線圖**未**如此宣稱。入 **G-HAR-1 partial**；清債＝HAR-ext／`refresh` 另授權 |
| **F-U6-4** | `harvest_knowledge`「全鏈」用語 | **low–medium** | **文本**：docstring「acquire→staging→promote **全鏈**落地」。**形式**：實作輪末僅 `promote`；全文／切句／embed 在 `acquire_topic`（預設 `--complete`）／`refresh_knowledge_pipeline`。**實務**：把「跑完 harvest_knowledge」當 #29b 終態＝半套。 | **成立（用語陷阱）**；引擎分層可辯；建議 docstring 消歧（執行層另案） |
| **F-U6-5** | `acquire_local_files` access_scope | **pass（已修）** | **文本**：R6 閉合稱 CLI 明示優先。**形式**：`acquire_local_files.py:120-122` CLI＞cfg＞`local_private`；owned_local≠private→exit；煙測 `--access-scope local_private`。**實務**：live `owned_local` 非 private＝**0**；`chk_itext_owned_local_private` 在（哨兵 A1）。 | **已修復路徑**；非新 finding |
| **F-U6-6** | 他入口 scope 對稱 | **low（殘留）** | **文本**：遠端通道亦 owned_local⇒private。**形式**：`acquire_remote_files.py:85` **僅** `cfg.get("access_scope","local_private")`——無 CLI 覆寫對稱；admission 仍擋 owned_local≠private。**實務**：錯 cfg public＋CC 會公開（意圖軸）；錯 cfg public＋owned_local＝admission／CHECK 擋。 | **殘留知情**；不升 conflict；對稱 CLI 另案 |
| **F-U6-7** | 隔離破口 | **pass** | **文本**：G-ISO-1 none。**形式**：`pytest tests/test_philosophy_isolation.py` → **9 passed**（本輪）；哨兵 A4／A5：app≠predict、predict 對素養 SELECT denied 3/3；A6 e2e 含 private 反向。**實務**：features／models／universe／evaluation／ingestion 靜態 import knowledge／advisor／philosophy＝0（抽樣 grep）。 | **維持 none**；動態 SQL 旁路全追蹤＝Critic 未查 |
| **F-U6-8** | TERMINAL／blocked 誠實 | **pass（對齊）** | **文本**：`TERMINAL_VOCAB` blocked＝落 `knowledge_fulltext_status`≠漏做。**形式**：表＋status CHECK 在（A2）；live 狀態⊆封閉集（skip_*／abstract_*）；無「ok＝blocked」謊言。CLAUDE 歷史名 `fulltext_blocked`＝同概念別名。 | **不成立為缺陷**；禁把「有 status 列」讀成「可答」 |
| **F-U6-9** | 文件半套肯定宣稱 | **pass** | **形式**：哨兵 A3 PASS；擴掃 reports／audits／HANDOFF——無「僅 metadata＝完成／可答」肯定句（禁令／風險列除外）。 | **現況乾淨** |
| **F-U6-10** | G-KDO-1 假關 | **pass** | A10／帳本仍 **calendar**／DEFER；本輪**未**改。 | **維持** |

**本輪親驗指令摘要**（零 FinMind／FRED；HAR-local）：

* `./venv/bin/python scripts/verify_roadmap_r6_s12.py --selftest` → 全通過
* `./venv/bin/python scripts/verify_roadmap_r6_s12.py --with-smoke --json` → `pass=true`（A9 SKIP）
* `pytest tests/test_philosophy_isolation.py` → 9 passed
* DB 唯讀計數見 F-U6-3／F-U6-5（PG `127.0.0.1:5432` accepting）

---

## 三、Critic（還沒查什麼）

* features／models 執行期**動態**組字串觸及 knowledge／chat 表的實例追蹤（AST 外）
* admin 重啟後僅靠 log／mtime 的 done 誤判矩陣（pid 丟失路徑）
* `acquire_topic --no-complete` 與 admin 放量預設 complete＝True 之 UX 教育是否足夠
* 91k pending 的 domain／source 分布與「該不該抓」治權裁決（HAR-ext 計畫域；本輪未放量）
* Qdrant／Milvus 影子索引與 `local_private` 外洩回歸（僅靜態讀 export 過濾）
* advisor live 回答是否對「僅 metadata item」謊稱有引用（需 live chat；本輪未打外部／未開 HAR-ext）
* 10-14／G-KDO-1 與 R6 交互（禁假關；未重開）

---

## 四、Synthesize（呈核）

### 結論句

R6 **近程 S1＋S2（R6-E12）**在 A1–A8＋A10 意義上**可維持閉合**——A9 本輪由 **U6 對抗檔**補齊呈核，**前提**：對外敘事嚴格＝「終態詞彙鎖＋本地暢通／隔離哨兵」，**不是**「可答完備／全域 harvest 完成／全量 R6 DONE」。

庫存 **91933** 件「無全文且無終態帳」＋ admin「✓ 完成」＝**程序結束語意** → 誤讀路徑成立，已入 **G-HAR-1 partial**；**不**回滾 G-FT-1／G-ISO-1＝none。

### gap_class 建議（本輪）

| ID | 建議 | 理由 |
|---|---|---|
| G-ISO-1 | **維持 none** | pytest 9＋哨兵 A4 再親驗 |
| G-FT-1 | **維持 none** | CHECK＋owned_leak=0＋A1 |
| G-KDO-1 | **維持 calendar** | 未假關 |
| **G-HAR-1**（新） | **partial** | admin 完成詞≠TERMINAL；庫存半套 pending 知情；HAR-local 未清債 |

### 可否「可答完備／全量 R6 DONE」？

| 語義 | 可否 |
|---|---|
| 近程 R6-E12（S1＋S2＋哨兵；A9＝U6 本檔） | **可呈核 YES**（本 U6） |
| 可答完備／全域 harvest 完成 | **NO** — F-U6-3／UI 詞彙 |
| 路線圖大標「素養／顧問半系統」產品完備 | **NO** — S3a／HAR-ext／R7 另案 |
| 解凍 FinMind／FRED | **NO** — FZ-keep |

### 建議處置（執行層、零 [N]）

1. 本檔＝U6 DONE；路線圖標 U6 DONE；Gap 最小 diff 加 **G-HAR-1**
2. 另案最小修：`_DONE_MARKS` 對齊 `acquire_topic` 終行；UI「完成」→「程序結束」（≠終態可答）
3. `harvest_knowledge` docstring 消歧「promote 段≠#29b 終態」
4. 維持 FZ-keep／HAR-local；清 91k pending＝另開 HAR-ext／refresh（**≠**市場 API 解凍）
5. `archive_push.sh --slug roadmap-u6`

# Augur 深化理解報告 r2——獨立核驗＋重開機後全面重測（2026-07-31 午）

* **用途**：Steward 指示「深化理解此專案所有檔案內容後詳細理解並記住，並做出深化理解的專案報告，
  以做為後續優化此一專案的基礎」。本報告為該指示之**第二輪**產出。
* **與基線之關係**：今晨已有 `reports/augur_deep_understanding_20260731.md`（下稱**基線**，
  08:5x 產製、42 則債務）。基線 §11 自陳「本報告本身未受獨立核驗——依 `RULING-2026-028` 第 3 點，
  施作後宜由非施作者核驗」。**本報告即該獨立核驗**：由另一 session（非施作者）以 12 路平行唯讀探查
  （workflow `wf_cdbaf172-737`，12 agent／508 次工具呼叫／0 錯誤）＋繕打者親讀治權檔全文後合成。
* **為何必須重測**：機器於 **11:09 重開機**（今日第二次），基線多項 live 錨（孤兒佔埠、load 10-24、
  兩支 30h replay）已翻頁；且 07-31 上午 07:56–10:33 之間落地了一整條治權生效鏈（sim 專章、
  靈魂 v1.10.0、憲章三連升），基線因與其平行產製而**零覆蓋**。
* **三份互補**：基線＝債務排序地圖；`augur_full_reread_facts_20260730.md`＝逐檔事實底本；
  **本報告＝核驗結論＋07-31 治權全景＋重開機後現況**。三者互引、以最新實查為準。

---

## §0 讀法

| 標記 | 意義 |
|---|---|
| **【親驗】** | 繕打者或本輪 agent 實跑指令／SQL 得到輸出（全部附取得方式） |
| **【單路】** | 單一 agent 所得、繕打者未獨立複跑 |
| **【轉述】** | 引用文件、未獨立驗證 |

**所有 live 數字取樣於 2026-07-31 11:20–11:36（重開機後）**。本專案數字以小時計腐爛
（見 §1），引用前一律重跑附註指令。

---

## §1 最重要的元發現：基線報告在 commit 之前就已過期

基線報告檔 mtime **10:42:37**、commit `20d1ec9` **10:43:55**。逐項對時【親驗】：

| 基線內容 | 現實時點 | 落差 |
|---|---|---|
| 債 #15「12 則治權死鏈 RC=1」列為 CONFIRMED high | `ceac40c`（**09:19:35**）已把死鏈全數清綠；以 `git archive` 重放兩個樹態證實 | 報告寫入時**已過期 83 分鐘** |
| 債 #31「governance_queue 無 TTY 閘」列為 CONFIRMED high | `847f65a`（**10:14:09**）已補真閘 | 已過期 28 分鐘 |
| B1「embed 0 新列根因四路皆未查明」 | `f143aa6`（**07:58**）已修好該根因，ledger 07:56/07:57 兩列 `IDEMPOTENT_REWALK` 為證 | 產製前約 1 小時已修 |
| A10「pending 池 15 分鐘掉 14,361→有人在推進」（B4） | 07,003 是 **04:01 的 log 行**、121,364 是 08:41 的 live SQL；池子實為**上升**（08:06:17 harvest 進料 14,361 件） | 方向整個抓反 |
| 對 07-31 sim 專章生效鏈 | 09:41–10:33 七 commit 一氣呵成 | **零覆蓋**（全檔 "sim" 僅 1 次且無關） |

**07-31 上午時間線**（本輪重建，全部可由 git log／DB 時戳覆算）：
`07:56-07:58` KH 批次裁決＋embed 修復（f143aa6）→ `08:06` harvest 進料 14,361 件 →
`08:39` staging 回收工具 → `08:5x` 基線四路深讀 → `09:19` 靈魂 v1.10.0＋死鏈清綠（ceac40c）→
`09:41-10:33` sim 生效鏈七 commit → `10:42` 基線報告落檔 → `11:09` 重開機 → 本輪。

**教訓（比任何單項債都值錢）**：本專案的治權與現實在同一個上午以分鐘為單位互相超車。
任何「深化理解報告」都是快照；**可信的不是報告裡的數字，是報告附的驗證指令**。
本報告自身同樣適用此折舊率。

---

## §2 系統是什麼（r2 修訂）

基線的定性（一台「把治理寫進資料庫」的誠實性機器；預測與知識庫是它的測試載荷；
機械閘分三層強度而專案用同一個詞稱呼）經本輪核驗**成立**。r2 補上兩塊基線沒有的：

**(a) 系統現在有了明文的終點**【親驗，靈魂 v1.10.0，hugo 拍板 2026-07-31 入憲】：

> **讓本地 AI 具備與人一樣的判斷力。**

且該條同時做了四件事：①界分**能力 ≠ 權威**（判斷力趨近人不移轉授權根節點，P5.W2/W5 屬 §8.4
不可豁免核心）；②明文禁止「機器分不出人與 AI」被當成「已達成」之證據（「量不出差別≠沒有差別」
——並把 pg_roles 無 hugo、getpass 代簽、人簽帳本被自測寫入三次等實查事實直接寫進條文）；
③達成須走普遍晉升路徑，六項可判定判準（分域、同題盲測、過地板、含「不知道」題、獨立複現、
後果回流）；④**本地化是要件**——達成認定不得繫於外部服務。
**後續一切優化都應對準這個終點**：優化的不是預測分數，是「判斷力可被證明」的那套機制。

**(b) 憲章在 48 小時內三連升，KH0 義務半徑倍增**【親驗】：
v1.52.0（07-30，KH0 底線：有原文必達 KH0）→ v1.53.0（07-31，**入口底線**：入 staging 者不得因
欄位缺漏判死、判死唯一合法理由＝無任何可理解內容；撤回 metadata-only 例外、分母改**全部**
`knowledge_item`——原「破口 0」係窄口徑假綠，**真實普遍破口 138,829／285,177＝48.68%**
【本輪 psql 親核同數】；46,775 筆 rejected 已溯及回收，`staging_rejection_recovery` 46,775 列）→
v1.54.0（07-31，登錄 sim 下位專章）。

---

## §3 基線 42 債逐項核驗總表

判定語彙：**維持**＝CONFIRMED 原樣；**已修**＝基線後修復（附證據）；**半修**＝主通道修、旁道開；
**惡化**＝範圍擴大；**翻頁**＝重開機自然消除（根因未修）；**翻案**＝基線該項錯。

| # | 基線債 | r2 判定 | 現況一句話 |
|---|---|---|---|
| 1 | validation_evidence 19/19 假綠 | **維持** | 12 條 check_sql 逐條重跑：E1/E2/E4_exclusion 仍 false、7 條無 check_sql；`verify_validation_evidence.py` 仍零排程 |
| 2 | 正典對帳紅、停跑 | **維持且續惡化** | 最後 passed=t 仍 2026-07-16 15:43；07-25 18:14 後零執行；**重開機亦未觸發任何補跑**（對比：tw 軸有 drain timer 自動 resume，raw 對帳無等價機制）——這是不對稱的關鍵 |
| 3 | 「AI 不得代簽」DB 層零強制 | **維持，範圍更大** | 簽核 CHECK 仍全部只驗非空；`current_user` 全庫唯一用者 kh_gate_guard 只記錄不授權；**新增**：簽核 gate 的 trigger 一律不含 INSERT 事件（`local_model_version` 可直接 INSERT `status='serving'` 零簽名晉升）；sim 新表兩條簽核 CHECK 同為非空式 |
| 4 | delete_only_guard 不擋 UPDATE | **惡化** | 覆蓋由 14 表擴至 **23 表 46 trigger**（P2 把同模式複製到 sim 八表＋mc_simulation_run），`tgtype&16` 命中 **0**＝UPDATE 100% 全裸；正解 `honesty_ledger_guard`（5 表）同庫服役 |
| 5 | TWEVO 殭屍輪卡死 | **處置中** | tw-20260728-r01 仍 running/closed_at NULL（DB 狀態不隨重開機清除），steps_json 3→17 步；drain timer（OnBootSec=10min）11:19:56 首發、pid 1696/1709 正 resume 中，結果未知。**新增**：`evolution_run` 已堆 **6 列 running 殭屍**（run_id 11-16，TimeoutExpired/SIGTERM 後從不回填 failed）——同根因在另一張表的重複體現且隨重試增生 |
| 6 | repo 層零自動觸發器 | **維持** | hooks 0／無 workflows／無 pre-commit，逐項重查零改變 |
| 7 | 零失敗通知路徑 | **維持** | 13 支 unit 全無 OnFailure=；12 條 cron 全 `>> log`；self_seek「不入鎖」註解 vs `flock -w 3600` 實作矛盾逐字仍在 |
| 8 | 知識進料在跑、出料死 | **半修＋升級** | embed 段已修（f143aa6，待 08-01 04:00 排程實證）；但 fulltext 段由「timer 壞掉」**升級為「根本沒排程」**——ATA ExecStart 明寫 `--stages sentences embed`、crontab 與全部 timer 無一涉 fetch；item_text 最後寫入停 07-30 18:00；進料端同時仍在灌（今日 +14,361，harvest 還在撞 429/timeout） |
| 9 | KH8 鑑別力閘自解＋降級零效果 | **維持且更糟** | population_discriminates ok=True（靠 0.27% 尾巴解閘）；**新增**：07-30 15:29-30 的 bulk 降級（每批 5,000 列只改 admit_depth 不改 layer_scores）**結構上不可持久**——upsert 用 `GREATEST(existing, EXCLUDED)`，下次 auto_admit 跑到即自動還原 9 |
| 10 | 孤兒舊碼佔埠 | **翻頁** | 六埠現全由 systemd 絕對路徑正版持有（STARTED=11:09:06/07、NRestarts=0、pid 與 ExecMainPID 吻合）；根因未修——再手動 `./venv` 起同 script 即複發 |
| 11 | 四條週排程零執行 | **維持** | ~/logs/ 四檔仍不存在；list-timers 確認 LAST 全空白；首跑 08-01/02/03 |
| 12 | own_stack 三門零列可評 | **維持** | `own_stack_rolling` 仍 0 列（live 鍵是 `own_daily_rolling`）、horizon_td 仍只有 5；三門仍 approved/36 |
| 13 | 驗證器層未接線 | **維持且更嚴峻** | 排程真可達的 verify_* 僅 **2/35**（verify_eval_set_validity 經 01:30 演化鏈、verify_prodset_hotpath 經 23:00 TWEVO I6）；另約 9-10 支雖有 codebase 呼叫者，但**呼叫者自身也不在任何排程**；verify_validation_evidence／verify_knowledge_admission_health 仍零真呼叫者 |
| 14 | 字面斷言/恆真式自測 | **維持＋同型再犯** | evolve_cycle.py:400-401 恆真式原封（且方向與名稱相反：斷言字面「存在」）；review_evolution_candidates.py:43 仍 `chk(...,True)`；**新增同日再犯**：`migrate_sim_evolution_ddl.py:368-369` 對八表 DDL 串接字串做子字串比對→`sim_evolution_candidate` 缺 `CHECK (is_synthetic)` 仍全綠——發生在該檔自陳「已修 or True 假綠」之後 |
| 15 | 治權 12 死鏈＋CS 落後 | **半修＋翻案** | 死鏈半邊**已修**（check_treaty_refs 現 RC=0；且基線量測本身已過期 83 分鐘）；CS 半邊**惡化**：`CS-系統架構大憲章_v1.54.0.md` 同檔**五個版號**（檔名 v1.54.0／標題 v1.53.0／spec-version v1.53.0／增量段 v1.49.0／覆蓋宣稱 v1.50.0），逐原則論證自 07-29 起跨五次升版未動 |
| 16 | lint corpus 只含 specs/ | **維持，證據強化** | report.py:51-53 逐字確認；本輪三個新破口（CS 五版號、README:30、專章不在 MAP）**全部落在 lint 射程外**——因果宣稱再獲三個樣本 |
| 17 | lint report 綠 vs selftest 紅 | **維持** | report RC=0／--selftest RC=1（唯一 FAIL 仍 G10）；引用不指明子命令即傳播錯誤結論 |
| 18 | KH 十層僅 3 層 per-item | **維持** | admit_depth 7 佔 99.7%（145,948/146,348）＝深淺分桶空集合；KH7 note 逐字寫「run_id=6 …（庫級；≠approve）」 |
| 19 | 123,304 件 INNER JOIN 不可達 | **維持** | 數字逐字重現；**新增量化**：實際可檢索 item＝145,952＝恰等於 eligible 數＝總量 51.2% |
| 20 | 149 萬哲學句嵌入零消費 | **維持** | 1,489,274 列（85.3%）；消費端普查仍零；works 走 philosophy_chunk_embedding（126,609，覆蓋 100%） |
| 21 | Qdrant ANN 漏 eligible 過濾 | **維持且升級為 live** | `sentence_items` 後端實為 `qdrant_server`（:6333 active）→ 15,921 件非 eligible **現在就可**經 ANN 進引文；fallback pgvector 有過濾→可答性隨 Qdrant 死活漂移、不亮燈 |
| 22 | retrieval :373/:408 死碼 | **部分翻案** | :408 死碼 CONFIRMED（AST 證明）；**:373 不是死碼**（cur 是 `_finalize_items_kh_first` 形參）——真病是快取不寫 `_at` 致每次檢索白掃 146k 列兩次；auto_admit docstring「已修」與殘留呼叫並存之矛盾成立 |
| 23 | 互斥機制三套不相交 | **部分改善** | holder 帳已落地（heavy_slot_holder_log，能答「誰、pid、從何時」且正確界分 orphan）＋`--slot-wait` 有界等待；**覆蓋率未解且將擴大**（sim 軸依計畫入同一 slot）；live 實證：deferred #4/#5 因「heavy slot busy」連三日推遲＝專章附二警告的當場證據 |
| 24 | ledger 類表零 trigger＋predict 可 DELETE | **維持，暴露面更大** | augur_predict 的 DELETE+UPDATE 面實為 **10 表**（基線點名 4）：data_audit_log／feature_values／judgestop_threshold／model_registry／pipeline_execution_log／prediction_values／revalidation_baseline／revalidation_ledger／revalidation_verdict／trial_ledger，其中僅 3 表有閘 |
| 25 | migrate_* 自測不查 live schema | **維持＋新例**（見 #14） | 唯 `migrate_sim_evolution_ddl.py --check` 走 live DB 查詢屬進步；--selftest 仍字面 |
| 26 | check_cmd_matrix＝字串稽核 | **維持** | 受檢 437→**440**、缺漏 0；機制不變；**新增盲區**：`__init__.py` 無條件豁免→`catalog/__init__.py` **923 行全邏輯**（含放量 build）永不受稽核、`arena/__init__.py` **0 bytes** 亦不亮燈 |
| 27 | 測試層無安全子集 | **維持** | 275 tests／26 檔／無 conftest／無 marker；arena/catalog/execution/universe 仍零測試 |
| 28 | ≥60 clusters 治權數字 live 無門在用 | **維持（數字微修）** | min_clusters 分佈實查：**250×11**（基線記 12）／36×6／NULL×12；`≥60` 仍無任何門在用；**新增**：`report_triple_evolution_week.py:39` evidence 字串寫死「cluster N/60」與凍結值不符 |
| 29 | RBAC 收窄零 live 證據 | 維持【單路，本輪未重查】 | — |
| 30 | 顧問單答 33 分鐘 | 維持【單路，本輪未重測】 | — |
| 31 | governance_queue 自動代簽 | **半修** | `_require_human_tty()`（:86）真閘、fail-closed 且先於 DB【行為級親驗：--approve rc=1、管道餵 stdin 亦拒】；gp_86c8063fc688 是唯一經新閘的簽名。**三條殘道**：(a) pty 十行可破（唯讀探針實證 `isatty()=True` 下 `_require_human_tty()` 回 'hugo'）；(b) TTY 內**按 Enter 回退 `getpass.getuser()`**——docstring 與專章 §4.4 補強1「親手打簽名」之宣稱**強於 code 實況**，且 selftest:167 反把回退鎖成通過條件；(c) DB 層 `governance_proposal_immutable` 不看 decided_by 也不看寫入者，一句 psql UPDATE 繞過整支 CLI |
| 32 | flock 靜默＋註解矛盾 | **維持** | 逐字仍在 |
| 33 | watchdog 守死標的 | **維持** | timer 每 30 分準時（11:14:56 又跑）；audit_retry.log 仍停 **07-15**（16 天） |
| 34 | GOV-1 未閉 | 維持【讀碼】 | 無新裁決 |
| 35 | 兩張零列帳本 | **維持** | local_ai_iteration_ledger／pipeline_execution_log 仍 0 列（注意：SUNSET (c) 的正確判準表是 `local_model_eval_run`，見 §8） |
| 36 | HUMAN_ONLY 空殼 | **維持** | 一字未改；同族第二空殼 `assert_human_decider()`（常數比對、預設即過）更易誤導 |
| 37 | concordance 不套 RBAC | 維持【單路】 | knowledge_concordance 已 53,247,307 列（+89k） |
| 38 | 嵌入口徑差 92 倍 | **維持** | 445 vs 40,951（比值 92.0）；與 #8 交互：以 ATA 池量判收工會留 4 萬句未嵌 |
| 39 | self_seek 無上界 | 維持【單路】 | — |
| 40 | qdrant 跨專案依賴 | **維持** | 二進位仍在 ~/project/ttai/；本次重開機 systemd 正常拉起（風險特定於換機情境） |
| 41 | knowhow-refresh timer 死 | **翻頁** | 現 active(waiting)、下次 08-02 04:30；先前為何 inactive 根因未查、可能復發 |
| 42 | 雙懸崖 | **維持** | 10-14 七項（75 天）checklist 全未勾；SUNSET 0/3（92 天）；詳 §8 |

---

## §4 本輪新發現（基線未載）

依「不修會怎樣」排序：

| N# | 發現 | 嚴重度 | 證據級 | 不修會怎樣 |
|---|---|---|---|---|
| **N1** | **sim 軸候選物理死鎖**：`simulation_method_registry` 0 列，而 `sim_evolution_candidate.method` 有 FK 指向它 ⇒ 任何 sim 候選**寫不進去**；解鎖須先註冊方法，而 `chk_smr_registered_signed` 要求人簽＋`gate_ref` 指向 governance_proposal ⇒ 20 個既有 method 的註冊路徑（一件包裹提案 or 逐件）**無文件交代**；計畫 V2.5 驗收（registry ≥20）未達，「P2 完成」的射程實為「表＋閘落地、內容零」 | high | 親驗 | 專章生效但軸永遠空轉；且「P2 完成」易被誤讀為可開跑 |
| **N2** | **KH0 普遍破口 48.68% 成為現行 [N] 義務**：v1.53.0 把分母改為全部 knowledge_item，138,829 件未達 KH0（psql 親核同數）。這不是舊債翻新——是 07-31 新入憲的義務半徑 | high | 親驗 | 「先不丟棄、再必理解、無一例外」三合一底線有一半庫未履行；本地 AI 判斷力終點（靈魂 v1.10.0）的地基就是這個 |
| **N3** | **evolution_run 殭屍累積機制**：6 列 running/finished_at NULL（run_id 11-16），timeout/SIGTERM 後從不回填；與 #5 同根因、會隨每次重試增生 | high | 親驗 | 帳本無法表達「死了」；任何以 running 數判斷活性的邏輯永遠高估 |
| **N4** | **簽核 gate 的 INSERT 路徑零人簽**：所有簽核表 trigger 不含 INSERT 事件；`local_model_version` 無 CHECK 要求 promoted_by ⇒ 直接 INSERT `status='serving'` 可零簽名晉升 | high | 親驗（單路） | 「不可回改」保護的是已存在的列；晉升本身可從旁門進 |
| **N5** | **治權入口三盲區**：①README.md:30「憲章 v1.51.0」落後三版但 check_treaty_refs 全綠（regex 錨全名 stem、不匹配縮寫「憲章」——實測驗證）；②新生效專章全 repo 僅大憲章 :216 一處引用、**GOVERNANCE-MAP 零提及**＝新治權檔不在統一入口讀序內；③`docs/原則精華_v1.12.0.md:7` 裸版號 v1.51.0（REF_RE 只認連結/反引號路徑） | medium | 親驗 | 「統一入口」與「機械稽核」雙雙漏接新法；下一個 session 從 MAP 讀不到專章 |
| **N6** | **專章自相矛盾殘留**：生效版附三仍寫「未寫入任何 DB、未建立 governance_proposal 列」，與同日 10:23:55 由 claude 建立 gp_86c8063fc688 的事實直接矛盾（提案版原文未修殘留） | medium | 親驗 | 治權檔內文與帳本互斥＝給未來讀者的假線索 |
| **N7** | **`lending_fee_rate_mean_20d` clean-room 不可重建**：prodset 僅有的 2 個 active 特徵之一、feature_values 17,072 列，**全 repo 零產生器**（chip.py 只有 `_30d` 版）；候選側 `lending_fee_vw_mean_20d` 同樣零產生器且列數相同（改名鏈不在 repo）——由「future plan gap」升格為 **#16 clean-room／#9 可溯源破口** | high | 親驗 | 生產特徵無法由治權檔＋repo 重建；換機後此特徵成為不可復原的黑箱 |
| **N8** | **`feature_candidate_values` 零 guard 且已 390,274 列**（172,109→390,274）——與全鎖的 feature_values 只差一個字 | medium | 親驗 | 候選值可被無痕改寫；四關漏斗的輸入端不設防 |
| **N9** | **heavy_slot._selftest 用生產鎖名真寫 DB**（違 #18 免 DB）；自測會與 23:00 排程互搶生產鎖 | medium | 親驗（單路） | 自測隨排程時點假紅＋自測本身干擾生產 |
| **N10** | **direction_gate 簽名帳的可區分性**：18 列裸 `hugo` vs 8 列自陳「claude 繕打,不冒充親簽」——誠實註記存在但機械層無法區分二者；`knowhow_governance_ledger` 43 列全為字面 'HUMAN'（且該欄 DEFAULT 就是 'HUMAN'）、07-31 07:56:50-52 同批 0.5 秒級寫入 | medium | 親驗 | 事後鑑識不可能；「誰簽的」永久成謎（專章 §4.4 已明文承認偵測級，此為其量化現況） |
| **N11** | **gain_basis CHECK 留 NULL 缺口**：`sim_evolution_iteration_ledger.gain_basis` nullable ⇒ 不填即繞過值域（tilt_free 為 NOT NULL 無此洞）；五臂地板在 DB 只鎖值域枚舉（含 robot 六臂＝加嚴）**不鎖完備性**，單臂證據即可開判決（`chk_sev_evidence_nonempty` 僅 ≥1） | medium | 親驗 | 專章 §3.4/§3.6 的 DB 落地比條文弱一階；P3 driver 未寫，現無 code 層補位 |
| **N12** | sim kill-switch 未含 sim scope：`KILL_SCOPES=("tw","lai","raw","global")` 寫死＋自測鎖四值封閉集＋argparse choices 限四值 ⇒ 加 sim 須改碼＋改自測＋hugo 親 INSERT，三者順序無文件 | low | 親驗 | 專章生效但緊急煞車對新軸無作用點 |

---

## §5 07-31 治權生效鏈全景（基線零覆蓋區）

**七 commit 兩小時**【親驗，git log】：`0ff869e` 09:41（heavy-slot 餓死三日之修：有界等待＋
holder 帳＋drain 補跑器）→ `f9ee049` 09:51（drain timer 入 install_services SSOT、30 分一輪）→
`847f65a` 10:14（人閘補真閘）→ `b62163e` 10:19（axis registry 遷移工具）→ `ddf356a` 10:24
（專章提案凍結入列）→ `e6afa36` 10:28（**專章 v1.0 生效**＋憲章 v1.54.0＋13 檔指標同步）→
`1a73ade` 10:33（P2 八表 DDL）。

**生效鏈 DB 實證全部為真**【親驗】：gp_86c8063fc688 `kind=treaty_text／status=enacted／
proposed_by=claude／decided_by=hugo／decided_at=10:25:17／note='axis registry 性質認定: patch'`；
凍結 diff_text md5 與定稿檔**逐位元相同**；DB 議決（10:25）早於 git commit（10:28）3 分鐘；
它是 07-25 之後首件、也是**新 TTY 閘生效後唯一一筆**可推定經人親簽的治權簽名。

**專章要點**（`docs/模擬方法自進化專章_v1.0.md`，繕打者全文親讀）：
- 本軸＝八行走者之④能力宣稱＋⑤模擬方法＋⑦迭代程序三重身分，走同一條路；**不是預測軸**
  （§1.2 永久除外項零鬆動：逐日價格點位/路徑/目標價無 GATE 可解）。
- 判準先於資料（prereg＋criteria_sha 指紋錨定）；**五臂地板不可省**（live/ceiling/floor/
  shuffled/mismatched；DB 枚舉另加 robot 臂＝加嚴）；終審＝**統計級校準檢定**（覆蓋率＋PIT），
  明文非 #14 經濟終關（①＝甲）。
- 目標函數硬限：唯「風險形狀之校準品質」，禁方向命中率/報酬（gain_basis CHECK）；禁 tilt 抽樣
  （tilt_free CHECK）。
- 人簽＝**偵測級＋三補強**（②＝甲′）：TTY 閘（已完成 847f65a）＋selftest 不寫人簽欄（行為鎖已落）＋
  明文承認偵測非預防。§4.5 三筆自測簽名之處置**仍待 Steward 裁**（實查原封未動）。
- axis 登錄＝registry 表（③＝乙、性質 patch）：`evolution_axis` 5 列（tw/lai/raw/program/sim）、
  DELETE/TRUNCATE 拒；兩處寫死 CHECK 已改 FK——**兩表值域漂移已消滅**。
- 換尺＝換身分（T.28）；判死留檔 append-only；誠實的無能宣告為合法產出；OCV 白名單僅模擬參數。

**落地與缺口對照**：八表俱在**全 0 列**；`evolution_prereg_gate` 仍僅 V2-SUNSET 一列＝
**§3.1 判準凍結未做、節點二未成立**；`src/augur/simulation/` 不存在＝P3–P6 未起；
方法註冊死鎖見 N1；kill-switch 見 N12。**專章附二的餓死警告當場應驗**：sim 未接線，
tw 軸已長佔 heavy slot（pid 1698 自 11:19:57）、deferred #4/#5 未清。

**同日其他治權事件**：靈魂 v1.10.0（§2a）；憲章 v1.53.0 入口底線＋KH0 普遍口徑（§2b）；
`recover_rejected_titled_works.py` 溯及回收 46,775 筆（knowledge_staging rejected 45,551→2,180、
pending 18,722→76,734）；`ceac40c` 清死鏈。

---

## §6 重開機後基建快照（11:20–11:36）

- **六埠全綠**：8090/8500/8600/11434 → 200、8399 `/v1/models` → 200（六型模型）、6333 → qdrant 1.18.2；
  六支皆 systemd 絕對路徑、STARTED=11:09:06/07、NRestarts=0【親驗】。
- **13 unit（6 service＋7 timer）＋12 條 crontab**＝HANDOFF 重開機節數字完全吻合【親驗】。
- **長跑翻頁**：兩支 replay（30h/24h）已隨重開機消失；philosophy evolution ×2 重起（resume=0 從頭）；
  drain timer 11:19:56 首發正 resume tw-20260728-r01（結果待查）。
- **load 由 10-24 → ~1**；/tmp 兩把鎖檔不存在（無人持有）。
- **systemd 記憶被重置的副作用**：ata-advance 連三日 failed 的狀態證據已被重開機抹除
  （ActiveState=inactive/Result=success）——失敗史現在只活在 ~/ata_advance.log 與 ledger 裡。

---

## §7 對基線的更正（誠實登記，含對並行 07-30 報告）

1. **#15 死鏈**：基線量測已過期（§1）；債應改寫為「治權指標維護只靠一支**有已證盲區**的稽核器，
   且 CS 與入口地圖不在其射程」。
2. **#31**：已半修（§3 債表）；基線列 CONFIRMED high 時修復已 28 分鐘。
3. **A10/B4 翻案**：pending 池是**上升**非下降（log 行 vs live SQL 時序錯配）；**沒有任何人在推進
   全文池**——教訓：把日誌行當即時讀數與 live SQL 併排＝時序錯配造假訊號。
4. **:373 非死碼**（僅 :408 是）；:373 的真病是快取毒化。
5. **min_clusters=250 者 11 門非 12**；direction_gate 現況 29 列＝approved 14／evaluated_fail 12／
   superseded 3（07-30 基線底本「10 fail/16 approved」與其自身廢棄節已自相矛盾，live 為 12/14/3）。
6. **「16 條簽核 CHECK」「15 個 no-goalpost trigger」屬口徑差**：本輪以引用簽核欄口徑得 12 與 14；
   基線未附原始查詢，無法逐條對帳——引用時附口徑。
7. **src/augur 為 16 package 非 18**（memory 與基線沿用的 18 含糊口徑：`ls -d src/augur/*/` 17 項
   含 `__pycache__`）；scripts/*.py 301 支（297→+4）。
8. **記憶「A3 有 2026-08 deadline」查無出處**：dgate_a3_threelens_* 現況 superseded、criteria 無
   deadline 鍵、v4 報告零命中「2026-08」——不宜再引用。
9. **「axis registry 部分實現 path_* 統一設計」措辭誤導**：`path_gate/path_candidate/path_verdict`
   DB 查無任何表＝未實作；evolution_axis 是範圍窄得多的另一件事（僅統一 evolution 自家三表 axis 值域）。
10. **基線債務表實為 42 則**，commit 訊息寫「40 則」（commit 訊息與內容不符）。
11. 對 07-30 並行報告的三處更正（基線 §C 已載）本輪維持成立。

---

## §8 日曆懸崖（全部親驗）

| 日期 | 距今 | 義務 | 現況 |
|---|---|---|---|
| **2026-10-14** | 75 天 | ≥7 項同日到期：RULING-002 五檔 CS 補正、WM.35/36 消費禁令補正（**10-15 起無條件適用**）、RULING-029 L5 §8.2 復審、RULING-025/037 L7 residual ①復審、RULING-012 Phase 7、原則精華 #7 P4.E5（AUD-02 code 補正窗）、ULTRACODE-SCHEDULE 七項併結 | checklist 七格全 `[ ]`；CS 半邊正在惡化（§3 債 #15） |
| **2026-10-31** | 92 天 | V2-SUNSET（三軸整體停止、帳本封存、不得重開） | **0/3**（官方腳本 `report_triple_evolution_week.py` 親跑）：(a) evaluated_pass=0（且腳本 evidence 寫死 /60 與凍結值 250/36 不符）；(b) prodset active=2 未成長（唯一產能管道＝tw 夜輪，正被 drain 補跑但 apply_allowed=false，跑完也不晉升）；(c) LAIEVO 正確判準表＝`local_model_eval_run`：behavior 臂首輪勝過地板但**無任一臂達 ≥2 run 複現**——基線 B7 至此定案 |
| 事件觸發 | — | Moirai cc-by-nc-4.0 商業化前清算 | 非日曆型；provenance 已留痕 |
| 未知 | — | FinMind Sponsor 下次續訂日 | repo 零明文（僅知 2026-07-12 已續訂）；須問用戶/後台 |

**結構性觀察**：SUNSET (b) 是唯一活路，其產能管道（tw 夜輪）當前同時被三件事卡：
heavy slot 競爭（部分修）、apply_allowed=false（刻意、P2-6 不得開）、殭屍輪佔位（drain 補跑中）。
sim 軸不在 SUNSET 三軸內，**不構成續命路徑**，反而分食同一 slot。

---

## §9 優化槓桿 r2（對基線 P0/P1/P2 的增修；未變項不重列）

**槓桿原則不變**：報酬＝（失敗沉默污染多少下游）×（修法多便宜）；最高槓桿仍是「讓紅燈會亮」。

**P0 增修**：
- **P0-2（綠燈帳本）維持最高優先**，加註：E1 的上游（attestation 停跑）已跨過一次重開機仍零觸發
  ——tw 軸有 drain timer 自動 resume 而 raw 對帳無等價機制，**補上這個對稱**（把 audit_selfheal
  或等價物掛回排程）與掛 verify_validation_evidence 同屬一件事的兩半。
- **P0-3（清孤兒）已由重開機翻頁**——改為低成本規範：手動起服務一律 systemd 或絕對路徑（一行進
  HANDOFF 陷阱節即可）。
- **P0-7（殺 replay）已翻頁**——改為：若重跑 replay，先給它鎖與帳（同 P1-5）。
- **新 P0-8**：`evolution_run` 殭屍回填機制（timeout/SIGTERM 落 failed）＋ tw-20260728-r01 收尾
  （**先等 drain 補跑結果**，勿並行介入；該表受 delete-only guard，收尾＝UPDATE＋人簽＝Steward 動作）。
- **新 P0-9**：GOVERNANCE-MAP 補登專章＋README:30/原則精華:7 裸版號清理＋check_treaty_refs 補
  縮寫錨與裸版號規則（工具已在，改 regex 一處）。
- **新 P0-10**：`report_triple_evolution_week.py:39` 之 /60 改讀門內凍結值（一行；防每週儀表
  從首跑起就印錯門檻）。

**P1 增修**：
- **P1-1（人閘抉擇）證據更新**：pty 破口＋Enter 回退＋INSERT 旁門＋DB UPDATE 繞道四條並列後，
  「甲（真機械）vs 乙（誠實承認偵測級）」的天平更清楚——專章 §4.4 已為 sim 軸選了乙（偵測級＋
  明文承認），**建議全系統向專章對齊**：其餘通道也明文降級或真上機械（role 分離另案）；
  並修 governance_queue 的 Enter 回退使「親手打簽名」名實相符（改 `typed or die`，一行）。
- **P1-2（UPDATE guard）範圍更新**：14→23 表；且 sim 八表剛複製同病——migration 時一併處理。
- **P1-3（KH 誠實化）加一件**：降級操作必須同時改 layer_scores 或改 GREATEST 邏輯，否則一切降級
  都會被自動還原（本輪實證）。
- **新 P1-10：KH0 普遍破口 48.68% 的履行計畫**（v1.53.0 新義務；138,829 件、標題級理解、
  本地 AI 產能與車道皆是約束）——這是靈魂 v1.10.0 終點的地基工程，量級最大、宜獨立計畫書。
- **新 P1-11：sim P3 前置三件**（方法註冊人簽路徑〔20 method 包裹 or 逐件〕、kill_switch 加 sim、
  車道決議）——**未解前不開 P3**，否則專章附二的三軸餓死從警告變日常。
- **新 P1-12：fulltext 出料端補排程**（#8 升級後的正確修法是「加一條 fetch 排程」而非修 timer）。

**P2（不該碰）增列**：
- **P2-9**：不要在 drain 補跑進行中並行動 tw-20260728-r01（兩個 writer 撞同一殭屍輪）。
- **P2-10**：不要為了讓 sim 軸「有東西」而由 AI 批次註冊 20 個 method——`chk_smr_registered_signed`
  要求的人簽＋gate_ref 正是專章剛立的門，繞它＝生效第一天就毀約。
- **P2-11**：不要把 admit_depth 的 bulk UPDATE 當降級手段（會被 GREATEST 還原；見 P1-3）。

---

## §10 記憶漂移（本輪已修正／待修正清單）

實查活 memory 與 repo 快照 73/73 一致，故修正須同步兩處（改活 memory 後由既有 export 流程帶走）。

| 記憶 | 漂移 | 處置 |
|---|---|---|
| MEMORY.md KH0 行＋kh0-coverage-vs-quality | 「破口 0 已達」已被 v1.53.0 撤回（真破口 48.68%）；「90.3s 逾時、從未答成」已被該檔正文自我更正（62.7s 答成）但索引/description 未同步；「ollama 無 unit」→ 實為 `augur-ollama.service`（user-level）active | **本輪修正** |
| augur-tech-baseline-20260730 | 治權版號四件套全過期；294 表/63 DDL/425 矩陣/270,736 item/3 proposal/11 unit 全過期（現 309 relations/68/440/285,177/4/13）；「18 package」實為 16 | **本輪加更正註** |
| jian-a-admission-hardening | 「verify_knowledge_admission_health＝日常哨兵」＝零接線（crontab/unit/hook 全無） | **本輪修正** |
| augur-construction-v4 索引行 | 「A3=preregistered〔有 2026-08 deadline〕」：A3 已 superseded 且 deadline 查無出處 | **本輪修正** |
| augur-project-map／augur-db-schema-traps／augur-three-gate-strengths | 版號/數字快照過期（21→27 零列表、437→440 等）；檔內已自帶「引用前實查」護欄 | 列入下次 consolidate，不逐檔動 |

---

## §11 誠實界定：本輪未做與仍未知

- **未修任何債**（本報告是核驗與地圖；記憶修正除外——屬「記住」指示之一部）。
- **仍未知**：07:56/07:57 兩次手動 embed 與 07-30 15:29 bulk 降級由誰發動（無 actor 欄）；
  drain 補跑 tw-20260728-r01 的最終結果（進行中）；`+15 表`中 5 張中間 oid 表的精確落地時點；
  G10 FAIL 的實際殘留位置；direction_arena 結算停在 4,128 是標籤未到期還是 07-30 結算輪未產出；
  f143aa6 的排程級驗證（08-01 04:00 才有）；`getpass.getuser()` 在 cron/systemd 下的回傳值。
- **未涵蓋**：reports/ 281 檔中約 260 檔仍僅標題級分類（結構掃描已做、逐份核驗未做）；
  RBAC live 行為（債 #29/#30 沿用基線單路）；DESKTOP-8MQPFS8 側。
- **本報告未受獨立核驗**——與基線同一條款（RULING-2026-028 第 3 點）適用於本報告自身；
  且依 §1 之折舊率，本報告的 live 數字自 11:36 起開始腐爛。

## §12 繕打者親驗記錄（非 agent 轉述）

親讀全文：基線報告 528 行、`docs/模擬方法自進化專章_v1.0.md`、`docs/系統核心思想_v1.10.0.md`、
07-30 並行報告、HANDOFF.md 全文；親跑：`git log`（分支＝main 同步確認）、`ls docs/`（版號）、
憲章 v1.52-54 修訂歷程段、DB ping、`systemctl --user list-units`、`date/uptime`（11:09 重開機、
11:16 查核）。12 路 agent 結果經交叉比對（同一數字多路互證者：prodset active=2、arena 4,128、
kh4 eligible 145,952、governance_proposal 4 列、evolution_axis 5 列——全數一致）；
單路且未複跑者一律標【單路】。

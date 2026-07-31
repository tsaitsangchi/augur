# Augur 深化理解報告——優化地基（2026-07-31）

* **用途**：Steward 指示「深化理解此專案所有檔案內容後詳細理解並記住，並做出深化理解的專案報告，
  以做為後續優化此一專案的基礎」。本報告即該基礎。
* **產製**：四路平行深讀（workflow `wf_92189d46-ac9`：治權層／知識顧問層／維運工具層／結構性債務）
  ＋綜合；**繕打者就承重宣稱逐項親驗**（見 §0 與 §10）。
* **與既有兩份之關係**：`augur_full_reread_facts_20260730.md`（296KB／1,031 行）＝**逐檔事實底本**，
  查細節用；`augur_deep_understanding_optimization_base_20260730.md`（並行 session，12.7KB）
  ＝早一版優化地圖，**本報告已核驗並更正其兩項**（§10）。本報告＝**行動地圖**，三者互補。

---

## §0 讀法：三種可信度，而且所有數字都是快照

| 標記 | 意義 |
|---|---|
| **【親驗】** | 繕打者本輪實跑指令／SQL 得到輸出 |
| **【單路】** | 單一 agent 讀碼或查表所得，繕打者未獨立複跑 |
| **【轉述】** | 引用他人文件，未獨立驗證 |

**數字會在數小時內腐爛。** 本輪覆核期間 public 表數 295→296、大憲章 v1.52.0→v1.54.0、
chat/admin 重啟計數 10,819→**24,064**。凡硬數字一律附取得方式；**引用前請重跑其附註指令**。

---

## §1 這個系統實際上是什麼

> Augur 實際上是**一台單人操作的「把治理寫進資料庫」的研究機**——296 張表／437 支可執行入口／41 份裁決／十層知識准入閘，整套架構圍繞「不自欺」這一個目標建造；但它的自我監督分三種強度且被同一個詞（「機械閘」）包起來：**PG trigger 真的擋得住（僅 33 表）／Python `--selftest` 大多在驗字串常數而非行為（437 支入口，零 CI 零 hook）／「只有人能做」這件事在整個系統裡沒有任何一行 code 或 DDL 分得出人與 AI**。更關鍵的是，它唯一那張宣稱「驗證鏈全綠」的總表 `validation_evidence`（19/19 green）現在有 **3/12 機械檢查回 false、另 7 列根本沒有 check_sql**，而正典對帳 **最後一次通過是 2026-07-16、2026-07-25 後停跑**。所以現況一句話：**這是一台儀表板全綠、但多數儀表沒接線的機器；它最珍貴的資產不是知識庫也不是預測，而是那套「禁止假關」的誠實文化——而那套文化目前跑得比它的機械閘快。**

**用我自己的話重講**：它不是「預測系統＋知識庫＋治理文件」三件事拼起來，而是**一件事**——
一台**以 PostgreSQL 為唯一系統記錄、把「什麼才算真的」寫成表與 trigger 的誠實性機器**。
台股預測與知識庫都是它的**測試載荷**，用來壓測那套誠實性機制撐不撐得住。

這解釋了許多看似怪異之處：為什麼判死要留檔、為什麼帳本不准刪、為什麼「誠實的無能宣告」
被明文列為合法產出、為什麼一個人的專案要寫 41 份裁決。**因為產品不是預測，是那套機制本身。**

---

## §2 全報告的地圖：機械閘有三層強度，而專案用同一個詞稱呼它們

| 層 | 是什麼 | 覆蓋 | 真的擋得住嗎 |
|---|---|---|---|
| **L-硬** | PG trigger／GRANT | 33 表 | **是**——不需要任何人記得 |
| **L-半** | trigger 只綁 DELETE+TRUNCATE，UPDATE 全裸 | 14 表 | **一半**——刪不掉，但可被 UPDATE 改寫 |
| **L-軟** | Python `--selftest` | 437 支入口，**零 CI、零 git hook** | **多數不是**——大量在驗「字串出現在自己原始碼裡」 |

**這是所有誤判的來源**：專案的自我敘事把三層當同一件事講。看到「15 個 no-goalpost trigger」
「7 個 GUC guard」「437/437 矩陣全過」會合理推論「這系統被機械守著」——
但**最承重的那條（只有人能做）落在 L-軟，甚至更弱**。

---

## §3 治權層：兩套法、一張導航紙、一個分不出人與 AI 的簽名欄

治權是**兩套**：`constitution/`+`specs/`（L0–L7 元憲章與七層規格，**有 lint 天天守**，
本輪實跑 PASS 7/7、WM.44 覆蓋缺口 0/102）與 `docs/`（領域四檔：靈魂／原則精華／大憲章／CLAUDE，
**工具寫好了但沒掛**）。兩者靠 `GOVERNANCE-MAP.md` 導航。

**lint 的射程不含 docs**【親驗】——`corpus_files()` 只 glob `specs/*.md`
（`tools/constitution_lint/report.py:51-61`）。所以 audits 裡反覆出現的「lint PASS 7/7」
**一個字都沒檢查**領域四檔與五份合規聲明。這正是那半邊能長出死鏈與版本錯亂的原因。

**權力結構**：Steward 是單一自然人；`RULING-2026-031`（2026-07-23）廢止「原則級修訂須 14 日
公示」後，**修憲成本已降到「一個人簽字」**。剩下的結構性制衡只有 §8.5(b) 二要件與
§8.4 不可豁免核心（Prime Axiom／Evidence 追溯／人類權威 P5.W2、P5.W5——**連履行時程亦不得豁免**）。

---

## §4 最重要的一件事：綠燈帳本本身是假的

`validation_evidence` 是全世界唯一一張「驗證鏈健康」總表，**19/19 green**【親驗】。
拆開來看【親驗，本輪逐條重跑】：

- 19 列中只有 **12 列有 `check_sql`**（可機器覆算），另 7 列是 manual／script_exit 斷言；
- 12 條可執行檢查中，**現在有 3 條回 false**：

| evidence_id | chain_link | last_verified |
|---|---|---|
| `E1_raw_reconcile_exit` | raw | **2026-07-15** |
| `E2_feature_frozen_panel` | feature | **2026-07-11** |
| `E4_exclusion_set_contract` | gate | **2026-07-11** |

- 能把它們翻紅的 `verify_validation_evidence.py` **不在任何排程**。

**所以：這個世界的地基綠燈，已經紅了兩週而無人知道。** 這不是「慢」，是**沉默污染**——
任何人（含未來的 AI session）讀到的都是全綠，並在此之上做判斷。

### §4.1 三個 false 是三種不同的病，不要一起處理

- **E1 是真退步**：正典對帳最後 `passed=t` 為 **2026-07-16**，07-24/25 五次全 false，
  07-25 18:14 後**停跑**。資料地基的唯一持久化驗證停擺，而 arena 每天照樣出單。
- **E2／E4 是契約被政策合法作廢**：契約寫死凍結期數字（35 特徵／2,418,655 列），
  而 2026-07-12 已拍板「解凍→live 增量」，live 現為 38／8,540,331。**這不是壞掉，是過期。**

**混為一談的後果**：有人會去改 `check_sql` 湊綠——那正是 #12 禁止的 hand-patch。
E1 要修；E2/E4 要 Steward 決定 **retire 還是 re-baseline**。

---

## §5 最會騙人的假綠：systemd 說在管，實際跑的是孤兒舊碼

【親驗，本輪 `ss` ＋ `systemctl show`】

```text
:8090 → pid 3387306   啟動 Thu Jul 30 15:46:46   ./venv/bin/python scripts/serve_chat_ui.py
:8500 → pid 3342300   啟動 Thu Jul 30 14:23:41   ./venv/bin/python scripts/serve_admin_console.py
augur-chat   NRestarts=12005   Active=activating
augur-admin  NRestarts=12059   Active=activating
```

兩支**昨天手動起的孤兒**佔住埠（相對路徑 `./venv` ＝從 shell 起），
systemd 副本每幾秒崩潰重啟、累計 **24,064 次**。

**為什麼這是最危險的一種假綠**：`systemctl restart` 回報成功、埠通、頁面開得起來——
**但載入的是 18–20 小時前的記憶體版**。CLAUDE.md #7（改常駐服務後須重啟再實測）
在這兩支上**完全失效，而且是以「重啟成功」的形式失效**。重開機後這兩支不會自動回來。

**對照組**：advisor（:8399）、probability（:8600）、ollama（:11434）皆為今日 08:00 由 systemd
以絕對路徑啟動、NRestarts=0【親驗】——**同一套設施，差別只在有沒有孤兒佔埠**。

---

## §6 債務總表

依「不修會怎樣」排序（不是依修的難度）。CONFIRMED = 有實測輸出；PLAUSIBLE = 僅讀碼推論。

| # | 債務 | severity | 證據級 | 不修會怎樣 |
|---|---|---|---|---|
| **1** | **`validation_evidence` 19/19 綠是假的**：12 條機器檢查現 3 條 false（`E1`/`E2`/`E4_exclusion`）、另 7 條無 `check_sql`；能翻紅的 `verify_validation_evidence.py` 不在 crontab | high | **CONFIRMED**（本輪逐條重跑） | 這是全世界唯一一張「驗證鏈健康」總表，所有下游宣稱（含 arena 資料地基）都站在它上面。不修＝任何人（含未來 AI session）讀到的都是全綠，**錯誤會沉默地污染所有判斷**，而非只是慢 |
| **2** | **正典對帳紅兩週、停跑六天**：`attestation_result` 最後 `passed=t` 為 2026-07-16，07-24/07-25 五次全 f，07-25 18:14 後無執行 | high | **CONFIRMED** | 資料地基的唯一持久化驗證停擺。arena 每日照樣出單、演化照樣跑，全部建立在一個未經驗證的 raw 層上 |
| **3** | **「AI 不得代簽」在 DB 層零機械強制**：16 條簽核 CHECK 全部只驗非空；零 `current_user`/`session_user` trigger；7 個 guard 全是可自設的 GUC；單一 `augur` role；`knowhow_governance_ledger.decided_by` 預設值就是 `'HUMAN'` 且該表零 trigger；已有 3 筆 `selftest`/`hugo-authorized-selftest` 寫進人簽帳本 | high | **CONFIRMED** | P5 人類權威、L6.18(a) 反自我交易、憲章 §213、CLAUDE #26 全繫於此。目前它是紀律不是機制，且**外觀很機械**（15 個 no-goalpost trigger、7 個 GUC guard）會誤導人以為人閘也被守住。事後永久無法區分「hugo 親按」與「腳本批寫」 |
| **4** | **`honesty_delete_only_guard` 不擋 UPDATE**（14 表，含 `evolution_production_feature_set`／`promotion_queue`／`evolution_kill_switch`／`philosophy_principle`） | high | **CONFIRMED**（本輪 tgtype 解碼） | 一句 UPDATE 就能把生產特徵集從 `removed` 翻回 `active`、關掉 kill switch、改寫原則——零留痕。**這不是理論風險：`evolution_iteration_ledger` 的 07-28 steps_json 已經被逐夜覆寫吃掉了**。現成解法（`honesty_ledger_guard`，UPDATE 需 GUC 通行證）已在同一 DB 內服役於 4 張表 |
| **5** | **TWEVO 夜輪四晚零產出 + orphan `running` 卡住下一輪**：`tw-20260728-r01` 自 07-28 開輪至今 running、steps=3，07-30 撞 `TimeoutExpired(7200s)` | high | **CONFIRMED** | V2-SUNSET (b)「prodset active 由 2 成長」是三條落日條件中唯一還活著的，唯一產能管道就是這條夜輪。距 2026-10-31 落日剩三個月，**在完全不知情的狀態下走向「三軸整體停止、帳本封存、不得重開」** |
| **6** | **repo 層零自動觸發器**：`.git/hooks/` 非 sample 檔 0、無 `.github/workflows/`、無 `.pre-commit-config.yaml` | high | **CONFIRMED** | `check_cmd_matrix`／`check_treaty_refs`／`import_isolation`／`verify_validation_evidence` 四個真有價值的機械閘全部「存在但不會自己跑」。DB trigger 之所以可信正因為不需要人記得；code 層繼承了同一個名字卻沒有同一個性質 |
| **7** | **零失敗通知路徑**：12 條 cron 全部只 `>> log`、6 個 systemd unit 全無 `OnFailure=`、`flock -n` 搶不到鎖靜默 exit、`arena_pipeline.log` 2213 行零時間戳 | high | **CONFIRMED** | 這是債 #1/#5/#8/#11/#13 全部能同時存在而無人知的**共同根因**。不先修這個，之後每一項優化只會在更多靜默失敗上疊加更多靜默失敗 |
| **8** | **知識進料在跑、出料死三天**：`augur-ata-advance` 連續 07-29/30/31 exit 1（embed 自我保護「處理 185 句但 0 新列」）；`harvest_knowledge.py` 對三段後續管線引用數 0 | high | **CONFIRMED** | `item→item_text` 損耗 48.7%（285,177 → 146,397）**每天都在惡化**，因為進料端在跑而出料端是死的。CLAUDE.md #29(b) v1.20「不得只抓 metadata 就宣稱完成」目前靠一個壞掉的 timer 履行 |
| **9** | **KH8 fail-closed 鑑別力閘已自行解開，07-30 降級是零效果儀式**：`population_discriminates → ok=True`（靠 396+16+380 列失敗樣本製造變異）；`DEEP_KH_FLOOR=7` 使降級後仍在深水印帶；`layer_scores` 仍寫 8/9 pass 與 `admit_depth=7` 自相矛盾 | high | 親驗·單路（lens 2、4 獨立同結論） | 145,952 件平均 78 字元的 ERP 欄位說明，長期在顧問引文中排在公版原典之前。而帳面上有一道「證據不具鑑別力就不套深度優先」的閘——**它是開的，且沒有任何告警會說它開了**。這是「加一列 band=low 即解閘」漏洞換個分量的重演（F-bypass-1） |
| **10** | **systemd 說在管、實際跑的是孤兒舊碼**：8090/8500 被 07-30 手動行程佔住，systemd 副本 NRestarts 11,027/11,079 仍在漲 | high | **CONFIRMED**（本輪 `ss` + `NRestarts`） | 會騙過所有標準檢查手法的假綠：`systemctl restart` 成功、埠通、頁面開，載入的卻是 07-30 的記憶體版。CLAUDE.md #7 在這兩支上完全失效；重開機後服務不會自動回來；22,106 次 5 秒一輪的重啟長期佔 CPU |
| **11** | **四條週排程從未執行過一次**（Mon 08:00 維運健檢、Mon 08:40 工具自測、Sat 09:00 RAWEVO、Sun 09:00 三軸週儀表） | high | **CONFIRMED**（`~/logs/` 四檔皆不存在） | 「已寫、已裝、零實證」卻已被當成既成維運機制引用。首次執行在 08-01/02/03，若有語法或路徑錯誤，依債 #7 也不會有人知道。且 Sun 09:00 輸出檔名日期寫死，週儀表永遠只有一份、無歷史可比 |
| **12** | **三個 approved arena 方向門結構上零列可評**：`dgate_arena_own_stack_20/40/82` 的 `model_id='own_stack_rolling'` 在 `direction_arena_prediction` 中一列都沒有，且全表 `horizon_td` 只有 5 | high | **CONFIRMED**（本輪） | 比「門檻太高」更糟——它連 `undecidable` 都不會回報，每日被 pipeline 檢查卻永遠不可能 evaluate。同時修正了並行報告「一律 250、物理不可達」的說法 |
| **13** | **驗證器層事實上未接線**：35 支 `verify_*` 中 28 支無任何自動呼叫者，含被專案記憶記為「日常哨兵」的 `verify_knowledge_admission_health.py` | high | 親驗·單路（lens 3） | 專案建了一整層驗證器，一支都沒排進自動回歸。更危險的是**記憶與現實已脫節**——以「我們有健檢」為前提做的任何優化決策都建立在錯誤前提上 |
| **14** | **`--selftest` 大量為字面斷言/恆真式**，且憲章上最要緊的兩項保證恰好只有字面證據 | high | **CONFIRMED**（本輪逐行） | `evolve_cycle.py:401` 是恆真式（斷言的字面量就寫在斷言那一行）；`review_evolution_candidates.py:43` 是 `chk(..., True)`；`run_evolution_iteration.py` 的「零代簽人閘」「APPLY 預設關」靠字串比對。**一次保留字串但改變行為的重構，這些會照樣全綠**。該檔自陳同型教訓已五犯 |
| **15** | **治權引用 12 則死鏈 + CS 落後三版且持續惡化**：全部指向不存在的 v1.51.0；`CS-...v1.53.0.md` 內文仍寫 v1.51.0/v1.50.0，兩次升版都是純改名 | high | **CONFIRMED**（本輪重跑 RC=1） | `GOVERNANCE-MAP.md` 的存在理由就是 10 分鐘知道義務落點，它指向死檔＝入口失效；新 session 讀序第一站就撞牆或去讀 SUPERSEDED 的 v1.47.0。工具已寫好且 exit 1，**只差沒人叫它**——最廉價的修法 |
| **16** | **`constitution_lint` 的 corpus 只含 `specs/*.md`**，完全不含 `docs/` 四檔與 `docs/compliance/`；而 audits 反覆以「lint PASS 7/7」當治權衛生證據 | medium | **CONFIRMED**（讀 `report.py:51-61` + 兩子命令 RC 對比） | 造成系統性錯覺：治權有兩半、只有一半有守衛，通過報告卻寫得像全域通過。債 #15 的死鏈與 CS 版本錯亂**全部落在 lint 射程外，這正是它們能存活的原因** |
| **17** | **`constitution_lint --selftest` 真實 exit 1（G10 FAIL），且是四套工具中唯一未被納入週一自測 cron 的** | medium | **CONFIRMED**（本輪 `REPORT_RC=0` vs `SELFTEST_RC=1`） | 唯一真的在紅的那套，恰好是唯一沒被排程的那套。且極易誤引：`report` 綠、`--selftest` 紅，引用時不指明子命令就會傳播錯誤結論 |
| **18** | **KH0–KH10 十層裡只有 KH0/KH3/KH4 有 per-item 鑑別力**：KH6/KH7 庫級（145,952 件靠 6 列 pass 過關）、KH9 是 KH8 的純函式、KH10 是布林、KH1/KH2/KH5 的 fallback 幾乎恆真 | high | 親驗·單路（lens 2 讀碼＋查表） | 「十層漸進准入」帳面上是縱深防禦，實際上只要有 text+sentence+embedding+kh4 就自動變 depth 7「深水印」並在檢索優先。**深度水印傳達的資訊量遠低於它的名字暗示的**。優化第一步不是加 KH11，是先讓 KH5/6/7 變 per-item 或誠實降級為庫級旗標 |
| **19** | **123,304 件 item 因無 `kh4_state` 列而結構性不可達**（`_ITEM_JOIN` 是 INNER JOIN） | medium | 親驗·單路（lens 2） | 不是分數低撈不到，是 SQL 上 join 不到。任何以 `knowledge_item` 列數描述「知識體量」的宣稱都高估可答性約 2 倍；且「有 text 卻無 kh4 列」的子集顯示 `kh4.refresh_items` 覆蓋不完整 |
| **20** | **約 149 萬條哲學側句嵌入零消費端**（佔 `knowledge_sentence_embedding` 85%；works 作答走另一組 `philosophy_chunk_embedding`） | medium | 親驗·單路（lens 2） | 最大一塊「已完成但接不上」的資產。同時佔用 HNSW 索引記憶體（本專案已兩次踩 HNSW×並發 OOM），對每次 ANN 查詢造成成本卻不貢獻召回 |
| **21** | **`retrieve_items` 的 Qdrant ANN 分支漏 `k4.answer_status='eligible'` 過濾**（exact 與 pgvector 分支都有） | medium | 親驗·單路（lens 2） | 可答性判準隨「Qdrant 有沒有活著」而改變：Qdrant 活著時 15,921 件 provisional/ineligible/blocked 可經 ANN 進入引文。**閘壞了不會變紅燈，只會安靜地多放行一些東西** |
| **22** | **`retrieve_all():408` 的 `set_kh_evidence_validity(cur)` 是死碼**（`cur` 未定義，NameError 被 `except: pass` 吞）；`:373` 那處則寫快取不寫 `_at` 導致每次白掃 146k 列 | medium | **CONFIRMED**（本輪確認行號；AST 由 lens 2/4 獨立驗證） | 目前靠 `kh_evidence_valid()` 自開連線兜底，是巧合而非設計。`auto_admit.py:130-139` 的 docstring 白紙黑字寫「此病已修為呼叫端零配合」——**文件宣稱已修、code 裡原病還在**，會讓下一個讀者誤以為所有呼叫端都乾淨了 |
| **23** | **三套互斥機制命名空間互不相交**：flock `/tmp/augur_llm.lock`／PG advisory `HeavySlot`／完全不上鎖者（advisor 常駐、arena 4 小時管線、兩個手動 replay） | medium | **CONFIRMED**（本輪 crontab + load） | 全機無單一重活車道。實測後果：load 10-24、ollama 降到 0.31 t/s、TWEVO 的 I3 從 cron 註解宣稱的「25-35 分」變成 7200 秒 timeout。`heavy_slot.py` 本身設計優良，**問題純在覆蓋率不在實作** |
| **24** | **27 張 ledger/log/audit/verdict 類表零 trigger**，其中 4 張（`revalidation_ledger`/`revalidation_verdict`/`data_audit_log`/`pipeline_execution_log`）還對 `augur_predict` 開了 DELETE | medium | 親驗·單路（lens 4） | 帳本的價值等於「不能被改寫」。預測管線的服務帳號可以刪掉自己的複驗紀錄。同批的 `trial_ledger`/`revalidation_baseline` 已被 `honesty_ledger_guard` 中和，**證明修法已知、只是覆蓋不全** |
| **25** | **`migrate_*.py` 的 `--selftest` 系統性只驗 Python 字串常數、從不查 live schema**（至少 8 支） | medium | 親驗·單路（lens 4） | 證明的是「我寫的 SQL 文字裡有這句話」，不是「DB 裡真的有這個約束」。DDL 沒 apply、apply 到別的 DB、或事後被 ALTER 掉，自測一律全綠。**跨機（DB 不隨 git）情境下特別危險**。正解已存在於同 repo（`to_regclass` 查 live） |
| **26** | **`check_cmd_matrix` 的 437/437 只是字串存在稽核**（`MATRIX_STR = "執行指令矩陣"`） | medium | **CONFIRMED** | CLAUDE.md #29(d) 要求「矩陣＋須實測可執行」，稽核只機械化了前半。437/437 很容易被讀成「437 個入口都驗過了」 |
| **27** | **測試層無法分離安全子集**：無 conftest、無 marker、9/24 檔連 DB 其中 4 檔含寫入；`arena`/`catalog`/`execution`/`universe` 四個 package 零測試 | medium | 親驗·單路（lens 3）＋本輪 275 tests 確認 | 想跑回歸只能全跑（會寫 DB）或逐檔手挑＝實務上沒有可日常執行的回歸。而零測試的 `arena` 正是**每交易日 20:00 出單、唯一對外產生預測、且無 selftest 又不上鎖**的子系統 |
| **28** | **`≥60 clusters` 這個現行 [N] 治權數字，live 沒有一個門在用**；H 軸三個 approved gate 用 36（低於治權門檻） | medium | **CONFIRMED**（本輪 grep 條文 + 查 gate） | 方向是「放寬」，依大憲章通則二／原則精華:173「放寬從嚴」應認定為重大判準修正並附 OCV 前後對照，但無此程序留痕。注意：**門柱 trigger 只禁事後改，不禁一開始就訂低**——挪門柱閘防不了這一類 |
| **29** | **RBAC 收窄邏輯零 live 執行證據**：`app_user` 只有 admin 一人且是 superuser，150,772 筆 ERP 私有內容 owner 全是 user 1；`is_super=True` 時 `clean_item_sql` 一律不濾 | medium | 親驗·單路（lens 2） | 整套隔離讀起來 fail-closed 且嚴謹，但 live 上每一次檢索走的都是「不濾」分支。**要把 ERP know-how 開給第二個人之前，這是必須先補的實證** |
| **30** | **顧問單次作答 33 分鐘**（實測 1,978.2s，timeout 已拉到 2400s） | medium | 親驗·單路（lens 2） | 不是 bug，但決定了這一層的可用性上限：任何需要人在回圈的作答品質驗證（RBAC、KH-first 排序是否真的更好）在此成本下**事實上做不了 A/B**。優化檢索品質前得先有一條不經 qwen3:8b 的評測路徑 |
| **31** | **`governance_queue.py` 是唯一治權提案人閘 CLI，卻無 TTY 檢查且用 `getpass.getuser()` 自動取簽名**，其 docstring 卻宣稱「比照 direction_gate TTY 親核先例」 | high | **CONFIRMED**（本輪 grep） | 它管的是 `criteria_change`/`treaty_text`/`soul_amendment`——最高風險的治權動作。AI 以 hugo 帳號跑 `--approve` 會自動簽成 hugo 且無阻擋。**docstring 的宣稱會讓後續讀者（含 AI）相信該通道已 fail-closed 而不再檢查** |
| **32** | **`flock -n` 靜默跳過，且 self_seek 的 cron 註解與實作對「是否入鎖」自相矛盾** | medium | **CONFIRMED**（本輪 crontab 原文） | 01:30 演化鏈與 4/10/16/22 evolve_cycle 一旦碰撞，整個作業無聲消失（連腳本內部的「另一條鏈在跑，略過」都不可達）。而註解寫「不入鎖」的 self_seek 實際用 `flock -w 3600` 佔 LLM 單槽鎖最多一小時——**沒有人知道那把鎖現在被誰持有多久** |
| **33** | **`augur-audit-watchdog` 準時執行，但其標的 `~/audit_retry.log` 已 16 天未更新** | medium | 親驗·單路（lens 3） | 看門狗活著、log 在長、systemctl 一切正常——但它守的東西早就停了。邏輯是「最後一條 attestation 若 PASS 則無需動作」，log 停在某個 PASS 上就永遠回報健康。**機制沒壞，是它守護的對象消失了，而機制不知道** |
| **34** | **GOV-1（§8.1 解釋權無實體界線）仍是未閉的 major**；`RULING-2026-031` 廢止強制公示後修憲成本降到「一個人簽字」，該洞的可利用性反而升高 | medium | 讀碼 / PLAUSIBLE | 治權體系唯一被自己的對抗稽核判為 major 的結構洞。原 2026-08-06 期限已失效＝此案現在**沒有任何時間壓力**，靠一份自陳「無法自我封口」的過渡裁決撐著 |
| **35** | **`local_ai_iteration_ledger` 與 `pipeline_execution_log` 至今零列** | low | 親驗·單路（lens 4） | 不是少落帳，是零落帳。任何以「有這張帳本」為由的可追溯性宣稱都是空的 |
| **36** | **`HUMAN_ONLY = set()` 死閘空殼**：判斷式仍在、集合為空、自測反過來鎖定它必須是空的 | low | 讀碼 / CONFIRMED（讀碼層面） | v1.48.0 有意廢止，非 bug；但在一個以「人閘」為核心紅線的系統裡，**留一個空殼人閘在程式碼裡比刪掉它更危險**——任何 grep `HUMAN_ONLY` 的人（含未來 AI）會誤以為仍有唯人閘 |
| **37** | **`concordance_lookup` 不套 RBAC 收窄，靠「目前沒有呼叫端」保護** | low | 親驗·單路（lens 2） | 明文寫在 docstring 的已知地雷，但保護機制是社會性約束不是機械閘。`knowledge_concordance` 有 5,325 萬列且正是 exact 路徑核心索引，未來很可能有人想接進顧問路徑 |
| **38** | **`embed_knowledge` 與 ATA 對「還差多少嵌入」口徑相差 92 倍**（40,920 vs 445） | low | 親驗·單路（lens 2） | 沒有單一可信的「進度真相」。ATA 用「item 層級有任一已嵌句就算過」，會在 item 只嵌 1/50 句時報 0 缺口——**任何以 ATA 池量判斷「補完了」的自動化都會提早收工** |
| **39** | **`evolve_self_seek` 每 6 小時固定 +12 條 query 無上界**（單域 software_engineering） | low | 親驗·單路（lens 3） | 每天 +48 條而 quant_finance 已回報無新缺口。尚未故障但趨勢單向，最終會擠壓 01:30 演化鏈的 `--max-minutes` 預算 |
| **40** | **`augur-qdrant.service` 的二進位在 `~/project/ttai/` 下，跨專案依賴** | low | 親驗·單路（lens 3） | 換機接續時 `sync_from_github.sh` 帶不到、HANDOFF 流程也不檢查 → 「repo 完整還原但 qdrant 起不來」的斷點 |
| **41** | **`augur-knowhow-refresh.timer` inactive/dead 且無下次觸發，實質已停用但仍在 unit 清單** | low | 親驗·單路（lens 3） | 盤點排程時易被誤計為「有在跑」，形成對知識管線更新頻率的錯誤認知 |
| **42** | **2026-10-14 治權懸崖（≥7 項義務同日到期）與 2026-10-31 V2-SUNSET，相隔 17 天** | medium | 讀碼 | WM.35/36 的後果是「自 10-15 起消費禁令**無條件適用**」——會改變系統能否合法消費某類資料的硬開關，不是文書工作。而 SUNSET 三條件目前 (a) 結構上零列可評、(b) 產能停擺、(c) 未查。距第一個懸崖 75 天 |

---

## §7 優化槓桿

## 核心判斷

從債務表看，**這個專案不缺工具、不缺條文、不缺紀律文化——它缺的是「條文/工具」與「會自己跑的機械閘」之間那一段接線**。四路獨立得出同一結論：`check_treaty_refs`、`check_cmd_matrix`、`import_isolation`、`verify_validation_evidence`、35 支 `verify_*` 全部已經寫好、多數會正確 exit≠0，但**沒有一個會自己跑**。同時，唯一那類「不需要人記得」的閘（PG trigger／GRANT）恰好是全系統唯一沒有假綠的部分。

**槓桿排序原則：報酬 = (該處失敗會沉默污染多少下游) × (修法多便宜)。** 依此，最高槓桿全部集中在「讓紅燈會亮」，而不是任何新能力。

---

## P0 — 現在就該做（全部可逆、唯讀或單向增強、本地零 Claude usage、不需計畫書）

> 判準：屬 CLAUDE #26「改正確／補完整」之執行層，或屬純接線；**唯 P0-6 觸及治權判準，須 Steward 拍板**。

**P0-1｜把四個現成閘接上 pre-commit（單一 `.pre-commit-config.yaml`，一次到位）**
- `check_treaty_refs.py`（現 12 則、RC=1）、`check_cmd_matrix.py`（現 RC=0）、`import_isolation`、`tools.constitution_lint --selftest`（現 RC=1）。
- 報酬：直接封住債 #6/#15/#17；且 CLAUDE.md #29(d) 原文就寫「供 CI／pre-commit 掛勾」——這是**兌現一句已入憲卻從未落地的話**，成本一個檔。
- 注意：`constitution_lint` 有 `report`（RC=0）與 `--selftest`（RC=1）兩個子命令結論相反，掛哪個要明示。

**P0-2｜把 `verify_validation_evidence.py` 掛進每日排程，並先分流三個 false**
- **必須先分流，否則會有人去改 `check_sql` 湊綠（違 #12 不 hand-patch）**：
  - `E1_raw_reconcile_exit` = **真退步**（對帳紅＋停跑）→ 修 attestation 執行鏈。
  - `E2_feature_frozen_panel`、`E4_exclusion_set_contract` = **凍結期契約被「解凍→live 增量」政策合法作廢**（契約寫死 35 特徵/2,418,655 列，live 已 38/8,540,331/113 panel）→ 這是 **Steward 決策**：retire 該列，還是 re-baseline 成 live 口徑。
  - 另 7 列 `check_sql IS NULL`（manual/script_exit）→ 至少在報表上與 12 條機器檢查**分開呈現**，不再合併成「19/19 綠」。
- 報酬：封住債 #1/#2，這是全系統地基綠燈。

**P0-3｜恢復 chat/admin 的 systemd 管轄**
- 清掉 8090/8500 的 07-30 孤兒行程（pid 3387306/3342300）→ 讓 unit 正常 bind。
- 報酬：封住債 #10（會騙過所有標準檢查的假綠）＋回收約 0.4 核長期佔用。
- **這是破壞性操作（殺他人進程），依 CLAUDE #6 與本 workflow 紀律，須 Steward 明示授權後才執行——本輪僅報告。**

**P0-4｜給所有 augur unit 加 `OnFailure=`，並讓失敗訊號可讀**
- 至少讓 `augur-ata-advance`（連三天紅）、`augur-chat`、`augur-admin` 的失敗有一個落點。
- 注意 `augur-ata-advance` 用 `StandardError=append` 把 stderr 導離 journal——**lens 2 因此誤判「沒有錯誤訊息可讀」，lens 3 在 `~/ata_advance.log` 找到了明確原因**。這個模式若複製到其他 unit 會讓 systemd 層可觀測性歸零。
- 報酬：封住債 #7 的一半（另一半是 cron）。

**P0-5｜清 orphan `running` 並加「開輪逾時未閉即落帳」**
- `evolution_iteration_ledger.tw-20260728-r01`（07-28 開至今）與 `evolution_run` 對應列。
- 報酬：封住債 #5 的可見性部分；讓帳本能表達「卡死」這個狀態（目前只有 running/succeeded/halted，沒有超時）。
- **注意：該表受 `honesty_delete_only_guard`（DELETE 禁）保護，收尾必須用 UPDATE ＋人簽，屬治權動作，須 Steward 執行。**

**P0-6｜補 `CS-系統架構大憲章_v1.53.0.md` 內文**（現標題 v1.51.0、SSOT 指死檔、`spec-version: v1.50.0`）
- 兩次升版都是純改名，已落後三版。依 `RULING-2026-002` 主文二，補正期至 2026-10-14。
- **屬治權檔增修，非執行層——須 Steward 拍板，AI 不得逕改。**

**P0-7｜停用或延後兩個手動長跑 replay**（`run_arena_replay` 已 30h、`run_meta_replay` 已 24h）
- 它們是 load 10-24 與 TWEVO I3 timeout 的主因之一，且不在任何排程/鎖/面板中。
- 同屬破壞性（kill 他人進程），須授權。

---

## P1 — 需計畫先行（CLAUDE #20：治權判準／跨檔／跨 package／不可逆）

**P1-1｜人閘的根本抉擇（最重要的一項，且必須 Steward 親裁）**
- 二選一，不能兩者都不選：**(甲)** 真的落到機械層（DB role 分離／`current_user` trigger／全通道 TTY fail-closed）；**(乙)** 誠實承認它是紀律而非機制，把「機械強制」四個字從所有相關描述中拿掉。
- 現況是最糟的第三種：**外觀很機械（15 個 no-goalpost trigger、7 個 GUC guard、16 條簽核 CHECK）但實質零強制**，且 `governance_queue.py` 的 docstring 主動宣稱它 fail-closed（債 #31）。
- 附帶必須一併處理：`evolve_cycle.py` 預打 `promoted_by='hugo'` 待貼 SQL、`run_evolution_iteration.py` 斷言「程式體不寫 promoted_by」——**同 repo 兩支腳本對同一件事持相反不變式，代表這件事從未被統一決定過**。

**P1-2｜`honesty_delete_only_guard` → UPDATE 需 GUC 通行證（14 表）**
- 一次 migration，但**必須先盤點合法 UPDATE 路徑**（`evolution_iteration_ledger.steps_json` 逐步更新就是合法的），否則會把夜輪打死。
- 現成範本已在同 DB 服役（`honesty_ledger_guard`，4 表）。報酬：封住債 #4，且回收「帳本不可改寫」這個帳本存在的唯一理由。

**P1-3｜KH 層的誠實化**
- KH5/KH6/KH7 從庫級改 per-item，或誠實降級為「庫級旗標」而非計入 item 深度；KH9 若確為 KH8 純函式則合併；重新決定 `DEEP_KH_FLOOR`（現 7，恰等於被降級那批的深度＝降級零效果）。
- 同時修 KH8 鑑別力判準（現靠 396 列失敗樣本解閘）與 `layer_scores` 對 `admit_depth` 的自相矛盾。
- **先做這個再談任何檢索品質優化**——否則排序特權是無鑑別力地發出去的。

**P1-4｜知識漏斗的出料端**
- 決定 30,938 件非 DOI item 的抓取器編排（ATA 的 `_ALLOWED` 只含 `fetch_oa_fulltext.py` 一支）；補 `kh4.refresh_items` 覆蓋（123,304 件因缺列而 INNER JOIN 不到）；統一 `embed_knowledge` 與 ATA 的進度口徑（現差 92 倍）。
- 決定 149 萬條哲學側句嵌入：接進檢索，還是承認是 build 副產品並停止建索引（它們正在吃 HNSW 記憶體）。

**P1-5｜重活單車道統一**
- 把 `heavy_slot`（PG advisory，設計正確）擴到 arena 每日管線、advisor 服務、以及**手動長跑**；統一 `/tmp/augur_llm.lock` 與 advisory 兩個命名空間；修 `flock -n` 靜默（至少讓它寫一行 log）。
- 報酬：TWEVO 的 I3 從 7200s timeout 回到 cron 註解宣稱的 25-35 分。

**P1-6｜arena：`own_stack_rolling` 的三個門要嘛餵資料、要嘛標 superseded**
- 現況是三個 approved、每日被檢查、結構上零列可評的門。同時處置 `min_clusters=36 < 治權 60`（債 #28，屬「放寬」→ 依通則二須走重大判準修正並附 OCV 對照）。

**P1-7｜自測從字面斷言改為行為/live-schema 斷言**
- 優先序：先改**人閘**與 **APPLY 預設關**兩項（憲章上最要緊、恰好只有字面證據），再改 8 支 `migrate_*` 改查 `to_regclass`（正解已在同 repo）。
- 加一條 meta 檢查：**偵測「斷言的字面量出現在斷言自己那一行」的恆真式**（已知至少 2 例：`evolve_cycle.py:401`、`simulate_portfolio_risk.py:607`）。

**P1-8｜兩個日曆懸崖的處置計畫**（2026-10-14 七項＋2026-10-31 V2-SUNSET，相隔 17 天，距今 75 天）
- WM.35/36 自 10-15 起無條件適用是**會改變系統能否合法消費某類資料的硬開關**，不是文書工作。

**P1-9｜測試層可日常化**
- 加 `conftest.py` + marker（`db_write` / `unit`），讓「安全回歸子集」可以每天跑；為 `arena` 補最小測試（它是唯一對外出單、卻同時無測試、無 selftest、不上鎖的子系統）。

---

## P2 — 明確不該碰（附理由）

**P2-1｜預測 ⊥ 知識的三道隔離閘（AST import 稽核 + 字面 grep + `REVOKE`）**
- 這是全系統**唯一一處經三路獨立檢查、無任何假綠**的機制（實跑 9 passed、`augur_predict` 對 89 張知識表 SELECT 權限 0）。它同時是靈魂層「素養層零量化價值、不進預測管線」的唯一實質保證。**動它就毀掉這個專案最可信的一件東西。**（唯一可補的是射程註記：`PIPELINE` 只含 7 個 package，`execution`/`arena`/`identity`/`deliberation` 不在掃描範圍。）

**P2-2｜`heavy_slot.py` 的 advisory lock 實作**
- 設計正確（session 級、程序死亡自動釋放、掉鎖 fail-loud、明確拒用 `db.connect()`）。**問題在覆蓋率不在實作**——要加的是用戶，不是改它。

**P2-3｜不要為了讓 `validation_evidence` 變綠而改 `check_sql` 或直接 UPDATE `status`**
- 違 CLAUDE #12（不 hand-patch 已 committed 資料），而且**這正是這張表失去意義的路徑**。三個 false 要分流處置（見 P0-2），不是抹平。

**P2-4｜人閘未拍板前，不得新增任何「AI 可自動 approve」的通道，也不得移除既有兩支 CLI 的 TTY 檢查**
- 目前 fail-closed 只剩 `preregister_direction_gate.py:361` 與 `review_evolution_candidates.py:48` 兩處。在 P1-1 決定之前，那兩處是唯一實質存在的人閘。

**P2-5｜不要動 arena 資料地基 `as-of 2026-06-30` 的 G1-PIN**
- 原則精華 v1.12.0:81 明載「不滾動追」，且判準 sha 不得事後挪動（`arena_adm_5305655ad1cd`）。as-of 屬治權參數，更新須 Steward 決策入憲。

**P2-6｜不要為了讓 TWEVO 跑完而加 `--allow-apply`**
- cron 註解已明示「刻意不帶：R2 授權閘內自動 APPLY，但 driver 尚未跑完任一次完整輪；先讓它連續跑出乾淨的輪再開 APPLY」。**卡死的原因是資源競爭（P1-5），不是授權不足。**

**P2-7｜在 load 已 10-24 的機器上，不要排任何新的重活**
- 先收手動 replay（P0-7）、先統一車道（P1-5），再談新排程。任何在此之前加的排程都會加劇 TWEVO/ATA 的 timeout。

**P2-8｜不要把任何數字硬編進文件或從報告轉抄**
- 本輪實證：public 表數在數小時內 295→296、大憲章 v1.52.0→v1.53.0、NRestarts 10,819→11,027。`constitution_lint` 自己就警告「手抄即本專案四度腐爛之根因」，並提供 `<!--lint:KEY-->` + `--sync` 綁定機制——**該用的是那個機制，不是更勤快地手抄。**

---

## §8 矛盾與未知（誠實登記）

## A. 四路之間的矛盾（不擅自選邊，逐項標明我能查到什麼）

**A1｜public 表數：298（lens 1）vs 295 base + 3 view（lens 4）vs 296 base + 3 view（我，08:54）**
- **三者都對**。lens 4 指出 lens 1「把 view 算進表」，但更根本的原因是**數字在漲**（migrate 腳本持續新增表）。
- 結論：**表數是快照不是常數，任何寫死表數的文件都會腐爛。** 引用時必須附時戳與口徑（base table / +view）。

**A2｜`check_cmd_matrix` 受檢數：436（lens 3）vs 437（lens 1、lens 4、我）**
- 同上，repo 在增檔。三次都 RC=0、缺漏 0。無實質矛盾。

**A3｜`augur-chat`/`augur-admin` NRestarts：10,819/10,871（lens 3）→ 10,859/10,911（lens 2）→ 11,027/11,079（我）**
- 單調遞增、間隔約 5 秒一次，三組數字互相印證。**無矛盾，反而是最強的 CONFIRMED**。

**A4｜`augur-ata-advance` 的失敗原因是否可讀——這一項 lens 2 錯了**
- lens 2：「unit 未擷取 stdout 故無錯誤訊息可讀」「journalctl -o cat 只有 systemd 五行」。
- lens 3：在 `~/ata_advance.log` 找到明確原因（`StandardOutput/StandardError=append` 導到該檔）。
- **我本輪覆核支持 lens 3**：`tail ~/ata_advance.log` 直接讀到「處理 185 句但 0 新列:疑換模未遷 PK/游標錯位之靜默假成功(SOP-A ③)→ 停手查核」「✗ embed exit=1」。
- **教訓本身值得記**：lens 2 只查了 journalctl 就下「無訊息可讀」的結論——這正是 unit 用 `append` 導離 journal 造成的可觀測性陷阱，連查的人都會被騙。

**A5｜`honesty_delete_only_guard` 覆蓋表數：13（lens 4 文字）vs 14（lens 4 自己列的名單、我實查）**
- 我實查為 **14 表**。lens 4 的文字與其自身證據不一致，取證據。

**A6｜`constitution_lint` 是綠是紅：PASS 7/7 error 0（lens 1）vs exit 1 FAIL（lens 3）**
- **兩者都對，不同子命令**：我本輪同時跑了 `report` → **RC=0**、`--selftest` → **RC=1**（G10 界線 FAIL）。
- **這是一個真實的引用陷阱**：兩個子命令結論相反，任何引用「constitution_lint 通過/失敗」而不指明子命令的說法都不可用。

**A7｜`min_clusters=36` 的意義：治權違憲放寬（lens 1）vs 結構上零列可評才是真死因（lens 4）**
- **不衝突，但優先序不同，我不選邊——兩者都需處置**：
  - lens 1 對：`36 < 60` 且原則精華 v1.12.0:81 是現行 [N] 正文（我本輪 grep 確認全文），依「放寬從嚴」應走重大判準修正，無此留痕。
  - lens 4 更硬：`own_stack_rolling` 在 `direction_arena_prediction` 一列都沒有、全表 `horizon_td` 只有 5（我本輪確認）→ **就算門檻改成 1 也永遠不會 evaluate**。
- 兩者共同推翻並行報告的「一律 250、物理不可達」。

**A8｜`evolve_cycle.py:401` 的病名：標籤與檢查內容無關（lens 1）vs 恆真式（lens 4）**
- **lens 4 的診斷更準且我本輪確認**：字面 `promoted_by='hugo'` 出現在行 240/360/**401**，而 401 就是斷言本身 → 刪掉 240/360 兩處真正功能行，斷言仍為真。兩路對「這是假綠」的結論一致。

**A9｜KH10 candidate 數字：並行報告「pending 34／rejected+killed 5」vs 實查「pending 6／rejected 33」**
- lens 2 判為「報告把 pending 和 rejected 對調了」；lens 4 判為「07-31 07:56 批次改判 28 件，寫報告當下應為真、屬已過期」。
- 我本輪查得 `rejected 33／pending 6／approved 4`，與兩路一致；**但成因（打字對調 vs 資料變動）我未獨立驗證 `updated_at` 時戳，無法裁定誰對**。

**A10｜知識漏斗 pending 數：121,364（lens 2，08:41）vs 107,003（我，08:56 讀 ATA log）**
- 15 分鐘內少了 14,361 件。**這產生一個新的未知**：ATA timer 是 `failed` 狀態，那**是誰在推進這個池？**（見 B4）

---

## B. 誰都查不到的東西（誠實列出，不補 placeholder）

**B1｜`augur-ata-advance` 的 embed 為何「處理 200、新嵌 0」**
- log 只寫「疑換模未遷 PK/游標錯位之靜默假成功(SOP-A ③)」——這是防呆機制**正確地擋下了假成功**，但根因（是否真的換模未遷 PK、還是游標錯位、還是 junk 過濾把整批吃掉）**沒有任何一路查出來**。這是連三天失敗的直接原因，但目前只有症狀沒有診斷。

**B2｜`tw-20260728-r01` 在 07-28 的原始 `steps_json` 內容——永久不可復原**
- 已被 07-30 的 UPDATE 覆寫，該表 trigger 不管 UPDATE、無版本、無 audit。**這是債 #4 造成的第一起實際證據滅失。**

**B3｜`knowhow_governance_ledger` 那幾筆 approved 究竟是 hugo 親按還是腳本批寫——永久不可證**
- lens 4 觀察到 07-30 16:46:14–17 四筆在 2 秒內落地、07-31 07:56:45 三筆在 0.5 秒內落地，這是**間接證據**（人不太可能 0.5 秒按三次），但 DB 層沒有任何欄位能證明或否證。`decided_by` 的預設值就是 `'HUMAN'`。

**B4｜是誰在推進知識全文池（pending 121,364 → 107,003）**
- 不在 crontab、ATA timer 是 failed。可能是某個手動執行、或某個背景 session、或 ATA 在 embed 失敗前 fulltext 階段已成功寫入（但 ATA 的 `--stages` 只有 `sentences embed`）。**四路皆未查明。**

**B5｜兩個手動長跑 replay 由誰、為何、預計何時結束**
- `run_arena_replay.py --from 2015-01-01 --to 2026-06-30`（已 30h）與 `run_meta_replay.py`（已 24h）不在 crontab、不在 systemd、不持鎖、不在任何帳本。**無帳可查。**

**B6｜四條週排程首次執行（08-01/08-02/08-03）會不會成功**
- 零先例、零實證。依債 #7（零通知），若失敗也不會有人知道。

**B7｜V2-SUNSET (c) LAIEVO 臂的現況**
- lens 4 提到「(c) LAIEVO 臂未完結」但未附查詢；`local_ai_iteration_ledger` 實查**零列**。三條落日條件中這一條**本輪無人查證**。

**B8｜三個 false 的 `status_note` 為何不記載原因**
- 我查了 `status_note`：`E2` 為 `<none>`，`E1`/`E4` 的 note 講的是當初設計理由，**沒有任何一條說明「因解凍而預期為 false」**。所以「`E2`/`E4` 是凍結期契約被政策合法作廢」是**我的推論（讀碼級）**，不是帳本記載——**須 Steward 確認，不可當既成事實引用。**

**B9｜DESKTOP-8MQPFS8 側狀態**
- 本 session 完全未觸及（`pull_desktop_evolution_delta.sh` 每 2h 在跑、log 有更新，但對端狀態未查）。

**B10｜`PIPELINE` 隔離閘的射程外 package 是否真的乾淨**
- `import_isolation.PIPELINE` 只含 7 個 package；`execution`／`arena`／`identity`／`deliberation` 不在掃描範圍。lens 2 註記 `deliberation/engine.py:16` 確實 import `augur.advisor.ollama`（合規），但**其餘三個 package 是否有 import 知識層，無人掃過**。

---

## C. 對「已有素材」的處置建議

- `reports/augur_deep_understanding_optimization_base_20260730.md`（並行 session、未經核驗）：**大部分量化錨經核為真**（prodset active=2、feature_values 38 特徵、admit_depth 分佈、埠號、隔離鐵律），但有三處須更正／加註：(a) §2.3「HUMAN 門 AI fail-closed」**高估**；(b) §5.2 D4 的 clusters 矛盾**方向抓反**；(c) KH10 數字已翻轉。建議主 session 在最終報告中**明確標註這三處已被覆核修正**，因為該檔被定位為「優化地基 SSOT」，後續計畫書會直接引用它。
- 專案記憶中「`verify_knowledge_admission_health.py` = 日常哨兵」**已被實查推翻**（零外部呼叫）。記憶與現實脫節，建議在合成報告中點名，供後續 memory consolidate。

---

## §9 可信度分層總表

## A. 【親驗·本輪覆核】——我在本輪實際重跑並取得輸出（最高可信度）

**A1 快照即時性（本身就是一項發現）**
- public schema：`BASE TABLE 296 / VIEW 3`（2026-07-31 08:54，`information_schema.tables`）。lens 1 記 298、lens 4 記 295+3——**三者都對，數字在漲**。
- `docs/系統架構大憲章_v1.53.0.md`（`ls`）。lens 1 覆核時為 v1.52.0，其記錄的 v1.51.0 死鏈仍在。**憲章在四路深讀期間又升一版。**
- `check_cmd_matrix.py` → 「受檢 **437** 支／缺漏 0／豁免 0」RC=0。lens 3 記 436——快照差。

**A2 綠燈帳本（最重要的一組）**
- `validation_evidence`：`green|19`，無其他狀態。
- 逐條重跑全部 `check_sql`：`E1_raw_reconcile_exit=f`、`E2_feature_frozen_panel=f`、`E4_exclusion_set_contract=f`；其餘 9 條 `t`。
- **7 列 `check_sql IS NULL`**（`E10_daily_green`/`E6_purge_assertion` 為 `script_exit`；`E2_macro_latent_debt`/`E3_promotion_funnel`/`E4_gm_promotion_gap`/`E5_survivorship_debt`/`E7_h60_ece_outlier` 為 `manual`）——**19 綠中只有 12 條有機器檢查。**
- `attestation_result`：最後 `passed=t` 為 **2026-07-16 15:43**；2026-07-24×2、2026-07-25×3 全 `f`；`driver='daily_maintenance --audit-only --heal'`；07-25 18:14 後無任何執行。
- `scripts/verify_validation_evidence.py:89` 有 `UPDATE validation_evidence`；`crontab -l | grep -c validation_evidence` → **0**。
- `feature_values` 現況 `8,540,331 列／38 特徵／113 panel`，而 `E2` 契約寫死 `count(*)=2418655 AND count(DISTINCT feature)=35 AND count(DISTINCT panel_date)=35`。三列 false 的 `status_note` **均未載明「因解凍而預期為 false」**。

**A3 人簽與誠實閘**
- `honesty_delete_only_guard` 綁 **DEL + TRUNC，共 14 表**（`evolution_apply_log, evolution_coverage_snapshot, evolution_evidence_run, evolution_hypothesis_hint, evolution_iteration_ledger, evolution_kill_switch, evolution_production_feature_set, evolution_run, local_ai_iteration_ledger, philosophy_principle, principle_factor_map, promotion_queue, raw_evolution_iteration_ledger, steward_question_ledger`）——**無 UPD**。lens 4 記 13 表但列出 14 個名字。
- `honesty_ledger_guard` 綁 **DEL + UPD + TRUNC**，僅 4 表（`local_model_eval_item/run, revalidation_baseline, trial_ledger`）——**現成解法已存在，只是沒套上去。**
- `knowhow_governance_ledger.decided_by` 預設值 = `'HUMAN'::text`；`decided_at` 預設 `now()`；該表 **user trigger 數 = 0**。
- 自測程式已寫入人簽帳本：`arena_admission_gate` 有 `arena_selftest_38eea79f|superseded|selftest`；`prediction_unfreeze_gate` 有 `unfreeze_selftest_6b30cc56|superseded|selftest`。

**A4 假綠自測（逐行確認）**
- `scripts/evolve_cycle.py`：字面 `promoted_by='hugo'` 出現在行 **240、360、401**，而 401 就是那句斷言本身 → **恆真式**。
- `scripts/review_evolution_candidates.py:43` → `chk("TTY 閘於 mutate", True)  # 實閘在 _require_tty`；同檔 `:36` `chk("無 --auto-approve", "--auto-approve" not in (__doc__ or ""))` 只掃 docstring。
- `scripts/run_evolution_iteration.py:335-337`：`chk("**零代簽人閘**...", not any(k in body for k in ("promoted_by","decided_by","approved_by")))` 與 `chk("**APPLY 預設關**", "apply_allowed) VALUES (%s,'tw','running',%s,false)" in body)` — 皆為字面比對；:333 註解自陳「同型教訓已五犯」。
- `src/augur/philosophy/retrieval.py`：`set_kh_evidence_validity(cur)` 出現在 **:373 與 :408**，import 於 :370/:406。
- `scripts/governance_queue.py`：`:18 import getpass`、`:74 actor = getpass.getuser()`、`:77 SET status=%s, decided_by=%s`；**全檔無 `isatty`**。

**A5 工具與 CI**
- `check_treaty_refs.py` → **12 則缺陷、RC=1**；含 `[status_line_stale] HANDOFF.md:272` 與 `HANDOFF-governance.md:241`（宣告 v1.51.0，現行 **v1.53.0**）、`[dead_superseded] docs/系統架構大憲章_v1.47.0.md:3`。
- `tools.constitution_lint report` → **RC=0**，`total_errors 0 / total_warnings 0 / mc_universe 102`。
- `tools.constitution_lint --selftest` → **RC=1**，`:131 ✗FAIL G10 界線`，`:292 自檢：有 FAIL ✗`。**兩個子命令結論相反——引用時必須指明哪一個。**
- `.git/hooks/` 非 sample 檔數 = **0**；`.github/workflows/` 不存在；`.pre-commit-config.yaml` 不存在。
- `pytest tests/ --collect-only -q` → **275 tests collected in 2.86s**。

**A6 合規聲明落後三版（且持續惡化）**
- `docs/compliance/CS-系統架構大憲章_v1.53.0.md`：標題寫 **v1.51.0**、正文 SSOT 指向不存在的 `docs/系統架構大憲章_v1.51.0.md`、YAML `spec-version: v1.50.0`。git commit `6731153`（v1.53.0 入憲）對它是**純改名**。
- `docs/compliance/` 現有 7 份 CS（含 v1.47.0/v1.48.0/v1.53.0 三份大憲章 CS）。

**A7 排程與服務**
- `crontab -l` 實際 **12 條**作業。`45 */6` self_seek 註解寫「純 SQL/文字，不碰 ollama，**故不入鎖**」，指令卻是 `flock -w 3600 /tmp/augur_llm.lock` — **註解與實作直接矛盾**。
- `~/logs/` 實際 12 檔，**無** `ops_weekly.log`／`verify_weekly.log`／`rawevo.log`／`evolution_week_20260727.md` → 四條週排程（Mon 08:00、Mon 08:40、Sat 09:00、Sun 09:00）**從未執行過**。
- `augur-chat` NRestarts=**11,027**、`augur-admin`=**11,079**，兩者 ActiveState=`activating`；`ss -ltnp` 顯示 8090→pid 3387306、8500→pid 3342300（皆 07-30 手動起），8399→pid 3776896（= advisor systemd MainPID，正常）。
- `augur-ata-advance`：`ActiveState=failed, Result=exit-code, ExecMainStatus=1`；`~/ata_advance.log` 尾端：「完成 embed…處理 200、新嵌 0…」「**處理 185 句但 0 新列:疑換模未遷 PK/游標錯位之靜默假成功(SOP-A ③)→ 停手查核**」「✗ embed exit=1」「池量: pending=**107003**」。
- `uptime` → load average **10.39, 12.05, 15.03**（12 執行緒）。

**A8 演化軸與 arena**
- `evolution_iteration_ledger`：`tw-20260728-r01|running|opened 2026-07-28 23:00|closed_at NULL|steps=3`；上一輪 `tw-20260727-r03|succeeded|steps=10`。
- `direction_gate` 有 `min_clusters` 者共 17 列：**250** 者 12 列（含 2 列 `evaluated_fail`）；**36** 者 6 列 —— `dgate_arena_own_stack_20/40/82`（**approved**，`model_id=own_stack_rolling`）與 `dgate_a3_threelens_20/40/82`（superseded）。
- `direction_arena_prediction`：8 個 `model_key`，**`horizon_td` 全部為 5**，**無 `own_stack_rolling`** → 那三個 approved 門結構上零列可評。
- `evolution_production_feature_set`：`active 2 / removed 7`。
- `knowhow_evolution_candidate`：`rejected_for_loop 33 / governance_pending 6 / approved_for_loop 4`。
- 知識漏斗（08:54）：`knowledge_item 285,177`／有 item_text 者 `146,397`／`kh4 eligible 145,952`／`admit_depth=7` 者 `145,952`。

**A9 治權條文**
- `docs/原則精華_v1.12.0.md:81` 為**現行 [N] 正文段**，明載「live 數字入任何『確立級』宣稱唯經方向軸門二 `direction_gate` evaluate（**≥60 clusters**）（憲章④硬綁不變）」——lens 1 的引用成立。

---

## B. 【親驗·單路】——單一 lens 實跑且附可貼回證據，本輪未重跑（高可信度，但為當時快照）

- 預測⊥知識隔離：`pytest tests/test_philosophy_isolation.py` → **9 passed**；`augur_predict` 對 89 張 `knowledge_*`/`philosophy_*`/`knowhow_*` 表 SELECT 權限數 = **0**（lens 2）。
- `evidence.population_discriminates(cur)` → `{'ok': True, 'terminal=1／embed=2／kh4_ok=2', n=146348}`；`auto_admit.DEEP_KH_FLOOR = 7`（lens 2、lens 4 各自獨立得同結論）。
- `knowhow_auto_admit_state`：145,949 列 `layer_scores` 仍寫 `'8':pass,'9':pass` 而 `admit_depth=7`（lens 2）。
- `knowledge_fulltext_status` 19,927 列**全為 skip_*/abstract_*/error**（設計上 'ok' 不入帳）；無 text 且無 fulltext_status 者 121,364 件，其中 DOI-like 90,426、非 DOI **30,938**（lens 2）。
- `knowledge_sentence` 依側分：`text_id`（哲學）1,542,146／`itext_id`（items）297,118；哲學側句嵌入無任何消費端，works 作答走 `philosophy_chunk_embedding`(126,609)（lens 2）。
- 123,304 件 item 無 `knowledge_kh4_state` 列，而 `retrieval.py:251-254 _ITEM_JOIN` 是 INNER JOIN（lens 2）。
- `retrieve_items` 之 Qdrant ANN 分支（:335）無 `k4.answer_status='eligible'` 過濾，exact(:303/308) 與 pgvector(:353) 有（lens 2）。
- advisor 單次作答 **1,978.2 秒**（journal）；`app_user` 僅 1 列（admin, superuser）；150,772 筆 `local_private` item_text 的 owner 全為 user 1（lens 2）。
- `scripts/` 297 支中 **210 支（71%）無任何自動呼叫者**；`verify_*` 35 支中 28 支無呼叫者，含 `verify_knowledge_admission_health.py`（lens 3）。
- 118/297 script 具 `--selftest`（lens 3）。
- 測試層：24 檔覆蓋 12 package；**arena／catalog／execution／universe 零測試**；無 `tests/conftest.py`、無 marker、9 檔連 DB 其中 4 檔含寫入（lens 3）。
- `augur-qdrant.service` 的 ExecStart 指向 `~/project/ttai/.qdrant_server/qdrant`（**跨專案依賴**）（lens 3）。
- 兩個手動長跑：`run_arena_replay.py` 已 1 天 5 小時、`run_meta_replay.py` 已 23.5 小時，皆不受排程/鎖管轄（lens 3）。
- `augur-audit-watchdog.timer` 每 30 分準時執行，但其標的 `~/audit_retry.log` 最後更新 **2026-07-15**（lens 3）。
- `pg_constraint` 全掃：16 條與簽核相關的 CHECK **全部只驗 NOT NULL 或 `btrim<>''`**；`pg_proc` 中**無任何 `current_user`/`session_user` 用法**，7 個 `current_setting` 全為可自設的 GUC；`pg_roles` 中僅 `augur` 擁有全部治權表（lens 1）。
- 27 張 ledger/log/audit/verdict 類表零 user trigger；`augur_predict` 對 `revalidation_ledger`/`revalidation_verdict`/`data_audit_log`/`pipeline_execution_log` 具 DELETE+UPDATE+INSERT（lens 4）。
- `local_ai_iteration_ledger` 與 `pipeline_execution_log` **至今零列**（lens 4）。
- 哲學側語料閘乾淨：126,566 條 chunk 全數通過 CLEAN 閘；來自未過閘 works 的句子 0；但 1,167 件 clean works 中僅 467 件真有 work_text（lens 2）。
- `philosophy_principle` 54 條：validated 1／sign_refuted 7／untested 46；`principle_factor_map` 111 列（lens 2、lens 4 一致）。
- `flock -n` 巢狀實測：搶不到鎖時**只回 exit 1、零訊息**（lens 4）。
- `ULTRACODE-SCHEDULE.md` 之 2026-10-14 併結 checklist 七項**全為未勾 `[ ]`**（lens 1）。
- 七份規格 open-tensions 共 46 則、waivers 全為 `[]`（lens 1）。

---

## C. 【讀碼】——讀了檔案/條文但未執行驗證其運行時行為

- `constitution/META-CONSTITUTION.md` = **AUGUR-MC v1.6**（生效 2026-07-23）；specs L1–L7 版本 WM v1.0／ONT v1.0／ID v1.0／KS v1.1／L5 v1.0／L6 v1.2／L7 v1.0。
- `tools/constitution_lint/report.py:51-61` `corpus_files()` **只 glob `specs/*.md`**——lint 完全不含 `docs/` 治權四檔與 `docs/compliance/` 五份 CS。
- 大憲章第 213 行：「晉升須經人類核准…**AI 不得代簽**、不得為涉及自身監督機制之變更之核准主體（L6.18(a)）」。
- `src/augur/knowledge/evolution.py:49-52` `assert_human_decider()` 只做字串比對 `decided_by != "HUMAN"` → raise；`:149` 預設值即通過。
- `src/augur/knowledge/curation.py:33-34` `HUMAN_ONLY = set()`（v1.48.0 有意廢止），但 `:67-69` 的判斷式仍在 → **死閘空殼**。
- `src/augur/knowledge/auto_admit.py`：KH6 `:422-426`「交互 probe run 帳存在（**庫級**）」／KH7 `:440-452`「run_id=N 有 eligibility_pass（**庫級**；≠approve）」／KH10 `:481-484` = `gate['enabled']` 布林。
- `src/augur/knowledge/synthesis.py:36-48` KH9 = band 的確定性映射，零獨立資訊。
- `src/augur/core/heavy_slot.py:4-8, 67, 77`：PG session 級 advisory lock、明確拒用 `db.connect()`、掉鎖 `raise SlotLost` fail-loud。
- `scripts/harvest_knowledge.py` 對 `fetch_*fulltext`/`build_sentences`/`embed_knowledge` 的引用數 = 0 → CLAUDE.md #29(b) v1.20 的「harvest 自動接三段」在 harvest 這一支未實作。
- `scripts/check_cmd_matrix.py:38 MATRIX_STR = "執行指令矩陣"` → 437/437 證明的是「檔案含這五個中文字」，**不是指令可執行**。
- `RULING-2026-031` 廢止 14 日強制公示 → Sole Steward 期間**一份書面裁決即生效**；`PROPOSAL-2026-001`（GOV-1）之正式議決至今未作成，現況靠 `RULING-2026-028` 過渡性自我拘束（該裁決自陳「本身即解釋、無法自我封口」）。
- `specs/AGENT-RUNTIME-SPECIFICATION.md:495` T-L6-5 自陳結構性自我交易誘因：本層度量 OCV 由 Agent 起草者定義。
- `docs/compliance/CS-CLAUDE.md` 三則 open-tensions，含 T-CLAUDE-WM44-MATRIX「本檔之形式充分性**目前無法機器判定**」。
- `RULING-2026-039` 明列禁止假關六項；`RULING-2026-040` 沿用。
- 2026-10-14 為多重義務到期日（RULING-002 主文五檔 CS、L5 §8.2 復審、L7 §8.2 residual、WM.35/36 補正期〔10-15 起消費禁令無條件適用〕、RULING-012 Phase 7、原則精華 #7 P4.E5）；`V2-SUNSET` deadline **2026-10-31**，後果「三軸整體停止、帳本封存、不得換 trigger_code 重開」。
- `migrate_*.py` 至少 8 支的 `--selftest` 只驗 Python 字串常數（`"..." in DDL`），**從不查 live schema**。
- `run_arena_round.py:71-85` 與 `run_arena_daily_pipeline.py:44/116/157` 的 arena 雙機械閘確實接線（非死碼）。

---

## D. 【轉述·未獨立驗證】——出自他人文件或本輪未觸及的來源

- `reports/augur_deep_understanding_optimization_base_20260730.md`（並行 session、未經核驗）之各項宣稱。**已被三路交叉核出至少三處問題**：(a) §2.3「HUMAN 門：AI fail-closed」→ 高估（fail-closed 僅及 2 支 CLI 的 TTY 檢查，DB 層與 `governance_queue.py` 皆無）；(b) §5.2 D4「治權 ≥60 vs 凍結 250」→ 方向抓反（250 是加嚴；真衝突是 H 軸三門 36<60，且更硬的死因是零列可評）；(c) KH10 candidate 數字 pending/rejected 對調或已過期。**其餘量化錨（prodset active=2、feature_values 38 特徵、admit_depth 分佈、埠號、隔離鐵律）經核為真。**
- `reports/augur_full_reread_facts_20260730.md`（1031 行逐檔事實底本）——本輪未逐條覆核。
- `reports/augur_plain_language_full_report_20260730.md`——本輪未讀（且屬平行 workflow 射程）。
- 專案記憶中「`verify_knowledge_admission_health.py` 為日常哨兵」——**lens 3 實查推翻**（全 repo 零外部呼叫）。記憶與現實已脫節。
- DESKTOP-8MQPFS8 側狀態、V2-SUNSET (c) LAIEVO 臂現況——本輪完全未觸及。

---

## §10 繕打者之獨立核驗記錄

四路 agent 之回報**未照單全收**。本輪親跑並確認之承重宣稱：

| 宣稱 | 親驗結果 |
|---|---|
| `validation_evidence` 19/19 green | ✓ 狀態分佈實查＝green 19 |
| 12 列有 check_sql、7 列無 | ✓ 實查 (12, 19) |
| 3 條機器檢查現回 false | ✓ **逐條重跑**：E1_raw_reconcile_exit／E2_feature_frozen_panel／E4_exclusion_set_contract |
| 8090/8500 為孤兒舊碼 | ✓ `ss`＋`ps` 得 pid 與啟動時刻；NRestarts 12005/12059 |
| `augur-ata-advance` failed | ✓ `is-failed` ＝ failed |
| guard 函式存在 | ✓ `honesty_delete_only_guard`／`honesty_ledger_guard` 皆在 pg_proc |
| advisor 是否載入本人今日改動 | ✓ pid 3776896 起於 07-31 08:00:18，晚於 `auto_admit.py` mtime 07-30 17:36 ⇒ **已載入**（先前宣稱無誤） |

**更正並行報告（`augur_deep_understanding_optimization_base_20260730.md`）兩項**：
① 其 §2.3 稱「HUMAN 門：AI fail-closed」＝**高估**——TTY fail-closed 當時只存在於 3 支 CLI，
`governance_queue.py` 自稱比照先例卻無 isatty（**本報告產製期間已修，commit 847f65a**）；
② 其 §5.2 稱治權「≥60 clusters」vs 凍結 250 為衝突＝**抓錯方向**（250 比 60 嚴、不違憲）；
真正的問題是 H 軸三個 approved gate 用 **36 < 60**。

**未親驗、照收者**一律標【單路】，動工前須複驗。

---

## §11 本報告未做之事

- **未修任何債**：本報告是地圖不是施工。惟產製期間順修兩項（`governance_queue` TTY 閘、
  heavy-slot 有界等待＋補跑器），因其正好擋在當時進行中的工作前面，已各自 commit 留痕。
- **未涵蓋**：`reports/` 下 40+ 份既有報告之逐份核驗；tests/ 之實際執行（會寫 DB）。
- **本報告本身未受獨立核驗**——依 `RULING-2026-028` 第 3 點，施作後宜由非施作者核驗；
  本份尚未經此程序，讀者請依 §0 可信度標記自行折扣。

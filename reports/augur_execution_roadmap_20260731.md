# Augur 執行行程計畫書（2026-07-31）——依 r2 深化理解逐步執行

> **性質**：[I] 執行計畫（不創設治權判準；凡涉判準變更者一律列為拍板點、不由本計畫決定）
> **依 CLAUDE #20 計畫先行**：本計畫觸及高風險門檻（跨 ≥2 治權檔、含不可逆項、跨 ≥3 package），
> 故已行**多視角平行對抗審查**（workflow `wf_ae21c531-20e`：5 路蒐集＋2 路對抗，7 agent／348 工具呼叫／0 錯誤），
> 發現表留痕於 §7。**本計畫骨架經對抗審查後大幅重排**——原骨架有三個結構性排序錯誤（§7 A1–A3）。
> **依憲章 v1.39.0 計畫完整性**：附 **(a) table schema**（§5）與 **(b) python 程式規畫**（§6），表與程式雙落實。
> **上游**：`reports/augur_deep_understanding_r2_20260731.md`（r2 獨立核驗）→ `augur_deep_understanding_20260731.md`（基線）。
> **產製基準**：repo HEAD `7358233`；現況取樣 2026-07-31 11:20–12:45（重開機 11:09 後）。**引用前重跑附註指令。**

---

## §0 授權鏈留痕（CLAUDE #26 授權四要件；Steward 2026-07-31 12:0x 拍板「照你的版本」）

| 要件 | 內容 |
|---|---|
| **(a) 範圍** | 本計畫 **W0–W2 之執行層項目**：改碼、改排程檔（`install_cron.sh`／`install_services.sh` SSOT）、跑唯讀驗收、改動後重啟對應常駐服務並實測（#7）、每波封存 push（#14 已明示授權）。**不含** W3 各項與 §0.1 所列四類 |
| **(b) 結束條件** | **一波一停**——每波完成即回報並等 Steward 放行下一波；**逾期自動失效＝2026-08-07**（逾 7 日未續授權即失效） |
| **(c) 可撤銷** | Steward 隨時收回；收回時停於當前可續狀態，不留半完成之不可逆狀態（#28 resume-safe） |
| **(d) 計畫參照** | 本檔 `reports/augur_execution_roadmap_20260731.md` |
| **授權時點** | 2026-07-31 12:0x（對話拍板；繕打者記錄，非代簽） |
| **自動鏈上限**（#26 OCV C／D） | **最大連續無人介入＝一波**。本計畫**不新增**自我喚醒鏈；新增排程之項目（W1-4／W1-6／W2-3）各附「人類介入點數／否決可達性／揭露比例／最大自動鏈長」前後對照並聲明未弱化（單向棘輪） |

### §0.1 本授權涵蓋不到之四類——碰到即停下問

1. **人簽欄**：`approved_by`／`decided_by`／`promoted_by`／`signed_by` 之寫入一律 hugo 親跑，AI 僅備 SQL。
2. **破壞性或不可逆**：DDL `--apply`、殺進程、`push --force`、刪表——先出 `--check`／`--dry-run`，Steward 確認才 apply。
3. **治權判準變更**（#19／MC §8.1）：改條文、門檻、判準值。**AI 只能草擬呈案**。
4. **§2 之 12 個拍板點**。

### §0.2 封存節奏

每波一封存點（`archive-YYYYMMDD-w<N>-<slug>`）。前置固定四步：`sync_memory.py export` → 密碼掃描 →
`archive_push.sh --dry-run` 預覽 → 正式封存。

---

## §1 現況一句話

這專案不缺工具、不缺條文、不缺紀律——缺的是「條文／工具」與「會自己跑的機械閘」之間那段接線。
排序原則：**報酬 ＝（失敗會沉默污染多少下游）×（修法多便宜）**。故 W0／W1 全部集中在
「讓紅燈會亮」與「讓剛生效的治權名實相符」，而非任何新能力。

**但對抗審查改變了三件事**：(1) 有一個**正在增生**的洞（I3 逾時）比所有存量債更急；
(2) 「讓紅燈會亮」的前提——**告警 sink 不存在**——本身是拍板點；
(3) 兩個日曆懸崖中，**10-31 SUNSET (a) 已在算術上關閉**，故「是否接受落日」不能等到 W3。

---

## §2 拍板點（12 項；原骨架只列 4 項，對抗審查指出 8 項被當執行項偷渡）

> 標「**阻塞**」者為關鍵路徑，未裁則該波不能動工。

| # | 拍板點 | 選項／要決定什麼 | 阻塞 |
|---|---|---|---|
| **D1** | **SUNSET 落日是否可接受**（併同 D2 一次議決） | 三路現況：**(a) 已物理不可能**——`direction_arena_prediction` distinct `pred_date`＝**6**（07-15～07-30、12 交易日 ≈ 0.5 cluster/日），到 36 需再約 60 交易日、到 250 需約 488 交易日；**(b)** 唯一活路但產能管道每晚崩（見 W0-0）且 `apply_allowed=false`；**(c)** 見 D2。若 D2 不開，三路同時關閉、10-31 只剩落日一種結局 | **W0-0／W3-D** |
| **D2** | **`apply_allowed` 是否開** | 不開則 (b) 亦死。cron 註解原意是「先讓它連續跑出乾淨的輪再開」——而它從未跑完一輪乾淨的（W0-0 是前提） | **同上** |
| **D3** | **SUNSET (c) 之尺是否已依靈魂 v1.10.0 判準三失效** | 對抗審查實測：唯一同時具受測臂與 robot 臂的尺上 **robot 1.000 嚴格勝過 behavior 0.967**。靈魂判準三逐字「橡皮圖章式的一律同意必須落在地板以下——若全部同意就能得高分，該尺無效」⇒ 該尺無效；但 SUNSET (c) 凍結文字**不含 robot 臂**，故仍可在一把靈魂判死的尺上宣告達成。凍結判準不得事後挪動（no-goalpost），正解可能是「另立新尺並凍結」而非改 SUNSET | **W3-E** |
| **D4** | **KH0 判準三層打架，取哪一層** | 憲章 :164 條文＝「本地 AI 對其內文之基本理解」／:176 機械判準＝「有 `knowhow_auto_admit_state` 列」／code 實作＝「`item_text` 在庫」。**甲**：標題在庫即 pass（與既有 146,348 件同標準，成本 ~16 分鐘）；**乙**：須經本地 AI 產生理解物件（成本 7–43 天獨佔車道）；**丙**：只補列不改判準——**丙須明文否決**（會產生 138,780 件 verdict=fail 的鏡像假綠） | **W3-A 全部** |
| **D5** | **OnFailure sink 選型** | 本機**無 mail／msmtp／sendmail**，只有 `notify-send`（headless 未必送達）。選項：本地 log＋DB 告警帳本（零外部依賴，合 #28）／外部推送（新外部依賴）。cron 側需另一套等價物 | **W1 全部**（沒有 sink，紅燈亮了也沒人看見） |
| **D6** | **FinMind 放量授權**（attestation 恢復） | `audit_selfheal.sh:11-18` 呼叫真實 FinMind API、內含 48 輪重試＋30 分休養 ⇒ 屬 #24／#25「API 大規模落地」護欄。須依 #26 四要件明示；且訂閱狀態現為 UNKNOWN。**這是 10-14 D-PRIN-2（原則精華 #7 P4.E5）的上游** | **W1-5** |
| **D7** | **`honesty_*` guard 統一模式** | 庫內已有**兩種不相容範式**：GUC 通行證（`honesty_ledger_guard`，5 表）vs forward-only（`sim_candidate_forward_only`）。選哪種是判準決策。另需裁 `evolution_kill_switch` 是否豁免——它的 `state` 就是靠 UPDATE 切 clear/halt，擋死＝**緊急煞車失能** | **W2-1／W1-7** |
| **D8** | **治權檔增修呈案**（原 W0-4／W0-5） | 依 MC §8.1「Agent 不得參與修憲與解釋」，AI 只能草擬。含：專章 :240 殘留矛盾句（就地補正 or 另開 proposal？凍結提案文與生效檔本已不同 md5，改檔後兩者永久各執一詞，「怎麼記」是治權決定）、GOVERNANCE-MAP 補登專章、README:30／原則精華:7 版號 | **W0 收尾** |
| **D9** | **`validation_evidence` 人裁欄位保全＋manual 五條複核期限** | (i) `verify_validation_evidence.py:88-90` 的 `status_note=COALESCE(%s, status_note)` 在 sql 路徑**新 note 恆非空**⇒ **首跑即覆寫 hugo 的人裁文字**（`E1_raw_reconcile_exit` 的 note 內含「2026-07-14 hugo 拍板」）；該表零 trigger、無 pre-image。(ii) 19 條中 **5 條 `check_type='manual'` 被 run() 直接 skip、永遠 green**、`last_verified_at` 最新只到 07-15 ⇒ 26% 對紅燈永久免疫。需訂「人裁有效期」規則 | **W1-2／W1-3** |
| **D10** | **E2／E4 是 retire 還是 re-baseline** | 凍結期契約被「解凍→live 增量」合法作廢（契約寫死 35 特徵／2,418,655 列，live 已 38／8,540,331）。**不得直接 UPDATE status 湊綠**（違 #12、P2-3） | **W1-3** |
| **D11** | **`lending_fee_rate_mean_20d` 處置** | prodset 僅有 2 個 active 之一、17,072 列、**全 repo 零產生器**。選項：回填產生器／走正式 demote 留 `apply_log`／標 known-debt 暫留。**注意：退出 active 會使 SUNSET (b) 分子由 2 變 1** | W2-8 |
| **D12** | **專章 §4.5 三筆自測人簽處置** | (i) 加註記列／(ii) 重簽／(iii) 僅於專章記明。實查三筆仍原封未動 | — |

---

## §3 分波行程總表

> **時間預算誠實化**（對抗審查指出原估不成立）：**今日是週五**。W0 五項中含兩項治權呈案（未必今日有 Steward 在場），
> 實際約半日；原「W1 本週」不成立，改稱**第一輪（08-01～08-07）**。

| 波 | 名稱 | 時窗 | 項數 | 前置 | 封存 tag |
|---|---|---|---|---|---|
| **W0** | 止血＋名實相符（純程式） | 今日 07-31 | 4 | 無 | `archive-20260731-w0-…` |
| **W0′** | 呈案（Steward 決定） | 今日起 | 3 呈案 | 無（AI 只草擬） | 併 W0 |
| **W1** | 讓紅燈會亮 | 08-01～08-07 | 12 | D5 sink 先裁 | `archive-2026080X-w1-…` |
| **W2** | 止血既有惡化 | 08-08 起 | 11 | D7／D11 | `archive-…-w2-…` |
| **W3** | 需獨立計畫書 | 另案 | 5 | D1–D4 | — |

---

## §4 各波逐項施工單

### W0｜今日・止血與名實相符

**W0-0｜I3 逾時根因（最急；正在增生中）** ⚠
- **現況實測（12:43）**：pid 1709 `run_philosophy_evolution.py --local-gates` 於 **11:20:24** 起跑，
  `run_evolution_iteration.py:130` 硬寫 `timeout=7200` 且 `TimeoutExpired` **完全不被捕捉**
  ⇒ **13:20:24 必崩**，產生第 7 個殭屍列。昨夜 TWEVO 已因此崩（`~/logs/twevo.log` 尾段 Traceback 實見）。
- **這支就是 SUNSET (b) 唯一的產能管道，它從未跑完一輪乾淨的。**
- **做法**：(a) 先量 `--local-gates` 真實牆鐘（讀歷史 log，**不沿用 cron 註解的「25-35 分」**——該註解本身是錯的）；
  (b) `_run_cmd` 補 `TimeoutExpired` 捕捉 → step 記 failed、`evolution_run` 回填 failed（**這才是止血**）；
  (c) timeout 改為可組態並對齊實測；(d) 同時修 `install_cron.sh:52-53` 錯誤註解。
- **13:20 前的抉擇**（須 Steward，屬 §0.1 第 2 類）：讓它自然崩（多一個殭屍、但不干預進行中作業，
  合 r2 P2-9）／或提前中止。**我的建議：讓它崩**——干預進行中的 drain 會踩 P2-9，且崩了正好給 (a) 一個乾淨的實測樣本。

**W0-1｜`governance_queue.py` Enter 回退**
- `:89-91` `typed or default`（default＝`getpass.getuser()`）改為空輸入即拒；**同步改 `:167`**
  ——現行自測把「空輸入回退 OS 帳號」鎖成通過條件，不同改就立刻 FAIL。
- 這是讓**今日剛生效的專章 §4.4 補強1**（「須 TTY＋親手打簽名」）名實相符。

**W0-2｜`check_treaty_refs.py` 補錨（必須同一次改三處＋補自測）**
- (a) `FAMILY_ALIASES`：靈魂→系統核心思想、憲章／大憲章→系統架構大憲章；
- (b) `LEGACY_MARKERS` 補「史述」——否則 `HANDOFF-governance.md:241`（同行既含 STATUS_MARKER「現行版」
  又刻意保留史述版號）立刻**假陽性**；更穩的判準是「取行內最大版號與現行版比」；
- (c) `:131` entries 擴入 docs 全部治權檔＋CLAUDE.md，裸版號另立規則；
- (d) `_selftest` 合成樹補兩例（縮寫落後須被抓／同行史述須豁免）。
- **gate**：`--selftest rc=0` 且全掃 rc=0 才算完成——這是 W1-12（pre-commit）的上游。

**W0-3｜`report_triple_evolution_week.py:39`** 之 `"cluster N/60"` 改讀門內凍結 `min_clusters`。
週日 09:00 是它的**首跑**，不改則從第一份儀表起就印錯門檻。

### W0′｜呈案（AI 草擬、Steward 裁）

- **W0′-a｜D8 治權檔增修呈案**：專章 :240 殘留句＋GOVERNANCE-MAP 補登＋README:30／原則精華:7。
  建議**只改 :240，不動 :111／:223**——那兩處是有日期的親驗快照史述，改它反而是竄改記錄。
  順序：**W0-2 先於改數字**，且 commit 訊息須留痕「本次為手抄權宜，綁定機制待 lint corpus 擴至 docs/（債 #16）」——
  否則字面上踩 P2-8。
- **W0′-b｜D1＋D2 SUNSET 三路算術呈案**：附上述三個數字與 (b) 路徑阻塞清單。
- **W0′-c｜D5 sink 選型呈案**。

### W1｜第一輪（08-01～08-07）・讓紅燈會亮

> **依賴順序已依對抗審查重排**。W1-1～W1-3 是所有後續的地基。

| 項 | 內容 | 前置 |
|---|---|---|
| **W1-1** | **建 sink**：`augur-alert@.service` ＋ 掛全 13 unit `OnFailure=`；cron 側加 `\|\| <alert>` 等價物 | **D5** |
| **W1-2** | **人裁欄位保全**：先 `pg_dump -t validation_evidence` 存證；改 code 讓機器判定寫 `machine_note`／或 UPDATE 只寫 status＋last_verified_at | **D9** |
| **W1-3** | **三條 false 分流**（E1 真退步／E2·E4 待 D10）＋**manual 五條處置** | D9／D10 |
| **W1-4** | **掛 `verify_validation_evidence` 日排程 07:00**——指令**必須兩段式** `--run && --strict`（`main()` 分派先看 `args.run`，`--run --strict` 會吞掉 strict、且 `run()` 無條件 return 0 ⇒ 單掛＝掛一盞永不紅的燈）；另須加 `--with-scripts` 否則 2 條 script_exit 永不驗 | W1-1～W1-3 |
| **W1-5** | **attestation 恢復（診斷已更正）**：真因**不是**「沒有觸發器」，而是 `audit_watchdog.sh:15-20` 只抓 `~/audit_retry.log` 最後一條 attestation 行、**不論時效**——該檔 mtime 停在 **07-15** 且最後一行是 PASS，故 watchdog 已連續 16 天／今日 442 輪回報「已綠」。(a) 一行級＝判態改讀 **DB `attestation_result` 最近一列 `run_at` 是否在 N 小時內**（訊號源與判準源合一）；(b) selfheal 恢復＝**D6 拍板後**才動 | **D6** |
| **W1-6** | **`install_cron.sh` 對帳**：live crontab 的 TWEVO 行帶 `--slot-wait 10800`，但 SSOT `:57` **沒有**——`--apply` 是整段替換式，跑一次就把有界等待改回預設。**必須先於任何新增 cron** | 無 |
| **W1-7** | **殭屍回填設計**（只設計不動資料）：判準＝`started_at < $(uptime -s)` OR pid 不存在 OR 逾 N 小時無心跳。**不可無條件標 failed**——run_id=16 是活的。順帶 reconcile `heavy_slot_holder_log`；另加 OnBootSec「開機後對帳」unit（否則每次重開機復發） | W0-0 |
| **W1-8** | **Qdrant ANN 洩漏修**（由 W2 上提——這是**現行**洩漏非待辦債）：`retrieval.py:335` 補 `answer_status='eligible'`；與 `:408` 死碼、`:373` 快取 `_at` **併同一 commit**（同檔同一次重啟）。**驗收含 `systemctl --user restart augur-advisor augur-chat` ＋實跑一則檢索**（#7） | 無 |
| **W1-9** | **靈魂六判準落差表**（純唯讀、零風險）：對「判斷力」六判準逐項列現有機制落差 | 無 |
| **W1-10** | **WM.35/36 射程盤點**（純唯讀）：查清消費禁令針對哪類資料、系統現在有無在消費、10-15 後哪條管線會違規 | 無 |
| **W1-11** | **看顧表（按日曆釘死）**：07-31 23:00 TWEVO → 08-01 04:00 ata-advance（f143aa6 排程級首驗）→ 08-01 09:00 RAWEVO → 08-02 04:30 knowhow-refresh → 08-02 09:00 週儀表 → 08-03 08:00/08:40 維運＋自測。**每項等待前先寫下預期輸出＋失敗判準** | W1-1 |
| **W1-12** | **pre-commit（最末）**：三步——① G10 界線 FAIL 先處置（屬治權解釋、須呈 Steward；裁前只掛 `constitution_lint report`）；② 把 W2-6 提前同批（否則 W2-6 落地當天 repo 被封鎖）；③ 用純 `.git/hooks/pre-commit` shell（零新依賴，#28），並在 `install_*.sh` 提供安裝入口（hooks 不隨 git 走） | W0-2／W2-6 |

### W2｜第二輪（08-08 起）・止血既有惡化

W2-1 guard UPDATE 通行證（**抽成獨立子計畫**，見 §7 A3）／W2-2 KH8 病 A＋病 B（**病 A 優先**）／
W2-3 fulltext fetch（**須先補 #24 等價防護**）／W2-4 `check_cmd_matrix` `__init__.py` 豁免收窄（與補矩陣**同 commit**）／
W2-5 `feature_candidate_values` guard（須先盤點重建路徑有無 DELETE/TRUNCATE）／W2-6 同 W2-4／
W2-7 heavy_slot selftest 換測試鎖名＋ROLLBACK（**保留真寫入**，改回字面斷言會退回假綠）／
W2-8 D11 處置／**W2-9 N4 INSERT 旁門**（簽核 trigger 擴含 INSERT ＋ `local_model_version` 補 CHECK；
**與人閘甲乙兩案皆相容、不預判 D 拍板**）／W2-10 debt #13 驗證器接線／W2-11 lint corpus 擴至 docs（債 #16）。

### W3｜需獨立計畫書

W3-A KH0 履行（**第一節改為判準呈案 D4，非車道算術**）／W3-B 人閘根本抉擇（**四條通道並列**：
TTY-Enter／pty／INSERT 旁門／裸 psql UPDATE）／W3-C sim P3 前置**四件**（＋N11 `gain_basis` NOT NULL，
**趁八表零列時做、成本隨時間單調上升**）／W3-D 兩懸崖（10-14 七項逐項落點）／
**W3-E 判斷力判準專章**（靈魂 §三逐字「供後續專章細化」，模擬專章是現成體例）。

---

## §5 對應 table schema（憲章 v1.39.0 強制節 a）

**本計畫不新建表即可完成 W0／W1**（新表僅 W1-7／W3-A 之候選草案，見末）。所讀既有表 schema 摘要
（全部唯讀 psql 親驗 2026-07-31 12:0x；完整欄位見 workflow `wf_ae21c531-20e` schema-map 路輸出）：

| 表 | PK | 關鍵 CHECK | Trigger | 現列數 | 本計畫用途 |
|---|---|---|---|---|---|
| `validation_evidence` | evidence_id | check_type∈(sql/script_exit/manual)、status∈(green/amber/red/unverified) | **無** | 19 | W1-2/3/4 讀寫；**零 trigger＝無 pre-image** |
| `attestation_result` | id | 無 | 無 | 8 | W1-5 判態來源（改讀此表 `run_at`） |
| `evolution_run` | run_id | status∈(running/succeeded/failed/halted) | delonly ROW+TRUNC（**UPDATE 無 guard**） | 13（running **6**） | W0-0 回填、W1-7 |
| `evolution_iteration_ledger` | iteration_id | — | delonly（UPDATE 無 guard） | 4 | W0-0；`steps_json` 為**合法 UPDATE 路徑**（W2-1 一刀切會打死） |
| `evolution_deferred_work` | defer_id | — | **無** | 4 | W0-0 觀察；`cleared_at/by` 為合法 UPDATE |
| `heavy_slot_holder_log` | log_id | — | **無** | 4 | W1-7 reconcile（`released_at` 合法 UPDATE） |
| `evolution_production_feature_set` | feature | set_status∈(active/removed) | delonly（UPDATE 無 guard） | 9（active **2**） | D11／SUNSET (b) |
| `direction_gate` | gate_id | chk_dg_approved_signed（**僅驗非空**） | no_goalpost | 29 | D1 算術 |
| `governance_proposal` | proposal_id | kind／status 枚舉；**無** decided_by 非空 CHECK | immutable（BEFORE DEL+UPD，**不含 INSERT**） | 4 | W2-9（N4 旁門具體印證） |
| `knowhow_auto_admit_state` | (target_kind,target_id) | admit_depth 0–10 | **UPDATE 已有 guard**（`admit_state_guard`，非 delonly 23 表之一） | 146,348 | D4 分母基礎（285,177−146,348＝**138,829**） |
| `knowledge_item` | item_id | 無 | 無 | 285,177 | KH0 分母 |
| `knowledge_item_text` | itext_id | **全文准入三軌不變式在此**（license 白名單／owned_local↔local_private／禁 ai_generated） | 無 | 158,528 | KH0 判定輸入 |
| `feature_values` | (panel_date,stock_id,feature) | 無 | **fv_row 全鎖＋fv_stmt** | 8,540,331 | 對照組 |
| `feature_candidate_values` | 同上 | 無 | **無**（N8） | 390,274 | W2-5 |
| `simulation_method_registry` | method | chk_smr_registered_signed、tilt_free 必 true | delonly | **0** | N1 死鎖點 |
| `sim_evolution_candidate` | candidate_id | trust_rank 必 'TR-C' | simc_forward_only | **0** | FK→registry＝死鎖 |

**`honesty_delete_only_guard` 23 表施工分級（W2-1 用）**：
**A 組 7 表已親證有合法 UPDATE**（`evolution_run`／`evolution_kill_switch`／`evolution_production_feature_set`／
`evolution_iteration_ledger`／`philosophy_principle`／`promotion_queue`／`steward_question_ledger`）——
其中 `evolution_kill_switch` 的 `state` 就是靠 UPDATE 切換，**擋死＝緊急煞車失能**（D7 須裁豁免）；
B 組 3 表同 schema 家族未活躍；C 組 3 表跡象模糊待查；D 組 3 表已有既存 UPDATE guard **可當範本**。

**新表草案（僅草案、未 apply）**：`evolution_run_zombie_reconcile`（W1-7 回填帳）、
`knowledge_kh0_progress`（W3-A 進度帳）——兩者均已確認未撞既有表名。

---

## §6 對應 python 程式規畫（憲章 v1.39.0 強制節 b）

| 項 | 檔:行 | 現況 | 改法 | 連帶影響 |
|---|---|---|---|---|
| W0-0 | `scripts/run_evolution_iteration.py:130` | `subprocess.run(..., timeout=7200)` 硬寫、`TimeoutExpired` 不捕捉 | `_run_cmd` 補 except → step 記 failed ＋ `evolution_run` UPDATE status='failed'；timeout 改組態 | 須同改 `install_cron.sh:52-53` 註解；回填 UPDATE 未來受 W2-1 GUC 閘 ⇒ **須同批設計成 GUC-aware** |
| W0-1 | `scripts/governance_queue.py:89-91`、`:167` | `typed or default`；自測反鎖回退 | 空輸入即拒；自測改斷言「空輸入被拒」 | 無其他呼叫端 |
| W0-2 | `scripts/check_treaty_refs.py:47/49/131/139/147-150` | stem 全名錨、LEGACY 不認「史述」、entries 不含 docs | 四處同改＋自測補兩例 | **W1-12 上游**；改壞會使 repo 級封鎖 |
| W0-3 | `scripts/report_triple_evolution_week.py:39` | 寫死 `/60` | 讀 `direction_gate.criteria->>'min_clusters'` | 週日首跑 |
| W1-2/4 | `scripts/verify_validation_evidence.py:88-90`、`main()` 分派、`run()` 結尾 | `status_note=COALESCE(...)` 覆寫人裁；`run()` 無條件 return 0；`--run` 吞掉 `--strict` | 分離 machine_note；排程改兩段式 | **首跑即毀 hugo 人裁文字**（D9） |
| W1-5 | `audit_watchdog.sh:15-20` | 判態抓 log 最後一行、不論時效 | 改查 DB `attestation_result.run_at` | `audit_selfheal.sh:11-18` 打真實 FinMind ⇒ D6 |
| W1-7 | `src/augur/core/heavy_slot.py`（holder_status）；新回填器 | orphan 已可辨識 | 回填判準＋逐列清單交人簽 | 受 delete-only guard ⇒ UPDATE＋人簽 |
| W1-8 | `src/augur/philosophy/retrieval.py:335`／`:408`／`:373` | ANN 分支缺過濾；死碼；快取不寫 `_at` | 三處同 commit | **必重啟 advisor/chat 再實測**（#7） |
| W2-2 | `src/augur/knowledge/auto_admit.py`（`population_discriminates`／`upsert_state` GREATEST） | 閘靠 0.27% 尾巴解開；降級被 GREATEST 還原 | 病 A＝判準重訂（**決策層**）；病 B＝先查 GREATEST 原始設計意圖（讀碼＋git log），查不到標 UNKNOWN 不擅改 | P2-11 已禁 bulk UPDATE 當降級手段 |
| W2-4/6 | `scripts/check_cmd_matrix.py:83` | `if fn == "__init__.py": continue` | 收窄為「薄 `__init__` 才豁免」＋補 `catalog`／`arena` 矩陣（**同 commit**） | 不同 commit ⇒ repo 封鎖 |
| W2-7 | `src/augur/core/heavy_slot.py:25/46/267-274` | `_selftest` 用生產鎖名、真寫生產表 | 換測試鎖名＋ROLLBACK（**保留真寫入**） | 註解自陳字面斷言曾漏抓欄名不存在 ⇒ 不可改回字面 |
| W2-9 | 簽核表 trigger；`local_model_version` | trigger 一律不含 INSERT；`promoted_by` nullable 無 CHECK | trigger 擴含 INSERT ＋ 補 CHECK | **與人閘甲乙兩案皆相容** |
| W3-A | `auto_admit.py:315-318`／`:680-682`／`:698-699`；`run_kh_chain.py:181/226` | KH0 判定＝兩行純 SQL；候選 **INNER JOIN** item_text ⇒ 破口件永遠選不到、`--phase advance` 必然 rc=4；`:181` 指示語**是錯的** | 依 D4 裁決 | 若改 LEFT JOIN 而不改判準 ⇒ 138,780 件 verdict=fail 的**鏡像假綠** |

---

## §7 對抗審查發現表（CLAUDE #20 留痕）

**兩路共 27 則 findings，其中 critical 5 則。全部已反映進上文。** 摘最重要者：

| # | 級 | 發現 | 處置 |
|---|---|---|---|
| **A1** | critical | **治症狀不治根因**：原骨架 W1-5 只回填殭屍，但殭屍是 I3 逾時所生、每 30 分 drain 重試就再長一個 | 新增 **W0-0** 並排在回填之前 |
| **A2** | critical | **偵測層蓋在沒有地基上**：機器上**無任何 sink**，OnFailure 排第四位 ⇒ W1-2/1-3 的紅燈在 sink 建好前等於沒亮 | sink 上提為 **W1-1**＋列為 **D5** |
| **A3** | critical | **已在算術上關閉的懸崖被留到最後**：SUNSET (a) 在 10-31 前物理不可能 | D1／D2 上提為 W0′ 呈案 |
| **A4** | critical | **W2-1 是最大破壞性項**：前置倒置（W1-7 回填器會被自己的閘擋死）＋一刀切打死 7 張表＋`kill_switch` 煞車失能＋DDL 撞 dump/夜輪 | 抽成獨立子計畫、加 D7 |
| **A5** | critical | **靈魂 v1.10.0 在全骨架零落點**：「判斷力」全 repo 只出現在一個檔案，零 code、零 DB、連自己的 CS 都沒覆蓋 | 新增 **W1-9** 落差表＋**W3-E** 判準專章 |
| **A6** | high | **W1-4 首跑即銷毀 hugo 人裁紀錄** | 新增 **W1-2** 保全＋**D9** |
| **A7** | high | **W1-5 根因診斷錯了**：真因是 watchdog 判態抓 07-15 舊 PASS 行 | 改寫 W1-5 |
| **A8** | high | **W1-12 會使 repo 立即不可 commit**（`constitution_lint --selftest` rc=1，G10）；且 pre-commit 框架未安裝＝新外部依賴 | 移最末＋三步拆解；**順帶解掉 r2 §11 一個未知**：G10 FAIL 逐字定位在 selftest 輸出 :131 |
| **A9** | high | **W1-7 會殺掉活的 run_id=16**（pid 1709 仍在跑） | 加存活判準＋逐列人簽 |
| **A10** | high | **W0-4／W0-5 是治權檔增修**（MC §8.1） | 移出 W0 → **D8 呈案** |
| **A11** | high | **`install_cron.sh:57` SSOT 漂移**：`--apply` 會靜默拿掉 TWEVO 的 `--slot-wait 10800` | 新增 **W1-6**，先於任何新增 cron |
| **A12** | high | **manual 五條對紅燈永久免疫**（26%） | 併入 W1-3＋D9 |
| **A13** | high | **N4 INSERT 旁門漏列**；標的 `local_model_version` 正是靈魂終點的模型晉升表 | 抽為 **W2-9**（不預判人閘拍板） |
| **A14** | medium | **「掛好但不啟」在本專案不成立**：兩個 timer 註解寫「待開閘」，實際 enabled＋active 且今日已跑 | W1 新 timer 前先補真 gate |
| **A15** | medium | **W3-A 第一節排錯**：分水嶺是**判準**不是車道 | 改為 D4 呈案；驗收須**兩個**指標（破口=0 **且** verdict=pass 比例） |
| **A16** | medium | **W2-2 只修病 B 漏病 A**（KH8 閘自己開著） | 改為兩件並列、病 A 優先 |
| **A17** | medium | **W2-4／W2-6 順序陷阱**：先掛稽核後收窄豁免 ⇒ 收窄當天 repo 封鎖 | 同 commit |
| **A18** | medium | **今日是週五**，最近看顧點是**今晚 23:00** 不是明天；另漏 08-01 04:00 ata-advance 排程級首驗 | W1-11 按日曆釘死 |
| **A19** | medium | **N11 漏列**：`gain_basis` nullable 可繞過 CHECK；五臂只鎖值域不鎖完備性 | W3-C 由三件改四件、**趁零列時做** |
| **A20** | medium | **N9 漏列**：heavy_slot selftest 用生產鎖名真寫 DB，會與 W1-12／W1-11 互撞 | W2-7；**保留真寫入**改 ROLLBACK |

**另本輪順帶解掉 r2 §11 兩個未知**：(1) G10 FAIL 位置已逐字定位；
(2) **KH0 每件計算＝零 LLM 純 SQL**（`auto_admit.py:315-318` 兩行；全 knowledge package 對 ollama grep 零命中）
——原「96 天」假設**不成立**，純 SQL 路徑實測 145 items/s ⇒ **約 16 分鐘**。
「62.7s/件」出自 `admission_assist_run` 單樣本（examined=1）、屬**來源審批車道**，從不碰 `knowledge_item`。

---

## §8 驗收判準（機械可判、唯讀可重跑）

每條均須能回答「**這個檢查若壞了會不會安靜變綠燈**」。

```bash
# W0-0：逾時可被捕捉（非唯讀，於修後跑一次）
grep -n "TimeoutExpired" scripts/run_evolution_iteration.py     # 期望：捕捉分支存在
psql -tAc "SELECT count(*) FROM evolution_run WHERE status='running' AND started_at < (SELECT pg_postmaster_start_time())"
                                                                 # 期望：0（存量殭屍已回填）
# W0-1：非 TTY 拒絕、空輸入拒絕
venv/bin/python scripts/governance_queue.py --approve gp_test < /dev/null; echo "rc=$?"   # 期望 rc=1 且訊息含 P5.W2
# W0-2：稽核器抓得到縮寫與裸版號
venv/bin/python scripts/check_treaty_refs.py; echo "rc=$?"       # 期望 rc=1（現存 README:30 等應被抓出）
venv/bin/python scripts/check_treaty_refs.py --selftest; echo "rc=$?"  # 期望 rc=0
# W1-4：燈會紅（掛排程後）
venv/bin/python scripts/verify_validation_evidence.py --run --with-scripts && \
venv/bin/python scripts/verify_validation_evidence.py --strict; echo "rc=$?"  # 期望：有 false 時 rc≠0
# W1-5：判態改讀 DB
psql -tAc "SELECT max(run_at) > now() - interval '36 hours' FROM attestation_result"   # 期望 t
# W1-8：洩漏已堵（改後須先重啟服務）
systemctl --user restart augur-advisor augur-chat && sleep 5 && curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8399/v1/models
grep -c "answer_status" src/augur/philosophy/retrieval.py        # 期望 ≥4（原 3）
```

**整體健康單一指令組**（每日可跑，Steward 一眼看出哪波卡住）：
```bash
cd /home/hugo/project/augur && venv/bin/python scripts/check_treaty_refs.py; \
venv/bin/python scripts/check_cmd_matrix.py; \
venv/bin/python scripts/verify_validation_evidence.py --strict; \
psql -tAc "SELECT 'zombie', count(*) FROM evolution_run WHERE status='running' AND started_at < pg_postmaster_start_time() UNION ALL SELECT 'attest_age_h', extract(epoch from now()-max(run_at))/3600 FROM attestation_result"
```

**人簽類驗收**（W1-7、D 系列）：判準寫成「**由 hugo 親跑、AI 不得代填**」，
人簽欄為 `decided_by`／`approved_by`／`closed_by`。

---

## §9 明確不做（承基線 P2 八項＋r2 三項＋本輪新增）

不動 import_isolation 三道隔離閘（唯一無假綠者）／不動 `heavy_slot` advisory 實作（問題在覆蓋率）／
**不為讓 `validation_evidence` 變綠而改 `check_sql` 或 UPDATE status**（P2-3；本計畫 W1-4 之寫入是
「依預先存在的 check_sql 誠實回填」，與此性質相反，已於 §4 明文界定）／人閘未拍板前不新增 AI 可自動 approve 通道／
不動 arena G1-PIN as-of／不為讓 TWEVO 跑完而加 `--allow-apply`／load 高時不排新重活／
不硬編數字轉抄（P2-8；W0′-a 之手抄權宜已留痕）／**不在 drain 補跑進行中並行動 tw-20260728-r01**（P2-9）／
**不由 AI 批次註冊 20 個 sim method**（P2-10）／**不把 admit_depth bulk UPDATE 當降級手段**（P2-11）／
**不代勾 10-14 checklist、不因任何補正假關其他日曆項**（RULING-039/040 明文，且本專案有假關前科被列管）。

---

## §10 未知與風險登記

| # | 未知 | 阻擋什麼 | 查證方式 |
|---|---|---|---|
| U1 | `--local-gates` 真實牆鐘 | W0-0 timeout 設多少 | 讀歷史 log（W0-0 步驟 a） |
| U2 | FinMind 訂閱現況 | D6 | 問 Steward／查 `/user_info`（屬 API 呼叫、須授權） |
| U3 | `GREATEST` 之原始設計意圖 | W2-2 病 B | 讀碼＋git log；查不到即標 UNKNOWN 不擅改 |
| U4 | 07-30 15:29 bulk 降級由誰發動 | W2-2 | 無 actor 欄，可能永久不可考 |
| U5 | 四支 fetch 腳本有無 #24 等價節流 | W2-3 | 讀碼（已知只有裸 `time.sleep`） |
| U6 | 候選重建流程有無 DELETE/TRUNCATE | W2-5 | grep 寫入器 |
| U7 | f143aa6 排程級驗證 | W2-3 前提 | 08-01 04:00 自然揭曉（W1-11） |
| U8 | drain 補跑最終結果 | W1-7 | 進行中；13:20 後可判 |

**最大風險**：本計畫 W1 的價值全繫於 **D5（sink）** 先裁——沒有 sink，W1 做完只是把更多紅燈接到沒人看的地方。
次大風險：**D1／D2 若拖過兩週**，SUNSET (b) 的可挽救時間所剩無幾（每拖一週吃掉 92 天預算的 7.6%）。

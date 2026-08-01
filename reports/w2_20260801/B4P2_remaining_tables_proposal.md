# [DRAFT 呈案] B4-P2｜殘餘 delete-only 19 表分批升級 UPDATE-GUC——RULING-2026-043 甲案射程擴充案

> **[DRAFT 呈案] 未經拍板不得施作。**
> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草；所涉 19 表全數記錄 AI 引擎自身的迭代、晉升、模擬與治理答案（引擎即主要寫入者），通行證補丁亦將由 AI 寫入（含兩支現正禁改之引擎檔）。故本案一律以機械可判驗收與證偽條件為據，不以「相信起草者」為據；凡「排除某表」之建議（§5 kill_switch）尤須注意起草者利益方向＝少上閘少受束，Steward 應獨立衡量。
> 日期：2026-08-01（全部數字為本日執行時現查，配方＝`.env` 唯讀 psql＋repo 靜態掃描；非抄自舊報告）。
> 上游：`reports/w2_20260801/B4_update_guc_upgrade.md`（P0 四表；已依 RULING-2026-043 甲案於 2026-08-01 施作完畢，本日親驗 4/4 已掛 `honesty_ledger_guard`）。

---

## §1 問題、授權鏈與治權定位

**問題**：B4 P0 只覆蓋晉升鏈判準四要害；`honesty_delete_only_guard` 現仍掛於 **20 表**（親驗 `pg_trigger`，本日），其中 19 表 **UPDATE 面全裸**——一句裸 psql UPDATE 即可默改 queue 決議、迭代帳本、Steward 答案、模擬 run 紀錄，零留痕（#15 默改面；07-31 單一角色整併後 DB 層 role 縱深不存，trigger＋GUC＝僅存 DB 層機械屏障）。第 20 表 `sim_evolution_verdict` 為 edge case：sim 專章 §5.1/5.2 已另掛 `sev_no_update`（UPDATE 綁 `honesty_ledger_guard`，`scripts/migrate_sim_evolution_ddl.py:214-216`），**不在本案射程**。

**治權定位**：RULING-2026-043（B4-043）明文「C5 對其餘 delete-only 表（PME 5 表＋P2 殘餘）效力不變」（`scripts/migrate_honesty_guards_ddl.py:12-17` 註記）。故本案性質＝**請求 Steward 將 043 甲案（先合寫入者通行證補丁、DDL 後行）之適用範圍分批擴至 P2 表集**——屬治權判準變更，AI 僅得草擬、比對與呈案（`AUGUR-MC v1.6 §8.1`／L6.18(a)）。C5 三理由之逐條回應已在 P0 呈案 §1 成立，本案不複述；**本案新增的逐表事實**（§3）用於判定各表落 043 邏輯（current-state／生命週期欄，宜上 GUC）還是 C5 ③ 邏輯（純 append-only，追加修訂列為正解、GUC 為零成本加固）。

**授權鏈**：本呈案＝W2 呈案批 P2B 路（範圍：唯讀親驗＋寫本呈案；結束條件：文件交付；所繫任務＝B4-P2 批次呈案）。拍板後之補丁與 DDL＝執行層，於統一 DDL 窗進行；**run 21 進行中，`run_evolution_iteration.py`／`run_philosophy_evolution.py` 禁改**——凡補丁落於此二檔之表（§4 P2b）其施作一律順延至 run 21 結束後。

---

## §2 現況親驗（2026-08-01）

### 2.1 delete-only 現掛表集（pg_trigger 現查）

`SELECT c.relname, t.tgname, p.proname … WHERE p.proname='honesty_delete_only_guard'` → **20 表 × 各 2 trigger**（DELETE row 級＋TRUNCATE statement 級）。扣除 `sim_evolution_verdict`（已另有 UPDATE 閘）＝**殘餘 19 表**，與登錄冊 P2 口徑相符。P0 四表（`principle_factor_map`／`philosophy_principle`／`evolution_production_feature_set`／`feature_sign_check`）本日親驗均已掛 `honesty_ledger_guard`（tgtype 含 UPDATE 面），delete-only 舊名零殘留——043 施作完畢之獨立佐證。

### 2.2 UPDATE 活動實況（pg_stat_user_tables 現查；計數＝自統計重置起累計）

| 表 | n_live_tup | n_tup_ins | **n_tup_upd** | n_tup_del |
|---|---:|---:|---:|---:|
| steward_question_ledger | 1,417 | 1,417 | **2,262** | 0 |
| promotion_queue | 603 | 604 | **100** | 0 |
| mc_simulation_run | 540 | 540 | **64** | 0 |
| evolution_iteration_ledger | 5 | 5 | **61** | 0 |
| evolution_run | 18 | 20 | **16** | 0 |
| evolution_hypothesis_hint | 20 | 20 | **10** | 0 |
| raw_evolution_iteration_ledger | 2 | 2 | 2 | 0 |
| evolution_kill_switch | 5 | 5 | 1 | 0 |
| evolution_apply_log／evolution_coverage_snapshot／evolution_evidence_run | 23／795／4 | 24／795／5 | **0** | 0 |
| local_ai_iteration_ledger＋sim 七表 | 0～1 | 0～2 | **0** | 0 |

讀法：**UPDATE 是這些表的真實日常**（八表非零），閘不能「掛了看有沒有人叫」——凡活躍表必先補通行證否則立斷工具鏈；反之九表 n_tup_upd=0 且 repo 零 UPDATE 寫入者＝**零補丁白撿的升級**。n_tup_del 全表為 0＝delete-only 閘從未誤傷，佐證掛閘以來無合法 DELETE 需求。

### 2.3 寫入者普查（repo 靜態掃描：`UPDATE <tbl>`＋`INSERT…ON CONFLICT DO UPDATE`；範圍 scripts/・src/・tools/・ops/・augur_proxy/ 之 .py/.sh/.sql；另做全 repo 邊界掃描——僅見 worktree 鏡像，無漏網）

普查方法之射程限制（誠實）：動態拼接 SQL（f-string 組表名）與 repo 外工具不在靜態掃描射程；已以 §2.2 活動計數交叉對照（活躍表均找得到對應寫入者，無「有活動卻無寫入者」之表——普查自洽）。

### 2.4 trigger 住所地圖（升級機制的關鍵前提）

| 住所 | 表（trigger 命名） |
|---|---|
| `scripts/migrate_honesty_guards_ddl.py`（PME_TABLES） | evolution_run・evolution_coverage_snapshot・promotion_queue・evolution_apply_log・evolution_kill_switch（標準名 `trg_<t>_delonly_*`） |
| `src/augur/audit/evolution_ledger_ddl.py` | evolution_evidence_run（`evidence_no_*`）・evolution_hypothesis_hint（`hint_no_*`）・evolution_iteration_ledger（`tw_iter_no_*`）・local_ai_iteration_ledger（`lai_iter_no_*`）・raw_evolution_iteration_ledger（`raw_iter_no_*`） |
| `scripts/migrate_sim_evolution_ddl.py` | mc_simulation_run（`mcsim_no_*`）＋sim 七表（`sce/simc/sim_iter/simllm/sro/simlink/smr_no_*`） |
| `scripts/migrate_steward_qledger_ddl.py` | steward_question_ledger（標準名、住所獨立） |

**含義**：P0 四表升級時 `_upgrade_sql` 的 DROP 清單（只卸 `trg_<t>_delonly_*`／`trg_<t>_honesty_*` 標準名）恰好夠用；P2 有 **14 表住所在別檔**、其中 13 表 trigger 為自訂名——照抄 P0 機制會（a）舊 delonly trigger 殘留（DELETE 面雙攔無害，但 #12 閘住所分裂）且（b）原 DDL 腳本冪等重跑會把 delete-only 再掛回。機制修正見 §6。

---

## §3 逐表盤點（19 表）

「補丁點」＝含 UPDATE 之獨立交易數（一交易補一句 `SET LOCAL augur.honesty_write='on'`）；「性質」依欄語意：**治權**＝決議/人簽/治理答案欄、**帳本**＝run/迭代生命週期紀錄、**資料**＝模擬/快照數據。

| # | 表 | 性質 | 合法 UPDATE 寫入者（現查） | 補丁點 | 升級風險 |
|---|---|---|---|---:|---|
| 1 | promotion_queue | **治權**（queue_status/decided_by——晉升鏈斷點之一） | `apply_evolution_promotions.py:285`（halted）/`:319`（rejected_gate）各自獨立交易須補；`:388`（applied）**已在 :349 通行證交易內＝零補** | **2**＋ops | 低。另 `ops/a3_gsign/rollback_pending_auto_gsign.sql`（A3 待命回滾）裸 UPDATE promotion_queue——**上閘後須同步加通行證，否則未來 A3 回滾被自家閘擋**；`migrate_pending_auto_gsign.sql` 同型（若已執行完畢則僅屬史料） |
| 2 | steward_question_ledger | **治權**（status/resolution_ref/resolved_by——治理答案） | `triage_questions.py`（1 交易）；`resolve_questions.py` classify/solve/advisor/sweep_queued/sweep_awaiting（5 交易） | **6** | 中。最活躍表（2,262 次 UPDATE）——漏補任一交易立斷問題處理鏈；但全部寫入者集中兩支工具腳本、無引擎檔 |
| 3 | evolution_hypothesis_hint | **治權**（decision/decided_by **人簽欄**） | `serve_admin_console.py:1306`（console 決議路） | **1** | 低。另 `run_raw_evolution_iteration.py:223` **印給 hugo 的手動 UPDATE 教學句**須同步改寫（附咒語或改教 CLI），否則文件教的路被閘擋。GUC 半閘正面強化「不代打人簽」：裸手改 decided_by 被拒＝逼意圖留痕 |
| 4 | evolution_apply_log | 帳本（apply 紀錄＋delta 補填） | `apply_evolution_promotions.py:215`——**已在 :201 通行證交易內** | **0** | 零。白撿 |
| 5 | evolution_evidence_run | 帳本（證據 run） | 無 | **0** | 零。白撿（自訂名 `evidence_no_*` 須入 §6 卸舊映射） |
| 6 | evolution_kill_switch | **治權**（stop-switch state） | `set_evolution_kill_switch.py:97`；`evolution_ledger_ddl.py:253`（backfill、現匹配 0 列＝不觸發）；另兩處 runner 說明文字教手動 psql UPDATE 解除 | **1** | **特殊：見 §5**——緊急煞車的否決可達性 vs 防默改 clear，建議單獨裁 |
| 7 | evolution_run | 帳本（status/finished_at 生命週期） | `run_philosophy_evolution.py:923`/`:962`（**禁改檔**）；`audit_philosophy_feature_coverage.py:274`；`backfill_evolution_run_zombies.py:100` | **4** | 中。2 點落在禁改引擎檔→**順延 run 21 後**；殭屍回填工具亦是合法寫入者、漏補則殭屍清理斷 |
| 8 | evolution_iteration_ledger | 帳本（TW 迭代、引擎逐迭代更新） | `run_evolution_iteration.py:263`/`:347`（**禁改檔**） | **2** | 中。全部補丁在禁改檔＋活躍（61 次）→**必須順延 run 21 後**，且 DDL 換閘（ACCESS EXCLUSIVE）不得與 run 重疊 |
| 9 | raw_evolution_iteration_ledger | 帳本（raw 軌迭代） | `run_raw_evolution_iteration.py:209` | **1** | 低（raw runner 不在禁改清單；仍建議同窗處理） |
| 10 | evolution_coverage_snapshot | 資料（覆蓋快照、insert-only） | 無 | **0** | 零。白撿 |
| 11 | local_ai_iteration_ledger | 帳本（LAI-Evo；寫入者尚未誕生—H1 R-CELL′ 未落地） | 無 | **0** | 零。白撿；未來寫入者出生即須帶通行證（把約束寫進 H1 施作清單） |
| 12 | mc_simulation_run | 資料（MC 模擬 run） | **3 處 upsert**（`simulate_mc_paths.py:151`、`simulate_portfolio_risk.py:396`/`:495`，`INSERT…ON CONFLICT DO UPDATE`） | **3** | 中。**C5 ②「首過再死」型的活教材**：不先補通行證，首跑過、重跑同情境死——嚴守 043 次序（補丁先合、DDL 後行、驗收打衝突分支） |
| 13-19 | sim 七表（sim_calibration_eval・sim_evolution_candidate・sim_evolution_iteration_ledger・sim_llm_proposal・sim_realized_outcome・sim_run_link・simulation_method_registry） | 資料/帳本（sim 專章 P2 落地表；引擎未建） | 無（n_tup_upd 全 0；僅 candidate 2 列、registry 1 列 insert） | **0** | 零補丁但**判準歸屬問題**：sim 專章已自行逐表設計 mutability（verdict 特掛 UPDATE 閘、candidate forward-only）——由 honesty 機制越俎升級＝住所與判準雙分裂，見 §4 P2c |

**補丁總量**：P2a＋P2b 合計約 **19 個交易補丁點、分佈 10 檔**（其中 2 檔現禁改）＋1~2 支 ops SQL＋3 處說明文字；4 表零補丁白撿。

---

## §4 建議分批（供圈選）

### P2a——高危治權表 6 表（先行；補丁全在工具腳本、不碰禁改檔）

`promotion_queue`・`steward_question_ledger`・`evolution_hypothesis_hint`・`evolution_apply_log`・`evolution_evidence_run`（＋`evolution_kill_switch` 若 §5 裁甲）。
理由：決議欄/人簽欄/治理答案＝默改代價最高；補丁點 9 個全在 5 支工具腳本＋1 支 ops SQL，與 run 21 零交集，**本週 DDL 窗即可上**。次序照 043 甲案：補丁 commit → DDL `--apply` → §7 探針。

### P2b——引擎 run/資料帳本 6 表（run 21 結束後之 DDL 窗）

`evolution_run`・`evolution_iteration_ledger`・`raw_evolution_iteration_ledger`・`evolution_coverage_snapshot`・`local_ai_iteration_ledger`・`mc_simulation_run`。
理由：4 個補丁點落在 `run_evolution_iteration.py`／`run_philosophy_evolution.py`（現禁改），且換閘 DDL 對 run 中引擎正在寫的表拿 ACCESS EXCLUSIVE 必衝突（lock_timeout 5s 會 abort 保平安、但等於白跑）——**時機約束是硬的**。mc_simulation_run 三處 upsert 補丁可先行合入（無 trigger 時 SET LOCAL 無害），DDL 與本批同窗。

### P2c——sim 專章七表（**建議緩議**）

建議：**維持 delete-only、不納本案**。理由：(a) sim 專章對自家表的 mutability 已有逐表設計權與先例（verdict UPDATE 閘、candidate forward-only 均出 `migrate_sim_evolution_ddl.py`），honesty 機制代升＝閘住所自 sim DDL 分裂出去（#12）且繞過 sim 專章判準；(b) 引擎未建、表近空（最多 2 列）、n_tup_upd 全 0——現在的威脅面＝零價值標的；(c) 待 sim 引擎寫入者設計時逐表定案（append-only 者依 C5 ③ 走追加修訂列＋可加零成本 GUC 閘）。**次選**：若 Steward 欲即刻上閘，應由 `migrate_sim_evolution_ddl.py` 就地升級（沿 verdict 先例），不進 `GUC_TABLES` 集合。

---

## §5 kill_switch 單獨裁（兩案並陳）

威脅：裸 UPDATE `state='clear'` 可**默默解除一次 halt**（連 set_by 都可偽填）——治理級默改。
代價：kill_switch 同時是**人類緊急煞車**；兩支 runner 的說明文字（`run_evolution_iteration.py:661`、`run_raw_evolution_iteration.py:191`）現行教的解除路徑就是裸 psql UPDATE。上 GUC 後，hugo 急停/解除須 `BEGIN; SET LOCAL augur.honesty_write='on'; UPDATE …; COMMIT;`——緊急時刻多記一句咒語＝**否決可達性下降**（#26 OCV 單向棘輪明文：否決可達性弱化＝治權變更、停下問——這正是本節單獨呈裁的原因）。

- **甲案（納入 P2a）**：`set_evolution_kill_switch.py` 補通行證（1 點）成為正路，兩處說明文字改教 CLI＋附完整咒語備援。得：clear 默改被閘。失：CLI 壞掉的最壞情境下，裸 psql 最後手段多一道門檻。
- **乙案（排除；維持 delete-only）**：緊急路徑零摩擦不變。失：clear 默改面保留（緩解＝C2 watchdog 對 halt 狀態的獨立監看、n_tup_upd 異動可事後稽）。

**AI 建議：乙案**（煞車綁人手優先於閘完整性；利益揭露：此建議同時=起草者少做一表，Steward 請獨立衡量甲案）。

---

## §6 DDL 機制（沿 `migrate_honesty_guards_ddl.py`；說明白、本呈案不改碼）

1. **集合**：新增 `GUC_TABLES_P2A`／`GUC_TABLES_P2B` tuple；`PME_TABLES` 遷出對應表（防 `--apply` 重掛 delete-only——P0 遷出三表之既有先例）。
2. **卸舊清單擴充**：`_upgrade_sql` 現行只 DROP 標準名；P2 須加**逐表 legacy trigger 名映射**（§2.4 自訂名 13 表，如 `LEGACY_TRIGGERS = {"evolution_iteration_ledger": ("tw_iter_no_delete_row","tw_iter_no_truncate"), …}`），同交易內先卸盡（全 `IF EXISTS` 冪等）再掛 `honesty` 雙 trigger——原子換閘無空窗。
3. **原住所同步**（#19 跨檔一致）：`evolution_ledger_ddl.py`／`migrate_steward_qledger_ddl.py` 之 delete-only 段對已升級表改為 no-op 或改建 honesty 版，否則其冪等重跑把 delonly 掛回（無害但住所分裂復發）；各檔 selftest 斷言同步。
4. **執行**：補丁 commit 先行 → `python scripts/migrate_honesty_guards_ddl.py --apply`（逐表獨立交易＋`SET LOCAL lock_timeout='5s'` 不排隊，#30 鎖紀律不變）→ `--check` 收尾。P2b 一律在 run 21 結束後的 DDL 窗。
5. **回滾**（可逆性）：逐表 `DROP TRIGGER trg_<t>_honesty_*` ＋重跑原 DDL 重掛 delete-only＝完整退回現狀，零資料損失。

---

## §7 機械驗收（施作後回呈）

1. `pg_trigger` 現查：升級表全數掛 `honesty_ledger_guard` 且 tgtype 含 UPDATE 面；legacy 名 **0 殘留**（含自訂名 13 表逐名驗）。
2. 紅測（每表）：`BEGIN; UPDATE <t> … WHERE <既有一列>; ROLLBACK;` → 須 EXCEPTION（**打既有列＝打 C5 ② 衝突分支等價路徑**，非只測首插）。
3. 綠測（每表）：`BEGIN; SET LOCAL augur.honesty_write='on'; UPDATE 同列自值; ROLLBACK;` → 須過。
4. 工具鏈實跑（#7）：`triage_questions.py`／`resolve_questions.py`／`apply_evolution_promotions.py --dry-run`＋實跑各一最小單位；mc 模擬同情境**重跑一次**（upsert 衝突分支實測）。
5. 原 DDL 腳本冪等重跑後複驗 1（delonly 未被掛回）。

## §8 證偽條件

- 若任一升級表存在本普查未列之合法 UPDATE 寫入者（動態 SQL／repo 外工具／cron 外掛），首次執行被閘拒＝普查證偽 → 該表補通行證或縮射程退回 delete-only（回滾 §6.5，可逆）。
- 若 P2a 上閘後 steward 問題鏈或晉升鏈在補丁齊備下仍報閘錯 → 該表立即回滾並重呈。
- 若 kill_switch 裁甲後發生一次「緊急停/解除被咒語卡住」實例 → 立即退回 delete-only（乙案），本案關於甲案之論證作廢留檔。
- 若 sim 引擎設計時判定某 sim 表需 in-place UPDATE 語意 → P2c「緩議」判斷證偽，屆時由 sim 專章重呈。
- 若 §2.2 活動計數因統計重置未涵蓋某年度批次作業而漏判「低活動」→ 以施作後首月閘錯誤日誌為準修訂分批。

## §9 Steward 決定欄（留白）

- P2a（6 表；kill_switch 依 §5 另裁）：＿＿＿＿
- §5 kill_switch（甲／乙）：＿＿＿＿
- P2b（6 表；run 21 後窗）：＿＿＿＿
- P2c（sim 七表；建議緩議）：＿＿＿＿
- 裁決編號：＿＿＿＿　簽署：＿＿＿＿　日期：＿＿＿＿

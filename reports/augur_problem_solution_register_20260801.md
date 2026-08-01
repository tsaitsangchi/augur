# augur 問題解法登錄冊（2026-08-01）——全問題×解法×執行序

> **性質**：全專案問題之解法登錄（Steward 指示「記錄所有問題的解決方式，之後依記錄逐項展開解決」）。
> **來源**：問題面＝r3 深化理解（11 路親驗，`fd06c9b`）；解法面＝8 域平行解法設計＋critic 對抗排序（`wf_fe396f76-6c0`，9/9）。
> **執行紀律**：依冊逐項、每項過驗收才勾［狀態欄］；標【Steward】者呈案不代決；絆線守三規則
> （純函式餵真輸入／下游絆線／禁字面斷言——凡新回歸鎖必先驗紅）。
> **誠實限制**：critic 之輸入在 G 域中段截斷、H 域全缺（digest 90KB 上限）⇒ **G2-G4 與 H1-H2 未受
> critic 衝突審查**，主 session 已自 journal 直讀補入本冊，執行至該五項時須自行做衝突檢查。

---

## §1 總表（32 項；波次依 critic CR4/CR5）

| id | 問題一句話 | 層級 | 波次 | 狀態 |
|---|---|---|---|---|
| F4 | CLAUDE.md:74 殘留「PROPOSAL-2026-001 待議決」已議決句 | AI | **W0-α** | ☑ |
| E3 | arena 六交易日斷檔零機械揭露 | AI | **W0-α** | ☑ |
| A4 | mean_20d FAIL 帳 rejected_gate 無人裁載體 | AI（除役裁決=Steward） | **W0-α** | ☑ |
| C4′ | 全棧零 OnFailure sink（手動等價版，不跑 install_services.sh） | AI | **W0-α** | ☑ |
| A5 | close「任一步曾敗即敗」標籤失真（per-step 取末次） | AI（動已結列=Steward） | **W0-β** | ☑ |
| B1 | evolution_run 殭屍：寫者自收尾＋回填器 | AI（--apply=Steward） | **W0-β** | ☑ |
| C3 | lint 修 7 誤報→gate_raise 6 恆真→基線→掛閘 | AI | **W0-β** | ☑ |
| E4 | FinMind 讀錶腳本＋cron 前綴 | AI（--apply=hugo） | **W0-β** | ☑ |
| F3 | consequence 封存腳本（execute_sunset_consequence.py） | AI（首次 --apply=Steward） | **W0-β** | ☐ |
| G1 | 定期 pg_dump 腳本＋輪替＋cron 兩行 | AI（--apply/首跑=hugo） | **W0-β** | ☑ |
| A1 | 兩現役跑符號尺 --record（(b) 機械證據） | AI | **W1**（RAWEVO 輪後） | ☑ |
| D1 | fulltext 'unattempted' 旗標補 121,389 件 | AI（DDL 小窗） | **W1** | ☐ |
| cron 合批 | E4＋C1＋G1＋C4 之 install_cron.sh **單 agent 一批**＋hugo 一次 --apply | 合批=AI；apply=hugo | **W1** | ☑ |
| A2-S1 | mean_20d 語意復原探針（四假設 SQL 對照） | AI 唯讀 | **W1** | ☑ |
| F2 | 10-14 checklist 七項 Evidence 備料（不代勾） | AI 唯讀 | **W1** | ☐ |
| A3 | G-SIGN 入閘呈案包（四件套＋77 筆三案） | 呈案 AI／拍板 Steward | **W2** | ☐ |
| A2-S2 | mean_20d 產生器重建 或 除役（與 A4 併案） | 呈案→裁 | **W2** | ☐ |
| B2 | deferred 7 筆逐筆處置 SQL（探針標 test-artifact） | Steward 拍板後執行 | **W2** | ☐ |
| B4 | 23 表 UPDATE 裸缺口：P0/P1 四表升級 UPDATE-GUC 閘 | 呈案（翻 C5 一部）→裁 | **W2** | ☐ |
| C1 | validation_evidence 排程＋manual 5 條有效期呈案 | 排程 AI／有效期 Steward | **W2** | ☐ |
| C2 | attestation 掛回 watchdog（DB 三態機） | 呈案→裁（API 放量節奏） | **W2** | ☐ |
| D2 | KH8 鑑別力閘（MIN_MINORITY_MASS 三選項） | 呈案→Steward | **W2** | ☐ |
| D3 | KH5 恆 ready→逐 item 軸覆蓋證據 | 呈案→Steward | **W2** | ☐ |
| D4 | GREATEST 再膨脹：重評樓地板＋再晉升通行證 | 呈案→Steward | **W2** | ☐ |
| E1 | dgate own_stack 三門錯配：supersede vs 補 h 出單（⚠時效：E1-B′ 須 08-03 20:00 前拍板） | 呈案→Steward | **W2** | ☐ |
| E2 | headline 錨落帳：新表 alpha_headline_anchor | DDL AI／簽錨=hugo TTY | **W2** | ☐ |
| F1 | L7.16 衝突登錄：RULING-2026-042 草稿（DRAFT 與施作同 commit） | 草擬 AI／簽=Steward | **W2** | ☐ |
| F5 | 回歸鎖三規則入 CLAUDE.md 呈案（限向前生效） | 草擬 AI／定版 Steward | **W2** | ☐ |
| G2 | 異地備份三案比較呈案（外接碟/加密上NAS/第二機） | 呈案→Steward | **W2** | ☐ |
| G3 | identity 六表：沙盒演練→建表＋最小接線一案 | 呈案→Steward（P5 一次拍板） | **W2** | ☐ |
| H1 | LAIEVO 判讀層逐格有效性（R-CELL′ 預凍；不換尺） | 呈案→Steward | **W2** | ☐ |
| H2 | sim 死鎖：derive_param_schema 腳本＋首 method 入冊程序 | 呈案→Steward（D-1＋親簽） | **W2** | ☐ |
| B3 | drain timer 修好再重啟（stale-hold 護欄；前置=B2） | 判準 Steward 輕裁＋AI | **W3-b**（固定序 B2→B1 apply→B3） | ☐ |
| G4 | install_cron live --apply 一頁程序（hugo 照跑） | hugo | **W3** | ☑ |
| 3c | 統一 DDL 窗收 D4/B4/E2 之 trigger/表 | 拍板後排窗 | **W3-c** | ☐ |

## §2 critic 五裁決（執行時必守）

**CR1 九組資源衝突之首**：`install_cron.sh` AUGUR_BLOCK 被 C1/C4/E4/G1 四方搶改，而 `--apply` 是**整段替換**——分四次 apply 會互相覆蓋。裁：**單 agent 一批改完**（行序 E4→C1→G1→C4→各 selftest chk）、一次 `--check` 呈 diff、hugo **一次** `--apply`。
**CR2 層級糾正**：C4 原步驟「跑 install_services.sh」**否決**——親驗該腳本會無條件 `enable --now` drain timer（翻掉 hugo 的停用態）＋restart 六常駐服務；僅准手動等價（drop-in＋daemon-reload）。F1 之「先入 repo 必紅測試」改為**與 RULING 同 commit**（否則落地前對一切測試輪常紅＝狼來了）。D1 加逐段過目＋DDL 小窗。C3 掛閘前過目。
**CR3 絆線抽審**：D2/B1/A5/C3 合格典範；E1 之 getsource 斷言只准當第二道；F1 已糾正。
**CR4 波次**：W0 即刻（α：F4/E3/A4/C4′ 互不同檔並行；β：A5+B1 碼批/C3/E4+F3+G1 三腳本）→ W1 今日特定時機（A1 於 RAWEVO 輪後；D1；cron 合批；A2-S1/F2 唯讀）→ W2 呈案全並行 → W3 拍板後施作（3b 固定序 B2→B1→B3；3c 統一 DDL 窗）。
**CR5 首波六項**：F4（小）、E3（中）、A4（中）、A5+B1 合批（大）、C3（中）、E4/F3/G1 三腳本（各中）。

## §3 各域解法詳錄（執行依據；每項含驗收與絆線）

### A 晉升鏈
- **A1** 跑尺程序（不改碼）：前置四確認（slot 無持有／表在／map 方向 +1·−1 已驗／panel 覆蓋 22·108 已驗）→ TaskCreate → `verify_sign_consistency.py --run --features inst_cumflow_position_120d,lending_fee_rate_mean_20d --record` → stdout 貼 `audits/SIGN-B-RECORD-ACTIVE2-20260801.md` → 驗收：`feature_sign_check` 恰 4 列（2×h∈{20,60}）且 verdict∈{PASS,FAIL}；週報 (b) 不再「無紀錄」。⚠ r3「零產生器恐 UNJUDGEABLE」之慮**已排除**——尺讀 feature_values 存值非產生器。FAIL 如實入帳呈裁，不得改判。
- **A2** 兩段：S1 探針（四假設 H1 最近20筆均/H2 尾20日曆日/H3 尾20交易日/H4 日均之均，LATERAL 對照 ≥500 列跨 22 panel，|Δ|<1e-9）；S2a 命中≥99.9% → chip.py 落 f8 產生器（循 f6 型、as-of 安全 date<=panel_date）＋22 panel 全量回算 match==total；S2b 未中 → 併 A4 呈案（甲 demote 除役／乙 _v2 新名重走漏斗）。絆線：黃金 (sid,panel) fixture 斷言重算==DB 值。
- **A3** 呈案包四件套：GATE_IDS 八閘＋selftest len==8；judge_sign 移居 evolution.py＋`evaluate_g_sign_from_evidence`（<6 序列或無方向⇒FAIL+UNJUDGEABLE，FAIL vs SKIP 二選一呈裁）；build_gate_json 加**必填** kwarg g_sign（漏改呼叫端即 TypeError fail-loud；波及 7 呼叫端）；DEFAULT_GATE_CONFIG 入 sha＋_gate_scale 納閘集指紋（跨閘集 incomparable）。既存 pending_auto（執行時現查，勿寫死）三案：甲惰化／乙【建議】重評＋遷移（decided_by='gate_set_migration_gsign'，engine 欄非人簽）／丙只重評。時機：車道空＋running=0；APPLY-go 必在其後；T4 證偽=重評後 >50% 掉 rejected 即回報破壞性低估。
- **A4** 週報加「待你裁決」段：純函式 `demote_fail_pending(is_active,action,queue_status,prom_verdict)`（judge_b 同型）；SQL 已親驗恰回 mean_20d queue 487。零寫入。
- **A5** per-step 取末次：iteration.py 新純函式 `final_attempts(steps_json)`；close 依末次判；`gain_evidence.retried_steps` 留「曾敗」痕。r01 真實步序抄為 fixture、**舊邏輯下必紅**內建。動已結 r01 列＝Steward。

### B 帳本誠實
- **B1** 三段：寫者自收尾（run_philosophy_evolution.py 加 SIGTERM handler＋`_abort_status` 純函式＋`_abort_close` 短連線 UPDATE ... WHERE status='running'）；回填器（pgrep＋1h 雙閘不碰活引擎）；run11-19 --apply=Steward。絆線：假連線收 SQL 參數斷言謂詞、Popen 假物件斷言 terminate 先於 kill。
- **B2** 逐筆 SQL（Steward 後執行）：探針 4 筆 `cleared_by='test-artifact-20260731'`；真積壓 #4/#5 依 drain 補跑或標 superseded；#11 併 B3 裁。⚠ #2/#3 已於 07-31 09:43 清訖不在列。cleared_by 一律非人名。
- **B3** 修好再重啟（非停用）：前置 B2；decide() 加 stale-hold（age>72h ⇒ hold，判準=Steward 輕裁）；再 `systemctl --user start`。
- **B4** P0/P1 四表（principle_factor_map／philosophy_principle 等）升級 `honesty_ledger_guard`（UPDATE-GUC）；DDL 帶 `SET lock_timeout='5s'` 絕不排隊；翻 C5 裁決一部＝Steward。

### C 綠燈體系
- **C1** cron 兩行（每日 07:10 sql 型／週日連 script 型）＋manual 5 條有效期呈案（骨架備妥）。
- **C2** 沿用 `augur-audit-watchdog.timer`，由「log 末行閂鎖」改「DB 帳本三態機」（無 1 日內 PASS 才發車）；`timeout -k 60 21600` 牆鐘上限；FinMind 放量節奏=Steward。
- **C3** 三步：`_SLICED` regex 改 `.+?\.split\(` 容鏈式＋fixtures 兩則；gate_raise 6 條恆真改行為驗證（同 settle 手法）；餘量基線檔＋掛 pre-commit 第四閘（0.63s 實測；過目後掛）。
- **C4′** sink 裁定＝`~/logs/alerts.log` 追記（純 bash 零依賴；DB 表案否決——postgres 掛掉時 sink 沉默）＋週報印近 7 日 alerts；**手動 drop-in**（CR2：不跑 install_services.sh）。

### D KH 層
- **D1** 新 status 值 `'unattempted'`（誠實非終態）＋`backfill_fulltext_unattempted.py`（分批冪等零 API）＋9 處「有列＝終態」判定改「有列且 status<>'unattempted'」（行為保存）；CHECK 重建=秒級小窗。
- **D2** `discrimination_verdict(band_counts, comp_minority_masses)` 純函式：ok ⇔ band≥2 且非眾數質量≥門檻（0.02/0.05/0.10 三選項呈裁；現況 exp(H)=1.019 四案皆 fail）。絆線=真直方圖雙向紅（合格典範）。
- **D3** kh_axis_state 改逐 item 軸覆蓋證據（domain 落於 principle_domain_map/knowledge_domain_map 等工件才 ready；缺表分支 false）。
- **D4** 再晉升鎖：admit_state_guard 加「item 曾被重評降級者，升 depth 須通行證＋理由帳」；time-based 窗列次選（非證據繫結）。

### E arena 資料
- **E1** 兩案呈裁：A supersede（trigger 白名單轉移，先例 a3_threelens）／B′ 補多 h 出單（讀 pipeline 評估）。**時效：若選 B′ 須 08-03 20:00 前拍板**。
- **E2** 新表 `alpha_headline_anchor`（IDENTITY PK＋honesty guard 上閘後不可刪）；簽錨 INSERT=hugo TTY；**不得事後補造時戳**（記錄「登錄時刻」與「宣稱所指時點」兩欄分開）。
- **E3** `settle_arena_labels.py` 加 `_ledger_gaps(cal, pred_dates)` 純函式（TAIEX 日曆差集、零 hardcode 日期）＋scoreboard 印斷檔列表。
- **E4** `check_finmind_quota.py`（複用 `finmind._user_quota`，讀錶不計額度）＋arena cron 行前綴一步（不增自動鏈長）。

### F 治理
- **F1** RULING-2026-042 草稿（號碼依現況 042/AL-046）：既成事實認定＋L7.16 適用性註記；DRAFT 與施作同 commit（CR2 糾正）。
- **F2** `augur_1014_checklist_evidence_pack` 七節備料（義務原文/現況 Evidence/選項/Steward 決定欄留白）；**明文不代勾**（039 禁）。
- **F3** `execute_sunset_consequence.py`：停止=既有 kill_switch 路徑四 scope halt（誠實印讀者覆蓋）；封存=**trigger 拒寫**（非狀態欄——要的是引擎層拒絕）；重開=綁 trigger_code 檢查。首次 --apply=Steward。
- **F4** 一行 Edit（old/new 已備）：`PROPOSAL-2026-001` 句改「已於 2026-07-23 依 §8.5(b) 議決通過（AL-2026-035…MC 現行 v1.6）」。
- **F5** 三規則入 CLAUDE.md 呈案（新條號、限「新寫或改寫之保護斷言」向前生效；定版=Steward）。

### G 基礎設施（⚠未受 critic 衝突審查，執行前自查）
- **G1** `backup_database.sh`：flock 單實例（鎖檔兼「dump 進行中」公示）→ pg_dump -Fd -j4 → 驗 toc → /mnt/c 鏡像 → 輪替（白名單 regex 限定誤刪界）；cron 兩行入合批。
- **G2** 三案呈裁：A 外接碟（零授權問題）／B 加密後上 NAS（授權衝突須裁）／C 第二機（私有通道先例）；§威脅模型分層已備。
- **G3** 沙盒演練（`createdb -T template0 augur_sandbox` 全程可逆）→ 呈 P5 一次拍板 → 生產 apply＋最小接線；backfill 設計自帶 ROLLBACK 零殘留。
- **G4** hugo 一頁程序：P1 selftest RC=0 → P2 --check RC=2 且恰 3 hunks（**出現第 4 hunk 即停手判源**）→ --apply → 驗收。

### H lai／sim（⚠未受 critic 衝突審查）
- **H1** 不換尺（不動 eval_code_hash）：判讀層逐格有效性 R-CELL′ 預凍呈案（修尺前 A13 verdict 快照＝T1 絆線）；S-8 robot 語意權=Steward。
- **H2** 三件套：`derive_sim_param_schema.py`（唯讀；run 欄入 properties、summary 鍵列 x-unclassified）→ draft →首 method 入冊=hugo 親簽＋D-1；DDL（三 CHECK＋kill_switch 加 sim scope）入統一窗。

## §4 依據與可追溯

問題面 SSOT＝`reports/augur_deep_understanding_r3_20260801.md`（§八 15 佇列）＋r2 42 債；解法全文＝workflow `wf_fe396f76-6c0` journal（session 工件，本冊為其持久萃取）。未裁六項原 SSOT（`evolution_execution_plan_20260731.md` §七）由本冊 W2 承接。執行狀態以本冊 §1 狀態欄為準，完成一項勾一項（勾＝驗收指令通過，非「做了」）。

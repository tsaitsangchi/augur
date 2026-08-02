# [DRAFT 呈文] I5B-甲｜引擎世代 supersede 逐字 diff（只呈不施；run 22 前逐字過目用）

> **狀態**：DRAFT 呈文——裁決「I5B-照建議」（`I5B_stale_pending_supersede_proposal.md` 裁決登錄）明文
> 甲案繫「**run 22 前另呈引擎 diff 逐字過目**」後施作；本檔即該 diff。**本檔零碼改動、零 DDL、
> 零 DB 寫入**；所有紅綠證據出自 scratchpad 副本實跑（repo 檔未動），所有數字出自 live DB
> 現查 2026-08-02（#9/#10）。基準：git HEAD `be09735`；引擎現碼 selftest rc=0、migrate DDL selftest rc=0。
> **L6.18(c) 自我利益揭露**：AI 呈 AI 自建引擎之變更 diff；紅綠證據為 self-reported（#32(a)），
> 惟三突變驗紅之指令與輸出全文可由 hugo 本機重跑覆核；施作與否之裁決權全在 Steward。

---

## §1 現況親驗（2026-08-02 live；引用前請重跑）

- **CHECK 現值（親查 `pg_get_constraintdef`）**：`promotion_queue_queue_status_check` ＝
  `CHECK (queue_status IN ('pending_auto','applied','rejected_gate','halted'))`——**無 `superseded`**
  （I5B 呈案機械事實一，本日覆核仍真）。
- **誠實閘（親讀 `honesty_ledger_guard` prosrc）**：BEFORE **UPDATE/DELETE**（＋TRUNCATE）觸發；
  DELETE/TRUNCATE 一律拒；UPDATE 須 `SET LOCAL augur.honesty_write='on'`。**INSERT 不在閘上**
  ——故現行引擎 INSERT 無須 GUC，新增之 supersede **UPDATE 須帶 GUC**。
- **佇列現況**：pending_auto **17 列、全屬 run 21**（r3 記憶之 19 列已由 hugo 親裁 2 列 applied；
  17 列＝10 個 feature：cycle_position_252d×1、debt_ratio×5、gov_bank_net_buy_60d×2、market_cap_log×1、
  momentum_5d×1、top_holders_pct×2、volume_gini_20d/60d、volume_max_share_20d/60d、volume_surge_5_60）。
  跨 run 殘留今日＝0（與呈案 §2.4 一致）。
- **run 邊界**：run 21 succeeded（08-01 18:41 → 08-02 04:11）；**run 22 尚未存在＝施作窗現正開著**。
  kill_switch 五 scope 全 clear。
- **queue 開列處唯一**：全 repo `INSERT INTO promotion_queue` 僅 `run_philosophy_evolution.py:907` 一處
  （grep 親驗）；driver `run_evolution_iteration.py` I3 呼叫本引擎＝改本檔即覆蓋 cron 路與手動路。
- **SIM-CAL-R1 無涉澄清（criteria_text 逐字親讀）**：其正則命中 `supersede` 係 §5.3
  「換尺＝換身分…開新 gate_id、**本列**轉 superseded」——指 sim 門列自身，與 promotion_queue 零交集；
  本案不觸 sim 專章判準。

## §2 設計決定（裁決語→機械落點）

裁決語：「引擎開新世代列時自動 supersede 同 feature 舊 pending_auto」。落點：

1. **觸發＝與新列 INSERT 同一交易**（逐 map 短交易內先 UPDATE 後 INSERT）——世代交替原子性；
   冪等（該 feature 首列即清空，後續 rowcount=0，計數如實累加）。
2. **最窄謂詞三件合取**：`queue_status='pending_auto' ∧ feature=同 ∧ run_id<本 run`——
   同 run 多 principle 合法列（呈案 §2.4 型）與一切已裁列（applied/rejected_gate/halted，含 hugo
   親裁列）**永不觸碰**；機器僅關機器寫的 pending，不碰人裁（防呆記憶「機器覆寫人裁」之反面設計）。
   `run_id<` 天然跨代補抓（若某代 halt 未關，下個 clear run 一併關）。
3. **不看新列之 queue_status**：新世代重評同一 feature 後不論綠紅，舊世代 pending 皆為過期證據
   ——若僅新列 pending 才關舊列，新列 rejected 時舊 stale pending 反而存活、I5 整批照吃＝缺口未閉。
4. **kill halt 期間不動舊列**：`kill_eff == KILL_CLEAR` 才呼叫（halt＝「照跑但不採用」；緊急停時
   機器不得改寫既有列；靠 2. 之跨代謂詞於下個 clear run 自癒）。
5. **decided_by 自陳機器世代**：`superseded_by_run_<N>`（20 字＜varchar(64)）——非人簽、不代打
   （never-type-human-signature 合規）；逐列可稽。
6. **殘餘誠實揭露**：supersede 掛在「該 feature 開新列」上——若某 feature 自 `principle_factor_map`
   被移除（下輪不再開列），其舊 pending **不會被本機制關**；該罕見型仍靠丙（--queue-id 逐顆）／
   乙（邊界清理模板）備援。本機制閉合的是呈案 §2.3 實證之主型態（每 run 全量重發）。

## §3 引擎 diff 逐字（`scripts/run_philosophy_evolution.py`；四段一函式）

以下為 scratch 副本與現碼之 `diff -u` 全文（行號錨於 HEAD `be09735` 現碼）：

```diff
--- a/scripts/run_philosophy_evolution.py
+++ b/scripts/run_philosophy_evolution.py
@@ -124,6 +124,22 @@
     chk("B1:run_id 以參數傳入（非字串拼接）",
         any(p and 77 in p for p in _rec.cur.params))
 
+    # ── I5B-甲 世代 supersede(裁決 I5B-照建議;行為驗證零 DB;recording double 同 B1 先例)──
+    _q = _RecConn()
+    _q.cur.rowcount = 3
+    _n_sup = _supersede_stale_pending(_q.cur, 22, "debt_ratio")
+    _qsql = " ".join(_q.cur.sql)
+    chk("I5B:回傳 rowcount 誠實計數(非常數)", _n_sup == 3)
+    chk("I5B:最窄謂詞三件齊(pending_auto ∧ 同 feature ∧ run_id<本 run)——拔任一即紅",
+        "queue_status='pending_auto'" in _qsql and "feature=%s" in _qsql
+        and "run_id < %s" in _qsql)
+    chk("I5B:標 superseded 終態且帶誠實閘 GUC 通行證(同交易)",
+        "SET queue_status='superseded'" in _qsql
+        and "SET LOCAL augur.honesty_write" in _qsql)
+    chk("I5B:decided_by 自陳機器世代(非人簽)+參數化傳值",
+        any(p and "superseded_by_run_22" in p and "debt_ratio" in p and 22 in p
+            for p in _q.cur.params))
+
     text = Path(__file__).read_text(encoding="utf-8")
     chk("script G-NOEXEC clean", scan_noexec_text(text) == [])
     g = build_gate_json(
@@ -657,6 +673,23 @@
     return 0
 
 
+def _supersede_stale_pending(cur, run_id: int, feature: str) -> int:
+    """I5B-甲(裁決 I5B-照建議):開新世代列前,同 feature 舊 run 之 pending_auto 標 superseded。
+
+    最窄謂詞=pending_auto ∧ 同 feature ∧ run_id<本 run——同 run 多 principle 合法列、
+    已裁列(applied/rejected_gate/halted)永不觸碰(機器僅關機器 pending,不碰人裁);
+    decided_by 自陳世代供逐列稽核(非人簽、不代打)。UPDATE 過誠實帳本閘(B4-P2a)須 GUC
+    通行證,與新列 INSERT 同交易=世代交替原子性。前置 DDL:queue_status CHECK 須含 superseded。
+    """
+    cur.execute("SET LOCAL augur.honesty_write = 'on'")
+    cur.execute(
+        "UPDATE promotion_queue SET queue_status='superseded', decided_at=now(), "
+        "decided_by=%s "
+        "WHERE queue_status='pending_auto' AND feature=%s AND run_id < %s",
+        (f"superseded_by_run_{run_id}", feature, run_id))
+    return cur.rowcount
+
+
 def run_evolution(
     *,
     since: str,
@@ -871,7 +904,7 @@
             )
 
     # queue 列：local-gates 計算可能很久 → 逐筆短交易，避免長鎖
-    n_pending = n_rej = n_halt = 0
+    n_pending = n_rej = n_halt = n_superseded = 0
     verdict_tally = {"G-PROM": {}, "G-ECON": {}, "G-SIGN": {}}
     for m in maps:
         cls = feat_class[m["feature"]]
@@ -902,6 +935,11 @@
         # action 先算再裁 queue_status:demote+FAIL_SIGN → pending_auto(R3 除役通道)
         qs = decide_queue_status(gj, kill_eff, action=action)
         with db.connect() as conn, db.transaction(conn) as cur:
+            # I5B-甲:同交易先關同 feature 舊世代 pending(冪等;該 feature 首列即清空,
+            # 後續 0 列)。kill halt 期間不動舊列(halt=照跑但不採用;供下個 clear run 自癒補關,
+            # 謂詞 run_id<本 run 天然跨代補抓)。
+            if kill_eff == KILL_CLEAR:
+                n_superseded += _supersede_stale_pending(cur, run_id, m["feature"])
             cur.execute(
                 """
                 INSERT INTO promotion_queue
@@ -926,7 +964,8 @@
         )
     _ACTIVE_RUN["closed"] = True            # B1：正常關帳，abort 收尾不再介入
 
-    print(f"✓ run_id={run_id} status={final} queue pending={n_pending} rejected={n_rej} halted={n_halt}")
+    print(f"✓ run_id={run_id} status={final} queue pending={n_pending} rejected={n_rej} "
+          f"halted={n_halt} superseded_stale={n_superseded}")
     print(f"  G-PROM tally={verdict_tally['G-PROM']} G-ECON tally={verdict_tally['G-ECON']} "
           f"G-SIGN tally={verdict_tally['G-SIGN']}")
     if n_pending:
```

備註：`KILL_CLEAR` 本檔已 import（現碼第 37 行）；G-NOEXEC 禁字（下單類字面）零觸及——改後全文
經自身 `scan_noexec_text` 掃描 PASS（§6 綠燈證據內含）。

## §4 CHECK 處置兩案並陳（親查 CHECK 現無 `superseded`；建議甲-A）

### A案（建議）｜`superseded` 入 CHECK（最小 DDL ＋ 模板同步一行）

**live DDL（hugo 過目後於施作窗執行；表 ~750 列、驗證瞬時）**：

```sql
BEGIN;
SET LOCAL lock_timeout = '5s';   -- ACCESS EXCLUSIVE 搶不到即失敗、絕不排隊(#30 鎖風暴;timing DDL 前例)
ALTER TABLE promotion_queue DROP CONSTRAINT promotion_queue_queue_status_check;
ALTER TABLE promotion_queue ADD CONSTRAINT promotion_queue_queue_status_check
  CHECK (queue_status IN ('pending_auto','applied','rejected_gate','halted','superseded'));
COMMIT;
```

**模板同步（`src/augur/philosophy/evolution.py:168`；全 repo 該 CHECK 唯一 code 副本，grep 親驗；
migrate script 引 `EVOLUTION_DDL` 同源 #12，全新 DB 由此得五值）**：

```diff
--- a/src/augur/philosophy/evolution.py
+++ b/src/augur/philosophy/evolution.py
@@ -165,7 +165,7 @@
         apply_log_id    BIGINT,
         CHECK (action IN ('promote','demote','freeze')),
-        CHECK (queue_status IN ('pending_auto','applied','rejected_gate','halted'))
+        CHECK (queue_status IN ('pending_auto','applied','rejected_gate','halted','superseded'))
     )""",
```

- 模板改動不破既有自測：migrate DDL selftest 之六斷言（段數/CREATE/表名/kill/prodset CHECK）
  不釘 queue_status CHECK 內容——已以改後 DDL 串列逐條複驗全 True（scratch 實跑）。
- **既有 DB 不吃模板**（`CREATE TABLE IF NOT EXISTS` 跳過）⇒ live ALTER 為必要步、缺一不可。
- **carrier 二選一**（主 session 裁）：(i) hugo 親跑上述 psql 五行（一次性、最小）；
  (ii) 新 `scripts/migrate_promotion_queue_supersede_ddl.py`（比照 timing DDL 前例：
  `--check` 唯讀／`--apply` 冪等＋lock_timeout／`--selftest`；首提交即含矩陣 #18/#29d）——
  **兩機實況下建議 (ii)**：DESKTOP 之 DB 亦有本表舊 CHECK，若只拉新碼不 ALTER，其 run 22+ 首次
  supersede UPDATE 撞 CHECK → 該列交易炸、B1 收尾記 failed（fail-loud 非靜默，但屬可預防事故）。
- 讀端無破壞（逐支親讀）：`apply_evolution_promotions` 只選 `pending_auto`；`report_applygo_readiness`
  只列 pending；`settle_sunset_gate` 不濾 status；`audit_philosophy_feature_coverage`／
  `sync_philosophy_principle_status` 三態計數——superseded 列乾淨落於三態之外（正確語意：
  非待裁、非閘紅）。

### B案（備援）｜零 DDL：標 `rejected_gate` ＋ decided_by 註記

同 §3 diff 但 `queue_status='rejected_gate'`（CHECK 不動）。**親查後之真實代價——並非零碼改**：

- `report_triple_evolution_week.demote_fail_pending`（:49-56 親讀）＝
  `active ∧ demote ∧ rejected_gate ∧ G-PROM FAIL*` 四要件合取入「待你裁決」週報；而現行 17 列
  pending 多為 demote＋FAIL_SIGN（R3 通道）⇒ B 案關閉之舊列**逐週誤入 Steward 待裁清單**，
  須再改該報表濾 `decided_by NOT LIKE 'superseded_by_run_%'`＝第二處碼改；
- 「閘沒紅卻標 rejected_gate」與 08-01 `gate_set_migration_gsign` 同型語意債（呈案 §3乙 已自陳）；
  audit/sync 之 rejected_gate 計數自此摻假。

**建議：A案**——語意正確、讀端零改；DDL 僅一條約束換五值、風險受 lock_timeout 與空窗排程約束。

## §5 施作序（code＋DDL 同窗；窗口數學）

- **窗口**：run 21 已收（08-02 04:11）、run 22 不存在（親查）。run 22 最早機器觸發＝
  **cron `0 23 * * 1-5` 之 `run_evolution_iteration.py --run`（即週一 2026-08-03 23:00）**；
  今日（日）該 cron 不跑；`run_evolution_chain.sh`（01:30）為知識鏈、不開 evolution_run。
  ⇒ 施作窗＝現在起至 08-03 23:00（或 hugo 手動起 run 之前）；引擎現正 idle＝ALTER 無鎖競爭。
- **順序（依賴方向：DDL 先、碼後）**：
  1. live ALTER（§4-A SQL；或 migrate script `--apply`）——舊碼＋新 CHECK 無害（值未被用）；
  2. `evolution.py:168` 模板一行（A案同窗同 commit）；
  3. `run_philosophy_evolution.py` §3 diff；
  4. `--selftest` rc=0（新四鎖綠）＋ `--local-gates --dry-run` 走一遍（dry 路不進 queue 迴圈、
     驗閘算不炸即可）＋ `migrate_philosophy_evolution_ddl.py --selftest` rc=0；
  5. run 22 前快照 `SELECT run_id, queue_status, count(*) FROM promotion_queue GROUP BY 1,2` 留檔
     （§6 驗收基線）。
  逆序之害：碼先落而 DDL 未跟 ⇒ run 22 首列 supersede UPDATE 違 CHECK → 逐列交易炸、
  B1 記 failed（fail-loud，但整輪報廢）。**commit/push 依 #14 由 hugo 明示授權，本呈文不代辦。**

## §6 驗收（紅綠已實證＋run 22 後 SQL 斷言）

**已實證（scratch 副本 `i5b_mod.py`；repo 零動；hugo 可重跑覆核）**：

- **綠**：改後 `--selftest` rc=0、22/22 全 ✓（含新四鎖；含改後全文 G-NOEXEC clean）；AST parse OK。
- **紅（#35 突變驗紅，三發全紅 rc=1、各中靶 chk）**：
  | 突變 | 結果 |
  |---|---|
  | 拔 ` AND run_id < %s`（謂詞放寬＝會誤傷同 run 列） | ✗FAIL「最窄謂詞三件齊」 |
  | 拔 `SET LOCAL augur.honesty_write` 行（裸手 UPDATE） | ✗FAIL「帶誠實閘 GUC 通行證」 |
  | 拔 `queue_status='pending_auto'` 過濾（會覆寫已裁列） | ✗FAIL「最窄謂詞三件齊」 |
- 呈案證偽條件 3（誤傷同 run 合法多列）之回應：`run_id < 本 run` 謂詞使同 run 多 principle 列
  物理不可及，且該謂詞已上突變鎖（拔之即紅）。

**run 22 落地後（主 session／hugo 跑，唯讀 SQL）**：

```sql
-- (1) 跨 run 殘留歸零(本機制主張)
SELECT count(*) FROM promotion_queue WHERE queue_status='pending_auto' AND run_id < 22;   -- 期望 0
-- (2) superseded 列自陳世代且僅來自舊 run(期望≈run22 起跑時 run21 尚 pending 之列數;今日口徑 17)
SELECT run_id, count(*) FROM promotion_queue
 WHERE queue_status='superseded' AND decided_by='superseded_by_run_22' GROUP BY 1;        -- 僅 run_id<22
-- (3) 本 run 自身零 superseded(同 run 列不可及之直接證據)
SELECT count(*) FROM promotion_queue WHERE run_id=22 AND queue_status='superseded';       -- 期望 0
-- (4) 歷史已裁列不動:applied/rejected_gate/halted 各 run 計數與 §5 步 5 快照逐列相等
--     (唯一允許之 diff=舊 pending_auto → superseded)
```

stdout 面：run 22 收尾行應含 `superseded_stale=<n>`（n>0 且＝(2) 之總和；引擎自陳、可稽）。

## §7 回滾

- **碼**：兩檔同 commit ⇒ `git revert` 單發（run 邊界執行，勿在 run 進行中）。
- **DDL**：若尚無 superseded 列 ⇒ 換回四值 CHECK 即淨回滾；已有列 ⇒ 換回會被 ALTER 驗證擋下
  （fail-loud、非靜默）——屆時二選一：保留五值 CHECK（多餘值無害、零讀端依賴）或由 hugo 裁定
  該批列之改標（帶 GUC、逐列留痕）後再收約束。**不 hand-patch、不 DELETE**（表有 DELETE 拒閘）。

## §8 L6.16 四項對照（承呈案 §3甲，補實測面）

| 項 | 前→後 | 說明 |
|---|---|---|
| 人類介入點數 | 不減 | 被關列＝舊世代機器 pending，本就非人裁對象；新世代列照常等 S-i／I5 |
| 否決可達性 | 不變 | kill halt 期間 supersede 不執行（實碼 `kill_eff==KILL_CLEAR` 閘）；--queue-id 逐顆路不受影響 |
| 揭露比例 | 增 | decided_by 逐列自陳＋收尾行 `superseded_stale=` 計數 |
| 最大自動鏈長 | 不增 | 同一 INSERT 交易內之標記；未新增任何鏈節／排程／喚醒 |

## §9 Steward 決定

> **（留白待 Steward 圈選）**
> 圈選格式：`I5B-diff-施作`（＝§3 diff＋§4-A 全採、依 §5 序）／`I5B-diff-改B`（零 DDL 備援案，
> 併裁週報過濾第二處碼改）／`I5B-diff-退回`（附修改指示）。
> 施作屬碼改＋DDL：依 #14/#19 由主 session 於 hugo 拍板後執行；本呈文不施作。

---

## 過目與施作登錄（2026-08-02 晚）

> **Steward 圈選（AskUserQuestion 留痕）**：「過目通過，CHECK 採 A 案」。施作：四 hunk＋函式落齊、模板五值同步、四鎖綠＋突變紅（拔 run_id< 謂詞 rc=1）、DDL A 案上線（constraintdef 五值親驗）、裸 UPDATE 仍被誠實閘拒。DESKTOP 下次上線補跑同一冪等 DDL（migrate 模板已同源五值）。run 22 邊界起同 feature 舊 pending 自動收斂。

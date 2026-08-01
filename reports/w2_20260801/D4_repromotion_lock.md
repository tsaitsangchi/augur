# [DRAFT 呈案] D4｜admit_state_guard 再晉升鎖（GREATEST 再膨脹之機械閉鎖）

> **[DRAFT 呈案] 未經拍板不得施作。** 本檔全部 DDL／diff 僅為呈案文本；施作依 §7 Steward 決定後入 3c 統一 DDL 窗。
>
> **L6.18(c) 自我利益揭露**：本呈案由 AI（Claude Fable 5）草擬；所提之鎖約束的正是 AI 自身可觸發之自動晉升路徑（`run_kh_chain.py`／`run_knowhow_auto_admit.py`），不涉及 AI 監督機制之弱化；AI 於本案僅得草擬、比對與呈案，核准主體＝Constitution Steward。
>
> 呈案批：W2（2026-08-01）；全程唯讀親驗（零 DDL、零寫入、零 systemctl、零外部 API）。

---

## §1 問題與授權鏈

### 1.1 問題

`knowhow_auto_admit_state.admit_depth` 是顧問引文排序鍵（`rank_citations_kh_first`，深度 ≥7 排公版 works 前）。其寫入熱路徑 `upsert_state()` 以 **`GREATEST(舊值, 新值)` 單調升** 設計（`src/augur/knowledge/auto_admit.py:260`）——這使 2026-07-30 Steward 拍板之治權行為「**重評降級 145,949 件 depth 9→7**」（橡皮章 KH8 證據無效，帳＝`knowhow_depth_reevaluation`）**可被例行 drain 靜默逆轉**：

- KH8 之母體鑑別力閘現靠 **0.27% 尾巴**（非 high 僅 396/146,354）回 `ok=True`；
- 被降級的 145,945 件（現 depth 7）**最新 band 100% 仍是 high**（本檔 §2 Q5 親驗）；
- 故任何一次 `--until-empty --apply-up-to 9` 全量 drain，KH8/KH9 逐件 pass、`GREATEST` 逐件抬回 9——**降級在機械上不可持久**。

07-31 已實證：4 件被降級 item 經 `apply-up-to=9` 之 run **無任何通行證、無任何理由帳**爬回 depth 9（§2 Q3）。現行 `admit_state_guard` 只鎖「下降」與「刪除」，**上升方向裸奔**——降級是 Steward 拍板＋通行證＋145,949 列留帳的治權行為，逆轉它卻零門檻，權限不對稱。

### 1.2 授權鏈

| 環節 | 依據 |
|---|---|
| 降級之治權行為 | hugo 拍板 2026-07-30「重評 145,949 件」；留痕 `audits/KH8-REEVAL-WIDEN-20260730.md`；帳 `knowhow_depth_reevaluation` 145,949 列 |
| 風險預言→實證 | r2 預言「降級不可持久」→ r3（`reports/augur_deep_understanding_r3_20260801.md:104`）實證 07-31 再膨脹【引用；本檔 §2 以 live 現查覆核並修正其計數口徑】 |
| 解法定案 | `reports/augur_problem_solution_register_20260801.md` §3-D4：「admit_state_guard 加『item 曾被重評降級者，升 depth 須通行證＋理由帳』；time-based 窗列次選（非證據繫結）」 |
| 建議案與證偽條件 | `reports/augur_steward_adjudication_sheet_20260801.md`：「建議：再晉升鎖——證據繫結案；time-window 次選不採。證偽：若通行證流程使正當重評大量卡住（週 >10 件待人裁），加自動白名單條件」 |
| 本呈案 | W2 呈案批（2026-08-01）：親驗 live 現況＋展開為可拍板全文；施作窗＝W3-c 統一 DDL 窗 |

---

## §2 現況親驗（2026-08-01 午後現查；全部出自 live DB／repo，非抄舊數）

### Q1 深度分佈與降級帳（現況）

```sql
SELECT coalesce(admit_depth,0) d, count(*) FROM knowhow_auto_admit_state
 WHERE target_kind='item' GROUP BY 1 ORDER BY 1;
--  3 | 396
--  7 | 145948
--  9 | 6

SELECT run_id, count(*), min(at), max(at) FROM knowhow_depth_reevaluation GROUP BY 1;
-- kh-reeval-20260730152923 | 145949 | 2026-07-30 15:29:23 | 2026-07-30 15:35:35
```

降級帳全部為 `depth_before=9 → depth_after=7`、單一 run、distinct item = 145,949。

### Q2 現行閘（live 與 repo 一致）

`\d knowhow_auto_admit_state` → 兩 trigger 在位：`trg_admit_state_guard`（BEFORE UPDATE OR DELETE）＋`trg_admit_state_no_truncate`。`pg_get_functiondef('admit_state_guard')` 與 repo `scripts/migrate_admit_state_guard_ddl.py:44-62` **逐字一致**：只攔 `NEW.admit_depth < OLD.admit_depth`（通行證 `augur.admit_depth_lower='on'`）與 DELETE／TRUNCATE；**上升零檢查**。閘落地 commit `36f5d3e`（2026-07-30 15:56）。

### Q3 07-31 再膨脹實例現查覆核（**與登錄冊/r3 口徑不符處明標**）

```sql
SELECT s.target_id, s.admit_depth cur, r.depth_before, r.depth_after,
       r.at demoted_at, s.updated_at reinflated_at, s.last_run_id, s.channel
  FROM knowhow_auto_admit_state s
  JOIN LATERAL (SELECT depth_before, depth_after, at
                  FROM knowhow_depth_reevaluation r
                 WHERE r.item_id = s.target_id::bigint
                   AND r.depth_after < r.depth_before
                 ORDER BY r.reeval_id DESC LIMIT 1) r ON true
 WHERE s.target_kind='item' AND s.admit_depth > r.depth_after
 ORDER BY s.updated_at;
```

| target_id | cur | 降級 | 降級時刻 | 再膨脹時刻 | last_run_id |
|---|---|---|---|---|---|
| 277948 | 9 | 9→7 | 07-30 15:35:35 | **07-31 08:57:37** | 521810 |
| 277949 | 9 | 9→7 | 07-30 15:35:35 | 07-31 08:57:37 | 521811 |
| 277950 | 9 | 9→7 | 07-30 15:35:35 | 07-31 08:57:37 | 521812 |
| 277951 | 9 | 9→7 | 07-30 15:35:35 | 07-31 08:57:37 | 521813 |

**⚠ 口徑修正一（明標）**：登錄冊／r3 稱「07-31 **六筆爬回** depth 9」——live 親驗：**爬回（曾降級→再升）者僅 4 筆**（277948–277951）；另 2 筆 depth 9（368764＝07-31 13:20:38、368765＝07-31 13:21:31，run 521814/15）**無任何降級帳＝全新准入**，非「爬回」。正確口徑＝「6 筆現居 depth 9 ＝ 4 再膨脹 ＋ 2 新准入」。

**⚠ 口徑修正二（明標）**：r3 稱「四筆 7→9 帶 band=high **score=0.72**」——live 親驗（`layer_scores->'8'`）：4 筆再膨脹全 band=high，但 score 分別 **1.0（cite=23）／0.72（cite=1）／1.0（cite=14）／1.0（cite=6）**——0.72 者僅 1 筆；兩筆新准入才是 0.72。「橡皮章樣式」（全 band=high、0.72 底線）成立，score 數字不成立。

再膨脹之 run 帳（`knowhow_auto_admit_run` 521810–521815）`note='apply-up-to=9'`、四筆同秒——與 `run_kh_chain.py:57` 組出的 `--until-empty --apply-up-to 9` 指令一致【推定入口、run 帳無 invoker 欄故非親證】。crontab（52 行）現查**無** kh_chain／knowhow 排程＝此路目前純手動觸發，但零機械限制。

### Q4 再膨脹當時合法——閘只鎖下降

4 筆 7→9 是 UPDATE 上升，現行 guard 逐字檢視無上升分支 → **無繞閘、無 bug，是設計缺口**。層 0–7 之 layer_scores 全記 `"note":"prior_depth"`（`progressive_item` 對 d<before 蓋 pass 章，auto_admit.py:581-588）＝再膨脹連淺層都未重評。

### Q5 潛在再膨脹面（本案 blast radius）

```sql
-- 曾降級 item 之現況深度
SELECT s.admit_depth, count(*) FROM knowhow_auto_admit_state s
 WHERE s.target_kind='item' AND EXISTS (SELECT 1 FROM knowhow_depth_reevaluation r
        WHERE r.item_id=s.target_id::bigint AND r.depth_after<r.depth_before)
 GROUP BY 1;
--  7 | 145945    9 | 4

-- 仍在 7 的曾降級 item，其最新 band：
--  high | 145945   （＝100%）
```

全表 band 分佈：high 145,958／absent 380／low 16（n=146,354）→ `population_discriminates` 兩判準均由 0.27% 尾巴撐起 `ok=True`（`evidence.py:133-173` 邏輯對照親驗）。gate 現值：`auto_admit_v1` enabled=t、max_auto_depth=9、require_kh8=t、require_kh9=t。**結論：下一次全量 advance drain 在機械上會把 145,945 件全部抬回 9**——07-31 的 4 筆只是有限批次的先頭。

### Q6 熱路徑與索引前提

- `kh_reeval_item_idx`（btree item_id）**已在**——再晉升鎖之 `EXISTS` 判定為索引探測，熱路徑成本 O(log n)（145,949 列）。
- `run_batch`（`scripts/run_knowhow_auto_admit.py:93-108`）**無 per-item 例外處理、批末一次 commit**——trigger 例外會令整批 abort（§5 風險 R1 之依據）。

---

## §3 方案

三件一組：**(a) DDL 再晉升鎖**（機械閘，管一切寫入者含動態 SQL）＋**(b) 引擎配套 clamp**（行為保存，防 drain 整批 crash）＋**(c) 遷移腳本同步**（check/selftest 防假綠）。另附 (d) 四筆再膨脹之回收 SQL（獨立裁）。

### 3.0 曾降級判定——查詢子句全文（本鎖之核心謂詞）

```sql
SELECT EXISTS (
    SELECT 1
      FROM knowhow_depth_reevaluation r
     WHERE r.item_id = NEW.target_id::bigint
       AND r.depth_after < r.depth_before
) INTO _was_demoted;
```

語意：**該 item 在重評帳上存在任一「降級」列（depth_after < depth_before）即為曾降級**。再晉升（通行證授權後由本閘自動留帳）之列為 depth_after > depth_before，**不會**污染本謂詞；`kh_reeval_item_idx` 使其為索引探測。前置條件 `NEW.target_kind='item' AND NEW.target_id ~ '^[0-9]+$'`（帳表 item_id 為 bigint；非數字 target_id 不可能在帳上，跳過＝語意精確而非放行漏洞）。

### 3.1 (a) DDL 全文（建議案＝乙：token 通行證＋trigger 自動留理由帳）

通行證 GUC 設計：

| GUC | 值 | 語意 |
|---|---|---|
| `augur.admit_depth_repromote` | **非空 token**（授權參照，如 `RULING-2026-0xx` 或 `kh-repromote-<批次名>`） | 再晉升通行證；`SET LOCAL`＝交易域、commit/rollback 即失效、不外洩。**不用 'on'**——token 本身就是「誰授權」的可稽核參照，由本閘寫入理由帳 `run_id` 欄 |
| `augur.change_actor` | 操作者名 | 沿 `migrate_kh_gate_guard_ddl.py` 既例；未設則 fallback `current_user`，記入 evidence |

```sql
-- D4 再晉升鎖 DDL（呈案全文；施作於 3c 統一 DDL 窗）
-- 注意：trigger 事件不變（既有 trg_admit_state_guard 已綁本函式名），
--       核心 apply＝CREATE OR REPLACE FUNCTION（不鎖表）；重建 trigger 僅為新庫冪等路徑。
SET lock_timeout = '5s';

CREATE OR REPLACE FUNCTION admit_state_guard() RETURNS trigger AS $$
DECLARE
    _lower_pass text := current_setting('augur.admit_depth_lower', true);
    _repro_pass text := current_setting('augur.admit_depth_repromote', true);
    _actor      text := coalesce(current_setting('augur.change_actor', true), current_user);
    _was_demoted boolean := false;
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'knowhow_auto_admit_state 為准入狀態帳：DELETE 一律拒絕（只得改深度並留帳）';
    END IF;
    IF TG_OP = 'UPDATE'
       AND NEW.admit_depth IS NOT NULL AND OLD.admit_depth IS NOT NULL
       AND NEW.admit_depth < OLD.admit_depth THEN
        IF _lower_pass IS DISTINCT FROM 'on' THEN
            RAISE EXCEPTION
              'admit_depth 下降（% → %）＝撤銷既有准入宣稱：須通行證 '
              '(SET LOCAL augur.admit_depth_lower = ''on'') 且須留理由帳',
              OLD.admit_depth, NEW.admit_depth;
        END IF;
    END IF;
    -- ── D4 再晉升鎖（2026-08-01 呈案）：曾被重評降級之 item，升 depth 須通行證＋理由帳。
    --    起因＝GREATEST 熱路徑使 07-30 降級 145,949 件可被例行 drain 靜默逆轉（07-31 已實證 4 筆）。
    IF TG_OP = 'UPDATE'
       AND NEW.target_kind = 'item'
       AND NEW.admit_depth IS NOT NULL AND OLD.admit_depth IS NOT NULL
       AND NEW.admit_depth > OLD.admit_depth
       AND NEW.target_id ~ '^[0-9]+$' THEN
        SELECT EXISTS (
            SELECT 1
              FROM knowhow_depth_reevaluation r
             WHERE r.item_id = NEW.target_id::bigint
               AND r.depth_after < r.depth_before
        ) INTO _was_demoted;
        IF _was_demoted THEN
            IF _repro_pass IS NULL OR btrim(_repro_pass) = '' THEN
                RAISE EXCEPTION
                  'item % 曾經重評降級（帳＝knowhow_depth_reevaluation）：admit_depth 上升（% → %）＝再晉升，'
                  '須通行證 SET LOCAL augur.admit_depth_repromote = ''<授權參照>''（如 RULING 編號／Steward 拍板紀錄）；'
                  '本閘將以該參照自動留理由帳',
                  NEW.target_id, OLD.admit_depth, NEW.admit_depth;
            END IF;
            INSERT INTO knowhow_depth_reevaluation
                   (run_id, item_id, depth_before, depth_after, reason, evidence)
            VALUES (_repro_pass, NEW.target_id::bigint, OLD.admit_depth, NEW.admit_depth,
                    '再晉升：曾降級 item 經通行證授權升深（admit_state_guard 自動留帳）',
                    jsonb_build_object(
                        'guard',          'admit_state_guard.repromote',
                        'actor',          _actor,
                        'authorized_via', _repro_pass,
                        'last_run_id',    NEW.last_run_id));
        END IF;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION admit_state_no_truncate() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'knowhow_auto_admit_state 為准入狀態帳：TRUNCATE 一律拒絕';
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_admit_state_guard ON knowhow_auto_admit_state;
CREATE TRIGGER trg_admit_state_guard
    BEFORE UPDATE OR DELETE ON knowhow_auto_admit_state
    FOR EACH ROW EXECUTE FUNCTION admit_state_guard();

DROP TRIGGER IF EXISTS trg_admit_state_no_truncate ON knowhow_auto_admit_state;
CREATE TRIGGER trg_admit_state_no_truncate
    BEFORE TRUNCATE ON knowhow_auto_admit_state
    FOR EACH STATEMENT EXECUTE FUNCTION admit_state_no_truncate();
```

設計不變式（selftest 將逐條固化）：
1. **未曾降級 item 之升級零阻礙**（EXISTS 為前置；新 item／396 件 depth 3 者照常推進）；
2. 降級鎖與 DELETE/TRUNCATE 鎖**逐字保留**；
3. 通行證＝非空 token（空白字串不算）；留帳由閘自動完成＝**留痕機械化**，不再靠寫入者紀律；
4. 自動留帳列 depth_after > depth_before，**不回饋污染**「曾降級」謂詞。

### 3.2 (b) 引擎配套 clamp（逐檔 diff 計畫；與 DDL 同窗、**先 code 後 DDL**）

**檔 1：`src/augur/knowledge/auto_admit.py`**

- **:105 之後**（`get_admit_depth` 後）新增 helper：

```python
def repromotion_locked(cur, item_id: int) -> bool:
    """item 曾被重評降級（knowhow_depth_reevaluation 有 depth_after<depth_before 列）→ D4 再晉升鎖。"""
    if not _table_exists(cur, "knowhow_depth_reevaluation"):
        return False  # 帳表不存在＝從未有降級治權行為；DB trigger 為最終防線
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM knowhow_depth_reevaluation "
        "WHERE item_id=%s AND depth_after < depth_before)",
        (int(item_id),),
    )
    return bool(cur.fetchone()[0])
```

- **:616-618 之間**（`progressive_item` 逐層迴圈結束後、`raw_v` 計算前）插入 clamp：

```python
    # D4 再晉升鎖之引擎側配套：曾降級 item 不因 KH8 band=high 自動爬回；
    # 誠實記 held、深度維持原值（無升→trigger 靜默）；再晉升唯 Steward 通行證路徑。
    if depth > before and repromotion_locked(cur, item_id):
        layer_scores["repromote_lock"] = {
            "verdict": "held",
            "note": f"曾重評降級：{before}→{depth} 之再晉升須 Steward 通行證（D4）；本輪維持 {before}",
            "layer": "REPROMOTION_LOCK",
        }
        actions.append({"layer": "repromote", "action": "held_at_floor"})
        depth = before
```

（dry-run 亦 clamp＝報告誠實；`layer_scores` 增一非數字鍵 `repromote_lock`——施作前 grep `layer_scores` 消費者確認無 `int(key)` 迭代；本輪親查 `auto_admit.py`／`run_knowhow_auto_admit.py` 內無此型消費。）

**檔 2：`scripts/run_knowhow_auto_admit.py`**

- **:111-120**（`run_batch` 收尾統計）增 `repromote_held` 計數並印出：

```python
        held = sum(
            1 for r in results
            if r.get("ok") and any(
                a.get("action") == "held_at_floor" for a in r.get("actions", []))
        )
        print(f"done ok={ok_n} advanced={advanced} unchanged={stuck} repromote_held={held}")
```

（回傳 dict 加 `"held": held`；`run_until_empty` 之 stuck-queue 判定不變——held 者 `advanced` 不計，行為即正確。）

### 3.3 (c) `scripts/migrate_admit_state_guard_ddl.py` 同步（diff 計畫）

- **:41**：增 `REPRO_GUC = "augur.admit_depth_repromote"`。
- **:43-78**：`DDL` 常數替換為 §3.1 全文（含 `SET lock_timeout='5s'` 前置）。
- **:81-95 `check()`**：除 trigger 在位檢查外，**加函式版本探針**（防「trigger 在、函式舊」假綠——現行 check 只看 trigger 名，函式體換不換它都綠）：

```python
    cur.execute(
        "SELECT prosrc LIKE '%admit_depth_repromote%' FROM pg_proc WHERE proname='admit_state_guard'"
    )
    row = cur.fetchone()
    repro = bool(row and row[0])
    print(f"再晉升鎖：{'✓ 函式含 repromote 分支' if repro else '✗ 函式為舊版（升方向裸奔）'}")
    ok = ok and repro
```

- **:106-125 `_selftest()`**：
  - **必改**：`:121` 現行斷言 `"NEW.admit_depth > OLD.admit_depth" not in DDL`（「升級不受阻」）在新 DDL 下**必紅**——改為「升鎖僅限曾降級者」之形：`DDL.count("NEW.admit_depth > OLD.admit_depth") == 1 and "r.depth_after < r.depth_before" in DDL`。
  - **新增**：repromote GUC 名一致；通行證非空判定（`btrim` in DDL）；自動留帳（`INSERT INTO knowhow_depth_reevaluation` in DDL）；`target_kind = 'item'` 限定；`~ '^[0-9]+$'` 防呆；`SET lock_timeout` 前置；降級鎖與 DELETE/TRUNCATE 原文逐字仍在。
- **docstring**：補再晉升鎖一段與兩通行證對照表；執行指令矩陣不變（#18/#29(d)）。

### 3.4 (d) 07-31 四筆再膨脹之回收 SQL（獨立裁決項；建議回收）

```sql
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL augur.admit_depth_lower = 'on';      -- 降級通行證（既有閘）
SET LOCAL augur.change_actor = 'hugo';         -- Steward 親跑；AI 不代打
UPDATE knowhow_auto_admit_state
   SET admit_depth = 7, updated_at = now()
 WHERE target_kind='item'
   AND target_id IN ('277948','277949','277950','277951')
   AND admit_depth = 9;                        -- 冪等前提：仍為 9 才動
INSERT INTO knowhow_depth_reevaluation (run_id, item_id, depth_before, depth_after, reason, evidence)
SELECT 'kh-redemote-D4-20260801', v.i, 9, 7,
       '回收 07-31 GREATEST 再膨脹（無通行證之再晉升；KH8 殘餘二：band=high 非 per-item 強證據）',
       jsonb_build_object('via','D4_repromotion_lock 呈案 §3.4',
                          'reinflated_at','2026-07-31 08:57:37+08',
                          'run_ids', jsonb_build_array(521810,521811,521812,521813))
  FROM (VALUES (277948),(277949),(277950),(277951)) v(i);
COMMIT;
```

射程明界：**僅 4 筆再膨脹**；368764／368765 係新准入非再膨脹，**不在回收射程**（其 depth 9 之效力繫於 KH8 殘餘二之後續案，非本案）。執行者＝hugo（涉治權行為之逆轉之回復；「不代打人簽」紀律）。

---

## §4 選項與建議案

| 案 | 內容 | 評 |
|---|---|---|
| **甲（最小）** | 通行證 `='on'`（鏡射降級閘）；理由帳靠寫入者紀律 | 與既有降級閘對稱、diff 最小；但留痕仍靠紀律——正是「防呆機制自己靜默失效」型缺口；07-31 實證熱路徑寫入者**不會**自發留帳 |
| **乙（建議）** | **token 通行證＋trigger 自動留帳**（§3.1 全文） | 留痕機械化：每筆再晉升必然落 `knowhow_depth_reevaluation` 一列、`run_id`＝授權參照可稽核；成本＝授權升深時每列 +1 INSERT（未授權時零成本、未曾降級者僅 1 次索引探測） |
| 丙（次選，**已裁不採**） | time-based 再晉升冷卻窗 | 非證據繫結——時間到自動可再膨脹＝換湯不換藥；判決書已明文不採，列此僅存檔 |
| 回收子項 R1（建議） | §3.4 回收 4 筆至 7 | 與降級治權行為一致；帳目閉環 |
| 回收子項 R2 | 不回收、僅本檔留痕 | 4 筆 depth 9 續居引文排序深帶——與「該 depth 不成立」之 07-30 認定矛盾，不建議 |

**建議案＝乙＋R1**；施作序＝**先 (b) code、後 (a) DDL（3c 窗）、末 R1**（見 §5-R1 排序理由）。

**證偽條件**（判決書原文照錄）：若通行證流程使正當重評大量卡住（**週 >10 件待人裁**），加自動白名單條件。度量載體＝`run_knowhow_auto_admit.py` 新增之 `repromote_held` 計數（週報可讀）；另一向證偽＝若 KH8 修出真 per-item 鑑別力後 Steward 授權全量再評，token 路徑一次交易可放行全批（`SET LOCAL` 交易域），**不構成流程瓶頸**。

---

## §5 風險與回滾

| # | 風險 | 緩解 |
|---|---|---|
| R1 | **鎖先行而引擎未配套 → advance drain 首批 crash**：`run_batch` 無 per-item savepoint（run_knowhow_auto_admit.py:93-108），trigger 例外令整批 rollback、腳本裸 traceback；145,945 件曾降級者現全 band=high＝首批必踩 | **施作序固定：先 (b) 引擎 clamp、後 (a) DDL**。clamp 不依賴 trigger 存在（謂詞同源），code 落地即止血；DDL 隨 3c 窗封死動態 SQL 旁路 |
| R2 | 正當再晉升被卡（KH8 真修好後） | token 通行證路徑＋§4 證偽條件（週 >10 件加白名單）；`SET LOCAL` 批次放行不構成量瓶頸 |
| R3 | 熱路徑效能：每次 item 升深 UPDATE 多 1 次 EXISTS | `kh_reeval_item_idx` 已在（§2 Q6）＝索引探測；未升深／非 item 之 UPDATE 零額外成本 |
| R4 | `knowhow_depth_reevaluation` 本身無 guard——任何寫入者可 INSERT 假降級列使任意 item 被鎖（DoS 型）、或 DELETE 降級列使鎖失效 | 誠實記載為**殘餘債**：該表屬 B4 族「UPDATE/INSERT 裸缺口」後續批次（honesty guard 上閘），本案不擴權順手處理（#3 最小邊界）；DELETE 向已有紀律但無機械閘 |
| R5 | superuser `DISABLE TRIGGER` 殘道（單一角色終態下物理不可封） | 與 V-5／L7.16 既知殘餘同款；F1（RULING-2026-042）明載不粉飾；本閘防的是「例行路徑靜默逆轉」，非防蓄意 superuser |
| R6 | DDL 窗鎖風暴 | 核心 apply＝`CREATE OR REPLACE FUNCTION`（不取表鎖）；trigger 重建段有 `SET lock_timeout='5s'` 快敗不排隊（#30 教訓）；建議 3c 窗仍避開 advance drain 進行中 |

**回滾**：單一 `CREATE OR REPLACE FUNCTION` 回舊版全文即可（舊版＝§2 Q2 親驗之 live 現行版，原文在 `scripts/migrate_admit_state_guard_ddl.py:44-62`＝git 可溯）；零資料遷移、零列損失；閘已自動留下之再晉升帳列**不刪**（append-only）。code 側回滾＝git revert 兩檔。R1 回收之回滾＝同型 UPDATE 9 復原＋留帳（仍須通行證，合設計）。

---

## §6 驗收判準（機械可判；全部於 3c 窗內或其後執行）

1. **函式版本**：`SELECT prosrc LIKE '%admit_depth_repromote%' FROM pg_proc WHERE proname='admit_state_guard'` → `t`。
2. **負測（窗內、可逆）**：`BEGIN; UPDATE knowhow_auto_admit_state SET admit_depth=8 WHERE target_kind='item' AND target_id='277948'; ROLLBACK;`（若 R1 已回收該筆為 7）→ **必拋** `再晉升，須通行證` 例外。
3. **正測（窗內、可逆）**：同上但先 `SET LOCAL augur.admit_depth_repromote='ACCEPTANCE-PROBE-D4';` → UPDATE 成功**且**同交易內 `SELECT count(*) FROM knowhow_depth_reevaluation WHERE run_id='ACCEPTANCE-PROBE-D4'` = 1；`ROLLBACK` 後該列消失（同交易域證明）。
4. **未曾降級者不受阻（窗內、可逆）**：取任一 depth 3 item（396 件），`BEGIN; UPDATE ... SET admit_depth=4 ...; ROLLBACK;` 無 GUC → **成功不拋**。
5. **遷移腳本**：`python3 scripts/migrate_admit_state_guard_ddl.py --selftest` → GREEN（含 §3.3 新斷言全數）；`--check` → PASS 且印「✓ 函式含 repromote 分支」；對**舊函式庫**跑 `--check` 須 FAIL（防假綠探針生效）。
6. **引擎行為**：下一次 advance 輪（`run_kh_chain.py --run --phase advance`）rc=0、summary 印 `repromote_held=N`（N>0 預期）、**`knowhow_auto_admit_state` 中曾降級者 depth 分佈不變**（§2 Q5 查詢 9 之計數不增）。
7. **終態守恆（持續判準）**：§2 Q3 再膨脹偵測 SQL 回 **0 列**（R1 拍板回收後）或凍結於 4 列不增（R2）；任何新列＝閘破防、立即呈報。

---

## §7 Steward 決定欄（留白）

| 決定項 | 選項 | 決定 | 簽署 |
|---|---|---|---|
| 再晉升鎖方案 | 甲／**乙（建議）**／丙（已裁不採） | ☐ | |
| 07-31 四筆處置 | **R1 回收（建議）**／R2 留現狀 | ☐ | |
| 施作窗 | 3c 統一 DDL 窗（先 code 後 DDL） | ☐ | |
| 備註 | | | |

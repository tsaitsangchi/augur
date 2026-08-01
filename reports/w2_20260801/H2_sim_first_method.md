# [DRAFT 呈案] H2｜sim 候選物理死鎖解鎖——derive_sim_param_schema 腳本＋首 method 入冊程序＋DDL 入統一窗

> **[DRAFT 呈案] 未經拍板不得施作。**
> **自我利益揭露（L6.18(c)）**：本呈案由 AI 起草，sim 軸含 `origin='llm_local'`（本地 AI 產候選）路徑，
> 即 AI 為自身參賽鋪路；人簽三處（§3.3 ★標）皆 hugo 親為、AI 機械上不可代填，且候選天花板 TR-C／
> `is_synthetic=true` 依專章 §2.3 釘死，本呈案不觸碰該上限。
>
> 設計 SSOT＝`reports/augur_problem_solution_register_20260801.md` §3 H2
> ＋`reports/augur_steward_adjudication_sheet_20260801.md` 「八、lai／sim」H2
> ＋`reports/augur_local_ai_sim_evolution_impl_plan_20260731.md`（§2.1 B-1／§5.2／§9 D-1）。
> 親驗時點＝2026-08-01 下午；repo HEAD＝`e00135c`；本呈案全程唯讀（零 DDL、零 DB 寫入）。

---

## §1 問題與授權鏈

### 1.1 問題：候選物理死鎖（B-1）與 param_schema 空懸（U-2）

專章（`gp_86c8063fc688`，enacted 07-31）生效但軸完全空轉：
`sim_evolution_candidate.method` FK → `simulation_method_registry(method)`，而 registry **0 列**
⇒ **任何候選在 DB 層寫不進去**。註冊一法又須過三道鎖：
`chk_smr_registered_signed`（status='registered' ⇒ `approved_by`/`approved_at`/`gate_ref` 三者非空）
＋`gate_ref` FK→`governance_proposal`（**已 enacted 之治權提案**）＋`param_schema` NOT NULL
（20 個史料 method 之參數規格**尚未反推**＝impl plan U-2）。
另 `evolution_kill_switch` 無 `sim` scope（且有 CHECK 封閉四值——見 §2.3 **親驗新事實**），
本軸唯一煞車＝`global`（會連停三軸）。

### 1.2 授權鏈（P5.W2／L6.5-L6.8 四要件）

| 要件 | 內容 |
|---|---|
| (a) 範圍 | 呈案起草：唯讀查證＋scratchpad 寫入；**不施作、不寫 repo、不寫 DB** |
| (b) 期限 | 本批（W2 呈案批）交付即結 |
| (c) 可撤銷 | 隨時 |
| (d) 參照 | 登錄冊 §1 H2 列（W2；「呈案→Steward（D-1＋親簽）」） |

裁決權專屬 Steward；人簽三處機械上唯 hugo 可為（governance_queue TTY 閘＋psql 親跑）。

---

## §2 現況親驗（2026-08-01 現查）

### 2.1 sim 八表＋registry 全 0 列（與登錄冊一致）

```sql
-- sim_evolution_candidate / sim_calibration_eval / sim_evolution_verdict /
-- sim_evolution_iteration_ledger / sim_llm_proposal / sim_realized_outcome /
-- sim_run_link / simulation_method_registry  → 全部 count = 0（親驗）
```

`evolution_prereg_gate` 之 `axis='sim'`＝**0 列**（節點二未成立；屬 D-2 另案，非本呈案射程）。
`evolution_axis` 含 `sim`（5 軸：lai/program/raw/sim/tw）；專章提案 `gp_86c8063fc688` status=**enacted**。

### 2.2 史料素材 `mc_simulation_run`：540 列／20 method（與登錄冊一致）

```sql
SELECT count(*), count(DISTINCT method) FROM mc_simulation_run;   -- 540 | 20
-- 分佈：block_bootstrap 261、iid_bootstrap 261、其餘 18 法各 1 列
-- 覆蓋：53 target、asof 全部=2026-05-31（FREEZE 錨）、19 個 horizon、seed 單值
```

**summary 抽 3 筆之鍵集（現查）**：

```sql
-- iid_bootstrap（首列 mc_98035e023e6848d6）與 block_bootstrap（mc_1740cbf712cf2d48）同形：
  {cone, disclaimer, horizon_td, last_close, note_p_up, sim_stat_p_terminal_up, terminal}   -- 7 鍵
-- garch_fhs（mc_cc86f7a7a74d2a12）完全異形（17 鍵）：
  {cell, disclaimer, dropped_dates, effective_window_td, fit_diag, kind, maxdd, n_members,
   note_candidate, note_policy, note_window_bias, p_maxdd_lt_info, p_maxdd_lt_policy,
   panel_date, policy_threshold, terminal, window_actual_maxdd}
```

**鍵形穩定度**：iid/block 各有 **2 種鍵形**（非單一）；單列法各 1 種。
⇒ summary 鍵**異質且會漂**——這正是「summary 鍵只列 x-unclassified、不自動入 properties」的實證依據。

**參數欄實查**（derive 之素材）：iid/block 之 `n_paths` 單值 {10000}、`horizon_td` 六值
{21,30,42,60,63,126}、`block_len_td`：block=21／iid=NULL；`mc_simulation_run_method_check` CHECK
封閉 20 個 method 值。

### 2.3 與登錄冊/舊計畫**不符處（明標）**

1. **`mc_baseline` 一名全 repo＋DB 查無**：僅出現於呈案單 H2 建議句。20 個史料 method、
   `mc_simulation_run_method_check` 值域、任何 code 皆無此鍵。若照字面以 `mc_baseline` 為 method key
   入冊：零史料對應（D-5 回填斷）、且寫 run 會被 method CHECK 擋（需第 4 條 DDL 加寬）。
   **本呈案讀作「MC 基線法」之描述語，正名＝`iid_bootstrap`**（§4 甲案；乙案保留字面）。
2. **impl plan §5.2「kill_switch 新增一列（非新表）、hugo 親跑 INSERT 即可」與 live 不符**：
   親驗 `chk_kill_switch_scope` CHECK 封閉 `{tw,lai,raw,global}`——**單靠 INSERT 必被 CHECK 擋**，
   須先 DDL 加寬（登錄冊 H2「DDL…kill_switch 加 sim scope 入統一窗」已正確反映；此處補「為什麼」）。
3. **kill_switch 現有 4 列之 `set_by`＝migration 腳本名**（`migrate_philosophy_evolution_ddl`／
   `migrate_evolution_v2_ddl`），**非 hugo**——「INSERT 須 hugo 親簽」無先例支撐；`set_by` 語意＝
   狀態設定者之 provenance（誠實記「誰做的」），非授權人簽。詳 §4 選項丙。

### 2.4 code 側封閉集（改碼點親驗）

- `src/augur/philosophy/evolution.py:242`：`KILL_SCOPES = ("tw", "lai", "raw", "global")`。
- `scripts/set_evolution_kill_switch.py:31` import KILL_SCOPES；`:52` selftest 硬斷言四值封閉集；
  `:87-88`/`:111` 皆引 KILL_SCOPES（改 `:242`＋`:52` 兩處即全鏈同步）。
- 人閘 CLI `scripts/governance_queue.py`：submit（AI；trigger 凍結）→ **approve/reject（TTY＋親手打簽名，
  非 TTY 一律拒）** → enact（AI 標記）。proposal_id＝`gp_`+sha256(title+diff)[:12]。
- `sim_evolution_candidate.gate_ref` **nullable**（親驗 information_schema）⇒ registry 一有列，
  候選列即物理可寫（合法評估仍須 D-2 之 prereg gate，procedural 非 physical）。

---

## §3 方案（三件套）

### 3.1 件一｜`scripts/derive_sim_param_schema.py` 腳本規畫（唯讀；解 U-2）

**命名**：動作動詞片語（#18）；**零寫入**（stdout 為主，`--out` 選填寫檔至指定路徑）。

**執行指令矩陣（首次提交即含，#29d）**：
```
python scripts/derive_sim_param_schema.py                      # 無參數：現況（20 法×列數×鍵形數摘要，唯讀）
python scripts/derive_sim_param_schema.py --method iid_bootstrap   # 單法 param_schema 草案 JSON → stdout
python scripts/derive_sim_param_schema.py --all                # 全 20 法草案
python scripts/derive_sim_param_schema.py --all --out <dir>    # 寫檔（僅明示路徑才寫）
python scripts/derive_sim_param_schema.py --selftest           # 零 DB 紅綠
```

**推導規則（確定性、可溯源 #9/#10）**：
- **run 欄入 properties**：參數欄限 `horizon_td`／`n_paths`／`seed`／`block_len_td`
  （`target_id`/`asof_date` 為資料座標、`summary` 為輸出、`git_sha`/`created_at` 為 provenance——皆非參數）。
  每個 property 附 `x-observed`：{distinct values, min, max, n_rows}（全由 DB aggregate 現查）。
  全列非 NULL 之欄入 `required`；全列 NULL 之欄（如 iid 之 `block_len_td`）**不入** properties、
  列 `x-excluded` 並註「該法無此參數（史料全 NULL）」。`additionalProperties: false`。
- **summary 鍵列 x-unclassified**：逐法列出**每一種鍵形**（鍵集合＋該形列數），
  一鍵不漏、一鍵不分類——**輸出欄之語意分類屬人審，腳本禁代判**（防 AI 擅自定義語意入冊）。
- `x-provenance`：{SQL 原文, 查詢時點, git_sha, n_rows}。

**iid_bootstrap 草案輸出形（依 §2.2 現查值預覽）**：
```json
{"title": "iid_bootstrap param_schema（derive 草案；未經人審不生效）",
 "type": "object",
 "properties": {
   "horizon_td": {"type": "integer", "x-observed": {"values": [21,30,42,60,63,126], "n_rows": 261}},
   "n_paths":    {"type": "integer", "x-observed": {"values": [10000]}},
   "seed":       {"type": "integer", "x-observed": {"values": [42]}}},
 "required": ["horizon_td", "n_paths", "seed"],
 "additionalProperties": false,
 "x-excluded": {"block_len_td": "史料全 NULL（iid 無此參數）"},
 "x-unclassified": {"summary_key_shapes": [ {"keys": ["cone","disclaimer","horizon_td","last_close",
   "note_p_up","sim_stat_p_terminal_up","terminal"], "n_rows": "…"}, {"keys": ["…第二鍵形…"], "n_rows": "…"} ],
   "note": "summary 鍵＝輸出非參數；不自動入 properties，逐鍵分類屬人審"},
 "x-provenance": {"source": "mc_simulation_run", "asof": "<查詢時點>", "git_sha": "<HEAD>"}}
```

**函式規畫**（library 級純函式可測；#20 之 (b)）：
`observed_param_profile(cur, method) -> dict`（DB 聚合）／`summary_key_shapes(cur, method) -> list`／
`draft_schema(profile, shapes) -> dict`（**純函式**，selftest 標的）／`main`。
**絆線（三規則；新回歸鎖先驗紅）**：以現查 iid/block profile 為 fixture——
①iid 之 `block_len_td` 必不入 required/properties、block 之必入（紅測＝天真版把 NULL 欄也入 required）；
②任何 summary 鍵若出現在 properties ⇒ 斷言 FAIL（禁自動分類，先驗紅）；
③同輸入兩次呼叫 byte-identical（確定性）。

### 3.2 件二｜首 method 入冊程序（逐步；★＝hugo TTY 親簽點，AI 機械上不可代）

前提：§7 拍板（D-1 粒度＋method key 案）。以下以甲案（`iid_bootstrap`）行文。

| 步 | 執行者 | 動作 | 產物／驗證 |
|---|---|---|---|
| 0 | Steward | §7 圈選：D-1（建議「首件逐件」）＋method key（建議甲＝iid_bootstrap） | 拍板碼 |
| 1 | AI | `derive_sim_param_schema.py --method iid_bootstrap` 產草案 JSON | stdout 草案＋x-provenance |
| 2 | **hugo（人審）** | 過目草案：values 是否合理、required 是否過嚴、x-unclassified 逐鍵知悉 | 修訂指示或「照案」 |
| 3 | AI | `governance_queue.py --submit --kind other --title "sim 首法註冊：iid_bootstrap" --diff-file <註冊 payload 全文：method/family/purpose/param_schema/tilt_free 論證＋本呈案路徑>`（KINDS 無 method_registration 值，用 other 並於 title 明示——見 §5 風險 5） | `gp_XXXX`；submit 即 trigger 凍結 |
| 4 | **★hugo TTY** | `python scripts/governance_queue.py --approve gp_XXXX`（TTY 閘＋親手打簽名；非 TTY 一律拒） | status=approved、decided_by 人簽留痕 |
| 5 | AI | `governance_queue.py --enact gp_XXXX`（AI 落地標記，不寫 decided_by） | status=**enacted**（gate_ref FK 前提達成） |
| 6 | **★hugo TTY（psql 親跑）** | 執行下方 INSERT（首法不新寫註冊 CLI，人簽路徑零新碼；`register_simulation_method.py` 留給餘 19 法批次時再落，屆時比照 governance_queue isatty 閘、**不設人名旗標**） | registry 1 列、`chk_smr_registered_signed` 滿足 |
| 7 | AI | 驗收探針（§6-2）：交易內 INSERT 候選→ROLLBACK，證 B-1 已解、零殘留 | rc=0 |
| 8 | AI | 登錄 audit（`audits/`）＋登錄冊 §1 H2 勾（驗收過才勾） | 留痕 |

**步 6 之 INSERT 全文（hugo 親跑；`<>` 佔位由當步實值替換）**：
```sql
INSERT INTO simulation_method_registry
  (method, family, purpose, param_schema, tilt_free, status,
   gate_ref, approved_by, approved_at, git_sha, note)
VALUES
  ('iid_bootstrap', 'bootstrap',
   '歷史日報酬 iid 重抽之分位錐基線（模擬非預測；純歷史重抽零 tilt；史料 261 列對應）',
   '<步 1-2 經人審之 param_schema JSON>'::jsonb,
   true, 'registered',
   '<gp_XXXX>', 'hugo', now(), '<git rev-parse --short HEAD>',
   '呈案單 H2 所稱 mc_baseline 之正名＝iid_bootstrap；首法入冊（D-1 逐件）');
```

### 3.3 件三｜DDL 全文（**入統一 DDL 窗 3c**，與 D4/B4/E2 同窗；不在本案單獨排窗）

三 CHECK＋`arms_covered` 欄（impl plan §5.2 承接）＋kill_switch scope 加寬（§2.3-2 親驗新事實）：

```sql
BEGIN;
SET lock_timeout = '5s';           -- 絕不排隊（#30 鎖風暴教訓）；timeout 即整包回滾零殘留

-- (1) 專章 §2.3 機械化：llm_local 候選必攜 synthetic 標記（八表 0 列，驗證零成本）
ALTER TABLE sim_evolution_candidate
  ADD CONSTRAINT chk_sce_llm_is_synthetic
  CHECK (origin <> 'llm_local' OR is_synthetic);

-- (2) 專章 §3.6 NULL 缺口封閉：終態輪必須聲明目標函數基礎
ALTER TABLE sim_evolution_iteration_ledger
  ADD CONSTRAINT chk_seil_gain_basis_on_terminal
  CHECK (status NOT IN ('succeeded','failed') OR gain_basis IS NOT NULL);

-- (3) 專章 §3.4 五臂完備性：promoted 之判決須涵蓋五臂（robot 為加嚴第六臂、不強制）
ALTER TABLE sim_evolution_verdict ADD COLUMN IF NOT EXISTS arms_covered text[];
ALTER TABLE sim_evolution_verdict
  ADD CONSTRAINT chk_sev_five_arm_floor
  CHECK (verdict <> 'promoted' OR
         arms_covered @> ARRAY['live','ceiling','floor','shuffled','mismatched']::text[]);

-- (4) kill_switch scope 值域加 sim（現 CHECK 封閉四值＝INSERT 之物理前提；表僅 4 列、驗證瞬時）
ALTER TABLE evolution_kill_switch DROP CONSTRAINT chk_kill_switch_scope;
ALTER TABLE evolution_kill_switch
  ADD CONSTRAINT chk_kill_switch_scope
  CHECK (scope = ANY (ARRAY['tw'::text,'lai'::text,'raw'::text,'global'::text,'sim'::text]));

COMMIT;
```

**DDL 後之 DML（sim 煞車列；見 §4 丙案二擇一）**：
```sql
INSERT INTO evolution_kill_switch (switch_id, state, set_by, reason, scope)
VALUES (5, 'clear', '<丙案裁定：腳本名 或 hugo>', 'sim 軸開軸前置：緊急煞車作用點', 'sim');
```

**同批 code diff（與 DDL 同一變更集）**：
- `src/augur/philosophy/evolution.py:242`：`KILL_SCOPES = ("tw", "lai", "raw", "global", "sim")`。
- `scripts/set_evolution_kill_switch.py:52`：selftest 封閉集斷言同步為五值
  （**先驗紅**：DDL/改碼前跑必 FAIL，落地後轉綠＝真行為鎖）；`:87-88`/`:111` 隨 import 自動同步。

**誠實記載**：sim scope 列落地後**初期零消費者**（`run_sim_evolution_iteration.py` 尚未存在，W5 才接線）
——不得宣稱「本軸已受煞車保護」；此列＝作用點預置（r3 對 lai scope「零消費者」同型批評，不重蹈）。

---

## §4 選項與建議案

**D-1｜20 法入冊粒度**
| 案 | 內容 | 評註 |
|---|---|---|
| **甲（建議）** | **首件逐件**（僅 iid_bootstrap 走 §3.2 全鏈）；餘 19 法待首輪 sim 候選跑通後，以**一件包裹提案**收（每列 gate_ref 指向同一提案、note 逐列註明；status='retired' 逐列可退不受包裹牽連） | 首件把「提案→親簽→enact→入冊→候選可寫」全鏈跑通一次＝死鎖診斷之實證；20 次 TTY 親簽＝純儀式成本 |
| 乙 | 20 件逐件 | 親簽 ×20，儀式化風險（人審 <1 分鐘/法＝rubber-stamp） |
| 丙 | 一次包裹 20 法 | 首鏈未經實證即放大 blast radius；param_schema ×20 一次人審品質難保 |

**method key｜「mc_baseline」之處置（§2.3-1 明標之不符）**
| 案 | 內容 | 評註 |
|---|---|---|
| **甲（建議）** | 正名＝**`iid_bootstrap`**；registry note 註「呈案單所稱 mc_baseline」 | 261 列史料直接對應（D-5 回填可用）；零額外 DDL |
| 乙 | 字面新鍵 `mc_baseline` | 零史料、寫 run 須第 5 條 DDL 加寬 `mc_simulation_run_method_check`、derive 腳本無素材可推——三重代價換一個名字 |

**丙｜kill_switch sim 列之 `set_by`**
| 案 | 內容 | 評註 |
|---|---|---|
| **甲（建議）** | 統一窗 migration 腳本寫入、`set_by='migrate_sim_constraints_ddl'` | 與現 4 列先例一致（§2.3-3 親驗）；`set_by`＝誠實 provenance——腳本做的就寫腳本名，寫 'hugo' 反而是代打人簽（never-type-human-signature 紀律） |
| 乙 | hugo psql 親跑、set_by='hugo' | impl plan 原文如此；惟 'clear' 初始列不授權任何事，親簽無授權語意、僅儀式 |

**證偽條件**：
1. （呈案單原文）入冊後首輪 sim 候選仍寫不進（FK 之外另有暗礁）⇒ 死鎖診斷不完整——
   以 §6-2 探針提前偵測。
2. 若包裹批次（餘 19 法）之人審出現 rubber-stamp 樣態（單法審 <1 分鐘）⇒ 包裹粒度過粗、退回逐件。
3. 若 derive 草案兩次執行不 byte-identical、或 iid/block 鍵形數再增 ⇒ 推導不確定／上游 writer 在漂，
   先鎖 writer 再入冊。
4. （甲 method key 案）若 D-5 裁「另取新窗不回填」⇒「史料對應」理由弱化，乙案代價重估。

---

## §5 風險與回滾

| # | 風險 | 說明與緩解 |
|---|---|---|
| 1 | registry 錯列**不可刪**（`smr_no_delete`/`smr_no_truncate` trigger 親驗在位） | 回滾＝`UPDATE … SET status='retired'`（值域含 retired；判死留檔合憲）。故 param_schema **人審在 INSERT 前**（步 2） |
| 2 | DDL 窗鎖衝突 | `SET lock_timeout='5s'` 絕不排隊；timeout ⇒ 整包 BEGIN…COMMIT 回滾零殘留；**排窗避開 pg_dump**（#30 dump 期間禁 DDL；G1 備份 cron 上線後查其時窗） |
| 3 | DROP+ADD `chk_kill_switch_scope` 之空窗 | 同一交易內完成，外部不可見中間態；表 4 列驗證瞬時 |
| 4 | sim 煞車列零消費者期 | §3.3 已誠實記載；W5 driver 落地時以 `WHERE scope IN ('sim','global')` 接線並補行為級測試 |
| 5 | governance kind 值域無「方法註冊」 | 用 `other`＋title 明示；若 Steward 認為應擴 KINDS，屬另案小修（不阻本案） |
| 6 | `mc_simulation_run_method_check` 未來債 | 新候選若產新 method key，寫 run 會被 20 值 CHECK 擋——**已知、不在本案修**（首法 iid_bootstrap 在值域內）；留待首輪候選設計時併 D-4（H-1 黑名單→白名單）一起裁 |
| 7 | 回滾總則 | code diff 可 revert；DDL 可逆（DROP CONSTRAINT／恢復四值 CHECK——惟 sim 列一經 INSERT 不可 DELETE〔delonly trigger〕，回滾＝state 維持 clear＋CHECK 不收窄）；enacted 提案不可撤＝新提案正路（回滾不對稱認知錨） |

---

## §6 驗收判準（機械可判）

1. **入冊成立**：
   `SELECT method, family, status, approved_by IS NOT NULL AND approved_at IS NOT NULL AND gate_ref IS NOT NULL AS signed FROM simulation_method_registry`
   ＝恰 1 列 `iid_bootstrap | bootstrap | registered | t`；
   且 `SELECT status FROM governance_proposal WHERE proposal_id=<gp_XXXX>`＝`enacted`。
2. **B-1 解除探針（零殘留）**：
   ```sql
   BEGIN;
   INSERT INTO sim_evolution_candidate (candidate_id, method, spec, spec_sha, origin, git_sha)
   VALUES ('probe_b1_unlock', 'iid_bootstrap', '{"horizon_td":21,"n_paths":10000,"seed":42}'::jsonb,
           'probe_'||md5(random()::text), 'human', 'probe');
   ROLLBACK;
   ```
   rc=0（FK 通過）；隨後 `SELECT count(*) FROM sim_evolution_candidate`＝0（零殘留）。
3. **DDL 在位**：`pg_constraint` 含 `chk_sce_llm_is_synthetic`／`chk_seil_gain_basis_on_terminal`／
   `chk_sev_five_arm_floor`；`sim_evolution_verdict.arms_covered` 欄存在；
   `pg_get_constraintdef` 之 `chk_kill_switch_scope` 含 `'sim'`。
4. **煞車列**：`SELECT scope, state FROM evolution_kill_switch WHERE scope='sim'`＝`sim | clear`；
   `venv/bin/python scripts/set_evolution_kill_switch.py --selftest` rc=0（五值斷言、曾驗紅留證）。
5. **derive 腳本**：`--selftest` rc=0（§3.1 三絆線，含先驗紅留證）；
   `--method iid_bootstrap` 連跑兩次 byte-identical；`check_cmd_matrix.py` 對其零缺漏（#29d）。
6. **negative 驗證**（CHECK 真會咬）：交易內
   `INSERT … origin='llm_local', is_synthetic=false` 必被 `chk_sce_llm_is_synthetic` 拒（後 ROLLBACK）。

---

## §7 Steward 決定欄（留白）

- [ ] H2-同意（三件套照案：D-1 甲「首件逐件」＋method key 甲「iid_bootstrap 正名」＋丙 甲「set_by=腳本名」＋DDL 入統一窗 3c）
- [ ] H2-改採＿＿＿＿（D-1：甲/乙/丙；method key：甲/乙；set_by：甲/乙）
- [ ] 步 4/步 6 親簽時點另約：＿＿＿＿＿＿
- 簽署：＿＿＿＿＿＿　時點：＿＿＿＿＿＿

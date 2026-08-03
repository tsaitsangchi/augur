# augur 深化理解報告 r4（2026-08-03 09:xx）——優化地基・第四輪

> **性質**：[I] 全專案現況之深化理解，作為後續優化之依據。**不創設治權判準**、不改任何 [N] 文字。
> **承接**：r0（07-30 optimization_base）→ r1（07-30 deep_understanding）→ r2（07-31 重開機核驗）→ **r3（08-01 晨）** → 本檔 r4。
> **方法**：十區平行分域探索（治權／工具規則與記憶／進化引擎／閘體系／知識層／sim 軸／預測與資料／排程維運／變更圖／債務帳）＋三路對抗核驗；
> 合成者對**每一則載重數字重新現查**（psql／實跑腳本／git），不抄任何報告舊值。
> **本檔紀律（承 r3，本輪加一）**：
> 1. 綠燈一律先問「**這個綠燈量的是不是它宣稱在量的東西？**」
> 2. 引用任何數字必附**口徑**——本專案至少有四個量已被證實「一名多義」（見 §3.4）。
> 3. **self-reported（CLAUDE #32a）**：本檔一切判讀為 AI 自陳，非「世界如此」。可機械覆核者一律附覆核指令；未附指令者即為推論。
>
> **本檔取代**：同路徑之 2026-08-03 08:29 初稿（四路探索版）。初稿框架（三十秒定錨表／不可談判不變式／架構圖／優化禁區）已併入本檔 §1、§8；其三處已過期敘述於 §7.3 具名更正。

**接續讀序**：`HANDOFF.md` → **本檔（r4）** → r3（債表與假綠方法論仍高價值）→ r2（重開機核驗史料）→ `reports/augur_construction_understanding_20260713.md`（建構 how）→ 治權五檔（版號一律 `ls docs/` 現查）→ `constitution-mcp`。

---

## §0 一頁摘要（30 秒讀者）

**這個專案是什麼**：一個「**先立法、再長智慧**」的世界建構工程。憲章（L0 元憲章 `AUGUR-MC v1.6` ＋ L1–L7 規格 ＋ 領域三件套 ＋ L6 工具規則 `CLAUDE.md v1.35`）先於程式碼定義何謂「真」、何謂「可宣稱」；程式碼與資料庫是這套法的物理載體。判準先凍結、證據後產生、人類是唯一能簽字的節點。

**今天的三個里程碑（r3 以來 48 小時）**
1. **引擎首度自掙晉升**——`cycle_position_252d`、`lending_fee_rate_mean_30d` 於 08-02 19:49 經八閘全綠＋hugo 逐顆 `--queue-id` 親簽入 prodset，`active` 由 2 → **3**。這是本專案「候選→證據→人門→晉升」全鏈**第一次靠引擎自己跑通**。
2. **sim 軸上膛**——`SIM-CAL-R1` 門 hugo 親簽 approved（雙級指紋 server 端覆算**全合**），四件套落地且 selftest 全綠，P0 候選 `simc_r1_iid_baseline` 就位。時鐘尚未起跑（anchor 待今晚 08-03 收盤入庫）。
3. **WM.36 合規弧啟動**——World Concept Registry 五物件於 08-02 21:23 落地；vendor 直綁止血閘上崗成為 pre-commit 第五閘。

**今天最該知道的三個壞消息**
1. **`RULING-2026-043` 不存在**——11＋張表的誠實閘架構以它為法源施作，`constitution/` 無該檔、`AMENDMENT-LOG` 無對應 AL；生產碼有 **18 處**引用（6 個檔）。覆核：`ls constitution/RULING-2026-043*` → No such file。
2. **在 worktree 內 commit 完全不過五閘**——親驗：`cd <worktree> && bash ops/githooks/pre-commit` → **rc=0**、只印「無 …/venv/bin/python，略過」。現有三個 worktree 皆無 venv，且它們注入給 agent 的 `CLAUDE.md` 是 **v1.31／v1.32**（main 為 v1.35）。
3. **sim 的 W5→W3 資料契約已斷**——runner 寫 `terminal_q_grid.p` 為 `list[99]`，evaluator 只認 `dict`。親驗：`normalize_q_grid(runner 實形)` → **None**。今晚首格照樣落地，但三個月後 K=3 齊時會算出 `n_valid=0`，而錯誤訊息會說「等 settle 波」。

**一句話的現況**：**判準的品質已經遠遠超過判準的執行力**。八閘、雙級指紋、append-only 帳本、五道 pre-commit、單向棘輪都寫得很對；但它們的自動觸發面只有一個 pre-commit hook（可被 `--no-verify` 與 worktree 兩條路繞過）、零 CI、292 支 selftest 只有 3 支在排程、26 支 pytest 零排程。**下一輪優化的最高投報不是加新閘，是讓已有的閘真的會自己跑、並且紅燈時真的會紅。**

---

## §1 這個專案現在是什麼

### 1.1 兩半＋第三塊（概念骨架，r3 以來未變）

| 半 | 是什麼 | 成功定義 | 不是什麼 |
|---|---|---|---|
| **半-1 預測** | 台股**相對強弱**＋經濟終關＋方向機／arena | 經濟價值（非裸 IC）；確立級唯 `direction_gate` 過門 | 絕對漲跌占卜；live API 硬前提 |
| **半-2 素養／顧問** | know-how → 句 → 嵌 → 檢索 → 本地 LLM | license 允許之**可答終態**＋誠實 decline | 入庫＝進化核准；cite 率＝過閘 |
| **第三塊 審議／自進化** | TWEVO／PME／RAWEVO／LAIEVO／sim ＋ 本地審議引擎 | 預註冊閘＋雙綠／八閘＋**人門** | 自動下單；AI 代簽治理 |

**一條合法成長路**：候選 → 可證偽／樣本外／經濟終審 → **人類授權門** → 晉升或判死留檔 → 後果回流。
域（台股／ERP／太陽能）只是足跡，不是特權通道。

### 1.2 世界 L0–L7 現行版本（2026-08-03 現查）

| Layer | 規格 | 版本 | 現查 |
|---|---|---|---|
| 0 | `constitution/META-CONSTITUTION.md`（AUGUR-MC） | **v1.6** | `:15` 版本欄 |
| 1 | WORLD-MODEL（WM） | v1.0 | `specs/*.md` 前 6 行 |
| 2 | ONTOLOGY | v1.0 | 同 |
| 3 | IDENTITY | v1.0 | 同 |
| 4 | KNOWLEDGE-SYSTEM（KS） | **v1.1** | 同 |
| 5 | COGNITIVE-KERNEL | v1.0 | 同 |
| 6 | AGENT-RUNTIME | **v1.2** | `CLAUDE.md`＝工具落點 |
| 7 | INFRASTRUCTURE | v1.0 | 同 |

領域三件套：靈魂 `docs/系統核心思想_v1.10.0.md`／原則精華 `docs/原則精華_v1.12.0.md`／領域大憲章 `docs/系統架構大憲章_v1.54.0.md`；下位專章 `docs/模擬方法自進化專章_v1.0.md`。
工具規則 `CLAUDE.md` **v1.35**（`head -1 CLAUDE.md` 現查；#35 回歸鎖三規則）。
裁決 **40** 份（`ls constitution/RULING-2026-*.md | wc -l`）；修憲登錄 **46** 條（`grep -c "^## AL-" constitution/AMENDMENT-LOG.md`）。

### 1.3 「一條路」的物理現況

r3 以來最重要的結構事實：**這條路現在真的走通過一次**。

```
principle_factor_map
   └─► run_philosophy_evolution --local-gates（I3，7–10 小時）
        └─► promotion_queue（663 列：rejected_gate 620／applied 26／pending_auto 17）
             ├─ 八閘全綠者（run 21：3 列 = q555/556/599，2 個相異 feature）
             └─► hugo --queue-id N --allow-apply --gate-ref TWEVO-APPLY-go
                  └─► evolution_apply_log（25 列）
                       └─► evolution_production_feature_set（active 3／removed 8）
```

`active` 三顆（現查 `SELECT feature,set_status,source_run_id,source_queue_id,apply_log_id,principle_id FROM evolution_production_feature_set`）：

| feature | source_run | queue | apply_log | principle |
|---|---|---|---|---|
| `cycle_position_252d` | 21 | 556 | 25 | 98 |
| `inst_cumflow_position_120d` | 6 | 253 | 16 | 77 |
| `lending_fee_rate_mean_30d` | 21 | 599 | 26 | 107 |

**但這條路仍是六條並行的其中一條**（記憶 `augur-path-six-parallel-gap`）：tw／raw／lai／sim／program 五軸各有自己的 ledger 與 gate 表，`evolution_iteration_ledger` 表上甚至並存兩條互相包含的 axis CHECK（`ANY(ARRAY['tw','lai','raw'])` 與 `= 'tw'`）。四軸 ledger 現況：tw **5** 列／raw **2** 列／lai **0** 列／sim **0** 列。

---

## §2 十區逐區現況與關鍵事實

> 全部數字為 2026-08-03 09:0x–09:3x 現查。凡與既有報告不符者，於本節標【報告說 X／live 實為 Y】。

### Z1 治權層

**已生效**：`RULING-2026-042`（L7.16 單一角色衝突登錄）於 08-01 hugo 簽核（`constitution/RULING-2026-042-L716-SINGLE-ROLE-CONFLICT.md:59` `- [x] 准…（簽：hugo，日期：2026-08-01）`），登錄 AL-2026-046。回歸鎖 `tests/test_l716_conflict_registered.py` 2 passed。

**四個治權層漂移（皆現查）**：

1. **RULING-2026-043 無本體**。`ls constitution/RULING-2026-043*` → 不存在；`grep -c "^## AL-"` 之最末為 AL-2026-046（歸 042）。但 `grep -rn "RULING-2026-043\|B4-043" scripts src audits` → **18 處／6 檔**（`scripts/migrate_honesty_guards_ddl.py`、`scripts/migrate_sim_evolution_ddl.py`、`scripts/migrate_steward_qledger_ddl.py`、`src/augur/audit/evolution_ledger_ddl.py`、`audits/B4-P2A-…`、`audits/B4-P2B-…`）。唯一原始留痕＝呈案檔內之「Steward 圈選」文字。
2. **CS 版本自我漂移三檔**：
   - `docs/compliance/CS-系統架構大憲章_v1.54.0.md`：檔名 v1.54.0／`:1` 標題 **v1.53.0**／`:13` `spec-version: v1.53.0`
   - `docs/compliance/CS-系統核心思想_v1.10.0.md`：檔名 v1.10.0／`:1` 標題 **v1.9.0**／`:15` `spec-version: v1.9.0`
   - `docs/compliance/CS-CLAUDE.md`：`:15` `spec-version: v1.35`（正確），但 `date` 停在 07-23
3. **CS-系統核心思想內部自相矛盾（WM.42）**：`:10` 明寫「幅度級 E[r] 於 A.38 閉集之模態定性是否須依 WM.52 作 Profile minor 增列，**列 open-tension 呈 Steward 裁**」；同檔 `:22` `open-tensions: []`、`:55`「本檔與 MC 無已登錄未解緊張」。同一份檔對「有沒有待裁事項」給出兩個相反答案。
4. **領域大憲章修訂表雙現行**：`grep -oE "\| (SUPERSEDED|\*\*ACTIVE\*\*|\*\*現行\*\*) \|$" docs/系統架構大憲章_v1.54.0.md | sort | uniq -c` → SUPERSEDED **54**／`**ACTIVE**` **1**（`:446` v1.49.0）／`**現行**` **1**（`:451` v1.54.0）。根因是降級步驟按字串 `**現行**` 比對，漏掉寫成 `**ACTIVE**` 的那列。

**治權帳簿分裂**：`grep -c "系統架構大憲章" constitution/AMENDMENT-LOG.md` → **1**。領域大憲章 v1.47.0→v1.54.0 共八版（07-25～07-31，含三次判準變更）零 AL 登錄；其中僅二版有 DB 側 `governance_proposal` 留痕。`governance_proposal` 全表 **6** 列（5 enacted／1 rejected，`decided_by` 全為 hugo）——而 DB 不隨 git 跨機，此軸留痕有隨機器遺失之虞。

**治權層的機械檢查射程極窄**：`tools/constitution_lint/report.py:51-61` 之 `corpus_files()` **只 glob `specs/*.md`**。`constitution/`（46 條 AL、40 份裁決）、`docs/` 三件套、`docs/compliance/` 七份 CS **一份都不在射程**。`report` 子命令 rc=**0**（並自陳 `git HEAD 45ea88d+dirty ⚠ 工作區有未提交變更，本輸出無法僅由該 SHA 重現`）；`--selftest` 子命令 rc=**1**，291 條斷言中僅 1 條 FAIL（輸出第 131 行：「G10 界線：`### TR.Z …（DRAFT）` 之殘留不由本檢查代 Steward 認定」）。因這一條 FAIL，pre-commit 刻意不掛它 ⇒ **291 條治權斷言目前零自動觸發點**。

**Steward 人裁佇列從未有人裁**：`steward_question_ledger` 1,425 列（superseded 845／queued_for_claude 270／awaiting_hugo 159／pending 151）；`resolved_by` 分布＝NULL 580／`rules_v1_classify` 371／`rules_v3` 352／`rules_v3_sweep` 96／`rules` 24／`rules_v3_sweep_awaiting` 2 —— **`resolved_by='hugo'` 為 0 列**。`triage='decision'` 198 列中 **159 列仍 awaiting_hugo**，最舊 `asked_at`＝**2026-06-22**。

### Z2 工具規則與記憶

- `CLAUDE.md` main＝**v1.35**；三個 worktree＝`can-use-ca1439` **v1.31**／`project-analysis-report-fc3448` **v1.32**／`zai-ma-9f972d` **v1.31**（`for w in .claude/worktrees/*/; do head -1 $w/CLAUDE.md; done`）。v1.32 版**仍以生效文字載已被 #34 反向廢止的「非必要不 fan-out」**，且缺 #33（禁阻塞等待迴圈）／#34（平行度拉滿）／#35（回歸鎖三規則）。
- **記憶層雙向一致**（正面事實）：活記憶與 `handoff_memory/` **各 79 檔、內容全同**（`python3 sync_memory.py` → 「✓ 一致」）。
- **project-memory 索引正在追趕**：`.project_memory/index.db` 現查 `built_at=2026-08-03T08:08:08`、**files 358／chunks 4,123**。【Z2 材料於 08:43 量到 26／527；同一日 40 分鐘內已增至 358 檔 ⇒ indexer 在跑，該區「26/1,825」之債務敘述已部分自癒，但仍未全覆蓋。】
- `CLAUDE.md` 自身仍留過期硬編數：`:127`「2026-07-11 稽核 **137/137**」——live 為 **467/467**。
- **條號前綴紀律之最尖銳一例**：`CLAUDE.md:62`「把模組核心不變式固化成**回歸鎖 #15**」——本檔 #15＝PR/遠端，回歸鎖之真正住所是新設的 **#35**。`:126`「三敵人零容忍（#1／#8／#15）」在本檔對映為「Read before Edit／報告誠實／PR 遠端」，語意全毀。紀律本文（`:12`）自承「存量之逐處補前綴列殘餘待辦」且**無任何 lint**。
- `HANDOFF.md` 數字漂移：`:26` 稱「13 個 enabled user unit ＋ **12 條 crontab**」——unit 部分現查**仍成立**（6 service ＋ 7 timer ＝ 13），crontab 現查為 **15**（`crontab -l | grep -c '^[^#]'`）。`:7` 快照時點寫 2026-07-30，內文最新節已到 08-02。
- `HANDOFF.md:53` 之接續讀序**已指向本檔 r4**（即本檔為當前 SSOT 入口）。

### Z3 進化引擎

- `GATE_IDS` 已為**八閘**（`src/augur/philosophy/evolution.py:28-37`，含 `G-SIGN`，註記「G-SIGN 入閘 2026-08-01（A3 Steward 拍板）」）。run 21 之 `config_json` 現查 `gate_set_rev=8g-sign-v1`、`mode=local_gates`。
- run 21 之 111 列閘態分布（現查 GROUP BY）：`FAIL/FAIL/PASS` 47｜`FAIL_SIGN/FAIL/FAIL` 16｜`SKIP/SKIP/SKIP` 15｜`PASS/FAIL/PASS` 12｜`FAIL/FAIL/FAIL` 11｜`FAIL/PASS/PASS` 5｜**`PASS/PASS/PASS` 3**｜`FAIL/PASS/FAIL` 2。
- `evolution_run` **18** 列（succeeded 8／failed 10／**running 0**）——r3 之「9 列殭屍 running」已清。`evolution_deferred_work` 9 列、**未清 0**。
- `evolution_apply_log` **25** 列、max id=**26**、**id 23 缺號**（`EXCEPT` 現查）。
- **可溯源鏈斷點（現查）**：`lending_fee_rate_mean_20d` 之 `source_queue_id=487`、`apply_log_id=24`，而 log 24 的 `queue_id` 是 **311**。q487 為唯一一筆 `queue_status='applied'` 而 `apply_log_id IS NULL` 者（`decided_by='hugo'`，08-01 18:32 手工）。
- **一筆值得留檔的誠實範例**：q311 的 `decided_by` 逐字為 `hugo(對話拍板)〔claude 繕打,不冒充親簽 §8.1〕`——這正是 `never-type-human-signature` 紀律在資料層的正確落法。
- `evolution_iteration_ledger` 5 列，**`apply_allowed` 全 f、`gate_ref`／`source_run_id` 全 NULL**（現查）——#26 授權四要件之留痕在正規欄位上是空的。
- **方向衝突四列（現查，最毒的一個）**：
  ```sql
  SELECT q.queue_id,q.principle_id,m.direction,q.gate_json->'G-PROM'->'evidence'->>'expected_direction'
  FROM promotion_queue q JOIN principle_factor_map m USING(principle_id,feature)
  WHERE q.run_id=21 AND m.direction::text <> q.gate_json->'G-PROM'->'evidence'->>'expected_direction';
  ```
  → q562(p116, map=+1, gate=−1)／q563(p123, +1／−1)／q643(p116, −1／+1)／q644(p123, −1／+1)。
  成因：`gate_cache` 以 feature 為鍵，方向取自最小 `principle_id` 那一列。目前四列因 G-ECON=FAIL 而 rejected；**只要 G-ECON 轉 PASS，就會用反方向的證據把假說判 validated**。
  相關：`factor_direction_ruling` 僅 2 列（hugo 07-28 對話拍板），而 p123 的兩列 map 建於 07-29（裁決之後、方向與裁決相反、未列入裁決文字）。`principle_factor_map` 零業務 CHECK、零業務 trigger。
- **整批路完全不受武裝閘約束（親驗）**：`single_apply_gate`（`scripts/apply_evolution_promotions.py:68-81`）於 `queue_id is None` 時 `return True, "batch mode（既有語意）"`。實跑 `venv/bin/python scripts/apply_evolution_promotions.py --dry-run`（零旗標）→ **`✓ applied=17 skipped=0`**（含 16 筆 FAIL_SIGN demote ＋ 1 筆 promote）。
- `:304` 之 kill switch 只讀 `scope IN ('tw','global')`——按下 `lai`／`sim`／`raw` 煞車後晉升 APPLY 仍放行。
- `feature_sign_check` 現查 **40 列／36 feature**（PASS 23／FAIL 17，max `checked_at`＝2026-08-02 04:11:19）——r3 之「0 列」已作廢。
- `feature_values` **38 feature／8,540,331 列**；`feature_candidate_values` **11 feature／390,274 列**，而全 repo 無任何路徑把候選值搬進 `feature_values`（漏斗 `scripts/verify_candidate_promotion.py` 從未被 driver 呼叫）⇒ **`dual_green_n` 目前沒有成長來源**。
- `philosophy_principle`：validated **3**／sign_refuted **7**／untested **44**。

### Z4 閘體系

- **DB trigger 普查**：非內部 trigger **116** 支／**63** 張表（public 表 relkind='r' **334**、`pg_tables` **335**）／**34** 個 guard 函式；`tgenabled` **全為 `'O'`**，`ALWAYS`＝**0**。
- `honesty_ledger_guard`（UPDATE 須 GUC 通行證）掛 **25** 表；`honesty_delete_only_guard` 掛 **9** 表。
- **116 支 trigger 可由一句 session GUC 全部靜音**（親驗，`BEGIN; SET LOCAL session_replication_role='replica'; SHOW …; ROLLBACK;` → 回 `replica`）。唯一登入角色 `augur` 為 superuser（`pg_roles` 僅 `augur`／`postgres`、皆 rolsuper=t）；DB 內 **0 個 event trigger、0 條 rule、0 張 RLS 表** ⇒ 無任何機制可攔此路，且**事後 `pg_trigger.tgenabled` 仍是 `'O'`、鑑識查不到痕跡**。
- **pre-commit 五閘（主 repo 逐支取真 rc，未經 pipe）**：
  | 閘 | rc | 輸出 |
  |---|---|---|
  | `check_treaty_refs.py` | 0 | 治權引用稽核：全綠 |
  | `check_cmd_matrix.py` | 0 | 受檢 **467** 支／缺漏 0／豁免 0 |
  | `check_false_assertions.py --gate` | 0 | 無新增（基線容忍 **20** 條存量） |
  | `check_vendor_binding.py --gate` | 0 | 無新增（基線容忍 **130** 條指紋／**172** 處存量） |
  | `#8 AST`（`check_isolation()`） | — | `[]` |
- **五閘在 worktree 全部靜默跳過（親驗，可重現）**：於 `.claude/worktrees/project-analysis-report-fc3448` 內 `bash /home/hugo/project/augur/ops/githooks/pre-commit` → **rc=0**、輸出「pre-commit: 無 …/venv/bin/python，略過（請先 pip install -e .）」。而 `git rev-parse --git-path hooks` 在 worktree 內解析為共用之 `/home/hugo/project/augur/.git/hooks` ⇒ **hook 確實會被觸發、但走 `exit 0` 這條**。
- **零 CI**：`.github/workflows` 不存在。pre-commit 是唯一自動觸發點，且 `--no-verify` 可繞（hook 自己在失敗訊息中寫出該繞法）。
- **`reconcile_audit.py` 之 coverage_gap 假綠仍在**：`:157` `passed = vm == 0 and ex == 0 and not inc`——未納 `coverage_gap`；全檔對 `verdict(` 之唯一命中在 `:150` 且是**字串內文**，即 CLI 真的不呼叫 library 判式。正確判式住在 `src/augur/audit/reconcile.py:587`（`… and not coverage_gap`）且有回歸鎖——**修好的判式住在沒人呼叫的函式裡**。
- **與之相連的一筆現場證據**：`attestation_result` 最新列（id=10，08-01 18:43，driver=`daily_maintenance --heal`）`passed=**t**` 而 `missing_in_db=**11,145**`。watchdog 現讀此帳本判態，日誌連續印「冷卻中(最新 PASS@08-01 18:43)」。
- `tests/test_l716_conflict_registered.py` 只斷言「檔案存在＋含 `L7.16`＋含 `AL-2026-046`」（`:49-54`）——**把簽核欄從 `[x]` 改回 `[ ]` 測試仍綠**；且不在 pre-commit 五閘內。
- **軟閘層排程覆蓋率**：`crontab -l | grep -c pytest` ＝ **0**（26 支 pytest 檔零排程）；週一 08:40 僅跑 3 支 MCP `--selftest`。

### Z5 知識層

- 水位（現查）：`knowledge_item` **285,227**／`knowledge_item_text` **158,532**／`knowhow_auto_admit_state` **146,352**／`knowledge_staging` **395,471**／`knowledge_fulltext_status` **141,316**。
- **KH0 兩把尺（現查同一句 SQL）**：未評（無 state 列）＝**138,875（48.69%）**；無原文＝**138,826**。
- depth 分布：3→396／4→2／**7→145,952**／9→2。
- **KH8 鑑別力閘現為關閉**：`population_discriminates` 現跑回 `ok=**False**`（`band_minority_mass=0.002706 < 0.05`，n=146,354，耗時 **0.33s**）。
  【**r3 說 KH8「閘實際是開的、靠 0.27% 尾巴 ok=True」／live 實為 ok=False**——判準已改為 `MIN_MINORITY_MASS=0.05`（D2 中庸案），深度優先排序**已關**。但 `DEEP_KH_FLOOR=7` 且 145,952 件已寫死 depth 7，母體的退化排序原封不動等在那裡。】
- **KH0 破口在現行碼下無路可補**：兩個唯一的 state 列產生者都硬性要求有全文——`src/augur/knowledge/auto_admit.py:719` `JOIN knowledge_item_text x ON x.item_id=i.item_id`、`src/augur/knowledge/ingress_kip.py:92` `EXISTS (SELECT 1 FROM knowledge_item_text t …)`。而憲章 v1.53.0 已撤回「無原文豁免」⇒ `run_kh_chain.py --run --phase advance` 是一個**永遠紅、且紅得不會變綠**的閘。
- **全文管線只完成「誠實標記」、未完成「推進」**：`unattempted` **121,389** 列，四桶＝`pending_oa_queue` **90,426**／`no_resolver` **21,484**／`pending_entity_queue` **9,477**／`local_no_text` 2；而 crontab 與 timer **沒有任何一項**跑 `fetch_oa_fulltext.py`／`fetch_entity_fulltext.py`／`run_kh_chain.py`。
- **週更排程實質空轉（現查決定性證據）**：`augur-knowhow-refresh.service` 帶 `--domain finance`，而 `domain='finance'` 在 `knowledge_item`／`knowledge_query`／`knowledge_source` **三表皆 0 列**。同時刻全域真實 `staging pending`＝**102,039**（最舊 `fetched_at`＝2026-07-02 14:49、最新 2026-08-03 03:06）。
- **D3 軸判準與可答性反相關**：`knowledge_kh4_state` ready **19,475**／pending **142,448**；而 `answer_status='eligible'` 者中 pending **142,443**、ready 僅 **3,556**（2.4%）。唯一 100% 可答的 `erp_tiptop` 域不在映射工件內故恆 pending。
- 隔離不變式：`check_isolation()` → `[]`（零違規）。但 `src/augur/audit/import_isolation.py` 檔內自陳：單一角色整併後 `augur_predict` role 退役，**本 AST／字面閘現為唯一閘**，動態組字串 SQL 不再有 DB 層攔截。

### Z6 sim 軸

- **門全合**：`SIM-CAL-R1` axis=sim／status=approved／approved_by=hugo／approved_at=2026-08-02 19:49:40。**雙級指紋 server 端覆算全合**（現查一句 SQL：`criteria_sha` 對 `criteria_text` 之 sha256 → `t`；`criteria_text` 末行嵌入之 `thresholds_sha` 對 `criteria->'thresholds'` 之 sha256 → `t`）。
- 八表水位：`simulation_method_registry` 1／`sim_evolution_candidate` 1／`mc_simulation_run` **540**／其餘六表全 **0**；`evolution_prereg_gate` **3** 列。
- **時鐘尚未起跑**：`TaiwanStockPriceAdj` TAIEX `max(date)=2026-07-31`；`count(*) WHERE date > '2026-08-02'` ＝ **0** ⇒ anchor 待今晚 20:00 cron 把 08-03 收盤入庫。
- 四件套 `--selftest` **全部 rc=0**（propose／runner／settle／evaluator）。
- **W5→W3 資料契約已斷（親驗）**：
  ```
  runner _q_grid() → type=list, len=99
  normalize_q_grid({'terminal_q_grid':{'unit':'x','p':<list99>}}) → None
  ```
  evaluator `normalize_q_grid`（`scripts/evaluate_sim_calibration.py:124-130`）只認 `p` 為 dict。**而該檔 `:742-744` 的自測項字面寫著「q_grid 巢狀形（runner 實形 unit+p 子鍵）可解」、`:126` 註解寫「2026-08-02 契約對齊親驗」——兩處都宣稱已對齊真實 runner，卻用手寫的錯形狀當 fixture，於是永遠是綠的**（CLAUDE #35(1) 之射程內新犯）。
- **W4 判決工具不存在**：`scripts/decide_sim_verdict.py` 未建，`sim_evolution_verdict`／`sim_evolution_iteration_ledger`／`sim_llm_proposal` 三表零 writer。專章 §5.1「判死留檔・永不靜默消失」在 DB 層無落點。
- 三張 sim 證據表（`sim_calibration_eval`／`sim_realized_outcome`／`sim_run_link`）**只有 delete-only 閘、無 UPDATE 閘**——它們恰好是「用來證明能力宣稱」的表。

### Z7 預測與資料地基

- `direction_gate`：evaluated_fail **12**／approved **11**／superseded **6**——**無 `evaluated_pass` 狀態列** ⇒ 確立級仍全紅，禁「可交易／確立級」宣稱。
- `TaiwanStockPriceAdj` 至 2026-07-31（日更白名單路徑有效）。
- `validation_evidence` **19** 列＝green **16**（manual 5＋script_exit 1＋sql 10）／red **3**（script_exit 1＋sql 2）。
  【**記憶 `augur-three-gate-strengths` 說「green14/red5」／live 實為 green16/red3**——`E1_raw_reconcile_exit` 已轉綠。】
  **`validation_evidence` 中與 sim 相關者 0 列**（`WHERE evidence_id ILIKE '%sim%' OR claim ILIKE '%sim%'` → 0）——最新、最治權敏感的一軸是唯一沒有自動哨兵的軸。
- **備份現況（r3 債 #12 已部分清償，但異地層現為零）**：
  - 週六 07:30 cron 已掛：`bash scripts/backup_database.sh --run`
  - `~/db_dumps/` 現有兩份 11G dump（`augur_20260731_postmerge_Fd`、`augur_20260801_weekly_Fd`）
  - `~/logs/backup.log` 記 08-01 那輪「✓ 11G / 2696 物件 / 352s」「✓ 鏡像完成」
  - **但 `/mnt/c/database/` 現查為空目錄**（mtime 08-03 08:21）；`bash scripts/backup_database.sh`（唯讀狀態模式）自己也印「鏡像 /mnt/c/database: **(無)**」
  - 該腳本檔頭誠實自陳：「本支解檔案級/vhdx 級；碟亡層須異裝置（G2 呈案）——**不假裝解決**」

### Z8 排程與維運

- `crontab -l | grep -c '^[^#]'` ＝ **15**（r3／HANDOFF 記 12）。`install_cron.sh --check` → **rc=0「✓ 一致」**——r3 債 #15（週報檔名凍死 `evolution_week_20260727.md`）**已清償**，live 週報檔現為 `~/logs/evolution_week_20260802.md`。
- enabled user unit **13**（6 service：admin/advisor/chat/ollama/probability/qdrant ＋ 7 timer：admission-assist／ata-advance／audit-watchdog／drain-deferred／embed-catchup／knowhow-refresh／l2-deliberation）。
- TWEVO cron：週一至五 23:00 `run_evolution_iteration.py --run --slot-wait 10800`，**刻意不帶 `--allow-apply`**。今日為週一 ⇒ 今晚 23:00 即 run 22（亦即 I5B supersede 之首次生效點）。
- RAWEVO 週六 09:00；三軸週儀表週日 09:00；證據帳本重驗每日 07:10（週日 07:40 含 script_exit 型）；備份週六 07:30。
- **R6 週掃視有可見性缺口**：`scripts/report_triple_evolution_week.py:347` 之 digest 查詢過濾 `gate_ref='V2-AUTOADVANCE'`。近 7 日 apply_log 之 gate_ref 分布現查＝**V2-AUTOADVANCE 20／TWEVO-APPLY-go 2／HUMAN-PROMOTION 1** ⇒ **08-02 的兩顆自掙晉升與 07-29 的人工晉升完全不出現在 Steward 的週掃視清單上**。

### Z9 規模與變更圖

`scripts/*.py` **327** 支｜`reports/*.md` **300**｜`audits/*.md` **200**｜`src/augur/` **16** package｜`check_cmd_matrix` 受檢 **467** 支（`scripts/` 全量＋非 `src/augur` 之 `__main__` 模組，兩把不同的尺）。
08-03 當日已 4 個 commit（`3916c38`→`b78efd5`→`c8f6f2c`→`45ea88d`），另有三份並行 agent 產出之新報告（`wm_annexf_authoritative_binding_prep_20260803.md`／`wm_channel_registration_draft_20260803.md`／`wm_m3_batch1_target_scoping_20260803.md`）與 `augur_gov3b_human_signature_clause_20260803.md`／`augur_kdo4_measurement_scope_20260803.md`。

### Z10 WM.36 合規弧（今日主戰場）

- **Registry 已落地**：`world_concept`(6)／`world_concept_version`(6)／`world_concept_registry_current`(view)／`world_concept_registry_legacy`(6)／`world_channel_binding`(98)。落地時點 08-02 21:23。
  【**F2 備料（`reports/augur_1014_review_evidence_prep_20260801.md` §1(b)）說「Registry 表本體＝NONE」／live 實為五物件皆在**。】
- **但「已建表」≠「WM.36 已履行」**：現查 6 個 concept 中 `authoritative_binding_id IS NULL` **6/6**、`decided_by IS NULL` **6/6**；`world_channel_binding` 98 列中 `mapped` 10／`unmapped` 88、**`source_column` 非空者 0/98**（WM.36 欄3 要求粒度至欄位級）⇒ 依 WM.36「七欄俱全且各欄可解析者為登錄完成」之逐字判準，**今日登錄完成數＝0**。
- **vendor 直綁四把尺並存**（引用時必須連口徑一起講）：

  | 尺 | 值 | 出處／指令 |
  |---|---|---|
  | GROUNDING-MAP 07-17 快照 | **37** 檔 | `GROUNDING-MAP.md:46`（現仍寫 37、標 🔨） |
  | F2 報告 08-01 | 47 檔 | 同 grep、不同日 |
  | 同一 grep 今日 | **50** 檔 | `grep -rlE 'FROM\s+"Taiwan' src scripts --include='*.py' \| wc -l` |
  | 止血閘 `--scan`（寬口徑） | **56 檔／172 處** | `venv/bin/python scripts/check_vendor_binding.py --scan`（rc=1；quoted_table 142＋esc 26＋fred_series 4） |

  凍結基線 `ops/vendor_binding_baseline.txt` 現為 **130** 條指紋（非註解行）。
  ⚠ **同一日內又漂了一次**：08:48 之 commit `45ea88d`（「止血閘補數字表名漏洞——我昨晚建的閘有洞」）把基線由 128/170 → **130/172**。這說明止血閘本身在早期就漏掉了一類承載形。

---

## §3 對抗核驗結果（三表）

### 3.1 矛盾表（同一事實，兩處說法互斥）

| # | 甲說 | 乙說 | 現查裁決 |
|---|---|---|---|
| C1 | `CS-系統核心思想:10`「列 open-tension 呈 Steward 裁」 | 同檔 `:22` `open-tensions: []`／`:55`「無已登錄未解緊張」 | **二者必居其一**；以 front-matter 為準即靜默吞掉一項待裁事項。屬 Steward |
| C2 | 大憲章 `:451` v1.54.0 標 `**現行**` | 同表 `:446` v1.49.0 標 `**ACTIVE**` | 兩列同時宣稱現行；grep「現行」會得兩個答案 |
| C3 | 生產碼 18 處引 `RULING-2026-043` 為法源 | `constitution/` 無該檔、AL 無該列 | 法源不存在。屬 Steward |
| C4 | `MC §0.5` Layer 4 寫「**Knowledge Graph** Specification」 | 生效本標題《Knowledge **System** Specification》 | §0.5 自稱「新增規格必須先在本表登錄方生效力」，照字面比對會誤得「KS 未登錄」 |
| C5 | `evaluate_sim_calibration.py:126` 註解「runner 實形＝dict…2026-08-02 契約對齊**親驗**」 | runner `_q_grid()` 實回 `list[99]` | 註解與自測皆宣稱已驗，實際未驗（親驗 `normalize_q_grid` → None） |
| C6 | `.git/hooks/pre-commit:13`「須由 **install_services.sh** 安裝」 | `grep 'hook' install_services.sh` → 零命中 | 真安裝者是 `resume_project.sh` → `scripts/install_git_hooks.py` |
| C7 | `evolution_iteration_ledger` axis CHECK `ANY(ARRAY['tw','lai','raw'])` | 同表另一條 CHECK `axis = 'tw'` | 後者使前者形同虛設；三軸各有自己的 ledger 表 |

### 3.2 過期表（報告說 X／live 實為 Y）

| 出處 | 報告說 | live 實為（現查） |
|---|---|---|
| r3 `:66` | `feature_sign_check ＝ 0 列` | **40 列／36 feature**（PASS 23／FAIL 17，08-02 04:11） |
| r3 `:69` | G-SIGN 未入 GATE_IDS（七閘） | **八閘**；run 21 `gate_set_rev=8g-sign-v1` |
| r3 `:73` | apply_log 止於 id=24 | **25 列／max id=26**（23 缺號） |
| r3 `:75` | prodset active ＝ 2 | **3** |
| r3 `:92` | kill_switch 無 sim scope | **5 scope**（含 sim，08-01 18:20 種下）、全 clear |
| r3 `:95` | evolution_run 9 列 running／deferred 未清 7 筆 | **running 0／未清 0** |
| r3 `:103` | KH8 閘實際是開的（靠 0.27% 尾巴 ok=True） | **ok=False**（0.002706 < 0.05 門檻）⇒ 深度優先已關 |
| r3 `:128` | 12 條 cron 零 pg_dump／`/mnt/c/database` 已空 | **15 條 cron，含週六 07:30 備份**；本地 2 份 11G dump；**但 `/mnt/c/database` 現仍為空** |
| r3 `:150` | 週報檔名 live 凍死 `evolution_week_20260727.md` | `install_cron --check` **rc=0 一致**；live 檔為 `evolution_week_20260802.md` |
| `GROUNDING-MAP.md:45-47` | Registry「零跡象」；直綁 37 檔 | Registry 五物件在（08-02 21:23）；直綁 **50／56 檔**（兩把尺） |
| F2 備料 §1(b) | Registry 表本體＝**NONE** | 五物件皆在 |
| `RULING-2026-042` §二2 | delete_only 23 表／ledger_guard 5 表（08-01 快照） | **delete_only 9／ledger_guard 25**（方向完全反轉；B4-P2a/P2b 所致） |
| 記憶 `three-gate-strengths` | 綠燈帳本 green14/red5；矩陣 437/437 | **green16/red3**；**467/467** |
| 記憶 `single-role-consolidation` | 只剩一個庫 | **3 個庫**：`augur` 61GB／**`augur_sandbox` 34MB**／`postgres` |
| `CLAUDE.md:127` | scripts 稽核 137/137 | **467/467** |
| `HANDOFF.md:26` | 12 條 crontab | **15** |
| `tools/constitution_lint/github-workflow.yml` 檔頭 | 接線阻斷理由＝WM.44-LABEL 尚有 error | live WM.44-LABEL error **＝0**；真阻斷改為 selftest 之單一 G10 FAIL |

> ⚠ 關於 `RULING-2026-042`：依大憲章 v1.51.0 通則一「史述凍結」，**已簽生效裁決之正文不得改**。上表列它不是要求修改，而是提醒**引用其閘位數字時必須加「08-01 快照」限定詞**。

### 3.3 假綠表（綠燈量的不是它宣稱在量的東西）

| # | 綠燈 | 它宣稱在量 | 實際在量 | 覆核指令 |
|---|---|---|---|---|
| G1 | worktree 內 pre-commit rc=0 | 五閘通過 | **venv 不存在、直接 exit 0** | `cd <worktree> && bash ops/githooks/pre-commit`（現回 rc=0＋「略過」） |
| G2 | `reconcile_audit.py` 印 `PASS ✅` | 對帳通過 | **未納 coverage_gap**；死 feed／空視窗表照樣 PASS | `sed -n '150,160p' scripts/reconcile_audit.py` |
| G3 | `attestation_result.passed=t`（08-01） | audit 已綠 | `missing_in_db=11,145` 不入判式 | `SELECT passed,missing_in_db FROM attestation_result ORDER BY id DESC LIMIT 1` |
| G4 | `evaluate_sim_calibration --selftest` PASS | q_grid 契約已對齊 runner | **用手寫的錯形狀當 fixture** | 見 §2/Z6 之三行覆核 |
| G5 | `augur-knowhow-refresh` systemd Finished | 週更完成 | `--domain finance` 使分子分母同時歸零；全域 pending 102,039 | `psql -Atc "SELECT count(*) FROM knowledge_item WHERE domain='finance'"` → 0 |
| G6 | `tests/test_l716_conflict_registered.py` 2 passed | 裁決已登錄生效 | **只鎖「檔在」，不鎖「已簽」** | `grep -n assert tests/test_l716_conflict_registered.py` |
| G7 | `constitution_lint report` rc=0 | 治權層全綠 | corpus 只含 `specs/*.md` 七份 | `grep -n 'def corpus_files' -A 12 tools/constitution_lint/report.py` |
| G8 | 63 張表「有 trigger」 | 資料改不動 | 116 支全 origin-mode，一句 `SET session_replication_role='replica'` 全靜音、無痕 | `SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal AND tgenabled='A'` → **0** |
| G9 | `steward_question_ledger` 159 awaiting_hugo | 159 件待 Steward 裁決 | 主要是會話中的一般提問；`resolved_by='hugo'` 恆 **0** | `SELECT resolved_by,count(*) FROM steward_question_ledger GROUP BY 1` |
| G10 | `execute_sunset_consequence --check` 綠 | consequence 載體可用 | 綠燈原文＝「本行印得出來＝未鏽」，量的是它自己；seal trigger 於 116 支普查中 **零筆** | `SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'trg_sunset_seal_%'` |
| G11 | `knowhow_evidence_weight` band=high 145,958 件 | 絕大多數知識高可信 | 權重只在「已終態＋已嵌入＋已 eligible」上算＝母體選擇效應 | `src/augur/knowledge/evidence.py:108-112` 自陳 |
| G12 | KH1 通過率 100%（qual 1,056 列全 pass） | 准入把關嚴格 | 28.4 萬件走「既有原文即視為 qual 已過」旁路 | `src/augur/knowledge/auto_admit.py:337-360` |

### 3.4 一名多義表（同尺陷阱）

| 詞 | 並存的口徑 | 現值 |
|---|---|---|
| **public 表數** | `relkind='r'` ／ `pg_tables`（含分區父表） | 334 ／ 335 |
| **KH0 破口** | 未評（無 state 列）／ 無原文 | 138,875 ／ 138,826 |
| **vendor 直綁** | GROUNDING-MAP 快照／F2／今日 grep／止血閘寬口徑 | 37／47／50／**56 檔·172 處** |
| **script 支數** | `ls scripts/*.py` ／ `check_cmd_matrix` 射程 | 327 ／ **467** |
| **閘表分層** | 記憶「硬33/半14」（人工分類）／`tgtype` bitmask（有 trigger 63／含 UPDATE 51／UPDATE 裸 12）／B4「裸 UPDATE 面 20→9」（治權表子集） | 三把尺不可相減 |
| **sent_no_emb** | items 側未嵌句／一句未嵌之 item／全庫未嵌句 | 14,208 ／ 396 ／ 67,080 |
| **雙綠 dual_green_n** | G-PROM∧G-ECON 之相異 feature 數 | run 21＝**2**；而八閘全綠**列**數＝3 |

---

## §4 未修債總表（依「不修會怎樣」排序）

> 排序原則：**能安靜地讓錯的東西通過** ＞ 能讓對的東西被誤讀 ＞ 效能與體積。
> 「層級」欄：**S**＝屬 Steward（判準／解釋／不可逆／外部副作用）；**A**＝AI 可為之執行層修正；**A+S**＝AI 實作但須先取得一次授權。

| # | 債 | 不修會怎樣 | 層級 |
|---|---|---|---|
| **D1** | **worktree 內 pre-commit 靜默 exit 0**（`ops/githooks/pre-commit:12-14` 以 `git rev-parse --show-toplevel` 定位 venv） | 三個 worktree（含現正並行寫報告者）之每一筆 commit 完全不過五閘；併回 main 後閘從未看過那些內容。且失效**完全靜默**，只有一行「略過」 | A |
| **D2** | **worktree 注入過期治權檔**（v1.31／v1.32 vs main v1.35） | worktree agent 讀不到 #33／#34／#35，且讀到**已被明示反向廢止**的「非必要不 fan-out」之生效版；它不會知道自己讀的是舊法 | A（同步）＋S（#13 文字） |
| **D3** | **`RULING-2026-043` 無本體**（18 處引用／6 檔） | 後續稽核依 `ls constitution/*RULING*` 盤點時，11＋張表的閘架構完全不可見；「043 明文之射程界線」無原文可查證；與 042 §四「`ls … \| tail -1` → 本檔」之驗證慣行直接衝突 | **S** |
| **D4** | **`reconcile_audit.py:157` 未納 coverage_gap** | 死 feed／空視窗表印 `PASS ✅` → 寫進 `attestation_result.passed=true` → watchdog 讀成「audit 已綠」；三層堆疊後最上層綠燈完全脫離事實 | A（正解已在 `reconcile.py:587`，接上即可） |
| **D5** | **綠燈帳本自己沒有寫入閘**（`validation_evidence` 19 列、`attestation_result` 9 列皆零 trigger） | 一句裸 UPDATE 即可讓整個誠實性宣稱體系變綠，無 pre-image、無留痕、無人察覺——量綠燈的尺自己可被改 | A+S（DDL 落治權表，宜循 B4 呈案格式） |
| **D6** | **116 支 trigger 全 origin-mode**，`SET session_replication_role='replica'` 一句全靜音且無痕 | 所有「誠實帳本閘」在單一 superuser 下實為紀律提示；而文件一律以「硬閘」稱之 ⇒ 後人高估強度 | **S**（`ENABLE ALWAYS` 是否算升嚴／是否回退角色架構） |
| **D7** | **sim q_grid 契約斷裂**（runner list vs evaluator dict） | 09 月首波 settle 後 evaluator 會算出 `n_valid=0` 並印「等 settle 波」——把解析失敗誤述為尚未結算；最壞 11 月才發現整季白等 | A（改 evaluator 接受 list，**不可改 runner**——見 §5 T7） |
| **D8** | **方向衝突四列**（q562/563/643/644：map.direction ≠ gate expected_direction） | 只要 G-ECON 轉 PASS，就會用**反方向**的證據把假說判 validated ⇒ M-1 病灶從另一入口復發 | A（加方向鍵）＋S（是否改判「不符即 FAIL_SIGN」） |
| **D9** | **整批路完全不受武裝閘約束**（`single_apply_gate` queue_id=None → True） | 「S-i 一次一顆人裁」可被一句無旗標指令整個繞過；親驗 dry-run 即 `applied=17` | **S**（涉 PME-AUTO-B 與人閘紀律交界） |
| **D10** | **KH0 破口 138,826 件在現行碼下無路可補**（`auto_admit.py:719` JOIN／`ingress_kip.py:92` EXISTS） | `run_kh_chain --check` 成為永遠紅、且紅得不會變綠的閘 ⇒ 一個月內必被當「已知紅燈」忽略，憲章 v1.53.0 退化成純文字 | A（改 JOIN）＋**S**（KH0 對無原文 item 之通過條件＝條文解釋） |
| **D11** | **`--domain finance` 使週更空轉** | 102,039 筆 pending staging（最舊已滿一個月、每日仍增）永不 promote；unit 每週準時 Finished、journal 自陳「待辦(前) 0」自己蓋掉自己 | A（改 unit 須用戶授權動 systemd） |
| **D12** | **治權 lint 291 條斷言零自動觸發**（單一 G10 FAIL 卡住） | `compliance_lint`／`annex_d_range_lint`／`report` 的全部保護只在有人手動想到時才跑；治權檔任一次編輯都可能靜默破壞不變式數月 | **S**（G10 界線之解釋）＋A（known-issue 化後掛第六閘） |
| **D13** | **CS 與 `constitution/` 全域不在 lint 射程**（`corpus_files()` 只吃 `specs/*.md`） | §3.1 之 C1／C2／CS 版號漂移沒有一類能被機械捕獲；治權層唯一自動紅燈是一支不在 pre-commit 內的 pytest | A（新增 `cs_selfversion_mismatch` 第五類 finding） |
| **D14** | **CS 版本自我漂移三檔** | `spec-version` 是機器可解析欄；欄值指向舊版＝該版正文之合規聲明在形式上不存在；RULING-2026-002 主文二補正期到 10-14 | A（純機械一致性）＋先驗紅 |
| **D15** | **R6 週掃視 gate_ref 過濾**（`report_triple_evolution_week.py:347`） | 本專案最重大的兩顆自掙晉升（TWEVO-APPLY-go）在 Steward 的週掃視清單上**不存在**；P5.W5 之義務只履行在舊路徑 | A（一句 WHERE） |
| **D16** | **`sim_calibration_eval`／`sim_realized_outcome`／`sim_run_link` 無 UPDATE 閘** | 用來證明能力宣稱的核心證據可被裸 UPDATE 靜默改寫；B4 三批的漏網 | A+S |
| **D17** | **prodset 可溯源鏈斷點**（`lending_fee_rate_mean_20d`：apply_log_id=24 指向 queue 311） | 事後稽核沿 apply_log_id 回查會拿 07-29 的 promote 證據當 08-01 demote 的依據，正是 #10 之反例 | A（補 log＋改指） |
| **D18** | **積壓計數漏 `cleared_at IS NULL`**（driver:433／驗收器 A8:238-241） | 「積壓 9 列」只增不減＝等於沒有告警；A8 是結構上不可能 FAIL 的橡皮圖章；heavy slot 餓死（本軸最貴失效）分辨不出 | A |
| **D19** | **`prior_depth` 是自我背書的 pass** | 14.6 萬件 `layer_scores` 寫著 `{"verdict":"pass","note":"prior_depth"}`，而今天用現行 KH5 判準實查全部 fail ⇒ 任何下層判準收緊對存量零效果、帳面卻寫著 pass | A（改記 `not_reevaluated`，零行為變更） |
| **D20** | **全文管線只完成誠實標記、未完成推進**（121,389 unattempted、零排程） | CLAUDE #29(b) v1.20「不得只抓 metadata 就宣稱完成」在 14 萬件外部語料上長期未履行；顧問對 25 個域可答率固定 0% | **S**（外部 API 放量節奏） |
| **D21** | **「不代打人簽」無治權住所**（`CS-CLAUDE.md:50` 把 MC §P5 落點指向記憶檔） | 換機／清記憶／新 agent 未載入時該義務在治權層不存在，而合規聲明卻宣稱有落點；DB 層對 `decided_by` 零 CHECK、`augur` 為 superuser ⇒ 這是該義務唯一實質防線 | **S**（涉自身監督機制，AI 不得為核准主體） |
| **D22** | **「git add 逐檔明列」「不同時派 agent 改同檔」「pgrep 正法」三則無治權住所** | 多 worktree／多 agent 並行是常態；本次三 agent 並行靠父 agent 口頭約定規避撞檔，**不是靠規則**；#34「平行度拉滿」之三項硬邊界未含「檔案集不重疊」 | **S**（修 #34 屬判準） |
| **D23** | **`sim_evolution_iteration_ledger` 為孤兒表** | runner 寫入 `iteration_uid` 但該表 0 列、零 writer、無 FK ⇒ 專章 §3.6 之 `gain_basis` 硬 CHECK 掛在永遠不會被寫的表上 | A |
| **D24** | **W4 判決工具不存在** | 11 月 K=3 齊、evaluator 產出 5 列後，沒有任何載體把 k1/k2/k3 轉成 verdict；專章「判死留檔・永不靜默消失」在 DB 層無落點 | A（killed／undecidable 兩路徑）＋S（promoted 路徑） |
| **D25** | **Steward 人裁佇列只寫不讀**（`resolved_by='hugo'` 恆 0；159 件 awaiting 自 06-22 懸置） | 機器結掉送給人的案子（含 `rules_v3_sweep_awaiting`）本身即是 OCV「否決可達性」之弱化訊號 | **S** |
| **D26** | **20 條假斷言／130 條 vendor 指紋凍在基線、無清償期限** | 棘輪只擋新增、存量永不縮；WM.36 於 10-15 起無條件適用時，172 處即為違規存量 | **S**（清償節奏） |
| **D27** | **異地備份層現為零**（`/mnt/c/database` 空） | 本地 2 份 11G dump 與 DB、repo 同在一顆 vhdx／同一實體碟；碟亡＝全亡。腳本自己誠實標「不假裝解決」 | **S**（G2 異裝置呈案） |
| **D28** | **`knowhow_auto_admit_run` 556 MB／509,551 列，每輪 +14.6 萬列** | 一次完整推進輪＝+160 MB，其中絕大多數列內容逐字相同；pg_dump 窗與還原時間線性上升 | A+S（帳本留痕義務範圍屬 Steward） |
| **D29** | **KH7 仍是庫級放行**（6 列 probe 撐 145,952 件 depth 7） | 一個不區分個體的布林旗標在替 28 萬件排序，外觀上卻是「七層深度證據」——與 KH8 被判死的理由同構 | **S** |
| **D30** | **`gate_scale` 指紋只認 `min_abs_hac_t`** | 改 `--since`／panel 口徑／G-ECON 成本＝靜默換尺，而 `compare_gain` 仍宣稱兩輪可比；碼內註解已自陳此風險卻未修 | **S**（改「什麼算可比」＝改判準） |
| **D31** | **RAWEVO gain 恆為真且豁免對照臂**（`gain = bool(made or true_gap or freeze_gap)`） | raw 軸永遠自稱有進步、永不停損；`basis='new_gap'` 不在驗收器 METRIC_BASES ⇒ 用一個自訂名稱繞過對照臂要求 | **S** |
| **D32** | **MEMORY.md 索引無稽核器**（1 孤兒檔／3 截短名／3 則同時自稱 ⭐權威） | 索引是新 session 唯一自動載入的記憶入口；索引漂移＝新 agent 從第一秒起被導向過期權威 | A |
| **D33** | **`sync_memory.py export` 無密碼掃描** | export 把 79 檔全量推 public monorepo，僅一行人讀提醒；2026-07-13 已有一次未遂（ttai admin 密碼）。一次疏忽即不可逆公開洩漏 | A |
| **D34** | **`apply_evolution_promotions.py:304` kill scope 只有 tw+global** | 按下 lai／sim／raw 煞車後晉升 APPLY 仍放行——煞車鈕上寫著軸名，那一步卻不看軸 | A（一行） |
| **D35** | **292 支 selftest 僅 3 支在排程、26 支 pytest 零排程** | #18／#29(d) 之「每支可個別驗證」事實上只是「可被驗證」而非「有被驗證」；偵測時點推遲到下次有人想起 | A |
| **D36** | **`ledger.apply_allowed` 恆 false、`gate_ref`／`source_run_id` 恆 NULL** | #26 授權四要件之留痕在正規欄位上是空的，稽核只能靠 apply_log 單邊佐證 | A |
| **D37** | **`knowledge_access_audit` 名不副實**（66 列、最後 07-06、檢索路徑零寫入） | 看起來像「知識存取有稽核軌跡」，實際誰讀了哪些私有 item 完全無紀錄 | A（誠實正名）＋S（是否補真軌跡） |
| **D38** | **`eval_code_hash` ＝整檔位元組 sha** | 改一個註解即產生新 cell；把邏輯抽到別檔則實質改了演算法而 hash 不動——兩個方向都失真 | A |
| **D39** | **`augur_sandbox` 庫之治權定位未定**（34 MB／14 表，17 處引用） | 記憶「終態＝只剩一個庫」已不成立；該庫不在 HANDOFF／README／備份範圍，隔離靠什麼保證不明 | **S** |
| **D40** | **`HANDOFF.md`／`CLAUDE.md` 殘存硬編數字** | HANDOFF 是換機第一份該讀的文件；以 12 條 cron 核對會漏掉 3 條（含 `--slot-wait`、證據重驗） | A（照 README 先例辦理） |

---

## §5 踩雷與反直覺（後人必讀）

**T1 rc 會被 pipe 吃掉。** `cmd | tail -4; echo rc=$?` 取到的是 `tail` 的 rc（恆 0）。本輪第一次量五閘時就中招。正解：重導向到檔再取 `$?`，或用 `${PIPESTATUS[0]}`。這是 `augur-verifier-traps`「rc=0≠通過」在本區的實例。

**T2 `constitution_lint` 兩個子命令 rc 相反。** `--selftest` rc=**1**（G10 界線 FAIL，刻意不掛 hook）、`report` rc=**0**。取錯一個就會得出相反結論。

**T3 README 自引的機械軌指令不重現自己的數字。** README 寫「依 `ls -d src/augur/*/` 實測 16 個 package」，但現跑 `ls -d src/augur/*/ | wc -l` ＝ **17**（多出 `__pycache__`）。README 的**數字正確、指令不正確**。任何把未過濾指令寫進治權檔的「機械軌」註記，下一個人跑出不同數字時會誤判為腐爛。

**T4 「World Concept Registry 已建表」≠「WM.36 已履行」。** 五個物件在，很容易被讀成 checklist 可勾。實際：欄4 權威表徵 6/6 空、通道映射 98 列全為表級（欄位級 0/98）、88/98 unmapped、provenance 自標 `採認狀態: pending`。**登錄完成數＝0**。

**T5 `ls constitution/*RULING*.md | tail -1` 不等於「最高裁決號」。** 該指令（RULING-042 §四自己在用）今日回 042，但 043 已在生產碼中被當成生效法源。正確覆核：`grep -rn "RULING-2026-0[0-9][0-9]" scripts src audits | grep -oE 'RULING-2026-[0-9]{3}' | sort -u` 與 `ls constitution/RULING-*` 取差集。

**T6 `AL-2026-031` 在 AMENDMENT-LOG 中排在 033 之後**（`:341` 032 → `:351` 033 → `:360` 031 → `:368` 034）。這是刻意的號碼避讓＋補登（RULING-028 讓與 GOV 側），檔內 `:345` 有註記——但用 `tail` 或按行序讀的人會誤判為亂序或遺漏。

**T7 sim 首格一旦落地，summary 事實上不可修。** runner 用 `INSERT … ON CONFLICT (run_id) DO NOTHING`，run_id 由 `(gate,candidate,stock,asof,h,spec_sha)` 決定、**不含 code 版本**。重跑是 DO NOTHING、UPDATE 被 honesty guard 擋、換 run_id 須換 spec_sha＝換候選。所以 q_grid 契約若選擇「改 runner 寫成 dict」，今晚已產的 52 列會永久卡在舊形。**正解是改 evaluator**（數字本身是對的，只是形狀）。

**T8 C 類 12 張「UPDATE 全裸」表不是同一件事。** `entity_registry`／`entity_alias` 的 UPDATE 全裸是**設計如此**——`identity_no_delete` 的例外訊息逐字寫「下市/去識別化以 UPDATE status=tombstoned 標記」。把 12 張一律當缺口會做出錯誤的補閘提案。

**T9 `session_replication_role` 不是 `DISABLE TRIGGER`。** 前者無 DDL、無鎖、schema 無差異、事後 `tgenabled` 仍是 `'O'`——**事後鑑識查不到痕跡**。任何「trigger 都在、所以沒被繞過」的推論不成立。

**T10 `memory_status` 回 isError 不是故障，是規格。** 工具描述逐字「缺索引／缺 FTS／嵌入不可達 → isError，**不靜默回空**」。在 worktree 看到 isError 的正確結論是「本 session 無 recall 能力」，不是「去修它」。這是本專案少數把 fail-closed 做對的地方，誤修反而引入靜默回空。

**T11 `dual_green_n` 名實不符。** 它只數 G-PROM ∧ G-ECON 皆 PASS 之相異 feature，而 APPLY 需**八閘**全綠。run 21：雙綠=2、八閘全綠**列**=3。且 `compare_gain` 要求 `dual_green_n` **逐輪嚴格遞增**才算有增益 ⇒ 平台期（哪怕停在健康的 2）一律記 gain=False，三輪即 `stopped_no_gain`。

**T12 `prodset_delta` 在人閘模式下結構上恆為 0。** v2 口徑把 `prodset_active_n` 限縮為 `source_run_id = 本輪 run`，而 cron 刻意不帶 `--allow-apply` ⇒ APPLY 一律發生在結輪之後。現查 `tw-20260801-r01` 之 `prodset_active_n=0`——**本專案最大的里程碑在 gain 帳本上是 0**。

**T13 同一份 `gate_json` 內兩種 IC 口徑。** `G-PROM.evidence.mean_ic` 是**已乘 direction** 之口徑（負值＝與假說反向，故可裁 FAIL_SIGN）；`G-SIGN.evidence.point_ic` 是**還原後的 raw IC**。方向為 −1 的 feature 上兩者符號必然相反。

**T14 四個 run 級閘是逐列蓋章，不隨 run 中途狀態改變。** G-ISO／G-NOEXEC／G-ATTEST／G-KILL 在 run 開始前算一次、之後對 111 列逐列寫同一份 dict。I3 需 7–10 小時，期間若有人按下 kill switch，**已寫入之列仍記 G-KILL=PASS**。

**T15 `G-NOEXEC` 的射程遠窄於名稱。** 只掃三個檔（apply／run_philosophy_evolution／set_kill_switch），**不掃 driver、不掃 `src/augur` 任何模組**。

**T16 `--queue-id` 的「人裁」是旗標不是人。** `single_apply_gate` 只比對字串常數 `TWEVO-APPLY-go`；docstring 寫「hugo 親跑＝授權載體」屬**文件宣稱強於 code 實況**。查授權時看的是有沒有 isatty／簽名輸入，不是 docstring。

**T17 「一名多義」清單見 §3.4。** 引用任何數字前先問：這是哪把尺？

**T18 `docs/` 下同時有兩份大憲章正文**（v1.47.0 與 v1.54.0）、`docs/compliance/` 有**三份** CS-大憲章而正文只有兩份；且 `CS-系統架構大憲章_v1.48.0.md` 的 mtime（08-03 08:12）新於 v1.54.0，以 mtime 排序會誤取更低版本為最新。

**T19 我在 worktree 內 grep 會得到三倍假象。** `.claude/worktrees/` 有三份完整副本。量檔案數一律明列 `scripts/ src/ tools/ ops/ tests/`，別用 `.`。

**T20 `except Exception: pass` 吞掉 NameError。** `src/augur/philosophy/retrieval.py:405-409` 與 `:371-375` 兩段同形，一段能跑一段是 NameError 死碼，肉眼讀起來一模一樣。判斷法：`f.__code__.co_varnames` 有沒有那個名字。

---

## §6 待 Steward 之決定與解釋（分類彙整）

> 僅列真需人裁者（條文解釋／判準變更／不可逆／外部副作用）。工程問題一律歸 §4 之 A 級。
> AI 於此類事項僅得**草擬、比對與呈案**（`AUGUR-MC v1.6 §8.1`／`AUGUR-L6 v1.2` L6.18(a)）。

### 6.1 條文解釋

| Q | 問題 | 為何非工程問題 |
|---|---|---|
| Q1 | **`RULING-2026-043` 之編號與形制如何收束？**（甲：補作正式裁決檔＋AL，追認 P0/P2a/P2b 為同案分批；乙：明示「圈選留痕即為完整裁決、不編號」並清除碼內 18 處字樣） | 牽涉「什麼樣的留痕構成一份裁決」；且 043 已被引為對其他 delete-only 表之射程界線依據 |
| Q2 | **領域治權檔升版是否須登錄 `constitution/AMENDMENT-LOG.md`？** | 現為分裂雙帳簿（AL 46 列全屬 MC/specs 軸；領域軸八版 0 列入 AL、2 版入 DB）；`GOVERNANCE-ANNEX.md` 第 6 條 1 款字面要求「一律以文件形式存於 `constitution/`」。附帶風險：DB 不隨 git 跨機 |
| Q3 | **`模擬方法自進化專章 v1.0` 是否為 MC §0.5 意義下之「規格」而須先登錄方生效力？** | 它載實質 [N] 義務句、自稱條文 SSOT，但形制是大憲章第三部之下位專章；現無 CS、無 AL、未入 §0.5 |
| Q4 | **`constitution_lint --selftest` 之 G10 界線斷言如何裁？**（`### TR.Z …（DRAFT）` 殘留是否構成 status error） | 這一條 FAIL 是治權 lint 全體 291 條斷言無法接上任何自動觸發點的**唯一**阻斷 |
| Q5 | **CS-系統核心思想 `:10` 之 open-tension（A.38 閉集 E[r] 模態定性）是仍未裁還是已被吸收？** | 同檔 `:22`／`:55` 已宣告「無已登錄未解緊張」。AI 不得代為認定其已閉（RULING-2026-039「禁止假關」） |
| Q6 | **KH0 對無原文 item 之通過條件為何？** v1.53.0 撤回 metadata-only 例外之理由是「就算是一個標題也有其語意」，但 `evaluate_layer(0)` 的 `has_text` 只看 `knowledge_item_text` 有無列 | 甲案（進得來、判 fail 亦可，破口即關）與乙案（有標題即 pass）對「KH0 通過率」的意義完全不同，且乙案會讓 13.8 萬件一次進入推進池 |
| Q7 | **`ENABLE ALWAYS` 算不算「升嚴」而須走 GATE-raise？** | 本專案對挪門柱有明文程序，但對象是**判準文字**；`ENABLE ALWAYS` 不動判準文字、只讓既有判準更難繞。§8.1 解釋權專屬 Steward |
| Q8 | **`vendor_binding_strangler_ledger` 之「不掛 honesty trigger」（08-03 已裁）是否延伸適用於其他 29 張零 trigger 之治權味表？** | 若不延伸，`attestation_result`／`validation_evidence`／`model_registry`／`knowhow_auto_admit_gate_change` 四張要害表應補閘；若延伸，需成為可引用的通則而非個案 |
| Q9 | **10-14 併審應以何為 L7.16 現行承載之依據？** `RULING-2026-042` §二2 之閘位數字已與 live 反向，而依 v1.51.0 通則一史述凍結**不得改其正文** | AI 可備滾動快照附卷，但「以哪份為認定基礎」屬 Steward |

### 6.2 判準變更

| Q | 問題 |
|---|---|
| Q10 | **晉升單位是 feature 還是 (principle, feature)？** 三處口徑不一：prodset 以 feature 為 PK／`philosophy_principle.status` 以 principle 為單位／`promotion_queue` 以 (run, principle, feature) 為列。實例：q555/556 同為 `cycle_position_252d` 八閘全綠，hugo 簽了 556，**555 至今仍 pending_auto，今晚 run 22 會把它標 superseded**。此問同時決定 D8／D17／收斂謂詞 |
| Q11 | **2026-07-29 新增之 p123 兩列 map 方向與 07-28 裁決相反，如何處置？**（甲：依裁決改方向；乙：撤下 map 列；丙：承認同一 feature 可承載多方向假說、改為逐 (principle, feature) 裁方向） |
| Q12 | **TWEVO 之「什麼算進步」要不要改？** `compare_gain` 現要求 `dual_green_n` 逐輪嚴格遞增，而 `prodset_delta` 在人閘模式下結構恆 0 ⇒ run 22 起若停在 2，三輪後即 `stopped_no_gain`。此變更會改變自動鏈的停手時點（#26 自動鏈上限之相關項） |
| Q13 | **RAWEVO 的 gain 語意是否為原意？**（恆為真、永不停損、以 `basis='new_gap'` 繞過對照臂） |
| Q14 | **KH7 是逐 item 判準還是庫級前提？**（甲：逐 item 化並接受 depth 掉檔；乙：明文認定為庫級前提、要求 layer_scores 顯式標 `evidence_scope`；丙：維持現狀） |
| Q15 | **D3 軸判準之映射工件是否納 `erp_tiptop`？** 唯一 100% 可答的域因不在名冊而恆 pending，而 mapped 的 quant_finance 反而不可答。`knowledge_domain_map` 之納新域＝人拍板，**AI 不得自行 INSERT** |
| Q16 | **`gate_scale` 指紋是否升級為 config gates 子樹＋since＋horizon 之 sha？** 這是「什麼算可比」之判準輸入 |
| Q17 | **`--allow-apply` 是否升為 TTY 人閘／整批路是否也經武裝閘？** 會改變 PME-AUTO-B「閘內狀態晉升屬執行層」與「S-i 一次一顆」之交界 |
| Q18 | **是否開啟 cron 的 `--allow-apply`？** ⚠ 在 D9 未修前開啟即等於啟用**無武裝閘的整批路**（driver 不把旗標傳給子行程，子行程走 `queue_id=None` 分支）；現查該路徑會一次 `applied=17` |
| Q19 | **#34 是否增列第 (iv) 項硬邊界「並行以檔案集不重疊為前提」？** 現三項硬邊界未含撞檔，唯一護欄只活在記憶檔 |
| Q20 | **`never-type-human-signature` 是否升格為 CLAUDE.md 正式條？** 屬**涉及 AI 自身監督機制之變更**，AI 不得為核准主體。附帶：若不升格，`CS-CLAUDE.md:50` 之落點宣稱是否應改寫為「目前無治權層落點」？ |
| Q21 | **`guard-mechanisms` 型 6（機器覆寫人裁且無痕）與型 7（凍結了判準文字沒凍結判準的實作）是否入憲？** #35 目前只吸收型 3／4；型 6 已實犯、型 7 觸及 §8.1 解釋權 |
| Q22 | **機器規則可否把 `awaiting_hugo` 改成 `superseded`？** 直接落在 P5.W2／OCV C 分量（#26 自動鏈上限） |

### 6.3 不可逆／外部副作用

| Q | 問題 |
|---|---|
| Q23 | **單一角色整併是否為「閘的強度」局部回退？**（恢復一個非 superuser 寫入角色）——不可逆、跨治權檔，且會重啟已結案的整併。hugo 07-31 曾主動問過此題，該題現仍在 `steward_question_ledger` awaiting_hugo 之列 |
| Q24 | **外部全文抓取的放量節奏。** 90,426＋9,477 件佇列零排程；#29(b) 要求端到端至 license 終態，但 #24/#25 要求受控。建議比照 ata-advance 之 200/日先跑一週。**屬外部副作用，AI 不自行啟動** |
| Q25 | **兩本存量基線之清償期限與配額**（假斷言 20 條／vendor 130 指紋·172 處）。WM.36 於 10-15 起無條件適用；AI 不得自訂生效要件（v1.31） |
| Q26 | **異地備份（G2 異裝置）。** 本地 2 份 11G dump 與 DB、repo 同碟；`/mnt/c/database` 現為空。腳本已誠實聲明「碟亡層不假裝解決」 |
| Q27 | **`augur_sandbox` 之治權定位**：是否受表級不變式約束？是否納入備份？與生產庫之隔離由什麼機制保證（現況兩庫同屬 superuser `augur`）？ |
| Q28 | **`knowhow_auto_admit_run` 之留痕義務範圍**：「每次評估都留一列」是誠實要件（則 D28 不可做），還是「每個**不同**結果留一列」（則去重合規）？一旦刪過不可逆 |
| Q29 | **5 條 manual `validation_evidence` 於 10-09／10-10 到期後之處置**：其中 `E3_promotion_funnel`／`E4_gm_promotion_gap` 連 `last_verified_at` 都是 NULL（從未被檢驗）——到期是「重簽」還是「轉為可機械化的 sql 型」？ |
| Q30 | **2026-07-25 `promoted_by='hugo'` 代打事件是否構成 GOV-3 B 之「再現越權 Evidence」？** 07-24 盤點結論為「無新 Evidence」，但該事件發生於 07-25 且未被登錄為候選 Evidence。10-14 checklist 第 7 項即問此事 |

### 6.4 2026-10-14 併結日曆（禁假關）

`ULTRACODE-SCHEDULE.md:112-122` 之七個勾選框**本日親讀仍全 `[ ]`**（WM.35/36 直綁消費禁令生效盤點・025 (iii)(iv)(vi)②③・029 L5 PRV/ASF 日曆復審・L7.16 全棧 owner≠app 矩陣・KDO.4/LDO.4 量測落地・020 M2・GOV-3 B 有無新越權 Evidence），且該節自標「**到期前不得勾『結清』**」。
`2026-10-14` 於 `constitution/`＋`specs/`＋`docs/compliance/` 之命中現查為 **88 處／32 檔**（`grep -ro "2026-10-14" constitution/ specs/ docs/compliance/ | wc -l`）。【Z1 材料於 08:4x 量到 74 處／27 檔——同一日內已增，係今日治權檔續增所致；引用此數必附時戳。】checklist 外另有六項同綁該日（RULING-002 主文二／主文五・LDI.7・D-PRIN-2・C1 manual 有效期 10-09/10-10・RULING-012 Phase 7）。
**距 10-14 尚有 72 日，且這段期間 live 還會大幅漂移**——建議依 §7.4 之「條文 ↔ live 探針綁定表」把手抄數字改為自動 diff。

---

## §7 r3 以來之變更帳

### 7.1 已兌現（r3 債表之清償）

| r3 債 # | 內容 | 現況 |
|---|---|---|
| 6 | 假斷言 lint 修誤報→基線化→掛 pre-commit | ✅ 已成 pre-commit 第四閘（基線 20），`--gate` rc=0 |
| 7 | **G-SIGN 入 GATE_IDS** | ✅ 八閘生效（08-01 A3 Steward 拍板）；run 21 `gate_set_rev=8g-sign-v1`；77 筆遷移 |
| 5 | 殭屍清帳（run 11–19 running／deferred 7 筆） | ✅ running **0**／deferred 未清 **0** |
| 11 | L7.16 衝突補登錄 | ✅ `RULING-2026-042`＋AL-2026-046（08-01 hugo 簽）＋回歸鎖 |
| 15 | 週報檔名 live `--apply` | ✅ `install_cron --check` rc=0 一致；live 檔 `evolution_week_20260802.md` |
| 12 | 定期 pg_dump | 🟡 **部分**——週六 07:30 cron 已掛、本地 2 份 11G dump 已產；**異地層仍為零**（`/mnt/c/database` 空） |
| 1 | W2-‖A 符號尺 `--record` | ✅ `feature_sign_check` 40 列／36 feature（08-02 04:11） |
| 2 | validation_evidence 掛排程＋manual 有效期 | ✅ 每日 07:10／週日 07:40 cron；`chk_ve_manual_expiry` CHECK 在（5 列 manual valid_until 10-09／10-10） |
| — | I5B 世代 supersede | ✅ 08-02 落引擎（commit `2b6350d`）；今晚 run 22 為首次生效點 |
| — | 首兩顆引擎自掙晉升 | ✅ 08-02 19:49，prodset active 2→**3** |
| — | sim 門親簽＋四件套＋P0 候選 | ✅ 08-02（門雙級指紋覆算全合、selftest 全綠） |
| — | B4 三批 UPDATE-GUC | ✅ ledger_guard 5→**25** 表、delete_only 23→**9** 表 |
| — | pre-commit 五閘 | ✅ 08-02 21:20 上崗（治權引用／指令矩陣／#8 AST／假斷言／vendor 直綁） |
| — | WM.36 Registry | ✅ 五物件落地（08-02 21:23）；🟡 但登錄完成數 0（見 T4） |

### 7.2 r3 說錯／已過期（具名更正）

見 §3.2 完整表。**最需要注意的三則**：

1. **r3 §五「KH8 閘實際是開的」已反轉**——現為 `ok=False`（0.002706 < 0.05），深度優先排序已關。但**問題沒有消失，只是換了形態**：145,952 件仍寫死 depth 7，`DEEP_KH_FLOOR=7`，一旦 KH8 任何時點回 `ok=True`，退化排序會**無聲地**重新生效，沒有第二道閘。
2. **r3 §三晉升鏈斷點圖已全部打通**（sign 0 列 → 40 列；G-SIGN 七閘 → 八閘；APPLY-go 未開 → 已開；prodset 2 → 3）。該圖現為史料，不可再引為現況。
3. **r3 §七「12 條 cron 零 pg_dump」已不成立**——現 15 條、含備份。但備份的**異地層**仍為零，且這是 r3 該債的核心（「碟亡＝全亡」）⇒ **不可據此認為該債已清**。

### 7.3 本輪對「同日 08:29 初稿 r4」之更正

| 初稿說 | 實況（現查） |
|---|---|
| 「sim **runner／W3／W5 未齊**→時鐘易空轉」 | 四件套已於 08-02 落地（commit `92647f0`）、`--selftest` 全 rc=0。真正的問題不是「未齊」而是 **W5→W3 契約已斷**（§2/Z6）＋ **W4 判決工具不存在** |
| §九 P0-#1「I5B supersede 過目落地」列為待辦 | 已於 08-02 落引擎（`2b6350d`）；`promotion_queue` superseded 現為 0 列僅因 run 22 尚未跑 |
| `HEAD 3916c38` | 現為 `45ea88d`（08-03 08:48）——初稿自己已註「勿釘死」，此處僅補戳 |
| 「pending_auto 17——已消化／遷移大量」 | 數字正確，但語意應為：17 列只對應 **11 個相異 feature**，其中 16 筆是 FAIL_SIGN demote 待決、1 筆（q555）是**被 hugo 簽了孿生列而遺留的孤兒 promote** |

### 7.4 本輪自己的方法論產出

1. **「口徑必附」升為硬紀律**——本輪至少七個量被證實一名多義（§3.4）。建議把「引用數字必附口徑」寫進下一輪報告模板。
2. **建議建立「條文 ↔ live 探針」綁定表**（一列一義務，欄位＝條文 file:line／可重跑指令／本日值／上次值／判定），取代目前散在 F2 報告／GROUNDING-MAP／ULTRACODE-SCHEDULE 三處的手抄數字。本輪找到的三類過期（F2 說 Registry NONE／GROUNDING-MAP 說 37／042 說 delete_only 23）全部會變成自動偵測到的 diff。探針須「不由被量測構件自身支配」（L7.26(a) 已有此要求，可直接引為設計約束）。**純備料、不代 Steward 勾任何一項**（F2 已立此紀律）。
3. **第二問法之第三型**（承 `guard-mechanisms-that-silently-fail`）：除「這綠燈量的是不是它宣稱在量的東西」外，本輪反覆命中的是——**「這個閘會不會在某些環境下根本沒被執行？」**（worktree／venv 缺失／corpus glob 無命中／目錄改名）。三支掃描器（`check_treaty_refs._iter_files`／`import_isolation._string_ref_violations`／`_ast_import_scan`）皆以**空集合＝綠燈**，無「至少掃到 N 個對象」之地板斷言。

---

## §8 誠實邊界（本報告未讀／未驗者）

**本報告之射程聲明**：
- 本輪**沒有**字面讀完全 repo。規模：`scripts/*.py` 327 支｜`reports/*.md` 300｜`audits/*.md` 200｜public 表 334｜`src/augur` 16 package。本檔＝**可優化的心智模型 SSOT**，不是全文索引。
- 本輪為**全程唯讀**：零 DDL、零 DB 寫入、零 commit、零 systemctl、未改任何既有檔（唯一寫入＝本報告檔本身）。`session_replication_role` 之驗證以 `BEGIN … ROLLBACK` 執行，零寫入。
- 未跑 `run_kh_chain.py --check` 全鏈（改以等價 SQL 現查 KH0 兩把尺）；未跑 292 支 selftest 全量；未跑 pytest 全量（僅引 Z 區材料所報之 `test_l716` 2 passed）。
- 未驗 §2/Z7 之常駐埠連通性、未驗 Qdrant collection 健康、未驗 FinMind 配額錶（唯讀輪禁 API，#24/#25）。
- 未親讀之區塊：`docs/系統架構大憲章_v1.54.0.md` 全文逐條（僅查修訂表與指定行）；40 份裁決之正文（僅查 042 簽核欄與檔名清單）；三份並行 agent 今日產出之新報告（`wm_annexf_*`／`wm_channel_registration_*`／`wm_m3_batch1_*`／`gov3b_*`／`kdo4_*`）之內容——它們只新增不修改，但**其結論可能與本檔某些數字互補或衝突，讀者宜對照**。

**引用自他區材料而未由我親自重跑者**（標為【引用】，可覆核指令已附於各處）：
- Z6 之 k1/k2/k3 史料模擬結果（7/7 序列全判死、mismatched 與 live 差 0.0014）——屬 self-reported 模擬，且門明文史料不得入證據列。
- Z5 之 `retrieval.py:408` NameError 死碼與「每次檢索多付約 1.3s」之計時。
- Z2 之 `CS-CLAUDE.md:50` 逐字內容、`OCV` 四處註解。
- （Z1 之 `ULTRACODE-SCHEDULE.md` 七框與 `2026-10-14` 命中數已由我親自重跑並更正，見 §6.4。）
- Z4 之 `knowhow_kh7_eligibility` 40 列／最新 run_id=6。

**self-reported 聲明（CLAUDE #32a）**：本檔一切「若壞了會不會安靜變綠」「這是假綠」「這是債」之判讀，均為 AI 自陳，**不得作為「世界如此」或「能力如此」之權威確認**。凡附有覆核指令者，指令輸出才是證據；未附指令者為推論，須實跑方能定論。本檔亦不代 Steward 認定任何 10-14 日曆項之開閉（RULING-2026-039 禁假關）。

**今晚三個可驗證的預測（供明日自我校準）**：
1. 23:00 run 22 起跑後，`promotion_queue` 應首次出現 `superseded` 列（I5B 生效點），且 q555 會被收斂。
2. 20:00 arena cron 把 08-03 收盤入庫後，sim anchor 實現，runner 可產首格 52 列 `mc_simulation_run`／`sim_run_link`。
3. 若 §4/D7 未修，09 月首波 settle 完成後 evaluator 會回報 `n_valid=0` 並印「等 settle 波」——**該訊息屆時為誤導，真因是 q_grid 解析失敗**。

---

## 附：本輪所讀主要表與程式（#20 對映，純分析零寫入）

**表**：`pg_class`／`pg_trigger`／`pg_proc`／`pg_roles`／`pg_database`／`pg_constraint`｜`world_concept(_version/_registry_current/_registry_legacy)`／`world_channel_binding`｜`evolution_run`／`evolution_iteration_ledger`／`raw_evolution_iteration_ledger`／`local_ai_iteration_ledger`／`sim_evolution_iteration_ledger`／`promotion_queue`／`evolution_apply_log`／`evolution_production_feature_set`／`evolution_kill_switch`／`evolution_deferred_work`／`evolution_prereg_gate`／`feature_sign_check`／`principle_factor_map`／`factor_direction_ruling`／`philosophy_principle`｜`validation_evidence`／`attestation_result`／`governance_proposal`／`steward_question_ledger`｜`knowledge_item(_text)`／`knowhow_auto_admit_state`／`knowledge_staging`／`knowledge_fulltext_status`／`knowledge_kh4_state`／`knowledge_query`／`knowledge_source`｜`simulation_method_registry`／`sim_evolution_candidate`／`mc_simulation_run`／`sim_run_link`／`sim_realized_outcome`／`sim_calibration_eval`／`sim_evolution_verdict`／`sim_llm_proposal`｜`direction_gate`／`direction_arena_prediction`／`feature_values`／`feature_candidate_values`／`TaiwanStockPriceAdj`。

**程式／檔**：`CLAUDE.md`／`HANDOFF.md`／`README.md`／`GROUNDING-MAP.md`｜`constitution/META-CONSTITUTION.md`／`AMENDMENT-LOG.md`／`RULING-2026-042`｜`docs/系統架構大憲章_v1.54.0.md`／`docs/compliance/CS-*`｜`ops/githooks/pre-commit`／`scripts/check_treaty_refs.py`／`check_cmd_matrix.py`／`check_false_assertions.py`／`check_vendor_binding.py`／`scripts/backup_database.sh`／`install_cron.sh`／`sync_memory.py`｜`tools/constitution_lint/{report.py,github-workflow.yml}`｜`src/augur/philosophy/evolution.py`／`retrieval.py`｜`scripts/run_evolution_iteration.py`／`run_philosophy_evolution.py`／`apply_evolution_promotions.py`／`report_triple_evolution_week.py`｜`scripts/reconcile_audit.py`／`src/augur/audit/reconcile.py`／`import_isolation.py`｜`src/augur/knowledge/{auto_admit,evidence,kh4,ingress_kip}.py`｜`scripts/{propose_sim_candidate,run_sim_calibration_cell,settle_sim_outcomes,evaluate_sim_calibration}.py`｜`tests/test_l716_conflict_registered.py`。

**結果落點**：本檔 ＋ `HANDOFF.md` 指針（已指向本檔）＋（可選）記憶更新。**不寫任何 DB 表、不改任何 [N] 文字、不 commit。**

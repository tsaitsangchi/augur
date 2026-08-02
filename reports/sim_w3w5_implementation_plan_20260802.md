# sim 軸 W3（評估器）＋W5（runner／回流）實作規畫 — SIM-CAL-R1 證據管線（2026-08-02）

> **性質**：[I] 實作計畫（CLAUDE #16/#20；憲章 v1.39.0 附 (a) 所讀既有表 schema ＋ (b) python 程式規畫）。
> **不創設判準**——判準 SSOT＝`evolution_prereg_gate` 之 `SIM-CAL-R1` 列 `criteria->>'criteria_text'`
> （binding，hugo 2026-08-02 19:49 親簽 approved）＋《模擬方法自進化專章 v1.0》（gp_86c8063fc688）。
> **本計畫全程唯讀取證（零 DDL、零 DB 寫入、零 commit）；唯一寫入＝本檔。未實作、未測試。**
> 親驗基準：live DB 現查 2026-08-02（git HEAD 52e33d9 之後）；所有數字出自 DB query（#9/#10）。
> 上游計畫：`reports/augur_local_ai_sim_evolution_impl_plan_20260731.md`（W1–W6 波次 SSOT）＋
> `reports/w2_20260801/D2S_sim_prereg_gate_proposal.md`（§3.4 程式規畫表；§9 Steward 已圈選建議案總成）。

---

## §0 摘要（30 秒版）與 W 編號對照

門已生效、時鐘已起算（approved_at=2026-08-02 19:49），**現況零 runner 在產新 run＝時鐘空轉**。
證據鏈四件缺口：①候選 0 列（W2 propose 工具未建）②live run 產生器未建 ③`sim_realized_outcome`
結算器未建（今日 repo 唯 `migrate_sim_evolution_ddl.py` 提及該表＝零 writer）④五臂評估器未建。
本計畫規畫 ③②＝W5（回流波）與 ④＝W3（評估波），並以最小代價解 ①（P0 一列候選）。
**第一個格點 asof₁≈2026-08-03（次一交易日）——runner 若在 1–2 日內落地即可準時產首格**
（遲到亦合法：iid_bootstrap 對 ≤asof 資料決定論，可補產，見 §4.3 誠實條款）。

**W 編號對照（消歧義；以 impl plan 20260731 §6/§8 為 SSOT）**：

| impl plan 波次 | 內容 | 本任務指派語 |
|---|---|---|
| **W3** | `arms`／`evaluate_sim_calibration`（五臂評估器） | 「W3 評估器」（同名） |
| **W4** | `decide_sim_verdict`（判決＋人閘） | 任務語「W4 settle?」**非**——settle 屬 W5 |
| **W5** | 回流：`settle_sim_realized`＋driver（＋本計畫補明的 live run 產生器） | 「W5 runner」 |

即：**settle 端 `sim_realized_outcome` 的 writer 是 W5 的 `settle_sim_realized.py`（未建）**，
W4 是判決工具（亦未建；killed/undecidable 可腳本寫、promoted 三鎖須人）。

---

## §1 現況親驗（2026-08-02；引用前請重跑）

### 1.1 門（判準 SSOT）

- `SIM-CAL-R1`：axis=sim、status=**approved**、approved_by=**hugo**、approved_at=**2026-08-02 19:49:40+08**、
  git_sha=52e33d9、evaluated_at/result_snapshot/evaluation_ref 皆 NULL（未評估）。
- **兩級指紋覆算全合**（本機 python 覆算）：
  - `sha256(criteria->>'criteria_text')` ＝ criteria_sha ＝ `9e0abe04…882c23b` ✓
  - `sha256((criteria->'thresholds')::text)` ＝ 文末 thresholds_sha ＝ `cd1e623a…baf5e9d4` ✓
- **52 檔凍結清單覆算合**：`SELECT DISTINCT target_id FROM mc_simulation_run WHERE target_id ~ '^[0-9]+$'`
  → 52 檔；**排序後以換行（`\n`）串接** sha256 ＝ `649221f491e67048…4125982ce4` ＝ thresholds.targets_sha ✓
  （口徑親驗：等價於 `string_agg(target_id, E'\n' ORDER BY target_id)`。）
- thresholds（T-A 嚴案）關鍵值：h=[21]、K（n_windows_min）=3、n_valid_min=100、date_clusters_min=3、
  cov_tol p80/p90=0.05、skill_metric=crps_mean、skill_arms=[floor,shuffled,mismatched]、
  skill_test={date_cluster_block_bootstrap, B=1000, seed=42, one_sided_lcb=0.95}、
  pit={ks, p_min=0.05, critical_values=date_cluster_bootstrap}、settle_modes=[normal,last_trade]、
  calendar=twse、promoted_allowed=true。

### 1.2 八表與物理鎖（全親驗）

| 表 | 列數 | 對本計畫要緊的約束 |
|---|---|---|
| `simulation_method_registry` | 1（iid_bootstrap registered，hugo 簽 2026-08-01 21:53，gate_ref=gp_df544cbb1b94） | param_schema required={horizon_td,n_paths,seed}、**additionalProperties:false**；tilt_free CHECK |
| `sim_evolution_candidate` | **0** | method FK→registry；spec_sha UNIQUE；trust_rank 必 TR-C；`simc_forward_only`（終態不可回改、spec_sha/method 身分欄不可改） |
| `sim_calibration_eval` | **0** | gate_id NOT NULL FK→prereg_gate；arm 六值；`uq_sce_cell` UNIQUE(gate_id, COALESCE(candidate_id,'-'), arm, eval_set_id, eval_code_hash)；`chk_sce_valid_le_runs`；DELETE/TRUNCATE 拒 |
| `sim_evolution_verdict` | **0** | `chk_sev_five_arm_floor`（promoted ⇒ arms_covered ⊇ 五臂）；`chk_sev_promote_signed`（promoted ⇒ 人簽三欄＋gate_proposal_ref FK→governance_proposal）；no_update/no_delete |
| `sim_evolution_iteration_ledger` | **0** | iteration_uid ~ `^sim-[0-9]{8}-r[0-9]{2}$`；終態（succeeded/failed）必填 gain_basis ∈{calibration_delta,none,incomparable} |
| `sim_llm_proposal` | **0** | （本輪不用——R1 非 llm_local 起手） |
| `sim_realized_outcome` | **0** | PK=run_id FK→mc_simulation_run；`chk_sro_forward`（label>asof）；`chk_sro_unsettleable_null`；settle_mode 三值；DELETE/TRUNCATE 拒（**UPDATE 未鎖——設計上寫一次不改**） |
| `sim_run_link` | **0** | PK=run_id（一 run 唯一臂/唯一候選）；arm 六值；candidate_id/gate_id NOT NULL FK |

- `mc_simulation_run`：**540 列全 asof=2026-05-31 史料**（數字 target 520 列/52 檔；另 1 檔
  `PORT_RankRidge_H60_2026-05-31` 20 列）。method CHECK 20 法含 iid_bootstrap。PK=run_id、
  **無 (target,asof,h,method,seed) 唯一鍵**——冪等靠決定論 run_id。honesty trigger：DELETE/TRUNCATE 拒、
  UPDATE 須 `SET LOCAL augur.honesty_write='on'`。
- `evolution_kill_switch`：**scope='sim' 列已在（state=clear，set_by=migrate_sim_constraints_ddl）**；
  code 側 `KILL_SCOPES` 已含 'sim'（`src/augur/philosophy/evolution.py:267`）＋
  `normalize_kill_state`/`effective_kill_state` 純函式可複用。**現況零消費者＝W5 接線點。**

### 1.3 資料與時鐘素材

- `TaiwanStockPriceAdj` TAIEX 錨最新日＝**2026-07-31（五）**；2026-08-02 之後尚無交易日入庫（正常，T+1 sync）。
- 52 檔凍結清單全數仍活躍（每檔 max(date) ≥ 2026-07-25 ✓）→ 首格 unsettleable 風險低。
- 2026-07 實收 22 交易日（TAIEX 親數）→「每 21 交易日一格」≈ 月頻。

---

## §2 可複用件盤點（結論）

| 件 | 可否複用 | 依據與缺口 |
|---|---|---|
| `scripts/simulate_mc_paths.py` 引擎函式（`_hist_logrets`/`_simulate`/`_summary`/`_git7`） | **可，為 W5 產 run 引擎核心**；sibling import 有先例（`simulate_portfolio_risk.py` 即 `from simulate_mc_paths import …`） | 四缺口見 §2.1——**不可整支直接當 runner** |
| `simulate_mc_paths.py` 之 `run()` 入口 | **不可**直接用 | (i) 一次固定雙法（iid＋block），block run 對本門是無主雜訊；(ii) run_id key=`mc_{stock}_{asof}_{h}_{method}_{seed}` **不含 n_paths/window/spec_sha**（多候選輪會撞 id 互蓋）；(iii) 不寫 `sim_run_link`、不識 gate/candidate、不讀 kill switch；(iv) summary 分位不足（§2.1-C） |
| `scripts/simulate_portfolio_risk.py` | **R1 不用** | 全為 PORT_* 組合層；判準明文「PORT_* 不入首輪（U-3 結算口徑未定）」 |
| `scripts/settle_arena_labels.py` | **W5 settle 之設計藍本**（不直接呼叫） | 已驗證語意可整套鏡射：TAIEX 已實現日曆數 label 日（未來日曆不可知）、`WAIT_DAYS=7` 停牌觀察、`UNSETTLE_GAP_DAYS=30`、PriceAdj factor 連續性檢核→factor_event 標 unsettleable、created_at<label 真未來斷言、冪等只挑未結列 |
| `src/augur/philosophy/evolution.py` kill-switch 純函式 | **可直接 import** | `normalize_kill_state`/`effective_kill_state`；W5/W3 以 `WHERE scope IN ('sim','global')` 讀表後過此函式 |
| `src/augur/simulation/` | **不存在**（親驗 src/augur 16 package 無 simulation） | W3 之 `calibration.py`/`arms.py` 為新建（impl plan §6 W2/W3 既定規畫） |

### 2.1 引擎複用的三個必修缺口（load-bearing）

- **A｜run_id 身分**：新 runner 的 run_id 改為 `"mc_" + sha256(f"simcal|{gate_id}|{candidate_id}|{stock}|{asof}|{h}|{spec_sha}")[:16]`
  ——含 spec_sha，未來多候選不撞；與史料 key 空間不同不衝突；冪等＝`ON CONFLICT (run_id) DO NOTHING`
  （**不走 DO UPDATE**：live 證據列一次寫死，亦免 honesty GUC）。
- **B｜雙法迴圈**：runner 只跑候選 spec 之單一 method（R1＝iid_bootstrap），直接呼叫 `_simulate(logr, h, n_paths, "iid_bootstrap", …)`。
- **C｜summary 分位不足（評估器的物理前提）**：現行 `_summary` 之 PCTS=(5,25,50,75,95)——
  **cov_p80 需要 p10/p90，現制拿不到**；PIT 與 CRPS 需細分位。W5 runner 於既有 summary 之上
  **追加 `terminal_q_grid`：終值報酬 p1..p99 共 99 分位**（仍是摘要、不存逐路徑＝四鎖②不破）。
  CRPS 以分位分解計（2×mean pinball over τ∈{.01..%.99}）、PIT 以 q_grid 反插值計 F(realized)。
  史料 540 列**不受影響也不回填**（判準明文史料不得入證據列）。

---

## §3 缺口清單（大→小）

1. **候選 0 列＋W2 propose 工具未建**：`sim_run_link.candidate_id` NOT NULL ⇒ 無候選則 live run 無法入鏈。
   R1 最小解＝P0 一列候選（§4.1），完整 propose_simulation_candidates.py 留 R2。
2. **live run 產生器不存在**：540 史料全 asof=2026-05-31；門後零新 run＝時鐘空轉（本計畫 W5-1）。
3. **settle writer 不存在**：`sim_realized_outcome` 全 repo 唯 migrate DDL 提及（本計畫 W5-2）。
4. **五臂評估器不存在**（本計畫 W3）。
5. **W4 判決工具不存在**（本計畫僅列現況與介面，不在本波實作範圍）。

---

## §4 W5 設計（回流波：產 run ＋ settle ＋ 薄編排）

### 4.1 P0（人裁前置；見 §10 停手點）——R1 候選一列

判準語「首輪即 iid_bootstrap 之 spec 變體」。registry param_schema `additionalProperties:false` 且
required={horizon_td,n_paths,seed}、h 被門釘 21 ⇒ **有意義變體空間近零**（歷史窗 756td 是引擎常數、
不在 schema）。建議 R1＝**單一基線候選**：

```
candidate_id = 'simc_r1_iid_baseline'（或 spec_sha 前綴式）
method='iid_bootstrap'；spec={"horizon_td":21,"n_paths":10000,"seed":42}
spec_sha=sha256(canonical JSON(sort_keys,separators))；origin='carryover'
origin_ref='mc_simulation_run 261 列史料基線（H2 入冊 gp_df544cbb1b94）'
gate_ref='SIM-CAL-R1'；is_synthetic=true（DB default；carryover 非 llm_local 不受 §2.3 強制，惟不改 default 亦無害）
note='engine window=756td（HIST_WINDOW_TD 常數；param_schema 外，據實記載）'
```

候選 INSERT 依專章非人簽欄（人閘在晉升），但**候選集合＝R1 評什麼**——屬 Steward 確認事項（停手點 S-1）。

### 4.2 W5-1｜`scripts/run_sim_live_window.py`（新；動作動詞片語 #18）

**職責**：在每個格點 asof 對 52 檔凍結清單產候選 spec 之 live run，寫 `mc_simulation_run`＋`sim_run_link`。

**格點數學（判準逐字落地）**：
- anchor＝`SELECT min(date) FROM "TaiwanStockPriceAdj" WHERE stock_id='TAIEX' AND date > '2026-08-02'`
  （＝「本門 approved_at 次一交易日」，資料驅動、不猜未來日曆；預期 2026-08-03）。
- 格點＝已實現 TAIEX 交易日序列上 index 0, 21, 42, …（`asof_k = anchor 之後第 21k 個交易日`）；
  窗 k＝(asof_k, asof_k+21td]，天然不重疊。**每格跑、非每日跑**——判準唯計格點 asof 之 run，
  非格點日產 run 無意義；觸發形式見 §4.4。
- **catch-up 冪等**：每次執行掃「所有 已實現≤資料最新日 之格點」，缺 run 的格點補產
  （iid_bootstrap 對 ≤asof 資料＋seed 決定論 ⇒ 晚產＝同結果；resume-safe，機器停擺不掉格）。

**逐格流程**：
1. kill switch：`scope IN ('sim','global')` 任一 halt ⇒ 印明 exit 1 零寫入（`effective_kill_state` 複用）。
2. 門防衛：重讀 SIM-CAL-R1，status='approved' 且**覆算兩 sha**，不符 ⇒ 拒產（拒評條款延伸到產端，便宜防呆）。
3. 凍結清單防衛：以**史料限定式**推導（`… WHERE target_id ~ '^[0-9]+$' AND asof_date='2026-05-31'`，
   史料受 DELETE 閘保護＝永穩定），覆算 sha 必等 targets_sha，不等 ⇒ halt（§9 R-1 陷阱）。
4. 逐檔：`_hist_logrets(cur, stock, asof, 756)` → `_simulate(logr, 21, 10000, 'iid_bootstrap', …, rng(seed))`
   → `_summary(...)` ＋ **追加 terminal_q_grid p1..p99**（§2.1-C）→ INSERT run（§2.1-A run_id；
   `ON CONFLICT DO NOTHING`）→ INSERT `sim_run_link(run_id, candidate_id, 'SIM-CAL-R1', iteration_uid, 'live')`。
5. 收尾印格點×52 檔對帳表（已產/跳過/歷史不足），歷史不足（<60td）者印明並留給 settle 端 n_excluded 口徑。

**執行指令矩陣（規畫）**：
```
python scripts/run_sim_live_window.py              # 無參數:現況(唯讀:格點對照表/已產/缺產/時鐘)
python scripts/run_sim_live_window.py --run        # 冪等:補產所有已到期缺產格點(kill switch/sha 三防衛)
python scripts/run_sim_live_window.py --run --asof 2026-08-03   # 只產指定格點(須為合法格點,否則拒)
python scripts/run_sim_live_window.py --selftest   # 零 DB:格點數學/run_id 決定論/q_grid 形狀/防衛紅測
```

### 4.3 誠實條款：遲產 run

判準唯以 `asof_date` 計 live 臂、未限 created_at。決定論方法晚產無洩漏，但**若產出時該格 label 已實現**
（realized 已知）觀感上是「先看答案再交卷」。設計：runner 預設**拒產 label 已實現之格點**、
須 `--allow-post-label` 明示旗標才產，且該批 run 於 link 時由 W3 在 detail 揭露
`post_label_created` 清單供 Steward 目視（run 之 created_at 本已入庫可稽）。政策本身列停手點 S-3。

### 4.4 觸發形式（排程＝W6/D-3 未解，本計畫不接 cron）

R1 全程僅需 **~3 次產格＋~3 次結算＋1 次評估**（K=3、月頻）。建議：**人工/有界自主逐次觸發**
（catch-up 冪等當保險，跑晚幾天無損），cron 接線留 W6 俟 Steward 解 D-3（impl plan R-1 車道原則不破——
本 runner 為秒級輕載，但「接排程」本身是 Steward 裁點）。

### 4.5 W5-2｜`scripts/settle_sim_realized.py`（新）

**職責**：對 `sim_run_link` 中 gate='SIM-CAL-R1' 且尚無 `sim_realized_outcome` 列之 run，判 label 並寫實現值。

**語意（鏡射 settle_arena_labels 已驗證口徑）**：
- label_date＝TAIEX 已實現日曆上「asof 後第 21 個交易日」（bisect；未實現則跳過待下輪——#8 不猜未來日曆）。
- 該檔 label 日有成交 ⇒ `settle_mode='normal'`、realized_close=close(label)；
  label 日無成交且市場日曆已過 label＋7 日 ⇒ `'last_trade'` 用最後成交價；
  最後成交距 label >30 日 ⇒ `'unsettleable'`（realized_logret NULL，`chk_sro_unsettleable_null`）；
  PriceAdj factor 於 [asof,label] 窗不連續 ⇒ `'unsettleable'`（factor_event；毒值不入證據，計 n_excluded）。
- realized_logret＝ln(close_label/close_asof)（asof 收盤＝run summary.last_close 同源自檢，差異>捨入即印警告）。
- 寫入紀律：insert-only 一次寫死（表無 UPDATE 閘，**自律不 UPDATE**）；逐列斷言 label>asof（CHECK 兜底）。
- kill switch 同 §4.2 步 1。

```
python scripts/settle_sim_realized.py              # 無參數:現況(唯讀:未結/已結/settle_mode 分佈)
python scripts/settle_sim_realized.py --run        # 冪等結算所有 label 已實現之 run
python scripts/settle_sim_realized.py --selftest   # 零 DB:label 數日/停牌分支/factor 檢核紅綠
```

### 4.6 W5-3｜薄編排與 ledger（R1 可選、R2 收斂）

impl plan 之 `run_sim_evolution_iteration.py`（全五節點 driver）R1 **不必等**——三支個別可執行即可走完。
惟 `sim_evolution_iteration_ledger` 落帳屬憲制（§3.6 gain_basis 載體）：R1 由**評估/判決側**開列
`iteration_uid='sim-20260803-r01'`（status planned→running→終態＋gain_basis），駕駛艙式 driver 留 R2。

---

## §5 W3 設計（五臂評估器）

### 5.1 檔與分工

| 檔 | 角色 |
|---|---|
| `src/augur/simulation/calibration.py`（新 library，#18 領域名詞＋自測矩陣） | 純函式：coverage／pinball／CRPS-from-q_grid／PIT／KS／日期簇 bootstrap（LCB 與 KS 臨界值） |
| `src/augur/simulation/arms.py`（新 library） | 五臂＋robot 構造與**完備性斷言**（缺任一臂 raise，不得靜默少跑） |
| `scripts/evaluate_sim_calibration.py`（新 CLI） | 編排：拒評防衛→收集→五臂計算→寫 `sim_calibration_eval`；`--check` 唯讀預演 |

### 5.2 拒評防衛（判準「評估紀律」逐字落地；先驗紅）

1. 覆算 `sha256(criteria->>'criteria_text')`＝criteria_sha 且 `sha256((criteria->'thresholds')::text)`＝
   文末 thresholds_sha，**任一不符 ⇒ 拒評 exit 1 零寫入**（負向 fixture 自測：假門壞 sha 必紅）。
2. targets_sha 覆算（§4.2 步 3 同式）。
3. 樣本外斷言：逐 run 斷言 `asof_date ≥ anchor` 且 asof ∈ 格點集；**史料（asof≤2026-05-31）任何數字不得混入**。
4. 臂完備：`arms.assert_complete` 缺臂 raise（robot 選配不在必列）。
5. kill switch 同前。

### 5.3 收集與 n 口徑

- 母集＝`sim_run_link`（gate='SIM-CAL-R1', arm='live', candidate=R1 候選）join `mc_simulation_run`
  join `sim_realized_outcome`。
- `n_runs`＝link 之 live run 總數；`n_valid`＝settle_mode∈{normal,last_trade} 且 q_grid 在的列；
  `n_excluded`＝unsettleable（含 factor_event）；日期簇＝distinct asof 格點數（K）。
- 名目量：52 檔×3 格＝156；n_valid_min=100 ⇒ 容忍 56 缺；date_clusters_min=3 ⇒ 三格皆須有結清列。

### 5.4 五臂構造（判準定義凍結之落地）

| 臂 | 構造（每觀測 i＝(target,asof)，realized＝realized_logret 換算之簡單報酬口徑對齊 q_grid） |
|---|---|
| live | run 之 terminal_q_grid（p1..p99）＝該觀測之預測分佈 |
| ceiling | 同 asof 窗內 52 檔實現值之**事後**經驗分位（每窗一錐、全 target 共用）；僅上界參照不參賽 |
| floor | 常態錐：σ_pooled×√21 之 N(0,·) 分位（p1..p99 解析式）；全 target 全 asof 同一 σ；σ 截止日見停手點 S-2 |
| shuffled | live 錐不動，同 asof×h 內 target 間實現值以 `np.random.default_rng(42)` 重排 |
| mismatched | target i 之 live 錐配 target j≠i 之實現值；固定 derangement seed=42（逐窗同一映射；有缺席 target 時對「該窗 valid 集」取 derangement 並記入 detail） |
| robot | 選配第六臂——**R1 不跑**（非地板要件） |

### 5.5 指標與判定素材（全部寫 `sim_calibration_eval`，判定本身屬 W4）

- `cov_p50/p80/p90`＝realized 落 [q25,q75]/[q10,q90]/[q5,q95] 之比率（q_grid 直讀——史料 summary 無 q_grid
  即物理算不出＝天然擋史料混入）。
- `pinball_mean`＝mean over τ∈{.05,.10,.25,.50,.75,.90,.95}；`crps_mean`＝2×mean pinball over τ=.01..%.99。
- `pit_ks_stat/p`＝PIT=F̂(realized)（q_grid 線性插值、端點外夾 [0.005,0.995] 記入 detail）之 KS 對均勻；
  **p 值以日期簇 bootstrap 臨界值**（B=1000, seed=42；K=3 之粒度限制誠實揭露於 detail，見 §9 R-3）。
- k2 素材：Δcrps(arm−live) 之逐簇均值＋date_cluster_block_bootstrap LCB(0.95)（B=1000, seed=42）落 detail
  （W4 讀之判「勝過每一臂」）。
- `eval_set_id`＝`'R1:h21:' + sha256('\n'.join(asof 格點))[:12]`；`eval_code_hash`＝
  sha256(calibration.py ∥ arms.py ∥ evaluate_sim_calibration.py 原始碼)——**評估碼變更即新 cell**（uq_sce_cell），
  實質變更即換尺（§5.3 專章：新 gate_id，非本工具自裁）。
- detail JSONB：σ_pooled 與其 SQL、格點清單、逐窗逐臂分項、bootstrap 診斷、post_label_created 揭露、
  derangement 映射、n 對帳。

```
python scripts/evaluate_sim_calibration.py            # 無參數:現況(唯讀:門态/證據水位/K 進度)
python scripts/evaluate_sim_calibration.py --check    # 全計算唯讀預演(不寫表;K<3 亦可跑=進度診斷)
python scripts/evaluate_sim_calibration.py --write    # 防衛全過+K≥3 才寫 5 列(live/ceiling/floor/shuffled/mismatched)
python scripts/evaluate_sim_calibration.py --selftest # 零 DB:合成資料回歸(已知常態→覆蓋收斂名目值/PIT 均勻)
                                                      #   +缺臂 raise 紅測+壞 sha 假門拒評紅測(R-5)
```

---

## §6 W4 現況與缺口（本計畫不實作，僅釘介面）

- **現況**：`decide_sim_verdict.py` 不存在；`sim_evolution_verdict` 0 列。
- **介面**：讀 5 列 eval＋thresholds → k1（cov tol）/k2（CRPS LCB 勝三臂）/k3（PIT p<0.05）/undecidable
  （n_valid<100 或簇<3 或缺臂）→ INSERT verdict。**killed/undecidable 可由腳本寫**（DB 層唯 promoted 綁
  `chk_sev_promote_signed` 三欄＋`chk_sev_five_arm_floor`＋enacted proposal 三鎖）；promoted 一律 hugo 親跑、
  工具**不設人名旗標**（專章 §4.2/§4.4 補強 2）。
- 時序上 W4 在 K=3 齊（≈2026-11 上旬）才用得到，**不是本波 critical path**；先驗紅樣板（§5.2）先鋪。

---

## §7 對應 schema（#20 (a)；**本計畫零新表零 DDL**——結果落既有表）

**寫入落點**：
`mc_simulation_run`（W5-1；run_id/target_id/asof_date/horizon_td=21/method/block_len_td=NULL/n_paths/seed/
summary(＋terminal_q_grid)/is_simulation=true/git_sha）→ `sim_run_link`（W5-1；run_id/candidate_id/
gate_id/iteration_uid/arm='live'）→ `sim_realized_outcome`（W5-2；run_id/target_id/asof_date/horizon_td/
label_date/realized_close/realized_logret/settle_mode/git_sha）→ `sim_calibration_eval`（W3；§1.2 全欄）→
（W4）`sim_evolution_verdict`；帳側 `sim_evolution_iteration_ledger`（§4.6）；P0 `sim_evolution_candidate` 一列。

**唯讀引用**：`evolution_prereg_gate`（SIM-CAL-R1 防衛）、`simulation_method_registry`（spec 驗 schema）、
`evolution_kill_switch`（scope in sim/global）、`TaiwanStockPriceAdj`（歷史報酬＋TAIEX 日曆＋結算價）。
各表全欄與約束之親驗清單見 §1.2（本檔即所讀 schema 之落卷）。

---

## §8 分階段與驗收（唯讀 SQL 可重跑）

| 階段 | 內容 | 驗收 |
|---|---|---|
| **P0**（人） | §10 S-1/S-2/S-3 三停手點裁示＋候選一列 INSERT | `sim_evolution_candidate`=1 列、gate_ref='SIM-CAL-R1'、spec 過 param_schema |
| **P1** | W5-1 runner＋W5-2 settle 落碼（矩陣＋selftest 首提交即備 #18/#29d） | 兩支 `--selftest` rc=0（防衛紅測「先驗紅」：壞 sha/壞清單/halt 必紅）；無參數 graceful |
| **P2**（≈08-03/04） | 首格產出 | `mc_simulation_run` 新增 52 列（asof=anchor、h=21、iid）＋`sim_run_link` 52 列 arm='live'；重跑 `--run` 零新增（冪等證明） |
| **P3**（09-01 前） | W3 三檔落碼 | `--selftest` 合成回歸過（覆蓋±MC 誤差內收名目值）；`--check` 對 P2 實料可跑（K=1 印 undecidable 進度） |
| **P4**（≈09-02 起逐窗） | settle 波 1/2/3＋`--check` 增量診斷 | `sim_realized_outcome` 逐窗 +≤52；settle_mode 分佈印出；n_excluded 口徑對帳 |
| **P5**（≈11 上旬） | K=3 齊 → `--write` 5 列 → W4 判決（另波） | `sim_calibration_eval` 恰 5 列同 eval_set_id/code_hash；detail 含 k2 LCB 素材；後續 verdict 屬 W4 |

---## §9 風險

| # | 風險 | 處置 |
|---|---|---|
| R-1 | **凍結清單 SQL 自指陷阱**：binding 推導式無 asof 過濾——任何人對「新的數字 target」跑 simulate_mc_paths 即改變 DISTINCT 集→sha 崩 | 推導一律加史料限定（asof='2026-05-31'，受 DELETE 閘保護＝永穩）＋sha 必等 pinned 才跑；R1 期間 ops 紀律：勿對新股 ad-hoc 產 run（違者 sha 防衛會 halt、不靜默） |
| R-2 | 引擎中途改碼＝live 臂跨窗異碼 | run 已存 git_sha 逐列可稽；紀律：R1 期間凍結 `simulate_mc_paths` 引擎函式；不得不改則揭露＋Steward 判是否換尺 |
| R-3 | K=3 簇 bootstrap 粒度極粗（3 簇重抽僅 10 種多重集）；LCB/KS-p 可能退化 | 判準 binding 照做；退化方向＝偏 undecidable/killed（保守、非 pass 灌水）——設計內結果，detail 揭露粒度 |
| R-4 | unsettleable 超額→n_valid<100 | undecidable＝合法產出（專章 §5.4）；52 檔現全活躍，風險低；逐窗 settle 即時看分佈 |
| R-5 | 校準指標自身算錯 | 合成資料回歸自測（已知分佈→覆蓋收斂名目、PIT 均勻）＋缺臂 raise＋壞門拒評三紅測，先驗紅再轉綠 |
| R-6 | sync 斷檔/機器停擺跨格點 | catch-up 冪等補產（決定論）＋§4.3 遲產揭露；補產僅用 ≤asof 資料，無洩漏面 |
| R-7 | 評估前門列被動 payload（trigger 護 sha 欄不護 payload） | 拒評條款＝每次評估即覆算，動 payload 必被抓（D2S §2.3 已預埋此設計） |

## 拍板登錄（2026-08-02 夜）

> **Steward 圈選（AskUserQuestion 留痕）**：「simW-照建議」——S-1 單一基線候選／S-2 σ 截止 2026-07-31／
> S-3 catch-up 註記遲產／S-4 R1 人工逐次觸發，四點全採。實作授權成立（W2→W5→W3；
> promoted 三鎖人簽欄唯 hugo；首個真產格 run 於 08-03 資料到位後）。

## §10 停手點與未定（誠實；不自裁）

- **S-1｜R1 候選集合**：param_schema 封閉（additionalProperties:false、h 釘 21）⇒「spec 變體」實際空間
  近零。建議單一基線候選（§4.1）；候選集合＝「R1 評什麼」，**請 Steward 確認**（含 origin='carryover' 之認定）。
- **S-2｜floor σ 之「全史」截止日**：判準未定。建議 ≤2026-07-31（approved 前最後交易日；先於樣本外窗、
  決定論可覆算），σ 與 SQL 全文落 eval detail。**請裁示**（此值直接進 k2 對手臂）。
- **S-3｜遲產政策**：label 已實現後補產 live run 是否允許（§4.3；預設拒＋旗標明示＋detail 揭露）。**請裁示**。
- **S-4｜排程**：W6/D-3 未解，本計畫全程人工/有界自主逐次觸發；接 cron 屬 Steward 裁點。
- **U-3（承襲）**：PORT_* 結算口徑仍未定——R1 明文不入，本計畫零 PORT 工作，不猜。
- 專章 §4.5 三筆既有自測簽名之處置：Steward 裁量中，與本波無交集，不動。

## §11 時鐘數學（估計值；實際一律以已實現 TAIEX 日曆資料驅動）

- anchor（次一交易日）＝**2026-08-03（一）**待 sync 證實；asof₁=anchor。
- 純平日數法（8 月無台股假日）：**asof₂=label₁=2026-09-01**；9 月若中秋(09-25)＋教師節(09-28)休市 ⇒
  9 月 20 td：**asof₃=label₂≈2026-10-01~10-06**；10 月若 10-09 彈休 ⇒ 21 td：**label₃≈2026-11-03/04**。
- ⇒ 第一格滿（label₁ 結清＋sync）≈ **2026-09-02**；**K=3 齊 ≈ 2026-11 上旬**；
  T-A verdict 最早 ≈ **2026-11 上旬**（label₃＋T+1 sync＋settle＋eval，與 D2S §4 自估一致）。
  未來假日不在 DB、以上為估——runner/settle 全部按已實現日曆計，估錯只挪日期不挪判準。

> 本計畫未經獨立核驗（RULING-2026-028 第 3 點）；未執行任何變更。數字皆 2026-08-02 live 現查。

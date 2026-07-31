# 本地 AI 股市模擬自進化 — 實作計畫書 v1（2026-07-31）

> **性質**：[I] 實作計畫。**不創設治權判準**——本軸判準已由《模擬方法與自進化元件專章 v1.0》
> （2026-07-31 enacted，`gp_86c8063fc688`）成文；本計畫只做「把已生效之條文接成會跑的東西」。
> **依 CLAUDE #20 計畫先行**；依憲章 v1.39.0 附 **(a) table schema**（§5）與 **(b) python 程式規畫**（§6）。
> **基礎文件（Steward 指定）**：`reports/augur_plain_language_full_report_20260730.md`
> （說人話報告書 v2・世界建構版）。
> **取代關係**：`reports/augur_local_ai_market_sim_evolution_plan_20260731.md`（910 行，P0–P7）為**前身**——
> 該檔成文於專章 enact **之前**，其 §九 三件拍板事項已於同日全數獲解（見 §1.3）。
> 本檔以專章生效後之現況重寫，前身降為史料、其 H-1~H-18 硬邊界仍有效並於 §4 承接。
> **現況取樣**：2026-07-31 傍晚（單一角色整併後）。**引用前重跑附註指令。**

---

## §1 這件事在世界裡的位置（承說人話報告書 v2）

### 1.1 為什麼是「本地」——這不是成本選擇

說人話報告書 §四之二 第 3 條逐字：

> **推理與嵌入接縫一律限本機模型**——大憲章明標「不可違反」之隱私上限：**禁任何外部／雲端 LLM**，
> 且可靠度不足之解**不得以外部 LLM 換取**（因引文可能含私有 `owned_local` 內容）。
> 所以「本地 AI 自進化」不是成本選擇，是**憲法要求**。

⇒ 本計畫之 LLM 環節（`origin='llm_local'` 之候選生成）**只准走 ollama 本機**。
外部 API 不是「暫不用」，是**不得用**。此為 H-0，優先於一切效能考量。

### 1.2 為什麼是「模擬」而不是「預測」

說人話報告書 §四 表列第五行（⑤模擬方法）逐字：

> 凍結判讀規則同場競技→保守值入風險畫像→自己也上擂台受審
> ｜四法一輪結案（天真法把尾巴低估一個數量級）；**MC 隊方向判死＝「模擬畫風險形狀、不猜方向」的邊界實證**

專章 §1.2 把這件事釘成永久除外項：**逐日／任意粒度之價格點位、價格路徑、目標價無 GATE 可解**
（解除唯再修憲）。⇒ 本軸產物**只能是風險形狀**，且硬綁「模擬非預測」標示。

**這條界線是本計畫最重要的護欄**：任何「讓模擬更準地猜方向」之改良方向，**在本軸為非法**，
不是「先不做」。專章 §3.6 已把它下沉為 DB CHECK（`gain_basis`）與 §3.7（`tilt_free`）。

### 1.3 三件拍板事項已解（前身計畫 §九）

| 項 | 專章之定案 | 落點 |
|---|---|---|
| ①終審定性 | **統計級——校準檢定**（覆蓋率＋PIT 均勻性），**明文非 #14 經濟終關** | 專章 §3.5（選定甲） |
| ②人簽層級 | **偵測級＋三項最低補強**（TTY 閘／selftest 不寫人簽欄／明文承認非預防） | 專章 §4.4（選定甲′） |
| ③axis 登錄 | **registry 表**（`evolution_axis`），性質認定＝patch | 專章 §8（選定乙）；`evolution_axis` 5 軸含 `sim` |

---

## §2 現況：條文已生效，但軸完全空轉

**全部 2026-07-31 傍晚實查**：

| 項 | 值 | 意義 |
|---|---|---|
| sim 八表 | **全部 0 列** | 專章生效、零實跑 |
| `simulation_method_registry` | **0 列** | **⚠ 候選物理死鎖**（見下） |
| `evolution_prereg_gate` 之 `axis='sim'` | **0 列** | **§3.1 節點二未成立**——判準未凍結，不得跑候選 |
| `evolution_kill_switch` scope | `global／tw／lai／raw`——**無 `sim`** | 緊急煞車對本軸無作用點 |
| `src/augur/simulation/` | **不存在** | P3–P6 未起 |
| sim 驅動腳本 | **0 支** | 同上 |
| `mc_simulation_run`（史料） | **540 列／20 method** | 首批註冊之標的與回填素材 |

### 2.1 四個必須先解的阻塞（順序不可換）

**B-1｜候選物理死鎖**：`sim_evolution_candidate.method` 有 FK → `simulation_method_registry(method)`，
而 registry 為 0 列 ⇒ **任何候選在 DB 層寫不進去**。
解鎖須先註冊方法；而 `chk_smr_registered_signed` 要求 `status='registered'` 時
`approved_by`／`approved_at`／`gate_ref` **三者非空**，`gate_ref` FK→`governance_proposal`
⇒ **每次註冊方法都要一件治權提案**。20 個既有 method 是**一件包裹提案**還是逐件？**未定，屬 D-1。**

**B-2｜節點二未成立**：專章 §3.1 要求每輪評估前先於 `evolution_prereg_gate` 建 `axis='sim'` 一列
（可證偽條件／樣本外窗／臂組成／門檻／`criteria_sha`）。**現 0 列** ⇒ 依專章不得跑候選。
建立該列須 Steward 親簽（人閘）。

**B-3｜kill switch 無作用點**：`KILL_SCOPES = ("tw","lai","raw","global")` 寫死於
`src/augur/philosophy/evolution.py:242`，且 `scripts/set_evolution_kill_switch.py:52` 自測**硬斷言四值封閉集**、
`:111` argparse `choices` 限四值 ⇒ 加 `sim` **須同時改碼、改自測、並由 hugo 親跑 INSERT**（人簽欄）。
**在此之前，本軸唯一的煞車是 `global`（會一併停掉三軸）。**

**B-4｜車道**：專章附二第 1 項之警告已於同日應驗——`evolution_deferred_work` 因
「heavy slot busy」連三日推遲，tw 軸長佔 slot。**sim 軸接進同一 slot 將使四軸互相餓死。**

### 2.2 兩個條文與 DB 落地之落差（趁零列時修，成本隨時間單調上升）

| 專章條文 | DB 現況 | 落差 |
|---|---|---|
| §2.3「`origin='llm_local'` 永久攜 `is_synthetic=true`」 | `sim_evolution_candidate.is_synthetic` 僅 `NOT NULL DEFAULT true`，**無 CHECK** | `origin='llm_local'` ∧ `is_synthetic=false` 之列**可合法寫入** |
| §3.6「目標函數僅得為校準品質」 | `gain_basis` **nullable** | 不填即繞過值域 CHECK |
| §3.4「五臂地板不可省」 | `arm` 為六值枚舉（含 robot＝加嚴），但**無完備性約束**；`chk_sev_evidence_nonempty` 僅要求 ≥1 筆 | **單臂證據即可開判決** |

---

## §3 目標與非目標

### 3.1 目標（三層，逐層可獨立驗收）

**T-1｜讓軸能合法跑起來**：解 B-1～B-4，跑出**第一輪完整五節點**（候選→證據→人閘→判決→回流），
產出**一筆 `sim_evolution_verdict`**——無論該筆是 `promoted` 還是 `killed`。
（專章 §5.4：**誠實的無能宣告與有效之能力宣告同為合法產出**。）

**T-2｜讓本地 AI 參與候選生成**：`origin='llm_local'` 之候選經 `sim_llm_proposal` 落帳，
攜 `is_synthetic=true`／`TR-C` 天花板，與 `grid`／`human` 候選**同場競技**、不享特權。
承靈魂 v1.10.0 之終點（讓本地 AI 具備與人一樣的判斷力）——**本軸是該終點的一個可判定分域**。

**T-3｜讓校準品質成為可回流之後果**：`sim_realized_outcome` 落地，實現值回流比對預測分位錐，
校準劣化即自動開新候選輪（專章 §6.2「不得靜默沿用」）。

### 3.2 非目標（明文排除，非「暫不做」）

- **不做方向預測**：任何以模擬猜漲跌、產生點位／路徑／目標價者，**本軸為非法**（§1.2）。
- **不以經濟價值為終審**：本軸終審為統計級校準（專章 §3.5 已明文非 #14）。
- **不外接雲端 LLM**（§1.1，憲法要求）。
- **不繞過人閘**：`gate_ref`／`approved_by` 一律 hugo 親跑；本軸工具**不設人名旗標**（專章 §4.2）。
- **不自行擴 axis 值域**：新軸＝`evolution_axis` INSERT 一列（專章 §8），不改 CHECK。
- **不動 SUNSET**：sim 軸**不在** V2-SUNSET 三軸範圍（其 criteria 針對 arena／prodset／LAIEVO），
  **本軸不構成續命路徑**，反而分食同一 heavy slot（見 B-4）。

---

## §4 硬邊界（承前身計畫 H-1~H-18，經專章生效後重述）

| # | 邊界 | 機械落點 |
|---|---|---|
| **H-0** | LLM 一律本機（憲法要求，非成本） | `augur.advisor.ollama._assert_local_host`（現有） |
| **H-1** | 無逐日價格點位／路徑／目標價欄 | `migrate_sim_evolution_ddl` 之關鍵字黑名單（**現為 4 字串正則、非結構驗證**——見 §7 R-2） |
| **H-2** | 目標函數僅校準品質 | `gain_basis CHECK`（**須補 NOT NULL**，見 §6 W1-3） |
| **H-3** | 禁 tilt 抽樣 | `simulation_method_registry.tilt_free CHECK (tilt_free)` NOT NULL（**已足**） |
| **H-4** | 判準先於資料、指紋錨定 | `evolution_prereg_gate.criteria_sha`（覆算不符即拒） |
| **H-5** | 五臂地板不可省 | **現僅值域枚舉、無完備性**（見 §6 W1-3） |
| **H-6** | 判決 append-only、終態單向 | `sev_no_delete`／`sev_no_truncate`／`sev_no_update`／`simc_forward_only`（**已足**） |
| **H-7** | 換尺＝換身分（T.28） | `uq_sce_cell` 含 `eval_code_hash`（**已足**） |
| **H-8** | AI 不得代簽、工具不設人名旗標 | `migrate_sim_evolution_ddl --selftest` 三項行為鎖（**已足**） |
| **H-9** | OCV 單向棘輪：可調維度僅模擬參數 | **無機械落點**——屬審查紀律（見 §7 R-4） |

---

## §5 對應 table schema（憲章 v1.39.0 強制節 a）

### 5.1 已存在、本計畫消費之表（八表＋二史料表）

| 表 | 關鍵欄 | 關鍵約束 | 現列數 | 本計畫用途 |
|---|---|---|---|---|
| `simulation_method_registry` | method(PK)／family／param_schema／**tilt_free**／status／gate_ref／approved_by | `chk_smr_registered_signed`（人簽三欄）；`tilt_free` 必 true；family 六值 | **0** | W1 首批註冊 |
| `sim_evolution_candidate` | candidate_id(PK)／method(FK)／spec／spec_sha／origin／**is_synthetic**／trust_rank／status | origin 四值；`trust_rank` 必 `TR-C`；`simc_forward_only` | 0 | W2 候選 |
| `sim_calibration_eval` | gate_id／candidate_id／**arm**／eval_set_id／eval_code_hash／覆蓋率／PIT | `arm` 六值枚舉；`uq_sce_cell` 唯一 | 0 | W3 五臂評估 |
| `sim_evolution_verdict` | verdict／decided_by／gate_proposal_ref／evidence_eval_ids | `chk_sev_promote_signed`；`chk_sev_evidence_nonempty(≥1)`；三 guard | 0 | W4 判決 |
| `sim_evolution_iteration_ledger` | iteration_uid／status／**gain_basis**／steps_json | `gain_basis` ∈(calibration_delta,none,incomparable)**或 NULL** | 0 | W2–W4 落帳 |
| `sim_llm_proposal` | — | `CHECK (is_synthetic)` | 0 | T-2 |
| `sim_realized_outcome` | run_id／target_id／asof_date／horizon_td／**realized_close**／realized_logret／settle_mode | — | 0 | T-3 回流 |
| `sim_run_link` | arm／run_id | `arm` 六值 | 0 | 評估↔run 橋 |
| `mc_simulation_run`（史料） | run_id／method／n_paths／seed／**is_simulation**／summary | `CHECK (is_simulation)`；`mcsim_no_delete`／`no_truncate` | **540／20 法** | W1 註冊素材、W5 回填對照 |
| `evolution_prereg_gate` | gate_id／**axis**(FK→evolution_axis)／criteria／criteria_sha／status | — | 1（V2-SUNSET） | W1 建 sim 門 |

### 5.2 本計畫需新增之 DDL（**皆為補既有落差，不新建表**）

```sql
-- W1-3a｜§2.3 之機械化：llm_local 候選必攜 synthetic 標記（趁 0 列時加，零遷移成本）
ALTER TABLE sim_evolution_candidate
  ADD CONSTRAINT chk_sce_llm_is_synthetic
  CHECK (origin <> 'llm_local' OR is_synthetic);

-- W1-3b｜§3.6 之 NULL 缺口封閉：終態輪必須聲明目標函數基礎
ALTER TABLE sim_evolution_iteration_ledger
  ADD CONSTRAINT chk_seil_gain_basis_on_terminal
  CHECK (status NOT IN ('succeeded','failed') OR gain_basis IS NOT NULL);

-- W1-3c｜§3.4 五臂完備性：判決之證據須涵蓋五臂（robot 為加嚴之第六臂、不強制）
--   以 verdict 側之 CHECK 落地；arms_covered 為新欄（text[]），由評估收攏時寫入。
ALTER TABLE sim_evolution_verdict ADD COLUMN IF NOT EXISTS arms_covered text[];
ALTER TABLE sim_evolution_verdict
  ADD CONSTRAINT chk_sev_five_arm_floor
  CHECK (verdict <> 'promoted' OR
         arms_covered @> ARRAY['live','ceiling','floor','shuffled','mismatched']::text[]);
```

**新增一列（非新表）**：`evolution_kill_switch` 之 `scope='sim'`——**須 hugo 親跑 INSERT**（人簽欄），
且 code 側 `KILL_SCOPES` 與其自測須同批改（見 §6 W1-4）。

---

## §6 對應 python 程式規畫（憲章 v1.39.0 強制節 b）

> **命名依 CLAUDE #18**：package＝管線階段（`src/augur/simulation/`）；library 模組＝**領域名詞**；
> CLI script＝**動作動詞片語**。每支具 `__main__`＋`--selftest`（免 DB 免 API）＋執行指令矩陣（#29d）。

### W1｜解阻塞（可全自動，除人簽三處）

| 檔 | 角色 | 關鍵簽名 | 輸入→輸出表 |
|---|---|---|---|
| `scripts/migrate_sim_constraints_ddl.py` | **新**：落 §5.2 三條 CHECK＋`arms_covered` 欄 | `--check`／`--apply`／`--selftest` | DDL only；`--check` 查 live `pg_constraint` |
| `src/augur/philosophy/evolution.py:242` | 改：`KILL_SCOPES` 加 `"sim"` | — | — |
| `scripts/set_evolution_kill_switch.py:52,111` | 改：自測封閉集與 argparse choices 同步 | — | `evolution_kill_switch` |
| `scripts/register_simulation_method.py` | **新**：方法註冊 CLI（**不設人名旗標**；`--gate-ref` 須指向已 enacted 之 proposal） | `register(method, family, param_schema, tilt_free, gate_ref)` | → `simulation_method_registry` |
| `scripts/preregister_sim_gate.py` | **新**：建 `axis='sim'` 之預註冊門（判準凍結＋`criteria_sha`） | `preregister(criteria)`／`--check` | → `evolution_prereg_gate` |

### W2｜候選與 LLM 提案

| 檔 | 角色 | 關鍵簽名 |
|---|---|---|
| `src/augur/simulation/method_spec.py` | 領域名詞：method＋參數之規格與 `spec_sha` 正規化 | `spec_sha(spec: dict) -> str`；`validate(spec, param_schema)` |
| `src/augur/simulation/calibration.py` | 領域名詞：校準指標（覆蓋率、PIT 均勻性、CRPS） | `coverage(paths, realized, qs) -> dict`；`pit_uniformity(...) -> dict` |
| `scripts/propose_simulation_candidates.py` | 動作：由 grid／human／**llm_local** 產候選 | `--origin {grid,llm_local,human}`；LLM 走 `advisor.ollama`（H-0） |

**LLM 環節之硬紀律**：產出一律 `is_synthetic=true`／`trust_rank='TR-C'`（專章 §2.3），
且經 `sim_llm_proposal` 落帳；**不得單獨作為任何高風險 Action 之依據**。

### W3｜五臂評估（本軸之核心加嚴）

| 檔 | 角色 |
|---|---|
| `src/augur/simulation/arms.py` | 五臂＋robot 之定義與**完備性斷言**（缺臂即 raise，不得靜默少跑） |
| `scripts/evaluate_sim_calibration.py` | 動作：對某 gate×candidate 跑五臂、寫 `sim_calibration_eval`；`--check` 唯讀預演 |

**地板鐵律**（專章 §3.4，記憶級）：地板未被顯著超越者，**該分數不得作為能力宣稱**。
本軸不得以「模擬與評測不同」為由豁免——實證＝2026-07-26 常數字串 0.654 > 冠軍 0.492。

### W4｜判決與人閘

| 檔 | 角色 |
|---|---|
| `scripts/decide_sim_verdict.py` | 動作：收攏證據→寫 `sim_evolution_verdict`（`promoted` 須人簽三欄非空；**AI 不得代填**） |

### W5｜回流

| 檔 | 角色 |
|---|---|
| `scripts/settle_sim_realized.py` | 動作：實現值回流寫 `sim_realized_outcome`，比對分位錐 |
| `scripts/run_sim_evolution_iteration.py` | 動作：一輪五節點編排（比照 `run_evolution_iteration.py` 之 driver 體例，**含 #33 之非阻塞紀律**） |

---

## §7 對抗自問（#20 要求；本計畫之已知弱點）

| # | 風險 | 現況與處置 |
|---|---|---|
| **R-1** | **四軸互相餓死**（B-4 已應驗於三軸） | **本計畫 W1–W4 全程不接 heavy slot**——評估以小樣本、單次手動觸發；接排程屬 W6，**須先解車道**（D-3） |
| **R-2** | H-1 之 4 字串黑名單非結構驗證 | 新增欄位時仍可繞過。建議改為「欄名白名單＋新欄須列舉」，列 D-4 |
| **R-3** | `migrate_sim_evolution_ddl:368` 之 §2.3 自測為**串接字串子字串比對** ⇒ 缺 CHECK 仍全綠 | §5.2 之 `chk_sce_llm_is_synthetic` 補上後，自測須改為**查 live `pg_constraint`**（非字面） |
| **R-4** | H-9（OCV 可調維度）無機械落點 | 誠實列為紀律而非機制；`sim_evolution_candidate.spec` 之 diff 審查屬人工 |
| **R-5** | 校準指標本身之正確性無獨立驗證 | W3 須含**已知答案之合成資料回歸**（給定分佈→覆蓋率應收斂至名目值） |
| **R-6** | 本軸產物若被誤讀為預測 | 專章 §1.2＋H-1；另**所有輸出一律硬綁「模擬非預測」標示**（承四鎖先例） |

---

## §8 分階段行程與驗收

| 波 | 內容 | 可自動？ | 驗收（唯讀可重跑） |
|---|---|---|---|
| **W1** | 解阻塞：三條 CHECK＋`arms_covered`／kill switch 加 sim／首批方法註冊／建 sim 門 | **部分**——DDL 與改碼可自動；**方法註冊之 `gate_ref`、kill switch INSERT、門之 approve 三處須 hugo** | `psql` 查三 CHECK 在位；`evolution_kill_switch` 有 sim 列；`simulation_method_registry` ≥1 且 `status='registered'`；`evolution_prereg_gate` 有 `axis='sim'` 且 `criteria_sha` 非空 |
| **W2** | `method_spec`／`calibration`／`propose_simulation_candidates` | **是** | 各支 `--selftest` rc=0；產出 ≥1 列 `sim_evolution_candidate`（DB 層可寫＝B-1 已解之證明） |
| **W3** | `arms`／`evaluate_sim_calibration` | **是** | 五臂齊備斷言之**行為級測試**（故意少跑一臂→須 raise）；合成資料回歸（R-5） |
| **W4** | `decide_sim_verdict` | **否**（人簽） | `sim_evolution_verdict` ≥1 列；`promoted` 者三欄非空且 `gate_ref` 指向 enacted proposal |
| **W5** | 回流：`settle_sim_realized`／`run_sim_evolution_iteration` | **是** | `sim_realized_outcome` ≥1 列；校準劣化觸發新輪之行為級測試 |
| **W6** | 接排程 | **否**（須先解車道 D-3） | — |

**T-1 之終局驗收**：`sim_evolution_verdict` 出現**第一筆**——`promoted` 或 `killed` 皆算成功。
（專章 §5.4：誠實的無能宣告為合法產出。）

---

## §9 拍板點（Steward）

| # | 事項 | 阻塞 |
|---|---|---|
| **D-1** | 20 個既有 method 之註冊路徑：**一件包裹提案** vs **逐件**（`chk_smr_registered_signed` 要求每筆帶 `gate_ref`） | W1／B-1 |
| **D-2** | sim 門之判準內容：可證偽條件、樣本外窗、臂組成、校準門檻（覆蓋率容差／PIT p 值） | W1／B-2 |
| **D-3** | 車道：sim 是否接 heavy slot；若接，四軸如何排序（現三軸已互相餓死） | W6 |
| **D-4** | H-1 是否由關鍵字黑名單改為欄名白名單（結構驗證） | R-2 |
| **D-5** | 首輪標的：以 `mc_simulation_run` 之 540 列史料回填校準，或另取新窗 | W3 |

---

## §10 未知與誠實界定

- **U-1**：校準門檻之合理值（覆蓋率容差、PIT 顯著水準）無先例，須 D-2 定；本計畫不代擬數字。
- **U-2**：20 個 method 之 `param_schema` 須逐一從 `mc_simulation_run.summary` 反推，**尚未做**。
- **U-3**：`realized_close` 之結算口徑（`settle_mode`）與 arena 之 `settle_arena_labels` 是否共用，未查。
- **U-4**：本計畫未估 LLM 候選生成之車道成本（qwen3:4b 於 CPU-only 本機）——W2 動工前須實測單次耗時。
- **本計畫未經獨立核驗**（`RULING-2026-028` 第 3 點）；亦**未執行任何變更**。

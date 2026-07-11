# augur 審議引擎補完計畫 — 從 A5「not_yet」到可信賴驗證

- **日期**:2026-07-11
- **檔案**:`reports/augur_deliberation_completion_plan_20260711.md`(#16 命名)
- **性質**:計畫先行報告(CLAUDE #20 v1.39.0:附 (a) table schema〔§1.5 所讀既有表+§2/§3/§4 新表 DDL〕+ (b) python 程式規畫〔§2/§3/§4 各節+§3.4 總表〕+ 元件〔§5〕+ 分階段〔§6〕+ 驗收〔各節+§6〕)
- **上游裁決**:審議引擎 A5 自審(wf_472951a6,40 agents)裁決=**not_yet**——MVP 可用、「可信賴驗證」未達:3 blocker、模式 4/9/10 未實作、七片零量測
- **SSOT 引用**:十模式完整版設計與預註冊判準=`reports/augur_local_ultracode_engine_plan_20260710.md`(下稱 **master 計畫**;§5.1 為預註冊判準唯一 normative 節);本計畫=其「補完執行篇」,與 master 衝突處以 master 為準、據實差異列 §3.0
- **數字口徑**:本檔所有現況數字於 2026-07-11 經 DB 實查(`augur.core.db`)或 read code 取得,並經獨立對抗批判 pass 逐項複核(裁定:草稿 §1 現況盤點零幻像);定稿合併僅修訂**設計層**(批判 A1-A3/B1-B5/C1-C3,對照見附錄 A),未改動任何現況數字(#9 零幻像)
- **修訂記錄**:v1 草稿(前半+後半)→ 對抗批判(12 項具體缺陷)→ **本定稿**(全數修訂納入)

---

## 目錄

- §0 三十秒摘要
- §1 現況誠實盤點(帳本/十模式/三 blocker/七片/既有表 schema)
- §2 三 blocker 封閉設計(B1 語意綁定/B2 GATE-lite/B3 fast_anchor 規則化)
- §3 模式補完(§3.0 與 master 差異表;模式 10→9→4;§3.4 程式規畫總表)
- §4 七片零量測維度封閉(D1–D7)
- §5 共用元件(5-A~5-E)
- §6 分階段執行、時間/硬體預算與驗收總表
- §7 誠實邊界、不做清單與拍板點
- 附錄 A 批判修訂對照表

---

## §0 三十秒摘要

本地審議引擎(qwen 提可機驗宣稱 → 5 oracle 確定性裁決 → 帳落 `deliberation_*`)的 MVP 已上線且方向性證據成立:2026-07-11 三重覆基準(git e2f257a)引擎臂 **72/72 判對、假確認 0**,單發臂 36/72、假確認 6(`deliberation_benchmark` 實查)。但 A5 自審裁決 **not_yet**——「可用」不等於「可信賴」:

1. **三個 blocker 未封**:①confirmed 機械鎖只鎖「錨成立」、不鎖「claim 語意=錨語意」(語意層架空);②master 計畫預註冊 GATE(+15pp/McNemar/3 輪)**從未跑過**,現有 54 列 benchmark 全部是手動 CLI 對照、判準無快照;③`fast_anchor` 讓 claim 文字本身即可鑄造 db_query/pytest 錨、無條件覆寫 verifier 指派(注入通道)。
2. **三個模式未建**:模式 4(judge panel)/9(自我迭代)/10(resume run-task 帳本)——無 `deliberation_run/task/proposal/panel_score` 表、無 idempotency_key、無 `--resume`。
3. **七片零量測**:效能/可重現/長跑/resume/人裁閉環/redline/跨模一致率,全部零數據或零 consumer。

**本計畫路線**:§2 封三 blocker(每項:機轉→修法→驗收)→ §3 補模式 10→9→4(附完整 DDL;模式 10 先建,因 GATE 長跑與 resume 皆依賴它)→ §4 補七片量測 → §6 分四階段(P0 DDL/P1 blocker/P2 模式10+GATE/P3 模式9、4+量測收尾)。**誠實邊界**:GATE 過閘之前,引擎一切裁決效力維持 **experimental**(master §5.1 G4 裁決權範圍閘),本計畫不預支「已驗證」宣稱。全程本地 qwen/psql、零 Claude usage(#28)。

---

## §1 現況誠實盤點

### 1.1 帳本現況(2026-07-11 DB 實查)

| 表 | 列數 | 關鍵分佈(實查) |
|---|---:|---|
| `deliberation_session` | 28 | 全部 2026-07-10;model 分佈 qwen3:4b×27、qwen3:8b×1 |
| `deliberation_claim` | 127 | confirmed 72 / escalated 43 / refuted 12;`provenance ? 'fast_path'`=16 條、**16/16 全 confirmed**(分佈:db_query 9/pytest 4/file_grep 2/information_schema 1) |
| `deliberation_verdict` | 126 | 無 verdict 之 claim=1(human_claude 直升 escalate 路) |
| `deliberation_escalation` | 43 | reason:undecidable 42、no_oracle 1;**resolved=false 43/43(閉環零運轉)** |
| `deliberation_benchmark` | 54 | 2026-07-10 36 列+2026-07-11 18 列(e2f257a 三重覆);全部手動 CLI run,無 GATE 判定;累計彙總:engine 臂假確認 4b 4/150、8b 0/48;single_shot 4b 22/150、8b 22/48 |
| `deliberation_lens` | 3 | skeptic / complete / doctrine(seed 自 migrate DDL) |
| `deliberation_redline_trigger` | 9 | doctrine_file 5、antileakage_column 4;**全 repo 唯一引用處=migrate_deliberation_ddl.py(零 consult)** |

基準最新證據(e2f257a,2026-07-11,qwen3:4b,三重覆 run):engine 臂 72/72 判對、假確認 0、棄權 0;single_shot 臂 36/72 判對、假確認 6。方向與 20/80 立論一致(增量全來自 oracle 錨定),**但此非 GATE**——無判準快照、無統計檢定、無重複軸控制(§2.2)。

### 1.2 十模式就緒表(逐模式附證據)

| 模式 | 名稱 | 狀態 | 證據(file:line) |
|---|---|---|---|
| 1 | pipeline/fan-out | **部分** | panel 迴圈逐 lens 序列(`engine.py:81-85`);無 task 佇列/LLM×工具雙車道(依賴模式 10) |
| 2 | 對抗驗證三級殺權 | 落地 | `consensus.py:33-43`(oracle 反證單票殺/全 escalate 需人裁/混合標 contested);純意見票未落帳(master §3.3.8 `deliberation_vote` 未建=master P2,本計畫不建,§7) |
| 3 | lens 庫住 DB | 落地 | `lens.py:28-40` 讀 `deliberation_lens`(3 列);lens 版本化欄未有(master P2) |
| 4 | **judge panel** | **未實作** | 無 `synthesize_panel`、無 proposal/panel_score 表 → §3.3 |
| 5 | loop-until-dry | 落地 | `critic.py:23-25` is_dry + `engine.py:78-92` 迴圈;dedup_key=verifier+anchor(`consensus.py:16-18`) |
| 6 | 完整性 critic | 落地(機械層) | `critic.py:28-47` uncovered_tables(information_schema 實查);LLM 殘差 critic 未建(master P2) |
| 7 | 結構化輸出+有界重試 | **扎實** | `ollama.py:70` make_structured_llm_fn;17 pytest(`tests/test_deliberation_engine.py`,--collect-only 實查 17 collected) |
| 8 | 工具實證錨定 | **扎實** | `verifiers.py` 5 oracle;`verify_claim`(`verifiers.py:148-182`)=全系統唯一 confirmed 寫入點;DB CHECK 同錨(`migrate_deliberation_ddl.py:43-60,127-133`) |
| 9 | **自我迭代 DRAFT→ATTACK→REFINE→VERIFY** | **未實作** | 無狀態機、無轉移帳 → §3.2 |
| 10 | **resume-safe 帳本** | **未實作** | 無 `deliberation_run/task` 表、無 idempotency_key、`deliberate.py` CLI 無 `--resume`(:42-83 實查僅 --run/--panel/--report)→ §3.1 |

### 1.3 三 blocker(摘要;封閉設計=§2)

| # | blocker | 一句話機轉 |
|---|---|---|
| B1 | 語意層架空 confirmed 機械鎖 | 機械鎖驗的是 **anchor**,報告印的是 **claim_text**(`ledger.py:63-64`)——兩者對應關係零檢查,✓ [confirmed] 讀者以為 claim 文字被驗證了 |
| B2 | 預註冊 GATE 從未跑 | `benchmark_deliberation.py` 之「習得」判定(:195-211)是事後即興比較,master §5.1 預註冊判準(+15pp/McNemar p<0.05/3 輪/判準快照)零落地 |
| B3 | fast_anchor 注入通道 | `ledger.insert_claim`(:34-37)對**每條** claim 無條件跑 `fast_anchor`,claim 文字即可鑄造 db_query/pytest 錨並覆寫原 verifier 指派(含 human_claude 之 escalate 意圖) |

### 1.4 七片零量測維度

| # | 維度 | 現況實證 |
|---|---|---|
| 1 | 效能(tok/s、VRAM) | `ollama.py:70` 丟棄 Ollama 回應 metadata(全檔零 `eval_count` 引用,grep 實證);無 agent_call 帳 |
| 2 | 可重現(#11) | propose 之 options 無 seed(`engine.py:23-24`:僅 temperature 0/num_predict 1600);引擎自身從未同題多跑取統計 |
| 3 | 長跑 | 無 heartbeat/watchdog;28 session 全單日短跑,連 duration 都無欄可證 |
| 4 | resume | 機制不存在,遑論實測 |
| 5 | 人裁閉環 | `escalation.resolved/resolution` 欄 43/43 全 false、全 repo 零 consumer(grep 僅 migrate DDL) |
| 6 | redline_trigger | 9 列死設定,引擎裁決路徑零 consult(escalation reason CHECK 早預留 `'red_line_category'` 卻 0 列此因) |
| 7 | 跨模一致率 | 27×4b vs 1×8b,同題跨模一致率從未比對 |

(七片封閉設計=§4;此處列現況供 §2/§3 設計對齊。)

### 1.5 所讀既有表 schema(#20a:本節純盤點、不產表;結果落本報告)

現行 7 表 DDL 唯一住所=`scripts/migrate_deliberation_ddl.py:30-137`(冪等、--verify 斷言)。承重約束摘要:

- `deliberation_claim`:status CHECK ∈ (pending,confirmed,refuted,undecidable,escalated);assigned_verifier CHECK ∈ 5 oracle+human_claude+none(pytest 經 :127-133 遷移擴入);anchor 非空 CHECK;provenance jsonb NOT NULL
- `deliberation_verdict`:verdict CHECK ∈ (confirmed,refuted,undecidable);CHECK(verdict='undecidable' OR evidence IS NOT NULL);is_deterministic 預設 true
- `deliberation_escalation`:reason CHECK ∈ (no_oracle,undecidable,red_line_category,verifier_none);resolved/resolution/resolved_at(現零 consumer)
- `deliberation_benchmark`:arm CHECK ∈ (single_shot,engine);逐題 detail jsonb+git_sha(#10)
- `deliberation_lens`:**PK=lens_key text**(:114-120)——注意:master 計畫 §3.3 用 lens_id bigint,本計畫新表 FK 依 live 現實用 lens_key(§3.0 差異 #1)
- `deliberation_session`:status CHECK ∈ (open,adjudicating,escalated,closed);**無 heartbeat 欄**(resume/watchdog 不可承載,故需 §3.1 run/task 表+§4 D3 三欄)

---

## §2 三 blocker 封閉設計

> 落地順序(批判 B3 修訂):**§2.3(fast_anchor 規則化)先於 §2.1(semantic_bound 回填)**——回填的重導出檢查依賴 §2.3 的規則化簽名與 config;§2.2 GATE 依賴 §3.1 run/task(P2)。順序細節=§6。

### 2.1 B1:語意層架空 confirmed 機械鎖 → 語意綁定二級制

**機轉(實碼實證)**:`verify_claim` 只跑 `assigned_verifier(anchor)`(`verifiers.py:148-182`),confirmed 的完整語意=「**這個錨成立**」;但 `ledger.report`(:63-64)印 `✓ [confirmed] {claim_text}`——claim_text 是 LLM 自由文字,錨與文字的對應**從未被任何機械檢查**。極端例:claim_text=「X 資料集無洩漏」+ anchor=`SELECT 1 => == 1` → confirmed 照發。現庫 72 條 confirmed 中,僅 16 條(fast_path)之錨由 claim 文字確定性導出、語意天然綁定;其餘 56 條錨為 LLM 自寫,綁定度未知。

**修法(零 LLM、確定性)**:
1. **導出欄** `semantic_bound`:錨可自 claim_text 機械重導出——判準=`fast_anchor(claim_text, target, RULES_ALL)[:2] == (verifier, anchor)`(正規化後相等;**簽名為 §2.3 統一後之 3-tuple 版,取前兩元比對**〔批判 B1 修訂〕;`RULES_ALL`=全規則開含 L6——導出檢查**只比對、不執行**,無注入面,故與生產預設 L6=off 解耦〔批判 B3 修訂〕)→ true;否則再走 `binding_check` 反抽取(claim_text 內的數字/表名/檔路徑/引號字串,必須逐一出現在 anchor 參數中,缺一即 false)。
2. **報表二級制**:`✓✓ [confirmed·bound]`(claim 文字可直接引用)vs `✓ [confirmed·anchor-only]`(**以 anchor+證據為主體呈現**,claim_text 降格標註「(語意未綁定,僅錨成立)」)。confirmed 的寫入權不變(仍唯 `verify_claim`);本修法不放鬆、只誠實。
3. **回填**:對既有 127 claims 一次性重算 `semantic_bound`(冪等 UPDATE;#12 writer code 修正、非 hand-patch——導出邏輯住 anchors.py,回填 script 只呼叫它;**固定以 `RULES_ALL` 執行、且排程在 §2.3 落地之後**,故 16 條 fast_path〔含 4 條 pytest〕全數可重導出=設計保證,非巧合性通過〔批判 B3 修訂〕)。

**Schema(ALTER,DDL 住所=migrate_deliberation_ddl.py 追加)**:

```sql
ALTER TABLE deliberation_claim
  ADD COLUMN IF NOT EXISTS semantic_bound boolean NOT NULL DEFAULT false;
COMMENT ON COLUMN deliberation_claim.semantic_bound IS
  '錨可自 claim_text 確定性導出/反抽取全命中=true;false 之 confirmed 僅表「錨成立」,報表以 anchor 為主體(B1 封閉)';
```

**程式規畫**:

| 檔 | 動作 | 函式(簽名) | 輸入→輸出 |
|---|---|---|---|
| `src/augur/deliberation/anchors.py` | 增 | `binding_check(claim_text, verifier, anchor, target=None) -> bool` | 純文字比對,零 DB 寫 |
| `src/augur/deliberation/ledger.py` | 改 | `insert_claim` 落 semantic_bound;`report` 二級 icon+anchor-only 主體改印 anchor | 寫/讀 `deliberation_claim` |
| `scripts/backfill_semantic_bound.py` | 新(一次性;#29a `_bootstrap`+指令矩陣) | `--dry-run`(預設)/`--run`;呼叫重導出(RULES_ALL)+binding_check 冪等回填 | 讀寫 `deliberation_claim.semantic_bound` |
| `tests/test_deliberation_engine.py` | 增 | bound 正例(fast_path 樣式)+反例(語意無關錨,如 SELECT 1 錨配洩漏宣稱) | — |

**驗收**:①pytest 全綠(17+新增);②回填後 DB 斷言:16 條 fast_path claims 全 `semantic_bound=true`(RULES_ALL 重導出之設計保證);③anchor-only confirmed 抽 3 條人審對照(報表呈現=anchor 主體);④`ledger.report` 實跑一個歷史 session 目視二級 icon。

### 2.2 B2:預註冊 GATE 從未跑 → GATE-lite 自動化(先凍結、後開跑、事後不得挪門柱)

**機轉(實查)**:`deliberation_benchmark` 54 列全部出自手動 `benchmark_deliberation.py --run`;「習得」判定(:195-211)=當場比較 `fb<fa and acc_b>=acc_a`,判準是 code 常數、無預註冊快照、無統計檢定、無重複軸控制。master §5.1 已裁定預註冊判準唯一 normative——**零落地**。

**修法(GATE-lite,master §5.1 之最小忠實子集;全量七臂三 suite 屬 master P2,不在本補完偷渡)**:

- **臂集**:`single_fast`(think=false)/`single_think`(think=true)/`engine` 三臂(majority_fast/single_union/ast_floor 誠實列為範圍外,§7)。
- **重複軸=題集抽樣 seed,非解碼 seed(批判 A1 修訂,拍板點 P-1)**:兩臂皆維持 `temperature=0`(=生產口徑 `engine.py:24`,GATE 測的臂=生產臂);貪婪解碼下解碼 seed 為 no-op,「3 seed 輪」若解為解碼 seed 將退化為三次重播、統計自我架空。故重複軸重定義為:**每輪以不同題集 seed(41/42/43)驅動 `build_tasks(seed)` 抽樣/構造/排列題庫**,3 輪=3 個不同題集,輪間變異來源=題目抽樣(統計上真實)。GPU 非決定性殘差另以「同輪同題重放一次」落 detail 照實報(不作第三軸)。此為對 master §5.1「3 seed 輪」字面的據實重釋 → §3.0 差異 #3,依 #19 屬判準詮釋、列拍板點。
- **題量(批判 B5 修訂)**:n-per-class=10、三類共 30 題/輪——但 `_QUANT_TABLES` 現僅 8 項(`benchmark_deliberation.py:40-41`)、`build_tasks` 取 `[:n_per_class]`(:65),n=10 時 quant 類只 8 題=28 題/輪。**修法=quant 素材擴至 ≥10**(自 public schema 既有量化表以 information_schema 實查挑 2 追加,P1 過目);fallback(若擴充未拍板):預註冊 n-per-class=8(24 題/輪)。二者擇一**凍結入快照**,不得開跑後改。
- **預註冊判準(開跑前凍結、快照入 batch 表)**:
  1. engine vs **最佳非引擎臂**:3 輪 median case-accuracy 增量 ≥ **+15pp**(master §5.1 預註冊值,不得挪動;拍板點 P-3 建議維持);
  2. engine 假確認 ≤ 各非引擎臂最小值(逐輪與 3 輪彙總皆須);
  3. **McNemar 精確檢定(批判 A3 延伸之檢定力修訂)**:對最佳非引擎臂之成對比較,**以 3 輪合併(90 題)計 p<0.05** 為門檻(`math.comb` 二項尾機率,零新依賴);逐輪 p 照實另報、不作門檻——檢定力計算:30 題/輪下 +15pp≈淨勝 5 題,b=0,c=5 之雙尾精確 p=2·(0.5)⁵=0.0625>0.05,逐輪構造上幾乎不可能過=假嚴格;合併 90 題、淨勝 13、b=0 → p≈2.4e-4,檢定有意義。master §5.1 未指明逐輪/合併,此為具體化非偏離;
  4. **計分口徑預註冊(批判 A3 修訂)**:case-accuracy 分母=**全題**(`n_correct/n_total`;abstain 計錯,分母不縮水——現行 `_print_verdict` 之「正確/已裁決」口徑〔:207〕廢止);abstain rate 另行照實報;McNemar 對子=逐題「判對與否」布林(abstain=判錯,保守方向對 engine 不利,因僅 engine 會棄權)。口徑字串逐項入快照;
  5. **think 臂規格(批判 C1 修訂)**:`num_predict=4096`(思考+答案預算;thinking token 佔額截斷 JSON 為已知實證 `ollama.py:79-80`)、per-call timeout=900s、**逐題 try/except:單題失敗=該題計錯+detail 記 error,臂不整臂死**;規格入快照;
  6. **engine 臂=生產行為(批判 A2 修訂)**:`--gate` 之 engine 臂 fast_anchor **必須讀生產 `deliberation_engine_config` 同一 rules**(§2.3/§5-A),`config_sha` 入快照;`--report-gate` 斷言 benchmark 所用 sha==生產現行 sha,不符=exit 1——杜絕「GATE 驗的引擎≠生產引擎」。
- **先凍結後開跑(機械可驗)**:`--preregister` 先寫 batch 快照列,`--report-gate` 斷言 `preregistered_at < min(run_at)` 且門檻/臂集/口徑**逐項讀自快照非 code 常數**,快照缺失或不一致=exit 1(master E-31 同款)。誠實限制:此機制防「事後在 code 挪門柱」,不防蓄意 UPDATE 快照列(治理層問題,#6+git 審計,非機械閘可及)。
- **承載(批判 C2 修訂)**:GATE 全批 ≈ 每輪 2 單發臂×~30 call+engine 臂 ~30+ propose/裁決 call,3 輪合計 ~180+ LLM calls,GTX 1650 上估**小時級(3-6 hr,think 臂 ~7× 單發,`ollama.py:75-76` docstring 實測比)** → GATE runner 以 §3.1 run/task 帳本承載(每題=一 task,kill-resume 安全)+每 5 分 stdout 進度(#21)+heartbeat(D3)——GATE 自己先滿足「長跑」「resume」兩片量測,過夜跑(#22)。**順序依賴:P2 先落模式 10,才跑 GATE**。

**Schema(新表+ALTER;DDL 住所=migrate_deliberation_ddl.py 追加)**:

```sql
CREATE TABLE IF NOT EXISTS deliberation_bench_batch (
  batch_id         text PRIMARY KEY,            -- 'gate_'+uuid12
  purpose          text NOT NULL CHECK (purpose IN ('gate','adhoc')),
  arm_config       jsonb NOT NULL,              -- 預註冊快照:臂集/門檻/計分口徑/題集 seeds/題量/think 規格/rules config_sha/題庫版本
  preregistered_at timestamptz NOT NULL DEFAULT now(),
  git_sha          text NOT NULL,
  note             text
);
ALTER TABLE deliberation_benchmark
  ADD COLUMN IF NOT EXISTS batch_id text REFERENCES deliberation_bench_batch(batch_id);
ALTER TABLE deliberation_benchmark
  ADD COLUMN IF NOT EXISTS seed int;             -- 題集抽樣 seed(D2 共用;非解碼 seed)
```

**程式規畫**:

| 檔 | 動作 | 函式/內容 | 輸入→輸出 |
|---|---|---|---|
| `scripts/migrate_deliberation_ddl.py` | 改 | bench_batch DDL+benchmark 兩欄+--verify 斷言 | DDL |
| `scripts/benchmark_deliberation.py` | 改 | `build_tasks(seed)` 抽樣化;quant 素材 8→10;`--preregister`(寫快照)/`--gate BATCH_ID`(三臂×3 輪,經 run/task)/`--report-gate BATCH_ID`(讀快照斷言+三判準+McNemar);`mcnemar_exact(b,c)->p`(§5-C);**:121 caller 改 3-tuple 解包+rules 同步讀 config**(批判 B1/A2 修訂) | 寫 `deliberation_bench_batch`/`deliberation_benchmark`;經 `deliberation_run/task` |
| `tests/test_deliberation_engine.py` | 增 | mcnemar_exact 對照已知值(b=0,c=13→p≈2.44e-4;b=c→p=1);快照缺失→report-gate exit 1;計分口徑(abstain 計錯)單元例 | — |

**驗收**:①`--preregister → --gate → --report-gate` 端到端真跑一全批(qwen3:4b,過夜,run/task 承載);②報告輸出三判準逐項 pass/fail+合併 p 值+逐輪 p(照實);③斷言測試:快照缺失/config_sha 不符/preregistered_at≥min(run_at) 三種皆 exit 1;④GATE 結果無論過不過,**照實寫回 A5 追蹤報告——不過=engine 效力維持 experimental,不改門柱重跑**(重跑須新 batch 新預註冊,舊 batch 帳跡永存)。

### 2.3 B3:fast_anchor 注入通道 → 規則化+住 DB config+不覆寫人裁

**機轉(實碼實證)**:`ledger.insert_claim`(:34-37)對每條 claim 無條件跑 `fast_anchor(claim_text, target)`(`anchors.py:58-95`),命中即**覆寫** LLM/人原本的 assigned_verifier+anchor:①claim 文字本身即可鑄造 db_query/pytest 錨=注入通道(惡意/失控文字→任意唯讀 SQL 或任意測試節點執行);②human_claude 指派(escalate 意圖)可被劫持改走機裁;③16/16 fast_path 全 confirmed=通道已實際運轉,現況靠題目良性而非機制安全。

**修法(五件事)**:
1. **規則化+簽名統一(批判 B1 修訂)**:`fast_anchor(claim_text, target, rules) -> (verifier, anchor, rule_id) | None`——每條快路=一條具名規則(rule_id:`L4_db_query`/`L4_information_schema`/`L5_file_grep`/`L6_pytest`),錨**只能由固定樣板+抽取參數構造**(表名經 information_schema 實存驗證、檔路徑經 repo 白名單),**不接受 claim 文字整段 SQL/節點原樣入錨**。全 caller 同步:`ledger.insert_claim`、`benchmark_deliberation.py:121`(`ver, anc = fp` → 3-tuple 解包,否則 ValueError)、`backfill_semantic_bound.py`(§2.1)。
2. **規則開關住 DB(#29b「決定行為的資料住 DB」)**:`deliberation_engine_config` 表(DDL 下);種子列 `fast_anchor_rules = {"L4_db_query":true,"L4_information_schema":true,"L5_file_grep":true,"L6_pytest":false}`——**L6_pytest 預設關**(執行任意測試節點=攻擊面最大)。`config_sha`=正規化 JSON sha256,供 GATE 快照對齊(§2.2 判準 6)。
3. **不覆寫人裁**:assigned_verifier=`human_claude` 之 claim **一律跳過快路**(escalate 意圖不可劫持);其餘指派命中規則才改寫,且 `provenance.fast_path={rule_id, original_verifier, original_anchor}` 全程留痕(audit)。〔草稿原有「assigned_verifier='none' 走快路」條款**刪除**——CLAIM_SCHEMA enum(`anchors.py:25`)不含 none,LLM 產不出,屬空集死碼;批判 B4 修訂。〕
4. **pytest oracle 誠實定位(批判 B4 修訂,拍板點 P-2)**:lens CONTRACT(`lens.py:12-18`)只教 4 oracle 錨式、從未教 pytest → LLM 顯式指派 pytest 之路 de facto 不存在;L6 又預設關。**本計畫誠實宣告:pytest oracle 進入 dormant 狀態**(verifier 本體與 DB CHECK 保留;唯 human 顯式指派或 L6=on 之受控 replay 可達)。「教 CONTRACT+開 L6」與否=單一拍板點 P-2(建議:維持 dormant,待 B1/B3 驗收穩定後再議),不留兩個半開的門。
5. **執行層雙保險**:db_query oracle 之執行面加唯讀護欄(單句 SELECT 樣式閘+read-only transaction)——與鑄錨限制成雙層;此為防禦縱深,不替代規則化。

**Schema(新表;DDL 住所=migrate_deliberation_ddl.py 追加)**:

```sql
CREATE TABLE IF NOT EXISTS deliberation_engine_config (
  config_key text PRIMARY KEY,                  -- 'fast_anchor_rules' 等
  config     jsonb NOT NULL,
  config_sha text NOT NULL,                     -- 正規化 JSON sha256(GATE 快照對齊)
  updated_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO deliberation_engine_config (config_key, config, config_sha) VALUES
  ('fast_anchor_rules',
   '{"L4_db_query":true,"L4_information_schema":true,"L5_file_grep":true,"L6_pytest":false}', '<sha>')
ON CONFLICT (config_key) DO NOTHING;
```

**程式規畫**:

| 檔 | 動作 | 函式(簽名) | 輸入→輸出 |
|---|---|---|---|
| `src/augur/deliberation/anchors.py` | 改 | `fast_anchor(claim_text, target, rules) -> tuple[str,str,str] | None`;樣板化構錨+參數驗證;`RULES_ALL` 常數(僅導出比對用,§2.1) | 純函式 |
| `src/augur/deliberation/engine_config.py` | 新 | `load_rules(cur) -> (dict, sha)`(process cache) | 讀 `deliberation_engine_config` |
| `src/augur/deliberation/ledger.py` | 改 | `insert_claim`:human_claude 跳快路;rules 自 config;provenance.fast_path 留痕 3 欄 | 讀 config、寫 claim |
| `src/augur/deliberation/verifiers.py` | 改 | db_query 執行面唯讀護欄 | — |
| `scripts/benchmark_deliberation.py` | 改 | :121 3-tuple 解包+rules 同步(§2.2 已列) | — |
| `scripts/migrate_deliberation_ddl.py` | 改 | engine_config DDL+種子列 | DDL |
| `tests/test_deliberation_engine.py` | 增 | 注入反例(claim 含惡意 SQL 不鑄錨)/human_claude 不被劫持/L6=off 下 pytest 樣式不走快路/L6=on 受控命中 | — |

**驗收(批判 B2 修訂)**:①pytest 新增全綠;②replay:**12 條 L4/L5 fast_path claims(db_query 9+file_grep 2+information_schema 1)以新碼重放裁決不變;4 條 pytest claims 以顯式 `--rules L6=on` 重放,斷言 rule_id=`L6_pytest` 命中且結果不變**(預設 L6=off 下不命中快路=預期行為、非回歸——原草稿「16 條 replay 結果不變」構造上不可能,已修);③注入實測:構造含 UPDATE/嵌套注入樣式之 claim_text → 斷言不鑄錨、走原指派或 escalate;④human_claude 指派經 insert_claim 後 assigned_verifier 不變(DB 斷言)。

---

## §3 模式補完(10→9→4)

### 3.0 與 master 計畫據實差異表

| # | 項 | master | 本計畫 | 理由 |
|---|---|---|---|---|
| 1 | lens 外鍵 | §3.3 `lens_id bigint` | 新表 FK=`lens_key text` | live PK=lens_key(`migrate_deliberation_ddl.py:114-120`);遷移現實優先 |
| 2 | GATE 臂集 | 七臂三 suite | GATE-lite 三臂 | 其餘=master P2,本補完不偷渡(§7) |
| 3 | 「3 seed 輪」語意 | 未定義 temp=0 下 seed 之義 | 題集抽樣 seed×3 輪;解碼維持 temp=0 生產口徑 | 貪婪解碼下解碼 seed=no-op,原字面統計自我架空(批判 A1);拍板點 P-1 |
| 4 | McNemar 口徑 | 未指明逐輪/合併 | 合併 90 題 p<0.05 為門檻;逐輪 p 照實另報 | 30 題/輪檢定力不足(最小可達 p=0.0625);具體化非偏離 |
| 5 | `deliberation_vote`(模式 2 意見票) | §3.3.8 有 | 不建 | master P2 範圍 |
| 6 | proposal/panel_score 細節 | 僅列名 | 本計畫具體 DDL(§3.2/§3.3) | 補完執行篇職責 |

### 3.1 模式 10:resume-safe run-task 帳本(最先建——GATE 與 D3/D4 皆依賴)

**Schema(新表)**:

```sql
CREATE TABLE IF NOT EXISTS deliberation_run (
  run_id          text PRIMARY KEY,               -- 'dlrun_'+uuid12
  idempotency_key text NOT NULL UNIQUE,           -- 同計畫重送=回同 run(冪等 #6)
  plan            jsonb NOT NULL,                 -- [{topic,target,lens,model,n,seed},...]
  status          text NOT NULL DEFAULT 'running' CHECK (status IN ('running','completed','failed')),
  created_at      timestamptz NOT NULL DEFAULT now(),
  finished_at     timestamptz
);
CREATE TABLE IF NOT EXISTS deliberation_task (
  task_id    bigserial PRIMARY KEY,
  run_id     text NOT NULL REFERENCES deliberation_run(run_id) ON DELETE CASCADE,
  seq        int  NOT NULL,
  payload    jsonb NOT NULL,
  status     text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','done','failed')),
  attempt    int  NOT NULL DEFAULT 0,
  session_id text REFERENCES deliberation_session(session_id),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (run_id, seq)
);
```

**resume 語意**:`--resume RUN_ID` → `done` 跳過;`pending`/`failed(attempt<3)` 續跑;`running`(kill 殘留)→ 重置 pending、attempt+1。單機單工,取工=`status='pending' ORDER BY seq LIMIT 1`。

**程式規畫**:

| 檔 | 動作 | 函式(簽名) | 輸入→輸出 |
|---|---|---|---|
| `src/augur/deliberation/ledger.py` | 增 | `create_run(cur, idempotency_key, plan) -> run_id`(UNIQUE 撞→回既有 run);`next_task(cur, run_id)`;`mark_task(cur, task_id, status, session_id=None)`;`finish_run(cur, run_id)` | 讀寫 run/task |
| `scripts/deliberate.py` | 改 | `--run-plan plan.json` / `--resume RUN_ID` / `--list-runs`(指令矩陣同步 #29d) | 經 ledger CRUD |

**驗收**:D4 kill-resume 真機劇本(§4 D4)+ pytest(subprocess 版)+ 驗收 SQL(attempt≥2 帳跡)。

### 3.2 模式 9:自我迭代 DRAFT→ATTACK→REFINE→VERIFY

**設計**:狀態機逐轉移落帳,**不變式不動**——迭代只改「提案品質」,confirmed 唯一寫點仍=`verify_claim`(`verifiers.py:148`);任何 REFINE 產物要成為 confirmed,一律過 oracle。流程:DRAFT(propose 初稿)→ ATTACK(lens=skeptic 逐點批判,`deliberation_lens` 現有 3 列重用)→ REFINE(修稿,批判逐點回應)→ VERIFY(refined 宣稱送現行裁決管線)。收斂=critic dry(`critic.py:23-25` 重用)或 round 上限 3(凍結參數)。

**Schema(新表)**:

```sql
CREATE TABLE IF NOT EXISTS deliberation_proposal (
  proposal_id bigserial PRIMARY KEY,
  session_id  text NOT NULL REFERENCES deliberation_session(session_id),
  parent_id   bigint REFERENCES deliberation_proposal(proposal_id),   -- 迭代鏈可溯(#10)
  stage       text NOT NULL CHECK (stage IN ('draft','attack','refine','final')),
  round       int  NOT NULL DEFAULT 1,
  content     jsonb NOT NULL,                    -- 提案本文(結構化)
  critique    jsonb,                             -- attack 產物(逐點)
  claim_ids   bigint[],                          -- VERIFY 送裁之宣稱 id
  created_at  timestamptz NOT NULL DEFAULT now()
);
```

**程式規畫**:

| 檔 | 動作 | 函式(簽名) | 輸入→輸出 |
|---|---|---|---|
| `src/augur/deliberation/iterate.py` | 新(領域名詞 #18) | `run_iteration(cur, llm_fn, topic, target, max_rounds=3) -> proposal_id` | 寫 proposal;經 engine/verify_claim 寫 claim/verdict |
| `scripts/deliberate.py` | 改 | `--iterate TOPIC`(可與 --run-plan 組合為 task payload) | — |

**驗收**:①1 真 topic 完整走 4 階段(過夜可,run/task 承載),proposal 鏈 parent_id 可溯至 draft;②迭代期間新 confirmed 全數有對應 verdict 列(SQL 斷言=不繞 oracle);③REFINE 後 false_confirm 不升(對照 ATTACK 前後送裁結果,照實報)。

### 3.3 模式 4:judge panel(soft 排序權、零 confirmed 權)

**設計**:判官(lens×model)只對 proposal **評分/排序**(選擇送 VERIFY 的優先序、或多提案擇優)——**panel 分數絕不產生 confirmed**(#15:多數與人意見皆不造真;hard 裁決唯 oracle)。rubric(評分規準)預註冊入列。**8b 判官=選配**(批判 C3:qwen3:8b Q4≈5GB>4GB VRAM→CPU offload、模型交換分鐘級;預設 4b 判官,8b 判官單獨過夜批)。執行 model-batched:同 run 內先跑完同模型所有評分再換模(載入 ≤2 次/run)。

**Schema(新表)**:

```sql
CREATE TABLE IF NOT EXISTS deliberation_panel_score (
  score_id    bigserial PRIMARY KEY,
  proposal_id bigint NOT NULL REFERENCES deliberation_proposal(proposal_id),
  judge_model text NOT NULL,
  judge_lens  text REFERENCES deliberation_lens(lens_key),   -- live PK=lens_key(§3.0 #1)
  rubric      jsonb NOT NULL,                    -- 預註冊規準快照
  score       numeric NOT NULL,
  rationale   text,
  created_at  timestamptz NOT NULL DEFAULT now()
);
```

**程式規畫**:

| 檔 | 動作 | 函式(簽名) | 輸入→輸出 |
|---|---|---|---|
| `src/augur/deliberation/panel_judge.py` | 新 | `synthesize_panel(cur, llm_fn, proposal_ids, lenses, model) -> list[score_id]` | 讀 proposal/lens、寫 panel_score |
| `scripts/deliberate.py` | 改 | `--judge RUN_ID 或 proposal ids`(model-batched) | — |

**驗收**:①一 panel run:3 judge lens × ≥3 proposal 落分+rationale;②panel 排序 vs oracle 裁決結果之秩相關**照實報、不設門檻**(首輪=量測非考核);③SQL 斷言:panel run 期間 `deliberation_claim.status` 零筆由 panel 路徑寫入 confirmed。

### 3.4 程式規畫總表(#20b 彙總)

| 檔 | 新/改 | 職責 | 讀表 | 寫表 |
|---|---|---|---|---|
| `scripts/migrate_deliberation_ddl.py` | 改 | 全部 DDL 追加(冪等+--verify) | — | 全新表/欄 |
| `src/augur/deliberation/anchors.py` | 改 | fast_anchor 規則化 3-tuple/RULES_ALL/binding_check | — | — |
| `src/augur/deliberation/engine_config.py` | 新 | rules config 讀取+sha | engine_config | — |
| `src/augur/deliberation/ledger.py` | 改 | semantic_bound/快路留痕/run-task CRUD/heartbeat | config,run,task | claim,session,run,task |
| `src/augur/deliberation/verifiers.py` | 改 | db_query 唯讀護欄 | — | verdict,claim(既有) |
| `src/augur/deliberation/iterate.py` | 新 | 模式 9 狀態機 | lens,session | proposal(+經管線 claim/verdict) |
| `src/augur/deliberation/panel_judge.py` | 新 | 模式 4 評分 | proposal,lens | panel_score |
| `src/augur/deliberation/redlines.py` | 新 | D6 consult | redline_trigger | —(經 ledger 改指派) |
| `scripts/deliberate.py` | 改 | --run-plan/--resume/--list-runs/--iterate/--judge | run,task | 經 ledger |
| `scripts/benchmark_deliberation.py` | 改 | 題集 seed/--preregister/--gate/--report-gate/mcnemar/3-tuple caller | bench_batch,config | benchmark,bench_batch |
| `scripts/backfill_semantic_bound.py` | 新 | B1 一次性回填 | claim | claim.semantic_bound |
| `scripts/probe_deliberation_models.py` | 新 | D1 效能 probe | — | model_probe |
| `scripts/compare_deliberation_models.py` | 新 | D7 跨模對比 | session,claim | model_agreement |
| `scripts/resolve_escalation.py` | 新 | D5 人裁 CLI | escalation | escalation 三欄 |
| `scripts/daily_green.py` | 改 | D3 watchdog+D5 積壓警示(重用 #29c) | session,escalation | —(stdout) |
| `src/augur/advisor/ollama.py` | 增 | `chat_with_stats()`(既有 chat 不動) | — | — |
| `tests/test_deliberation_engine.py` | 增 | 各節新測(17→30+) | — | — |

(所有新 script 依 #29:`_bootstrap`、指令矩陣、無參數 graceful、實測。)

---

## §4 七片零量測維度封閉(D1-D7:各給「工具 → 落帳表 → 驗收 SQL」)

> A5 自審裁定七片維度「零量測」。本節逐片封閉。共同原則:**量測=落帳**(#9 三來源;不落帳=未量測)、全程本地 qwen/psql **零 Claude token**(#28)、量測不鬆三敵零容忍(#27 凌駕邊界)。
>
> **現況實證錨(2026-07-11 本機 DB 複查)**:session 28(4b 27/8b 1)、claim 127(confirmed 72/escalated 43/refuted 12)、verdict 126、escalation 43(undecidable 42/no_oracle 1;resolved 43/43 全 false)、benchmark 54(engine 臂假確認 4b 4/150、8b 0/48;single_shot 4b 22/150、8b 22/48)、lens 3、redline_trigger 9。`to_regclass('deliberation_run'/'task'/'proposal'/'panel_score')` 四者皆 NULL。

### D1 效能(tok/s / VRAM 零落帳)

- **缺口實證**:`ollama.py` 對 `eval_count`/`eval_duration`/`load_duration` 全 repo grep 零命中(回應統計被丟棄);session/benchmark 無速度/記憶體欄。
- **工具**:`scripts/probe_deliberation_models.py`(新)+ `ollama.chat_with_stats()`(§5-B)。標準題庫=3 類固定 prompt(propose 契約/錨轉換/純結構化 JSON)× {qwen3:4b, qwen3:8b} × 3 重複(#11)。VRAM 以 `nvidia-smi --query-gpu=memory.used` 實測;WSL2 下不可得 → 落 `NULL`+`note='nvidia-smi unavailable'`(**誠實缺測,不估算** #9)。8b 於 4GB VRAM 下 CPU offload——tok/s 慢=事實,照實落帳(批判 C3);probe 執行 model-batched(先 4b 全部、後 8b 全部,載入 2 次)。
- **落帳表 DDL(新)**:

```sql
CREATE TABLE IF NOT EXISTS deliberation_model_probe (
  probe_id          bigserial PRIMARY KEY,
  run_at            timestamptz NOT NULL DEFAULT now(),
  model_tag         text NOT NULL,
  task_kind         text NOT NULL CHECK (task_kind IN ('propose','anchor','structured_json')),
  prompt_chars      int  NOT NULL,
  prompt_eval_count int, eval_count int,          -- Ollama 終包實回;無則 NULL
  load_ms bigint, prompt_eval_ms bigint, eval_ms bigint, total_ms bigint NOT NULL,
  tok_per_s         numeric,                      -- eval_count/eval_ms 換算;NULL=未回,不補值
  gpu_mem_used_mb   int,                          -- nvidia-smi 實測;不可得=NULL+note
  note              text,
  git_sha           text NOT NULL
);
```

- **驗收 SQL**:

```sql
SELECT count(*) FROM deliberation_model_probe
WHERE model_tag IN ('qwen3:4b','qwen3:8b') AND tok_per_s IS NOT NULL;   -- 目標 >= 18(2 模 x 3 類 x 3 重複)
```

### D2 可重現(#11)——依批判 A1 重定義量測軸

- **缺口實證**:`engine.py:23-24` propose options 僅 temperature 0/num_predict 1600;`grep seed` 於 deliberation 模組+兩支 CLI 零命中(唯 `lens.py:7` DDL 種子註解)。
- **誠實前提(批判 A1)**:現行引擎=temperature 0 貪婪解碼,**解碼 seed 為 no-op**——「加 seed 多跑」不構成統計重複。可重現量測軸重定義為兩件真事:
  1. **殘差重放**:同 config×同題集×3 次重放之 min/median/max(量測 GPU/量化非決定性殘差;以統計為準、不宣稱 bitwise);
  2. **題集軸**:GATE 之 3 題集 seed 輪(§2.2,seed 欄共用)。
- **工具**:`engine.propose(..., seed=None)` 增參數並落 `claim.provenance`(誠實註記:temp=0 下無作用;為未來 temp>0 模式預留+帳面可溯);`benchmark_deliberation.py --replicates 3`(重放)。
- **落帳 DDL(改)**:`deliberation_benchmark.seed`(§2.2 已列;此處=題集 seed)。
- **驗收 SQL**:

```sql
SELECT count(DISTINCT seed) FROM deliberation_benchmark
WHERE batch_id IS NOT NULL AND seed IS NOT NULL;                         -- >= 3(GATE 三題集輪)
```
加:殘差重放 3 次之逐題一致率落 benchmark.detail,照實報。

### D3 長跑(heartbeat/duration 無欄可證)

- **缺口實證**:`deliberation_session` DDL 僅 created_at(`migrate_deliberation_ddl.py:31-42`);`engine.py:53` elapsed 只印 stdout。
- **工具**:session 加三欄(下);`engine.deliberate` 每 claim 裁決後 `ledger.heartbeat(cur, sid)`、收尾寫 finished_at/duration_s;panel/GATE 同。watchdog 掛既有 `scripts/daily_green.py`(#29c 重用):open session heartbeat 落後 >15 分 → 警示(#21/#22)。
- **落帳 DDL(改)**:

```sql
ALTER TABLE deliberation_session ADD COLUMN IF NOT EXISTS heartbeat_at timestamptz;
ALTER TABLE deliberation_session ADD COLUMN IF NOT EXISTS finished_at  timestamptz;
ALTER TABLE deliberation_session ADD COLUMN IF NOT EXISTS duration_s   numeric;
```

- **驗收 SQL**:

```sql
SELECT count(*) FROM deliberation_session WHERE duration_s >= 1800;      -- >= 1(P2 GATE 過夜長跑實證)
SELECT count(*) FROM deliberation_session
WHERE status='open' AND heartbeat_at < now() - interval '1 hour';        -- = 0(無殭屍 session)
```

### D4 resume 實測(模式 10 帳本 + kill-resume 真機劇本)

- **缺口實證**:四張帳表 to_regclass 全 NULL;全 repo 無 idempotency_key;deliberate.py 無 --resume。
- **機制**:=§3.1(DDL/CRUD/CLI 皆在該節,不重複)。
- **實測劇本(非紙上,P3 執行)**:`--run-plan`(6 tasks)→ 於 task 3 執行中 `kill -9` → `--resume RUN_ID` → 斷言:done task 不重跑(session 總數不增)、被殺 task attempt=2 重裁、run 收斂 completed。劇本同時入 pytest(subprocess 版)+手跑一次落真帳。
- **驗收 SQL**:

```sql
SELECT count(*) FROM deliberation_run r
WHERE r.status='completed'
  AND EXISTS (SELECT 1 FROM deliberation_task t
              WHERE t.run_id=r.run_id AND t.attempt >= 2);               -- >= 1(真 kill-resume 帳跡)
```

### D5 人裁閉環(escalation.resolved 零 consumer → 真讀者 + 真人裁帳)

- **缺口實證**:resolved 43/43 全 false;`grep resolved` 於 src/scripts 僅命中 migrate DDL(:83,85,89)=零程式讀者。
- **工具**:`scripts/resolve_escalation.py`(新):`--list`(讀 resolved=false 佇列=第一個真 consumer)/`--resolve ID --outcome {human_confirmed,human_refuted,wont_fix} --resolution TEXT`。第二 consumer=`daily_green.py` 審議段(積壓超閾警示)。
- **機械鎖不鬆(關鍵)**:人裁**只寫 escalation 三欄**,**絕不**把 claim.status 改 confirmed——confirmed 唯一寫點仍=verify_claim;人若認定為真,正道=補可機驗 anchor 重新裁決,而非人手升格(#15 多數與人意見皆不造真)。
- **落帳**:既有欄,零 DDL。
- **驗收 SQL**:

```sql
SELECT count(*) FROM deliberation_escalation
WHERE resolved AND resolution IS NOT NULL AND resolved_at IS NOT NULL;   -- >= 10(對現積壓 43 實裁一輪;拍板點 P-5)
```

### D6 redline consult(9 列死設定 → 掛上強制升級通道)

- **缺口實證**:`grep redline` 全 repo 僅命中 migrate DDL;escalation reason CHECK 早預留 `'red_line_category'`(:81)但 43 列中 0 列此因=通道從未接電。9 列(DB 實查)=4 antileakage_column(TaiwanStockDividend.AnnouncementDate/AnnouncementTime、TaiwanStockMonthRevenue.create_time、TaiwanStockShareholding.RecentlyDeclareDate)+5 doctrine_file(四治權檔+README)。
- **工具**:`src/augur/deliberation/redlines.py`(新,§5-E):`consult(claim_text, anchor, verifier)` 讀 redline_trigger(process cache);`ledger.insert_claim` 於正規化後 consult——命中 antileakage_column(claim_text/anchor 含觸線欄)或 doctrine_file(file_grep 路徑 LIKE 觸線檔)→ assigned_verifier 強制改 `'human_claude'`+`provenance.redline={kind,pattern}`;`verify_claim` 讀到 provenance.redline → escalation `reason='red_line_category'`。consult 順序在快路之前(redline 命中=快路豁免不了)。
- **語意**:治權檔/anti-leakage 欄相關宣稱**不得由弱模型+oracle 逕行機裁**——治權判準人拍板(#19/#26),oracle 證據可附 payload 供人參考。
- **落帳**:既有表(9 列設定+escalation 通道),零新表。
- **驗收 SQL + pytest**:

```sql
SELECT count(*) FROM deliberation_escalation WHERE reason='red_line_category';  -- >= 1
```
pytest:注入含 `TaiwanStockDividend.AnnouncementDate` 之 claim → 斷言 status='escalated' 且 reason='red_line_category'。

### D7 跨模一致率(4b vs 8b 從未同題對比)

- **缺口實證**:session 4b 27/8b 1;benchmark 兩模各自彙總(前言錨)但無同題 session 級對齊。
- **工具**:`scripts/compare_deliberation_models.py`(新):同 topic+lens+題集 seed 各跑 4b/8b 一 session → 以 `consensus.dedup_key`(verifier+正規化 anchor,`consensus.py:16-18`)對齊 → 三個誠實指標:(i)檢查集合重疊 Jaccard(兩模「想驗什麼」像不像);(ii)交集 key 之 status 一致率(同錨同 oracle 恆同=此值偏高屬預期,照實報不當成績);(iii)escalate 率差(弱模湊不出合約錨的頻率差)。**執行預算(批判 C3)**:model-batched——先跑完全部 topic 之 4b session、再一次載 8b 跑完(單 run 模型載入 ≤2 次);排 P3 過夜。
- **落帳表 DDL(新)**:

```sql
CREATE TABLE IF NOT EXISTS deliberation_model_agreement (
  agree_id    bigserial PRIMARY KEY,
  run_at      timestamptz NOT NULL DEFAULT now(),
  topic       text NOT NULL,
  seed        int,
  model_a     text NOT NULL, model_b text NOT NULL,
  session_a   text REFERENCES deliberation_session(session_id),
  session_b   text REFERENCES deliberation_session(session_id),
  n_a int NOT NULL, n_b int NOT NULL, n_common int NOT NULL,
  jaccard     numeric NOT NULL,
  n_agree     int NOT NULL,               -- 交集中 status 一致數
  escalate_rate_a numeric, escalate_rate_b numeric,
  detail      jsonb NOT NULL,             -- 逐 key 對照,可重現(#10)
  git_sha     text NOT NULL
);
```

- **驗收 SQL**:

```sql
SELECT count(DISTINCT topic) FROM deliberation_model_agreement WHERE n_common >= 0;  -- >= 5(5 題同題對比)
```

---

## §5 共用元件

| 元件 | 住所 | 內容 | 消費者 |
|---|---|---|---|
| **5-A** rules config 讀取 | `src/augur/deliberation/engine_config.py`(新) | `load_rules(cur) -> (dict, sha)`;process cache;`RULES_ALL` 常數住 anchors.py(僅導出比對) | ledger.insert_claim/benchmark --gate/backfill(§2.1/§2.2/§2.3) |
| **5-B** `chat_with_stats()` | `src/augur/advisor/ollama.py`(增) | 新函式回 `(text, stats)`(prompt_eval_count/eval_count/各 duration);**既有 `chat()` 簽名不動=零回歸** | D1 probe;(選配)session 級速率落帳 |
| **5-C** `mcnemar_exact(b, c) -> p` | `scripts/benchmark_deliberation.py` 內函式 | 雙尾精確二項(math.comb,零新依賴);pytest 對照已知值(b=0,c=13→p≈2.44e-4;b=c→p=1.0) | --report-gate(§2.2) |
| **5-D** run-task CRUD | `src/augur/deliberation/ledger.py`(增) | create_run/next_task/mark_task/finish_run(§3.1) | deliberate.py/GATE runner/iterate |
| **5-E** redline consult | `src/augur/deliberation/redlines.py`(新) | `consult(claim_text, anchor, verifier)`;cache;順序先於快路 | ledger.insert_claim(D6) |

---

## §6 分階段執行、時間/硬體預算與驗收總表

### 6.1 階段(#19 一段一段過目;每階段末=用戶檢視點)

| 階段 | 內容 | 前置 | 估時 | 驗收 |
|---|---|---|---|---|
| **P0** DDL 一次到位 | migrate_deliberation_ddl.py 追加全部新表/欄(engine_config/semantic_bound/bench_batch+benchmark 兩欄/session 三欄/run/task/proposal/panel_score/model_probe/model_agreement)+--verify 斷言;**避開任何 pg_dump 時段(#30 dump 期間禁 DDL)** | — | 0.5 天 | --verify 全綠;to_regclass 全非 NULL |
| **P1** 封 blocker | **§2.3 → §2.1**(順序=批判 B3)→ 回填 → replay/注入驗收 | P0 | 1 天 | §2.1/§2.3 驗收全項;pytest 17→25+ 全綠 |
| **P2** 模式 10+GATE | §3.1 run/task → D3 heartbeat → §2.2 `--preregister → --gate`(**過夜,#21/#22,run/task 承載**)→ `--report-gate` | P1 | 1-2 天(含過夜) | §3.1/§2.2 驗收;D3 兩 SQL;GATE 結果照實入 A5 追蹤報告 |
| **P3** 模式 9/4+量測收尾 | §3.2 → §3.3 → D1/D5/D6/D7 → D4 kill-resume 真機 → 收尾:A5 七片複量報告 | P2 | 2-3 天 | 各節驗收 SQL 全過;七片逐片有帳 |

### 6.2 時間/硬體預算(GTX 1650 4GB;批判 C1/C2/C3 落點)

| 項 | 估計 | 依據 |
|---|---|---|
| GATE 全批(3 輪×3 臂,~180+ LLM calls) | 3-6 hr → **過夜** | think 臂 ~7× 單發(`ollama.py:75-76` docstring 實測比);run/task 承載 kill-resume 安全 |
| single_think 單題 | num_predict 4096/timeout 900s;失敗=單題計錯不整臂死 | §2.2 判準 5 |
| 8b 相關(D1/D7/panel 8b 判官選配) | CPU offload,模型載入分鐘級;model-batched ≤2 次載入/run | 批判 C3 |
| kill-resume 劇本 | <30 min | D4 |
| Claude usage | **0**(全程本地 qwen+psql;#28) | — |

### 6.3 治權對齊清單

#9/#10(所有量測落帳可溯+git_sha)、#11(重放/多輪統計)、#12(回填走 writer 邏輯非 hand-patch)、#15(人裁/panel 不造真)、#19(逐段過目)、#28(零 Claude usage)、#29(新 script 四件事)、#30(DDL 避 dump)。

---

## §7 誠實邊界、不做清單與拍板點

**效力邊界**:GATE 過閘前,引擎一切裁決效力=**experimental**(master §5.1 G4);GATE 過閘後之效力升級仍屬決策層=用戶拍板(#26),本計畫不預支。GATE 不過=照實記錄、engine 維持 experimental、**不改門柱重跑**(重跑須新 batch 新預註冊)。

**不做清單(master P2,誠實列出不偷渡)**:majority_fast/single_union/ast_floor 臂、benchmark 三 suite 全量、`deliberation_vote` 意見票表、LLM 殘差 critic、lens 版本化欄。

**量測不鬆三敵(#27 凌駕邊界)**:效能/重現/長跑量測全部只作用 operational 層;假資料/偷看未來/自我欺騙零容忍不因任何量測便利而鬆動。

**拍板點(執行前用戶裁)**:

| # | 拍板點 | 建議 |
|---|---|---|
| P-1 | GATE 重複軸:題集 seed×3 輪(解碼維持 temp=0 生產口徑) vs 改 temp>0 配解碼 seed(臂≠生產臂) | **題集 seed**(GATE 測的=生產跑的;§2.2/§3.0 #3) |
| P-2 | pytest oracle 去留:dormant(human/受控 replay 可達,L6 預設關) vs 教 CONTRACT+開 L6 | **dormant**(攻擊面最小;B1/B3 穩定後再議) |
| P-3 | GATE 門檻 +15pp | **不動**(master 預註冊值) |
| P-4 | panel 8b 判官 | **選配**(預設 4b;8b 單獨過夜批) |
| P-5 | D5 對 43 積壓實裁一輪(人時投入,驗收 ≥10) | 首輪裁 10+,餘由 daily_green 警示驅動 |

---

## 附錄 A 批判修訂對照表(對抗批判 12 項 → 定稿落點)

| 批判 | 缺陷一句話 | 定稿落點 |
|---|---|---|
| A1 | temp=0 下「3 seed 輪」統計自我架空(seed=no-op) | §2.2 重複軸改題集抽樣 seed;§3.0 差異 #3;D2 重定義;拍板點 P-1 |
| A2 | GATE engine 臂可能測不到生產行為(rules 分裂) | §2.2 判準 6:--gate 讀生產 config、config_sha 入快照、report-gate 斷言相符 |
| A3 | 棄權計分口徑未預註冊(分母可挪 ±10pp 級) | §2.2 判準 4:全題分母/abstain=錯/McNemar 對子口徑,逐項凍結入快照 |
| B1 | fast_anchor 簽名 3-tuple 漏 caller+計畫內自相矛盾 | §2.3 修法 1 統一 3-tuple+全 caller 清單(含 benchmark:121);§2.1 判準改 `[:2]` 比對 |
| B2 | §2.3 驗收「16 條 replay 不變」構造上必紅(4 條 L6) | §2.3 驗收②:12 條 L4/L5 不變+4 條 pytest 以 --rules L6=on 顯式重放 |
| B3 | 回填 rules 狀態未指定、與 §2.3 落地順序耦合未定 | §2.1 修法 3:固定 RULES_ALL+§6 P1 順序(2.3→2.1);16/16=設計保證 |
| B4 | pytest oracle 殭屍未明說+'none' 快路屬空集 | §2.3 修法 4:dormant 誠實宣告、併單一拍板點 P-2;'none' 條款刪除 |
| B5 | n-per-class=10 與 _QUANT_TABLES 8 項不符(28≠30) | §2.2 題量:quant 素材 8→10 擴充(P1 過目)或預註冊 fallback n=8,凍結入快照 |
| C1 | single_think 臂截斷/逾時無 spec、單題失敗殺整臂 | §2.2 判準 5:num_predict 4096/timeout 900s/逐題 try-except 計錯;入快照 |
| C2 | GATE 全批小時級、長跑/watchdog 自己先違反 | §2.2 承載:run/task 帳本+#21 進度+D3 heartbeat;P2 順序=先模式 10 後 GATE |
| C3 | 8b 不入 4GB VRAM、反覆交換分鐘級未預算 | §3.3/D1/D7 model-batched(≤2 次載入/run)+§6.2 預算表+8b 判官降選配(P-4) |
| (統計補強) | 逐輪 McNemar 30 題檢定力不足(最小 p=0.0625) | §2.2 判準 3:合併 90 題為門檻、逐輪 p 照實另報;§3.0 差異 #4 |

---

*本計畫=master 計畫之補完執行篇;過閘前不預支「已驗證」,過閘後效力升級由用戶拍板。全程本地執行、零 Claude usage、量測即落帳。*
# 本地審議編排器計畫 v2(deliberation orchestrator — 本地事實整備 + 分流,非審查替代)

**日期**:2026-07-09 ｜ **版本**:v2(經 6-agent 對抗審查、35 findings/9 high 修正後定稿)｜ **性質**:plan-first(#20 高風險門檻,拍板後才實作)
**動因**:用戶問「能否最小化 Claude token+多用本地 AI 做規劃、讓本地 AI 習得 ultracode 對抗審查」→ 6-agent 對抗審查誠實裁決(§1)→ 用戶請把可行的那塊寫成計畫書評估「**值不值得建**」。
**守**:#8(隔離命門、擴 import_isolation 之 AST + 字串雙面)· #12(複用既有機械閘、零雙軌)· #15(誠實標破口)· #20/#26(決策層人拍板)· #28(執行vs理解二分)· #29b(決定行為的資料住 DB)· 靈魂(弱 LLM 不可信、系統建議人決策)。

> **v2 修了什麼(對抗審查留痕)**:H1 修正「可用 oracle 只有 4 個、非 6 個」· H2 修正 import 邊界假宣稱 · H3 補 `deliberation_*` 字串 SQL 掃描(#8 第二半)· H4 補 FK CASCADE · H5 red-line 觸發資料改住 DB(#29b)· H6 把「qwen 不當 judge」升成機械鎖 · M1-M6 硬化 DDL/去矛盾/誠實下修 · L1-L7 措辭精確化。發現表 SSOT=本輪 workflow journal。

---

## 0. 三十秒 + 最重要的誠實一級結論(先講,免得被當賣點)

**這計畫在回答一個決策:「這系統值不值得建?」——不是「怎麼把它建到最好」。**

1. **有意義規模的省 Claude token 不可得。** 安全的確定性類(帶錨 claim → 本地派機械 oracle → CONFIRMED)**確有一小塊**可省 Claude「調度+讀結果」的 token;**但量級小、且因覆蓋不可靠(§8)部分回吐**。能被本地安全處理的與最危險的語意判斷**高度綁定**——真正想省的那批(判讀核)恰是不可下放的那批。
2. **本地 AI 學不到 ultracode 的價值核心。** ultracode 威力來自 **B(每 agent 推理品質)**、不是 **A(編排結構)**。**qwen 當 judge 時品質乘零**;當 proposer/覆蓋放大器則有**有界價值**(受 §8a 漏提上限約束)。同底模五視角錯誤相關 → 退化成「自信地一致錯」、替爛計畫蓋假背書(比不審更危險)。
3. **augur 自己早已下此結論(非臆測)。** `advise.py:20-24` 連「別亂編股名」4 輪 prompt 都壓不住 qwen 漂移 → 最終**把生成職責整個拿掉**改確定性注入;蒸餾 `advisor_distill_teacher.py:8`「Claude 只教 **behavior**、**不供事實**」——**augur 對『讓 qwen 做難判斷』的答案就是 NO**。
4. **能建、值得建的,是「本地確定性事實整備器 + 提案分流器」,不是「審查者」。** 真實效益是 **wall-clock**(本地把事實錨好、平行 surface 覆蓋餵 Claude),**不是省 token**;且帶四個原理上不可全閉的破口(§8)。**當它被當『本地 ultracode 審查替代』用,就在最需要判讀的地方失效。**

> **一句話**:值得建的是「幫 Claude 把事實準備好的本地跑腿」,不是「取代 Claude 判斷的本地審查官」。**對你真正想要的「本地 AI 在環路、習得 ultracode 判讀」——答案基本是不建**(§10)。本計畫只設計前者。

---

## 1. 為何有這計畫:6-agent 對抗審查的誠實裁決(SSOT)

- **Q1(最小化 token+多用本地 AI)**:只能到「確定性事實抓取肢+樣板肢」,判讀核不可下放 → **「所有規劃最小化 token」= 否**。
- **Q2(習得 ultracode 對抗審查)**:編排骨架可移植、**區辨性核心不可移植** → **否**。
- **紅線(#28 保留區,搞錯沉默污染下游、成本不對稱)**:①anti-leakage 時點欄語意(#8)②真兆/假兆判讀(#15)③治權判準變更/跨檔一致(#19/#26)。
- **guard 為何擋不住**:`guard(response,payload,citations)` @`guard.py:45` **綁 advisor `PredictionPayload`**、只驗 advisor 輸出、**無法驗任意計畫 claim**;且五閘實為 **3 閘 vs ground truth 比對 + 2 閘 banned-pattern regex**(future-leak/reverse)——審查計畫**沒有外部真兆 oracle**、判斷即產出。

---

## 2. 治權框定(全守、無判準變更)

- **#8 隔離命門(雙面)**:(a) 新 package `augur.deliberation` 加入 import_isolation **`FORBIDDEN`**(AST import 方向:預測管線 7 package 絕不 import 審議層);(b) `deliberation_*` 表為 qwen 生成之**非真兆表**,與 `advisor_distill_*` 界線同構 → 加入**字串 SQL 掃描 `DELIB_LITERALS`**(防 pipeline 用 raw SQL `SELECT ... FROM deliberation_claim` 把 qwen 文字拉進真兆庫,AST 稽核看不到 raw SQL,故需第二面)。
- **#28 執行vs理解**:審議層只做**執行/整備層**(枚舉真兆、派確定性 verifier、路由);**判讀層(無 oracle 的語意/判準/真兆)一律 escalate 給 Claude**,不下放。
- **靈魂 / qwen 不當 judge(機械鎖 §6.4)**:qwen 只准提「帶錨點 + 指定確定性 verifier」的結構化 claim、**只能寫 `status='pending'`**;`status='confirmed'` **僅 adjudication 可寫、且須有對應 `is_deterministic=true` 的 confirmed verdict**,由稽核不變式強制(#8 風格 exit 1)。
- **三敵零容忍**:qwen 提案非真兆來源(#1);審議不觸市場資料/不改 as-of(FREEZE);不因省 token 鬆動紅線(#15)。

---

## 3. 架構:A(可移植編排)+ B(不可移植判讀)分解 → 混合設計

| 層 | 誰做 | 為何 |
|---|---|---|
| **本地 fan-out 提案**(A) | qwen3:8b 多視角 | 覆蓋放大(強迫掃各子系統),**只准提帶錨結構化 claim、只寫 pending、不做自由推理** |
| **確定性裁決**(機械) | **4 個真可用 oracle**(§6.2) | `information_schema`/`import_isolation`/`file_grep`/`db_query`——**有 oracle 即機械證偽,零 LLM** |
| **真兆錨定覆蓋** | 枚舉器(information_schema/檔案樹) | completeness **錨在真兆全集、絕不接受模型列的清單**;只達**結構**完整(語意不可枚舉、誠實標) |
| **無 oracle 判讀**(B) | **Claude 理解層閘** | anti-leakage 時點/真兆假兆/IC 顯著性/治權判準/跨檔一致——**升級、不下放**;payload 最小化、人拍板 |

**核心不變式**:qwen 輸出**永遠是「待驗提案(pending)」、永遠不是「裁決」**;每 claim 出生綁一 `assigned_verifier`,無錨/無 verifier = 拒收;紅線類別 + undecidable + verifier∈{human_claude,none} **一律強制 escalate(不靠 qwen 自覺)**。

---

## 4. 元件圖 + 資料流

```
草稿/主題 ─▶ [perspective] qwen 多視角 fan-out ─▶ 結構化 claim(anchor+category+assigned_verifier, status=pending)
                                                        │ 無錨/無 verifier → 拒收(不落列)
                                                        ▼
                          [claim] deliberation_claim ──▶ [adjudication] 依 assigned_verifier 派確定性 oracle(唯一 status writer)
                                                        │        ├─ information_schema(欄/型別存在;core.schema)
                                                        │        ├─ import_isolation(#8 AST 閘;subprocess)
                                                        │        ├─ file_grep(檔/行/字串存在;subprocess)
                                                        │        └─ db_query(唯讀內部 SQL 斷言;core.db、非 API reconcile)
                          ▼
              [verdict] deliberation_verdict(append-only, is_deterministic)
                          │
      confirmed(且有 det. verdict)─▶ 入計畫清單
      refuted   ─▶ 丟棄
      undecidable / 紅線類別(硬觸發 §6.3)/ verifier∈{human_claude,none}
                          ▼
              [escalation] deliberation_escalation ──▶ Claude 理解層閘(最小 payload、人拍板)──▶ resolution 回寫
                          
              [coverage] 真兆枚舉(information_schema/檔案樹)──▶ deliberation_session.coverage(結構完整度 + 誠實標語意不可枚舉)
              [redline]  deliberation_redline_trigger(doctrine 檔/anti-leakage 欄)──▶ escalation 硬觸發來源(§6.3)
```

---

## 5. table schema(v1.39.0 (a);**5 新表**;權威=DB information_schema #2;慣例對齊 knowledge_*/revalidation_ledger)

```sql
-- 5.1 一次審議 session(topic + 覆蓋摘要 + 本地模型可溯源)
CREATE TABLE IF NOT EXISTS deliberation_session (
    session_id  text PRIMARY KEY,                       -- 'delib_20260709_shorthorizon'
    topic       text NOT NULL,
    draft_path  text,
    as_of       date,                                   -- 涉市場資料綁 FREEZE as-of(否則 NULL)
    status      text NOT NULL DEFAULT 'open'
                CHECK (status IN ('open','adjudicating','escalated','closed')),
    coverage    jsonb NOT NULL DEFAULT '{}'::jsonb,      -- {dim:{enumerated_total,covered,source_of_truth,enumerable,structural_only}}; dim∈{tables,columns,files}
    model_tag   text,                                   -- 本地 LLM tag(qwen3:8b)+ 版本(#1 可溯源)
    created_at  timestamptz NOT NULL DEFAULT now()
);

-- 5.2 qwen 提的結構化 claim(強制錨點 + 指定 verifier;無錨/無 verifier 應用層拒收不落列)
CREATE TABLE IF NOT EXISTS deliberation_claim (
    claim_id    bigserial PRIMARY KEY,
    session_id  text NOT NULL REFERENCES deliberation_session(session_id) ON DELETE CASCADE,
    perspective text NOT NULL,
    category    text NOT NULL                           -- qwen 自標(破口 a);紅線類別另有硬觸發覆蓋(§6.3)
                CHECK (category IN ('schema','program','isolation','doctrine',
                                    'antileakage','truesign','coverage','other')),
    claim_text  text NOT NULL,
    anchor      text NOT NULL CHECK (btrim(anchor) <> ''),   -- file:line / table.column(空字串亦擋、DB 機械閘)
    assigned_verifier text NOT NULL                     -- 只列真可用集(H1 修正:移除 guard/effective_t_hac/sql_reconcile)
                CHECK (assigned_verifier IN ('information_schema','import_isolation','file_grep',
                                             'db_query','human_claude','none')),
    status      text NOT NULL DEFAULT 'pending'         -- perspective.py 只寫 pending;confirmed 僅 adjudication(§6.4 鎖)
                CHECK (status IN ('pending','confirmed','refuted','undecidable','escalated')),
    provenance  jsonb NOT NULL,                          -- raw LLM 輸出 + prompt hash(#1 命門、無 DEFAULT:漏給即 loud fail)
    created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_delib_claim_session ON deliberation_claim(session_id, status);

-- 5.3 確定性裁決 audit(append-only;採 bigserial 代理鍵便逐次留痕+索引,非比照 ledger keyless)
CREATE TABLE IF NOT EXISTS deliberation_verdict (
    verdict_id  bigserial PRIMARY KEY,
    claim_id    bigint NOT NULL REFERENCES deliberation_claim(claim_id) ON DELETE CASCADE,
    verifier    text NOT NULL,
    verdict     text NOT NULL CHECK (verdict IN ('confirmed','refuted','undecidable')),
    evidence    text CHECK (verdict = 'undecidable' OR evidence IS NOT NULL),  -- 確定性裁決強制附機械證據(#10)
    is_deterministic boolean NOT NULL DEFAULT true,      -- false=需 Claude 判讀(→ 應走 escalation)
    ran_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_delib_verdict_claim ON deliberation_verdict(claim_id, ran_at);

-- 5.4 Claude 理解層升級佇列(無 oracle 判讀;最小 payload、人拍板回寫)
CREATE TABLE IF NOT EXISTS deliberation_escalation (
    escalation_id bigserial PRIMARY KEY,
    claim_id    bigint NOT NULL REFERENCES deliberation_claim(claim_id) ON DELETE CASCADE,
    reason      text NOT NULL
                CHECK (reason IN ('no_oracle','undecidable','red_line_category','verifier_none')),
    payload     jsonb NOT NULL,                         -- 固定鍵:{question,anchor,category,verdict_evidence,draft_excerpt}
    resolved    boolean NOT NULL DEFAULT false,
    resolution  text,
    resolved_at timestamptz,
    created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_delib_esc_open ON deliberation_escalation(resolved, created_at);

-- 5.5 red-line 觸發資料(H5:#29b「決定行為、會增減、可策展」之 config → 住 DB、非 hardcode)
CREATE TABLE IF NOT EXISTS deliberation_redline_trigger (
    trigger_id  bigserial PRIMARY KEY,
    kind        text NOT NULL CHECK (kind IN ('doctrine_file','antileakage_column')),
    pattern     text NOT NULL,                          -- 檔路徑 glob / table.column 名
    source      text NOT NULL,                          -- 權威來源('column_catalog.anti_leakage' / '治權檔清單')
    note        text,
    created_at  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (kind, pattern)
);
-- 冪等種子(#29b bootstrap、SSOT 是 DB 表):doctrine_file ← 5 治權檔路徑;
--   antileakage_column ← column_catalog 之 anti-leakage 欄(Dividend.AnnouncementDate/MonthRevenue.create_time/
--   Shareholding.RecentlyDeclareDate…);ON CONFLICT (kind,pattern) DO NOTHING。
```

**冪等/遷移**:專屬 `scripts/migrate_deliberation_ddl.py`(含 `--check`,對齊 `migrate_advisor_distill_ddl.py` 慣例=DDL 單一住所);重跑同 session 靠 `ON DELETE CASCADE`(刪 session/claim 自動級聯 verdict/escalation,per-session 冪等重寫)。

---

## 6. python 程式規畫(v1.39.0 (b);複用既有機械閘 #12、命名 #18)

### 6.1 library 模組(`src/augur/deliberation/`,領域名詞)

| 模組 | 職責 | 關鍵函式(簽名) | 輸入→輸出 |
|---|---|---|---|
| `claim.py` | Claim/Verdict/Escalation dataclass(**DDL 住 migrate script、非此**,L3) | `@dataclass Claim/Verdict/Escalation` | — |
| `perspective.py` | 本地 LLM fan-out:**import `advisor.ollama.make_llm_fn`**(FORBIDDEN→FORBIDDEN 單向合法)跑多視角、解析結構化 claim(強制錨點+verifier、無錨拒收、**只寫 pending**) | `fan_out(conn,session,draft,perspectives)->list[Claim]`;`parse_structured_claim(raw)->Claim|None` | draft → deliberation_claim |
| `adjudication.py` | 確定性裁決分派(**唯一 status writer**):依 `assigned_verifier` 派 4 真 oracle,寫 verdict + 回填 claim.status | `adjudicate(conn,claim)->Verdict`;dispatch `{information_schema:_v_schema, import_isolation:_v_iso, file_grep:_v_grep, db_query:_v_dbq}` | claim → verdict(+status) |
| `escalation.py` | 升級路由:undecidable/紅線/verifier∈{human_claude,none} → **強制**寫 escalation;紅線硬觸發讀 `deliberation_redline_trigger` 覆蓋自標 category | `route(conn,claim,verdict)->Escalation|None`;`red_line_override(conn,claim)->str|None` | claim/verdict/redline → escalation |
| `coverage.py` | 真兆錨定覆蓋:枚舉 information_schema/檔案樹真兆全集、算結構完整度、**誠實標 `enumerable=false` 於語意維度** | `enumerate_truth(conn,dim)->set`(dim∈tables/columns/files);`coverage_report(conn,session)->dict` | information_schema/檔案樹 → session.coverage |

### 6.2 4 個真可用確定性 oracle(H1 修正;複用/新寫誠實區分)

| verifier | 實作 | 可驗什麼 | 複用/新 |
|---|---|---|---|
| `information_schema` | `augur.core.schema.get_dataset_columns` + `generic_schema.db_primary_key`(L1:非 core.db) | 表/欄/型別/PK 存在性 | 複用 |
| `import_isolation` | subprocess `python -m augur.audit.import_isolation`(有 `__main__`:184) | #8 AST import 邊界 | 複用 |
| `file_grep` | subprocess `grep -n`(唯讀) | 檔/行/字串存在(錨點 `file:line` 對位) | 複用 |
| `db_query` | **新寫**純唯讀內部 SQL 斷言(`core.db`;**明標非複用 `reconcile.py`**——後者 `:28` import ingestion 打 FinMind/FRED API、觸 FREEZE+#24、token 已過期) | 凍結 DB 內部事實(如「core_universe_asof as-of X 有 N 列」) | 新 |

> **移除的偽 oracle(H1、誠實)**:`guard`(綁 advisor payload、只驗 advisor 輸出)· `effective_t_hac`(吃 IC 序列、不從錨點取 `ic_by_panel`;信任既有 artifact 只驗算術=confirm 未驗之物=§8b 搭便車)· `sql_reconcile`(**無此函式**)。**凡需 IC 顯著性/經濟價值/anti-leakage 語意判斷之 claim → `assigned_verifier='human_claude'` 升級 Claude,不機械假驗。**

### 6.3 CLI script + 既有檔擴充(#18 動作動詞;#19 跨檔一致)

| 檔 | 新/改 | 職責 | 驗收 |
|---|---|---|---|
| `scripts/deliberate_plan.py` | **新** | 組合根:一輪審議(fan_out→adjudicate→route→coverage)寫五表;`--topic/--draft/--perspectives/--as-of`;無參數印矩陣 | 端到端跑通、五表落列 |
| `scripts/report_deliberation_verdict.py` | **新** | 唯讀報告:confirmed 清單+escalation 佇列+coverage 結構完整度+**§8 四破口首屏標註** | 報告首屏印四破口 |
| `scripts/migrate_deliberation_ddl.py` | **新** | 5 表 DDL 單一住所 + 冪等種子 redline + `--check` | migration 冪等、--check 綠 |
| `src/augur/audit/import_isolation.py` | **改** | (a) `FORBIDDEN += ("augur.deliberation",)`;(b) **`DELIB_LITERALS=("deliberation_claim","deliberation_verdict",...)` + `SCAN_DELIB=PIPELINE+("core","knowledge","philosophy")`** 接進 `check_isolation()`(H3、對位 DISTILL_LITERALS:41/SCAN_DISTILL:45);(c) 新不變式 `_confirmed_needs_verdict`(H6) | pipeline 掃描仍 exit 0;注入字串 SQL/直寫 confirmed → exit 1 |
| `tests/test_deliberation_isolation.py` | **新** | 斷言 deliberation∈FORBIDDEN、字串掃描涵蓋、confirmed 不變式 | pytest 綠 |

### 6.4 「qwen 不當 judge」機械鎖(H6,升應用約定為 #8 風格不變式)

- **status 唯一 writer = adjudication.py**;`perspective.py` 只寫 `pending`(code review 契約 + 稽核)。
- **不變式(import_isolation 風格、exit 1)**:`_confirmed_needs_verdict` — 「不得有 `status='confirmed'` 之 claim 缺對應 `is_deterministic=true` 的 confirmed verdict」;任何直寫 confirmed 繞閘(perspective bug/未來 writer/qwen 夾帶)被 CI 抓。

---

## 7. import-isolation 擴充細節(#8 命門雙面,單獨列因觸三敵防線)

- **(a) AST import(既有面)**:`FORBIDDEN += ("augur.deliberation",)` — 預測管線 7 package 絕不 import 審議層(它用本地 LLM+讀全碼、單向)。
- **(b) 字串 SQL(H3 補、命門第二半)**:`DELIB_LITERALS` + `SCAN_DELIB=PIPELINE+("core","knowledge","philosophy")` — 防「import 稽核看不到的 raw SQL」把 `deliberation_*`(qwen 生成非真兆表)拉進真兆庫;與既有 `DISTILL_LITERALS`(:41)完全同構。
- **deliberation 自身 import 邊界(H2 修正、據實)**:`perspective.py` **import `augur.advisor.ollama.make_llm_fn`**(deliberation→advisor = FORBIDDEN→FORBIDDEN、單向合法、pipeline 零 import 二者);`adjudication` 之 `import_isolation`/`file_grep` 走 **subprocess**(有 `__main__`/是 CLI),`information_schema`/`db_query` 走 `core.schema`/`core.db`(import core、合法)。**不留「只 import core+全 subprocess」假宣稱**(guard/hac/make_llm_fn 皆 library 無 `__main__`、無法 subprocess)。
- **跨檔一致(#19)**:改 FORBIDDEN/字串掃描/不變式 → 同步 docstring + test + 憲章 philosophy/isolation 邊界條(§10 入憲)。

---

## 8. 四個未解破口(誠實一級結論、不可粉飾;決定「值不值得建」)

| 破口 | 機制 | 緩解嘗試 | **殘留(原理上不可全閉)** |
|---|---|---|---|
| **(a) category 自標 + 漏提** | escalation 依 qwen 自標 category;誤標 doctrine→schema 就永不升級 | 紅線硬觸發(`deliberation_redline_trigger` 讀 doctrine 檔/anti-leakage 欄 → 強制覆蓋自標);anchor 觸集即攔 | qwen **完全不提**某 doctrine claim(漏提)→ 無從觸發;**anti-leakage 觸發集非可枚舉、清單外漏網欄仍靜默走機械閘**;「該升級」本身需語意理解才知 |
| **(b) undecidable 不吐** | confidently-wrong qwen 不說 undecidable → 最需升級的失敗模式最不觸發 | verifier∈{human_claude,none}/紅線 → 強制 escalate | qwen 把「該 human_claude」誤指為「information_schema 可驗」→ 機械閘驗了**錯的東西**給 confirmed = 搭便車 |
| **(c) 覆蓋只到結構** | 枚舉真兆(表/欄/檔)達**結構**完整;doctrine 張力/anti-leakage 語意**不可枚舉** | coverage 明標 `structural_only=true`、語意維度 `enumerable=false` | 「已審完」語意完整**達不到**;結構 covered 易被誤讀成「看完了」 |
| **(d) oracle 覆蓋殘缺(H1 新增)** | 只有 4 個機械 oracle;IC 顯著性/經濟價值/anti-leakage 語意/真兆假兆**無機械 oracle** | 這些一律 `human_claude` 升級、不假驗 | **需判讀的 claim 佔正確性權重多數 → 大部分仍回落 Claude**;本地「省」的只是最不需要判讀的那塊 |

> **可信邊界(寫死在 report 輸出)**:此編排器 = Claude 判讀的**前置整備 + 分流器**,**非替代**。當替代,省的 token 與放行的錯判是同一批 claim(§0 結論 1)。

---

## 9. 分階段 W1..W6 + 驗收(resume-safe、本地背景、零外部 usage)

| 階段 | 內容 | 驗收(可機械判定) |
|---|---|---|
| **W1** | 5 表 DDL(`migrate_deliberation_ddl.py`+種子)+ import_isolation 三擴(FORBIDDEN/DELIB_LITERALS/不變式)+ test | migration+--check 冪等;**同 session 重跑冪等**(CASCADE 實測);pipeline 掃描 exit 0;注入 pipeline import/字串 SQL/直寫 confirmed → 各 exit 1;pytest 綠 |
| **W2** | `coverage.py` 真兆枚舉 + `adjudication.py` 4 oracle dispatch(**先不含 LLM**) | 每 oracle 各 ≥1 confirmed+1 refuted 具體 fixture 通過;coverage 對 DB 全表枚舉數=information_schema 真值 |
| **W3** | `perspective.py` 本地 fan-out(make_llm_fn)+ 結構化 claim 解析 | **無錨/無 verifier claim 100% 拒收不落列**(主驗收);qwen 對真實草稿產帶錨 claim;只寫 pending |
| **W4** | `escalation.py` 路由 + 紅線硬觸發(讀 redline 表) | 紅線/undecidable/verifier∈{human_claude,none} 一律入佇列;注入「誤標 doctrine→schema」→ 硬觸發攔截升級 |
| **W5** | `deliberate_plan.py` + `report_deliberation_verdict.py` | 端到端對短 horizon 草稿跑一輪;**報告首屏印 §8 四破口** |
| **W6(可選)** | Claude 理解層閘整合(escalation payload→判讀→回寫) | escalation 佇列被消化、resolution 回寫、session close |

- **W5 dogfooding(#15 誠實界)**:拿本計畫草稿餵編排器——但**綠燈只證硬觸發路徑可動,不證 §8a 漏提/§8b 誤驗被抓到**(結構上抓不到靜默殘留),**勿當「編排器可信」背書**(否則在 meta 層重演 §8c)。

---

## 10. 決策點:值不值得建 + 入憲(拍板後)

### 10.1 誠實成本效益(給用戶決策,非賣點)

| | 內容 |
|---|---|
| **建置成本** | 新 package(5 模組)+ 5 表 + 擴 #8 隔離閘雙面 + 3 CLI + test + 維護;W1-W5 中等偏重 |
| **真實效益** | **wall-clock**(本地錨事實、平行 surface 覆蓋餵 Claude);**非省 token**(§0 結論 1) |
| **不帶來的** | ❌ 有意義的 token 節省 ❌ ultracode 判讀能力 ❌ 可信自動審查(帶四破口) |
| **風險** | 被當「本地審查替代」→ 敵人③帶假背書污染;紅線靜默破口(§8a/b/d) |

### 10.2 務實建議(AI 觀點、非決策)

- **對你原意(本地 AI 在環路、習得 ultracode)——答案基本是不建**:判讀核不可移植(§0/§1)。
- **除非規劃頻率高到「事實整備成瓶頸」,否則現況已足**(Claude 直接規劃 + 既有機械閘 import_isolation/verify_candidate_promotion/deflate 已在)。
- **若要建,建議只建 W1-W2 的確定性子集**(真兆枚舉 + 4 oracle dispatch,**不含 qwen fan-out**)——這塊**零 LLM 風險、純確定性**、效益最實(自動枚舉真兆全集 + 機械驗**Claude/人 authoring 的**帶錨 claim)。**但誠實標**:此子集是「Claude/人 authoring 錨點 → 本地批次確定性驗證」工具,**非「本地 AI 整備器」**(無 LLM 則無自主 claim 來源、claim 只能人/Claude 給)——已不是你問的那件事。W3 qwen fan-out 層才回應原意,但風險與四破口集中於此。

### 10.3 入憲(拍板 + 實測後、#19)

- 憲章 philosophy/isolation 邊界條擴 `augur.deliberation`∈FORBIDDEN + `DELIB_LITERALS` 字串掃描(同步 test + docstring)。
- CLAUDE #28 二分補一句:「審議編排器=本地整備+分流,判讀不下放;弱模型不當 judge」。
- **無靈魂/憲章判準變更**(仍 Claude 理解層拍板、三敵零容忍、系統建議人決策皆既有法律之落地)。

---

## 附:實查錨(2026-07-09、#15、對抗審查逐一 grep/rollback txn 驗)
`import_isolation.py:31` PIPELINE(7)· `:33` FORBIDDEN(philosophy/advisor/knowledge)· `:41` DISTILL_LITERALS · `:45` SCAN_DISTILL · `:184` `__main__` · `guard(response,payload,citations)@guard.py:45`(綁 PredictionPayload、無 __main__)· `effective_t_hac(ic_by_panel,*,lag)@metrics.py:89`(吃 IC 序列、無 __main__)· **無 sql_reconcile**;`reconcile.py:28` import ingestion 打 API · information_schema 實住 `core/schema.py:70`(非 core.db)· codebase 零 trigger · `migrate_advisor_distill_ddl.py`(--check 慣例)· revalidation_ledger keyless append-only · guard 五閘=3 vs ground truth + 2 regex · 現有 package 無 deliberation(新)。

# Augur 未來發展計畫書（2026-07-30）——實作層對接規格版

> **依據**：`reports/augur_plain_language_full_report_20260730.md`（v11・世界建構版）之核心——**這個世界只有一條合法成長路徑，八種行走者無特權通道**。
>
> **本檔性質**：可直接開工之**實作層對接規格**（hugo 指示：「之後可以具體實作…先預先規畫相關的工具，如模型／database／data schema／程式…等可以具體實作層對接的」）。故本檔不寫願景，只寫**表、欄、DDL、檔、函式、CLI、模型角色、服務端點、凍結驗收**。
>
> **憲章第六部 v1.39.0 計畫完整性**：(a) 表 schema 見 §四（新表 DDL 全文＋所讀既有表）；(b) python 程式規畫見 §五（檔·函式·角色·簽名）；元件見 §六（模型）§七（服務端點）；分階段見 §九；驗收見 §十。
>
> **所有現況數字皆本日親驗**（`psql` 實查／`pip list`／`ollama` API／`ls`），非記憶。誠實界限見 §十一。

---

## 一、計畫的組織原則：按「行走者」切，不按產品線切

報告書的核心是一條路：

> 候選 →（證據通道：可證偽／樣本外／實效終審）→ 人類授權門 → 晉升或**判死留檔** → 後果回流成新觀測 → 下一圈

八種行走者：①認知候選 ②人類原典 ③思想原理 ④AI 能力宣稱 ⑤模擬方法 ⑥模型／隊伍 ⑦迭代程序本身 ⑧法律自己。

**所以未來發展的第一要務不是新增第九種產品，而是讓這條路在實作層真的只有一條**——見 §三 的實測發現。

## 二、現況技術底座（2026-07-30 親驗）

| 層 | 現況 | 取證 |
|---|---|---|
| **DB** | PostgreSQL，`augur` 庫 **294 張 public 表**；角色 `augur`（應用）／`augur_predict`（隔離讀）；DDL SSOT＝`scripts/migrate_*.py` **63 支** | `psql` 實查 |
| **資料規模** | `feature_values` **8,540,331** 列／`knowledge_item` **270,736**／`knowledge_sentence` **1,811,477**／`governance_proposal` 3／`trial_ledger` 32／`principle_domain_map` 8 | `psql` 實查 |
| **本機模型（ollama）** | `qwen3:8b`（教師／oracle）、`qwen3:4b`（顧問引擎／受評）、`nomic-embed-text`（嵌入） | `localhost:11434/api/tags` |
| **預測側套件** | lightgbm 4.6.0・xgboost 3.3.0・scikit-learn 1.9.0・statsmodels 0.14.6（HAC）・**arch 8.0.0**（GARCH-FHS）・scipy 1.18・pandas 3.0.5・numpy 2.4.6 | `pip list` |
| **語意側套件** | sentence-transformers 5.6.0・transformers 5.12.1・torch 2.4.1・accelerate 1.14.0・datasets 2.17.1 | `pip list` |
| **微調棧** | ⚠ **無 peft／trl／bitsandbytes／gguf／dspy** ——LoRA 路線環境**尚未備**（記憶曾誤記為已裝，本日親驗推翻） | `pip list` |
| **服務（user-level systemd）** | 11 unit＋5 timer：`augur-{chat,advisor,admin,probability,qdrant,ollama}.service`、`augur-{admission-assist,ata-advance,audit-watchdog,embed-catchup,l2-deliberation}.service+.timer` | `~/.config/systemd/user/` |
| **程式** | `src/augur/` **16 package**：advisor・arena・audit・catalog・core・deliberation・evaluation・evolution・execution・features・identity・ingestion・knowledge・models・philosophy・universe | `ls -d src/augur/*/ \| grep -v __pycache__` |
| **硬體上限** | GTX 1650 4GB（無 tensor core）→ **1.7b QLoRA 可行、4b no-go**；單通道記憶體（hugo 已拍板不修） | `ops/machines/PC002-S1800.md` |

## 三、核心實測發現：「一條路」目前是六條並行的路

親查 `information_schema` 之結果：

**(a) 三個預註冊門表，其實是同一個 13 欄骨架重複三次**

| 表 | 列數 | 欄位 |
|---|---|---|
| `arena_admission_gate` | 3 | gate_id, **axis**, purpose, criteria, criteria_sha, status, preregistered_at, approved_by, approved_at, git_sha, evaluated_at, result_snapshot, evaluation_ref, supersedes_gate_id |
| `direction_gate` | 29 | gate_id, **track, horizon**, purpose, criteria, criteria_sha, status, preregistered_at, approved_by, approved_at, evaluated_at, result_snapshot, evaluation_ref, git_sha |
| `evolution_prereg_gate` | 1 | gate_id, **axis**, purpose, criteria, criteria_sha, status, preregistered_at, approved_by, approved_at, git_sha, evaluated_at, result_snapshot, evaluation_ref, note |

**共同核心 12 欄完全一致**，差別只在「作用域欄」（axis vs track+horizon）與尾欄。三者各自有一份 migrate DDL、各自的評估器、各自的 status 詞彙。

**(b) 六個裁決表異質，且其中兩個從未被寫過**

| 表 | 列數 | 性質 |
|---|---|---|
| `deliberation_verdict` | 768 | 本地審議引擎 oracle 裁決（claim/verifier/verdict/evidence/is_deterministic） |
| `revalidation_verdict` | 2 | 重驗軌（cell/universe/track/state/triggered_cond/metric_snapshot/baseline_ref） |
| `direction_arena_verdict` | **0** | 空表——方向軸判決實際寫在 `direction_gate.status/result_snapshot` |
| `direction_econ_verdict` | **0** | 空表 |
| `econ_verdict_rule` | — | 規則表（非裁決事實） |
| `knowledge_import_verdict_dict` | — | 詞典（非裁決事實） |

**(c) 一個被命名為 gate 但不是預註冊門的東西**：`knowhow_auto_admit_gate`（enabled／require_kh8／require_kh9／channels／max_auto_depth）——它是**開關組態表**，不是「先凍結判準再看資料」的證據門。名字撞了概念。

### 診斷（這是本計畫的軸心）

報告書宣稱「無特權通道」，但實作層的事實是：**每條線各自實作了自己的門與裁決**，於是——

1. 新增第九種行走者＝再抄一份 13 欄表＋一支評估器（成本線性增長）；
2. 「這個世界目前對什麼有把握」**沒有單一可查之處**（要 union 6 張表、還要知道哪兩張是空的）；
3. 判死留檔散落在 status 欄與 result_snapshot JSONB，**跨線不可比**；
4. 「回流」沒有共同落點——各線自行決定失敗要不要記、記在哪。

**所以 P1 就是把路修成一條**：不是重寫既有六條（那會動到已定案的證據），而是**加一層統一登錄簿與唯一裁決寫入器，並以 adapter 把既有六條掛上來**。

## 四、對接規格 A・資料層（新表 DDL 全文）

> 設計紀律：**新表只增不改既有**（既有門與裁決表之列為已定案證據，`#12`／不朽律）；統一層以 **adapter 讀既有、新事實寫新表**，逐步收斂。所有新表受誠實閘（GUC 通行證）保護。

### A-1 `path_gate`——統一預註冊門登錄簿

```sql
CREATE TABLE IF NOT EXISTS path_gate (
    gate_id            TEXT PRIMARY KEY,
    walker_kind        TEXT NOT NULL,              -- 八行走者（見 A-4 值域）
    scope              JSONB NOT NULL DEFAULT '{}',-- 吸收 axis/track/horizon/cell/universe
    purpose            TEXT NOT NULL,
    criteria           JSONB NOT NULL,             -- 預先凍結之判準（機器可判）
    criteria_sha       TEXT NOT NULL,              -- 凍結指紋：評估時必須相符
    status             TEXT NOT NULL,              -- 見 A-4 狀態機
    preregistered_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    approved_by        TEXT,                       -- 唯人；AI 不得代填（L6.13）
    approved_at        TIMESTAMPTZ,
    git_sha            TEXT NOT NULL,
    evaluated_at       TIMESTAMPTZ,
    result_snapshot    JSONB,
    evaluation_ref     TEXT,
    scope_label        TEXT NOT NULL DEFAULT 'live', -- live | replay-確立 | meta | sim
    supersedes_gate_id TEXT REFERENCES path_gate(gate_id),
    adapter_source     TEXT,                       -- 若由既有表登錄而來：'arena_admission_gate' 等
    adapter_key        TEXT,                       -- 既有表之主鍵值（回溯用）
    note               TEXT,
    CONSTRAINT path_gate_status_ck CHECK (status IN
        ('preregistered','approved','evaluated_pass','evaluated_fail','undecidable','superseded','never_shown')),
    CONSTRAINT path_gate_walker_ck CHECK (walker_kind IN
        ('cognition','corpus','principle','ai_capability','sim_method','model','procedure','law')),
    CONSTRAINT path_gate_scope_label_ck CHECK (scope_label IN ('live','replay-確立','meta','sim')),
    CONSTRAINT path_gate_approved_pair_ck CHECK ((approved_by IS NULL) = (approved_at IS NULL)),
    CONSTRAINT path_gate_eval_needs_approval_ck CHECK (
        status NOT IN ('evaluated_pass','evaluated_fail') OR approved_by IS NOT NULL),
    CONSTRAINT path_gate_criteria_nonempty_ck CHECK (criteria <> '{}'::jsonb)
);
CREATE INDEX IF NOT EXISTS path_gate_walker_idx ON path_gate (walker_kind, status);
CREATE INDEX IF NOT EXISTS path_gate_label_idx  ON path_gate (scope_label);
```

**關鍵不變式**：`path_gate_eval_needs_approval_ck`——**未經人類核准之門不得評估**（把 L6 的人類授權門變成 DB 級不可繞）；`criteria_sha` 於評估時比對，不符即拒（判準凍結）。

### A-2 `path_candidate`——統一候選

```sql
CREATE TABLE IF NOT EXISTS path_candidate (
    candidate_id  BIGSERIAL PRIMARY KEY,
    walker_kind   TEXT NOT NULL,
    subject_ref   TEXT NOT NULL,            -- 被裁決之主體（feature 名／item_id／pack_id／model_key／proc_sha／proposal_id）
    origin        TEXT NOT NULL,            -- raw_evolution | human | philosophy | self_probe | external | law
    origin_ref    TEXT,                     -- 來源證據（hint_id／source_id／report 路徑）
    state         TEXT NOT NULL DEFAULT 'candidate',
    gate_id       TEXT REFERENCES path_gate(gate_id),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    payload       JSONB NOT NULL DEFAULT '{}',
    CONSTRAINT path_candidate_walker_ck CHECK (walker_kind IN
        ('cognition','corpus','principle','ai_capability','sim_method','model','procedure','law')),
    CONSTRAINT path_candidate_state_ck CHECK (state IN
        ('candidate','gated','promoted','retired','killed')),
    CONSTRAINT path_candidate_uniq UNIQUE (walker_kind, subject_ref, created_at)
);
CREATE INDEX IF NOT EXISTS path_candidate_state_idx ON path_candidate (walker_kind, state);
```

### A-3 `path_verdict`——唯一裁決寫入落點（含判死留檔）

```sql
CREATE TABLE IF NOT EXISTS path_verdict (
    verdict_id      BIGSERIAL PRIMARY KEY,
    gate_id         TEXT NOT NULL REFERENCES path_gate(gate_id),
    candidate_id    BIGINT REFERENCES path_candidate(candidate_id),
    walker_kind     TEXT NOT NULL,
    subject_ref     TEXT NOT NULL,
    verdict         TEXT NOT NULL,           -- pass | fail | undecidable
    is_terminal     BOOLEAN NOT NULL,        -- 終局（判死留檔、永不翻案）
    metric_snapshot JSONB NOT NULL,          -- 實際量到的值（可溯源）
    threshold_source TEXT NOT NULL,          -- 判準出處（gate criteria_sha／條號）
    evidence_ref    TEXT,                    -- 證據鏈落點（帳本列／報告路徑）
    scope_label     TEXT NOT NULL,           -- live | replay-確立 | meta | sim（不得混算）
    decided_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_by      TEXT NOT NULL,           -- 'oracle:<name>' | 'human:<id>'（AI 不得寫 human:*）
    adapter_source  TEXT,                    -- 由既有裁決表登錄者標明
    CONSTRAINT path_verdict_ck CHECK (verdict IN ('pass','fail','undecidable')),
    CONSTRAINT path_verdict_walker_ck CHECK (walker_kind IN
        ('cognition','corpus','principle','ai_capability','sim_method','model','procedure','law')),
    CONSTRAINT path_verdict_label_ck CHECK (scope_label IN ('live','replay-確立','meta','sim')),
    CONSTRAINT path_verdict_metric_nonempty_ck CHECK (metric_snapshot <> '{}'::jsonb),
    CONSTRAINT path_verdict_undecidable_ck CHECK (verdict <> 'undecidable' OR is_terminal = false)
);
CREATE INDEX IF NOT EXISTS path_verdict_subject_idx ON path_verdict (walker_kind, subject_ref);
CREATE INDEX IF NOT EXISTS path_verdict_label_idx   ON path_verdict (scope_label, decided_at);
```

**誠實閘（三表共用；沿用 `fv_guard`／honesty trigger 之既成形式）**

```sql
CREATE OR REPLACE FUNCTION path_honesty_guard() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'path_* 為不朽帳本：DELETE 一律拒絕（只得標 superseded/retired）';
    END IF;
    IF current_setting('augur.honesty_write', true) IS DISTINCT FROM 'on' THEN
        RAISE EXCEPTION 'path_* 寫入須通行證：SET LOCAL augur.honesty_write = ''on''';
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;
-- 三表各掛 BEFORE INSERT OR UPDATE OR DELETE；TRUNCATE 另掛 statement-level 拒絕
```

**「人不得被代簽」之機械化**（承 never-type-human-signature 之教訓，升格為 DB 閘）

```sql
CREATE OR REPLACE FUNCTION path_no_ai_human_sig() RETURNS trigger AS $$
BEGIN
    IF NEW.decided_by LIKE 'human:%'
       AND current_setting('augur.human_session', true) IS DISTINCT FROM 'on' THEN
        RAISE EXCEPTION 'human:* 裁決須人類會話通行證（AI 不得代簽 §8.1／L6.13）';
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;
```

### A-4 值域與狀態機（單一權威家；`#29(b)` 資料驅動之例外說明）

- `walker_kind` 八值＝報告書八行走者，**寫在 CHECK 而非 DB 資料表**：它是概念層閉集（八類由治權定義、非策展資料），符合「詞表不鎖＝執行層、安全繫於閘」之裁。新增第九類須先入憲。
- 狀態機：`preregistered → approved →（evaluated_pass｜evaluated_fail｜undecidable）`；`superseded`／`never_shown` 為側支。**未 approved 不得 evaluated**（CHECK 強制）。

### A-5 所讀之既有表（不改，只讀／掛 adapter）

`arena_admission_gate`・`direction_gate`・`evolution_prereg_gate`・`deliberation_verdict`・`revalidation_verdict`・`direction_arena_verdict`・`direction_econ_verdict`・`evolution_production_feature_set`・`evolution_hypothesis_hint`・`evolution_iteration_ledger`・`trial_ledger`・`feature_values`・`feature_candidate_values`・`knowledge_item`／`knowledge_sentence`／`knowledge_source`・`principle_domain_map`・`governance_proposal`／`governance_queue`・`arena_replay_run`／`direction_arena_replay`・`meta_replay_cutoff`／`meta_replay_perf`。

## 五、對接規格 B・程式層

### B-1 新套件 `src/augur/path/`（第 19 個 package；領域名詞、非角色名——`#18` 命名慣例）

| 檔 | 角色 | 主要函式簽名 |
|---|---|---|
| `registry.py` | 門登錄簿讀寫 | `register_gate(walker, scope, purpose, criteria, git_sha) -> str`（回 gate_id；status=preregistered）<br>`approve_gate(gate_id, approved_by, *, human_session) -> None`（拒 AI 代簽）<br>`get_gate(gate_id) -> Gate`／`list_gates(walker=None, status=None) -> list[Gate]`<br>`assert_criteria_frozen(gate_id, criteria) -> None`（sha 不符即 raise） |
| `candidate.py` | 候選生命週期 | `submit(walker, subject_ref, origin, origin_ref=None, payload=None) -> int`<br>`attach_gate(candidate_id, gate_id) -> None`<br>`transition(candidate_id, state, *, reason) -> None`（狀態機守衛） |
| `verdict.py` | **唯一**裁決寫入器 | `write_verdict(gate_id, subject_ref, verdict, metric_snapshot, threshold_source, *, scope_label, decided_by, is_terminal, candidate_id=None, evidence_ref=None) -> int`<br>內含：GUC 通行證、criteria_sha 核對、`human:*` 阻擋、終局不可覆寫檢查 |
| `adapters.py` | 掛既有六條上來 | `sync_gate_table(source: str) -> int`（把 arena／direction／evolution 三門表登錄進 path_gate，帶 adapter_source/adapter_key，冪等）<br>`sync_verdict_table(source: str) -> int`（同理，含空表誠實回報 0） |
| `status.py` | 全景查詢（唯讀） | `walker_summary() -> list[Row]`（每行走者：候選數／門數／pass／fail／undecidable／最近裁決）<br>`path_integrity() -> list[Finding]`（斷點偵測：門無裁決、裁決無門、approved 缺人簽、scope_label 混算） |
| `__main__.py` | `#18` 自測 CLI | `python -m augur.path`（印用途＋公開入口）／`--selftest`（免 DB：狀態機、sha 核對、human 阻擋之純邏輯紅綠） |

### B-2 新 `scripts/`（薄 CLI，邏輯在 src；`#29` 四件全備）

| script | 職責 | CLI（指令矩陣節錄） |
|---|---|---|
| `migrate_path_registry_ddl.py` | 建 A-1~A-3 三表＋兩 guard＋索引；`--check` 唯讀驗證；冪等 | `python3 scripts/migrate_path_registry_ddl.py --check` |
| `sync_path_registry.py` | 跑 adapters：把既有 3 門表＋4 裁決表登錄進統一層 | `--source all｜arena_admission_gate｜…`／`--dry-run` |
| `path_status.py` | 印八行走者全景＋路完整性缺口（人與 CI 共用） | 無參數＝全景；`--walker cognition`；`--json`；`--integrity`（缺口非 0 則 exit 1） |
| `submit_path_candidate.py` | 通用候選投遞（各線共用，取代逐線私有腳本） | `--walker corpus --subject item:12345 --origin harvest` |

### B-3 既有程式之接線點（改動最小化）

| 既有 | 改法 | 影響 |
|---|---|---|
| `scripts/verify_candidate_promotion.py` | 四關結束後改呼 `path.verdict.write_verdict(walker='cognition', …)`（原輸出不動） | +3 行 |
| `scripts/run_economic_eval.py` | 實效終審結果一併寫 path_verdict（threshold_source＝econ 判準） | +3 行 |
| `scripts/evaluate_meta_replay_gate.py` | 終局裁決改走統一寫入器，`scope_label='meta'` | +3 行 |
| `scripts/run_arena_replay.py`／`settle_arena_labels.py` | 判決寫入時帶 `scope_label='replay-確立'`／`'live'`——**機械保證 live 門不吃 replay** | +2 行 |
| `scripts/eval_local_model.py` | 能力宣稱裁決寫 `walker='ai_capability'` | +3 行 |
| `scripts/governance_queue*`（人閘 CLI） | enacted 時寫 `walker='law'`、`decided_by='human:<id>'`（須人類會話通行證） | +3 行 |
| `scripts/promote_knowledge.py` | 准入裁決寫 `walker='corpus'` | +3 行 |
| `scripts/deliberate.py` | oracle 裁決寫 `decided_by='oracle:<name>'`（既有 `deliberation_verdict` 保留為引擎內帳） | +3 行 |

## 六、對接規格 C・模型層（角色 → 模型對映）

| 角色 | 現行模型 | 介面 | 上限／約束 |
|---|---|---|---|
| **顧問引擎（受評者）** | `qwen3:4b`（ollama） | `tools/local_llm_mcp` → `/api/generate`，經 **LANE-GOV flock** 序列化 | 4GB VRAM；逐字引用受 guard 核對 |
| **教師／oracle** | `qwen3:8b`（ollama） | 同上 | hugo 鐵律：**演化教師永久本地化**（oracle＞8b 教 4b＞人裁），外部 AI token 歸零 |
| **嵌入** | `nomic-embed-text`（ollama）＋ sentence-transformers（e5 系）雙軌 | pgvector（private）／Qdrant（public serving） | 口徑須單一登錄，混用即污染檢索 |
| **橫斷面預測** | Ridge（sklearn 1.9）＋ LightGBM 4.6／XGBoost 3.3 | `src/augur/models` | 走著瞧、只吃完整核心股 |
| **統計檢定** | statsmodels 0.14.6（HAC／Eff-t） | `evaluation/metrics.py:effective_t_hac` | 禁裸用 iid effective_t |
| **風險模擬** | arch 8.0.0（GARCH-FHS）＋自建重抽法 | 模擬方法庫 | 四鎖：模擬非預測 |
| **外來時序基礎模型** | chronos-bolt／moirai-2.0／timesfm-2.5 | replay 合法窗已親驗（權重污染邊界） | 僅 replay／arena 對照，不入生產認知 |
| **微調（規劃中）** | 1.7b 級 QLoRA | peft＋trl＋bitsandbytes → `convert_lora_to_gguf` → ollama `ADAPTER` | ⚠ **四套件皆未裝**＝P0 環境前置；4b no-go（embedding 不被量化）；llama.cpp 未裝且**禁跑其 requirements.txt** |

## 七、對接規格 D・服務與端點

**現有 11 unit＋5 timer**（user-level systemd）：`augur-chat`（聊天前台）・`augur-advisor`（顧問）・`augur-admin`・`augur-probability`・`augur-qdrant`（public serving）・`augur-ollama`（含 `max-loaded.conf` drop-in）・`augur-admission-assist`＋timer・`augur-ata-advance`＋timer・`augur-audit-watchdog`＋timer・`augur-embed-catchup`＋timer・`augur-l2-deliberation`＋timer。

**本計畫新增／改動**：

| 端點 | 動作 | 理由 |
|---|---|---|
| `augur-path-integrity.service`＋`.timer`（日一次） | **新增**：跑 `path_status.py --integrity`，缺口非 0 則寫 `evolution_deferred_work` 並告警 | 路的完整性須有守夜人（否則斷點靜默） |
| `augur-advisor`／`augur-chat` | 改動後**必須 restart**（`http.server` 啟動時載入、不熱更新——CLAUDE #7 血淚條） | 否則實測跑舊記憶體版＝假通過 |
| LANE-GOV flock | 沿用；新增之任何 LLM 消費者一律經 `/tmp/augur_llm.lock` | 兩 session 搶 ollama 曾致評測餓死 |

## 八、八行走者各線之下一步（實作級）

> 本節逐線之現況表名／腳本／缺口，由 10-agent 實作事實蒐集（`wf_23534a31-6fd`）逐條補齊後定稿；**下表為已親驗之骨架與確定項**。

| 行走者 | 已有的路 | 下一步（實作級） | 需要 |
|---|---|---|---|
| ①認知候選 | `evolution_hypothesis_hint`→`feature_candidate_values`→四關→`evolution_production_feature_set`（**注意：無 `prodset*` 表，真名為此**） | 7 顆交互候選走四關；存活者促升；四關結果改寫統一裁決 | 零 schema 變動＋B-3 接線 |
| ②人類原典 | `knowledge_source`→staging→`knowledge_item`(270,736)→`knowledge_sentence`(1,811,477)→嵌入；KH1–KH4 閉環 | KH5–KH9 逐層點亮；每層之「可答性」寫成門 | 各層一個 `path_gate` |
| ③思想原理 | `principle_domain_map`(8 列)→factor 映射 | 映射→假說→四關之接線閉合；跨域擴張 | 零 schema 變動 |
| ④AI 能力 | `eval_local_model` 凍結集＋能力格 v2；A′ 待判 | **P0 環境前置**（peft/trl/bitsandbytes＋4-bit smoke）→1.7b QLoRA→權重鏈 | 環境；訓練資料落點表 |
| ⑤模擬方法 | 四法對照已結案（arch/GARCH-FHS） | 第二輪：episode 五窗＋copula-t／EVT／跨市場；參數 commit 即凍結 | 方法登錄列＋門 |
| ⑥模型／隊伍 | `arena_admission_gate`／`direction_gate`(29)／`arena_replay_run`／`direction_arena_replay` | TSFM 三隊 replay；**live 2/250 clusters**（凍結門 `dgate_arena_own_daily_5` 等 11 門實查＝250；own_stack H 門＝36；治權檔「≥60」不符、呈裁）；門評待樹乾淨 | `scope_label` 機械化（A-3） |
| ⑦迭代程序 | `meta_replay_cutoff`／`meta_replay_perf`；proc_sha 家族 | M2 月頻掃完→門評；n<60 誠實 undecidable | 零 schema 變動 |
| ⑧法律自己 | `governance_proposal`(3)／`governance_queue`；honesty triggers | 乙批五案待裁；提案自動投遞（進化迴圈→人閘） | `walker='law'` 接線 |

## 九、分階段（每階段可獨立驗收、可獨立回退）

| 階段 | 內容 | 前置 | 產出 |
|---|---|---|---|
| **P0 環境前置** | `pip install peft trl bitsandbytes`＋4-bit 載入 smoke（GTX 1650）；不動 torch/transformers 版本 | 無 | import smoke 綠；版本鎖記錄 |
| **P1 統一層落地** | `migrate_path_registry_ddl.py` 建三表二 guard；`src/augur/path/` 五模組＋`--selftest` | 無（不動既有） | `--check` 綠；selftest 綠 |
| **P2 掛既有** | `sync_path_registry.py --source all`（3 門表 33 列＋4 裁決表 770 列，冪等） | P1 | `path_status.py` 全景可查；空表誠實顯示 0 |
| **P3 接線八線** | B-3 八處各 +2~3 行；新裁決一律雙寫（既有表＋統一表），觀察一週後才考慮單寫 | P2 | 每線至少一筆新裁決落統一表 |
| **P4 守夜人** | `augur-path-integrity` timer；缺口寫 `evolution_deferred_work` | P3 | 首輪 integrity 報告 |
| **P5 各線推進** | §八 逐線下一步（可與 P1–P4 平行，互不阻塞） | 各線自身前置 | 各線既有驗收 |
| **P6 第二域 pilot** | 以「法屬世界」之實證為目標：登錄一個**不需新 API 額度**之第二域（候選：已在庫的總經／知識域），走完 L1 附錄→L2 型別→L3 鑄造→L4 五元組→一條路一圈 | P1–P3 | 一份 Domain Profile 附錄草案＋一顆走完整路的候選 |

## 十、驗收（機器可判、先於實作凍結）

| # | 判準 | 驗收指令 |
|---|---|---|
| V1 | 三表建立、二 guard 生效：無通行證寫入被拒、DELETE 被拒 | `python3 scripts/migrate_path_registry_ddl.py --check` |
| V2 | `path/` 五模組自測綠（狀態機、sha 核對、human 代簽阻擋） | `python -m augur.path --selftest` |
| V3 | adapter 冪等：連跑兩次列數不變、`adapter_key` 無重複 | `python3 scripts/sync_path_registry.py --source all` ×2 |
| V4 | 未 approved 之門不得評估（CHECK 實測拒絕） | selftest 內建負向案例 |
| V5 | `scope_label` 不混算：live 門之樣本計數 SQL 排除 `replay-確立` | `path_status.py --integrity` exit 0 |
| V6 | 八行走者全景可一頁查得（含 0 值誠實顯示） | `python3 scripts/path_status.py` |
| V7 | 既有六條路之證據**零變動**（列數與 sha 前後相同） | 前後 `count(*)`＋`md5(array_agg(...))` 比對 |
| V8 | P0 環境：4-bit 1.7b 載入成功、4b 明確 OOM（誠實記錄上限） | smoke log |

## 十一、誠實界限與風險

1. **本檔為計畫，未實作**：§四 DDL 尚未執行、§五 程式尚未寫；所有「已有」欄位皆本日親驗，所有「新增」皆未動工。
2. **微調棧未備**（§二 ⚠）：任何 LoRA 排程在 P0 完成前都是空中樓閣；記憶曾誤記為已裝，本日推翻並已更正記憶檔。
3. **雙寫期風險**：P3 採雙寫（既有＋統一）以保既有證據零動；若兩邊不一致，以既有為準、統一層標 `adapter_source` 待對帳——**不得反過來以統一層覆寫既有**。
4. **`walker_kind` 八值閉集**：新增第九類行走者屬治權變更（須入憲），不得由 code 逕自加值。
5. **不觸判準**：本計畫全部屬執行層（新增機制、接線、守夜人）；§八 ⑧之乙批五案與「一條路總則入憲」（乙-3）仍待 Steward 裁，**本計畫不預設其結果**。
6. **第二域 pilot 之邊界**：P6 僅到「走完一圈」之實證，**不含放量抓取、不含新 API 額度、不改 FREEZE 相關判準**。

---

*上位依據：`AUGUR-MC v1.6`（§4 EV 鏈／§P4／§P5）；`AUGUR-KS v1.1`（信度格／不朽律）；`AUGUR-L6`（授權鏈根為人／OCV 棘輪）；`AUGUR-L7`（登錄簿模式／可執行測試證明）；領域：大憲章 v1.49.0・原則精華 v1.11.0・CLAUDE.md v1.31。量尺：`reports/augur_plain_language_full_report_20260730.md`（v11）。姊妹計畫：`reports/augur_treaty_core_alignment_plan_20260730.md`（治權對核）。*

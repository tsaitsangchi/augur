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
| **硬體上限（2026-07-30 親驗更正）** | **當家機 PC002-S1800＝CPU-only、無獨顯**（`GPU: 無 nvidia-smi`／`nvcc: 未安裝`／x86_64／12 緒／RAM 11.7–15.9 GiB＋swap 69.8 GiB／單通道，hugo 已拍板不修）。**GTX 1650 4GB 屬 DESKTOP-8MQPFS8**（25.4 GiB／CUDA 12.6／sm_75），該機**與當家機並行使用於本專案**（Steward 2026-07-30 確認）。⚠ 故「1.7b QLoRA 可行」**只對 DESKTOP 成立、對當家機不成立**（CPU LoRA 已退場）；與 §8.4 之親驗一致 | `ops/machines/PC002-S1800.md`＋`DESKTOP-8MQPFS8.md` 逐行親驗 |

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
| **微調（規劃中）** | 1.7b 級 QLoRA | peft＋trl＋bitsandbytes → `convert_lora_to_gguf` → ollama `ADAPTER` | ⚠ **雙重阻塞（親驗）**：(1) 四套件皆未裝；(2) **當家機無 GPU 無 CUDA → QLoRA 於本機物理不可行**（`torch.cuda.is_available()=False`），唯 DESKTOP-8MQPFS8（GTX 1650 4GB、**並行使用中**）可跑。4b no-go；llama.cpp 未裝且**禁跑其 requirements.txt** |

## 七、對接規格 D・服務與端點

**現有 11 unit＋5 timer**（user-level systemd）：`augur-chat`（聊天前台）・`augur-advisor`（顧問）・`augur-admin`・`augur-probability`・`augur-qdrant`（public serving）・`augur-ollama`（含 `max-loaded.conf` drop-in）・`augur-admission-assist`＋timer・`augur-ata-advance`＋timer・`augur-audit-watchdog`＋timer・`augur-embed-catchup`＋timer・`augur-l2-deliberation`＋timer。

**本計畫新增／改動**：

| 端點 | 動作 | 理由 |
|---|---|---|
| `augur-path-integrity.service`＋`.timer`（日一次） | **新增**：跑 `path_status.py --integrity`，缺口非 0 則寫 `evolution_deferred_work` 並告警 | 路的完整性須有守夜人（否則斷點靜默） |
| `augur-advisor`／`augur-chat` | 改動後**必須 restart**（`http.server` 啟動時載入、不熱更新——CLAUDE #7 血淚條） | 否則實測跑舊記憶體版＝假通過 |
| LANE-GOV flock | 沿用；新增之任何 LLM 消費者一律經 `/tmp/augur_llm.lock` | 兩 session 搶 ollama 曾致評測餓死 |

## 八、八行走者＋路自己＋第二域：逐線實作級現況與可開工缺口

> **來源**：10-agent 實作事實蒐集（`wf_23534a31-6fd`；1,253,834 tokens／573 次工具調用），全部以 live DB `psql`／repo DDL／code 逐行親驗，每則標取證方式。**凡標「親驗 CONFIRMED」者為實查坐實之缺口，非推測。**

### 8.0 跨線最嚴重五則（先看這個）

| 嚴重度 | 線 | 缺陷 | 為何要命 |
|---|---|---|---|
| 🔴 | ⑧法律自己 | **人閘人簽可被裸 SQL 自蓋**（親驗 CONFIRMED）：`governance_proposal_immutable` 只鎖 DELETE 與部分欄改，未鎖「AI 直接 UPDATE 人簽欄」 | 人類授權門是 L6 之根；可自蓋＝整條授權鏈失效 |
| 🔴 | ⑧法律自己 | **`local_model_version` 晉升人簽可由 INSERT 全繞**（親驗 CONFIRMED）：`model_version_no_goalpost` 只擋 UPDATE | 模型晉升 serving 之人簽保證形同虛設 |
| 🔴 | ⑥模型隊伍 | **cluster 門檻三處口徑分裂，且計分板每日對你印錯數字** | 我今日即因此對你誤報「2/60」；錯的數字每天在印 |
| 🟠 | ①認知候選 | **生產認知集成員 `lending_fee_rate_mean_20d` 在 repo 內完全沒有產生器** | 該特徵不可複現＝生產認知集有一半無法重建 |
| 🟠 | 第二域 | **World Concept Registry 零實作，且自 2026-07-30 起已成硬阻塞**；且 **FRED 與國際股票都不算第二域**（Annex A.0 已涵蓋） | 「法屬世界」之實證路徑被堵；第二域範圍認定比想像窄 |

### 8.1 ①認知候選

*行走者①認知候選(假說→四關→生產認知集)——實作級事實與可開工缺口*

**既有表（18）**：`feature_values`（8,540,331 列 / 38 distinct feature / 113 distinct panel_date(）、`feature_candidate_values`（155,037 列 / 11 candidate feature;7 顆 INTERACT(28 panel 2014-）、`evolution_production_feature_set`（9 列;**active=2**(inst_cumflow_position_120d 07-24、lending_fe）、`promotion_queue`（310 列:rejected_gate/demote 251、rejected_gate/freeze 20、appli）、`evolution_apply_log`（最大 id=24;id 24 = lending 促升,evidence_json.gate_ref='HUMAN-PR）、`evolution_run`（7 列(run_id 1,2,3,4,5,6,10);run 10 = human_promotion 事件列,note）、`evolution_coverage_snapshot`（最新 run_id=6(非 10):mapped 35、missing 3、blocked_div 1 = 39 列;但）、`principle_factor_map`（104 列 / 51 distinct feature;created_at:07-27 58 列、07-28 19 列）、`evolution_hypothesis_hint`（**10 列全為 approved、pending=0**;decided_by='hugo(對話拍板)'、decisi）、`core_universe_asof`（**102 panel**、2018-01-31..2026-06-30、2018-2025 各 12/年 + 2026）、`trial_ledger`（32 列,**source 全為 'revalidation_ledger'、recipe 全 'plain'、feat）、`evolution_iteration_ledger`（tw 4 列:**tw-20260728-r01 status='running' 但 jsonb_array_leng）、`evolution_deferred_work`（4 列(id 2-5);id 4/5 = 07-28、07-29 23:00 TWEVO cron 'heavy slo）、`evolution_prereg_gate`（1 列）…

**既有 script（22）**：`verify_candidate_promotion.py`、`verify_sign_consistency.py`、`run_economic_eval.py`、`run_philosophy_evolution.py`、`apply_evolution_promotions.py`、`run_evolution_iteration.py`、`build_interaction_candidates.py`、`build_feature_panel.py`、`prodset_contract.py`、`baseline.py`、`verify_prodset_hotpath.py`、`verify_evolution_acceptance.py`、`evolution.py`、`heavy_slot.py`、`run_raw_evolution_iteration.py`、`build_pme_fundamental_features.py`…

**缺口與可開工下一步（11）**

| 工 | 缺什麼 | 可開工的第一步 | 需要的表／欄 |
|---|---|---|---|
| M | **生產認知集成員 `lending_fee_rate_mean_20d` 在 repo 內完全沒有產生器**——repo-wide `grep -rln --include=*.py --include=*.sh --include=*.sql` 只命中 verify_sign_consistency.py / verify_candidate_promotion.py / run_economic_eval.py 三處**皆為 docstring 或 CLI 範例字串**,`src/augur/features/` 零實作(chip.py 只有名實不符的 `lending_fee_rate_mean_30d`)。該特徵卻已有 1 | 在 `src/augur/features/chip.py` 新增 `lending_fee_rate_mean_20d`(真 20 交易日窗;現有 `_LEND_SQL` 為「最近 100 筆」需另開查詢)與 `lending_fee_vw_mean_20d`(量加權),在 `src/augur/features/phase.py` 新增 `days_since_high_126d` / `days_since_high_252d_raw` / `log1p_days_since_high_252d`;於 `src/augur/features/panel.py:build_panel` 註冊呼叫。然後 `python scrip | 零 schema 變動(feature_values 既有);新增 code 於 features/chip.py、features/phase.py、features/panel.py |
| M | **候選建值(I1)與四關(I2)未接進一鍵迴圈**——`scripts/run_evolution_iteration.py:50-56` 之 `STEP_CMD["I1"]=None`、`STEP_CMD["I2"]=None`,`_do_step`(:143-148)只跑 `SELECT count(DISTINCT feature) FROM feature_candidate_values` 並寫 note,**從不呼叫 build_interaction_candidates.py 或 verify_candidate_promotion.py / verify_sign_consistency.py / run_eco | 改 `scripts/run_evolution_iteration.py`:`STEP_CMD["I1"]=["scripts/build_candidate_values.py","--run"]`(新增之統一 builder,見下一 gap)、`STEP_CMD["I2"]=["scripts/run_candidate_funnel.py","--run"]`(新增之四關批次 driver:對 staging 全候選依序跑 as-of HAC → 多 seed 增量 → 符號尺 → econ,逐候選寫 gate 結果並對過關者 INSERT promotion_queue action='promote' queue_sta | 新表 `candidate_gate_result`(見下一 gap);新增 script scripts/run_candidate_funnel.py;改 scripts/run_evolution_iteration.py |
| M | **四關結果零落帳**——`verify_candidate_promotion.py` 全檔唯一 INSERT 是寫 staging 值(:71-72),不存任何 gate 判定;`run_economic_eval.py` **零 INSERT/UPDATE**(grep 確認),經濟終關結果只在 stdout。後果:(1) 每次要重跑才知道候選過沒過(CPU 重、違 #28)(2) 無法機器稽核「這顆真的過了四關嗎」(3) lending 促升時 promotion_queue:311 之 gate_json 是自由格式 `{"kind":"human_promotion","gates":{"g1_hac_t":2.63," | 新增 `scripts/migrate_candidate_gate_ddl.py` 建 `candidate_gate_result(result_id BIGSERIAL PK, feature VARCHAR(255) NOT NULL, gate VARCHAR(16) NOT NULL CHECK(gate IN ('G1-ASOF','G2-HACT','G3-DELTA','G4-SIGN','G5-ECON')), horizon INT, verdict VARCHAR(16) NOT NULL CHECK(verdict IN ('PASS','FAIL','SKIP','UNJUDGEABLE')), metr | 新表 candidate_gate_result + honesty trigger;三支 script 加 --ledger;apply_evolution_promotions.py 加前置查驗 |
| M | **七閘引擎看不見 staging,11 顆已掛 map 的候選永遠進不了 promotion_queue**——`run_philosophy_evolution.py:180` 以 `EXISTS(SELECT 1 FROM feature_values fv WHERE fv.feature=m.feature)` 判 in_fv,取值查詢(:288/:458/:462/:473/:488)一律 FROM feature_values。而 principle_factor_map 51 feature 中有 11 顆**只在 feature_candidate_values**(close_x_sbl_balance_leve | 改 `scripts/run_philosophy_evolution.py`:(a) in_fv 查詢改為 `EXISTS(... feature_values) OR EXISTS(... feature_candidate_values)` 並在 coverage_snapshot 增記來源(既有欄 in_feature_values 保留原義,新增 `in_candidate_values BOOLEAN`)(b) 取值路徑改走 `augur.evaluation.baseline._panel_matrix`(已支援併讀)而非裸 SQL,#12 不重造(c) gate_json 增記 `value_source: 'pro | evolution_coverage_snapshot 加一欄 `in_candidate_values BOOLEAN NOT NULL DEFAULT false`(冪等 ALTER);改 scripts/run_philosophy_evolution.py |
| S | **7 顆 INTERACT 候選建在舊網格上,與 prodset 基準不同尺**——staged panel 為 28 枚(2014-12-31、2015..2020 各年底、2021-03-31 起季頻、末枚 2026-05-31),其中**只有 24 枚落在現行 102 枚 as-of 網格內**(2014-2017 四枚年度 panel 已不在 core_universe_asof,其 min=2018-01-31),且缺 78 枚月頻 panel、缺 2026-06-30。四關之 IC 走 `core_universe_asof` 102 panel,候選只有 24 panel 有值 → 增量 Δ 測試兩側樣本數不等 =  | 先 `venv/bin/python scripts/build_interaction_candidates.py --dry-run` 確認末 panel 已是 2026-06-30,再 `--run`(讀 core_universe_asof:107,冪等 upsert,自動補至 102 panel),隨即 `--audit-visibility` 跑洩漏自稽(revenue 15 日發布閘 + 越窗斷言);之後以 SQL 確認每顆候選 `count(distinct panel_date)` == core_universe_asof `count(distinct as_of_date)`;2014-2017 四枚孤兒 p | 零 schema 變動、零改碼 |
| S | **TWEVO 迴圈實質停擺 3 日**——`evolution_iteration_ledger` 之 `tw-20260728-r01` status='running' 且 `jsonb_array_length(steps_json)=0`;`open_round`(:172-178)見有 running 即印「已有進行中之輪…續跑用 --step 或 --run」直接 return 0,故 cron 每晚只是重撞同一堵牆;07-28 與 07-29 23:00 兩次皆寫 evolution_deferred_work(reason='heavy slot busy')並 rc=75。heavy_slot advisory  | (a) 立即:待 LAIEVO 臂收槍後 `venv/bin/python scripts/run_evolution_iteration.py --run`(續跑 tw-20260728-r01);(b) 結構修:於 `scripts/run_evolution_iteration.py` 新增 `--reap-stale [--hours 48]`,把 opened_at 早於閾值且 steps_json 為空之 running 輪以 `--close --partial` 語意收為 status='halted'、gain_basis='incomparable'、stop_reason='stale_no_progress' | 零新表(evolution_iteration_ledger 既有 stop_reason 欄);改 scripts/run_evolution_iteration.py + scripts/verify_evolution_acceptance.py |
| M | **SUNSET (b) 之符號一致性尺未接到 APPLY 邊界**——`verify_sign_consistency.py`(5-bootstrap 全同號才 PASS、UNJUDGEABLE fail-closed)在 repo 內**零呼叫者**;實際擋 APPLY 的是 `philosophy/evolution.py` 的 M-1 弱檢(direction-adjusted `mean_ic < 0` → FAIL_SIGN),無 bootstrap、無「全 h 同 PASS」要求。且 `GATE_IDS` 七閘不含 G-SIGN。後果:SUNSET (b) 白紙條件「每一新成員通過符號一致性檢查」在機械上無人執行——現 | (a) 把 `verify_sign_consistency.py` 的 `judge_sign` + bootstrap 迴圈抽進 `src/augur/philosophy/evolution.py`(判準單一住所 #12),於 GATE_IDS 增 'G-SIGN' 並在 DEFAULT_GATE_CONFIG 加 `{"n_boot_seeds":5,"seed0":42,"require_all_h":true}`;(b) `apply_evolution_promotions.py` 之 all_gates_green 自動連坐(GATE_IDS 增列即生效);(c) 回溯親驗現有 active 2 顆:`venv/bi | 零新表;改 src/augur/philosophy/evolution.py(GATE_IDS + config + evaluate_g_sign)、scripts/run_philosophy_evolution.py(組 gate_json)、scripts/verify |
| S | **候選搜尋的多重檢定成本未入 N,DSR 系統性低估**——`trial_ledger` 32 列 **source 全為 'revalidation_ledger'、feats_hash 僅 1 種**;`run_economic_eval.py` 零寫入,`verify_candidate_promotion.py` 的多 seed × 多 h × 多模型 ladder 也零寫入。實測 07-29 lending 一顆就跑了「3 seed × 2 h × 2 模型」增量 + 4 配置 econ 雙跑 ≈ 十餘個 trial,全未計入 N。DSR deflation 因此把「撒網成本」記為 0(直接違 #11「撒更多網=多重檢定 | 為 `run_economic_eval.py` 與 `verify_candidate_promotion.py` 各加 `--ledger` 旗標,以 `execute_values` 寫 trial_ledger:`source='candidate_econ'` / `'candidate_promotion'`,`recipe` 記候選名,`feats_hash` = sha256(sorted(feats)+panels_hash) 前 12 字(使不同網格自然分家,承便宜尺寸先行教訓),ON CONFLICT DO UPDATE 保持同 config 重跑不增 N;於 `scripts/revalidate.py:re | 零 schema 變動(trial_ledger 既有 source/recipe/feats_hash 欄、UNIQUE 8 欄含 recipe);改兩支 script |
| M | **假說前端已抽空,下一批候選無來源**——`evolution_hypothesis_hint` 10 列**全 approved、pending=0**(全數已於 07-28 由 hugo 以 H3-CONV-20260728 批完並掛進 map);`raw_evolution_iteration_ledger` **僅 1 輪**(raw-20260727-r01),RAWEVO cron 為週六 09:00 → 最快 08-01 才有新 hint。另 map 有 3 顆特徵**兩表皆無值**:`macro_regime`(dir +1, p88)、`peg_ratio`(dir -1, p87)、`piotroski_fsc | (a) 不等週六:立刻 `venv/bin/python scripts/run_raw_evolution_iteration.py --run --top-hints 15` 手動開一輪產 pending hint(唯讀 raw、零 FinMind);(b) 在 `src/augur/features/fundamentals.py` 實作 `piotroski_fscore`(9 項二元、全出財報 raw、發布日 gate 15 日)與 `peg_ratio`(PER ÷ 盈餘成長率;注意 raw PER=0 是哨兵佔 23.5%、PER=-1 僅 2 列,須先過濾),移除 build_pme_fundamental_feat | 零新表;改 src/augur/features/fundamentals.py、scripts/build_pme_fundamental_features.py;map 退場需新增 status 欄或以 validated_econ 記誠實註記(擇一,須人裁) |
| L | **候選建值無統一 builder,違 #29(c) 通用可重用**——現況:7 顆 INTERACT 有 `build_interaction_candidates.py`(FEATURES 為寫死 list、WIN=20、MIN_OBS=10 寫死於 code);4 顆借券/高點族之產生器**根本不在 repo**;`validate_feature_candidates.py` 與 `verify_interaction_candidates.py` 各自內建另一組寫死候選名(前者 pb_xsec_rank/pb_industry_demean/pb_self_pctile_252d/inst_govbank_divergen | 新增 `scripts/migrate_candidate_recipe_ddl.py` 建 `candidate_recipe(recipe_id BIGSERIAL PK, feature VARCHAR(255) UNIQUE NOT NULL, recipe_kind VARCHAR(32) NOT NULL CHECK(recipe_kind IN ('window_agg','zscore_product','zscore_diff','xsec_rank','self_pctile','ols_resid','log1p','industry_demean')), legs JSONB NOT NULL, params | 新表 candidate_recipe;新增 scripts/build_candidate_values.py + scripts/migrate_candidate_recipe_ddl.py;build_interaction_candidates.py 之純函式抽進 sr |
| S | **coverage_snapshot 落後 12 個 feature,SUNSET 進度自陳與 DB 不同步**——最新 `evolution_coverage_snapshot.run_id=6`(共 39 列:mapped 35/missing 3/blocked_div 1),但 principle_factor_map 現有 51 distinct feature(07-28 加 19 列、07-29 加 27 列)。run 10 是 human_promotion 事件列、未跑閘故未拍快照。故任何以 coverage_snapshot 為據之進度陳述都會漏掉 12 顆(含全部 7 顆 INTERACT) | `venv/bin/python scripts/run_philosophy_evolution.py --local-gates --dry-run` 先看新 map 之閘裁決分佈,樹淨後正式 `--local-gates` 拍新 run 之 coverage_snapshot;並於 `verify_evolution_acceptance.py` 增一條:最新 coverage_snapshot 之 feature 數必須 == `select count(distinct feature) from principle_factor_map`,否則 FAIL(防快照靜默過期) | 零 schema 變動;改 scripts/verify_evolution_acceptance.py 增一條 |

**機器可判驗收（可預先凍結）**
- prodset 成長(SUNSET (b) 門檻 >2):`psql -tAc "select count(*) from evolution_production_feature_set where set_status='active'"` ≥ 3。現況基線 = 2(實測 verify_prodset_hotpath --check:['inst_cumflow_position_120d','lending_fee_rate_mean_20d'])
- 每顆 active 成員符號一致:`venv/bin/python scripts/verify_sign_consistency.py --run --features <全部 active,逗號分隔>` 輸出「合計:PASS N/FAIL 0/不可判 0」且 N == active 顆數(UNJUDGEABLE 記為未通過,非通過)
- 每顆 active 成員可複現:`grep -rl "<feature>" src/augur/features/*.py` 非空,且 `scripts/build_feature_panel.py --panels <該特徵全部 panel>` 重算後,與 feature_values 現值逐 (panel_date,stock_id) 差異絕對值 > 1e-6 之列數 = 0
- 四關落帳完整:對每顆進入 prodset 之 feature,`select count(distinct gate) from candidate_gate_result where feature=X and verdict='PASS'` = 5(G1-ASOF/G2-HACT/G3-DELTA/G4-SIGN/G5-ECON);且 apply_evolution_promotions.py 對缺任一 PASS 之 promote 回 exit≠0(以刻意缺一列之 dry-run 反向驗證閘真的會拒)
- 一鍵迴圈真的包含候選與四關:`python -c "import ast,pathlib; t=ast.parse(pathlib.Path('scripts/run_evolution_iteration.py').read_text())"` 後檢 STEP_CMD['I1'] 與 STEP_CMD['I2'] 皆非 None;且 `scripts/run_evolution_iteration.py --selftest` exit 0(其自測含「步圖十步齊」與新增之 I1/I2 非 None 斷言)
- 同尺:對 feature_candidate_values 每一 distinct feature,`count(distinct panel_date)` == `select count(distinct as_of_date) from core_universe_asof`(現值 102);不等者列出即 FAIL(擋同尺陷阱)
- econ 同尺自證:run_economic_eval 兩側(--add-features 與 --drop-features)輸出之 panel hash 字串相同、n_periods 相同;不同即該次雙跑作廢(承 07-29 作廢先例,已成先驗紀律)
- 多重檢定 N 誠實:候選 econ / promotion 每跑一組配置後,`select count(*) from trial_ledger where source in ('candidate_econ','candidate_promotion')` 之增量 == 本次實跑配置數(同 config 重跑不增,由 UNIQUE 8 欄保證)
- 無停擺輪:`select count(*) from evolution_iteration_ledger where status='running' and opened_at < now()-interval '48 hours'` = 0
- 快照不過期:最新 evolution_coverage_snapshot 之 `count(distinct feature)` == `select count(distinct feature) from principle_factor_map`(現況 39 vs 51 = FAIL)
- 全域驗收不退步:`venv/bin/python scripts/verify_evolution_acceptance.py` 之 FAIL 計數 = 0 且 PASS 計數 ≥ 11(現況實測 PASS 11 · FAIL 0 · N/A 3)
- 矩陣義務:`python3 scripts/check_cmd_matrix.py` exit 0(新增之 build_candidate_values.py / run_candidate_funnel.py / migrate_*_ddl.py 於首次提交當下即含執行指令矩陣與 --selftest)
- 洩漏自稽:`scripts/build_interaction_candidates.py --audit-visibility` exit 0(revenue 15 日發布閘 + 窗永不越 panel_date 斷言全綠)
- 隔離不變式不退:`scripts/verify_prodset_hotpath.py --check` 仍印「isolation 0 違規」、predict role 對 evolution_run / promotion_queue 之 SELECT 授權皆 False

<details><summary>本線誠實界限</summary>

取證方式與誠實界限:  【live DB 實查(db)】psql 連線走 .env 之 DB_USER=augur(注意:`psql -d augur` 以 hugo 身分會 FATAL role 不存在,須帶 -U augur -h 127.0.0.1 + PGPASSWORD)。所有列數/panel 數/狀態分佈/gate_json/trigger 定義皆本次 live 查得,非讀 DDL 推測:feature_values 8,540,331 列38 特徵113 panel、feature_candidate_values 155,037 列11 候選、prodset 9 列 active=2、promotion_queue 310 列、trial_ledger 32 列、principle_factor_map 104 列51 特徵、hint 10 列全 approved、core_universe_asof 102 panel、factor_direction_ruling 僅 2 列、coverage_snapshot 最新 run_id=6。  【實跑腳本(code+實測)】本次真正執行並取其 stdout 者三支:`verify_prodset_hotpath.py --check`(PASS,active n=2)、`verify_sign_consistency.py`(無參數現況:候選 11、map 方向全覆蓋)、`verify_evolution_acceptance.py`(PASS 11 · FAIL 0 · N/A 3)、`python -m augur.core.heavy_slot`(持鎖 backend pid=[3136793])。⚠ 系統 python3 無 numpy,一律須用 `/home/hugo/project/augur/venv/bin/python`。  【只讀 code 未實跑(code)】verify_candidate_promotion.py / run_economic_eval.py / run_philosophy_evolution.py / apply_evolution_promotions.py / build_interaction_candidates.py / run_evolution_iteration.py 之行為由原始碼與 docstring 判定,**未實際跑四關或 econ**(CPU 重、且 heavy_slot 現被佔用、#28 省 usage)。故「四關若真跑會判 PASS/FAIL」一律未預言,只陳述機具存在與否。  【查無 / 誠實留白】 - 「lending_fee_rate_mean_20d 的產生器」repo-wide grep(*.py/*.sh/*.sql)**查無**——只有三處 docstring/CLI 範例字串。同樣查無:lending_fee_vw_mean_20d、days_since_high_126d、days_since_high_252d_raw、log1p_days_since_high_252d 之建值 code。G-PROM-D2 probe 報告(reports/augur_gprom_d2_probe_20260724.md)證實這些值曾被算出,但**產生它們的 script 不在 scripts/**,亦未在 git 刪除記錄中找到(僅掃近 20 commit,未窮盡全史)。 - `heavy_slot` 為 PG advisory lock,**無實體表**(`select * from heavy_slot` → relation does not exist),持有者只能由 holder_pids() 查 backend pid;未進一步確認 pid 3136793 對應哪支程式(未查 /proc)。 - evolution_deferred_work count(*)=4(id 2-5);verify_evolution_acceptance 亦報 4,一致。 - SUNSET (b) 之「active 由 2 成長」我依 audits/V2-ADOPTED-SUNSET-20260726.md §三「門檻 >2」解為 ≥3;此為文字解釋,**非我可裁**,若人裁另解則驗收判準第 1 條須改。 - `macro_regime` 是否可 as-of 安全建置未評估(未讀 src/augur/features/macro_vintage.py 內容),僅據 build_pme_fundamental_features.py docstring「不建」陳述現況。 - promotion_queue 之 pending_auto 14+2 列全屬 run 3/4(07-27 舊 run),run 6 之 PASS/PASS 一列(queue 253)已 applied;未逐列核 run 3/4 之 pending 為何未被 APPLY 消費(可能為 gate 未全綠或 kill-switch,未查 evolution_kill_switch)。

</details>

---

### 8.2 ②人類原典 KH1→KH10

*行走者②人類原典(KH1→KH10 十層) — 現況實作級盤點與可開工缺口*

**既有表（21）**：`knowledge_item`（270,736 列;其中 146,345 有 text、124,391 無 text）、`knowledge_item_text`（158,053 列 / 146,345 distinct item_id）、`knowledge_sentence`（1,811,477 列;72,408 句未嵌(影響 1,405 items)）、`knowledge_sentence_embedding`（1,737,070 列）、`knowledge_source`（3,604 列;approval_status: proposed 3,504 / active 96 / approv）、`knowledge_query`（5,220 列）、`knowledge_staging`（340,511 列;具 trigger staging_source_gate）、`knowledge_fulltext_status`（19,362 列(skip_no_oa 9,552 / skip_license 4,058 / abstract_no）、`knowledge_kh4_state`（146,432 列。answer_status: eligible 145,837 / ineligible 396 /）、`knowhow_auto_admit_state`（146,345 列(＝有 text 之 item 全覆蓋,with_text_not_in_machine=0)。dep）、`knowhow_auto_admit_gate`（1 列: auto_admit_v1, enabled=t, progressive_enabled=t, requir）、`knowhow_kh7_eligibility`（40 列 / run_id 2..6。最新 run_id=6: eligibility_pass 6 / eligibi）、`knowhow_evidence_weight`（145,837 列;confidence_band **100% 皆 high**(min score 0.720 / ）、`knowhow_synthesis_run`（145,837 列;answer_state **100% replay_logged**;query_text 145）…

**既有 script（18）**：`acquire_knowledge.py`、`promote_knowledge.py`、`harvest_knowledge.py`、`build_sentences.py`、`embed_knowledge.py`、`advance_knowledge_terminal.py`、`fetch_pd_fulltext.py, fetch_oa_fulltext.py, fetch_confirmed_fulltext.py, fetch_entity_fulltext.py`、`kh4.py`、`auto_admit.py`、`run_knowhow_auto_admit.py`、`run_knowhow_interaction_probes.py`、`eval_knowhow_interaction_probes.py`、`kh7_eligibility.py`、`evidence.py`、`synthesis.py`、`assist_admission_review.py`…

**缺口與可開工下一步（11）**

| 工 | 缺什麼 | 可開工的第一步 | 需要的表／欄 |
|---|---|---|---|
| M | KH5 擴軸 per-item 空轉:kh_axis_state=ready 佔 146,432/146,432(100%),因 kh4.py:90-94 判準為『approval=active AND domain 非空 AND source_key 非空』——即『有 domain 標籤』而非抽軸。auto_admit.py:253-266 depth==5 的 fallback 更直接『有 domain＝軸起步』即 pass。全庫無任何軸持久化表(to_regclass 對 knowledge_query_axis / knowhow_query_axis / knowhow_axis_cache 三名皆 NULL),retri | (1) 新增 scripts/migrate_kh5_axis_ddl.py 建 knowhow_item_axis;(2) 新增 src/augur/knowledge/axis.py,函式 extract_axes(cur, item_id) -> list[dict],軸來源限 DB 策展(retrieve_glossary / knowledge_topic_alias / knowledge_domain_map / principle_domain_map,守 #29b 不寫死 dict)+ selftest;(3) 改 src/augur/knowledge/auto_admit.py depth==5 分支:刪除『有 | 新表 knowhow_item_axis(axis_id bigserial PK, item_id int FK→knowledge_item ON DELETE CASCADE, axis_kind text NOT NULL CHECK(axis_kind IN ('dom |
| M | KH6 交互投影 per-item 亦空轉且含庫級假綠:interaction_state=ready 判準為 has_embedding(kh4.py:97-99);更嚴重者 auto_admit.py:268-283 fallback 為『SELECT 1 FROM knowhow_interaction_probe_run LIMIT 1』——只要全庫存在任一探針批次(現 7 列),**所有** item 一律 pass KH6。實況:15 支探針 / 38 筆結果 撐起 145,837 個 depth≥6 item。符合記憶『防呆機制自己靜默失效』之判斷句(這機制若壞了會不會安靜變綠燈?→會)。 | (1) 新增 scripts/migrate_kh6_item_probe_link_ddl.py 建 knowhow_item_probe_link;(2) 改 scripts/run_knowhow_interaction_probes.py:於寫 knowhow_interaction_probe_result 的同一 transaction,對每筆命中句所屬 item 寫 link 列(contributed=true 者為真投影);(3) 改 auto_admit.py depth==6:刪除庫級 LIMIT 1 fallback 與 has_embedding fallback,改為要求該 item_id 在 knowh | 新表 knowhow_item_probe_link(link_id bigserial PK, item_id int FK→knowledge_item, probe_id text FK→knowhow_interaction_probe, run_id bigint, h |
| M | KH7 對抗裁決是庫級、非 per-item:auto_admit.py:285-322 之註解自陳『庫級』,規則為『最新 run_id 若存在任一 eligibility_pass 則 pass』。live 最新 run_id=6 有 6 筆 pass → 145,837 個 item 全數繼承 depth 7,而那 6 筆裁決全是關於 AI/太陽能探針、與絕大多數 item 無關。另 contradiction_found 狀態雖入 DDL CHECK 卻從未產生(0 列),矛盾模板在 KH7 計畫 §line23 明列『S1 不實作』。 | (1) 新增 scripts/migrate_kh7_per_item_ddl.py 為 knowhow_kh7_eligibility 加 item_id int NULL FK→knowledge_item + 索引 (item_id, run_id DESC);(2) 改 scripts/run_kh7_eligibility.py 增 --per-item 模式:對 probe_result 每筆命中句回推 item_id 寫入裁決列;(3) 改 auto_admit.py depth==7:要求該 item_id 存在裁決列且 status='eligibility_pass';(4) 新增矛盾模板:於 knowhow_e | 零新表;knowhow_kh7_eligibility 加 1 欄(item_id)+1 索引;knowhow_eval_suite_case 增列(策展資料,零 schema 變動)。 |
| M | KH8 判別器不判別(結構性假綠):knowhow_evidence_weight 145,837 列 confidence_band **100% high**,min evidence_score 0.720,medium/low/absent 三帶全空。成因可從公式直接推:輸入 has_text/has_sentence/has_embedding/kh4_ok 在 item 抵達 depth 4 時已全部必為真,故 score 恆 ≥0.35+0.25+0.25+0.15−0=1.0 之區間,band 恆 high。且公式完全未用已存在且已填值的判別維度——knowledge_source.authority_tier(有  | 改 src/augur/knowledge/evidence.py 之 evaluate_item_evidence():加入三項在 depth 8 仍會變動之判別項——(a) authority 權重 = f(knowledge_source.authority_tier),internal 給最低;(b) fulltext 深度 = abstract-only(knowledge_fulltext_status.status LIKE 'abstract%')降權;(c) 真實 citation_count 分布(現 cite_norm=min(n/5,1) 在句多時飽和,改為分位數化)。**判準必須在重跑前凍結寫入計畫書**, | 零新表(authority_tier 已是 knowledge_source 既有欄、已填值;fulltext_status 既有表)。建議加 knowhow_evidence_weight.formula_version text NOT NULL DEFAULT 'v1' 以 |
| M | KH9 合成回放同為全綠且非真查詢:knowhow_synthesis_run 145,837 列 answer_state **100% replay_logged**,postmortem_needed 0 列;query_text 有 145,837 個各異值＝每 item 自造一句合成查詢(非真實使用者問題)。母計畫 §KH9 驗收『不同 run 可比較』『系統可回看為何這次這樣回答』在 per-item 一次性列上無法成立(無同一問題的多 run 可 diff)。 | (1) 新增 scripts/migrate_kh9_replay_case_ddl.py 建 knowhow_replay_case,種子取自既有 advisor_probe_candidate(9 列)與 scripts/mine_advisor_probes.py 產出;(2) 改 scripts/replay_knowhow_run.py 增 --from-case 模式:以 (case_id, run_id) 為單位寫 replay,replay_json 記檢索命中、KH8 權重、KH7 裁決、最終 answer/decline;(3) 比照 KNI-S3 之 expect_decline 手法,種子中含 ≥1 筆刻意不 | 新表 knowhow_replay_case(case_id text PK, query_text text NOT NULL, expected_role text NOT NULL CHECK(expected_role IN ('answerable','expect_d |
| M | KH10-ENABLE-S1 完全未實作:三表已建但全 0 列(KH10-ENABLE-S0-CLOSED-20260730),計畫 §6-S1 指名之三支檔案經 ls 實查**皆不存在**——scripts/collect_evolution_candidates.py、scripts/review_evolution_candidates.py、src/augur/knowledge/evolution.py。且 gate.max_auto_depth=9 夾住,depth 10 永為 0 列。最新計畫(20260730:277)明示 KH10-ENABLE-S1 為未發之獨立拍板碼。 | 依 reports/augur_kh10_enable_plan_20260729.md §6-S1 實作三檔:(a) src/augur/knowledge/evolution.py — collect_candidates(cur, source_type)/record_decision(cur, candidate_id, decision, decided_by, rationale) + --selftest;(b) scripts/collect_evolution_candidates.py — 掃 knowhow_kh7_eligibility(現有 40 列可餵)/knowhow_synthesis_run/kn | 零 schema 變動(三表 S0 已建、CHECK 已齊)。 |
| S | KH10 人簽保證是假的:knowhow_governance_ledger.decided_by 為 **DEFAULT 'HUMAN'**,任何機械 INSERT 未帶該欄即自動讀作 'HUMAN'。live pg_trigger 掃描 knowledge*/knowhow* 全部表,只有 knowledge_staging(staging_source_gate) 與 knowledge_unit(trg_ku_touch) 有 trigger——KH10 三張治理表**零 honesty guard**,DELETE 亦無阻擋(僅 FK 保護子表)。此正犯記憶『不代打人簽』之判斷句(這欄位是不是為了證明某事由人做的?→是)與 | 新增 scripts/migrate_kh10_governance_guard_ddl.py,比照既有 scripts/migrate_honesty_guards_ddl.py 之 GUC 通行證模式:(1) ALTER TABLE knowhow_governance_ledger ALTER COLUMN decided_by DROP DEFAULT;(2) BEFORE INSERT trigger 要求 current_setting('augur.human_decision','t') 非空且等於 NEW.decided_by;(3) BEFORE DELETE/UPDATE trigger 一律 RAISE EX | 零新表;1 個 DROP DEFAULT + 3 個 trigger + 1 個 plpgsql 函式。 |
| S | 107,540 個 item 無全文且**無任何 fulltext_status 帳** = silent drop。live 實算:no_text_no_ftstatus 107,540 vs no_text_has_ftstatus 16,851(合計 124,391 無 text item)。來源分布 crossref 74,876 / generic_json 26,924 / openalex 6,899 / openlibrary 4,190 / semantic_scholar 3,831 / arxiv 3,790 / internet_archive 3,535 / osti 321 / manual_file 2 | (1) 新增 migration 擴 chk_fulltext_status CHECK 增值 'never_attempted';(2) 改 scripts/advance_knowledge_terminal.py 增 --reconcile-missing-status 模式:對每個『無 knowledge_item_text 且無 knowledge_fulltext_status』之 item INSERT 一列 status='never_attempted', reason 記 adapter 與判定時點(冪等 ON CONFLICT DO NOTHING、分批 --limit);(3) 於 scripts/verif | 零新表;knowledge_fulltext_status 之 chk_fulltext_status CHECK 增 1 個容許值。 |
| S | KH2 預審層近乎空轉:knowledge_admission_assist 僅 26 列,對照 knowledge_source 之 3,504 筆 proposed 來源＝覆蓋率 0.7%。憲章 v1.48.0 已廢 approve 唯人、改『一律准入＋漸進精準』,故 KH2 的定位需重新對焦(原設計前提『來源仍需人裁』已不成立),但目前既未重新定義亦未擴量。 | 先產一份 KH2 重定位判斷(屬理解層、須 Steward 拍板):v1.48.0 後 KH2 是否改為『排序與風險旗供 harvest 優先序』而非『人裁前預審』。可開工之機械側:改 scripts/assist_admission_review.py 增 --backfill-all --limit N 對 proposed 來源批次打分,並在 knowledge_admission_assist 加 assist_purpose text CHECK('pre_human_review','harvest_priority') 以誠實區分兩種語意。 | knowledge_admission_assist 加 1 欄 assist_purpose;其餘零 schema 變動。 |
| S | 508 個 item 卡 depth 3、72,408 句未嵌(影響 1,405 items)、interaction_state pending 510。LSRS-S23 已 APPROVED(audits/LSRS-S23-APPROVED-20260730.md)但**無 CLOSED audit**→在飛未收官。此為已授權執行項,非新設計。 | 執行既有授權鏈(零新碼):python scripts/embed_knowledge.py --gap-fill → python -m augur.knowledge.kh4 refresh → python scripts/run_knowhow_auto_admit.py --until-empty --apply-up-to 9;完成後補 audits/LSRS-S23-CLOSED-<date>.md。 | 零 schema 變動。 |
| S | 探針庫過窄使 KH5/KH6 擴軸宣稱無法規模化驗證:knowhow_interaction_probe 僅 15 列(arity 2 共 14、arity 3 共 1、arity≥4 為 0,CHECK 容許至 8);retrieve_glossary 僅 13 列。母計畫 §KH5 驗收『新三元/n 元議題靠 INSERT 即可擴題、不需新增 if 分支』目前僅由 1 支三元探針支撐,無四元以上實證。 | 純資料策展、零改碼(#29b):對 knowhow_interaction_probe INSERT ≥6 支新探針(其中 ≥2 支 arity=4、≥1 支 arity=5),axes 取自 knowledge_domain(42 列)與 principle_domain_map(8 列)既有策展值;同步對 retrieve_glossary INSERT 擴詞;再跑 scripts/run_knowhow_interaction_probes.py --show 與 eval_knowhow_interaction_probes.py 驗證零改碼即生效。 | 零 schema 變動(arity CHECK 已容許 2..8、axes jsonb 已在)。 |

**機器可判驗收（可預先凍結）**
- G1 KH5:對 depth≥5 之 item,100% 在 knowhow_item_axis 有 ≥1 列且 axis_kind<>'domain';且『僅憑 domain 標籤即通過』之比例 = 0%(SQL 可判)。python -m augur.knowledge.axis --selftest exit 0。
- G1 KH5 非退化鎖:knowhow_item_axis 之 axis_kind 至少 3 種非空;單一 axis_kind 佔比 ≤80%(防再現『100% ready』式空轉)。
- G2 KH6:count(item at depth≥6) == count(distinct item_id from knowhow_item_probe_link where contributed) ;且 grep 確認 auto_admit.py depth==6 分支已無 'knowhow_interaction_probe_run LIMIT 1' 庫級 fallback(字面掃描 exit 0)。
- G3 KH7:select count(*) from knowhow_kh7_eligibility where item_id is null and run_id=(最新) = 0;且每個 depth≥7 之 item 有自己的 eligibility_pass 列。矛盾模板:knowhow_eval_suite_case 中 role='expect_contradiction' ≥3 列,且 knowhow_kh7_eligibility 出現 ≥1 列 status='contradiction_found'(現為 0)。
- G4 KH8 非退化(判準須在重跑前凍結入計畫書):重算後單一 confidence_band 佔比 ≤80%;four bands 中 ≥3 帶非空;所有 authority_tier='internal' 且 abstract-only 之 item band ≤ 'medium'(SQL 可判)。
- G4 反例鎖:刻意構造薄輸入 item(僅 text、無句、無 embedding)必得 band='absent' 且 evaluate_layer(8) 回 fail — 以 --selftest 單元鎖定,不靠 live 抽樣。
- G5 KH9:knowhow_replay_case ≥20 列且 provenance 可追至 advisor_probe_candidate 或 mine_advisor_probes 輸出;同一 case_id 存在 ≥2 個 run_id 之 replay 可 diff;≥1 列 answer_state='postmortem_needed' 由 expect_postmortem case 機械產出(現為 0)。
- G6 KH10-S1:scripts/collect_evolution_candidates.py 可自 knowhow_kh7_eligibility 收 ≥1 筆 candidate;三支新檔皆過 python scripts/check_cmd_matrix.py(NEED=0);argparse 全域 grep 無 '--auto-approve';knowhow_governance_ledger 列數僅因 review CLI 而增。
- G7 人簽鎖(機器可判三臂):①未設 GUC 之 INSERT → RAISE EXCEPTION;②decided_by='HUMAN' 但未設 GUC → RAISE EXCEPTION;③任何 DELETE/UPDATE → RAISE EXCEPTION。三臂皆須實測非僅讀 DDL(承記憶『防呆機制自己靜默失效』)。
- G8 誠實帳閉合:select count(*) from knowledge_item i where not exists(text) and not exists(fulltext_status) = 0(現 107,540);此斷言寫入 scripts/verify_knowledge_e2e_smoke.py 成為回歸鎖。
- G10/G11 執行收官:knowhow_auto_admit_state 中 admit_depth<9 之列數 = 0,或每筆殘留在 knowledge_kh4_state.status_reason 有非空誠實阻擋原因;knowledge_sentence 未嵌句數(items 側)= 0。
- G12 零改碼擴題實證:INSERT 新 arity≥4 探針後,run_knowhow_interaction_probes.py --show 即列出新探針且 eval 可跑,git diff 顯示 **零 .py 變動**(#29b/NHC 機械證明)。
- 全域護欄(每項皆須同時成立):零 FinMind／FRED 呼叫(FZ-keep);無 approve/activate 自動化繞路;無專題答案樹 hardcode;素養層不進預測 runtime;所有新增 script 首次提交即含執行指令矩陣(check_cmd_matrix.py NEED=0)。

<details><summary>本線誠實界限</summary>

【取證方式】live DB 為主:psql -h 127.0.0.1 -U augur -d augur(.env 之 DB_USER/DB_PASSWORD;直接 psql -d augur 會因 role \"hugo\" 不存在而失敗——後續 agent 請用此連法)。所有列數、狀態分布、CHECK 約束、trigger 掃描、\\d schema 皆 live 實查(db)。DDL 常數另比對 scripts/migrate_*_ddl.py(ddl)。判準邏輯讀 src/augur/knowledge/{kh4,auto_admit,evidence,synthesis,kh7_eligibility}.py(code)。未結項讀 reports/ 與 audits/(doc)。  【誠實界限——只讀未跑】本次**未執行任何 script**(含 --selftest / --check / runner),故『腳本可執行』一律未親驗;僅確認檔案存在與 docstring 矩陣文字。G1-G12 之 effort 估算為讀碼推估,非實測。  【查無(不編)】①`review_flag`:任務提示所指之三態欄,live 掃 information_schema 僅存在於 **philosophy_work**,**不在** knowledge_source。②`fulltext_blocked`:無此字面欄位;誠實阻擋實作為 knowledge_fulltext_status.status 之 13 值 CHECK(skip_*/abstract_*)。③軸持久化表:knowledge_query_axis / knowhow_query_axis / knowhow_axis_cache 三名 to_regclass 皆 NULL(母計畫 §9.3 建議之三類 cache 全未建)。④authority_tier 為 knowledge_source 之**欄**,非獨立表(scripts/migrate_authority_tier_ddl.py 存在但 live 無同名表)。⑤scripts/collect_evolution_candidates.py、review_evolution_candidates.py、src/augur/knowledge/evolution.py:ls 實查不存在。  【最重要的一件事】KH5/KH6/KH7 三層之 per-item 通過判準目前分別退化為「有 domain 標籤」「有 embedding 或全庫存在任一探針批次」「全庫最新 run 存在任一 pass」,其中 KH6/KH7 為**庫級**(auto_admit.py:268-283、285-322,後者註解自陳「庫級」)。故『145,837 個 item 已達 depth 9』此宣稱之真實含量僅為 KH1-KH4(檢索可答)+ KH8/KH9(per-item 但公式恆綠:band 100% high、replay 100% logged)。KH8 之 100% high 屬**結構性必然**(輸入在 depth 4 已全為真),非資料恰好優良。建議計畫書把 depth 語意誠實降級標註,並優先做 G7(人簽鎖,S)+G8(誠實帳閉合,S)兩件低風險高價值項,再處理 G1-G5 之判準硬化(涉既有 145,837 列水印退位,須 Steward 拍板)。  【與現行授權的關係】LSRS-S23 已授權未收官(G10);KH10-ENABLE-S1 為明文未發之獨立拍板碼(G6),最新計畫 20260730:279 明示「只說『做到 KH10』≠授權 LSR 放量或 KH10-S1」——計畫書不得將二者綁為一次授權。

</details>

---

### 8.3 ③思想原理 PME

*行走者③思想原理 — 哲學原理→可證偽假說→PME 四關→跨域映射（憲章 v1.47.0）之接線閉合度與機械落點*

**既有表（8）**：`philosophy_principle`（51 列；status 分布 untested 43 / sign_refuted 7 / validated 1(唯 ）、`philosophy_school`（跨域載體實例：sun_tzu(孫子→企管)、ml_predict_evolution(AI/ML→投資)、solar_s）、`principle_factor_map`（104 列／51 distinct feature／51 distinct principle。37 列有 valida）、`principle_domain_map`（8 列(business_mgmt 4＝p108/109/110/112 孫子；ai_ml 4＝p113/114/115）、`factor_direction_ruling`（2 列：days_since_high_252d=-1、range_position_120d=+1；ruled_by=）、`evolution_hypothesis_hint`（10 列全 decision='approved' 且 decided_by 齊備。其中 7 則已入 principle）、`promotion_queue`（310 列：rejected_gate/demote 251、rejected_gate/freeze 20、appli）、`philosophy_chunk / philosophy_work_text / philosophy_chunk_embedding / stock_philosophy_tag`（philosophy_chunk 126,609 列／philosophy_work_text 31,782 列／sto）

**既有 script（15）**：`evolution.py`、`run_philosophy_evolution.py`、`verify_sign_consistency.py`、`curate_pme_map_expand.py`、`curate_pme_xdom_map.py`、`curate_pme_xdom_ai_predict_map.py`、`curate_pme_xdom_solar_map.py`、`report_hint_curation_queue.py`、`sync_philosophy_principle_status.py`、`audit_philosophy_feature_coverage.py`、`report_pme_gate_diagnosis.py`、`import_isolation.py`、`migrate_principle_domain_map_ddl.py`、`apply_evolution_promotions.py`、`verify_philosophy_factors.py`

**缺口與可開工下一步（10）**

| 工 | 缺什麼 | 可開工的第一步 | 需要的表／欄 |
|---|---|---|---|
| S | 【已實犯，最高優先】canonical 方向裁決 → principle_factor_map 無機械傳播，且新策展可反向寫入。factor_direction_ruling 於 2026-07-28 16:56 由 hugo 裁定 days_since_high_252d=-1、range_position_120d=+1；但 map 現存 4 列持相反方向：map_id 189/190(p116, xdom_loop=ai_predict, created 07-28 13:52＝裁決前，可理解為殘留)與 **map_id 217/218(p123 solar_supply_invest, created 2026-07-29  | ① 新增 scripts/migrate_factor_ruling_propagation_ddl.py：建 trigger function factor_map_direction_guard() 掛 principle_factor_map BEFORE INSERT OR UPDATE OF direction — 若 EXISTS(SELECT 1 FROM factor_direction_ruling r WHERE r.feature=NEW.feature AND r.canonical_direction<>NEW.direction) 則 RAISE EXCEPTION(比照既有 factor_ruling_ | 零新表。新增 1 個 trigger function＋1 個 trigger(principle_factor_map)；三支 curate 腳本各加一次 SELECT。 |
| S | G-MAP 不驗量化域載體——憲章 v1.47.0 clause(ii)「他域原理欲入量化，須以投資域 school 下之 principle 條目為載體」在閘層零落點。run_philosophy_evolution.py:676/:745 之 g_map verdict 僅 = (coverage_class=='mapped')，另帶 coverage_class／in_feature_values 兩個診斷欄，**未 join philosophy_school 檢查 domain**。G-ISO 亦不管此事(其射程為 import／字面旁路)。唯一執行期強制是三支 curate_pme_xdom_*.py 的 Runtim | ① src/augur/philosophy/evolution.py 新增純函式 g_map_verdict(*, coverage_class: str, carrier_domain: str｜None) -> dict：carrier_domain<>'investment' 或 None → {'verdict':'FAIL','reason':'carrier_domain_not_investment'}；並在 _selftest() 加紅綠鎖。② run_philosophy_evolution.py 之 _load_maps(cur) 的 SELECT 加 JOIN philosophy_principle p U | 零新表、零新欄(philosophy_school.domain 已存在)。改 2 支既有檔＋1 個 trigger。 |
| S | V-I8 驗收(「無 code 以 domain_map join 當量化資格」，reports/augur_pme_cross_domain_evolution_enable_plan_20260728.md §5)之守衛是**自檔源碼字面斷言**，命中記憶檔「防呆機制自己靜默失效」之第四型。實作(curate_pme_xdom_map.py:200-207，另兩支同款)：src=open(__file__).read(); apply_body=src.split("def apply_seed")[1].split("\ndef main")[0]; map_loop=apply_body.split('for f, d in | 把 I8 升為全 repo 稽核：src/augur/audit/import_isolation.py 新增 QUALIFY_LITERALS = ('principle_domain_map',) 與 GATE_APPLY_PATH = ('scripts/run_philosophy_evolution.py','scripts/apply_evolution_promotions.py','scripts/evolve_cycle.py','src/augur/philosophy/evolution.py')，以既有 _string_ref_violations() 機具掛入 check_isolation() 回傳串(標 | 零 schema 變動。改 import_isolation.py(加 2 個常數＋1 行串接)＋三支 curate 腳本刪自檔 split 斷言。 |
| S | 憲章 v1.47.0 clause(i)「素養層維護基本原理×應用域映射為一等素養物件（**可檢索**、帶真實文獻 citation）」——「可檢索」零落點。principle_domain_map 目前是唯寫表：全 repo 讀取者僅 setup_predict_role.py(:53 授權清單)與三支 curate 腳本自己的 upsert 存在性查詢；grep principle_domain_map／domain_map 於 src/augur/philosophy/retrieval.py、src/augur/advisor/*.py、scripts/query_philosophy.py 命中數 0。8 列跨域注記(孫子 | scripts/query_philosophy.py 新增 --domain-map [--domain X] [--principle-id N] 子命令：SELECT d.domain,d.note_kind,d.application_note,d.citation,p.statement,s.name FROM principle_domain_map d JOIN philosophy_principle p USING(principle_id) JOIN philosophy_school s ON s.school_id=p.school_id；並在 src/augur/philosophy/retrieval.p | 零 schema 變動(表與 8 列已在)。改 query_philosophy.py＋retrieval.py 各加一讀路徑。 |
| M | 跨域計畫 E 階段評測尺未建：reports/augur_pme_cross_domain_evolution_enable_plan_20260728.md §4.2 列為「**新** scripts/report_pme_xdom_gate_eval.py — 異域 map 過閘專表(map_id×來源閉環×verdict)；對照同窗隨機／既有 investment map 基線」，ls 確認該檔不存在。因此「異域假說是否真過閘」目前無可複現數字，只能靠 promotion_queue 生資料人工判讀；§5 之 V-EVAL(數字須出自 run/DB)與 V-ORTH(禁用顧問 cite 率當 G-PROM PASS)無機械尺可 | 新增 scripts/report_pme_xdom_gate_eval.py(需含執行指令矩陣＋--selftest，CLAUDE #18/#29d 向前生效)：輸入 --run-id(預設 max(evolution_run))；GROUP BY provenance->>'xdom_loop'(sunzi_mgmt/ai_predict/solar/NULL=investment 基線)× gate verdict，輸出每迴圈 n_map／G-PROM PASS 率／G-ECON PASS 率／雙綠率／FAIL_SIGN 率。**依記憶檔「評測樣板地板」鐵律，須同時輸出三對照臂**：ceiling(既有 investment  | 零新表(讀 promotion_queue.gate_json＋principle_factor_map.provenance 即足；計畫 §4.1 已明示不產新表、來源標籤用 provenance JSONB)。 |
| M | philosophy_principle.hypothesis(自由文本假說)與 principle_factor_map(結構列)無對帳。hypothesis 以散文寫死特徵名與方向，例 p116=「range_position_120d 越低、days_since_high_252d 越高 → 未來報酬假說（位置−／…」——與 07-28 canonical ruling 恰好相反，而該文本至今未動、p116.status 仍 untested。無任何機械檢查驗「hypothesis 提及的特徵集合 == 該 principle 的 map 列集合」「hypothesis 敘述的方向 == map.direction」。後果：原 | 新增 scripts/verify_hypothesis_map_agreement.py(唯讀＋--selftest)：對每 principle，以 feature 白名單(SELECT DISTINCT feature FROM principle_factor_map ∪ feature_values)對 hypothesis 做字面掃描抽出提及特徵，比對該 principle 的 map 列；輸出三類 — hypothesis_mentions_unmapped(散文有、map 無)、mapped_not_in_hypothesis(map 有、散文無)、direction_phrase_conflict(散文含「越低/越高 | 零 schema 變動。純新增 1 支唯讀 script。 |
| S | PME 閘與 SIGN-B 尺皆未排程，僅手動。crontab -l 顯示：run_evolution_chain.sh(01:30)、pull_desktop_evolution_delta.sh(每 2h)、report_triple_evolution_week.py(週日 09:00)、run_raw_evolution_iteration.py(週六 09:00)、run_evolution_iteration.py(平日 23:00)。對 run_evolution_chain.sh grep run_philosophy_evolution｜verify_sign_consistency 命中數＝0。即：策展新增 ma | 在 run_evolution_chain.sh 尾段(verify_eval_set_validity.py 之後)串入兩支唯讀哨兵：venv/bin/python scripts/verify_sign_consistency.py 與 venv/bin/python scripts/report_pme_gate_diagnosis.py --stdout-only，輸出附加至 $HOME/logs/pme_sentinel.log；閘的實跑(run_philosophy_evolution.py --local-gates)因會寫 evolution_run/promotion_queue 屬放量，**先不入 cron**， | 零 schema 變動。改 run_evolution_chain.sh 加 2 行(cron 表本身不動)。 |
| S | 3 則已 approve 的 hint 未入 map，燃料線斷在人簽節點：raw-h-3691b263、raw-h-601020c5、raw-h-c4e9eef6(decision=approved、decided_by 齊備，但 principle_factor_map 無對應 hint_id 列)。已有 report_hint_curation_queue.py --stanzas 能產 ready-to-fill 策展段，缺的是人填【原理陳述／可核文獻／方向±1】三處。此為設計上的必要人閘(direction/principle_id NOT NULL＝假說著作權歸人)，非程式缺陷，但目前無「approved 未入 map 之 | ① 由 hugo 跑 python scripts/report_hint_curation_queue.py --stanzas 取這 3 則草稿、人填後貼入 curate_pme_map_expand.py 之 SEED，--apply 入 map(AI 不得代填 direction／principle 歸屬)。② 程式側可做的是可見度：report_hint_curation_queue.py 無參數輸出加一行「approved 未入 map：N 則，最久滯留 D 天(min(created_at))」，並在 report_pme_gate_diagnosis.py 摘要同步顯示。 | 零 schema 變動(evolution_hypothesis_hint.created_at 已有)。 |
| M | 14 列 map 指向 feature_values 不存在的特徵，污染覆蓋統計。清單(db 實查)：close_x_sbl_balance_level、days_since_high_126d、days_since_high_252d_raw、inst_gross_x_money_change、inst_gross_x_turnover_change、inst_gross_x_turnover_level、inst_gross_x_volume_change、inst_gross_x_volume_level、lending_fee_vw_mean_20d、log1p_days_since_high_252d、macro_regi | principle_factor_map 加一欄記錄生命週期狀態，取代靠 feature_values 存在性反推：ALTER TABLE principle_factor_map ADD COLUMN lifecycle text NOT NULL DEFAULT 'active' CHECK (lifecycle IN ('active','pending_build','retired_feature'))；由新增 scripts/reconcile_map_lifecycle.py(唯讀＋--apply)依 feature_values 存在性＋verify_sign_consistency 候選名單機械標記(pending | 1 個新欄(principle_factor_map.lifecycle，帶 CHECK)＋1 支新 script；不新增表。注意 CLAUDE #30：DDL 須排在任何 pg_dump 完成後。 |
| S | factor_direction_ruling → philosophy_principle.status 無同步路徑。p116(ml_predict_evolution 迭代回饋)與 p123(solar_supply_invest H6 週期高點回落)之全部已裁方向皆落在 ruling 的敗方，實質等同方向被否證，但兩者 status 仍為 untested(非 sign_refuted)。sync_philosophy_principle_status.py 之 classify_status_alignment() 分類輸入只有 status／map.validated_*／promotion_queue APPLY 證據， | ① src/augur/philosophy/evolution.py 之 STATUS_ALIGNMENT_CLASSES 增第 9 類 'ruling_contradicted'(定義：該 principle 之所有 map 列 feature 皆有 canonical ruling 且 direction 全部不符)，並在 sync_action_for_alignment() 對此類回 None(＝**不可機械 heal、須人裁**，比照 map_evidence_gate_rejected 之誠實殘留紀律，絕不自動翻 sign_refuted——status 改寫牽涉證據宣稱，屬決策層)。② sync_philosophy | 零 schema 變動。改 evolution.py(加 1 類＋自測鎖)＋sync_philosophy_principle_status.py(查詢加 JOIN)。 |

**機器可判驗收（可預先凍結）**
- 【G1-a】方向牴觸歸零可查：psql -tAc "SELECT count(*) FROM principle_factor_map m JOIN factor_direction_ruling r ON r.feature=m.feature WHERE r.canonical_direction<>m.direction" 回傳 0。凍結基線＝今日實測 4(map_id 189/190/217/218)。
- 【G1-b】反向寫入被 DB 拒：於交易中 INSERT INTO principle_factor_map(principle_id,feature,direction) VALUES(123,'range_position_120d',-1) 必 RAISE EXCEPTION 且 ROLLBACK 後列數不變；同一 INSERT 在 SET LOCAL augur.honesty_write=on 下仍拒(方向牴觸不開豁免，區別於 ruling 表自身之改裁豁免)。
- 【G1-c】curate 腳本自守：venv/bin/python scripts/curate_pme_xdom_solar_map.py(dry-run 預設)輸出含 n_skip_ruling≥1 且明列被拒 feature 名，不整批 abort。
- 【G2-a】g_map_verdict 純函式紅綠：python -m augur.philosophy.evolution --selftest exit 0，且自測含斷言 g_map_verdict(coverage_class='mapped', carrier_domain='business_mgmt')['verdict']=='FAIL' 與 carrier_domain=None → 'FAIL'(fail-closed)。
- 【G2-b】非投資載體無法過閘：以 dry-run 對一個 domain='business_mgmt' school 下的合成 map 列跑 run_philosophy_evolution.py --local-gates --dry-run，gate_json['G-MAP']['verdict']=='FAIL' 且 all_gates_green(gate_json) is False。
- 【G3】I8 升級為 repo 級：python -m augur.audit.import_isolation exit 0；且人為在 scripts/run_philosophy_evolution.py 插入字串 'principle_domain_map' 後重跑，exit 1 並輸出含標籤 'qualify' 之違規行(改回後 exit 0)。此測證明守衛掃的是閘路徑、非自己。
- 【G4】可檢索性成立：python scripts/query_philosophy.py --domain-map 回傳 8 列(＝principle_domain_map 現存列數，凍結基線 8)，每列同時含 citation 非空與 note_kind ∈{verbatim_quote,human_authored}；且輸出文字含「非量化資格」註記字樣。
- 【G5-a】E 尺存在且可個別執行：python scripts/report_pme_xdom_gate_eval.py 無參數 graceful(印指令矩陣或安全預設、無裸 traceback)；--selftest exit 0；python3 scripts/check_cmd_matrix.py exit 0(新檔含執行指令矩陣，CLAUDE #18/#29d)。
- 【G5-b】三對照臂齊備(記憶檔「評測樣板地板」鐵律)：報告輸出同時含 ceiling(investment 基線)／floor(隨機 direction 置換)／mismatched(feature×principle 錯配) 三臂之 PASS 率；**若 floor 臂 PASS 率 ≥ 異域臂 PASS 率，判本尺無鑑別力、不得用其數字宣稱異域假說過閘**(預先凍結之否證條件)。
- 【G5-c】數字可溯源：報告每個數字附 run_id 與來源表名，且 report 內 n_map 分組合計 == psql count(*) FROM principle_factor_map(凍結基線 104)。
- 【G6】對帳器可跑且射程誠實：python scripts/verify_hypothesis_map_agreement.py exit 0(唯讀)；輸出必列出 p116 於 direction_phrase_conflict 類(以今日已知事實為凍結正例——p116 hypothesis 敘述方向與 canonical ruling 相反)；docstring 明載「純字面掃描、不做 NLP 語意推斷」。
- 【G7】哨兵入鏈：grep -c 'verify_sign_consistency' run_evolution_chain.sh ≥1；chain 執行後 $HOME/logs/pme_sentinel.log 出現當日時戳與「map 無 validated_*: N 列」計數行(N 今日凍結基線＝67)。
- 【G8】滯留可見：python scripts/report_hint_curation_queue.py 無參數輸出含「approved 未入 map：3 則」(今日凍結基線 3＝raw-h-3691b263／raw-h-601020c5／raw-h-c4e9eef6)，且列出最久滯留天數。
- 【G9】lifecycle 分母誠實：ALTER 後 psql -tAc "SELECT lifecycle,count(*) FROM principle_factor_map GROUP BY 1" 之 pending_build+retired_feature 合計 == 14(今日凍結基線)；audit_philosophy_feature_coverage.py 覆蓋率輸出同時印「排除 retired 後分母」與「原始分母」兩數，不只印一個。
- 【G10】ruling_contradicted 類上線且 fail-closed：python -m augur.philosophy.evolution --selftest 含斷言 len(STATUS_ALIGNMENT_CLASSES)==9 且 sync_action_for_alignment('ruling_contradicted') is None(不可機械 heal)；python scripts/sync_philosophy_principle_status.py 輸出將 p116、p123 歸入該類；即使加 --apply 亦不改動此二列 status(以 apply 前後 SELECT status 相
- 【橫向-憲政不變式】三條共同不變式回歸不得鬆動：(a) principle_domain_map 之兩 CHECK 仍在(source_type<>'ai_generated'、note_kind 封閉二值)——以 psql \d 驗；(b) 全 principle 之載體 school.domain 皆 'investment'——SELECT count(*) FROM philosophy_principle p JOIN philosophy_school s USING(school_id) WHERE s.domain<>'investment' 回 0；(c) 閘閾不降——DEFAULT_GATE_CONFIG 之 m

<details><summary>本線誠實界限</summary>

取證方式與界限，逐項誠實交代：  **(1) DB 為 live 實查、非讀 DDL 推測。** peer auth 下 `psql -d augur` 失敗(role hugo 不存在)，改用 .env 之 DB_USER/DB_PASSWORD 走 TCP：`PGPASSWORD=augur psql -h 127.0.0.1 -U augur -d augur`。所有列數、status 分布、方向牴觸、created_at vs ruled_at 時序、觸發器定義(pg_get_functiondef)皆為 2026-07-30 當下 live 結果，非 DDL 推論。全程唯讀，零寫入、零 DDL、零 API。  **(2) G1 的「裁決後新增違反」是時序實證，不是推斷。** map_id 217/218 created_at=2026-07-29 16:41:05，factor_direction_ruling.ruled_at=2026-07-28 16:56:17 — 相差約 23.7 小時。配合 grep 證實 curate_pme_xdom_solar_map.py 不讀該表(全 repo 讀者僅 3 支，均非 curate)。此為本次最硬的一則發現。  **(3) 憲章條文出處需注意版本。** 任務提示的 v1.47.0 已被 superseded：docs/ 下同時有 系統架構大憲章_v1.47.0.md 與 _v1.49.0.md，我引的「跨域原理映射準則」全文取自 **v1.49.0 第 163 行**(現行有效)；v1.47.0 在 v1.49.0 修訂表第 388 行標記為 SUPERSEDED —— 即該準則條文本身在 v1.49.0 仍生效，只是引入它的那個版本號已被後續版本取代。constitution/ 目錄(META-CONSTITUTION 與 41 份 RULING)grep 「跨域」命中 0 —— 此準則住領域憲章(L6 下層)，不在上位 AUGUR-MC，屬預期。  **(4) 未實跑的部分(明說，不佯稱)。** `verify_sign_consistency.py --run` 未跑(需重算 as-of IC＋5 bootstrap，耗時長)；只跑了無參數唯讀模式，故「候選 11 顆及其 map 方向」為實測，但**各候選的 PASS/FAIL/UNJUDGEABLE 判定我沒有實測數字**——「p116/p123 那兩顆恆為 UNJUDGEABLE」是依其 docstring 明文判式(「多列方向衝突＝UNJUDGEABLE」)＋DB 實測衝突事實所作的推論，標為推論而非實測。`run_philosophy_evolution.py`、`apply_evolution_promotions.py`、`sync_philosophy_principle_status.py`、`audit_philosophy_feature_coverage.py`、`report_pme_gate_diagnosis.py` 均未執行(會寫帳本或耗時)，其行為描述出自源碼與 docstring 逐行閱讀。`apply_evolution_promotions.py` 我只由 grep 確認它是 promotion_queue／build_gate_json 消費者，**未讀其 docstring 與函式體**——它是 APPLY 最後一哩，建議後續補讀。實跑者僅二：`curate_pme_xdom_map.py --selftest`(19 項全綠)、`verify_sign_consistency.py`(無參數)。  **(5) 一個「看似缺口、實為設計」的澄清 —— 避免誤導下游計畫。** 四支 curate_pme_*.py 內含 hardcoded SEED 常數(MAP_E012_SEED／XDOM_SUNZI_MGMT_SEED／PRINCIPLES 等)，初看像 CLAUDE #29(b)「repo 檔＝另一種 hardcode」違規。**但這是刻意的憲政設計**，依據＝report_hint_curation_queue.py docstring 原文：「map 的 direction/principle_id 皆 NOT NULL 是憲政設計(每列＝繫於原理的有向假說)…方向與原理歸屬＝假說著作權＝人…人填完後入 SEED(**入 git＝人簽軌**)」。故我**不**把它列為 gap。殘留的真問題只是 #29(c) 收斂性：四支 350–491 行高度雷同的腳本(各自重寫 upsert＋自測＋domain 檢查)，這也正是 G1/G2 兩個守衛「逐檔漏抄」的結構成因 —— 若未來要收斂為單一參數化引擎，須設計上保住「SEED 入 git＝人簽」這條性質，不可為了資料驅動把假說搬進 DB 而消滅人簽軌。此項我列為觀察、未寫成 gap，因它牽涉治權設計取捨(決策層)。  **(6) 整體閉合度判讀。** 原理→假說→四關這條鏈**結構上已閉合**(51 原理→104 有向映射→七閘→queue→apply→prodset，且 310 列 queue 中 271 列 rejected_gate＝閘真的在擋、不是橡皮圖章；37/104 有 validated_* ＝誠實未飽和)。真正的缺口集中在**橫向一致性守衛**，而非鏈本身：ruling↔map(G1)、憲章 clause(ii) 之閘層落點(G2)、V-I8 守衛射程(G3)、clause(i) 可檢索(G4)、E 階段評測尺(G5)。其中 G1 已造成 live 資料違反已簽裁決，G2/G3 是「現在合規但無機械保證」——兩者皆命中記憶檔「防呆機制自己靜默失效」的判斷句：**這機制若壞了會不會安靜變綠燈？** G2、G3 的答案都是會。  **(7) 查無項(不編)。** scripts/report_pme_xdom_gate_eval.py 不存在(ls 確認)。principle_domain_map 於檢索層命中 0(grep 確認)。crontab 及 run_evolution_chain.sh 內 run_philosophy_evolution／verify_sign_consistency 命中 0。stock_philosophy_tag 0 列(表在、從未使用，本主題未深究其設計意圖)。  **(8) 一則工具面小事。** 用 `NOT EXISTS` 對 feature_values(約 2.5M 列)查死特徵會逾時 120s；改寫為 `WITH fv AS (SELECT DISTINCT feature FROM feature_values) … LEFT JOIN` 後數秒完成。後續寫覆蓋率 script 時建議沿用此寫法。

</details>

---

### 8.4 ④AI 能力宣稱 LAIEVO

*行走者④AI 能力宣稱(本地模型自我進化 LAIEVO)——A′ 判決後之下一載具、訓練語料來源、權重鏈(convert_lora_to_gguf)、評測尺之防樣板地板*

**既有表（13）**：`local_model_eval_item`（252 列 = v1 集 4183475c5089(120 題:L1_RETRIEVED/L2_NO_RETRIEVAL）、`local_model_eval_run`（57 列;尺系譜 f3075238eb55→0646872fdce7→ef142e9374c1→35aeffc3e160）、`local_model_eval_set_check`（0 列(空表)）、`local_model_gold_sample`（745 列;來源 knowledge_item 618 / column_catalog 67 / field_corr）、`local_model_version`（4 列全為 prompt pack(pp_72cfaf5950ad/pp_7c553198837a/pp_a945296）、`evolution_prereg_gate`（1 列 V2-SUNSET;deadline 2026-10-31(今日起 93 天);criteria_sha=65e）、`local_ai_iteration_ledger`（**0 列**;對照 evolution_iteration_ledger 4 列(全 axis='tw')、raw_e）、`evolution_kill_switch`（4 列;scope=global/tw/lai/raw,state 全 'clear'）、`knowledge_capability_charter`（**0 列**(空表)）、`advisor_distill_context / advisor_distill_question / advisor_distill_seed_topic`（334 / 334 / 46 列）、`deliberation_model_probe / deliberation_model_agreement`（18 / 5 列）、`knowhow_eval_suite_case`（4 列）、`model_registry`（16 列）

**既有 script（16）**：`eval_local_model.py`、`behavior_rubric.py`、`evidence_protocol.py`、`verify_evolution_acceptance.py`、`build_eval_set.py`、`report_post_batch_verdicts.py`、`evolve_cycle.py`、`verify_eval_set_validity.py`、`report_triple_evolution_week.py`、`evolve_self_seek.py`、`heavy_slot.py`、`run_evolution_chain.sh`、`evolution_ledger_ddl.py`、`migrate_local_model_eval_ddl.py`、`advisor_distill_teacher.py`、`run_raw_evolution_iteration.py`

**缺口與可開工下一步（16）**

| 工 | 缺什麼 | 可開工的第一步 | 需要的表／欄 |
|---|---|---|---|
| S | A′(A13) 結構性不可達:A13 之 SQL 帶 `AND NOT is_invalid`,而 is_invalid=(n_valid<n_items) 是全有全無旗標。現行 T1200 尺(b6e5208ef821)之 behavior 唯一 run ev_8189862035e9ab 為 123/132(9 題 done 為空=逾時)→ is_invalid=true → A13 判 N/A。live 實跑 `--only A13` 回「v2 集尚無有效受測 run(批跑進行中)」。全表 LLM 臂 is_invalid:behavior 6 true/2 false(2 false 皆在舊 v1 集)、grammar 4  | 改 /home/hugo/project/augur/scripts/verify_evolution_acceptance.py 之 A13 段(216–256 行):(1) 拿掉 `AND NOT is_invalid`;(2) per_item 聚合時逐 cell 計 n_valid_cell/n_items_cell,cell 有效率 < 預凍值(建議 0.90)即該 cell 判 incomparable(非通過);(3) 同時改 /home/hugo/project/augur/scripts/eval_local_model.py 之 run_arm INSERT 補寫 n_excluded=len(items)-n_ | 零 schema 變動(n_excluded/selection_scope/n_trials 欄已存在);新增 evolution_prereg_gate 一列(gate_id='A-PRIME-VALIDITY', axis='lai', criteria 含 min_cel |
| S | 預註冊之 behavior 第 2 輪未跑:audits/V2-RUBRIC-GO-20260728.md §八 明訂 T1200 重跑集=五對照×2 + behavior×2、各恰 ×2、仍 INVALID 則誠實報告不迴圈。實查 eval_code_hash=b6e5208ef821 之臂數:ceiling/floor/shuffled/mismatched/robot 各 2、**behavior 僅 1**(2026-07-29 08:32);grammar/pack 於該尺 0 輪(audit 明示不追)。今日 07-30 無任何新 eval run | 跑 `cd /home/hugo/project/augur && venv/bin/python scripts/eval_local_model.py --arm behavior`(經 heavy_slot 單槽,須排 llama 道空窗、與 TWEVO I3 / RAWEVO 錯開);收槍後跑 `venv/bin/python scripts/report_post_batch_verdicts.py --run` 出 A′ 首判與 v2 逐格對照 | 零 schema 變動、零改碼 |
| S | 能力格比較未配對(unpaired):同一 cell 各臂以各自的有效題子集取平均。實測 C1_ZH_EXISTENCE:behavior n_f=32 而 floor n_f=36;C2P 兩者恰齊 24。tier2 設計書 §4.4 明訂主檢定為配對 McNemar,現行實作是不配對均值比大小 | 在 /home/hugo/project/augur/scripts/verify_evolution_acceptance.py 之 A13 段改為先取交集題集:對同一 (set_id, eval_code_hash, cell),取 live 與 floor/mismatched/robot 三對照臂皆有非 null f 值之 item_id 交集,再各自於該交集上取均值後比大小;交集題數 < 預凍下限(建議每格 ≥20)即判 incomparable。可加 --paired-detail 印交集題數留痕 | 零 schema 變動(per_item 已含 item_id) |
| M | A 軸(LoRA 復活之唯一理由)本身無鑑別力且樣本僅 12 題:v2 集之 A 軸只存在於 B3_AMBIGUITY,且該格 24 題中僅 truth='ambiguous' 的 12 題記 A(另 12 題 truth='unique' 記 F)。T1200 尺逐格實測 B3.A = floor **1.000**、robot **1.000**、shuffled 0.9167、behavior 0.0833——最強退化常數(BOILERPLATE_ARM 含「多筆請指明」)在 A 軸滿分。故「A 軸缺口巨大且明確」雖為真,但**A 軸上任何改善都無法與樣板區分**,照此軸訓 LoRA 即第三次踩樣板地板 | 改 /home/hugo/project/augur/scripts/build_eval_set.py:B3 之 A 軸孿生化——新增一格(建議 C3P_AMBIG_TWIN,capability class)以 zh↔en 語意鏈綁定,一半真歧義(候選 ≥2)、一半唯一實體,**兩側合記同一 A 軸**;同時改 /home/hugo/project/augur/src/augur/evolution/behavior_rubric.py 之 judge():truth='unique' 之題於 A 軸記「不得出現 MULTI_RE」(現行 unique 完全不記 A → 恆喊多筆者白拿半格)。改判準模組即換 eval_code_ | 零新表;local_model_eval_item.layer 之 CHECK 需加新格名(改 scripts/migrate_local_model_eval_ddl.py 之 CELLS_V2 常數 + ALTER CHECK) |
| S | 聚合 axis_f 已被無鑑別力格污染,直接引用即產生假宣稱:T1200 尺逐格實測 behavior vs robot——B1_FAITHFUL 0.9048 vs **0.9583(robot 勝)**、B3.F 0.4167 vs **1.0000(robot 勝)**、C1 0.6250 vs 0.5000、C2P 0.6667 vs 0.5000。聚合後 behavior axis_f=0.6742 < robot axis_f=0.6771 → 以聚合值判即零能力證據;唯 capability 兩格 behavior 嚴格勝孿生盲答上界 0.500。而 report_triple_evolution_week.py 之  | 在 /home/hugo/project/augur/src/augur/audit/evidence_protocol.py 增純函式 capability_cells_only(per_item, cell_class),並在 A13 與週報兩處呼叫端強制以 cell_class='capability' 逐格判讀;在 /home/hugo/project/augur/scripts/eval_local_model.py 之 compare()/_print_layer_matrix() 對 behavior class 之格常駐印「robot ≥ live → 本格無能力證據」;在 report_triple_evoluti | 零 schema 變動(expect->>'cell_class' 已在 local_model_eval_item) |
| M | 下一載具(1.7b QLoRA)之訓練語料**不存在**:tier2 設計書 §4.2 指定新表 local_model_behavior_sample(B1 CITE_GIVEN 300/B2 DECLINE 250/B3 DISAMBIGUATE 150/B4 TO_SQL 250 ≈950 條)——實查 pg_tables 中 local_model% 僅五張,**無 behavior_sample**。現有 745 條 gold 之拒答/消歧義樣本 0 條、僅 3 個 f-string 模板、83% 為文獻 metadata。即欲背進權重的窄塊(拒答/消歧義)在語料中完全缺席;直接用 745 條訓練會強化「永遠補一個作者+年 | (1) 新增 /home/hugo/project/augur/scripts/migrate_local_model_behavior_ddl.py 建表 local_model_behavior_sample(sample_id, kind CHECK IN ('CITE_GIVEN','DECLINE','DISAMBIGUATE','TO_SQL'), prompt, gold_behavior, source_key jsonb, gen_code_hash, contains_private DEFAULT false, created_at);(2) 新增 /home/hugo/project/augur/script | 新表 local_model_behavior_sample(DDL 概要如上);新 script 兩支(皆須含執行指令矩陣 + --selftest,CLAUDE #18 v1.30);零既有表變動 |
| S | 權重鏈零件在**當家機**全數缺席(本次親驗,非轉述):hostname=PC002-S1800;nvidia-smi command not found、torch.cuda.is_available()=False、device_count=0;venv(torch 2.4.1+cu121)**無 peft、無 trl、無 bitsandbytes、無 gguf、無 dspy**(pip list 164 包逐一 grep);~/llama.cpp、~/llama.cpp-bin、~/models/Qwen3-1.7B、~/models/lora 四者皆不存在;ollama /api/tags 僅 nomic-embed-tex | 先做零成本存在性閘:新增 /home/hugo/project/augur/scripts/verify_lora_prereq.py(唯讀、零下載),逐項印 PASS/FAIL 並 exit≠0——(a) torch.cuda.is_available() 與 mem_get_info free MiB;(b) importlib 檢 peft/trl/bitsandbytes/gguf;(c) Path 檢 ~/llama.cpp/convert_lora_to_gguf.py 與 ~/models/Qwen3-1.7B;(d) ollama /api/tags 含 qwen3:1.7b;(e) RAM available Gi | 零 schema 變動;新 script 一支(無外部依賴時 graceful SKIP 非 FAIL,守 CLAUDE #18 v1.30) |
| S | LoRA 復活記分卡第 4 條件之機器歸屬矛盾(記分卡記「⚠ 邊緣」,實為當家機 FAIL):reports/augur_laievo_pack_stall_qlora_gate_20260729.md 第 18 行以「GTX 1650 4GB、RAM 11GB 總量」對表,但該硬體屬另一台 DESKTOP(記憶 machines-two-concurrent:乙案=本機當家、DESKTOP 僅週末開)。當家機 PC002-S1800 實測:i5-10500、12 執行緒、**AVX2 only(無 AVX-512)**、RAM 11GB 總量 / **available 2GB**、零 GPU。v2 總控 §10 復活條件為「GP | 把記分卡第 4 格改為**逐機兩列**並以 verify_lora_prereq.py 實測值填:(a) PC002-S1800 = FAIL(無 GPU / RAM avail 2GB);(b) DESKTOP = 待該機實跑同一支 script 回填。若 hugo 選 DESKTOP 為載具,計畫須明列:週末窗口、跨機資料流(scripts/pull_desktop_evolution_delta.sh 已在 cron 37 */2 拉取)、以及「評測須與訓練同機同尺」之約束——eval_code_hash 含 MODEL 但不含硬體,換機不換尺卻會改變 INVALID 率 → 逾時題集不同 = 不配對 | 零 schema 變動;修記分卡(reports/ 新檔,#16 命名)+ verify_lora_prereq.py 逐機輸出 |
| M | LAI 軸無輪次帳本亦無 driver:local_ai_iteration_ledger **0 列**,而 tw 有 scripts/run_evolution_iteration.py(cron 週一至五 23:00)、raw 有 scripts/run_raw_evolution_iteration.py(cron 週六 09:00)。後果:LAI 無 gain/consecutive_no_gain → LAIEVO-STOP-N 停損無法機械觸發;無 gain_evidence → A4 驗收對 LAI 永遠無據;無 briefs_out/hints_out → 跨軸互惠(B4 賭注)在 LAI 側零落點 | 新增 /home/hugo/project/augur/scripts/run_local_ai_iteration.py,對齊既有兩支介面(--run/--partial/--close/--selftest;iteration_uid 格式 lai-YYYYMMDD-rNN 已由 verify_evolution_acceptance.py:26 之 UID_RE 預期)。步驟建議:L0 前置閘(verify_lora_prereq 或 pack 現況)→ L1 verify_eval_set_validity → L2 離線五臂(零成本必跑)→ L3 behavior 臂(heavy_slot)→ L4 A13 判讀(evid | 零新表(local_ai_iteration_ledger 已存在,欄位含 eval_set_id/eval_code_hash/n_trials/selection_scope) |
| S | 三 hash 鎖仍空轉(tier2 設計書 4 天前指出、至今未修):local_model_version 四列之 anchor_hash / eval_code_hash / gate_id 全 NULL、lora_path 全 NULL。設計本意「寫版本列時強制填,NULL 即拒絕寫入」,現行 evolve_cycle.search_packs() 之 INSERT 只填 version_id/base_model/train_sample_manifest_hash/eval_result。後果:任何版本分數皆無法機械綁回它是在哪把尺、哪個預註冊閘下取得 | 改 /home/hugo/project/augur/scripts/migrate_local_model_eval_ddl.py 加約束 `ALTER TABLE local_model_version ADD CONSTRAINT lmv_hash_lock CHECK (status='candidate' OR (eval_code_hash IS NOT NULL AND gate_id IS NOT NULL)) NOT VALID`(既有 4 列全 retired 且不得 hand-patch #12,故用 NOT VALID);同時改 evolve_cycle.py 之 INSERT/UPDATE 兩處補填 eva | 零新表;一條 CHECK(NOT VALID)+ 兩處 INSERT 補欄 |
| S | 漂移哨兵不落帳,升級條件無法計算:verify_eval_set_validity.py 已掛 run_evolution_chain.sh 第 48 行,但其自測第 223 行明文斷言自身無 INSERT/UPDATE/DELETE → local_model_eval_set_check 0 列。docstring 承諾之「連續 3 日 n_drifted>20 且無人處置 → 升級 fail-loud 阻斷 evolve_cycle」(v2 §6 Phase 2.5 中止條件)因無歷史列而不可能實現。而凍結集是對 live DB 的宣稱,gold/知識庫每日被收割 cron 餵大(07-30 仍 +119),L3/absent | 改 /home/hugo/project/augur/scripts/verify_eval_set_validity.py:新增 --record 旗標(預設仍唯讀)於複驗後 INSERT 一列進 local_model_eval_set_check(set_id, n_items, n_drifted, detail={逐題漂移清單});同步把該檔 _selftest 之「唯讀」斷言改為「預設路徑唯讀、--record 僅 INSERT 不 UPDATE/DELETE」;改 run_evolution_chain.sh 第 48 行加 --record;新增判停查詢:連續 3 個 checked_at::date 之 n_dri | 零 schema 變動(表已存在) |
| M | 唯一能產新候選的路徑仍跑在已作廢的尺上:evolve_cycle.cycle() 之 ④ 已用 `if False` 停用(考古保留),但 --search-packs 與 --eval-all 兩入口仍呼 _eval_pack → _score(CJK 雙字元組覆蓋率;親驗病灶=常數樣板 0.654 > 當時冠軍 0.492、數字全竄改仍 1.000),且 search_packs() 會 INSERT 新 local_model_version 列並把該尺分數寫進 eval_result、eval_all() 會 UPDATE fixed_eval。2026-07-29 報告指出解除 pack 停滯需「教材選取變異」,而變異機制 | 改 /home/hugo/project/augur/scripts/evolve_cycle.py:把 _eval_pack 的評分端由 _score 換為走凍結集三軸尺(呼叫 eval_local_model.run_arm(arm=f'pack:{vid}'),分數寫 local_model_eval_run 帳本),search_packs() 之冠軍判定改讀 capability 格之 evidence_level;_score/_eval_pack 依 P4.E3 只失效不刪(比照 ④ 之 if False,加 docstring 註明作廢理由);INSERT 補填 eval_code_hash。為免 script 互  | 零 schema 變動;可能新增一個 library 模組(須含執行指令矩陣 + --selftest) |
| S | SUNSET (c) 之凍結文字與現行判讀鐵則相衝且與 v2 集不相容(S-8 待裁):(c) 逐字只要求勝 floor 與 mismatched、不含 robot;而 evidence_protocol 明訂 robot 在場且 live 未嚴格勝之即 none。實測舊集 aeff01c18ace:behavior F@L1=0.9667 > floor 0.3333 > mismatched 0.0(首半成立),但 robot F@L1=**1.0000** ≥ behavior。此外 (c) 說「F@L1」而週報實作用**聚合 axis_f**,且 v2 集根本無 L1 格(五格為 B1/B2/B3/C1/C2P)。93 天後 | 不得改 criteria(criteria_sha 已鎖,改即挪門柱)。可做兩件:(1) 產一份對照報告(reports/,#16 命名)把「(c) 文字口徑」與「A′ 口徑」兩種判讀之現值並列(文字口徑=首半已成立、缺複現;A′ 口徑=robot veto 下 none),供 hugo 裁 S-8 語意權;(2) 若 hugo 裁定以 A′ 取代 (c),須走 governance_queue 正路對 V2-SUNSET 做 minor 修訂或新增一列 gate 並註明 supersede,**不得 UPDATE 既有 criteria**。實作落點:改 /home/hugo/project/augur/scripts/repor | 零 schema 變動;若走修訂則 evolution_prereg_gate 新增一列(不動舊列) |
| M | 假 oracle 仍在:local_model_gold_sample.verdict 745/745 單值 'oracle_pass',系統中不存在任何 oracle(evolve_cycle.py 之 INSERT 寫死 'oracle_pass'),所有 `WHERE verdict='oracle_pass'` 是空操作;teacher 全 NULL、is_synthetic 全 true。欄位語意暗示「已驗證」,是能力宣稱鏈上游最大的未修真兆風險 | 二選一(tier2 設計書 C11 / §4.6 人閘第 8 項):(A) 實作確定性 oracle 使 'oracle_fail' 會出現——field_correlation 型題重算 SQL 比對、column_catalog 型題驗 answer ⊆ catalog 逐字、knowledge_item 型題驗欄位存在,不過者寫 verdict='oracle_fail' 之**新列**(表 append-only,不 UPDATE #12);落點=新增 /home/hugo/project/augur/scripts/verify_gold_oracle.py;(B) 改名為 auto_seeded 並移除所有暗示已驗證之  | (A) 零 schema 變動(新 script 一支);(B) ALTER TABLE RENAME COLUMN + 全 repo WHERE 修正 |
| M | B5 射程二選一未裁,故任何 LAI 增益之受益面未定義:實測 serving 空缺(四版全 retired、~/.cache/augur/serving_pack.txt 已移除、MCP 回基線);v2 總控 §11.3 B5 指出唯一受益面是 local-llm MCP 之 ask profile(審議引擎用裸 4b 不讀 pack、advisor 用 8b 而 pack 在 4b 上評)。既有落點 deliberation_model_probe 18 列 / deliberation_model_agreement 5 列 | 若 hugo 選 (A)「serving 產物接審議引擎受 5 oracle 反向驗證」:改 scripts/deliberate.py 之 LLM 意見端讀 ~/.cache/augur/serving_pack.txt 並把 pack 版本 id 寫入 deliberation_model_probe,以 5 oracle 之 confirmed 率當反向驗證指標。若選 (B)「誠實標注射程僅及一個 MCP profile」:在 local_model_version 加註記欄或於 reports/ 記錄,並在週報與 brief 之措辭閘加「射程僅及 local-llm ask profile」強制字串。兩者皆須先有 servi | (A) 零新表(deliberation_model_probe 可能需加 pack_version_id 欄);(B) 零 schema 變動 |
| M | knowledge_capability_charter 空表:能力宣稱之**聲明側**(逐層 can_answer/cannot_answer/forbidden_pat)零列,故「本地模型能答什麼、不能答什麼」目前只存在於 BEHAVIOR_PROMPT 四條守則(寫死在 eval_local_model.py:44 附近、且在 eval_code_hash 內=改守則即換尺)與各報告文字,無 DB SSOT,與 CLAUDE #29b「決定行為的資料住 DB 不寫死 Python」相衝 | 新增 /home/hugo/project/augur/scripts/seed_capability_charter.py --build:把現行四條行為守則逐條拆為 knowledge_capability_charter 列(layer 對應 B1/B2/B3/C1/C2P),並改 eval_local_model.py 之 BEHAVIOR_PROMPT 由該表組出。**關鍵防呆**:BEHAVIOR_PROMPT 在 _code_hash() 內,改為 DB 驅動後必須把**組出的 prompt 全文**(而非表名)餵進 hash,否則 DB 一改就悄悄換尺而 hash 不動(=靜默失效的防呆) | 零新表(knowledge_capability_charter 已存在);_code_hash() 須改為涵蓋 rendered prompt 全文 |

**機器可判驗收（可預先凍結）**
- A′(A13)機器判定:`cd /home/hugo/project/augur && venv/bin/python scripts/verify_evolution_acceptance.py --only A13` 輸出 verdict=PASS,且證據句列出至少一個 `<arm>@C1_ZH_EXISTENCE` 或 `<arm>@C2P_ZH_PAIR` 並標 (≥2 run)。判準本體不得放寬:evidence_level ≥weak,即 live 於該格嚴格 > floor 且 > mismatched 且 > robot(現值 floor=robot=0.500,故 live 須嚴格 >0.500)。
- 配對性:A13 之比較須在 live 與 floor/mismatched/robot 皆有非 null f 值之 item_id 交集上進行,且該交集於每個 capability 格 ≥20 題;交集不足即輸出 incomparable(非 PASS)。門檻值須先存在於 evolution_prereg_gate 之 gate_id='A-PRIME-VALIDITY' 列且 status='approved'、approved_by='hugo'。
- 尺未漂移:`venv/bin/python scripts/eval_local_model.py --selftest` 全綠(含「尺之錨:qwen3:4b 之 eval_code_hash 仍為 b6e5208ef821」一項);`python -m augur.evolution.behavior_rubric --selftest` 全綠;`python -m augur.audit.evidence_protocol --selftest` 全綠。任一紅=尺已變,該輪結論一律作廢。
- 防樣板地板五臂常駐:任何宣稱所依附之 (set_id, eval_code_hash) 上,ceiling/floor/shuffled/mismatched/robot 五臂皆各有 ≥1 筆 run,且 ceiling 於該 capability 格 =1.000。SQL 可判:`select count(distinct arm) from local_model_eval_run where set_id=$1 and eval_code_hash=$2 and arm in ('ceiling','floor','shuffled','mismatched','robot')` = 5。
- 禁用聚合 axis_f 作能力宣稱:任何 LAI 能力宣稱之證據句須逐格(cell_class='capability')列出,且同時列出同格 robot 值。機器判:`scripts/report_post_batch_verdicts.py --run` 輸出須含 'robot' 與該格名,`grep -c` = 0 即不合格。
- A 軸宣稱之前置:若宣稱依附 A 軸,同格 floor 之 axis_a 必須 <1.000。現值 B3.A floor=1.000 → **A 軸現階段一律不得作為能力宣稱依據**(此條可即刻凍結,無須等新集)。
- LoRA 前置閘(開輪前必過):`venv/bin/python scripts/verify_lora_prereq.py` exit 0 且五項全 PASS,輸出須含所在機器 hostname——(a) torch.cuda.is_available()=True 且 free VRAM ≥3000 MiB;(b) peft/trl/bitsandbytes/gguf 四包可 import;(c) ~/llama.cpp/convert_lora_to_gguf.py 與 ~/models/Qwen3-1.7B 存在;(d) ollama /api/tags 含 qwen3:1.7b;(e) RAM available ≥8 G
- 權重鏈雙向對照(非單向「跑起來了」):PEFT adapter → convert_lora_to_gguf → ollama create 成功後,須證明擾動 adapter 使輸出改變——同一 prompt 在 base 與 +adapter 下輸出 byte hash 不等,且把 adapter 權重乘 0 後輸出 byte hash 回到 base 值;三個 hash 寫入 local_model_version.eval_result。
- 正控制(訓練管線是否壞的唯一判別):32 條樣本 × 30 epochs,訓練集逐字回吐率 ≥0.95 且 final train loss <0.1。不過即判「訓練管線壞」,**明文不得判「LoRA 無效」**。
- 訓練/評測格式同一:訓練端與服務端之 prompt 前綴 byte-sha256 相等(assert,不等即 fail-loud 中止);兩個 hash 寫入報告。
- 洩漏防護(樣本粒度):訓練 sample_id 清單之 sha256 寫入 local_model_version.train_sample_manifest_hash,且與 local_model_eval_item.source_key 所指來源鍵之交集為空(SQL 可判 + 程式 assert)。
- 三 hash 鎖生效:`select count(*) from local_model_version where status<>'candidate' and (eval_code_hash is null or gate_id is null)` = 0(以 CHECK 約束機械保證)。
- 漂移可見:`select count(*) from local_model_eval_set_check` > 0,且每個演化鏈執行日有 ≥1 列;連續 3 日 n_drifted > 20 時 `verify_eval_set_validity.py --record` exit≠0。
- 晉升人閘不可代打:local_model_version.promoted_by 一律 hugo 親跑 psql 寫入;AI 不得執行該 UPDATE(既犯一次已於 pp_7c553198837a 之 eval_result.signature_provenance 自陳,不竄改)。
- 重跑紀律:預註冊之重跑次數為**恰 ×2**;仍 INVALID 則誠實報告不迴圈——禁止為湊 ≥2 run 而反覆重跑至碰巧全 valid(變相 p-hacking)。
- 停損可觸發:local_ai_iteration_ledger 有 ≥1 列且 gain_basis 僅允 'capability_cell_evidence';缺對照臂之輪一律記 incomparable 且不計入 consecutive_no_gain(否則 LAIEVO-STOP-N 會誤觸發)。
- 落日倒數可讀:`venv/bin/python scripts/report_triple_evolution_week.py` 之 V2-SUNSET 段須印剩餘天數與 0/3–3/3 計數;deadline 2026-10-31 前 (a)/(b)/(c) 任一未達成即照凍結後果執行,不得換 trigger_code 重開。

<details><summary>本線誠實界限</summary>

誠實界限與取證方式:(1) **DB 為 live 直查**——以 .env 之 DB_USER/DB_PASSWORD 經 psql 連 augur 庫(注意:`psql -d augur` 裸連會失敗,role "hugo" 不存在,必須帶 .env 憑證);所有列數、欄位、逐格軸值(detail->per_item 以 jsonb_array_elements 展開後 group by)皆本次於 2026-07-30 親查。(2) **實跑四支**:`verify_evolution_acceptance.py --only A13 A5 A4`(得 A13=N/A「v2 集尚無有效受測 run」、A5=PASS、A4=N/A)、`report_triple_evolution_week.py`(得 SUNSET 剩 93 天、0/3 皆未達成、(c) 複現之臂=無、robot 同尺 F=1.0)、`eval_local_model.py --selftest`(全綠,PINNED 錨 b6e5208ef821 確認未漂)、`augur.evolution.behavior_rubric --selftest`(全綠)。(3) **硬體與環境為本機親驗**:hostname=PC002-S1800、nvidia-smi 不存在、torch.cuda.is_available()=False、venv 無 peft/trl/bitsandbytes/gguf/dspy、~/llama.cpp 與 ~/models/Qwen3-1.7B 不存在、ollama 無 qwen3:1.7b、RAM total 11GB / available 2GB、i5-10500 AVX2 only。**這與 reports/augur_tier2_lora_spike_design_20260726.md §1 之親驗表(GTX 1650 4GB、bnb 0.50.0、peft 0.19.1、trl 1.9.0、gguf 0.19.0、torch 2.12.1+cu126、RAM 17GB)全面不符——該表應屬另一台 DESKTOP,我無法登入該機驗證,故 DESKTOP 側一切數字本報告一律標為「未親驗、轉述」。同理 MEMORY.md 之「venv 新增 peft/trl/dspy/gguf」在本機為假。**(4) **只讀 DDL 未驗 live 者**:無——本主題所有表皆已 live 查列數與欄位。(5) **查無(明確)**:local_model_behavior_sample 表查無;convert_lora_to_gguf 之任何 code 查無(全 repo 僅 3 份 report + 記憶檔提及);run_local_ai_iteration.py 查無;lora_training_run 表查無;L5_ANCHOR(通用能力錨集)不在 layer CHECK 九值中 → 「通用能力是否退步」目前**無尺可量**,任何 LoRA 結論都無法排除通用能力退步;scripts/run_evolution_chain.sh 查無(該檔在 repo 根目錄 /home/hugo/project/augur/run_evolution_chain.sh,crontab 01:30 指向根目錄版)。(6) **推論而非實測者**:「CPU-only 下第 2 輪 behavior 大概率仍 INVALID」係由 9/132 逾時率外推,非實測;真值須跑第 2 輪才知。(7) **未查證者**:知識庫每日成長對凍結集 absent 型題目之實際反轉數(需跑 verify_eval_set_validity.py 全量,唯讀但耗時,本次未跑);SUNSET (a) 條件(arena/direction 線)之現值屬他主題,本次僅引週報輸出之「未達成」而未自行複核。(8) **低優先觀察項(未寫成 gap)**:local_model_eval_run 之 INSERT 仍為 `ON CONFLICT (run_id) DO NOTHING`(靜默丟棄),v2 總控 §10 已裁「不復活長格式改造,改 fail-loud + 兩欄」但 fail-loud 尚未落地;因 run_id 現含 attempt 序,碰撞機率低。

</details>

---

### 8.5 ⑤模擬方法

*行走者⑤模擬方法（風險畫像方法庫進化）——第二輪 episode 五窗＋copula-t／EVT／跨市場類比之實作級現況與可開工缺口*

**既有表（8）**：`mc_simulation_run`（540 列總計；其中 target_id LIKE 'PORT%' 僅 20 列、且全部同一 target `PORT_）、`mc_simulation_run.method CHECK 白名單（現行 20 值）`（20 值全部已有實跑列（每個新方法各 1 列，皆 asof 2026-05-31））、`risk_policy`（6 列＝H60/H120 × {dd_circuit, max_position, turnover_budget}；d）、`prediction_values`（panel 2026-05-31：五 cell（H20/H40/H60/H82/H120）各 33 檔；panel 20）、`TaiwanStockPriceAdj`（H60 cell 33 檔共同覆蓋 749 td（設計窗 756、剔除 7 日））、`USStockPrice / UKStockPrice / JapanStockPrice / EuropeStockPrice`（US 1928-02-01～2026-06-18（35,052,889 列）；UK 1968-01-01～2026-07）、`direction_gate / evolution_prereg_gate`（direction_gate 六門（全 evaluated_fail）；evolution_prereg_gate 1 ）、`freeze_manifest`（0 列）

**既有 script（7）**：`simulate_portfolio_risk.py`、`simulate_mc_paths.py`、`migrate_mc_method_check_ddl.py`、`serve_probability_ui.py`、`verify_risk_overlay.py`、`migrate_risk_policy_ddl.py`、`check_cmd_matrix.py`

**缺口與可開工下一步（12）**

| 工 | 缺什麼 | 可開工的第一步 | 需要的表／欄 |
|---|---|---|---|
| S | **前提修正（最重要事實）**：任務提示所稱「第二輪 episode 五窗＋copula-t／EVT／跨市場已拍板在隊列」——實際已於 2026-07-27 全部落地並實跑入帳（commit 1d403f8 五窗+garch、640e506 M1、a2b9b20 M2、eb7e622 M3；白名單 20 值、20 筆 PORT_ run 在庫）。真正缺的是**收尾報告與預註冊規則判讀**：07-26 四法對照有 `reports/augur_risk_sim_method_comparison_20260726.md`，07-27 三法（M1/M2/M3）**無對應結果報告**，判讀規則未逐條套用、七法保守值未更新入風險畫像敘述 | 寫 `reports/augur_risk_sim_advanced_results_20260730.md`：數字唯出 `mc_simulation_run`（EVT P(MaxDD<-0.20)=0.0257／copula 0.0005／block 0.0559／iid 0.0033；analog us2008 MaxDD -45.6% vs 台股 2008 重放 -37.9% 校準錨Δ=-0.076；us1987 -31.7%／us2000 -26.5%；三窗誠實拒答 us1929/us1973/uk1973），逐條套用進階三法計畫 §分階段 E1/E2/E3 驗收表，並明寫「H60 最保守值仍為 block 5.6%、EVT | 零 schema 變動（純讀 mc_simulation_run.summary） |
| S | 帳本 provenance 說謊：兩處 INSERT 之 `ON CONFLICT (run_id) DO UPDATE SET summary=EXCLUDED.summary, created_at=now()` **不更新 git_sha** → 重跑覆寫 summary 但 git_sha 停在舊 commit。live 已實證：iid/block 兩列 git_sha=`df4043c`（2026-07-25 commit）但 created_at=2026-07-27（M2/M3 那輪必然重跑過整個 bootstrap 迴圈） | 改 `scripts/simulate_portfolio_risk.py` 兩處 upsert（run_analogs ~line 396、run ~line 495）為 `DO UPDATE SET summary=EXCLUDED.summary, git_sha=EXCLUDED.git_sha, n_paths=EXCLUDED.n_paths, created_at=now()`；並在 `--selftest` 加一項字面斷言鎖住 SQL 含 `git_sha=EXCLUDED.git_sha`（同 EVT 路徑口徑那條字面鎖之慣例） | 零 schema 變動 |
| S | n_paths 欄與 summary 不一致／缺記：line 500 寫 `n_paths if method.endswith("bootstrap") else 1` → garch_fhs／evt_pot_hybrid／copula_t_garch 三法欄位一律記 1（實際 10,000）；且 `_bootstrap_summary` 完全不寫 n_paths/seed/horizon_td，故 **garch_fhs 的路徑數在欄位與 summary 兩處皆無記錄**（live 實查 summary->>'n_paths' 為 NULL） | 改 `simulate_portfolio_risk.py`：(a) upsert 的 n_paths 一律傳真值（episode/analog 之確定性重放才傳 1，並在 summary 記 `"n_paths_semantics":"deterministic_replay"`）；(b) `_bootstrap_summary` 回傳 dict 補 `n_paths/seed/horizon_td`（與 evt/copula 對齊）；(c) selftest 加「四法 summary 皆含 n_paths/seed/horizon_td」紅綠 | 零 schema 變動 |
| M | **參數凍結無機械鎖（本主題最大治權缺口）**：所有凍結參數（EVT_U_Q／EVT_REFIT／COP_DOF_GRID／COP_MIN_SURVIVE／WINDOW_TD／BLOCK_LEN／MIN_COMMON_TD／MIN_EPISODE_W_COVER／MIN_ANALOG_STOCKS／EPISODES／ANALOG_EPISODES 窗值）只住 code 常數＋md 計畫；run_id 雜湊 key 僅 `target/panel/horizon/method/seed`，**不含任何參數** → 改常數後重跑會 UPSERT 覆蓋同一 run_id、舊值消失、無人察覺（挪門柱不留痕）。既有 `direction_ga | (1) `simulate_portfolio_risk.py` 新增 `_params_sha(method) -> str`：把該法凍結常數序列化為 canonical JSON 取 sha256[:12]，寫入 `summary['params_sha']` **並納入 run_id key**（參數一改自動分家、不覆蓋）；(2) 新增 `scripts/verify_sim_param_freeze.py`（#18/#29 全矩陣＋--selftest）：逐列比對帳本 `summary->>'params_sha'` 與當前 code 重算值，不符即 exit≠0 並印「參數已漂移：某列須以新方法名重跑」；(3) 選配人閘層 | 步驟(1)(2) 零 schema 變動（用 summary JSONB）；步驟(3) 需新表 `sim_method_gate` + 一個 trigger function（DDL 抄 direction_gate 樣板） |
| S | 凍結 panel 無法釘死 → 已入帳的「凍結 panel 2026-05-31」結果**現在無法重現**：`_load_cell_portfolio(cur, cell)` 硬用 `panel_date=(SELECT max(panel_date) FROM prediction_values)`，live max 已推進到 2026-06-30（H60 成分 33→22 檔）；且 H82/H120 於 2026-06-30 無列 → `--cell RankRidge_H120` 今天執行會 `raise RuntimeError`（裸 traceback、非 graceful） | 改 `_load_cell_portfolio(cur, cell, panel=None)`（panel=None 維持 max()，否則 `panel_date=%s`）＋ CLI 加 `--panel YYYY-MM-DD`；`run()`／`run_analogs()` 透傳；查無列時改印「cell X 於 panel Y 無候選組合列（可用 panel：…）」並 return 1（不裸 traceback，#29a）；selftest 加「指定不存在 panel → graceful 非例外」 | 零 schema 變動 |
| M | 四鎖之④呈現面對組合層是**破的**：`/simulate` 下拉選單列出 `PORT_RankRidge_H60_2026-05-31`（_mc_targets 無過濾），選它即 500——親測 `_fan_svg` / `simulate_page` 皆 `KeyError('cone')`（組合層 summary 無 cone/last_close）。且下拉之 horizon 清單被 episode 的 n_td 污染（實測列出 1,60,66,78,105,123,142,145,226,238） | 改 `scripts/serve_probability_ui.py`：(a) `_mc_targets` 分兩組（個股 target 給錐頁；`PORT_%` 走新 `_portfolio_risk_block(cur, target)`）；(b) 新區塊只渲染既有 summary 欄位——主結論 episode 表（cum/MaxDD/weight_coverage）＋參考層六法 MaxDD 分位表＋analog 三句硬標示＋拒答列如實顯示「拒答」而非空白；(c) 改完 `sudo systemctl restart augur-probability`（#7 http.server 不熱更新）再實測 /simulate?sto | 零 schema 變動 |
| S | `--compare` 只印 BOOT_METHODS 四法，EVT／copula／analog **無任何唯讀對照面**（親跑輸出標題仍為「四法對照」）；而 commit eb7e622 訊息宣稱「七法對照齊」＝宣稱與 code 不符 | 改 `compare(cell)`：新增 `REF_METHODS = BOOT_METHODS + ('evt_pot_hybrid','copula_t_garch')` 六法並排（EVT 附 ξ/CI/n_tail 列、copula 附 dof/λ/存活數列）；加 `--layer {reference,episode,analog}` 三層唯讀表（analog 表每列強制前綴 `analog:`）；表尾維持窗偏差＋主結論聲明 | 零 schema 變動 |
| M | M3 copula 未達成其宣稱目的（「補相關性趨一之洞」）且結果方向可疑，但已入帳無標記：live summary `copula_dof=30` **正好撞 COP_DOF_GRID 上界**（profile MLE 飽和＝近高斯 copula）、`tail_dep_lambda=0.0001`≈0、`p_maxdd_lt_policy=0.0005` **低於 iid 的 0.0033**（六法中最樂觀）；且 note 自陳「條件波動固定於期末值（不遞迴外推=保守）」——凍結 σ 實際是移除波動叢聚、對 MaxDD 屬**反保守**，標為「保守」是誤標 | (1) `_fit_t_copula` 回傳加 `dof_at_grid_boundary: bool`，`_copula_summary` 於 True 時改寫 note 為「dof 撞格點上界⇒尾部相依不可辨識、本列不得作為尾部風險證據」（不改已凍參數、只補揭露）；(2) 修正 note_structure 之「保守」誤標為「σ 凍結於期末值⇒移除前向波動叢聚、對 MaxDD 方向為低估」；(3) 若要真補洞＝**另註冊新方法名** `copula_t_garch_recursive`（σ 逐步 GARCH 遞迴），走白名單 +1 值＋新 params_sha，禁改 M3 已凍列 | (1)(2) 零 schema 變動；(3) 需 `migrate_mc_method_check_ddl.py` METHODS +1 值（20→21） |
| S | 跨市場類比三窗**永久拒答**且無復活路徑登記：live 實證 us1929 日覆蓋 min=1、us1973 min=54、uk1973 min=28（皆 <MIN_ANALOG_STOCKS=100）；現有來源無法修（fred_series 最早日頻股指為 NASDAQCOM 1971-02，1929/1973 無日頻指數）。同時 `JapanStockPrice`（1999-05 起）與 `EuropeStockPrice`（1980-04 起）已在庫但**零窗註冊** | 二擇一寫進計畫並機械化：(A) 承認永久拒答——`ANALOG_EPISODES` 三窗加 `permanently_refused` 註記＋在 verify 腳本鎖「這三列必須維持 analog_refused」（防日後放寬 MIN_ANALOG_STOCKS 偷過）；(B) 擴可行窗——註冊 `episode_analog_{jp2008,eu2008,eu2011,eu2020}`（資料底已足），走 `migrate_mc_method_check_ddl.py` METHODS 20→24＋`ANALOG_EPISODES` 加四列（窗值 commit 即凍）；1929/1973 若要救只能改「指數級月頻」新方法（須先 in | (A) 零 schema 變動；(B) 白名單 +4 值（無新表） |
| M | `mc_simulation_run` 無任何機械誠實閘：pg_trigger 查 0 列（對比 direction_gate 有 no-goalpost trigger）；summary 亦無 `disclaimer` 存在性 CHECK → 鎖①「disclaimer 硬綁」目前**只靠 code 自律＋selftest**，任何人／任何腳本可 UPDATE 或 DELETE 帳本列而不留痕 | 新增 `scripts/migrate_mc_sim_guards_ddl.py`（#18/#29 全矩陣、--dry-run/--apply/--selftest 零 DB SQL 文字紅綠）：(a) `ALTER TABLE mc_simulation_run ADD CONSTRAINT mc_sim_disclaimer_present CHECK (summary ? 'disclaimer')`；(b) BEFORE DELETE OR UPDATE trigger 沿 `direction_gate_no_goalpost()` 樣式——DELETE 一律拒、UPDATE 僅允許 summary/git_sha/n_p | 無新表；一條 CHECK + 一個 trigger function + trigger |
| S | 窗日期脊取自 `members[0]`（依 stock_id 排序之第一檔）之交易日 → 有效窗隨成分排序而變（實測 756 設計窗 → 749 有效），非市場日曆；同時 copula 另用 `cop_dates`（全成分交集）＝**同一輪內兩套日期口徑** | 改 `run()`：日期脊改為 `SELECT DISTINCT date FROM "TaiwanStockPriceAdj" WHERE date<=%s ORDER BY date DESC LIMIT WINDOW_TD+1`（市場日曆、與成分無關），bootstrap 與 copula 共用同一 `common` 交集；summary 加 `date_spine='market_calendar'` 與 `spine_td/effective_window_td` 兩數並記；selftest 加「脊不因成分排序改變」紅綠 | 零 schema 變動 |
| S | 無排程：`crontab -l` 查無任何 risk sim 項、repo 無對應 systemd timer；live 增量維運下 panel 已前進到 2026-06-30 但風險畫像仍停在 2026-05-31（且成分由 33 檔降為 22 檔＝畫像對象已變） | 加 systemd timer 或 cron（月度、panel 更新後次日）：`venv/bin/python scripts/simulate_portfolio_risk.py --run --cell RankRidge_H60 --panel <新 panel>` 再 `--run --analog all`；新 panel 產生新 target_id（append-only、不動舊列）；同時登記進 `ops/` 排程檔入 git（#21 背景作業可見、排程入 git 之既有慣例） | 零 schema 變動；需 ops 排程檔（cron/systemd drop-in） |

**機器可判驗收（可預先凍結）**
- 參數凍結：`python3 scripts/verify_sim_param_freeze.py` exit=0，且 `select count(*) from mc_simulation_run where target_id like 'PORT%' and summary->>'params_sha' is null` = 0；人為改 EVT_U_Q 為 0.06 後同一指令 exit≠0（負向測試必須紅）
- 分家不覆蓋：以 `--n-paths 20000` 重跑同 cell/method，`select count(*) from mc_simulation_run where target_id='PORT_RankRidge_H60_<panel>' and method='evt_pot_hybrid'` 由 1 變 2（舊列 summary 與 params_sha 逐位不變）
- provenance：`select count(*) from mc_simulation_run where target_id like 'PORT%' and git_sha <> '<當前 HEAD 前 7 碼>' and created_at::date = current_date` = 0（重跑當日寫入之列 git_sha 必等於當時 HEAD）
- n_paths 誠實：`select count(*) from mc_simulation_run where target_id like 'PORT%' and method in ('garch_fhs','evt_pot_hybrid','copula_t_garch') and (n_paths <> (summary->>'n_paths')::int)` = 0，且 `summary->>'n_paths'` 皆非 NULL
- panel 可釘：`--panel 2026-05-31 --cell RankRidge_H60` 之 n_members=33、effective_window_td=749、window_maxdd=-0.24281（與現存列逐位相同）；`--cell RankRidge_H120 --panel 2026-06-30` 印 graceful 訊息並 return 1（stderr 無 Traceback）
- UI 不崩：`curl -s -o /dev/null -w '%{http_code}' 'http://127.0.0.1:8600/simulate?stock=PORT_RankRidge_H60_2026-05-31&h=60'` = 200，且回應內含 'analog' 或 '拒答' 字樣、含 SIM_WATERMARK；`python -c` 直呼 `simulate_page(cur,'PORT_...',60)` 不再拋 KeyError（現況實測 KeyError('cone')）
- 對照面齊：`--compare --cell RankRidge_H60` stdout 行數含 evt_pot_hybrid 與 copula_t_garch 兩列（grep -c 各 =1）；`--compare --layer analog` 每一資料列以 'analog' 前綴（grep -v '^ *analog' 之資料列數 = 0）
- copula 邊界旗標：`select summary->>'dof_at_grid_boundary' from mc_simulation_run where method='copula_t_garch'` = 'true'（現況 copula_dof=30＝格點上界），且 note_structure 不再含「保守」二字
- 拒答不可被偷放寬（若採 G9-A）：`select count(*) from mc_simulation_run where method in ('episode_analog_us1929','episode_analog_us1973','episode_analog_uk1973') and summary->>'kind' <> 'analog_refused'` = 0
- 帳本閘（若採 G10）：`select count(*) from pg_trigger where tgrelid='mc_simulation_run'::regclass and not tgisinternal` ≥ 1；未帶 GUC 通行證之 `delete from mc_simulation_run where run_id='<任一>'` 必須被拒（SQLSTATE 非 00000）；`select count(*) from mc_simulation_run where not (summary ? 'disclaimer')` = 0
- 白名單仍為閉集：`select count(*) from pg_constraint where conrelid='mc_simulation_run'::regclass and conname='mc_simulation_run_method_check'` = 1，且新增方法後 `insert ... method='typo_method'` 必被 CHECK 拒
- 回歸不退：`venv/bin/python scripts/simulate_portfolio_risk.py --selftest` 維持全綠且項數 ≥ 23（現況實跑 23/23）；`python3 scripts/check_cmd_matrix.py` exit=0（新增之 verify_sim_param_freeze.py／migrate_mc_sim_guards_ddl.py 首次提交即含矩陣）
- 主結論地位不變（每次改動後必驗）：episode_replay_2008 之 summary maxdd 仍為 -0.37948、weight_coverage=1.0；episode_replay_1997/2000 仍為 episode_refused（覆蓋 30%/58% < 70%）；任何參考層方法之數字不得寫入 risk_policy（`select max(updated_at) from risk_policy` 維持 2026-07-07）

<details><summary>本線誠實界限</summary>

誠實界限：(1) **任務前提須更正**——「第二輪五窗＋copula/EVT/跨市場已拍板在隊列」實際已全部落地並實跑（2026-07-27 四個 commit、白名單 20 值、20 筆 PORT_ run 在 live DB），故本次蒐證重心自動轉為「已落地之後的機械缺口」。(2) 全部表結構與列數皆 live DB 實查（psql via .env 五件套；hugo role 不存在故必須用 DB_USER），非只讀 migration 檔；`_fan_svg` KeyError('cone')、selftest 23/23、`--compare` 只出四法三項為**親跑實測**。(3) **live-vs-報告漂移（查無、誠實回報）**：`reports/augur_risk_sim_method_comparison_20260726.md` §五 宣稱「帳本 PORT_ 35 筆＝5 cell × 7 法」，但本機 live 僅 20 筆、且 target_id 只有 `PORT_RankRidge_H60_2026-05-31` 一個——該報告 §一 之 H60 列（-12.5/-21.0/-21.0/-13.7 與 P 值）可從本機帳本逐位重現，**H120 那半張表在本機查無來源列**（可能跑在另一台 DESKTOP，或跑後未留）；引用該報告 H120 數字前須先在當家機重跑。(4) 未執行任何 `--run`（會寫帳本、且會以新 panel 2026-06-30 產生新 target），故所有 live 數字均來自既存列＋唯讀 CLI。(5) 四鎖現況：①disclaimer 僅 code＋selftest 保證、DB 無 CHECK；②只存 summary 成立（無逐路徑表）；③模擬數字不入對話白名單——結構上成立（全 repo grep：advisor 完全不讀 mc_simulation_run，`src/augur/advisor/prompt.py` 只以文字導向 /simulate 頁），但**無任何測試斷言此隔離**，日後接線可靜默破鎖；④憲章明文＝`docs/系統架構大憲章_v1.49.0.md` 第 137 行「逐日價格點位/路徑永久除外……路徑類需求唯得以蒙地卡羅模擬情境滿足，且輸出硬綁『模擬非預測』標示、模擬數字不入對話層數字白名單」（code docstring 仍引 v1.42.0 §1.2＝指針過期但實質條文在）。(6) `audits/` 與 `docs/` 全文 grep 對 simulate_portfolio_risk／evt_pot_hybrid／copula_t_garch／episode_replay **零命中**＝模擬方法軸尚未進入任何稽核清單，這本身是缺口（未列為獨立 gap，併入 G4/G10 之機械化）。(7) 現行 crontab（user hugo）對 risk/simulate 零命中；freeze_manifest 為空表、與模擬參數凍結無關。

</details>

---

### 8.6 ⑥模型／隊伍

*行走者⑥ 模型/隊伍(arena live + replay 重演)——實作級現況與可開工缺口*

**既有表（9）**：`direction_arena_candidate`（11 列:10 active + 1 retired(own_threelens_interact,2026-07-25）、`direction_arena_prediction`（11,440 列 / 8 model_key / 5 個 pred_date(2026-07-15,07-16,07-2）、`direction_arena_replay`（4,362,946 列;majority/momentum_20/mc_bootstrap 各 2,798 cluste）、`arena_replay_run`（8 列(majority×3 含 probe、momentum_20×2、mc_bootstrap×2、own_dail）、`direction_gate`（29 列 = 14 approved + 12 evaluated_fail + 3 superseded。approv）、`direction_arena_policy`（2 列:futility_min_clusters=60、futility_z=1.645,frozen=true(hu）、`direction_arena_verdict`（**0 列**——判停機制自 2026-07-12 凍結閾值以來從未產出任何裁決列）、`arena_admission_gate`（3 列:1 evaluated_pass(arena_adm_5305655ad1cd,hugo 2026-07-16 ）、`meta_replay_perf / meta_replay_cutoff`（meta_replay_perf 122 列 / meta_replay_cutoff 61 列,但**橫跨 4 個 p）

**既有 script（13）**：`run_arena_replay.py`、`evaluate_direction_gate.py`、`settle_arena_labels.py`、`verify_arena_watchlist.py`、`run_arena_daily_pipeline.py`、`run_arena_round.py`、`adapters.py`、`preregister_direction_gate.py`、`arena_scoreboard.py`、`migrate_arena_replay_ddl.py`、`evaluate_meta_replay_gate.py`、`register_arena_candidate.py`、`evaluate_arena_admission.py`

**缺口與可開工下一步（13）**

| 工 | 缺什麼 | 可開工的第一步 | 需要的表／欄 |
|---|---|---|---|
| M | TSFM 三隊 replay 完全未跑,且其中兩隊**合法窗長度先天不足**凍結門檻:R3 發布日已親驗(reports/augur_arena_replay_plan_20260729.md 補記 2026-07-30)——chronos_bolt_small 合法窗 2024-12-26→2026-06-30、moirai2_small_5 2025-09-15→2026-06-30、timesfm_25_200m 2025-10-16→2026-06-30;但 DB 實查該三窗之 TAIEX 交易日僅 **363 / 189 / 169** 天,而三門 criteria.min_clusters 一律凍在 **250**(cl | ① 先跑可判者:`python scripts/run_arena_replay.py --model chronos_bolt_small --from 2024-12-26 --to 2026-06-30 --run --allow-pretrained`(363 clusters ≥250,唯一能過門檻的外隊);② moirai2/timesfm 走「誠實不可判」路徑:不得改既有門(no_goalpost trigger),須以 preregister_direction_gate.py 新增 --preregister-replay-v2 另立 gate_id(如 dgate_replay_moirai2_small_5_5 | 零 schema 變動(direction_gate/arena_replay_run/direction_arena_replay 皆已具欄);僅新增 direction_gate 列 + evaluate_direction_gate 內新增 min_nonoverlap_c |
| S | `weights_cutoff_ok` 是**寫錯 + 從未被讀**的雙重靜默失效:(a) scripts/run_arena_replay.py:109 以 `model in CLEAN_TEAMS` 賦值——外隊即使跑在親驗合法窗內也一律寫成 false(把合法窗錯標為污染);(b) repo 全文 grep 只在 migrate DDL 與該行 INSERT 出現,evaluate_direction_gate.py:_fetch_samples 的 SQL 只 WHERE horizon/model_key/settled,**完全沒有 join arena_replay_run 過濾 weights_cutoff_ok= | ① 改 run_arena_replay.py:71-109——新增 `WEIGHTS_RELEASE = {model_key: 親驗發布日}` 與 `_legal_window(model, w_from)` 純函式(clean team→True;pretrained→w_from >= release+30d),weights_cutoff_ok 改由該函式決定,並在 --selftest 加紅綠(pretrained+違窗→False、pretrained+合法窗→True);② 改 evaluate_direction_gate.py:_fetch_samples,當 estimand.table='direction_ | 零 schema 變動;WEIGHTS_RELEASE 屬「決定行為的資料」邊界案例——建議寫入 direction_arena_candidate.spec.provenance.release_date(已有 provenance 子物件)而非 Python dict,守 # |
| S | cluster 門檻**三處口徑分裂**,且計分板每日對 hugo 印錯數字:settle_arena_labels.py:48 `GATE_TRIGGER_CLUSTERS=60` 與 :267 印「確立門檻 60=direction_gate」、CLAUDE.md 資料真實性條亦寫「≥60 clusters」——但全部 6 支 live dgate_arena_*(D×5)與 4 支 replay 門之 criteria.min_clusters 實凍在 **250**;H 軌三門凍在 36。後果:cluster 60→249 之間,settler 會每日呼叫裁判、裁判每日回「REFUSE(auto_trigger 未達)」,而 | ① 改 settle_arena_labels.py:48-67 與 :267——把 60 從寫死常數改為**從 DB 讀真門檻**:`SELECT min((criteria->>'min_clusters')::int) FROM direction_gate WHERE status='approved' AND gate_id LIKE 'dgate_arena%'`,計分板改印「trigger 掃描門檻 X / 各門真門檻 Y」兩個數,並把 --selftest 第 296 行那條「門檻=60 與計分板同源常數」斷言改成「印出值 == DB 讀值」(現行斷言是字面比對,正是會靜默變綠燈的那型);② 決策層問句(不得 AI  | 零 schema 變動 |
| S | 6 支 `dgate_replay_*` 與 2 支 `dgate_meta_replay_*` 在 DB 內 approved,但 **repo 沒有任何程式能產生它們**——`grep -rn 'dgate_replay\／dgate_meta_replay' --include=*.py` 只命中 evaluate/scoreboard 的引用字串,preregister_direction_gate.py 內 'replay' 零命中;計畫 §五 表格聲稱由「preregister_direction_gate.py(既有)」註冊,與實作不符。等於 8 條凍結判準不可從 repo 複現、criteria_sha 無法被 -- | 在 /home/hugo/project/augur/scripts/preregister_direction_gate.py 新增 `--preregister-replay` 與 `--preregister-meta-replay` 兩模式(沿用既有 _sha(criteria) 與 draft→approve 流程),criteria dict 逐字重建成與 DB 現存列**位元相同**;接著跑 `--check dgate_replay_own_daily_rolling_5` 等 8 次覆算 sha 驗證相符。若覆算不符即代表 DB 列非任何 repo 版本所生,須以誠實註記(note 欄)記錄其 ad-hoc 來源, | 零 schema 變動 |
| S | `--evaluate-all` 無 gate 選擇性、也無「重演批完整性」前置,造成**部分窗被終判**的即時風險:該旗標 SQL 是 `WHERE status='approved'` 全撈(:242),而 own_daily_rolling 重演此刻正跑到第 248 個 cluster(門檻 250),**數小時內即跨線**;任何人在此期間跑一次 --evaluate-all(或 live cluster 到 60 後由 settler 自動觸發),就會拿 2015-2019 的殘窗對 dgate_replay_own_daily_rolling_5 下**不可回改的終判**(trg_direction_no_goalpost | 在 evaluate_direction_gate.py:_fetch_samples 的 replay 分支加 fail-closed 完整性閘:對 estimand.table='direction_arena_replay' 之門,先查 `SELECT window_start, window_end FROM arena_replay_run WHERE model_key=%s`,再斷言該窗內 TaiwanStockPriceAdj 之 distinct 交易日數 == direction_arena_replay 之 distinct pred_date 數,不等即 return 'REFUSE' 並印「重演批未跑完(X | 零 schema 變動 |
| S | 門評硬性要求 git 工作樹乾淨(evaluate_direction_gate.py:83-85 `git status --porcelain` 非空即 sys.exit),而主 worktree 現有 8 個未提交項(scripts/build_sentences.py 已改 + LSRS 重切句 7 個新檔);settler 的自動觸發雖有 `if r.returncode != 0` 誠實印一行警語(:71),但那行只進 $HOME/logs/arena_settle.log 尾部——實務上等於「到門檻那天因為別條工作線的髒樹而沒判成,且沒人會看到」。 | ① 立即:把 LSRS 那批(reports/augur_long_sentence_resplit_embed_kh10_bridge_plan_20260730.md、scripts/resplit_long_sentences.py、scripts/migrate_sentence_resplit_ddl.py、scripts/refresh_kh4_after_resplit.py、src/augur/knowledge/sent_resplit.py、audits/LSRS-*.md、scripts/build_sentences.py)逐檔明列 commit(#14 授權後、禁 add -A);② 結構性:改 settl | 零 schema 變動(方案②若要落表,可複用既有 governance_queue,不新建表) |
| S | own_daily_rolling 全窗重演的算力估計錯 4 倍以上,連帶使「今晚三門終評」的排程承諾落空:計畫 §六與 reports/augur_all_evolution_next_steps_20260729.md 第 9/19 項都寫「~23h 重活、跨夜」;實測(PID 2980944,02:46 起跑,11:49 查帳本)9.05 小時完成 248/2798 clusters = 27.4 clusters/h,剩 2,550 clusters 需 **≈93 小時**,全窗完成落在 **≈2026-08-03**(且後段年份宇宙更大、只會更慢)。reports/arena_replay_first_readings_ | ① 在 scripts/run_arena_replay.py 的無參數現況輸出加吞吐與 ETA 兩欄(已跑 clusters / 窗內總交易日 / 近 1h clusters 速率 / 推估完成時點),讓長跑不靠人算;② 排程面二擇一:(a) 承認 4 天、把 dgate_replay_own_daily_rolling_5 終評與 W2 十年旁證改排 08-03 後,或 (b) 先跑 2024-01-01→2026-06-30 子窗(601 clusters,≥250 即可判,約 22h)取得可判樣本、全窗續作為後續補強——但 (b) 會使該門樣本窗與已判的 momentum/mc(2798)不同窗,**須在 result_sn | 零 schema 變動 |
| M | H 軌 own_stack_rolling **零出單**,三門(dgate_arena_own_stack_20/40/82,min_clusters=36)在現行 cadence 下要 **36 個月**才可能評:run_arena_round.py:100 `h_fires = month_days[0] == as_of` 只在當月首個交易日出手,而 arena 07-15 才開賽、07-27 才恢復 cron,故 8 月 3 日(下個月首交易日)才會有第一列 H 軌預測;h=20/40/82 交易日的標籤又要 1-4 個月後才實現。live D×5 側同理:cluster 現 2、settler 掃描門檻 60 約需再 ~ | ① 先把事實寫進計畫書時程表(H 軌首單 2026-08-03、36 clusters≈2029、D×5 真門檻 250≈2027 年中),不要再出現「近期可判」字樣;② 若要提早取得 H 軌證據,唯一乾淨路徑是 replay:為 own_stack_rolling 新增 replay 門(同上第 4 條的新 --preregister-replay 模式)並跑 `run_arena_replay.py --model own_stack_rolling --from 2015-01-01 --to 2026-06-30`——但引擎現以日頻迴圈+H_TD=5 寫死,須先把 horizon 參數化(新增 --horizon,預設 5) | 零 schema 變動(horizon_td 欄已在兩表);run_arena_replay.py 需 --horizon 參數化 |
| S | chronos2_market_5 是**第四支預訓練外隊但完全沒有 replay 路徑**:它有 live 門(dgate_a4_chronos2_5,approved)卻無 dgate_replay_*,且 2026-07-30 的 R3 發布日親驗補記只涵蓋 chronos_bolt_small/moirai2/timesfm 三隊,amazon/chronos-2 的發布日未查證→合法窗未知→引擎會 fail-closed 拒跑。另 moirai2_small_5 的 spec.provenance.license = **cc-by-nc-4.0**(非商用),若該隊將來過門,產品化路徑受授權阻斷——此約束目前只躺在 sp | ① 親驗 amazon/chronos-2 的 HF 發布日(web/HF model card,禁引記憶)→寫入 direction_arena_candidate.spec.provenance.release_date→新增 dgate_replay_chronos2_market_5_5(同第 4 條新模式)→跑合法窗重演;若查不到可靠發布日,依計畫 §七 R3 停損句「誠實棄」並在 note 欄留檔;② 在 scripts/arena_scoreboard.py 加一列授權揭露:對每隊讀 spec->'provenance'->>'license',非 apache-2.0/MIT 者於計分板標「授權受限(不可商用)」,讓 | 零 schema 變動(spec JSONB 內加鍵) |
| S | 重演帳本允許**跨批重複列**且門評不去重:PK 含 replay_run_id,故同一 (model,target,pred_date) 可在多批各存一份。實查 majority 之 pred_date 2026-06-30 同時存在 2 批(probe 批 rp_9552b636e4b9 與全窗批),該日 688 列=344 標的×2;evaluate_direction_gate.py:_fetch_samples 不 scope replay_run_id 也不 DISTINCT,這 344 列會**雙計進門評樣本**(majority 總列 1,391,879 比 momentum 1,391,535 多的正好是 344) | ① 在 scripts/migrate_arena_replay_ddl.py 的 --check 加一條稽核 SQL:`SELECT model_key, pred_date, count(DISTINCT replay_run_id) FROM direction_arena_replay GROUP BY 1,2 HAVING count(DISTINCT replay_run_id)>1`,非空即 exit≠0(可掛 cron/pre-commit,零 usage);② 在 evaluate_direction_gate.py replay 分支改用 `SELECT DISTINCT ON (model_key,target | 零 schema 變動(不可加 UNIQUE:那會擋掉合法的不同批重演) |
| S | futility 判停整條鏈**凍結三週從未實跑**:direction_arena_policy 已 frozen(futility_min_clusters=60、z=1.645,2026-07-12),direction_arena_verdict 卻 0 列;crontab 只掛了 run_arena_daily_pipeline(20:00)與 settle_arena_labels --run/--scoreboard(21:30),**沒有任何排程呼叫 arena_scoreboard.py --judge**。等於「連兩輪 excess 信賴上界<0 就建議停出新單」這個止損機制目前只是一支沒人按的按鈕。 | 在 21:30 那條 cron 尾端串接 `venv/bin/python scripts/arena_scoreboard.py --judge >> $HOME/logs/arena_settle.log 2>&1`(與結算同一 crontab 行、順序在 --scoreboard 之後);因 policy.futility_min_clusters=60 而現況 cluster=2,該支會誠實印「未達/判停停用」不寫任何列——正好可用來驗接線正確。驗收=log 出現 --judge 段輸出且 direction_arena_verdict 仍 0 列。 | 零 schema 變動;crontab 一行(機器本地,不隨 git,須同步記錄進 repo 的排程檔) |
| M | live 宇宙成分中途縮水且無逐 cluster 留痕:pred_date 07-15/16/27/28 皆 344 標的,**07-29 掉到 226**(pipeline log 同時顯示「宇宙:762 檔(PIT 成分,74 快照)」但「as-of=2026-07-29 宇宙 226 檔」、D 軌特徵 11 交易日×226 檔)。門評把不同宇宙的列 pool 在一起算 hit 與「同窗多數類基線」,成分變動會直接改變基線與相關結構(計分板自己揭露首批 DEFF≈43-53、有效 n≈8),但兩張帳本都沒有記錄「這個 cluster 用了哪個 universe 快照/幾檔」。 | ① 先診斷 226 是真宇宙變動還是 build_daily_direction_features 的覆蓋回歸:比對 `core_universe_asof` 於 2026-07-28 與 07-29 的快照檔數,再比對 daily_direction_feature_values 該兩日 distinct stock_id——若快照未變而特徵少了,是特徵側缺料 bug,修 writer 重建(#12 禁 hand-patch);② 不論結論,在出單時把宇宙指紋落帳:run_arena_round.py 寫入時同時記 universe 快照日與檔數(可放既有 direction_arena_prediction 無空欄,故建議新增輕 | **新表 arena_round_universe**(4 欄,PK=pred_date)——這是本主題唯一需要 schema 變動的缺口;其餘全部零 schema 變動 |
| M | 行走者⑦入口的程序增益門因 proc_sha 家族碎片化而不可判(與⑥共用 direction_gate,故連帶影響本主題之門評樹):meta_replay_perf 有 61 個 cutoff,卻散在 4 個 proc_sha 家族(n=30/22/8/1),門檻 n≥60(首期排除)——最大家族只到一半。每次程序碼變動就新開一個 proc_sha 家族、計數歸零,現行做法下永遠攢不到 60。 | 跑 reports/augur_all_evolution_next_steps_20260729.md 第 12 項已規畫的正式批:`python scripts/run_meta_replay.py --step month --from 2018-01-01 --to 2026-04-30`(單一新 proc_sha 一次跑滿 ~100 個月 cutoff,一次跨過 60),完成後 `python scripts/evaluate_meta_replay_gate.py --evaluate dgate_meta_replay_M1_gbdt --proc-sha <新 sha>` 與 B2_ridge 各一次(前置=樹淨,見 | 零 schema 變動 |

**機器可判驗收（可預先凍結）**
- A1 外隊 replay 落地:`SELECT model_key, count(DISTINCT pred_date) FROM direction_arena_replay WHERE model_key='chronos_bolt_small' GROUP BY 1` == 363,且 `SELECT weights_cutoff_ok, window_start, window_end FROM arena_replay_run WHERE model_key='chronos_bolt_small'` == (true, 2024-12-26, 2026-06-30)
- A2 as-of 零違例(全表恆為真):`SELECT count(*) FROM direction_arena_replay WHERE train_data_max_date <> pred_date` == 0
- A3 跨批零重複:`SELECT count(*) FROM (SELECT model_key,pred_date FROM direction_arena_replay GROUP BY 1,2 HAVING count(DISTINCT replay_run_id)>1) x` == 0(現值=1:majority@2026-06-30),且此查詢已成為 migrate_arena_replay_ddl.py --check 之一條、非空即 exit≠0
- A4 weights_cutoff_ok 真被讀:對一筆刻意以違窗參數跑出的 run(weights_cutoff_ok=false),`evaluate_direction_gate.py --evaluate <該隊門>` 之 result_snapshot.n_samples 必等於 true 列數、且 result_snapshot 含 excluded_illegal_window_n>0;現況基線=該鍵不存在(SQL 無此過濾)
- A5 門檻口徑單一來源:`python scripts/settle_arena_labels.py --scoreboard` 輸出之門檻數字 == `SELECT min((criteria->>'min_clusters')::int) FROM direction_gate WHERE status='approved' AND gate_id LIKE 'dgate_arena%'`(現況印 60、DB 為 250=不符),且 --selftest 之該條斷言改為比對 DB 讀值(現為字面 '確立門檻 60' 比對)
- A6 凍結判準可複現:對 6 支 dgate_replay_* 與 2 支 dgate_meta_replay_* 逐一跑 `preregister_direction_gate.py --check <gate_id>`,criteria_sha 覆算全部相符、exit 0(現況:該支無 replay 模式,8 門皆無法覆算)
- A7 部分窗不得終判:於 own_daily_rolling 重演未達 2,798 clusters 期間執行 `evaluate_direction_gate.py --evaluate dgate_replay_own_daily_rolling_5`,輸出須含「重演批未跑完(X/2798 日)——拒判,非 fail」且 `SELECT status FROM direction_gate WHERE gate_id='dgate_replay_own_daily_rolling_5'` 仍為 'approved';跑滿後同指令方得落 evaluated_pass/fail 且 result_snapshot.n_panels 
- A8 H 軌首單:2026-08-03 收盤後 `SELECT count(*), array_agg(DISTINCT horizon_td) FROM direction_arena_prediction WHERE model_key='own_stack_rolling'` > 0 且 horizons == {20,40,82}(現值 0 列)
- A9 futility 接線:2026-07-31 起 $HOME/logs/arena_settle.log 每交易日出現 arena_scoreboard --judge 段落,且 cluster<60 期間 `SELECT count(*) FROM direction_arena_verdict` 恆 == 0(接線正確且不誤判)
- A10 宇宙指紋:新表 arena_round_universe 於每個 pred_date 有且僅有一列,且 `SELECT count(*) FROM arena_round_universe u JOIN (SELECT pred_date,count(DISTINCT target_id) n FROM direction_arena_prediction GROUP BY 1) p USING(pred_date) WHERE u.n_targets <> p.n` == 0;226 檔事件之成因(宇宙變動 or 特徵缺料)以 SQL 證據入報告
- A11 樹淨前置可觀測:settler 自動觸發在裁判 exit≠0 時除 log 外另有可見失敗訊號(cron 非零退出或佇列列),驗收=人為造髒樹後跑 `settle_arena_labels.py --scoreboard` 且 cluster 已達門檻之情境下,失敗不只存在於 log 尾
- A12 程序增益門可判:`evaluate_meta_replay_gate.py` 無參數輸出中,某單一 proc_sha 之 B2_ridge 與 M1_gbdt n 皆 ≥60(現況最大 n=30),隨後兩門各落一次終判

<details><summary>本線誠實界限</summary>

取證界限與誠實說明:(1) DB 為 **live 實查**(psql -h 127.0.0.1 -U augur -d augur;注意 .env 未設 hugo role,直接 `psql -d augur` 會 FATAL),所有列數/門態/criteria/result_snapshot 皆本次實際查詢所得,非讀 DDL 推測;三支 script 之無參數唯讀模式(run_arena_replay、evaluate_meta_replay_gate)實跑取現況。(2) own_daily_rolling 重演之 ETA(≈93h、≈2026-08-03)是以單點取樣推算:PID 2980944 於 02:46 起跑、11:49 查得 248/2798 clusters,推得 27.4 clusters/h;**未做第二次取樣驗證速率穩定性**,且後段年份宇宙較大只會更慢,故 93h 應視為下界。(3) 「W1 全窗 560 批、百分位中位 41.9、Bonferroni 低端 9.6%」與「11.5 年計分板三隊命中/Brier」係引用 reports/arena_replay_first_readings_20260730.md(doc 級),本次**未親自重跑 verify_arena_watchlist --replay-adjunct 覆算**;W1/W2 live 側計數(達標 0/3、紅旗 1 批)引用 reports/arena_watchlist_verification_20260728.md,亦未重跑。(4) chronos_bolt_small/moirai2/timesfm 三隊之權重發布日採計畫書 2026-07-30 補記所載親驗值(2024-11-26 / 2025-08 / 2025-09),本次**未再次向 HF 查證**;amedon/chronos-2(chronos2_market_5)發布日**查無**——repo 與 DB 皆無記載,故其合法窗無法計算,已列為缺口。(5) 07-29 宇宙 226 檔 vs 前四批 344 檔為 DB 實查事實,但**成因未診斷**(未比對 core_universe_asof 快照與 daily_direction_feature_values 覆蓋),缺口中只寫成「先診斷再落指紋」而非斷言為 bug。(6) 跨批重複只實查了 majority 在 2026-05-01..06-30 區間(得 2026-06-30 雙批 688 列);**全表 dup 掃描因逾時未完成**,故「量級 0.02%」是由總列數差(1,391,879 − 1,391,535 = 344)推得而非全表實查。(7) 三支 evaluate/settle 之 --selftest 本次**未執行**,關於斷言強度之判讀(如 :296 字面比對)出自讀碼而非跑測。(8) 未查證的鄰接面:live D×5 六門之 power_disclosure 數字(MDE 6.24/8.44pp)是否曾以現行樣本重算、`judgestop_threshold.calib_late_ece_ceiling` live 值是否仍為 0.05、以及 direction_arena_prediction 兩支 trigger 函式本體是否真能擋回填(只讀了 trigger 名稱未讀函式體)。

</details>

---

### 8.7 ⑦迭代程序 META-REPLAY

*行走者⑦ 迭代程序本身（META-REPLAY 程序重演）：M2 月頻掃描現位、n<60 不可判、與「下一步該掃什麼」的實作級事實*

**既有表（6）**：`meta_replay_cutoff`（4 家族／共 61 列（2026-07-30 11:46 親查）：2052dfa7de64=1（probe-one @2）、`meta_replay_perf`（122 列。可判性關鍵：b859d95b4706 每模型 22 列中僅 15 列 ic_next 與 ic_next_s）、`direction_gate（track='M' 兩列）`（dgate_meta_replay_B2_ridge（criteria_sha 7738586f7371）、dgate_）、`core_universe_asof`（102 panel、2018-01-31 → 2026-06-30（全月底）；窗內（2018-01-01～2026-04）、`feature_values`（DISTINCT feature = **38**（計畫書 §二寫「35 產生器」→ 文件與 live 不一致，見 ga）、`meta_replay 兩表之 DB 閘（查無）`（0 個 trigger）

**既有 script（11）**：`run_meta_replay.py`、`evaluate_meta_replay_gate.py`、`migrate_meta_replay_ddl.py`、`baseline.py`、`walkforward.py`、`verify_candidate_promotion.py`、`verify_sign_consistency.py`、`migrate_honesty_guards_ddl.py`、`augur_meta_replay_plan_20260729.md`、`augur_all_evolution_next_steps_20260729.md`、`replay_knowhow_run.py`

**缺口與可開工下一步（10）**

| 工 | 缺什麼 | 可開工的第一步 | 需要的表／欄 |
|---|---|---|---|
| S | G1 季頻家族結構性不可判、且 static 全 NULL：974f53b32e29 有 30 期 ic_next（58/60 非空）但 ic_next_static 0 非空（撞 e0aa0e8 修正前的「靜態基準＝首 cutoff（空集）」bug）；更根本地，月底網格中季頻 cutoff 上限僅 33 期 < min_clusters=60 → 季頻家族**永遠 undecidable**，計畫 §七 M2 的「季頻 34 cutoff 驗收」與 §六 n≥60 判準互斥。三個死家族（2052dfa7de64/8113c670241d/974f53b32e29）在帳本裡與活家族混列、無狀態標記。 | 新增 scripts/migrate_meta_replay_family_ddl.py 建家族登錄表並回填 4 列；再改 scripts/evaluate_meta_replay_gate.py 之 evaluate()：查 meta_replay_family.status，若 in ('retired','engine_probe') 直接 exit 1 印「該家族已退場不開判」。不回填 974f 的 static（省算力：即使補齊 n≤32 仍不可判）。 | 新表 meta_replay_family(proc_sha TEXT PRIMARY KEY, git_sha TEXT, step TEXT, window_from DATE, window_to DATE, pool_n INT, panels_n INT, machin |
| M | G2 M2 月頻吞吐在現行實作下不可行：b859d95b4706 於 09:00:25 啟動，09:07 前 8 期瞬完（prodset 空＝bootstrap），此後逐期變慢——2019-09-30 耗 17m29s、2019-10-31 耗 26m29s（各僅 1 個 gate2 候選＝4 次 run_ladder），第 23 期（2019-11-30）自 10:37 起已跑 >73 分未落列。成本主因：run_ladder 每次重跑全部 k 折、每折 _fold_xy 重載 → 單期 ~O(k²)，k 由 22 長到 100。窗內共 100 期、現 22 期。 | 在 src/augur/evaluation/baseline.py 之 run_ladder **內部**加 module 級 fold 快取（key=(tuple(feats), test_pd, tuple(train), seed, asof, robust)，值＝該折四模型 rank IC），並加 models 參數預設四模型、由 meta 側傳 ("B2_ridge","M1_gbdt") — 但**呼叫端簽名與 run_meta_replay.py 源碼一字不改**，因 compute_proc_sha 只雜湊 gate1_hac/label_guarded_train/run_cutoffs（run_meta_rep | 零 schema 變動（純 code：baseline.run_ladder 加 fold_cache/models；新增落盤 helper） |
| S | G3 proc_sha 射程不足＝「中途任何變動＝新 sha」的宣稱不成立：compute_proc_sha 只雜湊 gate1_hac、label_guarded_train、run_cutoffs 三者源碼，**未含同檔的 next_panel_ic（績效量測本體）**，亦未含全部復用機具（baseline.run_ladder / baseline._fold_xy / walkforward.splits / metrics.effective_t_hac / metrics.rank_ic / vss.judge_sign / vcp._asof_ic_series）。且 meta_replay_cutoff 無 git_ | 新增 scripts/verify_meta_replay_provenance.py：以 inspect.getsource 對上列 6 個復用 callable ＋ next_panel_ic 併算 machinery_sha（sha256 前 12 碼）、取 git rev-parse --short HEAD，(a) 無參數＝印當前 machinery_sha 與家族表登錄值之比對表；(b) --pin <proc_sha> 寫入 meta_replay_family.machinery_sha/git_sha；(c) --require <proc_sha> 不符即 exit 1。並在 evaluate_meta_repl | meta_replay_family.machinery_sha / git_sha 欄（同 G1 一張新表即含） |
| S | G4 判準缺「開判時點」凍結規則 → 一次性終態門何時開火屬人為裁量（挑 n 剛好好看的時點＝p-hacking 面）。live criteria 只有 min_clusters=60、fail_path、三關；無 stopping rule。b859 掃到約第 68 期（≈2023-08-31）就會湊到 61 對非空樣本，可提前開判並永久鎖死結論，放棄後段 32 期資訊。且 direction_gate trigger 禁止 approved 後改 criteria/criteria_sha（migrate_direction_gate_ddl.py:51-54），故規則不能塞進 criteria。 | ① 走人閘：以 governance_queue CLI 開一案「META-REPLAY 開判時點凍結」，內容＝『唯家族掃完窗內全 100 期（cutoff 達 2026-04-30）後開判；屆時 n<60 仍記 undecidable、不得以中途 n≥60 提前開判』，hugo 親簽後寫入 direction_gate.note（note 未被 trigger 凍結，approved 列可 UPDATE）。② scripts/evaluate_meta_replay_gate.py 加 --require-complete-window（預設開）：SELECT count(*) FROM meta_replay_cutoff WH | 零 schema 變動（用 direction_gate.note ＋ evaluate 新旗標；家族窗界可讀 meta_replay_family.window_to） |
| S | G5 evaluate 腳本兩處自身可驗缺陷：(a) status() 印「perf: b859d95b4706 B2_ridge n=22（門檻 60+首期排除）」，但 evaluate() 實際樣本要求 ic_next 與 ic_next_static 皆非空再扣首期＝**14**，讀數高估 8 期＝假可判感；(b) docstring 宣稱「守 #15（不可判誠實／**判準 sha 核對**）」，但 evaluate() 只讀 criteria/status，全程未比對 criteria_sha（既有可抄的模式：scripts/preregister_arena_admission_gate.py:33 SOURCE_SHA  | 改 scripts/evaluate_meta_replay_gate.py：(a) status() 之 SQL 加 「AND ic_next IS NOT NULL AND ic_next_static IS NOT NULL」並印 usable=count-1；(b) 檔頭加 EXPECTED_CRITERIA_SHA={'dgate_meta_replay_B2_ridge':'7738586f7371','dgate_meta_replay_M1_gbdt':'27a787ecd09d'}，evaluate() 讀到的 criteria_sha 不符即 print+return 1；(c) _selftest() 加兩鎖： | 零 schema 變動 |
| S | G6 meta_replay 兩表零 DB 閘：pg_trigger 實查 0 個。帳本可被裸手 DELETE/UPDATE 默改，與 trial_ledger/revalidation_baseline（雙閘）及 PME 八表（delete-only）標準不一致——而這兩表正是 meta 門唯一樣本來源。 | 改 scripts/migrate_honesty_guards_ddl.py：PME_TABLES 追加 ('meta_replay_cutoff','meta_replay_perf')（delete-only 版即足——perf 走 ON CONFLICT DO NOTHING、cutoff 走純 INSERT，無合法 UPDATE 路徑；若日後要 backfill static 再改走 GUC 版），同步把 _selftest 的「PME 八表全覆蓋」斷言改為十表並逐表列名；跑 --check → --apply。 | 零新表（只加 trigger） |
| M | G7 M2 這一趟 run 幾乎零觀測性與零重啟韌性：stdout/stderr 皆指向匿名 pipe（/proc/3136966/fd/1 → pipe:[13998785]），**無 log 檔**；crontab 查無任何 meta/replay 條目 → 停電或重開機後不會自動續跑；帳本只有 computed_at，無逐期耗時／當時負載／ladder 呼叫數 → ETA 只能從 computed_at 差值反推且被機器競爭污染。 | ① 新增 scripts/report_meta_replay_progress.py（唯讀、零 usage）：由 meta_replay_cutoff.computed_at 差值算逐期耗時、已完成期數/窗內總期數、以 O(k²) 與 O(k) 兩情境給 ETA 區間、印當前家族 usable n；--watch 每 N 分附 load1 追加到 log。② 新增 scripts/run_meta_replay.sh 包裝：flock 車道鎖＋nice -n 10＋輸出到 /tmp/augur_logs/meta_replay_<proc_sha>_<YYYYMMDD>.log，並掛 @reboot cron 續跑（resume  | 旁表 meta_replay_runlog(proc_sha TEXT, cutoff_date DATE, elapsed_sec NUMERIC, load1 NUMERIC, observed_at TIMESTAMPTZ DEFAULT now(), PRIMARY KE |
| S | G8 車道規則實測被違反，M2 是被競爭壓住而非只是慢：11:50 親查 load average 30.60（12 核），同時在跑 ollama llama-server 510% CPU、embed_knowledge.py --gap-fill 291%、run_arena_replay.py own_daily_rolling 193%、run_meta_replay 僅 145%。本機為單通道記憶體（無獨顯、無 AVX-512），LightGBM＋DB 矩陣載入屬記憶體頻寬敏感 → 四作業互搶使單期耗時 17→26 分的斜率無法歸因於 k²。總控計畫 §二已成文「sklearn 道互斥」，但無機械執行。 | 在 run_meta_replay.py / run_arena_replay.py / 其他呼叫 baseline.run_ladder 的長跑入口，於 main() 取 flock('/tmp/augur_lanes/sklearn.lock', LOCK_EX／LOCK_NB)：取不到即印「sklearn 道占用中（持鎖 PID/腳本），排隊或稍後重入」並 return 0（graceful，非 traceback）。⚠ 這會改 run_meta_replay.py 源碼——但 flock 若寫在 main() 而非 run_cutoffs/gate1_hac/label_guarded_train 之內，**不進 proc_ | 零 schema 變動（檔案鎖；建目錄 /tmp/augur_lanes/） |
| M | G9 M1_gbdt 之 ic_next 為單 seed 抽樣，違 #11「含隨機性之 production metric ≥3 次取統計」：next_panel_ic 只以 seed=42 fit 一次 LGBM（run_meta_replay.py:87-90），而 dgate_meta_replay_M1_gbdt 整門建在這條單抽序列上（gate2 的增量關另用 2 seeds，但門的樣本不是）。 | 呈 hugo 二擇一（決策層）：(甲) b859 家族照跑，門評報告與 result_snapshot 明列「M1_gbdt 為單 seed(42) 抽樣，過門只作『觀察級』、不入確立級」；(乙) 開新家族：next_panel_ic 改 seeds=(42,43,44) 取 median、並把三值寫 meta_replay_perf.ic_next_seeds JSONB — **走 (乙) 前必須先修 G3**，否則 next_panel_ic 不在雜湊內 → 同一 proc_sha 底下混入兩種語意的 ic_next＝帳本污染。 | (乙) 才需：ALTER TABLE meta_replay_perf ADD COLUMN ic_next_seeds JSONB（可空、舊列留空＝誠實標示單抽） |
| S | G10 計畫書 §二/§七 與 live 三處不符（會讓「可直接開工」的下一份計畫書照抄錯數字）：① §二稱資料地板『core_universe_asof 起 2014-12』，live 網格起 2018-01-31（102 panel 至 2026-06-30）；② §二稱候選池『35 產生器特徵』，live DISTINCT feature=38；③ §七 M2 驗收寫『帳本 34 期滿』，但月底網格季頻上限 33 期且 <60 恆不可判（同 G1）。 | Edit reports/augur_meta_replay_plan_20260729.md：§二資料地板改為「core_universe_asof live 網格 2018-01-31→2026-06-30、102 panel（月底）」；候選池改「38（live DISTINCT feature，隨 feature_values 增減；池變＝proc_sha 分家）」；§七 M2 一列改為「季頻僅作引擎試跑（engine_probe），**不作門評樣本**——季頻上限 33 期 < min_clusters 60」，並把 M4 月頻由『條件細化』改為『唯一可判路徑』。每處後面貼上取數 psql 指令，供下次覆核。 | 零 schema 變動（純文件對真；屬 CLAUDE #26『改正確／補完整』執行層，不改判準） |

**機器可判驗收（可預先凍結）**
- A1 可判樣本讀數一致：`python scripts/evaluate_meta_replay_gate.py` 印出的每家族 usable 數，必等於 evaluate() 內 diffs 長度（同 WHERE：ic_next IS NOT NULL AND ic_next_static IS NOT NULL，再扣首期）。凍結現值：b859d95b4706 兩模型皆 usable=14、974f53b32e29 皆 usable=0（static 全 NULL）。
- A2 家族登錄完整：`SELECT count(*) FROM meta_replay_family`=4，且 status='engine_probe' 或 'retired' 之列恰含 2052dfa7de64、8113c670241d、974f53b32e29；b859d95b4706 為 'running'。對 retired/engine_probe 之 sha 下 --evaluate 必 exit≠0 且 direction_gate.status 維持 'approved'。
- A3 fold 快取數值等價：對同一 (feats, panels_k, seed)，開快取與關快取之 run_ladder 回傳 B2_ridge/M1_gbdt 之 mean_ic 絕對差 < 1e-12（新增比對腳本或 selftest 紅綠）。
- A4 fold 快取效能達標：加快取後，第 40 期之單 cutoff wall-clock（由 meta_replay_cutoff.computed_at 差或 meta_replay_runlog.elapsed_sec 判）≤ 加快取前第 22 期實測 26m29s 的 1.5 倍（≤ 39m45s）。
- A5 proc_sha 對帳鎖：人為改動 baseline.run_ladder 任一行後，`python scripts/verify_meta_replay_provenance.py --require b859d95b4706` 必 exit≠0；未改動時 exit 0。
- A6 誠實閘上線：psql 執行 `DELETE FROM meta_replay_cutoff WHERE proc_sha='b859d95b4706'` 與 `DELETE FROM meta_replay_perf WHERE proc_sha='b859d95b4706'` 皆回 EXCEPTION（訊息含表名）；`migrate_honesty_guards_ddl.py --check` 列出兩表 trigger 已在。
- A7 判準 sha 核對鎖：evaluate() 遇 criteria_sha ≠ {B2_ridge:7738586f7371, M1_gbdt:27a787ecd09d} 即 exit≠0，且不寫 direction_gate。
- A8 開判時點硬鎖：對尚未掃完窗內全 100 期之家族下 --evaluate，必 exit≠0 印「窗未掃完不開判」，且門狀態仍為 approved、evaluated_at 仍 NULL。
- A9 開判前置樣本量：b859 掃至 cutoff=2026-04-30 後，`SELECT model,count(*) FROM meta_replay_perf WHERE proc_sha='b859d95b4706' AND ic_next IS NOT NULL AND ic_next_static IS NOT NULL GROUP BY 1` 每模型 ≥61（扣首期後 n≥60）才允許開判；否則裁決必為 undecidable 且不落終態。
- A10 車道鎖：同一 lane 之第二支腳本啟動後 5 秒內以 exit 0 離場、印出持鎖者資訊，且不呼叫 run_ladder（可用 lock 檔存在性＋log 斷言驗）。
- A11 三支腳本 --selftest 續全綠且鎖數不減：run_meta_replay ≥9 鎖、evaluate_meta_replay_gate ≥8＋新增 2 鎖（sha 核對／status-evaluate SQL 一致）、migrate_meta_replay_ddl ≥4 鎖；`python3 scripts/check_cmd_matrix.py` exit 0（新增腳本皆須帶執行指令矩陣＋--selftest）。

<details><summary>本線誠實界限</summary>

誠實界限（逐條）： (1) **未開判**：我沒有跑 `--evaluate`（終態不可回改，且 b859 現 usable n=14 < 60，必回 undecidable）。門狀態現為 approved／evaluated_at NULL，親查所得。 (2) **ETA 是估算不是量測**：帳本無逐期計時欄，我以 computed_at 差值反推（第 22 期 26m29s、第 21 期 17m29s、第 23 期自 10:37 起 >73 分未落列）。若假設單期 ~O(k²)、k 由 22→100 且無競爭，單期在 k≈100 時約數小時、剩 78 期合計約 10-15 天；此數**同時被機器競爭污染**（11:50 load 30.60/12 核、四大作業並行），故只能當量級參考，不得寫進計畫書當承諾。要得到可信數字須先做 G7 的 runlog。 (3) **974f53b32e29 之 static 全 NULL 成因為推論**：依 commit e0aa0e8（2026-07-30 08:08「靜態基準錨改首個非空 prodset」）＋該家族最後寫入 08:40（行程啟動早於修正、Python 不熱更新）＋語意一致；我沒有回溯執行舊碼證明。 (4) **b859d95b4706 是否等於現 HEAD 碼所生的 sha，我沒有重算**（重算須跑引擎、佔 sklearn 道）。可推論其已含 e0aa0e8 修正（22 期中 15 期 static 非空）。這也正是 G3 要補的對帳缺口。 (5) **pool=38 是「現在」的值**：feature_values 無時間戳欄，無法查證 09:00 啟動當時池是否也是 38；若期間有新特徵落地，任何重啟都會產生新 proc_sha 而使 22 期停在原家族（G3/G7 的 --require 對帳即為此設）。 (6) **查無項**：crontab 無任何 meta/replay 條目（grep 空）；meta_replay 兩表 pg_trigger 空集；reports/augur_open_problems_schedule_20260730.md 全文 grep「meta」查無；audits/ 僅 SH-ASOF-WRITE-CLOSED-20260729.md 提及 `meta_replay_` 前綴（predict role 授權盤點），非未結項；無 `ladder_cache` 之持久化表（全 repo grep 僅 run_meta_replay.py:119/162-165 之記憶體 dict）。 (7) **run_meta_replay.py:119 註解與實作不符**（已核）：ladder_cache key 含 tuple(panels_k)，而 panels_k 每 cutoff 都變 → 「跨 cutoff 重用」實際命中率 0，只在同一 cutoff 內讓 baseline ladder 少算 (候選數−1)×2 次。此為 G2 最大槓桿的依據。 (8) **compute_proc_sha 射程已逐字核對**：`for fn in (gate1_hac, label_guarded_train, run_cutoffs)`——next_panel_ic 與所有跨檔機具都不在內。這使 G2/G8 的改動可以「不分家」執行（優點），同時使「中途任何變動＝新 sha」的宣稱不成立（缺口）；兩件事是同一枚硬幣，計畫書須同時寫。 (9) 三支腳本的 --selftest 我親跑全綠（4/9/8 鎖），DDL 冪等；DB 讀取一律以 .env 之 DB_USER=augur 連 127.0.0.1（直接 `psql -d augur` 會因 role hugo 不存在而失敗，後續腳本請沿用 PGPASSWORD 取自 .env 的方式）。 (10) scripts/replay_knowhow_run.py 名稱含 replay 但屬 KH9 synthesis，與行走者⑦無關，已排除。

</details>

---

### 8.8 ⑧法律自己

*行走者⑧法律自己(人閘 + 治權機械閘)——實作級現況與缺口盤點*

**既有表（9）**：`governance_proposal`（3 列(1 rejected + 2 enacted;0 pending)）、`deliberation_escalation`（218 列;未決 124(undecidable 87 / red_line_category 35 / no_orac）、`steward_question_ledger`（1280 列:superseded 845 / queued_for_claude 225 / awaiting_hug）、`local_model_version`（4 列(全 retired;其中 1 列 promoted_by IS NULL)）、`promotion_queue`（310 列）、`trial_ledger`（32 列）、`evolution_prereg_gate`（(未計列數)）、`append-only 誠實帳本群(honesty_delete_only_guard,全拒 DELETE/TRUNCATE)`（14 表 × row+truncate 雙觸發器）、`門柱鎖群(*_no_goalpost / *_immutable / *_frozen)`（public schema 非內部觸發器共 68 個）

**既有 script（13）**：`governance_queue.py`、`preregister_direction_gate.py`、`curation.py`、`deliberate.py`、`check_cmd_matrix.py`、`check_treaty_refs.py`、``、`github-workflow.yml`、`run_evolution_chain.sh`、`apply_evolution_promotions.py`、`verify_evolution_acceptance.py`、`evolve_cycle.py`、`run_raw_evolution_iteration.py`

**缺口與可開工下一步（7）**

| 工 | 缺什麼 | 可開工的第一步 | 需要的表／欄 |
|---|---|---|---|
| S | **人閘人簽可被裸 SQL 自蓋(最重缺口;親驗 CONFIRMED)**。governance_proposal_immutable 只鎖 DELETE／diff+evidence+kind 凍結／終態(rejected,enacted);對 status pending→approved 與 decided_by 之寫入**零管制**。親驗(rolled-back tx):`INSERT ... status 預設 pending` 後 `UPDATE governance_proposal SET status='approved', decided_by='hugo'` → UPDATE 1、回讀 status=approv | 雙層封:①`scripts/governance_queue.py` 之 `decide()` 開頭插 direction_gate 同款 fail-closed 閘——`if not sys.stdin.isatty(): sys.exit('✗ approve/reject 唯決策層人(TTY 閘;AI/腳本 fail-closed 拒)')`,並在 `selftest()` 加紅綠:以 `subprocess` 用 `stdin=DEVNULL` 跑 `--approve __probe__` 斷言 exit≠0 且輸出含 TTY 字樣。②新增 `scripts/migrate_governance_humansign_ddl | 零新表。改 1 支既有 script(governance_queue.py)+ 新增 1 支 migrate DDL(僅 CREATE OR REPLACE FUNCTION,不動欄位) |
| S | **local_model_version 晉升人簽可由 INSERT 全繞(親驗 CONFIRMED)**。model_version_no_goalpost 為 `BEFORE DELETE OR UPDATE`,**不含 INSERT**;其人簽要求之條件更僅限 `NEW.status='serving' AND OLD.status='candidate'`。親驗(rolled-back tx):`INSERT INTO local_model_version (version_id,base_model,status) VALUES ('__probe_bypass__','probe','serving')` → INS | 新增 `scripts/migrate_model_version_insert_guard_ddl.py`:(a) 觸發器改掛 `BEFORE INSERT OR UPDATE OR DELETE`;(b) 函式內把人簽判準改為與 OLD 無關之終局條件——`IF NEW.status='serving' AND (NEW.promoted_by IS NULL OR NEW.promoted_at IS NULL) THEN RAISE EXCEPTION ...` (TG_OP='INSERT' 時 OLD 為 NULL,現行 `OLD.status<>'candidate'` 比較會 NULL→false 而靜默放行,須改寫 | 零新表。新增 1 支 migrate DDL;新增 1 個 CHECK constraint;改寫 1 個既有 trigger function 與其掛載事件 |
| M | **人裁佇列自身無誠實閘、且積壓無告警(親驗 CONFIRMED)**。deliberation_escalation 是治權觸線之強制人裁落點(red_line_category),卻是全 16 張 deliberation_* 表中**零觸發器**者之一:親驗 `DELETE FROM deliberation_escalation WHERE escalation_id=(SELECT min(...))` → DELETE 1 成功(218→217);且 claim_id 為 `ON DELETE CASCADE`,刪 claim 即連帶靜默消滅其 escalation。現況未決 124 筆(含 red_line_categ | ①新增 `scripts/migrate_escalation_honesty_ddl.py`:對 deliberation_escalation 掛 honesty_ledger_guard(既有函式可直接複用,DELETE/TRUNCATE 拒、UPDATE 須 GUC),並把 claim_id FK 由 `ON DELETE CASCADE` 改 `ON DELETE RESTRICT`(留痕優先於級聯清理)。②新增 `scripts/verify_human_gate_backlog.py`(唯讀哨兵、零 usage):印三佇列未決數與最舊未決天數——deliberation_escalation(NOT resolved) | 零新表。新增 2 支 script(1 DDL + 1 哨兵);改 1 個 FK 之 ON DELETE 行為;改 run_evolution_chain.sh 加一段 |
| S | **全 repo 零 CI／零 pre-commit——所有治權機械閘皆須靠人記得手跑**。實查:`.github/workflows/` 不存在(`.github/` 僅 README.md)、無 `.pre-commit-config.yaml`、無 `.git/hooks/pre-commit`;grep 全 repo 無任何檔案呼叫 check_cmd_matrix／check_treaty_refs／constitution_lint。四支已寫好且現正全綠之稽核器(check_cmd_matrix 425/0、check_treaty_refs 全綠、constitution_lint report 7/7 PASS)因此 | 新增 `scripts/install_git_hooks.py`(冪等、可 --uninstall、零 usage),寫入 `.git/hooks/pre-commit` 依序跑:`python3 scripts/check_cmd_matrix.py --quiet` → `python3 scripts/check_treaty_refs.py --json` → `python3 -m tools.constitution_lint report`(三者現皆 exit=0,故上閘當下即綠、不阻塞既有工作);任一 exit≠0 即拒 commit。**暫不納 constitution_lint --selftest**(現 e | 零新表。新增 1 支 install script + 1 份 ops/hooks/pre-commit;不動 DDL |
| S | **CI 接線之公告阻卻已過期,真阻卻縮為單一過時斷言**。github-workflow.yml 檔首橫幅稱「現行生效規格於 WM.44-LABEL 尚有未結之 error,照原樣接線將立即全紅(阻斷全部 push／PR)」並列 L2–L7 六份 ❌ FAIL;但親跑 `python3 -m tools.constitution_lint report` 實得 **PASS 7／FAIL 0、error 合計 0、exit=0**(橫幅內 `<!--lint:-->` 綁定值亦已同步為 0,與其散文敘述自相矛盾)。真正殘留阻卻僅 `--selftest` 之 exit=1,且該 FAIL 為**斷言前提過時**:`tools/co | 改 `tools/constitution_lint/selftest.py:566-572`:把 G10 界線鎖改為前提守衛式——`if "DRAFT" in l5_text: chk("G10 界線:...", not any(f.kind.startswith("status_") ...))` `else: chk("G10 界線前提已解除(TR.Z 殘餘 DRAFT 不存在,RULING-2026-029);本鎖不適用", True)`(不得逕刪該 chk,否則 TR.Z 殘餘若再現將無鎖);併更新 github-workflow.yml 橫幅散文使其與 `--sync` 值一致(現 7/7 PASS/0 error),再 | 零新表。改 1 支既有模組(selftest.py 1 處斷言)+ 1 份 yml 橫幅散文 |
| M | **人閘提案來源尚無自動投遞——進化迴圈與人閘正典表完全斷線**。grep 全 repo:引用 governance_proposal 者僅 2 檔(`scripts/governance_queue.py` 與 `scripts/migrate_ai_evolution_ddl.py`),即除 CLI 與建表 DDL 外**零呼叫端**。run_evolution_chain.sh 八段(cron 01:30)註解書明「晉升永遠人閘」,實作卻只 `grep -E "version／gold\["` 印待簽現況;evolve_cycle.py／run_raw_evolution_iteration.py 之人閘亦僅為「印 SQL 供 | 新增 `scripts/submit_governance_proposal_from_evolution.py`(投遞器,唯寫 pending、絕不碰 status/decided_by):(a) `--from-escalation <id>` 讀 deliberation_escalation 未決之 red_line_category 列,組 diff_text(payload 之宣稱+oracle 裁決)、evidence_refs(session_id/claim_id),kind 依 reason 映射(red_line_category→criteria_change);(b) `--from-model-candi | 零 schema 變動(governance_proposal 現有欄位足用:kind/title/diff_text/evidence_refs/proposed_by='claude'/status 預設 pending)。新增 1 支 script + run_evolut |
| M | **promotion_queue 之 decided_by 預設即 'evolution_engine',機械晉升與人簽晉升共用同一欄而無型別區分**。DEFAULT `'evolution_engine'::varchar` 且 NOT NULL,apply_evolution_promotions.py:270/:372 亦寫入該值;verify_evolution_acceptance.py:141 之偵測器僅查 `decided_by IS NULL`,故機械決策永遠「有值」=永遠通過該偵測。無欄位可機械區分「此列係 PME-AUTO-B 閘內狀態晉升(執行層,合法)」與「此列係判準變更(須人閘)」,亦無 FK 連回 go | 新增 `scripts/migrate_promotion_decision_provenance_ddl.py`:對 promotion_queue 加 `decision_channel text NOT NULL DEFAULT 'auto_gate' CHECK (decision_channel IN ('auto_gate','human_gate'))` 與 `proposal_id text REFERENCES governance_proposal(proposal_id)`,併加 CHECK `(decision_channel='auto_gate' AND proposal_id IS NULL) OR ( | promotion_queue 加 2 欄 + 2 CHECK + 1 FK(310 列,ALTER 加 DEFAULT 欄在 PG11+ 為 metadata-only、快);新增 1 支 migrate DDL;改 1 支既有 verify script |

**機器可判驗收（可預先凍結）**
- A1 人簽 TTY 閘(機器判):`python scripts/governance_queue.py --approve <任一 pending id> < /dev/null` 於非 TTY 下 exit≠0 且 stderr 含「TTY」;同令於 TTY 下對 pending 列 exit=0。凍結判準:非 TTY 路徑 exit≠0 為必要條件。
- A2 人簽 DB 閘(機器判):於 psql 裸連線內 `BEGIN; INSERT 一筆 pending 提案; UPDATE governance_proposal SET status='approved', decided_by='hugo' WHERE ...;` 必 RAISE EXCEPTION(訊息含 augur.human_sign);同一 UPDATE 前加 `SET LOCAL augur.human_sign='on'` 則成功。二者皆 ROLLBACK。(本輪已親驗現況為「無閘、UPDATE 1 成功」,故此判準為真實紅→綠轉換,非既綠。)
- A3 model_version INSERT 閘(機器判):`BEGIN; INSERT INTO local_model_version (version_id,base_model,status) VALUES ('__probe__','probe','serving'); ROLLBACK;` 必 RAISE EXCEPTION(含 promoted_by／人簽字樣)。(本輪親驗現況為 INSERT 0 1 成功=紅。)
- A4 人裁佇列誠實閘(機器判):`BEGIN; DELETE FROM deliberation_escalation WHERE escalation_id=(SELECT min(escalation_id) FROM deliberation_escalation); ROLLBACK;` 必 RAISE EXCEPTION(含 append-only／誠實帳本閘)。(本輪親驗現況為 DELETE 1 成功=紅。)
- A5 INSERT 盲區普查(機器判、預先凍結):新增自測斷言——凡 public schema 中 trigger 名含 no_goalpost／immutable／frozen 且其函式體含 'promoted_by' 或 'approved_by' 或 'decided_by' 者,其 tgtype 必含 INSERT 位。以 `SELECT count(*) FROM pg_trigger t JOIN pg_proc p ON p.oid=t.tgfoid WHERE NOT t.tgisinternal AND (pg_get_functiondef(p.oid) ~ '(promoted_by／approved_by／
- A6 三稽核器全綠且受 pre-commit 阻擋(機器判):`bash ops/hooks/pre-commit` exit=0;且刻意造一支缺矩陣之 scripts/__probe.py 後同令 exit≠0(驗閘真會紅、非空轉綠燈)。凍結基線:check_cmd_matrix 受檢≥425／缺漏 0;check_treaty_refs 全綠;constitution_lint report PASS 7／FAIL 0／error 0。
- A7 constitution_lint --selftest exit=0(機器判)。且回歸鎖:人工於 L5 規格暫時插回 `### TR.Z …（DRAFT）` 字樣後,G10 界線鎖須仍能判(不得因前提守衛化而變成永久不適用之空轉)——以 selftest 內合成暫存檔實現,不改動 specs/ 真檔。
- A8 自動投遞器不能自簽(機器判):`python scripts/submit_governance_proposal_from_evolution.py --selftest` exit=0,其中一項斷言為「本檔原始碼不含任何同時出現 UPDATE governance_proposal 與 (status='approved'／decided_by) 之語句」;另跑 `--from-escalation <id>` 兩次,governance_proposal 列數只增 1(_pid 冪等)、且該列 status='pending' AND decided_by IS NULL。
- A9 人閘積壓哨兵可判(機器判):`python scripts/verify_human_gate_backlog.py` 印三佇列未決數與最舊未決天數,exit 依閾值。凍結本輪基線供對照:deliberation_escalation 未決 124(red_line_category 35)／steward_question_ledger awaiting_hugo 149 + pending 61／governance_proposal pending 0。閾值本身須 hugo 拍板後才凍結(屬判準)。

<details><summary>本線誠實界限</summary>

【取證方式】DB 為 live 親查(`psql -h 127.0.0.1 -U augur -d augur`;注意預設 `psql -d augur` 會因 role \"hugo\" 不存在而失敗,須帶 -U augur,憑證在 .env)。三個「可繞過」缺口皆以 **rolled-back transaction 親驗**(BEGIN…ROLLBACK,未留任何資料),非讀 DDL 推論——A2/A3/A4 之現況紅燈是實測結果:裸 SQL 自簽 UPDATE 1 成功、直插 serving INSERT 0 1 成功、裸刪人裁佇列 DELETE 1 成功。  【已親跑之 exit code】check_cmd_matrix.py --quiet exit=0(425/0);check_treaty_refs.py exit=0(全綠);`python3 -m tools.constitution_lint report` exit=0(7/7 PASS、error 0);`--selftest` exit=**1**(1 FAIL:G10 界線)。⚠ 取 exit code 時不可接 pipe(`／ tail` 會回 tail 之 exit 而非 python 之;本輪初次即因此誤讀為 exit=0,已改導檔重測校正)。constitution_lint report 輸出自附 `git HEAD 403ac97…+dirty`——工作區不乾淨,該輸出無法僅由該 SHA 重現。  【誠實界限】(1) `promotion_queue.action` 之值域分布**未查**,故 gap 7 之「哪些 action 屬判準變更」無法凍結,已標為須 hugo 拍板。(2) `evolution_prereg_gate`、`trial_ledger` 僅驗觸發器存在與函式體,**未逐欄展開 schema**,亦未實測其鎖(trial_ledger 之 GUC 鎖係讀 honesty_ledger_guard 函式體所得,非親驗擋掉)。(3) 68 個觸發器僅全量列出並精讀 5 個關鍵函式體(governance_proposal_immutable／honesty_ledger_guard／honesty_delete_only_guard／model_version_no_goalpost／prereg_gate_no_goalpost);其餘 fv_guard、arena 系列、src_whitelist_guard 等**未讀函式體**,A5 之 INSERT 盲區普查即為補此未讀面而設計的機械替代。(4) reports/、audits/ 之未結項僅 grep HANDOFF.md／HANDOFF-governance.md;github-workflow.yml 橫幅所引「HANDOFF.md 待裁 #22」在 HANDOFF.md 內**grep 查無**(可能已改編號或移檔),故 gap 5 之 blocked_by 以橫幅原文引述、未能獨立複現該待裁項。(5) 本輪未改動任何檔案、未 commit。  【與記憶對照】記憶「不代打人簽」條之 07-25 實犯(代打 promoted_by='hugo')之結構成因於本輪確認**仍未封**:全系統人簽機制目前一律為「script 印 SQL、hugo 親跑」之榮譽制(evolve_cycle.py:240/:360、run_raw_evolution_iteration.py:203,且以自測斷言「印出而非代打」自我證明),唯一真機械閘為 preregister_direction_gate.py:361 之 isatty fail-closed——該先例被 governance_queue.py docstring 引為依據,但未實作。

</details>

---

### 8.9 路自己（橫切基建）

*路自己(橫切基建:門登錄簿/證據帳本/作用域標籤/誠實閘/車道治理)*

**既有表（16）**：`direction_gate`（29 列(evaluated_fail 10 / approved 12 / superseded 3 / 其餘)）、`arena_admission_gate`（3 列(evaluated_pass 1=arena_adm_5305655ad1cd approved_by=hugo）、`prediction_unfreeze_gate`（2 列,皆 superseded(unfreeze_06dcb178267d sha=990ddea219ad / un）、`evolution_prereg_gate`（1 列:gate_id=V2-SUNSET, axis=program, status=approved, criter）、`knowhow_auto_admit_gate`（1 列）、`validation_evidence`（19 列,全 status=green;其中 2 列 last_verified_at IS NULL 仍記 green）、`trial_ledger`（32 列,recipe 僅 1 種,metric_name 全為 net_sharpe(distinct seed=0 ）、`evolution_evidence_run`（4 列）、`evolution_iteration_ledger / raw_evolution_iteration_ledger / local_ai_iteration_ledger`（27/25/26 欄;4 / 1 / 0 列）、`revalidation_ledger / revalidation_verdict / revalidation_baseline`（560 / 2 / (baseline 有閘) 列）、`deliberation_claim / deliberation_verdict`（deliberation_verdict 768 列;deliberation_escalation 218 列;del）、`direction_arena_candidate / knowhow_evolution_candidate / advisor_probe_candidate / promotion_queue`（11 / 0 / 9 / 310 列）、`direction_arena_verdict / direction_econ_verdict / econ_verdict_rule / factor_direction_ruling`（0 / 0 / 5 / 2 列）、`governance_proposal`（3 列(enacted 2 / rejected 1),decided_by 全為 'hugo'）…

**既有 script（18）**：`preregister_direction_gate.py`、`evaluate_direction_gate.py`、`preregister_unfreeze_gate.py`、`preregister_arena_admission_gate.py`、`evaluate_arena_admission.py`、`governance_queue.py`、`verify_validation_evidence.py`、`verifiers.py`、`migrate_honesty_guards_ddl.py`、`check_cmd_matrix.py`、`daily_green.py`、` verify_arena_watchlist.py`、`evolution_contract.py`、`evolution_ledger_ddl.py`、`tools.py`、` install_services.sh`…

**缺口與可開工下一步（13）**

| 工 | 缺什麼 | 可開工的第一步 | 需要的表／欄 |
|---|---|---|---|
| M | 無統一門登錄簿:四張 prereg 型門表(direction_gate 29 列 / arena_admission_gate 3 / prediction_unfreeze_gate 2 / evolution_prereg_gate 1)共用 12 欄同名同義骨架,卻分裂為**兩套狀態詞彙**(preregistered→approved vs draft→frozen)、**四份各自實作的 no_goalpost trigger 函式**(散居六個 DDL 住所)。跨軸『這條路上現在有幾道門、哪些已判死』無法一句 SQL 查出,advisor/prompt.py:79 只能硬查 direction_gate 一表當全系統門數 | ① 新增 src/augur/audit/gate_registry.py:提供 gate_rows()(UNION ALL 四表為統一列型:gate_id, axis_kind, axis_value, criteria, criteria_sha, lifecycle_state∈{registered,signed,passed,failed,superseded}, approved_by, approved_at, evaluated_at, result_snapshot, git_sha, source_table)+ criteria_sha(criteria) 單一計算口徑(抄 preregister_arena_ | 零 schema 變動(不動任何既有欄位/資料)。新增 1 個 SQL 函式 gate_no_goalpost() + 4 個 trigger 重指向 + 1 個唯讀 VIEW gate_registry_v(UNION ALL)。可選:CREATE VIEW 而非 librar |
| M | evolution_prereg_gate 是四門最弱閘,且其唯一一列(V2-SUNSET)**永遠不會有機械判決**:(a) prereg_gate_no_goalpost() 只在 status∈終態時全鎖,**沒有狀態轉移白名單**(draft/preregistered↔approved 可任意跳),(b) 只比 criteria_sha、**不比 criteria jsonb 本體**——改 criteria 而保留舊 sha 即穿閘(對比 direction_gate/arena/unfreeze 三函式皆 `NEW.criteria::text IS DISTINCT FROM OLD.criteria::text`  | ① 改 src/augur/audit/evolution_ledger_ddl.py:205 PREREG_NO_GOALPOST_FN:補 criteria jsonb 併查、補狀態轉移白名單(preregistered→approved／superseded;approved→evaluated_*／superseded)、補終態 result_snapshot/evaluated_at 凍結(抄 direction_gate_no_goalpost 該段)。② 同檔 PREREG_DDL 補 `ALTER TABLE evolution_prereg_gate ADD CONSTRAINT chk_epg_approved_ | 零新表。新增 1 條 CHECK constraint(chk_epg_approved_signed)+ 改 1 個 SQL 函式 + 新增 1 支 script。若 V2-SUNSET.approved_at 為 NULL,CHECK 須以 NOT VALID 先掛再補 |
| S | arena_admission_gate 與 prediction_unfreeze_gate 的判決快照**在終態仍可被改寫**。兩函式(arena_admission_no_goalpost / unfreeze_gate_no_goalpost)只鎖 criteria + 簽核欄 + 狀態轉移,沒有 direction_gate_no_goalpost 獨有的那段『終態列判決快照凍結(result_snapshot/evaluated_at/evaluation_ref/git_sha 不可改寫)』。故 `UPDATE arena_admission_gate SET result_snapshot=... WHERE sta | 合入上一項的統一 gate_no_goalpost() 即一併解決;若要單點止血:改 scripts/migrate_arena_admission_gate_ddl.py:64 附近與 scripts/migrate_unfreeze_gate_ddl.py:57 附近的函式體,各補一段 `IF OLD.status IN ('evaluated_pass','evaluated_fail') AND (NEW.result_snapshot::text IS DISTINCT FROM OLD.result_snapshot::text OR NEW.evaluated_at IS DISTINCT FROM OLD.evalu | 零 schema 變動,純改兩個 SQL 函式體(或一次併入統一函式) |
| M | **人類授權門在機械上只落地了一處**。全 repo isatty() 僅 4 個命中:preregister_direction_gate.py:361、review_knowledge_source.py:66/:92、src/augur/knowledge/curation.py:48。以下自稱人閘者皆**無機械閘**:(a) governance_queue.py --approve/--reject(判準變更之總閘)且 :74 `actor = getpass.getuser()` 把 decided_by 自動填成 OS 帳號——本機 OS user 即 hugo,故任何 AI/腳本跑 --approve 都會寫出 de | ① 新增 src/augur/core/human_gate.py:`require_tty(action: str)` —— 非 TTY 即 sys.exit(fail-closed);`human_actor(explicit: str／None)` —— 強制要求顯式傳入且**拒絕 getpass.getuser() 作為來源**(不代打人簽),另回一個 `attest_note` 記錄 tty 裝置名+時戳;附 --selftest(以 monkeypatch stdin 驗兩種分支)。② 改 governance_queue.py:74 改呼叫 human_gate.require_tty('approve') + hum | 零 schema 變動。新增 1 個 library 模組 + 1 支稽核 script,改 4 支既有 script。可選加值:governance_proposal / local_model_version 增 `signed_via text CHECK (signed_ |
| M | **作用域標籤(replay/觀察級 vs 確立級)完全不是資料**。全庫掃 column_name like '%claim%／%scope%／%level%／%tier%' 的結果中,沒有任何一欄是判決的作用域等級:evolution_evidence_run.selection_scope 是選擇偏差範圍(值如 'control_arms_v1')、raw_evolution_iteration_ledger.tier 是原始資料層級、knowledge_source.authority_tier 是知識來源權威。『觀察級/確立級』只以兩種形式存在:(a) print 字串(settle_arena_labels.py:267 | ① 新增 scripts/migrate_claim_scope_ddl.py:對五張判決/證據表(direction_gate、arena_admission_gate、evolution_prereg_gate、direction_arena_verdict、revalidation_verdict、validation_evidence)各加 `claim_scope text NOT NULL DEFAULT 'observational' CHECK (claim_scope IN ('observational','replay','established'))`,並加**升級閘 trigger** claim_scop | **需 DDL**:6 張表各加 1 欄 claim_scope + 1 條 CHECK + 1 個 promotion guard trigger 函式。既有列以 DEFAULT 'observational' 回填(對 validation_evidence 19 列、dir |
| S | 評測器之 git_sha 未綁乾淨樹:_assert_clean_tree()(git status --porcelain)**全 repo 僅存於 evaluate_direction_gate.py**。evaluate_arena_admission.py 與 preregister_unfreeze_gate.py --evaluate 皆會寫 git_sha 進門表,但可在髒樹下執行→門表記的 sha 不代表實際跑的碼(『評測分數所屬的碼版本』這條溯源斷掉) | 把 evaluate_direction_gate.py:79 的 _assert_clean_tree 與 :36 _git7 抽到 src/augur/core/repo_state.py(新模組,含 assert_clean_tree() / git_sha7() / --selftest,selftest 以 subprocess mock 驗兩分支),三支評測器改為 import 同一函式;evaluate_arena_admission.py 與 preregister_unfreeze_gate.py 的 evaluate 路徑各於進入判決前呼叫 assert_clean_tree() | 零 schema 變動。新增 1 個 library 模組,改 3 支 script |
| S | 證據帳本(validation_evidence)是最接近『一條路』骨幹的既有零件,但目前:(a) 19 列全 green 而其中 2 列 last_verified_at IS NULL——**未驗過卻記 green**;(b) 最新 last_verified_at=2026-07-15(15 天前),**無新鮮度規則**,沒有任何機制讓 green 隨時間過期成 unverified;(c) 此表**無 guard trigger**(可裸手 UPDATE 把 red 改 green、可 DELETE 整列);(d) verify_validation_evidence.py --strict 存在但**不在 daily_gr | ① 改 scripts/migrate_validation_evidence_ddl.py:補 CHECK `chk_ve_green_verified: status <> 'green' OR last_verified_at IS NOT NULL`(先跑 UPDATE 把該 2 列改 status='unverified' 再掛,或以 NOT VALID 掛後補);補 honesty_ledger_guard trigger(DELETE/TRUNCATE 拒、UPDATE 須 GUC——verify_validation_evidence.py 自身寫入前 SET LOCAL augur.honesty_write='o | 零新表。新增 1 條 CHECK + 1 組 trigger(重用既有 honesty_ledger_guard 函式)+ 1 個 CLI 參數 + daily_green STEPS 加一行 |
| M | **LANE-GOV 車道只封了一個入口,漏三個**。/tmp/augur_llm.lock 的 in-process 持鎖只在 tools/local_llm_mcp/tools.py:281。實查所有 ollama HTTP 呼叫者(10 支 py 直打 11434/api/*),其中 **0 個**有鎖的包括:scripts/eval_local_model.py(:36 自建端點,即 LANE-GOV 註記所指 T1200 敗因的當事評測臂)、src/augur/advisor/ollama.py(:88/:125/:176,serve_advisor_openai / serve_chat_ui / deliberatio | ① 新增 src/augur/core/llm_lane.py:`LOCK_PATH`(單一住所,可由 AUGUR_LLM_LOCK env 覆蓋)+ `lane(timeout_s=None)` context manager(阻塞版,附等鎖時長回傳)+ `try_lane()`(非阻塞版,回 bool)+ `lane_stats()`(記 skip/wait 次數落 log)+ --selftest(以兩個 subprocess 驗互斥)。② 改 src/augur/advisor/ollama.py 的三處 urlopen 全部包 lane()——一改即覆蓋 advisor/chat/deliberation 三個服務側消費者 | 零 schema 變動。新增 1 個 library 模組 + 1 支稽核 script,改 4 支消費者。可選:新增表 llm_lane_log(ts, holder, wait_ms, skipped bool) 讓 skip 率可查(install_services.sh: |
| L | 無統一候選表、候選與門之間**無機械連結**。四個候選登錄簿(direction_arena_candidate 11 列 / knowhow_evolution_candidate 0 / advisor_probe_candidate 9 / promotion_queue 310)四套狀態詞彙(active／stopped／retired ÷ candidate_for_evolution／governance_pending／approved_for_loop／rejected_for_loop／superseded ÷ pending／approved_eval／approved_gold／rejected ÷ pendi | ① 新增 scripts/migrate_candidate_gate_link_ddl.py:對四表各加 `gate_id text`(可空;不加 FK 因跨四張門表,改在 view 層 join)+ `lane text CHECK (lane IN ('arena','knowhow','probe','feature'))`;並 backfill direction_arena_candidate.gate_id——現有 dgate_arena_* / dgate_a3_* / dgate_a4_* / dgate_replay_* 之 gate_id 命名已含 model 線索,可由 register_arena_cand | **需 DDL**:四表各加 2 欄(gate_id, lane)。新增 1 個 library 模組 + 1 個 VIEW。11 列 backfill 須人核對映(不可猜) |
| M | 無統一 verdict 寫入器。七個判決落點各自被不同 script 直接 UPDATE/INSERT:direction_gate.result_snapshot(evaluate_direction_gate.py:205)、arena_admission_gate.result_snapshot(evaluate_arena_admission.py)、evolution_prereg_gate.result_snapshot(無人寫)、direction_arena_verdict(arena_scoreboard.py:170)、direction_econ_verdict(未查到寫入者)、revalidation_ver | ① 新增 src/augur/audit/verdict_writer.py:`write_verdict(kind, key, state, metric_snapshot, threshold_source, claim_scope, gate_id, cur)` 單一入口——內含四道共用前置:(a) threshold_source 非空且指向 frozen 政策列或 gate criteria_sha,(b) claim_scope 非 'established' 除非過升級閘,(c) 冪等鍵檢查(同 key+同 as_of 不覆寫,回既有列),(d) 寫入前後計數落 log;+ --selftest(以 sqlite/mo | 零 schema 變動(claim_scope 欄若採第 5 項則相依)。新增 1 個 library 模組 + 1 支稽核 script,改 3 支寫入端 |
| M | 三支近同構迭代帳本(evolution / raw_evolution / local_ai_iteration_ledger,21 欄共用骨架)只掛 honesty_delete_only_guard(BEFORE DELETE / TRUNCATE),**完全沒有 UPDATE 閘**——與 trial_ledger 的 honesty_ledger_guard(UPDATE 須 SET LOCAL augur.honesty_write='on')不一致。這三張表的 gain / gain_basis / gain_evidence / stop_reason 正是『這一圈有沒有進步』的判決欄,現況可裸手 UPDATE 把 g | 改 scripts/migrate_honesty_guards_ddl.py:在既有 TABLES(trial_ledger, revalidation_baseline)與 PME_TABLES 之外新增第三組 `VERDICT_TABLES`,對 evolution_iteration_ledger / raw_evolution_iteration_ledger / local_ai_iteration_ledger / evolution_evidence_run / revalidation_ledger / attestation_result / knowhow_governance_ledger / validat | 零 schema 變動,純加 trigger(重用既有 honesty_ledger_guard 函式)。改 1 支 migrate script |
| S | 34 支 verify_* script 中**沒有一支稽核門登錄簿或帳本本身的完整性**。缺的機械檢查至少七項:四門表 criteria_sha 覆算是否相符(evaluate_direction_gate.py 完全沒做 sha 覆算,而 unfreeze/arena 兩支有)、終態列是否簽核齊全、evolution_prereg_gate 是否有 approved 而無簽核、arena_admission_gate 繼承 sha 990ddea219ad 是否仍成立、三帳本 gate_ref 是否指向存在的 gate_id、candidate 是否有 gate_eligible=true 卻無對應門、validation_ev | 新增 scripts/verify_gate_registry.py(唯讀、零外部依賴、可入 daily_green.py STEPS 與 pre-commit):讀 gate_registry.gate_rows(),逐項機械斷言並以表格印出 PASS/FAIL 逐列——A1 四門表全列 criteria_sha == sha256(criteria) 覆算(用 preregister_arena_admission_gate.py:47 同口徑);A2 lifecycle_state∈{signed,passed,failed} 之列 approved_by/approved_at 皆非空;A3 lifecycle_state∈ | 零 schema 變動,零新表。新增 1 支唯讀 script(依賴第 1 項的 gate_registry library;若第 1 項未落地,可先以四段 UNION ALL 內嵌 SQL 版本上線) |
| S | trial_ledger 的 UNIQUE 鍵八欄(model,horizon,top_frac,weight,feats_hash,cost,sample_since,recipe)**不含 metric_name**,配合 revalidate.py:286 明載的 ON CONFLICT DO UPDATE 語義 → 同一配方無法同時存兩種 metric(存第二種會覆寫第一種)。live 現況尚未咬到(32 列 metric_name 全為 net_sharpe、recipe 僅 1 種、seed 全空),但一旦要把 IC 與 net_sharpe 併存於同一 DSR 分母,或要多 seed 落列(CLAUDE #11 要求  | 新增 scripts/migrate_trial_ledger_metric_ddl.py:`DROP INDEX trial_ledger_uq; CREATE UNIQUE INDEX trial_ledger_uq ON trial_ledger(model,horizon,top_frac,weight,feats_hash,cost,sample_since,recipe,metric_name,coalesce(seed,-1))`——把 metric_name 與 seed 併入鍵,同時保留『不含 as_of』以維持 revalidate.py:286 的『同 config 重跑不增 N』不變式;並改 scripts/ | **需 DDL**:重建 1 個 UNIQUE INDEX(含 seed 的 coalesce 表達式索引)。零欄位新增。改 1 支既有 script 的 ON CONFLICT 子句 |

**機器可判驗收（可預先凍結）**
- A1 門登錄簿收斂:`SELECT count(DISTINCT proname) FROM pg_proc WHERE proname LIKE '%no_goalpost%' AND pronamespace='public'::regnamespace` 現值 5(direction/arena/prereg/unfreeze/model_version),統一後四門表之 trigger 必全部指向同一 tgfoid;斷言 `SELECT count(DISTINCT t.tgfoid) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid WHERE c.relname I
- A2 criteria_sha 全覆算相符:scripts/verify_gate_registry.py --run 對四門表 35 列(29+3+2+1)逐列覆算 sha256(json.dumps(criteria,sort_keys=True,ensure_ascii=False,separators=(',',':')))[:16],不符列數必 = 0;exit 0。(註:preregister_direction_gate.py:167 已記錄過『手刻配方 bug(12碼/無 separators)』先例,故此斷言必須印出每列的 expected/actual 而非只回總數)
- A3 終態簽核齊全:`SELECT count(*) FROM gate_registry_v WHERE lifecycle_state IN ('signed','passed','failed') AND (approved_by IS NULL OR approved_at IS NULL)` = 0;且 `... WHERE lifecycle_state IN ('passed','failed') AND (evaluated_at IS NULL OR result_snapshot IS NULL)` = 0
- A4 終態快照不可改寫(四門表對稱):對每張門表各跑一次 `BEGIN; UPDATE <tbl> SET result_snapshot='{"tamper":1}' WHERE status IN ('evaluated_pass','evaluated_fail') LIMIT 1; ROLLBACK;` —— 四表皆須 RAISE EXCEPTION(現況只有 direction_gate 會);任一表未擋即 FAIL
- A5 evolution_prereg_gate 補齊:(a) `SELECT count(*) FROM pg_constraint WHERE conrelid='evolution_prereg_gate'::regclass AND contype='c'` 由 2 升為 ≥3(新增 chk_epg_approved_signed);(b) 負向測 `BEGIN; UPDATE evolution_prereg_gate SET criteria=criteria／／'{"x":1}'::jsonb WHERE gate_id='V2-SUNSET'; ROLLBACK;` 須被擋(現況會通過,因 guard 只比 crit
- A6 人閘覆蓋率 100%:scripts/verify_human_gate_coverage.py exit 0 —— 全 repo 凡有寫入 approved_by / decided_by / promoted_by 之 SQL 字面的函式,其呼叫鏈上必出現 augur.core.human_gate.require_tty;現況預期 FAIL 清單至少含 governance_queue.py:77、preregister_unfreeze_gate.py:125、preregister_arena_admission_gate.py:157(三處);修完必為空清單。附加:`grep -c getpass scripts/
- A7 作用域標籤入庫:六張表皆有 claim_scope 欄且 `SELECT count(*) FROM <每表> WHERE claim_scope IS NULL` = 0;負向測 `BEGIN; INSERT INTO direction_arena_verdict(...,claim_scope) VALUES (...,'established'); ROLLBACK;` 在 cluster<60 時須被 promotion guard 擋下
- A8 證據帳本新鮮且無假綠:`SELECT count(*) FROM validation_evidence WHERE status='green' AND (last_verified_at IS NULL OR last_verified_at < now()-interval '7 days')` = 0(現況此查回 19,即全數超齡/未驗);且 scripts/verify_validation_evidence.py --run --strict exit 0;且 `SELECT count(*) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid WHERE c.
- A9 車道零漏口:scripts/verify_llm_lane_coverage.py exit 0 —— 現況預期 FAIL 清單含 scripts/eval_local_model.py、src/augur/advisor/ollama.py、tools/project_memory_mcp/embed.py、scripts/serve_admin_console.py(四支);修完清單為空。且 `grep -rn "/tmp/augur_llm.lock" --include=*.py src/ scripts/ tools/ ／ grep -v llm_lane.py ／ wc -l` = 0(鎖路徑單一住所)
- A10 車道不餓死:llm_lane_log(若採納)中連續 3 日 skipped 比率 <100%;或退而以既有 log 機械判:`journalctl --user -u augur-deliberation --since '3 days ago' ／ grep -c 'skip.*busy'` 不得等於該期間總觸發次數(install_services.sh:249 之中止條件機械化)
- A11 判決通道非空:scripts/verify_verdict_pipeline.py exit 0 —— 斷言 direction_arena_policy 兩列 frozen=true 且 direction_arena_prediction 已結算 4,128 列的前提下,direction_arena_verdict 列數 ≥1(現況 0 → 必 FAIL,逼出『通道從未被呼叫』或『確實未觸發』的誠實答案)
- A12 帳本 UPDATE 閘齊備:`SELECT count(*) FROM (VALUES ('evolution_iteration_ledger'),('raw_evolution_iteration_ledger'),('local_ai_iteration_ledger'),('evolution_evidence_run'),('revalidation_ledger'),('attestation_result'),('knowhow_governance_ledger'),('validation_evidence'),('knowhow_auto_admit_gate')) v(t) WHERE NOT EXIS
- A13 trial_ledger 鍵不吞列:改鍵前後 `SELECT count(*) FROM trial_ledger` 皆為 32;且改鍵後可成功插入同 recipe 不同 metric_name 兩列(`count(*) FROM trial_ledger` 變 33 而非仍 32)
- A14 矩陣不退化:python scripts/check_cmd_matrix.py exit 0 且『缺漏 0 支』——本主題新增之全部 library 模組(gate_registry / human_gate / llm_lane / verdict_writer / candidate_registry / repo_state)與 script(verify_gate_registry / verify_human_gate_coverage / verify_llm_lane_coverage / verify_verdict_pipeline / evaluate_evolution_prereg_gate)於**
- A15 一句 SQL 答得出『一條路』:VIEW one_path_v 落地後,`SELECT lane, lifecycle_state, claim_scope, count(*) FROM one_path_v GROUP BY 1,2,3` 必回非空結果且各 candidate 之 lifecycle_state 與其 gate 之 lifecycle_state 不矛盾(gate passed 而 candidate retired、或 candidate active 而 gate failed 的組合須為 0 列或被列為待人裁清單)

<details><summary>本線誠實界限</summary>

誠實界限如下。  【live DB 已親驗】本次全部表存在性/欄位/CHECK/trigger/函式體/索引/列數皆為 live `augur` 庫實查(psycopg2 經 /home/hugo/project/augur/venv,查詢輔助檔 /tmp/claude-1000/-home-hugo-project-augur--claude-worktrees-zai-ma-9f972d/223fa752-0df8-474d-aa39-9ddbcbfef034/scratchpad/q.py)。psql CLI 直連失敗(role "hugo" does not exist / augur 密碼認證失敗),改走 augur.core.db.connect() 讀 .env,故所有 db 級事實均屬 live 而非 DDL 推測。四個 no_goalpost 函式體與 honesty guard 兩函式體皆以 pg_get_functiondef 取全文逐字比對,詞彙分裂與 result_snapshot 凍結缺漏兩項為函式體實證,非推論。  【只讀 code 未跑】以下為 grep/讀檔級事實,未實跑驗證:(a) governance_queue.py 無 isatty —— 我以 `grep -c isatty` 得 0 並讀了 :74 getpass.getuser() 與 :77 UPDATE,但**未實跑 --approve 驗證非 TTY 下真能寫入**(該操作會污染人簽帳本,依 CLAUDE #6/不代打人簽鐵律不試);(b) evaluate_direction_gate.py 無 criteria_sha 覆算 —— 依 `grep -n "criteria_sha\／_sha(\／sha256"` 於該檔零命中判定;(c) 「evolution_prereg_gate criteria 可改而 sha 不變即穿閘」為讀函式體推得的負向路徑,**未實跑 UPDATE 驗證**(同理不試,留作 A5(b) 之預先凍結驗收項)。  【查無】① 查無任何統一 gate registry / 統一 candidate 表 / 統一 verdict 寫入器 —— 唯一近似先例是 src/augur/deliberation/verifiers.py:152 verify_claim(僅服務 deliberation 一軸)。② 查無 verify_gate_registry.py 或任何跨門表/跨帳本完整性稽核 script(34 支 verify_* 全數點名檢查後確認)。③ 查無 evolution_prereg_gate 的評測器(僅三支 script 碰此表,其中 report_triple_evolution_week.py 自我斷言唯讀)。④ 查無 direction_econ_verdict 的寫入者(grep 僅得 DDL 與 0 列)。⑤ 查無任何欄位承載「觀察級/確立級」語意(全庫 %claim%/%scope%/%level%/%tier% 欄位逐一檢視後確認,最接近者 evolution_evidence_run.selection_scope 語意為選擇偏差範圍而非宣稱等級)。⑥ 查無 llm 車道之 skip 率留痕表。  【未查/相依待補】(a) V2-SUNSET 之 approved_at 實值未查(影響第 2 項 CHECK 能否直接掛,已於該項 blocked_by 標明);(b) direction_arena_verdict 0 列究竟是「arena_scoreboard futility 通道從未被呼叫」或「呼叫了但 cluster<60 未觸發」未鑑識(已於第 10 項 blocked_by 標明,並設計 A11 逼出答案);(c) direction_arena_candidate 11 列與 12 個 dgate_arena_*/a3/a4/replay 門的對映關係未逐列核對,故第 9 項 backfill 明列須人核不得由命名推斷。  【口徑校正一則】src/augur/deliberation/verifiers.py 檔頭 docstring 兩處寫「四真 oracle」,但 :34 ORACLES 為五元(information_schema, import_isolation, file_grep, db_query, pytest)且 :208 selftest 斷言 `len(ORACLES) == 5`。code 為準=5,docstring 落後。屬純機械修正(CLAUDE #20 判準:不另立計畫),不列為 gap。  【本次未越界】全程唯讀:無任何 DDL、無 INSERT/UPDATE/DELETE、無 FinMind/FRED 呼叫、無服務重啟。查詢輔助檔僅寫入 scratchpad。cwd 為 worktree /home/hugo/project/augur/.claude/worktrees/zai-ma-9f972d,但所有讀取與行號皆取自真實工作目錄 /home/hugo/project/augur(CLAUDE #13);兩處已比對確認 LANE-GOV(2026-07-30 註記)只存在於真實目錄之 tools/local_llm_mcp/tools.py,worktree 鏡像未含,故行號以真實目錄為準。

</details>

---

### 8.10 第二域可行性

*第二域可行性(證明「法屬世界」非口號之最小落點)*

**既有表（15）**：`(查無) world_concept_registry / observation_channel / domain_profile`（0 列(表不存在)）、`knowledge_domain`（42 列;其中 is_authz_boundary=true 27 個）、`knowledge_item`（47 域;domain 無 FK 至 knowledge_domain(僅 source_key/taxonomy_id）、`knowledge_source`（3,573 列;adapter 15 種(generic_json 3547/dbpedia_sparql 26/man）、`knowledge_domain_map`（25 列）、`principle_domain_map`（8 列）、`group_domain_grant`（31 列）、`dataset_catalog`（97 列;source: finmind 94(excluded 11)/infra 2/fred 1;category）、`column_catalog`（769 列 / 97 dataset）、`fred_series`（344,830 列 / 31 series(BAMLC0A0CM, CPIAUCSL, DGS10, DEXTAUS, ）、`JapanStockPrice / UKStockPrice / EuropeStockPrice`（JP 16,878,584 列 / UK 23,665,534 列 / EU 4,183,873 列）、`USStockPrice`（35,052,889 列;stale 42 天）、`JapanStockInfo / USStockInfo / UKStockInfo / EuropeStockInfo`（JP 3,640 / US 17,906 / UK 24,339 / EU 1,306 列）、`mc_simulation_run`（method='episode_analog_*' 共 6 列;全庫 method 15 種）…

**既有 script（10）**：`simulate_portfolio_risk.py`、`audit_domain_hygiene.py`、`build_catalog.py`、`acquire_knowledge.py、promote_knowledge.py、harvest_knowledge.py`、`verifiers.py`、`compliance_lint.py`、`check_treaty_refs.py`、`check_cmd_matrix.py`、`migrate_rbac_ddl.py`、`manage_rbac_user.py`

**缺口與可開工下一步（8）**

| 工 | 缺什麼 | 可開工的第一步 | 需要的表／欄 |
|---|---|---|---|
| M | **World Concept Registry 零實作,且自 2026-07-30 起已成硬阻塞**。WM.36 命『必須維護為一級結構』,七欄俱全方為登錄完成;而今日升版之 `docs/原則精華_v1.11.0.md` #1 WHAT 已改寫為『任一特徵值必須是經**登錄觀測通道**之真實值』並明文『**新增通道須經 World Concept Registry 登錄(§WM.35–36)後,其值方為本條所稱之真實值**』。表不存在 ⇒ 任何新通道(含第二域全部通道)之值在字面上**永遠無法成為 #1 意義下的真實值**。這不是待辦,是登錄第二域的先決條件 | 新增 `scripts/migrate_world_registry_ddl.py`(仿 migrate_rbac_ddl.py 型樣,`--migrate` / `--dry-run` / `--selftest`),建三表:`world_domain`(域登錄)、`world_concept`(概念,七欄之 1/2/4/7)、`world_concept_channel`(通道映射,七欄之 3/5/6,粒度至欄位級,FK→world_concept 且 FK→(dataset,column_name) 對 column_catalog)。再新增 `scripts/register_world_concept.py`(資料驅動註冊 | 新表 3 張。`world_domain`(domain_key PK, profile_annex, spec_version, status ∈ {draft,enacted,superseded}, enacted_by, enacted_at, note);`world_ |
| M | **『第二域』之範圍認定陷阱:FRED 與國際股票都不算第二域**。Annex A A.0 已宣告涵蓋『台灣上市櫃證券市場**及其預測所需之全球金融與總體經濟觀測域**』,且 A.9(ForeignSecurity)明文『外國市場證券(含外國指數)為一級實體,屬日級情境輸入之觀測對象』。故 fred_series(344,830 列)、JapanStockPrice(16.9M)、UKStockPrice(23.7M)全部**已在第一域範圍內**,拿它們宣稱『第二域已存在』是自我欺騙。真正的第二域必須是主體不在證券市場之域 | 以 `software_engineering` 或 `quant_finance` 為 pilot 域(二者皆 knowledge_item 有資料、knowledge_domain 字典無 ⇒ 同時修掉孤兒;且憲章 P3.W2 自身即以 Factory／Machine／Material 為 Physical Entity 例示,非金融域為母法原生預期)。在 `specs/WORLD-MODEL-SPECIFICATION.md` 末新增 **Annex G [N] — 第二域 Domain Profile**,嚴格照 WM.50 五部編排(①存在宣告 ②候選同一性判準槽[全標 [I]] ③時間語意宣告 ④通道登錄與世界映射[排除 | 零 schema 變動(規格側);DB 側僅 `world_domain` INSERT 一列 + `knowledge_domain` INSERT 一列(補孤兒)。規格升版 AUGUR-WM v1.0 → v1.1(WM.52:新增 Profile ＝ minor,**正文  |
| M | **WM.50 五部結構 / WM.51 越界禁止 / ONT.50 T-Map 覆蓋 三者皆無機器閘**。grep -rln 'T-Map／ONT.50／WM.50' scripts/ tools/ src/ → 零命中;compliance_lint.py 只查 WM.39–45 合規聲明。⇒ 新 Annex 寫錯(混入分類體系、載入 Registry 具體條目、漏一部、多出第六部)會安靜通過。這正是記憶中『防呆機制自己靜默失效』的第五型 | 新增 `scripts/check_domain_profile.py`(純文字、零 DB、仿 check_treaty_refs.py 骨架,含 --json/--selftest/exit 1),機械斷言四事:(a) 每一 Domain Profile Annex 恰含 WM.50 五部標頭且『待決事項』外無第六部;(b) ②部每一條含 [I] 標記(WM.21(e) 效力封印);(c) ④部排除清單每列附排除理由類型且落在 A.42 閉集(或該 Profile 自訂閉集);(d) ONT.13/ONT.50 封閉集與 Annex T-Map 列數雙向一致。掛入 pre-commit / CI | 零新表。純 repo 檔案解析。須順帶處理 ONT 側:ONT.13 可判定判準把封閉集**寫死**為『{§A.1–§A.30, §A.57, §A.58}(共 32 條)』,Annex T-Map 實測恰 32 列——第二域若含①部存在宣告,ONT.50 要求『涵蓋全部存在宣告 |
| S | **已在生產違反 WM.36 消費規則:以供應商表名字面繫結**。WM.36 明文『必須以世界概念為鍵、經 Registry 解析至權威表徵,**不得**以來源位置字面(供應商表名、欄名、series 識別碼)直接繫結』。實證:simulate_portfolio_risk.py 之 ANALOG_EPISODES 直接寫 ('USStockPrice', …)、('UKStockPrice', …),且 mc_simulation_run.summary->>'market_table' 六列全記字面表名。並非新開發缺口,是既存待補正項(享 §8.3 過渡規則 (b) 補正期,補正期到期日之翌日起無條件適用) | WCR 三表落地後,改 `scripts/simulate_portfolio_risk.py`:ANALOG_EPISODES 之值由 (表名, 起, 迄) 改為 (concept_key, 起, 迄),新增 `_resolve_channel(cur, concept_key)` 經 world_concept_channel 解析出 (dataset, 收盤欄) 再組 SQL;summary 改寫 concept_key 並保留 market_table 為解析結果之揭露欄(非繫結鍵)。**窗值(六個 episode 日期)不得動**(commit 即凍結紀律);既有 6 列舊 run 不回頭改寫(#12 不 hand-pat | 零新表(用上條 WCR 三表)。ANALOG_EPISODES 六列同時是 WCR 第一批非台股通道 seed。附帶:海外表收盤欄為大寫 "Close"、台股為小寫 close(code 內已註 2026-07-27 實撞),此差異正該由 Registry 欄位級映射吸收,不再散 |
| S | **A.35 第三項『跨市場軸對映宣告』無任何存放位置,且保守解釋已然生效**。A.35 命:凡通道時間鍵為外國市場交易日者,必須宣告其對映至本域交易日軸之規則(含『外國 t-1 收盤於本域 t 日之可知地位』),未宣告者『依保守解釋**不可用於本域 as-of 推理**』並『**禁止下層以「同日即對齊」隱含假設消費**』。RULING-2026-030 §五(f)/AL-2026-033 已將其納為 WM.36 第 5 欄之一部分。實查:無此欄、無此表、無任何檔案承載之——即所有國際股/FRED 通道目前一律落入『不可用於 as-of 推理』 | 上條 `world_concept_channel.cross_market_axis_mapping` 欄即其住所。新增 `scripts/audit_world_concept_registry.py --asof-eligibility`:對每一 timestamp_semantics 為外國市場交易日之通道,若 cross_market_axis_mapping IS NULL 則列為 asof_ineligible,並反向掃 code(file_grep oracle)確認無任何 as-of 路徑消費之。第二域 Profile ③部須逐通道填此宣告 | 零新表(欄位在 world_concept_channel)。須先釐清一個事實問題:M1 analog 是否構成『as-of 推理』——它重放固定歷史窗、以 β=1 承受該市場路徑,並未把外國 t-1 對齊本域 t;但 us2008 明文為『校準錨:對照台股 2008 重放』,對 |
| S | **5 個孤兒域,FK 從未安裝**。knowledge_item.domain 有值但 knowledge_domain 字典無:software_engineering 1,685 / quant_finance 1,191 / local 323 / erp_semantics 14 / solar_rd 6(共 3,219 列);knowledge_source 側另有 philosophy 4 / economics 1 / erp_semantics 1 / management 1 / solar_rd 1。audit_domain_hygiene.py 自陳『FK VALIDATE 前須為 0』,但實查 knowle | (1) 跑 `venv/bin/python scripts/audit_domain_hygiene.py --seed` 把 5 個孤兒 fail-closed 註冊(is_authz_boundary=FALSE,只註冊不賦權);(2) 新增 `scripts/migrate_domain_fk_ddl.py` 以兩階段 FK(ADD CONSTRAINT … NOT VALID → VALIDATE CONSTRAINT)裝上 knowledge_item.domain → knowledge_domain(domain),**須排在任何 pg_dump 完成後**(#30 dump 期間禁 DDL 鐵律:pg_dump 持 | 零新表;knowledge_item 增一個 FK 約束。是否升為授權邊界(is_authz_boundary=TRUE)屬決策層,走 manage_rbac_user.py --add-domain --authz-boundary,不自動 |
| L | **市場/預測/arena 全鏈無域軸**。全庫掃 column_name in ('domain','domain_key','market','market_code','world_domain'):15 個命中全落在 knowledge_/advisor_/philosophy_/principle_/group_ 前綴(唯一市場側命中 TaiwanStockLoanCollateralBalance.market 語意為交易所別)。feature_values、panel、model_registry、direction_arena_*、arena_admission_gate、arena_replay_run 皆無域欄  | **pilot 刻意不碰預測管線**(憲章知識層不變式:多域知識素養層零量化價值、不進預測管線;domain 欄隔離因子鏈純度)。因此 pilot 之驗收只到『域已登錄＋通道已登錄＋既有消費端改以概念鍵解析』,**不含第二域出預測**。若日後要出,再另立計畫評估 arena/panel 加 domain_key(預設 'tw-equity' 回填)之遷移成本——現在寫進 pilot 會把 M 級變成 L 級且觸及 as-of 地基 | pilot 階段:零 schema 變動。日後階段:direction_arena_* 與 panel 系列加 domain_key NOT NULL DEFAULT 'tw-equity'——**不在本 pilot 範圍** |
| S | **第二域若選市場型,survivorship 無法滿足且已有誠實揭露先例**。JapanStockInfo/USStockInfo 等 roster 表無上市日/下市日欄(實查 JapanStockInfo 僅 date/stock_id/Exchange/Sector/stock_name),故 A.2 point-in-time 成員資格/survivorship 禁令在非台股域無通道可滿足。現況已誠實記錄:ANALOG_NOTES 第三句『來源是否含已下市股未證實:倖存者偏誤方向未知,數字僅類比參考』,且 6 個窗中 3 個以 kind='analog_refused' 拒答(n_stocks_min 1/54/28 < M | 若 hugo 選市場型第二域(如日本),則 Annex G『待決事項』節須逐字列入『成員資格 point-in-time 通道缺席 ⇒ survivorship 方向未知』並標明『**禁止下層以隱含假設消費**』;同時 `world_concept_channel` 為該域 Roster 概念登錄 unmapped=TRUE(WM.35 顯式合法過渡態),不得偽稱已登錄。驗收沿用既有 refused 型樣:覆蓋不足即 kind='*_refused' 落帳,不硬出數字 | 零新表。unmapped 旗標已在上述 world_concept_channel DDL 內 |

**機器可判驗收（可預先凍結）**
- 【oracle: information_schema】`world_domain`、`world_concept`、`world_concept_channel` 三表存在;且 `world_concept.kind` 之 CHECK 約束字面等於 WM.36 第 2 欄閉集 {entity,event,state,relation,quantity}(五值,不多不少);`world_concept.provenance`、`world_concept_channel.provenance`、`timestamp_semantics`、`knowability_rule` 四欄皆 NOT NULL。任一欄可空即 FAIL(WM.3
- 【oracle: db_query】WM.14/WM.37 權威表徵恰一:`SELECT count(*) FROM (SELECT concept_key FROM world_concept_channel GROUP BY 1 HAVING sum(is_authoritative::int) <> 1) x` = 0。解析至零個或多個皆 FAIL(WM.14『恰解析至一個』)
- 【oracle: db_query】第二域已登錄且非空:`SELECT count(*) FROM world_domain WHERE domain_key='<pilot>' AND status='enacted'` = 1,且 `SELECT count(*) FROM world_concept WHERE domain_key='<pilot>'` ≥ 1,且該域每一 concept 至少一列 world_concept_channel(unmapped=TRUE 亦計,WM.35 顯式過渡態合法)
- 【oracle: db_query】人簽不可代打:`SELECT enacted_by FROM world_domain WHERE domain_key='<pilot>'` 之值須為 hugo 親跑寫入;驗收時同時斷言 `enacted_at` 非 AI session 時窗內由 script 自動填(以 governance_proposal 三表三鎖之人簽紀錄交叉對帳)
- 【oracle: db_query】孤兒域歸零:`SELECT count(*) FROM knowledge_item ki LEFT JOIN knowledge_domain kd ON kd.domain=ki.domain WHERE kd.domain IS NULL` = 0(當前基線 = 5 個域 / 3,219 列);且 knowledge_source 側同查 = 0(當前基線 = 5 個域 / 8 列)
- 【oracle: db_query】FK 真的裝上且已驗證:`SELECT convalidated FROM pg_constraint WHERE conrelid='knowledge_item'::regclass AND contype='f' AND pg_get_constraintdef(oid) LIKE '%knowledge_domain%'` 回 't'。NOT VALID 停在半途即 FAIL
- 【oracle: db_query】as-of 資格誠實標示:凡 `world_concept_channel.timestamp_semantics` 標為外國市場交易日且 `cross_market_axis_mapping IS NULL` 之通道,必於稽核輸出列為 asof_ineligible;且 `SELECT count(*) FROM world_concept_channel WHERE timestamp_semantics ~ '外國／foreign' AND cross_market_axis_mapping IS NULL AND is_authoritative` = 0(A.35 保守解釋:未宣告者不可
- 【oracle: file_grep】WM.52 正文零觸動:`git diff <base>..HEAD -- specs/WORLD-MODEL-SPECIFICATION.md` 之變更行**不含**任何 WM.1–WM.53 條文行(僅得新增 Annex G 區塊與目錄列)。正文任一行被改即 FAIL
- 【oracle: file_grep】WM.50 五部結構:Annex G 區塊內恰含五個部標頭(①實體/事件/狀態存在宣告、②候選同一性判準記載槽、③時間語意宣告、④通道登錄與世界映射、⑤領域評價性謂詞判準與世界觀定位宣告),『待決事項』節之外無第六部;且②部每一條含 `[I]` 標記(WM.21(e) 效力封印)
- 【oracle: file_grep】WM.51 越界禁止:Annex G 內不得出現具體 Registry 條目(concept_key 字面)、不得出現欄位/DDL/流程設計、不得內嵌營運日期(③部『不得內嵌營運日期』);全部產品名/供應商名/資料集名須標 [I]
- 【oracle: file_grep】WM.36 消費規則補正:`grep -nE "'(USStockPrice／UKStockPrice／JapanStockPrice／EuropeStockPrice)'" scripts/simulate_portfolio_risk.py` 於 ANALOG_EPISODES 定義區塊回零命中(改為 concept_key);表名僅得出現於 Registry 解析結果之揭露欄
- 【oracle: db_query】ANALOG 窗值凍結未被回改:改碼後重跑之 `episode_analog_us2008` 新 run 之 summary->>'span' 與既存舊 run 逐字相同,且 maxdd 仍為 -0.45565(±0)、n_stocks_min 仍 3009;數字漂移即 FAIL(證明只換繫結方式、未動語意)
- 【oracle: db_query】拒答閘仍然咬人:重跑 `--analog all` 後 `SELECT count(*) FROM mc_simulation_run WHERE method LIKE 'episode_analog%' AND summary->>'kind'='analog_refused'` ≥ 3(us1929/us1973/uk1973 之 n_stocks_min 1/54/28 < 100 必須繼續拒答;變成出數即 FAIL＝閘被繞過)
- 【oracle: pytest / db_query】ONT.50 雙向覆蓋:Annex T-Map 列數 == ONT.13 封閉集基數(當前實測皆 32);若 Annex G 含①部存在宣告,則 T-Map 須同步擴充至 32 + n 且每列雙向可解析,未對映且未列 A-OPEN 即 FAIL
- 【oracle: pytest】新增三支 script(migrate_world_registry_ddl / register_world_concept / audit_world_concept_registry)＋一支 lint(check_domain_profile)各具 `--selftest` 且純紅綠通過(免 DB 免 API 零 usage);`python3 scripts/check_cmd_matrix.py` exit 0(#18/#29d、RULING-2026-026:缺矩陣者不得宣稱已個別驗證)
- 【oracle: db_query】零放量自證:pilot 全程 `pipeline_execution_log` 無新增 FinMind/FRED 抓取列(第二域 pilot 之硬性前提＝不需新 API 額度);若有即 FAIL

<details><summary>本線誠實界限</summary>

【取證方式】DB 為 **live 實查**:以 /home/hugo/project/augur/.env 之 DB_USER/DB_PASSWORD 連 augur 庫(current_user=augur,294 張 public 表)跑唯讀 psql -tAc。規格/報告為讀檔(doc)。code 為 grep + 讀 docstring。  【查無(誠實列出)】① `world_concept_registry` / `observation_channel` / `domain_profile` 三者在 DB(294 表全掃)、在 63 支 migrate_*.py、在 scripts/ src/ tools/ 全域 grep 皆**零命中**——WCR 目前純屬規格文字(WM.36)＋Annex F 六條 [I] 啟動條目(地位聲明自陳『採認狀態＝待 Steward 附卷裁定』),無任何機器載體。② 無任何 script 提及 T-Map / ONT.50 / WM.50(grep 零命中)⇒ Domain Profile 結構無機器閘。③ Steward 就 §8.3 過渡規則 (b) 補正期之**具體到期日**未查到(RULING-2026-030 等檔內未見日期);故『字面繫結補正期何時屆滿』我無法斷言。④ 未找到任何既有『第二域』計畫書或未結項(reports/ 內 grep 第二域/Domain Profile 僅回 augur_treaty_core_alignment_plan_20260730.md 之域中立原則陳述,無施工計畫)。  【只讀 DDL/規格未驗 live 者】① Annex A/F、WM.35–37、WM.49–52、ONT.13/ONT.50 全為讀規格原文,非 live 驗證(規格本身即 SSOT,此處無 live 可驗)。② JP/UK/EU 三表『仍每日增量同步中』係由 max(date)=2026-07-28 ＋ sync.py:56 daily_datasets() 動態列舉推得,**未直接查 crontab/systemd 確認排程項**(記憶亦載 crontab 為機器本地、不隨 git)。③ `USStockPrice` max(date)=2026-06-18 係以 `WHERE date > '2024-01-01'` 有界窗探測所得;裸 `max(date)` 因 PK=(stock_id,date) 需全掃、兩次逾 2 分鐘 timeout,故該值僅保證為 2024 之後之最大日(對 stale 判定已足)。④ 未逐張讀完 63 支 migrate_*.py,採全域 grep 關鍵字替代。  【與任務前提的一處實質修正】提示語推測『既有非台股資料(FRED 總經/知識庫多域)』可作第二域證據,但實查 Annex A A.0 已宣告第一域涵蓋『台灣上市櫃證券市場**及其預測所需之全球金融與總體經濟觀測域**』,且 A.9(ForeignSecurity)明文將外國市場證券(含外國指數)declare 為第一域內之一級實體(日級情境輸入)。⇒ FRED(344,830 列)與 JapanStockPrice(16.9M)/UKStockPrice(23.7M)/EuropeStockPrice(4.2M)/USStockPrice(35.1M)**全部在第一域範圍內**,不構成第二域。真正的第二域須主體不在證券市場之域(知識層 47 域中的非金融域,如 software_engineering / quant_finance / erp_tiptop),或另立 Annex 之自反域(WM.26／A.19／A.20,但 A.19/A.20 亦已寫在 Annex A 內)。此判斷來自規格原文,非我的偏好,但『pilot 域選哪一個』屬決策層,須 hugo 拍板。  【最有力的既有落點(供計畫書取用)】非台股市場資料**已有一條在生產運行、且誠實度良好的消費路徑**:scripts/simulate_portfolio_risk.py 之 M1 跨市場類比。實證帳本 mc_simulation_run 六列:us1987/us2000/us2008 出數(n_stocks_min 717/1737/3009、maxdd -0.31652/-0.26537/-0.45565),us1929/us1973/uk1973 以 kind='analog_refused' 拒答(n_stocks_min 1/54/28 < MIN_ANALOG_STOCKS=100),三句 analog 揭露硬綁。它同時是最現成的 WM.36 違規實例(summary->>'market_table' 記字面表名 'USStockPrice'/'UKStockPrice'),故『補正這條路徑』＝最小成本同時證明「法屬世界」(概念鍵跨域可解析)與收斂既存合規債,不必開新戰場。  【順手發現、非本題(不擅自處理)】CLAUDE.md v1.31 橫幅仍引 `docs/原則精華_v1.10.0.md`,而該檔今日已升為 v1.11.0(檔名同步改名)。此屬 check_treaty_refs.py(今日新建,正為此類缺陷而生)射程內之交叉引用漂移,建議跑一次該 lint 確認,但我未改動任何治權檔。

</details>

---
## 九、分階段（每階段可獨立驗收、可獨立回退）

| 階段 | 內容 | 前置 | 產出 |
|---|---|---|---|
| **P0 環境前置** | `pip install peft trl bitsandbytes`＋4-bit 載入 smoke——**須在 DESKTOP-8MQPFS8 上做**（當家機無 GPU 無 CUDA、smoke 必失敗）；不動 torch/transformers 版本 | **DESKTOP 可用（並行使用中）** | `verify_lora_prereq.py` exit 0 且輸出含 hostname；當家機明記為不可跑之機 |
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
| V8 | P0 環境：4-bit 1.7b 載入成功、4b 明確 OOM（誠實記錄上限）——**驗收須附 hostname，於當家機執行者一律不算通過** | smoke log＋`verify_lora_prereq.py` 輸出 |

## 十一、誠實界限與風險

1. **本檔為計畫，未實作**：§四 DDL 尚未執行、§五 程式尚未寫；所有「已有」欄位皆本日親驗，所有「新增」皆未動工。
2. **微調棧未備＋載具錯置（親驗雙重更正）**：(a) peft／trl／bitsandbytes／gguf 四套件皆未裝；(b) **本檔初版把 GTX 1650 4GB 當成當家機能力，實為 DESKTOP-8MQPFS8 之硬體**——當家機 PC002-S1800 為 CPU-only 無獨顯（`ops/machines/` 兩檔逐行對照）。此為我**未先確認該硬體屬哪台機即引用**之誤（假兆③：憑記憶而未實證），致 §二／§六／§九 與 §8.4 agent 親驗結果自相矛盾，已於本版逐處更正。LoRA 排程須改為「週末於 DESKTOP 訓練、平日於當家機評測」，或改走非微調路線。
3. **雙寫期風險**：P3 採雙寫（既有＋統一）以保既有證據零動；若兩邊不一致，以既有為準、統一層標 `adapter_source` 待對帳——**不得反過來以統一層覆寫既有**。
4. **`walker_kind` 八值閉集**：新增第九類行走者屬治權變更（須入憲），不得由 code 逕自加值。
5. **不觸判準**：本計畫全部屬執行層（新增機制、接線、守夜人）；§八 ⑧之乙批五案與「一條路總則入憲」（乙-3）仍待 Steward 裁，**本計畫不預設其結果**。
6. **第二域 pilot 之邊界**：P6 僅到「走完一圈」之實證，**不含放量抓取、不含新 API 額度、不改 FREEZE 相關判準**。

---

*上位依據：`AUGUR-MC v1.6`（§4 EV 鏈／§P4／§P5）；`AUGUR-KS v1.1`（信度格／不朽律）；`AUGUR-L6`（授權鏈根為人／OCV 棘輪）；`AUGUR-L7`（登錄簿模式／可執行測試證明）；領域：大憲章 v1.49.0・原則精華 v1.11.0・CLAUDE.md v1.31。量尺：`reports/augur_plain_language_full_report_20260730.md`（v11）。姊妹計畫：`reports/augur_treaty_core_alignment_plan_20260730.md`（治權對核）。*

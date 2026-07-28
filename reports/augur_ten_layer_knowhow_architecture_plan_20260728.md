# Augur 10 層 Know-how（KH10）判準長期架構計畫 [I]

**日期**：2026-07-28  
**性質**：[I] plan-first 正式計畫書（CLAUDE #16／#20；憲章第六部計畫完整性 v1.39.0）  
**工作目錄**：`/home/hugo/project/augur`  
**定位**：把現有 **KH4 / RKI / KNI / IMPORT-QUAL-GATE / KH-XDOM / ATA / ADM-AI-ASSIST / PME-XDOM** 整併成一條 **raw data 產生智慧** 的長期架構，從「最低可用 know-how 閉環」升級到「10 層完整智慧線」  
**位階**：本檔為執行層與架構層藍圖，**不創設 [N]**；若後續需入憲或改治理判準，另開案  
**交叉錨點**：
- `reports/augur_raw_knowhow_interaction_probe_plan_20260728.md`（RKI：二元交互探針）
- `reports/augur_knowhow_nary_interaction_plan_20260728.md`（KNI：n 元交互）
- `reports/augur_knowhow_cross_domain_advisor_plan_20260728.md`（KH-XDOM：跨域檢索作答）
- `reports/augur_ai_admission_assist_plan_20260728.md`（ADM-AI-ASSIST：入庫前 AI 預審）
- `reports/augur_pme_cross_domain_evolution_enable_plan_20260728.md`（PME-XDOM：異域進化寫側）
- `reports/augur_pme_xdom_ai_predict_plan_20260728.md`（PME-XDOM-AI-PREDICT）
- `reports/augur_no_hardcode_db_ssot_constitution_plan_20260728.md`（NHC：策展映射住 DB）

---

## 0. 一句結論

**KH4 是最低可用閉環，確保 augur 已能「納入、檢索、交互、作答」；KH10 才是完整智慧線，要求系統不只會找資料，而是能對證據做合格檢驗、擴軸、投影交互、判斷可答、做矛盾對抗、權衡證據、紀律合成、回放學習、進化迭代，且全程保留 human override 與治理鎖。**

---

## 1. What / Why / Non-goals

### 1.1 What

本計畫要建立一個 **10 層 KH 判準架構**，把 augur 的 know-how 鏈路分成 10 個可機械驗證的層級。每一層都必須有：

1. 精確工程語意  
2. 狀態機或明確狀態  
3. 輸入／輸出定義  
4. 對應的表、腳本、模組  
5. 驗收條件  
6. live / batch 屬性  

目標不是新增一套平行宇宙，而是把既有 KH4、RKI/KNI、KH-XDOM、ATA、ADM-AI-ASSIST、IMPORT-QUAL-GATE、PME-XDOM 等，重新收編成同一條長期架構。

### 1.2 Why

現況其實已經有多個關鍵零件，但它們分散在不同計畫，且位階不同：

- `IMPORT-QUAL-GATE` 管的是匯入前合格檢驗
- `ADM-AI-ASSIST` 管的是 proposed/staging 的 AI 預審建議
- `RKI / KNI` 管的是 know-how 交互探針
- `KH-XDOM` 管的是跨域檢索作答
- `ATA` 管的是 coverage/terminal state 自動推進
- `PME-XDOM` 管的是「何時可以寫進 investment 假說鏈」

若沒有一個總體分層架構，系統容易發生三種長期風險：

1. 把局部能力誤當完整智慧，例如「能答」就誤認為「已會判斷與進化」。
2. 把探針、作答、進化、審批混成一團，最後誤踩治理紅線。
3. 為特定題目寫死 prompt / Q&A / 分支，違反 no-hardcode 與 DB-SSOT。

### 1.3 Non-goals

| 不做 | 理由 |
|---|---|
| 不 hardcode 專題答案樹 | KH10 的核心是一般機制＋DB 策展，不是領域專支 |
| 不自動 approve / activate 來源 | `approve` / `activate` 仍唯人；AI 只可做 assist / ATA 類執行層 |
| 不把 know-how 直接灌成預測因子 | KH 智慧鏈與 PME 寫側正交；要進 `principle_factor_map` 必經人策展與閘 |
| 不因 KH10 解凍 FinMind / FRED | 市場 API 凍結規則不變；KH10 主要吃庫內語料與 DB |
| 不把整庫 raw 升格成靈魂 / [N] | soul-vs-raw 邊界不變；升格的是交互抽象與可證偽關係 |
| 不等於自動下單或可交易宣稱 | KH10 是 know-how 智慧架構，不是交易最終授權 |

---

## 2. 為何 KH4 是最低線，KH10 才是完整智慧線

### 2.1 KH4 的定義

本計畫正式把 **KH4** 定義為：

1. **能進**：資料／語料可進入庫內且過最小 qualification
2. **能存**：可被切句、嵌入、檢索
3. **能交互**：可形成 know-how × know-how / raw 概念橋探針
4. **能答**：可在 guard 下組出引用回答，或誠實 decline

這 4 層對應到現況大致已存在的最小閉環：

- `IMPORT-QUAL-GATE`
- `ATA` / `FT-COV`
- `RKI` / `KNI`
- `KH-XDOM`

所以 KH4 是 **最低可用線**。沒有 KH4，augur 連「把 know-how 放進來並產生受控回答」都做不到。

### 2.2 為何 KH4 不夠

KH4 只能保證系統「可檢索、可交互、可作答」，但仍缺：

- qualification 之後的多軸擴展能力
- 對矛盾與反例的主動處理
- 證據強弱與風險權衡
- 合成紀律與結論邊界
- 回放與學習
- 可累積的演化閉環
- 治理層 final override

換句話說，KH4 比較像 **有知識管線的顧問**，還不是 **有紀律的智慧系統**。

### 2.3 KH10 的定義

**KH10** 是完整智慧線，要求系統具備以下 10 層能力，且每層有對應狀態機與驗收。  
前 4 層是最低線，後 6 層是完整智慧補齊。

---

## 3. KH10 十層逐層定義

### 3.1 總表

| 層 | 名稱 | 一句定義 | 性質 |
|---|---|---|---|
| KH1 | Qualification | 先判斷「這份輸入有沒有資格進鏈」 | 入門閘 |
| KH2 | Admission Assist | 在人裁前給出 AI 預審、風險旗標與排序 | 預審層 |
| KH3 | Terminal Readiness | 把可入庫內容推到 answerable / blocked 終態 | 終態層 |
| KH4 | Retrieval-Answer Baseline | 可檢索、可引用、可誠實作答 | 最低閉環 |
| KH5 | Axis Expansion | 把問題擴成多軸 know-how / raw 概念空間 | 擴軸層 |
| KH6 | Interaction Projection | 對多軸之間形成交互探針、橋接與候選關係 | 投影層 |
| KH7 | Adversarial Eligibility | 對回答與假說做可答性／矛盾／反例審核 | 對抗層 |
| KH8 | Evidence Weighting | 對證據厚度、來源、風險、時點做權重化判讀 | 權衡層 |
| KH9 | Synthesis & Replay | 依紀律產出結論，並把過程回放入帳 | 合成回放層 |
| KH10 | Evolution & Governance | 讓可驗學習進入進化閉環，但 final authority 仍在人 | 進化治理層 |

---

### KH1. Qualification

**工程語意**：  
任何輸入，不論來自本機匯入、SFTP、topic harvest、manual file、既有 staging，都必須先經過一層「是否有資格進 know-how 鏈」的檢驗。這層不處理「內容好不好」，只處理「能不能進系統」。

**狀態**：

- `new`
- `preflight_pass`
- `preflight_fail`
- `requires_human`

**輸入**：

- 本機匯入檔
- 遠端檔案
- harvest payload
- source metadata

**輸出**：

- `knowledge_import_job`
- `knowledge_import_qualification`
- verdict / reason code

**對應現況**：

- `IMPORT-QUAL-GATE`
- `scripts/migrate_import_qualification_ddl.py`
- `src/augur/knowledge/import_qualification.py`
- `scripts/acquire_local_files.py`

**驗收**：

1. dry-run 與真實最小匯入都會落 qualification
2. 不得 silent drop
3. reason code 由 DB SSOT 管，不散落在 code

**live / batch**：`live`

---

### KH2. Admission Assist

**工程語意**：  
在來源仍需人裁的前提下，系統可對 proposed source、staging candidate、待審 item 產生 AI assist：打分、排序、風險旗、建議理由，但不得改寫 `approval_status`。

**狀態**：

- `unreviewed`
- `assist_scored`
- `assist_hold`
- `escalated_to_human`
- `human_resolved`

**輸入**：

- `knowledge_source`
- `knowledge_staging`
- L1 admission gate 結果

**輸出**：

- `knowledge_admission_assist`
- `recommend_score`
- `flags`
- `reason`

**對應現況**：

- `ADM-AI-ASSIST`
- `scripts/assist_admission_review.py`
- `scripts/migrate_admission_assist_ddl.py`

**驗收**：

1. AI assist 永不執行 `approve` / `activate`
2. audit 可證明所有升級仍來自 HUMAN_ONLY
3. gov / assist 隊列可依 score / flags 排序

**live / batch**：`batch` 為主，可低頻 `live` 輔助

---

### KH3. Terminal Readiness

**工程語意**：  
系統要把「可入庫但尚不可答」的內容，推到一個誠實終態：要嘛 `answerable`，要嘛 `terminal_blocked`。這層的本質不是 approve，而是 **coverage completion**。

**狀態**：

- `pending`
- `ft_no_sent`
- `sent_no_emb`
- `answerable`
- `terminal_blocked`

**輸入**：

- `knowledge_item`
- `knowledge_item_text`
- `knowledge_fulltext_status`

**輸出**：

- sentences
- embeddings
- terminal advance logs

**對應現況**：

- `ATA`
- `FT-COV`
- `scripts/advance_knowledge_terminal.py`
- `build_sentences.py`
- `embed_knowledge.py`

**驗收**：

1. ATA 只推進終態，不碰 human approval
2. blocked 需誠實保留原因，不得洗成 answerable
3. terminal completion rate 可儀表化

**live / batch**：`batch`

---

### KH4. Retrieval-Answer Baseline

**工程語意**：  
系統已具備最低 know-how 閉環：可檢索、可引用、可 guard、可誠實 decline。這一層只要求「答得出或誠實答不出」，尚不要求回答已經過強對抗驗證。

**狀態**：

- `retrievable`
- `answerable`
- `declined_honestly`
- `guard_blocked`

**輸入**：

- query
- knowledge sentences / embeddings
- glossary / alias / topic mappings

**輸出**：

- cited answer
- decline
- guard result

**對應現況**：

- `KH-XDOM`
- `NHC`
- `src/augur/advisor/advise.py`
- `src/augur/philosophy/retrieval.py`
- `src/augur/advisor/query_translation.py`

**驗收**：

1. 跨域題可在無 `domain=` 作答閘時被檢索
2. guard 過或誠實 decline
3. 不可為單題硬寫 Q&A / if-domain 分支

**live / batch**：`live`

---

### KH5. Axis Expansion

**工程語意**：  
把單題 query 展開成可分析的多軸空間，而不是只把原句丟給檢索器。軸可以是 principle、domain、method、feature family、tech domain、raw concept bridge、time semantics。

**狀態**：

- `raw_query_only`
- `axis_extracted`
- `axis_normalized`
- `axis_scoped`

**輸入**：

- 原始 query
- `retrieve_glossary`
- `knowledge_topic_alias`
- `principle_domain_map`
- `knowledge_domain_map`

**輸出**：

- `axes[]`
- normalized query variants
- target domain candidates

**對應現況**：

- `KNI`
- `NHC`
- `retrieve_glossary`
- `RKI-FP-AI-SOLAR` / `arity` / `axes[]`

**驗收**：

1. 新三元／n 元議題靠 INSERT 或 DB 策展即可擴題
2. 不需要新增 `if 太陽能 and AI and 第一性`
3. 軸抽出結果可回放與追溯

**live / batch**：`live` 輕量 + `batch` 預運算均可

---

### KH6. Interaction Projection

**工程語意**：  
把多軸之間投影成可測的 interaction probes，不直接跳到答案。這層是 raw / know-how 智慧化的核心，因為它把「資料相鄰」提升成「可檢驗的交互候選」。

**狀態**：

- `seeded`
- `expanded`
- `probed`
- `gap_flagged`
- `candidate_formed`

**輸入**：

- `knowhow_interaction_probe`
- `arity`
- `axes`
- philosophy / knowledge / feature family / raw concept metadata

**輸出**：

- probe result
- gap flags
- spurious risk
- candidate bridge list

**對應現況**：

- `RKI`
- `KNI`
- `knowhow_interaction_probe`
- `scripts/run_knowhow_interaction_probes.py`（規畫／待補）

**驗收**：

1. 新交互議題可 INSERT 零改碼
2. probe 報告能區分有橋、缺料、假相關
3. 探針結果不是答案 SSOT

**live / batch**：`batch`

---

### KH7. Adversarial Eligibility

**工程語意**：  
不是所有 probe 結果或回答都可直接升格。這一層要對回答／假說做 adversarial check：有無矛盾、是否缺反例、是否可答但不可信、是否跨域過度投射。

**狀態**：

- `unchecked`
- `eligibility_pass`
- `eligibility_fail`
- `contradiction_found`
- `needs_human_review`

**輸入**：

- KH4 回答
- KH6 probe 結果
- guard 結果
- contradiction templates / eval set

**輸出**：

- eligibility verdict
- contradiction ledger
- escalation queue

**對應現況**：

- `KH-XDOM-EVAL`（待開）
- `KH-XDOM-QUAL`（待開）
- `deliberation_*`
- future `eval_cross_domain_advisor.py`

**驗收**：

1. 系統可標「可答但不夠可信」
2. 對跨域高風險回答可 escalate
3. contradiction / adversarial 結果可追溯

**live / batch**：`batch` 為主；關鍵路徑可 `live` 用輕量 eligibility

---

### KH8. Evidence Weighting

**工程語意**：  
把命中句、來源、終態、時點、license、cross-domain bridge、probe quality、反例狀況整合成證據權重。這層不是機率學裝飾，而是避免「有命中就算懂」。

**狀態**：

- `unweighted`
- `weighted`
- `risk_adjusted`
- `confidence_banded`

**輸入**：

- citation set
- source status
- probe quality
- contradiction flags
- terminal coverage

**輸出**：

- evidence weight vector
- confidence band
- risk notes

**對應現況**：

- 部分散落於 `relevance`、`guard`、`ATA`、`RKI gap_flags`
- 本計畫需新收編為統一 evidence model

**驗收**：

1. 回答可區分高證據 / 低證據 / 缺料
2. 高風險交互不可與高質量交互同權
3. 權重計算不依賴 hardcode 專題答案

**live / batch**：`live` 輕量打分 + `batch` 回放重算

---

### KH9. Synthesis & Replay

**工程語意**：  
對回答與候選結論施加 synthesis discipline。這層要求系統不只給片段，而是以紀律合成輸出，並把關鍵步驟回放入帳，以便日後比較、回歸、糾錯。

**狀態**：

- `drafted`
- `synthesized`
- `replay_logged`
- `postmortem_needed`

**輸入**：

- weighted evidence
- probe outputs
- eligibility verdict
- answer draft

**輸出**：

- structured synthesis
- replay log
- diffable artifact

**對應現況**：

- `reports/` 系列計畫部分手工承擔此責任
- `audits/` 承擔部分回放
- 本計畫需新規範為機械化輸出格式與帳本

**驗收**：

1. 系統可回看「為何這次這樣回答／這樣判定」
2. 不同 run 可比較
3. synthesis 不越權升格成 approve / activate / PME apply

**live / batch**：`batch`

---

### KH10. Evolution & Governance

**工程語意**：  
把可驗學習納入可持續閉環，但治理權仍在人。KH10 的重點不是「自動化愈多愈好」，而是「哪些可以自進化、哪些只能建議、哪些永遠 human override」。

**狀態**：

- `candidate_for_evolution`
- `governance_pending`
- `approved_for_loop`
- `rejected_for_loop`
- `superseded`

**輸入**：

- replay logs
- evidence histories
- PME candidate queues
- human rulings

**輸出**：

- new curated principles
- new maps / candidate queues
- updated probes / eval sets
- governance decision artifacts

**對應現況**：

- `PME-XDOM`
- `PME-XDOM-AI-PREDICT`
- `ADM-AI-ASSIST` 的 human boundary
- governance audits / plans

**驗收**：

1. 只有人能把 know-how 正式送進寫側閉環
2. 系統可自動形成 candidate，但不得自動 apply
3. human override、freeze、kill switch 必須常在

**live / batch**：`batch`

---

## 4. 各層與現有系統對應

### 4.1 功能對照表

| 現有系統 | 在 KH10 的位置 | 角色 |
|---|---|---|
| 本機匯入 / SFTP / topic harvest | KH1 | 輸入與 qualification 起點 |
| `IMPORT-QUAL-GATE` | KH1 | 匯入合格檢驗 |
| `ADM-AI-ASSIST` | KH2 | 人裁前 assist |
| `ATA` / `FT-COV` | KH3 | 終態推進 |
| `KH-XDOM` | KH4 | 跨域檢索作答最低閉環 |
| `NHC` | KH4 / KH5 | DB-SSOT query expansion / no-hardcode |
| `RKI` | KH6 | 二元交互探針 |
| `KNI` | KH5 / KH6 | n 元擴軸與交互投影 |
| future `KH-XDOM-EVAL` / `QUAL` | KH7 | 對抗與可答性評測 |
| unified evidence model | KH8 | 證據加權 |
| replay / audit ledger | KH9 | 回放與合成紀律 |
| `PME-XDOM` / `PME-XDOM-AI-PREDICT` | KH10 | 經人裁後的進化寫側 |

### 4.2 正交原則

| 邊界 | 正式定義 |
|---|---|
| KH10 ≠ 專題答案樹 | 只能靠 DB 策展＋統一檢索／probe／guard |
| KH10 ≠ 自動 approve | 來源升級仍唯人 |
| KH10 ≠ 自動 activate | 同上 |
| KH10 ≠ 預測熱路徑直接吃 know-how | 保持 `import_isolation` |
| KH10 ≠ 自動把 know-how 灌進因子 | 需人裁＋PME 閘 |
| KH10 ≠ API 解凍 | 市場 API 冻結規則不變 |

---

## 5. Schema 規畫

### 5.1 既有表（直接納入 KH10）

| 表 | KH 層 | 角色 |
|---|---|---|
| `knowledge_import_job` | KH1 | 匯入工作帳本 |
| `knowledge_import_qualification` | KH1 | qualification verdict |
| `knowledge_admission_assist` | KH2 | AI 預審建議 |
| `knowledge_item` | KH3+ | know-how 主體 |
| `knowledge_item_text` | KH3+ | 可答文本 |
| `knowledge_fulltext_status` | KH3 | blocked / fetch status |
| `knowledge_sentence` / embeddings | KH3 / KH4 | answerable 基礎 |
| `retrieve_glossary` | KH5 | query 擴軸詞表 |
| `knowledge_topic_alias` | KH5 | 主題別名 |
| `knowhow_interaction_probe` | KH6 | probe seeds / axes |
| `principle_domain_map` | KH5 / KH10 | 應用注記，非量化資格 |
| `principle_factor_map` | KH10 | 僅經人裁後之寫側映射 |

### 5.2 建議新增表

| 表 | 角色 | KH 層 |
|---|---|---|
| `knowhow_evidence_weight` | 存每次回答／探針的 evidence weighting 結果 | KH8 |
| `knowhow_synthesis_run` | 記錄一次 synthesis / replay | KH9 |
| `knowhow_contradiction_ledger` | 記矛盾、反例、eligibility fail | KH7 |
| `knowhow_evolution_candidate` | 存可供 human 審的演化候選 | KH10 |

### 5.3 建議 DDL 方向

```sql
-- KH8: 證據權重帳本（示意）
CREATE TABLE IF NOT EXISTS knowhow_evidence_weight (
    weight_id        BIGSERIAL PRIMARY KEY,
    run_id           TEXT NOT NULL,
    probe_id         TEXT,
    query_hash       TEXT NOT NULL,
    citation_count   INT NOT NULL DEFAULT 0,
    terminal_score   REAL NOT NULL DEFAULT 0,
    contradiction_score REAL NOT NULL DEFAULT 0,
    evidence_score   REAL NOT NULL DEFAULT 0,
    confidence_band  TEXT NOT NULL,
    risk_flags       JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- KH9: 合成/回放帳本（示意）
CREATE TABLE IF NOT EXISTS knowhow_synthesis_run (
    synthesis_id     BIGSERIAL PRIMARY KEY,
    run_id           TEXT NOT NULL UNIQUE,
    query_text       TEXT NOT NULL,
    answer_state     TEXT NOT NULL,
    evidence_score   REAL,
    replay_json      JSONB NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 6. Python / 模組規畫

### 6.1 既有腳本收編

| 檔 | KH 層 | 角色 |
|---|---|---|
| `scripts/acquire_local_files.py` | KH1 | import qualification writer |
| `scripts/migrate_import_qualification_ddl.py` | KH1 | qualification DDL |
| `scripts/assist_admission_review.py` | KH2 | assist scorer |
| `scripts/advance_knowledge_terminal.py` | KH3 | ATA runner |
| `src/augur/advisor/advise.py` | KH4 | answer generation |
| `src/augur/philosophy/retrieval.py` | KH4 / KH5 | retrieval and domain un-gating |
| `scripts/migrate_knowhow_interaction_probe_ddl.py` | KH5 / KH6 | probe schema |
| `scripts/curate_pme_xdom_ai_predict_map.py` | KH10 | human-curated write side |

### 6.2 建議新增腳本

| 檔 | 角色 | KH 層 |
|---|---|---|
| `scripts/run_knowhow_eligibility_eval.py` | 跑 answer / probe eligibility 與 contradiction checks | KH7 |
| `scripts/compute_knowhow_evidence_weight.py` | 統一 evidence weighting | KH8 |
| `scripts/replay_knowhow_run.py` | 回放單次回答／探針／合成 | KH9 |
| `scripts/curate_knowhow_evolution_candidates.py` | 形成可送 human 的 evolution candidates | KH10 |
| `scripts/migrate_kh10_ledger_ddl.py` | KH7~KH10 新帳本 DDL | KH7~KH10 |

### 6.3 library 模組建議

| 模組 | 角色 |
|---|---|
| `src/augur/knowledge/eligibility.py` | KH7 可答性/矛盾檢查 |
| `src/augur/knowledge/evidence.py` | KH8 證據加權規則 |
| `src/augur/knowledge/synthesis.py` | KH9 合成與 replay |
| `src/augur/knowledge/evolution.py` | KH10 candidate formation / governance boundary |

---

## 7. live vs batch 分層

### 7.1 可 live 的層

| 層 | 原因 |
|---|---|
| KH1 | 匯入當下就該判 qualification |
| KH4 | 作答需即時 |
| KH5 | query 擴軸可即時計算 |
| KH8 | 可做輕量 evidence scoring 輔助當次回答 |

### 7.2 應 batch / offline 的層

| 層 | 原因 |
|---|---|
| KH2 | assist 適合批量排隊與人裁前處理 |
| KH3 | terminal advance / embed 屬批次背景作業 |
| KH6 | probe 適合批次掃描與帳本化 |
| KH7 | adversarial / contradiction check 計算較重 |
| KH9 | replay / synthesis 屬回放工件 |
| KH10 | evolution candidate 與 governance 必須慢、可審、可停 |

### 7.3 混合層

KH7 / KH8 可做雙模式：

- `live`：輕量 eligibility / confidence band
- `batch`：完整對抗、重放、反例整理、權重重算

---

## 8. 分階實作路線

### 8.1 Stage 定義

| 階段 | 目標 | 對應 KH 層 |
|---|---|---|
| S1 | 固化最低閉環 | KH1-KH4 |
| S2 | 擴軸與交互化 | KH5-KH6 |
| S3 | 可答性與證據化 | KH7-KH8 |
| S4 | 合成、回放、進化治理 | KH9-KH10 |

### 8.2 建議執行順序

#### `KH10-S1`：最低閉環收斂

收斂並補齊：

- `IMPORT-QUAL-GATE`
- `ADM-AI-ASSIST` S1
- `ATA`
- `KH-XDOM`
- `NHC`

**驗收**：KH4 正式成立。

#### `KH10-S2`：擴軸與交互

擴充：

- `retrieve_glossary`
- `RKI-S2`
- `KNI-S2`
- n 元 probe runner

**驗收**：KH5-KH6 成立。

#### `KH10-S3`：對抗與權衡

新增：

- `KH-XDOM-EVAL`
- `KH-XDOM-QUAL`
- contradiction ledger
- evidence weighting ledger

**驗收**：KH7-KH8 成立。

#### `KH10-S4`：回放與治理進化

新增：

- synthesis run
- replay
- evolution candidate queue
- PME 人裁接口

**驗收**：KH9-KH10 成立。

---

## 9. 風險 / 延遲 / 成本 / cache / audit / human override

### 9.1 風險

| 風險 | 說明 | 緩解 |
|---|---|---|
| 名詞堆疊但無機械落點 | KH10 變成口號 | 每層強制表/腳本/驗收 |
| 重新造平行宇宙 | 與既有 KH-XDOM / PME 疊床架屋 | 優先收編既有表與模組 |
| 為了提昇命中率又偷加 hardcode | 破壞 NHC | 以 INSERT / alias / glossary / probe 取代 code 分支 |
| 自動化過界 | 誤踩 approve / activate / PME apply | HUMAN_ONLY 常鎖 |
| 探針結果被誤當因子 | KH 與 PME 邊界混掉 | KH10 文件與測試強制正交 |

### 9.2 延遲與成本

| 區塊 | 主要成本 |
|---|---|
| KH1-KH4 | 低到中，主要是收斂與補漏 |
| KH5-KH6 | 中，需補 probe runner / axes / query expansion |
| KH7-KH8 | 中到高，需定義 eval、矛盾、權重模型 |
| KH9-KH10 | 高，需治理設計與 replay 工具化 |

### 9.3 Cache

建議新增三類 cache：

1. `query axis cache`：KH5 軸抽取結果
2. `probe result cache`：KH6 對同一 probe / as-of 的結果
3. `evidence weight cache`：KH8 同一回答上下文的加權結果

原則：

- cache 是加速，不是權威
- SSOT 仍在 DB 原始表與 ledger
- cache 過期必須可重建

### 9.4 Audit

每層至少一個 audit 工件：

| 層 | 工件 |
|---|---|
| KH1 | qualification closure |
| KH2 | assist dry-run / apply audit |
| KH3 | ATA schedule / completion audit |
| KH4 | cross-domain answer eval |
| KH5-KH6 | probe inventory / runner closure |
| KH7-KH8 | eligibility / evidence audit |
| KH9-KH10 | replay / candidate governance audit |

### 9.5 Human Override

**正式原則**：

1. 人可停止任何 batch loop
2. 人可拒絕任何 evolution candidate
3. 人可保留 blocked 終態，不因 completeness 壓力而洗白
4. 人是 approve / activate / PME 寫側 final authority

---

## 10. 治理紅線

1. **不得 hardcode 專題答案樹**  
   包含 `if query contains "太陽能"` 類 prompt 分支、特定 Q&A 模板、單題英文詞表藏在 `.py`。

2. **不得自動 approve / activate**  
   KH2 assist、KH3 ATA、KH10 evolution 都不構成來源升級權限。

3. **不得把 know-how 自動灌進預測因子**  
   KH6 probe 結果、KH8 evidence score、KH9 synthesis 結果，都只能形成 candidate，不得直接寫入 `principle_factor_map` 或 prodset。

4. **不得把 KH10 誤解成解凍市場 API**  
   本架構可完全在 DB as-of 與本地 know-how 語料上成長。

---

## 11. 建議拍板碼

### 11.1 主拍板

| 碼 | 含義 | 建議 |
|---|---|---|
| `KH10-PLAN` | 採納本 10 層架構、層定義、正交邊界、分階與 schema/python 規畫 | ✅ 必拍 |
| `KH10-S1` | 開工最低閉環收斂（KH1-KH4） | ✅ 近程建議 |
| `KH10-S2` | 開工擴軸與交互（KH5-KH6） | 次拍 |
| `KH10-S3` | 開工 eligibility / contradiction / evidence（KH7-KH8） | 次拍 |
| `KH10-S4` | 開工 synthesis / replay / evolution governance（KH9-KH10） | 次拍 |

### 11.2 保留邊界碼

| 碼 | 含義 |
|---|---|
| `NHC-keep` | 保持 no-hardcode / DB-SSOT |
| `FZ-keep` | 保持 FinMind / FRED 凍結 |
| `PME-GATE-keep` | 保持寫側仍需人裁與閘 |
| `HUMAN-APPROVE-keep` | 保持 approve / activate 唯人 |

### 11.3 建議拍板句

```text
KH10-PLAN + KH10-S1 + NHC-keep + FZ-keep + PME-GATE-keep + HUMAN-APPROVE-keep
```

含義：採納 10 層 know-how 長期架構；先落最低閉環收斂；保留 no-hardcode、API 凍結、PME 寫側人裁與來源升級唯人。

---

## 12. 回報摘要（給拍板頁）

| 項 | 內容 |
|---|---|
| **路徑** | `reports/augur_ten_layer_knowhow_architecture_plan_20260728.md` |
| **一句總結** | KH4 是最低可用 know-how 閉環；KH10 才是 augur raw data 產生智慧的完整長期架構，新增的是擴軸、交互投影、對抗可答、證據權衡、回放與治理進化，而非專題 hardcode 或自動 approve |
| **建議拍板碼** | `KH10-PLAN`＋`KH10-S1`＋`NHC-keep`＋`FZ-keep`＋`PME-GATE-keep`＋`HUMAN-APPROVE-keep` |

---

## 13. 修訂

| 日期 | 說明 |
|---|---|
| 2026-07-28 | 初版：以現有 KH4 / RKI / KNI / IMPORT-QUAL-GATE / KH-XDOM / ATA / ADM-AI-ASSIST / PME-XDOM 整併成 10 層 KH 長期架構 |

*位階：[I] 計畫。治理原文仍以憲章 [N]、specs 與既有裁決為準。*

# KH10 Evolution & Governance 層開通計畫 [I]（2026-07-29）

* **性質**：[I] plan-first 計畫書（CLAUDE #16／#20；憲章第六部計畫完整性 v1.39.0）— **不創設 [N]；本輪只出計畫，不跑 code**
* **母計畫**：`reports/augur_ten_layer_knowhow_architecture_plan_20260728.md` §KH10 + §S4
* **授權**：`audits/NET8-WAVE-APPROVED-20260729.md` `KH10-ENABLE-PLAN` + `FZ-keep`
* **定位**：KH10 = 十層 Know-how 架構最頂層——讓可驗學習進入進化閉環，但 final authority 仍在人
* **正交**：PME-XDOM（寫側灌因子）、KH-XDOM（顧問讀側）、KH7-KH9（對抗／權衡／合成——KH10 消費其輸出）
* **治權錨**：憲章 v1.47.0 跨域原理映射準則；soul-vs-raw；predict-vs-market-api；FZ-keep

### Steward 拍板欄

| 欄 | 內容 |
|---|---|
| **日期** | 2026-07-29 |
| **狀態** | ⏳ 待拍 |
| **拍板碼** | `KH10-ENABLE-PLAN` + `FZ-keep` |
| **效力** | 採納 KH10 層 S0–S2 實作路線＋DDL＋腳本規畫；不實作 |

---

## 0. 一句結論

**KH10 Evolution & Governance 把 KH7–KH9 的對抗／權衡／合成產出，收斂為「可供人裁的進化候選佇列」，並以 governance ledger 記錄所有裁決——系統可自動形成 candidate，但永遠不得自動 APPLY。**

---

## 1. What / Why / Non-goals

### 1.1 What

KH10 層要解決的問題：**KH9 合成結果該怎麼變成系統可累積的進化？**

本層提供：

1. **Evolution candidate 佇列** — 從 KH9 synthesis / KH6 probe / PME-XDOM 候選中自動收集「可能值得進化的項目」
2. **Governance ledger** — 記錄每一筆人裁決定（approve / reject / defer / supersede），形成可追溯審計軌跡
3. **Human override 常鎖** — approve / activate / APPLY 永遠唯人；kill switch 隨時可停
4. **回饋閉環** — 裁決結果可回饋 KH7 eval set / KH8 weight tuning / KH9 replay

### 1.2 Why

- KH9 合成後若無收斂佇列，成果散落 `reports/` / `audits/`，無法機械化追蹤
- PME-XDOM 寫側需要結構化 candidate 來源，而非 ad-hoc 人讀報告
- 現況 `curate_pme_xdom_ai_predict_map.py` 是人驅腳本，但缺系統性 candidate formation 與 governance 帳本
- 母計畫 §KH10 已定義狀態機：`candidate_for_evolution → governance_pending → approved_for_loop / rejected_for_loop / superseded`

### 1.3 Non-goals

| 不做 | 理由 |
|---|---|
| 自動 APPLY evolution | HUMAN_ONLY 常鎖；AUTO-B 七閘 AND 不因 KH10 鬆動 |
| 自動寫 `philosophy_principle` | #1 禁 AI 生成入庫；人撰 |
| 把 KH10 當 API 解凍理由 | FZ-keep |
| 整庫 raw 灌 candidate | soul-vs-raw；candidate 須為**概念抽象**，非觀測列 |
| 繞過 PME 閘 | candidate 僅為佇列；進 prodset 仍走 G-PROM / G-ECON / AUTO-B 全鏈 |
| 本輪實作 code | plan-first only |

---

## 2. 與母計畫 §KH10 對齊

母計畫已定義 KH10 的：

| 母計畫定義 | 本計畫落地 |
|---|---|
| 狀態機 5 態 | §3 DDL `status` CHECK |
| 輸入：replay logs / evidence / PME candidate | §4.1 消費關係 |
| 輸出：new curated principles / maps / eval sets / governance artifacts | §4.2 產出 |
| 驗收三條 | §7 驗收條件 |

---

## 3. Schema（DDL 草案）

### 3.1 `knowhow_evolution_candidate` — 進化候選佇列

```sql
CREATE TABLE IF NOT EXISTS knowhow_evolution_candidate (
    candidate_id     BIGSERIAL PRIMARY KEY,
    source_type      TEXT NOT NULL
                     CHECK (source_type IN (
                       'kh9_synthesis','kh6_probe','pme_xdom_map',
                       'manual','kh7_contradiction')),
    source_ref       TEXT NOT NULL,          -- run_id / probe_id / map 行 ref
    hypothesis_text  TEXT NOT NULL,          -- 人讀一句：這個 candidate 想驗什麼
    target_domain    TEXT NOT NULL DEFAULT 'investment',
    axes_json        JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence_score   REAL,                   -- KH8 帶入，可 NULL
    status           TEXT NOT NULL DEFAULT 'candidate_for_evolution'
                     CHECK (status IN (
                       'candidate_for_evolution',
                       'governance_pending',
                       'approved_for_loop',
                       'rejected_for_loop',
                       'superseded')),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    note             TEXT
);
CREATE INDEX IF NOT EXISTS idx_evo_cand_status
  ON knowhow_evolution_candidate (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_evo_cand_source
  ON knowhow_evolution_candidate (source_type, source_ref);
```

### 3.2 `knowhow_governance_ledger` — 治理裁決帳本

```sql
CREATE TABLE IF NOT EXISTS knowhow_governance_ledger (
    ledger_id        BIGSERIAL PRIMARY KEY,
    candidate_id     BIGINT NOT NULL REFERENCES knowhow_evolution_candidate(candidate_id),
    decision         TEXT NOT NULL
                     CHECK (decision IN (
                       'approved','rejected','deferred','superseded','killed')),
    decided_by       TEXT NOT NULL DEFAULT 'HUMAN',  -- 永遠 HUMAN；AI 只 propose
    rationale        TEXT,
    downstream_ref   TEXT,           -- 若 approved：對應 principle_id / map_id
    decided_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_gov_ledger_cand
  ON knowhow_governance_ledger (candidate_id, decided_at DESC);
```

### 3.3 `knowhow_evolution_feedback` — 回饋閉環帳本

```sql
CREATE TABLE IF NOT EXISTS knowhow_evolution_feedback (
    feedback_id      BIGSERIAL PRIMARY KEY,
    ledger_id        BIGINT NOT NULL REFERENCES knowhow_governance_ledger(ledger_id),
    feedback_type    TEXT NOT NULL
                     CHECK (feedback_type IN (
                       'eval_set_update','weight_tune','probe_retire',
                       'replay_annotation','kill_propagation')),
    payload_json     JSONB NOT NULL DEFAULT '{}'::jsonb,
    applied_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    script           TEXT NOT NULL DEFAULT 'apply_evolution_feedback.py'
);
```

### 3.4 既有表消費（不新建，引用）

| 既有表 | KH10 角色 |
|---|---|
| `knowhow_kh7_eligibility` | candidate 來源之一（contradiction_found → 反面 candidate） |
| `knowhow_interaction_probe` / `_run` | KH6 probe 結果 → candidate 來源 |
| `knowhow_synthesis_run`（KH9 DDL，待建） | synthesis → candidate 來源 |
| `philosophy_principle` | approved candidate 最終落地處（人撰） |
| `principle_factor_map` | approved candidate 的 feature 映射（人撰） |
| `evolution_production_feature_set` | AUTO-B APPLY 終點（PME 既有鏈） |

---

## 4. 資料流

### 4.1 消費關係（KH10 吃什麼）

```
KH6 probe result ──┐
KH7 contradiction ─┤
KH8 evidence score ┤──→ knowhow_evolution_candidate
KH9 synthesis ─────┤
PME-XDOM map ──────┘
```

### 4.2 產出關係（KH10 產什麼）

```
knowhow_evolution_candidate
  ↓ (human governance)
knowhow_governance_ledger
  ↓ (if approved)
  ├─→ philosophy_principle (人撰)
  ├─→ principle_factor_map (人撰)
  └─→ knowhow_evolution_feedback → KH7 eval / KH8 weight / KH9 replay
```

### 4.3 決策閘

```
candidate → governance_pending → HUMAN decides
  ├─ approved → downstream PME 全鏈（G-PROM/G-ECON/AUTO-B）
  ├─ rejected → ledger 留痕 + optional feedback
  ├─ deferred → 佇列保留，不進 PME
  ├─ superseded → 被更新 candidate 取代
  └─ killed → 永遠不進；propagate kill to probes
```

---

## 5. Python 模組／腳本規畫

### 5.1 新增腳本

| 檔 | 角色 | KH 層 |
|---|---|---|
| `scripts/migrate_kh10_evolution_ddl.py` | 建三張新表（冪等） | KH10 DDL |
| `scripts/collect_evolution_candidates.py` | 從 KH6–KH9 / PME-XDOM 收集候選，INSERT `knowhow_evolution_candidate` | KH10 batch |
| `scripts/review_evolution_candidates.py` | 列出 `governance_pending` 候選供人裁；人裁後寫 `knowhow_governance_ledger` | KH10 interactive |
| `scripts/apply_evolution_feedback.py` | 依 ledger 裁決回饋 KH7 eval set / KH8 weight / probe retire | KH10 batch |

### 5.2 新增 library 模組

| 模組 | 角色 |
|---|---|
| `src/augur/knowledge/evolution.py` | candidate formation 邏輯、governance boundary 常數、feedback dispatcher |

### 5.3 既有腳本銜接（不改、只消費）

| 檔 | 銜接方式 |
|---|---|
| `scripts/curate_pme_xdom_ai_predict_map.py` | 人撰 map 時可參考 approved candidates |
| `scripts/run_knowhow_interaction_probes.py` | probe 結果為 candidate 來源 |
| `scripts/run_knowhow_eligibility_eval.py`（KH7） | eligibility 結果為 candidate 來源 |

---

## 6. 分階路線（S0–S2）

### S0. DDL + 空表 + 冪等遷移

**交付**：
- `scripts/migrate_kh10_evolution_ddl.py`：建 3 張表（冪等 `IF NOT EXISTS`）
- selftest `--selftest`：import smoke + 表存在斷言
- 執行指令矩陣

**驗收**：
- `python scripts/migrate_kh10_evolution_ddl.py` 可執行、冪等
- 3 張表存在、CHECK 約束正確

### S1. Candidate collection + governance CLI

**交付**：
- `scripts/collect_evolution_candidates.py`：掃描 KH6 probe / KH7 contradiction / KH9 synthesis（如已落地），INSERT candidates
- `scripts/review_evolution_candidates.py`：列出 pending、接受人裁 CLI（`--approve` / `--reject` / `--defer` / `--kill`）
- `src/augur/knowledge/evolution.py`：candidate formation + governance helpers

**驗收**：
- 可從 KH7 eligibility 表收集至少 1 筆 candidate（如 KH7 有資料）
- 人裁 → ledger 留痕
- `decided_by` 永遠 = `HUMAN`

### S2. Feedback loop + PME 銜接

**交付**：
- `scripts/apply_evolution_feedback.py`：依 approved/rejected/killed 回饋下游
- 與 PME-XDOM `curate_*` 腳本的銜接文件

**驗收**：
- approved candidate 可追溯到 governance ledger → 對應 principle_id / map
- killed candidate propagate 到 probe retire
- feedback 帳本有紀錄

---

## 7. 驗收條件（對齊母計畫 §KH10）

| # | 母計畫驗收條件 | 本計畫機械落地 |
|---|---|---|
| V1 | 只有人能把 know-how 正式送進寫側閉環 | `decided_by` DEFAULT 'HUMAN'；CLI 無 `--auto-approve`；code review 確認無繞路 |
| V2 | 系統可自動形成 candidate，但不得自動 apply | `collect_evolution_candidates.py` 只 INSERT candidate；`apply_evolution_promotions` 仍唯人觸發 |
| V3 | human override、freeze、kill switch 必須常在 | `--kill` flag propagate；governance ledger 不可刪（`ON DELETE RESTRICT`）；凍結仍 FZ-keep |

---

## 8. 風險與緩解

| 風險 | 緩解 |
|---|---|
| candidate 堆積無人裁 | `review_evolution_candidates.py` 附 priority sort（evidence_score DESC）；定期提醒 |
| governance 帳本被誤刪 | FK `ON DELETE RESTRICT`；備份隨 DB dump |
| 與 PME-XDOM 邊界混淆 | candidate ≠ principle；candidate 進 PME 仍需人撰 principle + map + 全鏈閘 |
| KH7–KH9 尚未全落地 | S1 設計為**有什麼吃什麼**——KH7 已有表即可收集；KH8/KH9 空則 candidate = 0，不報錯 |

---

## 9. 治理紅線

1. **HUMAN_ONLY 常鎖**：`decided_by` = `HUMAN`；禁 AI 寫 governance_ledger 的 decision
2. **不自動 APPLY**：candidate approved ≠ 已入 prodset；仍走 PME 全鏈
3. **不因 KH10 解凍 API**：FZ-keep
4. **不把整庫 raw 灌 candidate**：candidate 須為概念假說（hypothesis_text），非觀測列
5. **不降閘**：GATE-keep

---

## 10. 回報摘要（給拍板頁）

| 項 | 內容 |
|---|---|
| **路徑** | `reports/augur_kh10_enable_plan_20260729.md` |
| **一句總結** | KH10 Evolution 層以 3 張新表（candidate / governance ledger / feedback）＋4 支腳本＋1 支 library，讓 KH7–KH9 產出收斂為人裁進化佇列，永遠 HUMAN_ONLY |
| **建議拍板碼** | `KH10-ENABLE-PLAN` + `FZ-keep` |

---

## 11. 修訂

| 日期 | 說明 |
|---|---|
| 2026-07-29 | 初版：KH10 Evolution & Governance 層 S0–S2 計畫 |

*位階：[I] 計畫。治理原文仍以憲章 [N]、specs 與既有裁決為準。*

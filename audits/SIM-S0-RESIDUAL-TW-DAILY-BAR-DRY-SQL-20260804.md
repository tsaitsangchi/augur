# ⚠ DRY／勿執行 — `tw.daily_bar` → binding **75**（2026-08-04）

> **位階**：[I] DRY 備料（非 [N]）。  
> **授權殘差**：`SIM-S0-RESIDUAL: tw.daily_bar authoritative-binding | GATE-keep | no-SIM-apply`  
> **COMMIT 硬門**：`REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo` → ✅ **已 EXECUTED**（`audits/U0-75-REGISTRY-EXECUTED-20260804.md` · 2026-08-04 13:37:44+08）；本檔保留 DRY 原文備查  
> **上游備料**：`reports/wm_annexf_authoritative_binding_prep_20260803.md` §2.1／§5.1（建議案＝**75** `TaiwanStockPrice` observation；**不**採 81 derived／Adj）  
> **硬界**：GATE-keep · no-SIM-apply · 零 FinMind 放量 · AI 不代填 `decided_by`／不代 `COMMIT`

---

## 1. 診斷摘要（live 唯讀；2026-08-04）

| 項 | 值 |
|---|---|
| `world_concept_registry_current` `tw.daily_bar` | `authoritative_binding_id` **NULL**；`decided_by` NULL；category=`event` |
| binding **75** | `TaiwanStockPrice` · `observation` · `mapped` · `source_column` NULL（表級暫登） |
| binding **81** | `TaiwanStockPriceAdj` · `derived` · `mapped` · `source_column` NULL |
| 建議權威 | **75**（Annex F §2.1：欄 5／欄 7 只與 raw 相容；Adj＝restating 與「次一交易日定案」相斥） |
| `check_sim_clock` 消費點 | `resolve_sql("tw.daily_bar")` → TAIEX 日曆錨（禁 vendor 直綁） |

---

## 2. ⚠ DRY — BEGIN…ROLLBACK（Annex F 範本 A 形）

> `decided_by`／`decided_at`／`decision_ref` 佔位由 hugo 親打；**有 REGISTRY-GO 前不得改 COMMIT**。

```sql
-- SIM-S0-RESIDUAL tw.daily_bar → binding 75 · DRY／ROLLBACK only
BEGIN;
SET LOCAL augur.honesty_write = 'on';
-- ↑ 須另句 REGISTRY-GO honesty=75 通行證才得在親簽窗使用；本塊預設 ROLLBACK。

-- ① 標舊列 superseded（append-only；內容欄不原地改）
UPDATE world_concept_version
   SET superseded_at = now()
 WHERE concept_key = 'tw.daily_bar'
   AND superseded_at IS NULL;                       -- 期望 UPDATE 1

-- ② INSERT 新版本列（權威＝75；其餘六欄承襲現行列）
INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref,
     decided_by, decided_at)
SELECT concept_key,
       category,
       75,                                           -- Annex F §2.1 建議案
       ts_semantics, knowability_rule, cross_market_axis,
       coalesce(provenance, '{}'::jsonb) || jsonb_build_object(
           '採認狀態', 'adopted',
           'decision_ref', '⟨附卷／REGISTRY-GO 原文⟩',
           'adopted_basis',
             'Annex F-1；reports/wm_annexf_authoritative_binding_prep_20260803.md §2.1',
           'residual_auth',
             'SIM-S0-RESIDUAL tw.daily_bar authoritative-binding',
           'not_chosen_binding_id', 81,
           'not_chosen_reason',
             'derived／restating 與欄7「次一交易日定案」相斥'),
       finality_predicate, conflict_set_ref,
       '⟨hugo 親打⟩',
       TIMESTAMPTZ '⟨YYYY-MM-DD HH:MM:SS+08⟩'
  FROM world_concept_version
 WHERE concept_key = 'tw.daily_bar'
 ORDER BY transaction_time DESC
 LIMIT 1;                                            -- 期望 INSERT 0 1

-- ③ 驗（純 SELECT）
SELECT concept_key, authoritative_binding_id, decided_by, decided_at, category
  FROM world_concept_registry_current
 WHERE concept_key = 'tw.daily_bar';

SELECT binding_id, source_table, channel_role, mapping_status
  FROM world_channel_binding
 WHERE binding_id = 75 AND superseded_at IS NULL;

ROLLBACK;   -- ← 有 REGISTRY-GO＋親簽前禁止改 COMMIT
```

---

## 3. COMMIT 變體（**尚未授權**）

Steward 須另貼（或等價）：

```text
REGISTRY-GO: binding=75 + honesty=75 + decided_by=hugo
```

後：將上塊末行 `ROLLBACK` → `COMMIT`，並由 hugo 親填 `decided_by`／`decided_at`／`decision_ref`。  
執行後寫 `audits/SIM-S0-RESIDUAL-TW-DAILY-BAR-REGISTRY-EXECUTED-*.md`。

---

## 4. COMMIT 後驗收（預告；本窗不跑）

```bash
cd /home/hugo/project/augur
venv/bin/python -m augur.catalog.world_concept --resolve tw.daily_bar
# 期望 → TaiwanStockPrice（binding_id=75）
venv/bin/python scripts/check_sim_clock.py --check
# 期望：無 calendar_unmapped；週報行可含下一格日期（若日曆伸長）
```

---

## 5. 本窗不做

- 不 `COMMIT`／不寫 `decided_by=hugo`  
- 不改指 binding 81  
- 不 sim `--apply`／不 FinMind 放量／不殺 A1  

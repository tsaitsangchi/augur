# ⚠ DRY／勿執行 — P0-C 草案殘 86／35／70 dry SQL（W1-R2 · 2026-08-04）

> # ⚠⚠⚠ **DRY／勿執行** ⚠⚠⚠  
> **授權備料**：`W1-go`。**禁止 COMMIT**。  
> **形制**：Q-R1=(a)；W2-1=(a) 分隔字串（決策卡 2026-08-03）。  
> **honesty**：CIRCLE 39／50 證**已消費**→本批須**新證**。  
> **上游七欄**：`reports/wm_channel_registration_draft_20260803.md` §3.8／§3.15／§3.20。  
> **Live**：三 binding 現況＝`unmapped`／`concept_key` NULL（2026-08-04 親查）。

### 寫庫解鎖句（整批或分拆）

```text
REGISTRY-GO: Q-R1=a + honesty=86,35,70 + decided_by=hugo
```

---

## 1. 假設摘要

| binding | 表 | concept_key | category | source_column |
|---:|---|---|---|---|
| **86** | `TaiwanTotalExchangeMarginMaintenance` | `tw.margin_maintenance_ratio.market` | quantity | `TotalExchangeMarginMaintenance` |
| **35** | `TaiwanStockDayTrading` | `tw.day_trading.stock` | quantity | `Volume,BuyAmount,SellAmount` |
| **70** | `TaiwanStockMarketValue` | `tw.market_capitalization.stock` | quantity | `market_value` |

共通：ts=`交易日`；knowability=`收盤後當日可得`；finality=`當日值於次一交易日收盤後定案`；cross_market_axis=NULL。

---

## 2. Dry SQL｜86

```sql
-- ⚠ DRY — binding 86 only
BEGIN;
SET LOCAL augur.honesty_write = 'on';
INSERT INTO world_concept (concept_key) VALUES ('tw.margin_maintenance_ratio.market');
INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref,
     decided_by, decided_at)
VALUES (
    'tw.margin_maintenance_ratio.market', 'quantity', 86, '交易日',
    '收盤後當日可得（法定公開規則型；表內無公告欄）', NULL,
    jsonb_build_object(
        'basis', 'wm_channel_registration_draft §3.15',
        'dry_sql_ref', 'reports/augur_w2_draft8670_dry_sql_propose_20260804.md',
        'w2_1_form', 'delimiter_string', 'pilot_status', 'dry'),
    '當日值於次一交易日收盤後定案', NULL,
    '⟨hugo 親打⟩', TIMESTAMPTZ '⟨YYYY-MM-DD HH:MM:SS+08⟩');
UPDATE world_channel_binding
   SET concept_key='tw.margin_maintenance_ratio.market', mapping_status='mapped',
       source_column='TotalExchangeMarginMaintenance',
       provenance=coalesce(provenance,'{}'::jsonb)||jsonb_build_object('map_note','P0-C dry 86')
 WHERE binding_id=86 AND superseded_at IS NULL AND mapping_status='unmapped' AND concept_key IS NULL;
ROLLBACK;
```

## 3. Dry SQL｜35

```sql
-- ⚠ DRY — binding 35 only
BEGIN;
SET LOCAL augur.honesty_write = 'on';
INSERT INTO world_concept (concept_key) VALUES ('tw.day_trading.stock');
INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref,
     decided_by, decided_at)
VALUES (
    'tw.day_trading.stock', 'quantity', 35, '交易日',
    '收盤後當日可得（法定公開規則型）', NULL,
    jsonb_build_object(
        'basis', 'wm_channel_registration_draft §3.8',
        'consumption_anchor', 'build_daily_direction_features.py:136',
        'dry_sql_ref', 'reports/augur_w2_draft8670_dry_sql_propose_20260804.md',
        'w2_1_form', 'delimiter_string', 'pilot_status', 'dry'),
    '當日值於次一交易日收盤後定案', NULL,
    '⟨hugo 親打⟩', TIMESTAMPTZ '⟨YYYY-MM-DD HH:MM:SS+08⟩');
UPDATE world_channel_binding
   SET concept_key='tw.day_trading.stock', mapping_status='mapped',
       source_column='Volume,BuyAmount,SellAmount',
       provenance=coalesce(provenance,'{}'::jsonb)||jsonb_build_object(
           'map_note','P0-C dry 35','multi_value_note','BuyAfterSale 不入 source_column')
 WHERE binding_id=35 AND superseded_at IS NULL AND mapping_status='unmapped' AND concept_key IS NULL;
ROLLBACK;
```

## 4. Dry SQL｜70

```sql
-- ⚠ DRY — binding 70 only
BEGIN;
SET LOCAL augur.honesty_write = 'on';
INSERT INTO world_concept (concept_key) VALUES ('tw.market_capitalization.stock');
INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref,
     decided_by, decided_at)
VALUES (
    'tw.market_capitalization.stock', 'quantity', 70, '交易日',
    '收盤後當日可得（法定公開規則型）', NULL,
    jsonb_build_object(
        'basis', 'wm_channel_registration_draft §3.20',
        'dry_sql_ref', 'reports/augur_w2_draft8670_dry_sql_propose_20260804.md',
        'w2_1_form', 'delimiter_string', 'pilot_status', 'dry'),
    '當日值於次一交易日收盤後定案', NULL,
    '⟨hugo 親打⟩', TIMESTAMPTZ '⟨YYYY-MM-DD HH:MM:SS+08⟩');
UPDATE world_channel_binding
   SET concept_key='tw.market_capitalization.stock', mapping_status='mapped',
       source_column='market_value',
       provenance=coalesce(provenance,'{}'::jsonb)||jsonb_build_object('map_note','P0-C dry 70')
 WHERE binding_id=70 AND superseded_at IS NULL AND mapping_status='unmapped' AND concept_key IS NULL;
ROLLBACK;
```

## 5. 親簽後驗收

```bash
venv/bin/python -m augur.catalog.world_concept --check
venv/bin/python scripts/reconcile_channel_columns.py --survey
# 期望：mapped 15→18；sc 5→8
```

*零 COMMIT。*

-- U0-37 COMMIT — Steward: Q-R8=jp-ok + REGISTRY-GO: binding=37 + honesty=37 + decided_by=hugo
-- Dry twin: audits/U0-37-DRY-SQL-20260804.md (ROLLBACK form)
-- APPLIED 2026-08-04 11:34+08 (see audits/U0-37-REGISTRY-EXECUTED-20260804.md) — DO NOT RE-RUN
BEGIN;
SET LOCAL augur.honesty_write = 'on';

DO $$
DECLARE
  missing text;
BEGIN
  SELECT string_agg(c, ',') INTO missing
    FROM (VALUES ('Open'),('High'),('Low'),('Close'),('Volume')) AS t(c)
   WHERE NOT EXISTS (
     SELECT 1 FROM information_schema.columns
      WHERE table_schema='public' AND table_name='JapanStockPrice' AND column_name=t.c
   );
  IF missing IS NOT NULL THEN
    RAISE EXCEPTION 'U0-37 fail-closed: missing JapanStockPrice columns: %', missing;
  END IF;
END $$;

INSERT INTO world_concept (concept_key) VALUES ('jp.daily_bar');
INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref,
     decided_by, decided_at)
VALUES (
    'jp.daily_bar', 'quantity', 37, '交易日（日本市場）',
    '收盤後當日可得（法定公開規則型；表內無公告欄）',
    '日本市場交易日曆軸（非台股；與台股 as-of 對齊規則待裁）',
    jsonb_build_object(
        'basis', 'Q-R8=jp-ok + REGISTRY-GO binding=37',
        'dry_sql_ref', 'audits/U0-37-DRY-SQL-20260804.md',
        'w2_1_form', 'delimiter_string',
        'q_r8', 'jp-ok',
        'observation_columns', 'Open,High,Low,Close,Volume',
        'out_of_scope', jsonb_build_array('Adj_Close'),
        'category_note', 'quantity＝日頻 OHLCV 觀測（概念卡 U0-2）'),
    '當日值於次一交易日收盤後定案', NULL,
    'hugo', clock_timestamp())
RETURNING concept_key, category, authoritative_binding_id, decided_by, decided_at, cross_market_axis;

UPDATE world_channel_binding
   SET concept_key='jp.daily_bar', mapping_status='mapped',
       source_column='Open,High,Low,Close,Volume',
       provenance=coalesce(provenance,'{}'::jsonb)||jsonb_build_object(
           'map_note','U0-2 jp-ok 2026-08-04',
           'w2_1','delimiter_string',
           'out_candidate','Adj_Close 不入')
 WHERE binding_id=37 AND superseded_at IS NULL AND mapping_status='unmapped' AND concept_key IS NULL
RETURNING binding_id, concept_key, source_column, mapping_status;

COMMIT;

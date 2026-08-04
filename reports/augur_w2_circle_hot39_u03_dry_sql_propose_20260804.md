# ⚠ DRY／勿執行 — W2 CIRCLE HP-39＋U0-3（Gold）dry SQL — 2026-08-04

> # ⚠⚠⚠ **DRY／勿執行** ⚠⚠⚠
>
> **本檔＝登錄草稿、待通行證＋親簽後執行。**  
> **禁止**對 live DB `COMMIT`；示範以 `BEGIN; … ROLLBACK;`。  
> **禁止**代填 `decided_by`／`decided_at`（佔位 `⟨…⟩`）。  
> **觸發**：Steward「**要進 Registry**」（提案批准之後）。  
> **圈選**：`CIRCLE-39-U0: 登錄 HP-39+U0-3`（`reports/augur_w2_concept_cards_hot39_u0_20260804.md`）。

---

## 0. 本件邊界

| 項 | 本檔 |
|---|---|
| 射程 | **僅** binding **39**（`TaiwanStockBlockTrade`）＋ **50**（`GoldPrice`） |
| 不含 | U0-1／2／4／5／6（仍俟 Q-R*）；其他 65／草案殘 |
| 形制 | Q-R1＝**(a) 原地 UPDATE**（決策卡 2026-08-03 已裁）；W2-1＝**(a) 分隔字串**（同上） |
| U1 honesty 證 | **不可複用**（僅 31／62／93；已消費） |
| 本批 honesty | **待發** → `audits/W2-CIRCLE-HONESTY-PASSPORT-REQUEST-20260804.md` |
| 寫庫？ | **否**（本檔仍 DRY；須新證＋`decided_by` 親填＋明示「親簽執行／do it」） |

### 仍待 Steward 一句（建議複製）

```
REGISTRY-GO: Q-R1=a + honesty=39,50 + decided_by=hugo + Q-R8=cm-ok
```

| token | 意義 |
|---|---|
| `Q-R1=a` | 確認沿用已裁形制 (a) |
| `honesty=39,50` | **新發**通行證（U1 證不擴） |
| `decided_by=hugo` | 親簽欄允許寫入該字串（AI 仍不代打以外的人名） |
| `Q-R8=cm-ok` | 允許 `cm.gold.spot_price` 非 `tw.` 前綴（否則先改名再登） |

收到後：把本檔兩段 SQL 之 `⟨…⟩` 換成親簽值、`ROLLBACK`→`COMMIT`，寫 EXECUTED audit。

---

## 1. 試點假設

### 1.1 HP-39｜`tw.block_trade.print`

| 欄 | 值 |
|---|---|
| binding | **39**／`TaiwanStockBlockTrade` |
| category | `event` |
| ts_semantics | `交易日` |
| knowability_rule | `收盤後當日可得（TWSE 鉅額交易資訊盤後發布）；表內無公告欄，法定公開規則型（WM.31(b)）` |
| cross_market_axis | `NULL` |
| finality_predicate | `當日值於次一交易日收盤後定案` |
| source_column（W2-1=a） | `trading_money,price,volume`（無空白；`trade_type`＝列維度，不入欄——Q-R2 殘） |
| 消費錨 | `field_correlation.py:75` `block_money`←`sum(trading_money)` |

### 1.2 U0-3｜`cm.gold.spot_price`

| 欄 | 值 |
|---|---|
| binding | **50**／`GoldPrice` |
| category | `quantity` |
| ts_semantics | `觀測日（報價日）` |
| knowability_rule | `來源發布後當日可得；單位／幣別不在 schema（人裁殘）` |
| cross_market_axis | `全球商品現貨（非台股交易日曆軸；與台股 as-of 對齊規則待裁）` |
| finality_predicate | `當日報價值於次一日定案（未宣告更嚴規則前依 WM.32 缺省）` |
| source_column | `Price`（抽樣機械自動配對＝True） |
| Q-R8 | **須** `Q-R8=cm-ok` 或改名後重稿 |

---

## 2. Dry SQL｜binding 39

```sql
-- ⚠ DRY／勿執行 — CIRCLE HP-39 · binding 39 only
BEGIN;

SET LOCAL augur.honesty_write = 'on';
-- ↑ 須本批新通行證（39／50）；U1 證不可用。親簽前不得改 COMMIT。

INSERT INTO world_concept (concept_key)
VALUES ('tw.block_trade.print');

INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref,
     decided_by, decided_at)
VALUES (
    'tw.block_trade.print',
    'event',
    39,
    '交易日',
    '收盤後當日可得（TWSE 鉅額交易資訊盤後發布）；表內無公告欄，法定公開規則型（WM.31(b)）',
    NULL,
    jsonb_build_object(
        'source', '所列通道之當次回應',
        'basis', 'CIRCLE-39-U0；reports/augur_w2_concept_cards_hot39_u0_20260804.md 卡 HP-39',
        'decision_ref', 'CIRCLE-39-U0 + 提案批准 + 要進 Registry',
        'dry_sql_ref', 'reports/augur_w2_circle_hot39_u03_dry_sql_propose_20260804.md',
        'vendor_source', 'finmind',
        'w2_1_form', 'delimiter_string',
        'source_column_assumption', 'trading_money,price,volume',
        'consumption_anchor', 'src/augur/audit/field_correlation.py:75 block_money',
        'known_gaps', jsonb_build_array(
            'trade_type 列維度＝Q-R2 殘；消費端若篩類別仍須字面',
            '不等同 binding 42 BlockTradingDailyReport（B0 緩登）',
            'source_column 未主張 WM.36 全庫完成'
        ),
        'pilot_status', 'dry；待通行證＋親簽'
    ),
    '當日值於次一交易日收盤後定案',
    NULL,
    '⟨hugo 親打⟩',
    TIMESTAMPTZ '⟨YYYY-MM-DD HH:MM:SS+08⟩'
);

UPDATE world_channel_binding
   SET concept_key    = 'tw.block_trade.print',
       mapping_status = 'mapped',
       source_column  = 'trading_money,price,volume',
       provenance     = coalesce(provenance, '{}'::jsonb) || jsonb_build_object(
           'map_note', 'CIRCLE HP-39 2026-08-04；鉅額逐筆成交',
           'mapped_basis', 'reports/augur_w2_concept_cards_hot39_u0_20260804.md',
           'source_column_basis', 'W2-1=(a)；消費主欄 trading_money',
           'w2_1', 'delimiter_string',
           'multi_value_note', 'trade_type 不入 source_column'
       )
 WHERE binding_id = 39
   AND superseded_at IS NULL
   AND mapping_status = 'unmapped'
   AND concept_key IS NULL;
-- 期望 UPDATE 1

SELECT concept_key, category, authoritative_binding_id, decided_by
  FROM world_concept_registry_current
 WHERE concept_key = 'tw.block_trade.print';

SELECT binding_id, concept_key, source_column, mapping_status
  FROM world_channel_binding WHERE binding_id = 39 AND superseded_at IS NULL;

ROLLBACK;  -- 親簽執行時改 COMMIT
```

---

## 3. Dry SQL｜binding 50

```sql
-- ⚠ DRY／勿執行 — CIRCLE U0-3 · binding 50 only
BEGIN;

SET LOCAL augur.honesty_write = 'on';

INSERT INTO world_concept (concept_key)
VALUES ('cm.gold.spot_price');

INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref,
     decided_by, decided_at)
VALUES (
    'cm.gold.spot_price',
    'quantity',
    50,
    '觀測日（報價日）',
    '來源發布後當日可得；單位／幣別不在 schema（人裁殘）',
    '全球商品現貨（非台股交易日曆軸；與台股 as-of 對齊規則待裁）',
    jsonb_build_object(
        'source', '所列通道之當次回應',
        'basis', 'CIRCLE-39-U0；卡 U0-3',
        'decision_ref', 'CIRCLE-39-U0 + 提案批准 + 要進 Registry',
        'dry_sql_ref', 'reports/augur_w2_circle_hot39_u03_dry_sql_propose_20260804.md',
        'vendor_source', 'finmind',
        'w2_1_form', 'delimiter_string',
        'source_column_assumption', 'Price',
        'q_r8', 'cm-ok 待 Steward 明示',
        'known_gaps', jsonb_build_array(
            'Q-R8 命名空間',
            '單位／幣別不在 schema',
            '跨市場 as-of 對齊未裁'
        ),
        'pilot_status', 'dry；待通行證＋親簽＋Q-R8'
    ),
    '當日報價值於次一日定案（未宣告更嚴規則前依 WM.32 缺省）',
    NULL,
    '⟨hugo 親打⟩',
    TIMESTAMPTZ '⟨YYYY-MM-DD HH:MM:SS+08⟩'
);

UPDATE world_channel_binding
   SET concept_key    = 'cm.gold.spot_price',
       mapping_status = 'mapped',
       source_column  = 'Price',
       provenance     = coalesce(provenance, '{}'::jsonb) || jsonb_build_object(
           'map_note', 'CIRCLE U0-3 2026-08-04；黃金現貨單價',
           'mapped_basis', 'reports/augur_w2_concept_cards_hot39_u0_20260804.md',
           'source_column_basis', '抽樣 §2 #5 自動配對 Price',
           'w2_1', 'delimiter_string'
       )
 WHERE binding_id = 50
   AND superseded_at IS NULL
   AND mapping_status = 'unmapped'
   AND concept_key IS NULL;
-- 期望 UPDATE 1

SELECT concept_key, category, authoritative_binding_id, cross_market_axis, decided_by
  FROM world_concept_registry_current
 WHERE concept_key = 'cm.gold.spot_price';

SELECT binding_id, concept_key, source_column, mapping_status
  FROM world_channel_binding WHERE binding_id = 50 AND superseded_at IS NULL;

ROLLBACK;  -- 親簽執行時改 COMMIT
```

---

## 4. 親簽後驗收（COMMIT 後）

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
venv/bin/python -m augur.catalog.world_concept --check
venv/bin/python scripts/reconcile_channel_columns.py --survey
# 期望：mapped 13→15；source_column 3→5；兩概念可 resolve
```

---

## 5. 不做

- 本檔不 COMMIT、不代簽、不擴 U0 其餘五卡  
- 不改 `field_correlation.py` 直綁（解直綁＝另授權）  
- 不因 API-THAW 開 sync  

*完。*

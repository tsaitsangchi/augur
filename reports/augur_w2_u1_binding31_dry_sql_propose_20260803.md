# ⚠ DRY／勿執行 — W2 U1 binding 31 dry SQL／propose 稿 — 2026-08-03

> # ⚠⚠⚠ **DRY／勿執行** ⚠⚠⚠
>
> **本檔＝試點草稿、待親簽後執行。**  
> **禁止**對 live DB `COMMIT`／任何寫入路徑；示範以 `BEGIN; … ROLLBACK;` 包裹。  
> **禁止**代填 `decided_by`／`decided_at`（佔位 `⟨…⟩`）。  
> **FZ-keep** · **M-T5 不搶 heavy_slot** · **不 commit**。  
> 上游裁示：`reports/augur_w2_steward_cut_card_20260803.md`（2026-08-03 16:55+08 簽核）。

---

## 0. 本件邊界

| 項 | 本檔 |
|---|---|
| 射程 | **僅** binding **31**（`TaiwanStockBalanceSheet`）unmapped → mapped |
| 不含 | binding **62**（另檔 `augur_w2_u1_binding62_dry_sql_propose_20260803.md`）；**93**（另檔 `augur_w2_u1_binding93_dry_sql_propose_20260803.md`；已裁登錄／2-B 單概念） |
| 形制 | ① Q-R1＝**(a) 原地 UPDATE**；③ W2-1＝**(a) 分隔字串**；②-A／②-B 見決策卡建議原文（本批 31 不消費 2-B） |
| 寫庫？ | **否**（本輪仍不自動執行／不連庫 COMMIT；須親簽執行句才動） |
| honesty | **已發放**（限 U1 31／62／93 dry→親簽窗；見下節） |

### 通行證狀態

| 項 | 本檔 |
|---|---|
| 通行證 | **已發放**（決策卡 2026-08-03 **19:05+08** Steward 補裁；建議項） |
| 意義 | ＝允許「親簽後依 dry 稿執行 UPDATE」之**資格**；**≠** 已授權 `COMMIT` |
| 射程 | **僅** binding **31**（U1 試點窗內；不擴及其他 binding） |
| 仍待 | hugo 親填 `decided_by`／`decided_at` ＋明示一句「親簽執行／do it」（或等價） |
| 本輪 | **仍不自動執行**、零連庫 COMMIT；DRY 大紅字不變 |
| 不解凍 | 其他 binding · 假 concept 灌庫 · FinMind／FRED 取數 |

---

## 1. 試點假設（self-reported；摘自草案／Phase1／抽樣）

| 欄／假設 | 試點值 | 出處 |
|---|---|---|
| `binding_id` | **31** | Live／DRAFT23 |
| `source_table` | `TaiwanStockBalanceSheet` | 通道列（不變） |
| `concept_key` | **`tw.financial_statement.balance`** | 草案 §3.7；決策卡 U1-31 |
| `category` | `event` | 同 §3.6／§3.7（財報揭露＝事件；`state` 替代讀未另裁） |
| `ts_semantics` | `資料所屬期末（季底）` | 草案 §3.6／§3.7 |
| `knowability_rule` | `季底 +45 日（Q1/Q2/Q3）／+90 日（年報 Q4）` | 草案 §3.6（`release_lag.py` 已在產） |
| `finality_predicate` | `季報值於法定申報期屆滿後定案` | 草案 §3.6／A.37 例示二 |
| `cross_market_axis` | `NULL` | 本域 |
| **`source_column`（W2-1＝(a)）** | **`value`** | 抽樣 §2 #3：long-form 事實載體＝`value`；`type`＝PK 列鍵；`origin_name`＝provenance 非事實載體。單欄⇒分隔字串形僅一 token（無需逗號） |
| M3／68 | **不合併** | 草案 §3.7；決策卡備註 |
| 殘留（不阻塞本乾跑形） | 一概念對全表科目 vs 一科目一概念 **未裁**；可知錨不在表內（Q-R5-i） | 抽樣／草案；寫入 provenance 揭露 |

**分隔約定（③ (a)；本檔釘最小）**：`source_column`＝單欄 `text`；多欄時以英文逗號 `,` 連接、**無空白**；本試點＝單一識別符 `value`。

---

## 2. Dry SQL（形制 (a)；示範 `ROLLBACK`）

```sql
-- ⚠ DRY／勿執行 — 試點草稿、待親簽後執行
-- W2-CUT-20260803-U1-31 · binding 31 only · FZ-keep · NO-DB-THIS-FILE
BEGIN;

SET LOCAL augur.honesty_write = 'on';
-- ↑ 通行證已發放（限 U1 binding 31／62／93 之 dry→親簽執行窗）。
--   本檔仍 DRY／ROLLBACK；親簽前須 decided_by 親填＋明示「親簽執行／do it」，否則不得改 COMMIT。

-- ① 概念身分列（INSERT 免 honesty 通行證；幂等親簽前請先 SELECT 確認不存在）
INSERT INTO world_concept (concept_key)
VALUES ('tw.financial_statement.balance');
-- 期望：INSERT 0 1（若已存在 → 本句 FAIL；改核現況後再裁）

-- ② 概念版本列（WM.36 七欄 + decided_* 佔位）
INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref,
     decided_by, decided_at)
VALUES (
    'tw.financial_statement.balance',
    'event',
    31,
    '資料所屬期末（季底）',
    '季底 +45 日（Q1/Q2/Q3）／+90 日（年報 Q4）；表內無公告日欄，法定公開規則型（WM.31(b)；Q-R5-i 仍開放）',
    NULL,
    jsonb_build_object(
        'source', '所列通道之當次回應',
        'basis', 'W2 U1 試點；reports/wm_channel_registration_draft_20260803.md §3.7',
        'decision_ref', 'W2-CUT-20260803-U1-31',
        'cut_card', 'reports/augur_w2_steward_cut_card_20260803.md',
        'dry_sql_ref', 'reports/augur_w2_u1_binding31_dry_sql_propose_20260803.md',
        'vendor_source', 'finmind',
        'w2_1_form', 'delimiter_string',
        'source_column_assumption', 'value',
        'known_gaps', jsonb_build_array(
            'Q-R5-i：可知錨不在表內',
            '科目粒度：一概念對全表 type vs 一科目一概念 未裁',
            '金融保險／證券／期貨業 Q1/Q3 法定 60 日（release_lag docstring 自陳；現況 45 日低估）',
            'M3 合併候補 68：本輪明示分立'
        ),
        'pilot_status', '試點草稿、待親簽後執行'
    ),
    '季報值於法定申報期屆滿後定案',
    NULL,
    '⟨hugo 親打⟩',                          -- decided_by：AI 不代填
    TIMESTAMPTZ '⟨YYYY-MM-DD HH:MM:SS+08⟩'  -- decided_at：AI 不代填
);
-- 期望：INSERT 0 1

-- ③ 通道繫結 unmapped → mapped（CHECK：兩欄同句；UPDATE 需通行證）
UPDATE world_channel_binding
   SET concept_key    = 'tw.financial_statement.balance',
       mapping_status = 'mapped',
       source_column  = 'value',   -- W2-1=(a)；單欄＝單 token
       provenance     = coalesce(provenance, '{}'::jsonb) || jsonb_build_object(
           'map_note', 'W2 U1 試點 2026-08-03；資產負債表 long-form value',
           'mapped_basis', 'reports/wm_channel_registration_draft_20260803.md §3.7',
           'source_column_basis', 'reports/augur_w2_source_column_reconcile_sampling_20260803.md §2 #3',
           'w2_1', 'delimiter_string',
           'multi_value_note', 'type＝PK 列鍵（科目）；非 source_column；消費端仍依 type 篩選＝Q-R2 殘留'
       )
 WHERE binding_id = 31
   AND superseded_at IS NULL
   AND mapping_status = 'unmapped';
-- 期望：UPDATE 1

-- ④ 驗（純 SELECT）
SELECT concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
       cross_market_axis, finality_predicate, conflict_set_ref, decided_by, decided_at
  FROM world_concept_registry_current
 WHERE concept_key = 'tw.financial_statement.balance';

SELECT binding_id, concept_key, source_table, source_column, channel_role, mapping_status
  FROM world_channel_binding
 WHERE binding_id = 31;

ROLLBACK;   -- ⚠ DRY：一律 ROLLBACK；親簽核准前禁止改為 COMMIT
```

---

## 3. 親簽前檢查清單（零寫入）

1. `SELECT binding_id, concept_key, mapping_status, source_column FROM world_channel_binding WHERE binding_id=31;` → 預期現況 `unmapped`／`concept_key` NULL／`source_column` NULL。  
2. `SELECT 1 FROM world_concept WHERE concept_key='tw.financial_statement.balance';` → 預期無列（否則改冪等路徑）。  
3. **honesty 通行證＝已發放**（限 U1 31／62／93；見「通行證狀態」）——仍非自動執行。  
4. hugo 親填 `decided_by`／`decided_at` 後，另下一句明示「親簽執行／do it」（或「執行 binding 31 登錄」）才可把上節 `ROLLBACK` 改 `COMMIT`。  
5. 執行後（若授權）：`venv/bin/python -m augur.catalog.world_concept --check`。

---

## 4. 明確排除（防誤讀）

| ID | 本檔 |
|---|---|
| 62 | **已裁登錄**；dry SQL＝`augur_w2_u1_binding62_dry_sql_propose_20260803.md`（本檔不觸） |
| 93 | **已裁登錄**（2-B 單概念）；dry SQL＝`augur_w2_u1_binding93_dry_sql_propose_20260803.md`（本檔不觸） |
| 68 | 不合併、不觸碰 |
| 其餘 DRAFT23 | 不在本試點 |

---

## Trace

| 宣稱 | 出處 |
|---|---|
| 形制 (a)／W2-1 (a)／U1 僅 31 | 決策卡簽核 2026-08-03 |
| 七欄與 balance 概念 | `wm_channel_registration_draft_20260803.md` §3.6–§3.7 |
| `source_column=value` | 抽樣 §2 binding 31 |
| SQL 骨架 | 草案 §7.2 範本 A（改鍵／欄） |

*完。零 DB 連線寫入、零 commit、`decided_by` 未填。*

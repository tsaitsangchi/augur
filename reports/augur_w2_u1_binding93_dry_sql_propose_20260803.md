# ⚠ DRY／勿執行 — W2 U1 binding 93 dry SQL／propose 稿 — 2026-08-03

> # ⚠⚠⚠ **DRY／勿執行** ⚠⚠⚠
>
> **本檔＝試點草稿、待親簽後執行。**  
> **禁止**對 live DB `COMMIT`／任何寫入路徑；示範以 `BEGIN; … ROLLBACK;` 包裹。  
> **禁止**代填 `decided_by`／`decided_at`（佔位 `⟨…⟩`）。  
> **FZ-keep** · **M-T5 不搶 heavy_slot** · **不 commit**。  
> 上游裁示：`reports/augur_w2_steward_cut_card_20260803.md`（2026-08-03 **17:50+08** 補裁 **U1-93＝登錄**；口徑＝**2-B 單概念**；形制沿用同卡 ①(a)／③(a)）。
>
> **口徑釘死**：**2-B 單概念、非整表多靈魂**——本試點只登一個 `concept_key`＝`tw.business_cycle_indicator`；**不**依 A.11 嚴讀拆成 7–8 個概念／多 binding（日後可 supersede 再拆）。

---

## 0. 本件邊界

| 項 | 本檔 |
|---|---|
| 射程 | **僅** binding **93**（`TaiwanBusinessIndicator`）unmapped → mapped |
| 不含 | binding **31**／**62**（各另檔；已裁登錄，本檔不觸） |
| 形制 | ① Q-R1＝**(a) 原地 UPDATE**；③ W2-1＝**(a) 分隔字串**；②-A 範圍預設維持；**②-B＝(單) 單表單概念**（本批 93 消費此裁） |
| 寫庫？ | **否**（本輪仍不自動執行／不連庫 COMMIT；須親簽執行句才動） |
| honesty | **已發放**（限 U1 31／62／93 dry→親簽窗；見下節） |

### 通行證狀態

| 項 | 本檔 |
|---|---|
| 通行證 | **已發放**（決策卡 2026-08-03 **19:05+08** Steward 補裁；建議項） |
| 意義 | ＝允許「親簽後依 dry 稿執行 UPDATE」之**資格**；**≠** 已授權 `COMMIT` |
| 射程 | **僅** binding **93**（U1 試點窗內；不擴及其他 binding） |
| 仍待 | hugo 親填 `decided_by`／`decided_at` ＋明示一句「親簽執行／do it」（或等價） |
| 本輪 | **仍不自動執行**、零連庫 COMMIT；DRY 大紅字不變 |
| 不解凍 | 其他 binding · 假 concept 灌庫 · FinMind／FRED 取數 |

**與 31／62 稿目錄關係**：本檔**獨立新檔**（勿與 31／62 混併）；決策卡「Dry SQL 稿」表列三者並列。

---

## 1. 試點假設（self-reported；摘自草案／Phase1／抽樣／決策卡 2-B）

| 欄／假設 | 試點值 | 出處 |
|---|---|---|
| `binding_id` | **93** | Live／DRAFT23；U1 序 3 |
| `source_table` | `TaiwanBusinessIndicator` | 通道列（不變） |
| `concept_key` | **`tw.business_cycle_indicator`** | 草案 §3.10；決策卡 U1-93／**2-B (單)**；Phase1 §2.1 |
| `category` | `state` | 草案 §3.10（景氣狀態） |
| `ts_semantics` | `資料所屬期末（月）` | 草案 §3.10（親驗月頻） |
| `knowability_rule` | **`待定錨`** | 草案 §3.10／Q-R5-ii；表內無發布日欄；WM.31⇒不可 as-of（現行消費缺口顯性化） |
| `finality_predicate` | `未宣告` | 草案 §3.10（`attestation_mode=cadence`） |
| `cross_market_axis` | `NULL` | 本域 |
| 桶 | **B4**（5–9 值欄）；Live 抽樣 **8** 值欄 | 抽樣 §2 #9；Phase1 附錄 B4 |
| **`source_column`（W2-1＝(a)）** | 見下節 **入 8** 分隔字串 | ③(a)＋**2-B 單概念**＋草案 §3.10 景氣燈號／指標入同一概念 |

### 1.1 八值欄 → 入／出（W2-1＝(a)；**2-B 單概念**）

> **權威欄列**＝catalog／walkthrough `TaiwanBusinessIndicator`（PK＝`date` 不入值欄）。  
> **處置口徑**＝決策卡 **2-B (單)**＋草案 §3.10「領先／同時／落後指標＋對策信號燈號」＝**同一個世界概念之維度切面**——故 **8 欄全入**；**非整表另立多靈魂**。  
> A.11「一指標一概念」嚴讀＝**已裁否**（採暫登）；張力寫 provenance／`known_gaps`，日後可拆。

| 處置 | 欄名 | 理由（草案／抽樣要旨） |
|---|---|---|
| **入** `source_column` | `leading` | 領先指標 |
| **入** | `leading_notrend` | 領先指標（不含趨勢）＝同概念循環成分切面 |
| **入** | `coincident` | 同時指標 |
| **入** | `coincident_notrend` | 同時指標（不含趨勢） |
| **入** | `lagging` | 落後指標 |
| **入** | `lagging_notrend` | 落後指標（不含趨勢） |
| **入** | `monitoring` | 景氣對策信號（分數） |
| **入** | `monitoring_color` | 信號燈號＝`monitoring` 之分級呈現（抽樣：同一事實兩表徵；單概念下仍入同字串） |
| **出**（不入） | — | 無；PK `date` 非值欄。**不另立** 7–8 概念／binding |

**分隔約定（③ (a)；本檔釘）**：`source_column`＝單欄 `text`；多欄以英文逗號 `,` 連接、**無空白**；順序＝上表「入」列由上而下（catalog 欄序）。

**試點字面（8 token）**：

```text
leading,leading_notrend,coincident,coincident_notrend,lagging,lagging_notrend,monitoring,monitoring_color
```

**殘留（不阻塞 dry 形；須 provenance 揭露）**

1. **W2-4／A.11 張力**：單概念暫登與「每一指標為世界量」字面張力——已裁 2-B＝暫登、後可 supersede 拆分。  
2. **Q-R5-ii／待定錨**：無發布日欄⇒WM.31 不可 as-of；但 `build_market_direction_features`／`verify_regime_timing` **現正消費**——登錄＝缺口顯性化，非解凍／非放行 as-of。  
3. **`monitoring` vs `monitoring_color`**：同事實兩表徵——若日後採「多」會再裁是否獨立概念；本檔單概念兩者皆入。

---

## 2. Dry SQL（形制 (a)；示範 `ROLLBACK`）

```sql
-- ⚠ DRY／勿執行 — 試點草稿、待親簽後執行
-- W2-CUT-20260803-U1-93 · binding 93 only · 2-B single-concept · FZ-keep · NO-DB-THIS-FILE
BEGIN;

SET LOCAL augur.honesty_write = 'on';
-- ↑ 通行證已發放（限 U1 binding 31／62／93 之 dry→親簽執行窗）。
--   本檔仍 DRY／ROLLBACK；親簽前須 decided_by 親填＋明示「親簽執行／do it」，否則不得改 COMMIT。

-- ① 概念身分列（INSERT 免 honesty 通行證；幂等親簽前請先 SELECT 確認不存在）
INSERT INTO world_concept (concept_key)
VALUES ('tw.business_cycle_indicator');
-- 期望：INSERT 0 1（若已存在 → 本句 FAIL；改核現況後再裁）

-- ② 概念版本列（WM.36 七欄 + decided_* 佔位）
INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref,
     decided_by, decided_at)
VALUES (
    'tw.business_cycle_indicator',
    'state',
    93,
    '資料所屬期末（月）',
    '待定錨（表內無發布日欄；WM.31⇒不可用於任何 as-of 推理；Q-R5-ii 仍開放；現行消費缺口顯性化）',
    NULL,
    jsonb_build_object(
        'source', '所列通道之當次回應',
        'basis', 'W2 U1；reports/wm_channel_registration_draft_20260803.md §3.10',
        'decision_ref', 'W2-CUT-20260803-U1-93',
        'cut_card', 'reports/augur_w2_steward_cut_card_20260803.md',
        'dry_sql_ref', 'reports/augur_w2_u1_binding93_dry_sql_propose_20260803.md',
        'vendor_source', 'finmind',
        'w2_1_form', 'delimiter_string',
        'w2_4_grain', 'single_concept_provisional',
        'note_2b', '2-B 單概念、非整表多靈魂',
        'bucket', 'B4',
        'value_column_count', 8,
        'source_column_in', jsonb_build_array(
            'leading',
            'leading_notrend',
            'coincident',
            'coincident_notrend',
            'lagging',
            'lagging_notrend',
            'monitoring',
            'monitoring_color'
        ),
        'source_column_out', jsonb_build_array(),
        'source_column_assumption',
            'leading,leading_notrend,coincident,coincident_notrend,lagging,lagging_notrend,monitoring,monitoring_color',
        'known_gaps', jsonb_build_array(
            'W2-4／A.11：單概念暫登與「每一指標為世界量」張力；日後可 supersede 拆 7–8 keys',
            'Q-R5-ii：knowability=待定錨；現行 build_market_direction_features／verify_regime_timing 消費＝anti-leakage 缺口顯性化',
            'monitoring_color＝monitoring 分級呈現（同事實兩表徵）；單概念下兩者皆入 source_column'
        ),
        'pilot_status', '試點草稿、待親簽後執行'
    ),
    '未宣告',
    NULL,
    '⟨hugo 親打⟩',                          -- decided_by：AI 不代填
    TIMESTAMPTZ '⟨YYYY-MM-DD HH:MM:SS+08⟩'  -- decided_at：AI 不代填
);
-- 期望：INSERT 0 1

-- ③ 通道繫結 unmapped → mapped（CHECK：兩欄同句；UPDATE 需通行證）
UPDATE world_channel_binding
   SET concept_key    = 'tw.business_cycle_indicator',
       mapping_status = 'mapped',
       source_column  = 'leading,leading_notrend,coincident,coincident_notrend,lagging,lagging_notrend,monitoring,monitoring_color',
       provenance     = coalesce(provenance, '{}'::jsonb) || jsonb_build_object(
           'map_note', 'W2 U1 試點 binding 93；B4 八值欄全入單概念（2-B）',
           'mapped_basis', 'reports/wm_channel_registration_draft_20260803.md §3.10',
           'source_column_basis', 'reports/augur_w2_source_column_reconcile_sampling_20260803.md §2 #9＋2-B 單概念',
           'w2_1', 'delimiter_string',
           'w2_4', 'single_concept_provisional',
           'multi_value_note', '2-B 單概念、非整表多靈魂；八欄分隔字串'
       )
 WHERE binding_id = 93
   AND superseded_at IS NULL
   AND mapping_status = 'unmapped';
-- 期望：UPDATE 1

-- ④ 驗（純 SELECT）
SELECT concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
       cross_market_axis, finality_predicate, conflict_set_ref, decided_by, decided_at
  FROM world_concept_registry_current
 WHERE concept_key = 'tw.business_cycle_indicator';

SELECT binding_id, concept_key, source_table, source_column, channel_role, mapping_status
  FROM world_channel_binding
 WHERE binding_id = 93;

ROLLBACK;   -- ⚠ DRY：一律 ROLLBACK；親簽核准前禁止改為 COMMIT
```

---

## 3. 親簽前檢查清單（零寫入）

1. `SELECT binding_id, concept_key, mapping_status, source_column FROM world_channel_binding WHERE binding_id=93;` → 預期現況 `unmapped`／`concept_key` NULL／`source_column` NULL。  
2. `SELECT 1 FROM world_concept WHERE concept_key='tw.business_cycle_indicator';` → 預期無列（否則改冪等路徑）。  
3. **honesty 通行證＝已發放**（限 U1 31／62／93；見「通行證狀態」）——仍非自動執行。  
4. hugo 親填 `decided_by`／`decided_at` 後，另下一句明示「親簽執行／do it」（或「執行 binding 93 登錄」）才可把上節 `ROLLBACK` 改 `COMMIT`。  
5. 執行後（若授權）：`venv/bin/python -m augur.catalog.world_concept --check`。  
6. **不得**與 binding 31／62 同一事務強行合併（各檔獨立拍板碼；可分次親簽）。

---

## 4. 明確排除（防誤讀）

| ID | 本檔 |
|---|---|
| 31 | 另見 `augur_w2_u1_binding31_dry_sql_propose_20260803.md`——不觸 |
| 62 | 另見 `augur_w2_u1_binding62_dry_sql_propose_20260803.md`——不觸 |
| A.11「多」鍵 | **本檔不擬** 7–8 `concept_key`（2-B 已裁否） |
| 其餘 DRAFT23 | 不在本試點 |

---

## Trace

| 宣稱 | 出處 |
|---|---|
| 形制 (a)／W2-1 (a)／U1-93＝登錄／2-B (單) | 決策卡簽核 2026-08-03 17:50+08 補裁 |
| 七欄與 business_cycle_indicator 概念 | `wm_channel_registration_draft_20260803.md` §3.10 |
| B4／8 值欄／A.11 張力 | 抽樣 §2 binding 93（#9） |
| U1 序 3 | Phase1 §2.1 |
| SQL 骨架 | 草案 §7.2 範本 A（改鍵／欄）；對齊 31／62 dry 稿結構 |

*完。零 DB 連線寫入、零 commit、`decided_by` 未填。*

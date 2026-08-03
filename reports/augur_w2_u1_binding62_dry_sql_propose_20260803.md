# ⚠ DRY／勿執行 — W2 U1 binding 62 dry SQL／propose 稿 — 2026-08-03

> # ⚠⚠⚠ **DRY／勿執行** ⚠⚠⚠
>
> **本檔＝試點草稿、待親簽後執行。**  
> **禁止**對 live DB `COMMIT`／任何寫入路徑；示範以 `BEGIN; … ROLLBACK;` 包裹。  
> **禁止**代填 `decided_by`／`decided_at`（佔位 `⟨…⟩`）。  
> **FZ-keep** · **M-T5 不搶 heavy_slot** · **不 commit**。  
> 上游裁示：`reports/augur_w2_steward_cut_card_20260803.md`（2026-08-03 17:34+08 補裁 62＝登錄；形制沿用同卡 ①(a)／③(a)）。

---

## 0. 本件邊界

| 項 | 本檔 |
|---|---|
| 射程 | **僅** binding **62**（`TaiwanStockShareholding`）unmapped → mapped |
| 不含 | binding **31**（另檔）；**93**（另檔 `augur_w2_u1_binding93_dry_sql_propose_20260803.md`；已裁登錄／2-B 單概念） |
| 形制 | ① Q-R1＝**(a) 原地 UPDATE**；③ W2-1＝**(a) 分隔字串**；②-A 範圍預設維持；②-B 不消費於本批 62 |
| 寫庫？ | **否**（本輪仍不自動執行／不連庫 COMMIT；須親簽執行句才動） |
| honesty | **已發放**（限 U1 31／62／93 dry→親簽窗；見下節） |

### 通行證狀態

| 項 | 本檔 |
|---|---|
| 通行證 | **已發放**（決策卡 2026-08-03 **19:05+08** Steward 補裁；建議項） |
| 意義 | ＝允許「親簽後依 dry 稿執行 UPDATE」之**資格**；**≠** 已授權 `COMMIT` |
| 射程 | **僅** binding **62**（U1 試點窗內；不擴及其他 binding） |
| 仍待 | hugo 親填 `decided_by`／`decided_at` ＋明示一句「親簽執行／do it」（或等價） |
| 本輪 | **仍不自動執行**、零連庫 COMMIT；DRY 大紅字不變 |
| 不解凍 | 其他 binding · 假 concept 灌庫 · FinMind／FRED 取數 |

**與 31 稿目錄關係**：本檔**獨立新檔**（勿與 `augur_w2_u1_binding31_dry_sql_propose_20260803.md` 混併）；決策卡「Dry SQL 稿」表列二者並列。

---

## 1. 試點假設（self-reported；摘自草案／Phase1／抽樣）

| 欄／假設 | 試點值 | 出處 |
|---|---|---|
| `binding_id` | **62** | Live／DRAFT23；U1 序 2 |
| `source_table` | `TaiwanStockShareholding` | 通道列（不變） |
| `concept_key` | **`tw.foreign_ownership.stock`** | 草案 §3.4；決策卡 U1-62；Phase1 §2.1 |
| `category` | `state` | 草案 §3.4（外資持股比率＝時點存量） |
| `ts_semantics` | `交易日` | 草案 §3.4（TWSE 每交易日發布） |
| `knowability_rule` | **暫採甲讀**：`收盤後當日可得`；`RecentlyDeclareDate`＝內容欄非整列可知錨 | 草案 §3.4 兩讀；Q-R5-iii **未另裁**——寫入 provenance／known_gaps |
| `finality_predicate` | `當日值於次一交易日收盤後定案` | 草案 §3.4（採甲讀時） |
| `cross_market_axis` | `NULL` | 本域 |
| 桶 | **B5**（≥10 值欄）；Live 抽樣 **11** 值欄 | 抽樣 §2 #6；Phase1 附錄 B5 |
| **`source_column`（W2-1＝(a)）** | 見下節 **入 6** 分隔字串 | 抽樣 §2 #6 逐欄裁定 |

### 1.1 十一值欄 → 入／出（W2-1＝(a) 已裁形制）

> **權威入／出**＝W2 抽樣 §2 binding 62（B5）逐欄裁定；本試點**不另重裁**。

| 處置 | 欄名 | 理由（抽樣要旨） |
|---|---|---|
| **入** `source_column` | `ForeignInvestmentShares` | 外資持股股數＝概念事實維度 |
| **入** | `ForeignInvestmentSharesRatio` | 外資持股比率 |
| **入** | `ForeignInvestmentRemainingShares` | 外資尚可投資股數 |
| **入** | `ForeignInvestmentRemainRatio` | 外資尚可投資比率 |
| **入** | `ForeignInvestmentUpperLimitRatio` | 外資投資上限比率（⚠ 法令上限 vs 持股狀態——可能再拆；見殘留） |
| **入** | `ChineseInvestmentUpperLimitRatio` | 陸資投資上限比率（同上殘留） |
| **出**（不入） | `InternationalCode` | A.28 第二識別碼體系／identity claim ≠ 持股事實 |
| **出** | `stock_name` | 標籤 |
| **出** | `note` | 異動原因（非持股量測本體） |
| **出** | `NumberOfSharesIssued` | **另一世界事實**——應另立概念／binding |
| **出** | `RecentlyDeclareDate` | Q-R5-iii 兩讀未決；本試點採甲＝**內容欄**，故不進 `source_column` |

**分隔約定（③ (a)；本檔釘）**：`source_column`＝單欄 `text`；多欄以英文逗號 `,` 連接、**無空白**；順序＝上表「入」列由上而下。

**試點字面（6 token）**：

```text
ForeignInvestmentShares,ForeignInvestmentSharesRatio,ForeignInvestmentRemainingShares,ForeignInvestmentRemainRatio,ForeignInvestmentUpperLimitRatio,ChineseInvestmentUpperLimitRatio
```

**殘留（不阻塞 dry 形；須 provenance 揭露）**

1. **Q-R5-iii**：knowability 甲／乙兩讀未另裁；本檔暫採甲。  
2. **兩個 UpperLimitRatio**：屬監理上限狀態抑持股狀態——可能須拆第二概念／binding（W2-5）；本試點仍入同概念字串。  
3. **`NumberOfSharesIssued`**：另概念未立——本檔不登錄。

---

## 2. Dry SQL（形制 (a)；示範 `ROLLBACK`）

```sql
-- ⚠ DRY／勿執行 — 試點草稿、待親簽後執行
-- W2-CUT-20260803-U1-62 · binding 62 only · FZ-keep · NO-DB-THIS-FILE
BEGIN;

SET LOCAL augur.honesty_write = 'on';
-- ↑ 通行證已發放（限 U1 binding 31／62／93 之 dry→親簽執行窗）。
--   本檔仍 DRY／ROLLBACK；親簽前須 decided_by 親填＋明示「親簽執行／do it」，否則不得改 COMMIT。

-- ① 概念身分列（INSERT 免 honesty 通行證；幂等親簽前請先 SELECT 確認不存在）
INSERT INTO world_concept (concept_key)
VALUES ('tw.foreign_ownership.stock');
-- 期望：INSERT 0 1（若已存在 → 本句 FAIL；改核現況後再裁）

-- ② 概念版本列（WM.36 七欄 + decided_* 佔位）
INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref,
     decided_by, decided_at)
VALUES (
    'tw.foreign_ownership.stock',
    'state',
    62,
    '交易日',
    '收盤後當日可得（暫採甲讀：RecentlyDeclareDate＝內容欄非整列可知錨；Q-R5-iii 仍開放）',
    NULL,
    jsonb_build_object(
        'source', '所列通道之當次回應',
        'basis', 'W2 U1；reports/wm_channel_registration_draft_20260803.md §3.4',
        'decision_ref', 'W2-CUT-20260803-U1-62',
        'cut_card', 'reports/augur_w2_steward_cut_card_20260803.md',
        'dry_sql_ref', 'reports/augur_w2_u1_binding62_dry_sql_propose_20260803.md',
        'vendor_source', 'finmind',
        'w2_1_form', 'delimiter_string',
        'bucket', 'B5',
        'value_column_count', 11,
        'source_column_in', jsonb_build_array(
            'ForeignInvestmentShares',
            'ForeignInvestmentSharesRatio',
            'ForeignInvestmentRemainingShares',
            'ForeignInvestmentRemainRatio',
            'ForeignInvestmentUpperLimitRatio',
            'ChineseInvestmentUpperLimitRatio'
        ),
        'source_column_out', jsonb_build_array(
            'InternationalCode',
            'stock_name',
            'note',
            'NumberOfSharesIssued',
            'RecentlyDeclareDate'
        ),
        'source_column_assumption',
            'ForeignInvestmentShares,ForeignInvestmentSharesRatio,ForeignInvestmentRemainingShares,ForeignInvestmentRemainRatio,ForeignInvestmentUpperLimitRatio,ChineseInvestmentUpperLimitRatio',
        'known_gaps', jsonb_build_array(
            'Q-R5-iii：RecentlyDeclareDate 可知錨 vs 內容欄兩讀未另裁；本試點暫採甲',
            'ForeignInvestmentUpperLimitRatio／ChineseInvestmentUpperLimitRatio：法令上限 vs 持股狀態可能再拆概念',
            'NumberOfSharesIssued：另一世界事實，未入本概念、未另立 binding'
        ),
        'pilot_status', '試點草稿、待親簽後執行'
    ),
    '當日值於次一交易日收盤後定案',
    NULL,
    '⟨hugo 親打⟩',                          -- decided_by：AI 不代填
    TIMESTAMPTZ '⟨YYYY-MM-DD HH:MM:SS+08⟩'  -- decided_at：AI 不代填
);
-- 期望：INSERT 0 1

-- ③ 通道繫結 unmapped → mapped（CHECK：兩欄同句；UPDATE 需通行證）
UPDATE world_channel_binding
   SET concept_key    = 'tw.foreign_ownership.stock',
       mapping_status = 'mapped',
       source_column  = 'ForeignInvestmentShares,ForeignInvestmentSharesRatio,ForeignInvestmentRemainingShares,ForeignInvestmentRemainRatio,ForeignInvestmentUpperLimitRatio,ChineseInvestmentUpperLimitRatio',
       provenance     = coalesce(provenance, '{}'::jsonb) || jsonb_build_object(
           'map_note', 'W2 U1 試點 binding 62；B5 十一值欄入六出五',
           'mapped_basis', 'reports/wm_channel_registration_draft_20260803.md §3.4',
           'source_column_basis', 'reports/augur_w2_source_column_reconcile_sampling_20260803.md §2 #6',
           'w2_1', 'delimiter_string',
           'multi_value_note', '分隔字串六欄；NumberOfSharesIssued／RecentlyDeclareDate 明示不入'
       )
 WHERE binding_id = 62
   AND superseded_at IS NULL
   AND mapping_status = 'unmapped';
-- 期望：UPDATE 1

-- ④ 驗（純 SELECT）
SELECT concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
       cross_market_axis, finality_predicate, conflict_set_ref, decided_by, decided_at
  FROM world_concept_registry_current
 WHERE concept_key = 'tw.foreign_ownership.stock';

SELECT binding_id, concept_key, source_table, source_column, channel_role, mapping_status
  FROM world_channel_binding
 WHERE binding_id = 62;

ROLLBACK;   -- ⚠ DRY：一律 ROLLBACK；親簽核准前禁止改為 COMMIT
```

---

## 3. 親簽前檢查清單（零寫入）

1. `SELECT binding_id, concept_key, mapping_status, source_column FROM world_channel_binding WHERE binding_id=62;` → 預期現況 `unmapped`／`concept_key` NULL／`source_column` NULL。  
2. `SELECT 1 FROM world_concept WHERE concept_key='tw.foreign_ownership.stock';` → 預期無列（否則改冪等路徑）。  
3. **honesty 通行證＝已發放**（限 U1 31／62／93；見「通行證狀態」）——仍非自動執行。  
4. hugo 親填 `decided_by`／`decided_at` 後，另下一句明示「親簽執行／do it」（或「執行 binding 62 登錄」）才可把上節 `ROLLBACK` 改 `COMMIT`。  
5. 執行後（若授權）：`venv/bin/python -m augur.catalog.world_concept --check`。  
6. **不得**與 binding 31 同一事務強行合併（各檔獨立拍板碼；可分次親簽）。

---

## 4. 明確排除（防誤讀）

| ID | 本檔 |
|---|---|
| 31 | 另見 `augur_w2_u1_binding31_dry_sql_propose_20260803.md`——不觸 |
| 93 | **已裁登錄**（2-B 單概念）；dry SQL＝`augur_w2_u1_binding93_dry_sql_propose_20260803.md`——不觸 |
| 已出 5 欄 | 不寫入 `source_column`；`NumberOfSharesIssued` 不另立 binding |
| 其餘 DRAFT23 | 不在本試點 |

---

## Trace

| 宣稱 | 出處 |
|---|---|
| 形制 (a)／W2-1 (a)／U1-62＝登錄 | 決策卡簽核 2026-08-03 17:34+08 補裁 |
| 七欄與 foreign_ownership 概念 | `wm_channel_registration_draft_20260803.md` §3.4 |
| 入 6／出 5 | 抽樣 §2 binding 62（B5） |
| U1 序 2 | Phase1 §2.1 |
| SQL 骨架 | 草案 §7.2 範本 A（改鍵／欄）；對齊 31 dry 稿結構 |

*完。零 DB 連線寫入、零 commit、`decided_by` 未填。*

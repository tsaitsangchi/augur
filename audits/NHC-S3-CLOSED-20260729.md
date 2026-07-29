# NHC-S3 CLOSED（2026-07-29）

> **性質**：[I] 執行收官；不創設 [N]。  
> **授權**：Steward「所有 working 開始跑」＝開 **`NHC-S3`**（同掛 **`FZ-keep`**；**無** `NHC-CONSTITUTE`）。  
> **計畫**：`reports/augur_no_hardcode_db_ssot_constitution_plan_20260728.md` §3.3／§6 S3  
> **前置**：`audits/NHC-S12-CLOSED-20260728.md`（`retrieve_glossary` 讀表）  
> **不含**：改憲章 [N]／FinMind／FRED／`PME-XDOM-SOLAR`／為 A0 加領域答案樹

## 一、§3.3 逐件處置

| ID | 符號 | 處置 | 結果 |
|---|---|---|---|
| **Q1** | `_OOC_TOPICS` | **遷 DB** | 表 `advisor_distill_seed_topic`（kind=`ooc`）；active=**30** |
| **Q2** | `_IMPOSSIBLE_TOPICS` | **遷 DB** | 同表 kind=`impossible`；active=**16** |
| **A1** | `AWARDS` | **結案豁免**（bootstrap-seed） | 僅 expand 一次性 INSERT `knowledge_source`；runtime SSOT＝DB 列；註記於 `expand_knowledge_registry.py` |
| **C1** | `_DEDICATED_URL` 等 | **結案豁免**（07-13 裁定 3 維持） | catalog build 種子→`dedicated_url` 欄；註記於 `catalog/__init__.py` |
| **I1** | `_AGGREGATE_DAILY` | **完成欄 migrate** | `dataset_catalog.aggregate_daily_method` 已建；GoldPrice=`close`／TaiwanStockNews=`all`；runtime `aggregate_method` DB-first；code dict＝fail-safe 後備 |
| **L1** | `LICENSE_MAP` | **結案豁免**（封閉枚舉／邏輯側） | 與 `LICENSE_WHITELIST`／DB CHECK 同命運；註記於 `fetch_oa_fulltext.py` |

**驗收錨**：無殘留 A 類 clear 違規（S12 已清 G1；S3 清 Q1/Q2；其餘 borderline 正式豁免或 DB-first 交棒）。

## 二、做了什麼

| 項 | 狀態 | 摘要 |
|---|---|---|
| DDL＋種子 | ✅ | `scripts/migrate_advisor_distill_seed_topic_ddl.py --apply`；ooc=30／impossible=16；provenance=`steward_seed_nhc_s3_20260729` |
| 蒸餾讀表 | ✅ | `advisor_distill_generate_questions` 刪 runtime `_OOC_TOPICS`／`_IMPOSSIBLE_TOPICS`；`_load_seed_topics` 讀表；模板留 code（邏輯側） |
| I1 欄交棒 | ✅ | `migrate_catalog_aggregate_ddl.py --migrate` |
| 零專題答案樹 | ✅ | advisor／蒸餾路徑無 domain 答案常數／`domain_answer`；A0 四探針仍走通用 glossary／`advise` |
| FZ-keep | ✅ | 零 FinMind／FRED |
| 入憲 | ❌ | **無** `NHC-CONSTITUTE` → 未改 META／大憲章 |

## 三、驗證（真兆）

| 檢查 | 結果 |
|---|---|
| `migrate_advisor_distill_seed_topic_ddl.py --selftest` | ✅ |
| `advisor_distill_generate_questions.py --selftest` | ✅ 無 `_OOC_TOPICS`／`_IMPOSSIBLE_TOPICS` |
| `migrate_catalog_aggregate_ddl.py --selftest` | ✅ |
| `python -m augur.advisor.query_translation --selftest` | ✅（含 A0 四探針不崩；無 `_GLOSSARY`） |
| live：`_load_seed_topics` ooc=30／imp=16 | ✅ |
| live：`aggregate_method` DB-first | ✅ close／all／None |
| `check_cmd_matrix.py` | ✅ NEED=0（395 支） |

## 四、變更檔

- `scripts/migrate_advisor_distill_seed_topic_ddl.py` — **新**
- `scripts/advisor_distill_generate_questions.py` — 讀 `advisor_distill_seed_topic`
- `scripts/migrate_catalog_aggregate_ddl.py` — I1 apply＋`--selftest`
- `scripts/expand_knowledge_registry.py` — A1 豁免註記
- `scripts/fetch_oa_fulltext.py` — L1 豁免註記
- `src/augur/catalog/__init__.py` — C1 豁免註記
- 本 CLOSED；`HANDOFF.md` 近程一句；計畫拍板欄更新

## 五、硬邊界

| 項 | 結果 |
|---|---|
| 零 FinMind／FRED | ✅ |
| 不改 [N] | ✅ |
| 無太陽能／第一性專用組答分支 | ✅ |
| predict 不吃蒸餾種子表 | ✅（`advisor_distill_*` 已在 `FORBIDDEN_PREFIXES`） |

## 六、下一步（待人拍）

1. **`NHC-CONSTITUTE`** — 見文末建議拍板句（§7.2 草案入 [N]＋CLAUDE #29b 對齊）  
2. 可選：蒸餾重啟 `--batch-tag` 新批（消費 DB 種子；非本輪必跑）  
3. A0 加深答題 → INSERT glossary／知識管線／FT-COV，**勿**改碼專支  

---

## `NHC-CONSTITUTE` 建議拍板句（**僅建議 · 未執行 · 不改 [N]**）

> Steward 若採納入憲，建議回覆一字組合：  
> **`NHC-CONSTITUTE`**  
> （可同掛 **`FZ-keep`**；入憲範圍＝計畫 §7.2 草案——策展映射住 PG＋know-how 產生禁領域 hardcode＋明示豁免清單；落點＝大憲章第一部子條＋知識層表 roster 加 `retrieve_glossary`／`advisor_distill_seed_topic`＋CLAUDE #29b 對齊；**不解凍**市場 API。）

**本輪未拍 → agent 不得改憲章 [N] 正文。**

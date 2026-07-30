# NHC-CONSTITUTE CLOSED（2026-07-29）

> **性質**：[N] 憲章變更落地。  
> **授權**：Steward `NHC-CONSTITUTE`＋`FZ-keep`。  
> **計畫**：`reports/augur_no_hardcode_db_ssot_constitution_plan_20260728.md` §7.2 草案  
> **前置**：`audits/NHC-S12-CLOSED-20260728.md`＋`audits/NHC-S3-CLOSED-20260729.md`（code 已落地）

## 一、憲章變更（v1.48.0 → v1.49.0）

| 落點 | 動作 |
|---|---|
| **第一部「資料本質」** | 新增子條「**策展映射住 PostgreSQL（curated-mapping SSOT）〔v1.49.0〕**」——策展映射 runtime SSOT＝PG（`retrieve_glossary`／`advisor_distill_seed_topic`／`knowledge_topic_alias`…）；know-how 產生禁領域 hardcode；明示豁免清單（safe_general／relevance／guard／LICENSE_WHITELIST／SOURCE_TYPE_WHITELIST／演算法常數） |
| **第三部 philosophy 表 roster** | 加 `retrieve_glossary`／`advisor_distill_seed_topic` 交叉引用 |
| **修訂歷程** | v1.48.0→SUPERSEDED；v1.49.0→ACTIVE |
| **檔名** | `系統架構大憲章_v1.48.0.md` → `系統架構大憲章_v1.49.0.md` |

## 二、同步

| 檔 | 動作 |
|---|---|
| CLAUDE.md #29b | 舉例加 `retrieve_glossary`／`advisor_distill_seed_topic`〔v1.49.0 入憲〕 |
| GOVERNANCE-MAP | 版本 v1.48.0→v1.49.0；摘要更新 |
| CS 換發 | `docs/compliance/CS-系統架構大憲章_v1.49.0.md` |

## 三、硬邊界

| 項 | 結果 |
|---|---|
| 零 FinMind／FRED | ✅ |
| 未誤遷 safe_general／guard 豁免類 | ✅ |
| predict 不吃 glossary／distill 種子 | ✅（隔離不變式） |
| §7.2 草案原文忠實入憲 | ✅（含 NHC-S3 豁免結果：A1/C1/L1 結案豁免） |

## 四、留痕

- 計畫 `NHC-CONSTITUTE` 狀態→已執行
- NHC-S3-CLOSED §六 下一步→本收官

# RKI S0 庫內盤點 [I]（2026-07-28）

> **性質**：[I] 唯讀盤點；零寫生產表（除後續 S1 DDL）。  
> **拍板**：`RKI-PLAN`＋`RKI-SCOPE-ALL-KH`＋`RKI-S01`＋`FZ-keep`＋`NHC-keep`  
> **FZ-keep**：零 FinMind／FRED。  
> **實證**：`./venv/bin/python`＋`augur.core.db` 親查。

## 1. Consumable 表族

| 表 | 存在 | 列數 |
|---|---|---|
| `philosophy_principle` | ✅ | 40 |
| `philosophy_work` | ✅ | 1,579 |
| `philosophy_work_text` | ✅ | 31,782 |
| `philosophy_sentence` | ❌ | — |
| `principle_domain_map` | ✅ | 4 |
| `principle_factor_map` | ✅ | 67 |
| `knowledge_item` | ✅ | 270,333 |
| `knowledge_item_text` | ✅ | 155,748 |
| `knowledge_sentence` | ✅ | 1,786,656 |
| `knowledge_sentence_embedding` | ✅ | 1,720,541 |
| `knowledge_source` | ✅ | 3,603 |
| `feature_values` | ✅ | 2,559,434（distinct `feature`＝**38**） |
| `dataset_catalog` | ✅ | 97 |
| `column_catalog` | ✅ | 769 |
| `retrieve_glossary` | ✅ | 13 active |
| `field_knowhow_lexical_affinity` | ✅ | 65,795 |
| `knowhow_interaction_probe` | ❌→S1 建 | — |

## 2. 種子命中診斷（title／sentence；非答案）

| 族 | `knowledge_item` | `knowledge_sentence` | `retrieve_glossary` | 缺口桶 |
|---|---|---|---|---|
| 第一性／first principles | 17 | 872 | 0 | `no_glossary`（可 INSERT）；原則表 statement 字面命中 0→概念橋弱 |
| Pareto／八二 | 12 | 22 | 0 | `no_glossary`；原則字面弱 |
| 孫子／兵法 | 0（title） | 146 | 0 | title 弱；有 sentence；PME-XDOM 已有 literature bridge |
| 太陽能／光伏 | 2,455 | 4,552 | 2 | 語料足；概念橋仍靠 advise |
| 企管／management | 6,768 | 12,192 | 0 | 語料足 |
| AI／ML 相關 title | **2,282** | （未全扫 sentence） | 0 | 語料可橋；禁專答 |
| model evolution title | 47 | — | 0 | 偏薄→`gap` 風險 |
| 量化／預測／portfolio title | 686 | — | 0 | 可橋 |
| alignment／RLHF title | 85 | — | 0 | 可橋 |

## 3. PME／預測物件（可概念橋；非探針權重）

| 物件 | n |
|---|---|
| `principle_factor_map` | 67 |
| `evolution_run` | 4 |
| `evolution_production_feature_set` | 8 |
| `evolution_iteration_ledger` | 3 |
| `direction_arena_candidate` | 11 |
| `direction_arena_prediction` | 6,880 |
| `model_registry` | 15 |

## 4. 假相關／升格風險（預標）

| 風險 | 說明 |
|---|---|
| 字面「太陽」 | 天文語料共現 ≠ 太陽能材料概念 |
| AI×預測 | 語料共現 ≠ 可證偽閘門轉移；升格須人裁＋另拍 PME 碼 |
| 第一性×迭代 | 禁把探針報告當 citation 權威入 principle |

## 5. S0 結論

庫內 **足以做 DB 驅動探針帳本**；缺口誠實標 `no_glossary`／概念橋弱／model-evolution 語料偏薄。S1＝建表＋12 種子 INSERT。**S2 runner 另拍**；**`PME-XDOM-AI-PREDICT` 另拍**。

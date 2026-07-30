# LSR-S01 CLOSED（2026-07-30）

> **性質**：[I] 執行收官；不創設 [N]。  
> **授權**：Steward `LSRS-PLAN + LSR-S01 + FZ-keep`  
> **拍板**：`audits/LSRS-PLAN-S01-APPROVED-20260730.md`  
> **計畫**：`reports/augur_long_sentence_resplit_embed_kh10_bridge_plan_20260730.md`  
> **不含**：LSRS-S23（再嵌／KH4／admit）／KH10-ENABLE-S1

## 一、做了什麼

| 階段 | 結果 |
|---|---|
| **S0 DDL** | `scripts/migrate_sentence_resplit_ddl.py --apply` → `knowledge_sentence_resplit_ledger` |
| **S1 library** | `src/augur/knowledge/sent_resplit.py`（`--selftest` 綠） |
| **S1 CLI** | `scripts/resplit_long_sentences.py` |
| **S1.1 前瞻** | `build_sentences.py --max-chars`（新段硬切；禁 >1000） |
| **items apply** | `--apply --side items --max-chars 800`；**3111** parents；fail=0 |
| **FZ-keep** | ✅ |

## 二、真兆

| 指標 | 前 | 後 |
|---|---:|---:|
| items 側 `len>800` 句（parents） | 3594 句／3111 parent | **0／0** |
| items 句總數 | 247,638 | **269,331** |
| ledger 列（note=LSRS-S01-20260730） | 0 | **3111** |
| sum(old_count)→sum(new_count) | — | 見 DB ledger 合計 |

log：`/tmp/lsr_s01_apply_items_20260730.log`

## 三、硬邊界

| 項 | |
|---|---|
| 未改 `is_junk` 1000 線 | ✅ |
| 未跑 embed／KH4／admit | ✅（屬 S23） |
| 未開 KH10-S1 | ✅ |
| 刪舊句時 CASCADE 嵌 → 受影響 parent 需 S23 再嵌 | ✅ 誠實 |

## 四、下一步（待另令）

```text
LSRS-S23 + FZ-keep
```

→ en／zh items `--gap-fill` → Qdrant `--url` → KH4 refresh → `admit --until-empty --apply-up-to 9`

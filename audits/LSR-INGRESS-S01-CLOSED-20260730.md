# LSR-INGRESS-S0／S1 CLOSED（2026-07-30）

> **性質**：[I] 執行收官；不創設 [N]。  
> **授權**：Steward `LSR-INGRESS-PLAN + LSR-INGRESS-S0 + LSR-INGRESS-S1 + FZ-keep`  
> **拍板**：`audits/LSR-INGRESS-PLAN-S01-APPROVED-20260730.md`  
> **計畫**：`reports/augur_long_sentence_resplit_embed_kh10_bridge_plan_20260730.md`  
> **不含**：S2 後台／acquire 接線；KH10 自動 APPLY

## 一、做了什麼

| 階段 | 結果 |
|---|---|
| **S0 DDL** | `scripts/migrate_knowledge_ingress_kip_ddl.py --apply` → `knowledge_ingress_kip_run` |
| **S1 library** | `src/augur/knowledge/ingress_kip.py`（`--selftest` 綠） |
| **S1 CLI** | `scripts/run_knowledge_ingress_kip.py` |
| **段序** | sentences → resplit → embed（scoped）→ qdrant（可 skip）→ kh4 → admit≤9 |
| **FZ-keep** | ✅ 零市場 API |

## 二、真兆（實測）

| 項 | 結果 |
|---|---|
| DDL `--selftest`／`--apply` | ✓；表已在 |
| library／CLI `--selftest` | ✓ |
| `check_cmd_matrix` | NEED=0 |
| dry-run job4 limit=2 | kip_run_id=2；status=done；各段 dry_run ok |
| apply item `277615` `--skip-qdrant` | kip_run_id=4；status=**done**；kh4 eligible=1；admit depth_hist `{9:1}` |

## 三、硬邊界

| 項 | |
|---|---|
| 未接 acquire_local／remote／admin（屬 S2） | ✅ |
| 未自動 KH10／PME APPLY | ✅ |
| junk／max_chars≤800 未放寬 | ✅ |
| qdrant 可 `--skip-qdrant`／無 url 誠實 skip | ✅ |

## 四、下一步（待另令）

```text
LSR-INGRESS-S2 + FZ-keep
```

→ local／sftp／harvest／admin 預設呼叫 `run_kip_for_items`

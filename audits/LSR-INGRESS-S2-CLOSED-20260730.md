# LSR-INGRESS-S2 CLOSED（2026-07-30）

> **性質**：[I] 執行收官；不創設 [N]。  
> **授權**：Steward `LSR-INGRESS-S2 + FZ-keep`  
> **拍板**：`audits/LSR-INGRESS-S2-APPROVED-20260730.md`  
> **計畫**：`reports/augur_long_sentence_resplit_embed_kh10_bridge_plan_20260730.md`

## 一、做了什麼

| 通道／面 | 接線 |
|---|---|
| **本機** | `acquire_local_files` 預設 `run_kip_hook`；`--no-kip`／`--acquire-only`；完成標記移到 KIP 之後 |
| **SFTP** | `acquire_remote_files` 對新 item 預設 KIP；`--acquire-only` 交 DAG |
| **主題抓取** | `acquire_topic` 下游 `--until kip`；`refresh_knowledge_pipeline` 加 `resplit`＋`kip`，`sentences` 帶 `--max-chars 800` |
| **後台** | 上傳／SFTP 預設勾 KIP；進度顯示 kip_status；`/gov` 列 `kip_runs` |
| **library** | `run_kip_hook`／`record_kip_skipped_explicit`／`--domain`＋`--needs-kip` |

## 二、真兆

| 項 | 結果 |
|---|---|
| `ingress_kip`／CLI `--selftest` | ✓ |
| 靜態配線（三 acquire／refresh／admin） | ✓ |
| DAG dry-run 矩陣（DB 曾連通時） | 見 `resplit` 段；`kip` 待辦 SQL 已修 `target_kind`／`target_id` |
| 收官當下 live DB | ⚠ PostgreSQL 17 cluster 標 **down**／5432 拒連（進程殘影；未能重啟）；**未**再跑 live apply |
| admin | 已重啟載入新碼（`serve_admin_console.py --serve`） |

## 三、硬邊界

| 項 | |
|---|---|
| FZ-keep | ✅ |
| 不自動 KH10 APPLY | ✅ |
| `--no-kip` → `skipped_explicit` 帳 | ✅ |
| DAG `--acquire-only` 不雙跑 KIP 於 acquire 時 | ✅（kip 段收束） |

## 四、建議用戶

Postgres 恢復後可驗：

```text
python scripts/run_knowledge_ingress_kip.py --channel local_files --job-id 4 --limit 2 --dry-run --skip-qdrant
python scripts/refresh_knowledge_pipeline.py --dry-run --from-stage sentences --until kip
```

---
name: qdrant-serving-hnsw-overfilter
description: Qdrant serving 上線(2026-07-14 拍板)+pgvector HNSW+CLEAN WHERE over-filtering 陷阱與 shadow eval 假 FAIL 鑑識
metadata: 
  node_type: memory
  type: project
  originSessionId: 778040ca-21b5-4b60-ad2d-0fad302930ca
---

**Qdrant serving 已上線（hugo 2026-07-14 拍板「一定要上 Qdrant」）**：`augur-qdrant.service`（systemd user、開機自啟）、storage=`~/qdrant_augur`（augur 專屬、不共用 ttai）、二進位暫用 `~/project/ttai/.qdrant_server/qdrant`（native 85MB）。sentence_items public en 55,861 向量 synced 差=0（⚠2026-07-17 本機實查 Qdrant collection points_count=55,854、PG CLEAN×public=55,861→**差 7**;「差=0」是 `qdrant_sync_state` 帳本宣稱、與實際 server 不符,成因未定、Qdrant 儲存不隨 pg_dump 遷移→本機不宜當現況引用）；config `sentence_items=qdrant_server` active；shadow eval **0.972 PASS**。pgvector 仍 SSOT、Qdrant 可拋棄隨時從 PG 重建。

**核心陷阱（鑑識教訓）**：`pgvector HNSW + CLEAN-public WHERE` 會 **over-filter**——items 語料 15 萬多為 local_private ERP，查詢最近向量多為私有 → HNSW 取 top-ef 候選後被 WHERE 事後濾空 → **COUNT 有 5.5 萬可搜但 ORDER BY <=> LIMIT 10 回 []**。兩個下游假象：① shadow eval 假 FAIL（0.302→查詢池未過 CLEAN 被 ERP 主宰＋baseline 假空；修查詢池 CLEAN 後 0.716 仍低→baseline 本身退化）② 生產 public ANN 檢索劣化。**鑑識法**：`SET LOCAL enable_indexscan=off` 跑 exact 比對——Qdrant vs exact=0.988（近完美）、vs HNSW=0.61 → 證明 Qdrant 優、退化在 pgvector HNSW 過濾路。shadow eval baseline 已修為 exact ground truth（verify_qdrant_shadow.py）。

**Why**: 誤信 HNSW-filtered baseline 會把「Qdrant 更好」誤判成「Qdrant 壞掉」，方向完全相反；分區式外部索引（預先只含 public、無 WHERE）正是 over-filtering 的解。

**How to apply**: 凡 pgvector 帶高選擇性 WHERE 的 ANN 出現空/劣化結果，先跑 exact（enable_indexscan=off）分辨「索引近似問題 vs 資料真沒有」；比對兩索引品質一律用 exact 當 ground truth。retrieval.py 讀路：Qdrant 只服務 `access_scope='public'`、private 直走 pgvector、Qdrant 未填滿 k 回落 pgvector 補。相關：[[restart-systemd-after-edit]]（改 retrieval 後須 restart advisor）、[[augur-construction-v4]]。

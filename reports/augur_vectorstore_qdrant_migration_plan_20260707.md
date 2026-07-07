# 向量庫遷移計劃：pgvector → Qdrant（條件觸發式）

**日期**：2026-07-07
**性質**：規劃報告（憲章第六部計畫先行 #20）；決策層待用戶拍板
**定位**：**架構就緒的可選遷移**，非現在就要做的施工。誠實結論寫在最前面——不盲推 Qdrant。
**grounding**：本報告所有規模/延遲/耦合陳述皆出自 DB 實查 + code 實讀（末節 §8 附來源），非記憶或推估（#9/#15）。

---

## 0. 三十秒讀完：這份計劃的誠實立場

1. **現在不該做全量 cutover。** 48 萬向量在 pgvector 0.8.3 + HNSW 是舒適區（社群舒適區數百萬～千萬）。換 Qdrant 現階段是**解一個不存在的問題**。
2. **GPU 不是換的理由。** GPU 加速的是**嵌入生成（`embed_knowledge`）與 LLM 推論（Ollama）**，不是 ANN 搜尋。pgvector 與 Qdrant 社群版的 HNSW 搜尋主力**都是 CPU**。「未來有 GPU」與「換向量庫」是兩條正交的線。
3. **換庫的真成本不在 48 萬向量，在 RBAC/CLEAN 過濾 + 逐字回查對 pg 的深度耦合。** 搬向量只是搬索引；治權不變式（RBAC fail-closed、owned_local 隔離、逐字可溯源）留在 pg，跨庫後要**重新機械強制**，這才是風險所在。

**但計劃備妥**：若用戶基於未來規劃仍要推進，本報告給出**分階段、可回退、可拋棄式**的落地路徑，並把治權驗收關卡列為最高優先。**建議先執行的實質上只有「架構就緒」的階段 0–2（零行為風險），階段 3 cutover 列為量化門檻觸發**。

---

## 1. 誠實必要性裁決 + 可量化觸發門檻

### 1.1 現況規模（實查）

| 嵌入表 | 列數 | 維度 | 模型 | 索引 | PK 世代 |
|---|---:|---:|---|---|---|
| `knowledge_lexicon_embedding` | 154,875 | 384 | e5-small | HNSW | `(lex_id, model_tag)` 複合 |
| `knowledge_sentence_embedding` | 200,157 | 384 | e5-small | HNSW | `(sent_id, model_tag)` 複合 |
| `philosophy_chunk_embedding` | 126,609 | 384 | e5-small | HNSW | `chunk_id` 單欄（舊世代）|
| **合計** | **481,641** | | | | 三表 PK 世代不一致 |

> ⚠ **sentence 表在本次評估的 session 內從 198,048 漂到 200,157**（活躍寫入中）。這不是筆誤——它證明**嵌入是持續增量的**，是 §4.3 dual-store「新列可見延遲」風險的實證依據。

儲存合計約 1.6GB（sentence 701MB / lexicon 551MB / chunk 395MB，含 HNSW 索引），單機記憶體可整包放下。

### 1.2 延遲現況（實測，暖快取、單機、單併發、EXPLAIN ANALYZE，不含 client round-trip 與 encode）

- philosophy chunk 純 HNSW kNN：**~81–90ms**
- 含 4 表 JOIN（chunk/work/thinker/work_text）取 Citation：**~116–135ms**（JOIN 增量約 40–50ms）
- sentence（~20 萬）kNN：**~121–139ms**
- 冷快取首查：~537ms（HNSW warmup / page cache，屬非穩態）

對顧問對話而言，**LLM 生成（分鐘級）才是瓶頸**，向量檢索延遲可忽略。此規模**無延遲痛點**。

> 誠實邊界：上述為本機單併發估算，非生產 p95。真實 p95 須含 `SentenceTransformer.encode`（CPU 上每查數十 ms）+ 併發競爭，應以生產查詢集實測（#15 實測先於估算）。且 **`hnsw.ef_search` 從未刻意調校過**（實查 session 內為預設值），召回/延遲權衡還有便宜的優化空間（見 §7）。

### 1.3 GPU 到底改變什麼（不可對用戶隱瞞）

| 環節 | 吃 GPU？ | 說明 |
|---|---|---|
| **嵌入生成**（`embed_knowledge` 的 `model.encode`）| ✅ 是 | GPU 真正受益點；`embedspec.QUERY_DEVICE='cpu'` 已註明「批量嵌入另用 GPU」，裝置分離已預留 |
| **LLM 推論**（Ollama qwen3）| ✅ 是 | 與向量庫選型無關 |
| **ANN 搜尋**（pgvector HNSW / Qdrant HNSW）| ❌ 否 | HNSW 是 CPU 圖遍歷演算法 |
| Qdrant GPU 索引（較新版本）| ⚠ 僅建索引 | 加速 build、**不加速查詢**，且非社群版主賣點 |

**若換 Qdrant 的動機是「想用 GPU 加速檢索」＝誤解。** 正解是把 `embed_knowledge` 的批量嵌入搬 GPU（裝置分離已就緒），與向量庫選型正交。

### 1.4 裁決 + 量化觸發門檻

**裁決：現階段架構就緒即可，不 cutover。** 觸發全量 cutover（階段 3）須滿足**任一硬門檻**或**兩個軟訊號同時**：

**硬門檻（任一）**
- 單表向量數跨越約 **500 萬～1000 萬**（當前的 ~10–20 倍；哲學英文全嵌 + 十域全嵌堆疊後的合理上限區間）；
- 生產查詢 **p95 端到端 > 300–500ms** 且已窮盡 `ef_search`/HNSW 調參仍不達標；
- 單機 **RAM 裝不下 HNSW 圖**（索引已數十 GB）。

**軟訊號（需兩個同時）**
- RBAC/payload 過濾選擇性升高，導致 pgvector 過濾式 kNN 退化（filtered-HNSW 塌成暴力掃）；
- 需水平 sharding / 向量服務要與 pg OLTP 解耦獨立擴縮。

> 這些數字是依 pgvector 社群舒適區 + 本專案十域全嵌的合理外推，**非本機實測到的崩潰點**。真正的門檻應在接近時以本機硬體重新實證（#27 重覆驗證再定論），**不可當治權常數寫死**。

---

## 2. Qdrant vs pgvector 公平對照

| 維度 | pgvector 0.8.3（現況）| Qdrant | 現規模裁決 |
|---|---|---|---|
| **48 萬向量檢索** | HNSW，81–139ms 暖快取，綽綽有餘 | 同量級亦快 | **平手**，pgvector 已夠 |
| **千萬～億級規模** | HNSW build/記憶體/recall 吃緊 | quantization、on-disk、多 segment 成熟 | Qdrant 贏（門檻未到）|
| **RBAC/過濾＋kNN** | **filtered-HNSW 一句 SQL 內做完**（先 RBAC 過濾再 kNN 取 k）；`AND false` 天然 fail-closed | payload filter（等值封閉集），動態集合過濾難乾淨表達 | **pgvector 明顯贏**（見 §4.2）|
| **逐字回查 + JOIN 原文** | 一句 SQL 免費 JOIN 出 Citation 全欄 | 只能回 (pg_pk, distance)，須回 pg 二趟 | **pgvector 贏**（耦合利便）|
| **水平分散式 sharding** | 靠 pg 本身擴展，較重 | 原生 sharding/replication | Qdrant 贏（未觸發）|
| **維運（服務數）** | 0 個額外常駐（在 pg 內）| +1 常駐服務（監看/升級/資源）| pgvector 贏 |
| **備份** | 單一 `pg_dump -Fd -j4`（#30），一次全備、跨機獨立 | 需 Qdrant snapshot，或走可拋棄不備份 | pgvector 贏（見 §4.1）|
| **GPU 加速搜尋** | ❌（HNSW=CPU）| ❌（社群版 HNSW=CPU）| **平手，兩者都不吃 GPU** |

**結論**：Qdrant 真正贏的地方（規模/分散式/進階過濾/量化壓縮）門檻都**未觸發**；pgvector 現在贏在**耦合利便 + 零額外維運**。48 萬規模是 pgvector 兩全的甜蜜點。

---

## 3. 遷移架構（若啟動）

### 3.1 split 本質（命門紅線強制，非設計選擇）

```
        ┌────────────── Qdrant（可拋棄召回索引）──────────────┐
        │  只存：384-dim 向量 + 窄 payload（過濾用）           │
        │  只回：[(pg_pk, distance)]  ← 紅線③ 嵌入=索引非內容 │
        └───────────────────────┬─────────────────────────────┘
                                 │ pg_pk 清單
                                 ▼
        ┌──────────────────── PostgreSQL（SSOT / 真源）─────────┐
        │  逐字原文（philosophy_work_text / knowledge_item_text）│
        │  provenance（char_range / source_url / license）      │
        │  RBAC（clean_item_sql + resolve_allowed_domains）      │
        │  owned_local / local_private 的 DB CHECK              │
        │  verify_verbatim + guard 逐字回查                     │
        └───────────────────────────────────────────────────────┘
```

**這是「向量去 Qdrant、真兆/治權留 pg」的 split，不是把知識庫搬去 Qdrant。** 逐字回查、provenance、RBAC、owned_local DB CHECK **全部無法且不應搬進 Qdrant**——它們是 pg 關聯引擎的機制，且是 guard 命門（`guard.py:53` 引號≥8字須逐字 ∈ citation）+ 紅線③（嵌入=索引非內容）硬性要求。**pg 永不拔。**

### 3.2 遷移座位已存在（別重造）

`src/augur/knowledge/vectorindex.py` 已定義 **`VectorIndex` 五方法封閉介面**（`ensure_collection` / `upsert` / `delete` / `search` / `stats`），且已有一個 `MilvusLiteIndex` adapter + `scripts/export_milvus_index.py` 匯出器。標頭明寫「**換 Standalone/他牌＝另寫 adapter 換裝，pgvector 及以上零改動**」「search 只回 (pg_pk, distance)、內容永遠回 PG JOIN 取」「Milvus 隨時可 DROP 從 PG 全量重建（SOP-B）」。

→ **Qdrant 遷移正解 = 新增一個 `QdrantIndex(VectorIndex)` adapter**，走同一介面，`pgvector`/`embedspec`/`embed_knowledge` 零改動。

> ⚠ **但這個抽象只被 `export_milvus_index.py` 一支腳本用，live 讀路徑（`retrieval.py`）完全沒 import 它**（grep 實證：`retrieval.py` 4 處 `<=>` 全是裸 SQL、零 vectorindex import）。所以「加個 adapter」只解 search 的一半；真正的主工作是把 live 讀路徑從裸 SQL 改成走抽象——見 §5。

### 3.3 Collection schema + payload

- **3 collection 對 3 表**（lexicon / sentence-works / sentence-items，或沿用 `embedspec.collection_name(layer, side, model_tag, textnorm_ver)` 世代命名），**不用單 collection + type payload**（維持與現有 export 一致、對帳邊界清晰）。
- **collection 名一律出自 `embedspec.collection_name`（禁手寫）**，model_slug + textnorm_ver 世代入名；換模型＝新 collection、舊不覆蓋（SOP-A/P6）。
- 每 point：`id = pg_pk`（`sent_id`/`lex_id`/`chunk_id`）、`vector = 384-dim`、`payload = {粗過濾欄}`。
- **維度 assert**：遷移腳本須 `assert dim == 384`（`vectorindex._assert_dim` 已有此紀律，Qdrant 版照做）。

**payload 欄設計（關鍵決策，見 §4.2）**：現行 `PAYLOAD_FIELDS = (domain, entity_type, taxonomy_id, language)` **缺 `access_scope`、`owner_user_id`、`license`、`review_flag`、`corpus_class`**。這是一個**刻意的最小化**——payload 只承載「**粗過濾**」欄（language / entity_type），**精確 RBAC 與 fail-closed 一律回 pg 兜死**（§4.2 推薦路 A）。

### 3.4 寫入路徑

- **不改 `embed_knowledge`**（維持 pg 為寫入真源，`model.encode` 寫 pg embedding 表）。
- Qdrant 由 **`export_qdrant_index.py`（照抄 `export_milvus_index.py` 對帳骨架）游標增量同步**：pg 寫完 → export 追。
- 對帳沿用 `export_milvus_index.py` 的**雙向 anti-join**（missing 補 / orphan 刪 / `synced == source` 斷言 / coverage_metric 落庫）。

### 3.5 讀取路徑（cutover 時，唯一有行為風險的一步）

在 `retrieval.py` 的 ANN leg 加 backend 開關（`.env` `AUGUR_ANN_BACKEND=pgvector|qdrant`）：
1. `QdrantIndex.search(qv, k', filters={language, entity_type})` → 得 `[(pg_pk, dist)]`（k' = over-fetch 後的 k，見 §4.2）
2. 取 pg_pk 清單 → 用**現有的 PG JOIN + `clean_item_sql` RBAC WHERE** 回原文並**精確 RBAC 收窄**
3. `verify_verbatim` / `guard` 逐字回查（**pg JOIN 那步絕不可省**，省了＝guard 無原文可驗＝破 #1 命門）

`lexicon_lookup` / `concordance_lookup`（純 exact SQL、不碰向量）不動。

### 3.6 批次遷移 schema + Python 程式（#29 慣例：資料驅動、冪等、resume-safe、#25 可測）

**是，可批次移轉的 schema + 程式較佳**（優於一次性手工搬）——理由：①嵌入持續增量寫入（sentence 表本 session 就 198k→200k）→ 須游標續跑追；②冪等可續 = cutover/rollback 安全；③**CLEAN 過濾寫進程式 = 治權保護機械強制**（非人工記得）；④#25 可測 = 放量前驗私有零外洩。組成三件：

**(a) pg 側 sync 狀態表（resume 帳本，#6/#22）** — `migrate_qdrant_sync_ddl.py`（#29a bootstrap/指令矩陣/冪等）：
```sql
CREATE TABLE IF NOT EXISTS qdrant_sync_state (
  collection  varchar(64) PRIMARY KEY,          -- embedspec.collection_name 世代名（禁手寫）
  last_pk     bigint      NOT NULL DEFAULT 0,    -- 已同步之最大 pg_pk（游標）
  n_synced    bigint      NOT NULL DEFAULT 0,
  n_source_clean bigint,                         -- 對帳:CLEAN 過濾後之來源合規列數
  updated_at  timestamptz NOT NULL DEFAULT now()
);
```

**(b) 批次 export 引擎** — `export_qdrant_index.py`（照抄 `export_milvus_index.py` 對帳骨架，**但 SELECT 補 CLEAN**）：
- 🔴 **命門：CLEAN-filtered SELECT**（現有 milvus exporter items SELECT 零過濾＝洩漏；批次程式 SELECT 必須 JOIN CLEAN 條件）：
  - `license ∈ 白名單`（public_domain/cc-by/cc-by-sa/cc0）· `review_flag = false`（過稽核）· `source_type <> 'ai_generated'` · **`access_scope <> 'local_private'`**（私有一律不入共享 collection；若要索引私有須另建 owner-scoped collection + Qdrant 端 owner payload 過濾）。
- 游標驅動：`WHERE pg_pk > last_pk AND <CLEAN> ORDER BY pg_pk LIMIT batch` → Qdrant upsert（`id=pg_pk`、`payload={粗過濾欄:language,entity_type}`，**RBAC 精確欄不入 payload**，§4.2）→ 更新 `last_pk`。冪等（upsert）、可續（游標）、殺掉重跑不重複。
- `assert dim == 384`（`vectorindex._assert_dim` 紀律）；雙向 anti-join 對帳（missing 補 / orphan 刪 / **`synced == n_source_clean` 斷言**、非 == 全表）。

**(c) 指令矩陣**：
```
python scripts/migrate_qdrant_sync_ddl.py                     # 建 sync 帳本（冪等）
python scripts/export_qdrant_index.py --collection X --smoke  # #25 最小單位（單 collection 單 batch）
python scripts/export_qdrant_index.py --all --resume          # 放量續跑（游標帳本驅動）
python scripts/export_qdrant_index.py --reconcile             # 對帳 anti-join + coverage 落庫
```

**驗收（#25 放量前必過）**：smoke 批出來的 Qdrant collection 逐點回查 pg，確認 **零 local_private / 零 review_flag=true / 零非白名單 license** 外洩（CLEAN 過濾機械證實），且 `count == n_source_clean`。

---

## 4. 治權/維運衝擊 + 不變式重強制

### 4.1 #30 備份 — 裁決：Qdrant 走可拋棄（SOP-B），不進備份鏈

現況 pg 一庫 `pg_dump -Fd -j4` 即含全部向量 + 原文 + RBAC，單一 restore 即一致。

搬 Qdrant 後有兩條路，**明確裁決走 (B)**：

- **(A) 雙庫時點一致快照**：pg_dump + Qdrant snapshot 須時點對齊，否則向量 pg_pk 對不上 pg 原文列 = orphan/幽靈引用。運維面變重，且踩 #30 已記的 snapshot 時點陷阱同類。
- **(B) ✅ 推薦：Qdrant 純可拋棄索引，不進 #30 備份鏈。** `vectorindex.py` 標頭已表態 SOP-B「Milvus 隨時可 DROP 從 PG 全量重建」＝**治權已裁走可拋棄路線**。跨機遷移只帶 pg dump，Qdrant 在新機從 pg **re-export 重建**（不進 git，承「DB 跨機獨立不進 git」）。

> **走 (B) 則「雙庫時點對齊風險」根本不存在**——這是三個視角在兩個緩解間搖擺、但實則已被治權裁決消解的點。**代價**：換機後有一段 Qdrant 重建時間窗（48 萬向量 re-export，估分鐘級 IO-bound）。`#30` 的「dump 期間禁 DDL 鎖風暴」教訓不變；Qdrant 為獨立進程無此鎖佇列問題。

### 4.2 RBAC scope → payload filter — 最大暗礁

**pg 側 RBAC 是動態參數化 SQL**（`corpus.clean_item_sql` 產 `license × entity_type × access_scope × domain=ANY(allowed_domains) × owner_user_id` 的 WHERE frag，fail-closed：非 super 無授權 → `AND false`；`local_private` 無 owner → `AND false`）。

**Qdrant payload filter 是等值封閉集**（`_filter_expr` 只支援 `field == value`），**無法表達 `domain = ANY([...])` per-user 動態集合，也無 `AND false` 那種「空集合恆真拒絕」的直觀語意**。

**兩條合規路，明確推薦 (A)**：

- **(A) ✅ Qdrant 只做粗過濾（language/entity_type）→ over-fetch 撈超額候選 → 回 pg JOIN 時用 `clean_item_sql` 做精確 RBAC 收窄。** 安全永遠由 pg 的 WHERE 兜死，寧可多撈也不漏過濾。與現有 fail-closed 一致，owner_user_id/local_private 全留 pg。
- **(B) Qdrant 用 `MatchAny` filter 帶 allowed_domains**（qdrant-client 支援）但 owner_user_id/local_private 仍須 pg 兜底 → **不推薦把安全下放向量庫**。

**over-fetch 是 (A) 的真工程難題（四視角低估、對抗審查點出）**：pgvector 的 filtered-HNSW 是「在滿足 RBAC 的子圖上找最近鄰」；Qdrant 粗召回 + pg post-filter 是「先找全域最近鄰、再事後濾掉不合規」。
- **正確性風險**：某 user 的 `allowed_domains` 極窄（41 個 domain 中只授權 1–2 個），Qdrant top-k 可能**全數被 pg RBAC 濾光** → 需 k 的數十倍 over-fetch 才湊得到 k 筆合規結果，且**無法先驗知道要 over-fetch 多少**（選擇性 per-user 動態）。
- **召回品質風險**：若合規子集在向量空間分佈稀疏，Qdrant 的 top-N 可能「最近的都不合規、合規的排在 N+1 之後被截斷」＝**召回品質比 pgvector 差**，不只是延遲問題。
- **兩難**：安全（pg post-filter）↔ 召回品質（Qdrant filter 融入圖遍歷但要把 RBAC 欄 payload 化 = 回到「RBAC 下放向量庫」暗礁）。→ 現規模下 pgvector filtered-HNSW 兩全，是**不換的又一實質理由**。

**fail-closed 方向不可寫反**：Qdrant filter 若寫成「白名單為空 = 不加 filter = 全放行」＝從 fail-closed 翻成 **fail-open 靜默洩漏**，且比 pg 難靜態證明。

### 4.3 逐字回查 cross-store + 新列可見延遲

- **逐字回查必然 cross-store JOIN、pg 拔不掉**：`verify_verbatim`(`retrieval.py:110`)/`verify_verbatim_item`(`:346`) 拿 pg_pk 回 pg 原文表做子字串比對；`guard.py` 全套在 Python 層對 `citation.text` 比對。遷移後 = 「Qdrant 撈 id → pg 補 JOIN 原文 + RBAC 欄 + verbatim 驗證」兩段式，延遲多一次 round-trip。
- **⚠ 新列可見延遲（對抗審查揪出、比 payload staleness 更嚴重）**：sentence 表活躍寫入（本 session 內 +2,109 列）。dual-store 過渡期 pg 一直長、Qdrant 靠游標 export 追，**永遠有追趕窗口**。若 cutover 後讀 Qdrant，**新嵌入的句子在 export 追上前對 Qdrant 不可見 = 靜默漏檢（全列缺席，非 payload 陳舊）**。緩解：cutover 前確認寫入已收斂 / export 游標延遲有上界監控 / 或維持 pgvector 讀路徑直到寫入穩定。

### 4.4 payload staleness（Qdrant 模式獨有的新正確性風險）

pgvector 靠 live JOIN：`review_flag`（歸屬稽核事後改）、`domain`（可重策展）、`license` 一改，下次查詢立即反映。搬 payload 進 Qdrant 後這些變成**嵌入當下的快照**。歷史上 attribution audit 曾事後級聯清理 chunks（memory 載）——**稽核把某 work `review_flag` 設 true 後，Qdrant payload 仍是舊值 → 該內容仍被檢索到（繞過 CLEAN 閘）＝靜默洩漏**。緩解：走 **SOP-B（重建而非增量改 payload）**——稽核/重策展後從 pg 全量 re-export，避免陳舊。這也是選推薦路 A（RBAC 留 pg、payload 只放粗過濾靜態欄）能大幅降低此風險的原因。

### 4.5 clean-room / 預測隔離不變式（不受影響，但需納入測試）

`import_isolation.FORBIDDEN = (augur.philosophy, augur.advisor, augur.knowledge)`。`QdrantIndex` adapter 住 `augur.knowledge`、`qdrant-client` 只被 knowledge/advisor import，**不碰 features/models/universe/evaluation/ingestion**，隔離不破。**遷移須把新模組納入 `import_isolation` 禁 import 名單**、維持 `test_philosophy_isolation` 邊界。

---

## 5. 碼觸點 + 抽象層建議 + 工作量/風險

### 5.1 精確碼觸點

| 元件 | 檔案:行 | 遷移動作 | 難度 |
|---|---|---|---|
| `VectorIndex` 五方法介面 | `vectorindex.py:27` | 沿用，不動 | — |
| **新增 `QdrantIndex(VectorIndex)`** | `vectorindex.py`（新 class）| 對照 `MilvusLiteIndex` 實作五方法；`_filter_expr` 改 qdrant `models.Filter` | **低**（機械照抄）|
| **`export_qdrant_index.py`** | 新（抄 `export_milvus_index.py`）| 換 adapter 實例化，對帳骨架一字不改 | **低** ⚠見下 |
| **`PAYLOAD_FIELDS` 擴充決策** | `vectorindex.py:14` | 走推薦路 A：**只加 language/entity_type 粗過濾，RBAC 欄不進 payload** | **中**（安全決策）|
| **`retrieve` works 側 ANN** | `retrieval.py:77,84` | 把 `<=>` 裸 SQL 換成 `QdrantIndex.search()` → pg_pk → PG JOIN | **中高** |
| **`retrieve_items` items 側 ANN** | `retrieval.py:310,314` | 同上 + **exact-then-ANN 混合合併保序/去重**（見下）| **高** |
| `verify_verbatim` / `guard` | `retrieval.py:110,346` / `guard.py` | **不動**（只吃 pg_pk 回 pg）| — |
| `lexicon_lookup` / `concordance_lookup` | `retrieval.py:190` | **不動**（純 exact SQL）| — |
| import 隔離測試 | `import_isolation.py:33` / `test_philosophy_isolation` | 新模組納 FORBIDDEN | 低 |

### 5.2 🔴 命門警示：現有 Milvus 匯出器已經漏 RBAC（code 實證，非理論）

`export_milvus_index.py` 的 items 側 `_SELECT` 實碼：

```sql
SELECT e.sent_id, e.embedding::text, i.domain, i.entity_type, COALESCE(i.taxonomy_id,0), s.language
  FROM knowledge_sentence_embedding e JOIN knowledge_sentence s USING (sent_id)
  JOIN knowledge_item_text x ON x.itext_id = s.itext_id
  JOIN knowledge_item i ON i.item_id = x.item_id
 WHERE s.itext_id IS NOT NULL AND s.language = %s AND e.model_tag = %s
```

**它 JOIN 了 item_text/item 卻完全沒有 `clean_item_sql`、沒有 license 白名單、沒有 access_scope 過濾、沒有 review_flag 稽核閘**——會把 **local_private 私有句向量、未稽核（review_flag=true）、非白名單 license 的句子全部無差別匯出到外部索引**。

> **這正是 §3.2 建議「照抄 `export_milvus_index.py`、對帳骨架一字不改」的陷阱**：若有人把這支當 Qdrant 遷移範本直接改 adapter，就**複製這個洩漏**。**遷移前，export 腳本的 items SELECT 必須先補齊 CLEAN/RBAC 過濾**（`WHERE ... AND (license IN 白名單) AND (review_flag=false) AND (access_scope='public')` 或明確標記 local_private 帶 owner），否則 owned_local/local_private DB CHECK 的治權保護**在向量離開 pg 那刻就失效**。這是計劃裡最該用紅字標的命門。

### 5.3 items 側 exact-then-ANN 混合合併（對抗審查揪出的具體缺口）

`retrieve_items` 先 `knowledge_concordance` exact SQL 計數取 `out`，再算 `need = k - len(out)`，ANN 段用 `sent_id != ALL(seen)` 去重補位。**跨庫後**：
- exact 段的 `seen` 清單要餵給 Qdrant search 當**排除條件**，但 `_filter_expr` 只支援等值、**無法表達 `sent_id NOT IN (seen)`**。
- 兩條落地：(i) Qdrant 端加 `must_not` 條件（payload 需帶 sent_id、且 seen 清單可能很長）；(ii) **over-fetch 後在 pg 端 dedup**（推薦，與路 A 一致）。
- 保序：exact 段在 pg、ANN 段在 Qdrant，跨庫合併 + dedup + 保序邏輯要在應用層重寫，比 works 側單純 kNN 複雜。

### 5.4 新依賴 / 服務 / config（目前全零）

- 依賴：`qdrant-client`（現況 requirements 無 qdrant-client、無 pymilvus client、無 pgvector client；向量全走 psql `<=>`）
- 服務：Qdrant server（Docker `qdrant/qdrant`，REST 6333 / gRPC 6334，掛 volume）＝**第一個非 pg 的常駐狀態存儲**
- config：`.env` 加 `QDRANT_URL` / `QDRANT_API_KEY`（不進 git，承 .env 治權；現有 .env 無任何向量庫 key）
- import smoke test（#23）先過才進後續

### 5.5 工作量本質

**碼面小、安全語意面重**：核心就 `retrieval.py` 兩函式 + 一新 adapter + 一遷移腳本。機械易的部分（adapter、export 骨架、依賴/Docker/.env）照抄即可；**難的是「翻譯 RBAC fail-closed 到跨庫、且錯了會靜默污染下游」——不是量的問題，是對錯的問題**。

---

## 6. 分階段落地（每階段附驗收）

> **明確建議：現在只做階段 0–2（零行為風險，讓架構就緒當 GPU 預備件）；階段 3 cutover 列 §1.4 門檻觸發才做。**

### 階段 0 — 前置（零風險）
- 新增 `qdrant-client`；Docker 起 Qdrant（persist volume）；`.env` 加 `QDRANT_URL`/`QDRANT_API_KEY`。
- **驗收**：import smoke test 過；Qdrant health check 通。

### 階段 1 — 新增 adapter（clean-room、對照介面）
- 在 `vectorindex.py` 新增 `QdrantIndex(VectorIndex)`，五方法對照 `MilvusLiteIndex`：`ensure_collection`→`create_collection(size=384, distance=Cosine)`；`upsert`→`PointStruct(id=pg_pk, vector, payload)`；`search`→回 `[(pg_pk, distance)]` **只此（紅線③）**；`stats`→count + 枚舉 pg_pk 自驗（`len == count`）。
- collection 名沿用 `embedspec.collection_name`（禁手寫）；assert dim==384。
- 納入 `import_isolation` FORBIDDEN 測試。
- **驗收**：`test_philosophy_isolation` 綠；adapter 五方法單元測試通；`search` 只回 (pg_pk, distance) 不回內容。

### 階段 2 — 匯出器 + dual-store 影子（pg 仍真源、讀路徑仍走 pgvector）
- 抄 `export_milvus_index.py` → `export_qdrant_index.py`，**🔴 先補 items SELECT 的 CLEAN/RBAC 過濾**（§5.2），再換 adapter，對帳/游標/斷言其餘照抄。
- bulk export 48 萬向量到 Qdrant（IO-bound，估分鐘級；GPU 無用）。
- **驗收**：
  - 雙向 anti-join `synced == source`（missing=0, orphan=0）；
  - Qdrant vs pgvector 對同一批 query 的 top-k pg_pk **重合率**（recall sanity）；
  - **RBAC 過濾正確性離線驗證**：export 出的 items 不含 local_private/未稽核/非白名單 license 句向量（對照 pg 全集 anti-join）。

### 階段 3 — cutover 讀路徑（唯一有行為風險，僅門檻觸發才做）
- `retrieval.py` ANN leg 加 `AUGUR_ANN_BACKEND` 開關；qdrant 分支 = `QdrantIndex.search()`（粗過濾）→ over-fetch → pg_pk → **現有 PG JOIN + `clean_item_sql` RBAC** 回原文（RBAC/verbatim/guard 全不動）。
- items 側處理 exact-then-ANN 合併保序/dedup（§5.3）。
- 先**影子比對**（同 query 兩後端最終 citation + guard verdict 一致）再切主。
- **驗收（治權最高優先關卡，不可妥協）**：
  1. **kNN 結果一致**：兩後端 top-k pg_pk 重合率達標；
  2. **RBAC 不漏**：新增跨-store 隔離測試（等價 `test_philosophy_isolation`）——local_private 私有向量不被跨用戶檢索到、空授權必 deny、DB/store 錯誤 fail-closed、review_flag=true 應被擋；**over-fetch 後仍夠 k**；
  3. **逐字回查對**：`verify_verbatim` / guard verdict 兩後端一致，pg JOIN 取原文那步存在（未被省）；
  4. **備份可還原**：走 SOP-B，DROP Qdrant collection → 從 pg re-export 重建 → 結果一致。

### rollback（全程可回退）
任一階段退回 = `.env` 切回 `pgvector` 即恢復（pg HNSW 索引**全程保留、從未 DROP**）。Qdrant 出事直接 DROP collection、讀路徑退 pgvector，**零資料損失**（Qdrant 是可拋棄索引、真源在 pg）。

---

## 7. 不做什麼 / 更高槓桿的前置（誠實 timing）

**在啟動任何 Qdrant 工作之前，兩個更高槓桿的事該先做**：

1. **先調 pgvector 便宜旋鈕（成本低几個數量級）**：實查 `hnsw.ef_search` 從未刻意設定（用預設）。換庫前應：`SET hnsw.ef_search`（調高換召回、調低換延遲）、評估 `m`/`ef_construction`、必要時 partial index；並用**生產查詢集實測 p50/p95/p99 端到端延遲**（含 encode + kNN + JOIN）。**多數延遲需求這一步就消化掉**。不能拿未調過的 pgvector 去對比調好的 Qdrant（不公平比較）。

2. **GPU 到位後：先升嵌入模型，而非換向量庫**：三表全 e5-small 384-dim。GPU 最高槓桿是**用 GPU 批量重嵌到更大/更強模型**（如 e5-large 1024-dim / bge-m3），對**跨語檢索品質**的提升遠大於換庫。`embedspec` 的 `MODEL_DIMS` 登記 + `collection_name` 世代命名**已為換模型設計**（SOP-A：新 tag+dim=新表世代、舊不覆蓋），純在 pg 內完成、零架構風險。

**別把「換向量庫」與「升嵌入模型」綁一起**——前者解規模（門檻未到）、後者解檢索品質（跨語弱是現況痛點，見 memory 載「e5-small 跨語崩壞」）。若 GPU 預算有限，**升模型優先於換庫**。

**唯一該提前做的準備**：把 `retrieval.py` 熱路徑接進既有 `VectorIndex` 抽象（先用 pgvector 當第二後端驗證 two-phase 讀路正確，零外部依賴）。**注意這本身就是階段 3 cutour 的大部分工作量**——它把 split 的核心難題（over-fetch / RBAC post-filter）提前暴露，這是好事：可在零外部依賴下先驗證正確性、改善可測性、且不綁定任何特定外部庫。

---

## 8. 決策層 vs 執行層 + grounding

**決策層（人拍板）**：是否啟動遷移（現階段建議否）、是否改 #30 備份慣例（建議走 SOP-B 則不需改）、是否投 GPU 於升模型 vs 換庫。

**執行層（護欄內 AI 可主動）**：先調 pgvector `ef_search` 旋鈕、實測基準延遲、（若拍板）做階段 0 adapter POC。這些 clean-room、可逆、無外部副作用。

### grounding（實查/實讀來源，2026-07-07）

- **pgvector 0.8.3**；三表 rows：lexicon 154,875 / sentence **200,157**（session 內從 198,048 漂升，活躍寫入實證）/ chunk 126,609 = **481,641**；三表 HNSW 索引在位。
- **delay 實測**（EXPLAIN ANALYZE 暖快取）：chunk 純 kNN 81–90ms / +4表JOIN 116–135ms / sentence 121–139ms / 冷首查 537ms。
- `vectorindex.py`：`VectorIndex` 五方法介面（:27）；`PAYLOAD_FIELDS=(domain,entity_type,taxonomy_id,language)`（:14，**缺 access_scope/owner_user_id/license/review_flag/corpus_class**）；`MilvusLiteIndex` adapter；標頭 SOP-B「隨時 DROP 從 PG 重建」。
- `retrieval.py`：4 處 `<=>` 裸 SQL（:77,84 works / :310,314 items），**grep 確認零 import vectorindex**；`verify_verbatim`(:110)/`verify_verbatim_item`(:346) 從 pg 原文表逐字回查；`concordance_lookup`(:193) docstring 自註「不過 clean_item_sql 收窄、接入讀路必先加」（遷移期高風險回歸點）。
- `corpus.clean_item_sql`（:38–69）：`local_private` 無 owner→`AND false`；`public` 空授權→`AND false`（fail-closed）。`access.resolve_allowed_domains` 任何異常→`(False, ∅)`。
- 🔴 `export_milvus_index.py` items `_SELECT`（:37–52）：JOIN item_text/item 取 domain/entity_type，**無 clean_item_sql / license / access_scope / review_flag 過濾**＝現存洩漏面（實碼證實）。
- `guard.py`（:53）引號≥8字須逐字 ∈ citation；出處閘（:30）補裸出處。
- `import_isolation.FORBIDDEN=(augur.philosophy, augur.advisor, augur.knowledge)`（:33）。
- `embedspec`：`MODEL_TAG=intfloat/multilingual-e5-small`、`MODEL_DIMS={...:384}`、`QUERY_DEVICE='cpu'`（:18，註「批量嵌入另用 GPU」）、`collection_name(layer,side,model_tag,textnorm_ver)` 世代入名禁手寫。
- 41 個 distinct item domain（RBAC 收窄軸基數）；依賴實查：無 qdrant-client / 無 pymilvus / 無 pgvector client；.env 無任何向量庫 key。

### 誠實邊界（#7）
本報告全為**靜態讀碼 + DB 實查**，**未實跑遷移、未起 Qdrant、未實測 filter 等價**。qdrant-client 的 `MatchAny`/`Filter` 能否乾淨表達 `domain=ANY([...])` 動態集合 + owner 收窄 + fail-closed（空授權=零結果），須真啟動時以最小單位（#25）實測驗證——現階段是**待驗證假設，不可當已知事實**。延遲數字為本機單併發估算，非生產 p95。

# 知識入庫統一管線：主題抓取／本機匯入／SFTP → LSR → KH4／admit → 銜接 KH10 [I]（2026-07-30）

* **性質**：[I] plan-first 計畫書（CLAUDE #16／#20；憲章第六部計畫完整性）
* **檔名沿用**：`reports/augur_long_sentence_resplit_embed_kh10_bridge_plan_20260730.md`（升格為**入庫總規**；原 LSR 補洞為本規 Phase A）
* **觸發**：
  1. Steward——長句重切＋再嵌→KH10 橋接  
  2. Steward——「修改為可直接應用到 augur 後台：主題抓取、本機匯入、遠端 SFTP，**所有取得資料都須經此規畫進入系統**」
* **正交**：FZ-keep（零 FinMind／FRED）；predict⊥API；不降 KH4／CLEAN／junk 閘；KH10 HUMAN_ONLY
* **治權錨**：原則精華 #1／#15；CLAUDE #29／#29b；十層母計畫；既有 e2e `refresh_knowledge_pipeline.py`

### Steward 拍板欄

| 欄 | 內容 |
|---|---|
| **日期** | 2026-07-30 |
| **狀態（已執行）** | ✅ `LSRS-PLAN`＋`LSRS-S01`＋`LSRS-S23`＋`FZ-keep`（庫內歷史長句補洞 CLOSED） |
| **狀態（本版升格）** | ✅ **`LSR-INGRESS-PLAN`＋`S0`＋`S1`＋`FZ-keep`**（2026-07-30；`audits/LSR-INGRESS-PLAN-S01-APPROVED-20260730.md`／`LSR-INGRESS-S01-CLOSED-20260730.md`） |
| **待拍** | —（S2 已 CLOSED；KH10-ENABLE 另碼） |
| **效力** | 總規＋S0／S1／S2 已落地；三通道／後台預設走 KIP（`--no-kip`／`--acquire-only` 例外） |

---

## 0. 一句結論

**凡經 augur 後台或 CLI 進入知識層的資料——主題抓取（harvest）、本機匯入（local_files）、遠端 SFTP——一律走同一條「准入→切句（含長句硬切）→嵌入→KH4→auto_admit≤9」強制管線；可答＝KH4 eligible；KH10 進化另碼人裁，永不因入庫自動 APPLY。**

---

## 1. What / Why / Non-goals

### 1.1 What（本版升格後）

| 層 | 內容 |
|---|---|
| **A. 歷史補洞（已 CLOSED）** | 庫內超長 en 句重切→再嵌→KH4→admit（S01／S23） |
| **B. 強制入庫規（本版主體）** | 三通道新進資料**不得**只停在 `knowledge_item`／qualification；必須編排跑完 §2 終態 |
| **C. 後台可操作** | admin console 觸發之 harvest／本機／SFTP job，預設串同一 DAG（或 job 完成後自動 enqueue） |
| **D. 銜接 KH10** | admit≤9 之後；進化候選／人裁另碼 `KH10-ENABLE-S1+` |

### 1.2 適用通道（強制集合）

| 通道 | 入口（現況） | adapter／job |
|---|---|---|
| **主題抓取** | `harvest_knowledge.py`／後台 harvest；下游 `promote`／全文 | OpenAlex 等 topic 源 |
| **本機匯入** | `acquire_local_files.py`／後台本機選夾 | `local_files`；`knowledge_import_job` |
| **遠端 SFTP** | `acquire_remote_files.py`／後台 SFTP | `adapter='sftp'` |

**判準**：只要結果落入 `knowledge_item`＋（可有）`knowledge_item_text`，即屬本規強制範圍。  
**不含**：FinMind／FRED 市場 raw（FZ-keep；≠知識入庫通道）。

### 1.3 Why

- 使用者要「後台抓／匯進來就能問」——須材料可嵌＋KH4 eligible，不是只 `ingest_status=inserted`
- 三通道若各走半截（只入庫、不切句／不嵌／不抬 KH），會重現 ERP／長句／provisional 假可答
- 已有 `refresh_knowledge_pipeline.py`（harvest→…→embed→vector_export）與 local 的 `[kh_progressive]` 鉤子——**缺的是：統一強制、含 LSR 硬切、三通道對稱、後台預設不可跳過**

### 1.4 Non-goals

| 不做 | 理由 |
|---|---|
| 關 junk／無限長句硬灌向量 | #15 檢索污染 |
| 非語意 entity 假抬 eligible | KH4 已定 |
| zip／無正文 skip 假裝已嵌 | 誠實缺料 |
| 入庫＝自動 KH10／PME APPLY | HUMAN_ONLY |
| 解凍市場 API | FZ-keep |
| 哲學 works 側強制同速（可選） | 顧問熱路徑＝items；works＝可選段 |

---

## 2. 強制入庫管線（SSOT 段序）

> **名**：Knowledge Ingress Pipeline（KIP）＝本規強制 DAG。  
> **終態定義（可檢索／可答）**：有正文（license 允許）→有句（`max_chars≤800`）→有嵌（CLEAN）→`knowledge_kh4_state.answer_status='eligible'`（語意型）→`admit_depth` 盡力抬至 `max_auto_depth`（現 9）。  
> **半終態誠實標**：`provisional`／`ineligible`／`skipped` 必須可在後台／qualification 看見，**不得**標成「已可答」。

```
[通道取得]
  harvest_knowledge / acquire_local_files / acquire_remote_files
       ↓ 幂等寫 knowledge_item(+text)／import_qualification
[KIP-1] build_sentences --scope items --max-chars 800
       ↓ 若仍有 len>800（舊段／競態）
[KIP-2] resplit_long_sentences --apply --side items --max-chars 800
       ↓ （僅處理本批 parent／或全庫 gap）
[KIP-3] embed_knowledge --layer sentence --scope items --gap-fill（zh+en）
[KIP-4] export_qdrant_index --side items --url <server>（公開 CLEAN；private 可只留 pgvector）
[KIP-5] kh4.refresh（本批 item_ids）
[KIP-6] run_knowhow_auto_admit --apply-up-to 9（本批 item-id 或 until-empty 有界）
[KIP-7]（可選／另碼）KH10 collect —— 不自動 decision
```

### 2.1 與既有驅動器對齊

| 既有 | 本規要求 |
|---|---|
| `refresh_knowledge_pipeline.py` STAGES | **加段／改段**：`sentences` 必須帶 `--max-chars 800`；在 `sentences` 後插入 **`resplit`**；`embed` 後接 **`kh4_refresh`**＋**`admit`**（或合併為 `kip_finalize`） |
| `acquire_local_files.py` 末段 `[kh_progressive]` | **保留**；其前必須保證本批已切句＋嵌＋KH4（或改呼叫統一 `run_kip_for_items`） |
| `acquire_remote_files.py` | 完成後**不得**只印「建議接下游」——須預設 enqueue／呼叫同一 KIP（可 `--kip`／`--no-kip` 明示跳過＝例外） |
| 後台 harvest job | 成功收束條件＝KIP 終態或誠實半終態列帳，不是「harvest metadata 完」 |

### 2.2 設計定錨（沿用＋擴充）

| ID | 定錨 |
|---|---|
| **D1–D7** | 見原 LSR（junk 不放寬；MAX=800；確定性硬切；items 優先；ledger；不假抬；路徑→admit≤9） |
| **D8** | **三通道對稱**：local／sftp／harvest 新進 items **同一 KIP**；禁止「本機有 KH、SFTP 沒有」 |
| **D9** | **後台預設開啟 KIP**；跳過須 admin 明示旗標＋audit 留痕 |
| **D10** | 批次可非同步（job queue／nohup），但 **job 狀態機**須有 `kip_pending`／`kip_running`／`kip_done`／`kip_partial` |
| **D11** | private／`local_private`：pgvector 必嵌；Qdrant 外部匯出仍受 access_scope 擋（憲章）——顧問私模可讀庫內 |

---

## 3. Schema

### 3.1 既有（消費）

| 表 | 角色 |
|---|---|
| `knowledge_source`／`knowledge_item`／`knowledge_item_text` | 源與正文 |
| `knowledge_import_job`／`knowledge_import_qualification` | 本機／SFTP 檔案級帳 |
| `knowledge_sentence`／`*_embedding`／`knowledge_embed_ledger` | 句與向量 |
| `knowledge_sentence_resplit_ledger` | LSR 重切帳（**已建**，S0 CLOSED） |
| `knowledge_kh4_state` | 作答門 |
| `knowhow_auto_admit_state` | 精準水印 |
| `knowledge_pipeline_heartbeat` 等（若有） | 驅動器心跳 |

### 3.2 建議新表：`knowledge_ingress_kip_run`（入庫管線帳本）

```sql
CREATE TABLE IF NOT EXISTS knowledge_ingress_kip_run (
    kip_run_id     BIGSERIAL PRIMARY KEY,
    channel        TEXT NOT NULL
                   CHECK (channel IN ('topic_harvest','local_files','sftp','manual_cli','backfill')),
    trigger_ref    TEXT,                 -- job_id / harvest log / source_key
    item_ids       BIGINT[] NOT NULL DEFAULT '{}',
    status         TEXT NOT NULL DEFAULT 'pending'
                   CHECK (status IN (
                     'pending','running','done','partial','failed','skipped_explicit')),
    stages_json    JSONB NOT NULL DEFAULT '{}'::jsonb,  -- 每段 started/finished/counts
    error_text     TEXT,
    actor          TEXT NOT NULL DEFAULT 'system',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at    TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_kip_run_channel_time
  ON knowledge_ingress_kip_run (channel, created_at DESC);
COMMENT ON TABLE knowledge_ingress_kip_run IS
  'KIP: 三通道入庫強制管線跑批帳（#15；非答案 SSOT／非預測）';
```

（`knowledge_*` 前綴已在 predict FORBIDDEN。）

---

## 4. Python／後台規畫

### 4.1 核心（建議新增）

| 檔 | 角色 |
|---|---|
| **新** `src/augur/knowledge/ingress_kip.py` | `run_kip_for_items(item_ids, *, channel, trigger_ref)`；段序 D8；寫 `kip_run` |
| **新** `scripts/run_knowledge_ingress_kip.py` | CLI：`--item-ids`／`--job-id`／`--source-key`／`--channel`／`--apply`／`--selftest` |
| **新** `scripts/migrate_knowledge_ingress_kip_ddl.py` | kip_run DDL |

### 4.2 既有（改接線）

| 檔 | 改動要点 |
|---|---|
| `refresh_knowledge_pipeline.py` | STAGES 插入 `resplit`；`sentences` 加 `--max-chars 800`；末段加 `kh4`＋`admit` 或呼叫 `ingress_kip` |
| `acquire_local_files.py` | 成功 inserted 後：預設 `run_kip_for_items`（可把現有 progressive 收進 KIP-6） |
| `acquire_remote_files.py` | 同步：預設 KIP；`--no-kip` 須明示 |
| `harvest_knowledge.py`／promote 鏈 | promote／fulltext 成功後 enqueue KIP（或由 refresh DAG 覆蓋） |
| `serve_admin_console.py` | 後台「主題抓取／本機／SFTP」完成頁：顯示 KIP 狀態；預設勾選「跑入庫管線」；禁止靜默跳過 |

### 4.3 已落地（Phase A·勿重做）

| 檔 | 狀態 |
|---|---|
| `migrate_sentence_resplit_ddl.py`／`sent_resplit.py`／`resplit_long_sentences.py` | ✅ S01 |
| `build_sentences --max-chars` | ✅ S1.1 |
| `refresh_kh4_after_resplit.py` | ✅ S23 |
| LSR-S23 embed／Qdrant／admit | ✅ CLOSED |

### 4.4 CLI 矩陣（目標）

```text
# 本批 item（三通道收束後）
python scripts/run_knowledge_ingress_kip.py --channel local_files --job-id 4 --apply
python scripts/run_knowledge_ingress_kip.py --channel sftp --source-key my_sftp --apply
python scripts/run_knowledge_ingress_kip.py --channel topic_harvest --trigger-ref <log> --item-ids 1,2,3 --apply

# 全庫驅動（領域／有界）
python scripts/refresh_knowledge_pipeline.py --from-stage sentences --until admit --domain ...
```

---

## 5. 分階路線

### Phase A — 歷史 LSR 補洞（✅ 已完成）

| 碼 | 內容 | 審計 |
|---|---|---|
| LSR-S01 | DDL＋items 重切 3111 parents | `LSRS-S01-CLOSED` |
| LSR-S23 | 再嵌＋Qdrant＋KH4＋admit＋112→9 | `LSRS-S23-CLOSED` |

### Phase B — 入庫規採納＋DDL（✅ `LSR-INGRESS-S0` CLOSED）

- 採納本檔為三通道強制規  
- 建 `knowledge_ingress_kip_run`  
- **驗收**：DDL＋selftest ✓

### Phase C — 統一執行器（✅ `LSR-INGRESS-S1` CLOSED）

- `ingress_kip.py`＋`run_knowledge_ingress_kip.py`  
- dry-run／apply 抽樣 ✓（見 `audits/LSR-INGRESS-S01-CLOSED-20260730.md`）  
- **驗收**：kip_run=`done`／`partial`／`failed` 誠實

### Phase D — 三通道＋後台接線（✅ `LSR-INGRESS-S2` CLOSED）

- local／sftp／harvest（或 refresh DAG）預設呼叫 KIP  
- admin UI：狀態燈＋不可靜默跳過  
- **驗收**：三通道各一最小實測（單檔／單題／單 SFTP 檔）；後台可見 kip_run

### Phase E — 銜接 KH10（另碼）

- `KH10-ENABLE-S1`：collect＋人裁 CLI  
- **驗收**：見 `reports/augur_kh10_enable_plan_20260729.md`；**入庫≠進化核准**

---

## 6. 後台（augur admin）操作契約

| 操作 | 完成定義（本規） |
|---|---|
| 主題抓取 | harvest／promote／（全文若授權）**且** KIP done／partial 入帳 |
| 本機匯入 | qualification 終態 **且** 對 `inserted` item 跑 KIP |
| SFTP 匯入 | 同本機；憑證仍住 `.env`（#5） |
| 顯示 | job 頁同時顯示 ingest 計數 **＋** KIP stages_json（切句／嵌／KH4／admit） |

**禁止**：後台顯示「匯入成功」但 KIP 未跑且未標 `skipped_explicit`。

---

## 7. 驗收總表（GATE）

| ID | 條件 |
|---|---|
| V-CH | 三通道文件／code 路徑皆指向同一 `run_kip_for_items` |
| V-MAX | 新段 `build_sentences --max-chars 800`；殘長句 resplit |
| V-EMB | CLEAN 可嵌句 gap-fill；junk 誠實入 ledger |
| V-KH4 | 語意型＋已嵌→eligible；非語意不假抬 |
| V-ADM | 本批 admit 盡力→≤9 |
| V-UI | 後台完成態含 KIP；跳過須明示 |
| V-FZ | 零市場 API |
| V-KH10 | 本規不自動 governance decision |

---

## 8. 風險與緩解

| 風險 | 緩解 |
|---|---|
| 後台同步 KIP 過久 | 預設背景 job＋心跳；UI 輪詢 kip_run |
| 三通道漏接 | S2 驗收強制三通道最小實測清單 |
| 與 refresh DAG 雙跑 | 單一 `ingress_kip` 入口；DAG 只編排呼叫 |
| private 不進 Qdrant | D11；顧問走 pgvector／私模 |
| 使用者以為＝KH10 | UI／審計寫死「自動最高 9」 |

---

## 9. 治理紅線

1. 三通道**不得**只入庫不跑 KIP（除非 `skipped_explicit`＋人）  
2. 不關 junk／不假抬 eligible  
3. 不自動 KH10／PME APPLY  
4. FZ-keep  
5. 重切＝結構修復，≠ AI 摘要入庫  

---

## 10. 建議拍板碼

| 碼 | 含義 |
|---|---|
| **`LSR-INGRESS-PLAN`**＋**`FZ-keep`** | ✅ 已採納（2026-07-30） |
| **`LSR-INGRESS-S0`** | ✅ kip_run DDL CLOSED |
| **`LSR-INGRESS-S1`** | ✅ 統一執行器 CLOSED |
| **`LSR-INGRESS-S2`** | ✅ local＋sftp＋harvest／admin 接線 CLOSED |
| **`KH10-ENABLE-S1`** | 另句（進化人裁） |

**次拍建議一句**：

```text
KH10-ENABLE-S1 + FZ-keep
```

（或 Postgres 恢復後先做 S2 live 抽樣驗收，無需新拍板。）

---

## 11. 回報摘要

| 項 | 內容 |
|---|---|
| **路徑** | 本檔（升格後） |
| **一句** | 主題抓取／本機／SFTP 全部強制走切句（含長句硬切）→嵌→KH4→admit≤9；後台同規；KH10 另碼 |
| **已完成** | 庫內 LSR 補洞；INGRESS S0／S1／S2 |
| **待拍** | `KH10-ENABLE-S1`（進化人裁） |

---

## 修訂

| 日 | 摘要 |
|---|---|
| 2026-07-30 | 初版：LSR 補洞→KH10 橋 |
| 2026-07-30 | **升格**：三通道＋後台強制 KIP；Phase A 標已 CLOSED；新增 INGRESS 拍板碼 |
| 2026-07-30 | Steward 拍 `LSR-INGRESS-PLAN+S0+S1+FZ-keep`；S0／S1 CLOSED；S2 待拍 |
| 2026-07-30 | Steward 拍 `LSR-INGRESS-S2+FZ-keep`；三通道＋後台接線 CLOSED |

*位階：[I] 計畫。治理原文以憲章 [N] 與 constitution-mcp 為準。*

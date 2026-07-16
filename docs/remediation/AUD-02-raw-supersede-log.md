# AUD-02 補正設計卷宗：raw_supersede_log

* **狀態**：✅ **計畫定案（決策 A/B 已解）、實作受閘**——設計與對抗評審已完成、兩項治權決策經 Steward 拍板（見 §三）。本文即 augur-code CLAUDE.md #20 意義下之**計畫先行報告**。程式實作依 #20（拍板後實作）、#7（須實測，本機無 PostgreSQL→須於備援環境跑 migration --check＋selftest）、#19（核心共用模組 generic_schema.py 逐檔檢視）受閘，**尚未寫入生產程式、未 apply 生產 DB**；施工待執行額度恢復後由工作流程 build 階段續行（含被中斷之三重對抗審查）。
* **憲章依據**：`AUGUR-MC v1.3 §P4.E5`（矛盾保存，MUST NOT last-write-wins，§8.4 不可豁免）、`§P4.E3`（只失效不刪除）、`§P4.E6`（provenance）；`AUGUR-WM v1.0 §WM.16`（矛盾保存）、`§WM.30`（雙時間）、`§WM.34`（機器稽核）。
* **對應審計**：AUD-02（critical）。解釋裁決 2026-001：AUD-02 為原始證據覆寫滅失，維持 critical。
* **來源**：ultracode 工作流程 `wf_bd8e98eb-474`（研究基準→三取向設計→評審擇 B→〔施工/審查/修訂因額度中斷〕）。分支：`remediation/aud-02-raw-supersede-log`。

---

## 一、問題與目標

現行 `generic_schema.upsert` 為 `ON CONFLICT DO UPDATE`；`reconcile.heal_by_date` 偵測 value_mismatch（DB≠API，即兩個不同時點 Observation 衝突）後以同一 upsert 路徑將 DB 舊值原地覆寫為 API 現值。衝突舊值僅以 examples 留存（上限 10、只在日誌），`attestation_result` 僅落計數——舊值一經 heal 即不可復原，構成 P4.E5 明文禁止之 last-write-wins（衝突證據未共存、未顯式標記、被靜默消滅）。

**目標**：heal 覆寫前，將受影響舊列與裁決脈絡快照至 append-only 帳表，使「API wins」成為攜帶自身 Evidence 的新 Knowledge；**upsert 主路徑語義一 byte 不動**、快照與 heal **同交易**（原子）。

## 二、設計（評審擇定：取向 B——憲章 supersede 語義完備版）

評審核心判準：P4.E5 要求的不只是「留舊值」，而是「衝突雙方共存＋裁決為攜帶 Evidence 之新紀錄」。故帳表同列並存 **old_row（敗方 DB pre-image）＋ new_row（勝方 incoming API 列）＋ attestation_run_id（裁決 provenance）**，使衝突對自足、可機器重建、不依賴可變主表。

### 2.1 帳表 DDL

```sql
-- raw_supersede_log：heal 覆寫前「被取代原值」快照帳本（AUD-02；P4.E5 衝突裁決留痕）
-- 每列＝一次「API wins」裁決之新 Knowledge：同時指涉衝突敗方(old_row)＋勝方(new_row)，
-- 攜自身 Evidence(attestation_run_id + reason)，append-only、永不覆寫原始證據。
CREATE TABLE IF NOT EXISTS raw_supersede_log (
    id                 BIGSERIAL   PRIMARY KEY,
    "table"            TEXT        NOT NULL,   -- 被 heal 之 raw API 表名（SQL 保留字→雙引號）
    pk                 JSONB       NOT NULL,   -- {鍵欄:值}（effective PK；schema-agnostic）
    old_row            JSONB       NOT NULL,   -- 敗方：upsert 前 DB 現值 pre-image（被取代之原始 Observation）
    new_row            JSONB       NOT NULL,   -- 勝方：本批 incoming API 列（ON CONFLICT 勝出側，攜勝方 Evidence）
    superseded_at      TIMESTAMPTZ NOT NULL DEFAULT now(),  -- transaction time（WM.30 交易軸）
    valid_time         DATE,                   -- valid time（被取代觀測之 date；WM.30 有效軸；非日欄時 NULL）
    reason             TEXT        NOT NULL,   -- 裁決由來（'heal_by_date' / 'daily_heal'）
    attestation_run_id BIGINT      REFERENCES attestation_result(id),  -- 裁決 provenance（P4.E6）
    note               TEXT
);
CREATE INDEX IF NOT EXISTS ix_supersede_table_time ON raw_supersede_log ("table", superseded_at);
CREATE INDEX IF NOT EXISTS ix_supersede_run        ON raw_supersede_log (attestation_run_id);
CREATE INDEX IF NOT EXISTS ix_supersede_pk_gin     ON raw_supersede_log USING GIN (pk);
```

### 2.2 接入點與交易語義

* **seam**：`src/augur/core/generic_schema.py:provision_and_upsert`，第 281 行 `eff = ensure_table(...)` 之後、第 282 行 `return upsert(...)` 之前——唯一同時握有 `cur / table / schema / eff(effective PK) / rows` 且早於 byte 覆寫之點。新增私有 helper `_snapshot_superseded(cur, table, rows, schema, eff, reason, run_id)`。
* **快照邏輯**：以 `eff` 對 incoming rows（比照 261–263 批內去重後）算 PK 集 → `SELECT <schema cols> FROM "table" WHERE (pkcols) IN (...)` 取 DB 現值 pre-image → **共用 `reconcile._norm`（reconcile.py:53）**同語意比對非鍵欄，僅值真異者為 supersession（純新 insert／未變列不留痕）→ 組 pk/old_row/new_row 之 JSONB（`psycopg2.extras.Json`，Decimal/date 以 `default=str` 序列化）→ `execute_values` 批次 INSERT。
* **同交易**：沿用呼叫端 `ingest.store`（ingest.py:182）之 `with db.transaction(conn) as cur:` 單一交易；快照 INSERT 排在 upsert **之前**、共用同一 cur，先取 pre-image 後覆寫；任一例外 → rollback → 快照與 heal 一起回滾（P4.E5 交易同一性）。
* **Gate（主路徑不動）**：新增 passthrough 參數 `snapshot_reason=None`（預設不快照＝upsert 主路徑與 daily 增量 sync 語義完全不變）。僅 heal 呼叫端透傳非 None：`reconcile.heal_by_date`（reconcile.py:238）、`daily_maintenance heal`（daily_maintenance.py:122）→ `sync.sync_by_date`（sync.py:495）→ `ingest.store`（ingest.py:183）→ `provision_and_upsert`（281–282）逐層傳 `"heal_by_date"`/`"daily_heal"`。

### 2.3 落位與隔離（must_graft 已納）

1. **INFRA_DDL 連動**：`src/augur/core/schema.py` INFRA_DDL + bootstrap_infra 加入本表（store() 依賴其存在）；**必須同步更新 schema.py:126 之 selftest 斷言**（現斷言 `set(INFRA_DDL)=={pipeline_execution_log, data_audit_log, attestation_result}`，不更新即紅）。
2. **冪等 migration**：`scripts/migrate_raw_supersede_ddl.py`（比照 `migrate_revalidation_ledger_ddl.py` 非破壞新表型：預設套用 DDL、`--check` 唯讀、VERIFY 查 information_schema/pg_constraint/pg_indexes）。
3. **被預測回讀隔離**：`old_row`（被取代舊值）+`superseded_at`（事後修正知識）落入預測回讀屬 `AUGUR-WM §WM.35` 消費閘破口——**須 REVOKE SELECT from augur_predict**，建表後即跑 `setup_predict_role --apply`；import_isolation 字面掃描不誤報（表名非 RBAC/chat/distill 禁字面）。
4. **值差判定共用 `reconcile._norm`**，不得另實作（防 Decimal/date/前導零/round 口徑漂移致假 supersession 或漏 supersession）。
5. **紅綠回歸鎖**：`--selftest` 固化「heal 觸發快照、非 heal 不觸發、no-op upsert 不入帳、byte-differ 入帳、帳表 append-only、同交易回滾」（CLAUDE #7/#15）。

## 三、治權決策（Steward 已拍板，2026-07-17）

評審官明示下列二項屬治權硬化／寫序變更，須 Steward 裁決。裁決結果：

* **決策 A — append-only DB trigger → 採 (a)：加硬 trigger＋併設 tombstone 法規抹除例外路徑**。
  * 裁決人：Constitution Steward（tsaitsangchi）；依 Steward「就把第七步收尾」之指示採認執行層建議 (a)。
  * 理由：本帳表承載原始證據，P4.E3/P4.E5 保護需求高於同族帳表對稱；`BEFORE UPDATE OR DELETE ... RAISE` 使不可覆寫成為機器可稽核保證（`AUGUR-WM v1.0 §WM.34`）。
  * 附帶義務：**必須併設 P4.E3 唯一例外之 tombstone 法規抹除路徑**（受控函式：抹除內容本體但留 tombstone＋完整 provenance；非經該路徑之 UPDATE/DELETE 一律被 trigger RAISE 擋下）。此例外機制列入實作檢查清單。
* **決策 B — attestation_result 寫序 → 採 (b)：`attestation_run_id` nullable＋事後回填**（Steward 明示確認）。
  * 裁決人：Constitution Steward（tsaitsangchi），2026-07-17 明示「nullable 事後回填」。
  * 理由：最小侵入、不改既有寫序；`reconcile.heal_by_date` 直呼 sync、無對帳 run 時 `run_id` 恆 NULL，`reason` 仍留痕（P4.E6 遞迴溯源鏈以 reason＋old_row/new_row 承載，不因無 run_id 而斷）。
  * 不採 (a) 前置 pending run，故 `attestation_result` 寫序完全不動、無 append-only 例外之新增。

**另注**：`docs/原則精華_v1.9.0.md #7`（correction＝覆蓋為當前值）須改為「新版本入庫、舊版標 superseded」以與本補正一致——屬 Layer 4 治權檔（原則精華）變更，依 CLAUDE #19/#26 須用戶拍板，code 不得先行（見步 12 治理收尾）。

## 四、實作檢查清單（審查/施工用）

- [ ] `scripts/migrate_raw_supersede_ddl.py`（DDL＋indexes＋**append-only trigger〔決策 A=(a)〕**；--check 唯讀；VERIFY）
- [ ] **tombstone 法規抹除受控函式〔決策 A 附帶義務〕**：唯一得繞過 append-only trigger 之路徑，抹除內容本體但留 tombstone＋provenance（P4.E3 例外）
- [ ] `src/augur/core/schema.py`：INFRA_DDL＋bootstrap_infra 加本表；**更新 :126 selftest 斷言**
- [ ] `src/augur/core/generic_schema.py`：`_snapshot_superseded` helper；`provision_and_upsert` 加 `snapshot_reason=None` gate（281–282 間接入）；upsert 本體不動
- [ ] heal 呼叫鏈透傳 `snapshot_reason`（＋run_id 視決策 B）：reconcile.py、daily_maintenance.py、sync.py、ingest.py
- [ ] `setup_predict_role`：raw_supersede_log 列入 REVOKE-from-augur_predict；建表後 --apply
- [ ] `--selftest` 紅綠鎖（六不變式，見 2.3.5）
- [ ] 共用 `reconcile._norm`（不另實作）
- [ ] 施工後：本機無 PostgreSQL，須於備援環境或人類本機跑 migration --check ＋ selftest 後，經人類 P5 拍板 apply 生產 DB、併 main

## 五、風險（評審官列示，供審查聚焦）

1. pre-image 取值成本：每次 heal 多一次 `SELECT WHERE PK IN`；heal 低頻、影響有限，但寬 PK/大批次須注意 IN 子句規模與複合鍵 `(col1,col2) IN ((...))` 建構正確性。
2. JSONB 序列化：DB pre-image 為 typed（Decimal/date/None），須 `Json(..., default=str)`；old_row 忠實反映 DB 現值、new_row 反映 incoming 原樣，兩側口徑一致以利重建。
3. `_norm` 語意漂移：不共用即假/漏 supersession（違 P4.E5）。
4. 主路徑共用風險：`provision_and_upsert` 為所有 upsert 主路徑，`snapshot_reason` 雖預設 None，仍須紅綠鎖防未來誤觸。

# Roadmap R4 — 資料地基親驗／帳本更新 [I]（2026-07-24）

* **性質**：[I] 執行／狀態報告（不創設義務；不改 [N]；禁假關 10-14）
* **拍板**：Steward「**開 R4**」（R0–R3／U3 DONE；對齊落地〔A〕）
* **路線圖**：`reports/augur_constitution_to_implementation_roadmap_20260724.md` §3.5
* **帳本**：`reports/augur_roadmap_r3_gap_ledger_20260724.md`（G-CAT-1／G-DIV-1／G-ATTEST）
* **閉合**：`audits/ROADMAP-R4-CLOSED-20260724.md`

## 0. 一句結論

R4＝**親驗＋安全最小動作＋工單／帳本更新**，非全量 FinMind 放量、非 DROP+re-sync。本機 `db.ping()=True`；`build_catalog --db-only` 綠（欄級對齊 0 mismatch）；Dividend **仍塌列**（工單待授權）；INFRA_DDL／歷史 attestation PASS 列可溯，**當日端到端對帳哨兵未重跑**（放量護欄）。

## 1. 環境

| 項 | 結果 | 證據 |
|---|---|---|
| 代理沙箱 `db.ping()` | False（預期） | 沙箱網路／PG 不可達 |
| unrestricted + `source .env` | **True** | 本輪 stdout |
| `pg_isready` | accepting | `127.0.0.1:5432` |

## 2. 驗收表（R4）

| # | 驗收項 | 結果 | 證據 |
|---|---|---|---|
| A | catalog 最小親驗（`db_only`，不打 API） | **PASS** | `python scripts/build_catalog.py --db-only` → exit 0；`完成: {'datasets': 84, 'table_zh': 0, 'column_zh': 1}`；log `/tmp/r4_build_catalog_db_only.log` |
| A2 | 欄級對齊（post） | **PASS** | SQL：`column_catalog`↔`information_schema` col-count mismatch **0**；orphan cc 列 **0** |
| A3 | 表級 provenance／n_stocks 真值 | **FAIL（已知債）** | `TaiwanStockPrice` catalog `n_stocks=3102`／`source_provenance=probe`／`last_verified≈2026-06-16`；DB `COUNT(DISTINCT stock_id)=55121`；landed 仍 probe **82**/86；`db_only` **故意不動表級**（`catalog.build` docstring） |
| B | Dividend 塌列診斷（唯讀） | **PASS（診斷）** | PK=`(stock_id)`；rows=**2411**=distinct stock_id；2330=**1** 列；`DividendResult`=(30973, 2369) |
| B2 | Dividend DROP+re-sync | **SKIP** | 破壞性＋放量；本輪未授權；見 §4 工單 |
| C | INFRA_DDL 哨兵（本地） | **PASS** | `python -m augur.core.schema --selftest` 全 ✓；四表 `to_regclass` 皆在 |
| C2 | attestation 端到端綠哨兵（當日） | **SKIP** | 須 `daily_maintenance --audit-only --heal`＝FinMind 放量；本輪停手 |
| C3 | 歷史綠哨兵列（可溯） | **PASS（史料）** | `attestation_result` id=**4** `2026-07-16` `passed=True` VM=0 EX=0 `audit_since=2026-06-01`（對齊 HANDOFF G1 attestation #4 敘事） |
| D | G1-PIN 不滾動追 | **PASS** | 原則精華 v1.10.0 解凍子條＋`scripts/preregister_arena_admission_gate.py` `PIN_ASOF="2026-06-30"`；本輪未改 as-of |
| E | 無 hand-patch | **PASS** | 未手動 UPDATE raw；catalog 走 writer `build(db_only=True)` |

**階段判定**：交付完成＝**DONE**；承重缺口 G-CAT-1（表級）／G-DIV-1／G-ATTEST（當日 e2e）仍 **partial**（≠假關清零）。

## 3. G-CAT-1 — catalog

### 3.1 親驗前（表級 STALE，與 construction v4 同構）

```text
landed / landed_probe / max(last_verified) / total
= 86 / 82 / 2026-06-29 / 97

TaiwanStockPrice catalog: n_stocks=3102, provenance=probe, last_verified≈2026-06-16
DB TaiwanStockPrice DISTINCT stock_id: 55121
```

### 3.2 最小安全動作

```bash
./venv/bin/python scripts/build_catalog.py --db-only
# → 84 datasets 欄級 refresh；exit 0；零 API
```

Post：表級數字**不變**（預期）；欄數對齊 mismatch=0。

### 3.3 gap_class

維持 **partial**：欄級可宣稱對齊；表級 provenance／n_stocks 須全量 `build`（API）才動——另案授權，非本輪。

## 4. G-DIV-1 — Dividend 工單（待 Steward 放量授權）

### 4.1 真兆（2026-07-24 本機）

| 指標 | 值 |
|---|---|
| PK | `PRIMARY KEY (stock_id)` 單欄 |
| 列數 | 2411 |
| distinct `stock_id` | 2411（＝每股恰 1 列） |
| `2330` | 1 列 |
| 對照 `TaiwanStockDividendResult` | 30973 列／2369 股 |

根因（既有）：首建 PK 鎖 `stock_id`；writer 已修 `require_keys=("date",)`（`src/augur/ingestion/sync.py:217-220`／by-date `:495-498`），**既有表 PK 不因新 writer 自癒**。

### 4.2 建議修復（**未執行**）

1. `#25` 最小探測：`TaiwanStockDividend` 單股單窗確認 IP／token 健康。  
2. Steward 明示授權後：`DROP TABLE "TaiwanStockDividend"`（或 rename 備份）→ 全史 per-stock re-sync（走現 writer，強制 date∈PK）。  
3. 驗收：PK ⊇ `(stock_id, date)`；同股多列；抽樣 2330 多年事件；**禁止** hand-patch INSERT。  
4. 未入生產特徵路徑前，alpha 不受污染（既有建設理解）；修復後才可升特徵候選。

**gap_class**：維持 **partial**（診斷閉合；資料未修）。

## 5. G-ATTEST — attestation

### 5.1 本地哨兵（本輪跑）

```text
python -m augur.core.schema --selftest
→ INFRA_DDL 含 pipeline_execution_log + data_audit_log + attestation_result + raw_supersede_log ✓
→ 全通過 ✓
```

| 表 | 存在 | 列數（本輪） |
|---|---|---|
| `pipeline_execution_log` | ✓ | 0 |
| `data_audit_log` | ✓ | 260464 |
| `attestation_result` | ✓ | 3 |
| `raw_supersede_log` | ✓ | 0 |

### 5.2 歷史 PASS（未當日重跑）

| id | run_at | driver | passed | VM | EX | audit_since |
|---|---|---|---|---|---|---|
| 4 | 2026-07-16 15:43 +08 | `daily_maintenance --audit-only --heal` | **True** | 0 | 0 | 2026-06-01 |
| 3 | 2026-07-16 15:04 +08 | 同上 | False | 0 | 6826 | 2026-06-01 |
| 2 | 2026-07-15 15:46 +08 | 同上 | True | 0 | 0 | 2026-07-01 |

綠哨兵句 SSOT（HANDOFF）：**「attestation：✅ PASS」**（非僅 rc=0）。E1 freshness 慣例「最近 PASS ≤2 日」→ 相對 2026-07-24，id=4 **已陳舊**；當日重跑＝放量 → **SKIP**。

**gap_class**：維持 **partial**（infra＋史料綠；當日 e2e 未親跑）。

## 6. 未做／護欄

* 未改 `constitution/` [N]、未開 RULING  
* 未假關 10-14／calendar 列  
* 未 FinMind 放量 audit／Dividend re-sync  
* 未 hand-patch raw  

## 7. 建議下一句

* **開 R5**（預測半系統）或 **開 U4**（攻擊「完整／綠／可開賽」）  
* 單點：Steward 授權 **Dividend DROP+re-sync** 夜批  
* 單點：授權全量 `build_catalog`（非 `--db-only`）刷新表級 provenance／n_stocks  
* 單點：窄窗 `daily_maintenance --audit-only --heal`（honor #7 近窗）刷新 attestation freshness

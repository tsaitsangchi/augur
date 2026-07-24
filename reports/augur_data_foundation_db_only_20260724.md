# 資料地基（僅庫內／零 API）[I]（2026-07-24）

* **性質**：[I] 執行／證據報告（不創設義務；不改 [N]；禁假關）
* **授權**：Steward 明示「**開資料地基（僅庫內／零 API）**」
* **硬邊界**：FinMind／FRED **仍凍**（`.cursor/rules/finmind-fred-api-freeze.mdc`）；不 DROP Dividend live；不改 [N]；不搶 PME 核心
* **帳本**：`reports/augur_roadmap_r3_gap_ledger_20260724.md`（G-CAT-1／G-DIV-1／G-ATTEST）
* **閉合摘要**：`audits/ROADMAP-DATA-FOUNDATION-DB-ONLY-20260724.md`
* **對照**：R4＝`reports/augur_roadmap_r4_data_foundation_20260724.md`；U4＝`audits/ROADMAP-U4-R4-ULTRACODE-20260724.md`

## 0. 一句結論

庫內可做的部分已親驗＋欄級 `build_catalog --db-only` 刷新：**欄級綠**；**表級 STALE 仍在**（需全量 API build）；Dividend **庫內斷點不變／PAUSED**；attestation **infra＋史料 id=4 複驗／當日 e2e 仍 SKIP**。三 Gap **皆維持 partial**——API 洞另帳，不假關「資料地基完整」。

## 1. 環境

| 項 | 結果 |
|---|---|
| `pg_isready` | `127.0.0.1:5432` accepting |
| `db.ping()` | **True**（unrestricted＋`.env`） |
| FinMind／FRED | **未呼叫** |

## 2. G-CAT-1 — catalog（庫內）

### 2.1 動作

```bash
./venv/bin/python scripts/build_catalog.py --db-only
# → exit 0；完成: {'datasets': 84, 'table_zh': 0, 'column_zh': 0}
# log: /tmp/df_build_catalog_db_only.log
```

`db_only=True` **故意不動**表級 `n_stocks`／`source_provenance`／`last_verified`（與 R4／U4 同構）。

### 2.2 前後對照（表級）

| 指標 | R4 | U4（Dividend 離線） | **本輪（庫內）** |
|---|---|---|---|
| landed／landed_probe／total | 86／82／97 | ≈83／81／97 | **84／82／97** |
| max(`last_verified`) | 2026-06-29 | （同族） | **2026-06-29**（未動） |
| Price catalog `n_stocks` | 3102 | 3102 | **3102**（未動） |
| Price `source_provenance` | probe | probe | **probe**（未動） |
| Price `last_verified` | ≈2026-06-16 | 同 | **2026-06-16**（未動） |
| DB `TaiwanStockPrice` DISTINCT `stock_id` | 55121 | 55121 | **55121** |
| DB Price 列數 | — | — | **12,100,183** |
| 欄數 mismatch（landed） | 0 | — | **0** |
| orphan cc（landed 缺表／缺欄） | 0 | — | **0** |
| cc 無實體表（excluded／tick 等） | （知情） | — | 71 列屬預期、非 landed 債 |

**判讀**：欄級可宣稱對齊；表級 provenance／`n_stocks` 與 DB 真值仍偏離 → **G-CAT-1 partial 不關**。全量 `build_catalog`（非 `--db-only`）＝API 洞、另授權。

## 3. G-DIV-1 — Dividend（唯讀／PAUSED）

**本輪禁止**：resume sync、probe、窄窗 audit／heal、DROP live。

### 3.1 庫內斷點親驗（2026-07-24 本輪）

| 指標 | 重建停點（09:39） | **本輪唯讀** | 判讀 |
|---|---|---|---|
| live 存在 | ✓ | ✓ | 不變 |
| PK | `(stock_id, date)` | `(stock_id, date)` | ✅ 正確 PK；**勿 DROP** |
| 列數／distinct stock_id | 9721／588 | **9721／588** | 斷點凍結 |
| 2330 列 | 42 | **42** | 不變 |
| bak | 2411／PK=`(stock_id)` | **2411／`(stock_id)`** | 保留 |
| DividendResult | 30973／2369 | **30973／2369** | 對照不變 |
| roster sync | 800／3123 | （無進度表變更；API 停） | **PAUSED** |
| 窄窗 audit | SKIP | **SKIP** | 凍結 |

詳見 `reports/augur_dividend_rebuild_20260724.md` §4／§8（已標庫內斷點複驗）。

**gap_class**：維持 **partial**。

## 4. G-ATTEST — attestation（infra／史料；禁當日放量）

### 4.1 本地哨兵

```text
python -m augur.core.schema --selftest
→ INFRA_DDL 四表 ✓；自測:全通過 ✓
```

| 表 | 存在 | 列數（本輪） | R4 對照 |
|---|---|---|---|
| `pipeline_execution_log` | ✓ | 0 | 0 |
| `data_audit_log` | ✓ | **261163** | 260464（庫內增量；非本輪 audit） |
| `attestation_result` | ✓ | 3 | 3 |
| `raw_supersede_log` | ✓ | 0 | 0 |

### 4.2 史料複驗（非當日 e2e）

| id | run_at | passed | VM | EX | audit_since |
|---|---|---|---|---|---|
| 4 | 2026-07-16 15:43 +08 | **True** | 0 | 0 | 2026-06-01 |
| 3 | 2026-07-16 15:04 +08 | False | 0 | 6826 | 2026-06-01 |
| 2 | 2026-07-15 15:46 +08 | True | 0 | 0 | 2026-07-01 |

**禁讀**：id=4 PASS ≠ 當日 e2e／今日 freshness／「可開賽」。當日 `daily_maintenance --audit-only/--heal`＝FinMind → **SKIP**。

**gap_class**：維持 **partial**。

## 5. Gap 狀態（誠實）

| ID | gap_class | 本輪 | 仍欠（API 洞／另帳） |
|---|---|---|---|
| G-CAT-1 | **partial** | 欄級 db_only 再綠；表級數字親驗仍 STALE | 全量 `build_catalog` |
| G-DIV-1 | **partial** | 庫內斷點複驗＝停點；**PAUSED** | 解凍後 resume（勿 DROP）；窄窗 audit |
| G-ATTEST | **partial** | infra selftest＋id=4 史料複驗 | 授權窄窗／正典 audit 刷新 freshness |

## 6. 未做／護欄

* 未呼叫 FinMind／FRED  
* 未 DROP／RENAME Dividend live  
* 未改 `constitution/` [N]、未開 RULING  
* 未假關三 Gap／10-14  
* 未動無關 PME 核心碼／呈核檔  

## 7. 建議下一句

* 續 **PME-Efull 呈核**（與本輪並行、已隔離）  
* 單點（API 洞）：路線圖全落地後明示「解凍 FinMind／FRED」→ Dividend resume（勿 DROP）＋窄窗 audit  
* 單點：授權全量 `build_catalog`（非 db-only）刷新表級  
* 單點：授權正典 attestation 刷新 freshness（或明示接受史料至解凍後）

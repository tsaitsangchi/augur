# Dividend 重建＋窄窗 audit（2026-07-24）

* **性質**：[I] 執行／證據報告（不創設義務；不改 [N]）
* **授權**：Steward 本輪明示 — Dividend 重建＋窄窗 audit；封存 `archive_push.sh --slug dividend-rebuild-narrow-audit`
* **工單 SSOT**：`reports/augur_roadmap_r4_data_foundation_20260724.md` §4；帳本 G-DIV-1
* **狀態**：**PAUSED（partial＋API 凍結）** — 已完成 rename／PK 修復／部分 per-stock sync（800/3123）；額度閘暫停後由 API 凍結護欄停跑。凍結＝`.cursor/rules/finmind-fred-api-freeze.mdc`。解凍＝路線圖全部落地 **且** 用戶明示「解凍 FinMind／FRED」。

## 0. 一句結論

**根因已修一半**：live 表 PK=`(stock_id, date)`、2330=42 列、總列 9721≫2411；roster 同步停於 **800/3123**（額度 5887/6000 主動暫停 → 隨後 API 凍結殺程）。窄窗 audit **未跑**（凍結禁止 FinMind）。G-DIV-1 維持 **partial**。

## 1. 診斷（before）

| 指標 | 值 | 來源 |
|---|---|---|
| 時間戳 | 2026-07-24T08:54:58 | `datetime.now()`＋`db.ping()=True` |
| PK | `(stock_id)` 單欄 | `pg_index` |
| 列數／distinct stock_id | 2411／2411 | `COUNT` |
| 2330 列數 | 1 | `COUNT`（僅最新事件） |
| DividendResult | 30973 列／2369 股；2330=45 | `COUNT` |
| catalog | `fetch_mode=per-stock`；`reconcile_scope=roster-scoped`；`attestation_mode=restating` | `dataset_catalog` |

根因：首建 PK 鎖 `stock_id`；writer 已 `require_keys=("date",)`，**既有表 PK 不自癒**。

## 2. 計畫（dry-run）

1. `#25` 最小探測：`data_id=2330` `start=end=2026-06-17` → OK 1 列（非 403）
2. `ALTER TABLE "TaiwanStockDividend" RENAME TO "TaiwanStockDividend_collapsed_bak_20260724"`
3. `sync.sync_finmind_dataset`／`_per_stock_sync`（`require_keys=("date",)`）
4. 驗收：PK⊇`(stock_id,date)`；2330≫1；總列≫2411；禁 hand-patch
5. 窄窗 audit（凍結後 **SKIP**）

## 3. 執行指令與 exit／關鍵事件

| 步驟 | 結果 | 證據 |
|---|---|---|
| diagnose | exit 0（catalog 欄名初誤用 `dataset_id` 後改 `dataset`） | stdout 08:54:58 |
| #25 probe | OK rows=1（`2026-06-17`）；非 403 | 08:55:08 |
| RENAME bak | exit 0；bak COUNT=2411 | 08:55:14 |
| 首輪 sync | **卡住／失敗**：RENAME 後索引名仍為 `TaiwanStockDividend_pk` → `CREATE TABLE` `DuplicateTable` → catalog 路徑失敗 → adaptive 寬窗探測表象「凍結」 | micro-sync traceback 09:06:52 |
| 修索引 | `ALTER INDEX "TaiwanStockDividend_pk" RENAME TO "TaiwanStockDividend_collapsed_bak_20260724_pk"` | 09:07:15 `pk_left=None` |
| micro-sync 5 股 | OK；PK=`(stock_id,date)`；2330=42 | 09:07:42 |
| full resume | `dividend_resume_sync.py` workers=4；進度至 **800/3123** 累計 log 9167 列 | log 09:08–09:20 |
| 額度閘 | `[finmind] 額度 5887/6000 ≥ 5800 → 主動暫停` | stdout |
| API 凍結停程 | `PAUSED by R5-S3 agent — FinMind/FRED API freeze` | log 09:38:52 |
| 窄窗 audit | **SKIP**（凍結禁止） | — |
| heal | **SKIP** | — |

Log：`/tmp/augur_logs/dividend_rebuild_20260724.log`；stdout：`…/dividend_rebuild_20260724.stdout`

## 4. 對照（after＝凍結停點 DB 親驗 09:39:43）

| 指標 | before | after（partial） | 判準 |
|---|---|---|---|
| PK | `(stock_id)` | `(stock_id, date)` | ✅ |
| 列數 | 2411 | **9721** | ✅ ≫2411 |
| distinct stock_id | 2411 | **588**／roster 3123 | ⚠️ 未滿 |
| 2330 列數 | 1 | **42**（對照 Result≈45） | ✅ ≫1 |
| bak | — | `TaiwanStockDividend_collapsed_bak_20260724` 仍在（2411／舊 PK） | 保留 |

## 5. 窄窗 audit／heal

**未執行**。`attestation_mode=restating` → 即便解凍後 audit 亦可能 exempt；須解凍後再跑：

```bash
./venv/bin/python scripts/daily_maintenance.py --audit-only --datasets TaiwanStockDividend --audit-days 14
```

## 6. G-DIV-1

**gap_class=`partial`**

* 已閉：塌列 PK 根因（live 新表含 `date`）；2330 多年事件；總列已超過舊 2411
* 剩餘：roster 未跑完（約 800/3123）；窄窗 audit 未跑；bak 尚未處置（可留可丟，另裁）

## 7. HEAD／tag

- **HEAD**（archive push）：`2bbf452b3da74fb01c2c1f1dd757ff9a9e40574a`（`2bbf452`）— `2026-07-24 archive push`
- **tag**：`archive-20260724-dividend-rebuild-narrow-audit` → 同上 commit

## 8. 停點／續跑

1. **凍結期間禁止**任何 FinMind／FRED（含 probe／audit／resume sync）。
2. 解凍後（用戶明示）：
   - live 已存在且 PK 正確 → **勿再 RENAME／DROP**
   - 直接：`sync.seed_roster` → `sync._per_stock_sync(..., start_floor="2005-06-19")` 或 `sync_finmind_dataset`（每股 `max(date)` resume）
   - 見 403／ban → 停；記錄 `failed_ids`；額度恢復後同路徑續
3. 勿再重演：RENAME 後須一併 rename 舊表上之 `TaiwanStockDividend_pk` 索引名，否則新表建不起。

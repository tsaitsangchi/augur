# Dividend 重建＋窄窗 audit（2026-07-24）

* **性質**：[I] 執行／證據報告（不創設義務；不改 [N]）
* **授權**：Steward 本輪明示 — Dividend 重建＋窄窗 audit；封存 `archive_push.sh --slug dividend-rebuild-narrow-audit`
* **工單 SSOT**：`reports/augur_roadmap_r4_data_foundation_20260724.md` §4；帳本 G-DIV-1
* **狀態**：**PAUSED（API 凍結）** — 2026-07-24 Steward 指示（同日收緊）：**constitution-to-implementation 全部階段落地前**不開 FinMind／FRED；runner `dividend_rebuild_runner.py --run`（原 PID 499349）已 `SIGTERM` 停掉；勿續打 API。護欄＝`.cursor/rules/finmind-fred-api-freeze.mdc`；HANDOFF §4.4。解凍＝路線圖全部落地 **且** 用戶明示「解凍 FinMind／FRED」（「計畫落地」／R5 局部 ≠ 解凍）。

## 0. 一句結論

**PAUSED（API 凍結）**：重建未完成（log 停於 probe OK → roster n=3123、sync 放量前／中被凍）。續跑須待 API 解凍後再 `sync_finmind_dataset`（表若已 bak／absent：見 §8，勿再盲目 RENAME）。

## 1. 診斷（before）

| 指標 | 值 | 來源 |
|---|---|---|
| 時間戳 | _pending_ | DB／runner log |
| PK | _pending_（R4 史料：`(stock_id)`） | `pg_index` |
| 列數／distinct stock_id | _pending_（R4：2411／2411） | `COUNT` |
| 2330 列數 | _pending_（R4：1） | `COUNT` |
| DividendResult | _pending_（R4：30973／2369；2330≈45） | `COUNT` |

## 2. 計畫（dry-run）

1. `#25` 最小探測：`TaiwanStockDividend` `data_id=2330` 單日窗；見 403／ban → 停、不重試風暴  
2. `ALTER TABLE "TaiwanStockDividend" RENAME TO "TaiwanStockDividend_collapsed_bak_20260724"`（保留塌列證據）  
3. `sync.sync_finmind_dataset(conn, "TaiwanStockDividend", roster)`（現 writer `require_keys=("date",)`）  
4. 驗收：PK⊇`(stock_id,date)`；2330≫1；總列≫2411；**禁** hand-patch  
5. 窄窗：`daily_maintenance.py --audit-only --datasets TaiwanStockDividend --audit-days 14`（可選 `--heal`）

Runner：`/tmp/augur_logs/dividend_rebuild_runner.py`；log：`/tmp/augur_logs/dividend_rebuild_20260724.log`

## 3. 執行指令與 exit

| 步驟 | 指令 | exit | 註 |
|---|---|---|---|
| diagnose | `dividend_rebuild_runner.py --diagnose` | _pending_ | |
| probe | `… --probe` | _pending_ | |
| run | `… --run` | _pending_ | |
| audit | `daily_maintenance.py --audit-only --datasets TaiwanStockDividend --audit-days 14` | _pending_ | |
| archive | `bash scripts/archive_push.sh --slug dividend-rebuild-narrow-audit` | _pending_ | |

## 4. 對照（after）

| 指標 | before | after |
|---|---|---|
| PK | _pending_ | _pending_ |
| 列數／stocks | _pending_ | _pending_ |
| 2330 列數 | _pending_ | _pending_ |

## 5. 窄窗 audit／heal

_pending_

## 6. G-DIV-1

_pending_（清 → `none`；否則 `partial`＋剩餘）

## 7. HEAD／tag

* HEAD：`d07c1caa83cb2d364d09791b70b41e37bba151e5`（`d07c1ca`）
* tag：`archive-20260724-api-freeze-plans-pending`

## 8. 停點／續跑（若有）

**2026-07-24 PAUSED（API 凍結）**：runner 已 kill；log＝probe OK、roster 3123、sync 未完成。表狀態：`TaiwanStockDividend` 當時已 absent、bak=`TaiwanStockDividend_collapsed_bak_20260724`（見 runner log）。解凍後：若 live 仍 absent／已以新 PK 首建 → **勿再 RENAME／DROP**；直接重跑 `sync_finmind_dataset`（每股 `max(date)` resume）。見 403 → 停、記錄 `failed_ids`、額度恢復後同路徑續。**凍結期間禁止任何 FinMind／FRED 呼叫。**

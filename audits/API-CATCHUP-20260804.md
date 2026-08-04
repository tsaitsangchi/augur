# API 補抓／日頻增量 [I]（2026-08-04）

> **位階**：[I] 工具／接續記憶（非 META-CONSTITUTION [N]）  
> **授權鏈**：Steward「**解凍 API**」→ `audits/API-THAW-20260804.md`（INV1∧INV2 ✅）→ 本輪最小增量補抓  
> **截止視窗**：`--end 2026-08-03`（完整交易日；**未**納 2026-08-04 部分日）  
> **時刻**：前後對照約 `2026-08-04 08:58 +0800`

---

## 0. 結論

| 項 | 結果 |
|---|---|
| FinMind 日維 | ✅ 完成；**無** 403／ban／額度停手 |
| FRED `sync_macro --no-catalog` | ✅ 完成；**無**停手訊號 |
| 中斷 | ❌ 未因 403／ban 中斷（曾為 log 緩衝殺重啟一次，resume-safe） |
| `--with-dim-sync`／Dividend rebuild／`--full-universe`／`heavy_slot`／`--allow-apply` | **未用** |
| `simulate_mc_paths` | 本輪期間 **未見** 在跑；未殺任何 MC |
| commit | **未**做（待 Steward） |

**補到哪日**：Price 系日表 `max(date)=2026-08-03`（維持／冪等重寫當日）；`fred_series` overall `max(date)` **2026-07-31 → 2026-08-03**（31 series 中 5 檔已到 08-03；其餘多停 07-31／更舊＝來源發布節奏，非本次 API 拒答）。

---

## 1. 前後 `max(date)` 對照（親查 DB）

| 表 | BEFORE | AFTER |
|---|---|---|
| `TaiwanStockPriceAdj` | 2026-08-03 | 2026-08-03 |
| `TaiwanStockPrice` | 2026-08-03 | 2026-08-03 |
| `TaiwanStockMarginPurchaseShortSale` | 2026-08-03 | 2026-08-03 |
| `TaiwanStockInstitutionalInvestorsBuySell` | 2026-08-03 | 2026-08-03 |
| `TaiwanStockPER` | 2026-08-03 | 2026-08-03 |
| `TaiwanStockDayTrading` | 2026-08-03 | 2026-08-03 |
| `TaiwanStockTotalReturnIndex` | 2026-07-09 | 2026-07-09（**未** dim-sync） |
| `TaiwanStockDividend` | 2026-08-23 | 2026-08-23（**未**碰） |
| `fred_series` overall `max(date)` | 2026-07-31 | **2026-08-03** |
| fred per-series `max(date)` 範圍 | 2026-04-01 .. 2026-07-31（n=31） | 2026-04-01 .. **2026-08-03**（n=31；≥08-03＝5） |

---

## 2. 指令與 log

### FinMind

```bash
# 顯式 --datasets（禁 Dividend／禁預設過寬全表）；禁 --with-dim-sync
env PYTHONUNBUFFERED=1 venv/bin/python -u scripts/daily_maintenance.py --end 2026-08-03 \
  --datasets TaiwanStockPriceAdj TaiwanStockPrice TaiwanStockMarginPurchaseShortSale \
             TaiwanStockInstitutionalInvestorsBuySell TaiwanStockPER TaiwanStockDayTrading
```

- PID（成功輪）：`826434`
- log：`/tmp/augur_logs/daily_maintenance_20260803_catchup.log`
- 摘錄：6／6 dataset 各 1 筆 by-date；**共 144,238 列**；句尾「增量完成」
- **rc**：程序已結束；log 無 Traceback → **推斷 0**（未包 wrapper 寫 `EXIT=`；以完成句為準）

### FRED

```bash
env PYTHONUNBUFFERED=1 venv/bin/python -u scripts/sync_macro.py --no-catalog
```

- PID（成功輪）：`826435`
- log：`/tmp/augur_logs/sync_macro_20260804_catchup.log`
- 摘錄：31 series；「落地完成：**344,886** 列 / 31 series → fred_series」
- **rc**：同上推斷 **0**

### 操作備註

- 首輪無 `-u`，log 緩衝為空 → **殺後**以 `PYTHONUNBUFFERED=1`／`-u` resume 重跑（#6）；**非** 403 停手。
- 並行探路之 `full_market_sync.py`（他 agent `head -80`）曾見存活 → **已停**，避免誤放量。
- 另見無參數 `daily_maintenance.py` 矩陣探路進程 → 補抓完成後已尝试停止，防預設全表燒額度。

---

## 3. 停手訊號（#24／#25）

| 訊號 | 本輪 |
|---|---|
| HTTP 403／IP ban／額度滿 | **未見**（兩份 log `rg` 無 403／ban／Quota／COOLDOWN／Traceback） |
| 處置 | 無需停手；正常完成 |

---

## 4. 仍缺口（誠實另帳，本輪故意不做）

- `TaiwanStockTotalReturnIndex` 仍 **2026-07-09** → 需 `--with-dim-sync`（M-G10），**本輪明示禁**
- Dividend：**未** rebuild
- 08-04 當日部分：**未**納入 `--end`（釘 08-03）
- FRED 多數系列 `max` 仍 07-31：屬來源／公佈日差異；overall 與部分利差／通膨預期系列已到 08-03

---

## 5. 與 thaw／MC

- 解凍判定：`audits/API-THAW-20260804.md`
- PriceAdj 於 thaw 親查已 08-03；本輪冪等確認＋FRED 追上
- **未**搶 `heavy_slot`、**未** `--allow-apply`、**未**啟動／終止 MC

---

*寫於 2026-08-04。位階 [I]。不 commit（待問）。*

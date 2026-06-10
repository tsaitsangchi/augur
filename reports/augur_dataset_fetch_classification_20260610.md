# augur dataset 抓取分類 + by-date / 範圍外排除決策（2026-06-10）

**用途**：記錄全市場 sync 對各 FinMind dataset 的抓取分類、4 個 date-based dataset 的處置、及 pilot 實證。
**誠實聲明（#15）**：全部數字皆 **pilot 實跑 source-traceable**（`finmind.fetch` API 回應 + augur DB `count(*)` query）。

---

## 抓取分類（adaptive，`sync_finmind_dataset`，無 hardcoded 清單，守 #3）

1. **market**：不帶 data_id 寬窗探測回資料 → market mode（整存）。
2. **per-stock**：canonical-2330-probe 有資料 → 逐股全史（resume per-stock `max_date`）。
3. **by-date fallback**（本次新增）：per-stock 探測失敗 → 試 `sync_by_date`（逐交易日全市場，不帶 data_id）；resume-aware（從 DB `max_date` 續）。
4. **OUT_OF_UNIT（範圍外，#3 排除清單）**：明文排除，不收 raw。

## 4 個 date-based dataset 之處置（pilot 實證）

| dataset | pilot 實測 | 處置 | 理由 |
|---|---|---|---|
| **GovBankBuySell** | 單日 14,474 列；近 3 交易日 **44,261 列、無塌陷**（DB=API；distinct(date,stock_id)=7,756 → 多銀行保留）| **by-date 抓** | 全市場/日（8 大行庫×股×日），量適中、可行 |
| **BlockTradingDailyReport** | 單日 97 列；**稀疏（單日僅數十～百列）→ backward-probe 取樣日多落空，無法可靠定起點 / 易漏歷史** | **排外（OUT_OF_UNIT）** | sub-stock（券商×股×日，鉅額交易事件）；稀疏致 #18 探測不可靠 → 無法不空抓地可靠抓；非當前 features 所需 |
| **TradingDailyReport（券商分點）** | 單股單日 4,645 列；**多日範圍被 FinMind 拒（單股×單日 only）；2015 無史** | **排外（OUT_OF_UNIT）** | sub-stock（券商×股×日）；單股×單日 × 3100 股 × 數百日 = **數十億列 / ~9-18 天連抓**，物理不可行；非當前 features 所需 |
| **WarrantTradingDailyReport** | **權證宇宙 126,368 檔**（`TaiwanStockInfoWithWarrant`）；需 warrant id | **排外（OUT_OF_UNIT）** | 非系統預測標的（系統預測上市櫃個股）；126k 檔 × 各活躍日 = 數百萬 call / 海量列 |

> 核心原則（呼應靈魂「系統單位 = 個股 × 日」+ #4 時間最小單位之實體延伸）：**raw 層收「個股×日」或粗類別標準信號（如 3 法人）；sub-stock 券商分點明細 / 鉅額交易 + 非股標的（權證）為範圍外排除**。

## 全量 + 增量一致（3 層守 OUT_OF_UNIT）

| | 排除 OUT_OF_UNIT（券商分點 / 權證 / 鉅額交易）| GovBank by-date |
|---|---|---|
| 列舉 | `daily_datasets()` 過濾 intraday + OUT_OF_UNIT | — |
| **全量** | `sync_finmind_dataset` 早退排除 | by-date **fallback**（per-stock 失敗 → sync_by_date）|
| **增量** | `sync_by_date` 早退排除（本次補，與全量一致）| `sync_by_date` **原生**（daily_maintenance 路徑）|

→ 任何入口（列舉 / 全量 / 增量 / 直接點名）皆一致排除券商分點 / 權證 / 鉅額交易；GovBank 全量與增量都抓得到。

## PK 註記（GovBank，誠實揭露 #15）

GovBank by-date 偵測 PK 偏寬：`[date, stock_id, buy_amount, sell_amount, buy, sell, bank_name]`——因 `bank_name` 維度不在 generic 標準 key 候選 → `detect_keys` 退回 fallback（非空非 TEXT 欄）。**無塌陷**（44,261 = API 列數）、**#7 對帳對穩定資料 PASS**；僅「未來值重述」時有重複列小風險（歷史 gov-bank 罕重述）。可選改善：將 `bank_name` 納入 KEY_CANDIDATES 得乾淨 PK `(date, stock_id, bank_name)`——本次未做（不影響正確性）。

## 變動檔（本次封存）

- `src/augur/ingestion/ingest.py`：`OUT_OF_UNIT` 排除清單（券商分點 + 權證 + 鉅額交易）。
- `src/augur/ingestion/sync.py`：`daily_datasets` 過濾 + `sync_finmind_dataset`（早退 + by-date fallback resume-aware + `_bydate_data_start` backward-probe）+ `sync_by_date`（早退排除）。
- `docs/原則精華_v1.3.0.md`：#3 ENFORCE 範圍外 + #18（API-driven fetch / 不空抓）明文入憲。

**source（#15）**：列數自 `finmind.fetch` pilot 回應；44,261 / distinct 7,756 自 augur DB query；126,368 自 `TaiwanStockInfoWithWarrant`；多日被拒 / 2015 無史自 pilot API 回應。

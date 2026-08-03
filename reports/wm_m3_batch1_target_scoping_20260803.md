# WM.36 M3 首批絞殺目標盤點——A 類 29 檔 × mapped 10 通道之交叉與第一批建議（2026-08-03）

**性質**：備料／證據整備呈案（**全程唯讀**：零 DDL、零 DB 寫入、零 commit、零 systemctl、未改任何 A 類檔、人簽欄未填）。
**射程**：M3＝A 類 29 檔五批絞殺（讀法乙，G0 格 1 已拍板）；本件只回答「**第一批該切哪些檔**」及其前置。
**上位錨**：`specs/WORLD-MODEL-SPECIFICATION.md` WM.35／WM.36（binding，逐字對齊）；設計 SSOT＝`reports/wm3536_vendor_registry_plan_20260802.md`（§5 程式規畫／§6 分階段／§11 逐檔清單）＋`reports/w2_20260801/WM_M1_pk_vs_appendonly_20260802.md`。
**不做**：**不解釋條文**（`AUGUR-MC v1.6 §8.1`）——凡遇條文歧義一律列入 §7 問題表待 Steward，本檔不代裁；不改既有報告、不動 `reports/w2_20260801/INDEX.md`。
**誠實級別**：全部歸類、排序、風險判讀為 **AI self-reported**（CLAUDE.md #32(a)）；全部數字出自本日唯讀實跑，指令逐條附上、任何人可零 AI 重跑覆核。

---

## §0 三句話結論

1. **A 類 29 檔中，16 檔（22 處）之直綁對象已有 mapped 通道**、7 檔半綠、6 檔全缺；但**「有通道」不等於「可切」**——六概念 `authoritative_binding_id` 全 NULL，`resolve()` 現況 **0/6**（親驗），故任何檔今日都還切不了，起點仍是 Steward 附卷採認。
2. **更硬的阻塞不在採認，而在驗收判準本身**：`compare_shadow_binding.py` 對新路 SQL 一律回掃 M2 口徑，而 9 個 mapped 通道**全部指向 vendor 名表**⇒ 依 plan §5 表列 5 之改線形（`FROM "TaiwanStockPrice"` → `f'FROM {resolve_sql("tw.daily_bar")}'`），新路 runtime SQL 與舊路**逐字相同**，工具必然落 `residual 拒`（親驗）或 `identical_sql → pending`——**M3 驗收判準「帳本 29 綠列」以現行工具無法達成**。此為本件第一順位待裁（§8 甲）。
3. 在上述兩件解開的前提下，**第一批建議 4 檔＋1 備選**（`build_pme_fundamental_features` / `build_feature_panel` / `run_sim_calibration_cell` / `simulate_mc_paths`；備選 `train_direction_threelens`）——全部冷路徑、單一查詢、結果 ≤6,832 列、參數可由 CLI 表達、無動態組表名、無「字面當參數」盲點，且**恰好同時觸兩個概念**（`tw.roster_membership`×2、`tw.daily_bar`×2），第一批即可把兩條解析路徑一次驗到。

---

## §1 現況親驗（2026-08-03；每條可獨立重跑）

| # | 事實 | 值 | 取得指令 |
|---|---|---|---|
| 1 | M2 基線 | **56 檔／170 處**（fred_series 4／quoted_table 140／quoted_table_esc 26），caliber_sha256=`0e0e608f75122bf5` | `venv/bin/python scripts/check_vendor_binding.py --scan` |
| 2 | A 類（plan §11 歸類） | **29 檔／69 處** | 同上 |
| 3 | 未歸類（出血中） | **4 檔**：`survivorship_economic_verdict` / `train_market_direction` / `verify_arena_watchlist` / `universe/core_gate` | 同上（`[UNCLASSIFIED]` 節） |
| 4 | Registry 概念（現行列） | **6**，`authoritative_binding_id` **全 NULL**、`decided_by`／`decided_at` 全 NULL | `SELECT … FROM world_concept_version WHERE superseded_at IS NULL` |
| 5 | 通道 | **98 列**＝mapped **10**／unmapped **88**；`superseded_at` 非空 **0** | `SELECT mapping_status, count(*) FROM world_channel_binding GROUP BY 1` |
| 6 | 解析可用性 | **0/6**（六概念皆「未指定權威表徵」） | `venv/bin/python scripts/compare_shadow_binding.py --preflight` |
| 7 | 絞殺帳本 | 表在，**0 列**；`verdict` CHECK ∈ {green, red, pending} | `\d vendor_binding_strangler_ledger`＋`SELECT count(*)` |
| 8 | 資料量（影響比對可行性） | `TaiwanStockPriceAdj` 11,190,394 列（≥2016-06-01 為 5,700,756）；`TaiwanStockInfo` distinct stock_id 3,128；TAIEX 交易日 6,832 | 四條 `SELECT count(*)`（見 §4.4） |

**mapped 10 通道全表**（本件交叉之唯一依據）：

| binding_id | concept_key | source_table | role |
|---|---|---|---|
| 2 | tw.roster_membership | TaiwanStockDelisting | observation |
| 3 | tw.delisting | TaiwanStockDelisting | observation |
| 4 | tw.trading_calendar | TaiwanStockTradingDate | observation |
| 12 | tw.fx.twd_usd | fred_series | observation |
| 25 | tw.corporate_action.ex_dividend | TaiwanStockDividend | observation |
| 28 | tw.roster_membership | TaiwanStockInfo | observation |
| 32 | tw.fx.twd_usd | TaiwanExchangeRate | observation |
| 48 | tw.corporate_action.ex_dividend | TaiwanStockDividendResult | observation |
| 75 | tw.daily_bar | TaiwanStockPrice | observation |
| 81 | tw.daily_bar | TaiwanStockPriceAdj | **derived** |

⇒ 10 通道覆蓋 **9 個 vendor 表**、**6 個概念**；其中 **4 個概念各有 2 條 mapped 通道**（見 §3）。

---

## §2 (a) A 類 29 檔 × mapped 通道之逐檔交叉

判準：檔內每個直綁表字面是否落在上表 9 表內。三分如下（處數＝M2 口徑靜態處數）。

### 2.1 全綠——**所有**直綁表皆已有 mapped 通道：**16 檔／22 處**

| 檔 | 處 | 直綁表 | 涉概念 | 熱路徑 |
|---|---|---|---|---|
| scripts/build_feature_panel.py | 1 | TaiwanStockInfo | tw.roster_membership | 否 |
| scripts/build_pme_fundamental_features.py | 1 | TaiwanStockInfo | tw.roster_membership | 否 |
| src/augur/advisor/payload.py | 1 | TaiwanStockInfo | tw.roster_membership | **是**（augur-advisor 常駐 active） |
| scripts/build_interaction_candidates.py | 1 | TaiwanStockPriceAdj | tw.daily_bar | 否 |
| scripts/evaluate_sim_calibration.py | 2 | TaiwanStockPriceAdj | tw.daily_bar | 否 |
| scripts/produce_direction_probability.py | 2 | TaiwanStockPriceAdj | tw.daily_bar | 否 |
| scripts/run_arena_daily_pipeline.py | 1 | TaiwanStockPriceAdj | tw.daily_bar | **是**（cron 20:00 週一–五） |
| scripts/run_sim_calibration_cell.py | 1 | TaiwanStockPriceAdj | tw.daily_bar | 否 |
| scripts/settle_arena_labels.py | 2 | TaiwanStockPriceAdj | tw.daily_bar | **是**（cron 21:30 週一–五） |
| scripts/settle_sim_outcomes.py | 1 | TaiwanStockPriceAdj | tw.daily_bar | 否 |
| scripts/simulate_mc_paths.py | 1 | TaiwanStockPriceAdj | tw.daily_bar | 否 |
| scripts/simulate_portfolio_risk.py | 3 | TaiwanStockPriceAdj | tw.daily_bar | 否 |
| scripts/train_direction_stack.py | 1 | TaiwanStockPriceAdj | tw.daily_bar | 否 |
| scripts/train_direction_threelens.py | 1 | TaiwanStockPriceAdj | tw.daily_bar | 否 |
| src/augur/arena/adapters.py | 1 | TaiwanStockPriceAdj | tw.daily_bar | 否（arena 每日鏈間接觸及） |
| src/augur/features/macro_vintage.py | 2 | fred_series | tw.fx.twd_usd | 否 |

⚠ 「全綠」只表示 **M2 靜態口徑內**之字面皆有通道；其中 **4 檔另有靜態射程外之直綁**（§6），已於 §5 排除出第一批。

### 2.2 半綠——部分表已 mapped、其餘缺通道：**7 檔／26 處**

| 檔 | 處 | 已 mapped | 缺通道 |
|---|---|---|---|
| scripts/build_daily_direction_features.py | 8 | PriceAdj | TaiwanDailyShortSaleBalances／DayTrading／InstitutionalInvestorsBuySell／MarginPurchaseShortSale／Shareholding／TotalReturnIndex |
| scripts/build_direction_stack_monthly.py | 4 | PriceAdj | InstitutionalInvestorsBuySell／TotalReturnIndex |
| scripts/run_arena_replay.py | 3 | PriceAdj | TotalReturnIndex |
| scripts/run_arena_round.py | 4 | PriceAdj | TotalReturnIndex |
| scripts/train_daily_direction.py | 2 | PriceAdj | TotalReturnIndex |
| src/augur/features/panel.py | 2 | PriceAdj | TaiwanStockMonthRevenue |
| src/augur/features/valuation.py | 3 | TaiwanStockPrice | TaiwanStockPER／TaiwanStockMarketValue |

### 2.3 全缺——無任一 mapped 通道：**6 檔／21 處**

`build_market_direction_features`(9 表)、`src/augur/features/chip.py`(7 表)、`derive_market_iv`(TaiwanOptionDaily)、`src/augur/features/fundamentals.py`(BalanceSheet＋FinancialStatements)、`src/augur/features/margin_cycle.py`(FinancialStatements)、`src/augur/features/phase.py`(InstitutionalInvestorsBuySell)。

### 2.4 A 類缺通道之表——**22 個**（WM.35 登錄前置；依 A 類處數排序）

| 表 | A 類處數 | 解鎖檔數 |
|---|---|---|
| TaiwanStockTotalReturnIndex | 9 | 5（replay／round／train_daily／stack_monthly／build_daily） |
| TaiwanStockInstitutionalInvestorsBuySell | 4 | 4（build_daily／stack_monthly／chip／phase） |
| TaiwanDailyShortSaleBalances · TaiwanStockMarginPurchaseShortSale · TaiwanStockShareholding · TaiwanOptionDaily · TaiwanStockFinancialStatements | 各 2 | 各 2 |
| DayTrading · CnnFearGreedIndex · TaiwanBusinessIndicator · FuturesInstitutionalInvestors · FuturesOpenInterestLargeTraders · TotalInstitutionalInvestors · TotalMarginPurchaseShortSale · TotalExchangeMarginMaintenance · GovernmentBankBuySell · HoldingSharesPer · SecuritiesLending · BalanceSheet · MonthRevenue · MarketValue · PER | 各 1 | 各 1 |

**登錄槓桿**：只補 `TaiwanStockTotalReturnIndex` 一表（＋其概念）即把 **5 檔／9 處**從半綠推進到全綠——是 A 類最高投報之單一登錄項。

---

## §3 交叉時撞見的三個結構事實（**不解釋條文**，列為 §7 問題）

**(3-1) 一概念多通道 ⇒ 權威指定會「收斂」語意。** `tw.daily_bar` 同時綁 `TaiwanStockPrice`(75, observation) 與 `TaiwanStockPriceAdj`(81, derived)。`resolve()` 只回一個。A 類中讀 PriceAdj 者 16 檔、讀 Price 者僅 `features/valuation.py` 1 處——若權威指 81，valuation 那處會被改寫成 PriceAdj（**還原前後價值不同＝行為變更**，影子比對應判 red）；若權威指 75，則 16 檔全部被改寫成未還原價。同型情形另見 `tw.roster_membership`（Info 28 vs Delisting 2）、`tw.corporate_action.ex_dividend`（Dividend 25 vs DividendResult 48）、`tw.fx.twd_usd`（fred_series 12 vs TaiwanExchangeRate 32）。

**(3-2) 一表多概念 ⇒ auto 模式必須 `--map`。** `TaiwanStockDelisting` 服務 2 概念（binding 2／3），工具明文要求 `--map TABLE=<concept_key>`（親驗：`make_lookup` len(keys)>1 即拋）。A 類目前不讀該表，故第一批不受影響；D 類 `backfill_lifecycle_retire` 會撞到。

**(3-3) 通道語意窄於實際消費（fred_series）。** `fred_series` 唯一 mapped 通道是 `tw.fx.twd_usd`(12)，但 `src/augur/features/macro_vintage.py` 是「fred_series 之唯一合法消費門」，以 `series_id=%s` 讀**任意總經序列**（其 docstring 自陳「未來 macro 特徵一律經此門」）。以概念鍵改線時，`concepts_for_table('fred_series')` 只會回 `tw.fx.twd_usd`，而該概念之權威若指向 `TaiwanExchangeRate`(32)，新路將指到**欄位形完全不同**的表。⇒ macro_vintage **不列入前批**，其前置是「總經觀測通道之概念登錄」。

---

## §4 (c) 影子比對可行性——工具親驗（讀 docstring／`--help`／唯讀 dry-run，**零 `--apply`**）

### 4.1 兩模式與硬閘（`scripts/compare_shadow_binding.py`）

- **auto**（`--sql/--sql-file`）：`concepts_for_table` → `resolve` → 換表名。現況 `resolve` 0/6 ⇒ **必 fail-closed**（工具 docstring 自陳此為正確行為）。
- **explicit**（`--old-sql-file`＋`--new-sql-file`）：兩路皆由改線者給定。
- **兩模式共通硬閘**（原始碼 :301）：`residual_vendor(new_sql)` 以 **M2 口徑**回掃新路，命中即拒。

### 4.2 親驗：residual 硬閘使「表名不變之改線」無法取得 green

```
$ venv/bin/python scripts/compare_shadow_binding.py \
    --old-sql 'SELECT max(date) FROM "TaiwanStockPriceAdj"' \
    --new-sql 'SELECT max(date) FROM "TaiwanStockPriceAdj"'
✗ ShadowError: 新路 SQL 仍含 vendor 直綁 [('TaiwanStockPriceAdj', 'quoted_table')]——「新路」是假的，拒絕比對（否則記出假 green）。
（exit code 親驗 = 1，fail-closed 正確）
```

而 plan §5 表列 5 之改線形是 `'FROM "TaiwanStockPrice"'` → `f'FROM {resolve_sql("tw.daily_bar")}'`——`resolve_sql` 回的是**引號 vendor 表名**（`world_concept.quote_ident(b.table)`），故：

- 新路**若照實給** ⇒ 撞 residual（上方親驗）；
- 新路**若等於舊路** ⇒ `identical_sql=True` ⇒ 判定 **pending**（「比對無鑑別力」，工具明文不記 green）。

且 9 條 mapped 通道之 `source_table` **全部**是 vendor 名表；DB 內亦**無**任何 canonical 小寫替身（親驗：`information_schema.tables` 查 `%price_adj%`／`%daily_bar%` 命中 0，`world_*` 僅 registry 自身 5 個關聯）。
⇒ **推論（機械事實，非條文解釋）：M3 驗收判準③「帳本 29 綠列」以現行工具＋現行通道形制無法達成。** 待裁選項見 §8 甲。

### 4.3 親驗：比對核心與 DB 路徑本身正常（用非 vendor 兩路驗）

```
$ venv/bin/python scripts/compare_shadow_binding.py \
    --old-sql 'SELECT count(*) FROM world_concept' \
    --new-sql 'SELECT count(*) FROM world_concept_version WHERE superseded_at IS NULL'
verdict=green n_old=1 n_new=1 diff_rows=0
```
⚠ 順帶記一筆：**1 列聚合之 green 鑑別力極低**（任何兩個湊巧同值的查詢都綠）。`run_arena_daily_pipeline` 之 `SELECT max(date)` 正屬此型 ⇒ 即使機制解開，該檔之 green 也不應被當成強證據。

### 4.4 親驗：參數與列數之可行性邊界

| 事項 | 親驗結果 | 對應限制 |
|---|---|---|
| `--param` 皆為字串（client-side 綁定） | `SELECT 1 LIMIT '61'` → **可**；`ANY('2330')` → **錯**（malformed array literal）；`ANY('{2330,2317}')` → **可** | 含 `= ANY(%s)` 之查詢須以 **array literal 形** 傳參（`--param '{2330,2317}'`），不可傳單一代號 |
| `--max-rows` 預設 200,000，超過即 `pending`（未讀完） | PriceAdj 全表 11,190,394 列、≥2016-06-01 5,700,756 列 | `train_direction_stack`／`train_direction_threelens`／`arena/adapters`／`produce_direction_probability` 之全宇宙查詢**必然超限** ⇒ 須縮窗（限少數 stock_id）才有鑑別力 |
| 唯讀護欄 `assert_readonly` 拒寫入動詞與多段語句 | 第一批 5 支候選之 SQL 逐條檢視，**無** insert/update/create/call/merge… 等字樣、皆單段 SELECT | 第一批不受此閘影響 |
| 資料漂移窗 | PriceAdj 每交易日 20:00 由 arena 鏈 sync、21:30 結算 | 影子雙跑**避開 19:30–22:00**，否則兩路之間落新列 ⇒ 假 red |

### 4.5 全綠 16 檔之 explicit 模式可行性逐檔判定

| 檔 | SQL 形 | 參數 | 預估列數 | explicit 可跑？ |
|---|---|---|---|---|
| build_pme_fundamental_features | `SELECT DISTINCT stock_id FROM "TaiwanStockInfo" ORDER BY stock_id` | 無 | 3,128 | ✅ 直接可跑 |
| build_feature_panel | 同上（**逐字相同**） | 無 | 3,128 | ✅ 直接可跑 |
| run_sim_calibration_cell | `SELECT date … WHERE stock_id=%s AND date > %s ORDER BY date` | scalar×2 | ≤6,832 | ✅ 直接可跑 |
| simulate_mc_paths | `SELECT date, close … WHERE stock_id=%s AND date<=%s AND close>0 ORDER BY date DESC LIMIT %s` | scalar×3（LIMIT 親驗可傳字串） | ≤window+1 | ✅ 直接可跑 |
| train_direction_threelens | `… WHERE stock_id = ANY(%s) AND date >= '2016-06-01'` | 陣列×1 | 全宇宙超限 | ⚠ 須 array literal＋縮窗 |
| train_direction_stack | 同型，另有**固定窗** 2016-06-01…2026-05-31（覆蓋期間最穩定） | 陣列×1 | 超限 | ⚠ 須縮窗 |
| arena/adapters | 同型（`date >= '2016-06-01'` 開放窗） | 陣列×1 | 超限 | ⚠ 須縮窗 |
| produce_direction_probability | 單句內含 2 處字面（含子查詢 `max(date)`），滾動 400 日窗 | 陣列×1＋scalar | 每股一列 | ⚠ 須 array literal |
| evaluate_sim_calibration | 2 句：`stddev_samp` 聚合（ANY）＋TAIEX 日曆 | 陣列＋scalar | 1 列／≤6,832 | ⚠ 聚合句鑑別力低 |
| build_interaction_candidates | `%`-格式化欄名白名單組出 4 種變體 | scalar×1 | ≤6,832 | ⚠ 抽 SQL 須處理 `%%` 轉義、4 條各驗 |
| settle_arena_labels | 2 靜態 ＋ **3 處字面當參數** ＋ **1 處動態組表名**；同時讀 PriceAdj 與 Price | — | — | ✗ 不宜（§6） |
| settle_sim_outcomes | 1 靜態 ＋ **3 處字面當參數**（含 Price）；`_prices` 自 settle_arena_labels 匯入 | — | — | ✗ 不宜 |
| simulate_portfolio_risk | 3 靜態 ＋ **6 處海外表字面當常數**（US/UK，皆 unmapped）＋ 1 處動態組表名 | — | — | ✗ 不宜 |
| macro_vintage | 通道語意窄於消費（§3-3） | — | — | ✗ 不宜 |
| advisor/payload | 單句、`ANY(%s)`；**live 服務**（改後須 `systemctl --user restart augur-advisor` 再實測，#7） | 陣列×1 | ≤picks | ⏸ 依 plan A5 殿後 |
| run_arena_daily_pipeline | `SELECT max(date)`（1 列）；**cron 熱路徑** | 無 | 1 | ⏸ 鑑別力低＋熱路徑 |

---

## §5 (b) 第一批建議——**4 檔＋1 備選**（逐檔說理）

排序判準（依任務給定優先序）：熱路徑外 ＞ 影子比對易做 ＞ 單一查詢 ＞ 覆蓋期間穩定；再加兩條本件實證得出的否決條件：**(x) 有靜態射程外直綁者不入首批**、**(y) 同檔同時讀兩張同概念表者不入首批**（§3-1 收斂會直接改值）。

| 序 | 檔 | 處 | 概念 | 入選理由 | 殘餘風險 |
|---|---|---|---|---|---|
| 1 | `scripts/build_pme_fundamental_features.py` | 1 | tw.roster_membership | 冷路徑（無 cron／無服務引用）；單句無參數；3,128 列；全檔僅 1 處 vendor 字面且無註解外殘留；無動態、無字面當參數、無 selftest 綁字面 | 概念權威若指 `TaiwanStockDelisting`(2) 則語意完全不同（roster ≠ 下市名冊）——**第一批正好用來把這個裁定驗出來** |
| 2 | `scripts/build_feature_panel.py` | 1 | tw.roster_membership | 與 1 之 SQL **逐字相同**（`SELECT DISTINCT stock_id FROM "TaiwanStockInfo" ORDER BY stock_id`），一次改線模板可覆蓋兩檔；冷路徑（親驗：全 repo 無程式呼叫者，`run_evaluation:81`／`run_feature_audit:56` 僅在提示字串提及、非 import／非 subprocess；非 cron） | 兩檔**須各自實跑影子比對**、不得以一次結果冒充兩列帳本（#15：綠燈量的必須是它宣稱在量的東西） |
| 3 | `scripts/run_sim_calibration_cell.py` | 1 | tw.daily_bar | 冷路徑；單句；參數全 scalar（`'TAIEX'`, approved_date）CLI 可直接表達；結果 ≤6,832 列（TAIEX 交易日）＝**有列可比又不撞 max-rows**；覆蓋期間為已實現交易日、最穩定 | 需避開 19:30–22:00 sync 窗 |
| 4 | `scripts/simulate_mc_paths.py` | 1 | tw.daily_bar | 冷路徑（`serve_probability_ui.py:237` 僅在提示字串提及、**非 import／非 subprocess**，親驗）；單句；三個 scalar 參數（`LIMIT %s` 傳字串親驗可行）；結果 ≤window+1 列 | 有 sibling import：`run_sim_calibration_cell:172` 取 `_hist_logrets`（**含本次改線之查詢**）、`evaluate_sim_calibration:573` 僅取 `_git7` ⇒ 改線後須連帶跑該兩支之自測 |
| 備 | `scripts/train_direction_threelens.py` | 1 | tw.daily_bar | 冷路徑、單句、單處；缺點是 `ANY(%s)`＋全宇宙列數超 max-rows，須以 array literal 縮窗（親驗可行） | 縮窗後之 green 只對該窗成立，須於 evidence 註明窗口 |

**為何刻意不選**：`run_arena_daily_pipeline`／`settle_arena_labels`（cron 熱路徑，且後者另有 3 處字面當參數＋1 處動態表名＋同時讀 Price 與 PriceAdj）、`settle_sim_outcomes`（同型盲點）、`simulate_portfolio_risk`（6 處海外表常數、全 unmapped）、`advisor/payload`（live 服務、plan A5 殿後）、`macro_vintage`（§3-3）、`train_direction_stack`／`adapters`／`produce_direction_probability`（列數超限，屬第二批）。

**第一批之概念覆蓋**：`tw.roster_membership`×2 ＋ `tw.daily_bar`×2 ⇒ 一批即檢驗兩個概念之權威裁定是否選對表，**把 §3-1 的收斂風險在最小爆炸半徑內暴露**。

---

## §6 (e) 誠實：靜態射程外之直綁（**本件所有交叉皆只涵蓋 M2 靜態口徑**）

M2 口徑＝`FROM\s+"CamelCase"`／其跳脫變體／`FROM\s+fred_series`。以下**不在**口徑內，`grep → 0` 之驗收句對它們**假綠**：

| 型 | 全 repo | A 類 | 舉證 |
|---|---|---|---|
| **動態組表名**（`FROM "{var}"`） | **52 處／20 檔** | **3 處／3 檔**：`settle_arena_labels:84`、`simulate_portfolio_risk:340`、`features/chip.py:55` | `grep -rn 'FROM \\?"{' --include=*.py src/ scripts/` |
| **vendor 字面當參數／常數**（不在 FROM 行） | 未全量掃 | **35 處／7 檔**：`build_market_direction_features` 15（provenance 標籤，寫進特徵列）、`simulate_portfolio_risk` 6（`ANALOG_EPISODES` 內 USStockPrice×5／UKStockPrice×1）、`chip.py` 4（`_table_covers(cur,"…")`×3＋selftest 斷言×1）、`settle_arena_labels` 3、`settle_sim_outcomes` 3、`valuation.py` 3、`margin_cycle.py` 1 | 見 §9 重跑腳本 |
| **JOIN 形直綁**（M2 只認 FROM） | **2 處**：`verify_daytrade_candidates:25`（B）、`repair_priceadj_basis:30`（D） | **A 類 0 處**（親驗全 repo 僅上列兩處） | `grep -rn 'JOIN \\?"[A-Z][A-Za-z]*\\?"'` |
| **完全在 52／56 檔清單外之消費模組** | 至少 1：**`src/augur/evaluation/label.py`**——`ADJ_TABLE = "TaiwanStockPriceAdj"` 常數 ＋ 3 處 `FROM "{ADJ_TABLE}"`；**不在 baseline 56 檔、不在 plan §11 52 檔**，而它是標籤產生器（生產消費鏈正身形） | — | `grep -n ADJ_TABLE src/augur/evaluation/label.py` |

**兩個連帶效應**：
1. **selftest 會變紅是預期、不是意外**：`features/valuation.py:90/92/96`、`features/margin_cycle.py:122`、`features/chip.py:219` 之自測以「SQL 內含 vendor 字面」為斷言 ⇒ 改線同批必須改斷言，且**須先退回舊版確認該斷言真的會紅**（記憶：回歸鎖唯一有效驗法）。
2. **「A 類 grep → 0」不等於「A 類已絞殺完」**：至少 3 檔（chip／settle_arena_labels／simulate_portfolio_risk）在靜態歸零後仍留動態或參數形直綁。**建議把「A 類清償」定義為靜態 0 ＋ 上述三型逐檔 AST／人工親驗留檔**，否則會複製「綠燈量的不是它宣稱在量的東西」之舊病。

---

## §7 (d) 五批草案與依賴序

現行 plan §6 之 M3 批次是**依模組型別**（A1 features lib ×7 → A2 build_* → A3 train/produce → A4 arena＋sim → A5 advisor）。本件交叉顯示：**A1 features lib 恰是通道最缺的一群**（chip 7 表全缺、fundamentals／margin_cycle／phase 全缺、valuation／panel 半綠、macro_vintage 語意窄）——若照原序開工，第一批就會卡在 WM.35 登錄而不是絞殺本身。故並陳**乙案：依 registry 就緒度排批**（原案＝甲案，保留）。

**乙案（建議）**

| 批 | 名 | 檔 | 前置依賴 |
|---|---|---|---|
| **B1** | 已 mapped × 冷路徑 × 小結果 | build_pme_fundamental_features、build_feature_panel、run_sim_calibration_cell、simulate_mc_paths（＋備 train_direction_threelens） | ①Steward 採認 `tw.roster_membership`／`tw.daily_bar` 權威表徵 ②§8 甲之判準處置 |
| **B2** | 已 mapped × 大結果／陣列參數 | train_direction_stack、train_direction_threelens、arena/adapters、produce_direction_probability、build_interaction_candidates、evaluate_sim_calibration | B1 之比對協定（縮窗規格）定案 |
| **B3** | 已 mapped × 熱路徑／多形直綁 | run_arena_daily_pipeline、settle_arena_labels、settle_sim_outcomes、simulate_portfolio_risk、advisor/payload（殿後、改後重啟服務再實測） | B2 完成；`simulate_portfolio_risk` 另需 US／UK 表通道登錄；settle 兩支需先處理「同檔讀 Price＋PriceAdj」 |
| **B4** | 需新通道登錄（單／雙表即可解鎖） | run_arena_replay、run_arena_round、train_daily_direction、build_direction_stack_monthly（皆卡 TRI）、features/panel（MonthRevenue）、features/valuation（PER＋MarketValue）、features/phase（IIBS）、features/margin_cycle＋fundamentals（FinancialStatements／BalanceSheet）、derive_market_iv（OptionDaily） | **WM.35 登錄批次**（概念＋通道＋權威指定，人簽）；TRI 為最高槓桿（解 5 檔） |
| **B5** | 多表重檔 | features/chip.py（7 表＋動態＋參數形）、build_daily_direction_features（7 表）、build_market_direction_features（9 表＋15 處 provenance 字面）、macro_vintage（總經通道概念） | B4 登錄完成；且需 §7 之 provenance 字面是否在射程內之裁示 |

**關鍵路徑**：B4／B5 之瓶頸不是改線工時，而是**22 表之概念與通道登錄＋人簽**。若 10-05 硬里程碑不動，**登錄批次須與 B1 平行啟動**，不可等 B3 做完再開。

---

## §8 尾節——hugo 圈選（本件唯一決策面；AI 不代裁、人簽欄未填）

**甲｜M3 驗收判準與工具實作之衝突處置（第一順位，B1 開工前必須有解）**
- **甲-1** 建 canonical 關聯（如 `world_daily_bar` view）作為權威表徵之 `source_table`，使新舊 SQL 真的不同 ⇒ 可得真 green。（代價：DDL＋新通道登錄，須 #6 明示；好處：判準③「29 綠列」原文可原封達成）
- **甲-2** 維持表名不變之改線，**把 `pending(identical_sql)` 正式認定為該型之合格證據**，另以「(i) 檔內自測紅綠 (ii) 行為探針對照」補足。（代價：判準③需改寫；好處：零 DDL、最小改動）
- **甲-3** 放寬 `residual_vendor`：豁免「恰等於 resolve 所得權威表名」者。（代價：弱化 #35 絆線，須同時補「豁免只在 resolve 成功時成立」之機械檢查）
- **甲-4** 其他／暫緩（則 B1 不開工，M3 排程需重估）

**乙｜第一批名單**
- **乙-1** 照本件建議 4 檔（build_pme_fundamental_features／build_feature_panel／run_sim_calibration_cell／simulate_mc_paths）
- **乙-2** 上列 4 檔 ＋ 備選 train_direction_threelens（5 檔）
- **乙-3** 只切 2 檔（同概念 roster 對）先驗協定
- **乙-4** 自訂（請指名）

**丙｜批次順序**
- **丙-1** 乙案（依 registry 就緒度，本件建議）｜**丙-2** 甲案（照 plan §6 原模組序）｜**丙-3** 混合（請指示）

**丁｜WM.35 登錄批次是否與 B1 平行啟動**（22 表；建議先登 `TaiwanStockTotalReturnIndex`＝解鎖 5 檔）
- **丁-1** 平行啟動、TRI 優先 ｜ **丁-2** 序列（B3 後才登錄，10-05 風險由 Steward 承擔）｜ **丁-3** 其他

**戊｜「A 類清償」之定義**（影響驗收句是否假綠）
- **戊-1** 靜態 grep 0 即算 ｜ **戊-2** 靜態 0 ＋ 動態／參數／JOIN 三型逐檔親驗留檔（本件建議）｜ **戊-3** 其他

**待 Steward 解釋之條文問題（AI 不代裁，僅列兩造事實）**
- **Q-A（§3-1）**：一概念多通道時，`authoritative_binding_id` 之指定使還原價／未還原價二擇一。WM.14「權威表徵恰解析至一」與「行為零變更」之絞殺要求，在 `tw.daily_bar` 上是否要求**再分概念**（如另立「已還原日 K」概念），或由權威指定逕行收斂？
- **Q-B（§6）**：`build_market_direction_features` 之 15 處字面是寫進特徵列的 **provenance 標籤**（記錄「這個值來自哪張表」），非查詢繫結。WM.36「不得以來源位置字面直接繫結」是否及於 provenance 記錄？
- **Q-C（§6）**：`src/augur/evaluation/label.py` 不在 plan §11 之 52 檔內，但形制屬生產消費鏈。其歸類（A？）與是否納入 M3 射程，請一併裁示。連同 M2 已呈報之 4 檔 UNCLASSIFIED（`survivorship_economic_verdict`／`train_market_direction`／`verify_arena_watchlist`／`universe/core_gate`）。

---

## §9 誠實揭露與可重跑指令（CLAUDE.md #32／L6.18(c)）

- 本報告**全部判讀為 AI self-reported**，不構成「世界如此」之權威確認；決策權在 Steward。
- **本輪唯一產出＝本檔**；零 DDL、零 DB 寫入、零 commit、零 systemctl；未改任何 A 類檔（`git status --porcelain` 於作業前後皆空）；`--apply` 未曾使用（帳本仍 0 列，可覆核）。
- **未做**：未逐檔 AST 排除動態組表名（僅以 regex 掃出 52 處並抽樣親驗常數值）；未全 repo 掃「字面當參數」（僅掃 A 類 29 檔）；未驗 88 條 unmapped 通道之語意正確性；未對第一批 4 檔實跑影子比對（`resolve` 0/6 ⇒ 今日跑必 fail-closed，跑了也只是記錄阻塞）。
- **重跑指令**（唯讀）：

```bash
cd /home/hugo/project/augur
venv/bin/python scripts/check_vendor_binding.py --scan          # 56 檔/170 處、A/B/C/D 歸類、UNCLASSIFIED
venv/bin/python scripts/compare_shadow_binding.py --preflight   # 帳本在否 + 六概念可解析 0/6
set -a && . ./.env && set +a
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c \
 "SELECT binding_id, concept_key, source_table, channel_role FROM world_channel_binding WHERE mapping_status='mapped' ORDER BY binding_id"
grep -rn 'FROM \\?"{' --include=*.py src/ scripts/ | wc -l                    # 動態組表名 52
grep -rn 'JOIN \\?"[A-Z][A-Za-z]*\\?"' --include=*.py src/ scripts/           # JOIN 形 2 處
grep -n 'ADJ_TABLE' src/augur/evaluation/label.py                             # 清單外消費模組
```

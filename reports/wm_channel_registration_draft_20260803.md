# WM.35 通道登錄批次｜A 類缺通道 22 表之「概念定義＋通道繫結」草案（Steward 圈選單）——2026-08-03

> **性質**：WM.35／WM.36 登錄批次之**備料呈案**（`AUGUR-MC v1.6 §8.1`：AI 僅**草擬、比對、呈案**；**本報告零條文解釋**——凡條文歧義一律列 §6 待 Steward）。
> **全程唯讀**：本輪零 DDL、零 DB 寫入、零 commit、零 systemctl；`decided_by`／`decided_at` 一欄未填、範本留 `⟨…⟩` 佔位（never-type-human-signature）。唯讀證明見 §8。
> **目的**：把 `reports/wm_m3_batch1_target_scoping_20260803.md` §2.4 之「A 類 22 表缺 mapped 通道」從**研究**壓成**圈選**。該報告 §7 明載「登錄批次須與 B1 平行啟動，不可等 B3 做完」＝關鍵路徑。
> **上游 SSOT**：`specs/WORLD-MODEL-SPECIFICATION.md`（WM.14／WM.15／WM.31／WM.32／WM.35／WM.36／WM.37／A.34／A.35／A.37）／`reports/wm3536_vendor_registry_plan_20260802.md`（設計）／`reports/wm_m3_batch1_target_scoping_20260803.md`（§2.4 目標集）／`reports/wm_annexf_authoritative_binding_prep_20260803.md`（丙案形制＋既有六概念）。
> **數字時點**：全部為 **2026-08-03 live 唯讀現查**（psql／`data_audit_log`／`dataset_catalog`／原始碼親讀），**非抄既有報告**；指令附 §8，可零 AI 重跑覆核。
> **誠實級別**：全部歸類、命名、七欄草擬、重疊判斷為 **AI self-reported**（CLAUDE.md #32(a)），不構成「世界如此」之權威確認。

---

## §0 五句話結論

1. **目標集不是 22 表、是 23 表**。M2 掃描器之正規式 `FROM\s+"([A-Z][A-Za-z]+)"`（`scripts/check_vendor_binding.py:52`）**不含數字字元類**，故 `TaiwanStock10Year` 之 2 處直綁（`src/augur/features/valuation.py:37`、`src/augur/audit/field_correlation.py:63`）**從未進入 M2 口徑**——`valuation.py` 被記為 3 處，實為 4 處。此為既有假綠，非本輪新增（§1.3）。
2. **建議 23 個世界概念**（非 22）。抵銷來源：＋1 表（10Year）、＋1 概念（`TaiwanDailyShortSaleBalances` 一表供兩事實）、−1 概念（`TaiwanStockMarginPurchaseShortSale` 與 `TaiwanDailyShortSaleBalances` 之融券餘額**經親驗為同一世界事實、兩通道、單位差 ×1000**）。另列 **3 組可合併候選**，若 Steward 全採合併則收斂為 **20 個概念**（§5）。
3. **TRI 一節之結論與原假設相反**：`TaiwanStockTotalReturnIndex` 之 9 個 A 類處中，**4 處純粹把它當交易日曆用**（只 `SELECT date`），而其 TAIEX 日期集合與已 mapped 之 `tw.trading_calendar`（binding 4，`TaiwanStockTradingDate`）**完全相同**（5,788 vs 5,788，雙向差集皆 0，親驗）。⇒ 那 4 處**不需要新概念**，應直接繫既有 `tw.trading_calendar`；新概念只服務 5 處取價用途（§2）。
4. **TRI 同時是本批唯一「已死」之表**：`max(date)=2026-07-09`，而其餘 22 表皆 `2026-07-31`；`data_audit_log` 最後一筆為 **2026-06-20**，其後 14 個交易日（06-22→07-09）之列**無任何 audit 列**，07-09 之後完全停滯。`TaiwanStockTradingDate` 在 (07-09, 07-31] 尚有 **16 個交易日**是 TRI 沒有的。⇒ 4 個「拿 TRI 當日曆」的消費點目前吃的是一份**落後 16 個交易日的錯日曆**（§2.4）。
5. **登錄不足以解除直綁**：23 表中 **7 表為多值表**（TRI 之 TAIEX/TPEx、OptionDaily 之 `option_id='TXO'`＋`trading_session='position'`、法人表之 `name`、HoldingSharesPer 之 `HoldingSharesLevel`…），消費端即使改繫概念鍵，**仍須內嵌列篩選字面**——正是 WM.36 禁令原文所列之「series 識別碼」。此與 Annex F 呈案 §7 **Q2 同型且更廣**，是本批之第一順位待裁（§6 Q-R2）。

---

## §1 現況親驗（2026-08-03；每條可獨立重跑）

### 1.1 Registry 起始基線（作業前後同值＝零寫入證明，§8）

| 身分列 | 版本列 | 現行列 | 已親簽 `decided_by` | 已指定權威 | 通道列 | mapped | 已 supersede 通道 |
|---|---|---|---|---|---|---|---|
| 6 | 6 | 6 | **0** | **0** | **98** | **10** | **0** |

`venv/bin/python -m augur.catalog.world_concept --check` ⇒ 六概念**全部**未指定權威表徵，`resolve()` **0/6 fail-closed**（沿 Annex F 呈案 §1.3，本輪複查未變）。

### 1.2 目標 23 表之通道現況（皆已有 binding 列，狀態皆 `unmapped`／`observation`）

**⇒ 「缺 mapped 通道」之精確語意＝「binding 列在、`concept_key` 為 NULL、`mapping_status='unmapped'`」；缺的是概念定義與繫結，不是 binding 列本身。**

### 1.3 誠實：M2 口徑第 23 表（本輪新發現）

```
scripts/check_vendor_binding.py:52
  _QUOTED = re.compile(r'FROM\s+"([A-Z][A-Za-z]+)"')      # ← [A-Za-z]+ 不含 0-9
```

親驗 repo 全量含數字之引號表名直綁：

```
$ grep -rnoE 'FROM \\?"[A-Za-z]*[0-9][A-Za-z0-9]*\\?"' --include=*.py src/ scripts/
src/augur/audit/field_correlation.py:63:FROM "TaiwanStock10Year"
src/augur/features/valuation.py:37:FROM "TaiwanStock10Year"
```

而 M2 掃描器對 `valuation.py` 的輸出是：

```
src/augur/features/valuation.py (3): TaiwanStockMarketValue×1 TaiwanStockPER×1 TaiwanStockPrice×1
```

⇒ **`TaiwanStock10Year` 落在 M2 靜態口徑之外**。這使 `wm_m3_batch1_target_scoping` §2.2 之「valuation.py 3 處」與「A 類 22 表」皆低估。本件把它補進來（第 23 表，binding 30），並列入 §6 Q-R6 請 Steward 裁其歸類與是否納入 M3 射程（形制同 Annex F 呈案 Q-C 之 `evaluation/label.py`）。
**連帶**：`src/augur/audit/field_correlation.py` 亦不在 plan §11 之 52 檔清單內（`grep` 親驗），與 `label.py` 同型。

### 1.4 二十三表資料現況總表（psql 現查，**非抄報告**）

| # | 表（binding_id） | 列數 | 期間 min→max | 維度基數 | PK | 最近 `data_audit_log` | `attestation_mode` / `finalize_lag_days` |
|---|---|---|---|---|---|---|---|
| 1 | `TaiwanStockTotalReturnIndex`(**78**) | **10,830** | 2003-01-02 → **2026-07-09** | **2** `stock_id`(TAIEX 5,788／TPEx 5,042) | (stock_id,date) | **2026-06-20**（⚠ 唯一非 08-01） | byte / 1 |
| 2 | `TaiwanStockInstitutionalInvestorsBuySell`(60) | 28,037,624 | 2012-05-02 → 2026-07-31 | **43,906** stock_id | (stock_id,date,name) | 2026-08-01 17:49（83,312 列） | byte / 1 |
| 3 | `TaiwanDailyShortSaleBalances`(56) | 7,758,897 | 2005-07-01 → 2026-07-31 | 2,480 stock_id | (stock_id,date) | 2026-08-01 17:45 | byte / 1 |
| 4 | `TaiwanStockMarginPurchaseShortSale`(49) | 8,106,445 | 2001-01-05 → 2026-07-31 | 2,437 stock_id | (stock_id,date) | 2026-08-01 17:49 | byte / 1 |
| 5 | `TaiwanStockShareholding`(62) | 8,825,289 | 2004-02-12 → 2026-07-31 | 2,642 stock_id | (stock_id,date) | 2026-08-01 17:55 | byte / 1 |
| 6 | `TaiwanOptionDaily`(43) | **34,108,503** | 2002-01-02 → 2026-07-31 | 205 option_id | **13 欄 PK（含 open/max/min/close/volume/…）** | 2026-08-01 17:46 | byte / 1 |
| 7 | `TaiwanStockFinancialStatements`(68) | 2,694,918 | 1991-12-31 → **2026-06-30** | 2,450 stock_id | (stock_id,date,type) | 2026-08-01 17:48 | byte / 1 |
| 8 | `TaiwanStockDayTrading`(35) | 4,409,702 | 2014-01-06 → 2026-07-31 | 2,397 stock_id | (stock_id,date) | 2026-08-01 17:47 | byte / 1 |
| 9 | `CnnFearGreedIndex`(85) | 3,954 | 2011-01-03 → 2026-07-31 | — | (date) | 2026-08-01 18:19 | byte / 1 |
| 10 | `TaiwanBusinessIndicator`(93) | **534** | 1982-01-01 → **2026-06-01** | — | (date) | 2026-08-01 17:45 | **cadence** / 1 |
| 11 | `TaiwanFuturesInstitutionalInvestors`(44) | 112,350 | 2018-06-05 → 2026-07-31 | 26 futures_id | (futures_id,date,institutional_investors) | 2026-08-01 17:45 | byte / 1 |
| 12 | `TaiwanFuturesOpenInterestLargeTraders`(38) | 1,912,932 | 2007-01-02 → 2026-07-31 | 484 futures_id | (futures_id,date,name,contract_type) | 2026-08-01 17:46 | byte / 1 |
| 13 | `TaiwanStockTotalInstitutionalInvestors`(69) | 26,805 | 2004-04-07 → 2026-07-31 | **7** name | (date,name) | 2026-08-01 17:55 | byte / 1 |
| 14 | `TaiwanStockTotalMarginPurchaseShortSale`(23) | 18,813 | 2001-01-03 → 2026-07-31 | **3** name | (date,name) | 2026-08-01 17:55 | byte / 1 |
| 15 | `TaiwanTotalExchangeMarginMaintenance`(86) | 6,264 | 2001-01-05 → 2026-07-31 | — | (date) | 2026-08-01 17:55 | byte / 1 |
| 16 | `TaiwanStockGovernmentBankBuySell`(51) | 14,183,538 | 2021-07-01 → 2026-07-31 | 2,854 stock_id | **7 欄 PK（含 buy_amount/sell_amount/buy/sell）** | 2026-08-01 17:48 | byte / 1 |
| 17 | `TaiwanStockHoldingSharesPer`(53) | 21,159,221 | 2010-01-29 → 2026-07-31 | 4,200 stock_id | (stock_id,date,HoldingSharesLevel) | 2026-08-01 17:48 | byte / 1 |
| 18 | `TaiwanStockSecuritiesLending`(77) | 748,994 | 2003-11-11 → 2026-07-31 | 2,169 stock_id | (stock_id,date) | 2026-08-01 18:40 | byte / 1 |
| 19 | `TaiwanStockBalanceSheet`(31) | 5,798,061 | 2012-12-31 → **2026-06-30** | 2,419 stock_id | (stock_id,date,type) | 2026-08-01 17:46 | byte / 1 |
| 20 | `TaiwanStockMonthRevenue`(83) | 476,578 | 2002-02-01 → **2026-07-01** | 2,496 stock_id | (stock_id,country,date) | 2026-08-01 17:50 | byte / 1 |
| 21 | `TaiwanStockMarketValue`(70) | 8,597,042 | 2004-02-12 → 2026-07-31 | 2,988 stock_id | (stock_id,date) | 2026-08-01 17:49 | byte / 1 |
| 22 | `TaiwanStockPER`(17) | 7,622,812 | 2005-09-02 → 2026-07-31 | 2,134 stock_id | (stock_id,date) | 2026-08-01 17:54 | byte / 1 |
| 23 | `TaiwanStock10Year`(**30**，§1.3 新增) | 5,402,871 | 2011-01-24 → 2026-07-31 | 2,026 stock_id | (stock_id,date) | 2026-08-01 17:46 | byte / 1 |

**「是否 live 更新」判準＝`data_audit_log` 最近一筆是否落在最近一輪每日維護（2026-08-01 17:45–18:40）**。結論：**22 表 live、1 表（TRI）不 live**。

---

## §2 TRI 專節（最高槓桿；寫到可直接圈）

### 2.1 (a) 現況親驗

| 項 | 值 | 取得方式 |
|---|---|---|
| 列數 | **10,830** | `SELECT count(*)` |
| 維度 | **2 個 `stock_id`**：`TAIEX`（5,788 列、2003-01-02→2026-07-09）／`TPEx`（5,042 列、2006-01-02→2026-07-09） | `GROUP BY stock_id` |
| 欄 | `stock_id varchar(255)`, `date date`, `price numeric(20,6)` | `pg_attribute` |
| PK | `PRIMARY KEY (stock_id, date)` | `pg_constraint` |
| 時點欄 | **僅 `date`**；表內**無**公告欄／建立時點欄 | 同上 |
| 值域 | TAIEX 4,140.34 → 109,231.58；TPEx 60.28 → 832.88 | `min/max(price)` |
| **是否 live 更新** | **否**。`data_audit_log` 最後 2 列＝`2026-06-20 13:10`（`data_id=TAIEX` 5,774 列／`TPEx` 5,028 列，`action=upsert`）。其後 **14 個交易日（2026-06-22→2026-07-09）之列存在但無任何 audit 列**；2026-07-09 之後停滯。log 本身覆蓋 2026-06-16→2026-08-01 連續（261,483 列），故非 log 被裁切 | `data_audit_log` 查詢 |
| 落後幅度 | `TaiwanStockTradingDate` 之 `max(date)=2026-12-31`；(2026-07-09, 2026-07-31] 區間有 **16 個交易日**是 TRI 沒有的 | 兩表對查 |
| 同步路徑 | `dataset_catalog`：`fetch_mode=by-date`、**`data_id_required=t`**、`reconcile_scope=by-dim-id`、`n_dimension_ids=2`、`data_id_source=doc`；`src/augur/ingestion/sync.py:177` 之 `_DOC_SEED_IDS["TaiwanStockTotalReturnIndex"]=["TAIEX","TPEx"]`。每日維護走 `sync_all_by_date`（`sync.py:565`），對需 `data_id` 之 dataset 回 `not-by-date-capable` 而略過 | catalog＋原始碼親讀 |

> ⚠ **兩件本節無法定案者**（列 §6）：(i) 06-22→07-09 之 14 個交易日**由何路徑寫入而未留 audit 列**，本輪未查明——屬 provenance 缺口；(ii) TRI 是否「應」進每日增量鏈，屬維運決策，非本件射程。

### 2.2 (b) 現有 binding 列

| binding_id | concept_key | source_table | source_column | channel_role | mapping_status | superseded_at |
|---|---|---|---|---|---|---|
| **78** | **NULL** | `TaiwanStockTotalReturnIndex` | NULL | `observation` | **`unmapped`** | NULL |

`provenance` 現值：`{"seed_basis":"reports/wm3536_vendor_registry_plan_20260802.md §4 種子(G0 格3 照案)","granularity":"table_level(§9 Q5 表級暫登;欄位級=column_catalog 待後批)","seed_source":"dataset_catalog","vendor_source":"finmind","catalog_category":"TW-Technical"}`

### 2.3 **重大發現：9 處中 4 處根本不是在讀 TRI，而是在讀交易日曆**

逐處親讀（`sed` 引原文，非推測）：

| # | 位置 | 取用欄 | 真實用途 | 應繫概念 |
|---|---|---|---|---|
| 1 | `scripts/build_daily_direction_features.py:49` | `date, price` | 建 TAIEX 指數序列算報酬 | **TRI 新概念** |
| 2 | `scripts/build_direction_stack_monthly.py:59` | **`date` only** → `cal = [r[0] …]`（變數名自陳 `cal`） | **交易日曆** | **`tw.trading_calendar`（binding 4，已 mapped）** |
| 3 | `scripts/build_direction_stack_monthly.py:80` | `date, price` → `mk[…"mpx"]` | 市場指數水準 | TRI 新概念 |
| 4 | `scripts/build_market_direction_features.py:53` | `date, price::float8` | 算 `mkt_ret_1/5/20/60`、`mkt_vol_20`、`mkt_dist_high_60` | TRI 新概念 |
| 5 | `scripts/run_arena_replay.py:84` | **`date` only** → `cal = […]` | **交易日曆** | `tw.trading_calendar` |
| 6 | `scripts/run_arena_replay.py:103` | `date, price` → `taiex` | 市場指數水準 | TRI 新概念 |
| 7 | `scripts/run_arena_round.py:96` | **`date` only** → `month_days`；`h_fires = month_days[0]==as_of`（月首交易日判定） | **交易日曆** | `tw.trading_calendar` |
| 8 | `scripts/run_arena_round.py:112` | **`price` only** → `series["TAIEX"]` | 市場指數水準 | TRI 新概念 |
| 9 | `scripts/train_daily_direction.py:82` | **`date` only** → `return [r[0] …]` | **交易日曆** | `tw.trading_calendar` |

**日曆等價性親驗（此為「應改繫 `tw.trading_calendar`」之機械依據，非語意推測）**：

```sql
WITH tri AS (SELECT DISTINCT date FROM "TaiwanStockTotalReturnIndex" WHERE stock_id='TAIEX'),
     cal AS (SELECT DISTINCT date FROM "TaiwanStockTradingDate"
              WHERE date BETWEEN DATE '2003-01-02' AND DATE '2026-07-09')
SELECT (SELECT count(*) FROM tri), (SELECT count(*) FROM cal),
       (SELECT count(*) FROM tri t WHERE NOT EXISTS(SELECT 1 FROM cal c WHERE c.date=t.date)),
       (SELECT count(*) FROM cal c WHERE NOT EXISTS(SELECT 1 FROM tri t WHERE t.date=c.date));
-- → 5788 | 5788 | 0 | 0     （雙向差集皆 0）
```

### 2.4 連帶效應：那 4 處目前吃的是落後 16 個交易日的錯日曆

TRI 停在 2026-07-09；`TaiwanStockTradingDate` 在 (07-09, 07-31] 另有 16 個交易日。⇒ `run_arena_round`（**cron 20:00 熱路徑**）之 `h_fires`（月首交易日出手判定）與 `train_daily_direction`／`run_arena_replay`／`build_direction_stack_monthly` 之日曆，**現況即為錯的**。

> ⚠ **這使「絞殺＝行為零變更」在此 4 處不可能成立**：改繫 `tw.trading_calendar` 後日曆會多 16 天（**且是改對**），影子比對必判 `red`。此為 §6 Q-R3 之待裁點——**AI 不代裁「改對算不算行為變更」**。

### 2.5 (c) 建議之世界概念——`tw.market_total_return_index`（WM.36 七欄逐欄）

| # | WM.36 欄 | 草擬值 | 為何如此（依據） |
|---|---|---|---|
| 1 | 世界概念 | `tw.market_total_return_index` | 沿既有六概念之慣例：`tw.` 市場前綴＋小寫底線領域名詞（比照 `tw.trading_calendar`／`tw.daily_bar`）。**不用 `tw.taiex`**——TAIEX 是 series 識別碼，WM.36 明列為禁止繫結之「來源位置字面」 |
| 2 | 歸類（閉集） | **`quantity`** | WM.8「量」；`price` 為一個隨時間演進之指數水準值，非事件、非實體、非關係。（對照：`tw.daily_bar` seed 因原文雙寫「事件／狀態」而暫置 `event` 並自書「採認時校正」；本概念原文無此雙寫，故無同型歧義） |
| 3 | 通道映射 | binding **78**（`TaiwanStockTotalReturnIndex`, `observation`）；`source_column` 留 NULL（表級暫登，同既有 10 列） | 全庫唯一供應此事實之表（98 個 binding 逐列檢視，無第二候選） |
| 4 | 權威表徵指定 | **78** | WM.14「恰解析至一」；單通道，無裁量空間（同 `tw.trading_calendar`／`tw.delisting` 之形） |
| 5 | 時間屬性雙宣告 | ts=**`交易日`**；knowability=**`收盤後當日可得（TWSE 盤後發布）`**；cross_market_axis=**NULL**（本域市場，A.35 第三項不適用） | ts 取 A.35 開放列舉之「交易日」；日期集合與 `TaiwanStockTradingDate` 全等（§2.3）為「本表時間鍵即本域交易日」之機械佐證。knowability 為 [I] 保守宣告——**表內無公告欄可定錨**，見證偽條件 |
| 6 | provenance | `{"seed_basis":…（承襲 binding 78 現值）, "adopted_basis":"reports/wm_channel_registration_draft_20260803.md §2", "資料現況":"2026-08-03 親驗 10,830 列／2 series／max(date)=2026-07-09（非 live，last audit 2026-06-20）", "已知缺口":"14 個交易日（2026-06-22→07-09）無 audit 列；停滯於 07-09"}` | WM.36 欄 6；**停滯與 provenance 缺口必須隨卷揭露**，否則下游會把「表只到 07-09」誤讀為「市場只開到 07-09」 |
| 7 | 定案性述語 | **`當日值於次一交易日收盤後定案`** | A.37 三例示之第一例逐字；`dataset_catalog.finalize_lag_days=1`、`attestation_mode=byte`（逐 byte 對帳）與之相容 |
| — | `conflict_set_ref` | **NULL** | 單通道，WM.37「多來源供應時預留衝突保存」不觸發 |

**證偽條件**：(i) Steward 認 TAIEX／TPEx 為**兩個**世界事實（兩個市場）⇒ 須拆為兩概念，但表級登錄無法承載列篩選 ⇒ 落入 Q-R2；(ii) 若欄 2 由 `quantity` 校正為 `state` ⇒ 重審；(iii) 若「非 live」被認定為通道不合格（WM.35 得保存／對帳／追溯，未就停滯設判準）⇒ 本概念改列「不採認（過渡）」。

### 2.6 (d) 與現有六概念之重疊判斷

- **與 `tw.trading_calendar` 部分重疊**：TRI 之 `date` 集合＝該概念之現有權威候選（binding 4）之 `date` 集合（§2.3 親驗）。**但不應把 binding 78 加掛為 `tw.trading_calendar` 之第二通道**——TRI 是**殘缺的**日曆（停在 07-09、且無未來日；`TaiwanStockTradingDate` 有 103 個未來日至 2026-12-31）；加掛後若權威誤指 78，全系統日曆會回退。建議：78 只繫新概念，4 處日曆用途**改繫既有 `tw.trading_calendar`**。
- **與 `tw.daily_bar` 不重疊**：`tw.daily_bar` 為個股日 K（`TaiwanStockPrice`／`PriceAdj`，3,127–55,674 個 `stock_id`）；TRI 為市場級指數（2 個），實體層級不同。
- 與其餘四概念（`delisting`／`roster_membership`／`corporate_action.ex_dividend`／`fx.twd_usd`）無交集。

### 2.7 TRI 解鎖之 5 檔／9 處逐處結論

| 檔 | 該檔 TRI 處 | 該檔其他缺通道表 | 登 TRI 後是否全綠 |
|---|---|---|---|
| `scripts/run_arena_replay.py` | 2（:84 曆／:103 價） | 無（另 1 處 PriceAdj 已 mapped） | **✅ 全綠**（3/3 處有通道） |
| `scripts/run_arena_round.py` | 2（:96 曆／:112 價） | 無（另 2 處 PriceAdj 已 mapped） | **✅ 全綠**（4/4） |
| `scripts/train_daily_direction.py` | 1（:82 曆） | 無（另 1 處 PriceAdj） | **✅ 全綠**（2/2） |
| `scripts/build_direction_stack_monthly.py` | 2（:59 曆／:80 價） | `TaiwanStockInstitutionalInvestorsBuySell`(:101) | ❌ 仍差 1 表（需併登 #2 概念） |
| `scripts/build_daily_direction_features.py` | 1（:49 價） | ShortSaleBalances／DayTrading／IIBS／MarginPurchaseShortSale／Shareholding（5 表） | ❌ 仍差 5 表 |
| `scripts/build_market_direction_features.py` | 1（:53 價） | 另 8 表全缺 | ❌ 仍差 8 表 |

⇒ **`wm_m3_batch1_target_scoping` §2.4 之「解鎖 5 檔」須修正為「解鎖 3 檔（replay／round／train_daily）」**；`build_direction_stack_monthly` 需同時登 IIBS（本件 #2）才全綠，另兩檔需整批。**若同時登 TRI ＋ IIBS 兩概念 ⇒ 解鎖 4 檔／11 處**（stack_monthly 之 4 處一併轉綠）。

**A 類外之 TRI 消費（誠實揭露，不在 M3 A 類射程但同表）**：`scripts/verify_regime_timing.py:42`（date+price）、`scripts/verify_arena_watchlist.py:131`（date only，**UNCLASSIFIED**）、`scripts/train_market_direction.py:88`（date+price，**UNCLASSIFIED**）。⇒ TRI repo 全量 **12 處／9 檔**。

---

## §3 其餘 22 表逐表備料（依 §2.4 之 A 類處數序）

> 格式：**表（binding）→ 建議概念｜七欄要點｜為何如此｜重疊判斷**。所有列數／期間／PK 見 §1.4 總表，不重複。
> `channel_role` 除特別註明外一律沿現值 `observation`；`source_column` 一律留 NULL（表級暫登，比照既有 10 列，見 §6 Q-R2）。

### 3.1 `TaiwanStockInstitutionalInvestorsBuySell`（binding 60）｜A 類 4 處／4 檔

- **概念**：`tw.institutional_net_flow.stock`
- **category**＝`quantity`｜每日每法人別之買進／賣出金額，為量（WM.8）。
- **ts_semantics**＝`交易日`｜A.35 列舉；TWSE 盤後公布當日買賣超。
- **knowability_rule**＝`收盤後當日可得（TWSE 盤後公布）`｜`finalize_lag_days=1`、`attestation_mode=byte`。表內無公告欄可定錨 ⇒ 本宣告為法定公開規則型（WM.31(b) 允許之第二型）。
- **finality_predicate**＝`當日值於次一交易日收盤後定案`（A.37 例示一）。
- **conflict_set_ref**＝**指向 `tw.institutional_net_flow.market`**（見 §5 合併候選 M1）｜市場級表為同一底層流量之聚合，WM.37「多來源供應時預留衝突保存」之落點。
- **cross_market_axis**＝NULL。
- **重疊**：與現有六概念無交集。⚠ **多值表**：`name` 欄（法人別）為列篩選維度——`features/phase.py:52` 與 `chip.py:68` 皆以 `sum(buy)-sum(sell)` 全法人合計消費（未內嵌 `name` 字面，**此表反而是本批少數不觸 Q-R2 者**）；但 `build_direction_stack_monthly.py:101` 亦同型合計 ⇒ 三個消費點皆合計，**登錄後可真正解除直綁**。
- **維度異常（誠實）**：`count(DISTINCT stock_id)=43,906`，遠大於 `TaiwanStockInfo` 之 3,128——含權證等非普通股標的。屬**宇宙選擇**問題，非通道問題（同 Annex F §2.1 對 `TaiwanStockPrice` 之判讀）。

### 3.2 `TaiwanDailyShortSaleBalances`（binding 56）｜A 類 2 處／2 檔 — **一表供兩世界事實**

親驗（2026-07-31、`ShortSaleTodayBalance>0`）：

| stock_id | `MarginPurchaseShortSale.ShortSaleTodayBalance` | `DailyShortSaleBalances.MarginShortSalesCurrentDayBalance` | `…SBLShortSalesCurrentDayBalance` |
|---|---|---|---|
| 00401A | 2 | **2,000** | 3,121,000 |
| 00403A | 1,482 | **1,482,000** | 316,116,000 |
| 00405A | 699 | **699,000** | 42,118,000 |

⇒ **融券餘額之兩通道為同一世界事實、單位差 ×1000（張 vs 股）**。共同鍵 48,320 列中 24,068 列「數值不同」（`IS DISTINCT FROM` 口徑）＝**單位差所致，非資料衝突**。

- **概念 A**：`tw.margin_trading_balance.stock`（融資融券餘額）——**兩通道**：binding **49**（`TaiwanStockMarginPurchaseShortSale`，融資＋融券完整，張）＋ binding **56**（融券段，股）。權威建議 **49**（涵蓋融資與融券，且 `chip.py:75` 之融資使用率需 `MarginPurchaseLimit`，僅 49 有）。`conflict_set_ref`＝`單位不對等：49=張、56=股（×1000）；擇用規則見 WM.15 單一宣告`。
- **概念 B**：`tw.sbl_short_balance.stock`（借券賣出餘額）——binding 56 之 SBL 欄群；**49 無此欄**。
- ⚠ **形制**：一個 binding 列只有一個 `concept_key` 欄 ⇒ **56 服務兩概念須新增第二個 binding 列**（先例＝`TaiwanStockDelisting` 之 binding 2／3）。範本見 §7.3。
- ⚠ **跨概念查詢**：`scripts/build_daily_direction_features.py:130-134` 之
  `coalesce("MarginShortSalesCurrentDayBalance",0)+coalesce("SBLShortSalesCurrentDayBalance",0)`
  **同時跨兩個概念**（融券＋借券合計）。改繫概念鍵時該處無單一概念可解析 ⇒ 列 §6 Q-R4。
- **七欄**（兩概念共通）：category=`state`（餘額＝時點存量，非流量）｜ts=`交易日`｜knowability=`收盤後當日可得`｜finality=`當日值於次一交易日收盤後定案`｜cross_market_axis=NULL。

### 3.3 `TaiwanStockMarginPurchaseShortSale`（binding 49）｜A 類 2 處／2 檔

見 §3.2 概念 A。**建議為 `tw.margin_trading_balance.stock` 之權威通道**。

### 3.4 `TaiwanStockShareholding`（binding 62）｜A 類 2 處／2 檔

- **概念**：`tw.foreign_ownership.stock`
- category=`state`｜外資持股比率為時點存量。
- ts=`交易日`｜TWSE 每交易日發布外資持股表。
- knowability=**⚠ 兩讀並存，本件不定案**：`dataset_catalog.anti_leakage_note` 載「as-of 欄: `RecentlyDeclareDate`」；但親驗 `date=2026-07-31` 之列，其 `RecentlyDeclareDate` 落在 **2026-05-12→2026-05-15**（≈2.5 個月前）⇒ 該欄看來是「標的最近一次申報異動日」（**內容欄**），非「本列自何時可知」（**可知錨**）。兩讀：(甲) knowability=`收盤後當日可得`、`RecentlyDeclareDate` 為內容；(乙) knowability 錨於 `RecentlyDeclareDate`，則 07-31 之列須到 05-15 後才可知（**恆真、無鑑別力**）。⇒ **§6 Q-R5**。
- finality=`當日值於次一交易日收盤後定案`（採甲讀時）。
- **重疊**：與 `tw.roster_membership` 無交集（後者為成員資格，本概念為持股比率）。

### 3.5 `TaiwanOptionDaily`（binding 43）｜A 類 2 處／2 檔

- **概念**：`tw.option_daily_quote`
- category=`quantity`｜日級契約報價與未平倉量。
- ts=`交易日`｜knowability=`收盤後當日可得`｜finality=`當日值於次一交易日收盤後定案`｜cross_market_axis=NULL。
- ⚠ **多值表最嚴重者**：`scripts/derive_market_iv.py:57-60` 內嵌 **`option_id='TXO'` ＋ `trading_session='position'`** 兩個列篩選字面；`build_market_direction_features.py:79` 同型。**登錄後這兩個字面仍在** ⇒ Q-R2。
- ⚠ **PK 病理**：`PRIMARY KEY (date, option_id, contract_date, strike_price, call_put, open, max, min, close, volume, settlement_price, open_interest, trading_session)`＝**13 欄、值欄入 PK**。同一契約同一日若供應商修正報價，會**新增一列而非覆蓋**（無真實鍵）⇒ 該通道之 `attestation_mode=byte` 與此形制之相容性、以及是否需 `conflict_set_ref`，列 §6 Q-R7。

### 3.6 `TaiwanStockFinancialStatements`（binding 68）｜A 類 2 處／2 檔

- **概念**：`tw.financial_statement.income`（綜合損益表；long form `type/value`）
- category=`event`｜「財報揭露」為世界事件（對照 Annex F-2 `CorporateAction.除權息` 亦歸事件）。**替代讀法** `state`（期末財務狀態）並存 ⇒ 附註於圈選單。
- ts=**`資料所屬期末（季底）`**｜A.35 列舉之第二型；親驗 `date` 值僅為 `2026-03-31`／`2026-06-30` 等季底日。
- knowability=**`季底 +45 日（Q1/Q2/Q3）／+90 日（年報 Q4）`**｜**此規則 repo 內已存在且已在生產使用**：`src/augur/features/release_lag.py`（`FIN_LAG_QUARTER=45`、`FIN_LAG_ANNUAL=90`、`financial_released()`），消費者＝`features/fundamentals.py:35`、`features/margin_cycle.py:47`。**登錄＝把已在 code 裡的可知規則搬進 Registry 欄 5**，非新創。
- finality=**`季報值於法定申報期屆滿後定案`**（A.37 例示二逐字）。
- ⚠ **可知錨不在通道內**：表欄僅 `date, stock_id, type, value, origin_name`——**無公告日欄**。WM.31(b) 允許「法定公開規則」型宣告，但 Annex F 呈案 **Q4** 正是問「可知規則錨是否必須存在於該權威通道之表內」。⇒ 同一問題適用本概念，列 §6 Q-R5。
- ⚠ **已知缺口（`release_lag.py` docstring 自陳）**：金融保險／證券／期貨業法定 Q1/Q3 為 **60 日**（證交法 §36 但書），現行 45 日對其低估滯後。docstring 自陳「現況無生產消費者觸發」。登錄時**須隨 provenance 揭露**，否則 Registry 會把一個已知不精確的規則洗成權威。

### 3.7 `TaiwanStockBalanceSheet`（binding 31）｜A 類 1 處／1 檔

- **概念**：`tw.financial_statement.balance`（資產負債表）
- 七欄與 §3.6 逐欄相同（同 ts／同 knowability／同 finality），僅概念名與 binding 不同。
- **重疊判斷**：與 §3.6 **不合併**——損益表與資產負債表是兩份不同報表（兩個世界事實），非同一事實之兩觀測；且 `features/fundamentals.py:23/28` 兩支 SQL 各取各表之 `type` 集合（NetIncome… vs Equity/Liabilities/TotalAssets）。**合併候選 M3 仍列於 §5 供 Steward 裁**。

### 3.8 `TaiwanStockDayTrading`（binding 35）｜A 類 1 處

- **概念**：`tw.day_trading.stock`｜category=`quantity`｜ts=`交易日`｜knowability=`收盤後當日可得`｜finality=`當日值於次一交易日收盤後定案`｜cross_market_axis=NULL。
- 消費：`build_daily_direction_features.py:136`（`(BuyAmount+SellAmount)/2`）。無列篩選字面 ⇒ **登錄後可真正解除直綁**。

### 3.9 `CnnFearGreedIndex`（binding 85）｜A 類 1 處 — **本批唯一非本域市場之表**

- **概念**：**`us.market_sentiment.fear_greed`**（**不用 `tw.` 前綴**）
- **依據**：`dataset_catalog.category='Global Economic Data'`（親驗）；CNN Fear & Greed 為美股市場情緒指標。既有六概念全為 `tw.`，本概念是**第一個非 `tw.` 概念** ⇒ 命名空間慣例之擴充，請 Steward 一併確認（§6 Q-R8）。
- category=`state`｜0–100 之情緒狀態＋`fear_greed_emotion` 分級字串。
- ts=`交易日`（**美股**交易日）。
- **cross_market_axis**＝**必填、且為本批唯一必填者**｜A.35 第三項逐字：「凡通道之時間鍵為**外國市場交易日**者，**必須**宣告其對映至本域交易日軸之規則（含可知性之對映，如外國 t-1 收盤於本域 t 日之可知地位）；未宣告者依保守解釋不可用於本域 as-of 推理，**禁止下層以『同日即對齊』隱含假設消費**。」
  - **草擬值**：`美股交易日 t 之值於台股交易日 t+1 可知（美東收盤 16:00 ET ≈ 台北次日 04:00；不得以同日對齊消費）`。
  - ⚠ **現況即為 A.35 所禁之形**：`scripts/build_market_direction_features.py:73` 以 `date` 直接與台股 `date` 對齊（同日）。⇒ 登錄後該處**必然行為變更**（與 §2.4 之 TRI 日曆同型），列 §6 Q-R3。
  - ⚠ 既有六概念之 `cross_market_axis` **全為 NULL**（親驗）；`tw.fx.twd_usd` 之 `fred_series` 通道亦屬外國資料庫（A.36 揭露之時間模型不對稱），其 NULL 是否為缺漏，非本件射程。
- knowability=`美股收盤後可得，於本域次一交易日方可 as-of 消費`｜finality=`未宣告`（WM.32 缺省推定 non-final；CNN 指標無公告定案機制可證）。

### 3.10 `TaiwanBusinessIndicator`（binding 93）｜A 類 1 處

- **概念**：`tw.business_cycle_indicator`｜category=`state`（景氣狀態：領先／同時／落後指標＋對策信號燈號）。
- ts=**`資料所屬期末（月）`**｜親驗 534 列、`max(date)=2026-06-01`、月頻。
- knowability=**`待定錨`**｜表欄僅 `date` ＋七個指標值 ＋ `monitoring_color`，**無發布日欄**；國發會發布時點未在庫內可證。**WM.31 明文：標記「待定錨」者視同未宣告，該通道之資料推定不可用於任何 as-of 推理。**
  - ⚠ 但 `scripts/build_market_direction_features.py:100` 與 `scripts/verify_regime_timing.py:42` **現正消費之**。⇒ 登錄「待定錨」＝把一個**現行 anti-leakage 缺口**顯性化。這是登錄的價值，也是它會擋住 M3 的原因。列 §6 Q-R5。
- finality=`未宣告`｜`attestation_mode=cadence`（本批唯一非 byte）。

### 3.11 `TaiwanFuturesInstitutionalInvestors`（binding 44）｜A 類 1 處

- **概念**：`tw.futures.institutional_position`｜category=`quantity`｜ts=`交易日`｜knowability=`收盤後當日可得`｜finality=`當日值於次一交易日收盤後定案`。
- ⚠ 多值表：26 個 `futures_id` ×「三大法人別」；`build_market_direction_features.py:69` 之列篩選字面未逐字檢查（本輪只親讀 SQL 行首），列為殘項。

### 3.12 `TaiwanFuturesOpenInterestLargeTraders`（binding 38）｜A 類 1 處

- **概念**：`tw.futures.large_trader_open_interest`｜category=`state`（未平倉部位＝時點存量）｜ts=`交易日`｜knowability=`收盤後當日可得`｜finality=`當日值於次一交易日收盤後定案`。
- ⚠ 多值表：484 個 `futures_id` × `contract_type` × `name`。

### 3.13 `TaiwanStockTotalInstitutionalInvestors`（binding 69）｜A 類 1 處

- **概念**：`tw.institutional_net_flow.market`｜七欄與 §3.1 同型，僅實體層級為「市場」而非「個股」。
- 親驗 `name` 值域（7）：`total`／`Foreign_Investor`／`Investment_Trust`／`Dealer_self`／`Dealer_Hedging`／`Dealer`／`Foreign_Dealer_Self`。
- **重疊**：與 §3.1 為**同一底層流量之兩種粒度** ⇒ **合併候選 M1**（§5）。**本件建議分立**，理由：`resolve()` 只回一個 binding，若併為一概念，市場級消費點會被解析到個股表（或反之）＝機械錯誤。

### 3.14 `TaiwanStockTotalMarginPurchaseShortSale`（binding 23）｜A 類 1 處

- **概念**：`tw.margin_trading_balance.market`｜七欄同 §3.2 概念 A，實體層級為市場。
- 親驗 `name` 值域（3）：`MarginPurchase`／`MarginPurchaseMoney`／`ShortSale`。
- **重疊**：與 §3.3 為兩粒度 ⇒ **合併候選 M2**（§5）；建議分立，理由同 §3.13。

### 3.15 `TaiwanTotalExchangeMarginMaintenance`（binding 86）｜A 類 1 處

- **概念**：`tw.margin_maintenance_ratio.market`｜category=`quantity`（整體市場融資維持率 %）｜ts=`交易日`｜knowability=`收盤後當日可得`｜finality=`當日值於次一交易日收盤後定案`。
- 單值表（`date` 為 PK、僅一個指標欄）⇒ **無 Q-R2 問題**，是本批最乾淨的登錄項之一。

### 3.16 `TaiwanStockGovernmentBankBuySell`（binding 51）｜A 類 1 處

- **概念**：`tw.government_bank_flow.stock`｜category=`quantity`｜ts=`交易日`｜knowability=`收盤後當日可得`｜finality=`當日值於次一交易日收盤後定案`。
- ⚠ **PK 病理**：`PRIMARY KEY (date, stock_id, buy_amount, sell_amount, buy, sell, bank_name)`＝金額值欄入 PK ⇒ 同 §3.5 之形（供應商修正值會新增列）。
- ⚠ **消費端已知名實不符**（`features/chip.py:105-111` 自陳，稽核 2026-07-04 決 7）：特徵名為「60d」實為「最近 ≤60 個官股有交易之**事件日**」（`LIMIT 60`、無日期下界）⇒ 稀疏股窗跨度可達數年。**與登錄無關但與 provenance 有關**，建議隨卷揭露。

### 3.17 `TaiwanStockHoldingSharesPer`（binding 53）｜A 類 1 處

- **概念**：`tw.holder_dispersion.stock`（集保股權分散表）｜category=`state`。
- ts=**`資料所屬期末（集保週五快照）`**。
- knowability=**`快照日 +7 日（TDCC 延後公布；保守取上限）`**｜**repo 內已有**：`src/augur/features/release_lag.py` 之 `HOLDINGS_LAG_DAYS = 7`，docstring 自陳「2026-07-11 審計 1A 拍板；無發布日欄可查，寧晚勿早 #8；待 probe 公布時刻可精修」。消費端 `features/chip.py:83-90` 已以 `holdings_visible_cutoff(panel)` 落地。⇒ 同 §3.6，**登錄＝把 code 裡的規則搬進 Registry**。
- finality=`快照值於公布日後定案`（A.37 形式；**非 A.37 三例示之逐字**，屬新述語 ⇒ 請 Steward 確認形式合格）。
- ⚠ 多值表：`HoldingSharesLevel` 級距；`chip.py:88` 內嵌 `'more than 1,000,001'`、`audit/field_correlation.py` 另內嵌 `'1-999'`／`'total'` ⇒ Q-R2。

### 3.18 `TaiwanStockSecuritiesLending`（binding 77）｜A 類 1 處

- **概念**：`tw.securities_lending.stock`｜category=**`event`**（逐筆借券成交紀錄，非時點存量——親驗 `transaction_type` 值域：`議借` 586,785／`競價` 162,141／`定價` 68，且同股同日可多筆）。
- ts=`交易日`｜knowability=`收盤後當日可得`｜finality=`當日值於次一交易日收盤後定案`。
- ⚠ **消費端已知名實不符**（`features/chip.py:96-101` 自陳，稽核 2026-07-04 決 8）：特徵名為「30d」實為「最近 **100 筆**借券成交紀錄之均」、無日期下界、窗跨度中位 ≈1.5 年；且來源為議借成交 `fee_rate`，非放空成本嚴格語意。建議隨 provenance 揭露。
- **重疊**：與 §3.2 概念 B（`tw.sbl_short_balance.stock`）**不同**——本概念為**借券成交事件**，B 為**借券賣出餘額存量**。

### 3.19 `TaiwanStockMonthRevenue`（binding 83）｜A 類 1 處

- **概念**：`tw.monthly_revenue.stock`｜category=`event`（月營收公告）。
- ts=**`資料所屬期末（營收所屬月）`**——⚠ **精確語意須注意**：`release_lag.py` docstring 自陳「`date` 實＝**公告月**（資料月+1；DB 實證 474,246/474,246 列 `date` 恆＝資料月+1）」。故 `date` 既非純期末亦非公告日。**建議欄 5 逐字寫**：`date = 公告月首日（＝營收所屬月 + 1 月）`。
- knowability=**`該公告月 15 日（法定 10 日 + buffer，保守）`**｜`release_lag.REVENUE_DAY = 15`、`revenue_released()`；消費者＝`features/panel.py:64`（`LIMIT 16` 註解自陳「過發布日 gate 剔 ≤2 未公告月後仍 ≥13 供 YoY」）。
- finality=`營收值於公告月 15 日後定案`（A.37 形式）。
- ⚠ **`create_time` 不足以承載可知規則**：`dataset_catalog.anti_leakage_note` 標「as-of 欄: `create_time`」，但親驗 **430,157／476,578 列為 NULL（90.3%）**；有值者（如 `date=2026-07-01`）分佈於 07-01→07-29 共數十個相異值。⇒ 現行 code **並未**使用 `create_time`，而是用日期算術。登錄時應寫「法定公開規則型」而非「顯式時點欄型」，並於 provenance 揭露 90.3% NULL。

### 3.20 `TaiwanStockMarketValue`（binding 70）｜A 類 1 處

- **概念**：`tw.market_capitalization.stock`｜category=`quantity`｜ts=`交易日`｜knowability=`收盤後當日可得`｜finality=`當日值於次一交易日收盤後定案`。
- 單一值欄（`market_value`）＋(stock_id,date) PK ⇒ 乾淨，無 Q-R2 問題。

### 3.21 `TaiwanStockPER`（binding 17）｜A 類 1 處

- **概念**：`tw.valuation_ratio.stock`（PER／PBR／殖利率三值同表同鍵）｜category=`quantity`｜ts=`交易日`｜knowability=`收盤後當日可得`｜finality=`當日值於次一交易日收盤後定案`。
- ⚠ **髒值須隨 provenance 揭露**（既有記憶：`PER=0` 為哨兵值、佔比顯著；`PER=-1` 僅 2 列）。**本輪未重驗該比例**（列為殘項）——登錄前應以一次 `GROUP BY` 實查後填入 provenance，避免把哨兵值洗成權威量。

### 3.22 `TaiwanStock10Year`（binding 30）— **§1.3 補入之第 23 表**

- **概念**：`tw.long_term_price_average.stock`
- **channel_role**＝⚠ **建議由現值 `observation` 改為 `derived`**｜`docs/datasets_zh.md:135` 明載「**十年線（月均價）**」、`docs/finmind-references/datasets.md:58` 載「十年線」。⇒ 這是**移動平均之衍生量**，非原始市場觀測，形制同 `TaiwanStockPriceAdj`(binding 81) 之 `derived`（WM.15 衍生觀測）。
- category=`quantity`｜ts=`交易日`｜knowability=`收盤後當日可得`｜finality=**`未宣告`**（移動平均之定案性依賴底層價之定案性與窗長，本件無法定案 ⇒ WM.32 缺省 non-final）。
- ⚠ **消費端把它當原始價用**：`features/valuation.py:37-41` 之註解自陳「與 raw-basis 之 `TaiwanStock10Year` 同 point-in-time 口徑」——把它與 `TaiwanStockPrice` 並列為 raw-basis。若 docs 之「月均價」為真，則此處存在**口徑理解落差**。⇒ 列 §6 Q-R6（含歸類與是否納 M3 射程）。
- **重疊**：與 `tw.daily_bar` 為不同粒度／不同處理（日 K vs 十年月均線），**不併入**。

---

## §4 二十三表 → 建議概念對照總表

| # | 建議 concept_key | category | binding | 供應表 | 是否多值表（Q-R2） | 備註 |
|---|---|---|---|---|---|---|
| 1 | `tw.market_total_return_index` | quantity | **78** | TotalReturnIndex | **是**（TAIEX/TPEx） | §2；表已停滯 |
| 2 | `tw.institutional_net_flow.stock` | quantity | 60 | IIBS | 是（name），但三消費點皆合計 ⇒ **不觸** | 合併候選 M1 |
| 3 | `tw.institutional_net_flow.market` | quantity | 69 | TotalInstitutionalInvestors | **是**（7 個 name） | 合併候選 M1 |
| 4 | `tw.margin_trading_balance.stock` | state | **49**(權威)＋56 | MarginPurchaseShortSale＋DailyShortSaleBalances | 否 | 兩通道、單位差 ×1000 |
| 5 | `tw.margin_trading_balance.market` | state | 23 | TotalMarginPurchaseShortSale | **是**（3 個 name） | 合併候選 M2 |
| 6 | `tw.sbl_short_balance.stock` | state | **新 binding**（同表 56） | DailyShortSaleBalances | 否 | 須 INSERT 第二 binding 列 |
| 7 | `tw.margin_maintenance_ratio.market` | quantity | 86 | TotalExchangeMarginMaintenance | 否 | 最乾淨 |
| 8 | `tw.securities_lending.stock` | event | 77 | SecuritiesLending | 是（transaction_type） | 名實不符須揭露 |
| 9 | `tw.foreign_ownership.stock` | state | 62 | Shareholding | 否 | knowability 兩讀 Q-R5 |
| 10 | `tw.holder_dispersion.stock` | state | 53 | HoldingSharesPer | **是**（HoldingSharesLevel） | knowability 已在 code |
| 11 | `tw.government_bank_flow.stock` | quantity | 51 | GovernmentBankBuySell | 否 | PK 病理 |
| 12 | `tw.day_trading.stock` | quantity | 35 | DayTrading | 否 | 乾淨 |
| 13 | `tw.option_daily_quote` | quantity | 43 | OptionDaily | **是**（TXO/position） | PK 13 欄 |
| 14 | `tw.futures.institutional_position` | quantity | 44 | FuturesInstitutionalInvestors | **是** | — |
| 15 | `tw.futures.large_trader_open_interest` | state | 38 | FuturesOpenInterestLargeTraders | **是** | — |
| 16 | `tw.financial_statement.income` | event | 68 | FinancialStatements | 是（type） | knowability 已在 code；錨不在表內 |
| 17 | `tw.financial_statement.balance` | event | 31 | BalanceSheet | 是（type） | 合併候選 M3 |
| 18 | `tw.monthly_revenue.stock` | event | 83 | MonthRevenue | 否 | create_time 90.3% NULL |
| 19 | `tw.market_capitalization.stock` | quantity | 70 | MarketValue | 否 | 乾淨 |
| 20 | `tw.valuation_ratio.stock` | quantity | 17 | PER | 否 | 哨兵值須揭露 |
| 21 | `tw.business_cycle_indicator` | state | 93 | BusinessIndicator | 否 | knowability=**待定錨** |
| 22 | `us.market_sentiment.fear_greed` | state | 85 | CnnFearGreedIndex | 否 | **唯一非 tw.；cross_market_axis 必填** |
| 23 | `tw.long_term_price_average.stock` | quantity | **30** | TaiwanStock10Year | 否 | **role 應改 derived**；§1.3 新增 |

**⇒ 23 表 → 23 個概念**（binding 24 列：23 現有 ＋ 1 新增於 §3.2）。

**「為何不是 22」**：＋1 表（10Year，§1.3）、＋1 概念（56 供兩事實，§3.2）、−1 概念（49／56 之融券餘額為同一事實兩通道，§3.2）。

---

## §5 合併判斷——三組合併候選（若 Steward 全採，收斂為 **20 個概念**）

| 代號 | 合併對象 | 支持合併 | 反對合併（機械事實） |
|---|---|---|---|
| **M1** | `tw.institutional_net_flow.stock`(60) ＋ `.market`(69) | 市場級＝個股級之聚合，同一底層流量；WM.15「兩個以上 Observation Channel 描述同一世界事實」之字面可涵蓋 | `resolve()` 只回**一個** binding。併為一概念後，`build_market_direction_features.py:60`（市場級消費）與 `features/phase.py:52`（個股級消費）**必有一方被解析到錯的表**。Registry **無粒度欄**可區分 |
| **M2** | `tw.margin_trading_balance.stock`(49+56) ＋ `.market`(23) | 同 M1 | 同 M1 |
| **M3** | `tw.financial_statement.income`(68) ＋ `.balance`(31) | 同為「季度財報揭露」事件、同 ts／同 knowability／同 finality | 兩表為**不同報表**、`type` 值域不相交（NetIncome… vs Equity/Liabilities/TotalAssets）；`features/fundamentals.py:23/28` 兩支 SQL 各取各表。併後同一 `resolve()` 無法同時服務兩支 |

**本件建議：三組皆不合併**（保持 23 概念）。**理由一句**：Registry 現行結構（`resolve()` 回單一 `(table, column, role)`、無粒度欄、無列篩選欄）使「同事實不同粒度」之合併在**機械上會解析到錯表**——這不是語意判斷，是 `src/augur/catalog/world_concept.py:110-160` 之實作事實。
**若 Steward 認為語意上應合併**，則須先解 Q-R2（Registry 是否增列篩選／粒度表達力）——合併與 Q-R2 是同一個結構問題的兩面。

---

## §6 無法定案者——待 Steward（AI 不解釋條文，`AUGUR-MC v1.6 §8.1`；本節僅列兩造事實）

| # | 問題 | 為何非 AI 可決 | 卡住什麼 |
|---|---|---|---|
| **Q-R1** | 既有 unmapped binding 由 `unmapped` → `mapped`，形制應為 **(a) 原地 UPDATE**（`binding_id` 不變，需 `SET LOCAL augur.honesty_write='on'`）還是 **(b) 標舊列 superseded ＋ INSERT 新列**（append-only，`binding_id` 改變）？WM.35 明文「unmapped 為顯式合法過渡態」似支持 (a)；Annex F 呈案 §5.2 對 `map_note` 事實更正採 (b) | 版本化義務（WM.13／WM.25）之適用範圍＝條文解釋 | **全部 23 個登錄之執行路徑**；(b) 會使本件所列 binding_id 全部作廢重編 |
| **Q-R2** | **多值表之列篩選表達力**（Annex F Q2 之擴大版）。本批 **7 表**為多值表，消費端即使改繫概念鍵仍須內嵌 `stock_id='TAIEX'`／`option_id='TXO'`／`trading_session='position'`／`HoldingSharesLevel='more than 1,000,001'` 等字面——WM.36 禁令原文列舉「供應商表名、欄名、**series 識別碼**」。是否須在 `world_channel_binding` 增列篩選欄（表結構變更＝Steward 專屬）？ | WM.36 欄 3「粒度至欄位級」之適用範圍 ＋ 表結構變更權限 | 7 個概念之登錄完成判準；M3 之 B4／B5 全批 |
| **Q-R3** | **「改對」算不算「行為變更」？** 兩處實證：(i) TRI 4 個日曆用途改繫 `tw.trading_calendar` ⇒ 多 16 個交易日（§2.4）；(ii) `CnnFearGreedIndex` 依 A.35 第三項宣告跨市場軸後，`build_market_direction_features.py:73` 之同日對齊須改為 t+1（§3.9）。二者影子比對**必判 red**，但都是修正既有錯誤 | 絞殺「行為零變更」要求與 A.35／WM.31 保守解釋之交互適用 | TRI 之 3–4 檔解鎖；`build_market_direction_features` 全檔 |
| **Q-R4** | **跨概念查詢之合法載體**：`build_daily_direction_features.py:130-134` 之單一 SQL 同時取「融券餘額」與「借券賣出餘額」（兩個建議概念）。改繫概念鍵時無單一 `resolve()` 可服務 | WM.36「以世界概念為鍵」之顆粒度 | `tw.margin_trading_balance.stock` 與 `tw.sbl_short_balance.stock` 之消費端改線 |
| **Q-R5** | **可知規則錨不在通道表內者，欄 5 是否可解析**（Annex F Q4 之擴大）。本批三型：(i) 財報／BalanceSheet——表內無公告欄，規則在 `release_lag.py`；(ii) `TaiwanBusinessIndicator`——**無任何錨**，須寫「待定錨」＝WM.31 明文「不可用於任何 as-of 推理」，但**現正被消費**；(iii) `TaiwanStockShareholding`——catalog 標 `RecentlyDeclareDate` 為 as-of 欄，但親驗其值落後 2.5 個月，疑為內容欄非可知錨 | WM.31(b)／A.35 之適用＝條文解釋 | 5 個概念之採認；`BusinessIndicator` 一項會直接使 2 檔現行消費落入違規 |
| **Q-R6** | **`TaiwanStock10Year` 之歸類與射程**：不在 plan §11 之 52 檔口徑內（因 M2 正規式漏數字，§1.3），但形制屬生產消費鏈（`features/valuation.py` 為 canonical 特徵產生器）。另 `src/augur/audit/field_correlation.py` 同型。**連同 Annex F 呈案 Q-C 已呈之 `evaluation/label.py` 與 4 檔 UNCLASSIFIED 一併裁** | 射程界定＝Steward 補裁事項 | valuation.py 之「已絞殺」宣稱是否假綠 |
| **Q-R7** | **值欄入 PK 之通道**（`TaiwanOptionDaily` 13 欄 PK、`TaiwanStockGovernmentBankBuySell` 7 欄 PK）：供應商修正值會新增列而非覆蓋。其 `attestation_mode=byte` 與 `finality_predicate='當日值於次一交易日收盤後定案'` 是否相容？是否須設 `conflict_set_ref`（WM.37「多來源供應時預留衝突保存」之落點在此是否適用「同來源多列」）？ | WM.32／WM.37 之適用 | 2 個概念之欄 7 與 conflict 欄 |
| **Q-R8** | **命名空間慣例**：`us.market_sentiment.fear_greed` 為第一個非 `tw.` 概念。前綴閉集是否須先由 Steward 定？（現有六概念全為 `tw.`，無明文慣例文件） | 命名為 Registry 一級結構之識別鍵，變更成本高 | 本概念之 `concept_key` 定名 |
| **Q-R9** | **`TaiwanStockTotalReturnIndex` 之停滯**：14 個交易日（2026-06-22→07-09）之列**無 audit 列**（provenance 缺口）；07-09 後停滯，且不在每日增量鏈（需 `data_id`、by-date 路徑略過）。WM.35 對「通道停止更新」未設判準——停滯之通道得否登錄為 mapped 並被指定權威？ | WM.35 通道地位之適用 | TRI 概念之採認；4 檔解鎖 |

---

## §7 尾節——hugo 圈選單 ＋ 親簽 SQL 範本

> 圈選方式：在「圈選」欄打勾，或直接寫下你要的 `concept_key`／「不登錄」。**`decided_by`／`decided_at` 一律由你親打**，本備料未填、亦不代填。
> **先決**：Q-R1（形制）未定前，下方任何 SQL 皆不得執行——形制決定 SQL 形狀。

### 7.1 圈選單（一概念一列）

| # | 建議 concept_key | 繫哪個 binding | 一句理由 | 圈選 |
|---|---|---|---|---|
| 1 | `tw.market_total_return_index` | **78**（權威 78） | 全庫唯一供應市場總報酬指數之表；但表已停滯於 07-09（Q-R9） | ☐ 登錄　☐ 不登錄　☐ 改名：____ |
| 2 | `tw.institutional_net_flow.stock` | 60（權威 60） | 三個消費點皆全法人合計、無列篩選字面＝本批少數登錄後可真正解除直綁者 | ☐ 登錄　☐ 併入 #3（M1）　☐ 不登錄 |
| 3 | `tw.institutional_net_flow.market` | 69（權威 69） | 市場級為獨立實體層級；併入 #2 會使 `resolve()` 解析到錯表 | ☐ 登錄　☐ 併入 #2（M1）　☐ 不登錄 |
| 4 | `tw.margin_trading_balance.stock` | **49（權威）＋56（第二通道）** | 融券餘額經親驗為同一事實兩通道、單位差 ×1000；49 另含融資與 `MarginPurchaseLimit` | ☐ 登錄（權威 49）　☐ 權威改 56　☐ 拆為融資／融券兩概念　☐ 不登錄 |
| 5 | `tw.margin_trading_balance.market` | 23（權威 23） | 同 #3 之理由 | ☐ 登錄　☐ 併入 #4（M2）　☐ 不登錄 |
| 6 | `tw.sbl_short_balance.stock` | **新 binding**（表＝DailyShortSaleBalances） | 借券賣出餘額為 49 完全沒有的欄群；須新增第二 binding 列（先例＝binding 2／3） | ☐ 登錄＋新 binding　☐ 併入 #4　☐ 不登錄 |
| 7 | `tw.margin_maintenance_ratio.market` | 86（權威 86） | 單值表、PK 為 date、無多值問題——本批最乾淨 | ☐ 登錄　☐ 不登錄 |
| 8 | `tw.securities_lending.stock` | 77（權威 77） | 逐筆借券成交＝event；消費端名實不符須隨卷揭露 | ☐ 登錄　☐ 不登錄 |
| 9 | `tw.foreign_ownership.stock` | 62（權威 62） | 通道乾淨，但 knowability 兩讀未決（Q-R5-iii） | ☐ 登錄　☐ 俟 Q-R5　☐ 不登錄 |
| 10 | `tw.holder_dispersion.stock` | 53（權威 53） | knowability（+7 日）已在 `release_lag.py` 生產使用，搬進 Registry 即可 | ☐ 登錄　☐ 不登錄 |
| 11 | `tw.government_bank_flow.stock` | 51（權威 51） | 通道單一；PK 病理須揭露（Q-R7） | ☐ 登錄　☐ 俟 Q-R7　☐ 不登錄 |
| 12 | `tw.day_trading.stock` | 35（權威 35） | 單一消費點、無列篩選字面 | ☐ 登錄　☐ 不登錄 |
| 13 | `tw.option_daily_quote` | 43（權威 43） | 多值最嚴重（TXO＋position 兩字面）＋13 欄 PK ⇒ 登錄不解直綁 | ☐ 登錄　☐ 俟 Q-R2　☐ 不登錄 |
| 14 | `tw.futures.institutional_position` | 44（權威 44） | 多值（26 futures_id） | ☐ 登錄　☐ 俟 Q-R2　☐ 不登錄 |
| 15 | `tw.futures.large_trader_open_interest` | 38（權威 38） | 多值（484 futures_id） | ☐ 登錄　☐ 俟 Q-R2　☐ 不登錄 |
| 16 | `tw.financial_statement.income` | 68（權威 68） | knowability（45/90 日）已在 `release_lag.py`；但錨不在表內（Q-R5-i） | ☐ 登錄　☐ 併入 #17（M3）　☐ 俟 Q-R5　☐ 不登錄 |
| 17 | `tw.financial_statement.balance` | 31（權威 31） | 與 #16 為不同報表、`type` 值域不相交 | ☐ 登錄　☐ 併入 #16（M3）　☐ 不登錄 |
| 18 | `tw.monthly_revenue.stock` | 83（權威 83） | knowability（公告月 15 日）已在 `release_lag.py`；`create_time` 90.3% NULL 須揭露 | ☐ 登錄　☐ 不登錄 |
| 19 | `tw.market_capitalization.stock` | 70（權威 70） | 單值欄、乾淨 | ☐ 登錄　☐ 不登錄 |
| 20 | `tw.valuation_ratio.stock` | 17（權威 17） | 乾淨；`PER=0` 哨兵比例須先實查填 provenance（殘項） | ☐ 登錄　☐ 不登錄 |
| 21 | `tw.business_cycle_indicator` | 93（權威 93） | 無可知錨 ⇒ 欄 5 須寫「待定錨」＝WM.31 明文不可 as-of，但**現正被消費**（Q-R5-ii） | ☐ 登錄（待定錨）　☐ 不登錄（過渡）　☐ 俟 Q-R5 |
| 22 | `us.market_sentiment.fear_greed` | 85（權威 85） | 唯一非本域市場；`cross_market_axis` 為本批唯一必填（A.35 第三項） | ☐ 登錄　☐ 改名：____　☐ 俟 Q-R8 |
| 23 | `tw.long_term_price_average.stock` | **30**（權威 30） | §1.3 新補之第 23 表；`channel_role` 建議由 observation 改 **derived** | ☐ 登錄＋改 derived　☐ 登錄維持 observation　☐ 俟 Q-R6　☐ 不登錄 |

**附帶待圈（同一批次須決定）**

| 項 | 建議 | 圈選 |
|---|---|---|
| **Q-R1 形制**：unmapped→mapped 用 (a) 原地 UPDATE 還是 (b) supersede+INSERT | 未定即無法執行 | ☐ (a) 原地 UPDATE　☐ (b) append-only　☐ 其他 |
| 本批是否得用 `SET LOCAL augur.honesty_write='on'`（(a)(b) 皆需，honesty guard 親驗） | 需明示同意，否則無合法路徑 | ☐ 同意　☐ 改由腳本封裝　☐ 其他 |
| TRI 之 4 個「日曆用途」處是否改繫既有 `tw.trading_calendar`（會多 16 交易日、影子比對必 red） | 建議改繫（Q-R3） | ☐ 改繫　☐ 維持　☐ 俟 Q-R3 |
| `TaiwanStock10Year` 之 M2 口徑漏洞（正規式不含數字）是否同批修 `check_vendor_binding.py:52` | 建議修（否則 A 類清償判準持續假綠） | ☐ 同批修　☐ 另案　☐ 不修 |
| `wm_m3_batch1_target_scoping` §2.4「TRI 解鎖 5 檔」之修正（實為 3 檔；+IIBS 則 4 檔） | 建議由 Steward 認可後更正該報告 | ☐ 認可更正　☐ 維持原文　☐ 其他 |

### 7.2 親簽 SQL 範本 A｜新概念登錄（形制 (a)；以 `tw.market_total_return_index` → binding 78 為例）

> **紀律**：`⟨…⟩` 佔位**由 hugo 親打**；AI 不代填。**執行前先 `BEGIN`，逐句核回傳列數，確認才 `COMMIT`；有疑即 `ROLLBACK`。**
> **親查依據（本輪實跑）**：`world_channel_binding` **有** honesty guard（`trg_world_channel_binding_honesty_row BEFORE DELETE OR UPDATE … EXECUTE FUNCTION honesty_ledger_guard()`），函式本體 `UPDATE` 分支要求 `current_setting('augur.honesty_write')='on'`，`DELETE/TRUNCATE` 一律拒絕。⇒ **UPDATE binding 必須帶通行證**。
> `world_concept` 之 guard 亦為 `BEFORE DELETE OR UPDATE` ⇒ **INSERT 身分列免通行證**。
> CHECK `world_channel_binding_check`：`(mapping_status='mapped') = (concept_key IS NOT NULL)` ⇒ **兩欄必須同一句設定**。

```sql
BEGIN;
SET LOCAL augur.honesty_write = 'on';   -- 僅為 ③ 之 UPDATE 所需（honesty guard 親驗）

-- ① 概念身分列（world_concept；INSERT 免通行證）
INSERT INTO world_concept (concept_key) VALUES ('tw.market_total_return_index');
                                                -- 期望 INSERT 0 1

-- ② 概念版本列（WM.36 七欄；本概念為新建，故無舊列須 supersede——
--    與 Annex F 六概念之「採認」不同：那六個已有 seed 現行列，須先標 superseded）
INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref,
     decided_by, decided_at)
VALUES ('tw.market_total_return_index',
        'quantity',                                   -- 欄 2（閉集）
        78,                                           -- 欄 4 權威表徵（WM.14 恰一）
        '交易日',                                      -- 欄 5(a) A.35 列舉
        '收盤後當日可得（TWSE 盤後發布）；表內無公告欄，本宣告為法定公開規則型（WM.31(b)）',
        NULL,                                         -- 欄 5 第三項：本域市場，A.35 不適用
        jsonb_build_object(
            'source', '所列通道之當次回應',
            'basis',  'WM.35 登錄批次；備料 reports/wm_channel_registration_draft_20260803.md §2',
            'decision_ref', '⟨附卷裁定編號⟩',
            'vendor_source', 'finmind',
            '資料現況_20260803', '10,830 列／2 series（TAIEX 5,788／TPEx 5,042）／2003-01-02→2026-07-09',
            '已知缺口', '非 live：data_audit_log 最後一筆 2026-06-20；2026-06-22→07-09 共 14 交易日無 audit 列；07-09 後停滯；不在每日 by-date 增量鏈（需 data_id）',
            '登錄狀態', 'registered'),
        '當日值於次一交易日收盤後定案',                  -- 欄 7（A.37 例示一逐字）
        NULL,                                         -- conflict_set_ref：單通道不觸發 WM.37
        '⟨hugo 親打⟩',                                 -- decided_by：AI 不代填
        TIMESTAMPTZ '⟨YYYY-MM-DD HH:MM:SS+08⟩');      -- decided_at：AI 不代填
                                                -- 期望 INSERT 0 1

-- ③ 通道繫結 unmapped → mapped（CHECK 要求兩欄同句設定；UPDATE 需通行證）
UPDATE world_channel_binding
   SET concept_key    = 'tw.market_total_return_index',
       mapping_status = 'mapped',
       provenance     = provenance || jsonb_build_object(
           'map_note', 'WM.35 登錄批次 2026-08-03；供應市場總報酬指數（TAIEX／TPEx 兩 series）',
           'mapped_basis', 'reports/wm_channel_registration_draft_20260803.md §2.5',
           'multi_value_note', '表級暫登；消費端仍須內嵌 stock_id 篩選字面＝待決 Q-R2')
 WHERE binding_id = 78 AND superseded_at IS NULL;
                                                -- 期望 UPDATE 1

-- ④ 驗（純 SELECT）：七欄俱全、權威可解析、人簽欄已填
SELECT concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
       cross_market_axis, finality_predicate, conflict_set_ref, decided_by, decided_at
  FROM world_concept_registry_current
 WHERE concept_key = 'tw.market_total_return_index';

SELECT binding_id, concept_key, source_table, channel_role, mapping_status
  FROM world_channel_binding
 WHERE binding_id = 78;

COMMIT;   -- 或 ROLLBACK
```

**其餘概念只需改五處**：`concept_key`（4 處）、`category`、`authoritative_binding_id`／`binding_id`（各 1 處）、欄 5／欄 7 之字串、provenance 之資料現況與缺口。逐概念之值見 §3 與 §4 對照表。

**執行後複驗**（零 Claude usage）：`venv/bin/python -m augur.catalog.world_concept --check` ⇒ 該概念應由 ✗ 轉為可解析。

### 7.3 範本 B｜同一表供第二個概念（新增 binding 列；以 `tw.sbl_short_balance.stock` 為例）

> **先例**：`TaiwanStockDelisting` 已有 binding 2（`tw.roster_membership`）與 binding 3（`tw.delisting`）兩列。
> ⚠ **副作用**：`concepts_for_table('TaiwanDailyShortSaleBalances')` 將回 2 個概念 ⇒ `compare_shadow_binding.py` 之 auto 模式對該表**強制要求 `--map TABLE=<concept_key>`**（`make_lookup` 於 `len(keys)>1` 即拋，已由 `wm_m3_batch1_target_scoping` §3-2 親驗）。

```sql
BEGIN;
-- 本範本全為 INSERT，honesty guard 不攔 INSERT ⇒ 不需通行證
INSERT INTO world_concept (concept_key) VALUES ('tw.sbl_short_balance.stock');

INSERT INTO world_channel_binding
    (concept_key, source_table, source_column, channel_role, mapping_status, provenance)
VALUES ('tw.sbl_short_balance.stock',
        'TaiwanDailyShortSaleBalances',
        NULL,                                    -- 表級暫登（同既有 10 列）
        'observation',
        'mapped',
        jsonb_build_object(
            'map_note', 'WM.35 登錄批次 2026-08-03；本表 SBL 欄群（借券賣出餘額）',
            'second_channel_on_same_table', '本表另有 binding 56 服務 tw.margin_trading_balance.stock（融券段）；形制先例＝TaiwanStockDelisting 之 binding 2／3',
            'mapped_basis', 'reports/wm_channel_registration_draft_20260803.md §3.2',
            'vendor_source', 'finmind'))
RETURNING binding_id;                            -- ← 記下新 binding_id，供下一句欄 4 使用

INSERT INTO world_concept_version
    (concept_key, category, authoritative_binding_id, ts_semantics, knowability_rule,
     cross_market_axis, provenance, finality_predicate, conflict_set_ref, decided_by, decided_at)
VALUES ('tw.sbl_short_balance.stock', 'state',
        ⟨上一句 RETURNING 之 binding_id⟩,
        '交易日', '收盤後當日可得（TWSE 盤後公布）', NULL,
        jsonb_build_object('source','所列通道之當次回應',
                           'basis','WM.35 登錄批次；備料 §3.2',
                           'decision_ref','⟨附卷裁定編號⟩','登錄狀態','registered'),
        '當日值於次一交易日收盤後定案', NULL,
        '⟨hugo 親打⟩', TIMESTAMPTZ '⟨YYYY-MM-DD HH:MM:SS+08⟩');

SELECT binding_id, concept_key, source_table, mapping_status
  FROM world_channel_binding
 WHERE source_table = 'TaiwanDailyShortSaleBalances' AND superseded_at IS NULL;
                                                 -- 期望 2 列（56 + 新列）
COMMIT;   -- 或 ROLLBACK
```

### 7.4 範本 C｜一概念兩通道（第二通道繫同一概念；以 binding 56 → `tw.margin_trading_balance.stock` 為例）

```sql
BEGIN;
SET LOCAL augur.honesty_write = 'on';

-- 第二通道亦標 mapped，但 authoritative_binding_id 只指一個（WM.14 恰一）
UPDATE world_channel_binding
   SET concept_key    = 'tw.margin_trading_balance.stock',
       mapping_status = 'mapped',
       provenance     = provenance || jsonb_build_object(
           'map_note', 'WM.35 登錄批次 2026-08-03；本表融券欄群（MarginShortSales*）為 binding 49 融券段之第二通道',
           'unit_mismatch', '本通道單位=股；binding 49 單位=張（×1000）。2026-07-31 親驗：00403A ShortSaleTodayBalance=1,482 vs MarginShortSalesCurrentDayBalance=1,482,000',
           'wm15_note', '同一世界事實之兩通道；擇用規則須單一登錄（WM.15），權威建議 49')
 WHERE binding_id = 56 AND superseded_at IS NULL;      -- 期望 UPDATE 1

-- 概念版本列之 conflict_set_ref 記錄衝突集（WM.37 落點）
--（若概念列尚未建立，併入範本 A 之 ② 一次寫入；此處示意獨立修訂之形：
--  須先標舊版本列 superseded 再 INSERT 新版本列——partial unique 使單獨 INSERT 必撞 23505，
--  形制已於 augur_sandbox 雙向實測，見 reports/wm_annexf_authoritative_binding_prep_20260803.md 附記）
COMMIT;   -- 或 ROLLBACK
```

### 7.5 唯讀乾解析結果（本輪實跑；**零寫入**）

以 `BEGIN; EXPLAIN (COSTS OFF) <各 DML>; … ROLLBACK;` 對範本 A ①②③④、範本 B 之 binding INSERT（含 `RETURNING`）、範本 C 之 UPDATE 共 **6 句**作語法／計畫解析（`EXPLAIN` 無 `ANALYZE` ⇒ 不執行）。**`RC=0`、`ROLLBACK`、全部通過**：

| 句 | 計畫 |
|---|---|
| 範本 A ① | `Insert on world_concept → Result` |
| 範本 A ② | `Insert on world_concept_version → Result` |
| 範本 A ③ | `Update on world_channel_binding → Index Scan using world_channel_binding_pkey (binding_id = 78), Filter: superseded_at IS NULL` |
| 範本 A ④ | `Nested Loop`（`world_concept_version` v Filter: `superseded_at IS NULL AND concept_key=…` ＋ `world_concept` c） |
| 範本 B binding INSERT | `Insert on world_channel_binding → Result` |
| 範本 C UPDATE | `Update on world_channel_binding → Index Scan (binding_id = 56)` |

> 乾解析用之 `⟨…⟩` 佔位以字串 `DRYPARSE_PLACEHOLDER` 代入（**非人簽值**；`EXPLAIN` 不執行、交易 `ROLLBACK`，該值未進入任何資料列）。腳本：`scratchpad/dryparse_reg.sql`。

**未被此檢查涵蓋者（誠實）**：唯一索引違反、CHECK 違反、trigger 拒絕、`jsonb ||` 併值結果、`RETURNING` 之實際值——皆屬執行期行為，`EXPLAIN` 一律不觸發。

---

## §8 本輪唯讀證明、殘項與可重跑指令

### 8.1 零寫入證明

作業前後複查 Registry 六數皆同值：身分 **6**／版本 **6**／現行 **6**／`decided_by` 非空 **0**／`authoritative_binding_id` 非空 **0**／通道 **98**（mapped **10**）／已 supersede 通道 **0**。
零 DDL、零 DB 寫入、零 commit、零 systemctl；未觸 FinMind／FRED 任何 API（#24／#25 不適用）；未改任何既有檔（本檔為新增，#16 命名）；`decided_by`／`decided_at` 全程未填、範本留 `⟨…⟩` 佔位。

### 8.2 殘項（誠實：本輪未做）

1. **未實查 `TaiwanStockPER` 之 `PER=0` 哨兵比例**（§3.21）——登錄前應補一次 `GROUP BY` 填入 provenance。
2. **未逐字檢查 `build_market_direction_features.py` 之 8 個非 TRI 直綁處之列篩選字面**（僅親讀 SQL 首行）——Q-R2 之受影響處數可能低估。
3. **未查明 TRI 之 14 個交易日由何路徑寫入而未留 audit 列**（§2.1）——provenance 缺口，非本件射程。
4. **未驗其餘 75 條 unmapped 通道**（98 − 23 本批 − 已 mapped 之表）之語意，僅本批 23 表逐表親驗。
5. **未實跑任何範本 SQL 之寫入路徑**——僅 `EXPLAIN` 乾解析；唯一索引／CHECK／trigger 之實際行為未在生產庫證實（形制之實測見 Annex F 呈案附記之 `augur_sandbox` 結果）。
6. **`category` 之閉集單值判斷**（尤 §3.6 財報之 `event` vs `state`、§2.5 TRI 之 `quantity` vs `state`）為 AI self-reported，未經 Steward 採認。

### 8.3 複核用一鍵指令（全唯讀、零 Claude usage）

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
Q="PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"

# ① Registry 基線（六數）
eval $Q -c "SELECT (SELECT count(*) FROM world_concept) ident,(SELECT count(*) FROM world_concept_version WHERE superseded_at IS NULL) cur,(SELECT count(decided_by) FROM world_concept_version) signed,(SELECT count(authoritative_binding_id) FROM world_concept_version) auth,(SELECT count(*) FROM world_channel_binding) bind,(SELECT count(*) FROM world_channel_binding WHERE mapping_status='mapped') mapped;"

# ② 本批 23 表之 binding 現況
eval $Q -c "SELECT binding_id, concept_key, source_table, channel_role, mapping_status FROM world_channel_binding WHERE binding_id IN (78,60,56,49,62,43,68,35,85,93,44,38,69,23,86,51,53,77,31,83,70,17,30) ORDER BY binding_id;"

# ③ TRI 停滯（§2.1）
eval $Q -c "SELECT stock_id, count(*), min(date)::text, max(date)::text FROM \"TaiwanStockTotalReturnIndex\" GROUP BY 1;"
eval $Q -c "SELECT dataset, max(logged_at)::text FROM data_audit_log WHERE dataset='TaiwanStockTotalReturnIndex' GROUP BY 1;"

# ④ TRI 日期集合 ≡ 交易日曆（§2.3 之機械依據）
eval $Q -c "WITH tri AS (SELECT DISTINCT date FROM \"TaiwanStockTotalReturnIndex\" WHERE stock_id='TAIEX'), cal AS (SELECT DISTINCT date FROM \"TaiwanStockTradingDate\" WHERE date BETWEEN DATE '2003-01-02' AND DATE '2026-07-09') SELECT (SELECT count(*) FROM tri),(SELECT count(*) FROM cal),(SELECT count(*) FROM tri t WHERE NOT EXISTS(SELECT 1 FROM cal c WHERE c.date=t.date)),(SELECT count(*) FROM cal c WHERE NOT EXISTS(SELECT 1 FROM tri t WHERE t.date=c.date));"

# ⑤ 融券兩通道之單位差（§3.2）
eval $Q -c "SELECT m.stock_id, m.\"ShortSaleTodayBalance\" AS lots, s.\"MarginShortSalesCurrentDayBalance\" AS shares FROM \"TaiwanStockMarginPurchaseShortSale\" m JOIN \"TaiwanDailyShortSaleBalances\" s USING (stock_id,date) WHERE m.date=DATE '2026-07-31' AND m.\"ShortSaleTodayBalance\">0 ORDER BY m.stock_id LIMIT 5;"

# ⑥ M2 正規式漏數字（§1.3）
grep -n '_QUOTED = re.compile' scripts/check_vendor_binding.py
grep -rnoE 'FROM \\?"[A-Za-z]*[0-9][A-Za-z0-9]*\\?"' --include=*.py src/ scripts/

# ⑦ 可知規則之 code 現住所（§3.6／3.17／3.19）
grep -n 'REVENUE_DAY\|FIN_LAG_QUARTER\|FIN_LAG_ANNUAL\|HOLDINGS_LAG_DAYS' src/augur/features/release_lag.py

# ⑧ 月營收 create_time 之 NULL 率（§3.19）
eval $Q -c "SELECT count(*) FILTER (WHERE create_time IS NULL) AS nulls, count(*) FROM \"TaiwanStockMonthRevenue\";"

# ⑨ honesty guard 本體（§7.2 之依據）
eval $Q -c "SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname='honesty_ledger_guard';"
```

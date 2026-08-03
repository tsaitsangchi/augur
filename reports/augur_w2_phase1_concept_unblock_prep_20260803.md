# W2 Phase 1 備料｜概念解阻（不寫 DB）— 2026-08-03

> **位階**：[I] 執行備料（CLAUDE #16／計畫 §10）。**非** [N]；AI 不代簽 `decided_by`。  
> **計畫 SSOT**：`reports/augur_w2_undefined_concept_unblock_plan_20260803.md`（Steward 已拍板 → 開 Phase 1 備料）。  
> **上游草案**：`reports/wm_channel_registration_draft_20260803.md`（23 概念＋Q-R1…Q-R9）。  
> **上游抽樣**：`reports/augur_w2_source_column_reconcile_sampling_20260803.md`。  
> **硬紀律**：不寫 DB（無 INSERT／UPDATE／DDL）；零 FinMind／FRED；不搶 `heavy_slot`；不 commit／不 push。  
> **Live 複核**：附錄 A＝**2026-08-03 PC002 已複核**（Steward 親跑 stdout；數字禁改）。

---

## §0 本檔對齊計畫 §10

| §10 項 | 本檔住所 | 狀態 |
|---|---|---|
| （1）Steward 先裁 §6 必裁三條 | §1（標「仍待裁／已拍預設」） | 備料用預設已填；**寫入仍閘在三裁** |
| （2-i）23 草案執行順序表（U1 三條優先） | §2 | ✓ |
| （2-ii）U0 六張概念卡 | §3 | ✓ |
| （2-iii）B0／infra 緩登名單 | §4 | ✓（含 W2-2 射程卷摘要） |
| （3）第二刀親簽 SQL | — | **未開**（須 §6 三裁＋圈選後） |

---

## §1 Steward 必裁三條｜備料假設標記

> 寫入／親簽 SQL **不得**憑本節假設執行。僅供 Phase 1 文件形狀與圈選序。

| # | 題 | 標記 | 本輪備料採用 |
|---|---|---|---|
| **1 Q-R1** | unmapped→mapped：(a) 原地 UPDATE vs (b) supersede＋INSERT | **仍待裁** | 文件／SQL 範本沿用草案 §7 **形制 (a) 草圖**（WM.35「unmapped＝合法過渡」字面傾向）；**不執行** |
| **2 納入範圍** | 65 無概念是否採 P1→P4＋B0／infra 緩登？A.11／W2-4（binding 93）一指標一概念 vs 單表單概念 | 範圍：**已拍預設**（計畫 §1.1／§6.2 建議已隨計畫拍板）<br>A.11／93：**仍待裁** | B0×11＋infra×2 **緩登**（§4）；P1→P4 佇列有效。binding 93 暫用草案單概念 `tw.business_cycle_indicator`，並**明示 W2-4 衝突**待裁 |
| **3 W2-1** | 多欄 `source_column`：(a) 分隔字串／(b) 一欄一 binding／(c) 改 schema | **仍待裁** | 概念卡只列 `proposed_source_columns[]`（陣列＝形制中立）；**不**選定 (a)(b)(c) |

**強烈建議同批（計畫 §6；非本輪必裁最小集）**：W2-2、W2-6／Q-R7、Q-R8、M-W3、M-N7——U0／抽樣會再卡。

---

## §2 （i）23 草案執行順序表

> 來源：`wm_channel_registration_draft_20260803.md` §4／§7.1。  
> 優先軸＝計畫 P1→P4：**U1 樣本三條最先**，再乾淨可登錄、再結構債／待裁閘。  
> DRAFT23 ids（Live 附錄 A 同值）＝`[78,60,56,49,62,43,68,35,85,93,44,38,69,23,86,51,53,77,31,83,70,17,30]`。

### 2.1 執行序（圈選／呈裁用；非寫入授權）

| 序 | Wave | binding | 建議 concept_key | 表（短） | 標記 | 備註 |
|---|---|---|---|---|---|---|
| **1** | **U1** | **31** | `tw.financial_statement.balance` | BalanceSheet | **U1 優先** | 草稿已擬；粒度／M3 合併候補 |
| **2** | **U1** | **62** | `tw.foreign_ownership.stock` | Shareholding | **U1 優先** | Q-R5-iii knowability；欄入／出見抽樣 |
| **3** | **U1** | **93** | `tw.business_cycle_indicator` | BusinessIndicator | **U1 優先** | **W2-4／A.11 仍待裁**；knowability 待定錨 |
| 4 | A 乾淨 | 86 | `tw.margin_maintenance_ratio.market` | TotalExchangeMarginMaintenance | — | 草案：本批最乾淨 |
| 5 | A 乾淨 | 35 | `tw.day_trading.stock` | DayTrading | — | 無列篩選字面 |
| 6 | A 乾淨 | 70 | `tw.market_capitalization.stock` | MarketValue | — | 單值乾淨 |
| 7 | A 乾淨 | 17 | `tw.valuation_ratio.stock` | PER | — | 哨兵值須 provenance |
| 8 | A 消費解鎖 | 60 | `tw.institutional_net_flow.stock` | IIBS | P1 味 | 合計消費＝登錄後可真解直綁 |
| 9 | A 消費解鎖 | 83 | `tw.monthly_revenue.stock` | MonthRevenue | — | `create_time` 缺口揭露 |
| 10 | B knowability 已在 code | 53 | `tw.holder_dispersion.stock` | HoldingSharesPer | Q-R2 | 多值 level |
| 11 | B | 68 | `tw.financial_statement.income` | FinancialStatements | Q-R5 | 與 #1 分立（建議不併 M3） |
| 12 | B | 49＋56 | `tw.margin_trading_balance.stock` | Margin＋DailyShortSale | — | 權威建議 49；56＝第二通道 |
| 13 | B | （新） | `tw.sbl_short_balance.stock` | DailyShortSaleBalances | 須新 binding | 先例 Delisting 2／3 |
| 14 | B | 23 | `tw.margin_trading_balance.market` | TotalMarginPurchaseShortSale | M2 | 建議不併 #12 |
| 15 | C 多值 | 69 | `tw.institutional_net_flow.market` | TotalInstitutionalInvestors | M1／Q-R2 | 建議不併 #8 |
| 16 | C | 44 | `tw.futures.institutional_position` | FuturesInstitutionalInvestors | Q-R2 | — |
| 17 | C | 38 | `tw.futures.large_trader_open_interest` | FuturesOpenInterestLargeTraders | Q-R2 | — |
| 18 | C | 43 | `tw.option_daily_quote` | OptionDaily | Q-R2／Q-R7 | 13 欄 PK |
| 19 | C | 51 | `tw.government_bank_flow.stock` | GovernmentBankBuySell | Q-R7 | PK 病理 |
| 20 | C | 77 | `tw.securities_lending.stock` | SecuritiesLending | — | 名實不符揭露 |
| 21 | D 特殊閘 | 78 | `tw.market_total_return_index` | TotalReturnIndex | Q-R9 | **停滯**；日曆用途宜改繫 calendar |
| 22 | D | 85 | `us.market_sentiment.fear_greed` | CnnFearGreedIndex | **Q-R8** | 唯一非 `tw.`；cross_market_axis 必填 |
| 23 | D | 30 | `tw.long_term_price_average.stock` | TaiwanStock10Year | Q-R6 | role→derived 建議 |

**合併預設（草案 §5；已拍計畫範圍內文件預設）**：M1／M2／M3 **皆不合併**（`resolve()` 單 binding 機械限制）。**仍待裁**若 Steward 要改語意合併 → 先解 Q-R2。

### 2.2 圈選狀態欄（人填）

| binding | 圈選（登錄／不登錄／改名／俟 Q-R*） | 備註 |
|---|---|---|
| （上表 1–23） | ☐ | 親簽見草案 §7；本備料不代填 |

---

## §3 （ii）U0 六張概念卡

> 欄位形＝計畫 §1.3。提案鍵來自抽樣 §2（self-reported）；**禁**為覆蓋率 INSERT 空殼。  
> `proposed_source_columns` 依抽樣裁定；Live `--sample 10 --seed w2` 之展開面見附錄 A（禁改數字）。

### 卡 U0-1｜binding **7** `TaiwanStockConvertibleBondInfo`

| 欄 | 值 |
|---|---|
| **concept_key** | `tw.convertible_bond.terms` |
| **category** | `state`（條款狀態；替代讀 `entity`＝標的本身 → **仍待裁**） |
| **identity_one_liner** | 台股可轉債之發行／轉換條款（金額與轉換起迄），非日頻成交列 |
| **candidate_binding_ids** | `[7]` |
| **proposed_source_columns[]** | `IssuanceAmount`, `InitialDateOfConversion`, `DueDateOfConversion`（**出**候補：`cb_name`＝標籤抑條款內容 **仍待裁**） |
| **co_morbid** | W2-1（多欄） |
| **knows_consumption?** | 未證（本輪未做 P1 掃描）；標 **unknown** |
| **draft_ref** | 抽樣 §2 #1；Live sample binding 7（值欄候選另含 `cb_name`） |

### 卡 U0-2｜binding **37** `JapanStockPrice`

| 欄 | 值 |
|---|---|
| **concept_key** | `jp.daily_bar`（**Q-R8 仍待裁**） |
| **category** | `quantity` |
| **identity_one_liner** | 日本市場個股日頻 OHLCV 觀測（原始價通道） |
| **candidate_binding_ids** | `[37]`（建議另拆 **derived** binding 承 `Adj_Close`） |
| **proposed_source_columns[]** | observation：`Open`,`High`,`Low`,`Close`,`Volume`；**出／第二概念**：`Adj_Close`（W2-3） |
| **co_morbid** | W2-3、Q-R8、A.35 跨市場軸 |
| **knows_consumption?** | unknown |
| **draft_ref** | 抽樣 §2 #4；Live sample binding 37 |

### 卡 U0-3｜binding **50** `GoldPrice`

| 欄 | 值 |
|---|---|
| **concept_key** | `cm.gold.spot_price`（提案；**Q-R8 仍待裁**——閉集未定） |
| **category** | `quantity` |
| **identity_one_liner** | 黃金現貨／報價水準（單一價格觀測；單位／幣別不在 schema） |
| **candidate_binding_ids** | `[50]` |
| **proposed_source_columns[]** | `Price`（Live：**唯一** sample 自動配對＝True） |
| **co_morbid** | （結構輕）欄 1／5／單位語意仍人裁 |
| **knows_consumption?** | unknown（表有聚合／audit 史；非本輪 P1 認證） |
| **draft_ref** | 抽樣 §2 #5；Live sample binding 50 |

### 卡 U0-4｜binding **65** `TaiwanOptionInstitutionalInvestorsAfterHours`

| 欄 | 值 |
|---|---|
| **concept_key** | `tw.option.institutional_flow.after_hours` |
| **category** | `quantity` |
| **identity_one_liner** | 台股選擇權盤後時段法人多空成交量／金額流量 |
| **candidate_binding_ids** | `[65]` |
| **proposed_source_columns[]** | `long_deal_amount`,`long_deal_volume`,`short_deal_amount`,`short_deal_volume` |
| **co_morbid** | W2-1；M-W4 列鍵（option_id／call_put／institutional_investors）；盤後 ts 語義 |
| **knows_consumption?** | unknown |
| **draft_ref** | 抽樣 §2 #7；Live sample binding 65 |

### 卡 U0-5｜binding **80** `TaiwanStockSplitPrice`

| 欄 | 值 |
|---|---|
| **concept_key** | `tw.corporate_action.split`（平行既有 `tw.corporate_action.ex_dividend`） |
| **category** | `event` |
| **identity_one_liner** | 股票分割公司行動（恢復買賣日為 ts；分割前後參考價與類型） |
| **candidate_binding_ids** | `[80]`＋**建議第二 binding** 承 A.26 漲跌停參考態 |
| **proposed_source_columns[]** | **入**：`before_price`,`after_price`,`type`；**出／第二概念**：`max_price`,`min_price`,`open_price`（W2-5） |
| **co_morbid** | W2-1、W2-5 |
| **knows_consumption?** | unknown |
| **draft_ref** | 抽樣 §2 #8；A.21 錨；Live sample binding 80 |

### 卡 U0-6｜binding **97** `TaiwanFuturesDaily`

| 欄 | 值 |
|---|---|
| **concept_key** | `tw.futures.daily_bar` |
| **category** | `quantity` |
| **identity_one_liner** | 台股期貨契約日頻行情與未平倉（含結算／價差／量） |
| **candidate_binding_ids** | `[97]` |
| **proposed_source_columns[]** | 事實載體（雖全入 PK）：`open`,`max`,`min`,`close`,`settlement_price`,`spread`,`spread_per`,`volume`,`open_interest`；鍵＝`futures_id`,`contract_date`,`date`,`trading_session` |
| **co_morbid** | **W2-6／Q-R7**（值欄偵測器＝0；自動配對必 False） |
| **knows_consumption?** | unknown |
| **draft_ref** | 抽樣 §2 #10；Live sample binding 97（bucket=B1；值欄機械＝0） |

### 3.1 非 U0 但同十條｜不建假 concept

| binding | 桶 | 處置 |
|---|---|---|
| **31／62／93** | U1 | 走 §2 草案圈選，不另開 U0 卡 |
| **11** | U2／B0 | **概念佇列暫停** → §4／W2-2；禁止為填欄造 concept |

---

## §4 （iii）B0／infra 緩登名單＋W2-2 射程卷（摘要）

> **已拍預設**：緩登、不進概念優先佇列；禁止不可驗欄位映射（計畫 §8.7）。

### 4.1 B0 無實體表（11）— Live `--issues` 同日親驗

| binding_id | source_table | mapping_status | 處置 |
|---|---|---|---|
| 11 | `TaiwanFuturesTick` | unmapped | 緩登（樣本 U2） |
| 16 | `TaiwanVariousIndicators5Seconds` | unmapped | 緩登 |
| 24 | `TaiwanStockKBar` | unmapped | 緩登 |
| 26 | `USStockPriceMinute` | unmapped | 緩登 |
| 27 | `TaiwanOptionTick` | unmapped | 緩登 |
| 42 | `TaiwanStockBlockTradingDailyReport` | unmapped | 緩登 |
| 45 | `TaiwanStockPriceTick` | unmapped | 緩登 |
| 59 | `TaiwanStockWarrantTradingDailyReport` | unmapped | 緩登 |
| 61 | `TaiwanStockEvery5SecondsIndex` | unmapped | 緩登 |
| 76 | `TaiwanStockTradingDailyReport` | unmapped | 緩登 |
| 94 | `TaiwanStockStatisticsOfOrderBookAndTrade` | unmapped | 緩登 |

### 4.2 infra log（2）— 非世界觀測

| binding_id | source_table | 唱讀問題（Live） | 處置 |
|---|---|---|---|
| 88 | `data_audit_log` | type_unregistered×多欄＋`id` pk_mismatch | 緩登；去留**另裁** |
| 89 | `pipeline_execution_log` | 同型 type_unregistered／pk | 緩登；去留**另裁** |

### 4.3 W2-2 射程裁決卷（摘要；呈裁用）

| 項 | 內容 |
|---|---|
| **題** | 未落地（excluded／`table_absent`）通道可否登錄欄位映射？ |
| **事實** | B0×11 catalog 有欄、實體表不存在；填 `source_column`＝不可驗宣稱（原則精華 #1） |
| **建議預設** | **否**—先裁射程；在落地或明示豁免前**不** mapped、不造 concept |
| **標記** | **仍待裁**（W2-2） |

---

## §5 還缺什麼才能進 Phase 2

Phase 2＝有概念可映之後的 vendor↔`source_column` 規則擴張。閘：

1. **§6 必裁三條**有 Steward 明示答案（尤其 Q-R1、W2-1；A.11／93）。  
2. **§2 至少 U1 三條**（或約定子集）完成圈選（登錄／不登錄／俟 Q-R*）。  
3. **第二刀**：hugo 親簽 SQL 寫入身分／版本／binding（本檔不寫）。  
4. **探針複核 K1**（§0.2／附錄 A 同口徑）。  
5. 結構債若不擋該子集：W2-1 形制、（若碰 97）W2-6、（若碰 37／50／85）Q-R8。

**本輪未做**（誠實）：母體 65 無概念之 P1 消費掃描全文；`propose_concept_cards.py` 未建；任何 Registry 寫入。

---

## 附錄 A｜Live 複核（2026-08-03 PC002 已複核）

> **機**：`PC002-S1800` · Steward 親跑 stdout。  
> **性質**：(a)(b)(c) 三類來源之程式輸出；**數字原文禁改**。  
> **範圍**：`--survey`／`--issues`／`--sample 10 --seed w2`／`--selftest`／`scratchpad/w2_red_proof.py`／`check_cmd_matrix`／`check_false_assertions --gate`／計畫 §0.2 概念覆蓋 SQL＋抽樣報告 §7 復現列印。

### A.1 `--survey`（錨）

| 指標 | 值 |
|---|---|
| source_column 已填 | **0/98** |
| mapping_status=mapped | **10/98** |
| 唱讀 | 773 欄；對得上 685（88.6%）／對不上 88（11.4%） |
| catalog_missing / live_missing / type_unregistered / type_mismatch / pk_mismatch | **1 / 71 / 15 / 1 / 2** |
| B0 / B1 / B2 / B3 / B4 / B5 | **11 / 10 / 10 / 29 / 25 / 13** |
| 機械自動配對 | **9/98（9.2%）**；須人裁 89/98（90.8%） |
| 展開總面（嚴格值欄） | **472** |
| 逐通道至少一欄對不上 | 15/98（15.3%） |

### A.2 概念覆蓋與分母拆解（計畫 §0.2 SQL＋抽樣復現）

| 指標 | 值 |
|---|---|
| 概念覆蓋 (mapped, 草案23, 無概念, 總計) | **(10, 23, 65, 98)** |
| DRAFT23 ids | `[78,60,56,49,62,43,68,35,85,93,44,38,69,23,86,51,53,77,31,83,70,17,30]` |
| 85 條 vendor 問題欄 | **(2, 687)**＝對不上 2／唱讀分母 687 |
| 2 條 infra | **(15, 15)** |
| live 欄合計／嚴格值欄／多值欄通道 | **702／472／67** |
| 分層外推（草擬成本） | **1747s＝29.1 分**；簡單外推 28.7 分 CI[19.5, 38.0] 分 |

### A.3 `--sample 10 --seed w2`

十條 binding：`7,11,31,37,50,62,65,80,93,97`。  
**全部** `concept_key=None`、`source_column=None`、`mapping_status=unmapped`。  
**自動配對=True 者僅 binding 50**（GoldPrice／`Price`）；其餘 9 條＝False。

| binding | 表 | bucket（Live） | 自動配對 |
|---|---|---|---|
| 7 | TaiwanStockConvertibleBondInfo | B3 | False |
| 11 | TaiwanFuturesTick | B0 | False |
| 31 | TaiwanStockBalanceSheet | （樣本） | False |
| 37 | JapanStockPrice | B4 | False |
| **50** | **GoldPrice** | **B2** | **True** |
| 62 | TaiwanStockShareholding | B5 | False |
| 65 | TaiwanOptionInstitutionalInvestorsAfterHours | B3 | False |
| 80 | TaiwanStockSplitPrice | B4 | False |
| 93 | TaiwanBusinessIndicator | B4 | False |
| 97 | TaiwanFuturesDaily | B1（值欄機械 0） | False |

### A.4 `--issues`（B0／infra 名單來源）

B0×11 與 infra×2 完整表＝正文 §4（與 stdout 一致）。另 vendor 側殘留問題含：binding 12 `fred_series.realtime_start`（catalog_missing）；ConvertibleBondDailyOverview date 型別不符等——**本備料不修 catalog**（寫 DB 路徑）。

### A.5 `--selftest`

自測：**全通過 ✓**（含型別／缺欄／桶邊界／auto_pairable 嚴式／分層配額／seed 復現／B0 `table_absent` 等列出之全綠項）。

### A.6 紅證 `scratchpad/w2_red_proof.py`

| 項 | 值 |
|---|---|
| 基線自測 | rc=0 ✓ 綠 |
| 突變 M1–M10 | **全部驗紅**（各 rc=1） |
| 還原後自測 | rc=0 ✓ 綠 |
| 總結 | 10 個突變全部驗紅＝True；還原回綠＝True |

### A.7 閘

```
── 執行指令矩陣稽核：受檢 495 支／缺漏 0 支／豁免 0 支
✓ check_cmd_matrix 對象數地板:受檢入口總數=495≥300; … 錨:scripts/check_cmd_matrix.py=1≥1; 錨:scripts/_bootstrap.py=1≥1
  ✓ 全數通過（NEED=0）
✓ check_false_assertions --gate 對象數地板:實讀 .py 檔總數=1002≥400; … 
✓ 假斷言閘：無新增（實讀 1002 檔；基線容忍 20 條存量）
```

（跑 `check_cmd_matrix` 時 stderr 有 `<unknown>:1: SyntaxWarning: invalid escape sequence '\w'`——與閘結果正交，僅存檔。）

---

## AskQuestion（呈 Steward）

下一步要哪一條？

1. **繼續下一階段備料**（65 無概念 P1 消費掃描／W2-* 併草案 §6／可選 `propose_concept_cards.py` 規格）  
2. **呈裁**（§6 必裁三條＋§2 U1 圈選單＋W2-2 射程卷，等人答）  
3. **收工守夜班**（本檔凍結；不碰 heavy_slot／evolution）

---

*完。零 DB 寫入、零 commit。*

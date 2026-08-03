# M-W2｜`source_column` 欄位級唱讀對帳：唯讀抽樣與規模外推 — 2026-08-03

> **性質**：M-W2（優化總計畫第 25 步）之交付。**全程唯讀**——零 DDL、零 DB 寫入、零 commit、零外部 API（FinMind／FRED 凍結中，FZ-keep）。唯一寫入＝本檔與 `scripts/reconcile_channel_columns.py`（新檔）。
> **未做**：未填任何 `source_column`（填欄屬 M-W5，且粒度須待 M-W3／M-W4 裁定）；未代裁任何待決項；未代簽 `decided_by`。
> **數字時點**：全部為 **2026-08-03 live 唯讀現查**（`scripts/reconcile_channel_columns.py` 實跑輸出），**非抄既有報告**。復現指令見 §6，每個數字可零 Claude usage 重跑。
> **誠實級別**：§1 之對帳數字為**機械輸出**；§2 之逐條展開提案、§4 之結構性發現為 **AI self-reported**（CLAUDE.md #32(a)），不構成「世界如此」之權威確認。
> **上游 SSOT**：`reports/augur_optimization_master_plan_20260803.md` 第 25 步（M-W2）·`specs/WORLD-MODEL-SPECIFICATION.md` WM.36:344-358 ·`reports/wm_channel_registration_draft_20260803.md`（23 表登錄草案）。

---

## §0 五句話結論

1. **「欄位級真值對不上」的規模比預期小得多，而且集中在兩個與 vendor 資料無關的角落**。98 條通道之 773 欄唱讀，對不上 88 欄（11.4%）；但**其中 71 欄全部來自 11 張從未落地的 excluded 表**（intraday／資料量物理界限），**另 15 欄全部來自 2 張 infra log 表**（`data_audit_log`／`pipeline_execution_log`）。**真正的 vendor 資料通道：85 條、687 欄、對不上僅 2 欄（0.29%）**。`column_catalog` 對既有 vendor 表是一把準的尺。
2. **真正的瓶頸不是「對不上」，是「沒東西可對」**。98 條通道中 **65 條連世界概念都還沒有**（10 條已 mapped ＋ 23 條在草案待圈選 ＝ 33 條有概念）。`source_column` 是「概念 → 欄」的映射；概念不存在時，欄位級展開在定義上不可為。
3. **機械可自動配對者僅 9/98（9.2%）**。判準＝恰一個非 PK 欄且逐欄唱讀零問題。其餘 89 條須人裁「哪些值欄屬該概念」；展開總面（嚴格非 PK 值欄）**472 欄**，上界 702 欄。
4. **抽樣 10 條之 AI 草擬單位成本＝ 17.6 秒/條**（實測，n=10，sd 7.95，95% CI [11.9, 23.3] 秒），分層外推 98 條 ＝ **29.1 分鐘**。相對 S3 之 08-31→09-30 窗口（30 日）有約 **1,500 倍餘裕**——**AI 產出速率不是關鍵路徑**。
5. **但抽樣之定案率為 0/10**——十條全部卡在「概念未定義」或「結構性待裁」。故**「S3 於某日完成」不可由本抽樣推得**：完成日由 Steward 裁決速率決定，而該速率本輪 **n=0、不可估**。本輪另新增 **6 項**結構性待裁（草案 §6 已有 9 項，合計 ≥15）。

---

## §1 母體唱讀對帳（98 條現行通道；機械輸出）

### 1.1 起始基線（作業前後同值＝零寫入證明，§7）

| 通道列 | 現行列 | `source_column` 非空 | `mapping_status=mapped` | `column_catalog` 列 | 涵蓋 dataset |
|---|---|---|---|---|---|
| 98 | 98 | **0** | 10 | 769 | 97 |

### 1.2 欄級唱讀結果

唱讀口徑＝**逐通道**取 `column_catalog` ∪ 實體表（`information_schema.columns` ＋ `pg_constraint` 之真 PK）之欄名聯集，逐欄比對「欄名存在性／型別／PK」。

| | 欄數 | 佔比 |
|---|---|---|
| 唱讀總欄數（逐通道聯集） | **773** | 100% |
| **對得上** | **685** | **88.6%** |
| **對不上** | **88** | **11.4%** |

> ⚠ 773 為**逐通道**計（`TaiwanStockDelisting` 有 binding 2 與 3 兩條通道，其 3 欄計兩次）。按**相異表**計為 770 欄。

### 1.3 對不上之型態分類（五型＋一通道級型）

| 型態 | 欄數 | 集中在哪 | 具體實例（表．欄） |
|---|---|---|---|
| **`live_missing`**（catalog 有、實體表無） | **71** | **100% 來自 11 張從未落地之 excluded 表** | `TaiwanFuturesTick.price`、`TaiwanStockKBar.close` |
| **`type_unregistered`**（catalog `inferred_type` 為 NULL） | **15** | **100% 來自 2 張 infra log 表** | `data_audit_log.logged_at`（catalog NULL vs live `timestamp without time zone`）、`pipeline_execution_log.task`（NULL vs `character varying`） |
| **`pk_mismatch`**（catalog `is_pk` 與實體 PK 不符） | **2** | 同上 2 張 infra 表 | `data_audit_log.id`（catalog `is_pk=False` vs 實體為 PK）、`pipeline_execution_log.id`（同型） |
| **`catalog_missing`**（實體表有、catalog 未登錄） | **1** | vendor 側 | **`fred_series.realtime_start`**（實體 `date` 且為 PK 之一，catalog 完全沒有這欄） |
| **`type_mismatch`**（型別不符） | **1** | vendor 側 | **`TaiwanStockConvertibleBondDailyOverview.date`**（catalog `VARCHAR` vs 實體 `date`） |
| **`table_absent`**（通道級：`source_table` 無實體表） | **11 條通道** | excluded 資料集 | binding 11 `TaiwanFuturesTick`、24 `TaiwanStockKBar`、42 `TaiwanStockBlockTradingDailyReport` … |

**分母拆解（本節最重要的一句）**：

| 子母體 | 通道數 | 唱讀欄 | 對不上 | 比例 |
|---|---|---|---|---|
| 全部（含未落地） | 98 | 773 | 88 | 11.4% |
| 僅實體表存在者 | 87 | 702 | 17 | 2.42% |
| **僅 vendor × 實體表存在** | **85** | **687** | **2** | **0.29%** |
| 僅 infra log 表 | 2 | 15 | 15 | **100%** |

⇒ **「column-level 真值對不上的規模」在 vendor 資料層 ＝ 2 欄／687 欄**。原先擔心的大規模欄位漂移**不存在**；`live_missing` 之 71 欄不是漂移，是「這 11 個 dataset 依 #4 日為最小單位／資料量物理界限被排除，從未落地」——catalog 記的是 API 探測所得之 schema，不是落地真值。

**誠實補充**：`column_catalog.last_verified` 之 754/769 列早於 30 日（最新 2026-06-29、最舊 2026-06-16），15 列為 NULL。上表之「對得上」係與**今日實體表**比對之結果，故 catalog 雖久未刷新，**內容仍屬正確**——這是實測結論，不是因為 catalog 新。

### 1.4 展開難度桶（值欄＝實體欄 − 真 PK 欄）

| 桶 | 通道數 | 值欄合計 | 意義 |
|---|---|---|---|
| **B0 無實體表** | 11 | 0 | catalog 有登錄但表不存在 ⇒ 無真值可驗 |
| **B1 零值欄（全 PK）** | 10 | 0 | 全部欄皆入 PK ⇒ **值欄偵測器在此失效**（見 §4-6） |
| **B2 單值欄** | 10 | 10 | 恰一非 PK 欄 ⇒ 機械唯一 |
| **B3 2–4 值欄** | 29 | 83 | 須人裁 |
| **B4 5–9 值欄** | 25 | 171 | 須人裁 |
| **B5 ≥10 值欄** | 13 | 208 | 須人裁，且多為多值表（尚須列鍵，M-W4） |
| **合計** | **98** | **472** | 上界＝全部 live 欄 **702** |

**自動配對率＝9/98（9.2%）**。B2 有 10 條，但 binding 12（`fred_series`）因 `catalog_missing` 被扣除——catalog 這把尺自己對不上時不得據以自動配對，否則會把錯的欄名寫進 Registry。

**多值欄通道 67 條**（>1 值欄）。這 67 條全部撞到同一個結構問題：`world_channel_binding.source_column` 是**單一 `text` 欄**（親驗無 CHECK 約束、無分隔符約定），無法承載「一個概念對多欄」。

### 1.5 概念覆蓋（決定「有沒有東西可展開」）

| 狀態 | 通道數 | 說明 |
|---|---|---|
| `mapped`（概念已定、已採認前） | **10** | 6 個 `world_concept` 身分列 |
| 草案已擬、待 Steward 圈選 | **23** | `wm_channel_registration_draft_20260803.md` §4 |
| **完全無概念** | **65** | 既無 `concept_key`，亦不在任何草案 |

⇒ WM.36 欄 3 是「**世界概念** → 通道位置」之映射。65 條通道**沒有概念可映射**；對它們談 `source_column` 是先有欄後有概念，順序顛倒。

---

## §2 抽樣：10 條逐條展開與實際耗時

**抽樣口徑**：分層抽樣，層＝§1.4 之六桶，按母體比例以最大餘數法配額，層內以 `md5("w2:<binding_id>")` 排序取前 n（決定性，同 seed 可完全復現）。配額＝`{B0:1, B1:1, B2:1, B3:3, B4:3, B5:1}`。

**計時口徑**：兩段分開量。
- **機械段**（唱讀對帳＋值欄枚舉）：程式內 `perf_counter`，全 98 條 <1 秒，**單條 <0.01 ms**，成本可視為零。
- **草擬段**（判定哪些欄屬該概念、識別阻塞）：AI wall-clock，逐條以 shell timestamp 夾量，記於 `scratchpad/w2_expand_log.tsv`。**此為 AI self-reported 速率，非 hugo 之速率**。

| # | binding | 表 | 桶 | 值欄 | 展開結果 | **耗時** |
|---|---|---|---|---|---|---|
| 1 | 7 | `TaiwanStockConvertibleBondInfo` | B3 | 4 | 提案 `tw.convertible_bond.terms`；`source_column`＝{IssuanceAmount, InitialDateOfConversion, DueDateOfConversion}。`cb_name` 屬識別標籤抑或條款內容＝未決。**阻塞**：概念未定義＋多欄裝不進單一 text 欄 | **21.9 s** |
| 2 | 11 | `TaiwanFuturesTick` | B0 | 0 | **不可展開**：excluded intraday、庫內零落地列；catalog 之 5 欄係 API 探測所得而非落地真值 ⇒ 填 `source_column` 等於登錄不可驗宣稱（違 #1 source-pure）。**阻塞**：11 條未落地通道是否屬 WM.35「已落地通道」射程 | **21.2 s** |
| 3 | 31 | `TaiwanStockBalanceSheet` | B3 | 2 | 草案概念 `tw.financial_statement.balance`。`source_column`＝`value`（long-form：`type`＝科目已入 PK 為列鍵、`origin_name`＝供應商原始標籤屬 provenance 非事實載體）。**殘留**：一概念對全表科目 vs 一科目一概念之粒度未裁 | **9.5 s** |
| 4 | 37 | `JapanStockPrice` | B4 | 6 | 提案 `jp.daily_bar`；observation 通道＝{Open, High, Low, Close, Volume}。**結構性發現**：`Adj_Close` 為 WM.15／A.58 之衍生觀測，與原始價**同表**，而單一 binding 列只有一個 `channel_role` ⇒ 須拆第二列。**阻塞**：命名空間（Q-R8）＋A.35 第三項跨市場軸宣告 | **19.6 s** |
| 5 | 50 | `GoldPrice` | B2 | 1 | `source_column`＝`Price`（**機械唯一**：恰一非 PK 欄、逐欄唱讀零問題）。**殘留**：計價幣別／單位不在 schema 內；欄 3 可機械填，欄 1／欄 5 仍須人裁 | **9.5 s** |
| 6 | 62 | `TaiwanStockShareholding` | B5 | 11 | 草案概念 `tw.foreign_ownership.stock`。逐欄裁定：**入 6**（ForeignInvestment{Shares, SharesRatio, RemainingShares, RemainRatio, UpperLimitRatio}、ChineseInvestmentUpperLimitRatio）；**出 5**（`InternationalCode`＝A.28 第二識別碼體系之 identity claim 非持股事實；`stock_name`＝標籤；`note`＝異動原因；`NumberOfSharesIssued`＝**另一世界事實**應另立概念；`RecentlyDeclareDate`＝草案 Q-R5-iii 兩讀未決）。另：兩個 UpperLimitRatio 屬法令上限（監理狀態）抑或持股狀態，可能須再拆概念 | **28.5 s** |
| 7 | 65 | `TaiwanOptionInstitutionalInvestorsAfterHours` | B3 | 4 | 提案 `tw.option.institutional_flow.after_hours`；`source_column`＝{long_deal_amount, long_deal_volume, short_deal_amount, short_deal_volume}（四欄皆為同一流量事實之維度切面，全數入）。**殘留**：PK 含 option_id／call_put／institutional_investors 三列鍵 ⇒ 消費端仍須內嵌字面（M-W4 原型）；盤後時段 ts 語義須另宣告 | **11.8 s** |
| 8 | 80 | `TaiwanStockSplitPrice` | B4 | 6 | A.21 已明文錨定（股票分割＝一級世界事件、ts＝恢復買賣日；catalog 之 `date` 中文名逐字為「分割恢復買賣日」＝機械對錨）。提案 `tw.corporate_action.split`（與既有 `tw.corporate_action.ex_dividend` 平行）；**入 3**＝{before_price, after_price, type}；**出 3**＝{max_price, min_price, open_price}＝**A.26 PriceLimit 之另一世界狀態** ⇒ 同表第二概念、須第二 binding 列 | **30.8 s** |
| 9 | 93 | `TaiwanBusinessIndicator` | B4 | 8 | 草案概念 `tw.business_cycle_indicator`（單一概念）。**與 A.11 抵觸之發現**：A.11 逐字「每一指標為世界量，非任何供應商之 series 識別」⇒ 領先／同時／落後／對策信號各為獨立世界量，本表 8 值欄應為 7–8 個概念而非 1 個。`monitoring_color` 為 `monitoring` 之分級呈現（同一事實兩表徵）。**阻塞**：須 Steward 裁 | **12.9 s** |
| 10 | 97 | `TaiwanFuturesDaily` | B1 | 0 | 提案 `tw.futures.daily_bar`。**機械偵測器在此失效**：13 欄全入 PK，值欄數＝0 但事實載體確實存在＝{close, max, min, open, settlement_price, spread, spread_per, volume, open_interest}（9 欄），鍵＝{futures_id, contract_date, date, trading_session} | **10.3 s** |

**統計**：總 176.0 s（2.93 分）／均 **17.6 s**／sd **7.95**／中位 16.3 s／全距 9.5–30.8 s／95% CI **[11.9, 23.3] s**。

**⚠ 定案率 0/10**。十條**沒有一條**能在本輪產出可直接寫入 DB 的 `source_column`——每一條都停在「概念未定義」或「結構性待裁」。故上表量到的是**「產出一份提案並識別阻塞」的成本**，**不是「完成登錄」的成本**。

---

## §3 規模外推

### 3.1 推導式與結果

**分層外推**（層均 × 層母體，加總）：

```
B0 無實體表   1 樣本 × 21.2s → 11 條 =  233.2s
B1 零值欄     1 樣本 × 10.3s → 10 條 =  103.0s
B2 單值欄     1 樣本 ×  9.5s → 10 條 =   95.0s
B3 2-4值欄    3 樣本 × 14.4s → 29 條 =  417.6s
B4 5-9值欄    3 樣本 × 21.1s → 25 條 =  527.5s
B5 ≥10值欄    1 樣本 × 28.5s → 13 條 =  370.5s
                                 ─────────────
                            98 條 = 1,747s = 29.1 分
```

**簡單外推**（不分層）：98 × 17.6 s ＝ 1,725 s ＝ **28.7 分**，95% CI **[19.5, 38.0] 分**。兩法相差 1.3%。

### 3.2 外推假設（逐項明載）

| # | 假設 | 是否可能不成立 |
|---|---|---|
| A1 | 未抽中之 88 條，其草擬成本與同桶樣本同分佈 | **可能不成立**：B0／B1／B2／B5 四層各只有 **1 個樣本**，層內變異未估 |
| A2 | 草擬成本主要由值欄數驅動（故以桶分層） | 樣本內部分支持（B5 最慢 28.5s、B2 最快 9.5s），但 binding 80（B4, 6 值欄）耗 30.8s 最久——**驅動因子其實是「概念未定義且須新查條文」**，非值欄數 |
| A3 | AI wall-clock 可代表工作量 | **僅代表 AI 側**。hugo 之逐條決定時間、Steward 之裁決時間**完全未量** |
| A4 | 每條通道各自獨立、無規模經濟 | 偏保守：同型問題（如多值表列鍵）一次裁定可覆蓋多條，實際總量應**低於**外推 |
| A5 | 「草擬完成」＝「登錄完成」 | **明確不成立**：定案率 0/10 |

**信賴邊界之誠實陳述**：29.1 分之點估計**只對「AI 產出 98 份提案」這件事有效**，且其 95% CI 在四個 n=1 的層上**無法計算**（本文報的 CI 係以不分層之 n=10 算出，已低估真實不確定性）。**不得**把它讀成「S3 只要 29 分鐘」。

### 3.3 機械結論（M-W2 驗收 (d) 所要求之一句）

> **以本輪實測速率，98 條通道之 AI 草擬於 29.1 分鐘完成，相對 S3 之 08-31→09-30 窗口（30 日）有約 1,500 倍餘裕 ⇒ AI 產出速率不是 10-14 的關鍵路徑。**
> **但本抽樣之定案率為 0/10，故「S3 於 YYYY-MM-DD 完成」不可由本抽樣推得。** 完成日之決定因素為：(i) **65 條通道之世界概念尚未定義**（連草案都沒有）；(ii) **≥15 項結構性待裁未決**（草案 §6 九項 ＋ 本輪新增六項，見 §4），其中 **Q-R1（unmapped→mapped 之形制）未裁前，任何登錄 SQL 皆不得執行**（草案 §7 明載）。此三者之速率本輪 **n=0**，**不可估、不編造**。

**由此可機械推得的排程結論**：M-W5 S3 之關鍵路徑**不是欄位展開的人力**，而是**裁決佇列**。若要讓 08-31 起跑有意義，08-31 前須完成的是**裁決**而非備料——備料本身半小時可清。

---

## §4 本輪新增之結構性待裁（6 項；AI 呈案，不代裁）

> 草案 `wm_channel_registration_draft_20260803.md` §6 已列 Q-R1…Q-R9。以下為**本輪抽樣新發現**、該草案未涵蓋者。

| # | 問題 | 機械事實 | 影響條數 |
|---|---|---|---|
| **W2-1** | **一個概念對多欄，要怎麼裝？** `world_channel_binding.source_column` 為單一 `text`，親驗**無 CHECK、無分隔符約定**。是 (a) 逗號分隔字串、(b) 一欄一 binding 列、還是 (c) 改表結構為陣列？ | 多值欄通道 **67 條**全部撞到；(b) 會使 98 條膨脹為約 **472 列** | **67** |
| **W2-2** | **從未落地之通道可否登錄欄位級映射？** 11 條通道之表不存在，catalog 之 71 欄係 API 探測 schema、非落地真值。填 `source_column` ＝ 登錄不可驗宣稱 | WM.35 之義務主體為「通道落地之作成者」，而這些通道**從未落地** | **11** |
| **W2-3** | **同表兼含 observation 與 derived 者如何登錄？** `JapanStockPrice` 之 `Adj_Close` 為 A.58／WM.15 衍生觀測，與原始價同表；但一 binding 列只有一個 `channel_role`（CHECK 限 observation／derived） | 台股是兩張表（binding 75／81）故無此問題；外國市場表是一張 | 至少 1（未全掃） |
| **W2-4** | **A.11「每一指標為世界量」與草案之單表單概念讀法抵觸** `TaiwanBusinessIndicator` 8 值欄，草案 §3.10 擬 1 個概念；A.11 逐字要求每一指標各為世界量 ⇒ 應為 7–8 個 | 若採 A.11 讀法，概念數將遠超「23 表 → 23 概念」 | 總經／指標類多條 |
| **W2-5** | **同表兼含兩個世界概念（非同一事實之兩通道）** `TaiwanStockSplitPrice` 同時載 A.21 分割事件（before/after_price）與 A.26 每日參考價／漲跌停狀態（max/min/open_price） | 與草案 §3.2 之「一表供兩事實」同型，但草案僅涵蓋 `DailyShortSaleBalances` 一例 | 至少 1（未全掃） |
| **W2-6** | **全 PK 表之值欄偵測器失效** 10 條通道之欄全部入 PK（`TaiwanFuturesDaily` 13/13、`TaiwanOptionDaily` 13/13、`TaiwanStockGovernmentBankBuySell` 7/7），機械值欄數＝0，但事實載體確實存在（如 binding 97 之 9 欄） | ⇒ **展開總面 472 欄為低估**；真值介於 472 與 702 之間。與草案 Q-R7（值欄入 PK）同根 | **10** |

---

## §5 誠實：本輪未覆蓋範圍

1. **未逐條展開 88/98 條**——僅抽 10 條（覆蓋率 **10.2%**）。四個層各只有 1 個樣本（B0／B1／B2／B5），層內變異未估。
2. **未量 hugo／Steward 之決定速率**（n=0）——§3.3 之「不可推得完成日」即源於此，非保留。
3. **未修**任何對不上之欄。`fred_series.realtime_start` 未登錄、`TaiwanStockConvertibleBondDailyOverview.date` 型別不符、2 張 infra 表 15 欄型別未登錄——**全部原樣留著**（修 catalog 屬 `build_catalog.py --db-only` 之射程，非本輪；且該路徑會寫 DB）。
4. **未判定** `data_audit_log`／`pipeline_execution_log` 兩條 infra 通道**是否應該在 Registry 裡**。它們的 `provenance.vendor_source='infra'`，不是世界觀測通道；但本輪不代裁其去留。
5. **未全掃** W2-3／W2-5 之影響條數——兩項各只在抽中的那 1 條上發現，母體有幾條同型**未查**（須逐表讀 catalog 中文名，成本同 §2 之草擬段）。
6. **未驗** `column_catalog` 之 `column_name_zh`／`anti_leakage_flag` 內容正確性——本輪只比對欄名／型別／PK 三項，中文名與 anti-leakage 旗標**只讀不驗**。
7. **未觸** M-W3（M3 絞殺判準結構不可達）——該項在 M-W5 之前，本輪不涉。

---

## §6 復現指令（全唯讀、零 Claude usage）

```bash
cd /home/hugo/project/augur

# ① 母體唱讀對帳總表（§1.1／1.2／1.3 之統計、§1.4 之桶、自動配對率）
venv/bin/python scripts/reconcile_channel_columns.py --survey

# ② 逐列印出 88 個對不上之欄（§1.3 之實例）
venv/bin/python scripts/reconcile_channel_columns.py --issues

# ③ §2 之分層抽樣（決定性；同 seed 必得同 10 條）
venv/bin/python scripts/reconcile_channel_columns.py --sample 10 --seed w2

# ④ 逐條明細（§2 表格之逐欄依據；10 條全部）
for b in 7 11 31 37 50 62 65 80 93 97; do \
  venv/bin/python scripts/reconcile_channel_columns.py --binding $b; done

# ⑤ 回歸鎖紅綠自測（免 DB 免 API）
venv/bin/python scripts/reconcile_channel_columns.py --selftest

# ⑥ #35 先驗紅：10 個突變逐一注入，親證自測會紅
venv/bin/python scratchpad/w2_red_proof.py

# ⑦ 兩道機械閘（本檔新增之 script 須通過）
venv/bin/python scripts/check_cmd_matrix.py
venv/bin/python scripts/check_false_assertions.py --gate
```

**§1.5 概念覆蓋、§3 之分層外推**（純 SQL／算術，可獨立重跑）：

```bash
cd /home/hugo/project/augur && venv/bin/python - <<'PY'
import sys; sys.path.insert(0,"src"); sys.path.insert(0,"scripts")
import statistics as st
from augur.core import db
import reconcile_channel_columns as M
DRAFT23=[78,60,56,49,62,43,68,35,85,93,44,38,69,23,86,51,53,77,31,83,70,17,30]
with db.connect() as conn:
    with conn.cursor() as cur:
        cur.execute("SET statement_timeout='40s'")
        cur.execute("""SELECT count(*) FILTER (WHERE mapping_status='mapped'),
              count(*) FILTER (WHERE mapping_status='unmapped' AND binding_id = ANY(%s)),
              count(*) FILTER (WHERE mapping_status='unmapped' AND NOT (binding_id = ANY(%s))),
              count(*) FROM world_channel_binding WHERE superseded_at IS NULL""",
              (DRAFT23, DRAFT23))
        print("概念覆蓋 (mapped, 草案23, 無概念, 總計) =", cur.fetchone())
    rows = M._fetch(conn)
INFRA={'data_audit_log','pipeline_execution_log'}
def cnt(rs): return (sum(1 for r in rs for c in r["cols"] if c["issues"]),
                     sum(len(r["cols"]) for r in rs))
ex=[r for r in rows if r["n_live"]>0]
print("87 條(實體表存在):", cnt(ex))
print("85 條 vendor:", cnt([r for r in ex if r["source_table"] not in INFRA]))
print("2 條 infra:",  cnt([r for r in ex if r["source_table"] in INFRA]))
print("live 欄合計", sum(r['n_live'] for r in rows), "／嚴格值欄", sum(r['n_value'] for r in rows),
      "／多值欄通道", sum(1 for r in rows if r['n_value']>1))
t={7:21.9,11:21.2,31:9.5,37:19.6,50:9.5,62:28.5,65:11.8,80:30.8,93:12.9,97:10.3}
idx={r['binding_id']:r for r in rows}; strat={}
for bid,sec in t.items(): strat.setdefault(idx[bid]['bucket'],[]).append(sec)
N={b:sum(1 for r in rows if r['bucket']==b) for b,_ in M.BUCKETS}
tot=sum(N[b]*st.mean(v) for b,v in strat.items())
v=list(t.values()); m=st.mean(v); sd=st.stdev(v); h=2.262*sd/len(v)**.5
print(f"均 {m:.1f}s sd {sd:.2f} CI[{m-h:.1f},{m+h:.1f}]s")
print(f"分層外推 {tot:.0f}s = {tot/60:.1f} 分；簡單外推 {98*m/60:.1f} 分 CI[{98*(m-h)/60:.1f},{98*(m+h)/60:.1f}] 分")
PY
```

---

## §7 唯讀證明、回歸鎖紅證、殘項

### 7.1 零寫入證明（M-W2 驗收 (e)）

作業前後複查同值：`world_channel_binding` **98** 列／`source_column` 非空 **0**／`mapping_status='mapped'` **10**／`world_concept` 身分列 **6**／`world_concept_version` 現行列 **6**。
零 DDL、零 DB 寫入、零 commit、零 systemctl；未觸 FinMind／FRED 任何 API；未搶 `heavy_slot`；未跑任何 `--apply`／`--allow-apply`／`--morning`；未改任何既有檔（`scripts/reconcile_channel_columns.py` 與本檔為新增）。全部查詢皆帶 `statement_timeout`（30–60 s），最長單次執行 **1.9 s**。

一行複驗：

```bash
venv/bin/python scripts/reconcile_channel_columns.py --survey | head -2
# 期望：source_column 已填：0/98　｜　mapping_status=mapped：10/98
```

### 7.2 新增檔與其合規（CLAUDE #18／#29）

`scripts/reconcile_channel_columns.py` — 唯讀對帳工具，**非重複造輪**：既有 `src/augur/audit/reconcile.py` 為 DB↔**API** byte-level attestation（需 FinMind／FRED，凍結中不可用）；`scripts/compare_shadow_binding.py` 為絞殺影子比對；兩者皆不做 catalog↔實體表↔binding 之欄位級唱讀。本支具：無參數 graceful（印母體總表；DB 不可達則誠實印原因、rc=0）／執行指令矩陣（六式）／`--selftest` 免 DB 免 API／`--sample` 參數化通用（任意 N 與 seed）。`check_cmd_matrix` 受檢 **495 支／缺漏 0**；`check_false_assertions --gate` **無新增**。

### 7.3 #35 先驗紅之紅證（10 個突變全部驗紅）

基線自測 rc=0（22 條全綠）。逐一注入突變後重跑，**全部轉紅**，還原後回綠：

| 突變 | rc | 失敗條數 | 若不紅代表什麼 |
|---|---|---|---|
| M1 `reconcile_column` 只回第一個問題碼 | 1 | 2 | 壓成單一 verdict 會靜默吃掉第二個問題 |
| M2 兩側皆無此欄時靜默回「對得上」 | 1 | 2 | fail-open：不存在之欄被判對得上 |
| M3 型別比對永遠放行 | 1 | 3 | catalog 型別漂移查不出來 |
| M4 `auto_pairable` 只看有無問題、不看桶 | 1 | 3 | 多值表被誤判為可機械自動配對 |
| M5 `auto_pairable` 忽略唱讀問題 | 1 | 2 | catalog 自己對不上時仍自動配對＝把錯欄名寫進 Registry |
| M6 桶邊界 off-by-one | 1 | 2 | 難度分佈失真、外推跟著錯 |
| M7 `allocate_strata` 寫死配置 | 1 | 4 | 分層抽樣變裝飾品 |
| M8 `allocate_strata` 無視 n 上限 | 1 | 2 | n 大於母體時虛報樣本數 |
| M9 `sample_order` 忽略 seed | 1 | 2 | 「可復現抽樣」宣稱是假的 |
| M10 `table_absent` 不標記 | 1 | 2 | 未落地通道被當正常通道計入可展開面 |

還原後 rc=0。突變harness＝`scratchpad/w2_red_proof.py`（可重跑，見 §6-⑥）。
**自測係餵真列形**：`TaiwanStockConvertibleBondDailyOverview.date`（VARCHAR vs date）、`data_audit_log.id`（NULL 型別＋PK 不符）、`fred_series.realtime_start`（catalog 缺登錄）、真母體分佈 `{11,10,10,29,25,13}` 皆為本輪唯讀親驗之真值；**無任何「原始碼含某字串」型斷言**。

### 7.4 殘項

1. 四個層各僅 1 樣本（§5-1）——若要收窄外推 CI，最小增量＝各層再抽 2 條（成本約 4 × 2 × 17.6 s ≈ 2.4 分）。
2. W2-3／W2-5 之母體影響條數未全掃（§5-5）。
3. `column_catalog` 之中文名／anti-leakage 旗標未驗（§5-6）。
4. 本輪 6 項新待裁未併入草案 §6——**併表屬文件工作，未做**（不擅改他人報告，見 CLAUDE #19）。

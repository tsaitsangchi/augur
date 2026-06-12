# augur 特徵設計計畫 — 第一性原理 × 欄位 → 預測特徵(2026-06-12)

**性質**:設計計畫(#15:**計畫、非成果**;任何特徵之預測力未經 walk-forward 驗證前皆為假說)。
**前提**:假設核心股已選定、其資料**完整且精準**(PHASE 8 過 gate)。
**問題**:第一性原理下,哪些**欄位**能生成預測「未來 H 日橫斷面相對強弱」的特徵值。
**欄位實證**:全部欄名/中文取自 schema catalog(live API 取樣),非記憶(#20)。

---

## 〇、第一性出發點

預測目標(靈魂):**給定 as-of 日 t,排序「誰未來 H 日相對強」**(週/月/季/年)。非預測絕對漲跌。

第一性分解——股價未來相對變動,只能來自:

> **未來報酬 ≈ f( ①價格行為慣性/反轉 + ②真金白銀的供需壓力 + ③企業價值引擎變化 + ④價格-價值缺口
> + ⑤公司行為訊號 + ⑥環境制約(全市場共同) + ⑦橫斷面結構位置 ) + 不可知噪音**

每一軸都必須過北極星三問:有真實 API 源(#1)?t 日當下真可得(#8)?對「相對強弱」有區分力假說?

**核心轉換原則**:目標是**相對**強弱 → 特徵也應**相對化**(同日橫斷面 z-score / percentile-rank /
產業內 demean),原始絕對值僅是中間量。

---

## 一、七軸:欄位 → 特徵族

### 軸① 價格行為(市場已聚合的信念)— P 類
| 表.欄 | 中文 | 特徵族(數學轉換) |
|---|---|---|
| `TaiwanStockPriceAdj.close` | **還原**收盤價 | **報酬一律用還原價**(除權息跳空非真報酬):log return 1/5/20/60/120/252d、動能、長短動能差(反轉) |
| `TaiwanStockPriceAdj.max/min/open/close` | 高低開收 | 真實波幅、區間位置 (close−min)/(max−min)、跳空 |
| `TaiwanStockPrice.close` | 原始收盤價 | 價位心理特徵(整數關卡距離以 rolling rank 表達,不硬編關卡值 #9) |
| `Trading_Volume/Trading_money/Trading_turnover` | 量/金額/迴轉 | 量能 z、量價背離(量↑價↓)、流動性(Amihud=|ret|/money)、迴轉率變化 |
| `spread` | 漲跌價差 | 日內力道;與 close 結合成單日 K 形態量值(實體/影線比) |
| `TaiwanStock10Year.close` | 十年線 | 超長期均值回歸位置:close_adj/十年線 −1 |
| `TaiwanStockDayTrading.Volume/BuyAmount/SellAmount` | 當沖量/金額 | 當沖佔比(投機熱度)、當沖買賣不平衡 |

### 軸② 資金流/籌碼(真金白銀的供需壓力)— P 類
| 表.欄 | 中文 | 特徵族 |
|---|---|---|
| `InstitutionalInvestorsBuySell.name/buy/sell` | 法人別買賣金額 | 三大法人淨買超/市值、流向 5/20/60d rolling sum、連續性(同號天數)、外資 vs 投信分歧 |
| `MarginPurchaseShortSale.MarginPurchaseTodayBalance/Limit` | 融資餘額/額度 | 融資使用率、融資增減速;`ShortSaleTodayBalance` 融券餘額 → 券資比、軋空壓力(券餘/日均量) |
| `TaiwanDailyShortSaleBalances.SBL*` | 借券系列 | 借券賣壓存量/增量(SBLShortSalesCurrentDayBalance/日均量)、借券回補(Returns/ShortCovering) |
| `Shareholding.ForeignInvestmentSharesRatio/UpperLimitRatio` | 外資持股比/上限 | 外資持股變化 5/20/60d、距上限空間(可加碼餘地) |
| `HoldingSharesPer.HoldingSharesLevel/people/percent` | 持股級距/人數/% | 大戶比(高級距 percent 合計)變化、散戶人數變化、集中度趨勢(申報週頻 → as-of 取最近) |
| `SecuritiesLending.transaction_type/volume/fee_rate` | 借券交易/費率 | 借券費率(放空成本=看空強度)、新借 vs 還券淨額 |
| `GovernmentBankBuySell.buy/sell/buy_amount/sell_amount` | 官股行庫買賣 | (半事件,真零)官股淨買 rolling 20/60d、護盤訊號 flag |

### 軸③ 企業價值引擎(基本面)— P-lag 類(發布日 gate 鐵則)
| 表.欄 | 中文 | 特徵族 |
|---|---|---|
| `MonthRevenue.revenue/revenue_month/revenue_year` | 單月營收 | **最高頻基本面**:YoY、MoM、3m-YoY 動能、創 N 月新高 flag(N=12 calendar 慣例)、累計 YoY |
| `FinancialStatements(type,value)` 選科目 | 損益科目 | 營收/毛利/營益/淨利/EPS:YoY、margin(毛利率/營益率/淨利率)及其變化(Δmargin) |
| `BalanceSheet(type,value)` 選科目 | 資產負債科目 | ROE/ROA(NI/權益、NI/資產)、負債比、流動比、存貨與應收變化(營運品質) |
| `CashFlowsStatement(type,value)` 選科目 | 現金流科目 | OCF/NI(應計品質)、自由現金流/市值、資本支出強度 |

> **科目選定原則(#9 防硬編)**:比率定義(ROE、毛利率)= 會計學標準恆等式(思想/慣例,如同 log return),
> 非預測值,允許;**禁止**的是「ROE>15% 才算好」這類硬編閾值——一律以橫斷面 rank/z 表達相對位置。
> 科目鍵以 `type` 欄值選取,**canonical 科目集以核心股全覆蓋為準據**(data-driven 收斂,#1)。

### 軸④ 價格-價值缺口(估值)— P 類
| 表.欄 | 中文 | 特徵族 |
|---|---|---|
| `TaiwanStockPER.PER/PBR/dividend_yield` | 本益比/淨價比/殖利率 | 估值水位=vs 自身 252d rolling percentile + vs 同日橫斷面 rank + vs 產業內 rank(三層相對化,無硬編「便宜」閾值) |
| `TaiwanStockMarketValue.market_value` | 市值 | log(市值)=規模因子;市值橫斷面 rank(size 思想,值由資料定 #9) |
| `Dividend.CashEarningsDistribution` 等 | 現金/股票股利 | 股利政策變化(增/減配 flag)、配發率 |

### 軸⑤ 公司行為/事件訊號 — E 類(真零語意:#7 PASS 前提下無列=真 0)
| 表.欄 | 特徵族 |
|---|---|
| `Dividend.AnnouncementDate/AnnouncementTime`(**公告時點,API 自帶!**) | 事件 as-of 以**公告日**為準(非除息日)→ 零洩漏 |
| `DividendResult`(除息實際) | 填息速度(除息後 N 日回補比例)— 用還原/原始價對算 |
| `BlockTrade.price/volume/trading_money` | 鉅額交易折溢價(price vs 當日 close)、頻率(大資金意圖) |
| `DispositionSecuritiesPeriod` | 處置股 flag/處置剩餘天數(流動性枷鎖) |
| `Suspended/MarginShortSaleSuspension/DayTradingSuspension` | 停牌/停券/停沖 flag 與 days-since |
| `News.date/stock_id`(**只用 count**) | 新聞密度 z(關注度);**title/source 文字不入特徵(#9 禁情緒字典)** |
| `CapitalReduction/SplitPrice/ParValueChange` | 減資/分割/面額變更 days-since flag(結構變化期不確定性) |

### 軸⑥ 環境制約(全市場共同)— X 類 → `context_values`(panel 前提,非個股判準)
| 來源 | 特徵族(context) |
|---|---|
| `TotalReturnIndex(TAIEX/TPEx).price` | 大盤動能/波動 → 個股 **beta、相對大盤強弱**(個股×context 交互=個股特徵) |
| `BusinessIndicator.leading/monitoring` | 景氣領先指標動能、燈號分數變化 |
| `ExchangeRate(USD).cash_buy/spot_*` | 台幣動能(外資匯損敏感) |
| `InterestRate/GovernmentBondsYield` | 資金成本水位/變化、期限利差 |
| `fred_series`(T10Y2Y/FEDFUNDS/VIXCLS/DTWEXBGS/DCOILWTICO…) | 美債利差/聯邦利率/恐慌/美元/油 —— **vintage 警語:嚴格 PIT 須 ALFRED,先以發布滯後保守 lag + metadata 標注(#8)** |
| `TotalInstitutionalInvestors/TotalMarginPurchaseShortSale` | 全市場法人/融資情緒 |
| `CnnFearGreedIndex`、期權 PCR/未平倉(F2g) | 市場情緒極值 |

### 軸⑦ 橫斷面結構(相對化的座標系)— R 類
| 來源 | 用法 |
|---|---|
| `IndustryChain.industry/sub_industry` | **產業內相對化**(demean/rank):同業比較才是「相對強弱」的正確座標;產業動能(產業內個股特徵聚合) |
| `TaiwanStockInfo.type/industry_category` | 上市/上櫃分群 normalize;categorical(one-hot,值=API 事實非知識字典) |
| `TaiwanStockDelisting` | 歷史宇宙 survivorship(#8)— 非特徵,是 label/宇宙基礎 |

---

## 二、轉換武器庫(全部 = 真實值之數學轉換,#1)

`log / diff / ratio / rolling(mean,std,sum,max,min) / zscore(self) / percentile-rank(self-history)
/ cross-sectional rank·z(同日) / industry-demean / days-since / count-in-window / flag`
視窗一律 5/20/60/120/252(calendar 慣例,builder 先例);**無任何預測性閾值入公式(#9)**。

## 三、紅線(明確不用)

- `News.title/source/link` 文字內容(#9 禁 sentiment/theme 字典)→ 只用 count。
- 任何「好壞閾值」(PER<15、ROE>15%…)→ 一律相對化(rank/z)。
- `TradingDate`(日曆=infra)、`Info.stock_name` 等識別欄。
- OUT_OF_UNIT 3 表(暫緩)、intraday 8 表(#4 永排)。
- label 設計屬 model 層(H 日還原價 log return → 橫斷面 rank);此處僅立鐵則:**label 窗與訓練 purge(#8)**。

## 四、anti-leakage 金礦(本計畫實證新發現)

1. `Dividend.AnnouncementDate/AnnouncementTime` —— **API 自帶公告時點**,股利事件 as-of 可精確到公告日。
2. `MonthRevenue.create_time` —— 疑似資料建立時戳,**若=入庫公告時點 → 月營收 PIT 可直接用**(待實證語意)。
3. `Shareholding.RecentlyDeclareDate` —— 申報日欄,持股資料之 as-of 錨。
4. 財報三表(`type/value` 長表)**無公告欄** → 仍需法定申報期限保守 lag(F2 roadmap 三.1)。

## 五、與 F2 roadmap 銜接

本計畫=「**欄位→特徵內容**」設計;落地順序/工程=`augur_f2_feature_expansion_roadmap_20260612.md`
(F2b 籌碼 → F2c 估值 → F2d 基本面 → F2e context → F2f 事件 → F2g 衍生/國際)。
每一特徵落地前置不變:**全史 sync ∧ #7 PASS ∧ 發布時點判準記錄**;落地後以 #11 五鏡治理存廢。

## 六、待實證

- [ ] `MonthRevenue.create_time` 語意(=公告時點?)— PIT 月營收的關鍵
- [ ] 財報三表科目 `type` 值域 × 核心股覆蓋率(canonical 科目集收斂)
- [ ] `HoldingSharesPer` 申報頻率(週?)與 as-of 規則
- [ ] `DayTrading.BuyAfterSale` 值域語意
- [ ] 法人 `name` 值域(外資/投信/自營 分類鍵)
- [ ] `TotalReturnIndex` 之 `stock_id` 值域(TAIEX/TPEx)再證

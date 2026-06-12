# augur 特徵設計計畫 — 八二法則「思想」× 欄位 → 預測特徵(2026-06-12)

**性質**:設計計畫(#15:計畫、非成果;預測力未經 walk-forward 驗證前皆為假說)。
**前提**:核心股已選定、資料完整且精準(同第一性計畫)。
**命題**:取八二法則之**思想**(#9 允許的啟發層)、**剔除一切特定值**(`0.8/0.2`、20/60/20、
decile 切點皆禁入公式)→ 哪些欄位能生成特徵。
**思想系譜**:承憲章附錄 B「量子金融藍圖→八二法則」之紀律化(#9/#16:思想可入、數字不回流)。

---

## 〇、思想萃取:把 80/20 的數字剝掉,剩下什麼?

八二法則的本質**不是** 0.8 或 0.2,而是四個可量化的「思想不變量」:

1. **不均勻是常態**——結果分布天然偏斜/重尾,少數單位貢獻多數結果。
2. **少數關鍵 vs 多數平庸**——資本/成交/報酬集中在少數(股票/玩家/日子/月份)。
3. **支配地位有慣性**(馬太效應)——強者恆強是 Pareto 世界的動態形式;領先者的 rank 有持續性。
4. **集中度本身會變**——集中⇄分散的「變化方向」是資訊(籌碼收斂=有人在收貨;市場寬度收窄=行情由少數股撐)。

> **方法論轉譯**:思想 → **無切點的分布泛函**(continuous functionals)。不問「前 20% 是誰」
> (要切點,禁),改測「**分布有多不均、往哪變**」(連續值,合法)。

## 一、#9 合規工具箱(全部 cutoff-free、純數學轉換 #1)

| 泛函 | 測什麼 | 公式本質 |
|---|---|---|
| **Gini 係數** | 不均度(0=全均、1=極端集中) | Lorenz 曲線面積,連續 |
| **HHI**(Σ share²) | 集中度(玩家/日子/級距的支配度) | 平方和,無切點 |
| **Shannon entropy** | 分散度(集中的反面) | −Σp·log p |
| **max-share**(max/Σ) | 最大單一貢獻者佔比 | max 是連續泛函、非「前 N」 |
| **CV / skew / kurtosis** | 波動相對量 / 偏斜 / 重尾 | 動差,連續 |
| **rank / Δrank / rank 自相關** | 支配地位與其慣性(馬太) | 排序泛函,無閾值 |
| **breadth**(高於自身 rolling mean 之股比例) | 參與度(寬 vs 窄市) | 參照=各自資料,非硬編 |

視窗一律 5/20/60/120/252(calendar 慣例);**嚴禁**:top-20% flag、四分位切點、「大戶=N 張以上」等任何固定分界。

## 二、六軸:Pareto 思想 × 實證欄位 → 特徵族

### 軸 P1 持股集中(誰擁有——所有權不均)
| 表.欄(catalog 實證) | 特徵族 |
|---|---|
| `TaiwanStockHoldingSharesPer.HoldingSharesLevel/people/percent` | **Pareto 本命表**(持股級距分布):級距 percent 之 **Gini/HHI/entropy**;**Δ集中度**(5/20/60d)=籌碼收斂/發散方向;人數分布 vs 持股分布的不均差(少數人持多數股的程度) |
| `TaiwanStockShareholding.ForeignInvestmentSharesRatio` | 外資(結構性少數關鍵者)持股 share 與其變化、距上限空間 |
| `TaiwanStockMarketValue.market_value` | 個股市值佔全市場/產業 share(支配地位本身) |

### 軸 P2 資金流集中(誰在買賣——流量支配)
| 表.欄 | 特徵族 |
|---|---|
| `InstitutionalInvestorsBuySell.name/buy/sell` | 各法人別 |淨買| 之 **HHI/max-share**(流向由單一玩家主導?)、主導者更替頻率(支配輪動) |
| `GovernmentBankBuySell.bank_name/buy/sell` | 官股內部集中度(單行庫獨買 vs 多行庫齊買,訊號強度不同) |
| `TaiwanDailyShortSaleBalances.SBL*/Margin*` | 空方力量集中:借券餘額/額度使用率、借券 vs 融券結構比(誰是主要空方) |
| `SecuritiesLending.transaction_type/volume/fee_rate` | 借券費率(空方擁擠度的價格訊號)× 量集中 |

### 軸 P3 量能時間集中(何時成交——時間軸上的 Pareto)
| 表.欄 | 特徵族 |
|---|---|
| `TaiwanStockPrice.Trading_Volume/Trading_money` | rolling 窗內**日量分布之 Gini/HHI/entropy**:量集中少數日(事件驅動/主力進出)vs 均勻吸納;**max-share**=最大單日量佔窗內總量 |
| `TaiwanStockBlockTrade.volume/trading_money/price` | 鉅額(交易中的少數關鍵):block 金額佔總成交 share、block 折溢價(大資金的價格讓步) |
| `TaiwanStockDayTrading.Volume/BuyAmount/SellAmount` | 當沖 share(投機性少數)及其變化 |

### 軸 P4 報酬集中(報酬怎麼來——少數日子造就全年)
| 表.欄 | 特徵族 |
|---|---|
| `TaiwanStockPriceAdj.close`(還原價報酬) | 窗內 |日報酬| 之 **Gini/max-share**(動能由少數跳躍 vs 平穩漂移構成——跳躍型動能與漂移型動能後續行為不同之假說);**skew/kurtosis**(重尾不對稱);上行貢獻 vs 下行貢獻之不均差 |
| `PriceAdj.max/min/close` | 振幅貢獻集中度(大振幅日佔比,連續) |

### 軸 P5 生意支配地位(營收集中與馬太效應)— P-lag(發布日 gate)
| 表.欄 | 特徵族 |
|---|---|
| `MonthRevenue.revenue` × `IndustryChain.industry` | **個股營收佔產業合計 share**(市場支配度)及其**動能**(share Δ=強者愈強/弱者讓位);產業本身的 **HHI**(集中產業之領先者 vs 分散產業之領先者,語境不同) |
| `MonthRevenue.revenue`(自身時序) | 月營收分布之 CV/entropy(穩定生意 vs 暴衝生意)、季節集中度(entropy across 月份) |
| `FinancialStatements/BalanceSheet` 科目 | 獲利佔產業合計 share;資產報酬之橫斷面 rank 持續性(品質的馬太) |

### 軸 P6 市場結構 regime(context,X 類)+ 支配慣性動態
| 來源 | 特徵族 |
|---|---|
| 全市場 `market_value`/`Trading_money` 橫斷面 | **市場集中度 regime**(橫斷面 Gini/HHI):窄市(少數股撐盤)vs 寬市——context_values,與個股「領先者/落後者」身分交互 |
| 全 roster `PriceAdj` | **breadth**(高於自身 rolling mean 之股比例)=參與不均度 |
| `TotalInstitutionalInvestors/TotalMarginPurchaseShortSale` | 全市場資金流的玩家結構比 |
| rank 動態(任何個股特徵之橫斷面 rank) | **rank 自相關/rank 動能**(馬太效應的直接量化:支配地位的慣性與其衰變速度) |

## 三、與第一性計畫的關係(互補、不重複)

- **第一性計畫**(`augur_feature_design_first_principles_20260612.md`)回答「**有哪些資訊軸**」(七軸:水位/動能/缺口…)。
- **本計畫**回答「**分布形狀本身是不是資訊**」——同一批欄位,換 **集中度/不均度/支配慣性** 的鏡頭。
- 工程上:Pareto 泛函(Gini/HHI/entropy/max-share/rank-persistence)作為 **transform 庫的一個家族**併入
  builder,吃的 raw 欄位與第一性計畫共用;落地順序仍依 F2 roadmap 分期。

## 四、紅線重申(#9)

- 禁:`0.8/0.2`、20/60/20、decile/quartile 切點、「大戶=N 張」、top-N% flag——**任何固定分界不入公式**。
- 允:Gini/HHI/entropy/CV/skew/kurt/max-share/rank(連續泛函)+ calendar 視窗慣例。
- 模型(樹)自己學分界——**我們供「不均度的連續量」,不替市場預設 80/20 在哪**(這才是思想不被數字綁架)。

## 五、待實證

- [ ] `HoldingSharesPer` 級距結構(幾級、級距定義)與申報頻率 → Gini/HHI 計算粒度
- [ ] `IndustryChain` 對核心股之覆蓋完整度 → 產業 share 特徵可行性
- [ ] 市場結構 regime 之計算宇宙(全 roster vs 核心股——傾向全 roster,市場結構本來就含全體)
- [ ] 法人 `name` 值域(玩家結構比的分母)
- [ ] BlockTrade `trade_type` 值域語意

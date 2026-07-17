# alpha Phase 1 尾段判決(1-6~1-9)

> **交付性質**:alpha 計畫(`reports/taiwan_alpha_improvement_plan_20260717.md`,hugo 已拍板)Phase 1 尾段 1-6~1-9 之合成判決報告,呈 hugo。
> **判決日**:2026-07-17。**資料地基**:G1-PIN ≤ 2026-06-30(不滾動追)。
> **誠實框架**:本報告不美化。預診放棄與漏斗死亡**全數留痕**(N 語境明列);過關與否一律以實跑數字(#9)為據、以 HAC Eff-t 為顯著性準(#11,禁裸 iid);未達經濟終關(#14)之候選一律**不付 N、不入 trial_ledger**(留痕不入 ledger,rule⑥)。
> **本輪淨結果**:D2+D3 共 **7 支候選全滅**——3 支預診放棄、4 支入漏斗全死(3 死於 IC、1 死於增量);**無一支抵達經濟終關**。**N 維持 33、headline 維持 ridge_H60_LO 1.1302 不動**。

---

## 判決速覽表

| 任務 | 候選 | name/事件維度 | 判決 | 死點 | 決定性數字 | N 影響 |
|---|---|---|---|---|---|---|
| 1-6 D2 | `x_trust_qend_accel` | 投信季底作帳加速度 | **死於 IC** | 漏斗②IC | HAC Eff-t=−1.86(<2)、median IC=−0.0047 near-zero | 不付 N |
| 1-6 D2 | `x_foreign_streak_60d` | 外資連續買賣天數 | **死於 IC** | 漏斗②IC | HAC Eff-t=−1.782(<2)、iid=−2.216(被禁口徑)=G8 教科書案 | 不付 N |
| 1-6 D2 | `x_dealer_hedge_int_60d` | 自營避險 gross 強度 | **預診放棄** | 漏斗(0) | max\|median ρ\|=0.654 vs `dollar_volume_log_20d`>0.6 | 不付 N |
| 1-7 D3 | `x_limitup_rate_252d` | 漲停命中頻率 | **預診放棄** | 漏斗(0) | max\|median ρ\|=0.676 vs `volatility_60d`>0.6 | 不付 N |
| 1-7 D3 | `x_limitup_maxstreak_252d` | 連板持續 | **預診放棄** | 漏斗(0) | max\|median ρ\|=0.614 vs `volatility_60d`>0.6;+0.95 冗於 up_rate | 不付 N |
| 1-7 D3 | `x_limitdown_rate_252d` | 跌停強制賣壓事件 | **死於 IC** | 漏斗②IC | HAC Eff-t=−1.773(<2)、median IC=−0.0506 | 不付 N |
| 1-7 D3 | `x_limitup_reversal_5d_252d` | 漲停後 5 日條件式反應 | **死於增量** | 漏斗④增量 | 過①②③;Δ ridge mean_IC=−0.0485(三 seed 恆負) | 不付 N |

漏斗四道口徑:①建值(隔離表 `feature_candidate_values`,生產表唯讀)→ ②as-of 單因子 rank IC vs H60 label + **HAC Eff-t**(`metrics.effective_t_hac`,lag=2,禁 iid;pass=\|Eff-t\|≥2 且方向穩)→ ③去相關 vs canonical-34(pass=max\|corr\|<0.6)→ ④34+候選 vs 34 之 ridge IC 增量(pass=Δ>0 且 seed 穩)→ **經濟終關(#14,IC 撐住≠可交易)**。**每道死即停,不續下一道。**

---

## 1-6 D2:法人 name 維度候選判決(死者入墓碑格式)

**維度**:`TaiwanStockInstitutionalInvestorsBuySell`(IIBS)法人買賣。**家族基率警語**:D2 同 name 維度**先前已 5 死**(見墓碑名錄:`dealer_net_r`/`gov_bank_net_buy_60d` 無條件水位、`foreign_trust_div` 單日背離、`inst_flow_hhi`/`max_share_20d` 集中度、`money_x_inst_net` 量×淨交互);本輪 2 支進漏斗者期望值本即低-中。**本輪結果:再 +2 死(IC 關),D2 name 維度累計 7 死、0 生。**

### 墓碑 D2-1｜`x_trust_qend_accel`(投信季底作帳之時點條件化加速度)

- **配方角度**:投信 W10 短窗淨比 − 自身 W60 季內基線,量「作帳窗異常加速度」而非水位/背離/集中——計畫書 C-M3 進場條款明點名之合格例(季節條件化 ≠ 已死水位)。
- **預診**:PASS。max\|median ρ\|=**0.173** vs `momentum_20d`(單 panel 峰值 0.228);次高 `volume_surge_5_60` +0.101、`institutional_net_buy_ratio_20d` +0.094——遠低於 0.6 gate,角度確實新。
- **建值(①,PASS)**:12,393 值 / 28 as-of panel(2014-12-31…2026-05-31),隔離寫 `feature_candidate_values`(生產表 `feature_values` 全程唯讀)。as-of 正確:W10/W60 以 2330 TSP 日曆定錨、全部 date≤panel(法人盤後 date≤t 安全);手算 2330@2026-05-31=0.017334 與入庫值吻合;source-pure(2024-09-30 因 V10/V60=0 掉 1 股;缺投信列=真零計 0)。分布 mean −0.003 / std 0.057 / range[−0.54,+0.43]。
- **死因(②IC)**:27 有效 panel(2026-05-31 無 H60 label 掉)。median rank IC=**−0.0047**(near-zero)、mean IC=−0.0181、**HAC Eff-t=−1.86**(法定 Bartlett lag=2)、iid Eff-t=−1.88。\|HAC-t\|=1.86<2.0 **不顯著**;方向不穩(僅 17/27=0.63 同負號,負均值由 2024-03 −0.16、2022-09 −0.148 少數 outlier 季拉動)。lag 4/5 才越 −2.0,非法定口徑、且 near-zero median + outlier 驅動非真兆 → **robust FAIL**。
- **後續道次**:去相關/增量未跑(每道死即停)。
- **N 語境**:未達經濟終關 → **不付 N**(留痕不入 ledger)。staging 已清(feature-scoped 刪 12,393 列;並存候選未動)。
- **教訓**:季節條件化加速度角度**在預診層是真新**(0.173),但真兆檢定崩於 near-zero median + 少數作帳季 outlier——「角度新」≠「有訊號」,IC 關才是真檢定。

### 墓碑 D2-2｜`x_foreign_streak_60d`(外資買賣之持續時間/duration)

- **配方角度**:外資連續同號買賣天數計數(magnitude-free),量 duration/persistence——無任何死者或生產特徵量測 duration,計畫書明點名「外資連續買賣天數 ≠ 已死集中度」。
- **預診**:PASS(誠實揭露最近鄰)。max\|median ρ\|=**0.298** vs `inst_cumflow_position_60d`(單 panel 峰值 0.555);次高 `institutional_net_buy_ratio_20d` +0.258、`return_1d` +0.233——median 全低於 0.6 gate,為最近鄰但未共線。
- **建值(①,PASS)**:12,028 值 / 28 panel,隔離寫入。手驗 2330@2026-05-31:anchor d0=2026-05-29 f0=+13.28M(sign+)、前一交易日 2026-05-28=−7.08M 反號斷鏈 → k=1 → value=+0.016667,與 stored 一致。覆蓋保留率 97.1%(近全覆蓋、無覆蓋假象 §2.3)。
- **死因(②IC)**:27 panel。median rank IC=**−0.02694**、mean=−0.02872、hit_rate 40.7%(方向偏負且尚穩:外資連買 streak → 後續相對報酬走弱之反轉訊號)。**HAC Eff-t=−1.782**(lag=2);lag 敏感度**全數不過**:lag1=−1.912、lag2=−1.782、lag3=−1.689、lag4=−1.642(最寬鬆 lag1 仍 −1.912)。**唯獨被禁的 iid-t=−2.216 越線**——此正是 **G8 教科書案例**:重疊 H60 窗 × 月頻 panel 致 IC 序列正自相關、iid 高估顯著,HAC 誠實去相關後即崩到門檻下。
- **後續道次**:停於②,未跑去相關/增量。
- **N 語境**:未達經濟終關 → **不付 N**。死候選 12,028 列已自 staging DELETE(乾淨);生產表零寫入。
- **教訓**:**iid 越線、HAC 崩線 = G8 的活體標本**。若當初裸用 iid(−2.216)會誤判此候選「顯著」而放行——rule③ 禁裸用 iid 在此支救下一次假通過。

### 墓碑 D2-3｜`x_dealer_hedge_int_60d`(自營避險 gross 活動強度)【預診放棄】

- **配方角度(進預診立論)**:name 子維度拆分(避險 vs 自營,死者 `dealer_net_r` 為全 Dealer 合計)+ gross 活動強度 ≠ 淨方向水位;權證發行商機械避險流強度 = 散戶權證投機熱度 proxy(sentiment 機制)。
- **預診放棄(0,FAIL)**:max\|median ρ\|=**0.654** vs `dollar_volume_log_20d`(單 panel 峰值 0.713)> 0.6 gate;次高 `turnover_mean_20d` +0.584、`market_cap_log` +0.544、`sbl_short_balance_log` +0.482 全高位。
- **放棄理據**:權證避險活動集中大型高流動股,候選本質 = **流動性/size 代理**,與 field_correlation §D「短券側偏 size」同型死法。依 §4.1(0) **放棄留痕、不入 trial_ledger**(付預診不付 N)。
- **未來重測條件**:若需「產業內 / size 中和後之避險強度」等真正交化新角度,**非本配方重掃**。
- **N 語境**:預診放棄 → **不付 N**。

---

## 1-7 D3:漲跌停事件維度候選判決(死者入墓碑格式)

**維度**:`TaiwanStockPrice` ⨝ `TaiwanStockPriceLimit`(漲跌停事件)。**制度斷點標準化(任務硬要求,已實證且落 formula)**:`TaiwanStockPriceLimit.limit_up/down` 全史以現行 10% 規則回填,2015-06-01 前(實際 7%)為**反事實值**(2330 於 2010/2013 表值仍顯 ~9.9%、市場中位 pre-break=9.91% 已證)。故偵測分軌——斷點後用表值(era-true 10%),斷點前改用當日報酬對 7% 帶判定(tol=0.005 吸收 tick 進位);28 panel 僅 2015-12-31 窗跨斷點,由逐日 era-true 偵測 + 逐 panel rank 正確處理。**家族基率警語**:D3 家族先前五輪全淘汰、base-rate≈0-1/5。**本輪結果:2 死於預診、1 死於 IC、1 死於增量,0 生。**

### 核心發現(D3 整體)

**D3 最『直覺』的長窗漲停計數(up_rate)與連板 streak 皆死在預診**——命中頻率 \|median ρ\|≈0.62~0.69 vs `volatility_60d`,即**漲停/連板本質是波動家族的機械重編碼**(踩 `x_day_trade_ratio` 當沖前車同坑:0.79 共線入漏斗、HAC-t −2.09 過卻增量 −0.023 有害、fair-test 死)。存活入漏斗者 = 兩支『非頻率』角度:下跌強制賣壓(方向不對稱)與條件式事件後反應(最正交)。

### 墓碑 D3-1｜`x_limitup_rate_252d`(漲停命中頻率,252d)【預診放棄】

- **配方角度**:離散漲停事件之投機/樂透強度 ≠ 連續二階矩波動。
- **預診放棄(0,FAIL)**:max\|median ρ\|=**0.676** vs `volatility_60d`;次高 `range_mean_20d` 0.597、`margin_usage_ratio` 0.473;+ 內部與 maxstreak 冗餘 0.95。
- **放棄理據**:漲停命中頻率是波動/振幅家族的機械重編碼,非新資訊軸;踩當沖前車同型坑、超 0.6 門檻。**不入 ledger、留痕(A-x1)。**
- **N 語境**:預診放棄 → **不付 N**。

### 墓碑 D3-2｜`x_limitup_maxstreak_252d`(最長連板日數,252d)【預診放棄】

- **配方角度**:連板持續性(集中投機)≠ 總命中頻率。
- **預診放棄(0,FAIL)**:max\|median ρ\|=**0.614** vs `volatility_60d`;且與 `x_limitup_rate_252d` 內部 Spearman=**0.95**(近乎同一信號)。
- **放棄理據**:同屬波動重編碼、非獨立軸;超 0.6 且內部冗餘。**留痕不入 ledger。**
- **N 語境**:預診放棄 → **不付 N**。

### 墓碑 D3-3｜`x_limitdown_rate_252d`(跌停命中頻率 = 強制賣壓事件,252d)

- **配方角度**:無既有特徵計數『下跌鎖停之強制賣壓事件』;`volatility_60d` 對稱(不辨方向),與 up_rate 內部僅 0.51 ⇒ 下跌尾為獨立軸(Miller 1977 賣空約束 / 融資追繳強平串 / 處置過熱回落)。非 §D 六弱欄墓碑。
- **預診**:PASS。max\|median ρ\|=**0.476** vs `volatility_60d`(<0.6,遠低於殺死 day_trade 的 0.79)。註:29.7% nonzero(zero-inflated 但 100% 可算,0=無事件非缺列)。
- **建值(①,PASS)**:21,728 值 / 全 28 panel、369+ 股,隔離寫入。制度斷點對稱標準化實測正確——post-2015 直比 limit_down(2317 於 2020-01-30 COVID 崩盤 close=limit_down=83.1 命中)、pre-2015 用 reference_price 重建 7%(−6.6% drop 命中)。#8 as-of 嚴守:searchsorted side=right 保 date≤panel;有效日<60 缺列。
- **死因(②IC)**:27 panel(2026-05-31 之 H60 exit ~2026-08 超 max 價格日 2026-07-16、label 算不出而 drop,誠實非 bug)。median rank IC=**−0.0506**、mean=−0.0438、iid-t=−1.48、**HAC Eff-t=−1.773**、hit_rate 0.37。方向穩定且經濟合理(跌停頻率高 → 未來相對強度弱,median/mean 同負、63% panel IC<0),**但 \|HAC-t\|=1.77<2 顯著性不足** → FAIL、即停。
- **後續道次**:去相關/增量未跑。
- **N 語境**:未達經濟終關 → **不付 N**。script=`scripts/verify_pricelimit_candidates.py`;staging 值留存隔離表(不污染 canonical,`--clear` 可清)。
- **教訓**:方向不對稱角度**真新**(0.476)、經濟解釋自洽、方向亦穩——但強度不足以越 HAC 門檻。**「合理 + 穩定 + 不夠強」= 誠實記死**,不因故事好聽而放水。

### 墓碑 D3-4｜`x_limitup_reversal_5d_252d`(漲停後 5 日條件式前向反應,252d)【最深、死於增量】

- **配方角度**:條件式行為反應——給定漲停,個股後 5 日續漲或反轉之特有簽名(Cho et al. 2003 磁吸 + post-limit drift/過度反應)。所有墓碑皆『無條件』level/frequency/shape,無一涵蓋『條件於事件』之前向反應 ⇒ 符合計畫 D3『進場條款』真新角度。
- **預診**:PASS(**最正交候選**)。max\|median ρ\|=**0.273** vs `range_mean_20d`;次高 `volatility_60d` 0.257、`momentum_252d` 0.230;與 `x_limitdown_rate_252d` 內部僅 0.218(兩 enterer 近正交)。
- **建值(①,PASS)**:in-universe 6,502/12,394=**52.46%**(與 hint 吻合、確認配方正確;staging 寫 12,813 超集,IC/去相關/增量三關均限回逐 panel 名單、超集列不被使用)。fwd5=close[i+5]/close[i]−1,嚴守 i+5<j(事件後第 5 交易日 ≤ t,#8 anti-leak)。value mean=+0.00557 median=+0.00317。
- **②IC(PASS)**:27 panel。median IC=**−0.031287**、mean=−0.035728、**HAC Eff-t=−2.2166**(≥2 且方向穩)、iid-t=−2.170、hit_rate 0.370。**唯一過 IC 門檻者**。經濟解讀:近一年漲停後 5 日續強之股,未來 H60 相對強弱反偏弱(顯著負向、方向一致)。
- **③去相關(PASS)**:pooled 最高 \|corr\|=**0.237** vs `volatility_60d`;次高 `range_mean_20d` +0.224、`dollar_volume_log_20d` +0.223、`momentum_252d` +0.212。<0.6,新角度不與 34 共線。
- **死因(④增量,FAIL)**:seeds 41/42/43。三 seed 之 B2_ridge mean_IC 皆:**34=+0.15107 → 34+候選=+0.10254,Δ=−0.04853**(Ridge 確定性擬合、seed 只影響 B0/M1,故增量三 seed 恆等,seeds_consistent=True 但**方向為負**)→ **死於增量**。
- **誠實 caveat(#15)**:此 −0.0485 增量**含稀疏宇宙限縮之混淆**——候選 pooled 52.5% 覆蓋,`_panel_matrix` 要求全特徵齊備,故加入候選使建模宇宙縮至「同時具候選值」之股(2025-12-31:337 core → 34 齊 332 → 35 齊 273,限縮至 82%;早期 panel 更低)。base 34 在全宇宙(0.151)、add 35 在限縮宇宙(0.103)**非乾淨 apples-to-apples**。**惟凍結判準即標準增量(base 全 vs add 限縮,同姊妹檔)** → 依凍結判準判決 = 死於增量。「是否值得再做稀疏公平測」屬決策層(見下 §拍板點 S1)、留痕供研判,**不自行放量**。
- **N 語境**:未達經濟終關 → **不付 N**(N 維持 33)。staging 12,813 列已清。script=scratchpad `verify_limitup_reversal.py`。
- **教訓**:**唯一走完三道的候選**,證明「條件式事件反應」角度在 IC/去相關層真的獨立且顯著;死於增量的直接原因是**稀疏宇宙的建模限縮**而非角度本身無用——這是本輪唯一「有再議空間」的死者(公平測屬決策層)。

---

## 過三道者之經濟終關(#14)方案:誠實記全滅

**結論:本輪無任何候選抵達經濟終關(#14)。**

- 四道漏斗死點分布:預診放棄 ×3、死於②IC ×3、死於④增量 ×1。**經濟終關(run_economic_eval / portfolio.py)未被觸發任何一次**——因無候選通過④增量。
- 依鐵律⑥:預診放棄與漏斗死亡皆**留痕不入 trial_ledger、不付 N**。**N 維持 33、headline `ridge_H60_LO` 1.1302(canonical34/since2014/cost0.585%/T=25)不動。**
- **最接近者** = `x_limitup_reversal_5d_252d`(過①②③、死於④)。其死因帶稀疏宇宙混淆之 caveat,**是否重做「稀疏同宇宙 impute 公平測」(§2.3 verify_incremental_fair)屬決策層**,列拍板點 S1;在 hugo 未拍板前**不自行放量、不改判**——凍結判準下該候選判死成立。
- **下一步(若 hugo 未開 S1)**:D2/D3 兩維度本輪收官、全滅入墓碑名錄;Phase 1 特徵探索軸不因此輪全滅而動搖判準——base-rate 本即低,全滅屬預期範圍內的誠實結果,非流程失效。

---

## 1-8 D1 前置盤點(純盤點;API 放量待 hugo 呈量授權)

> 全部數字出自 live DB query + live code Read(#9);DB 現況 as-of 2026-07-17(BS 最新期 2026-03-31)。**本節零 API 重抓、零 code 變動**——供 hugo 對 D1 缺季工程 API 放量授權(#6/#24/#25)。

### (a) BalanceSheet 缺季盤點 + 對計畫的淨修正

三張基本面表季度網格覆蓋(2013Q1–2026Q1 期望 54 季):

| 表 | present 季數 | 範圍 | 系統性缺季 |
|---|---|---|---|
| **TaiwanStockBalanceSheet** | 39 | 2012-12-31..2026-03-31 | **15 缺** |
| TaiwanStockCashFlowsStatement | 57 | 2012-03-31..2026-03-31 | **0** |
| TaiwanStockFinancialStatements | 138 | 1991-12-31..2026-03-31 | **0** |

→ **僅 BS 需重抓**;CF/FS 網格完整,D1 缺季工程範圍**收斂為 BS 單表**。

**系統性缺季 15 季**(影響全體股票):
`2013-03-31 · 2013-06-30 · 2016-12-31 · 2017-09-30 · 2017-12-31 · 2018-03-31 · 2018-06-30 · 2018-09-30 · 2019-03-31 · 2019-06-30 · 2022-12-31 · 2023-09-30 · 2023-12-31 · 2024-03-31 · 2024-06-30`

**對計畫 §3.1 的修正**:計畫「2016-19、2022缺Q4/2023僅Q1Q2/2024僅Q3Q4」大致正確,但**漏了 2013Q1/Q2**;「2016-19」精確為 2016Q4 + 2017Q3–2019Q2 連續段(**2018Q4 存在、打斷該段**)。

**per-stock 殘留洞(不進重抓範圍)**:present 網格內 830 股有洞、合計 5,448 個 (股,季) 洞,但 **96% 是 Q1/Q3**(Q1=2570/Q3=2694/Q2=180/Q4=4),且 **302/2419 股歷史從未出現 Q1/Q3 = 半年報申報者**(FinMind 源頭本無資料 = 真零、重抓不生資料)。**值得重抓 = 15 系統性缺季;殘留 Q1/Q3 洞列 `_table_covers`/真零處理、不放量。**

**補抓 call 量估(per-stock 整檔重抓,待 hugo 授權)**:
- fetch_mode 實查 = **`per-stock`**(`data_id_required=True`,endpoint `/data`)→ **不支援 by-date 整市場抓**,必須逐股;1 call/股回該股全區間所有季(基本面表無分頁)。
- **只補現有 2,419 股 → ~2,419 calls**;補全 roster 3,102 股 → **上限 ~3,102 calls**。最省 = 1 call/股跨全區間、upsert 冪等(勿逐缺季群集發 call,~5× 浪費)。
- **配額**:2,419–3,102 < FinMind 6000/hr rolling → **單一配額窗即可**(不需過夜)。純步調地板 ~37 分;sustained-throttle 實證會降至 ~0.2/s → 實際數小時(緊盯前段、re-ban 即停 #25)。
- **護欄(B-m4)**:API 放量逐次授權(#6/#24/#25);與 `audit_selfheal`/`daily_maintenance` 對帳窗**同 IP 互斥排程**;FinMind Sponsor 訂閱有效為外部依賴。
- 落點:計畫 §六附表新 script `scripts/resync_balance_sheet_gaps.py`(經 `ingestion/finmind.py` 同一 fetch/三層防護、落回原 raw 表)。

### (b) CashFlows 累計態實查 + 去累計規則草案 + 對帳斷言

**自動判別器(within-year + cross-year reset 雙比)跑遍 34 type / ~28,600 股-年**,證偽計畫「20累計/4水位/6混合」:

| 類別 | 數 | 判準 | 例 |
|---|---|---|---|
| **CUMULATIVE(YTD 累計)** | **32** | within<0.7 且 cross≈within(每年 reset) | 營/投/籌活動 CF、CashBalancesIncrease、各損益項… |
| 非累計:期末水位(LEVEL) | 1 | within≈0.98,cross≈1.0(跨年連續) | CashBalancesEndOfPeriod |
| 非累計:年初定錨(ANCHOR) | 1 | within=1.00,cross≈1.0 | CashBalancesBeginningOfPeriod |

計畫所謂「混合」4 個(CashBalancesIncrease/ReceivableIncrease/AccountsPayable/AmountDueToRelatedParties)經 **cross-year reset 測試確認仍是純累計 YTD**(cross≈within,若真水位 cross 應≈1.0);比值偏高只是「淨額項變號」的噪音,非水位。恆等式驗證 TSMC 2022Q4:`EndOfPeriod = Beginning(年) + Increase(Q)` = 10649.90+2778.24=13428.14 ✓。

**去累計規則草案**(builder 內函式 `decumulate_ytd()`,#3 不建中間表):
- type ∈ {EndOfPeriod, BeginningOfPeriod}:原值直通(非累計)。
- 其餘 32 累計 type:`single_Q1=YTD_Q1`、`single_Qk=YTD_Qk − YTD_Q(k−1)`(k=2,3,4,須同 fiscal_year 前一季)。
- **邊界(實測)**:`CashFlowsFromOperatingActivities` q>1 中 **4,524/76,777=5.9% 缺同年前一季**(半年報 Q2 缺 Q1、缺季段缺前季)→ 去累計 **emit NULL**(不得用鄰年/跨年硬相減污染單季流量)。此為 (a) 半年報發現與 (b) 去累計設計之接點。

**對帳斷言(#15;附本次 live 通過率)**:① 跨年現金連續 `EndOfPeriod(Q4,Y)==Beginning(Q1,Y+1)` → live **24,268/24,507=99.0%** 在 1% 內(最強判別鎖,<95% 警示 type 分類漂移)｜② 恆等式(TSMC 逐季 ✓)｜③ 去累計還原 `Σ single_Q1..Q4==YTD_Q4`(回歸鎖)｜④ 淨額類允許變號(斷言只查 reset、不查單調,避誤殺)｜⑤ NULL 傳播:缺前季單季必 NULL 不得 0(0=假單季流量污染 D1 accruals/FCF)。

### (c) release_lag.py 金融股 60 日分支設計(D1 觸金融股基本面之硬前置)

**現碼**(`src/augur/features/release_lag.py`):`FIN_LAG_QUARTER=45`/`FIN_LAG_ANNUAL=90`,`financial_release_date` **無產業別分支** → 金融股 Q1/Q3 被低估滯後(法定 60 日,證交法 §36 但書)= #8 洩漏。現況休眠因唯一消費者 `gross_margin_pctile` 已排除金融股;**D1 `fundamental_composite.py` 為首個觸金融股基本面之消費者 → 此分支須先上線**(BS/CF/FS 三表共用同一 gate,一次到位三表齊惠)。

**分支設計**(純函式零 DB,向後相容):新增 `FIN_LAG_QUARTER_FINANCIAL=60`,`financial_release_date(d, *, is_financial=False)`——`if d.month==12: 90` `elif is_financial and d.month in (3,9): 60` `else: 45`。`is_financial` 預設 False(既有呼叫不變);金融股集合由 `TaiwanStockInfo.industry_category ∈ {金融保險, 金融業}`(live:金融保險 70 股+金融業)於 builder 一次性建 `frozenset` 穿線傳入(#29(b) 資料住 DB、release_lag 本身不碰 DB)。自測案例:`3/31+60=5/30`、`9/30+60=11/29`、`6/30+45=8/14`(Q2 不變)、`12/31+90=3/31`(年報不變)、一般 Q1 仍 5/15(向後相容)、邊界 5/29 未公告/5/30 已。

**誠實旗標(需決策層確認,不臆造法律值 #9)**:本設計只實作**已文件化的 Q1/Q3=60**;**金融股 Q2 半年報、Q4 年報是否亦有延長法定期限尚未查證**——保留 Q2=45/Q4=90 並註明待法源(#8 精神下若日後查得更長只會往後調、更保守,不影響 Q1/Q3 正確性)。

### D1 前置三段淨修正摘要

1. **(a)** 缺季收斂為 **BS 單表 15 系統性缺季**(補 2013Q1/Q2);per-stock 5,448 洞中 96% 半年報真零不可補;重抓 **~2,419–3,102 calls、單配額窗**(待 hugo 呈量授權)。
2. **(b)** type 分類 **32 累計 + 2 非累計**(證偽 20/4/6);去累計含 5.9% 缺前季 NULL 邊界;跨年連續斷言 live 99.0% 通過。
3. **(c)** `financial_release_date` 加 `is_financial` 分支(Q1/Q3→60),純函式零 DB;金融股 Q2/Q4 延長期限待法源(#9)。

**相關檔(絕對路徑)**:`/home/hugo/project/augur/src/augur/features/release_lag.py`(part c 現碼)｜`/home/hugo/project/augur/src/augur/ingestion/finmind.py`(per-stock fetch/MIN_INTERVAL/quota gate)｜`/home/hugo/project/augur/reports/taiwan_alpha_improvement_plan_20260717.md`(§3.1/§六附表)。

---

## 1-9 live OOS 承接管線明文化(預註冊文本,待 hugo 拍板)

> 全部數字於 2026-07-17 對 live DB + repo 實查重核;**未建 timer、未改 code、未跑 cycle**——純文本預註冊,呈 hugo 拍板後才動工(#20 執行前確認)。本稿取代 `reports/alpha_phase1_tail_partial_20260717.md` 的 §1-9 部分草案。

### A. `scripts/run_revalidation_cycle.py` 現況 + 排程歸屬

**A.1 現況(四步編排,全本地零 usage 除上游 sync)**:① #8 gate(`test_release_lag_antileakage.py`,不過即中止 fail-closed)→ ② `revalidate.py --run --skip-existing`(B/C/D 全 cell 重跑 + deflation,寫 `revalidation_ledger`,同 as_of 有列則整輪跳過)→ ③ `revalidate_verdict.py`(兩軌三態,寫 `revalidation_verdict`)→ ④ 告警 print 橫幅。cycle 之 as_of = `min(max core_universe_asof, max feature_values.panel)`(`revalidate.py:80`)——**無新 panel 即 no-op**,可安全過度排程。

**A.2 承接斷鏈(live 實查,1-9 驗收「panel 續建節奏」之答案)**:**宇宙續建是缺口**——`feature_values` max panel=**2026-06-30**(G1-PIN 已建),但 `core_universe_asof` max=**2026-05-31**;as_of 被 `min()` 釘死在 05-31、`revalidation_ledger` max as_of 亦 05-31。**不補宇宙,live OOS 永遠進不了 ledger。** 每季承接鏈四段:① 季末後 attestation 綠(`audit_selfheal.sh`/`daily_maintenance.py`,既有)→ ② `build_core_universe.py --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial --asof`(補新季 as-of 宇宙)→ ③ `build_feature_panel.py --panels <季末日>`(冪等重建)→ ④ `run_revalidation_cycle.py`。**settle 滯後誠實條款**:H60 需 ~78 日曆日 forward settle → 2026-06-30 panel 首個 live 期約 **2026-09 下旬** 才入淨值序列;live T 增量固有 ~一季滯後,月頻排程 + 冪等自動吸收。

**A.3 panel 續建頻率口徑(拍板點 A2)**:`feature_values` 已含 05-31/06-30 兩個非純季 panel、STAGE C/D 吃範圍內全部 panel(續建頻率本身即建構口徑)。**建議預設 = 季頻續建**(與凍結配方同頻,下一個 2026-09-30);月頻併入 = P6(`tr3m`)預註冊事項,**未過 P6 前置不建月末 panel**(P0 §7 實證月中 tranche 會誤放金融股 60d 財報=#8 洩漏)。

**A.4 排程歸屬(拍板點 A1)**:**主案 = systemd `--user` timer**(oneshot + `Persistent=true`、**月頻**、建議每月 5 日 04:30 避開 03:30 embed-catchup 與 audit 對帳窗峰;本支零 API、B-m4 IP 互斥不適用)。**先例已驗**:`augur-embed-catchup.timer`(03:30 Persistent)、`augur-l2-deliberation.timer`(06:15 Persistent)、`augur-audit-watchdog.timer`。**替代 = user crontab**(arena 三條 flock 先例已驗,功能等價但**漏跑不補**,列次選)。**理由**:WSL2 常關機,`Persistent=true` 補漏跑;季頻工作漏一次=延誤三月。**告警承接誠實條款**:現行告警=print 一次性(假設「執行者當下看見」,無人值守下此假設破)→ 明文 service stdout 落 `~/revalidation_cycle.log`;裁決 SSOT=DB `revalidation_verdict`;**hugo 檢視點=每季 settle 窗後(約 1/4/7/10 月上旬)檢視 log+verdict**;非 `deploying` 狀態=人審,系統不自動下架(靈魂:建議/決策分層)。

### B. live 期 trial 記帳口徑預註冊(N/T 界線;引 P0 §6 錨)

**錨(P0 §6 實算,`reports/alpha_p0_diagnostics_20260718.md`)**:每筆 trial 抬確立門檻 **+0.0086** 年化 SR(即期 −0.7pp DSR,N=32→33);每個 live 期降門檻 **−0.0162**;**1 trial ≈ 0.53 live 期 ≈ 1.6 個月** live 等效紅利。**誠實框架**:現行 sr_pp<SR_0(N=32),do-nothing 之 DSR 隨 T **微降而非爬升**——live T 的價值 = 門檻下移 + 真 OOS 檢定力,**不是** DSR 自然過線(預註冊此句防「等 T」被當 DSR 操作手段)。

**規則 R1–R8(凍結;改動=新預註冊須 hugo)**:
- **R1(同 trial T 延伸=免 N)**:trial 身分=`trial_ledger` UNIQUE 八元組 `(model,horizon,top_frac,weight,feats_hash,cost,sample_since,recipe)`。同 key 對末端延長之窗重評=同 trial(ON CONFLICT UPDATE `metric_value`/`n_periods`,**N 不動**)——schema UNIQUE 不含 as_of 已機械強制。
- **R2(新 trial=N+1)**:八元組任一分量變動=新 trial,**live 不豁免**(live 給免費 T、永不給免費 N);新 `recipe` 詞須先入 §4.3(b) 凍結詞彙表。
- **R3(窗方向性)**:「T 延伸」僅指末端追加;改 `sample_since`/剔中段 panel/改 panel 頻率=建構變更 → 新 trial 或獨立預註冊(P6)。
- **R4(feats_hash 穩定 guard)**:live 續跑 `feats_hash` 必須=凍結 `canonical34_stageB_20260706`;若 live 覆蓋缺損致交集漂移 → **資料品質事故非 trial**:該輪中止不入 ledger、修 writer/重建(#12),禁以新 hash 列帳(建議落 cycle 內 assert fail-closed)。
- **R5(per-trial confirmatory clock)**:每筆 trial confirmatory live T 只計該 key 首次入 ledger(min run_at)之後才 settle 之期數(設計當下已可觀測之 live 期屬 in-sample,不得回收充 OOS);headline(07-06 凍結)自 G1-PIN(2026-06-30)起全數乾淨。封「看 live 再註冊貼合配方回頭宣稱 OOS」之洞。
- **R6(live 期診斷)**:本地唯讀診斷/預診不入 ledger(§4.3(a));因看 live 而放棄之候選入 reports 留痕(P0 §8 先例)。判準=**是否產出用於挑選的淨值成績**(confirmatory 必入帳、唯讀量測不入)。
- **R7(記帳算術)**:每季重算 **N=ledger 當下機械 DISTINCT(含 recipe)**、**T=headline 淨值序列全期數(含已 settle live 期)**;**N 與 T 去耦**(T 隨 R1 成長、N 只隨 R2)。任何 DSR 引用一律帶戳記「**DSR x% @ N=y, T=z, as_of=w**」(P0 §5 紀律)。
- **R8(負面清單,皆付 N)**:改 cost 常數、任何 H20 借道(`h20_dead_no_shortcut`)、live 試新 overlay 出成績不入帳(=敵③)。

**live 現況錨(佐證 R1/R2 已運作)**:`trial_ledger` 現 **33 列** = 32 `plain` + 1 `buf10/20`。該 `buf10/20`(=1-3 P1 buffer)已跑並**判死**(換手↓34%/28% ✓,但雙宇宙不同向:asof +0.023/pit −0.008)——**R2 的活案例**:新建構 overlay 即使 live 期不變也付 N(32→33),判死後仍留帳(付 DSR 代價、不回收)。

### C. 每季 DSR 隨 T 重算並入檔

**C.1 重算引擎=既存零新碼**:`revalidate.py` 之 `refresh_trial_ledger`(寫 net_sharpe)→ `deflation_rows`(讀 ledger 全 net_sharpe 算 N → `evaluation/deflation.py::deflated_floor`)→ 逐 cell 寫 `revalidation_ledger` 之 `dsr`+`deflated_sharpe_ann`(as_of 戳)。入檔 SSOT=`revalidation_ledger`。

**C.2 新發現(本次實查):DSR 陳舊是「N 驅動」不只「T 驅動」**——`trial_ledger` 現 N=**33**,但 `revalidation_ledger` 最新已發布 dsr 列(H60 LO since2014,as_of 2026-05-31)**內嵌 N=32**(值 0.4762、deflated_ann=−0.023)= **與當下 N=33 不一致、已陳舊**。成因:DSR 重算目前只綁 `revalidate.py --run`(觸發=新 panel/as_of=T 驅動),而 1-3 `buf10/20` 由候選漏斗直寫 `trial_ledger`(N 驅動)、**未觸發 DSR 重算** → 已發布 headline DSR 停在 N=32。

**C.2 預註冊補強(拍板點 C2;小改判準零改動)**:DSR 重算觸發須涵蓋**兩條路徑**——(i) T 驅動(既有 cycle 季頻 timer 已覆蓋);(ii) **N 驅動(候選漏斗新增任何 trial)**:§4.1 漏斗第(4)步 deflation 後**強制重跑 `deflate_headline_verdict.py`**(或 cycle 等效 DSR refresh),使已發布 KPI 反映當下 N(因 N 陳舊不等下一季、不能只靠季頻 timer 吸收)。落地二擇一:`verify_candidate_funnel.py` 收尾一律接 `deflate_headline_verdict.py`;或 cycle 起手先 refresh_trial_ledger + 重算 headline DSR 再判 as_of。

**C.3 headline KPI 戳記與住所**:KPI SSOT=`deflate_headline_verdict.py`(print + `revalidation_ledger` dsr 列)。建議(零 code 變動)排程 unit 內 cycle 後串跑、輸出 append 同一 log;次選 cycle 加第 5 步。每次發布帶 R7 戳記。

**C.4 殘留債(拍板點 C1;P0 §5「建議、未做」)**:`deflation_rows` 寫 dsr 列時 note 未持久化 `sr_pp`/`ppy`/`skew`/`kurt` → 歷史 DSR 無法免重跑復現。建議併 1-9 落地:note 補此四值 + T(判準零改動、純 provenance,改 `revalidate.py` 一處 + selftest)。可選人讀層:每季 digest 落 `reports/revalidation_digest_<YYYYQn>.md`(非 SSOT)。

**1-9 驗證清單(2026-07-17 實查)**:`trial_ledger`=33 列(plain 32+buf10/20 1;八元組 DISTINCT=33)｜`revalidation_ledger` max as_of=2026-05-31｜`feature_values` panel max=2026-06-30｜`core_universe_asof` max as_of=2026-05-31｜已發布 H60 LO since2014 dsr=0.4762 @ 內嵌 N=32/T=25/deflated_ann=−0.023(**陳舊,當下 N=33**)｜systemd 先例三支、crontab arena 三條 flock｜CLI 旗標 `build_core_universe.py`(--since/--liquidity-pct/--exempt-revenue-financial/--asof)、`build_feature_panel.py`(--panels)皆存在。

**1-9 關鍵路徑(絕對)**:`/home/hugo/project/augur/scripts/run_revalidation_cycle.py`｜`.../scripts/revalidate.py`(:80 as_of min、:284 refresh_trial_ledger、:292 deflation_rows)｜`.../scripts/revalidate_verdict.py`｜`.../scripts/deflate_headline_verdict.py`｜`.../scripts/build_core_universe.py`｜`.../scripts/build_feature_panel.py`｜`.../reports/alpha_p0_diagnostics_20260718.md`(§5/§6 N/T 錨)。

---

## 拍板點清單(須 hugo)

| # | 拍板點 | 建議 | 出處 |
|---|---|---|---|
| **S1** | `x_limitup_reversal_5d_252d` 是否重做「稀疏同宇宙 impute 公平測」(§2.3 verify_incremental_fair) | 唯一過三道者,死於增量帶稀疏宇宙混淆;凍結判準下已判死,重測屬決策層放量、不自行做 | 1-7 |
| **D1-放量** | BS 15 系統性缺季重抓 API 放量授權(~2,419–3,102 calls、單配額窗、per-stock upsert 冪等) | 逐次授權(#6/#24/#25),與對帳窗同 IP 互斥;殘留 Q1/Q3 半年報洞不放量(真零) | 1-8(a) |
| **D1-lag** | 金融股 Q2/Q4 財報延長期限法源查證(現只實作已文件化 Q1/Q3=60、保留 Q2=45/Q4=90 待查) | 不臆造法律值(#9);#8 精神下若查得更長只往後調 | 1-8(c) |
| **A1** | live OOS 排程歸屬 | systemd `--user` timer、月頻、`Persistent=true`(先例已驗);crontab 次選 | 1-9 A.4 |
| **A2** | live panel 續建頻率 | 季頻預設(下一個 2026-09-30);月頻繫 P6 前置未過不做 | 1-9 A.3 |
| **A3** | 告警承接檢視點 | 季 settle 窗後檢視 log + DB `revalidation_verdict`;不自動下架 | 1-9 A.4 |
| **B** | R1–R8 預註冊文本凍結 | 照案凍結;改動=新預註冊 | 1-9 B |
| **C1** | dsr note 持久化 sr_pp/ppy/skew/kurt+T | 小改 `revalidate.py` 一處 + selftest | 1-9 C.4 |
| **C2** | **DSR 重算觸發涵蓋 N 驅動(非只 T 驅動)** | **漏斗收尾強制重跑 headline DSR;修現行 N=32/33 陳舊斷鏈** | 1-9 C.2 |

---

## 未做/未測聲明

- 1-6/1-7:七支候選之預診、建值、IC、去相關、增量數字**全實跑**(#9);死候選 staging 值均已清或留隔離表(生產表 `feature_values` 全程唯讀、零寫入)。無候選抵達經濟終關 → **N 維持 33、trial_ledger 未動、headline 未動**。
- 1-8:**純盤點、零 API 重抓、零 code 變動**;BS 缺季/去累計/lag 分支為 D1 前置設計草案,API 放量與 code 實作待 hugo 拍板。
- 1-9:**未建 timer unit、未改任何 code、未跑 cycle**;§A 斷鏈、§B live 錨、§C 機制與 N 陳舊發現皆 live DB/repo 實查。全拍板點須 hugo 拍板後才動工(#20 執行前確認)。

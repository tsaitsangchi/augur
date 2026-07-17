# P0 診斷包報告(alpha 提升計畫 Phase 1-0)

- **依據**:`reports/taiwan_alpha_improvement_plan_20260717.md` §3.2 P0 交付清單(L279-283)、§五 1-0 驗收(L357)。八項交付全數完成,對映本報告 §1-§8。
- **紀律**:全部數字出自本地實跑(python script / live DB query;CLAUDE #9 零現編);全程唯讀、零 `trial_ledger` 寫入、零生產表變動、零 Claude-side 估算。
- **實跑日**:2026-07-17。
- **口徑錨(headline 配方複刻)**:`B2_ridge` / H60 / long-only / since2014 / top_frac=0.1 / equal weight / cost=0.00585 / asof=True;`core_universe_asof` 28 panels → `_nonoverlap(h=60)` → n=25 非重疊期(2016-12-31..2025-12-31)、ppy=2.7761;同 `scripts/revalidate_baseline.py` 凍結路徑。複刻迴圈與正典 `portfolio.run_backtest` 逐期比對:dates / net_series / avg_turnover **完全一致**(np.allclose atol=1e-12)。
- **工件(scratchpad,可重跑複現)**:`p0_diag_turnover_corr.py`(§1/§2)、`p0_exposure_attribution.py`(§4)、`dsr_dual_baseline_recon.py`(§5)、`p0_sr0_sensitivity_v2.py`+`p0_sr0_result_v2.json`(§6);另實跑 `scripts/deflate_headline_verdict.py` 與 `scripts/repair_priceadj_basis.py`(唯讀掃描)。scratchpad 目錄=`/tmp/claude-1000/-home-hugo-project-augur/778040ca-21b5-4b60-ad2d-0fad302930ca/scratchpad/`。

---

## 摘要(每項一句話結論+裁決建議)

| § | 交付 | 一句話結論 | 裁決建議 |
|---|---|---|---|
| 1 | 換手+成本歸因 | avg_turnover ≈65%/次再平衡=高換手(舊口徑 0.6468/新含漂移 0.6440),成本總邊際 ~1.05pp 報酬/年 ≈ 0.072 年化 SR;equal weight 下新舊口徑幾乎重合(+2.8% 相對)。 | P1 降換手空間存在、維持順序 1;P2 誠實化代價微小、照做且先於 P1 定案。 |
| 2 | 三 horizon 相關 | 全部相關 <0.9(最高 H60-H120=0.7671)。 | **P5 不觸放棄門檻**,保留可測(Phase 2-5)。 |
| 3 | panel 節奏 | 月頻歷史 panel 不存在(月距樣本僅 1 對);季頻期 60 個月底只有 20、缺 40。 | P6 **非**「既有資料直接可用」——須先補建 ≥40 個月底 panel(寫 feature_values=生產表,**須 hugo 授權**)。 |
| 4 | 曝險/歸因 | 市值傾斜確立(持股 MV 中位=宇宙 55%、Spearman(pred,MV)=−0.199、25/25 期同向)但樣本內超額 ~+5.5%/年幾乎全在截距,**非** SMB 溢酬(β×mean(SMB)≈−0.03%/年)。 | 曝險揭露非判停;風險場景=小型股急殺 regime,直接連動 P4(vol targeting)/P8(ADV 容量)。 |
| 5 | DSR 雙基線對帳 | 0.407 與 75.6% 同公式同口徑,差異 **100% 由 trial 池帳本時點解釋**(N=32 vs N=16);兩者皆可用現行工具復現。 | 採 **0.407 口徑**(全表混頻 N)為唯一 KPI SSOT;75.6% 降格歷史快照——**須 hugo(拍板點 3)**。 |
| 6 | SR_0 敏感度+do-nothing | sr_pp(0.7185/0.6795)< SR_0(N=32)=0.7712 → **do-nothing 的 DSR 逐季倒退而非累積**;確立門檻需年化 SR≈2.00,缺口 +0.80。 | 採納 N 預算錨:1 筆 trial ≈ 1.6 個月 live 等效紅利+0.7pp 即期 DSR;開採僅在期望 SR 增益 >0.0086/筆時為正 EV=單一配方預註冊紀律的量化依據。 |
| 7 | lag/stale gate 月頻複核 | 月底月頻 10/10 gate 全安全,但金融股 60d 缺口之安全繫於「差 1 日」刀鋒條件;**月中 tranche 會誤放(#8 洩漏)**。 | P6 若採非月底進場日,release_lag 金融股分支(前置(a))**升為硬前置**;「逐一證明排除金融股」替代路線不成立為機械保證。 |
| 8 | 預診留痕框架 | 兩層預診機制+留痕模板+首批名單(D2/D3/D4/P5/P6/P1)定稿;P0 時點尚無正式放棄案例(P5 未觸門檻)。 | 依框架執行;每筆放棄留痕不入 ledger、N 語境揭露。 |

> **⚠ 跨切重大發現(§0)**:headline 錨 1.1972 今日不可再現(同配方重跑=**1.1321**,Δ−0.065);指向 TaiwanStockPriceAdj live sync 史改寫(216 支 core 股/307 個拼接違規點)。**建議先裁「修復後重定錨 vs 凍結期快照口徑」再開 P1-P8,否則錨漂移污染全部增量歸因——須 hugo。**

---

## 0. 跨切重大發現:headline 錨漂移(#15;三路實算獨立撞到)

§1、§4、§5/§6 三路各自複刻同一凍結配方,同撞一事:

- **凍結錨**:net Sharpe **1.197185**(`revalidation_ledger` run_at=2026-07-09 / `trial_ledger` trial_id=1 / `revalidation_verdict` 2026-07-08 metric_snapshot.net_sharpe=1.197184709380887,as_of 2026-05-31)。
- **今日同配方重跑**:net Sharpe **1.132083**(Δ−0.065;sr_pp 0.7185→0.6795、skew −0.214、kurt 2.060)。
- **已排除(逐項實查)**:n=25 期不變;特徵集相符(feats_hash `canonical34_stageB_20260706`);`core_universe_asof` committed_at=2026-06-30 未動;feature_values 對 G2 hash baseline **verify PASS**(凍結段值不變);剔除 2026-05-31 未完窗 panel 重跑=1.1321 不變(該 panel 本就不產生有效期)。
- **指向源=label/價格側**:TaiwanStockPriceAdj 已被 live sync 改寫(synced 至 07-16);`scripts/repair_priceadj_basis.py` 唯讀掃描實跑=**當前 216 支 core 股/307 個 factor 拼接違規點**(FACTOR_TOL=0.995;除息季基準拼接損傷為結構性已知問題)。
- **誠實限制**:本機無 07-09 資料快照,無法在地把 −0.065 逐股逐期分解到具體改寫列。

**含義**:(a) 今日全部 P0 數字帶有此標籤噪音(跨近期除息日之窗);(b) §5(DSR 對帳)與任何以 1.1972 為錨之比較,以及 P1-P8 全部增量歸因,都以「錨是什麼」為前提。

**處置兩案(裁定=須 hugo,建議列為 Phase 1 第 0 順位)**:
- (A) 修復 PriceAdj 拼接後**重定錨**——走 1-5 全鏈刷新條款(revalidate+deflate→verdict 同步;verdict 變向=停下報);
- (B) **凍結期快照口徑**——P1-P8 比較一律以 07-09 前資料狀態複現(需快照/還原機制,本機現無)。

**附帶錨句修正(文字執行層,hugo 過目)**:計畫簡報所稱「canonical **29** 特徵」與 DB 實況不符——headline 實際用 2014+ 交集之 **34 特徵**(=trial_ledger feats_hash `canonical34_stageB_20260706`;較 29 多 5 支:inst_cumflow_position_60d/120d、institutional_net_buy_ratio_20d、price_to_10yr、top_holders_pct);「29」=2008+ 全 panel 交集。今日實跑:34 特徵=1.1321、29 特徵變體=1.1462。§4 曝險結論對兩特徵集穩健(詳 §4 附)。另「DSR 0.407(n=25)」之 n=25 係 T(報酬期數)非 trial 數,0.407 背後 trial N=32(詳 §5(a)),錨句易誤讀、建議一併修正。

---

## 1. 換手與成本歸因(交付 1;→P1 buffer-zone 增益條件化、P2 口徑裁決)

來源:`p0_diag_turnover_corr.py` 實跑(唯讀);配方=口徑錨,n=25 期。

### 1a. avg_turnover 三口徑並列

| 口徑 | 全期均 | 排除首期均 | 中位 | min/max(排首) |
|---|---|---|---|---|
| 舊(交集法,`portfolio._turnover` 現行) | **0.6468** | 0.6321 | 0.6145 | 0.5238 / 0.8000 |
| 新 0.5·Σ\|Δw\|(無漂移) | 0.6347 | 0.6404 | 0.6215 | 0.5333 / 0.8182 |
| 新 0.5·Σ\|Δw\|(含漂移;漂移=前期持有窗實際 60td 報酬) | **0.6440** | 0.6500 | 0.6269 | 0.5320 / 0.8225 |

### 1b. 成本歸因(cost=0.585% 來回)

| 口徑 | 每期拖累 | 年化拖累(×ppy 2.776) | gross→net Sharpe | ΔSR(年化) |
|---|---|---|---|---|
| 舊 | 0.3784pp | 1.0504pp/年 | 1.2040→1.1321 | **0.0719** |
| 新·無漂移 | 0.3713pp | 1.0308pp/年 | 1.2040→1.1331 | 0.0709 |
| 新·含漂移 | 0.3768pp | 1.0459pp/年 | 1.2040→1.1320 | **0.0720** |

### 裁決依據

- **P1**:avg_turnover ≈**65%/次再平衡=高換手**,非「季頻換手本低」情境 → buffer-zone 的降換手空間**存在**,計畫 §3.2 P1 之條件化增益不必縮減、維持順序 1。
- **P2**:等權配方下新舊口徑幾乎重合(排首期 0.6321 vs 0.6500,+2.8% 相對)——「交集法系統性低估」在 equal weight 下**不成立**(僅 pred 加權才顯著)→ P2 誠實化代價微小,照計畫做、先於 P1 定案。
- **C-x8 合併上限實測上界**:換手成本總邊際=**~1.05pp 報酬/年、~0.072 年化 SR**(per-period SR 拖累=0.0720/√2.7761≈0.043)——P1/P3/M3 三通道收益合計不得超過此數。

---

## 2. 三 horizon net series 相關矩陣(交付 2;→P5 裁決)

來源:`p0_diag_turnover_corr.py` 實跑;同配方換 h。H40=28 panels(n=25)、H120 `_nonoverlap` 後 17 panels(n=15,半年頻)。net Sharpe:H40=1.0957、H60=1.1321、H120=1.2630(今日資料,見 §0 錨漂移標註)。

| 對 | 樣本 | Pearson | Spearman |
|---|---|---|---|
| H40 × H60 | 對齊 n=25 | **0.7044** | 0.7477 |
| H40 × H60 | 三方共同再平衡日 n=15 | 0.5659 | 0.6286 |
| H60 × H120 | 三方共同 n=15 | **0.7671** | 0.8393 |
| H40 × H120 | 三方共同 n=15 | **0.4660** | 0.5607 |

**P5 裁決**:全部 <0.9 → **不觸放棄門檻(計畫 L274)**,多 horizon 混合保留可測(Phase 2-5,擇一配方預註冊、入 ledger 一次)。

誠實 caveat:同起點窗巢狀重疊(H120 含 H60 前 60td)使相關**機械性偏高**——真分散度只會更好,不影響「不放棄」方向;H120 側 n=15 屬 thin。

---

## 3. feature_values panel 節奏盤點(交付 3;→P6 資料面裁決)

來源:live DB 實查(`SELECT panel_date, COUNT(*), COUNT(DISTINCT feature), COUNT(DISTINCT stock_id) FROM feature_values GROUP BY 1`)。

**全序列 36 個 panel_date、三段節奏**:

| 段 | 範圍 | 節奏 | panel 數 | 間距實測 |
|---|---|---|---|---|
| 年頻 | 2007-12-31 → 2020-12-31 | 每年 12/31 | 14 | 365/366d(9+4 次) |
| 季頻 | 2021-03-31 → 2025-12-31 | 每季底 | 20 | 90/91/92d(4+6+10 次) |
| 斷層+月頻起點 | 2025-12-31 → 2026-05-31 → 2026-06-30 | — | 2 | **151d**(FREEZE 斷層,2026-03-31 季底缺)、**30d**(live 月頻首步) |

- 間距分布全集:{30d×1, 90d×4, 91d×6, 92d×10, 151d×1, 365d×9, 366d×4};全部 panel 皆月底日(含 2026-05-31)。
- 最新 panel=2026-06-30:91,385 列、35 特徵、2,846 股;特徵數演化 28(2007)→34(2012)→35(2021-09 起)。

**P6 資料面裁決依據**:
1. **月頻歷史 panel 不存在**——月頻間距樣本只有 1 對(2026-05-31→06-30)。月頻 tranche 回測所需:季頻期 2021-01..2025-12 共 60 個月底、已有 20、**缺 40**;2026-01..04 再缺 4(含缺的季底 2026-03-31);年頻期 2007-12..2020-12 缺 143(若也要月頻)。
2. **raw 面支撐重建**:TaiwanStockPriceAdj max=2026-07-16、FinancialStatements max=2026-03-31、MonthRevenue max=2026-07-01;panel builder(`src/augur/features/panel.py` build_panel)為 as-of 純後向確定性計算 → 補建缺月底 panel **資料面可行、屬確定性特徵計算非 trial**(不付 N 代價)。
3. **結論:P6 非「既有資料直接可用」**——須先補建 ≥40 個月底 panel(2021+ 季頻期)才有月頻回測樣本;僅用既有 20 季頻 panel 無法評估月頻 tranche。補建=寫 feature_values(生產表)→ **執行授權須 hugo**(P0 未動)。

---

## 4. 曝險/歸因分解(交付 4;B-x3 示警核實;→P4/P8 連動)

來源:`p0_exposure_attribution.py` 實跑(唯讀);配方=口徑錨,T=25 期。

### (a) 市值傾斜——確立、25/25 期全數同向

- **持股市值中位數/宇宙中位數**(逐期;MV=TaiwanStockMarketValue 當日或前 30 日內最近值):全期中位=**0.550**、平均=0.581、range 0.449–0.915——top-decile 持股市值中位僅約宇宙的 **55%**。
- **size 分位分布**:持股落宇宙市值最小兩檔(Q1+Q2,最小 40%)平均 **62.1%**;最大兩檔(Q4+Q5)僅 18.3%。
- **訊號層直接量**:Spearman(預測分數, 市值) 橫斷面逐期——mean=**−0.199**、median=−0.211、**25/25 期全為負**。傾斜住在訊號本身,非個別期偶然。
- **最新 live panel 2026-05-31**(prediction_values `RankRidge_H60_2026-05-31_seed42_3a4e66fae8cfa2fa`,33/339 in_portfolio):持股 MV 中位 9.9 十億 vs 宇宙 17.1 十億(ratio **0.58**);分位分布 [Q1..Q5]=[6,13,6,3,5],下兩檔 58%;最小持股 2.4–4.2 十億(6151/4106/3038/5410/2488),但同時含 2330(61,071 十億)/2303——非純小型股組合,是「中位下移+兩端都有」。
- **對照 field_correlation(20260627 報告)**:market_value 單變量 IC=−0.092、89%/85% 同號「小型股效應」;short_sale_balance −0.027「偏 size 效應」——計畫 B-x3 所引示警**屬實**。

### (b) 產業集中——中度,前三合計 ~40%

- 前三產業合計權重(等權持股、檔數比):全期平均=**41.7%**、median=40.5%、max=59.5%。
- 近 4 期反覆超配:生技醫療業(持股 9–14% vs 宇宙 4%,~3x)、電子零組件(19% vs 7%)、電機機械(11% vs 5%)、建材營造;電子工業/半導體大致貼宇宙權重。
- live 2026-05-31:電子工業 18%(宇宙 19%)|半導體 12%(10%)|**建材營造 12%(宇宙 4%,3x 超配)**;前三合計 42%。
- **誠實標註**:產業分類用 TaiwanStockInfo **snapshot(非 PIT)**、多類股取最新列——歷史期分類有前視漂移可能,僅作揭露不作判準(與計畫 D8 PIT 分類議題同源)。

### (c) size β vs alpha 粗分解——傾斜是曝險揭露,樣本內非報酬來源

SMB 序列實算(未用替代路):逐期同 common 宇宙內,市值 Q1(最小 20%)−Q5(最大 20%)等權前向 h=60td simple 報酬差。OLS(n=25 非重疊期,iid t、未做 HAC):

| y | β(SMB) | t(β) | α_pp | t(α) | α 年化≈ | R² |
|---|---|---|---|---|---|---|
| net(long-only) | −0.083 | −0.27 | +0.0584 | +3.33 | +16.2% | 0.003 |
| gross | −0.083 | −0.27 | +0.0622 | +3.54 | +17.3% | 0.003 |
| **net−bench(市場中和)** | **+0.116** | +1.11 | **+0.0197** | +3.29 | **+5.5%** | 0.051 |

- 樣本內 SMB 均值≈**−0.0008/期(≈0)** → size premium 貢獻 β×mean(SMB)×ppy≈**−0.03%/年,可忽略**——超額 ~+5.5%/年幾乎全落在截距(alpha),**非**吃到 size 溢酬。
- **誠實界線**:n=25、β 標準誤大(~0.10),點估 +0.116 與「中度傾斜 β~0.3」統計上不可區分;基準=等權宇宙(本身已較市值加權偏小型),對市值加權指數而言 size 曝險會顯著更大;單因子分解、無產業/動能控制。
- **判讀**:(a) 的持股層傾斜為真且持續,但 (c) 顯示樣本內報酬非由 SMB spread 解釋——風險場景是「**小型股急殺 regime 下的曝險**」而非「報酬靠 size 溢酬灌」。P4(vol targeting)/P8(ADV 容量)與此曝險直接相關,非判停訊號。

### 附:對特徵集選擇之穩健性

34/29 兩特徵集分跑,(a)(b)(c) 結論不變:MV ratio 0.550/0.538、下兩檔 62.1%/62.4%、Spearman −0.199/−0.202、top3 41.7%/39.2%、net−bench β +0.116/+0.064。

---

## 5. DSR 雙基線對帳(交付 5;C-M2;→KPI SSOT 建議=拍板點 3)

來源:`scripts/deflate_headline_verdict.py` 實跑、`dsr_dual_baseline_recon.py` 實跑(唯讀)、live DB query(`trial_ledger` 32 列、`revalidation_ledger`)。

### (a) 0.407 從何而來

- **住所**:live DB `revalidation_ledger`(run_at=2026-07-09, as_of_date=2026-05-31, stage=C, horizon=60, model=ridge, config='LO|since2014', metric_name='dsr', value=0.4069);note 原文=「per-period DSR **N=32**(軌A 標註、<95%=薄edge常態非判停);deflated_ann=-0.090」。
- **寫入者**:`scripts/revalidate.py` 之 `deflation_rows()`(寫 net_sharpe→`refresh_trial_ledger`→讀 N→算 DSR),計算走 `src/augur/evaluation/deflation.py::deflated_floor` → `metrics.py::deflated_sharpe`(Bailey-LdP 2014 per-period 口徑)。
- **池組成 N=32**=當時(07-09 短 horizon 復驗後)trial_ledger 全表:{H20,H40,H60,H120}×{ridge LO, ridge LS, ridge LS+borrow2%, gbdt LO}×{since2014, since2021}。
- **輸入**:SR_obs(pp)=0.7185(年化 1.1972)、T=25、skew=−0.148、kurt=2.218、SR_0≈0.771(由 deflated_ann=−0.090 反推 0.7725,本次重算 0.7712)。
- **澄清**:short_horizon_verdict 表列「n=25」=T(報酬期數)**非** trial 數;0.407 背後 trial N=32。

### (b) 75.6% 從何而來

- **住所**:`reports/augur_prediction_deflation_verdict_20260708.md` §2,由 `scripts/deflate_headline_verdict.py` 親跑。
- **池組成 N=16**=當日(07-08)trial_ledger 全表——當時只有 H60/H120 兩家族(8 config×2 sample_since,今 trial_id 1-16);H20/H40 的 16 筆係 07-09 短 horizon 復驗才入帳。
- **輸入**:同一 frozen headline 序列(sr_pp=0.7185、T=25、skew=−0.148、kurt=2.218)、SR_0=0.560。

### (c) 對帳表——同口徑、不同帳本時點,非兩種方法

| 項 | 75.6%(07-08) | 0.407(07-09) | 差異 |
|---|---|---|---|
| trial 池 | N=16=H60+H120 全家族 | N=32=+H20/H40 全家族 | **差集=16 筆 H20/H40 trial**(trial_id 49-56, 65-72) |
| Var(SR_pp) | 0.0961(sd 0.310) | 0.1349(sd 0.367) | H20 LS 極端負值(−0.572/−0.656 年化)拉大分散 |
| SR_0(pp) | 0.560 | 0.771 | N↑+Var↑ 雙推 |
| SR_obs / T / skew / kurt | 0.7185 / 25 / −0.148 / 2.218 | 同左 | 無差 |
| 公式 | Bailey-LdP per-period | 同左(同 `metrics.deflated_sharpe`) | 無差 |

**差異分解(frozen 統計固定,本次實算)**:N=16+Var16→DSR 75.8%;只加 N 效應(N=32, Var16)→61.6%;只加 Var 效應(N=16, Var32)→59.9%;全效應→40.9%。**兩效應貢獻約各半。**

### (d) 現行工具重算(可復現性驗證)

Frozen 復現(以 verdict 記錄統計餵現行 `metrics.deflated_sharpe`;frozen net_series 未持久化=誠實限制):
- N=8 H60 家族:DSR=**0.8951**,與 verdict 89.51% 逐位吻合。
- N=16 池:SR_0=0.5581、DSR=**0.7577**、ann=0.267(vs 報告 0.560/0.7556/~0.26,差 0.002)。
- N=32 池:SR_0=0.7712、DSR=**0.4091**、ann=−0.088(vs ledger 0.4069/−0.090,差 0.002)。
- 殘差 0.002 來源已定位:trials_pp 轉換所需 H120/H20 之 **ppy 未持久化**,今日重跑因 live 增量多一片 panel(H120 T:14→15、ppy 1.647→1.666)微移;H60 ppy 不變(2.776)故 N=8 精確吻合。

**結論:兩數字皆可用現行工具復現、差異 100% 由池組成解釋、無公式分歧。**

今日 live 資料重算(headline 序列已漂,見 §0:sr_pp 0.6795、年化 1.1321、skew −0.214、kurt 2.060):N=16 池→DSR **70.1%**;N=32 池→DSR **34.5%**(=`deflate_headline_verdict.py` 今日實跑之保守值)。

### (e) 單一 KPI SSOT 建議(**須 hugo,拍板點 3**)

**採「N=trial_ledger 全表混頻池、per-period、`deflation.deflated_floor` 計算、落 `revalidation_ledger` dsr 列」為唯一 KPI 基線**——即 0.407 的口徑。理由:
1. 已是 code 內明文 SSOT(`deflate_headline_verdict.py` L133:「deflation 一律取較保守(較大)N 為準——禁用樂觀 N 灌水」),且 `revalidate.py` 與 `deflate_headline_verdict.py` 共用同一 helper(#12)——**不存在兩種方法之爭**。
2. N 由 DB 機械得出禁人手(SOP G7),方向單調保守(加 trial 只壓 DSR),抗敵③。
3. 75.6% 降格為「同口徑在 N=16 帳本時點之歷史快照」,今後**禁作現況引用**。

**配套紀律**:DSR 是帳本狀態相依量,任何引用一律帶戳記「DSR x% @ N=y, as_of=z」(現況=0.407 @ N=32, frozen as_of 2026-05-31;live 資料下已是 34.5% @ N=32)。**殘留債(建議、未做)**:revalidate 寫 dsr 列時未持久化 sr_pp/ppy/skew/kurt 輸入,致歷史 DSR 無法免重跑精確復現——建議入 note 或加欄。

---

## 6. SR_0 敏感度+do-nothing 基準(交付 6;C-M5/C-x1;→N 預算錨)

來源:`p0_sr0_sensitivity_v2.py` 實跑+`p0_sr0_result_v2.json`(全曲線數值)。口徑:`deflation.py`/`metrics.deflated_sharpe`(Bailey-LdP per-period)+trial 池=trial_ledger 32 列逐 horizon ppy 轉 per-period 並池(保守混頻 N)。實跑參數:T=25、ppy=2.7761、skew=−0.2139、kurt=2.0598、池 per-period sd=0.3673(var=0.134891)、SR_0(N=32)=0.7712(pp)。

**雙軌並列(承 §0 錨漂移)**:Track B=錨 1.1972(sr_pp=0.7185;skew/kurt/ppy 借今日序列——經 07-08 DSR=75.6% 反推分母 1.263 vs 今日 1.268 相符)/Track A=今日 1.1321(sr_pp=0.6795,全今日實算)。鑑識補充:剔除 2026-05-31 未完窗 panel 重跑=1.1321 不變 → 漂移非末 panel 所致(成因追查=§0)。**兩軌結論一致。**

### (a) 敏感度曲線:每加 1 筆 trial 壓多少 DSR(SR/T 固定、sr_var 固定於現池估計)

| N | SR_0(pp) | DSR(B錨) | Δ/筆 | DSR(A今) | Δ/筆 |
|---|---|---|---|---|---|
| 32(現況) | 0.7712 | **0.4101** | — | **0.3448** | — |
| 33 | 0.7758 | 0.4024 | −0.77pp | 0.3375 | −0.74pp |
| 35 | 0.7846 | 0.3879 | ~−0.71pp/筆 | 0.3237 | ~−0.68pp/筆 |
| 40 | 0.8041 | 0.3560 | ~−0.60pp/筆 | 0.2937 | ~−0.56pp/筆 |
| 45 | 0.8211 | 0.3291 | ~−0.51pp/筆 | 0.2689 | ~−0.46pp/筆 |
| 50 | 0.8360 | 0.3062 | ~−0.44pp/筆 | 0.2479 | ~−0.40pp/筆 |

- 每筆 trial 現價 ≈**−0.7pp DSR**(N=32→33),邊際遞減至 N=50 的 ≈−0.4pp;N=32→50 累計 −10.4pp(B)/−9.7pp(A)。
- 關鍵閾值:**0.95 早已不可及**(同 var 下 N=4(B)/N=3(A) 即跌破;現況 N=32 距 0.95 有 54-61pp);**0.5 已跌破**(B 於 N=23、A 於 N=18 跌破)。

### (b) do-nothing 基準:SR 不變、N=32 不變、純 live T 累積

**核心發現:T 紅利為負——幾季都不會自然過 0.95,永不。** 因 sr_pp(B=0.7185/A=0.6795)低於 SR_0(N=32)=0.7712,z=(sr_obs−SR_0)·√(T−1) 為負且隨 T 更負 → DSR 隨 live 累積**下降**:

| T | +期 | DSR(B錨) | DSR(A今) |
|---|---|---|---|
| 25 | 0 | 0.4101 | 0.3448 |
| 29 | +4 | 0.4030(−0.71pp) | 0.3331(−1.17pp) |
| 41 | +16(≈4年) | 0.3846 | 0.3031 |
| 65 | +40(≈10年) | 0.3553 | 0.2572 |

- T 紅利轉正之 break-even:N≤22(B)/N≤17(A) 才有正 T 紅利;即便如此——N=16 需 ≈260 年(B)、N=12 需 70 年、僅 N=8(H60 家族單獨計)約 20 年。**任何現實 N 下 do-nothing 都不確立。**
- 反解確立門檻(DSR≥0.95 所需年化 headline SR;skew/kurt 固定近似):N=32/T=25 需 **2.0012**;live +4 年(T=41)降至 1.8248;N=50/T=25 抬至 2.1229。vs 錨 1.1972 → **缺口 ≈+0.80 年化 SR,4 年 live 也只縮到 +0.63**。

### (c) 結論句:N 代價 vs T 紅利的量化錨

> **在現行 SR 水位,「等」不是選項、「省 N」只是次要——確立的唯一貨幣是 SR 本身。** 邊際交換率(N=32、T=25,以「確立門檻年化 SR」計價):每筆 trial 抬門檻 +0.0086、每期 live 降門檻 −0.0162 → **1 筆 trial ≈ 0.53 期 live ≈ 1.6 個月的 live 紅利**(live 季頻 ≈4 期/年)。但此交換率是二階項:一階事實是 headline(1.1972)距門檻(2.0012)缺 0.80 年化 SR,且因 sr_pp<SR_0(N=32),do-nothing 之 DSR 逐季倒退(−0.7~−1.2pp/4期)而非累積。**候選開採的機會成本錨=每筆 trial 用掉 1.6 個月 live 等效紅利+0.7pp 即期 DSR;開採僅在「期望 SR 增益 >0.0086/筆」時為正 EV——這正是把預算集中於少數高期望配方(單一配方預註冊紀律 §4.3)而非亂掃的量化依據。**

**誠實邊界**:(i) 敏感度假設新 trial 同分布(sr_var 固定)——若新 trial 系統性更弱,var 增大、SR_0 更高、代價更重;(ii) do-nothing 假設 live 期報酬同分布;(iii) Track B 之 skew/kurt/ppy 為今日近似(當時未持久化);(iv) 本 DSR 仍是樂觀上界(單 seed/成本平坦/survivorship 債);(v) 錨漂移成因未定位(§0)。

---

## 7. lag/stale gate 月頻行為複核(交付 7;A-M2;→P6 前置狀態)

前提區分:**月頻=月底 panel**(P6 主案)vs **月中 tranche 錯開**(P6 timing-luck 通道可能引入非月底日)——兩情境判定不同。全部 gate 逐一實核(引檔行號):

| # | Gate | 住所 | 月底月頻 | 月中 tranche |
|---|---|---|---|---|
| 1 | 月營收 REVENUE_DAY=15 | `src/augur/features/release_lag.py:33,40-43`;消費 `panel.py:151-152` | **安全**(實跑:5月營收 release=6/15≤6/30 可見) | 10-14 日 panel **誤擋**(法定 10 日已公開、gate 至 15 日才放=保守損時效、非洩漏);≥15 日安全 |
| 2 | 財報 FIN_LAG_QUARTER=45 | `release_lag.py:34,46-49` | 非金融股**安全**(法律事實);金融股見 #3 | 同左 |
| 3 | **金融股 Q1/Q3 60 日缺口**(未實作分支,`release_lag.py:16-22` 明文休眠債) | 無 code、僅 docstring | **不觸發但刀鋒邊緣**:實算誤放窗=[5/15,5/30)、[11/14,11/29),月底 5/31、11/30 恰在窗外**各僅 1 日之差**(2024/2025 皆驗證);live 實查=universe 內 4 檔金融保險股(2832/2850/2851/2852)之 GrossProfit 停於 2010-12-31→被 400d 守衛剔除、現代 panel 無 gross_margin_pctile | **誤放(#8 洩漏)**:落在誤放窗內之 panel 日(5/15-5/29、11/14-11/28)會把金融股未到法定期限的 Q1/Q3 財報判為已公告。且「逐一證明排除金融股」路線被 live 實查部分反駁:feature_values 有 4 檔金融業股(5878/6028/6035/6878)**現役攜帶 gross_margin_pctile**(2026-06-30 仍在)——今日不在 core_universe(344 股,實查 0/4 在內)故無生產路徑,但此為**經驗巧合非機械閘**,universe 更新即可能引入 |
| 4 | 年報 FIN_LAG_ANNUAL=90 | `release_lag.py:35,48` | **安全**(=現行 3/31 季底 panel 同語意);註:閏年 +90=3/30 比法定 3/31 早 1 日(實跑 2023-12-31+90=2024-03-30),月底 panel 只落 3/31 不觸 | tranche 落 3/30(閏年)**誤放 1 日**;另 Q2 金融股若法定為 2 個月(module 未文件化、須法規查證)則 8/14-8/28 tranche 同險 |
| 5 | 價格 recency MAX_STALE_CALENDAR_DAYS=45 | `panel.py:39,145` | **安全**(panel 相對;月距 30/31d<45 無新邊界) | 安全 |
| 6 | 毛利陳舊 MAX_STALE_DAYS=400 | `margin_cycle.py:30,59` | **安全**(即現在剔除 universe 保險股的機制,live 驗證) | 安全 |
| 7 | 籌碼表覆蓋 _MAX_STALENESS_DAYS=14 | `chip.py:49,63` | **安全**(live 月頻要求 sync 距 panel ≤14d,同現況) | 安全 |
| 8 | 集保 HOLDINGS_LAG_DAYS=7 | `release_lag.py:36,62-71`;消費 `chip.py:149` | **安全**(週快照、panel−7 cutoff 與節奏無關) | 安全 |
| 9 | walkforward purge _FEATURE_LAG_TD=62 | `src/augur/evaluation/walkforward.py:22` | **安全**(90 日曆≈62td 日曆界、與 panel 頻率無關;月頻下 purge 窗內被剔 panel 變多=機械正確之輕微資料損;若 60d 金融分支落地仍被 90>60 覆蓋) | 安全 |
| 10 | _REVENUE_SQL LIMIT 16 緩衝 | `panel.py:55-58,64` | **安全**(月底 panel 未公告月=0;最壞月中 1-2 筆被剔,16−2=14≥13 供 YoY) | 安全 |

非 lag gate、順帶確認與節奏無關:`chip.py:106-113` gov_bank「60d」實=LIMIT 60 事件日、`chip.py:98-104` lending LIMIT 100——皆無 panel 節奏耦合。

**裁決要點(供 P6 拍板)**:
1. **月底月頻對全部 10 個 gate 皆安全**——但金融股 60d 缺口之安全繫於「月底恰在誤放窗外 1 日」+「firm 守法定期限」兩個刀鋒條件,**非設計保證**。
2. **月中 tranche 錯開會顯現 60d 缺口(誤放=#8 洩漏)與 REVENUE_DAY 誤擋**——P6 若採非月底進場日,`release_lag.py` 金融股分支(計畫 L282 前置(a))**升為硬前置**;「逐一證明排除金融股」替代路線因 4 檔現役金融業攜帶者(僅靠 universe 成員資格隔離、非機械閘)而**不成立為機械保證**。
3. `release_lag.py:18`「現況無生產消費者」敘述在股票粒度不精確(4 檔金融業股在 feature_values 現役消費 financial_released),僅在「core_universe 內」粒度成立——文字宜修正(執行層消歧義,建議後續順手修)。

另:P6 前置(b)(混頻並池口徑 C-x7 之 selftest 級覆核)不在 P0 範圍、尚未執行——屬 P6 執行期硬前置,狀態=**未完成**。

---

## 8. 預診留痕框架+首批名單(交付 8;A-x1)

機制錨經 live 核驗:`src/augur/audit/feature_candidate.py:33` FEATURE_TABLE='feature_candidate_values'、`:126` clear_candidates、`:148` selftest 鎖生產表;`src/augur/evaluation/deflation.py:48` deflated_floor 收 n_trials(機械 N)、`:37` trials_per_period;trial_ledger 現況 32 列 2 模型(本次實查)。

### 8.1 哪些候選會經預診(兩層機制,計畫書皆有明文)

**(A) 通則層**(§4.1 步驟(0),L315-316;每個 x_ 候選無例外):入漏斗前本地零 usage 預診=覆蓋率/與 35 特徵相關矩陣/as-of 欄定錨;檢核項=§2.4 七條;放棄者連同依據入 reports 留痕。

**(B) 具名條款層**:

| 候選 | 預診條款(計畫原文錨) | 放棄觸發 |
|---|---|---|
| D2 法人細分 | 共線預診先行(L237)+「與死者的新角度差異」書面說明(L236) | 說不出與 ≥4 具 name 維度死者的差異;或與 4 個 inst 特徵共線 |
| D3 漲跌停 | 共線預診(vs momentum/range/volume_surge)+制度斷點標準化入配方(L243) | 共線;N 預算表明文「預診死不入、留痕」(L408) |
| D4 short-interest 三表 | 「三表逐一歸位判決(併入/backlog/判死)」(L248) | 非「約束狀態/事件」新角度=水位重掃(踩 §2.1 六弱欄墓碑)→不試 |
| P5 多 horizon 混合 | P0 交付 2=其預診;「>0.9 即放棄不浪費 N」(L274) | 相關 >0.9(本輪實測未觸,見 §2) |
| P6 tranche | P0 交付 3+7=裁決依據;硬前置(a)(b)(L282) | 前置不成立→順延/放棄 |
| P1 buffer-zone | 增益條件化於 P0 量得的 avg_turnover(L270) | 季頻換手本低→增益等比例縮→可降序(本輪實測=高換手,不觸,見 §1) |
| (橫切)全候選 | §6.9 do-nothing 基準(L414) | 邊際期望值輸給免費 live T 累積(量化錨=§6(c)) |

### 8.2 預診用什麼資料

凍結窗(≤2026-05-31)+已入庫 live 增量之在庫資料——raw 表覆蓋統計、feature_values 35 特徵面板(相關矩陣)、trial artifacts 之 net_series(P5)、回測重建之 avg_turnover(P1)。全部唯讀、本地零 usage、不寫 DB、不入 ledger。**A-x1 理由本體**:預診看的正是凍結資料——「預診亦是用凍結資料決定測什麼的分叉」(L280),即使不跑 trial,選什麼進漏斗已受凍結窗資訊影響=researcher-degrees-of-freedom 分叉。候選若已建值住 staging 表 `feature_candidate_values`,生產表全程唯讀;放棄清除一律 `fc.clear_candidates` 非手寫 DELETE。

### 8.3 預診放棄=N 語境的什麼(為何不入 ledger 但須留痕)

- deflation 的 N=trial_ledger 逐列記帳,語意=「實際走過漏斗、產生過可挑選統計量的試驗數」;預診放棄者**從未產生 trial 統計量**、無可挑選之 z,不該付 N 代價(硬灌反而懲罰廉價篩查、誘使跳過預診直接進漏斗=更糟)。
- 但不留痕=N 語境不可稽核:實際搜索寬度=入帳 trial+預診篩掉的分叉。留痕使 N 的解讀誠實:**ledger N=機械下界(付 DSR 代價),預診寬度=揭露性語境(不付代價但可稽核)**。
- **預診放棄 ≠ 墓碑**:墓碑=「測過且證偽」;預診放棄=「未測、期望值不划算」——三態分明,受 §2.3 冤殺翻案先例約束(稀疏候選未經同宇宙公平測不得蓋棺);日後憑新角度/新資料可再入場。

### 8.4 留痕格式(固定欄位,後續每輪照填)

每候選一條:**候選 ID+計畫 § 錨/預診日期+執行者+工具(script 或 query 原文,#10 可溯源)/所用資料(表名+窗+as-of 欄裁定)/量測值(逐項附 stdout 或 query 來源)/判準引用(觸發哪條)/判決三態(進漏斗・放棄・改造後再議)/N 記帳註記(「不入 ledger;重試須憑新角度或新資料,自預診重走」)/墓碑連動(明注「預診放棄≠證偽,不入墓碑名錄」)/staging 清理證據(fc.clear_candidates)**;另每輪一列總帳(預診數/進漏斗/放棄/改造再議/ledger 影響)。

### 8.5 首批將預診候選名單

1. **D2 ≤3 支**(例:投信季底作帳季節條件化、外資連續買賣天數):新角度差異書面說明+與 4 inst 特徵及 name 維度 4 死者共線矩陣+2012 拆分口徑 `_table_covers` gate+buy/sell 負值髒值檢。
2. **D3 ≤3 支**(長窗漲停/跌停計數、連板 streak、磁吸距離):與 momentum/range/volume_surge 共線+2015-06-01 斷點標準化方案+TaiwanStockPriceLimit 覆蓋(2000-01 起)。
3. **D4 三表歸位判決**(TaiwanDailyShortSaleBalances/TaiwanStockSecuritiesLending/TaiwanStockDayTradingBorrowingFeeRate):水位角度已被 §2.1 六弱欄墓碑封死,只有「約束狀態/事件」角度可進。
4. **P5**:即 §2——本輪實測 <0.9,不成為放棄案例、進 Phase 2-5。
5. **P6**:即 §3+§7——前置未全成立,判決=**順延留痕**(補建 panel+前置(a)(b) 完成後再議)。
6. **P1**:即 §1——高換手證實增益空間,判決=**進漏斗**(Phase 1-3 預註冊單點)。

**P0 時點總帳**:預診 3 項組合軸(P1/P5/P6)——進漏斗 1(P1)、保留可測 1(P5)、順延 1(P6)、正式放棄 0;ledger 影響 0 筆。D2/D3/D4 之實際預診量測值屬 Phase 1 執行期產出,本報告不預跑不現編。

---

## 九、裁決依據總表

| 軸 | P0 說了什麼(實測) | 建議 | 誰拍板 |
|---|---|---|---|
| **錨** | headline 1.1972 不可再現(今 1.1321);PriceAdj 216 支/307 拼接違規點 | **先裁「修復後重定錨(A) vs 凍結快照口徑(B)」,再開 P1-P8**;建議列 Phase 1 第 0 順位 | **須 hugo** |
| **P1** | avg_turnover≈65%/次=高換手,非季頻本低;成本邊際 ~1.05pp/年、~0.072 SR | 維持順序 1;照 1-3 預註冊單點(進 10%/出 20%);C-x8 三通道合併上限=0.072 SR 實測上界 | 依既定計畫 |
| **P2** | equal weight 下交集法低估不成立(+2.8% 相對);pred 加權才顯著 | 照做、先於 P1 定案;誠實化代價微小 | 依既定計畫 |
| **P5** | 相關 max 0.7671,全 <0.9 | **不放棄**,保留 Phase 2-5;巢狀重疊使相關機械偏高=真分散只更好 | 依既定計畫(門檻條款自動裁) |
| **P6** | 月頻 panel 缺 ≥40;月底 gate 10/10 安全但金融股 60d=刀鋒;月中 tranche 誤放(#8) | 順延:(i) 補建 panel(寫生產表,授權須 hugo)(ii) 若月中 tranche→前置(a) 金融股分支硬前置(iii) 前置(b) C-x7 覆核未做 | **補建授權須 hugo**;其餘依前置條款 |
| **KPI SSOT** | 0.407 vs 75.6%=同法同口徑、純帳本時點差;兩者皆復現 | 採 0.407 口徑(全表混頻 N)為唯一 KPI;引用帶「@ N, as_of」戳記 | **須 hugo(拍板點 3)** |
| **N 預算** | 1 trial≈1.6 個月 live 紅利+0.7pp DSR;do-nothing DSR 逐季倒退;確立缺口 +0.80 年化 SR | 採納為 §6.9 do-nothing 基準之量化錨;開採僅在期望 SR 增益 >0.0086/筆 | 依既定計畫 |
| **曝險** | size 傾斜真且持續、但非報酬來源;產業集中中度 | 非判停;P4/P8 直接對此曝險;產業 PIT 議題連動 D8 拍板 | 依既定計畫 |
| **錨句修正** | 「canonical 29」實=34;「DSR n=25」係 T 非 trial 數 | 計畫書/簡報錨句修正(文字執行層) | hugo 過目 |
| **release_lag.py:18** | 「無生產消費者」股票粒度不精確(4 檔現役攜帶者) | docstring 消歧義(執行層) | 執行層順手修 |

---

## 十、無法算出項(誠實列+缺什麼)

1. **1.1972→1.1321 漂移的在地逐股分解**:缺 07-09 資料快照——只能定位到 PriceAdj 史改寫(拼接違規點掃描),無法逐列歸因。若走 §0 方案 (B) 需先解此。
2. **4 檔金融業攜帶者(5878 台名/6028 公勝保經/6035 悠遊卡/6878 歐付寶)是否各自適用證交法 §36 但書 60 日**:屬法規事實查證(需 MOPS 實際公告日 probe),本診斷無來源、不裁。
3. **Q2 金融股法定期限是否為 2 個月**:module 未文件化,須法規查證(影響 §7 gate #4 之 8/14-8/28 tranche 風險判定)。
4. **frozen net_series 未持久化**:歷史 DSR(75.6%/0.407)無法免重跑逐位復現(僅能以 verdict 記錄統計餵公式,殘差 0.002 且來源已定位=H120/H20 ppy 未持久化)——殘留債建議:revalidate 寫 dsr 列時持久化 sr_pp/ppy/skew/kurt。
5. **Track B(錨 1.1972)之 skew/kurt/ppy**:當時未持久化,§6 以今日序列近似(反推分母 1.263 vs 1.268 相符,近似可用但非精確)。
6. **產業曝險之 PIT 版本**:TaiwanStockInfo 為 snapshot 非 PIT,歷史期產業集中數字有前視漂移可能——僅作揭露、不作判準。
7. **D2/D3/D4 首批候選的實際預診量測值**:屬 Phase 1 執行期產出(§8.5),本報告不預跑;D2 最終名單須先過「新角度差異」書面條款。
8. **P6 前置(b)(C-x7 混頻並池 selftest 級覆核)**:不在 P0 範圍,未執行——P6 執行期硬前置。

---

*P0 診斷包終。全程唯讀、零 ledger 寫入、零生產表變動;所有數字可由「工件」節所列 script 重跑複現(§0 錨漂移下,重跑值將隨 live 資料續動——引用請帶實跑日戳記)。*

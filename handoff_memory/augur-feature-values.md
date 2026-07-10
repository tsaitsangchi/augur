---
name: augur-feature-values
description: augur 特徵值全貌 — 產生器檔案地圖 + feature_values 35 落地特徵(含八二/康波鏡頭 8 存活+gross_margin_pctile) + headline + 已修/殘留盲點
metadata:
  node_type: memory
  type: reference
  originSessionId: b6b65aa3-b9fc-49cb-b589-2fff5a7b85de
---

augur 特徵值知識錨(2026-06-27 大更新)。產生器 `src/augur/features/`:`panel.py`(價量+月營收 YoY,組裝層,呼叫各模組)、`chip.py`(籌碼)、`valuation.py`(估值 5)、`concentration.py`(**八二法則量能集中**)、`phase.py`(**康波相位**)、`macro.py`(FRED 宣告、無 builder)。消費端:`universe/core_gate.py`、`evaluation/{label,baseline,metrics,walkforward}.py`、`audit/feature_diagnostics.py`(五鏡)。CLI:`scripts/build_feature_panel.py`(`--asof` 旗標限 as-of 宇宙省算)。

**`feature_values`**:PK `(panel_date, stock_id, feature)`、source-pure(算不出即缺列、#1)。panel 網格 35(2007-2020 年度 + 2021+ 季度 + 末 2026-05-31)。**現 35 特徵(2026-06-29 加 gross_margin_pctile)、2.42M 列、全 roster ~2068-3080 股**。

**🎯 gross_margin_pctile(2026-06-29 已 PRODUCTIONIZED=35 特徵第 35 個、`features/margin_cycle.py`)**:毛利率自身歷史百分位(康波 C3 margin 循環相位;發布日 gate financial_released、≥8 季、自身百分位)。落地 34 panel(2007-12-31 因財報史<8季 source-pure 缺、正確)、全 28 as-of panel、進 canonical(模型會用)、值域 0.012-1.0 均 0.559。歷史「基本面零增量」被冤殺(5 候選綑綁+覆蓋假象 bug)。公平測(同宇宙)4格全正增量;#14 經濟測 H120 Calmar 看似 +0.62。**但穩健測(`verify_stability.py`、#15)修正後分裂**:
- **Ridge H60=真穩健**:ΔSharpe +0.12/ΔCalmar +0.23、逐期 t=2.05 顯著、前後半都正、LOO 從不翻負 ✅
- **Ridge H120 的 +0.62 Calmar=部分樣本噪音**(子期翻號/LOO 翻負/Sharpe 持平);GBDT 不穩健(H120 Sharpe 負)。
**定論:是真的、但是「Ridge/H60 配置適度(+0.12 Sharpe)」改善,非戲劇性。** 三次穩健確認(用戶堅持)防止把 H120 +0.62 噪音當 alpha——示範 #15「IC/Calmar headline ≠ 穩健 alpha,須逐期 t-stat+子期+LOO+分位多角驗」。工具鏈 `reexam_sparse_candidates`/`verify_economic_reexam`/`verify_stability`。**已 productionize**(commit 95cdea0、34→35;scope 認知=Ridge/H60 適度改善)。

**價量已改還原價(2026-06-27 修 R1)**:`panel.py:_PRICE_SQL` 用 `TaiwanStockPriceAdj`(非原始 `TaiwanStockPrice`)+ `close>0` + recency gate(MAX_STALE 45 日)→ **一舉修除權息污染 + 停牌 close=0 污染 cycle + 下市 stale**(舊 memory 列的這三盲點已修)。

**35 特徵清單(34 基礎如下+第 35 個 gross_margin_pctile 見上)**:
- 價量(panel.py,還原價):`return_1d`、`momentum_5/20/60/120/252d`、`volatility_60d`(**volatility_20d 已五鏡剪枝**——與 range_mean_20d 共線+0.94)、`dollar_volume_log_20d`、`turnover_mean_20d`、`range_mean_20d`、`price_to_252d_high`、`cycle_position_252d`、`volume_surge_5_60`。
- 月營收:`monthly_revenue_yoy`。
- 籌碼 chip.py:`institutional_net_buy_ratio_20d`、`margin_usage_ratio`、`foreign_holding_pct`、`top_holders_pct`、`sbl_short_balance_log`、`lending_fee_rate_mean_30d`、`gov_bank_net_buy_60d`(**假零已修**:`_table_covers` gate,表未涵蓋即缺列;且被 canonical intersection 排除出模型)。
- 估值 valuation.py:`pe_ratio`、`pb_ratio`、`dividend_yield`、`market_cap_log`、`price_to_10yr`。
- **八二鏡頭 concentration.py(過完整漏斗存活)**:`volume_gini_20/60d`、`volume_max_share_20/60d`(量能時間集中 P3)。
- **康波鏡頭 phase.py(過完整漏斗存活)**:`range_position_120d`、`days_since_high_252d`(價格相位 C2)、`inst_cumflow_position_60/120d`(法人累計流相位 C4、30 panel)。

**鏡頭驗證結論(見 `reports/augur_lens_validation_20260627.md` + [[augur-three-lens-research]])**:八二+康波 12 軸生成 → 4 軸 8 特徵存活(過 as-of+HAC+多seed 提拔關卡、全 |HAC-t|≥2.8)。**headline H60 Ridge +0.1326→+0.1418(+7%)、GBDT +0.0997→+0.1130(+13%)**。淘汰:持股集中(冗餘 top_holders_pct +0.97)、報酬集中(弱)。最強=`inst_cumflow_position_120d`(HAC-t 4.35)。欄位三鏡頭地圖見表 `field_lens_map`(342 欄×量形位)+ `reports/augur_field_lens_map_20260627.md`。

**特徵集已飽和 + 經濟價值驗證(2026-06-27 戰役、總報告 `augur_three_lens_campaign_summary_20260627`)**:擴張探索**五輪全淘汰**:A 跨鏡交互(線性冗餘、x_gini_resid HAC-t −6.29 卻零增量)、B 八二 P6 馬太(動能冗餘)、當沖/鉅額/融資券 flow(day_trade_ratio HAC-t −2.09 但共線 range_mean +0.79、增量 −0.023 傷模型)、C 衛生(無改)、**phase-2 基本面(P5 營收/產業 share + C3 財報循環、發布日 gate)**——5 候選全淘汰:**真正交新資訊(全低共線 |r|<0.5)卻仍零增量**(x_gross_margin_pctile 單因子 HAC-t 2.08 過、單獨增量 3/4≤0)。**深度飽和定論:不只重組類、連全新基本面維度亦不增量 → 34 特徵已達此宇宙/H20-60 資訊前沿、勿再挖特徵**;前瞻在經濟/執行層(alpha 扛成本已證)、不同宇宙/horizon、regime-conditional。
**逃脫飽和方向(2026-06-28、換問題非加特徵、雙雙見效)**:(1) **長 horizon**——模型 IC 隨 H 單調升(Ridge H60 +0.141→H120 +0.152、GBDT +0.112→H252 +0.149);H120 經濟回測(非重疊半年)淨 Sharpe 1.27/**Calmar 3.55/MaxDD −5.3%**/CAGR +18.8%、低換手省成本(vs H60 Calmar 1.32);(2) **擴宇宙**——訓練 core→測擴大,模型 IC core +0.141→擴大 +0.120(2.4× 股 461→1117、Eff-t 5.66)、alpha 推廣。**戰略:前沿在 horizon×宇宙×執行配置、非加特徵**。工具 `run_horizon_universe_scan`/`run_economic_eval`(非重疊)。caveat:H120 17 期小樣本/窗異、確切回撤偏樂觀,結構優勢穩健。

**發布日 gate(keeper、`features/release_lag.py`)**:月營收次月15/財報季底+45/90日;修 monthly_revenue_yoy 洩漏(panel 3/31 原偷看 3 月營收)→ gated IC +0.0476/HAC-t 3.14 ≈ 洩漏版(特徵本就誠實)、headline 守住。C3 用財報 gate;capex 因 YTD 累計暫緩。三軸正交性實證(形×位 |corr| 0.022、形最互補,`augur_lens_correlation_analysis`)。**經濟價值(#14、`evaluation/portfolio.py`,2026-06-28 深化含交易成本)**:Ridge **long top10%/equal** 為最佳——扣台股 0.585% 來回成本後**淨 Sharpe 1.26 / Calmar 1.32 / CAGR +19.5% vs 基準 0.96/0.89/+15.4%**(2021-25、18期、換手68%)→ **alpha 扛得住成本**;top10%>20%>30%(集中度升淨報酬)、等權≈預測加權、long-short 無效、GBDT 淨僅微勝基準。**regime-conditional**(C1 `TaiwanBusinessIndicator` 領先去趨勢動能 `lead_nt_rising`、23 年 TAIEX 驗 MaxDD −54%→−15%/Sharpe 0.75→1.04):套投組砍 MaxDD −15%→−6%/Calmar→2.09 但 CAGR 降(現金拖累)→ **風控工具非報酬增強、目標依賴**。工具 `run_economic_eval`/`verify_regime_timing`/`verify_regime_portfolio`。教訓:強單因子≠增量、顯式線性交互冗餘、高相關≠可刪、rank-IC 對離群穩健、context 不可橫斷面驗。

**殘留盲點(未修)**:🟡 `pe_ratio` 極端值(max 14500x)未 winsorize(C1;五鏡判 keep、但餵 Ridge StandardScaler 仍受離群影響);🟡 `lending_fee_rate_mean_30d` 名實不符(實近 100 筆均);🟡 相對化母原則③多數仍 raw(pb_xsec_rank/industry_demean 候選經漏斗淘汰、無單因子增益)。完整見 `reports/augur_feature_thinking_gaps_20260626.md`。

驗證紀律(#15):特徵值主張先 psql 比對;IC 顯著性禁裸用 iid Eff-t、用 `metrics.effective_t_hac`(去相關);候選提拔走 `scripts/verify_candidate_promotion.py`/`verify_lens_promotion.py`。見 [[augur-project-map]]。

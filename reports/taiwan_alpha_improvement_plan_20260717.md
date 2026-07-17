# 台股預測報酬率/準確率提升計畫(2026-07-17 定稿)

**狀態**:定稿,呈 hugo 拍板(#20 計畫先行;拍板後動工前另行執行前確認)。
**版本沿革**:草案(2026-07-17 上午)→ 三路對抗審查(治權一致鏡/完整性鏡/期望值誠實鏡,四路 live 實證)→ 本定稿逐條處置 51 項發現(§零)。
**範圍**:相對強度軸(橫斷面排序→long-only 投組)。方向軸為獨立軸(arena 8 隊+3 基線 live 中),不在本計畫轄區、僅作邊界引用。
**框架**(hugo 已認可):三軸期望值排序 = **①資料維度(最高)> ②組合構建維度(中高、最被低估)> ③方法維度(最低)**。
**證據紀律**:所有數字出自 live DB query + live code Read/Grep + reports/ 判決文,零記憶推測;定稿另對全部 blocker/major 級審查宣稱做獨立 live 複核(§零末)。
**導讀(30 分鐘)**:§零 只讀導言+不採/部分採列(3 分)→ §一(5 分)→ §二 只讀 2.3-2.5(4 分)→ §三 各軸摘要表+D1/D2/P6(8 分)→ §四.3 + §五 + §六.7-6.9 + §七(10 分)。§零全表、§二全表、附錄=執行期查閱件。

---

## 零、審查發現處置總表

三路審查共 **51 項**(含 missing):**50 採納、1 部分採納、0 不採**。多數發現彼此獨立驗證同一批 live 事實,定稿再獨立複核後全部成立——這不是客氣,是審查真的抓到了「計畫與 live 機械現實的接線」斷點。重複發現以「=」標合併。

### 審查 A(治權一致鏡)

| ID | 級 | 發現(摘) | 處置 | 落點 |
|---|---|---|---|---|
| A-B1 | blocker | 候選直寫 feature_values 違 audit 邊界(候選現行住所=feature_candidate_values;canonical_features 無前綴過濾→密集候選自動混入生產交集) | **採納**(=B-M4) | §2.4-7、§4.1、附A/B |
| A-M1 | major | trial_ledger UNIQUE 鍵無欄可表達建構/標籤變體→N 靜默低估 | **採納**,選方案(b) 加 recipe 欄+DDL(=B-B1) | §4.3、附A |
| A-M2 | major | P6 月頻觸發 release_lag.py 明文金融股 60 日休眠雷 | **採納**(=B-m5) | §3.2 P6 前置 |
| A-M3 | major | M4 漏權重通道洩漏(encoder 預訓練語料可能含回測窗) | **採納**,三項硬前置 | §3.3 M4 |
| A-M4 | major | 建構/成本口徑變更後 econ_verdict/revalidation/registry/輸出契約同源鏈無刷新步驟 | **採納**,新增 Phase 1 收尾項 | §五 1-5 |
| A-M5 | major | D8 分類回套=自我授權接受回望通道,屬決策層 | **採納**,列拍板點+快照期主證據設計 | §3.1 D8、§七 |
| A-m1 | minor | P2 新換手口徑連動 risk_policy.turnover_budget(0.75 錨舊口徑)失錨 | **採納** | §五 1-2 驗收 |
| A-m2 | minor | P4「清償 G2」過度宣稱(G2=vol target×趨勢過濾雙件套;基準切換待 G3/G4) | **採納**(=B-M5) | §3.2 P4 |
| A-m3 | minor | §4.2「ΔSharpe +0.05」不可溯卻掛「現行口徑」 | **部分採納**:定稿實查**有出處**=`scripts/verify_economic_reexam.py:108`「ΔSharpe 有感升(>+0.05)」——非不可溯;但該處屬 print 級判讀非機械閘,故採納其精神:§4.2 逐數附 SSOT,+0.05 引該行並由本計畫升格為預註冊明文閾值(**值不變、非新值**) | §4.2 |
| A-x1 | missing | 預診放棄之候選+預診結果須入 reports 留痕(N 語境可稽核) | **採納** | §3.2 P0、§4.3(a) |
| A-x2 | missing | spread 表須 COMMENT as-of 語意+禁作特徵消費(升表級) | **採納** | 附A DDL |
| A-x3 | missing | 候選清除點名 fc.clear_candidates(機械工具、selftest 有鎖) | **採納** | §4.1 |
| A-x4 | missing | M4 選維 config 須落鍵 | **採納**(併 recipe 詞彙表) | §4.3(b) |
| A-x5 | missing | 輸出契約 fail-closed trigger 複核斷言 | **採納**(併 1-5) | §五 1-5 |

### 審查 B(完整性鏡)

| ID | 級 | 發現(摘) | 處置 | 落點 |
|---|---|---|---|---|
| B-B1 | blocker | ledger 遷移 DDL 缺席(construction key+回填+UNIQUE 擴) | **採納**(=A-M1) | §4.3、附A |
| B-M1 | major | 稀疏公平測重檢**已完成**(reexam_sparse_candidates.py+verify_economic_reexam.py 已存在已跑),草案當未來 backlog=重做已完成工作 | **採納**:§2.3 改寫、fair-test-confirmed 補墓碑、刪 backlog 重檢項 | §2.1/2.3 |
| B-M2 | major | §2.5「FRED vintage reader 無實作」失實——macro_vintage.py 已是完整實作 | **採納**:改寫;其餘三條(gov_bank Y4/pe winsorize/金融股 60 日)複核仍成立 | §2.5 |
| B-M3 | major | 「零新驗證碼」不實(verify_candidate_promotion CANDS 硬編碼、慣例=每家族一支) | **採納**,選方案(a) 參數化通用漏斗 runner;表述改「**判準零改動、驗證碼有新增**」 | 附B |
| B-M4 | major | 候選隔離倒退(staging 表已存在、7 支舊 script 直寫=歷史工件) | **採納**(=A-B1;舊 script 收斂列 backlog) | §2.4-7 |
| B-M5 | major | P4 半清償+decision-G3/G4 拍板點未列 | **採納** | §3.2 P4、§七 |
| B-M6 | major | Phase 2/3 無驗收條款 | **採納**,逐項補驗收欄 | §五 |
| B-m1 | minor | 附A 缺既有表 schema+risk_policy 6 列盤點與相容裁決 | **採納**(live 實查回填) | 附A |
| B-m2 | minor | COST_TW 散落 >10 支、run_backtest cost 預設 0.0=忘傳假通過 | **採納**,P7 前置 SSOT 化+防呆 | §3.2 P7、附B |
| B-m3 | minor | 證據錨過時(model_registry 15 非 9、column_catalog 769、ledger=ridge24+gbdt8) | **採納**(全數 live 重核回填) | §1.1、證據索引 |
| B-m4 | minor | D1 放量漏「與 audit 對帳同 IP 互斥」排程約束+FinMind Sponsor 依賴 | **採納** | §五 1-8 |
| B-m5 | minor | P6 未交叉引用 release_lag 明文警示 | **採納**(=A-M2) | §3.2 P6 |
| B-x1 | missing | 墓碑漏 field_correlation §D 六個弱欄名錄 | **採納** | §2.1 |
| B-x2 | missing | short-interest 三表未歸位 | **採納**:併 D4 範圍註記+backlog 具名 | §3.1 D4 |
| B-x3 | missing | P0 缺曝險/歸因分解(size β vs alpha) | **採納** | §3.2 P0 |
| B-x4 | missing | live OOS 累積無承接管線工作項 | **採納**,新增 1-9 | §五 1-9 |
| B-x5 | missing | 成本缺執行時點維度(收盤 vs T+1 開盤) | **採納**,入 P7 範圍 | §3.2 P7 |
| B-x6 | missing | 「飽和定論係污染前掃描」附帶條件懸空 | **採納**:明文裁定——**建議結案不重掃**(重掃=對凍結窗再取樣付 N、期望值低於未開採表;D1-D8 本身即乾淨口徑之新開採),列拍板點 | §3.1 backlog、§七 |
| B-x7 | missing | 端點節未顯式宣告 N/A | **採納** | 附C |
| B-x8 | missing | D1 資料源不完整(accruals 需損益表、net issuance 需股本沿革) | **採納** | §3.1 D1 |

### 審查 C(期望值誠實鏡)

| ID | 級 | 發現(摘) | 處置 | 落點 |
|---|---|---|---|---|
| C-M1 | major | P6「√(T−1)~1.75×」是尺度混淆(per-period 口徑下 z 頻率近不變;deflation.py 自立過同族血案碑) | **採納**:重推降評,§1.2 拆開——唯 live OOS 是乾淨 √T 槓桿 | §1.2、§3.2 P6 |
| C-M2 | major | KPI 錨挑了較好看的 DSR(75.6% vs 0.407 同表並存未對帳) | **採納**:雙基線並列、保守值 0.407 為操作起點、對帳=P0 交付、KPI SSOT 宣告列拍板點 | §1.2、§七 |
| C-M3 | major | D2「真未用」被自家墓碑反證(同表 name 維度 ≥4 具屍體、家族基率≈0/5) | **採納**:降評低-中+「新角度差異」進場條款 | §3.1 D2 |
| C-M4 | major | 「GBDT 3/4 cell 輸 Ridge」與 live ledger 不符(since2014=2/4 輸、since2021=1/4 輸) | **採納**:live 重查證實,§1.5/§2.2/M1 改寫(H60 主 cell 明顯輸、餘互有勝負無檢定) | §1.5、§2.2、M1 |
| C-M5 | major | 全計畫無期望值算術(N 預算/SR_0 敏感度/KPI 位移/do-nothing 基準) | **採納**:§六 新增三節;數字由 P0 本地實算(#9 不現編) | §6.7-6.9 |
| C-M6 | major | D1 反證漏引(Pincus 2007/Titman-Wei-Xie 2013/McLean-Pontiff 2016/Hou-Xue-Zhang 2020)+零檢定力分析 | **採納**:補反證、「高」限定為相對評級、預期結局分布明寫 | §3.1 D1 |
| C-m1 | minor | P4 漏 Cederburg et al. 2020 反證;「速贏」高報 | **採納** | §3.2 P4 |
| C-m2 | minor | Phase 1「速贏」自相矛盾;「換手降 30-50%」全計畫唯一零引註 | **採納**:改名+雙籃拆分;30-50% 降格為待 P0 實測假設 | §五 Phase 1 |
| C-m3 | minor | M4 評級與自述矛盾 | **採納**:降低-中+trial 硬上限 ≤2 筆 | §3.3 M4 |
| C-x1 | missing | do-nothing 反事實基準 | **採納**(P0 實算) | §6.9 |
| C-x2 | missing | N 預算表+SR_0 敏感度 | **採納** | §6.7 |
| C-x3 | missing | 候選成功之 KPI 位移量化 | **採納** | §6.8 |
| C-x4 | missing | DSR 雙基線對帳+SSOT 宣告 | **採納**(=C-M2) | §1.2 |
| C-x5 | missing | D1 檢定力分析(T=25 最小可測效應) | **採納**,列 D1 前置交付 | §3.1 D1 |
| C-x6 | missing | 反證引註補齊 | **採納** | §3.1/3.2 |
| C-x7 | missing | P6 混頻 SR_0 並池口徑相容性 | **採納**,列 P6 技術前置 | §3.2 P6 |
| C-x8 | missing | P1/P3/M3 攻同一換手邊際,收益不可疊加 | **採納**,合併上限條款 | §3.2 末 |

**定稿獨立複核清單**(不轉述審查、逐項以 live 重驗):`feature_candidate.py:33` FEATURE_TABLE="feature_candidate_values"+`:126` clear_candidates+`:148` selftest 鎖生產表唯讀;`baseline.py:31,41-48,60-61` canonical_features 無前綴過濾+CANDIDATE_TABLE 併讀「不看候選表→core 不受污染」;trial_ledger UNIQUE=(model,horizon,top_frac,weight,feats_hash,cost,sample_since)(pg_constraint 實查)、32 列=ridge 24+gbdt 8;model_registry 15、column_catalog 769、dataset_catalog 97;risk_policy 6 列(H60/H120 × dd_circuit/max_position/turnover_budget 0.75 warn);feature_candidate_values 現 0 列;feature_values DISTINCT=35、PK=(panel_date,stock_id,feature);macro_vintage.py 存在;release_lag.py 標頭金融股 60 日警語+「勿讓 panel 改為季中/月頻消費金融股財報」原文;reexam_sparse_candidates.py/verify_economic_reexam.py 存在;`verify_economic_reexam.py:108` ΔSharpe>+0.05;`verify_incremental_fair.py:111` ±0.002;`verify_candidate_promotion.py:27` CANDS 硬編碼;sop_master `:192` G2=「波動目標×趨勢過濾」+`:165` 雙基準待 G3/G4;GBDT vs Ridge 全 cell 矩陣(ledger 實查,§1.5);deflation.py per-period docstring(√ppy 灌水血案自記);DSR 0.407=short_horizon_verdict_20260709 實文。

---

## 一、誠實邊界

### 1.1 現況錨(全部 live 實證,定稿重核)

| 項 | 現況 | 來源 |
|---|---|---|
| 特徵 | feature_values 35 特徵生產中;canonical 模型口徑 ~29(CANONICAL_START=2008-12-31 起全 panel 交集;gov_bank 被交集排除) | live DB DISTINCT+baseline.py |
| 模型 | RankRidge H60 LO=部署主(thin_unestablished);H40/82/120=thin 追蹤;H20=econ **dead**。model_registry 全表 15 列(RankRidge 家族 9+方向軸 6) | model_registry+econ_verdict_rule |
| headline | ridge_H60_LO(asof_incumbent):net Sharpe 1.1972、bench 0.7623、net_excess 0.4348、HAC-t 6.95;T=25 非重疊季 panel;state=deploying_unestablished | revalidation_verdict 2026-07-08 |
| **DSR 雙基線** | **0.407**(short_horizon_verdict_20260709 輪,H60 n=25)與 **75.6%**(deflation_verdict_20260708,N=16;N=8 池 89.5%)——兩者皆真、trial 池與計算路徑不同,**對帳=P0 交付(§3.2);未對帳前一律雙列並報、敘事以保守值 0.407 為操作起點**;deflated 有效 Sharpe 0.2646 | 兩 verdict 並列 |
| 誠實地板 | 廣宇宙 pit_broad ~1.00 為主誠實地板(deflated ~0.07);成本升至 ~1.1% 即穿零 | deflation/survivorship verdicts |
| trial 記帳 | trial_ledger 32 列 = ridge 24(4 horizon×LO/LS/LS+borrow×2 池)+ gbdt 8(LO×4 horizon×2 池) | live DB 實查 |
| 候選 staging | feature_candidate_values 存在、現 0 列;audit 邊界=生產表 feature 層獨佔寫 | live DB+feature_candidate.py |
| 資料地基 | G1-PIN 2026-06-30;解凍後 live 增量維運(v1.9.0) | 治權 |
| 方法基準 | 台股 TSFM benchmark:top5 股×4 模型×20 DM 檢定**零顯著**(最小單尾 p=0.408、RW 4/5 股 MAE 最低) | tsfm_taiwan_benchmark_20260717 |

### 1.2 能提高什麼(目標函數)

1. **deflated 淨值**(主 KPI):DSR(雙基線 0.407/75.6% → 95% 確立線)、deflated 有效 Sharpe(0.2646 上移)、成本敏感度帶內 DSR 曲線、pit_broad 誠實地板。**KPI SSOT=deflate_headline_verdict(deflation.py per-period 口徑、ledger 機械 N);雙基線對帳與單一基線宣告→須 hugo(§七-3)**。
2. **檢定力 T——只有一條乾淨槓桿**:**live OOS 累積**(G1-PIN 後同頻新期數=免費檢定力,承接管線見 §五 1-9)。~~tranche/月頻觀測~~不是:per-period 口徑下頻率變更 z 近不變(§3.2 P6 重推);此拆分係 C-M1 修正。
3. **成本真實度**:逐股價差、權重法 turnover、執行時點、容量邊界——數字預期微降,但地板變真(#15)。
4. **未開採資料維度的新 alpha**:唯一能抬 gross 的正途(§三資料軸)。

### 1.3 不能提高什麼(誠實承認)

- **個股 30/60 天絕對漲跌機率**:假兆、違靈魂;系統只做橫斷面相對強弱排序可信度(short_horizon_verdict)。
- **已判死假說之數字**:方向軸(no-v3)、H20 經濟價值(h20_dead_no_shortcut)、long-short(2021+ 崩潰、兩度坐實不採)。
- **「headline 1.20 已確立」**:deflation FAIL 前不得宣稱已驗證可交易;定位=promising-not-proven。

### 1.4 明文排除清單(鐵律;計畫全程有效)

1. **不放鬆判準換數字**(不挪門柱;選型偏誤已被 deflation verdict 定性為敵③向量)。
2. **知識素養層零量化價值、永不進預測管線**(治權鎖;本計畫全部候選皆市場資料衍生、零交集——三路審查 live 核對零違規)。
3. **no-v3**:方向軸判死假說不得對凍結資料重試(邊界見 §2.3)。
4. **每候選一律四道提拔漏斗+經濟終關**(§四)。
5. **預期大部分候選會死=功能非缺陷**。
6. 衍生鎖:H≥252 禁入(walkforward `_H_FORBIDDEN`)、pan-hist 宇宙/iid Eff-t 禁用於提拔、多 seed 不得抬 deflation N(DDL 證偽)、TSFM 點預測判死、NN/Transformer/AutoML/外部 SOTA 移植判 X、不得跑多標籤/horizon 挑好看者當 headline、**候選不落生產表 feature_values(住 staging,§4.1)**。

### 1.5 三軸排序根據(為何資料>組合>方法)

- **①資料最高**:治權認知「真天花板=資料累積非碼」;五輪探索全淘汰=「已掃表深度飽和」,但飽和判決僅及已掃過的表——財務三表複合、法人細分、漲跌停、處置、CB、ADR、借貸擔保品**從未進過掃描**。且 G1-PIN 後 live OOS=免費檢定力,新方法要付 N(§4.3)。附帶誠實條件(飽和定論係污染修復前掃描)之處置:**建議結案不重掃**,見 §3.1 backlog+§七-6。
- **②組合中高、最被低估**:SR_pp↑(降 turn×cost/降序列變異)與 DSR 分母縮(壓 kurt)**全不需新 alpha**;sop_master G2 規則地板是已拍板 doctrine 零實作=欠債。注意:√T 通道已自②軸移除(C-M1),②軸真通道=SR_pp 與分母。
- **③方法最低**:TSFM 20 檢定零顯著(2026-07-17 實證);**GBDT vs Ridge(live ledger 修正句):部署主 H60 GBDT 明顯輸(0.913 vs 1.197 since2014;1.109 vs 1.265 since2021),H20/H40 GBDT 微勝、H120 分池互異,皆無顯著性檢定**——單 cell 微勝不構成換模型依據;交互冗餘判決另證共線使非線性無增量。「換更強模型」不是主槓桿。

---

## 二、墓碑地圖(新候選禁踩;重測需「新角度或新資料」)

### 2.1 已證偽特徵名錄

| 墓碑 | 死因 | 證據 |
|---|---|---|
| holding_gini/hhi/entropy(八二P1) | 與 top_holders_pct 共線 +0.97 冗餘 | lens_validation_20260627 §二 |
| return_skew/kurt/gini(八二P4) | IC≈0 | 同上 |
| inst_flow_hhi / inst_flow_max_share | Eff-t<2 | 同上 |
| momentum_accel/resonance/vol_term_structure/range_position_60d/days_since_low/max_drawdown | Eff-t<2 | 同上 |
| volatility_20d | 與 range_mean_20d +0.94;剪了反升 Δ+0.0018(生產唯一真剪) | 同上 §四 |
| pb_xsec_rank / pb_industry_demean | 漏斗淘汰、無單因子增益 | feature_candidate.py:35 |
| pb_self_pctile_252d | 單獨顯著但多因子冗餘 | verify_candidate_promotion.py:27 |
| inst_govbank_divergence | pan-hist 2.53→as-of 1.67(pan-hist 高估教科書案例) | methodology §四漏斗4(a) |
| x_gini_resid_size | 全戰役最強 HAC-t −6.29 卻多因子零增量(模型自組) | campaign_summary §五 Track A |
| x_flow_phase_divergence / x_price_flow_divergence | 顯式線性交互冗餘 | 同上 |
| x_mktcap_rank_chg / x_mom_rank_chg(馬太) | 0.58 不顯著/1.96 臨界且增量全負 | 同上 Track B |
| x_day_trade_ratio_20d / imbalance(當沖) | HAC-t −2.09 過但共線 +0.79、增量 −0.023 有害;**公平測+經濟終測後再確認死亡(fair-test-confirmed)** | verify_daytrade_candidates.py;reexam+verify_economic_reexam |
| x_inventory_ratio_chg 系(phase-2 稀疏) | 同宇宙 impute 公平測+經濟終測後確認死亡(**fair-test-confirmed**) | reexam_sparse_candidates.py+verify_economic_reexam.py |
| dealer_net_r / foreign_pct_x_turnover | 漏斗淘汰 | verify_signal_promotion.py |
| foreign_trust_div | IC 增量 4 格全非負,經濟終關敗(net ΔSharpe 4格3負、Calmar/MaxDD 全惡化)——「IC 撐住≠可交易」實證 | verify_economic_candidate.py |
| money_x_inst_net | crude 掃描 t=3.6 → as-of HAC-t 0.17 崩潰 | verify_interaction_promotion.py |
| x_revenue_industry_share / share_mom / x_inventory×2(phase-2 基本面) | 真正交(\|r\|<0.5)仍零增量=深度飽和根據 | campaign_summary §十一 |
| momentum「精英核心單因子 alpha」 | 特徵仍在產(多因子貢獻),單因子 rank IC<0.02 失效 | methodology §六 |
| **6 個未探索 raw 欄 crude 全弱**(B-x1 新增) | short_sale_balance(−0.027 且偏 size)/short_margin_ratio/foreign_room(與既有 −0.989 機械冗餘)/retail_pct(弱反向)/holder_count/lending_volume,\|IC\|≤0.027 | field_correlation_20260627 §D |

### 2.2 已證偽假說名錄

| 假說 | 判決 |
|---|---|
| 方向軸 v1 六門 / v2 K=4 家族 | 全 evaluated_fail、never_shown;v2 二次證偽 → no-v3 入憲 |
| 方向擇時經濟價值 | v1/v2 擇時 Sharpe≈buy&hold |
| 個股絕對漲跌機率可交付 | 假兆、違靈魂 |
| long-short 市場中性 | 2021+ 0.406 崩潰輸基準;借券 2%/yr 再砍;alpha 在 long 尾,確定不採 |
| H20 相對強度經濟價值 | econ dead;h20_dead_no_shortcut 硬規 |
| 「換更強模型」為主槓桿 | **修正句(C-M4)**:GBDT 於部署主 H60 明顯輸 Ridge、其餘 cell 小幅互有勝負且無顯著性(live ledger);共線使非線性無增量(交互冗餘判決);TSFM 零顯著 |
| NN/Transformer/AutoML/SOTA 移植 | 過擬合三要件全備+clean-room 違反,判 X |
| TSFM 日頻點預測有 edge | 20 檢定零顯著;合法用途=方向 arena 候選 |
| 特徵層繼續挖掘(既有宇宙、H20-60) | 五輪全淘汰→深度飽和;前沿=未開採表(附帶條件處置見 §3.1 backlog) |
| 顯式線性交互 / 強單因子=可提拔 / 高相關=可刪 / winsorize 抬 IC | 四條方法論教訓 |
| context/regime 過橫斷面漏斗 | 全股同值→IC 恆 0;regime-conditional=風控工具非報酬增強 |
| headline 1.20 已統計確立 | deflation FAIL;promising-not-proven |
| 下市 survivorship 推低 headline | 實證 ≈0(+0.0023);−16.5% 係 incumbency 宇宙定義誤歸 |
| 多 seed 抬 deflation N | trial_ledger UNIQUE 鍵不含 seed,DDL 證偽 |
| pan-hist / iid Eff-t 可用於提拔 | 禁;一律 core_universe_asof + HAC |
| H≥252 / ensemble 堆疊超越 Ridge | walkforward 禁入 / 階段 3 未勝 |
| **年化 SR 配 √(T−1) 的 DSR 算術** | deflation.py 血案自記(z 灌水 √ppy、DSR 高估~14pp);**衍生:頻率變更(季→月)非 √T 槓桿(§3.2 P6)** |

### 2.3 特殊墓碑與邊界(必讀;B-M1 改寫)

- **x_gross_margin_pctile 冤殺翻案先例**:初判淘汰係覆蓋假象 bug(稀疏候選缺值股被踢→宇宙縮 37%→Δ假負);同宇宙公平測翻案 productionize。**規則:稀疏候選必經 verify_incremental_fair 同宇宙 impute 公平測後才蓋棺**。
- **稀疏舊淘汰之公平測重檢:已完成、非 backlog**——`scripts/reexam_sparse_candidates.py`(7 稀疏候選=當沖2+基本面5,同宇宙 impute 公平 Δ)+`scripts/verify_economic_reexam.py`(3 目標經濟終測)已存在已跑;翻案唯一=gross_margin_pctile,day_trade/inventory 系公平測後確認死亡(已補 §2.1 fair-test-confirmed)。草案誤列 Phase 2 backlog,定稿刪除。
- **gov_bank_net_buy_60d 半墓碑**:在 feature_values 但被 canonical 交集排除(LOOΔ −0.087);Y4 金額vs股數 sign-flip 未修(未爆因已排除)。
- **no-v3 邊界**:僅鎖「同假說對凍結資料重試」;真未來 prereg-now-evaluate-later 新 gate 合法(A3/A4/arena 先例)。相對強度軸無 no-v3,但同凍結窗重試的真約束=trial_ledger 記帳墊高全體 DSR 地板(§4.3)。

### 2.4 盲點守則(每個新候選的進場檢核)

1. **as-of 口徑鐵則**:crude 掃描結果一律不算數(money_x_inst_net t=3.6→0.17);提拔一律 core_universe_asof 逐 panel PIT + HAC。
2. **發布時點先定錨**:每張新表先裁 as-of 欄與 lag gate(財報 45/90 日、月營收公告月 15 日、集保 7 日、panel stale 45 日、毛利 stale 400 日)——搞錯=沉默污染,屬理解層 ultracode 保留區(#28)。
3. **覆蓋假象**:稀疏候選同宇宙公平測(§2.3)。
4. **共線先查**:與既有 35 特徵相關矩陣先看——HAC-t 過但共線者仍可有害(day_trade 前車)。
5. **真零 vs 缺列**:表未涵蓋期即缺列,走 `_table_covers` gate。
6. **髒值**:停牌 close=0、buy/sell 負值、varchar date、`1911-00-00`、財報/營收單位=元。
7. **實驗隔離(A-B1 改寫)**:候選一律 `x_` 前綴且**只寫 staging 表 `feature_candidate_values`**(入口=`audit/feature_candidate.py` 之 `ensure_candidate_table`/`fc.FEATURE_TABLE`;audit 邊界:生產表 feature 層獨佔寫)。漏斗全程只讀 staging(`baseline._panel_matrix` 已支援明點名併讀;`canonical_features` 不看候選表→core 不受污染——**隔離靠表分離、非靠前綴**)。清除一律 `fc.clear_candidates`(機械工具、selftest 有鎖),不手寫 DELETE。唯全過漏斗+hugo 拍板 productionize 後,才由 feature 層寫 feature_values(除前綴)。7 支歷史直寫 feature_values 之舊 verify_* script(construction v4 點名)=歷史工件,新候選禁沿用;其收斂列品質 backlog、非本計畫主線。

### 2.5 殘留埋雷(定稿逐條複核;B-M2 修正)

- ~~FRED vintage reader 無實作~~ → **修正:`src/augur/features/macro_vintage.py` 已是完整實作**(Tier A/B 濾版、visible_cutoff/as_of 唯一消費門、fail-loud、自測 CLI)。**真殘留=尚無生產特徵接線**:任何 macro 特徵一律經 `macro_vintage.as_of()` 消費,禁對 fred_series 寫 raw SQL。
- gov_bank Y4(金額vs股數,~3% 股 sign 翻轉)未修——複核仍成立。
- pe_ratio 14500x 未 winsorize(rank-IC non-issue,Ridge scaler 仍受影響)——複核仍成立。
- release_lag 金融股 Q1/Q3 60 日未實作(release_lag.py 標頭明文,含「勿讓 panel 改為季中/月頻消費金融股財報」警語)——複核仍成立;**D1 候選碰金融股前、及 P6 月頻化前,皆須先補(D1∧P6 共同前置)**。

---

## 三、候選假說清單

> 期望值三級誠實評;「漏斗路徑」皆指 §四標準路徑,只列該候選特有前置與死因風險。

### 3.1 ①資料軸

**摘要表(定稿評級)**

| # | 候選 | 資料源 | 期望值 | 成本 | 首要死因風險 |
|---|---|---|---|---|---|
| D1 | 財務三表複合異象 | BalanceSheet+CashFlows+FinancialStatements(+股本沿革) | **高(相對)** | 中-高 | 台股先驗弱於美股文獻(反證見下);T=25 檢定力 |
| D2 | 法人玩家細分 | 既用長表 name 維度 | **低-中**(C-M3 降評) | 低(零新 sync) | 同維度已陣亡 ≥4 支;與 4 個 inst 特徵共線 |
| D3 | 漲跌停事件 | TaiwanStockPriceLimit | 中 | 低 | 與動能/波動家族共線 |
| D4 | 處置/賣空約束狀態 | Disposition+Suspension(+short-interest 三表歸位) | 中 | 低-中 | 經濟終關(訊號在但不可交易) |
| D5 | CB 溢價/轉換進度 | ConvertibleBond 家族 | 中 | 中 | 覆蓋窄、stale price |
| D6 | ADR/美股產業領先 | USStockPrice | 中 | 中 | 產業級需分類回套;大盤級已證冗餘 |
| D7 | 借貸擔保品隱形槓桿 | LoanCollateralBalance | 中 | 中 | 文獻先驗低;序列 2016 起 |
| D8 | 產業動能 | StockInfo+IndustryChain | 中(**附拍板點**) | 低-中 | 回套=回望通道(§七-5) |

**D1 財務三表複合異象(資料軸主力)**
- 假說:asset growth、accruals(盈餘−營運現金流)、NOA、FCF yield、net issuance、capex 成長六族(Sloan 1996、Cooper-Gulen-Schill 2008、HXZ q-factor、Pontiff-Woodgate)。
- **反證引註(C-M6 補齊,列為評級限定)**:Pincus-Rajgopal-Venkatachalam 2007(accruals 異象集中普通法系;台灣屬大陸法系→先驗打折)、Titman-Wei-Xie 2013(asset growth 在發展中亞洲市場弱/不顯著)、McLean-Pontiff 2016(發表後平均衰減 ~58%)、Hou-Xue-Zhang 2020(多數異象複製失敗)。**「高」=相對於本計畫其他候選的期望值最高(BalanceSheet/CashFlows 特徵層真零使用,grep 已核),非「大概率成功」;預期結局分布=0-2/6 族存活、存活者效果量 +0.002 IC 量級**。
- 資料源(B-x8 補齊):TaiwanStockCashFlowsStatement + TaiwanStockBalanceSheet(合計 ~8.2M 列在庫、特徵層零使用)+ **TaiwanStockFinancialStatements(盈餘,accruals 必需、已在庫)**;net issuance 主路徑=BalanceSheet 股本科目差分,輔以在庫資本異動類表——具體表名/覆蓋=D1 前置盤點交付,不預先臆斷。
- as-of 欄:date=季底≠可見日;必經 release_lag.financial_release_date(季底+45/90 日);金融股 60 日 lag 未實作(前置,§2.5)。
- **檢定力前提(C-x5)**:D1 預註冊時附最小可測效應分析——2021+ 季頻 T=25 面板、ΔIC≥0.002+HAC-t≥2 門檻下,慢頻基本面異象即使為真也可能測不出;此為裁決「族死亡=異象不存在 vs 檢定力不足」時的誠實邊界,預先寫死、不事後補。
- 成本:中-高。前置工程:(a) BalanceSheet 缺季修復(2016-19、2022缺Q4/2023僅Q1Q2/2024僅Q3Q4;FinMind 重抓=API 放量);(b) CashFlows YTD 去累計(20累計/4水位/6混合已逐 type 分類);(c) type 碼 origin_name 解碼(224 碼);(d) 金融股 IFRS 科目缺口。
- 漏斗路徑:標準;稀疏處理走同宇宙公平測。

**D2 法人玩家細分(C-M3 改寫)**
- **誠實現況**:「生產聚合未用」成立(chip.py/phase.py 皆 sum GROUP BY date,已核),但**探索史已在同一 name 維度陣亡 ≥4 支**——foreign_trust_div(經濟終關死)、inst_flow_hhi/max_share(Eff-t<2)、dealer_net_r(漏斗死),另 money_x_inst_net 崩潰、gov_bank 半墓碑;家族基率≈0/5。「最快可試」是成本敘事,不得外溢為期望值敘事。
- **進場條款**:每支 D2 候選須逐支書面說明「與死者的新角度差異」(如:投信季底作帳之**季節條件化**≠已死的水位/背離;外資**連續買賣天數**≠已死的集中度)——說不出差異者不進 Phase 1。
- 資料源:既用長表 TaiwanStockInstitutionalInvestorsBuySell 之 name 欄;as-of=date(盤後公布,date≤panel 安全)。陷阱:buy/sell 負值;拆分口徑 2012 後才全→`_table_covers` gate。共線預診先行。

**D3 漲跌停事件**
- 假說:rolling 漲停/跌停計數、連板 streak、收盤距漲跌停距離(磁吸)、觸停後續動能/反轉。資料源 TaiwanStockPriceLimit(11.9M 列、2000-01 起,從未掃描)。
- as-of:漲跌停價由前日收盤決定=盤前已知,全 84 表最乾淨者之一;rolling 計數 date≤panel 安全。
- 文獻:Cho et al. 2003(磁吸,TWSE 樣本)、lottery 偏好;反證:多為日內/日級效應,H20-120 衰減不明。
- 陷阱:2015-06-01 漲跌幅 7%→10% 制度斷點(標準化方案入預註冊配方);季度 panel 稀釋→須長窗計數非旗標;與 momentum/range/volume_surge 共線(當沖前車)。

**D4 處置/賣空約束狀態(B-x2 歸位)**
- 假說:處置中旗標/近 N 日處置次數(投機過熱→反轉)、暫停融券=賣空約束→高估回落(Miller 1977、Chang-Cheng-Yu 2007)。DispositionSecuritiesPeriod(2005 起 2,042 檔)+MarginShortSaleSuspension+DayTradingSuspension。
- as-of:公告日 gate(實測公告先於處置期,均值 1.47 日、min 0);區間=ex-ante 已知。
- **short-interest 三表歸位(表級盤點閉環)**:TaiwanDailyShortSaleBalances、TaiwanStockSecuritiesLending、TaiwanStockDayTradingBorrowingFeeRate 併入 D4 預診範圍——注意其 crude 欄位掃描已弱(§2.1 六弱欄墓碑:short_sale_balance/short_margin_ratio/lending_volume),D4 若用此三表**須為「約束狀態/事件」新角度**(非水位重掃),否則不試;預診交付=三表逐一歸位判決(併入/backlog/判死)。
- 經濟終關高風險:處置股分盤交易/流動性驟降=「IC 撐住≠可交易」典型候選;效應集中小型投機股,可能被 core universe 濾掉大半。稀疏→狀態化區間旗標(E 類真零前例)。

**D5 CB 家族**:溢價率(欄現成)、套利賣壓、OutstandingAmount 遞減=轉換進度。as-of=date 日頻+Overview 權利日(ex-ante 契約)。文獻 Choi-Getmansky-Tookes 2009。陷阱:Overview.date `1911-00-00` 非法值清洗、覆蓋僅發 CB 股、stale price 噪音。

**D6 ADR/美股產業領先**:ADR 溢價(TSM 7,216 列;~5-10 檔→窄)、美股產業回報 t−1→台股電子/非電子傾斜。as-of=美東收盤,台股 t 只用 ≤t−1(時區=唯一命門)。陷阱:國際股 Adj_Close overflow→raw close 自算;匯率用在庫 DEXTAUS。

**D7 借貸擔保品隱形槓桿**:不限用途借貸餘額=margin_usage_ratio 看不到的大戶槓桿通道;與融資餘額背離。5.3M 列 37 欄從未掃描。as-of=date(盤後,finalize_lag=1)。誠實定位:「資料獨家性高、文獻先驗低」。陷阱:實質起點 ~2016(2014 全零非真零)、37 欄勿混口徑。

**D8 產業動能(A-M5 改列拍板點)**
- 假說:產業 t−1~t−12 月回報→成分股傾斜(Moskowitz-Grinblatt 1999)。
- **回望通道誠實揭示**:無歷史快照(StockInfo 2020-06 起 249 快照、IndustryChain 2026-06-16 起),早年以現行分類回套=**事後資訊**(股票被重分類進熱門產業與其後續表現相關,可憑此通道製造假 alpha)。「學界慣例」不是本專案判準來源——**此接受與否=決策層拍板點(§七-5),計畫不逕行裁定**。
- 預設緩解配方(若拍板准做):主證據**限快照期**(2020-06+ PIT 分類);回套期僅作敏感度分析、**不得單獨支撐提拔**;快照期 panel 數不足以裁決→D8 順延至 live 累積足量後再試。

**低期望 backlog(不進主力)**:Dividend 事件(塌列壞資料 2,411 列須 DROP+re-sync,修復後可升中;AnnouncementDate/Time 為全表唯二真公告時點欄)/News 注意力(覆蓋漂移 2010=200→2023=528K)/DayTrading(已死)/BlockTrade(已掃全弱)/指數衍生品(精華已被方向軸摘)/市場級 Total*(regime=風控非報酬)/公司行動小表(n 小)/商品匯率(fred 冗餘)/國際股票(鏈路長)/infra 維度表(非訊號源)。
**既有宇宙乾淨重掃(飽和附帶條件,B-x6 裁定)**:**建議結案不重掃**——重掃=對凍結窗再取樣付 N 代價,期望值低於未開採表;D1-D8 全部走乾淨 as-of 口徑,本身即「乾淨口徑下的新開採」。此裁定**須 hugo(§七-6)**;若不採,改列 Phase 3 之後之選擇項。

### 3.2 ②組合軸(全部 no_new_alpha_needed;紀律=先本地零 usage 診斷不入 ledger,再每軸預註冊單一配方一次定案)

| # | 缺口 | 改動點 | 機理→DSR 通道 | 期望值(定稿) | 順序 |
|---|---|---|---|---|---|
| P0 | 診斷包(前置) | 新診斷 script(唯讀) | 見下方交付清單;**不入 ledger** | — | 最先 |
| P1 | buffer-zone 遲滯 | build_long_portfolio 加 prev_ids+exit_frac | rank 噪音=換手主源;降 turn×cost→SR_pp↑。「換手降 30-50% 而 gross 幾乎不損」**降格為待 P0 實測假設(無引註,C-m2)**;增益條件化於 P0 量得的 avg_turnover(若季頻換手本低,增益等比例縮) | 中高(條件化) | 1 |
| P2 | turnover 權重法量測 | `_turnover` 改半和口徑 0.5·Σ\|Δw\|(含漂移) | 量尺校準:交集法系統性低估(pred 加權 net 虛高);P1/P3 前置 | 誠實化(數字微降) | 1(先於 P1 定案) |
| P3 | 成本感知權重 | score′=pred_rank+λ·1{已持有}(單一 λ 預註冊) | 每壓 10pp 換手 0.585% 下省 ~0.16%/年、真實帶 1.5-2% 下 ~0.4-0.6%/年(機理估算) | 中高 | 2 |
| P4 | vol targeting+inverse-vol | portfolio 純函式+risk_policy 政策列 | 直攻 DSR 分母(壓 kurt/修 skew)。**G2 部分清償(vol target 側;G2 全文=vol target×趨勢過濾,趨勢過濾另列 backlog 或併本項擇一預註冊)**;**經濟裁決基準維持等權單基準,雙基準切換須 decision-G3/G4 另行拍板(§七-7)**。反證(C-m1):Cederburg-O'Doherty-Wang-Yan 2020——vol-managed 多數因子 OOS 無可靠改善;long-only 只降不升在長多市場機械減曝→**預期=MaxDD/分母改善、headline Sharpe 可能微降,非報酬勝利、不入速贏敘事** | 中(誠實化+欠債) | 1-2 |
| P5 | 多 horizon 訊號混合 | rank 平均或三等分 sleeve(擇一預註冊) | 估計誤差分散→SR_pp↑;先量 net_series 相關,>0.9 即放棄不浪費 N | 中 | 2 |
| P6 | tranche 錯開 | run_backtest 加 tranche 模式 | **重推(C-M1):per-period 口徑下季→月 T 25→~75、√(T−1) ×1.756,但 sr_pp 同步縮 ~1/√3(×0.577),z≈sr_pp·√(T−1) 淨變 ~×1.01(iid)——「1.75× 機械槓桿」撤回(deflation.py 血案同族錯誤);60td 持有重疊使月序列自相關、有效 T 再打折**。真通道=進場日錯開之 timing-luck 分散(SR_pp 溫和改善) | 中(自「高」降評) | 2 |
| P7 | 逐股有效價差+執行時點 | Corwin-Schultz/Abdi-Ranaldo 從在庫 OHLC 估 cost_bps;**+ rebalance 成交時點敏感度(panel 收盤 vs T+1 開盤,B-x5)** | 誠實化+讓 P3 有的放矢;headline 點 DSR 可能微降=假樂觀換真地板 | 誠實化 | 2 |
| P8 | ADV 容量約束 | w_i≤ρ·ADV_i·持有期/AUM(reuse apply_position_cap) | 防禦性:堵 paper alpha 依賴不可成交小型股;為 deflation 裁決補容量邊界 | 防禦性 | 3 |

**P0 診斷包交付清單(擴充後;全本地零 usage、不入 ledger、落 reports/)**:
1. avg_turnover(新舊口徑並列)+成本歸因;2. 三 horizon net_series 相關矩陣(P5 裁決);3. feature_values panel 節奏盤點(P6 裁決);4. **曝險/歸因分解(市值傾斜/產業集中/size β vs alpha;B-x3——field_correlation 已示警短券側偏 size)**;5. **DSR 雙基線對帳(0.407 vs 75.6% 之 trial 池與口徑差異,C-M2)**;6. **SR_0 敏感度曲線+do-nothing 基準(deflation.py 實算:每加一筆 trial 壓多少 DSR;SR 不變下純 live T 累積幾季自然過 95%,C-M5/C-x1)**;7. **月頻節奏下全部 lag/stale gate(45/90/60、毛利 400d、panel stale 45d)行為複核(A-M2)**;8. **因預診放棄之候選清單+放棄依據(A-x1:預診亦是用凍結資料決定測什麼的分叉,須留痕使 N 語境可稽核——不入 ledger 但誠實揭露)**。

**P6 前置(硬性)**:(a) release_lag 金融股 60 日分支落地(**D1∧P6 共同前置**,附錄 B),或月頻 panel 明文排除金融股財報衍生特徵(逐一證明現行財報消費特徵皆排除金融股,引 release_lag.py 休眠債條);(b) 混頻並池口徑覆核(C-x7):月頻 ppy 之 headline 對 trial_ledger 混頻 per-period SR_0 並池是否 apples-to-apples——deflation.trials_per_period 已逐 horizon ppy 轉換,觀測頻率變更情境須 selftest 級覆核。

**P7 前置(B-m2)**:成本常數 SSOT 化(COST_TW 散落 >10 支收斂至單一住所+逐檔改引)+run_backtest cost 預設防呆(現預設 0.0=忘傳 net==gross 假通過);per-stock 成本模式下 ledger cost 鍵表示法一併預註冊(附錄 A)。

**換手三通道合併上限(C-x8)**:P1(buffer)/P3(λ)/M3(EMA)攻同一 0.585%(真實帶 1.5-2%)成本邊際——三者收益**不可疊加,合併上限=總換手成本本身**;三項一律相對「已含前序 overlay 之基準」評估增量,不得各自對原始基準報數。

**治權相容**:全部不動預測訊號、不挪門柱;P2/P7/P8 誠實化(期望數字微降=地板變真)。每個建構變體入 ledger 抬 SR_0→亂掃參數=自己灌 N 自己壓 DSR,單一配方紀律=§4.3。雙宇宙(asof_incumbent 上界/pit_broad 主地板)並列報。

### 3.3 ③方法軸(墊後)

| # | 候選 | 期望值(定稿) | 成本 | 治權風險 |
|---|---|---|---|---|
| M1 | GBDT B4 複核收尾+lambdarank | 低(**修正句 C-M4**:ledger 既存訊號=H20/H40 gbdt 微勝、H60 明顯輸、H120 分池互異、皆無檢定——B4 未跑完=**欠債了結性質,非換模型依據**) | 低(≤6 config 預註冊) | 低;每 config 入 ledger(recipe 鍵)、不得因 H40 好看換 headline horizon、H20 不得借道 |
| M2 | 風險調整標籤 rank(H 報酬/已實現波動) | 中(標籤口徑與經濟終關對齊) | 低 | **中——判準敏感區**:預註冊「配方+裁決判準」先凍再跑,禁跑兩種挑好看,輸了誠實入檔 |
| M3 | 預測 EMA 平滑+rank 穩定度調製 | 中(半屬②軸;受三通道合併上限約束) | 低 | 低;EMA 嚴格 ≤t(#8)、過同一經濟終關 |
| M4 | TSFM-embedding-as-feature | **低-中(C-m3 降評)**=有界 option-value 實驗;誠實預期=大概率動能/波動重編碼被去相關關殺(新表徵≠新資訊:輸入仍是同一 ≤t 價格窗;同源點預測軸剛交 20/20 零顯著) | 中 | **trial 硬上限 ≤2 筆 ledger(含選維)**;**權重通道洩漏三前置(A-M3)**:(a) 揭露所用權重之訓練資料截止日與語料範圍;(b) 訓練窗與回測窗(2021+)重疊者,漏斗 PASS 一律標 provisional、終裁以 G1-PIN 後 live OOS 為準;(c) 優先選訓練截止早於回測窗起點之權重版本。選維 config 落 recipe 鍵(§4.3) |
| M5 | 板塊相對標籤 | 低(374 股產業中位數雜訊大;phase-2 前車) | 低 | 同 M2+industry as-of 定錨(理解層;連動 D8 拍板) |
| M6 | Ridge+GBDT blend/多 seed 平均 | 低 | 低 | 低;入 ledger、禁挑最好組合報 headline |
| M7 | regime-conditional 模型 | 低(既有實證:regime=風控非報酬;CAGR 19.5→12.7) | 中 | **高——f3 明文六案中 snooping 最高**;若做,kernel/regime 定義預註冊凍結單一配方 |
| M8 | NN(MLP/TFT) | 低(n=25 期×374×35 遠低於 NN 門檻;f3 紅線) | 中-高 | 中;trial 爆炸→N 惡性膨脹;三軸他項枯竭再議 |

若方法軸只挑 2 項:M2+M3(皆低成本、直擊經濟終關口徑);M1 屬欠債應了結;M4 是唯一新資訊形態但預期死亡率最高、已設硬上限。

---

## 四、驗證漏斗(走既有工具、判準零改動;驗證碼有新增——B-M3 誠實表述)

### 4.1 標準路徑(每個候選,無例外;A-B1 改寫)

```
x_ 前綴候選 → 寫入 staging 表 feature_candidate_values
             (入口=audit/feature_candidate.py:ensure_candidate_table/fc.FEATURE_TABLE;
              生產表 feature_values 全程唯讀——audit 邊界+canonical 交集隔離)
 → (0) 本地零 usage 預診(不入 ledger;放棄者連同依據入 reports 留痕):
       覆蓋率/與 35 特徵相關矩陣/as-of 欄定錨(§2.4 檢核)
 → (1) 四道提拔漏斗(通用 runner scripts/verify_candidate_funnel.py,附錄 B):
       as-of 口徑(core_universe_asof 逐 panel PIT)
       + 去相關 + Eff-t HAC(evaluation/metrics.py:effective_t_hac;禁 iid)
       + 多 seed(≥3)多因子增量(staging 併讀:baseline._panel_matrix 明點名)
 → (2) 經濟終關(scripts/run_economic_eval.py;COST_TW=0.00585、portfolio.run_backtest
       purged walk-forward embargo≥h+62td):IC 撐住≠可交易
 → (3) 穩健終關(verify_stability:逐期 t+LOO+子期同向+分位一致)
 → (4) deflation(trial_ledger 機械 N 含 recipe 鍵、deflation.py per-period SSOT、雙宇宙並列)
 → 全過=呈 hugo 拍板 productionize(此時才由 feature 層寫 feature_values、除前綴、canonical 交集重測)
   任一敗=fc.clear_candidates 清除+墓碑入檔(§二追加)
```

### 4.2 判準魔數(逐數附 SSOT;A-m3 處置)

| 魔數 | 值 | SSOT |
|---|---|---|
| IC 增量閾 | ±0.002 | verify_incremental_fair.py:111(mark 邏輯)/verify_candidate_promotion 同口徑 |
| ΔSharpe 閾 | +0.05 | **verify_economic_reexam.py:108**(「ΔSharpe 有感升(>+0.05)+MaxDD 不惡化→提拔」);原屬 print 級判讀,本計畫升格為預註冊明文閾值(值不變)——**升格確認須 hugo(§七-8)** |
| Eff-t | HAC-t≥2 | evaluation/metrics.py:effective_t_hac+漏斗工具慣例 |
| 來回成本 | 0.00585(敏感度帶 0.585%→3%) | run_economic_eval.py:16/predict_asof.py:37(P7 前置後收斂單一住所) |
| embargo | ≥h+62td | walkforward.py:22 |
| seed | ≥3 | verify_candidate_promotion.py |
| 稀疏公平測 | 同宇宙 impute | verify_incremental_fair.py |

### 4.3 N 記帳經濟學與預註冊紀律(本計畫核心紀律;A-M1/B-B1 落鍵)

- **(a) 診斷不入 ledger**:本地零 usage 量測;因預診放棄之候選+依據入 reports 留痕(N 語境可稽核)。
- **(b) 變體落鍵方案(拍板前預註冊;DDL 見附錄 A,須 hugo §七-2)**:trial_ledger 加 `recipe TEXT NOT NULL DEFAULT 'plain'` 欄、UNIQUE 擴含之、既有 32 列回填 'plain'。**詞彙表(凍結,新增詞=新預註冊)**:`plain`(現行無 overlay)、`buf{f}/{2f}`(P1)、`volT{σ}`(P4)、`lam{λ}`(P3)、`tr3m`(P6)、`ema{α}`(M3)、`label=riskadj`(M2)、`label=sector`(M5)、`m4dim{k}`(M4 選維)。消費端 N DISTINCT 口徑(deflate_headline_verdict/revalidate)同步納 recipe(#12 兩處一起改),遷移 script 附 selftest 斷言兩端一致。
- **(c) 每軸預註冊單一配方一次定案**(buffer 單點、λ 單點、σ_target 單點、標籤配方先凍);禁掃參數、禁跑多變體挑好看(=敵③)。
- **凍結窗(≤2026-05-31)重試付 N 代價;G1-PIN(2026-06-30)後 live 累積 OOS=免費檢定力**——框架①>③的機械根據。
- 相對強度軸無 no-v3,但 h20_dead_no_shortcut 硬規有效:任何新方法不得繞道復活 H20。

---

## 五、分階段(Phase 2/3 補驗收;B-M6)

### Phase 1:誠實化+地基+首批候選(C-m2 改名;明拆兩籃——「誠實化籃:數字降=成功」與「候選籃:多半死=功能」)

| 項 | 內容 | 驗收 |
|---|---|---|
| 1-0 | P0 診斷包(8 項交付清單見 §3.2;本地零 usage、不入 ledger) | 診斷報告落 reports/ 含全部 8 項;P5/P6/P1 得到裁決依據;DSR 雙基線對帳+do-nothing 基準數字產出 |
| 1-1 | **trial_ledger recipe 遷移**(§4.3(b);拍板後最先動) | DDL 落地+32 列回填 'plain'+UNIQUE 擴+deflate/revalidate N 口徑同步+selftest 斷言兩端一致 |
| 1-2 | P2 turnover 權重法修正(誠實化籃) | selftest 更新;pred 加權隱形偏袒消除;headline 重算(recipe 鍵區分)誠實入檔;**risk_policy.turnover_budget(0.75 錨舊口徑)以新口徑重測後提重錨提案——政策值變更=判準相鄰,hugo 過目(A-m1)** |
| 1-3 | P1 buffer-zone(預註冊單點:進 10%/出 20%;候選籃) | 換手率下降、net SR_pp 與 DSR 較基準抬升、雙宇宙同向;入 ledger 一次(recipe=buf10/20) |
| 1-4 | P4 vol targeting+inverse-vol(誠實化+欠債籃;**G2 部分清償**,趨勢過濾另列;政策落 risk_policy) | verify 腳本比照 verify_risk_overlay;MaxDD/Calmar/DSR 分母通道驗證;誠實揭露 dormant 期;**經濟裁決基準維持等權單基準(G3/G4 未拍板前)** |
| 1-5 | **建構變更全鏈刷新收尾(A-M4/A-x5)** | 任何建構/成本口徑變更合入後:重跑 revalidate+deflate_headline_verdict→econ_verdict_rule/revalidation_verdict/model_registry 狀態同步(**verdict 變向=停下報 hugo**)→輸出契約 fail-closed DB trigger 仍成立+E[r]/機率產物同源複核;**全鏈完成前新建構不得接管 live serving** |
| 1-6 | D2 候選(通過「新角度差異」條款者,≤3 支;共線預診先行) | 走完 §4.1 全路徑;判決(含墓碑)入檔 |
| 1-7 | D3 候選(長窗計數 2-3 支;制度斷點標準化入配方) | 同上 |
| 1-8 | D1 前置工程:BalanceSheet 缺季重抓+CashFlows 去累計+金融股 60 日 lag | 缺季回補逐季覆蓋查核;去累計逐 type 對帳;release_lag 金融股分支+自測;**護欄(B-m4):API 放量逐次授權(#6/#24/#25)+與 audit_selfheal/daily_maintenance 對帳窗同 IP 互斥排程(HANDOFF 07-14 入檔)+FinMind Sponsor 訂閱有效為外部依賴條款** |
| 1-9 | **live OOS 承接管線(B-x4;①軸紅利制度化)** | live panel 續建節奏確認→run_revalidation_cycle.py(既存、季頻 panel-driven)排程歸屬明文→每季 DSR 隨 T 重算並入檔→live 期 trial 記帳口徑(live 期數不付凍結窗 N 代價之界線)預註冊 |

### Phase 2:資料軸主力+組合軸第二批

| 項 | 內容 | 驗收 |
|---|---|---|
| 2-1 | D1 六族全漏斗(最高期望戰役;附最小可測效應分析) | 每族:走完 §4.1 全路徑+判決入檔+墓碑追加;六族全滅亦為有效定論(「台股基本面複合異象不增量」入墓碑);D1 全程 ≤6 筆 ledger |
| 2-2 | D4-D7 選擇性推進(每輪 ≤2-3 候選;D8 視 §七-5 拍板結果) | 同 §4.1 全路徑條款;D4 之 short-interest 三表歸位判決入 reports |
| 2-3 | P6 tranche(前置雙條件過後;預註冊單點 tr3m) | 前置(a)(b)完成證明;SR_pp 通道(非 √T)增益、雙宇宙同向;入 ledger 一次 |
| 2-4 | P3 成本感知權重(吃 P2/P7 校準;λ 單點) | 相對「已含 P1 之基準」報增量(三通道合併上限);雙宇宙同向;入 ledger 一次 |
| 2-5 | P5 多 horizon 混合(僅當 P0 相關<0.9) | 擇一配方預註冊;入 ledger 一次;相關>0.9 之放棄留痕 |
| 2-6 | P7 逐股價差+執行時點(前置:成本 SSOT 化+防呆) | stock_effective_spread 建表(§七-9)+審計斷言(禁作特徵);entry-lag 敏感度入報告;per-stock cost 之 ledger 鍵表示法落地 |
| 2-7 | P8 容量約束+容量衰減報告 | 報告落 reports/;deflation 裁決補容量邊界條款 |
| backlog | Dividend 表修復(DROP+re-sync)後升中重評;7 支舊直寫 script 收斂 | 各自獨立驗收,不佔主線 |

### Phase 3:方法軸選擇性

| 項 | 內容 | 驗收 |
|---|---|---|
| 3-1 | M1 GBDT B4 收尾(≤6 config 預註冊) | 每 config 入 ledger(recipe 鍵);欠債了結報告;不因 H40 好看換 headline horizon |
| 3-2 | M2 風險調整標籤+M3 EMA(方法軸首選雙項) | 配方+裁決判準先凍再跑;M3 受三通道合併上限;各入 ledger 一次;輸了誠實入檔 |
| 3-3 | M4 TSFM embedding(≤2 筆 ledger 硬上限;三洩漏前置) | 權重截止揭露+provisional 標記規則落地;選維 recipe 鍵;死亡誠實入墓碑 |
| 3-4 | M5-M8 僅前項枯竭後議 | M7 需 snooping 防護全套;M8 維持評低;議前先報 hugo |

### 跨階段護欄

FinMind 重抓=放量,逐次授權(#6/#24/#26)+audit 互斥排程;長跑登記可見任務(#21);所有 commit 明示授權(#14);計畫變更判準=停下問(#19/#26);每軸單一配方紀律(§4.3)全程有效。

---

## 六、預期管理(誠實)

1. **大部分候選會死=功能非缺陷**。歷史基準率:五輪探索全淘汰;最好一輪 C3=1/3 存活;foreign_trust_div 證明「IC 增量全非負」也可死在經濟終關。
2. **成功定義=deflated 淨值改善,非 IC**。主 KPI:DSR(雙基線 0.407/75.6%→95%)、deflated 有效 Sharpe(0.2646 上移)、成本帶內 DSR 曲線、pit_broad 地板上移。非 KPI:IC、gross Sharpe、任何未過 deflation 之 headline。
3. **誠實化項預期數字微降**:P2/P4/P7/P8 把假樂觀換真地板——headline 微降是計畫成功的一種形態。
4. **機理估算≠承諾**:所引效果量皆機理/文獻估算,實際以工具實跑為準;本計畫不承諾任何點估計。
5. **最大單一風險**:②軸紀律失守(掃參數灌 N)自傷全體 DSR 地板——§4.3 單一配方+recipe 落鍵是計畫成立前提,非可選項。
6. **時間結構誠實**:同凍結窗上能擠的統計力有限;真正的確立之路=G1-PIN 後 live OOS 累積(1-9 承接),所有動作以「live 資料進來時已就位」為隱含期限觀。
7. **N 預算表(C-x2;上限制,入帳前逐筆問「資訊價值>全體 DSR 地板上移代價?」)**:

| Phase | 新增 trial 上限 | 構成 |
|---|---|---|
| 1 | ≤9 | P1 1、P4 1、P2 重算 1(recipe 區分)、D2 ≤3、D3 ≤3(僅走到終關者入帳;預診死不入、留痕) |
| 2 | ≤10 | D1 ≤6、P6 1、P3 1、P5 ≤1、P7 重算 1 |
| 3 | ≤10 | M1 ≤6、M2 1、M3 1、M4 ≤2 |

   機理量級:E[max z] 於 N=16→30 約 1.86→2.13(審查 C 估);**精確 SR_0 敏感度曲線=P0 以 deflation.py 實算(#9 不現編)**。
8. **KPI 位移誠實算術(C-x3)**:歷史存活效果量=ΔIC +0.002/ΔSharpe +0.05 級(gross_margin_pctile 單獨 H60 ΔIC +0.002)——單一候選存活對 deflated 0.26/DSR 的位移微小。**主要 KPI 通道排序=live OOS 時間紅利 > 誠實化 > 組合 SR_pp > 候選存活累積**,與①>②>③框架一致;拍板者應以此為期望值基準,不以「某候選大爆發」為預設。
9. **do-nothing 基準(C-x1)**:SR 不變下純靠 live T 累積,DSR 幾季自然過 95%——P0 實算交付;**一切凍結窗工作的邊際期望值皆與此免費基準相比較**,比不過的項目應主動降序或放棄。

---

## 七、拍板點清單(全部須 hugo;#19/#26 決策層)

1. **本計畫整體拍板**(#20;拍板後動工前另行執行前確認)。
2. **trial_ledger recipe 遷移 DDL**(附錄 A;schema 變更+N 口徑消費端連動)。
3. **KPI SSOT 宣告**:DSR 雙基線對帳(P0 交付)後,宣告單一 KPI 基線(建議=deflate_headline_verdict 口徑、以保守值敘事)。
4. **候選 productionize**:每一支全過漏斗之候選,寫入 feature_values 前逐支拍板。
5. **D8 分類回套通道**:接受(限快照期主證據+回套僅敏感度)或不接受(D8 順延 live 累積)。
6. **既有宇宙乾淨重掃**:建議結案不重掃;不採則列 Phase 3 後選擇項。
7. **decision-G3/G4**(另案,sop_master 既有拍板點):經濟終判基準是否擴為「等權+規則地板」雙基準;未拍板前一律等權單基準。
8. **§4.2 ΔSharpe +0.05 升格**:自 print 級判讀升格為預註冊明文閾值(值不變)。
9. **stock_effective_spread 建表**(P7;新表)。
10. **P2 之 risk_policy.turnover_budget 重錨**(政策值變更=判準相鄰)。
11. **D1 API 放量**:BalanceSheet 缺季重抓逐次授權(#6/#24)。

---

## 附錄 A:對應 table schema(#20 v1.39.0 (a);B-m1 補齊)

**原則:候選不落生產表;新 DDL 僅二——trial_ledger 遷移(拍板點 2)與 stock_effective_spread(拍板點 9)。**

### A.1 所讀/所寫既有表 schema(live 實查)

| 表 | 欄位(live) | 本計畫角色 |
|---|---|---|
| `feature_values` | panel_date date, stock_id varchar, feature varchar, value numeric;PK(panel_date,stock_id,feature) | **生產表,候選期全程唯讀**;僅 productionize 後由 feature 層寫入 |
| `feature_candidate_values` | panel_date date, stock_id varchar, feature varchar, value numeric(現 0 列) | **候選唯一寫入口**(fc.ensure_candidate_table/fc.FEATURE_TABLE;清除=fc.clear_candidates) |
| `trial_ledger` | trial_id bigint PK, run_at, model text, horizon int, top_frac float, weight text, feats_hash text, cost float, sample_since text, metric_name, metric_value, n_periods, seed, source, note;UNIQUE(model,horizon,top_frac,weight,feats_hash,cost,sample_since);現 32 列=ridge24+gbdt8 | N 記帳;**遷移見 A.2** |
| `econ_verdict_rule` | horizon int, verdict text, source_report, note, created_at | 1-5 全鏈刷新之同步對象 |
| `revalidation_verdict` | verdict_at, as_of_date, cell, universe, track, state, triggered_cond, metric_snapshot jsonb, baseline_ref, threshold_source, note | 同上 |
| `risk_policy` | horizon int, policy_key text, threshold float, action text, source_ref, note, updated_at;**現 6 列**:H60/H120 × dd_circuit(−0.20/−0.25 reduce_half)、max_position(0.10 cap)、turnover_budget(0.75 warn) | P1/P3/P4/P8 各政策落列 (horizon,policy_key);**相容裁決**:buffer/λ/σ_target/ADV ρ 各一新列(H60 起、H120 比照);turnover_budget 0.75 錨舊口徑→P2 後重錨(拍板點 10) |
| 各 raw 表(§3.1)+release_lag+core_universe_asof | — | D1-D8 讀端;as-of 欄逐表定錨(§2.4-2) |

P0 診斷:讀 trial artifacts+feature_values+DB → **只落 reports/,不落 DB、不入 ledger**。

### A.2 trial_ledger 遷移 DDL(拍板點 2;Phase 1-1)

```sql
ALTER TABLE trial_ledger ADD COLUMN recipe text NOT NULL DEFAULT 'plain';
COMMENT ON COLUMN trial_ledger.recipe IS
  '建構/標籤配方鍵(詞彙表=改善計畫 §4.3(b) 凍結;plain=無 overlay 現行建構;新詞=新預註冊)';
ALTER TABLE trial_ledger DROP CONSTRAINT trial_ledger_uq;
ALTER TABLE trial_ledger ADD CONSTRAINT trial_ledger_uq
  UNIQUE (model, horizon, top_frac, weight, feats_hash, cost, sample_since, recipe);
-- 既有 32 列由 DEFAULT 'plain' 自動回填;消費端(deflate_headline_verdict/revalidate)
-- N DISTINCT 口徑同步納 recipe(#12 兩處一起改),遷移 script selftest 斷言兩端一致。
```

### A.3 stock_effective_spread DDL(拍板點 9;P7,A-x2 補 COMMENT)

```sql
CREATE TABLE stock_effective_spread (
  stock_id      text    NOT NULL,
  date          date    NOT NULL,
  spread_bps_cs numeric,          -- Corwin-Schultz (2012) high-low 估計
  spread_bps_ar numeric,          -- Abdi-Ranaldo close-high-low 估計
  window_td     integer NOT NULL,
  PRIMARY KEY (stock_id, date)
);
COMMENT ON TABLE stock_effective_spread IS
  '執行成本估計(P7);來源=已在庫 TaiwanStockPrice OHLC;非 alpha 特徵、禁作特徵消費(審計斷言看守)';
COMMENT ON COLUMN stock_effective_spread.window_td IS
  '截至 date(含)之回看窗交易日數——as-of:估計僅用 ≤date 之 OHLC';
```

D1 之 CashFlows 去累計不建中間表(builder 內函式,#3);BalanceSheet 重抓落回原 raw 表。

## 附錄 B:對應 python 程式規畫(#20 v1.39.0 (b);B-M3 誠實化——判準零改動、驗證碼有新增)

| 檔 | 動作 | 職責/簽名要點 | 輸入→輸出 |
|---|---|---|---|
| `src/augur/evaluation/portfolio.py` | 改 | `_turnover` 改權重半和 `0.5*Σ\|w_t−w_{t−1}·drift\|`(P2);`build_long_portfolio(..., prev_ids=None, exit_frac=None)`(P1);`score'=pred_rank+λ·1{held}`(P3);`run_backtest` 加 tranche 模式(P6)+**cost 參數防呆(預設 0.0→改 fail-loud,B-m2)**;**COST_TW 常數單一住所落此(>10 支散落逐檔改引)**;與 predict_asof.py live 共用同一支(#12)→**任何改動觸發 1-5 全鏈刷新** | preds+prev_port→portfolio |
| `src/augur/execution/risk_control.py` | 改 | inverse-vol+`exposure_t=min(1, σ_target/σ_trailing)`(P4);政策讀 risk_policy;`turnover_check` 複用新 `_turnover` 口徑→連動重錨(拍板點 10) | trailing vol→weights/exposure |
| `scripts/diagnose_construction_baseline.py` | 新(唯讀) | P0 診斷包 8 項交付(§3.2 清單,含 deflation.py 實算 SR_0 敏感度+do-nothing 基準+DSR 雙基線對帳);無參數 graceful(#29a) | DB+artifacts→stdout+reports/ |
| `scripts/migrate_trial_ledger_recipe.py` | 新 | A.2 DDL+回填+`--dry-run`;selftest 斷言 UNIQUE 鍵與消費端 N DISTINCT 欄集一致 | DDL→trial_ledger |
| `scripts/verify_candidate_funnel.py` | 新 | **參數化通用漏斗 runner(B-M3 方案a)**:候選 registry 驅動(名稱+計算函式+as-of 欄宣告),跑 §4.1 (1)(3);判準常數 import 自既有工具(±0.002/HAC-t≥2/seed≥3)**零改動**;取代「每家族一支 verify_*」慣例(#29c 收斂);讀寫僅 staging | feature_candidate_values→stdout+reports/ |
| `src/augur/features/inst_flow_split.py` | 新 | D2:長表 name 維度→候選;**輸出=fc.FEATURE_TABLE(staging)**;`_table_covers` gate;進場前附「與死者角度差異」說明 | InstitutionalInvestorsBuySell→feature_candidate_values |
| `src/augur/features/price_limit_events.py` | 新 | D3:join Price、長窗計數、2015-06 斷點標準化;**輸出=staging** | PriceLimit+Price→feature_candidate_values |
| `src/augur/features/fundamental_composite.py` | 新 | D1 六族;內含 `decumulate_ytd()`(逐 type);release_lag gate;盈餘讀 FinancialStatements;**輸出=staging** | BalanceSheet+CashFlows+FinancialStatements→feature_candidate_values |
| `src/augur/features/release_lag.py` | 改 | 金融股 Q1/Q3 60 日分支(**D1∧P6 共同前置**);簽名收 stock_id→industry、穿線全消費者、逐檔驗口徑+自測 | — |
| `scripts/resync_balance_sheet_gaps.py` | 新 | D1 前置缺季重抓;一律經 ingestion/finmind.py 同一 fetch/三層防護(#24);放量須逐次授權+audit 互斥排程(B-m4) | FinMind API→raw 表 |
| `scripts/build_effective_spread.py` | 新 | P7:讀 TaiwanStockPrice→寫 stock_effective_spread;+entry-lag 敏感度模式(B-x5) | raw OHLC→新表 |
| `evaluation/label.py` | 改(Phase 3) | M2/M5 標籤配方(預註冊凍結後);配方名=recipe 詞彙表項 | — |
| `deflate_headline_verdict`/`revalidate` 消費端 | 改 | N DISTINCT 口徑納 recipe(與 A.2 同批,#12) | trial_ledger→verdict |
| 驗證鏈其餘 | reuse | run_economic_eval / verify_stability / verify_incremental_fair / deflate_cost_sensitivity / run_revalidation_cycle(1-9 排程歸屬)——**判準零改動** | — |

每支新檔守 #18(白話標頭+守原則 #+指令矩陣/自測 CLI)+#29(a)(d)(_bootstrap、個別可執行、graceful、實測)。

## 附錄 C:元件・端點(B-x7)

**端點=N/A**——本計畫為純批次/報告型(diagnose/verify/build scripts+DB 表+reports/),不新增任何 HTTP 端點或 UI 面;既有 advisor/admin 服務不動。唯一與 live serving 的接點=1-5 全鏈刷新閘(新建構通過前不接管 predict_asof 路徑)。

---

**證據索引**(定稿重核):reports/augur_lens_validation_20260627.md、augur_three_lens_campaign_summary_20260627.md、augur_feature_discovery_methodology_20260626.md §四、augur_prediction_deflation_verdict_20260708.md、augur_short_horizon_verdict_20260709.md(DSR 0.407)、tsfm_taiwan_benchmark_20260717.md、augur_field_correlation_20260627.md §D-F、augur_f3_model_plan_three_thoughts_20260612.md、augur_prediction_sop_master_20260706.md(G2 :192/G3G4 :165)、plan_timeliness_review_post_arena_20260717.md、direction_econ(_v2)_20260711;live code:portfolio.py/ranker.py/label.py/walkforward.py/metrics.py/deflation.py/risk_control.py/release_lag.py/panel.py/baseline.py/feature_candidate.py/macro_vintage.py/verify_economic_reexam.py/reexam_sparse_candidates.py;live DB:feature_values(35 特徵)、feature_candidate_values(0 列)、trial_ledger(32=ridge24+gbdt8;UNIQUE 七欄)、model_registry(15=RankRidge 9+方向軸 6)、econ_verdict_rule、direction_gate(21)、direction_arena_candidate(11)、revalidation_verdict、risk_policy(6 列)、dataset_catalog(97)、column_catalog(769)。
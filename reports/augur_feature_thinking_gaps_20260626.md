# augur 特徵思考盲點審查報告 — 2026-06-26

> **範圍**:對 augur「特徵」全鏈(程式 + 方法論報告 + 治權檔)做思考盲點審查——找出**思考不足、名實不符、方法論與實作落差、未驗證假設、違反自身紀律**之處。
> **判準**:一律以 augur **自身 doctrine**(原則精華 20 條 + 特徵發現方法論,已入憲 v1.10.0)為 bar,非泛泛 quant。
> **方法**:兩輪多鏡頭審查 + 對抗驗證 + DB 實證(見文末「審查方法與可追溯」)。
> **結果**:39 個確認盲點(第一輪 7 鏡頭 25 個 + 補跑 statistical-rigor 9 個 + 完整性 critic 5 個)。

---

## 0. 總體判斷:五個系統性盲點

augur 的特徵紀律在「程式碼層」遠比「結論層」紮實。最該強化的不是寫更多特徵,而是:

0. **可重現性/持久化失效(S1,最該先處理)**——支撐整個特徵計畫的 M1 `+0.132 / valuation 為 alpha 主源 / 371 as-of 核心` 結論,其對應 DB 狀態已被 22-feat 重建覆蓋、**今天無法從 DB 重現**,卻已被方法論報告以「實證已知」載入憲章。其餘統計議題(去相關 Eff-t、size-neutralize、FDR)都假設這些數字能先被重現。
1. **anti-leakage 多處靠巧合成立**——「panel 都在月底」使月營收/籌碼/集保的發布落後恰好不洩漏,缺顯式發布日 gate;且 `label` t+1 進場未處理漲跌停鎖死(有報價但不可成交)。
2. **方法論宣稱「特徵必相對化」vs 實作存 raw、結論建立在 raw 上**——母原則③要求橫斷面/產業/自身歷史相對化,valuation/chip 一層都沒做;「交給樹/橫斷面」是未驗證假設,且生產主力 Ridge 連分界都不學。
3. **已生產特徵缺「資料覆蓋/真零前提」與「離群值」之實證守護**——gov_bank 對整段不存在的表填 0(假零、通過完整度 gate＝自我欺騙);stale/凍結價 artifact(≈-25σ)未 winsorize 直入 Ridge。
4. **評估只到 rank IC,完全沒有經濟價值/成本**——無 MaxDD/Calmar/top-N/turnover/逐空頭;在 augur 自己的 #14 判準下,「alpha 是真的」目前**不成立**(IC 類被 #14 明文排除在經濟價值判定外)。

---

## 1. 🔴 根本性(雙確認、違反核心紀律或動搖現有結論)

### S1 — M1 headline 數字無法從現行 DB 重現(雙驗證者 HIGH;已入憲)
- **原則**:#15 誠實(可重現＝半年重跑一致,靈魂級成功定義)/ #12 SSOT
- **實證**(雙驗證者各自獨立 psql 坐實):
  - `feature_values` 只有 **22 特徵**——`pe_ratio/pb_ratio/dividend_yield/market_cap_log/price_to_10yr` 一列都沒有。
  - `core_universe` 是 **878 股**(`committed_at=2026-06-25 22:29`,F2c 前),非 headline 的 371。
  - `core_universe_asof` 表**不存在**(`relation does not exist`)。
  - 現行 878 宇宙重測最強單因子為 `price_to_252d_high +0.086`,材質與報告「cycle +0.088 / pe −0.081 / div +0.079」不同。
- **本質**:headline 是某次未持久化 stdout 快照,DB 狀態已被覆蓋;`augur_evaluation_M1_baseline` 全部結論 + `augur_feature_discovery_methodology`(§六,**已入憲 v1.10.0**)以「實證已知 alpha 主源」承載這批不可溯源數字。驗證者界定:程式仍在、**可重建**,故非三敵①假資料;病灶是「可重現/持久化」失效——「日後可重建」≠「現在可重現」。
- **強化**:重建並**持久化** 27-feat feature_values + core_universe_asof;把「valuation 為 alpha 主源 / as-of>pan-hist」從「實證已知」**降為「單次未持久化觀測、待重建驗證」**;評估產物落地時連同 `(panel_set, universe_id, feat_set)` 三元組存才可比(#12)。

### G2+G3 — `gov_bank_net_buy_60d` 假零(雙驗證者 HIGH;已落地生產)
- **原則**:#1 Source-Pure(算不出即缺列、不存 zero-fill)/ 三敵③自我欺騙
- **位置**:`src/augur/features/chip.py:136-139`;前提宣告於 `chip.py:19-26`
- **實證**:`TaiwanStockGovernmentBankBuySell` 表最早列才 **2021-07-01**;2014–2021/06 共 **9 個 panel** 該表零列,特徵卻對全 roster 寫 0.0(`zeros/total=1884/1884…2526/2526`,100% 全零)。
- **本質**:不是「無官股介入＝中性真零」,而是「**資料整段不存在被編碼成 0**」＝#1 明禁的 zero-fill;且因通過 `core_gate` 完整度關,讓這些股**看似更完整**＝教科書級自我欺騙。`chip.py` docstring 自稱「真零前提已實證」,但只驗了 `max(date)` 到 as-of,**漏驗 `min(date)` vs panel 起點**。
- **範圍精準**:只有 gov_bank 受害——SBL(2005)、Lending(2003)來源表都早於 panel 窗,其早期 0 是合法真零。
- **強化**:E 類真零前加 per-table 覆蓋 gate——`panel_date − window < min(表.date)` 時該特徵**缺列**(回 P 類)、不填 0、不入完整度 gate;重建受污染的 9 個 panel。

### G1 — `monthly_revenue_yoy` 發布日洩漏(HIGH/MEDIUM;靠月底 panel 巧合安全)
- **原則**:#8 Anti-Leakage(t 當下真看得到)/ 方法論「月營收→P-lag」鐵則
- **位置**:`src/augur/features/panel.py:41-44`(`_REVENUE_SQL`)、:123,131-133
- **實證**:`_REVENUE_SQL` 用 `date <= panel_date`,但 `TaiwanStockMonthRevenue.date` = **營收所屬月之月首日標籤**,非公告日;真公告約**次月 10 日**(create_time 佐證:date=2026-06-01→create_time=2026-06-10;全表 44086/44089 列 create_time>date,lag 集中 7-11 天)。
- **現況**:目前洩漏輕微(生產 panel 全月底,晚報者僅 ~0.04%),但**已餵進 M1 IC(+0.047)**,且**無任何顯式發布日防線**——panel 頻率一改即破。
- **驗證者關鍵修正**:**create_time 不可當 PIT 錨**(它是 augur 入庫時戳,90.7% 缺、歷史列回填於 2026,拿來 gate 會把歷史營收掏空)。正解＝**法定保守 lag**(營收所屬月 + 次月 10 日),並改用 `revenue_year/revenue_month` 直接配對(別依賴 date 偏移巧合)。

---

## 2. 🟡 重要(威脅結論可信度 / 潛在 footgun)

### 相對化「說了沒做」(G5/G12/G13/G19/G20 群)
方法論母原則③白紙黑字:「目標相對→特徵**必**相對化(橫斷面 rank/z、產業內 demean、自身歷史 percentile)」。但 `valuation.py`/`chip.py` 存的全是 **raw 絕對值**,特徵層相對化**零落地**。
- 「交給樹/橫斷面」是未驗證假設:樹學絕對閾值、不會把 raw 轉同日橫斷面座標;**生產主力是 Ridge(GBDT 全輸),Ridge 連分界都不學**→辯護在最佳模型上落空。實證 PER 跨產業 4×(建材 11.6 vs 電子 48.4)、跨年 2× regime drift。
- 單因子 rank IC 對單調變換不變→五鏡①**結構上看不到相對化缺口**,卻被當「raw 估值夠用」背書(#15 自欺)。
- 驗證者:此屬執行計畫階段1 已排 deferred,但**殘留**:M1「alpha 主源」claims 建立在帶已知跨產業/regime 混淆的 raw 特徵上、無 caveat;最廉價的「同日橫斷面 rank」是普世 mandate 卻每個出貨特徵都沒做。**強化**:跑相對化消融(raw vs +橫斷面 z vs +產業 demean,用現成 run_ladder/feature_diagnostics),驗證前別把「raw 夠用」當定論。⚠️ 順序前移屬決策層。

### G8 — Eff-t 用 iid √n、未校正 IC 序列自相關(雙確認 MEDIUM)
`metrics.py:80` `eff_t = mean/std×√n`,假設 IC 序列 iid。但季度 panel + H=60 重疊 label 窗 + 慢變價值因子→IC 正自相關→真有效自由度 ≪ 25→**Eff-t 6.13 與勝率 0.96 系統性高估**。報告列了 caveat 卻在標題用未校正數字下「決定性/極罕見」。**強化**:加 Newey-West/HAC 或 block-bootstrap 雙列,未校正前措辭降級。(「as-of 4/4 > pan-hist」單調比較對此 robust,核心方向不倒。)

### G14 — 完整度 gate ＝ size 精英,污染 in-universe IC(MEDIUM/low)
核心 878 股流動性中位數是非核心的 **~15 倍**;level 特徵 IC 可能部分是 size premium 的 in-universe 投影。as-of 只消時間維 survivorship,沒消「每個 t 的核心都是當時 size-elite」。**強化**:size-neutralize 後重算 IC,確認 pe/foreign/cycle 是否存活。

### G9 — 完整度 gate canonical-union 0-核心靜默失效(雙確認 MEDIUM)
`core_gate.py:64` `canonical_features` 取全 panel union;早期 panel(2007-2013)結構性沒有籌碼特徵→任何含早期 panel 的 `build_universe` 靜默回 ~0 核心。現在安全純因呼叫端剛好用 2014+ 窗,gate 本身無守護。**強化**:偵測「某 panel 全市場 0 覆蓋某 canonical 特徵」→ raise/log 揭露(#15 不靜默)。

### S2 — 經濟價值(#14)完全缺席(MEDIUM/low)
全 `src/augur` **0 個** MaxDD/Calmar/top-N/long-short/drawdown 實作(僅 `metrics.py:12` 一行註解)。「alpha 是真的」只靠 rank IC,而 #14 明文把 IC 類排除在經濟價值判定外;空頭期(2022)是否撐住、最大回撤多少全未測。**強化**:建 evaluation/portfolio 層(top-N/分位 long-short 淨值→MaxDD/Calmar/逐 2022 空頭、扣保守成本與容量),「可交易 alpha」結論改以 #14 指標佐證、IC 僅作前置排序力。(驗證者:報告自承 deferred M-3,但 §0「alpha 是真的」措辭易被讀成可交易 alpha。)

### S3 — in-universe rank IC 不可外推(MEDIUM/low)
IC 分母 = 精英核心 ~371-850 股內排序,非全市場 ~3000;命題(全市場相對強弱)與量測口徑不對齊,量級不可外推、可交易性未驗。**強化**:每處 IC 明標宇宙基數(「core-N 內排序」);補一條更寬宇宙(放鬆完整度、僅留 raw-price 可算者)的 IC 對照。

### S4 — E 類真零特徵橫斷面退化混入 IC 表(MEDIUM/low)
`gov_bank` 在 ~9-10 panel 全 0、零變異→`rank_ic` 回 None→只在「有事件」的 18-19 panel 算 `mean_ic`,卻與別人的 27 panel 同表並列、不標分母差(#15「沒比到≠比過且乾淨」)。**強化**:裁定表附 `n_panels` 與「退化 panel 比例」;E 類零變異 panel 記 IC=0(中性)而非 None-剔除。(驗證者:只有 gov_bank 退化、非全 E 類;Eff-t 已部分懲罰小 n。)

### C1 — 離群值/數值穩定性:價量 artifact 未 winsorize(critic,MEDIUM)
stale/凍結價 artifact(`stock_id=710533` `momentum_5d=-4.077537` ≈ -25σ、跨 5 個不相關 panel 六位小數完全相同→必為凍結價非真動能)直入矩陣;Ridge(StandardScaler)對極端值極敏感,係數可被高槓桿列拉動→威脅「B2 Ridge 最強」結論。`panel.py:91-93` 只做 isfinite,無 winsorize/clip。**強化**:每 panel 橫斷面 winsorize(1%/99% 或 MAD clip)或對 momentum 加 stale 偵測 sanity gate;查 price ingestion 有無凍結 close。(驗證者:該例股未進矩陣,但核心齊備股仍有 max 5.1σ;rank IC robust 但 Ridge 擬合不 robust。)

### C2 — 不規則 panel 節奏 vs 單一 embargo(critic,MEDIUM)
2007-2020 年度(252td 間距)+ 2021+ 季度(~63td)+ 末筆 2026-05-31 月底;`walkforward.embargo_panels_for` 用單一全局中位 gap 套全程。**強化**:embargo 改 per-fold 依該 test 與相鄰 train 之局部 gap 算,或分段各自 embargo。(驗證者:當前是 over-purge=安全但損早期樣本,非洩漏;屬潛在 bug,節奏一變即可能 under-purge 真洩漏。)

### C3 — t+1 進場未處理漲跌停鎖死(critic,MEDIUM)
`label.py:79-80` 只剔 close≤0;台股漲跌停**鎖死**有收盤價但買不到,動能/題材股最常 t+1 漲停→label 用不可成交價→高估可實現報酬＝「偷看未來」隱形變體。`TaiwanStockPrice` 有 `Trading_Volume` 欄可判零成交卻未用。**強化**:進場日加可成交 gate(`Trading_Volume>0`,低成本第一步);改進場日屬決策層。

### C4 — 跨 H 共用同一特徵集 + Ridge 共線塌縮(critic,MEDIUM)
不同持有期 alpha 來源應不同(短期動能 vs 長期估值),但 `run_ladder` 對所有 H 用同一 canonical 特徵 + 同一 `Ridge(alpha=1.0)`;共線群權重塌縮到 `cycle_position`,短 H 流動性/動能訊號被長 H 估值權重蓋掉。**強化**:per-H 特徵選擇/正交化,報 per-H 各特徵 IC 異號/異強。(驗證者:實跑只 H=20/60、差距溫和;屬執行層改善。)

### C5 — turnover/交易成本未進任何評估口徑(critic,MEDIUM)
IC 不含「實現排序的換手成本」;高 turnover 特徵(`volume_surge_5_60`/`momentum_5d`)在台股稅 0.15%+手續+滑價下淨值可能為負;「IC 極罕見」之經濟意義無法成立。**強化**:portfolio 層估每 panel rebalance turnover、套台股成本,報淨 IC/淨 Calmar;高 turnover 特徵懲罰或拉長 rebalance。

### G7 — valuation PER>0 排除虧損股(MEDIUM/low,latent)
`valuation.py:48` 虧損股 PER≤0 缺列;若 pe_ratio 成 gate 必備項,501/1965(25.5%)虧損股被結構性排除→獲利股 survivorship。虧損股正是相對強弱訊號最強端(轉機/景氣循環)。**強化**:pe_ratio 註冊為 conditional 豁免,或改 signed earnings-yield。(尚未 materialize,乾淨修補窗口。)

### G15 — conditional 豁免在 model 矩陣層被靜默作廢(MEDIUM/low,休眠)
`core_gate` 豁免金融股缺月營收→入核心,但 `baseline._panel_matrix:49` `if len(fv)==len(feats)` 又因缺欄剔除→豁免成 dead-letter。現 opt-in、實證 0 受害,但屬名實不一致(#12 口徑)。**強化**:`_panel_matrix` 對豁免特徵 industry-aware 缺欄處理,或對齊不豁免。

### G6 — walkforward embargo docstring vs 實作(**驗證者分歧**)
`walkforward.py:6` docstring 要求「embargo ≥ label 窗 + 特徵最大滯後」,但 `embargo_panels_for` 只算 `ceil(h/間距)`、無特徵滯後項。**兩驗證者意見相反**:一說特徵純後向使該要求對 train→test 方向非必要(改 docstring 即可);一說標準 purge(López de Prado)顧慮 train-label 與 test-feature 共用觀測,embargo 對 252d 長窗確實不足(改 `embargo=max(label, feat_lag)`)。**→ 需實證裁決**(跑雙設定看 IC 是否變動)。

---

## 3. 🟢 增強(潛在 / 技術債 / 名實不符 / 已合理 deferred)

| ID | 盲點 | 驗證後 | 一句話 + 強化 |
|---|---|---|---|
| G10 | 籌碼逐表公布時點未驗證 | M/low | 集保大戶比(週結算次週公布)有確定性落後;現月底 panel 安全;逐表 probe + 文件化公布時點 |
| G11 | NULL/缺列 vs 0 語意不一致 | M/low | 同「資料不存在」P 類缺列、E 類填 0;對窄覆蓋表加「是否在名單」伴生特徵 |
| G16 | 月營收 date 語意脆弱 | M/low | 與 G1 同根;引入非月底 panel 前補顯式公告日 gate |
| G17 | macro Tier A 跨時區 PIT 過度宣稱 | low | 美股數列在台股 panel 落後 1 日;未生產;修 docstring + 上線前 date<panel |
| G18 | PriceAdj 還原價回溯重算未文件化 | low | label 比值中性;**驗證者揪出更實 bug:price_to_10yr 分子后復權÷分母原始價均=量綱混亂** |
| G21 | macro/context 全缺席 | low | 模型 0 macro、無 regime 條件化;`macro.py` 宣告 31 series 僅 12 落地(名實不符) |
| G22 | `lending_fee_rate_mean_30d` 名實不符 | low | 實為「最近 100 筆≈154 日均」非 30 日;改名 `_100d` 或真窄到 30 日 |
| G23 | 月營收 YoY 配對靠 date 偏移巧合 | low | 改 `revenue_year/revenue_month` 直接配對 |
| G24 | `gov_bank [:60]` 死碼 | low | SQL 已 LIMIT 60;刪 `[:60]` + docstring 註明「60 交易日」 |
| G25 | as-of canonical 固定取全期 | low | 特徵集定義層 look-ahead;驗證者:效應為保守(縮早期核心)非 IC 高估;補 caveat |
| S5 | 無 multiple-testing/FDR 校正 | low | Meff≈15.8;五鏡合判+walk-forward 已部分守;加 BH-FDR + survive_fdr 旗標 |
| S6 | 單 seed 硬編 | low | docstring 宣稱不存在的 `seeds` 參數＝假宣稱;「GBDT 確定無增量」措辭軟化;補 ≥3 seed |
| S7 | 高共線歸因偏差 | low | 報告多在主題/群層歸因(OK);`threshold=0.9` 太高漏 0.77-0.88 群;歸因前群層級正交化 |
| S8 | Eff-t 常態 + 小異質 n | low/none | 併入 G8;改 Student-t(df=n-1)或 block-bootstrap p |
| S9 | volatility 跨 regime 拼接 | low | 現核心宇宙 0-4 例(全 2007-2011 IPO 稀疏);放寬宇宙前加時間跨度上界 |

---

## 4. 建議修復順序(考慮依賴)

1. **S1 先重建並持久化** 27-feat feature_values + core_universe_asof,或在治權檔明標「不可重現、待重建」——**否則下面的統計驗證都無從談起**。
2. **🔴 G2/G3 gov_bank 假零 + G1 月營收發布日 gate**(source-purity / anti-leakage 紅線;用法定 lag 非 create_time)。
3. **C3 漲跌停零成交 gate + C1 winsorize**——動搖「B2 Ridge 最強」與 label 真實性。
4. **S2/C5 建 portfolio 層**(top-N/MaxDD/Calmar/turnover/成本)——讓「alpha 真」能用 #14 立論。
5. 去相關 Eff-t(G8/S8)、size-neutralize IC(G14/S3)、相對化消融(§2 相對化群)、FDR(S5)、C2 per-fold embargo、C4 per-H 特徵。
6. 🟢 技術債(G18 復權口徑、G22/G24 命名/死碼、S6 假 seeds 宣稱、S7 共線 threshold)。

---

## 5. 審查方法與可追溯(#15)

- **第一輪**:7 批判鏡頭(anti-leakage / source-purity-truezero / relativization-gap / three-lens-coverage / statistical-rigor / implementation-vs-design / universe-survivorship)並行讀全特徵語料 → 44 候選 → 每候選 2 對抗驗證者(嚴格 doctrine + 反駁者,皆可 psql 實證)→ **25 確認**(19 雙否誤解剔除)。workflow run `wf_b476f26f-9c0`。
  - ⚠️ 第一輪 statistical-rigor 鏡頭驗證者多數撞 session 上限失敗(僅 G8 存活)。
- **補跑**:額度重置後重跑 statistical-rigor(10 候選→**9 確認**)+ 完整性 critic(8 候選→**5 確認**),同樣對抗驗證 + DB 實證。workflow run `wf_ce745d80-3ed`。
- **DB 實證基礎**:本機 PostgreSQL 17(2026-06-26 自 `augur_20260625.dump` 還原,84 表完整、`feature_values` 1.7M 列)。
- **誠實標註**:每個 gap 標 finder 嚴重度 vs 驗證者(調整後)嚴重度 vs 共識(雙確認/單確認);驗證者的下修、誤解修正、意見分歧(如 G6)如實保留。所有量化主張可 trace 回 psql / code:line / 報告段落。
- **未盡**:第一輪 critic 階段亦曾失敗、已於補跑補回;經濟價值/成本(S2/C5)為整片未建領域,本報告只指出缺席、未量化其對結論之影響(待 portfolio 層建成)。

---

## 6. 第三輪:特徵值運算層深挖(2026-06-27)

> 聚焦【特徵值本身的數學 / SQL / 邊界 / 實際 DB 數值】,刻意不重覆前兩輪結構性盲點。7 運算族群並行深讀 + psql 比對同股同日 raw vs adj close + 查除權息表。workflow run `wf_32b29759-c63` 部分完成後撞**週上限**(~25 候選的驗證者未跑)→ 以下 **4 項經雙驗證確認**、**3 項由主迴圈 psql 自驗坐實**,其餘候選列文末待重置後驗證。

> **🔄 2026-06-27 完整重跑(`wf_885a0708-465`)**:週上限重置後全新完整重跑 7 族群 + 對抗驗證 + 綜合 → **34 候選 / 24 確認(全為新運算盲點)**,專屬報告 **`reports/augur_feature_compute_blindspots_20260627.md`**(R1-R4 根本 / Y1-Y7 重要 / G1-G7 增強 / N1-N2 否定,含共識標記)。**最重磅 R1(雙 HIGH)**:`cycle_position_252d` 的 252 窗 min 被**停牌 close=0 佔位列污染為 lo=0** → 全庫 **28.2% 逐位元退化、訊號可完全反向**(與除權息正交、換還原價不解)→ 與 CG1-CG4 構成 headline 最強 alpha(+0.088 cycle/position)之**雙重正交威脅**。下方 CG1-CG4 為該輪部分結果,完整 24 項以新報告為準。

### 🔴 CG1 — 價量特徵全用「原始價」、label 用「還原價」→ 除權息污染最強 alpha(雙確認 HIGH)
- **原則**:#1 名實相符 + 方法論 §73 自我矛盾 + 三敵③(偽 alpha);(非 #8 洩漏——驗證者修正:用原始價非偷看未來)
- **位置**:`panel.py:35-39`(`_PRICE_SQL` 從 `TaiwanStockPrice` 原始價)、`:88,93,102-106`(momentum/cycle/position 之 c/hi/lo 皆原始 close)vs `label.py:21,63`(label 用 `TaiwanStockPriceAdj` 還原價)
- **實證**:同股同日(2026-05-31)股 1436(殖利率 8.45%、2025-07 配息 9.8 元):raw `price_to_252d_high`=0.355 vs adj=0.505(raw 252d-high 灌水 42%);raw `momentum_252d`=-1.030 vs adj=-0.679(0.35 log≈35 個百分點幻象跌幅);DB 存值與 raw 逐位元吻合 → 確認落地用原始價。族群層:2026-05-31 panel 約 **36% 股**於 252d 窗內除息;`adj−raw` 偏移與**殖利率 corr=+0.18**(label 端無此偏移)。
- **本質**:方法論 §73 明文「還原價 close → 動能 / 高低開收 → 真實波幅 / 區間位置」,實作卻用原始價 = intended-vs-implemented 直接矛盾;同管線 label 嚴守還原價、特徵卻用原始價 = **雙標**。報告稱 `cycle_position`/`price_to_252d_high`(+0.088,§六)為最強 alpha,但該偏移**與高股息正相關、label 端不存在** → 可能是與股息混淆的**偽 alpha**(非單調變換、會重排橫斷面 rank,故真威脅 +0.088)。
- **與 S1 雙重打擊**:S1 已證 +0.132 headline 不可重現;CG1 進一步證即使重建,最強 alpha 也須先做 raw-vs-adj 消融才能信。
- **修法(低成本)**:momentum / volatility / cycle / position / range 全族 c/hi/lo 改用 `TaiwanStockPriceAdj`(已含 max/min/close 欄,僅換表);與 label 同源;重建受污染 panel;M1 結論加 caveat;補 raw-vs-adj 消融 IC 確認 alpha 是否存活。

### 🔴 CG2 — momentum_5/20/60/120/252d 同上、除權息=幻象跌幅(雙確認 HIGH)
與 CG1 同根,獨立坐實:股 1436 `momentum_252d` raw=-1.030 vs adj=-0.679,「下跌」大半是配息除權非真動能;高股息股動能被系統性低估、長窗累積誤差最大。隨 CG1 一併改還原價。

### 🟡 CG3 — cycle_position_252d 假地板(雙驗證 real、low)
除息股被原始價灌水的 252d-high 壓到 `cycle=0`(全庫 5.7% 零值中含偽零)。隨 CG1 改還原價;修後重查零值群、加「cycle 觸 0/1 之 panel 比例」診斷揭露(#15 不靜默)。

### 🟡 CG4 — monthly_revenue_yoy 微基期 log 爆量未 winsorize(HIGH/MEDIUM)
`_compute_revenue_yoy`(`panel.py:47-70`)對微基期照算 `log(last/r12)`、無 magnitude floor 也無 clip(對比 chip f1 有 [-1,1]、margin 有 [0,10] 域界)。實證:股 2528@2014 基期 NT$3000→NT$16億 → `value=-13.21`(=**-17.8σ**);全特徵 `|value|>5`(=148× YoY)共 248 obs / 75 股,**其中 16 檔在 core_universe 會進模型矩陣**。raw 灌進 StandardScaler→Ridge,威脅「B2 Ridge 最強」robust 性(驗證者修正:rank IC 對單調變換不變,衝擊在 Ridge 係數擬合非 IC 計算;最嚴重例 2528 不在 core,與 C1 平行)。**修法**:微基期記缺列(#1「算不出即缺列」)或 per-panel 橫斷面 winsorize/MAD-clip;floor 用該股自身歷史中位數比例(#9 不硬編絕對額)。

### 主迴圈 psql 自驗坐實(3 項,未經對抗驗證但事實確認)
- **turnover_mean_20d = 成交「筆數」非週轉率**:`column_catalog` 證 `Trading_turnover=成交筆數`;特徵名「turnover」誤導為週轉率,實為原始計數均值(size proxy,大型股天然高)、未 log/未相對化,std=57266 極端右偏。
- **feature_values 混入 ~32 個指數/類股偽個股**:`TAIEX / TPEx / Electronic / Semiconductor / FinancialInsurance / Cement…` 被當個股算了 momentum/turnover(`turnover_mean_20d` 前 5 名全是指數:TAIEX 684 萬筆…)。`core_gate` 的 `stock_id ~ '^[0-9]'` 會擋掉它們入核心,但它們**仍在 feature_values**(浪費運算 + 任何直讀 feature_values 者的 footgun)。
- **停更股 stale 無時效上界**:`institutional` 等 `LIMIT 1`/最近窗特徵無 recency gate;股 1107/9104/2381 之 `TaiwanStockInstitutionalInvestorsBuySell` 停在 2012,若仍在 2026 panel 取值即 14 年 stale 偽裝成 as-of。

### 主迴圈 psql 續驗坐實(2026-06-27 補,候選升級為確認)
- **三大法人成分隨時間漂移(medium)**:`_INST_SQL` 的 `sum(buy)-sum(sell)` 盲加所有 `name`,但類別逐年增加——2012-05 起 3 類(`Dealer`合計/`Foreign_Investor`/`Investment_Trust`)→ 2014-12 拆 `Dealer_self`+`Dealer_Hedging`→ 2017-12 加 `Foreign_Dealer_Self`。分母 gross 成分跨時間不一致(早期 3 類 vs 近期 5 類)→ 特徵時間序列定義漂移、跨時不可直比(IC 評估又混用早晚期 panel)。**無同日「合計+拆分」雙計**(`intersect(Dealer, Dealer_self)` by (stock,date) = 0)→ 非雙重計算 bug。修法:固定成分(或合併後的單一 Dealer)、文件化改版。
- **institutional buy/sell = 股數非「總交額」(low)**:實證 2330 外資買 13,311,364(股數量級),docstring 稱「淨買/總交額(金額)」不精確;ratio 無量綱故數值影響小,修 docstring 即可。
- **gov_bank 只看淨額、丟 gross 參與強度(medium-low)**:`sign×log1p(|60日淨買金額|)`(`buy_amount/sell_amount`=元)。實證股 2408/2344/2454 之 60 日官股 gross 達 468B/298B/297B 元但 net 僅 −5.1B/−3.8B/−1.9B(<2% gross)→ log1p(|net|) 仍給 ~22 強訊號,卻無法區分「大額平衡參與」與「中額單向介入」;兩日反向大額互抵後 net≈0 又看似「無介入」。修法:另加 gross/參與度伴生特徵,或淨額除以 gross 正規化。
- **core_gate 流動性門檻查詢污染(low,新)**:`_select_core` 的 `percentile_cont(...) FROM feature_values WHERE feature='dollar_volume_log_20d'` **無 `^[0-9]`/ETF 過濾**(與主 gate 查詢不一致)→ 門檻在含 32 偽股+ETF 的母體上算(filter-then-compute 不一致)。實證 P25 影響小(14.742 vs 真股 14.732,偽股偏高端),但高 `--liquidity-pct` 時放大(偽股中位 22.95 vs 真股 16.46)。修法:percentile 查詢加同樣候選空間過濾。
- **澄清(假警報排除)**:(1) `revenue` 欄實證=**當月營收(千元)非累計** → YoY「當月 vs 去年同月」語意正確、無 bug;(2) sbl/lending 源表 2005-07 / 2003-11 早於 2007 panel 窗 → 其真零**合法**(表有資料、0=真無事件),**只有 gov_bank(表 2021-07)是假零**(G2/G3 範圍精準再確認)。

### 未驗證候選(週上限擋住驗證者,待 11pm 後補驗 — 品質未過對抗驗證)
finder 提出但未驗證,擇要(可能含誤判):volatility/range 視窗無 recency 下界、`range_mean_20d` 的 `.mean()` skipna 致除以變動分母、volatility std `ddof=1` 小樣本+人造 0 報酬、`margin_usage` 對禁買股缺列丟失強訊號、`top_holders_pct`「>100萬股」固定股數絕對切點跨股不可比、`lending_fee` 混三種 transaction_type 未量加權、金控月營收可為負不可橫斷面比、LIMIT 14 在缺月致偽缺列、raw 動能污染具 Q3 除權息季強季節性(40% vs Q1 9%)致跨 panel IC 不同口徑。

> **第三輪對 headline 的淨影響**:S1(不可重現)+ CG1/CG2(最強 alpha 建於除權息污染的原始價、與股息混淆)疊加 → **報告「+0.132 / cycle+position 為 alpha 主源」在「重建持久化 + 改還原價重算 + raw-vs-adj 消融」三者完成前,皆不可當定論**。CG1 修法成本極低(換表),應與 S1 重建一併執行。

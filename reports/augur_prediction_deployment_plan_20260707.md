# Augur 股市預測 — 部署層 + 持續再驗證 計畫書

**日期**:2026-07-07 ｜ **性質**:plan-first(憲章第六部;只計畫、不建、不 commit)｜ **HEAD**:`debe8cb`
**SSOT 邊界**:研究結論以 `reports/augur_prediction_stage{B,CD,D}_*.md` + `augur_prediction_sop_master_20260706.md` 為準;本文只把「上線 + 顧問呈現真預測 + 風控 + 持續再驗證」凝為可執行、可稽核之階段鏈。
**現況數字來源紀律(#15)**:本文所有 DB 現況數字皆**當次 live query**(pgenv),非引記憶;報告結論引自上列 SSOT。

---

## 0. 一頁摘要(30 秒)

研究 A'→B→C→D 已全過:H60/H120 long-only 扣成本淨 Sharpe ~1.2 勝基準、經濟價值(#14)成立。**部署層元件多數已存在且 #8-safe**,但要真正 live + 顧問呈現真預測 + 加風控 + 持續再驗證,仍有明確 gap。**完成度估計 ~55%**:

> **✅ 2026-07-08 階段 2 執行落地竣工(風控 + live 投組建構)**:風控層 `execution/risk_control.py` + `risk_policy` 表(H60/H120 STAGE D 閾值)**已建已 seed**;predict_asof **已建 top-decile 投組 + 三風控 overlay 全接線**(prev_ids 換手 live、`_deployed_dd_returns` DD熔斷 live〔#8 forward-窗-關閉 filter 兩向實證、off-by-one 修 `future[h]`〕、單標的 cap)。**驗收 `scripts/verify_risk_overlay.py`**:生產 −20% 閾 in-sample dormant 無害(0 觸發、風控後==原始、淨 Sharpe 仍勝基準);−10% 壓測證機制運作(觸 4/18、MaxDD −19.4%→−16.6%、Calmar 1.00→1.03、仍 PASS)。DD/換手現況 dormant(prediction_values 僅 1 期、forward 窗未實現),隨歷史自動啟動。**下欄「風控層完全不存在」「predict_asof 只出排序」已解決**。

- ✅ **已有可用**:predict_asof(as-of 排序 + **top-decile 投組 + 風控 overlay**、寫 prediction_values)、train_ranker(→ model_registry)、release_lag(#8 發布日 gate,**建於 feature build 時、架構正確**)、PredictionPayload(frozen 唯讀 + guard)、advisor 服務殼、setup_predict_role(已寫、**未 apply**)、DDL 兩表(已落地)、**風控層 risk_control.py + risk_policy(✅ 階段 2)**。
- ✅ **advisor 已接真實預測(2026-07-08 實查更正:D4 早已 wire、本 session 增強誠實地板)**:`build_prediction_payload` 讀 prediction_values(34 檔真 picks)+ revalidation_ledger(驗證標籤);serve_advisor 已 `picking_payload_fn=build_prediction_payload`、`picking_intent` 路由選股題 → 真預測。本 session 增強 caveat 接 harness 誠實地板(未過 deflation DSR 76%、廣宇宙 deflated 0.07、裁決 deploying_unestablished)+ 修過時 survivorship(下市≈0 閉環/incumbency −16%)。**運維 #7:advisor 服務須重啟載新 payload.py 才生效**。
- 🔴 **需補建**:STAGE D 首選模型 **H120 未訓練**(registry 僅 H60);**持續再驗證 harness 不存在**;`augur_predict` role **未建**(DB 隔離硬閘缺)。

**最大命門(#8)現狀**:release-lag gate 已在 feature build 時正確落地(期間型財報/月營收經 `release_lag`,日頻籌碼/估值以 `date<=panel` 保守含同日)。predict_asof 讀 `feature_values`,**繼承 build 時的 as-of 純度**——只要 build 正確,predict 即 #8-safe。**但目前無「決策日 T 不用任何 release>T 資料」的機械測試**,需補為驗收 gate(見 §7 P1 驗收)。

---

## 1. 目標 / 範圍 / 治權約束

### 1.1 目標
把已驗證之預測研究**上線為可持續運作的顧問產品**:
1. **live 預測服務**:決策日 → as-of 特徵(release-lag gated)→ 生產模型 → 排序 → **投組建構** → prediction_values。
2. **advisor 呈現真預測**:predict 產出 → PredictionPayload → advisor 三姿態 + guard,取代 example_payload。
3. **STAGE D 風控**:DD 熔斷 / 部位上限 / 換手預算,閾值全來自 STAGE D 實測。
4. **持續再驗證**:資料累積時自動重跑 B/C/D、追蹤 IC/經濟價值、消解 H120 近期 n=8 小樣本 caveat。

### 1.2 範圍界定(明文不做)
- **不下單、不動錢**:靈魂「系統建議、人決策——有紀律的顧問,不是自動駕駛」。風控層產出的是**建議部位/告警**,非自動執行。
- **不改研究判準**:模型組態、embargo 口徑、成本假設、經濟成功定義皆已由 SSOT 拍板;本文不重開。
- **不重造已有元件**:predict_asof / train_ranker / release_lag / payload / guard / 服務殼皆沿用,只接線/補缺。

### 1.3 治權約束(硬邊界)
| 約束 | 條號 | 落地機制 | 現狀 |
|---|---|---|---|
| **#8 release-lag 命門**:決策日 T 只用 release≤T 資料 | #8 | `release_lag` gate 於 feature build;predict 繼承 | ✅ 架構正確、⚠ 缺機械測試 |
| **survivorship 未閉環債 b** | #8 | `core_universe_asof` 實為當前存活名單(`core_gate.py` join 當前 roster) | 🔴 未閉環;上線須明標 caveat、以 `as-of IC ≤ pan-hist IC` 為代理 |
| **DB 隔離**:預測進程不得讀素養層 | #8 | `augur_predict` role REVOKE 素養層 62 表 + AST import_isolation 雙閘 | ⚠ role 已寫未建(live query 證實 `pg_roles` 無 `augur_predict`) |
| **系統建議、人決策** | 靈魂 | predict/風控只出建議清單、不自動下單 | ✅ predict_asof 已明載 |
| **clean-room** | #16 | 不參考 stock_backend | ✅ |
| **payload frozen 唯讀** | 憲章 v1.17 | `@dataclass(frozen=True)` + guard 數字白名單 | ✅ |

---

## 2. 元件 × 現況 × gap 表(逐元件實證)

判定圖例:🟢 已有可用 ｜ 🟡 需接線 ｜ 🔴 需補建

| 元件 | 檔案 | 現況(實證) | 判定 | gap |
|---|---|---|---|---|
| **as-of 排序出單** | `scripts/predict_asof.py` | 載 registry `latest(family,horizon,asof)` → `_asof_stocks` + `_panel_matrix` → `estimator.predict` → 排序 → 寫 `prediction_values`。feats_hash 口徑鎖防漂移。**只出 (rank,sid,score)** | 🟢/🟡 | **不建投組**:無 top_frac 選取、無權重、無風控。要接 §2c 風控 |
| **模型訓練** | `scripts/train_ranker.py` | fit RankRidge/RankGBDT → artifact + `registry.register`(git_sha + feats_hash 凍結、resume 冪等)。複用 baseline helper(零雙軌漂移) | 🟢 | **H120 未訓練**(見 registry) |
| **生產模型** | `src/augur/models/ranker.py` | RankRidge=StandardScaler+Ridge(α=1.0),刻意與 baseline B2_ridge 同組態 | 🟢 | 無(H120 = 同 code、換 `--horizon 120`) |
| **#8 發布日 gate** | `src/augur/features/release_lag.py` | 月營收→公告月15日;財報 Q1-3 +45、年報 +90。純日期算術 | 🟢 | 無(見 §3 命門專節) |
| **feature build** | `src/augur/features/panel.py` 等 | 月營收 gate(panel.py:147)、財報 gate(margin_cycle.py:44);籌碼/估值/法人 `date<=panel`(日頻 T+1 保守) | 🟢 | 增量 panel build(見 §2a) |
| **PredictionPayload** | `src/augur/advisor/payload.py` | frozen dataclass、`.numbers()` guard 白名單、source_ref 溯源。**`example_payload()` 為寫死示範**;`empty_payload()` 為一般問答空 payload | 🟢/🟡 | 缺「從 prediction_values 組真 payload」的 builder |
| **advisor 組裝 + guard** | `advise.py` / `guard.py` | payload 型別分派、數字 ∈ payload 白名單、引文逐字、未來洩漏閘、逆向閘。已支援 PredictionPayload 路徑(`else: guard()`) | 🟢 | 無(guard 已能吃真 PredictionPayload) |
| **advisor 服務** | `scripts/serve_advisor_openai.py` | `make_server(..., payload_fn=empty_payload, ...)`。**寫死 empty_payload**(serve:70) | 🟡 | 接 real payload_fn / 選股題路由 |
| **OpenAI 相容殼** | `src/augur/advisor/oai_compat.py` | `chat_completion(payload_fn=example_payload)`;每回合 `payload_fn()` 取 payload → advise() | 🟡 | payload_fn 需能依 query 回真 PredictionPayload |
| **DDL 兩表** | `scripts/migrate_prediction_ddl.py` | model_registry + prediction_values 已建(live 證實有列) | 🟢 | 無 |
| **DB 隔離 role** | `scripts/setup_predict_role.py` | 已寫、冪等、`--apply --confirm` 建。**live query:`augur_predict` role 不存在** | 🔴 | 須 apply + predict 進程改連此 role |
| **投組回測** | `src/augur/evaluation/portfolio.py` | `run_backtest`(top_frac 選取、equal/pred 權重、換手成本、short_borrow)——**離線回測用,非 live 出單路徑** | 🟢(參考) | live 投組建構須抽 top_frac/weight 邏輯供 §2a 複用(複用鐵律 #12,勿另寫一套) |
| **風控層** | (不存在) | — | 🔴 | 全新:DD 熔斷/部位上限/換手預算(見 §2c) |
| **持續再驗證** | (不存在;僅 `reconcile_audit.py` 對帳) | — | 🔴 | 全新:revalidate harness(見 §3-③) |

### DB 現況(2026-07-07 live query)
- `model_registry`:**1 列** — `RankRidge_H60_2026-05-31_seed42_ce62866bb62de38b`(H60、asof 2026-05-31、28 feats、35 panels、12034 train rows)。
- `prediction_values`:**344 列**(panel 2026-05-31、上述 H60 model)——predict_asof 已跑過一次。
- `feature_values`:35 panels、`2007-12-31 .. 2026-05-31`,**季底 cadence**(3/31·6/30·9/30·12/31)。
- `core_universe_asof`:28 as-of 日、`2014-12-31 .. 2026-05-31`、12394 列(最新 panel 344 股)。
- `pg_roles`:**無 `augur_predict`**。

---

## 3. #8 release-lag 命門專節(最大命門、重點著墨)

### 3.1 命門本質
財報/月營收的 `date` 是**資料期間/公告月、非精確公開日**——用 `date` 當 as-of gate 就是偷看未來。台灣法定公告期限給了保守上界:
- **月營收**:`date` 恒 = 資料月+1(DB 實證 474,246/474,246 列);release = 公告月 15 日(法定 10 + buffer)。
- **財報**:Q1/Q2/Q3 季底 +45 日、年報(Q4)季底 +90 日(次年 3/31)。

### 3.2 現狀:架構**正確**且已落地
gate **建在 feature build 時**,非 predict 時。實證:
- `panel.py:147-148`:月營收 YoY 只取 `release_lag.revenue_released(d, panel)` 為真者。
- `margin_cycle.py:44`:毛利循環相位只取 `release_lag.financial_released(dd, pdt)` 為真者。
- `chip.py` / `valuation.py` / `phase.py`:籌碼/PER/法人以 `date<=panel_date` gate——**這是正確的**:此類為**日頻盤後公布**(T+1、公布日≈資料日),`date<=panel` 含同日屬保守(chip.py:17 明載此設計、上線後待 probe 精確公布時刻)。

**因此 predict_asof 讀 `feature_values` 即繼承 build 時的 as-of 純度**:給定決策日 T,只要 T 的 panel 是用 release≤T 資料 build 的,predict 就是 #8-safe。這是「gate 一次、下游繼承」的正確設計,predict 端無需(也不應)重做 gate。

### 3.3 gap:缺「機械測試」證明命門守住
現狀是**架構論證正確**,但無自動化 gate 實證「決策日 T 的特徵不含任何 release>T 之資料」。上線前必補:
- **測試 T-1(注入型)**:取兩個相鄰決策日 T1<T2,對某股在 (T1,T2] 間有新財報公告(release∈(T1,T2])。斷言:T1 的 `gross_margin_pctile`/`monthly_revenue_yoy` **不反映**該新財報(用未公告前的值),T2 的**才反映**。若 T1 已反映 → 洩漏、build 有 bug。
- **測試 T-2(邊界型)**:對 release_date 落在 panel 當日 vs 前一日 vs 後一日的財報,斷言 `financial_released` / `revenue_released` 的布林正確(± 1 日邊界)。
- **測試 T-3(整合型)**:同一模型、同一股,對 asof=T 預測不得使用 asof=T+Δ 才可得的任何特徵值(以 feature_values 逐列比對 build provenance)。

此三測試列為 §7 各階段**必過驗收**(尤 P1)。

### 3.4 殘餘命門(標邊界、非本計畫解)
- **survivorship 債 b(🔴)**:`core_universe_asof` 名義 point-in-time,實為當前存活名單(`core_gate` join 當前 `TaiwanStockInfo`、無 as-of listing 維度)——所有 as-of IC 帶未量化樂觀偏誤。**上線 payload/顧問輸出須明標此 caveat**;閉環需 as-of listing 維度(SOP decision-D1,屬 universe 判準變更、決策層,**不在本計畫範圍**)。
- **FRED vintage**:總經因子若入模須 vintage/ALFRED(事後修訂洩漏);現生產特徵集為價量+籌碼+財報,總經未入模——上線暫不觸,但持續再驗證擴因子時須守。

---

## 4. ②a live 預測服務

**目標**:決策日 → prediction_values(排序)**+ 投組建議**(選取/權重/風控後之部位)。

### 4.1 現有可直接用
- predict_asof 的排序核心(載 registry → 特徵矩陣 → predict → 排序 → 寫 prediction_values)**已完整可用**。

### 4.2 需補
1. **增量 feature build**(🟡):新決策日 T(下一季底)到來時,先 `build_feature_panel.py --panels T` build 該 panel(前置:raw sync 到 T + release_lag 使 T 之財報已公告者才入)、再 `build_core_universe.py --asof` 建 T 的 as-of 名單。**這是既有 script、只需排程觸發**。
2. **H120 模型訓練**(🔴):`train_ranker.py --run --horizon 120`(STAGE D 首選)。**H60 已在 registry**;二者並存,predict 依 `--horizon` 選。
3. **投組建構層**(🔴,新):predict 排序後,套 STAGE D 組態選投組——
   - top_frac(STAGE D 用 top10%,predict 現印 top-N 但不落選取旗標)
   - 權重(equal 或 pred-rank;STAGE D 用 equal LO)
   - **複用鐵律**:選取/權重邏輯**抽自 `portfolio.py` 之 `run_backtest`**(勿另寫一套,否則 live≠回測雙軌漂移 #12)。建議 refactor `portfolio.py` 出一個 pure `select_and_weight(preds, top_frac, weight)` 供 backtest 與 live 共用。
4. **模型選擇(部署決策 2026-07-07 對齊)**:**部署主模型 = Ridge H60 LO**——依 revalidation_ledger 蘋果對蘋果**超額 alpha(netSharpe−基準)**:H60 兩樣本期皆正(2014起 **+0.435**、2021近期 **+0.327**;n 25/18 大樣本、現在即可定論);H120 全期風險調整較亮(Calmar 2.21、MaxDD −8.7%)**但近期(2021起)超額 alpha 歸零、跌破基準(−0.015)、n=8 小樣本未定論**。按靈魂「**經濟價值非 IC + 誠實不誇小樣本**」,取現在即可定論之穩健者 **H60 為部署主投組**;**H120 列追蹤候選**,由 D5 harness 追近期 n≥20 再議(屆時若 H120 近期 alpha 定論轉正即重新對齊——可逆)。二者皆 long-only(long-short 已淘汰、放空成本坐實不採)。現況 prediction_values:**H60 in_portfolio=34 檔 equal-weight(部署主投組)、H120=0(追蹤候選)**。

### 4.3 資料流
```
決策日 T (季底)
  → raw sync 到 T (full_market_sync;release_lag 使未公告財報不入)
  → build_feature_panel.py --panels T           [feature_values, #8-safe]
  → build_core_universe.py --asof               [core_universe_asof T 名單]
  → train_ranker.py --run --horizon 120 --asof T [model_registry;或用既有若特徵集未變]
  → predict_asof.py --run --horizon 120 --asof T [prediction_values 排序]
  → 投組建構 select_and_weight(top10%, equal)     [部位建議]
  → 風控層 (§2c)                                  [DD 熔斷/部位上限/換手 → 最終建議]
```

---

## 5. ②b advisor payload 整合

**目標**:advisor 呈現**真實預測**,取代 example_payload。

### 5.1 現有可直接用
- **guard 已能吃真 PredictionPayload**:`advise.py:81-82` 對非 KnowledgePayload 走 `guard()`,數字白名單 = `payload.numbers()`(picks 的 score/rank + validation 數值)。
- **服務殼、SSE、三姿態、逆向閘、出處閘**皆已運作。
- payload frozen + source_ref 溯源已具備。

### 5.2 需補
1. **real payload builder**(🔴,新):`build_prediction_payload(as_of, horizon, top_n)` — 從 `prediction_values` + `model_registry` 讀真預測,組 `PredictionPayload`:
   - `picks` = top-N `StockPick(symbol, rank, score, source_ref="prediction_values:panel=T,model=...")`
   - `validation` = 從 STAGE B/C/D 報告之**已凍結**驗證標籤(rank_ic、淨 Sharpe、note 含「alpha 僅 long 側」「n 小屬方向性」「survivorship 債 b 未閉環」誠實 caveat)。**validation 數值須 trace 回報告/DB,非記憶**(#15)。
2. **payload_fn 路由**(🟡):`serve_advisor_openai.py:70` 現寫死 `empty_payload`。改為**依 query 分派**:選股題(「該買什麼」「排序」「top 標的」)→ `build_prediction_payload`;一般/知識題 → `empty_payload`(維持現行去雜訊行為,精準度 §2.4 D-1)。分派可用既有 relevance/意圖判定,勿新造編排器(唯一出口仍 `advise()`)。
3. **三姿態呈現**:顧問對真 picks 以「系統建議、人決策」框架呈現——**不得**輸出「必漲/保證/該買」(guard `_FUTURE_LEAK` 已擋)、**不得**逆向翻轉(guard `_REVERSE` 已擋)。validation caveat(n 小、long 側、survivorship)須隨 picks 一併呈現(誠實 #15)。

### 5.3 命門
- payload frozen:顧問不可改一個數字(guard 白名單機械強制)——**已有**。
- validation 標籤**誠實**:必含 STAGE D 的限制(H120 近期 n=8、n 小屬方向性、survivorship 債 b)。**不得只報亮眼 Sharpe 而略 caveat**(headline 過度樂觀是 STAGE C/D 已記取的教訓)。

---

## 6. ②c STAGE D 風控層

**目標**:把 STAGE D 實測 DD 統計落地為部署層風控。**閾值全有據**(STAGE D §三 Ridge LO 實測):

| horizon | 最壞單期 | 最深回檔 | 最長水下 | 負期比例 |
|---|---|---|---|---|
| H60 | −8.3% | −13.9% | 5 期 | 28% |
| H120 | −8.7% | −8.7% | 2 期 | 14% |

### 6.1 風控規則(新建、閾值來自上表)
1. **DD 熔斷**:實現回檔觸 **H60 ~−15% / H120 ~−10%** → 建議**降倉**(非清倉;顧問建議、人決策)。閾值取實測 MaxDD 稍外緣(H60 −13.9%→−15%、H120 −8.7%→−10%),防正常波動誤觸。
2. **單標的部位上限**:top10% 投組內單股上限(如 equal-weight 下自然 = 1/N;pred-weight 下設 cap 防集中)。
3. **換手預算**:~65-71%/期(STAGE D 實測 avg_turnover 0.65)。超預算 → 告警(高換手侵蝕淨值)。
4. **負期連續告警**:連續 ≥N 期負報酬 → 告警(H60 負期比例 28%、H120 14%,連續 3 期屬尾部訊號)。

### 6.2 落地形式
- 風控**不自動執行**:產出**部位建議 + 告警旗標**,經 advisor 呈現給人。守「不是自動駕駛」。
- 風控狀態(當前回檔、水下期數、換手)可寫入一張 `risk_monitor` 表(供 advisor 讀、供再驗證追蹤)——**DDL 待階段設計**。
- 閾值為**操作值、不寫死於判準**(#9/#27):存 config,重覆實證後才調(STAGE D n 小 8-25、閾值屬方向性)。

### 6.3 命門
- 閾值 **n 小(8-25 期)**:STAGE D 明載抽樣誤差大、排名方向性非精確。風控閾值屬**保守起手**,持續再驗證(§3-③)資料累積後校準。**不得**把小樣本 DD 當精確保證。

---

## 7. ③ 持續再驗證 harness

**目標**:資料累積(新季底 panel)時自動重跑 B/C/D、追蹤 IC/經濟價值/風控,消解 H120 近期 n=8 小樣本 caveat。

### 7.1 現有可直接用
- STAGE B/C/D 的評估碼**全部存在**:`baseline.run_ladder`(IC 階梯 + HAC-t)、`portfolio.run_backtest`(經濟價值)、`walkforward.splits`(embargo 保證下界)。**再驗證 = 用新資料重跑這些、不重造評估邏輯**。

### 7.2 需補:`revalidate.py`(🔴,新)
1. **觸發**:新 panel 定案(新季底 as-of + label 實現)時,重跑:
   - **B 關**:`run_ladder` H{60,120} as-of → 追蹤 rank IC + HAC-t(gate |HAC-t|≥2)。
   - **C/D 關**:`run_backtest` Ridge LO H{60,120} top10% → 淨 Sharpe/MaxDD/Calmar,對比等權基準。
2. **追蹤 + 消解 caveat**:每次重跑記錄 n 的增長(H120 從 n=8/14 往上)、IC/Sharpe 時序。**消解 H120 近期小樣本**:當 2021 起 H120 LO 的 n 從 8 增至可定論規模(如 ≥15),判定近期優勢是否為真(現況 2021-H120 淨 Sharpe 0.792 ≈ 基準 0.807、不足以定論)。
3. **試驗數帳本(#15、SOP G7 blocker)**:重跑計入 `trial_ledger`(`count DISTINCT (model,top_frac,weight,feats_hash,cost,horizon)`)——deflation(DSR/deflated Sharpe)之 N 由 DB query 機械得出、**禁人手填**(手報低估 → Sharpe 少扣血、屬自欺向量)。
4. **判停**:若殘差 alpha 消失(C2:靈魂要 skill 非 beta)、或 IC 掉破 HAC-t≥2、或經濟價值輸基準 → **誠實判停告警**(#14/#15,判停是預期正常結局之一)。
5. **排程**:季頻(panel cadence)。用 harness 背景模式 / 一次性排程,**不自掛長喚醒鏈**(#28 省 usage)。本地計算零 usage(#28 本地優先)。

### 7.3 命門
- 再驗證**同口徑**:embargo(h+62td 逐折)、asof(#8)、cost 0.585%、H120 non-overlap 稀釋——與 SSOT 一致,勿放鬆(放鬆 = 樂觀洩漏)。
- 再驗證**自包含**:validate 自 re-fit、不回讀生產 artifact(雙軌獨立,憲章 L120-124)。

---

## 8. 分階段 + 每階段驗收準則

**執行前確認(#20)**:動工前確認本計畫①完整②內部一致③與 code 一致④可實作,有落差先修計畫。以下為建議階段序,**逐階段用戶過目再進下一**(#19)。

### 階段 D0 · DB 隔離硬閘(前置、破壞性須授權)
- **做**:`setup_predict_role.py --apply --confirm`(設 `DB_PREDICT_PASSWORD`);predict/train 進程改連 `augur_predict` role(config `DB_PARAMS_PREDICT`)。
- **驗收**:`has_table_privilege('augur_predict','philosophy_chunk','SELECT')`=false;`prediction_values`=true(可寫)。predict_asof 連 predict role 能跑通。
- **命門**:破壞性(建 role/改 GRANT)+ 跨機(role 不在 pg_dump、換機重跑)——**須用戶授權**(#6)。

### 階段 D1 · #8 命門機械測試(硬前提)
- **做**:實作 §3.3 測試 T-1/T-2/T-3(注入型 + 邊界型 + 整合型)。
- **驗收**(**必過、否則不進 D2**):
  - T-1:決策日 T1 的財報型特徵不反映 release∈(T1,T2] 的新財報。
  - T-2:`financial_released`/`revenue_released` 於 ±1 日邊界布林正確。
  - T-3:asof=T 預測不使用 asof>T 才可得之任何特徵值。
- **命門**:此為 anti-leakage 機制化,**#8 命門守住的唯一機械證據**。

### 階段 D2 · H120 模型 + live 投組建構
- **做**:(a) `train_ranker.py --run --horizon 120`;(b) refactor `portfolio.py` 出 `select_and_weight` pure fn;(c) predict_asof 接投組建構(top10% equal LO)。
- **驗收**:H120 model 入 registry(git_sha/feats_hash 凍結);live 投組選取與 `run_backtest` 同 panel 逐值等同(複用鐵律 #12 零漂移);dry-run 印投組建議。

### 階段 D3 · 風控層
- **做**:實作 §6 風控規則(DD 熔斷/部位上限/換手預算/連續負期);`risk_monitor` 表 DDL;閾值存 config。
- **驗收**:對 STAGE D 歷史序列回放,風控在 −15%(H60)/−10%(H120)正確觸降倉旗標;換手超 71% 告警;閾值可 config 調(不寫死判準)。

### 階段 D4 · advisor payload 整合
- **做**:`build_prediction_payload`(從 prediction_values/model_registry + 凍結 validation 標籤);`serve_advisor_openai` payload_fn 依 query 分派;重啟 advisor 服務載新碼(#7 常駐服務須重啟)。
- **驗收**:選股 query → advisor 呈現真 picks + validation caveat(含 survivorship 債 b、n 小);guard 數字白名單 = 真 payload.numbers();一般 query 仍走 empty_payload;guard 全閘過(數字/引文/未來/逆向/出處)。**實測**:真跑一則選股對話,確認數字 trace 回 prediction_values、caveat 呈現、未觸 guard fail。

### 階段 D5 · 持續再驗證 harness
- **做**:`revalidate.py`(重跑 B/C/D、trial_ledger、判停告警);季頻排程。
- **驗收**:對現有 panel 重跑,IC/經濟價值數字重現 SSOT(±抽樣);trial_ledger N 由 DB query 機械得出;判停條件可觸發(注入劣化 label 測試)。

### 階段序依賴
```
D0(隔離)─┬─→ D1(#8 測試)──→ D2(H120+投組)──→ D3(風控)──→ D4(advisor)
          └─→ (D5 再驗證可與 D3/D4 並行,只依賴 D2 之評估碼)
```

---

## 9. 命門 / 風險總表

| 命門/風險 | 嚴重度 | 落點階段 | 處置 |
|---|---|---|---|
| **#8 release-lag**:build 正確但缺機械測試 | 🔴 命門 | D1 | 三測試為硬 gate、不過不進 D2 |
| **survivorship 債 b**:as-of 名單實為存活名單 | 🔴 | (範圍外) | 上線明標 caveat、payload validation 含此、以 `as-of IC≤pan-hist IC` 為代理;閉環走 SOP decision-D1(決策層) |
| **augur_predict role 未建** | 🔴 | D0 | apply(須授權)+ predict 改連 |
| **H120 未訓練** | 🔴 | D2 | train_ranker --horizon 120 |
| **風控/再驗證不存在** | 🔴 | D3/D5 | 新建、閾值有據於 STAGE D 實測 |
| **H120 近期 n=8 小樣本** | ⚠ | D5 | 持續再驗證消解、資料累積才定論 |
| **風控閾值 n 小(8-25)** | ⚠ | D3 | 保守起手、config 可調、再驗證校準 |
| **雙軌漂移**(live 投組≠回測) | ⚠ | D2 | 複用鐵律 #12:抽 portfolio.py 共用 fn |
| **advisor headline 過度樂觀** | ⚠ | D4 | validation 必含 caveat(#15、STAGE C/D 教訓) |
| **常駐服務未重啟載新碼** | ⚠ | D4 | #7:改 advisor 碼後重啟服務再實測 |

---

## 10. 成功定義 + 誠實邊界

- **部署成功 ≠ 預測保證未來**:靈魂成功定義是**經濟價值**(已於 STAGE C/D 有界達成),部署是把它可持續運作;顧問輸出恒守「系統建議、人決策」。
- **誠實判停是正常結局**:持續再驗證若見 alpha 消失/IC 破 gate/輸基準 → 判停告警,非失敗掩蓋(#14/#15)。
- **資料誠實只保證「不是假兆」、不保證「有可交易價值」**:各階段成功 = 可稽核證明無洩漏(尤 #8),非證明有 alpha。
- **本計畫不改任何判準**:模型組態/embargo/成本/成功定義皆 SSOT 已拍板;有衝突以 SSOT 為準。

## 11. 複現 / 現況查證
```bash
cd /home/hugo/project/augur && source venv/bin/activate && source <PGENV>
# 現況查證(本文數字來源):
python scripts/predict_asof.py                          # 印矩陣、不預測
python scripts/train_ranker.py                          # 印矩陣
python scripts/setup_predict_role.py --dry-run          # role 分類盤點(唯讀)
python scripts/migrate_prediction_ddl.py --check        # DDL 驗證清單(唯讀)
psql -c "SELECT model_id,horizon,asof_snapshot FROM model_registry"
psql -c "SELECT rolname FROM pg_roles WHERE rolname='augur_predict'"  # 現為空=role 未建
```
```

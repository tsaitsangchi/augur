# Augur 股市預測整體做法 SOP 主計劃

**版本**：master v1.0 · **日期**：2026-07-06 · **性質**：plan-first 計劃（**只寫計劃、不實作**，遵憲章 v1.31-v1.33）
**作者軌跡**：五視角提案（資料層防洩漏／特徵建模方法論／經濟終判／誠實治理／12-PHASE 維運序）→ 本文合成
**成功定義（一句話）**：靈魂成功＝**經濟價值（扣真成本後可交易 alpha）非 IC**（#14）；「骨幹跑通 ≠ 預測有價值」。

---

## 0. 標頭：性質・關係・SSOT 邊界

### 0.1 本文性質
- **plan-first 計劃**：本文只規劃、不改任何 code、不放量 API、不查 live DB、不擅改治權判準。實作前須經人拍板（憲章 v1.31-33，plan-first）。
- **不重造**：本文**建立於既有兩份 SOP 之上、consolidate（合併）並改進之**，不重寫既有已拍板判準。
- **與既有拍板出入處一律標 `decision`**：不擅改，匯總於 §6 供人拍板。

### 0.2 與既有文件的關係
| 文件 | 角色 | 本文如何對待 |
|---|---|---|
| `reports/augur_prediction_sop_plan_20260705.md` | 既有 SOP 計劃（四鏡對抗審查、§14 八決策點、階段 A/A'/B/C/D） | **基座**：階段序、8 拍板點、3 處誠實債全繼承 |
| `reports/augur_stock_prediction_sop_20260705.md` | 既有端到端大 SOP | **基座**：端到端細節沿用 |
| `reports/augur_feature_discovery_methodology_20260626.md` §四 | 特徵發現方法論 SSOT | **引用不複述**：三鏡頭×四漏斗+提拔關卡+經濟價值收尾 |
| `HANDOFF.md` §4-5 | stage A 進度快照 + 誠實紅線 | **現況與債的來源** |

### 0.3 SSOT 邊界（本文不改寫、只引用）
- **治權判準 SSOT**：`docs/系統核心思想_v1.5.0.md`（靈魂）/ `docs/原則精華_v1.7.1.md` / `docs/系統架構大憲章_v1.35.0.md`。
- **方法論 SSOT**：`reports/augur_feature_discovery_methodology_20260626.md` §四。
- **as-of 完整性口徑 SSOT**：`reports/augur_asof_completeness_verification_20260624.md`。
- **本文只是「把上述凝為一條可執行、可稽核的階段鏈」**，任何與 SSOT 衝突處以 SSOT 為準。

### 0.4 現況數字的來源紀律（#15）
DB 正在 restore 不穩。本文**一切現況數字皆引自既有報告 / git / code，不查 live DB**。凡引用數字均標來源；未經本次 out-of-sample 重跑者一律標「未閉環／不可當定案」。

---

## 1. 系統目標與成功定義

### 1.1 預測什麼（靈魂 L28）
predict 標的 ＝ **橫斷面相對強弱 rank**（比誰相對強，非絕對漲跌幅、非單日神算）。產物＝每股分數/機率 → top-N 選股 + 可信度（walk-forward IC / Effective-t / 勝率）。H 可週/月/季多尺度。

### 1.2 成功定義（#14，唯一 success gate）
- **經濟價值非 IC**：靈魂成功以扣真成本後之 **CAGR / Sharpe / MaxDD / Calmar** 對比基準風險調整後勝出為準；**IC 降為中間診斷**（原則精華 #14 L116-119；憲章 feature 層 L103「IC 撐住 ≠ 可交易」）。
- **上線判準（實驗值 #27，標實驗中、不入憲）**（既有拍板 7）：net Sharpe ≥ 1.0 ∧ Calmar ≥ 0.5 ∧ MaxDD ≤ 25% ∧ 逐空頭子期（2015/2018/2020/2022）每段 net 不顯著劣於等權基準同期。
  - **⚠️ 樣本量誠實閘（繼承既有 stock SOP §228，見 §6 decision-C7）**：h=60 經濟回測僅 21 個非重疊 panel，按 regime 切 4 子期 → 每段 ~5 obs、`effective_t_hac` 內建 n<3→None、5-obs HAC-t 統計上無意義。故「**逐空頭子期不顯著劣**」在**補 h=20 增 panel 之前一律為探索性信號、不下強結論、不得當硬 pass/fail 閘**；補 h=20 後樣本足方升為判準。以下 §3-V4/V5、§7.2#5 同此註記。

### 1.3 誠實判停是預期的正常結局之一（#15）
台股橫斷面 alpha 本質微弱（rank IC 0.02-0.05 即實用）、經濟優先取徑最不寬容 → **很可能根本沒有扣真成本後存活的 alpha**。SOP 明訂：**過不了經濟終關即誠實判停、據實揭露、不宣稱成功、不補 placeholder 漂亮數字**。判停 ≠ 失敗；誠實記停項入 `reports/` 即為靈魂成功之一種。

---

## 2. 端到端管線總覽

```
raw ──► feature ──► universe ──► model ──► validate
 │         │           │            │          │
 └── 橫切：core（infra/schema）· audit（byte 對帳 #7 + 五鏡 #11 + 隔離稽核）· catalog · philosophy/advisor（零 import 進預測 7 package）
```

**層職責鐵律（憲章 L84）**：選股不算特徵、特徵不抓 API、驗證不讀訓練產物。

| 層 | 職責 | 守的敵人 | 硬邊界 |
|---|---|---|---|
| core | 路徑/DB/generic_schema/型別 SSOT/infra log DDL | ①（#2#3#5） | 不抓 API、不選股、不算特徵 |
| raw（ingestion） | 通用 ingester → API 回應 byte-equal 落 DB（無白名單 #3） | ①（#1#2#4#6#7#17#18） | 不算特徵、不選股；intraday 只存日級衍生 |
| feature | source-pure 算 panel，算不出→缺列（不 fake/不 zero-fill） | ①（#1#9）+②（#8 時點） | 不抓 API、不選股、公式禁 hardcoded 閾值 |
| universe | 核心＝全部 source-pure 完整股（無評分無排名上限） | ①（#1#10）+③（質>量） | 不算特徵、不訓練、不評分 |
| model | 訓練產 artifacts+registry（只吃 0 缺值核心） | ①+②（切分無洩漏 #8） | 不抓 API、不選股 |
| validate | 自包含 purged walk-forward → 可信度 + 經濟價值 | ②（purged #8）+③（#12-15） | **不讀 model 層 artifacts（雙軌獨立）** |
| 橫切 audit | DB↔API byte 對帳（#7）+ 訓練前五鏡（#11）+ 隔離 AST/GRANT | ①#7 + ③#11#15 | 唯讀、不改資料、不選股 |
| 橫切 philosophy/advisor | 假說來源 + 解讀素養層 | ①#1#16 + ③#14#15 | **零 import 進預測 7 package、不進預測管線、不取代真實資料** |

**兩軌關係（防漂移）**：`evaluation/*`（baseline/label/walkforward/portfolio/metrics/cross_section）＝**離線驗證軌**（自 train→predict、明訂不讀 models artifacts）；`models/*`+兩支 CLI＝**上線生產軌**（fit→artifact→prediction_values）。二軌靠**複用鐵律 #12**（models.RankRidge 與 `baseline.py:141-142` B2_ridge 逐值等同組態、全複用 `canonical_features/_fold_xy/_asof_stocks/_panel_matrix` helper）對齊，驗收含雙軌一致 CI。

---

## 3. 階段化 SOP（12-PHASE × A→A'→B→C→D，不可跳序）

**核心命題**：12-PHASE 是「資料供應鏈 → 骨幹」的**建置序**；A→A'→B→C→D 是「骨幹已通後 → 推到可交易 alpha 或誠實判停」的**驗證序**。二者對齊為**一條不可跳鏈**——A'/B/C 正是 PHASE9/11 audit gate 的落地載體，**非兩套流程**（本文主張，見 §6 decision-M1）。

> 圖例：✅=已建　🔜=下一棒　⏸=維運後置　🔴=critical 未閉環債

### PHASE 0-1 · 環境 + Infra bootstrap ✅（常備前置）
- **目標**：確認執行環境與基礎設施可跑，不帶半殘狀態進資料層。
- **輸入**：venv/.env/PostgreSQL role/db。
- **方法**：core schema bootstrap 建 infra log DDL（pipeline_execution_log/data_audit_log）；import smoke test（`python -c "import augur"`，CLAUDE #23）；scripts 個別可執行（#29 `_bootstrap` 自插 `src/`）。
- **anti-leakage**：N/A（基礎設施層）。
- **Audit Gate（可驗證）**：imports 全過 ∧ DDL 無誤 ∧ db.ping() OK。
- **產出**：可用 venv + infra log 兩表 + smoke pass 記錄。
- **人拍板**：無。 **Resume**：無狀態、可重跑。

### PHASE 2-4 · 資料供應鏈 sync ✅（as-of 2026-05-31 已定案，之後增量維運）
- **目標**：FinMind/FRED 全市場全史真兆落 PostgreSQL SSOT。
- **輸入**：FinMind token（sponsor）/ FRED api_key。
- **方法**：`full_market_sync.py` 串跑 seed 名冊（P2）→ FRED fetch（P2b）→ universe bootstrap 過渡名單（P3）→ 全史段 `sync.daily_datasets` 動態列舉 generic auto-schema 自動建表（P4，無白名單 #3）；增量走 `daily_maintenance.py` by-date。限速三層防護 `_pace/_quota_gate/QUOTA_COOLDOWN`（#24）、最小單位探測（#25）、長跑 watchdog+sentinel+resume（#22）。
- **anti-leakage**：FRED Tier B 數列須落地為 ALFRED **vintage**（非最新修訂值，`macro.py` vintage_map），否則巨集特徵偷看未來修訂。
- **Audit Gate**：各 raw 表 max(date) ≤ as_of ∧ 供應鏈完整度 PERFECT（逐表實證 max(date)；漏抓 vs 停更以 probe API「缺窗+有窗」判別）。**restore 中不查 live**，以既有報告 **84/84 passed**（`reports/augur_asof_completeness_verification_20260624.md`）為據。
- **產出**：84/84 raw 表全史 ~46GB PG（既有 committed 事實）。
- **人拍板**：as-of 值變更（治權參數，#19 停下問）。 **Resume**：DB-driven resume（#22）。

### PHASE 5 · Raw 對帳（byte-level，敵① attestation）✅
- **目標**：證 DB 落地值 ＝ API 真值，零幻像，把資料誠實鎖在骨幹之前。
- **方法**：`audit/reconcile.py` DB↔API byte-level 逐值比對（只驗 ≤as_of，#7）；帶公告時點欄的表（Dividend.AnnouncementDate / MonthRevenue.create_time / Shareholding.RecentlyDeclareDate）須確認**公告欄本身也 byte-equal 落地**（下游 release gate 的根據）；API 探測用最小單位（單股單日 #25）。
- **Audit Gate**：`value_mismatch=0 ∧ extra=0`；否則整鏈停、不放行 feature、修 writer code 重建（**不 hand-patch** #12）；attestation 產 `data_audit_log` 一列（#7）。
- **產出**：reconcile attestation（GoldPrice 型真漏抓已補齊、84/84 passed，既有報告）。
- **人拍板**：無。 **Resume**：唯讀、可重跑。

### PHASE 6-8 · feature / universe ✅（🔴 survivorship 為未閉環債 b）
- **目標**：算 source-pure 特徵面板 + 選 completeness-gate 完整核心股，產 point-in-time snapshot 供訓練。
- **方法**：
  - **feature build（P7）**：算 35 特徵入 `feature_values`（source-pure，算不出→缺列不 zero-fill #1；停牌 close≤0→log inf→缺列，承 core-universe v4 volatility 修正教訓）。**發布日 gate**（`release_lag.py`：revenue 公告月 15 日 / financial +45/+90 日；`panel.py:147-149` 月營收、`margin_cycle.py:44` 財報均已 gate）。公式**禁 hardcoded 知識閾值**（#9：八二 0.80/0.20、康波 40-60 年、theme keyword 分數禁入 feature；一律相對化＝橫斷面 rank/z、產業內 demean、自身歷史 percentile）。
  - **universe build（P6/P8）**：`core_gate._select_core`＝真股票代碼 ∧ 非 ETF ∧ 流動性下界（`dollar_volume_log_20d` 動態橫斷面 P25，#9 不硬編）∧ universal 全齊 ∧ conditional（金融保險月營收豁免 `--exempt-revenue-financial`）。`build_core_universe.py` completeness gate 為 P8 預設，`--asof` 產 point-in-time `core_universe_asof`。
- **anti-leakage**：發布日 gate 逐字（date=期間底非公開日，用 date 當 as-of 即偷看）；橫斷面相依交互量（如 `inter_fh_x_p10yr`）不入 `feature_values`、由 eval 層 `cross_section.augment` 在組好 panel 後動態 append 綁當前宇宙（只用該 panel 當下宇宙 z、不跨日）。
- **Audit Gate**：P6 raw 完整度 PERFECT；P7 面板落地；P8 核心股全面板 **0 缺值**（逐核心股×每 canonical feature 確認有值）；流動性閾值須為**動態百分位算出值非常數**（#9 稽核）。**【誠實紅線 gate】`as-of IC ≤ pan-hist IC`** 為驗收信號——as-of 高於即 survivorship 假象未清。
- **產出**：`feature_values`（35 特徵，`reports/M1_baseline_20260626.md` 記載口徑）+ `core_universe_asof` snapshot。
- **🔴 未閉環債 b（critical）**：`universe/core_gate.py:167` join 當前 roster `TaiwanStockInfo`（**無 as-of listing 維度**）、HAVING count 逐 panel 全齊 ＝ **實為倖存名單**；`core_universe_asof` 雖名 point-in-time 實為當前存活名單 → **所有 as-of IC 帶未量化樂觀偏誤**。閉環排 STAGE D。**未閉環前禁宣稱已消 survivorship**，以 `as-of IC ≤ pan-hist IC` 為唯一驗收代理。
- **人拍板**：見 §6 decision-D1（survivorship 消除法 A/B）。 **Resume**：DB-driven。

### STAGE A ≈ PHASE 10-11 · 模型骨幹端到端跑通 ✅【已 committed】
- **目標**：把「特徵→模型→as-of 預測→prediction_values」接通，產靈魂產品輸出口（橫斷面 rank→top-N），證管線機械可跑。
- **方法**（新建，全複用 baseline helper 防雙軌漂移 #12）：
  - `src/augur/models/ranker.py`：**RankRidge**（StandardScaler+Ridge alpha=1.0，刻意與 `baseline.py:141-142` B2_ridge 同組態）+ **RankGBDT**（LGBMRegressor n_estimators=200/lr=0.05/num_leaves=15/min_child_samples=30/subsample=0.8/colsample=0.8，與 `baseline.py:145-147` M1_gbdt 同參）。契約極薄 `fit(X,y_rank)→predict→ndarray(n,)`，SHAP 留 audit 不進此層。
  - `registry.py`：model_registry CRUD（register 冪等 upsert / latest ≤as_of / exists resume 跳過 / git_sha HEAD）。
  - `artifact.py`：joblib 存 estimator + 凍結 feats + feats_hash 口徑鎖（predict 拒載口徑不符 artifact）。
  - `scripts/train_ranker.py`：`_fold_xy(asof=True)`→fit→artifact→register，**H=252 於 `main()` 硬擋退出**（`:88`）。
  - `scripts/predict_asof.py`：latest→feats_hash 鎖→`_panel_matrix`→rank→寫 `prediction_values`（先 DELETE 同 panel+model 再 executemany INSERT）。
  - `scripts/migrate_prediction_ddl.py`：兩表 DDL——**model_registry**（model_id PK / family CHECK∈{RankRidge,RankGBDT} / horizon / train_span / asof_snapshot / feats_hash / seed / metrics jsonb / artifact_path / git_sha）+ **prediction_values**（PK=(panel_date,model_id,stock_id) / score / rank / FK→model_registry）。
- **anti-leakage**：label t+1 進場（`evaluation/label.py` 不重造）；scaler 統計凍進 artifact、predict 不重算；model 不得用晚於 as-of 訓練。
- **Audit Gate**：端到端跑通（as-of 2026-05-31 top1=2330、`prediction_values` **344 列**，HANDOFF §4 本機實查，**非照抄 memory 舊載 875**〔另機時點〕#15）∧ 雙軌一致 CI（`baseline.run_ladder` B2 與 `predict_asof` 對同 as-of/feats_hash/seed 產同 score）∧ 對抗反例（故意讓 train 讀晚於 as-of panel→被硬上界擋、報錯不靜默）。
- **產出**：【已 committed · tag `prediction-sop-stage-a-20260706` / commit `3069c72`】model_registry + prediction_values 兩表 + models 4 檔 + 兩支 CLI。
- **誠實定性**：**骨幹通 ≠ 預測有價值**，top-N 排序尚未驗證有預測力。接續點＝STAGE A'。
- **人拍板**：無（已 committed）。 **Resume**：registry exists 冪等跳過。

### STAGE A' 🔜（下一棒·硬前提）· 隔離稽核 + embargo 保證下界
- **目標**：把「隔離不變式」與「embargo 防洩漏」從**文字約定升為機制強制**；未建則 B/C 一切 IC/經濟數字之 honesty 須降級為「約定」。
- **輸入**：STAGE A 兩表 + 現 `walkforward.py`。
- **方法**：
  - ① 新建 `audit/import_isolation.py` **AST 稽核**（預測 7 package 零 import knowledge/philosophy/advisor、不 SELECT prediction_values 當特徵）+ prediction_values/model_registry **DB GRANT REVOKE 雙閘**，列建表前置 gate。
  - ② **embargo 改保證下界**：`walkforward.embargo_panels_for`（現 `:30` 用 median_cal×0.69 交易日**估**、非下界）→ 改以實際交易日曆逐折驗 min gap ≥ h + 特徵最大滯後（release lag 最大值年報 90 日 ≈ 62 交易日）；H=60 ≥ 5 交易日 buffer；H=252 禁入 gate。
- **anti-leakage**：此階段本身即 anti-leakage 的機制化。
- **Audit Gate（對抗反例義務）**：故意在 models 加 `import augur.knowledge` → AST 稽核須 **fail**（fail-closed）∧ DB GRANT 使 predict_role SELECT prediction_values 被拒 ∧ H=60 逐折 min gap ≥5、H=252 被 gate 擋報錯。**【債 c 閉環】** 此 gate 過方可撤回「隔離僅文字約定」之降級。
- **產出**：`import_isolation.py` + DB GRANT 遷移 + embargo 下界改造。
- **🔴 未閉環債 c**：現 `src/augur/audit/` 實查僅 feature_candidate/feature_diagnostics/field_correlation/reconcile 四檔、**無 import_isolation.py**（僅 `verify_code_reports.py` 做 py_compile）→ DDL COMMENT / models 標頭之「隔離不變式」目前**僅文字約定非機制**。閉環前 honesty 降級為「約定、稽核待建」，**禁稱機制強制**。
- **人拍板**：見 §6 decision-M3（A' 是否為 B 硬阻塞）。 **Resume**：純新建、可重跑。

### STAGE B ≈ PHASE 9 · 提拔三審（預測到底有沒有價值·第一道真檢驗）🔜
- **目標**：訓練/上線前，用 IC 診斷判定特徵集+模型是否有「去掉洩漏與 survivorship 後仍存在」的橫斷面預測力，或誠實判無。
- **輸入**：凍結特徵集 + `core_universe_asof` + STAGE A' 之 embargo 下界。
- **方法**：
  - **F0 候選入場券**（北極星三問 + 紀律閘，連測都不測）：①有真實 API 源（#1）②t 日當下真看得到（#8：估值無 P-lag/財報法定 lag/FRED vintage/事件以公告日錨/chip 同日含先保守 `date<panel_date`）③對橫斷面相對強弱有區分力假說。任一否即丟、source-traceable 記淘汰理由。
  - **F1 三鏡頭×四漏斗生成 + 相對化**（方法論 SSOT，引不複述）：三鏡頭旋轉 → 相對化落地 `feature_values`（生產）/ `feature_candidate_values`（audit staging，canonical_features 不看此表故 core 不受污染）。
  - **F2 五鏡 #11 存廢**（不得單一指標判生死、尤不得單看 gain）：①有號 IC + sign 穩定 ②共線群（volume~turnover 0.96 型）③leave-one-out 必要性 ④ensemble SHAP ⑤purged-CV。不顯影（SHAP≈0）且 ablation-safe **必移**。**+ sanity 負對照**：隨機打亂 label 後 IC 須 ≈0（仍顯著＝管線洩漏，整段停查因）。稽核由 audit 層做（唯讀、SHAP 不進 models）。
  - **F3 提拔關卡**（三審全過方入生產，方法論 §四漏斗 4）：**(a) as-of 口徑禁 pan-hist**（pan-hist 高估，實證 `inst_govbank_divergence` pan-hist Eff-t 2.53→as-of 1.67，方法論報告）；驗收＝`as-of IC ≤ pan-hist IC`。**(b) 去相關 HAC-t 綁死**：IC 顯著性一律用 `metrics.effective_t_hac`、**禁裸用 iid effective_t**（重疊窗高估、審查 G8）、|HAC-t| ≥ 2 方顯著。**(c) 多因子增量 + ≥3 seed**：候選加入現生產特徵集、run_ladder mean IC 須穩定正增量、Δ≤0 即冗餘必移。
- **anti-leakage**：purged walk-forward 必附 purged 口徑（單報 raw IC 視違規 #8）；test 永不回流調參；H=252 禁入。
- **Audit Gate**：特徵分診完成 ∧ |HAC-t|≥2 方顯著（iid 禁入提拔判定）∧ 隨機 label 負對照 IC≈0 ∧ **【核心驗收】`as-of IC ≤ pan-hist IC`**（高於＝survivorship 假象未清）∧ **headline +0.132 標「不可重現、禁當 alpha 錨」**。
- **產出**：五鏡診斷表 + 提拔通過/淘汰特徵集（凍結為入模集），寫 `reports/`。
- **🔴 未閉環債 a**：headline **+0.132 IC 不可重現**（存 committed `reports/M1_baseline_20260626.md:106` 但當前 DB 22-feat 重建覆蓋無法重現、係 iid Eff-t 未經 HAC 復驗）→ **禁當 alpha 錨**（既有 SOP 拍板 4）。閉環需 DB 重建 + HAC 重算 + 退市股補完方採信。
- **誠實判停口**：三鏡頭特徵同源共線，消融「無增量 vs 共線稀釋」不可完全分辨；此關過 **≠ 可交易**，只是通往 C。
- **人拍板**：見 §6 decision-B1/B2/B3/B4/B5。 **Resume**：候選狀態住 staging 表。

### STAGE C ≈ PHASE 11 · 經濟終判（靈魂唯一成功 gate·扣真成本 walk-forward 投組）🔜
- **目標**：以**經濟價值（非 IC）**裁決系統成功與否；不優即誠實判停、不宣稱成功。
- **輸入**：STAGE B 凍結入模集 + 生產模型。
- **方法**（`run_economic_eval.py` → `portfolio.run_backtest`，long-only top 分位）：
  - **V0 終判前置閘**（缺一即停）：(1) 提拔通行證（B 三審已過）(2) survivorship 標記閘（債 b 未消前掛 `survivorship_optimistic=true`、net 為樂觀上界）(3) headline 不錨閘（禁引 +0.132）(4) 成本非零閘（cost ≥ 0.00585；`portfolio.py:45` 預設 cost=0.0 **絕不可作終判**）(5) **deflation 閘（債 d）**：終判經濟數字須計 DSR/deflated Sharpe（**試驗數 N 一律由 `trial_ledger` DB query 機械得出——`count DISTINCT (model,top_frac,weight,feats_hash,cost,horizon)`、禁人手填報；12 僅為 headline 選型之下界，真 N 隨下游 ladder/多 seed/backtest 增長**、多重比較調整、單 seed 揭露），**未 deflate 之 headline Sharpe（現況 1.23）絕不可作終判**；**N 若係人手自報（非 `trial_ledger` query）視為未驗證、不放行 headline**（見 §6 decision-G7）。
  - **V1 淨值曲線**：`run_backtest(top_frac=0.2, long_short=False, cost=0.00585, asof=True)`；long-only 定調（long-short Sharpe 0.23 空方已死、台股平盤下不得放空券源不足結構不可執行）；成本套於**換手率**（基準亦計其換手成本，公平比）；gross/net 雙報（net 為主表）；H=20/60 主、H=5 次要、**H=252 禁入**；entry `close(t+1)` close-to-close 偏樂觀 → 以 t+1 開盤/VWAP 重跑取下界。
  - **V2 風險調整 vs 基準**：net CAGR/Sharpe/MaxDD/Calmar 四項，對比**等權基準**（既有拍板 7 之單基準口徑）**〔+ 規則地板雙基準：待 decision-G3/G4 拍板；未拍板前判停/上線基準維持既有拍板 7 之等權基準〕**（見 §3 G2），看 Δ 增量非絕對值；經濟數字須 deflated（DSR/deflated Sharpe，見 STAGE C-V5 誠實閘）後方採信；≥3 seed 取統計（#15）。
  - **V3 exposure 偽裝歸因**：size/beta 中性化揭殘差 alpha 截距；中性化後 alpha 消失＝記 `exposure_disguise=true`、非 skill。
  - **V4 穩健度**：逐空頭子期 2015/2018/2020/2022 每段 vs 同期基準——**⚠️ 21 panel 下每子期 ~5 obs、`effective_t_hac` n<3→None、5-obs HAC-t 無效 → 探索性不下強結論，補 h=20 增 panel 前不得當硬 pass/fail 閘**（樣本量閘見 §1.2、繼承既有 stock SOP §228，關係見 §6 decision-C7）；**容量/衝擊成本上界**（ADV 衝擊+spread+集中懲罰+借券費）重算小型股 net（固定 0.585% 對小型股偏樂觀、真成本 2-5%）。
  - **V5 終關 pass/fail + 誠實判停**：所有經濟數字須先過 **deflation（DSR / deflated Sharpe，計入試驗數 N——`N` 一律由 `trial_ledger` DB query 機械得出〔`count DISTINCT (model,top_frac,weight,feats_hash,cost,horizon)`〕、禁人手填報；12 僅為 headline 選型之下界〔12 選 1〕、真 N 隨下游 ladder/多 seed/backtest 增長、多重比較調整、單 seed 揭露）**、以 deflated 值判定，**未 deflate 之 headline Sharpe 禁作終判**（見 §5 誠實債 d）；**N 若係人手自報一律視為未驗證、不放行 headline**（見 §6 decision-G7）。PASS＝deflated net Sharpe≥1.0 ∧ Calmar≥0.5 ∧ MaxDD≤25% ∧ 風險調整後優基準〔等權基準；規則地板雙基準待 decision-G3/G4 拍板，未拍板前維持等權單基準〕 ∧ 殘差 alpha 顯著正 ∧ 容量後小型股 net 未崩 ∧ **〔逐空頭每段不顯著劣＝探索性信號，補 h=20 增 panel 前不當硬 pass/fail 條件、見 §1.2/V4〕**。前六條硬條件任一不達 → **FAIL＝誠實判停**，據實記樣態〔(a)IC 撐住但 net 不優＝「IC 撐住≠可交易」(b)alpha 僅 long 側/long-short 無效 (c)size 中性化後消＝exposure 偽裝 (d)成本升到容量 net 消＝非可交易 (e)空頭崩＝規則地板不可省，補 panel 前為探索性〕。
- **anti-leakage**：validate 自包含 re-fit、**不回讀 STAGE A 生產 artifact**（雙軌獨立，憲章 L120-124）。
- **Audit Gate**：V5 六硬條件（deflated Sharpe/Calmar/MaxDD/優基準/殘差 alpha 顯著正/容量後小型股未崩）全綠＝PASS（仍標樂觀債）；任一紅＝誠實判停。**經濟數字須 deflated 後方採信**（未 deflate 的 headline 禁作終判依據）。逐空頭子期在 h=20 增 panel 前為**探索性、不列入硬 pass/fail**（樣本量閘 §1.2）。**對抗反例**：cost=0 vs 0.585% net alpha 隨成本消失＝非可交易判停項；size 中性化後 alpha 消失＝exposure 偽裝。判準本身為**實驗值 #27 標實驗中、依實證調整、不入憲**。
- **產出**：經濟終判裁決書 `economic_verdict.md`（verdict PASS/STOP、**六硬條件逐項**〔deflated net Sharpe≥1.0 / Calmar≥0.5 / MaxDD≤25% / 風險調整後優基準 / 殘差 alpha 顯著正 / 容量後小型股 net 未崩，逐項具 pass/fail 與來源數字供稽核勾稽〕、逐空頭子期探索性信號欄（非硬 gate、樣本量閘 §1.2）、停項樣態、樂觀債清單、git_sha 半年重跑一致鍵），入 `reports/`（#16 命名）。
- **誠實風險**：**大概率 FAIL，且 FAIL 就是正確結論**、非缺陷。
- **人拍板**：見 §6 decision-C1..C6。 **Resume**：DB restore 穩定後方可實跑（見 §6 decision-M4）。

### STAGE D ⏸（維運後置·閉環四債殘餘 + 持續監看）
- **目標**：把四處未閉環債補到閉環（a/b/c 於此收尾；d 之 DSR/deflated Sharpe 計算於 STAGE C-V5 起、多 seed 統計殘餘於此收尾）、建容量/衝擊模型使小型股 net 可信、建監看使系統長期運作並半年重跑一致。
- **方法**：
  - ① **point-in-time roster 真消 survivorship**（改 `_select_core` join 帶 as-of listing-status + 完整度改滾動近窗，閉環債 b；路徑 A/B 見 §6 decision-D1）。
  - ② **容量/衝擊成本模型**（ADV 衝擊+bid-ask spread+集中懲罰+借券費）揭 0.585% 樂觀幅度。
  - ③ `monitor_prediction.py`（IC 衰變 + 逐空頭子期 + 半年重跑同 git_sha 一致 #15）。
  - ④ **chip 同日含 probe 5 表公布時刻**閉環（現保守 `date<panel_date` T+1 gate，拍板 6）。
  - ⑤ **headline +0.132 完整閉環**（DB 重建 + HAC 重算 + 退市補完，閉環債 a）。
  - ⑥ **經濟數字 deflation 收尾**（多 seed 統計 + DSR/deflated Sharpe；**試驗數 N 一律由 `trial_ledger` DB query 機械得出——`count DISTINCT (model,top_frac,weight,feats_hash,cost,horizon)`、禁人手填報；12 僅為 headline 選型下界、真 N 隨下游 ladder/多 seed/backtest 增長**、計入下游全部試驗，承 STAGE C-V5 起始計算，閉環債 d 之殘餘；見 §6 decision-G7；#11）。
  - **重訓 cadence ＝ 季度**（對齊 H=60、不日更，拍板 8）。
- **Audit Gate**：半年重跑同 git_sha 產同結果 ∧ **survivorship 補後 as-of IC 不升**（升即原倖存名單樂觀已量化）∧ 小型股 top-N 加容量衝擊後 net 未崩 ∧ 四債各自閉環驗收過（d 之 deflated Sharpe 起於 C-V5、多 seed 統計於此收尾）。
- **產出**：point-in-time roster + 容量/衝擊模型 + monitor CLI + chip probe 閉環；四債關閉記錄。
- **誠實風險（無技術解）**：退市股若 FinMind 源本身不全只能**部分消**、殘留樂觀無法完全量化；容量模型仍是估計、真可交易性須 paper-trading 逐步驗。
- **人拍板**：見 §6 decision-D1。 **Resume**：DB-driven。

### 橫切治理階段（與 A→D 並行，非另一條序）

- **G2 規則型風控地板優先（#13）**：在任何 regime 預測增強前，**先建不需預測之規則地板**（波動目標 vol target × 趨勢過濾，零預測、確定性可重現）；地板單獨跑 purged WF 逐空頭子期得防守基線 MaxDD/Calmar；regime 預測只當**可選增強**，須證 ΔMaxDD<0 ∧ ΔCalmar>0 否則標冗餘移除；**regime 預測絕不當主角**（靈魂 L116）。C 經濟終判基準列擴為「**等權 + 規則地板**」雙基準（見 §6 decision-G3）。
- **G3 可重現 + 隨機統計紀律（#15）**：所有 stochastic production metric ≥3 seed 取 min/median/max/mean（單次極值註明）；提拔增量 ≥3 seed Δ≤0 不提拔；Ridge alpha=1.0 固定 random_state、test 永不回流調參；monitor 半年重跑＝同 git_sha+feats_hash+seed 產同 score，不一致即記漂移；registry.metrics 每數字 trace 回程式輸出。

---

## 4. 三敵防護在每階段的落點

| 敵人 | 條號 | 落點階段 |
|---|---|---|
| ① 假資料（source-pure） | #1 #7 #9 #12 | PHASE5 byte 對帳 gate（value_mismatch=0）· feature 缺列不 zero-fill · universe 0 缺值 gate · 禁 hand-patch 重建 |
| ② 偷看未來（anti-leakage） | #8 | feature 發布日 gate · FRED vintage · label t+1 進場 · STAGE A' embargo 保證下界 · purged WF 必附 purged 口徑 · H=252 禁入 · 真消 survivorship（債 b） |
| ③ 自我欺騙（誠實） | #11 #13 #14 #15 | STAGE B 五鏡 + sanity 負對照 + HAC-t 綁死（非裸 iid）· STAGE C 經濟終判為唯一 success gate · 誠實判停準則 · ≥3 seed 統計 · 三來源 trace · 誠實債帳本 |

**橫切機制**：每 PHASE 一個 **fail-closed audit gate**（不過即整鏈停、不靜默降級）；每 gate 之過關判準只能是三來源之一（(a)程式輸出/(b)DB query/(c)API），禁「我以為過了」。三敵零容忍＝**憲法紅線、非試錯對象**（#19 L134-135）；試的是方法與參數，**絕不為 net 報酬放鬆資料誠實**。

---

## 5. 誠實紅線與四處未閉環債（明列為債、非既成 alpha）

> **誠實債帳本**（honesty ledger）：每筆綁「未閉環前禁宣稱 X」硬規則；任何報告/宣稱引用被綁數字而未附標籤 ＝ 違 #15 誠實紅線、退回。

| 債 ID | 描述 | 引用 | 閉環條件 | **未閉環前禁宣稱** | 閉環階段 |
|---|---|---|---|---|---|
| **a** | headline +0.132 IC 不可重現（iid Eff-t 未 HAC 復驗、當前 DB 22-feat 重建覆蓋） | `reports/M1_baseline_20260626.md:106` | DB 重建 + HAC 重算 + 退市補完 | 禁引 +0.132 當 alpha 錨；引用須附「不可重現、待閉環」標籤 | B（部分）→ D |
| **b** 🔴critical | survivorship 未真消：`core_gate.py:167` join 當前 roster 無 as-of listing 維度、HAVING count 逐 panel 全齊＝倖存名單 | `universe/core_gate.py:167`；HANDOFF §5 | point-in-time roster（上市/下市日）+ 完整度改滾動近窗 | 所有 as-of IC 標「survivorship 未消、樂觀上界」；以 `as-of IC ≤ pan-hist IC` 為驗收（高於＝假象、判停） | D |
| **c** | 隔離 AST 稽核未建：`audit/` 僅 4 檔無 `import_isolation.py`、僅 `verify_code_reports.py` 做 py_compile | 本次實查 `src/augur/audit/`；HANDOFF §5 | 建 AST 稽核 + DB GRANT REVOKE 雙閘 | 隔離「零 import」「prediction_values 禁回讀」降級表述為「約定、稽核待建」，禁稱機制強制 | A' |
| **d** | 經濟數字未 deflate：現況 net Sharpe **1.23** 係「12 選 1（試驗數 N≥12）之後、多重比較 deflation 之前、單 seed、僅比例成本 0.585% 口徑」，未經 DSR/deflated Sharpe 校正 → 樂觀上界。**✅ 2026-07-08 deflation 閘建成並實算(`trial_ledger` + `metrics.py` DSR + `scripts/deflate_headline_verdict.py`,Bailey-LdP,3 鏡對抗驗證 CONFIRM):headline H60 LO 2014 未過——DSR = 75.6%(N=16 保守)~ 89.5%(N=8),兩端皆 < 95%;deflated 年化有效 Sharpe ≈ 0.26~0.48(正但未達統計確立)。⚠舊記「~0.34 / 89.6% / N=8 96.9%」係年化 units bug、作廢。債 d 由「未建」→「已建已跑=FAIL、待 survivorship/多seed/成本 realism 偏誤消解後複跑」。SSOT=`reports/augur_prediction_deflation_verdict_20260708.md`** | 既有 stock SOP §22/§180（多重比較 deflation 強制註記）；§230（試驗數 N 機械化 blocker）；附錄現況表 | 計 DSR / deflated Sharpe（**試驗數 N 一律由 `trial_ledger` DB query 機械得出——`count DISTINCT (model,top_frac,weight,feats_hash,cost,horizon)`、禁人手填報；12 僅為 headline 選型之下界，真 N 隨下游 ladder/多 seed/backtest 增長**、計入下游全部試驗）+ 多重比較調整 + 多 seed（#11） | 任何引用 headline 經濟數字（Sharpe/CAGR/Calmar）者一律附「12 選 1、deflation 之前、單 seed、僅比例成本」標籤；未 deflate 之值禁作終判/上線依據；**N 若係人手自報（非 `trial_ledger` query）一律視為未驗證、不放行 headline**（見 §6 decision-G7） | C（V5 deflation）→ D |

**其他結構性殘留（無技術解、只能誠實標邊界）**：
- expanding 折 label 窗重疊使 IC 自相關，HAC 只**校正不消除**（|HAC-t|≥2 為必要非充分）。
- 三鏡頭特徵同源共線，消融「無增量 vs 共線稀釋」不可完全分辨。
- entry close-to-close 偏樂觀；容量/衝擊模型建成前小型股 net 是不可信上界；真可交易性最終須 paper-trading/實盤逐步驗。
- 完整度 gate 之「全史至 t 齊」本身即 survivorship 篩選器（偏向資料完美的老股），樣本選擇偏誤與 alpha 估計交纏，不可完全分辨。
- AST 字面稽核擋不住動態 SQL/間接讀，須 DB GRANT 才閉環；honesty 只能到「大幅提高洩漏成本」非「數學保證零洩漏」。

---

## 6. 決策層拍板清單（decision points 匯總）

> 既有 SOP §14 之 **8 拍板點已於 2026-07-05 拍板**（模型選型/horizon/survivorship 排序/headline 不錨/成本深度/chip gate/上線閾值/重訓 cadence），本文**繼承不重列**。下列為本合成新增或需再確認之 decision，皆待人拍板、不擅改。
>
> **✅ §6 拍板記錄（2026-07-06，用戶）**：**採納全部建議預設**。7 個 🔴 重項確認——**M3**=嚴格釘死（A' 未過不進 B）；**D1**=真消 survivorship 走 (A) point-in-time roster〔empirical 前提：待實證 FinMind 上市/下市日可得性；不可得則 (B) 滾動近窗齊當過渡並標債 b 未閉環〕；**C2**=殘差 alpha 消失即 STOP（靈魂要 skill 非 beta）；**C4**=survivorship 未消時僅得「條件性 PASS、待 roster 真消復驗」、不作上線依據；**C7**=繼承 §228 樣本量閘（補 h=20 前逐空頭子期為探索性、不當硬 gate）；**G5**=分級嚴謹容忍度（骨幹先通、誠實標債、漸進補閘）；**G7**=繼承 §230 `trial_ledger` N 機械化 blocker。其餘 M/D/B/C/G 採各自預設建議。→ 計畫解鎖為**可執行（A'→B→C→D 研究序）**；此序為**多階段研究、非跑腳本**，成功定義=經濟價值（#14），**含誠實判停之可能**（台股 alpha 微弱、很可能過不了經濟終關）。

### 架構序（M）
- **M1**：採納「12-PHASE 是建置序、A→D 是驗證序，二者對齊為單一不可跳鏈（A'/B/C 落地於 PHASE9/11 audit gate）」？（本文主張對齊為一鏈，避免兩套 gate 漂移）
- **M2**：本治理層（G2/G3/誠實債帳本/fail-closed gate 註冊表）作為既有 A→D 之**橫切層、不改階段序與 8 拍板**，僅新增誠實紀律機制？
- **M3**：A'（隔離稽核 + embargo 下界）未建前，是否**釘死「A' 未過不得進 B」**（嚴格不可跳）？或允許 B 先探索性跑、A' 並行補（較快但 B 首輪結論須標「隔離未閉環」）？
- **M4**：是否要求「DB restore 驗證通過（pg_restore -j4 + reconcile 抽樣）」作為進入 STAGE B/C **實跑**的隱性 PHASE 0.5 前置？

### 資料層防洩漏（D）
- **D1**：survivorship 消除法二選一（既有拍板 3「排階段 D」已定，需選具體路徑）——**(A)** 建 point-in-time roster 表（上市/下市日，依 FinMind 源可得性）；**(B)** 完整度改「滾動近窗齊」取代「全史至 t 齊」。二者對核心母體定義不同、動 `core_gate.py:167` 屬 universe 判準變更、決策層。
- **D2**：embargo 下界口徑——改實際交易日曆 min gap 逐折驗 ≥ h + 特徵最大滯後（年報 90 日 ≈62 交易日）；確認 H=60 之 buffer 是否足、H=252 維持禁入（工程校正、非治權變更，需確認採此取徑）。
- **D3**：發布日 gate 精確化——維持法定期限近似（release_lag +45/+90/15）vs 改用 API 自帶公告欄（AnnouncementDate/create_time〔待實證〕）逐股對齊？涉及 feature 時點口徑變更。
- **D4**：完整度 gate 之流動性 P25 地板 / conditional 金融保險豁免是否維持現值（v1.24.0），或擴豁免其他結構性缺特徵產業？動 universe 判準屬決策層。

### 特徵建模（B）
- **B1**：提拔關卡 |HAC-t|≥2 由「顯示」升為「綁死硬 gate」——現 `baseline.py:151` 只把 `effective_t_hac` 併入 summarize 顯示、未當提拔 gate。確認此為既有 §5(b) 之落實、非新增判準。
- **B2**：**sanity 負對照**（隨機打亂 label 後 IC≈0）納為 F2 五鏡稽核之強制前置 gate（打亂後仍顯著即整段停查洩漏）？既有 SOP §9 列「負結果誠實入檔」但未明訂為 gate；本文主張納為敵③自檢硬 gate。
- **B3**：`as-of IC ≤ pan-hist IC` 作為 survivorship 未消之驗收警燈——確認 point-in-time roster（D）閉環前所有 as-of IC 一律標樂觀偏誤、不宣稱已消 survivorship。
- **B4**：RankGBDT 上位判準——確認須「≥3 seed mean IC 正增量 **∧** 經濟終關同贏」**雙條件**（對齊拍板 1），非單看 IC，否則誠實記「非線性無增量」、Ridge 維持生產默認。
- **B5**：交互特徵（`cross_section.INTERACTIONS` 如 `inter_fh_x_p10yr`）換宇宙 ΔIC 轉負＝局部效應——確認維持「opt-in 限特定核心宇宙、不設生產預設、不外推擴展宇宙」政策。

### 經濟終判（C）
- **C1**：上線判準之「不顯著劣於」**顯著性檢定口徑**（t-test / bootstrap / 閾值 p？）與「MaxDD≤25%」是 hard-fail 或可與 Sharpe 權衡——現為定性，需拍板具體統計定義。
- **C2**：size/beta 中性化後殘差 alpha 消失時——判「整模型無經濟價值直接 STOP」還是「記 exposure 偽裝但保留為 factor-tilt 產品候選」？本文傾向前者（靈魂要 skill 非 beta）。
- **C3**：容量/衝擊成本模型的終判定位——既有拍板 5 排階段 D（後置），但本文認為它是「小型股 net 是否可信」的判定工具本身。**前移為 V4 必建**，還是接受 V5 先以固定 0.585% 出 PASS/STOP、容量模型後補校正？
- **C4**：survivorship 未消時可否宣稱 PASS——既有拍板 3 允許「先跑骨幹 + 明標未消債」；本文傾向：若在債 b 未消時得出 PASS，須**降級為「條件性 PASS、待 roster 真消復驗」**，不得作上線依據。
- **C5**：judged horizon 經濟主表範圍——H=20/60 主、H=5 次要、H=252 禁入（拍板 2）；既有理解顯示 H120>H60。是否將 **H=120 納入經濟終判主表**（須先驗 H=120 embargo 是否也觸結構洩漏如 H=252）？
- **C6**：entry 口徑敏感度作為 gate 還是揭露——開盤/VWAP 下界 net 若跌破 PASS 閾值，是 hard-fail STOP，還是僅報表揭露樂觀幅度、以 close-to-close 為主 PASS？
- **C7**（**與既有 stock SOP §228 樣本量閘之關係，需明拍**）：既有 stock SOP §228 明訂「h=60 僅 21 非重疊 panel、按 regime 切 4 子期→每段 ~5 obs、`effective_t_hac` n<3→None、5-obs HAC-t 無意義→ regime 子期一律標『探索性、不下強結論』、須先補 h=20 增 panel」。本主 SOP §1.2/§3-V4/V5/§7.2#5 之「逐空頭子期不顯著劣」是否**繼承**此樣本量閘（→ 補 h=20 前一律探索性、不當硬 pass/fail、不擅升為終判 gate），或**覆寫**為硬判準（若覆寫須先補足 panel 使樣本量成立、並 source-traceable 證 HAC-t 有效）？**本文預設繼承**（未拍板前不得將探索性信號升為終判 gate）；覆寫屬變更既有基座判準、決策層停下問（#19）。上位動作＝優先補 h=20 增 panel 使檢定樣本量成立。

### 治理與嚴謹容忍度（G）
- **G1**：誠實債帳本化——是否採納把四筆失真（a headline 不可重現 / b survivorship / c 隔離未機制化 / d 經濟數字未 deflate）從「報告警語」升為機讀帳本 + 綁禁宣稱硬規則（不改任何既有判準、僅提升強制度）？
- **G2**：fail-closed gate 一律硬停 vs 允許部分 gate「警告+人工放行」——嚴謹 vs 有產物張力之拍板點。
- **G3**：規則風控地板列為**骨幹必建**（A→D 主線）還是可選增強？且 C 經濟終判基準列擴為「等權 + 規則地板」雙基準——與既有 SOP §8（regime 感知列維運、未明訂地板為必建）之出入。
- **G4**：誠實判停時是否也對比「規則地板基準」——若「選股 alpha 不優於純規則地板」是否亦觸判停？（對拍板 7 之補強）
- **G5**：**嚴謹容忍度檔位**——全嚴（每 gate fail-closed + 雙基準判停，可能長期無上線產物）vs 分級（骨幹先通、誠實標債、漸進補閘）？既有執行序 A→A'→B→C→D 已隱含分級取向，本文建議明文化此檔位由人拍板。
- **G6**：上線閾值入憲時機（#27 重覆驗證再定論）——net Sharpe≥1.0 等現為實驗值，何時、憑幾次重覆實證寫入治權檔？或永久保持 operational 不入憲？
- **G7**（**採納既有 stock SOP §230「試驗數 N 機械化」blocker，需明拍**）：既有 stock SOP §230 明訂「N 靠自報跨 session 幾乎必然低報、與 guard 機械防線非自律矛盾 → **N 由 `trial_ledger` DB query 得出（`count DISTINCT (model,top_frac,weight,feats_hash,cost,horizon)`）、不由人/AI 填；人手填 N 一律視為未驗證、不放行 headline**」。本主 SOP §5 債 d 閉環條件、§3 STAGE C-V0(5)/V5 deflation 閘、STAGE D⑥ 之 deflation 收尾一律**繼承**此 blocker（`trial_ledger` 為 N 唯一合法來源、12 僅 headline 選型下界、真 N 隨下游 ladder/多 seed/backtest 增長）。確認採納此為敵③（#15 自我欺騙零容忍）之機讀硬 gate——**手報 N 低估真試驗數 → deflation 系統性做不夠、Sharpe 被少扣血**，屬 blocker 級自欺向量、非可試錯項；本文預設繼承（承既有基座 blocker、不擅改），覆寫或放寬屬變更既有基座判準、決策層停下問（#19）。此 decision 同時消解與既有 stock SOP §230 blocker 判準之表面衝突（本文由固定常數「N≥12」明確改述為「N 機械化、12 僅下界」）。（#15 誠實/自我欺騙零容忍；#10 可溯源；#1 三來源之一〔DB query〕；#12 不 hand-patch）

---

## 7. 風險與判停準則

### 7.1 最大失敗模式（誠實接受）
**V5 大概率 FAIL，而 FAIL 就是正確結論、不是缺陷。** 台股橫斷面 alpha 本質微弱（rank IC 0.02-0.05 即實用）、經濟優先取徑最不寬容 → 很可能根本沒有扣真成本（≥0.585%）後存活的 alpha。SOP 必須容許「整條鏈跑完結論是誠實判停」而非硬湊成功。

### 7.2 明文誠實判停準則（#14/#15，6 條觸發）
過 purged walk-forward 投組 net（扣 cost≥0.585%、**經 deflation 後**）對比**等權基準**〔+ 規則地板雙基準：待 decision-G3/G4 拍板；未拍板前判停基準維持既有拍板 7 之等權基準〕，達下列任一即**誠實判停、記停項、不宣稱成功、不補 placeholder**：
1. 風險調整後（Sharpe/Calmar/MaxDD）不優於基準 → 記「IC 撐住 ≠ 可交易」。
2. size/beta 中性化後殘差 alpha 消失/轉負 → 記「exposure 偽裝、非 skill」。
3. net alpha 隨 cost 0→0.585% 消失 → 記「非可交易」。
4. alpha 僅在 long 側 / long-short 無效（既有實證 long-short Sharpe 0.23）→ **據實揭露、不掩飾**。
5. 逐空頭子期任一段 net 顯著劣於基準同期 → 記「規則地板不可省」。**⚠️ 但 21 panel 下每子期 ~5 obs、`effective_t_hac` n<3→None、5-obs HAC-t 無效（繼承既有 stock SOP §228、見 §1.2/§6 decision-C7）→ 補 h=20 增 panel 前此條為探索性信號、不下強結論、不當硬判停觸發；補 panel 樣本足後方升為判停條件。**
6. 容量/衝擊模型後小型股 net 崩 → 揭 0.585% 樂觀幅度、記「小型股 net 上界不可信」。

**判停 ≠ 失敗**：誠實記停項入 `reports/` 即為靈魂 out-of-sample 誠實之成功。判準閾值屬決策層（拍板 7 實驗值），AI 只執行判定與據實回報、不擅調閾值。

### 7.3 結構性殘留風險（無技術解、只能標邊界）
見 §5 末段；核心：survivorship 部分消不完全量化、IC 自相關 HAC 只校正、共線消融不可完全分辨、容量真可交易性須實盤驗、AST 擋不住動態讀須 GRANT 閉環。**資料誠實只保證「不是假兆」、不保證「有可交易價值」**——SOP 各資料層階段之成功＝**可稽核地證明無洩漏**，非證明有 alpha。

### 7.4 DB restore 依賴（本任務期間紀律）
DB restore 中不穩：本文引用之現況數字（344 列 / 84 表 / 35 特徵 / +0.132）**全部引自既有報告與 git、未查 live DB**。restore 完成前，STAGE B/C 的「重跑驗證」類 gate 無法真跑；實測須等 DB 穩定（見 decision-M4）。

---

## 附錄 · 現況宣稱來源對照（#15 trace）

| 宣稱 | 來源 |
|---|---|
| stage A 兩表已落地、tag `prediction-sop-stage-a-20260706` / commit `3069c72` | 本次 `git tag` 實查 + HANDOFF §4 |
| `prediction_values` 344 列、top1=2330、as-of 2026-05-31 | HANDOFF §4（本機實查，非 memory 舊載 875） |
| `audit/` 僅 4 檔、無 `import_isolation.py`（債 c） | 本次 `ls src/augur/audit/` 實查 |
| models 4 檔 + 兩支 CLI + migrate_prediction_ddl | 本次 `ls` 實查 + 提供之 code 行號 |
| headline +0.132 不可重現（債 a） | `reports/M1_baseline_20260626.md:106` + HANDOFF §5 |
| survivorship 倖存名單（債 b） | `universe/core_gate.py:167` + HANDOFF §5 |
| 84/84 raw 表 as-of 完整 | `reports/augur_asof_completeness_verification_20260624.md` |
| 35 特徵 / H60 IC / net Sharpe **1.23**（**強制註記：12 選 1、多重比較 deflation 之前、單 seed、僅比例成本 0.585% 口徑**；deflated 後方採信、見 §5 誠實債 d） | 既有 stock SOP（標樂觀/未 deflate/不可重現、禁當定案） |
| 8 拍板點（2026-07-05） | `reports/augur_prediction_sop_plan_20260705.md` §16 |
| 三鏡頭×四漏斗+提拔關卡+經濟收尾 | `reports/augur_feature_discovery_methodology_20260626.md` §四（引不複述） |

**治權引用**：靈魂 `docs/系統核心思想_v1.5.0.md:28,116-119` / 原則精華 `docs/原則精華_v1.7.1.md:18-21,82-85,111-124,73-76` / 憲章 `docs/系統架構大憲章_v1.35.0.md:81-159,216-248,260-268`。

---

*本文為 plan-first 計劃。實作前經人拍板；碰治權判準變更/破壞性/API 放量/commit-push/真兆最終確認即停下問（#20/#26）。clean-room #16 零 stock_backend。*

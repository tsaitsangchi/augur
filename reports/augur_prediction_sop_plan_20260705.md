# augur → 股市預測整體做法 SOP 計劃(端到端骨幹 + 三敵誠實)

**日期**:2026-07-05　**性質**:整體系統計劃(plan-first §20;跨 ≥3 package + 架構 + 判準 = 高風險門檻 → 多視角級)
**產出法**:ultracode 多視角對抗審查 workflow(13 agents:Understand×4 → Design×3+評審 → 四鏡 Adversarial〔洩漏/自欺/假兆/工程〕→ Synthesize)
**狀態**:**待拍板**(§14 有 8 個決策點)。本報告僅規劃、**未寫 code、未放量 API、未碰治權判準**。
**選定取徑**:【經濟價值優先】為主軸,嫁接【穩健簡約】(Ridge alpha=1.0 固定、複用鐵律)與【量化嚴謹】(models 極薄契約、HAC gate)之精華。

> **靈魂對齊**:成功定義 = **經濟價值(可交易 alpha)非 IC**;IC 降為中間診斷。系統建議、人決策;有紀律的顧問,不是自動駕駛。三敵零容忍 = 憲法紅線、非試錯對象。

---

## 0. 摘要

把 augur 從「raw→feature→universe→eval 機具齊備、但中間模型骨幹全空」推進為可端到端輸出「**as-of 橫斷面相對強弱 rank → top-N 選股 + 可信度**」的股市預測 SOP。**唯一真動工 = 新建 `src/augur/models/` 薄封裝 + `train`/`predict` 兩支 CLI + 兩張產物表 + AST 隔離稽核;`evaluation/` 六模組全複用不重造。**

**四鏡對抗審查校正了 3 處 ground-truth 失真(誠實入計劃、不當既成事實)**:
- **(a) headline +0.132 不可重現**:存於 committed 報告 `M1_baseline_20260626.md:106` 但**當前 DB 無法重現**(22-feat 重建覆蓋)、且係 iid Eff-t 未經 HAC 復驗 → **禁當 alpha 錨**。
- **(b) survivorship 未真消**(critical):`core_gate.py:167` join 當前 roster `TaiwanStockInfo`(無 as-of listing 維度)、HAVING count 逐 panel 全齊 = **實為倖存名單** → survivorship 為**未建債**,所有 as-of IC 帶未量化樂觀。
- **(c) 隔離 AST 稽核不存在**:僅 `verify_code_reports.py` 做 py_compile,**無隔離稽核** → 聲稱「機制強制」前須先建。

## 1. 現況與缺口

**已建**:ingestion(84/84 表全史 as-of 2026-05-31、raw 46GB PostgreSQL SSOT)、features(35 特徵入 `feature_values`、`release_lag.py` 發布日 gate 已落地實證)、universe(`core_universe_asof` 快照表)、**evaluation 六模組全建為 SSOT**(`label.py` t+1 進場還原價 rank / `walkforward.py` purged split+embargo / `portfolio.py` 經濟回測 run_backtest / `metrics.py` rank_ic+effective_t_hac / `cross_section.py` / `baseline.py` B0/B1/B2/M1 階梯)、audit/catalog。

**缺口(做成「股市預測 SOP」的未建部分)**:
1. **`src/augur/models/` package 不存在**——「特徵→模型」層完全空白(已 `ls` 確認)。
2. **無 `scripts/train_*.py` / `scripts/predict_*.py`** 端到端入口。
3. 骨幹「模型訓練 + as-of 預測 + 回測出單」未接。

**實證校正的硬編/預設**:`portfolio.py:79`+`baseline.py:142` Ridge(alpha=1.0) 硬編、`portfolio.py:45` cost=0.0 預設、`walkforward.py:30` embargo 用 median×0.69 交易日**估(非下界)**、`core_gate.py:167` join 當前 roster 無 as-of listing 維度、無 AST 隔離稽核。

## 2. 預測標的定案

**台股核心宇宙(`core_universe_asof` 當日快照)個股之「未來 H 日橫斷面相對強弱 rank」**——非絕對漲跌、非股價點位(對齊靈魂「比誰相對強、非神算漲跌幅」)。

- **label 完全複用 `evaluation/label.py`**(SSOT、不重造):t 日 as-of 算特徵 → **t+1 進場**(`_entry_exit`:panel_date 之後首交易日,非交易日不漂 t+2)→ 持有 H 交易日 → 還原價 `PriceAdj log(close_exit/close_entry)` → 同 panel 內 `cross_sectional_rank` 轉 0-1 百分位;停牌/close≤0/湊不足 h+1 交易日 → 缺列(#1)。
- **主戰場 H=20/60**(月/季;H=60 與季度 panel 對齊、非重疊、基本面慢變使長 horizon IC 更穩);**H=5 次要**(雜訊高);**H=252 禁入提拔/經濟主表**——因 `embargo_panels_for` 對 H=252 算 embargo=4、實測 label 窗越 test panel 1 交易日 = **結構性洩漏**。
- **選 rank 而非絕對報酬**:天生 market-neutral、抗 regime 平移、直接對接 top-N 選股 = 靈魂產品形態。**成本不放 label**(污染橫斷面口徑)、放組合層。

## 3. 模型層設計(新建 `src/augur/models/`)

原則 = **薄、確定性、可解釋、零重造 evaluation、模型服務於成本後組合經濟**。

- **`ranker.py`**:`RankRidge`(生產默認)+ `RankGBDT`(挑戰者)。契約刻意極薄 = `fit(X, y_rank) → predict(X) → ndarray(n,)`(float、任意尺度,metrics/portfolio 只看序位)。**SHAP/可解釋明訂留 audit 層、不進 models**(防膨脹侵入 SSOT)。
- **`registry.py`**:`model_registry` 表 CRUD(#15 可重現、resume 帳本;須加並發/半寫保護)。
- **`artifact.py`**:joblib 序列化 fit 好的 sklearn pipeline + 凍結 feats 清單 + as-of 日(冪等 resume、離線=上線同一 artifact)。

**模型選型**:默認 = **B2 Ridge(StandardScaler+Ridge alpha=1.0 固定、不 nested-CV)**——**採複用鐵律**:必與 `baseline.py:142`/`portfolio.py:79` 內聯 fit 同一組態,否則製造「離線驗證≠上線預測」雙軌漂移(**拒取徑1 nested-CV 提議即因其破壞此一致性**)。理由:M1 實證 Ridge 4/4 勝 GBDT、35 特徵共線嚴重(volume~turnover 0.96)線性+L2 對症、係數可讀。**GBDT(RankGBDT、固定超參)= 挑戰者**,須 ≥3 seed mean IC 穩定正增量且經濟終關同贏才提拔,否則誠實記「非線性無增量」。**輸入** = canonical 35 特徵(每 panel 皆現、0 缺值)。**防過擬合**:單超參 Ridge、固定 random_state、test 永不回流。**隔離**:models 零 import knowledge/philosophy/advisor(由**新建 AST 稽核強制**、非約定)。

## 4. 端到端管線(逐階段 · as-of 凍結 · 誠實機制)

| 階段 | 做什麼 | as-of 凍結點 | 誠實機制 |
|---|---|---|---|
| **S0 as-of 凍結** | 固定 `as_of_date`、寫 `run_manifest`(as_of/feature_ver/universe_ver/model_id/git_sha/embargo 交易日數) | ①此後全鏈不讀晚於此日之列 | #15 可重現(凍結防重跑漂移、**不防當初就含同日洩漏**) |
| **S1 raw sync**(複用 full_market_sync) | FinMind/FRED 全史落 PG | 各表 max(date)≤as_of | 敵①:日級真兆皆抓、缺值不補 |
| **S2 對帳**(複用 reconcile_audit) | DB↔API byte-level | 只驗 ≤as_of | value_mismatch=0∧extra=0 才放行、否則整鏈停 |
| **S3 feature build**(複用 build_feature_panel+release_lag) | 35 特徵 source-pure | ②**發布日 gate**:月營收+15日/財報 Q1-3+45·Q4+90日/gross_margin 只計 released 季/FRED vintage | 敵①②:release_date>panel_date 不入(**最穩固處**);**未閉環**:chip 同日含須 probe |
| **S4 universe build**(複用+改 core_gate) | 完整度+流動性 P25、逐 panel 重算 | ③每 as_of 只用 ≤t panel | **實證校正**:現為倖存名單、survivorship 未建債、禁宣稱已消 |
| **S5 特徵 audit**(複用 run_feature_audit) | 五鏡 IC+共線+ablation+SHAP+purged-CV | as-of IC 不回填 | 敵③:SHAP≈0∧ablation-safe 必移;入模集在此凍結 |
| **S6 model train**(**新建 models+train_ranker.py**) | purged walk-forward 逐折 fit Ridge→artifact+registry | ④train 只用 test 之前剔 embargo;scaler 統計凍進 artifact | 敵②③:單超參防過擬合;resume-safe;離線=上線同組態 |
| **S7 predict**(**新建 predict_asof.py**) | 載 registry ≤as-of artifact+當日快照→top-N→`prediction_values` | ⑤只用 ≤as-of 特徵、model 不得用晚於 as-of 訓練 | 靈魂產品口;附可信度;**禁被預測 7 package 回讀當特徵** |
| **S8 經濟終判**(#14、複用 run_economic_eval+portfolio) | long-only top 分位、扣成本×換手、對比基準 | 非重疊再平衡、net 為主表 | **唯一 success gate**;**必修**:強制 cost≥0.00585+size/beta 中性化歸因 |
| **S9 monitor**(複用 run_evaluation+verify_stability) | IC 衰變+逐空頭子期+半年重跑一致 | 每快照 as-of 凍結留痕 | 敵③:≥3 seed 取統計;結果 source-traceable 入 reports/ |

## 5. 驗證機制

**purged walk-forward**(複用 `walkforward.splits`)expanding train + embargo,**test 永不回流調參**、Ridge alpha=1.0 固定不搜。
- **embargo 改保證下界**(採洩漏鏡 mitigation):現 `embargo_panels_for` 用 median×0.69 交易日**估**;改以實際交易日曆數 panel 間 distinct 交易日、**逐折用 min gap 驗 ≥ h + 特徵最大滯後**;H=60 至少 ≥5 交易日 buffer(現 embargo=1 僅~2-4 天);**H=252 禁入主表**。
- **提拔關卡套模型**(方法論 §四漏斗4 升維,三審全過方提拔):(a) **as-of 口徑**(禁 pan-hist,實證高估 Eff-t 2.53→1.67);(b) **去相關 HAC-t**——gate **綁死** `metrics.effective_t_hac`、**禁裸用 iid effective_t**(重疊窗高估、審查 G8)、|HAC-t|≥2 方顯著(**現 code 只「顯示」HAC 未當 gate、須綁死**);(c) **多因子增量 + ≥3 seed**(對生產集 mean IC 穩定正增量、Δ≤0 不提拔)。
- **經濟終關 #14**(唯一成功判準):net Sharpe/Calmar 優基準 + MaxDD 可控 + 逐空頭子期(2015/2018/2020/2022)不崩。
- **headline 復驗**(採自欺鏡 mitigation):M1 +0.132/Eff-t 6.13 **標「不可重現、未 HAC 復驗、禁當 alpha 錨」**,須先 DB 重建 + HAC 重算 + 退市股補完方採信。
- **共同樣本窗鐵則**:所有消融同一期間比(各表歷史深度不齊:官股 2021 起/財報 2012 起)。

## 6. 防洩漏機制(敵②逐項)

1. label **t+1 進場**(不用 t 當日未收盤價)、close≤0/缺價缺列;
2. **發布日 gate 逐字命中**(release_lag 已實證):release_date>panel_date 不入;
3. **embargo 保證下界**(實際交易日 min gap、H=60 ≥5 天、H=252 禁入);
4. 單報 raw IC 視違規、必附 purged 雙口徑(附差量化殘留重疊);
5. **core_universe_asof 逐 panel 重算**——**現況未閉環**,須改 `_select_core` join 帶 as-of listing-status + 完整度改滾動近窗真消 survivorship;未建前**標樂觀**;
6. scaler 統計凍進 artifact、predict 不重算;model 不得用晚於 as-of 訓練;
7. **chip 籌碼同日含**(`chip.py:17`)須 probe 5 表 API 盤後公布時刻閉環、未 probe 前標未閉環風險;
8. evaluation 雙軌**不讀 model artifact**(portfolio/baseline 內聯 re-fit)防污染;
9. **entry 口徑復驗**:`label.py` entry=close(t+1) 為 close-to-close 偏樂觀 → 以 t+1 開盤/VWAP 重跑敏感度下界。

## 7. 經濟價值驗證(靈魂終判)

`run_economic_eval.py → portfolio.run_backtest`:purged walk-forward、long-only top 分位、扣台股來回成本×換手、net CAGR/Sharpe/MaxDD/Calmar 對比等權基準、逐空頭子期。**long-only 定調**(long-short Sharpe 0.23、空方已死)。

**必修三處(否則「經濟優先」名不副實)**:
1. **成本誠實化**:`portfolio` 預設 cost=0.0 → 呼叫端強制 cost≥0.00585;且固定 0.585% 對小型股偏樂觀 → 標「樂觀下界、非可交易保證」;**容量/衝擊模型(ADV 衝擊+bid-ask spread+集中懲罰+借券費)列 models 前緊接必建項**(是終判工具本身)。
2. **beta 偽裝歸因**:benchmark 為等權 common 股 → long top20% 贏可能是 size/低價 beta 偽裝 → S8 新增對市值因子+市場 beta 回歸、揭殘差 alpha,中性化後消失即誠實記 exposure 非 skill。
3. **entry 口徑**:close-to-close 偏樂觀 → 開盤/VWAP 重跑敏感度。

判準 = 淨報酬×信任度×穩健度×風險綜合,**不裸追最高 net**。

## 8. 維運 SOP

- **重訓 cadence**:**季度**(對齊 H=60 與新 feature 落地);expanding 加最新 panel;不日更。
- **一次完整預測**:①凍結 as_of 寫 manifest → ②raw 增量+對帳過 → ③feature+universe 快照就緒 → ④特徵 audit 過、集凍結 → ⑤`train_ranker.py` purged WF fit → ⑥`predict_asof.py` top-N 寫 `prediction_values` → ⑦附可信度+經濟 headline(標成本下界) → ⑧**出單只給人參考、系統不下單不動錢(扣扳機是人)**。
- **regime 感知**:不做 regime 預測當主角(紅線);防守走規則型風控地板(波動目標×趨勢);經濟報告逐空頭子期拆分。
- **resume-safe**:raw/feature/universe DB-driven 冪等;train/predict artifact 寫 registry、中斷從最後 panel 續;registry 加並發/半寫/孤兒清理;配額近上限即停(#24/#28)。
- **Claude usage**:全鏈本地零 usage、背景長跑不輪詢(#28)。

## 9. 三敵誠實保證(機制強制、非模型自律)

- **①假資料**:每入模值必為 API 真值經數學轉換、算不出缺列不補;S2 reconcile byte-level + S3 source-pure + S4 completeness 三道機制;models 只吃完整 core 股;E 類真零須源表完整至 as-of 否則缺列。
- **②偷看未來**:label t+1、發布日 gate 逐字(已實證)、embargo 保證下界、core_universe(survivorship 未閉環須補)、FRED vintage、chip 須 probe;單報 raw IC 違規。
- **③自我欺騙**:test 永不回流、HAC-t gate 綁死(禁裸用 iid)、≥3 seed 取統計、as-of 非 pan-hist、雙軌不讀 artifact、提拔三關全過、負結果誠實入檔、git_sha 凍結保半年重跑一致。
- **邊界不可逾**:試的是方法/參數,**絕不為 net 報酬放鬆資料誠實**;survivorship/headline 重現/成本模型三未閉環須誠實標債。

## 10. 元件表(含新表 DDL)

| 檔 | 角色 | why |
|---|---|---|
| `src/augur/models/__init__.py`(新) | package 入口 | 唯一核心缺口 |
| `src/augur/models/ranker.py`(新) | RankRidge(默認)+RankGBDT(挑戰者)`fit→predict→ndarray` | 薄封裝;與 baseline/portfolio 同組態(複用鐵律);SHAP 留 audit |
| `src/augur/models/registry.py`(新) | `model_registry` CRUD | #15 可重現、resume;並發/半寫保護 |
| `src/augur/models/artifact.py`(新) | joblib 序列化 pipeline+凍結 feats+as-of | 冪等 resume、離線=上線 |
| `src/augur/audit/import_isolation.py`(新) | **AST 稽核**:預測 7 package 不 import knowledge/philosophy/advisor、不 SELECT 新表當特徵 | 隔離現為約定非機制;聲稱強制前必建 |
| `scripts/train_ranker.py`(新) | CLI:purged WF 逐折 fit→artifact+registry | 缺 train 入口 |
| `scripts/predict_asof.py`(新) | CLI:載 registry→top-N→`prediction_values` | 缺 predict 出單入口、靈魂產品口 |
| `scripts/monitor_prediction.py`(新) | 薄 CLI:IC 衰變+逐空頭子期+半年重跑一致 | 維運留痕 |
| `evaluation/walkforward.py`(改) | embargo 改保證下界 | median×0.69 估 → 實際交易日 min gap |
| `evaluation/portfolio.py`(改) | 呼叫端強制 cost≥0.00585+size/beta 歸因 | cost=0.0 預設不可作終判 |
| `evaluation/metrics.py`(改) | HAC gate 綁死 | 現只顯示未當 gate |
| `universe/core_gate.py`(改) | `_select_core` join 帶 as-of listing 維度 | 真消 survivorship |
| `features/chip.py`(改) | probe 公布時刻閉環 | 同日含 open question |

**新表 DDL(住遷移器 `migrate_prediction_ddl.py`,冪等 `IF NOT EXISTS`)**:

```sql
CREATE TABLE IF NOT EXISTS model_registry (
    model_id      TEXT PRIMARY KEY,          -- 如 RankRidge_H60_20260531_seed0
    family        TEXT NOT NULL,             -- RankRidge / RankGBDT
    horizon       INT  NOT NULL,             -- H(交易日)
    train_span    daterange NOT NULL,        -- 訓練 panel 期間
    asof_snapshot DATE NOT NULL,             -- as-of 凍結日
    feats_hash    TEXT NOT NULL,             -- canonical 特徵集 hash(口徑鎖)
    seed          INT  NOT NULL,
    metrics       JSONB,                     -- {rank_ic, hac_t, net_sharpe, maxdd...}(#15 真兆)
    artifact_path TEXT NOT NULL,             -- joblib 落點
    git_sha       TEXT NOT NULL,             -- 半年重跑一致鍵
    created_at    TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT model_family_chk CHECK (family IN ('RankRidge','RankGBDT'))
);
CREATE TABLE IF NOT EXISTS prediction_values (
    panel_date  DATE NOT NULL,               -- as-of 預測 panel
    model_id    TEXT NOT NULL REFERENCES model_registry(model_id),
    stock_id    TEXT NOT NULL,
    score       DOUBLE PRECISION NOT NULL,   -- 模型原始 score(任意尺度)
    rank        INT NOT NULL,                -- 橫斷面序位(1=最強)
    PRIMARY KEY (panel_date, model_id, stock_id)
);
COMMENT ON TABLE prediction_values IS '預測產物;禁被預測 7 package 回讀當特徵(AST+DB GRANT 雙稽核為建表前置驗收)';
-- 預測角色 GRANT:REVOKE SELECT ON prediction_values, model_registry FROM <predict_role>
```

## 11. 分階段建置

- **階段 A 骨幹先通**:新建 models/{ranker,registry,artifact}+train_ranker+predict_asof+兩表 DDL;RankRidge(alpha=1.0)走 purged WF→top-N 寫表。**驗收**:端到端跑通、`baseline.run_ladder` 與 `predict_asof` 對同 as-of/feats_hash/seed 產同 score(雙軌一致 CI);**對抗反例**:故意讓 train 讀晚於 as-of 之 panel → 須被硬上界擋、報錯不靜默。
- **階段 A' 隔離+embargo 硬前提(與 A 並行、必補)**:新建 `import_isolation.py` AST 稽核+新表 DB GRANT(列建表前置 gate);embargo 改保證下界。**驗收**:故意在 models 加 `import augur.knowledge` → 稽核須 fail;H=60 min gap≥5、H=252 標禁入。
- **階段 B 提拔(IC 診斷)**:五鏡+提拔三審(as-of/HAC gate 綁死/≥3 seed)。**驗收**:HAC-t≥2 方顯著、iid 禁入;M1 headline 先 DB 重建+HAC 重算方採信;**對抗反例**:隨機打亂 label 之 sanity 負對照 IC≈0;as-of IC 不得高於 pan-hist(高於=survivorship 假象未清)。
- **階段 C 經濟(靈魂終判)**:強制 cost≥0.00585+size/beta 中性化+逐空頭子期+entry 開盤/VWAP 敏感度。**驗收**:net Sharpe/Calmar 優基準+MaxDD 可控+空頭段不崩;**對抗反例**:cost=0 vs 0.585% 兩版,net alpha 隨成本消失即非可交易停項;size 中性化後 alpha 消失即記 exposure 偽裝。
- **階段 D 維運**:容量/衝擊成本模型+monitor 半年重跑一致+chip probe 閉環+point-in-time roster 真消 survivorship。**驗收**:半年重跑同 git_sha 產同結果;**對抗反例**:小型股 top-N 加容量衝擊後 net 崩 → 揭 0.585% 樂觀幅度。

## 12. 驗收準則(含對抗性反例)

見各階段「驗收+對抗反例」。關鍵鐵閘:①雙軌 byte 一致;②H=252 結構洩漏被 gate 擋;③注入 release>panel 值須缺列;④as-of IC ≤ pan-hist IC;⑤HAC-t≥2 gate、隨機 label 負對照 IC≈0;⑥M1 headline 重建前禁當錨;⑦cost=0 vs 0.585% net alpha 存活;⑧net 優基準+空頭段不崩;⑨size/beta 中性化後殘差 alpha 存活;⑩AST+GRANT 雙閘 fail-closed;⑪stochastic ≥3 seed 取統計。

## 13. 對抗審查發現表(四鏡 · severity · disposition)

| 鏡 | 發現 | severity | 處理 |
|---|---|---|---|
| **自欺** | core_universe_asof 宣稱消 survivorship,但 code join 當前 roster = 倖存名單 | **critical** | 全採納:禁宣稱已消、列未建債;改 `_select_core` 帶 as-of 維度;as-of IC≤pan-hist 為驗收 |
| **自欺** | headline +0.132 存於報告但當前 DB 不可重現、iid Eff-t 未 HAC 復驗當 alpha 錨 | **critical** | 全採納:標不可重現、禁當錨;先 DB 重建+HAC 重算+退市補完 |
| 偷看未來 | embargo median×0.69 估非下界;H=252 embargo=4 label 窗越 test panel=結構洩漏 | high | 全採納:改實際交易日 min gap;H=60 ≥5 天;H=252 禁入主表 |
| 偷看未來 | chip 同日含(chip.py:17)未閉環、T+1 揭露若晚於次日開盤即洩漏 | high | 全採納:probe API 公布時刻閉環、未 probe 標風險 |
| 假兆 | 成本固定 0.585%(預設 0.0)、零容量/衝擊;小型股真成本 2-5%→net 是假 net | high | 全採納:強制 cost≥0.00585、標樂觀下界、容量模型列前緊接必建 |
| 假兆 | benchmark=等權 common 股,long top20% 贏可能 size/beta 偽裝非 skill | high | 全採納:S8 size/beta 中性化歸因、揭殘差 alpha |
| 假兆 | label entry=close(t+1) close-to-close 偏樂觀 | medium | 採納:開盤/VWAP 重跑敏感度 |
| 工程 | AST 隔離稽核當既成寫進驗收,但 codebase 不存在(僅 py_compile) | high | 全採納:新建 import_isolation.py+DB GRANT、列建表前置;未建前 honesty 降級「約定、稽核待建」 |
| 工程 | 取徑1 nested-CV alpha 與 baseline 硬編 alpha=1.0 不一致=雙軌漂移 | high | 採納取徑3:拒 nested-CV、固定 alpha=1.0、CI 稽核比對兩路徑組態 |
| 流程 | 三取徑皆單視角草案(#20 高風險門檻應多視角) | medium | 已補:四鏡對抗審查+發現表留痕滿足 #20 |

## 14. 待你拍板(8 決策點)

1. **模型選型**:默認 B2 Ridge(alpha=1.0 固定、實證 4/4 勝 GBDT)+ GBDT 僅真贏時上位 —— 確認「穩健簡約線性主軸」為生產默認?
2. **預測 horizon**:主戰場 H=20/60、H=5 次要、**H=252 禁入主表**(結構洩漏)—— 確認是否徹底放棄年週期訴求?
3. **survivorship 未建債(critical)**:先建 point-in-time roster(上市/下市日)+完整度滾動近窗再談 as-of IC 可信,或先跑骨幹但明標 survivorship 未消?**影響所有 as-of IC 可信度。**
4. **headline 錨定**:M1 +0.132 當前不可重現 —— 先 DB 重建+HAC 重算作可信 baseline 前提,或接受先跑新 baseline 不錨舊數字?
5. **成本模型深度**:固定 0.585% vs 容量/衝擊模型 —— 後者列 models 前緊接必建(終判工具本身)還是可後置未來債?
6. **chip 同日含**:先 probe 5 表 API 公布時刻閉環,或先保守改 `date<panel_date`(T+1 gate、輕損時效)?
7. **上線判準量化閾值**:net Sharpe/Calmar 具體門檻(如 net Sharpe≥1.0、MaxDD≤?%)、逐空頭子期不崩之定義 —— 須人拍板數值。
8. **重訓 cadence**:季度 vs 對 H=20 提高頻率(增 look-ahead/usage 權衡)?

## 15. 殘留風險(誠實)

- **台股橫斷面 alpha 本質微弱**(rank IC 0.02-0.05 即實用);經濟優先取徑最不寬容、會頻繁判停項 —— 誠實非缺陷,但意味**可能根本沒有扣真成本後存活的 alpha**,無技術解。
- survivorship 即使補 roster,台股下市股若 FinMind 源本身不全則只能部分消、殘留樂觀無法完全量化。
- 容量/衝擊成本模型建成前小型股 net Sharpe 上界不可信;即使建成仍是估計,真可交易性只能靠 paper-trading/實盤逐步驗證。
- 樣本期若偏多頭,逐空頭子期只能拆已發生回撤、對未來 regime 無外推;「半年重跑一致」保證可重現性非樣本外真 alpha 存續。
- 三鏡頭特徵同源共線,消融「無增量」vs「共線稀釋」不可完全分辨、歸因自欺結構性殘留。
- AST 字面稽核擋不住動態 SQL/間接讀,須 DB GRANT 才閉環;embargo 保證下界後 expanding 折 label 窗重疊仍使 IC 自相關、HAC 只校正不消除。
- long-short 因台股平盤下不得放空/券源不足可能結構性不可執行,long-only 犧牲 market-neutral 抗 regime 之靈魂賣點。

---

**一句話**:骨幹只欠 `models/` 一層 + train/predict 兩支 CLI + 兩表,evaluation 全複用;但**真正的難點不是接骨幹,是誠實**——survivorship/headline 重現/成本模型三處未閉環必須誠實標債、不當既成 alpha,否則接了骨幹只是「用未校準的尺量假兆」。三敵零容忍是這條路的憲法紅線。

---

## 16. 拍板紀錄(2026-07-05 用戶「照建議全採」)

1. ✅ 模型=Ridge(alpha=1.0)主軸、GBDT 僅真贏上位。
2. ✅ horizon=H=20/60 主、H=5 次要、**H=252 禁入提拔/經濟主表**。
3. ✅ survivorship=先跑骨幹+**明標未消債**,point-in-time roster 排階段 D。
4. ✅ headline=**不錨舊 +0.132**、跑新誠實 baseline。
5. ✅ 成本=階段 C 先固定 0.585%+標樂觀下界,容量/衝擊模型排階段 D。
6. ✅ chip=先保守 `date<panel_date`(T+1 gate)、probe 排後。
7. **上線判準(實驗值 #27、標實驗中、依實證調整、不入憲)**:net Sharpe ≥ 1.0、Calmar ≥ 0.5、MaxDD ≤ 25%、**逐空頭子期(2015/2018/2020/2022)每段 net 報酬不顯著劣於等權基準同期**;未達不上線、誠實記停項。
8. ✅ 重訓=季度。

**執行序(§26 一支一支 #19、實測 #7、三敵零鬆動)**:階段 A 骨幹先通 → A' 隔離+embargo → B 提拔(HAC gate) → C 經濟 → D 維運。

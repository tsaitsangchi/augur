# Augur 專案總覽（記憶快照 2026-06-18；⭐ 最新進展見下方 2026-06-26 段）

> 讀完此頁即懂 augur 全貌。權威來源永遠是 repo 裡的 5 治權檔；此為導航 + 現況快照。
> ⚠️ **DB 狀態多變、且不隨 git（每台機器各自獨立）→ 永遠以實查為準，勿照抄 handoff。**

## ⭐ 2026-06-26 最新里程碑（覆蓋下方舊快照「F3 未建/DB 3 表/治權版本」等過時處）
**全管線 raw→feature→universe→model→validate 打通**（兩機並行整合）：
1. **raw 84 表到 as-of 2026-05-31 完整**（GoldPrice 補漏抓、三層驗證、tag `asof-complete-20260624`）→ [[asof-completeness-per-table-verification]]
2. **核心股選出 875**（`core_gate` 四道閘：候選空間+完整度+流動性+conditional；pilot 演進 3105→1211→633→742→**875**、代表權值股 10/10 全納入）→ [[core-universe-and-f3-model]]
3. **F3 模型 as-of Ridge H60 rank IC +0.132、勝率 0.96 — alpha 為真**（M-0/M-1/M-2 + 五鏡 + F2c 估值；⚠️ 待親讀 evaluation 驗 purged 口徑 #15）
- **治權已升**：原則精華 **v1.7.1**（+資料完整性判準 as-of 2026-05-31）、憲章 **v1.9.1**、CLAUDE **v1.5**。最新 tag `evaluation-m2-asof-baseline-20260626`。
- **下方舊快照之「F3 待做/本機 DB 3 表/原則精華 v1.6.0/憲章 v1.8.0」均已過時**——以本段 + 連結 memory 為準。

## 一句話
**Augur = stock_backend 的 clean-room 重啟**——「只用真實資料、誠實預測台股」。從 FinMind/FRED 抓可溯源日級資料 → source-pure 特徵 → 選資料乾淨核心股 → 樹/transformer 模型預測未來 H 日**相對強弱**（橫斷面排序→top-N）→ walk-forward 誠實驗證附可信度。名字 augur=古羅馬觀兆者，**只信真兆、不造假兆**。系統建議、人決策，不下單動錢。

## 位置 / 環境
- **Repo**：`/home/hugo/project/augur/`（GitHub `tsaitsangchi/augur`，branch main）。WSL2/Linux。
- **git 現況**：HEAD **`7ff03f9`**（2026-06-18 已 push origin/main）；**最新 tag `reconcile-scope-fixes-20260618`**（reconcile_by_dim_id 逐維度 id 對帳 + catalog `_reconcile_scope` 對齊 fetch_mode[by-dim-id/8表/TotalReturnIndex 假 MIS 修]；issue 全稽核 catalog fetch_mode↔reconcile_scope 全一致）。**2026-06-18 session 大事**：①禁閘實驗失敗+還原（我 token meter 為真會撞 6000 觸 403、禁閘只適 Mac 黑箱 meter token）②Institutional heal VM=87→0（最新日 preliminary→final、非幻像）③gated 全 re-run 進行中（per-stock 表 reconcile 殘小 VM=修訂漂移、benign EX=0）。前序 tag `catalog-clean-rebuild-20260616`（catalog drop+乾淨重建:95/95表·754欄·dirty欄VARCHAR·FULL_START探源頭）。catalog 系列 tag:catalog-clean-rebuild>catalog-complete>catalog-builder>catalog-driven-sync(20260615-16)。〔以下為 2026-06-11/12 舊快照、多已演進〕關鍵 tags：**by-dimension-id-20260611**（封存點 2026-06-11 晚：#2#3#4 by 維度 id 落地→**82 dataset 全可抓**）、**handoff-20260611**、treaty-v1.4.0、claude-v1.1。**本 session（2026-06-11）大躍進**：canonical 死點修(News 單日型 end_date 相容、非「最早日」問題) + News 週末漏抓修(事件型 datetime by-date 不跳週末) + **#18 維度 id 來源階層**(/datalist→roster→文檔+probe、一律問 /datalist 不抄文檔) + **CLAUDE #26 自我糾錯強化**(執行層主動/真兆為據/放量定義收斂) + **FinMind/FRED 兩資料源完整研究**([[finmind-data-source]] sponsor 6000hr⏰6-24到期 + [[fred-data-source]] 免費無到期+#8 vintage) + **#2#3#4 by 維度 id**(GovBonds maturity/TotalReturnIndex index/CapitalReduction fallback) + ingest PK 維度欄通用修。詳 `reports/augur_cross_machine_handoff_20260611.md`。
- **DB（關鍵：不隨 git，跨機各自獨立、內容不同）**：PostgreSQL db=`augur` user=`augur`。
  - **本機 WSL2**（實查 2026-06-11 晚）：**僅 3 表 / ~11 萬列**（GovBonds 99199 + TotalReturnIndex 10792 + CapitalReduction 1，是 #2#3#4 修法**實測落地**；先前全市場 sync 半成品 ~1800 萬列已清）。**全史要從零重跑**（趕 FinMind **6-24 到期**）。`full_market_sync` 未在跑。（更早 2026-06-11 上午曾有 24 表 ~1.09 億列；用戶常 drop 重測 → 永遠以實查為準。）
  - **原機 Mac**（`caizongyede-MacBook-Pro`，handoff 20260611 記載）：**另一套獨立 DB**，13 表 ~78M 列，sync 背景跑中（8/82、ETA~1週）。表組成與本機不同（原機有 GovBank；本機有 HoldingSharesPer/PriceAdj/MarginPurchase/CashFlows…）。
  - ⚠️ git 只帶 code/reports/charter/CLAUDE，**不帶 `.env` 與 DB**；兩機 DB 不互通。用戶常 drop 全表重測 → **以實查為準**。
- **venv**：`venv/`（psycopg2-binary/pandas/polars/numpy/requests/python-dotenv 已裝；sklearn/xgboost/lightgbm/catboost 在 pyproject deps；torch optional `[deep]`）。測試一律 `PYTHONPATH=src venv/bin/python`。
- **.env**（machine-local，不進 git，本機已存在）：DB_* + FINMIND_TOKEN + FRED_API_KEY；範本 `.env.example`。

## 5 治權檔（SSOT，先讀這些；改 code 只依這 5 份 + schema 目錄 + live API）
| 檔 | 角色 | 版 |
|---|---|---|
| `docs/系統核心思想_v1.2.0.md` | 靈魂（是什麼/為什麼/絕不能違反） | **v1.2.0** |
| `docs/原則精華_v1.6.0.md` | **20 條不可違反法律**（WHAT｜WHY｜ENFORCE） | **v1.6.0** |
| `docs/系統架構大憲章_v1.8.0.md` | 憲法（三敵人×管線 + 12-PHASE + 升版 + 附錄C理論定位） | **v1.8.0**（+catalog橫切元資料登錄 + **官方 datasets.md 入憲為 catalog 抓法權威輸入源**；附錄C＝業界4維度架構理論驗證、grounding不升版） |
| `CLAUDE.md` | AI 工具規則（27 條，含 #26 自驅動/#27 試錯 + #18 標頭與命名慣例）| **v1.5** |
| `README.md` | 對外總覽 | — |

## 三個敵人 × 三條基石（★ 一條守一個敵人）
- **① 假資料**（imputed/補值/hardcoded/推估，無 API 源）→ 基石 **#1 零幻像/Source-Pure ★**
- **② 偷看未來**（時間洩漏，回測美實戰崩）→ 基石 **#8 Anti-Leakage ★**
- **③ 自我欺騙**（灌水回報，把計畫當成果/單次極值當定論）→ 基石 **#15 誠實回報 ★**
- **北極星問題**：寫任何數字/結論前問「**這是真兆，還是假兆？**」三個都「是」才寫。

## 20 條原則（速查；全文以 原則精華_v1.6.0 為準）
**A 資料紀律**：#1 零幻像★ / #2 API即權威 / #3 純通用ingestion(無白名單；**唯一資料本質排除=#4日；`OUT_OF_UNIT` 重定義為「規模物理不可行之 operational 暫緩」**:券商分點/權證/鉅額,非治權排除) / **#4 日為最小單位(唯一資料本質排除準則,v1.4.0)**:不收intraday;凡API日級真兆皆抓、不以抓取維度/非個股標的排除 / #5 型別紀律(字串VARCHAR255→TEXT、數字NUMERIC(20,6)自動擴大) / #6 冪等+斷點續傳 / #7 DB↔API對帳(value_mismatch=0∧extra=0) / **#17 API速率公民/主動限速**(現操作值 MIN_INTERVAL=**0.7s**、PER_STOCK_WORKERS=32;非治權凍結值、依 #19 試錯逐級調整、住 finmind.py 單一處;防IP ban) / **#18 抓取依API探測方式+範圍/不空抓**(探測抓法 market/per-stock/by-date/**by維度id** + 起點 resume/backward-probe;**需特殊維度id→補通用多維度抓取(非排除)**;唯規模不可行者 operational 暫緩)
**B 建模紀律**：#8 Anti-Leakage★(walk-forward IC附purged) / #9 思想≠特定值(Pareto 0.80、康波40-60年等不硬編進feature) / #10 核心股質>量(可少、不評分排名) / #11 五鏡特徵治理(IC/共線/必要性/SHAP/purged-CV合看) / #12 單一引用源(panel+metric由單一helper)
**C 風險治理**：#13 空頭防護規則地板優先(預測為輔) / #14 經濟價值判定(MaxDD/Calmar非AUC) / #15 誠實回報★ / **#19 可控風險下逐級逼近最佳奇異點**(試錯即進步;可恢復+有界+即時退場;重覆驗證再定論;只試方法/參數絕不試資料真假)
**D 開發/協作紀律**：#16 **Clean-Room 重建/零 stock_backend 參考**（augur 所有 code 只依 5 治權檔+schema目錄+live API；**不讀/不移植 stock_backend 任何 code/數字/設定**；唯一觸點＝憲章附錄B考古+思想啟發，皆不得回流 code） / **#20 自驅動×實證決策**(2026-06-12入憲;經授權AI自己prompt自己[loop]推進+執行層方法AI主導+自我糾錯試錯;凡判斷/做法/operational決策先實證[probe/API/code/DB]、嚴禁憑「我以為」;**決策層人拍板/執行層AI自駕**;實證動因:憑臆測pattern連兩次誤殺進程→無實證的主動必闖禍;＝#15誠實擴展)

## 管線（各層職責不越界）
`raw(FinMind/FRED) → feature(source-pure) → universe(核心股 gate) → model(樹/transformer) → validate(multi-cycle walk-forward)` + 橫切 `core`/`audit`。
- raw：通用 ingester 自動建任意 API 表（無白名單）
- feature：只用 source-pure 值；**算不出即缺列，不存 fake/zero-fill**
- universe：核心股＝**全部 source-pure 完整股**（純完整度 gate，**無評分排名**）；任一面板任一特徵缺值即排除
- model：樹家族主軸、transformer 輔
- validate：自包含 walk-forward，**不讀 model artifacts**（雙軌獨立）

## 12-PHASE 從零重建（不可跳/不可改序）
0 環境 → 1 Infra bootstrap(2 log表) → 2 名冊(TaiwanStockInfo) → 2b FRED(fred_series) → 3 宇宙引導 → 4 全市場全史sync(--all) → 5 Raw對帳(#7) → 6 核心候選(raw完整) → 7 Feature Store → 8 最終核心(完整度gate,0缺值) → 9 五鏡特徵audit → 10 模型訓練 → 11 模型驗證。
**三種建法**：① generic auto-schema→API原始表 ② explicit DDL→infra log(PHASE1) ③ builder自建→計算型表(feature/universe/model 各自 PHASE `CREATE IF NOT EXISTS`)。

## 表 inventory（數字隨 live enum/範圍變動，以報告與實查為準）
- **通用 ingester live API 驗證**（schema-catalog-live 2026-06-10）：**81 表 / 662 欄**（FinMind 80 + FRED 1）；目錄 `reports/augur_generic_ingester_schema_catalog_20260610.md`。
- **全市場 sync 範圍**：用戶選「全部含期權/外股/商品」共 **82 dataset** 全史 + FRED 12 series。
- intraday（#4）守門排除；券商分點/權證/鉅額交易（#3#18 OUT_OF_UNIT）範圍外排除。
- 早期（2026-06-09）取樣建表另有 85 表口徑（會隨 enum 變動）：`reports/augur_finmind_fred_table_schema_20260609.md`。

## Code 現況（src/augur/，全 clean-room、§18 精簡標頭、實測過）
**已建 F0+F1+F4+F2**：
- `core/`：config.py(.env→SSOT,守#12) / db.py(connect/transaction/ping,守#6) / generic_schema.py(auto-schema infer/detect_keys/ensure_table/upsert,守#5#3#2#6#1;**3韌性修正**:date型別推導 + upsert按主鍵去重 + detect_keys(require=)強制納指定鍵欄防by-date單日塌陷) / schema.py(infra log DDL + DB-derived helper)
- `ingestion/finmind.py`：FinMind client + **主動限速三層防護**:`_pace()` **MIN_INTERVAL=0.7s**(現操作值、依 #19/#27 試錯逼近、非治權凍結) + **`_quota_gate()` 主動額度閘**(閉環問 /user_info 權威錶、撞 403 前先停、退夠續) + 403 `QUOTA_COOLDOWN=1800s` 長冷卻(防重試風暴);PER_STOCK_WORKERS=32(fetch 並發、DB 寫序列、start rate 仍 _pace-bound) + `fetch_dedicated`(分點/權證專屬 endpoint) + list_datasets/datalist/translation（守#7#3#2#1#17#24）
- `ingestion/fred.py`：FRED client，"."→NULL；**只存(series_id,date,value)丟realtime metadata**（守#7#2#1）
- `ingestion/ingest.py`：單來源orchestrator + **#4 intraday守門** + **OUT_OF_UNIT 排除券商分點/權證/鉅額交易(#3#18)** + require_keys透傳（守#4#3#1#6）
- `ingestion/sync.py`：全市場sync engine — seed_roster+daily_datasets+sync_finmind_dataset(market-probe→per-stock→canonical-2330-probe)+sync_fred+sync_all + by-date增量(sync_by_date/sync_all_by_date,require_keys=('date',)) + **by-date backward-probe(自近往遠探資料邊界,取代forward-probe空掃,#18)**（守#3#4#6#1#2#17#18）
- `audit/reconcile.py`（F4）：#7 DB↔API byte對帳(matched/value_mismatch/missing_in_db/extra_in_db,pass=VM0∧EX0)+reconcile_by_date/market/fred + heal_by_date(偵測→重跑sync補齊,correction=重跑sync非hand-patch) + **`_key` 用 `_norm` 修數值欄寬 PK false-negative(fadba1a)**（守#7#2#1#15）
- `scripts/daily_maintenance.py`(薄CLI) + `scripts/full_market_sync.py`(**全市場全量驅動**:PHASE1→2 seed→2b FRED→4+5 逐dataset sync + 逐dataset #7對帳→問題寫 reports/augur_fullsync_issues_20260610.md)
- `features/panel.py`（**F2**；2026-06-15 rename 自 builder.py、合規 #18 禁通用角色名）：source-pure 價量特徵；算不出即缺列；anti-leakage(#1#8#9)
- `universe/core_gate.py`（**F2**）：純完整度 gate＝全部 source-pure 完整股，**無評分排名上限**(#1#10)
- `catalog/__init__.py`（橫切 catalog 元資料登錄；2026-06-16 全實作完成）：2表 DDL(dataset_catalog 含 **table_name_zh**/column_catalog)+`probe_dataset`(**全實作**:landed DB讀/unlanded probe cascade+**FULL_START refine 探源頭真起點**[含 landed 表、DB min 被當初 FULL_START sync 截斷→US1928/UK1968/CrudeOil1986]+**dirty欄強制VARCHAR**防型別爆炸+**稀疏月結算表短窗fallback**+**權證多檔probe取真型別**+snapshot哨兵)+optimal_mode+**seed 表名/欄名中文(datasets_zh.md SSOT、curated 入 md 非 code dict)**。**drop+一次乾淨重建完成:95/95表·754欄·全欄完整(中文/型別/應全填 0 NULL)·全驗證**(tag catalog-clean-rebuild-20260616)。datasets_zh.md＝中文策展 SSOT、可由表反向生成。
**未建（空 __init__）**：`models/` `evaluation/` → **F3 待做**。
**治權合規**：2026-06-15 全 codebase 稽核過（tag `compliance-audit-20260615`、~2239行/15模組、零資料層違規）；命名慣例 library=領域名詞/CLI=動作動詞(CLAUDE #18 v1.4)。

## Roadmap（plan F0-F4）
- **F0 地基**✅ / **F1 ingestion**✅(finmind/fred/ingest/sync + by-date增量 + daily_maintenance) / **F4 audit reconcile**✅起步(#7對帳+heal;五鏡#11待) / **F2 features+universe**✅(builder + core_gate)
- **F3 models(樹base+樹家族)+evaluation(multi-cycle validators,metric/panel單一helper #12)** ← **下一步**（PHASE 10-11）
- research torch 模型(chronos/tft/…)：deferred，需隔離venv
- **pilot 教訓**：全量全史前先 pilot 驗全鏈(fetch→#7對帳→heal)；pilot 抓到 by-date PK 塌陷等 3 真bug

## 全史 sync 現況（區分本機 vs 原機，DB 不隨 git）
- **本機 WSL2**（實查 **2026-06-12 17:0x**）：run2 sync **跑中**(PID 81095、nohup)、[2/82] 完成、**31.1M 列/7 表**;HEAD `796bdf6`、今日 8 tag(treaty-v1.6.0→f3-self-critique);**0.8s/8w=用戶決策、gate 週期暫停=預期**;跨機接續讀 `reports/augur_cross_machine_handoff_20260612b.md`。(用戶頻繁清空重測,永遠以實查為準。)
- **原機 Mac**（handoff 20260611）：8/82 dataset、~78M、背景跑中 ETA~1週；防護 caffeinate+nohup+resume-safe。**2 個 #7 FAIL 皆 reconcile artifact 非資料問題**：(1) GovBank VM=0 EX=MIS=412111＝`_key` 寬PK數值欄 Decimal vs raw 永不配對，已修 fadba1a；(2) Institutional per-stock 落地 vs reconcile market by-date scope 不一致(含權證)，scope 待修。
- **IP-ban 教訓**：0.7s持續串流曾觸發 FinMind「持續濫用/每日累積」ban(非hourly quota)→放慢+跨日分批+commit-per-stock resume；冷卻須靜置零請求honor retry_after。測試用**最小單位(單股單日)**先確認IP健康才放量。

## 與 AI 協作的硬規則（CLAUDE.md）
- **clean-room #16**：產生 augur code 絕不讀/移植 stock_backend code。
- **繁體中文**對話。
- **Commit/Push 須明示授權**；不 hand-patch 已 committed 資料（改 writer+重建）；不在 commit 含 .env/token。
- **誠實 #15**：數字 trace 回 (a)程式/(b)DB/(c)API；不把未跑完當成果（無 aspirational）；stochastic≥3次取統計。
- **重大改動一支/一段做完讓用戶過目再進下一**（不批次傾倒）；改治權檔須跨檔一致性。
- **≥5min任務每5min回報；≥30min防睡眠**。

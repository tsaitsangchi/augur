# 全系統架構與程式合規稽核報告(2026-07-04)

**方法**:8 視角讀碼稽核(架構層職責/core+ingestion/catalog+audit/features+universe+evaluation/素養三層/scripts #29 全 69 支/命名測試依賴/三敵資料誠實掃描)→ 合併 ≤30 → 每條 3 懷疑者對抗驗證(≥2/3 存活)。基準=憲章 v1.22.0+原則精華 v1.7.1(2026-07-04 晨版)。
**結果**:原始 77 條 → 確認 **28** 條(執行層 19/決策層 9)、否決 2 條。首輪撞 session limit 之 4 條已於 resume 補驗。

## 執行層(直接修+實測)

### 執1. 〔medium·bug〕philosophy
- **檔**:/home/hugo/project/augur/src/augur/philosophy/framework.py
- **問題**:framework.build()/build_people() 的 DELETE 重建在語料擴張後已既不冪等也跑不完:重跑 scripts/build_philosophy_framework.py 會先 commit school 層 wipe(CASCADE 連帶清 school_thinker 19 列與 stock_philosophy_tag),再於 build_people() 的 DELETE FROM philosophy_thinker 炸 NO ACTION FK 而中止,留下半完成 committed 狀態;docstring 仍宣稱「冪等」。tag 現為 0 列,疑已受災一次。
- **證據**:psql pg_constraint 實查:philosophy_work.thinker_id FK=CASCADE、但 knowledge_lexicon.source_work_id 與 knowledge_sentence.text_id 皆 NO ACTION——DELETE thinker 之 CASCADE 鏈必被擋下報錯;DB 現有 thinker=3,982/work=1,317/lexicon=154,875/sentence=1,539,019 而 THINKERS 種子僅 17 人。core/db.py transaction() 每個 with 區塊獨立 commit → 第一交易(school wipe)先 commit、第二交易失敗回滾=school_thinker/tag 已清而不復建(tag 現 0 列)。framework.py:356 DELETE 語句 2026-07-04 複驗仍在。
- **修法**:build_people() 改 upsert(INSERT ... ON CONFLICT (name) DO UPDATE)只維護 17 位策展思想家,不再 blanket DELETE philosophy_thinker(下游已掛 1,317 works/63,601 chunks/154,875 lexicon);docstring 修正「冪等」敘述。
- **驗證**:3/3

### 執2. 〔medium·bug〕evaluation/label 口徑
- **檔**:/home/hugo/project/augur/src/augur/evaluation/label.py
- **問題**:「t+1 進場」口徑在 panel_date 非交易日時漂移為 t+2:_entry_exit 假設 calendar[0]==panel_date,但 cal 以 d >= panel_date 過濾——非交易日 panel 之 cal[0] 已是次一交易日,entry=calendar[1] 變成第二個交易日進場。方向保守、非洩漏,但與 docstring/doctrine 宣告之 t+1 口徑不符,且 12/35 個現有 panel 受影響(含最新 panel 2026-05-31)。
- **證據**:label.py:43-47 entry=calendar[1]、label.py:58 `cal=[d for d in calendar if d >= panel_date]`(2026-07-04 於 HEAD b0216f5 複驗仍在)。DB 實查:35 個 panel_date 中 12 個不在 TaiwanStockPriceAdj 交易日曆(2011-12-31、2012-12-31、2016-12-31、2017-12-31、2018-12-31、2021-12-31、2022-12-31、2023-09-30、2023-12-31、2024-03-31、2024-06-30、2026-05-31)。
- **修法**:改為 cal 過濾 d > panel_date、entry=cal[0]、exit=cal[h](交易日 panel 結果不變、非交易日 panel 修正為真 t+1);修後重跑受影響 eval 確認 headline 數字變動幅度。
- **驗證**:3/3

### 執3. 〔medium·bug〕ingestion/by-date 完整性
- **檔**:/home/hugo/project/augur/src/augur/ingestion/sync.py
- **問題**:sync_by_date 單日 FinMindError「跳過該日不中斷」但不記錄失敗日,summary 無 failed_days;resume 以 DB max(date) 起算 → 較早被跳過的整日成永久空洞;且 reconcile_by_date 只迭代 DB 已存在的 distinct date,整日缺失連對帳也看不見。對偶路徑 _per_stock_sync 有 failed_ids 供精準 heal,by-date、_dimension_sync、sync_fred 皆無同等機制——對 #6「不掉資料」之防護不對稱、靜默漏抓風險。
- **證據**:(合併稽2/稽8)sync.py:425-430 `except FinMindError ... continue`(無記錄;2026-07-04 複驗仍在)、:409-413 start=_max_date resume、:446 回傳 dict 無 failed 欄;_dimension_sync(:262-263)/sync_fred(:463-464)亦靜默 continue;reconcile.py:127-130 只對 DB 已有日對帳;對照 sync.py:190 failed=[] 僅 per-stock 有(且該註解引「heal(#8)」條號錯置,應為 #6/#7)。
- **修法**:sync_by_date 記錄 failed_days 入回傳 summary(對齊 failed_ids 模式)並於 progress 回報,sync_all_by_date/daily_maintenance 印出供 scoped 重跑;_dimension_sync/sync_fred 同補;可另加交易日曆驅動之缺日偵測補 reconcile 盲區;順修 #8 條號錯置。
- **驗證**:3/3

### 執4. 〔medium·doctrine-drift〕philosophy/knowledge 檢索契約
- **檔**:/home/hugo/project/augur/src/augur/philosophy/retrieval.py
- **問題**:textnorm 三方 JOIN 契約在查詢端未履行:textnorm.py 契約明文「knowledge_concordance、knowledge_lexicon、advisor 檢索三方用同一函式產 term」(#12),寫入端已守約,但 retrieval._term_forms 只做 NFC+lowercase、不經 textnorm、無 Porter stem/jieba——英文屈折形查詢對 stem 過的庫必 miss,對庫內確有的內容誠實回空 → 顧問將答「知識庫中無此內容」而該句為假(#15 反效果)。
- **證據**:寫入端守約(scripts/build_concordance.py:30、build_lexicon.py:148 皆 import textnorm);DB 實查:knowledge_concordance term='run'(en)=6,918 列、'running'=0 列;knowledge_lexicon term='invest'=4 列、以 'investment' 查=0 列——lexicon_lookup('investment')/concordance_lookup('running') 實際回空。2026-07-04 複驗:_term_forms(retrieval.py:113-115)仍不呼叫 textnorm(docstring 稱「呼叫端可先正規化再查」但 grep 全 repo 無任何呼叫端先過 textnorm)。
- **修法**:_term_forms 改 import augur.knowledge.textnorm:除 NFC 原形/lowercase 外,加 norm_headword(term,'en')(stem 形)與 norm_headword(term,'zh') 入 IN 清單(lexicon_lookup 與 concordance_lookup 同步);零資料重建、純查詢端修正。
- **驗證**:3/3

### 執5. 〔medium·doctrine-drift〕advisor 防幻覺機械閘
- **檔**:/home/hugo/project/augur/src/augur/advisor/advise.py
- **問題**:憲章「防幻覺=機械 gate 非 prompt 自律」五項中兩項(檢索空→固定誠實句、lexicon 定義引用必附 locator)目前只是零外部呼叫端的 library 函式:advise() 僅呼叫 guard(),guard_empty_retrieval/guard_definition 無組裝路徑接線,lexicon_lookup/concordance_lookup 亦無 caller——該兩閘現況屬「口號」非機械強制。且 prompt.py 空檢索誠實句「素養庫無對應公版原文」與 guard 固定句「知識庫中無此內容」不同——日後接線時遵循 prompt 的回覆會被 guard_empty_retrieval 攔截,兩處誠實句自相矛盾。附帶:數字閘 ② 僅檢 ≥2 位小數,整數/1 位小數編造值(「IC 0.2」)不經白名單即放行,憲章「量化數字須 ∈ payload 白名單」句與機械閘實際覆蓋面不一致(payload.numbers() 之 rank 整數項實質死碼)。
- **證據**:(合併稽5 兩條)2026-07-04 複驗:advise.py:24 僅 `verdict = guard(...)`;guard_empty_retrieval/guard_definition 除 guard_definition 內部互呼外全 repo 零呼叫端;prompt.py:15,25「素養庫無對應公版原文」vs guard.py:12 NO_KNOWLEDGE_RESPONSE=「知識庫中無此內容」;guard.py:32-34 regex `\d+\.\d{2,}` 與 in-code 註解自證窄化。憲章 v1.22.0 L134 明列五閘為機械 gate。
- **修法**:(1) 統一誠實句——prompt.py 改引 guard.NO_KNOWLEDGE_RESPONSE 同一常數(#12);(2) advise() 組裝 lexicon/concordance 路徑時把 guard_empty_retrieval+guard_definition 接進 verdict 鏈,並對 citations 過 verify_verbatim 後再入 prompt(順帶機械攔下 57 個 stale chunk);(3) 數字閘採憲章句補限定如實描述+「IC/Sharpe/score」鄰接數字不論位數皆須 ∈ 白名單。
- **驗證**:3/3

### 執6. 〔medium·boundary-breach〕audit 層邊界
- **檔**:/home/hugo/project/augur/src/augur/audit/feature_candidate.py
- **問題**:audit 層直接寫入 feature 層生產表 feature_values(INSERT/UPDATE/DELETE),違憲章第三部 audit 邊界「唯讀稽核,不改資料、不選股」(模組 docstring 自行把邊界改寫為「不改 raw」);且為潛在核心股污染源——core_gate.canonical_features 為資料驅動(取面板內全部 distinct 特徵),候選列若存在時重建 core 會被納入完整度 gate 而靜默縮小核心,僅靠 docstring 紀律而非機制防護。現況無實害(DB 實查 4 候選已清、distinct feature 恰為 35 個生產特徵)。附帶:audit 層自建分析表(field_correlation/field_return_leadlag/field_lens_map)不在憲章「三種建法」任一類,歸屬分類有文字缺口。
- **證據**:(合併稽1/稽3)feature_candidate.py:27 FEATURE_TABLE="feature_values"、:99-104 INSERT INTO feature_values ... ON CONFLICT DO UPDATE、:113 DELETE(2026-07-04 複驗仍在);憲章 audit 段「邊界:唯讀稽核,不改資料、不選股」;core_gate.py:102-105 canonical_features=SELECT DISTINCT feature FROM feature_values;psql:4 候選在 feature_values 為 0 列。field_correlation.py:26-37 自建表 DDL;憲章三種建法 ③ 僅列 feature_*/core_universe_*/model_registry。
- **修法**:候選特徵改寫入獨立 staging 表(feature_candidate_values,schema 同構)並讓 diagnostics 讀該表,feature_values 回歸 feature 層獨佔寫入(或最低限度 core_gate 機制性排除候選清單);憲章三種建法於下次例行升版補「audit/研究結果表由 audit 層自建(唯讀指 raw/生產資料)」一句。
- **驗證**:3/3

### 執7. 〔medium·bug〕audit/reconcile scope 路由鏈
- **檔**:/home/hugo/project/augur/scripts/reconcile_audit.py
- **問題**:reconcile scope 路由鏈兩端皆有缺口:(1) reconcile_audit._audit 與 full_market_sync.verify 均無 'full-history' 分支,reconcile_audit 另無 'market' 分支,coverage 路由依 _AGGREGATE_DAILY 而非 catalog scope——catalog 可產 5 種 scope,未識別者一律落 by-date,一旦 catalog 重建修正頻率,季頻 per-stock 財報表將被以 by-date 端點對帳(reconcile.py 自述會產假 VM/MIS 的端點錯配);(2) catalog._reconcile_scope 沒有 'market' 輸出:15 張 fetch_mode='market' 表全被標 'by-date',對 date-insensitive snapshot 表(TaiwanFutOptDailyInfo 忽略日期參數、查 1955 回現值)逐日對帳=每個歷史日拿到現在的 snapshot → 假 EX/MIS 風暴;reconcile_market 函數存在但經 scope 路由永遠到不了。目前潛伏(DB 無 full-history 列),但擋住 catalog 重建。
- **證據**:(合併稽3 兩條)reconcile_audit.py:86-100 僅 by-dim-id/roster-scoped/_AGGREGATE_DAILY coverage/else by-date(2026-07-04 複驗 usage line 14 branch 集合未變);full_market_sync.py:64-76 無 full-history;catalog/__init__.py:567-578(5 種輸出、無 market 分支、fallback 'by-date');psql:15 列 fetch_mode='market' ∧ scope='by-date';catalog/__init__.py:758-760 哨兵註解實證 date-insensitive;reconcile.py:296-311 reconcile_market 存在。
- **修法**:執行層補齊:(a) _audit 加 full-history 分支——per-stock 全史對帳+排除最新一季未定案(#7 ENFORCE 類別②);(b) coverage 依 catalog scope 路由(_AGGREGATE_DAILY 為備援);(c) 加 market 分支走 reconcile_market;(d) _reconcile_scope 增 market 判準(frequency in ('snapshot','single-series') → 'market'、date-insensitive 另標不可逐日);full_market_sync.verify 同步。scope 欄更新隨 catalog 重建落地。
- **驗證**:3/3

### 執8. 〔medium·doctrine-drift〕catalog 動態重算原則
- **檔**:/home/hugo/project/augur/src/augur/ingestion/sync.py
- **問題**:「存原料、動態重算最優模式(fetch_mode 不寫死、不凍結)」與「登錄失效 → 引擎 adaptive fallback 重探並回寫」兩條憲章 catalog 描述皆與 code 不符:(1) catalog.build 把 optimal_mode 結果凍結寫入 fetch_mode 欄,sync._catalog_plan 直讀凍結欄位、不從原料即時重算——設計檔 §3.3 明言「fetch_mode 不寫死…由引擎即時算」;(2) 全 codebase 無任何 catalog 表回寫點在 catalog 模組之外——adaptive fallback 存在但「回寫」未實作。
- **證據**:憲章 v1.22.0 catalog 邊界段原文;reports/augur_metadata_catalog_design_20260615.md:66-67(§3.3);catalog/__init__.py:353(meta['fetch_mode']=optimal_mode 後 upsert)、:234 DDL 註解「派生:見 optimal_mode」;sync.py:269-277 SQL 直讀 fetch_mode(2026-07-04 複驗仍在,註解自承「不 import catalog 避循環」);grep 'UPDATE|INSERT dataset_catalog' 全 src/scripts 僅 catalog 模組內。
- **修法**:執行層擇一對齊:(a) _catalog_plan 改讀原料欄(n_stocks/n_dates/frequency/data_id_source/excluded)以共用純函數即時算 mode,fetch_mode 欄降為人看視圖,並在 fallback 成功後回寫;或 (b) 若判定「build 時重算+快取」即為意圖,則修憲章與設計檔文字——先報告供用戶擇路。
- **驗證**:3/3

### 執9. 〔medium·doctrine-drift〕audit/evaluation IC 顯著性口徑
- **檔**:/home/hugo/project/augur/src/augur/audit/feature_diagnostics.py
- **問題**:兩個面向人的顯著性顯示面仍裸用 iid effective_t,違 CLAUDE #11「IC 顯著性禁裸用 iid effective_t(重疊窗高估、審查 G8)」:(1) 五鏡輸出欄 ic_eff_t 取自 metrics.summarize 的 iid t,run_feature_audit.py 以「Eff-t」欄呈現供人合判(verdict 邏輯未用故無自動誤刪,但誤導人工裁定);(2) run_evaluation.py 基準階梯 headline 只印 iid t、無 HAC 對照。metrics.effective_t_hac(Newey-West)已存在,提拔關卡工具 verify_candidate_promotion.py:108 有用,僅此兩面未接。
- **證據**:(合併稽3/稽4)feature_diagnostics.py:130 'ic_eff_t': sf[f].get('effective_t') 與 run_evaluation.py:45 印 s['effective_t'](2026-07-04 複驗兩處仍在);metrics.py:80(iid t=mean/std×√n)vs :86-108(effective_t_hac docstring 自述「iid 高估顯著性,審查 G8」);scripts/run_feature_audit.py:67 印 Eff-t 欄;CLAUDE.md #11 條文。
- **修法**:single_factor_ic 對 per-panel IC 加算 effective_t_hac,five_mirror 輸出改帶 ic_eff_t_hac(iid 值可並列但標名 iid);run_feature_audit.py 表頭改印 HAC t;run_evaluation.py 輸出加印 effective_t_hac(或將 iid t 標示為 raw-t 非顯著性判準),與提拔工具口徑一致。
- **驗證**:3/3

### 執10. 〔medium·doctrine-drift〕ingestion/FinMind 三層防護
- **檔**:/home/hugo/project/augur/src/augur/ingestion/finmind.py
- **問題**:4 個 metadata endpoint(list_datasets/translation_datasets/translation/datalist)繞過 _protected_get:僅有 _quota_gate+_pace 兩層,缺 #17 三層防護之第 3 層(403 長冷卻/honor retry_after/退避重試)。後果:(a) 403/限流時靜默回 []——daily_datasets() 靜默變空清單(sync_all 無聲跳過全部 dataset)、translation 空集被誤當「查無」寫入 catalog;(b) list_datasets 之 resp.json() 無 try——非 JSON 回應(502 HTML)噴裸 ValueError 而非 FinMindError。translation docstring 自稱「與 data fetch 同一防護(#17)」與行為不符。
- **證據**:2026-07-04 複驗:finmind.py:202/215/230/244 四處仍直呼 requests.get(:202 resp.json() 無 try);對照 _protected_get(:120-158)才有 403 QUOTA_COOLDOWN/retry_after/退避。doctrine:原則精華 #17 ENFORCE 三層+403 長冷卻保險網。
- **修法**:4 函式改經 _protected_get 發請求(_RETRY_STATUS 不含 422,探測用 422 body 照樣返回、解析不受影響),使 metadata call 與 data fetch 真正同一防護;translation docstring 即與行為相符。
- **驗證**:3/3

### 執11. 〔medium·doctrine-drift〕features/chip E 類真零前提防呆
- **檔**:/home/hugo/project/augur/src/augur/features/chip.py
- **問題**:E 類真零(無事件填 0)之宣告前提「3 表 sync 完整至 as-of」只在註解宣稱、code 未強制:_table_covers 只查 min(date) <= panel(起始側),不查 max(date) 是否到 panel(近端側)——若對超過源表 sync 進度之新 panel 建面板,「無列」會被當真無事件填 0(捏造零、違 #1)。現況資料未違(3 表 max=2026-06-16/18/16 > 最新 panel 2026-05-31),屬結構性單邊防呆缺口;build_feature_panel.py --panels 可指定任意未來面板日,無護欄。
- **證據**:(合併稽4/稽8)chip.py:41-43 _table_covers 僅 SELECT min(date)(2026-07-04 複驗仍在);chip.py:23-24/138 docstring 前提「sync 完整至 as-of(實證 2026-06-25)」僅為一次性註記;DB 實查 3 表 max(date) vs feature_values 最新 panel 2026-05-31(latent)。
- **修法**:_table_covers 同時查 max(date),要求 max >= panel_date(或 panel − 小容忍)才允許真零、否則該 E 特徵缺列不填 0——把已聲明前提從註解變成機械 gate(現有面板值不變)。
- **驗證**:3/3

### 執12. 〔medium·bug〕依賴宣告
- **檔**:/home/hugo/project/augur/pyproject.toml
- **問題**:兩個有實際 import 的套件完全未宣告於 pyproject:(1) sentence_transformers(philosophy 檢索與 2 支 embed 腳本用)——deep extra 只列 torch,而 torch 反而無任何直接 import(僅傳遞依賴);(2) shap(五鏡鏡④ TreeSHAP 用)。fresh install 後 philosophy 檢索/embed 與 feature 稽核鏡④皆 ModuleNotFoundError。附帶決策項:xgboost/catboost/polars 三包宣告為硬依賴但全 codebase 零 import(可能為 F3 預留,去留屬決策層)。
- **證據**:(合併稽7 三條)import 點:src/augur/philosophy/retrieval.py:37、scripts/embed_knowledge.py:53、scripts/embed_philosophy_chunks.py:37 皆 from sentence_transformers import;audit/feature_diagnostics.py:83 import shap;2026-07-04 複驗 pyproject.toml:dependencies 含 polars/xgboost/catboost、deep=["torch>=2.2"]、無 sentence-transformers/shap;grep 全 codebase import torch/xgboost/catboost/polars 零命中;本機 .venv 實測兩包 import → ModuleNotFoundError(稽7)。
- **修法**:sentence-transformers 加入 deep extra(與「重型 transformer 隔離安裝」語意一致);shap 加入 dependencies 或與 lightgbm 診斷鏈同放一 extra;xgboost/catboost/polars 由用戶裁決保留(註明 F3 預留)或依 #3 移出、F3 動工再加回。
- **驗證**:3/3

### 執13. 〔medium·doctrine-drift〕測試覆蓋
- **檔**:/home/hugo/project/augur/src/augur/advisor/guard.py
- **問題**:advisor guard(防幻覺機械閘)零測試:guard.py docstring 自稱「誠實率 100% 之機制保證非自律」、憲章 v1.21.0 已將機械閘入憲為架構不變式,但 guard/guard_empty_retrieval/guard_definition 三閘全是純函數(regex+集合比對)卻無任何單測——閘本身的正確性只靠自律,與其存在理由自相矛盾;regex 回歸(_FUTURE_LEAK/_REVERSE 改壞)會靜默放行。
- **證據**:2026-07-04 複驗 tests/ 僅 6 檔(test_finmind/fred/generic_schema/ingest/philosophy_isolation/reconcile),無 test_guard;guard.py 全文為無 DB/API 依賴之純函數;憲章修訂歷程 v1.21.0 行明載機械閘入憲。isolation 測試只保證「管線不 import advisor」,不測 guard 行為。
- **修法**:新增 tests/test_guard.py:① 引文逐字(庫內過/潤飾攔)② 數字 ∈ payload 白名單 ③ _FUTURE_LEAK/_REVERSE 正反例 ④ 檢索空固定誠實句 ⑤ 定義 source_locator 課責。純函數、無外部依賴,clean-room 可直接落地。
- **驗證**:3/3

### 執14. 〔medium·doctrine-drift〕測試覆蓋
- **檔**:/home/hugo/project/augur/src/augur/evaluation/metrics.py
- **問題**:evaluation 整包(metrics/label/walkforward/cross_section/portfolio/baseline)零單測,其中 effective_t_hac 是 CLAUDE #11 點名之提拔關卡唯一合法顯著性工具——此統計函數若實作有誤會系統性污染所有特徵提拔判決,但無任何測試驗證其對自相關序列確實收縮 t 值(HAC < iid)、Bartlett 核與 lag 經驗式正確。label/walkforward 之 anti-leakage 不變式同樣無回歸測試。
- **證據**:2026-07-04 複驗 tests/ 目錄無 test_metrics/test_label/test_walkforward/test_evaluation;metrics.py:86 def effective_t_hac 存在且 docstring 自載「iid effective_t 高估顯著性,審查 G8」;CLAUDE.md #11 明文指定此函數為關卡工具。
- **修法**:新增 tests/test_metrics.py:合成 AR(1) 正自相關 IC 序列驗證 effective_t_hac < iid effective_t、白噪音下兩者近等、lag 經驗式邊界(n 小);並補 label/walkforward 最小 anti-leakage 回歸測試(as-of 切點後資料不得進訓練窗)。純 numpy 合成資料、無 DB 依賴。
- **驗證**:3/3

### 執15. 〔medium·script-29〕scripts/metadata-annotation
- **檔**:/home/hugo/project/augur/scripts/annotate_schema_comments.py
- **問題**:違 #29a + #29b/#12 三重:(1) 任何 cwd ≠ repo root 執行即裸 IndexError traceback(相對路徑 glob 'reports/augur_generic_ingester_schema_catalog_*.md');(2) 欄/表中文來源仍是 reports/ markdown 快照+in-file 硬編 dict(TABLE_ZH/OWN_COL_ZH),但 DB catalog 已是完整 SSOT——dataset_catalog.table_name_zh 95/95、column_catalog.column_name_zh 754/754 全有值;(3) 指令矩陣仍教過時 'PYTHONPATH=src venv/bin/python' 前置。
- **證據**:實跑(稽6):cd /home/hugo && venv/bin/python scripts/annotate_schema_comments.py → 'IndexError: list index out of range' at load_catalog(在 db.connect 前爆);2026-07-04 複驗 :55 glob 相對路徑仍在;psql:dataset_catalog 95|95、column_catalog 754|754 中文名全有值;line 13 指令矩陣原文。
- **修法**:改讀 DB catalog(table_name_zh/column_name_zh+zh_source)取代 markdown glob 與 in-file dict;指令矩陣改 'python scripts/annotate_schema_comments.py';路徑若仍需檔案一律經 config.PROJECT_ROOT。
- **驗證**:3/3

### 執16. 〔medium·script-29〕scripts/philosophy-knowledge
- **檔**:/home/hugo/project/augur/scripts/seed_world_philosophers.py
- **問題**:#29b 殘留:4 支哲學層 script 仍在 repo 內硬編策展資料——seed_world_philosophers.py PHILOSOPHERS 101 筆(中文名/生卒/國籍/簡介,由 AI 記憶整理;姊妹作 seed_wikidata_philosophers.py 標頭自承『不靠 AI 記憶窮舉(會漏/會編造)』即為其翻案)、fetch_gutenberg_classics.py TH 26 筆思想家傳記+GUTENBERG 50 筆書單、fetch_public_domain_classics.py CLASSICS 8 部、fetch_chinese_classics.py CLASSICS 12 部。2026-07-02 refactor(46ae2b5、b956a40)已為同一理由刪 7 支 seed script+data/philosophy/*.json,這 4 支漏未收斂。
- **證據**:AST 掃描全 scripts literal 常量(稽6):seed_world_philosophers.py:18 List n=101、fetch_gutenberg_classics.py:24 Dict n=26/:55 List n=50、fetch_public_domain_classics.py:30 List n=8、fetch_chinese_classics.py:27 List n=12(皆親讀確認為策展資料非參數);git show b956a40 --stat:刪 3 json+3 seed script,訊息『以 acquire/promote 取代 seed 腳本,移除靜態資料檔案』;46ae2b5 刪 4 支同類。
- **修法**:同已批准之 #29b 模式收斂:策展清單轉 manual_curation 傳輸工件經 acquire_knowledge --source manual_curation 入 knowledge_staging,script 退役(內容已落 DB、不需重抓);傳記類欄位以 DBpedia/Wikidata 實證版覆核;是否保留供考古由用戶過目後定(#19)。
- **驗證**:3/3

### 執17. 〔low·doctrine-drift〕audit/#7 未定案緩衝
- **檔**:/home/hugo/project/augur/scripts/reconcile_audit.py
- **問題**:#7 ENFORCE 列三類「未定案/非穩定期差異可接受」:(i) 當日結算中、(ii) 季頻最新季發布/重編、(iii) PriceAdj 隨未來除權息回溯重算。code 僅實作 (i) 之 by-date 版(UNSETTLED_BUFFER=2 只在 kind=='by-date' 生效)與 FRED Tier A restatement 容忍;31 張 roster-scoped 日頻籌碼表(同樣有次日校正曝險)無未定案排除,(ii) 因 full-history scope 從未產生而無處落地,(iii) PriceAdj 全史 VM 容忍完全未實作(除權息發生後對帳將 VM 風暴)。方向保守(假 FAIL 非假 PASS)、heal 可修,但與 #7「非紅旗、非 sync bug」分類意圖有距。
- **證據**:原則精華 v1.7.1 #7 ENFORCE 第三點;reconcile_audit.py:28 UNSETTLED_BUFFER=2(2026-07-04 複驗仍在)、:106 僅 by-date 分支排除、:89-92 roster-scoped 分支無 unsettled 處理;reconcile.py:195-249 reconcile_per_stock 僅 dbmax 窗上限;grep PriceAdj 容忍邏輯全 repo 無。
- **修法**:(a) roster-scoped 分支同套 _unsettled 排除;(b) full-history 分支落地時內建「排最新一季」;(c) PriceAdj 對帳採「以抓取時點 API 當前值為準」註記——VM 出現時報告標註疑似除權息回溯、指向 heal 重抓而非紅旗。
- **驗證**:3/3

### 執18. 〔low·bug〕audit/reconcile MIS 盲點
- **檔**:/home/hugo/project/augur/src/augur/audit/reconcile.py
- **問題**:reconcile_by_date 與 reconcile_per_stock 的比對範圍取自「該表自身的 DISTINCT stock_id」而非真名冊(sync.ROSTER_TABLE):整股缺漏(roster 股在該表 0 列)之 API 列被過濾掉或根本不迭代 → 整股級覆蓋缺口永遠不會出現在 missing_in_db;註解自稱「只比 DB roster 內個股」實為「只比該表已有之股」,兩者混同。屬偵測盲點非假 PASS(完整性另有 as-of 判準把關),但 #7 之 missing_in_db 類別對整股缺漏失明。
- **證據**:reconcile.py:131-136(roster_ids=SELECT DISTINCT stock_id FROM 該表自身)、:149(api 過濾至 roster_ids)、:211-212(per_stock 迭代該表 DISTINCT stock_id);sync.ROSTER_TABLE(TaiwanStockInfo)存在而未用。
- **修法**:roster 來源改 sync.ROSTER_TABLE(與寫入端同一 roster);或至少 docstring 明示「以表內既有股為 scope、整股缺漏由完整性判準另管」消除註解與行為混同。
- **驗證**:2/3

### 執19. 〔low·stale-comment〕ingestion/操作值 SSOT
- **檔**:/home/hugo/project/augur/src/augur/ingestion/finmind.py
- **問題**:MIN_INTERVAL 註解自相矛盾:finmind.py:38 記「2026-06-20 0.7→0.9」且 code 值=0.9,但 :39 結尾仍寫「→ 現操作值 0.7」。憲章/原則精華 #17 明定「當前值……見 finmind.py」=此處為 operational 值之 SSOT 所在,自相矛盾破壞可溯源(#15)。
- **證據**:(合併稽2/稽8)2026-07-04 於 HEAD b0216f5 複驗:finmind.py:39 仍含「→ 現操作值 0.7(#27 試錯逼近最佳奇異點…)」;import 實測 f.MIN_INTERVAL=0.9;git 2f5fa6e「MIN_INTERVAL 0.7→0.9」證實 0.9 為現值。【合併註記】原始 77 條 → 輸出 30 條(涵蓋 47 條原始項,其中 17 條為跨稽核重複已併入保最強證據)。捨棄 30 條:1 條失效——稽1 頭號發現「finmind.py committed merge conflict @a7a5ee5」於本合併階段實測已修(HEAD=b0216f5、git grep 全 src 無衝突標記、import OK),按規剔除;pe_ratio winsorize(known 在案,3 條重複)與 walkforward docstring(2 條重複)整組讓位;其餘 24 條為 low 級微修——憲章 philosophy 表清單漏 2 表、標頭版本釘批次、6 支缺 🎯 標記、SHMM/caffeinate/OUT_OF_UNIT 過時註解、HORIZONS 死常數、catalog build docstring、五鏡/isolation/framework 6表 docstring 漂移、latent portfolio asof=False 崩潰與 long_short 空腿成本、canonical_features 同名雙口徑、超參雙寫、conditional gate 已併入 core_gate 條、data_id 巧合入鍵、fred 無 pace、intraday 前瞻封閉、_fmt_pg 重複、verify_code_reports 硬編路徑、no-arg DB 寫、test_reconcile 待補(known)、daily_maintenance 命名——皆有據但價值低於保留門檻,可於例行清理批次處理。
- **修法**:finmind.py:39 尾句改「→ 前操作值 0.7、現值 0.9(見上行 2026-06-20 調整)」或刪具體數字改指向左側 code 值(值以 code 為準,防再漂移)。
- **驗證**:3/3

## 決策層(待用戶拍板)

### 決1. 〔high·doctrine-drift〕ingestion/FRED PIT
- **檔**:/home/hugo/project/augur/src/augur/ingestion/ingest.py
- **問題**:FRED PIT 雙軌(#8)只存在於 code、從未落地 DB:fred_series 實表仍為 pre-PIT 舊 schema(僅 series_id/date/value、無 realtime_start;PK=(series_id,date);12 series、84,756 列、最後寫入 2026-06-17),ingest_fred docstring 宣稱「強制 (series_id,date,realtime_start) 複合鍵」與 DB 事實不符——require_keys 因「PK 首建固定」(ensure_table 沿用既有 PK)對既有表永不生效。且全鏈無守門:直接跑 scripts/sync_macro.py,Tier B vintage 多版會在 upsert 批內去重+ON CONFLICT(series_id,date) 下靜默塌版=vintage 流失、realtime_start 語意錯亂(錯誤 PIT)。macro.py 31 檔 PIT sync 從未執行。
- **證據**:唯讀 psql 實查:information_schema.columns(fred_series)=series_id/date/value(無 realtime_start);pg_index PK=(series_id,date);count=84756/12 series;data_audit_log max(logged_at)=2026-06-17。code:ingest.py:103-110(require_keys 僅首建有效)、generic_schema.py:188-242(表存在→沿用 DB PK)、:257-259(批內去重保留最後一筆)。sync_macro.py:10-11 header 自承「舊表須先一次性 DROP 重建」但 main() 無 PK 前置檢查;grep 全 repo 無 fred_series 重建 script;audit/reconcile.py:350 docstring 亦寫錯 PK。
- **修法**:決策層:一次性 DROP fred_series + 跑 scripts/sync_macro.py 重建(31 檔 FRED 放量,需用戶授權 #24)。附帶執行層守門(可先行):ingest_fred/sync_fred 落地前檢查 db_primary_key('fred_series')——PK 不含 realtime_start 即拋錯拒落地,把文字警告變程式強制。
- **驗證**:3/3

### 決2. 〔已知在案〕〔high·bug〕ingestion/raw 既有資料
- **檔**:/home/hugo/project/augur/src/augur/ingestion/sync.py
- **問題**:(已知在案)TaiwanStockDividend 仍為塌列狀態:實表 PK=stock_id 單欄,歷年股利事件被 ON CONFLICT 互蓋只剩最後一筆——每股僅 1 列、全史遺失。code 側已根治防再發(_per_stock_sync 強制 require_keys=('date',)),但既有表因 PK 首建固定仍塌、資料未重抓。
- **證據**:(合併稽1/稽2/稽8 三重覆確認)唯讀 psql 實查:count(*)=2,411=count(DISTINCT stock_id)(每股恰 1 列、2330 僅 1 列);pg_index PK=[stock_id](對照健康表 TaiwanStockPrice PK=[stock_id,date]);sync.py:196-199 註解記載 2026-06-28 實證與 require_keys=('date',) 修法已入 code。
- **修法**:在案決策層待辦:DROP 該表後以修正後 per-stock sync 路徑重抓全史(#7 correction=重跑正常 sync;API 放量需授權排程 #24),重抓後過對帳;不 hand-patch(CLAUDE #12)。
- **驗證**:3/3

### 決3. 〔medium·doctrine-drift〕features/anti-leakage 口徑(月營收發布日 gate)
- **檔**:/home/hugo/project/augur/src/augur/features/release_lag.py
- **問題**:月營收 gate 假設 `date`=資料期間月份,但實測 TaiwanStockMonthRevenue.date=公告月(資料月+1):gate 實效=資料月+2 個月+15 日,monthly_revenue_yoy 全 35 面板系統性多滯後約一個月。方向保守(非偷看未來),但 doctrine 描述與資料事實不符且損失時效;同一 gate 亦被 verify_fundamental_candidates.py/run_cross_table_interaction_scan.py 引用。附帶:audit/field_correlation.py compute_leadlag 之 revenue 腿直用 date join+ffill、未過任何 release 慣例,與其 docstring「predictor 用 ≤t」自相矛盾(探索性模組、生產不受影響)。
- **證據**:(合併稽8 兩條)release_lag.py:1-9 docstring 稱「月營收的 date 是資料期間(月份)…月 M 之 release=次月 15 日」(2026-07-04 複驗仍在);DB 唯讀實查:2330 之 date=2026-06-01 列 revenue_month=5/revenue_year=2026;全表檢核 extract(month FROM date)-revenue_month NOT IN (1,-11) → 0/474,246 列(date 恆=資料月+1)。故 revenue_release_date('2026-06-01')=2026-07-15,而 5 月營收法定 6/10 已公開。field_correlation.py:60(revenue SQL 直用 date)+:77 _FFILL+:184 docstring。
- **修法**:決策層裁定後:revenue_release_date(d) 改為同月 15 日(仍保守於法定 10 日),同步修 release_lag.py/panel.py 註解,並重建 monthly_revenue_yoy 全 35 面板+重跑提拔/經濟驗證(特徵值會變=資料語意變更)。field_correlation 之 revenue 腿同步平移或 docstring 明示未過 gate。
- **驗證**:3/3

### 決4. 〔medium·doctrine-drift〕philosophy/chunk 溯源不變式
- **檔**:/home/hugo/project/augur/scripts/build_philosophy_chunks.py
- **問題**:1,189/63,601 個 philosophy_chunk(涉 41 個 text_id)相對現行 work_text 已 stale——char_range 溯源不變式(chunk.content == content[char_start:char_end])不成立;其中 57 個 chunk 連子字串都不是,即檢索可回「非現行原文逐字」引文且 advisor guard ①(引號 ⊂ citation.text)照樣放行,#1 逐字可溯源鏈對此 57 chunk 斷裂。根因=chunk builder resume 以「該 text_id 已有 chunk 即跳過」,對 work_text 事後再清洗(wikitext -{}- 轉換標記剝除、CRLF 正規化)無感知。
- **證據**:psql 全量實查:62,412/63,601 通過 0-based substring 等式、1,189 不過(0 個通過 1-based,排除口徑問題);不過者中 1,132 仍為子字串(僅 offset 錯)、57 非子字串。樣本 chunk_id=24/84/150/257(道德經/六韜/三十六計)content 含 -{谷}-、-{斗}- MediaWiki 標記而 work_text 已清洗,且 char_end > length(content);chunk_id=765 含 \r 而源文已正規化。builder line 107 SELECT DISTINCT text_id resume 邏輯。
- **修法**:決策層(需重建資料、本地零 API):對 41 個受影響 text_id 刪 chunk(embedding 隨 FK CASCADE)→ 重跑 build_philosophy_chunks.py + embed_philosophy_chunks.py;並(執行層)為 resume 補內容漂移偵測(比對 max(char_end)≤length(content) 或存 content hash)。
- **驗證**:3/3

### 決5. 〔medium·doctrine-drift〕universe 層 / 憲章第三部
- **檔**:/home/hugo/project/augur/src/augur/universe/core_gate.py
- **問題**:生產核心股名單之選拔判準已超出憲章描述:憲章 universe 段稱核心=全部 source-pure 完整股、「無評分、無排名上限」、「任一面板任一特徵缺值即排除」,但 code 另有 (a) 流動性分位地板 liquidity_pct、(b) conditional 產業豁免,且 2026-06-30 生產 build 兩者皆啟用——憲章其後升版均未承載此判準變更。附帶執行層小項:conditional gate 要求 count==len(panel_dates) 與 universal gate 之 available-combos(G9)語意不對稱,若 conditional 特徵任一 panel 全市場缺席會誤清非豁免股(現況 latent:monthly_revenue_yoy 覆蓋 35/35 panel)。
- **證據**:(合併稽1/稽4)core_gate.py L127-143 流動性 gate、L145-153 conditional 豁免(2026-07-04 複驗 DDL 欄 liquidity_pct/conditional 仍在);DB 實查 core_universe_build_meta build 1-2(2026-06-30):liquidity_pct=25、threshold=14.929、conditional=monthly_revenue_yoy=金融保險|金融業、core_count=344;憲章 v1.22.0 universe 段無流動性/豁免字樣;core_gate.py:117-123 universal 用實際可用組合數 vs :145-153 conditional 綁 len(panel_dates)。
- **修法**:決策層二擇一:(a) 憲章 universe 段+PHASE 8 承載「流動性分位地板+conditional 結構性豁免」為正式判準(升 minor);或 (b) 認定生產 build 越界、以純完整度重建 core(universe 規模改變、下游 eval 全變)。執行層可先行:conditional 要求數改為逐 panel 實際可用數(對齊 G9)。
- **驗證**:3/3

### 決6. 〔medium·doctrine-drift〕catalog metadata 時效
- **檔**:/home/hugo/project/augur/src/augur/catalog/__init__.py
- **問題**:dataset_catalog 表級 metadata 大規模停留在「落地前 probe 時代」:82/84 表 source_provenance='probe'、last_verified=2026-06-16,但這 82 表今皆已落地;憲章設計是已落地表全讀 DB 真值。後果已實證:TaiwanStockFinancialStatements 記 frequency='daily'、n_dates=8442(DB 實查 distinct date=138)、TaiwanStockMonthRevenue 'daily'/5971(實際 293)——probe 路徑 n_dates=None 時 _infer_frequency 直接 default 'daily' → 季/月頻表永不被標 quarterly/monthly → reconcile_scope 'full-history'(#7 低頻全史對帳設計意圖)從未產生。
- **證據**:psql:SELECT source_provenance,count(*) FROM dataset_catalog GROUP BY 1 → probe=82, DB=2;SELECT count(DISTINCT date) FROM "TaiwanStockFinancialStatements" → 138 vs catalog n_dates=8442;DB scope 僅 by-date/roster-scoped/by-dim-id 三種;TaiwanStockNews scope 寫入(2026-06-16)早於 coverage 邏輯入 code(git 7650167, 2026-06-18);catalog/__init__.py:548(無 n_dates → 'daily')、:552-557(daily cadence 估 8442)。
- **修法**:決策層:授權後全量重跑 catalog.build(landed 表多為 DB 讀+少量 API datalist/refine,屬放量須授權;重建前先 ANALYZE 大表)。注意連動:重建後 n_dates 修正會翻轉部分 optimal_mode、frequency=quarterly 會產生 'full-history' scope——須先完成 driver 之 full-history/market 分支(見對應發現)並人工複核 fetch_mode 翻轉。
- **驗證**:3/3

### 決7. 〔medium·naming〕features/chip 命名語意
- **檔**:/home/hugo/project/augur/src/augur/features/chip.py
- **問題**:gov_bank_net_buy_60d 名實不符(獨立新發現,同類於已知 lending_fee_rate):「官股 60 日淨買」實作=最近 ≤60 個「官股有交易之事件日」(SQL LIMIT 60、無任何日期下界),非 60 交易日/日曆日——稀疏股之窗跨度可達 3 年、<60 事件日之股為全史累計。
- **證據**:(合併稽4/稽8 獨立 DB 覆核一致)chip.py:94 _GOVBANK_SQL 'GROUP BY date ORDER BY date DESC LIMIT 60' 無 date 下界(2026-07-04 複驗仍在)、:159-163 註明「累計有幾日算幾日」;DB 實查(兩次獨立):~2,760 檔 ≥60 事件日之股,最近 60 事件日日曆跨度 median 86-88 天(≈60 交易日、多數 OK)、p90 104-113 天、max 1,065 天——約一成股跨度遠超名義窗。
- **修法**:決策層擇一:(a) SQL 加日期下界(如 panel_date − 86~90 日曆日 ≈ 60 交易日)使名實相符——值會變、需重建該欄+重走提拔口徑確認;(b) 保持語意、改名(如 gov_bank_net_buy_60ev)明示事件日口徑。
- **驗證**:3/3

### 決8. 〔已知在案〕〔medium·naming〕features/chip 命名語意
- **檔**:/home/hugo/project/augur/src/augur/features/chip.py
- **問題**:(已知在案)lending_fee_rate_mean_30d 名實不符:宣稱「近 30 日費率平均」,實作=最近 100 筆借券成交紀錄之平均(不限日期、每日可多筆),實際窗跨度中位 1.5 年;另名稱示意「借券費率」放空成本,實際源自 TaiwanStockSecuritiesLending.fee_rate(借券系統議借成交語意),名稱與資料語意雙重落差;屬 E 類真零設計(無事件填 0.0)。
- **證據**:(合併稽1/稽4/稽8)chip.py:87 _LEND_SQL 'ORDER BY date DESC LIMIT 100' 無 30 日窗(2026-07-04 複驗仍在;註解自稱「近 30 日各筆 fee_rate 平均」);DB 實查:988 檔 ≥100 筆之股其最近 100 筆日曆跨度 median 546 天、p90 2,671 天、max 5,549 天(另一稽核獨立抽樣 0050=471、006206=4082 天,一致);chip.py:154-157 無事件填 0.0。
- **修法**:在案決策層待辦:改為 date > panel−30(或 45)日之窗後重建該特徵並重驗;或改名符實(併考慮換源表以符「借券費率」語意);未拍板前於 catalog/報告明標語意。
- **驗證**:3/3

### 決9. 〔low·doctrine-drift〕catalog↔治權檔 SSOT 方向
- **檔**:/home/hugo/project/augur/docs/系統架構大憲章_v1.22.0.md
- **問題**:憲章 catalog 段「datasets_zh.md 由此表生成(表=SSOT、md=人看視圖)」與現實相反且無工具支撐:全 repo 無任何由表生成 md 之程式,實際資料流是 datasets_zh.md(code 內註解自稱「單一策展 SSOT」)→ seed_table_zh/seed_column_zh → 灌入 catalog;中文名非 API-derivable,md 作 curated 輸入有其正當性——但同一系統內「表=SSOT」與「md=策展 SSOT」兩說並存、生成方向文字與 code 相反。
- **證據**:憲章 catalog 職責段原文;grep -rln datasets_zh → 僅 catalog/__init__.py(:124-193 解析 md 寫 DB)與 build_catalog.py(註解「可由表生成」,無生成 code);catalog/__init__.py:121 註解「datasets_zh.md(單一策展 SSOT『## 補充』段)」。
- **修法**:決策層擇一:(a) 補一支由 dataset_catalog/column_catalog 生成 datasets_zh.md 之本地腳本,令憲章描述成真(中文名策展段保留為輸入);(b) 修憲章文字為「fetch 元資料以表為 SSOT;欄/表中文名以 md 策展為源、seed 入表」。涉治權檔判準取向,報告供用戶拍板。
- **驗證**:3/3

## 否決紀錄(對抗驗證濾除)

- /home/hugo/project/augur/scripts/verify_candidate_promotion.py: #29c『通用可重用、擴充靠參數』落差:CLAUDE #11 指定 verify_candidate_promotion.py 為第 4 道提拔關卡標準工具,但其候選名單硬編在 code(CANDS,argparse 僅 --h/--see (votes 0/3; 推翻。發現引用的行號事實皆屬實（CANDS 於 :27、僅 --h/--seeds 於 :90-91、signal 變體 --cands 於 :102、lens 硬編 :25-42、CLAUDE.md v1.16 #11 行 33 指定該工具），但其核心因果主張與 proposed_fix 效益主張經實查不成立，且所指結構為 doctrine 實際允許的設計，非 drift：(1) 加 --cands 無法使工具「真正通用」——第 4 道關卡必須以 as-of 口徑「重算」候選值，各候選公式是候選特定 code（verify_candidate_promotion.py:40-70 _compute_asof_candidates 寫死 PBR ≤t 自身百分位與 inst/gov 背離 z；被發現當作合規範本的 verify_signal_promotion.py 之 --cands 其實只在 _candidate_values(:53-65) 三個硬編公式中「挑選」，未知候選直接 raise ValueError——新候選照樣得改碼）。「含 fc 候選解析」亦是封閉集（src/augur/audit/feature_candidate.py:28 CANDIDATES 為固定 4-tuple、compute_candidates 硬編公式）。故「下一個候選要複核就得改碼」對含 --cands 之變體同樣成立，signal 有參數＝通用、candidate 無＝drift 是假對比。(2) #29 自身文字區分「資料/參數擴充」與「新邏輯本質是 code」：#29b 明文「新來源協定才寫新 adapter、新 entity_type 才加 mapping 函式（本質是 code,合理）」；#29c 的合併範例正是 seed 批次檔→引擎（擴充靠 DB 資料列與參數）。候選公式非 DB 資料列可表達，屬「本質是 code」側。且 #29 入憲當日的專項合規改造 commit 46ae2b5（訊息明書「守 CLAUDE v1.14 #29」、涵蓋 61 支）有碰 verify_candidate_promotion.py（加 _bootstrap、升「執行指令矩陣」）而僅收斂 seed 家族——現狀是該次 #29 合規詮釋下的既定結果，非漂移遺漏。(3) 「同型第 4 道 script 一再另立」非未經允許的增生：CLAUDE #11 明文「詳法 SSOT＝reports/augur_feature_discovery_methodology_20260626.md §四」，該 SSOT 工具鏈對映（:140）明列漏斗 4 為工具家族 verify_candidate_promotion/verify_lens_promotion/verify_interaction_candidates/verify_matthew_candidates（memory augur-feature-toolkit 同載），家族制即文件化設計；verify_lens_promotion 更是批次提拔＋剪枝（prod_full/prod_pruned/promoted 三向比較）之不同形狀，非可直接參數合併之同型。(4) 硬編 CANDS 兼具已結案戰役之可溯源記錄功能（commit e36de87：該 2 候選走完漏斗後已淘汰），docstring 明書其特定範圍。綜上：claim 的違規定性（#29c drift）不成立、evidence 對比為假二分、proposed_fix 允諾的「真正通用」效益經事實檢驗無法兌現——至多是無害的便利性建議，不構成合規稽核發現。)
- /home/hugo/project/augur/src/augur: (已知在案:F3 未建)憲章第三部 4·model(src/augur/models/、model_registry 表)與第五部 PHASE 10「models train → artifacts + registry」完全無 code  (votes 1/3; 事實面全數屬實(實查:src/augur 無 models/、scripts 無 train 入口、psql information_schema 無 %model% 表、憲章 line 101-105/202 確有描述、baseline.py docstring 與 test_philosophy_isolation.py:17,26-27 皆如 evidence 所述),但所指非違規:(1) README.md(治權五檔之一)line 14「`models`（F3）未建（規劃中）」與 line 36「models(F3 未建)」已明文標註建置狀態,治權文件集合對現狀無失真——非 doctrine-drift,是已揭露的 roadmap 里程碑;(2) 憲章第三部(line 71「系統怎麼建」)與第五部(line 187「從零重建一律照此序列」)本質是目標架構藍圖/重建序列,未走到 PHASE 10 是進度狀態非違規;(3) claim 之「PHASE 11 evaluation 以 baseline.py 代行」誤讀憲章 line 111——validate 層邊界明定「不讀 model 層 artifacts(雙軌獨立,自做 train/predict)」,內嵌 Ridge/LGBM 是設計要求非替代品;(4) proposed_fix「在憲章標註建置狀態」與 SSOT 鐵律(憲章 line 228 任一概念只有一個權威家)扞格——建置狀態權威家已是 README;「建 F3」則屬 roadmap 排程非稽核修復。finding 自標 known=true 亦自承此為已記錄決策層待辦,不構成新的合規違規發現。)
---

## 決策層處置紀錄(用戶「照建議」2026-07-04)

- **決1 FRED PIT**:✅ 執行層守門(ingest.py `_fred_pk_ok` 拒落地舊 PK)+ FRED 重建(DROP+sync_macro,PK 含 realtime_start;FRED key 有效、量小)。
- **決2 Dividend 塌列**:⏳ 排夜批 2026-07-05 01:00(scheduled task augur-dividend-refetch-d2;FinMind free-tier 重抓、#25 最小探測先行)。
- **決3 月營收 gate 語意**:⏸ **保留待用戶單獨確認**(影響最大:改語意=重建 35 面板+重跑提拔/經濟驗證;AI 未逕改)。
- **決4 stale chunk**:✅ 刪 41 text_id 重建→stale=0;副作用=語料增長觸發全語料重切(63,601→149,111 塊)、+87k 嵌入背景跑(有益、擴知識覆蓋)。
- **決5 universe 判準**:✅ (a) 入憲 v1.24.0(流動性分位地板+conditional 豁免承載)+執行層 core_gate G9 對齊(conditional 要求數=逐 panel 實際可用)。
- **決6 catalog 時效**:⏸ 暫緩(有前置依賴=full-history driver 分支;待補後 db-only 刷新)。
- **決7/決8 命名**:✅ 語意標註(chip.py `_LEND_SQL`/`_GOVBANK_SQL` 註+標頭;full rename 漣漪 4 檔/125k 列故不改名、非 canonical)。
- **決9 md 生成方向**:✅ (b) 憲章 catalog 段校正 SSOT 分工(抓法=表 SSOT;中文名=md 策展為源 seed 入表)v1.24.0。

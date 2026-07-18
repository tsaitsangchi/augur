---
name: augur-construction-map
description: augur 專案怎麼建構的完整心智圖:治權脊椎(三敵×管線)→分層 SSOT→三敵機械化不變式→資料驅動零hardcode→fail-closed冪等;各子系統建構作法+關鍵不變式;詳版 reports/augur_construction_understanding_20260709.md
metadata: 
  node_type: memory
  type: reference
  originSessionId: c3c40e0c-7154-4936-8937-6d9ce947808c
---

**2026-07-09 全專案深讀合成(9 讀者平行讀 src ~70 模組/9565 行 + scripts ~110 支/17156 行 + 治權 4 檔 + tests 16;SSOT 詳版=`reports/augur_construction_understanding_20260709.md`)**。augur=clean-room 只用真實資料誠實預測台股相對強弱 + 橫切博學投資顧問素養層。

**建構脊椎(兩軸貫穿每層)**:WHY=三個敵人(①假資料#1 零AI幻像 ②偷看未來#8 anti-leakage ③自我欺騙#15 誠實)↔ 三基石法律;HOW=管線 `raw→feature→universe→model→validate` + 橫切(core/audit/catalog/philosophy/knowledge/advisor)。**核心信念:三敵零容忍從口號變機械不變式**(schema/型別/封閉集/AST 稽核/正則閘/DB CHECK/純函式複用結構性封死,非自律)。

**治權分層 SSOT 防漂移 #12**:靈魂 v1.5.0(WHY)/原則精華 v1.8.0(20 條法律全文 WHAT|WHY|ENFORCE)/憲章 **v1.39.0**(HOW 架構+12-PHASE+命名慣例+**第六部計畫先行/計畫完整性**,只承載框架交叉引用不複述)/CLAUDE **v1.22**/方法論報告(詳法)。原則精華在憲章~30版間維持 v1.7.1、唯 FREEZE 實質法律擴展才首次連動 v1.8.0。**⭐憲章第六部計畫完整性(v1.27.0→v1.39.0 強化 2026-07-09):所有計畫書〔含純分析〕一律須附 (a) 對應 table schema〔產表新 DDL/不產表引用既有表〕+ (b) python 程式規畫〔script·函式·角色·輸入輸出表〕、表與程式雙落實。**寫任何計畫報告必附此兩段。

**各層建構作法**:
- **raw(ingestion+core)**:sync→ingest→generic_schema→db→PG 嚴格分層;FinMind 三層限速(_quota_gate 問錶主動閘/_pace 0.9s start-rate/403 固定冷卻1800s不風暴);**資料驅動零 hardcode**(422-enum probe 取 dataset 全集、generic_schema 推斷型別/PK);零幻像由建構(API 值逐字、唯一轉換是無值映射);FRED vintage PK 強制(date,realtime_start)防塌陷。FULL_START 1990 非全史保證。
- **feature**:每模組 compute_*(cur,sid,pd)→{feat:val} 只含有限值;**missing-row 紀律**(算不出省列不 fake/zero);調整價單一基礎(自動移停牌);#8 命門 release_lag 發布日 gate(15/45/90)。
- **universe**:core_gate 四道閘;core_universe_asof point-in-time 消 survivorship。
- **model+validate**:**evaluation 數學 SSOT + models 薄殼雙軌零漂移**;誠實四關 purged walk-forward(embargo _FEATURE_LAG_TD=62/H≥252 禁)→HAC effective_t_hac(禁裸 iid)→經濟回測(net=gross−turn×cost 0.00585 #14)→deflation DSR per-period 命門(trial_ledger N 機械 count DISTINCT)。forward_returns on-the-fly 無表。IC 撐住≠可交易。
- **audit**:純 kernel+I/O orchestrator 分離;**import_isolation 三偵測面**(AST+literal+resolver)PIPELINE(features/models/universe/evaluation/ingestion/audit/catalog)禁 import FORBIDDEN(philosophy/advisor/knowledge)=素養層物理隔離;reconcile #7 對帳。
- **execution**:risk_control DD熔斷/cap/turnover 複用 portfolio._turnover/drawdown_series(零重造)。
- **knowledge**:三層 DB-driven(knowledge_source registry→acquire→staging→promote,擴領域=INSERT一列零改碼);license 白名單三處硬同步+DB CHECK;lexicon 逐字原文子串禁改寫;述詞 SSOT/契約函式/六同型 parser;vectorindex=pgvector-SSOT。
- **philosophy+advisor**:framework 策展常數 SEED+冪等 upsert 避 blanket DELETE;哲學=假說非真兆(DB CHECK 擋 AI 生成、validated_ic 須自證);**advisor 三通道(唯讀 payload⊕逐字檢索⊕lexicon)+抽象 llm_fn(v1.37.0 本機限定)+guard 五閘 fail-closed**;信念=弱 LLM 不可信→逐字原文+確定性 picks 系統注入、LLM 只白話解讀、過 guard;誠實閉集變更=憲章判準。advisor 對預測/哲學表唯讀零寫。
- **scripts(#29)**:薄 CLI 組合根(_bootstrap 首行個別可執行/標頭指令矩陣/安全無參數/單連線);複用鐵律 train/predict/revalidate 共用 evaluation helper 零雙軌漂移。三服務 advisor:8399/chat:8090/admin:8500。

**七大建構 meta-pattern**:①純 kernel+I/O 分離 ②SSOT 複用鐵律(一算法一住所)③資料驅動零 hardcode ④三敵機械化不變式(license 三同步/import_isolation/guard 五閘/trial_ledger N/per-period DSR/release_lag)⑤fail-closed 漏斗(缺資料回誠實閉集)⑥冪等 resume-safe(ON CONFLICT/SAVEPOINT/游標表/DB-driven resume)⑦命名慣例(library 領域名詞/CLI 動作動詞)。

**關鍵不變式**:COST 0.00585 · embargo 62td/H禁252 · trial_ledger N ⚠**2026-07-17 更正:非 count DISTINCT(那 6 欄是 `ix_trial_sopkey` 索引);live UNIQUE=8 欄 `trial_ledger_uq(model,horizon,top_frac,weight,feats_hash,cost,sample_since,recipe)`;N=`len(trials_pp)`=net_sharpe 列數(deflate_headline_verdict.py:99)、去重靠 UNIQUE 約束**(搞錯直接算錯 DSR 的 N) · DSR per-period · release_lag 15/45/90 · missing-row 不 fake · feats_hash sha256 sorted[:16] · guard 五閘+誠實閉集二句(變更=憲章)· license 5 白名單三同步 · as-of 2026-05-31 FREEZE。

**⭐2026-07-09 v2 對抗審查+自我迭代(20-agent pipeline、supersede 同日第一版、詳版=同報告 v2)**:核心框架升級——**augur=兩個半系統,只被 (a) PostgreSQL message bus + (b) 一個唯讀 dataclass PredictionPayload 接起來**;半-1 預測管線(features/models/universe/evaluation/ingestion/catalog/audit)、半-2 顧問知識服務(philosophy/advisor/knowledge+3 web server 8090/8399/8500),import_isolation 機械強制半-1 對半-2 零反向 import(本輪實跑 exit 0)。**對抗驗證抓到第一版真實錯誤(親驗過)**:①feats_hash「防漂移」=死碼過度宣稱(predict_asof cur_feats unused、只查 artifact↔registry 竄改非 live 漂移)②per-module 契約非統一(concentration/panel 純 price_df、macro 無 compute)③missing-row 兩 regime(P 省列/E 真零)④quota-gate 120=兩獨立值⑤FRED PK 含 series_id、_RETRY_STATUS 含 402⑥jieba floor 非 pin⑦philosophy 9 表非 6⑧DSR 操作 N=16 非 8。補齊半-2(RBAC pbkdf2 240k/蒸餾/serving 拓撲/revalidation 兩軌三態判停)。教訓:第一版純靜態讀有精度誤差、對抗驗證 against code+run tools 才抓出=#15 親驗勝於平行讀。

**一句話**:治權定 WHY/法律 → 嚴格分層 SSOT 定 HOW → 三敵零容忍全部結構機械化 → 資料驅動零 hardcode → fail-closed 冪等;每行 code 溯回 (敵人×管線層×治權)。相關:[[augur_project_overview]] [[augur-data-layer]](94表772欄四層)[[prediction-headline-undeflated]] [[investment-philosophy-framework]] [[ttai-integration-and-platform]]。

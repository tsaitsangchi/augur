---
name: augur-project-map
description: augur 專案定位與當前里程碑(2026-07-03 全專案 212 檔精讀後更新)— 治權 SSOT 版本、程式地圖(含知識/哲學/顧問層)、市場層+知識層進度、兩機狀態與 operational 約束
metadata:
  node_type: memory
  type: project
  originSessionId: b6b65aa3-b9fc-49cb-b589-2fff5a7b85de
---

augur＝只用真實資料、誠實預測台股的系統:預測各核心股未來 H 日**橫斷面相對強弱排序**(非絕對漲跌)、附 walk-forward 可信度;定位擴為「**有廣博哲學素養的投資量化顧問(博學投資大師 AI)**」(靈魂 v1.8.0)——哲學/知識=假說來源+素養解讀層、**非真兆、零量化價值、不進預測管線**。三敵人＝①假資料 ②偷看未來 ③自我欺騙;最神聖紀律＝#1 Source-Pure。靈魂成功定義＝**經濟價值(MaxDD/Calmar)非 IC**(#14)。

**治權 SSOT(5 檔、改動須跨檔一致)**:靈魂 `docs/系統核心思想_v1.8.0.md`｜法律 `docs/原則精華_v1.9.1.md`(20 條、基石 #1/#8/#15)｜憲法 `docs/系統架構大憲章_v1.46.0.md`。⚠️**版本號 2026-07-17 更正(原記 v1.4.0/v1.7.1/v1.24.0/CLAUDE v1.16 四者全過時、指向不存在檔名)**;另五治權檔已受上位 `AUGUR-MC v1.3`(Layer 0 lex superior)約束、見新檔規劃。**以下 v1.21-v1.25 為史料細節、非現行版**:(v1.21=advisor入憲;v1.22=9視角審查22條;v1.23=知識域端到端管線準則〔七段一驅、pgvector=SSOT/Milvus=可拋棄、對話單閘advise+guard、可替換接縫層;詳計畫=augur_knowhow_e2e_pipeline_plan_20260704.md〕;v1.24=稽核決策層承載〔universe 完整度兩限定:流動性分位地板+金融月營收豁免;catalog SSOT分工〕;v1.25=三級誠實固定句閉集擴二句〔(i)檢索空(ii)歸屬未驗 review_flag=true 隔離館藏;guard.py HONESTY_CLOSED_SET,分級器待W8 answer.py〕)。**v3.0 計畫13拍板點已鎖定(照建議)**:多數 baked into W1-W9;拍板3已改憲章v1.25;拍板2(en全量)待GPU+L5證需求;拍板12(item鏈)v3.x;拍板6 merge阻於無舊機dump、拍板10阻於sudo。**稽核決策層9條(2026-07-04「照建議」)**:決1FRED PIT重建(PK含realtime_start)+ingest守門、決4 stale chunk修(stale=0,副作用全語料重切63,601→149,111+87k嵌入)、決5入憲+G9對齊、決7/8命名標註、決9憲章校正=已落地;決2排夜批(Dividend 07-05 01:00)、決3保留待單獨確認(改月營收gate=重建35面板)、決6暫緩(前置依賴)｜`CLAUDE.md` **v1.29**(原記 v1.16)｜`README.md`。v1.14 之後入憲重點:**v1.15 執行省 usage × 理解 ultracode 窮盡二分**(執行層 how 省、概念定義 what/why 窮盡、有疑偏理解層)｜v1.16-1.18 哲學框架層(哲學=假說須過四道漏斗+#14「驗證活下來非大師說了算」、禁 AI 生成入庫 DB CHECK 硬擋、版權著作僅核心精神經真實文獻 citation 合規路)｜v1.19 知識層多域擴充(通用知識管線、domain 欄隔離因子鏈)｜v1.20 全文准入雙軌(哲學原典限公版;knowledge_item_text 納 CC 白名單 cc-by/cc-by-sa/cc0)。CLAUDE 新條:**#29 script 個別可執行(_bootstrap)×資料驅動不 hardcode(三層管線 knowledge_source→acquire→staging→promote、擴域=INSERT 零 code)**、**#30 平行 dump(`pg_dump -Fd -j4 -Z1` 先 ext4 後搬 drvfs;dump 期間禁 DDL 鎖風暴)**。**回答前重讀對應 SSOT、勿憑摘要**(#20 實證)。

**程式地圖(`src/augur/`)**:預測管線 7 pkg——`core`(db/config/generic_schema/schema)｜`ingestion`(finmind 限速+fred vintage+sync+ingest)｜`catalog`(dataset/column_catalog 元資料 SSOT)｜`audit`(reconcile 對帳+五鏡+feature_candidate+field_correlation)｜`features`(panel/chip/valuation/macro/concentration/phase/margin_cycle/release_lag)｜`universe`(core_gate)｜`evaluation`(label/walkforward/metrics/baseline/portfolio/cross_section)。素養橫切 3 pkg——`knowledge`(textnorm 契約+lexicon_parsers)｜`philosophy`(framework 9 表+retrieval RAG)｜`advisor`(payload/prompt/advise/guard 防幻覺閘)——與預測管線隔離=AST import-lint 測試+DB role 無 SELECT(詳 [[augur-knowledge-philosophy]])。`models/`(F3)**仍未建**(Ridge 生產模型只活在 evaluation 雙軌內、無正式 train/serve 入口)。scripts/ 69 支全 `_bootstrap` 個別可執行、無參數=安全預設。

**市場層狀態(2026-06 底定格、特徵層飽和)**:35 特徵×35 panel≈2.42M 列;headline H60 as-of Ridge rank IC +0.1418、net top10% Sharpe 1.26 vs 基準 0.96(alpha 僅 long 側);特徵層五輪探索飽和定論、**前沿=horizon×宇宙×執行配置**(H120 Calmar 3.55/擴宇宙 2.4× IC −15% 推廣);regime C1(`lead_nt_rising` 23 年驗)=風控非報酬。詳 [[augur-feature-values]]/[[augur-feature-toolkit]]。

**合規稽核波(2026-07-04,commit 4010382/tag compliance-audit-exec19)**:8視角×3懷疑者稽核確認 28 條——執行層 19 全修(label 真t+1/retrieval textnorm 契約/advise 機械閘升級/audit staging 表/chip 雙側 gate/HAC-t 顯示/framework upsert 等,85 tests 綠);**決策層 9 待拍板**:FRED PIT 從未落地 DB(重建需放量授權)、Dividend 塌列重抓、月營收 gate 實為+2月+15日(date=公告月)、1189 stale chunk 重建、universe 判準超出憲章描述、catalog 時效、gov_bank/lending 名實不符、md 生成器方向。跨學說統計層已落庫(term_stats 2.76M/affinity 2.96M/cooc 6.5M;school 軌 0=63 seed 待人審)。text 計畫 v3.0=reports/augur_knowledge_text_understanding_plan_20260704.md(命門8/9/10、排序公理、W0 兩機merge、13 拍板點)。

**知識層狀態(2026-07-03 活躍前沿)**:三部曲 expansion(已執行)→harvest v1.3(上線、nightly 批)→text v2.0(W5 嵌入進行中);lexicon 154,875 逐字定義/concordance 49.1M 列/sentence 1.54M 句/corpus 1,317 部全蓋章;W6-W9+L5(answer/profile/coverage)未建。詳 [[augur-knowledge-philosophy]]。

**兩機狀態(2026-07-03)**:舊機 PC002-S1800、本機 DESKTOP-8MQPFS8(皆 WSL2)。本機已自 4.5GB dump 還原+**路 B 重放完成**(W1 蓋章 provenance 523/audit 794、reference 清理 sentence 1,539,019/concordance 49,106,830 皆精確對帳、W5 嵌入本機重跑)。**教訓:嵌入表(全部 vector 欄)不在該 dump 內**——任何還原機都須重跑嵌入或確認新 dump 含之。本機 2026-07-03 夜已三粒度全嵌+HNSW 三索引(lexicon 154,875/zh 句 33,314/chunk 63,601;本機吞吐 lexicon 50 筆/s、句 134/s、chunk 7.8 塊/s)。DB/catalog/.env/memory 皆 machine-local 不隨 git、完整性宣稱必本機實查。

**關鍵 operational 約束**:FinMind sponsor token **2026-06-24 到期**(降 free)→ sponsor-only 資料(分點/tick/可轉債/法人 by-date/官股)已落地=**最終資產、不可 drop 重建**;`TaiwanStockDividend` 塌列待 token 續期重建。`OUT_OF_UNIT`＝3 表物理排除。**`finmind.py:_quota_gate` 已恢復為預設啟用(2026-07-03 用戶裁定、三路徑 mock 實測過)**——doctrine #17/#24 三層防護與 code 一致;黑箱錶機台(如 2026-06 Mac token)以 env `FINMIND_QUOTA_GATE=off` 降為只 log、勿改 code。git push 用 .env 之 GITHUB_TOKEN([[git_identity_in_env]])。as-of 治權參數=2026-05-31。

---
name: investment-philosophy-framework
description: 哲學素養框架(06-30 相容版 v1.16.0 → 07-01 擴博學 v1.17.0 → 07-02 版權合規路 v1.18.0)— augur「博學投資大師 AI」;投資哲學=因子假說來源、廣博哲學=解讀素養層、明文從屬三敵;素養庫 861 thinker/work 699/全文 572 部多語言(work_text 加 language 欄)
metadata:
  node_type: memory
  type: project
  originSessionId: c3c40e0c-7154-4936-8937-6d9ce947808c
---

augur **哲學素養框架層**(2026-06-30 入憲相容版、2026-07-01 擴博學、tag `philosophy-erudition-20260701`、commit 6bb9696)。

**定位演進**:投資哲學框架(v1.16.0 相容版)→ **哲學素養框架擴博學(v1.17.0、B 路)**。用戶連續要「柏拉圖等西方哲學都抓」→ 我**停下釐清**(相對論離題觸定位紅線)→ AskUserQuestion → 用戶拍板 **B(擴通用哲學庫、改靈魂)**。augur = 「**有廣博哲學素養的投資量化顧問(博學投資大師 AI)**」:投資哲學(價值/成長…)=**因子假說來源**、廣博哲學經典(東西方)=**解讀/素養層**。

**入憲(逐檔跨檔對齊、git mv 檔名)**:靈魂 v1.3→**v1.4.0**、憲章 v1.16→**v1.17.0**(philosophy 層擴博學 + **原典抓取範圍界定**)、CLAUDE v1.11→**v1.12**、README/原則精華引用。

**守則(三敵不因擴定位鬆動)**:① 來源限**公版真實文獻、禁 AI 生成**(`work_type` 禁 ai_generated、`license` 限 public_domain);② **廣博哲學全文量化零價值、不產因子、不進預測管線、不取代真實資料**;③ **範圍界定「能抓≠該抓」**:納人類哲學經典、**排除非哲學離題(純物理如相對論)**。

**哲學素養庫(DB、跨機獨立不進 git、實查為準)**:thinker **152→765**、work 320、**有全文 298+ 部 / 1.6 億字**。9 中文古典(維基文庫 raw wikitext:孫子/道德經/武經七書/三十六計)+ 50 Gutenberg(投資/行為經典 + 西方哲學:柏拉圖 8 對話/亞里斯多德/斯多葛/近代/德國古典/尼采/英美)+ 自動遍歷 thinker 補抓。

**工具鏈(本地零 usage #28、逐字無 AI 摘要 #1、限公版 #15、冪等可續)**:`fetch_public_domain_classics`(維基文庫)/`fetch_gutenberg_classics`(Gutenberg 50)/`fetch_all_thinker_works`(遍歷 thinker)/`seed_world`+`seed_wikidata`+`seed_dbpedia_philosophers`(thinker metadata)。

**教訓**:(1)用戶要與靈魂衝突方向→**先停下誠實指出張力、釐清相容版、不盲從**(相對論離題我勸阻→用戶改 B 拍板);(2)**WebFetch 小模型對長古籍會摘要/改寫(假兆)、吳子曾被改寫成白話→改本地 raw wikitext/Gutenberg 逐字解析零 usage**(#1 命門:寧缺勿假、不入摘錄/改寫);(3)Wikidata WDQS outage→DBpedia 替代(有中文維基篩 major)、**BC 年 DBpedia 存正數需轉負、壽命>120 判資料錯清 NULL**;(4)Gutenberg 品質:舊式 `End of PG's` strip 漏認、非英文多語版混入、Chaucer heavy `[[markup]]`→修 strip+英文過濾+程式化清;(5)**背景任務**:`pkill -f` 自匹配 shell 自殺(exit 144)、orphan stdout 接死 shell 的 grep→SIGPIPE 中斷、用 **PID `kill -0` 哨兵**監控 orphan 結束。

**學習計畫實作 L2+L3(2026-07-01、tag philosophy-advisor-20260701、commit ca375f7)**:《augur 哲學思想學習計畫》(reports/augur_philosophy_learning_plan_20260701.md、workflow 5 agent 多視角+治權對抗審查產出;釐清「學習」=顧問解讀層 **L1 因子假說/L2 知識檢索/L3 顧問角色**、**非訓練預測模型/非取代真實資料**)。實作 P0-P6:**P0** import-lint 隔離不變式(`tests/test_philosophy_isolation.py`:預測管線 7 模組禁 import philosophy/advisor、「哲學不進預測管線」變可自動檢測)+pgvector 0.8.3;**L2**(P1-P3)切塊(77318 塊逐字 char_range 溯源、二分硬切防超窗)+嵌入(`e5-small` 384維、bge-m3 CPU 53.7h 太久改)+`philosophy/retrieval.py`(pgvector cosine kNN+pg_trgm 逐字回查、Citation 帶 source_url、多語檢索實測精準);**L3**(P5-P6)`advisor/` package(`PredictionPayload` frozen 唯讀契約+system prompt 三姿態三硬約束+`guard` 防幻覺閘:數字∈payload/引號⊂檢索原文/掃未來洩漏/逆向不翻轉、審查修正 C-1/C-3)。守憲章 v1.17.0(哲學不進預測管線、數字唯讀、引文逐字可溯源);真實 LLM(Claude API)/payload 量化本體整合、boilerplate transcriber note 清理重嵌為後續。**誠實定位**:對預測績效貢獻近零(因子飽和)、真價值在顧問可解釋性/角色深度(不誇大)。教訓:e5-small vs bge-m3 CPU 速度差 17×(smoke 測速再定選型)。關聯 [[feature-execution-plan]] [[augur-project-overview]] [[rigor-completeness-discipline]]

**素養庫擴充 + 版權合規路(2026-07-02、tag `philosophy-erudition-expand-20260702`、commit 4854aba)**:憲章 v1.17→**v1.18.0**/CLAUDE v1.12→**v1.13**(**版權著作核心精神合規路入憲**:現代版權著作全文法律不可抓、禁 AI 整理摘要入庫 #1;核心精神經真實文獻 `philosophy_principle`→`principle_factor_map`→**#14 經濟價值驗證**入庫、採用由 #14 裁決非大師權威;work_type/license/source_type DB CHECK 硬擋)。**DB**:thinker 765→**861**(管理各領域窮舉:組織/財務/會計/生產/投資/研發/策略/行銷/HR 90 位、`seed_management_thinkers[2]`)、work→**699**(major 代表著作**書目 125**、`seed_thinker_bibliography` 105 部書名/年份事實 metadata;**DBpedia notableWork 覆蓋極差 701 僅 1 筆→改我知識窮舉**)、citation 30→44(`seed_master_citations` 現代大師 proponents 顯性化)、#14 回填 37。**`philosophy_work_text` 加 `language` 欄**(en 25017/zh 552 回填)支援**多語言全文**(原文+公版譯本並存、去重 (work_id,language))。**全文抓取 triage workflow**(逐部窮盡判別 129 部無全文 work 合法公版可得性→對抗驗證防幻覺 URL→本地 fetcher;**用戶指令演進**:有原文抓原文→原文及譯本全抓、逐版本依作者/**譯者**卒年獨立判、英譯版權陷阱):107 版權硬邊界/10 有公版/confirmed 抓鶡冠子(zh 原文)+泰勒《科學管理原理》(Gutenberg 6435 en)。**教訓**:(6)**AI 生成「逐字逐句定義與意涵」入庫=違 #1 命門**(用戶要此、我 AskUserQuestion 停下:真實公版註疏〔王弼注/十三經注疏/說文解字〕才是逐字定義的真兆載體、非 AI 生成;向量化不需中間定義層、原文嵌入已足;向量庫薦 pgvector〔已嵌 76795 塊〕非另建 qdrant);(7)**熊彼得 archive.org 版權存疑**(1942 帶版權聲明、archive.org 未認定 PD)→verify agent 誠實揭露→依 #17 license 限 public_domain **排除不抓**(公版存疑寧缺勿抓);(8)**git add rename 陷阱**:`git add` 舊檔名(已 rename)報 fatal **中斷整個 add 命令**致其他檔漏 staged→`reset --mixed` 不丟工作重做、`git diff <base> HEAD --stat` 驗證無遺漏。**重開機接續(handoff)**:完整執行記錄報告 `reports/augur_philosophy_erudition_handoff_20260702.md`(commit `7f4449b`、已 push)存本階段指令時序/成果/DB 實證狀態/3 命門守護/環境 resume。**resume 待辦**:① **逐字定義任務岔路待用戶決策**(定義來源:真實公版註疏〔王弼注/十三經注疏/說文解字〕/ 直接向量化不設定義層 / AI 生成〔違 #1 不可〕;向量庫:qdrant / pgvector 已在用)② 新全文(鶡冠子 w564 + 泰勒 w663)已入 `work_text` 但**需重切塊+嵌入**(`philosophy_chunk` 仍 76795 未涵蓋、檢索尚不含)③ triage verify session limit 18:00(台北)重置後 `Workflow resumeFromRunId=wf_eb713121-32e` 續。

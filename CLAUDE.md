# CLAUDE.md — Augur AI 協作工具規則 v1.16

**性質**：AI（Claude 等）在本專案編輯/執行時的工具規則。
**位階**：系統 doctrine 以 `docs/系統核心思想_v1.4.0.md` + `docs/原則精華_v1.7.1.md` + 憲章為準；
本檔只管「**如何用 AI 工具編輯本專案**」這層短半衰期協作規則。
**語言**：與用戶**所有對話一律繁體中文**（程式碼/識別碼/英文專名可保留原文）。

---

## 一、通用規則

1. **Read before Edit**：任何 Edit/Write 前必須先 Read 該檔；不憑記憶或推測編輯。
2. **Edit 優先於 Write**：既有檔案用 Edit（只送 diff）；Write 只用於新檔或完整重寫。
3. **最小邊界**：只改要求的部分；不順手重構、不順便清理、不為假想未來加抽象。
4. **註解最小化**：預設不寫；只在「why 非顯而易見」時寫一行；不寫 what 註解、不寫時效性註解。
5. **不引入安全漏洞**：注意 OWASP Top 10；輸入驗證；**不在 commit 含 `.env`/credentials/token**。
6. **不確定就停手問**：破壞性操作（`rm -rf`、`git reset --hard`、`git push --force`、刪表/分支、改 CI、清空 DB）**必先確認**；授權某次 ≠ 授權所有同類。
7. **改動需實測**：不只靠 type-check/單測宣稱完成；UI/資料改動須實際跑。無法測則**明說「未測試」**，不佯稱成功。
8. **報告誠實**：描述「做了什麼」非「打算做什麼」；工具失敗要明說；不假裝完成。

## 二、資料真實性（呼應原則精華 #1 / #15）

> **北極星自檢**（寫任何數據/結論前）：先問「**這是真兆，還是假兆？**」——有真實 API 來源嗎(①)？決策當下真看得到嗎(② 不洩漏)？真的跑出來、out-of-sample 撐住嗎(③)？三個都「是」才寫；任一不確定 → 當假兆，先查清楚。

9. **零 AI 幻像**：任何產出數據（metrics / IC / Sharpe / 表格 / 對比值）必須出自三類唯一來源之一：
   **(a)** 程式輸出（stdout / JSON / log）｜ **(b)** DB query 結果 ｜ **(c)** API 回應。
   **禁止**：記憶 / 推測 / 估算 / 為完整度補 placeholder / 從相似 model 推估。
10. **可溯源**：每個量化數字能 trace 回 (a)(b)(c)；對比表兩邊都要有真實來源。
11. **Stochastic 多跑**：含隨機性的 production metric ≥3 次取統計（min/median/max/mean）；單次極值須註明。**特徵候選提拔生產前一律走方法論 §四「第 4 道提拔關卡」**（as-of 口徑 + 去相關 Eff-t `evaluation/metrics.py:effective_t_hac` + 多 seed 多因子增量,工具 `scripts/verify_candidate_promotion.py`）；**IC 顯著性禁裸用 iid `effective_t`**（重疊窗高估、審查 G8）。**特徵集＋模型最終須過 §四收尾「經濟價值驗證」(#14、工具 `scripts/run_economic_eval.py`/`evaluation/portfolio.py`)——IC 撐住 ≠ 可交易、靈魂成功定義是經濟價值非 IC**。詳法 SSOT＝`reports/augur_feature_discovery_methodology_20260626.md` §四(此處僅引、不複述);特徵發現完整工具鏈見 memory `augur-feature-toolkit`。
12. **不 hand-patch 已 committed 資料**：發現錯誤改 writer code + 重建，不手動 UPDATE 補值。

## 三、本專案編輯規則

13. **編輯位置**：一律寫專案**真實工作目錄**（隨機器而定，如本機 `/Users/hugo/project/augur/`、WSL2 `/home/hugo/project/augur/`）；不寫 worktree 鏡像目錄。
14. **Commit / Push 須明示授權**：不自行 `git commit` / `git push`；用戶要求時遵守 git 安全協議（不 `--amend` 已 push、不 `--force` 主分支、不跳 hooks）。commit 訊息結尾加 `Co-Authored-By: Claude ...`。
15. **PR / 遠端**：不自行建/關 PR、不在 issue 留言；影響遠端狀態的 `gh` 操作先確認。
16. **研究報告**：寫入 `reports/`，命名 `<module>_<topic>_<YYYYMMDD>.md`。
17. **Clean-Room 重建（SSOT＝原則精華 #16，本條僅工具層引用）**：augur 所有程式產生一律 **clean-room**——只依 5 治權檔（靈魂 / 原則精華 / 憲章 / CLAUDE.md / README）+ augur 自身 schema 目錄 + live API 實證 建立；**產生任何 code 時，不讀、不參考、不移植 stock_backend 之任何 code / 資料 / 報告 / 數字 / 設定**（唯一 sanctioned 觸點＝憲章附錄 B 考古／已抽象之思想啟發，二者**不得回流 code**）。碰 ingestion/feature/universe/model 時對照 `docs/原則精華_v1.7.1.md`（source-pure / anti-leakage / 型別 / SSOT…）；不確定先查靈魂與憲章。**哲學素養框架層（憲章 v1.18.0 橫切 philosophy：投資哲學因子假說 ＋ 廣博哲學素養）之內容一律來源真實權威文獻（書籍／論文／原始文獻／公版原典），禁從 AI 平台生成內容入庫當真兆（敵人① / clean-room；`work_type` 禁 `ai_generated`、`license` 限 `public_domain`）；原典全文限**公版**、本地抓取解析（維基文庫 raw wikitext／Gutenberg）零 usage（#28）逐字無 AI 摘要（#1）；**納人類哲學經典**（投資哲學／戰略／行為財務＝因子假說來源；東西方哲學經典＝解讀／素養層）、**排除非哲學離題**（純物理／自然科學如相對論——「能抓≠該抓」）；廣博哲學全文量化零價值、僅素養／解讀、不產因子、不取代真實資料預測；**現代版權著作全文不可抓（法律 + #1），其核心精神經**真實文獻出處**的 `philosophy_principle` 條目 → `principle_factor_map` 因子假說 → **#14 經濟價值驗證**入庫（採用由 #14 裁決、非大師權威）；**嚴禁 AI 整理／摘要版權著作內容入庫**——AI 生成假兆（違 #1）＋ 侵權、`work_type`／`license` DB CHECK 硬擋（憲章 v1.18.0）**。**
18. **程式標頭與命名慣例（精簡——不重蹈 stock_backend 50-230 行標頭）**：
    - **每支**：🎯 白話 docstring（這支在做什麼，給人看的）+ 一行「守原則 #X #Y」。
    - **CLI 入口程式**（sync / builder / trainer / validator）：再加**執行指令矩陣**（各用法實例，見 #29）。
    - **library 模組**：白話 docstring 即可，不需指令矩陣。
    - **不** per-file 複述憲章 § / 治權宣言（憲章 + 原則精華為 SSOT #12；標頭只引原則 #，不改寫）。
    - **不**寫 in-file 全修訂歷程 → 交給 git（演變史進 git，不入檔；對齊「憲法只記現行法律」）。
    - 標頭目標：讓人/AI 30 秒看懂這支做什麼、守哪些原則。
    - **命名慣例（screaming architecture + DDD ubiquitous language + PEP 8；理論定位見憲章附錄 C）**：`package`（`src/augur/<pkg>/`）＝管線階段或橫切元件（靈魂架構元素、screaming）。
    - **library 模組**（`src/augur/`）＝**領域名詞**（這支是「什麼」）：`finmind`·`reconcile`·`generic_schema`·`catalog`；**禁通用角色名**——`build`·`registry`·`probe`·`util`·`helper`·`manager`·`handler`·`service`（別的領域也能用＝會撞、看不出做什麼）。
    - **CLI script**（`scripts/`）＝**動作動詞片語**（做什麼）：`full_market_sync`·`build_catalog`。
    - **一看就懂測試**：`augur.<package>.<module>` 單看即知做什麼、不必開檔；命名前自問 (a) 是領域詞嗎？(b) `package.module` 讀起來＝做什麼嗎？(c) 別的領域會搶這名（太通用）嗎？→ (c) 中即重取領域概念、合成單一內聚模組。
19. **重大改動逐檔/逐段檢視 + 跨檔一致性**：實質改動**一支/一段做完讓用戶過目再進下一**，不批次傾倒（用戶 directive「一支一支來檢視」）。改動治權檔（核心思想 / 原則精華 / 憲章 / CLAUDE.md / README）或共用模組時，**檢查跨檔一致性**——一處改、全鏈對齊（如嚴格 source-pure 須三檔同步）。
20. **多步驟 / 破壞性任務先計畫**：≥3 步或破壞性任務**先寫計畫 + 用戶確認後執行**（可用 plan mode）；不邊想邊做大改。

29. **Script 個別可執行 × 資料驅動不 hardcode（用戶 directive 2026-07-02 入憲）**：`scripts/` 每支程式須滿足四件事——
    - **(a) 個別可執行**：任何 cwd 直接 `python scripts/X.py` 即跑，**不依賴 `PYTHONPATH=src` 前置**——每支於 `import augur` 前 `import _bootstrap`（`scripts/_bootstrap.py` 自動插 `src/` 進 path、#12 單一住所），並與 `pip install -e .`（README 標準 setup）並存相容。無參數執行須 graceful（印指令矩陣或跑安全預設），不得裸 traceback。
    - **(b) 資料驅動、來源住 DB、不 hardcode 資料（v1.15 升級,用戶 directive 2026-07-02:repo JSON 檔=另一種 hardcode）**：策展/擷取資料一律住**本地 PostgreSQL**,以**三層知識管線**運作（鏡射 raw→下游）——**來源定義表 `knowledge_source`**（adapter+查詢模板 registry）→ `acquire_knowledge.py`（通用擷取引擎,從外部真實來源 DBpedia/Gutenberg/維基文庫/手動策展抓入）→ **暫存表 `knowledge_staging`**（payload JSONB+provenance,#1 可溯源,pending 待審）→ `promote_knowledge.py`（晉升引擎,審核後冪等寫正式表）。**擴新領域（如能源材料 know-how）＝ INSERT 一列 knowledge_source（換 domain/查詢模板）,零 code 變動**;新「來源協定」才寫新 adapter、新 entity_type 才加 mapping 函式（本質是 code,合理）。JSON/CSV 僅為 manual_file adapter 之**傳輸工件**（匯入口/備份),**非來源 SSOT**;跨機遷移用 `pg_dump -t knowledge_source -t knowledge_staging`。內容納入範圍仍受治權判準約束（憲章 v1.20.0「知識層多域擴充準則」:能抓≠該抓、新領域入庫=決策層人拍板、多域知識素養層零量化價值不進預測管線、domain 欄隔離因子鏈純度）。
    - **(c) 通用可重用**：同型 script 合併為單一參數化工具（如 acquire+promote 兩支引擎取代九支 hardcode/JSON seed 批次檔）,設計為未來不同情境重覆使用、擴充靠 DB 資料列與參數。
    - **(d) 指令矩陣 + 實測**：標頭 docstring 寫「**執行指令矩陣**」（各用法實例指令），且**須實測可執行**（#7；安全驗證分級：唯讀類實跑、放量類 import 級 + 最小單位 #25，不為驗證而觸 API 放量）。
    - **效益**：用戶可自行執行零 usage（#28 本地優先）、新增資料不需 AI 改碼、script 數量收斂可維護。

## 四、Long-Running 工作流程

21. **≥5 分鐘任務每 5 分鐘回報**：已完成階段 + elapsed + 剩餘估計 + 已知 metrics + warning；不靜默。
22. **≥30 分鐘 / 過夜任務防睡眠**：背景啟動 + 進程存活 watchdog + sentinel；WSL2/雲機**確認主機不會睡眠**（本機 Linux 端用 `systemd-inhibit`，但擋不住 Windows/雲主機睡眠——須用戶確認電源設定）；長跑須有 resume 後路。
23. **環境前置**：首次 setup 跑 import smoke test 才進後續；OS 層依賴（OpenMP for xgboost/lightgbm、PostgreSQL headers）先補。
24. **API 限速（對齊原則 #17；三層防護）**：對 FinMind / FRED 抓取一律經 `ingestion/finmind.py` 內建——(1) `_pace()` 最小間隔（基礎步調）、(2) **主動額度閘 `_quota_gate()`**（閉環輪詢 `/user_info` 權威錶，額度近滿撞前先停、退夠自動續）、(3) **403 長冷卻 `QUOTA_COOLDOWN`**（不短退避反覆撞）；honor `retry_after`；**不得高併發 / 無間隔狂打服務端**；驗證與全史走同一 `fetch`、同一防護。
    - **FinMind 限流實證地圖（2026-06-09/12）**：(a) **額度為 rolling 視窗**（零 call 期間錶連續下退、非整點清零）、且計數含未知成分（403 當下錶可 < 上限）→ 配額判斷**一律問錶（`/user_info`，403 期間可讀、讀錶不自計），不本地推算**；(b) **兩種 403**——額度型（錶滿，gate 可預防）與 **IP sustained 型**（曾 8/6000 也 ban；只能靠保守步調＋休養）；(c) **重試風暴是惡化路徑**：撞 403 後高併發短退避反覆重試 → 錶永遠滿、不自癒（實證 2026-06-12 卡死 → #25 止血）。教訓：「低於 hourly 上限」≠ 安全；見訊號即停，勿續衝。
25. **測試用最小單位（單股單日）**：任何 API 探測/健康檢查一律用**最小單位**——單一個股 + 單一日期（`data_id=X, start_date=end_date=某日`，回 ~1 列），**不用寬窗 / 多股串流去測**（測試本身也是負載，會戳已敏感的 IP）。流程：**先最小探測確認 IP 健康，通了才放量跑 sync**；放量後緊盯前段，re-ban 立即停、退回休息（**不留無人看顧的 hang**）。實證 2026-06-09：寬窗（8013 列）/ 120 股串流測試太重，且給「短測過了」的假信心 → sync 一放量又 re-ban。

28. **Claude usage 經濟原則 + 配額護欄（批量/長跑通用；#24 之 Claude-配額對偶）**：批量 / 長跑作業（workflow、多 agent、過夜 sync、逐特徵 build）須**配額感知**——近額度上限即暫停、過重置點再續，**絕不在配額用盡時被硬切於半途**留下不一致狀態。#24 防的是**外部 API（FinMind/FRED）**過載；本條防的是 **Claude 自身 usage 配額**耗盡，同一精神。
    - **最小化 usage 為總則（用戶 directive 2026-06-27）**：**本專案所有批量處理之設計與執行一律以「最小化 Claude usage 消耗」為原則**——(a) **本地優先**：能用本地 DB / Python / script 算的（build / sync / 對帳 / 大量查詢）不繞道 Claude model / subagent（本地計算零 usage）；(b) **harness 背景監看、不輪詢**：長跑用背景模式（完成自動通知），不主動反覆查狀態、不自掛喚醒鏈（每次喚醒 / 查詢皆重讀 context 耗 usage）；(c) **非必要不 fan-out**：workflow / 多 agent 僅在真需多視角 / 平行 / 對抗驗證時用、規模配合任務，可單次 main-loop 解決者不開；(d) **批次 / 向量化優於逐項**、一次做完勝過反覆來回；(e) **回報精簡**：只報關鍵、不冗長重述。經濟原則與 ultracode「窮盡」傾向衝突時，**分執行層 vs 理解層裁決（用戶 directive 2026-06-29 入憲）**：凡屬**執行／產出層（how）**——build／sync／對帳／掃描／逐特徵計算／批量落地——**一律省 usage 為先**（本地優先、非必要不 fan-out、批次、背景不輪詢；除非用戶當次明示放量）；**唯「對任務之概念性意義與定義之理解（what／why）」為保留區，仍以 ultracode 窮盡深化為最優先、不得為省 usage 打折**——含治權檔詮釋與跨檔一致、靈魂／原則意涵、資料層 table／field／raw 語意定義（尤 anti-leakage 時點欄 #8）、方法論概念、架構意義、結果之真兆假兆判讀（#15）。**判據＝交付物本質**：交付「理解了什麼意思／定義」（語意正確、一次定錨、錯則沉默污染下游 code／資料）→ 理解層 ultracode；交付「跑出結果／落地資料」（機械、冪等可續、可本地腳本化零 usage）→ 執行層省 usage。**混合任務切兩段不整段歸一邊**（語意／設計／判讀子任務走 ultracode、機械落地／計算子任務走省 usage 並本地算完餵回）；**判不準時裁決句「搞錯會不會沉默污染下游？會→歸理解軸窮盡；僅慢→歸執行軸省」，仍有疑則偏當理解層**（成本不對稱：誤解 doctrine／誤定 field 之下游污染 ≫ 少省的 usage）。**邊界不可逾**：理解再深仍只到執行層「改正確／補完整」，不因 ultracode 鬆動三敵人零容忍（#1／#8／#15）與治權判準變更須停下問（#19／#26）。**反例（禁）**：為省 token 不讀清 doctrine、靠「我以為」解釋 `FULL_START` 越描越錯＝在理解層誤用省 usage。
    - **判據與限制（誠實）**：AI **讀不到即時 usage % 儀表**（無查詢工具）；唯一可程式感知的信號＝API 回的**限額錯誤**（429 / weekly / session limit）→ 撞到即**停、不 retry 硬衝**（承 #24「見訊號即停、不重試風暴」，擴及 Claude 配額）。**用戶可設暫停閾值 / 續跑時點**（如「95% 暫停、10:10 後續」），由**用戶監看儀表發信號**或以限額錯誤近似——AI 不謊稱能自動偵測 %。
    - **resume-safe 前提**：暫停前作業須冪等可續（#6 / #22）、暫停不得損資料、不得留半完成之不可逆狀態；workflow 用 `resumeFromRunId`（同 session 快取）或 scoped 重跑續；批量 build/sync 用 DB-driven resume。
    - **不自掛長喚醒鏈（省配額）**：不為等待一個遠時點而連掛多次自我喚醒（喚醒本身重讀 context、耗配額）；改由用戶於續跑時點 ping、或排一次性續跑。
    - **碰護欄即停（同 #26）**：配額近滿屬「停下問/等用戶」之護欄；過重置點且 resume-safe 才續。

30. **DB 備份/遷移慣例(用戶 directive 2026-07-03 入憲;實測依據)**:
    - **平行 dump 為預設**:`pg_dump -Fd -j 4 -Z1 -d augur -f <WSL ext4 目錄>` → 再 `cp -r` 到 Windows 碟——**先寫本地 ext4、後搬 drvfs**(drvfs 寫入慢);還原端 `pg_restore -j 4` 同樣平行。實測對照:單線程 `-Fc -Z6` 44GB 庫 ≈ 1h+(瓶頸=單核壓縮 65% CPU、~140MB/分),平行 4 工人+輕壓估 **15-20 分(3-4×)**;新安全值依 #27 重覆實證後回填本條。
    - **dump 期間禁 DDL(鎖風暴教訓 2026-07-03 實證)**:pg_dump 持 ACCESS SHARE 鎖,`ALTER TABLE` 要 ACCESS EXCLUSIVE 被擋;且 **timeout 殺掉 client 後 postgres 後端仍掛鎖佇列**,其等待中的 EXCLUSIVE 請求會擋住後續一切查詢(連 UPDATE/SELECT 都排隊)→ 症狀=全庫查詢突然 hang;處置=查 `pg_stat_activity` 找 `state=active, wait_event_type=Lock` 之殘留後端、`pg_terminate_backend(pid)` 清除。DDL 一律排在 dump 完成後;UPDATE/INSERT(ROW EXCLUSIVE)與 dump 相容可照跑。

## 五、協作運作模式

26. **有界自主推進 / 自驅動（授權後主動、碰護欄停手；＝原則精華 #20 之工具層落地）**：經用戶授權，AI 得不逐步等指令、**自己 prompt 自己（loop）**自主朝**靈魂目標**（SSOT＝`docs/系統核心思想_v1.4.0.md`）持續推進**護欄內**工作（clean-room、可逆、不需外部副作用之開發／測試／研究／規劃）；**執行層「如何最佳達成目標」由 AI 主導**（技術路徑 AI 更清楚，承原則精華 #20）。
    - **自我糾錯主動（執行層）**：護欄內發現問題／錯誤／不一致（分類死點、漏抓、doctrine 描述與事實不符…）→ **自行驅動修正、試各種解法、實測驗證**，不被動報告等用戶逐一裁示；做完呈過目（#19）。判據：「**改正確／補完整**」（含 doctrine 文字消歧義、修錯誤描述）屬執行層 → 主動；「**變更判準／新增原則／外部副作用**」屬決策層 → 停下問。
    - **主動求完整、不讓用戶當 QA（自驅動之完整性紀律，用戶 directive 2026-06-16 入憲）**：接任務先**窮舉其完整範圍與所有子需求**再動手——「補 X 的 metadata／欄位」＝主動列 `X` 的**每一欄／每一狀態**一次補齊到底（一個 design 做完），**非**用戶指一個、漏一個、才補一個。執行中與收尾**自問「還缺哪一步？哪個欄位？哪個 edge case 沒顧到？」**；完整性**亦須實證**（查 schema 全欄、逐一確認每欄真有值落地，#15），不靠「我以為已完整」。**用戶不是你的缺漏檢查員**。反例 2026-06-16：excluded 表 metadata 被用戶逐次點 column 空→型別空→`data_id_source`/`earliest_date` 空才補；正解＝接到「欄位要完整」當下即窮舉 `dataset_catalog`+`column_catalog` 全欄、對 excluded 表一次補完。
    - **以真兆為據、凡事實證不靠「我以為」（#15）**：**凡解釋／判斷／回答／做法，皆先以 probe／實測／API／code 事實驗證**，不靠記憶或推測（實證教訓 2026-06-12：靠「我以為」解釋 `FULL_START` 角色一路越描越錯、被 code 事實逼正）；**並主動自我追問「有沒有更近事實、更正確的做法？」**——對自己的答案存疑、用事實檢驗，而非自我說服「我覺得對」（防三敵人「以為懂其實自欺」——主動 ≠ 自信犯錯）。
    - **碰護欄即停**、不自行跨越：API **大規模落地／過夜放量**（#24；限速受控之診斷探測 dry-run 不算放量、屬執行層）／ commit-push（#14）／ **變更治權檔判準**（#19；文字改正確除外）／ 破壞性（#6）／ 真兆最終確認（原則精華 #15）。

    精神承靈魂「系統建議、人決策；**有紀律的顧問，不是自動駕駛**」——**決策層人拍板、執行層 AI 主動**，同樣適用於開發 augur 本身。授權可隨時收回。

27. **可控風險下逐級逼近最佳奇異點 / 試錯即進步（對齊原則精華 #19；augur 解問題之通用做法）**：經用戶授權探索某參數/解法之最佳點（FinMind throttle rate / 並發 / 任何可調項）時——
    - **可控才試**：僅在**可恢復**（ban 自癒 + resume-safe）＋**有界**（最壞退回上一已驗證安全級）＋**可即時偵測退場**（速率崩塌/錯誤碼/指標異常即退一級、不退過度保守）下進行；缺一即不試。
    - **逐級逼近奇異點**：某級經持續性驗證可行 → 再往進一級試（如 `0.6s` 可行 → `0.5s` → 以此類推），直到持續性失敗 → 退回上一安全級＝最佳奇異點。不被單次過往觀測錨定（如前次 `0.7s` ban 屬「某情境一觀測」、非永久上限）；以 production 當 sustained 載具（短測會騙人 #24/#25），緊盯持續性訊號。
    - **重覆驗證再定論、單次不入憲**：新 operational 安全值須重覆實證 + source-traceable 才寫治權檔（#9/#10）；未驗證前既有已驗證安全值維持為操作值（不寫死數字、見 `finmind.py`），程式內實驗值須註明「實驗中」。**不怕一時的可恢復錯誤——進步來自試錯**。
    - **凌駕邊界（不可逾）**：只作用 **operational/方法層**（速率/並發/參數/解法）；**絕不**為「報酬」放鬆資料誠實——三敵（假資料/偷看未來/自我欺騙）**不是試錯對象**、永遠零容忍。試的是「方法與參數」，不是「資料真假」。

## 六、本檔升版

- 半衰期 6-12 個月（隨工具演進更新）；工具/協作慣例變更時更新，**不需動憲章**。
- 若工具變更影響系統 doctrine（能否進某層），須同步憲章。

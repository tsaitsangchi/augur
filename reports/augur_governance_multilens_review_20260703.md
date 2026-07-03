# 五治權檔 9 視角對抗審查——確認發現與執行工單(2026-07-03)

**性質**:治權檔多視角審查結果(9 鏡平行 → 合併 → 每條 3 懷疑者對抗驗證,22 條全數 3/3 確認)+ 用戶已拍板之執行工單。
**排程**:2026-07-03 23:35 自動執行(用戶 directive:「甲乙全做,丙1a、丙2要、丙3要」)。
**前情(當日已完成、勿重做)**:A1-A6 細修+B1(advisor 入憲 v1.21.0)+B2(_quota_gate 恢復)+B3(README 去重)已落地;W5 嵌入完成(lexicon 154,875/zh 句 33,314/HNSW);全部未 commit。

## 執行紀律(硬約束)
1. **內容零刪減、判準不動**:乙組全部=搬家/收斂/排版,任何字義變更即停手記錄。
2. **逐檔做完自驗**(#7/#15):每檔改完 grep 驗證錨點、跨檔引用鏈重查(#19 一處改全鏈對齊);code 類(C4 docstring/C7 sync.py 註解/丙3 測試)須 import/pytest 實測。
3. **不 commit、不 push**(#14):做完產差異總結呈用戶過目。
4. 修訂歷程既有列=歷史快照,一律不動(C9 為唯一例外:v1.9.1 列尾補一句漏記事實)。
5. C23(datasets_zh.md:563 千元→元):SSOT=column_catalog 已標「當月營收（元）」,md 視圖同步此一行。

## 丙、用戶拍板(三點皆已裁決)
- **丙1=(a)**:憲章第四部 #20 索引欄之 500 字法律細則(完整性天職/真邊界窮舉/慣例值待驗/GoldPrice 1990 教訓)**移入原則精華 #20 ENFORCE 增列一點**(法律位階);憲章 cell 縮回一句話+「全文見原則精華 #20」。搬家零語意變更 → 原則精華**不升版號**、檔尾演進記錄記一行(v1.7.1 內文字搬家)。
- **丙2=要**:憲章第六部新增修訂歷程體例規則——自下一版起,新列以「變更類型+一句判準+同步清單+動因」約 3 行封頂;既有列不動。
- **丙3=要**:隔離範圍擴 `augur.knowledge`——tests/test_philosophy_isolation.py 之 FORBIDDEN 加 `augur.knowledge`(PIPELINE 7 pkg 不變),憲章 philosophy 層隔離不變式句同步「零 import augur.philosophy／augur.advisor／augur.knowledge」;改後 pytest 實跑該測試須 PASS(若現有預測管線真有 import knowledge → 停手回報,勿硬改)。
- **升版承載**:丙2(第六部規則)+丙3(隔離判準明文擴)+乙組 SSOT 收斂 → **憲章 v1.21.0→v1.22.0**(git mv 改名、header、修訂歷程新列——該列本身即示範丙2 的 3 行體例;README/原則精華第 5 行交叉引用同步)。甲組纯文字修正不另升版、由 v1.22.0 歷程列一併記載。

## 甲、細部修正(12 條,另加 C23 見下)

### C4〔medium·factual-error〕docs/系統架構大憲章_v1.21.0.md
- **位置**:第三部 橫切 · philosophy「檢索與顧問前端〔v1.21.0〕」(L132)
- **問題**:「lexicon/concordance 逐字回查、pg_trgm verbatim 驗證」——宣稱逐字驗證用 pg_trgm,但 pg_trgm 未安裝、全 repo 無任何 trigram 使用;實際機制為 Python 子字串包含檢查。逐字回查機制真實存在,憲章沿用 code docstring 的錯誤技術名。
- **證據**:DB 實查 `SELECT extname FROM pg_extension` 只回 plpgsql、vector;src/augur/philosophy/retrieval.py:74-82 `verify_verbatim()` 實作為純 Python 子字串檢查(`citation.text in row[0]`);全 repo 無 pg_trgm 運算子(%、similarity()),pg_trgm 僅存在 retrieval.py:1,5,75 與 scripts/query_philosophy.py:4 docstring 字樣。同句其餘宣稱皆實證成立(e5-small=intfloat/multilingual-e5-small、vector(384)、pgvector kNN `<=>` 查 philosophy_chunk_embedding 1216 列)。(來源:鏡3-憲章＋鏡7-doctrine↔code,取鏡7完整實證)
- **修法**:憲章該句改事實描述:「…pgvector kNN ＋ lexicon/concordance 逐字回查、verbatim 逐字包含回查驗證(`retrieval.verify_verbatim`,DB 原文子字串比對)」;同步修 retrieval.py(3 處)與 query_philosophy.py(1 處)docstring 之 pg_trgm 字樣,免下次入憲再複製錯名。現行子字串精確包含比 trigram 更嚴格,機制無缺陷、純命名失實。

### C5〔medium·stale〕docs/系統架構大憲章_v1.21.0.md
- **位置**:第五部 12-PHASE 維運矩陣「主程式/動作」欄(PHASE 2/4/8,L190/193/197)
- **問題**:PHASE 2 主程式=「ingestion `--seed`」、PHASE 4=「ingestion `--all`」、PHASE 8=「universe `--completeness-gate`」——三旗標全 repo 不存在;憲章明言「從零重建一律照此序列」,照偽旗標逐字執行會失敗、找不到入口。
- **證據**:repo 全域 grep:`--seed`/`--all`/`--completeness-gate` 在 scripts/ 與 src/ 無任何 add_argument(僅有他義的 `--seeds`/`--datasets`);ingestion package 無 __main__/argparse。實際入口:scripts/full_market_sync.py(docstring 明載「PHASE 1 bootstrap → 2 seed 名冊 → 2b FRED → 4 全日頻 → 5 對帳」,唯一旗標 `--new-only`;seed=sync.seed_roster()、全史=sync.daily_datasets() 動態列舉);scripts/build_core_universe.py 之 completeness gate 為預設行為(旗標僅 --since/--liquidity-pct/--exempt-revenue-financial/--asof)。(來源:鏡3-憲章＋鏡7-doctrine↔code)
- **修法**:主程式欄改實際可執行對映:PHASE 2/2b/4/5 → `scripts/full_market_sync.py`(內含 seed→FRED→全史 sync→對帳序列);PHASE 8 → `scripts/build_core_universe.py`(gate 為預設,可加 `--asof`);其餘 PHASE 對映 build_feature_panel.py/run_feature_audit.py/run_evaluation.py。屬文字改正確(執行層),不動判準。

### C6〔medium·stale〕docs/原則精華_v1.7.1.md
- **位置**:#3 純通用 Ingestion WHAT/ENFORCE(L29-31)
- **問題**:「`--all` 動態列舉、無 hardcoded 清單」及「任意 `--dataset X` 即建表」——引用兩個不存在的 CLI 旗標作為守則機制;機制本身實證成立,但旗標記法落空。
- **證據**:全 repo 實查(grep src/+scripts/):不存在 `--all` 或 `--dataset`(單數)旗標;scripts/full_market_sync.py 唯一旗標 `--new-only`、daily_maintenance.py 為 `--datasets`(複數)。實際機制=sync.py:52-55 `daily_datasets()` 動態列舉(無白名單)+ingest.ingest_finmind 任意 dataset auto-schema 建表(generic_schema.py);唯一 `--all` 出現處=finmind.py:11 docstring 引用本條原文(引用不存在的旗標)。憲章第四部 #3 列已用無旗標措辭,本檔落後。(來源:鏡2-原則精華＋鏡7-doctrine↔code)
- **修法**:WHAT 改「全 dataset 動態列舉(`sync.daily_datasets()`)、無 hardcoded 清單」;ENFORCE 改「任意 dataset 名傳入 ingester 即 auto-schema 建表(如 `daily_maintenance.py --datasets X`)」;同步修 finmind.py:11 docstring 引文。純文字微修正、不升版。

### C7〔medium·stale〕docs/原則精華_v1.7.1.md
- **位置**:#18 ENFORCE「辨明」段(L66)
- **問題**:「`full_start`(如 1990)僅 per-stock/market 單次 call 之全史下界保險——API 只回實際有資料範圍、不空抓」——此假設已被實證推翻(API 以 start_date 為下界截斷),治權檔仍保留被推翻的措辭;sync.py 註解同殘留舊假設、與 catalog 實證註解自相矛盾。
- **證據**:src/augur/catalog/__init__.py:739-742「FULL_START 註解原假設『API 只回實際範圍』實測為錯——API 以 start_date 為下界截斷(GoldPrice 真起點 1979 被 1990 截斷之教訓)」;同檔 :897 列 UKStockPrice 1990→源頭 1968 等,需 `_refine_earliest` 往更早探;憲章第四部 #20 列(L176)明載 2026-06-16 GoldPrice 教訓——教訓日早於本檔 v1.7.1(2026-06-24)。src/augur/ingestion/sync.py:36 註解「早於任何 FinMind 資料、API 只回實際範圍→等同全史」同樣殘留。(來源:鏡2-原則精華)
- **修法**:#18 辨明段改:「查詢下界參數(非全史保險:API 以 `start_date` 為下界截斷、GoldPrice 真起點 1979 被 1990 截斷之 2026-06-16 教訓;earliest 卡 `FULL_START` 者由 catalog `_refine_earliest` 往更早探真起點)」;同步修 sync.py:36 註解對齊 catalog 實證(跨檔一致 CLAUDE #19)。純文字修錯誤描述、不升版。

### C8〔medium·inconsistency〕docs/系統核心思想_v1.4.0.md
- **位置**:「資料只來自哪」(L41-46)
- **問題**:該節無範圍限定地宣稱系統資料只來自 FinMind API + FRED、「每個值都能 trace 回某次 API 回應——沒有『第四類來源』」;但同檔 L119 世界觀已載明廣納哲學經典/真實文獻入庫,且素養語料已實體落地 DB。僅讀本節的讀者會誤解全系統 DB 只含兩 API 來源之值。
- **證據**:同檔 L119:「廣納人類哲學經典(…公版原典)作解讀與智慧素養層…來源限真實文獻」;憲章 v1.21.0 L125-132 philosophy/knowledge 橫切層(維基文庫/Gutenberg/OpenAlex 等來源);DB 實查(pg_stat_user_tables):philosophy_work=1,317、philosophy_work_text=31,778、philosophy_chunk=63,601、knowledge_staging=23,450、knowledge_source=3,592 列——大量非 FinMind/FRED 語料已在庫。(來源:鏡1-靈魂)
- **修法**:最小修法(執行層消歧義、不動判準):L41-46 節加一行範圍限定——「本節指預測用市場/總經資料(真兆)之來源;哲學/知識素養文獻另循『真實文獻、可溯源、不進預測管線』判準(見世界觀末列與憲章 philosophy 層)」。

### C9〔medium·inconsistency〕docs/系統架構大憲章_v1.21.0.md
- **位置**:修訂歷程 v1.9.0/v1.9.1 vs 現行本文 #4/#18、第三部 raw 邊界
- **問題**:修訂歷程對鉅額分點的最後記錄(v1.9.0, 06-23)是「可抓、移出 OUT_OF_UNIT」,但現行法律本文與 code 皆為「3 表排除(含鉅額分點)」;06-24 重列 OUT_OF_UNIT 之判準變更在歷程中無任何一列記錄——追溯歷史鏈時最後記錄與現行法互相矛盾,違反第六部「重大判準修正記修訂歷程」。
- **證據**:憲章 L283(v1.9.0):「鉅額分點稀疏…可抓、移出 OUT_OF_UNIT」「ingest.py(OUT_OF_UNIT={分點,權證}/BACKFILL_DEFERRED={鉅額})」;現行 src/augur/ingestion/ingest.py:34-42 OUT_OF_UNIT 含 TaiwanStockBlockTradingDailyReport、註「鉅額分點 2026-06-24 移入 OUT_OF_UNIT」、BACKFILL_DEFERRED=空集;L284(v1.9.1, 06-24)全列無鉅額分點字樣。(來源:鏡3-憲章)
- **修法**:最小修法:v1.9.1(2026-06-24)列尾補一短句——「同日:鉅額分點 probe 實證(endpoint 不吃 end_date+schema PK bug 16+→1 覆蓋)自 BACKFILL_DEFERRED 重列 OUT_OF_UNIT,3 表確認排除(ingest.py 同步)」。不動 v1.9.0 歷史快照。

### C17〔low·inconsistency〕README.md ＋ docs/系統架構大憲章_v1.21.0.md
- **位置**:README 狀態段(L14)vs 目錄(L37)＋憲章第三部 model 層(L101-105)
- **問題**:models(F3) 狀態表述不一:README 同檔 L14「續建中」vs L37「未建」——「續建中」暗示已部分建成,「未建」才是事實;憲章第三部 model 層(路徑 src/augur/models/、model_registry 表)亦無任何已建/藍圖區辨,為唯一未提示此落差之治權檔。
- **證據**:README:14「`models`(F3)續建中」;README:37「models(F3)未建」;ls /home/hugo/project/augur/src/augur/ 列 advisor/audit/catalog/core/evaluation/features/ingestion/knowledge/philosophy/universe,無 models/;DB information_schema 查無 model_registry 表;tests/test_philosophy_isolation.py 以目錄不存在即 skip。(來源:鏡1-靈魂＋鏡3-憲章＋鏡6-跨檔一致＋鏡9-治權法理,四鏡共識)
- **修法**:README L14 統一為「未建(規劃中)」與 L37 一致;憲章 model 層標題加一註「〔F3,未建——現況見 README 狀態段〕」,不在憲章複述進度細節(狀態 SSOT 留 README)。

### C18〔low·stale〕CLAUDE.md
- **位置**:#17 / #29(b) 憲章版本釘
- **問題**:#17 兩處引「憲章 v1.18.0」、#29(b) 引「憲章 v1.20.0『知識層多域擴充準則』」,皆為活體規範性交叉引用釘死於已不存在的憲章版本;且版本錨本身不準(philosophy 層立於 v1.16.0/擴於 v1.17.0,v1.18.0 只加版權準則;多域擴充準則立於 v1.19.0)。每次憲章升版即再過期——今日升 v1.21.0 未同步此三處。
- **證據**:現行憲章檔=docs/系統架構大憲章_v1.21.0.md(v1.18.0/v1.20.0 檔已不存在);憲章「知識層多域擴充準則」段自標〔v1.19.0〕(L131);git 史證此釘被逐次手改(#17 原寫 v1.16.0(commit 2755245)→5cd760f 改 v1.18.0);憲章修訂歷程 v1.16.0「立」/v1.17.0「擴博學」/v1.18.0「版權準則」/v1.19.0「多域擴充入憲」逐列可查。(來源:鏡4-CLAUDE＋鏡9-治權法理)
- **修法**:去版本釘:改「憲章 philosophy 層」「(憲章 DB CHECK 硬擋)」「憲章『知識層多域擴充準則』」——本檔位階行引憲章本就不帶版本,統一此慣例即免每次升版連動。

### C19〔low·inconsistency〕docs/原則精華_v1.7.1.md
- **位置**:#18 ENFORCE 維度 id 全集取得順序(L66)
- **問題**:宣稱 fallback 順序為 (a) datalist → (b) roster/Info → (c) 官方文檔/IndexCodes+live-probe,但 code 實際順序 (b)(c) 對調:datalist → 文檔種子 → Info roster。
- **證據**:src/augur/ingestion/sync.py:241-252 `_dimension_sync` docstring「#18 階層:FinMind `/datalist` → 文檔種子 → 同家族 Info roster」;實作 :245-246 先 `finmind.datalist()`、無則 `_DOC_SEED_IDS`(L154-157 含 TAIEX/TPEx),再無才 :250 `_info_roster_ids`。(來源:鏡2-原則精華)
- **修法**:L66 改「(a) `/datalist`(b) 官方文檔/IndexCodes+live-probe 證實之文檔種子(c) roster/Info 表(per-stock)」對齊 `_dimension_sync` 實際階層。純文字微修正。

### C20〔low·stale〕docs/系統架構大憲章_v1.21.0.md
- **位置**:第一部 系統本質 · 邊界列(L24)
- **問題**:第一部「邊界」摘要列停在靈魂 v1.2.0 時代的 6 項,漏了靈魂 v1.4.0 新增的第 7 項「不做 AI 占卜大師」——同檔 philosophy 段(L128)已引用該邊界,僅第一部摘要未同步。
- **證據**:憲章 L24「邊界｜不日內、不保證獲利、不擇時躲崩盤、不用未來資訊(anti-leakage)、不下單動錢、不存無源值」;靈魂 v1.4.0 L151「不做 AI 占卜大師(v1.4.0):…不取代真實資料預測、不存 AI 生成內容當真兆…」;憲章 L128 已引「仍是『有廣博哲學素養的量化顧問、非 AI 占卜大師』(靈魂 v1.4.0)」。(來源:鏡6-跨檔一致)
- **修法**:第一部邊界列補「不做 AI 占卜大師」(文字同步靈魂 v1.4.0,屬執行層改正確、非判準變更)。

### C21〔low·stale〕README.md
- **位置**:目錄段 docs/ 行(L40)
- **問題**:「docs/ 治權三件套 + datasets_zh.md(資料源逐欄 catalog) + archive(考古索引)」漏列 finmind-references/——該目錄為 code 依賴的權威資料源(憲章已入憲),從零重建者依 README 不會知道其存在。
- **證據**:ls docs/ 有 finmind-references/(內含 datasets.md);src/augur/catalog/__init__.py:22-29 以其為「官方 FinMind dataset 參考…入憲、抓法元資料權威源」(_OFFICIAL_REF=docs/finmind-references/datasets.md,`_parse_official_datasets` 解析驅動);憲章 L120 明載;git dd9c817「官方 datasets.md 入憲 + builder 去硬編」。(來源:鏡5-README＋鏡7-doctrine↔code)
- **修法**:README docs/ 行補「+ finmind-references(FinMind 官方 dataset 參考,catalog 抓法元資料權威源)」。

### C22〔low·inconsistency〕docs/系統架構大憲章_v1.21.0.md
- **位置**:第三部 philosophy 橫切層「守」③(L127)
- **問題**:「③ #15 `validated_ic/econ` 由 augur 自身實證回填、可溯源 #10」——裸 #10 在本憲章語境=原則 #10(核心股質>量),與「可溯源」無關;疑原意為 CLAUDE #10(可溯源)但漏前綴,成錯誤條號交叉引用。
- **證據**:第四部 #10 行(L160)=「核心股:質 > 量」;可溯源/trace 屬 #15(L169「數字可 trace (a)程式/(b)DB/(c)API」);防線地圖 philosophy/advisor 列(L64)③ 亦僅列 #14 #15、無 #10;憲章引 CLAUDE.md 條目一律帶前綴(「CLAUDE.md #28」「CLAUDE #29b」)。(來源:鏡3-憲章)。另捨棄 9 條低值發現(靈魂『樹為主軸』決策問句、docs/archive 指向落空、#29c『九支』數字、#8/#15 缺 ★、附錄 A 為空、verify_code_reports.py 寫死路徑、靈魂世界觀 cell 排版、憲章 feature 層 L93 版本括號、第六部升版類別縫隙)。
- **修法**:「可溯源 #10」改「可溯源(#15)」;若原意確為工具層規則,改「可溯源(CLAUDE #10)」。一處字元級修改。

## 乙、SSOT 收斂+排版重構(8 條,內容零刪減、判準不動)

### C1〔high·ssot-violation〕docs/原則精華_v1.7.1.md ＋ docs/系統架構大憲章_v1.21.0.md
- **位置**:原則精華 #3 ENFORCE(L31)/#4 ENFORCE(L36)/#18 ENFORCE(L66)＋憲章第三部 raw 層邊界(L86)＋第四部 #18 索引列(L152)
- **問題**:`OUT_OF_UNIT`(分點/權證/鉅額分點物理界限排除)之完整論證——probe 實證 2026-06-23/24、TB 級/數千萬列、鉅額分點 endpoint 不吃 end_date、schema PK bug 16+→1 覆蓋、「非暫緩」——在兩檔共五處全文複述。同一概念五個家＝漂移風險最高點;成員異動(ingest.py 註解明示「schema PK 修後重議」)須同改五處;亦是 #18 ENFORCE 膨脹成 600+ 字單段的最大成因。
- **證據**:原則精華 L31「3 表確認排除(非『待有能力』暫緩;是資料量+schema 雙重物理界限)」;L36「→ `OUT_OF_UNIT` 排除(#3,probe 實證 2026-06-23/24…)〔辨明:…〕」;L66「唯資料量規模物理不可行者(分點/權證/鉅額分點:全史 TB/數千萬列、DB 裝不下+鉅額分點 endpoint 不吃 end_date+schema PK bug 16+→1 覆蓋)→ #3 `OUT_OF_UNIT` 排除(probe 實證 2026-06-23/24…)」;憲章 L86 與 L152 再各全文複述一次(僅憲章 #4 列用短指標「見 #18」是正確做法)。(來源:鏡2-原則精華＋鏡8-可讀性反膨脹,取鏡8五處全景)
- **修法**:指定唯一權威家＝原則精華 #3 ENFORCE(OUT_OF_UNIT 定義本就掛 #3);#4 與 #18 各縮一句「資料量物理界限者 → `OUT_OF_UNIT` 排除,全文見 #3」;憲章 raw 層邊界與第四部 #18 列縮為「…`OUT_OF_UNIT` 排除(判準全文＝原則精華 #3)」。內容零刪減、只收斂住所,判準不動、不升版。

### C3〔high·readability〕docs/系統架構大憲章_v1.21.0.md
- **位置**:第三部 橫切 · philosophy(L125-133)＋修訂歷程(L274-296)
- **問題**:philosophy 層是全憲章膨脹震央:9 行、每行 300-900 字、總量超過第三部其餘六層總和;「三敵從屬/量化零價值/不進預測管線/不產因子」同組不變式在 L127/L128/L129/L131 複誦 ≥4 次(各版準則段各自複誦);heading 內嵌 10 個表名近 200 字;L132(今日新增)一段壓三個異質關切(檢索技術棧/防幻覺五閘/隔離不變式)。修訂歷程近期列(v1.16.0-v1.21.0)每列 600-1000 字、單表近占全憲章一半 token;body↔歷程雙寫已實證漂移一次(表清單,v1.21.0 才據 DB 實查校正),重複面積越大下次漂移機率越高。
- **證據**:L127「廣博哲學原典全文量化零價值、僅素養/解讀素材、不產投資因子、不進預測管線」;L129/L131 近似句逐段複誦;heading L125 內嵌 `philosophy_school`…`philosophy_build_meta` 10 表名;L291(v1.16.0)歷程列約 900 字 vs L274(v1.0.0)僅 ~80 字;L224 自訂「30 分鐘可讀、膨脹即是警訊」;漂移實例＝v1.21.0 列自述「同版同步校正:表清單據 DB 實查更正為 10 表」。(來源:鏡8-可讀性反膨脹三發現＋鏡9-治權法理)
- **修法**:層頂立「共同不變式」小段一次寫清(三敵從屬/量化零價值/不進預測管線/不產因子/禁 AI 生成),v1.17.0-v1.21.0 各準則段只留該版增量;10 表名自 heading 移為層內一行;L132 拆三子彈(職責/防幻覺機械閘/隔離不變式)。修訂歷程既有列一律不動(歷史快照);自下一版起新列以「變更類型＋一句判準＋同步清單＋動因」~3 行封頂,此體例上限若入第六部須用戶拍板。內容零刪減、判準不動,估砍該層 1/3 篇幅。

### C10〔medium·ssot-violation〕CLAUDE.md
- **位置**:#17 哲學素養框架段(L39 後半)
- **問題**:#17 條首自稱「本條僅工具層引用」,後半卻以 ~600 字全文複述憲章 philosophy 層准入判準(禁 AI 生成、公版限定、納/排範圍、版權合規路、DB CHECK 硬擋),與憲章 L127-130 準則段實質同文、成第二個家,且已現漂移苗頭;巢狀括號達 4 層、使 #17 成全檔第二長單行(990 字元)。
- **證據**:憲章 v1.20.0 已改「全文准入雙軌」(work_text 限公版;knowledge_item_text 另納 CC 白名單,DB 實查 knowledge_item_text_license_check 允 cc-by/cc-by-sa/cc0),而 #17 仍一句到底寫「`license` 限 `public_domain`」——就 philosophy_work_text 不假,但無範圍限定詞之複述易被過度概括到知識層,正是「複述=漂移風險」實例。(來源:鏡4-CLAUDE＋鏡8-可讀性反膨脹)
- **修法**:縮為兩句工具層指引:「哲學素養層內容產生時,判準 SSOT＝憲章第三部 philosophy 層(禁 AI 生成入庫、公版/CC 雙軌准入、版權著作合規路);本地抓取零 usage(#28)、逐字無 AI 摘要(#1)。」細節單住憲章;內容零刪減(憲章已全載)、判準不動。

### C12〔medium·readability〕README.md
- **位置**:狀態段(L14)
- **問題**:狀態段三題:(i)「嵌入 W5 與 L5 顧問角色層續建中」用內部代號,全部治權檔無 W5/L5 定義、入口檔讀者無從解析;(ii)「三鏡頭 8 特徵＋康波毛利循環相位入生產(27→35)」直算 27+8+1=36≠35,漏了同批剪除 volatility_20d(共線)、讀者無法自洽核算;(iii) 單段塞 6 個進度子句,且「防漂移 pointer」在 L14 與 L24 各寫一次(去重註記本身重覆)。
- **證據**:grep 全治權檔(憲章/靈魂/原則精華/CLAUDE.md)無 W5/L5 定義,唯一出處=reports/augur_knowledge_text_understanding_plan_20260702.md(L24「L5 角色層」、L124「W5 embed」);git 92f9d33(提拔 8+剪 volatility_20d,27→34)+95cdea0(34→35);DB 實查 feature_values distinct=35、volatility_20d 不在列(僅 volatility_60d)——端點數字(27、35)正確,「8＋1」措辭與端點差(+8)矛盾。(來源:鏡5-README 兩發現＋鏡6-跨檔一致＋鏡8-可讀性反膨脹)
- **修法**:W5/L5 改白話(「嵌入模型與顧問角色層續建中」)或附報告路徑;帳補「(淨+7,剪共線 volatility_20d)」使自洽;狀態段拆「治權」「管線進度」兩短句,防漂移 pointer 留 L24 表格一處、L14 刪。

### C13〔medium·ssot-violation〕docs/系統架構大憲章_v1.21.0.md
- **位置**:第五部 Long-running 治權「Claude usage 經濟原則」條(L213)
- **問題**:該條自稱「SSOT 在 CLAUDE.md 工具層,本處僅引、不複述」,但同一子彈仍複述 CLAUDE #28 的總則五要點與執行/理解二分 tie-break(含判據語)約 300 字——「僅引不複述」宣言與實文自相矛盾;三個版本括號〔v1.11.0;v1.12.0 補;v1.15.0 補〕嵌正文使句子斷裂。
- **證據**:L213「(本地計算優先、harness 背景通知非輪詢、非必要不 fan-out…批次優於逐項、回報精簡)——衝突時執行層…省 usage 為先,唯『概念性意義與定義之理解(what/why)』仍以 ultracode 窮盡為最優先(執行省、理解窮盡;判據+正反例見 CLAUDE.md #28)…(SSOT 在 CLAUDE.md 工具層,本處僅引、不複述)」。(來源:鏡8-可讀性反膨脹)
- **修法**:縮為兩句:「批量/長跑受 Claude usage 配額護欄與『最小化 usage』經濟總則約束(執行省、理解窮盡);完整規則與判據 SSOT＝CLAUDE.md #28。」版本括號交修訂歷程承載;內容零刪減(CLAUDE #28 全載)。

### C14〔medium·ssot-violation〕docs/原則精華_v1.7.1.md
- **位置**:升版哲學(L157)＋檔尾演進記錄(L161-162)
- **問題**:「重大判準修正→升 minor」規則子彈內嵌 ~200 字 v1.7.0 歷史敘事(OUT_OF_UNIT 重定義全過程、probe 日期、by-broker 參數名),把「規則」與「演變史」混同一彈點——違反本檔自己的萃取原則「憲法只記現行法律,不記怎麼演變到今天」;且演進明細現有三個家(升版哲學內嵌明細/檔尾演進記錄/憲章修訂歷程),README 已宣告單一權威家＝憲章修訂歷程,前兩處遂成第二/第三家;此複述模式已有實證漂移前例(憲章 philosophy 表清單 body↔歷程不一致、v1.21.0 才校正)。
- **證據**:L157「…升 minor 並記錄演進(v1.4.0:…;v1.7.0:`OUT_OF_UNIT` 由 operational 暫緩定為『資料量規模物理界限排除』——分點/權證 probe 實證 2026-06-23 抓法已知(by-broker `securities_trader_id`+`date`)…鉅額稀疏…移出)」vs L7「憲法只記『現行不可違反的法律』」;該歷史已完整住憲章修訂歷程 v1.9.0 列;README L14/L24 宣告「演進明細單一權威家＝憲章修訂歷程、不複列防漂移(#12)」。(來源:鏡8-可讀性反膨脹＋鏡9-治權法理)
- **修法**:升版哲學彈點只留「(例:v1.4.0、v1.7.0)」版本指標,v1.7.0 敘事刪(憲章 v1.9.0 歷程列已全載)或移檔尾演進記錄一行式;演進記錄維持一行指回憲章修訂歷程。不動判準本文;若要改「各治權檔自帶 changelog」慣例則屬決策層、先問用戶。

### C15〔medium·readability〕docs/原則精華_v1.7.1.md
- **位置**:#18 ENFORCE(L66)
- **問題**:#18 ENFORCE 為單一段落約 700 字,內含至少 6 個獨立機制(探測方式階層、維度 id 全集三層來源、resume 起點、辨明 full_start、單日型 dataset、OUT_OF_UNIT),「辨明」為括號→內層括號→雙破折號三層巢狀插入——20 條中最難讀的一段;對照同檔 #7 ENFORCE 已用子彈點分列,體例不一。
- **證據**:L66 單段內嵌「(辨明:資料最早日由 API 回傳/探測決定…;`full_start`(如 1990)僅 per-stock/market 單次 call 之全史下界保險——API 只回實際有資料範圍、不空抓——非最早日、亦非逐日掃起點;故『不寫死起點』禁的是 by-date 逐日空掃、非此下界參數)」三層巢狀。(來源:鏡8-可讀性反膨脹)
- **修法**:比照 #7 體例拆 5 個子彈點:方式階層/維度 id 全集/起點(辨明 full_start 獨立一點)/單日型與週末取捨/OUT_OF_UNIT(一句指 #3)。純排版重構、逐字保留判準內容;可與 full_start 措辭修正、OUT_OF_UNIT 去重同批處理。

### C16〔medium·readability〕CLAUDE.md
- **位置**:#11(L30)/#17(L39)/#28(L71)/#29b(L56) 排版
- **問題**:四處單行巨型段妨礙 30 分鐘可讀:L71(#28)1224 字元/32 個粗體、L39(#17)990、L56(#29b)738、L30(#11)525。#28 最常用的操作裁決句(「搞錯會不會沉默污染下游?」)埋在段落 3/4 深處難檢索;#11 標題仍是「Stochastic 多跑」但條文 2/3 已是另一主題(特徵提拔第 4 道關卡+經濟價值驗證之強制引用),掃標題會漏硬約束,且自稱「僅引不複述」卻仍複述關卡三要件與工具路徑。
- **證據**:程式實測行長:line 30=525、line 39=990、line 56=738、line 71=1224 字元(粗體配對無破損);#28 其餘子項已用縮排 bullet,唯最長的二分裁決內容擠首行(內容經查邏輯自洽,問題純在排版);L30 標題後接「特徵候選提拔生產前一律走方法論 §四…詳法 SSOT＝reports/augur_feature_discovery_methodology_20260626.md §四(此處僅引、不複述)」。(來源:鏡4-CLAUDE＋鏡8-可讀性反膨脹兩發現)
- **修法**:純排版拆子彈(判準零字義變更):#28 首行按「總則(a)-(e)/tie-break/判據＋裁決句/混合任務切兩段/邊界＋反例」拆縮排子 bullet;#17/#29b 同法分句;#11 改標題「Stochastic 多跑＋特徵提拔/經濟驗證關卡」並縮為指標句(三要件細節單住方法論報告與憲章 L93)。

## 附:C23(甲組追加)
- **位置**:docs/datasets_zh.md:563
- **問題**:「當月營收（千元）」為過期視圖;SSOT column_catalog=「當月營收（元）」、DB 實證(2330 2025Q1 月和 831.5B vs 財報 839.3B 比≈0.99)。
- **修法**:該行改「當月營收（元）」。

## 否決紀錄(對抗驗證濾除,勿執行)
- datasets_zh 千元條原案(定性為 doctrine 錯誤)遭否決 1/3——實情=視圖過期,已重定性為 C23。
- CLAUDE #29b「收斂已完成」質疑遭否決 1/3。

**溯源**:9 鏡審查+對抗驗證完整 transcript=session 9009c955 workflow wf_fbbea5f5-1d0;確認 JSON=scratchpad/gov_review_confirmed.json(session-local)。本檔為 SSOT 快照。

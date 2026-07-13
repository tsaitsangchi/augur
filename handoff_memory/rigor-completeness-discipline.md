---
name: rigor-completeness-discipline
description: "用戶 2026-06-16 反覆強調(入憲章#20+CLAUDE v1.5)的工作紀律——完整性是天職、凡事實證不憑「我以為」、真窮舉到真邊界、不自我合理化、可抓即抓真資料；漏做之源"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 59b6aa15-483d-4e47-b40f-7daa0635e8d4
---

用戶 2026-06-16 一輪內 5 次糾正(系統老出錯之源)。核心紀律已入憲章 #20 + CLAUDE v1.5、敵人③長相,此處摘要供 recall:

1. **完整性是執行層(AI)天職、無條件**——「補 X 的 metadata/欄位」＝主動窮舉 X 的每一欄/每一狀態一次補齊到底(一個 design),非用戶指一個漏一個才補一個。**用戶不是你的 QA**。完整資訊更是決策層(用戶)判斷「要不要用/抓」之前提;以「我以為不需要/不重要」預判砍完整＝越權(替用戶決定)＋失職(不給判斷依據)。

2. **凡事完整驗證、嚴禁「我以為」**——任何判斷/解釋/做法/operational 決策先以 probe/API/code/DB 事實驗證;「我以為」(尤「我以為不重要」)是漏做之源。實例:「GoldPrice 我們不抓」是假設(實際 ingest._AGGREGATE_DAILY 有聚合日級存);「earliest 不重要」是假設(實際餵 n_dates 估算)。

3. **真窮舉要試到真邊界**——不能停在假設邊界(慣例值)然後自稱窮舉;連範圍/邊界/慣例值(如 FULL_START=1990)本身都是待驗證對象。實例:earliest floor 用 1990「慣例」截斷 GoldPrice 真資料(真起點 1979),改 1800 sanity + 邊界邏輯才探到真。

4. **見可疑不自我合理化**——可疑結果(如「剛好卡在邊界」)追查到底、不說服自己「正常」(＝#15 自欺)。實例:GoldPrice earliest=1990-02 剛好卡 floor,我曾合理化掉。

5. **可抓即抓真資料、退役 deferral**——「可抓但暫緩(scope待決)」類 placeholder 不該存在;抓法已實證就要有真實抓取的資料/metadata(非 NULL+藉口)。實例:分點/權證 catalog 改走 dedicated endpoint 真實 probe(分點實證 4838 列 7 欄),退役 BACKFILL_DEFERRED 的「可抓但暫緩」reason。

6. **完整性要跨「所有層級/維度」、收尾做全 NULL 稽核**——「中文化」≠ 只欄級,須**表級(table_name_zh)＋欄級(column_name_zh)一次補齊**;補某類 metadata 後**主動掃全 schema 每欄 NULL**(列「應全填 vs 條件性空」、應全填者 0 NULL?),揪出自己沒想到的維度,別等用戶逐一指。實例 2026-06-16:只加 column_name_zh、漏 table_name_zh 被用戶抓「考量不完整」→補後做 dataset_catalog 全 23 欄 NULL 稽核、連帶補 tier(7 表官方無 tier→F/FRED/sponsor 預設)、data_id_source(權證 dedicated→roster) 等用戶還沒問的缺口。

7. **FULL_START refine 之 edge case(2026-06-16 實證,接 #3)**——earliest 卡 FULL_START 須往更早探,但**單一法對不同表型失效**:年逐日窄窗碰 pre-DB 早年假日假陰性(GoldPrice 截 1985)、snapshot 表忽略日期回現值會空探到 floor(FutOptDailyInfo→1900 垃圾)、月頻表窄窗漏點(BusinessIndicator)、寬窗 min(date) 又誤抓單一 artifact(GoldPrice 1970 之 $17 非真金價)。解:**2 個月窗(涵蓋月頻+含工作日)+ 哨兵年 1955 偵 date-insensitive→None + 跳過 dense 起點前的 sparse 雜訊(年逐探遇無資料年即止=dense 真起點)**;國際股(UK/Europe)API 對寬窗行為 erratic、earliest best-effort。

8. **「drop+一次乾淨重建→逐欄 review→修 bug」優於零碎打補丁(用戶 2026-06-16 directive「不要用補的」)**——build 程式做對、單 pass 出完整資料、再逐欄自檢揪 bug;curated 中文入 datasets_zh.md SSOT(非 code dict)。逐欄 review 揪出之系統性 bug:(a) **FULL_START refine 漏 landed 表**——DB min 常是當初 FULL_START sync 截斷、源頭更早(UK DB-min 1990→源頭 1968、US→1928),refine 條件須含 landed + 放寬到「FULL_START 月」(首交易日 01-02 非 01-01);(b) **dirty 欄(契約碼/週選碼/sentinel)樣本剛好純數字→推 NUMERIC**,須強制 VARCHAR 防型別爆炸;(c) **稀疏-windowed 表(月結算 FinalSettle)**單日 probe 漏結算日、寬窗 size-too-large 回 0→須短窗(3月)fallback;(d) 國際股 API 對歷史窗 erratic 間歇回空→retry 辨真空;(e) snapshot 表忽略日期→哨兵年(1955 有資料=date-insensitive)回 None。教訓:**每個 fix 常揭一整類(landed 漏→US/CrudeOil/ExchangeRate 同類);earliest「真起點」須以幣別/契約 id 寬查驗證(ExchangeRate 1990 經驗證為真、非限制)**。

**Why**:用戶系統老出錯之源＝AI 假設驅動漏做;且逼用戶重覆提醒會讓人棄用平台。
**How to apply**:接任務先窮舉完整範圍+所有子需求(含「同類 metadata 的所有層級」);收尾**做全欄 NULL 稽核**自問「還缺哪一步/哪欄/哪維度/哪 edge case?」;凡 NULL/空必有**實證原因**(非「暫緩」藉口);完整性亦須實證(查 schema 全欄逐一確認落地)。連 [[bounded-autonomy-mode]] [[finmind-fetch-methods]]。

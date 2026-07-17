---
name: cross-claim-contradiction-check
description: 逐宣稱對抗驗證抓不到「跨宣稱矛盾」;鐘擺型記憶(曾以為X後來發現不是X)自帶權威口吻最危險;索引/frontmatter/內文會各自漂移且哪個對不固定;無對抗層深讀結論須標驗證級別
metadata: 
  node_type: memory
  type: discipline
  originSessionId: aac75e63-bffa-4a09-be73-f8f4937ad7f1
---

三個 2026-07-17 實證的**驗證盲區**,都不是「不夠努力」造成,是**方法本身的形狀**造成的。

## 1. 對抗驗證是逐宣稱做的,不是逐「跨宣稱」做的
`reports/augur_construction_understanding_20260713.md`(v4)**自身矛盾**:§3.3 說 `features/macro_vintage.py` 07-11 已建;§8.3/§11 說「repo 無」。
- **親驗 §3.3 對**(`ls src/augur/features/macro_vintage.py`＝5376B 存在、commit `abf5da8`)。
- 該矛盾**存活過 58-agent 深讀 + 12 條對抗 REFUTED + 終審 16 修**——因為**子系統章與橫切章從未互相對帳**。
- 已沉默污染下游:一個 6 天前完工的模組被登記成「待 hugo 拍板決策項」。
- **做法**:深讀收尾要有一輪 **cross-claim 對帳**(同一物件被兩章提到 → 兩章結論是否一致?),而非只驗每條宣稱本身。

## 2. 鐘擺型記憶最危險(它自帶糾錯的權威口吻)
`OUT_OF_UNIT` 三次擺動:06-15「都抓得到」→ 06-16「**物理不可行證偽**、退役 BACKFILL_DEFERRED」→ **06-23/24 probe 再翻回「治權級排除」**(親驗 `ingest.py:32-46`:OUT_OF_UNIT 3 表、`BACKFILL_DEFERRED=frozenset()` 空集)。
- 三份記憶(`finmind-fetch-methods`/`ingestion-strengthen-probe-not-enumerate`/`rigor-completeness-discipline`)**全停在中間位置＝方向與現行 code 相反**(2026-07-17 已加更正標)。
- **它們讀起來比一般記憶更可信**——因為在講「我們曾經以為 X、後來發現不是 X」,這種糾錯敘事讓讀者放下戒心。
- **做法**:凡記憶含「證偽/推翻/退役/改名」字樣 → **一律回查現行 code**,別信它是終局。

## 3. 索引 / frontmatter / 內文 三者各自漂移(且哪個對不固定)
2026-07-17 同時實測到三種方向:
- **索引錯、內文對**:`arena-g1g5` frontmatter「D-1~D-5 已拍板」vs 內文「全 7 顆」。
- **索引對、內文錯**:`augur-deliberation-engine` 索引「L2 已掛」(親驗 crontab 15:6 + delib_daily.log 07-17 有輸出＝對),frontmatter 卻「L2 cron 待掛」(錯)。
- **索引與其所指檔互不一致**:MEMORY.md「憲章 v1.20」vs `augur-project-map` 內「v1.24.0」vs 實 **v1.46.0**——三方全錯且互不相同。
- **做法**:更新記憶內文時**同步改 frontmatter description 與 MEMORY.md 索引行**(三處);讀記憶時 frontmatter 與內文打架,**以內文為準**(內文較常被更新)。

## 4. 無對抗層深讀 = 錯誤率須外顯
`refuted=[]` 代表「**沒人去駁**」,不代表「全部通過」。前次同型深讀(58 agent + 完整對抗層)駁回 12 條 high-stakes 宣稱 ≈ **每 5 條錯 1 條**。→ 無對抗層深讀,結論一律標級別:**【親驗】/【單域宣稱】/【索引時效】**,別讓三者混成同一種語氣。**連提案標 A 級都會偏差**(實例:2026-07-17 提案稱「10 個 PG 調優值 live 全回 default」,親驗 maintenance_work_mem 確回 default 但 shared_buffers 160MB/effective_cache_size 5GB 皆非預設值＝部分推翻)。

關聯 [[rigor-completeness-discipline]] [[augur-construction-v4]] [[no-concurrent-agents-same-files]] [[augur-mechanical-gate-gaps]]。

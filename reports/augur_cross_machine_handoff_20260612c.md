# augur 跨機接續 handoff — 對帳總驗 + 全檔讀畢快照(2026-06-12 c 版)

> 接續者(人/AI)**先讀這份**,再讀治權 SSOT。對話一律**繁體中文**。
> 前序:`..._20260612b.md`(夜版)。本份為 **Mac 機實況 + 對帳總驗結果 + 完整理解索引**。
> 數字皆 source-traceable(#15):標 `[DB]`=DB query、`[log]`=driver stdout、`[API]`=user_info/實打。

---

## ⚠️ 0. 最關鍵事實(先看)

1. **本機=Mac(Darwin,`/Users/hugo/project/augur`),非夜版 handoff 所稱「新機從零」**。實查 `[DB]`:
   **15 表 / 97.9M 列、Price 全史到 2026-06-12** —— **遠超夜版記的 WSL2「31M/7 表」**。
   以真兆為據(#15):**這台 Mac 才是當前資料最完整、可開發的機器**;98M 從何而來脈絡只有用戶清楚,不臆測。
2. **這台 sync 遠未完成:只 15/82 表**(schema catalog 可建 82)。B 籌碼大半 / C 部分 / D 可轉債 / E 衍生 /
   F 國際 / G 商品 **共 ~67 表未抓** → IP 健康對後續 sync 至關重要。
3. **FINMIND_TOKEN `2026-06-24` 到期**(Sponsor 6000/hr)`[API]`,剩 ~12 天;全史 sync 須在此前完成。
4. **本 session 末 FinMind data endpoint 被 sustained-throttle**:對帳連跑 56 分鐘 → server 降速(非 ban、非額度;
   metadata endpoint 0.3s 仍可連 `[API]`)→ 已主動停 driver 讓 IP 休養(#25)。**接續前先讓 IP 休息數小時**。
5. **rate 鐵則(承夜版 + 本 session 再證)**:FinMind throttle 的是 **sustained 負載**,非 pace;保守 `≤1/s`
   是奇異點;**一見 throttle 訊號(latency 暴增)就停**,勿硬撐(會惡化成 deep-throttle / ban)。
6. **`.env` 不進 git**:本機已存在且 14 key 齊全 `[API]`(DB 五件套 + FINMIND/FRED/GEMINI/GITHUB)。
   注意 `.env.example` 的 `PROJECT_ROOT=/home/hugo/...`(WSL2)— 本機 config.py 用 `Path(__file__)` 推導,不受影響。

---

## 1. 環境現況(本機已 setup,不需接機)

- venv ✓ / deps ✓(`import psycopg2,pandas,numpy,requests` OK)/ augur 套件可 import ✓ / PostgreSQL 17 ✓。
- 本機 DB `augur` 15 表 `[DB]`:InstitutionalInvestorsBuySell 24.87M · GovBank 13.67M · Price 11.04M ·
  PriceAdj 10.99M · Shareholding 8.65M · BalanceSheet 8.29M · ShortSale 7.68M · PER 7.54M ·
  FinancialStatements 2.69M · CashFlow 2.38M · fred_series 84.7k · TotalInst 26.7k · data_audit_log 25.2k ·
  TaiwanStockInfo 4.14k · pipeline_execution_log 0。
- git:已同步 origin/main `bc5e082`(+8 tag,含 treaty-v1.6.0);治權 SSOT = 靈魂 v1.2.0 / 原則精華 v1.6.0
  (20 條)/ 憲章 v1.6.0 / CLAUDE v1.3 / README。

---

## 2. 本 session 成果

### A. schema 中文註解(已落地,純 DB 無 API)
`scripts/annotate_schema_comments.py` 重跑 → **15 表 / 107 欄 PG COMMENT 已寫入** `[log]`(catalog 81 表,
本機只 15 表 → 只註解現有;無「缺中文」警告)。**全 sync 完成後須重跑(→82 表)**。

### B. 對帳總驗(#7,近期切片 + 低成本表全史)— 完成 9/13 表
新寫 driver **`scripts/reconcile_audit.py`**(複用 reconcile.*、日頻後處理排除未定案緩衝日、未 commit)。
結果 `[log]`:

| 表(7 日頻 PASS,定案日) | matched | 表(FAIL/部分) | 數據 |
|---|---|---|---|
| Price / PER / InstBuySell / TotalInst | 85k/63k/371k/192 | **PriceAdj** ❌ | VM214 EX0 |
| GovBank / ShortSale / Shareholding | 469k/70k/74k | **BalanceSheet** ❌ | VM1533 EX97 MIS221 |
| (定案日 VM0 ∧ EX0) | | **FinancialStatements**(停 90/138) | VM0 EX94 MIS485 |

- **未跑**:CashFlow / FRED(走 FRED 額度、不受 FinMind throttle)/ roster(smoke 已知 **VM1=2936 名冊
  date 06-04→06-12 新鮮度**,非幻像)。
- **重要:GovBank / InstitutionalInvestorsBuySell 本次 PASS** → 夜版 2 類歷史 reconcile artifact
  (寬 PK 數值 / per-stock vs by-date universe)**已修復確認**。

### C. 對帳三類發現(皆非真幻像 EX≈0,且與 F2/F3 設計呼應)
1. **PriceAdj 還原價非 byte-stable**:還原價隨**未來除權息回溯重算**(原始價 Price PASS、還原價 FAIL 佐證)。
   → F3 用 `PriceAdj` log return 算 label 須意識此特性(報酬 SSOT 但歷史值會被改寫;非洩漏,但影響重現/對帳)。
2. **財報季頻:最新季未定案 + API 時間覆蓋邊界**:BalanceSheet 最新季 VM/EX 暴增(restatement + 暫定值);
   FinancialStatements 早期季 EX(API 不回極早 / 下市財報)+ 近期季 MIS(財報還在發布)。→ F2d「發布日 gate」鏡像。
3. **driver 設計疏失(誠實記錄 #15)**:季頻**未排除最新未定案季**(我 smoke 時只測 CashFlow 單季 PASS 就
   過度泛化「季頻都定案」)。修法:季頻也加「排除最近 N 季緩衝」後處理,或排除「當前發布中季別」。
4. **待查**:BalanceSheet **EX97 根因**(疑最新季 DB 暫定值 vs API 撤回/重編)— 需對最新 3 季單獨對帳,
   **待 IP 休養後做**(勿在 throttle 中打)。

### D. 全 55 檔讀畢 → 完整理解已建(本份附「§3 理解索引」作記憶替身)

---

## 3. 完整理解索引(記憶替身;接續者快速 recall)

- **靈魂**:只信真兆。三敵人(①假資料 ②偷看未來 ③自我欺騙)× 三基石(#1 零幻像 / #8 anti-leakage /
  #15 誠實)。北極星自檢:真兆還是假兆(真 API 源?當下可得?out-of-sample 撐住?)。
- **20 原則(v1.6.0)**:A 資料`1-7,17,18` · B 建模`8-12` · C 風控`13-15,19` · D 開發`16,20`(非連續、按新增序)。
- **管線**:`raw→feature→universe→model→validate` + 橫切 core/audit;各層職責不越界。
- **code map(全讀)**:core(config/db/schema/**generic_schema** auto-schema 引擎)· ingestion(**finmind**
  三層限速 `_pace`0.8s→`_quota_gate` 問權威錶→`QUOTA_COOLDOWN`1800s / fred / ingest 守門+OUT_OF_UNIT /
  **sync** adaptive: market→per-stock(canonical 2330)→by-date→by-dim-id)· audit(**reconcile** #7:
  compare/verdict/by_date/market/fred/heal)· features(builder 價量特徵,缺列不補)· universe(core_gate
  純完整度 gate 無評分)· models/evaluation **未建(F3)**。
- **資料地圖(catalog 82 表/665 欄)**:四分類 **P22 個股連續 / E12 事件真零 / X36 市場 context / R12 參照**;
  真排除只 8 intraday(#4);OUT_OF_UNIT 3(券商分點/權證/鉅額,規模暫緩非排除);29+ 表待 by-dim-id 落地。
  **anti-leakage 金礦**:`Dividend.AnnouncementDate/Time`(API 自帶公告時點=零洩漏)>`MonthRevenue.create_time`/
  `Shareholding.RecentlyDeclareDate`(疑 as-of 待證)>財報三表(無公告欄→法定申報期限 lag)>FRED(vintage/ALFRED)。
- **F2 roadmap**:gate 不改、擴 builder + 新 `context_values` 表;分期 F2b 籌碼→F2c 估值→F2d 基本面(發布日 gate)
  →F2e context(FRED vintage)→F2f 事件真零→F2g 衍生/國際/CB。
- **F3 model plan v1.2**:**正名=橫斷面相對強弱排序(非預測股價)**,H∈{5,20,60,252};基準階梯 B0→B1 動能→
  B2 Ridge→**B2.5 標準因子對照**→**M1 GBDT 主軸**→M2 ensemble→M3 transformer(deferred);purged walk-forward
  + core_universe as-of 快照(survivorship);三族消融裁決;**§九自我批判 5 修正**(H=20/60 主戰場 / 共同樣本窗
  鐵則 / conviction 降級 / 成本入 #14 核心 / 消融防共線稀釋誤判)。
- **三族特徵**:第一性原理(七軸:價格/籌碼/價值/缺口/事件/環境/結構)× Pareto(集中度泛函 Gini/HHI/entropy,
  無切點)× 康波(相位/歷時/共振/背離,無固定週期)— 同欄位三 transform 家族,#9 零硬編閾值/零情緒字典。

---

## 4. 接續 TODO(順序)

- [ ] **IP 休養數小時**後再動 FinMind(本 session 末 throttle)。
- [ ] **補完對帳**(IP 恢復後):CashFlow / FRED / roster + FinancialStatements 後段 + **BalanceSheet EX97
      查根因**(對最新 3 季單獨對帳);driver 季頻補「排除未定案季」後處理。
- [ ] **全市場 sync 續跑**(最大缺口:67/82 表未抓):保守 `MIN_INTERVAL=1.0s` + `caffeinate -dimsu` + nohup
      detach + 緊盯 throttle 即停;6/24 前完成。最大未落地=**by-dim-id 通用多維度抓取**(B/C/E/F/G 多表)。
- [ ] 全 sync 完成後:重跑 `annotate_schema_comments.py`(→82 表)+ 全表 #7 對帳總驗。
- [ ] **F3 M-0**(可並行,clean-room 不需放量):label/panel/metric SSOT helpers + core_universe as-of 快照。
- [ ] F2b 籌碼特徵起步(本機 P 類籌碼表已在,可動真資料)。
- [ ] commit/push 一律**用戶明示授權**(本 session 新增 `reconcile_audit.py` + schema COMMENT + 本 handoff
      皆未 commit);clean-room #16;治權判準變更須停下問。

---

## 5. 關鍵檔案 / 本 session 產出

- 本 session 新寫:**`scripts/reconcile_audit.py`**(對帳總驗 driver,未 commit)、本 handoff。
- 既有關鍵:driver `scripts/full_market_sync.py` · 引擎 `src/augur/ingestion/sync.py` ·
  `finmind.py`(限速三層)· 對帳 `audit/reconcile.py` · 註解 `scripts/annotate_schema_comments.py` ·
  治權 5 檔(§1)· 設計 5 報告(F2 roadmap / F3 plan / 特徵三部曲)· schema catalog `..._20260611.md`(82 表)。
- log(本機 /tmp,不進 git):`augur_reconcile_full.log`(前段 4 表)、`augur_reconcile_resume.log`(續跑 9/13)。

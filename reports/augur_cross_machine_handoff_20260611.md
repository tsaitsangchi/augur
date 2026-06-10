# augur 跨機接續 handoff — 執行階段快照 (2026-06-11)

> 接續者(人/AI)**先讀這份**,再讀下方治權 SSOT。對話一律**繁體中文**。
> 前一份一般性 orientation:`reports/augur_cross_machine_handoff_20260610.md`(治權 SSOT 清單 / code 結構 / 三敵人三基石)仍有效,本份只補**目前執行階段**狀態。

---

## ⚠️ 0. 最關鍵警告 — DB 資料**不隨 git 走**

- **`DB_HOST=127.0.0.1`(本機 PostgreSQL)**。本 session 跑了 ~10 小時的全市場 sync,已落地 **13 表 / ~78M 列**,**全部在原本那台 Mac(`caizongyede-MacBook-Pro`)的本機 DB**。
- **git(GitHub)只帶 code / reports / charter / CLAUDE.md**;**`.env`(gitignored,含真 token)與 DB 資料都不在 git**。
- 換機後新電腦的 Postgres 是**空的 / 獨立的** → 那 ~78M 列**不會自動出現**。

**換機後三選項(擇一)**:
1. **留原機跑完**(建議):全市場 sync 仍在原機背景跑(detach + caffeinate,resume-safe,ETA ~1 週)。新電腦只做 code 工作;要用資料時回原機,或日後 `pg_dump` 遷移。
2. **新機從零重跑**:`.env` 設好 + 空 DB → `caffeinate -dimsu nohup bash <wrapper> &` 重跑 `scripts/full_market_sync.py`(又 ~1 週;resume-safe)。
3. **遷移 DB**:原機 `pg_dump` → 新機 `pg_restore`(~78M 列,dump 檔大;最完整但需手動搬)。

---

## 1. 換機怎麼接 code

```bash
git clone https://github.com/tsaitsangchi/augur   # 或 git pull
git checkout main                                  # 最新 commit: fadba1a
# 建 .env(參 .env.example,填真 FINMIND_TOKEN / FRED / DB 五件套);.env 永不進 git
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt  # 或既有 venv
PYTHONPATH=src venv/bin/python -c "import psycopg2,pandas,numpy,requests; print('ok')"
```
- **最新 commit**:`fadba1a`(reconcile _key 修正)。**關鍵 tags**:`reconcile-key-norm-fix-20260611` · `fullsync-launch-20260610` · `schema-catalog-live-20260610` · `treaty-v1.3.0`(治權檔 18 原則)。

## 2. 治權 SSOT(改 code 一律只依這 5 份,clean-room #16)
`docs/系統核心思想_v1.0.0.md`(靈魂)· `docs/原則精華_v1.3.0.md`(**18 條不可違反**;三基石 #1 零幻像 / #8 anti-leakage / #15 誠實)· `docs/系統架構大憲章_v1.3.0.md`(憲法 + 12-PHASE)· `CLAUDE.md` · `README.md`。

---

## 3. 目前執行階段 — 全市場全量 from-zero sync(進行中)

- **驅動**:`scripts/full_market_sync.py`(PHASE 1 infra → 2 seed 名冊 → 2b FRED → 4+5 逐 dataset sync + 逐 dataset #7 byte 對帳 → 問題寫 `reports/augur_fullsync_issues_20260610.md`)。
- **範圍**:全 82 dataset 全史 + FRED 12 series(用戶選「全部含期權/外股/商品」)。
- **進度(2026-06-11 ~07:15)**:**dataset 8/82 完成、第 9 (TaiwanStockPrice) 進行中、已跑 ~593 分鐘**。
- **限速**:`finmind.py MIN_INTERVAL=1.0s`(~3600/hr)。**實測 by-date endpoint 伺服器端 ~4-10s/筆(非限流)→ ETA ~1 週**。
- **防護**:`caffeinate -dimsu`(防睡,已驗 PreventSystemSleep=1)+ `nohup` detach(跨日/跨 session 存活)+ **resume-safe**(中斷重跑自各表 DB `max(date)` / 逐股 max_date 續)。
- **啟動式**(原機重啟或新機重跑):`cd augur && nohup caffeinate -dimsu bash /tmp/augur_fullmarket.sh > /tmp/augur_fullsync.log 2>&1 &`(wrapper 內 `PYTHONPATH=src ./venv/bin/python scripts/full_market_sync.py`)。
- **看進度**:`tail /tmp/augur_fullsync.log`;**問題記錄**:`reports/augur_fullsync_issues_20260610.md`。
- **監看**:本 session 有 Monitor `bj87y1rk0`(每 5 分鐘全狀態 + 即時錯誤),**session 結束即停**(sync 不受影響續跑);新 session 可重掛。

### 已落地 DB(原機 127.0.0.1,13 表 ~78M 列;**不隨 git**)
| 表 | 列數 |
|---|---|
| TaiwanStockInstitutionalInvestorsBuySell | 25,799,985 |
| TaiwanStockGovernmentBankBuySell | 13,685,802 |
| TaiwanStockShareholding | 8,725,271 |
| TaiwanStockBalanceSheet | 8,350,795 |
| TaiwanDailyShortSaleBalances | 7,663,859 |
| TaiwanStockPER | 7,538,239 |
| TaiwanStockPrice | 3,316,136(增長中) |
| TaiwanStockFinancialStatements | 2,703,112 |
| fred_series | 64,902 |
| TaiwanStockTotalInstitutionalInvestors | 26,698 |
| TaiwanStockInfo(名冊) | 4,139 |

---

## 4. 已知問題(2 個 #7 FAIL,**皆 reconcile artifact 非資料問題**;詳 `reports/augur_fullsync_issue_analysis_20260610.md`)

1. **GovBank `VM=0 EX=MIS=412111`**:reconcile `_key` 原用 `str()` → 寬 PK 含數值欄 DB(Decimal)vs API(raw)永不配對。**已修**(`_key`→`_norm`,commit `fadba1a`,synthetic 單測過)。資料乾淨(13.7M 列 0 重複 VM=0)。
2. **InstitutionalInvestorsBuySell `VM=3 EX=0 MIS=2,627,750`**:此表 per-stock 落地(roster ~2,387 檔/日),但 reconcile 用 market by-date(含權證 ~16,800 檔)→ MIS = 非 roster 權證法人資料,augur **正確排除**。VM=3 = 微重述(benign)。**reconcile scope 待修**(per-stock 表應 roster-scoped 對帳)。

> ⚠️ commit `fadba1a` 的 `_key` 修正**未套用於運行中進程**(已載入舊碼)→ 後續 Institutional 類仍會 false-MIS,但已知 artifact。修正惠及未來 from-zero + 跑完後 post-hoc re-verify。

---

## 5. 本 session 關鍵決策 / 學習

- **#18 入憲**(treaty-v1.3.0):抓取依 API 探測決定方式+範圍 / 不空抓;`_bydate_data_start` 改 **backward-probe**(自近往遠探資料邊界,取代會空掃 1990-2020 的 forward-probe)。
- **`ingest.OUT_OF_UNIT` 排除 3**:券商分點(`TradingDailyReport`)/ 權證(`WarrantTradingDailyReport`)/ 鉅額交易(`BlockTradingDailyReport`)—— sub-stock/非股/稀疏,無法不空抓地可靠抓。**GovBank 保留**(by-date)。
- **throttle `1.0s`**(throttle-1.0s tag):0.7s 曾 re-ban、2.0s 過保守 → 1.0s 平衡;若 re-ban 回退 2.0s。
- **schema catalog**(schema-catalog-live):live API 驗證**通用 ingester 共 81 表 / 662 欄**(FinMind 80 + FRED 1),`reports/augur_generic_ingester_schema_catalog_20260610.md`。
- **per-stock roster 排序**:0xxx ETF 在前(無財報/法人)→ per-stock dataset 前段「累計 0 列」為正常,到 1xxx 公司才回升(非 bug)。

## 6. 接續 TODO(待用戶授權,**勿自動 commit/retrain**)
- [ ] sync 跑完(82/82)後:全表 #7 對帳總驗 + 修正版/scoped reconcile re-verify GovBank/Institutional → 應 PASS
- [ ] reconcile per-stock 表改 roster-scoped(修 Issue 2 類);(可選)`bank_name` 入 `KEY_CANDIDATES`
- [ ] 下游階段:feature → universe(核心股 gate)→ model → validate(依憲章 12-PHASE)
- [ ] commit/push 一律須用戶明示授權(§CLAUDE.md);clean-room #16(不讀/移植 stock_backend)

## 7. 關鍵檔案
- 驅動:`scripts/full_market_sync.py` · sync 引擎:`src/augur/ingestion/sync.py`(adaptive 分類 + by-date + backward-probe)· `ingest.py`(OUT_OF_UNIT/intraday 守門)· `finmind.py`(限速/退避)
- 對帳:`src/augur/audit/reconcile.py`(#7 byte 對帳)· schema:`src/augur/core/generic_schema.py`(auto-schema)
- log:`/tmp/augur_fullsync.log` · 問題:`reports/augur_fullsync_issues_20260610.md` · 根因:`reports/augur_fullsync_issue_analysis_20260610.md`

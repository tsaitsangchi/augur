# augur 跨機接續 handoff — 執行階段快照 (2026-06-12)

> 接續者(人/AI)**先讀這份**,再讀治權 SSOT。對話一律**繁體中文**。
> 前序仍有效:`augur_cross_machine_handoff_20260611.md`(setup/結構)+ `..._20260610.md`(三敵人三基石/orientation)。本份補 **2026-06-12 最新執行階段 + 今晚關鍵變更**。

---

## ⚠️ 0. 三個最關鍵警告(先看)

1. **FINMIND_TOKEN 到期 `2026-06-24`(sponsor)** —— 全市場全史 sync 必須在此前跑完。剩 ~12 天。
2. **DB 資料不隨 git 走**：`DB_HOST=127.0.0.1`(本機 PostgreSQL)。git 只帶 code/reports/charter;`.env`(gitignored,真 token)與 DB 列都**不在 git**。換機後新機 Postgres 是**空的**。
3. **本機 FinMind IP 今晚被打進深度 throttle(60s timeout)** —— 因今晚過度試探 rate 上限。**但換機 = 不同 IP = 全新未被罰** → 新機可乾淨跑。**切勿重蹈**:别再 aggressive 測 rate/worker(已證會 throttle、方向錯),用保守 `MIN_INTERVAL=1.0s`(已是 code 預設)。

**換機後 DB 三選項**:
1. **新機從零重跑**(最簡):`.env` + 空 DB → 跑 `scripts/full_market_sync.py`(resume-safe)。**今晚的修法讓 from-zero 快很多**(見 §4)。
2. **遷移 DB**:原機 `pg_dump` → 新機 `pg_restore`(目前 DB 小、僅 ~2 dataset + FRED,dump 不大)。
3. **留原機跑**:但原機 IP throttle 中,需先休養數小時。

---

## 1. 換機接 code

```bash
git clone https://github.com/tsaitsangchi/augur && cd augur   # 或 git pull
git checkout main                          # 最新 commit: a3ac16c
# 建 .env(填真 FINMIND_TOKEN[6/24 到期] / FRED_API_KEY / DB 五件套);永不進 git
python -m venv venv && source venv/bin/activate && pip install -e .
brew install libomp postgresql@17          # macOS OS 依賴(xgboost/lightgbm OpenMP + pg)
PYTHONPATH=src venv/bin/python -c "import psycopg2,pandas,numpy,requests,sklearn; print('ok')"
```
- **最新 commit**:`a3ac16c`(#19 入憲)+ `1054c40`(起點 API 化 + GROUP-BY + FRED 全史)。
- **封存 tag**:**`treaty-v1.5.0`**(本次)· 前序 `treaty-v1.4.0` / `schema-catalog-v1.4.0-20260611` / `throttle-1.0s-20260610`。

## 2. 治權 SSOT(改 code 只依這 5 份,clean-room #16;**版本已升**)
`docs/系統核心思想_v1.1.0.md`(靈魂)· `docs/原則精華_v1.5.0.md`(**19 條不可違反**;三基石 #1 零幻像 / #8 anti-leakage / #15 誠實)· `docs/系統架構大憲章_v1.5.0.md`(憲法 + 12-PHASE)· `CLAUDE.md v1.2`(27 條工具規則)· `README.md`。

---

## 3. 目前執行階段 — 全市場全史 sync(早期、進行中)

- **驅動**:`scripts/full_market_sync.py`(PHASE 1 infra → 2 seed → 2b FRED → 4+5 逐 dataset sync + #7 byte 對帳 → 問題寫 `reports/augur_fullsync_issues_20260610.md`)。全 82 dataset + FRED 12 series。
- **目前進度**:才 **~2/82 dataset + FRED 完成**(GovBank [1/82] + BalanceSheet [2/82] + FRED)。**80 dataset 未抓**。(註:今晚多數時間在排查 sync 慢的原因 + rate 實驗,sync 本身進度有限。)
- **限速**:`finmind.py MIN_INTERVAL=1.0s`(保守、已驗證安全)。**勿改更快**(見 §4 rate 真相)。

### 已落地 DB(本機 127.0.0.1,**不隨 git**;2026-06-12 實查)
| 表 | 列數 | 備註 |
|---|---|---|
| TaiwanStockGovernmentBankBuySell | 13,703,261 | [1/82] by-date 完成 |
| TaiwanStockBalanceSheet | 4,582,198 | [2/82] per-stock(到 2026-03-31)|
| fred_series | 84,732 | **今晚回填全史 1919-2026**(12 series)|
| TaiwanStockInfo(名冊) | 4,140 | seed |
| data_audit_log | 2,747 | infra log |

> 換機從零重跑會重建全部;此表僅供「遷移 vs 重跑」決策參考。

---

## 4. 今晚(6/12)關鍵成果 + 學習 — **接續者必讀**

### A. 程式真修法(已 commit 1054c40,from-zero 會快很多)
1. **起點全面 API 化(#18)**:`_data_era_start` —— per-stock fetch 起點改由 **canon(2330)API 元年**決定(取代寫死 `FULL_START=1990`)。**無資料股(ETF)寬窗空掃 18s → 0.2s(90×)**。實證:0050 從 1990 空掃=18s、從 2012=0.2s;BalanceSheet 元年=2012、5 檔老股驗證 era-uniform(不丟資料)。
2. **GROUP-BY 批量 max_date**:`_per_stock_sync` 開跑前 3101 筆 N+1 `max_date` 查詢 → **單句 `GROUP BY`(~250s → ~0.5s,500×)**。
3. **FRED 全史回填(用戶抓出的 1990 截斷 bug)**:`sync_fred` 改 `start=None` 一律抓全史 → 回填 pre-1990 總經史(實證從 1990 截斷漏 504-3544 列/series;UNRATE 437→941 列、回到 1948)。
4. **`FULL_START` 釐清**:僅 FinMind backward-search/寬窗探測 outer-bound,**非 fetch 起點、非 FRED**(FinMind 無 pre-1990 → 1990 永不截斷;FRED 有 → 用 None)。
5. **thread-safe 並發 `_pace`** + `PER_STOCK_WORKERS=4`:start rate 仍 ≤MIN_INTERVAL(IP 對外速率不變)。

### B. ⚠️ rate 實驗真相(別重蹈)
- **FinMind throttle 的是「sustained 負載」**:burst/短測快(8 並發=39/s、20 股=1.39/s),但**持續跑數分鐘就被降速**(0.6s→soft-throttle 5-18s;持續更久→60s timeout deep-throttle)。
- **pace 不是 binding constraint,sustained-throttle 才是** → 「0.6 vs 0.75 vs 1.0s」對 sustained 殊途同歸;**沒有「又快又持續安全」的點**。
- **奇異點(sustained)= 保守 ≤1/s**。**0.1s+16w 是錯方向**(會 hard-ban)。
- **教訓(已入 #19)**:過度試探 rate 上限會**深化 throttle / 傷資源**;一見 throttle 訊號就該停、讓 IP 休養,而非續衝。**新機 IP 全新,直接保守 1.0s 跑、別測。**

### C. 治權:#19 入憲(treaty-v1.5.0)
**#19 可控風險下逐級逼近最佳奇異點 / 試錯即進步**(原則精華 v1.5.0 / 憲章 v1.5.0 / 靈魂 v1.1.0 / CLAUDE #27):可控風險三要件(可恢復+有界+即時退場)+ 重覆驗證再定論 + **兩條凌駕邊界**(只作用 operational 層;**資料誠實零容忍、不可拿三敵試錯**)。

---

## 5. 接續 TODO(待用戶授權,勿自動 commit/retrain)
- [ ] **續跑全市場 sync**(新機,@1.0s,caffeinate+nohup detach):`scripts/full_market_sync.py`,80 dataset 未抓;6/24 token 到期前完成。
- [ ] 跑完 → 全表 #7 對帳總驗(per-stock 表 reconcile 已 roster-scoped,見前序 handoff)。
- [ ] 下游 12-PHASE:feature → universe(核心股 gate)→ model → validate。
- [ ] commit/push 一律須用戶明示授權;clean-room #16(不讀/移植 stock_backend)。

## 6. 關鍵檔案
- 驅動:`scripts/full_market_sync.py` · sync 引擎:`src/augur/ingestion/sync.py`(`_data_era_start` / GROUP-BY / `sync_fred` 全抓 / adaptive 分類 + by-date + backward-probe)· `ingest.py`(OUT_OF_UNIT/intraday 守門)· `finmind.py`(thread-safe `_pace` / `MIN_INTERVAL=1.0`)· `fred.py`
- 對帳:`src/augur/audit/reconcile.py` · schema:`src/augur/core/generic_schema.py`
- 啟動式:`cd augur && nohup caffeinate -dimsu bash <wrapper> &`(wrapper 內 `PYTHONPATH=src ./venv/bin/python scripts/full_market_sync.py`);看進度 `tail /tmp/augur_fullsync.log`

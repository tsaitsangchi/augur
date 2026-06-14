# augur 全市場全量 sync — 進度封存 / handoff (2026-06-14)

**性質**:from-zero 全市場全史 sync 的 source-traceable 進度封存(#15);供 resume / 跨機接續 / 封存點。
**數字皆實跑**:dataset 進度自 `/tmp/augur_fullsync.log`(driver stdout)、列數自 augur DB `count(*)`、額度自 `/user_info`。

---

## 0. 一句話現況

WSL2 本機 from-zero 全市場 sync(`scripts/full_market_sync.py`,16w/0.8s)：**12/82 dataset 已完成且 #7 對帳 PASS、DB 共 17 表 / 105,847,078 列**;dataset 13 partial,**resume 進行中**。token 6/24 到期(剩 ~10 天)。

## 1. 已完成 12 dataset(#7 對帳 PASS;真=日頻近窗真對帳,空=季頻近窗 0 列見 §3)

| # | dataset | 列數 | 對帳 |
|---|---|---|---|
| 1 | TaiwanStockGovernmentBankBuySell | 13,708,185 | 真 |
| 2 | TaiwanStockBalanceSheet | 8,379,010 | 空(季) |
| 3 | TaiwanDailyShortSaleBalances | 7,685,860 | 真 |
| 4 | TaiwanStockFinancialStatements | 2,692,746 | 空(季) |
| 5 | TaiwanStockInstitutionalInvestorsBuySell | 24,909,065 | 真(最大表) |
| 6 | TaiwanStockTotalInstitutionalInvestors | 26,710 | 真(market) |
| 7 | TaiwanStockShareholding | 8,663,212 | 真 |
| 8 | TaiwanStockPER | 7,556,329 | 真 |
| 9 | TaiwanStockPrice | 11,049,065 | 真 |
| 10 | TaiwanStockPriceAdj | 11,046,832 | 真 |
| 11 | TaiwanStockCashFlowsStatement | 2,372,515 | 空(季) |
| 12 | TaiwanStockMonthRevenue | 474,194 | 真(月,近窗較薄) |

+ `[13] TaiwanStockMarginPurchaseShortSale` partial 7,165,027 列(killed 時 2750/3101 股)· `fred_series` 84,741 · `TaiwanStockInfo` 4,140。

**最大、最重的表(法人 25M、Price/PriceAdj 各 11M、GovBank 13.7M、ShortSale/Shareholding ~8M、PER 7.6M)全部抓完且 PASS。**

## 2. 速率定案:16w / 0.8s(已驗證)

`finmind.MIN_INTERVAL=0.8` + `sync.PER_STOCK_WORKERS=16`。實證 **連續穩跑 10.5 小時、完成 12 大表、0 throttle、0 資料異常**。`_pace` thread-safe → IP 對外 start rate 仍鎖 ~1/0.8s(16 並發只增加在途請求重疊,不提高發送率)。

## 3. ⚠️ 兩個關鍵發現(下個 session 必讀)

### (A) 額度 gate 暫停 ≠ throttle(#20 實證教訓)
`_quota_gate` 在 `/user_info` 錶 ≥5800 時**主動暫停 ~150s**(rolling 視窗退到 ~2900 自動續抓),本次正常 pause↔resume **循環 8 次**。此暫停會讓進度行出現 ~150-160s 的「停頓」——**那是設計行為、非 FinMind throttle,切勿誤判而停 run**。判別:
- latency 暴增 **＋ log 有 `[finmind] …主動暫停` 行 ＋ 無 403** → **正常 gate 暫停**。
- latency 暴增 **＋ 403/timeout ＋ 無 gate 行** → 才是**真 throttle**(此時依 #25 退一級/休養)。

### (B) 季頻表的「#7 對帳 PASS」是近窗空 PASS(attestation 缺口)
`full_market_sync.py` 逐 dataset 對帳用近窗 `RECENT=2026-05-01`,對**日頻表**有效(近期日落窗內=真 byte 對帳);但**季頻表**(BalanceSheet/FinancialStatements/CashFlow,最新季 ≤2026-03-31 在窗外)→ 窗內 0 日 → **空 PASS(0 列被比對)**。實證 BalanceSheet:57 個季末日、近窗 0 個。
→ **季頻表的真 byte-attestation 須跑 `scripts/reconcile_audit.py`**(它對季頻全史對帳 `since=None`、且排除未定案最新季)。全 sync 完成後務必補跑。

## 4. resume / 接續

- **resume-safe**:`scripts/full_market_sync.py`(DB `max(date)` 續 + `ON CONFLICT` 冪等)。中斷後重跑即從 DB 狀態續;已完成 dataset 逐股快速空增量 + 重新對帳帶 current。
- 啟動式(WSL2,主機須設不睡眠):`PYTHONPATH=src setsid nohup venv/bin/python -u scripts/full_market_sync.py > /tmp/augur_fullsync.log 2>&1 < /dev/null &`
- `--new-only`:跳過已有資料之 dataset(省 re-walk;但會跳過 partial 的 dataset 13,須先補完該表再用)。

## 5. 待辦(順序)

- [ ] sync 跑到 82/82(剩 70 個多為小表:籌碼明細/估值/事件 E 類真零/衍生 by-dim-id/國際/商品)。
- [ ] 全 sync 完成 → 跑 `reconcile_audit.py` 補**季頻表全史真對帳**(§3B)+ 重跑 `annotate_schema_comments.py`(→ 全表中文註解)。
- [ ] token 6/24 前完成(sponsor-only dataset 到期後抓不到)。
- [ ] 下游 12-PHASE:feature → universe → model → validate。
- [ ] commit/push 一律用戶明示授權;clean-room #16。

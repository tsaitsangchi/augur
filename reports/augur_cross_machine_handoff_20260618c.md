# augur 跨機交接 — 2026-06-18c(Mac、sync 推進 US by-date + News 修正 commit 待執行)

> 換機接手導航 + 現況快照。**權威永遠是 repo 5 治權檔 + 實查**;DB 與 .env 不隨 git、新機以實查為準。
> 本檔為 `_20260618.md`(Mac)之增量續寫;另有 `_20260618b.md`(WSL 並行主力、不同 token)。

## 0. 一句話現況

Mac mac-resume **from-zero sync 跑到 [24/83] `USStockPrice` by-date**(~1980、~53%;UK [23/83] 完成 2352 萬列 #7 PASS、OptionDaily 3373 萬列 PASS、**禁用閘下連跑 30+ 小時零撞 403**)。本會話另完成 **issue 審查** + **News 以日為最小單位 + coverage 對帳 code 改動**(commit `7650167`、**待 sync 完成執行**)。git HEAD **`7650167`**。

## 1. 自上次 handoff(20260618)後的進展

1. **issue 審查**(commit `14423dd`、tag `augur-issue-status-20260618`):reports/ 下 5 個 issue 檔 ~19 dataset 逐筆狀態實證 → `reports/augur_issue_status_20260618.md`(✅6 閉環 / 🔄2 待 re-verify / ⏳11 待重抓 + commit 索引)。**關鍵洞察**:mac-resume 進程用啟動時舊 code → log 的對帳 FAIL 須當前 code re-verify(fred EX=1 已實證當前 code PASS=vintage 容忍)。
2. **News 以日為最小單位 + coverage 對帳**(commit `7650167`、tag `news-daily-coverage-20260618`):
   - **病根**:News 是秒級時間戳新聞流(`2026-06-17 22:36:12`、distinct date **156 萬**、無數值 value 欄)、漏網 intraday → 違反 #4 日為最小單位 + 不適合逐條 byte 對帳(reconcile_by_date 對 156 萬時間戳逐一打 API → 爆炸 incomplete)。
   - **改動①(ingest)**:News 加入 `_AGGREGATE_DAILY` 用新 `method='all'`(保留同日多則、僅 date 去時間;區別 GoldPrice `close` 取末筆)→ date 聚合到日、推 DATE、同日同 PK upsert 去重。**復用既有 intraday→日機制、不改核心 generic_schema**。
   - **改動②(reconcile/catalog/verify)**:新增 `reconcile_coverage`(按日曆日抽樣比列數量級、不逐條 byte);`_reconcile_scope` 加 `col_types`、無數值 value 欄→`coverage`(Info 因 data_id_source=roster 提前截走、不誤判);`verify` 加 coverage 分支。
   - **smoke test 通過**(語法 + 單元邏輯);**端到端未驗**(見 §3)。
3. **sync 推進**:UK by-date 完成(1968→2026、2352 萬列 #7 PASS、驗證 optimal_mode 國際股修正 + FULL_START refine)→ 現 US by-date(1928→、~1980)。

## 2. ⚠️ News/Institutional 修正「code 已備、待執行」(最重要)

**News code 改好並 commit,但還沒套用到資料**(實證:News DB date 仍 `varchar`、distinct 156 萬、catalog scope 仍 `by-date`)。原因:重建要打 FinMind 重抓 News、不宜跟正在跑的 US by-date 並發(#24)。**probe.sh 顯示的「對帳 FAIL 2」= log 歷史(舊 code 跑 [5/83] Institutional + [22/83] News 寫的 2 行)、非即時、不會自己消失**,須 sync 完成後執行重建 + re-verify 才變 PASS。

## 3. 接續 TODO(待 mac-resume from-zero 跑完)

1. **執行 News 修正**:重抓/重建 `TaiwanStockNews`(新 ingest 自動 date 聚合到日)→ 重 build catalog(News `reconcile_scope` 自動變 `coverage`)→ `reconcile_audit` 驗證 News coverage PASS。
2. **Institutional VM=1 heal**:`reconcile.heal_by_date`(per-stock 重抓覆蓋為 API 當前、非 hand-patch #12);殘 VM=1 = 近日修訂真差異。
3. 全表 #7 對帳乾淨(`scripts/reconcile_audit.py`、含 vintage/per-stock/by-dim-id/coverage 新對帳)→ 解凍 F2/F3 → **F3 models + evaluation**。

## 4. git 現狀

- HEAD **`7650167`**(已 push)。本 session tags:`augur-issue-status-20260618`、`news-daily-coverage-20260618`。
- ⚠️ **`finmind.py` 禁用閘特例仍本地未 commit**(Mac token user_count 黑箱;別機 token 正常用 git 原版主動額度閘、黑箱才參考此改、`git restore` 還原)。
- DB 不隨 git:Mac DB 31 表(US by-date 進行中)。一律實查。

## 5. 換機第一步

```bash
git clone https://github.com/tsaitsangchi/augur.git && git checkout main   # HEAD=7650167
python -m venv venv && source venv/bin/activate && pip install -e .
cp .env.example .env   # DB_* / FINMIND_TOKEN(2026-06-24 到期) / FRED_API_KEY
PYTHONPATH=src venv/bin/python -m pytest tests/ -q
```
新機 `finmind.py` gate:token user_count 正常用 git 原版;黑箱卡死才參考 Mac 禁用改法(§4)。

> 放量 / commit / push 一律須用戶明示授權。clean-room #16:零參考 stock_backend。

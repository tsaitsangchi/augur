# augur 跨機交接 — 2026-06-17

> 換另一台電腦繼續本專案的接手指南。**權威永遠是 repo 的 5 治權檔 + 實查**;此為導航 + 現況快照。
> ⚠️ **DB 與 .env 不隨 git(每機獨立)→ 新機永遠以實查為準、勿照抄列數。**

## 0. 一句話現況

本機 Mac 正在跑**從零 clean-rebuild**(drop 1.0 億列 → build_catalog 新代碼 → full_market_sync catalog 驅動全史 + 逐 dataset #7 byte 對帳)。本會話發現+修一個**國際股漏抓 bug**(`catalog.optimal_mode`)、已 push。git HEAD **`184cd7d`**(已 push)、封存 tag **`catalog-intl-fix-20260617`**。

## 1. 換機第一步(取 code)

```bash
git clone https://github.com/tsaitsangchi/augur.git   # 或既有 repo git pull
git checkout main                                      # HEAD = 184cd7d
git tag -l | grep catalog-intl-fix-20260617           # 確認封存點
python -m venv venv && source venv/bin/activate && pip install -e .
cp .env.example .env   # 填 DB_* / FINMIND_TOKEN / FRED_API_KEY(.env 不進 git)
PYTHONPATH=src venv/bin/python -m pytest tests/ -q     # smoke
```
**先實查新機 DB**(勿假設空/滿):`select count(*) from pg_stat_user_tables where n_live_tup>0`。

## 2. 本會話(2026-06-17)做了什麼

1. **讀取全 74 檔 onboard** + 更新記憶(校正 OUT_OF_UNIT→BACKFILL_DEFERRED、MIN_INTERVAL 0.7、CLAUDE v1.5)。
2. **發現+修 `optimal_mode` 國際股 bug(核心)**:UK/Europe/US/Japan Price 之 `data_id_source="none"`(by-date 全市場探測命中)但 `n_stocks` 誤填台股 roster 3102 → optimal_mode 選 per-stock → `sync._sync_by_plan` 用**台股 roster** 抓國際股 → **0 列漏抓**。鐵證:UK by-date 5158 列/日 vs per-stock 台股 2330=**0** 列。修:per-stock 候選**僅 `data_id_source="roster"`(台股 canonical 命中)時加入**,`src="none"` 走 by-date。台股不受影響。驗證:UK/US 重 build 後 fetch_mode=by-date、真起點 US 1928/UK 1968。commit `184cd7d`。
3. **啟動從零 clean-rebuild**(用戶授權 drop 1.0 億列不備份、新代碼最乾淨):drop → seed roster 3102 → build_catalog(新代碼 refined earliest)→ full_market_sync(PHASE 1-5)。

## 3. ⭐ 本機 clean-rebuild 進行中(本機 DB、不隨 git)

- **driver**:`/tmp/augur_clean_rebuild.py`(一次性、不進 git):drop 全部 → seed roster → build_catalog → `full_market_sync.main()`。問題寫 `reports/augur_fullsync_issues_20260616.md`。
- **進度(實查、勿照抄;~12h 時點)**:**~14/83 dataset、對帳 12 PASS / 1 FAIL、錯誤 0**。已完成:GovBank/BalanceSheet/FinancialStatements/CashFlows(財報三表)/Institutional(24.9M)/InstitutionalWide/TotalInstitutional/ShortSale/PER/Price(11M)/PriceAdj(11M)/MonthRevenue/Shareholding(8.75M)…;當前 MarginPurchaseShortSale per-stock。
- **防護**:`caffeinate -dimsu nohup`(過夜不睡、**session 結束仍續跑**)+ SHMM(主心跳 `b5pkmxdsk`/watchdog `bqksj3kqt`,**Claude session 結束則停、nohup 進程不受影響**)+ resume-safe(中斷重跑:sync DB-driven resume + 冪等)。
- **log**:`/tmp/augur_clean_rebuild.log`(`tail -f` 可看)。
- **換機後本機處置**:clean-rebuild nohup 自會跑完(**還要 ~20-30h**、含國際股 by-date ~12h);但無 Claude 監控 → 手動查 log/DB。跑完 DB 全表完整(catalog 驅動正解、**國際股 by-date 抓全**、FULL_START 真起點、財報三表 per-stock)。

## 4. 換機 DB 兩方案

- **方案 A(等本機跑完 → pg_dump 搬)**:本機 clean-rebuild 跑完(~20-30h)→ `pg_dump -Fc` → 傳新機 `pg_restore`。免重抓、保完整 + 已驗對帳。
- **方案 B(新機從零重抓)**:新機跑 `build_catalog.py` + 仿 driver 跑 full_market_sync(新代碼 184cd7d 正解)。⚠️ **FinMind token 2026-06-24 到期(剩 7 天)**→ 走 B 須趕到期前完成 sponsor-only(分點/snapshot/法人 by-date/可轉債/八大行庫)。

## 5. 關鍵知識(記憶 machine-local、這裡轉移)

- **optimal_mode 國際股修正**(`184cd7d`):per-stock 候選僅 `src="roster"`、國際股(src=none、by-date 全市場可行)走 by-date。
- **ShortSale 對帳 EX=68**(唯一 FAIL):**VM=0(值無幻像)** + EX=68(DB 有 API 無、疑已下市股合法歷史/對帳近窗 scope)→ #7 紅旗「不自動補刪、調查根因」、待人判(B 對帳方法學)。**非值造假**。
- **FULL_START refine**(`_refine_earliest_below`):API 以 start_date 截斷 → 真起點往更早探。US 1928/UK 1968/GoldPrice 1979/Europe 1980/CrudeOil 1986/BusinessIndicator 1982。
- **catalog 驅動 sync**:讀 `dataset_catalog.fetch_mode` 走正解;catalog DB-local、新機須重跑 `build_catalog.py`。BACKFILL_DEFERRED 3 表(券商分點/權證/鉅額)不自動全史抓(可抓、scope 待決)。
- **FinMind 限速**:三層防護(`_pace` 0.7s → `_quota_gate` 問錶 → 403 冷卻);額度 user_count rolling、問 `_user_quota` 讀錶;見訊號即停。

## 6. 治權現狀

靈魂 **v1.2.0** · 原則精華 **v1.6.0**(20 條) · 憲章 **v1.8.0** · CLAUDE **v1.5**(#20 執行層天職＝確保完整性) · README。三敵(#1/#8/#15)。

## 7. 接續 TODO

1. **本機**:clean-rebuild 跑完 → 驗證全表完整 + 全表 #7 對帳乾淨(`scripts/reconcile_audit.py` 全史對帳)。
2. **對帳紅旗人判**:ShortSale EX=68 等(查是否已下市;B 對帳方法學:reconcile scope/季頻/PriceAdj 回溯)。
3. **全表完整 + 對帳乾淨 → 才解凍 F2/F3**(見 downstream-frozen 鐵則)。
4. **F3 models + evaluation**(PHASE 10-11、`src/augur/models/`+`evaluation/` 空 = 下一主階段);計畫見 `reports/augur_f3_model_plan_three_thoughts_20260612.md`。

> 放量 / commit / push 一律須用戶明示授權。clean-room #16:零參考 stock_backend。

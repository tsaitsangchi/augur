# augur 跨機交接 — 2026-06-17（WSL 機，下午更新）

> 換另一台電腦繼續本專案的接手指南。**權威永遠是 repo 的 5 治權檔 + 實查**；此為導航 + 現況快照。
> ⚠️ **DB 與 .env 不隨 git（每機獨立）→ 新機永遠以實查為準、勿照抄列數。**
> （本檔取代同日稍早 Mac 版內容；git 歷史保留舊版。）

## 0. 一句話現況

本機（**WSL2/Linux**）正在跑**從零 clean-rebuild**（drop → build_catalog → full_market_sync catalog 驅動全史 + 逐 dataset #7 byte 對帳）。本會話**發現並修正一個對帳方法 bug**：roster-scoped（per-stock 落地）表原走 by-date 重抓對帳，因 FinMind 兩端點值差 → 假 VM（三大法人 VM=73）。已新增 `reconcile_per_stock` 對齊抓取端點、實證 **VM 73→0 乾淨 PASS**、commit+push+tag。git HEAD **`e8ef8c4`**、封存 tag **`reconcile-perstock-fix-20260617`**。

## 1. 換機第一步（取 code）

```bash
git clone https://github.com/tsaitsangchi/augur.git   # 或既有 repo git pull
git checkout main                                      # HEAD = e8ef8c4
git tag -l | grep reconcile-perstock-fix-20260617      # 確認封存點
python -m venv venv && source venv/bin/activate && pip install -e .
cp .env.example .env   # 填 DB_* / FINMIND_TOKEN / FRED_API_KEY（.env 不進 git）
PYTHONPATH=src venv/bin/python -m pytest tests/ -q     # smoke
```
**先實查新機 DB**（勿假設空/滿）：`select count(*),sum(n_live_tup) from pg_stat_user_tables where n_live_tup>0`。

## 2. 本會話（2026-06-17 WSL）做了什麼

1. **確認此 WSL 為當前作業機**、kill 舊程式、從零啟動 clean-rebuild（setsid 背景、survive session/shell 結束）。
2. **發現+解讀+修正 reconcile 方法 bug（核心）**：
   - 現象：`TaiwanStockInstitutionalInvestorsBuySell` #7 對帳 FAIL `VM=73 EX=0 MIS=0`（24.9M 列中）。
   - 實證根因（零 AI 臆測）：該表 **per-stock 抓**（`fetch(data_id=股)`）但 `reconcile_by_date` 用 **by-date 重抓**（`fetch(start_date=d,end_date=d)`）對帳——**兩個不同 FinMind 端點**，對 ~73 列 (股,日,法人) 回值有極小差 → 假 VM。佐證：同源 Wide 表 by-date 對帳 PASS；長↔Wide 在 DB 內逐欄互證（present 值全等，差異僅長格式省略「當日零活動」投資人別列）。
   - `verify()` 原僅 `_has_date` 路由、**未讀 catalog `reconcile_scope`** → 34 個 roster-scoped 表全錯走 by-date。
   - 修：新增 `reconcile.reconcile_per_stock`（per-stock 重抓、對齊寫入端點；等距抽樣 sample_n；end_date 上限=DB 最新日，對齊 by_date/fred 同窗、免同日假 MIS）；`full_market_sync.verify()` 改依 `reconcile_scope` 路由（roster-scoped → per-stock）。
   - **驗證（用戶決策提前、與 sync 並發、實測無 403）**：sample 60 →舊 by-date `VM=73` → 新 per-stock **`VM=0 MIS=0 EX=0 verdict.passed=True`**。**資料本忠實（VM=0），原 VM=73 為對帳法端點差、非幻像。**
   - commit `e8ef8c4` + tag `reconcile-perstock-fix-20260617`（已 push）。

## 3. ⭐ 本機 clean-rebuild 進行中（本機 DB、不隨 git）

- **driver**：`/tmp/augur_clean_rebuild_wsl.py`（一次性、**不進 git**）：drop 全表 → seed roster → build_catalog → `full_market_sync`（PHASE 1-5）。
- **啟動法（resume-safe / survive session）**：`PYTHONPATH=src setsid venv/bin/python -u /tmp/augur_clean_rebuild_wsl.py > /tmp/augur_clean_rebuild_wsl.log 2>&1 < /dev/null &` 後 `disown`。
- **進度（實查、勿照抄；~8.8h 時點）**：**8/83 dataset、#7 對帳 PASS 7 / FAIL 1（FAIL=三大法人 VM=73，已修+驗，資料無誤）、護欄 0**。已完成：GovBank/BalanceSheet/ShortSale/FinancialStatements/Institutional(24.9M)/InstitutionalWide(5.5M)/TotalInstitutional/Shareholding(8.75M)；當前 PER per-stock。DB **15 表 ~75.8M 列、成長中**。
- **log**：`/tmp/augur_clean_rebuild_wsl.log`（`tail -f`）。問題寫 `reports/augur_fullsync_issues_20260613.md`（**sync 寫入中、未 commit**；全跑完才提交完整紀錄）。
- **⚠️ 注意**：此 run 用**舊 by-date 對帳**（修法 commit 時模組已載入、不影響進行中 run）→ roster-scoped 表的 #7 仍可能標假 VM（資料無誤）。新機若**重跑**（方案 B、code e8ef8c4）則自動走**修好的 per-stock 對帳**、#7 更乾淨。
- **防睡眠（WSL2 關鍵）**：setsid 擋得住 Claude session/shell 結束，但**擋不住 Windows 主機睡眠**→ 用戶須確保 **Windows 電源設定不休眠/不睡**，否則 WSL2 連同 sync 一起被掛起。長跑 resume-safe（中斷重跑：sync DB-driven resume + 冪等 upsert）。

## 4. 換機 DB 兩方案

- **方案 A（本機跑完 → pg_dump 搬）**：本機 clean-rebuild 跑完（還要 ~10-20h）→ `pg_dump -Fc` → 傳新機 `pg_restore`。免重抓、保完整。注意 issues 報告會含三大法人 VM=73（舊對帳法的假旗、資料無誤）。
- **方案 B（新機從零重抓、推薦給乾淨對帳）**：新機跑 build_catalog + 仿 driver 跑 full_market_sync（code e8ef8c4 = **修好的 per-stock 對帳**）。⚠️ **FinMind token 2026-06-24 到期（剩 ~7 天）**→ 走 B 須趕到期前完成 sponsor-only（分點/snapshot/法人 by-date/可轉債/八大行庫）。

## 5. 關鍵知識（記憶 machine-local、這裡轉移）

- **reconcile per-stock 修法**（`e8ef8c4`）：per-stock 抓的表用 by-date 重抓對帳會因兩端點值差→假 VM；解＝`reconcile_per_stock` 對齊端點（同 data_id 重抓）。路由依 catalog `reconcile_scope`（roster-scoped → per-stock）。
- **FinMind 長格式省略零列**：`InstitutionalInvestorsBuySell`（長）省略「當日零活動」投資人別列（Wide 顯式存 0）；對帳 end_date 須上限=DB 最新日，免同日 API 較新→假 MIS。
- **技巧**：長↔Wide 可在 DB 內逐欄互證 writer（**零 API**），快速排除「資料造假」。
- **FULL_START refine**（`_refine_earliest_below`）：US 1928/UK 1968/GoldPrice 1979/Europe 1980/CrudeOil 1986/BusinessIndicator 1982。
- **optimal_mode 國際股修正**（`184cd7d`，前次）：per-stock 候選僅 `data_id_source="roster"`、國際股（src=none）走 by-date。
- **FinMind 限速**：三層防護（`_pace` 0.7s → `_quota_gate` 問錶 → 403 冷卻 1800s）；額度 rolling 視窗、問 `/user_info` 讀錶；**錶有雜訊→以 DB 列數成長為「真在抓」訊號**；見訊號即停。gate 暫停（額度≥5800 自停、退≤2900 自續、每輪 ~27-32 分）≠ throttle。

## 6. 治權現狀

靈魂 **v1.2.0** · 原則精華 **v1.6.0**（20 條）· 憲章 **v1.8.0** · CLAUDE **v1.5**（#20 執行層天職＝確保完整性）· README。三敵（#1 零幻像/#8 anti-leakage/#15 誠實）。

## 7. 接續 TODO

1. **本機/接手**：clean-rebuild 跑完 → commit 完整 issues 報告 + 全表 #7 對帳稽核（`scripts/reconcile_audit.py` 全史；roster-scoped 表現走 per-stock）。
2. **寫 memory（durable）**：reconcile per-stock 修法、FinMind 長格式省略零列、長↔Wide 互證技巧。
3. **全表完整 + 對帳乾淨 → 才解凍 F2/F3**（downstream-frozen 鐵則）。
4. **F3 models + evaluation**（PHASE 10-11、`src/augur/models/`+`evaluation/` 空 = 下一主階段）；計畫見 `reports/augur_f3_model_plan_three_thoughts_20260612.md`。

> 放量 / commit / push 一律須用戶明示授權。clean-room #16：零參考 stock_backend。

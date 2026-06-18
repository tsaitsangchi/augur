# augur 重開機續跑指南 — 2026-06-18（WSL gated 全 re-run 中途 kill）

> 重開機清 `/tmp`（driver + log 消失）；**DB + git code 持久**。此檔＝重開機後續跑步驟。
> ⚠️ DB 不隨 git、以實查為準。

## 0. 一句話現況
gated 全 re-run 進行中、重開機前 kill：**5/83 完成、PASS 4 / FAIL 1**（Institutional benign 修訂漂移）、**0 真 403**、gate 暫停 3 次（健康）。已完成並 #7 對帳：1 GovBank · 2 BalanceSheet · 3 DailyShortSale · 4 FinancialStatements · 5 Institutional。kill 時 dataset 6 `InstitutionalInvestorsBuySellWide` ~90%。

## 1. 持久 vs 消失
- ✅ **持久**：DB（**118.86M 列 / 28 表**；datasets 1-5 re-verified + 原 clean-rebuild 之 1-20+OptionDaily 部分；**catalog 9 列 reconcile_scope 修正已落 DB**）；git code（HEAD **`7ff03f9`** 已 push origin、tag **`reconcile-scope-fixes-20260618`** 已 push）。
- ❌ **消失**（/tmp 清）：`/tmp/augur_resume_gated.py`、`/tmp/augur_resume_gated.log`、monitor 暫存。

## 2. ⚠️ gate 設定（重要、勿改）
`finmind.py` = git 原版**主動額度閘啟用**。我的 WSL token meter **為真**（會撞 6000 觸真 403）→ **需 gate 擋 403**。2026-06-18 禁閘實驗失敗（32 worker 全撞 403）已還原。**重開機後勿禁閘**。

## 3. 重開機後續跑步驟
1. **確認服務**：PostgreSQL 起來 → `cd /home/hugo/project/augur && PYTHONPATH=src venv/bin/python -c "from augur.core import db; db.connect(); print('DB ok')"`
2. **#25 放量前先探 IP 健康**（單股單日、勿略）：
   ```bash
   PYTHONPATH=src venv/bin/python -c "from augur.ingestion import finmind; print(len(finmind.fetch('TaiwanStockPrice',data_id='2330',start_date='2026-06-16',end_date='2026-06-16')),'列 → IP ok')"
   ```
   回 1 列＝健康才放量；403/空＝休養。
3. **重建 resume driver**（/tmp 已清）：
   ```python
   # 存成 /tmp/augur_resume_gated.py
   import sys, runpy
   sys.argv = ["full_market_sync.py"]
   runpy.run_path("scripts/full_market_sync.py", run_name="__main__")
   ```
4. **啟動**（gated、不 drop、背景 setsid）：
   ```bash
   cd /home/hugo/project/augur
   PYTHONPATH=src setsid venv/bin/python -u /tmp/augur_resume_gated.py > /tmp/augur_resume_gated.log 2>&1 < /dev/null &
   ```
   - `full_market_sync.main()` 從 dataset 1 re-run（DB-driven resume：已完成表 incremental 重抓 + re-reconcile；re-verify 1-5 again ~2-3h + 續 6-83）。用戶選 **A 徹底**。
   - 加速替代：加 `--new-only`（跳過已有資料表、不 re-verify；但會跳過半成品 OptionDaily、需另補）。

## 4. 已知 benign（非問題、勿誤判）
- per-stock 日表（Institutional/Price/PriceAdj/Shareholding…）reconcile 殘**小 VM = 修訂漂移**（TWSE 持續修訂近日值；**EX=0 無幻像、資料抓取時 byte-faithful**）。非缺口、非幻像。要 VM=0 須最終對帳前再 heal（但又漂）。
- gate 暫停（meter ≥5800 → 暫停、退 ≤2900 續）＝預期擋 403、非異常。

## 5. TODO（續跑後）
1. gated run 完成 6-83 → 最終 issues 報告 attestation（commit + push、#14 授權）。
2. 寫 memory durable learnings：①禁閘只適黑箱 meter token、真 meter token 需 gate ②catalog reconcile_scope 須對齊 fetch_mode（非 data_id_source）③最新日 preliminary→final（per-stock 抓當日法人未定案）④per-stock 日表修訂漂移＝benign ⑤reconcile_by_dim_id 逐維度 id 對帳。
3. **F3 models + evaluation**（下一主階段、`models`/`evaluation` 空、PHASE 10-11）。

## 6. 本 session（2026-06-18）做了什麼
pull Mac 3 commit（FRED vintage）→ 禁閘實驗失敗+還原 → Institutional heal（VM=87→0）→ issue 全稽核（reports/ 5 個 issue 檔全核對、分 3 類全處理）→ 揪+修 catalog 2+1 bug（8 表 by-date/roster-scoped、by-dim-id 表、TotalReturnIndex）→ reconcile_by_dim_id 新增 → commit `7ff03f9` + tag。權威：repo 5 治權檔 + 實查。

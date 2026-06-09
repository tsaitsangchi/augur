# Augur 全市場全史 sync — 抓取過程問題記錄（2026-06-09）

**用途**：記錄 augur 從零建表 + 全史 sync 嘗試過程**實際遭遇的問題、根因、修法、現況**（供 re-launch 與跨機接續直接照走）。
**誠實聲明（#15 / §一.10）**：全部問題/error/數字皆**實跑 source-traceable**（stdout / DB query / API 回應）；全史 sync **未完成**（IP 暫時限速中斷，待解封 re-launch）。

---

## §0 背景

承用戶指令「建 87 表 + 抓取驗證 → 後續全市場全史 sync」。流程:two-round live probe → 取樣建表驗證(85 表)→ 清空 augur db → 啟動全史 sync。本檔記錄此過程的問題。

## §1 遭遇問題 → 根因 → 修法（依實跑順序）

### 問題 1：augur/.env 誤指 stock_backend 的 `stock` DB（clean-room #16 違規）
- **現象**：augur 程式連到的 DB 有 17 表 / 81.5M 列 + 原生 `FredData`/`fetch_log`/`stocks`——全是 stock_backend 的資料。
- **根因**：augur/.env 是**整份複製 stock_backend 的 .env**（`DB_NAME=stock`/`DB_USER=stock`/`PROJECT_ROOT=…/stock_backend`），未切到獨立 augur db。
- **修法**：用戶將 .env 改為 `DB_NAME/DB_USER/DB_PASSWORD=augur`；驗證 `current_database()=augur`、0 表、無 shell env override。stock db 全程只被 SELECT、未受影響。

### 問題 2：全史 sync 驅動腳本缺 PHASE 1 → `data_audit_log` does not exist
- **現象**：sync 啟動數秒即崩;`seed_roster` 第一筆 ingest 之 `store()` 寫 `data_audit_log` → `psycopg2.errors.UndefinedTable`。
- **根因**：清空 augur db 後 2 個 log 表也沒了;`sync.sync_all` 是 **PHASE 2-4**（不含 PHASE 1 infra bootstrap）;驅動腳本漏了先建 log 表。整個 transaction rollback → augur db 仍 0 表（無殘留）。
- **修法（驅動腳本）**：`sync_all` 前先 `schema.bootstrap_infra(cur)` 建 2 log 表（對齊 12-PHASE PHASE 1→2-4）。修後:PHASE 1 ✅ → PHASE 2 seed `TaiwanStockInfo` ✅ → PHASE 4 起跑。

### 問題 3：FinMind IP 暫時限速封鎖（403 ip banned）— 全史 sync 中斷
- **現象**：PHASE 4 第一個 dataset 起 sync 進程 `STAT=Ss`/cpu 0%/6 分無進度;獨立快測 `finmind.fetch` 回 **`status=403 msg=ip banned`**（0.2s）;`user_info` 回 **`{'msg':'ip banned','status':403,'retry_after':1408}`**。
- **性質（§一.9）**：**暫時 IP 速率封鎖,`retry_after`≈23.5 分自動解 → 屬「可重試」非「永久 blocked」**。**接口/token/tier 皆正常**（probe + 85 表 build 已證實可抓）;純 IP 短時請求量過高。
- **根因（時間線）**：同 IP 今日累積用量過大 —— stock_backend 5h sync(81.5M 列,workers=4)+ augur 兩輪 probe(~94 call)+ 85 表 build(~82 call,含大窗 dataset)+ **build 後無間隔連續啟動/重啟全史(每次重跑 seed + PHASE 4 探測)**之短時 burst → 越過 FinMind IP 限速線。
- **處置**：停止 sync（勿再 hammer 被封 IP）+ 停 HB;augur db 保留 PHASE 1+2 之 3 表（名冊 + 2 log）供 resume。

## §2 已驗證 OK（非問題,佐證機制正確）

- **取樣建表驗證**:清空隔離之 augur db generic 逐表建 → **85 表 / 0 失敗 / ~2.18M 取樣列**（82 FinMind + fred_series + 2 log;2 sponsor-tier 無資料未建）。
- **PHASE 1+2**:log 表 bootstrap + `TaiwanStockInfo` seed 皆成功。
- → 抓取/建表/落地/稽核留痕全鏈**已驗證可運作**;全史唯一阻斷為外部 IP 限速。

## §3 教訓 / 待修（re-launch 前）

1. ~~**augur `finmind.py` 缺主動限速**~~ **【已修 + 入憲,2026-06-09】**:已於 `finmind.py` 加 `_pace()` 主動限速（0.7s 間隔,上限 ~5100/hr）+ honor `retry_after`（402/429/403）;並**入憲為原則 #17「API 速率公民 / 主動限速」**（原則精華 + 憲章 v1.2.0）。全史 re-launch 時 throttle 內建保護,不再 burst 封;驗證與全史走同一 `fetch`、同一限速。
2. **長跑前拉開間隔**:重操作（build / 全史）間應留冷卻,勿在「燙」IP 上連續 burst。
3. **re-launch 策略**:待 IP 解封 + 今日累積用量老化（建議過數小時/過夜）再跑;driver 已含 PHASE 1;per-stock dataset DB-driven resume 會接續（market dataset 重抓）。

## §4 現況

- augur db:3 表（`TaiwanStockInfo` + 2 log;PHASE 1+2 成果,保留供 resume）。
- stock_backend `stock` db:未受影響。
- 全史 sync:**未完成,待 IP 解封 re-launch**（不預先宣稱完成,§一.10 / 無 aspirational #15）。

**事實來源（§一.10）**：問題/error 自實跑 stdout（`/tmp/augur_fullsync.log` traceback）;IP ban 自 `finmind.fetch` + `user_info` API 回應（`status=403`/`retry_after=1408`）;表數/列數自 DB query;build 結果自 `/tmp/augur_build_result.json` + log。

# augur 跨機接力 handoff (2026-06-10)

**用途**：用戶換另一台電腦繼續本專案。新機 `git clone` 後**先讀此檔 + 5 治權檔**，再照下方設置 → 接續。
**誠實聲明（#15）**：本檔數字皆實跑——git/tag 自 repo、列數自 augur DB READ-ONLY query、sync 進度自 log。

---

## 0. 一句話
augur＝stock_backend 的 **clean-room** 重啟，「只用真實資料、誠實預測台股」。管線 `raw→feature→universe→model→validate` + core/audit。**F0/F1/F2/F4-audit 已建並 committed；F3（models+evaluation）待做**；全市場全量 sync 在**舊機**執行中（DB 不在 git → 新機需重抓或轉移）。

## 1. git 接力點
- **clone**：`git clone https://github.com/tsaitsangchi/augur.git`（branch `main`）
- **HEAD**：`bfc33f1`
- **關鍵 tags**：`treaty-v1.2.0`（治權檔）· `schema-catalog-v1.1`（80表 schema 目錄）· `f0-f1-v0.1.0`（地基+ingestion）· `f1-bydate-audit-v0.2.0`（by-date增量+對帳/heal）· `f2-features-universe-v0.3.0`（特徵+核心gate）· `fullsync-progress-20260610`（sync 進度快照）

## 2. 先讀（治權 SSOT，改 code 一律只依這 5 份）
`docs/系統核心思想_v1.0.0.md`（靈魂）· `docs/原則精華_v1.2.0.md`（**17 條不可違反**）· `docs/系統架構大憲章_v1.2.0.md`（憲法+12-PHASE）· `CLAUDE.md`（AI 工具規則）· `README.md`。
三敵人×三基石：**#1 零幻像 / #8 anti-leakage / #15 誠實**。**#16 clean-room：產生 augur code 絕不讀/移植 stock_backend**。對話**繁體中文**。

## 3. 已建 code（committed，全 clean-room，14 檔）
| 層 | 檔 | 內容 |
|---|---|---|
| core | `config/db/generic_schema/schema.py` | 設定/連線/auto-schema引擎(infer/detect_keys require/ensure/upsert dedup)/infra DDL+DB-derived schema |
| ingestion | `finmind.py`(主動限速)·`fred.py`(只存series_id/date/value)·`ingest.py`(#4 intraday守門)·`sync.py`(seed/列舉/per-stock canonical-2330-probe/**sync_by_date 全市場增量**/sync_all_by_date) | |
| audit | `reconcile.py` | #7 DB↔API byte對帳(matched/VM/MIS/EX)+per_date+fixable/flagged+**heal_by_date** |
| features | `builder.py` | **14 source-pure 價量特徵**(缺列/無hardcoded/anti-leakage) |
| universe | `core_gate.py` | **純完整度 gate**(無評分排名/pan-historical/反硬編canonical) |
| scripts | `full_market_sync.py`(從零全量+逐dataset#7對帳+問題記錄)·`daily_maintenance.py`(by-date增量+對帳) | |

## 4. ⚠️ NOT in git（machine-local — 新機沒有，須自建）
- **DB**：augur PostgreSQL（舊機現 8 表 / ~32.5M 列）— **不在 git**。
- **venv**：`venv/`（需 pip install）。
- **`.env`**：DB_* + `FINMIND_TOKEN` + `FRED_API_KEY`（密鑰，**絕不進 git**）。
- **/tmp logs**、augur 記憶（`~/.claude/projects/-home-hugo-project-augur/memory/`，per-machine）。

## 5. 新機設置步驟
```bash
git clone https://github.com/tsaitsangchi/augur.git && cd augur
# PostgreSQL：建 augur db/user（依 .env 設定）
python3 -m venv venv && venv/bin/pip install -e . && venv/bin/pip install numpy pandas
cp .env.example .env   # 填 DB_*（host/port/dbname/user/password=augur）+ FINMIND_TOKEN + FRED_API_KEY
PYTHONPATH=src venv/bin/python -c "from augur.core import db; print('DB ping', db.ping())"   # 須 True
```

## 6. 資料(DB)接續 — 兩選項
- **A. 從零重抓（clean-room 正規）**：`PYTHONPATH=src venv/bin/python scripts/full_market_sync.py`（~40-50h、resume-capable、逐 dataset #7 對帳）。最乾淨，但重花時間。
- **B. 轉移舊機 DB（保留 ~32M 列成果）**：舊機先停 sync（TaskStop/kill）→ `pg_dump -U augur augur | gzip > augur.sql.gz` → 傳新機 → `gunzip -c augur.sql.gz | psql -U augur augur` → 再跑 `full_market_sync.py`（DB-driven resume 接續未完成的）。**推薦**（不浪費已抓的 5h）。

## 7. 舊機現況（this machine，不轉移除非走選項 B）
- 全市場 sync **執行中** ~5h：**7/85 dataset 處理**（[1-4] date-based 跳過 + [5-7] per-stock 載入），進行中 **[8/85] 法人 ~45%**；DB **~32.5M 列 / 8 表**。
- **#7 無幻像對帳 PASS**：roster + FRED + 3 per-stock 大表（BalanceSheet/借券/財報，VM=0∧EX=0）。
- 詳見 `reports/augur_fullsync_progress_20260610.md`（committed）。
- 2 monitors（5-min 心跳 + 問題警示）+ driver 皆 machine-local，換機即失效。

## 8. Roadmap（接續方向）
- ✅ F0 core · F1 ingestion(+by-date) · F2 features+universe · F4 audit(reconcile+heal)
- 🚧 **全市場全量 sync**（進行中；新機走選項 A/B）
- ⬜ **F3：models（樹 base + 樹家族 trainer）+ evaluation（multi-cycle walk-forward validator，panel/metric 單一 helper #12、purged-CV #8、雙軌獨立）** ← 下一大步（需全市場 raw + feature store 就緒）
- ⬜ follow-up：4 date-based 表（GovBank/BlockTrading/TradingDailyReport/Warrant）需 **by-date 路徑**補抓；roster「公司優先」優化（減 461 ETF 前綴空跑）

## 9. 注意事項
- **finmind throttle**：`finmind.py:MIN_INTERVAL` 目前 **1.0s**（檔案值）；舊機這次 sync 跑 2.0s（啟動時值）。長跑建議 2.0s（文件實證安全；0.7s 曾 re-ban）。
- **WSL2 機器睡眠**：長跑須確保主機不睡（caffeinate 對 Windows host 無效）。
- **drop 表慣例**：開發中常 drop 全表重測 → DB 狀態多變，以實查為準。
- **pilot-first**：大規模抓取前先 pilot 驗全鏈（pilot 曾抓出 by-date PK 塌陷等 3 真 bug）。

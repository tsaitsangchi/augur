# augur 跨機交接 — 2026-06-16

> 換另一台電腦繼續本專案的接手指南。**權威永遠是 repo 的 5 治權檔 + 實查**；此為導航 + 現況快照。
> ⚠️ **DB 與 .env 不隨 git（每機獨立）→ 新機永遠以實查為準，勿照抄本檔列數。**

## 0. 一句話現況
catalog 元資料登錄**全實作完成**——drop → 一次乾淨重建 → 逐欄完整自檢 → 修正所有發現（**95/95 表 · 754 欄 · 全欄完整 0 NULL · 全驗證**）。已 push `origin/main` HEAD **`233a3df`**、封存 tag **`catalog-clean-rebuild-20260616`**。**下一個主階段＝F3 models + evaluation**。

## 1. 換機第一步：取 code（git 只帶 code/docs/reports，不帶 DB/.env）
```bash
git clone https://github.com/tsaitsangchi/augur.git   # 或既有 repo git pull
git checkout main                                      # HEAD = 233a3df
git tag -l | grep catalog-clean-rebuild-20260616       # 確認封存點存在
```

## 2. ⚠️ 最關鍵：DB 不隨 git、每機各自獨立
**本機（將換出）PostgreSQL `augur` 現況（2026-06-16 實查）：**
- catalog/log 表：`dataset_catalog` **95**、`column_catalog` **754**、`data_audit_log` **53,412**、`pipeline_execution_log` 0
- 原始資料 **27 表 / 約 1.197 億列**（TaiwanStockPrice 11.0M、InstitutionalInvestorsBuySell 24.9M、GovernmentBankBuySell 13.7M、PriceAdj 11.0M、Shareholding 8.7M、BalanceSheet 8.4M、MarginPurchase 8.0M、ShortSale 7.7M、PER 7.6M、OptionDaily 7.0M、FinancialStatements 2.7M、News 2.5M、USStockPrice 2.2M…）
- **以上全在本機 PostgreSQL、NOT in git。新機 DB 是空的。**

**換機 DB 兩方案：**
- **方案 A（推薦——因 token 即將到期）**：`pg_dump` 本機 → 傳輸 → 新機 `pg_restore`。保留 1.2 億列 + 完整 catalog，免重抓。
  ```bash
  # 本機（換出）
  pg_dump -U augur -d augur -Fc -f augur_20260616.dump
  # 傳到新機（scp / 隨身碟），新機（先 createdb augur）
  pg_restore -U augur -d augur --no-owner augur_20260616.dump
  ```
- **方案 B（新機從零重抓）**：⚠️ **FinMind sponsor token 2026-06-24 到期（約 8 天）**——之後降 free、**sponsor-only 資料抓不到**（分點/tick/snapshot/KBar/可轉債/法人 by-date…，catalog 內 `tier='S'` 之表）。走 B 必須趕在 **6-24 前**完成全史 sync，否則 sponsor-only 永久缺。

## 3. 新機環境前置
- PostgreSQL（db=`augur`, user=`augur`）。
- venv：建 venv + 裝 deps（pyproject；psycopg2-binary/pandas/polars/numpy/requests/python-dotenv + sklearn/xgboost/lightgbm/catboost；torch 為 optional `[deep]`）。一律 `PYTHONPATH=src venv/bin/python`。
- **`.env`（machine-local、不進 git、新機須重建）**：`DB_*` + **`FINMIND_TOKEN`** + **`FRED_API_KEY`**。範本 `.env.example`。
- 首次 setup 先跑 import smoke test 才進後續；OS 層依賴（OpenMP for xgboost/lightgbm、PostgreSQL headers）先補。

## 4. 本階段（2026-06-16）做了什麼：catalog 全實作 + 逐欄修正
工作模式：**drop 全 catalog 表 → 一次乾淨 build → 逐欄完整 review → 修系統性 bug（非零碎補丁）**。
- **中文**：`table_name_zh` 95/95 + `column_name_zh` 全覆蓋；curated 中文移入 `docs/datasets_zh.md` 為單一 SSOT、退役 code fallback dict（用戶 directive「不要用補的」）。
- **型別**：dirty 欄（契約碼 `200710/200711`、週選碼 `201211W4`、sentinel `-1`）強制 VARCHAR（樣本剛好純數字也不推 NUMERIC、防型別爆炸）。
- **FULL_START refine 探源頭真起點**（關鍵 bug：原只對 unlanded probe 表跑、漏 landed 表——landed DB min 常是當初 FULL_START sync 截斷、源頭更早）→ 擴及 landed + 放寬到「FULL_START 月」：**US 1928 / UK 1968 / CrudeOil 1986 / GoldPrice 1979 / Europe 1980 / BusinessIndicator 1982**（全以幣別/契約 id 寬查驗真）。
- **稀疏月結算表短窗 fallback**（FinalSettle：單日 probe 漏結算日、寬窗 size-too-large 回 0 → 3 個月短窗 catches）、**權證多檔 probe 取真型別**（單檔撞過期 → 試多檔到有成交）、**snapshot 哨兵**（1955 有資料＝date-insensitive → earliest None）、**國際股 API erratic retry**。
- **catalog 程式現已 perfect**：新機跑 `build_catalog.py` 一次乾淨 build 即重現此完整正確資料。

## 5. 換機後重建 catalog（走方案 B、或想刷新時）
```bash
PYTHONPATH=src venv/bin/python scripts/build_catalog.py   # 全 95 dataset + FRED；放量、經三層限速；約 10–30 分
```
（方案 A `pg_restore` 後 catalog 已含、免重建。）

## 6. 下一步 roadmap
- **F3 models（樹 base + 樹家族）+ evaluation（multi-cycle walk-forward validators，metric/panel 單一 helper #12）← 下一個主階段**（PHASE 10-11）。`src/augur/models/`、`evaluation/` 目前空 `__init__`。
- 已建：F0 地基 / F1 ingestion / F2 features+universe / F4 audit 起步 / **catalog 橫切完成**。
- 若新機重抓：趕 FinMind token **6-24 到期前**完成全史 sync。

## 7. 關鍵檔案
- catalog 程式：`src/augur/catalog/__init__.py`（全實作）
- 中文 SSOT：`docs/datasets_zh.md`
- catalog 全欄清單：`reports/augur_catalog_tables_fields_20260616.md`（99 表 × 全欄）
- ingestion：`src/augur/ingestion/`（finmind.py 三層限速 MIN_INTERVAL 0.7s / fred.py / ingest.py / sync.py）
- **5 治權檔**（`docs/` 內、以實際版本為準）：系統核心思想 + 原則精華（20 條）+ 系統架構大憲章 + `CLAUDE.md`（AI 工具規則）+ `README.md`
- ⚠️ **memory 不隨 git**：本機 `~/.claude/projects/.../memory/` 有專案記憶（augur_project_overview / rigor-completeness-discipline / finmind-fetch-methods / fred-data-source…）——**換機不跟著走**；新機靠本 handoff + 5 治權檔 + 實查重建認知。

## 8. 注意事項（硬規則）
- **DB 狀態多變**（用戶常 drop 重測）→ 新機**永遠以實查為準**，勿照抄本檔列數。
- **clean-room #16**：augur code 只依 5 治權檔 + schema 目錄 + live API；**絕不參考 stock_backend**。
- **commit/push 須明示授權**；不 hand-patch 已 committed 資料（改 writer + 重建）；不 commit `.env`/token。
- **FinMind 限速**：一律經 `ingestion/finmind.py` 三層防護（`_pace` MIN_INTERVAL 0.7s → `_quota_gate` 閉環問錶 → 403 冷卻）；放量前先**最小單位（單股單日）**探 IP 健康。
- `data_audit_log`（53,412 列稽核史）目前保留未清。
- 繁體中文對話。

---
*封存點 `catalog-clean-rebuild-20260616` @ `233a3df`；本機 FinMind 額度餘 ~3773/6000、token ⏰2026-06-24 到期。*

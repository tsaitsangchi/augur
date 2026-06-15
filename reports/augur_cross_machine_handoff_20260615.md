# augur 跨機接續快照 — 2026-06-15（catalog builder 完整 + 全跑）

**用途**：換另一台電腦接續本專案。讀此 + 5 治權檔 + 下列報告即可接手。
**鐵則**：① **DB 不隨 git、每機各自獨立** → 狀態一律**實查**（`pg_stat_user_tables`），勿照抄本快照本機數字。② **記憶（`~/.claude/.../memory/`）machine-local、不進 git** → 知識靠此 handoff + committed 報告轉移。③ commit/push 須用戶授權（#14）；放量須授權 + 防睡眠（#22/#24/#25）。

---

## 0. 一句話現況
本 session 把 **metadata catalog builder 從零建到完整並全跑**——它探測 FinMind+FRED 每個 dataset 的「怎麼抓」元資料（endpoint/模式/data_id 來源/最早日/欄型別/排除/reconcile_scope/髒值…）落地 `dataset_catalog`/`column_catalog` 兩表，成為**後續所有抓取的權威依據**（更正確/快/省 token）。**git HEAD `b9a7476`（已 push）**；今日 tags：`treaty-v1.7.0`（catalog 入憲）→ `compliance-audit-20260615`（全碼合規稽核）→ **`catalog-builder-20260615`**（builder 完整）。

## 1. 換機後第一步（在新電腦）
```bash
cd <repo>                       # 真實工作目錄（隨機器：本機 /home/hugo/project/augur）
git pull                        # 取 b9a7476 + 全報告 + 本 handoff
python -m venv venv && source venv/bin/activate && pip install -e .   # 若新環境
cp .env.example .env            # 填 DB_* / FINMIND_TOKEN / FRED_API_KEY（.env 不進 git）
PYTHONPATH=src venv/bin/python -m pytest tests/ -q                    # smoke：應 39 passed
```
**先實查新機 DB 狀態**（勿假設）：
```bash
PYTHONPATH=src venv/bin/python -c "from augur.core import db
with db.connect() as c:
  with db.transaction(c) as cur:
    cur.execute(\"select count(*) from pg_stat_user_tables where n_live_tup>0\"); print('有資料表數',cur.fetchone()[0])
    cur.execute(\"select to_regclass('dataset_catalog')\"); print('catalog 表',cur.fetchone()[0])\"
```

## 2. 本 session 完成了什麼
1. **catalog 架構入憲 v1.7.0**（憲章第三部新增橫切層 catalog + 附錄 C 理論定位）+ 設計檔 `reports/augur_metadata_catalog_design_20260615.md`。
2. **`datasets_zh.md`**（83 表逐欄中英 + 🔌抓法 + 📅最早日，docs/，正式參考）。
3. **catalog builder（`src/augur/catalog/__init__.py`，一支模組）**：
   - **段1**：2 表 explicit DDL + `optimal_mode`（動態最優模式）+ 冪等 upsert + build orchestration。
   - **段2 `probe_dataset`**：landed 全讀 DB 真值（pg 統計估、避千萬列慢查）；un-landed **robust 6 階梯探測 cascade**（`/datalist`→文檔種子→canonical 2330→by-date→Info roster→大型老股，復用 sync #18 階層 helper）。
   - **完整 fetch-method SSOT 擴充**（7 新欄）：`endpoint`(含分點 dedicated URL)/`single_day_only`/`reconcile_scope`(防假MIS/假PASS)/`dedicated_url`/`quota_expiry`/`data_id_required`；欄級 `dirty_value_note`(防型別爆炸)/`type_caveat`。curated 報告知識 seed(provenance=doc)。
   - **`scripts/build_catalog.py`** 薄 CLI。
4. **治權審視/命名慣例（CLAUDE v1.4 #18）**：library 模組＝領域名詞、CLI＝動作動詞、package＝管線階段/橫切（禁通用角色名 build/registry/probe/util/…）；經 screaming architecture + DDD ubiquitous language + PEP 8 + 業界 4 維度理論驗證（附錄 C + `reports/augur_architecture_theory_20260615.md`）。
5. **全碼合規稽核**（4 agent，~2239 行/15 模組，零資料層違規；`features/builder.py→panel.py` 合規 #18）→ tag `compliance-audit-20260615`。
6. **#4 data-driven 偵測**：catalog `_is_intraday_data` 由資料事實判 intraday（補硬編 `ingest.INTRADAY` 漏網，如 GoldPrice 5-min）。

## 3. ⭐ 怎麼跑 catalog build（新機要重跑——catalog 是 DB 表、不隨 git）
```bash
PYTHONPATH=src venv/bin/python scripts/build_catalog.py            # 全 83+FRED（放量 #17、~15-25 分鐘）
PYTHONPATH=src venv/bin/python scripts/build_catalog.py --datasets TaiwanStockPrice,GoldPrice   # 子集測
```
- **放量**：un-landed dataset 需 API 探測（含 earliest backward-probe）；landed 多 DB 讀。經 finmind 三層防護（_pace 0.8s→_quota_gate 問錶→403 冷卻 1800s）。
- **長跑須防睡眠**（#22）+ 背景啟動 + 監看；**真 403=靜默冷卻＝進度停滯**（非印出來；勿被 "~4031 calls" 估計數的 403 誤導）。
- **跑完抽查**：各 dataset 的 `fetch_mode`/`excluded`/新欄是否合理；有無 `source_provenance='probe(empty)'` 漏網（真抓不到或需未知 id）。
- **本機現況**（實查，勿照抄）：catalog build **完成 84/84**、catalog 85 dataset/636 欄、DB 29 表有資料。
- **本輪後續修 3 個 build-完整性 bug**（已 commit、新機 pull 即含）：(a) build target 改 `finmind.list_datasets()` 全集 → **含 excluded(intraday/OUT_OF_UNIT)亦記抓法**（如分點 `dedicated_url=/taiwan_stock_trading_daily_report`）；(b) cascade 加 **4b 寬窗/無參步驟** → catch market/名冊類漏網（BusinessIndicator/國際 Info/ParValueChange/SplitPrice/FutOptTickInfo）；(c) **`_safe_date`** 正規化月頻日期（`2026/06`→月初）。→ 新機 rebuild 得 **~94 dataset、~0 漏網**（excluded 也記抓法）。

## 4. 關鍵知識（記憶 machine-local、這裡轉移）
- **鐵則：所有資料都抓得到、只是要用對方法**（用戶 directive）。真排除只有 **#4 intraday(8)** + **#3 OUT_OF_UNIT 規模暫緩(3)**；其餘 82 表皆該抓。分點走 dedicated URL、tick/KBar 走 `/storage_objects` parquet、snapshot 單日型、法人 by-date 靠 sponsor——**catalog 記下每個的正確抓法**。
- **完整抓取方法地圖** 見 `reports/augur_datasource_finmind_fred_20260615.md`（endpoint 全集/模式/data_id 階層/edge case）+ `augur_finmind_research_20260611` + `augur_dataset_fetch_classification_20260610` + `augur_fullsync_issue_analysis_20260610`（髒值/PK 塌陷/reconcile scope 實戰）。
- **⏰ FinMind sponsor token 2026-06-24 到期**（剩 ~9 天）：sponsor-only（分點/tick/snapshot/KBar/可轉債/法人 by-date/八大行庫）到期降 free 抓不到 → **全史 data sync 須趕到期前**。FRED 無到期。
- **anti-leakage 公告欄（#8 金礦）**：Dividend.AnnouncementDate/AnnouncementTime · MonthRevenue.create_time(待實證) · Shareholding.RecentlyDeclareDate；財報三表無→法定 lag。catalog `anti_leakage_flag` 已標。
- 本機記憶檔（可重建於新機）：`finmind-fetch-methods` / `finmind-data-source` / `fred-data-source` / `augur_project_overview`（含 catalog builder 進度）。

## 5. 治權現狀（5 檔版本各自獨立）
靈魂 **v1.2.0** · 原則精華 **v1.6.0（20 條）** · 憲章 **v1.7.0（+catalog 橫切 + 附錄 C 理論定位）** · CLAUDE **v1.4（#18 標頭與命名慣例）** · README。三敵人×三基石（#1/#8/#15）；#19 試錯逼近奇異點 + #20 自驅動×實證。

## 6. 下一步（接續方向）
1. **新機跑 catalog build**（§3）→ 產出該機的 catalog SSOT。
2. **item 3（未做、用戶問過「為何硬編 INTRADAY」）**：把 sync 的 #4 gate 改**資料驅動**（用 catalog `_is_intraday_data` 取代/補硬編 `ingest.INTRADAY`，動 ingest/sync code）——消除 #3/#18 違規。
3. **⏰ 全市場全史 data sync（趕 6/24）**：catalog 現可驅動最優抓取（每表讀 catalog row 即知 endpoint/模式/範圍）。`scripts/full_market_sync.py`（--new-only 補缺）+ `refetch_fixed_tables.py`（修截斷 Futures/Option/USStock）。放量須授權 + 防睡眠 + #25 緊盯前段。
4. **F3 models + evaluation**（PHASE 10-11，未建）；F3 計畫見 `reports/augur_f3_model_plan_three_thoughts_20260612`。
5. **catalog → datasets_zh.md 反向生成**（表＝SSOT、md＝視圖）；catalog 驅動 sync（optimization plan 階段 F）。

## 7. 本機遺留（不隨 git、新機無關）
- catalog build（task brrzok3li）**已完成 84/84**（本機 catalog 已落地 85 dataset/636 欄）；cron 已停。
- 新機從乾淨開始：git pull（含 3 build-完整性修正）→ 跑 `scripts/build_catalog.py`（rebuild、得 ~94 dataset）→ 接續。

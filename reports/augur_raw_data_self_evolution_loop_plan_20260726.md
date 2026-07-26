# augur 全庫 raw data 自進化迭代學習計畫（RAWEVO）[I]（2026-07-26）

> **SSOT 已移轉（V2-P-yes，2026-07-26 hugo 拍板、登錄 `audits/V2-ADOPTED-SUNSET-20260726.md`）**：本檔之總控／介面契約 SSOT＝`augur_self_evolution_master_plan_v2_20260726.md`；本檔降為前身史料，衝突時以 v2 為準；v2 §0.6 明列本檔哪些段落作廢／修訂／撤回。

> **性質**：[I] 計畫書（#20 plan-first；v1.39 表＋程式雙落實）——**拍板前零實作**；不創設 [N]、不改憲章。
> **定位**：雙自進化（TWEVO × LAIEVO）之**資料地基層**閉環——raw／catalog／對帳／覆蓋／缺口→假說燃料。
> **對偶檔**：預測＝`reports/augur_tw_prediction_self_evolution_loop_plan_20260726.md`（TWEVO）· advisor＝`reports/augur_local_ai_route_b_no_gpu_plan_20260726.md`（LAIEVO）· 介面＝`reports/augur_dual_self_evolution_interface_20260726.md`（DUAL-IFACE）。
> **本文所有數字**：皆出自 2026-07-26 本地 DB 唯讀實測（`pg_class.reltuples` 估計＋逐表 `min/max(date)` 實掃，零 FinMind／FRED 呼叫）；掃描耗時 297 秒。

---

## 0. 結論（先讀這段即可）

augur DB 現有 **248 張 public 表**，其中 **84 張 raw／市場源表**（83 張 FinMind 落地表＋`fred_series` 31 series）**已 100% 登錄 `dataset_catalog`**、多數新鮮度到 2026-07-23／24。已有 profile／coverage／對帳／field 交互工具**各自能跑**，**缺的是「一輪 raw 迭代」的編排帳本＋driver**：把「盤點→覆蓋對帳→缺口分類→交互假說候選→人閘分流→回寫帳本」編成 resume-safe、可 dry-run、可停損的閉環，並把產出以 DUAL-IFACE 允許流向餵給 TWEVO（map 假說提示）與 LAIEVO（gold 情境句）。

成功定義＝**每輪產出一份可驗的覆蓋快照＋分類過的缺口帳＋（若有）人閘前假說提示**；**≠** 補洞（FZ-keep 不解凍）、**≠** raw 升格靈魂、**≠** 直接 APPLY prodset、**≠** 改 LLM 權重。

---

## 1. What／Why／非目標／與雙計畫關係

### 1.1 What

| 面向 | 定義 |
|---|---|
| **標的** | 全庫 84 張 raw 表（＋catalog／attestation 既有登錄）的**自進化迭代**：每輪讓「我們對 raw 的理解」變好一格——覆蓋更清楚、缺口分類更準、交互假說更多候選 |
| **閉環** | 盤點 profile → 覆蓋／freshness 對帳（庫內）→ 缺口分類（真缺／凍結致缺／schema／語意）→ 交互假說候選（field 工具族）→ **人閘分流**（資料債 vs TWEVO map 提示 vs LAIEVO gold 情境）→ 回寫迭代帳本 → 下一輪 |
| **新交付（拍板後）** | (1) `raw_evolution_iteration_ledger`＋`raw_table_coverage_snapshot` 兩表；(2) 一輪 driver `scripts/run_raw_evolution_iteration.py`；(3) migrate DDL 腳本 |
| **人** | 拍板開階；R4 人閘分流（何者僅記資料債、何者升 TWEVO／LAIEVO 提示）；停損；治權變更。**AI 不自行解凍、不自行升格** |

### 1.2 Why（缺口，非重複發明）

| 既有零件 | 能做什麼 | **閉環缺口** |
|---|---|---|
| `scripts/profile_raw_data.py` | 逐表逐欄事實 profile（null 率／值域／YTD 偵測） | 一次性輸出、無迭代 ID、無快照落表 |
| `scripts/scan_coverage.py` | 逐表逐年覆蓋掃描、標缺口年 | 印 stdout 即散佚；無缺口**分類**（真缺 vs 凍結致缺）；無帳 |
| `scripts/reconcile_audit.py`／`daily_maintenance.py --audit` | DB↔API byte 對帳＋heal | **API 門——凍結中不可跑**；本計畫只**讀**其歷史 `attestation_result`／`full_attest_progress` |
| `scripts/build_catalog.py` | 建 `dataset_catalog`／`column_catalog` | 全量模式打 API（凍）；`--db-only` 欄級 refresh 可用 |
| `scripts/run_field_correlation.py`／`build_field_lens_map.py` | 欄位兩兩相關（65.7 萬列）／三鏡頭地圖 | 未接迭代閉環；結果無「第 N 輪新發現什麼」的差分帳 |
| `field_return_leadlag`（13.5 萬列） | 欄位 lead-lag | 同上 |
| TWEVO `evolution_iteration_ledger`（規劃中） | 預測閉環帳本 | **不是** raw 層帳本——混用＝錯歸因（DUAL-IFACE 禁共用 iteration id 命名空間，本計畫同理自立帳本） |

### 1.3 明確不做

| 不做 | 理由 |
|---|---|
| 為補洞開 FinMind／FRED（sync／probe／heal／Dividend 重建） | **FZ-keep**（`finmind-fred-api-freeze.mdc`；INV1＋INV2 未成立） |
| hand-patch 已 committed raw／手動 UPDATE 補值 | CLAUDE #12；correction＝supersede 留痕路徑，且受閘另案 |
| 把 raw 列／全市場列舉寫進靈魂文書或任何 [N] | `soul-vs-raw-correlation.mdc`——升格的只能是**概念與可證偽關係**，且走 PME 人閘 |
| 直接 APPLY prodset／寫 `feature_values`／降 GATE 閾值 | TWEVO 職權；本計畫只出**提示**，GATE-keep |
| 改 advisor LLM 權重／prompt-pack／gold 直灌 | LAIEVO 職權；本計畫只出**情境句候選**（人審） |
| 宣稱可交易／確立級／「資料洞已補」 | `evaluated_pass=0`；凍結中缺口只能記帳不能補 |
| 對 248 表同等力道深挖 | 力道依 §3.4 優先序；非 raw 的 164 張表僅分類登錄不進閉環 |

### 1.4 與雙計畫的一句相容

TWEVO 從 I0 假說 map 出發、LAIEVO 從 gold 教材出發，**兩者都假設「庫內 raw 是已知的、乾淨的」**；RAWEVO 就是把這個假設變成**每輪重新驗證的機械事實**——地基層在下、兩閉環在上，只以 DUAL-IFACE 允許流向相接（§7）。

---

## 2. 硬邊界（寫進計畫＝執行時不可逾）

1. **FZ-keep**：全程**庫內 DB 唯讀＋本地計算**；零 FinMind／FRED 網路呼叫；發現缺口→**寫帳**，不 sync、不 heal、不 probe。「可以迭代」**≠**「可以再開 API」。
2. **soul↔raw**：raw＝觀測／結果呈現；**不因庫裡有 raw 升格靈魂**。可升格的唯有 raw **交互**抽象出的概念與可證偽關係（相關係數／lead-lag 作為概念載體），且一律經 R4 人閘→（TWEVO 側）`curate_pme_map_expand` 或（LAIEVO 側）人審 gold；禁整庫 raw 貼進靈魂／原則精華／[N]。
3. **不 hand-patch**：發現 raw 錯誤→記缺口帳＋（解凍後另案）走 writer＋supersede 路徑（`raw_supersede_log`），不手動 UPDATE。
4. **#1 source-pure**：快照與缺口帳的每個數字出自 DB query（本計畫附錄數字即為先例）；不估算、不 placeholder。
5. **#8 anti-leakage**：交互假說候選一律沿用既有 field 工具族的 as-of 紀律；事件表未來日期（如 `TaiwanStockDividend` max=2026-08-23 之未來除息日、`TaiwanStockTradingDate` 至 2026-12-31 之日曆）屬**正常語意**，快照須標註「未來日=事件公告特性」而非缺陷，且提醒特徵消費端 as-of 過濾。
6. **輸出只做三件事**：覆蓋 ledger、缺口／近失分類、允許的 brief／map 假說**提示**——不 APPLY、不降閘、不改權重（DUAL-IFACE 正交）。
7. **候選隔離**：R3 交互結果只寫 `field_correlation`／`field_return_leadlag`／報告檔；**不**寫 `feature_values`／prodset。
8. **[I] 位階**：本計畫及其帳本皆 [I]；任何判準若要入憲（[N]）另開案。

---

## 3. 現況實測（2026-07-26 庫內唯讀）

### 3.1 全庫 248 表分類總表

| 分類 | 表數 | 代表 |
|---|---|---|
| **raw／市場源**（本計畫標的） | **84** | TaiwanStock*×47、TaiwanFutures/Option/FutOpt*×17、海外 Info/Price×8、總經匯率×11、`fred_series` |
| features／panel／universe／labels／prediction | 31 | `feature_values`（251 萬）、`daily_direction_feature_values`（1,928 萬）、`core_universe*`、`direction_*`、`prediction_*` |
| arena／evolution／governance | 20 | `evolution_run`／`promotion_queue`／`direction_arena_*`／`trial_ledger`／`revalidation_*` |
| knowledge／philosophy | 71 | `knowledge_*`（含 concordance 16 分區）、`philosophy_*` |
| advisor／app／deliberation | 30 | `advisor_distill_*`、`chat_*`、`deliberation_*`、`local_model_*` |
| catalog／audit／field 工具 | 12 | `dataset_catalog`（97）、`column_catalog`（769）、`attestation_result`、`raw_supersede_log`、`field_correlation`（65.7 萬）、`field_return_leadlag`（13.5 萬）、`field_lens_map` |

（分類含 5 表跨界計一次；raw 全表清單＝附錄 A。）

### 3.2 raw 層健康快照（重點發現）

* **登錄完整**：84 張 raw 實表 **100% 在 `dataset_catalog`**；catalog 另有 11 個 dataset 登錄但無實表（tick／minute 級 excluded：`TaiwanStockPriceTick`、`USStockPriceMinute` 等）＋2 筆對映差異待 S0 釐清。
* **新鮮度**：多數日頻表 max(date)=2026-07-23／24（live 增量健康）；attestation 最近一輪 2026-07-24（`daily_maintenance --heal`，豁免 18、部分覆蓋 26、未完整 4 表）。
* **陳舊／異常候選（S1 缺口分類的第一批素材）**：
  - `ExchangeRate` max=**2020-11-13**（停更 5 年半——真缺 or 來源停供，待分類）
  - `GovernmentBondsYield`／`USStockPrice` max=2026-06-18（落後一個月+）
  - `TaiwanFutOptTickInfo` 的 date 欄值＝`2026/06` 字串（**schema／語意類**缺口，非日期型）
  - `EuropeStockInfo`／`JapanStockInfo`／`UKStockInfo`＝2019 snapshot（catalog `attestation_mode=snapshot` 豁免型，屬**語意正常**，須在快照標註而非誤報）
  - `TaiwanStockDividend` 僅 2,411 列（**已知 G-DIV 缺股另帳**——凍結致缺，禁假稱已滿）
  - `TaiwanFuturesSpreadTick` 僅 2026-05 起、`TaiwanStockIndustryChain`／`InfoWithWarrant` 僅 2026-06-16 起（新落地表，短史屬正常）
* **未來日期（#8 語意提醒）**：`TaiwanStockDividend`（除息公告）、`TaiwanStockTradingDate`（日曆）含未來日——正常事件語意，消費端須 as-of 過濾。

### 3.3 既有可讀登錄（本計畫消費、不重建）

| 表 | 現量 | 本計畫怎麼用 |
|---|---|---|
| `dataset_catalog`（97 列） | 26 欄含 `earliest_date`／`frequency`／`reconcile_scope`／`attestation_mode`／`finalize_lag_days` | 分類與豁免路由的 SSOT；快照 join 它判「snapshot 型≠陳舊」 |
| `column_catalog`（769 列） | 逐欄中文名／`anti_leakage_flag`／`dirty_value_note` | R0 schema drift 對照；語意缺口候選來源 |
| `attestation_result`／`full_attest_progress` | 凍結前歷史 attest 結論 | R1 只**讀**——「上次 byte 級對帳到哪天」＝凍結期覆蓋基線 |
| `data_audit_log`（26 萬）／`raw_supersede_log`（3,914） | 抓取行為史／supersede 留痕 | 缺口成因佐證（何時停抓＝凍結致缺證據） |
| `field_correlation`／`field_return_leadlag`／`field_lens_map` | 65.7 萬／13.5 萬／342 | R3 交互假說候選的既有基線；每輪算**差分**（新增了什麼結構） |

### 3.4 深度優先序（不對 84 表同等力道）

排序鍵＝**預測消費熱度 → 覆蓋完整度 → 新鮮度**：

| 級 | 表群 | 理由 |
|---|---|---|
| **P1**（逐欄深挖＋R3 交互） | 價量／籌碼／估值／月營收 ~22 欄面板已消費之表（`TaiwanStockPrice`／`PER`／`MarginPurchaseShortSale`／`InstitutionalInvestorsBuySell`／`MonthRevenue`／`Shareholding` 等 ~15 表） | prodset 與 field_correlation 面板的現役地基 |
| **P2**（覆蓋＋freshness 逐輪） | 期貨／期權 17 表、財報 3 表、其餘台股日頻 | 量大、假說潛力高（三鏡頭「位」軸）、尚未進面板 |
| **P3**（僅快照登錄） | 海外 Price／Info、總經匯率、`fred_series`、snapshot 型 | 凍結中不可補；只記帳不深挖 |

---

## 4. (a) Table schema

### 4.1 所讀既有表（摘要；DDL 住所不變）

§3.3 全列——本計畫對它們**一律唯讀**；`dataset_catalog` 回填建議（如 `dirty_value_note`）屬 S5 可選項且人閘後才寫。

### 4.2 新表一：`raw_table_coverage_snapshot`（每輪每表一列；建議 DDL）

```sql
CREATE TABLE IF NOT EXISTS raw_table_coverage_snapshot (
    snapshot_id      BIGSERIAL PRIMARY KEY,
    iteration_id     VARCHAR(64)  NOT NULL,          -- 'rawevo_0001'
    dataset          VARCHAR(255) NOT NULL,          -- FK 語意對 dataset_catalog.dataset
    snapshot_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
    est_rows         BIGINT,                         -- pg_class.reltuples（估，標明）
    exact_rows       BIGINT,                         -- 可選精確 count（P1 表才算）
    min_date         DATE,
    max_date         DATE,
    date_semantics   VARCHAR(32)  NOT NULL DEFAULT 'observation',
                     -- observation|event_future_ok|calendar|snapshot|no_date
    staleness_days   INTEGER,                        -- 今日−max_date（snapshot 型記 NULL）
    freq_class       VARCHAR(16),                    -- 日|週|月|季|事件（承 scan_coverage 推斷）
    gap_years_json   JSONB,                          -- 偏離常態頻率之年（scan_coverage 邏輯落表）
    catalog_registered BOOLEAN NOT NULL,
    last_attest_ref  TEXT,                           -- attestation_result id / run_id（唯讀引用）
    detail           JSONB,
    UNIQUE (iteration_id, dataset)
);
CREATE INDEX IF NOT EXISTS idx_rtcs_dataset ON raw_table_coverage_snapshot (dataset, snapshot_at);
```

### 4.3 新表二：`raw_evolution_iteration_ledger`（一輪一列；建議 DDL）

```sql
CREATE TABLE IF NOT EXISTS raw_evolution_iteration_ledger (
    iteration_id     VARCHAR(64) PRIMARY KEY,        -- 'rawevo_0001'（獨立命名空間，禁與 TWEVO/LAIEVO 混用）
    opened_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at        TIMESTAMPTZ,
    status           VARCHAR(24) NOT NULL DEFAULT 'running',
                     -- running|closed_no_finding|closed_findings|halted
    steps_json       JSONB NOT NULL DEFAULT '{}',    -- R0..R5 各步狀態/exit/產物 path（resume 依據；fail-closed）
    n_tables_scanned INTEGER,
    gap_summary_json JSONB,                          -- {真缺:[..],凍結致缺:[..],schema:[..],語意:[..]}
    hypothesis_hints_out JSONB,                      -- 假說提示（人閘前候選；文字＋SSOT 出處，非數值權重）
    briefs_out       JSONB,                          -- 匯出給 TWEVO/LAIEVO 之 brief 檔 path＋雜湊
    cross_notify_json JSONB,                         -- 對偶閉環 kill/停損告警（只讀通知，不連鎖）
    human_gate       JSONB,                          -- R4 人閘結論：{approved_hints:[..], data_debt_only:[..], by, at}
    no_gain_streak   INTEGER NOT NULL DEFAULT 0,     -- 停損計數
    approved_by      VARCHAR(64),                    -- 開輪拍板碼（如 RAWEVO-S2-go）
    notes            TEXT
);
```

設計對齊：與 TWEVO `evolution_iteration_ledger`／LAIEVO `local_ai_iteration_ledger` **同構不同帳**（DUAL-IFACE「兩閉環、兩帳本」原則延伸為三帳本）；`steps_json` fail-closed 承 TWEVO §3。

---

## 5. (b) Python 程式規畫

### 5.1 既有 script 消費清單（本計畫直接用；零改動或最小改動）

| script | 角色 | 本閉環用法 |
|---|---|---|
| `scripts/profile_raw_data.py` | 逐表逐欄事實 profile | R0 呼叫（`--table` 對 P1 表）；stdout 落報告檔、path 記 ledger |
| `scripts/scan_coverage.py` | 逐年覆蓋掃描 | R1 邏輯來源——其推斷函式抽用或子行程呼叫，結果落 `raw_table_coverage_snapshot` |
| `scripts/run_field_correlation.py` | 欄位兩兩相關 → `field_correlation` | R3（P1 面板；`--report-only` 供差分讀取） |
| `scripts/build_field_lens_map.py` | 三鏡頭欄位地圖 | R3 假說提示的框架出處（唯讀 join） |
| `scripts/build_catalog.py --db-only` | 欄級 catalog refresh（零 API） | R0 前置（schema drift 對齊 column_catalog） |
| `scripts/reconcile_audit.py`／`daily_maintenance.py` | **API 門——凍結中不跑** | 僅讀其歷史 `attestation_result`；解凍後（另案）才可能重啟 |

### 5.2 新編排：`scripts/run_raw_evolution_iteration.py`（草案；拍板後才寫）

```
執行指令矩陣（首次提交即須含；#18/#29）：
  python scripts/run_raw_evolution_iteration.py                  # 無參數＝安全預設：印現況（最近一輪 ledger＋停損計數，唯讀）
  python scripts/run_raw_evolution_iteration.py --selftest       # 零 DB 紅綠自測（步驟機/分類器純函式）
  python scripts/run_raw_evolution_iteration.py --open           # 開新一輪（寫 ledger 列；需已拍板輪次）
  python scripts/run_raw_evolution_iteration.py --step R0..R3    # 跑指定步（冪等；steps_json resume）
  python scripts/run_raw_evolution_iteration.py --dry-run        # 全流程只算不寫（快照印 stdout）
  python scripts/run_raw_evolution_iteration.py --close          # R4 人閘結論落帳＋R5 結案（--human-gate file.json）
  python scripts/run_raw_evolution_iteration.py --tier P1|P2|P3  # 依 §3.4 限縮力道
```

步驟機（一輪＝一個 `iteration_id`）：

```
R0 盤點 profile：248 表分類 diff＋P1 表逐欄 profile（新表出現/欄型漂移→schema 類缺口）
R1 覆蓋＋freshness：逐 raw 表 min/max/freq/gap_years → raw_table_coverage_snapshot
     （join dataset_catalog 之 attestation_mode/frequency 免誤報 snapshot 型；join attestation_result 記對帳基線）
R2 缺口分類：staleness×data_audit_log×catalog → {真缺|凍結致缺|schema|語意}
     凍結致缺一律標 'FZ-blocked'（禁 heal；解凍後另案的 backlog 帳）
R3 交互假說候選：field_correlation 差分＋leadlag＋lens join
     → hypothesis_hints_out（文字＋出處＋n_obs；不寫 feature_values）
R4 人閘（Steward）：逐 hint 分流——資料債 only／升 TWEVO map 提示／升 LAIEVO gold 情境
R5 結案：ledger 收斂＋briefs_out 匯出＋no_gain_streak 更新 → 下一輪或停損
```

失敗語意：任一步 exit≠0 → `steps_json` 記 fail、輪保持 `running` 不半套前進；重跑同步冪等。

### 5.3 其他新檔（拍板後、最小集）

| 檔 | 職責 | 簽名要點 |
|---|---|---|
| `scripts/migrate_raw_evolution_ddl.py` | §4.2/4.3 兩表 idempotent DDL | `--dry-run`／`--selftest`；不動既有表 |
| （可選，S3）`export_raw_evolution_brief()` | ledger→brief JSON（給 TWEVO `consumed_briefs`／LAIEVO 情境註記） | 只含結論句＋path＋雜湊；禁 raw 列內容 |

不新增 package；邏輯薄層放 script 內或 `augur.audit` 既有模組旁（實作時依 #18 命名慣例定案）。

---

## 6. 分階段落地（S0–S5）＋機械驗收＋停損

| 階段 | 內容 | 機械驗收 | 回滾 |
|---|---|---|---|
| **S0 前置＋DDL** | migrate 兩表；driver 骨架＋`--selftest`／無參數唯讀；首次 `--dry-run` 全表快照 | `--selftest` 綠；`--dry-run` 印 84 表快照且**零寫入**；`check_cmd_matrix.py` 過 | DROP 兩空表即淨 |
| **S1 首輪 R0–R2** | 開 `rawevo_0001`；快照落表＋缺口分類（§3.2 候選為驗收樣本） | snapshot 84 列；`ExchangeRate` 被分類（真缺/停供）；snapshot 型**未**誤報陳舊；G-DIV 標 FZ-blocked | ledger 標 `halted`；快照表可整輪 DELETE |
| **S2 R3 交互假說** | field_correlation 差分＋hints 產出（P1 面板） | hints 每則含出處＋n_obs；`feature_values`／prodset **零寫入**（機械斷言） | hints 只在 ledger JSONB，清欄即回滾 |
| **S3 接口匯出** | brief 匯出＋DUAL-IFACE 掛接（TWEVO `consumed_briefs`／LAIEVO 情境） | brief 檔零 raw 列；對偶帳本能引用 path；`cross_notify_json` 通 | 刪 brief 檔＋ledger 欄 |
| **S4 節奏化** | 週輪 cron 草案＋錯峰＋停損啟用 | 連兩輪 resume-safe；錯峰規則寫入（§7.3） | 停 cron 即回手動 |
| **S5 回顧＋catalog 回填建議** | 回顧報告；`dirty_value_note` 等回填**建議清單**（人閘後才寫） | 建議每則引 snapshot 證據；未批**零寫** catalog | 建議僅報告檔 |

**節奏**：建議週輪（R0–R2 全自動 ~10 分鐘級；R3 依面板量 ~30 分鐘級，錯峰跑）。
**停損**：連續 **N=2** 輪（可 `RAWEVO-STOP-N=k` 改）「無新缺口發現∧無 hint 被 R4 採納」→ 降頻至月輪或 `halted`；任何步觸 API 呼叫（機械斷言 import 檢查）→ 立即 halt＋報告。

---

## 7. 與 TWEVO／LAIEVO／DUAL-IFACE 接口矩陣

### 7.1 正交（禁）

| 禁 | 理由 |
|---|---|
| RAWEVO 直接寫 `feature_values`／prodset／`promotion_queue`／呼叫 `apply_evolution_promotions` | TWEVO 職權＋GATE-keep；地基層不碰晉升閘 |
| RAWEVO 直接寫 gold／改 prompt-pack／LLM 權重 | LAIEVO 職權（人簽 serving） |
| 三帳本共用 iteration id 命名空間 | DUAL-IFACE「錯歸因」同理；`rawevo_*` 自立 |
| raw 快照／整庫列 → 靈魂文書或 advisor「權威」 | soul↔raw；禁確立級話術 |
| 缺口帳當「可以解凍」的論據 | 倒果為因禁止（INV2 仍須 Steward 明示） |

### 7.2 允許流向

| 方向 | 允許內容 | 入口 |
|---|---|---|
| **RAWEVO→TWEVO** | 缺口帳結論句（「X 表凍結致缺至 D 日」＝I1 建值窗依據）；R4 已批假說提示（欄位對＋方向＋出處）→ 人 → `curate_pme_map_expand` | TWEVO ledger `consumed_briefs` 同構欄；**無自動橋** |
| **RAWEVO→LAIEVO** | 覆蓋結論句／語意缺口（dirty_value 候選）作 gold **情境註記**（provenance 標 `rawevo_brief`；P4.E7 不洗成真人知識） | LAIEVO B4 選材（人審） |
| **TWEVO/LAIEVO→RAWEVO** | gap ledger 之「缺資料」訴求 → 下輪 R1 加掃該表 | ledger `notes`／開輪參數 |
| **雙向通知** | 停損／halt 寫 `cross_notify_json`；對偶只讀告警不連鎖 | 各方 ledger |
| **儀表** | `report_dual_evolution_week.py`（LAIEVO 規劃中）擴列第三帳本 | 並列展示 |

### 7.3 錯峰

R3（field_correlation 全量 run）與 TWEVO I3 local-gates／I6 train_ranker、LAIEVO embed／B2／B3 **互斥**；driver 偵測對偶 ledger `status=running` → `--defer-heavy`（只跑 R0–R2）。

---

## 8. 風險與誠實預期

* **凍結致缺不會變少**：本計畫**不能**讓 `ExchangeRate`／G-DIV 變滿——只能讓「缺什麼、為何缺、解凍後補單」變成機械帳。期望管理：迭代收益在**理解與假說燃料**，不在資料量。
* **假說提示≠特徵**：R3 產出的欄位交互結構全部要過 TWEVO 漏斗（HAC／多 seed／G-ECON）才可能進 prodset；歷史基線 65.7 萬列相關中絕大多數不會成為特徵——誠實預期每輪 hints 個位數。
* **大表掃描成本**：84 表 min/max 實測 297 秒（無 date 索引之大表 seq scan）；P1 精確 count 另計。週輪可承受；若膨脹→限縮 `--tier`。
* **同構三帳本的維護債**：以「同構不同帳」換正交清晰；若未來三帳本欄位漂移→S5 回顧提合併案（另拍板）。

---

## 9. 建議拍板碼

| 碼 | 語意 |
|---|---|
| `RAWEVO-P-yes` | 採納本計畫書為 raw 地基層自進化 SSOT；**不自動開工** |
| `RAWEVO-S0-go` … `RAWEVO-S5-go` | 逐階授權（S1 起每階含跑輪授權） |
| `RAWEVO-HINT-approve <ids>` | R4 人閘：批准指定 hints 升 TWEVO／LAIEVO 提示 |
| `RAWEVO-STOP-N=k` | 改停損輪數（未拍＝2） |
| `RAWEVO-P-no`／`RAWEVO-Sx-hold` | 否決／暫緩 |

**與雙計畫同批建議**：`RAWEVO-P-yes` 可與 `TWEVO-P-yes`＋`LAIEVO-P-yes`＋`DUAL-IFACE-yes`＋`FZ-keep`＋`GATE-keep` 同批；`RAWEVO-S2-go`（重掃）與 `TWEVO-S3/S4`、`LAIEVO-B2-train/B3` **分開**（錯峰）。

---

## 10. 30 分鐘閱讀地圖

§0 結論＋§2 硬邊界 → §3.2 健康快照（真發現）→ §5.2 步驟機＋§6 分階 → §7 接口矩陣 → 附錄 A 可掃即過。

---

## 附錄 A：raw 全表清單（84 表；列數＝reltuples 估計、日期＝2026-07-26 實掃）

| 表 | 估列數 | min_date | max_date | 備註 |
|---|---:|---|---|---|
| TaiwanStockPrice | 11,894,869 | 1994-09-13 | 2026-07-24 | P1 |
| TaiwanStockPriceAdj | 11,159,569 | 1992-01-04 | 2026-07-24 | P1 |
| TaiwanStockPriceLimit | 11,955,902 | 2000-01-03 | 2026-07-24 | P2 |
| TaiwanStockPER | 7,601,156 | 2005-09-02 | 2026-07-23 | P1 |
| TaiwanStockMonthRevenue | 476,575 | 2002-02-01 | 2026-07-01 | P1 |
| TaiwanStockMonthPrice | 606,446 | 1999-12-01 | 2026-06-01 | P2 |
| TaiwanStockWeekPrice | 2,368,933 | 1999-12-20 | 2026-07-13 | P2 |
| TaiwanStockMarginPurchaseShortSale | 8,082,244 | 2001-01-05 | 2026-07-23 | P1 |
| TaiwanStockInstitutionalInvestorsBuySell | 27,047,628 | 2012-05-02 | 2026-07-23 | P1 |
| TaiwanStockInstitutionalInvestorsBuySellWide | 5,921,102 | 2012-05-02 | 2026-07-23 | P1 |
| TaiwanStockShareholding | 8,799,321 | 2004-02-12 | 2026-07-23 | P1 |
| TaiwanStockHoldingSharesPer | 20,954,490 | 2010-01-29 | 2026-07-17 | P2 |
| TaiwanStockMarketValue | 8,567,110 | 2004-02-12 | 2026-07-23 | P1 |
| TaiwanStockMarketValueWeight | 107,461 | 2024-10-30 | 2026-07-23 | P2（短史） |
| TaiwanStockDayTrading | 4,387,134 | 2014-01-06 | 2026-07-24 | P2 |
| TaiwanStockDayTradingBorrowingFeeRate | 32,893 | 2015-10-14 | 2026-07-23 | P2 |
| TaiwanStockDayTradingSuspension | 36,338 | 2014-07-09 | 2026-07-24 | P2 |
| TaiwanStockGovernmentBankBuySell | 14,034,333 | 2021-07-01 | 2026-07-23 | P2 |
| TaiwanStockLoanCollateralBalance | 5,343,788 | 2006-10-02 | 2026-07-23 | P2 |
| TaiwanStockSecuritiesLending | 743,464 | 2003-11-11 | 2026-07-23 | P2 |
| TaiwanDailyShortSaleBalances | 7,734,491 | 2005-07-01 | 2026-07-23 | P2 |
| TaiwanStockTotalInstitutionalInvestors | 26,739 | 2004-04-07 | 2026-07-24 | P2 |
| TaiwanStockTotalMarginPurchaseShortSale | 18,780 | 2001-01-03 | 2026-07-23 | P2 |
| TaiwanTotalExchangeMarginMaintenance | 6,253 | 2001-01-05 | 2026-07-23 | P2 |
| TaiwanStockMarginShortSaleSuspension | 37,858 | 2015-04-01 | 2026-07-24 | P2 |
| TaiwanStockBalanceSheet | 5,791,736 | 2012-12-31 | 2026-06-30 | P2（季） |
| TaiwanStockFinancialStatements | 2,693,419 | 1991-12-31 | 2026-06-30 | P2（季） |
| TaiwanStockCashFlowsStatement | 2,373,105 | 2012-03-31 | 2026-06-30 | P2（季） |
| TaiwanStockDividend | 2,411 | 2005-09-03 | 2026-08-23 | **G-DIV 缺股另帳；未來日=事件語意** |
| TaiwanStockDividendResult | 30,839 | 2003-07-07 | 2026-07-24 | P2 |
| TaiwanStockCapitalReductionReferencePrice | 678 | 2011-01-25 | 2026-06-30 | P3（事件） |
| TaiwanStockParValueChange | 16 | 2019-09-09 | 2025-08-25 | P3（事件） |
| TaiwanStockSplitPrice | 32 | 2019-09-09 | 2026-07-07 | P3（事件） |
| TaiwanStockDelisting | 342 | 2001-01-20 | 2026-07-16 | P3（事件） |
| TaiwanStockSuspended | 2,220 | 2025-03-07 | 2026-07-23 | P3 |
| TaiwanStockDispositionSecuritiesPeriod | 7,116 | 2005-01-04 | 2026-07-23 | P3 |
| TaiwanStockBlockTrade | 63,401 | 2005-06-28 | 2026-07-23 | P2 |
| TaiwanStockNews | 2,503,167 | 2010-03-02 | 2026-07-24 | P3（coverage 型） |
| TaiwanStockInfo | 4,291 | 2020-06-03 | 2026-07-24 | P3（名錄） |
| TaiwanStockInfoWithWarrant | 319,369 | 2026-06-16 | 2026-07-24 | P3（新表） |
| TaiwanStockInfoWithWarrantSummary | 220,830 | 2011-01-03 | 2026-07-24 | P3 |
| TaiwanStockIndustryChain | 31,041 | 2026-06-16 | 2026-07-24 | P3（新表） |
| TaiwanStock10Year | 5,383,797 | 2011-01-24 | 2026-07-24 | P2 |
| TaiwanStockTotalReturnIndex | 10,830 | 2003-01-02 | 2026-07-09 | P2 |
| TaiwanStockTradingDate | 6,937 | 1999-01-05 | 2026-12-31 | 日曆（未來日正常） |
| TaiwanStockConvertibleBondDaily | 1,314,632 | 2007-01-02 | 2026-07-23 | P2 |
| TaiwanStockConvertibleBondDailyOverview | 1,108,950 | 2010-01-04 | 2026-07-23 | P2 |
| TaiwanStockConvertibleBondInfo | 238 | — | — | P3（無 date 名錄） |
| TaiwanStockConvertibleBondInstitutionalInvestors | 418,332 | 2009-04-01 | 2026-07-23 | P2 |
| TaiwanSecuritiesTraderInfo | 64 | 2025-02-10 | 2026-07-15 | P3（名錄） |
| TaiwanFuturesDaily | 5,827,314 | 1998-08-03 | 2026-07-24 | P2 |
| TaiwanFuturesInstitutionalInvestors | 111,591 | 2018-06-05 | 2026-07-23 | P2 |
| TaiwanFuturesInstitutionalInvestorsAfterHours | 42,570 | 2021-10-12 | 2026-07-24 | P2 |
| TaiwanFuturesDealerTradingVolumeDaily | 5,513,171 | 2021-04-01 | 2026-07-24 | P2 |
| TaiwanFuturesOpenInterestLargeTraders | 1,905,419 | 2007-01-02 | 2026-07-23 | P2 |
| TaiwanFuturesFinalSettlementPrice | 3,133 | 2016-01-08 | 2026-07-22 | P2 |
| TaiwanFuturesSpreadTick | 1,571,329 | 2026-05-01 | 2026-07-24 | P3（新落地） |
| TaiwanFuturesSpreadTrading | 15,494 | 2007-11-02 | 2026-07-24 | P2 |
| TaiwanOptionDaily | 33,971,880 | 2002-01-02 | 2026-07-24 | P2（最大表） |
| TaiwanOptionInstitutionalInvestors | 61,122 | 2018-06-05 | 2026-07-24 | P2 |
| TaiwanOptionInstitutionalInvestorsAfterHours | 6,930 | 2021-10-12 | 2026-07-24 | P2 |
| TaiwanOptionDealerTradingVolumeDaily | 1,351,861 | 2021-04-01 | 2026-07-24 | P2 |
| TaiwanOptionOpenInterestLargeTraders | 954,872 | 2007-01-02 | 2026-07-23 | P2 |
| TaiwanOptionFinalSettlementPrice | 1,788 | 2002-01-17 | 2026-07-22 | P2 |
| TaiwanFutOptDailyInfo | 1,323 | — | — | P3（無 date） |
| TaiwanFutOptInstitutionalInvestors | 135,060 | 2017-07-17 | 2026-07-23 | P2 |
| TaiwanFutOptTickInfo | 10,621 | 2026/06* | 2027/06* | **schema 缺口：date 欄為字串契約月** |
| TaiwanExchangeRate | 96,193 | 2006-01-02 | 2026-07-23 | P2 |
| TaiwanBusinessIndicator | 533 | 1982-01-01 | 2026-05-01 | P3（月） |
| ExchangeRate | 54,730 | 1990-01-02 | **2020-11-13** | **陳舊候選（S1 分類）** |
| InterestRate | 3,083 | 1990-01-01 | 2026-07-15 | P3 |
| GovernmentBondsYield | 99,303 | 1990-01-02 | 2026-06-18 | 落後候選 |
| GoldPrice | 12,403 | 1979-01-01 | 2026-07-24 | P3 |
| CrudeOilPrices | 18,489 | 1990-01-02 | 2026-07-20 | P3 |
| CnnFearGreedIndex | 3,943 | 2011-01-03 | 2026-07-24 | P3 |
| USStockPrice | 35,052,888 | 1928-02-01 | 2026-06-18 | P3；落後候選 |
| USStockInfo | 17,872 | 2019-01-01 | 2026-07-24 | P3（名錄） |
| JapanStockPrice | 16,855,360 | 1999-05-06 | 2026-07-23 | P3 |
| JapanStockInfo | 3,640 | 2019-01-14 | 2019-01-14 | snapshot 型（豁免） |
| EuropeStockPrice | 4,178,718 | 1980-04-01 | 2026-07-23 | P3 |
| EuropeStockInfo | 1,306 | 2019-01-14 | 2019-01-14 | snapshot 型（豁免） |
| UKStockPrice | 23,625,076 | 1968-01-01 | 2026-07-23 | P3 |
| UKStockInfo | 24,339 | 2019-01-31 | 2019-01-31 | snapshot 型（豁免） |
| fred_series | 344,063（31 series） | 1919-01-01 | 2026-07-15 | P3；FRED 凍 |

（catalog 另 11 個無實表 dataset＝tick／minute 級 excluded／BACKFILL_DEFERRED：`TaiwanFuturesTick`、`TaiwanOptionTick`、`TaiwanStockBlockTradingDailyReport`、`TaiwanStockEvery5SecondsIndex`、`TaiwanStockKBar`、`TaiwanStockPriceTick`、`TaiwanStockStatisticsOfOrderBookAndTrade`、`TaiwanStockTradingDailyReport`、`TaiwanStockWarrantTradingDailyReport`、`TaiwanVariousIndicators5Seconds`、`USStockPriceMinute`——S0 一併登錄為「未落地、凍結中不補」。）

---

**本檔完。標 [I]。實作零授權直至 `RAWEVO-S0-go`。全程零 FinMind／FRED；raw 不升格靈魂；輸出只做覆蓋帳、缺口帳、人閘前假說提示。**

# 核心股特徵值取得 SOP — augur 完整可重現作法（2026-06-29）

> **性質**：標準作業程序（SOP）。定義「**如何從原始資料取得核心股的特徵值**」之完整、可重現、可驗證流程。全程實證自 code（`features/` · `universe/` · `evaluation/` · `scripts/`），非憑記憶。
> **靈魂對齊**：只用真實資料、誠實預測台股；三敵零容忍（#1 零幻像 / #8 anti-leakage / #15 誠實）。

---

## 〇、一句話

核心股特徵值 = **三階段管線**：`raw（DB）→【階段1】全 roster 特徵面板 build → feature_values → 【階段2】核心股完整度選拔 → core_universe(_asof) → 【階段3】取核心股 × canonical 特徵矩陣`。全程 **as-of point-in-time（#8）**、**算不出即缺列（#1）**、**動態相對不硬編（#9）**。

```
 raw tables ──build_feature_panel──▶ feature_values ──build_core_universe──▶ core_universe_asof
 (15 核心表)   (panel.build_panel)    (全roster×35feat)   (core_gate 四道閘)    (as-of 374核心股)
                                            │                                        │
                                            └──────────── _panel_matrix(核心股, canonical_features) ───────┘
                                                          → (stock_ids, X 特徵矩陣)  【階段3 取值】
```

---

## 一、前置條件（環境 + 資料）

| 項 | 要求 |
|---|---|
| **DB** | augur PostgreSQL，15 核心 raw table 對核心股完整到 **as-of=2026-05-31**（覆蓋 374/374、時間連續、sentinel 極低；已驗 `reports/...` 完整性）|
| **環境** | `venv` + numpy/pandas/psycopg2/scikit-learn/lightgbm；OpenMP（xgboost/lightgbm）|
| **as-of 參數** | 治權參數＝**2026-05-31**（完整性判準截止日；固定使「完整」可定案、可驗證）|
| **執行** | 一律 `PYTHONPATH=src venv/bin/python3`；冪等可重跑（#6）|

---

## 二、【階段 1】全 roster 特徵面板 build

**CLI**：`PYTHONPATH=src python scripts/build_feature_panel.py [--since YYYY-MM-DD] [--panels d1,d2] [--asof]`
- 預設＝重建 feature_values 既有全部 panel；`--asof` 只建 core_universe_asof 之股（省算）。
- orchestrator 對每 panel date × roster 呼叫 **`panel.build_panel(conn, panel_date, stock_ids)`**，逐股算特徵 → 寫 `feature_values(panel_date, stock_id, feature, value)`。

**核心口徑（鐵則）**：
1. **as-of ≤t（#8）**：所有 raw 查詢 `date <= panel_date`、純後向（取 df 末列）；**禁未來列**。
2. **還原價**：價量一律 `TaiwanStockPriceAdj`（`_PRICE_SQL`）+ `close > 0`（剔停牌哨兵）。
3. **發布日 gate（#8 命門）**：財報/月營收 date=期間末非公開日 → 須過法定申報期（月營收次月 15、財報季+45/年報+90）才可 as-of 用（`release_lag.py`；月營收 `_REVENUE_SQL` LIMIT 16 剔未公告月後仍≥13 供 YoY）。
4. **recency gate**：價量過期（`MAX_STALE_CALENDAR_DAYS=45`）之停牌/下市股不出特徵。
5. **算不出即缺列（#1）**：任一特徵無資料/log→inf/源表未覆蓋 → **不寫該列**（嚴格 source-pure、不補 0、不 placeholder）。

**7 計算模組鏈（panel.build_panel 內、35 特徵）**：

| 模組 | 鏡頭/類 | 特徵（數）|
|---|---|---|
| `panel.compute_features`（價量）| 第一性·量軸 | return_1d、momentum_{5,20,60,120,252}d、volatility_60d、range_mean_20d、turnover_mean_20d、dollar_volume_log_20d、volume_surge_5_60、cycle_position_252d、price_to_252d_high（13）|
| `panel._compute_revenue_yoy` | 基本面成長 | monthly_revenue_yoy（1、發布日 gate）|
| `chip.compute_chip_features` | F2b 籌碼 | institutional_net_buy_ratio_20d、margin_usage_ratio、foreign_holding_pct、top_holders_pct、sbl_short_balance_log、lending_fee_rate_mean_30d、gov_bank_net_buy_60d（7）|
| `valuation.compute_valuation_features` | F2c 估值 | pe_ratio、pb_ratio、dividend_yield、market_cap_log、price_to_10yr（5）|
| `concentration.compute_concentration_features` | 八二·形軸 P3 | volume_gini_20d、volume_gini_60d、volume_max_share_20d、volume_max_share_60d（4）|
| `phase.compute_phase_features` | 康波·位軸 | range_position_120d、days_since_high_252d、inst_cumflow_position_60d、inst_cumflow_position_120d（4）|
| `margin_cycle.compute_margin_cycle_features` | 康波 C3 | gross_margin_pctile（1、發布日 gate）|

**輸出**：`feature_values` 全 roster（~2752 股 × 28 panel、各股各 feat 算不出則缺列）。

---

## 三、【階段 2】核心股完整度選拔

**CLI（生產口徑）**：
```
PYTHONPATH=src python scripts/build_core_universe.py --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial --asof
```
呼叫 `core_gate.build_universe`（pan-historical 單名單）+ `build_universe_asof`（逐 as-of 面板 point-in-time）。判準＝`_select_core`：

**四道閘（候選空間 ∩ 完整度 ∩ 流動性 ∩ conditional）**：
1. **候選空間**：真台股個股代碼（`_REAL_STOCK_PREDICATE` 排產業名/指數名污染）∧ **非 ETF**（排 `TaiwanStockInfo.industry_category` ETF 類）。
2. **完整度**：`universal` 特徵（35 feat 減 conditional）在**每個可用 (panel, feature) 格全齊**（`HAVING count = available_combos`；某 feat 全市場 0 覆蓋之 panel 不計入 required，審查 G9）。
3. **流動性**（`--liquidity-pct 25`）：以最近 panel `dollar_volume_log_20d` 之 P25 為下界（**動態相對、#9 不硬編**）。
4. **conditional**（`--exempt-revenue-financial`）：月營收完整度對**金融保險/金控業豁免**（其無傳統月營收）。

**pan-hist vs as-of（#8 關鍵）**：
- `core_universe`（pan-hist）：用全 panel 算單一名單（含 look-ahead，僅供概覽）。
- **`core_universe_asof`（逐 as-of 面板 t 用 ≤t panels 算）**：**消 survivorship bias**、生產/評估一律用此。

**輸出**：`core_universe_asof`（as-of=2026-05-31 口徑：848 distinct 股 × 28 panel、latest panel 374 股）。

---

## 四、【階段 3】取核心股特徵值（程式介面）

評估/模型層三函式（`evaluation/baseline.py`）：

```python
panels  = SELECT DISTINCT as_of_date FROM core_universe_asof           # 28 panel
feats   = baseline.canonical_features(conn, panels)                    # 每 panel 都出現之 feat 交集（35）
stocks  = baseline._asof_stocks(conn, panel_date)                      # 該 panel point-in-time 核心股（#8）
sids, X = baseline._panel_matrix(conn, panel_date, stocks, feats)      # (核心股id, 特徵矩陣 k×f)
```

**取值口徑**：
- `canonical_features`：**每 panel 都出現**之特徵交集（部分 panel 缺之特徵排除、確保維度一致、審查 G9；由資料判定反硬編）。
- `_panel_matrix`：只收「**全 feats 齊**」之股（缺任一不入；核心股應齊）→ 純 I/O primitive。
- `_asof_stocks`：讀 `core_universe_asof` 該 as_of_date 名單（point-in-time）。

**輸出**：`(stock_ids, X)`，X 為核心股 × canonical 特徵之數值矩陣，供模型 `run_ladder` / 投組 `run_backtest`（後續 StandardScaler + Ridge/GBDT、purged walk-forward）。

---

## 五、橫切守則（每階段皆守）

| 守則 | 落地 |
|---|---|
| **#8 anti-leakage** | raw ≤t、純後向、財報/月營收發布日 gate、core_universe_asof 消 survivorship、label t+1 |
| **#1 零幻像/source-pure** | 算不出即缺列、不補 0/placeholder、不從相似 model 推估 |
| **#9 無硬編** | 流動性 P25 動態相對、completeness available_combos 由資料判定 |
| **#15 誠實** | 含隨機性 metric 多 seed；特徵入生產須過四道漏斗 + 經濟價值 #14（IC≠可交易）|
| **#6 冪等** | 三階段 CLI 皆可重跑、ON CONFLICT upsert、DB-driven resume |

---

## 六、完整可重現 CLI 序列

```bash
cd <augur 工作目錄>
export PYTHONPATH=src
# 階段 1：全 roster 特徵面板（raw 已在 DB）
venv/bin/python3 scripts/build_feature_panel.py --since 2014-01-01
# 階段 2：核心股選拔（pan-hist + as-of）
venv/bin/python3 scripts/build_core_universe.py --since 2014-01-01 --liquidity-pct 25 --exempt-revenue-financial --asof
# 階段 3：取值即評估（取核心股 canonical 特徵 → 基準階梯 rank IC）
venv/bin/python3 scripts/run_evaluation.py --asof --h 20,60,120 --seeds 3
# （經濟價值 #14 終測）
venv/bin/python3 scripts/run_economic_eval.py --h 60 --cost 0.00585
```

冪等：DB 已對齊（dump 匯入）時階段 1/2 可略，直接階段 3 取值。

---

## 七、35 生產特徵清單（鏡頭分類）

**三鏡頭 × 紀律漏斗**（同 raw 欄三旋轉、三軸正交 形×位 corr 0.022）：
- **第一性·量軸**（價量資訊內容）：momentum_{5,20,60,120,252}d、return_1d、volatility_60d、range_mean_20d、turnover_mean_20d、dollar_volume_log_20d、volume_surge_5_60、cycle_position_252d、price_to_252d_high
- **八二·形軸**（分布形狀）：volume_gini_{20,60}d、volume_max_share_{20,60}d
- **康波·位軸**（時間結構/相位）：range_position_120d、days_since_high_252d、inst_cumflow_position_{60,120}d、gross_margin_pctile（C3）
- **基本面/籌碼/估值**：monthly_revenue_yoy、institutional_net_buy_ratio_20d、margin_usage_ratio、foreign_holding_pct、top_holders_pct、sbl_short_balance_log、lending_fee_rate_mean_30d、gov_bank_net_buy_60d、pe_ratio、pb_ratio、dividend_yield、market_cap_log、price_to_10yr

**特徵增刪須過四道漏斗**（紀律閘 #1/#8/#9 → 五鏡 #11 → purged walk-forward → 提拔關卡 as-of+HAC+多seed增量）**+ 經濟價值 #14 收尾**（詳法 SSOT＝`reports/augur_feature_discovery_methodology_20260626.md`）。**交互/raw 候選 opt-in 走 `cross_section.py`**（如 inter_fh_x_p10yr，但須過經濟價值 + 換宇宙穩健才設預設）。

---

## 八、誠實邊界

- 本 SOP 描述**現行生產流程**；特徵集為 2026-06-29 之 35 feat 快照（演變進 git，非本檔）。
- 「完整性」以 as-of=2026-05-31 為界；as-of 後（2026-06）未定案不計入。
- 兩已知 raw bug（Dividend PK 塌列、BalanceSheet 缺季）**不在生產特徵資料路徑**（dividend_yield 用 PER 表、無 feature 用 BalanceSheet），不污染。

---

## 九、完整重建驗證（2026-06-29、依本 SOP 三階段一步一步實證）

依本 SOP 從 raw 完整重走三階段（非依 dump），實證結果：

| 階段 | 結果 | 判定 |
|---|---|---|
| **1 特徵面板** | feature_values 2,420,089 列重算（35feat×35panel×3080股、ERROR 0）== 重建前 | ✅ 冪等可重現 |
| **2 核心股** | core_universe **344**（P25 方法）≠ 原 dump 374 | ⚠️ 見局限 |
| **3 取值+重現** | H60 as-of Ridge IC **+0.142**（≈+0.143）、H120 +0.148、net Ridge top10% Sharpe **1.18 > 基準 0.95**（CAGR+18.2%>15.2%）| ✅ alpha+經濟價值完全重現 |

**核心股參數局限（誠實 #15）**：原 dump 374 之確切 build 參數**不可考**（dump 是成品、未隨附參數）；本 SOP `--liquidity-pct 25` 得 **344**（無任一 liquidity/feat 組合精確 = 374：35feat 15→376 / 20→364 / 25→344）。**但 344 宇宙 alpha 與經濟價值完全重現**（H60 IC +0.142≈+0.143、Sharpe 1.18≈1.20）→ 證 **SOP 方法論正確可重現、30 股邊際差異不影響 alpha 本質（宇宙穩健）**。DB 現保留 **344**（SOP 方法之可重現產物；之前 inter_fh/dealer_self 等候選驗證為 374 口徑、與 344 不可直接逐值比，但結論〔局部/淘汰〕不變）。

**教訓**：「一步一步實作」才挖出文檔宣稱外的真實局限（核心股參數不可考）——**實證 > 文檔宣稱（#15）**；但關鍵的 **alpha 重現**證明 SOP 三階段方法可信、可交付。

**A1 補強（2026-06-29 已實作、解此局限）**：新增 `core_universe_build_meta` 表（`core_gate.build_universe(_asof)` build 時自動寫入 `scope / panel 範圍 / liquidity_pct / liquidity_threshold / conditional / feat_count / feat_list / core_count`、append 歷史、最新列＝當前快照）→ **此後 build 之核心股參數完全可考、可精確重現**（原 dump 374 為 A1 前之產物、其參數仍不可考，但新流程不再有此盲點）。階段 2 CLI 執行後可 `SELECT * FROM core_universe_build_meta ORDER BY build_id DESC LIMIT 1` 查當前核心股之確切 build 參數。

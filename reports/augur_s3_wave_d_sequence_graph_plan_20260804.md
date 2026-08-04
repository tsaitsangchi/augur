---
status: phase1-2c-executed
series: s3_wave_plan
wave: S3-WAVE-D
depends_on:
  - reports/augur_s3_features_for_market_model_families_20260804.md
  - reports/augur_deep_understanding_r6_20260804.md
  - reports/augur_project_optimization_plan_r6_20260804.md
executed_audit: audits/S3-WAVE-D-EXECUTED-20260804.md
---

# S3-WAVE-D 計畫書（plan-first）：序列窗張量（組 12）＋圖邊（組 13）· 2026-08-04

> **執行狀態（2026-08-04 追記）**：Phase 1＋2a＋2b＋2c **全數 GO＋EXECUTED**（`audits/S3-WAVE-D-GO-20260804.md`／
> `audits/S3-WAVE-D-EXECUTED-20260804.md`）——設計與下方 §2／§3 完全一致，未偏離。`stock_graph_edge`
> 已寫入 **13,021** 列（產業共群 1,831＋報酬相關性 5,089/6,101）＠`as_of=2026-06-30`（Phase 2c 經
> `AskQuestion` 明示授權後執行）。本檔以下內文保留原 plan-first 原文不改（對照實作之用），差異僅
> EXECUTED 帳所載之「產業共群邊 1,831（原估 1,750，同量級）」。

> **位階**：[I] 計畫（非 META [N]）；本檔本身**不含任何 build／apply／寫庫**——純規劃，拍板後才動工。
> **觸發**：`reports/augur_s3_features_for_market_model_families_20260804.md` §3 master list 第 12–13 行原文標註「**S3-D｜12–13｜序列窗＋圖邊（plan-first）**」——本檔即補齊該債。
> **為何現在**：`audits/S4-WAVE-C-EXECUTED-20260804.md`／`S4-WAVE-E-EXECUTED-20260804.md` 均將「缺序列 panel／圖邊契約」列為 S4 Wave C／D／E 三波誠實 SKIP 之**根因**——本檔為單一最高槓桿下一手（見 `augur_project_optimization_plan_r6_20260804.md` §5）。
> **self-reported（#32a）**：本檔數字為本次親查 DB 所得（(b) DB，見 §1），非記憶推估。

---

## 0. 一句定錨

組 12／13＝**現有庫內資料的兩種不同加工方式**——序列窗＝既有 raw 之**重排列**（零新資訊，故不建新表）；圖邊＝股票間**新推導關係**（有新資訊，故建一張小表）。兩者皆零新 API、零新原始資料，只動 as-of 安全的讀取／推導層。

---

## 1. 現況錨（本次親查，(b) DB；修正前輪報告之粗估假設）

| 錨 | 值 | 修正說明 |
|---|---|---|
| `feature_values` schema | `(panel_date date, stock_id varchar, feature varchar, value numeric)`——EAV 長表 | — |
| `feature_values.panel_date` 頻率 | **月頻**（近年月底 1 筆；早年甚至年頻）——**113 個 distinct panel_date，2007-12-31→2026-06-30** | ⚠ **推翻前輪優化計畫書 §2.1 之假設**——原假設「序列窗可直接展開 `feature_values`」不成立：月頻面板無法充當日頻 LSTM/Transformer 輸入 |
| `TaiwanStockPriceAdj` 日期覆蓋 | **8,817** distinct 交易日，1992-01-04→2026-08-03（日頻） | 序列窗真正原料在此（日頻 raw），非 `feature_values` |
| 核心宇宙（最新 as-of） | **225** 股 | `core_universe_asof` |
| `TaiwanStock*` 原始表 | **48** 張（含 `PriceAdj`／`InstitutionalInvestorsBuySell`／`MarginPurchaseShortSale`／`SecuritiesLending`／`Info.industry_category` 等） | 日頻籌碼/價量原料齊備 |
| 既有「每日對齊面板」builder | **已存在**：`src/augur/audit/field_correlation.py:build_stock_panel(conn, stock_id)`——單股、~22 欄、合併 ~12 張 raw 表、日期對齊 | S4-WAVE-C audit 原話「可由 PriceAdj／chip 重建序列」之**確切落點**——本計畫**複用**、不重造 |
| 現有圖／邊表 | **僅** `knowledge_edge` 等 KH 概念關係表；**無**股票／產業／相關性邊表 | `S4-WAVE-E-EXECUTED` 已澄清二者語義層不同、不可混用 |
| `TaiwanStockInfo.industry_category` | 既有產業分類欄 | 圖邊來源之一（產業共群） |

**未覆蓋**：尚未親查 225 核心股在 `industry_category` 之分布集中度（估計用，非真數）；動工前 Phase 2 應先跑一次分布查詢。

---

## 2. 組 12：序列窗張量——設計決策＝**不建新表**

### 2.1 判讀

`feature_values` 已是**衍生特徵**的月頻快照；序列窗所需的是**日頻原始價量／籌碼**之多通道對齊窗，兩者不是同一層資料。若新建一張「序列窗」表去**materialize**這些窗，將重複儲存已在 raw 表中的資訊、且每次 as-of 前進就要重建——違反 SSOT（CLAUDE #12）。**決定**：序列窗＝**讀取時 reshape**，不新增實體表。

### 2.2 Python 程式規畫

| 檔案 | 類型 | 職責 | 簽名 |
|---|---|---|---|
| `src/augur/features/sequence.py`（新） | library 模組 | 給定股票清單＋as_of＋窗長＋通道，回傳對齊張量 | `build_sequence_tensor(conn, stock_ids: list[str], as_of: date, window_len: int, channels: list[str] \| None = None) -> tuple[np.ndarray, list[str], list[str]]`——回傳 `(tensor[n_ok_stocks, window_len, n_channels], ok_stock_ids, channel_names)`；內部逐股呼叫既有 `audit.field_correlation.build_stock_panel(conn, stock_id)`，篩 `date<=as_of`，取最後 `window_len` 列；**歷史不足 window_len 之股票排除**（回傳於第二個值之外的 `excluded_stock_ids`，不 zero-fill、不前補，守 #1） |
| `scripts/build_sequence_panel.py`（新） | CLI script（唯讀為預設） | 覆蓋率報告／可選匯出快取陣列 | `--asof DATE --window N [--channels c1,c2,...] [--stocks-from-core] [--export PATH.npz\|--coverage-report(default)]`；預設**不寫庫**，只印覆蓋率（多少核心股足窗長、排除清單）；`--export` 才寫檔案快取（非 DB 表，類同 `models/artifact.py` 之 artifact 慣例，供訓練腳本讀取，可重建、非 SSOT） |

### 2.3 as-of／anti-leakage

`build_stock_panel` 本身即回傳日期索引 DataFrame，`build_sequence_tensor` 篩 `date<=as_of` 為天然邊界；缺值**不補**（NaN 保留，訓練端自行決定丟棄或遮罩），符合 #1／#8。

### 2.4 驗收（本波若拍板）

1. `--coverage-report` 對 225 核心股、window∈{20,60,120}（交易日）印出：足窗股數／排除股數／各通道缺值率。
2. 純函式單元測試：合成小面板（3 股×30 日×3 通道）餵 `build_sequence_tensor`，斷言 shape、排除邏輯、NaN 政策——**先驗紅**（CLAUDE #35）：故意餵不足窗長之股票確認被排除、故意留 NaN 確認不被悄悄補值。
3. 零寫庫、零新 API、零訓練。

---

## 3. 組 13：圖邊——設計決策＝**新建一張小表**

### 3.1 判讀

圖邊（產業共群／報酬相關性）是**新推導關係**（非既有欄位重排列），且圖模型訓練需要**凍結的 as-of 快照**（訓練當下的圖結構不可用未來相關性重算，否則違反 #8）——materialize 一張小表可稽核、可重複使用、成本遠低於每次重算。此設計與既有 `market_direction_feature`（as-of 揭露欄慣例）、`feature_candidate_values`（候選材料化慣例）同構。

### 3.2 Table schema 草案：`stock_graph_edge`

| 欄 | 型別 | 說明 |
|---|---|---|
| `as_of_date` | date | 圖快照日（PK 之一） |
| `source_stock_id` | varchar | 邊起點（慣例：`source_stock_id < target_stock_id` 避免雙存無向邊） |
| `target_stock_id` | varchar | 邊終點 |
| `edge_type` | varchar | `industry_same`｜`return_corr_60d`｜`return_corr_120d` |
| `weight` | numeric | 產業邊固定 `1.0`；相關性邊＝Pearson 相關係數值 |
| `n_obs` | integer | 相關性邊之共同觀測數（門檻揭露，同 `field_correlation.MIN_OBS` 慣例，預設 60） |
| `source_table` | varchar | 溯源（`TaiwanStockInfo` 或 `TaiwanStockPriceAdj`） |
| `git_sha` | varchar | 產生時 commit（同 `market_direction_feature` 慣例） |
| `created_at` | timestamptz | |

**主鍵**：`(as_of_date, source_stock_id, target_stock_id, edge_type)`。**索引**：`(as_of_date, source_stock_id)`、`(as_of_date, target_stock_id)`（雙向查詢鄰居）。

**規模估算**（親查 225 核心股後才能定案，本檔僅估）：產業邊≈數百至一千（受 `industry_category` 集中度影響）；相關性邊須設門檻（如 `|corr|≥0.3`）以避免 225²≈25K 全連通表爆量——**具體門檻值待 Phase 2 分布查詢後定案，不在本檔先射一個數字**。

### 3.3 Python 程式規畫

| 檔案 | 類型 | 職責 | 簽名 |
|---|---|---|---|
| `scripts/build_stock_graph_edges.py`（新） | CLI script | 給定 as_of，(a) 產業共群邊＝同 `industry_category` 兩兩配對；(b) 報酬相關邊＝複用 `build_stock_panel` 之日頻報酬欄，Pearson 相關＋`MIN_OBS`／`|corr|` 雙門檻，upsert `stock_graph_edge` | `--asof DATE [--corr-threshold F=0.3] [--min-obs N=60] [--dry-run(default)] [--commit]`；預設 dry-run 只印統計，**不寫庫**——首次真寫入須另一次明示（`--commit`），呼應本波 GO 句之邊界討論（見 §6） |
| DDL 遷移 | `scripts/migrate_stock_graph_edge_ddl.py`（新，沿用既有 83 支 `migrate_*_ddl.py` 慣例） | 建表（冪等 `CREATE TABLE IF NOT EXISTS`） | 無參數，直跑 |

### 3.4 驗收（本波若拍板）

1. Phase 2 先跑**唯讀分布查詢**：225 核心股 `industry_category` 分布（各產業幾股）、估算產業邊量級——**先查後定門檻**，不倒果為因。
2. `--dry-run` 印邊數量／稀疏度／anti-leakage 斷言（僅用 `date<=as_of` 之報酬序列算相關）。
3. 下游絆線回歸鎖（CLAUDE #35）：故意餵入「使用 as_of 之後的報酬」驗證相關性計算會被篩掉（非「拆掉篩選再測」，而是驗篩選存在時真的擋住）。
4. 首次 `--commit` 前先呈過目（#19），非批次直接寫庫。

---

## 4. 分階段（Phase 1/2 各自獨立驗收，互不阻斷）

| Phase | 內容 | 寫庫？ | 前置 |
|---|---|---|---|
| **Phase 1** | 組 12：`features/sequence.py`＋`build_sequence_panel.py`（唯讀，覆蓋率報告＋單元測試） | 否（`--export` 才寫檔案快取，非 DB） | 無（`build_stock_panel` 已存在） |
| **Phase 2a** | 組 13：`industry_category` 分布唯讀查詢 | 否 | 無 |
| **Phase 2b** | 組 13：`stock_graph_edge` DDL＋`build_stock_graph_edges.py --dry-run` | 否 | Phase 2a（門檻定案） |
| **Phase 2c** | 組 13：首次 `--commit` 寫入 as_of 快照 | **是**（首次寫庫） | Phase 2b 驗收過目 |
| **Phase 3** | 交還 S4：重評 Wave C/D/E 之 SKIP 判定（**契約解除≠adapter 已寫**——仍可能 SKIP，但理由從「缺契約」變「缺 adapter」，屬另一債） | 否 | Phase 1＋2 |

---

## 5. 邊界（本波不做）

- 不寫任何 sequence DL／GNN 模型訓練碼（adapter 實作＝另句，見 S4-REOPT-BACKLOG）。
- 不擴大核心宇宙、不放量取數（skip-sync）。
- 不將圖邊或序列窗自動接入現有 `train_ranker.py`／`predict_asof.py` 生產熱路徑。
- 不含 sim `--apply`。
- Phase 2c（首次寫庫）前必經人過目——本波 GO **不**預先授權 `--commit`（除非 Steward 於 GO 句明示涵蓋）。

---

## 6. 開工授權（草擬句，供 Steward 選擇範圍）

```text
S3-WAVE-D-go | FZ/GATE-keep | skip-sync | no-SIM-apply
```

**範圍待您明示**（本檔不代拍板）：

- 若僅授權 **Phase 1＋2a＋2b**（唯讀規劃到 dry-run，不含首次寫庫）→ 上句已足。
- 若一併授權 **Phase 2c**（`stock_graph_edge` 首次 `--commit` 寫入）→ 請於 GO 句加註如 `+ allow-graph-edge-commit`，本檔會於 EXECUTED 帳中逐一勾稽該加註。

---

## 7. 與既有 SSOT 之關係

- 本檔完成後，`reports/augur_s3_features_for_market_model_families_20260804.md` §3 第 12 行「missing／partial」與第 13 行「missing」狀態，於 Phase 1/2 EXECUTED 後應更新為對應新狀態（該檔另行更新，本檔不越權代改母檔）。
- 與 `reports/augur_deep_understanding_r6_20260804.md` §7 表 #6（序列窗／圖邊契約缺口）為同一債之對應計畫。

---

*plan-first 完稿（2026-08-04）——等候 Steward GO；零 build、零 apply、零寫庫。*

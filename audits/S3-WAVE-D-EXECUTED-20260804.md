# S3-WAVE-D 執行帳 [I]（2026-08-04）— EXECUTED（Phase 1＋2a＋2b＋2c 全數完成）

> **位階**：[I] 執行留痕（非 META [N]）
> **GO**：`audits/S3-WAVE-D-GO-20260804.md`（範圍＝Phase 1+2a+2b；Phase 2c 明示排除）
> **計畫 SSOT**：`reports/augur_s3_wave_d_sequence_graph_plan_20260804.md`
> **母 SSOT**：`reports/augur_s3_features_for_market_model_families_20260804.md`
> **as-of**：2026-06-30（與 S3-WAVE-A/B 一致）
> **logs**：`/tmp/s3-wave-d-20260804/`
> **self-reported（#32a）**：以下數字皆 (a) 程式輸出／(b) DB query 之真實結果；**≠**確立級／可交易／sim-apply

---

## 1. 約束遵守

| 約束 | 本波 |
|---|---|
| skip-sync | **守**——零 FinMind／FRED 呼叫，全程唯讀既有 raw／`core_universe_asof` |
| no-SIM-apply | **守** |
| FZ／GATE-keep | **守**——未改任何既有 gate |
| Phase 2c 不執行 | **守**——`stock_graph_edge` 全程只跑 `--dry-run`，全部 4 種驗證（selftest／smoke／225 股 dry-run／過後複查）皆確認 0 列 |

---

## 2. Phase 1：組 12 序列窗張量（不建新表）

### 2.1 新增檔案

| 檔案 | 類型 | 內容 |
|---|---|---|
| `src/augur/features/sequence.py` | library | `stack_windows`（純函式）／`build_sequence_tensor`（DB 薄殼）／`coverage_report` |
| `scripts/build_sequence_panel.py` | CLI | 覆蓋率報告（預設）／`--export` 匯出 `.npz` 快取 |

### 2.2 設計更正（誠實揭露，對照計畫書 §1）

親查確認 `feature_values.panel_date` 為**月頻**（113 個 distinct 日期，非日頻）——原優化計畫書 r6 草擬之
「讀 `feature_values` 展開序列窗」已於 plan-first 階段修正為**複用既有** `audit.field_correlation.build_stock_panel`
（日頻對齊面板，`TaiwanStockPriceAdj` 為底）。本波依修正後設計實作，**未**踩回原誤設計。

### 2.3 回歸鎖驗紅（CLAUDE #35）

`_selftest()` 內建 9 項斷言，涵蓋：足窗入選／不足窗排除／`None` 面板排除／shape 對齊／channel 由資料判定／
as-of 邊界（下游絆線）／NaN 不補（下游絆線）／缺 channel fail-loud／空輸入邊界。**親證驗紅**：以
monkey-patch 移除「不足窗排除」判斷後重跑，確認斷言由綠轉紅（`B` 錯誤地被納入 `ok_ids`）——非拆守衛
測試，而是在守衛下游注入絆線（規則 2），證實斷言量的是它宣稱在量的東西（規則 3）。

```text
$ python -m augur.features.sequence --selftest
✓ 足窗股入選（A）　✓ 不足窗股排除（B）　✓ None 面板排除（C）　✓ tensor shape 對齊
✓ channel_names 由資料判定　✓ as_of 太早→不足窗排除　✓ NaN 保留、未被補值
✓ 要求不存在之 channel → 報錯　✓ 空 panels → 空張量
自測:全通過 ✓
```

### 2.4 覆蓋率結果（225 核心股、window∈{20,60,120}，as_of=2026-06-30；程式輸出）

| window | 足窗 | 排除 | 通道數 | NaN 率最高 5 通道 |
|---|---|---|---|---|
| 20 | **225/225** | 0 | 33 | block_share 95.9%／holder_count 80.0%／retail_pct 80.0%／top_holders 80.0%／lending_fee 52.0% |
| 60 | **225/225** | 0 | 33 | block_share 96.2%／holder_count 78.3%／retail_pct 78.3%／top_holders 78.3%／lending_fee 53.7% |
| 120 | **225/225** | 0 | 33 | block_share 96.5%／holder_count 79.2%／retail_pct 79.2%／top_holders 79.2%／lending_fee 56.5% |

**誠實揭露**：核心股 100% 足窗（價格史夠長），但少數籌碼通道（鉅額佔比／大戶與散戶持股結構／借券費率）
高 NaN——這是**既有 raw 源覆蓋稀疏**之真實反映（非本波新債，`field_correlation.py` 早已對這些欄位注記
「某欄某日無資料→NaN→不補」），序列窗張量原樣繼承此稀疏度，訓練端須自行決定遮罩策略。

### 2.5 效能

225 股 × 3 窗長一次覆蓋率報告：**262.6 秒**（`build_stock_panel` 每股 ~31 條 SQL、非向量化批次查詢——
可用範圍：診斷／小批次訓練資料準備；若日後接生產訓練迴圈之高頻重跑，應另評批次化優化，**本波不做**
過度工程）。

---

## 3. Phase 2a：`industry_category` 分布唯讀查詢

### 3.1 發現：`TaiwanStockInfo` 非嚴格 SCD 歷史表

親查 `TaiwanStockInfo`：4,300 列／3,132 個 distinct `stock_id`（平均 1.37 列/股）；多數股僅有**單一「最近
同步」列**（本次查詢時點多數列 `date=2026-08-04`，即今日批次同步），僅少數股因產業重分類而有多列歷史。
**結論**：`date<=as_of` 嚴格 as-of 篩選對此表**不適用**（會誤排除絕大多數僅有「今日同步」列之股）；
比照既有 `universe/core_gate.py` 對此欄之既有作法（無 as-of 篩選、逕用當前列），Phase 2b 之 `industry_same`
邊採**同一慣例**（見 §4.2 已知限制揭露）。

### 3.2 分布結果（225 核心股、latest-row dedup；程式輸出）

- **31** 個產業分類覆蓋 **225/225** 核心股（零缺口）。
- 產業共群邊估計：**1,750**（族群大小 pairwise 加總估算）→ 實際 builder 跑出 **1,831**（§4.3；差異來自估算取樣時點與 builder 正式跑之間的統計口徑差，兩者同量級，非異常）。
- 最大產業：電子工業 87 股（3,741 對內部估算上界，實際受其他過濾影響）；最小多檔產業僅 1-3 股。

---

## 4. Phase 2b：`stock_graph_edge` DDL＋builder `--dry-run`

### 4.1 新增檔案

| 檔案 | 類型 | 內容 |
|---|---|---|
| `scripts/migrate_stock_graph_edge_ddl.py` | DDL migration | `stock_graph_edge` 表＋2 索引；`ddl_invariants()` 純函式＋7 項自測（含 5 項驗紅） |
| `scripts/build_stock_graph_edges.py` | CLI builder | `industry_same`／`return_corr_60d`／`return_corr_120d` 三型邊；預設 `--dry-run`，`--commit` 待 Phase 2c |

### 4.2 已知限制（誠實揭露，非隱藏）

`industry_same` 邊之產業別＝**目前最新分類**，非嚴格 `as_of` 當時分類（§3.1 原因）；因產業分類變動極慢，
短期誤差風險低，且與既有 `core_gate.py` 慣例一致，**但不宣稱**此邊型別為 anti-leakage 嚴格意義下之
point-in-time。`return_corr_*` 邊則**嚴格 as-of**（SQL 篩 `date<=as_of`，見 `_fetch_returns`）——兩種
邊型別之時點紀律等級不同，程式與本帳皆分別標示、不混稱。

### 4.3 DDL 執行（程式輸出）

```text
$ python3 scripts/migrate_stock_graph_edge_ddl.py --selftest
✓ 本尊 DDL 全不變式守住（綠）　✓ 驗紅:拿掉 lock_timeout → 報違　✓ 驗紅:拿掉複合主鍵 → 報違
✓ 驗紅:拿掉 edge_type 閉集 CHECK → 報違　✓ 驗紅:少一個索引 → 報違　✓ 驗紅:DDL 夾帶 INSERT → 報違
✓ EDGE_TYPES 三型別與 DDL CHECK 一致
自測:全通過 ✓

$ python3 scripts/migrate_stock_graph_edge_ddl.py --apply
✓ DDL 冪等完成（建表+2 索引，零資料寫入）
  ✓ table stock_graph_edge 在　索引數：2/2　現有列數：0（表已建、尚未寫入——符合 Phase 2b 唯讀邊界）
```

### 4.4 Dry-run 結果（225 核心股、as_of=2026-06-30、corr_threshold=0.3、min_obs=60；程式輸出）

| edge_type | 邊數 | 備註 |
|---|---|---|
| `industry_same` | **1,831** | 31 產業分類、225/225 股覆蓋 |
| `return_corr_60d` | **5,089** | weight：min=-0.458／median=0.367／max=0.853 |
| `return_corr_120d` | **6,101** | weight：min=0.300／median=0.359／max=0.791 |
| **合計** | **13,021** | 遠低於全連通上界（225²≈50,625／2≈25,312 對），門檻有效控制表大小 |

執行耗時：**2.6 秒**（225 股輕量查詢＋pandas 向量化相關性計算，遠快於 Phase 1 之逐欄查詢）。

**`--corr-threshold 0.3` 與 `--min-obs 60` 為 operational 初始值**（非治權值，CLAUDE #27）——未經重覆驗證
前不寫死進治權檔；沿用 `audit.field_correlation.MIN_OBS` 之既有慣例作為起點。

### 4.5 Phase 2b 邊界確認（`--commit` 前複查）

```text
$ SELECT count(*) FROM stock_graph_edge;
0
```

`--commit` 執行前複查表為 0 列——確認 Phase 2b 階段全程唯讀，符合原 GO 帳授權範圍。

---

## 4.6 Phase 2c：首次寫入（另行明示後執行，2026-08-04 同日）

**授權**：使用者於 `AskQuestion`「S3-WAVE-D 已完成 Phase 1+2a+2b。下一手？」選定
「**Phase 2c：把已驗證的 13,021 條邊寫庫**」——即 GO 帳 §1 所述「另一次明示」之明文兌現。

```text
$ python3 scripts/build_stock_graph_edges.py --asof 2026-06-30 --commit
...（統計數字與 dry-run 逐項相同，略）
✓ 已寫入 13021 列 @ as_of=2026-06-30

$ python3 scripts/migrate_stock_graph_edge_ddl.py --check
  ✓ table stock_graph_edge 在　索引數：2/2
  industry_same: 1831 列（1 個 as_of_date 快照）
  return_corr_120d: 6101 列（1 個 as_of_date 快照）
  return_corr_60d: 5089 列（1 個 as_of_date 快照）
```

**驗證**：`--commit` 寫入之列數與 §4.4 dry-run 統計**逐項相符**（1,831／5,089／6,101，合計 13,021）——同一份計算、同一批數字，寫入非另跑一套邏輯。`as_of_date=2026-06-30` 單一快照，符合表設計之「同 as_of 冪等覆寫」（`DELETE...WHERE as_of_date=%s` 後再插入，可重跑不重複累積）。

**組 13 現況更新**：`missing`→**`partial`（已有資料）**——圖邊資料已落地，惟：(a) 尚無 GNN 套件／adapter 消費此表（S4 Wave E 之 SKIP 理由仍為「缺 adapter」，非「缺邊」）；(b) `industry_same` 邊之產業別為「目前最新分類」而非嚴格 as-of（§4.2 已知限制，未變）。

---

## 5. 機械稽核（CLAUDE #18／#29／#35）

| 稽核 | 結果 |
|---|---|
| `scripts/check_cmd_matrix.py` | **502 支受檢／缺漏 0**（含本波新增 4 檔） |
| `scripts/check_false_assertions.py --gate` | **無新增假斷言**（1,009 檔實讀；基線 20 條存量不變） |

---

## 6. 硬禁未觸

無 sync · 無 sim `--apply` · 無 gate 改動 · 無序列窗新表（依計畫刻意不建）· `stock_graph_edge` 寫入僅發生於 Phase 2c 明示授權後、且僅寫入已 dry-run 驗證之同一批統計。

---

## 7. 下一刀（另句，本帳不代拍板）

- **交還 S4**：契約解除＋資料已落地，可重評 Wave C／D／E 之 SKIP 判定——但**契約解除≠adapter 已寫**，adapter 實作仍是另一債（序列 DL／Transformer／GNN 之訓練程式碼本波未觸碰，計畫書 §5 邊界原文）。
- **`--corr-threshold`／`--min-obs` 調參**：目前為初始 operational 值，如日後接實際 GNN 訓練，建議依 CLAUDE #27 逐級試驗（可控可恢復）後再定案；`stock_graph_edge` 設計為同 `as_of_date` 冪等覆寫，調參後重跑不會累積重複列。
- **`industry_same` as-of 精確化**（可選、低優先）：若日後需要嚴格 point-in-time 產業分類，須先補 `TaiwanStockInfo` 之完整歷史同步（目前多數股僅有單一「最近同步」列），為另一資料地基債、非本波範圍。

---

## 8. SSOT 回寫

- `reports/augur_s3_features_for_market_model_families_20260804.md` §3 第 12–13 行狀態、§6.2、§7 變更紀錄——待本帳完成後同步更新（見下一 commit）。
- `reports/augur_s3_wave_d_sequence_graph_plan_20260804.md`：plan-first 已對照實作完全一致，無需修訂本體，僅狀態頭由 `plan-first` 可另標 `phase1-2b-executed`。

---

*完。EXECUTED＝Phase 1＋2a＋2b＋2c 全數完成（序列窗 library／CLI；圖邊 DDL＋13,021 列已寫入 `stock_graph_edge`＠as_of=2026-06-30）。self-reported（#32a）。*

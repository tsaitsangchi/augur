# WM36-GAP 選項 A 執行留痕——新概念卡 `tw.daily_bar_adjusted`（2026-08-04）

> **位階**：[I] 執行留痕。
> **父案**：`audits/WM36-GAP-RAW-VS-ADJUSTED-CONCEPT-20260804.md`（缺口發現＋三選項呈報）。
> **授權**：`AskQuestion wm36_gap_decision=new_concept_card`，decided_by=hugo（2026-08-04）。

## 執行結果

| 項 | 值 |
|---|---|
| concept_key（新） | `tw.daily_bar_adjusted` |
| binding_id（新） | **100** |
| source_table | `TaiwanStockPriceAdj` |
| channel_role | `derived`（延續 binding 81 之標記慣例——調整值本質為計算衍生物） |
| mapping_status | `mapped` |
| category | `event` |
| ts_semantics | `交易日` |
| knowability_rule | `收盤後當日可得，但逢除權息等 CorporateAction 事件回溯重算全歷史（非最終定案值）` |
| finality_predicate | `不適用「次一交易日定案」——調整值隨未來除權息事件回溯重算，無恆定終值`（與 `tw.daily_bar` 之 finality 明確區隔，此即 81 當初未獲選為 `tw.daily_bar` 權威之理由） |
| decided_by | `hugo` |
| decided_at | 2026-08-04（COMMIT 時點） |
| 未動 | `tw.daily_bar`（binding 75 仍權威、81 仍掛該概念下 not_chosen）——**零改動**，本次純新增 |

## 執行序（ROLLBACK 演練 → COMMIT，同 U0-75 模式）

腳本：`scratchpad/wm36_new_concept_tw_daily_bar_adjusted.py`（一次性；`scratchpad/` 不入版控，本檔存留執行內容）。

1. 查重：`concept_key='tw.daily_bar_adjusted'` 不存在於 `world_concept` → 可進行
2. 三表 INSERT（`world_concept` → `world_channel_binding` RETURNING binding_id → `world_concept_version`）
3. 演練：查 `world_concept_registry_current` 現行列＝`('tw.daily_bar_adjusted','event',99)`（演練值）→ **ROLLBACK**
4. 驗回滾：`SELECT count(*) FROM world_concept WHERE concept_key='tw.daily_bar_adjusted'` → **0**
5. 正式：同流程 → binding_id **100**（IDENTITY 序號演練後前進，正常現象）→ **COMMIT**

## 驗收（真實輸出）

```text
$ python -m augur.catalog.world_concept --resolve tw.daily_bar_adjusted
Binding(concept_key='tw.daily_bar_adjusted', binding_id=100, table='TaiwanStockPriceAdj', column=None, role='derived')
```

## 消費端接線：`scripts/build_stock_graph_edges.py`

`_fetch_returns`／`return_corr_edges` 改經 `world_concept.resolve('tw.daily_bar_adjusted')` 取權威表（`quote_ident` 組 SQL），不再字面 `"TaiwanStockPriceAdj"`。

**行為不變性驗證**（同 as_of=2026-06-30 重跑 `--dry-run`）：

| 指標 | 接線前（今早直接執行 `--commit` 時） | 接線後（本次 `--dry-run`） |
|---|---|---|
| 核心股數 | 225 | 225 |
| industry_same 邊 | 1831 | 1831 |
| return_corr_60d 邊 | 5089 | 5089 |
| return_corr_120d 邊 | 6101 | 6101 |
| **合計** | **13021** | **13021** |

逐項比對零差異——確認本次為純「解析路徑」重構（registry 取代字面），非資料/邏輯變更（#35 回歸鎖精神：純函式輸出不變）。

## WM.36 止血閘復查

```text
$ python scripts/check_vendor_binding.py --gate
✗ vendor 直綁出血：新增 1 條/增處 0 條（不在基線）：
  ＋ scripts/build_stock_graph_edges.py	TaiwanStockInfo	quoted_table
```

**由「2 條新增直綁」降為「1 條」**——`TaiwanStockPriceAdj` 一項已消除。剩餘 `TaiwanStockInfo`（`industry_same` 邊之產業分類來源）**非本次授權範圍**：現行 registry 掛該表之唯一概念為 `tw.roster_membership`（binding 28，語意＝上市名冊成員），借用於「產業分類查詢」語意不符，屬另一獨立缺口，需另案呈裁（新概念卡如 `tw.stock_industry_category`，或其他設計）——**本輪不擅自決定**，見 `build_stock_graph_edges.py` 標頭新增段落之誠實揭露。

## 不做

- 未動 `tw.daily_bar`／binding 75／binding 81 之既有登錄
- 未處理 `TaiwanStockInfo`／`tw.roster_membership` 之語意錯配缺口（另案）
- 未更新 `ops/vendor_binding_baseline.txt`（該基線本應收斂而非放寬；待 `TaiwanStockInfo` 缺口一併解決後再一次性移除本檔兩條殘留，或視 Steward 是否要求分批移除）
- 未 commit／push（本次僅 DB 寫入＋程式碼修改，git 動作待用戶另行指示）

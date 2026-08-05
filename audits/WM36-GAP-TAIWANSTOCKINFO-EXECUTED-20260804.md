# WM36-GAP 殘留缺口執行留痕——新概念卡 `tw.stock_industry_category`（2026-08-04）

> **位階**：[I] 執行留痕。
> **父案**：`audits/WM36-GAP-OPTION-A-EXECUTED-20260804.md`（該案執行選項 A 時誠實揭露之新殘留缺口——`TaiwanStockInfo` 借用 `tw.roster_membership` 語意不符,本案不擅自決定,留待另案）。
> **授權**：`AskQuestion taiwan_stock_info=new_concept_card`，decided_by=hugo（2026-08-04）。

## 執行結果

| 項 | 值 |
|---|---|
| concept_key（新） | `tw.stock_industry_category` |
| binding_id（新） | **102** |
| source_table | `TaiwanStockInfo` |
| channel_role | `observation`（原廠供應之產業分類,非 augur 衍生計算——與 `tw.daily_bar_adjusted` 之 `derived` 有別） |
| mapping_status | `mapped` |
| category | `state`（產業分類為股票之持續性屬性,非逐日事件——比照 `tw.roster_membership` 之 category） |
| ts_semantics | `最近同步(非逐日)` |
| knowability_rule | `僅保留每股最新一列產業分類(TaiwanStockInfo 對多數股僅有單一「最近同步」列,非完整 SCD 歷史)——當前可得之最近同步值,非嚴格逐日 as-of 版本化` |
| finality_predicate | `不適用「次一交易日定案」——僅單一最近同步列,產業分類變動極慢但無版本化歷史,不具嚴格 as-of 意義下之終值` |
| decided_by | `hugo` |
| decided_at | 2026-08-04（COMMIT 時點） |
| 未動 | `tw.roster_membership`（binding 28 仍掛該表,語意＝上市名冊成員）——**零改動**，本次純新增獨立概念鍵 |

## 執行序（ROLLBACK 演練 → COMMIT，同 WM36-daily_bar_adjusted／U0-75 模式）

腳本：`scratchpad/wm36_new_concept_tw_stock_industry_category.py`（一次性；`scratchpad/` 不入版控，本檔存留執行內容）。

1. 查重：`concept_key='tw.stock_industry_category'` 不存在於 `world_concept` → 可進行
2. 三表 INSERT（`world_concept` → `world_channel_binding` RETURNING binding_id → `world_concept_version`）
3. 演練：查 `world_concept_registry_current` 現行列＝`('tw.stock_industry_category','state',101)`（演練值）→ **ROLLBACK**
4. 驗回滾：`SELECT count(*) FROM world_concept WHERE concept_key=...` → **0**；`world_channel_binding WHERE binding_id=101` → **0**
5. 正式：同流程 → binding_id **102**（IDENTITY 序號演練後前進，正常現象）→ **COMMIT**

## 驗收（真實輸出）

```text
$ python -m augur.catalog.world_concept --resolve tw.stock_industry_category
Binding(concept_key='tw.stock_industry_category', binding_id=102, table='TaiwanStockInfo', column=None, role='observation')
```

## 消費端接線：`scripts/build_stock_graph_edges.py`

`industry_same_edges()`／`main()` 改經 `world_concept.resolve('tw.stock_industry_category')` 取權威表（`quote_ident` 組 SQL），不再字面 `"TaiwanStockInfo"`；函式簽名擴充 `ind_table_sql`／`source_table` 兩參數（同 `_fetch_returns`／`return_corr_edges` 既有慣例，呼叫端解析、函式不自決表名）。

**行為不變性驗證**（同 as_of=2026-06-30 重跑 `--dry-run`）：

| 指標 | 接線前（`WM36-GAP-OPTION-A-EXECUTED` 記錄值） | 接線後（本次 `--dry-run`） |
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
✓ check_vendor_binding --gate 對象數地板:...
（7 條基線已清償/收緊，可自 vendor_binding_baseline.txt 手動移列——不自動改，防棘輪反轉）
  ...(7 條與本案無關之既有存量,詳見終端輸出)
✓ vendor 直綁閘：無新增（基線容忍 130 條指紋/172 處存量，清償制）
```

`scripts/build_stock_graph_edges.py` 之 `TaiwanStockInfo` 一項殘留（`WM36-GAP-OPTION-A-EXECUTED` §「WM.36 止血閘復查」所列「＋ scripts/build_stock_graph_edges.py TaiwanStockInfo quoted_table」）**已消除**——`--gate` 現況對此檔零違規。

**基線檔核對**：`grep build_stock_graph_edges ops/vendor_binding_baseline.txt` → **零筆**——本檔從未被納入基線容忍名單（其 2 條直綁皆屬「新增檔即時違規」而非「既有存量豁免」），故本次修正**不需**、亦**未**編輯 `ops/vendor_binding_baseline.txt`（該檔本應收斂而非放寬，#35 基線只許收斂不許增列；本案零觸碰，非遺漏）。

## 不做

- 未動 `tw.roster_membership`／binding 28 之既有登錄
- 未處理該概念之 `authoritative_binding_id`（現況仍 NULL，即該概念本身未完成權威指定）——與本案獨立、非本次授權範圍
- 未 commit／push（本次僅 DB 寫入＋程式碼修改，git 動作待用戶另行指示）

---

*完。self-reported（#32a）。WM36-GAP 殘留缺口（`TaiwanStockInfo`）已補正；`build_stock_graph_edges.py` 兩處直綁（`TaiwanStockPriceAdj`／`TaiwanStockInfo`）現皆經 registry 解析，零字面直綁殘留。*

# WM.36 發現：Registry 概念設計缺口——`tw.daily_bar` 無法區分 raw／adjusted [I]（2026-08-04）

> **位階**：[I] 發現／追蹤留痕（非 META-CONSTITUTION [N]；非新裁決，僅呈報現況待 Steward 選擇）。
> **觸發**：`archive_push.sh`（本次封存 `archive-20260804-s3waved-s4full-r6-simcell`）pre-commit「WM.36 vendor 直綁止血閘」（`scripts/check_vendor_binding.py --gate`）擋下 `scripts/build_stock_graph_edges.py` 之 2 處新增直綁（`TaiwanStockInfo`、`TaiwanStockPriceAdj`）。
> **本次處置**：Steward 經 `AskQuestion` 選定「本次 commit `--no-verify` 跳過（明示一次性）；先完成封存；另開追蹤項」——本檔即該追蹤項。
> **✅ 2026-08-04 後續已解決（選項 A 執行）**：Steward 經 `AskQuestion` 選 `new_concept_card`；新概念卡 `tw.daily_bar_adjusted`（binding_id=100）已登錄並接線 `build_stock_graph_edges.py`，行為不變性已驗證（13,021 邊逐項比對零差異）。詳見 `audits/WM36-GAP-OPTION-A-EXECUTED-20260804.md`。**殘留**：`TaiwanStockInfo`（產業分類來源）語意錯配為獨立新缺口，未含在本次授權範圍，另案處理。
>
> **⚠ 2026-08-05 再發（封存 `archive-20260805-dirfamily-p6-s4b-alog-beta2`）**：`scripts/probe_classical_ts_phase0b.py`／`scripts/train_classical_ts.py` 新增 `TaiwanStockPriceAdj` 直綁，再次撞 WM.36 閘。Steward 選本封存 `--no-verify`（一次性）。**正確後續**＝改走已落地之 `tw.daily_bar_adjusted`（選項 A／binding 100），勿再累加 `--no-verify`。帳＝`audits/ARCHIVE-CHECKPOINT-20260805-DIRFAMILY-P6-S4B-ALOG-BETA2.md`。

## 一句結論

Registry 目前**同一概念鍵 `tw.daily_bar` 底下同時掛著 raw（`TaiwanStockPrice`）與 adjusted（`TaiwanStockPriceAdj`）兩張候選表**，但 `resolve(concept_key)` API 設計上**只回權威表徵、無法指名要哪一候選**——而今早（`U0-75-REGISTRY-EXECUTED-20260804.md`）已把 `tw.daily_bar` 權威指向 binding **75**（`TaiwanStockPrice`，raw）。若 `build_stock_graph_edges.py` 依閘之建議「改走 registry 解析」，會**悄悄把報酬相關性計算換成未調整價**——除權息跳空污染相關係數，是正確性倒退，非風格問題。故本次**不**照建議改線，改由 Steward 明示 `--no-verify` 放行本次 commit。

## 證據（真實查詢，2026-08-04）

```sql
-- world_channel_binding 現行列（superseded_at IS NULL）
binding_id=28  concept_key=tw.roster_membership  source_table=TaiwanStockInfo
binding_id=81  concept_key=tw.daily_bar          source_table=TaiwanStockPriceAdj
-- （另：binding_id=75 concept_key=tw.daily_bar source_table=TaiwanStockPrice，
--   今早 REGISTRY-GO 已指定為 tw.daily_bar 之 authoritative_binding_id；見 U0-75-REGISTRY-EXECUTED）
```

`src/augur/catalog/world_concept.py` 之 `resolve_rows()`／`resolve()`（M2 API）：解析路徑為「概念鍵 → 現行概念列 → `authoritative_binding_id` → 恰一 binding」，**無任何入參可指定「這個概念下我要哪一個非權威候選」**——`Binding` NamedTuple 亦無 role 篩選欄可供呼叫端二次篩選候選集（`resolve()` 直接回權威那一個，不回候選清單）。

## 為何不能簡單照閘的建議修

`scripts/build_stock_graph_edges.py` 的 `return_corr_*` 邊計算需要**還原（除權息調整）收盤價**才能得到正確報酬序列（`audit/field_correlation.py`、`features/sequence.py` 等既有模組同樣選用 `TaiwanStockPriceAdj` 而非 `TaiwanStockPrice`，是一致慣例、非本腳本獨有選擇）。若改用 `world_concept.resolve('tw.daily_bar')`，因權威現指 75（raw），會拿到**未還原**價格——這不是「換個等價的取數路徑」，是**換了語意不同的資料**。

## 未決選項（呈報、非本檔裁決）

| 選項 | 內容 | 代價／風險 |
|---|---|---|
| **A（新概念卡）** | 新登 `tw.daily_bar_adjusted`（或等義鍵名），權威指向 binding 81（`TaiwanStockPriceAdj`）；比照今早 `REGISTRY-GO: binding=81 + decided_by=hugo` 模式親簽 | 需 Steward 一句裁示＋honesty 證，同 `U0-75` 模式；概念卡數＋1 |
| **B（擴充 resolve API）** | `world_concept.py` 加一入參（如 `role=` 或 `binding_id=` 白名單校驗）允許呼叫端在**已知候選集**中指名非權威 binding，仍全程走 registry（不回退字面） | 改動 M2 API 本體，屬治權工具層擴充，需重新過 `_selftest`／`--check`；影響面較 A 大 |
| **C（維持現狀＋白名單豁免）** | 承認「adjusted 系列」暫時不受 WM.36 消費禁令約束（在 2026-10-15 前另案處理），`build_stock_graph_edges.py` 兩處登記為顯式豁免（附本檔為依據） | 需比照 `reports/wm3536_vendor_registry_plan_20260802.md` §7.3 白名單流程，但本腳本本質是「消費產生下游特徵」而非 C/D 觀測層維運，**歸類恐不誠實**（已於 `AskQuestion` 選項中排除） |

**本檔不選邊**——留待 Steward 於 registry／WM.36 後續批次裁示。

## 誠實邊界（本次 `--no-verify` 之影響範圍）

| 是 | 不是 |
|---|---|
| 本次 commit（`archive-20260804-s3waved-s4full-r6-simcell`）之 pre-commit「vendor 直綁閘」被明示跳過 | 其餘三道閘（治權引用稽核／執行指令矩陣／假斷言閘／`check_vendor_binding --gate` 之對象數地板檢查）**皆已通過**，僅「新增直綁」一項被跳 |
| 已委託 `stock_graph_edge` 13,021 列（S3-WAVE-D Phase 2c，2026-08-04 稍早以直接執行 `--commit` 產生，非經本次 commit）**資料本身正確**——執行當下讀的就是 `TaiwanStockPriceAdj`（還原價），未受影響 | 本次跳過**不代表**問題已解決；`ops/vendor_binding_baseline.txt` 基線**未更新**（下次任何人對 `build_stock_graph_edges.py` 再跑 `--gate` 仍會擋，除非走上表 A／B／C 之一或再次 `--no-verify`） |
| 追蹤項已留痕（本檔），下次 S3/S4 相關工作觸及此腳本時應優先處理 | 不得靜默消失、不得未來又用 `--no-verify` 繞過而不留痕（違 CLAUDE 回歸鎖／誠實精神） |

## 下一動作（建議，非義務）

下次有 Steward 明示裁示（選 A／B／C 之一，或另案）時處理；在此之前 `build_stock_graph_edges.py` 維持現狀（正確但未過 WM.36 閘），**任何人對此檔再次 commit 前須知悉本檔**。

---
status: executed
series: s4_model_families
depends_on:
  - reports/augur_s4_dirfamily_generalize_plan_20260804.md
---

# S4-DIRFAMILY-GENERALIZE Phase 0 — 執行紀錄（2026-08-04）

> **性質**：[I] 執行紀錄（計畫＝`reports/augur_s4_dirfamily_generalize_plan_20260804.md`；Steward 2026-08-04 授權「approve_now」）。
> 範圍＝計畫§4「Phase 0」全表列 3 支腳本泛化＋R1/R2 防禦性加固；**不含** Phase 1（無新 family 寫入、無新 `model_id`）。

## 1. 完成項目

| 檔 | 動作 | 結果 |
|---|---|---|
| `scripts/build_probability_oos_sample.py` | `MODEL_FAMILY` 常數 → `--model-family` CLI（`default="RankRidge"`,`choices=ranker.ALL_FAMILIES`）；`emit_horizon` 移除 inline `StandardScaler+Ridge`,改 `{c.family: c for c in ranker.ALL_FAMILIES}[model_family]` dispatch(同 `portfolio.py` 既有模式) | ✓完成 |
| `scripts/calibrate_relative_probability.py` | `MODEL_FAMILY` → `--model-family` CLI；`_load`/`emit_horizon` 之 family 過濾參數化；**R1 修法**:`cid` 加入 family(`platt_{family}_h{h}_asof{FREEZE}_g{git7}`) | ✓完成 |
| `scripts/train_direction_stack.py` | `_load_joined(cur,h)` → `_load_joined(cur,h,model_family="RankRidge")`,SQL 加 `AND s.model_family=%s`;`run()` 簽名同步加 `model_family="RankRidge"` 參數(**R2 修法**) | ✓完成 |

**與計畫文字之偏差(誠實記錄)**：計畫§4 第三列寫「`run()`／`run_v2()` 呼叫處傳入同一參數」;實際讀碼確認 `run_v2()`(DirStackM 月頻)**從不呼叫** `_load_joined`——其標籤自算自 `TaiwanStockPriceAdj`(docstring 原文「不再抄 probability_oos_sample.fwd_ret」),與 `probability_oos_sample`/`MODEL_FAMILY` 完全無涉。故只改 `run()`,`run_v2()` 零改動——此為依code事實(#26)之範圍修正,非漏做。

## 2. 行為不變性驗證(§6 Gate;非字面「全表逐列 diff」,理由見下)

**方法論調整(誠實記錄)**：原計畫§7 設想「重跑 --fit/--run 前後輸出 diff」。實際執行時發現 `build_probability_oos_sample.py --run --horizon 60`(無 `--limit-folds`)於**今日**重跑,因 `feature_values` 為 live 增量表(每日成長),產出折數從原 24 折/10549 列漲到 102 折/34611 列——此為資料成長,非程式改動之效果;若以「重跑前 vs 重跑後」之全表列數/總和做 diff,會被資料成長混淆,無法乾淨歸因於程式改動本身。改採**兩種更嚴謹、不受資料成長干擾**之驗證：

### 2a. 演算法等價性(直接證明,非旁證)
於同一 Python session,對同一筆真實 (Xtr,ytr,Xte)(H60、test_pd=2026-04-30 折,223 檔測試):
- 舊法:`StandardScaler().fit(Xtr)` → `Ridge(alpha=1.0).fit(...)` → `predict`
- 新法:`ranker.RankRidge().fit(Xtr,ytr).predict(Xte)`

```
pred_old vs pred_new 位元級相等(atol=0,rtol=0): True
max abs diff: 0.0
pred_new vs DB 實際寫入 score:  max diff: 0.0
```

**結論**：`build_probability_oos_sample.py` 之 dispatch 化改動,對預設族(RankRidge)零漂移——非「大致一樣」,是**位元級相同**。

### 2b. 無資料成長干擾之路徑(H20,`train_direction_stack.py` R2 修法)

`probability_oos_sample` H20 本次**未被觸碰**(僅 H60 被重跑),故前後可乾淨對照：

| | count | sum(p_up) | sum(y_up) | sum(fwd_abs_ret) | fold 數 |
|---|---|---|---|---|---|
| 修改前(R2 修法前之現況值) | 6188 | 2975.990386912016 | 2848 | 10.646644929021662 | 16 |
| 修改後(`_load_joined` 加 `AND model_family='RankRidge'` 後重跑) | 6188 | 2975.990386912016 | 2848 | 10.646644929021662 | 16 |

**逐值位元相同**——確認現況下 `probability_oos_sample` 僅有 `RankRidge` 一族,新增之 family 過濾為**精確 no-op**,`direction_oos_sample` 輸出零改變。

### 2c. R1 修法(`calibrate_relative_probability.py`)實跑確認

```
✓ H60: platt_RankRidge_h60_asof2026-05-31_g5a96c09 | 折 101/102 | Brier 0.2452 vs 基線 0.2500 | ECE 0.0075 | ...
✓ H60: emit 339 檔 | p∈[0.373,0.626] | econ=thin_unestablished | ≈87 日曆日 | platt_RankRidge_h60_asof2026-05-31_g5a96c09
```

`calibrator_id` 確認含 family(`platt_RankRidge_...`,原格式無 family)——R1 修法生效;`_platt_fit`/`_sigmoid` 核心計算邏輯零改動,`emit_horizon` 成功產出 `prediction_probability`。**因 H60 之 `probability_oos_sample` 已於 2a 步驟重跑漲至 102 折**,此處 Brier/ECE 數字為**新折數下之現況值**,非「與舊值逐位元相同」之宣稱對象——舊格式 `calibrator_id`(不含 family)之歷史列仍留在 `probability_calibrator` 表中未被覆蓋(新舊 id 不同,`ON CONFLICT` 不會撞;`emit_horizon` 之 `ORDER BY created_at DESC LIMIT 1` 選到新列,行為正確),為 R1 修法之預期、可解釋的副作用,非資料損毀。

## 3. 查核中發現、誠實揭露(超出本計畫範圍,不在此修)

**發現**：H60 之 `probability_calibrator` 新列 `purge_verified=False`(修改前舊列為 `True`)。追查根因：`_asof_panels`/`AS_OF="2026-05-31"` 只限制**測試 panel** 之上界(`panel_date<=AS_OF`),**未限制其 `exit_date`**;H60=60 個交易日≈3 個月,故 panel_date 落在 2026-03-31/2026-04-30(距 AS_OF 僅 1-2 個月)之折,其 h=60 exit_date 自然落在 AS_OF **之後**(2026-06-30/2026-07-29)。今日 `feature_values` 已成長到含這些晚期 panel(原始建表時未必有),故今日重跑才第一次觸發此旗標。

**確認非洩漏**(#8)：`SELECT max(date) FROM "TaiwanStockPriceAdj"` = `2026-08-04`(今日);exit_date=2026-07-29 之 `fwd_ret` 使用之價格**已真實實現**(非未來偷看)——`purge_verified=False` 反映的是「此列超出**該管線原始設計時**選定之 2026-05-31 靜態快照錨」之**標籤/命名邊界**,不是「用了尚未發生的價格」之**時點邏輯**違規。

**歸屬**：此為 `build_probability_oos_sample.py`/`calibrate_relative_probability.py`**原始(未經本計畫編輯)程式碼**既有之 AS_OF 邊界設計缺口(只治「哪些 panel 可當測試折」,未治「exit_date 是否仍在快照窗內」)——**任何人今天重跑未經編輯之原版腳本,會得到完全相同的 `purge_verified=False`**,與本計畫之 family-dispatch 泛化編輯**無因果關係**。是否要修補(如替 AS_OF 加 exit_date 上界過濾,或把 `oracle e2e` 這條舊管線之 FREEZE 錨滾動/退役)**不在本計畫授權範圍**,留待 Steward 另裁——本記錄僅誠實揭露、不誅代修。

## 4. 硬邊界遵守確認

- ✓ FZ/GATE-keep:全程未碰 `direction_gate`/`arena_admission_gate` 任何 criteria。
- ✓ no-SIM-apply／skip-sync:全程零 FinMind／FRED 呼叫、零模擬套用。
- ✓ 零新 family 寫入:`probability_oos_sample`/`probability_calibrator`/`direction_oos_sample` 皆只有 `RankRidge`(唯一既有族)之列;Phase 1(materialize 其他族)未觸發、未執行。
- ✓ `ReadLints`:3 檔皆無新增 lint 錯誤。

## 5. 結論

Phase 0 完成、行為不變性以**演算法等價性直接證明**(2a)+**無干擾路徑逐值相同**(2b)+**實跑成功**(2c)三種互補證據確立(較原計畫「全表 diff」設想更嚴謹,因排除資料成長干擾)。R1(calibrator_id 碰撞)、R2(混族攤平污染)兩項既有潛在缺陷已修補。額外發現一項**既有、非本計畫範圍**之 AS_OF/exit_date 邊界問題已誠實記錄於§3,留 Steward 裁示是否另案處理。

Phase 1(某族 materialize+新 `model_id` DirStack 比較)**仍未觸發**——依計畫§6,需等 Wave-A Phase 0 探針「某族 3-seed net Sharpe min 真贏 RankRidge」;探針現正背景執行中(見 `S4-WAVE-A-SKLEARN-EVAL-20260804.md`,H20 已見 `RankSVM` 真贏訊號,H60 尚未有族真贏)——是否推進 Phase 1 待該探針完整結束後另評估、另請 Steward 授權。

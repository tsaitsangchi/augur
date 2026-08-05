# S3-WAVE-C EXECUTED 帳 [I]（2026-08-04）——組 10–11 契約查核：確認已對齊＋一項新缺口另呈

> **位階**：[I] 執行留痕（非 META [N]）
> **GO**：`audits/S3-WAVE-C-GO-20260804.md`
> **性質**：本波為**唯讀查核**（非新建）——結論：組 10–11 之「方向表↔ranker 契約對齊」**已由既有「oracle 主計畫」（`reports/augur_oracle_upgrade_master_plan_20260711.md`，2026-07-11）系出一脈的獨立管線滿足**，非本波新做。母 SSOT（2026-08-04 撰寫）標記該二組為「旁路表；契約分離」係**特徵表本身**（`feature_values` 未含 direction 欄）之字面觀察，**未計入**同日期更早已存在、經契約對齊之下游 direction 管線——本帳以程式證據更正此描述落差，並誠實標出查核中新發現、超出本波字面授權範圍之一項缺口供另裁。

---

## 1. 查核方法

逐一讀程式（非猜測，CLAUDE #15）：`build_market_direction_features.py`／`train_market_direction.py`／`build_daily_direction_features.py`／`train_daily_direction.py`／`train_direction_stack.py`／`cross_section.py`／`evaluation/baseline.py`／`evaluation/portfolio.py`／`build_probability_oos_sample.py`／`calibrate_relative_probability.py`；並以 DB 查詢核列數（見 §2/§3 各表列數，來源＝psql 查詢，符合 #9 三類來源之 (b)）。

## 2. 組 10（Market-level／regime／direction panel）——確認已對齊

| 子項 | 表 | 消費端 | as-of／PIT 機制 | 現況（DB 實測） |
|---|---|---|---|---|
| 市場級（大盤/選擇權/景氣燈號） | `market_direction_feature`（20 特徵，逐欄 `visible_date`） | `train_market_direction.py`（`_load_features`：`searchsorted(visible_date, panel_date, side="right")-1`＝每 panel 取最新 `visible_date≤panel` 之值，forward-fill 語意） | 逐欄 `visible_date`（盤後 lag1／同日 lag0／VIX 走 `macro_vintage.as_of` PIT）；`#8` 消費端強制過濾，非 builder 端假設 | `market_direction_probability`：**28,621 列／2 model_id（MktLogit／MktLogit_v2）／4 horizon** |
| 個股日頻方向 | `daily_direction_feature_values`（14 特徵：`d_*` 個股＋`m_iv`／`m_taiex_ret5` 市場） | `train_daily_direction.py`（v1 champion + v2 `DailyGBDT_cal` purged isotonic 校準） | 年塊 walk-forward＋真 purge（train 樣本日 ≤ test 年首前推 k+1 td） | **19,300,921 列／2,853 panel／776 檔** |
| 相對→市場合成（stacking 之市場臂） | 上兩表之下游 | `train_direction_stack.py`（`DirStack`／`DirStackM` 月頻版） | 合成器再 walk-forward、輸入分量皆已各自 OOS | `direction_oos_sample`：**model_id ∈ {DirStack, DirStackM}** 皆有列 |

**結論**：組 10 之「契約對齊」——即「市場級／日頻方向特徵如何以 point-in-time 安全之方式進入模型訓練」——**已在 2026-07-11 起之 oracle 主線完整落地並持續產出**，非待做事項。母 SSOT 稱其「旁路表；契約分離」係指**未併入 `feature_values`**（EAV 股級生產特徵表）此一物理事實，但下游**已有專屬對齊管線**，非無契約。

## 3. 組 11（Interaction／composite candidates）——確認已對齊、且新族自動繼承

- **註冊表**：`src/augur/evaluation/cross_section.py` 之 `INTERACTIONS` dict（現 1 項：`inter_fh_x_p10yr`＝`foreign_holding_pct`×`price_to_10yr` 橫斷面 z 乘積；已過四道漏斗＋經濟價值驗證、opt-in 限 374 核心宇宙）。
- **接線**：`baseline._fold_xy`／`baseline.run_ladder` 之 `interactions=` 參數（研究/驗證路徑，`verify_interaction_promotion.py` 消費）；`portfolio.run_backtest` 之 `interactions=` 參數（**經濟評測路徑**，`run_economic_eval.py` 消費）——兩路徑皆呼叫 `_panel_matrix`→（若 `interactions`）`cross_section.augment`→`_fold_xy`，同一組矩陣同時餵 train／test。
- **對 Wave-A 新族之繼承驗證（本次讀碼確認，非假設）**：`portfolio.py` 第 195–198 行本回合新增之 `_WAVE_A_SKLEARN_FAMILIES` 分支（`RankXGB`／`RankCat`／`RankRF`／`RankSVM`／`RankKNN`／`RankMLP`）位於 per-fold 迴圈**之內**、在同一個已套用 `interactions` 之 `Xtr/Xte` 之**後**才 dispatch model class——即新 6 族**零額外接線、自動享有 `interactions` 支援**（`portfolio.py:174-180,195-198`）。

**結論**：組 11 之契約**在本波查核前即已完整**（`cross_section.py` 建於更早的 Wave-B 期間），且本回合新增之 Wave-A 6 族因複用同一 `_fold_xy`/`_panel_matrix` 管線而自動對齊，不需任何本波程式異動。

## 4. 誠實查核中發現、超出本波字面授權之一項缺口（不在本波執行、另呈）

`probability_oos_sample`（`build_probability_oos_sample.py`）→ `calibrate_relative_probability.py` → `train_direction_stack.py` 三支之「相對分量」端**全程硬編碼 `MODEL_FAMILY="RankRidge"`**（三支各自常數，非參數化；`build_probability_oos_sample.py:36`／`calibrate_relative_probability.py:40`）。

- **影響**：Wave-A 現有 8 族（`RankRidge`／`RankGBDT`／本回合新增 6 族）中，**僅 `RankRidge` 能餵入 DirStack／`direction_gate`**；其餘 7 族（含新 6 族）目前**無法**成為「相對分量」候選，即母 SSOT「服務 direction／stacking（S4 Wave A／E）」對**新擴充 Wave-A 族**尚未完全實現。
- **為何不在本波執行**：(a) 此為**模型 dispatch 泛化**問題（S4 模型層性質），非組 10–11 之**特徵契約**問題（S3 字面範圍）；(b) 觸碰對象＝`probability_oos_sample`／`direction_gate`／arena 准入之**確立級生產鏈**（CLAUDE 資料真實性條款所稱「live 准入」路徑），非「無新表需求」之輕量對齊，屬 CLAUDE #20 之「介面／架構變更」門檔，宜另立 plan-first 供 Steward 拍板範圍（尤其是否連動 `calibrate_relative_probability.py`／`train_direction_stack.py`，以及是否需要為新族重跑歷史 `probability_oos_sample`）。
- **建議下一手句**（供 Steward 選用，本帳僅記錄不代為執行）：`S4-DIRFAMILY-GENERALIZE-plan-first`——泛化 `build_probability_oos_sample.py` 之 `--model-family`（複用 `augur.models.ranker.ALL_FAMILIES` dispatch，同 `train_ranker.py`／`portfolio.py` 已用模式），預設仍 `RankRidge`（零行為改變），新族僅新增列（`DELETE...WHERE...model_family=%s` 既已限定單族、天然冪等不動舊列）。

## 5. 硬邊界遵守確認

- `skip-sync`：全程零 FinMind／FRED 呼叫（僅讀本地程式碼＋本地 DB `SELECT`）。
- `no-SIM-apply`：未碰任何 sim 相關表／腳本。
- `FZ/GATE-keep`：未修改任何 gate 判準；`direction_gate`／`arena_admission_gate` 程式碼零異動。
- 未寫入任何生產表（`market_direction_probability`／`probability_oos_sample`／`direction_oos_sample` 等）——本波純查詢＋讀碼，DB 存取皆 `SELECT`。

## 6. 結論

- **組 10–11 契約對齊＝確認已達成**（非本波新建；證據＝§2/§3 程式讀碼＋DB 列數）。
- **母 SSOT 描述已更正**：「旁路表；契約分離」僅指未併入 `feature_values` 之物理事實，非「無契約」。
- **新發現缺口**（Wave-A 新族尚不能餵 DirStack）**已誠實記錄、未擅自執行**，留供 Steward 另裁範圍。
- S3-Wave-C 波**視為完成**（查核性質；`reports/augur_project_optimization_plan_r6_20260804.md` §2 候選 GO 句表隨後同步更新）。

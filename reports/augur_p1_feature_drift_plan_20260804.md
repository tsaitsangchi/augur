# P1 特徵漂移對齊呈案（2026-08-04）

> **位階**：[I] 呈案（非 META [N]）。**授權**：`P1-DRIFT-PLAN-go`。  
> **本輪只呈案**——**不**擅改 prodset 特徵名、**不**重訓、**不**寫 `prediction_values`。  
> **證據錨**：`audits/OPT-R3-W2PREP-S1P1-20260804.md`＋本輪唯讀複現。

---

## 1. 事實（親查）

| 項 | 值 |
|---|---|
| 指令 | `python scripts/predict_asof.py --run --dry-run` |
| 結果 | **拒載中止（誠實）** |
| 訊息要旨 | `feature_source=prodset` 特徵漂移：frozen `['inst_cumflow_position_120d','lending_fee_rate_mean_20d']` vs current `['cycle_position_252d','inst_cumflow_position_120d','lending_fee_rate_mean_30d']` |
| 現役 prodset（`set_status='active'`） | `cycle_position_252d` · `inst_cumflow_position_120d` · `lending_fee_rate_mean_30d` |
| 根因類別 | artifact 凍結特徵集與現行 prodset **不一致**（`mean_20d`→`mean_30d`＋多了 `cycle_position_252d`）——**非** FinMind／FRED／API 凍結問題 |

`predict_asof` 行為（code）：prodset 源 → 漂移則**拒載**；canonical 舊模型 → 僅告警仍 serve。本拒＝prodset 路徑之正確誠實。

---

## 2. 選項（Steward 圈選）

| 代號 | 方案 | 做什麼 | 不做／風險 | 何時適用 |
|---|---|---|---|---|
| **A. rename-align** | 對齊名／artifact 與 prodset | 以現行 active 三顆為準，重產或換掛 **prodset 口徑**之 predict artifact（凍結 feats＝current） | 不手改歷史 panel 列；不把 `mean_20d` 假稱仍現役 | 要恢復 prodset hotpath dry／serve |
| **B. canonical-arm** | 研究臂 | 明示 `--feature-source=canonical`（若 CLI／registry 仍供）走 canonical 集；或接受「僅研究、非 prodset」 | **不得**把 canonical 分數宣稱＝可交易／確立級 | 只要庫內推估數字、不堅持 prodset 契約 |
| **C. retrain-asof** | 庫內 as-of 重訓 | `train_*`／panel as-of 重訓，metrics 寫入現行 prodset feats；再 dry-run | 需 slot／算力窗；**仍** `--skip-sync`；禁 live API 硬前提 | A 的完整版（新模型＋新凍結） |

可複選時序：**B（先看數）→ A／C（恢復 prodset 契約）**。

---

## 3. 建議裁句（AI 不代勾）

```text
P1-DRIFT: A=rename-align | B=canonical-arm | C=retrain-asof | defer
```

單選示例：

```text
P1-DRIFT: B-first then C   # 先 canonical 研究臂；再庫內 as-of 重訓掛回 prodset
P1-DRIFT: C-go             # 直接重訓 as-of（另授 train 窗／不搶 TWEVO）
P1-DRIFT: defer            # 維持拒載誠實；不開 predict hotpath
```

執行時建議加護欄句（可併）：`FZ/GATE-keep` · `no-SIM-apply` · `skip-sync`。

---

## 4. 驗收（裁後才適用）

| 方案 | 驗收 |
|---|---|
| A／C | `predict_asof.py --run --dry-run` **不再**因 prodset 漂移拒載；stdout 可溯 frozen＝current active |
| B | dry／serve 明示 `feature_source=canonical`；報告不寫「prodset 可交易」 |
| 共通 | 零 FinMind／FRED 新抓；不 hand-patch artifact JSON 卻謊稱同源 |

---

## 5. 本輪未做（呈案當下）

- 未改 `evolution_production_feature_set`  
- 未重訓、未 `--apply` sim  
- 未宣稱預測可交易  

---

## 6. 執行回填（Steward `P1-DRIFT: A` · 2026-08-04）

| 驗收 | 狀態 |
|---|---|
| [x] A：`predict_asof.py --run --dry-run` 不再因 prodset 漂移拒載 | **綠** — `audits/P1-DRIFT-A-EXECUTED-20260804.md` |
| [x] stdout 可溯 frozen＝current active 三顆 | `RankRidge_H60_2026-06-30_seed42_56d03625463b3eba` |
| [ ] B canonical-arm | 未授權／未做 |
| [x] C 完整 retrain-asof（多 horizon／經濟終關） | **EXECUTED** — `audits/P1-DRIFT-C-EXECUTED-20260804.md`（H20＋H60；econ prodset） |

機制：換掛不可行（無既有 artifact＝active 三顆）→ `train_ranker.py --run` 重產 prodset 口徑。零 FinMind／FRED；dry-run 未寫 `prediction_values`；≠可交易。

### C 回填（Steward `P1-DRIFT: C-go` · 2026-08-04）

| 項 | 狀態 |
|---|---|
| H20／H60 RankRidge prodset 重產／對齊 | 綠（H60＝A 既有；H20 本輪新產） |
| dry-run 兩 H | 綠；未寫庫 |
| 經濟終關 `run_economic_eval --feature-source=prodset` | 已跑；Ridge net＞基準（H20／H60）；≠確立級 |
| 殘 | H40／H120；predict 寫庫／SIM／direction_gate 另句 |

*完。*

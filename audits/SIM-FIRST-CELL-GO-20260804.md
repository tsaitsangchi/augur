# SIM-FIRST-CELL-go 授權留痕 [I]（2026-08-04）

> **位階**：[I] 拍板留痕（非 META-CONSTITUTION [N]）。
> **父 SSOT**：`reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` §7.3（`predict-asof-write-go` / **`SIM-FIRST-CELL-go`** 等，列於「加料，非默認」）。
> **上游門**：`evolution_prereg_gate.SIM-CAL-R1`（status=approved，approved_at≈2026-08-02；K_TARGET=3、H_TD=21、arm=live、52 檔凍結清單）。
> **本輪選項來源**：`AskQuestion`（Steward 從「Tier 1 已就緒單句可貼」清單中選 `sim_first_cell`）。

## 授權四要件（CLAUDE #26）

| 要件 | 內容 |
|---|---|
| (a) 範圍 | 僅 `scripts/run_sim_calibration_cell.py --apply`（產格：寫 `mc_simulation_run`＋`sim_run_link`＋開/推進 `sim_evolution_iteration_ledger`）；視 dry-run 結果**可能**接續 `settle_sim_outcomes.py`／`evaluate_sim_calibration.py`／`decide_sim_verdict.py`（唯讀或 --apply，視當下是否有可結算格點而定，若 0 可結算則僅執行現況查詢） |
| (b) 期限 | 本次對話會話內；一次性產格動作（insert-only 冪等，非常駐） |
| (c) 可撤銷 | 隨時可撤；寫入為 insert-only（表無 UPDATE/DELETE 通道），撤銷＝不再呼叫 `--apply`，不代表刪列 |
| (d) 所繫計畫 | `augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` §2.7（S0 Discovery）／§7.3 |

## 效力邊界

| 是 | 不是 |
|---|---|
| 產出 sim 校準首格（`mc_simulation_run`＋`sim_run_link`）、開啟 `sim_evolution_iteration_ledger` 首輪（`planned→running`） | `--allow-apply` TWEVO／arena；FinMind／FRED 放量；kill A1 |
| 若當下已有可結算格點（label 已實現）→ 可續跑 `settle_sim_outcomes.py --apply` | 假造未實現之 realized_outcome；催 K&lt;3 當完成 |
| 0 自動 promoted（`decide_sim_verdict` 僅在 K≥3 才有意義；本輪大機率 K=1，不觸發） | 任何形式之「可交易」／「確立級」宣稱 |
| 三防衛（kill switch／門 sha／52 檔清單 sha）先驗紅、拒產即停 | 繞防衛、放寬門檻 |

## 硬禁（本輪，繼承父計畫）

- 零 FinMind／FRED 放量；零 sync
- 零 `--allow-apply`（TWEVO／arena）；不殺 A1；不搶 `heavy_slot`
- 零假確立級／可交易宣稱；sim 校準 ≠ #14 經濟終關 ≠ direction_gate
- 不 commit／push（除非另行明示）

## 執行序（將依 dry-run 結果調整，逐段留痕於 EXECUTED 審計）

1. `run_sim_calibration_cell.py`（無參數＝現況）→ `--selftest` → `--dry-run` → 呈結果 → （如乾淨）`--apply`
2. `settle_sim_outcomes.py`（無參數＝現況，判斷本輪是否有可結算格點）
3. 視 (2) 結果決定是否有意義呼叫 `evaluate_sim_calibration.py`／`decide_sim_verdict.py`（K&lt;3 大機率僅現況查詢，不觸發真評估）

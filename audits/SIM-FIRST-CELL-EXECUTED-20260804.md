# SIM-FIRST-CELL-go 執行／驗收帳 [I]（2026-08-04）

> **位階**：[I] 執行留痕（非 META-CONSTITUTION [N]）。
> **授權**：`audits/SIM-FIRST-CELL-GO-20260804.md`（`SIM-FIRST-CELL-go`，Steward 經 `AskQuestion` 從 Tier 1 清單選定）。
> **上游門**：`evolution_prereg_gate.SIM-CAL-R1`（approved 2026-08-02 19:49:40+08；K_TARGET=3、H_TD=21、arm=live、52 檔凍結清單）。
> **對應 Discovery**：`audits/SIM-SELF-EVOLVE-S0-DISCOVERY-20260804.md` D-CELL（「sim 首格未落地」，本輪解決）。

## 一句結論

**sim 校準首格已落地**：格點 `2026-08-03`、候選 `simc_r1_iid_baseline`、52/52 檔全產（`mc_simulation_run`＋`sim_run_link`），迭代帳本 `sim-20260803-r01` 開為 `running`；時鐘現讀 **K=1/3**。settle／evaluate／decide 三段誠實回報「未到、非錯誤」——**0 自動 promoted**，符合效力邊界。

## 做了什麼（依序、皆真實指令輸出）

| # | 步驟 | 指令 | 結果 |
|---|---|---|---|
| 1 | 工具健康 | `run_sim_calibration_cell.py --selftest` | 33/33 綠（格點數學／run_id 決定論／三防衛先驗紅／帳本 SQL 不變式全過） |
| 2 | 現況（唯讀） | `run_sim_calibration_cell.py`（無參數） | 門 approved；kill clear/clear；候選僅 1（`simc_r1_iid_baseline`）；anchor=2026-08-03；已產 link 0/52 |
| 3 | 預演（唯讀，零寫入） | `--dry-run` | 1 格點待產；52 檔皆歷史足量（0 排除）；補鏈 0（無殘留） |
| 4 | **產格（寫入）** | `--apply` | 帳本 `sim-20260803-r01` 新開 `planned→running`；新產 52／52 檔；`insert-only ON CONFLICT DO NOTHING` |
| 5 | 冪等驗證 | 重跑 `--apply` | 帳本「沿用既有列」；新產 **0**／已跳過 52（證明冪等不重複） |
| 6 | 結算現況（唯讀） | `settle_sim_outcomes.py`（無參數） | link 52 列｜已結 0｜未結 52（label 未實現，誠實非錯誤） |
| 7 | 評估現況（唯讀） | `evaluate_sim_calibration.py`（無參數） | 兩級指紋覆算合；已實現格點=1；K 需求=3；`本評估=self-reported，promoted 須三鎖人簽` |
| 8 | 判決現況（唯讀） | `decide_sim_verdict.py`（無參數） | eval=0／verdict=0；殘項：`promoted` 路徑需人簽，本工具不寫 `promoted` |
| 9 | 時鐘驗證（唯讀） | `check_sim_clock.py --week-line` | **`sim 時鐘：K=1/3，下一格 未實現，待結算 52 列`**（不再是 D-CELL discovery 之 `UnmappedConcept` 阻斷） |

## 產出（真實 DB 狀態，2026-08-04）

| 表 | 變化 |
|---|---|
| `mc_simulation_run` | +52 列（`target_id`∈52 檔凍結清單；`asof_date=2026-08-03`；`horizon_td=21`；`method=iid_bootstrap`；`n_paths=10000`；`seed=42`；`is_simulation=true`） |
| `sim_run_link` | +52 列（`gate_id=SIM-CAL-R1`；`candidate_id=simc_r1_iid_baseline`；`iteration_uid=sim-20260803-r01`；`arm=live`） |
| `sim_evolution_iteration_ledger` | +1 列（`sim-20260803-r01`，`status=running`，FK 之被指對象） |
| `sim_realized_outcome`／`sim_calibration_eval`／`sim_evolution_verdict` | **仍 0**（label 未實現；下一動作＝等 21 個交易日後之 label 日再 `settle_sim_outcomes.py --apply`） |

## 效力邊界（本輪守住）

| 是 | 不是 |
|---|---|
| 首格已產、K=1/3、迭代帳本 running | K=3 完整校準；`decide_sim_verdict` 判 `promoted` |
| insert-only、冪等已驗證（重跑零新增） | UPDATE／DELETE／覆寫任何既有列 |
| settle／evaluate／decide 誠實回報「未到」 | 假造 `sim_realized_outcome`／催 K&lt;3 當完成 |
| 三防衛（kill switch／門 sha／52 檔清單 sha）全過 | 繞防衛、放寬門檻、改 `SIM-CAL-R1` criteria |

## 硬禁複核

- 零 FinMind／FRED 放量；零 sync
- 零 `--allow-apply`（TWEVO／arena）；未殺 A1；未搶 `heavy_slot`
- 零假確立級／可交易宣稱；sim 校準 ≠ #14 經濟終關 ≠ `direction_gate`
- 未 commit／push

## 下一動作（誠實排程，非本輪義務）

1. **等待**：label 日＝anchor 後第 21 個已實現交易日（≈2026-09 下旬，視交易日曆），屆時 `settle_sim_outcomes.py --apply` 才有列可結。
2. **格點 2／3**：`run_sim_calibration_cell.py --apply` 為冪等補產設計——後續每 21 個交易日再跑一次（或掛日頻/週頻 cron，另案授權）即可補產格點 2、3；**本輪未**掛排程，維持人工節奏。
3. **K=3 後**：`evaluate_sim_calibration.py --apply` 才可能真評估（仍受五臂／樣本外門檻）；`decide_sim_verdict.py --apply` 僅寫 `killed`／`undecidable`，**`promoted` 恆需人簽**。

## 複核指令

```bash
cd /home/hugo/project/augur && set -a && . ./.env && set +a
venv/bin/python scripts/run_sim_calibration_cell.py           # 現況：應顯示 link 52/52
venv/bin/python scripts/check_sim_clock.py --week-line        # 應顯示 K=1/3
```

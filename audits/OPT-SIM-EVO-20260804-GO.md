# OPT Sim Evolution 專項拍板登錄 [I]（2026-08-04）

> **位階**：[I] 拍板留痕（非 META-CONSTITUTION [N]）。  
> **時點**：約 **2026-08-04 08:08+08**（Steward 裁示「拍板」）  
> **碼**：`OPT-SIM-EVO-20260804-go` ＋ `FZ-keep` ＋ `GATE-keep` ＋ `M-T5-watch`

## 標的檔

| 角色 | 路徑 |
|---|---|
| **專項 SSOT（本裁）** | `reports/augur_local_ai_sim_evolution_plan_20260804.md`（`status: current`） |
| 一般優化 step／runbook | `reports/augur_optimization_step_plan_r2_20260804.md`（`OPT-STEP-R2-20260804-go`） |
| 執行註冊（master） | `reports/augur_optimization_master_plan_r2_20260803.md` |
| 理解地基 | `reports/augur_deep_understanding_r5_20260803.md` |

## 定位

| 是 | 不是 |
|---|---|
| sim 校準自進化優化**專項** SSOT | **不取代** `OPT-STEP-R2-20260804-go` |
| **complement** step r2（吃觀測窗／共槽紀律） | 第三份 master／另一條「夜班後第一刀」執行序 |
| FZ-keep／GATE-keep／M-T5-watch | 解凍 FinMind／FRED；降閘；代簽 I5 |

## 兩裁＋預設伴隨裁

| 問 | 裁 |
|---|---|
| 1. 拍板本檔為 sim 自進化優化專項 SSOT？ | **是（go）** |
| 2. 取代一般 step r2？ | **否**——complement only |
| **預設伴隨裁 A**（用戶未另答 Q2） | run22 期間開工＝**僅觀測＋儀器設計＋零 DB selftest**；禁 Lane-SIM-APPLY／搶 `heavy_slot`／`--allow-apply` |
| **預設伴隨裁 B**（用戶未另答 Q3） | 結輪後優先＝**先 Step1 65 triage**（已拍 `wait_done`）；sim P0 **不搶 slot**，可後接或輕並行 |

> 伴隨裁標 **預設、可另改**——本波 Steward 只明示「拍板」；Q2／Q3 採計畫書建議預設落地。

## 効力邊界（本波）

| 是 | 不是 |
|---|---|
| draft→current；專項讀序成立 | 搶 `heavy_slot` |
| 允許文件／唯讀儀表設計／零 DB `--selftest` | `--allow-apply`／改 evolution driver／殺 run22 |
| 與 Step0 監看敘事相容 | **現在**開 65 triage SQL／報告 |
| 結輪後 sim P0 後接或輕並行（不插隊 Step1） | 自動授權首格人工 `--apply` 窗 |

## 硬禁（本波落地窗）

- 不搶 `heavy_slot`  
- 不 `--allow-apply`／不開 Lane-SIM-APPLY  
- 不開 65 triage  
- 不 commit／push（待 AskQuestion）

## 下一步（機械提醒）

1. 守伴隨裁 A 至 run22 結輪；DB 復通後才做 P0-D 數字帳。  
2. 結輪後 **Step1 先**（`OPT-STEP-R2-20260804-go`）；sim P0 不申請插隊。  
3. 首格若確認未落地 → **另裁**單次 apply 窗（本拍不授權）。  
4. Steward 確認：commit／push？；是否現在開觀測＋selftest 第一刀？

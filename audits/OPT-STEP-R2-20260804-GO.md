# OPT Step Plan r2 拍板登錄 [I]（2026-08-04）

> **位階**：[I] 拍板留痕（非 META-CONSTITUTION [N]）。  
> **時點**：約 **2026-08-04 01:07+08**（Steward 裁示）  
> **碼**：`OPT-STEP-R2-20260804-go` ＋ `FZ-keep` ＋ `GATE-keep` ＋ `M-T5-watch`

## 標的檔

| 角色 | 路徑 |
|---|---|
| **step／runbook 執行 SSOT** | `reports/augur_optimization_step_plan_r2_20260804.md` |
| 執行註冊（master） | `reports/augur_optimization_master_plan_r2_20260803.md` |
| 理解地基 | `reports/augur_deep_understanding_r5_20260803.md` |
| 上游 SSOT 拍板 | `audits/OPT-R5-R2-SSOT-APPROVED-20260803.md` |
| 降為史料 | `reports/augur_optimization_step_plan_20260803.md`（舊 `OPT-STEP-20260803-go` 退場） |

## 兩裁（對 §8）

| 問 | 裁 |
|---|---|
| 1. 拍板本檔為逐步執行 SSOT？ | **是（go）** |
| 2. 立刻開 Step 1／Lane-R？ | **否**——採 **(a) 等結輪**；Step 1＝**`wait_done`** |

## 効力邊界

| 是 | 不是 |
|---|---|
| 採納 r2 step plan 為後續開工讀序 | 現在開 65 triage SQL／報告 |
| Step 0 繼續唯讀監看至 run22 終態 | 搶 `heavy_slot`／手動發 TWEVO／`--allow-apply` |
| 結輪後再開 Step 1（P0-A） | 本裁＝結輪後自動開工（仍須另啟動） |
| FZ-keep／GATE-keep／M-T5-watch | 解凍 FinMind／FRED；降閘；代簽 |

## 硬禁（本波）

- 不跑 morning（輪未結假綠）  
- 不搶 slot  
- 不開 65 triage SQL 報告  
- 不 move 既有 archive tag

## 下一步（機械提醒）

1. 守 Step 0 至 run22／I5B 收口；結輪後 `--morning --write-audit`。  
2. **結輪後**再開 Step 1（65 triage 唯讀）。  
3. 舊 step 讀序只當史料；操作改本檔。

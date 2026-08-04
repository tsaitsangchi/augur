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
| 結輪後再開 Step 1（P0-A） | 本裁本身≠自動開工 triage；**喚醒＝auto**（見下） |
| FZ-keep／GATE-keep／M-T5-watch | 解凍 FinMind／FRED；降閘；代簽 |


## Step1 喚醒（Steward 補裁 · 2026-08-04）

- **Step1 喚醒＝auto**：背景監看觀察 `run22` **succeeded**／morning 五驗收可結 → **ping**（寫 sentinel＋stdout 標記）。
- **≠** 自動開 65 triage、**≠** 自動 `--morning --write-audit`（收口仍屬 Step0；ready 時僅建議用戶指令）。
- 監看掛載細節見本檔「監看已掛」段／sentinel。

## 硬禁（本波）

- 不跑 morning（輪未結假綠）  
- 不搶 slot  
- 不開 65 triage SQL 報告  
- 不 move 既有 archive tag

## 下一步（機械提醒）

1. 守 Step 0 至 run22／I5B 收口；結輪後由人／提醒後 `--morning --write-audit`（**監看預設不代寫**）。  
2. **Step1 喚醒＝auto**：ready sentinel → ping；**不**自動開 65 triage。  
3. 舊 step 讀序只當史料；操作改本檔。

## 補記（甲案開工 · 2026-08-04）

> Steward 明示選 **甲**：`OPT-P0-20260804-go + TRIAGE-65-go + FZ/GATE/NHC-keep`。  
> 效力＝在 ready sentinel 已成立前提下，**正式開工** Step0 morning 收口＋Step1 65 唯讀 triage。  
> 執行／驗收帳＝`audits/OPT-P0-TRIAGE65-20260804.md`（不廢本檔原裁；本節＝後續擴權留痕）。

## 監看已掛（Step1 喚醒＝auto · 2026-08-04 01:21:21+0800）

| 項 | 值 |
|---|---|
| 指令 | `nohup /home/hugo/project/augur/scripts/watch_run22_step1_ready.sh >> /home/hugo/logs/run22_step1_watch_20260804.log 2>&1 &` |
| pid | `302776` |
| log | `/home/hugo/logs/run22_step1_watch_20260804.log` |
| 腳本 | `scripts/watch_run22_step1_ready.sh` |
| 間隔 | 240s（4 分） |
| 超時 | 28800s（8h）→ `audits/RUN22-WATCH-TIMEOUT-20260804.md` |
| ready sentinel | `audits/RUN22-READY-FOR-STEP1-20260804.md` |
| 行為 | 唯讀 probe `evolution_run`＋`observe_twevo_run22.py --morning`（**無** `--write-audit`）；不搶 slot；不開 triage |

**判定條件（滿任一即 ping）**：
1. `observe --morning` rc=0（I5B／morning 五驗收可結），或  
2. `latest run_id=22 && status=succeeded`（最小條件）

ready 時 stdout 印 `STEP1_READY run22 succeeded` 並寫 sentinel；**不**自動開 65 triage、**不**代寫 morning audit。


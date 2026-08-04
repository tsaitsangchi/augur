# GO｜LOOP-S4-TO-S5 + LOOP-S5-TO-S4-OPT + LOOP-FULL-CHAIN · 2026-08-04

> **位階**：[I] 授權留痕（非 META [N]）  
> **Steward message（要旨）**：`OOP-S4-TO-S5-go`（typo→**LOOP-S4-TO-S5-go**）／`LOOP-S5-TO-S4-OPT-go`／`LOOP-FULL-CHAIN-go`；並 ack `S4-WAVE-A`  
> **時點**：2026-08-04 ≈13:30+08:00  
> **SSOT**：`reports/augur_s4_s5_closed_loop_plan_20260804.md` · parent `reports/augur_local_ai_predict_sim_self_evolve_opt_plan_20260804.md` §0.7–0.8／§7.2d  
> **self-reported（#32a）**

---

## 1. 消費之 GO（三連＋旗標）

| 句 | 效力 |
|---|---|
| **LOOP-S4-TO-S5-go** | 正向 C2：對**可引用** S4 artifact 跑 S5 方向／漲跌比 OOS（dry／唯讀） |
| **LOOP-S5-TO-S4-OPT-go** | 回饋 C2：有 S5 分數後寫再訓／再驗 backlog；**不**默授 APPLY／全 taxonomy 重訓 |
| **LOOP-FULL-CHAIN-go** | 採納 C0 地圖（C1∪C2）；**仍**逐段 GO；**≠**一鍵 S1–S5 重建／寫庫 |
| **S4-WAVE-A**（已授權／in flight） | **不重啟**；與 `/tmp/s4-wave-a-20260804` 協調；落地待 `S4-WAVE-A-EXECUTED*` |

**Default keep（省略＝此列）**：`GATE-keep` + `NHC-keep` + `API-THAW-bounded` + `no-SIM-apply` + `skip-sync`

---

## 2. 硬邊界（本 GO 不鬆）

| 禁 | 允 |
|---|---|
| 重啟／kill Wave A 訓練矩陣 | 讀 Wave A log／已落地 artifact |
| kill A1 `daily_maintenance` | 錯峰；不疊放量 sync |
| `prediction_values` 寫（無 `predict-asof-write-go`） | `predict_asof --dry-run` |
| sim `--apply` | sim 旁軸尺分離 |
| 假確立級／改 `direction_gate` | dgate **唯讀**；pass=0 誠實 |
| 放量 FinMind／FRED／Dividend rebuild | 庫內 as-of；`--skip-sync` |
| 一次默授全鏈 ingest+build+train+predict 寫 | 各段各自 GO |

---

## 3. WAVE-A 協調（執行當下快照）

| 項 | 值 |
|---|---|
| 日誌根 | `/tmp/s4-wave-a-20260804/`（`train-matrix.log`） |
| 啟動 | 2026-08-04T13:25:25+08:00 · ASOF=`2026-06-30` |
| A1 | pid **877790／877801** 仍跑——**不殺** |
| 已就緒（本 GO 可引用） | RankRidge H40／H120（新）；H20／H60 resume-skip（P1-C）；RankGBDT H60×seed1/2/42；RankGBDT H20×seed1 |
| train-matrix | **DONE** 2026-08-04T13:30:30+08:00（RankRidge H40/H120＋RankGBDT H20/H60×3seed；**不含** direction 臂） |
| EXECUTED audit | **尚無** `audits/S4-WAVE-A-EXECUTED*`（本 LOOP **不**代寫）→ S5 消費 P1-C＋train 已落地 artifact；方向臂／正式 Wave 收口另帳 |

---

## 4. 執行順序（本窗）

1. 本檔 GO 登錄  
2. **LOOP-FULL-CHAIN-go**：parent／C2 計畫 status→C0 **地圖授權**（docs only；零瞬間全鏈重建）  
3. **LOOP-S4-TO-S5-go**：S5 dry-run＋OOS 漲跌比／勝率（可用 artifact）→ `audits/LOOP-S4-TO-S5-EXECUTED-20260804.md`／`audits/S5-OOS-20260804.md`  
4. **LOOP-S5-TO-S4-OPT-go**：分數齊後寫最小安全 opt／backlog → `audits/LOOP-S5-TO-S4-OPT-EXECUTED-20260804.md`（Wave A 未完則標 **partial／STOP+backlog**）  
5. 更新 `audits/S4-MODELS-TRIED-LIST-20260804.md`／閉環計畫 checkbox  

---

## 5. Paste-ready（已消費）

```text
LOOP-S4-TO-S5-go + LOOP-S5-TO-S4-OPT-go + LOOP-FULL-CHAIN-go
+ GATE-keep + NHC-keep + API-THAW-bounded + no-SIM-apply + skip-sync
+ S4-WAVE-A（ack in-flight；do-not-restart）
```

*完。*

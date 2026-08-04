# S4-WAVE-A 執行帳 [I]（2026-08-04）— PARTIAL→近滿 EXECUTED

> **位階**：[I] 執行留痕（非 META-CONSTITUTION [N]）。  
> **時點**：約 **2026-08-04 13:25–14:39+08**  
> **GO（Steward 原文）**：`S4-WAVE-A-go | FZ/GATE-keep | no-SIM-apply | skip-sync`  
> **前置**：`S4-FAMILIES-PLAN-go` EXECUTED（`audits/S4-FAMILIES-PLAN-GO-20260804.md`）  
> **SSOT**：`reports/augur_s4_market_model_families_opt_plan_20260804.md` Wave A  
> **as-of**：`2026-06-30`（DB `feature_values` max；庫內／skip-sync）  
> **logs**：`/tmp/s4-wave-a-20260804/`  
> **self-reported（#32a）**：數字出自 stdout／DB query；**≠**確立級／可交易／direction_gate pass／sim apply

## 約束遵守

| 約束 | 本窗 |
|---|---|
| skip-sync | **守**——零 FinMind／FRED fetch |
| no-SIM-apply | **守** |
| FZ/GATE-keep | **守**——未擴解凍；未降閘 |
| 不殺 A1 | **守**——`daily_maintenance` 全程並存；未疊第二支 maintenance |
| predict 寫庫／確立級 | **未做／未宣稱** |
| DB as-of only | **守** |

## Wave A 結果總表

| ID | 變體族 | 結果 | model_id／證據 | 關鍵 metrics（stdout／DB） |
|---|---|---|---|---|
| **A-4a** | RankRidge≡B2 | **PASS** | `RankRidge_H{20,40,60,120}_2026-06-30_seed42_56d03625463b3eba`（H20/H60 resume 跳過；H40/H120 新訓） | #14 top20%/equal **net Sharpe**：H60 **1.30**／H40 **1.14**／H120 **1.22** vs 基準 1.09／1.07／1.00 |
| **A-3a** | LightGBM／RankGBDT＋M1 | **PASS** | `RankGBDT_H{20,60}_2026-06-30_seed{1,2,42}_56d03625463b3eba`（6 artifact） | train OK；#14 M1 top20%/equal H60 net **1.09**≈基準；**#11 三 seed** top20% net Sharpe H60 min/med/max/mean＝**1.031／1.090／1.153／1.091**；H20＝**0.625／0.659／0.672／0.652**（皆＜基準 0.869）→ **不得**單 seed 勝出宣稱 |
| **A-D1** | DailyGBDT_cal | **PASS** | `train_daily_direction.py --run-v2 --ks 5 --seeds 3`；`daily_direction_oos_sample` | 寫 **3,626,103** 列（per-seed×3）；seed0/1/2 hit＝**0.5161／0.5149／0.5161**；pooled hit **0.5157** brier **0.2551**（DB；≠ gate pass） |
| **A-2a** | 線性／邏輯（partial） | **PASS（併 A-D1／A-4a）** | Daily 側走 v2 GBDT_cal；截面 Ridge＝A-4a | 同上；未另跑 v1 DailyLogit champion |
| **A-D2** | market／stack／threelens | **PASS** | `MktLogit_v2` H20；`DirStackM` H20；threelens H40 冒煙 | market：H20 folds=4189 P_mkt；stack：OOS 35356 列 p̄=0.516；threelens H40 OOS n=37736 hit=**0.5218** brier=0.2553（3-seed 平均；工程冒煙≠gate） |
| **A-B0／A-B1** | 地板 | **PARTIAL** | econ `基準(淨)` 對照臂 | 未另跑字面 `B0_random`／`B1_momentum` model 臂；基準淨 Sharpe 見上 |
| **A-4c** | 截面因子＋shrinkage | **PARTIAL** | 文件／B1 特徵側 | 不冒充新 model family PASS |
| A-3b XGB | missing | **SKIP** | — | 無 ranker adapter |
| A-3c CatBoost | missing | **SKIP** | — | 同上 |
| A-3d RF | missing | **SKIP** | — | 同上 |
| A-4b LTR | missing | **SKIP** | — | 同上 |
| A-2b SVM | missing | **SKIP** | — | 同上 |
| A-2c KNN | missing | **SKIP** | — | 同上 |
| A-2d NB | missing | **SKIP** | — | 同上 |
| A-2e 淺 MLP | missing | **SKIP** | — | 同上 |

## 最低完成定義對照

| # | 定義 | 本窗 |
|---|---|---|
| 1 | RankRidge × 多 horizon（含 H40／H120） | **滿足** |
| 2 | RankGBDT train ≥3 seed × 主 horizon＋#14 | **滿足**（train＋econ＋3-seed probe） |
| 3 | direction 至少一臂 v2 多 seed 數字 | **滿足**（A-D1＋A-D2） |
| 4 | missing 族 SKIP 列帳 | **滿足** |

## 阻塞／干擾（誠實）

| 項 | 說明 |
|---|---|
| A1 dual-watch／`daily_maintenance` | 全程並存 → DB IO 爭用；direction 特徵載入～55min 才出首行 fold |
| 初版 GBDT 3-seed inline | 嵌套 heredoc 引號 SyntaxError → 改 `/tmp/s4-wave-a-20260804/gbdt_3seed_probe.py` 重跑 **PASS** |
| threelens 無參冒煙 | 曾與 A1／econ 搶 `TaiwanStockPriceAdj`；後改 `--horizon 40` **PASS** |
| H20 全表 `run_economic_eval` | 本窗未重跑（耗時）；#11 H20 三 seed 已由 probe 覆蓋 |

## 硬禁未觸

- 無 sim `--apply`；無 FinMind／FRED；無 kill A1；無 predict 寫庫；無確立級／direction_gate evaluate 宣稱通過。

## 下一步（另句；本窗不自動開）

```text
S4-WAVE-B-go | FZ/GATE-keep | no-SIM-apply | skip-sync
```

殘餘可選：字面 B0／B1 臂；H20 全表 econ；missing adapter 實作另 GO；A-D1 → `evaluate_direction_gate`（人裁／另句）。

---

*完。[I] Wave A 近滿 EXECUTED（exists／partial 已驗；missing＝SKIP）。*

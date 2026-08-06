---
status: executed
series: s4_s5_verify
track: V5
date: 2026-08-06
viewpoint: 2026-08-06T16:45+08:00
go: audits/S5-OOS-VERIFY-GO-20260806.md
plan: reports/augur_s4_other_model_verify_matrix_plan_20260806.md
prior_oos: audits/S5-OOS-20260804.md
logs: /tmp/s5-oos-verify-20260806/
paste: "S5-OOS-VERIFY-go | FZ/GATE-keep | read-mostly | no-new-train | hold-#1"
layer: "[I]"
self_reported: true
---

# EXECUTED｜S5-OOS-VERIFY（V5 輕量）· 2026-08-06

> **一句**：不新訓；對既有 OOS／pp 表重算方向尺＋覆驗 dgate／econ_verdict；**禁**當成確立級或可交易。  
> **#1**：PriceAdj 頂仍 **2026-08-05**；watcher 續候 **08-06**（本窗未搶 B3）。

---

## 0. 邊界（已守）

| 項 | 結果 |
|---|---|
| 新訓／`run_economic_eval` 重跑 | **未做**（CPU 重→屬 V1；本刀 read-mostly） |
| sim `--apply`／寫 predict | **未做** |
| NF-pause | **未撤** |
| dgate 寫入 | **未做**（唯讀） |

---

## 1. LIVE 錨

| 鍵 | 值 |
|---|---|
| `TaiwanStockPriceAdj` max | **2026-08-05** |
| `prediction_probability` max panel | **2026-08-05**（3890 列跨 H） |
| `prediction_values` max panel | **2026-08-05**（4793） |
| `direction_gate.evaluated_pass` | **0**（approved 11／fail 12／superseded 6） |

→ **禁假確立級**（與 08-04 S5-OOS 同結論）。

---

## 2. 投資組合尺（引用·不重跑）

SSOT 仍為 `audits/S5-OOS-20260804.md`（B2_ridge≡RankRidge · top20% · cost=0.00585 · until=2026-06-30）：

| H | n | net hit | bench hit | net Sharpe | 方向註 |
|---|---|---|---|---|---|
| 20 | 61 | **0.639** | 0.623 | 1.17 | folds 偏正 |
| 60 | 19 | **0.632** | 0.579 | **1.30** | 主尺 |
| 40 | 30 | 0.567 | **0.633** | 1.14 | **劣 bench** |
| 120 | 8 | 0.875 | 0.750 | 1.22 | **n 不足** |

本窗**未**重算 panel hash／net Sharpe（避免∥候 A 時重訓型 walk-forward）。

---

## 3. 方向／漲跌比 · 庫內重算（本窗產出）

### 3a `direction_oos_sample`（p_up≥0.5 vs y_up）

| H | model | hit | n | panels |
|---|---|---|---|---|
| 20 | DirStackM | 0.517 | 35356 | 84 |
| 20 | DirStack | 0.548 | 6188 | 16 |
| 20 | DirStack_RankSVM | 0.504 | 28535 | 90 |
| 40 | DirStackM | 0.514 | 34502 | 82 |
| 40 | DirStack | 0.604 | 6186 | 16 |
| 82 | DirStackM | 0.542 | 32476 | 77 |
| 82 | DirStack | 0.571 | 5753 | 15 |
| 120 | DirStack | 0.566 | 4994 | 13 |

DirStackM H20 **panel-mean** hit≈0.516；folds early／mid／late≈ **0.520／0.527／0.501**（無單 fold 當終局）。  
**無 H60 DirStack*** 列（庫內誠實空）。

### 3b `daily_direction_oos_sample`

| k | model | seed | hit | brier | n |
|---|---|---|---|---|---|
| 1 | DailyLogit | 0 | 0.552 | 0.247 | ~1.21e6 |
| 5 | DailyGBDT | 0 | 0.519 | 0.254 | ~1.21e6 |
| 5 | DailyGBDT_cal | 0／1／2 | 0.515–0.516 | ≈0.255 | ~1.21e6×3 |

→ 日頻方向弱於「可交易確立」；**#11 多 seed 一致、無單 seed 勝謊**。

### 3c `probability_oos_sample` RankRidge top20%（panel 平均個股 up-rate；**≠** §2 投組 period hit）

| H | n_panel | top20% up-rate | univ up-rate | note |
|---|---|---|---|---|
| 20 | 104 | 0.567 | 0.510 | 尺≠§2 |
| 40 | 103 | 0.604 | 0.531 | 與§2 H40 警示**不可互消** |
| 60 | 102 | 0.633 | 0.541 | 數近§2 net hit，**定義仍異** |
| 120 | 98 | 0.671 | 0.574 | 勿與§2 n=8 混讀 |

---

## 4. `prediction_probability.econ_verdict`（最新至 08-05）

| H | verdict | @08-05 model |
|---|---|---|
| **20** | **dead** | RankRidge_H20_…56d036… |
| 40／60／82／120 | thin_unestablished | 同族 seed42 artifact |

→ H20 **econ=dead** 與深解讀一貫；**不得**用 predict 列假關確立級。

---

## 5. 對帳結論（誠實）

1. **dgate pass=0** 覆驗成立 → S5 驗証 ≠ 確立級。  
2. §2 投組尺仍以 **08-04 OOS 帳**為準；本窗補 **方向 OOS／日頻／econ_verdict** 活證。  
3. 方向 hit 多落 **≈0.50–0.55**（DirStackM）／日頻 **≈0.51–0.55** → 有弱信号、**無**升格理由。  
4. H40 投組 hit 劣 bench（§2）警告**仍有效**；未因 3c top20% 好看而改寫。  
5. **未**開新族、**未**撤 NF、**未**假 B3。

---

## 6. 路徑

- GO：`audits/S5-OOS-VERIFY-GO-20260806.md`  
- 本帳：`audits/S5-OOS-VERIFY-EXECUTED-20260806.md`  
- 前帳：`audits/S5-OOS-20260804.md`  
- log：`/tmp/s5-oos-verify-20260806/`

---

## 7. 建議下一句（非本窗）

| 若… | 貼 |
|---|---|
| A 到後重跑投組／多 seed | `S4-V1-REVERIFY-go` |
| S5→S4 回饋弧 | `LOOP-S5-TO-S4-OPT-run` |
| 新族 | 先 `NF-*-go-plan` 撤 pause |

*完。[I] executed；self-reported。*

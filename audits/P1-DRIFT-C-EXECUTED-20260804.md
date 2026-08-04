# P1-DRIFT C（retrain-asof／多 horizon＋經濟終關）執行帳 · 2026-08-04

> **位階**：[I] 執行留痕（非 META [N]）。  
> **授權**：Steward `P1-DRIFT: C-go`（多 horizon／經濟終關）。  
> **前序**：A＝`audits/P1-DRIFT-A-EXECUTED-20260804.md`（H60 prodset 已綠）。  
> **呈案**：`reports/augur_p1_feature_drift_plan_20260804.md` §2 C／§6 殘列。  
> **護欄**：`FZ/GATE-keep` · `no-SIM-apply` · `skip-sync`；零 FinMind／FRED；未寫 `prediction_values`；≠可交易／確立級。

---

## 1. 範圍（依計畫／主戰場，非自創）

| 項 | 取捨 |
|---|---|
| horizon | **H20＋H60**（`train_ranker` 主戰場 20/60；SIGN active3 同窗；H60 已由 A 重產） |
| 未做 horizon | H40／H120（非主戰場；H252 禁入） |
| 特徵 | 現行 active 三顆＝`cycle_position_252d` · `inst_cumflow_position_120d` · `lending_fee_rate_mean_30d` |
| 經濟終關 | `run_economic_eval.py --feature-source=prodset --until 2026-06-30`（walk-forward；非寫庫 predict） |
| 寫庫／SIM | **未做**（dry-run only；`predict-asof-write-go`／`SIM-FIRST-CELL-go` 另層） |

腳本小補：`scripts/run_economic_eval.py` 增 `--feature-source={canonical,prodset}`（預設 canonical 不變）＋`--seed`（傳入 GBDT）。

---

## 2. 多 horizon 重產／對齊

| H | 指令 | 結果 |
|---|---|---|
| 20 | `python scripts/train_ranker.py --run --horizon 20 --family RankRidge --seed 42 --resume` | **新產** rc=0 |
| 60 | 同上 `--horizon 60 --resume` | **跳過**（A 已登錄同 model_id） |

| 項 | H20 | H60 |
|---|---|---|
| model_id | `RankRidge_H20_2026-06-30_seed42_56d03625463b3eba` | `RankRidge_H60_2026-06-30_seed42_56d03625463b3eba` |
| feature_source | prodset | prodset |
| frozen feats | 上列三顆 | 上列三顆 |
| n_feats／n_train_rows／panels | 3／42738／113 | 3／42255／113（A 帳） |
| panels 窗 | `[2007-12-31..2026-06-30]` | 同 |
| artifact | `models_artifacts/RankRidge_H20_2026-06-30_seed42_56d03625463b3eba.joblib` | （A 既有） |

---

## 3. Dry-run 驗收（未寫庫）

| 指令 | 結果要旨 |
|---|---|
| `predict_asof.py --run --dry-run --horizon 20` | ✓ as-of 2026-06-30 model=H20… feature_source=prodset n_feats=3（dry-run 未寫庫） |
| `predict_asof.py --run --dry-run --horizon 60` | ✓ 同；model=H60… |

frozen＝current active：**是**（兩 H）。**未**寫 `prediction_values`。

---

## 4. 經濟終關（#9／#10＝程式 stdout）

共用：`--since 2021-01-01 --until 2026-06-30 --feature-source=prodset --cost 0.00585`；feats＝active 三顆。

### 4.1 H60（panel hash=`ca1b6ff379`；22 非重疊 panel；19 期／4.22 per-yr）

**B2_ridge**（確定性；對齊生產 RankRidge 族）— log=`/tmp/p1-drift-c-econ-h60.log`

| 組態 | 換手 | net CAGR | net Sharpe | net MaxDD | net Calmar | 勝率 |
|---|---|---|---|---|---|---|
| top10%/equal | 55% | +29.9% | 1.03 | −16.2% | 1.84 | 58% |
| top10%/pred | 59% | +33.6% | 1.03 | −14.6% | 2.29 | 63% |
| **top20%/equal** | **47%** | **+26.6%** | **1.30** | **−9.2%** | **2.88** | **63%** |
| top20%/pred | 50% | +29.4% | 1.17 | −10.7% | 2.76 | 63% |
| top30%/equal | 39% | +25.3% | 1.25 | −9.8% | 2.57 | 63% |
| top30%/pred | 44% | +27.6% | 1.24 | −10.3% | 2.69 | 63% |
| **基準(淨)** | 13% | +17.6% | **1.09** | −14.7% | 1.20 | 58% |

→ Ridge top20%/equal **net Sharpe 1.30＞基準 1.09**；Calmar 2.88＞1.20（同尺 stdout）。

**M1_gbdt** seed=42 全表見同 log。top20%/equal net Sharpe **1.09＝基準 1.09**（無明顯邊際）。

**GBDT 3-seed**（#11；僅 top20%/equal net Sharpe；log=`/tmp/p1-drift-c-gbdt-seeds-h60.log`）：

| seed | net Sharpe | net CAGR | net Calmar | bench net Sharpe |
|---|---|---|---|---|
| 1 | 1.1525 | +21.94% | 1.5914 | 1.0938 |
| 2 | 1.0310 | +18.54% | 1.1139 | 1.0938 |
| 42 | 1.0896 | +19.41% | 1.4990 | 1.0938 |
| **min／median／max／mean** | **1.0310／1.0896／1.1525／1.0910** | — | — | — |

→ GBDT 中位≈基準；**不得**以單 seed 宣稱挑戰者勝出。生產熱路徑仍為 RankRidge。

### 4.2 H20（panel hash=`26e4c2daaa`；66 非重疊 panel；61 期／12.19 per-yr）

log=`/tmp/p1-drift-c-econ-h20.log` · seed=42

**B2_ridge**

| 組態 | 換手 | net CAGR | net Sharpe | net MaxDD | net Calmar | 勝率 |
|---|---|---|---|---|---|---|
| top10%/equal | 39% | +24.4% | 1.27 | −14.1% | 1.73 | 64% |
| top10%/pred | 43% | +24.0% | 1.18 | −16.9% | 1.42 | 64% |
| **top20%/equal** | **32%** | **+19.9%** | **1.17** | **−13.2%** | **1.50** | **64%** |
| top20%/pred | 35% | +22.2% | 1.23 | −13.6% | 1.63 | 61% |
| top30%/equal | 25% | +19.6% | 1.18 | −13.6% | 1.44 | 62% |
| top30%/pred | 29% | +21.2% | 1.22 | −13.6% | 1.56 | 64% |
| **基準(淨)** | 7% | +13.1% | **0.87** | −13.4% | 0.98 | 62% |

→ Ridge 各 top 分位 net Sharpe／Calmar **皆優於基準**（stdout）。

**M1_gbdt**（單 seed=42；H20 未另跑 3-seed——GBDT 非生產族、且 net 已低於基準）：

| 組態 | net Sharpe | vs 基準 0.87 |
|---|---|---|
| top10%/equal | 0.69 | 劣 |
| top20%/equal | 0.66 | 劣 |
| top30%/equal | 0.76 | 劣 |

→ H20 上 GBDT **未過**經濟尺（成本吃掉邊際）；誠實留檔。

---

## 5. 誠實邊界（必讀）

| 宣稱 | 本輪 |
|---|---|
| prodset H20／H60 artifact 對齊＋dry-run | **綠** |
| 經濟尺（Ridge walk-forward net＞基準）H20／H60 | **數字成立（stdout）** |
| 可交易／確立級 | **未宣稱**（無 `direction_gate`／無人裁晉升） |
| 寫 `prediction_values`／SIM `--apply` | **未做** |
| FinMind／FRED／Registry COMMIT／git commit | **未做** |

腳本判讀句「真可交易」＝方法論用語；**本 audit 不把該句升格為確立級**。

---

## 6. 殘餘

| 項 | 狀態 |
|---|---|
| H40／H120 prodset 重產 | 未做 |
| H20 GBDT ≥3 seed | 未做（GBDT 已單 seed 劣於基準；優先序低） |
| B canonical-arm | 未授權 |
| predict 寫庫／SIM apply | 須另句 |
| direction_gate／確立級 | 另層 |

---

## 7. 產物路徑

| 類 | 路徑 |
|---|---|
| train H20 | `/tmp/p1-drift-c-train-h20.log` |
| dry H20／H60 | `/tmp/p1-drift-c-dry-h20.log` · `/tmp/p1-drift-c-dry-h60.log` |
| econ H60／H20 | `/tmp/p1-drift-c-econ-h60.log` · `/tmp/p1-drift-c-econ-h20.log` |
| GBDT 3-seed H60 | `/tmp/p1-drift-c-gbdt-seeds-h60.log` |
| code | `scripts/run_economic_eval.py`（`--feature-source`／`--seed`） |

*完。*

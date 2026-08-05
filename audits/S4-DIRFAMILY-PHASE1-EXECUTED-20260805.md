---
status: executed
series: s4_model_families
depends_on:
  - reports/augur_s4_dirfamily_generalize_plan_20260804.md
  - audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md
  - audits/S4-DIRFAMILY-GENERALIZE-EXECUTED-20260804.md
---

# S4-DIRFAMILY Phase 1 — RankSVM@H20 → DirStack 研究比較（2026-08-05）EXECUTED

> **性質**：[I] 執行留痕。Steward 已授權 Phase 1（步驟 1–4）。  
> **硬邊界**：不掛 GATE／不改 criteria／不自動升格；僅 H20。  
> **self-reported（#32a）**：數字＝(a) stdout／(b) DB。

## 1. 步驟結果

| 步 | 動作 | 結果 |
|---|---|---|
| 1 | `build_probability_oos_sample --model-family RankSVM --horizon 20` | ✓ 101 折／34,388 列（2016-12-31..2026-03-31）；exit 0 |
| 2 | `train_direction_stack` `--model-family`＋`DirStack_<family>` | ✓ 先前已完成（本輪沿用） |
| 3 | `--run --horizons 20 --model-family RankSVM` | ✓ `DirStack_RankSVM` H20＝28,535 列／90 panel |
| 4 | 對齊 panel 研究比較（非 `evaluate_direction_gate`） | ✓ 見下 |

**未跑**：`calibrate_relative_probability --model-family RankSVM`（計畫已註：DirStack 不讀 calibrator）。

## 2. 研究比較（對齊 16 共同 panel × 4,034 股-日）

> 可比窗＝既有 `DirStack`（RankRidge 相對分量）有列之 panel；`DirStack_RankSVM` 面板更密（90），**不得**用全量列數直接比勝負。

| model_id | n | Brier↓ | hit↑ | AUC↑ |
|---|---|---|---|---|
| `DirStack` | 4034 | **0.24606** | **0.5461** | **0.5619** |
| `DirStack_RankSVM` | 4034 | 0.24678 | 0.5305 | 0.5299 |
| Δ(SVM−Dir) | | +0.00072 | −0.0156 | −0.0320 |

**判定**：在對齊窗上，`DirStack_RankSVM` **未優於**既有 `DirStack`（三指標皆略差或持平偏劣）。  
**與 Wave-A 不矛盾**：`RankSVM@H20` 贏的是**截面經濟尺**（net Sharpe）；DirStack 吃的是相對分位＋市場分量之**方向合成**——兩題不同，單點真贏不保證 stack 變好。

## 3. 硬邊界遵守

- 零 `direction_gate_criteria` 新列；零 FinMind／FRED；零 sim。  
- 既有 `DirStack`／`RankRidge` 列未覆蓋。  
- **不晉升**／不改 `predict_asof` 預設族。

## 4. 結論與下一手

Phase 1 **研究比較收口：DirStack 變體未贏**——誠實記帳，止步。可選後續（另句）：刪研究列、或換特徵集後重驗 RankSVM 截面、或他族——**皆非本帳自動觸發**。

---

*完。EXECUTED＝步驟 1–4；變體未過研究比較門。self-reported（#32a）。*

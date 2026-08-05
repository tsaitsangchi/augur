# RankEnsemble(ENS_ridge_gbdt) Phase 0 評測執行帳 [I]（2026-08-04）— EXECUTED（誠實未過門）

> **位階**：[I] 執行留痕（非 META-CONSTITUTION [N]）。
> **GO**：Steward 對話拍板「Phase 0（評測）」（`reports/augur_s4_rank_ensemble_blend_plan_20260804.md`）。
> **SSOT**：同上計畫書 §1／§3 Phase 0。
> **as-of**：`until=2026-06-30`（庫內 as-of，skip-sync）。
> **logs**：`/tmp/rank-ensemble-3seed-h60.log`、`/tmp/rank-ensemble-3seed-h20.log`。
> **self-reported（#32a）**：數字出自 stdout（(a)）；判讀為 AI 呈案。

---

## 1. 約束遵守

| 約束 | 本窗 |
|---|---|
| skip-sync | **守**——零 FinMind／FRED |
| no-SIM-apply | **守** |
| FZ/GATE-keep | **守** |
| 零 registry 寫入（Phase 0 定義） | **守**——僅呼叫既有 `portfolio.run_backtest`，未觸 `model_registry`／artifact |
| 預凍對照臂（CLAUDE #32b） | **守**——門檻於計畫書內**先**寫定（3-seed min 須真勝冠軍），後才跑值，非事後找理由 |

---

## 2. 產品碼變動（Phase 0 範圍內、唯一改動）

| 檔 | 變動 | 效果 |
|---|---|---|
| `scripts/run_economic_eval.py` | `for model in ("B2_ridge", "M1_gbdt")` → 加入 `"ENS_ridge_gbdt"` | 既有經濟評測 CLI 起自動含 ensemble 分支（供未來任何人重跑對照，工具永久留存、不因本次未過門而撤回） |

`ReadLints`：無新增 lint。`git diff` 範圍＝上表 1 行，符合計畫書 §3 表列。

---

## 3. 3-seed 探針結果（top20%/equal、cost=0.585%、prodset、until=2026-06-30）

### H60（panel hash `ca1b6ff379`，與冠軍評測**同一 panel 集**，22 panels）

| seed | net Sharpe | net hit | net CAGR | net Calmar |
|---|---|---|---|---|
| 1 | 1.1641 | 0.6316 | +27.77% | 2.8718 |
| 2 | 1.2567 | 0.6842 | +24.96% | 2.0835 |
| 42 | 1.2454 | 0.6842 | +25.63% | 2.5251 |
| **min／median／max／mean** | **1.1641／1.2454／1.2567／1.2220** | 0.6316／0.6842／0.6842／0.6667 | — | — |

**冠軍對照** `RankRidge_H60`：net Sharpe **1.3016**、net hit **0.6316**（`audits/S5-OOS-20260804.md`，同 panel hash）。

### H20（panel hash `26e4c2daaa`，與冠軍評測**同一 panel 集**，66 panels）

| seed | net Sharpe | net hit | net CAGR | net Calmar |
|---|---|---|---|---|
| 1 | 1.0054 | 0.6066 | +16.42% | 1.0903 |
| 2 | 1.1225 | 0.6230 | +18.44% | 1.3727 |
| 42 | 1.1312 | 0.6066 | +19.18% | 1.4813 |
| **min／median／max／mean** | **1.0054／1.1225／1.1312／1.0863** | 0.6066／0.6066／0.6230／0.6120 | — | — |

**冠軍對照** `RankRidge_H20`：net Sharpe **1.1684**、net hit **0.6393**（同上）。

---

## 4. 對照計畫書 §1 驗收門檻（逐項判定）

| # | 門檻 | H60 實測 | 判定 | H20（非升格門檻，供參） |
|---|---|---|---|---|
| 1 | ensemble net Sharpe 3-seed **min > 1.3016** | min=1.1641 | **✗ 未過**（min 甚至低於冠軍**任一**表現、更低於冠軍點值） | min=1.0054 ＜ 冠軍 1.1684，同向未過 |
| 2 | ensemble net hit 3-seed **min > 0.6316** | min=0.6316（**打平、非嚴格大於**） | **✗ 未過**（嚴格不等式；即便寬鬆認定"持平"，Sharpe 已定生死） | min=0.6066 ＜ 冠軍 0.6393，同向未過 |
| 3 | 禁中位數／單 seed 宣稱勝出 | 中位數 1.2454、max 1.2567 亦**皆低於**冠軍 1.3016——**連寬鬆判準都過不了**，非僅嚴格判準未過 | n/a（無勝出可宣稱） | 同左 |
| 4 | H20 同框比較 | 見上表 | 非升格門檻，僅確認同向未過（非 H60 單一失利、兩 horizon 一致） | — |

**判定：Phase 0 gate 全數未過（1、2 項均否，且非邊緣未過——H60 三 seed 無一達冠軍水準）。**

---

## 5. 判讀（誠實；非事後找理由）

- **技術解讀**：`ENS_ridge_gbdt` 為**等權 rank-average**（無學習權重）。RankGBDT 本身在 H60 三 seed 已知落於 1.031–1.153（`S5-OOS-20260804.md`），明顯弱於 RankRidge 之 1.3016；等權平均一個強模型與一個較弱模型，數學上**傾向把結果拉向中間、而非取兩者之長**——本結果與此先驗一致，非意外。
- **與 RankGBDT 先例呼應**：`S4-REOPT-BACKLOG` 項4 判 RankGBDT「不挑戰生產」；本次 ensemble 未過門為**同一因果鏈的自然延伸**（弱模型無論單獨或等權併入，皆無法超車）。
- **非徒勞**：本次驗證**排除了一個看似合理但實證不成立的假設**（"混合兩個既有模型應該更穩健"）——這本身是誠實的新知識，且成本極低（1 行程式碼 + 兩次探針、零新依賴、零 registry 寫入）。

---

## 6. 決策（依計畫書 §5 分階段設計）

**Phase 0 gate 未過 → 依計畫書預先寫定之規則，止於此，不進 Phase 1**（不新增 `RankEnsemble` 類別、不掛 `train_ranker.py` FAMILIES、不寫 `model_registry`）。

**保留**：`run_economic_eval.py` 的 `ENS_ridge_gbdt` 分支掛載（本次唯一產品碼變動）予以保留——零成本、供未來換特徵集／換折法時可一鍵重探，不因本次未過門而回退。

**下一步（若要重啟此方向，需另立新假設，非重跑同一設計）**：等權 rank-average 已證偽；若未來想再嘗試模型融合，須換成**有學習權重**的合成器（如 `train_direction_stack.py` 那樣的 L2 元學習器，用 walk-forward 學到的權重而非固定等權）——但這已是不同的技術設計，需另一輪 plan-first，非本計畫書範圍內的延伸。

---

## 7. 硬禁未觸

零 FinMind／FRED；零 sim `--apply`；零 `direction_gate`／`model_registry` 寫入；零確立級／可交易宣稱。

---

*完。[I] Phase 0 EXECUTED——誠實未過門，不進 Phase 1。self-reported（#32a）。*

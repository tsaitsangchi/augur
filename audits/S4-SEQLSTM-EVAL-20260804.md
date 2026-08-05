# SeqLSTM Phase 0b 全量評測執行帳 [I]（2026-08-04）— EXECUTED（誠實未過門）

> **位階**：[I] 執行留痕（非 META-CONSTITUTION [N]）。
> **GO**：Steward 對話拍板「Phase 0b（全量評測，接受與 S3-Wave-B 驗證 CPU 競合）」（`reports/augur_s4_wave_c_lstm_adapter_plan_20260804.md` §4）。
> **前置**：Phase 0a 可行性煙測已判可行（`audits/S4-SEQLSTM-SMOKE-20260804.md`）。
> **as-of**：既有 H60 冠軍評測同一 panel 集（`baseline._asof_stocks` 歷史宇宙聯集），skip-sync。
> **log**：`/tmp/s4-wave-c-lstm-20260804/phase0b.log`（PID 1170255，`train_sequence_ranker.py --run --seeds 1,2,42`）。
> **self-reported（#32a）**：數字出自 stdout（(a)）；判讀為 AI 呈案。

---

## 1. 約束遵守

| 約束 | 本窗 |
|---|---|
| skip-sync | **守**——零 FinMind／FRED，全程僅讀 `TaiwanStockPriceAdj`／籌碼表／`core_universe_asof`（既有庫內資料） |
| no-SIM-apply | **守** |
| FZ/GATE-keep | **守** |
| 零 `model_registry`／`prediction_values` 寫入（Phase 0 定義） | **守**——僅呼叫 `train_sequence_ranker.py --run`（評測），未觸任何生產表 |
| 預凍對照臂（CLAUDE #32b） | **守**——門檻於計畫書內**先**寫定（3-seed min 須真勝冠軍 1.3016），後才跑值 |

---

## 2. 全量評測結果（19 折×3 seed，H60，window=60，318 股一次性面板抓取）

| seed | n_folds | gross Sharpe | gross hit | net Sharpe | net hit | net CAGR |
|---|---|---|---|---|---|---|
| 1 | 19 | 1.2560 | 0.6316 | 1.1311 | 0.5789 | +11.84% |
| 2 | 19 | 1.2551 | 0.6316 | 1.1649 | 0.5789 | +16.73% |
| 42 | 19 | 1.2585 | 0.5263 | 1.1517 | 0.5263 | +13.40% |
| **min／median／max／mean** | — | 1.2551／1.2560／1.2585／1.2565 | 0.5263／0.6316／0.6316／0.5965 | **1.1311／1.1517／1.1649／1.1493** | 0.5263／0.5789／0.5789／0.5614 | — |

**耗時**：一次性面板抓取 394.8s（318 股，全程僅一次）＋全量評測 2140.0s（19 折×3 seed）＝總計 ≈42.2 分鐘（優於 Phase 0a 估算之 ≈64.4 分鐘）。

**冠軍對照** `RankRidge_H60`：net Sharpe **1.3016**、net hit **0.6316**（`audits/S5-OOS-20260804.md`）。

---

## 3. 對照計畫書 §4「決策門檻」逐項判定

| # | 門檻 | 實測 | 判定 |
|---|---|---|---|
| 1 | 3-seed net Sharpe **min > 1.3016** | min=**1.1311** | **✗ 未過**（min 甚至低於冠軍 11.6%；三 seed 全數低於冠軍，非邊緣未過） |
| 2 | 禁中位數／單 seed 宣稱勝出 | median=1.1517、max=1.1649 | n/a（無勝出可宣稱——三 seed 皆低於 1.3016，連寬鬆判準都過不了） |
| 3（供參，非計畫明文之獨立 gate） | net hit 同向比較 | min=0.5263 ＜ 冠軍 0.6316 | 同向未過（非僅 Sharpe 單指標失利，hit rate 亦全數低於冠軍） |

**判定：Phase 0b gate 未過（三 seed net Sharpe 皆低於現任冠軍 1.3016，最高 1.1649 仍差 10.5%）。**

---

## 4. 判讀（誠實；非事後找理由）

- **三 seed 高度一致**（gross Sharpe 1.2551–1.2585，區間僅 0.0034；net Sharpe 1.1311–1.1649）——模型本身訓練穩定、非隨機噴發偶然贏/輸，此為**穩定地**輸給冠軍,非不穩定的邊緣結果。
- **策略本身仍正收益**（三 seed net CAGR 皆 +11.8%~+16.7%、net Sharpe 皆 >1.13）——SeqLSTM 並非「壞模型」，只是**未達比橫斷面 Ridge 更優**的門檻；冠軍 RankRidge 本身已是同宇宙同期驗證多年之強基準（`原則精華` H20-60 飽和定論脈絡）。
- **技術解讀**：本次 LSTM 僅用**27 個保留通道**（NaN 率 <30% 篩選,見 Phase 0a）、單層 `hidden_size=32`、CPU-only、無超參搜尋（單一組固定超參跑 3 seed）——這是「架構最小可行版」而非「已窮盡調優版」；未過門**不能**解讀為「序列 DL 對此問題無效」，只能誠實記錄「本次最小可行配置未過門」（#15 誠實記錄，非過度推論）。
- **與 RankEnsemble 先例呼應**：本日第二個「先評測、贏了才升格」設計誠實未過門（第一個是 `S4-RANKENSEMBLE-EVAL-20260804.md`）——兩次獨立驗證皆顯示：**橫斷面 Ridge 冠軍在本宇宙／本特徵集下之護城河比預期深**，非僅單一挑戰者偶然失利。

---

## 5. 決策（依計畫書 §4 分階段設計）

**Phase 0b gate 未過 → 依計畫書預先寫定之規則，止於此，不進 Phase 1**（不寫 `model_registry`、不改 `predict_asof.py`、不設計序列模型 as-of 推論介面）。

**保留**：`src/augur/models/sequence_ranker.py`（`SeqLSTM` class）＋`scripts/train_sequence_ranker.py`（評測 CLI）予以保留——零額外成本，供未來換超參／換通道集／換 horizon 時可重探，不因本次未過門而回退或刪除。

**下一步（若要重啟此方向，需另立新假設，非重跑同一設計）**：可能方向——(a) 超參搜尋（`hidden_size`/`epochs`/`lr` 網格）、(b) 換 horizon（H20 較短窗可能序列訊號更強）、(c) 換通道集（放寬 NaN 篩選門檻或改插補策略）——但這些皆屬**不同的技術設計**，須另一輪 plan-first 明示範圍,非本計畫書既定範圍內的延伸；本帳僅誠實記錄現況、不代為決定是否投入。

---

## 6. 硬禁未觸

零 FinMind／FRED；零 sim `--apply`；零 `direction_gate`／`model_registry` 寫入；零確立級／可交易宣稱；CPU-only 誠實揭露（本機無 GPU，全程 CPU 訓練，未宣稱更高規格）。

---

*完。[I] Phase 0b EXECUTED——誠實未過門，不進 Phase 1。self-reported（#32a）。*

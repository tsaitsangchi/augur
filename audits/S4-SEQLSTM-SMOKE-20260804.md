# S4-Wave-C SeqLSTM Phase 0a 可行性煙測 — EXECUTED（2026-08-04）

> **位階**：[I] 執行留痕（非 META-CONSTITUTION [N]）。
> **授權（exact）**：「授權 Phase 0a（可行性煙測），实測後回來回報是否可行」（2026-08-04）。
> **計畫 SSOT**：`reports/augur_s4_wave_c_lstm_adapter_plan_20260804.md` §4（Phase 0a 定義）。
> **範圍**：**僅**可行性煙測（單折、單 seed、量耗時）；**不**含 Phase 0b 全量評測、**不**含經濟門檻判定（3-seed net Sharpe vs 冠軍）——那是 Phase 0b 的問題,本輪不作答。
> **self-reported（#32a）**：時間數字出 (a) stdout 實測；零 DB 寫入、零 model_registry 登錄、零 FinMind/FRED。

---

## 1. 執行內容

新增兩個檔案（皆已過 `ReadLints`／`py_compile`／`--selftest` 紅綠驗證）：

| 檔 | 角色 |
|---|---|
| `src/augur/models/sequence_ranker.py` | `SeqLSTM` library（單層 LSTM+線性頭；train 統計凍結正規化，#8 防洩漏）；`--selftest` 10 項零 DB 斷言全綠（含 NaN 輸入、seed 可重現性、不同 seed 真的給不同輸出）。 |
| `scripts/train_sequence_ranker.py` | CLI 編排：一次性面板快取→資料驅動通道篩選→複用 `walkforward.splits`／`build_long_portfolio`／`portfolio._metrics`／`_turnover`（#12,同冠軍評測共用函式）。`--smoke`＝Phase 0a；`--run`＝Phase 0b（已寫好完整鏈式換手邏輯,本輪**未執行**,見 §5）。 |

零改動既有生產路徑（`train_ranker.py`／`predict_asof.py`／`ranker.py`／`portfolio.py`）。

---

## 2. 煙測設定與實測結果

```text
PYTHONPATH=src ./venv/bin/python scripts/train_sequence_ranker.py --smoke --seed 42
```

| 項 | 值 |
|---|---|
| 折選取 | 全量 19 折中的**最後一折**（train 樣本最多＝最壞情境）；`fold train`=19 panels、`test`=2026-04-30 |
| h／window | 60／60（同冠軍 RankRidge_H60 panel 集口徑） |
| 歷史 as-of 宇宙聯集 | 318 支股票 |
| **一次性面板抓取**（318 股） | **364.5s**（≈6.1 分鐘；此為全程僅付一次的成本,folds/seed 增加不重付） |
| 通道篩選（NaN 率 <30%） | 保留 27／排除 6（`block_share`／`holder_count`／`lending_fee`／`lending_volume`／`retail_pct`／`top_holders`——資料驅動排除,非硬編） |
| n_train／n_test／n_port | 6005／314／62 |
| build_xy／fit／predict | 14.4s／45.1s／0.1s |
| **單折重覆成本**（build_xy+fit+predict,不含一次性抓取） | **59.5s** |
| 單折 gross return（未扣成本,僅 1 期） | −0.0215（**非 Sharpe,煙測不代表完整 OOS,不作經濟判讀**） |
| **全量外推**（19 折×3 seed） | **≈3866s（≈64.4 分鐘）** |

---

## 3. Phase 0a 判定（比照計畫 §4 門檻,本輪修正為「單折重覆成本」以避免與一次性抓取混淆）

| 門檻 | 實測 | 判定 |
|---|---|---|
| 單折重覆成本 < 5 分鐘（300s） | 59.5s | ✓ 過 |
| 全量外推 < 2 小時（7200s） | 3866s | ✓ 過 |

**結論：可行**——CPU-only（本機無 GPU）足以支撐 19 折×3 seed 全量 walk-forward,估計總耗時 **≈65 分鐘**（不含已付清的一次性面板抓取 364.5s）。

### 3.1 一處與原計畫估算之差異（誠實記錄,不影響本輪判定）

計畫 §3.1 曾估「一次性抓取…估 ≤5 分鐘」（外推自 S3-Wave-D 225 股/3 窗長實測 262.6s）；本次 318 股單一窗長實測 364.5s（≈6.1 分鐘）,略高於估算。**此差異不影響 Phase 0a 可行性判定**（一次性成本與「單折重覆成本 <5 分鐘」門檻是兩件事,見計畫 §4 原文「只跑最後一折…實測一次 fit+predict 耗時」——門檻對象是 fit+predict,非一次性抓取）；本輪已在 `train_sequence_ranker.py` 的煙測輸出中明確拆開兩者,避免未來誤讀。

---

## 4. 通道排除之誠實記錄

排除 6 通道（`block_share`／`holder_count`／`lending_fee`／`lending_volume`／`retail_pct`／`top_holders`）NaN 率 ≥30%——與計畫 §3.2「資料驅動、非硬編」設計一致;**非**本次臨時決定,是 `_select_channels` 對「本折 test as-of」實際掃描之結果,若未來窗口/期別不同,保留/排除清單可能隨資料變動（設計如此,非 bug）。

---

## 5. 未做（本輪範圍外,誠實列帳）

- **Phase 0b 全量評測未執行**——`--run`（19 折×3 seed,估≈65 分鐘）已寫好完整程式碼（含鏈式換手成本,同 `run_backtest` 口徑）,但**未經授權不擅自跑**；等回報後由用戶裁示是否投入。
- **經濟門檻判定未做**——3-seed net Sharpe vs 冠軍 RankRidge_H60（1.3016）比較屬 Phase 0b 產出,本輪煙測之單折 gross return（−0.0215）**不得**被解讀為模型優劣訊號。
- **零 model_registry 登錄、零 `prediction_values` 寫入、零 FinMind/FRED**。

---

## 6. 建議下一步（呈用戶裁決,AI 不擅自決定）

Phase 0a 誠實判定「可行」——序列 DL（SeqLSTM）是 8 族缺 adapter 中**首個實測證實 CPU 可行**的候選（Wave B classical TS／Wave A 七族尚未動工;Wave D Transformer-TS 同序列窗契約但未寫 adapter;Wave E GCN/GAT 仍卡 `torch_geometric`/`dgl` 未裝之硬阻斷)。若授權 Phase 0b：

```text
PYTHONPATH=src ./venv/bin/python scripts/train_sequence_ranker.py --run --seeds 1,2,42
```

預估 ≈65 分鐘（背景執行,完成後依計畫 §4 決策門檻「3-seed net Sharpe min > 1.3016」誠實判定;中位數/單 seed 勝出不算數,承 #32b 預凍對照臂紀律、同 RankEnsemble 之驗收紀律)。

---

*完。Phase 0a EXECUTED——可行；Phase 0b 待另授。*

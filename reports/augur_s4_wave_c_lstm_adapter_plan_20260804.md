# S4-Wave-C 真 Adapter 計畫｜SeqLSTM（首個序列 DL 模型族）· 2026-08-04

> **性質**：[I] plan-first（CLAUDE #20——新模型族＋新資料管線接法，架構層決定）。
> **觸發**：Steward 選定「T4b：S4-Wave-C 真 LSTM adapter」為下一手（本檔 2026-08-04 對話拍板）。
> **前置 SSOT**：`audits/S4-WAVE-C-EXECUTED-20260804.md`（誠實 SKIP 普查，SKIP 理由＝「無 adapter；需 sequence panel builder」）、`audits/S3-WAVE-D-EXECUTED-20260804.md`（Phase 1 已建 `sequence.py`／`build_sequence_panel.py`，SKIP 之前提缺口已補）、`audits/S4-RANKENSEMBLE-EVAL-20260804.md`（同日姊妹計畫，示範「先評測、贏了才升格」之紀律）。
> **self-reported（#32a）**：本文為 AI 呈案；一切數字待 Phase 0/1 實跑後以 stdout 為準。

---

## 0. 一句話

**S4-Wave-C 被 SKIP 的唯一理由（`torch 在場≠已接 adapter；無 sequence panel builder`）已在同日稍早被 S3-Wave-D 補上——本計畫把這個「契約已解除、adapter 仍未寫」的斷點真正接通：用既有序列窗張量（`features.sequence`）餵一個小型 LSTM，走與其他模型完全相同的 walk-forward／經濟評測紀律，只有真贏過現任冠軍才寫入 `model_registry`。**

---

## 1. 為何是這把、為何現在可行（背景查證）

| 前提 | 狀態 | 來源 |
|---|---|---|
| PyTorch 是否可用 | **`torch 2.4.1+cu121` 已裝**（本機**無 GPU**，CPU-only） | `torch.cuda.is_available()==False`（本輪查證） |
| 序列窗資料管線 | **已建**：`src/augur/features/sequence.py`（`stack_windows`／`build_sequence_tensor`）＋`scripts/build_sequence_panel.py` | `audits/S3-WAVE-D-EXECUTED-20260804.md` §2 |
| 覆蓋率 | 225 核心股於 window∈{20,60,120} **100% 足窗**；33 通道，少數籌碼通道 NaN 率高（78-96%） | 同上 §2.4 |
| 資料抓取成本 | 225 股一次性 `build_stock_panel` 抓取（每股 ~31 條 SQL）＝**262.6 秒**；**與 window_len／as-of 數量無關**（`stack_windows` 之後為純記憶體運算，零 DB） | 同上 §2.5；本計畫關鍵設計依據見 §3.1 |
| 既有排序模型冠軍 | `RankRidge_H60`：net Sharpe **1.3016**、net hit **0.6316**（22 panels，2021-01-01+） | `audits/S5-OOS-20260804.md` |

**與 RankEnsemble 之關係**：兩者皆為「先評測、贏了才升格」設計；差異在於 RankEnsemble 是**零新資料管線**（純組合既有輸出），SeqLSTM 是**首次真正消費**一條全新資料型態（日頻序列張量,非月頻 canonical 特徵）——工程量與風險皆較高，故拆更細的 phase gate。

---

## 2. 核心架構問題（先想清楚，避免中途卡關）

`train_ranker.py`／`predict_asof.py` 之泛化機制（`FAMILIES` dict＋`registry.latest`＋`artifact.load`）**建立在 2D 表格特徵（`feature_values`，月頻）之上**（`baseline._fold_xy`／`baseline._panel_matrix` 皆硬編此資料源）。序列張量是**3D、日頻、不同 raw 源**（`TaiwanStockPriceAdj`＋籌碼表，經 `build_stock_panel`）——**兩種資料管線不相容,不可直接塞進既有 FAMILIES**。

**決定（比照既有先例）**：`train_direction_stack.py` 早有相同情境（DirStack 資料管線與 `train_ranker.py` 不同源）,採**獨立腳本＋獨立走 `walkforward.splits`**、不硬塞泛化機制。本計畫比照此先例：
- 新增**獨立**函式庫模組 `src/augur/models/sequence_ranker.py`（非塞進 `ranker.py`——資料型態不同,#18 領域命名）。
- 新增**獨立**評測腳本 `scripts/train_sequence_ranker.py`（非改 `train_ranker.py`）。
- **複用**（#12 鐵律）：`walkforward.splits`（折切分）、`label_mod.labels`（rank 標籤,0-1)、`portfolio.build_long_portfolio`（選股)、`portfolio._metrics`／`_turnover`／`drawdown_series`（指標）、`baseline._asof_stocks`（歷史 as-of 宇宙)、`features.sequence.stack_windows`（張量 reshape)、`audit.field_correlation.build_stock_panel`（逐股日頻面板)。
- Phase 0/1（本 GO 範圍）**不**寫 `model_registry`、**不**改 `predict_asof.py`——僅評測。正式接生產出單（Phase 2）**另句**,比照計畫書慣例。

---

## 3. (b) 對應 python 程式規劃

### 3.1 一次性面板快取（效能命門，直接決定本計畫是否可行）

**問題**：`build_sequence_tensor` 每次呼叫皆重新對每股跑 `build_stock_panel`（31 條 SQL/股）。Walk-forward 需對**每折的每個歷史 as-of 訓練面板**取序列窗——若天真逐 as-of 呼叫,將重複抓取相同股票之相同歷史資料 N 次(N=折數)。

**解法**（`stack_windows` 本身是純函式,零 DB——見 `sequence.py:31`）：
1. 先用 `baseline._asof_stocks` 對「本次實驗會用到的所有 as-of 日期」（=H60 既有 22 個非重疊 panel,同 `audits/S5-OOS-20260804.md` panel hash `ca1b6ff379`）取歷史宇宙聯集。
2. 對聯集內**每支股票只呼叫一次** `build_stock_panel`（快取為 `dict[stock_id, DataFrame]`,存記憶體;可選存 pickle 供腳本中斷後 resume,比照 `--export .npz` 慣例)。
3. 之後對每個 as-of 日期、每一折,呼叫**零 DB 成本**的 `stack_windows(panels_cache, as_of_i, window_len=60, channels=kept_channels)` 取當期張量。

**預估成本**：一次性抓取（比照 S3-Wave-D 225 股實測 262.6 秒／3 窗長≈**單一窗長 ~90-100 秒**量級;股數若因歷史聯集略增,線性放大,估**≤5 分鐘**一次性成本、非重複發生)。

### 3.2 通道選擇（資料驅動,不硬編,比照 `sequence.py` 既有慣例）

- 對快取好的 panels,以**最新 as-of**算一次全通道 NaN 率(複用 `coverage_report` 既有函式)。
- **保留** NaN 率 < 30% 之通道（預期為價量／估值／技術類主幹通道)；**排除**過稀通道（籌碼結構類,如 `block_share`／`holder_count`,NaN 78-96%）。
- 腳本印出保留／排除清單（透明,非事後合理化)——若保留通道數過少(如<5),誠實中止並回報,不硬湊。

### 3.3 新增檔案規劃

| 檔 | 類型 | 職責 |
|---|---|---|
| `src/augur/models/sequence_ranker.py` | library（#18 需執行指令矩陣＋`--selftest`） | `class SeqLSTM`：`__init__(seed, hidden_size=32, epochs=50, lr=1e-3)`；`fit(tensor, y_rank)`（內部：z-score 正規化＝train 統計、NaN→0、建 `nn.LSTM(input_size=n_channels, hidden_size, batch_first=True)`+`nn.Linear(hidden_size,1)`、Adam、MSE loss、`epochs` 次全批訓練——資料量小(數千樣本)故不另分 mini-batch，CPU 可行)；`predict(tensor)`（沿用 fit 時凍結之正規化統計，避免測試期用測試期統計＝洩漏)。契約與 `RankRidge`/`RankGBDT` 同構(`fit`/`predict`)，供未來若要並入既有機制時零介面改動。 |
| `scripts/train_sequence_ranker.py` | CLI（#29 執行指令矩陣＋個別可執行） | 主編排：一次性面板快取（§3.1）→通道篩選（§3.2）→對 H60 既有 22-panel walk-forward 折（複用 `walkforward.splits`，folds 與冠軍評測**同一份**）逐折建訓練張量＋fit SeqLSTM＋predict test 折＋`build_long_portfolio`＋指標彙總（`_metrics`/`_turnover`，回傳值與 `run_backtest` **同形狀** dict,供直接比較)。`--seeds 1,2,42`、`--smoke`（Phase 0a 單折限時探測,見 §4）。 |

**零改動**：`train_ranker.py`／`predict_asof.py`／`ranker.py`／`portfolio.py`——本計畫全程新增檔案,不動既有生產路徑（#3 最小邊界)。

---

## 4. 分階段（每階段皆為停損點,任一不過即誠實收尾,不勉強推進）

| 階段 | 內容 | Gate | 寫庫? |
|---|---:|---|---|
| **Phase 0a：可行性煙測** | 只跑**最後一折**（訓練樣本最多、最壞情境）、**單一 seed**，實測一次 fit+predict 耗時 | 單折 < 5 分鐘 → 可行,估算全量（22 折×3 seed=66 次)是否 < ~2 小時；若單折即 >5 分鐘,誠實回報「CPU 算力不足以支撐全量 walk-forward」，與用戶討論縮小範圍（減折數／減 seed／減 epochs）而非硬跑 | 否 |
| **Phase 0b：全量 walk-forward 評測** | 22 折×3 seed，H60,同既有冠軍 panel 集 | 產出 net Sharpe/hit（min/median/max/mean），**零預設會贏**——如實記錄 | 否 |
| **決策門檻** | 比照 RankEnsemble 紀律：**3-seed net Sharpe min > 1.3016**（現任冠軍)才算真贏;中位數/單 seed 勝出**不算數**（#32b 預凍對照臂) | — | — |
| **Phase 1（條件觸發，另句）** | 若真贏：設計 `predict_asof.py` 序列模型變體（需另評估——不同資料源之 as-of 推論介面）、`model_registry` 登錄方式 | 本計畫**不含**,通過 gate 後另立短計畫 | 是（另句授權） |

**若 Phase 0a 即顯示 CPU 算力不足**：這本身是誠實且有價值的發現（"序列 DL 需要 GPU 才可行,現況本機無 GPU"），比照既有 S4-Wave-B/C/D SKIP 先例誠實列帳,**不得**為了「有結果可交」而縮水 epoch／折數到失真程度、也不得靜默降規格後仍稱「已評測」。

---

## 5. (a) 對應 table schema

**Phase 0/1（本 GO 範圍）零新表**。全部使用既有 DB 讀取（`TaiwanStockPriceAdj`／籌碼表經 `build_stock_panel`；`core_universe_asof`；`feature_values`不使用，序列窗自成一路)。`model_registry`／`prediction_values` schema **不觸碰**（Phase 2 條件觸發才可能寫入,結構同 RankEnsemble 計畫書 §2 既有表,屆時沿用,非本階段規劃範圍)。

---

## 6. 硬邊界（承既有 GO 慣例）

- FZ/GATE-keep／no-SIM-apply／skip-sync：**守**,零 FinMind／FRED,零 sim `--apply`,零 gate 改動。
- **零** `model_registry` 寫入、**零** `prediction_values` 寫入（Phase 0/1 範圍)。
- **零**確立級／可交易宣稱——即便 Phase 0b 顯示真贏,亦只代表「評測分數優於現任冠軍」,非可交易判定（direction_gate／人裁另層,承既有全部模型邊界)。
- CPU-only 誠實揭露：不得宣稱「已用 GPU 訓練」或暗示規格高於實際。

---

## 7. 驗收方式

- Phase 0a：stdout 耗時數字,寫入 `audits/S4-SEQLSTM-SMOKE-20260804.md`（可行/不可行判定＋下一步建議)。
- Phase 0b：stdout 22 折×3 seed 全數字,寫入 `audits/S4-SEQLSTM-EVAL-20260804.md`（比照 `S4-RANKENSEMBLE-EVAL` 格式,含逐項對照 gate 判定表)。
- `ReadLints`／`--selftest`（`sequence_ranker.py` 新模組結構斷言,零 IO)。

---

*定版（2026-08-04）。下一手＝Phase 0a 可行性煙測（單折、單 seed,先確認 CPU 算力可行,再決定是否投入全量 22 折×3 seed）。*

---

## 執行後記（2026-08-04，Phase 0a EXECUTED）

**Phase 0a 已執行、誠實判定「可行」**——詳見 `audits/S4-SEQLSTM-SMOKE-20260804.md`。

| 門檻 | 實測 | 判定 |
|---|---|---|
| 單折重覆成本（build_xy+fit+predict,不含一次性面板抓取）< 5 分鐘 | 59.5s | ✓ |
| 全量外推（19 折×3 seed）< 2 小時 | ≈3866s（≈64.4 分鐘） | ✓ |

一次性面板抓取（318 股）實測 364.5s,略高於 §3.1 估算之 ≤5 分鐘（估算基準為 S3-Wave-D 225 股/3 窗長 262.6s 外推單一窗長;此差異不影響 Phase 0a 判定,因該門檻對象是「單折重覆成本」非一次性抓取——詳見審計 §3.1）。

`scripts/train_sequence_ranker.py` 之 `--run`（Phase 0b 全量,19 折×3 seed）已寫好完整程式碼（含鏈式換手成本,同 `run_backtest` 口徑,#12 共用）,**尚未執行**——待另授權。Phase 1（若 Phase 0b 過經濟門檻）仍未動工。

## 執行後記二（2026-08-04，Phase 0b EXECUTED——誠實未過門）

**Phase 0b 已執行、誠實判定「未過經濟門檻」**——詳見 `audits/S4-SEQLSTM-EVAL-20260804.md`。

| 門檻 | 實測（3-seed net Sharpe） | 判定 |
|---|---|---|
| min > 1.3016（現任冠軍 `RankRidge_H60`） | min=1.1311／median=1.1517／max=1.1649 | ✗ 未過（三 seed 皆低於冠軍,非邊緣未過） |

全量評測耗時 2140.0s（19 折×3 seed）＋一次性面板抓取 394.8s＝總計 ≈42.2 分鐘。三 seed 高度一致（gross Sharpe 區間僅 0.0034）、策略本身仍正收益（net CAGR +11.8%~+16.7%），但未達比橫斷面 Ridge 冠軍更優之門檻。**不進 Phase 1**——`SeqLSTM` class 與評測 CLI 予以保留供未來換超參／horizon／通道集重探,不刪除。8 族 missing model adapter 之首族評測至此收尾。

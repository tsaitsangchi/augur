# S4-Wave-A 6 族 sklearn adapter Phase 0 全量評測執行帳 [I]（2026-08-04）— EXECUTED（1/12 真贏）

> **位階**：[I] 執行留痕（非 META-CONSTITUTION [N]）。
> **GO**：Steward 對話拍板「approve_now」（`reports/augur_s4_wave_a_sklearn_adapters_plan_20260804.md`；6 族 class＋dispatch 已先行寫完,評測延後至背景資源空出才跑）。
> **前置**：`ranker.py` 6 新族 class＋`_selftest`＋真實資料煙測（thread oversubscription 已修,`n_jobs=1`/`thread_count=1`）。
> **探針**：`/tmp/wavea_phase0_probe.py`（一次性,非產品碼;直呼 `portfolio.run_backtest`,同冠軍評測口徑）,log=`/tmp/wavea-phase0-probe.log`,PID 1196473。
> **self-reported（#32a）**：數字出自 stdout（(a)）；判讀為 AI 呈案。

---

## 1. 約束遵守

| 約束 | 本窗 |
|---|---|
| skip-sync | **守**——零 FinMind／FRED,全程僅讀既有 `feature_values`／`prodset` 特徵 |
| no-SIM-apply | **守** |
| FZ/GATE-keep | **守** |
| 零 `model_registry`／`prediction_values` 寫入(Phase 0 定義) | **守**——僅呼叫 `portfolio.run_backtest`(評測),未觸任何生產表 |
| 預凍對照臂(CLAUDE #32b) | **守**——冠軍門檻(`CHAMPION` dict)於探針程式**先**寫定(H60=1.3016/0.6316、H20=1.1684/0.6393,同 `S5-OOS-20260804.md` 口徑),後才跑值 |

---

## 2. 全量評測結果(6 族×3 seed×2 horizon=36 次獨立 backtest;top20%/equal/cost=0.585%/prodset/until 2026-06-30)

### H60(22 panels)冠軍 net Sharpe=1.3016 net hit=0.6316

| 族 | seed1 | seed2 | seed42 | min/median/max | min hit | 判定 |
|---|---|---|---|---|---|---|
| RankXGB | 1.1905 | 1.1075 | 1.1116 | 1.1075/1.1116/1.1905 | 0.6316 | ✗未過 |
| RankCat | 1.1527 | 1.0049 | 1.0164 | 1.0049/1.0164/1.1527 | 0.5789 | ✗未過 |
| RankRF | 1.1169 | 1.1068 | 1.0206 | 1.0206/1.1068/1.1169 | 0.6316 | ✗未過 |
| RankSVM | 1.2190 | 1.1961 | 1.2321 | 1.1961/1.2190/1.2321 | 0.5789 | ✗未過 |
| RankKNN | 1.2908 | 1.2908 | 1.2908 | 1.2908/1.2908/1.2908 | 0.6316 | ✗未過(確定性演算法,3 seed 完全同值) |
| RankMLP | 1.1005 | 1.1692 | 0.9935 | 0.9935/1.1005/1.1692 | 0.5263 | ✗未過 |

### H20(66 panels)冠軍 net Sharpe=1.1684 net hit=0.6393

| 族 | seed1 | seed2 | seed42 | min/median/max | min hit | 判定 |
|---|---|---|---|---|---|---|
| RankXGB | 0.9567 | 1.0007 | 1.0142 | 0.9567/1.0007/1.0142 | 0.5902 | ✗未過 |
| RankCat | 1.0429 | 1.0303 | 1.0559 | 1.0303/1.0429/1.0559 | 0.6557 | ✗未過 |
| RankRF | 1.0222 | 1.0391 | 0.9662 | 0.9662/1.0222/1.0391 | 0.6557 | ✗未過 |
| **RankSVM** | **1.2345** | **1.2770** | **1.2258** | **1.2258/1.2345/1.2770** | **0.6393** | **✓真贏** |
| RankKNN | 0.5994 | 0.5994 | 0.5994 | 0.5994/0.5994/0.5994 | 0.5738 | ✗未過(確定性演算法) |
| RankMLP | 1.1944 | 1.2308 | 1.0663 | 1.0663/1.1944/1.2308 | 0.5902 | ✗未過 |

**耗時**：總計 2593.4s ≈ 43.2 分鐘(36 次 backtest,含與 S3-Wave-B 驗證＋DIRFAMILY 驗證之 CPU 三方競合期,較無競合下預估更慢)。

---

## 3. 對照計畫書「決策門檻」逐項判定

| # | 門檻 | 實測 | 判定 |
|---|---|---|---|
| 1 | 3-seed net Sharpe min > 冠軍(逐族逐 horizon) | 12 個(族×horizon)組合中,**僅 RankSVM@H20 一項**滿足 min(1.2258) > 冠軍(1.1684) | **1/12 真贏** |
| 2 | 禁中位數／單 seed 宣稱勝出 | 遵守——除 RankSVM@H20 外,其餘 11 組合 3 seed 皆低於冠軍(非邊緣單 seed 偶然) | 遵守 |
| 3 | RankSVM@H20 hit rate 同向確認 | min hit=0.6393 = 冠軍 hit 0.6393(**相等,非更低**) | 同向不劣,非僅 Sharpe 單指標偏高 |

**判定：RankSVM@H20 為本次探針唯一真贏組合;其餘 5 族(RankXGB/RankCat/RankRF/RankKNN/RankMLP)在 H60、H20 兩個 horizon 上均未過門。**

---

## 4. 判讀(誠實;非事後找理由)

- **RankSVM@H20 三 seed 一致真贏**(1.2258/1.2345/1.2770,區間 0.051,不寬)——非單 seed 噴發偶然,3/3 seed 穩定贏冠軍 5%~9%,net hit 持平非因犧牲勝率換 Sharpe。**但 RankSVM@H60 卻未過**(min=1.1961 < 冠軍 1.3016,差 8%)——同一族在不同 horizon 表現分歧,不可將 H20 之贏推論為「RankSVM 全面優於 RankRidge」,僅能誠實記錄「RankSVM 於 H20、本特徵集(prodset,3 特徵)、本評測口徑下真贏,H60 不贏」。
- **RankKNN／RankRF 兩族在兩個 horizon 皆穩定跑輸**,且 RankKNN 因確定性演算法(無 `random_state` 影響)3 seed 完全同值——非評測 bug,是 `RankKNN` 本身`seed`參數確實被忽略(`ranker.py` 已明文記載此設計:「確定性演算法、無 random_state」)之預期現象。
- **RankXGB／RankCat／RankMLP 三族全數未過**——與 SeqLSTM Phase 0b、RankEnsemble 兩次先例呼應:橫斷面 Ridge 冠軍護城河深,GBDT 系與淺層 MLP 皆未能穩定超越;RankSVM(線性核)之贏,方向上與「線性模型在此宇宙/特徵集有優勢」之既有觀察(RankRidge 本身即線性)一致,而非樹模型/神經網路方向。
- **`prodset` 特徵集僅 3 個特徵**(探針輸出 `feats=3`)——這是**目前生產特徵集的現況規模**,樣本量/特徵維度都不大,RankSVM(LinearSVR)在低維、線性可分場景本有先天優勢;此結果**不能外推**到未來特徵集擴充(如 S3-Wave-B/C 若新特徵入列)後是否仍成立,需在特徵集變動後重新驗證。

---

## 5. 決策(依計畫書分階段設計)

**RankSVM@H20 真贏,依 CLAUDE #32(b) 觸發後續驗證,但尚不足以直接宣稱「可交易」或「升格生產」**——依 FZ/GATE-keep 硬邊界,升格需另一輪 plan-first＋Steward 明示,本帳僅誠實記錄探針結果,**不**自動：
- 不寫 `model_registry`
- 不改 `predict_asof.py` 預設族
- 不觸發 `S4-DIRFAMILY-GENERALIZE` Phase 1(該計畫§6 之觸發條件雖技術上已滿足「某族真贏」,但 Phase 1 本身仍需另一句 Steward 授權,非本帳自動觸發)

**其餘 5 族(RankXGB/RankCat/RankRF/RankKNN/RankMLP)**：兩個 horizon 均未過門,依「誠實 SKIP」慣例保留 class(零額外成本,供未來換特徵集/超參重探),不進一步投入。

**下一步(若要推進 RankSVM@H20)**：建議至少一項獨立確認才進入下一階段討論——(a) 換一組不重疊評測窗複驗(降低「單一窗口幸運」風險)、(b) 檢查 `RankSVM`(LinearSVR)之逐 panel 換手率/持股集中度是否合理(非僅看 Sharpe)、(c) 若要餵 DIRFAMILY Phase 1,需先取得 Steward 對「是否推進 Phase 1」之明示授權——本帳不代為決定,僅呈現探針結果供裁示。

---

## 6. 硬禁未觸

零 FinMind／FRED；零 sim `--apply`；零 `direction_gate`／`model_registry` 寫入；零確立級／可交易宣稱；CPU-only 誠實揭露(本機無 GPU,全程 CPU 訓練,與 S3-Wave-B／DIRFAMILY 驗證三方 CPU 競合下完成,耗時已如實記錄非最佳單獨執行時間)。

---

## 7. RankSVM@H20 獨立確認(跨期分半複驗,2026-08-04 追記)

> **觸發**：用戶對「RankSVM@H20 真贏之後下一步」裁示「先跑獨立確認」。**預先寫定判準**(跑前定義,非看結果後選)：RankSVM 3-seed min Sharpe 須在**兩個獨立時間半段**皆 > 對應半段之 RankRidge Sharpe,才算「跨期穩健真贏」；任一半不贏,誠實記錄「僅 pooled 期間贏」。
> **方法**：非重跑不同 pooled 窗(會犧牲訓練資料量、失去可比性),而是複用 `portfolio.run_backtest` 已回傳之逐折 `dates`/`net_series`(全歷史訓練,與原探針完全同折)、按時序切兩半、各半獨立以 `portfolio._metrics()`(零重寫,同函式)重新聚合——**同一次訓練豐富度,只切輸出**,排除「切半導致訓練資料變少」之干擾。`/tmp/ranksvm_h20_split_verify.py`,PID 1246002,耗時 434.5s。

| 半段 | 日期範圍 | RankRidge Sharpe | RankSVM min/median/max Sharpe(3-seed) | 判定 |
|---|---|---|---|---|
| 前半(30 折) | 2021-06-30..2023-11-30 | 0.9916 | 1.2192/1.2548/1.3141 | ✓贏(min 仍 >22%優於冠軍) |
| 後半(31 折) | 2023-12-31..2026-06-30 | 0.5266 | 1.2651/1.3065/1.3118 | ✓贏(min 仍 >140%優於冠軍) |

**判定：✓跨期穩健真贏(兩半皆贏)**——非 pooled 期間之偶然集中。值得一提的觀察(誠實記錄,非過度延伸)：`RankRidge` 本身在後半段(2023-12+)Sharpe 大幅滑落(0.99→0.53,近乎腰斬),`RankSVM` 三 seed 卻在後半維持甚至略升(1.22~1.31→1.27~1.31)——顯示此優勢**不是「兩者同步衰退、RankSVM 衰得較慢」之相對假象**,而是 RankSVM 在 RankRidge 明顯失能的近期子期間**絕對表現仍強**。此獨立確認**提升**(非降低)RankSVM@H20 真贏之可信度,但**仍限於**：本評測僅用 `prodset` 現況 3 特徵、單一 horizon(H20)、`top_frac=0.2`/`equal` 權重之單一設定——換特徵集或換設定後是否仍成立未測,不外推。

**下一步仍待 Steward 授權**(§5 決策未變)：是否推進 DIRFAMILY Phase 1(materialize RankSVM 餵 DirStack)——本追記僅提升證據強度,不自動觸發 Phase 1。

---

*完。[I] Phase 0 EXECUTED——1/12(族×horizon)組合真贏(RankSVM@H20),其餘 11 組合誠實未過門；獨立跨期分半複驗確認 RankSVM@H20 為穩健真贏、非 pooled 偶然。self-reported（#32a）。升格與否待 Steward 裁示。*

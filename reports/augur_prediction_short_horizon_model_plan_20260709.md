# 短 horizon 誠實預測模型計畫(H20/H40/H60 「30/60 天」相對強弱)

**日期**:2026-07-09 ｜ **性質**:plan-first(#20,拍板後才實作)｜ **動因**:用戶拍板「另建 H30/H60 誠實 horizon 模型」(omniscient 計畫 §7.1 決策1)
**守**:#8(源純特徵、零 import 素養層)· #14(經濟價值=成功定義)· #15(誠實四關、標真實可信度、不偽造)· 靈魂(相對強弱非絕對機率、禁占卜)· 原則精華 v1.8.0 **FREEZE**(只用 as-of 2026-05-31 凍結快照)

---

## 0. 三十秒 + 誠實預期(先講最重要的)

**這是探索、不是保證贏。** 誠實預期:短 horizon 歷來**更弱**(親查 H20 IC 0.113 < H60 0.152;H20 經濟 cell=0=**已判死**),加上特徵層飽和定論,新 H20/H40 **多半也是「真但薄、未達統計確立」**,甚至過不了經濟價值 #14。本計畫做的是**誠實地訓練+驗證這些 horizon,得出真實(多半薄)的可信度標籤**,餵進顧問的相對強弱讀數——**不是造出一個能可靠報「個股 30 天漲跌機率」的模型**(那是假兆、違靈魂)。

**若驗證結果是薄/未確立,那本身就是誠實交付**(#15:真兆是「薄」就報「薄」),非失敗。

## 1. 「30/60 天」單位釐清(命門,先釘清才不誤導)

horizon 單位是**交易日**;用戶「30天/60天」若指**日曆日**:

| 用戶說法(日曆日) | ≈ 交易日 horizon | 現況 |
|---|---|---|
| 30 天 | ≈ **H20**(20 交易日 ≈ 28 日曆日) | 已有 IC 0.113、經濟判死 |
| 60 天 | ≈ **H40**(40 交易日 ≈ 58 日曆日) | **新 horizon、未訓練** |
| (H60 已部署) | 60 交易日 ≈ **84 日曆日 ≈ 3 個月** | 已部署、未確立(DSR 0.756) |

**計畫做 horizon 矩陣 {H20, H40, H60},由驗證結果 + 你確認「日曆日 vs 交易日」定採哪個。** 不預設單一 horizon,誠實呈現各 horizon 之真實強度。

## 2. 治權框定(全守、無判準變更)

- **靈魂**:輸出**橫斷面相對強弱排序**(誰相對強、選 top-N)+ 誠實可信度,**非個股絕對漲跌機率**;禁占卜大師。顧問對「30/60 天」問題回此 horizon 的相對強弱讀數 + 薄可信度。
- **#8 隔離**:模型**只用 source-pure 特徵**(現有 feature_values),**零 import knowledge/philosophy**(import_isolation 閘覆蓋 models/evaluation);know-how 不進此模型(那是顧問解讀層、另一條路)。
- **FREEZE**(唯一觸點,對抗修正已納入):**只讀 as-of 2026-05-31 凍結 panel 訓練驗證**(develop-on-frozen-snapshot);接最新資料明文延後至系統完美後。**不因「要預測未來 30 天」去抓新資料**——用凍結快照做 out-of-sample walk-forward。
- **成功定義=經濟價值 #14**,非 IC。

## 3. 誠實四關管線(全複用既有 SSOT、零雙軌漂移 #12)

沿用既有 evaluation SSOT(baseline/walkforward/metrics/portfolio/deflation),horizon 只是參數:

```
train_ranker.py --horizon {20,40,60} --run       # RankRidge 確定性 + RankGBDT 多seed(既有)
  → 第1關 purged walk-forward(walkforward.splits,embargo=h+62td 保證下界 #8;H<252 允許)
  → 第2關 as-of rank IC + HAC effective_t_hac(禁裸 iid、G8;|HAC-t|≥2)
  → 第3關 經濟價值 #14(portfolio.run_backtest net=gross−turn×cost 0.585%、long top10%、vs 基準)
  → 第4關 deflation DSR(deflate_headline_verdict.py --horizon N,per-period、取保守 N;trial_ledger 機械)
  → 記 revalidation_ledger(B/C/D)+ trial_ledger + 誠實 verdict(標真實可信度、n 小 exploratory)
```

**每關都是既有工具**(train_ranker/verify_candidate_promotion/run_economic_eval/deflate_headline_verdict);新增=跑 H20/H40 兩 horizon(H60 已有)+ 誠實裁決報告。**零繞道 Claude(#28)、本地背景跑。**

## 4. 分階段 W1..W5 + 驗收

| 階段 | 內容 | 驗收 |
|---|---|---|
| **W1** | forward_returns@H40 口徑確認(label.py on-the-fly、無表;H40 embargo=102td<252 通過) | walkforward.splits(pds,40,cal) 不 raise、逐折 embargo≥102td |
| **W2** | train H20/H40(RankRidge+GBDT 多seed)、predict_asof 凍結快照 | model_registry 加 H20/H40 列、prediction_values 出(in_portfolio=0 候選) |
| **W3** | 誠實四關:Stage B IC+HAC-t、Stage C/D 經濟、deflation(取保守 N) | revalidation_ledger 補 H20/H40 B/C/D;deflate_headline_verdict --horizon 40 出 DSR |
| **W4** | 誠實裁決報告:H20/H40/H60 對比(IC/Sharpe/Calmar/DSR/deflated),標真實可信度+日曆日對映 | 報告 reports/;每 horizon 標【確立/未確立/判死】+ n 小 exploratory 誠實揭露 |
| **W5** | 接顧問:顧問對「30/60 天」問題回對應 horizon 相對強弱+薄可信度(承 omniscient 計畫三通道) | 端到端:「2330 未來 30 天?」→ H20 相對強弱排序+deflated 可信度+四 caveat+guard 過 |

**全 resume-safe、冪等、本地背景、零外部 usage。** 部署切換(若某 horizon 過關)屬決策層人拍板(#26、AI 不自改 in_portfolio)。

## 5. 誠實裁決預判(基於已知證據)

| horizon | 已知 | 預判 |
|---|---|---|
| H20(≈30 日曆日) | IC 0.113、經濟判死 | 大概率**未過經濟價值**(維持判死或薄) |
| H40(≈60 日曆日) | 新、介於 H20/H60 | 未知,**可能薄**(短 horizon+特徵飽和) |
| H60(≈84 日曆日) | 已部署、DSR 0.756 未確立 | 已知**未確立**(deflation 未過) |
| H120 對照 | DSR 0.936 近門檻最強 | 反證:**越長 horizon 越強**、短的更難 |

**誠實結論預期**:「30/60 天」比目前部署的 H60/最強的 H120 **更難確立**;若真做出來多半是薄 edge。這不會變成「可靠的 30 天漲跌預言」——但會是**誠實標好可信度的相對強弱讀數**,顧問據此誠實作答。

## 6. 用戶拍板 + 入憲(拍板後、實測後)

- **拍板前確認**:①「30/60 天」是日曆日(→H20/H40)還是交易日(→H20/H60)?②接受「多半薄/未確立」的誠實預期、以誠實標籤交付(非保證贏)?
- **入憲(驗證完成後、#19)**:horizon 矩陣結果記憲章修訂歷程/方法論;若某 horizon 過四關且人拍板部署→ payload `_DEPLOY_HORIZON` + revalidation baseline(承 H120 tracked-candidate 慣例);FREEZE 綁定(只凍結快照)留痕。**無靈魂/憲章判準變更**(相對強弱+誠實四關+FREEZE 皆既有法律之落地)。

---

## 7. 對應 table schema + python 程式規畫(憲章 v1.39.0 計畫完整性)

### 7.1 table schema:**無新表**(全用既有;schema 權威=DB information_schema #2)

本計畫**不產生新表**——訓練/驗證結果落既有表:

| 既有表 | PK / 關鍵欄 | 本計畫寫入 |
|---|---|---|
| `model_registry` | model_id;family/horizon/feats_hash/seed/metrics/train_span | 加 H20/H40 列 |
| `prediction_values` | (panel_date,model_id,stock_id);rank/score/in_portfolio | 加 H20/H40:in_portfolio=0 候選 |
| `revalidation_ledger` | **無 PK**（append-only ledger、按 run_at 逐列;唯一約束=CHECK `stage∈{B,C,D}`;index=ix_reval_asof_stage/ix_reval_metric_time **非唯一**）;欄 as_of_date/stage/horizon/model/config/metric_name/metric_value/n_periods/hac_t。**冪等靠 per-as_of DELETE 重寫、非 ON CONFLICT** | 補 H20/H40 之 B/C/D 列 |
| `trial_ledger` | **PK=(trial_id)** surrogate;**UNIQUE=(model,horizon,top_frac,weight,feats_hash,cost,sample_since)**（=`trial_ledger_uq`=N 機械計數鍵);seed 揭露欄 | 加 H20/H40 試驗列(N=count DISTINCT 之計數鍵) |
| (deflation) | 讀 trial_ledger + portfolio 即時重算 | 不落新表(裁決印出) |

### 7.2 對應 python 程式規畫(全既有工具、horizon 為參數、幾乎零新 code、守 #12 複用鐵律)

| 程式 | 新/改 | 職責 | 輸入表→輸出表 |
|---|---|---|---|
| `scripts/train_ranker.py --horizon {20,40} --run` | 既有(參數) | 訓 RankRidge 確定性 + RankGBDT 多seed | feature_values/core_universe_asof → model_registry |
| `scripts/predict_asof.py --horizon {20,40}` | 既有(參數) | 凍結快照預測、標 in_portfolio=0 候選 | model_registry/feature_values → prediction_values |
| `scripts/revalidate.py --run` | **改**(B_HORIZONS/CD_HORIZONS 加 20/40) | 誠實四關 Stage B(IC+HAC-t)/C/D(經濟) | feature_values → revalidation_ledger + trial_ledger |
| `scripts/deflate_headline_verdict.py --horizon {20,40}` | 既有(參數) | per-period DSR 取保守 N | revalidation_ledger/trial_ledger →(裁決印出) |
| `scripts/verify_candidate_promotion.py` | 既有 | 提拔關卡 HAC-t(禁裸 iid) | revalidation_ledger →(裁決) |
| `scripts/report_short_horizon_verdict.py` | **新**(W4) | H20/H40/H60 對比 + 誠實可信度 + 日曆日對映 | revalidation_ledger/trial_ledger → reports/ |

**唯一新 code**=W4 裁決報告腳本 + revalidate.py 加 horizon 常數;其餘全既有工具加 `--horizon` 參數(offline 驗證與 live 預測共用同 evaluation SSOT,零雙軌漂移 #12)。**#8 隔離**:全程零 import knowledge/philosophy(import_isolation 閘覆蓋 models/evaluation)。

---

## 附:實查錨(2026-07-09、venv python、#15)
horizon 單位=交易日(walkforward.py:17,48)· H≥252 禁入 · model_registry 訓練 {H60,H120} · H20 IC 0.113/經濟 cell **0**(判死)· H60 IC 0.152/DSR 0.756 · H120 IC 0.155/DSR 0.936 · 1 交易日≈1.45 日曆日。

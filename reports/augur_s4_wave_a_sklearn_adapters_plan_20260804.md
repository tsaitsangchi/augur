---
status: draft
series: s4_model_families
depends_on:
  - reports/augur_s4_market_model_families_opt_plan_20260804.md
  - audits/S4-MODELS-TRIED-LIST-20260804.md
---

# S4-Wave-A 缺 adapter 8 族 — sklearn/xgboost/catboost 排序模型 plan-first（2026-08-04）

> **性質**：[I] plan-first（憲章第六部；CLAUDE #20）。**不含**任何 `--run`／registry 寫入／自動晉升。
> **觸發**：`audits/S4-MODELS-TRIED-LIST-20260804.md` §4「未試／殘餘」——`XGB／Cat／RF／LTR／SVM／KNN／NB／淺MLP` 8 族 **SKIP until adapter**；`audits/S4-REOPT-BACKLOG-20260804.md` 亦列為下一波候選。
> **對照紀律**：比照 `reports/augur_s4_rank_ensemble_blend_plan_20260804.md`（T4a）之驗收紀律——3-seed net Sharpe **min** 須真贏現任冠軍才算數,中位數/單 seed 勝出不算（CLAUDE #32b 預凍對照臂）。

---

## 1. 背景與現有介面盤點（why + 現狀）

現有生產排序族僅 2 個，皆為**逐股橫斷面回歸「rank 目標」**（`label.labels()` 產出之 0-1 百分位），契約極薄：

```12:14:src/augur/models/ranker.py
   契約極薄:fit(X, y_rank) → self;predict(X) → ndarray(n,)(float、任意尺度,只看序位)。
```

```20:65:src/augur/models/ranker.py
class RankRidge:
    family = "RankRidge"
    def __init__(self, alpha=1.0): ...
    def fit(self, X, y_rank): ...   # StandardScaler + Ridge
    def predict(self, X): ...

class RankGBDT:
    family = "RankGBDT"
    def __init__(self, seed=42): ...
    def fit(self, X, y_rank): ...   # LGBMRegressor(固定超參)
    def predict(self, X): ...
```

`scripts/train_ranker.py` 用 `FAMILIES = {"RankRidge": RankRidge, "RankGBDT": RankGBDT}` dict 做 `--family` 字串 dispatch,登錄 `model_registry` 後 `predict_asof.py` 純用 `registry.latest(family, horizon, asof)` 字串比對＋`artifact.load()` 泛型反序列化載入——**對 estimator 類別完全無知**（不管裡面是 Ridge／LightGBM／XGBoost，只要有 `.predict()` 就能載）。**這代表新增族只需**：(a) 在 `ranker.py` 加新 class（同構 `fit`/`predict`）,(b) 在 `train_ranker.py` 的 `FAMILIES` dict 掛一行——`predict_asof.py` **零改動**即可服務新族。

評測側（`portfolio.run_backtest`）是**獨立的第二套 inline 建模邏輯**（非重用 `models/ranker.py` classes——這是既有架構,非本計畫引入）：

```180:193:src/augur/evaluation/portfolio.py
        if model == "B2_ridge":
            ...
        elif model == "ENS_ridge_gbdt":
            ...
        else:
            pred = LGBMRegressor(...).fit(Xtr, ytr).predict(Xc)
```

比照 T4a（`ENS_ridge_gbdt`）先例,新族之**評測**掛點＝在此加 `elif model=="RankXGB": ...` 分支；**生產**掛點＝`ranker.py` 新 class ＋ `train_ranker.py` FAMILIES。兩者分開（評測≠生產路徑,本計畫不改此既有雙軌設計,#3 最小邊界）。

**套件盤點（零新依賴,已全數確認安裝）**：

| 套件 | 版本 | 用途 |
|---|---|---|
| `xgboost` | 3.3.0 | RankXGB |
| `catboost` | 1.2.10 | RankCat（需 `allow_writing_files=False`,見 §3） |
| `scikit-learn` | 1.9.0 | RankRF／RankSVM／RankKNN／RankMLP／RankNB |
| `lightgbm` | 4.6.0 | 已用（RankGBDT） |

---

## 2. 8 族逐一設計——6 族同構 + 2 族架構不同（誠實標記,不硬套）

### 2.1 六族同構（直接回歸 rank 目標,與 RankRidge/RankGBDT 完全同契約,零架構新增）

| 族名 | Estimator | 建構要點 |
|---|---|---|
| `RankXGB` | `xgboost.XGBRegressor` | `n_estimators=200, max_depth=4, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=seed, n_jobs=1`（超參量級比照 RankGBDT,非調參最優——首輪普查非最優化,同 T4a 精神；`n_jobs=1` 見下方執行後記,避免 walk-forward 序列迴圈下執行緒過度訂閱） |
| `RankCat` | `catboost.CatBoostRegressor` | `iterations=200, depth=4, learning_rate=0.05, thread_count=1, random_state=seed, verbose=False, allow_writing_files=False`——**後兩者必帶**,否則預設寫 `catboost_info/` 訓練日誌到 cwd（副作用污染工作目錄,非本計畫要的） |
| `RankRF` | `sklearn.ensemble.RandomForestRegressor` | `n_estimators=200, max_depth=8, min_samples_leaf=10, random_state=seed, n_jobs=1` |
| `RankSVM` | `sklearn.svm.LinearSVR` | `LinearSVR`（非 RBF `SVR`）——RBF-kernel SVR 訓練成本 O(n²–n³),n_train≈6000+ 時單折即可能數十秒~分鐘級、乘 19-22 折×3 seed 不成比例;`LinearSVR` 訓練近線性、`random_state=seed`。**若後續想試非線性 kernel,建議先在 n 截斷子樣本上量測耗時再決定,不預設跑全量** |
| `RankKNN` | `sklearn.neighbors.KNeighborsRegressor` | `n_neighbors=20, weights="distance"`——**無 `random_state`**（確定性演算法,已查證 sklearn 1.9.0 API）,`seed` 參數接受但忽略 |
| `RankMLP` | `sklearn.neural_network.MLPRegressor` | `hidden_layer_sizes=(32,), max_iter=300, early_stopping=True, random_state=seed`——刻意**淺層**（單隱藏層 32 units),對齊債表原文「淺 MLP」;`early_stopping=True` 防過長訓練 |

**契約範例**（比照 `RankGBDT` 結構,`ranker.py` 新增,略去 import 細節）：

```python
class RankXGB:
    family = "RankXGB"
    def __init__(self, seed=42):
        self.seed = seed
        self._model = None
    def fit(self, X, y_rank):
        from xgboost import XGBRegressor
        self._model = XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.05,
                                    subsample=0.8, colsample_bytree=0.8,
                                    random_state=self.seed).fit(
            np.asarray(X, dtype=float), np.asarray(y_rank, dtype=float))
        return self
    def predict(self, X):
        if self._model is None:
            raise RuntimeError("RankXGB 未 fit")
        return self._model.predict(np.asarray(X, dtype=float))
```

其餘 5 族結構相同,僅 `fit()` 內建構的 estimator 不同（見上表）。

**介面小簡化（連帶,#3 範圍內最小必要）**：`train_ranker.py` 現用 `est_cls(seed=seed) if family == "RankGBDT" else est_cls()` 特判 RankGBDT。新增 6 族中 4 族（XGB/Cat/RF/MLP）需 `seed`,2 族（SVM/KNN）不需但可接受忽略——建議 `RankRidge.__init__` 亦加一個**忽略**的 `seed=None` 形參,讓 dispatch 行統一簡化為 `est_cls(seed=seed)`（全族一致,移除特判）。此為現有檔案的最小訊號修改（1 個形參,向後相容,不影響既有呼叫）。

### 2.2 兩族架構不同——誠實標記,不強套（本計畫核心誠實揭露）

| 族 | 為何不是「直接套同契約」 | 可行做法（若要做） | 建議 |
|---|---|---|---|
| **RankNB**（Naive Bayes) | sklearn 之 `GaussianNB`／`MultinomialNB` 皆為**分類器**,無「NB 回歸器」;不能直接 `fit(X, y_rank)` 之連續目標 | 需先將連續 rank 目標**離散化**（如五分位/十分位桶）→ `GaussianNB` 分類 → 用 `predict_proba(X)[:, top_bucket]` 之機率當「排序分數」——**近似**,非原生回歸,且離散化門檻（幾分位）是新增超參 | **Phase 0 暫緩**——與其他 6 族混評會扭曲比較（不同誤差結構);若要做建議獨立小節,附離散化敏感度分析 |
| **RankLTR**（Learning-to-Rank，pairwise/listwise) | 真正 LTR（如 `LGBMRanker`/`XGBRanker` 之 `lambdarank`/`rank:pairwise` 目標）需要**「每列屬於哪個 as-of panel」之 group 資訊**,現有 `fit(X, y_rank)` 二參數契約無此欄位；`train_ranker.py`/`baseline._fold_xy` 現況把多個 panel **攤平**成單一 (X,y),沒有保留 panel 邊界 | 需擴充契約為 `fit(X, y_rank, groups=None)`（`groups`=各列所屬 panel 之陣列或每組列數),`_fold_xy` 需同步回傳 group 邊界——**影響面擴及 `evaluation/baseline.py` 既有函式簽名**,非本計畫「加一個 class」等級的小改 | **本計畫不做**——若不擴充 group 資訊,「LTR」只能退化成 pointwise 回歸（=RankRidge/RankGBDT 已經在做的事,無新增價值,假冒 LTR 之名）。**建議獨立另立計畫**評估是否值得擴充 `fit()` 契約（跨既有函式簽名,風險/效益需先討論） |

**一句誠實結論**：8 族中 **6 族**可用現有契約零架構改動完成；NB 需近似法（獨立小節）；LTR 需契約擴充（建議另立計畫,不在本次範圍內硬做假 LTR）。

---

## 3. Table Schema

**零新表**。全程複用既有：

| 表 | 用途 | 是否新增欄位 |
|---|---|---|
| `model_registry` | Phase 1（若有族真贏）登錄 model_id／family／metrics | 否 |
| `feature_values` | 訓練特徵來源（既有 prodset/canonical） | 否 |
| （模型 artifact 檔案,非 DB 表） | `models/artifact.py` 現有 joblib 序列化路徑 | 否 |

Phase 0（評測）**零 DB 寫入**——沿用 `portfolio.run_backtest` 唯讀評測模式（同 RankEnsemble Phase 0）。

---

## 4. Python 程式規畫

| 檔 | 動作 | 內容 |
|---|---|---|
| `src/augur/models/ranker.py` | 修改（新增 6 class＋`RankRidge` 加忽略 `seed` 形參） | `RankXGB`／`RankCat`／`RankRF`／`RankSVM`／`RankKNN`／`RankMLP`（§2.1 結構）；`_selftest()` 對應擴充 6 族之 family 標識／未 fit 守衛斷言 |
| `scripts/train_ranker.py` | 修改 3 行 | `FAMILIES` dict 加 6 項；dispatch 行簡化為 `est_cls(seed=seed)`（去特判） |
| `src/augur/evaluation/portfolio.py` | `run_backtest` 新增 6 個 `elif model=="RankXGB": ...` 分支（比照 `ENS_ridge_gbdt` 既有模式） | 供評測/Phase 0 用；分支內建構同 §2.1 estimator（**與 `ranker.py` 的 6 class 建構參數須一致**,否則評測與生產訓練漂移,#12） |
| 新 script `scripts/probe_wave_a_families.py`（或沿用 heredoc 模式,比照 T4a 之 `/tmp/rank-ensemble-3seed-h60.log` 做法） | 新建 | 迴圈 6 族 × 3 seed × H60（+H20 交叉參考）,呼叫 `portfolio.run_backtest`,彙總 net Sharpe/hit(min/median/max/mean) vs 冠軍,產出單一比較表；**唯讀,零寫庫** |
| `audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md`（Phase 0 完成後另寫） | 新建 | 比照 `audits/S4-RANKENSEMBLE-EVAL-20260804.md` 格式 |

---

## 5. 分期與驗收門檻

| 階段 | 內容 | 驗收 | 需另授權？ |
|---|---|---|---|
| **Phase 0：評測** | 6 族 × H60 3-seed（+H20 交叉參考）net Sharpe/hit,對照冠軍 RankRidge_H60（net Sharpe 1.3016／hit 0.6316）、RankRidge_H20（1.1684／0.6393） | **3-seed net Sharpe min > 冠軍**才算真贏（中位數/單 seed 不算數,#32b）；逐族獨立判定,允許「6 族全輸」之誠實結果 | 否（純評測,零寫庫,同 T4a Phase 0 已有先例） |
| **Phase 1（條件觸發）** | 若有族真贏：登錄 `model_registry`＋`train_ranker.py --family RankXXX --run`,納入 `predict_asof.py` 候選 | 本計畫不含,通過 gate 後另立短句 | 是 |
| **NB 近似法**（獨立） | 若想追加,獨立小節：離散化門檻敏感度＋機率轉分數 | 同 Phase 0 門檻,但誤差結構不同、不與其他 6 族混評 | 視 Phase 0 結果決定是否追加 |
| **LTR 契約擴充**（獨立） | 是否值得擴充 `fit(X,y,groups)` | 本計畫不含,另立計畫評估 | 是（跨既有函式簽名,風險較高） |

---

## 6. 風險與硬邊界

- **零預設會贏**——比照 RankEnsemble 教訓（等權融合看似穩健卻未過門）,6 族任一族都可能全部劣於 RankRidge/RankGBDT;誠實記錄,不為「有新結果可交」硬湊。
- **SVR 效能**：`LinearSVR` 而非 `SVR`（RBF）是刻意選擇,避免 O(n²-n³) 訓練成本在 19-22 折×3 seed 下不成比例拖慢；若 Phase 0 後想試 RBF-kernel,建議先在單折量時再決定（比照 LSTM Phase 0a 先煙測再全量的紀律）。
- **CatBoost 副作用**：務必 `allow_writing_files=False`,否則預設寫 `catboost_info/` 到 cwd。
- **NB／LTR 不強套**：寧可誠實列「架構不同、本次不做」,不為衝數量把分類器硬拗成回歸、或把 pointwise 回歸包裝成「LTR」之名。
- **評測與生產雙軌需同參數**（#12）：`portfolio.py` 的 `elif` 分支與 `ranker.py` 的 class 建構參數若不一致,會導致「評測贏但生產 artifact 建出來的模型不同」之隱性漂移——實作時逐族核對兩處參數字面相同。
- **零改動** `predict_asof.py`（已確認泛型,零特判 estimator 類別）。

---

## 7. 驗收方式

- Phase 0：stdout 全數字寫入 `audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md`（比照 `S4-RANKENSEMBLE-EVAL` 格式,含逐族逐 seed 明細＋對冠軍門檻判定表）。
- `ReadLints`／`ranker.py --selftest`（新 6 class 之 family 標識／未 fit 守衛/`fit`+`predict` 契約斷言,零 IO,#29a 個別可驗證）。
- `git diff` 對照 `portfolio.py`／`train_ranker.py` 改動範圍（確認僅新增 dispatch 分支,未動既有 B2_ridge/M1_gbdt/ENS_ridge_gbdt 邏輯）。

---

*定版（2026-08-04）。下一手＝實作 §4 程式規畫（6 族同構,零架構風險)→ Phase 0 評測；NB／LTR 明確排除本輪範圍,誠實標記待另裁。*

---

## 執行後記（2026-08-04）

`src/augur/models/ranker.py` 6 族已實作＋`--selftest` 全通過（結構斷言）＋**真輸入 fit/predict 煙測全通過**（80×5 隨機矩陣,8 族皆產出 finite 預測,見下）：

| 族 | 首次煙測（未限執行緒） | 修正後（`n_jobs=1`／`thread_count=1`） |
|---|---|---|
| RankXGB | **>2.5 分鐘未完**（493% CPU,執行緒過度訂閱） | 0.12s |
| RankCat／RankRF | 未測（同批修正） | 0.38s／0.30s |
| 其餘 5 族 | 正常（<3.3s,含首次 import） | 不變 |

**發現＝真實工程問題,非臆測**：`XGBRegressor`／`RandomForestRegressor`／`CatBoostRegressor` 預設搶全機核心；本回合系統已有 2 個背景工作（LSTM Phase 0b／Wave-B verify）佔用多核,單支 80 列小 fit 因執行緒過度訂閱（thread thrashing）卡住 >2.5 分。**修正**：三族一律加 `n_jobs=1`／`thread_count=1`——理由不僅是「避開本次背景競合」,walk-forward 迴圈本身即**序列**呼叫多折多 seed,單折內部再搶多核對整體吞吐反而有害（外層序列＋內層單執行緒＝正確調度）。§2.1 表格與 §4 程式規畫之建構參數已同步更新為含此限制。

§4 表列之 `portfolio.py` 評測分支與 `scripts/train_ranker.py` FAMILIES／dispatch 簡化,下一步實作。

---

## 執行後記二（2026-08-04）——Phase 0 全量評測完成

背景探針（6 族×3 seed×{H60,H20}=36 次 backtest,總耗時 2593.4s≈43.2 分鐘,與 S3-Wave-B／DIRFAMILY 驗證三方 CPU 競合下完成)已結束,結果詳 `audits/S4-WAVE-A-SKLEARN-EVAL-20260804.md`：

**12 個(族×horizon)組合中,僅 `RankSVM`@H20 一項真贏**(min net Sharpe 1.2258 > 冠軍 1.1684,hit 持平 0.6393)；`RankSVM`@H60 及其餘 5 族(`RankXGB`/`RankCat`/`RankRF`/`RankKNN`/`RankMLP`)於兩個 horizon 皆未過門。與 RankEnsemble、SeqLSTM Phase 0b 兩次先例呼應——橫斷面 Ridge 冠軍護城河深,多數挑戰者未能穩定超越;`RankSVM`(線性核)之單點真贏,方向上與「線性模型有優勢」之既有觀察一致,但**不可**外推為「Wave-A 整體贏」或「RankSVM 全 horizon 皆贏」。

**下一手未自動觸發**：`S4-DIRFAMILY-GENERALIZE` 計畫 Phase 1 之技術觸發條件（「某族 3-seed net Sharpe min 真贏 RankRidge」）已滿足,但依 FZ/GATE-keep 硬邊界,Phase 1 本身仍需另一輪 Steward 明示授權,本執行後記僅誠實記錄探針結果、不代為決定是否推進。

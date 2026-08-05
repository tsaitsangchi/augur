"""生產排序模型 — RankRidge(默認)+ 8 族挑戰者(RankGBDT/XGB/Cat/RF/SVM/KNN/MLP)。

🎯 這支在做什麼(白話):把 as-of 特徵矩陣 X(n 股 × f 特徵)fit 成「橫斷面相對強弱分數」。
   RankRidge = StandardScaler + Ridge(alpha=1.0)——**刻意與 evaluation.baseline B2_ridge 同一組態**
   (baseline.py:141-142),否則離線驗證≠上線預測雙軌漂移(複用鐵律 #12);
   其餘 7 族皆為挑戰者、須真贏才提拔(RankGBDT=LightGBM,同 baseline M1_gbdt 同參)。
   契約極薄:fit(X, y_rank) → self;predict(X) → ndarray(n,)(float、任意尺度,只看序位)。
   **`seed` 形參全族統一接受**(即便演算法本身無隨機性如 RankKNN、亦接受並忽略)——
   `train_ranker.py` dispatch 因此可對所有族一致呼叫 `est_cls(seed=seed)`,零 per-family 特判。
   SHAP/可解釋明訂不在此層(留 audit,防膨脹侵入預測 SSOT)。
守 #12(與 baseline 同組態、複用鐵律)· 隔離不變式(零 import 知識/哲學/顧問)· #15(random_state 固定可重現)。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.models.ranker              # 印用途+公開入口（唯讀）
  python -m augur.models.ranker --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import numpy as np


class RankRidge:
    """StandardScaler + Ridge(alpha=1.0)。與 evaluation.baseline B2_ridge 同組態(複用鐵律 #12)。"""

    family = "RankRidge"

    def __init__(self, alpha=1.0, seed=None):
        self.alpha = alpha
        self.seed = seed  # 忽略(Ridge 無隨機性);僅為 dispatch 統一簽名(#12)
        self._scaler = None
        self._model = None

    def fit(self, X, y_rank):
        from sklearn.linear_model import Ridge
        from sklearn.preprocessing import StandardScaler
        X = np.asarray(X, dtype=float)
        self._scaler = StandardScaler().fit(X)
        self._model = Ridge(alpha=self.alpha).fit(self._scaler.transform(X),
                                                  np.asarray(y_rank, dtype=float))
        return self

    def predict(self, X):
        if self._model is None:
            raise RuntimeError("RankRidge 未 fit")
        return self._model.predict(self._scaler.transform(np.asarray(X, dtype=float)))


class RankGBDT:
    """LightGBM 固定超參(與 baseline M1_gbdt 同參)。挑戰者:須 ≥3 seed 正增量 + 經濟同贏才提拔。"""

    family = "RankGBDT"

    def __init__(self, seed=42):
        self.seed = seed
        self._model = None

    def fit(self, X, y_rank):
        from lightgbm import LGBMRegressor
        self._model = LGBMRegressor(
            n_estimators=200, learning_rate=0.05, num_leaves=15, min_child_samples=30,
            subsample=0.8, colsample_bytree=0.8, random_state=self.seed, verbose=-1).fit(
            np.asarray(X, dtype=float), np.asarray(y_rank, dtype=float))
        return self

    def predict(self, X):
        if self._model is None:
            raise RuntimeError("RankGBDT 未 fit")
        return self._model.predict(np.asarray(X, dtype=float))


class RankXGB:
    """XGBoost 固定超參(量級比照 RankGBDT;首輪普查非調參最優)。挑戰者,須真贏才提拔。"""

    family = "RankXGB"

    def __init__(self, seed=42):
        self.seed = seed
        self._model = None

    def fit(self, X, y_rank):
        from xgboost import XGBRegressor
        # n_jobs=1:預設會搶全機核心,walk-forward 多折多 seed 序列呼叫下每折都搶滿反而執行緒
        # 過度訂閱(oversubscription)拖慢(實測:80 列 fit 於背景 CPU 競合下 >2 分未完、單執行緒 <1s)
        self._model = XGBRegressor(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, random_state=self.seed, n_jobs=1).fit(
            np.asarray(X, dtype=float), np.asarray(y_rank, dtype=float))
        return self

    def predict(self, X):
        if self._model is None:
            raise RuntimeError("RankXGB 未 fit")
        return self._model.predict(np.asarray(X, dtype=float))


class RankCat:
    """CatBoost 固定超參。`allow_writing_files=False` 必帶——否則預設寫 catboost_info/ 到 cwd 污染工作目錄。"""

    family = "RankCat"

    def __init__(self, seed=42):
        self.seed = seed
        self._model = None

    def fit(self, X, y_rank):
        from catboost import CatBoostRegressor
        self._model = CatBoostRegressor(
            iterations=200, depth=4, learning_rate=0.05, thread_count=1,
            random_state=self.seed, verbose=False, allow_writing_files=False).fit(
            np.asarray(X, dtype=float), np.asarray(y_rank, dtype=float))
        return self

    def predict(self, X):
        if self._model is None:
            raise RuntimeError("RankCat 未 fit")
        return self._model.predict(np.asarray(X, dtype=float))


class RankRF:
    """RandomForestRegressor 固定超參。挑戰者,須真贏才提拔。"""

    family = "RankRF"

    def __init__(self, seed=42):
        self.seed = seed
        self._model = None

    def fit(self, X, y_rank):
        from sklearn.ensemble import RandomForestRegressor
        self._model = RandomForestRegressor(
            n_estimators=200, max_depth=8, min_samples_leaf=10, random_state=self.seed,
            n_jobs=1).fit(  # 同 RankXGB 理由:序列 walk-forward 下單執行緒避免過度訂閱
            np.asarray(X, dtype=float), np.asarray(y_rank, dtype=float))
        return self

    def predict(self, X):
        if self._model is None:
            raise RuntimeError("RankRF 未 fit")
        return self._model.predict(np.asarray(X, dtype=float))


class RankSVM:
    """LinearSVR(非 RBF-kernel SVR)——RBF 訓練成本 O(n²–n³),多折多 seed 下不成比例;線性核近線性成本。"""

    family = "RankSVM"

    def __init__(self, seed=42):
        self.seed = seed
        self._model = None

    def fit(self, X, y_rank):
        from sklearn.svm import LinearSVR
        self._model = LinearSVR(random_state=self.seed, max_iter=5000).fit(
            np.asarray(X, dtype=float), np.asarray(y_rank, dtype=float))
        return self

    def predict(self, X):
        if self._model is None:
            raise RuntimeError("RankSVM 未 fit")
        return self._model.predict(np.asarray(X, dtype=float))


class RankKNN:
    """KNeighborsRegressor(距離加權)。確定性演算法、無 random_state——`seed` 接受但忽略(#12 統一簽名)。"""

    family = "RankKNN"

    def __init__(self, seed=42):
        self.seed = seed  # 忽略(KNN 無隨機性)
        self._model = None

    def fit(self, X, y_rank):
        from sklearn.neighbors import KNeighborsRegressor
        self._model = KNeighborsRegressor(n_neighbors=20, weights="distance").fit(
            np.asarray(X, dtype=float), np.asarray(y_rank, dtype=float))
        return self

    def predict(self, X):
        if self._model is None:
            raise RuntimeError("RankKNN 未 fit")
        return self._model.predict(np.asarray(X, dtype=float))


class RankMLP:
    """MLPRegressor 刻意淺層(單隱藏層 32 units)+ early_stopping。挑戰者,須真贏才提拔。"""

    family = "RankMLP"

    def __init__(self, seed=42):
        self.seed = seed
        self._model = None

    def fit(self, X, y_rank):
        from sklearn.neural_network import MLPRegressor
        self._model = MLPRegressor(
            hidden_layer_sizes=(32,), max_iter=300, early_stopping=True,
            random_state=self.seed).fit(
            np.asarray(X, dtype=float), np.asarray(y_rank, dtype=float))
        return self

    def predict(self, X):
        if self._model is None:
            raise RuntimeError("RankMLP 未 fit")
        return self._model.predict(np.asarray(X, dtype=float))


ALL_FAMILIES = (RankRidge, RankGBDT, RankXGB, RankCat, RankRF, RankSVM, RankKNN, RankMLP)


def _selftest():
    # 零 IO:不觸 sklearn/lightgbm/xgboost/catboost(imports 皆 lazy 在 fit/predict 內);僅結構+未 fit 守衛
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    def raises_runtime(fn):
        try:
            fn(); return False
        except RuntimeError:
            return True
        except Exception:
            return False

    chk("8 族 family 標識各異且=類名去 Rank 前綴後仍可讀", len({c.family for c in ALL_FAMILIES}) == 8)
    chk("RankRidge 默認 alpha=1.0(與 baseline B2_ridge 同組態)", RankRidge().alpha == 1.0)
    chk("RankRidge 忽略 seed(統一簽名,#12)", RankRidge(seed=99).seed == 99)
    for cls in (RankGBDT, RankXGB, RankCat, RankRF, RankSVM, RankKNN, RankMLP):
        chk(f"{cls.family} 默認 seed=42(#15 可重現)", cls().seed == 42)
    for cls in ALL_FAMILIES:
        inst = cls()
        chk(f"{cls.family} 未 fit → 無 model", getattr(inst, "_model", "MISSING") is None)
        chk(f"{cls.family} 未 fit predict 拋 RuntimeError", raises_runtime(lambda c=cls: c().predict([[1.0]])))
    chk("公開契約:8 族皆有 fit/predict", all(
        hasattr(c, "fit") and hasattr(c, "predict") for c in ALL_FAMILIES))
    chk("ALL_FAMILIES 恰 8 族(RankRidge/GBDT/XGB/Cat/RF/SVM/KNN/MLP)", len(ALL_FAMILIES) == 8)

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.models.ranker --selftest;免 DB 免 API)")

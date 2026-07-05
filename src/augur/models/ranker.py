"""生產排序模型 — RankRidge(默認)+ RankGBDT(挑戰者)。

🎯 這支在做什麼(白話):把 as-of 特徵矩陣 X(n 股 × f 特徵)fit 成「橫斷面相對強弱分數」。
   RankRidge = StandardScaler + Ridge(alpha=1.0)——**刻意與 evaluation.baseline B2_ridge 同一組態**
   (baseline.py:141-142),否則離線驗證≠上線預測雙軌漂移(複用鐵律 #12);
   RankGBDT = LightGBM 固定超參(baseline M1_gbdt 同參),挑戰者、須真贏才提拔。
   契約極薄:fit(X, y_rank) → self;predict(X) → ndarray(n,)(float、任意尺度,只看序位)。
   SHAP/可解釋明訂不在此層(留 audit,防膨脹侵入預測 SSOT)。
守 #12(與 baseline 同組態、複用鐵律)· 隔離不變式(零 import 知識/哲學/顧問)· #15(random_state 固定可重現)。
"""
from __future__ import annotations

import numpy as np


class RankRidge:
    """StandardScaler + Ridge(alpha=1.0)。與 evaluation.baseline B2_ridge 同組態(複用鐵律 #12)。"""

    family = "RankRidge"

    def __init__(self, alpha=1.0):
        self.alpha = alpha
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

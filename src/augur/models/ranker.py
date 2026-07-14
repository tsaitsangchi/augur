"""生產排序模型 — RankRidge(默認)+ RankGBDT(挑戰者)。

🎯 這支在做什麼(白話):把 as-of 特徵矩陣 X(n 股 × f 特徵)fit 成「橫斷面相對強弱分數」。
   RankRidge = StandardScaler + Ridge(alpha=1.0)——**刻意與 evaluation.baseline B2_ridge 同一組態**
   (baseline.py:141-142),否則離線驗證≠上線預測雙軌漂移(複用鐵律 #12);
   RankGBDT = LightGBM 固定超參(baseline M1_gbdt 同參),挑戰者、須真贏才提拔。
   契約極薄:fit(X, y_rank) → self;predict(X) → ndarray(n,)(float、任意尺度,只看序位)。
   SHAP/可解釋明訂不在此層(留 audit,防膨脹侵入預測 SSOT)。
守 #12(與 baseline 同組態、複用鐵律)· 隔離不變式(零 import 知識/哲學/顧問)· #15(random_state 固定可重現)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.models.ranker              # 印用途+公開入口（唯讀）
  python -m augur.models.ranker --selftest   # 純紅綠自測（零 IO）
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


def _selftest():
    # 零 IO:不觸 sklearn/lightgbm(imports 皆 lazy 在 fit/predict 內);僅結構+未 fit 守衛
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("RankRidge.family 標識", RankRidge.family == "RankRidge")
    chk("RankGBDT.family 標識", RankGBDT.family == "RankGBDT")
    chk("RankRidge 默認 alpha=1.0(與 baseline B2_ridge 同組態)", RankRidge().alpha == 1.0)
    chk("RankGBDT 默認 seed=42(#15 可重現)", RankGBDT().seed == 42)
    chk("RankRidge 未 fit → 無 model/scaler", RankRidge()._model is None and RankRidge()._scaler is None)
    chk("RankGBDT 未 fit → 無 model", RankGBDT()._model is None)

    def raises_runtime(fn):
        try:
            fn(); return False
        except RuntimeError:
            return True
        except Exception:
            return False
    chk("RankRidge 未 fit predict 拋 RuntimeError", raises_runtime(lambda: RankRidge().predict([[1.0]])))
    chk("RankGBDT 未 fit predict 拋 RuntimeError", raises_runtime(lambda: RankGBDT().predict([[1.0]])))
    chk("公開契約:兩族皆有 fit/predict", all(
        hasattr(c, "fit") and hasattr(c, "predict") for c in (RankRidge, RankGBDT)))

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.models.ranker --selftest;免 DB 免 API)")

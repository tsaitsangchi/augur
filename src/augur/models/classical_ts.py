"""古典單序列薄殼 — ARIMA／SARIMA 預測熱路徑雛形(S4-Wave-B 普查後接續 Phase 0)。

🎯 這支在做什麼(白話):給一支股的單變量報酬／價序列,fit 一個小 ARIMA,吐出未來 h 步點預測。
   **不是**橫斷面 ranker;量尺另書(方向 hit／vs naive),不得與 RankRidge #14 冠軍門混稱可交易。
   不收斂／樣本不足 → 誠實 raise／由呼叫端 SKIP,不填假預測。
守 #15(可重現 order 固定)· #12(與 sim GARCH 分尺)· Wave-B EXECUTED「套件在≠adapter」之接續。

執行指令矩陣（library #18；免 DB 免 API）:
  python -m augur.models.classical_ts              # 印用途+公開入口
  python -m augur.models.classical_ts --selftest   # 純紅綠自測（可觸 statsmodels；零 DB／零網路）
"""
from __future__ import annotations

import numpy as np


class ArimaUnivariate:
    """statsmodels ARIMA(order) 薄殼。family 名供日後 registry；本 Phase 0 不寫庫。"""

    family = "ArimaUnivariate"

    def __init__(self, order=(1, 0, 1), seed=None):
        self.order = tuple(order)
        self.seed = seed  # 忽略(ARIMA 無隨機性);統一簽名
        self._res = None

    def fit(self, series):
        from statsmodels.tsa.arima.model import ARIMA
        y = np.asarray(series, dtype=float)
        if y.ndim != 1:
            raise ValueError("ArimaUnivariate.fit 須 1d series")
        if len(y) < max(20, sum(self.order) + 5):
            raise ValueError(f"樣本過短 n={len(y)}(誠實 SKIP 上游)")
        if not np.all(np.isfinite(y)):
            raise ValueError("series 含非有限值(誠實 SKIP)")
        self._res = ARIMA(y, order=self.order).fit()
        return self

    def predict_horizon(self, h: int):
        if self._res is None:
            raise RuntimeError("ArimaUnivariate 未 fit")
        if h < 1:
            raise ValueError("h>=1")
        fc = self._res.forecast(steps=h)
        return np.asarray(fc, dtype=float)

    def predict(self, h: int = 1):
        """別名:預設 1 步;多步用 predict_horizon。"""
        return self.predict_horizon(h)


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("family 標識", ArimaUnivariate.family == "ArimaUnivariate")
    chk("未 fit → predict 拋 RuntimeError", _raises(RuntimeError, lambda: ArimaUnivariate().predict(1)))
    chk("過短序列 → ValueError(誠實 SKIP)", _raises(ValueError, lambda: ArimaUnivariate().fit([0.1, 0.2])))
    # 合成可收斂序列(確定性)
    rng = np.random.default_rng(0)
    y = np.cumsum(rng.normal(0, 0.01, size=80))
    est = ArimaUnivariate(order=(1, 0, 0)).fit(y)
    pred = est.predict_horizon(5)
    chk("forecast 長度=h", len(pred) == 5)
    chk("forecast 全有限", bool(np.all(np.isfinite(pred))))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _raises(exc, fn):
    try:
        fn()
        return False
    except exc:
        return True
    except Exception:
        return False


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.models.classical_ts --selftest;免 DB 免 API)")

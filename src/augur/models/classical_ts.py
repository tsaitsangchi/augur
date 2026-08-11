"""古典 TS 薄殼 — ARIMA／VAR／Kalman／Coint／GarchMeanDir（S4 Wave-B）。

🎯 這支在做什麼(白話):單股／小維古典預測薄殼。GarchMeanDir＝**預測臂**（均值路徑方向）,
   **不是** simulate_* 風險 GARCH，不得混稱可交易。
   不收斂／樣本不足 → 誠實 raise／由呼叫端 SKIP,不填假預測。
守 #15(可重現規格固定)· #12(與 sim GARCH 分尺)· Wave-B「套件在≠adapter」接續。

執行指令矩陣（library #18；免 DB 免 API）:
  python -m augur.models.classical_ts              # 印用途+公開入口
  python -m augur.models.classical_ts --selftest   # 純紅綠自測（可觸 statsmodels／arch；零 DB／零網路）
"""
from __future__ import annotations

import numpy as np

# NF-B-VAR 契約：Phase 0 維度上限（plan：k≤5）
VAR_K_MAX = 5
VAR_K_MIN = 2
VAR_P_DEFAULT = 1

# NF-B-KALMAN：Local Level 固定規格字面（statsmodels UnobservedComponents）
KALMAN_LEVEL = "local level"

# NF-B-COINT：Engle–Granger 對；殘差半衰期衰減（固定、非搜參）
COINT_K = 2
COINT_RHO = 0.9  # z_{t+1} ≈ rho * z_t（均值回復）

# NF-B-GARCH 預測臂：固定 GARCH(1,1)+ConstantMean
GARCH_P = 1
GARCH_Q = 1


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


class VarSmall:
    """statsmodels VAR(p) 小維薄殼（NF-B-VAR 0a）。

    輸入 panel shape=(T, k)，k∈[2,5]；輸出 forecast shape=(h, k)。
    固定小 p（預設 1）；不寫庫；不接 predict_asof。
    """

    family = "VarSmall"

    def __init__(self, p: int = VAR_P_DEFAULT, seed=None):
        if int(p) < 1:
            raise ValueError("VarSmall p>=1")
        self.p = int(p)
        self.seed = seed  # 忽略（VAR 點預測無 seed）；統一簽名
        self._res = None
        self._k = None
        self._endog = None

    def fit(self, panel):
        from statsmodels.tsa.api import VAR
        y = np.asarray(panel, dtype=float)
        if y.ndim != 2:
            raise ValueError("VarSmall.fit 須 2d panel (T,k)")
        t, k = y.shape
        if k < VAR_K_MIN or k > VAR_K_MAX:
            raise ValueError(
                f"VarSmall k 須 ∈[{VAR_K_MIN},{VAR_K_MAX}]（誠實 SKIP 上游）; got k={k}"
            )
        if t < max(40, self.p * k + 20):
            raise ValueError(f"樣本過短 T={t} k={k} p={self.p}(誠實 SKIP 上游)")
        if not np.all(np.isfinite(y)):
            raise ValueError("panel 含非有限值(誠實 SKIP)")
        self._res = VAR(y).fit(self.p)
        self._k = k
        self._endog = y
        return self

    def predict_horizon(self, h: int):
        if self._res is None or self._endog is None:
            raise RuntimeError("VarSmall 未 fit")
        if h < 1:
            raise ValueError("h>=1")
        # statsmodels: forecast(y, steps) 需最後 p 列
        y0 = self._endog[-self.p :]
        fc = self._res.forecast(y0, steps=h)
        out = np.asarray(fc, dtype=float)
        if out.shape != (h, self._k):
            raise RuntimeError(f"forecast shape 異常 {out.shape}≠{(h, self._k)}")
        if not np.all(np.isfinite(out)):
            raise ValueError("forecast 含非有限值(誠實 SKIP 上游)")
        return out

    def predict(self, h: int = 1):
        return self.predict_horizon(h)


class KalmanLocalLevel:
    """statsmodels UnobservedComponents(local level) 薄殼（NF-B-KALMAN 0a）。

    輸入 1d 序列（契約建議＝log close）；輸出 h 步 level 點預測。
    固定 level='local level'；不寫庫；不接 predict_asof。
    """

    family = "KalmanLocalLevel"

    def __init__(self, level: str = KALMAN_LEVEL, seed=None):
        if level != KALMAN_LEVEL:
            # Phase 0：禁隨意換規格當「已最佳化」
            raise ValueError(f"KalmanLocalLevel 僅允許 level={KALMAN_LEVEL!r}（誠實）")
        self.level = level
        self.seed = seed  # 忽略
        self._res = None

    def fit(self, series):
        from statsmodels.tsa.statespace.structural import UnobservedComponents
        y = np.asarray(series, dtype=float)
        if y.ndim != 1:
            raise ValueError("KalmanLocalLevel.fit 須 1d series")
        if len(y) < 40:
            raise ValueError(f"樣本過短 n={len(y)}(誠實 SKIP 上游)")
        if not np.all(np.isfinite(y)):
            raise ValueError("series 含非有限值(誠實 SKIP)")
        # MLE；disp=False；不收斂 → 例外上拋由呼叫端 SKIP
        with np.errstate(all="ignore"):
            self._res = UnobservedComponents(y, level=self.level).fit(disp=False)
        return self

    def predict_horizon(self, h: int):
        if self._res is None:
            raise RuntimeError("KalmanLocalLevel 未 fit")
        if h < 1:
            raise ValueError("h>=1")
        fc = self._res.forecast(steps=h)
        out = np.asarray(fc, dtype=float).reshape(-1)
        if len(out) != h:
            raise RuntimeError(f"forecast 長度異常 {len(out)}≠{h}")
        if not np.all(np.isfinite(out)):
            raise ValueError("forecast 含非有限值(誠實 SKIP 上游)")
        return out

    def predict(self, h: int = 1):
        return self.predict_horizon(h)


class CointPairEG:
    """Engle–Granger 成對薄殼（NF-B-COINT 0a）。

    輸入 panel shape=(T, 2)=[log y, log x]；OLS y~1+x；殘差 z 以固定 rho 均值回復，
    預測 x 水平凍結、y 沿均衡調整。不寫庫；≠可套利授權。
    """

    family = "CointPairEG"

    def __init__(self, rho: float = COINT_RHO, seed=None):
        if not (0.0 < float(rho) < 1.0):
            raise ValueError("CointPairEG rho 須 ∈(0,1)")
        self.rho = float(rho)
        self.seed = seed
        self._a = self._b = None
        self._resid_std = None
        self._last = None
        self._last_resid = None

    def fit(self, panel):
        ymat = np.asarray(panel, dtype=float)
        if ymat.ndim != 2 or ymat.shape[1] != COINT_K:
            raise ValueError(f"CointPairEG.fit 須 shape (T,{COINT_K})")
        t = ymat.shape[0]
        if t < 40:
            raise ValueError(f"樣本過短 T={t}(誠實 SKIP 上游)")
        if not np.all(np.isfinite(ymat)):
            raise ValueError("panel 含非有限值(誠實 SKIP)")
        y, x = ymat[:, 0], ymat[:, 1]
        X = np.column_stack([np.ones(t), x])
        coef, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
        if rank < 2:
            raise ValueError("OLS 秩不足(誠實 SKIP 上游)")
        resid = y - X @ coef
        std = float(np.std(resid, ddof=1))
        if not np.isfinite(std) or std < 1e-12:
            raise ValueError("殘差標準差過小(誠實 SKIP 上游)")
        self._a, self._b = float(coef[0]), float(coef[1])
        self._resid_std = std
        self._last = ymat[-1].copy()
        self._last_resid = float(resid[-1])
        return self

    def zscore(self):
        if self._last_resid is None or self._resid_std is None:
            raise RuntimeError("CointPairEG 未 fit")
        return self._last_resid / self._resid_std

    def predict_horizon(self, h: int):
        """回 (h, 2)：x 凍結 last_x；y = a+b*x + resid*rho^t（殘差均值回復）。"""
        if self._last is None or self._a is None:
            raise RuntimeError("CointPairEG 未 fit")
        if h < 1:
            raise ValueError("h>=1")
        last_x = float(self._last[1])
        out = np.empty((h, 2), dtype=float)
        resid = float(self._last_resid)
        for t in range(1, h + 1):
            resid = resid * self.rho
            x_hat = last_x
            y_hat = self._a + self._b * x_hat + resid
            out[t - 1, 0] = y_hat
            out[t - 1, 1] = x_hat
        if not np.all(np.isfinite(out)):
            raise ValueError("forecast 含非有限值(誠實 SKIP 上游)")
        return out

    def predict(self, h: int = 1):
        return self.predict_horizon(h)


class GarchMeanDir:
    """arch ConstantMean＋GARCH(1,1) 預測臂薄殼（NF-B-GARCH 0a）。

    輸入 1d **報酬**序列；輸出未來 h 步**條件均值**點預測（方向用 sum／末號）。
    **不**輸出 σ 當漲跌信號；**不**接 simulate_* 風險路徑；不寫庫。
    """

    family = "GarchMeanDir"

    def __init__(self, p: int = GARCH_P, q: int = GARCH_Q, seed=None):
        if int(p) != GARCH_P or int(q) != GARCH_Q:
            raise ValueError(f"GarchMeanDir 僅允許 GARCH({GARCH_P},{GARCH_Q})（誠實固定規格）")
        self.p = GARCH_P
        self.q = GARCH_Q
        self.seed = seed
        self._res = None

    def fit(self, series):
        from arch.univariate import ConstantMean, GARCH
        import warnings
        y = np.asarray(series, dtype=float)
        if y.ndim != 1:
            raise ValueError("GarchMeanDir.fit 須 1d returns")
        if len(y) < 60:
            raise ValueError(f"樣本過短 n={len(y)}(誠實 SKIP 上游)")
        if not np.all(np.isfinite(y)):
            raise ValueError("series 含非有限值(誠實 SKIP)")
        am = ConstantMean(y)
        am.volatility = GARCH(self.p, self.q)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._res = am.fit(disp="off")
        return self

    def predict_horizon(self, h: int):
        if self._res is None:
            raise RuntimeError("GarchMeanDir 未 fit")
        if h < 1:
            raise ValueError("h>=1")
        fc = self._res.forecast(horizon=h)
        # last row = asof forecast path
        row = fc.mean.iloc[-1].values
        out = np.asarray(row, dtype=float).reshape(-1)
        if len(out) != h:
            raise RuntimeError(f"mean forecast 長度異常 {len(out)}≠{h}")
        if not np.all(np.isfinite(out)):
            raise ValueError("forecast 含非有限值(誠實 SKIP 上游)")
        return out

    def predict(self, h: int = 1):
        return self.predict_horizon(h)


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # —— ARIMA ——
    chk("Arima family 標識", ArimaUnivariate.family == "ArimaUnivariate")
    chk("Arima 未 fit → predict 拋 RuntimeError",
        _raises(RuntimeError, lambda: ArimaUnivariate().predict(1)))
    chk("Arima 過短序列 → ValueError(誠實 SKIP)",
        _raises(ValueError, lambda: ArimaUnivariate().fit([0.1, 0.2])))
    rng = np.random.default_rng(0)
    y = np.cumsum(rng.normal(0, 0.01, size=80))
    est = ArimaUnivariate(order=(1, 0, 0)).fit(y)
    pred = est.predict_horizon(5)
    chk("Arima forecast 長度=h", len(pred) == 5)
    chk("Arima forecast 全有限", bool(np.all(np.isfinite(pred))))

    # —— VarSmall（0a）——
    chk("VarSmall family 標識", VarSmall.family == "VarSmall")
    chk("VarSmall 未 fit → RuntimeError",
        _raises(RuntimeError, lambda: VarSmall().predict(1)))
    chk("VarSmall k=1 → ValueError",
        _raises(ValueError, lambda: VarSmall().fit(rng.normal(size=(80, 1)))))
    chk("VarSmall k=6 → ValueError",
        _raises(ValueError, lambda: VarSmall().fit(rng.normal(size=(80, 6)))))
    chk("VarSmall 過短 T → ValueError",
        _raises(ValueError, lambda: VarSmall(p=1).fit(rng.normal(size=(10, 3)))))
    panel = rng.normal(0, 0.01, size=(120, 3))
    var = VarSmall(p=1).fit(panel)
    vpred = var.predict_horizon(5)
    chk("VarSmall forecast shape=(h,k)", vpred.shape == (5, 3))
    chk("VarSmall forecast 全有限", bool(np.all(np.isfinite(vpred))))
    chk("VAR_K_MAX==5", VAR_K_MAX == 5)

    # —— KalmanLocalLevel（0a）——
    chk("Kalman family 標識", KalmanLocalLevel.family == "KalmanLocalLevel")
    chk("Kalman 未 fit → RuntimeError",
        _raises(RuntimeError, lambda: KalmanLocalLevel().predict(1)))
    chk("Kalman 過短 → ValueError",
        _raises(ValueError, lambda: KalmanLocalLevel().fit([1.0, 2.0])))
    chk("Kalman 禁改 level 規格",
        _raises(ValueError, lambda: KalmanLocalLevel(level="local linear trend")))
    logp = np.cumsum(rng.normal(0, 0.01, size=100)) + 4.0
    kal = KalmanLocalLevel().fit(logp)
    kpred = kal.predict_horizon(5)
    chk("Kalman forecast 長度=h", len(kpred) == 5)
    chk("Kalman forecast 全有限", bool(np.all(np.isfinite(kpred))))
    chk("KALMAN_LEVEL 釘死", KALMAN_LEVEL == "local level")

    # —— CointPairEG（0a）——
    chk("Coint family 標識", CointPairEG.family == "CointPairEG")
    chk("Coint 未 fit → RuntimeError",
        _raises(RuntimeError, lambda: CointPairEG().predict(1)))
    chk("Coint k≠2 → ValueError",
        _raises(ValueError, lambda: CointPairEG().fit(rng.normal(size=(80, 3)))))
    chk("Coint 過短 → ValueError",
        _raises(ValueError, lambda: CointPairEG().fit(rng.normal(size=(10, 2)))))
    x = np.cumsum(rng.normal(0, 0.01, size=120))
    ypair = 0.5 + 1.2 * x + rng.normal(0, 0.005, size=120)
    pair = np.column_stack([ypair, x])
    cg = CointPairEG().fit(pair)
    cpred = cg.predict_horizon(5)
    chk("Coint forecast shape=(h,2)", cpred.shape == (5, 2))
    chk("Coint forecast 全有限", bool(np.all(np.isfinite(cpred))))
    chk("Coint zscore 有限", np.isfinite(cg.zscore()))
    chk("COINT_K==2", COINT_K == 2)

    # —— GarchMeanDir（0a 預測臂）——
    chk("Garch family 標識", GarchMeanDir.family == "GarchMeanDir")
    chk("Garch 未 fit → RuntimeError",
        _raises(RuntimeError, lambda: GarchMeanDir().predict(1)))
    chk("Garch 過短 → ValueError",
        _raises(ValueError, lambda: GarchMeanDir().fit(rng.normal(size=20))))
    chk("Garch 禁改階",
        _raises(ValueError, lambda: GarchMeanDir(p=2, q=1)))
    # 給一點波動簇使 GARCH 可辨識
    e = rng.normal(0, 1.0, size=250)
    vol = np.ones(250)
    for t in range(1, 250):
        vol[t] = np.sqrt(0.0001 + 0.05 * (e[t - 1] ** 2) + 0.9 * vol[t - 1] ** 2)
    rets = e * vol * 0.01
    gch = GarchMeanDir().fit(rets)
    gpred = gch.predict_horizon(5)
    chk("Garch mean forecast 長度=h", len(gpred) == 5)
    chk("Garch mean forecast 全有限", bool(np.all(np.isfinite(gpred))))
    chk("GARCH_P/Q==1", GARCH_P == 1 and GARCH_Q == 1)

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
    print("公開: ArimaUnivariate, VarSmall, KalmanLocalLevel, CointPairEG, GarchMeanDir")

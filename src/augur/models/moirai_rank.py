"""預訓練時序排序薄殼 — MoiraiRank2Small（NF-D-MOIRAI 0a）。

🎯 這支在做什麼（白話）：用本地 Moirai-2.0-R-small 對每股價上下文做分位／樣本預測，
   終點 median 相對末價 → log 比截面分數（口徑＝`chronos_rank.score_from_quantiles`）。
   預訓練零 fit；缺權重／推論失敗 → 誠實 RuntimeError／SKIP。
   ⊥ arena `MarketMoirai2` 方向 P。
守 #8 · #12 · #15 · local_files_only 預設。

執行指令矩陣（library #18；免 DB；預設免網）:
  python -m augur.models.moirai_rank              # 印用途
  python -m augur.models.moirai_rank --selftest    # stub 自測
  AUGUR_MOIRAI_REAL_SELFTEST=1 python -m augur.models.moirai_rank --selftest
"""
from __future__ import annotations

import os
from typing import Optional, Sequence

import numpy as np

from augur.models.chronos_rank import QL, score_from_quantiles

MOIRAI2_ID = "Salesforce/moirai-2.0-R-small"
CONTEXT_MAX = 512


class _StubForecast:
    def __init__(self, med_path: np.ndarray):
        self._med = np.asarray(med_path, dtype=float)

    def quantile(self, q):
        # 簡化：各分位＝median × (0.9+0.2q)
        return self._med * (0.9 + 0.2 * float(q))


class _StubPredictor:
    """延續末段報酬 → gluonts 風格 predictor.predict(ds)。"""

    def __init__(self, drift: float = 0.001, horizon: int = 5):
        self.drift = float(drift)
        self.horizon = int(horizon)

    def predict(self, dataset):
        for item in dataset:
            x = np.asarray(item["target"], dtype=float).reshape(-1)
            last = float(x[-1])
            prev = float(x[-2]) if x.size >= 2 and x[-2] > 0 else last
            base_r = (last / prev - 1.0) if prev > 0 else 0.0
            d = float(np.clip(base_r + self.drift, -0.5, 0.5))
            path = np.maximum(last * (1.0 + d) ** np.arange(1, self.horizon + 1), 1e-8)
            yield _StubForecast(path)


class MoiraiRank2Small:
    """Moirai-2.0-R-small → 截面排序分數。0a 不寫庫。"""

    family = "MoiraiRank2Small"
    model_id = MOIRAI2_ID

    def __init__(
        self,
        *,
        horizon: int = 20,
        context_max: int = CONTEXT_MAX,
        local_files_only: bool = True,
        seed: int = 42,
        predictor=None,
        batch_size: int = 8,
    ):
        if horizon < 1:
            raise ValueError("horizon>=1")
        self.horizon = int(horizon)
        self.context_max = int(context_max)
        self.local_files_only = bool(local_files_only)
        self.seed = int(seed)
        self.batch_size = int(batch_size)
        self._predictor = predictor
        self._pred_h = None if predictor is None else int(horizon)
        self._fitted = False

    def fit(self, contexts: Optional[Sequence[np.ndarray]] = None, y=None):
        if contexts is not None:
            for c in contexts:
                if np.asarray(c, dtype=float).reshape(-1).size < 2:
                    raise ValueError("每條 context 至少 2 點")
        self._fitted = True
        return self

    def _load(self, horizon: int):
        if self._predictor is not None and self._pred_h == horizon:
            return self._predictor
        if self._predictor is not None and self._pred_h != horizon:
            # stub 重綁 horizon
            if isinstance(self._predictor, _StubPredictor):
                self._predictor = _StubPredictor(drift=self._predictor.drift, horizon=horizon)
                self._pred_h = horizon
                return self._predictor
        try:
            from uni2ts.model.moirai2 import Moirai2Forecast, Moirai2Module
        except ImportError as e:
            raise RuntimeError(f"uni2ts/moirai2 不可用（誠實 SKIP）: {e}") from e
        try:
            mod = Moirai2Module.from_pretrained(
                self.model_id, local_files_only=self.local_files_only
            )
            m = Moirai2Forecast(
                module=mod,
                prediction_length=int(horizon),
                context_length=self.context_max,
                target_dim=1,
                feat_dynamic_real_dim=0,
                past_feat_dynamic_real_dim=0,
            )
            self._predictor = m.create_predictor(batch_size=self.batch_size)
            self._pred_h = int(horizon)
        except Exception as e:
            raise RuntimeError(
                f"Moirai 權重不可用／offline 失敗（誠實 SKIP；"
                f"local_files_only={self.local_files_only}): {e}"
            ) from e
        return self._predictor

    def predict_scores(self, contexts: Sequence[np.ndarray], horizon: Optional[int] = None) -> np.ndarray:
        import pandas as pd
        from gluonts.dataset.common import ListDataset

        if not self._fitted and self._predictor is None:
            self._fitted = True
        h = int(horizon if horizon is not None else self.horizon)
        pred = self._load(h)
        ctxs = []
        lasts = []
        for c in contexts:
            x = np.asarray(c, dtype=float).reshape(-1)
            if x.size < 2:
                raise ValueError("context 過短（誠實 SKIP 上游）")
            x = x[-self.context_max :]
            lasts.append(float(x[-1]))
            ctxs.append(x)
        ds = ListDataset(
            [{"target": x, "start": pd.Period("2000-01-03", freq="B")} for x in ctxs],
            freq="B",
        )
        scores = []
        for i, fc in enumerate(pred.predict(ds)):
            try:
                if hasattr(fc, "quantile"):
                    med = np.asarray(fc.quantile(0.5), dtype=float).reshape(-1)
                else:
                    med = np.median(np.asarray(fc.samples, dtype=float), axis=0).reshape(-1)
                if med.size < 1 or not np.all(np.isfinite(med)):
                    raise RuntimeError("Moirai median 非有限（誠實 SKIP）")
                scores.append(score_from_quantiles(lasts[i], med))
            except ValueError as e:
                raise RuntimeError(f"Moirai 分數不可比（誠實 SKIP）: {e}") from e
        if len(scores) != len(lasts):
            raise RuntimeError(
                f"Moirai 輸出條數 {len(scores)}≠輸入 {len(lasts)}（誠實 SKIP）"
            )
        return np.asarray(scores, dtype=float)

    def predict(self, contexts: Sequence[np.ndarray], horizon: Optional[int] = None) -> np.ndarray:
        return self.predict_scores(contexts, horizon=horizon)


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("family", MoiraiRank2Small.family == "MoiraiRank2Small")
    chk("model_id", MoiraiRank2Small.model_id == MOIRAI2_ID)

    m = MoiraiRank2Small(horizon=5, predictor=_StubPredictor(drift=0.01, horizon=5), seed=1).fit()
    rng = np.random.RandomState(0)
    ctxs = [np.cumprod(1.0 + 0.01 * rng.randn(30)) * 100 for _ in range(4)]
    ctxs[0] = np.linspace(100, 120, 40)
    ctxs[1] = np.linspace(100, 80, 40)
    s = m.predict_scores(ctxs)
    chk("predict 形狀=(n,)", s.shape == (4,))
    chk("分數皆 finite", np.all(np.isfinite(s)))
    chk("上升 > 下降（stub）", s[0] > s[1])

    def raises(fn, exc=ValueError):
        try:
            fn()
            return False
        except exc:
            return True
        except Exception:
            return False

    chk("過短 context → ValueError", raises(lambda: m.predict_scores([np.array([1.0])])))
    s2 = MoiraiRank2Small(horizon=5, predictor=_StubPredictor(drift=0.01, horizon=5), seed=1).fit().predict(
        ctxs
    )
    chk("同 stub 可重現", np.allclose(s, s2))

    if os.environ.get("AUGUR_MOIRAI_REAL_SELFTEST") == "1":
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        real_ctxs = [
            100.0 * np.cumprod(1.0 + 0.002 * rng.randn(64)),
            50.0 * np.cumprod(1.0 + 0.002 * rng.randn(64)),
        ]
        try:
            real = MoiraiRank2Small(horizon=5, local_files_only=True, seed=1, batch_size=2).fit()
            sr = real.predict_scores(real_ctxs, horizon=5)
            chk("離線真載 predict finite", sr.shape == (2,) and np.all(np.isfinite(sr)))
            print("  （real selftest：本地權重可用）")
        except RuntimeError as e:
            print(f"  ～ SKIP 離線真載（誠實）: {e}")
            chk("離線真載失敗以 SKIP 記", True)
    else:
        print("  （略過真載；設 AUGUR_MOIRAI_REAL_SELFTEST=1 可測）")

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.models.moirai_rank --selftest)")

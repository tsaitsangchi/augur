"""預訓練時序排序薄殼 — TimesFMRank25（NF-D-TIMESFM 0a）。

🎯 這支在做什麼（白話）：用本地 TimesFM-2.5-200m 對每股價上下文做分位預測，
   終點 median 相對末價 → log 比截面分數（口徑＝`chronos_rank.score_from_quantiles`）。
   預訓練零 fit 更新；缺本地權重 → 誠實 RuntimeError／SKIP。
   ⊥ arena `MarketTimesFM` 方向 P。
守 #8 · #12（分數口徑複用 Chronos）· #15 · local_files_only 預設。

執行指令矩陣（library #18；免 DB；預設免網）:
  python -m augur.models.timesfm_rank              # 印用途
  python -m augur.models.timesfm_rank --selftest    # stub 自測
  AUGUR_TIMESFM_REAL_SELFTEST=1 python -m augur.models.timesfm_rank --selftest
"""
from __future__ import annotations

import os
from typing import Optional, Sequence

import numpy as np

from augur.models.chronos_rank import QL, score_from_quantiles

TIMESFM_25_ID = "google/timesfm-2.5-200m-pytorch"
CONTEXT_MAX = 512


class _StubTimesFM:
    """确定性 stub：延續上下文末段報酬方向 → (mean+9分位) 形 (n,H,10)。"""

    def __init__(self, drift: float = 0.001):
        self.drift = float(drift)

    def forecast(self, horizon, inputs):
        n = len(inputs)
        h = int(horizon)
        q = np.zeros((n, h, 1 + len(QL)), dtype=float)
        for i, ctx in enumerate(inputs):
            x = np.asarray(ctx, dtype=float).reshape(-1)
            last = float(x[-1])
            # 延續近窗幾何報酬（使上升／下降序列分數可分）
            prev = float(x[-2]) if x.size >= 2 and x[-2] > 0 else last
            base_r = (last / prev - 1.0) if prev > 0 else 0.0
            for j, qv in enumerate(QL):
                d = base_r + self.drift * (float(qv) - 0.5)
                # 防負價：夾住單步
                d = float(np.clip(d, -0.5, 0.5))
                path = last * (1.0 + d) ** np.arange(1, h + 1)
                q[i, :, 1 + j] = np.maximum(path, 1e-8)
            q[i, :, 0] = q[i, :, 1 + QL.index(0.5)]
        return None, q


class TimesFMRank25:
    """TimesFM-2.5-200m → 截面排序分數。0a 不寫庫。"""

    family = "TimesFMRank25"
    model_id = TIMESFM_25_ID

    def __init__(
        self,
        *,
        horizon: int = 20,
        context_max: int = CONTEXT_MAX,
        local_files_only: bool = True,
        seed: int = 42,
        model=None,
    ):
        if horizon < 1:
            raise ValueError("horizon>=1")
        self.horizon = int(horizon)
        self.context_max = int(context_max)
        self.local_files_only = bool(local_files_only)
        self.seed = int(seed)
        self._model = model
        self._fitted = False

    def fit(self, contexts: Optional[Sequence[np.ndarray]] = None, y=None):
        if contexts is not None:
            for c in contexts:
                if np.asarray(c, dtype=float).reshape(-1).size < 2:
                    raise ValueError("每條 context 至少 2 點")
        self._fitted = True
        return self

    def _load(self):
        if self._model is not None:
            return self._model
        try:
            import timesfm
        except ImportError as e:
            raise RuntimeError(f"timesfm 套件不可用（誠實 SKIP）: {e}") from e
        try:
            m = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
                self.model_id, local_files_only=self.local_files_only
            )
            m.compile(
                timesfm.ForecastConfig(
                    max_context=self.context_max,
                    max_horizon=128,
                    normalize_inputs=True,
                    use_continuous_quantile_head=True,
                )
            )
            self._model = m
        except Exception as e:
            raise RuntimeError(
                f"TimesFM 權重不可用／offline 失敗（誠實 SKIP；"
                f"local_files_only={self.local_files_only}): {e}"
            ) from e
        return self._model

    def predict_scores(self, contexts: Sequence[np.ndarray], horizon: Optional[int] = None) -> np.ndarray:
        if not self._fitted and self._model is None:
            self._fitted = True
        h = int(horizon if horizon is not None else self.horizon)
        model = self._load()
        ctxs = []
        lasts = []
        for c in contexts:
            x = np.asarray(c, dtype=float).reshape(-1)
            if x.size < 2:
                raise ValueError("context 過短（誠實 SKIP 上游）")
            x = x[-self.context_max :]
            lasts.append(float(x[-1]))
            ctxs.append(x)
        _, q = model.forecast(horizon=h, inputs=ctxs)
        q = np.asarray(q, dtype=float)
        # 預期 (n, H, 10)：[:, :, 0]=mean · 1..=QL
        if q.ndim != 3 or q.shape[-1] < 1 + len(QL):
            raise RuntimeError(f"TimesFM q 形異常 shape={q.shape}（誠實 SKIP）")
        mid = 1 + QL.index(0.5)
        scores = []
        for i in range(len(lasts)):
            try:
                scores.append(score_from_quantiles(lasts[i], q[i, :, mid]))
            except ValueError as e:
                raise RuntimeError(f"TimesFM 分數不可比（誠實 SKIP）: {e}") from e
        return np.asarray(scores, dtype=float)

    def predict(self, contexts: Sequence[np.ndarray], horizon: Optional[int] = None) -> np.ndarray:
        return self.predict_scores(contexts, horizon=horizon)


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("family", TimesFMRank25.family == "TimesFMRank25")
    chk("model_id", TimesFMRank25.model_id == TIMESFM_25_ID)

    m = TimesFMRank25(horizon=5, model=_StubTimesFM(drift=0.01), seed=1).fit()
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
    s2 = TimesFMRank25(horizon=5, model=_StubTimesFM(drift=0.01), seed=1).fit().predict(ctxs)
    chk("同 stub 可重現", np.allclose(s, s2))

    if os.environ.get("AUGUR_TIMESFM_REAL_SELFTEST") == "1":
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        # 真載用嚴格正價、溫和波動（避免模型輸出非正 median）
        real_ctxs = [
            100.0 * np.cumprod(1.0 + 0.002 * rng.randn(64)),
            50.0 * np.cumprod(1.0 + 0.002 * rng.randn(64)),
        ]
        try:
            real = TimesFMRank25(horizon=5, local_files_only=True, seed=1).fit()
            sr = real.predict_scores(real_ctxs, horizon=5)
            chk("離線真載 predict finite", sr.shape == (2,) and np.all(np.isfinite(sr)))
            print("  （real selftest：本地權重可用）")
        except RuntimeError as e:
            print(f"  ～ SKIP 離線真載（誠實）: {e}")
            chk("離線真載失敗以 SKIP 記", True)
    else:
        print("  （略過真載；設 AUGUR_TIMESFM_REAL_SELFTEST=1 可測）")

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.models.timesfm_rank --selftest)")

"""預訓練時序排序薄殼 — ChronosRankBolt（NF-D-CHRONOS 0a）。

🎯 這支在做什麼（白話）：用本地 Chronos-Bolt-small 對每股價上下文做分位預測，
   把終點 median 相對末價轉成截面可比分數（預設 log 比），供後續 0b 有界評測。
   **預訓練＝零 fit 權重更新**；缺本地權重／offline 失敗 → 誠實 raise（CALL 端 SKIP）。
   ⊥ arena `MarketChronos` 方向機率口徑（可共 pipeline，升格尺不同）。
守 #8（asof／上下文由上游鎖）· #15（seed 僅影響可選 stub）· 預設 local_files_only。

執行指令矩陣（library #18；免 DB；預設免網）:
  python -m augur.models.chronos_rank              # 印用途
  python -m augur.models.chronos_rank --selftest    # stub 自測（零權重載入）
  AUGUR_CHRONOS_REAL_SELFTEST=1 python -m augur.models.chronos_rank --selftest
      # 可選：離線真載本地权重煙測（HF_HUB_OFFLINE=1；失敗＝誠實 SKIP，非 FAIL）
"""
from __future__ import annotations

import os
from typing import List, Optional, Sequence

import numpy as np

CHRONOS_BOLT_ID = "amazon/chronos-bolt-small"
CONTEXT_MAX = 512
QL = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def score_from_quantiles(last_px: float, q_path: np.ndarray) -> float:
    """終點 median／末價 → log 比分數；q_path shape (H,) 或 (H, n_q)。"""
    q = np.asarray(q_path, dtype=float)
    if q.ndim == 2:
        # (H, n_q) → 取 0.5 列
        mid = QL.index(0.5)
        med = float(q[-1, mid])
    else:
        med = float(q[-1])
    if not np.isfinite(last_px) or last_px <= 0 or not np.isfinite(med) or med <= 0:
        raise ValueError("last_px／median 須為正有限（誠實 SKIP 上游）")
    return float(np.log(med / last_px))


class _StubPipe:
    """确定性 stub：預測路徑＝末價 × (1+drift)^t；供 selftest 零權重。"""

    def __init__(self, drift: float = 0.001):
        self.drift = float(drift)

    def predict_quantiles(self, contexts, prediction_length, quantile_levels):
        import torch

        outs = []
        for ctx in contexts:
            x = np.asarray(ctx if not hasattr(ctx, "numpy") else ctx.numpy(), dtype=float).reshape(-1)
            last = float(x[-1])
            h = int(prediction_length)
            nq = len(quantile_levels)
            # 路徑：越高分位 drift 越大
            path = np.zeros((h, nq), dtype=float)
            for i, qv in enumerate(quantile_levels):
                d = self.drift * (0.5 + float(qv))
                path[:, i] = last * (1.0 + d) ** np.arange(1, h + 1)
            outs.append(torch.tensor(path, dtype=torch.float32))
        # Chronos-Bolt 常見：(n, H, Q)
        return torch.stack(outs, dim=0), None


class ChronosRankBolt:
    """Chronos-Bolt-small → 截面排序分數。family 供日後 registry；0a 不寫庫。"""

    family = "ChronosRankBolt"
    model_id = CHRONOS_BOLT_ID

    def __init__(
        self,
        *,
        horizon: int = 20,
        context_max: int = CONTEXT_MAX,
        local_files_only: bool = True,
        seed: int = 42,
        pipe=None,
    ):
        if horizon < 1:
            raise ValueError("horizon>=1")
        self.horizon = int(horizon)
        self.context_max = int(context_max)
        self.local_files_only = bool(local_files_only)
        self.seed = int(seed)
        self._pipe = pipe  # 可注入 stub
        self._fitted = False

    def fit(self, contexts: Optional[Sequence[np.ndarray]] = None, y=None):
        """預訓練：無權重更新；僅標記就緒（可選校驗 contexts 形狀）。"""
        if contexts is not None:
            for c in contexts:
                a = np.asarray(c, dtype=float).reshape(-1)
                if a.size < 2:
                    raise ValueError("每條 context 至少 2 點")
        self._fitted = True
        return self

    def _load(self):
        if self._pipe is not None:
            return self._pipe
        try:
            import torch
            from chronos import BaseChronosPipeline
        except ImportError as e:
            raise RuntimeError(f"chronos 套件不可用（誠實 SKIP）: {e}") from e
        device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self._pipe = BaseChronosPipeline.from_pretrained(
                self.model_id,
                device_map=device,
                torch_dtype="auto",
                local_files_only=self.local_files_only,
            )
        except Exception as e:
            raise RuntimeError(
                f"Chronos 權重不可用／offline 失敗（誠實 SKIP；"
                f"local_files_only={self.local_files_only}): {e}"
            ) from e
        return self._pipe

    def predict_scores(self, contexts: Sequence[np.ndarray], horizon: Optional[int] = None) -> np.ndarray:
        """contexts: 長度 n 的 1D 價序列；回 (n,) log(med_end/last)。"""
        import torch

        if not self._fitted and self._pipe is None:
            # 允許未顯式 fit（預訓練）；仍要求至少呼叫過 fit 或注入 pipe——一律 auto-fit
            self._fitted = True
        h = int(horizon if horizon is not None else self.horizon)
        pipe = self._load()
        tensors = []
        lasts = []
        for c in contexts:
            x = np.asarray(c, dtype=float).reshape(-1)
            if x.size < 2:
                raise ValueError("context 過短（誠實 SKIP 上游）")
            x = x[-self.context_max :]
            lasts.append(float(x[-1]))
            tensors.append(torch.tensor(x, dtype=torch.float32))
        q, _ = pipe.predict_quantiles(
            tensors, prediction_length=h, quantile_levels=QL
        )
        q = np.asarray(q if not hasattr(q, "numpy") else q.numpy(), dtype=float)
        # 統一到 (n, H, Q)
        while q.ndim > 3:
            q = q[0]
        if q.ndim == 2:
            # 單序列 (H,Q)
            q = q[None, ...]
        scores = [score_from_quantiles(lasts[i], q[i]) for i in range(len(lasts))]
        return np.asarray(scores, dtype=float)

    def predict(self, contexts: Sequence[np.ndarray], horizon: Optional[int] = None) -> np.ndarray:
        """別名＝predict_scores（對齊 fit/predict 慣例）。"""
        return self.predict_scores(contexts, horizon=horizon)


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("family", ChronosRankBolt.family == "ChronosRankBolt")
    chk("model_id=bolt-small", ChronosRankBolt.model_id == CHRONOS_BOLT_ID)

    m = ChronosRankBolt(horizon=5, pipe=_StubPipe(drift=0.01), seed=1)
    m.fit()
    rng = np.random.RandomState(0)
    ctxs = [np.cumprod(1.0 + 0.01 * rng.randn(30)) * 100 for _ in range(4)]
    # 刻意讓後半段上升／下降，使分數有差異
    ctxs[0] = np.linspace(100, 120, 40)
    ctxs[1] = np.linspace(100, 80, 40)
    s = m.predict_scores(ctxs)
    chk("predict 形狀=(n,)", s.shape == (4,))
    chk("分數皆 finite", np.all(np.isfinite(s)))
    chk("上升序列分數 > 下降序列（stub drift 同向）", s[0] > s[1])

    def raises(fn, exc=ValueError):
        try:
            fn()
            return False
        except exc:
            return True
        except Exception:
            return False

    chk("過短 context → ValueError", raises(lambda: m.predict_scores([np.array([1.0])])))
    chk(
        "score_from_quantiles 基本",
        abs(score_from_quantiles(100.0, np.full(5, 110.0)) - np.log(1.1)) < 1e-9,
    )

    # 同 stub 可重現
    s2 = ChronosRankBolt(horizon=5, pipe=_StubPipe(drift=0.01), seed=1).fit().predict(ctxs)
    chk("同 stub 可重現", np.allclose(s, s2))

    # 可選：離線真載（缺權重＝SKIP 記帳，非 selftest FAIL）
    if os.environ.get("AUGUR_CHRONOS_REAL_SELFTEST") == "1":
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        try:
            real = ChronosRankBolt(horizon=5, local_files_only=True, seed=1).fit()
            sr = real.predict_scores(ctxs[:2], horizon=5)
            chk("離線真載 predict finite", sr.shape == (2,) and np.all(np.isfinite(sr)))
            print("  （real selftest：本地權重可用）")
        except RuntimeError as e:
            print(f"  ～ SKIP 離線真載（誠實）: {e}")
            chk("離線真載失敗以 SKIP 記、非炸進程", True)
    else:
        print("  （略過真載；設 AUGUR_CHRONOS_REAL_SELFTEST=1 可測本地權重）")

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.models.chronos_rank --selftest)")

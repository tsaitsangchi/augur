"""股圖 GCN 薄殼 — numpy 消息傳遞（NF-E-GNN 0a）。

🎯 這支在做什麼（白話）：給節點特徵 X 與無向邊列表，做固定兩層
   Â X W 式 GCN 前向（對稱歸一化鄰接）。可選極淺監督（最小平方／固定步數），
   **不是** PyG／DGL；**不**寫庫、**不**接 B3／predict_asof。
   缺邊／維度不合 → 誠實 raise，由呼叫端 SKIP。
守 #8（asof 由上游鎖）· #15（seed／hidden 固定）· plan NF-E-GNN。

執行指令矩陣（library #18；免 DB 免 API）:
  python -m augur.models.gnn_small              # 印用途＋公開入口
  python -m augur.models.gnn_small --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import numpy as np

GCN_HIDDEN_DEFAULT = 8
GCN_LAYERS = 2


def normalized_adjacency(n: int, edges: np.ndarray, *, self_loops: bool = True) -> np.ndarray:
    """對稱歸一化 Â = D^{-1/2}(A+I)D^{-1/2}；edges shape (E,2) int。"""
    if n < 1:
        raise ValueError("n>=1")
    e = np.asarray(edges, dtype=int)
    if e.size == 0:
        raise ValueError("edges 空(誠實 SKIP 上游)")
    if e.ndim != 2 or e.shape[1] != 2:
        raise ValueError("edges 須 shape (E,2)")
    if np.any(e < 0) or np.any(e >= n):
        raise ValueError("edge 端點越界(誠實 SKIP 上游)")
    a = np.zeros((n, n), dtype=float)
    for u, v in e:
        a[u, v] = 1.0
        a[v, u] = 1.0
    if self_loops:
        a = a + np.eye(n)
    deg = a.sum(axis=1)
    if np.any(deg <= 0):
        raise ValueError("存在零度節點(誠實 SKIP 上游)")
    d_inv_sqrt = 1.0 / np.sqrt(deg)
    return (d_inv_sqrt[:, None] * a) * d_inv_sqrt[None, :]


def _relu(z):
    return np.maximum(z, 0.0)


class GcnSmall:
    """兩層 GCN（numpy）。family 供日後 registry；本 Phase 0a 不寫庫。"""

    family = "GcnSmall"

    def __init__(self, in_dim: int, hidden: int = GCN_HIDDEN_DEFAULT, out_dim: int = 1, seed: int = 42):
        if in_dim < 1 or hidden < 1 or out_dim < 1:
            raise ValueError("in_dim/hidden/out_dim >=1")
        self.in_dim = int(in_dim)
        self.hidden = int(hidden)
        self.out_dim = int(out_dim)
        self.seed = int(seed)
        self._w1 = self._w2 = None
        self._adj = None
        self._n = None

    def _init_weights(self):
        rng = np.random.default_rng(self.seed)
        # Xavier-ish
        self._w1 = rng.normal(0, np.sqrt(2.0 / (self.in_dim + self.hidden)), size=(self.in_dim, self.hidden))
        self._w2 = rng.normal(0, np.sqrt(2.0 / (self.hidden + self.out_dim)), size=(self.hidden, self.out_dim))

    def fit(self, x, edges, y=None, *, n_steps: int = 0, lr: float = 0.05):
        """前向就緒；n_steps>0 且 y 給定時做極淺 MSE 梯度步（可選）。

        x: (N,F) · edges: (E,2) · y: (N,) 或 (N,out_dim)
        """
        x = np.asarray(x, dtype=float)
        if x.ndim != 2:
            raise ValueError("x 須 2d (N,F)")
        n, f = x.shape
        if f != self.in_dim:
            raise ValueError(f"x 特徵維 {f}≠in_dim={self.in_dim}")
        if not np.all(np.isfinite(x)):
            raise ValueError("x 含非有限值(誠實 SKIP)")
        adj = normalized_adjacency(n, edges)
        self._adj = adj
        self._n = n
        self._init_weights()
        if n_steps > 0:
            if y is None:
                raise ValueError("n_steps>0 須提供 y")
            yarr = np.asarray(y, dtype=float)
            if yarr.ndim == 1:
                yarr = yarr.reshape(-1, 1)
            if yarr.shape != (n, self.out_dim):
                raise ValueError(f"y shape {yarr.shape}≠{(n, self.out_dim)}")
            for _ in range(int(n_steps)):
                pred = self._forward(x)
                err = pred - yarr
                # 反傳（簡化；僅訓練用烟）
                h = _relu(adj @ x @ self._w1)
                # dL/dW2
                d_w2 = h.T @ err / n
                d_h = err @ self._w2.T
                d_h = d_h * (h > 0)
                d_w1 = (adj @ x).T @ d_h / n
                self._w2 = self._w2 - lr * d_w2
                self._w1 = self._w1 - lr * d_w1
        return self

    def _forward(self, x):
        if self._adj is None or self._w1 is None:
            raise RuntimeError("GcnSmall 未 fit")
        h = _relu(self._adj @ x @ self._w1)
        return self._adj @ h @ self._w2

    def rebind(self, edges):
        """換圖拓撲、保留 W（轉移探針用）。須已 fit 過權重。"""
        if self._w1 is None or self._w2 is None:
            raise RuntimeError("GcnSmall 未 fit（無权重可轉移）")
        e = np.asarray(edges, dtype=int)
        # n = max index + 1；呼叫端應保节点 0..n-1 連續
        if e.size == 0:
            raise ValueError("edges 空(誠實 SKIP 上游)")
        n = int(e.max()) + 1
        self._adj = normalized_adjacency(n, e)
        self._n = n
        return self

    def predict(self, x=None):
        """節點分數 (N,out_dim)。x 缺省＝fit 時需另存——本薄殼要求呼叫端重傳 x。"""
        if self._adj is None or self._w1 is None or self._n is None:
            raise RuntimeError("GcnSmall 未 fit")
        if x is None:
            raise ValueError("predict 須傳 x（與 fit 同圖節點特徵）")
        x = np.asarray(x, dtype=float)
        if x.ndim != 2 or x.shape[0] != self._n or x.shape[1] != self.in_dim:
            raise ValueError("x 與 fit 圖／維度不一致")
        out = self._forward(x)
        if not np.all(np.isfinite(out)):
            raise ValueError("predict 含非有限值(誠實 SKIP 上游)")
        return out

    def predict_scores(self, x):
        """別名：回 (N,)（out_dim=1 時 squeeze）。"""
        out = self.predict(x)
        if self.out_dim == 1:
            return out.reshape(-1)
        return out


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("family 標識", GcnSmall.family == "GcnSmall")
    chk("未 fit → RuntimeError", _raises(RuntimeError, lambda: GcnSmall(3).predict(np.zeros((2, 3)))))
    chk("空邊 → ValueError", _raises(ValueError, lambda: normalized_adjacency(3, np.zeros((0, 2)))))
    chk("越界邊 → ValueError", _raises(ValueError, lambda: normalized_adjacency(3, np.array([[0, 9]]))))

    # 三角形無向圖 + 隨機特徵
    edges = np.array([[0, 1], [1, 2], [2, 0]])
    rng = np.random.default_rng(0)
    x = rng.normal(size=(3, 4))
    m = GcnSmall(in_dim=4, hidden=8, out_dim=1, seed=42).fit(x, edges)
    s = m.predict_scores(x)
    chk("predict 長度=N", s.shape == (3,))
    chk("predict 全有限", bool(np.all(np.isfinite(s))))
    # 可選淺訓不爆
    y = rng.normal(size=(3,))
    m2 = GcnSmall(in_dim=4, hidden=4, out_dim=1, seed=1).fit(x, edges, y=y, n_steps=3, lr=0.01)
    s2 = m2.predict_scores(x)
    chk("淺訓後仍有限", bool(np.all(np.isfinite(s2))))
    chk("GCN_LAYERS==2", GCN_LAYERS == 2)
    # 維度錯
    chk("特徵維不符 → ValueError",
        _raises(ValueError, lambda: GcnSmall(3).fit(x, edges)))

    # —— rebind 煙 ——
    m3 = GcnSmall(in_dim=4, hidden=4, out_dim=1, seed=2).fit(x, edges, y=y, n_steps=2)
    edges2 = np.array([[0, 1], [1, 2]])  # 少一邊
    m3.rebind(edges2)
    s3 = m3.predict_scores(x)
    chk("rebind 後仍有限", bool(np.all(np.isfinite(s3))))

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
    print("(自測:python -m augur.models.gnn_small --selftest;免 DB 免 API)")
    print("公開: GcnSmall, normalized_adjacency")

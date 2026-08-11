"""序列 DL 排序模型 — SeqPatchTSTSmall（patchify＋小 TransformerEncoder＋線性頭），NF-D-PATCH 0a。

🎯 這支在做什麼（白話）：與 SeqLSTM／SeqTransformerSmall 同契約——吃 as-of 序列窗
   (n × window_len × channels)，沿時間切非重疊 patch → 投影 → 小 TransformerEncoder
   → mean-pool → 橫斷面相對分數 (n,)。**不安** HuggingFace／TimesFM／Chronos 預訓練權重。
   正規化僅用 train 統計凍結（#8）。尾段不足一 patch 的時間步 **截斷**（誠實、不 pad 假值）。
守 #8 · #12（fit/predict 對齊 RankRidge／SeqLSTM）· #15（seed）· 零寫庫。

執行指令矩陣（library #18；免 DB 免 API）:
  python -m augur.models.sequence_patchtst              # 印用途
  python -m augur.models.sequence_patchtst --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import numpy as np

# CPU-only 友善預設（0a／後續 0b 可覆寫）
PATCH_LEN = 4
PATCH_D_MODEL = 32
PATCH_NHEAD = 4
PATCH_NLAYERS = 1
PATCH_DIM_FF = 64
PATCH_EPOCHS = 50
PATCH_LR = 1e-3


class SeqPatchTSTSmall:
    """非重疊 patchify → Linear → TransformerEncoder(batch_first) → mean-pool → Linear。"""

    family = "SeqPatchTSTSmall"

    def __init__(
        self,
        seed=42,
        patch_len=PATCH_LEN,
        d_model=PATCH_D_MODEL,
        nhead=PATCH_NHEAD,
        nlayers=PATCH_NLAYERS,
        dim_feedforward=PATCH_DIM_FF,
        epochs=PATCH_EPOCHS,
        lr=PATCH_LR,
        dropout=0.0,
    ):
        if int(patch_len) < 1:
            raise ValueError("patch_len>=1")
        if d_model % nhead != 0:
            raise ValueError(f"d_model={d_model} 須被 nhead={nhead} 整除")
        self.seed = int(seed)
        self.patch_len = int(patch_len)
        self.d_model = int(d_model)
        self.nhead = int(nhead)
        self.nlayers = int(nlayers)
        self.dim_feedforward = int(dim_feedforward)
        self.epochs = int(epochs)
        self.lr = float(lr)
        self.dropout = float(dropout)
        self._model = None
        self._mean = None
        self._std = None

    def _normalize(self, X):
        Xn = (X - self._mean) / self._std
        return np.nan_to_num(Xn, nan=0.0, posinf=0.0, neginf=0.0)

    @staticmethod
    def _n_patches(window_len: int, patch_len: int) -> int:
        return int(window_len) // int(patch_len)

    def fit(self, X, y_rank):
        """X:(n,window_len,n_channels)；y_rank:(n,)。回 self。"""
        import torch
        from torch import nn

        X = np.asarray(X, dtype=float)
        y = np.asarray(y_rank, dtype=float)
        if X.ndim != 3:
            raise ValueError(
                f"SeqPatchTSTSmall.fit 需 3D 張量(n,window,channels)，收到 shape={X.shape}"
            )
        n, wl, n_channels = X.shape
        n_patches = self._n_patches(wl, self.patch_len)
        if n_patches < 1:
            raise ValueError(
                f"window_len={wl} < patch_len={self.patch_len}（誠實 SKIP 上游）"
            )
        self._mean = np.nanmean(X, axis=(0, 1))
        self._std = np.nanstd(X, axis=(0, 1))
        self._std = np.where((self._std == 0) | np.isnan(self._std), 1.0, self._std)
        self._mean = np.nan_to_num(self._mean, nan=0.0)
        Xn = self._normalize(X)

        torch.manual_seed(self.seed)
        Xt = torch.tensor(Xn, dtype=torch.float32)
        yt = torch.tensor(y, dtype=torch.float32).view(-1, 1)

        patch_len = self.patch_len
        d_model = self.d_model
        nhead = self.nhead
        nlayers = self.nlayers
        dim_ff = self.dim_feedforward
        dropout = self.dropout
        patch_in = patch_len * n_channels

        class _Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.patch_proj = nn.Linear(patch_in, d_model)
                enc_layer = nn.TransformerEncoderLayer(
                    d_model=d_model,
                    nhead=nhead,
                    dim_feedforward=dim_ff,
                    dropout=dropout,
                    batch_first=True,
                    activation="gelu",
                )
                self.encoder = nn.TransformerEncoder(enc_layer, num_layers=nlayers)
                self.head = nn.Linear(d_model, 1)

            def _patchify(self, x):
                # x: (n,T,C) → (n,n_patches,patch_len*C)；截斷尾段不足一 patch
                t_use = (x.size(1) // patch_len) * patch_len
                x = x[:, :t_use, :]
                npatch = t_use // patch_len
                # (n, npatch, patch_len, C) → (n, npatch, patch_len*C)
                x = x.view(x.size(0), npatch, patch_len, x.size(2))
                return x.reshape(x.size(0), npatch, patch_in)

            def forward(self, x):
                p = self._patchify(x)
                h = self.patch_proj(p)
                h = self.encoder(h)
                h = h.mean(dim=1)
                return self.head(h)

        self._model = _Net()
        opt = torch.optim.Adam(self._model.parameters(), lr=self.lr)
        loss_fn = nn.MSELoss()
        self._model.train()
        for _ in range(self.epochs):
            opt.zero_grad()
            loss = loss_fn(self._model(Xt), yt)
            loss.backward()
            opt.step()
        return self

    def predict(self, X):
        import torch

        if self._model is None:
            raise RuntimeError("SeqPatchTSTSmall 未 fit")
        X = np.asarray(X, dtype=float)
        Xn = self._normalize(X)
        Xt = torch.tensor(Xn, dtype=torch.float32)
        self._model.eval()
        with torch.no_grad():
            pred = self._model(Xt)
        return pred.view(-1).numpy()


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("family 標識", SeqPatchTSTSmall.family == "SeqPatchTSTSmall")
    m0 = SeqPatchTSTSmall()
    chk(
        "預設超參合理",
        m0.patch_len > 0
        and m0.d_model > 0
        and m0.nhead > 0
        and m0.nlayers > 0
        and m0.epochs > 0
        and m0.lr > 0,
    )
    chk("d_model 可被 nhead 整除", m0.d_model % m0.nhead == 0)
    chk("未 fit → 無 model/mean/std", m0._model is None and m0._mean is None)

    def raises_runtime(fn):
        try:
            fn()
            return False
        except RuntimeError:
            return True
        except Exception:
            return False

    chk(
        "未 fit predict 拋 RuntimeError",
        raises_runtime(lambda: SeqPatchTSTSmall().predict(np.zeros((2, 8, 4)))),
    )

    def raises_value(fn):
        try:
            fn()
            return False
        except ValueError:
            return True
        except Exception:
            return False

    chk(
        "d_model 非整除 nhead → ValueError",
        raises_value(lambda: SeqPatchTSTSmall(d_model=30, nhead=4)),
    )
    chk(
        "window < patch_len → ValueError",
        raises_value(
            lambda: SeqPatchTSTSmall(patch_len=8, d_model=8, nhead=2, epochs=1).fit(
                np.zeros((2, 4, 3)), np.zeros(2)
            )
        ),
    )

    rng = np.random.RandomState(0)
    n, wl, c = 12, 9, 3  # 9→截斷至 8＝2 patches×4
    X = rng.randn(n, wl, c)
    y = rng.rand(n)
    m = SeqPatchTSTSmall(
        seed=1, patch_len=4, d_model=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=3
    ).fit(X, y)
    pred = m.predict(X)
    chk("predict 形狀=(n,)", pred.shape == (n,))
    chk("predict 皆 finite", np.all(np.isfinite(pred)))

    Xnan = X.copy()
    Xnan[0, 0, 0] = np.nan
    Xnan[1, :, 1] = np.nan
    m2 = SeqPatchTSTSmall(
        seed=1, patch_len=4, d_model=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=3
    ).fit(Xnan, y)
    chk(
        "含 NaN 輸入 fit/predict 不炸、輸出 finite",
        np.all(np.isfinite(m2.predict(Xnan))),
    )

    Xtest = rng.randn(5, wl, c) * 10 + 100
    manual_norm = np.nan_to_num((Xtest - m._mean) / m._std, nan=0.0)
    chk("正規化用 train 統計凍結(#8)", np.allclose(m._normalize(Xtest), manual_norm))

    m3 = SeqPatchTSTSmall(
        seed=7, patch_len=4, d_model=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=5
    ).fit(X, y)
    m4 = SeqPatchTSTSmall(
        seed=7, patch_len=4, d_model=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=5
    ).fit(X, y)
    chk("同 seed 可重現(#15)", np.allclose(m3.predict(X), m4.predict(X)))

    m5 = SeqPatchTSTSmall(
        seed=99, patch_len=4, d_model=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=5
    ).fit(X, y)
    chk("不同 seed → 不同 predict", not np.allclose(m3.predict(X), m5.predict(X)))

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.models.sequence_patchtst --selftest;免 DB 免 API)")

"""序列 DL 排序模型 — SeqTransformerSmall（小 TransformerEncoder＋線性頭），NF-C-TFM 0a。

🎯 這支在做什麼（白話）：與 SeqLSTM 同契約——吃 as-of 序列窗張量
   (n × window_len × channels)，輸出橫斷面相對分數 (n,)。內部用小型
   TransformerEncoder（少層／少頭）取代 LSTM；**不安** HuggingFace／Chronos
   等預訓練權重。正規化僅用 train 統計凍結（#8）。
守 #8 · #12（fit/predict 對齊 RankRidge／SeqLSTM）· #15（seed）· 零寫庫。

執行指令矩陣（library #18；免 DB 免 API）:
  python -m augur.models.sequence_transformer              # 印用途
  python -m augur.models.sequence_transformer --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import math

import numpy as np

# CPU-only 友善預設（0a／後續 0b 可覆寫）
TFM_D_MODEL = 32
TFM_NHEAD = 4
TFM_NLAYERS = 1
TFM_DIM_FF = 64
TFM_EPOCHS = 50
TFM_LR = 1e-3


class SeqTransformerSmall:
    """小 TransformerEncoder(batch_first)+mean-pool＋線性頭。"""

    family = "SeqTransformerSmall"

    def __init__(
        self,
        seed=42,
        d_model=TFM_D_MODEL,
        nhead=TFM_NHEAD,
        nlayers=TFM_NLAYERS,
        dim_feedforward=TFM_DIM_FF,
        epochs=TFM_EPOCHS,
        lr=TFM_LR,
        dropout=0.0,
    ):
        if d_model % nhead != 0:
            raise ValueError(f"d_model={d_model} 須被 nhead={nhead} 整除")
        self.seed = int(seed)
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

    def fit(self, X, y_rank):
        """X:(n,window_len,n_channels)；y_rank:(n,)。回 self。"""
        import torch
        from torch import nn

        X = np.asarray(X, dtype=float)
        y = np.asarray(y_rank, dtype=float)
        if X.ndim != 3:
            raise ValueError(
                f"SeqTransformerSmall.fit 需 3D 張量(n,window,channels)，收到 shape={X.shape}"
            )
        n_channels = X.shape[2]
        self._mean = np.nanmean(X, axis=(0, 1))
        self._std = np.nanstd(X, axis=(0, 1))
        self._std = np.where((self._std == 0) | np.isnan(self._std), 1.0, self._std)
        self._mean = np.nan_to_num(self._mean, nan=0.0)
        Xn = self._normalize(X)

        torch.manual_seed(self.seed)
        Xt = torch.tensor(Xn, dtype=torch.float32)
        yt = torch.tensor(y, dtype=torch.float32).view(-1, 1)

        d_model = self.d_model
        nhead = self.nhead
        nlayers = self.nlayers
        dim_ff = self.dim_feedforward
        dropout = self.dropout

        class _Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.in_proj = nn.Linear(n_channels, d_model)
                # 可學習位置編碼（小窗；不依賴絕對日曆）
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
                self._pos = None

            def _pos_embed(self, t: int, device):
                if self._pos is None or self._pos.size(1) < t:
                    # 正弦位置（固定，非學習）——重現性穩
                    pe = torch.zeros(1, t, d_model, device=device)
                    pos = torch.arange(t, device=device).unsqueeze(1).float()
                    div = torch.exp(
                        torch.arange(0, d_model, 2, device=device).float()
                        * (-math.log(10000.0) / d_model)
                    )
                    pe[0, :, 0::2] = torch.sin(pos * div)
                    pe[0, :, 1::2] = torch.cos(pos * div[: (d_model // 2)])
                    self._pos = pe
                return self._pos[:, :t, :]

            def forward(self, x):
                # x: (n,T,C)
                h = self.in_proj(x)
                h = h + self._pos_embed(h.size(1), h.device)
                h = self.encoder(h)
                h = h.mean(dim=1)  # mean-pool over time
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
            raise RuntimeError("SeqTransformerSmall 未 fit")
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

    chk("family 標識", SeqTransformerSmall.family == "SeqTransformerSmall")
    m0 = SeqTransformerSmall()
    chk(
        "預設超參合理",
        m0.d_model > 0 and m0.nhead > 0 and m0.nlayers > 0 and m0.epochs > 0 and m0.lr > 0,
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
        raises_runtime(lambda: SeqTransformerSmall().predict(np.zeros((2, 3, 4)))),
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
        raises_value(lambda: SeqTransformerSmall(d_model=30, nhead=4)),
    )

    rng = np.random.RandomState(0)
    n, wl, c = 12, 5, 3
    X = rng.randn(n, wl, c)
    y = rng.rand(n)
    m = SeqTransformerSmall(seed=1, d_model=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=3).fit(
        X, y
    )
    pred = m.predict(X)
    chk("predict 形狀=(n,)", pred.shape == (n,))
    chk("predict 皆 finite", np.all(np.isfinite(pred)))

    Xnan = X.copy()
    Xnan[0, 0, 0] = np.nan
    Xnan[1, :, 1] = np.nan
    m2 = SeqTransformerSmall(seed=1, d_model=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=3).fit(
        Xnan, y
    )
    chk(
        "含 NaN 輸入 fit/predict 不炸、輸出 finite",
        np.all(np.isfinite(m2.predict(Xnan))),
    )

    Xtest = rng.randn(5, wl, c) * 10 + 100
    manual_norm = np.nan_to_num((Xtest - m._mean) / m._std, nan=0.0)
    chk("正規化用 train 統計凍結(#8)", np.allclose(m._normalize(Xtest), manual_norm))

    m3 = SeqTransformerSmall(seed=7, d_model=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=5).fit(
        X, y
    )
    m4 = SeqTransformerSmall(seed=7, d_model=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=5).fit(
        X, y
    )
    chk("同 seed 可重現(#15)", np.allclose(m3.predict(X), m4.predict(X)))

    m5 = SeqTransformerSmall(seed=99, d_model=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=5).fit(
        X, y
    )
    chk("不同 seed → 不同 predict", not np.allclose(m3.predict(X), m5.predict(X)))

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.models.sequence_transformer --selftest;免 DB 免 API)")

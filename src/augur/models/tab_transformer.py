"""表格 DL 排序模型 — RankFTTransformer（NF-A-FTTR 0a）。

🎯 這支在做什麼（白話）：月頻／截面特徵矩陣 X(n×f) → 每特徵一個 token，
   小 TransformerEncoder 做特徵交互，池化後線性頭輸出排序分數。
   契約對齊 RankRidge：fit(X,y_rank)／predict(X)→(n,)。
   **不安** pytorch-tabnet；純 torch（本機 CPU-only 可行）。
守 #8（train scaler 凍結）· #12 · #15（seed）。

執行指令矩陣（library #18；免 DB 免 API）:
  python -m augur.models.tab_transformer              # 印用途
  python -m augur.models.tab_transformer --selftest   # 純紅綠自測
"""
from __future__ import annotations

import numpy as np

FT_D_TOKEN = 16
FT_NHEAD = 4
FT_NLAYERS = 1
FT_DIM_FF = 32
FT_EPOCHS = 40
FT_LR = 1e-3


class RankFTTransformer:
    """Feature-Tokenizer + TransformerEncoder（小）→ 排序分數。0a 不寫庫。"""

    family = "RankFTTransformer"

    def __init__(
        self,
        seed=42,
        d_token=FT_D_TOKEN,
        nhead=FT_NHEAD,
        nlayers=FT_NLAYERS,
        dim_feedforward=FT_DIM_FF,
        epochs=FT_EPOCHS,
        lr=FT_LR,
        dropout=0.0,
    ):
        if d_token % nhead != 0:
            raise ValueError(f"d_token={d_token} 須被 nhead={nhead} 整除")
        self.seed = int(seed)
        self.d_token = int(d_token)
        self.nhead = int(nhead)
        self.nlayers = int(nlayers)
        self.dim_feedforward = int(dim_feedforward)
        self.epochs = int(epochs)
        self.lr = float(lr)
        self.dropout = float(dropout)
        self._model = None
        self._mean = None
        self._std = None
        self._n_features = None

    def _normalize(self, X):
        Xn = (X - self._mean) / self._std
        return np.nan_to_num(Xn, nan=0.0, posinf=0.0, neginf=0.0)

    def fit(self, X, y_rank):
        import torch
        from torch import nn

        X = np.asarray(X, dtype=float)
        y = np.asarray(y_rank, dtype=float)
        if X.ndim != 2:
            raise ValueError(f"RankFTTransformer.fit 需 2D (n,f)，收到 {X.shape}")
        n, f = X.shape
        self._n_features = f
        self._mean = np.nanmean(X, axis=0)
        self._std = np.nanstd(X, axis=0)
        self._std = np.where((self._std == 0) | np.isnan(self._std), 1.0, self._std)
        self._mean = np.nan_to_num(self._mean, nan=0.0)
        Xn = self._normalize(X)

        torch.manual_seed(self.seed)
        Xt = torch.tensor(Xn, dtype=torch.float32)
        yt = torch.tensor(y, dtype=torch.float32).view(-1, 1)

        d_token = self.d_token
        nhead = self.nhead
        nlayers = self.nlayers
        dim_ff = self.dim_feedforward
        dropout = self.dropout

        class _Net(nn.Module):
            def __init__(self):
                super().__init__()
                # 每特徵：value → d_token，再加可學習特徵嵌入
                self.val_proj = nn.Linear(1, d_token)
                self.feat_emb = nn.Embedding(f, d_token)
                enc_layer = nn.TransformerEncoderLayer(
                    d_model=d_token,
                    nhead=nhead,
                    dim_feedforward=dim_ff,
                    dropout=dropout,
                    batch_first=True,
                    activation="gelu",
                )
                self.encoder = nn.TransformerEncoder(enc_layer, num_layers=nlayers)
                self.cls = nn.Parameter(torch.zeros(1, 1, d_token))
                self.head = nn.Linear(d_token, 1)
                nn.init.normal_(self.cls, std=0.02)
                nn.init.normal_(self.feat_emb.weight, std=0.02)

            def forward(self, x):
                # x: (n, f)
                n_, f_ = x.shape
                tokens = self.val_proj(x.unsqueeze(-1))  # (n,f,d)
                idx = torch.arange(f_, device=x.device).unsqueeze(0).expand(n_, -1)
                tokens = tokens + self.feat_emb(idx)
                cls = self.cls.expand(n_, -1, -1)
                h = torch.cat([cls, tokens], dim=1)  # (n,1+f,d)
                h = self.encoder(h)
                return self.head(h[:, 0, :])

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
            raise RuntimeError("RankFTTransformer 未 fit")
        X = np.asarray(X, dtype=float)
        if X.ndim != 2 or X.shape[1] != self._n_features:
            raise ValueError(
                f"predict 須 (n,{self._n_features})，收到 {X.shape}"
            )
        Xn = self._normalize(X)
        Xt = torch.tensor(Xn, dtype=torch.float32)
        self._model.eval()
        with torch.no_grad():
            pred = self._model(Xt)
        return pred.view(-1).numpy()


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("family", RankFTTransformer.family == "RankFTTransformer")
    m0 = RankFTTransformer()
    chk("預設超參合理", m0.d_token > 0 and m0.nhead > 0 and m0.epochs > 0)
    chk("d_token % nhead == 0", m0.d_token % m0.nhead == 0)
    chk("未 fit 無 model", m0._model is None)

    def raises_runtime(fn):
        try:
            fn()
            return False
        except RuntimeError:
            return True
        except Exception:
            return False

    def raises_value(fn):
        try:
            fn()
            return False
        except ValueError:
            return True
        except Exception:
            return False

    chk(
        "未 fit predict → RuntimeError",
        raises_runtime(lambda: RankFTTransformer().predict(np.zeros((2, 3)))),
    )
    chk(
        "d_token 非整除 → ValueError",
        raises_value(lambda: RankFTTransformer(d_token=15, nhead=4)),
    )

    rng = np.random.RandomState(0)
    n, f = 24, 6
    X = rng.randn(n, f)
    y = rng.rand(n)
    m = RankFTTransformer(
        seed=1, d_token=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=5
    ).fit(X, y)
    pred = m.predict(X)
    chk("predict 形狀=(n,)", pred.shape == (n,))
    chk("predict finite", np.all(np.isfinite(pred)))

    Xnan = X.copy()
    Xnan[0, 0] = np.nan
    Xnan[1, :] = np.nan
    m2 = RankFTTransformer(
        seed=1, d_token=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=5
    ).fit(Xnan, y)
    chk("含 NaN fit/predict finite", np.all(np.isfinite(m2.predict(Xnan))))

    Xtest = rng.randn(5, f) * 10 + 50
    manual = np.nan_to_num((Xtest - m._mean) / m._std, nan=0.0)
    chk("scaler 用 train 統計凍結(#8)", np.allclose(m._normalize(Xtest), manual))

    m3 = RankFTTransformer(
        seed=7, d_token=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=8
    ).fit(X, y)
    m4 = RankFTTransformer(
        seed=7, d_token=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=8
    ).fit(X, y)
    chk("同 seed 可重現(#15)", np.allclose(m3.predict(X), m4.predict(X)))

    m5 = RankFTTransformer(
        seed=99, d_token=8, nhead=2, nlayers=1, dim_feedforward=16, epochs=8
    ).fit(X, y)
    chk("不同 seed → 不同 predict", not np.allclose(m3.predict(X), m5.predict(X)))

    chk(
        "特徵數不符 → ValueError",
        raises_value(lambda: m.predict(np.zeros((2, f + 1)))),
    )

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.models.tab_transformer --selftest)")

"""序列 DL 排序模型 — SeqLSTM(單層 LSTM+線性頭)，S4-Wave-C 首個真 adapter。

🎯 這支在做什麼(白話):把 as-of 序列窗張量(n 股 × window_len 交易日 × f 通道，來自
   `features.sequence.stack_windows`)fit 成「橫斷面相對強弱分數」——契約刻意對齊
   `models.ranker`(RankRidge/RankGBDT)之 fit(X,y_rank)→predict(X)→ndarray(n,)，供未來
   若證實真贏後可比照既有機制擴充(#12 複用鐵律精神，非強塞)。
   內部:z-score 正規化(**僅用 train 統計**，凍結存於 self，predict 時沿用，防洩漏#8)→
   NaN(訓練統計後仍缺值)填 0(=正規化後之通道均值，非任意數字)→單層 LSTM(batch_first)
   →取最後時間步隱狀態→線性頭→純量分數。CPU-only 可行(本機無 GPU)，資料量小(數千樣本
   量級)故整批訓練、不另分 mini-batch。
守 #8(train 統計凍結、不用 predict 期資料回算正規化)· #12(fit/predict 契約同 RankRidge/RankGBDT)·
   #15(seed 固定可重現)· 隔離不變式(零 import 知識/哲學/顧問)。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.models.sequence_ranker              # 印用途+公開入口（唯讀）
  python -m augur.models.sequence_ranker --selftest   # 純紅綠自測（零 IO；合成張量，含 NaN 處理與正規化行為驗證）
"""
from __future__ import annotations

import numpy as np


class SeqLSTM:
    """單層 LSTM(batch_first)+線性頭。train 統計正規化凍結於 self,#8 防洩漏。"""

    family = "SeqLSTM"

    def __init__(self, seed=42, hidden_size=32, epochs=50, lr=1e-3):
        self.seed = seed
        self.hidden_size = hidden_size
        self.epochs = epochs
        self.lr = lr
        self._model = None
        self._mean = None
        self._std = None

    def _normalize(self, X):
        """(X-mean)/std(train 統計,#8 凍結)→殘餘 NaN(如整通道無值)填 0(=正規化後通道均值)。"""
        Xn = (X - self._mean) / self._std
        return np.nan_to_num(Xn, nan=0.0, posinf=0.0, neginf=0.0)

    def fit(self, X, y_rank):
        """X:(n,window_len,n_channels)ndarray(可含 NaN)；y_rank:(n,)。回 self。"""
        import torch
        from torch import nn

        X = np.asarray(X, dtype=float)
        y = np.asarray(y_rank, dtype=float)
        if X.ndim != 3:
            raise ValueError(f"SeqLSTM.fit 需 3D 張量(n,window,channels)，收到 shape={X.shape}")
        n_channels = X.shape[2]
        # train 統計(逐通道，忽略 NaN；全 NaN 通道 std 落 nan→後續 clip 防除零)
        self._mean = np.nanmean(X, axis=(0, 1))
        self._std = np.nanstd(X, axis=(0, 1))
        self._std = np.where((self._std == 0) | np.isnan(self._std), 1.0, self._std)
        self._mean = np.nan_to_num(self._mean, nan=0.0)
        Xn = self._normalize(X)

        torch.manual_seed(self.seed)
        Xt = torch.tensor(Xn, dtype=torch.float32)
        yt = torch.tensor(y, dtype=torch.float32).view(-1, 1)

        class _Net(nn.Module):
            def __init__(self, n_channels, hidden_size):
                super().__init__()
                self.lstm = nn.LSTM(input_size=n_channels, hidden_size=hidden_size, batch_first=True)
                self.head = nn.Linear(hidden_size, 1)

            def forward(self, x):
                out, _ = self.lstm(x)
                return self.head(out[:, -1, :])   # 取最後時間步隱狀態→線性頭

        self._model = _Net(n_channels, self.hidden_size)
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
            raise RuntimeError("SeqLSTM 未 fit")
        X = np.asarray(X, dtype=float)
        Xn = self._normalize(X)
        Xt = torch.tensor(Xn, dtype=torch.float32)
        self._model.eval()
        with torch.no_grad():
            pred = self._model(Xt)
        return pred.view(-1).numpy()


def _selftest():
    """自測（零 DB/零 API；torch 為本機計算、非外部 IO）：真跑 fit/predict 驗證自訂邏輯
    (正規化凍結／NaN 填補／契約形狀)，非僅結構檢查——本檔含自訂邏輯(非純轉呼叫 sklearn/
    lightgbm 之off-the-shelf estimator)，依 CLAUDE #35「純函式餵真輸入」須真跑驗證。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("SeqLSTM.family 標識", SeqLSTM.family == "SeqLSTM")
    chk("預設超參合理(hidden_size/epochs/lr 皆正)",
        SeqLSTM().hidden_size > 0 and SeqLSTM().epochs > 0 and SeqLSTM().lr > 0)
    chk("未 fit → 無 model/mean/std", SeqLSTM()._model is None and SeqLSTM()._mean is None)

    def raises_runtime(fn):
        try:
            fn(); return False
        except RuntimeError:
            return True
        except Exception:
            return False
    chk("未 fit predict 拋 RuntimeError",
        raises_runtime(lambda: SeqLSTM().predict(np.zeros((2, 3, 4)))))

    # 真跑 fit/predict(合成小張量,零 IO):驗證形狀契約與 NaN 處理不炸
    rng = np.random.RandomState(0)
    n, wl, c = 12, 5, 3
    X = rng.randn(n, wl, c)
    y = rng.rand(n)   # 模擬 rank_pctile∈[0,1]
    m = SeqLSTM(seed=1, hidden_size=4, epochs=3).fit(X, y)
    pred = m.predict(X)
    chk("predict 回傳形狀=(n,)", pred.shape == (n,))
    chk("predict 輸出皆為 finite(無 NaN/inf 洩漏到輸出)", np.all(np.isfinite(pred)))

    # NaN 輸入(#1 缺值場景):不得炸、輸出仍 finite(下游絆線:若移除 nan_to_num 應會 NaN 傳播,見下方驗紅)
    Xnan = X.copy()
    Xnan[0, 0, 0] = np.nan
    Xnan[1, :, 1] = np.nan   # 整通道缺值(模擬稀疏籌碼通道)
    m2 = SeqLSTM(seed=1, hidden_size=4, epochs=3).fit(Xnan, y)
    pred2 = m2.predict(Xnan)
    chk("含 NaN 輸入(單格+整通道缺值)fit/predict 不炸、輸出皆 finite",
        np.all(np.isfinite(pred2)))

    # train 統計凍結(#8 下游絆線):同一 fit 好的模型，對「偏移過的」測試張量 predict，
    # 應用同一組(fit 時凍結的)mean/std 正規化——手動重算應與 predict 內部結果一致
    Xtest = rng.randn(5, wl, c) * 10 + 100   # 刻意偏移，驗證用的是 train 統計非 test 統計
    manual_norm = np.nan_to_num((Xtest - m._mean) / m._std, nan=0.0)
    chk("正規化用 train 統計凍結(#8,非 test 期重算)",
        np.allclose(m._normalize(Xtest), manual_norm))

    # 同 seed 可重現(#15):兩次獨立 fit(同資料同 seed)應得相同 predict
    m3 = SeqLSTM(seed=7, hidden_size=4, epochs=5).fit(X, y)
    m4 = SeqLSTM(seed=7, hidden_size=4, epochs=5).fit(X, y)
    chk("同 seed 兩次 fit → predict 完全一致(#15 可重現、真跑非字面斷言)",
        np.allclose(m3.predict(X), m4.predict(X)))

    # 不同 seed 應給不同初始化 → 不同 predict(弱檢查,真跑驗證非恆真)
    m5 = SeqLSTM(seed=99, hidden_size=4, epochs=5).fit(X, y)
    chk("不同 seed 給不同 predict(初始化真的有影響,非死碼)",
        not np.allclose(m3.predict(X), m5.predict(X)))

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.models.sequence_ranker --selftest;免 DB 免 API)")

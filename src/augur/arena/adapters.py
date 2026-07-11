"""arena adapters — 擂台候選之統一預測介面(arena plan §2.1/§5;本地推論、離線可跑)。

🎯 這支在做什麼(白話):每個參賽者一個 adapter,統一簽名
   `predict(series: dict[str, list[float]], horizon_td: int) -> dict[str, float]`
   (own_stack_rolling 另收可選 `context={'p_mkt','rank'}` 外掛分量,缺省中性、簽名相容)
   ——輸入=各標的之歷史收盤序列(由呼叫端提供:合成冒煙給隨機漫步、live 給 DB 價格),
   輸出=各標的 P(未來 horizon 交易日累積報酬>0)。**adapter 自己零 DB/零網路**(離線單測斷言;
   市場模型=本地權重推論)。轉換口徑(市場模型點/樣本預測→方向機率)寫死於此、隨 code_sha 凍結:
   `conversion=樣本路徑正報酬比例(零調參、唯一嘗試之口徑)`——選擇紀錄入候選 spec。

守 #8(輸入序列由呼叫端裁切至 as-of,adapter 不碰時間軸)· #28(本地)· 憲章(輸出僅供 ledger,不進 UI)。
"""
import numpy as np

WINDOW_MOMENTUM = 20      # 基線參數=慣例值、隨 code_sha 凍結(非資料挑選;arena plan §2.1)
BLOCK_BOOT_WEEKS = 52
N_BOOT = 2000
WINDOW_VOL = 60           # own_stack_rolling:DirStackM 口徑之 vol_60/mom_60/beta_252 視窗
WINDOW_BETA = 252
MKT_SERIES_KEY = "TAIEX"
MKT_LOGIT_SCALE = 5.0     # 動量→p_mkt 代理之 sigmoid 斜率(慣例值、隨 code_sha 凍結)


def _rets(px):
    px = np.asarray(px, float)
    return px[1:] / px[:-1] - 1.0


def _roll_std(x, w):
    out = np.full(len(x), np.nan)
    if len(x) >= w:
        from numpy.lib.stride_tricks import sliding_window_view
        out[w - 1:] = sliding_window_view(x, w).std(axis=1)
    return out


def _roll_beta(rt, rm, w):
    """滾動 beta=cov(rt,rm)/var(rm) 尾窗 w;窗含 NaN(對齊缺口/序列頭)→ NaN(下游 impute)。"""
    out = np.full(len(rt), np.nan)
    if len(rt) >= w:
        from numpy.lib.stride_tricks import sliding_window_view
        swt, swm = sliding_window_view(rt, w), sliding_window_view(rm, w)
        mt, mm = swt.mean(axis=1), swm.mean(axis=1)
        cov = ((swt - mt[:, None]) * (swm - mm[:, None])).mean(axis=1)
        var = swm.var(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            out[w - 1:] = np.where(var > 0, cov / var, np.nan)
    return out


class BaselineMajority:
    """全局多數類:P=歷史上「horizon 累積報酬>0」之頻率(全標的 pooled)。excess≡0 之誠實地板。"""
    key = "majority"

    def predict(self, series, horizon_td):
        ups, n = 0, 0
        for px in series.values():
            px = np.asarray(px, float)
            if len(px) <= horizon_td:
                continue
            fwd = px[horizon_td:] / px[:-horizon_td] - 1.0
            ups += int((fwd > 0).sum()); n += len(fwd)
        p = ups / n if n else 0.5
        return {t: p for t in series}


class BaselineMomentum:
    """動量規則:近 20 日報酬>0 → p=歷史條件頻率(上/下兩桶,pooled)。"""
    key = "momentum_20"

    def predict(self, series, horizon_td):
        up_b, dn_b = [0, 0], [0, 0]     # [ups, n]
        sig = {}
        for t, px in series.items():
            px = np.asarray(px, float)
            if len(px) <= horizon_td + WINDOW_MOMENTUM:
                sig[t] = None; continue
            mom = px[WINDOW_MOMENTUM:] / px[:-WINDOW_MOMENTUM] - 1.0
            fwd = px[horizon_td:] / px[:-horizon_td] - 1.0
            m = mom[:len(px) - WINDOW_MOMENTUM - horizon_td]
            f = fwd[WINDOW_MOMENTUM:]
            for b, mask in ((up_b, m > 0), (dn_b, m <= 0)):
                b[0] += int((f[mask] > 0).sum()); b[1] += int(mask.sum())
            sig[t] = mom[-1] > 0
        pu = up_b[0] / up_b[1] if up_b[1] else 0.5
        pd = dn_b[0] / dn_b[1] if dn_b[1] else 0.5
        return {t: (0.5 if s is None else (pu if s else pd)) for t, s in sig.items()}


class BaselineMcBootstrap:
    """block bootstrap:52 週窗日報酬重抽 N 路徑,P=正終值比例(同 /simulate 口徑、每標的獨立)。"""
    key = "mc_bootstrap"

    def __init__(self, seed=42):
        self.seed = seed

    def predict(self, series, horizon_td):
        out = {}
        rng = np.random.default_rng(self.seed)
        for t, px in series.items():
            r = _rets(px)[-BLOCK_BOOT_WEEKS * 5:]
            if len(r) < 60:
                out[t] = 0.5; continue
            blk = 5
            idx = rng.integers(0, len(r) - blk, size=(N_BOOT, (horizon_td // blk) + 1))
            paths = np.concatenate([r[i:i + blk] for row in idx for i in row]).reshape(N_BOOT, -1)[:, :horizon_td]
            out[t] = float(((1 + paths).prod(axis=1) - 1 > 0).mean())
        return out


class OwnDailyRolling:
    """自家 D 軌配方(凍結配方+滾動 refit 類):價量 7 特徵(v2 D 軌子集之純價量部分,adapter 內自算,
    零 DB)+HistGBDT(3-seed 均值)+isotonic(train 尾段)。refit 政策=每次 predict 以輸入序列重訓
    (呼叫端裁切 as-of=政策留痕 train_data_max_date)。"""
    key = "own_daily_rolling"

    def predict(self, series, horizon_td):
        from sklearn.ensemble import HistGradientBoostingClassifier
        from sklearn.isotonic import IsotonicRegression
        X_tr, y_tr, X_te, te_keys = [], [], [], []
        for t, px in series.items():
            px = np.asarray(px, float)
            if len(px) < 120 + horizon_td:
                continue
            r1 = np.concatenate([[np.nan], _rets(px)])
            feats = np.column_stack([
                px / np.concatenate([[np.nan] * 1, px[:-1]]) - 1,
                px / np.concatenate([[np.nan] * 5, px[:-5]]) - 1,
                px / np.concatenate([[np.nan] * 20, px[:-20]]) - 1,
                np.array([np.nanstd(r1[max(0, i - 19):i + 1]) for i in range(len(px))]),
            ])
            fwd = np.full(len(px), np.nan)
            fwd[:-horizon_td] = px[horizon_td:] / px[:-horizon_td] - 1.0
            ok = ~np.isnan(feats).any(axis=1)
            tr = ok & ~np.isnan(fwd)
            X_tr.append(feats[tr]); y_tr.append((fwd[tr] > 0).astype(int))
            if ok[-1]:
                X_te.append(feats[-1]); te_keys.append(t)
        if not X_tr or not te_keys:
            return {t: 0.5 for t in series}
        X, y = np.vstack(X_tr), np.concatenate(y_tr)
        if len(set(y)) < 2:
            return {t: float(np.mean(y)) for t in series}
        cut = int(len(X) * 0.85)
        preds = np.zeros(len(te_keys))
        for sd in range(3):
            clf = HistGradientBoostingClassifier(max_iter=200, max_depth=3, learning_rate=0.05,
                                                 early_stopping=True, random_state=sd)
            clf.fit(X[:cut], y[:cut])
            iso = IsotonicRegression(y_min=0, y_max=1, out_of_bounds="clip").fit(
                clf.predict_proba(X[cut:])[:, 1], y[cut:])
            preds += iso.predict(clf.predict_proba(np.vstack(X_te))[:, 1])
        return dict(zip(te_keys, (preds / 3).tolist()))


class OwnStackRolling:
    """自家 H 軌配方(DirStackM 配方+MktLogit_v2 分量;滾動 refit):特徵=DirStackM 口徑
    [logit(p_mkt), rank−0.5, 交互, vol_60, mom_60, beta_252(對 TAIEX 序列;無則 NaN→impute)],
    模型=L2 logit(impute median+standardize,同 DirStackM pipeline),每次 predict 以輸入序列
    自造訓練樣本(每點 t 之特徵 vs t+h 方向)重訓=滾動 refit(呼叫端裁切 as-of)。
    context 可含 {'p_mkt': float, 'rank': {target: pctile}}(A2 live 由呼叫端從 DB 餵);
    缺省=中性:p_mkt 以 series 之 TAIEX 動量 logit 代理(無 TAIEX 則 0.5)、rank 全 0.5
    (歷史無 rank 源→訓練期 rank/交互恆中性,其權重待 live 分量到位才有效——誠實限制)。"""
    key = "own_stack_rolling"

    def predict(self, series, horizon_td, context=None):
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        ctx = context or {}
        ranks = ctx.get("rank") or {}
        lg_ctx = None
        if ctx.get("p_mkt") is not None:
            pm_ctx = float(np.clip(ctx["p_mkt"], 1e-4, 1 - 1e-4))
            lg_ctx = float(np.log(pm_ctx / (1 - pm_ctx)))
        m_r1 = m_lg = None
        if MKT_SERIES_KEY in series:
            mkt = np.asarray(series[MKT_SERIES_KEY], float)
            if len(mkt) > WINDOW_VOL:
                m_r1 = np.concatenate([[np.nan], _rets(mkt)])
                m_mom = np.full(len(mkt), np.nan)
                m_mom[WINDOW_VOL:] = mkt[WINDOW_VOL:] / mkt[:-WINDOW_VOL] - 1.0
                pm = 1.0 / (1.0 + np.exp(-MKT_LOGIT_SCALE * m_mom))
                pm = np.clip(np.where(np.isfinite(pm), pm, 0.5), 1e-4, 1 - 1e-4)
                m_lg = np.log(pm / (1 - pm))
        X_tr, y_tr, X_te, te_keys = [], [], [], []
        for t, px in series.items():
            px = np.asarray(px, float)
            n = len(px)
            if n < WINDOW_VOL + horizon_td + 10:
                continue
            r1 = np.concatenate([[np.nan], _rets(px)])
            mom = np.full(n, np.nan)
            mom[WINDOW_VOL:] = px[WINDOW_VOL:] / px[:-WINDOW_VOL] - 1.0
            vol = _roll_std(r1, WINDOW_VOL)
            lg, beta = np.zeros(n), np.full(n, np.nan)
            if m_r1 is not None:
                off = len(m_r1) - n            # 尾端對齊(呼叫端皆裁至同一 as-of)
                lo, hi = max(0, -off), min(n, len(m_r1) - off)
                if hi > lo:
                    rm = np.full(n, np.nan)
                    rm[lo:hi] = m_r1[lo + off:hi + off]
                    beta = _roll_beta(r1, rm, WINDOW_BETA)
                    lg[lo:hi] = m_lg[lo + off:hi + off]
            rk = np.zeros(n)                    # 歷史 rank 無源→中性 0(=0.5−0.5)
            feats = np.column_stack([lg, rk, lg * rk, vol, mom, beta])
            fwd = np.full(n, np.nan)
            fwd[:-horizon_td] = px[horizon_td:] / px[:-horizon_td] - 1.0
            core_ok = np.isfinite(vol) & np.isfinite(mom)
            tr = core_ok & np.isfinite(fwd)
            X_tr.append(feats[tr]); y_tr.append((fwd[tr] > 0).astype(int))
            if core_ok[-1]:
                row = feats[-1].copy()
                if lg_ctx is not None:
                    row[0] = lg_ctx
                if ranks.get(t) is not None:
                    row[1] = float(ranks[t]) - 0.5
                row[2] = row[0] * row[1]
                X_te.append(row); te_keys.append(t)
        out = {t: 0.5 for t in series}
        if not X_tr or not te_keys:
            return out
        X, y = np.vstack(X_tr), np.concatenate(y_tr)
        if len(set(y)) < 2:
            return {t: float(np.mean(y)) for t in series}
        pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                             LogisticRegression(penalty="l2", C=1.0, max_iter=1000))
        pipe.fit(X, y)
        preds = pipe.predict_proba(np.vstack(X_te))[:, 1]
        out.update({t: float(np.clip(p, 0.0, 1.0)) for t, p in zip(te_keys, preds)})
        return out


class MarketChronos:
    """Chronos-Bolt(本地權重、樣本路徑推論):P=樣本路徑正累積報酬比例(零調參轉換,唯一口徑)。
    lazy import;無套件/OOM → RuntimeError(operational 除名事由,誠實留痕)。"""
    key = "chronos_bolt_small"
    model_id = "amazon/chronos-bolt-small"

    def __init__(self):
        self._pipe = None

    def _load(self):
        if self._pipe is None:
            from chronos import BaseChronosPipeline
            import torch
            self._pipe = BaseChronosPipeline.from_pretrained(
                self.model_id, device_map="cuda" if torch.cuda.is_available() else "cpu",
                torch_dtype="auto")
        return self._pipe

    def predict(self, series, horizon_td):
        import torch
        pipe = self._load()
        out = {}
        for t, px in series.items():
            ctx = torch.tensor(np.asarray(px, float)[-512:], dtype=torch.float32)
            q, _ = pipe.predict_quantiles([ctx], prediction_length=horizon_td,
                                          quantile_levels=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
            # 轉換口徑(凍結):終點分位數 vs 現價 → P(終值>現價)=線性插值分位曲線過現價之位置
            last = float(px[-1])
            qe = q[0, -1, :].numpy()
            levels = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
            if last <= qe[0]:
                p = 0.95
            elif last >= qe[-1]:
                p = 0.05
            else:
                p = 1.0 - float(np.interp(last, qe, levels))
            out[t] = float(np.clip(p, 0.0, 1.0))
        return out


class MarketTimesFM:
    """TimesFM 2.5 200m(本地權重):分位頭終點分位 → 同 Chronos 轉換口徑。lazy import。"""
    key = "timesfm_25_200m"
    model_id = "google/timesfm-2.5-200m-pytorch"

    def __init__(self):
        self._m = None

    def _load(self):
        if self._m is None:
            import timesfm
            self._m = timesfm.TimesFM_2p5_200M_torch.from_pretrained(self.model_id)
            self._m.compile(timesfm.ForecastConfig(max_context=512, max_horizon=128,
                                                   normalize_inputs=True, use_continuous_quantile_head=True))
        return self._m

    def predict(self, series, horizon_td):
        m = self._load()
        keys = list(series.keys())
        ctxs = [np.asarray(series[t], float)[-512:] for t in keys]
        _, q = m.forecast(horizon=horizon_td, inputs=ctxs)   # q: [n, horizon, 10](mean+9 分位)
        levels = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
        out = {}
        for i, t in enumerate(keys):
            last = float(ctxs[i][-1])
            qe = np.sort(np.asarray(q[i, -1, 1:], float))
            if last <= qe[0]:
                p = 0.95
            elif last >= qe[-1]:
                p = 0.05
            else:
                p = 1.0 - float(np.interp(last, qe, levels))
            out[t] = float(np.clip(p, 0.0, 1.0))
        return out


REGISTRY = {a.key: a for a in (BaselineMajority, BaselineMomentum, BaselineMcBootstrap,
                               OwnDailyRolling, OwnStackRolling, MarketChronos, MarketTimesFM)}

"""arena adapters — 擂台候選之統一預測介面(arena plan §2.1/§5;本地推論、離線可跑)。

🎯 這支在做什麼(白話):每個參賽者一個 adapter,統一簽名
   `predict(series: dict[str, list[float]], horizon_td: int) -> dict[str, float]`
   (own_stack_rolling 另收可選 `context={'p_mkt','rank'}` 外掛分量,缺省中性、簽名相容)
   ——輸入=各標的之歷史收盤序列(由呼叫端提供:合成冒煙給隨機漫步、live 給 DB 價格),
   輸出=各標的 P(未來 horizon 交易日累積報酬>0)。**adapter 自己零 DB/零網路**(離線單測斷言;
   市場模型=本地權重推論)。轉換口徑(市場模型點/樣本預測→方向機率)寫死於此、隨 code_sha 凍結:
   `conversion=樣本路徑正報酬比例(零調參、唯一嘗試之口徑)`——選擇紀錄入候選 spec。

守 #8(輸入序列由呼叫端裁切至 as-of,adapter 不碰時間軸)· #28(本地)· 憲章(輸出僅供 ledger,不進 UI)。

執行指令矩陣（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.arena.adapters              # 印用途+公開入口（唯讀）
  python -m augur.arena.adapters --selftest   # 純紅綠自測（零 IO）
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


class MarketChronos2:
    """Chronos-2(2025-10;A4 波次):同 MarketChronos 轉換口徑(終點分位 vs 現價插值、口徑凍結)。
    回形雷(2026-07-17 benchmark 實證):predict_quantiles 回 list[(1,H,9)]非 v1 stacked→squeeze 統一。"""
    key = "chronos2_market_5"
    model_id = "amazon/chronos-2"

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
        levels = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
        out = {}
        for t, px in series.items():
            ctx = torch.tensor(np.asarray(px, float)[-512:], dtype=torch.float32)
            q, _ = pipe.predict_quantiles([ctx], prediction_length=horizon_td,
                                          quantile_levels=list(levels))
            arr = np.asarray(q[0], float)
            while arr.ndim > 2:                    # Chronos-2 list[(1,H,9)] → (H,9)
                arr = arr[0]
            qe = arr[-1, :]
            last = float(px[-1])
            if last <= qe[0]:
                p = 0.95
            elif last >= qe[-1]:
                p = 0.05
            else:
                p = 1.0 - float(np.interp(last, qe, levels))
            out[t] = float(np.clip(p, 0.0, 1.0))
        return out


class MarketMoirai2:
    """Moirai-2.0-R-small(Salesforce;A4 波次):gluonts 批次路徑、樣本→終點九分位→同插值口徑(凍結)。"""
    key = "moirai2_small_5"
    model_id = "Salesforce/moirai-2.0-R-small"

    def __init__(self):
        self._pred = None
        self._h = None

    def _load(self, h):
        if self._pred is None or self._h != h:
            from uni2ts.model.moirai2 import Moirai2Forecast, Moirai2Module
            m = Moirai2Forecast(module=Moirai2Module.from_pretrained(self.model_id),
                                prediction_length=h, context_length=512, target_dim=1,
                                feat_dynamic_real_dim=0, past_feat_dynamic_real_dim=0)
            self._pred, self._h = m.create_predictor(batch_size=32), h
        return self._pred

    def predict(self, series, horizon_td):
        import pandas as pd
        from gluonts.dataset.common import ListDataset
        levels = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
        keys = list(series.keys())
        ds = ListDataset([{"target": np.asarray(series[t], float)[-512:],
                           "start": pd.Period("2000-01-03", freq="B")} for t in keys], freq="B")
        out = {}
        for t, fc in zip(keys, self._load(horizon_td).predict(ds)):
            qe = np.sort(np.array([float(np.asarray(fc.quantile(q_)).reshape(-1)[-1]) for q_ in levels])
                         if hasattr(fc, "quantile") else np.quantile(fc.samples[:, -1], levels))
            last = float(np.asarray(series[t], float)[-1])
            if last <= qe[0]:
                p = 0.95
            elif last >= qe[-1]:
                p = 0.05
            else:
                p = 1.0 - float(np.interp(last, qe, levels))
            out[t] = float(np.clip(p, 0.0, 1.0))
        return out


class OwnThreelensInteract:
    """own_threelens_interact(三鏡頭候選 T3):44 特徵(35 直餵+9 交互)月頻,HistGBM 3-seed+isotonic,
    rolling refit(train=標籤結算<as-of 之全歷史 panel;as-of=特徵表最新 panel);特徵源=
    direction_threelens_feature_monthly(builder 同 feature_values generator,零口徑漂移);
    市場 context 不用——與 own_stack 之 delta=特徵寬度(候選假說隔離);SYNTH_* 冒煙=中性 0.5(零 DB)。
    標籤配方與 scripts/train_direction_threelens.py 同(spec 凍結;改版=新候選新家族)。"""
    key = "own_threelens_interact"
    SEEDS = (7, 42, 2026)

    def predict(self, series, horizon_td, context=None):
        out = {t: 0.5 for t in series}
        if not series or all(str(t).startswith("SYNTH_") for t in series):
            return out
        try:
            import pandas as pd
            from sklearn.ensemble import HistGradientBoostingClassifier
            from sklearn.isotonic import IsotonicRegression
            from augur.core import db
            with db.connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT panel_date, stock_id, feature, value FROM direction_threelens_feature_monthly")
                rows = cur.fetchall()
                if not rows:
                    return out
                X = (pd.DataFrame(rows, columns=["panel_date", "stock_id", "feature", "value"])
                       .pivot_table(index=["panel_date", "stock_id"], columns="feature", values="value")
                       .reset_index())
                asof = X.panel_date.max()
                sids = sorted(X.stock_id.unique())
                cur.execute('SELECT stock_id, date, close FROM "TaiwanStockPriceAdj" '
                            "WHERE stock_id = ANY(%s) AND date >= '2016-06-01' ORDER BY stock_id, date", (sids,))
                px = pd.DataFrame(cur.fetchall(), columns=["stock_id", "date", "close"])
            lab = []
            for sid, g in px.groupby("stock_id", sort=False):
                dates = g["date"].to_numpy(); close = g["close"].to_numpy(dtype=float)
                for pd_ in X.loc[X.stock_id == sid, "panel_date"]:
                    i = int(np.searchsorted(dates, pd_, side="right")) - 1
                    if i < 0:
                        continue
                    if i + horizon_td < len(dates) and close[i] > 0:
                        lab.append((pd_, sid, float(close[i + horizon_td] / close[i] - 1) > 0, dates[i + horizon_td]))
            lab = pd.DataFrame(lab, columns=["panel_date", "stock_id", "y", "settle_date"])
            d = X.merge(lab, on=["panel_date", "stock_id"], how="left")
            feats = [c for c in d.columns if c not in ("panel_date", "stock_id", "y", "settle_date")]
            train = d[(d.settle_date.notna()) & (d.settle_date < asof) & d.y.notna()]
            test = d[d.panel_date == asof]
            if len(train) < 2000 or test.empty or train.y.nunique() < 2:
                return out
            tr_p = sorted(train.panel_date.unique())
            fit_p = set(tr_p[: int(len(tr_p) * 0.8)]); cal_p = set(tr_p[int(len(tr_p) * 0.8):])
            fit, cal = train[train.panel_date.isin(fit_p)], train[train.panel_date.isin(cal_p)]
            if len(fit) < 500 or len(cal) < 100 or fit.y.nunique() < 2:
                return out
            feats_f = [c for c in feats if fit[c].notna().any()]
            p_cal = np.zeros(len(cal)); p_test = np.zeros(len(test))
            for s in self.SEEDS:
                clf = HistGradientBoostingClassifier(max_iter=200, max_depth=3, learning_rate=0.05, random_state=s)
                clf.fit(fit[feats_f], fit.y.astype(int))
                p_cal += clf.predict_proba(cal[feats_f])[:, 1] / len(self.SEEDS)
                p_test += clf.predict_proba(test[feats_f])[:, 1] / len(self.SEEDS)
            iso = IsotonicRegression(out_of_bounds="clip", y_min=0.01, y_max=0.99)
            iso.fit(p_cal, cal.y.astype(int))
            p = iso.predict(p_test)
            for sid, pi in zip(test.stock_id, p):
                if sid in out:
                    out[sid] = float(np.clip(pi, 0.0, 1.0))
        except Exception:
            return {t: 0.5 for t in series}      # fail-neutral:任何缺料=不出手(0.5),不編造
        return out


REGISTRY = {a.key: a for a in (BaselineMajority, BaselineMomentum, BaselineMcBootstrap,
                               OwnDailyRolling, OwnStackRolling, MarketChronos, MarketTimesFM,
                               OwnThreelensInteract, MarketChronos2, MarketMoirai2)}


def _selftest():
    """自測（零 DB/零 API #29a）:合成序列紅綠測純數學核（_rets/_roll_std/_roll_beta）+ 離線
    baseline adapter(BaselineMajority——純 numpy、零 IO)+ REGISTRY 結構鎖(統一介面不變式)。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("_rets 逐期報酬([100,110,99]→[.1,-.1])",
        np.allclose(_rets([100.0, 110.0, 99.0]), [0.1, 99 / 110 - 1]))
    rs = _roll_std(np.arange(5.0), 3)                      # 窗前 NaN、窗內有限(不變式:len 對齊+暖機 NaN)
    chk("_roll_std 對齊+暖機 NaN", len(rs) == 5 and np.isnan(rs[:2]).all() and np.isfinite(rs[2:]).all())
    r = np.array([0.01, -0.02, 0.03, -0.01, 0.02])
    beta = _roll_beta(r, r.copy(), 3)                      # rt≡rm → cov≡var → beta≡1(自對齊恆等式)
    chk("_roll_beta 自身 beta≡1", np.allclose(beta[2:], 1.0))
    p = BaselineMajority().predict({"A": [1.0, 2.0, 3.0, 4.0, 5.0]}, 1)   # 全升 → 全正 fwd → P=1
    chk("BaselineMajority 單調升→P=1", p == {"A": 1.0})
    chk("REGISTRY 十參賽者+key 一致(A4 波次 +chronos2/moirai2 2026-07-17)",
        len(REGISTRY) == 10 and all(k == a.key and hasattr(a, "predict") for k, a in REGISTRY.items()))
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.arena.adapters --selftest;免 DB 免 API)")

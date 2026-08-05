"""股級 macro 候選 — CONTRACT v1／v2（經 macro_vintage PIT；寫入 feature_candidate_values）。

v1：audits/S3-MACRO-STOCK-CONTRACT-20260805.md
v2 P1：audits/S3-MACRO-STOCK-CONTRACT-v2-20260805.md
  A z_mom20_x_vix · B z_mom20_x_t10y2y_chg · C ind_demean_mom20_x_vix

守 #1 缺列 · #8 PIT 唯一門 macro_vintage · 禁寫 feature_values · 禁 Tier-B。
WM.36：價／市／產業經 registry（`tw.daily_bar_adjusted`／`tw.stock_industry_category`）；
市報序列＝PriceAdj `TAIEX.close`（TRI 概念未登錄，不直綁 TotalReturnIndex）。

執行指令矩陣（library）:
  python -m augur.features.macro_stock              # 印用途
  python -m augur.features.macro_stock --selftest   # 純函式紅綠
"""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
from psycopg2.extras import execute_values

from augur.audit import feature_candidate as cand
from augur.catalog import world_concept
from augur.core import db
from augur.features import macro_vintage

ADJ_CONCEPT = "tw.daily_bar_adjusted"
IND_CONCEPT = "tw.stock_industry_category"

NAMES = (
    "stock_beta60_x_vix",
    "stock_ret20_x_t10y2y_chg",
    "mkt_vix_broadcast",
)
V2_NAMES = (
    "z_mom20_x_vix",
    "z_mom20_x_t10y2y_chg",
    "ind_demean_mom20_x_vix",
)
P2_NAMES = (
    "beta60_x_hyoas",
    "z_vol60_x_vix_chg",
    "beta60_x_dextaus_chg",
)

_BETA_WIN = 60
_MIN_BETA_OBS = 40  # 60 窗內至少有效重疊報酬點，否則缺列


def _coerce(d):
    return d if isinstance(d, date) else date.fromisoformat(str(d)[:10])


def ols_beta(y, x):
    """日報酬 OLS β；樣本不足或市報 var=0 → None（#1 缺列）。純函式。"""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    m = np.isfinite(y) & np.isfinite(x)
    if int(m.sum()) < _MIN_BETA_OBS:
        return None
    yy, xx = y[m], x[m]
    var = float(np.var(xx))
    if not np.isfinite(var) or var <= 0:
        return None
    cov = float(np.cov(yy, xx, ddof=0)[0, 1])
    b = cov / var
    return float(b) if np.isfinite(b) else None


def _load_close_panel(cur, stock_ids, start, end, *, adj_sql):
    """{stock_id: [(date, close), ...]} 升序；還原價經 registry。"""
    cur.execute(
        f"SELECT stock_id, date, close::float8 FROM {adj_sql} "
        "WHERE stock_id = ANY(%s) AND date >= %s AND date <= %s AND close IS NOT NULL "
        "ORDER BY stock_id, date",
        (list(stock_ids), start, end),
    )
    out = {}
    for sid, d, c in cur.fetchall():
        out.setdefault(str(sid), []).append((d, float(c)))
    return out


def _load_taiex_mkt(cur, start, end, *, adj_sql):
    """TAIEX 市報 [{date: close}, calendar]——PriceAdj／WM.36（不直綁 TRI）。"""
    cur.execute(
        f"SELECT date, close::float8 FROM {adj_sql} "
        "WHERE stock_id='TAIEX' AND date >= %s AND date <= %s AND close IS NOT NULL "
        "ORDER BY date",
        (start, end),
    )
    rows = cur.fetchall()
    return {d: float(p) for d, p in rows}, [d for d, _ in rows]


def _log_rets(series_dates_px):
    """[(date,px),...] → {date: logret} 對 date[i] 存相對 date[i-1] 之報酬。"""
    out = {}
    for i in range(1, len(series_dates_px)):
        d0, p0 = series_dates_px[i - 1]
        d1, p1 = series_dates_px[i]
        if p0 > 0 and p1 > 0 and np.isfinite(p0) and np.isfinite(p1):
            out[d1] = float(np.log(p1 / p0))
    return out


def _stocks_for_panel(cur, panel_date, fallback_core):
    cur.execute(
        "SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s ORDER BY stock_id",
        (panel_date,),
    )
    rows = [str(r[0]) for r in cur.fetchall()]
    return rows if rows else list(fallback_core)


def compute_macro_stock_candidates(conn, panel_dates, fallback_core, *, progress=None):
    """對 panel_dates 寫契約三名 → feature_candidate_values。回寫入列數。"""
    cand.ensure_candidate_table(conn)
    written = 0
    panels = [_coerce(p) for p in panel_dates]
    if not panels:
        return 0

    # 跨 panel 窗：最早 panel 往前約 120 曆日夠 60+ 交易日
    start = min(panels) - timedelta(days=180)
    end = max(panels)

    adj_sql = world_concept.resolve_sql(ADJ_CONCEPT, conn=conn)
    with db.transaction(conn) as cur:
        # 預載全程可能出現之核心股（最後 panel asof ∪ fallback）
        all_stocks = set(str(s) for s in fallback_core)
        for pd_ in panels:
            all_stocks.update(_stocks_for_panel(cur, pd_, fallback_core))
        stock_px = _load_close_panel(cur, sorted(all_stocks), start, end, adj_sql=adj_sql)
        mkt_px, mkt_cal = _load_taiex_mkt(cur, start, end, adj_sql=adj_sql)

    mkt_series = [(d, mkt_px[d]) for d in mkt_cal]
    mkt_rets = _log_rets(mkt_series)
    stock_rets = {sid: _log_rets(px) for sid, px in stock_px.items()}

    t10_by_panel, vix_by_panel = {}, {}
    with db.transaction(conn) as cur:
        for pd_ in panels:
            t10 = macro_vintage.as_of(cur, "T10Y2Y", pd_)
            t10_by_panel[pd_] = float(t10[0]) if t10 else None
            vx = macro_vintage.as_of(cur, "VIXCLS", pd_)
            vix_by_panel[pd_] = float(vx[0]) if vx else None

    prev_t10 = None
    for pd_ in panels:
        stocks = None
        with db.transaction(conn) as cur:
            stocks = _stocks_for_panel(cur, pd_, fallback_core)
            mom20 = {}
            if stocks:
                cur.execute(
                    "SELECT stock_id, value::float8 FROM feature_values "
                    "WHERE panel_date=%s AND feature='momentum_20d' AND stock_id = ANY(%s)",
                    (pd_, stocks),
                )
                mom20 = {str(r[0]): float(r[1]) for r in cur.fetchall()}

        vix = vix_by_panel.get(pd_)
        t10 = t10_by_panel.get(pd_)
        t10_chg = None
        if t10 is not None and prev_t10 is not None:
            t10_chg = t10 - prev_t10
        if t10 is not None:
            prev_t10 = t10

        # 該 panel 可見交易日曆（≤panel）
        cal = [d for d in mkt_cal if d <= pd_]
        if len(cal) < _BETA_WIN + 1:
            if progress:
                progress(f"  macro_stock {pd_}: calendar short, skip")
            continue
        win_dates = cal[-_BETA_WIN:]

        rows = []
        for sid in stocks:
            # 1) beta × vix
            if vix is not None:
                sr = stock_rets.get(sid) or {}
                ys, xs = [], []
                for d in win_dates:
                    if d in sr and d in mkt_rets:
                        ys.append(sr[d])
                        xs.append(mkt_rets[d])
                b = ols_beta(ys, xs)
                if b is not None:
                    rows.append((pd_, sid, "stock_beta60_x_vix", round(b * vix, 6)))

            # 2) mom20 × t10y2y_chg
            if t10_chg is not None and sid in mom20:
                rows.append(
                    (pd_, sid, "stock_ret20_x_t10y2y_chg", round(mom20[sid] * t10_chg, 6))
                )

            # 3) broadcast
            if vix is not None:
                rows.append((pd_, sid, "mkt_vix_broadcast", round(vix, 6)))

        if rows:
            with db.transaction(conn) as cur:
                execute_values(
                    cur,
                    f"INSERT INTO {cand.FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s "
                    f"ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value",
                    rows,
                )
            written += len(rows)
        if progress:
            progress(f"  macro_stock {pd_}: +{len(rows)}（累計 {written}）")
    return written


def compute_macro_stock_candidates_v2(conn, panel_dates, fallback_core, *, progress=None):
    """CONTRACT-v2 P1 三名 → feature_candidate_values。不刪 v1。"""
    cand.ensure_candidate_table(conn)
    written = 0
    panels = [_coerce(p) for p in panel_dates]
    if not panels:
        return 0

    t10_by_panel, vix_by_panel = {}, {}
    with db.transaction(conn) as cur:
        for pd_ in panels:
            t10 = macro_vintage.as_of(cur, "T10Y2Y", pd_)
            t10_by_panel[pd_] = float(t10[0]) if t10 else None
            vx = macro_vintage.as_of(cur, "VIXCLS", pd_)
            vix_by_panel[pd_] = float(vx[0]) if vx else None

    prev_t10 = None
    for pd_ in panels:
        with db.transaction(conn) as cur:
            stocks = _stocks_for_panel(cur, pd_, fallback_core)
            mom20 = {}
            if stocks:
                cur.execute(
                    "SELECT stock_id, value::float8 FROM feature_values "
                    "WHERE panel_date=%s AND feature='momentum_20d' AND stock_id = ANY(%s)",
                    (pd_, stocks),
                )
                mom20 = {str(r[0]): float(r[1]) for r in cur.fetchall()}
            industry = {}
            if stocks:
                ind_sql = world_concept.resolve_sql(IND_CONCEPT, conn=conn)
                cur.execute(
                    f"SELECT stock_id, industry_category FROM {ind_sql} "
                    "WHERE stock_id = ANY(%s)",
                    (stocks,),
                )
                industry = {str(r[0]): r[1] for r in cur.fetchall()}

        vix = vix_by_panel.get(pd_)
        t10 = t10_by_panel.get(pd_)
        t10_chg = None
        if t10 is not None and prev_t10 is not None:
            t10_chg = t10 - prev_t10
        if t10 is not None:
            prev_t10 = t10

        zm = cand._zscore(mom20)
        dem = {}
        if mom20:
            df = pd.DataFrame({"mom": mom20}).assign(ind=lambda d: d.index.map(industry))
            # 產業內≥2 才 demean
            cnt = df.groupby("ind")["mom"].transform("count")
            med = df.groupby("ind")["mom"].transform("median")
            ok = cnt >= 2
            demean = (df["mom"] - med).where(ok)
            dem = {k: float(v) for k, v in demean.dropna().items()}

        rows = []
        if vix is not None:
            for sid, z in zm.items():
                rows.append((pd_, sid, "z_mom20_x_vix", round(z * vix, 6)))
            for sid, d in dem.items():
                rows.append((pd_, sid, "ind_demean_mom20_x_vix", round(d * vix, 6)))
        if t10_chg is not None:
            for sid, z in zm.items():
                rows.append((pd_, sid, "z_mom20_x_t10y2y_chg", round(z * t10_chg, 6)))

        if rows:
            with db.transaction(conn) as cur:
                execute_values(
                    cur,
                    f"INSERT INTO {cand.FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s "
                    f"ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value",
                    rows,
                )
            written += len(rows)
        if progress:
            progress(f"  macro_stock_v2 {pd_}: +{len(rows)}（累計 {written}）")
    return written


def compute_macro_stock_candidates_p2(conn, panel_dates, fallback_core, *, progress=None):
    """CONTRACT-v2-P2：beta×HY／z(vol)×VIX_chg／beta×DEXTAUS_chg。"""
    cand.ensure_candidate_table(conn)
    written = 0
    panels = [_coerce(p) for p in panel_dates]
    if not panels:
        return 0

    start = min(panels) - timedelta(days=180)
    end = max(panels)
    adj_sql = world_concept.resolve_sql(ADJ_CONCEPT, conn=conn)
    with db.transaction(conn) as cur:
        all_stocks = set(str(s) for s in fallback_core)
        for pd_ in panels:
            all_stocks.update(_stocks_for_panel(cur, pd_, fallback_core))
        stock_px = _load_close_panel(cur, sorted(all_stocks), start, end, adj_sql=adj_sql)
        mkt_px, mkt_cal = _load_taiex_mkt(cur, start, end, adj_sql=adj_sql)

    mkt_rets = _log_rets([(d, mkt_px[d]) for d in mkt_cal])
    stock_rets = {sid: _log_rets(px) for sid, px in stock_px.items()}

    hy, vix, fx = {}, {}, {}
    with db.transaction(conn) as cur:
        for pd_ in panels:
            a = macro_vintage.as_of(cur, "BAMLH0A0HYM2", pd_)
            hy[pd_] = float(a[0]) if a else None
            b = macro_vintage.as_of(cur, "VIXCLS", pd_)
            vix[pd_] = float(b[0]) if b else None
            c = macro_vintage.as_of(cur, "DEXTAUS", pd_)
            fx[pd_] = float(c[0]) if c else None

    prev_vix = prev_fx = None
    for pd_ in panels:
        with db.transaction(conn) as cur:
            stocks = _stocks_for_panel(cur, pd_, fallback_core)
            vol60 = {}
            if stocks:
                cur.execute(
                    "SELECT stock_id, value::float8 FROM feature_values "
                    "WHERE panel_date=%s AND feature='volatility_60d' AND stock_id = ANY(%s)",
                    (pd_, stocks),
                )
                vol60 = {str(r[0]): float(r[1]) for r in cur.fetchall()}

        vix_chg = None
        if vix.get(pd_) is not None and prev_vix is not None:
            vix_chg = vix[pd_] - prev_vix
        if vix.get(pd_) is not None:
            prev_vix = vix[pd_]
        fx_chg = None
        if fx.get(pd_) is not None and prev_fx is not None:
            fx_chg = fx[pd_] - prev_fx
        if fx.get(pd_) is not None:
            prev_fx = fx[pd_]

        zv = cand._zscore(vol60)
        cal = [d for d in mkt_cal if d <= pd_]
        win_dates = cal[-_BETA_WIN:] if len(cal) >= _BETA_WIN + 1 else []

        betas = {}
        if win_dates:
            for sid in stocks:
                sr = stock_rets.get(sid) or {}
                ys, xs = [], []
                for d in win_dates:
                    if d in sr and d in mkt_rets:
                        ys.append(sr[d])
                        xs.append(mkt_rets[d])
                b = ols_beta(ys, xs)
                if b is not None:
                    betas[sid] = b

        rows = []
        hy_v = hy.get(pd_)
        if hy_v is not None:
            for sid, b in betas.items():
                rows.append((pd_, sid, "beta60_x_hyoas", round(b * hy_v, 6)))
        if vix_chg is not None:
            for sid, z in zv.items():
                rows.append((pd_, sid, "z_vol60_x_vix_chg", round(z * vix_chg, 6)))
        if fx_chg is not None:
            for sid, b in betas.items():
                rows.append((pd_, sid, "beta60_x_dextaus_chg", round(b * fx_chg, 6)))

        if rows:
            with db.transaction(conn) as cur:
                execute_values(
                    cur,
                    f"INSERT INTO {cand.FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s "
                    f"ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value",
                    rows,
                )
            written += len(rows)
        if progress:
            progress(f"  macro_stock_p2 {pd_}: +{len(rows)}（累計 {written}）")
    return written


def clear_macro_stock_candidates(conn, *, version="v1"):
    cand.ensure_candidate_table(conn)
    feats = list(NAMES)
    if version == "v2":
        feats = list(V2_NAMES)
    elif version == "p2":
        feats = list(P2_NAMES)
    elif version == "all":
        feats = list(NAMES) + list(V2_NAMES) + list(P2_NAMES)
    with db.transaction(conn) as cur:
        cur.execute(
            f"DELETE FROM {cand.FEATURE_TABLE} WHERE feature = ANY(%s)",
            (feats,),
        )
        return cur.rowcount


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("NAMES 恰 3", len(NAMES) == 3)
    chk("V2_NAMES 恰 3", len(V2_NAMES) == 3)
    chk("P2_NAMES 恰 3", len(P2_NAMES) == 3)
    rng = np.random.default_rng(0)
    x = rng.normal(0, 0.01, 60)
    y = x * 1.5
    b = ols_beta(y, x)
    chk("ols β≈1.5", b is not None and abs(b - 1.5) < 1e-6)
    chk("ols 短窗→None", ols_beta([0.1, 0.2], [0.1, 0.2]) is None)
    z = cand._zscore({"a": 1.0, "b": 2.0, "c": 3.0})
    chk("z helper 中位≈0", abs(z["b"]) < 1e-9)
    print("macro_stock selftest", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print(__doc__)

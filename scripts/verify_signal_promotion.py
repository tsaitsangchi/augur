#!/usr/bin/env python
"""augur 通用訊號提拔複核 — 對深度掃描浮現之候選跑完整關卡(as-of + HAC Eff-t + 多 seed 增量)。

🎯 這支在做什麼(白話):深度 as-of 掃描(run_deep_interaction_scan)浮現之候選,逐個走完整漏斗定生死:
- dealer_net_r:自營商淨買/量(三 horizon as-of HAC-t 2.2/3.0/2.7 最穩健單因子)
- foreign_pct_x_turnover:wz(外資持股%)×wz(週轉率)(H60 as-of HAC-t 5.4 最強交互)
- foreign_trust_div:wz(外資淨買比)×wz(投信淨買比)(背離交互 HAC-t -3.8)
各候選:as-of 逐 panel IC + iid/HAC-t + 多 seed 對生產集增量 Δ(對 34 特徵是否真增量)。
判據:HAC-t |≥2| + 多 seed Δ 穩定為正 → 提拔;否則維持候選。驗後清列、不入生產。
守 #8 · #11 · #12 · #15 · #28。用法:python scripts/verify_signal_promotion.py --cands dealer_net_r,foreign_pct_x_turnover,foreign_trust_div --h 20,60 --seeds 3

執行指令矩陣:
  python scripts/verify_signal_promotion.py
"""
import argparse

import numpy as np
from psycopg2.extras import execute_values

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.evaluation import baseline, metrics
from augur.evaluation import label as label_mod


def _wz(d):
    items = [(k, float(v)) for k, v in d.items() if v is not None and np.isfinite(float(v))]
    if len(items) < 30:
        return {}
    v = np.array([x for _, x in items]); mu, sd = v.mean(), v.std()
    if sd == 0:
        return {}
    return {k: float(z) for (k, _), z in zip(items, np.clip((v - mu) / sd, -3, 3))}


def _panel_inputs(cur, ps, stk):
    """拉某 panel 算候選所需 raw → dict of {sid:val}。"""
    def col(sql):
        cur.execute(sql, (ps, stk)); return {str(r[0]): float(r[1]) for r in cur.fetchall() if r[1] is not None}
    vol = col('SELECT stock_id,"Trading_Volume" FROM "TaiwanStockPrice" WHERE date::text=%s AND stock_id=ANY(%s)')
    tno = col('SELECT stock_id,"Trading_turnover" FROM "TaiwanStockPrice" WHERE date::text=%s AND stock_id=ANY(%s)')
    fpct = col('SELECT stock_id,"ForeignInvestmentSharesRatio" FROM "TaiwanStockShareholding" WHERE date::text=%s AND stock_id=ANY(%s)')
    cur.execute("SELECT stock_id,name,COALESCE(buy,0)-COALESCE(sell,0) FROM \"TaiwanStockInstitutionalInvestorsBuySell\" WHERE date::text=%s AND stock_id=ANY(%s)", (ps, stk))
    fnet, tnet, dnet = {}, {}, {}
    for sid, nm, net in cur.fetchall():
        sid = str(sid); net = float(net or 0)
        if nm == "Foreign_Investor": fnet[sid] = fnet.get(sid, 0) + net
        elif nm == "Investment_Trust": tnet[sid] = tnet.get(sid, 0) + net
        elif nm and nm.startswith("Dealer"): dnet[sid] = dnet.get(sid, 0) + net
    return vol, tno, fpct, fnet, tnet, dnet


def _candidate_values(cand, vol, tno, fpct, fnet, tnet, dnet):
    """候選名 → {sid:value}。"""
    if cand == "dealer_net_r":
        return {s: dnet[s] / vol[s] for s in dnet if vol.get(s, 0) > 0}
    if cand == "foreign_pct_x_turnover":
        zf, zt = _wz(fpct), _wz(tno)
        return {s: zf[s] * zt[s] for s in set(zf) & set(zt)}
    if cand == "foreign_trust_div":
        fr = {s: fnet[s] / vol[s] for s in fnet if vol.get(s, 0) > 0}
        tr = {s: tnet[s] / vol[s] for s in tnet if vol.get(s, 0) > 0}
        zf, zt = _wz(fr), _wz(tr)
        return {s: zf[s] * zt[s] for s in set(zf) & set(zt)}
    raise ValueError(cand)


def _compute(conn, panels, cand):
    written = 0
    for pd_ in panels:
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (pd_,))
            stk = [str(r[0]) for r in cur.fetchall()]
            if not stk:
                continue
            vals = _candidate_values(cand, *_panel_inputs(cur, str(pd_), stk))
        rows = [(pd_, s, cand, round(v, 6)) for s, v in vals.items() if np.isfinite(v)]
        if rows:
            with db.transaction(conn) as cur:
                execute_values(cur, "INSERT INTO feature_values (panel_date, stock_id, feature, value) VALUES %s "
                               "ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", rows)
            written += len(rows)
    return written


def _ic_series(conn, panels, h, feat, cal):
    out = {}
    for pd_ in panels:
        stk = baseline._asof_stocks(conn, pd_)
        sids, X = baseline._panel_matrix(conn, pd_, stk, [feat])
        if len(sids) < 5:
            continue
        lab = label_mod.labels(conn, pd_, sids, h, calendar=cal)
        ic = metrics.rank_ic({s: X[i, 0] for i, s in enumerate(sids)}, lab)
        if ic is not None:
            out[pd_] = ic
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cands", default="dealer_net_r,foreign_pct_x_turnover,foreign_trust_div")
    ap.add_argument("--h", default="20,60")
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()
    cands = args.cands.split(","); hs = [int(x) for x in args.h.split(",")]

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
            panels = [r[0] for r in cur.fetchall()]
        cal = label_mod.full_calendar(conn)
        for c in cands:
            print(f"算 as-of 候選 {c}… 寫入 {_compute(conn, panels, c):,} 值")
        prod = [x for x in baseline.canonical_features(conn, panels) if x not in cands]

        print("\n══ 1. as-of 單因子 rank IC:iid-t vs HAC-t（去相關 G8）══")
        print(f"{'candidate':24s} {'H':>3s} {'IC':>8s} {'iid-t':>7s} {'HAC-t':>7s} {'勝率':>5s} {'n':>3s}")
        for c in cands:
            for h in hs:
                ser = _ic_series(conn, panels, h, c, cal)
                s = metrics.summarize(ser); hac = metrics.effective_t_hac(ser)
                if s["mean_ic"] is None:
                    print(f"{c:24s} {h:>3d}   n/a"); continue
                print(f"{c:24s} {h:>3d} {s['mean_ic']:>+8.4f} {s['effective_t']:>7.2f} "
                      f"{(hac if hac is not None else float('nan')):>7.2f} {s['hit_rate']:>5.2f} {s['n_panels']:>3d}")

        print(f"\n══ 2. 多 seed 增量(生產基準 {len(prod)} 特徵、{args.seeds} seed)══")
        for c in cands:
            for h in hs:
                bi, ai = {"B2_ridge": [], "M1_gbdt": []}, {"B2_ridge": [], "M1_gbdt": []}
                for k in range(args.seeds):
                    rb = baseline.run_ladder(conn, panels, h, None, feats=prod, seed=42 + k, asof=True)
                    ra = baseline.run_ladder(conn, panels, h, None, feats=prod + [c], seed=42 + k, asof=True)
                    for m in ("B2_ridge", "M1_gbdt"):
                        if rb[m]["mean_ic"] is not None: bi[m].append(rb[m]["mean_ic"])
                        if ra[m]["mean_ic"] is not None: ai[m].append(ra[m]["mean_ic"])
                for m in ("B2_ridge", "M1_gbdt"):
                    b = np.mean(bi[m]) if bi[m] else float('nan'); a = np.mean(ai[m]) if ai[m] else float('nan')
                    print(f"   {c:24s} H={h:>3d} {m:10s} {b:+.4f} → {a:+.4f}  Δ={a-b:+.4f}")

        with db.transaction(conn) as cur:
            cur.execute("DELETE FROM feature_values WHERE feature = ANY(%s)", (cands,))
            print(f"\n清候選列:{cur.rowcount} 列刪(實驗、不入生產)")
        print("判讀:HAC-t |≥2| + 多 seed Δ 穩定為正 → 提拔;否則維持候選(冗餘)。")


if __name__ == "__main__":
    main()

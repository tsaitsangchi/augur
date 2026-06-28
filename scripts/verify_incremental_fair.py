#!/usr/bin/env python
"""augur 公平增量測 — 修稀疏候選的覆蓋假象(候選缺值補 panel 中位 → base 與 +候選同宇宙)。

🎯 這支在做什麼(白話):verify_signal_promotion 揭一個方法瑕疵——_panel_matrix 剔除缺任一特徵之股,
故加稀疏候選(覆蓋 ~63%)會掉 37% 股 → IC 跌純屬宇宙縮小假象、非候選有害(三候選 Δ 一致即證)。
此支修正:候選缺值以**該 panel 橫斷面中位數補滿**(中性、rank 居中)→ 全 asof 宇宙保留 → base 與
+候選跑**同一宇宙**,Δ 才真反映候選增量。對 step-1 已 as-of 顯著之候選(dealer_net_r/foreign_pct×turnover/
foreign_trust_div)定真生死。守 #8 · #11 · #15(揭並修自身測之瑕疵)· #28。
用法:PYTHONPATH=src python scripts/verify_incremental_fair.py --h 20,60 --seeds 3
"""
import argparse

import numpy as np
from psycopg2.extras import execute_values

from augur.core import db
from augur.evaluation import baseline
from augur.evaluation import label as label_mod

CANDS = ["dealer_net_r", "foreign_pct_x_turnover", "foreign_trust_div"]


def _wz(d):
    items = [(k, float(v)) for k, v in d.items() if v is not None and np.isfinite(float(v))]
    if len(items) < 30:
        return {}
    v = np.array([x for _, x in items]); mu, sd = v.mean(), v.std()
    if sd == 0:
        return {}
    return {k: float(z) for (k, _), z in zip(items, np.clip((v - mu) / sd, -3, 3))}


def _vals(cur, ps, stk, cand):
    def col(sql):
        cur.execute(sql, (ps, stk)); return {str(r[0]): float(r[1]) for r in cur.fetchall() if r[1] is not None}
    vol = col('SELECT stock_id,"Trading_Volume" FROM "TaiwanStockPrice" WHERE date::text=%s AND stock_id=ANY(%s)')
    if cand == "foreign_pct_x_turnover":
        tno = col('SELECT stock_id,"Trading_turnover" FROM "TaiwanStockPrice" WHERE date::text=%s AND stock_id=ANY(%s)')
        fpct = col('SELECT stock_id,"ForeignInvestmentSharesRatio" FROM "TaiwanStockShareholding" WHERE date::text=%s AND stock_id=ANY(%s)')
        zf, zt = _wz(fpct), _wz(tno)
        return {s: zf[s] * zt[s] for s in set(zf) & set(zt)}
    cur.execute("SELECT stock_id,name,COALESCE(buy,0)-COALESCE(sell,0) FROM \"TaiwanStockInstitutionalInvestorsBuySell\" WHERE date::text=%s AND stock_id=ANY(%s)", (ps, stk))
    fnet, tnet, dnet = {}, {}, {}
    for sid, nm, net in cur.fetchall():
        sid = str(sid); net = float(net or 0)
        if nm == "Foreign_Investor": fnet[sid] = fnet.get(sid, 0) + net
        elif nm == "Investment_Trust": tnet[sid] = tnet.get(sid, 0) + net
        elif nm and nm.startswith("Dealer"): dnet[sid] = dnet.get(sid, 0) + net
    if cand == "dealer_net_r":
        return {s: dnet[s] / vol[s] for s in dnet if vol.get(s, 0) > 0}
    if cand == "foreign_trust_div":
        fr = {s: fnet[s] / vol[s] for s in fnet if vol.get(s, 0) > 0}
        tr = {s: tnet[s] / vol[s] for s in tnet if vol.get(s, 0) > 0}
        zf, zt = _wz(fr), _wz(tr)
        return {s: zf[s] * zt[s] for s in set(zf) & set(zt)}
    raise ValueError(cand)


def _compute_dense(conn, panels, cand):
    """算候選、**缺值補 panel 中位**(全 asof 股保留)→ 寫 <cand>_imp。回(寫入, 真實覆蓋率)。"""
    name = cand + "_imp"
    written = real = total = 0
    for pd_ in panels:
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (pd_,))
            stk = [str(r[0]) for r in cur.fetchall()]
            if not stk:
                continue
            vals = _vals(cur, str(pd_), stk, cand)
        real += len(vals); total += len(stk)
        med = float(np.median(list(vals.values()))) if vals else 0.0
        rows = [(pd_, s, name, round(float(vals.get(s, med)), 6)) for s in stk]   # 缺→中位補滿
        with db.transaction(conn) as cur:
            execute_values(cur, "INSERT INTO feature_values (panel_date, stock_id, feature, value) VALUES %s "
                           "ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", rows)
        written += len(rows)
    return written, (real / total if total else 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--h", default="20,60"); ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()
    hs = [int(x) for x in args.h.split(",")]
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
            panels = [r[0] for r in cur.fetchall()]
        imp_names = []
        for c in CANDS:
            w, cov = _compute_dense(conn, panels, c)
            imp_names.append(c + "_imp")
            print(f"{c}_imp:寫 {w:,} 值(真實覆蓋 {cov:.0%}、餘補中位)")
        prod = [x for x in baseline.canonical_features(conn, panels) if x not in imp_names]
        print(f"\n══ 公平增量(同宇宙、base {len(prod)} 特徵、{args.seeds} seed)══")
        print(f"   {'candidate':24s} {'H':>3s} {'model':10s} {'base':>8s} {'+cand':>8s} {'Δ':>8s}")
        for c in CANDS:
            name = c + "_imp"
            for h in hs:
                bi, ai = {"B2_ridge": [], "M1_gbdt": []}, {"B2_ridge": [], "M1_gbdt": []}
                for k in range(args.seeds):
                    rb = baseline.run_ladder(conn, panels, h, None, feats=prod, seed=42 + k, asof=True)
                    ra = baseline.run_ladder(conn, panels, h, None, feats=prod + [name], seed=42 + k, asof=True)
                    for m in ("B2_ridge", "M1_gbdt"):
                        if rb[m]["mean_ic"] is not None: bi[m].append(rb[m]["mean_ic"])
                        if ra[m]["mean_ic"] is not None: ai[m].append(ra[m]["mean_ic"])
                for m in ("B2_ridge", "M1_gbdt"):
                    b = np.mean(bi[m]) if bi[m] else float('nan'); a = np.mean(ai[m]) if ai[m] else float('nan')
                    mark = " ✅+" if a - b > 0.002 else (" ~" if abs(a - b) <= 0.002 else " ✗−")
                    print(f"   {c:24s} {h:>3d} {m:10s} {b:>+8.4f} {a:>+8.4f} {a-b:>+8.4f}{mark}")
        with db.transaction(conn) as cur:
            cur.execute("DELETE FROM feature_values WHERE feature = ANY(%s)", (imp_names,))
            print(f"\n清候選列:{cur.rowcount} 列刪")
        print("判讀(公平、同宇宙):Δ 穩定 >+0.002 → 真增量提拔;~0 → 冗餘;<0 → 有害。")


if __name__ == "__main__":
    main()

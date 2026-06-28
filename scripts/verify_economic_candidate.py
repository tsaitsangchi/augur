#!/usr/bin/env python
"""augur 候選經濟價值測(#14 靈魂判準) — foreign_trust_div 能否提升投組 net Sharpe/Calmar(非僅 IC)。

🎯 這支在做什麼(白話):IC 增量小(GBDT-H20 +0.0065),但靈魂成功定義是**經濟價值**(#14)。此支問終極問題:
把 foreign_trust_div(外資×投信背離、imputed 同宇宙)加入生產集,**投組扣成本後的 Sharpe/Calmar/MaxDD 有變好嗎?**
- 候選缺值補 panel 中位(同宇宙、修覆蓋假象)
- base(33 特徵)vs +候選,headline 配置 top10%/equal、h=20/60、Ridge + GBDT(3 seed 均)
- 扣台股來回成本 0.585%,對比等權基準 net
判據(#14):net Sharpe/Calmar **有感提升**(非僅 IC 邊際)→ 提拔;持平/變差 → 維持候選(IC 邊際非真經濟 alpha)。
守 #8 · #12 · #14 · #15(net 雙報、對基準)· #28。用法:PYTHONPATH=src python scripts/verify_economic_candidate.py
"""
import argparse

import numpy as np
from psycopg2.extras import execute_values

from augur.core import db
from augur.evaluation import baseline, portfolio

CAND = "foreign_trust_div"
IMP = CAND + "_imp"
COST = 0.00585


def _wz(d):
    items = [(k, float(v)) for k, v in d.items() if v is not None and np.isfinite(float(v))]
    if len(items) < 30:
        return {}
    v = np.array([x for _, x in items]); mu, sd = v.mean(), v.std()
    if sd == 0:
        return {}
    return {k: float(z) for (k, _), z in zip(items, np.clip((v - mu) / sd, -3, 3))}


def _compute_dense(conn, panels):
    written = real = total = 0
    for pd_ in panels:
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (pd_,))
            stk = [str(r[0]) for r in cur.fetchall()]
            if not stk:
                continue
            cur.execute('SELECT stock_id,"Trading_Volume" FROM "TaiwanStockPrice" WHERE date::text=%s AND stock_id=ANY(%s)', (str(pd_), stk))
            vol = {str(r[0]): float(r[1]) for r in cur.fetchall() if r[1] is not None}
            cur.execute("SELECT stock_id,name,COALESCE(buy,0)-COALESCE(sell,0) FROM \"TaiwanStockInstitutionalInvestorsBuySell\" WHERE date::text=%s AND stock_id=ANY(%s)", (str(pd_), stk))
            fnet, tnet = {}, {}
            for sid, nm, net in cur.fetchall():
                sid = str(sid); net = float(net or 0)
                if nm == "Foreign_Investor": fnet[sid] = fnet.get(sid, 0) + net
                elif nm == "Investment_Trust": tnet[sid] = tnet.get(sid, 0) + net
        fr = {s: fnet[s] / vol[s] for s in fnet if vol.get(s, 0) > 0}
        tr = {s: tnet[s] / vol[s] for s in tnet if vol.get(s, 0) > 0}
        zf, zt = _wz(fr), _wz(tr)
        vals = {s: zf[s] * zt[s] for s in set(zf) & set(zt)}
        real += len(vals); total += len(stk)
        med = float(np.median(list(vals.values()))) if vals else 0.0
        rows = [(pd_, s, IMP, round(float(vals.get(s, med)), 6)) for s in stk]
        with db.transaction(conn) as cur:
            execute_values(cur, "INSERT INTO feature_values (panel_date, stock_id, feature, value) VALUES %s "
                           "ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", rows)
        written += len(rows)
    return written, (real / total if total else 0)


def _net(conn, panels, h, feats, model, seeds, top):
    """回 (sharpe, calmar, maxdd, cagr) net,GBDT 多 seed 均。"""
    sh, ca, dd, cg = [], [], [], []
    for sd in seeds:
        r = portfolio.run_backtest(conn, panels, h, feats=feats, model=model, top_frac=top, weight="equal", seed=sd, cost=COST)
        if not r or not r.get("portfolio_net"):
            continue
        m = r["portfolio_net"]
        if m.get("sharpe") is not None: sh.append(m["sharpe"])
        if m.get("calmar") is not None: ca.append(m["calmar"])
        dd.append(m["max_drawdown"]); cg.append(m["cagr"])
    if not sh:
        return None
    return (np.mean(sh), np.mean(ca) if ca else float('nan'), np.mean(dd), np.mean(cg))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=float, default=0.1)
    args = ap.parse_args()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
            panels = [r[0] for r in cur.fetchall()]
        w, cov = _compute_dense(conn, panels)
        print(f"{IMP}:寫 {w:,} 值(真實覆蓋 {cov:.0%}、餘補中位)、{len(panels)} panel")
        base = [x for x in baseline.canonical_features(conn, panels) if x != IMP]
        print(f"base {len(base)} 特徵 vs +{CAND}(imputed 同宇宙)、top{args.top:.0%}/equal、成本 {COST:.3%}\n")
        print(f"  {'model':9s} {'H':>3s} {'set':6s} {'Sharpe':>7s} {'Calmar':>7s} {'MaxDD':>7s} {'CAGR':>7s}")
        for model, seeds in (("B2_ridge", [42]), ("M1_gbdt", [42, 43, 44])):
            for h in (20, 60):
                rb = _net(conn, panels, h, base, model, seeds, args.top)
                ra = _net(conn, panels, h, base + [IMP], model, seeds, args.top)
                bench = portfolio.run_backtest(conn, panels, h, feats=base, model=model, top_frac=args.top, cost=COST)
                bm = bench.get("benchmark_net") if bench else None
                if rb:
                    print(f"  {model:9s} {h:>3d} {'base':6s} {rb[0]:>7.2f} {rb[1]:>7.2f} {rb[2]:>+7.1%} {rb[3]:>+7.1%}")
                if ra:
                    dsh = ra[0] - rb[0] if rb else float('nan')
                    print(f"  {model:9s} {h:>3d} {'+cand':6s} {ra[0]:>7.2f} {ra[1]:>7.2f} {ra[2]:>+7.1%} {ra[3]:>+7.1%}   ΔSharpe={dsh:>+.2f}")
                if bm and bm.get("sharpe") is not None:
                    print(f"  {'  基準':9s} {h:>3d} {'bench':6s} {bm['sharpe']:>7.2f} {(bm['calmar'] if bm['calmar'] else float('nan')):>7.2f} {bm['max_drawdown']:>+7.1%} {bm['cagr']:>+7.1%}")
                print()
        with db.transaction(conn) as cur:
            cur.execute("DELETE FROM feature_values WHERE feature=%s", (IMP,))
            print(f"清候選列:{cur.rowcount} 列刪")
        print("判讀(#14):+候選 net Sharpe/Calmar 有感升 + MaxDD 不惡化 → 提拔;持平/變差 → IC 邊際非真經濟 alpha、維持候選。")


if __name__ == "__main__":
    main()

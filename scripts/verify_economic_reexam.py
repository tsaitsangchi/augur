#!/usr/bin/env python
"""augur 翻案候選經濟價值測(#14) — 公平測翻案者能否提升投組 net Sharpe/Calmar。

🎯 這支在做什麼(白話):公平重檢翻案出 x_gross_margin_pctile(4格全正增量)等;但 IC 增量 ≠ 經濟價值
(foreign_trust_div 殷鑑)。此支對翻案候選做 #14 靈魂終測:復用既有 _compute 填候選 → 補滿同宇宙 →
base(33特徵)vs +候選 之 top10%/equal 投組、扣 0.585% 成本、Ridge+GBDT(3seed)、h20/60 → net Sharpe/Calmar/MaxDD/Δ。
判據(#14):net Sharpe/Calmar 有感升 + MaxDD 不惡化 → 真提拔;持平/變差 → IC 邊際非真經濟 alpha。
守 #8 · #12 · #14 · #15 · #28。用法:PYTHONPATH=src python scripts/verify_economic_reexam.py
"""
import argparse
import importlib.util

import numpy as np
from psycopg2.extras import execute_values

from augur.core import db
from augur.evaluation import baseline, portfolio

ROOT = "/home/hugo/project/augur/scripts/"
COST = 0.00585
TARGETS = ["x_gross_margin_pctile", "x_day_trade_imbalance_20d", "x_inventory_ratio_chg"]
HS = (20, 60)


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, ROOT + fn)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _densify(conn, panels, cand):
    name = cand + "_imp"
    for pd_ in panels:
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (pd_,))
            stk = [str(r[0]) for r in cur.fetchall()]
            if not stk:
                continue
            cur.execute("SELECT stock_id, value FROM feature_values WHERE panel_date=%s AND feature=%s AND stock_id=ANY(%s)", (pd_, cand, stk))
            vals = {str(r[0]): float(r[1]) for r in cur.fetchall()}
        if not vals:
            continue
        med = float(np.median(list(vals.values())))
        rows = [(pd_, s, name, round(float(vals.get(s, med)), 6)) for s in stk]
        with db.transaction(conn) as cur:
            execute_values(cur, "INSERT INTO feature_values (panel_date, stock_id, feature, value) VALUES %s "
                           "ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", rows)


def _net(conn, panels, h, feats, model, seeds, top=0.1):
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
    ap = argparse.ArgumentParser(); ap.add_argument("--top", type=float, default=0.1)
    ap.add_argument("--targets", default=",".join(TARGETS))
    ap.add_argument("--hs", default="20,60")
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()
    targets = args.targets.split(","); hs = [int(x) for x in args.hs.split(",")]
    gbdt_seeds = list(range(42, 42 + args.seeds))
    dt = _load("vdt", "verify_daytrade_candidates.py")
    fu = _load("vfu", "verify_fundamental_candidates.py")
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
            panels = [r[0] for r in cur.fetchall()]
        print("填候選 + 補滿同宇宙…")
        dt._compute(conn, panels); fu._compute(conn, panels)
        for t in targets:
            _densify(conn, panels, t)
        impnames = [t + "_imp" for t in targets]
        allnames = dt.CANDS + fu.CANDS + impnames
        base = [f for f in baseline.canonical_features(conn, panels) if f not in allnames]
        print(f"base {len(base)} 特徵、top{args.top:.0%}/equal、成本 {COST:.3%}、{len(panels)} panel\n")
        print(f"  {'candidate':26s} {'model':9s} {'H':>3s} {'set':6s} {'Sharpe':>7s} {'Calmar':>7s} {'MaxDD':>7s} {'CAGR':>7s}")
        for t in targets:
            name = t + "_imp"
            for model, seeds in (("B2_ridge", [42]), ("M1_gbdt", gbdt_seeds)):
                for h in hs:
                    rb = _net(conn, panels, h, base, model, seeds, args.top)
                    ra = _net(conn, panels, h, base + [name], model, seeds, args.top)
                    if rb:
                        print(f"  {t:26s} {model:9s} {h:>3d} {'base':6s} {rb[0]:>7.2f} {rb[1]:>7.2f} {rb[2]:>+7.1%} {rb[3]:>+7.1%}")
                    if ra and rb:
                        ds = ra[0] - rb[0]; dc = ra[1] - rb[1]
                        mark = "✅" if (ds > 0.05 and ra[2] <= rb[2] + 0.005) else "✗"
                        print(f"  {t:26s} {model:9s} {h:>3d} {'+cand':6s} {ra[0]:>7.2f} {ra[1]:>7.2f} {ra[2]:>+7.1%} {ra[3]:>+7.1%}  ΔSh={ds:+.2f} ΔCal={dc:+.2f} {mark}")
                print()
        with db.transaction(conn) as cur:
            cur.execute("DELETE FROM feature_values WHERE feature = ANY(%s)", (allnames,))
            print(f"清候選列:{cur.rowcount} 列刪")
        print("判讀(#14):ΔSharpe 有感升(>+0.05)+ MaxDD 不惡化 → 提拔;否則 IC 邊際非真經濟 alpha、維持候選。")


if __name__ == "__main__":
    main()

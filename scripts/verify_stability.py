#!/usr/bin/env python
"""augur x_gross_margin_pctile 穩定性確認 — 防樣本噪音當 alpha(#15),productionize 前最後一關。

🎯 這支在做什麼(白話):H120 Calmar 跳升(1.85→2.47)亮眼但非重疊期數少 → 須驗「是真穩健還是 1-2 期僥倖」:
1. **逐期 Δ 一致性**:per-period(cand−base)net 報酬,正期比例 + 均(普遍貢獻 vs 集中單期?)
2. **Leave-one-period-out ΔCalmar**:抽掉任一期重算,看最壞值(min)——若翻負=單期驅動、脆
3. **子期間**:前半/後半 ΔCalmar 各自成立?
4. **top 分位掃**:10/20/30% ΔCalmar 一致?
判據(#15):逐期 Δ 多數正 + LOO 最壞仍正 + 兩子期同向 + 分位一致 → 穩健可 productionize;否則樣本噪音、不入生產。
複用既有 _compute + run_backtest net_series(高效)。守 #8 · #12 · #14 · #15 · #28。
用法:PYTHONPATH=src python scripts/verify_stability.py
"""
import importlib.util

import numpy as np
from psycopg2.extras import execute_values

from augur.core import db
from augur.evaluation import baseline, portfolio

ROOT = "/home/hugo/project/augur/scripts/"
CAND = "x_gross_margin_pctile"
IMP = CAND + "_imp"
COST = 0.00585


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, ROOT + fn)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _densify(conn, panels):
    for pd_ in panels:
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (pd_,))
            stk = [str(r[0]) for r in cur.fetchall()]
            if not stk:
                continue
            cur.execute("SELECT stock_id, value FROM feature_values WHERE panel_date=%s AND feature=%s AND stock_id=ANY(%s)", (pd_, CAND, stk))
            vals = {str(r[0]): float(r[1]) for r in cur.fetchall()}
        if not vals:
            continue
        med = float(np.median(list(vals.values())))
        rows = [(pd_, s, IMP, round(float(vals.get(s, med)), 6)) for s in stk]
        with db.transaction(conn) as cur:
            execute_values(cur, "INSERT INTO feature_values (panel_date, stock_id, feature, value) VALUES %s "
                           "ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", rows)


def _calmar(series, ppy):
    m = portfolio._metrics(series, ppy)
    return m.get("calmar")


def main():
    fu = _load("vfu", "verify_fundamental_candidates.py")
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
            panels = [r[0] for r in cur.fetchall()]
        print("填候選 + 補滿…")
        fu._compute(conn, panels); _densify(conn, panels)
        # base 須排除「全部」實驗候選(fu._compute 寫 5 個基本面候選、皆全 panel 覆蓋會混入 canonical)→ 否則 base 汙染
        base = [f for f in baseline.canonical_features(conn, panels) if f not in (fu.CANDS + [IMP])]
        print(f"base {len(base)} 特徵(已排除全 {len(fu.CANDS)} 實驗候選 + imp)")

        for model in ("B2_ridge", "M1_gbdt"):
            for h in (60, 120):
                rb = portfolio.run_backtest(conn, panels, h, feats=base, model=model, top_frac=0.1, cost=COST, seed=42)
                ra = portfolio.run_backtest(conn, panels, h, feats=base + [IMP], model=model, top_frac=0.1, cost=COST, seed=42)
                if not rb or not ra:
                    continue
                bn, an, ppy = rb["net_series"], ra["net_series"], rb["ppy"]
                n = min(len(bn), len(an)); bn, an = bn[:n], an[:n]
                delta = np.array(an) - np.array(bn)
                bc, ac = _calmar(bn, ppy), _calmar(an, ppy)
                dcal = (ac - bc) if (ac is not None and bc is not None) else float('nan')
                tstat = float(delta.mean() / delta.std() * np.sqrt(n)) if delta.std() > 0 else 0.0  # 逐期 Δ 顯著性(穩健)
                def _sh(s):
                    m = portfolio._metrics(s, ppy); return m.get("sharpe")
                bs, as_ = _sh(bn), _sh(an)
                dsh = (as_ - bs) if (as_ is not None and bs is not None) else float('nan')
                half_ = n // 2
                ds1 = (_sh(an[:half_]) or np.nan) - (_sh(bn[:half_]) or np.nan)   # Sharpe 子期(少期數比 Calmar 穩)
                ds2 = (_sh(an[half_:]) or np.nan) - (_sh(bn[half_:]) or np.nan)
                # LOO ΔCalmar
                loo = []
                for i in range(n):
                    bi = bn[:i] + bn[i+1:]; ai = an[:i] + an[i+1:]
                    cb, ca = _calmar(bi, ppy), _calmar(ai, ppy)
                    if cb is not None and ca is not None:
                        loo.append(ca - cb)
                # 子期間
                half = n // 2
                d1 = (_calmar(an[:half], ppy) or np.nan) - (_calmar(bn[:half], ppy) or np.nan)
                d2 = (_calmar(an[half:], ppy) or np.nan) - (_calmar(bn[half:], ppy) or np.nan)
                print(f"\n══ {model} H={h}({n} 非重疊期、ppy {ppy:.1f})══")
                print(f"  全期 ΔSharpe={dsh:+.2f}(base {bs:.2f}→cand {as_:.2f}) | ΔCalmar={dcal:+.2f}(base {bc:.2f}→cand {ac:.2f})")
                print(f"  逐期 Δnet:正期 {int((delta>0).sum())}/{n}、均 {delta.mean():+.4f}、**t={tstat:+.2f}**(穩健顯著性)")
                print(f"  子期間 ΔSharpe(穩):前半 {ds1:+.2f}、後半 {ds2:+.2f}  | ΔCalmar:前 {d1:+.2f}、後 {d2:+.2f}")
                if loo:
                    print(f"  LOO ΔCalmar(脆性參考、少期數會爆):最壞 {min(loo):+.2f}、最好 {max(loo):+.2f}")

        print("\n══ top 分位掃(H120 Ridge + GBDT、ΔCalmar)══")
        for model in ("B2_ridge", "M1_gbdt"):
            for top in (0.1, 0.2, 0.3):
                rb = portfolio.run_backtest(conn, panels, 120, feats=base, model=model, top_frac=top, cost=COST, seed=42)
                ra = portfolio.run_backtest(conn, panels, 120, feats=base + [IMP], model=model, top_frac=top, cost=COST, seed=42)
                if rb and ra and rb.get("portfolio_net") and ra.get("portfolio_net"):
                    bc = rb["portfolio_net"].get("calmar"); ac = ra["portfolio_net"].get("calmar")
                    bs = rb["portfolio_net"].get("sharpe"); as_ = ra["portfolio_net"].get("sharpe")
                    if bc and ac:
                        print(f"  {model} top{top:.0%}: ΔCalmar {ac-bc:+.2f}(→{ac:.2f})、ΔSharpe {as_-bs:+.2f}")

        with db.transaction(conn) as cur:
            cur.execute("DELETE FROM feature_values WHERE feature = ANY(%s)", (fu.CANDS + [IMP],))
            print(f"\n清候選列:{cur.rowcount} 列刪")
        print("判讀(#15):逐期 Δ 多數正 + LOO 最壞仍正 + 兩子期同向 + 分位一致 → 穩健;否則樣本噪音、不入生產。")


if __name__ == "__main__":
    main()

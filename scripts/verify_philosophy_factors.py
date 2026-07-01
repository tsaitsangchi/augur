#!/usr/bin/env python
"""P7 哲學因子假說 #14 驗證 — principle_factor_map 回填 validated_ic / validated_econ。

🎯 對投資哲學原則→因子映射(引真實文獻策展)跑 as-of rank IC(direction 校正、HAC 顯著性)
   + 經濟價值 #14 回測,回填 validated_ic/econ。顯性化「每投資原則→因子」之真實實證(可解釋性)。
   哲學零加權、經濟價值 #14 為唯一裁決;不在 augur 特徵者(roe/peg/fscore…已試盡淘汰)標 NULL。
守 #1(as-of、真實 feature_values)· #8(label t+h forward)· #14(經濟價值)· #15(誠實回填、飽和不誇大)。

用法:PYTHONPATH=src python scripts/verify_philosophy_factors.py [--since 2021-01-01] [--h 60]
"""
import sys

from augur.core import db
from augur.evaluation import label as label_mod, metrics, portfolio


def main():
    since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv else "2021-01-01"
    h = int(sys.argv[sys.argv.index("--h") + 1]) if "--h" in sys.argv else 60
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT feature, direction FROM principle_factor_map ORDER BY feature")
            fmaps = cur.fetchall()
            cur.execute("SELECT DISTINCT feature FROM feature_values")
            augur_feats = {r[0] for r in cur.fetchall()}
            cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date", (since,))
            panels = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT stock_id FROM core_universe")
            universe = [r[0] for r in cur.fetchall()]
        cal = label_mod.full_calendar(conn)
        print(f"panels {len(panels)}(≥{since})、universe {len(universe)}、H{h};驗 {len(fmaps)} 個 feature-direction\n")
        for feature, direction in fmaps:
            if feature not in augur_feats:
                with db.transaction(conn) as cur:
                    cur.execute("UPDATE principle_factor_map SET validated_ic=NULL, validated_econ=NULL WHERE feature=%s", (feature,))
                print(f"⊘ {feature}: augur 未建/已試盡淘汰 → NULL")
                continue
            ic_by_panel = {}
            for pd in panels:
                with db.transaction(conn) as cur:
                    cur.execute("SELECT stock_id, value FROM feature_values WHERE panel_date=%s AND feature=%s AND stock_id=ANY(%s)",
                                (pd, feature, universe))
                    preds = {s: v * direction for s, v in cur.fetchall()}
                if len(preds) < 5:
                    continue
                labs = label_mod.labels(conn, pd, list(preds), h, calendar=cal)
                ic = metrics.rank_ic(preds, labs)
                if ic is not None:
                    ic_by_panel[pd] = ic
            summ = metrics.summarize(ic_by_panel)
            vic = summ.get("mean_ic")
            hac_t = metrics.effective_t_hac(ic_by_panel) if ic_by_panel else None
            try:
                bt = portfolio.run_backtest(conn, panels, h, feats=[feature], top_frac=0.1, cost=0.00585, asof=True)
                vecon = bt["portfolio_net"].get("sharpe")
            except Exception as e:
                vecon = None
                bt_err = str(e)[:50]
            with db.transaction(conn) as cur:
                cur.execute("UPDATE principle_factor_map SET validated_ic=%s, validated_econ=%s WHERE feature=%s",
                            (vic, vecon, feature))
            icstr = f"{vic:+.4f}" if vic is not None else "None"
            tstr = f"{hac_t:.2f}" if hac_t is not None else "?"
            estr = f"{vecon:+.2f}" if vecon is not None else "None"
            print(f"✓ {feature}(dir {direction:+d}): IC {icstr} (HAC-t {tstr}, {len(ic_by_panel)}p)  econ_sharpe {estr}")


if __name__ == "__main__":
    main()

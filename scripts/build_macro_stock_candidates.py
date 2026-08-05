#!/usr/bin/env python
"""S3-MACRO-STOCK BUILD v1／v2／P2 — 契約候選材料化＋IC。

🎯 這支在做什麼（白話）：把契約內股×宏交互候選寫入 feature_candidate_values，
並印 pan-hist／as-of IC（HAC）。研究臂；禁默認 prodset。軌 M＝M-stop 後本 CLI 僅留痕／重跑須另 GO。

守 #1 缺列 · #8 PIT（macro_vintage）· WM.36（經 features.macro_stock registry）· 禁 Tier-B。

執行指令矩陣:
  python scripts/build_macro_stock_candidates.py
  python scripts/build_macro_stock_candidates.py --selftest
  python scripts/build_macro_stock_candidates.py --run --since 2014-01-01 --h 20,60
  python scripts/build_macro_stock_candidates.py --run --v2 --since 2014-01-01
  python scripts/build_macro_stock_candidates.py --run --p2 --since 2014-01-01
  python scripts/build_macro_stock_candidates.py --run --ic-only --h 20,60
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.audit import feature_diagnostics as fd
from augur.core import db
from augur.features import macro_stock as ms


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--v2", action="store_true")
    ap.add_argument("--p2", action="store_true")
    ap.add_argument("--since", default="2014-01-01")
    ap.add_argument("--h", default="20,60")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--ic-only", action="store_true", help="略過 materialize，只印既有候選 IC")
    args = ap.parse_args(argv)
    if args.selftest:
        return ms._selftest()
    if not args.run:
        print(__doc__)
        return 0
    if args.p2:
        names, tag, fn = list(ms.P2_NAMES), "p2", ms.compute_macro_stock_candidates_p2
    elif args.v2:
        names, tag, fn = list(ms.V2_NAMES), "v2", ms.compute_macro_stock_candidates_v2
    else:
        names, tag, fn = list(ms.NAMES), "v1", ms.compute_macro_stock_candidates

    hs = [int(x) for x in args.h.split(",")]
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute(
                "SELECT DISTINCT panel_date FROM feature_values "
                "WHERE panel_date>=%s ORDER BY panel_date",
                (args.since,),
            )
            panels = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT stock_id FROM core_universe ORDER BY stock_id")
            core = [str(r[0]) for r in cur.fetchall()]
        print(f"macro_stock BUILD-{tag} | {len(panels)} panel", flush=True)
        if not args.ic_only:
            n = fn(conn, panels, core, progress=lambda m: print(m, flush=True))
            print(f"  寫入/更新 {n:,} 值", flush=True)
        with db.transaction(conn) as cur:
            for name in names:
                cur.execute(
                    "SELECT count(*), min(panel_date)::text, max(panel_date)::text "
                    "FROM feature_candidate_values WHERE feature=%s",
                    (name,),
                )
                print(f"  {name}: {cur.fetchone()}", flush=True)
        for label, asof in (("pan-hist", False), ("as-of", True)):
            print(f"\n══ IC {label} ══", flush=True)
            for f in names:
                bits = []
                for h in hs:
                    s = fd.single_factor_ic(conn, panels, h, core, [f], asof=asof).get(f, {})
                    ic = s.get("mean_ic")
                    if ic is None:
                        bits.append(f"H{h}:n/a")
                    else:
                        bits.append(
                            f"H{h}:{ic:+.4f}/{s.get('effective_t_hac'):.2f}/"
                            f"{s.get('hit_rate'):.2f}/{s.get('n_panels')}"
                        )
                print(f"  {f:28s} " + "  ".join(bits), flush=True)
        print("判讀:|HAC|≥2→VERIFY；禁 prodset。", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

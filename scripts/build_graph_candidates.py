#!/usr/bin/env python
"""GRAPH-G3 path=A — 圖聚合候選材料化＋IC（禁 prodset／提拔）。

🎯 這支在做什麼（白話）：S-EQ 讀 stock_graph_edge，聚合成 ≤3 名扁平候選，
寫入 feature_candidate_values。印 as-of IC 供判讀；**不**跑 verify 提拔、
**不**改熱路徑。

執行指令矩陣:
  python scripts/build_graph_candidates.py
  python scripts/build_graph_candidates.py --selftest
  python scripts/build_graph_candidates.py --run --since 2026-06-30 --h 20,60
  python scripts/build_graph_candidates.py --run --ic-only --since 2026-06-30
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.audit import feature_diagnostics as fd
from augur.core import db
from augur.features import graph_candidate as gc


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--since", default="2026-06-30")
    ap.add_argument("--h", default="20,60")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--ic-only", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return 0 if gc._selftest() else 1
    if not args.run:
        print(__doc__)
        return 0

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
        print(f"graph_candidate BUILD | panels={len(panels)} since={args.since}", flush=True)
        if not args.ic_only:
            n, skips = gc.compute_graph_candidates(
                conn, panels, progress=lambda m: print(f"  {m}", flush=True)
            )
            print(f"  寫入/更新 {n:,} 值｜SKIP={len(skips)}", flush=True)
            for s in skips:
                print(f"    · {s}", flush=True)
        with db.transaction(conn) as cur:
            for name in gc.NAMES:
                cur.execute(
                    "SELECT count(*), min(panel_date)::text, max(panel_date)::text "
                    "FROM feature_candidate_values WHERE feature=%s",
                    (name,),
                )
                print(f"  {name}: {cur.fetchone()}", flush=True)
        # IC only on panels that actually have graph candidates (S-EQ survivors)
        with db.transaction(conn) as cur:
            cur.execute(
                "SELECT DISTINCT panel_date FROM feature_candidate_values "
                "WHERE feature = ANY(%s) AND panel_date>=%s ORDER BY panel_date",
                (list(gc.NAMES), args.since),
            )
            ic_panels = [r[0] for r in cur.fetchall()]
        print(f"\n══ IC as-of｜n_panels={len(ic_panels)} ══", flush=True)
        for f in gc.NAMES:
            bits = []
            for h in hs:
                s = fd.single_factor_ic(conn, ic_panels, h, core, [f], asof=True).get(f, {})
                ic = s.get("mean_ic")
                eht = s.get("effective_t_hac")
                hr = s.get("hit_rate")
                np_ = s.get("n_panels")
                if ic is None:
                    bits.append(f"H{h}:n/a")
                elif eht is None:
                    bits.append(
                        f"H{h}:{ic:+.4f}/hac-n/a/"
                        f"{(hr if hr is not None else float('nan')):.2f}/{np_}"
                    )
                else:
                    bits.append(
                        f"H{h}:{ic:+.4f}/{eht:.2f}/"
                        f"{(hr if hr is not None else float('nan')):.2f}/{np_}"
                    )
            print(f"  {f:28s} " + "  ".join(bits), flush=True)
        print(
            "判讀:fwd label 不足→n/a 誠實；|HAC|≥2 且多 panel 才可另 VERIFY-go；"
            "本窗禁 prodset／提拔。熱路徑仍不讀圖。",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

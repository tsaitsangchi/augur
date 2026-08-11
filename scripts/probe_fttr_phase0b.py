#!/usr/bin/env python
"""NF-A-FTTR Phase 0b — RankFTTransformer H60 walk-forward vs RankRidge 冠軍門。

🎯 prodset · 非重疊 panel · portfolio.run_backtest(model=RankFTTransformer)。
   預凍: 3-seed min net Sharpe > 1.3016 且 min hit ≥ 0.6316；否則 STOP promote。
   ≠ ALL_FAMILIES／registry／serve。

執行指令矩陣:
  python scripts/probe_fttr_phase0b.py
  python scripts/probe_fttr_phase0b.py --run --until 2026-07-31 --horizon 60 --seeds 1,2,42
"""
from __future__ import annotations

import argparse
import hashlib
import statistics
import sys

import _bootstrap  # noqa: F401

CHAMPION = {"sharpe": 1.3016, "hit": 0.6316}


def _nonoverlap(panels, h):
    need = h * 1.45 * 0.9
    out = [panels[0]]
    for p in panels[1:]:
        if (p - out[-1]).days >= need:
            out.append(p)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--since", default="2021-01-01")
    ap.add_argument("--until", default="2026-07-31")
    ap.add_argument("--horizon", type=int, default=60)
    ap.add_argument("--seeds", default="1,2,42")
    ap.add_argument("--cost", type=float, default=0.00585)
    args = ap.parse_args(argv)
    if not args.run:
        print(__doc__.split("執行指令矩陣:")[1])
        return 0

    from augur.core import db
    from augur.core.prodset_contract import FEATURE_SOURCE_PRODSET
    from augur.evaluation import baseline, portfolio

    seeds = [int(s) for s in str(args.seeds).split(",") if s.strip()]
    h = int(args.horizon)
    print(
        f"預凍門：min net Sharpe > {CHAMPION['sharpe']} 且 min hit ≥ {CHAMPION['hit']}；"
        f"else STOP promote | until={args.until} H={h} seeds={seeds}",
        flush=True,
    )
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT panel_date FROM feature_values "
                "WHERE panel_date>=%s AND panel_date<=%s ORDER BY panel_date",
                (args.since, args.until),
            )
            panels = [r[0] for r in cur.fetchall()]
        panels = _nonoverlap(panels, h)
        ph = hashlib.sha256(",".join(map(str, panels)).encode()).hexdigest()[:10]
        feats = baseline.resolve_train_feats(conn, panels, source=FEATURE_SOURCE_PRODSET)
        print(
            f"panel_hash={ph} n_panels={len(panels)} n_feats={len(feats)} feats={feats}",
            flush=True,
        )
        print(
            "註：prodset=live active（與 RankRidge＠07-31 artifact feats 同尺／hash 路徑）；"
            "≠ canonical 全表",
            flush=True,
        )

        rows = []
        for seed in seeds:
            print(f"── seed={seed} 開始 ──", flush=True)
            r = portfolio.run_backtest(
                conn,
                panels,
                h,
                feats=feats,
                model="RankFTTransformer",
                top_frac=0.2,
                weight="equal",
                cost=args.cost,
                seed=seed,
            )
            if not r:
                print(f"seed={seed} EMPTY", flush=True)
                continue
            pn = r["portfolio_net"]
            sh, hit = pn.get("sharpe"), pn.get("hit_rate")
            print(
                f"seed={seed} n_folds={r.get('n_periods')} "
                f"netSharpe={sh} hit={hit} cagr={pn.get('cagr')}",
                flush=True,
            )
            rows.append((seed, float(sh), float(hit)))

    if len(rows) < 3:
        print("✗ 可用 seed<3 → STOP promote", flush=True)
        return 1
    sharpes = [x[1] for x in rows]
    hits = [x[2] for x in rows]
    mn_s, md_s, mx_s = min(sharpes), statistics.median(sharpes), max(sharpes)
    mn_h = min(hits)
    print(f"min/med/max Sharpe={mn_s:.4f}/{md_s:.4f}/{mx_s:.4f}", flush=True)
    print(f"min hit={mn_h:.4f}", flush=True)
    promote = (mn_s > CHAMPION["sharpe"]) and (mn_h + 1e-12 >= CHAMPION["hit"])
    if promote:
        print("閘：PASS promote-gate（仍須另句才 registry／serve）", flush=True)
    else:
        print("閘：STOP promote", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

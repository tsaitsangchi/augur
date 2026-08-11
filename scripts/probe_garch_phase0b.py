#!/usr/bin/env python
"""NF-B-GARCH Phase 0b — GarchMeanDir 方向 hit vs naive（預測臂）。

🎯 另書量尺:core 單股、月步 walk-forward、條件均值累積方向 vs naive。
   預凍: mean(GARCH hit) > mean(naive)。⊥ simulate_* 風險尺。
守 #32b· #8· skip-sync· 禁稱可交易。

執行指令矩陣:
  python scripts/probe_garch_phase0b.py
  python scripts/probe_garch_phase0b.py --run --asof 2026-07-31 --horizon 20 --n-stocks 300
"""
from __future__ import annotations

import argparse
import statistics
import sys
import warnings

import _bootstrap  # noqa: F401
import numpy as np

from augur.catalog import world_concept
from augur.models.classical_ts import GarchMeanDir

ADJ_CONCEPT = "tw.daily_bar_adjusted"


def _core_stocks(conn, asof, n):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT stock_id FROM core_universe_asof
               WHERE as_of_date=%s ORDER BY stock_id LIMIT %s""",
            (asof, n),
        )
        return [r[0] for r in cur.fetchall()]


def _series(conn, sid, asof, adj_sql):
    with conn.cursor() as cur:
        cur.execute(
            f"""SELECT date, close FROM {adj_sql}
               WHERE stock_id=%s AND date<=%s AND close>0
               ORDER BY date""",
            (sid, asof),
        )
        rows = cur.fetchall()
    if not rows:
        return None, None
    dates = [r[0] for r in rows]
    closes = np.array([float(r[1]) for r in rows], dtype=float)
    return dates, closes


def _eval_stock(closes, h, min_train=120, step=21, max_folds=36, train_window=504):
    rets = np.diff(np.log(closes))
    g_hits, n_hits = [], []
    idxs = list(range(min_train, len(closes) - h, step))
    if max_folds and len(idxs) > max_folds:
        idxs = idxs[-max_folds:]
    for i in idxs:
        y_full = rets[:i]
        if len(y_full) < 60:
            continue
        y = y_full[-train_window:] if len(y_full) > train_window else y_full
        realized = closes[i + h] / closes[i] - 1.0
        y_up = 1 if realized > 0 else 0
        naive_up = 1 if y[-1] > 0 else 0
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fc = GarchMeanDir().fit(y).predict_horizon(h)
            pred_up = 1 if float(np.sum(fc)) > 0 else 0
        except Exception:
            continue
        g_hits.append(1 if pred_up == y_up else 0)
        n_hits.append(1 if naive_up == y_up else 0)
    return g_hits, n_hits


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-stocks", type=int, default=300)
    ap.add_argument("--horizon", type=int, default=20)
    ap.add_argument("--asof", default="2026-07-31")
    ap.add_argument("--min-train", type=int, default=120)
    ap.add_argument("--step", type=int, default=21)
    ap.add_argument("--max-folds", type=int, default=36)
    args = ap.parse_args(argv)
    if not args.run:
        print(__doc__.split("執行指令矩陣:")[1])
        return 0

    from augur.core import db

    print(
        f"預凍門檻: mean(GARCH hit) > mean(naive hit)；pred-arm-only；"
        f"n_stocks={args.n_stocks} h={args.horizon} asof={args.asof} "
        f"max_folds={args.max_folds} train_window=504",
        flush=True,
    )
    with db.connect() as conn:
        adj_binding = world_concept.resolve(ADJ_CONCEPT, conn=conn)
        adj_sql = world_concept.quote_ident(adj_binding.table)
        print(
            f"registry：{ADJ_CONCEPT} → {adj_binding.table}"
            f"（binding_id={adj_binding.binding_id}）",
            flush=True,
        )
        stocks = _core_stocks(conn, args.asof, args.n_stocks)
        print(f"宇宙={len(stocks)}: {stocks[:8]}{'...' if len(stocks) > 8 else ''}", flush=True)
        per = []
        for sid in stocks:
            dates, closes = _series(conn, sid, args.asof, adj_sql)
            if closes is None or len(closes) < args.min_train + args.horizon + 10:
                print(f"  SKIP {sid}: 序列不足", flush=True)
                continue
            g_h, n_h = _eval_stock(
                closes, args.horizon, args.min_train, args.step, args.max_folds, train_window=504
            )
            if len(g_h) < 5:
                print(f"  SKIP {sid}: 有效折 {len(g_h)}<5", flush=True)
                continue
            gm, nm = float(np.mean(g_h)), float(np.mean(n_h))
            per.append((sid, gm, nm, len(g_h)))
            mark = "✓" if gm > nm else "✗"
            print(
                f"  {sid}: garch_hit={gm:.3f} naive_hit={nm:.3f} folds={len(g_h)} {mark}",
                flush=True,
            )

    if len(per) < 5:
        print(f"✗ 有效股僅 {len(per)}<5——無證據")
        return 1
    a_all = [x[1] for x in per]
    n_all = [x[2] for x in per]
    a_m, n_m = statistics.mean(a_all), statistics.mean(n_all)
    win = sum(1 for a, n in zip(a_all, n_all) if a > n)
    print(
        f"\n彙總 n_stocks={len(per)} | GARCH mean hit={a_m:.4f} "
        f"(min/med/max={min(a_all):.3f}/{statistics.median(a_all):.3f}/{max(a_all):.3f})"
    )
    print(
        f"         naive mean hit={n_m:.4f} "
        f"(min/med/max={min(n_all):.3f}/{statistics.median(n_all):.3f}/{max(n_all):.3f})"
    )
    print(f"         每股贏地板={win}/{len(per)}")
    if a_m > n_m:
        print("判定:✓ 有證據(整體 mean hit > naive)——仍≠可交易、≠ sim 綠、≠ registry")
        return 0
    print("判定:✗ 無證據(未嚴格勝過 naive 地板)——STOP promote")
    return 2


if __name__ == "__main__":
    sys.exit(main())

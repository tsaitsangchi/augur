#!/usr/bin/env python
"""NF-B-COINT Phase 0b — CointPairEG 成對方向 hit vs naive 地板臂。

🎯 另書量尺探針:core 非重疊對、月步 walk-forward、EG 殘差均值回復預測 y 未來 h 日方向,
   對照 naive(近 1 日 y 報酬符號)。預凍: mean(coint hit) > mean(naive hit)。
   ≠可套利／可交易；不寫 registry。
守 #32b· #8(as-of)· skip-sync。

執行指令矩陣:
  python scripts/probe_coint_phase0b.py
  python scripts/probe_coint_phase0b.py --run --asof 2026-07-31 --horizon 20 --n-pairs 100
"""
from __future__ import annotations

import argparse
import statistics
import sys
import warnings

import _bootstrap  # noqa: F401
import numpy as np

from augur.catalog import world_concept
from augur.models.classical_ts import CointPairEG

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


def _align_pair(dates_a, closes_a, dates_b, closes_b):
    ma = {d: c for d, c in zip(dates_a, closes_a)}
    mb = {d: c for d, c in zip(dates_b, closes_b)}
    common = sorted(set(ma) & set(mb))
    if len(common) < 80:
        return None
    ca = np.array([ma[d] for d in common], dtype=float)
    cb = np.array([mb[d] for d in common], dtype=float)
    return np.column_stack([ca, cb])  # close levels; log inside eval


def _eval_pair(close_mat, h, min_train=120, step=21, max_folds=36, train_window=504):
    """close_mat (T,2): col0=y, col1=x. Score direction of y only."""
    closes_y = close_mat[:, 0]
    logp = np.log(close_mat)
    c_hits, n_hits = [], []
    idxs = list(range(min_train, len(close_mat) - h, step))
    if max_folds and len(idxs) > max_folds:
        idxs = idxs[-max_folds:]
    for i in idxs:
        y_full = logp[: i + 1]
        if len(y_full) < 40:
            continue
        y = y_full[-train_window:] if len(y_full) > train_window else y_full
        realized = closes_y[i + h] / closes_y[i] - 1.0
        y_up = 1 if realized > 0 else 0
        naive_up = 1 if closes_y[i] / closes_y[i - 1] - 1.0 > 0 else 0
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fc = CointPairEG().fit(y).predict_horizon(h)  # (h,2) log
            pred_up = 1 if float(fc[-1, 0]) > float(logp[i, 0]) else 0
        except Exception:
            continue
        c_hits.append(1 if pred_up == y_up else 0)
        n_hits.append(1 if naive_up == y_up else 0)
    return c_hits, n_hits


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--asof", default="2026-07-31")
    ap.add_argument("--horizon", type=int, default=20)
    ap.add_argument("--n-pairs", type=int, default=100)
    ap.add_argument("--min-train", type=int, default=120)
    ap.add_argument("--step", type=int, default=21)
    ap.add_argument("--max-folds", type=int, default=36)
    args = ap.parse_args(argv)
    if not args.run:
        print(__doc__.split("執行指令矩陣:")[1])
        return 0

    from augur.core import db

    need = args.n_pairs * 2
    print(
        f"預凍門檻: mean(coint hit) > mean(naive hit)；"
        f"asof={args.asof} h={args.horizon} n_pairs={args.n_pairs} "
        f"max_folds={args.max_folds} train_window=504 EG rho=0.9",
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
        stocks = _core_stocks(conn, args.asof, need + 20)
        print(f"core_fetch={len(stocks)} need≈{need}", flush=True)
        pairs = []
        i = 0
        while len(pairs) < args.n_pairs and i + 2 <= len(stocks):
            pairs.append((stocks[i], stocks[i + 1]))
            i += 2
        print(f"pairs={len(pairs)} (non-overlap k=2)", flush=True)

        per = []
        for p_idx, (sy, sx) in enumerate(pairs):
            dy, cy = _series(conn, sy, args.asof, adj_sql)
            dx, cx = _series(conn, sx, args.asof, adj_sql)
            if cy is None or cx is None:
                print(f"  SKIP pair#{p_idx} ({sy},{sx}): 缺序列", flush=True)
                continue
            if len(cy) < args.min_train + args.horizon + 10 or len(cx) < args.min_train + args.horizon + 10:
                print(f"  SKIP pair#{p_idx} ({sy},{sx}): 序列短", flush=True)
                continue
            mat = _align_pair(dy, cy, dx, cx)
            if mat is None or mat.shape[0] < args.min_train + args.horizon + 10:
                print(f"  SKIP pair#{p_idx} ({sy},{sx}): 對齊短", flush=True)
                continue
            ch, nh = _eval_pair(
                mat, args.horizon, args.min_train, args.step, args.max_folds, train_window=504
            )
            if len(ch) < 5:
                print(f"  SKIP pair#{p_idx} ({sy},{sx}): 有效折 {len(ch)}<5", flush=True)
                continue
            cm, nm = float(np.mean(ch)), float(np.mean(nh))
            per.append((sy, sx, cm, nm, len(ch), p_idx))
            mark = "✓" if cm > nm else "✗"
            print(
                f"  [{p_idx}] {sy}/{sx}: coint_hit={cm:.3f} naive_hit={nm:.3f} "
                f"folds={len(ch)} {mark}",
                flush=True,
            )

    if len(per) < 10:
        print(f"✗ 有效對僅 {len(per)}<10——無證據")
        return 1
    a_all = [x[2] for x in per]
    n_all = [x[3] for x in per]
    a_m, n_m = statistics.mean(a_all), statistics.mean(n_all)
    win = sum(1 for a, n in zip(a_all, n_all) if a > n)
    print(
        f"\n彙總 n_pairs={len(per)} | coint mean hit={a_m:.4f} "
        f"(min/med/max={min(a_all):.3f}/{statistics.median(a_all):.3f}/{max(a_all):.3f})"
    )
    print(
        f"         naive mean hit={n_m:.4f} "
        f"(min/med/max={min(n_all):.3f}/{statistics.median(n_all):.3f}/{max(n_all):.3f})"
    )
    print(f"         每對贏地板={win}/{len(per)}")
    if a_m > n_m:
        print("判定:✓ 有證據(整體 mean hit > naive)——仍≠可交易／可套利、≠ registry")
        return 0
    print("判定:✗ 無證據(未嚴格勝過 naive 地板)——STOP promote")
    return 2


if __name__ == "__main__":
    sys.exit(main())

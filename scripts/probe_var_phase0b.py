#!/usr/bin/env python
"""NF-B-VAR Phase 0b — VarSmall 小系方向 hit vs naive 地板臂。

🎯 另書量尺探針(非產品碼):core 非重疊 k 股系、月步 walk-forward、預測未來 h 日累積報酬方向,
   對照 naive(近 1 日報酬符號)。預凍: mean(VAR hit) > mean(naive hit)。
守 #32b· #8(as-of)· skip-sync· 禁稱可交易· 不寫 registry。

執行指令矩陣:
  python scripts/probe_var_phase0b.py
  python scripts/probe_var_phase0b.py --run --asof 2026-07-31 --horizon 20 --k 3 --n-systems 60
"""
from __future__ import annotations

import argparse
import statistics
import sys
import warnings

import _bootstrap  # noqa: F401
import numpy as np

from augur.catalog import world_concept
from augur.models.classical_ts import VarSmall

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


def _align_panel(series_list):
    """series_list: list of (dates, closes) → aligned log-returns (T-1, k) + close matrix for realized."""
    maps = []
    for dates, closes in series_list:
        maps.append({d: c for d, c in zip(dates, closes)})
    common = sorted(set.intersection(*[set(m) for m in maps]))
    if len(common) < 80:
        return None, None
    close_mat = np.column_stack([[m[d] for d in common] for m in maps])
    rets = np.diff(np.log(close_mat), axis=0)  # (T-1, k)
    # rets[i] = return from common[i] → common[i+1]; at index i in rets, "asof close" = close_mat[i+1]?
    # Match ARIMA probe: at fold i in closes-space, y=rets[:i], realized from closes[i] to closes[i+h]
    # Here closes_aligned = close_mat; fold index on close_mat rows
    return close_mat, rets


def _eval_system(close_mat, h, min_train=120, step=21, max_folds=36, train_window=504, p=1):
    """Per-stock hit lists for one k-system."""
    t, k = close_mat.shape
    rets = np.diff(np.log(close_mat), axis=0)
    # fold index i on close rows: need i>=min_train, i+h < t; train on rets[:i] (len i)
    idxs = list(range(min_train, t - h, step))
    if max_folds and len(idxs) > max_folds:
        idxs = idxs[-max_folds:]
    hits_v = [[] for _ in range(k)]
    hits_n = [[] for _ in range(k)]
    for i in idxs:
        y_full = rets[:i]  # shape (i, k)
        if len(y_full) < 40:
            continue
        y = y_full[-train_window:] if len(y_full) > train_window else y_full
        realized = close_mat[i + h] / close_mat[i] - 1.0  # (k,)
        naive_up = (y[-1] > 0).astype(int)  # (k,)
        y_up = (realized > 0).astype(int)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fc = VarSmall(p=p).fit(y).predict_horizon(h)  # (h, k)
            pred_up = (np.sum(fc, axis=0) > 0).astype(int)
        except Exception:
            continue
        for j in range(k):
            hits_v[j].append(1 if pred_up[j] == y_up[j] else 0)
            hits_n[j].append(1 if naive_up[j] == y_up[j] else 0)
    return hits_v, hits_n


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--asof", default="2026-07-31")
    ap.add_argument("--horizon", type=int, default=20)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--n-systems", type=int, default=60)
    ap.add_argument("--p", type=int, default=1)
    ap.add_argument("--min-train", type=int, default=120)
    ap.add_argument("--step", type=int, default=21)
    ap.add_argument("--max-folds", type=int, default=36)
    args = ap.parse_args(argv)
    if not args.run:
        print(__doc__.split("執行指令矩陣:")[1])
        return 0
    if args.k < 2 or args.k > 5:
        print("✗ k 須 ∈[2,5]")
        return 1

    from augur.core import db

    need = args.k * args.n_systems
    print(
        f"預凍門檻: mean(VAR hit) > mean(naive hit)；"
        f"asof={args.asof} h={args.horizon} k={args.k} n_systems={args.n_systems} "
        f"p={args.p} max_folds={args.max_folds} train_window=504",
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
        stocks = _core_stocks(conn, args.asof, need + 20)  # slack for SKIP
        print(f"core_fetch={len(stocks)} need≈{need}", flush=True)

        systems = []
        i = 0
        while len(systems) < args.n_systems and i + args.k <= len(stocks):
            systems.append(stocks[i : i + args.k])
            i += args.k
        print(f"systems={len(systems)} (non-overlap k={args.k})", flush=True)

        per_stock = []  # (sid, var_mean, naive_mean, n_folds, system_id)
        for s_idx, group in enumerate(systems):
            loaded = []
            ok = True
            for sid in group:
                dates, closes = _series(conn, sid, args.asof, adj_sql)
                if closes is None or len(closes) < args.min_train + args.horizon + 10:
                    print(f"  SKIP system#{s_idx} {group}: {sid} 序列不足", flush=True)
                    ok = False
                    break
                loaded.append((dates, closes))
            if not ok:
                continue
            close_mat, _ = _align_panel(loaded)
            if close_mat is None or close_mat.shape[0] < args.min_train + args.horizon + 10:
                print(f"  SKIP system#{s_idx} {group}: 對齊後過短", flush=True)
                continue
            hv, hn = _eval_system(
                close_mat,
                args.horizon,
                args.min_train,
                args.step,
                args.max_folds,
                train_window=504,
                p=args.p,
            )
            # require enough folds per stock
            if any(len(x) < 5 for x in hv):
                print(f"  SKIP system#{s_idx} {group}: 有效折不足", flush=True)
                continue
            for j, sid in enumerate(group):
                vm, nm = float(np.mean(hv[j])), float(np.mean(hn[j]))
                per_stock.append((sid, vm, nm, len(hv[j]), s_idx))
                mark = "✓" if vm > nm else "✗"
                print(
                    f"  [{s_idx}] {sid}: var_hit={vm:.3f} naive_hit={nm:.3f} "
                    f"folds={len(hv[j])} {mark}",
                    flush=True,
                )

    if len(per_stock) < 10:
        print(f"✗ 有效股槽僅 {len(per_stock)}<10——無證據")
        return 1
    a_all = [x[1] for x in per_stock]
    n_all = [x[2] for x in per_stock]
    a_m, n_m = statistics.mean(a_all), statistics.mean(n_all)
    win = sum(1 for a, n in zip(a_all, n_all) if a > n)
    n_sys_ok = len({x[4] for x in per_stock})
    print(
        f"\n彙總 n_stocks={len(per_stock)} n_systems_ok={n_sys_ok} | "
        f"VAR mean hit={a_m:.4f} "
        f"(min/med/max={min(a_all):.3f}/{statistics.median(a_all):.3f}/{max(a_all):.3f})"
    )
    print(
        f"         naive mean hit={n_m:.4f} "
        f"(min/med/max={min(n_all):.3f}/{statistics.median(n_all):.3f}/{max(n_all):.3f})"
    )
    print(f"         每股贏地板={win}/{len(per_stock)}")
    if a_m > n_m:
        print("判定:✓ 有證據(整體 mean hit > naive)——仍≠可交易、≠自動 P1／registry")
        return 0
    print("判定:✗ 無證據(未嚴格勝過 naive 地板)——STOP promote")
    return 2


if __name__ == "__main__":
    sys.exit(main())

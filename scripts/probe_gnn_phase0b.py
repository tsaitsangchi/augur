#!/usr/bin/env python
"""NF-E-GNN Phase 0b — GcnSmall 截面轉移探針 vs naive。

🎯 train＠graph/feat/label(asof_train,H) → rebind test 圖 → predict＠asof_test。
   預凍: mean(GNN 方向 hit) > mean(naive)（test 宇宙）。
   S-EQ 圖；prodset 節點特徵；≠可交易／≠ registry／≠ B3。
守 #8· #32b· skip-sync。

執行指令矩陣:
  python scripts/probe_gnn_phase0b.py
  python scripts/probe_gnn_phase0b.py --run --asof-train 2026-06-30 --asof-test 2026-07-31 --horizon 4
"""
from __future__ import annotations

import argparse
import datetime as dt
import statistics
import sys

import _bootstrap  # noqa: F401
import numpy as np

from augur.catalog import world_concept
from augur.core.prodset_contract import resolve_prodset_feats
from augur.features.graph_consume import load_edges
from augur.models.gnn_small import GcnSmall

ADJ_CONCEPT = "tw.daily_bar_adjusted"
FEATS_DEFAULT = None  # resolve at runtime


def _core(conn, asof):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT stock_id FROM core_universe_asof
               WHERE as_of_date=%s ORDER BY stock_id""",
            (asof,),
        )
        return [r[0] for r in cur.fetchall()]


def _feat_matrix(conn, asof, stock_ids, feat_names):
    """Return X (N,F) aligned to stock_ids; missing row → nan mask."""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT stock_id, feature, value FROM feature_values
               WHERE panel_date=%s AND feature = ANY(%s)
                 AND stock_id = ANY(%s)""",
            (asof, list(feat_names), list(stock_ids)),
        )
        rows = cur.fetchall()
    idx = {s: i for i, s in enumerate(stock_ids)}
    fidx = {f: j for j, f in enumerate(feat_names)}
    x = np.full((len(stock_ids), len(feat_names)), np.nan, dtype=float)
    for sid, feat, val in rows:
        if sid in idx and feat in fidx and val is not None:
            x[idx[sid], fidx[feat]] = float(val)
    return x


def _fwd_dir(conn, adj_sql, stock_ids, asof, h):
    """Per stock: 1 if close[t+h]/close[t]-1 > 0 else 0; None if missing."""
    out = {}
    with conn.cursor() as cur:
        for sid in stock_ids:
            cur.execute(
                f"""SELECT date, close FROM {adj_sql}
                   WHERE stock_id=%s AND date>=%s AND close>0
                   ORDER BY date LIMIT %s""",
                (sid, asof, h + 5),
            )
            rows = cur.fetchall()
            # find asof row then +h trading days
            dates = [r[0] for r in rows]
            closes = [float(r[1]) for r in rows]
            if not dates or str(dates[0]) > str(asof) and dates[0] != asof:
                # may start after asof if asof not trading — require exact或 first >=
                pass
            # reload: last date <= asof + forward chain
            cur.execute(
                f"""SELECT date, close FROM {adj_sql}
                   WHERE stock_id=%s AND date<=%s AND close>0
                   ORDER BY date DESC LIMIT 1""",
                (sid, asof),
            )
            base = cur.fetchone()
            if not base:
                out[sid] = None
                continue
            d0, c0 = base[0], float(base[1])
            cur.execute(
                f"""SELECT close FROM {adj_sql}
                   WHERE stock_id=%s AND date>%s AND close>0
                   ORDER BY date ASC LIMIT %s""",
                (sid, d0, h),
            )
            fwd = cur.fetchall()
            if len(fwd) < h:
                out[sid] = None
                continue
            c1 = float(fwd[h - 1][0])
            out[sid] = 1 if (c1 / c0 - 1.0) > 0 else 0
    return out


def _naive_dir(conn, adj_sql, stock_ids, asof):
    out = {}
    with conn.cursor() as cur:
        for sid in stock_ids:
            cur.execute(
                f"""SELECT close FROM {adj_sql}
                   WHERE stock_id=%s AND date<=%s AND close>0
                   ORDER BY date DESC LIMIT 2""",
                (sid, asof),
            )
            rows = cur.fetchall()
            if len(rows) < 2:
                out[sid] = None
                continue
            c0, c1 = float(rows[0][0]), float(rows[1][0])  # DESC: [asof, prev]
            out[sid] = 1 if (c0 / c1 - 1.0) > 0 else 0
    return out


def _edges_index(bundle, stock_ids):
    """Map stock_graph edges to (E,2) over stock_ids order; drop OOV."""
    idx = {s: i for i, s in enumerate(stock_ids)}
    pairs = []
    for row in bundle.edges:
        # dataclass fields - check graph_consume Edge bundle
        u = getattr(row, "source_stock_id", None) or row[0]
        v = getattr(row, "target_stock_id", None) or row[1]
        if u in idx and v in idx:
            pairs.append((idx[u], idx[v]))
    if not pairs:
        return None
    return np.array(pairs, dtype=int)


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--asof-train", default="2026-06-30")
    ap.add_argument("--asof-test", default="2026-07-31")
    ap.add_argument("--horizon", type=int, default=4)
    ap.add_argument("--n-steps", type=int, default=40)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)
    if not args.run:
        print(__doc__.split("執行指令矩陣:")[1])
        return 0

    from augur.core import db

    print(
        f"預凍門檻: mean(GNN hit)>mean(naive) @ test；"
        f"train={args.asof_train} test={args.asof_test} H={args.horizon} "
        f"n_steps={args.n_steps} seed={args.seed}",
        flush=True,
    )
    with db.connect() as conn:
        adj_binding = world_concept.resolve(ADJ_CONCEPT, conn=conn)
        adj_sql = world_concept.quote_ident(adj_binding.table)
        feats = resolve_prodset_feats(conn, [dt.date.fromisoformat(args.asof_test)])
        print(f"prodset={feats}", flush=True)

        core_tr = set(_core(conn, args.asof_train))
        core_te = set(_core(conn, args.asof_test))
        # stable union order for separate graphs — train/test each on own core list
        stocks_tr = sorted(core_tr)
        stocks_te = sorted(core_te)

        b_tr = load_edges(conn, args.asof_train)
        b_te = load_edges(conn, args.asof_test)
        print(f"graph_train n={b_tr.n} asof={b_tr.graph_asof}", flush=True)
        print(f"graph_test  n={b_te.n} asof={b_te.graph_asof}", flush=True)

        x_tr = _feat_matrix(conn, args.asof_train, stocks_tr, feats)
        x_te = _feat_matrix(conn, args.asof_test, stocks_te, feats)
        # keep rows with finite features
        m_tr = np.all(np.isfinite(x_tr), axis=1)
        m_te = np.all(np.isfinite(x_te), axis=1)
        stocks_tr = [s for s, k in zip(stocks_tr, m_tr) if k]
        stocks_te = [s for s, k in zip(stocks_te, m_te) if k]
        x_tr = x_tr[m_tr]
        x_te = x_te[m_te]
        print(f"nodes_train={len(stocks_tr)} nodes_test={len(stocks_te)}", flush=True)

        e_tr = _edges_index(b_tr, stocks_tr)
        e_te = _edges_index(b_te, stocks_te)
        if e_tr is None or e_te is None:
            print("✗ 過濾後無邊")
            return 1
        print(f"edges_train={len(e_tr)} edges_test={len(e_te)}", flush=True)

        y_tr_map = _fwd_dir(conn, adj_sql, stocks_tr, args.asof_train, args.horizon)
        y_te_map = _fwd_dir(conn, adj_sql, stocks_te, args.asof_test, args.horizon)
        naive_te = _naive_dir(conn, adj_sql, stocks_te, args.asof_test)

        # drop train nodes without label
        keep_tr = [i for i, s in enumerate(stocks_tr) if y_tr_map.get(s) is not None]
        if len(keep_tr) < 20:
            print(f"✗ train labeled <20 ({len(keep_tr)})")
            return 1
        # remap train subgraph
        inv = {old: new for new, old in enumerate(keep_tr)}
        stocks_tr_f = [stocks_tr[i] for i in keep_tr]
        x_tr_f = x_tr[keep_tr]
        y_tr = np.array([float(y_tr_map[s]) for s in stocks_tr_f], dtype=float)
        # map labels to -1/+1 for MSE
        y_signed = np.where(y_tr > 0.5, 1.0, -1.0)
        e_tr_f = []
        for u, v in e_tr:
            if u in inv and v in inv:
                e_tr_f.append((inv[u], inv[v]))
        e_tr_f = np.array(e_tr_f, dtype=int)
        if len(e_tr_f) < 10:
            print("✗ train 邊過少")
            return 1

        model = GcnSmall(in_dim=x_tr_f.shape[1], hidden=8, out_dim=1, seed=args.seed)
        model.fit(x_tr_f, e_tr_f, y=y_signed, n_steps=args.n_steps, lr=0.05)
        print(f"trained steps={args.n_steps} on N={len(stocks_tr_f)}", flush=True)

        # test: rebind + predict
        e_te_f = e_te  # already on stocks_te index
        model.rebind(e_te_f)
        scores = model.predict_scores(x_te)
        gnn_hits, naive_hits = [], []
        detail = []
        for i, sid in enumerate(stocks_te):
            yt = y_te_map.get(sid)
            nt = naive_te.get(sid)
            if yt is None or nt is None:
                continue
            pred_up = 1 if scores[i] > 0 else 0
            gnn_hits.append(1 if pred_up == yt else 0)
            naive_hits.append(1 if nt == yt else 0)
            detail.append((sid, scores[i], pred_up, yt, nt))

        print(f"eval_n={len(detail)}", flush=True)
        for sid, sc, pu, yt, nt in detail[:12]:
            mark = "✓" if (1 if sc > 0 else 0) == yt else "✗"
            print(f"  {sid}: score={sc:.4f} pred={pu} y={yt} naive={nt} {mark}", flush=True)
        if len(detail) > 12:
            print(f"  ... +{len(detail)-12} more", flush=True)

    if len(gnn_hits) < 20:
        print(f"✗ 有效評測股 {len(gnn_hits)}<20")
        return 1
    g_m = statistics.mean(gnn_hits)
    n_m = statistics.mean(naive_hits)
    win = sum(1 for a, b in zip(gnn_hits, naive_hits) if a > b)
    # per-stock equal: hit is 0/1 so "win floor" = count gnn hit and naive wrong? use hit rates
    print(
        f"\n彙總 n={len(gnn_hits)} | GNN mean hit={g_m:.4f} | naive mean hit={n_m:.4f}"
    )
    print(f"         GNN 正確數={sum(gnn_hits)}/{len(gnn_hits)} naive 正確數={sum(naive_hits)}/{len(naive_hits)}")
    if g_m > n_m:
        print("判定:✓ 有證據(GNN mean hit > naive)——仍≠可交易、≠ registry／serve")
        return 0
    print("判定:✗ 無證據(未嚴格勝過 naive)——STOP promote")
    return 2


if __name__ == "__main__":
    sys.exit(main())

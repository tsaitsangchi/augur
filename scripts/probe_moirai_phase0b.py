#!/usr/bin/env python
"""NF-D-MOIRAI Phase 0b — MoiraiRank2Small 方向 hit vs naive（排序臂／預訓練）。

🎯 另書量尺:core 單股、月步 walk-forward、log(q50終/末價) 符號＝方向 vs naive。
   預凍: mean(Moirai hit) > mean(naive)。offline-local；≠升格。
守 #32b· #8· skip-sync· 禁稱可交易。

執行指令矩陣:
  python scripts/probe_moirai_phase0b.py
  HF_HUB_OFFLINE=1 python scripts/probe_moirai_phase0b.py --run --asof 2026-07-31 --horizon 20 --n-stocks 300
"""
from __future__ import annotations

import argparse
import os
import statistics
import sys
import warnings

import _bootstrap  # noqa: F401
import numpy as np

from augur.catalog import world_concept
from augur.models.moirai_rank import MoiraiRank2Small

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


def _eval_stock(model, closes, h, min_train=120, step=21, max_folds=24, ctx_max=512):
    m_hits, n_hits = [], []
    idxs = list(range(min_train, len(closes) - h, step))
    if max_folds and len(idxs) > max_folds:
        idxs = idxs[-max_folds:]
    for i in idxs:
        ctx = closes[max(0, i - ctx_max) : i]
        if len(ctx) < 32:
            continue
        realized = closes[i + h] / closes[i] - 1.0
        y_up = 1 if realized > 0 else 0
        naive_up = 1 if closes[i] > closes[i - 1] else 0
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                score = float(model.predict_scores([ctx], horizon=h)[0])
            if not np.isfinite(score):
                continue
            pred_up = 1 if score > 0 else 0
        except Exception:
            continue
        m_hits.append(1 if pred_up == y_up else 0)
        n_hits.append(1 if naive_up == y_up else 0)
    return m_hits, n_hits


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-stocks", type=int, default=300)
    ap.add_argument("--horizon", type=int, default=20)
    ap.add_argument("--asof", default="2026-07-31")
    ap.add_argument("--min-train", type=int, default=120)
    ap.add_argument("--step", type=int, default=21)
    ap.add_argument("--max-folds", type=int, default=24)
    args = ap.parse_args(argv)
    if not args.run:
        print(__doc__.split("執行指令矩陣:")[1])
        return 0

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

    from augur.core import db

    print(
        f"預凍門檻: mean(Moirai hit) > mean(naive hit)；offline-local；no-promote；"
        f"n_stocks={args.n_stocks} h={args.horizon} asof={args.asof} "
        f"max_folds={args.max_folds}",
        flush=True,
    )
    model = MoiraiRank2Small(
        horizon=args.horizon, local_files_only=True, batch_size=8
    ).fit()
    # 預熱載入（失敗＝整輪 SKIP）
    try:
        _ = model.predict_scores([np.linspace(100, 101, 64)], horizon=args.horizon)
        print("模型預熱：OK", flush=True)
    except Exception as e:
        print(f"✗ 模型預熱失敗（誠實 STOP）: {e}", flush=True)
        return 2

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
        for j, sid in enumerate(stocks):
            dates, closes = _series(conn, sid, args.asof, adj_sql)
            if closes is None or len(closes) < args.min_train + args.horizon + 10:
                print(f"  SKIP {sid}: 序列不足", flush=True)
                continue
            m_h, n_h = _eval_stock(
                model, closes, args.horizon, args.min_train, args.step, args.max_folds
            )
            if len(m_h) < 3:
                print(f"  SKIP {sid}: 有效折 <3", flush=True)
                continue
            mh, nh = statistics.mean(m_h), statistics.mean(n_h)
            per.append((sid, mh, nh, len(m_h)))
            if (j + 1) % 10 == 0 or j == 0:
                print(
                    f"  [{j+1}/{len(stocks)}] {sid} moirai={mh:.3f} naive={nh:.3f} folds={len(m_h)}",
                    flush=True,
                )

    if not per:
        print("✗ 無有效股票（誠實 STOP）", flush=True)
        return 1
    m_mean = statistics.mean(p[1] for p in per)
    n_mean = statistics.mean(p[2] for p in per)
    win = sum(1 for p in per if p[1] > p[2])
    print("\n═══ 彙總 ═══", flush=True)
    print(f"n_stocks_ok={len(per)}", flush=True)
    print(
        f"Moirai mean hit={m_mean:.4f} "
        f"(min/med/max="
        f"{min(p[1] for p in per):.3f}/"
        f"{statistics.median(p[1] for p in per):.3f}/"
        f"{max(p[1] for p in per):.3f})",
        flush=True,
    )
    print(
        f"naive mean hit={n_mean:.4f} "
        f"(min/med/max="
        f"{min(p[2] for p in per):.3f}/"
        f"{statistics.median(p[2] for p in per):.3f}/"
        f"{max(p[2] for p in per):.3f})",
        flush=True,
    )
    print(f"每股贏地板={win}/{len(per)}", flush=True)
    if m_mean > n_mean:
        print("閘：有證據（mean Moirai > naive）→ 仍 STOP promote（預凍）", flush=True)
        return 0
    print("閘：無證據（mean Moirai ≤ naive）→ STOP", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

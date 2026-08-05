#!/usr/bin/env python
"""S4-Wave-B-ADAPTER Phase 0b — ARIMA 小宇宙方向 hit vs naive 地板臂。

🎯 另書量尺探針(非產品碼):對 N 檔核心股、expanding 月頻 as-of、預測未來 h 交易日累積報酬方向,
   對照 naive(最近 1 日報酬符號)。預凍門檻:ARIMA 平均 hit 嚴格 > naive 平均 hit 才「有證據」。
守 #32b(地板臂)· #8(as-of)· skip-sync· 禁稱可交易。

執行指令矩陣:
  python scripts/probe_classical_ts_phase0b.py                     # 印矩陣
  python scripts/probe_classical_ts_phase0b.py --run               # 預設 15 股 × H20
  python scripts/probe_classical_ts_phase0b.py --run --n-stocks 12 --horizon 20 --asof 2026-05-31
"""
import argparse
import statistics
import sys
import warnings

import _bootstrap  # noqa: F401
import numpy as np

from augur.models.classical_ts import ArimaUnivariate


def _core_stocks(conn, asof, n):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT stock_id FROM core_universe_asof
               WHERE as_of_date=%s ORDER BY stock_id LIMIT %s""",
            (asof, n),
        )
        rows = cur.fetchall()
    return [r[0] for r in rows]


def _series(conn, sid, asof):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT date, close FROM "TaiwanStockPriceAdj"
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


def _eval_stock(dates, closes, h, min_train=120, step=21, max_folds=36, train_window=504):
    """月步 walk-forward:於 i 用近端 train_window 日報酬 fit,預測未來 h 日累積方向。

    取序列尾端最多 max_folds 折。滾動窗(非全史 expanding)＝探針可完成＋近端紀律。
    """
    rets = np.diff(np.log(closes))
    arima_hits, naive_hits = [], []
    idxs = list(range(min_train, len(closes) - h, step))
    if max_folds and len(idxs) > max_folds:
        idxs = idxs[-max_folds:]
    for i in idxs:
        # rets 對齊: rets[j] = close[j]→close[j+1]; 訓練截止 closes[i] → y=rets[:i]
        y_full = rets[:i]
        if len(y_full) < 40:
            continue
        y = y_full[-train_window:] if len(y_full) > train_window else y_full
        realized = closes[i + h] / closes[i] - 1.0
        y_up = 1 if realized > 0 else 0
        naive_up = 1 if y[-1] > 0 else 0
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fc = ArimaUnivariate(order=(1, 0, 1)).fit(y).predict_horizon(h)
            pred_up = 1 if float(np.sum(fc)) > 0 else 0
        except Exception:
            continue
        arima_hits.append(1 if pred_up == y_up else 0)
        naive_hits.append(1 if naive_up == y_up else 0)
    return arima_hits, naive_hits


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-stocks", type=int, default=15)
    ap.add_argument("--horizon", type=int, default=20)
    ap.add_argument("--asof", default="2026-05-31")
    ap.add_argument("--min-train", type=int, default=120)
    ap.add_argument("--step", type=int, default=21)
    ap.add_argument("--max-folds", type=int, default=36,
                    help="每股最多取近端折數(預設 36≈3y 月步)")
    args = ap.parse_args(argv)
    if not args.run:
        print(__doc__.split("執行指令矩陣:")[1])
        return 0

    from augur.core import db
    # 預凍門檻(跑前寫定,#32b)
    print(f"預凍門檻: mean(ARIMA hit) > mean(naive hit) 於每股平均後再比整體；"
          f"n_stocks={args.n_stocks} h={args.horizon} asof={args.asof} "
          f"max_folds={args.max_folds} train_window=504",
          flush=True)
    with db.connect() as conn:
        stocks = _core_stocks(conn, args.asof, args.n_stocks)
        if len(stocks) < 5:
            # fallback: distinct from PriceAdj
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT DISTINCT stock_id FROM "TaiwanStockPriceAdj"
                       WHERE date<=%s ORDER BY 1 LIMIT %s""",
                    (args.asof, args.n_stocks),
                )
                stocks = [r[0] for r in cur.fetchall()]
        print(f"宇宙={len(stocks)}: {stocks[:8]}{'...' if len(stocks)>8 else ''}",
              flush=True)
        per = []
        for sid in stocks:
            dates, closes = _series(conn, sid, args.asof)
            if closes is None or len(closes) < args.min_train + args.horizon + 10:
                print(f"  SKIP {sid}: 序列不足", flush=True)
                continue
            a_h, n_h = _eval_stock(
                dates, closes, args.horizon, args.min_train, args.step,
                args.max_folds, train_window=504,
            )
            if len(a_h) < 5:
                print(f"  SKIP {sid}: 有效折 {len(a_h)}<5", flush=True)
                continue
            a_mean, n_mean = float(np.mean(a_h)), float(np.mean(n_h))
            per.append((sid, a_mean, n_mean, len(a_h)))
            print(f"  {sid}: arima_hit={a_mean:.3f} naive_hit={n_mean:.3f} folds={len(a_h)} "
                  f"{'✓' if a_mean > n_mean else '✗'}", flush=True)

    if len(per) < 5:
        print(f"✗ 有效股僅 {len(per)}<5——無證據")
        return 1
    a_all = [x[1] for x in per]
    n_all = [x[2] for x in per]
    a_m, n_m = statistics.mean(a_all), statistics.mean(n_all)
    win = sum(1 for a, n in zip(a_all, n_all) if a > n)
    print(f"\n彙總 n_stocks={len(per)} | ARIMA mean hit={a_m:.4f} "
          f"(min/med/max={min(a_all):.3f}/{statistics.median(a_all):.3f}/{max(a_all):.3f})")
    print(f"         naive mean hit={n_m:.4f} "
          f"(min/med/max={min(n_all):.3f}/{statistics.median(n_all):.3f}/{max(n_all):.3f})")
    print(f"         每股贏地板={win}/{len(per)}")
    if a_m > n_m:
        print("判定:✓ 有證據(整體 mean hit > naive)——仍≠可交易、不進 Phase 1 自動")
        return 0
    print("判定:✗ 無證據(未嚴格勝過 naive 地板)——停、不進 Phase 1")
    return 2


if __name__ == "__main__":
    sys.exit(main())

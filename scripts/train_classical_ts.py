#!/usr/bin/env python
"""古典 TS 薄殼 CLI — 庫內單股 ARIMA 煙測／探針入口(S4-Wave-B-ADAPTER Phase 0)。

🎯 這支在做什麼(白話):從庫內讀一支股的還原價序列,fit ArimaUnivariate,印未來 h 步點預測。
   預設 --dry-run(只算+印);**不**寫 model_registry／prediction_values。
   量尺另書——本 CLI 不做經濟終關、不與 RankRidge 冠軍比。
守 #8(as-of 只讀已見價)· skip-sync· no-SIM-apply· Wave-B「禁 sim GARCH 冒充預測」。

執行指令矩陣:
  python scripts/train_classical_ts.py                              # 無參數:印矩陣
  python scripts/train_classical_ts.py --selftest                   # 轉呼叫 library 自測
  python scripts/train_classical_ts.py --run --stock 2330 --asof 2026-05-31 --horizon 20
  python scripts/train_classical_ts.py --run --stock 2330 --asof 2026-05-31 --horizon 20 --dry-run
"""
import argparse
import sys

import _bootstrap  # noqa: F401
import numpy as np

from augur.catalog import world_concept
from augur.models.classical_ts import ArimaUnivariate

ADJ_CONCEPT = "tw.daily_bar_adjusted"  # WM.36；不直綁還原價表字面


def _load_close(conn, stock_id, asof, lookback=252):
    """讀 ≤asof 之還原收盤;不足則回空陣列(呼叫端誠實 SKIP)。

    表名經 registry `tw.daily_bar_adjusted` 解析（WM.36／binding 100），fail-closed。
    """
    adj_sql = world_concept.resolve_sql(ADJ_CONCEPT, conn=conn)
    with conn.cursor() as cur:
        cur.execute(
            f"""SELECT close FROM {adj_sql}
               WHERE stock_id=%s AND date<=%s AND close IS NOT NULL AND close>0
               ORDER BY date DESC LIMIT %s""",
            (stock_id, asof, lookback),
        )
        rows = cur.fetchall()
    if not rows:
        return np.array([], dtype=float)
    return np.array([float(r[0]) for r in reversed(rows)], dtype=float)


def run_one(stock_id, asof, horizon, dry_run):
    from augur.core import db
    with db.connect() as conn:
        closes = _load_close(conn, stock_id, asof)
    if len(closes) < 40:
        print(f"✗ SKIP {stock_id}: 有效收盤列 {len(closes)}<40")
        return 1
    # 用 log-return 序列 fit(較價水準穩定);預測還原為累積近似僅供煙測
    rets = np.diff(np.log(closes))
    try:
        est = ArimaUnivariate(order=(1, 0, 1)).fit(rets)
        fc = est.predict_horizon(horizon)
    except Exception as e:
        print(f"✗ SKIP {stock_id}: {type(e).__name__}: {e}")
        return 1
    print(f"✓ {stock_id} asof={asof} h={horizon} n_ret={len(rets)} "
          f"fc_mean={float(np.mean(fc)):.6f} fc_last={float(fc[-1]):.6f}"
          f"{' (dry-run)' if dry_run else ''}")
    print("  註:點預測≠可交易;另書量尺未跑——Phase 0 煙測 only")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--stock", default="2330")
    ap.add_argument("--asof", default="2026-05-31")
    ap.add_argument("--horizon", type=int, default=20)
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--no-dry-run", action="store_false", dest="dry_run")
    args = ap.parse_args(argv)
    if args.selftest:
        from augur.models.classical_ts import _selftest
        return _selftest()
    if not args.run:
        print(__doc__.split("執行指令矩陣:")[1])
        return 0
    return run_one(args.stock, args.asof, args.horizon, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())

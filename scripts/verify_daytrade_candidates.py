#!/usr/bin/env python
"""augur 當沖候選複核 — 探索浮現之當沖兩訊號,過提拔關卡(制度資產紀律:過漏斗才算)。

🎯 這支在做什麼(白話):擴充相關探索浮現 day_trade_ratio(當沖比)、day_trade_imbalance(當沖買賣不均)為僅有
之新預測訊號(弱、|0.02|、量軸相關)。做成 as-of 特徵(20d 均、≤t)、過提拔關卡(as-of HAC + 共線 + 多因子增量)。

cutoff-free(比率/不均、20d 均;#9)、as-of ≤t(#8)、算不出缺列(#1)。實驗 x_ 前綴、驗後 --clear。
守 #8 · #9 · #11 · #12 · #15 · #28。
執行指令矩陣:python scripts/verify_daytrade_candidates.py --seeds 3 --h 20,60 [--clear]
"""
import argparse

import numpy as np
from psycopg2.extras import execute_values

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.audit import feature_candidate as fc
from augur.audit import feature_diagnostics as fd
from augur.core import db
from augur.evaluation import baseline, metrics
from augur.evaluation import label as label_mod

CANDS = ["x_day_trade_ratio_20d", "x_day_trade_imbalance_20d"]
_SQL = ('SELECT d.date, d."Volume"::float8, p."Trading_Volume"::float8, d."BuyAmount"::float8, d."SellAmount"::float8 '
        'FROM "TaiwanStockDayTrading" d JOIN "TaiwanStockPrice" p ON p.stock_id=d.stock_id AND p.date=d.date '
        'WHERE d.stock_id=%s ORDER BY d.date')


def _asof_panels(cur):
    cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
    return [r[0] for r in cur.fetchall()]


def _compute(conn, panels):
    fc.ensure_candidate_table(conn)
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT stock_id FROM core_universe_asof")
        stocks = [str(r[0]) for r in cur.fetchall()]
    pset = sorted(panels)
    written = 0
    for sid in stocks:
        with db.transaction(conn) as cur:
            cur.execute(_SQL, (sid,))
            rows = cur.fetchall()
        if len(rows) < 20:
            continue
        dates = [r[0] for r in rows]
        ratio, imb = [], []
        for _, dv, tv, b, s in rows:
            ratio.append(dv / tv if (tv and tv > 0) else np.nan)
            imb.append((b - s) / (b + s) if (b is not None and s is not None and (b + s) > 0) else np.nan)
        ratio, imb = np.array(ratio, float), np.array(imb, float)
        out = []
        for pd_ in pset:
            j = np.searchsorted(dates, pd_, side="right")        # 最近 ≤ pd_ 之 index
            if j < 20:
                continue
            w_r, w_i = ratio[j - 20:j], imb[j - 20:j]
            r_, i_ = w_r[np.isfinite(w_r)], w_i[np.isfinite(w_i)]
            if len(r_) >= 10:
                out.append((pd_, sid, "x_day_trade_ratio_20d", round(float(r_.mean()), 6)))
            if len(i_) >= 10:
                out.append((pd_, sid, "x_day_trade_imbalance_20d", round(float(i_.mean()), 6)))
        if out:
            with db.transaction(conn) as cur:
                execute_values(cur, f"INSERT INTO {fc.FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s "
                               f"ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", out)
            written += len(out)
    return written


def _clear(conn):
    with db.transaction(conn) as cur:
        cur.execute(f"DELETE FROM {fc.FEATURE_TABLE} WHERE feature = ANY(%s)", (CANDS,))
        return cur.rowcount


def _ic(conn, panels, h, feat, cal):
    out = {}
    for pd_ in panels:
        stk = baseline._asof_stocks(conn, pd_)
        sids, X = baseline._panel_matrix(conn, pd_, stk, [feat])
        if len(sids) < 5:
            continue
        lab = label_mod.labels(conn, pd_, sids, h, calendar=cal)
        ic = metrics.rank_ic({s: X[i, 0] for i, s in enumerate(sids)}, lab)
        if ic is not None:
            out[pd_] = ic
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--h", default="20,60")
    ap.add_argument("--clear", action="store_true")
    args = ap.parse_args()
    hs = [int(x) for x in args.h.split(",")]
    with db.connect() as conn:
        if args.clear:
            print(f"清當沖候選:{_clear(conn)} 列刪"); return
        with db.transaction(conn) as cur:
            panels = _asof_panels(cur)
        print(f"算當沖候選… 寫入 {_compute(conn, panels):,} 值")
        cal = label_mod.full_calendar(conn)
        canon = [f for f in baseline.canonical_features(conn, panels) if f not in CANDS]

        print(f"\n══ 1. as-of 單因子 IC + HAC ══")
        print(f"{'candidate':26s} {'H':>3s} {'IC':>8s} {'iid-t':>7s} {'HAC-t':>7s} {'勝率':>5s}")
        passed = False
        for f in CANDS:
            for h in hs:
                s = metrics.summarize(_ic(conn, panels, h, f, cal))
                hac = metrics.effective_t_hac(_ic(conn, panels, h, f, cal))
                if s["mean_ic"] is None:
                    print(f"{f:26s} {h:>3d}  n/a"); continue
                if hac is not None and abs(hac) >= 2:
                    passed = True
                print(f"{f:26s} {h:>3d} {s['mean_ic']:>+8.4f} {s['effective_t']:>7.2f} {(hac if hac is not None else float('nan')):>7.2f} {s['hit_rate']:>5.2f}")

        print(f"\n══ 2. 共線(vs 量軸 volume/turnover/range)══")
        col = fd.collinearity(conn, panels, baseline._asof_stocks(conn, panels[-1]),
                              CANDS + ["turnover_mean_20d", "range_mean_20d", "volume_surge_5_60"], threshold=0.4, asof=True)
        for a, b, r in col["high_pairs"][:8]:
            print(f"  {a} ~ {b}: {r:+.3f}")
        if not col["high_pairs"]:
            print("  (無 |r|≥0.4 對)")

        if passed:
            print(f"\n══ 3. 多 seed 多因子增量(HAC 通過、續驗)══")
            for h in hs:
                base = {m: np.mean([baseline.run_ladder(conn, panels, h, None, feats=canon, seed=42+k, asof=True)[m]["mean_ic"] for k in range(args.seeds)]) for m in ("B2_ridge", "M1_gbdt")}
                add = {m: np.mean([baseline.run_ladder(conn, panels, h, None, feats=canon+CANDS, seed=42+k, asof=True)[m]["mean_ic"] for k in range(args.seeds)]) for m in ("B2_ridge", "M1_gbdt")}
                for m in ("B2_ridge", "M1_gbdt"):
                    print(f"  H={h:>3d} {m:10s} 生產 {base[m]:+.4f} → +當沖 {add[m]:+.4f}  Δ={add[m]-base[m]:+.4f}")
        else:
            print("\n→ 單因子 HAC 全 <2、不顯著 → 免續多因子;不提拔(省算 #28)。")
        print("\n判讀:HAC |≥2| + 低共線 + 多因子增量正 → 提拔;否則 --clear。")


if __name__ == "__main__":
    main()

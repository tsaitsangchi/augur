#!/usr/bin/env python
"""augur 評估 run — 呼叫 evaluation.baseline.run_ladder 跑基準階梯 purged walk-forward rank IC（#8/#12/#15）。

🎯 這支在做什麼（白話）：對核心股、用 feature_values 特徵，跑 B0 隨機 / B1 動能 / B2 Ridge / M1 GBDT 基準階梯，
過 purged walk-forward（#8），報每模型的 rank IC / Effective-t / 勝率（橫斷面相對強弱口徑、非 AUC #14）。
可選多 H（週/月/季/年）、pan-historical（固定 core_universe）或 as-of（逐面板 point-in-time、消 survivorship）、
多 seed（GBDT stochastic 取統計 #15）。純 DB 計算、不放 API。

組合根：把 evaluation 層接上薄 CLI；口徑（label/metric/walkforward）全 import SSOT helper（#12 可比）。

守 #8（label t+1 + purged walk-forward）· #12（單一 helper 口徑可比）· #14（rank IC 非 AUC）· #15（多 seed 誠實）· #18。

執行指令矩陣:python scripts/run_evaluation.py --since 2014-01-01 --h 20,60 --asof       （M-1/M-2 口徑）
      python scripts/run_evaluation.py --since 2014-01-01 --h 60 --seeds 3 --asof  （GBDT 3 seed）
"""
import argparse

import numpy as np

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.evaluation import baseline

MODELS = ("B0_random", "B1_momentum", "B2_ridge", "M1_gbdt")


def _panels(cur, since):
    sql = "SELECT DISTINCT panel_date FROM feature_values"
    params = ()
    if since:
        sql += " WHERE panel_date >= %s"
        params = (since,)
    cur.execute(sql + " ORDER BY panel_date", params)
    return [r[0] for r in cur.fetchall()]


def _core(cur):
    cur.execute("SELECT stock_id FROM core_universe ORDER BY stock_id")
    return [r[0] for r in cur.fetchall()]


def _fmt(s):
    if not s or s.get("mean_ic") is None:
        return "n/a"
    t = f" / t {s['effective_t']:.2f}" if s.get("effective_t") else ""
    hr = f" / 勝率 {s['hit_rate']:.2f}" if s.get("hit_rate") is not None else ""
    return f"IC {s['mean_ic']:+.3f}{t}{hr} (n={s['n_panels']})"


def _run(conn, panels, h, core, asof, seeds, interactions=None):
    """單 seed 直接 run_ladder；多 seed 對 4 模型 mean_ic 取平均（#15 stochastic）。"""
    if seeds <= 1:
        return baseline.run_ladder(conn, panels, h, core, asof=asof, interactions=interactions)
    runs = [baseline.run_ladder(conn, panels, h, core, seed=42 + k, asof=asof, interactions=interactions) for k in range(seeds)]
    agg = {}
    for m in MODELS:
        ics = [r[m]["mean_ic"] for r in runs if r[m]["mean_ic"] is not None]
        base = dict(runs[0][m])
        base["mean_ic"] = float(np.mean(ics)) if ics else None
        agg[m] = base
    return agg


def main():
    ap = argparse.ArgumentParser(description="run 基準階梯 purged walk-forward")
    ap.add_argument("--since", default="2014-01-01", help="面板起始日（預設 2014-01-01＝M-1 口徑）")
    ap.add_argument("--h", default="20,60", help="forward horizon 交易日（逗號分隔）")
    ap.add_argument("--asof", action="store_true", help="加跑 as-of point-in-time 口徑（消 survivorship）")
    ap.add_argument("--seeds", type=int, default=1, help="GBDT 多 seed 取統計（#15 stochastic）")
    ap.add_argument("--interactions", default=None, help="加入交互特徵（逗號分隔、如 inter_fh_x_p10yr；eval 層橫斷面 z 乘積、見 cross_section.INTERACTIONS）")
    args = ap.parse_args()
    hs = [int(x) for x in args.h.split(",")]
    inter = [s.strip() for s in args.interactions.split(",")] if args.interactions else None

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            panels = _panels(cur, args.since)
            core = _core(cur)
        if not panels or not core:
            print("無面板或無核心股（先跑 build_feature_panel / build_core_universe）")
            return
        print(f"評估：{len(panels)} 面板（{panels[0]}..{panels[-1]}）× {len(core)} 核心股"
              f" / H={hs} / seeds={args.seeds}" + (f" / interactions={inter}" if inter else ""))
        modes = [("pan-hist", False)] + ([("as-of ", True)] if args.asof else [])
        for h in hs:
            print(f"\n── H={h} ──")
            for name, asof in modes:
                res = _run(conn, panels, h, core, asof, args.seeds, inter)
                print(f"  [{name}]")
                for m in MODELS:
                    print(f"    {m:12s} {_fmt(res[m])}")


if __name__ == "__main__":
    main()

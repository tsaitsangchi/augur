#!/usr/bin/env python
"""augur horizon × 宇宙掃描 — 換 horizon/宇宙是否解鎖不同 alpha 結構(特徵飽和後之逃脫方向)。

🎯 這支在做什麼(白話):特徵層五輪飽和;換「問題」可能解鎖不同 alpha:
- **horizon 半**:模型 mean IC 於 H=5/20/60/120/252(as-of core)——哪個持有期預測結構最強。
- **宇宙 半**:訓練於 core、測於 core(848)vs 擴大(per-panel 全特徵齊備、全 roster ~3080)——
  (1) 模型推廣 IC(alpha 是否推廣到更多名)(2) 宇宙規模 (3) 關鍵特徵單因子 IC 對照。

口徑 reuse baseline/label/metrics/walkforward(#12);as-of point-in-time(#8);Ridge 確定性(宇宙半免多 seed)。
守 #8 · #12 · #15(揭露 n/規模) · #28(本地零 usage)。
執行指令矩陣:python scripts/run_horizon_universe_scan.py --mode both --seeds 3
"""
import argparse

import numpy as np

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.evaluation import baseline, walkforward
from augur.evaluation import label as label_mod
from augur.evaluation import metrics

KEY_FEATS = ["pb_ratio", "cycle_position_252d", "inst_cumflow_position_120d", "volume_gini_60d", "momentum_60d"]


def _feature_complete(conn, panel, feats):
    """某 panel 全特徵齊備之股(擴大宇宙、不限 core_gate)。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT stock_id FROM feature_values WHERE panel_date=%s AND feature = ANY(%s) "
                    "GROUP BY stock_id HAVING count(DISTINCT feature) = %s", (panel, list(feats), len(feats)))
        return [str(r[0]) for r in cur.fetchall()]


def _horizon_scan(conn, panels, seeds):
    print(f"══ 1. horizon 掃描(as-of core、{seeds} seed、模型 mean IC)══")
    print(f"{'H':>5s} {'B2_ridge':>10s} {'M1_gbdt':>10s} {'B1_mom':>10s}")
    for h in (5, 20, 60, 120, 252):
        acc = {"B2_ridge": [], "M1_gbdt": [], "B1_momentum": []}
        for k in range(seeds):
            r = baseline.run_ladder(conn, panels, h, None, seed=42 + k, asof=True)
            for m in acc:
                if r[m]["mean_ic"] is not None:
                    acc[m].append(r[m]["mean_ic"])
        f = lambda m: (np.mean(acc[m]) if acc[m] else float("nan"))
        print(f"{h:>5d} {f('B2_ridge'):>+10.4f} {f('M1_gbdt'):>+10.4f} {f('B1_momentum'):>+10.4f}")


def _universe_scan(conn, panels, h, feats, cal):
    """訓練於 core、測於 core vs 擴大:模型推廣 IC + 宇宙規模。"""
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    folds = walkforward.splits(panels, h)
    ic_core, ic_exp, n_core, n_exp = {}, {}, [], []
    for fold in folds:
        tpd = fold["test"]
        Xtr, ytr = baseline._fold_xy(conn, fold["train"], None, feats, h, calendar=cal, asof=True)  # 訓練=core(asof)
        if len(ytr) < 50:
            continue
        sc = StandardScaler().fit(Xtr)
        mdl = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr)
        core_test = baseline._asof_stocks(conn, tpd)
        exp_test = _feature_complete(conn, tpd, feats)
        for universe, store, ns in ((core_test, ic_core, n_core), (exp_test, ic_exp, n_exp)):
            sids, Xte = baseline._panel_matrix(conn, tpd, universe, feats)
            if len(sids) < 10:
                continue
            lab = label_mod.labels(conn, tpd, sids, h, calendar=cal)
            keep = [i for i, s in enumerate(sids) if s in lab]
            if len(keep) < 10:
                continue
            ic = metrics.rank_ic({sids[i]: float(mdl.predict(sc.transform(Xte[i:i + 1]))[0]) for i in keep},
                                 {sids[i]: lab[sids[i]] for i in keep})
            if ic is not None:
                store[tpd] = ic
                ns.append(len(keep))
    sc_c, sc_e = metrics.summarize(ic_core), metrics.summarize(ic_exp)
    print(f"\n══ 2. 宇宙掃描(H{h}、Ridge 訓練於 core、測於 core vs 擴大)══")
    print(f"{'宇宙':10s} {'平均股數':>8s} {'模型 IC':>9s} {'Eff-t':>7s} {'勝率':>5s} {'n':>4s}")
    print(f"{'core':10s} {np.mean(n_core) if n_core else 0:>8.0f} {sc_c['mean_ic']:>+9.4f} {sc_c['effective_t']:>7.2f} {sc_c['hit_rate']:>5.2f} {sc_c['n_panels']:>4d}")
    print(f"{'擴大':10s} {np.mean(n_exp) if n_exp else 0:>8.0f} {sc_e['mean_ic']:>+9.4f} {sc_e['effective_t']:>7.2f} {sc_e['hit_rate']:>5.2f} {sc_e['n_panels']:>4d}")


def _keyfeat_universe(conn, panels, h, cal):
    """關鍵特徵單因子 rank IC:core vs 擴大(各特徵以其齊備股為宇宙)。"""
    print(f"\n══ 3. 關鍵特徵單因子 IC(H{h}、core vs 擴大)══")
    print(f"{'feature':28s} {'core IC':>9s} {'expand IC':>10s} {'expand 股':>9s}")
    for feat in KEY_FEATS:
        def _ic(universe_core):
            out = {}
            for pd_ in panels:
                stk = baseline._asof_stocks(conn, pd_) if universe_core else _feature_complete(conn, pd_, [feat])
                sids, X = baseline._panel_matrix(conn, pd_, stk, [feat])
                if len(sids) < 10:
                    continue
                lab = label_mod.labels(conn, pd_, sids, h, calendar=cal)
                ic = metrics.rank_ic({s: X[i, 0] for i, s in enumerate(sids)}, lab)
                if ic is not None:
                    out[pd_] = (ic, len(sids))
            return out
        c = metrics.summarize({p: v[0] for p, v in _ic(True).items()})
        e = _ic(False)
        es = metrics.summarize({p: v[0] for p, v in e.items()})
        esz = np.mean([v[1] for v in e.values()]) if e else 0
        if c["mean_ic"] is None or es["mean_ic"] is None:
            print(f"{feat:28s}  n/a"); continue
        print(f"{feat:28s} {c['mean_ic']:>+9.4f} {es['mean_ic']:>+10.4f} {esz:>9.0f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="both", choices=["horizon", "universe", "both"])
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s ORDER BY panel_date", ("2014-01-01",))
            panels = [r[0] for r in cur.fetchall()]
        cal = label_mod.full_calendar(conn)
        feats = baseline.canonical_features(conn, panels)
        print(f"掃描:{len(panels)} panel、canonical {len(feats)} 特徵")
        if args.mode in ("horizon", "both"):
            _horizon_scan(conn, panels, args.seeds)
        if args.mode in ("universe", "both"):
            _universe_scan(conn, panels, 60, feats, cal)
            _keyfeat_universe(conn, panels, 60, cal)
        print("\n判讀:horizon——IC 最強之 H 較佳;宇宙——擴大模型 IC 維持→alpha 推廣(可交易更多名)、衰退→core-gate 必要。")


if __name__ == "__main__":
    main()

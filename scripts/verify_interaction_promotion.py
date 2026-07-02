#!/usr/bin/env python
"""augur 交互候選 money×inst_net 提拔複核 — as-of + 去相關 HAC Eff-t + 多 seed 增量(完整漏斗)。

🎯 這支在做什麼(白話):raw 交互掃描浮現 money×inst_net(IC +0.030、t=3.6、4.5× 成分);此支走**完整提拔關卡**
定生死(不過完整漏斗不入生產):
1. **as-of 口徑**:逐 as-of panel(core_universe_asof、消完整度 look-ahead)算候選=winsor-z(money)×winsor-z(inst_net)
   (復刻發現口徑;同 panel 橫斷面、#8 安全)、寫 feature_values
2. **去相關 Eff-t**:as-of 單因子 IC 序列 iid Eff-t vs Newey-West HAC Eff-t(解 G8 重疊窗高估)
3. **多 seed 增量**:加入生產特徵集,run_ladder as-of ≥3 seed,看 Ridge/GBDT IC 增量 Δ(對 34 特徵是否真增量)
判據:as-of HAC-t 仍 |≥2| + 多 seed Δ 穩定為正 → 提拔;否則維持候選(極可能與現籌碼特徵冗餘)。
實驗、驗後清列、不入生產。守 #8 · #11 · #12 · #15(雙口徑 t、誠實)· #28(本地零 usage)。
執行指令矩陣:python scripts/verify_interaction_promotion.py --h 20,60 --seeds 3
"""
import argparse

import numpy as np
from psycopg2.extras import execute_values

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.evaluation import baseline, metrics
from augur.evaluation import label as label_mod

CAND = "money_x_inst_net"


def _wz(d):
    """{id:val} → winsor±3 橫斷面 z(復刻 run_raw_interaction_ic 口徑;<30 或零變異→空)。"""
    items = [(k, float(v)) for k, v in d.items() if v is not None and np.isfinite(float(v))]
    if len(items) < 30:
        return {}
    v = np.array([x for _, x in items])
    mu, sd = v.mean(), v.std()
    if sd == 0:
        return {}
    z = np.clip((v - mu) / sd, -3, 3)
    return {k: float(zz) for (k, _), zz in zip(items, z)}


def _asof_panels(cur):
    cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
    return [r[0] for r in cur.fetchall()]


def _compute_candidate(conn, panels):
    """逐 as-of panel 算 money_x_inst_net=wz(money)×wz(inst_net)、寫 feature_values。回寫入列數。"""
    written = 0
    for pd_ in panels:
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (pd_,))
            stk = [str(r[0]) for r in cur.fetchall()]
            if not stk:
                continue
            cur.execute('SELECT stock_id, "Trading_money"::float8 FROM "TaiwanStockPrice" '
                        'WHERE date::text=%s AND stock_id = ANY(%s) AND "Trading_money" IS NOT NULL',
                        (str(pd_), stk))
            money = {str(r[0]): float(r[1]) for r in cur.fetchall()}
            cur.execute('SELECT stock_id, sum(COALESCE(buy,0)-COALESCE(sell,0)) '
                        'FROM "TaiwanStockInstitutionalInvestorsBuySell" '
                        'WHERE date::text=%s AND stock_id = ANY(%s) GROUP BY stock_id', (str(pd_), stk))
            inet = {str(r[0]): float(r[1]) for r in cur.fetchall()}
        zm, zi = _wz(money), _wz(inet)
        rows = [(pd_, sid, CAND, round(zm[sid] * zi[sid], 6)) for sid in set(zm) & set(zi)]
        if rows:
            with db.transaction(conn) as cur:
                execute_values(cur, "INSERT INTO feature_values (panel_date, stock_id, feature, value) VALUES %s "
                               "ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", rows)
            written += len(rows)
    return written


def _asof_ic_series(conn, panels, h, feat, cal):
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
    ap = argparse.ArgumentParser(description="money×inst_net 提拔複核")
    ap.add_argument("--h", default="20,60")
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()
    hs = [int(x) for x in args.h.split(",")]

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            panels = _asof_panels(cur)
        print(f"as-of 複核:{len(panels)} panel（{panels[0]}..{panels[-1]}）")
        print(f"算 as-of 候選 {CAND}… 寫入 {_compute_candidate(conn, panels):,} 值")
        cal = label_mod.full_calendar(conn)

        print("\n══ 1. as-of 單因子 rank IC:iid Eff-t vs Newey-West HAC Eff-t（去相關、審查 G8）══")
        print(f"{'candidate':18s} {'H':>3s} {'IC':>8s} {'iid-t':>7s} {'HAC-t':>7s} {'勝率':>5s} {'n':>3s}")
        for h in hs:
            ser = _asof_ic_series(conn, panels, h, CAND, cal)
            s = metrics.summarize(ser)
            hac = metrics.effective_t_hac(ser)
            if s["mean_ic"] is None:
                print(f"{CAND:18s} {h:>3d}   n/a"); continue
            print(f"{CAND:18s} {h:>3d} {s['mean_ic']:>+8.4f} {s['effective_t']:>7.2f} "
                  f"{(hac if hac is not None else float('nan')):>7.2f} {s['hit_rate']:>5.2f} {s['n_panels']:>3d}")

        print(f"\n══ 2. 多 seed 增量:{CAND} 加入生產集(as-of、{args.seeds} seed)══")
        prod = [x for x in baseline.canonical_features(conn, panels) if x != CAND]
        print(f"   生產基準 {len(prod)} 特徵 vs +{CAND}")
        for h in hs:
            base_ic, add_ic = {"B2_ridge": [], "M1_gbdt": []}, {"B2_ridge": [], "M1_gbdt": []}
            for k in range(args.seeds):
                rb = baseline.run_ladder(conn, panels, h, None, feats=prod, seed=42 + k, asof=True)
                ra = baseline.run_ladder(conn, panels, h, None, feats=prod + [CAND], seed=42 + k, asof=True)
                for m in ("B2_ridge", "M1_gbdt"):
                    if rb[m]["mean_ic"] is not None: base_ic[m].append(rb[m]["mean_ic"])
                    if ra[m]["mean_ic"] is not None: add_ic[m].append(ra[m]["mean_ic"])
            for m in ("B2_ridge", "M1_gbdt"):
                b = np.mean(base_ic[m]) if base_ic[m] else float('nan')
                a = np.mean(add_ic[m]) if add_ic[m] else float('nan')
                print(f"   H={h:>3d} {m:10s} 基準 {b:+.4f} → +候選 {a:+.4f}  Δ={a-b:+.4f}")

        with db.transaction(conn) as cur:
            cur.execute("DELETE FROM feature_values WHERE feature=%s", (CAND,))
            print(f"\n清候選列:{cur.rowcount} 列刪(實驗、不入生產)")
        print("判讀:as-of HAC-t |≥2| + 多 seed Δ 穩定為正 → 提拔;否則維持候選(與現籌碼特徵冗餘)。")


if __name__ == "__main__":
    main()

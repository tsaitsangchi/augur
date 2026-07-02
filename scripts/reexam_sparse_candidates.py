#!/usr/bin/env python
"""augur 歷史稀疏候選公平重檢 — 用同宇宙(impute)增量測重驗,看覆蓋假象是否冤殺過真訊號。

🎯 這支在做什麼(白話):揪出的覆蓋假象 bug(稀疏候選缺值股被踢→Δ 假負)意味歷史用舊增量測淘汰的
**稀疏籌碼/基本面候選可能被冤殺**。此支復用既有 _compute 填 7 個稀疏候選(當沖2 + 基本面5)→
各候選缺值補 panel 中位(同宇宙)→ base vs +候選公平增量 Δ。base 算一次快取、各候選共用(省算 #28)。
判據:公平 Δ 穩定為正(>+0.002)→ 翻案候選、續經濟價值測;否則確認原淘汰正確(非假象)。
守 #8 · #11 · #12 · #15 · #28。用法:python scripts/reexam_sparse_candidates.py --seeds 3 --h 20,60

執行指令矩陣:
  python scripts/reexam_sparse_candidates.py
"""
import argparse
import importlib.util

import numpy as np
from psycopg2.extras import execute_values

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.evaluation import baseline
from augur.evaluation import label as label_mod

ROOT = "/home/hugo/project/augur/scripts/"


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, ROOT + fn)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _densify(conn, panels, cand):
    """讀 feature_values 中稀疏候選 cand,各 panel 缺(as-of)股補中位 → 寫 cand+'_imp'。回(列, 覆蓋率)。"""
    name = cand + "_imp"
    written = real = total = 0
    for pd_ in panels:
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (pd_,))
            stk = [str(r[0]) for r in cur.fetchall()]
            if not stk:
                continue
            cur.execute("SELECT stock_id, value FROM feature_values WHERE panel_date=%s AND feature=%s AND stock_id=ANY(%s)",
                        (pd_, cand, stk))
            vals = {str(r[0]): float(r[1]) for r in cur.fetchall()}
        real += len(vals); total += len(stk)
        if not vals:
            continue
        med = float(np.median(list(vals.values())))
        rows = [(pd_, s, name, round(float(vals.get(s, med)), 6)) for s in stk]
        with db.transaction(conn) as cur:
            execute_values(cur, "INSERT INTO feature_values (panel_date, stock_id, feature, value) VALUES %s "
                           "ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", rows)
        written += len(rows)
    return written, (real / total if total else 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3); ap.add_argument("--h", default="20,60")
    args = ap.parse_args()
    hs = [int(x) for x in args.h.split(",")]
    dt = _load("vdt", "verify_daytrade_candidates.py")
    fu = _load("vfu", "verify_fundamental_candidates.py")
    sparse = dt.CANDS + fu.CANDS

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
            panels = [r[0] for r in cur.fetchall()]
        print("填稀疏候選(復用既有 _compute)…")
        print(f"  當沖:{dt._compute(conn, panels):,} 值;基本面:{fu._compute(conn, panels):,} 值")
        imp = []
        print("\n各候選真實覆蓋率(↓低=覆蓋假象嫌疑大):")
        for c in sparse:
            w, cov = _densify(conn, panels, c)
            imp.append((c, cov))
            print(f"  {c:30s} 覆蓋 {cov:>4.0%} → {c}_imp 補滿 {w:,}")

        allnames = sparse + [c + "_imp" for c in sparse]
        base = [f for f in baseline.canonical_features(conn, panels) if f not in allnames]
        print(f"\n══ 公平增量(同宇宙、base {len(base)} 特徵、{args.seeds} seed)══")
        # base IC 快取(各 h/seed/model 算一次)
        bcache = {}
        for h in hs:
            for k in range(args.seeds):
                r = baseline.run_ladder(conn, panels, h, None, feats=base, seed=42 + k, asof=True)
                for m in ("B2_ridge", "M1_gbdt"):
                    bcache.setdefault((h, m), []).append(r[m]["mean_ic"])
        bmean = {key: np.mean([x for x in v if x is not None]) for key, v in bcache.items()}

        print(f"  {'candidate':30s} {'H':>3s} {'Ridge Δ':>9s} {'GBDT Δ':>9s} {'判':>6s}")
        flagged = []
        for c, cov in imp:
            name = c + "_imp"
            for h in hs:
                add = {m: [] for m in ("B2_ridge", "M1_gbdt")}
                for k in range(args.seeds):
                    ra = baseline.run_ladder(conn, panels, h, None, feats=base + [name], seed=42 + k, asof=True)
                    for m in add:
                        if ra[m]["mean_ic"] is not None: add[m].append(ra[m]["mean_ic"])
                dr = (np.mean(add["B2_ridge"]) - bmean[(h, "B2_ridge")]) if add["B2_ridge"] else float('nan')
                dg = (np.mean(add["M1_gbdt"]) - bmean[(h, "M1_gbdt")]) if add["M1_gbdt"] else float('nan')
                mark = "✅+" if (dr > 0.002 or dg > 0.002) else ("~" if max(abs(dr), abs(dg)) <= 0.002 else "✗−")
                if dr > 0.002 or dg > 0.002:
                    flagged.append((c, h, dr, dg))
                print(f"  {c:30s} {h:>3d} {dr:>+9.4f} {dg:>+9.4f} {mark:>6s}")

        with db.transaction(conn) as cur:
            cur.execute("DELETE FROM feature_values WHERE feature = ANY(%s)", (allnames,))
            print(f"\n清候選列(稀疏+imp):{cur.rowcount} 列刪")
        if flagged:
            print("\n🔎 公平測下翻案嫌疑(Δ>+0.002、待經濟價值確認):")
            for c, h, dr, dg in flagged:
                print(f"  {c} H={h}:Ridge Δ{dr:+.4f} / GBDT Δ{dg:+.4f}")
        else:
            print("\n→ 公平測下全候選 Δ ≤ +0.002:**原淘汰正確、非覆蓋假象冤殺**。飽和確認。")
        print("判讀:Δ>+0.002 → 翻案、續 verify_economic_candidate;否則原淘汰成立。")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""augur 候選提拔複核 — as-of + 去相關 Eff-t(HAC) + 多 seed 增量,決定是否提拔進生產。

🎯 這支在做什麼(白話):對初步通過五鏡之 2 候選(pb_self_pctile_252d、inst_govbank_divergence),
做提拔前的嚴格複核(守「未過完整漏斗不入生產」):
1. **as-of 口徑**:逐 panel 用 core_universe_asof(point-in-time、消完整度 look-ahead)算候選與 IC
2. **去相關 Eff-t**:IC 序列 iid Eff-t vs Newey-West HAC Eff-t(解 G8、重疊窗自相關高估顯著)
3. **多 seed 增量**:pb_self_pctile 加入 26-feat 生產集,run_ladder as-of ≥3 seed,看 Ridge/GBDT IC 增量

候選 as-of 安全(#8):自身歷史百分位用 ≤t 窗;背離 z 於同 panel as-of 橫斷面。實驗、驗後 --clear、不入生產。
判據:as-of HAC Eff-t 仍顯著(|t|≥2)+ 多 seed 增量穩定為正 → 建議提拔;否則維持候選。

守 #8(as-of)· #11(五鏡)· #12(label/metric/baseline SSOT)· #15(雙口徑 t、誠實)· #28(本地、零 usage)。

執行指令矩陣:
  python scripts/verify_candidate_promotion.py --h 20,60 --seeds 3   # 內建 2 候選(重算+驗後清)
  python scripts/verify_candidate_promotion.py --features lending_fee_rate_mean_20d,days_since_high_126d\
      --h 20,60 --seeds 3   # 外部 staged 候選:不重算、逐候選增量、收尾不清表(A2 口徑)
"""
import argparse

import numpy as np

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.audit import feature_candidate as fc
from augur.core import db
from augur.evaluation import baseline, metrics
from augur.evaluation import label as label_mod

CANDS = ["pb_self_pctile_252d", "inst_govbank_divergence"]


def _asof_panels(cur):
    cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
    return [r[0] for r in cur.fetchall()]


def _asof_universe_union(cur):
    cur.execute("SELECT DISTINCT stock_id FROM core_universe_asof")
    return [str(r[0]) for r in cur.fetchall()]


def _compute_asof_candidates(conn, panels):
    """逐 panel 用 as-of 宇宙算 2 候選、寫候選 staging 表(as-of 橫斷面正確)。回寫入列數。"""
    fc.ensure_candidate_table(conn)
    with db.transaction(conn) as cur:
        union = _asof_universe_union(cur)
        cur.execute('SELECT stock_id, date, "PBR"::float8 FROM "TaiwanStockPER" WHERE stock_id = ANY(%s) AND "PBR" IS NOT NULL ORDER BY stock_id, date', (union,))
        pbr_hist = {}
        for sid, d, v in cur.fetchall():
            pbr_hist.setdefault(str(sid), []).append((d, float(v)))
    from psycopg2.extras import execute_values
    written = 0
    for pd_ in panels:
        with db.transaction(cur_conn := conn) as cur:
            cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (pd_,))
            stk = [str(r[0]) for r in cur.fetchall()]
            inst = fc._panel_feature(cur, pd_, "institutional_net_buy_ratio_20d", stk)
            gov = fc._panel_feature(cur, pd_, "gov_bank_net_buy_60d", stk)
        rows = []
        for sid in stk:                                            # pb_self_pctile_252d(≤t 自身歷史)
            hist = [v for (d, v) in pbr_hist.get(sid, []) if d <= pd_]
            if len(hist) >= 60:
                win = hist[-252:]
                rows.append((pd_, sid, "pb_self_pctile_252d", round(float(np.mean([1.0 if x <= win[-1] else 0.0 for x in win])), 6)))
        zi, zg = fc._zscore(inst), fc._zscore(gov)                 # inst_govbank_divergence(as-of 橫斷面 z)
        for sid in set(zi) & set(zg):
            rows.append((pd_, sid, "inst_govbank_divergence", round(zi[sid] - zg[sid], 6)))
        if rows:
            with db.transaction(conn) as cur:
                execute_values(cur, f"INSERT INTO {fc.FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s "
                               f"ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", rows)
            written += len(rows)
    return written


def _asof_ic_series(conn, panels, h, feat, cal):
    """單候選 as-of 逐 panel 橫斷面 rank IC → {panel: ic}。"""
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
    ap = argparse.ArgumentParser(description="候選提拔複核(as-of + HAC + 多 seed)")
    ap.add_argument("--h", default="20,60")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--features", help="逗號分隔候選名(已 staged 於 feature_candidate_values;"
                                       "略過內建 2 候選之重算,增量測試逐一對生產基準)")
    ap.add_argument("--keep", action="store_true", help="收尾不清候選表(staged 值另有主人時必帶)")
    args = ap.parse_args()
    hs = [int(x) for x in args.h.split(",")]
    feats_ext = args.features.split(",") if args.features else None

    with db.connect() as conn:
        with db.transaction(conn) as cur:
            panels = _asof_panels(cur)
        print(f"as-of 複核:{len(panels)} panel（{panels[0]}..{panels[-1]}）")
        if feats_ext is None:
            print(f"算 as-of 候選… 寫入 {_compute_asof_candidates(conn, panels):,} 值")
        else:
            print(f"外部候選 {len(feats_ext)} 顆(讀既有 staged 值,不重算): {', '.join(feats_ext)}")
        cal = label_mod.full_calendar(conn)

        print(f"\n══ 1. as-of 單因子 rank IC:iid Eff-t vs Newey-West HAC Eff-t（去相關、審查 G8）══")
        print(f"{'candidate':26s} {'H':>3s} {'IC':>8s} {'iid-t':>7s} {'HAC-t':>7s} {'勝率':>5s} {'n':>3s}")
        for f in (feats_ext or CANDS):
            for h in hs:
                ser = _asof_ic_series(conn, panels, h, f, cal)
                s = metrics.summarize(ser)
                hac = metrics.effective_t_hac(ser)
                if s["mean_ic"] is None:
                    print(f"{f:26s} {h:>3d}   n/a"); continue
                print(f"{f:26s} {h:>3d} {s['mean_ic']:>+8.4f} {s['effective_t']:>7.2f} "
                      f"{(hac if hac is not None else float('nan')):>7.2f} {s['hit_rate']:>5.2f} {s['n_panels']:>3d}")

        inc_feats = feats_ext or ["pb_self_pctile_252d"]
        print(f"\n══ 2. 多 seed 增量:逐候選加入生產集(as-of、{args.seeds} seed)══")
        prod = [x for x in baseline.canonical_features(conn, panels) if x not in fc.CANDIDATES]
        print(f"   生產基準 {len(prod)} 特徵;逐一 +{', '.join(inc_feats)}")
        rb_cache = {}
        for cand in inc_feats:
            # 覆蓋對齊(防覆蓋假象):候選有值的 panel 子集上「基準 vs +候選」同尺互比——
            # _panel_matrix 全齊才收股,候選短史會把 +候選側截斷成不同 panel 集=假 Δ。
            with db.transaction(conn) as cur:
                cur.execute(f"SELECT DISTINCT panel_date FROM {fc.FEATURE_TABLE} WHERE feature=%s", (cand,))  # noqa: S608
                p_use = sorted(set(r[0] for r in cur.fetchall()) & set(panels)) if feats_ext else panels
            if not p_use:
                print(f"   {cand:26s} 無重疊 panel(staged 值缺)——跳過")
                continue
            print(f"   {cand:26s} 比較尺={len(p_use)} panel({p_use[0]}..{p_use[-1]})")
            for h in hs:
                base_ic, add_ic = {"B2_ridge": [], "M1_gbdt": []}, {"B2_ridge": [], "M1_gbdt": []}
                for k in range(args.seeds):
                    key = (tuple(p_use), h, k)
                    if key not in rb_cache:
                        rb_cache[key] = baseline.run_ladder(conn, p_use, h, None, feats=prod, seed=42 + k, asof=True)
                    rb = rb_cache[key]
                    ra = baseline.run_ladder(conn, p_use, h, None, feats=prod + [cand], seed=42 + k, asof=True)
                    for m in ("B2_ridge", "M1_gbdt"):
                        if rb[m]["mean_ic"] is not None: base_ic[m].append(rb[m]["mean_ic"])
                        if ra[m]["mean_ic"] is not None: add_ic[m].append(ra[m]["mean_ic"])
                for m in ("B2_ridge", "M1_gbdt"):
                    b, a = np.mean(base_ic[m]) if base_ic[m] else float('nan'), np.mean(add_ic[m]) if add_ic[m] else float('nan')
                    print(f"   {cand:26s} H={h:>3d} {m:10s} 基準 {b:+.4f} → +候選 {a:+.4f}  Δ={a-b:+.4f}")

        if args.keep or feats_ext is not None:
            print("\n候選表保留(--keep/外部候選=staged 值另有主人,不清)")
        else:
            print(f"\n清候選列:{fc.clear_candidates(conn)} 列刪（實驗、不入生產）")
        print("判讀:as-of HAC-t 仍 |≥2| + 多 seed Δ 穩定為正 → 建議提拔;否則維持候選待強化。")


if __name__ == "__main__":
    main()

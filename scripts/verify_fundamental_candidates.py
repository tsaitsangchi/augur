#!/usr/bin/env python
"""augur phase-2 基本面候選複核 — P5 營收/產業 share(八二)+ C3 財報循環(康波),過提拔關卡。

🎯 這支在做什麼(白話):用發布日 gate(release_lag、#8)建兩條**新資訊維度**候選、過漏斗:
- **P5 八二**:`x_revenue_industry_share`(個股 TTM 營收佔產業合計、支配度)、`x_revenue_share_mom`(share ~1yr 變化、馬太×營收)
- **C3 康波**:`x_inventory_revenue_ratio`(庫存/4季營收、Kitchin)、`x_inventory_ratio_chg`(Δ、堆積vs去化方向)、
  `x_gross_margin_pctile`(毛利率於自身歷史百分位、margin 循環相位)

發布日 gate(#8):月營收次月15日、財報季底+45/90日——只用已公告者。capex 因 YTD 累計複雜暫緩。
cutoff-free(share/ratio/percentile/Δ、#9)。實驗 x_ 前綴、驗後 --clear。守 #8 · #9 · #11 · #12 · #15 · #28。
執行指令矩陣:python scripts/verify_fundamental_candidates.py --seeds 3 [--clear]
"""
import argparse
from datetime import date

import numpy as np
from psycopg2.extras import execute_values

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.audit import feature_candidate as fc
from augur.audit import feature_diagnostics as fd
from augur.core import db
from augur.evaluation import baseline, metrics
from augur.evaluation import label as label_mod
from augur.features import release_lag as rl

CANDS = ["x_revenue_industry_share", "x_revenue_share_mom", "x_inventory_revenue_ratio",
         "x_inventory_ratio_chg", "x_gross_margin_pctile"]


def _asof_panels(cur):
    cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
    return [r[0] for r in cur.fetchall()]


def _ttm_revenue(rev_rows, panel):
    """已公告(gate)之 trailing-12 月營收和;不足 12 月 → None。rev_rows=[(date,rev)] 升序。"""
    rel = [(d, v) for d, v in rev_rows if v is not None and rl.revenue_released(d, panel)]
    if len(rel) < 12:
        return None
    return float(sum(v for _, v in rel[-12:]))


def _latest_fin(rows, panel, n=1):
    """財報已公告(gate)之最近 n 筆 [(date,value)] 升序;不足 → []。"""
    rel = [(d, v) for d, v in rows if v is not None and rl.financial_released(d, panel)]
    return rel[-n:] if len(rel) >= n else []


def _compute(conn, panels):
    fc.ensure_candidate_table(conn)
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT stock_id FROM core_universe_asof")
        stocks = [str(r[0]) for r in cur.fetchall()]
        ind = fc._industry_map(cur, stocks)
        # 一次抓各源全史(避逐 panel 查)
        def _series(sql):
            cur.execute(sql, (stocks,))
            d = {}
            for sid, dt, v in cur.fetchall():
                d.setdefault(str(sid), []).append((dt, float(v) if v is not None else None))
            return d
        rev = _series('SELECT stock_id, date, revenue::float8 FROM "TaiwanStockMonthRevenue" WHERE stock_id = ANY(%s) ORDER BY stock_id, date')
        inv = _series('SELECT stock_id, date, value FROM "TaiwanStockBalanceSheet" WHERE type=\'Inventories\' AND stock_id = ANY(%s) ORDER BY stock_id, date')
        frev = _series('SELECT stock_id, date, value FROM "TaiwanStockFinancialStatements" WHERE type=\'Revenue\' AND stock_id = ANY(%s) ORDER BY stock_id, date')
        gp = _series('SELECT stock_id, date, value FROM "TaiwanStockFinancialStatements" WHERE type=\'GrossProfit\' AND stock_id = ANY(%s) ORDER BY stock_id, date')

    written = 0
    panels_sorted = sorted(panels)
    ttm_hist = {}                                                    # {stock: {panel: share}} 供 mom
    for pi, pd_ in enumerate(panels_sorted):
        with db.transaction(conn) as cur:
            cur.execute("SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s", (pd_,))
            stk = [str(r[0]) for r in cur.fetchall()]
        rows = []
        # P5:TTM 營收 → 產業 share
        ttm = {s: _ttm_revenue(rev.get(s, []), pd_) for s in stk}
        ttm = {s: v for s, v in ttm.items() if v is not None and v > 0}
        ind_sum = {}
        for s, v in ttm.items():
            ind_sum[ind.get(s)] = ind_sum.get(ind.get(s), 0) + v
        for s, v in ttm.items():
            tot = ind_sum.get(ind.get(s), 0)
            if tot > 0:
                share = v / tot
                rows.append((pd_, s, "x_revenue_industry_share", round(share, 8)))
                ttm_hist.setdefault(s, {})[pd_] = share
                prior = next((p for p in reversed(panels_sorted[:pi]) if (pd_ - p).days >= 350), None)
                if prior is not None and prior in ttm_hist.get(s, {}):
                    rows.append((pd_, s, "x_revenue_share_mom", round(share - ttm_hist[s][prior], 8)))
        # C3:庫存/營收、毛利 percentile(per stock)
        for s in stk:
            iv = _latest_fin(inv.get(s, []), pd_, 1)
            fr4 = _latest_fin(frev.get(s, []), pd_, 4)
            if iv and len(fr4) == 4:
                rev4 = sum(v for _, v in fr4)
                if rev4 > 0:
                    ratio = iv[-1][1] / rev4
                    rows.append((pd_, s, "x_inventory_revenue_ratio", round(ratio, 8)))
                    # Δ vs ~4q 前(用 inv 前一筆 / 對應營收近似)
                    iv2 = _latest_fin([r for r in inv.get(s, []) if (pd_ - r[0]).days >= 350], pd_, 1)
                    fr4b = _latest_fin([r for r in frev.get(s, []) if (pd_ - r[0]).days >= 350], pd_, 4)
                    if iv2 and len(fr4b) == 4 and sum(v for _, v in fr4b) > 0:
                        rows.append((pd_, s, "x_inventory_ratio_chg", round(ratio - iv2[-1][1] / sum(v for _, v in fr4b), 8)))
            # 毛利率 percentile(自身歷史)
            grel = [(d, v) for d, v in gp.get(s, []) if v is not None and rl.financial_released(d, pd_)]
            rrel = {d: v for d, v in frev.get(s, []) if v is not None and rl.financial_released(d, pd_)}
            margins = [v / rrel[d] for d, v in grel if d in rrel and rrel[d] > 0]
            if len(margins) >= 8:
                cur_m = margins[-1]
                rows.append((pd_, s, "x_gross_margin_pctile", round(float(np.mean([1.0 if x <= cur_m else 0.0 for x in margins])), 6)))
        if rows:
            with db.transaction(conn) as cur:
                execute_values(cur, f"INSERT INTO {fc.FEATURE_TABLE} (panel_date, stock_id, feature, value) VALUES %s "
                               f"ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value", rows)
            written += len(rows)
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
            print(f"清基本面候選:{_clear(conn)} 列刪"); return
        with db.transaction(conn) as cur:
            panels = _asof_panels(cur)
        print(f"算 P5+C3 基本面候選(發布日 gate)… 寫入 {_compute(conn, panels):,} 值")
        cal = label_mod.full_calendar(conn)
        canon = [f for f in baseline.canonical_features(conn, panels) if f not in CANDS]
        print(f"\n══ 1. as-of 單因子 IC + HAC ══")
        print(f"{'candidate':28s} {'H':>3s} {'IC':>8s} {'HAC-t':>7s} {'勝率':>5s} {'n':>3s}")
        passed = False
        for f in CANDS:
            for h in hs:
                s = metrics.summarize(_ic(conn, panels, h, f, cal)); hac = metrics.effective_t_hac(_ic(conn, panels, h, f, cal))
                if s["mean_ic"] is None:
                    print(f"{f:28s} {h:>3d}  n/a"); continue
                if hac is not None and abs(hac) >= 2:
                    passed = True
                print(f"{f:28s} {h:>3d} {s['mean_ic']:>+8.4f} {(hac if hac is not None else float('nan')):>7.2f} {s['hit_rate']:>5.2f} {s['n_panels']:>3d}")
        print(f"\n══ 2. 共線(vs 既有估值/規模)══")
        col = fd.collinearity(conn, panels, baseline._asof_stocks(conn, panels[-1]),
                              CANDS + ["market_cap_log", "pe_ratio", "monthly_revenue_yoy"], threshold=0.5, asof=True)
        for a, b, r in col["high_pairs"][:8]:
            print(f"  {a} ~ {b}: {r:+.3f}")
        if not col["high_pairs"]:
            print("  (無 |r|≥0.5 對)")
        if passed:
            print(f"\n══ 3. 多 seed 多因子增量(有顯著者、續驗)══")
            for h in hs:
                base = {m: np.mean([baseline.run_ladder(conn, panels, h, None, feats=canon, seed=42+k, asof=True)[m]["mean_ic"] for k in range(args.seeds)]) for m in ("B2_ridge", "M1_gbdt")}
                add = {m: np.mean([baseline.run_ladder(conn, panels, h, None, feats=canon+CANDS, seed=42+k, asof=True)[m]["mean_ic"] for k in range(args.seeds)]) for m in ("B2_ridge", "M1_gbdt")}
                for m in ("B2_ridge", "M1_gbdt"):
                    print(f"  H={h:>3d} {m:10s} 生產 {base[m]:+.4f} → +基本面 {add[m]:+.4f}  Δ={add[m]-base[m]:+.4f}")
        else:
            print("\n→ 單因子 HAC 全 <2 → 不續多因子;不提拔(省算 #28)。")
        print("\n判讀:HAC|≥2| + 低共線 + 多因子增量正 → 提拔;否則 --clear。")


if __name__ == "__main__":
    main()

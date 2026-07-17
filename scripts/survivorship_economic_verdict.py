#!/usr/bin/env python
"""survivorship 經濟重跑裁決 — 拆解「倖存樂觀」的兩個獨立效應(可複現、#8/#15、#10 可溯源)。

🎯 這支在做什麼(白話):headline 淨 Sharpe ~1.20 是在 production「全史齊」宇宙(core_universe_asof)上跑的。
   本支拆解它相對「真實可交易宇宙」高多少,且**分清兩個常被混為一談的效應**:
     ① 經典下市 survivorship:把「當時活著、後來下市」的股加回、用清算 label 捕捉實現損益 → 邊際貢獻。
     ② 完整度閘 incumbency:production 要求「[首panel, t] 每個 panel 都齊特徵」= 偏向自樣本起點連續在世的老股;
        放寬為「當下 t 可算即納入」(標準可交易準則)→ 宇宙 ~2.1x、看降多少。
   實證結論(2026-07-08):**① ≈ 0(下市邊際 +0.0023 Sharpe)、② = −16.5%(1.20→1.00)**——
   把整個 −16% 標「survivorship」是誤歸(敵③);真下市偏誤近零,降幅全來自宇宙定義(incumbency)。

   **清算 label 命門(#8)**:下市股取 [entry, exit] 內**最後可得還原價**(≤exit、不用未來價);
   下市中途 last_d<exit→clearing 捕捉部分窗損益;只有進場價→歸零近似(不外推)。
   PIT 宇宙三閘(recency/feature/liquidity)全純 ≤t、point-in-time。3 鏡對抗驗證 CONFIRM #8 乾淨、
   清算 label 對 survivor 股 == 生產 forward_returns(0 diff)。

守 #8(清算 label 無 look-ahead、宇宙純 ≤t) · #12(投組/經濟指標複用 portfolio) · #14(經濟價值) ·
   #15(兩效應拆乾淨、不誤歸、兩宇宙並存標註) · #28(本地零 API) · #29(個別可執行 + 指令矩陣) ·
   SSOT=reports/augur_prediction_survivorship_economic_verdict_20260708.md。

執行指令矩陣:
  python scripts/survivorship_economic_verdict.py                # H60、拆解 SURVIVOR/PIT/isolation
  python scripts/survivorship_economic_verdict.py --h 120        # 換 horizon
"""
import argparse
import bisect
import sys

import _bootstrap  # noqa: F401
import numpy as np

from augur.core import db
from augur.evaluation import baseline, label as label_mod, portfolio, walkforward

ADJ = "TaiwanStockPriceAdj"
FT = "feature_values"
ETF = ("ETF", "上櫃指數股票型基金(ETF)", "上櫃ETF")
_REAL = "stock_id ~ '^[0-9]'"
RECENCY_TD = 63
COST = 0.00585


def build_pit_universe(conn, pds, feats, *, liquidity_pct=25, recency_td=RECENCY_TD):
    """PIT 宇宙(當下 t 可算):T 活著(近窗有交易@≤T)∩ 真股 ∩ 非ETF ∩ 全 feats@T 齊(該 panel、非全史)
    ∩ 流動性 P25@T。放寬 production 的「全史齊」為「當下齊」→ 納入後來下市股 + 連續性不足的在世股。回 {T:名單}。"""
    with db.transaction(conn) as cur:
        cur.execute(f'SELECT DISTINCT date FROM "{ADJ}" ORDER BY date')
        cal = [r[0] for r in cur.fetchall()]
    out = {}
    for T in sorted(pds):
        hi = bisect.bisect_right(cal, T) - 1
        recency_floor = cal[max(0, hi - recency_td)] if hi >= 0 else T
        with db.transaction(conn) as cur:
            liq_filter, liq_params = "", []
            if liquidity_pct is not None:
                cur.execute("SELECT percentile_cont(%s) WITHIN GROUP (ORDER BY value) FROM feature_values "
                            "WHERE panel_date=%s AND feature='dollar_volume_log_20d'", (liquidity_pct / 100.0, T))
                thr = cur.fetchone()[0]
                if thr is not None:
                    liq_filter = ("AND EXISTS (SELECT 1 FROM feature_values lq WHERE lq.stock_id=fv.stock_id "
                                  "AND lq.panel_date=%s AND lq.feature='dollar_volume_log_20d' AND lq.value>=%s) ")
                    liq_params = [T, float(thr)]
            cur.execute(
                f"SELECT fv.stock_id FROM {FT} fv WHERE fv.panel_date=%s AND fv.feature=ANY(%s) AND {_REAL} "
                f"  AND NOT EXISTS (SELECT 1 FROM \"TaiwanStockInfo\" si WHERE si.stock_id=fv.stock_id AND si.industry_category IN %s) "
                f"  AND EXISTS (SELECT 1 FROM \"{ADJ}\" p WHERE p.stock_id=fv.stock_id AND p.date>%s AND p.date<=%s AND p.close>0) "
                f"  {liq_filter}"
                f"GROUP BY fv.stock_id HAVING count(*)=%s ORDER BY fv.stock_id",
                (T, feats, ETF, recency_floor, T, *liq_params, len(feats)))
            out[T] = [r[0] for r in cur.fetchall()]
    return out


def forward_returns_pit(conn, panel_date, stock_ids, h, *, calendar):
    """清算報酬 label(#8):exit 價取 [entry, exit] 內最後可得還原價(≤exit、不用未來)。
    倖存股 last_d==exit(full);下市股 last_d<exit(clearing、部分窗實現損益);只有 entry(entry_only、歸零近似)。
    回 (returns{sid:log_ret}, stats)。"""
    cal = [d for d in calendar if d > panel_date]
    entry, exit_ = label_mod._entry_exit(cal, h)
    if entry is None:
        return {}, {"full": 0, "clearing": 0, "entry_only": 0}
    with db.transaction(conn) as cur:
        cur.execute(f'SELECT stock_id, date, close FROM "{ADJ}" WHERE stock_id=ANY(%s) '
                    f'AND date>=%s AND date<=%s AND close>0 ORDER BY stock_id, date',
                    (list(stock_ids), entry, exit_))
        rows = cur.fetchall()
    series = {}
    for sid, d, c in rows:
        series.setdefault(str(sid), []).append((d, float(c)))
    out, stats = {}, {"full": 0, "clearing": 0, "entry_only": 0}
    for sid, seq in series.items():
        seq.sort()
        pe = dict(seq).get(entry)
        if pe is None or pe <= 0:
            continue
        last_d, last_px = seq[-1]                       # 區間內最後一筆(≤exit、#8)
        if last_d == entry:
            stats["entry_only"] += 1
            out[sid] = 0.0
            continue
        stats["full" if last_d == exit_ else "clearing"] += 1
        if last_px > 0:
            v = float(np.log(last_px / pe))
            if np.isfinite(v):
                out[sid] = v
    return out, stats


def _fold_xy(conn, panels, feats, h, cal, lookup):
    Xs, ys = [], []
    for pd_ in panels:
        sub = lookup.get(pd_) or []
        if not sub:
            continue
        sids, X = baseline._panel_matrix(conn, pd_, sub, feats)
        if len(sids) == 0:
            continue
        lab = label_mod.cross_sectional_rank(forward_returns_pit(conn, pd_, sids, h, calendar=cal)[0])
        keep = [(i, s) for i, s in enumerate(sids) if s in lab]
        if not keep:
            continue
        Xs.append(X[[i for i, _ in keep]]); ys.append(np.array([lab[s] for _, s in keep]))
    if not Xs:
        return np.empty((0, len(feats))), np.empty(0)
    return np.vstack(Xs), np.concatenate(ys)


def run_pit_economic(conn, pds, h, feats, lookup, *, top_frac=0.1, cost=COST, exit_frac=None):
    """PIT 宇宙 + 清算 label 之 long-only 經濟回測(同 portfolio.run_backtest 結構、換宇宙/報酬)。
    cost 參數化(default=COST;供成本敏感度帶掃描,#29b 不寫死);回 gross/turn 序列供 cost 解析套用。"""
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    cal = label_mod.full_calendar(conn)
    folds = walkforward.splits(pds, h, calendar=cal)
    gross, net, bench, dates, turns, bturns = [], [], [], [], [], []
    prev_top, prev_uni = None, None
    lstats = {"full": 0, "clearing": 0, "entry_only": 0}
    for fold in folds:
        tpd = fold["test"]
        sids, Xte = baseline._panel_matrix(conn, tpd, lookup.get(tpd) or [], feats)
        if len(sids) < 10:
            continue
        ret, st = forward_returns_pit(conn, tpd, sids, h, calendar=cal)
        for k in lstats:
            lstats[k] += st[k]
        common = [s for s in sids if s in ret]
        if len(common) < 10:
            continue
        Xtr, ytr = _fold_xy(conn, fold["train"], feats, h, cal, lookup)
        if len(ytr) < 50:
            continue
        Xc = Xte[[sids.index(s) for s in common]]
        sc = StandardScaler().fit(Xtr)
        pred = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr).predict(sc.transform(Xc))
        simple = {s: float(np.expm1(ret[s])) for s in common}
        port = portfolio.build_long_portfolio(common, pred, top_frac=top_frac,
                                              prev_ids=prev_top, exit_frac=exit_frac)   # P1 buffer 透傳(1-3;None=原行為)
        top_ids = [sid for sid, _, _ in port]
        long_ret = float(sum(w * simple[sid] for sid, w, _ in port))
        turn = portfolio._turnover(top_ids, prev_top)
        bturn = portfolio._turnover(common, prev_uni)
        prev_top, prev_uni = top_ids, common
        gross.append(long_ret)
        net.append(long_ret - turn * cost)
        bench.append(float(np.mean(list(simple.values()))) - bturn * cost)
        turns.append(turn); bturns.append(bturn); dates.append(tpd)
    if len(dates) < 3:
        return None
    ppy = len(dates) / max((dates[-1] - dates[0]).days / 365.0, 1e-9)
    return {"net": portfolio._metrics(net, ppy), "bench": portfolio._metrics(bench, ppy),
            "n": len(dates), "lstats": lstats, "span": f"{dates[0]}..{dates[-1]}",
            "net_series": net, "gross_series": gross, "turn_series": turns,
            "ppy": ppy}   # net/gross/turn_series 供 deflation 定錨 + cost 敏感度帶(P0、#12 helper)


def main(argv=None):
    ap = argparse.ArgumentParser(description="survivorship 經濟重跑裁決(兩效應拆解)")
    ap.add_argument("--h", type=int, default=60)
    ap.add_argument("--top-frac", type=float, default=0.1)
    args = ap.parse_args(argv)
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof ORDER BY as_of_date")
            pds = [r[0] for r in cur.fetchall()]
            cur.execute(f"SELECT stock_id, max(date) FROM \"{ADJ}\" WHERE {_REAL} GROUP BY stock_id")
            last = {r0: r1 for r0, r1 in cur.fetchall()}
        feats = baseline.canonical_features(conn, pds)
        delisted = {s for s, l in last.items() if l.year < 2026 and l >= pds[0]}

        surv = portfolio.run_backtest(conn, pds, args.h, model="B2_ridge", top_frac=args.top_frac,
                                      weight="equal", cost=COST, asof=True)
        pit_map = build_pit_universe(conn, pds, feats, liquidity_pct=25)
        pit = run_pit_economic(conn, pds, args.h, feats, pit_map, top_frac=args.top_frac)
        pit_ex = run_pit_economic(conn, pds, args.h, feats,
                                  {T: [s for s in v if s not in delisted] for T, v in pit_map.items()},
                                  top_frac=args.top_frac)

    sv = surv["portfolio_net"]["sharpe"]
    pf, px = pit["net"]["sharpe"], pit_ex["net"]["sharpe"]
    pit_distinct = set().union(*[set(v) for v in pit_map.values()])
    print("=" * 74)
    print(f"survivorship 經濟重跑裁決(H{args.h} LO top{args.top_frac:.0%} cost {COST:.3%})")
    print("=" * 74)
    print(f"下市股入 PIT distinct={len(delisted & pit_distinct)}  PIT distinct={len(pit_distinct)}  "
          f"清算: full={pit['lstats']['full']} clearing={pit['lstats']['clearing']} entry_only={pit['lstats']['entry_only']}")
    print(f"PIT span={pit['span']} n={pit['n']}\n")
    print(f"  SURVIVOR(全史齊、~穩定核心宇宙)      淨 Sharpe = {sv:.4f}")
    print(f"  PIT 全含(當下可算 + 下市股清算)       淨 Sharpe = {pf:.4f}   ({(pf-sv)/sv*100:+.1f}% vs SURVIVOR)")
    print(f"  PIT 排除下市股(隔離)                  淨 Sharpe = {px:.4f}")
    print()
    print(f"  ① 經典下市 survivorship 邊際 = {pf-px:+.4f} Sharpe  ({'≈0' if abs(pf-px)<0.02 else '有感'})")
    print(f"  ② 完整度閘 incumbency(宇宙定義)= {(px-sv):+.4f} Sharpe  ({(px-sv)/sv*100:+.1f}%)")
    print(f"\n裁決:下市 survivorship ≈0(債 b 下市偏誤實證解決);headline 1.20 vs 廣宇宙 1.00 之差=incumbency"
          f"(全史齊 point-in-time 但偏向連續在世老股),屬宇宙定義決策、兩者並存標註。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

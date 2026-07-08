#!/usr/bin/env python
"""持續再驗證 harness — 給定 as-of 上界,重跑 STAGE B/C/D 驗證、寫 revalidation_ledger(部署階段 D5)。

🎯 這支在做什麼(白話):研究 A'→B→C→D 已過(as-of IC HAC-t≫2 / 經濟價值 H60-H120 long-only 淨
   Sharpe~1.2 / H120 風險調整最佳但**近期 n=8 小樣本不定論**)。隨真實資料累積(as-of 日前推)、n 變大,
   H120 近期優勢才能定論。本 harness 把「重跑 B/C/D + 記錄隨時間」機械化:
   - **STAGE B**:as-of walk-forward rank IC + HAC-t(H20/60/120;Ridge 確定性,#11 GBDT 多 seed 中位)。
   - **STAGE C**:經濟價值 net Sharpe/Calmar/MaxDD(H60/120 long-only、扣成本 0.585%、對比等權基準)。
   - **STAGE D**:H120 vs H60 風險調整 + 兩樣本期(2014起/2021起)——**追蹤每 horizon 的 n_periods 隨
     as-of 前推如何成長、H120 近期 n 何時 ≥ 定論門檻(預設 20)可定論**。
   每 (stage, horizon, model, config, metric) 逐列寫 revalidation_ledger(機械 N + 指標,#15 可 trace)。

   **全複用 evaluation SSOT helper**(baseline/label/walkforward/metrics/portfolio),不改判準、不重造(#12);
   as-of 上界前推靠參數(--as-of),as-of=True 逐 panel point-in-time 消 survivorship(#8);純本地 DB 計算、
   不放量 API、不 commit、可逆(#28)。冪等:同 (run tag) 重跑覆寫;resume:--skip-existing 跳已寫入之 as-of。

守 #8(as-of/embargo 口徑同既有、A'-3 h+62td 保證下界,不放寬)· #11(GBDT 多 seed 統計、IC 用 HAC-t)·
   #12(SSOT helper)· #14(經濟價值非 IC)· #15(誠實、與 STAGE B/C/D 報告對齊)· #28(本地零 usage)·
   CLAUDE #29(個別可執行 + 指令矩陣 + 冪等 + resume)。SSOT=reports/augur_prediction_deployment_plan_20260707.md §8 D5。

執行指令矩陣:
  python scripts/revalidate.py                          # 印指令矩陣 + 現況(as-of 選項、ledger 現況);不跑驗證
  python scripts/revalidate.py --run                    # 以最新可用 as-of(latest panel)跑一輪 B/C/D、寫 ledger
  python scripts/revalidate.py --run --as-of 2026-05-31 # 指定 as-of 上界(不含其後 panel)跑一輪
  python scripts/revalidate.py --run --stages B         # 只跑 STAGE B(逗號分隔子集,如 B,C)
  python scripts/revalidate.py --run --dry-run          # 跑驗證、印結果,但**不寫 ledger**(對數用)
  python scripts/revalidate.py --run --skip-existing    # resume:該 as-of 已在 ledger 有列則整輪跳過
  python scripts/revalidate.py --track                  # 唯讀:印 n_periods 隨 as-of 前推之成長 + H120 定論追蹤
  python scripts/revalidate.py --track --verdict-n 20   # 追蹤時把 H120 定論門檻設為 n≥20(預設 20)
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path

import numpy as np

from augur.core import db
from augur.evaluation import baseline, deflation, metrics, portfolio
from augur.evaluation import label as label_mod
from augur.evaluation import walkforward
from migrate_trial_ledger_ddl import BACKFILL as _TRIAL_BACKFILL   # 執行序:refresh trial_ledger 供 N 機械

# ── 口徑常數(SSOT 同 STAGE B/C/D 報告,不改判準)──────────────────────────────
COST_TW = 0.00585        # 台股來回:手續費 2×0.1425% + 證交稅 0.3% ≈ 0.585%(STAGE C/D 同)
TOP_FRAC = 0.1           # top10%(STAGE C/D 同)
GBDT_SEEDS = (42, 43, 44)  # GBDT 多 seed 取中位(#11);Ridge 確定性單跑
B_HORIZONS = (20, 60, 120)   # STAGE B as-of IC 之 horizon
CD_HORIZONS = (60, 120)      # STAGE C/D 經濟價值之 horizon(H20 已判死、非追蹤重點)
SINCE_2014 = "2014-01-01"    # 全期(對齊 core_universe_asof 覆蓋)
SINCE_2021 = "2021-01-01"    # 近期(H120 小樣本 caveat 之樣本期)
VERDICT_N_DEFAULT = 20       # H120 近期 n ≥ 此 → 視為足以定論(可 --verdict-n 調)


# ── panel 取得(受 as-of 上界約束)───────────────────────────────────────────
def asof_panels(conn, as_of):
    """core_universe_asof 之 as_of_date(≤ as_of 上界)——STAGE B as-of 宇宙口徑。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof WHERE as_of_date <= %s ORDER BY as_of_date",
                    (as_of,))
        return [r[0] for r in cur.fetchall()]


def asof_union_stocks(conn, as_of):
    """as_of_date ≤ 上界之股票聯集(STAGE B pan-hist 對照宇宙)。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT stock_id FROM core_universe_asof WHERE as_of_date <= %s", (as_of,))
        return [str(r[0]) for r in cur.fetchall()]


def feature_panels_since(conn, since, as_of):
    """feature_values 之 panel_date(since ≤ p ≤ as_of 上界)——STAGE C/D 經濟價值口徑。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT panel_date FROM feature_values WHERE panel_date>=%s AND panel_date<=%s ORDER BY panel_date",
                    (since, as_of))
        return [r[0] for r in cur.fetchall()]


def latest_available_asof(conn):
    """最新可用 as-of = min(max core_universe_asof.as_of_date, max feature_values.panel_date)——兩表都要有。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT max(as_of_date) FROM core_universe_asof")
        a = cur.fetchone()[0]
        cur.execute("SELECT max(panel_date) FROM feature_values")
        f = cur.fetchone()[0]
    return min(a, f) if a and f else (a or f)


def _nonoverlap(panels, h):
    """稀釋成不重疊持有(rebalance 間距≈持有期):need≈h*1.45*0.9 日曆日(STAGE C/D、run_economic_eval 同口徑)。"""
    need = h * 1.45 * 0.9
    kept, last = [], None
    for p in sorted(panels):
        if last is None or (p - last).days >= need:
            kept.append(p)
            last = p
    return kept


# ── STAGE B:as-of walk-forward rank IC + HAC-t(複用 stage_b_promotion driver 之折邏輯)──
def _shuffle_labels(lab, rng):
    keys = list(lab.keys())
    vals = list(lab.values())
    rng.shuffle(vals)
    return dict(zip(keys, vals))


def _b_ridge_ic(conn, panel_dates, h, stocks, *, feats, seed, asof, shuffle=False):
    """B2 Ridge purged walk-forward as-of/pan-hist rank IC(可選 label shuffle 負對照)。
    複用 baseline._asof_stocks/_panel_matrix/label/walkforward/metrics SSOT helper,折邏輯同 stage_b driver。
    回 (ic_by_panel dict, n_folds)。"""
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler

    cal = label_mod.full_calendar(conn)
    folds = walkforward.splits(panel_dates, h, calendar=cal)   # A'-3 保證下界 h+62td(#8)
    rng = np.random.default_rng(seed)
    ic, n_used = {}, 0
    for fold in folds:
        test_pd = fold["test"]
        test_stocks = baseline._asof_stocks(conn, test_pd) if asof else stocks
        ts_sids, Xte = baseline._panel_matrix(conn, test_pd, test_stocks, feats)
        if len(ts_sids) < 5:
            continue
        lab = label_mod.labels(conn, test_pd, ts_sids, h, calendar=cal)
        keep = [i for i, s in enumerate(ts_sids) if s in lab]
        if len(keep) < 5:
            continue
        Xte, ts_sids = Xte[keep], [ts_sids[i] for i in keep]
        ylab = {s: lab[s] for s in ts_sids}
        if shuffle:
            ylab = _shuffle_labels(ylab, rng)
        Xs, ys = [], []
        for pd_ in fold["train"]:
            sub = baseline._asof_stocks(conn, pd_) if asof else stocks
            sids, X = baseline._panel_matrix(conn, pd_, sub, feats)
            if len(sids) == 0:
                continue
            l2 = label_mod.labels(conn, pd_, sids, h, calendar=cal)
            k2 = [(i, s) for i, s in enumerate(sids) if s in l2]
            if not k2:
                continue
            idx = [i for i, _ in k2]
            yv = np.array([l2[s] for _, s in k2])
            if shuffle:
                rng.shuffle(yv)
            Xs.append(X[idx])
            ys.append(yv)
        if not Xs:
            continue
        Xtr, ytr = np.vstack(Xs), np.concatenate(ys)
        if len(ytr) < 50:
            continue
        sc = StandardScaler().fit(Xtr)
        rdg = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr)
        val = metrics.rank_ic(dict(zip(ts_sids, rdg.predict(sc.transform(Xte)))), ylab)
        if val is not None:
            ic[test_pd] = val
            n_used += 1
    return ic, n_used


def stage_b(conn, panels, union, feats, *, horizons=B_HORIZONS):
    """STAGE B:每 horizon 之 as-of IC/HAC-t、pan-hist IC、shuffle IC(負對照)。
    回 list of ledger rows(dict);Ridge 確定性 → seed 恆等,單跑即可(shuffle 因 RNG 打亂 label 才隨 seed 變)。"""
    rows = []
    for h in horizons:
        if h >= walkforward._H_FORBIDDEN:   # H≥252 walkforward gate raise、跳過(不觸 exception)
            continue
        # as-of IC(Ridge 確定性、單 seed)
        asof_ic, n = _b_ridge_ic(conn, panels, h, None, feats=feats, seed=42, asof=True)
        s = metrics.summarize(asof_ic)
        hac = metrics.effective_t_hac(asof_ic)
        rows.append(dict(stage="B", horizon=h, model="B2_ridge", config="asof_ic",
                         metric_name="mean_ic", metric_value=s["mean_ic"], n_periods=n, hac_t=hac,
                         note=f"hit={s['hit_rate']}"))
        # pan-hist IC 對照(B3 survivorship 旗標)
        pan_ic, np_ = _b_ridge_ic(conn, panels, h, union, feats=feats, seed=42, asof=False)
        sp = metrics.summarize(pan_ic)
        rows.append(dict(stage="B", horizon=h, model="B2_ridge", config="panhist_ic",
                         metric_name="mean_ic", metric_value=sp["mean_ic"], n_periods=np_,
                         hac_t=metrics.effective_t_hac(pan_ic), note="B3 as-of≤pan-hist 旗標對照"))
        # shuffle 負對照(B2 sanity;RNG 打亂 → 多 seed 取中位)
        sh_ic, sh_hac = [], []
        for sd in GBDT_SEEDS:
            si, _ = _b_ridge_ic(conn, panels, h, None, feats=feats, seed=sd, asof=True, shuffle=True)
            ss = metrics.summarize(si)
            sh_ic.append(ss["mean_ic"])
            sh_hac.append(metrics.effective_t_hac(si))
        rows.append(dict(stage="B", horizon=h, model="B2_ridge", config="shuffle_ic",
                         metric_name="mean_ic",
                         metric_value=float(np.median([x for x in sh_ic if x is not None])) if any(x is not None for x in sh_ic) else None,
                         n_periods=n,
                         hac_t=float(np.median([x for x in sh_hac if x is not None])) if any(x is not None for x in sh_hac) else None,
                         note="B2 sanity 負對照(IC≈0 應)"))
    return rows


# ── STAGE C/D:經濟價值 net Sharpe/Calmar/MaxDD(複用 portfolio.run_backtest)──
def _backtest_cell(conn, panels, h, *, model, long_short, short_borrow):
    """單 cell 回測:Ridge 單跑、GBDT 多 seed 取中位;回 (dict of metrics, n_periods) 或 (None, 0)。"""
    m = "B2_ridge" if model == "ridge" else "M1_gbdt"
    seeds = (42,) if model == "ridge" else GBDT_SEEDS
    sh, ca, dd, bench_sh, r0 = [], [], [], None, None
    for sd in seeds:
        r = portfolio.run_backtest(conn, panels, h, model=m, top_frac=TOP_FRAC,
                                   long_short=long_short, seed=sd, asof=True,
                                   cost=COST_TW, short_borrow=short_borrow)
        if not r:
            continue
        r0 = r
        pn = r["portfolio_net"]
        sh.append(pn.get("sharpe"))
        ca.append(pn.get("calmar"))
        dd.append(pn.get("max_drawdown"))
    if not r0:
        return None, 0
    bench_sh = r0["benchmark_net"].get("sharpe")

    def _med(vals):
        v = [x for x in vals if x is not None]
        return float(np.median(v)) if v else None

    return ({"net_sharpe": _med(sh), "net_calmar": _med(ca), "net_maxdd": _med(dd),
             "bench_sharpe": bench_sh, "turnover": r0.get("avg_turnover"),
             "net_series": r0.get("net_series"), "ppy": r0.get("ppy")},   # 供 P1 deflation(ridge 確定性;gbdt 為代表 seed)
            r0["portfolio_net"].get("n"))


def stage_cd(conn, as_of, *, horizons=CD_HORIZONS):
    """STAGE C(經濟價值 long-only 淨 Sharpe/Calmar/MaxDD)+ D(H120 vs H60、兩樣本期、放空成本)。
    矩陣:since{2014,2021} × H{60,120} × {ridge LO, ridge LS, ridge LS+borrow2%, gbdt LO}。
    回 (rows, cell_series);cell_series[(stage,horizon,model,config)]=(net_series, ppy) 供 P1 deflation 整合。"""
    rows, cell_series = [], {}
    cells = [("ridge", "LO", False, 0.0), ("ridge", "LS", True, 0.0),
             ("ridge", "LS+borrow2%", True, 0.02), ("gbdt", "LO", False, 0.0)]
    for since in (SINCE_2014, SINCE_2021):
        allp = feature_panels_since(conn, since, as_of)
        for h in horizons:
            panels = _nonoverlap(allp, h)
            if len(panels) < 3:
                continue
            for model, tag, ls, sb in cells:
                met, n = _backtest_cell(conn, panels, h, model=model, long_short=ls, short_borrow=sb)
                if met is None:
                    continue
                # C 核心 = STAGE C 報告之經濟價值成立 cell(2014起 ridge H60 long-only);
                # H120 long-only(horizon 延伸)與 long-short/近期/GBDT 皆歸 D 穩健性延伸
                stage = "C" if (since == SINCE_2014 and model == "ridge" and tag == "LO" and h == 60) else "D"
                config = f"{tag}|since{since[:4]}"
                base = dict(stage=stage, horizon=h, model=model, config=config,
                            n_periods=n, hac_t=None)
                rows.append({**base, "metric_name": "net_sharpe", "metric_value": met["net_sharpe"],
                             "note": f"bench_sharpe={met['bench_sharpe']} turnover={met['turnover']}"})
                rows.append({**base, "metric_name": "net_calmar", "metric_value": met["net_calmar"], "note": None})
                rows.append({**base, "metric_name": "net_maxdd", "metric_value": met["net_maxdd"], "note": None})
                rows.append({**base, "metric_name": "bench_sharpe", "metric_value": met["bench_sharpe"], "note": None})
                if met.get("net_series"):   # 供 deflation(long-only 才是部署口徑;LS/borrow 亦記供對照)
                    cell_series[(stage, h, model, config)] = (met["net_series"], met["ppy"])
    return rows, cell_series


# ── ledger 寫入 ────────────────────────────────────────────────────────────
def write_ledger(conn, as_of, rows):
    """逐列寫 revalidation_ledger(單一 run_at、同 as_of);冪等由 --skip-existing 於呼叫端把關。"""
    with db.transaction(conn) as cur:
        for r in rows:
            cur.execute(
                "INSERT INTO revalidation_ledger "
                "(as_of_date, stage, horizon, model, config, metric_name, metric_value, n_periods, hac_t, note) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (as_of, r["stage"], r["horizon"], r["model"], r["config"],
                 r["metric_name"], r["metric_value"], r["n_periods"], r["hac_t"], r.get("note")))
    return len(rows)


def asof_already_run(conn, as_of):
    with db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM revalidation_ledger WHERE as_of_date=%s", (as_of,))
        return cur.fetchone()[0] > 0


# ── P1:deflation 整合(每 cell 走 #12 共用 helper 算 DSR)──────────────────────
def refresh_trial_ledger(conn):
    """執行序命門:寫 revalidation_ledger 之 net_sharpe 後 refresh trial_ledger,使 DSR 之 N 由此機械得出
    (禁人手,SOP §6 G7)。trial_ledger UNIQUE 鍵不含 as_of + ON CONFLICT UPDATE → 同 config 重跑不增 N
    (N 反身性已 schema 強制)、只更新最新 net_sharpe。"""
    with db.transaction(conn) as cur:
        cur.execute(_TRIAL_BACKFILL)


def deflation_rows(conn, cell_series):
    """每經濟 cell 之 deflated 地板 → dsr/deflated_sharpe_ann 之 ledger rows(#12 共用 deflation helper)。
    **須在 refresh_trial_ledger 之後呼叫**(N 含本輪 cell)。N/trials 由 trial_ledger 機械;ppy_by_h 取本輪
    cell 自身 ppy(逐 horizon)。DSR 屬軌A 標註(<95%=薄 edge 常態、非判停)。ridge 確定性;gbdt 為代表 seed 序列。"""
    with db.transaction(conn) as cur:
        cur.execute("SELECT horizon, metric_value FROM trial_ledger WHERE metric_name='net_sharpe'")
        trials = cur.fetchall()
    ppy_by_h = {}
    for (_stage, h, _model, _cfg), (_series, ppy) in cell_series.items():
        if ppy and h not in ppy_by_h:
            ppy_by_h[h] = ppy
    trials_pp = deflation.trials_per_period(trials, ppy_by_h)
    n_trials = len(trials_pp)
    rows = []
    for (stage, h, model, cfg), (series, ppy) in cell_series.items():
        d = deflation.deflated_floor(series, ppy, trials_pp, n_trials)
        if d["dsr"] is None:
            continue
        base = dict(stage=stage, horizon=h, model=model, config=cfg, n_periods=d["T"], hac_t=None)
        rows.append({**base, "metric_name": "dsr", "metric_value": d["dsr"],
                     "note": f"per-period DSR N={n_trials}(軌A 標註、<95%=薄edge常態非判停);deflated_ann={d['deflated_ann']:.3f}"})
        rows.append({**base, "metric_name": "deflated_sharpe_ann", "metric_value": d["deflated_ann"], "note": None})
    return rows


# ── --track:n 成長 + H120 定論追蹤(唯讀)──────────────────────────────────
def track(conn, verdict_n):
    """印每 horizon 之 n_periods 隨 as_of_date 前推如何成長、H120 近期 n 何時 ≥ verdict_n 可定論。"""
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT as_of_date, stage, horizon, config, n_periods "
            "FROM revalidation_ledger "
            "WHERE metric_name='net_sharpe' AND config LIKE 'LO|%' "
            "ORDER BY horizon, config, as_of_date")
        rows = cur.fetchall()
    if not rows:
        print("(ledger 尚無 net_sharpe long-only 列;先 --run)")
        return
    print("── n_periods 隨 as-of 前推之成長(long-only 淨 Sharpe cell)──")
    print(f"{'horizon':>7} {'config':>14} {'as_of':>12} {'n':>4} {'定論?':>6}")
    for as_of, stage, h, cfg, n in rows:
        verdict = "✓ 足" if (n is not None and n >= verdict_n) else "小樣本"
        print(f"{h:>7} {cfg:>14} {str(as_of):>12} {n if n is not None else '-':>4} {verdict:>6}")
    # H120 近期定論狀態摘要
    print(f"\n── H120 近期(since2021)定論門檻 n≥{verdict_n} 狀態 ──")
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT as_of_date, n_periods FROM revalidation_ledger "
            "WHERE metric_name='net_sharpe' AND horizon=120 AND config='LO|since2021' "
            "ORDER BY as_of_date")
        h120 = cur.fetchall()
    if not h120:
        print("  (尚無 H120 since2021 long-only 列)")
    else:
        for as_of, n in h120:
            state = "✅ 可定論" if (n is not None and n >= verdict_n) else f"⚠ n={n} < {verdict_n}(仍小樣本、待資料累積)"
            print(f"  as_of {as_of}: n={n} → {state}")


# ── 現況(無 --run/--track 時)──────────────────────────────────────────────
def show_status(conn):
    latest = latest_available_asof(conn)
    with db.transaction(conn) as cur:
        cur.execute("SELECT count(*), count(DISTINCT as_of_date) FROM revalidation_ledger")
        nrows, nasof = cur.fetchone()
        cur.execute("SELECT max(as_of_date) FROM core_universe_asof")
        max_asof = cur.fetchone()[0]
    print(__doc__.split("執行指令矩陣:")[1] if "執行指令矩陣:" in __doc__ else "")
    print("── 現況 ──")
    print(f"  最新可用 as-of(latest panel):{latest}")
    print(f"  core_universe_asof 最大 as_of_date:{max_asof}")
    print(f"  revalidation_ledger:{nrows} 列 / {nasof} 個 as-of")
    print("\n  → 跑一輪:python scripts/revalidate.py --run")
    print("  → 追蹤 n 成長:python scripts/revalidate.py --track")


def main(argv=None):
    ap = argparse.ArgumentParser(description="持續再驗證 harness(D5):重跑 B/C/D、寫 revalidation_ledger")
    ap.add_argument("--run", action="store_true", help="跑一輪 B/C/D 驗證、寫 ledger")
    ap.add_argument("--as-of", dest="as_of", default=None, help="as-of 上界(YYYY-MM-DD;預設=最新可用 panel)")
    ap.add_argument("--stages", default="B,C,D", help="要跑之 stage 子集(逗號分隔,如 B 或 B,C;C/D 同一回測)")
    ap.add_argument("--dry-run", action="store_true", help="跑驗證、印結果,但不寫 ledger")
    ap.add_argument("--skip-existing", action="store_true", help="resume:該 as-of 已在 ledger 有列則整輪跳過")
    ap.add_argument("--track", action="store_true", help="唯讀:印 n_periods 隨 as-of 前推之成長 + H120 定論追蹤")
    ap.add_argument("--verdict-n", type=int, default=VERDICT_N_DEFAULT, help=f"H120 定論門檻 n(預設 {VERDICT_N_DEFAULT})")
    args = ap.parse_args(argv)

    with db.connect() as conn:
        if args.track:
            track(conn, args.verdict_n)
            return 0
        if not args.run:
            show_status(conn)
            return 0

        as_of = args.as_of or str(latest_available_asof(conn))
        stages = {s.strip().upper() for s in args.stages.split(",") if s.strip()}
        cd_wanted = bool({"C", "D"} & stages)

        if args.skip_existing and asof_already_run(conn, as_of):
            print(f"[skip] as-of {as_of} 已在 ledger 有列(--skip-existing)。")
            return 0

        panels = asof_panels(conn, as_of)
        print(f"as-of 上界: {as_of}  |  as-of panels: {len(panels)} ({panels[0]}..{panels[-1]})")
        union = asof_union_stocks(conn, as_of)
        feats = baseline.canonical_features(conn, panels)
        print(f"pan-hist 宇宙: {len(union)} 股  |  canonical 特徵: {len(feats)}")
        print(f"stages={sorted(stages)}  cost={COST_TW:.3%}  top={TOP_FRAC:.0%}  GBDT seeds={GBDT_SEEDS}")
        print()

        all_rows = []
        if "B" in stages:
            print("==================== STAGE B (as-of IC + HAC-t) ====================")
            b_rows = stage_b(conn, panels, union, feats)
            for r in b_rows:
                ht = f"{r['hac_t']:+.2f}" if r["hac_t"] is not None else "  n/a"
                mv = f"{r['metric_value']:+.4f}" if r["metric_value"] is not None else "   n/a"
                print(f"  H{r['horizon']:>3} {r['config']:>12} IC={mv} HAC_t={ht} n={r['n_periods']}")
            all_rows += b_rows
            print()
        cell_series = {}
        if cd_wanted:
            print("==================== STAGE C/D (經濟價值) ====================")
            cd_rows, cell_series = stage_cd(conn, as_of)
            # 印 net_sharpe 主表(每 cell 一列)
            for r in cd_rows:
                if r["metric_name"] != "net_sharpe":
                    continue
                mv = f"{r['metric_value']:+.3f}" if r["metric_value"] is not None else "  n/a"
                print(f"  [{r['stage']}] H{r['horizon']:>3} {r['config']:>16} netSharpe={mv} n={r['n_periods']}  ({r['note']})")
            all_rows += cd_rows
            print()

        if args.dry_run:
            # dry-run 也算 DSR(不 refresh、用現況 trial_ledger N)、印不寫
            dsr_rows = deflation_rows(conn, cell_series) if cell_series else []
            for r in dsr_rows:
                if r["metric_name"] == "dsr":
                    print(f"  [deflation] {r['config']:>16} H{r['horizon']:>3} DSR={r['metric_value']:.4f} "
                          f"({'PASS' if r['metric_value']>=0.95 else 'FAIL'}≥95%、軌A 標註)")
            print(f"[dry-run] 不寫 ledger;共 {len(all_rows)+len(dsr_rows)} 列(含 {len(dsr_rows)} deflation)。")
        else:
            stages_written = sorted({r["stage"] for r in all_rows})
            with db.transaction(conn) as cur:   # 冪等(#6):重跑取代同 (as_of, stage) 之舊列、非累積重複
                cur.execute("DELETE FROM revalidation_ledger WHERE as_of_date=%s AND stage = ANY(%s)",
                            (as_of, stages_written))
            n = write_ledger(conn, as_of, all_rows)
            print(f"✓ 寫入 revalidation_ledger:{n} 列(as-of {as_of};冪等取代 stage {stages_written})。")
            # 執行序命門(#12/SOP G7):寫 net_sharpe → refresh trial_ledger → 讀 N → 算 DSR → 寫 dsr 列
            if cell_series:
                refresh_trial_ledger(conn)
                dsr_rows = deflation_rows(conn, cell_series)
                nd = write_ledger(conn, as_of, dsr_rows)
                print(f"✓ deflation 整合:refresh trial_ledger + 寫 {nd} 列 dsr/deflated(#12 helper、N 由 trial_ledger 機械)。")
        return 0


if __name__ == "__main__":
    sys.exit(main())

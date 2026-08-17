#!/usr/bin/env python
"""E4 特徵漏斗 — 一次一支、隔離表、死即停。

🎯 這支在做什麼（白話）：對 Steward 點名的一支既有欄，走 07-17 同尺漏斗
   (0)預診 → (1)只寫 staging → (2)HAC IC → (3)去相關 → (4)Ridge IC 增量 →
   (5)才准 #14。不過即停。不改 prodset、不寫 feature_values、不付 N、不 evaluate。

對齊 E4-feat-go | isolation-table。

守 #8 · #11（HAC lag=2、禁 iid）· #12 · #14（IC≠可交易）· #15（死即停、不清別人的 staging）。

執行指令矩陣:
  python scripts/run_econ_e4_feat_funnel.py --candidate range_mean_20d
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import date

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

import _bootstrap  # noqa: F401
from augur.audit import feature_candidate as fc
from augur.core import db
from augur.core.prodset_contract import load_active_features
from augur.evaluation import baseline, metrics, portfolio, walkforward
from augur.evaluation import label as label_mod

H_DEFAULT = 60
UNTIL_DEFAULT = date(2026, 4, 30)
SINCE_2021 = date(2021, 1, 1)
SINCE_2014 = date(2014, 1, 1)
HAC_LAG = 2
RHO_MAX = 0.6
HAC_MIN = 2.0
SIGN_MIN = 0.60
MIN_CROSS = 10
DSHARPE_MIN = 0.05
MAXDD_TOL = 0.005
COST = 0.00585
TOP = 0.1
SEED = 42
PROD_TABLE = "feature_values"


def _nonoverlap(panels, h):
    if not panels:
        return []
    need = h * 1.45 * 0.9
    out = [panels[0]]
    for p in panels[1:]:
        if (p - out[-1]).days >= need:
            out.append(p)
    return out


def _panel_hash(panels) -> str:
    return hashlib.sha256(",".join(str(p) for p in panels).encode()).hexdigest()[:16]


def _load_wide(conn, panels, feats):
    wide = {}
    with db.transaction(conn) as cur:
        for pd_ in panels:
            cur.execute(
                "SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s",
                (pd_,),
            )
            stocks = {str(r[0]) for r in cur.fetchall()}
            cur.execute(
                f"SELECT stock_id, feature, value FROM {PROD_TABLE} "
                "WHERE panel_date=%s AND feature = ANY(%s)",
                (pd_, list(feats)),
            )
            by = {}
            for sid, f, v in cur.fetchall():
                sid = str(sid)
                if sid not in stocks:
                    continue
                by.setdefault(sid, {})[f] = float(v)
            wide[pd_] = by
    return wide


def _load_labels(conn, panels, h, cal, wide):
    labs = {}
    for pd_ in panels:
        sids = list(wide.get(pd_) or {})
        labs[pd_] = label_mod.labels(conn, pd_, sids, h, calendar=cal) if sids else {}
    return labs


def _xy(by, lab, feats):
    sids, X, y = [], [], []
    for sid, fv in by.items():
        if sid not in lab:
            continue
        if any(f not in fv for f in feats):
            continue
        sids.append(sid)
        X.append([fv[f] for f in feats])
        y.append(lab[sid])
    if len(sids) < MIN_CROSS:
        return None
    return np.asarray(X, dtype=float), np.asarray(y, dtype=float), sids


def _ridge_ic_series(folds, wide, labs, feats):
    out = {}
    for fold in folds:
        te = _xy(wide.get(fold["test"]) or {}, labs.get(fold["test"]) or {}, feats)
        if te is None:
            continue
        Xte, yte, _ = te
        chunks_x, chunks_y = [], []
        for tpd in fold["train"]:
            tr = _xy(wide.get(tpd) or {}, labs.get(tpd) or {}, feats)
            if tr is None:
                continue
            chunks_x.append(tr[0])
            chunks_y.append(tr[1])
        if not chunks_x:
            continue
        Xtr = np.vstack(chunks_x)
        ytr = np.concatenate(chunks_y)
        if len(ytr) < 50:
            continue
        sc = StandardScaler().fit(Xtr)
        pred = Ridge(alpha=1.0).fit(sc.transform(Xtr), ytr).predict(sc.transform(Xte))
        ic = metrics._spearman(pred.tolist(), yte.tolist())
        if ic is not None:
            out[fold["test"]] = ic
    return out


def _median_abs_rho(wide, a, b, panels):
    xs = []
    for pd_ in panels:
        by = wide.get(pd_) or {}
        both = [fv for fv in by.values() if a in fv and b in fv]
        if len(both) < MIN_CROSS:
            continue
        r = metrics._spearman([fv[a] for fv in both], [fv[b] for fv in both])
        if r is not None:
            xs.append(abs(r))
    return float(np.median(xs)) if xs else None


def _copy_to_staging(conn, cand, since, until):
    fc.ensure_candidate_table(conn)
    with db.transaction(conn) as cur:
        cur.execute(
            f"INSERT INTO {fc.FEATURE_TABLE} (panel_date, stock_id, feature, value) "
            f"SELECT fv.panel_date, fv.stock_id, fv.feature, fv.value "
            f"FROM {PROD_TABLE} fv "
            f"JOIN core_universe_asof a "
            f"  ON a.as_of_date = fv.panel_date AND a.stock_id::text = fv.stock_id::text "
            f"WHERE fv.feature=%s AND fv.panel_date>=%s AND fv.panel_date<=%s "
            f"ON CONFLICT (panel_date, stock_id, feature) DO UPDATE SET value=EXCLUDED.value",
            (cand, since, until),
        )
        n = cur.rowcount
        cur.execute(
            f"SELECT count(*) FROM {fc.FEATURE_TABLE} WHERE feature=%s",
            (cand,),
        )
        kept = cur.fetchone()[0]
    return n, kept


def _clear_staging_feat(conn, cand):
    return fc.clear_candidates(conn, features=[cand])


def _econ_cell(conn, panels, h, feats):
    raw = portfolio.run_backtest(
        conn, panels, h, feats=feats, model="B2_ridge", top_frac=TOP,
        weight="equal", cost=COST, asof=True, seed=SEED,
    )
    if not raw or not raw.get("portfolio_net"):
        return None
    pn, bn = raw["portfolio_net"], raw.get("benchmark_net") or {}
    return {
        "n": raw.get("n_periods"),
        "net_sharpe": pn.get("sharpe"),
        "bench_sharpe": (bn or {}).get("sharpe"),
        "max_drawdown": pn.get("max_drawdown"),
        "calmar": pn.get("calmar"),
        "cagr": pn.get("cagr"),
    }


def run(*, cand: str, until: date, h: int) -> int:
    t0 = time.time()
    verdict = "pending"
    died_at = None
    payload = {"candidate": cand, "until": str(until), "h": h, "gates": {}}

    with db.connect() as conn:
        cal = label_mod.full_calendar(conn)
        active = load_active_features(conn)
        prodset = sorted(active)
        if cand in prodset:
            print(f"✗ {cand} 已在 prodset active——本漏斗是「未進產」路徑")
            return 2
        with db.transaction(conn) as cur:
            cur.execute(
                f"SELECT count(*) FROM {fc.FEATURE_TABLE} WHERE feature=%s",
                (cand,),
            )
            staged_before = cur.fetchone()[0]
            cur.execute(
                "SELECT DISTINCT panel_date FROM feature_values "
                "WHERE panel_date>=%s AND panel_date<=%s ORDER BY panel_date",
                (SINCE_2014, until),
            )
            fv_all = [r[0] for r in cur.fetchall()]
            cur.execute(
                "SELECT DISTINCT as_of_date FROM core_universe_asof "
                "WHERE as_of_date>=%s AND as_of_date<=%s ORDER BY 1",
                (SINCE_2014, until),
            )
            asof_pds = [r[0] for r in cur.fetchall()]
            cur.execute("SELECT count(*) FROM trial_ledger")
            ledger_before = cur.fetchone()[0]
            cur.execute(
                "SELECT feature FROM evolution_production_feature_set "
                "WHERE set_status='active' ORDER BY 1"
            )
            active_before = [r[0] for r in cur.fetchall()]
        panels_2014 = _nonoverlap(fv_all, h)
        panels_2021 = _nonoverlap([p for p in fv_all if p >= SINCE_2021], h)
        canon = baseline.canonical_features(conn, panels_2014)
        others = [f for f in canon if f != cand]
        print(
            f"candidate={cand} until={until} h={h}  "
            f"prodset={prodset} canon={len(canon)} asof={len(asof_pds)}"
        )
        print(f"staged_before[{cand}]={staged_before} ledger={ledger_before}")
        print(f"hash2014={_panel_hash(panels_2014)} hash2021={_panel_hash(panels_2021)}")

        need = list(dict.fromkeys(prodset + others + [cand]))
        print("wide-load …")
        wide = _load_wide(conn, asof_pds, need)
        labs = _load_labels(conn, asof_pds, h, cal, wide)

        # ── (0) 預診 ──
        rho_prod = {p: _median_abs_rho(wide, cand, p, asof_pds) for p in prodset}
        rho_canon = {f: _median_abs_rho(wide, cand, f, asof_pds) for f in others}
        rho_prod = {k: v for k, v in rho_prod.items() if v is not None}
        rho_canon = {k: v for k, v in rho_canon.items() if v is not None}
        max_prod = max(rho_prod.values()) if rho_prod else 0.0
        nearest_c, max_canon = (
            max(rho_canon.items(), key=lambda kv: kv[1]) if rho_canon else (None, 0.0)
        )
        max_rho = max(max_prod, max_canon)
        g0_pass = max_rho < RHO_MAX
        payload["gates"]["g0_prediag"] = {
            "pass": g0_pass,
            "max_rho": max_rho,
            "max_vs_prodset": max_prod,
            "max_vs_canonical": max_canon,
            "nearest_canonical": nearest_c,
            "rho_prodset": rho_prod,
            "rho_canonical_top5": dict(
                sorted(rho_canon.items(), key=lambda kv: -kv[1])[:5]
            ),
        }
        print(
            f"(0) 預診 max|ρ|={max_rho:.3f}  vs_prodset={max_prod:.3f}  "
            f"vs_canon={max_canon:.3f} nearest={nearest_c}  "
            f"{'PASS' if g0_pass else 'FAIL'}"
        )
        if not g0_pass:
            verdict, died_at = "dead_prediag", 0
            payload["verdict"] = verdict
            payload["died_at"] = died_at
            _dump(payload, t0)
            return 0

        # ── (1) 建值（隔離）──
        n_ins, n_kept = _copy_to_staging(conn, cand, SINCE_2014, until)
        g1_pass = n_kept > 0
        payload["gates"]["g1_stage"] = {
            "pass": g1_pass,
            "upsert_rowcount": n_ins,
            "staged_rows": n_kept,
            "wrote_feature_values": False,
        }
        print(f"(1) staging upsert rowcount={n_ins} kept={n_kept}  {'PASS' if g1_pass else 'FAIL'}")
        if not g1_pass:
            verdict, died_at = "dead_stage", 1
            _clear_staging_feat(conn, cand)
            payload["verdict"] = verdict
            payload["died_at"] = died_at
            _dump(payload, t0)
            return 0

        # ── (2) IC ──
        ics = {}
        for pd_ in asof_pds:
            by, lab = wide.get(pd_) or {}, labs.get(pd_) or {}
            common = [s for s, fv in by.items() if cand in fv and s in lab]
            if len(common) < MIN_CROSS:
                continue
            ic = metrics._spearman([by[s][cand] for s in common], [lab[s] for s in common])
            if ic is not None:
                ics[pd_] = ic
        summ = metrics.summarize(ics)
        hac = metrics.effective_t_hac(ics, lag=HAC_LAG)
        vals = list(ics.values())
        med_ic = float(np.median(vals)) if vals else None
        arr = np.array(vals, dtype=float) if vals else np.array([])
        if len(arr) and arr.mean() != 0:
            sign_frac = float((np.sign(arr) == np.sign(arr.mean())).mean())
        else:
            sign_frac = None
        g2_pass = (
            hac is not None
            and abs(hac) >= HAC_MIN
            and sign_frac is not None
            and sign_frac >= SIGN_MIN
        )
        payload["gates"]["g2_ic"] = {
            "pass": g2_pass,
            "n": summ["n_panels"],
            "mean_ic": summ["mean_ic"],
            "median_ic": med_ic,
            "hac_t": hac,
            "iid_t": summ["effective_t"],
            "hit": summ["hit_rate"],
            "sign_frac": sign_frac,
            "hac_lag": HAC_LAG,
        }
        print(
            f"(2) IC n={summ['n_panels']} med={med_ic} HAC={hac} iid={summ['effective_t']} "
            f"sgn={sign_frac}  {'PASS' if g2_pass else 'FAIL'}"
        )
        if not g2_pass:
            n_del = _clear_staging_feat(conn, cand)
            print(f"    staging 清本欄 {n_del} 列")
            verdict, died_at = "dead_ic", 2
            payload["verdict"] = verdict
            payload["died_at"] = died_at
            payload["staging_cleared"] = n_del
            _dump(payload, t0)
            return 0

        # ── (3) 去相關（值同 (0)；staging 已在）──
        g3_pass = g0_pass
        payload["gates"]["g3_decorr"] = {
            "pass": g3_pass,
            "note": "拷貝自 feature_values，ρ 與 (0) 同尺",
            "max_rho": max_rho,
            "nearest_canonical": nearest_c,
        }
        print(f"(3) 去相關 max|ρ|={max_rho:.3f}  {'PASS' if g3_pass else 'FAIL'}")
        if not g3_pass:
            n_del = _clear_staging_feat(conn, cand)
            verdict, died_at = "dead_decorr", 3
            payload["verdict"] = verdict
            payload["died_at"] = died_at
            payload["staging_cleared"] = n_del
            _dump(payload, t0)
            return 0

        # ── (4) Ridge 增量（窗穩：2014 與 2021）──
        folds14 = walkforward.splits(panels_2014, h, calendar=cal)
        folds21 = walkforward.splits(panels_2021, h, calendar=cal)
        # labels/wide 只載了 asof_pds；非重疊 fv 日應已在 asof 內
        def _delta(folds, tag):
            b = _ridge_ic_series(folds, wide, labs, prodset)
            a = _ridge_ic_series(folds, wide, labs, prodset + [cand])
            bm = float(np.mean(list(b.values()))) if b else None
            am = float(np.mean(list(a.values()))) if a else None
            dlt = (am - bm) if (am is not None and bm is not None) else None
            print(f"    {tag} base={bm} plus={am} Δ={dlt} n={len(a)}")
            return {"base": bm, "plus": am, "delta": dlt, "n": len(a)}

        d14 = _delta(folds14, "2014")
        d21 = _delta(folds21, "2021")
        g4_pass = (
            d14["delta"] is not None
            and d21["delta"] is not None
            and d14["delta"] > 0
            and d21["delta"] > 0
        )
        payload["gates"]["g4_increment"] = {
            "pass": g4_pass,
            "since2014": d14,
            "since2021": d21,
            "note": "Ridge 決定性；窗穩＝2014 且 2021 ΔIC>0",
        }
        print(f"(4) 增量  {'PASS' if g4_pass else 'FAIL'}")
        if not g4_pass:
            n_del = _clear_staging_feat(conn, cand)
            print(f"    staging 清本欄 {n_del} 列")
            verdict, died_at = "dead_increment", 4
            payload["verdict"] = verdict
            payload["died_at"] = died_at
            payload["staging_cleared"] = n_del
            _dump(payload, t0)
            return 0

        # ── (5) #14 research（不付 N）──
        print("(5) #14 research 有／無該欄 …")
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import survivorship_economic_verdict as sev  # noqa: E402

        cells = {}
        for since, pans, tag in (
            (SINCE_2014, panels_2014, "2014_incumbent"),
            (SINCE_2021, panels_2021, "2021_incumbent"),
        ):
            print(f"    incumbent {tag} base …")
            cells[tag + "_base"] = _econ_cell(conn, pans, h, prodset)
            print(f"    incumbent {tag} plus …")
            cells[tag + "_plus"] = _econ_cell(conn, pans, h, prodset + [cand])
        for since, pans, tag in (
            (SINCE_2014, panels_2014, "2014_pit"),
            (SINCE_2021, panels_2021, "2021_pit"),
        ):
            print(f"    pit {tag} …")
            lookup_b = sev.build_pit_universe(conn, pans, prodset, liquidity_pct=25)
            lookup_a = sev.build_pit_universe(conn, pans, prodset + [cand], liquidity_pct=25)
            rb = sev.run_pit_economic(conn, pans, h, prodset, lookup_b, top_frac=TOP, cost=COST)
            ra = sev.run_pit_economic(conn, pans, h, prodset + [cand], lookup_a, top_frac=TOP, cost=COST)

            def _pit(raw):
                if not raw:
                    return None
                pn, bn = raw.get("net") or {}, raw.get("bench") or {}
                return {
                    "n": raw.get("n"),
                    "net_sharpe": (pn or {}).get("sharpe"),
                    "bench_sharpe": (bn or {}).get("sharpe"),
                    "max_drawdown": (pn or {}).get("max_drawdown"),
                    "calmar": (pn or {}).get("calmar"),
                    "cagr": (pn or {}).get("cagr"),
                }

            cells[tag + "_base"] = _pit(rb)
            cells[tag + "_plus"] = _pit(ra)

        def _delta_sh(base, plus):
            if not base or not plus:
                return None, None
            ds = None
            if base.get("net_sharpe") is not None and plus.get("net_sharpe") is not None:
                ds = plus["net_sharpe"] - base["net_sharpe"]
            dd_ok = None
            if base.get("max_drawdown") is not None and plus.get("max_drawdown") is not None:
                dd_ok = plus["max_drawdown"] >= base["max_drawdown"] - MAXDD_TOL
            return ds, dd_ok

        ds21, dd21 = _delta_sh(cells.get("2021_incumbent_base"), cells.get("2021_incumbent_plus"))
        g5_pass = ds21 is not None and ds21 > DSHARPE_MIN and dd21 is True
        payload["gates"]["g5_econ"] = {
            "pass": g5_pass,
            "threshold_dsharpe": DSHARPE_MIN,
            "maxdd_tol": MAXDD_TOL,
            "decision_cell": "2021_incumbent",
            "dsharpe_2021_incumbent": ds21,
            "maxdd_ok_2021_incumbent": dd21,
            "cells": cells,
            "paid_n": False,
        }
        print(f"(5) #14 2021在位 ΔSharpe={ds21} MaxDD_ok={dd21}  {'PASS' if g5_pass else 'FAIL'}")
        if not g5_pass:
            n_del = _clear_staging_feat(conn, cand)
            print(f"    staging 清本欄 {n_del} 列")
            verdict, died_at = "dead_econ", 5
            payload["staging_cleared"] = n_del
        else:
            verdict, died_at = "funnel_pass_no_promote", None
            payload["staging_kept"] = True
            print("    staging 保留待 PROMOTE-feat-go（本 GO 不提拔）")

        with db.transaction(conn) as cur:
            cur.execute("SELECT count(*) FROM trial_ledger")
            ledger_after = cur.fetchone()[0]
            cur.execute(
                "SELECT feature FROM evolution_production_feature_set "
                "WHERE set_status='active' ORDER BY 1"
            )
            active_after = [r[0] for r in cur.fetchall()]
            cur.execute(
                "SELECT horizon, verdict FROM econ_verdict_rule "
                "WHERE horizon IN (20,60) ORDER BY 1"
            )
            verd = list(cur.fetchall())
        payload["ledger_before"] = ledger_before
        payload["ledger_after"] = ledger_after
        payload["active_before"] = active_before
        payload["active_after"] = active_after
        payload["verdict_rule"] = verd
        payload["verdict"] = verdict
        payload["died_at"] = died_at
        _dump(payload, t0)
        print(f"ledger {ledger_before}→{ledger_after}  active={active_after}")
        return 0


def _dump(payload, t0):
    payload["elapsed_s"] = round(time.time() - t0, 1)
    cand = payload.get("candidate") or "unknown"
    outp = f"/tmp/e4-feat-{cand}-20260817.json"
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, default=str)
    print(f"verdict={payload.get('verdict')} json {outp} elapsed={payload['elapsed_s']}s")


def main() -> int:
    ap = argparse.ArgumentParser(description="E4 一支漏斗（隔離表、不提拔、不付 N）")
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--until", default=str(UNTIL_DEFAULT))
    ap.add_argument("--h", type=int, default=H_DEFAULT)
    args = ap.parse_args()
    return run(cand=args.candidate, until=date.fromisoformat(args.until), h=args.h)


if __name__ == "__main__":
    raise SystemExit(main())

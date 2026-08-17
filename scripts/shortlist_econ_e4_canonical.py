#!/usr/bin/env python
"""E4 短名單 — 從 canonical 未進 prodset 的既有欄，排出下一支漏斗候選。

🎯 這支在做什麼（白話）：E3 證明 34 欄能把 2021 在位從輸基準翻成贏，3 欄現役翻不了。
   本支不開新表、不建新值：對「canonical ∖ prodset」逐欄做 (0) 對現役 3 欄去相關預診、
   (2) as-of 單因子 H60 rank IC＋HAC t（lag=2）、以及對 **2021 在位** 的 Ridge IC 增量
   （3+1 vs 3）。排出第一支。IC 增量 ≠ #14、≠ 可提拔。

   只讀 feature_values（不寫、不讀 staging）。不寫 prodset。不寫 trial_ledger。

對齊 E4-shortlist-go；until／H 與 E3 同尺。

守 #8（as-of、until＝已實現）· #11（HAC、禁裸 iid）· #12（IC／HAC／Ridge 住 evaluation）·
   #14（本支不到經濟終關）· #15（先前 removed 不當第一支）。

執行指令矩陣:
  python scripts/shortlist_econ_e4_canonical.py
      # 無參數＝E3 同尺短名單（until=2026-04-30, h=60）
  python scripts/shortlist_econ_e4_canonical.py --until 2026-04-30 --h 60
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
from augur.core import db
from augur.core.prodset_contract import load_active_features
from augur.evaluation import baseline, metrics, walkforward
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
FEATURE_TABLE = "feature_values"


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
    blob = ",".join(str(p) for p in panels)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _load_wide(conn, panels, feats):
    """as-of 宇宙 × feature_values（不碰 staging）。{panel: {sid: {feat: val}}}"""
    wide = {}
    n_asof = 0
    with db.transaction(conn) as cur:
        for pd_ in panels:
            cur.execute(
                "SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s",
                (pd_,),
            )
            stocks = {str(r[0]) for r in cur.fetchall()}
            if stocks:
                n_asof += 1
            cur.execute(
                f"SELECT stock_id, feature, value FROM {FEATURE_TABLE} "
                "WHERE panel_date=%s AND feature = ANY(%s)",
                (pd_, list(feats)),
            )
            by = {}
            for sid, f, v in cur.fetchall():
                sid = str(sid)
                if stocks and sid not in stocks:
                    continue
                if not stocks:
                    continue
                by.setdefault(sid, {})[f] = float(v)
            wide[pd_] = by
    return wide, n_asof


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
        tpd = fold["test"]
        te = _xy(wide.get(tpd) or {}, labs.get(tpd) or {}, feats)
        if te is None:
            continue
        Xte, yte, _sids = te
        chunks_x, chunks_y = [], []
        for tpd_tr in fold["train"]:
            tr = _xy(wide.get(tpd_tr) or {}, labs.get(tpd_tr) or {}, feats)
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
            out[tpd] = ic
    return out


def _ready(u):
    return (
        (not u["removed"])
        and (not u["prediag_fail"])
        and u["hac_t"] is not None
        and abs(u["hac_t"]) >= HAC_MIN
        and u["sign_frac"] is not None
        and u["sign_frac"] >= SIGN_MIN
        and u["delta_ic_2021"] is not None
        and u["delta_ic_2021"] > 0
    )


def run(*, until: date, h: int) -> int:
    t0 = time.time()
    with db.connect() as conn:
        cal = label_mod.full_calendar(conn)
        active = load_active_features(conn)
        with db.transaction(conn) as cur:
            cur.execute(
                "SELECT feature FROM evolution_production_feature_set "
                "WHERE set_status='removed' ORDER BY 1"
            )
            removed = [r[0] for r in cur.fetchall()]
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
        panels_2014 = _nonoverlap(fv_all, h)
        fv_2021 = [p for p in fv_all if p >= SINCE_2021]
        panels_2021 = _nonoverlap(fv_2021, h)
        canon = baseline.canonical_features(conn, panels_2014)
        prodset = sorted(active)
        cands = [f for f in canon if f not in set(prodset)]
        print(
            f"until={until} h={h}  canonical={len(canon)} prodset={len(prodset)} "
            f"cands={len(cands)}"
        )
        print(f"prodset={prodset}")
        print(f"removed={removed}")
        print(f"asof_panels={len(asof_pds)}  fv_nonoverlap_2014={len(panels_2014)} "
              f"hash={_panel_hash(panels_2014)}")
        print(f"fv_nonoverlap_2021={len(panels_2021)} hash={_panel_hash(panels_2021)}")
        if not cands:
            print("✗ 沒有 canonical-not-prodset")
            return 1

        need_feats = list(dict.fromkeys(prodset + cands))
        load_panels = sorted(set(asof_pds) | set(panels_2021))
        print(f"wide-load panels={len(load_panels)} feats={len(need_feats)} …")
        t1 = time.time()
        wide, n_asof = _load_wide(conn, load_panels, need_feats)
        print(f"  values {time.time()-t1:.1f}s  asof_hit={n_asof}")
        t1 = time.time()
        labs = _load_labels(conn, load_panels, h, cal, wide)
        n_lab = sum(1 for pd_ in asof_pds if len(labs.get(pd_) or {}) >= MIN_CROSS)
        print(f"  labels {time.time()-t1:.1f}s  labelled_asof={n_lab}")

        ic_map = {f: {} for f in cands}
        rho_lists = {f: {p: [] for p in prodset} for f in cands}
        for pd_ in asof_pds:
            by = wide.get(pd_) or {}
            lab = labs.get(pd_) or {}
            if len(lab) < MIN_CROSS:
                continue
            for f in cands:
                common = [s for s, fv in by.items() if f in fv and s in lab]
                if len(common) < MIN_CROSS:
                    continue
                x = [by[s][f] for s in common]
                y = [lab[s] for s in common]
                ic = metrics._spearman(x, y)
                if ic is not None:
                    ic_map[f][pd_] = ic
                for p in prodset:
                    both = [s for s in common if p in by[s]]
                    if len(both) < MIN_CROSS:
                        continue
                    r = metrics._spearman([by[s][f] for s in both], [by[s][p] for s in both])
                    if r is not None:
                        rho_lists[f][p].append(abs(r))

        uni = []
        for f in cands:
            ics = ic_map[f]
            vals = list(ics.values())
            med_ic = float(np.median(vals)) if vals else None
            summ = metrics.summarize(ics)
            hac = metrics.effective_t_hac(ics, lag=HAC_LAG)
            arr = np.array(vals, dtype=float) if vals else np.array([])
            if len(arr) and np.isfinite(arr.mean()) and arr.mean() != 0:
                sign_frac = float((np.sign(arr) == np.sign(arr.mean())).mean())
            else:
                sign_frac = None
            max_rho = 0.0
            rho_by = {}
            for p in prodset:
                xs = rho_lists[f][p]
                med = float(np.median(xs)) if xs else None
                rho_by[p] = med
                if med is not None:
                    max_rho = max(max_rho, med)
            uni.append(
                {
                    "feature": f,
                    "n_ic": summ["n_panels"],
                    "mean_ic": summ["mean_ic"],
                    "median_ic": med_ic,
                    "hac_t": hac,
                    "iid_t": summ["effective_t"],
                    "hit": summ["hit_rate"],
                    "sign_frac": sign_frac,
                    "max_rho": max_rho,
                    "rho_by": rho_by,
                    "removed": f in removed,
                    "prediag_fail": max_rho >= RHO_MAX,
                }
            )

        folds = walkforward.splits(panels_2021, h, calendar=cal)
        print(f"Ridge WF folds={len(folds)} on 2021 nonoverlap …")
        t1 = time.time()
        base_ics = _ridge_ic_series(folds, wide, labs, prodset)
        base_mean = float(np.mean(list(base_ics.values()))) if base_ics else None
        print(f"  prodset-3 mean_ic={base_mean} n={len(base_ics)} ({time.time()-t1:.1f}s)")

        delta = {}
        for j, f in enumerate(cands):
            t2 = time.time()
            ics = _ridge_ic_series(folds, wide, labs, prodset + [f])
            mean = float(np.mean(list(ics.values()))) if ics else None
            dlt = (mean - base_mean) if (mean is not None and base_mean is not None) else None
            delta[f] = {"mean_ic": mean, "delta": dlt, "n": len(ics)}
            print(
                f"  +{f} ΔIC={None if dlt is None else round(dlt, 4)} "
                f"n={len(ics)} ({time.time()-t2:.1f}s) [{j+1}/{len(cands)}]"
            )

    for u in uni:
        d = delta.get(u["feature"]) or {}
        u["delta_ic_2021"] = d.get("delta")
        u["ridge_mean_2021"] = d.get("mean_ic")
        u["ridge_n_2021"] = d.get("n")

    uni.sort(
        key=lambda u: (
            0 if _ready(u) else 1,
            -(u["delta_ic_2021"] if u["delta_ic_2021"] is not None else -9),
            -(abs(u["hac_t"]) if u["hac_t"] is not None else -1),
        )
    )
    ready = [u for u in uni if _ready(u)]
    first = ready[0]["feature"] if ready else None

    print("\n══ E4 shortlist（IC ≠ #14；≠ promote）══")
    print(
        f"{'feature':<36} {'medIC':>8} {'HACt':>7} {'sgn':>5} {'ΔIC21':>8} "
        f"{'ρmax':>6} {'rm':>3} {'pre':>4} ready"
    )
    for u in uni:
        def _fmt(v, w, nd):
            if v is None:
                return f"{'nan':>{w}}"
            return f"{v:{w}.{nd}f}"

        print(
            f"{u['feature']:<36} "
            f"{_fmt(u['median_ic'], 8, 4)} "
            f"{_fmt(u['hac_t'], 7, 3)} "
            f"{_fmt(u['sign_frac'], 5, 2)} "
            f"{_fmt(u['delta_ic_2021'], 8, 4)} "
            f"{u['max_rho']:6.3f} "
            f"{'Y' if u['removed'] else 'n':>3} "
            f"{'FAIL' if u['prediag_fail'] else 'ok':>4} "
            f"{'YES' if _ready(u) else '-'}"
        )
    print(f"\n第一支建議: {first or '（無漏斗就緒；見報告）'}")
    print(f"n_ready={len(ready)} elapsed {time.time()-t0:.1f}s  labelled_asof={n_lab}")
    payload = {
        "until": str(until),
        "h": h,
        "hac_lag": HAC_LAG,
        "rho_max": RHO_MAX,
        "hac_min": HAC_MIN,
        "sign_min": SIGN_MIN,
        "prodset": prodset,
        "removed": removed,
        "canonical_n": len(canon),
        "canon": canon,
        "cands": cands,
        "first": first,
        "n_ready": len(ready),
        "base_ridge_mean_ic_2021": base_mean,
        "base_ridge_n_2021": len(base_ics),
        "n_asof_panels": len(asof_pds),
        "n_labelled_asof": n_lab,
        "hash_2014": _panel_hash(panels_2014),
        "hash_2021": _panel_hash(panels_2021),
        "n_nonoverlap_2014": len(panels_2014),
        "n_nonoverlap_2021": len(panels_2021),
        "n_wf_folds": len(folds),
        "rows": uni,
    }
    outp = "/tmp/e4-shortlist-20260817.json"
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, default=str)
    print(f"json {outp}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="E4 canonical-not-prodset 短名單（不提拔、不付 N）")
    ap.add_argument("--until", default=str(UNTIL_DEFAULT))
    ap.add_argument("--h", type=int, default=H_DEFAULT)
    args = ap.parse_args()
    until = date.fromisoformat(args.until)
    return run(until=until, h=args.h)


if __name__ == "__main__":
    raise SystemExit(main())

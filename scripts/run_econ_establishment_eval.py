#!/usr/bin/env python
"""經濟確立同尺量產 — 凍結 H60 主格 × prodset/canonical × 雙宇宙 × 兩段 since。

🎯 這支在做什麼（白話）：E3 把「現役 3 欄 prodset 的 RankRidge H60 LO」跟 canonical
   對照，用同一把經濟尺量出來，寫入 econ_eval_run。預設 research、**不付 N**
   （不寫 trial_ledger）、**不改** econ_verdict_rule、**不 evaluate** 閘。
   until＝最後已實現 H60 label 的 panel（禁把未實現 08-14 段算進淨值）。

對齊 reports/augur_econ_prove_edge_plan_r17_20260817.md §5／§8 E3。
   閘須已 approved 才准 --kind establishment（本 GO 只准 research）。

守 #8（until＝已實現；as-of／PIT ≤t）· #12（選股／DSR／非重疊同既有住所）·
   #14（淨 vs 扣成本基準）· #15（不塗綠；DSR 年化 bug 禁）· #26（不改 verdict）。

執行指令矩陣:
  python scripts/run_econ_establishment_eval.py
      # 無參數:現況（唯讀；閘／until／ledger N）
  python scripts/run_econ_establishment_eval.py --kind research --no-pay-n
      # E3：八細胞＋主格 1.5×成本；寫 econ_eval_run；不寫 ledger
  python scripts/run_econ_establishment_eval.py --kind establishment --pay-n --gate GATE
      # 另 GO 才准；本檔仍拒除非明示兩個旗標
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import asof_ready, db
from augur.core.prodset_contract import ProdsetEmptyError
from augur.evaluation import baseline, deflation, portfolio
from augur.evaluation import label as label_mod

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import survivorship_economic_verdict as sev  # noqa: E402

GATE_ID = "egate_H_60_ridge_LO_prodset_r17"
H = 60
TOP = 0.1
WEIGHT = "equal"
LEDGER_WEIGHT = "LO"
MODEL = "B2_ridge"
COST = 0.00585
COST_STRESS = 0.008775
SEED = 42
SINCE_PRIMARY = date(2014, 1, 1)
SINCE_ROBUST = date(2021, 1, 1)


def _git7() -> str:
    try:
        return (
            subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parent.parent),
            ).stdout.strip()
            or "unknown"
        )
    except OSError:
        return "unknown"


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
    return hashlib.sha256(",".join(map(str, panels)).encode()).hexdigest()[:16]


def last_realized_panel(conn, h: int):
    """最後一個 feature_values panel，其 H 窗出場日已落在 PriceAdj 日曆內。"""
    cal = label_mod.full_calendar(conn)
    with db.transaction(conn) as cur:
        cur.execute("SELECT DISTINCT panel_date FROM feature_values ORDER BY panel_date")
        pds = [r[0] for r in cur.fetchall()]
        tip = asof_ready.taiex_price_max(cur)
    last = None
    entry = exit_ = None
    for p in reversed(pds):
        after = [d for d in cal if d > p]
        if len(after) >= h + 1:
            last, entry, exit_ = p, after[0], after[h]
            break
    return last, entry, exit_, tip, cal


def _ledger_n(cur):
    cur.execute(
        """
        SELECT count(*) FROM (
          SELECT DISTINCT model, horizon, top_frac, weight, feats_hash, cost
            FROM trial_ledger
        ) t
        """
    )
    n_all = int(cur.fetchone()[0])
    cur.execute(
        """
        SELECT count(*) FROM (
          SELECT DISTINCT model, horizon, top_frac, weight, feats_hash, cost
            FROM trial_ledger WHERE horizon=%s
        ) t
        """,
        (H,),
    )
    n_fam = int(cur.fetchone()[0])
    cur.execute("SELECT horizon, metric_value FROM trial_ledger WHERE metric_name='net_sharpe'")
    trials = [(int(h), float(s)) for h, s in cur.fetchall() if s is not None]
    cur.execute("SELECT count(*) FROM trial_ledger")
    n_rows = int(cur.fetchone()[0])
    return n_all, n_fam, trials, n_rows


def _dsr(net_series, ppy, trials, n_all, n_fam):
    """per-period DSR。混頻試驗用 ppy×(60/h) 近似（E3 不重跑他窗取 ppy；note 揭露）。"""
    ppy_by = {H: ppy}
    for h, _ in trials:
        if h not in ppy_by and h:
            ppy_by[h] = ppy * (H / float(h))
    pp_all = deflation.trials_per_period(trials, ppy_by)
    pp_fam = deflation.trials_per_period([(h, s) for h, s in trials if h == H], ppy_by)
    floor_all = deflation.deflated_floor(net_series, ppy, pp_all, n_all)
    floor_fam = deflation.deflated_floor(net_series, ppy, pp_fam, n_fam)
    dsr_all = floor_all.get("dsr")
    dsr_fam = floor_fam.get("dsr")
    # 保守＝較大 N
    dsr = dsr_all if dsr_all is not None else dsr_fam
    n_used = n_all if dsr_all is not None else n_fam
    return dsr, n_used, dsr_all, dsr_fam


def status() -> int:
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn:
        last, entry, exit_, tip, _ = last_realized_panel(conn, H)
        with db.transaction(conn) as cur:
            cur.execute(
                "SELECT gate_id, status, approved_by, criteria_sha FROM econ_establishment_gate WHERE gate_id=%s",
                (GATE_ID,),
            )
            g = cur.fetchone()
            n_all, n_fam, _t, n_rows = _ledger_n(cur)
            cur.execute("SELECT count(*) FROM econ_eval_run")
            n_run = cur.fetchone()[0]
            cur.execute("SELECT horizon, verdict FROM econ_verdict_rule WHERE horizon IN (20,60) ORDER BY 1")
            verd = list(cur.fetchall())
    print(f"gate: {g}")
    print(f"PriceAdj tip={tip}  last_realized_H{H}_panel={last} entry={entry} exit={exit_}")
    print(f"trial_ledger rows={n_rows} N_all={n_all} N_H{H}={n_fam}")
    print(f"econ_eval_run={n_run}  verdict={verd}")
    return 0


def _panels(conn, since, until, h):
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT DISTINCT panel_date FROM feature_values "
            "WHERE panel_date>=%s AND panel_date<=%s ORDER BY panel_date",
            (since, until),
        )
        pds = [r[0] for r in cur.fetchall()]
    return _nonoverlap(pds, h)


def _feats(conn, panels, source: str):
    if source == "prodset":
        return baseline.resolve_train_feats(conn, panels, source="prodset")
    if source == "canonical":
        return baseline.canonical_features(conn, panels)
    raise ValueError(source)


def _run_incumbent(conn, panels, feats, cost):
    return portfolio.run_backtest(
        conn, panels, H, feats=feats, model=MODEL, top_frac=TOP, weight=WEIGHT,
        cost=cost, asof=True, seed=SEED,
    )


def _run_pit(conn, panels, feats, cost):
    lookup = sev.build_pit_universe(conn, panels, feats, liquidity_pct=25)
    return sev.run_pit_economic(conn, panels, H, feats, lookup, top_frac=TOP, cost=cost)


def _normalize(raw, universe: str):
    if not raw:
        return None
    if universe == "asof_incumbent":
        pn, bn = raw.get("portfolio_net") or {}, raw.get("benchmark_net") or {}
        return {
            "n_periods": raw.get("n_periods"),
            "ppy": raw.get("ppy") or raw.get("periods_per_year"),
            "net_sharpe": (pn or {}).get("sharpe"),
            "bench_sharpe": (bn or {}).get("sharpe"),
            "net_cagr": (pn or {}).get("cagr"),
            "bench_cagr": (bn or {}).get("cagr"),
            "avg_turnover": raw.get("avg_turnover"),
            "span": raw.get("span"),
            "net_series": raw.get("net_series") or [],
        }
    pn, bn = raw.get("net") or {}, raw.get("bench") or {}
    turns = raw.get("turn_series") or []
    return {
        "n_periods": raw.get("n"),
        "ppy": raw.get("ppy"),
        "net_sharpe": (pn or {}).get("sharpe"),
        "bench_sharpe": (bn or {}).get("sharpe"),
        "net_cagr": (pn or {}).get("cagr"),
        "bench_cagr": (bn or {}).get("cagr"),
        "avg_turnover": (float(sum(turns) / len(turns)) if turns else None),
        "span": raw.get("span"),
        "net_series": raw.get("net_series") or [],
    }


def _insert(cur, *, kind, gate_id, source, universe, since, cost, panels, feats, norm, dsr, n_trials, paid_n, git7, note):
    ns = norm["net_sharpe"]
    bs = norm["bench_sharpe"]
    excess = (ns - bs) if (ns is not None and bs is not None) else None
    cur.execute(
        """
        INSERT INTO econ_eval_run (
          run_kind, gate_id, feature_source, model, horizon, top_frac, weight, cost,
          sample_since, universe, n_periods, periods_per_year, net_sharpe, bench_sharpe,
          net_excess, avg_turnover, dsr, n_trials, panel_hash, paid_n, git_sha, note
        ) VALUES (
          %s,%s,%s,%s,%s,%s,%s,%s,
          %s,%s,%s,%s,%s,%s,
          %s,%s,%s,%s,%s,%s,%s,%s
        ) RETURNING run_id
        """,
        (
            kind, gate_id, source, MODEL, H, TOP, LEDGER_WEIGHT, cost,
            since, universe, norm["n_periods"], norm["ppy"], ns, bs,
            excess, norm["avg_turnover"], dsr, n_trials, _panel_hash(panels), paid_n, git7, note,
        ),
    )
    return cur.fetchone()[0]


def measure(*, kind: str, pay_n: bool, gate_id: str) -> int:
    if kind != "research":
        print("✗ 本 GO 只准 --kind research（establishment 另句）")
        return 2
    if pay_n:
        print("✗ 本 GO 是 no-pay-n；禁寫 trial_ledger")
        return 2
    git7 = _git7()
    cells = []
    for source in ("prodset", "canonical"):
        for since in (SINCE_PRIMARY, SINCE_ROBUST):
            for universe in ("asof_incumbent", "pit_broad"):
                cells.append((source, since, universe, COST, False))
    cells.append(("prodset", SINCE_PRIMARY, "asof_incumbent", COST_STRESS, True))

    with db.connect() as conn:
        last, entry, exit_, tip, _ = last_realized_panel(conn, H)
        if last is None:
            print("✗ 找不到已實現 H60 panel")
            return 1
        with db.transaction(conn) as cur:
            cur.execute(
                "SELECT status, approved_by, criteria_sha FROM econ_establishment_gate WHERE gate_id=%s",
                (gate_id,),
            )
            grow = cur.fetchone()
            n_all, n_fam, trials, n_rows_before = _ledger_n(cur)
            cur.execute("SELECT horizon, verdict FROM econ_verdict_rule WHERE horizon IN (20,60) ORDER BY 1")
            verd_before = list(cur.fetchall())
        if not grow or grow[0] != "approved":
            print(f"✗ 閘未核准: {grow}（E3 量產仍可 research，但本路徑要求 E2 已閉）")
            return 1
        print(
            f"until={last} (entry={entry} exit={exit_} tip={tip})  "
            f"N_all={n_all} N_fam={n_fam} ledger_rows={n_rows_before}"
        )
        print(f"gate={gate_id} status={grow[0]} by={grow[1]} sha={grow[2]}")
        print("≠established：本輸出只寫 econ_eval_run research 列。")

        rows_out = []
        for source, since, universe, cost, is_stress in cells:
            tag = f"{source}/{since.isoformat()[:4]}/{universe}" + ("/cost1.5x" if is_stress else "")
            t0 = time.time()
            try:
                panels = _panels(conn, since, last, H)
                feats = _feats(conn, panels, source)
            except ProdsetEmptyError as e:
                print(f"✗ {tag} prodset empty: {e}")
                return 1
            print(f"── {tag}  panels={len(panels)} n_feats={len(feats)} hash={_panel_hash(panels)} ──")
            if universe == "asof_incumbent":
                raw = _run_incumbent(conn, panels, feats, cost)
            else:
                raw = _run_pit(conn, panels, feats, cost)
            norm = _normalize(raw, universe)
            elapsed = time.time() - t0
            if not norm or not norm["n_periods"]:
                print(f"✗ {tag} 回測空（elapsed {elapsed:.1f}s）")
                return 1
            dsr, n_used, dsr_all, dsr_fam = _dsr(norm["net_series"], float(norm["ppy"]), trials, n_all, n_fam)
            note = json.dumps(
                {
                    "batch": "e3-20260817",
                    "tag": tag,
                    "n_feats": len(feats),
                    "feats": list(feats) if source == "prodset" else f"canonical:{len(feats)}",
                    "span": norm["span"],
                    "until": str(last),
                    "cost_stress": is_stress,
                    "dsr_all": dsr_all,
                    "dsr_fam": dsr_fam,
                    "ppy_mixed": "scale 60/h (not re-run)",
                    "elapsed_s": round(elapsed, 1),
                    "verdict_untouched": True,
                },
                ensure_ascii=False,
            )
            with db.transaction(conn) as cur:
                rid = _insert(
                    cur, kind=kind, gate_id=gate_id, source=source, universe=universe,
                    since=since, cost=cost, panels=panels, feats=feats, norm=norm,
                    dsr=dsr, n_trials=n_used, paid_n=False, git7=git7, note=note,
                )
            beat = (
                "net>bench" if (norm["net_sharpe"] is not None and norm["bench_sharpe"] is not None
                                and norm["net_sharpe"] > norm["bench_sharpe"])
                else "net≤bench"
            )
            print(
                f"  run_id={rid} n={norm['n_periods']} ppy={norm['ppy']:.3f} "
                f"netSharpe={norm['net_sharpe']:.4f} bench={norm['bench_sharpe']:.4f} "
                f"{beat} DSR={None if dsr is None else f'{dsr:.4f}'} ({elapsed:.1f}s)"
            )
            rows_out.append((tag, rid, norm, dsr, beat, len(feats)))

        with db.transaction(conn) as cur:
            _n_all2, _nf, _t, n_rows_after = _ledger_n(cur)
            cur.execute("SELECT horizon, verdict FROM econ_verdict_rule WHERE horizon IN (20,60) ORDER BY 1")
            verd_after = list(cur.fetchall())
            cur.execute("SELECT status FROM econ_establishment_gate WHERE gate_id=%s", (gate_id,))
            st = cur.fetchone()[0]
        if n_rows_after != n_rows_before:
            print(f"✗ trial_ledger 列數變了 {n_rows_before}→{n_rows_after}")
            return 1
        if verd_after != verd_before:
            print("✗ econ_verdict_rule 變了")
            return 1
        if st != "approved":
            print(f"✗ 閘狀態被改成 {st}")
            return 1

    print("\n══ E3 摘要（research；≠ established）══")
    print(f"{'tag':<42} {'net':>8} {'bench':>8} {'beat':>10} {'DSR':>8} feats")
    for tag, rid, norm, dsr, beat, nf in rows_out:
        print(
            f"{tag:<42} {norm['net_sharpe']:8.4f} {norm['bench_sharpe']:8.4f} {beat:>10} "
            f"{(f'{dsr:.3f}' if dsr is not None else '  n/a'):>8} {nf}"
        )
    print(f"ledger 未動 rows={n_rows_after}  verdict={verd_after}  gate={st}")
    print("✓ E3 research 寫入完成；未付 N、未改 verdict、未 evaluate")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="經濟確立同尺量產（E3；預設 research／不付 N）")
    ap.add_argument("--kind", choices=("research", "establishment"), default=None)
    ap.add_argument("--pay-n", dest="pay_n", action="store_true")
    ap.add_argument("--no-pay-n", dest="no_pay_n", action="store_true")
    ap.add_argument("--gate", default=GATE_ID)
    args = ap.parse_args()
    if args.kind is None:
        return status()
    pay = bool(args.pay_n) and not args.no_pay_n
    if args.no_pay_n:
        pay = False
    return measure(kind=args.kind, pay_n=pay, gate_id=args.gate)


if __name__ == "__main__":
    raise SystemExit(main())

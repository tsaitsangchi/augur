#!/usr/bin/env python
"""UP-PULL 標註 Ridge — 八窗均分 Top10 加「等回撤」；進場欄＝v1（copy-only；dry-run）。

🎯 這支在做什麼（白話）：左欄＝RankRidge 八窗平均 score Top10（相對強，不是買點），
   逐檔對 UP-PULL 做多四閘；未過就標「高位相對強，等回撤；≠進場」。
   右欄＝UP-PULL-v1 strict 進場（不足不補）。score ≠ 漲跌幅％。做空≠可空。
   不寫 prediction_values。不改 standing 20,60。不接 live 顧問殼。

執行指令矩陣:
  python scripts/probe_up_pull_annotate_ridge.py --selftest
  python scripts/probe_up_pull_annotate_ridge.py --date 2026-08-18 --k-ridge 10 --k-entry 10
  python scripts/probe_up_pull_annotate_ridge.py --date 2026-08-19  # rc=3
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

import predict_asof
import probe_uptrend_pullback as pb
from augur.core import asof_ready, db
from augur.evaluation import uptrend_pullback as up
from augur.advisor.payload import _lookup_stock_names

NOTE = (
    "copy-only／dry-run；Ridge＝相對強＋等回撤標，不是進場；"
    "進場＝UP-PULL-v1 strict；score≠漲跌幅％；路徑％≠未來％；"
    "做空≠可空；不取代 standing 20,60；不寫 prediction_values"
)
FAMILY = "RankRidge"


def ridge_avg_order(asof_iso: str) -> tuple[list[tuple[float, str, dict]], int]:
    """dry-run 八窗 score；回 [(avg, sid, per_h), ...] 高→低。失敗 → ([], rc)。"""
    by_h = {}
    n = None
    for h in up.H_TRACK:
        rows = predict_asof.predict(
            h, FAMILY, asof_iso, top_n=3, dry_run=True, quiet=True,
        )
        if rows is None:
            return [], 2
        by_h[h] = {sid: float(sc) for _rk, sid, sc, *_ in rows}
        n = len(rows) if n is None else n
        if len(rows) != n:
            return [], 2
    common = None
    for h in up.H_TRACK:
        s = set(by_h[h])
        common = s if common is None else common & s
    out = []
    for sid in common or []:
        xs = [by_h[h][sid] for h in up.H_TRACK]
        per = {str(h): by_h[h][sid] for h in up.H_TRACK}
        out.append((sum(xs) / len(xs), sid, per))
    out.sort(key=lambda t: (-t[0], t[1]))
    return out, 0


def annotate(asof_iso: str, *, k_ridge: int, k_entry: int) -> tuple[dict, int]:
    with db.connect() as conn, conn.cursor() as cur:
        scored, funnel, snap, rc = pb.score_universe(cur, conn, asof_iso)
        if rc != 0:
            return {
                "asof": asof_iso,
                "status": snap.get("status"),
                "price_max": snap.get("price_max"),
                "note": NOTE,
            }, rc
        by_sid = {r["sid"]: r for r in scored}
        order, rrc = ridge_avg_order(asof_iso)
        if rrc != 0:
            return {"asof": asof_iso, "status": "ridge_dry_run_fail", "note": NOTE}, rrc
        top = order[: int(k_ridge)]
        names = _lookup_stock_names(conn, cur, [sid for _a, sid, _p in top])
        ridge_out = []
        n_wait = 0
        n_entry_overlap = 0
        for i, (avg, sid, per) in enumerate(top, 1):
            rec = by_sid.get(sid)
            bits = rec["long_bits"] if rec else {
                "L-A": False, "L-B": False, "L-C": False, "L-D": False, "pass": False,
            }
            annot = up.wait_pullback_annot(bits)
            if annot["wait"]:
                n_wait += 1
            else:
                n_entry_overlap += 1
            dd20 = None if rec is None else rec["dd20"]
            h5 = None if rec is None else rec["rets"].get(5)
            h10 = None if rec is None else rec["rets"].get(10)
            ridge_out.append({
                "rank": i,
                "sid": sid,
                "name": names.get(sid, ""),
                "avg_score": round(float(avg), 6),
                "per_h_score": {k: round(v, 6) for k, v in per.items()},
                "tag": annot["tag"],
                "wait": annot["wait"],
                "missing": annot["missing"],
                "reason_zh": annot["reason_zh"],
                "gates": bits,
                "dd20_pct": None if dd20 is None else round(float(dd20) * 100.0, 4),
                "h5_pct": None if h5 is None else round(up.log_to_pct(h5), 4),
                "h10_pct": None if h10 is None else round(up.log_to_pct(h10), 4),
                "cycle_position_252d": None if rec is None else rec.get("cyc"),
                "price_to_252d_high": None if rec is None else rec.get("p2h"),
                "line": up.render_ridge_wait_line(
                    i, sid, names.get(sid, ""), avg, annot,
                ),
            })

        longs = [r for r in scored if r["long_bits"]["pass"]]
        shorts = [r for r in scored if r["short_bits"]["pass"]]
        longs.sort(key=lambda r: up.long_sort_key(r["sid"], r["rets"], r["dd20"]))
        shorts.sort(key=lambda r: up.short_sort_key(r["sid"], r["rets"], r["bu20"]))
        longs = up.take_strict(longs, k_entry)
        shorts = up.take_strict(shorts, k_entry)
        enames = _lookup_stock_names(
            conn, cur, [r["sid"] for r in longs + shorts],
        )
        for r in longs + shorts:
            r["name"] = enames.get(r["sid"], "")
        long_pub, short_pub = [], []
        for i, r in enumerate(longs, 1):
            pub = pb._row_public(r, i)
            pub["side"] = "long"
            pub["gates"] = r["long_bits"]
            long_pub.append(pub)
        for i, r in enumerate(shorts, 1):
            pub = pb._row_public(r, i)
            pub["side"] = "short"
            pub["gates"] = r["short_bits"]
            short_pub.append(pub)

        payload = {
            "version": "UP-PULL-ANNOTATE-RIDGE",
            "up_pull": up.VERSION,
            "family": FAMILY,
            "copy_only": True,
            "dry_run": True,
            "standing_unchanged": True,
            "wrote_prediction_values": False,
            "asof": asof_iso,
            "price_max": snap.get("price_max"),
            "k_ridge": int(k_ridge),
            "k_entry": int(k_entry),
            "n_ridge": len(ridge_out),
            "n_wait": n_wait,
            "n_ridge_pass_entry": n_entry_overlap,
            "n_long": len(long_pub),
            "n_short": len(short_pub),
            "n_long_lt_k": len(long_pub) < int(k_entry),
            "n_short_lt_k": len(short_pub) < int(k_entry),
            "ridge": ridge_out,
            "entry_long": long_pub,
            "entry_short": short_pub,
            "funnel": funnel,
            "asof_status": snap["status"],
            "at_tip": snap.get("at_tip"),
            "note": NOTE,
        }
        return payload, 0


def _print(payload: dict) -> None:
    print("護欄: " + payload["note"])
    print(
        "asof=%s price_max=%s family=%s n_ridge=%s wait=%s ∩進場=%s"
        % (payload["asof"], payload.get("price_max"), payload["family"],
           payload.get("n_ridge"), payload.get("n_wait"),
           payload.get("n_ridge_pass_entry"))
    )
    print("── 欄 A｜RankRidge 八窗平均 score Top10（相對強；score≠％；等回撤≠預測跌幅）──")
    for r in payload["ridge"]:
        extra = ""
        if r.get("dd20_pct") is not None:
            extra = "  dd20=%+.1f%% H5=%+.1f%% H10=%+.1f%%" % (
                r["dd20_pct"], r.get("h5_pct") or 0.0, r.get("h10_pct") or 0.0,
            )
        print("  " + r["line"] + extra)
    print("── 欄 B｜UP-PULL-v1 進場 strict（不足不補；路徑％≠未來）──")
    print("  做多 n=%d／k=%d" % (payload["n_long"], payload["k_entry"]))
    if not payload["entry_long"]:
        print("  （無）")
    for r in payload["entry_long"]:
        print("  " + pb._fmt_row(r))
    print("  做空 n=%d／k=%d（≠可空）" % (payload["n_short"], payload["k_entry"]))
    if not payload["entry_short"]:
        print("  （無）")
    for r in payload["entry_short"]:
        print("  " + pb._fmt_row(r))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="UP-PULL 標註 Ridge（copy-only dry-run）")
    ap.add_argument("--date", dest="asof", default=None)
    ap.add_argument("--k-ridge", type=int, default=10, dest="k_ridge")
    ap.add_argument("--k-entry", type=int, default=10, dest="k_entry")
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        rc = up._selftest()
        if rc != 0:
            return rc
        fake = asof_ready.classify_asof("2026-08-19", "2026-08-18", 1000)
        if fake != asof_ready.STATUS_FAKE_B3:
            print("✗ classify 假 B3", file=sys.stderr)
            return 1
        rc2 = main(["--date", "D"])
        if rc2 != 2:
            print("✗ 佔位符 D 應 rc=2", file=sys.stderr)
            return 1
        print("  ✓ classify 假 B3；CLI 佔位符拒")
        print("自測:全通過 ✓")
        return 0
    if not args.asof:
        print(__doc__)
        return 0
    err = asof_ready.date_arg_error(args.asof)
    if err:
        print(err, file=sys.stderr)
        return 2
    if int(args.k_ridge) < 1 or int(args.k_entry) < 1:
        print("✗ --k-ridge／--k-entry 須 ≥1", file=sys.stderr)
        return 2
    payload, rc = annotate(args.asof, k_ridge=int(args.k_ridge), k_entry=int(args.k_entry))
    if rc == asof_ready.RC_FAKE_B3:
        print("✗ 假 B3：禁止把還沒進庫的日當 as-of", file=sys.stderr)
        return rc
    if rc != 0:
        print("✗ status=%s" % payload.get("status"), file=sys.stderr)
        return rc
    _print(payload)
    path = args.json_out or ("/tmp/up-pull-annotate-ridge-%s.json" % args.asof)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    print("JSON %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

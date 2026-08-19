#!/usr/bin/env python
"""RIDGE-THEN-PB — 相對強／相對弱池，回撤／反彈近→遠（dry-run；零寫庫）。

🎯 這支在做什麼（白話）：最後交易日 RankRidge 八窗均分。做多＝相對強 Top k
   當池不剔除，依回撤近→遠。做空＝相對弱 Top k 當池不剔除，依反彈近→遠。
   過齊才標「可當進場條件」；否則做多「等回撤」／做空「等反彈」。
   做空欄＝條件排序，不是下單、不是可融券可成交。score ≠ 漲跌幅％。

執行指令矩陣:
  python scripts/probe_ridge_then_pb.py --selftest
  python scripts/probe_ridge_then_pb.py --date 2026-08-18 --k 10
  python scripts/probe_ridge_then_pb.py --date 2026-08-19  # rc=3
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

import probe_up_pull_annotate_ridge as ann
import probe_uptrend_pullback as pb
from augur.core import asof_ready, db
from augur.evaluation import uptrend_pullback as up
from augur.advisor.payload import _lookup_stock_names

NOTE = (
    "RIDGE-THEN-PB-v1；做多池＝相對強 Top k 不剔除／回撤近→遠；"
    "做空池＝相對弱 Top k 不剔除／反彈近→遠；過齊才可當進場條件；"
    "做空≠下單≠可空；score≠％；路徑％≠未來；"
    "dry-run 不寫 prediction_values；不改 standing 20,60"
)
VERSION = "RIDGE-THEN-PB-v1"
SHORT_DISCLAIMER = "做空欄是條件排序，不是下單、不是可融券可成交"


def _pct(log_ret):
    if log_ret is None:
        return None
    v = up.log_to_pct(log_ret)
    return None if v is None else round(v, 4)


def _long_rows(pool, by_sid, names):
    rows = []
    empty_bits = {"L-A": False, "L-B": False, "L-C": False, "L-D": False, "pass": False}
    for ridge_rank, (avg, sid, per) in enumerate(pool, 1):
        rec = by_sid.get(sid)
        bits = rec["long_bits"] if rec else empty_bits
        rets = rec["rets"] if rec else {}
        dd20 = None if rec is None else rec["dd20"]
        annot = up.wait_pullback_annot(bits)
        rows.append({
            "ridge_rank": ridge_rank,
            "sid": sid,
            "name": names.get(sid, ""),
            "avg_score": round(float(avg), 6),
            "per_h_score": {h: round(v, 6) for h, v in per.items()},
            "dd20_pct": None if dd20 is None else round(float(dd20) * 100.0, 4),
            "h5_pct": _pct(rets.get(5)),
            "h10_pct": _pct(rets.get(10)),
            "dd_dist": None if rec is None else round(up.dd20_dist_to_long_band(dd20), 6),
            "short_penalty": None if rec is None else round(
                up.short_window_rise_penalty(rets), 6,
            ),
            "tag": up.ridge_then_pb_tag(bits),
            "missing": annot["missing"],
            "reason_zh": annot["reason_zh"],
            "gates": bits,
            "_key": up.ridge_then_pb_sort_key(sid, rets, dd20, bits),
        })
    rows.sort(key=lambda r: r["_key"])
    return _finalize(rows, up.RIDGE_THEN_PB_ENTRY)


def _short_rows(pool, by_sid, names):
    rows = []
    empty_bits = {"S-A": False, "S-B": False, "S-C": False, "S-D": False, "pass": False}
    for ridge_rank, (avg, sid, per) in enumerate(pool, 1):
        rec = by_sid.get(sid)
        bits = rec["short_bits"] if rec else empty_bits
        rets = rec["rets"] if rec else {}
        bu20 = None if rec is None else rec["bu20"]
        annot = up.wait_bounce_annot(bits)
        rows.append({
            "ridge_rank": ridge_rank,
            "sid": sid,
            "name": names.get(sid, ""),
            "avg_score": round(float(avg), 6),
            "per_h_score": {h: round(v, 6) for h, v in per.items()},
            "bu20_pct": None if bu20 is None else round(float(bu20) * 100.0, 4),
            "h5_pct": _pct(rets.get(5)),
            "h10_pct": _pct(rets.get(10)),
            "bu_dist": None if rec is None else round(up.bu20_dist_to_short_band(bu20), 6),
            "fall_penalty": None if rec is None else round(
                up.short_window_fall_penalty(rets), 6,
            ),
            "tag": up.ridge_then_pb_short_tag(bits),
            "missing": annot["missing"],
            "reason_zh": annot["reason_zh"],
            "gates": bits,
            "_key": up.ridge_then_pb_short_sort_key(sid, rets, bu20, bits),
        })
    rows.sort(key=lambda r: r["_key"])
    return _finalize(rows, up.RIDGE_THEN_PB_ENTRY)


def _finalize(rows, entry_tag):
    out = []
    n_entry = 0
    for i, r in enumerate(rows, 1):
        r = dict(r)
        r.pop("_key", None)
        r["rank"] = i
        if r["tag"] == entry_tag:
            n_entry += 1
        out.append(r)
    return out, n_entry


def _pack(rows, n_entry):
    return {
        "n_pool": len(rows),
        "n_entry": n_entry,
        "n_wait": len(rows) - n_entry,
        "rows": rows,
    }


def probe(asof_iso: str, *, k: int) -> tuple[dict, int]:
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
        order, rrc = ann.ridge_avg_order(asof_iso)
        if rrc != 0:
            return {"asof": asof_iso, "status": "ridge_dry_run_fail", "note": NOTE}, rrc
        kk = int(k)
        long_pool = order[:kk]
        weak = order[-kk:] if len(order) >= kk else list(order)
        short_pool = list(reversed(weak))
        sids = [sid for _a, sid, _p in long_pool] + [sid for _a, sid, _p in short_pool]
        names = _lookup_stock_names(conn, cur, sids)
        long_rows, n_long_entry = _long_rows(long_pool, by_sid, names)
        short_rows, n_short_entry = _short_rows(short_pool, by_sid, names)
        long_pack = _pack(long_rows, n_long_entry)
        short_pack = _pack(short_rows, n_short_entry)
        short_pack["disclaimer"] = SHORT_DISCLAIMER
        payload = {
            "version": VERSION,
            "family": "RankRidge",
            "dry_run": True,
            "wrote_prediction_values": False,
            "standing_unchanged": True,
            "asof": asof_iso,
            "price_max": snap.get("price_max"),
            "k": kk,
            "long": long_pack,
            "short": short_pack,
            "n_pool": long_pack["n_pool"],
            "n_entry": long_pack["n_entry"],
            "n_wait": long_pack["n_wait"],
            "rows": long_rows,
            "funnel": funnel,
            "asof_status": snap["status"],
            "at_tip": snap.get("at_tip"),
            "note": NOTE,
        }
        return payload, 0


def _fmt_h(r):
    hs = r.get("per_h_score") or {}
    return "/".join("%.4f" % hs[str(h)] for h in up.H_TRACK if str(h) in hs)


def _print_long(payload: dict) -> None:
    pack = payload["long"]
    print(
        "做多 asof=%s price_max=%s n_pool=%s 可當進場=%s 等回撤=%s"
        % (payload["asof"], payload.get("price_max"), pack["n_pool"],
           pack["n_entry"], pack["n_wait"])
    )
    print("── 做多｜回撤近→遠（池＝Ridge 相對強 Top k；不剔除）──")
    for r in pack["rows"]:
        print(
            "  %2d  %s %s  均=%.4f  dd20=%+.1f%% H5=%+.1f%% H10=%+.1f%%  %s"
            % (
                r["rank"], r["sid"], r["name"], r["avg_score"],
                r.get("dd20_pct") or 0.0, r.get("h5_pct") or 0.0, r.get("h10_pct") or 0.0,
                r["tag"],
            )
        )
        why = r.get("reason_zh") or ""
        extra = ("  缺：" + why) if why else ""
        print("      Ridge原序=%s  八窗=%s%s" % (r["ridge_rank"], _fmt_h(r), extra))


def _print_short(payload: dict) -> None:
    pack = payload["short"]
    print(SHORT_DISCLAIMER)
    print(
        "做空 n_pool=%s 可當進場=%s 等反彈=%s"
        % (pack["n_pool"], pack["n_entry"], pack["n_wait"])
    )
    print("── 做空｜反彈近→遠（池＝Ridge 相對弱 Top k；不剔除；≠可空）──")
    for r in pack["rows"]:
        print(
            "  %2d  %s %s  均=%.4f  bu20=%+.1f%% H5=%+.1f%% H10=%+.1f%%  %s"
            % (
                r["rank"], r["sid"], r["name"], r["avg_score"],
                r.get("bu20_pct") or 0.0, r.get("h5_pct") or 0.0, r.get("h10_pct") or 0.0,
                r["tag"],
            )
        )
        why = r.get("reason_zh") or ""
        extra = ("  缺：" + why) if why else ""
        print("      Ridge弱序=%s  八窗=%s%s" % (r["ridge_rank"], _fmt_h(r), extra))


def _print(payload: dict) -> None:
    print("護欄: " + payload["note"])
    _print_long(payload)
    print()
    _print_short(payload)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="RIDGE-THEN-PB 做多回撤／做空反彈排序（dry-run）")
    ap.add_argument("--date", dest="asof", default=None)
    ap.add_argument("--k", type=int, default=10)
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
    if int(args.k) < 1:
        print("✗ --k 須 ≥1", file=sys.stderr)
        return 2
    payload, rc = probe(args.asof, k=int(args.k))
    if rc == asof_ready.RC_FAKE_B3:
        print("✗ 假 B3：禁止把還沒進庫的日當 as-of", file=sys.stderr)
        return rc
    if rc != 0:
        print("✗ status=%s" % payload.get("status"), file=sys.stderr)
        return rc
    _print(payload)
    path = args.json_out or ("/tmp/ridge-then-pb-%s.json" % args.asof)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    print("JSON %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""WATCH-PB — 全宇宙「已離高／短窗仍衝」觀察篩（dry-run；零寫庫）。

🎯 這支在做什麼（白話）：核心宇宙裡挑長窗仍上、已距 20 日高 −15%～−3%、
   結構未破、但 H5／H10 還沒雙負的名字。不是進場。不做 Ridge Top10 池。
   不做空可成交。score 不參與排序。路徑％不是未來漲跌幅。

執行指令矩陣:
  python scripts/probe_watch_pullback.py --selftest
  python scripts/probe_watch_pullback.py --date 2026-08-18 --k 10
  python scripts/probe_watch_pullback.py --date 2026-08-19  # rc=3
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

import probe_uptrend_pullback as pb
from augur.core import asof_ready, db
from augur.evaluation import uptrend_pullback as up
from augur.advisor.payload import _lookup_stock_names

NOTE = (
    "WATCH-PB-v1；全宇宙觀察篩；L-A∧L-C∧L-D∧¬L-B；"
    "一律等回撤／等反彈，不是進場；不做 Ridge 池；score 不排序；"
    "做空≠可空；路徑％≠未來；dry-run 不寫 prediction_values；不改 standing 20,60"
)
VERSION = up.WATCH_PB_VERSION
SHORT_DISCLAIMER = "做空觀察欄是條件排序，不是下單、不是可融券可成交"


def _pct(log_ret):
    if log_ret is None:
        return None
    v = up.log_to_pct(log_ret)
    return None if v is None else round(v, 4)


def _pub_long(r, names, rank):
    rets = r["rets"]
    return {
        "rank": rank,
        "sid": r["sid"],
        "name": names.get(r["sid"], ""),
        "tag": up.watch_long_tag(),
        "dd20_pct": round(float(r["dd20"]) * 100.0, 4),
        "h5_pct": _pct(rets.get(5)),
        "h10_pct": _pct(rets.get(10)),
        "rise_penalty": round(up.short_window_rise_penalty(rets), 6),
        "mean_h60_120_240": r["mu"],
        "gates": r["long_bits"],
        "cycle_position_252d": r["cyc"],
        "price_to_252d_high": r["p2h"],
    }


def _pub_short(r, names, rank):
    rets = r["rets"]
    return {
        "rank": rank,
        "sid": r["sid"],
        "name": names.get(r["sid"], ""),
        "tag": up.watch_short_tag(),
        "bu20_pct": round(float(r["bu20"]) * 100.0, 4),
        "h5_pct": _pct(rets.get(5)),
        "h10_pct": _pct(rets.get(10)),
        "fall_penalty": round(up.short_window_fall_penalty(rets), 6),
        "mean_h60_120_240": r["mu"],
        "gates": r["short_bits"],
        "cycle_position_252d": r["cyc"],
        "price_to_252d_high": r["p2h"],
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
        wlong = [r for r in scored if up.is_watch_long(r["long_bits"])]
        wshort = [r for r in scored if up.is_watch_short(r["short_bits"])]
        wlong.sort(key=lambda r: up.watch_long_sort_key(r["sid"], r["rets"]))
        wshort.sort(key=lambda r: up.watch_short_sort_key(r["sid"], r["rets"]))
        names = _lookup_stock_names(
            conn, cur, [r["sid"] for r in wlong + wshort],
        )
        long_all = [_pub_long(r, names, i) for i, r in enumerate(wlong, 1)]
        short_all = [_pub_short(r, names, i) for i, r in enumerate(wshort, 1)]
        kk = int(k)
        payload = {
            "version": VERSION,
            "dry_run": True,
            "wrote_prediction_values": False,
            "standing_unchanged": True,
            "asof": asof_iso,
            "price_max": snap.get("price_max"),
            "k": kk,
            "funnel": funnel,
            "n_watch_long": len(long_all),
            "n_watch_short": len(short_all),
            "n_watch_long_shown": min(kk, len(long_all)),
            "n_watch_short_shown": min(kk, len(short_all)),
            "intersect_entry_long": 0,
            "intersect_entry_short": 0,
            "long": long_all,
            "short": short_all,
            "long_shown": long_all[:kk],
            "short_shown": short_all[:kk],
            "asof_status": snap["status"],
            "at_tip": snap.get("at_tip"),
            "short_disclaimer": SHORT_DISCLAIMER,
            "note": NOTE,
        }
        return payload, 0


def _print(payload: dict) -> None:
    print("護欄: " + payload["note"])
    print(
        "asof=%s price_max=%s 觀察多=%s（列 %s） 觀察空=%s（列 %s）"
        % (
            payload["asof"], payload.get("price_max"),
            payload["n_watch_long"], payload["n_watch_long_shown"],
            payload["n_watch_short"], payload["n_watch_short_shown"],
        )
    )
    print("── 觀察多｜已離 20 日高、短窗仍衝（全宇宙；不是進場）──")
    for r in payload["long_shown"]:
        print(
            "  %2d  %s %s  dd20=%+.1f%% H5=%+.1f%% H10=%+.1f%%  %s"
            % (
                r["rank"], r["sid"], r["name"],
                r.get("dd20_pct") or 0.0, r.get("h5_pct") or 0.0, r.get("h10_pct") or 0.0,
                r["tag"],
            )
        )
    print()
    print(SHORT_DISCLAIMER)
    print("── 觀察空｜已離 20 日低、短窗仍弱（全宇宙；不是可空）──")
    for r in payload["short_shown"]:
        print(
            "  %2d  %s %s  bu20=%+.1f%% H5=%+.1f%% H10=%+.1f%%  %s"
            % (
                r["rank"], r["sid"], r["name"],
                r.get("bu20_pct") or 0.0, r.get("h5_pct") or 0.0, r.get("h10_pct") or 0.0,
                r["tag"],
            )
        )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="WATCH-PB 全宇宙觀察篩（dry-run）")
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
    path = args.json_out or ("/tmp/watch-pb-%s.json" % args.asof)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    print("JSON %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""BULL5 — 長線多頭 × 5 日回跌（dry-run；零寫庫）。

🎯 這支在做什麼（白話）：核心宇宙裡挑現價高於 10／20／40／60／90／120／240
   日前收、且近 5 日為負的名字。不是累積遞減、不是進場、不用 Ridge 分數。
   做空鏡像不是可空。路徑％不是未來漲跌幅。

執行指令矩陣:
  python scripts/probe_bull5.py --selftest
  python scripts/probe_bull5.py --date 2026-08-18 --k 10
  python scripts/probe_bull5.py --date 2026-08-19  # rc=3
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

import probe_uptrend_pullback as pb
from augur.advisor.payload import _lookup_stock_names
from augur.core import asof_ready, db
from augur.evaluation import bull5 as b5
from augur.evaluation import uptrend_pullback as up

NOTE = (
    "BULL5-v1；H10…H240 全＞0 ∧ H5＜0；不是累積遞減；"
    "條件≠可交易；做空≠可空；不用 Ridge score；"
    "不盜用可當進場條件；路徑％≠未來；dry-run 不寫 prediction_values；不改 standing 20,60"
)
VERSION = b5.VERSION
SHORT_DISCLAIMER = "做空欄是條件排序，不是下單、不是可融券可成交"


def _pct(log_ret):
    if log_ret is None:
        return None
    v = up.log_to_pct(log_ret)
    return None if v is None else round(v, 4)


def _pub(r, names, rank, *, side: str) -> dict:
    rets = r["rets"]
    return {
        "rank": rank,
        "sid": r["sid"],
        "name": names.get(r["sid"], ""),
        "side": side,
        "tag": b5.long_tag() if side == "long" else b5.short_tag(),
        "h5_pct": _pct(rets.get(5)),
        "h10_pct": _pct(rets.get(10)),
        "h20_pct": _pct(rets.get(20)),
        "h60_pct": _pct(rets.get(60)),
        "h120_pct": _pct(rets.get(120)),
        "h240_pct": _pct(rets.get(240)),
        "mean_h60_120_240": r["mu"],
        "mean_h60_120_240_pct": None if r["mu"] is None else round(up.log_to_pct(r["mu"]), 4),
        "dd20_pct": round(float(r["dd20"]) * 100.0, 4),
        "up_pull_pass": bool(r["long_bits"]["pass"]) if side == "long" else bool(r["short_bits"]["pass"]),
        "watch": (
            up.is_watch_long(r["long_bits"]) if side == "long"
            else up.is_watch_short(r["short_bits"])
        ),
        "gates": {
            "B5-A": b5.gate_long_a(rets) if side == "long" else b5.gate_short_a(rets),
            "B5-B": b5.gate_long_b(rets) if side == "long" else b5.gate_short_b(rets),
        },
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
        longs = [r for r in scored if b5.is_bull5_long(r["rets"])]
        shorts = [r for r in scored if b5.is_bull5_short(r["rets"])]
        longs.sort(key=lambda r: b5.long_sort_key(r["sid"], r["rets"]))
        shorts.sort(key=lambda r: b5.short_sort_key(r["sid"], r["rets"]))
        names = _lookup_stock_names(
            conn, cur, [r["sid"] for r in longs + shorts],
        )
        long_all = [_pub(r, names, i, side="long") for i, r in enumerate(longs, 1)]
        short_all = [_pub(r, names, i, side="short") for i, r in enumerate(shorts, 1)]
        kk = int(k)
        n_entry_l = sum(1 for r in long_all if r["up_pull_pass"])
        n_entry_s = sum(1 for r in short_all if r["up_pull_pass"])
        payload = {
            "version": VERSION,
            "dry_run": True,
            "wrote_prediction_values": False,
            "standing_unchanged": True,
            "asof": asof_iso,
            "price_max": snap.get("price_max"),
            "k": kk,
            "funnel_scored": funnel.get("scored"),
            "n_bull5_long": len(long_all),
            "n_bull5_short": len(short_all),
            "n_bull5_long_shown": min(kk, len(long_all)),
            "n_bull5_short_shown": min(kk, len(short_all)),
            "intersect_entry_long": n_entry_l,
            "intersect_entry_short": n_entry_s,
            "intersect_watch_long": sum(1 for r in long_all if r["watch"]),
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
        "asof=%s price_max=%s 做多=%s（列 %s） 做空=%s（列 %s） ∩進場多／空=%s／%s"
        % (
            payload["asof"], payload.get("price_max"),
            payload["n_bull5_long"], payload["n_bull5_long_shown"],
            payload["n_bull5_short"], payload["n_bull5_short_shown"],
            payload["intersect_entry_long"], payload["intersect_entry_short"],
        )
    )
    print("── 做多｜長線多頭、5日回跌（全宇宙；≠可交易）──")
    for r in payload["long_shown"]:
        print(
            "  %2d  %s %s  H5=%+.1f%% H10=%+.1f%% H20=%+.1f%% H240=%+.1f%%  %s"
            % (
                r["rank"], r["sid"], r["name"],
                r.get("h5_pct") or 0.0, r.get("h10_pct") or 0.0,
                r.get("h20_pct") or 0.0, r.get("h240_pct") or 0.0,
                r["tag"],
            )
        )
    print()
    print(SHORT_DISCLAIMER)
    print("── 做空｜長線空頭、5日反彈（全宇宙；≠可空）──")
    for r in payload["short_shown"]:
        print(
            "  %2d  %s %s  H5=%+.1f%% H10=%+.1f%% H20=%+.1f%% H240=%+.1f%%  %s"
            % (
                r["rank"], r["sid"], r["name"],
                r.get("h5_pct") or 0.0, r.get("h10_pct") or 0.0,
                r.get("h20_pct") or 0.0, r.get("h240_pct") or 0.0,
                r["tag"],
            )
        )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="BULL5 長線多頭×5日回跌（dry-run）")
    ap.add_argument("--date", dest="asof", default=None)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        rc = b5._selftest()
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
    path = args.json_out or ("/tmp/bull5-%s.json" % args.asof)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    print("JSON %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

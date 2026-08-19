#!/usr/bin/env python
"""UP-PULL 探針 — 最近 as-of 做多／做空硬閘名單（唯讀；strict；零寫庫）。

🎯 這支在做什麼（白話）：對 D≤價頂的核心宇宙，用已發生還原價路徑做
   長窗結構＋短窗進出四閘，過閘後排序輸出做多／做空表（上限 k，不足不補）。
   路徑％不是未來漲跌幅。做空≠可空。不寫 prediction_values。不用 RankRidge 分數排序進場欄。

執行指令矩陣:
  python scripts/probe_uptrend_pullback.py --selftest
  python scripts/probe_uptrend_pullback.py --date 2026-08-18 --side both --k 10 --policy strict
  python scripts/probe_uptrend_pullback.py --date 2026-08-19 --side both   # 價未進 → rc=3
"""
from __future__ import annotations

import argparse
import json
import math
import sys

import _bootstrap  # noqa: F401

from augur.core import asof_ready, db
from augur.evaluation import label as label_mod
from augur.evaluation import uptrend_pullback as up
from augur.catalog import world_concept
from augur.advisor.payload import _lookup_stock_names

ADJ_CONCEPT = "tw.daily_bar_adjusted"
NOTE = (
    "已發生路徑，不是未來漲跌幅；≠可交易；做空≠可融券可成交；"
    "policy=strict 不足不補；不取代 RankRidge standing 20,60"
)


def _logret(a, b):
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return math.log(b / a)


def _row_public(r: dict, rank: int) -> dict:
    rets = r["rets"]
    return {
        "rank": rank,
        "sid": r["sid"],
        "name": r.get("name") or "",
        "pct": {str(h): None if rets.get(h) is None else round(up.log_to_pct(rets[h]), 4)
                for h in up.H_TRACK},
        "dd20_pct": round(r["dd20"] * 100.0, 4),
        "bu20_pct": round(r["bu20"] * 100.0, 4),
        "cycle_position_252d": r["cyc"],
        "price_to_252d_high": r["p2h"],
        "mean_h60_120_240": r["mu"],
        "mean_h60_120_240_pct": None if r["mu"] is None else round(up.log_to_pct(r["mu"]), 4),
        "gates": r["gates"] if "gates" in r else {},
        "tier": "strict",
    }


def _fmt_row(r: dict) -> str:
    pct = r["pct"]
    path = " ".join("H%s=%+.1f%%" % (h, pct[str(h)]) for h in up.H_TRACK)
    extra = " dd20=%+.1f%% bu20=%+.1f%%" % (r["dd20_pct"], r["bu20_pct"])
    return (
        "%2d  %s %s  cyc=%.2f p2h=%.2f%s | %s"
        % (r["rank"], r["sid"], r["name"], r["cycle_position_252d"],
           r["price_to_252d_high"], extra, path)
    )


def score_universe(cur, conn, asof_iso: str):
    """唯讀：核心宇宙＠D 的八窗路徑＋四閘位元。回 (scored, funnel, snap, rc)。"""
    snap = asof_ready.snapshot(cur, asof_iso)
    if snap["status"] != asof_ready.STATUS_READY:
        return [], {}, snap, int(snap.get("rc") or asof_ready.rc_of(snap["status"]))
    if not snap.get("has_core"):
        return [], {}, {**snap, "status": "no_core"}, 2
    asof = asof_ready.as_date(asof_iso)
    adj = world_concept.resolve_sql(ADJ_CONCEPT, conn=conn)
    cal = [d for d in label_mod.full_calendar(conn) if d <= asof]
    if asof not in cal:
        return [], {}, {**snap, "status": "not_on_calendar"}, 2
    i0 = cal.index(asof)
    if i0 < 240:
        return [], {}, {**snap, "status": "calendar_too_short"}, 2
    anchors = {h: cal[i0 - h] for h in up.H_TRACK}
    look_20 = cal[i0 - 19: i0 + 1]
    cur.execute(
        "SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s",
        (asof,),
    )
    uni = [str(r[0]) for r in cur.fetchall()]
    dates = list({asof, *anchors.values(), *look_20})
    cur.execute(
        f"SELECT stock_id, date, close FROM {adj} "
        "WHERE stock_id = ANY(%s) AND date = ANY(%s)",
        (uni, dates),
    )
    px = {}
    for sid, d, c in cur.fetchall():
        px.setdefault(str(sid), {})[d] = float(c)
    cur.execute(
        """
        SELECT stock_id, feature, value FROM feature_values
         WHERE panel_date=%s AND stock_id = ANY(%s)
           AND feature = ANY(%s)
        """,
        (asof, uni, ["cycle_position_252d", "price_to_252d_high"]),
    )
    fv = {}
    for sid, f, v in cur.fetchall():
        fv.setdefault(str(sid), {})[f] = float(v)

    scored = []
    funnel = {
        "universe": len(uni),
        "scored": 0,
        "L-A": 0, "L-B": 0, "L-C": 0, "L-D": 0, "long_pass": 0,
        "S-A": 0, "S-B": 0, "S-C": 0, "S-D": 0, "short_pass": 0,
    }
    for sid in uni:
        p = px.get(sid, {})
        p0 = p.get(asof)
        if not p0:
            continue
        rets = {}
        ok = True
        for h in up.H_TRACK:
            r = _logret(p.get(anchors[h]), p0)
            if r is None:
                ok = False
                break
            rets[h] = r
        if not ok:
            continue
        highs = [p[d] for d in look_20 if d in p]
        if len(highs) < 20:
            continue
        hi20, lo20 = max(highs), min(highs)
        f = fv.get(sid, {})
        rec = {
            "sid": sid,
            "rets": rets,
            "dd20": p0 / hi20 - 1.0,
            "bu20": p0 / lo20 - 1.0,
            "cyc": f.get("cycle_position_252d"),
            "p2h": f.get("price_to_252d_high"),
            "mu": up.mean_rank_ret(rets),
        }
        rec["long_bits"] = up.pass_long(rets, rec["dd20"], rec["cyc"], rec["p2h"])
        rec["short_bits"] = up.pass_short(rets, rec["bu20"], rec["cyc"], rec["p2h"])
        scored.append(rec)
        funnel["scored"] += 1
        if rec["long_bits"]["L-A"]:
            funnel["L-A"] += 1
        if rec["long_bits"]["L-A"] and rec["long_bits"]["L-B"]:
            funnel["L-B"] += 1
        if rec["long_bits"]["L-A"] and rec["long_bits"]["L-B"] and rec["long_bits"]["L-C"]:
            funnel["L-C"] += 1
        if rec["long_bits"]["pass"]:
            funnel["L-D"] += 1
            funnel["long_pass"] += 1
        if rec["short_bits"]["S-A"]:
            funnel["S-A"] += 1
        if rec["short_bits"]["S-A"] and rec["short_bits"]["S-B"]:
            funnel["S-B"] += 1
        if rec["short_bits"]["S-A"] and rec["short_bits"]["S-B"] and rec["short_bits"]["S-C"]:
            funnel["S-C"] += 1
        if rec["short_bits"]["pass"]:
            funnel["S-D"] += 1
            funnel["short_pass"] += 1
    return scored, funnel, snap, 0


def probe(asof_iso: str, *, side: str, k: int) -> tuple[dict, int]:
    """連庫唯讀。回 (payload, rc)。"""
    with db.connect() as conn, conn.cursor() as cur:
        scored, funnel, snap, rc = score_universe(cur, conn, asof_iso)
        if rc != 0:
            return {
                "asof": asof_iso,
                "status": snap.get("status"),
                "price_max": snap.get("price_max"),
                "note": NOTE,
            }, rc
        asof_iso_ok = asof_iso
        longs = [r for r in scored if r["long_bits"]["pass"]]
        shorts = [r for r in scored if r["short_bits"]["pass"]]
        longs.sort(key=lambda r: up.long_sort_key(r["sid"], r["rets"], r["dd20"]))
        shorts.sort(key=lambda r: up.short_sort_key(r["sid"], r["rets"], r["bu20"]))
        longs = up.take_strict(longs, k)
        shorts = up.take_strict(shorts, k)
        names = _lookup_stock_names(
            conn, cur, [r["sid"] for r in longs + shorts],
        )
        for r in longs + shorts:
            r["name"] = names.get(r["sid"], "")

        long_out = []
        for i, r in enumerate(longs, 1):
            pub = _row_public(r, i)
            pub["side"] = "long"
            pub["gates"] = r["long_bits"]
            long_out.append(pub)
        short_out = []
        for i, r in enumerate(shorts, 1):
            pub = _row_public(r, i)
            pub["side"] = "short"
            pub["gates"] = r["short_bits"]
            short_out.append(pub)

        payload = {
            "version": up.VERSION,
            "policy": up.POLICY_STRICT,
            "k": int(k),
            "asof": asof_iso_ok,
            "price_max": snap.get("price_max"),
            "side": side,
            "funnel": funnel,
            "n_long": len(long_out) if side in ("long", "both") else 0,
            "n_short": len(short_out) if side in ("short", "both") else 0,
            "n_long_lt_k": (len(long_out) < int(k)) if side in ("long", "both") else None,
            "n_short_lt_k": (len(short_out) < int(k)) if side in ("short", "both") else None,
            "long": long_out if side in ("long", "both") else [],
            "short": short_out if side in ("short", "both") else [],
            "asof_status": snap["status"],
            "at_tip": snap.get("at_tip"),
            "note": NOTE,
        }
        return payload, 0


def _print_tables(payload: dict) -> None:
    print("護欄: " + payload["note"])
    print(
        "asof=%s price_max=%s version=%s policy=%s k=%d"
        % (payload["asof"], payload.get("price_max"), payload["version"],
           payload["policy"], payload["k"])
    )
    fn = payload.get("funnel") or {}
    print(
        "漏斗 宇宙=%s 可算八窗=%s | 多 L-A=%s L-B=%s L-C=%s 過齊=%s | "
        "空 S-A=%s S-B=%s S-C=%s 過齊=%s"
        % (fn.get("universe"), fn.get("scored"),
           fn.get("L-A"), fn.get("L-B"), fn.get("L-C"), fn.get("long_pass"),
           fn.get("S-A"), fn.get("S-B"), fn.get("S-C"), fn.get("short_pass"))
    )
    if payload.get("side") in ("long", "both"):
        print("── 做多 strict n=%d／k=%d（過閘全列；不是預測漲幅）──" % (
            payload["n_long"], payload["k"]))
        if not payload["long"]:
            print("  （無）")
        for r in payload["long"]:
            print("  " + _fmt_row(r))
    if payload.get("side") in ("short", "both"):
        print("── 做空 strict n=%d／k=%d（條件排序；≠可空）──" % (
            payload["n_short"], payload["k"]))
        if not payload["short"]:
            print("  （無）")
        for r in payload["short"]:
            print("  " + _fmt_row(r))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="UP-PULL 探針（唯讀 strict）")
    ap.add_argument("--date", dest="asof", default=None)
    ap.add_argument("--side", choices=("long", "short", "both"), default="both")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--policy", default="strict")
    ap.add_argument("--json-out", default=None, help="JSON 路徑（預設 /tmp/up-pull-{asof}-strict.json）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        rc = up._selftest()
        if rc != 0:
            return rc
        fake = asof_ready.classify_asof("2026-08-19", "2026-08-18", 1000)
        if fake != asof_ready.STATUS_FAKE_B3:
            print("✗ classify 08-19>08-18 應 fake_b3", file=sys.stderr)
            return 1
        rc2 = main(["--date", "D", "--side", "both"])
        if rc2 != 2:
            print("✗ 佔位符 D 應 rc=2", file=sys.stderr)
            return 1
        rc3 = main(["--date", "2026-08-18", "--policy", "soft-fill"])
        if rc3 != 2:
            print("✗ soft-fill 應 rc=2", file=sys.stderr)
            return 1
        print("  ✓ classify 假 B3（08-19>價頂 08-18）")
        print("  ✓ CLI 佔位符／soft-fill 拒")
        print("自測:全通過 ✓")
        return 0
    if not args.asof:
        print(__doc__)
        return 0
    err = asof_ready.date_arg_error(args.asof)
    if err:
        print(err, file=sys.stderr)
        return 2
    if args.policy != up.POLICY_STRICT:
        print("✗ 本殼只准 --policy strict（soft-fill／relax-A 另 GO）", file=sys.stderr)
        return 2
    if int(args.k) < 1:
        print("✗ --k 須 ≥1", file=sys.stderr)
        return 2
    payload, rc = probe(args.asof, side=args.side, k=int(args.k))
    if rc == asof_ready.RC_FAKE_B3:
        print("✗ 假 B3：禁止把還沒進庫的日當 as-of", file=sys.stderr)
        return rc
    if rc != 0:
        print("✗ status=%s" % payload.get("status"), file=sys.stderr)
        return rc
    _print_tables(payload)
    path = args.json_out or ("/tmp/up-pull-%s-strict.json" % args.asof)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    print("JSON %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

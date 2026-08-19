#!/usr/bin/env python
"""TREND-PB 探針 — 閉集 W1 路徑族／W2 指標族／W3 Elder 兩屏近似（唯讀；strict；零寫庫）。

🎯 這支在做什麼（白話）：對 D≤價頂的核心宇宙算八窗路徑（及 SMA／RSI／布林／週 MACD 柱），
   套指定族閘，輸出 n_pass／Top k 與相對 T01 重疊。路徑／指標不是未來漲跌幅。
   做空≠可空。SMA／RSI／MACD 不寫 feature_values。不寫 prediction_values。
   T07 ≠ 原書三屏（approx=elder_2screen_daily）。

執行指令矩陣:
  python scripts/probe_trend_pb_catalog.py --selftest
  python scripts/probe_trend_pb_catalog.py --date 2026-08-18 --wave W1 --families all --k 10
  python scripts/probe_trend_pb_catalog.py --date 2026-08-18 --wave W2 --families T03,T04,T05,T06,T08,T12,C04 --k 10
  python scripts/probe_trend_pb_catalog.py --date 2026-08-18 --wave W3 --families T07 --k 10
  python scripts/probe_trend_pb_catalog.py --date 2026-08-19 --wave W3 --families T07  # rc=3
"""
from __future__ import annotations

import argparse
import json
import math
import sys

import _bootstrap  # noqa: F401

from augur.core import asof_ready, db
from augur.evaluation import label as label_mod
from augur.evaluation import trend_pullback_catalog as cat
from augur.evaluation import uptrend_pullback as up
from augur.catalog import world_concept
from augur.advisor.payload import _lookup_stock_names

ADJ_CONCEPT = "tw.daily_bar_adjusted"
NOTE = (
    "已發生路徑／條件，不是未來漲跌幅；≠可交易；做空≠可融券可成交；"
    "policy=strict 不足不補；不取代 RankRidge standing 20,60；"
    "SMA／RSI／布林／MACD 只在探針現算、不倒 canonical 31；"
    "T07≠原書三屏 approx=elder_2screen_daily"
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
        "pct": {
            str(h): None if rets.get(h) is None else round(up.log_to_pct(rets[h]), 4)
            for h in up.H_TRACK
        },
        "dd20_pct": round(float(r["dd20"]) * 100.0, 4),
        "bu20_pct": round(float(r["bu20"]) * 100.0, 4),
        "cycle_position_252d": r["cyc"],
        "price_to_252d_high": r["p2h"],
        "sma20": r.get("sma20"),
        "sma60": r.get("sma60"),
        "sma200": r.get("sma200"),
        "px_sma20_pct": None if r.get("px_sma20") is None else round(float(r["px_sma20"]) * 100.0, 4),
        "rsi2": None if r.get("rsi2") is None else round(float(r["rsi2"]), 4),
        "rsi14": None if r.get("rsi14") is None else round(float(r["rsi14"]), 4),
        "bb_low": r.get("bb_low"),
        "bb_up": r.get("bb_up"),
        "at_hi20": bool(r.get("at_hi20")),
        "at_lo20": bool(r.get("at_lo20")),
        "weekly_n": r.get("weekly_n"),
        "macd_hist_weekly": None
        if r.get("macd_hist_weekly") is None
        else round(float(r["macd_hist_weekly"]), 6),
        "macd_hist_weekly_prev": None
        if r.get("macd_hist_weekly_prev") is None
        else round(float(r["macd_hist_weekly_prev"]), 6),
        "macd_hist_weekly_slope": None
        if r.get("macd_hist_weekly_slope") is None
        else round(float(r["macd_hist_weekly_slope"]), 6),
        "t07_approx": r.get("t07_approx"),
        "tier": "strict",
    }


def load_panel(cur, conn, asof_iso: str):
    """唯讀：核心宇宙＠D 的八窗路徑＋20 日高／低＋cycle／p2h。"""
    snap = asof_ready.snapshot(cur, asof_iso)
    if snap["status"] != asof_ready.STATUS_READY:
        return None, snap, int(snap.get("rc") or asof_ready.rc_of(snap["status"]))
    if not snap.get("has_core"):
        return None, {**snap, "status": "no_core"}, 2
    asof = asof_ready.as_date(asof_iso)
    adj = world_concept.resolve_sql(ADJ_CONCEPT, conn=conn)
    cal = [d for d in label_mod.full_calendar(conn) if d <= asof]
    if asof not in cal:
        return None, {**snap, "status": "not_on_calendar"}, 2
    i0 = cal.index(asof)
    if i0 < 240:
        return None, {**snap, "status": "calendar_too_short"}, 2
    anchors = {h: cal[i0 - h] for h in up.H_TRACK}
    look_20 = cal[i0 - 19: i0 + 1]
    hist_lo = max(0, i0 - 251)
    look_hist = cal[hist_lo: i0 + 1]
    cur.execute(
        "SELECT stock_id FROM core_universe_asof WHERE as_of_date=%s",
        (asof,),
    )
    uni = [str(r[0]) for r in cur.fetchall()]
    dates = list({asof, *anchors.values(), *look_20, *look_hist})
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
        need201 = look_hist[-201:] if len(look_hist) >= 201 else []
        if len(need201) == 201 and all(d in p for d in need201):
            if all(d in p for d in look_hist):
                closes = [p[d] for d in look_hist]
            else:
                closes = [p[d] for d in need201]
            rec = cat.fill_w2_indicators(rec, closes)
        else:
            rec["at_hi20"] = abs(rec["dd20"]) <= cat.AT_EXTREME_EPS
            rec["at_lo20"] = abs(rec["bu20"]) <= cat.AT_EXTREME_EPS
        scored.append(rec)
    return {"universe": uni, "scored": scored, "snap": snap}, snap, 0


def apply_family(fid: str, scored: list, *, k: int, side: str) -> dict:
    """過閘 → 排序 → strict 截 k。回 n_pass（截前）與 listed。"""
    longs = [r for r in scored if cat.pass_long(fid, r)]
    shorts = [r for r in scored if cat.pass_short(fid, r)]
    longs.sort(key=lambda r: cat.long_sort_key(fid, r))
    shorts.sort(key=lambda r: cat.short_sort_key(fid, r))
    npl, nps = len(longs), len(shorts)
    longs = up.take_strict(longs, k) if side in ("long", "both") else []
    shorts = up.take_strict(shorts, k) if side in ("short", "both") else []
    if side == "long":
        shorts, nps = [], 0
    if side == "short":
        longs, npl = [], 0
    return {
        "id": fid,
        "wave": cat.WAVE[fid],
        "n_pass_long": npl,
        "n_pass_short": nps,
        "n_long": len(longs),
        "n_short": len(shorts),
        "n_long_lt_k": len(longs) < int(k) if side in ("long", "both") else None,
        "n_short_lt_k": len(shorts) < int(k) if side in ("short", "both") else None,
        "_long_recs": longs,
        "_short_recs": shorts,
        "pass_long_sids": [r["sid"] for r in scored if cat.pass_long(fid, r)] if side in ("long", "both") else [],
        "pass_short_sids": [r["sid"] for r in scored if cat.pass_short(fid, r)] if side in ("short", "both") else [],
    }


def probe(asof_iso: str, *, families: list[str], k: int, side: str, wave: str) -> tuple[dict, int]:
    with db.connect() as conn, conn.cursor() as cur:
        panel, snap, rc = load_panel(cur, conn, asof_iso)
        if rc != 0:
            return {
                "asof": asof_iso,
                "status": (panel or snap or {}).get("status") or snap.get("status"),
                "price_max": snap.get("price_max"),
                "note": NOTE,
            }, rc
        scored = panel["scored"]
        fam_out = {}
        listed_sids = []
        for fid in families:
            block = apply_family(fid, scored, k=k, side=side)
            listed_sids.extend(r["sid"] for r in block["_long_recs"])
            listed_sids.extend(r["sid"] for r in block["_short_recs"])
            fam_out[fid] = block
        names = _lookup_stock_names(conn, cur, listed_sids)
        public = {}
        for fid, block in fam_out.items():
            long_pub = []
            for i, r in enumerate(block["_long_recs"], 1):
                r["name"] = names.get(r["sid"], "")
                long_pub.append(_row_public(r, i))
            short_pub = []
            for i, r in enumerate(block["_short_recs"], 1):
                r["name"] = names.get(r["sid"], "")
                short_pub.append(_row_public(r, i))
            public[fid] = {
                "id": fid,
                "wave": block["wave"],
                "approx": cat.T07_APPROX if fid == "T07" else None,
                "n_pass_long": block["n_pass_long"],
                "n_pass_short": block["n_pass_short"],
                "n_long": block["n_long"],
                "n_short": block["n_short"],
                "n_long_lt_k": block["n_long_lt_k"],
                "n_short_lt_k": block["n_short_lt_k"],
                "long": long_pub,
                "short": short_pub,
            }
        t01_pass_l = {r["sid"] for r in scored if cat.pass_long("T01", r)}
        t01_pass_s = {r["sid"] for r in scored if cat.pass_short("T01", r)}
        overlap = {"pass_long": {}, "pass_short": {}, "listed_long": {}}
        for fid, block in fam_out.items():
            if fid == "T01":
                continue
            overlap["pass_long"][fid] = cat.overlap_vs(t01_pass_l, set(block["pass_long_sids"]))
            overlap["pass_short"][fid] = cat.overlap_vs(t01_pass_s, set(block["pass_short_sids"]))
            overlap["listed_long"][fid] = cat.overlap_vs(
                t01_pass_l, {r["sid"] for r in block["_long_recs"]},
            )
        payload = {
            "version": cat.VERSION,
            "policy": cat.POLICY_STRICT,
            "wave": wave,
            "k": int(k),
            "asof": asof_iso,
            "price_max": snap.get("price_max"),
            "side": side,
            "families": list(families),
            "universe": len(panel["universe"]),
            "scored": len(scored),
            "n_T01_pass_long": len(t01_pass_l),
            "n_T01_pass_short": len(t01_pass_s),
            "by_family": public,
            "overlap_vs_T01": overlap,
            "asof_status": snap["status"],
            "at_tip": snap.get("at_tip"),
            "note": NOTE,
        }
        return payload, 0


def _fmt_listed(rows: list) -> str:
    if not rows:
        return "（無）"
    return "  ".join("%s %s" % (r["sid"], r["name"]) for r in rows)


def _print_tables(payload: dict) -> None:
    print("護欄: " + payload["note"])
    print(
        "asof=%s price_max=%s version=%s wave=%s k=%d scored=%s／宇宙=%s"
        % (payload["asof"], payload.get("price_max"), payload["version"],
           payload["wave"], payload["k"], payload.get("scored"), payload.get("universe"))
    )
    print("── 規模（n_pass＝過閘截前；n＝strict 上限 k）──")
    print("  id   n_pass多  n多  n_pass空  n空")
    for fid in payload["families"]:
        b = payload["by_family"][fid]
        print(
            "  %-4s %6d %4d  %6d %4d"
            % (fid, b["n_pass_long"], b["n_long"], b["n_pass_short"], b["n_short"])
        )
    ov = payload.get("overlap_vs_T01") or {}
    t01n = payload.get("n_T01_pass_long")
    print("── 相對 T01 過閘集合（做多；T01 pass=%s）──" % t01n)
    print("  id   交集  T01  該檔  Jaccard")
    for fid in payload["families"]:
        if fid == "T01":
            continue
        cell = (ov.get("pass_long") or {}).get(fid) or {}
        jac = cell.get("jaccard")
        jac_s = "—" if jac is None else ("%.3f" % jac)
        print(
            "  %-4s %4s %4s %4s  %s"
            % (fid, cell.get("n_inter"), t01n, cell.get("n_other"), jac_s)
        )
    for fid in payload["families"]:
        b = payload["by_family"][fid]
        print("── %s 做多 listed n=%d／pass=%d ──" % (fid, b["n_long"], b["n_pass_long"]))
        print("  " + _fmt_listed(b["long"]))
        print("── %s 做空 listed n=%d／pass=%d（≠可空）──" % (fid, b["n_short"], b["n_pass_short"]))
        print("  " + _fmt_listed(b["short"]))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="TREND-PB 探針（唯讀 strict；W1／W2／W3）")
    ap.add_argument("--date", dest="asof", default=None)
    ap.add_argument("--families", default="all")
    ap.add_argument("--wave", default="W1", choices=("W1", "W2", "W3"))
    ap.add_argument("--side", choices=("long", "short", "both"), default="both")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        rc = cat._selftest()
        if rc != 0:
            return rc
        fake = asof_ready.classify_asof("2026-08-19", "2026-08-18", 1000)
        if fake != asof_ready.STATUS_FAKE_B3:
            print("✗ classify 假 B3", file=sys.stderr)
            return 1
        rc2 = main(["--date", "D", "--wave", "W1", "--families", "all"])
        if rc2 != 2:
            print("✗ 佔位符 D 應 rc=2", file=sys.stderr)
            return 1
        rc3 = main(["--date", "2026-08-18", "--wave", "W1", "--families", "T05"])
        if rc3 != 2:
            print("✗ T05＠W1 應 rc=2", file=sys.stderr)
            return 1
        rc4 = main(["--date", "2026-08-18", "--wave", "W2", "--families", "T01"])
        if rc4 != 2:
            print("✗ T01＠W2 應 rc=2", file=sys.stderr)
            return 1
        rc5 = main(["--date", "2026-08-18", "--wave", "W2", "--families", "T07"])
        if rc5 != 2:
            print("✗ T07＠W2 應 rc=2", file=sys.stderr)
            return 1
        rc6 = main(["--date", "2026-08-18", "--wave", "W3", "--families", "T05"])
        if rc6 != 2:
            print("✗ T05＠W3 應 rc=2", file=sys.stderr)
            return 1
        print("  ✓ classify 假 B3；CLI 佔位符／跨波次拒")
        print("自測:全通過 ✓")
        return 0
    if not args.asof:
        print(__doc__)
        return 0
    err = asof_ready.date_arg_error(args.asof)
    if err:
        print(err, file=sys.stderr)
        return 2
    if args.wave not in ("W1", "W2", "W3"):
        print("✗ 本殼只准 --wave W1／W2／W3（W4＋另 GO）", file=sys.stderr)
        return 2
    ids, ferr = cat.parse_families(args.families, wave=args.wave)
    if ferr:
        print(ferr, file=sys.stderr)
        return 2
    if int(args.k) < 1:
        print("✗ --k 須 ≥1", file=sys.stderr)
        return 2
    payload, rc = probe(
        args.asof, families=ids, k=int(args.k), side=args.side, wave=args.wave,
    )
    if rc == asof_ready.RC_FAKE_B3:
        print("✗ 假 B3：禁止把還沒進庫的日當 as-of", file=sys.stderr)
        return rc
    if rc != 0:
        print("✗ status=%s" % payload.get("status"), file=sys.stderr)
        return rc
    _print_tables(payload)
    path = args.json_out or ("/tmp/trend-pb-%s-%s.json" % (args.asof, args.wave))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    print("JSON %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

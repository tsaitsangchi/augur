#!/usr/bin/env python
"""RIDGE-THEN-PB — 相對強／相對弱池，回撤／反彈近→遠。

🎯 這支在做什麼（白話）：最後交易日（庫裡最後一盤還原價，不是日曆今天）RankRidge 八窗。
   做多＝相對強 Top k 當池不剔除，依回撤近→遠。做空＝相對弱 Top k 當池不剔除，依反彈近→遠。
   過齊才標「可當進場條件」；否則做多「等回撤」／做空「等反彈」。
   `--persist` 只把可當進場條件寫進 `ridge_then_pb_entry`，已實現才填 t+1 抱 30 日報酬。
   `--from-pv` 讀同日八窗分數；`--persist-long-close` 做多過齊者以該日還原收盤寫入 `ridge_then_pb_long_buy`。
   做空欄＝條件排序，不是下單、不是可融券可成交。score ≠ 漲跌幅％。

執行指令矩陣:
  python scripts/probe_ridge_then_pb.py --selftest
  python scripts/probe_ridge_then_pb.py --last-td --k 10
  python scripts/probe_ridge_then_pb.py --last-td --persist
  python scripts/probe_ridge_then_pb.py --date 2026-08-20  # rc=3
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

import probe_up_pull_annotate_ridge as ann
import probe_uptrend_pullback as pb
from augur.core import asof_ready, db
from augur.evaluation import ridge_then_pb_store as store
from augur.evaluation import uptrend_pullback as up
from augur.advisor.payload import _lookup_stock_names

NOTE = (
    "RIDGE-THEN-PB-v1；做多池＝相對強 Top k 不剔除／回撤近→遠；"
    "做空池＝相對弱 Top k 不剔除／反彈近→遠；過齊才可當進場條件；"
    "做空≠下單≠可空；score≠％；路徑％≠未來；"
    "asof＝PriceAdj 最後交易日不是日曆今天；不改 standing 20,60"
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
        wpass = up.path_window_pass(rets, side="long")
        rows.append({
            "ridge_rank": ridge_rank,
            "sid": sid,
            "name": names.get(sid, ""),
            "avg_score": round(float(avg), 6),
            "per_h_score": {h: round(v, 6) for h, v in per.items()},
            "dd20_pct": None if dd20 is None else round(float(dd20) * 100.0, 4),
            "h5_pct": _pct(rets.get(5)),
            "h10_pct": _pct(rets.get(10)),
            "path_pct": {str(h): _pct(rets.get(h)) for h in up.H_TRACK},
            "window_pass": wpass,
            "window_pass_zh": up.format_window_pass(wpass),
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
        wpass = up.path_window_pass(rets, side="short")
        rows.append({
            "ridge_rank": ridge_rank,
            "sid": sid,
            "name": names.get(sid, ""),
            "avg_score": round(float(avg), 6),
            "per_h_score": {h: round(v, 6) for h, v in per.items()},
            "bu20_pct": None if bu20 is None else round(float(bu20) * 100.0, 4),
            "h5_pct": _pct(rets.get(5)),
            "h10_pct": _pct(rets.get(10)),
            "path_pct": {str(h): _pct(rets.get(h)) for h in up.H_TRACK},
            "window_pass": wpass,
            "window_pass_zh": up.format_window_pass(wpass),
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


def ridge_avg_from_pv(conn, asof_iso: str) -> tuple[list[tuple[float, str, dict]], int]:
    """同日 RankRidge 八窗分數（prediction_values；asof_snapshot＝panel_date）。缺窗 → ([], 2)。"""
    asof = asof_ready.as_date(asof_iso)
    need = list(up.H_TRACK)
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH picked AS (
              SELECT DISTINCT ON (horizon) model_id, horizon
                FROM model_registry
               WHERE family = 'RankRidge'
                 AND asof_snapshot = %s
                 AND horizon = ANY(%s)
               ORDER BY horizon, created_at DESC
            )
            SELECT p.horizon, pv.stock_id, pv.score
              FROM picked p
              JOIN prediction_values pv
                ON pv.model_id = p.model_id
               AND pv.panel_date = %s
            """,
            (asof, need, asof),
        )
        raw = cur.fetchall()
    by_h: dict[int, dict[str, float]] = {}
    for h, sid, sc in raw:
        by_h.setdefault(int(h), {})[str(sid)] = float(sc)
    if any(h not in by_h or not by_h[h] for h in need):
        return [], 2
    common = set.intersection(*(set(by_h[h]) for h in need))
    if not common:
        return [], 2
    out = []
    for sid in common:
        xs = [by_h[h][sid] for h in need]
        per = {str(h): by_h[h][sid] for h in need}
        out.append((sum(xs) / len(xs), sid, per))
    out.sort(key=lambda t: (-t[0], t[1]))
    return out, 0


def probe(asof_iso: str, *, k: int, source: str = "dry_run") -> tuple[dict, int]:
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
        if source == "pv":
            order, rrc = ridge_avg_from_pv(conn, asof_iso)
        else:
            order, rrc = ann.ridge_avg_order(asof_iso)
        if rrc != 0:
            return {"asof": asof_iso, "status": "ridge_dry_run_fail" if source != "pv"
                    else "ridge_pv_incomplete", "note": NOTE}, rrc
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
        if source == "pv":
            stamps = {str(h): asof_iso for h in up.H_TRACK}
        else:
            stamps = store.model_asofs(asof_iso)
        payload = {
            "version": VERSION,
            "family": "RankRidge",
            "wrote_prediction_values": False,
            "standing_unchanged": True,
            "score_source": source,
            "asof": asof_iso,
            "price_max": snap.get("price_max"),
            "last_td": snap.get("price_max"),
            "k": kk,
            "hold_td": store.HOLD_TD,
            "model_asofs": stamps,
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
            "  %2d  %s %s  回撤=%+.1f%%  H5=%+.1f%% H10=%+.1f%%  %s"
            % (
                r["rank"], r["sid"], r["name"],
                r.get("dd20_pct") or 0.0, r.get("h5_pct") or 0.0, r.get("h10_pct") or 0.0,
                r["tag"],
            )
        )
        why = r.get("reason_zh") or ""
        extra = ("  缺：" + why) if why else ""
        print("      窗 %s%s" % (r.get("window_pass_zh") or "", extra))


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
            "  %2d  %s %s  反彈=%+.1f%%  H5=%+.1f%% H10=%+.1f%%  %s"
            % (
                r["rank"], r["sid"], r["name"],
                r.get("bu20_pct") or 0.0, r.get("h5_pct") or 0.0, r.get("h10_pct") or 0.0,
                r["tag"],
            )
        )
        why = r.get("reason_zh") or ""
        extra = ("  缺：" + why) if why else ""
        print("      窗 %s%s" % (r.get("window_pass_zh") or "", extra))


def _print_hold(payload: dict) -> None:
    h = payload.get("hold") or {}
    print()
    print("── 可當進場條件 → t+1 抱 %s 日 ──" % payload.get("hold_td"))
    n = int(h.get("n_long") or 0) + int(h.get("n_short") or 0)
    if n == 0:
        print("  （本 asof 無過齊列，30 日樣本＝0）")
        return
    print("  落庫 %s  多=%s 空=%s 已實現30日=%s" % (
        h.get("table"), h.get("n_long"), h.get("n_short"), h.get("n_realized_30")))
    for side in ("long", "short"):
        pack = payload.get(side) or {}
        for r in pack.get("rows") or []:
            if r.get("tag") != up.RIDGE_THEN_PB_ENTRY:
                continue
            hr = (h.get("returns") or {}).get(r["sid"]) or {}
            if hr.get("realized"):
                sign = -1.0 if side == "short" else 1.0
                pct = (hr.get("ret_30_pct") or 0.0) * sign
                print("  %s %s %s  進=%s 出=%s  30日毛=%+.2f%%" % (
                    side, r["sid"], r["name"], hr.get("entry_date"), hr.get("exit_date"), pct))
            else:
                print("  %s %s %s  進=%s  30日未實現（不編造）" % (
                    side, r["sid"], r["name"], hr.get("entry_date")))


def _print(payload: dict) -> None:
    print("護欄: " + payload["note"])
    print("model_asofs=%s" % payload.get("model_asofs"))
    _print_long(payload)
    print()
    _print_short(payload)
    if payload.get("hold"):
        _print_hold(payload)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="RIDGE-THEN-PB 做多回撤／做空反彈排序")
    ap.add_argument("--date", dest="asof", default=None)
    ap.add_argument("--last-td", action="store_true",
                    help="asof＝庫裡 PriceAdj 最後交易日（不是日曆今天）")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--persist", action="store_true",
                    help="可當進場條件寫入 ridge_then_pb_entry，已實現才填 30 日報酬")
    ap.add_argument("--from-pv", action="store_true",
                    help="八窗分數讀同日 prediction_values，不 dry-run 重算")
    ap.add_argument("--persist-long-close", action="store_true",
                    help="做多過齊者寫入 ridge_then_pb_long_buy（該日還原收盤）")
    ap.add_argument("--persist-short-close", action="store_true",
                    help="做空過齊者寫入 ridge_then_pb_short_sell（該日還原收盤；≠可空）")
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        rc = up._selftest()
        if rc != 0:
            return rc
        rc = store._selftest()
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
    asof = args.asof
    if args.last_td:
        with db.connect() as conn, conn.cursor() as cur:
            tip = asof_ready.taiex_price_max(cur)
        if tip is None:
            print("✗ 無價", file=sys.stderr)
            return 4
        asof = tip.isoformat()
    if not asof:
        print(__doc__)
        return 0
    err = asof_ready.date_arg_error(asof)
    if err:
        print(err, file=sys.stderr)
        return 2
    if int(args.k) < 1:
        print("✗ --k 須 ≥1", file=sys.stderr)
        return 2
    payload, rc = probe(asof, k=int(args.k), source="pv" if args.from_pv else "dry_run")
    if rc == asof_ready.RC_FAKE_B3:
        print("✗ 假 B3：禁止把還沒進庫的日當 as-of", file=sys.stderr)
        return rc
    if rc != 0:
        print("✗ status=%s" % payload.get("status"), file=sys.stderr)
        return rc
    if args.persist:
        with db.connect() as conn:
            payload["hold"] = store.persist_entries(conn, payload)
        payload["persisted"] = True
    else:
        payload["persisted"] = False
        entry_sids = [
            r["sid"] for side in ("long", "short")
            for r in (payload.get(side) or {}).get("rows") or []
            if r.get("tag") == up.RIDGE_THEN_PB_ENTRY
        ]
        with db.connect() as conn:
            rets = store.attach_hold_returns(conn, asof, entry_sids)
        payload["hold"] = {
            "table": None,
            "n_long": payload["long"]["n_entry"],
            "n_short": payload["short"]["n_entry"],
            "n_realized_30": sum(1 for v in rets.values() if v.get("realized")),
            "returns": rets,
        }
    if args.persist_long_close:
        from augur.catalog import world_concept
        sids = [r["sid"] for r in (payload.get("long") or {}).get("rows") or []]
        with db.connect() as conn:
            adj = world_concept.resolve_sql("tw.daily_bar_adjusted", conn=conn)
            closes = {}
            if sids:
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT stock_id, close FROM {adj} "
                        "WHERE date=%s AND stock_id=ANY(%s) AND close>0",
                        (asof_ready.as_date(asof), sids),
                    )
                    closes = {str(s): float(c) for s, c in cur.fetchall()}
            payload["long_close"] = store.persist_long_close_buys(conn, payload, closes)
    if args.persist_short_close:
        from augur.catalog import world_concept
        sids = [r["sid"] for r in (payload.get("short") or {}).get("rows") or []]
        with db.connect() as conn:
            adj = world_concept.resolve_sql("tw.daily_bar_adjusted", conn=conn)
            closes = {}
            if sids:
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT stock_id, close FROM {adj} "
                        "WHERE date=%s AND stock_id=ANY(%s) AND close>0",
                        (asof_ready.as_date(asof), sids),
                    )
                    closes = {str(s): float(c) for s, c in cur.fetchall()}
            payload["short_close"] = store.persist_short_close_sells(conn, payload, closes)
    _print(payload)
    path = args.json_out or ("/tmp/ridge-then-pb-%s.json" % asof)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    print("JSON %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

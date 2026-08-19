#!/usr/bin/env python
"""TWIN-EX 格子 — 3017／2395 進出（dry-run；不要抱牢；零寫庫）。

🎯 這支在做什麼（白話）：對兩檔重跑進場×出場全格，訓練 2024、保留
   2025-01～2026-06。合格組用訓練複利選，不把 OOS 最長持有當冠。
   抱牢只對照。未扣成本與成本地板兩欄。≠可交易、≠全宇宙。

執行指令矩陣:
  python scripts/probe_twin_ex.py --selftest
  python scripts/probe_twin_ex.py --tip 2026-08-18 --sids 3017,2395
  python scripts/probe_twin_ex.py --tip 2026-08-19  # rc=3
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date

import _bootstrap  # noqa: F401

from augur.advisor.payload import _lookup_stock_names
from augur.catalog import world_concept
from augur.core import asof_ready, db
from augur.evaluation import label as label_mod
from augur.evaluation import twin_ex as tx

ADJ_CONCEPT = "tw.daily_bar_adjusted"
NOTE = (
    "TWIN-EX-v1；不要抱牢；IS=2024 OOS=2025-01..2026-06；"
    "禁 OOS 最長持有當冠；兩檔≠宇宙；條件≠可交易；"
    "dry-run 不寫 prediction_values；不改 standing 20,60"
)
NAMES_FALLBACK = {"3017": "奇鋐", "2395": "研華"}


def _parse_sids(raw: str) -> list[str]:
    out = []
    for p in (raw or "").split(","):
        s = p.strip()
        if s:
            out.append(s)
    return out


def _load_cost(cur) -> float:
    try:
        cur.execute(
            "SELECT value FROM direction_product_config WHERE key='cost_roundtrip'"
        )
        row = cur.fetchone()
        if row is not None and row[0] is not None:
            return float(row[0])
    except Exception:
        pass
    return tx.COST_ROUNDTRIP_DEFAULT


def _closes_for(sid: str, cal: list, px: dict) -> list:
    return [px.get(sid, {}).get(d) for d in cal]


def _run_sid(sid, cal, px, flags, max_i, cost):
    closes = _closes_for(sid, cal, px)
    fl = flags[sid]
    cells = []
    trades_by = {}
    for entry_id in tx.ENTRY_IDS:
        for exit_id in tx.EXIT_IDS:
            trades = tx.simulate_trades(
                fl[entry_id], closes, cal, exit_id,
                h5_neg=fl["h5_neg"], la_fail=fl["la_fail"], max_i=max_i,
            )
            trades_by[(entry_id, exit_id)] = trades
            cells.append(tx.summarize_cell(
                trades, entry_id=entry_id, exit_id=exit_id, cost=cost, sid=sid,
            ))
    bh = {
        "is": tx.buy_hold_pct(closes, cal, tx.IS_START, tx.IS_END),
        "oos": tx.buy_hold_pct(closes, cal, tx.OOS_START, tx.OOS_END),
        "origin_tip": tx.buy_hold_pct(closes, cal, tx.IS_START, cal[max_i]),
    }
    return cells, trades_by, bh


def _pool_trades(by_sid, entry_id, exit_id):
    rows = []
    for sid, tb in by_sid.items():
        for t in tb[(entry_id, exit_id)]:
            rows.append({**t, "sid": sid})
    rows.sort(key=lambda t: (t["signal"], t["sid"]))
    return rows


def _pub_trade(t):
    return {
        "sid": t.get("sid"),
        "signal": t["signal"].isoformat() if hasattr(t["signal"], "isoformat") else str(t["signal"]),
        "entry": t["entry"].isoformat() if hasattr(t["entry"], "isoformat") else str(t["entry"]),
        "exit": t["exit"].isoformat() if hasattr(t["exit"], "isoformat") else str(t["exit"]),
        "hold_td": t["hold_td"],
        "ret_pct": round(float(t["ret"]) * 100.0, 4),
    }


def _pub_cell(c):
    def _win(w):
        out = dict(w)
        for k in ("compound_pct", "compound_cost_pct", "mean_hold", "mean_ret_pct"):
            if out.get(k) is not None:
                out[k] = round(float(out[k]), 4)
        return out
    return {
        "sid": c.get("sid"),
        "entry": c["entry"],
        "exit": c["exit"],
        "nominal_hold": c["nominal_hold"],
        "bh_like": c["bh_like"],
        "contrast_only": c["contrast_only"],
        "qualified": c["qualified"],
        "is": _win(c["is"]),
        "oos": _win(c["oos"]),
        "n_trades": c["n_trades"],
    }


def probe(tip_iso: str, sids: list[str]) -> tuple[dict, int]:
    with db.connect() as conn, conn.cursor() as cur:
        snap = asof_ready.snapshot(cur, tip_iso)
        if snap["status"] == asof_ready.STATUS_FAKE_B3:
            return {
                "tip": tip_iso,
                "status": snap.get("status"),
                "price_max": snap.get("price_max"),
                "note": NOTE,
            }, asof_ready.RC_FAKE_B3
        if snap["status"] != asof_ready.STATUS_READY:
            return {
                "tip": tip_iso,
                "status": snap.get("status"),
                "price_max": snap.get("price_max"),
                "note": NOTE,
            }, int(snap.get("rc") or asof_ready.rc_of(snap["status"]))
        tip = asof_ready.as_date(tip_iso)
        adj = world_concept.resolve_sql(ADJ_CONCEPT, conn=conn)
        cal = [d for d in label_mod.full_calendar(conn) if d <= tip]
        if tip not in cal:
            return {"tip": tip_iso, "status": "not_on_calendar", "note": NOTE}, 2
        max_i = cal.index(tip)
        cur.execute(
            f"SELECT stock_id, date, close FROM {adj} "
            "WHERE stock_id = ANY(%s) AND date <= %s AND close > 0",
            (sids, tip),
        )
        px = {}
        for sid, d, c in cur.fetchall():
            px.setdefault(str(sid), {})[d] = float(c)
        names = _lookup_stock_names(conn, cur, sids) or {}
        cost = _load_cost(cur)

    flags = {}
    for sid in sids:
        closes = _closes_for(sid, cal, px)
        flags[sid] = tx.daily_flags(closes)

    per_cells = {}
    trades_by_sid = {}
    bh_by_sid = {}
    for sid in sids:
        cells, tb, bh = _run_sid(sid, cal, px, flags, max_i, cost)
        per_cells[sid] = cells
        trades_by_sid[sid] = tb
        bh_by_sid[sid] = bh

    pooled = []
    pooled_trades = {}
    for entry_id in tx.ENTRY_IDS:
        for exit_id in tx.EXIT_IDS:
            rows = _pool_trades(trades_by_sid, entry_id, exit_id)
            pooled_trades[(entry_id, exit_id)] = rows
            pooled.append(tx.summarize_cell(
                rows, entry_id=entry_id, exit_id=exit_id, cost=cost, sid="pooled",
            ))
    champ = tx.pick_champion(pooled)

    per_name_champ = {}
    if champ.get("cell"):
        e, x = champ["cell"]["entry"], champ["cell"]["exit"]
        for sid in sids:
            cell = next(c for c in per_cells[sid] if c["entry"] == e and c["exit"] == x)
            per_name_champ[sid] = {
                "is_pct": cell["is"]["compound_pct"],
                "oos_pct": cell["oos"]["compound_pct"],
                "is_n": cell["is"]["n"],
                "oos_n": cell["oos"]["n"],
                "is_pos": (cell["is"]["compound_pct"] or 0) > 0,
                "oos_pos": (cell["oos"]["compound_pct"] or 0) > 0,
            }
        both_ok = all(
            v["is_pos"] and v["oos_pos"] and v["is_n"] >= 1 and v["oos_n"] >= 1
            for v in per_name_champ.values()
        )
    else:
        both_ok = False

    champ_pub = {
        "found": champ["found"],
        "n_qualified": champ["n_qualified"],
        "hypothesis": champ["hypothesis"],
        "hypothesis_is_champion": champ["hypothesis_is_champion"],
        "per_name_both_positive": both_ok,
        "confirmed": bool(champ["hypothesis_is_champion"] and both_ok),
        "qualified_order": champ["qualified_order"],
        "cell": None if champ["cell"] is None else _pub_cell(champ["cell"]),
        "per_name": per_name_champ,
    }

    payload = {
        "version": tx.VERSION,
        "dry_run": True,
        "wrote_prediction_values": False,
        "standing_unchanged": True,
        "tip": tip.isoformat(),
        "price_max": snap.get("price_max"),
        "sids": sids,
        "names": {s: names.get(s) or NAMES_FALLBACK.get(s, "") for s in sids},
        "is": {"start": tx.IS_START.isoformat(), "end": tx.IS_END.isoformat()},
        "oos": {"start": tx.OOS_START.isoformat(), "end": tx.OOS_END.isoformat()},
        "cost_roundtrip": cost,
        "asof_status": snap["status"],
        "champion": champ_pub,
        "grid_pooled": [_pub_cell(c) for c in pooled],
        "grid_per_sid": {sid: [_pub_cell(c) for c in per_cells[sid]] for sid in sids},
        "buy_hold": {
            sid: {
                k: None if v is None else {**v, "pct": round(v["pct"], 4)}
                for k, v in bh_by_sid[sid].items()
            }
            for sid in sids
        },
        "trades_champion": [
            _pub_trade(t) for t in (
                pooled_trades.get((champ["cell"]["entry"], champ["cell"]["exit"]), [])
                if champ.get("cell") else []
            )
            if tx.in_is(t["signal"]) or tx.in_oos(t["signal"])
        ],
        "note": NOTE,
    }
    return payload, 0


def _fmt_pct(v):
    if v is None:
        return "—"
    return "%+.1f" % float(v)


def _print(payload: dict) -> None:
    print("護欄: " + payload["note"])
    print(
        "tip=%s cost=%.3f%% 兩檔=%s"
        % (payload["tip"], float(payload["cost_roundtrip"]) * 100.0, ",".join(payload["sids"]))
    )
    print("── 兩檔合計（交易序列連乘；非同時持有組合）──")
    print(
        "%-10s %-10s %7s %11s %11s %7s %11s %11s %s"
        % ("進場", "出場", "IS n", "IS％", "IS成本％", "OOS n", "OOS％", "OOS成本％", "尺")
    )
    for c in payload["grid_pooled"]:
        tag = []
        if c["qualified"]:
            tag.append("合格")
        if c["contrast_only"]:
            tag.append("對照不當冠")
        elif c["bh_like"]:
            tag.append("偏抱牢")
        print(
            "%-10s %-10s %7d %11s %11s %7d %11s %11s %s"
            % (
                c["entry"], c["exit"],
                c["is"]["n"], _fmt_pct(c["is"]["compound_pct"]),
                _fmt_pct(c["is"]["compound_cost_pct"]),
                c["oos"]["n"], _fmt_pct(c["oos"]["compound_pct"]),
                _fmt_pct(c["oos"]["compound_cost_pct"]),
                " ".join(tag) or "淘汰",
            )
        )
    ch = payload["champion"]
    print()
    if not ch["found"]:
        print("合格組空；工作假說 E-charge×T5 未證實（也沒有替代冠軍）。")
        return
    cell = ch["cell"]
    print(
        "不要抱牢冠軍（主鍵 IS 複利）：%s × %s  IS %+0.1f%%／n=%s  OOS %+0.1f%%／n=%s"
        % (
            cell["entry"], cell["exit"],
            cell["is"]["compound_pct"], cell["is"]["n"],
            cell["oos"]["compound_pct"], cell["oos"]["n"],
        )
    )
    print(
        "工作假說 E-charge×T5：%s；分檔兩窗都正：%s；本格可稱為證實：%s"
        % (
            "仍是冠軍" if ch["hypothesis_is_champion"] else "被推翻",
            "是" if ch["per_name_both_positive"] else "否",
            "是（僅此兩檔格子）" if ch["confirmed"] else "否",
        )
    )
    print("分檔（冠軍規則）：")
    for sid, v in ch["per_name"].items():
        nm = payload["names"].get(sid, "")
        print(
            "  %s %s  IS n=%s %+0.1f%%  OOS n=%s %+0.1f%%"
            % (sid, nm, v["is_n"], v["is_pct"] or 0.0, v["oos_n"], v["oos_pct"] or 0.0)
        )
    print("抱牢對照（不是目標）：")
    for sid, bh in payload["buy_hold"].items():
        nm = payload["names"].get(sid, "")
        def _bh(x):
            return "—" if x is None else "%+.1f%%" % x["pct"]
        print(
            "  %s %s  IS %s  OOS %s  起源→頂 %s"
            % (sid, nm, _bh(bh.get("is")), _bh(bh.get("oos")), _bh(bh.get("origin_tip")))
        )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="TWIN-EX 兩檔進出格子（dry-run）")
    ap.add_argument("--tip", dest="tip", default=None)
    ap.add_argument("--date", dest="tip_alias", default=None, help="同 --tip")
    ap.add_argument("--sids", default="3017,2395")
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        rc = tx._selftest()
        if rc != 0:
            return rc
        fake = asof_ready.classify_asof("2026-08-19", "2026-08-18", 1000)
        if fake != asof_ready.STATUS_FAKE_B3:
            print("✗ classify 假 B3", file=sys.stderr)
            return 1
        rc2 = main(["--tip", "D"])
        if rc2 != 2:
            print("✗ 佔位符 D 應 rc=2", file=sys.stderr)
            return 1
        print("  ✓ classify 假 B3；CLI 佔位符拒")
        print("自測:全通過 ✓")
        return 0
    tip = args.tip or args.tip_alias
    if not tip:
        print(__doc__)
        return 0
    err = asof_ready.date_arg_error(tip)
    if err:
        print(err, file=sys.stderr)
        return 2
    sids = _parse_sids(args.sids)
    if sids != ["3017", "2395"]:
        print("✗ 本版只允許 --sids 3017,2395", file=sys.stderr)
        return 2
    payload, rc = probe(tip, sids)
    if rc == asof_ready.RC_FAKE_B3:
        print("✗ 假 B3：禁止把還沒進庫的日當 as-of", file=sys.stderr)
        return rc
    if rc != 0:
        print("✗ status=%s" % payload.get("status"), file=sys.stderr)
        return rc
    _print(payload)
    path = args.json_out or ("/tmp/twin-ex-grid-%s.json" % payload["tip"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    print("JSON %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""CHARGE-T5 宇宙驗證 — E-charge×T5、等權 k=10（dry-run；不要抱牢；零寫庫）。

🎯 這支在做什麼（白話）：把兩檔實驗室的冠軍規則拿到核心宇宙重跑。
   組合尺＝同日入選等權、檔內 T5。逐檔連乘與 T10／T20／T40／兩檔舊帳只對照。
   不把 OOS 最長持有當冠。≠可交易、≠改 standing。

執行指令矩陣:
  python scripts/probe_charge_t5.py --selftest
  python scripts/probe_charge_t5.py --tip 2026-08-18
  python scripts/probe_charge_t5.py --tip 2026-08-19  # rc=3
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date

import _bootstrap  # noqa: F401

from augur.advisor.payload import _lookup_stock_names
from augur.catalog import world_concept
from augur.core import asof_ready, db
from augur.evaluation import charge_t5 as ct
from augur.evaluation import label as label_mod
from augur.evaluation import twin_ex as tx

ADJ_CONCEPT = "tw.daily_bar_adjusted"
NOTE = (
    "CHARGE-T5-v1；E-charge×T5；PIT 宇宙＝最近 as_of≤D；"
    "同日 k=10 等權；IS=2024 OOS=2025-01..2026-06；"
    "禁 OOS 最長持有當冠；兩檔％≠產品績效；條件≠可交易；"
    "dry-run 不寫 prediction_values；不改 standing 20,60"
)
TWIN_SIDS = ("3017", "2395")
TWIN_IS = {"n": 15, "compound_pct": 56.8}
TWIN_OOS = {"n": 24, "compound_pct": 72.9}


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
    return ct.COST_ROUNDTRIP_DEFAULT


def _pub_win(w: dict) -> dict:
    out = dict(w)
    for k in ("compound_pct", "compound_cost_pct", "mean_ret_pct", "mean_n"):
        if out.get(k) is not None:
            out[k] = round(float(out[k]), 4)
    return out


def _pub_trade(t: dict) -> dict:
    return {
        "sid": t["sid"],
        "signal": t["signal"].isoformat() if hasattr(t["signal"], "isoformat") else str(t["signal"]),
        "entry": t["entry"].isoformat() if hasattr(t["entry"], "isoformat") else str(t["entry"]),
        "exit": t["exit"].isoformat() if hasattr(t["exit"], "isoformat") else str(t["exit"]),
        "hold_td": t["hold_td"],
        "ret_pct": round(float(t["ret"]) * 100.0, 4),
        "n_cands": t.get("n_cands"),
        "truncated": t.get("truncated"),
    }


def _closes_for(sid: str, cal: list, px: dict) -> list:
    row = px.get(sid, {})
    return [row.get(d) for d in cal]


def probe(tip_iso: str) -> tuple[dict, int]:
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
            "SELECT as_of_date, stock_id FROM core_universe_asof WHERE as_of_date <= %s",
            (tip,),
        )
        by_d = {}
        for a, s in cur.fetchall():
            by_d.setdefault(a, set()).add(str(s))
        snaps = sorted(by_d.items())
        # 只需 IS 前一年起曾進宇宙的名字（含 252 日回看）
        sids = sorted({
            sid for d, u in snaps if d >= date(2023, 1, 1) for sid in u
        })
        if not sids:
            return {"tip": tip_iso, "status": "no_core", "note": NOTE}, 2
        cur.execute(
            f"SELECT stock_id, date, close FROM {adj} "
            "WHERE stock_id = ANY(%s) AND date <= %s AND close > 0",
            (sids, tip),
        )
        px = {}
        for sid, d, c in cur.fetchall():
            px.setdefault(str(sid), {})[d] = float(c)
        cost = _load_cost(cur)
        names = _lookup_stock_names(conn, cur, list(TWIN_SIDS)) or {}

    uni_by_i = ct.pit_sets(snaps, cal)
    n_uni_days = sum(1 for u in uni_by_i if u)
    flags_by, scores_by, closes_by = {}, {}, {}
    for sid in sids:
        closes = _closes_for(sid, cal, px)
        closes_by[sid] = closes
        fl, sc = ct.sid_series(closes)
        flags_by[sid] = fl
        scores_by[sid] = sc

    trades = ct.select_book(
        flags_by, scores_by, uni_by_i, closes_by, cal,
        k=ct.K_DEFAULT, hold=ct.HOLD_MODEL, max_i=max_i,
    )
    bsk = ct.baskets_from_trades(trades)
    model_is = ct.window_from_baskets(bsk, tx.in_is, cost=cost)
    model_oos = ct.window_from_baskets(bsk, tx.in_oos, cost=cost)

    contrasts = [
        ct.contrast_hold_baskets(
            trades, closes_by, cal, h, max_i=max_i, cost=cost,
        )
        for h in ct.CONTRAST_HOLDS
    ]

    # 逐檔連乘（無 k；非組合）
    date_i = {d: i for i, d in enumerate(cal)}
    dummy_h5 = [False] * len(cal)
    dummy_la = [False] * len(cal)
    uncapped = []
    for sid in sids:
        raw = tx.simulate_trades(
            flags_by[sid], closes_by[sid], cal, "X-T5",
            h5_neg=dummy_h5, la_fail=dummy_la, max_i=max_i,
        )
        for t in raw:
            i = date_i[t["signal"]]
            uni = uni_by_i[i]
            if not uni or sid not in uni:
                continue
            uncapped.append({**t, "sid": sid})
    uncapped.sort(key=lambda t: (t["signal"], t["sid"]))
    cap_is = ct.window_from_trades(uncapped, tx.in_is, cost=cost)
    cap_oos = ct.window_from_trades(uncapped, tx.in_oos, cost=cost)

    twin_sel = [t for t in trades if t["sid"] in TWIN_SIDS]
    twin_unc = [t for t in uncapped if t["sid"] in TWIN_SIDS]
    twin_sel_is = ct.window_from_trades(twin_sel, tx.in_is, cost=cost)
    twin_sel_oos = ct.window_from_trades(twin_sel, tx.in_oos, cost=cost)
    twin_unc_is = ct.window_from_trades(twin_unc, tx.in_is, cost=cost)
    twin_unc_oos = ct.window_from_trades(twin_unc, tx.in_oos, cost=cost)

    win_is = [t for t in trades if tx.in_is(t["signal"])]
    win_oos = [t for t in trades if tx.in_oos(t["signal"])]
    top_is = Counter(t["sid"] for t in win_is).most_common(12)
    top_oos = Counter(t["sid"] for t in win_oos).most_common(12)

    model_ok = ct.both_windows_positive(model_is, model_oos)
    model_ok_cost = ct.both_windows_positive(
        {"compound_pct": model_is["compound_cost_pct"]},
        {"compound_pct": model_oos["compound_cost_pct"]},
    )
    t20 = next(c for c in contrasts if c["hold"] == 20)
    t40 = next(c for c in contrasts if c["hold"] == 40)
    oos_t20_higher = (
        t20["oos"]["compound_pct"] is not None
        and model_oos["compound_pct"] is not None
        and float(t20["oos"]["compound_pct"]) > float(model_oos["compound_pct"])
    )

    payload = {
        "version": ct.VERSION,
        "dry_run": True,
        "wrote_prediction_values": False,
        "standing_unchanged": True,
        "tip": tip.isoformat(),
        "price_max": snap.get("price_max"),
        "k": ct.K_DEFAULT,
        "hold": ct.HOLD_MODEL,
        "pit": "nearest_asof_le_D",
        "n_snaps": len(snaps),
        "n_sids": len(sids),
        "n_uni_days": n_uni_days,
        "is": {"start": ct.IS_START.isoformat(), "end": ct.IS_END.isoformat()},
        "oos": {"start": ct.OOS_START.isoformat(), "end": ct.OOS_END.isoformat()},
        "cost_roundtrip": cost,
        "asof_status": snap["status"],
        "model": {
            "entry": "E-charge",
            "exit": "X-T5",
            "is": _pub_win(model_is),
            "oos": _pub_win(model_oos),
            "both_windows_positive": model_ok,
            "both_windows_positive_after_cost": model_ok_cost,
            "not_tradable": True,
            "not_established": True,
        },
        "contrast_holds": [
            {
                "hold": c["hold"],
                "n_complete": c["n_complete"],
                "bh_like": c["bh_like"],
                "contrast_only": c["contrast_only"],
                "is": _pub_win(c["is"]),
                "oos": _pub_win(c["oos"]),
                "crowned": False,
            }
            for c in contrasts
        ],
        "do_not_crown_long_hold": True,
        "oos_t20_higher_than_t5": oos_t20_higher,
        "t40_not_champion": True,
        "uncapped_sequential": {
            "note": "逐檔 100% 連乘，非組合；對照兩檔研究口徑",
            "is": _pub_win(cap_is),
            "oos": _pub_win(cap_oos),
        },
        "two_name_in_universe_book": {
            "sids": list(TWIN_SIDS),
            "names": {s: names.get(s, "") for s in TWIN_SIDS},
            "selected_k10": {"is": _pub_win(twin_sel_is), "oos": _pub_win(twin_sel_oos)},
            "uncapped": {"is": _pub_win(twin_unc_is), "oos": _pub_win(twin_unc_oos)},
            "blotter_research": {"is": TWIN_IS, "oos": TWIN_OOS},
        },
        "top_sids": {
            "is": [{"sid": s, "n": n} for s, n in top_is],
            "oos": [{"sid": s, "n": n} for s, n in top_oos],
        },
        "n_selected_trades": len(trades),
        "trades_is_oos": [
            _pub_trade(t) for t in trades
            if tx.in_is(t["signal"]) or tx.in_oos(t["signal"])
        ],
        "note": NOTE,
    }
    # silence unused
    _ = t40
    return payload, 0


def _fmt_pct(v):
    if v is None:
        return "—"
    return "%+.1f" % float(v)


def _print(payload: dict) -> None:
    print("護欄: " + payload["note"])
    m = payload["model"]
    print(
        "tip=%s 宇宙=%d檔／PIT日=%d／快照=%d  cost=%.3f%%"
        % (
            payload["tip"], payload["n_sids"], payload["n_uni_days"],
            payload["n_snaps"], float(payload["cost_roundtrip"]) * 100.0,
        )
    )
    print("── 模型 E-charge×T5（同日等權 k=10；組合連乘）──")
    print(
        "IS  籃=%s 檔次=%s 勝=%s  %+0.1f%%  成本後 %s"
        % (
            m["is"]["n_baskets"], m["is"]["n_names"], m["is"]["wins"],
            m["is"]["compound_pct"] or 0.0,
            _fmt_pct(m["is"]["compound_cost_pct"]),
        )
    )
    print(
        "OOS 籃=%s 檔次=%s 勝=%s  %+0.1f%%  成本後 %s"
        % (
            m["oos"]["n_baskets"], m["oos"]["n_names"], m["oos"]["wins"],
            m["oos"]["compound_pct"] or 0.0,
            _fmt_pct(m["oos"]["compound_cost_pct"]),
        )
    )
    print(
        "兩窗同號（無成本／成本後）：%s／%s；≠可交易；≠#14"
        % (
            "是" if m["both_windows_positive"] else "否",
            "是" if m["both_windows_positive_after_cost"] else "否",
        )
    )
    print("── 同一進場、改持有（對照，不當冠）──")
    print(
        "T5  IS %s  OOS %s  ← 模型"
        % (_fmt_pct(m["is"]["compound_pct"]), _fmt_pct(m["oos"]["compound_pct"]))
    )
    for c in payload["contrast_holds"]:
        tag = "對照不當冠" if c["contrast_only"] else ("偏抱牢" if c["bh_like"] else "對照")
        print(
            "T%s IS %s  OOS %s  %s"
            % (
                c["hold"],
                _fmt_pct(c["is"]["compound_pct"]),
                _fmt_pct(c["oos"]["compound_pct"]),
                tag,
            )
        )
    if payload.get("oos_t20_higher_than_t5"):
        print("OOS 的 T20 高於 T5：仍不當冠（不要抱牢）。")
    u = payload["uncapped_sequential"]
    print(
        "逐檔連乘（非組合）IS n=%s %s  OOS n=%s %s"
        % (u["is"]["n"], _fmt_pct(u["is"]["compound_pct"]),
           u["oos"]["n"], _fmt_pct(u["oos"]["compound_pct"]))
    )
    tw = payload["two_name_in_universe_book"]
    print(
        "兩檔在宇宙帳（k=10 入選）IS n=%s %s  OOS n=%s %s；舊帳 IS 15/+56.8%% OOS 24/+72.9%%"
        % (
            tw["selected_k10"]["is"]["n"], _fmt_pct(tw["selected_k10"]["is"]["compound_pct"]),
            tw["selected_k10"]["oos"]["n"], _fmt_pct(tw["selected_k10"]["oos"]["compound_pct"]),
        )
    )
    print(
        "兩檔無 k（PIT）IS n=%s %s  OOS n=%s %s"
        % (
            tw["uncapped"]["is"]["n"], _fmt_pct(tw["uncapped"]["is"]["compound_pct"]),
            tw["uncapped"]["oos"]["n"], _fmt_pct(tw["uncapped"]["oos"]["compound_pct"]),
        )
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CHARGE-T5 宇宙驗證（dry-run）")
    ap.add_argument("--tip", dest="tip", default=None)
    ap.add_argument("--date", dest="tip_alias", default=None, help="同 --tip")
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        rc = ct._selftest()
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
    payload, rc = probe(tip)
    if rc == asof_ready.RC_FAKE_B3:
        print("✗ 假 B3：禁止把還沒進庫的日當 as-of", file=sys.stderr)
        return rc
    if rc != 0:
        print("✗ status=%s" % payload.get("status"), file=sys.stderr)
        return rc
    _print(payload)
    path = args.json_out or ("/tmp/charge-t5-universe-%s.json" % payload["tip"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    print("JSON %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

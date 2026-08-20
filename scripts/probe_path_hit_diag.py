#!/usr/bin/env python
"""PATH-HIT-DIAG — 四閘做多通過段分桶（dry-run；零寫庫；不改 θ）。

🎯 這支在做什麼（白話）：全宇宙做多四閘、每段連續過關第一天、t+1 進場、
   持有 30 日。依年、回撤子帶、H40 深淺、20 日成交額分桶，分 IS／OOS 報
   勝率與扣成本均酬。診斷 ≠ 新濾、≠ 可交易。

執行指令矩陣:
  python scripts/probe_path_hit_diag.py --selftest
  python scripts/probe_path_hit_diag.py --asof 2026-08-19 --start 2005-01-03
  python scripts/probe_path_hit_diag.py --asof 2026-08-20  # rc=3
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date

import numpy as np
import pandas as pd

import _bootstrap  # noqa: F401

from augur.catalog import world_concept
from augur.core import asof_ready, db
from augur.evaluation import uptrend_pullback as up

VERSION = "PATH-HIT-DIAG-v1"
COST = 0.00585
HOLD = 30
H_LONG = (40, 60, 90, 120, 240)
H_SHORT = (5, 10)
IS_START, IS_END = date(2018, 1, 2), date(2024, 12, 31)
OOS_START, OOS_END = date(2025, 1, 2), date(2026, 6, 30)
CONTRAST_END = date(2017, 12, 31)
NOTE = (
    "PATH-HIT-DIAG-v1；四閘 streak 首日；t+1；hold=30；"
    "分桶≠新濾；勝率≠報酬％；條件≠可交易；dry；不改 standing 20,60"
)


def split_of(d: date) -> str:
    if IS_START <= d <= IS_END:
        return "IS"
    if OOS_START <= d <= OOS_END:
        return "OOS"
    if d <= CONTRAST_END:
        return "contrast"
    return "other"


def dd20_band(dd20: float) -> str:
    x = float(dd20) * 100.0
    if x < -12:
        return "[-15,-12)"
    if x < -9:
        return "[-12,-9)"
    if x < -6:
        return "[-9,-6)"
    return "[-6,-3]"


def h40_band(h40_simple: float) -> str:
    x = float(h40_simple) * 100.0
    if x <= 5:
        return "(0,5%]"
    if x <= 15:
        return "(5,15%]"
    if x <= 30:
        return "(15,30%]"
    return ">30%"


def summarize(vals: list[float]) -> dict:
    if not vals:
        return {"n": 0, "hit": None, "hit_net": None, "mean": None, "mean_net": None,
                "med": None, "med_net": None}
    n = len(vals)
    nets = [v - COST for v in vals]
    return {
        "n": n,
        "hit": round(sum(v > 0 for v in vals) / n, 4),
        "hit_net": round(sum(v > 0 for v in nets) / n, 4),
        "mean": round(sum(vals) / n, 6),
        "mean_net": round(sum(nets) / n, 6),
        "med": round(sorted(vals)[n // 2], 6),
        "med_net": round(sorted(nets)[n // 2], 6),
    }


def _bucket_table(rows: list[dict], key: str) -> dict[str, dict]:
    g = defaultdict(list)
    for r in rows:
        v = r.get("fwd")
        if v is None:
            continue
        g[r[key]].append(v)
    return {k: summarize(g[k]) for k in sorted(g, key=lambda x: (str(x)))}


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("dd20 甜區", dd20_band(-0.08) == "[-9,-6)")
    chk("dd20 深", dd20_band(-0.14) == "[-15,-12)")
    chk("dd20 淺", dd20_band(-0.04) == "[-6,-3]")
    chk("h40 薄", h40_band(0.04) == "(0,5%]")
    chk("split IS", split_of(date(2020, 6, 1)) == "IS")
    chk("split OOS", split_of(date(2025, 6, 30)) == "OOS")
    chk("split contrast", split_of(date(2008, 10, 1)) == "contrast")
    s = summarize([0.02, -0.01, 0.0])
    chk("n=3", s["n"] == 3)
    fake = asof_ready.classify_asof("2026-08-20", "2026-08-19", 1000)
    chk("假 B3 分類", fake == asof_ready.STATUS_FAKE_B3)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _scan(asof: date, start: date) -> tuple[list[dict], dict]:
    with db.connect() as conn, conn.cursor() as cur:
        snap = asof_ready.snapshot(cur, asof.isoformat())
        if snap["status"] != asof_ready.STATUS_READY:
            return [], snap
        adj = world_concept.resolve_sql("tw.daily_bar_adjusted", conn=conn)
        cur.execute("SELECT DISTINCT stock_id FROM core_universe_asof")
        sids = [str(r[0]) for r in cur.fetchall()]
        cur.execute(f"SELECT DISTINCT date FROM {adj} ORDER BY 1")
        cal = [r[0] for r in cur.fetchall()]
        ncal = len(cal)
        di = {d: i for i, d in enumerate(cal)}
        if asof not in di or start not in di and not any(d >= start for d in cal):
            return [], {**snap, "status": "calendar_gap"}
        start_i = next(i for i, d in enumerate(cal) if d >= start)
        tip_i = di[asof]
        cur.execute(
            f'SELECT stock_id, date, close, "Trading_money" FROM {adj} '
            "WHERE stock_id = ANY(%s) AND close>0",
            (sids,),
        )
        px, money = {s: {} for s in sids}, {s: {} for s in sids}
        for sid, d, c, m in cur.fetchall():
            sid = str(sid)
            px[sid][d] = float(c)
            if m is not None:
                money[sid][d] = float(m)

    def path_arr(closes, h):
        out = np.full(ncal, np.nan)
        out[h:] = closes[h:] / closes[:-h] - 1.0
        return out

    def roll_ok_maxmin(closes, w):
        s = pd.Series(closes)
        valid = s.notna() & (s > 0)
        okw = valid.rolling(w, min_periods=w).sum() == w
        mx = s.rolling(w, min_periods=w).max().where(okw)
        mn = s.rolling(w, min_periods=w).min().where(okw)
        return mx.to_numpy(), mn.to_numpy()

    def fwd(closes, i, h=HOLD):
        je, jx = i + 1, i + 1 + h
        if jx >= ncal:
            return None
        pe, px_ = closes[je], closes[jx]
        if not (np.isfinite(pe) and np.isfinite(px_) and pe > 0 and px_ > 0):
            return None
        return float(px_ / pe - 1.0)

    def streak_starts(mask):
        idxs = np.flatnonzero(mask[start_i: tip_i + 1]) + start_i
        if len(idxs) == 0:
            return []
        starts = [int(idxs[0])]
        for a, b in zip(idxs[:-1], idxs[1:]):
            if int(b) != int(a) + 1:
                starts.append(int(b))
        return starts

    rows = []
    for sid in sids:
        closes = np.array([px[sid].get(d, np.nan) for d in cal], dtype=np.float64)
        mon = np.array([money[sid].get(d, np.nan) for d in cal], dtype=np.float64)
        ok = np.isfinite(closes) & (closes > 0)
        p = {h: path_arr(closes, h) for h in up.H_TRACK}
        mx20, _ = roll_ok_maxmin(closes, 20)
        hi252, lo252 = roll_ok_maxmin(closes, 252)
        with np.errstate(divide="ignore", invalid="ignore"):
            dd20 = closes / mx20 - 1.0
            p2h = closes / hi252
            cyc = (closes - lo252) / (hi252 - lo252)
        s_m = pd.Series(mon)
        m20 = s_m.rolling(20, min_periods=20).mean()
        m20 = m20.where(s_m.notna().rolling(20, min_periods=20).sum() == 20).to_numpy()
        LA = np.ones(ncal, dtype=bool)
        for h in H_LONG:
            LA &= np.isfinite(p[h]) & (p[h] > 0)
        LB = np.ones(ncal, dtype=bool)
        for h in H_SHORT:
            LB &= np.isfinite(p[h]) & (p[h] < 0)
        LC = np.isfinite(dd20) & (dd20 >= -0.15) & (dd20 <= -0.03)
        LD = np.isfinite(cyc) & np.isfinite(p2h) & (cyc >= 0.40) & (p2h >= 0.80)
        g4 = LA & LB & LC & LD & ok
        for i in streak_starts(g4):
            d = cal[i]
            rows.append({
                "sid": sid,
                "d": d.isoformat(),
                "split": split_of(d),
                "year": d.year,
                "dd20": float(dd20[i]),
                "dd20_band": dd20_band(float(dd20[i])),
                "h40": float(p[40][i]),
                "h40_band": h40_band(float(p[40][i])),
                "m20": None if not np.isfinite(m20[i]) else float(m20[i]),
                "fwd": fwd(closes, i),
            })
    snap_ok = {"status": "ready", "price_max": asof.isoformat(), "asof": asof.isoformat()}
    return rows, snap_ok


def _liq_edges(rows: list[dict]) -> list[float]:
    xs = [r["m20"] for r in rows if r["split"] == "IS" and r["m20"] is not None]
    if len(xs) < 20:
        xs = [r["m20"] for r in rows if r["m20"] is not None]
    if len(xs) < 4:
        return []
    qs = np.quantile(xs, [0.25, 0.5, 0.75]).tolist()
    return [float(q) for q in qs]


def _liq_band(m20, edges: list[float]) -> str:
    if m20 is None or not edges:
        return "unknown"
    a, b, c = edges
    if m20 <= a:
        return "Q1 低"
    if m20 <= b:
        return "Q2"
    if m20 <= c:
        return "Q3"
    return "Q4 高"


def build_payload(rows: list[dict], snap: dict) -> dict:
    complete = [r for r in rows if r["fwd"] is not None]
    edges = _liq_edges(complete)
    for r in complete:
        r["liq_band"] = _liq_band(r["m20"], edges)
    by_split = defaultdict(list)
    for r in complete:
        by_split[r["split"]].append(r["fwd"])
    payload = {
        "version": VERSION,
        "dry_run": True,
        "wrote_prediction_values": False,
        "standing_unchanged": True,
        "theta_unchanged": True,
        "asof": snap.get("asof"),
        "price_max": snap.get("price_max"),
        "hold": HOLD,
        "cost": COST,
        "note": NOTE,
        "n_signals": len(rows),
        "n_complete": len(complete),
        "n_incomplete": len(rows) - len(complete),
        "liq_q_is": edges,
        "overall": {k: summarize(by_split[k]) for k in ("contrast", "IS", "OOS", "other")
                    if k in by_split or True},
        "by_year": {},
        "by_dd20": {},
        "by_h40": {},
        "by_liq": {},
    }
    payload["overall"] = {k: summarize(by_split.get(k, [])) for k in ("contrast", "IS", "OOS", "other")}
    payload["overall"]["all"] = summarize([r["fwd"] for r in complete])
    for sp in ("IS", "OOS", "contrast"):
        sub = [r for r in complete if r["split"] == sp]
        payload["by_year"][sp] = _bucket_table(sub, "year")
        payload["by_dd20"][sp] = _bucket_table(sub, "dd20_band")
        payload["by_h40"][sp] = _bucket_table(sub, "h40_band")
        payload["by_liq"][sp] = _bucket_table(sub, "liq_band")
    return payload


def probe(asof_iso: str, start_iso: str) -> tuple[dict, int]:
    with db.connect() as conn, conn.cursor() as cur:
        snap = asof_ready.snapshot(cur, asof_iso)
    if snap["status"] != asof_ready.STATUS_READY:
        return {
            "asof": asof_iso,
            "status": snap.get("status"),
            "price_max": snap.get("price_max"),
            "note": NOTE,
        }, int(snap.get("rc") or asof_ready.rc_of(snap["status"]))
    asof = asof_ready.as_date(asof_iso)
    start = asof_ready.as_date(start_iso)
    rows, snap2 = _scan(asof, start)
    if snap2.get("status") not in (None, "ready", asof_ready.STATUS_READY) and not rows:
        st = snap2.get("status")
        if st and st != "ready":
            return {"asof": asof_iso, "status": st, "note": NOTE}, 2
    payload = build_payload(rows, {**snap, **snap2, "asof": asof_iso})
    return payload, 0


def _fmt_row(lab, s):
    if not s or s.get("n", 0) == 0:
        return f"  {lab}: n=0"
    return (
        f"  {lab}: n={s['n']}  毛>0={s['hit']:.1%}  扣成本>0={s['hit_net']:.1%}"
        f"  均={s['mean']*100:+.2f}%  中位={s['med']*100:+.2f}%"
        f"  均淨={s['mean_net']*100:+.2f}%"
    )


def _print(payload: dict) -> None:
    print("護欄: " + payload["note"])
    print(
        "asof=%s price_max=%s signals=%s complete=%s incomplete=%s"
        % (payload.get("asof"), payload.get("price_max"),
           payload.get("n_signals"), payload.get("n_complete"),
           payload.get("n_incomplete"))
    )
    print("── 總覽（四閘、不改 θ）──")
    for k in ("all", "contrast", "IS", "OOS", "other"):
        print(_fmt_row(k, payload["overall"].get(k)))
    for title, block in (
        ("回撤 dd20", "by_dd20"),
        ("H40 路徑", "by_h40"),
        ("成交額 20d 均（IS 四分位）", "by_liq"),
    ):
        print(f"── {title} ──")
        for sp in ("IS", "OOS"):
            print(f"  [{sp}]")
            tbl = payload[block].get(sp) or {}
            for lab, s in tbl.items():
                print(_fmt_row(str(lab), s))
    print("── 年（IS／OOS）──")
    for sp in ("IS", "OOS"):
        print(f"  [{sp}]")
        tbl = payload["by_year"].get(sp) or {}
        for lab, s in sorted(tbl.items(), key=lambda kv: int(kv[0])):
            print(_fmt_row(str(lab), s))
    print("診斷 ≠ 新濾。條件 ≠ 可交易。不 promote。")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="PATH-HIT-DIAG 四閘分桶（dry-run）")
    ap.add_argument("--asof", dest="asof", default=None)
    ap.add_argument("--start", default="2005-01-03")
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        rc = _selftest()
        if rc != 0:
            return rc
        rc2 = main(["--asof", "D"])
        if rc2 != 2:
            print("✗ 佔位符 D 應 rc=2", file=sys.stderr)
            return 1
        print("  ✓ CLI 佔位符拒")
        print("自測:全通過 ✓")
        return 0
    if not args.asof:
        print(__doc__)
        return 0
    err = asof_ready.date_arg_error(args.asof)
    if err:
        print(err, file=sys.stderr)
        return 2
    payload, rc = probe(args.asof, args.start)
    if rc == asof_ready.RC_FAKE_B3:
        print("✗ 假 B3：禁止把還沒進庫的日當 as-of", file=sys.stderr)
        return rc
    if rc != 0:
        print("✗ status=%s" % payload.get("status"), file=sys.stderr)
        return rc
    _print(payload)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("JSON " + args.json_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

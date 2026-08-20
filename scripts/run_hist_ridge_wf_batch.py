#!/usr/bin/env python
"""HIST-RIDGE-WF 批次 — 月尾先 collect；每個交易日 asof=D 訓八窗（禁用 D 之後資料）。

🎯 這支在做什麼（白話）：
  1) 先補月尾特徵＋核心（PIT 樣本河）
  2) 每個交易日 D：特徵＋核心＠D → RankRidge 八窗 **asof=D 重訓**（標出場日必須 ≤D）
     → 同日八窗分數。不是拿月末模型套月中，也不是拿 08-19 模型套回 2014。
  3) 分數夠、且 t+1 再抱 30 日已實現，才准 RIDGE-THEN-PB vs 路徑閘。

守: no-fake-B3 · no-promote · no-SIM-apply · NF-pause · standing 不改
    · 只 RankRidge × H_TRACK · 不重建 tip 核心 · 2000–2013 不做

執行指令矩陣:
  python scripts/run_hist_ridge_wf_batch.py --selftest
  python scripts/run_hist_ridge_wf_batch.py --month-ends --collect-only --apply
  python scripts/run_hist_ridge_wf_batch.py --all-days --train-predict --apply --from 2015-01-30
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import _bootstrap  # noqa: F401

from augur.core import asof_ready, db
from augur.core.closed_horizons import H_TRACK
from augur.evaluation import label as label_mod

ROOT = Path(__file__).resolve().parents[1]
SHELL = ROOT / "scripts" / "run_hist_ridge_wf.sh"
PROGRESS = ROOT / "audits" / "HIST-RIDGE-WF-MONTHENDS-PROGRESS.json"
PROGRESS_ALLDAYS = ROOT / "audits" / "HIST-RIDGE-WF-ALLDAYS-PROGRESS.json"
NEED = list(H_TRACK)


def _month_ends_completed(cal, tip):
    """≤tip 的月尾；當月若還沒走到該月最後交易日（tip 仍在月中）則不含當月。"""
    xs = [d for d in cal if d <= tip]
    out = []
    for i, d in enumerate(xs):
        nxt = xs[i + 1] if i + 1 < len(xs) else None
        if nxt is not None and (nxt.year, nxt.month) == (d.year, d.month):
            continue
        if nxt is None and (tip.year, tip.month) == (d.year, d.month):
            continue
        if d < date(2014, 1, 1):
            continue
        out.append(d)
    return out


def _trading_days(cal, start, last):
    return [d for d in cal if start <= d <= last]


def inventory(conn, tip):
    cal = [d for d in label_mod.full_calendar(conn) if d <= tip]
    mes = _month_ends_completed(cal, tip)
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT panel_date FROM feature_values")
        fv = {r[0] for r in cur.fetchall()}
        cur.execute("SELECT DISTINCT as_of_date FROM core_universe_asof")
        core = {r[0] for r in cur.fetchall()}
        cur.execute(
            """
            SELECT pv.panel_date, array_agg(DISTINCT m.horizon ORDER BY m.horizon)
              FROM prediction_values pv
              JOIN model_registry m ON m.model_id = pv.model_id
             WHERE m.family = 'RankRidge'
             GROUP BY 1
            """
        )
        pv = {r[0]: list(r[1] or []) for r in cur.fetchall()}
        cur.execute(
            "SELECT count(*) FROM core_universe_asof WHERE as_of_date=%s", (tip,)
        )
        n_tip = int(cur.fetchone()[0] or 0)
    return {
        "cal": cal,
        "month_ends": mes,
        "fv": fv,
        "core": core,
        "pv": pv,
        "n_tip": n_tip,
        "tip": tip,
    }


def eight_h_pv(inv, d):
    return list(inv["pv"].get(d) or []) == NEED


def load_progress(path=None):
    p = Path(path) if path else PROGRESS
    if not p.exists():
        return {"phase": None, "ok": [], "skip": [], "fail": []}
    return json.loads(p.read_text(encoding="utf-8"))


def save_progress(doc, path=None):
    p = Path(path) if path else PROGRESS
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=2, default=str) + "\n",
                 encoding="utf-8")


def run_one(d, *, apply, extra):
    cmd = ["bash", str(SHELL), "--date", d.isoformat()]
    cmd.append("--apply" if apply else "--dry-plan")
    cmd.extend(extra)
    print(f"\n>>> {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=str(ROOT))
    return r.returncode


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    print("[HIST-RIDGE-WF-batch selftest]")
    chk("shell", SHELL.is_file())
    chk("H_TRACK=8", len(NEED) == 8)
    dummy_cal = [
        date(2014, 1, 24), date(2014, 1, 27),
        date(2014, 2, 27),
        date(2026, 7, 30), date(2026, 7, 31),
        date(2026, 8, 18), date(2026, 8, 19),
    ]
    mes = _month_ends_completed(dummy_cal, date(2026, 8, 19))
    chk("當月未結束不含 08-19", date(2026, 8, 19) not in mes)
    chk("含 07-31 與 01-27", date(2026, 7, 31) in mes and date(2014, 1, 27) in mes)
    chk("1 月尾=01-27 非 01-24", date(2014, 1, 24) not in mes and date(2014, 1, 27) in mes)
    r = subprocess.run(["bash", str(SHELL), "--selftest"], cwd=str(ROOT))
    chk("inner shell selftest rc=0", r.returncode == 0)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="HIST-RIDGE-WF 月尾／月中批次")
    ap.add_argument("--selftest", action="store_true")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--month-ends", action="store_true")
    g.add_argument("--intra-month", action="store_true")
    g.add_argument("--all-days", action="store_true",
                   help="2014 起每個交易日（含月尾）；asof=D 重訓用這個")
    ap.add_argument("--collect-only", action="store_true",
                    help="只特徵＋宇宙")
    ap.add_argument("--train-predict", action="store_true",
                    help="asof=D 訓八窗＋打分（collect 已在則跳過 collect）")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-plan", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="最多處理幾日（0＝全部待做）")
    ap.add_argument("--from", dest="from_date", default=None, help="YYYY-MM-DD 起（含）")
    ap.add_argument("--until", dest="until_date", default=None, help="YYYY-MM-DD 迄（含）")
    ap.add_argument("--keep-going", action="store_true",
                    help="單日失敗繼續下一日（--all-days 預設開）")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.month_ends and not args.intra_month and not args.all_days:
        print(__doc__)
        return 0
    if args.apply == args.dry_plan:
        print("✗ 請顯式 --dry-plan 或 --apply", file=sys.stderr)
        return 2
    if (args.month_ends or args.all_days or args.intra_month) and not (
            args.collect_only or args.train_predict):
        print("✗ 須 --collect-only 或 --train-predict", file=sys.stderr)
        return 2

    with db.connect() as conn:
        with conn.cursor() as cur:
            tip = asof_ready.taiex_price_max(cur)
        if tip is None:
            print("✗ 無價", file=sys.stderr)
            return 4
        inv = inventory(conn, tip)

    lo = asof_ready.as_date(args.from_date) if args.from_date else date(2014, 1, 1)
    if args.until_date:
        hi = asof_ready.as_date(args.until_date)
    elif args.month_ends:
        hi = inv["month_ends"][-1]
    else:
        hi = tip
    if lo is None or hi is None:
        print("✗ --from／--until 須 YYYY-MM-DD", file=sys.stderr)
        return 2

    if args.month_ends:
        dates = [d for d in inv["month_ends"] if lo <= d <= hi]
        phase = "P1-collect" if args.collect_only else "P1-train-me"
    elif args.all_days:
        dates = [d for d in inv["cal"] if lo <= d <= hi and d >= date(2014, 1, 1)]
        phase = "P2-collect-daily" if args.collect_only else "P2-train-asof-D"
    else:
        me = set(inv["month_ends"])
        dates = [d for d in inv["cal"] if lo <= d <= hi and d not in me]
        phase = "P2-intra-collect" if args.collect_only else "P2-train-asof-D"

    todo = []
    skipped = []
    for d in dates:
        has_panel = d in inv["fv"]
        has_core = d in inv["core"]
        scored = eight_h_pv(inv, d)
        if args.collect_only:
            if has_panel and has_core:
                skipped.append((d, "already-panel+core"))
                continue
            todo.append(d)
        elif args.train_predict:
            if scored:
                skipped.append((d, "already-8h-pv"))
                continue
            todo.append(d)
        else:
            if scored:
                skipped.append((d, "already-8h-pv"))
                continue
            todo.append(d)

    if args.limit and args.limit > 0:
        todo = todo[: args.limit]

    print(f"HIST-RIDGE-WF-batch phase={phase} tip={tip} apply={int(args.apply)}")
    print(f"  month-ends completed={len(inv['month_ends'])} "
          f"({inv['month_ends'][0]}…{inv['month_ends'][-1]})")
    print(f"  todo={len(todo)} skip={len(skipped)} core@tip={inv['n_tip']}")
    if todo:
        print(f"  first={todo[0]} last={todo[-1]}")
    extra = []
    if args.collect_only:
        extra = ["--skip-train", "--skip-predict"]
    keep = bool(args.keep_going or args.all_days)
    prog_path = PROGRESS_ALLDAYS if args.all_days else PROGRESS
    prog = load_progress(prog_path)
    prog["phase"] = phase
    prog["tip"] = str(tip)
    prog.setdefault("ok", [])
    prog.setdefault("skip", [])
    prog.setdefault("fail", [])
    for d, why in skipped:
        rec = f"{d.isoformat()}:{why}"
        if rec not in prog["skip"]:
            prog["skip"].append(rec)

    n_ok = n_fail = 0
    for d in todo:
        rc = run_one(d, apply=args.apply, extra=extra)
        if rc == 0:
            n_ok += 1
            if args.apply:
                iso = d.isoformat()
                if iso not in prog["ok"]:
                    prog["ok"].append(iso)
        else:
            n_fail += 1
            if args.apply:
                prog["fail"].append({"date": d.isoformat(), "rc": rc})
                save_progress(prog, prog_path)
            print(f"⚠ 單日失敗 {d} rc={rc}" + (" ——繼續" if keep else " ——中止"),
                  file=sys.stderr)
            if not keep:
                return rc
        if args.apply:
            save_progress(prog, prog_path)

    with db.connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM core_universe_asof WHERE as_of_date=%s", (tip,)
        )
        n_tip_after = int(cur.fetchone()[0] or 0)
    print(f"\nbatch 結束 phase={phase} ok={n_ok} fail={n_fail} "
          f"core@tip {inv['n_tip']}→{n_tip_after}（應不變）")
    if n_tip_after != inv["n_tip"]:
        print("✗ tip 核心列數變了", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""已完成八窗日 → 做多 RIDGE-THEN-PB 池／收盤買進（不碰 HIST-RIDGE-WF 鎖）。

🎯 這支在做什麼（白話）：對「同日 RankRidge 八窗分數已齊」的交易日，
   相對強 Top10 當池（不因還沒回撤剔除）→ 回撤近→遠排序 → 過齊才標可當進場條件，
   其餘「等回撤，不是進場」。過齊者記該日還原收盤買進（不是 t+1）。
   與全交易日訓模河並行：只讀已完成日，不拿 `/tmp/augur_hist_ridge_wf.lock`。

執行指令矩陣:
  python scripts/run_ridge_then_pb_long_buy.py --selftest
  python scripts/run_ridge_then_pb_long_buy.py --dry-plan
  python scripts/run_ridge_then_pb_long_buy.py --apply --limit 1
  python scripts/run_ridge_then_pb_long_buy.py --apply --watch
"""
from __future__ import annotations

import argparse
import fcntl
import json
import sys
import time
from datetime import date
from pathlib import Path

import _bootstrap  # noqa: F401

import probe_ridge_then_pb as ridge_pb
from augur.catalog import world_concept
from augur.core import asof_ready, db
from augur.core.closed_horizons import H_TRACK
from augur.evaluation import ridge_then_pb_store as store
from augur.evaluation import uptrend_pullback as up

ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "audits" / "RIDGE-THEN-PB-LONG-BUY-PROGRESS.json"
LOCK = Path("/tmp/augur_ridge_then_pb_long.lock")
WF_LOCK = Path("/tmp/augur_hist_ridge_wf.lock")
ADJ_CONCEPT = "tw.daily_bar_adjusted"
NEED = list(H_TRACK)


def _load_progress():
    if not PROGRESS.exists():
        return {"ok": [], "skip": [], "fail": [], "n_buy": 0}
    return json.loads(PROGRESS.read_text(encoding="utf-8"))


def _save_progress(doc):
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def _eight(hs) -> bool:
    return list(hs or []) == NEED


def same_day_8h_dates(conn, lo: date, hi: date) -> list:
    """panel_date＝asof_snapshot 且八窗分數齊的交易日。"""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT pv.panel_date, array_agg(DISTINCT m.horizon ORDER BY m.horizon)
              FROM prediction_values pv
              JOIN model_registry m ON m.model_id = pv.model_id
             WHERE m.family = 'RankRidge'
               AND m.asof_snapshot = pv.panel_date
               AND pv.panel_date >= %s
               AND pv.panel_date <= %s
             GROUP BY 1
            """,
            (lo, hi),
        )
        return sorted(d for d, hs in cur.fetchall() if _eight(hs))


def same_day_8h_model_dates(conn, lo: date, hi: date) -> list:
    """同日 RankRidge 八窗已登錄（有模型即可跑；分數表可晚寫）。"""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT asof_snapshot, array_agg(DISTINCT horizon ORDER BY horizon)
              FROM model_registry
             WHERE family = 'RankRidge'
               AND asof_snapshot >= %s
               AND asof_snapshot <= %s
             GROUP BY 1
            """,
            (lo, hi),
        )
        return sorted(d for d, hs in cur.fetchall() if _eight(hs))


def fetch_closes(conn, asof, sids) -> dict[str, float]:
    if not sids:
        return {}
    adj = world_concept.resolve_sql(ADJ_CONCEPT, conn=conn)
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT stock_id, close FROM {adj} "
            "WHERE date=%s AND stock_id=ANY(%s) AND close>0",
            (asof, list(sids)),
        )
        return {str(s): float(c) for s, c in cur.fetchall()}


def _print_long(payload: dict) -> None:
    pack = payload.get("long") or {}
    print(
        "做多 asof=%s n_pool=%s 可當進場=%s 等回撤=%s"
        % (payload.get("asof"), pack.get("n_pool"), pack.get("n_entry"), pack.get("n_wait")),
        flush=True,
    )
    print("── 做多｜回撤近→遠（池＝Ridge 相對強 Top k；不剔除）──", flush=True)
    for r in pack.get("rows") or []:
        dd = r.get("dd20_pct")
        dd_s = "—" if dd is None else ("%+.1f%%" % float(dd))
        print(
            "  %2d  %s %s  回撤=%s  %s"
            % (r["rank"], r["sid"], r.get("name") or "", dd_s, r["tag"]),
            flush=True,
        )
        why = r.get("reason_zh") or ""
        extra = ("  缺：" + why) if why else ""
        print("      窗 %s%s" % (r.get("window_pass_zh") or "", extra), flush=True)


def run_one(asof, *, apply: bool, source: str = "pv") -> tuple[int, dict]:
    iso = asof.isoformat() if hasattr(asof, "isoformat") else str(asof)
    payload, rc = ridge_pb.probe(iso, k=10, source=source)
    if rc != 0:
        return rc, payload
    _print_long(payload)
    if not apply:
        return 0, payload
    sids = [r["sid"] for r in (payload.get("long") or {}).get("rows") or []]
    with db.connect() as conn:
        closes = fetch_closes(conn, asof_ready.as_date(iso), sids)
        payload["long_close"] = store.persist_long_close_buys(conn, payload, closes)
    h = payload["long_close"]
    print(
        "  落庫 %s  池=%s 過齊=%s 收盤買進=%s 缺價跳過=%s"
        % (h.get("table_buy"), h.get("n_pool"), h.get("n_entry"),
           h.get("n_buy"), h.get("n_skip_px")),
        flush=True,
    )
    return 0, payload


def _acquire_lock():
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    fd = open(LOCK, "w")
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fd.close()
        print("✗ 另一輪做多收盤帳在跑（%s）" % LOCK, file=sys.stderr)
        return None
    fd.write("%s\n" % Path(__file__).name)
    fd.flush()
    return fd


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    print("[ridge-then-pb-long-buy selftest]")
    chk("不拿 WF 鎖", str(LOCK) != str(WF_LOCK))
    chk("H_TRACK=8", NEED == [5, 10, 20, 40, 60, 90, 120, 240])
    chk("模型日函式", callable(same_day_8h_model_dates))
    chk("買進表", store.TABLE_LONG_BUY == "ridge_then_pb_long_buy")
    chk("池表", store.TABLE_LONG_ROW == "ridge_then_pb_long_row")
    chk("等回撤文案", up.RIDGE_THEN_PB_WAIT == "等回撤，不是進場")
    rc = store._selftest()
    chk("store selftest", rc == 0)
    rc2 = up._selftest()
    chk("uptrend_pullback selftest", rc2 == 0)
    rc3 = ridge_pb.main(["--date", "D"])
    chk("佔位符 D rc=2", rc3 == 2)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="已完成八窗日做多收盤買進排程")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-plan", action="store_true")
    ap.add_argument("--watch", action="store_true", help="輪詢新完成日（不擋訓模河）")
    ap.add_argument("--interval", type=int, default=90, help="--watch 秒")
    ap.add_argument("--limit", type=int, default=0, help="本輪最多處理幾日（0＝全部待做）")
    ap.add_argument("--from", dest="from_date", default="2014-01-02")
    ap.add_argument("--until", dest="until_date", default=None)
    ap.add_argument("--force", action="store_true", help="已處理日也重跑")
    ap.add_argument("--keep-going", action="store_true", default=True)
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.apply == args.dry_plan:
        print("✗ 請顯式 --dry-plan 或 --apply", file=sys.stderr)
        return 2
    if args.watch and not args.apply:
        print("✗ --watch 須配 --apply", file=sys.stderr)
        return 2

    lockf = None
    if args.apply:
        lockf = _acquire_lock()
        if lockf is None:
            return 3

    try:
        prog = _load_progress()
        n_done = 0
        while True:
            with db.connect() as conn:
                with conn.cursor() as cur:
                    tip = asof_ready.taiex_price_max(cur)
                if tip is None:
                    print("✗ 無價", file=sys.stderr)
                    return 4
                lo = asof_ready.as_date(args.from_date)
                hi = asof_ready.as_date(args.until_date) if args.until_date else tip
                if lo is None or hi is None:
                    print("✗ --from／--until 須 YYYY-MM-DD", file=sys.stderr)
                    return 2
                done_pv = set(same_day_8h_dates(conn, lo, hi))
                done_m = same_day_8h_model_dates(conn, lo, hi)
                already = set() if args.force else store.processed_long_asofs(conn)
            todo = [d for d in done_m if d not in already]
            print(
                "完成模型=%s 完成分數=%s 已入帳=%s 待做=%s tip=%s apply=%s"
                % (len(done_m), len(done_pv), len(already), len(todo), tip, args.apply),
                flush=True,
            )
            if args.dry_plan:
                for d in todo[:20]:
                    src = "pv" if d in done_pv else "dry_run"
                    print("  TODO %s (%s)" % (d, src))
                if len(todo) > 20:
                    print("  … 另 %s 日" % (len(todo) - 20))
                return 0
            if not todo and not args.watch:
                print("沒有待做日。")
                return 0
            for d in todo:
                if args.limit and n_done >= int(args.limit):
                    print("達 --limit %s" % args.limit, flush=True)
                    _save_progress(prog)
                    return 0
                src = "pv" if d in done_pv else "dry_run"
                print("\n>>> asof=%s source=%s persist-long-close" % (d, src), flush=True)
                try:
                    rc, payload = run_one(d, apply=True, source=src)
                except Exception as e:
                    rc, payload = 1, {"asof": str(d), "error": str(e)}
                    print("✗ exception %s" % e, file=sys.stderr, flush=True)
                if rc != 0:
                    prog.setdefault("fail", []).append("%s:rc=%s" % (d, rc))
                    _save_progress(prog)
                    if not args.keep_going:
                        return rc
                    continue
                n_done += 1
                prog.setdefault("ok", []).append(str(d))
                h = payload.get("long_close") or {}
                prog["n_buy"] = int(prog.get("n_buy") or 0) + int(h.get("n_buy") or 0)
                prog["last"] = str(d)
                prog["tip"] = str(tip)
                _save_progress(prog)
            if not args.watch:
                return 0
            time.sleep(max(15, int(args.interval)))
    finally:
        if lockf is not None:
            try:
                fcntl.flock(lockf, fcntl.LOCK_UN)
                lockf.close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())

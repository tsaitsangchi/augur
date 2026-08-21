#!/usr/bin/env python
"""P0 探針 — RankRidge-min 三張：by-date 還是要 data_id（每表 ≤2 call）。

🎯 這支在做什麼（白話）：讀 FinMind 額度錶，對還原價／法人買賣／借券成交
   各試「不帶 data_id 的單日」；失敗再試 data_id=2330。不寫 raw、不 heal、
   不開 L0。見 403／額度滿 → 停。不是解凍、不是 93 表。

執行指令矩陣:
  python scripts/probe_finmind_free_rankridge.py --selftest
  python scripts/probe_finmind_free_rankridge.py --dry-plan
  python scripts/probe_finmind_free_rankridge.py --apply
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from augur.core import asof_ready, config, db
from augur.ingestion import finmind

ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    "TaiwanStockPriceAdj",
    "TaiwanStockInstitutionalInvestorsBuySell",
    "TaiwanStockSecuritiesLending",
)
CANON = "2330"
MAX_PER_DS = 2
MAX_DATA_CALLS = len(DATASETS) * MAX_PER_DS  # 6


def classify_msg(msg: str) -> str:
    """應用層訊息 → 模式標籤。純函式。"""
    m = (msg or "").lower()
    if "register" in m or "update your level" in m:
        return "forbidden"
    if "data_id" in m and ("none" in m or "can't" in m or "cannot" in m or "required" in m):
        return "need-data-id"
    if "upper limit" in m or "reach the upper" in m:
        return "quota"
    if "ip" in m and ("ban" in m or "block" in m):
        return "ip-ban"
    return "error"


def scenario_of(rows: list) -> str:
    """三表結果 → A／B／C／mixed／abort。"""
    modes = [r.get("mode") for r in rows]
    if any(m in ("quota", "ip-ban", "abort") for m in modes):
        return "abort"
    if modes and all(m == "by-date" for m in modes):
        return "A"
    if modes and all(m == "per-stock" for m in modes):
        return "B"
    if any(m == "forbidden" for m in modes):
        return "C-forbidden"
    return "mixed"


def _one_shot(dataset: str, **params):
    """單次 fetch；max_retries=0 → 403 不睡 30 分。回 (ok, n, msg)。"""
    try:
        data = finmind.fetch(dataset, timeout=120, max_retries=0, **params)
        n = len(data) if data is not None else 0
        return True, n, ""
    except finmind.FinMindError as e:
        return False, 0, str(e)


def probe_dataset(dataset: str, day: str) -> dict:
    rec = {
        "dataset": dataset,
        "day": day,
        "calls": 0,
        "by_date_ok": None,
        "by_date_n": None,
        "per_stock_ok": None,
        "per_stock_n": None,
        "mode": None,
        "msg": "",
    }
    ok, n, msg = _one_shot(dataset, start_date=day, end_date=day)
    rec["calls"] += 1
    rec["by_date_ok"] = ok
    rec["by_date_n"] = n
    rec["msg"] = msg
    if ok:
        rec["mode"] = "by-date" if n > 0 else "by-date-empty"
        return rec
    tag = classify_msg(msg)
    if tag in ("quota", "ip-ban"):
        rec["mode"] = tag
        return rec
    ok2, n2, msg2 = _one_shot(dataset, data_id=CANON, start_date=day, end_date=day)
    rec["calls"] += 1
    rec["per_stock_ok"] = ok2
    rec["per_stock_n"] = n2
    if msg2:
        rec["msg"] = msg + " || " + msg2
    if ok2:
        rec["mode"] = "per-stock" if n2 > 0 else "per-stock-empty"
        return rec
    rec["mode"] = classify_msg(msg2) if msg2 else tag
    if rec["mode"] == "error" and tag != "error":
        rec["mode"] = tag
    return rec


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    print("[finmind-free-ridge P0 selftest]")
    chk("三張", list(DATASETS) == [
        "TaiwanStockPriceAdj",
        "TaiwanStockInstitutionalInvestorsBuySell",
        "TaiwanStockSecuritiesLending",
    ])
    chk("每表≤2", MAX_PER_DS == 2 and MAX_DATA_CALLS == 6)
    chk("register→forbidden", classify_msg("Your level is register. Please update your level") == "forbidden")
    chk("data_id→need", classify_msg("parameter data_id can't be none") == "need-data-id")
    chk("402→quota", classify_msg("Requests reach the upper limit. https://finmindtrade.com/") == "quota")
    chk("A", scenario_of([{"mode": "by-date"}] * 3) == "A")
    chk("B", scenario_of([{"mode": "per-stock"}] * 3) == "B")
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="P0 RankRidge-min FinMind 探針（每表≤2 call）")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-plan", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--date", dest="day", default=None, help="單日 YYYY-MM-DD；預設＝價頂")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.apply == args.dry_plan:
        print("✗ 請顯式 --dry-plan 或 --apply", file=sys.stderr)
        return 2
    if not config.FINMIND_TOKEN:
        print("✗ 無 FINMIND_TOKEN", file=sys.stderr)
        return 4

    with db.connect() as conn:
        with conn.cursor() as cur:
            tip = asof_ready.taiex_price_max(cur)
    day = args.day or (tip.isoformat() if tip else None)
    if not day:
        print("✗ 無價頂、且未給 --date", file=sys.stderr)
        return 4

    print("P0 RankRidge-min  日=%s  價頂=%s  每表≤%s call" % (day, tip, MAX_PER_DS), flush=True)
    print("表: %s" % ", ".join(DATASETS), flush=True)
    if args.dry_plan:
        print("將：讀 /user_info 一次；每表先不帶 data_id，失敗再 data_id=%s。不寫 raw。" % CANON)
        return 0

    info = {}
    try:
        count, limit = finmind._user_quota()
        info = {"user_count": count, "api_request_limit": limit}
    except Exception as e:
        print("✗ 讀錶失敗：%s" % e, file=sys.stderr)
        return 5
    remain = limit - count - finmind.QUOTA_HEADROOM
    print("額度錶 %s/%s  headroom=%s  reserve=%s" % (
        count, limit, limit - count, finmind.QUOTA_HEADROOM), flush=True)
    if remain < MAX_DATA_CALLS:
        print("✗ 保留區不夠做 ≤%s 次 data call，停" % MAX_DATA_CALLS, file=sys.stderr)
        return 1

    rows = []
    aborted = False
    n_calls = 0
    for ds in DATASETS:
        rec = probe_dataset(ds, day)
        n_calls += rec["calls"]
        rows.append(rec)
        print("  %s  mode=%s  calls=%s  by-date n=%s  per-stock n=%s" % (
            ds, rec["mode"], rec["calls"], rec["by_date_n"], rec["per_stock_n"]), flush=True)
        if rec.get("msg"):
            print("    msg: %s" % rec["msg"][:300], flush=True)
        if rec["mode"] in ("quota", "ip-ban"):
            aborted = True
            print("✗ 見額度／IP 訊號 → 停，不打其餘表", file=sys.stderr)
            break
        if n_calls > MAX_DATA_CALLS:
            aborted = True
            break

    scen = scenario_of(rows)
    out = {
        "asof_probe_day": day,
        "price_tip": None if tip is None else str(tip),
        "quota": info,
        "n_data_calls": n_calls,
        "aborted": aborted,
        "scenario": scen,
        "rows": rows,
        "note": "P0 現況地圖；若 limit≠600 則尚非 free 終局。不寫 raw。≠解凍。",
    }
    js = ROOT / "audits" / "FINMIND-FREE-PROBE-20260821.json"
    js.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print("scenario=%s  calls=%s  寫入 %s" % (scen, n_calls, js), flush=True)
    return 1 if aborted else 0


if __name__ == "__main__":
    raise SystemExit(main())

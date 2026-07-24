#!/usr/bin/env python
"""哲學↔市場進化結果解讀報告 — PME S4 顧問單向消費（零市場 API）。

🎯 這支在做什麼（白話）：唯讀查 evolution_production_feature_set／validated 原則／
   apply_log，印可解釋報告（或 JSON）。**不**寫 feature_values、不改權重、不下單。
   輸出供人讀／顧問注入；≠可交易／≠確立級。

守 #1 #15 #29；計畫 §4 S4；FZ-keep。

執行指令矩陣:
  python scripts/report_philosophy_evolution_interpretation.py           # 印 markdown 報告
  python scripts/report_philosophy_evolution_interpretation.py --json    # JSON 摘要
  python scripts/report_philosophy_evolution_interpretation.py --selftest  # 免 DB
"""
from __future__ import annotations

import argparse
import json
import sys

import _bootstrap  # noqa: F401

from augur.philosophy.interpretation import (
    DISCLAIMER_LINES,
    fetch_interpretation_snapshot,
    load_interpretation_markdown,
    render_interpretation_markdown,
    snapshot_from_rows,
    _selftest as _lib_selftest,
)


def _selftest() -> int:
    rc = _lib_selftest()
    # script 層：確認合成報告可印、含硬邊界句
    snap = snapshot_from_rows(
        prodset_rows=[{"feature": "f1", "set_status": "active", "principle_id": 1,
                       "source_run_id": 1, "apply_log_id": 1, "last_action": "promote"}],
        validated_rows=[],
        apply_rows=[],
    )
    md = render_interpretation_markdown(snap)
    ok = rc == 0 and "≠可交易" in md and DISCLAIMER_LINES[0][:8] in md
    print(f"  {'✓' if ok else '✗FAIL'} script 合成報告含免責")
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _to_json(snap) -> dict:
    return {
        "disclaimer": list(DISCLAIMER_LINES),
        "soul_wording_pending": snap.soul_wording_pending,
        "kill_state": snap.kill_state,
        "tag_count": snap.tag_count,
        "active_prodset": [e.__dict__ for e in snap.active_prodset],
        "validated_maps": [e.__dict__ for e in snap.validated_maps],
        "apply_logs": [e.__dict__ for e in snap.apply_logs],
        "note": snap.note,
        "boundaries": {
            "tradable": False,
            "established_grade": False,
            "writes_feature_values": False,
            "auto_order": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="PME S4 進化結果唯讀解讀報告")
    p.add_argument("--json", action="store_true", help="輸出 JSON 摘要")
    p.add_argument("--selftest", action="store_true", help="免 DB 自測")
    args = p.parse_args(argv)

    if args.selftest:
        return _selftest()

    from augur.core import db

    if not db.ping():
        print("SKIP: DB 不可達（誠實；非 PASS）", file=sys.stderr)
        return 2

    with db.connect() as conn:
        snap = fetch_interpretation_snapshot(conn)
        if args.json:
            print(json.dumps(_to_json(snap), ensure_ascii=False, indent=2, default=str))
        else:
            print(render_interpretation_markdown(snap))
            # 順便驗證 load 便利入口與 render 一致前綴
            md2 = load_interpretation_markdown(conn=conn)
            if not md2.startswith("## PME S4"):
                print("WARN: load_interpretation_markdown 異常", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""🎯 唯讀：manual validation_evidence 有效期落在 2026-10-09～10-10 的列數（10-14 同綁項探針）。

執行指令矩陣
------------
    python3 scripts/probe_ve_manual_1014_window.py            # 印計數
    python3 scripts/probe_ve_manual_1014_window.py --selftest # 免 DB（只驗本檔矩陣）
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        src = open(__file__, encoding="utf-8").read()
        ok = "執行指令矩陣" in src and "validation_evidence" in src
        print(("✓" if ok else "✗") + " selftest")
        return 0 if ok else 1
    from augur.core import db
    with db.connect() as c, c.cursor() as cur:
        cur.execute(
            """SELECT count(*) FROM validation_evidence
               WHERE check_type='manual'
                 AND valid_until::date BETWEEN DATE '2026-10-09' AND DATE '2026-10-10'"""
        )
        print(cur.fetchone()[0], "manual_ve_valid_until_1014window")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

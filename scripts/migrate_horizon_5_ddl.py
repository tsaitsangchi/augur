#!/usr/bin/env python
"""H5 納入相對機率層 horizon CHECK — 另開 5 交易日窗（2026-08-14）。

🎯 這支在做什麼（白話）：Steward 准加入 H5。本遷移冪等把四表 CHECK 對齊
   `closed_horizons.CHECK_ANY`（含 5、不准 82），並給 econ_verdict_rule 一列
   **thin_unestablished**（未經濟終關；H20 已 dead 不代表本窗已終關）。
   H5 ≠ 日頻 D 軌 k=5。不 emit B3、不 approve GATE。

執行指令矩陣:
  python scripts/migrate_horizon_5_ddl.py              # 無參數＝印現況（唯讀）
  python scripts/migrate_horizon_5_ddl.py --run        # ALTER CHECK＋seed 5
  python scripts/migrate_horizon_5_ddl.py --verify     # 斷言 CHECK 含 5、無 82、H5 rule 在
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.core.closed_horizons import CHECK_ANY

NEW_ANY = "ARRAY[" + ", ".join(str(h) for h in CHECK_ANY) + "]"
TABLES = (
    "probability_oos_sample",
    "probability_calibrator",
    "prediction_probability",
    "econ_verdict_rule",
)


def _def(cur, table: str) -> str:
    cur.execute(
        """
        SELECT pg_get_constraintdef(c.oid)
          FROM pg_constraint c
         WHERE c.conrelid = %s::regclass
           AND c.conname = %s
        """,
        (table, f"{table}_horizon_check"),
    )
    row = cur.fetchone()
    return row[0] if row else ""


def status(cur) -> None:
    print("═══ horizon CHECK 現況 ═══")
    for t in TABLES:
        d = _def(cur, t)
        print(f"  {t}: {d or '(缺約束)'}")
    cur.execute("SELECT horizon, verdict FROM econ_verdict_rule ORDER BY 1")
    print("econ_verdict_rule:", list(cur.fetchall()))


def run(cur) -> None:
    if 5 not in CHECK_ANY:
        print("✗ closed_horizons.CHECK_ANY 無 5；先改 SSOT")
        sys.exit(2)
    for t in TABLES:
        cname = f"{t}_horizon_check"
        cur.execute(f"ALTER TABLE {t} DROP CONSTRAINT IF EXISTS {cname}")
        cur.execute(
            f"ALTER TABLE {t} ADD CONSTRAINT {cname} "
            f"CHECK ((horizon = ANY ({NEW_ANY})))"
        )
        print(f"✓ {t} CHECK → {NEW_ANY}")
    cur.execute(
        """
        INSERT INTO econ_verdict_rule (horizon, verdict, source_report, note)
        VALUES (
          5,
          'thin_unestablished',
          'H5 另開 2026-08-14',
          '5 交易日窗；≠ D 軌 k=5；未經濟終關；禁塗 established／dead'
        )
        ON CONFLICT (horizon) DO NOTHING
        """
    )
    print("✓ econ_verdict_rule seed H5=thin_unestablished")


def verify(cur) -> int:
    ok = True
    for t in TABLES:
        d = _def(cur, t)
        compact = d.replace(" ", "")
        if "ARRAY[5," not in compact:
            print(f"✗ {t} CHECK 無 5: {d}")
            ok = False
        elif "82" in compact:
            print(f"✗ {t} CHECK 仍含 82: {d}")
            ok = False
        else:
            print(f"✓ {t} CHECK 含 5、不准 82")
    cur.execute("SELECT verdict FROM econ_verdict_rule WHERE horizon=5")
    row = cur.fetchone()
    if not row or row[0] != "thin_unestablished":
        print(f"✗ econ_verdict_rule H5 缺或非 thin_unestablished: {row}")
        ok = False
    else:
        print("✓ econ_verdict_rule H5=thin_unestablished")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="H5 horizon CHECK 遷移")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args(argv)
    with db.connect() as conn, db.transaction(conn) as cur:
        if args.run:
            run(cur)
        if args.verify:
            return verify(cur)
        if not args.run:
            print(__doc__)
            status(cur)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

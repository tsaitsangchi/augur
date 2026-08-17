#!/usr/bin/env python
"""H90 取代 H82 — CHECK 改作業閉集、**刪除**庫內 H82（2026-08-14）。

🎯 這支在做什麼（白話）：Steward「全部改開 H90、取消 H82」＋「H82 不保留要刪掉」。
   冪等：(1) 刪 horizon／horizon_td＝82 之作業列、H82 registry／artifact、H82 gate 列；
   (2) 四表 CHECK 改為 {20,40,60,90,120,240}（**不准 82**）；
   (3) econ_verdict_rule 只留 H90＝thin_unestablished。
   凍結家族配方仍在 preregister 代碼；庫列刪除後不得無新 GO 再插入。
   不 emit B3、不 approve GATE。

執行指令矩陣:
  python scripts/migrate_horizon_90_replace_82_ddl.py              # 無參數＝印現況（唯讀）
  python scripts/migrate_horizon_90_replace_82_ddl.py --run        # 刪 H82＋ALTER CHECK＋seed 90
  python scripts/migrate_horizon_90_replace_82_ddl.py --verify     # 斷言 CHECK 無 82、H82 列＝0、H90 rule 在
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db
from augur.core.closed_horizons import CHECK_ANY

NEW_ANY = "ARRAY[" + ", ".join(str(h) for h in CHECK_ANY) + "]"
CHECK_TABLES = (
    "probability_oos_sample",
    "probability_calibrator",
    "prediction_probability",
    "econ_verdict_rule",
)
PURGE_HORIZON = (
    "prediction_probability",
    "probability_calibrator",
    "probability_oos_sample",
    "market_direction_probability",
    "direction_oos_sample",
    "direction_combo_oos_sample",
    "direction_probability",
)
PURGE_HORIZON_TD = (
    "direction_arena_prediction",
    "direction_arena_replay",
    "mc_simulation_run",
    "sim_realized_outcome",
)
COUNT_PROBE = PURGE_HORIZON + ("econ_verdict_rule", "model_registry", "direction_gate")


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


def _count(cur, table: str, col: str = "horizon") -> int:
    cur.execute(f'SELECT count(*) FROM "{table}" WHERE "{col}"=82')
    return int(cur.fetchone()[0] or 0)


def status(cur) -> None:
    print("═══ horizon CHECK 現況 ═══")
    for t in CHECK_TABLES:
        d = _def(cur, t)
        print(f"  {t}: {d or '(缺約束)'}")
    cur.execute("SELECT horizon, verdict FROM econ_verdict_rule ORDER BY 1")
    print("econ_verdict_rule:", list(cur.fetchall()))
    print("═══ H82 列數 ═══")
    for t in COUNT_PROBE:
        print(f"  {t}.horizon=82: {_count(cur, t)}")
    cur.execute(
        "SELECT count(*) FROM direction_stack_feature_monthly WHERE feature='rank_pctile_h82'"
    )
    print(f"  monthly rank_pctile_h82: {cur.fetchone()[0]}")
    cur.execute(
        """
        SELECT count(*) FROM prediction_values pv
          JOIN model_registry mr ON mr.model_id=pv.model_id
         WHERE mr.horizon=82
        """
    )
    print(f"  prediction_values via H82 models: {cur.fetchone()[0]}")
    cur.execute("SELECT gate_id, status FROM direction_gate WHERE horizon=82 ORDER BY 1")
    print("  direction_gate H82:", list(cur.fetchall()))


def _purge_h82(cur) -> None:
    cur.execute(
        """
        DELETE FROM prediction_values
         WHERE model_id IN (SELECT model_id FROM model_registry WHERE horizon=82)
        """
    )
    print(f"✓ DELETE prediction_values H82 models: {cur.rowcount}")
    for t in PURGE_HORIZON:
        cur.execute(f'DELETE FROM "{t}" WHERE horizon=82')
        print(f"✓ DELETE {t} horizon=82: {cur.rowcount}")
    for t in PURGE_HORIZON_TD:
        cur.execute(
            "SELECT to_regclass(%s)", (f"public.{t}",)
        )
        if cur.fetchone()[0]:
            cur.execute(f'DELETE FROM "{t}" WHERE horizon_td=82')
            print(f"✓ DELETE {t} horizon_td=82: {cur.rowcount}")
    cur.execute(
        "DELETE FROM direction_stack_feature_monthly WHERE feature='rank_pctile_h82'"
    )
    print(f"✓ DELETE monthly rank_pctile_h82: {cur.rowcount}")
    cur.execute(
        """
        DELETE FROM direction_econ_verdict
         WHERE gate_id IN (SELECT gate_id FROM direction_gate WHERE horizon=82)
        """
    )
    print(f"✓ DELETE direction_econ_verdict H82 gates: {cur.rowcount}")
    cur.execute(
        """
        DELETE FROM daily_direction_probability
         WHERE gate_id IN (SELECT gate_id FROM direction_gate WHERE horizon=82)
        """
    )
    print(f"✓ DELETE daily_direction_probability H82 gates: {cur.rowcount}")
    cur.execute("ALTER TABLE direction_gate DISABLE TRIGGER trg_direction_no_goalpost")
    cur.execute("DELETE FROM direction_gate WHERE horizon=82")
    print(f"✓ DELETE direction_gate horizon=82: {cur.rowcount}")
    cur.execute("ALTER TABLE direction_gate ENABLE TRIGGER trg_direction_no_goalpost")
    cur.execute(
        """
        SELECT artifact_path FROM model_registry
         WHERE horizon=82 AND artifact_path IS NOT NULL
           AND artifact_path NOT LIKE 'GHOST%'
        """
    )
    paths = [r[0] for r in cur.fetchall()]
    cur.execute("DELETE FROM model_registry WHERE horizon=82")
    print(f"✓ DELETE model_registry horizon=82: {cur.rowcount}")
    n_art = 0
    for p in paths:
        fp = Path(p)
        if fp.is_file():
            fp.unlink()
            n_art += 1
    print(f"✓ unlink H82 artifacts: {n_art}/{len(paths)}")
    cur.execute("DELETE FROM econ_verdict_rule WHERE horizon=82")
    print(f"✓ DELETE econ_verdict_rule H82: {cur.rowcount}")


def run(cur) -> None:
    _purge_h82(cur)
    for t in CHECK_TABLES:
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
          90,
          'thin_unestablished',
          'H90 取代 H82 2026-08-14',
          '作業閉集改 90 交易日；H82 已刪、CHECK 不准 82；禁塗 established／dead'
        )
        ON CONFLICT (horizon) DO UPDATE SET
          note = EXCLUDED.note,
          source_report = EXCLUDED.source_report
        """
    )
    print("✓ econ_verdict_rule seed H90=thin_unestablished")


def verify(cur) -> int:
    ok = True
    for t in CHECK_TABLES:
        d = _def(cur, t)
        if "90" not in d:
            print(f"✗ {t} CHECK 無 90: {d}")
            ok = False
        elif "82" in d:
            print(f"✗ {t} CHECK 仍含 82: {d}")
            ok = False
        else:
            print(f"✓ {t} CHECK 含 90、不准 82")
    cur.execute("SELECT verdict FROM econ_verdict_rule WHERE horizon=90")
    row = cur.fetchone()
    if not row or row[0] != "thin_unestablished":
        print(f"✗ econ_verdict_rule H90 缺或非 thin_unestablished: {row}")
        ok = False
    else:
        print("✓ econ_verdict_rule H90=thin_unestablished")
    cur.execute("SELECT 1 FROM econ_verdict_rule WHERE horizon=82")
    if cur.fetchone():
        print("✗ econ_verdict_rule H82 仍在")
        ok = False
    else:
        print("✓ econ_verdict_rule 無 H82")
    leftover = []
    for t in COUNT_PROBE:
        n = _count(cur, t)
        if n:
            leftover.append(f"{t}={n}")
    cur.execute(
        "SELECT count(*) FROM direction_stack_feature_monthly WHERE feature='rank_pctile_h82'"
    )
    n_m = int(cur.fetchone()[0] or 0)
    if n_m:
        leftover.append(f"monthly_h82={n_m}")
    if leftover:
        print("✗ H82 列仍在: " + ", ".join(leftover))
        ok = False
    else:
        print("✓ 作業表 H82 列＝0")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="H90 取代 H82：刪 H82＋CHECK 遷移")
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

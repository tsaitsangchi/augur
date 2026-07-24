#!/usr/bin/env python
"""哲學假說↔特徵覆蓋審計 — PME S0 盤點＋S1 覆蓋（零市場 API）。

🎯 這支在做什麼（白話）：讀 philosophy_*／principle_factor_map／feature_values，印 S0 現況
   （schools／principles status／validated 覆蓋／G-ISO）與 S1 覆蓋類別
   （mapped｜missing｜retired｜blocked_div）。可選寫 evolution_coverage_snapshot。
   dividend 族標 blocked_div（G-DIV-1 PAUSED）；禁把 missing 當已驗證。

守 #1 #15 #29；計畫 §4 S0／S1；FZ-keep。

執行指令矩陣:
  python scripts/audit_philosophy_feature_coverage.py              # S0+S1 報告（唯讀）
  python scripts/audit_philosophy_feature_coverage.py --inventory  # 僅 S0
  python scripts/audit_philosophy_feature_coverage.py --write-snapshot  # 需表；建 coverage run＋寫入
  python scripts/audit_philosophy_feature_coverage.py --selftest   # 免 DB
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date

import _bootstrap  # noqa: F401

from augur.philosophy.evolution import (
    DEFAULT_GATE_CONFIG,
    classify_coverage,
    KILL_CLEAR,
)


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("blocked_div 優先於 in_fv", classify_coverage("dividend_yield", in_feature_values=True) == "blocked_div")
    chk("missing", classify_coverage("roe", in_feature_values=False) == "missing")
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _code_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()[:64]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _g_iso_line() -> tuple[str, int]:
    try:
        from augur.audit.import_isolation import check_isolation

        v = check_isolation()
        return ("PASS" if not v else "FAIL"), len(v)
    except Exception as e:  # noqa: BLE001 — 盤點誠實
        return f"SKIP({e.__class__.__name__})", -1


def inventory(cur) -> dict:
    out: dict = {}
    cur.execute("SELECT count(*) FROM philosophy_school")
    out["schools"] = cur.fetchone()[0]
    cur.execute("SELECT status, count(*) FROM philosophy_principle GROUP BY 1 ORDER BY 1")
    out["principle_status"] = {r[0]: r[1] for r in cur.fetchall()}
    cur.execute("SELECT count(*) FROM principle_factor_map")
    out["maps"] = cur.fetchone()[0]
    cur.execute(
        "SELECT count(*) FILTER (WHERE validated_ic IS NOT NULL), "
        "count(*) FILTER (WHERE validated_econ IS NOT NULL) FROM principle_factor_map"
    )
    vic, ve = cur.fetchone()
    out["validated_ic"] = vic
    out["validated_econ"] = ve
    cur.execute("SELECT count(DISTINCT feature) FROM feature_values")
    out["fv_features"] = cur.fetchone()[0]
    # status 不一致：有 validated_* 但 principle 仍 untested
    cur.execute(
        """
        SELECT count(DISTINCT p.principle_id)
        FROM philosophy_principle p
        JOIN principle_factor_map m ON m.principle_id = p.principle_id
        WHERE p.status = 'untested'
          AND (m.validated_ic IS NOT NULL OR m.validated_econ IS NOT NULL)
        """
    )
    out["status_desync_principles"] = cur.fetchone()[0]
    return out


def coverage_rows(cur) -> list[dict]:
    cur.execute(
        """
        SELECT m.feature, count(*) AS map_count,
               EXISTS(SELECT 1 FROM feature_values fv WHERE fv.feature = m.feature) AS in_fv
        FROM principle_factor_map m
        GROUP BY m.feature
        ORDER BY m.feature
        """
    )
    rows = []
    for feature, map_count, in_fv in cur.fetchall():
        cls = classify_coverage(feature, in_feature_values=bool(in_fv))
        rows.append({
            "feature": feature,
            "map_count": int(map_count),
            "in_feature_values": bool(in_fv),
            "coverage_class": cls,
        })
    return rows


def print_report(inv: dict, rows: list[dict], *, inventory_only: bool) -> None:
    iso, n_iso = _g_iso_line()
    print("── PME S0 盤點 ──")
    print(f"  schools={inv['schools']}  maps={inv['maps']}  fv_features={inv['fv_features']}")
    print(f"  principle_status={inv['principle_status']}")
    print(f"  validated_ic={inv['validated_ic']}  validated_econ={inv['validated_econ']}")
    print(f"  status_desync(untested∩validated_*)={inv['status_desync_principles']}")
    print(f"  G-ISO={iso}" + (f" violations={n_iso}" if n_iso >= 0 else ""))
    print("  ⚠ FZ-keep：FinMind／FRED 凍結；G-DIV-1 Dividend PAUSED；禁確立級宣稱")
    print("  ⚠ [I] 靈魂措辭另案 pending（PME-AUTO-B 張力；不擅改 [N]）")
    if inventory_only:
        return
    tallies: dict[str, int] = {}
    for r in rows:
        tallies[r["coverage_class"]] = tallies.get(r["coverage_class"], 0) + 1
    print("── PME S1 覆蓋 ──")
    print(f"  classes={tallies}  distinct_features={len(rows)}")
    for r in rows:
        flag = {"mapped": "✓", "missing": "⊘", "retired": "∅", "blocked_div": "⛔"}.get(
            r["coverage_class"], "?"
        )
        print(
            f"  {flag} {r['feature']:40} class={r['coverage_class']:12} "
            f"maps={r['map_count']} in_fv={r['in_feature_values']}"
        )


def write_snapshot(conn, rows: list[dict]) -> int:
    from augur.core import db

    with db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.evolution_run')")
        if cur.fetchone()[0] is None:
            print("✗ evolution 表未建 — 先: python scripts/migrate_philosophy_evolution_ddl.py --run")
            return 1
        cur.execute("SELECT state FROM evolution_kill_switch WHERE switch_id=1")
        ks = cur.fetchone()
        kill_at = ks[0] if ks else KILL_CLEAR
        cfg = dict(DEFAULT_GATE_CONFIG)
        cfg["phase"] = "S1-coverage"
        cur.execute(
            """
            INSERT INTO evolution_run
              (since_date, horizon_h, code_sha, config_json, status, kill_switch_at_start, notes)
            VALUES (%s, %s, %s, %s::jsonb, 'succeeded', %s, %s)
            RETURNING run_id
            """,
            (
                date(2021, 1, 1),
                60,
                _code_sha(),
                json.dumps(cfg),
                kill_at,
                "S1 coverage snapshot only",
            ),
        )
        run_id = cur.fetchone()[0]
        for r in rows:
            cur.execute(
                """
                INSERT INTO evolution_coverage_snapshot
                  (run_id, feature, map_count, in_feature_values, coverage_class, detail)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                """,
                (
                    run_id,
                    r["feature"],
                    r["map_count"],
                    r["in_feature_values"],
                    r["coverage_class"],
                    json.dumps({"source": "audit_philosophy_feature_coverage"}),
                ),
            )
        cur.execute(
            "UPDATE evolution_run SET finished_at=now() WHERE run_id=%s",
            (run_id,),
        )
    print(f"✓ wrote coverage snapshot run_id={run_id} rows={len(rows)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--inventory", action="store_true", help="僅 S0")
    ap.add_argument("--write-snapshot", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()

    from augur.core import db

    with db.connect() as conn, db.transaction(conn) as cur:
        inv = inventory(cur)
        rows = [] if args.inventory else coverage_rows(cur)
    print_report(inv, rows, inventory_only=args.inventory)
    if args.write_snapshot:
        if args.inventory:
            print("✗ --write-snapshot 需完整覆蓋列（勿併用 --inventory）")
            return 2
        with db.connect() as conn:
            return write_snapshot(conn, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

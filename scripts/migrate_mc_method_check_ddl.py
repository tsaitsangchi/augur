#!/usr/bin/env python
"""mc_simulation_run.method CHECK 白名單加寬 — 納 stationary_bootstrap/garch_fhs(方法擴充計畫 2026-07-26 hugo 拍板)。
🎯 這支在做什麼(白話):組合風險模擬擴兩個對照組方法,但 method 欄 CHECK 白名單只認原五值、新值寫不進——
   本支把白名單加寬為七值。**白名單保留**(繼續機械擋 typo 方法名,非改自由文字);冪等(已含七值即跳過)。
守 #6(DDL 明示執行)· #12(改約束非手補資料)· #29a/d。
執行指令矩陣:
  python scripts/migrate_mc_method_check_ddl.py            # 無參數:現況(唯讀:印現行約束定義)
  python scripts/migrate_mc_method_check_ddl.py --apply    # 執行遷移(冪等)
  python scripts/migrate_mc_method_check_ddl.py --dry-run  # 只印將執行之 SQL、不動 DB
  python scripts/migrate_mc_method_check_ddl.py --selftest # 零 DB 紅綠
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

METHODS = ("iid_bootstrap", "block_bootstrap", "stationary_bootstrap", "garch_fhs",
           "episode_replay_2008", "episode_replay_2020", "episode_replay_2022")
CON = "mc_simulation_run_method_check"
SQL = (f"ALTER TABLE mc_simulation_run DROP CONSTRAINT IF EXISTS {CON};\n"
       "ALTER TABLE mc_simulation_run ADD CONSTRAINT " + CON +
       "\n  CHECK (method = ANY (ARRAY[" + ", ".join(f"'{m}'" for m in METHODS) + "]));")


def _current_def(cur):
    cur.execute("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname=%s "
                "AND conrelid='mc_simulation_run'::regclass", (CON,))
    row = cur.fetchone()
    return row[0] if row else None


def apply(dry):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur_def = _current_def(cur)
        if cur_def and all(f"'{m}'" in cur_def for m in METHODS):
            print("✓ 白名單已含七值——冪等跳過"); return 0
        print(SQL)
        if dry:
            print("(--dry-run:未執行)"); return 0
        for stmt in SQL.split(";\n"):
            if stmt.strip():
                cur.execute(stmt)
        print(f"✓ 遷移完成:{CON} 加寬為 {len(METHODS)} 值(白名單保留、typo 仍擋)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        d = _current_def(cur)
        print(f"現行 {CON}:\n  {d}" if d else f"({CON} 不存在)")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("七方法值全入 SQL", all(f"'{m}'" in SQL for m in METHODS) and len(METHODS) == 7)
    chk("原五值保留(不破既有列)", all(m in METHODS for m in
        ("iid_bootstrap", "block_bootstrap", "episode_replay_2008", "episode_replay_2020", "episode_replay_2022")))
    chk("白名單型 CHECK(非自由文字)", "CHECK (method = ANY" in SQL)
    chk("DROP 在 ADD 前(可重入)", SQL.index("DROP CONSTRAINT") < SQL.index("ADD CONSTRAINT"))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="mc_simulation_run.method CHECK 白名單加寬(七值)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.apply or a.dry_run:
        return apply(a.dry_run)
    print(__doc__)
    return status()


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""meta-replay 帳本遷移 — 程序重演軌兩表(META-REPLAY-go,hugo 2026-07-29)。

🎯 這支在做什麼(白話):meta_replay_cutoff(每 cutoff 之 prodset+逐候選決策 JSON,proc_sha 鎖程序版)
   ＋meta_replay_perf(程序集 vs 靜態基準之次期 IC)。程序中途改=新 proc_sha 新家族,舊列留檔。
守 #15(決策全 JSON 可溯)· #29a/d。SSOT=reports/augur_meta_replay_plan_20260729.md §四。

執行指令矩陣:
  python scripts/migrate_meta_replay_ddl.py            # 無參數:現況(唯讀)
  python scripts/migrate_meta_replay_ddl.py --apply    # 遷移(冪等)
  python scripts/migrate_meta_replay_ddl.py --selftest # 零 DB 紅綠
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

SQL = """
CREATE TABLE IF NOT EXISTS meta_replay_cutoff (
    proc_sha    TEXT NOT NULL,
    cutoff_date DATE NOT NULL,
    prodset     JSONB NOT NULL,
    decisions   JSONB NOT NULL,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (proc_sha, cutoff_date));
CREATE TABLE IF NOT EXISTS meta_replay_perf (
    proc_sha       TEXT NOT NULL,
    cutoff_date    DATE NOT NULL,
    model          TEXT NOT NULL CHECK (model IN ('B2_ridge', 'M1_gbdt')),
    ic_next        NUMERIC,
    ic_next_static NUMERIC,
    n_stocks       INT,
    PRIMARY KEY (proc_sha, cutoff_date, model));
"""


def apply(dry=False):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.meta_replay_perf')")
        if cur.fetchone()[0] is not None:
            print("✓ 表皆在——冪等跳過")
            return 0
        if dry:
            print(SQL)
            return 0
        cur.execute(SQL)
        print("✓ meta-replay 兩表落地")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.meta_replay_cutoff')")
        if cur.fetchone()[0] is None:
            print("  (表未建;--apply)")
            return 0
        cur.execute("""SELECT proc_sha, count(*), min(cutoff_date), max(cutoff_date)
                       FROM meta_replay_cutoff GROUP BY 1 ORDER BY 1""")
        for r in cur.fetchall():
            print(f"  {r[0]} {r[1]} cutoff({r[2]}→{r[3]})")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("PK 含 proc_sha(改程序=新家族)", SQL.count("proc_sha") >= 4)
    chk("perf 模型枚舉 CHECK", "'B2_ridge', 'M1_gbdt'" in SQL)
    chk("決策 JSON 欄(可溯)", "decisions   JSONB NOT NULL" in SQL)
    chk("冪等", "IF NOT EXISTS" in SQL)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="meta-replay 帳本遷移")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.apply or a.dry_run:
        return apply(a.dry_run)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())

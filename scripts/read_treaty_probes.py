#!/usr/bin/env python3
"""🎯 跑探針 `check_cmd` → append `treaty_probe_reading`（M-N1 量測端）。

AI **只登錄量到的值**。`owner=Steward` 之 reading 一律 `verdict=undecidable`
（DB CHECK 亦擋 meets／not_meets）。`--check`＝每條綁定至少一列 reading 且
Steward 框無 meets。

守原則 #15（不代勾 10-14）#29a/d；RULING-2026-039 禁假關。

執行指令矩陣
------------
    python3 scripts/read_treaty_probes.py                 # 無參數＝印矩陣＋--check
    python3 scripts/read_treaty_probes.py --check         # 唯讀：覆蓋／人裁誠實
    python3 scripts/read_treaty_probes.py --apply         # 對所有綁定跑 check_cmd 並寫 reading
    python3 scripts/read_treaty_probes.py --probe ID      # 單條（須 --apply 才寫）
    python3 scripts/read_treaty_probes.py --selftest      # 免 DB
"""
from __future__ import annotations

import argparse
import subprocess
import sys

import _bootstrap  # noqa: F401


def _conn():
    from augur.core import db
    return db.connect()


def _run_cmd(cmd: str, timeout: int = 60) -> tuple[int, str]:
    try:
        # shell=True：種子 check_cmd 含管道／psql 引號；timeout 防掛
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=_repo()
        )
        out = (r.stdout or "") + (("\n" + r.stderr) if r.stderr else "")
        return r.returncode, out.strip()[:4000] or f"(empty; rc={r.returncode})"
    except subprocess.TimeoutExpired:
        return 124, f"(timeout {timeout}s)"
    except OSError as e:
        return 127, f"(oserror {e})"


def _repo():
    from pathlib import Path
    return str(Path(__file__).resolve().parent.parent)


def _verdict_for(owner: str, expect_expr: str, value_text: str) -> str:
    """人裁框永遠 undecidable；機器框才比 expect（本輪種子全 Steward）。"""
    if owner == "Steward":
        return "undecidable"
    if expect_expr == "undecidable":
        return "undecidable"
    if expect_expr.startswith("contains:"):
        needle = expect_expr.split(":", 1)[1]
        return "meets" if needle in value_text else "not_meets"
    if expect_expr.startswith("eq:"):
        return "meets" if value_text == expect_expr[3:] else "not_meets"
    return "undecidable"


def cmd_check() -> int:
    with _conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.treaty_probe_binding')")
        if cur.fetchone()[0] is None:
            print("✗ 表不在")
            return 1
        cur.execute("SELECT count(*) FROM treaty_probe_binding")
        n_bind = cur.fetchone()[0]
        cur.execute(
            """SELECT b.probe_id, b.owner,
                      (SELECT count(*) FROM treaty_probe_reading r WHERE r.probe_id=b.probe_id) AS n_r
               FROM treaty_probe_binding b ORDER BY 1"""
        )
        rows = cur.fetchall()
        missing = [p for p, _, n in rows if n == 0]
        for p, owner, n in rows:
            print(f"  {p:28s} owner={owner:7s} readings={n}")
        cur.execute(
            """SELECT count(*) FROM treaty_probe_reading
               WHERE probe_owner='Steward' AND verdict <> 'undecidable'"""
        )
        bad_st = cur.fetchone()[0]
        print(f"綁定 {n_bind}｜缺 reading {len(missing)}｜Steward 非 undecidable {bad_st}")
        if missing or bad_st:
            if missing:
                print("缺：" + ", ".join(missing))
            return 1
        if n_bind < 13:
            print("⚠ 綁定 <13（seed 未跑完）")
            return 1
        print("✓ --check 通過")
        return 0


def cmd_apply(probe_filter: str | None) -> int:
    from augur.core import db
    with _conn() as conn, db.transaction(conn) as cur:
        cur.execute(
            """SELECT probe_id, owner, check_cmd, expect_expr
               FROM treaty_probe_binding
               WHERE (%s::text IS NULL OR probe_id=%s)
               ORDER BY probe_id""",
            (probe_filter, probe_filter),
        )
        bindings = cur.fetchall()
        if not bindings:
            print("✗ 無綁定可讀" + (f"（probe={probe_filter}）" if probe_filter else "——先 sync --seed-1014"))
            return 1
        n_ok = 0
        for probe_id, owner, check_cmd, expect_expr in bindings:
            rc, value = _run_cmd(check_cmd)
            verdict = _verdict_for(owner, expect_expr, value)
            note = f"check_rc={rc}"
            cur.execute(
                """INSERT INTO treaty_probe_reading
                     (probe_id, probe_owner, value_text, verdict, machine_note)
                   VALUES (%s,%s,%s,%s,%s)""",
                (probe_id, owner, value, verdict, note),
            )
            print(f"  {probe_id}: verdict={verdict}  value={value[:80]!r}…")
            n_ok += 1
    print(f"✓ 寫入 {n_ok} 列 reading")
    return cmd_check()


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("Steward → undecidable", _verdict_for("Steward", "contains:x", "x") == "undecidable")
    chk("AI contains 綠", _verdict_for("AI", "contains:[ ]", "- [ ] foo") == "meets")
    chk("AI contains 紅", _verdict_for("AI", "contains:[x]", "- [ ] foo") == "not_meets")
    chk("AI eq", _verdict_for("AI", "eq:ok", "ok") == "meets")
    src = open(__file__, encoding="utf-8").read()
    chk("不寫死 meets 給 Steward", "if owner == \"Steward\"" in src or "owner == 'Steward'" in src)
    print("自測：" + ("全通過 ✓" if ok else "失敗 ✗"))
    return 0 if ok else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--check", action="store_true")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--probe")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.apply:
        return cmd_apply(args.probe)
    if args.probe and not args.apply:
        print("✗ --probe 須搭配 --apply")
        return 2
    if args.check or len(sys.argv) <= 1:
        if len(sys.argv) <= 1:
            print(__doc__)
        return cmd_check()
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

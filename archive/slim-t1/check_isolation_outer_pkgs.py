#!/usr/bin/env python3
"""🎯 隔離閘外圍三包配線探針——arena／execution／deliberation 須在掃描集合（M-O5）。

白話:07-31 單一角色整併後 REVOKE 對偶消失 ⇒ AST/字面閘為唯一閘。
  master 原載三包「不在任何字面掃描集合」；現行 `import_isolation.OUTER_PKGS`
  ＋ deliberation 專掃已補。本支鎖住**配線不回退**（先驗紅：抽掉 OUTER → 紅）。

守原則 #8 · #15 · #35 · #29a/d。

執行指令矩陣
------------
    python3 scripts/check_isolation_outer_pkgs.py            # 無參數＝--check
    python3 scripts/check_isolation_outer_pkgs.py --check    # 配線缺漏 → rc=1
    python3 scripts/check_isolation_outer_pkgs.py --selftest
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

REQUIRED_OUTER = frozenset({"arena", "execution", "identity"})
REQUIRED_DELIB_MARK = "deliberation"


def wiring_ok(*, outer: tuple | list | set, check_src: str) -> tuple[bool, list[str]]:
    """OUTER_PKGS 含三包＋check_isolation 正文掃 deliberation。純函式。"""
    miss = []
    have = set(outer)
    for p in REQUIRED_OUTER:
        if p not in have:
            miss.append(f"OUTER_PKGS 缺 {p}")
    if REQUIRED_DELIB_MARK not in check_src:
        miss.append("check_isolation 路徑未提及 deliberation")
    # 「字面面」：必須有 _string_ref_violations 或同等字面掃描仍存在（不撤掉字面閘）
    if "_string_ref_violations" not in check_src:
        miss.append("字面掃描 _string_ref_violations 消失")
    if "OUTER_PKGS" not in check_src and "outer-import" not in check_src:
        miss.append("outer-import AST 掃描配線消失")
    return (not miss), miss


def _check() -> int:
    from augur.audit import import_isolation as iso
    import inspect

    src = inspect.getsource(iso.check_isolation)
    ok, miss = wiring_ok(outer=iso.OUTER_PKGS, check_src=src)
    print("── 隔離外圍三包配線（M-O5）──")
    print(f"  OUTER_PKGS={iso.OUTER_PKGS}")
    print(f"  DELIB_FORBIDDEN={getattr(iso, 'DELIB_FORBIDDEN', ())}")
    if ok:
        print("  ✓ 配線在（arena/execution/identity AST + deliberation 專掃 + 字面閘仍在）")
        return 0
    print("  ✗ 配線缺口:")
    for m in miss:
        print(f"    · {m}")
    return 1


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    good_src = (
        "return (_ast_import_scan(OUTER_PKGS)...outer-import\n"
        "+ _ast_import_scan(deliberation)...\n"
        "+ _string_ref_violations(...))"
    )
    o, miss = wiring_ok(outer=("arena", "execution", "identity"), check_src=good_src)
    chk("完整配線 → ok", o and not miss)
    o2, miss2 = wiring_ok(outer=("arena",), check_src=good_src)
    chk("先驗紅：缺 execution/identity", (not o2) and any("execution" in m for m in miss2))
    o3, _ = wiring_ok(outer=REQUIRED_OUTER, check_src="只剩 AST 無字面")
    chk("先驗紅：字面閘消失", not o3)

    print("自測:全通過 ✓" if ok else "自測:有失敗 ✗")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="隔離外圍三包配線探針（M-O5）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    return _check()


if __name__ == "__main__":
    sys.exit(main())

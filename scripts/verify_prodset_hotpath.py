#!/usr/bin/env python
"""prodset 熱路徑哨兵 — P2H S1–S3 機械驗收（零 FinMind／FRED）。

🎯 這支在做什麼（白話）：檢查 active 列、resolve 非空且 ⊆active、PIPELINE 零 philosophy
   import、可選 dry train／predict 解析。不宣稱可交易／確立級。

守 #1 #15 #28；計畫 SSOT＝reports/augur_prodset_predict_hotpath_plan_20260724.md。

執行指令矩陣:
  python scripts/verify_prodset_hotpath.py                 # 印矩陣（安全）
  python scripts/verify_prodset_hotpath.py --check         # 哨兵（DB＋isolation）
  python scripts/verify_prodset_hotpath.py --selftest      # 零 IO 結構鎖
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401


def _selftest() -> int:
    ok = True

    def chk(name: str, cond: bool) -> None:
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    from augur.core import prodset_contract as pc
    from augur.evaluation import baseline
    from augur.audit import import_isolation as iso

    chk("prodset_contract 常數", pc.PRODSET_TABLE == "evolution_production_feature_set")
    chk("resolve_train_feats 預設 prodset",
        __import__("inspect").signature(baseline.resolve_train_feats).parameters["source"].default == "prodset")
    v = iso.check_isolation()
    chk("import_isolation 0 違規", v == [])
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _check() -> int:
    from augur.audit import import_isolation as iso
    from augur.core import db
    from augur.core.prodset_contract import load_active_features, resolve_prodset_feats
    from augur.evaluation import baseline

    fails = []
    v = iso.check_isolation()
    if v:
        fails.append(f"isolation {len(v)} violations")
        for line in v[:5]:
            print("  ", line)
    else:
        print("✓ isolation 0 違規")

    with db.connect() as conn:
        active = load_active_features(conn)
        print(f"✓ active n={len(active)} feats={active}")
        if not active:
            fails.append("prodset active empty")
        with db.transaction(conn) as cur:
            cur.execute(
                f"SELECT DISTINCT panel_date FROM {baseline.FEATURE_TABLE} "
                f"WHERE panel_date<=(SELECT max(as_of_date) FROM {baseline.ASOF_TABLE}) "
                f"ORDER BY panel_date"
            )
            panels = [r[0] for r in cur.fetchall()]
        resolved = resolve_prodset_feats(conn, panels)
        print(f"✓ resolve n_feats={len(resolved)} feats={resolved}")
        if active and not resolved:
            fails.append("resolve empty despite active")
        if not set(resolved).issubset(set(active)):
            fails.append("resolved not ⊆ active")
        # 原此處以受限 role `augur_predict` 之 GRANT 逐表驗 #8 隔離之 DB 層。
        # 2026-07-31 單一角色整併後該 role 退役 ⇒ **DB 層之隔離判準不復存在**（非「改用別的方式驗」，
        # 是這一層沒有了）。此處誠實印出射程縮減，不留「看似仍在驗」之殘骸。
        # 現行 #8 之唯一機械落點＝`src/augur/audit/import_isolation.py` 之 AST 稽核（射程 7 package）。
        # 依據＝reports/augur_single_role_consolidation_plan_20260731.md
        print("⚠ 射程註記：predict role 已退役，本檢查不再涵蓋 #8 之 DB 層"
              "（現唯 AST 稽核；見 tests/test_philosophy_isolation.py）")

    if fails:
        print("✗ FAIL:", "; ".join(fails))
        return 1
    print("✓ verify_prodset_hotpath PASS（≠可交易／≠解凍）")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="prodset 熱路徑哨兵")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.check:
        return _check()
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

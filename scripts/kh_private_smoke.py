#!/usr/bin/env python3
"""KH 私有／ASR readout 回歸 smoke（r14 #26 固化）。

矩陣（對齊 KH-PARALLEL-WP-K）：
  1) AVI 讀出 · 未登入 → 0 cite
  2) AVI 讀出 · super → ≥1 且 via=asr_transcribe · 錨 1818835
  3) AVI 讀出 · owner:1 → ≥1 且 via 標記
  4) DOC 讀出 · super · domain local → ≥1 · 錨 1818691

執行指令矩陣:
  python scripts/kh_private_smoke.py           # 跑矩陣；FAIL→rc=1
  python scripts/kh_private_smoke.py --selftest
"""

from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

AVI_Q = "WebService程式撰寫(I).avi：請讀出具體內容"
DOC_Q = "erp專案推動小組織成員.doc：請讀出具體內容"
AVI_ID = 1818835
DOC_ID = 1818691
VIA = "asr_transcribe"


def _run_cases() -> list[tuple[str, bool, str]]:
    from augur.core import db
    from augur.knowledge.readout import advise_readout_citations

    rows: list[tuple[str, bool, str]] = []
    with db.connect() as conn:
        cur = conn.cursor()

        def hit(q, scope):
            return advise_readout_citations(q, scope=scope)

        # 1 unauth
        c0 = hit(AVI_Q, None)
        ok = len(c0) == 0
        rows.append(("avi_unauth_zero", ok, f"n={len(c0)}"))

        # 2 super
        c1 = hit(AVI_Q, (True, frozenset({"local"}), None))
        ids = [int(c.item_id) for c in c1 if getattr(c, "item_id", None)]
        blob = "\n".join(getattr(c, "text", "") or "" for c in c1)
        ok = AVI_ID in ids and VIA in blob
        rows.append(("avi_super_via", ok, f"ids={ids[:5]} via={VIA in blob}"))

        # 3 owner 1
        c2 = hit(AVI_Q, (False, frozenset({"local"}), 1))
        ids2 = [int(c.item_id) for c in c2 if getattr(c, "item_id", None)]
        blob2 = "\n".join(getattr(c, "text", "") or "" for c in c2)
        ok = AVI_ID in ids2 and VIA in blob2
        rows.append(("avi_owner1_via", ok, f"ids={ids2[:5]} via={VIA in blob2}"))

        # 4 doc super
        c3 = hit(DOC_Q, (True, frozenset({"local"}), None))
        ids3 = [int(c.item_id) for c in c3 if getattr(c, "item_id", None)]
        ok = DOC_ID in ids3 and len(c3) >= 1
        rows.append(("doc_super_hit", ok, f"ids={ids3[:5]}"))

        # quiet unused
        _ = cur
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KH private/ASR smoke")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        from augur.knowledge import readout as ro

        assert ro.is_readout_intent(AVI_Q)
        assert ro.is_readout_intent(DOC_Q)
        print("SELFTEST PASS (intent only; DB cases via default run)")
        return 0

    print("══ KH-PRIVATE-SMOKE ══")
    fails = []
    for name, ok, detail in _run_cases():
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name}  {detail}")
        if not ok:
            fails.append(name)
    if fails:
        print(f"SMOKE FAIL: {fails}")
        return 1
    print("SMOKE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

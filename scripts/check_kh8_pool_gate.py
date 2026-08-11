#!/usr/bin/env python3
"""🎯 KH8 M3 答池闸探針——热路径不得仅凭 weight 放行无全文件（code-gate · no-merge）。

守 M3-adopt §硬前置 · pool_gate CONTRACT · #15 · #29 · FZ-keep。

验收：静扫＋函式自测全绿 → rc=0；任一缺口 → rc=1。
本支 **不** 写库、**不** MERGE 影表。

執行指令矩陣:
  python scripts/check_kh8_pool_gate.py
  python scripts/check_kh8_pool_gate.py --check
  python scripts/check_kh8_pool_gate.py --json
  python scripts/check_kh8_pool_gate.py --selftest
"""
from __future__ import annotations

import argparse
import inspect
import json
import re
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

REPO = Path(__file__).resolve().parents[1]


def _src(mod) -> str:
    return inspect.getsource(mod)


def scan_invariants() -> list[dict]:
    """回 failures（空＝全过）。"""
    from augur.knowledge import pool_gate as pg
    from augur.knowledge import evidence as ev
    from augur.knowledge import answer_auto_lift as al
    from augur.knowledge import readout as ro
    from augur.philosophy import retrieval as ret

    fails: list[dict] = []

    def fail(code: str, detail: str) -> None:
        fails.append({"code": code, "detail": detail})

    # 0) 契约模组可测
    if pg._selftest() != 0:
        fail("pool_gate_selftest", "pool_gate --selftest 非 0")

    # 1) evidence：无 text → fail（直判 has_text 或經 pool_gate）
    ev_src = _src(ev.evaluate_item_evidence)
    if "kh8_no_text" not in ev_src:
        fail("kh8_no_text_guard", "evaluate_item_evidence 缺 action=kh8_no_text")
    if "has_text" not in ev_src and "kh8_evaluate_requires_text" not in ev_src:
        fail("kh8_text_predicate", "evaluate_item_evidence 缺 has_text／pool_gate 谓词")

    # 2) AUTO-LIFT activate：has_text 或 pool_gate.activate_source_eligible
    lift_src = _src(al.lift_items)
    if "has_text" not in lift_src and "activate_source_eligible" not in lift_src:
        fail("autolift_has_text", "lift_items 缺 has_text／activate_source_eligible")

    # 3) readout resolve：JOIN item_text
    for name, fn in (
        ("_resolve_by_title", ro._resolve_by_title),
        ("_resolve_by_content_head", ro._resolve_by_content_head),
        ("citations_for_items", ro.citations_for_items),
    ):
        s = _src(fn)
        if "JOIN knowledge_item_text" not in s and "join knowledge_item_text" not in s.lower():
            fail(f"readout_{name}", f"{name} 未 JOIN knowledge_item_text")

    # 4) retrieve_items：须 JOIN item_text；SQL 不得查 weight（docstring 提禁令除外）
    ri = _src(ret.retrieve_items)
    ri_body = re.sub(r'""".*?"""', "", ri, count=1, flags=re.S)
    ri_body = re.sub(r"'''.*?'''", "", ri_body, count=1, flags=re.S)
    if "JOIN knowledge_item_text" not in ri:
        fail("retrieve_items_join_text", "retrieve_items 未 JOIN knowledge_item_text")
    if re.search(
        r"(FROM|JOIN)\s+knowhow_evidence_weight(?!_honest)\b", ri_body, re.I
    ):
        fail("retrieve_items_weight", "retrieve_items SQL 不当查询 knowhow_evidence_weight")

    ra = _src(ret.retrieve_all)
    if "retrieve_items" not in ra:
        fail("retrieve_all_uses_items", "retrieve_all 未走 retrieve_items")

    # 5) 函式语义：weight alone 不足
    if not pg.weight_alone_insufficient(has_weight=True, has_text=False):
        fail("weight_alone", "weight_alone_insufficient 语义崩")
    if pg.answer_pool_eligible(has_text=False, has_weight=True):
        fail("eligible_weight_only", "answer_pool_eligible 不该放行纯 weight")

    return fails


def _check(*, as_json: bool = False) -> int:
    fails = scan_invariants()
    snap = {
        "ok": len(fails) == 0,
        "fail_n": len(fails),
        "fails": fails,
        "contract": __import__(
            "augur.knowledge.pool_gate", fromlist=["CONTRACT"]
        ).CONTRACT,
        "note": "M3 pool-gate code check · no-merge · no DB write",
    }
    if as_json:
        print(json.dumps(snap, ensure_ascii=False, indent=2))
    else:
        print("KH8 M3 pool-gate check")
        print(f"  ok={snap['ok']} fail_n={snap['fail_n']}")
        for f in fails:
            print(f"  ✗ {f['code']}: {f['detail']}")
        if snap["ok"]:
            print("  ✓ all invariants")
    return 0 if snap["ok"] else 1


def _selftest() -> int:
    # 纯逻辑：扫应可调用；另测 classify 不依赖绿库
    fails = scan_invariants()
    print(f"selftest fail_n={len(fails)}")
    return 0 if not fails else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KH8 M3 pool-gate check")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    return _check(as_json=args.json)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""KH ingest-driven 觸發 CLI（階 C）— 量 S*／建議／有界 apply。

執行指令矩陣
------------
  python scripts/kh_ingest_trigger.py              # 同 --check
  python scripts/kh_ingest_trigger.py --check      # 唯讀量測＋建議；寫 baseline
  python scripts/kh_ingest_trigger.py --dry-run    # 印將 apply 的 argv，零副作用（不寫 baseline 外之跑）
  python scripts/kh_ingest_trigger.py --apply      # 有界執行（須環境或本旗；一次一槍）
  python scripts/kh_ingest_trigger.py --selftest

護欄: 無日曆假進化；不默開 AUTO-LIFT；與 B3 搶資源時勿對 LLM 重活硬搶。
"""

from __future__ import annotations

import argparse
import os
import sys

import _bootstrap  # noqa: F401


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="KH ingest-trigger C")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true",
                    help="有界 apply（等同 AUGUR_KH_INGEST_TRIGGER_APPLY=1 本行程）")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    from augur.knowledge import ingest_triggers as it

    if a.selftest:
        return it.selftest()

    if a.apply:
        os.environ[it.ENV_APPLY] = "1"

    if not it.enabled():
        print(f"SKIP: {it.ENV_ENABLE}=0")
        return 0

    from augur.core import db

    with db.connect() as conn:
        cur = conn.cursor()
        sig = it.measure_signals(cur)
    acts = it.recommend(sig)
    print(it.format_report(sig, acts))

    if a.dry_run:
        print("\n── dry-run apply preview ──")
        for row in it.apply_light(acts, dry_run=True):
            print(row)
        it.persist_baseline(sig)
        return 0

    if a.apply or it.apply_enabled():
        print("\n── apply_light ──")
        for row in it.apply_light(acts, dry_run=False):
            print({k: v for k, v in row.items() if k != "stdout_tail"})
            if row.get("stdout_tail"):
                print(row["stdout_tail"][-800:])
        it.persist_baseline(sig)
        return 0

    it.persist_baseline(sig)
    print(f"\n（唯讀；有界執行請 --apply 或 {it.ENV_APPLY}=1）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

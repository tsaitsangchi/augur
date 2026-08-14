#!/usr/bin/env python
"""as-of 就緒探針 — 某日 D 能否收特徵／訓練／出單（唯讀；anti fake-B3）。

🎯 這支在做什麼（白話）：印 PriceAdj／feature_values／core／邊界 A registry，
   並以 exit code 告訴殼下一步：0=ready、2=先 collect、3=假 B3（價還沒到）、4=無價。
   歷史 D（≤價頂）合法；今天還沒進庫的價不合法。零 live API、零寫庫。

執行指令矩陣:
  python scripts/check_asof_ready.py                         # 無 --date＝印本矩陣（不連庫）
  python scripts/check_asof_ready.py --selftest              # 轉呼叫 library 純自測（免 DB）
  python scripts/check_asof_ready.py --date 2026-08-07       # 探 08-07（歷史；預期 ready 或 need_collect）
  python scripts/check_asof_ready.py --date 2026-08-13       # 若價頂仍 08-12 → rc=3 假 B3
  python scripts/check_asof_ready.py --latest-date           # 只印可更新最新日（價頂 ISO）
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

from augur.core import asof_ready, db


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="as-of 就緒探針（唯讀）")
    ap.add_argument("--date", dest="asof", default=None, help="as-of 日 YYYY-MM-DD")
    ap.add_argument("--latest-date", action="store_true", dest="latest_date",
                    help="只印可更新最新日（PriceAdj TAIEX 價頂）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return asof_ready._selftest()
    if args.latest_date:
        with db.connect() as conn, conn.cursor() as cur:
            iso, err = asof_ready.bind_iso(cur, None)
        if err:
            print(err, file=sys.stderr)
            return 4
        print(iso)
        return 0
    if not args.asof:
        print(__doc__)
        return 0
    with db.connect() as conn, conn.cursor() as cur:
        snap = asof_ready.snapshot(cur, args.asof)
    for k in (
        "asof",
        "status",
        "rc",
        "price_max",
        "fv_max",
        "fv_nfeat",
        "fv_nrows",
        "has_core",
        "registry_a",
    ):
        print(f"{k}={snap[k]}")
    st = snap["status"]
    if st == asof_ready.STATUS_READY:
        print("→ 可訓可出單（截面族共用此 panel；no-promote）")
    elif st == asof_ready.STATUS_NEED_COLLECT:
        print("→ 價已到、缺 panel：先 build_feature_panel --panels D（skip-sync）")
    elif st == asof_ready.STATUS_FAKE_B3:
        print("→ 假 B3：禁止 train/predict 登記此 asof")
    else:
        print("→ 無 TAIEX 價")
    return int(snap["rc"])


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""回填 semantic_bound — 既有 deliberation_claim 一次性 B1 語意綁定重算(補完計畫 §2.1)。

🎯 這支在做什麼(白話):P0-B1 前的 claims 無 semantic_bound——本工具對每條既有 claim 呼叫
   anchors.semantic_bound_of(RULES_ALL 導出比對+binding_check 反抽取;**只比對、不執行**,零注入面)
   冪等 UPDATE。#12:導出邏輯住 anchors.py、本 script 只呼叫;重跑結果收斂一致。

守 #12(邏輯單一住所)· #6(冪等)· #29a。前置=migrate_deliberation_ddl.py --run(semantic_bound 欄)。

執行指令矩陣:
  python scripts/backfill_semantic_bound.py            # 無參數=dry-run(統計將 bound 幾條,不寫)
  python scripts/backfill_semantic_bound.py --run      # 冪等回填全部 claims
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.deliberation.anchors import semantic_bound_of


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT claim_id, claim_text, assigned_verifier, anchor, "
                    "(SELECT s.draft_path FROM deliberation_session s WHERE s.session_id=c.session_id) "
                    "FROM deliberation_claim c ORDER BY claim_id")
        rows = cur.fetchall()
        n_bound = 0
        for cid, txt, ver, anc, target in rows:
            b = semantic_bound_of(txt, ver, anc, target)
            n_bound += b
            if args.run:
                cur.execute("UPDATE deliberation_claim SET semantic_bound=%s WHERE claim_id=%s", (b, cid))
        if args.run:
            conn.commit()
        mode = "回填" if args.run else "dry-run"
        print(f"✓ {mode}:{len(rows)} claims → semantic_bound=true {n_bound} / false {len(rows) - n_bound}")
        # 驗收②:fast_path claims 應全 bound(RULES_ALL 重導出之設計保證)
        cur.execute("SELECT count(*), count(*) FILTER (WHERE semantic_bound) FROM deliberation_claim "
                    "WHERE provenance ? 'fast_path'")
        n_fp, n_fp_bound = cur.fetchone()
        if args.run:
            flag = "✓" if n_fp == n_fp_bound else "✗ 設計保證破功!"
            print(f"  驗收:fast_path {n_fp} 條中 bound={n_fp_bound} {flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

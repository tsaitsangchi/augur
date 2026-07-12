#!/usr/bin/env python
"""Wave 1 候選源策展+R4 親核包產生器(深抓計畫 S2;K 計畫 K3)。

🎯 這支在做什麼(白話):從 proposed 池篩指定域的候選源→逐源 probe(單次最小請求 #25,寫 review_log
   不落 staging)→產 R4 親核包:probe 結果表+copy-ready TTY approve 指令(approve 唯人,AI 永不代核)。

守 #25(最小探測)· 憲章 v1.41.0(approve=人閘)· #28(probe 之外零外部請求)。

執行指令矩陣:
  python scripts/curate_source_candidates.py                        # 列 proposed 池域分佈(唯讀)
  python scripts/curate_source_candidates.py --domain economics     # 該域候選+R4 包(不 probe)
  python scripts/curate_source_candidates.py --domain economics --probe --limit 10  # 逐源 probe 後產包
"""
import argparse
import subprocess
import sys

import _bootstrap  # noqa: F401
from augur.core import db

PY = sys.executable


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--domain")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.domain:
            cur.execute("SELECT domain, count(*) FROM knowledge_source WHERE approval_status='proposed' "
                        "GROUP BY 1 ORDER BY 2 DESC LIMIT 15")
            print("proposed 池(域×源數):")
            for d, n in cur.fetchall():
                print(f"  {d[:40]:42} {n}")
            print(__doc__.split("執行指令矩陣:")[1])
            return 0
        cur.execute("SELECT source_key, adapter, entity_type, COALESCE(license_regime,'(未策展)') "
                    "FROM knowledge_source WHERE approval_status='proposed' AND domain ILIKE %s "
                    "ORDER BY source_key LIMIT %s", (f"%{args.domain}%", args.limit))
        cands = cur.fetchall()
    if not cands:
        print(f"域 {args.domain} 無 proposed 候選")
        return 0
    print(f"== Wave 1 候選({args.domain},{len(cands)} 源)==")
    for sk, ad, et, lic in cands:
        line = f"  {sk[:36]:38} adapter={ad:16} entity={et:8} regime={lic}"
        if args.probe:
            r = subprocess.run([PY, "scripts/probe_knowledge_source.py", "--source", sk],
                               capture_output=True, text=True, timeout=120)
            line += f" probe={'✓' if r.returncode == 0 else '✗'}"
        print(line)
    print("\n== R4 親核包(TTY,approve 唯人;probe ✓ 者才建議升級)==")
    for sk, *_ in cands:
        print(f"python scripts/review_knowledge_source.py --approve {sk} --actor hugo")
    print("(核後 activate 同工具;未核者恆 proposed=三層閘擋於庫外)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

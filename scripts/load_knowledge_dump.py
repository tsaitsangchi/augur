#!/usr/bin/env python
"""知識 dump 批次載入(深抓計畫 S4;K 計畫 K3)——JSONL→staging(manual 導管,傳輸工件非 SSOT #29b)。

🎯 這支在做什麼(白話):讀 JSONL(每行一 payload)以指定 manual/dump 源灌 knowledge_staging(pending,
   走同一 promote 審核路);來源須 active(staging trigger 機械擋非 active);checkpoint 落
   knowledge_dump_checkpoint(resume-safe)。

守 #1(provenance=source+檔名+行號)· #6(checkpoint 續傳)· 憲章 v1.41.0(非 active 源=trigger 擋)。

執行指令矩陣:
  python scripts/load_knowledge_dump.py                                 # 現況:checkpoint(唯讀)
  python scripts/load_knowledge_dump.py --file X.jsonl --source manual_curation --entity-type work --domain economics --run
"""
import argparse
import json
import sys

import _bootstrap  # noqa: F401
from augur.core import db


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--file"); ap.add_argument("--source")
    ap.add_argument("--entity-type", dest="etype"); ap.add_argument("--domain", default="general")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    with db.connect() as conn, db.transaction(conn) as cur:
        if not (args.run and args.file and args.source and args.etype):
            cur.execute("SELECT * FROM knowledge_dump_checkpoint ORDER BY 1 DESC LIMIT 5")
            print("checkpoint 近 5 筆:", cur.fetchall() or "(空)")
            print(__doc__.split("執行指令矩陣:")[1])
            return 0
        cur.execute("SELECT COALESCE(max(items_loaded),0) FROM knowledge_dump_checkpoint WHERE dump_file=%s", (args.file,))
        start = cur.fetchone()[0]
        n = bad = 0
        with open(args.file, encoding="utf-8") as fh:
            for i, line in enumerate(fh, 1):
                if i <= start or not line.strip():
                    continue
                try:
                    p = json.loads(line)
                except Exception:
                    bad += 1
                    continue
                cur.execute("INSERT INTO knowledge_staging (source_key, entity_type, domain, payload, status, source_url) "
                            "VALUES (%s,%s,%s,%s,'pending',%s) ON CONFLICT DO NOTHING",
                            (args.source, args.etype, args.domain, json.dumps(p), f"dump:{args.file}#L{i}"))
                n += 1
                if n % 500 == 0:
                    cur.execute("INSERT INTO knowledge_dump_checkpoint (source_key, dump_file, byte_offset, items_loaded, finished) "
                                "VALUES (%s,%s,0,%s,false)", (args.source, args.file, i))
        cur.execute("INSERT INTO knowledge_dump_checkpoint (source_key, dump_file, byte_offset, items_loaded, finished) "
                    "VALUES (%s,%s,0,%s,true)", (args.source, args.file, i))
        print(f"✓ 載入 {n} 列(壞行 {bad};resume 自第 {start} 行;→ promote_knowledge.py 審核晉升)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""通用學派 citation seed 引擎 — 讀 JSON 資料檔補 proponents + philosophy_source(資料驅動、不 hardcode)。

🎯 這支在做什麼(白話):把「大師 → 學派 + 真實文獻 citation」資料檔(JSON)寫入——大師名補進
   philosophy_school.proponents(去重)、文獻書目補進 philosophy_source(source_type='book');冪等。
   合規路顯性化(憲章 v1.18.0):版權著作核心精神經真實文獻 citation → principle → 因子 → #14。
守 #1(citation=真實文獻書目事實、禁 ai_generated)· #15 · #6 冪等。

執行指令矩陣:
  python scripts/seed_citations.py                                          # 無參數:列可用資料檔+用法
  python scripts/seed_citations.py data/philosophy/master_citations.json   # 匯入指定資料檔
  python scripts/seed_citations.py my_new_citations.json                   # 未來擴充:自備 JSON 即用
JSON 格式(list of objects):
  [{"proponent":"Charlie Munger","school_zh":"品質/護城河",
    "citation":"Munger, Poor Charlie's Almanack, 2005"}, …]
"""
import sys
import json
from pathlib import Path

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "philosophy"


def usage():
    print(__doc__.split("執行指令矩陣:")[1].split("JSON 格式")[0])
    print("可用資料檔:")
    for f in sorted(DATA_DIR.glob("*citations*.json")):
        print(f"  {f.relative_to(DATA_DIR.parent.parent)}")


def main():
    if len(sys.argv) < 2:
        usage()
        return
    path = Path(sys.argv[1])
    rows = json.load(open(path))
    props_added = src_added = missing = 0
    with db.connect() as conn, db.transaction(conn) as cur:
        for r in rows:
            cur.execute("SELECT school_id, proponents FROM philosophy_school WHERE name_zh=%s", (r["school_zh"],))
            row = cur.fetchone()
            if not row:
                print(f"⚠ 無此學派: {r['school_zh']}")
                missing += 1
                continue
            sid, props = row
            if r["proponent"] not in (props or ""):
                cur.execute("UPDATE philosophy_school SET proponents=%s WHERE school_id=%s",
                            ((props + "; " + r["proponent"]) if props else r["proponent"], sid))
                props_added += 1
            cur.execute("SELECT 1 FROM philosophy_source WHERE school_id=%s AND citation=%s", (sid, r["citation"]))
            if not cur.fetchone():
                cur.execute("INSERT INTO philosophy_source (school_id, citation, source_type) VALUES (%s,%s,'book')",
                            (sid, r["citation"]))
                src_added += 1
        cur.execute("SELECT count(*) FROM philosophy_source")
        total = cur.fetchone()[0]
    print(f"{path.name}:proponents 補 {props_added}、citation 補 {src_added}(共 {total} 筆)、無對映學派 {missing}")


if __name__ == "__main__":
    main()

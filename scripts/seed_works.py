#!/usr/bin/env python
"""通用著作書目 seed 引擎 — 讀 JSON 資料檔 upsert philosophy_work(資料驅動、不 hardcode)。

🎯 這支在做什麼(白話):把「代表著作書目」資料檔(JSON)寫入 philosophy_work(書名/年份事實 metadata、
   非全文);thinker 以 name_zh 或 name 對映、同 thinker 同 title 跳過、冪等。新增書目=加資料列,不改程式。
守 #1(書目=事實 metadata、非 AI 摘要;現代版權著作全文法律不可抓、停在書目)· #15(年份不確定 null)· #6 冪等。
⚠️ 全文另由 fetch_confirmed_fulltext(triage 對抗驗證後)抓公版;版權著作停在書目=正確終點(憲章 v1.18.0)。

執行指令矩陣:
  python scripts/seed_works.py                                          # 無參數:列可用資料檔+用法
  python scripts/seed_works.py data/philosophy/works_bibliography.json  # 匯入指定資料檔
  python scripts/seed_works.py my_new_works.json                        # 未來擴充:自備 JSON 即用
JSON 格式(list of objects):
  [{"thinker":"彼得·杜拉克","title":"The Practice of Management","title_zh":"管理的實踐",
    "year":1954,"work_type":"book"}, …]  (thinker=name_zh 或 name;work_type: book/paper/…)
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
    for f in sorted(DATA_DIR.glob("works_*.json")):
        print(f"  {f.relative_to(DATA_DIR.parent.parent)}")


def main():
    if len(sys.argv) < 2:
        usage()
        return
    path = Path(sys.argv[1])
    works = json.load(open(path))
    added = skip = missing = 0
    miss = []
    with db.connect() as conn, db.transaction(conn) as cur:
        for w in works:
            cur.execute("SELECT thinker_id FROM philosophy_thinker WHERE name_zh=%s OR name=%s",
                        (w["thinker"], w["thinker"]))
            r = cur.fetchone()
            if not r:
                missing += 1
                miss.append(w["thinker"])
                continue
            tid = r[0]
            cur.execute("SELECT 1 FROM philosophy_work WHERE thinker_id=%s AND title=%s", (tid, w["title"]))
            if cur.fetchone():
                skip += 1
                continue
            cur.execute("INSERT INTO philosophy_work (thinker_id,title,title_zh,year,work_type,note) "
                        "VALUES (%s,%s,%s,%s,%s,'書目 metadata、代表著作、全文版權或另由 fetch_* 抓公版')",
                        (tid, w["title"], w.get("title_zh"), w.get("year"), w.get("work_type", "book")))
            added += 1
        cur.execute("SELECT count(*) FROM philosophy_work")
        nw = cur.fetchone()[0]
    print(f"{path.name}:新增 {added} 部、跳過 {skip}(已有)、無對映 thinker {missing}"
          + (f"({'、'.join(sorted(set(miss)))})" if miss else "") + f";philosophy_work 現共 {nw} 部")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""通用 thinker seed 引擎 — 讀 JSON 資料檔 upsert philosophy_thinker(資料驅動、不 hardcode)。

🎯 這支在做什麼(白話):把「思想家名冊」資料檔(JSON)寫入 philosophy_thinker;已有(name_zh 或 name
   相同)跳過、冪等可重跑。新增思想家=加資料列到 JSON(或另建新 JSON),不改本程式(#12 資料驅動)。
守 #1/#15(生卒/國籍/簡介=通行史實 metadata、可查證校正;不確定留 null 不編造)· #6 冪等 · #28 本地零 usage。
⚠️ 人物 metadata、不進預測管線;現代版權大師原則入因子須走真實文獻 principle→#14(憲章 v1.18.0)。

執行指令矩陣:
  python scripts/seed_thinkers.py                                        # 無參數:列可用資料檔+用法
  python scripts/seed_thinkers.py data/philosophy/thinkers_management.json   # 匯入指定資料檔
  python scripts/seed_thinkers.py my_new_thinkers.json                   # 未來擴充:自備 JSON 即用
JSON 格式(list of objects):
  [{"name_zh":"彼得·杜拉克","name":"Peter Drucker","birth_year":1909,"death_year":2005,
    "nationality":"奧地利／美國","bio":"現代管理學之父…"}, …]  (birth/death 不確定可 null)
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
    for f in sorted(DATA_DIR.glob("thinkers_*.json")):
        print(f"  {f.relative_to(DATA_DIR.parent.parent)}")


def main():
    if len(sys.argv) < 2:
        usage()
        return
    path = Path(sys.argv[1])
    people = json.load(open(path))
    added = skipped = 0
    with db.connect() as conn, db.transaction(conn) as cur:
        for p in people:
            cur.execute("SELECT thinker_id FROM philosophy_thinker WHERE name_zh=%s OR name=%s",
                        (p["name_zh"], p["name"]))
            if cur.fetchone():
                skipped += 1
                continue
            cur.execute("INSERT INTO philosophy_thinker (name,name_zh,birth_year,death_year,nationality,bio) "
                        "VALUES (%s,%s,%s,%s,%s,%s)",
                        (p["name"], p["name_zh"], p.get("birth_year"), p.get("death_year"),
                         p.get("nationality"), p.get("bio")))
            added += 1
        cur.execute("SELECT count(*) FROM philosophy_thinker")
        total = cur.fetchone()[0]
    print(f"{path.name}:新增 {added} 位、跳過 {skipped} 位(已有)、philosophy_thinker 現共 {total} 位")


if __name__ == "__main__":
    main()

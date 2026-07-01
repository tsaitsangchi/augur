#!/usr/bin/env python
"""依 philosophy_thinker 窮舉補 philosophy_work 書目 — DBpedia notableWork(實證代表著作)。

🎯 對無 work 的 thinker,以 DBpedia dbo:notableWork 抓其代表著作**書目**(書名/年份),補 philosophy_work。
   ⚠️ 補的是**書目 metadata**(事實、可溯源 DBpedia),非全文——現代版權著作全文法律不可抓(#1);
   有公版全文者另由 fetch_* 抓 work_text。書目讓「大師↔著作」關係完整、供合規路(原則→#14)溯源。
守 #1/#15(書目為實證事實 metadata、非 AI 摘要著作內容)· #28· #17/#18· 憲章 v1.18.0。

用法:PYTHONPATH=src python scripts/seed_thinker_works_dbpedia.py
"""
import re
import json
import time
import socket
import urllib.request
import urllib.parse

from augur.core import db

socket.setdefaulttimeout(60)
ENDPOINT = "https://dbpedia.org/sparql"
UA = {"User-Agent": "augur-research/1.0 (bibliography metadata)", "Accept": "application/sparql-results+json"}


def query_works(names):
    values = " ".join('"' + n.replace('"', '').replace('\\', '') + '"@en' for n in names)
    q = f"""SELECT DISTINCT ?name ?workLabel ?date WHERE {{
  ?p rdfs:label ?name ; dbo:notableWork ?w .
  ?w rdfs:label ?workLabel . FILTER(LANG(?workLabel)="en")
  OPTIONAL {{ ?w dbo:releaseDate ?date }}
  VALUES ?name {{ {values} }}
}}"""
    url = ENDPOINT + "?query=" + urllib.parse.quote(q)
    for _ in range(4):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read().decode())["results"]["bindings"]
        except Exception as e:
            print(f"  retry: {e}", flush=True)
            time.sleep(20)
    return []


def main():
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            cur.execute("SELECT thinker_id, name FROM philosophy_thinker th WHERE name IS NOT NULL "
                        "AND NOT EXISTS(SELECT 1 FROM philosophy_work w WHERE w.thinker_id=th.thinker_id)")
            thinkers = {}
            for tid, n in cur.fetchall():
                thinkers.setdefault(n, tid)
        names = list(thinkers)
        print(f"無 work 且有英文名之 thinker: {len(names)} 位;DBpedia notableWork 查詢中…", flush=True)
        added = 0
        for i in range(0, len(names), 80):
            batch = names[i:i + 80]
            rows = query_works(batch)
            time.sleep(3)
            with db.transaction(conn) as cur:
                for b in rows:
                    nm = b["name"]["value"]
                    wl = b["workLabel"]["value"]
                    tid = thinkers.get(nm)
                    if not tid:
                        continue
                    yr = None
                    if "date" in b:
                        m = re.match(r"(-?\d{3,4})", b["date"]["value"])
                        yr = int(m.group(1)) if m else None
                    cur.execute("SELECT 1 FROM philosophy_work WHERE thinker_id=%s AND title=%s", (tid, wl))
                    if cur.fetchone():
                        continue
                    cur.execute("INSERT INTO philosophy_work (thinker_id,title,year,work_type,note) "
                                "VALUES (%s,%s,%s,'book','書目 metadata、DBpedia notableWork、全文版權/未抓')", (tid, wl, yr))
                    added += 1
            print(f"  批次 {i//80+1}/{(len(names)+79)//80}: 累計 +{added} 書目", flush=True)
        with db.connect() as c2, db.transaction(c2) as cur:
            cur.execute("SELECT count(*) FROM philosophy_work"); nw = cur.fetchone()[0]
            cur.execute("SELECT count(DISTINCT thinker_id) FROM philosophy_work"); nt = cur.fetchone()[0]
    print(f"\n完成:DBpedia 補 {added} 筆著作書目;philosophy_work 共 {nw} 部 / 有著作 thinker {nt} 位")
    print("⚠️ 補的是書目 metadata(書名/年份、實證可溯源),非全文;現代版權著作全文法律不可抓。")


if __name__ == "__main__":
    main()

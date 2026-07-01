#!/usr/bin/env python
"""擴充 philosophy_thinker — 從 DBpedia 抓有中文維基之哲學家(Wikidata outage 之實證替代)。

🎯 Wikidata WDQS outage 時的替代:從 **DBpedia**(真實結構化來源)抓 dbo:Philosopher 且**有中文維基 label**
者(≈ major、且有中文名可入庫),含中英文名/生卒/中文簡介,upsert 入 philosophy_thinker。
守 #1/#15(實證真實來源、非 AI 編造;來源 DBpedia 可溯源)· #28(本地零 usage)· #17/#18。
⚠️ 人物 metadata、不進預測管線;生卒為 DBpedia 資料、古代 BC 年可能需校(DBpedia 存正數)。

用法:PYTHONPATH=src python scripts/seed_dbpedia_philosophers.py [--limit N]
"""
import re
import sys
import json
import time
import urllib.request
import urllib.parse

from augur.core import db

ENDPOINT = "https://dbpedia.org/sparql"
UA = {"User-Agent": "augur-research/1.0 (philosophy archival)", "Accept": "application/sparql-results+json"}


def query_dbpedia(limit):
    q = f"""SELECT DISTINCT ?p ?nameEn ?nameZh ?birth ?death ?abstract WHERE {{
  ?p a dbo:Philosopher ; rdfs:label ?nameEn, ?nameZh .
  FILTER(LANG(?nameEn)="en") FILTER(LANG(?nameZh)="zh")
  OPTIONAL {{ ?p dbo:birthYear ?birth }}
  OPTIONAL {{ ?p dbo:deathYear ?death }}
  OPTIONAL {{ ?p dbo:abstract ?abstract FILTER(LANG(?abstract)="zh") }}
}} LIMIT {limit}"""
    url = ENDPOINT + "?query=" + urllib.parse.quote(q)
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.loads(urllib.request.urlopen(req, timeout=150).read().decode())["results"]["bindings"]
        except Exception as e:
            print(f"  attempt {attempt+1}/5: {e},退避 30s…", flush=True)
            time.sleep(30)
    raise RuntimeError("DBpedia 多次重試仍失敗")


def yr(b, k):
    if k not in b:
        return None
    m = re.match(r"0*(\d+)", b[k]["value"])
    return int(m.group(1)) if m else None


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 3000
    print(f"DBpedia 查詢有中文維基之哲學家(LIMIT {limit})…")
    rows = query_dbpedia(limit)
    print(f"DBpedia 回 {len(rows)} 位")
    added = skipped = 0
    with db.connect() as conn, db.transaction(conn) as cur:
        for b in rows:
            name = b["nameEn"]["value"]
            name_zh = b["nameZh"]["value"]
            cur.execute("SELECT 1 FROM philosophy_thinker WHERE name=%s OR name_zh=%s", (name, name_zh))
            if cur.fetchone():
                skipped += 1
                continue
            bio = b.get("abstract", {}).get("value", "")[:300]
            cur.execute("INSERT INTO philosophy_thinker (name,name_zh,birth_year,death_year,nationality,bio) "
                        "VALUES (%s,%s,%s,%s,%s,%s)", (name, name_zh, yr(b, "birth"), yr(b, "death"), None, bio))
            added += 1
        cur.execute("SELECT count(*) FROM philosophy_thinker")
        total = cur.fetchone()[0]
    print(f"philosophy_thinker:DBpedia 新增 {added} 位、跳過 {skipped} 位(已有)、現共 {total} 位")
    print("⚠️ 來源 DBpedia(Wikidata outage 替代、實證可溯源 dbpedia.org);生卒為 DBpedia 資料、古代 BC 年可能需校。")


if __name__ == "__main__":
    main()

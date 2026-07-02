#!/usr/bin/env python
"""擴充 philosophy_thinker — 從 Wikidata 實證抓全球 major 哲學家(按知名度 sitelinks)。

🎯 不靠 AI 記憶窮舉(會漏/會編造),改從 **Wikidata**(真實結構化來源)按 sitelinks(知名度)
抓 occupation=philosopher 之 major 哲學家(中英文名/生卒/國籍/簡介),upsert 入 philosophy_thinker。
守 #1/#15(實證真實來源、非 AI 編造)· #25(429 限流退避重試)· #28(本地零 usage)· #17/#18。
⚠️ 人物 metadata、不進預測管線(廣博哲學量化零價值)。

執行指令矩陣:python scripts/seed_wikidata_philosophers.py [--min-sitelinks N]
"""
import re
import sys
import json
import time
import urllib.request
import urllib.parse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

SPARQL = "https://query.wikidata.org/sparql"
UA = {"User-Agent": "augur-research/1.0 (philosophy archival; contact tsaitsangchi@gmail.com)",
      "Accept": "application/sparql-results+json"}


def query_wikidata(min_sitelinks):
    q = f"""
SELECT ?p ?zhhant ?zh ?en ?birth ?death ?countryLabel ?descZh ?descEn ?sl WHERE {{
  ?p wdt:P106 wd:Q4964182 ; wikibase:sitelinks ?sl .
  FILTER(?sl >= {min_sitelinks})
  OPTIONAL {{ ?p wdt:P569 ?birth }}
  OPTIONAL {{ ?p wdt:P570 ?death }}
  OPTIONAL {{ ?p wdt:P27 ?country }}
  OPTIONAL {{ ?p rdfs:label ?zhhant FILTER(LANG(?zhhant)="zh-hant") }}
  OPTIONAL {{ ?p rdfs:label ?zh FILTER(LANG(?zh)="zh") }}
  OPTIONAL {{ ?p rdfs:label ?en FILTER(LANG(?en)="en") }}
  OPTIONAL {{ ?p schema:description ?descZh FILTER(LANG(?descZh)="zh") }}
  OPTIONAL {{ ?p schema:description ?descEn FILTER(LANG(?descEn)="en") }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "zh,en". }}
}}
ORDER BY DESC(?sl) LIMIT 800
"""
    url = SPARQL + "?format=json&query=" + urllib.parse.quote(q)
    # 長退避等 WDQS outage 恢復(背景本地 retry、零 usage、不輪詢——每 5 分鐘試、最多 ~3.3 小時)
    for attempt in range(40):
        try:
            req = urllib.request.Request(url, headers=UA)
            d = json.loads(urllib.request.urlopen(req, timeout=180).read().decode())
            return d["results"]["bindings"]
        except urllib.error.HTTPError as e:
            wait = 300 if e.code == 429 else 120
            print(f"  attempt {attempt+1}/40: HTTP {e.code},退避 {wait}s…", flush=True)
            time.sleep(wait)
        except Exception as e:
            print(f"  attempt {attempt+1}/40: {e},退避 120s…", flush=True)
            time.sleep(120)
    raise RuntimeError("Wikidata 多次重試仍失敗(WDQS outage 過久)")


def year(binding):
    v = binding.get("value", "")
    m = re.match(r"^(-?\d+)", v)
    return int(m.group(1)) if m else None


def main():
    min_sl = 40
    if "--min-sitelinks" in sys.argv:
        min_sl = int(sys.argv[sys.argv.index("--min-sitelinks") + 1])
    print(f"Wikidata 查詢 major 哲學家(sitelinks>={min_sl})…")
    rows = query_wikidata(min_sl)
    print(f"Wikidata 回 {len(rows)} 位")
    added = skipped = 0
    with db.connect() as conn, db.transaction(conn) as cur:
        for b in rows:
            name = b.get("en", {}).get("value") or b.get("p", {}).get("value", "").split("/")[-1]
            name_zh = (b.get("zhhant", {}).get("value") or b.get("zh", {}).get("value") or name)
            if not name:
                continue
            cur.execute("SELECT thinker_id FROM philosophy_thinker WHERE name=%s OR name_zh=%s", (name, name_zh))
            if cur.fetchone():
                skipped += 1
                continue
            birth = year(b["birth"]) if "birth" in b else None
            death = year(b["death"]) if "death" in b else None
            nat = b.get("countryLabel", {}).get("value")
            bio = (b.get("descZh", {}).get("value") or b.get("descEn", {}).get("value") or "")[:300]
            cur.execute("INSERT INTO philosophy_thinker (name,name_zh,birth_year,death_year,nationality,bio) "
                        "VALUES (%s,%s,%s,%s,%s,%s)", (name, name_zh, birth, death, nat, bio))
            added += 1
        cur.execute("SELECT count(*) FROM philosophy_thinker")
        total = cur.fetchone()[0]
    print(f"philosophy_thinker:Wikidata 新增 {added} 位、跳過 {skipped} 位(已有)、現共 {total} 位")
    print("⚠️ 資料源 Wikidata(實證、可溯源 wikidata.org);生卒/國籍/簡介為事實 metadata、不進預測管線。")


if __name__ == "__main__":
    main()

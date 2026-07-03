#!/usr/bin/env python
"""全球 know-how 目錄自我窮舉 — OpenAlex 分類樹/re3data 來源註冊表/獎項人物源 → 兩 registry 表。

🎯 這支在做什麼(白話):不由人/AI hardcode 列舉「全球知識」——直接抓權威機器可讀體系:
   P1 OpenAlex Topics(4 domains→26 fields→252 subfields→~4,500 topics)→ knowledge_taxonomy + 衍生 knowledge_query
   P2 re3data(~3,200 全球研究資料庫)→ knowledge_source 目錄列(enabled=false 待驗、誠實)
   P3 大獎項得主類別 → dbpedia 人物來源列
   P4 最小抽測(#25)+ 終態統計
計畫 SSOT:reports/augur_knowledge_registry_expansion_plan_20260702.md。
守 #1(權威 API 可溯源)· #17(步調限速)· #6(冪等可續、resume)· #28(本地零 usage)· #29 · 憲章 v1.19.0。

執行指令矩陣:
  python scripts/expand_knowledge_registry.py              # 全四階段(建議背景跑,~40-60 分)
  python scripts/expand_knowledge_registry.py --skip-re3data   # 跳過最耗時的 P2
"""
import sys
import time
import json
import socket
import subprocess
import urllib.request
import xml.etree.ElementTree as ET

import _bootstrap  # noqa: F401
from augur.core import db

socket.setdefaulttimeout(60)
UA = {"User-Agent": "augur-knowledge/1.0 (registry expansion)", "Accept": "application/json"}


def get(url, retry=1):
    for i in range(retry + 1):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read().decode()
        except Exception as e:
            if i == retry:
                print(f"  ✗ {url[:70]} → {e}", flush=True)
                return None
            time.sleep(5)


def p1_taxonomy(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS knowledge_taxonomy (
        tax_id serial PRIMARY KEY, openalex_id text UNIQUE, level varchar(16),
        parent_openalex_id text, name text, works_count bigint)""")
    cur.execute("ALTER TABLE knowledge_query ADD COLUMN IF NOT EXISTS origin varchar(32) DEFAULT 'manual'")
    total = 0
    for level, parent_key in [("domains", None), ("fields", "domain"), ("subfields", "field"), ("topics", "subfield")]:
        cursor = "*"
        while cursor:
            raw = get(f"https://api.openalex.org/{level}?per-page=200&cursor={cursor}")
            if not raw:
                break
            d = json.loads(raw)
            for r in d.get("results", []):
                parent = (r.get(parent_key) or {}).get("id") if parent_key else None
                cur.execute("INSERT INTO knowledge_taxonomy (openalex_id,level,parent_openalex_id,name,works_count) "
                            "VALUES (%s,%s,%s,%s,%s) ON CONFLICT (openalex_id) DO NOTHING",
                            (r["id"], level[:-1], parent, r["display_name"], r.get("works_count")))
                total += cur.rowcount
            cursor = d.get("meta", {}).get("next_cursor")
            time.sleep(0.3)
    # 衍生 knowledge_query:topic 名=查詢詞、domain=其 field 名 slug
    cur.execute("""INSERT INTO knowledge_query (domain, query, origin, note)
        SELECT lower(replace(replace(f.name,' ','_'),',','')), t.name, 'openalex_taxonomy', t.openalex_id
        FROM knowledge_taxonomy t
        JOIN knowledge_taxonomy s ON s.openalex_id = t.parent_openalex_id
        JOIN knowledge_taxonomy f ON f.openalex_id = s.parent_openalex_id
        WHERE t.level='topic' ON CONFLICT (domain, query) DO NOTHING""")
    print(f"P1 taxonomy +{total} 節點、query 衍生 +{cur.rowcount}", flush=True)


def p2_re3data(cur):
    raw = get("https://www.re3data.org/api/v1/repositories")
    if not raw:
        print("P2 re3data 清單不可達,跳過", flush=True)
        return
    ids = [(e.findtext("id"), e.findtext("name")) for e in ET.fromstring(raw).findall(".//repository")]
    print(f"P2 re3data 清單 {len(ids)} 個 repo,逐一取明細(resume:已有 skip)…", flush=True)
    cur.execute("SELECT source_key FROM knowledge_source WHERE source_key LIKE 're3data_%'")
    seen = {r[0] for r in cur.fetchall()}
    n = fail = 0
    for i, (rid, name) in enumerate(ids):
        key = f"re3data_{rid}"
        if key in seen:
            continue
        raw = get(f"https://www.re3data.org/api/v1/repository/{rid}", retry=0)
        subj = api = ""
        if raw:
            try:
                root = ET.fromstring(raw)
                ns = {"r": "http://www.re3data.org/schema/2-2"}
                subj = "; ".join(e.text or "" for e in root.findall(".//r:subject", ns)[:4])
                api = "; ".join((e.get("apiType") or "") + ":" + (e.text or "") for e in root.findall(".//r:api", ns)[:2])
            except ET.ParseError:
                fail += 1
        cur.execute("""INSERT INTO knowledge_source (source_key,adapter,domain,entity_type,enabled,note)
            VALUES (%s,'generic_json','general','work',false,%s) ON CONFLICT (source_key) DO NOTHING""",
            (key, f"re3data 目錄:{name} | 學科:{subj[:120]} | API:{api[:120]} | 未驗待啟用"))
        n += cur.rowcount
        if n % 200 == 0:
            print(f"  … {n} 列入(目前第 {i+1}/{len(ids)})", flush=True)
        time.sleep(0.5)
    print(f"P2 re3data +{n} 目錄列(明細解析失敗 {fail},誠實記)", flush=True)


AWARDS = ['Turing_Award_laureates', 'Fields_Medalists', 'Abel_Prize_laureates',
          'Nobel_laureates_in_Literature', 'Nobel_Peace_Prize_laureates',
          'Wolf_Prize_in_Physics_laureates', 'Wolf_Prize_in_Chemistry_laureates',
          'Copley_Medal_recipients', 'Pritzker_Architecture_Prize_winners',
          'Kyoto_Prize_winners', 'Lasker_Award_recipients', 'Millennium_Technology_Prize_winners']
SPARQL = ('SELECT DISTINCT ?name ?zh ?birth ?death WHERE { ?p dct:subject dbc:%s ; rdfs:label ?name . '
          'FILTER(LANG(?name)="en") OPTIONAL { ?p rdfs:label ?zh . FILTER(LANG(?zh)="zh") } '
          'OPTIONAL { ?p dbo:birthYear ?birth } OPTIONAL { ?p dbo:deathYear ?death } } LIMIT {limit}')


def p3_awards(cur):
    n = 0
    for a in AWARDS:
        slug = a.lower().replace('_laureates', '').replace('_recipients', '').replace('_winners', '').replace('_medalists', '_medal')
        cur.execute("""INSERT INTO knowledge_source (source_key,adapter,domain,entity_type,query_template,note)
            VALUES (%s,'dbpedia_sparql','general','thinker',%s,%s) ON CONFLICT (source_key) DO NOTHING""",
            (f"dbpedia_award_{slug}", SPARQL % a, f"獎項得主:{a}(批次註冊、抽測 1、餘用時驗)"))
        n += cur.rowcount
    print(f"P3 獎項人物源 +{n}", flush=True)


def p4_verify():
    for args in (['--source', 'dbpedia_award_turing_award', '--limit', '3'],):
        subprocess.run([PY := sys.executable, 'scripts/acquire_knowledge.py', *args], check=False)
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT level, count(*) FROM knowledge_taxonomy GROUP BY 1 ORDER BY 2")
        print("taxonomy:", dict(cur.fetchall()), flush=True)
        cur.execute("SELECT origin, count(*) FROM knowledge_query GROUP BY 1")
        print("query origin:", dict(cur.fetchall()), flush=True)
        cur.execute("SELECT enabled, count(*) FROM knowledge_source GROUP BY 1")
        print("source enabled:", dict(cur.fetchall()), flush=True)


def main():
    t0 = time.time()
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            p1_taxonomy(cur)
        if '--skip-re3data' not in sys.argv:
            with db.transaction(conn) as cur:
                p2_re3data(cur)
        with db.transaction(conn) as cur:
            p3_awards(cur)
    p4_verify()
    print(f"=== 完成 {(time.time()-t0)/60:.1f} 分 ===", flush=True)


if __name__ == '__main__':
    main()

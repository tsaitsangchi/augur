#!/usr/bin/env python
"""通用知識擷取引擎 — 依 knowledge_source(DB registry)從全球公開知識庫抓實體入 knowledge_staging。

🎯 這支在做什麼(白話):讀 DB `knowledge_source` 來源定義(adapter+查詢模板),從外部**真實免費 API**
   (OpenAlex / Crossref / arXiv / Semantic Scholar / OSTI / Wikidata / DBpedia / Open Library /
   Internet Archive / Unpaywall / Gutenberg / 手動策展檔)抓知識實體,帶 provenance 寫入
   `knowledge_staging`(pending 待審)。**新增領域=INSERT 一列 knowledge_source 或 --domain 覆寫,
   零 code 變動**;新「來源協定」才寫新 adapter。與 promote_knowledge.py 成對。
守 #1(真實來源、provenance 可溯源)· #3/#12(registry 資料驅動)· #17/#25(限速、最小單位測試)·
   #28(本地零 usage)· CLAUDE #29。
⚠️ 論文/著作**全文多有版權**:metadata+DOI/連結自由入庫;全文僅公版或 OA(CC)可另抓(triage 流程)。

執行指令矩陣:
  python scripts/acquire_knowledge.py                                    # 無參數:列 registry 來源+用法
  python scripts/acquire_knowledge.py --source openalex_works --query "perovskite solar cell" --limit 5
  python scripts/acquire_knowledge.py --source openalex_authors --query "Martin Green" --limit 3
  python scripts/acquire_knowledge.py --source crossref_works --query "portfolio selection" --limit 5
  python scripts/acquire_knowledge.py --source arxiv_search --query "battery electrolyte" --limit 5
  python scripts/acquire_knowledge.py --source semantic_scholar --query "prospect theory" --limit 5
  python scripts/acquire_knowledge.py --source osti_energy --query "perovskite" --limit 5
  python scripts/acquire_knowledge.py --source wikidata_people --query Q188094 --limit 20   # QID=職業(經濟學家)
  python scripts/acquire_knowledge.py --source openlibrary_books --query "intelligent investor" --limit 3
  python scripts/acquire_knowledge.py --source internet_archive --query 'creator:"Carnot"' --limit 3
  python scripts/acquire_knowledge.py --source unpaywall_doi --query 10.1086/294846          # DOI→OA 全文連結
  python scripts/acquire_knowledge.py --source manual_curation --file my.json --domain X --entity-type thinker
  python scripts/acquire_knowledge.py --source gutendex_search --query "Adam Smith"
  python scripts/acquire_knowledge.py --source openalex_works --query X --query-id 123  # harvest 蓋章 staging.query_id(lineage→query→taxonomy)
  # 任一來源皆可 --domain/--entity-type 覆寫 registry 預設(九領域重覆使用同一來源)
"""
import os
import sys
import json
import argparse
import socket
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

socket.setdefaulttimeout(60)
UA = {"User-Agent": "augur-knowledge/1.0 (research; contact via repo)", "Accept": "application/json"}
UA_SPARQL = {"User-Agent": "augur-knowledge/1.0", "Accept": "application/sparql-results+json"}


def fill(tpl, args):
    """模板安全代換(不使用 .format,容 SPARQL 大括號)。"""
    return (tpl.replace("{query}", urllib.parse.quote(str(args.query or "")))
               .replace("{query_raw}", str(args.query or ""))
               .replace("{limit}", str(args.limit or 20))
               .replace("{email}", os.environ.get("UNPAYWALL_EMAIL", ""))
               .replace("{extra_filter}", args.extra_filter or ""))


_PACE = [1.0]   # 每源步調(秒);main 依 knowledge_source.pace_seconds 設定(#24 對偶:限速住 DB)
_LAST = [0.0]


def get_json(url, headers=UA):
    import time as _t
    wait = _PACE[0] - (_t.monotonic() - _LAST[0])
    if wait > 0:
        _t.sleep(wait)
    _LAST[0] = _t.monotonic()
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=90).read().decode())


_QUERY_ID = None        # harvest 排程蓋章(--query-id);lineage:staging.query_id→knowledge_query→taxonomy
_HAS_QUERY_ID = False   # staging.query_id 欄存在與否(harvest_knowledge.py --migrate-only 後才有),main() 啟動偵測


def stage(cur, src_key, domain, etype, payload, url):
    cols = "source_key,domain,entity_type,payload,source_url"
    vals = [src_key, domain, etype, json.dumps(payload, ensure_ascii=False), url]
    if _HAS_QUERY_ID:   # 欄未建(尚未跑 harvest migrate)→ 退回原 5 欄寫入,不炸
        cols += ",query_id"
        vals.append(_QUERY_ID)
    cur.execute(f"INSERT INTO knowledge_staging ({cols}) VALUES ({','.join(['%s'] * len(vals))}) "
                "ON CONFLICT DO NOTHING", vals)
    return cur.rowcount


# ── adapters(每個 ~15 行;回傳入庫列數) ─────────────────────────────
def adapter_manual_file(cur, src, args, dom, et):
    if not args.file:
        sys.exit("manual_file 需 --file <json>")
    return sum(stage(cur, src[0], dom, et, p, f"manual:{args.file}") for p in json.load(open(args.file)))


def adapter_dbpedia_sparql(cur, src, args, dom, et):
    url = "https://dbpedia.org/sparql?query=" + urllib.parse.quote(fill(src[4], args).replace("{{", "{").replace("}}", "}"))
    d = get_json(url, UA_SPARQL)
    return sum(stage(cur, src[0], dom, et, {k: v["value"] for k, v in b.items()}, "https://dbpedia.org/sparql")
               for b in d["results"]["bindings"])


def adapter_wikidata_sparql(cur, src, args, dom, et):
    url = "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(fill(src[4], args))
    d = get_json(url, UA_SPARQL)
    return sum(stage(cur, src[0], dom, et, {k: v["value"] for k, v in b.items()}, "https://query.wikidata.org/sparql")
               for b in d["results"]["bindings"])


def adapter_gutendex(cur, src, args, dom, et):
    if not args.query:
        sys.exit("gutendex 需 --query")
    d = get_json(fill(src[4], args))
    n = 0
    for b in d.get("results", [])[: args.limit or 20]:
        n += stage(cur, src[0], dom, et,
                   {"gutenberg_id": b["id"], "title": b["title"], "authors": [a["name"] for a in b.get("authors", [])],
                    "languages": b.get("languages"), "copyright": b.get("copyright")},
                   f"https://www.gutenberg.org/ebooks/{b['id']}")
    return n


def adapter_openalex(cur, src, args, dom, et):
    d = get_json(fill(src[4], args))
    n = 0
    for r in d.get("results", []):
        if "/authors" in src[4]:
            p = {"name": r.get("display_name"), "orcid": r.get("orcid"),
                 "works_count": r.get("works_count"), "openalex_id": r.get("id"),
                 "affiliation": ((r.get("last_known_institutions") or [{}])[0]).get("display_name")}
        else:
            p = {"title": r.get("display_name") or r.get("title"), "year": r.get("publication_year"),
                 "doi": r.get("doi"), "authors": [a["author"]["display_name"] for a in r.get("authorships", [])][:8],
                 "venue": ((r.get("primary_location") or {}).get("source") or {}).get("display_name"),
                 "openalex_id": r.get("id"), "work_type": "paper"}
        n += stage(cur, src[0], dom, et, p, r.get("id") or "https://openalex.org")
    return n


def adapter_crossref(cur, src, args, dom, et):
    d = get_json(fill(src[4], args))
    n = 0
    for r in d.get("message", {}).get("items", []):
        year = (r.get("published-print") or r.get("published-online") or {}).get("date-parts", [[None]])[0][0]
        p = {"title": (r.get("title") or [""])[0], "year": year, "doi": r.get("DOI"),
             "authors": [f"{a.get('given','')} {a.get('family','')}".strip() for a in r.get("author", [])][:8],
             "venue": (r.get("container-title") or [""])[0], "work_type": "paper"}
        n += stage(cur, src[0], dom, et, p, f"https://doi.org/{r.get('DOI')}" if r.get("DOI") else "https://crossref.org")
    return n


def adapter_arxiv(cur, src, args, dom, et):
    xml = urllib.request.urlopen(urllib.request.Request(fill(src[4], args), headers=UA), timeout=90).read().decode()
    ns = {"a": "http://www.w3.org/2005/Atom"}
    n = 0
    for e in ET.fromstring(xml).findall("a:entry", ns):
        link = e.findtext("a:id", "", ns)
        p = {"title": " ".join(e.findtext("a:title", "", ns).split()),
             "year": int(e.findtext("a:published", "0000", ns)[:4]) or None,
             "authors": [a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)][:8],
             "arxiv_id": link.rsplit("/", 1)[-1], "work_type": "paper"}
        n += stage(cur, src[0], dom, et, p, link)
    return n


def adapter_semantic_scholar(cur, src, args, dom, et):
    key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "").strip()   # #29b:key 值住 .env、adapter 讀
    hdrs = {**UA, "x-api-key": key} if (key and not key.startswith("你的")) else UA  # 有 key→x-api-key header(拉高額度、解 429)
    d = get_json(fill(src[4], args), hdrs)
    n = 0
    for r in d.get("data", []):
        p = {"title": r.get("title"), "year": r.get("year"),
             "doi": (r.get("externalIds") or {}).get("DOI"),
             "authors": [a.get("name") for a in r.get("authors", [])][:8],
             "venue": r.get("venue"), "work_type": "paper"}
        n += stage(cur, src[0], dom, et, p, f"https://www.semanticscholar.org/paper/{r.get('paperId')}")
    return n


def adapter_osti(cur, src, args, dom, et):
    d = get_json(fill(src[4], args))
    rows = d if isinstance(d, list) else d.get("records") or d.get("data") or []
    n = 0
    for r in rows[: args.limit or 20]:
        p = {"title": r.get("title"), "year": (r.get("publication_date") or "")[:4] or None,
             "doi": r.get("doi"), "authors": (r.get("authors") or [])[:8],
             "osti_id": r.get("osti_id"), "work_type": "report"}
        n += stage(cur, src[0], dom, et, p, r.get("doi") and f"https://doi.org/{r['doi']}" or
                   f"https://www.osti.gov/biblio/{r.get('osti_id')}")
    return n


def adapter_openlibrary(cur, src, args, dom, et):
    d = get_json(fill(src[4], args))
    n = 0
    for r in d.get("docs", []):
        p = {"title": r.get("title"), "authors": (r.get("author_name") or [])[:4],
             "year": r.get("first_publish_year"), "openlibrary_key": r.get("key"), "work_type": "book"}
        n += stage(cur, src[0], dom, et, p, f"https://openlibrary.org{r.get('key','')}")
    return n


def adapter_internet_archive(cur, src, args, dom, et):
    d = get_json(fill(src[4], args))
    n = 0
    for r in d.get("response", {}).get("docs", []):
        p = {"title": r.get("title"), "authors": r.get("creator") if isinstance(r.get("creator"), list)
             else [r.get("creator")] if r.get("creator") else [],
             "year": r.get("year"), "ia_identifier": r.get("identifier"), "work_type": "book"}
        n += stage(cur, src[0], dom, et, p, f"https://archive.org/details/{r.get('identifier')}")
    return n


def adapter_unpaywall(cur, src, args, dom, et):
    if not os.environ.get("UNPAYWALL_EMAIL"):
        sys.exit("unpaywall 需環境變數 UNPAYWALL_EMAIL(任一聯絡信箱)")
    if not args.query:
        sys.exit("unpaywall 需 --query <DOI>")
    r = get_json(fill(src[4], args))
    oa = (r.get("best_oa_location") or {})
    p = {"title": r.get("title"), "year": r.get("year"), "doi": r.get("doi"),
         "is_oa": r.get("is_oa"), "oa_url": oa.get("url"), "license": oa.get("license"), "work_type": "paper"}
    return stage(cur, src[0], dom, et, p, oa.get("url") or f"https://doi.org/{r.get('doi')}")


def _walk(obj, path):
    """dot-path 取值(支援數字索引:'titles.0.title')。"""
    for part in str(path).split("."):
        if obj is None:
            return None
        if isinstance(obj, list):
            try:
                obj = obj[int(part)]
            except (ValueError, IndexError):
                return None
        elif isinstance(obj, dict):
            obj = obj.get(part)
        else:
            return None
    return obj


def adapter_generic_json(cur, src, args, dom, et):
    """通用 JSON API adapter:registry adapter_config 定義 results_path/fields 對映——新來源零 code。
    config 例:{"results_path":"resultList.result","fields":{"title":"title","year":"pubYear"},
               "url_path":"doi","work_type":"paper","list_key":"name"}"""
    cfg = src[5] or {}
    d = get_json(fill(src[4], args))
    rows = _walk(d, cfg["results_path"]) if cfg.get("results_path") else d
    if not isinstance(rows, list):
        rows = [rows] if rows else []
    n = 0
    for r in rows[: args.limit or 20]:
        p = {}
        for k, path in (cfg.get("fields") or {}).items():
            v = _walk(r, path)
            if isinstance(v, list):
                v = [x.get(cfg.get("list_key", "name")) if isinstance(x, dict) else x for x in v][:8]
            if v is not None:
                p[k] = v
        if not p:
            continue
        p.setdefault("work_type", cfg.get("work_type", "paper"))
        u = _walk(r, cfg["url_path"]) if cfg.get("url_path") else None
        n += stage(cur, src[0], dom, et, p, str(u) if u else f"api:{src[0]}")
    return n


def adapter_oai_pmh(cur, src, args, dom, et):
    """OAI-PMH ListRecords(oai_dc)→ staging(深抓計畫 §1 OAPEN/機構庫協定;K3 S3 新協定=新 adapter 合理)。"""
    xml = urllib.request.urlopen(urllib.request.Request(fill(src[4], args), headers=UA), timeout=90).read().decode()
    ns = {"o": "http://www.openarchives.org/OAI/2.0/", "dc": "http://purl.org/dc/elements/1.1/",
          "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/"}
    n = 0
    for rec in ET.fromstring(xml).iter("{http://www.openarchives.org/OAI/2.0/}record"):
        md = rec.find(".//oai_dc:dc", ns)
        if md is None:
            continue
        title = md.findtext("dc:title", "", ns).strip()
        if not title:
            continue
        ident = [x.text for x in md.findall("dc:identifier", ns) if x.text] or [""]
        year = next((int(d.text[:4]) for d in md.findall("dc:date", ns)
                     if d.text and d.text[:4].isdigit()), None)
        p = {"title": title, "year": year,
             "authors": [c.text for c in md.findall("dc:creator", ns) if c.text][:8],
             "openalex_id": None, "work_type": "book",
             "license_hint": ";".join(x.text for x in md.findall("dc:rights", ns) if x.text)[:200] or None}
        n += stage(cur, src[0], dom, et, p, ident[0])
    return n


ADAPTERS = {"manual_file": adapter_manual_file, "dbpedia_sparql": adapter_dbpedia_sparql,
            "oai_pmh": adapter_oai_pmh,
            "generic_json": adapter_generic_json,
            "wikidata_sparql": adapter_wikidata_sparql, "gutendex": adapter_gutendex,
            "openalex": adapter_openalex, "crossref": adapter_crossref, "arxiv": adapter_arxiv,
            "semantic_scholar": adapter_semantic_scholar, "osti": adapter_osti,
            "openlibrary": adapter_openlibrary, "internet_archive": adapter_internet_archive,
            "unpaywall": adapter_unpaywall}


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--source"); ap.add_argument("--file"); ap.add_argument("--query")
    ap.add_argument("--limit", type=int); ap.add_argument("--extra-filter", dest="extra_filter")
    ap.add_argument("--domain"); ap.add_argument("--entity-type", dest="entity_type")
    ap.add_argument("--query-id", dest="query_id", type=int)
    args, _ = ap.parse_known_args()
    global _QUERY_ID, _HAS_QUERY_ID
    _QUERY_ID = args.query_id
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.source:
            print(__doc__.split("執行指令矩陣:")[1])
            cur.execute("SELECT source_key, adapter, domain, entity_type, enabled FROM knowledge_source ORDER BY adapter, source_key")
            print("registry 現有來源:")
            for r in cur.fetchall():
                print(f"  {r[0]:28} adapter={r[1]:18} domain={r[2]:18} entity={r[3]:8} enabled={r[4]}")
            return
        cur.execute("SELECT 1 FROM information_schema.columns "
                    "WHERE table_name='knowledge_staging' AND column_name='query_id'")
        _HAS_QUERY_ID = cur.fetchone() is not None
        if args.query_id is not None and not _HAS_QUERY_ID:
            print("⚠ staging 無 query_id 欄(先跑 harvest_knowledge.py --migrate-only);本次不寫 query_id")
        cur.execute("SELECT source_key, adapter, domain, entity_type, query_template, adapter_config, "
                    "approval_status, COALESCE(pace_seconds, 1.0) FROM knowledge_source "
                    "WHERE source_key=%s AND enabled", (args.source,))
        src = cur.fetchone()
        if not src:
            sys.exit(f"registry 無此來源(或 disabled): {args.source}")
        if src[6] != 'active':                      # 閘二(fail-closed):非 active 源引擎拒抓(憲章 v1.41.0)
            sys.exit(f"來源 {args.source} approval_status={src[6]}≠active——approve 唯決策層人執行(review_knowledge_source.py)")
        _PACE[0] = float(src[7])                    # 每源步調住 DB(#24 對偶)
        if src[1] not in ADAPTERS:
            sys.exit(f"未知 adapter: {src[1]}(現有:{list(ADAPTERS)})")
        dom, et = args.domain or src[2], args.entity_type or src[3]
        n = ADAPTERS[src[1]](cur, src, args, dom, et)
        cur.execute("SELECT count(*) FROM knowledge_staging WHERE status='pending'")
        print(f"{args.source} → domain={dom} entity={et}:staging +{n} 列(去重後);pending 共 {cur.fetchone()[0]}")
        print("→ 審核後晉升:python scripts/promote_knowledge.py --entity-type " + et)


if __name__ == "__main__":
    main()

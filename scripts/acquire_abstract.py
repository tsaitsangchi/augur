#!/usr/bin/env python
"""件 B-0 paper abstract 補抓 — knowledge_item(paper、尚無內容)→ 多源回查 abstract → knowledge_item_text。

🎯 這支在做什麼(白話):對 harvest 只落了 metadata 的 paper(105,313 篇無 abstract/全文),依 source_key
   回查各源 API 取 abstract 純文字→knowledge_item_text(seq=0、source_type='abstract')。抽取全確定性
   (openalex inverted_index 依位置重建、JATS/HTML 剝標、Atom/JSON 純文字,零 AI 摘要 #1)。crossref/
   openalex 逐篇覆蓋不全→同 DOI 依序 fallback 接力(semantic_scholar→europepmc→openalex),命中即止、
   全空記 abstract_none 誠實終態(#15、下輪不重問=收斂)。abstract 只寫 seq=0,不封殺日後 OA 全文
   (fetch_oa_fulltext 的 PENDING 認非-abstract item_text)。

   **fail-closed by data(#26 碰護欄即停 by construction)**:只處理 knowledge_source.abstract_policy='allow'
   之源(每源人閘,憲章 v1.41.0);license 讀 adapter_config->>'abstract_license'(#29b 資料驅動,R-B0
   治權裁定「abstract=metadata」時由人 seed),缺則 abstract_no_license 記帳不入庫。故未拍板前此支抓 0 筆。

守 #1(逐字零 AI、來源可溯源)· 憲章全文准入三軌 + v1.41.0 每源 approve· #6(冪等、逐 item commit)·
   #25(--limit 首輪最小)· #24(pace 讀 DB、連 5 錯熔斷、honor Retry-After)· #28(本地零 usage)· #29(a/b/c/d)。

執行指令矩陣:
  python scripts/acquire_abstract.py                          # 無參數:印矩陣+待抓/待閘統計(不打 API)
  python scripts/acquire_abstract.py --limit 3               # 最小驗證(#25):只跑 3 筆
  python scripts/acquire_abstract.py --limit 3 --source arxiv_search   # 單源最小
  python scripts/acquire_abstract.py --domain finance_mgmt --run       # 圈域全跑(背景批)
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from fetch_oa_fulltext import strip_html, detect_language  # 同目錄;逐字剝標/語言判定共用單一實作(#1/#12)

UA = {"User-Agent": "augur-knowledge/1.0 (abstract backfill; mailto:UNPAYWALL_EMAIL)"}
BREAK_AFTER = 5        # 連續暫時錯熔斷(系統性故障不硬衝 #24)
MIN_ABSTRACT = 80      # 過短(< 80 字)視同無 abstract(殘頁/佔位),誠實 skip
DEFAULT_PACE = 1.0     # 無 source.pace_seconds 時的禮貌步調

_last_call = [0.0]


def _pace(sec):
    wait = _last_call[0] + sec - time.time()
    if wait > 0:
        time.sleep(wait)
    _last_call[0] = time.time()


def http_get(url, headers=None, timeout=60, max_bytes=4_000_000):
    req = urllib.request.Request(url, headers=headers or UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return (r.headers.get("Content-Type") or "").lower(), r.read(max_bytes)


def _doi(external_id, url):
    """external_id / url → 純 DOI('10.…');非 DOI 回 None(不猜測)。"""
    for v in (external_id or "", url or ""):
        v = v.strip()
        for p in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/",
                  "http://dx.doi.org/", "doi:"):
            if v.lower().startswith(p):
                v = v[len(p):]
                break
        if v.startswith("10."):
            return v
    return None


def _arxiv_id(external_id, url):
    """arxiv external_id / url → arXiv id(去版本尾非必要,API 容忍);非 arxiv 回 None。"""
    v = (external_id or "").strip()
    if v and "/abs/" not in v and "arxiv.org" not in v:
        return v.split("v")[0] if v[:1].isdigit() else v
    u = (url or "")
    if "arxiv.org/abs/" in u:
        return u.split("/abs/")[-1].split("v")[0]
    return None


def rebuild_inverted(inv):
    """openalex abstract_inverted_index → 原句(確定性:依位置擺字,#1 非 AI)。"""
    if not inv:
        return None
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[k] for k in sorted(pos)) if pos else None


# ── 各源 resolver:輸入 (item dict、doi、email);回 (abstract_text, source_url) 或 (None, None) ──
# item = {item_id, external_id, url}。resolver 只負責取回逐字 abstract;license 由呼叫端依源治理決定。

def res_arxiv(item, doi, email):
    aid = _arxiv_id(item["external_id"], item["url"])
    if not aid:
        return None, None
    src = f"http://export.arxiv.org/api/query?id_list={urllib.parse.quote(aid)}"
    _, body = http_get(src)
    x = body.decode("utf-8", "replace")
    a, b = x.find("<summary>"), x.find("</summary>")
    if a < 0 or b < 0:
        return None, None
    import html as _html
    return _html.unescape(x[a + 9:b]).strip(), f"http://arxiv.org/abs/{aid}"


def res_crossref(item, doi, email):
    if not doi:
        return None, None
    src = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='/')}"
    if email:
        src += f"?mailto={urllib.parse.quote(email)}"
    _, body = http_get(src)
    ab = json.loads(body.decode()).get("message", {}).get("abstract")
    return (strip_html(ab), f"https://doi.org/{doi}") if ab else (None, None)


def res_openalex(item, doi, email):
    key = item["url"] if "openalex.org" in (item["url"] or "") else (f"https://doi.org/{doi}" if doi else None)
    if not key:
        return None, None
    wid = key.rstrip("/").split("/")[-1] if "openalex.org" in key else f"doi:{doi}"
    src = f"https://api.openalex.org/works/{urllib.parse.quote(wid, safe=':')}"
    if email:
        src += f"?mailto={urllib.parse.quote(email)}"
    _, body = http_get(src)
    txt = rebuild_inverted(json.loads(body.decode()).get("abstract_inverted_index"))
    return (txt, key) if txt else (None, None)


def res_semantic(item, doi, email):
    if not doi:
        return None, None
    src = (f"https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi, safe='/')}"
           "?fields=abstract")
    _, body = http_get(src)
    ab = json.loads(body.decode()).get("abstract")
    return (ab.strip(), f"https://doi.org/{doi}") if ab else (None, None)


def res_europepmc(item, doi, email):
    if not doi:
        return None, None
    q = urllib.parse.quote(f'DOI:"{doi}"')
    src = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&resultType=core&format=json"
    _, body = http_get(src)
    res = json.loads(body.decode()).get("resultList", {}).get("result", [])
    ab = res[0].get("abstractText") if res else None
    return (strip_html(ab), f"https://doi.org/{doi}") if ab else (None, None)


def res_plos(item, doi, email):
    if not doi:
        return None, None
    q = urllib.parse.quote(f"id:{doi}")
    _, body = http_get(f"https://api.plos.org/search?q={q}&fl=abstract&wt=json")
    docs = json.loads(body.decode()).get("response", {}).get("docs", [])
    ab = docs[0].get("abstract") if docs else None
    if isinstance(ab, list):
        ab = " ".join(ab)
    return (strip_html(ab).strip(), f"https://doi.org/{doi}") if ab else (None, None)


def res_hal(item, doi, email):
    hid = None
    u = item["url"] or ""
    if "hal.science/" in u:
        hid = u.rstrip("/").split("/")[-1].split("v")[0]
    if not hid:
        return None, None
    q = urllib.parse.quote(f"halId_s:{hid}")
    _, body = http_get(f"https://api.archives-ouvertes.fr/search/?q={q}&fl=abstract_s&wt=json")
    docs = json.loads(body.decode()).get("response", {}).get("docs", [])
    ab = docs[0].get("abstract_s") if docs else None
    if isinstance(ab, list):
        ab = " ".join(a for a in ab if a and a != "absent")
    return (ab.strip(), u) if ab else (None, None)


def res_eric(item, doi, email):
    eid = (item["external_id"] or "").strip()
    if not eid.startswith(("EJ", "ED")):
        return None, None
    src = f"https://api.ies.ed.gov/eric/?search=id%3A{eid}&fields=description&format=json"
    _, body = http_get(src)
    docs = json.loads(body.decode()).get("response", {}).get("docs", [])
    ab = docs[0].get("description") if docs else None
    return (ab.strip(), f"https://eric.ed.gov/?id={eid}") if ab else (None, None)


def res_inspire(item, doi, email):
    rid = (item["external_id"] or "").strip()
    if not rid.isdigit():
        return None, None
    _, body = http_get(f"https://inspirehep.net/api/literature/{rid}")
    abs_ = json.loads(body.decode()).get("metadata", {}).get("abstracts", [])
    ab = abs_[0].get("value") if abs_ else None
    return (ab.strip(), f"https://inspirehep.net/literature/{rid}") if ab else (None, None)


def _desc_generic(item, doi, email, api_url, path):
    _, body = http_get(api_url)
    d = json.loads(body.decode())
    for k in path:
        d = (d or {}).get(k) if isinstance(d, dict) else None
    if isinstance(d, list):
        d = " ".join(x.get("description", "") if isinstance(x, dict) else str(x) for x in d)
    return (strip_html(str(d)).strip(), api_url) if d else (None, None)


def res_zenodo(item, doi, email):
    rid = (item["external_id"] or item["url"] or "").rsplit(".", 1)[-1]
    if not rid.isdigit():
        return None, None
    return _desc_generic(item, doi, email, f"https://zenodo.org/api/records/{rid}",
                         ["metadata", "description"])


def res_datacite(item, doi, email):
    if not doi:
        return None, None
    _, body = http_get(f"https://api.datacite.org/dois/{urllib.parse.quote(doi, safe='/')}")
    ds = json.loads(body.decode()).get("data", {}).get("attributes", {}).get("descriptions", [])
    ab = ds[0].get("description") if ds else None
    return (strip_html(ab).strip(), f"https://doi.org/{doi}") if ab else (None, None)


# 每源主 resolver(依 source_key);未列源走 DOI fallback 鏈
PRIMARY = {
    "arxiv_search": res_arxiv, "crossref_works": res_crossref, "openalex_works": res_openalex,
    "semantic_scholar": res_semantic, "europepmc": res_europepmc, "plos_search": res_plos,
    "hal_france": res_hal, "eric_education": res_eric, "inspire_hep": res_inspire,
    "zenodo_records": res_zenodo, "datacite_dois": res_datacite,
}
# DOI fallback 接力(crossref/openalex 覆蓋不全時;實證 S2 對 crossref DOI 覆蓋廣)
FALLBACK = [res_semantic, res_europepmc, res_openalex, res_crossref]

# 冪等 + fail-closed by data:僅 abstract_policy='allow' 源;已有非-abstract 全文或已判定過者不重問
PENDING_WHERE = """
  i.entity_type = 'paper'
  AND s.abstract_policy = 'allow'
  AND NOT EXISTS (SELECT 1 FROM knowledge_item_text t
                  WHERE t.item_id = i.item_id AND (t.source_type IS DISTINCT FROM 'abstract'))
  AND NOT EXISTS (SELECT 1 FROM knowledge_item_text t
                  WHERE t.item_id = i.item_id AND t.source_type = 'abstract')
  AND NOT EXISTS (SELECT 1 FROM knowledge_fulltext_status b
                  WHERE b.item_id = i.item_id AND b.status LIKE 'abstract_%%')
"""

BLOCKED_REASON = {
    "abstract_none": "多源回查皆無 abstract——覆蓋現實,非漏抓(下輪不重問=收斂)",
    "abstract_no_license": "源未設 adapter_config.abstract_license——待 R-B0 治權裁定 seed(fail-closed)",
    "abstract_short": "回查得 abstract 但過短(< %d 字,殘頁/佔位)——誠實停" % MIN_ABSTRACT,
    "abstract_fetch_error": "回查持久失敗(403/404/410)——存取被拒之終態,非漏抓",
}


def _tables_ok(cur):
    cur.execute("SELECT to_regclass('knowledge_item'), to_regclass('knowledge_item_text'), "
                "to_regclass('knowledge_fulltext_status'), "
                "(SELECT 1 FROM information_schema.columns "
                " WHERE table_name='knowledge_source' AND column_name='abstract_policy')")
    item, itext, status, pol = cur.fetchone()
    miss = []
    if not item:
        miss.append("knowledge_item")
    if not itext:
        miss.append("knowledge_item_text")
    if not status:
        miss.append("knowledge_fulltext_status(先跑 migrate_fulltext_status_ddl.py;abstract_* 終態標籤須先擴 CHECK)")
    if not pol:
        miss.append("knowledge_source.abstract_policy(先跑 migrate_source_governance.py)")
    return miss


def print_pending_stats(cur):
    """待閘統計:多少 paper 已在 allow 源(可抓)、多少卡在 policy≠allow(待 R-B0)。"""
    cur.execute("SELECT count(*) FROM knowledge_item i JOIN knowledge_source s ON s.source_key=i.source_key "
                f"WHERE {PENDING_WHERE}")
    allow = cur.fetchone()[0]
    cur.execute("""SELECT count(*) FROM knowledge_item i JOIN knowledge_source s ON s.source_key=i.source_key
                   WHERE i.entity_type='paper' AND (s.abstract_policy IS NULL OR s.abstract_policy<>'allow')
                   AND NOT EXISTS (SELECT 1 FROM knowledge_item_text t WHERE t.item_id=i.item_id)""")
    gated = cur.fetchone()[0]
    print(f"待抓(abstract_policy='allow' 源、尚無內容):{allow} 篇")
    print(f"待閘(policy≠allow、尚無內容,須 R-B0 治權裁定後 seed abstract_policy):{gated} 篇")


def fetch_abstract(item, doi, email):
    """取 abstract:先本源主 resolver,無則 DOI fallback 接力;回 (text, source_url) 或 (None, None)。"""
    tried = set()
    prim = PRIMARY.get(item["source_key"])
    chain = ([prim] if prim else []) + [f for f in FALLBACK if f is not prim]
    for fn in chain:
        if fn in tried:
            continue
        tried.add(fn)
        text, src = fn(item, doi, email)
        if text and len(text) >= MIN_ABSTRACT:
            return text, src
        if text:                       # 取到但過短:記短、不再試(視為明確覆蓋現實)
            return "__SHORT__", src
    return None, None


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--domain")
    ap.add_argument("--source")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--run", action="store_true")
    args, _ = ap.parse_known_args()
    email = os.environ.get("UNPAYWALL_EMAIL", "")
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            miss = _tables_ok(cur)
            run = args.run or args.limit is not None
            if not run:                                   # 無 --run/--limit:安全預設,不打 API
                print(__doc__.split("執行指令矩陣:")[1])
                if miss:
                    print("先決未備:\n  " + "\n  ".join(miss))
                else:
                    print_pending_stats(cur)
                return
            if miss:
                sys.exit("先決未備:\n  " + "\n  ".join(miss))
            sql = ("SELECT i.item_id, i.external_id, i.url, i.source_key, "
                   "s.pace_seconds, s.adapter_config->>'abstract_license' "
                   "FROM knowledge_item i JOIN knowledge_source s ON s.source_key=i.source_key "
                   f"WHERE {PENDING_WHERE}")
            params = []
            if args.domain:
                sql += " AND i.domain=%s"
                params.append(args.domain)
            if args.source:
                sql += " AND i.source_key=%s"
                params.append(args.source)
            sql += " ORDER BY i.item_id"
            if args.limit:
                sql += " LIMIT %s"
                params.append(args.limit)
            cur.execute(sql, params)
            todo = cur.fetchall()
    stats = {"ok": 0, "abstract_none": 0, "abstract_no_license": 0,
             "abstract_short": 0, "abstract_fetch_error": 0, "error": 0}
    streak = 0
    with db.connect() as conn:
        for n, (item_id, eid, url, skey, pace, lic) in enumerate(todo, 1):
            item = {"item_id": item_id, "external_id": eid, "url": url, "source_key": skey}
            doi = _doi(eid, url)
            try:
                _pace(float(pace or DEFAULT_PACE))
                text, src = fetch_abstract(item, doi, email)
                if text is None:
                    status = "abstract_none"
                elif text == "__SHORT__":
                    status = "abstract_short"
                elif not lic:                             # fail-closed:源未設 abstract_license(R-B0 未 seed)
                    status = "abstract_no_license"
                else:
                    lang = detect_language(text)
                    with db.transaction(conn) as cur:
                        cur.execute(
                            "INSERT INTO knowledge_item_text (item_id, seq, content, language, source_url, "
                            "license, source_type, access_scope) "
                            "VALUES (%s,0,%s,%s,%s,%s,'abstract','public') "
                            "ON CONFLICT (item_id, seq) DO NOTHING",
                            (item_id, text, lang, src, lic))
                    stats["ok"] += 1
                    streak = 0
                    if n % 25 == 0:
                        print(f"  … {n}/{len(todo)}(abstract {stats['ok']} 落地)", flush=True)
                    continue
                with db.transaction(conn) as cur:         # blocked 終態誠實落帳(#15、下輪不重問)
                    cur.execute(
                        "INSERT INTO knowledge_fulltext_status (item_id, status, reason, source_url) "
                        "VALUES (%s,%s,%s,%s) ON CONFLICT (item_id) DO UPDATE SET "
                        "status=EXCLUDED.status, reason=EXCLUDED.reason, checked_at=now()",
                        (item_id, status, BLOCKED_REASON.get(status, status), None))
                stats[status] += 1
                streak = 0
            except Exception as e:
                if getattr(e, "code", None) in (401, 403, 404, 410):   # 持久 access-denied=終態,落帳收斂
                    with db.transaction(conn) as cur:
                        cur.execute("INSERT INTO knowledge_fulltext_status (item_id, status, reason) "
                                    "VALUES (%s,'abstract_fetch_error',%s) ON CONFLICT (item_id) DO UPDATE "
                                    "SET status=EXCLUDED.status, reason=EXCLUDED.reason, checked_at=now()",
                                    (item_id, BLOCKED_REASON["abstract_fetch_error"]))
                    stats["abstract_fetch_error"] += 1
                    streak = 0
                else:
                    stats["error"] += 1
                    streak += 1
                print(f"  ✗ item {item_id} doi={doi}:{type(e).__name__}: {e}", flush=True)
                if streak >= BREAK_AFTER:
                    print(f"連續 {BREAK_AFTER} 錯 → 熔斷停止(剩 {len(todo)-n} 筆;冪等可續)", flush=True)
                    break
    print(f"✓ 掃 {len(todo)} 篇 → abstract 落地 {stats['ok']};"
          f"none {stats['abstract_none']} / no_license {stats['abstract_no_license']} / "
          f"short {stats['abstract_short']} / fetch_error {stats['abstract_fetch_error']} / error {stats['error']}")
    if stats["abstract_no_license"]:
        print("  ⚠ no_license:源未設 adapter_config.abstract_license → 待 R-B0 治權裁定 seed(fail-closed 正常)")


if __name__ == "__main__":
    main()

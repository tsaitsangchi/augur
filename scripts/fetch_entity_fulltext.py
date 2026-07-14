#!/usr/bin/env python
"""件 B-1~B-4 存量多域 entity 全文/描述窮舉補抓 — book/report/compound/material → knowledge_item_text。

🎯 這支在做什麼(白話):對只落 metadata 的多域 entity(book 5,915 / report 322 / compound 237 /
   material 212,全數 0 全文),依 source_key 回查各源 API 取逐字全文或描述→knowledge_item_text。
   每源專屬 resolver(#29b registry 分派):book→Internet Archive _djvu.txt(逐件公版判定,借閱版誠實
   skip)、openlibrary→ocaid→IA;report→OSTI DOE PAGES OA fulltext;compound→ChEMBL 描述+機轉 /
   pubchem description;material→COD CIF 描述欄 / UniProt function / GBIF description。抽取全確定性
   (剝標/欄位取值,零 AI #1)。

   **fail-closed by data(#26 by construction)**:僅 approval_status='active' 源;license 逐筆判——
   IA 依 metadata 版權狀態(公版才抓)、其餘源讀 adapter_config->>'fulltext_license'(#29b 資料驅動、
   R-B 治權裁定時人 seed),缺則 skip_no_license 記帳不入庫。現況除 IA(public_domain regime)外各源皆
   license_regime='metadata_only'、無 fulltext_license → 抓 0 筆,直到 hugo 逐源裁定放行。

守 #1(逐字零 AI、可溯源)· 憲章全文准入三軌 + v1.41.0 每源 approve· #6(冪等、逐 item commit)·
   #25(--limit/--source 首輪最小)· #24(pace 讀 DB、連 5 錯熔斷)· #28(本地零 usage)· #29(a/b/c/d)。

執行指令矩陣:
  python scripts/fetch_entity_fulltext.py                              # 無參數:印矩陣+各型待抓/待閘統計
  python scripts/fetch_entity_fulltext.py --run --limit 3              # 首輪最小(#25)
  python scripts/fetch_entity_fulltext.py --run --limit 3 --source internet_archive
  python scripts/fetch_entity_fulltext.py --run --entity compound --limit 50
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from fetch_oa_fulltext import strip_html, detect_language  # 逐字剝標/語言判定共用單一實作(#1/#12)

UA = {"User-Agent": "augur-knowledge/1.0 (multi-domain fulltext archival)", "Accept": "*/*"}
BREAK_AFTER = 5
MIN_CHARS = 40          # 描述類短(UniProt function 76 字),放寬;book djvu 全文遠大於此
DEFAULT_PACE = 1.0
ENTITIES = ("book", "report", "compound", "material")


def http_get(url, timeout=90, max_bytes=12_000_000):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return (r.headers.get("Content-Type") or "").lower(), r.read(max_bytes)


def _lic(acfg):
    """source 之 fulltext_license(#29b 住 adapter_config;R-B seed);未設回 None=fail-closed。"""
    return (acfg or {}).get("fulltext_license")


# ── 各源 resolver:輸入 (item, acfg);回 (text, license, source_url, source_type) 或 (None, blocked_reason) ──

def _ia_by_id(ia_id):
    """Internet Archive id → 逐件公版判定 + _djvu.txt 逐字。回 (text, 'public_domain', url) 或 (None, reason)。"""
    _, body = http_get(f"https://archive.org/metadata/{urllib.parse.quote(ia_id)}")
    meta = json.loads(body.decode())
    md = meta.get("metadata", {})
    cr = (md.get("possible-copyright-status") or "").lower()
    lu = (md.get("licenseurl") or "").lower()
    # IA 公版正向訊號(實證 2026-07-14:此語料最常見寫法=「unaware of any copyright restrictions」;
    # 多數 item copyright 欄為 None→保守判非公版 skip_license,寧缺勿錯抓在版權內容)
    pd_cr = ("no copyright", "no known copyright", "not in copyright", "not_in_copyright",
             "public domain", "unaware of any copyright")
    pd_lu = ("publicdomain", "/mark/", "cc0", "/zero/")
    is_pd = any(m in cr for m in pd_cr) or any(m in lu for m in pd_lu)
    if not is_pd:                                      # 借閱版/在版權/版權未明 → 誠實停 metadata(非漏抓)
        return None, "skip_license"
    txt = [f["name"] for f in meta.get("files", []) if f.get("name", "").endswith("_djvu.txt")]
    if not txt:
        return None, "skip_no_fulltext"
    _, body = http_get(f"https://archive.org/download/{urllib.parse.quote(ia_id)}/{urllib.parse.quote(txt[0])}")
    return body.decode("utf-8", "replace"), "public_domain", \
        f"https://archive.org/details/{ia_id}"


def res_ia(item, acfg):
    t = _ia_by_id(item["external_id"])
    if t[0] is None:
        return None, t[1]
    return t[0], t[1], t[2], "ia_fulltext"


def res_openlibrary(item, acfg):
    wid = (item["external_id"] or "").strip("/").split("/")[-1]  # OL…W
    if not wid:
        return None, "skip_no_fulltext"
    _, body = http_get(f"https://openlibrary.org/works/{wid}/editions.json?limit=30")
    ocaid = next((e.get("ocaid") for e in json.loads(body.decode()).get("entries", []) if e.get("ocaid")), None)
    if not ocaid:
        return None, "skip_no_fulltext"               # 無 IA 掃描本 → 止 metadata
    t = _ia_by_id(ocaid)
    if t[0] is None:
        return None, t[1]
    return t[0], t[1], t[2], "ia_fulltext"


def res_osti(item, acfg):
    lic = _lic(acfg)
    if not lic:
        return None, "skip_no_license"
    doi = (item["external_id"] or "").strip()
    _, body = http_get(f"https://www.osti.gov/api/v1/records?doi={urllib.parse.quote(doi, safe='/')}")
    recs = json.loads(body.decode())
    if not recs:
        return None, "skip_no_fulltext"
    links = [l.get("href") or l.get("value") for l in (recs[0].get("links") or [])
             if l.get("rel") == "fulltext"]
    if not links:
        return None, "skip_no_fulltext"
    ctype, body = http_get(links[0])
    if "pdf" in ctype:
        return None, "skip_pdf"                       # PDF 抽取屬深抓 P3、本支誠實不做
    if not ("text/html" in ctype or "text/plain" in ctype):
        return None, "skip_ctype"
    text = strip_html(body.decode("utf-8", "replace")) if "html" in ctype else body.decode("utf-8", "replace")
    return text, lic, links[0], "osti_fulltext"


def res_chembl(item, acfg):
    lic = _lic(acfg)
    if not lic:
        return None, "skip_no_license"
    cid = (item["external_id"] or "").strip()
    _, body = http_get(f"https://www.ebi.ac.uk/chembl/api/data/molecule/{cid}.json")
    d = json.loads(body.decode())
    parts = []
    if d.get("pref_name"):
        parts.append(str(d["pref_name"]))
    syn = [s.get("molecule_synonyms") or s.get("synonyms") for s in (d.get("molecule_synonyms") or [])]
    syn = [s for s in syn if s][:12]
    if syn:
        parts.append("Synonyms: " + ", ".join(syn))
    _, mb = http_get(f"https://www.ebi.ac.uk/chembl/api/data/mechanism.json?molecule_chembl_id={cid}")
    for m in json.loads(mb.decode()).get("mechanisms", []):
        if m.get("mechanism_of_action"):
            parts.append("Mechanism of action: " + m["mechanism_of_action"])
    text = ". ".join(parts)
    return (text, lic, f"https://www.ebi.ac.uk/chembl/compound_report_card/{cid}/", "chembl_desc") \
        if text else (None, "skip_no_fulltext")


def res_pubchem(item, acfg):
    lic = _lic(acfg)
    if not lic:
        return None, "skip_no_license"
    cid = (item["external_id"] or "").strip()
    _, body = http_get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/description/JSON")
    info = json.loads(body.decode()).get("InformationList", {}).get("Information", [])
    desc = next((i.get("Description") for i in info if i.get("Description")), None)
    return (desc.strip(), lic, f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}", "pubchem_desc") \
        if desc else (None, "skip_no_fulltext")


def res_cod(item, acfg):
    lic = _lic(acfg)
    if not lic:
        return None, "skip_no_license"
    cid = (item["external_id"] or item["url"] or "").strip()   # COD id 住 url 欄(external_id 空)
    _, body = http_get(f"http://www.crystallography.net/cod/{cid}.cif")
    cif = body.decode("utf-8", "replace")
    fields = []
    for tag in ("_chemical_name_systematic", "_chemical_name_common", "_chemical_formula_sum",
                "_journal_name_full", "_publ_section_title"):
        for line in cif.splitlines():
            if line.strip().startswith(tag):
                v = line.split(None, 1)[1].strip().strip("'\"") if len(line.split(None, 1)) > 1 else ""
                if v:
                    fields.append(f"{tag[1:]}: {v}")
                break
    text = ". ".join(fields)
    return (text, lic, f"http://www.crystallography.net/cod/{cid}.html", "cod_desc") \
        if text else (None, "skip_no_fulltext")


def res_uniprot(item, acfg):
    lic = _lic(acfg)
    if not lic:
        return None, "skip_no_license"
    acc = (item["external_id"] or "").strip()
    _, body = http_get(f"https://rest.uniprot.org/uniprotkb/{acc}.json")
    d = json.loads(body.decode())
    texts = []
    for c in d.get("comments", []):
        if c.get("commentType") == "FUNCTION":
            texts += [t.get("value") for t in c.get("texts", []) if t.get("value")]
    text = " ".join(texts)
    return (text, lic, f"https://www.uniprot.org/uniprotkb/{acc}/entry", "uniprot_desc") \
        if text else (None, "skip_no_fulltext")


def res_gbif(item, acfg):
    lic = _lic(acfg)
    if not lic:
        return None, "skip_no_license"
    key = (item["external_id"] or "").strip()
    _, body = http_get(f"https://api.gbif.org/v1/species/{key}/descriptions")
    res = json.loads(body.decode()).get("results", [])
    text = " ".join(strip_html(r.get("description", "")) for r in res if r.get("description"))
    return (text, lic, f"https://www.gbif.org/species/{key}", "gbif_desc") \
        if text else (None, "skip_no_fulltext")


RESOLVERS = {
    "internet_archive": res_ia, "openlibrary_books": res_openlibrary, "osti_energy": res_osti,
    "chembl_molecules": res_chembl, "pubchem_compounds": res_pubchem,
    "cod_crystals": res_cod, "uniprot_proteins": res_uniprot, "gbif_species": res_gbif,
}

BLOCKED_REASON = {
    "skip_license": "在版權/借閱版(IA metadata 非公版)——憲章三軌停 metadata,非漏抓",
    "skip_no_license": "源未設 adapter_config.fulltext_license——待 R-B 治權裁定 seed(fail-closed)",
    "skip_no_fulltext": "源無可抓全文/描述(無 ocaid/無 fulltext link/欄位空)——覆蓋現實",
    "skip_pdf": "全文僅 PDF——本支誠實不解析(深抓 P3 另做)",
    "skip_ctype": "全文非 text/html/plain——無法逐字剝標,誠實停",
    "skip_short": "抽取後過短(< %d 字)——殘頁/佔位,誠實停" % MIN_CHARS,
    "skip_fetch_error": "回查持久失敗(403/404/410)——存取被拒之終態,非漏抓",
    "skip_no_resolver": "無此 source_key 之 resolver——未支援源,誠實停",
}

PENDING_WHERE = """
  i.entity_type = ANY(%(ents)s)
  AND s.approval_status = 'active'
  AND (COALESCE(i.external_id,'') <> '' OR COALESCE(i.url,'') <> '')   -- COD id 住 url
  AND NOT EXISTS (SELECT 1 FROM knowledge_item_text t WHERE t.item_id = i.item_id)
  AND NOT EXISTS (SELECT 1 FROM knowledge_fulltext_status b WHERE b.item_id = i.item_id)
"""


def _tables_ok(cur):
    cur.execute("SELECT to_regclass('knowledge_item'), to_regclass('knowledge_item_text'), "
                "to_regclass('knowledge_fulltext_status')")
    item, itext, status = cur.fetchone()
    miss = []
    if not item:
        miss.append("knowledge_item")
    if not itext:
        miss.append("knowledge_item_text")
    if not status:
        miss.append("knowledge_fulltext_status(先跑 migrate_fulltext_status_ddl.py)")
    return miss


def print_pending_stats(cur, ents):
    cur.execute("SELECT i.entity_type, i.source_key, count(*) "
                "FROM knowledge_item i JOIN knowledge_source s ON s.source_key=i.source_key "
                f"WHERE {PENDING_WHERE} GROUP BY 1,2 ORDER BY 1,3 DESC", {"ents": list(ents)})
    rows = cur.fetchall()
    print("待抓統計(active 源、尚無全文;license 逐筆判在 --run 時):" + ("(無)" if not rows else ""))
    for et, sk, n in rows:
        has = "✓resolver" if sk in RESOLVERS else "✗無resolver"
        print(f"  {et:10} {sk:20} {n:6}  {has}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--entity", choices=ENTITIES)
    ap.add_argument("--source")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--dry-run", action="store_true", dest="dry_run",
                    help="抓+抽取+印,零 DB 寫入(#26 dry-run 屬執行層、驗 resolver 端到端)")
    args, _ = ap.parse_known_args()
    ents = [args.entity] if args.entity else list(ENTITIES)
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            miss = _tables_ok(cur)
            run = args.run or args.limit is not None or args.dry_run
            if not run:
                print(__doc__.split("執行指令矩陣:")[1])
                if miss:
                    print("先決未備:\n  " + "\n  ".join(miss))
                else:
                    print_pending_stats(cur, ents)
                return
            if miss:
                sys.exit("先決未備:\n  " + "\n  ".join(miss))
            sql = ("SELECT i.item_id, i.external_id, i.url, i.source_key, s.pace_seconds, s.adapter_config "
                   "FROM knowledge_item i JOIN knowledge_source s ON s.source_key=i.source_key "
                   f"WHERE {PENDING_WHERE}")
            params = {"ents": ents}
            if args.source:
                sql += " AND i.source_key = %(src)s"
                params["src"] = args.source
            sql += " ORDER BY i.item_id"
            if args.limit:
                sql += " LIMIT %(lim)s"
                params["lim"] = args.limit
            cur.execute(sql, params)
            todo = cur.fetchall()
    stats = {"ok": 0, "rows": 0, "error": 0}
    for k in BLOCKED_REASON:
        stats[k] = 0
    streak = 0
    with db.connect() as conn:
        for n, (item_id, eid, url, skey, pace, acfg) in enumerate(todo, 1):
            item = {"item_id": item_id, "external_id": eid, "url": url, "source_key": skey}
            fn = RESOLVERS.get(skey)
            try:
                time.sleep(float(pace or DEFAULT_PACE))
                if not fn:
                    res = (None, "skip_no_resolver")
                else:
                    res = fn(item, acfg or {})
                if args.dry_run:                          # 抓+抽取+印,零 DB 寫入(驗 resolver 端到端)
                    if res[0] is None:
                        print(f"  [dry] item {item_id} {skey}: BLOCKED {res[1]}", flush=True)
                    else:
                        text, lic, src, stype = res
                        print(f"  [dry] item {item_id} {skey}: OK license={lic} type={stype} "
                              f"len={len(text)} :: {text[:160]!r}", flush=True)
                    continue
                if res[0] is None:                        # blocked 終態誠實落帳(#15、下輪不重問)
                    status = res[1]
                    with db.transaction(conn) as cur:
                        cur.execute("INSERT INTO knowledge_fulltext_status (item_id, status, reason) "
                                    "VALUES (%s,%s,%s) ON CONFLICT (item_id) DO UPDATE SET "
                                    "status=EXCLUDED.status, reason=EXCLUDED.reason, checked_at=now()",
                                    (item_id, status, BLOCKED_REASON.get(status, status)))
                    stats[status] = stats.get(status, 0) + 1
                    streak = 0
                    continue
                text, lic, src, stype = res
                if len(text) < MIN_CHARS:
                    with db.transaction(conn) as cur:
                        cur.execute("INSERT INTO knowledge_fulltext_status (item_id, status, reason) "
                                    "VALUES (%s,'skip_short',%s) ON CONFLICT (item_id) DO UPDATE SET "
                                    "status=EXCLUDED.status, reason=EXCLUDED.reason, checked_at=now()",
                                    (item_id, BLOCKED_REASON["skip_short"]))
                    stats["skip_short"] += 1
                    streak = 0
                    continue
                lang = detect_language(text)
                with db.transaction(conn) as cur:         # 逐 item commit:中斷可續(#6);分段配 UNIQUE(item_id,seq)
                    for i0 in range(0, len(text), 8000):
                        cur.execute(
                            "INSERT INTO knowledge_item_text (item_id, seq, content, language, source_url, "
                            "license, source_type, access_scope) VALUES (%s,%s,%s,%s,%s,%s,%s,'public') "
                            "ON CONFLICT (item_id, seq) DO NOTHING",
                            (item_id, i0 // 8000 + 1, text[i0:i0 + 8000], lang, src, lic, stype))
                    stats["rows"] += len(range(0, len(text), 8000))
                stats["ok"] += 1
                streak = 0
                if n % 25 == 0:
                    print(f"  … {n}/{len(todo)}(全文 {stats['ok']} 落地)", flush=True)
            except Exception as e:
                if getattr(e, "code", None) in (401, 403, 404, 410):
                    with db.transaction(conn) as cur:
                        cur.execute("INSERT INTO knowledge_fulltext_status (item_id, status, reason) "
                                    "VALUES (%s,'skip_fetch_error',%s) ON CONFLICT (item_id) DO UPDATE SET "
                                    "status=EXCLUDED.status, reason=EXCLUDED.reason, checked_at=now()",
                                    (item_id, BLOCKED_REASON["skip_fetch_error"]))
                    stats["skip_fetch_error"] += 1
                    streak = 0
                else:
                    stats["error"] += 1
                    streak += 1
                print(f"  ✗ item {item_id} ({skey}):{type(e).__name__}: {e}", flush=True)
                if streak >= BREAK_AFTER:
                    print(f"連續 {BREAK_AFTER} 錯 → 熔斷停止(剩 {len(todo)-n} 筆;冪等可續)", flush=True)
                    break
    blocked = sum(stats[k] for k in BLOCKED_REASON)
    print(f"✓ 掃 {len(todo)} 件 → 全文/描述落地 {stats['ok']} 件 / item_text +{stats['rows']} 段;"
          f"阻擋 {blocked}(已落終態帳、下輪不重問);error {stats['error']}")
    print("  " + " / ".join(f"{k.replace('skip_','')} {stats[k]}" for k in BLOCKED_REASON if stats[k]))
    if stats["skip_no_license"]:
        print("  ⚠ no_license:源未設 adapter_config.fulltext_license → 待 R-B 治權裁定 seed(fail-closed 正常)")


if __name__ == "__main__":
    main()

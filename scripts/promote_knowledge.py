#!/usr/bin/env python
"""知識晉升引擎 — knowledge_staging(pending)審核晉升到正式表(philosophy_thinker/work/source)。

🎯 這支在做什麼(白話):讀 `knowledge_staging` 待審列(篩 entity_type/domain/source),寫入對映正式表
   (thinker→philosophy_thinker、work→philosophy_work、citation→philosophy_source+proponents、
   七類條目 paper/report/dataset/compound/material/protein/species→knowledge_item;work 無 thinker
   歸屬且非哲學域者後援轉 knowledge_item=論文/書目 metadata),冪等去重(已有跳過)、成功標 promoted。
   與 acquire_knowledge.py 成對(外部來源→staging→正式表)。
   新 entity_type(如 knowhow)→ 加一個 mapping 函式(本質是 schema 知識=code);來源與資料皆 DB 驅動。
守 #1(來源可溯源、staging 帶 provenance、item lineage→staging→query→taxonomy)· #6 冪等 ·
   #15(晉升數字實證回報)· CLAUDE #29。

執行指令矩陣:
  python scripts/promote_knowledge.py                                  # 無參數:列 pending 統計+用法
  python scripts/promote_knowledge.py --entity-type thinker            # 晉升全部 pending thinker
  python scripts/promote_knowledge.py --entity-type work --domain management
  python scripts/promote_knowledge.py --entity-type paper              # 七類條目→knowledge_item
  python scripts/promote_knowledge.py --entity-type compound --source chembl_molecules
  python scripts/promote_knowledge.py --entity-type thinker --source dbpedia_award_turing_award  # harvest 治理:thinker 僅單跑型來源
  python scripts/promote_knowledge.py --entity-type thinker --dry-run  # 只看會晉升什麼、不寫
"""
import re
import sys
import json
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db


def _year(v):
    """容 '1714' / '1714-01-01' / '-0428' / int / None(壞值→None 不編造)。"""
    if v in (None, ""):
        return None
    m = re.match(r"^(-?\d{1,4})", str(v).strip())
    return int(m.group(1)) if m else None


def promote_thinker(cur, p, source_key=None):
    name, name_zh = p.get("name"), p.get("name_zh") or p.get("zh")
    if not (name or name_zh):
        return "rejected"
    cur.execute("SELECT 1 FROM philosophy_thinker WHERE name_zh=%s OR name=%s", (name_zh or name, name or name_zh))
    if cur.fetchone():
        return "dup"
    birth = _year(p.get("birth_year") or p.get("birth"))
    death = _year(p.get("death_year") or p.get("death"))
    if birth and death and death < birth:                 # 資料錯(如 BC 存正)→ 清 NULL 不入錯值
        birth = death = None
    cur.execute("INSERT INTO philosophy_thinker (name,name_zh,birth_year,death_year,nationality,bio,source) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (name, name_zh, birth, death, p.get("nationality"), p.get("bio"), source_key))
    return "ok"


def promote_work(cur, p, source_key=None):
    thinker, title = p.get("thinker") or (p.get("authors") or [None])[0], p.get("title")
    if not (thinker and title):
        return "rejected"
    names = [thinker]
    if "," in thinker:                       # gutendex "Smith, Adam" → "Adam Smith"
        last, _, first = thinker.partition(",")
        names.append(f"{first.strip()} {last.strip()}")
    r = None
    for nm in names:
        cur.execute("SELECT thinker_id FROM philosophy_thinker WHERE name_zh=%s OR name=%s", (nm, nm))
        r = cur.fetchone()
        if r:
            break
    if not r:
        return "no_thinker"
    cur.execute("SELECT 1 FROM philosophy_work WHERE thinker_id=%s AND title=%s", (r[0], title))
    if cur.fetchone():
        return "dup"
    cur.execute("INSERT INTO philosophy_work (thinker_id,title,title_zh,year,work_type,note) "
                "VALUES (%s,%s,%s,%s,%s,'經 knowledge_staging 晉升(provenance 見 staging)')",
                (r[0], title, p.get("title_zh"), p.get("year"), p.get("work_type", "book")))
    return "ok"


def promote_citation(cur, p, source_key=None):
    school, cite = p.get("school_zh"), p.get("citation")
    if not (school and cite):
        return "rejected"
    cur.execute("SELECT school_id, proponents FROM philosophy_school WHERE name_zh=%s", (school,))
    r = cur.fetchone()
    if not r:
        return "no_school"
    sid, props = r
    prop = p.get("proponent")
    if prop and prop not in (props or ""):
        cur.execute("UPDATE philosophy_school SET proponents=%s WHERE school_id=%s",
                    ((props + "; " + prop) if props else prop, sid))
    cur.execute("SELECT 1 FROM philosophy_source WHERE school_id=%s AND citation=%s", (sid, cite))
    if cur.fetchone():
        return "dup"
    cur.execute("INSERT INTO philosophy_source (school_id, citation, source_type) VALUES (%s,%s,'book')", (sid, cite))
    return "ok"


def promote_school(cur, p, source_key=None):
    """學派入庫(name_zh 去重)+ 隨附真實文獻 citation;非投資域不接 factor_map(素養層)。"""
    name_zh = p.get("name_zh")
    if not (name_zh and p.get("core_thesis")):
        return "rejected"
    cur.execute("SELECT school_id FROM philosophy_school WHERE name_zh=%s", (name_zh,))
    r = cur.fetchone()
    if r:
        sid, res = r[0], "dup"
    else:
        cur.execute("INSERT INTO philosophy_school (name,name_zh,core_thesis,proponents,domain) "
                    "VALUES (%s,%s,%s,%s,%s) RETURNING school_id",
                    (p.get("name"), name_zh, p["core_thesis"], p.get("proponents"),
                     p.get("domain", "investment")))
        sid, res = cur.fetchone()[0], "ok"
    cite = p.get("citation")
    if cite:
        cur.execute("SELECT 1 FROM philosophy_source WHERE school_id=%s AND citation=%s", (sid, cite))
        if not cur.fetchone():
            cur.execute("INSERT INTO philosophy_source (school_id,citation,source_type) VALUES (%s,%s,%s)",
                        (sid, cite, p.get("source_type", "book")))
    return res


ITEM_TYPES = ("paper", "report", "dataset", "compound", "material", "protein", "species")
# external_id 優先序(harvest 計畫 §二5 明文;無任一 → title+year 去重鍵)
EXTID_PRIORITY = ("doi", "arxiv_id", "chembl_id", "cid", "uniprot_id", "gbif_id",
                  "osti_id", "openalex_id", "ia_identifier", "openlibrary_key")


def promote_item(cur, p, source_key=None, ctx=None):
    """七類知識條目(論文/報告/資料集/化合物/材料/蛋白/物種)→ knowledge_item;
    亦承接 work 後援路(無 thinker 歸屬之非哲學 work,條目類取 payload work_type)。
    taxonomy_id 由 staging.query_id→knowledge_query.taxonomy_id 回填(lineage 全鏈)。"""
    ctx = ctx or {}
    title = p.get("title") or p.get("name")
    if not title:
        return "rejected"
    title = str(title)
    etype = ctx.get("entity_type")
    if etype not in ITEM_TYPES:               # work 後援路:以 payload work_type 定條目類(paper/report/book…)
        etype = p.get("work_type") or "paper"
    ext = next((str(p[k]) for k in EXTID_PRIORITY if p.get(k)), None)
    year = _year(p.get("year"))
    if ext:
        cur.execute("SELECT 1 FROM knowledge_item WHERE entity_type=%s AND external_id=%s", (etype, ext))
    else:                                     # 僅無 external_id 者用 title+year 去重(對齊 partial uq_item_title)
        cur.execute("SELECT 1 FROM knowledge_item WHERE external_id IS NULL AND entity_type=%s "
                    "AND md5(title)=md5(%s) AND COALESCE(year,0)=COALESCE(%s,0)", (etype, title, year))
    if cur.fetchone():
        return "dup"
    tax = None
    if ctx.get("query_id"):
        cur.execute("SELECT taxonomy_id FROM knowledge_query WHERE query_id=%s", (ctx["query_id"],))
        r = cur.fetchone()
        tax = r[0] if r else None
    authors = p.get("authors")
    if isinstance(authors, list):
        authors = "; ".join(str(a) for a in authors if a) or None
    cur.execute("INSERT INTO knowledge_item (domain,entity_type,title,title_zh,year,authors,external_id,"
                "venue,url,taxonomy_id,source_key,staging_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (ctx.get("domain") or "general", etype, title, p.get("title_zh"), year, authors, ext,
                 p.get("venue"), ctx.get("source_url") or p.get("url") or p.get("oa_url"), tax,
                 source_key, ctx.get("staging_id")))
    return "ok"


MAPPERS = {"thinker": promote_thinker, "work": promote_work, "citation": promote_citation,
           "school": promote_school, **{et: promote_item for et in ITEM_TYPES}}


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--entity-type", dest="etype"); ap.add_argument("--domain")
    ap.add_argument("--source"); ap.add_argument("--dry-run", action="store_true")
    args, _ = ap.parse_known_args()
    with db.connect() as conn, db.transaction(conn) as cur:
        if not args.etype:
            print(__doc__.split("執行指令矩陣:")[1])
            cur.execute("SELECT entity_type, domain, count(*) FROM knowledge_staging WHERE status='pending' GROUP BY 1,2")
            rows = cur.fetchall()
            print("pending 待審:" + ("(無)" if not rows else ""))
            for r in rows:
                print(f"  {r[0]:10} {r[1]:16} {r[2]} 列")
            return
        if args.etype not in MAPPERS:
            sys.exit(f"未知 entity_type: {args.etype}(現有:{list(MAPPERS)};新類型=加 mapping 函式)")
        cur.execute("SELECT to_regclass('knowledge_item')")
        has_item = cur.fetchone()[0] is not None
        if args.etype in ITEM_TYPES and not has_item:
            sys.exit("knowledge_item 未建——先跑 python scripts/harvest_knowledge.py --migrate-only")
        cur.execute("SELECT 1 FROM information_schema.columns "
                    "WHERE table_name='knowledge_staging' AND column_name='query_id'")
        qid_col = "query_id" if cur.fetchone() else "NULL::int"   # 欄未建(未跑 harvest migrate)→ 容 NULL
        q = (f"SELECT staging_id, payload, source_key, entity_type, domain, source_url, {qid_col} "
             "FROM knowledge_staging WHERE status='pending' AND entity_type=%s")
        params = [args.etype]
        if args.domain:
            q += " AND domain=%s"; params.append(args.domain)
        if args.source:
            q += " AND source_key=%s"; params.append(args.source)
        cur.execute(q, params)
        rows = cur.fetchall()
        stats = {}
        for sid, payload, skey, s_et, s_dom, s_url, s_qid in rows:
            p = payload if isinstance(payload, dict) else json.loads(payload)
            if args.dry_run:
                print(f"  [dry] #{sid} {str(p)[:90]}")
                continue
            ctx = {"staging_id": sid, "entity_type": s_et, "domain": s_dom, "source_url": s_url, "query_id": s_qid}
            fn = MAPPERS[args.etype]
            res = fn(cur, p, source_key=skey, ctx=ctx) if fn is promote_item else fn(cur, p, source_key=skey)
            if res == "no_thinker" and args.etype == "work" and s_dom != "philosophy" and has_item:
                # work→item 後援(harvest 計畫 §一⑤):無 thinker 歸屬之非哲學 work=論文/書目 metadata
                # → knowledge_item;哲學域仍留 pending 人審(守審核後晉升)
                res = {"ok": "item_ok", "dup": "item_dup"}.get(
                    promote_item(cur, p, source_key=skey, ctx=ctx), "no_thinker")
            stats[res] = stats.get(res, 0) + 1
            if res in ("ok", "dup", "item_ok", "item_dup"):
                cur.execute("UPDATE knowledge_staging SET status='promoted', promoted_at=now() WHERE staging_id=%s", (sid,))
            elif res == "rejected":
                cur.execute("UPDATE knowledge_staging SET status='rejected' WHERE staging_id=%s", (sid,))
        print(f"{args.etype}:掃 {len(rows)} 列 pending → {stats or '(dry-run 未寫)'}")


if __name__ == "__main__":
    main()

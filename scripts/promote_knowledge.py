#!/usr/bin/env python
"""知識晉升引擎 — knowledge_staging(pending)審核晉升到正式表(philosophy_thinker/work/source)。

🎯 這支在做什麼(白話):讀 `knowledge_staging` 待審列(篩 entity_type/domain/source),寫入對映正式表
   (thinker→philosophy_thinker、work→philosophy_work、citation→philosophy_source+proponents),
   冪等去重(已有跳過)、成功標 promoted。與 acquire_knowledge.py 成對(外部來源→staging→正式表)。
   新 entity_type(如 knowhow)→ 加一個 mapping 函式(本質是 schema 知識=code);來源與資料皆 DB 驅動。
守 #1(來源可溯源、staging 帶 provenance)· #6 冪等 · #15(晉升數字實證回報)· CLAUDE #29。

執行指令矩陣:
  python scripts/promote_knowledge.py                                  # 無參數:列 pending 統計+用法
  python scripts/promote_knowledge.py --entity-type thinker            # 晉升全部 pending thinker
  python scripts/promote_knowledge.py --entity-type work --domain management
  python scripts/promote_knowledge.py --entity-type thinker --dry-run  # 只看會晉升什麼、不寫
"""
import sys
import json
import argparse

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db


def promote_thinker(cur, p, source_key=None):
    name, name_zh = p.get("name"), p.get("name_zh")
    if not (name or name_zh):
        return "rejected"
    cur.execute("SELECT 1 FROM philosophy_thinker WHERE name_zh=%s OR name=%s", (name_zh or name, name or name_zh))
    if cur.fetchone():
        return "dup"
    birth = p.get("birth_year") or p.get("birth")
    death = p.get("death_year") or p.get("death")
    cur.execute("INSERT INTO philosophy_thinker (name,name_zh,birth_year,death_year,nationality,bio,source) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (name, name_zh, int(birth) if birth else None, int(death) if death else None,
                 p.get("nationality"), p.get("bio"), source_key))
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


MAPPERS = {"thinker": promote_thinker, "work": promote_work, "citation": promote_citation}


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
        q = "SELECT staging_id, payload, source_key FROM knowledge_staging WHERE status='pending' AND entity_type=%s"
        params = [args.etype]
        if args.domain:
            q += " AND domain=%s"; params.append(args.domain)
        if args.source:
            q += " AND source_key=%s"; params.append(args.source)
        cur.execute(q, params)
        rows = cur.fetchall()
        stats = {}
        for sid, payload, skey in rows:
            p = payload if isinstance(payload, dict) else json.loads(payload)
            if args.dry_run:
                print(f"  [dry] #{sid} {str(p)[:90]}")
                continue
            res = MAPPERS[args.etype](cur, p, source_key=skey)
            stats[res] = stats.get(res, 0) + 1
            if res in ("ok", "dup"):
                cur.execute("UPDATE knowledge_staging SET status='promoted', promoted_at=now() WHERE staging_id=%s", (sid,))
            elif res == "rejected":
                cur.execute("UPDATE knowledge_staging SET status='rejected' WHERE staging_id=%s", (sid,))
        print(f"{args.etype}:掃 {len(rows)} 列 pending → {stats or '(dry-run 未寫)'}")


if __name__ == "__main__":
    main()

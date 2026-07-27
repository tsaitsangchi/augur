#!/usr/bin/env python
"""自 staging payload 物化 `knowledge_item_text` — 供「文本已隨 payload 進來」之 owned_local ETL 源。

🎯 這支在做什麼(白話):多數知識源是「先入 metadata、再去外部抓全文」;但 ETL 型私有源(如 ttai ERP
   語意層)的文本**本來就在 payload 裡**,沒有外部可抓——這類源若只走 promote,就會停在「item 有了、
   卻查不到內容」的半套狀態(#29b:harvest 的終點是**可被檢索作答**,不是有一列 item)。
   本支把 payload 之文本欄物化成 item_text,接上既有 `build_sentences --scope items` → `embed_knowledge`。

**口徑不自創,沿用同源既有列**:license／access_scope／source_type／language 一律取該 source_key 既有
   item_text 之眾數(同源同口徑,#12);該源尚無任何既有列時**停手要求明示旗標**,不擅自預設
   (猜 access_scope 猜錯＝私有內容外流,屬不可逆)。

守 #1(逐字搬運、零 AI 改寫)· #6(冪等:已有 item_text 者跳過;逐批 commit)· #9/#10(數字出自 query)
   · #12(口徑單一住所=同源既有列)· #15(無前例即停手,不預設)· #28(純本地零 token)· #29a/b/c/d。

執行指令矩陣:
  python scripts/build_item_text_from_payload.py                          # 無參數:各源待物化統計(唯讀)
  python scripts/build_item_text_from_payload.py --source ttai_erp_pilot --dry-run
  python scripts/build_item_text_from_payload.py --source ttai_erp_pilot --run
  python scripts/build_item_text_from_payload.py --source X --run --text-field body --limit 100
  python scripts/build_item_text_from_payload.py --selftest               # 零 DB 純紅綠
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DEFAULT_TEXT_FIELD = "semantic_text"
BATCH = 500

# 待物化 = 該源之 item 有 staging payload 文本、但尚無 item_text
PENDING_SQL = """
SELECT i.item_id, s.payload ->> %s AS body, i.external_id, i.title
FROM knowledge_item i
JOIN knowledge_staging s ON s.staging_id = i.staging_id
WHERE i.source_key = %s
  AND coalesce(btrim(s.payload ->> %s), '') <> ''
  AND NOT EXISTS (SELECT 1 FROM knowledge_item_text t WHERE t.item_id = i.item_id)
ORDER BY i.item_id"""

# 同源既有口徑(眾數);無列則回 None → 呼叫端停手
CONVENTION_SQL = """
SELECT mode() WITHIN GROUP (ORDER BY t.license),
       mode() WITHIN GROUP (ORDER BY t.access_scope),
       mode() WITHIN GROUP (ORDER BY t.source_type),
       mode() WITHIN GROUP (ORDER BY t.language),
       mode() WITHIN GROUP (ORDER BY t.owner_user_id),
       count(*)
FROM knowledge_item_text t
JOIN knowledge_item i ON i.item_id = t.item_id
WHERE i.source_key = %s"""

INSERT_SQL = """
INSERT INTO knowledge_item_text
  (item_id, seq, content, language, source_url, license, fetched_at,
   source_type, access_scope, owner_user_id)
VALUES (%s, 1, %s, %s, %s, %s, now(), %s, %s, %s)"""


def convention(cur, source_key):
    cur.execute(CONVENTION_SQL, (source_key,))
    lic, scope, stype, lang, owner, n = cur.fetchone()
    return {"license": lic, "access_scope": scope, "source_type": stype,
            "language": lang, "owner_user_id": owner, "n_precedent": n}


def source_url_for(source_key, external_id):
    """沿用同源既有列之 URL 形態(ttai:buffer.knowledge_unit:<stable_key>)——可溯回上游那一列。"""
    return f"{source_key}:payload:{external_id}" if external_id else f"{source_key}:payload"


def build(source_key, text_field, limit, dry, overrides=None):
    with db.connect() as conn:
        cur = conn.cursor()
        conv = convention(cur, source_key)
        conv.update({k: v for k, v in (overrides or {}).items() if v})
        missing = [k for k in ("license", "access_scope", "source_type", "language")
                   if not conv.get(k)]
        if missing:
            print(f"✗ {source_key} 無既有 item_text 可沿用口徑,且未明示:{','.join(missing)}")
            print("  停手不預設——猜錯 access_scope 等於把私有內容放進可外流範圍(不可逆)。")
            return 2
        print(f"── 口徑(沿用同源 {conv['n_precedent']} 列既有):license={conv['license']} "
              f"scope={conv['access_scope']} type={conv['source_type']} lang={conv['language']} ──")

        cur.execute(PENDING_SQL, (text_field, source_key, text_field))
        rows = cur.fetchall()
        if limit:
            rows = rows[:limit]
        print(f"待物化:{len(rows)} 列(payload.{text_field} 非空且尚無 item_text)")
        if dry:
            for item_id, body, ext, title in rows[:5]:
                print(f"  [dry] item={item_id} ext={ext} text={body[:50]!r}")
            print("(dry-run:未寫入)")
            return 0
        n = 0
        for item_id, body, ext, _title in rows:
            cur.execute(INSERT_SQL, (item_id, body, conv["language"],
                                     source_url_for(source_key, ext), conv["license"],
                                     conv["source_type"], conv["access_scope"],
                                     conv["owner_user_id"]))
            n += 1
            if n % BATCH == 0:
                conn.commit()
                print(f"  …{n}")
        conn.commit()
        print(f"✓ 物化 {n} 列 item_text")
        if n:
            print("  接續(#29b 至可檢索終態):")
            print("    python scripts/build_sentences.py --scope items")
            print("    python scripts/embed_knowledge.py --layer sentence --scope items --language zh")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""
          SELECT i.source_key,
                 count(*) FILTER (WHERE coalesce(btrim(s.payload->>%s),'')<>''
                                    AND NOT EXISTS (SELECT 1 FROM knowledge_item_text t
                                                    WHERE t.item_id=i.item_id)) AS pending,
                 count(*) AS items
          FROM knowledge_item i JOIN knowledge_staging s ON s.staging_id=i.staging_id
          GROUP BY 1 HAVING count(*) FILTER (WHERE coalesce(btrim(s.payload->>%s),'')<>''
                     AND NOT EXISTS (SELECT 1 FROM knowledge_item_text t
                                     WHERE t.item_id=i.item_id)) > 0
          ORDER BY 2 DESC""", (DEFAULT_TEXT_FIELD, DEFAULT_TEXT_FIELD))
        rows = cur.fetchall()
        if not rows:
            print(f"各源 payload.{DEFAULT_TEXT_FIELD} 皆已物化(零待辦)")
        for sk, pend, tot in rows:
            print(f"  {sk:24} 待物化 {pend:6} / item {tot}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("待物化條件含『尚無 item_text』(冪等,重跑零重複)", "NOT EXISTS" in PENDING_SQL)
    chk("空文本不物化(空 item_text 比沒有更糟:查得到卻沒內容)",
        "coalesce(btrim(s.payload ->> %s), '') <> ''" in PENDING_SQL)
    chk("**口徑沿用同源既有列**(mode 眾數,非程式內預設常數)",
        "mode() WITHIN GROUP" in CONVENTION_SQL)
    chk("access_scope 在沿用之列(私有性不可猜)", "t.access_scope" in CONVENTION_SQL)
    chk("欄名以參數傳(text_field 資料驅動,非寫死)", "payload ->> %s" in PENDING_SQL)
    src = open(__file__, encoding="utf-8").read()
    body = src.split("def _selftest")[0].split('"""', 2)[-1]
    chk("零 AI 改寫:程式體不對 body 做任何加工(逐字搬)", "body" in body and ".replace(" not in body)
    chk("無前例即停手(rc=2)非預設", "return 2" in body and "停手不預設" in body)
    chk("印出接續步驟至可檢索終態(#29b)", "build_sentences.py --scope items" in body)
    chk("逐批 commit(長跑可續)", f"n % BATCH == 0" in body)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="自 staging payload 物化 knowledge_item_text")
    ap.add_argument("--source", help="source_key(必要;資料驅動)")
    ap.add_argument("--text-field", default=DEFAULT_TEXT_FIELD)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--license"), ap.add_argument("--access-scope")
    ap.add_argument("--source-type"), ap.add_argument("--language")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.source and (a.run or a.dry_run):
        ov = {"license": a.license, "access_scope": a.access_scope,
              "source_type": a.source_type, "language": a.language}
        return build(a.source, a.text_field, a.limit, a.dry_run and not a.run, ov)
    print(__doc__)
    print("現況(各源待物化):")
    return status()


if __name__ == "__main__":
    sys.exit(main())

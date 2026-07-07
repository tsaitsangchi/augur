#!/usr/bin/env python
"""本機資料夾遞迴多格式解析入庫(admin 控制台 `+資料夾`,計畫 §三)— 逐字入 knowledge_item_text。

🎯 這支在做什麼(白話):把某資料夾(含子夾)所有可解析檔案抽出逐字文字,存進知識層 item_text,
   接既有切句/嵌入/檢索鏈 → 供「誠實博學的我」對話引用。**治權硬牆(不可繞)**:
   - `license` 受 DB CHECK 只准白名單(public_domain/cc-by/cc-by-sa/cc0/**owned_local**)——**版權未明檔進不了全文表**;
     admin 須為**確有公開授權/自有可釋出**之檔聲明 `--license`(責任在 admin;DB 物理擋)。
     **owned_local=自有私有軌**(憲章 v1.36.0):用戶自有專有檔(ERP 匯出/私人筆記)硬配 `access_scope='local_private'`
     (DB CHECK chk_itext_owned_local_private 綁死、永不公開;安全繫於本機+私有+自有,**非拿來繞他人版權**)。
   - `access_scope` 預設 `local_private`(不入對外對話池,拍板P2);`source_type='local_upload'`(DB CHECK<>ai_generated)。
   - 逐字入庫、禁 AI 摘要改寫(#1);抽不出=誠實跳過分類(fileparse,#15);符號連結不跟、大小上限(#5)。
守 #1 · #15 · #5 · #6(sha1 冪等 resume)· #29。SSOT 落地模板=fetch_oa_fulltext.py;抽取器=augur.knowledge.fileparse。

執行指令矩陣:
  python scripts/acquire_local_files.py                                  # 無參數:用法+已入本機檔統計(唯讀)
  python scripts/acquire_local_files.py --dir ~/docs --license public_domain --domain finance   # 遞迴入庫
  python scripts/acquire_local_files.py --dir ~/docs --license cc-by --access-scope public       # 對外可見
  python scripts/acquire_local_files.py --dir ~/erp --license owned_local --owner-user-id 1      # 自有私有(強制 local_private)
  python scripts/acquire_local_files.py --dir ~/docs --license public_domain --dry-run           # 掃描預覽不寫
"""
import argparse
import hashlib
import os
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import corpus, fileparse

SEG_CHARS = 8000
MIN_CHARS = 50            # 抽出總長 < 此=殘片,不入庫(仿 fetch_oa_fulltext)


def _detect_lang(text):
    cjk = sum(1 for c in text[:2000] if "一" <= c <= "鿿")
    return "zh" if cjk > len([c for c in text[:2000] if not c.isspace()]) * 0.30 else "en"


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--dir")
    ap.add_argument("--license", choices=list(corpus.LICENSE_WHITELIST))
    ap.add_argument("--access-scope", choices=["public", "local_private"], default="local_private")
    ap.add_argument("--domain", default="local")
    ap.add_argument("--owner-user-id", type=int, default=None,
                    help="local_private 擁有者 app_user.user_id(RBAC 擁有者收窄;僅本人+super 可檢索)")
    ap.add_argument("--dry-run", action="store_true")
    args, _ = ap.parse_known_args()

    with db.connect() as conn:
        if not args.dir:
            print(__doc__.split("執行指令矩陣:")[1])
            with db.transaction(conn) as cur:
                cur.execute("SELECT count(*) FROM knowledge_item_text WHERE source_type='local_upload'")
                cur.execute("SELECT count(DISTINCT it.item_id), coalesce(sum(length(it.content)),0) "
                            "FROM knowledge_item_text it WHERE it.source_type='local_upload'")
                n_item, n_char = cur.fetchone()
            print(f"  已入本機檔:{n_item} item / {n_char:,} 字元")
            return
        if not args.license:
            sys.exit("須 --license(DB 硬擋只准 %s;為確有授權/自有可釋出之檔聲明,責任在 admin)"
                     % ", ".join(corpus.LICENSE_WHITELIST))
        if args.license == "owned_local" and args.access_scope != "local_private":
            sys.exit("owned_local 自有私有軌硬配 --access-scope local_private"
                     "(DB CHECK chk_itext_owned_local_private 物理擋;不繞版權)")
        root = os.path.realpath(os.path.expanduser(args.dir))
        if not os.path.isdir(root):
            sys.exit(f"非資料夾:{root}")

        stats = {"scanned": 0, "ok": 0, "dup": 0, "short": 0, "rows": 0}
        skips = {}
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            for fn in filenames:
                path = os.path.join(dirpath, fn)
                stats["scanned"] += 1
                text, reason = fileparse.extract_text(path)
                if text is None:
                    skips[reason] = skips.get(reason, 0) + 1
                    continue
                text = text.strip()
                if len(text) < MIN_CHARS:
                    stats["short"] += 1
                    continue
                sha1 = hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()
                ext_id = "localfile:" + sha1
                url = "file://" + os.path.realpath(path)
                if args.dry_run:
                    stats["ok"] += 1
                    continue
                with db.transaction(conn) as cur:      # 逐檔 commit(#6 resume);sha1 冪等
                    cur.execute("SELECT item_id FROM knowledge_item WHERE entity_type='document' AND external_id=%s",
                                (ext_id,))
                    row = cur.fetchone()
                    if row:
                        stats["dup"] += 1
                        continue
                    # source_key=NULL(FK→knowledge_source;local_upload 來源列尚未註冊=後續精修);
                    # provenance 由 url=file://realpath + external_id=localfile:sha1 承載(#1 可溯源)
                    cur.execute(
                        "INSERT INTO knowledge_item (domain, entity_type, title, external_id, url) "
                        "VALUES (%s,'document',%s,%s,%s) RETURNING item_id",
                        (args.domain, fn[:250], ext_id, url))
                    item_id = cur.fetchone()[0]
                    lang = _detect_lang(text)
                    for i in range(0, len(text), SEG_CHARS):
                        cur.execute(
                            "INSERT INTO knowledge_item_text "
                            "(item_id, seq, content, language, source_url, license, source_type, access_scope, owner_user_id) "
                            "VALUES (%s,%s,%s,%s,%s,%s,'local_upload',%s,%s)",
                            (item_id, i // SEG_CHARS + 1, text[i:i + SEG_CHARS], lang, url,
                             args.license, args.access_scope,
                             args.owner_user_id if args.access_scope == "local_private" else None))
                        stats["rows"] += 1
                    stats["ok"] += 1

        tag = "[dry-run] " if args.dry_run else ""
        print(f"{tag}掃描 {stats['scanned']} 檔 → 入庫 {stats['ok']}(seg {stats['rows']})、"
              f"重複跳 {stats['dup']}、殘片跳 {stats['short']}")
        if skips:
            print("  誠實跳過分類:" + "、".join(f"{r}={n}" for r, n in sorted(skips.items())))
        print(f"  license={args.license} access_scope={args.access_scope} domain={args.domain}"
              + ("" if args.dry_run else "  → 接 build_sentences --scope items / embed_knowledge / retrieve_all(private 需 admin 私模)"))


if __name__ == "__main__":
    main()

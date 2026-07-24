#!/usr/bin/env python
"""本機資料夾遞迴多格式解析入庫(admin 控制台 `+資料夾`,計畫 §三)— 逐字入 knowledge_item_text。

🎯 這支在做什麼(白話):把某資料夾(含子夾)所有可解析檔案抽出逐字文字,存進知識層 item_text,
   接既有切句/嵌入/檢索鏈 → 供「誠實博學的我」對話引用。**治權硬牆(不可繞)**:
   - `license` 受 DB CHECK 只准白名單(public_domain/cc-by/cc-by-sa/cc0/**owned_local**)——**版權未明檔進不了全文表**;
     admin 須為**確有公開授權/自有可釋出**之檔聲明 `--license`(責任在 admin;DB 物理擋)。
     **owned_local=自有私有軌**(憲章 v1.36.0):用戶自有專有檔(ERP 匯出/私人筆記)硬配 `access_scope='local_private'`
     (DB CHECK chk_itext_owned_local_private 綁死、永不公開;安全繫於本機+私有+自有,**非拿來繞他人版權**)。
   - `access_scope`：CLI 明示優先；未給 → `adapter_config.access_scope` → 再預設 `local_private`
     (不入對外對話池,拍板P2；**禁**把「CLI 預設 local_private」覆寫成源 cfg 的 public——否則私有意圖靜默公開)。
     `source_type='local_upload'`(DB CHECK<>ai_generated)。
   - 逐字入庫、禁 AI 摘要改寫(#1);抽不出=誠實跳過分類(fileparse,#15);符號連結不跟、大小上限(#5)。
守 #1 · #15 · #5 · #6(sha1 冪等 resume)· #29。SSOT 落地模板=fetch_oa_fulltext.py;抽取器=augur.knowledge.fileparse。

執行指令矩陣:
  python scripts/acquire_local_files.py                                  # 無參數:用法+已入本機檔統計(唯讀)
  python scripts/acquire_local_files.py --dir ~/docs --license public_domain --domain finance   # 遞迴入庫
  python scripts/acquire_local_files.py --dir ~/docs --license cc-by --access-scope public       # 對外可見
  python scripts/acquire_local_files.py --dir ~/erp --license owned_local --owner-user-id 1      # 自有私有(強制 local_private)
  python scripts/acquire_local_files.py --dir ~/docs --license public_domain --access-scope local_private  # 明示私有(蓋過源 cfg)
  python scripts/acquire_local_files.py --dir ~/docs --license public_domain --dry-run           # 掃描預覽不寫
"""
import argparse
import hashlib
import os
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import admission, corpus, fileparse

SEG_CHARS = 8000
MIN_CHARS = 50            # 抽出總長 < 此=殘片,不入庫(仿 fetch_oa_fulltext)


def _detect_lang(text):
    cjk = sum(1 for c in text[:2000] if "一" <= c <= "鿿")
    return "zh" if cjk > len([c for c in text[:2000] if not c.isspace()]) * 0.30 else "en"


def ingest_file(cur, path, *, license, access_scope, domain, source_key, source_type,
                owner_user_id=None, source_url=None):
    """單檔逐字入庫(可重用;acquire_remote_files SFTP 通道復用之,#12 不複製 INSERT)。
    抽 fileparse → sha1 冪等去重 → INSERT knowledge_item(source_key 回填)+ knowledge_item_text(分段)。
    回 (item_id|None, n_rows, status);status∈{'ok','dup','short','skip:<reason>'};dup 回既有 item_id。
    source_url 預設 file://realpath;SFTP 傳 'sftp://host/remotepath'(暫存檔會刪、file:// 不穩)。
    ⚠ 呼叫端須在同一 transaction(cur)內用,並先過 admission_gate(本函式不重複判閘、專責入庫)。"""
    text, reason = fileparse.extract_text(path)
    if text is None:
        return None, 0, "skip:" + reason
    text = text.strip()
    if len(text) < MIN_CHARS:
        return None, 0, "short"
    sha1 = hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()
    ext_id = "localfile:" + sha1
    url = source_url or ("file://" + os.path.realpath(path))
    cur.execute("SELECT item_id FROM knowledge_item WHERE entity_type='document' AND external_id=%s", (ext_id,))
    row = cur.fetchone()
    if row:
        return row[0], 0, "dup"                    # 內容 sha1 已在(跨本機/SFTP 通道去重於 item 層)
    cur.execute("INSERT INTO knowledge_item (domain, entity_type, title, external_id, url, source_key) "
                "VALUES (%s,'document',%s,%s,%s,%s) RETURNING item_id",
                (domain, os.path.basename(path)[:250], ext_id, url, source_key))
    item_id = cur.fetchone()[0]
    lang = _detect_lang(text)
    n = 0
    for i in range(0, len(text), SEG_CHARS):
        cur.execute("INSERT INTO knowledge_item_text "
                    "(item_id, seq, content, language, source_url, license, source_type, access_scope, owner_user_id) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (item_id, i // SEG_CHARS + 1, text[i:i + SEG_CHARS], lang, url,
                     license, source_type, access_scope,
                     owner_user_id if access_scope == "local_private" else None))
        n += 1
    return item_id, n, "ok"


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--dir")
    ap.add_argument("--source-key", help="knowledge_source PK(件 A1:寫入必填、admission 源-active 閘;"
                    "無 --dir 時由該源 adapter_config.root_dir 取根目錄=驅動情境 #29b)")
    ap.add_argument("--source-type", choices=list(admission.SOURCE_TYPE_WHITELIST), default="local_upload",
                    help="item_text.source_type(白名單 SSOT=admission.SOURCE_TYPE_WHITELIST;預設 local_upload)")
    ap.add_argument("--license", choices=list(corpus.LICENSE_WHITELIST))
    ap.add_argument("--access-scope", choices=["public", "local_private"], default=None,
                    help="明示優先;未給→adapter_config.access_scope→local_private(勿把預設當可覆寫為 public)")
    ap.add_argument("--domain", default="local")
    ap.add_argument("--owner-user-id", type=int, default=None,
                    help="local_private 擁有者 app_user.user_id(RBAC 擁有者收窄;僅本人+super 可檢索)")
    ap.add_argument("--acquire-only", action="store_true",
                    help="僅入庫、不自鏈下游(C3;本 script 本即 acquire-only,此為 no-op-safe 之契約旗標)")
    ap.add_argument("--dry-run", action="store_true")
    args, _ = ap.parse_known_args()

    if not args.dir and not args.source_key:              # graceful:無寫入標的 → 先印用法(免 DB)、再試統計(#29a)
        print(__doc__.split("執行指令矩陣:")[1])
        try:                                              # R5:統計移出 with,DB 不可用時仍印矩陣、不裸 traceback
            with db.connect() as conn, db.transaction(conn) as cur:
                cur.execute("SELECT count(DISTINCT it.item_id), coalesce(sum(length(it.content)),0) "
                            "FROM knowledge_item_text it WHERE it.source_type = ANY(%s)",
                            (list(admission.SOURCE_TYPE_WHITELIST),))
                n_item, n_char = cur.fetchone()
            print(f"  已入本機/檔案通道:{n_item} item / {n_char:,} 字元")
        except Exception as e:                            # noqa: BLE001
            print(f"  (DB 未連線,略過統計:{e})")
        return

    with db.connect() as conn:
        # #29b 驅動情境:給 --source-key 未給 --dir/--license 時,由該源 adapter_config 取 root_dir/預設值
        cfg = {}
        if args.source_key:
            with db.transaction(conn) as cur:
                cur.execute("SELECT adapter_config FROM knowledge_source WHERE source_key=%s", (args.source_key,))
                r = cur.fetchone()
                cfg = (r[0] or {}) if r else {}
        the_dir = args.dir or cfg.get("root_dir")
        license = args.license or cfg.get("default_license")
        # CLI 明示 > 源 cfg > local_private(R6:禁「預設 private」被源 cfg public 靜默蓋掉→假私有實公開)
        access_scope = (args.access_scope if args.access_scope is not None
                        else cfg.get("access_scope", "local_private"))
        domain = args.domain if args.domain != "local" else cfg.get("domain", "local")
        if not args.source_key:                            # 寫入必填(#29b provenance;缺→本機通道非治理公民)
            sys.exit("須 --source-key(件 A1:本機通道須註冊 knowledge_source 列並經 admission 源-active 閘;"
                     "無源列時先跑 migrate_local_admission_ddl.py --apply 註冊 proposed、再 TTY activate)")
        if not the_dir:
            sys.exit(f"須 --dir 或 source '{args.source_key}' 之 adapter_config.root_dir(#29b 驅動情境)")
        if not license:
            sys.exit("須 --license 或 adapter_config.default_license(DB 硬擋只准 %s)"
                     % ", ".join(corpus.LICENSE_WHITELIST))
        if license == "owned_local" and access_scope != "local_private":
            sys.exit("owned_local 自有私有軌硬配 access_scope=local_private(DB chk_itext_owned_local_private 物理擋)")
        with db.transaction(conn) as cur:                  # admission 統一界閘 fail-fast(C2,四件)
            ok, reason = admission.admission_gate(cur, args.source_key, license, access_scope, args.source_type)
        if not ok:
            sys.exit(reason)
        root = os.path.realpath(os.path.expanduser(the_dir))
        if not os.path.isdir(root):
            sys.exit(f"非資料夾:{root}")

        stats = {"scanned": 0, "ok": 0, "dup": 0, "short": 0, "rows": 0}
        skips = {}
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            for fn in filenames:
                path = os.path.join(dirpath, fn)
                stats["scanned"] += 1
                if args.dry_run:                       # 掃描預覽:試抽取判可入否、不寫
                    text, reason = fileparse.extract_text(path)
                    if text is None:
                        skips[reason] = skips.get(reason, 0) + 1
                    elif len(text.strip()) < MIN_CHARS:
                        stats["short"] += 1
                    else:
                        stats["ok"] += 1
                    continue
                with db.transaction(conn) as cur:      # 逐檔 commit(#6 resume);ingest_file 內 sha1 冪等(#12 單一入庫)
                    item_id, n, status = ingest_file(
                        cur, path, license=license, access_scope=access_scope, domain=domain,
                        source_key=args.source_key, source_type=args.source_type,
                        owner_user_id=args.owner_user_id)
                if status == "ok":
                    stats["ok"] += 1; stats["rows"] += n
                elif status == "dup":
                    stats["dup"] += 1
                elif status == "short":
                    stats["short"] += 1
                else:                                   # skip:<reason>
                    r = status.split(":", 1)[1]
                    skips[r] = skips.get(r, 0) + 1

        tag = "[dry-run] " if args.dry_run else ""
        print(f"{tag}掃描 {stats['scanned']} 檔 → 入庫 {stats['ok']}(seg {stats['rows']})、"
              f"重複跳 {stats['dup']}、殘片跳 {stats['short']}")
        if skips:
            print("  誠實跳過分類:" + "、".join(f"{r}={n}" for r, n in sorted(skips.items())))
        print(f"  source_key={args.source_key} source_type={args.source_type} license={license} "
              f"access_scope={access_scope} domain={domain}"
              + ("" if (args.dry_run or args.acquire_only) else
                 "  → 接 build_sentences --scope items / embed_knowledge / retrieve_all(private 需 admin 私模)"))


if __name__ == "__main__":
    main()

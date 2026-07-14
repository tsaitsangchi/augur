#!/usr/bin/env python
"""件 A2 遠端 SFTP 通道 CLI — 增量抓遠端自有檔 → owned_local 逐字入庫 → 可檢索終態(#29b 通道公民)。

🎯 這支在做什麼(白話):讀 knowledge_source(adapter='sftp')之連線設定(host/port/base_path/glob 住
   adapter_config JSONB、#29b)+ .env 憑證(SFTP_<NAME>_USER/KEYPATH、#5 不入 DB)→ open_client(strict:
   RejectPolicy+known_hosts,防 MITM)→ sftpsync 增量(mtime/size 比對、未變不重抓)→ 逐檔複用
   acquire_local_files.ingest_file 入庫(source_type='remote_sftp'、owned_local⇒local_private)→ UPSERT
   sftp_sync_state(#6 冪等帳本;changed 記 superseded_item_id、skip/oversize 記帳使收斂)→ 非 --acquire-only
   時接 build_sentences→embed 達可檢索終態。

治權(R-H1 B案):明文豁免 staging,治權繫於——admission_gate 四件(源須 active、license 白名單、
   owned_local⇒local_private、source_type∈白名單)+ item_source_gate DB trigger(件 A1)+ 源活化唯人 TTY。
   憑證絕不落 DB/log/git(#5);抓取 fileparse 確定性零 AI(#1);path-traversal 圍欄(sftpsync)。

守 #1· #5· #6· #24(單連線循序、不高併發)· #26(源放量前須人 TTY activate、AI 不自 approve)· #28· #29(a/b/c/d)。

執行指令矩陣:
  python scripts/acquire_remote_files.py                          # 無參數:印矩陣+列 sftp 源與 sync_state(唯讀)
  python scripts/acquire_remote_files.py --source sftp_docs --dry-run    # 列將抓之新增/變更檔,零寫入
  python scripts/acquire_remote_files.py --source sftp_docs --limit 3    # 首輪最小(#25)
  python scripts/acquire_remote_files.py --source sftp_docs --acquire-only   # 只入庫、下游交驅動 DAG(C3)
"""
import argparse
import os
import sys

import _bootstrap  # noqa: F401
import acquire_local_files
from augur.core import db
from augur.knowledge import admission, sftpbrowse, sftpsync

SOURCE_TYPE = "remote_sftp"


def _conn_and_cfg(cur, source_key):
    """讀 sftp 源之 adapter_config + .env 憑證,組 paramiko conn dict。fail-closed:非 sftp/非 active/缺憑證→sys.exit。"""
    cur.execute("SELECT adapter, approval_status, adapter_config FROM knowledge_source WHERE source_key=%s",
                (source_key,))
    row = cur.fetchone()
    if not row:
        sys.exit(f"source '{source_key}' 未註冊(先 INSERT knowledge_source adapter='sftp' 一列)")
    adapter, status, cfg = row[0], row[1], (row[2] or {})
    if adapter != "sftp":
        sys.exit(f"source '{source_key}' adapter='{adapter}'≠sftp(本 CLI 僅處理 SFTP 通道)")
    cred = cfg.get("cred_name") or source_key.upper()
    env = cred.upper().replace("-", "_")
    user = os.environ.get(f"SFTP_{env}_USER")
    key_path = os.environ.get(f"SFTP_{env}_KEYPATH")
    if not (cfg.get("host") and user):
        sys.exit(f"缺連線設定/憑證:adapter_config.host + .env SFTP_{env}_USER(+ KEYPATH)(#5 憑證住 .env、不入 DB)")
    conn = {"host": cfg["host"], "port": int(cfg.get("port", 22)), "user": user, "key_path": key_path}
    return conn, cfg, status


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--source")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=5000)
    ap.add_argument("--acquire-only", action="store_true", help="只入庫、不自鏈下游(C3;驅動 DAG 模式)")
    args, _ = ap.parse_known_args()

    with db.connect() as conn:
        if not args.source:                                # graceful:列 sftp 源 + sync_state(#29a)
            print(__doc__.split("執行指令矩陣:")[1])
            with db.transaction(conn) as cur:
                cur.execute("SELECT source_key, approval_status FROM knowledge_source WHERE adapter='sftp' ORDER BY 1")
                srcs = cur.fetchall()
                has_tbl = cur.execute("SELECT to_regclass('sftp_sync_state')") or cur.fetchone()[0]
            print("  已註冊 SFTP 源:" + ("(無;先 INSERT knowledge_source adapter='sftp')" if not srcs else ""))
            for sk, st in srcs:
                print(f"    · {sk} [{st}]")
            if not has_tbl:
                print("  ⚠ sftp_sync_state 未建——先跑 migrate_sftp_sync_ddl.py --apply")
            return 0
        with db.transaction(conn) as cur:
            client_cfg, cfg, status = _conn_and_cfg(cur, args.source)
            # admission 源閘(C2 統一界閘;非 active 直接擋——能抓≠該抓、活化唯人 TTY)
            lic = cfg.get("default_license", "owned_local")
            scope = cfg.get("access_scope", "local_private")
            ok, reason = admission.admission_gate(cur, args.source, lic, scope, SOURCE_TYPE)
            if not ok:
                sys.exit(reason)
            cur.execute("SELECT to_regclass('sftp_sync_state')")
            if not cur.fetchone()[0]:
                sys.exit("sftp_sync_state 未建——先跑 scripts/migrate_sftp_sync_ddl.py --apply")
            # 預載 prior_state(增量比對基準)
            cur.execute("SELECT remote_path, remote_mtime, size_bytes FROM sftp_sync_state WHERE source_key=%s",
                        (args.source,))
            prior = {rp: (mt, sz) for rp, mt, sz in cur.fetchall()}
        domain = cfg.get("domain", "local")
        owner = cfg.get("owner_user_id")
        client = sftpbrowse.open_client(client_cfg, strict=True)    # headless:RejectPolicy+known_hosts(#5)
        stats = {"new": 0, "changed": 0, "skip": 0, "dup": 0, "short": 0, "rows": 0, "err": 0}
        import tempfile
        dest = tempfile.mkdtemp(prefix="sftp_" + args.source + "_")
        try:
            for sf in sftpsync.iter_changed_files(client, client_cfg["host"], cfg.get("base_path", "."),
                                                  cfg.get("glob"), dest, prior,
                                                  download=not args.dry_run, max_files=args.limit):
                if args.dry_run:
                    print(f"  [dry] {sf.change} {sf.remote_path} ({sf.size_bytes}B)")
                    stats[sf.change if sf.change in stats else "skip"] += 1
                    continue
                with db.transaction(conn) as cur:
                    if sf.change == "skip":                # oversize/unsafe:記帳(item_id NULL)使下輪不重抓(收斂)
                        _upsert(cur, args.source, sf, item_id=None, superseded=None)
                        stats["skip"] += 1
                        continue
                    src_url = f"sftp://{sf.remote_host}{sf.remote_path}"
                    item_id, n, status2 = acquire_local_files.ingest_file(
                        cur, sf.local_path, license=lic, access_scope=scope, domain=domain,
                        source_key=args.source, source_type=SOURCE_TYPE,
                        owner_user_id=owner, source_url=src_url)
                    sup = None
                    if sf.change == "changed":             # 對抗審查:changed 記舊 item_id 為 superseded(不遺棄舊版稽核)
                        cur.execute("SELECT item_id FROM sftp_sync_state WHERE source_key=%s AND remote_path=%s",
                                    (args.source, sf.remote_path))
                        old = cur.fetchone()
                        sup = old[0] if old and old[0] and old[0] != item_id else None
                    _upsert(cur, args.source, sf, item_id=item_id, superseded=sup)
                    if status2 == "ok":
                        stats["new" if sf.change == "new" else "changed"] += 1; stats["rows"] += n
                    elif status2 == "dup":
                        stats["dup"] += 1
                    elif status2 == "short":
                        stats["short"] += 1
                    else:
                        stats["skip"] += 1
        finally:
            client.close()
            import shutil
            shutil.rmtree(dest, ignore_errors=True)
        tag = "[dry-run] " if args.dry_run else ""
        print(f"{tag}SFTP {args.source}:new {stats['new']}、changed {stats['changed']}、skip {stats['skip']}、"
              f"dup {stats['dup']}、short {stats['short']}(seg {stats['rows']})")
        if not args.dry_run and not args.acquire_only and (stats["new"] or stats["changed"]):
            print("  → 接下游(build_sentences→embed):建議交驅動 DAG(refresh_knowledge_pipeline);"
                  "本 CLI 保留 --acquire-only 供 DAG 模式跳過")
    return 0


def _upsert(cur, source_key, sf, *, item_id, superseded):
    cur.execute("""
        INSERT INTO sftp_sync_state
          (source_key, remote_host, remote_path, remote_mtime, size_bytes, content_sha1,
           item_id, superseded_item_id, change_kind, last_synced)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s, now())
        ON CONFLICT (source_key, remote_path) DO UPDATE SET
          remote_mtime=EXCLUDED.remote_mtime, size_bytes=EXCLUDED.size_bytes,
          content_sha1=EXCLUDED.content_sha1, item_id=EXCLUDED.item_id,
          superseded_item_id=COALESCE(EXCLUDED.superseded_item_id, sftp_sync_state.superseded_item_id),
          change_kind=EXCLUDED.change_kind, last_synced=now()
        """, (source_key, sf.remote_host, sf.remote_path, sf.remote_mtime, sf.size_bytes,
              sf.content_sha1, item_id, superseded, sf.change))


if __name__ == "__main__":
    sys.exit(main())

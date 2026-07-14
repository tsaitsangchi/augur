#!/usr/bin/env python
"""🎯 件 A1 本機/SFTP 通道公民化之 DDL 遷移(hugo 2026-07-14 拍板 R-A-T1/保守 C1)——冪等、可 dry-run。

四件冪等 DDL(保守 C1:**不動 source_type DB CHECK**——維持黑名單擋 ai_generated+容 legacy NULL,
source_type 白名單由 admission_gate Python belt 對新通道強制,零斷通道風險):
  (1) seed knowledge_domain 'local'(本機匯入 domain;加 FK 前必先在)。
  (2) knowledge_item.domain FK → knowledge_domain(收斂 Task#16 增補;實證零 orphan、NOT VALID→VALIDATE 降鎖)。
  (3) **item_source_gate trigger(R-A-T1 必要、掛 knowledge_item_text BEFORE INSERT)**——B案≈A案物理牆:
      父 item 之源 protocol∈(local_file,sftp) 且 approval_status≠active → RAISE(能抓≠該抓 DB 強制);
      owned_local∧local_private∧父 item source_key IS NULL → RAISE(堵 NULL 逃生口,對抗審查 blocker 修正)。
  (4) register 本機源列 local_files_<域>(admission.register_local_source,approval_status='proposed';活化唯人 TTY)。

⚠ #30:本遷移含 254k 列 FK VALIDATE + item_text(15 萬,harvest 寫入中)加 trigger——**須 pg_dump 完成後、
   audit 綠、harvest 靜止再 --apply**(dump 期間/大量寫入中加 trigger=鎖風暴);--dry-run 隨時可跑(唯讀)。
守 #12(DDL 單一住所)· #6(冪等 IF NOT EXISTS/ON CONFLICT/DROP IF EXISTS)· #29a/#29d· #30· 隔離不變式。

執行指令矩陣:
  python scripts/migrate_local_admission_ddl.py                    # 無參數=--dry-run(唯讀:印各步現況+將做什麼)
  python scripts/migrate_local_admission_ddl.py --dry-run          # 同上
  python scripts/migrate_local_admission_ddl.py --apply            # 冪等套用(#30:dump 後+audit 綠+harvest 靜止)
  python scripts/migrate_local_admission_ddl.py --apply --source-key local_files_docs --root-dir ~/docs --domain local
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import admission

TRIGGER_FN = """
CREATE OR REPLACE FUNCTION trg_item_source_gate() RETURNS trigger AS $$
DECLARE sk varchar; proto varchar; st varchar;
BEGIN
  SELECT ki.source_key INTO sk FROM knowledge_item ki WHERE ki.item_id = NEW.item_id;
  -- 堵 NULL 逃生口(對抗審查 blocker):owned_local 私有內容 source_key IS NULL = 未經來源治理直插
  IF NEW.license = 'owned_local' AND NEW.access_scope = 'local_private' AND sk IS NULL THEN
    RAISE EXCEPTION 'item_source_gate: owned_local/local_private 內容須有 source_key(件 A1 治理公民;禁 NULL 逃生口)';
  END IF;
  IF sk IS NOT NULL THEN
    SELECT ks.protocol, ks.approval_status INTO proto, st FROM knowledge_source ks WHERE ks.source_key = sk;
    IF proto IN ('local_file','sftp') AND st IS DISTINCT FROM 'active' THEN
      RAISE EXCEPTION 'item_source_gate: source % (protocol=%%) approval_status=%% <> active(能抓≠該抓;活化唯人 TTY)', sk, proto, st;
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


def _has(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchone() is not None


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--source-key", default="local_files_local")
    ap.add_argument("--root-dir", default=None)
    ap.add_argument("--domain", default="local")
    ap.add_argument("--license", default="owned_local")
    args, _ = ap.parse_known_args()
    apply = args.apply and not args.dry_run
    with db.connect() as conn:
        with db.transaction(conn) as cur:
            dom_exists = _has(cur, "SELECT 1 FROM knowledge_domain WHERE domain=%s", (args.domain,))
            fk_exists = _has(cur, "SELECT 1 FROM pg_constraint WHERE conname='fk_item_domain'")
            trg_exists = _has(cur, "SELECT 1 FROM pg_trigger WHERE tgname='item_source_gate'")
            src_exists = _has(cur, "SELECT 1 FROM knowledge_source WHERE source_key=%s", (args.source_key,))
            cur.execute("SELECT count(DISTINCT ki.domain) FROM knowledge_item ki "
                        "LEFT JOIN knowledge_domain kd ON kd.domain=ki.domain WHERE kd.domain IS NULL")
            orphans = cur.fetchone()[0]
        print("件 A1 admission DDL 現況(保守 C1:不動 source_type CHECK):")
        print(f"  (1) domain '{args.domain}' seed: {'已在' if dom_exists else '待建'}")
        print(f"  (2) knowledge_item.domain FK: {'已在' if fk_exists else '待加'}(item domain orphan={orphans};需 0 才可加)")
        print(f"  (3) item_source_gate trigger: {'已在' if trg_exists else '待建'}(掛 item_text、R-A-T1 物理牆)")
        print(f"  (4) 源列 '{args.source_key}' register: {'已在' if src_exists else '待註冊(proposed)'}")
        if not apply:
            print("\n(唯讀 dry-run;--apply 才套用。⚠ #30:須 dump 後+audit 綠+harvest 靜止再 --apply)")
            return 0
        # ---- --apply(冪等)----
        if not dom_exists:
            with db.transaction(conn) as cur:
                cur.execute("INSERT INTO knowledge_domain (domain,label_zh,is_authz_boundary,is_investment,enabled) "
                            "VALUES (%s,'本機匯入',false,false,true) ON CONFLICT (domain) DO NOTHING", (args.domain,))
            print(f"  ✓ (1) domain '{args.domain}' seeded")
        if not fk_exists:
            if orphans:
                print(f"  ⚠ (2) 跳過 FK:item domain 有 {orphans} orphan(先 seed 缺漏 domain);不阻其餘步")
            else:
                with db.transaction(conn) as cur:
                    cur.execute("ALTER TABLE knowledge_item ADD CONSTRAINT fk_item_domain "
                                "FOREIGN KEY (domain) REFERENCES knowledge_domain(domain) NOT VALID")
                with db.transaction(conn) as cur:
                    cur.execute("ALTER TABLE knowledge_item VALIDATE CONSTRAINT fk_item_domain")
                print("  ✓ (2) fk_item_domain 加+VALIDATE")
        if not trg_exists:
            with db.transaction(conn) as cur:
                cur.execute(TRIGGER_FN)
                cur.execute("DROP TRIGGER IF EXISTS item_source_gate ON knowledge_item_text")
                cur.execute("CREATE TRIGGER item_source_gate BEFORE INSERT ON knowledge_item_text "
                            "FOR EACH ROW EXECUTE FUNCTION trg_item_source_gate()")
            print("  ✓ (3) item_source_gate trigger 建(掛 item_text)")
        with db.transaction(conn) as cur:                  # (4) 冪等 register(ON CONFLICT DO NOTHING)
            n = admission.register_local_source(cur, args.source_key, domain=args.domain,
                                                default_license=args.license, root_dir=args.root_dir)
        print(f"  ✓ (4) 源列 '{args.source_key}' {'新註冊 proposed' if n else '已存在(冪等)'}"
              "——活化須人 TTY:review_knowledge_source.py")
        print("\n完成。下一步:hugo TTY 活化源→acquire_local_files --source-key 即可入庫(admission 四件+trigger 物理牆)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

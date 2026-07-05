#!/usr/bin/env python
"""domain 標註 hygiene 常備稽核器(RBAC P2)— domain 由「因子鏈純度隔離」兼任「授權邊界」之 referential 稽核。

🎯 這支在做什麼(白話):RBAC 把 knowledge_item.domain 當授權邊界後,「標錯 domain＝靜默越權/漏權」。
   本器常備稽核:(a) **孤兒域**——knowledge_item.domain 有、knowledge_domain 字典無(FK VALIDATE 前必為 0);
   (b) 各域**是否已拍板為授權邊界**(is_authz_boundary)與列數;(c) 未進字典的域清單。
   `--seed` 把現存域**fail-closed 註冊**入字典(is_authz_boundary=FALSE、非邊界——**只註冊、不賦權**,
   為 FK 鋪路;哪些域升為授權邊界＝決策層走 manage_rbac_user.py --add-domain --authz-boundary 拍板,§8.2#3)。
   **兩階段 FK 與升邊界不在此自動執行**(FK 有 #30 DDL 時機鐵律、邊界是政策決定)。
守 #5(授權邊界 referential integrity)· #1(隔離、稽核不觸預測)· #29(個別可執行、資料驅動)· 憲章 v1.28.0(RBAC 準則 v)。

執行指令矩陣:
  python scripts/audit_domain_hygiene.py            # 稽核報告(唯讀):孤兒域/邊界狀態/覆蓋
  python scripts/audit_domain_hygiene.py --seed     # 把現存 domain fail-closed 註冊入字典(is_authz_boundary=FALSE)
"""
import argparse

import _bootstrap  # noqa: F401
from augur.core import db


def audit(cur):
    cur.execute("SELECT to_regclass('knowledge_domain')")
    if cur.fetchone()[0] is None:
        print("knowledge_domain 字典未建;先 python scripts/migrate_rbac_ddl.py --migrate")
        return
    cur.execute("SELECT count(DISTINCT domain) FROM knowledge_item")
    n_item_dom = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM knowledge_domain")
    n_dict = cur.fetchone()[0]
    # 孤兒域:item 有、字典無(兩階段 FK VALIDATE 前必 0)
    cur.execute("SELECT ki.domain, count(*) FROM knowledge_item ki "
                "LEFT JOIN knowledge_domain kd ON kd.domain = ki.domain "
                "WHERE kd.domain IS NULL GROUP BY ki.domain ORDER BY count(*) DESC")
    orphans = cur.fetchall()
    print(f"── domain hygiene 稽核 ──")
    print(f"  knowledge_item 相異域: {n_item_dom}   knowledge_domain 字典: {n_dict} 列")
    if orphans:
        print(f"  ⚠ 孤兒域(item 有/字典無){len(orphans)} 個(FK VALIDATE 前須為 0，--seed 註冊):")
        for d, n in orphans[:20]:
            print(f"      {d:40} {n:>7} 列")
    else:
        print("  ✓ 無孤兒域(所有 item.domain 皆在字典)")
    # 已拍板為授權邊界之域
    cur.execute("SELECT domain, is_authz_boundary, is_investment FROM knowledge_domain ORDER BY is_authz_boundary DESC, domain")
    rows = cur.fetchall()
    if rows:
        nb = sum(1 for _, b, _ in rows if b)
        print(f"  授權邊界域(is_authz_boundary=true){nb}/{len(rows)}(其餘非邊界=非 super 一律 deny):")
        for d, b, inv in rows:
            if b or inv:
                print(f"      {'[邊界]' if b else '      '}{'[investment]' if inv else ''} {d}")
        if nb == 0:
            print("      (尚無域被拍板為授權邊界；非 super 使用者現階段對全部域 deny＝fail-closed 安全預設)")


def seed(cur):
    """fail-closed 註冊:現存 domain 入字典、is_authz_boundary=FALSE(只註冊不賦權)。冪等。"""
    cur.execute("SELECT DISTINCT domain FROM knowledge_item WHERE domain IS NOT NULL")
    doms = [r[0] for r in cur.fetchall()]
    n = 0
    for d in doms:
        cur.execute("INSERT INTO knowledge_domain (domain, label_zh, is_authz_boundary, is_investment) "
                    "VALUES (%s,%s,false,%s) ON CONFLICT (domain) DO NOTHING",
                    (d, d, d == "investment"))
        n += cur.rowcount
    print(f"--seed:{len(doms)} 域,新註冊 {n} 列(is_authz_boundary=FALSE、fail-closed)。")
    print("  → 升某域為授權邊界(政策決定,§8.2#3):python scripts/manage_rbac_user.py --add-domain --domain X --label ... --authz-boundary")
    print("  → 兩階段 FK(需 #30:排 pg_dump 後、確認無 active dump):見計畫 §5 P2 DDL,決策層執行。")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--seed", action="store_true")
    args, _ = ap.parse_known_args()
    with db.connect() as conn, db.transaction(conn) as cur:
        if args.seed:
            seed(cur)
        else:
            audit(cur)


if __name__ == "__main__":
    main()

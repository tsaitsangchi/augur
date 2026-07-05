#!/usr/bin/env python
"""RBAC 使用者/群組/授權管理 CLI(P1)— 唯一建帳號路徑、全資料驅動 INSERT。

🎯 這支在做什麼(白話):bootstrap 首 admin、建使用者、設密碼、建群組、把人加進群組、授權群組可讀哪些
   domain——全部純 INSERT/UPDATE 落 PostgreSQL,加群組/授權零改碼(#29b 資料驅動)。密碼一律走 getpass
   (禁 --password 入 shell history);首帳號必為 --superuser(空表 bootstrap);--set-super/--grant-domain
   須 --confirm(授權某次≠授權所有同類 #6)並落 knowledge_access_audit(#10 可溯源)。CLI=本機信任邊界
   (跑此 script=有 shell 權=可信),故建帳號本身不另鑑權。
守 #5(密碼 getpass/最小權)· #6(破壞性/授權操作 --confirm)· #10(授權變更落稽核)· #29(單一參數化工具、資料驅動)。

執行指令矩陣:
  python scripts/manage_rbac_user.py                                              # 無參數:印矩陣 + --list
  python scripts/manage_rbac_user.py --create-user --username hugo --superuser    # bootstrap 首 admin(getpass 密碼)
  python scripts/manage_rbac_user.py --create-user --username bob                 # 一般帳號(表非空後)
  python scripts/manage_rbac_user.py --set-password --username hugo
  python scripts/manage_rbac_user.py --deactivate --username bob                  # 停用(即時撤 session)
  python scripts/manage_rbac_user.py --set-super --username alice --confirm
  python scripts/manage_rbac_user.py --add-domain --domain investment --label 投資 --authz-boundary  # 域字典拍板入字典
  python scripts/manage_rbac_user.py --create-group --group 研發組
  python scripts/manage_rbac_user.py --add-to-group --username bob --group 研發組
  python scripts/manage_rbac_user.py --grant-domain --group 研發組 --domain rd_mgmt --confirm
  python scripts/manage_rbac_user.py --explain-access --username bob             # 該人經哪些群組得哪些 domain
  python scripts/manage_rbac_user.py --list
"""
import argparse
import getpass
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import identity


def _audit(cur, action, outcome, detail, user_id=None):
    cur.execute("INSERT INTO knowledge_access_audit (user_id, action, outcome, detail) VALUES (%s,%s,%s,%s)",
                (user_id, action, outcome, detail))


def _user_id(cur, username):
    cur.execute("SELECT user_id FROM app_user WHERE lower(username)=lower(%s)", (username,))
    r = cur.fetchone()
    return r[0] if r else None


def _group_id(cur, group):
    cur.execute("SELECT group_id FROM permission_group WHERE group_name=%s", (group,))
    r = cur.fetchone()
    return r[0] if r else None


def _getpass_twice():
    pw = getpass.getpass("密碼:")
    if pw != getpass.getpass("再輸入一次:"):
        sys.exit("兩次不符")
    if len(pw) < 8:
        sys.exit("密碼至少 8 字元")
    return pw


def cmd_create_user(cur, a):
    if _user_id(cur, a.username) is not None:
        sys.exit(f"帳號已存在:{a.username}")
    cur.execute("SELECT count(*) FROM app_user")
    empty = cur.fetchone()[0] == 0
    if empty and not a.superuser:
        sys.exit("bootstrap 首帳號必為 --superuser(否則建出無人能管的無權孤兒;fail-closed)")
    pw = _getpass_twice()
    cur.execute("INSERT INTO app_user (username, pw_hash, is_superuser) VALUES (%s,%s,%s) RETURNING user_id",
                (a.username, identity.hash_password(pw), bool(a.superuser)))
    uid = cur.fetchone()[0]
    _audit(cur, "create_user", "ok", f"{a.username} super={bool(a.superuser)}", uid)
    print(f"✓ 建帳號 {a.username}(user_id={uid}, superuser={bool(a.superuser)})")


def cmd_set_password(cur, a):
    uid = _user_id(cur, a.username)
    if uid is None:
        sys.exit(f"無此帳號:{a.username}")
    pw = _getpass_twice()
    cur.execute("UPDATE app_user SET pw_hash=%s, updated_at=now() WHERE user_id=%s",
                (identity.hash_password(pw), uid))
    identity.revoke_user_sessions(uid)          # 改密即撤所有 session、強制重登
    _audit(cur, "set_password", "ok", a.username, uid)
    print(f"✓ 已改密並撤銷 {a.username} 全部 session")


def cmd_deactivate(cur, a, active):
    uid = _user_id(cur, a.username)
    if uid is None:
        sys.exit(f"無此帳號:{a.username}")
    cur.execute("UPDATE app_user SET is_active=%s, updated_at=now() WHERE user_id=%s", (active, uid))
    if not active:
        identity.revoke_user_sessions(uid)      # 停用同交易撤 session(下一請求即失效)
    _audit(cur, "reactivate" if active else "deactivate", "ok", a.username, uid)
    print(f"✓ {a.username} is_active={active}")


def cmd_set_super(cur, a):
    if not a.confirm:
        sys.exit("--set-super 須 --confirm(提權=授權某次≠授權所有同類 #6)")
    uid = _user_id(cur, a.username)
    if uid is None:
        sys.exit(f"無此帳號:{a.username}")
    cur.execute("UPDATE app_user SET is_superuser=true, updated_at=now() WHERE user_id=%s", (uid,))
    _audit(cur, "set_super", "ok", a.username, uid)
    print(f"✓ {a.username} 已設為 superuser")


def cmd_add_domain(cur, a):
    cur.execute("INSERT INTO knowledge_domain (domain, label_zh, is_authz_boundary, is_investment) "
                "VALUES (%s,%s,%s,%s) ON CONFLICT (domain) DO UPDATE SET "
                "label_zh=EXCLUDED.label_zh, is_authz_boundary=EXCLUDED.is_authz_boundary, is_investment=EXCLUDED.is_investment",
                (a.domain, a.label or a.domain, bool(a.authz_boundary), bool(a.investment)))
    _audit(cur, "add_domain", "ok", f"{a.domain} authz={bool(a.authz_boundary)}")
    print(f"✓ 域字典:{a.domain}(label={a.label or a.domain}, authz_boundary={bool(a.authz_boundary)})")


def cmd_create_group(cur, a):
    cur.execute("INSERT INTO permission_group (group_name) VALUES (%s) ON CONFLICT (group_name) DO NOTHING "
                "RETURNING group_id", (a.group,))
    r = cur.fetchone()
    _audit(cur, "create_group", "ok", a.group)
    print(f"✓ 群組 {a.group}" + (f"(group_id={r[0]})" if r else "(已存在)"))


def cmd_add_to_group(cur, a):
    uid, gid = _user_id(cur, a.username), _group_id(cur, a.group)
    if uid is None or gid is None:
        sys.exit("帳號或群組不存在(先 --create-user / --create-group)")
    cur.execute("INSERT INTO user_group (user_id, group_id, granted_by) VALUES (%s,%s,%s) "
                "ON CONFLICT DO NOTHING", (uid, gid, "cli"))
    _audit(cur, "add_to_group", "ok", f"{a.username}→{a.group}", uid)
    print(f"✓ {a.username} 加入群組 {a.group}")


def cmd_grant_domain(cur, a):
    if not a.confirm:
        sys.exit("--grant-domain 須 --confirm(授權變更 #6)")
    gid = _group_id(cur, a.group)
    if gid is None:
        sys.exit(f"無此群組:{a.group}")
    cur.execute("SELECT is_authz_boundary FROM knowledge_domain WHERE domain=%s", (a.domain,))
    r = cur.fetchone()
    if r is None:
        sys.exit(f"domain「{a.domain}」不在字典(先 --add-domain 由決策層拍板)")
    if not r[0]:
        sys.exit(f"domain「{a.domain}」未拍板為授權邊界(is_authz_boundary=false;--add-domain --authz-boundary 才可授)")
    cur.execute("INSERT INTO group_domain_grant (group_id, domain, granted_by) VALUES (%s,%s,%s) "
                "ON CONFLICT DO NOTHING", (gid, a.domain, "cli"))
    _audit(cur, "grant_domain", "ok", f"{a.group}→{a.domain}")
    print(f"✓ 群組 {a.group} 授權可讀 domain={a.domain}")


def cmd_explain_access(cur, a):
    uid = _user_id(cur, a.username)
    if uid is None:
        sys.exit(f"無此帳號:{a.username}")
    cur.execute("SELECT is_superuser FROM app_user WHERE user_id=%s", (uid,))
    if cur.fetchone()[0]:
        print(f"{a.username}:superuser → 可讀【全部 domain、不受限】")
        return
    cur.execute("SELECT g.group_name, gd.domain FROM user_group ug "
                "JOIN permission_group g ON g.group_id=ug.group_id "
                "LEFT JOIN group_domain_grant gd ON gd.group_id=g.group_id "
                "WHERE ug.user_id=%s ORDER BY g.group_name, gd.domain", (uid,))
    rows = cur.fetchall()
    if not rows:
        print(f"{a.username}:無群組 → allowed_domains=∅(預設 deny、看不到任何 domain)")
        return
    print(f"{a.username} 經群組取得之 domain:")
    for gname, dom in rows:
        print(f"  群組 {gname:12} → {dom or '(此群組尚無 domain 授權)'}")


def cmd_list(cur):
    cur.execute("SELECT user_id, username, is_superuser, is_active, "
                "(SELECT count(*) FROM user_group ug WHERE ug.user_id=u.user_id) "
                "FROM app_user u ORDER BY user_id")
    rows = cur.fetchall()
    if not rows:
        print("(app_user 空 — 尚未 bootstrap;先 --create-user --username <你> --superuser)")
        return
    print("使用者:")
    for uid, un, sup, act, ng in rows:
        print(f"  #{uid} {un:16} {'[superuser]' if sup else ''}{'' if act else ' [停用]'} 群組數={ng}")
    cur.execute("SELECT group_name, (SELECT count(*) FROM group_domain_grant gd WHERE gd.group_id=g.group_id) "
                "FROM permission_group g ORDER BY group_name")
    grp = cur.fetchall()
    if grp:
        print("群組:")
        for gn, nd in grp:
            print(f"  {gn:16} domain 授權數={nd}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    for flag in ("create-user", "set-password", "deactivate", "reactivate", "set-super",
                 "add-domain", "create-group", "add-to-group", "grant-domain", "explain-access", "list"):
        ap.add_argument("--" + flag, action="store_true", dest=flag.replace("-", "_"))
    ap.add_argument("--username")
    ap.add_argument("--group")
    ap.add_argument("--domain")
    ap.add_argument("--label")
    ap.add_argument("--superuser", action="store_true")
    ap.add_argument("--authz-boundary", action="store_true", dest="authz_boundary")
    ap.add_argument("--investment", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    a, _ = ap.parse_known_args()

    with db.connect() as conn, db.transaction(conn) as cur:
        if a.create_user:      cmd_create_user(cur, a)
        elif a.set_password:   cmd_set_password(cur, a)
        elif a.deactivate:     cmd_deactivate(cur, a, active=False)
        elif a.reactivate:     cmd_deactivate(cur, a, active=True)
        elif a.set_super:      cmd_set_super(cur, a)
        elif a.add_domain:     cmd_add_domain(cur, a)
        elif a.create_group:   cmd_create_group(cur, a)
        elif a.add_to_group:   cmd_add_to_group(cur, a)
        elif a.grant_domain:   cmd_grant_domain(cur, a)
        elif a.explain_access: cmd_explain_access(cur, a)
        else:
            if not a.list:
                print(__doc__.split("執行指令矩陣:")[1])
            cmd_list(cur)


if __name__ == "__main__":
    main()

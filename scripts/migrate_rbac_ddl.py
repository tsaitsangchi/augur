#!/usr/bin/env python
"""RBAC 群組模型 DDL 遷移器(P1)— 建 app_user + 群組(多對多) + app_session + 稽核 + domain 字典。

🎯 這支在做什麼(白話):把 RBAC 設計計畫(reports/augur_rbac_design_plan_20260705.md §2)之資料模型
   冪等落地本地 PostgreSQL——一切資料住 PG(憲章 v1.26.0 資料本質)。全部 CREATE TABLE IF NOT EXISTS /
   ADD COLUMN IF NOT EXISTS(可重放),職責與 migrate_text_understanding_ddl.py 隔離。**不 seed
   knowledge_domain**(域字典須決策層逐一人工拍板 is_authz_boundary,禁 INSERT SELECT DISTINCT 把
   標錯的域合法化;見計畫 §2 Step 0)。權限模型:app_user(無 role 欄)+ user_group/group_domain_grant
   多對多 + is_superuser 短路旗標;加群組/授權皆 INSERT 零改碼(#29b)。
守 #5(存取控制基礎設施)· #12(SSOT、與既有遷移器職責隔離)· #29(個別可執行、DDL 住遷移器)· 憲章 v1.26.0(資料住 PG)。

執行指令矩陣:
  python scripts/migrate_rbac_ddl.py                 # 無參數:印本矩陣 + 各表存在狀態(唯讀、不建)
  python scripts/migrate_rbac_ddl.py --migrate       # 冪等建全部 RBAC 表(可安全重放)
"""
import argparse
import sys

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db

TABLES = ("knowledge_domain", "app_user", "permission_group", "user_group",
          "group_domain_grant", "app_session", "knowledge_access_audit")

DDL = [
    # Step 0 — domain 字典(referential-integrity 地基;未拍板 domain 不可被 grant)
    """CREATE TABLE IF NOT EXISTS knowledge_domain (
         domain            varchar(64) PRIMARY KEY,
         label_zh          varchar(128) NOT NULL,
         is_authz_boundary boolean NOT NULL DEFAULT false,
         is_investment     boolean NOT NULL DEFAULT false,
         enabled           boolean NOT NULL DEFAULT true,
         note              text,
         created_at        timestamptz NOT NULL DEFAULT now()
       )""",
    # Step 1 — app_user(無 role 欄;is_superuser 為 resolver 短路旗標)
    """CREATE TABLE IF NOT EXISTS app_user (
         user_id        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
         username       varchar(64)  NOT NULL,
         pw_hash        text         NOT NULL,
         is_superuser   boolean      NOT NULL DEFAULT false,
         is_active      boolean      NOT NULL DEFAULT true,
         failed_logins  integer      NOT NULL DEFAULT 0,
         locked_until   timestamptz  NULL,
         last_login_at  timestamptz  NULL,
         created_at     timestamptz  NOT NULL DEFAULT now(),
         updated_at     timestamptz  NOT NULL DEFAULT now()
       )""",
    "CREATE UNIQUE INDEX IF NOT EXISTS uq_app_user_username ON app_user (lower(username))",
    # Step 2 — 群組 + 兩張多對多連結表
    """CREATE TABLE IF NOT EXISTS permission_group (
         group_id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
         group_name varchar(64) NOT NULL UNIQUE,
         note       text,
         created_at timestamptz NOT NULL DEFAULT now()
       )""",
    """CREATE TABLE IF NOT EXISTS user_group (
         user_id    bigint NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
         group_id   bigint NOT NULL REFERENCES permission_group(group_id) ON DELETE CASCADE,
         granted_at timestamptz NOT NULL DEFAULT now(),
         granted_by varchar(64),
         PRIMARY KEY (user_id, group_id)
       )""",
    """CREATE TABLE IF NOT EXISTS group_domain_grant (
         group_id   bigint      NOT NULL REFERENCES permission_group(group_id) ON DELETE CASCADE,
         domain     varchar(64) NOT NULL REFERENCES knowledge_domain(domain),
         granted_at timestamptz NOT NULL DEFAULT now(),
         granted_by varchar(64),
         note       text,
         PRIMARY KEY (group_id, domain)
       )""",
    # Step 3 — app_session(持久化、前後台共用;cookie 存明文、DB 只存 sha256)
    """CREATE TABLE IF NOT EXISTS app_session (
         token_hash   text        PRIMARY KEY,
         user_id      bigint      NOT NULL REFERENCES app_user(user_id) ON DELETE CASCADE,
         issued_at    timestamptz NOT NULL DEFAULT now(),
         expires_at   timestamptz NOT NULL,
         last_seen_at timestamptz NOT NULL DEFAULT now(),
         revoked_at   timestamptz NULL,
         client_note  varchar(128) NULL,
         client_ip    inet        NULL
       )""",
    "CREATE INDEX IF NOT EXISTS idx_session_user   ON app_session(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_session_expiry ON app_session(expires_at)",
    # Step 4 — 稽核落 DB
    """CREATE TABLE IF NOT EXISTS knowledge_access_audit (
         audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
         user_id  bigint,
         action   varchar(32) NOT NULL,
         domains  text,
         is_super boolean,
         outcome  varchar(16) NOT NULL,
         detail   text,
         at       timestamptz NOT NULL DEFAULT now()
       )""",
    # Step 5 — local_private 擁有者欄(ADD COLUMN IF NOT EXISTS 含 inline FK 亦冪等)
    "ALTER TABLE knowledge_item_text ADD COLUMN IF NOT EXISTS owner_user_id bigint REFERENCES app_user(user_id)",
]


def _status(cur):
    print("RBAC 表存在狀態(唯讀):")
    for t in TABLES:
        cur.execute("SELECT to_regclass(%s)", (t,))
        exists = cur.fetchone()[0] is not None
        n = 0
        if exists:
            cur.execute(f"SELECT count(*) FROM {t}")
            n = cur.fetchone()[0]
        print(f"  {'✓' if exists else '✗'} {t:24} {'列數 '+str(n) if exists else '(未建)'}")
    cur.execute("SELECT 1 FROM information_schema.columns "
                "WHERE table_name='knowledge_item_text' AND column_name='owner_user_id'")
    print(f"  {'✓' if cur.fetchone() else '✗'} knowledge_item_text.owner_user_id 欄")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--migrate", action="store_true")
    args, _ = ap.parse_known_args()
    with db.connect() as conn:
        if not args.migrate:
            print(__doc__.split("執行指令矩陣:")[1])
            with db.transaction(conn) as cur:
                _status(cur)
            print("\n→ 加 --migrate 冪等建表。**不 seed knowledge_domain**(域字典須決策層人工拍板,見計畫 §2 Step 0)。")
            return
        with db.transaction(conn) as cur:
            for stmt in DDL:
                cur.execute(stmt)
        print("migrate:RBAC DDL 冪等完成(CREATE TABLE/ADD COLUMN IF NOT EXISTS 可重放)。")
        with db.transaction(conn) as cur:
            _status(cur)
        print("\n下一步:python scripts/manage_rbac_user.py --create-user --username <你> --superuser(bootstrap 首 admin)。")


if __name__ == "__main__":
    main()

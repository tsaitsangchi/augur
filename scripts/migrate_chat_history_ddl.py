#!/usr/bin/env python
"""對話歷史 DDL 遷移(chat_session/chat_message)— 前台對話持久化(隔離命門:非預測資料)。

🎯 這支在做什麼(白話):建前台對話歷史兩表 + index + CHECK + owner CASCADE + 非預測 COMMENT;
   冪等(IF NOT EXISTS)、可重跑。對話原文＝真實往來、owner＝user_id、access_scope 語意＝local_private;
   **嚴禁進預測管線/當特徵、不得註冊為 dataset_catalog dataset(隔離命門;COMMENT 明標、isolation 測試釘死)**。
守 #5(型別/約束紀律)· 隔離命門(非預測資料)· 憲章 v1.29(RBAC owner 收窄)· 計畫 §7.1(三鏡對抗審查定稿)。

執行指令矩陣:
  python scripts/migrate_chat_history_ddl.py            # 無參數:印本矩陣 + 現況(不改 DB)
  python scripts/migrate_chat_history_ddl.py --migrate  # 建表(冪等、可重跑)
"""
import argparse
import sys

import _bootstrap  # noqa: F401  (scripts 個別可執行,#29a)
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS chat_session (
  session_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id    bigint NOT NULL REFERENCES app_user ON DELETE CASCADE,
  mode       varchar(16) NOT NULL DEFAULT 'chat' CHECK (mode IN ('chat','cowork','code')),
  title      text,
  starred    boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS chat_message (
  message_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  session_id bigint NOT NULL REFERENCES chat_session ON DELETE CASCADE,
  role       varchar(12) NOT NULL CHECK (role IN ('user','assistant')),
  content    text NOT NULL,
  guard_pass boolean,
  created_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS ix_chat_message_session ON chat_message(session_id, message_id);
CREATE INDEX IF NOT EXISTS ix_chat_session_user ON chat_session(user_id, updated_at DESC);
COMMENT ON TABLE chat_session IS '前台對話 session;RBAC owner=user_id;非預測資料、不得註冊為 dataset_catalog dataset(隔離命門)';
COMMENT ON TABLE chat_message IS '對話往來原文;owner=chat_session.user_id、access_scope=local_private;嚴禁進預測管線/當特徵(隔離命門)';
"""


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--migrate", action="store_true")
    a, _ = ap.parse_known_args()
    if not a.migrate:
        print(__doc__.split("執行指令矩陣:")[1])
        try:
            with db.connect() as conn, db.transaction(conn) as cur:
                cur.execute("SELECT to_regclass('chat_session'), to_regclass('chat_message')")
                cs, cm = cur.fetchone()
            print(f"  現況:chat_session={'已建' if cs else '未建'}  chat_message={'已建' if cm else '未建'}")
        except Exception as e:
            print(f"  (現況查詢失敗:{e})")
        return
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(DDL)
    print("✓ chat_session / chat_message 已建(冪等;owner CASCADE + mode/role CHECK + 非預測 COMMENT、隔離命門)")


if __name__ == "__main__":
    sys.exit(main())

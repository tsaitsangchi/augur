#!/usr/bin/env python
"""前台 user_settings schema — 每用戶介面偏好(chat-ui desktop parity 計畫 §3;#29b 設定住 DB)。

🎯 這支在做什麼(白話):user_settings 一人一列 JSONB——theme(light/dark/system)/font_size/
   default_tier/enter_to_send。前台 /api/settings GET/PUT 讀寫;owner 收窄(uid 出自 auth session)。

守 #6(冪等)· #12(DDL 單一住所)· #29b(偏好=資料住 DB 非 code)。

執行指令矩陣:
  python scripts/migrate_chat_ui_ddl.py           # 無參數:現況(唯讀)
  python scripts/migrate_chat_ui_ddl.py --run     # 冪等建表
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

DDL = """
CREATE TABLE IF NOT EXISTS user_settings (
  user_id bigint PRIMARY KEY,
  settings jsonb NOT NULL DEFAULT '{}',
  updated_at timestamptz NOT NULL DEFAULT now());
COMMENT ON TABLE user_settings IS '前台每用戶介面偏好(theme/font_size/default_tier/enter_to_send);owner 收窄';
"""


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    with db.connect() as conn:
        cur = conn.cursor()
        if args.run:
            cur.execute(DDL)
            conn.commit()
            print("✓ user_settings 就位(冪等)")
            return 0
        cur.execute("SELECT to_regclass('public.user_settings')")
        if cur.fetchone()[0]:
            cur.execute("SELECT count(*) FROM user_settings")
            print(f"user_settings:{cur.fetchone()[0]} 列")
        else:
            print("(未建;--run)")
    print(__doc__.split("執行指令矩陣:")[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())

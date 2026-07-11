#!/usr/bin/env python
"""admin 帳密同步 — .env AUGUR_ADMIN_USER/PASSWORD → app_user superuser 列(前後台單一帳密源)。

🎯 這支在做什麼(白話):用戶 directive 2026-07-11——**前台(chat :8090/機率 :8600)與後台(admin :8500)
   登入一律參考 .env 之 AUGUR_ADMIN_USER/AUGUR_ADMIN_PASSWORD**。三服務皆走 identity.authenticate
   (DB app_user)——本工具把 .env 帳密 upsert 成 app_user(pbkdf2 240k 雜湊落 DB、明文只住 .env,
   is_superuser=true)——改密碼=改 .env 重跑本工具,三服務即同步(admin 另有 env 後門雙路,同帳密)。
   #12:認證邏輯仍唯 identity 一家;本工具只做「.env→DB 列」同步,零第二套驗證。

守 #12(單一認證住所)· #5(DB 只存雜湊;明文限 .env,gitignored、綁 127.0.0.1 之既有取捨)· #6(冪等)· #29a。

執行指令矩陣:
  python scripts/sync_admin_user.py            # 無參數:現況(該帳號存在?superuser?;不印密碼)
  python scripts/sync_admin_user.py --run      # upsert(冪等;密碼以 .env 現值重設)
"""
import argparse
import os
import sys

import _bootstrap  # noqa: F401
from augur.core import db
from augur.knowledge import identity


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    user = os.environ.get("AUGUR_ADMIN_USER", "").strip()
    pw = os.environ.get("AUGUR_ADMIN_PASSWORD", "")
    if not user or not pw:
        sys.exit("✗ .env 缺 AUGUR_ADMIN_USER / AUGUR_ADMIN_PASSWORD")
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, is_superuser, is_active FROM app_user WHERE username=%s", (user,))
        row = cur.fetchone()
        if not args.run:
            print(__doc__.split("執行指令矩陣:")[1])
            print(f"現況:AUGUR_ADMIN_USER={user!r} → app_user "
                  + (f"存在(superuser={row[1]}, active={row[2]})" if row else "不存在(--run 建立)"))
            return 0
        ph = identity.hash_password(pw)
        if row:
            cur.execute("UPDATE app_user SET pw_hash=%s, is_superuser=true, is_active=true WHERE user_id=%s",
                        (ph, row[0]))
            print(f"✓ 更新 app_user {user!r}(密碼重設為 .env 現值;superuser/active=true)")
        else:
            cur.execute("INSERT INTO app_user (username, pw_hash, is_superuser, is_active) VALUES (%s,%s,true,true)",
                        (user, ph))
            print(f"✓ 建立 app_user {user!r}(superuser;pbkdf2 雜湊落 DB、明文只住 .env)")
        conn.commit()
    return 0


if __name__ == "__main__":
    sys.exit(main())

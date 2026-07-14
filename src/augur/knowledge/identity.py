"""RBAC 身分模組(P1)— 密碼雜湊 + 持久化 session（app_session）。後台/前台共用單一實作。

🎯 這支在做什麼(白話):pbkdf2 密碼雜湊(240k、標準庫零依賴)+ DB 持久化 session
   ——cookie 存明文 token、DB 只存 sha256(token)(外洩不直接得可用 token)。所有 verify_* 一律
   **fail-closed**:token 無效/過期/撤銷/帳號停用一律回 None/False,呼叫端無從放寬。authenticate 常數時間
   (無帳號也跑 dummy verify,抹平帳號列舉時間側信道)。
守 #5(密碼雜湊/session 安全、fail-closed)· #12(單一實作、後台+前台+CLI 三端 import)· #1(禁明文 token 落盤)。

執行指令矩陣(本檔=library;CLI 見 scripts/manage_rbac_user.py):
  python -c "from augur.knowledge.identity import hash_password; print(hash_password('x'))"

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.knowledge.identity              # 印用途+公開入口（唯讀）
  python -m augur.knowledge.identity --selftest   # 純紅綠自測（零 IO）
"""
from __future__ import annotations

import hashlib
import hmac
import secrets

from augur.core import db

_ITER = 240000                 # pbkdf2 迭代(≥ OWASP 210k 門檻)
SESSION_TTL_HOURS = 12


def hash_password(pw, salt=None):
    """回 'pbkdf2$<iter>$<salt>$<hash>'。salt 未給則隨機 16-byte。"""
    salt = salt or secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), _ITER).hex()
    return f"pbkdf2${_ITER}${salt}${h}"


def verify_password(pw, stored):
    """常數時間比對;未知前綴/格式壞一律 False(fail-closed、不 raise)。"""
    try:
        scheme, it, salt, h = (stored or "").split("$")
        if scheme != "pbkdf2":
            return False
        calc = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), int(it)).hex()
        return hmac.compare_digest(calc, h)
    except Exception:
        return False


def _sha256(token):
    return hashlib.sha256((token or "").encode()).hexdigest()


# 不存在帳號時比對用的 dummy hash(抹平時間側信道;永不 match 真密碼)
_DUMMY_HASH = "pbkdf2$%d$%s$%s" % (_ITER, "00" * 16, "0" * 64)


def authenticate(username, password):
    """回 {user_id, is_superuser} 或 None(fail-closed)。常數時間:無帳號也跑一次 verify。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT user_id, pw_hash, is_active, is_superuser FROM app_user "
                    "WHERE lower(username) = lower(%s)", (username,))
        row = cur.fetchone()
    ok = verify_password(password, row[1] if row else _DUMMY_HASH)
    if row and ok and row[2]:                      # row[2]=is_active
        return {"user_id": row[0], "is_superuser": row[3]}
    return None


def issue_session(user_id, client_note=None, ttl_hours=SESSION_TTL_HOURS):
    """發新 session:回明文 token(DB 只存 sha256)。登入成功一律發新 token(防 fixation)。"""
    token = secrets.token_urlsafe(32)
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(
            "INSERT INTO app_session (token_hash, user_id, expires_at, client_note) "
            "VALUES (%s, %s, now() + (%s * interval '1 hour'), %s)",
            (_sha256(token), user_id, int(ttl_hours), client_note))
    return token


def verify_session(token):
    """回 user_id 或 None。fail-closed 全 AND:revoked_at IS NULL AND expires_at>now() AND is_active。"""
    if not token:
        return None
    th = _sha256(token)
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute(
            "SELECT s.user_id FROM app_session s JOIN app_user u ON u.user_id = s.user_id "
            "WHERE s.token_hash = %s AND s.revoked_at IS NULL AND s.expires_at > now() AND u.is_active",
            (th,))
        row = cur.fetchone()
        if not row:
            return None
        cur.execute("UPDATE app_session SET last_seen_at = now() WHERE token_hash = %s", (th,))
        return row[0]


def revoke_session(token):
    """主動登出:撤銷單一 token。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("UPDATE app_session SET revoked_at = now() "
                    "WHERE token_hash = %s AND revoked_at IS NULL", (_sha256(token),))


def revoke_user_sessions(user_id):
    """停用/改密時撤銷該 user 全部有效 session(下一請求即失效)。"""
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("UPDATE app_session SET revoked_at = now() "
                    "WHERE user_id = %s AND revoked_at IS NULL", (user_id,))


def _selftest():
    """純紅綠自測(零 IO):固化密碼雜湊/驗證之核心不變式(fail-closed、常數時間比對)。"""
    ok = True
    def chk(name, cond):
        nonlocal ok; ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")
    salt = "ab" * 16
    stored = hash_password("secret", salt)
    scheme, it, s, h = stored.split("$")
    chk("hash 格式=pbkdf2$iter$salt$hash 四段", scheme == "pbkdf2" and int(it) == _ITER and s == salt)
    chk("salt 固定→hash 決定性可複現", hash_password("secret", salt) == stored)
    chk("verify 正確密碼 round-trip=True", verify_password("secret", stored) is True)
    chk("verify 錯密碼=False", verify_password("wrong", stored) is False)
    chk("verify 壞格式 fail-closed=False", verify_password("x", "not-a-hash") is False)
    chk("verify None/空 fail-closed=False", verify_password("x", None) is False and verify_password("x", "") is False)
    chk("verify 未知前綴 fail-closed=False", verify_password("x", f"bcrypt${_ITER}${salt}${h}") is False)
    chk("_DUMMY_HASH 永不 match 真密碼", verify_password("secret", _DUMMY_HASH) is False)
    chk("_sha256 決定性+64 hex", _sha256("tok") == _sha256("tok") and len(_sha256("tok")) == 64)
    chk("_sha256 None/空不 raise", isinstance(_sha256(None), str) and len(_sha256("")) == 64)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.knowledge.identity --selftest;免 DB 免 API)")

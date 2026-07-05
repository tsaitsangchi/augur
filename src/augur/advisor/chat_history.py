"""前台對話歷史持久化 — 只讀寫 chat_session/chat_message 兩表、owner 收窄、fail-closed。

🎯 這支在做什麼(白話):把前台對話存進 PostgreSQL(取代 localStorage)。create_session/append_message/
   rename/star/delete/list_sessions/load_messages;**所有讀寫一律以呼叫端傳入之 user_id(由端點
   `identity.verify_session` 解出、絕不信 client 帶入)收窄**——`WHERE user_id=%s`;他人 session
   一律 fail-closed 不可讀/不可寫(IDOR/OWASP A01 防護)。零觸預測/知識/哲學表。
   對話原文＝真實往來、owner＝user_id、access_scope 語意＝local_private,**嚴禁進預測管線/當特徵(隔離命門)**。
守 #1(存真實往來、非 AI 生成入知識庫)· #5(owner 授權 fail-closed、參數化)·
   隔離不變式(住 augur.advisor＝FORBIDDEN 前綴、預測 7 package 零 import;test_philosophy_isolation 正向釘死)·
   憲章 v1.29 RBAC owner 收窄 · 計畫 §7.1(三鏡對抗審查定稿)。
"""
from __future__ import annotations

from augur.core import db

_MODES = ("chat", "cowork", "code")


def create_session(user_id, mode="chat", title=None):
    """建 session、回 session_id;user_id 由端點 verify_session 解出。查無/錯 → None(fail-closed)。"""
    if user_id is None:
        return None
    if mode not in _MODES:
        mode = "chat"
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("INSERT INTO chat_session (user_id, mode, title) VALUES (%s,%s,%s) RETURNING session_id",
                        (user_id, mode, title))
            return cur.fetchone()[0]
    except Exception:
        return None


def append_message(session_id, user_id, role, content, guard_pass=None):
    """寫一則訊息 — **先驗 session 屬 user_id**(絕不寫入他人 session)。回 message_id 或 None。"""
    if user_id is None or role not in ("user", "assistant"):
        return None
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("SELECT 1 FROM chat_session WHERE session_id=%s AND user_id=%s", (session_id, user_id))
            if cur.fetchone() is None:
                return None                      # 非本人 session → 不寫(IDOR fail-closed)
            cur.execute("INSERT INTO chat_message (session_id, role, content, guard_pass) "
                        "VALUES (%s,%s,%s,%s) RETURNING message_id", (session_id, role, content, guard_pass))
            mid = cur.fetchone()[0]
            cur.execute("UPDATE chat_session SET updated_at=now() WHERE session_id=%s AND user_id=%s",
                        (session_id, user_id))
            return mid
    except Exception:
        return None


def rename_session(session_id, user_id, title):
    if user_id is None:
        return False
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("UPDATE chat_session SET title=%s, updated_at=now() WHERE session_id=%s AND user_id=%s",
                        (title, session_id, user_id))
            return cur.rowcount > 0
    except Exception:
        return False


def set_starred(session_id, user_id, starred):
    if user_id is None:
        return False
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("UPDATE chat_session SET starred=%s WHERE session_id=%s AND user_id=%s",
                        (bool(starred), session_id, user_id))
            return cur.rowcount > 0
    except Exception:
        return False


def delete_session(session_id, user_id):
    if user_id is None:
        return False
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("DELETE FROM chat_session WHERE session_id=%s AND user_id=%s", (session_id, user_id))
            return cur.rowcount > 0
    except Exception:
        return False


def list_sessions(user_id, mode=None, limit=200):
    """回該 user 之 session 列(新→舊);一律 WHERE user_id=%s;查無/錯 → [](fail-closed、不吐他人)。"""
    if user_id is None:
        return []
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            base = ("SELECT session_id, mode, title, starred, "
                    "extract(epoch from updated_at)*1000 FROM chat_session WHERE user_id=%s ")
            if mode:
                cur.execute(base + "AND mode=%s ORDER BY updated_at DESC LIMIT %s", (user_id, mode, limit))
            else:
                cur.execute(base + "ORDER BY updated_at DESC LIMIT %s", (user_id, limit))
            return [{"id": r[0], "mode": r[1], "title": r[2], "starred": r[3], "ts": int(r[4])}
                    for r in cur.fetchall()]
    except Exception:
        return []


def load_messages(session_id, user_id):
    """回某 session 訊息(**需屬 user_id**;JOIN chat_session 驗 owner,非 owner → [] fail-closed、IDOR 防護)。"""
    if user_id is None:
        return []
    try:
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("SELECT m.role, m.content FROM chat_message m "
                        "JOIN chat_session s ON s.session_id = m.session_id "
                        "WHERE m.session_id=%s AND s.user_id=%s ORDER BY m.message_id",
                        (session_id, user_id))
            return [{"role": r[0], "content": r[1]} for r in cur.fetchall()]
    except Exception:
        return []

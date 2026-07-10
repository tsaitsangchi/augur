"""審議帳本 — deliberation_session/claim 之 CRUD + claim 格式閘 + 報告(P3 模組化;模式 10)。

🎯 這支在做什麼(白話):審議的持久層(resume/追溯之所在)——開 session、經 anchors L1-L5 正規化後
   插 claim(provenance 記 model/lens/fast_path/lint)、收 session、印報告。**不含裁決邏輯**(在
   verifiers.verify_claim)、**不含 LLM**(在 lens/engine)——純帳本(#12 職責單一)。

守 #10(逐 claim 落庫可追溯)· #12(帳本 CRUD 單一住所)· #15(claim_text 為真實 LLM 輸出、anchor 為確定性正規化後)。
"""
import json
import uuid

from augur.core import db
from augur.deliberation.anchors import fast_anchor, normalize_anchor, verifier_lint

_ICON = {"confirmed": "✓", "refuted": "✗", "escalated": "⚠", "pending": "…", "undecidable": "?"}


def new_session_id():
    return f"delib_{uuid.uuid4().hex[:10]}"


def open_session(cur, sid, topic, target, model):
    cur.execute("INSERT INTO deliberation_session (session_id, topic, draft_path, model_tag) "
                "VALUES (%s,%s,%s,%s)", (sid, topic, target, model))


def insert_claim(cur, sid, claim, lens, model, target):
    """插一條 claim(先過 anchors L2/L3 正規化 + L4/L5 快路 + L2 lint);回 claim_id。
    快路命中 → 確定性錨凌駕 LLM 錨(provenance 記 fast_path);lint 改派記 provenance。"""
    ver = claim["assigned_verifier"]
    anc = normalize_anchor(claim["anchor"], ver, target)
    ver, anc, lint = verifier_lint(ver, anc, target)
    prov = {"model": model, "lens": lens}
    fp = fast_anchor(claim["claim_text"], target)
    if fp:
        ver, anc = fp
        prov["fast_path"] = True
    if lint:
        prov["lint"] = lint
    cur.execute(
        "INSERT INTO deliberation_claim (session_id,perspective,category,claim_text,anchor,"
        "assigned_verifier,provenance) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING claim_id",
        (sid, lens, claim["category"], claim["claim_text"], anc or "(空)", ver, json.dumps(prov)))
    return cur.fetchone()[0]


def close_session(cur, sid, tally):
    cur.execute("UPDATE deliberation_session SET status='closed', coverage=%s WHERE session_id=%s",
                (json.dumps(tally), sid))


def report(sid):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT topic, model_tag, status, coverage FROM deliberation_session WHERE session_id=%s", (sid,))
        s = cur.fetchone()
        if not s:
            print(f"✗ session {sid} 不存在"); return
        print(f"═══ 審議報告 {sid} ═══\n題目:{s[0]} | model={s[1]} | {s[2]} | {s[3]}")
        cur.execute("""SELECT c.claim_id, c.status, c.claim_text, c.assigned_verifier, c.anchor,
                              (SELECT v.evidence FROM deliberation_verdict v WHERE v.claim_id=c.claim_id
                               ORDER BY v.ran_at DESC LIMIT 1)
                       FROM deliberation_claim c WHERE c.session_id=%s ORDER BY c.claim_id""", (sid,))
        for cid, st, txt, ver, anc, ev in cur.fetchall():
            print(f"  {_ICON.get(st, '?')} [{st}] {txt[:70]}")
            print(f"      verifier={ver} anchor={anc[:70]}")
            if ev:
                print(f"      證據:{ev[:110]}")


def recent(limit=5):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT session_id, topic, status, coverage, created_at::date FROM deliberation_session "
                    "ORDER BY created_at DESC LIMIT %s", (limit,))
        return cur.fetchall()

"""審議帳本 — deliberation_session/claim 之 CRUD + claim 格式閘 + 報告(P3 模組化;模式 10)。

🎯 這支在做什麼(白話):審議的持久層(resume/追溯之所在)——開 session、經 anchors L1-L5 正規化後
   插 claim(provenance 記 model/lens/fast_path/lint)、收 session、印報告。**不含裁決邏輯**(在
   verifiers.verify_claim)、**不含 LLM**(在 lens/engine)——純帳本(#12 職責單一)。

守 #10(逐 claim 落庫可追溯)· #12(帳本 CRUD 單一住所)· #15(claim_text 為真實 LLM 輸出、anchor 為確定性正規化後)。
"""
import json
import uuid

from augur.core import db
from augur.deliberation import engine_config
from augur.deliberation.anchors import fast_anchor, normalize_anchor, semantic_bound_of, verifier_lint

_ICON = {"confirmed": "✓", "refuted": "✗", "escalated": "⚠", "pending": "…", "undecidable": "?"}


def new_session_id():
    return f"delib_{uuid.uuid4().hex[:10]}"


def open_session(cur, sid, topic, target, model):
    cur.execute("INSERT INTO deliberation_session (session_id, topic, draft_path, model_tag) "
                "VALUES (%s,%s,%s,%s)", (sid, topic, target, model))


def insert_claim(cur, sid, claim, lens, model, target):
    """插一條 claim(anchors L2/L3 正規化 + 具名規則快路 + L2 lint + B1 semantic_bound);回 claim_id。
    B3 三閘:①human_claude 指派**一律跳快路**(escalate 意圖不可劫持);②rules 自 DB config(缺=全關
    fail-safe);③快路命中之 db_query/info_schema 錨,表名再經 information_schema 實存驗證(caller 端
    參數驗證);provenance.fast_path 留痕 {rule_id, original_verifier, original_anchor}(audit)。"""
    from augur.deliberation import redlines
    ver = claim["assigned_verifier"]
    anc = normalize_anchor(claim["anchor"], ver, target)
    ver, anc, lint = verifier_lint(ver, anc, target)
    prov = {"model": model, "lens": lens}
    rl = redlines.consult(cur, claim["claim_text"], anc, ver)     # D6:redline 在快路之前、豁免不了
    if rl:
        prov["redline"] = rl
        ver = "human_claude"                                      # 治權觸線=強制人裁(#19/#26)
    if ver != "human_claude":                                     # B3①:不覆寫人裁
        rules, _sha = engine_config.load_rules(cur)               # B3②:rules SSOT=DB
        fp = fast_anchor(claim["claim_text"], target, rules)
        if fp and _fast_anchor_params_ok(cur, fp):                # B3③:參數實存驗證
            prov["fast_path"] = {"rule_id": fp[2], "original_verifier": ver, "original_anchor": anc}
            ver, anc = fp[0], fp[1]
    if lint:
        prov["lint"] = lint
    bound = semantic_bound_of(claim["claim_text"], ver, anc, target)   # B1 導出欄
    cur.execute(
        "INSERT INTO deliberation_claim (session_id,perspective,category,claim_text,anchor,"
        "assigned_verifier,provenance,semantic_bound) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING claim_id",
        (sid, lens, claim["category"], claim["claim_text"], anc or "(空)", ver, json.dumps(prov), bound))
    return cur.fetchone()[0]


def _fast_anchor_params_ok(cur, fp):
    """B3 caller 端參數驗證:db_query/info_schema 之表名須 information_schema 實存(防臆造表名鑄錨);
    file_grep/pytest 樣式已由規則 regex 白名單約束。"""
    ver, anc, _rid = fp
    if ver == "information_schema":
        t = anc.split(".")[0]
    elif ver == "db_query":
        import re as _re
        m = _re.search(r"FROM\s+([a-z_][a-z0-9_]*)", anc)
        if not m:
            return False
        t = m.group(1)
    else:
        return True
    cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name=%s", (t,))
    return bool(cur.fetchone()[0])


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
                              COALESCE(c.semantic_bound, false),
                              (SELECT v.evidence FROM deliberation_verdict v WHERE v.claim_id=c.claim_id
                               ORDER BY v.ran_at DESC LIMIT 1)
                       FROM deliberation_claim c WHERE c.session_id=%s ORDER BY c.claim_id""", (sid,))
        for cid, st, txt, ver, anc, bound, ev in cur.fetchall():
            # B1 二級制:confirmed·bound=claim 文字可直接引用;confirmed·anchor-only=以錨+證據為主體、
            # 文字降格標註(confirmed 語意=「錨成立」,不为未綁定文字背書)
            if st == "confirmed" and bound:
                print(f"  ✓✓ [confirmed·bound] {txt[:70]}")
            elif st == "confirmed":
                print(f"  ✓ [confirmed·anchor-only] anchor={anc[:60]}")
                print(f"      (語意未綁定,僅錨成立)claim:{txt[:60]}")
            else:
                print(f"  {_ICON.get(st, '?')} [{st}] {txt[:70]}")
            print(f"      verifier={ver} anchor={anc[:70]}")
            if ev:
                print(f"      證據:{ev[:110]}")


def recent(limit=5):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT session_id, topic, status, coverage, created_at::date FROM deliberation_session "
                    "ORDER BY created_at DESC LIMIT %s", (limit,))
        return cur.fetchall()


# ── 模式 10:resume-safe run/task 帳本(§3.1;GATE/D3/D4 承載)──────────────────
def create_run(cur, idempotency_key, plan):
    """建 run(冪等 #6:同 idempotency_key 重送=回既有 run_id、不重建);tasks 逐項 pending。"""
    cur.execute("SELECT run_id FROM deliberation_run WHERE idempotency_key=%s", (idempotency_key,))
    row = cur.fetchone()
    if row:
        return row[0]
    rid = f"dlrun_{uuid.uuid4().hex[:12]}"
    cur.execute("INSERT INTO deliberation_run (run_id, idempotency_key, plan) VALUES (%s,%s,%s)",
                (rid, idempotency_key, json.dumps(plan, ensure_ascii=False)))
    for seq, item in enumerate(plan):
        cur.execute("INSERT INTO deliberation_task (run_id, seq, payload) VALUES (%s,%s,%s)",
                    (rid, seq, json.dumps(item, ensure_ascii=False)))
    return rid


def resume_reset(cur, run_id, max_attempt=3):
    """resume 語意(§3.1):running(kill 殘留)→ 重置 pending、attempt+1;failed(attempt<max)→ pending。
    回重置數。"""
    cur.execute("UPDATE deliberation_task SET status='pending', attempt=attempt+1, updated_at=now() "
                "WHERE run_id=%s AND status='running'", (run_id,))
    n = cur.rowcount
    cur.execute("UPDATE deliberation_task SET status='pending', updated_at=now() "
                "WHERE run_id=%s AND status='failed' AND attempt < %s", (run_id, max_attempt))
    return n + cur.rowcount


def next_task(cur, run_id):
    """取工(單機單工):最小 seq 之 pending → 標 running;回 (task_id, seq, payload) 或 None。"""
    cur.execute("SELECT task_id, seq, payload FROM deliberation_task WHERE run_id=%s AND status='pending' "
                "ORDER BY seq LIMIT 1 FOR UPDATE", (run_id,))
    row = cur.fetchone()
    if not row:
        return None
    cur.execute("UPDATE deliberation_task SET status='running', updated_at=now() WHERE task_id=%s", (row[0],))
    return row


def mark_task(cur, task_id, status, session_id=None):
    cur.execute("UPDATE deliberation_task SET status=%s, session_id=COALESCE(%s, session_id), "
                "updated_at=now() WHERE task_id=%s", (status, session_id, task_id))


def finish_run(cur, run_id):
    """全 task 終態後收 run:任一 failed(attempt 用盡)→ failed,否則 completed。回 status。"""
    cur.execute("SELECT count(*) FILTER (WHERE status!='done'), count(*) FROM deliberation_task WHERE run_id=%s",
                (run_id,))
    n_bad, n_all = cur.fetchone()
    st = "completed" if n_bad == 0 and n_all > 0 else "failed"
    cur.execute("UPDATE deliberation_run SET status=%s, finished_at=now() WHERE run_id=%s", (st, run_id))
    return st

"""四真 oracle 確定性 verifier — 審議引擎唯一合法的 confirmed 來源(機械鎖落地)。

🎯 這支在做什麼(白話):qwen 提出的每個 claim 都指定一個 verifier;本模組用**確定性工具**
   (查 DB/掃檔/跑隔離稽核)裁決 confirmed/refuted/undecidable——LLM 的意見永遠不算證據,
   工具輸出才算(#15)。封閉集=前身計畫已裁決之 4 真 oracle(deliberation_claim CHECK 同錨):

   verifier            anchor 契約(確定性、可重跑)                        裁決語意
   ─────────────────  ─────────────────────────────────────────────  ─────────────────────
   information_schema  "table" 或 "table.column"                       存在=confirmed
   import_isolation    "check_isolation"(正典式;claim 須以正向句式表述)  violations==[]=confirmed
   file_grep           "<repo相對路徑>::<regex>"                        有匹配=confirmed
   db_query            "<單一SELECT> => <op> <數值>"(op∈==,!=,>,>=,<,<=)  單標量比較成立=confirmed

   安全:db_query 僅准單條 SELECT(禁寫入詞、READ ONLY 交易、statement_timeout);
   file_grep 路徑鎖 repo 內(realpath 圍欄、拒逃逸)。anchor 不合契約=undecidable(fail-closed,
   寧可 escalate 不硬猜)。`verify_claim` 是全系統**唯一**把 claim 寫成 confirmed 的地方。

守 #15(工具實證、LLM 意見零證據力)· #5(唯讀白名單沙箱)· #6(裁決冪等可重跑)· #12(封閉集
   單一住所=本檔+DDL CHECK 同錨)。SSOT=本地審議引擎計畫 v1 + 前身 augur_deliberation_orchestrator_plan_20260709.md。
"""
import json
import re
from pathlib import Path

from augur.core import db

REPO_ROOT = Path(__file__).resolve().parents[3]
ORACLES = ("information_schema", "import_isolation", "file_grep", "db_query")
_DB_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|grant|revoke|truncate|copy|call|do|vacuum|set)\b", re.I)
_CMP = {"==": lambda a, b: a == b, "!=": lambda a, b: a != b, ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b, "<": lambda a, b: a < b, "<=": lambda a, b: a <= b}


def _v_information_schema(anchor):
    """anchor='table' 或 'table.column' → 存在性。"""
    parts = anchor.strip().split(".")
    if not (1 <= len(parts) <= 2) or not all(re.fullmatch(r"[a-z_][a-z0-9_]*", p) for p in parts):
        return "undecidable", f"anchor 不合契約(需 table 或 table.column):{anchor!r}"
    with db.connect() as conn, db.transaction(conn) as cur:
        if len(parts) == 1:
            cur.execute("SELECT count(*) FROM information_schema.tables "
                        "WHERE table_schema='public' AND table_name=%s", (parts[0],))
        else:
            cur.execute("SELECT count(*) FROM information_schema.columns "
                        "WHERE table_schema='public' AND table_name=%s AND column_name=%s", tuple(parts))
        n = cur.fetchone()[0]
    return ("confirmed" if n else "refuted"), f"information_schema 命中 {n} 列(anchor={anchor})"


def _v_import_isolation(anchor):
    """anchor='check_isolation'(正典式);claim 須為正向句式「隔離不變式成立」。"""
    if anchor.strip() != "check_isolation":
        return "undecidable", f"anchor 不合契約(正典式='check_isolation'):{anchor!r}"
    from augur.audit.import_isolation import check_isolation
    v = check_isolation()
    return ("confirmed" if v == [] else "refuted"), f"check_isolation() == {v!r}"


def _v_file_grep(anchor):
    """anchor='<repo相對路徑>::<regex>' → 檔內有匹配。路徑鎖 repo 內(realpath 圍欄)。"""
    path_s, sep, pat = anchor.partition("::")
    if not sep or not pat:
        return "undecidable", f"anchor 不合契約(需 path::regex):{anchor!r}"
    p = (REPO_ROOT / path_s.strip()).resolve()
    if not str(p).startswith(str(REPO_ROOT)) or not p.is_file():
        return "undecidable", f"路徑不在 repo 內或非檔案:{path_s!r}"
    try:
        rx = re.compile(pat)
    except re.error as e:
        return "undecidable", f"regex 不合法:{e}"
    hits = [(i, ln.rstrip()[:120]) for i, ln in enumerate(p.read_text(encoding="utf-8",
            errors="replace").splitlines(), 1) if rx.search(ln)]
    if hits:
        ev = "; ".join(f"{path_s}:{i}: {t}" for i, t in hits[:3])
        return "confirmed", f"{len(hits)} 行匹配 → {ev}"
    return "refuted", f"{path_s} 無行匹配 /{pat}/"


def _v_db_query(anchor):
    """anchor='<SELECT…> => <op> <數值>' → READ ONLY 單標量比較。"""
    m = re.match(r"^(.*?)\s*=>\s*(==|!=|>=|<=|>|<)\s*(-?\d+(?:\.\d+)?)\s*$", anchor.strip(), re.S)
    if not m:
        return "undecidable", f"anchor 不合契約(需 'SELECT… => op 數值'):{anchor[:80]!r}"
    sql, op, val = m.group(1).strip().rstrip(";"), m.group(2), float(m.group(3))
    if not sql.lower().startswith("select") or ";" in sql or _DB_FORBIDDEN.search(sql):
        return "undecidable", f"SQL 不過唯讀白名單(僅單條 SELECT):{sql[:80]!r}"
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("BEGIN TRANSACTION READ ONLY")
        try:
            cur.execute("SET LOCAL statement_timeout = '30s'")
            cur.execute(sql)
            row = cur.fetchone()
            if row is None or len(row) != 1 or row[0] is None:
                return "undecidable", f"查詢未回單一標量:{row!r}"
            actual = float(row[0])
        except Exception as e:
            return "undecidable", f"查詢失敗:{type(e).__name__}: {str(e)[:120]}"
        finally:
            cur.execute("ROLLBACK")
    ok = _CMP[op](actual, val)
    return ("confirmed" if ok else "refuted"), f"實際值 {actual} {op} {val} → {ok}(sql={sql[:100]})"


_DISPATCH = {"information_schema": _v_information_schema, "import_isolation": _v_import_isolation,
             "file_grep": _v_file_grep, "db_query": _v_db_query}


def run_verifier(verifier, anchor):
    """跑單一 oracle(無副作用)。回 (verdict∈{confirmed,refuted,undecidable}, evidence:str)。"""
    if verifier not in _DISPATCH:
        return "undecidable", f"非 4 真 oracle(封閉集 {ORACLES}):{verifier!r}"
    return _DISPATCH[verifier](anchor)


def verify_claim(claim_id):
    """裁決一個 claim:跑其 assigned_verifier → 落 verdict(is_deterministic=true)→ 更新 claim.status。
    **全系統唯一把 status 寫成 'confirmed' 的地方**(機械鎖);undecidable → status='escalated'+開
    escalation(reason='undecidable',人裁);verifier∈{human_claude,none} → 直接 escalate(reason=
    'no_oracle'/'verifier_none'),LLM/本模組皆不得裁。冪等:重跑=追加新 verdict、status 收斂一致。"""
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT assigned_verifier, anchor, category FROM deliberation_claim WHERE claim_id=%s",
                    (claim_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"claim {claim_id} 不存在")
        verifier, anchor, category = row
        if verifier in ("human_claude", "none"):
            reason = "no_oracle" if verifier == "human_claude" else "verifier_none"
            cur.execute("INSERT INTO deliberation_escalation (claim_id, reason, payload) VALUES (%s,%s,%s)",
                        (claim_id, reason, json.dumps({"anchor": anchor, "category": category})))
            cur.execute("UPDATE deliberation_claim SET status='escalated' WHERE claim_id=%s", (claim_id,))
            conn.commit()
            return {"claim_id": claim_id, "verdict": None, "status": "escalated", "reason": reason}
        verdict, evidence = run_verifier(verifier, anchor)
        cur.execute("INSERT INTO deliberation_verdict (claim_id, verifier, verdict, evidence, is_deterministic) "
                    "VALUES (%s,%s,%s,%s,true) RETURNING verdict_id",
                    (claim_id, verifier, verdict, evidence if verdict != "undecidable" else evidence))
        vid = cur.fetchone()[0]
        if verdict == "undecidable":
            cur.execute("INSERT INTO deliberation_escalation (claim_id, reason, payload) VALUES (%s,%s,%s)",
                        (claim_id, "undecidable", json.dumps({"anchor": anchor, "evidence": evidence})))
            new_status = "escalated"
        else:
            new_status = verdict
        cur.execute("UPDATE deliberation_claim SET status=%s WHERE claim_id=%s", (new_status, claim_id))
        conn.commit()
    return {"claim_id": claim_id, "verdict": verdict, "status": new_status,
            "verdict_id": vid, "evidence": evidence}

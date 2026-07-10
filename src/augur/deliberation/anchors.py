"""claim 錨點確定性補強層 — L1-L5「把 LLM 從可機械化處移除」之單一住所(P3 模組化;行為逐字沿用 MVP)。

🎯 這支在做什麼(白話):qwen 提的 claim 常把錨點寫歪(前綴/方向/表名語序);本模組用**確定性規則**
   修正或直接產出錨點,LLM 只負責它做得到的(提出「大概要驗什麼」)。五層(2026-07-10 逐場實測而生):
   L1 schema_grounding=題目詞→information_schema 實查→注入真表清單(防臆造表名);
   L2 verifier_lint=查無表+程式符號→改派 file_grep(防假 refuted);
   L3 路徑誤蓋修(anchor 含 '/' 不補 target 前綴);
   L4 宣稱快路=可機械解析→零 LLM 直接產錨;L5 條件式快路=「T 表中 C 欄=V 的列數≥N」→ WHERE 錨。
   契約本體(verifiers.py)維持嚴格;本層只做零資訊損失之正規化/補全。

守 #12(L1-L5 單一住所=本檔;deliberate/benchmark 皆 import 此)· #15(確定性、不臆造)。
"""
import re

from augur.core import db

ORACLES = ("information_schema", "import_isolation", "file_grep", "db_query")

CLAIM_SCHEMA = {
    "type": "object",
    "properties": {"claims": {"type": "array", "items": {"type": "object", "properties": {
        "category": {"type": "string", "enum": ["schema", "program", "isolation", "doctrine",
                                                 "antileakage", "truesign", "coverage", "other"]},
        "claim_text": {"type": "string"},
        "anchor": {"type": "string"},
        "assigned_verifier": {"type": "string", "enum": list(ORACLES) + ["human_claude"]},
    }, "required": ["category", "claim_text", "anchor", "assigned_verifier"]}}},
    "required": ["claims"],
}


def normalize_anchor(anchor, verifier, target=None):
    """L2/L3 正規化:剝 'verifier名:' 前綴;file_grep 無 '::' 且有 target 且錨不含 '/' → 補 target::。"""
    a = (anchor or "").strip()
    prefix = verifier + ":"
    if a.lower().startswith(prefix.lower()):
        a = a[len(prefix):].strip()
    if verifier == "file_grep" and "::" not in a and target and "/" not in a:
        a = f"{target}::{a}"
    return a


def schema_grounding(topic):
    """L1:題目 snake_case 詞 → information_schema LIKE 實查 → 注入真表清單(確定性、零臆造)。"""
    tokens = {t for t in re.findall(r"[a-z][a-z0-9_]{3,}", topic.lower())}
    if not tokens:
        return ""
    hits = set()
    with db.connect() as conn, db.transaction(conn) as cur:
        for t in list(tokens)[:12]:
            cur.execute("SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema='public' AND table_name LIKE %s LIMIT 6", (f"%{t}%",))
            hits.update(r[0] for r in cur.fetchall())
    if not hits:
        return ""
    return ("\n[真實存在的相關資料表(逐字使用、勿臆造/縮寫表名):" + ", ".join(sorted(hits)[:20]) + "]")


def fast_anchor(claim_text, target=None):
    """L4/L5:可機械解析之宣稱直接產錨(零 LLM;確定性凌駕生成)。回 (verifier, anchor) 或 None。
    L5 條件式(表名在「表」前=中文語序;值可含 .-):「T 表中 C 欄等於 V 的列數 ≥/≤ N」→ WHERE 錨。"""
    _GE = r"(?:至少有?|不少於|>=|≥|不低於)"
    _LE = r"(?:至多|不超過|<=|≤|不高於)"
    for _cmp, _op in ((_GE, ">="), (_LE, "<=")):
        m = re.search(r"([a-z_][a-z0-9_]*)\s*表\s*(?:中|裡)?\s*(?:的)?\s*"
                      r"([a-z_][a-z0-9_]*)\s*欄?\s*(?:等於|=|為|是)\s*([a-z0-9_.-]+)\s*"
                      r"(?:的)?\s*列數?\s*" + _cmp + r"\s*([0-9,]+)", claim_text)
        if m:
            t, c, v, n = m.groups()
            return "db_query", f"SELECT count(*) FROM {t} WHERE {c}='{v}' => {_op} {n.replace(',', '')}"
    # L4 無條件量:「表 T 至少/至多 N 列」
    m = re.search(r"表\s*([a-z_][a-z0-9_]*)\s*(?:至少有?|不少於|>=?)\s*([0-9,]+)\s*列", claim_text)
    if m:
        return "db_query", f"SELECT count(*) FROM {m.group(1)} => >= {m.group(2).replace(',', '')}"
    m = re.search(r"表\s*([a-z_][a-z0-9_]*)\s*(?:至多|不超過|<=?)\s*([0-9,]+)\s*列", claim_text)
    if m:
        return "db_query", f"SELECT count(*) FROM {m.group(1)} => <= {m.group(2).replace(',', '')}"
    m = re.search(r"(?:資料)?表\s*([a-z_][a-z0-9_]*)\s*存在", claim_text)
    if m:
        return "information_schema", m.group(1)
    m = re.search(r"檔案\s*([\w./-]+\.(?:py|md|json|sh))\s*.{0,6}含.{0,4}字串?\s*[「\"']([^」\"']+)[」\"']", claim_text)
    if m:
        return "file_grep", f"{m.group(1)}::{re.escape(m.group(2))}"
    if target:
        m = re.search(r"含.{0,4}字串?\s*[「\"']([^」\"']+)[」\"']", claim_text)
        if m:
            return "file_grep", f"{target}::{re.escape(m.group(1))}"
    return None


def verifier_lint(verifier, anchor, target):
    """L2:information_schema 錨查無表、但錨形如程式符號且有 target → 改派 file_grep。回 (v, a, note)。"""
    if verifier != "information_schema" or not target:
        return verifier, anchor, None
    parts = anchor.strip().split(".")
    if not all(re.fullmatch(r"[a-z_][a-z0-9_]*", p or "") for p in parts):
        return verifier, anchor, None
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name=%s",
                    (parts[0],))
        if cur.fetchone()[0]:
            return verifier, anchor, None
    return "file_grep", f"{target}::{parts[0]}", f"lint:information_schema 查無表 {parts[0]!r}→改派 file_grep"

"""claim 錨點確定性補強層 — L1-L5「把 LLM 從可機械化處移除」之單一住所(P3 模組化;行為逐字沿用 MVP)。

🎯 這支在做什麼(白話):qwen 提的 claim 常把錨點寫歪(前綴/方向/表名語序);本模組用**確定性規則**
   修正或直接產出錨點,LLM 只負責它做得到的(提出「大概要驗什麼」)。五層(2026-07-10 逐場實測而生):
   L1 schema_grounding=題目詞→information_schema 實查→注入真表清單(防臆造表名);
   L2 verifier_lint=查無表+程式符號→改派 file_grep(防假 refuted);
   L3 路徑誤蓋修(anchor 含 '/' 不補 target 前綴);
   L4 宣稱快路=可機械解析→零 LLM 直接產錨;L5 條件式快路=「T 表中 C 欄=V 的列數≥N」→ WHERE 錨。
   契約本體(verifiers.py)維持嚴格;本層只做零資訊損失之正規化/補全。

守 #12(L1-L5 單一住所=本檔;deliberate/benchmark 皆 import 此)· #15(確定性、不臆造)。

自測（本檔=library #18；免 DB 免 API 可個別驗證）：
  python -m augur.deliberation.anchors              # 印用途+公開入口（唯讀）
  python -m augur.deliberation.anchors --selftest   # 純紅綠自測（零 IO）
"""
import re

from augur.core import db
from augur.deliberation.verifiers import ORACLES   # #12:oracle 封閉集單一住所=verifiers(含 pytest)

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


# B3(補完計畫 §2.3):快路=具名規則封閉集;RULES_ALL 僅供 B1 導出比對(只比對、不執行,無注入面);
# 生產 rules SSOT=DB deliberation_engine_config(#29b),L6_pytest 預設關(執行任意測試節點=最大攻擊面)。
RULES_ALL = {"L4_db_query": True, "L4_information_schema": True, "L5_file_grep": True,
             "L6_pytest": True, "L6_isolation": True}


def fast_anchor(claim_text, target=None, rules=None):
    """具名規則快路(B3 規則化):可機械解析之宣稱 → 樣板構錨(參數經嚴格 regex 抽取,**不接受整段
    SQL/節點原樣入錨**)。回 (verifier, anchor, rule_id) 或 None。rules=None → RULES_ALL(導出比對用;
    生產 caller 一律傳 DB config)。"""
    r = RULES_ALL if rules is None else rules
    if r.get("L4_db_query"):
        _GE = r"(?:至少有?|不少於|>=|≥|不低於)"
        _LE = r"(?:至多|不超過|<=|≤|不高於)"
        # L5 條件式(表名在「表」前=中文語序;值可含 .-)
        for _cmp, _op in ((_GE, ">="), (_LE, "<=")):
            m = re.search(r"([a-z_][a-z0-9_]*)\s*表\s*(?:中|裡)?\s*(?:的)?\s*"
                          r"([a-z_][a-z0-9_]*)\s*欄?\s*(?:等於|=|為|是)\s*([a-z0-9_.-]+)\s*"
                          r"(?:的)?\s*列數?\s*" + _cmp + r"\s*([0-9,]+)", claim_text)
            if m:
                t, c, v, n = m.groups()
                return ("db_query", f"SELECT count(*) FROM {t} WHERE {c}='{v}' => {_op} {n.replace(',', '')}",
                        "L4_db_query")
        m = re.search(r"表\s*([a-z_][a-z0-9_]*)\s*(?:至少有?|不少於|>=?)\s*([0-9,]+)\s*列", claim_text)
        if m:
            return "db_query", f"SELECT count(*) FROM {m.group(1)} => >= {m.group(2).replace(',', '')}", "L4_db_query"
        m = re.search(r"表\s*([a-z_][a-z0-9_]*)\s*(?:至多|不超過|<=?)\s*([0-9,]+)\s*列", claim_text)
        if m:
            return "db_query", f"SELECT count(*) FROM {m.group(1)} => <= {m.group(2).replace(',', '')}", "L4_db_query"
    if r.get("L4_information_schema"):
        m = re.search(r"(?:資料)?表\s*([a-z_][a-z0-9_]*)\s*存在", claim_text)
        if m:
            return "information_schema", m.group(1), "L4_information_schema"
    if r.get("L6_pytest"):
        # pytest node 僅 tests/ 白名單樣式(嚴格 charset;4b 對測試題不自選 pytest → 確定性路由)
        m = re.search(r"(tests/[\w./-]+\.py(?:::[\w\[\]-]+)?)", claim_text)
        if m and ("pytest" in claim_text or "測試" in claim_text or "通過" in claim_text):
            return "pytest", m.group(1), "L6_pytest"
    if r.get("L6_isolation"):
        # 固定錨 'check_isolation'(零參數=零注入面),故預設開
        m = re.search(r"check_isolation|隔離不變式(?:成立|通過|為真)", claim_text)
        if m:
            return "import_isolation", "check_isolation", "L6_isolation"
    if r.get("L5_file_grep"):
        m = re.search(r"檔案\s*([\w./-]+\.(?:py|md|json|sh))\s*.{0,6}含.{0,4}字串?\s*[「\"']([^」\"']+)[」\"']",
                      claim_text)
        if m and ".." not in m.group(1):
            return "file_grep", f"{m.group(1)}::{re.escape(m.group(2))}", "L5_file_grep"
        if target:
            m = re.search(r"含.{0,4}字串?\s*[「\"']([^」\"']+)[」\"']", claim_text)
            if m:
                return "file_grep", f"{target}::{re.escape(m.group(1))}", "L5_file_grep"
    return None


def binding_check(claim_text, verifier, anchor, target=None):
    """B1 語意綁定反抽取:claim_text 內的數字/引號字串/檔路徑/snake_case 識別子,須逐一出現在
    anchor 中,缺一即 False(純文字比對、零 DB 寫)。過嚴誤判為 False=安全方向(僅降呈現級、不動裁決)。"""
    a = anchor or ""
    for num in re.findall(r"\d[\d,]*", claim_text):
        if num.replace(",", "") not in a.replace(",", ""):
            return False
    for q in re.findall(r"[「\"']([^」\"']{2,})[」\"']", claim_text):
        if q not in a and re.escape(q) not in a:
            return False
    for p in re.findall(r"[\w/]+/[\w.]+\.\w+", claim_text):
        if p not in a:
            return False
    for ident in re.findall(r"\b[a-z_][a-z0-9_]{3,}\b", claim_text):
        if ident not in a and (not target or ident not in target):
            return False
    return True


def semantic_bound_of(claim_text, verifier, anchor, target=None):
    """B1 導出欄判準:①錨可自 claim_text 以 RULES_ALL 確定性重導出(只比對、不執行)==(verifier,anchor)
    → True;②否則 binding_check 反抽取全命中 → True;否則 False。"""
    fp = fast_anchor(claim_text, target, RULES_ALL)
    if fp and fp[0] == verifier and (fp[1] or "").strip().lower() == (anchor or "").strip().lower():
        return True
    return binding_check(claim_text, verifier, anchor, target)


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


def _selftest():
    """自測（零 DB/零 API、可個別驗證 #29a）:合成 claim 紅綠測純函式——
    normalize_anchor/fast_anchor/binding_check/semantic_bound_of（確定性構錨/反抽取不變式回歸鎖）。"""
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # L2 前綴剝除（大小寫不敏感）+ L3 file_grep 補 target::（錨不含 '/')
    chk("normalize_anchor 剝 verifier 前綴", normalize_anchor("file_grep:foo", "file_grep") == "foo")
    chk("normalize_anchor file_grep 補 target::", normalize_anchor("bar", "file_grep", "p.py") == "p.py::bar")
    chk("normalize_anchor 含 '/' 不補前綴", normalize_anchor("dir/x", "file_grep", "p.py") == "dir/x")
    # L4 快路:確定性構錨（information_schema 存在 / db_query 列數）
    chk("fast_anchor 表存在→information_schema",
        fast_anchor("表 foo 存在") == ("information_schema", "foo", "L4_information_schema"))
    chk("fast_anchor 列數→db_query",
        fast_anchor("表 bar 至少 100 列") == ("db_query", "SELECT count(*) FROM bar => >= 100", "L4_db_query"))
    chk("fast_anchor 不可解析→None", fast_anchor("這句無法機械解析") is None)
    # B1 反抽取:claim 數字/識別子須現於 anchor,缺一即 False（過嚴=安全方向）
    chk("binding_check 全命中→True",
        binding_check("表 bar 至少 100 列", "db_query", "SELECT count(*) FROM bar => >= 100") is True)
    chk("binding_check 數字缺失→False",
        binding_check("表 bar 至少 999 列", "db_query", "SELECT count(*) FROM bar => >= 100") is False)
    # B1 導出欄:錨可自 claim 確定性重導出==(verifier,anchor)→True
    chk("semantic_bound_of 可重導出→True",
        semantic_bound_of("表 foo 存在", "information_schema", "foo") is True)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print((__doc__ or __name__).split("🎯")[0].strip())
    print("(自測:python -m augur.deliberation.anchors --selftest;免 DB 免 API)")

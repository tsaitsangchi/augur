#!/usr/bin/env python
"""本地審議引擎最小迴圈 — qwen 提 claims(結構化)→ 四真 oracle 裁決 → 誠實報告(P1:單 lens 端到端)。

🎯 這支在做什麼(白話):給一個題目(+可選目標檔案),本地 qwen 以指定視角(lens)提出「可機械驗證
   的宣稱」——每條必帶錨點+指定 4 真 oracle 之一;引擎逐條用**確定性工具**裁決 confirmed/refuted,
   無法機驗者 escalate 人裁。**LLM 意見零證據力,工具輸出才是證據**(#15)——這就是把 Claude ultracode
   的「對抗驗證」搬到本地的核心:弱模型(qwen)只需會「提出可驗證的問題」,判對判錯交給誠實的工具。
   全程本地零 Claude token;帳落 deliberation_*(resume/追溯);session 冪等可重跑。

守 #15(裁決全出 oracle)· #28(零 Claude;唯本機 qwen)· #29a。前置=migrate_deliberation_ddl.py --run。
   SSOT=本地審議引擎計畫 v1(2026-07-10)+ 前身 plan §5 機械鎖。

執行指令矩陣:
  python scripts/deliberate.py                                        # 無參數:印矩陣+近期 session 現況(唯讀)
  python scripts/deliberate.py --run --topic "驗證機率層三表就位"        # 題目式(qwen 自析可驗宣稱)
  python scripts/deliberate.py --run --topic "..." --target reports/x.md --lens skeptic   # 附目標檔+視角
  python scripts/deliberate.py --run --topic "..." --model qwen3:8b --max-claims 8        # 換模/量
  python scripts/deliberate.py --report <session_id>                  # 重印某 session 裁決報告(唯讀)
"""
import argparse
import json
import sys
import time
import uuid
from pathlib import Path

import _bootstrap  # noqa: F401  個別可執行:自動把 src/ 插入 sys.path
from augur.core import db
from augur.deliberation.verifiers import ORACLES, verify_claim

REPO = Path(__file__).resolve().parent.parent

CLAIM_SCHEMA = {
    "type": "object",
    "properties": {"claims": {"type": "array", "items": {"type": "object", "properties": {
        "category": {"type": "string", "enum": ["schema", "program", "isolation", "doctrine",
                                                 "antileakage", "truesign", "coverage", "other"]},
        "claim_text": {"type": "string"},
        "anchor": {"type": "string"},
        "assigned_verifier": {"type": "string",
                              "enum": list(ORACLES) + ["human_claude"]},
    }, "required": ["category", "claim_text", "anchor", "assigned_verifier"]}}},
    "required": ["claims"],
}

LENS_PROMPTS = {
    "skeptic":  "你是對抗性懷疑者:假設題目中的宣稱可能是錯的,提出能「證偽」它的檢查點。",
    "complete": "你是完整性稽核者:找出題目範圍內「應存在而可能缺漏」的東西,逐一提出存在性檢查。",
    "doctrine": "你是治權稽核者:檢查是否違反 anti-leakage/隔離/誠實紀律,提出可機驗的違規探測。",
}

CONTRACT = """你的任務:對下列題目提出至多 {n} 條「可機械驗證的宣稱」(claims)。鐵則:
1. 每條 claim 指定 assigned_verifier(四選一);anchor **只放參數本身、絕不含 verifier 名稱前綴**:
   - information_schema:驗表/欄存在。anchor 範例:"feature_values" 或 "feature_values.panel_date"
   - db_query:單標量查詢比較。anchor 範例:"SELECT count(*) FROM model_registry => >= 4"
   - file_grep:檔內正則匹配。anchor 範例:"CLAUDE.md::換機接續"
   - import_isolation:隔離不變式。anchor 恆為:"check_isolation"
   無法用以上四工具驗證的重要疑點 → assigned_verifier='human_claude'(交人裁,不要硬湊)。
2. claim_text 用正向可判真偽句式(「X 存在」「Y 數量≥N」),不用問句。
3. 只輸出 JSON。{lens}

題目:{topic}
{target_block}"""


def _normalize_anchor(anchor, verifier, target=None):
    """機械正規化(LLM 天花板→機械繞道,承 D4b 前例):
    (a) 剝模型畫蛇添足的 'verifier名:' 前綴(實測 4b 系統性加,session delib_ab2ec676a3 六條全中);
    (b) file_grep 無 'path::' 且本 session 有 target → 以 target 補全(確定性補全:用已知執行參數、
        非臆造;實測 4b 常只給 regex,session delib_9dfaf4f826)。
    剝/補皆零資訊損失,契約本體(verifiers.py)維持嚴格不鬆動。"""
    a = (anchor or "").strip()
    prefix = verifier + ":"
    if a.lower().startswith(prefix.lower()):
        a = a[len(prefix):].strip()
    # L3(2026-07-10 commit 終驗實測):anchor 本身像路徑(含 '/')時不補 target:: 前綴——
    # 模型意在 grep 另一檔,誤蓋=把 path 當 regex 必 refuted;留原樣走契約(無 '::' → undecidable 誠實升級)
    if verifier == "file_grep" and "::" not in a and target and "/" not in a:
        a = f"{target}::{a}"
    return a


def _schema_grounding(topic):
    """L1 schema-grounding(session delib_9dfaf4f826/自身落地場實測:錯表名=refuted 主因):
    從題目抽 snake_case 詞 → information_schema LIKE 實查 → 注入「真實存在的表」清單(確定性、零臆造)。"""
    import re as _re
    from augur.core import db as _db
    tokens = {t for t in _re.findall(r"[a-z][a-z0-9_]{3,}", topic.lower())}
    if not tokens:
        return ""
    hits = set()
    with _db.connect() as conn, _db.transaction(conn) as cur:
        for t in list(tokens)[:12]:
            cur.execute("SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema='public' AND table_name LIKE %s LIMIT 6", (f"%{t}%",))
            hits.update(r[0] for r in cur.fetchall())
    if not hits:
        return ""
    return ("\n[真實存在的相關資料表(逐字使用、勿臆造/縮寫表名):" + ", ".join(sorted(hits)[:20]) + "]")


def _fast_anchor(claim_text, target=None):
    """L4 宣稱快路(2026-07-10 基準實測:quant 類 4b 轉譯錨方向/閾值寫歪→假確認 4)——
    可機械解析的宣稱**直接產錨、零 LLM**(確定性凌駕生成;LLM 只留給快路不匹配者)。
    回 (verifier, anchor) 或 None。"""
    import re as _re
    # L5 條件式快路(2026-07-10 集材:5/5 帶 WHERE 宣稱 escalate→LLM 錨不出;確定性產 WHERE)——
    # 「表 T 中 欄 C 等於 V 的列數 至少/至多 N」→ SELECT count(*) FROM T WHERE C='V' => op N
    # L5 條件式快路(2026-07-10 集材+實測:4b 改寫成「表 T 中 C 欄等於 V 的列數 ≥ N」〔含「欄」字/≥符號〕)——
    # 寬鬆吃 T/C/V/op/N:C 欄名(可帶「欄」尾綴)、V 值、比較詞(至少/至多/≥/≤/不少於…)、N。
    # 根因(2026-07-10 逐段除錯):中文語序「T 表中 C 欄等於 V」表名在「表」**之前**;值可含 .-(cc-by)。
    _GE = r"(?:至少有?|不少於|>=|≥|不低於)"
    _LE = r"(?:至多|不超過|<=|≤|不高於)"
    for _cmp, _op in ((_GE, ">="), (_LE, "<=")):
        m = _re.search(r"([a-z_][a-z0-9_]*)\s*表\s*(?:中|裡)?\s*(?:的)?\s*"
                       r"([a-z_][a-z0-9_]*)\s*欄?\s*(?:等於|=|為|是)\s*([a-z0-9_.-]+)\s*"
                       r"(?:的)?\s*列數?\s*" + _cmp + r"\s*([0-9,]+)", claim_text)
        if m:
            t, c, v, n = m.groups()
            return "db_query", f"SELECT count(*) FROM {t} WHERE {c}='{v}' => {_op} {n.replace(',', '')}"
    m = _re.search(r"表\s*([a-z_][a-z0-9_]*)\s*(?:至少有?|不少於|>=?)\s*([0-9,]+)\s*列", claim_text)
    if m:
        return "db_query", f"SELECT count(*) FROM {m.group(1)} => >= {m.group(2).replace(',', '')}"
    m = _re.search(r"表\s*([a-z_][a-z0-9_]*)\s*(?:至多|不超過|<=?)\s*([0-9,]+)\s*列", claim_text)
    if m:
        return "db_query", f"SELECT count(*) FROM {m.group(1)} => <= {m.group(2).replace(',', '')}"
    m = _re.search(r"(?:資料)?表\s*([a-z_][a-z0-9_]*)\s*存在", claim_text)
    if m:
        return "information_schema", m.group(1)
    m = _re.search(r"檔案\s*([\w./-]+\.(?:py|md|json|sh))\s*.{0,6}含.{0,4}字串?\s*[「\"']([^」\"']+)[」\"']", claim_text)
    if m:
        return "file_grep", f"{m.group(1)}::{_re.escape(m.group(2))}"
    if target:
        m = _re.search(r"含.{0,4}字串?\s*[「\"']([^」\"']+)[」\"']", claim_text)
        if m:
            return "file_grep", f"{target}::{_re.escape(m.group(1))}"
    return None


def _verifier_lint(verifier, anchor, target):
    """L2 verifier 選型 lint(8b W2 場實測:程式符號誤派 information_schema→假 refuted):
    information_schema 錨查無表/欄、但錨形如程式符號且有 target → 確定性改派 file_grep(target::錨)。
    只做「查無表+有更合理去處」之改派;改派記於 provenance 由呼叫端落帳。回 (verifier, anchor, lint_note)。"""
    import re as _re
    from augur.core import db as _db
    if verifier != "information_schema" or not target:
        return verifier, anchor, None
    parts = anchor.strip().split(".")
    if not all(_re.fullmatch(r"[a-z_][a-z0-9_]*", p or "") for p in parts):
        return verifier, anchor, None
    with _db.connect() as conn, _db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name=%s",
                    (parts[0],))
        if cur.fetchone()[0]:
            return verifier, anchor, None          # 表真存在 → 原派正確
    return "file_grep", f"{target}::{parts[0]}", f"lint:information_schema 查無表 {parts[0]!r}→改派 file_grep"


def _propose(topic, target, lens, model, n, timeout):
    from augur.advisor.ollama import make_structured_llm_fn
    tb = ""
    if target:
        p = (REPO / target).resolve()
        if not str(p).startswith(str(REPO)) or not p.is_file():
            sys.exit(f"✗ --target 須為 repo 內檔案:{target}")
        text = p.read_text(encoding="utf-8", errors="replace")
        tb = f"目標檔案 {target}(前 6000 字):\n---\n{text[:6000]}\n---"
    prompt = CONTRACT.format(n=n, lens=LENS_PROMPTS.get(lens, LENS_PROMPTS["skeptic"]),
                             topic=topic, target_block=tb) + _schema_grounding(topic)   # L1
    fn = make_structured_llm_fn(CLAIM_SCHEMA, model=model, timeout=timeout, retries=1,
                                options={"temperature": 0, "num_predict": 1600})
    out = fn(prompt)
    return out.get("claims", [])[:n], prompt


def run(topic, target, lens, model, n, timeout):
    t0 = time.time()
    sid = f"delib_{uuid.uuid4().hex[:10]}"
    claims, _ = _propose(topic, target, lens, model, n, timeout)
    if not claims:
        print("✗ qwen 未提出任何 claim(誠實記錄,非成功)"); return 1
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO deliberation_session (session_id, topic, draft_path, model_tag) "
                    "VALUES (%s,%s,%s,%s)", (sid, topic, target, model))
        ids = []
        for c in claims:
            ver, anc = c["assigned_verifier"], _normalize_anchor(c["anchor"], c["assigned_verifier"], target)
            ver, anc, lint = _verifier_lint(ver, anc, target)          # L2
            prov = {"model": model, "lens": lens}
            fp = _fast_anchor(c["claim_text"], target)                 # L4:可機械解析→確定性錨凌駕 LLM 錨
            if fp:
                ver, anc = fp
                prov["fast_path"] = True
            if lint:
                prov["lint"] = lint
            cur.execute(
                "INSERT INTO deliberation_claim (session_id,perspective,category,claim_text,anchor,"
                "assigned_verifier,provenance) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING claim_id",
                (sid, lens, c["category"], c["claim_text"], anc or "(空)", ver, json.dumps(prov)))
            ids.append(cur.fetchone()[0])
        conn.commit()
    print(f"session={sid} | {len(ids)} claims(model={model} lens={lens},{time.time()-t0:.0f}s)\n")
    tally = {}
    for cid in ids:
        r = verify_claim(cid)
        tally[r["status"]] = tally.get(r["status"], 0) + 1
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE deliberation_session SET status='closed', coverage=%s WHERE session_id=%s",
                    (json.dumps(tally), sid))
        conn.commit()
    report(sid)
    print(f"\n總計 {time.time()-t0:.0f}s | {tally}")
    return 0


def report(sid):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT topic, model_tag, status, coverage FROM deliberation_session WHERE session_id=%s", (sid,))
        s = cur.fetchone()
        if not s:
            sys.exit(f"✗ session {sid} 不存在")
        print(f"═══ 審議報告 {sid} ═══\n題目:{s[0]} | model={s[1]} | {s[2]} | {s[3]}")
        cur.execute("""SELECT c.claim_id, c.status, c.claim_text, c.assigned_verifier, c.anchor,
                              (SELECT v.evidence FROM deliberation_verdict v WHERE v.claim_id=c.claim_id
                               ORDER BY v.ran_at DESC LIMIT 1)
                       FROM deliberation_claim c WHERE c.session_id=%s ORDER BY c.claim_id""", (sid,))
        icon = {"confirmed": "✓", "refuted": "✗", "escalated": "⚠", "pending": "…", "undecidable": "?"}
        for cid, st, txt, ver, anc, ev in cur.fetchall():
            print(f"  {icon.get(st,'?')} [{st}] {txt[:70]}")
            print(f"      verifier={ver} anchor={anc[:70]}")
            if ev:
                print(f"      證據:{ev[:110]}")


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--topic")
    ap.add_argument("--target")
    ap.add_argument("--lens", default="skeptic", choices=list(LENS_PROMPTS))
    ap.add_argument("--model", default="qwen3:4b")     # 結構化步預設 4b(快檔;實測 format 約束壓思考洩漏)
    ap.add_argument("--max-claims", dest="n", type=int, default=6)
    ap.add_argument("--timeout", type=float, default=600)
    ap.add_argument("--report")
    args = ap.parse_args()
    if args.report:
        report(args.report); return 0
    if args.run:
        if not args.topic:
            sys.exit("--run 需 --topic")
        return run(args.topic, args.target, args.lens, args.model, args.n, args.timeout)
    print(__doc__.split("執行指令矩陣:")[1])
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT session_id, topic, status, coverage, created_at::date FROM deliberation_session "
                    "ORDER BY created_at DESC LIMIT 5")
        rows = cur.fetchall()
        print("近期 session:" if rows else "近期 session:(無)")
        for r in rows:
            print(f"  {r[0]} | {r[1][:40]} | {r[2]} | {r[3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

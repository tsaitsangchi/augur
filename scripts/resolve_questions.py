#!/usr/bin/env python
"""🎯 提問帳本解決器——先分辨「哪些還真的開著」,再解可機械解的(零 Claude token)。

白話:抽取器把 hugo 的每則訊息都收進帳本,但其中多數**不是可獨立回答的問題**——
  ① 脈絡片段/短指令(「全批照案」「有原文就抓原文」「PAT 更換」)當下即處理、脫離脈絡無語意;
  ② 同一 session 後續仍有訊息 ⇒ 該題在對話中已被回應(**機械可判**:同 session 有更晚的 asked_at)。
硬把這些丟給解決器只會產出胡說。故本支分兩段:
  --classify  規則分類(零 LLM):片段→superseded(context_bound);已在對話中回應→superseded
              (in_session_responded);其餘=**真正還開著**,留 pending 待解。
  --solve     對留下的 mechanical 題跑本地審議引擎(5 oracle);knowledge 題交 advisor(需 Ollama 空檔)。
判準誠實標註於 resolution_ref、append-only 不刪(誤判可追加更正列)。
守 #15(不假裝解決=不對片段生成答案)#28(零 token)#12(裁決走既有引擎不自造)#29;INTEG-H2。

執行指令矩陣:
  python scripts/resolve_questions.py                 # 無參數:現況統計(唯讀)
  python scripts/resolve_questions.py --classify --dry-run   # 預覽分類結果、零寫入
  python scripts/resolve_questions.py --classify      # 實際分類(只動 status='pending' 列)
  python scripts/resolve_questions.py --solve --limit 5      # 解 mechanical 題(本地引擎)
  python scripts/resolve_questions.py --selftest      # 零 DB 純紅綠(判準錨=今日真實樣本)
"""
import argparse
import re
import sys

import _bootstrap  # noqa: F401
from augur.core import db

# 疑問語式:有其一才可能是「可獨立回答的問題」
INTERROGATIVE = ("?", "？", "嗎", "什麼", "如何", "怎麼", "為什麼", "哪些", "哪個", "多少",
                 "是否", "可以", "能否", "請問", "列出", "說明", "檢查", "確認")
MIN_STANDALONE = 12          # 短於此且無疑問語式 → 視為脈絡片段(非獨立問題)
SUBSTANTIVE_LEN = 30         # 夠長即帶獨立語意(即使無疑問詞,如「回報 X 執行狀況:…」之完整請求)


def is_fragment(q: str) -> bool:
    """脈絡片段/短指令(非可獨立回答之問題)。純函式。

    規則 v2(2026-07-27 自測抓出 v1 誤判:長而完整之請求無疑問詞被誤剔):
      長度 ≥ SUBSTANTIVE_LEN → 非片段;有疑問語式且 ≥6 字 → 非片段;其餘 → 片段。
    """
    s = " ".join((q or "").split())
    if not s:
        return True
    if len(s) >= SUBSTANTIVE_LEN:
        return False
    has_q = any(k in s for k in INTERROGATIVE)
    if has_q and len(s) >= 6:
        return False
    return len(s) < MIN_STANDALONE or not has_q


def classify(dry, limit=None):
    n_frag = n_resp = n_open = 0
    samples = []
    with db.connect() as conn, db.transaction(conn) as cur:
        # 每 session 之最後提問時戳:晚於本題 ⇒ 對話續行 ⇒ 本題已在當時被回應(機械可判)
        cur.execute("""
            SELECT q.qid, q.question, q.triage,
                   (q.asked_at IS NOT NULL AND q.asked_at < m.last_at) AS responded
            FROM steward_question_ledger q
            JOIN (SELECT session_ref, max(asked_at) last_at FROM steward_question_ledger
                  GROUP BY session_ref) m USING (session_ref)
            WHERE q.status='pending' ORDER BY q.qid""" + (" LIMIT %s" if limit else ""),
            (limit,) if limit else ())
        for qid, q, _tri, responded in cur.fetchall():
            if is_fragment(q):
                kind, ref = "frag", "context_bound:非獨立問題(脈絡片段/短指令,當下已處理)"
                n_frag += 1
            elif responded:
                kind, ref = "resp", "in_session_responded:同 session 有更晚訊息⇒對話中已回應"
                n_resp += 1
            else:
                n_open += 1
                if len(samples) < 10:
                    samples.append(" ".join(q.split())[:74])
                continue
            if not dry:
                cur.execute("""UPDATE steward_question_ledger SET status='superseded',
                    resolution_ref=%s, resolved_by='rules_v1_classify', resolved_at=now()
                    WHERE qid=%s AND status='pending'""", (ref, qid))
        if not dry:
            conn.commit()
    print(f"{'[dry-run] ' if dry else ''}分類:片段 {n_frag}、對話中已回應 {n_resp} → "
          f"**真正還開著 {n_open} 題**")
    if samples:
        print("  ── 仍開著(樣本) ──")
        for s in samples:
            print(f"    · {s}")
    return 0


def solve(limit):
    """mechanical 題交本地審議引擎;knowledge 題標記待 advisor(不在此生成答案=不假裝)。"""
    import subprocess
    n = 0
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT qid, question FROM steward_question_ledger
            WHERE status='pending' AND triage='mechanical' ORDER BY qid LIMIT %s""", (limit,))
        rows = cur.fetchall()
    for qid, q in rows:
        topic = " ".join(q.split())[:200]
        print(f"  q{qid}: {topic[:60]}…")
        r = subprocess.run(["./venv/bin/python", "scripts/deliberate.py", "--run", "--topic", topic],
                           capture_output=True, text=True, timeout=1800)
        sid = None
        m = re.search(r"(dls_[0-9a-f]+|session[_ ]?id[=: ]+(\S+))", r.stdout or "")
        if m:
            sid = m.group(1)
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("""UPDATE steward_question_ledger SET status=%s, resolution_ref=%s,
                resolved_by='deliberation_engine', resolved_at=now() WHERE qid=%s""",
                ("auto_resolved" if r.returncode == 0 else "pending",
                 f"deliberate:{sid or 'rc=' + str(r.returncode)}", qid))
            conn.commit()
        n += 1
    print(f"  已交審議引擎 {n} 題(結論查 deliberation_claim/verdict;LLM 意見零證據力、oracle 為準)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT status||coalesce('/'||triage,''), count(*)
                       FROM steward_question_ledger GROUP BY 1 ORDER BY 1""")
        for k, n in cur.fetchall():
            print(f"  {k}: {n}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    # 錨=今日 pending 佇列真實樣本
    chk("片段:「全批照案」", is_fragment("「全批照案」"))
    chk("片段:「有原文就抓原文」", is_fragment("有原文就抓原文"))
    chk("片段:「(c) 全 74 支」", is_fragment("(c) 全 74 支"))
    chk("片段:「PAT 更換」", is_fragment("PAT 更換"))
    chk("非片段:含疑問語式之真問題",
        not is_fragment("此專案所有問題解決最佳下一步?或可同步執行作業?"))
    chk("非片段:長指令帶檢查語式",
        not is_fragment("回報 augur 所有背景程式執行狀況:回報時間點、ps 查所有 augur python 背景進程"))
    chk("空字串視為片段", is_fragment(""))
    chk("確定性", is_fragment("x") == is_fragment("x"))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--classify", action="store_true")
    ap.add_argument("--solve", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.classify:
        return classify(a.dry_run, a.limit)
    if a.solve:
        return solve(a.limit or 3)
    print((__doc__ or "").strip())
    print()
    return status()


if __name__ == "__main__":
    sys.exit(main())

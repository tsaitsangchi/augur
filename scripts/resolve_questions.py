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


# v3(2026-07-28 實犯:q5013 貼終端輸出因 ≥30 字被 v2 當實質問題送 advisor 佇列):
# 終端貼文與行程指令**不論多長都是片段**——長度規則之前先判型。錨定式(行首/全式)防誤殺真問題。
TERMINAL_RE = re.compile(r"^\(venv\)|^hugo@|@PC002|^\$ |^[a-z_]+@[\w-]+:~|crontab -|psql .*-c |systemctl ")
DIRECTIVE_RE = re.compile(r"^(下一棒|繼續往|接續|照(這個|此)?(序|案|行程)|開始 |先跑|開走|暫停|全批照案|"
                          r"回覆 ?\S+ 即生效|.{0,12}(-go|-yes|-keep)$)")


def is_fragment(q: str) -> bool:
    """脈絡片段/短指令/貼文(非可獨立回答之問題)。純函式。

    規則 v3:①終端貼文/行程指令/拍板碼 → 片段(**不論長度**;v2 之「≥30 字即實質」讓長貼文漏網)
    ②長度 ≥ SUBSTANTIVE_LEN → 非片段 ③有疑問語式且 ≥6 字 → 非片段 ④其餘 → 片段。
    """
    s = " ".join((q or "").split())
    if not s:
        return True
    if TERMINAL_RE.search(s) or DIRECTIVE_RE.match(s):
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


ADVISOR_URL = "http://127.0.0.1:8399/v1/chat/completions"
ADVISOR_TIMEOUT = 1800          # 慢可以、答案要準(hugo 07-27 指導;advisor think tier 可達 2400s)
DECLINE_RE = re.compile(r"知識庫中無此內容|查無|無相關內容")
LLM_LOCK = "/tmp/augur_llm.lock"


def solve_knowledge(limit, dry):
    """knowledge 題 → advisor(8399,經 guard 鏈)——INTEG-H2 之另半條線(原僅 docstring)。

    誠實三態:①實答 → auto_resolved,resolution_ref 存 advisor 全答(截 1800 字;答案唯出 advisor,
    本支零生成=不假裝)②誠實拒答 → **awaiting_hugo**(機器答不了=升人,不無限重試)③連線/逾時
    → 保持 pending(誠實記錯不改狀態)。每題經 flock(Ollama 單槽,與評測臂/cron 序列化;
    advisor 用 qwen3:8b=重活,**只在批跑空檔執行**)。"""
    import fcntl
    import json as _json
    import os
    import urllib.request
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT qid, question FROM steward_question_ledger
            WHERE status='pending' AND triage='knowledge' ORDER BY qid LIMIT %s""", (limit,))
        rows = cur.fetchall()
    if dry:
        print(f"  [dry] 將送 advisor {len(rows)} 題:")
        for qid, q in rows:
            print(f"    q{qid}: {' '.join(q.split())[:70]}")
        return 0
    secret = os.environ.get("AUGUR_INTERNAL_SECRET", "")
    n_ok = n_dec = n_err = 0
    for qid, q in rows:
        body = _json.dumps({"model": "augur-advisor",
                            "messages": [{"role": "user", "content": q}]}).encode()
        req = urllib.request.Request(ADVISOR_URL, body,
                                     {"Content-Type": "application/json",
                                      **({"X-Augur-Internal": secret} if secret else {})})
        with open(LLM_LOCK, "w") as lk:                    # Ollama 單槽禮讓(阻塞等,與臂序列化)
            fcntl.flock(lk, fcntl.LOCK_EX)
            try:
                with urllib.request.urlopen(req, timeout=ADVISOR_TIMEOUT) as r:
                    ans = _json.loads(r.read())["choices"][0]["message"]["content"]
            except Exception as ex:  # noqa: BLE001  連線/逾時:誠實記錯、狀態不動(可重試)
                print(f"  q{qid}: ✗ {type(ex).__name__}(保持 pending)")
                n_err += 1
                continue
            finally:
                fcntl.flock(lk, fcntl.LOCK_UN)
        declined = bool(DECLINE_RE.search(ans or ""))
        st = "awaiting_hugo" if declined else "auto_resolved"
        ref = ("advisor_declined:誠實拒答(知識庫無內容)→升人" if declined
               else f"advisor[qwen3:8b]:{' '.join((ans or '').split())[:1800]}")
        with db.connect() as conn, db.transaction(conn) as cur:
            cur.execute("""UPDATE steward_question_ledger SET status=%s, resolution_ref=%s,
                resolved_by='advisor', resolved_at=now() WHERE qid=%s AND status='pending'""",
                (st, ref, qid))
            conn.commit()
        n_dec += declined
        n_ok += (not declined)
        print(f"  q{qid}: {'誠實拒答→awaiting_hugo' if declined else '已答(auto_resolved)'}")
    print(f"  合計:實答 {n_ok}、拒答升人 {n_dec}、錯誤保持 pending {n_err}(答案唯出 advisor,零本支生成)")
    return 0


def sweep_queued(dry):
    """v3 規則掃 queued_for_claude(304 題積壓多為 v2 前誤入之貼文/指令;只降級不生成答案)。"""
    n_frag = n_keep = 0
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT qid, question FROM steward_question_ledger
            WHERE status='queued_for_claude' ORDER BY qid""")
        for qid, q in cur.fetchall():
            if is_fragment(q):
                n_frag += 1
                if not dry:
                    cur.execute("""UPDATE steward_question_ledger SET status='superseded',
                        resolution_ref='context_bound:v3 規則(終端貼文/行程指令/拍板碼)',
                        resolved_by='rules_v3_sweep', resolved_at=now()
                        WHERE qid=%s AND status='queued_for_claude'""", (qid,))
            else:
                n_keep += 1
        if not dry:
            conn.commit()
    print(f"{'[dry-run] ' if dry else ''}queued_for_claude 掃帚:降級片段 {n_frag}、留佇 {n_keep}")
    return 0


def sweep_awaiting(dry):
    """v3 掃帚擴 awaiting_hugo(hugo 2026-07-28「順手擴到 awaiting_hugo」):
    只降級**噪音與片段**(harness 系統事件塊/終端貼文/行程指令)——真決策題一律保留給人。
    噪音詞彙單一住所=mine_steward_questions.NOISE_*(#12,import 重用不另抄)。"""
    import mine_steward_questions as msq
    n_noise = n_frag = n_keep = 0
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("""SELECT qid, question FROM steward_question_ledger
            WHERE status='awaiting_hugo' ORDER BY qid""")
        for qid, q in cur.fetchall():
            s2 = " ".join((q or "").split())
            if any(m in s2 for m in msq.NOISE_SUBSTRINGS) or                any(s2.startswith(pfx) for pfx in msq.NOISE_PREFIXES):
                kind, ref = "noise", "noise:harness 系統事件塊誤入(v3 掃帚)"
                n_noise += 1
            elif is_fragment(q):
                kind, ref = "frag", "context_bound:v3 規則(終端貼文/行程指令/拍板碼)"
                n_frag += 1
            else:
                n_keep += 1
                continue
            if not dry:
                cur.execute("""UPDATE steward_question_ledger SET status='superseded',
                    resolution_ref=%s, resolved_by='rules_v3_sweep_awaiting', resolved_at=now()
                    WHERE qid=%s AND status='awaiting_hugo'""", (ref, qid))
        if not dry:
            conn.commit()
    print(f"{'[dry-run] ' if dry else ''}awaiting_hugo 掃帚:噪音 {n_noise}、片段 {n_frag} → "
          f"**留給 hugo 的真決策題 {n_keep}**")
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
    # v3 真實樣本錨(2026-07-28 實犯:三題以 ≥30 字漏網進 knowledge 佇列)
    chk("v3:終端貼文不論長度=片段(q5013 型)",
        is_fragment("hugo@PC002-S1800:~$ crontab -l > ~/crontab.backup.$(date +%Y%m%d) && echo ok"))
    chk("v3:行程指令=片段(q5015 型)", is_fragment("下一棒照行程走 B4"))
    chk("v3:續走指令=片段(q5017 型)", is_fragment("繼續往 M3 走"))
    chk("v3:拍板碼=片段", is_fragment("EVALSET-V2-go"))
    chk("v3:真問題不誤殺(含 crontab 字樣之疑問句)",
        not is_fragment("crontab 的排程語法中 */2 是什麼意思?可以說明嗎"))
    chk("v3:長真問題不誤殺", not is_fragment("太陽能產業專業研發人員此專案需要大量的資料滙入你認為最佳的向量資料庫是什麼?"))
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
    ap.add_argument("--sweep-awaiting", action="store_true",
                    help="v3 掃帚擴 awaiting_hugo(只降噪音/片段;真決策題保留給人)")
    ap.add_argument("--sweep-queued", action="store_true",
                    help="v3 規則掃 queued_for_claude 積壓(貼文/指令降級,不生成答案)")
    ap.add_argument("--solve-knowledge", action="store_true",
                    help="knowledge 題→advisor(8b 重活;批跑空檔才跑,每題 flock 禮讓)")
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
    if a.solve_knowledge:
        return solve_knowledge(a.limit or 16, a.dry_run)
    if a.sweep_queued:
        return sweep_queued(a.dry_run)
    if a.sweep_awaiting:
        return sweep_awaiting(a.dry_run)
    print((__doc__ or "").strip())
    print()
    return status()


if __name__ == "__main__":
    sys.exit(main())

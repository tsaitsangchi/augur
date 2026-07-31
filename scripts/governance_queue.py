#!/usr/bin/env python
"""判準人閘一鍵佇列 — governance_proposal 提案投遞/審視/核可 CLI(#11;hugo 2026-07-25 拍板)。
🎯 這支在做什麼(白話):「能力自動演化、判準人閘一鍵化」的人閘介面。AI 用 submit 投遞提案(diff+證據包,
   送出即被 trigger 凍結不可改);hugo 用 list/show 審視、approve/reject **一鍵裁決**(記 decided_by+時戳
   =P5.W2 人簽留痕);enact 由 AI 於 approved 後執行落地並標 enacted。撤回=withdraw(留痕不刪)。
   核可動作**機械上唯人執行**(2026-07-31 補上真閘:approve/reject 須 TTY＋親手打簽名,
   非 TTY 一律拒絕、不自動代填——前版僅 docstring 宣稱「由 hugo 在 TTY 跑」而無檢查,
   AI 以同 OS 帳號跑即被自動簽為 hugo;比照 direction_gate/review_evolution_candidates isatty 先例)。
   enact 不設 TTY 閘(依設計=AI 於 approved 後落地標記,不寫 decided_by)。
守 P5.W2(人閘)· P4.E3(不刪留痕)· #15(狀態機械可查)· #29a/d。SSOT=演化閉環計畫 §三/#11。
執行指令矩陣:
  python scripts/governance_queue.py                        # 無參數:pending 佇列(安全預設、唯讀)
  python scripts/governance_queue.py --show <id>            # 看單一提案全文(唯讀)
  python scripts/governance_queue.py --submit --kind treaty_text --title T --diff-file F [--evidence R1 R2]
  python scripts/governance_queue.py --approve <id> [--note N]   # hugo 一鍵核可(記人簽)
  python scripts/governance_queue.py --reject <id> [--note N]    # hugo 一鍵駁回
  python scripts/governance_queue.py --enact <id>                # approved→enacted(AI 落地後標記)
  python scripts/governance_queue.py --selftest                  # 零 DB 紅綠
"""
import argparse
import hashlib
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from augur.core import db

KINDS = ("criteria_change", "treaty_text", "soul_amendment", "gate_freeze", "other")


def _pid(title, diff):
    return "gp_" + hashlib.sha256((title + diff).encode()).hexdigest()[:12]


def list_pending(conn):
    with db.transaction(conn) as cur:
        cur.execute("""SELECT proposal_id, kind, title, proposed_by, created_at::date
            FROM governance_proposal WHERE status='pending' ORDER BY created_at""")
        rows = cur.fetchall()
    if not rows:
        print("(佇列空:無 pending 提案)")
    for pid, kind, title, by, d in rows:
        print(f"  {pid} [{kind}] {title} (by {by}, {d})")
    return 0


def show(conn, pid):
    with db.transaction(conn) as cur:
        cur.execute("""SELECT kind, title, diff_text, evidence_refs, proposed_by, status,
            decided_by, decided_at, decision_note FROM governance_proposal WHERE proposal_id=%s""", (pid,))
        row = cur.fetchone()
    if not row:
        print(f"✗ {pid} 不存在"); return 1
    kind, title, diff, ev, by, st, db_, dat, note = row
    print(f"═ {pid} [{kind}] {title}\n  by {by} | status={st}"
          + (f" | decided_by={db_} @{dat} note={note}" if db_ else ""))
    print(f"  證據包: {ev}\n──── diff 全文 ────\n{diff}")
    return 0


def submit(conn, kind, title, diff_file, evidence):
    diff = Path(diff_file).read_text()
    pid = _pid(title, diff)
    with db.transaction(conn) as cur:
        cur.execute("""INSERT INTO governance_proposal
            (proposal_id, kind, title, diff_text, evidence_refs, proposed_by)
            VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (proposal_id) DO NOTHING""",
            (pid, kind, title, diff, __import__("json").dumps(evidence or []), "claude"))
        cur.execute("SELECT status FROM governance_proposal WHERE proposal_id=%s", (pid,))
        st = cur.fetchone()[0]
    print(f"✓ 提案入列(內容已凍結): {pid} status={st}")
    return 0


def _require_human_tty() -> str:
    """人簽前置（2026-07-31 修）：TTY 閘＋打字確認，回簽名者名字。

    前版僅 `getpass.getuser()` 自動取 OS 帳號——docstring 寫「本 CLI 由 hugo 在 TTY 跑」
    但**無任何機械檢查**，致任何以 Steward 之 OS 帳號執行之行程（**含 AI**）會被自動
    簽為人（L6.18(a) AI 不得代簽之直接漏洞；深化理解核驗 2026-07-31 查獲，
    人簽帳本已三度被自測程式寫入之同族病）。修法比照既有三支 CLI 之 isatty 先例
    （`review_evolution_candidates.py:49`）：**非 TTY 一律拒絕寫入、絕不自動代填**；
    TTY 內亦不再默默取 OS 帳號，改要求**親手打出簽名者名字**——打字本身即人在場之證據。

    **2026-07-31 W0-0 補正**：前版留「直接 Enter＝OS 帳號」之回退，使 docstring 與
    模擬專章 §4.4 補強 1（「approve/reject 須 TTY＋**親手打簽名**」）之宣稱**強於 code 實況**
    ——按 Enter 仍取 `getpass.getuser()`，打字並未真的發生。此處改為**空輸入即拒**，
    使條文所述之「親手打字」成為機械要件而非文件描述。
    """
    if not sys.stdin.isatty():
        raise SystemExit("P5.W2 人閘: approve/reject 須 TTY 親跑（禁管道／AI 代簽；"
                         "L6.18(a)）——非互動環境一律拒絕，不自動代填簽名")
    typed = input("簽名者（親手輸入名字；不得留空，無預設值）: ").strip()
    if not typed:
        raise SystemExit("P5.W2 人閘: 簽名不得留空——本 CLI 無預設值、不代填 OS 帳號")
    return typed


def decide(conn, pid, verdict, note):
    actor = _require_human_tty()
    with db.transaction(conn) as cur:
        cur.execute("""UPDATE governance_proposal
            SET status=%s, decided_by=%s, decided_at=now(), decision_note=%s
            WHERE proposal_id=%s AND status='pending'""", (verdict, actor, note, pid))
        n = cur.rowcount
    if n:
        print(f"✓ {pid} → {verdict} (人簽={actor})")
    else:
        print(f"✗ {pid} → {verdict}(非 pending 或不存在)")
    return 0 if n else 1


def enact(conn, pid):
    with db.transaction(conn) as cur:
        cur.execute("""UPDATE governance_proposal SET status='enacted'
            WHERE proposal_id=%s AND status='approved'""", (pid,))
        n = cur.rowcount
    print(f"{'✓' if n else '✗'} {pid} → enacted" + ("" if n else "(須先 approved)"))
    return 0 if n else 1


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("proposal_id 決定性(同內容同 id=冪等投遞)", _pid("t", "d") == _pid("t", "d") and _pid("t", "d") != _pid("t", "e"))
    chk("kind 封閉集與 DDL 一致", set(KINDS) == {"criteria_change", "treaty_text", "soul_amendment", "gate_freeze", "other"})
    chk("decide 只動 pending(SQL 帶 status 守衛)", "status='pending'" in decide.__wrapped__.__doc__ if hasattr(decide, "__wrapped__") else "AND status='pending'" in __import__("inspect").getsource(decide))
    chk("enact 只動 approved", "status='approved'" in __import__("inspect").getsource(enact))
    chk("submit 冪等(ON CONFLICT DO NOTHING)", "DO NOTHING" in __import__("inspect").getsource(submit))

    # ── 人閘之行為驗證(2026-07-31;非字面斷言) ──
    class _NoTTY:
        def isatty(self):
            return False

    class _DBTouched(Exception):
        pass

    class _TripConn:
        def cursor(self):
            raise _DBTouched("decide 在 TTY 閘前就碰了 DB")

    _stdin = sys.stdin
    sys.stdin = _NoTTY()
    try:
        try:
            decide(_TripConn(), "gp_fake", "approved", None)
            chk("非 TTY 之 approve 被拒", False)
        except SystemExit as e:
            chk("非 TTY 之 approve 被拒(SystemExit,且訊息含 P5.W2)", "P5.W2" in str(e))
        except _DBTouched:
            chk("非 TTY 之 approve 被拒(**在碰 DB 之前**)", False)
    finally:
        sys.stdin = _stdin

    class _FakeTTY:
        def isatty(self):
            return True

    import builtins
    _input = builtins.input
    sys.stdin = _FakeTTY()
    builtins.input = lambda prompt="": "hugo-typed"
    try:
        chk("TTY 內簽名＝親手打的字(非默默取 OS 帳號)", _require_human_tty() == "hugo-typed")
        # 2026-07-31 W0-0:前版此處鎖定「空輸入回退 OS 帳號」為通過條件,等於把
        # 「打字並未真的發生」寫成規格,與專章 §4.4 補強 1 之「親手打簽名」相牴觸。改鎖為「拒絕」。
        builtins.input = lambda prompt="": ""
        _empty_rejected = False
        try:
            _require_human_tty()
        except SystemExit:
            _empty_rejected = True
        chk("**空輸入即拒**(無預設值、不回退 OS 帳號;專章 §4.4 補強 1 名實相符)", _empty_rejected)
        builtins.input = lambda prompt="": "   "
        _blank_rejected = False
        try:
            _require_human_tty()
        except SystemExit:
            _blank_rejected = True
        chk("純空白亦拒(strip 後為空)", _blank_rejected)
    finally:
        builtins.input = _input
        sys.stdin = _stdin
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="判準人閘一鍵佇列")
    ap.add_argument("--show"), ap.add_argument("--submit", action="store_true")
    ap.add_argument("--kind", choices=KINDS), ap.add_argument("--title"), ap.add_argument("--diff-file")
    ap.add_argument("--evidence", nargs="*")
    ap.add_argument("--approve"), ap.add_argument("--reject"), ap.add_argument("--enact"), ap.add_argument("--note")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    with db.connect() as conn:
        if a.show:
            return show(conn, a.show)
        if a.submit:
            if not (a.kind and a.title and a.diff_file):
                print("✗ --submit 需 --kind --title --diff-file"); return 1
            return submit(conn, a.kind, a.title, a.diff_file, a.evidence)
        if a.approve:
            return decide(conn, a.approve, "approved", a.note)
        if a.reject:
            return decide(conn, a.reject, "rejected", a.note)
        if a.enact:
            return enact(conn, a.enact)
        print(__doc__)
        print("pending 佇列:")
        return list_pending(conn)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""🎯 提問抽取器——從 Claude session 逐字稿+chat 表把 hugo 的提問挖進帳本(零 Claude token)。

白話:掃 ~/.claude/projects/*augur*/*.jsonl 的 user 回合(content 為字串=真人打字;陣列=tool
結果不取)+`chat_message`(role='user'),正規化去重(sha256[:16])寫入 steward_question_ledger,
ON CONFLICT 略過=冪等可重跑。全程本地純 Python(#28 最小 usage)。
守 #15(一題不忘)#28(零 token)#29;INTEG-H。

執行指令矩陣:
  python scripts/mine_steward_questions.py             # 無參數:統計預覽(唯讀)
  python scripts/mine_steward_questions.py --dry-run   # 列將入庫題目、零寫入
  python scripts/mine_steward_questions.py --run       # 實際入庫(冪等)
  python scripts/mine_steward_questions.py --selftest  # 零 DB 純紅綠(過濾邏輯)
"""
import glob
import hashlib
import json
import os
import sys

import _bootstrap  # noqa: F401
from augur.core import db

# augur 全家(含 worktree)+ttai+rdai(整合對象,hugo 提問一併收);stock-backend 刻意排除
# (clean-room #17:舊專案零觸點——寧缺勿污染,逐字稿亦不例外)
SESSION_GLOBS = (os.path.expanduser("~/.claude/projects/*augur*/*.jsonl"),
                 os.path.expanduser("~/.claude/projects/-home-hugo-project-ttai/*.jsonl"),
                 os.path.expanduser("~/.claude/projects/-home-hugo-project-rdai/*.jsonl"))
SESSION_GLOB = SESSION_GLOBS[0]  # 相容既有引用
NOISE_PREFIXES = ("<local-command-caveat", "<command-name", "Caveat:", "[Request interrupted",
                  "<system-reminder", "[SYSTEM NOTIFICATION", "<local-command-stdout",
                  "This session is being continued")
MIN_CHARS = 4


def _dedup(text):
    norm = " ".join(text.split())
    return hashlib.sha256(norm.encode()).hexdigest()[:16]


def keep(content) -> bool:
    """真人提問過濾:字串(非 tool 結果陣列)、非雜訊前綴、長度下限。純函式供自測。"""
    if not isinstance(content, str):
        return False
    s = content.strip()
    if len(s) < MIN_CHARS:
        return False
    return not any(s.startswith(p) for p in NOISE_PREFIXES)


def iter_session_questions():
    paths = sorted({p for g in SESSION_GLOBS for p in glob.glob(g)})
    for path in paths:
        sid = os.path.basename(path).rsplit(".", 1)[0]
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if obj.get("type") != "user":
                        continue
                    content = (obj.get("message") or {}).get("content")
                    if keep(content):
                        yield ("claude_session", sid, content.strip(), obj.get("timestamp"))
        except OSError:
            continue


def iter_chat_questions(cur):
    cur.execute("SELECT session_id, content, created_at FROM chat_message WHERE role='user'")
    for sid, content, ts in cur.fetchall():
        if keep(content):
            yield ("chat_ui", f"chat:{sid}", content.strip(), ts)


def run(dry):
    n_new, n_dup, preview = 0, 0, []
    with db.connect() as conn, db.transaction(conn) as cur:
        rows = list(iter_session_questions()) + list(iter_chat_questions(cur))
        for source, ref, q, ts in rows:
            key = _dedup(q)
            if dry:
                cur.execute("SELECT 1 FROM steward_question_ledger WHERE dedup_key=%s", (key,))
                if cur.fetchone():
                    n_dup += 1
                else:
                    n_new += 1
                    if len(preview) < 8:
                        preview.append(q[:60].replace("\n", " "))
                continue
            cur.execute(
                """INSERT INTO steward_question_ledger (source, session_ref, question, asked_at, dedup_key)
                   VALUES (%s,%s,%s,%s,%s) ON CONFLICT (dedup_key) DO NOTHING RETURNING qid""",
                (source, ref, q, ts, key))
            if cur.fetchone():
                n_new += 1
            else:
                n_dup += 1
        if not dry:
            conn.commit()
    mode = "[dry-run] " if dry else ""
    print(f"{mode}掃得 {len(rows)} 則 → 新入 {n_new}、既有略過 {n_dup}(冪等)")
    for p in preview:
        print(f"  + {p}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("真人字串保留", keep("augur database還原好了嗎?"))
    chk("tool 結果陣列剔除", not keep([{"type": "tool_result"}]))
    chk("雜訊前綴剔除(caveat)", not keep("<local-command-caveat>xxx"))
    chk("系統通知剔除", not keep("[SYSTEM NOTIFICATION - NOT USER INPUT] x"))
    chk("過短剔除", not keep("ok"))
    chk("dedup 正規化(空白不敏感)", _dedup("a  b\nc") == _dedup("a b c"))
    chk("dedup 內容敏感", _dedup("q1") != _dedup("q2"))
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--selftest" in a:
        sys.exit(_selftest())
    if "--run" in a:
        sys.exit(run(dry=False))
    if "--dry-run" in a:
        sys.exit(run(dry=True))
    print((__doc__ or "").strip())
    print(f"\nsession 檔: {len(glob.glob(SESSION_GLOB))} 個 @ {SESSION_GLOB}")
    sys.exit(0)

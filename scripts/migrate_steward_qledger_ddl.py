#!/usr/bin/env python
"""🎯 Steward 提問帳本 DDL——hugo 每日提問落表、逐項追蹤、一題不忘(INTEG-H;P4.E3 append-only)。

白話:對話裡的提問散在 session 逐字稿與 chat 表,無帳=會忘。本表是唯一落點:每題一列、
dedup 去重、triage 分流(機械/知識/實作/決策)、status 追到 resolved;DELETE/TRUNCATE 拒
(復用 honesty_delete_only_guard,#12)——問過的問題不可湮滅,錯了追加更正列。
守 #15(一題不忘=誠實)#12(guard 復用)#29;INTEG-H(整合計畫)。

執行指令矩陣:
  python scripts/migrate_steward_qledger_ddl.py             # 安全預設=印矩陣+--check
  python scripts/migrate_steward_qledger_ddl.py --check     # 唯讀:表/guard 現況
  python scripts/migrate_steward_qledger_ddl.py --apply     # 建表+trigger(冪等)
  python scripts/migrate_steward_qledger_ddl.py --selftest  # 零 DB 純紅綠
"""
import sys

import _bootstrap  # noqa: F401
from augur.core import db

TABLE = "steward_question_ledger"
DDL = f"""CREATE TABLE IF NOT EXISTS {TABLE} (
    qid            BIGSERIAL PRIMARY KEY,
    source         TEXT NOT NULL CHECK (source IN ('claude_session','chat_ui')),
    session_ref    TEXT,
    question       TEXT NOT NULL,
    asked_at       TIMESTAMPTZ,
    dedup_key      TEXT NOT NULL UNIQUE,
    triage         TEXT CHECK (triage IN ('mechanical','knowledge','implementation','decision')),
    triage_by      TEXT,
    status         TEXT NOT NULL DEFAULT 'pending'
                   CHECK (status IN ('pending','auto_resolved','queued_for_claude',
                                     'awaiting_hugo','resolved','superseded')),
    resolution_ref TEXT,
    resolved_by    TEXT,
    resolved_at    TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
)"""
TRIGGERS = (
    f"""DO $$ BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_{TABLE}_delonly_row') THEN
            CREATE TRIGGER trg_{TABLE}_delonly_row BEFORE DELETE ON {TABLE}
                FOR EACH ROW EXECUTE FUNCTION honesty_delete_only_guard();
        END IF;
    END $$""",
    f"""DO $$ BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='trg_{TABLE}_delonly_trunc') THEN
            CREATE TRIGGER trg_{TABLE}_delonly_trunc BEFORE TRUNCATE ON {TABLE}
                FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
        END IF;
    END $$""",
)


def check():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass(%s)", (f"public.{TABLE}",))
        t = cur.fetchone()[0]
        print(f"  {TABLE}: {'存在' if t else '未建'}")
        if t:
            cur.execute("SELECT count(*) FROM pg_trigger WHERE tgrelid=%s::regclass AND NOT tgisinternal", (TABLE,))
            print(f"  guard trigger: {cur.fetchone()[0]}/2")
            cur.execute(f"SELECT status||':'||count(*) FROM {TABLE} GROUP BY status ORDER BY 1")
            rows = [r[0] for r in cur.fetchall()]
            print(f"  列數分布: {', '.join(rows) if rows else '(空)'}")
    return 0


def apply():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT 1 FROM pg_proc WHERE proname='honesty_delete_only_guard'")
        if not cur.fetchone():
            print("✗ 缺 honesty_delete_only_guard——先跑 migrate_honesty_guards_ddl.py --apply")
            return 1
        cur.execute(DDL)
        for t in TRIGGERS:
            cur.execute(t)
        conn.commit()
    print(f"✓ {TABLE} 落地(冪等;guard 復用 #12)")
    return check()


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("dedup UNIQUE(不重複記錄)", "dedup_key      TEXT NOT NULL UNIQUE" in DDL)
    chk("status 封閉枚舉含 awaiting_hugo(決策不代答)", "awaiting_hugo" in DDL)
    chk("triage 封閉四類", all(x in DDL for x in ("mechanical", "knowledge", "implementation", "decision")))
    chk("guard 復用既有函式(#12 不重造)", all("honesty_delete_only_guard" in t for t in TRIGGERS))
    chk("DELETE+TRUNCATE 雙 trigger", len(TRIGGERS) == 2)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--selftest" in a:
        sys.exit(_selftest())
    if "--apply" in a:
        sys.exit(apply())
    if "--check" in a:
        sys.exit(check())
    print((__doc__ or "").strip())
    sys.exit(check())

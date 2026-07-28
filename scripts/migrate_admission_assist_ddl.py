#!/usr/bin/env python
"""建 knowledge_admission_assist 帳本 — ADM-AI-ASSIST S0/S1（選項 C）。

🎯 這支在做什麼(白話):為「本地 AI 入庫預審建議」建獨立帳本表——對 proposed 來源／
   pending staging 寫 score／reason／flags，**永不**改 approval_status、永不呼叫
   curation.transition(approve|activate)。多輪重跑冪等（同 target 可多列；查最新）。
守 #6(冪等 DDL)· #29a/d(指令矩陣)· FZ-keep(零市場 API)· 憲章 v1.41.0(升級唯人)。
SSOT=reports/augur_ai_admission_assist_plan_20260728.md §3.1 C。

執行指令矩陣:
  python scripts/migrate_admission_assist_ddl.py              # 安全預設=--dry-run
  python scripts/migrate_admission_assist_ddl.py --dry-run    # 唯讀現況
  python scripts/migrate_admission_assist_ddl.py --apply      # 冪等建表
  python scripts/migrate_admission_assist_ddl.py --selftest   # 零 DB 紅綠（DDL 字串不變式）
  python scripts/migrate_admission_assist_ddl.py --check     # 套用後活查表是否在
"""
from __future__ import annotations

import argparse
import sys

import _bootstrap  # noqa: F401

DDL = """
CREATE TABLE IF NOT EXISTS knowledge_admission_assist (
    assist_id      bigserial PRIMARY KEY,
    target_kind    text NOT NULL
                   CHECK (target_kind IN ('source', 'staging')),
    target_id      text NOT NULL,
    score          real NOT NULL
                   CHECK (score >= 0.0 AND score <= 1.0),
    reason         text NOT NULL,
    flags          jsonb NOT NULL DEFAULT '{}'::jsonb,
    actor          text NOT NULL DEFAULT 'local_ai_v1',
    model          text,
    prompt_hash    text,
    created_at     timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_kaa_target
  ON knowledge_admission_assist (target_kind, target_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_kaa_score
  ON knowledge_admission_assist (score DESC, created_at DESC);
COMMENT ON TABLE knowledge_admission_assist IS
  'ADM-AI-ASSIST: L2 本地 AI 預審建議帳本（score/reason/flags；禁改審批態；actor=local_ai_v1）';
ALTER TABLE knowledge_source_review_log
  DROP CONSTRAINT IF EXISTS knowledge_source_review_log_action_check;
ALTER TABLE knowledge_source_review_log
  ADD CONSTRAINT knowledge_source_review_log_action_check
  CHECK (action IN ('propose','probe','approve','activate','suspend','resume',
                    'exhaust','reject','reopen','edit','ratify','assist'));
"""

FORBIDDEN_SQL_FRAGMENTS = (
    "curation.transition",
    "UPDATE knowledge_source",
    "--approve",
    "--activate",
)


def selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    chk("DDL 建 knowledge_admission_assist", "knowledge_admission_assist" in DDL)
    chk("target_kind 含 source/staging", "'source'" in DDL and "'staging'" in DDL)
    chk("score CHECK 0..1", "score >= 0.0" in DDL and "score <= 1.0" in DDL)
    chk("actor 預設 local_ai_v1", "local_ai_v1" in DDL)
    chk("review_log action 含 assist", "'assist'" in DDL)
    for frag in FORBIDDEN_SQL_FRAGMENTS:
        chk(f"DDL 不含 {frag!r}", frag not in DDL)
    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def check_live() -> int:
    from augur.core import db

    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT to_regclass('public.knowledge_admission_assist')")
        reg = cur.fetchone()[0]
        print(f"knowledge_admission_assist: {'已在' if reg else '未建'}")
        if not reg:
            return 1
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name='knowledge_admission_assist'
            ORDER BY ordinal_position""")
        cols = [r[0] for r in cur.fetchall()]
        need = {"assist_id", "target_kind", "target_id", "score", "reason", "flags", "actor"}
        missing = need - set(cols)
        print(f"  columns={cols}")
        if missing:
            print(f"  ✗ 缺欄 {missing}")
            return 1
        cur.execute("""
            SELECT pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conrelid = 'knowledge_source_review_log'::regclass
              AND conname = 'knowledge_source_review_log_action_check'""")
        action_ck = (cur.fetchone() or [None])[0] or ""
        has_assist = "'assist'" in action_ck
        print(f"  review_log_action_check_has_assist={has_assist}")
        if not has_assist:
            print("  ✗ review_log action check 尚未納入 assist")
            return 1
        print("  ✓ 必要欄齊")
        return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ADM-AI-ASSIST 帳本 DDL（選項 C）")
    ap.add_argument("--apply", action="store_true", help="冪等建表")
    ap.add_argument("--dry-run", action="store_true", help="唯讀現況（預設）")
    ap.add_argument("--selftest", action="store_true", help="零 DB 紅綠")
    ap.add_argument("--check", action="store_true", help="活查表是否在")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.check:
        return check_live()

    apply = bool(args.apply) and not args.dry_run
    from augur.core import db

    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT to_regclass('public.knowledge_admission_assist')")
        exists = cur.fetchone()[0] is not None
        cur.execute("SELECT count(*) FROM knowledge_source WHERE approval_status='proposed'")
        n_prop = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM knowledge_staging WHERE status='pending'")
        n_pend = cur.fetchone()[0]
        print("ADM-AI-ASSIST DDL 現況（選項 C）:")
        print(f"  knowledge_admission_assist: {'已在' if exists else '待建'}")
        print(f"  池量（唯讀）: proposed={n_prop} pending_staging={n_pend}")
        if not apply:
            print("\n(唯讀 dry-run；--apply 才套用。硬禁：本 DDL 不改 approval_status)")
            return 0
        with db.transaction(conn) as cur2:
            cur2.execute(DDL)
        print("  ✓ CREATE TABLE IF NOT EXISTS knowledge_admission_assist + indexes")
        return check_live()


if __name__ == "__main__":
    sys.exit(main())

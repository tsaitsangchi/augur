#!/usr/bin/env python
"""advisor_probe_candidate 表遷移 — chat 真實問答之進化燃料候選(P-B;整合計畫 §四唯一新表)。

🎯 這支在做什麼(白話):chat 的真實使用軌跡是部署域分布——guard 拒答的問題=天然 L3/L4 題材、
   答得好的問答=gold 候選。本表收「候選」:append-only+誠實閘(DELETE/TRUNCATE 拒)、
   review_status 單向前進(pending→approved_eval/approved_gold/rejected,決定不可回改 P4.E3)。
   **人審後**才進 eval 題(僅入新 set_id,凍結集永不加題)或 gold(provenance 記 chat 來源)。
守 #1(候選≠題;人審才升)· #12(DDL 單一住所)· #15(誠實閘)· P4.E3(單向前進)· #29a/d。
SSOT=reports/augur_advisor_evolution_integration_plan_20260727.md §四。

執行指令矩陣:
  python scripts/migrate_advisor_probe_ddl.py            # 無參數:現況(表在?閘在?列數?)
  python scripts/migrate_advisor_probe_ddl.py --apply    # 執行遷移(冪等)
  python scripts/migrate_advisor_probe_ddl.py --dry-run  # 只印 SQL
  python scripts/migrate_advisor_probe_ddl.py --selftest # 零 DB 紅綠
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

SQL = """
CREATE TABLE IF NOT EXISTS advisor_probe_candidate (
    probe_id      BIGSERIAL PRIMARY KEY,
    source_kind   TEXT NOT NULL CHECK (source_kind IN ('chat_decline','chat_ambig','chat_gold')),
    session_id    BIGINT NOT NULL,
    message_id    BIGINT NOT NULL,
    question      TEXT NOT NULL,
    answer        TEXT,
    dedup_key     TEXT NOT NULL UNIQUE,
    review_status TEXT NOT NULL DEFAULT 'pending'
                  CHECK (review_status IN ('pending','approved_eval','approved_gold','rejected')),
    reviewed_by   TEXT, reviewed_at TIMESTAMPTZ,
    contains_private BOOLEAN NOT NULL DEFAULT false,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION probe_review_forward_only() RETURNS trigger AS $$
BEGIN
    IF TG_OP IN ('DELETE', 'TRUNCATE') THEN
        RAISE EXCEPTION '% on advisor_probe_candidate 遭誠實閘拒絕(append-only)', TG_OP;
    END IF;
    IF TG_OP = 'UPDATE' AND OLD.review_status <> 'pending'
       AND NEW.review_status IS DISTINCT FROM OLD.review_status THEN
        RAISE EXCEPTION 'probe % 已決(%)不可回改——單向前進(P4.E3)', OLD.probe_id, OLD.review_status;
    END IF;
    RETURN COALESCE(NEW, OLD);
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS probe_forward_row ON advisor_probe_candidate;
CREATE TRIGGER probe_forward_row BEFORE UPDATE OR DELETE ON advisor_probe_candidate
    FOR EACH ROW EXECUTE FUNCTION probe_review_forward_only();
DROP TRIGGER IF EXISTS probe_forward_stmt ON advisor_probe_candidate;
CREATE TRIGGER probe_forward_stmt BEFORE TRUNCATE ON advisor_probe_candidate
    FOR EACH STATEMENT EXECUTE FUNCTION probe_review_forward_only();
"""


def apply(dry):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.advisor_probe_candidate')")
        have = cur.fetchone()[0] is not None
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'probe_forward%' AND NOT tgisinternal")
        trigs = cur.fetchone()[0]
        if have and trigs >= 2:
            print("✓ 表與誠實閘皆在——冪等跳過")
            return 0
        if dry:
            print(SQL)
            print("(--dry-run:未執行)")
            return 0
        cur.execute(SQL)
        print("✓ advisor_probe_candidate + append-only/forward-only 閘 落地")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.advisor_probe_candidate')")
        if cur.fetchone()[0] is None:
            print("  (表未建;--apply)")
            return 0
        cur.execute("SELECT source_kind, review_status, count(*) FROM advisor_probe_candidate GROUP BY 1,2")
        rows = cur.fetchall()
        print("  分佈:", rows or "(0 列)")
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'probe_forward%' AND NOT tgisinternal")
        print(f"  誠實閘 trigger:{cur.fetchone()[0]} 個")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("三種候選源 CHECK", all(k in SQL for k in ("chat_decline", "chat_ambig", "chat_gold")))
    chk("review 四態 CHECK+預設 pending",
        all(k in SQL for k in ("pending", "approved_eval", "approved_gold", "rejected")))
    chk("dedup UNIQUE(防重覆入列)", "dedup_key     TEXT NOT NULL UNIQUE" in SQL)
    chk("誠實閘:DELETE/TRUNCATE 拒", "TG_OP IN ('DELETE', 'TRUNCATE')" in SQL)
    chk("review 單向前進(已決不可回改 P4.E3)", "不可回改" in SQL)
    chk("row+statement 雙 trigger", SQL.count("CREATE TRIGGER") == 2)
    chk("冪等(IF NOT EXISTS/OR REPLACE/DROP IF EXISTS)",
        "IF NOT EXISTS" in SQL and "OR REPLACE" in SQL and "DROP TRIGGER IF EXISTS" in SQL)
    chk("隱私旗標欄在(contains_private)", "contains_private" in SQL)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="advisor_probe_candidate 遷移(P-B)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.apply or a.dry_run:
        return apply(a.dry_run)
    print(__doc__)
    print("現況:")
    return status()


if __name__ == "__main__":
    sys.exit(main())

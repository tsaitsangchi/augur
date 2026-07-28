#!/usr/bin/env python
"""factor_direction_ruling 表遷移 — map 方向衝突之增列式裁決(裁多數方,hugo 2026-07-28)。

🎯 這支在做什麼(白話):principle_factor_map 掛誠實刪除閘(不刪史)——學派方向衝突不能靠刪列裁決。
   本表=**增列式裁決**:正典方向住這裡(人裁、帶證據可溯),各學派 map 列史料原封;符號尺先查裁決、
   無裁決才看 map 共識(衝突仍 fail-closed)。對齊 P4.E3 只增不刪。
   誠實閘:DELETE/TRUNCATE 拒(改裁=INSERT 新列覆蓋語意?否——UNIQUE(feature),改裁=UPDATE 須 GUC+
   evidence 更新,舊裁決以 git+evidence 溯)。
守 #29b(裁決=資料住 DB)· #15(evidence 禁空)· #9/#10(證據可溯)· #29a/d。
裁決 SSOT=reports/augur_factor_map_hygiene_20260728.md §一+hugo 拍板原文。

執行指令矩陣:
  python scripts/migrate_direction_ruling_ddl.py            # 無參數:現況(表在?裁決列?,唯讀)
  python scripts/migrate_direction_ruling_ddl.py --apply    # 遷移(冪等)
  python scripts/migrate_direction_ruling_ddl.py --dry-run  # 只印 SQL
  python scripts/migrate_direction_ruling_ddl.py --selftest # 零 DB 紅綠
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

GUC = "augur.honesty_write"

SQL = f"""
CREATE TABLE IF NOT EXISTS factor_direction_ruling (
    feature             TEXT PRIMARY KEY,
    canonical_direction SMALLINT NOT NULL CHECK (canonical_direction IN (1, -1)),
    ruled_by            TEXT NOT NULL CHECK (btrim(ruled_by) <> ''),
    evidence            JSONB NOT NULL,
    ruled_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (evidence <> 'null'::jsonb AND evidence <> '{{}}'::jsonb)
);

CREATE OR REPLACE FUNCTION factor_ruling_guard() RETURNS trigger AS $$
BEGIN
    IF TG_OP IN ('DELETE', 'TRUNCATE') THEN
        RAISE EXCEPTION '% on factor_direction_ruling 遭誠實閘拒絕(改裁=UPDATE 帶 GUC+新證據,不滅史)', TG_OP;
    END IF;
    IF TG_OP = 'UPDATE' AND coalesce(current_setting('{GUC}', true), '') <> 'on' THEN
        RAISE EXCEPTION 'UPDATE 遭拒:裁決被默改=方向正典默改;須經工具鏈(SET LOCAL {GUC}=on)';
    END IF;
    RETURN COALESCE(NEW, OLD);
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS fdr_row ON factor_direction_ruling;
CREATE TRIGGER fdr_row BEFORE UPDATE OR DELETE ON factor_direction_ruling
    FOR EACH ROW EXECUTE FUNCTION factor_ruling_guard();
DROP TRIGGER IF EXISTS fdr_stmt ON factor_direction_ruling;
CREATE TRIGGER fdr_stmt BEFORE TRUNCATE ON factor_direction_ruling
    FOR EACH STATEMENT EXECUTE FUNCTION factor_ruling_guard();
"""


def apply(dry):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.factor_direction_ruling')")
        have = cur.fetchone()[0] is not None
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'fdr_%' AND NOT tgisinternal")
        if have and cur.fetchone()[0] >= 2:
            print("✓ 表與誠實閘皆在——冪等跳過")
            return 0
        if dry:
            print(SQL)
            print("(--dry-run:未執行)")
            return 0
        cur.execute(SQL)
        print("✓ factor_direction_ruling + 誠實閘 落地(裁決列=人裁帶證據)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT to_regclass('public.factor_direction_ruling')")
        if cur.fetchone()[0] is None:
            print("  (表未建;--apply)")
            return 0
        cur.execute("SELECT feature, canonical_direction, ruled_by, ruled_at::date FROM factor_direction_ruling ORDER BY 1")
        rows = cur.fetchall()
        print(f"  裁決 {len(rows)} 列:" if rows else "  (0 裁決)")
        for r in rows:
            print(f"    {r[0]:28} → {r[1]:+d}  by {r[2]} @{r[3]}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("方向僅 ±1 CHECK", "canonical_direction IN (1, -1)" in SQL)
    chk("ruled_by 禁空(人裁)", "btrim(ruled_by) <> ''" in SQL)
    chk("evidence 禁空/null(裁決須可溯)", "evidence <> 'null'::jsonb" in SQL)
    chk("誠實閘:DELETE/TRUNCATE 拒+UPDATE 須 GUC", "遭誠實閘拒絕" in SQL and GUC in SQL)
    chk("row+stmt 雙 trigger", SQL.count("CREATE TRIGGER") == 2)
    chk("UNIQUE(feature)=PRIMARY KEY(一特徵一正典)", "feature             TEXT PRIMARY KEY" in SQL)
    chk("冪等", "IF NOT EXISTS" in SQL and "DROP TRIGGER IF EXISTS" in SQL)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="factor_direction_ruling 遷移(增列式方向裁決)")
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

#!/usr/bin/env python
"""feature_values 誠實閘遷移 — 生產特徵表上鎖(FV-GUARD-go,hugo 2026-07-29)。

🎯 這支在做什麼(白話):2026-07-29 事件(生產表被無帳批量寫入、鑑識耗時)之根因修補——
   feature_values 至今裸奔。閘型:**INSERT/UPDATE/DELETE 皆須 GUC 通行證**(生產表=衍生資料,
   合法重建/清理要留路,不硬拒;合法 writer=features/panel.py 已帶 SET LOCAL)、TRUNCATE 硬拒。
   人工操作(如 hugo 親搬)須先 SET LOCAL=強制留意識痕,配 evolution_run 事件列記帳(先例=run 10)。
守 #15(無帳寫入根絕)· #29a/d。SSOT=audits/PRODSET-LENDING-PROMOTION-20260729.md 殘餘債條。

執行指令矩陣:
  python scripts/migrate_feature_values_guard_ddl.py            # 無參數:現況(唯讀)
  python scripts/migrate_feature_values_guard_ddl.py --apply    # 上閘(冪等)
  python scripts/migrate_feature_values_guard_ddl.py --selftest # 零 DB 紅綠
"""
import argparse
import sys

import _bootstrap  # noqa: F401
from augur.core import db

GUC = "augur.honesty_write"

SQL = f"""
CREATE OR REPLACE FUNCTION fv_guard() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'TRUNCATE' THEN
        RAISE EXCEPTION 'TRUNCATE feature_values 遭誠實閘拒絕(重建走 writer 逐 panel upsert)';
    END IF;
    IF coalesce(current_setting('{GUC}', true), '') <> 'on' THEN
        RAISE EXCEPTION '% feature_values 遭拒:生產特徵表寫入須通行證(SET LOCAL {GUC}=on)——'
            '合法 writer=features/panel.py;人工操作須配 evolution_run 事件列記帳(先例 run 10)', TG_OP;
    END IF;
    RETURN COALESCE(NEW, OLD);
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS fv_row ON feature_values;
CREATE TRIGGER fv_row BEFORE INSERT OR UPDATE OR DELETE ON feature_values
    FOR EACH ROW EXECUTE FUNCTION fv_guard();
DROP TRIGGER IF EXISTS fv_stmt ON feature_values;
CREATE TRIGGER fv_stmt BEFORE TRUNCATE ON feature_values
    FOR EACH STATEMENT EXECUTE FUNCTION fv_guard();
"""


def apply(dry=False):
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'fv_%' AND NOT tgisinternal")
        if cur.fetchone()[0] >= 2:
            print("✓ 閘已在——冪等跳過")
            return 0
        if dry:
            print(SQL)
            return 0
        cur.execute(SQL)
        print("✓ feature_values 誠實閘落地(寫入須 GUC;TRUNCATE 拒)")
    return 0


def status():
    with db.connect() as conn, db.transaction(conn) as cur:
        cur.execute("SELECT tgname FROM pg_trigger WHERE tgname LIKE 'fv_%' AND NOT tgisinternal")
        rows = [r[0] for r in cur.fetchall()]
        print(f"  閘:{rows or '(未上;--apply)'}")
    return 0


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("INSERT/UPDATE/DELETE 皆入 row trigger(無帳寫入根絕)",
        "BEFORE INSERT OR UPDATE OR DELETE" in SQL)
    chk("TRUNCATE 硬拒", "TRUNCATE feature_values 遭誠實閘拒絕" in SQL)
    chk("GUC 通行證路留(合法重建/人工留痕)", GUC in SQL and "SET LOCAL" in SQL)
    chk("錯誤訊息指路(writer 與事件列先例)", "features/panel.py" in SQL and "run 10" in SQL)
    chk("冪等", "DROP TRIGGER IF EXISTS" in SQL)
    import pathlib
    src = pathlib.Path(__file__).resolve().parent.parent / "src/augur/features/panel.py"
    chk("writer 已帶通行證(上閘前置;GRID-A 逐 panel 新進程自動生效)",
        "SET LOCAL augur.honesty_write" in src.read_text())
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="feature_values 誠實閘(FV-GUARD)")
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

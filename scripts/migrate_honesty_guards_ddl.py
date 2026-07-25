"""🎯 誠實帳本 DB 閘:trial_ledger / revalidation_baseline 補 trigger 防默改(2026-07-25 hugo 拍板)。

兩表是 DSR 之 N 與凍結錨的機械來源,原零 trigger=最關鍵表最弱防護:刪 trial_ledger 列⇒DSR 虛高不留痕、
UPDATE baseline⇒凍結錨被靜默改寫。本閘:DELETE/TRUNCATE 一律拒(兩表皆無合法路徑);UPDATE 須帶 session
通行證 `SET LOCAL augur.honesty_write='on'`(工具鏈 refresh/freeze 的 ON CONFLICT UPDATE 才放行、裸手拒)。
守原則 #15(誠實)#8(錨不可默移)#12(單一閘住所)。冪等可重跑。

執行指令矩陣:
  python scripts/migrate_honesty_guards_ddl.py              # 安全預設=印本矩陣+--check
  python scripts/migrate_honesty_guards_ddl.py --check      # 唯讀:列兩表現有 trigger 狀態
  python scripts/migrate_honesty_guards_ddl.py --apply      # 建 guard 函式+每表 row/truncate 兩 trigger(冪等)
  python scripts/migrate_honesty_guards_ddl.py --selftest   # 零 DB 純紅綠:SQL 不變式斷言
"""
import sys

import _bootstrap  # noqa: F401
from augur.core import db

TABLES = ("trial_ledger", "revalidation_baseline")
GUC = "augur.honesty_write"

GUARD_FN = f"""
CREATE OR REPLACE FUNCTION honesty_ledger_guard() RETURNS trigger AS $$
BEGIN
    IF TG_OP IN ('DELETE', 'TRUNCATE') THEN
        RAISE EXCEPTION '% on % 遭誠實帳本閘拒絕:無合法路徑(N/凍結錨不可默改,#15)', TG_OP, TG_TABLE_NAME;
    END IF;
    IF TG_OP = 'UPDATE' AND coalesce(current_setting('{GUC}', true), '') <> 'on' THEN
        RAISE EXCEPTION 'UPDATE on % 遭拒:須經工具鏈(SET LOCAL {GUC}=''on'');裸手改寫=默改(#15)', TG_TABLE_NAME;
    END IF;
    RETURN COALESCE(NEW, OLD);
END $$ LANGUAGE plpgsql;
"""


def _trigger_sql(tbl):
    return f"""
DROP TRIGGER IF EXISTS trg_{tbl}_honesty_row ON {tbl};
CREATE TRIGGER trg_{tbl}_honesty_row BEFORE UPDATE OR DELETE ON {tbl}
    FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
DROP TRIGGER IF EXISTS trg_{tbl}_honesty_trunc ON {tbl};
CREATE TRIGGER trg_{tbl}_honesty_trunc BEFORE TRUNCATE ON {tbl}
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard();
"""


def check(conn):
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT c.relname, coalesce(string_agg(t.tgname, ', ' ORDER BY t.tgname), '(無)') "
            "FROM pg_class c LEFT JOIN pg_trigger t ON t.tgrelid = c.oid AND NOT t.tgisinternal "
            "WHERE c.relname = ANY(%s) GROUP BY c.relname ORDER BY c.relname", (list(TABLES),))
        for name, trgs in cur.fetchall():
            print(f"  {name}: {trgs}")
    return 0


def apply(conn):
    with db.transaction(conn) as cur:
        cur.execute(GUARD_FN)
        for tbl in TABLES:
            cur.execute(_trigger_sql(tbl))
    print("✓ honesty guards applied(冪等)")
    return check(conn)


def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    chk("guard 函式含 DELETE/TRUNCATE 無條件拒", "IF TG_OP IN ('DELETE', 'TRUNCATE')" in GUARD_FN)
    chk("guard 函式 UPDATE 綁 GUC 通行證", GUC in GUARD_FN and "TG_OP = 'UPDATE'" in GUARD_FN)
    chk("兩表皆覆蓋", all(tbl in ("".join(_trigger_sql(t) for t in TABLES)) for tbl in TABLES))
    for t in TABLES:
        s = _trigger_sql(t)
        chk(f"{t}: row 級(UPDATE OR DELETE)+statement 級(TRUNCATE)雙 trigger", "FOR EACH ROW" in s and "FOR EACH STATEMENT" in s)
        chk(f"{t}: 冪等(DROP IF EXISTS)", s.count("DROP TRIGGER IF EXISTS") == 2)
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    with db.connect() as conn:
        if "--apply" in argv:
            return apply(conn)
        if "--check" in argv:
            return check(conn)
        print(__doc__)
        print("現況(--check):")
        return check(conn)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

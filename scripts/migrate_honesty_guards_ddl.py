"""🎯 誠實帳本 DB 閘:trial_ledger / revalidation_baseline + PME 八表 補 trigger 防默改。

兩帳本表(2026-07-25 hugo 拍板):DSR 之 N 與凍結錨的機械來源——DELETE/TRUNCATE 一律拒;UPDATE 須帶
session 通行證 `SET LOCAL augur.honesty_write='on'`(工具鏈 ON CONFLICT UPDATE 才放行、裸手拒)。

**PME 八表(V2 Phase 2.3/C5,2026-07-26 hugo 拍板 V2-HONESTY-go)**:唯一由引擎自動寫入、decided_by
全為 'evolution_engine' 的帳本原本零閘(標準顛倒——§1.4)。掛**只擋 DELETE/TRUNCATE** 之 guard;
**刻意不做 UPDATE-GUC**——C5 裁決:GUC 對唯一自動寫入者(apply 引擎自行 SET LOCAL)豁免=閘只擋人不擋引擎;
且 prodset 走 ON CONFLICT DO UPDATE,GUC 版會使同一特徵首次 APPLY 過、再次死,單次測試驗不出。
要管 UPDATE 走「追加修訂列+superseded_by」不走 GUC。P4.E3 在 PME 側首次機械落地。冪等可重跑。
守原則 #15(誠實)#8(錨不可默移)#12(單一閘住所)。

執行指令矩陣:
  python scripts/migrate_honesty_guards_ddl.py              # 安全預設=印本矩陣+--check
  python scripts/migrate_honesty_guards_ddl.py --check      # 唯讀:列全部覆蓋表現有 trigger 狀態
  python scripts/migrate_honesty_guards_ddl.py --apply      # 建 guard 函式+每表 trigger(冪等)
  python scripts/migrate_honesty_guards_ddl.py --selftest   # 零 DB 純紅綠:SQL 不變式斷言
"""
import sys

import _bootstrap  # noqa: F401
from augur.core import db

TABLES = ("trial_ledger", "revalidation_baseline")
# PME 側(V2 Phase 2.3):§1.4 盤點之全部無閘表(6 evolution + 2 philosophy 判準表);
# repo 全掃無任何合法 DELETE 路徑(2026-07-26 實查),delete-only 閘零誤傷。
PME_TABLES = ("evolution_run", "evolution_coverage_snapshot", "promotion_queue", "evolution_apply_log",
              "evolution_production_feature_set", "evolution_kill_switch",
              "principle_factor_map", "philosophy_principle")
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


DELETE_ONLY_FN = """
CREATE OR REPLACE FUNCTION honesty_delete_only_guard() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION '% on % 遭誠實帳本閘拒絕:append-only(P4.E3 只失效不刪除);要改走追加修訂列,不裸刪',
        TG_OP, TG_TABLE_NAME;
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


def _delete_only_sql(tbl):
    """PME 側:只擋 DELETE/TRUNCATE;UPDATE 自由(引擎 ON CONFLICT DO UPDATE / kill-switch set_state 之合法路徑)。"""
    return f"""
DROP TRIGGER IF EXISTS trg_{tbl}_delonly_row ON {tbl};
CREATE TRIGGER trg_{tbl}_delonly_row BEFORE DELETE ON {tbl}
    FOR EACH ROW EXECUTE FUNCTION honesty_delete_only_guard();
DROP TRIGGER IF EXISTS trg_{tbl}_delonly_trunc ON {tbl};
CREATE TRIGGER trg_{tbl}_delonly_trunc BEFORE TRUNCATE ON {tbl}
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_delete_only_guard();
"""


def check(conn):
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT c.relname, coalesce(string_agg(t.tgname, ', ' ORDER BY t.tgname), '(無)') "
            "FROM pg_class c LEFT JOIN pg_trigger t ON t.tgrelid = c.oid AND NOT t.tgisinternal "
            "WHERE c.relname = ANY(%s) GROUP BY c.relname ORDER BY c.relname",
            (list(TABLES) + list(PME_TABLES),))
        for name, trgs in cur.fetchall():
            print(f"  {name}: {trgs}")
    return 0


def apply(conn):
    with db.transaction(conn) as cur:
        cur.execute(GUARD_FN)
        for tbl in TABLES:
            cur.execute(_trigger_sql(tbl))
        cur.execute(DELETE_ONLY_FN)
        for tbl in PME_TABLES:
            cur.execute(_delete_only_sql(tbl))
    print(f"✓ honesty guards applied(冪等):帳本雙閘 {len(TABLES)} 表 + PME delete-only {len(PME_TABLES)} 表")
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
    # V2 Phase 2.3(C5)增項
    chk("PME 閘=獨立 delete-only 函式(**不含** UPDATE-GUC 分支——C5:GUC 對引擎豁免+首過再死)",
        "honesty_delete_only_guard" in DELETE_ONLY_FN and "UPDATE" not in DELETE_ONLY_FN and GUC not in DELETE_ONLY_FN)
    chk("PME 八表全覆蓋(§1.4 盤點之無閘表)", len(PME_TABLES) == 8
        and all(t in "".join(_delete_only_sql(x) for x in PME_TABLES) for t in PME_TABLES))
    for t in PME_TABLES:
        s = _delete_only_sql(t)
        chk(f"{t}: DELETE row 級+TRUNCATE statement 級、**無 UPDATE trigger**",
            "BEFORE DELETE ON" in s and "BEFORE TRUNCATE ON" in s and "UPDATE" not in s.split("$$")[0])
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

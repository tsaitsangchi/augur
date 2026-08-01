"""🎯 誠實帳本 DB 閘:trial_ledger / revalidation_baseline + PME 表群 + B4 P0 四表 補 trigger 防默改。

兩帳本表(2026-07-25 hugo 拍板):DSR 之 N 與凍結錨的機械來源——DELETE/TRUNCATE 一律拒;UPDATE 須帶
session 通行證 `SET LOCAL augur.honesty_write='on'`(工具鏈 ON CONFLICT UPDATE 才放行、裸手拒)。

**PME 表群(V2 Phase 2.3/C5,2026-07-26 hugo 拍板 V2-HONESTY-go)**:唯一由引擎自動寫入、decided_by
全為 'evolution_engine' 的帳本原本零閘(標準顛倒——§1.4)。掛**只擋 DELETE/TRUNCATE** 之 guard;
**刻意不做 UPDATE-GUC**——C5 裁決:GUC 對唯一自動寫入者(apply 引擎自行 SET LOCAL)豁免=閘只擋人不擋引擎;
且 prodset 走 ON CONFLICT DO UPDATE,GUC 版會使同一特徵首次 APPLY 過、再次死,單次測試驗不出。
要管 UPDATE 走「追加修訂列+superseded_by」不走 GUC。P4.E3 在 PME 側首次機械落地。冪等可重跑。

**B4 部分翻案(2026-08-01 Steward 圈選甲案;RULING 編號待 Steward 指配)**:GUC_TABLES_P0 四表
(pfm/pp/prodset 自 delete-only 升級 + feature_sign_check 新掛)改掛 honesty_ledger_guard——
07-31 單一角色整併後 DB 層 role 縱深不存,「擋裸手」成僅存 DB 層價值(半閘:意圖留痕+防手滑,
**非**硬閘——C5「GUC 對引擎豁免」之警告全數保留,不得引為已機械防引擎默改)。寫入者通行證補丁
先合入、DDL 後行(消滅 C5 理由②首過再死);C5 對其餘 delete-only 表(PME 5 表+P2 殘餘)效力不變。
升級 DDL 逐表獨立交易+`SET LOCAL lock_timeout='5s'`(#30 鎖紀律:拿不到即 abort 不排隊)。
守原則 #15(誠實)#8(錨不可默移)#12(單一閘住所)。

執行指令矩陣:
  python scripts/migrate_honesty_guards_ddl.py              # 安全預設=印本矩陣+--check
  python scripts/migrate_honesty_guards_ddl.py --check      # 唯讀:列全部覆蓋表現有 trigger 狀態
  python scripts/migrate_honesty_guards_ddl.py --apply      # 建 guard 函式+每表 trigger(冪等;含 B4 四表升級)
  python scripts/migrate_honesty_guards_ddl.py --selftest   # 零 DB 純紅綠:SQL 不變式斷言
"""
import sys

import _bootstrap  # noqa: F401
from augur.core import db

TABLES = ("trial_ledger", "revalidation_baseline")
# PME 側(V2 Phase 2.3):§1.4 盤點之無閘表,repo 全掃無任何合法 DELETE 路徑(2026-07-26 實查),
# delete-only 閘零誤傷。B4(2026-08-01)遷出 principle_factor_map/philosophy_principle/
# evolution_production_feature_set → GUC_TABLES_P0 升級 UPDATE-GUC;本組餘 5 表維持 C5 delete-only。
PME_TABLES = ("evolution_run", "evolution_coverage_snapshot", "promotion_queue", "evolution_apply_log",
              "evolution_kill_switch")
# B4 P0 四表(3 升級+1 新掛):晉升鏈判準四要害——方向基準(pfm.direction)/原則 status(pp)/
# prodset SSOT(set_status)/符號 verdict(feature_sign_check,07-31 A1 建表後原零 trigger)。
GUC_TABLES_P0 = ("principle_factor_map", "philosophy_principle",
                 "evolution_production_feature_set", "feature_sign_check")
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


def _upgrade_sql(tbl):
    """B4:一表升級 UPDATE-GUC 閘——卸 delonly 雙名(feature_sign_check 本無,IF EXISTS 安全)再掛
    honesty 雙 trigger;同交易=原子換閘無空窗。呼叫端須逐表獨立交易(#30:單表 abort 不連坐)。"""
    return f"""
SET LOCAL lock_timeout = '5s';
DROP TRIGGER IF EXISTS trg_{tbl}_delonly_row   ON {tbl};
DROP TRIGGER IF EXISTS trg_{tbl}_delonly_trunc ON {tbl};
DROP TRIGGER IF EXISTS trg_{tbl}_honesty_row   ON {tbl};
DROP TRIGGER IF EXISTS trg_{tbl}_honesty_trunc ON {tbl};
CREATE TRIGGER trg_{tbl}_honesty_row BEFORE UPDATE OR DELETE ON {tbl}
    FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
CREATE TRIGGER trg_{tbl}_honesty_trunc BEFORE TRUNCATE ON {tbl}
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard()
"""


def check(conn):
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT c.relname, coalesce(string_agg(t.tgname, ', ' ORDER BY t.tgname), '(無)') "
            "FROM pg_class c LEFT JOIN pg_trigger t ON t.tgrelid = c.oid AND NOT t.tgisinternal "
            "WHERE c.relname = ANY(%s) GROUP BY c.relname ORDER BY c.relname",
            (list(TABLES) + list(PME_TABLES) + list(GUC_TABLES_P0),))
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
    # B4:P0 四表逐表獨立交易(交易首句 SET LOCAL lock_timeout='5s'——5 秒拿不到 ACCESS EXCLUSIVE
    # 即 abort 不排隊;排隊中的 EXCLUSIVE 會擋全庫後續查詢,07-03 鎖風暴教訓 #30)
    for tbl in GUC_TABLES_P0:
        with db.transaction(conn) as cur:
            cur.execute(_upgrade_sql(tbl))
    print(f"✓ honesty guards applied(冪等):帳本雙閘 {len(TABLES)} 表 + PME delete-only {len(PME_TABLES)} 表"
          f" + B4 UPDATE-GUC {len(GUC_TABLES_P0)} 表")
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
    chk("PME 五表覆蓋(§1.4 盤點-B4 遷出三表;C5 delete-only 於此組效力不變)", len(PME_TABLES) == 5
        and all(t in "".join(_delete_only_sql(x) for x in PME_TABLES) for t in PME_TABLES))
    for t in PME_TABLES:
        s = _delete_only_sql(t)
        chk(f"{t}: DELETE row 級+TRUNCATE statement 級、**無 UPDATE trigger**",
            "BEFORE DELETE ON" in s and "BEFORE TRUNCATE ON" in s and "UPDATE" not in s.split("$$")[0])
    # —— B4 增項(2026-08-01;新斷言依 #35 先驗紅,紅證=audits/B4-UPDATE-GUC-RED-20260801.md) ——
    chk("B4:P0 四表=pfm/pp/prodset/feature_sign_check 且與 PME delete-only 組互斥",
        set(GUC_TABLES_P0) == {"principle_factor_map", "philosophy_principle",
                               "evolution_production_feature_set", "feature_sign_check"}
        and not (set(GUC_TABLES_P0) & set(PME_TABLES)))
    for t in GUC_TABLES_P0:
        stmts = [x.strip() for x in _upgrade_sql(t).split(";") if x.strip()]
        drops = [x for x in stmts if x.startswith("DROP TRIGGER IF EXISTS")]
        creates = [x for x in stmts if x.startswith("CREATE TRIGGER")]
        chk(f"{t}: 交易首句 SET LOCAL lock_timeout='5s'(#30 不排隊)",
            bool(stmts) and stmts[0] == "SET LOCAL lock_timeout = '5s'")
        chk(f"{t}: 卸 delonly+honesty 四名(全 IF EXISTS 冪等)再掛 honesty 雙 trigger",
            len(drops) == 4 and sum("_delonly_" in d for d in drops) == 2 and len(creates) == 2)
        row_trg = next((c for c in creates if f"trg_{t}_honesty_row" in c), "")
        chk(f"{t}: row 閘=BEFORE UPDATE OR DELETE→honesty_ledger_guard(UPDATE 綁 GUC)",
            "BEFORE UPDATE OR DELETE ON" in row_trg and "honesty_ledger_guard()" in row_trg)
        trunc_trg = next((c for c in creates if f"trg_{t}_honesty_trunc" in c), "")
        chk(f"{t}: TRUNCATE statement 閘在且同函式",
            "BEFORE TRUNCATE ON" in trunc_trg and "FOR EACH STATEMENT" in trunc_trg
            and "honesty_ledger_guard()" in trunc_trg)
        chk(f"{t}: 先 DROP 後 CREATE(同交易原子換閘無空窗)",
            bool(drops) and bool(creates) and stmts.index(drops[-1]) < stmts.index(creates[0]))
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

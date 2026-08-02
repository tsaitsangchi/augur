"""🎯 誠實帳本 DB 閘:trial_ledger / revalidation_baseline + PME 表群 + B4 P0 四表 補 trigger 防默改。

兩帳本表(2026-07-25 hugo 拍板):DSR 之 N 與凍結錨的機械來源——DELETE/TRUNCATE 一律拒;UPDATE 須帶
session 通行證 `SET LOCAL augur.honesty_write='on'`(工具鏈 ON CONFLICT UPDATE 才放行、裸手拒)。

**PME 表群(V2 Phase 2.3/C5,2026-07-26 hugo 拍板 V2-HONESTY-go)**:唯一由引擎自動寫入、decided_by
全為 'evolution_engine' 的帳本原本零閘(標準顛倒——§1.4)。掛**只擋 DELETE/TRUNCATE** 之 guard;
**刻意不做 UPDATE-GUC**——C5 裁決:GUC 對唯一自動寫入者(apply 引擎自行 SET LOCAL)豁免=閘只擋人不擋引擎;
且 prodset 走 ON CONFLICT DO UPDATE,GUC 版會使同一特徵首次 APPLY 過、再次死,單次測試驗不出。
要管 UPDATE 走「追加修訂列+superseded_by」不走 GUC。P4.E3 在 PME 側首次機械落地。冪等可重跑。

**B4 部分翻案(2026-08-01 Steward 圈選甲案;RULING-2026-043,hugo 指配「B4-043」)**:GUC_TABLES_P0 四表
(pfm/pp/prodset 自 delete-only 升級 + feature_sign_check 新掛)改掛 honesty_ledger_guard——
07-31 單一角色整併後 DB 層 role 縱深不存,「擋裸手」成僅存 DB 層價值(半閘:意圖留痕+防手滑,
**非**硬閘——C5「GUC 對引擎豁免」之警告全數保留,不得引為已機械防引擎默改)。寫入者通行證補丁
先合入、DDL 後行(消滅 C5 理由②首過再死);C5 對其餘 delete-only 表(PME 5 表+P2 殘餘)效力不變。
升級 DDL 逐表獨立交易+`SET LOCAL lock_timeout='5s'`(#30 鎖紀律:拿不到即 abort 不排隊)。

**B4-P2a(2026-08-01 Steward 圈選「P2a-同意+§5-乙」,編號併 RULING-2026-043)**:GUC_TABLES_P2A 五表
(promotion_queue/steward_question_ledger/evolution_hypothesis_hint=治權欄默改代價最高三表,
evolution_apply_log/evolution_evidence_run=零寫入者白撿)自 delete-only 升級 honesty_ledger_guard。
**evolution_kill_switch 依 §5 乙案排除**——緊急煞車之裸 psql 解除路徑零摩擦優先於閘完整性,
維持 delete-only(否決可達性 #26 OCV 不弱化)。legacy 自訂名(hint_no_*/evidence_no_*,live pg_trigger
親驗 2026-08-01)逐名列 LEGACY_TRIGGERS、同交易先卸盡再掛=原子換閘;hint 之 hint_decision_forward_only
係獨立 domain 閘(decision 單向前進)**不卸**。P2c sim 七表緩議(住所歸 sim 專章)。

**B4-P2b(2026-08-02 Steward 圈選「P2b-同意、run 21 結輪後開窗」,編號併 RULING-2026-043;
run 21 已 2026-08-02 04:11 succeeded 親驗)**:GUC_TABLES_P2B 六表(evolution_run/
evolution_iteration_ledger/raw_evolution_iteration_ledger=引擎 run/迭代帳本,
evolution_coverage_snapshot/local_ai_iteration_ledger=零寫入者白撿,mc_simulation_run=三處
upsert 衝突分支)自 delete-only 升級 honesty_ledger_guard。live pg_trigger 親驗(2026-08-02)
六表全數僅掛 delete-only、UPDATE 面全裸——無「已閘表」須剔除;legacy 實名=tw_iter_no_*/
raw_iter_no_*/lai_iter_no_*/mcsim_no_*(mcsim 無 _row 後綴,勿抄標準名)。寫入者通行證 10 點
先合(run_philosophy_evolution×2/run_evolution_iteration×2/run_raw_evolution_iteration×1/
audit_philosophy_feature_coverage×1/backfill_evolution_run_zombies×1/simulate_mc_paths×1/
simulate_portfolio_risk×2)、DDL 後行。原住所同步:evolution_ledger_ddl(三 ledger)/
migrate_sim_evolution_ddl(M3)改產 honesty 版防掛回。
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
# evolution_production_feature_set → GUC_TABLES_P0;B4-P2a(RULING-2026-043 併案)再遷出
# promotion_queue/evolution_apply_log → GUC_TABLES_P2A;B4-P2b(2026-08-02)再遷出
# evolution_run/evolution_coverage_snapshot → GUC_TABLES_P2B(防 --apply 重掛 delete-only)。
# evolution_kill_switch §5 乙案明文留守 delete-only(緊急煞車零摩擦)——**絕不遷**。
PME_TABLES = ("evolution_kill_switch",)
# B4 P0 四表(3 升級+1 新掛):晉升鏈判準四要害——方向基準(pfm.direction)/原則 status(pp)/
# prodset SSOT(set_status)/符號 verdict(feature_sign_check,07-31 A1 建表後原零 trigger)。
GUC_TABLES_P0 = ("principle_factor_map", "philosophy_principle",
                 "evolution_production_feature_set", "feature_sign_check")
# B4-P2a 五表(2026-08-01「P2a-同意+§5-乙」併 RULING-2026-043;呈案=reports/w2_20260801/
# B4P2_remaining_tables_proposal.md §4):queue 決議/治理答案/人簽欄+二白撿;kill_switch 排除見 §5 乙。
GUC_TABLES_P2A = ("promotion_queue", "steward_question_ledger", "evolution_hypothesis_hint",
                  "evolution_apply_log", "evolution_evidence_run")
# B4-P2b 六表(2026-08-02「P2b-同意、run 21 結輪後開窗」併 RULING-2026-043;呈案=reports/w2_20260801/
# B4P2_remaining_tables_proposal.md §4):引擎 run/迭代帳本+二白撿+mc upsert;kill_switch 仍 §5 乙留守。
GUC_TABLES_P2B = ("evolution_run", "evolution_iteration_ledger", "raw_evolution_iteration_ledger",
                  "evolution_coverage_snapshot", "local_ai_iteration_ledger", "mc_simulation_run")
# P2a/P2b legacy trigger 名映射(live pg_trigger 親驗 2026-08-01/08-02;呈案 §2.4 之自訂名):非標準
# delonly 名者逐名列此,_upgrade_sql 同交易先卸盡(全 IF EXISTS 冪等)再掛 honesty 雙 trigger=原子換閘
# 無空窗。hint 之 hint_decision_forward_only=獨立 domain 閘(decision 單向前進,evolution_ledger_ddl
# 住所)——不在卸列。evolution_run/evolution_coverage_snapshot 為標準 trg_<t>_delonly_* 名=免列。
# mcsim 實名無 _row 後綴(mcsim_no_delete 非 mcsim_no_delete_row)——照 live 不照猜名。
LEGACY_TRIGGERS = {
    "evolution_hypothesis_hint": ("hint_no_delete", "hint_no_truncate"),
    "evolution_evidence_run": ("evidence_no_delete", "evidence_no_truncate"),
    "evolution_iteration_ledger": ("tw_iter_no_delete_row", "tw_iter_no_truncate"),
    "raw_evolution_iteration_ledger": ("raw_iter_no_delete_row", "raw_iter_no_truncate"),
    "local_ai_iteration_ledger": ("lai_iter_no_delete_row", "lai_iter_no_truncate"),
    "mc_simulation_run": ("mcsim_no_delete", "mcsim_no_truncate"),
}
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
    """B4:一表升級 UPDATE-GUC 閘——卸 delonly 雙名(feature_sign_check 本無,IF EXISTS 安全)
    +該表 legacy 自訂名(LEGACY_TRIGGERS;P2a)再掛 honesty 雙 trigger;同交易=原子換閘無空窗。
    呼叫端須逐表獨立交易(#30:單表 abort 不連坐)。"""
    legacy = "".join(f"DROP TRIGGER IF EXISTS {name} ON {tbl};\n"
                     for name in LEGACY_TRIGGERS.get(tbl, ()))
    return f"""
SET LOCAL lock_timeout = '5s';
{legacy}DROP TRIGGER IF EXISTS trg_{tbl}_delonly_row   ON {tbl};
DROP TRIGGER IF EXISTS trg_{tbl}_delonly_trunc ON {tbl};
DROP TRIGGER IF EXISTS trg_{tbl}_honesty_row   ON {tbl};
DROP TRIGGER IF EXISTS trg_{tbl}_honesty_trunc ON {tbl};
CREATE TRIGGER trg_{tbl}_honesty_row BEFORE UPDATE OR DELETE ON {tbl}
    FOR EACH ROW EXECUTE FUNCTION honesty_ledger_guard();
CREATE TRIGGER trg_{tbl}_honesty_trunc BEFORE TRUNCATE ON {tbl}
    FOR EACH STATEMENT EXECUTE FUNCTION honesty_ledger_guard()
"""


def _registry_problems(tables, pme, p0, p2a, p2b, legacy):
    """表集互斥+legacy 映射鍵完整之純函式檢核(#35);回傳問題清單(空=通過)。
    selftest 以現行常數驗綠、以壞變體驗紅——集合重疊/重複/映射懸空任一即非空。"""
    problems = []
    groups = (("TABLES", tables), ("PME_TABLES", pme),
              ("GUC_TABLES_P0", p0), ("GUC_TABLES_P2A", p2a), ("GUC_TABLES_P2B", p2b))
    for name, g in groups:
        if len(set(g)) != len(g):
            problems.append(f"{name} 內含重複")
    for i, (na, ga) in enumerate(groups):
        for nb, gb in groups[i + 1:]:
            overlap = set(ga) & set(gb)
            if overlap:
                problems.append(f"{na}∩{nb}≠∅:{sorted(overlap)}")
    for key in legacy:
        if key not in p2a and key not in p2b:
            problems.append(f"LEGACY_TRIGGERS 鍵 {key} 不在 GUC_TABLES_P2A/P2B(映射懸空)")
    return problems


def check(conn):
    with db.transaction(conn) as cur:
        cur.execute(
            "SELECT c.relname, coalesce(string_agg(t.tgname, ', ' ORDER BY t.tgname), '(無)') "
            "FROM pg_class c LEFT JOIN pg_trigger t ON t.tgrelid = c.oid AND NOT t.tgisinternal "
            "WHERE c.relname = ANY(%s) GROUP BY c.relname ORDER BY c.relname",
            (list(TABLES) + list(PME_TABLES) + list(GUC_TABLES_P0)
             + list(GUC_TABLES_P2A) + list(GUC_TABLES_P2B),))
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
    # B4:P0+P2a 表逐表獨立交易(交易首句 SET LOCAL lock_timeout='5s'——5 秒拿不到 ACCESS EXCLUSIVE
    # 即 abort 不排隊;排隊中的 EXCLUSIVE 會擋全庫後續查詢,07-03 鎖風暴教訓 #30)
    for tbl in GUC_TABLES_P0 + GUC_TABLES_P2A + GUC_TABLES_P2B:
        with db.transaction(conn) as cur:
            cur.execute(_upgrade_sql(tbl))
    print(f"✓ honesty guards applied(冪等):帳本雙閘 {len(TABLES)} 表 + PME delete-only {len(PME_TABLES)} 表"
          f" + B4 UPDATE-GUC {len(GUC_TABLES_P0)} 表 + B4-P2a {len(GUC_TABLES_P2A)} 表"
          f" + B4-P2b {len(GUC_TABLES_P2B)} 表")
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
    chk("PME 僅餘 kill_switch(B4 遷出三表+P2a 遷出二表+P2b 遷出二表;§5 乙案明文留守、絕不遷)",
        PME_TABLES == ("evolution_kill_switch",)
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
    # —— B4-P2a 增項(2026-08-01;RULING-2026-043 併案;#35 先驗紅,紅證=audits/B4-P2A-UPDATE-GUC-RED-20260801.md) ——
    chk("P2a:五表凍結=promotion_queue/steward_question_ledger/evolution_hypothesis_hint/"
        "evolution_apply_log/evolution_evidence_run",
        set(GUC_TABLES_P2A) == {"promotion_queue", "steward_question_ledger",
                                "evolution_hypothesis_hint", "evolution_apply_log",
                                "evolution_evidence_run"})
    chk("P2a:kill_switch 明文留守 PME delete-only(§5 乙案=緊急煞車零摩擦,不上 GUC)",
        "evolution_kill_switch" in PME_TABLES and "evolution_kill_switch" not in GUC_TABLES_P2A)
    chk("五表集互斥+legacy 映射鍵完整(_registry_problems 純函式=空)",
        _registry_problems(TABLES, PME_TABLES, GUC_TABLES_P0, GUC_TABLES_P2A,
                           GUC_TABLES_P2B, LEGACY_TRIGGERS) == [])
    chk("壞變體驗紅:PME 誤含 promotion_queue(重疊)須被抓",
        _registry_problems(TABLES, PME_TABLES + ("promotion_queue",), GUC_TABLES_P0,
                           GUC_TABLES_P2A, GUC_TABLES_P2B, LEGACY_TRIGGERS) != [])
    chk("壞變體驗紅:legacy 鍵懸空(不在 P2A/P2B)須被抓",
        _registry_problems(TABLES, PME_TABLES, GUC_TABLES_P0, GUC_TABLES_P2A, GUC_TABLES_P2B,
                           {"sim_llm_proposal": ("x_no_delete",)}) != [])
    chk("壞變體驗紅:PME 誤含 evolution_run(P2b 遷出後回流=重疊)須被抓",
        _registry_problems(TABLES, PME_TABLES + ("evolution_run",), GUC_TABLES_P0,
                           GUC_TABLES_P2A, GUC_TABLES_P2B, LEGACY_TRIGGERS) != [])
    hint_sql = _upgrade_sql("evolution_hypothesis_hint")
    chk("hint:卸 legacy 名 hint_no_delete+hint_no_truncate(live pg_trigger 親驗名 2026-08-01)",
        "DROP TRIGGER IF EXISTS hint_no_delete ON" in hint_sql
        and "DROP TRIGGER IF EXISTS hint_no_truncate ON" in hint_sql)
    chk("hint:不卸 hint_decision_forward_only(獨立 domain 閘=decision 單向前進,非 delonly)",
        "hint_decision_forward_only" not in hint_sql)
    ev_sql = _upgrade_sql("evolution_evidence_run")
    chk("evidence:卸 legacy 名 evidence_no_delete+evidence_no_truncate(live 親驗名)",
        "DROP TRIGGER IF EXISTS evidence_no_delete ON" in ev_sql
        and "DROP TRIGGER IF EXISTS evidence_no_truncate ON" in ev_sql)
    for t in GUC_TABLES_P2A:
        stmts = [x.strip() for x in _upgrade_sql(t).split(";") if x.strip()]
        drops = [x for x in stmts if x.startswith("DROP TRIGGER IF EXISTS")]
        creates = [x for x in stmts if x.startswith("CREATE TRIGGER")]
        n_legacy = len(LEGACY_TRIGGERS.get(t, ()))
        chk(f"{t}: 首句 lock_timeout+卸 {4 + n_legacy} 名(標準4+legacy{n_legacy})+先卸後掛",
            bool(stmts) and stmts[0] == "SET LOCAL lock_timeout = '5s'"
            and len(drops) == 4 + n_legacy and len(creates) == 2
            and stmts.index(drops[-1]) < stmts.index(creates[0]))
        row_trg = next((c for c in creates if f"trg_{t}_honesty_row" in c), "")
        trunc_trg = next((c for c in creates if f"trg_{t}_honesty_trunc" in c), "")
        chk(f"{t}: row 閘=BEFORE UPDATE OR DELETE→honesty_ledger_guard+TRUNCATE statement 閘同函式",
            "BEFORE UPDATE OR DELETE ON" in row_trg and "honesty_ledger_guard()" in row_trg
            and "BEFORE TRUNCATE ON" in trunc_trg and "FOR EACH STATEMENT" in trunc_trg
            and "honesty_ledger_guard()" in trunc_trg)
    # —— B4-P2b 增項(2026-08-02;RULING-2026-043 併案;#35 先驗紅,紅證=audits/B4-P2B-UPDATE-GUC-RED-20260802.md) ——
    chk("P2b:六表凍結=evolution_run/evolution_iteration_ledger/raw_evolution_iteration_ledger/"
        "evolution_coverage_snapshot/local_ai_iteration_ledger/mc_simulation_run",
        set(GUC_TABLES_P2B) == {"evolution_run", "evolution_iteration_ledger",
                                "raw_evolution_iteration_ledger", "evolution_coverage_snapshot",
                                "local_ai_iteration_ledger", "mc_simulation_run"})
    for t, names in (("evolution_iteration_ledger", ("tw_iter_no_delete_row", "tw_iter_no_truncate")),
                     ("raw_evolution_iteration_ledger", ("raw_iter_no_delete_row", "raw_iter_no_truncate")),
                     ("local_ai_iteration_ledger", ("lai_iter_no_delete_row", "lai_iter_no_truncate")),
                     ("mc_simulation_run", ("mcsim_no_delete", "mcsim_no_truncate"))):
        s = _upgrade_sql(t)
        chk(f"{t}: 卸 legacy 實名 {names[0]}+{names[1]}(live pg_trigger 親驗 2026-08-02;mcsim 無 _row 後綴)",
            all(f"DROP TRIGGER IF EXISTS {n} ON" in s for n in names))
    chk("P2b:evolution_run/coverage_snapshot 標準 delonly 名、不入 legacy 映射(標準 DROP 已涵蓋)",
        "evolution_run" not in LEGACY_TRIGGERS and "evolution_coverage_snapshot" not in LEGACY_TRIGGERS)
    for t in GUC_TABLES_P2B:
        stmts = [x.strip() for x in _upgrade_sql(t).split(";") if x.strip()]
        drops = [x for x in stmts if x.startswith("DROP TRIGGER IF EXISTS")]
        creates = [x for x in stmts if x.startswith("CREATE TRIGGER")]
        n_legacy = len(LEGACY_TRIGGERS.get(t, ()))
        chk(f"{t}: 首句 lock_timeout+卸 {4 + n_legacy} 名(標準4+legacy{n_legacy})+先卸後掛",
            bool(stmts) and stmts[0] == "SET LOCAL lock_timeout = '5s'"
            and len(drops) == 4 + n_legacy and len(creates) == 2
            and stmts.index(drops[-1]) < stmts.index(creates[0]))
        row_trg = next((c for c in creates if f"trg_{t}_honesty_row" in c), "")
        trunc_trg = next((c for c in creates if f"trg_{t}_honesty_trunc" in c), "")
        chk(f"{t}: row 閘=BEFORE UPDATE OR DELETE→honesty_ledger_guard+TRUNCATE statement 閘同函式",
            "BEFORE UPDATE OR DELETE ON" in row_trg and "honesty_ledger_guard()" in row_trg
            and "BEFORE TRUNCATE ON" in trunc_trg and "FOR EACH STATEMENT" in trunc_trg
            and "honesty_ledger_guard()" in trunc_trg)
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

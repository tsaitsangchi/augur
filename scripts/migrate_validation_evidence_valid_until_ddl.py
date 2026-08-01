#!/usr/bin/env python3
"""🎯 manual 型證據有效期 DDL——validation_evidence 加 valid_until＋存量回填＋CHECK 閉合（C1 甲案）。

守原則 #6（--apply/--backfill/--add-check 才動 DB；全段冪等可重跑）、#15（「人裁綠永久免疫」
之免疫消失＝紅燈會亮；selftest 以 sqlite 真表＋壞變體驗紅 #35）、#29a/d、#30（lock_timeout 5s
絕不排隊；dump 期間禁跑）。

內容（SSOT＝reports/w2_20260801/C1_manual_validity.md §3.1；Steward 裁決 2026-08-01
「90 天＋green/amber→unverified 降轉＋CHECK 閉合三旋鈕照甲案」）：
  DDL-1 --apply    ：ADD COLUMN IF NOT EXISTS valid_until timestamptz＋欄註（冪等）
  DDL-2 --backfill ：存量 manual 列 valid_until = COALESCE(last_verified_at, created_at)+90 天
                     ——以各列**實際簽核時戳**起算、不補造時戳；只補 NULL（冪等）。
                     現值代入之預期到期日：E2/E5/E7＝2026-10-10、E3/E4_gm＝2026-10-09。
  DDL-3 --add-check：ADD CONSTRAINT chk_ve_manual_expiry——「manual green/amber 而無有效期」
                     結構性不可能；**必在 --backfill 之後**（本支以違例前掃機械擋、違序 fail loud）。

**排窗紀律**：本支屬「備妥不跑」——執行歸主 session（hugo 確認；dump 期間禁 DDL #30）。
**同批 code diff（本支不改碼）**：verify_validation_evidence.py --run 過期自動轉 unverified
  （欄未就位時 graceful 走舊行為＋警示，cron 不因 DDL 時序斷炊）；重簽=hugo TTY 親跑
  （範本見呈案 §3.3），本支不代填人簽。
**誠實記載**：該表 trigger=0——任何寫入者可自延 valid_until 屬殘餘風險（DB 層防護歸 B4 射程）。

執行指令矩陣
------------
    python scripts/migrate_validation_evidence_valid_until_ddl.py             # 無參數=--check（唯讀）
    python scripts/migrate_validation_evidence_valid_until_ddl.py --check     # 唯讀：欄/CHECK/manual 各列效期
    python scripts/migrate_validation_evidence_valid_until_ddl.py --apply     # DDL-1 加欄（冪等）
    python scripts/migrate_validation_evidence_valid_until_ddl.py --backfill  # DDL-2 存量回填（只補 NULL）
    python scripts/migrate_validation_evidence_valid_until_ddl.py --add-check # DDL-3 CHECK 閉合（須在 backfill 後）
    python scripts/migrate_validation_evidence_valid_until_ddl.py --selftest  # 紅綠自測（免 DB 免 API；sqlite 真表）
"""

from __future__ import annotations

import argparse
import sqlite3
import sys

import _bootstrap  # noqa: F401

TABLE = "validation_evidence"
COL = "valid_until"
DAYS = 90  # Steward 拍板（甲案）；放寬 180 之證偽條件見呈案 §4——須新裁決，不設 CLI 旋鈕
CONSTRAINT = "chk_ve_manual_expiry"

# 三個共用謂詞常數：pg 端與 sqlite 自測跑**同一字串**（composition-by-construction，
# 改謂詞必同時改到自測所驗之物——謂詞漂移無處可藏）。
CHECK_EXPR = ("check_type <> 'manual' OR status NOT IN ('green','amber') "
              f"OR {COL} IS NOT NULL")
BACKFILL_WHERE = f"check_type='manual' AND {COL} IS NULL"
BASIS_EXPR = "COALESCE(last_verified_at, created_at)"  # 起算=實際簽核時戳,不補造

DDL_APPLY = f"""
SET lock_timeout = '5s';
ALTER TABLE {TABLE} ADD COLUMN IF NOT EXISTS {COL} timestamptz;
COMMENT ON COLUMN {TABLE}.{COL} IS
  'manual 型有效期(C1 2026-08-01):過期由 verify_validation_evidence --run 自動轉 unverified'
  '(green/amber→unverified;red 不動——紅比未驗更誠實);重簽=hugo 更新 status+last_verified_at+valid_until;'
  'sql/script_exit 型恆 NULL(每跑重驗、無效期概念)';
"""

SQL_BACKFILL = (f"UPDATE {TABLE} SET {COL} = {BASIS_EXPR} + interval '{DAYS} days' "
                f"WHERE {BACKFILL_WHERE}")

DDL_ADD_CHECK = (f"SET lock_timeout = '5s';\n"
                 f"ALTER TABLE {TABLE} ADD CONSTRAINT {CONSTRAINT} CHECK ({CHECK_EXPR})")

# 違例前掃＝CHECK 謂詞之逐字否定（同一常數,無第二套謂詞可漂移）
PRECHECK_SQL = f"SELECT evidence_id FROM {TABLE} WHERE NOT ({CHECK_EXPR})"


def payload_invariants(ddl_apply: str = DDL_APPLY, sql_backfill: str = SQL_BACKFILL,
                       ddl_add_check: str = DDL_ADD_CHECK) -> list[str]:
    """DDL/DML 載體不變式（純函式,參數化——selftest 之壞變體餵**同一函式**驗紅;空=全守）。
    載體字串即被逐字執行之物，對載體驗形＝對行為驗形（同波 migrate_sim_constraints_ddl
    先例）；行為本體另有 sqlite 真表臂。"""
    bad = []
    for name, payload in (("apply", ddl_apply), ("add_check", ddl_add_check)):
        if "SET lock_timeout" not in payload:
            bad.append(f"{name}_lock_timeout")
    if "ADD COLUMN IF NOT EXISTS" not in ddl_apply:
        bad.append("apply_idempotent")
    for kw in ("DROP TABLE", "TRUNCATE", "DELETE FROM", "DROP COLUMN"):
        for payload in (ddl_apply, sql_backfill, ddl_add_check):
            if kw in payload:
                bad.append("no_destructive")
    # 回填之 SET 子句只許賦值 valid_until 一項（不代機器改 status/status_note/last_verified_at）
    set_clause = sql_backfill.split(" SET ", 1)[1].split(" WHERE ", 1)[0].strip()
    if not set_clause.startswith(f"{COL} ="):
        bad.append("backfill_set_target_not_valid_until")
    elif set_clause.count("=") != 1:
        bad.append("backfill_multiple_assignments")
    return bad


# ── sqlite 真表 fixture（selftest 用;真實五列 manual 之實際時戳＋sql 對照列） ──
# (evidence_id, check_type, status, last_verified_at, created_at) —— 2026-08-01 live 現查值
FIXTURE_ROWS = [
    ("E2_macro_latent_debt", "manual", "green", "2026-07-12 02:01:03", "2026-07-11 11:49:37"),
    ("E3_promotion_funnel", "manual", "green", None, "2026-07-11 11:49:37"),
    ("E4_gm_promotion_gap", "manual", "green", None, "2026-07-11 11:49:37"),
    ("E5_survivorship_debt", "manual", "green", "2026-07-12 02:01:03", "2026-07-11 11:49:37"),
    ("E7_h60_ece_outlier", "manual", "green", "2026-07-12 02:01:03", "2026-07-11 11:49:37"),
    ("E6_oos_frozen_rowcount", "sql", "red", "2026-07-31 13:14:00", "2026-07-11 11:49:37"),
]
# 呈案 §3.1 已現算之預期到期日（獨立錨,非由本支公式推得）
EXPECTED_EXPIRY_DATE = {
    "E2_macro_latent_debt": "2026-10-10", "E3_promotion_funnel": "2026-10-09",
    "E4_gm_promotion_gap": "2026-10-09", "E5_survivorship_debt": "2026-10-10",
    "E7_h60_ece_outlier": "2026-10-10",
}


def _sqlite_table(con, check_expr=None):
    con.execute(f"CREATE TABLE {TABLE} (evidence_id TEXT PRIMARY KEY, check_type TEXT, "
                f"status TEXT, last_verified_at TEXT, created_at TEXT, {COL} TEXT"
                + (f", CHECK ({check_expr})" if check_expr else "") + ")")


def sqlite_backfill_sql(days: int = DAYS) -> str:
    """sqlite 版回填：WHERE／基準／天數與 pg 版共用常數，僅日期加法語法換引擎。"""
    return (f"UPDATE {TABLE} SET {COL} = datetime({BASIS_EXPR}, '+{days} days') "
            f"WHERE {BACKFILL_WHERE}")


def _selftest() -> int:
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗FAIL'} {name}")

    # ── CHECK 閉合行為（sqlite 真表跑部署同一 CHECK_EXPR;紅綠雙向） ──
    def _accepts(check_expr, row):
        con = sqlite3.connect(":memory:")
        _sqlite_table(con, check_expr)
        try:
            con.execute(f"INSERT INTO {TABLE} VALUES (?,?,?,?,?,?)", row)
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            con.close()

    chk("CHECK 拒:manual green 無效期（閉合本體——免疫結構性不可能）",
        not _accepts(CHECK_EXPR, ("x1", "manual", "green", None, "2026-07-11", None)))
    chk("CHECK 拒:manual amber 無效期",
        not _accepts(CHECK_EXPR, ("x2", "manual", "amber", None, "2026-07-11", None)))
    chk("CHECK 收:manual green 帶效期（正當人裁路徑不被擋）",
        _accepts(CHECK_EXPR, ("x3", "manual", "green", None, "2026-07-11", "2026-10-09")))
    chk("CHECK 收:manual red 無效期（紅列誠實記載,不強制效期）",
        _accepts(CHECK_EXPR, ("x4", "manual", "red", None, "2026-07-11", None)))
    chk("CHECK 收:sql 型無效期（每跑重驗、無效期概念）",
        _accepts(CHECK_EXPR, ("x5", "sql", "green", None, "2026-07-11", None)))

    con = sqlite3.connect(":memory:")
    _sqlite_table(con, CHECK_EXPR)
    con.execute(f"INSERT INTO {TABLE} VALUES (?,?,?,?,?,?)",
                ("x6", "manual", "green", None, "2026-07-11", "2026-10-09"))
    try:
        con.execute(f"UPDATE {TABLE} SET {COL}=NULL WHERE evidence_id='x6'")
        upd_blocked = False
    except sqlite3.IntegrityError:
        upd_blocked = True
    con.close()
    chk("CHECK 拒:UPDATE 抹掉效期（閉合對 UPDATE 同樣生效）", upd_blocked)

    # ── 回填行為（同一 BACKFILL_WHERE/BASIS_EXPR/DAYS;真實五列＋對照列） ──
    con = sqlite3.connect(":memory:")
    _sqlite_table(con)  # 回填發生在 CHECK 之前,故無 CHECK 之表
    con.executemany(f"INSERT INTO {TABLE} VALUES (?,?,?,?,?,NULL)", FIXTURE_ROWS)
    con.execute(f"INSERT INTO {TABLE} VALUES ('pre_set','manual','green',NULL,"
                "'2026-07-11','2099-01-01 00:00:00')")
    cur = con.execute(sqlite_backfill_sql())
    chk("回填:恰補 5 列 NULL manual（不多不少）", cur.rowcount == 5)
    got = dict(con.execute(
        f"SELECT evidence_id, date({COL}) FROM {TABLE} WHERE check_type='manual' "
        "AND evidence_id <> 'pre_set'"))
    chk("回填:到期日=呈案已現算之獨立錨（E2/E5/E7=10-10、E3/E4=10-09;COALESCE 起算不補造時戳）",
        got == EXPECTED_EXPIRY_DATE)
    chk("回填:sql 型不被觸碰（恆 NULL）",
        con.execute(f"SELECT {COL} FROM {TABLE} WHERE check_type='sql'").fetchone() == (None,))
    chk("回填:已有效期者不被覆寫（冪等;重跑 0 列）",
        con.execute(f"SELECT {COL} FROM {TABLE} WHERE evidence_id='pre_set'").fetchone()
        == ("2099-01-01 00:00:00",) and con.execute(sqlite_backfill_sql()).rowcount == 0)
    # 違例前掃＝CHECK_EXPR 逐字否定:回填後應零違例（--add-check 之違序護欄）
    chk("前掃:回填後零違例（--add-check 可安全落地）",
        con.execute(f"SELECT count(*) FROM {TABLE} WHERE NOT ({CHECK_EXPR})").fetchone() == (0,))
    con.execute(f"UPDATE {TABLE} SET {COL}=NULL WHERE evidence_id='E3_promotion_funnel'")
    chk("前掃:抹掉一列效期即抓到該列（違序 fail loud 有真依據）",
        con.execute(f"SELECT evidence_id FROM {TABLE} WHERE NOT ({CHECK_EXPR})").fetchall()
        == [("E3_promotion_funnel",)])
    con.close()

    # ── 壞變體驗紅（#35:對部署謂詞之突變,自測臂必須翻紅） ──
    weak = CHECK_EXPR.replace(f"OR {COL} IS NOT NULL", f"OR {COL} IS NULL OR {COL} IS NOT NULL")
    chk("驗紅:CHECK 弱化成恆真 → 免疫回歸,拒收臂翻紅",
        _accepts(weak, ("y1", "manual", "green", None, "2026-07-11", None)))
    basis_wrong = sqlite_backfill_sql().replace(BASIS_EXPR, "created_at")
    con = sqlite3.connect(":memory:")
    _sqlite_table(con)
    con.executemany(f"INSERT INTO {TABLE} VALUES (?,?,?,?,?,NULL)", FIXTURE_ROWS)
    con.execute(basis_wrong)
    got_wrong = dict(con.execute(
        f"SELECT evidence_id, date({COL}) FROM {TABLE} WHERE check_type='manual'"))
    con.close()
    chk("驗紅:起算基準改 created_at（補造時戳型錯誤）→ E2 期日臂翻紅",
        got_wrong != EXPECTED_EXPIRY_DATE)
    chk("驗紅:apply 去 lock_timeout → 同一真函式報違",
        "apply_lock_timeout" in payload_invariants(
            ddl_apply=DDL_APPLY.replace("SET lock_timeout = '5s';", "")))
    chk("驗紅:回填 SET 夾帶 status 賦值 → 同一真函式報違（不代機器改人裁狀態）",
        "backfill_set_target_not_valid_until" in payload_invariants(
            sql_backfill=SQL_BACKFILL.replace(f"SET {COL} =", f"SET status='green', {COL} =")))
    chk("驗紅:載體夾帶 DROP TABLE → no_destructive 報違",
        "no_destructive" in payload_invariants(
            ddl_add_check=DDL_ADD_CHECK + f";\nDROP TABLE {TABLE}"))
    chk("本尊載體不變式全守", payload_invariants() == [])

    print("自測:" + ("全通過 ✓" if ok else "有 FAIL ✗"))
    return 0 if ok else 1


def _check(conn) -> int:
    from augur.core import db
    with db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns "
                    "WHERE table_name=%s AND column_name=%s", (TABLE, COL))
        has_col = cur.fetchone()[0] == 1
        print(f"  {'✓' if has_col else '·'} {TABLE}.{COL} {'在' if has_col else '未落地（DDL-1 --apply）'}")
        cur.execute("SELECT count(*) FROM pg_constraint WHERE conname=%s", (CONSTRAINT,))
        has_chk = cur.fetchone()[0] == 1
        print(f"  {'✓' if has_chk else '·'} {CONSTRAINT} {'在位' if has_chk else '未落地（DDL-3 --add-check）'}")
        if has_col:
            cur.execute(f"SELECT evidence_id, status, to_char({COL},'YYYY-MM-DD') "
                        f"FROM {TABLE} WHERE check_type='manual' ORDER BY evidence_id")
            for eid, st, vu in cur.fetchall():
                print(f"    {eid:<24} {st:<10} 有效至 {vu or '（NULL——DDL-2 --backfill）'}")
        else:
            cur.execute(f"SELECT evidence_id, status, to_char({BASIS_EXPR} + interval '{DAYS} days',"
                        f"'YYYY-MM-DD') FROM {TABLE} WHERE check_type='manual' ORDER BY evidence_id")
            for eid, st, exp in cur.fetchall():
                print(f"    {eid:<24} {st:<10} 回填後將到期 {exp}")
    return 0


def _apply(conn) -> int:
    from augur.core import db
    with db.transaction(conn) as cur:
        cur.execute(DDL_APPLY)
    print(f"✓ DDL-1 完成（冪等）:{TABLE}.{COL} 就位")
    return _check(conn)


def _backfill(conn) -> int:
    from augur.core import db
    with db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns "
                    "WHERE table_name=%s AND column_name=%s", (TABLE, COL))
        if cur.fetchone()[0] != 1:
            print(f"✗ {COL} 欄不存在——先 --apply（DDL-1）", file=sys.stderr)
            return 1
        cur.execute(SQL_BACKFILL)
        print(f"✓ DDL-2 完成:回填 {cur.rowcount} 列（只補 NULL,冪等）")
    return _check(conn)


def _add_check(conn) -> int:
    from augur.core import db
    with db.transaction(conn) as cur:
        cur.execute("SELECT count(*) FROM pg_constraint WHERE conname=%s", (CONSTRAINT,))
        if cur.fetchone()[0] == 1:
            print(f"✓ {CONSTRAINT} 已在位（冪等,無動作）")
            return 0
        cur.execute("SELECT count(*) FROM information_schema.columns "
                    "WHERE table_name=%s AND column_name=%s", (TABLE, COL))
        if cur.fetchone()[0] != 1:
            print(f"✗ {COL} 欄不存在——先 --apply（DDL-1）", file=sys.stderr)
            return 1
        cur.execute(PRECHECK_SQL)
        bad = [r[0] for r in cur.fetchall()]
        if bad:
            print(f"✗ 違序:{len(bad)} 列 manual green/amber 無效期——先 --backfill（DDL-2）:{bad}",
                  file=sys.stderr)
            return 1
        cur.execute(DDL_ADD_CHECK)
        print(f"✓ DDL-3 完成:{CONSTRAINT} 落地（manual green/amber 無效期=結構性不可能）")
    return _check(conn)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="validation_evidence manual 有效期 DDL（C1 甲案;備妥不跑,執行歸主 session）")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--add-check", dest="add_check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if not (a.check or a.apply or a.backfill or a.add_check):
        print(__doc__.split("執行指令矩陣")[1].split("------\n")[-1])
    from augur.core import db
    import psycopg2
    try:  # graceful（#29a）:connect 為 contextmanager,例外在 __enter__ 才炸,故包整個 with
        with db.connect() as conn:
            if a.apply:
                return _apply(conn)
            if a.backfill:
                return _backfill(conn)
            if a.add_check:
                return _add_check(conn)
            return _check(conn)
    except psycopg2.OperationalError as e:
        print(f"✗ DB 連線失敗:{str(e).strip()}（需 .env 環境;set -a && . ./.env && set +a）")
        return 1


if __name__ == "__main__":
    sys.exit(main())
